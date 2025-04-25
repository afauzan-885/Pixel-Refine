from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QAbstractItemView, QMenu, QLabel, QStackedLayout, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QEvent # Tambah QUrl, QEvent
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent
import os
from UI.enhance_stack.logic.database_manager import DatabaseManager
from UI.resources.animation.animation_manager import StackedWidgetAnimator
from UI.resources.animation.fade import fade
from UI.resources.stylesheet.stylesheet import LIST_IMAGE_DATA_SINGLE_MODE
from UI.settings.General.Language import language_config
from config import SUPPORTED_FORMATS
from UI.settings.General.Language import language_config

class RightPanel(QWidget):
    """Right panel containing a list of images."""
    previewImageRequested = pyqtSignal(list)
    imagesDropped = pyqtSignal(list)
    
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
        self.image_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.image_list.setDropIndicatorShown(True)
        self.image_list.installEventFilter(self)
        
        # ------------------------------------

        # --- Setup Placeholder Widget ---
        self.placeholder_widget = QWidget()
        self.placeholder_widget.setObjectName("PlaceholderWidget")
        placeholder_internal_layout = QVBoxLayout(self.placeholder_widget)
        placeholder_internal_layout.setContentsMargins(20, 20, 20, 20)
        placeholder_internal_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            format_keys = SUPPORTED_FORMATS.keys()
            supported_formats_text = ", ".join(sorted(list(format_keys)))
        
        except NameError:
            supported_formats_text = "jpg, png, tiff" 
        
        except Exception as e:
            print(f"Error processing SUPPORTED_FORMATS keys: {e}") # Pesan error lebih spesifik
            supported_formats_text = "(Gagal memuat format)"

        html_text = f"""
        <p align="center">
            {language_config.PLACHOLDER_DRAG_AND_DROP_IMPORT_IMAGES}<br><br>
            <span style="color:#666;">{language_config.SUPPORTED_IMAGE_EXTENSION}:</span><br>
            {supported_formats_text}
        </p>
        """
        # Buat QLabel kosong terlebih dahulu
        self.placeholder_label = QLabel()
        self.placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        self.placeholder_label.setText(html_text)
        self.placeholder_label.setWordWrap(True)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 17px;
                border: none;
                background-color: transparent;
                padding: 10px; /* Tambah sedikit padding */
            }
        """)
        placeholder_internal_layout.addWidget(self.placeholder_label)
        self._original_stylesheet = LIST_IMAGE_DATA_SINGLE_MODE
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
        """Load image paths using DatabaseManager."""
        image_paths = self.db_manager.get_single_process_image_paths()
        current_selection = self.get_select_image_list() # Simpan seleksi
        self.image_list.clear()
        self.image_list.addItems(image_paths)
        # Pulihkan seleksi jika item masih ada (opsional)
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            if item.text() in current_selection:
                item.setSelected(True)
        self._update_placeholder_visibility()

    def _update_placeholder_visibility(self):
        """
        Menampilkan list atau placeholder menggunakan animasi fade.
        """
        is_empty = self.image_list.count() == 0
        target_widget = self.placeholder_widget if is_empty else self.image_list

        current_visible_widget = self.stacked_layout.currentWidget()

        if target_widget != current_visible_widget:
            fade(self.animator, self.stacked_layout, target_widget, duration=500)

    def add_dropped_images(self, paths):
        """Adds dropped images to the list and database (assuming DB logic elsewhere)."""
        self.image_list.addItems(paths)
        self._update_placeholder_visibility()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Dipanggil saat drag masuk ke RightPanel."""
        should_accept = False
        if event.mimeData().hasUrls():
            supported_extensions = {ext for formats in SUPPORTED_FORMATS.values() for ext in formats}
            has_image = any(
                url.isLocalFile() and os.path.splitext(url.toLocalFile())[1].lower() in supported_extensions
                for url in event.mimeData().urls()
            )
            if has_image:
                should_accept = True

        # Atur properti berdasarkan validitas drag (GUNAKAN STRING)
        new_state_str = "true" if should_accept else "false"
        current_state_str = self.property("acceptingDrop") # Properti akan dibaca sebagai string jika diset sebagai string

        # Periksa apakah state *perlu* diubah
        if new_state_str != current_state_str:
            self.setProperty("acceptingDrop", new_state_str) # SET DENGAN STRING
            self.style().unpolish(self)
            self.style().polish(self)
            self.update() # TAMBAHKAN UPDATE

        # Terima atau tolak event
        if should_accept:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QDropEvent): # Tipe event QDropEvent
        """Dipanggil saat drag keluar."""
        print("Drag Leave Detected") # DEBUG
        # Selalu set properti ke "false" saat drag keluar JIKA sebelumnya "true"
        if self.property("acceptingDrop") == "true":
            self.setProperty("acceptingDrop", "false") # SET DENGAN STRING
            self.style().unpolish(self)
            self.style().polish(self)
            self.update() # TAMBAHKAN UPDATE
        super().dragLeaveEvent(event)

    def dragMoveEvent(self, event: QDragEnterEvent):
         """Dipanggil saat drag bergerak di atas RightPanel."""
         if self.property("acceptingDrop") == "true":
              event.acceptProposedAction()
         else:
              event.ignore()

    def dragLeaveEvent(self, event: QDropEvent): # Tipe event QDropEvent
        """Dipanggil saat drag keluar."""
        if self.property("acceptingDrop"):
            self.setProperty("acceptingDrop", False)
            self.style().unpolish(self)
            self.style().polish(self)
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Dipanggil saat drop terjadi di RightPanel."""
        # Reset properti visual SEBELUM memproses drop
        if self.property("acceptingDrop"):
            self.setProperty("acceptingDrop", False)
            self.style().unpolish(self)
            self.style().polish(self)

        # Proses drop jika event diterima
        if event.mimeData().hasUrls():
            event.acceptProposedAction() # Terima drop
            valid_image_paths = [
                url.toLocalFile() for url in event.mimeData().urls()
                if url.isLocalFile() and os.path.isfile(url.toLocalFile()) and
                   os.path.splitext(url.toLocalFile())[1].lower() in ['.png', '.jpg', '.jpeg', '.tif', '.tiff', '.bmp', '.webp']
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
                confirmation_text = language_config.HANDLE_DELETE_BUTTON_IMAGE_CONFIRM_DELETE.format(selected_count)
                question_text = confirmation_text 
                
                title = "Delete Confirm"
                reply = QMessageBox.question(
                    self,                                    
                    title,      
                    question_text,                           
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No            
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.remove_selected_images()

                return True

        return super().eventFilter(source, event)
    
            
    def set_to_image_reference(self, item):
        """Move the selected item to the top of the list."""
        row = self.image_list.row(item)
        if row > 0:
            current_item = self.image_list.takeItem(row)
            self.image_list.insertItem(0, current_item)
            self.image_list.setCurrentItem(current_item)


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
            
    def get_select_image_list(self):
        """Return a list of paths for the selected items."""
        select_image_list = self.image_list.selectedItems()
        return [item.text() for item in select_image_list]

    def remove_selected_images(self):
        """Hapus gambar terpilih dan update visibilitas placeholder/list."""
        selected_items = self.image_list.selectedItems()
        if not selected_items: return
        image_paths_to_delete = [item.text() for item in selected_items]
        try:
            deleted_count = self.db_manager.single_process_delete_path_images(image_paths_to_delete)
            if deleted_count >= 0:
                 rows = sorted([self.image_list.row(item) for item in selected_items], reverse=True)
                 items_removed = False
                 for row in rows:
                     if row >= 0:
                         self.image_list.takeItem(row)
                         items_removed = True
                 if items_removed:
                      print("Items removed from list.")
                      self._update_placeholder_visibility() # Update HANYA jika ada yg dihapus dari UI
                 else: 
                      self._update_placeholder_visibility() 
            else: QMessageBox.warning(self, "Deletion Failed", "Could not remove from DB.")
        except Exception as e: print(f"Error deleting: {e}"); QMessageBox.critical(self, "Error", f"Error during deletion:\n{e}")

    def select_list_preview(self):
            """Emit sinyal ketika hanya satu gambar yang dipilih."""
            if self.preview_pause:
                return
            selected_paths = self.get_select_image_list()

            if len(selected_paths) == 1:
                self.previewImageRequested.emit(selected_paths)
                
            elif len(selected_paths) > 1:
                pass

    