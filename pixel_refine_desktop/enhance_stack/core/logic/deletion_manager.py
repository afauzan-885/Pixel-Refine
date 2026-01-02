# --- START OF FILE deletion_manager.py ---

import os
from PySide6.QtCore import (
    QObject,
    Signal,
    QThread,
    QTimer,
    Slot,
    QPoint,
    QRect,
    QCoreApplication,
)
from PySide6.QtWidgets import QMessageBox, QGraphicsOpacityEffect, QWidget

# Tambahkan import property animation jika belum ada di file ini
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    ProcessManager,
    is_widget_alive,
)
from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastPosition,
)


class ImageDeletionWorker(QObject):
    """
    Worker menghapus gambar dari DB/Disk.
    OPTIMASI: Menggunakan Chunk Besar (50) untuk efisiensi I/O Database (HDD Friendly).
    """

    finished = Signal(int, int)
    error = Signal(str, int)
    progress = Signal(list)

    def __init__(self, controller, batch_id, paths_to_remove):
        super().__init__()
        self.controller = controller
        self.batch_id = batch_id
        self.paths_to_remove = paths_to_remove

    def run(self):
        try:
            total_removed = 0
            all_paths = list(self.paths_to_remove)
            total_count = len(all_paths)

            # --- OPTIMASI UTAMA: DYNAMIC CHUNK SIZE ---
            # Default 50. Meningkat sesuai volume data untuk mengurangi transaksi disk secara agresif.
            chunk_size = 50
            if total_count >= 1499:
                chunk_size = 400
            elif total_count >= 999:
                chunk_size = 200
            elif total_count >= 500:
                chunk_size = 100

            print(
                f"[DeletionWorker] Starting deletion of {total_count} images with chunk_size: {chunk_size}"
            )

            for i in range(0, total_count, chunk_size):
                if QCoreApplication.closingDown():
                    return

                chunk_paths = all_paths[i : i + chunk_size]

                if self.controller:
                    # Database Manager yang sudah dioptimasi akan menghapus ini dalam < 100ms
                    count = self.controller.remove_images_from_batch(
                        self.batch_id, chunk_paths
                    )
                    total_removed += count

                deleted_ids = [os.path.basename(p) for p in chunk_paths]
                self.progress.emit(deleted_ids)

                # Sleep kecil sudah cukup karena chunk besar
                QThread.msleep(10)

            self.finished.emit(total_removed, self.batch_id)
        except Exception as e:
            self.error.emit(str(e), self.batch_id)


