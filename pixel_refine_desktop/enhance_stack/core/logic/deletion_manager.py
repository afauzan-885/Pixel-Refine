import os
from PySide6.QtCore import QObject, Signal, QThread, QTimer, Slot
from PySide6.QtWidgets import QMessageBox

from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    ProcessManager,
    is_widget_alive,
)
from pixel_refine_desktop.ui.resources.animations.fade import fade_out
from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastPosition,
)


# Worker Class (Moved from DisplayPanel)
class ImageDeletionWorker(QObject):
    """Worker untuk menghapus gambar di thread terpisah tanpa freeze UI."""

    finished = Signal(int, int)  # Signal with (count, batch_id)
    error = Signal(str, int)  # Signal with (error_message, batch_id)

    def __init__(self, controller, batch_id, paths_to_remove):
        super().__init__()
        self.controller = controller
        self.batch_id = batch_id
        self.paths_to_remove = paths_to_remove

    def run(self):
        try:
            removed_count = 0
            if self.controller:
                # Assuming batch_delete_images returns count
                removed_count = self.controller.batch_delete_images(
                    self.batch_id, self.paths_to_remove
                )
            self.finished.emit(removed_count, self.batch_id)
        except Exception as e:
            self.error.emit(str(e), self.batch_id)


class DeletionManager(QObject):
    """
    Manages image deletion workflow.
    Handles UI confirmation, Background Worker, Real-time 'Zombie' removal stream.
    """

    # Signal to update Main UI
    deletion_finished = Signal(int)  # Count removed
    deletion_error = Signal(str)

    def __init__(self, display_panel):
        super().__init__()
        self.panel = display_panel

        # State
        self.active_deletions = {}  # {batch_id: [paths]} for resume logic
        self.removal_queue = []  # [(card_id, widget), ...]

        # Thread & Timer references
        self.deletion_thread = None
        self.ui_removal_timer = None

    def request_deletion(self, selected_ids):
        """Request deletion of selected images with confirmation."""
        if (
            not selected_ids
            or not self.panel.current_batch_id
            or not self.panel.controller
        ):
            return

        reply = QMessageBox.question(
            self.panel,
            "Hapus Gambar",
            f"Apakah Anda yakin ingin menghapus {len(selected_ids)} gambar yang dipilih dari batch ini?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            paths_to_remove = []
            cards_to_remove = []

            for cid in selected_ids:
                if cid in self.panel.logic.grid_items:
                    paths_to_remove.append(self.panel.logic.grid_items[cid]["path"])
                    if cid in self.panel.all_cards:
                        cards_to_remove.append((cid, self.panel.all_cards[cid]))

            if paths_to_remove:
                # Show toast feedback
                self.panel.toast.show_message(
                    f"Menghapus {len(paths_to_remove)} gambar dari {self.panel.current_batch_name or 'batch'}...",
                    duration=2000,
                    position=ToastPosition.BOTTOM_RIGHT,
                )
                self.start_deletion_process(paths_to_remove, cards_to_remove)

    def start_deletion_process(self, paths_to_remove, cards_to_remove):
        """Start background deletion and frontend visual removal."""

        # 1. Background DB Deletion
        self.deletion_thread = QThread()
        # Note: Worker needs controller and batch_id
        worker = ImageDeletionWorker(
            self.panel.controller, self.panel.current_batch_id, paths_to_remove
        )
        worker.moveToThread(self.deletion_thread)

        self.deletion_thread.started.connect(worker.run)
        worker.finished.connect(self._on_worker_finished)
        worker.error.connect(self._on_worker_error)

        worker.finished.connect(self.deletion_thread.quit)
        worker.finished.connect(worker.deleteLater)
        self.deletion_thread.finished.connect(self.deletion_thread.deleteLater)

        # Register thread
        ProcessManager.instance().register_thread(
            "display_deletion", self.deletion_thread
        )

        self.deletion_thread.start()

        # 2. Setup UI Removal Queue
        self.removal_queue = list(cards_to_remove)

        # Store for resume logic
        self.active_deletions[self.panel.current_batch_id] = list(paths_to_remove)

        # 3. Start Timer
        self._start_removal_timer()

    def _start_removal_timer(self):
        """Start or restart the removal timer."""
        if self.ui_removal_timer and self.ui_removal_timer.isActive():
            return

        self.ui_removal_timer = QTimer(self)
        self.ui_removal_timer.timeout.connect(self._process_queue)

        ProcessManager.instance().register_timer(
            "display_sequential_removal", self.ui_removal_timer
        )
        self.ui_removal_timer.start(100)  # 100ms interval

    def queue_zombie_card(self, card_id, card_widget):
        """Add a resurrected zombie card to the removal queue (for batch switching support)."""
        self.removal_queue.append((card_id, card_widget))
        self._start_removal_timer()

    def _process_queue(self):
        """Process one item from removal queue."""
        if not self.removal_queue:
            if self.ui_removal_timer:
                self.ui_removal_timer.stop()
            # Finish up: Rebuild grid layout
            self.panel.grid_container._rebuild_grid()
            return

        card_id, card_widget = self.removal_queue.pop(0)

        if not is_widget_alive(card_widget):
            return

        try:
            # 1. Cleanup references in Panel and Logic
            # Note: We access panel internals here.
            # In a strict architecture we might expose methods on panel,
            # but for refactoring, direct access is pragmatic.

            if hasattr(self.panel.grid_container, "_stored_widgets"):
                if card_widget in self.panel.grid_container._stored_widgets:
                    self.panel.grid_container._stored_widgets.remove(card_widget)

            if card_id in self.panel.all_cards:
                del self.panel.all_cards[card_id]

            # Update Selection Manager
            if self.panel.selection_manager:
                self.panel.selection_manager.selected_thumbnails.discard(card_id)

            self.panel.logic.unregister_grid_item(card_id)

            # 2. Visual Fade Out
            fade_out(
                self.panel.grid_animator,
                card_widget,
                duration=300,
                on_finished_callback=card_widget.deleteLater,
            )

            # 3. Update Counts
            self.panel.total_image_count -= 1
            if self.panel.total_image_count < 0:
                self.panel.total_image_count = 0
            self.panel._update_header_title()  # Call internal method or public if available

            # 4. Update Active Deletions State
            current_batch = self.panel.current_batch_id
            if current_batch in self.active_deletions:
                remaining = self.active_deletions[current_batch]
                # Filter out path that matches this card_id (basename check)
                self.active_deletions[current_batch] = [
                    p for p in remaining if os.path.basename(p) != card_id
                ]
                if not self.active_deletions[current_batch]:
                    del self.active_deletions[current_batch]

        except Exception as e:
            print(f"Error vanishing card {card_id}: {e}")

    def _on_worker_finished(self, count, batch_id):
        self.deletion_finished.emit(count)
        # Notify success? Maybe toast already shown.

    def _on_worker_error(self, message, batch_id):
        self.deletion_error.emit(message)
        self.panel.toast.show_message(
            f"Error deleting: {message}", position=ToastPosition.BOTTOM_RIGHT
        )

    def resume_deletion_simulation(self, batch_id):
        """Resume visual deletion animation if there are pending deletions for this batch."""
        if batch_id not in self.active_deletions:
            return

        pending_paths = self.active_deletions[batch_id]
        if not pending_paths:
            return

        print(
            f"Resuming deletion simulation for {len(pending_paths)} items in batch {batch_id}"
        )

        # Build removal queue from current cards
        cards_to_remove = []
        pending_ids = {os.path.basename(p) for p in pending_paths}

        for cid, card in self.panel.all_cards.items():
            if cid in pending_ids:
                cards_to_remove.append((cid, card))

        if not cards_to_remove:
            return

        # Setup UI Queue
        self.removal_queue = list(cards_to_remove)
        self._start_removal_timer()
