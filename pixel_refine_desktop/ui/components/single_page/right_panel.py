from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QListWidget,
    QAbstractItemView,
    QMenu,
    QLabel,
    QStackedLayout,
    QMessageBox,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QColor
import os
from pixel_refine_desktop.core.logic.database_manager import DatabaseManager
from pixel_refine_desktop.ui.resources.animations.animation_manager import StackedWidgetAnimator
from pixel_refine_desktop.ui.resources.animations.fade import fade_in
from pixel_refine_desktop.ui.resources.styles import stylesheet
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from config import SUPPORTED_FORMATS
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class RightPanel(QWidget):
    """Right panel containing a list of images."""

    previewImageRequested = Signal(list)
    preloadRequested = Signal(list)
    imagesDropped = Signal(list)
    referenceImageChanged = Signal(str)

    PRELOAD_COUNT = 8

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.db_manager = database_manager
        self.preview_active = True
        self.preview_pause = False
        self.animator = StackedWidgetAnimator(self)
        self.setAcceptDrops(True)

        # --- Setup List Widget ---
        self.image_list = QListWidget()
        self.image_list.setObjectName("ImageList")
        self.image_list.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.image_list.setDropIndicatorShown(True)
        self.image_list.setStyleSheet(stylesheet.LIST_IMAGE_DATA_SPECIFIC_ITEM)
        self.image_list.installEventFilter(self)

        # --- Setup Placeholder Widget ---
        self.placeholder_widget = QWidget()
        self.placeholder_widget.setObjectName("PlaceholderWidget")
        placeholder_internal_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_internal_layout.setContentsMargins(20, 20, 20, 20)
        placeholder_internal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            format_keys = SUPPORTED_FORMATS.keys()
            supported_formats_text = ", ".join(sorted(list(format_keys)))
        except Exception as e:
            supported_formats_text = "(Failed to load format)"

        html_text = f"""
        <p align="center">
            {language_config.PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES}<br><br>
            <span style="color:#666;">{language_config.SUPPORTED_IMAGE_EXTENSION}:</span><br>
            {supported_formats_text}
        </p>
        """
        self.placeholder_label = QLabel()
        self.placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        self.placeholder_label.setText(html_text)
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.setStyleSheet(stylesheet.PLACEHOLDER_LABEL_STYLE)
        placeholder_internal_layout.addWidget(self.placeholder_label)
        self._original_stylesheet = stylesheet.LIST_IMAGE_DATA_SINGLE_MODE
        self.setProperty("acceptingDrop", False)
        self.setStyleSheet(self._original_stylesheet)

        self.stacked_layout = QStackedLayout()
        self.stacked_layout.setContentsMargins(0, 0, 0, 0)
        self.stacked_layout.addWidget(self.image_list)
        self.stacked_layout.addWidget(self.placeholder_widget)
        self.setLayout(self.stacked_layout)

        # --- Koneksi Sinyal ---
        self.image_list.itemSelectionChanged.connect(self.select_list_preview)
        self.image_list.itemDoubleClicked.connect(self.set_to_image_reference)

        # --- Muat data awal & update placeholder ---
        self.load_image_paths()
        self._update_placeholder_visibility()

    def load_image_paths(self):
        """
        Muat path gambar dari DB (sudah diurutkan oleh DB), tampilkan nama file (RATA TENGAH),
        simpan path lengkap, pulihkan seleksi, dan update placeholder.
        """
        try:
            full_image_paths = self.db_manager.get_single_process_image_paths()
        except Exception as e:
            print(f"Error loading image paths: {e}")
            full_image_paths = []

        current_selection_paths = self.get_select_image_list()

        self.image_list.clear()

        for full_path in full_image_paths:
            if not full_path or not os.path.exists(full_path):
                continue

            filename = os.path.basename(full_path)
            item = QListWidgetItem(filename)
            item.setData(Qt.ItemDataRole.UserRole, full_path)
            item.setToolTip(full_path)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.image_list.addItem(item)

            if full_path in current_selection_paths:
                item.setSelected(True)

        self._update_placeholder_visibility()
        self.image_list.setStyleSheet(
            stylesheet.LIST_IMAGE_DATA_SPECIFIC_ITEM
            if self.image_list.count() > 0
            else stylesheet.LIST_IMAGE_DATA_SINGLE_MODE
        )

    def _update_placeholder_visibility(self):
        """
        Menampilkan list atau placeholder menggunakan animasi fade.
        """
        is_empty = self.image_list.count() == 0
        target_widget = self.placeholder_widget if is_empty else self.image_list

        current_visible_widget = self.stacked_layout.currentWidget()

        if target_widget != current_visible_widget:
            fade_in(self.animator, self.stacked_layout, target_widget, duration=500)

    def add_dropped_images(self, paths):
        """Adds dropped images to the list and database (assuming DB logic elsewhere)."""
        self.image_list.addItems(paths)
        self._update_placeholder_visibility()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Dipanggil saat drag masuk ke RightPanel."""
        should_accept = False
        if event.mimeData().hasUrls():
            supported_extensions = {
                ext for formats in SUPPORTED_FORMATS.values() for ext in formats
            }
            has_image = any(
                url.isLocalFile()
                and os.path.splitext(url.toLocalFile())[1].lower()
                in supported_extensions
                for url in event.mimeData().urls()
            )
            if has_image:
                should_accept = True

        new_state_str = "true" if should_accept else "false"
        current_state_str = self.property("acceptingDrop")

        # Periksa apakah state *perlu* diubah
        if new_state_str != current_state_str:
            self.setProperty("acceptingDrop", new_state_str)  # SET DENGAN STRING
            self.style().unpolish(self)
            self.style().polish(self)
            self.update()  # TAMBAHKAN UPDATE

        # Terima atau tolak event
        if should_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragEnterEvent):
        """Dipanggil saat drag bergerak di atas RightPanel."""
        if self.property("acceptingDrop") == "true":
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDropEvent):  # Tipe event QDropEvent
        """Dipanggil saat drag keluar."""
        if self.property("acceptingDrop"):
            self.setProperty("acceptingDrop", False)
            self.style().unpolish(self)
            self.style().polish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Dipanggil saat drop terjadi di RightPanel."""
        if self.property(
            "acceptingDrop"
        ):  # Gunakan == "true" jika Anda set sebagai string
            self.setProperty("acceptingDrop", False)  # Atau "false"
            self.style().unpolish(self)
            self.style().polish(self)

        if event.mimeData().hasUrls():
            event.acceptProposedAction()

            supported_extensions = {
                ext.lower() for formats in SUPPORTED_FORMATS.values() for ext in formats
            }

            valid_image_paths = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile()
                and os.path.isfile(url.toLocalFile())
                and os.path.splitext(url.toLocalFile())[1].lower()
                in supported_extensions  # <-- Gunakan set dari SUPPORTED_FORMATS
            ]

            if valid_image_paths:
                self.imagesDropped.emit(valid_image_paths)

    def eventFilter(self, source, event: QEvent):
        if source == self.image_list and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Delete:

                selected_items = self.image_list.selectedItems()
                if not selected_items:
                    return True

                selected_count = len(self.image_list.selectedItems())
                confirmation_text = (
                    language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(
                        selected_count
                    )
                )
                question_text = confirmation_text

                title = "Delete Confirm"
                reply = QMessageBox.question(
                    self,
                    title,
                    question_text,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.remove_selected_images()

                return True

        return super().eventFilter(source, event)

    def set_to_image_reference(self, item: QListWidgetItem):
        """
        Sets the selected item as the reference image in the database
        and reloads the list.
        """
        if not item:
            return

        full_path = item.data(Qt.ItemDataRole.UserRole)
        if not full_path or not isinstance(full_path, str):
            return

        success = self.db_manager.set_single_process_reference(full_path)

        if success:
            self.load_image_paths()
            self.referenceImageChanged.emit(full_path)
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not set '{os.path.basename(full_path)}' as the reference image.",
            )

    def contextMenuEvent(self, event):
        """Display a context menu on right-click."""
        list_pos = self.image_list.mapFrom(self, event.pos())
        item = self.image_list.itemAt(list_pos)
        if item:
            menu = QMenu(self)
            set_ref_action = menu.addAction("Set as Image Reference")
            action = menu.exec(self.image_list.mapToGlobal(list_pos))

            if action == set_ref_action:
                self.set_to_image_reference(item)

    def get_select_image_list(self) -> list[str]:
        """Return a list of FULL paths for the selected items."""
        selected_paths = []
        for item in self.image_list.selectedItems():
            full_path = item.data(Qt.ItemDataRole.UserRole)  # Ambil dari UserRole
            if full_path:  # Pastikan data tidak None
                selected_paths.append(full_path)
        return selected_paths

    def remove_selected_images(self):
        """Hapus gambar terpilih dari DB dan list, lalu update placeholder."""
        selected_items = self.image_list.selectedItems()  # Ambil item terpilih
        if not selected_items:
            return

        # Ambil FULL PATH dari data item untuk dihapus dari DB
        image_paths_to_delete = []
        rows_to_remove = []
        for item in selected_items:
            full_path = item.data(Qt.ItemDataRole.UserRole)
            if full_path:
                image_paths_to_delete.append(full_path)
                rows_to_remove.append(
                    self.image_list.row(item)
                )  # Simpan row untuk dihapus dari UI

        if not image_paths_to_delete:
            print("No valid paths found in selected items to delete.")
            return

        try:
            deleted_count = self.db_manager.single_process_delete_path_images(
                image_paths_to_delete
            )

            if deleted_count >= 0:
                items_removed_from_ui = False
                for row in sorted(rows_to_remove, reverse=True):
                    if row >= 0:
                        taken_item = self.image_list.takeItem(row)
                        del taken_item
                        items_removed_from_ui = True
                if items_removed_from_ui:
                    self._update_placeholder_visibility()  # Update setelah hapus
            else:
                QMessageBox.warning(
                    self, "Deletion Failed", "Could not remove from DB."
                )
        except Exception as e:
            print(f"Error deleting: {e}")
            QMessageBox.critical(self, "Error", f"Error during deletion:\n{e}")

    def select_list_preview(self):
        """
        Memancarkan sinyal untuk gambar yang dipilih DAN untuk pra-pemuatan
        gambar-gambar berikutnya.
        """
        if self.preview_pause:
            return

        selected_items = self.image_list.selectedItems()

        # Hanya jalankan jika tepat satu item yang dipilih
        if len(selected_items) != 1:
            # Jika lebih dari 1 dipilih, kita bisa memilih untuk tidak melakukan apa-apa
            # atau membersihkan pratinjau. Untuk saat ini, kita ikuti logika Anda.
            if len(self.get_select_image_list()) > 1:
                pass  # Sesuai kode asli Anda
            return

        # 1. Kirim permintaan untuk pratinjau resolusi penuh (perilaku yang ada)
        selected_path = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if selected_path:
            self.previewImageRequested.emit([selected_path])

        # 2. Kumpulkan path untuk pra-pemuatan dan kirim sinyal baru
        paths_to_preload = []
        current_row = self.image_list.row(selected_items[0])

        for i in range(1, self.PRELOAD_COUNT + 1):
            next_row = current_row + i
            if next_row < self.image_list.count():
                item = self.image_list.item(next_row)
                path = item.data(Qt.ItemDataRole.UserRole)
                if path:
                    paths_to_preload.append(path)
            else:
                break  # Berhenti jika sudah mencapai akhir daftar

        if paths_to_preload:
            self.preloadRequested.emit(paths_to_preload)