class DeletionManager(QObject):
    deletion_finished = Signal(int)
    deletion_error = Signal(str)

    def __init__(self, display_panel):
        super().__init__()
        self.panel = display_panel
        self.active_deletions = {}
        self.removal_queue = []

        self.deletion_thread = None

        # Timer Manual (Recursive)
        self.ui_removal_timer = QTimer(self)
        self.ui_removal_timer.setSingleShot(True)
        self.ui_removal_timer.timeout.connect(self._process_one_item)

        self.total_to_remove = 0
        self.removed_count = 0

        self._current_worker = None

    def _is_widget_in_viewport(self, widget):
        if not is_widget_alive(widget) or not widget.isVisible():
            return False
        try:
            viewport = self.panel.grid_container.viewport()
            if not viewport:
                return False
            visible_rect = viewport.rect()
            widget_pos = widget.mapTo(viewport, QPoint(0, 0))
            widget_rect = QRect(widget_pos, widget.size())
            return visible_rect.intersects(widget_rect)
        except Exception:
            return False

    def _lite_fade_out(self, widget, duration, callback):
        """
        Animasi Fade Out Ringan (In-Place) untuk mencegah crash QPainter.
        """
        if not is_widget_alive(widget):
            if callback:
                callback()
            return

        # 1. Pasang Effect Transparansi
        effect = widget.graphicsEffect()
        if not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)

        # 2. Setup Animasi
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuad)

        # 3. Hubungkan Callback
        if callback:
            anim.finished.connect(callback)

        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _process_one_item(self):
        """
        Mengambil 1 item dari antrean UI dan memprosesnya.
        """
        if not self.removal_queue:
            return

        card_id, card_widget = self.removal_queue.pop(0)

        # Safety Check: Widget mati? Skip instan.
        if not is_widget_alive(card_widget):
            self.ui_removal_timer.start(0)
            return

        current_batch_id = self.panel.current_batch_id
        if not current_batch_id:
            self.removal_queue.clear()
            return

        next_delay = 0

        try:
            # --- Hapus Data Logis UI ---
            if hasattr(self.panel.grid_container, "_stored_widgets"):
                if card_widget in self.panel.grid_container._stored_widgets:
                    self.panel.grid_container._stored_widgets.remove(card_widget)

            if card_id in self.panel.all_cards:
                del self.panel.all_cards[card_id]

            self.panel.logic.unregister_grid_item(card_id)

            # --- Logika Visual (Domino Effect) ---
            is_visible = self._is_widget_in_viewport(card_widget)

            if is_visible:
                # KASUS A: Visible -> Animasi Fade Out
                self._lite_fade_out(
                    widget=card_widget, duration=250, callback=card_widget.deleteLater
                )

                # --- PACING LOGIC ---
                # Default 100ms agar terlihat satu per satu.
                next_delay = 100

                # CATCH-UP LOGIC:
                # Karena DB sekarang ngebut (chunk 50), antrean UI akan cepat penuh.
                # Jika antrean menumpuk > 100 item, kita percepat sedikit (30ms)
                # agar user tidak menunggu animasi selesai terlalu lama,
                # tapi tetap mempertahankan efek urutan.
                q_len = len(self.removal_queue)
                if q_len > 100:
                    next_delay = 20
                elif q_len > 50:
                    next_delay = 50

            else:
                # KASUS B: Off-Screen -> Hapus Instan
                card_widget.hide()
                card_widget.deleteLater()
                next_delay = 5

            # Update Header Count
            self.panel.total_image_count -= 1
            if self.panel.total_image_count < 0:
                self.panel.total_image_count = 0
            self.panel._update_header_title()

        except Exception as e:
            print(f"Error vanishing: {e}")
            next_delay = 10

        # --- JADWALKAN ITEM BERIKUTNYA ---
        if self.removal_queue:
            self.ui_removal_timer.start(next_delay)
        else:
            # Rebuild grid jika antrean habis
            QTimer.singleShot(300, self.panel.grid_container._rebuild_grid)

    def request_deletion(self, selected_ids):
        """Request deletion of selected images with confirmation."""
        if not selected_ids or not self.panel.current_batch_id:
            return

        reply = QMessageBox.question(
            self.panel,
            "Hapus Gambar",
            f"Apakah Anda yakin ingin menghapus {len(selected_ids)} gambar yang dipilih dari batch ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            paths_to_remove = []
            for cid in selected_ids:
                if cid in self.panel.logic.grid_items:
                    paths_to_remove.append(self.panel.logic.grid_items[cid]["path"])

            if paths_to_remove:
                self.total_to_remove = len(paths_to_remove)
                self.removed_count = 0

                self.panel.toast.show_progress(
                    f"Menghapus gambar {0}%",
                    position=ToastPosition.BOTTOM_RIGHT,
                    category="deletion_progress",
                )
                self.start_deletion_process(paths_to_remove)

    def start_deletion_process(self, paths_to_remove):
        self.deletion_thread = QThread()
        worker = ImageDeletionWorker(
            self.panel.controller, self.panel.current_batch_id, paths_to_remove
        )
        worker.moveToThread(self.deletion_thread)

        self.deletion_thread.started.connect(worker.run)

        # PENTING: Koneksikan sinyal progress ke handler UI
        worker.progress.connect(self._on_worker_progress)

        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)

        worker.finished.connect(self.deletion_thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.deletion_thread.finished.connect(self.deletion_thread.deleteLater)

        self._current_worker = worker
        self.active_deletions[self.panel.current_batch_id] = list(paths_to_remove)

        # Reset Queue
        self.removal_queue = []

        ProcessManager.instance().register_thread(
            "display_deletion", self.deletion_thread
        )
        self.deletion_thread.start()

    @Slot(list)
    def _on_worker_progress(self, deleted_ids):
        """
        Diterima saat Worker selesai menghapus CHUNK BESAR (50 gambar).
        Ini akan mengisi antrean UI sekaligus.
        """
        items_added = False
        for card_id in deleted_ids:
            if card_id in self.panel.all_cards:
                card_widget = self.panel.all_cards[card_id]
                self.removal_queue.append((card_id, card_widget))
                items_added = True

        # Pancing timer jika sedang diam
        if items_added and not self.ui_removal_timer.isActive():
            self._process_one_item()

        # Update Toast dengan persentase
        self.removed_count += len(deleted_ids)
        if self.total_to_remove > 0:
            pct = int((self.removed_count / self.total_to_remove) * 100)
            if pct < 100:
                self.panel.toast.show_progress(
                    f"Menghapus gambar {pct}%",
                    position=ToastPosition.BOTTOM_RIGHT,
                    category="deletion_progress",
                )

    def _on_worker_finished(self, count, batch_id):
        self.deletion_finished.emit(count)

        if batch_id in self.active_deletions:
            del self.active_deletions[batch_id]

        # Toast Succcess
        if count > 0:
            self.panel.toast.show_message(
                f"Berhasil menghapus {count} gambar.",
                duration=3000,
                position=ToastPosition.BOTTOM_RIGHT,
                priority="HIGH",
            )
        else:
            self.panel.toast.hide()

    def _on_worker_error(self, message, batch_id):
        self.deletion_error.emit(message)
        self.panel.toast.show_message(
            f"Gagal menghapus gambar: {message}",
            duration=4000,
            position=ToastPosition.BOTTOM_RIGHT,
            priority="URGENT",
        )

    # --- Method Legacy/Helper Lainnya ---
    def resume_deletion_simulation(self, batch_id):
        if batch_id not in self.active_deletions:
            return
        pending_paths = self.active_deletions[batch_id]
        if not pending_paths:
            return

        cards_to_remove = []
        pending_ids = {os.path.basename(p) for p in pending_paths}
        for cid, card in self.panel.all_cards.items():
            if cid in pending_ids:
                cards_to_remove.append((cid, card))

        if not cards_to_remove:
            return

        for cid, card in cards_to_remove:
            self.removal_queue.append((cid, card))

        if not self.ui_removal_timer.isActive():
            self._process_one_item()

    def queue_zombie_card(self, card_id, card_widget):
        self.removal_queue.append((card_id, card_widget))
        if not self.ui_removal_timer.isActive():
            self._process_one_item()
