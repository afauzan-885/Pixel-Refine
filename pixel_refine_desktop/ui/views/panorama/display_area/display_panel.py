from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QPoint,
    QEvent,
)
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QMouseEvent,
    QKeySequence,
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QScrollArea,
    QFrame,
    QGridLayout,
    QMenu,
    QGraphicsScene,
    QMessageBox,
    QFileDialog,
)

import cv2

from UI.enhance_stack.components.batch_page_layout.thumbnail import (
    ThumbnailLoader,
    stop_process_thumbnails,
)
from pixel_refine_desktop.core.logic.Zoomable_Handler import Zoomable
from pixel_refine_desktop.ui.views.panorama.display_area.display_thumbnail import ThumbnailWidget
from pixel_refine_desktop.ui.views.panorama.display_area.thumbnail_preview import ImagePreviewDialog
from pixel_refine_desktop.ui.views.panorama.logic.processing_view import ProcessingView
from pixel_refine_desktop.ui.resources.animations.animation_manager import StackedWidgetAnimator

class DisplayPanel(QWidget):
    """
    Panel yang bertanggung jawab untuk menampilkan konten utama:
    grid gambar, tampilan pemrosesan, dan hasil pratinjau panorama.
    Juga menangani semua interaksi pengguna yang terkait dengan konten ini.
    """
    # --- Sinyal untuk komunikasi ke parent (WorkingLeftPanel) ---
    rename_project_requested = Signal(str)
    images_to_import_selected = Signal(list)
    images_to_delete_selected = Signal(list)
    back_to_grid_requested = Signal()
    back_to_preview_requested = Signal()
    _cleanup_finished = Signal()
    
    # =========================================================================
    # === 1. Inisialisasi & Pengaturan UI ===
    # =========================================================================

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Variabel State Lokal ---
        self.animator = StackedWidgetAnimator(self) 
        self.thumbnail_threads = []
        self.selected_thumbnails = set()
        self.last_clicked_index = -1
        self.project_id = None
        self.project_name = "No Project Selected"
        self._is_busy_loading = False

        self._setup_ui()
        self.setAcceptDrops(True)
        self.clear_display(no_projects_exist=True)  

    def _setup_ui(self):
        """Membangun dan menyusun semua elemen UI statis untuk panel ini."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)

        # --- Header ---
        self.title_label = QLabel()
        self.title_label.setObjectName("sectionTitle")
        self.title_label.installEventFilter(self) # Untuk mendeteksi double-click

        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton")
        self.import_button.clicked.connect(self.import_images)

        self.back_to_grid_button = QPushButton("Back to Import Images")
        self.back_to_grid_button.clicked.connect(self.back_to_grid_requested.emit)

        self.back_to_preview_button = QPushButton("Restore Preview")
        self.back_to_preview_button.clicked.connect(self.back_to_preview_requested.emit)
        
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.back_to_preview_button)
        header_layout.addWidget(self.back_to_grid_button)
        header_layout.addWidget(self.import_button)
        container_layout.addLayout(header_layout)

        # --- QStackedWidget untuk beralih antar view ---
        self.display_stack = QStackedWidget()
        container_layout.addWidget(self.display_stack)

        # --- View 1: Grid Gambar ---
        self.grid_view_widget = QWidget()
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        grid_view_layout.addWidget(self.scroll_area)
        self.display_stack.addWidget(self.grid_view_widget)

        # --- View 2: Tampilan Pemrosesan ---
        processing_container = QWidget()
        processing_layout = QVBoxLayout(processing_container)
        processing_layout.setContentsMargins(50, 50, 50, 50)
        self.processing_view = ProcessingView()
        processing_layout.addWidget(self.processing_view)
        self.display_stack.addWidget(processing_container)
        
        # --- View 3: Tampilan Pratinjau (Zoomable) ---
        self.preview_view_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_view_widget)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        self.zoomable_preview = Zoomable() 
        preview_layout.addWidget(self.zoomable_preview)
        self.display_stack.addWidget(self.preview_view_widget)
        
        # --- View 4: Tampilan Pesan Hasil (Legacy/Cadangan) ---
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_stack.addWidget(self.result_label)

        main_layout.addWidget(display_container)

    # =========================================================================
    # === 2. Manajemen View & Tampilan Utama ===
    # =========================================================================
    
    @Slot()
    def show_grid_view(self):
        """Beralih ke tampilan grid gambar dan mengatur visibilitas tombol header."""
        self.display_stack.setCurrentWidget(self.grid_view_widget)
        self.import_button.setVisible(self.project_id is not None)
        self.back_to_grid_button.setVisible(False)
        self.back_to_preview_button.setVisible(False) 

    @Slot(str)
    def show_processing_view(self, title: str):
        """Beralih ke tampilan progress dan mengatur judul awalnya."""
        self.processing_view.update_progress(title, 0)
        processing_container = self.processing_view.parentWidget()
        self.display_stack.setCurrentWidget(processing_container)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)
        self.back_to_preview_button.setVisible(False)

    @Slot(str, int)
    def update_processing_progress(self, title: str, value: int):
        """Memperbarui nilai progress di ProcessingView."""
        self.processing_view.update_progress(title, value)

    def display_zoomable_image(self, numpy_image, max_preview_dim=4096):
        """
        Menampilkan gambar NumPy di view Zoomable dengan resolusi yang aman.
        
        - numpy_image: bisa merupakan crop dari memmap atau preview
        - max_preview_dim: batas maksimal dimensi untuk performa UI
        """
        scene = self.zoomable_preview.scene()
        if scene is None:
            scene = QGraphicsScene(self.zoomable_preview)
            self.zoomable_preview.setScene(scene)

        if numpy_image is None:
            scene.clear()
            return

        # Kecilkan gambar jika terlalu besar untuk performa
        h, w = numpy_image.shape[:2]
        if h > max_preview_dim or w > max_preview_dim:
            scale = max_preview_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            display_image = cv2.resize(numpy_image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        else:
            display_image = numpy_image

        # Konversi ke QPixmap
        try:
            rgb_image = cv2.cvtColor(display_image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
        except Exception as e:
            print(f"Error converting image for display: {e}")
            scene.clear()
            return

        # Tampilkan di scene
        scene.clear()
        pixmap_item = scene.addPixmap(pixmap)
        self.zoomable_preview.fitInView(pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

        # Atur UI
        self.display_stack.setCurrentWidget(self.preview_view_widget)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)
        self.back_to_preview_button.setVisible(False)
        
    @Slot(str)
    def show_preview_message(self, message: str):
        """Menampilkan pesan teks di view hasil."""
        self.result_label.setText(message)
        self.display_stack.setCurrentWidget(self.result_label)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)
        self.back_to_preview_button.setVisible(False) 
        
    @Slot(bool)
    def set_restore_button_visibility(self, visible):
        """Mengatur visibilitas tombol untuk kembali ke pratinjau terakhir."""
        self.back_to_preview_button.setVisible(visible)

    # =========================================================================
    # === 3. Slot Publik untuk Memuat Data ===
    # =========================================================================

    @Slot(int, str, list)
    def load_project(self, project_id, project_name, image_paths):
        """Slot utama untuk memuat data proyek dan menampilkan thumbnail."""
        self.project_id = project_id
        self.project_name = project_name
        self.title_label.setText(project_name)

        stop_process_thumbnails(self.thumbnail_threads)
        self._clear_selection()

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        if not image_paths:
            html = "<p>Drag & drop files here or use 'Import Images'.</p>"
            self.scroll_area.setWidget(self._create_placeholder_widget(html))
        else:
            grid_widget = QWidget()
            grid_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            grid_widget.customContextMenuRequested.connect(self._show_context_menu)
            
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(10)
            grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            for i, path in enumerate(image_paths):
                row, col = divmod(i, 8) # Cara lebih Pythonic untuk i // 8, i % 8
                thumb = ThumbnailWidget(path)
                thumb.clicked.connect(self._on_thumbnail_clicked)
                thumb.double_clicked.connect(self._on_thumbnail_double_clicked)
                grid_layout.addWidget(thumb, row, col)
                
                thread = ThumbnailLoader(path)
                thread.thumbnail_ready.connect(self._update_thumbnail)
                thread.start()
                self.thumbnail_threads.append(thread)

            self.scroll_area.setWidget(grid_widget)

        self.show_grid_view()

    @Slot(bool)
    def clear_display(self, no_projects_exist=False):
        """Membersihkan panel ke keadaan awal atau 'tidak ada proyek'."""
        stop_process_thumbnails(self.thumbnail_threads)
        self._clear_selection()
        self.title_label.setText("No Project Selected")
        self.project_id = None

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        text = ("No panorama projects found.<br>Click 'Add Pano' to create one."
                if no_projects_exist
                else "Please select or create a project.")
        self.scroll_area.setWidget(self._create_placeholder_widget(f"<p>{text}</p>"))
        
        self.show_grid_view()

    # =========================================================================
    # === 4. Penanganan Interaksi Pengguna ===
    # =========================================================================

    # --- 4a. Aksi Impor, Hapus, dan Ganti Nama ---
    
    def import_images(self):
        """Membuka dialog file untuk impor gambar."""
        if not self.project_id: return
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif)")
        if paths:
            self.images_to_import_selected.emit(paths)

    def delete_selected_images(self):
        """Meminta konfirmasi dan mengirim sinyal untuk menghapus gambar terpilih."""
        if not self.selected_thumbnails: return
        reply = QMessageBox.question(self, "Confirm Delete", 
                                     f"Remove {len(self.selected_thumbnails)} image(s)?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            paths = [thumb.image_path for thumb in self.selected_thumbnails]
            self.images_to_delete_selected.emit(paths)

    # --- 4b. Logika Seleksi Thumbnail ---
    
    @Slot(str, QMouseEvent)
    def _on_thumbnail_clicked(self, image_path, event):
        """Menangani logika seleksi (klik tunggal, Ctrl+klik, Shift+klik)."""
        modifiers = event.modifiers()
        grid_layout = self.scroll_area.widget().layout()
        if not grid_layout: return

        clicked_widget = self.sender()
        clicked_index = grid_layout.indexOf(clicked_widget)

        if event.button() == Qt.MouseButton.RightButton:
            if not clicked_widget.is_selected():
                self._clear_selection()
                self._select_one_thumbnail(clicked_widget)
        elif modifiers & Qt.KeyboardModifier.ControlModifier:
            self._toggle_thumbnail_selection(clicked_widget)
        elif (modifiers & Qt.KeyboardModifier.ShiftModifier and self.last_clicked_index != -1):
            self._select_range(clicked_index)
        else:
            self._clear_selection()
            self._select_one_thumbnail(clicked_widget)
        self.last_clicked_index = clicked_index
    
    def _clear_selection(self):
        for thumb in list(self.selected_thumbnails):
            thumb.set_selected(False) 
        self.selected_thumbnails.clear()

    def _select_one_thumbnail(self, widget):
        widget.set_selected(True)
        self.selected_thumbnails.add(widget)

    def _toggle_thumbnail_selection(self, widget):
        if widget.is_selected():
            widget.set_selected(False) 
            self.selected_thumbnails.discard(widget)
        else:
            widget.set_selected(True) 
            self.selected_thumbnails.add(widget)

    def _select_range(self, end_index):
        start = min(self.last_clicked_index, end_index)
        end = max(self.last_clicked_index, end_index)
        self._clear_selection()
        layout = self.scroll_area.widget().layout()
        for i in range(start, end + 1):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                self._select_one_thumbnail(widget)
    
    def _select_all_images(self):
        layout = self.scroll_area.widget().layout()
        if not layout: return
        self._clear_selection()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                self._select_one_thumbnail(widget)

    # --- 4c. Menu Konteks dan Interaksi Lainnya ---

    @Slot(str)
    def _on_thumbnail_double_clicked(self, image_path):
        """Menampilkan dialog pratinjau gambar saat thumbnail di-double-click."""
        ImagePreviewDialog(image_path, self).exec()

    @Slot(QPoint)
    def _show_context_menu(self, pos):
        """Menampilkan menu klik-kanan pada area grid."""
        grid_widget = self.scroll_area.widget()
        if not grid_widget: return

        menu = QMenu(self)
        del_action = menu.addAction(f"Delete ({len(self.selected_thumbnails)})")
        del_action.setEnabled(bool(self.selected_thumbnails))
        del_action.triggered.connect(self.delete_selected_images)
        
        menu.addSeparator()
        sel_all_action = menu.addAction("Select All")
        sel_all_action.triggered.connect(self._select_all_images)

        menu.exec(grid_widget.mapToGlobal(pos))
        
    # =========================================================================
    # === 5. Penanganan Event Sistem (Overrides) ===
    # =========================================================================

    def dragEnterEvent(self, event):
        """Menerima drag event jika berisi file gambar dan proyek aktif."""
        if self.project_id is not None and event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Memproses file yang di-drop dan mengirim sinyal untuk impor."""
        paths = [
            url.toLocalFile() for url in event.mimeData().urls()
            if url.isLocalFile() and url.toLocalFile().lower().endswith(
                ('.png', '.jpg', '.jpeg', '.bmp', '.tif'))
        ]
        if paths:
            self.images_to_import_selected.emit(paths)

    def keyPressEvent(self, event):
        """Menangani shortcut keyboard (Ctrl+A untuk Select All, Delete)."""
        if event.matches(QKeySequence.StandardKey.SelectAll):
            self._select_all_images()
        elif event.key() == Qt.Key.Key_Delete and self.selected_thumbnails:
            self.delete_selected_images()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, watched, event):
        """Mendeteksi double-click pada label judul untuk memulai rename."""
        if (watched == self.title_label and 
            event.type() == QEvent.MouseButtonDblClick and 
            self.project_id is not None):
            self.rename_project_requested.emit(self.title_label.text()) 
            return True
        return super().eventFilter(watched, event)

    # =========================================================================
    # === 6. Slot & Metode Bantuan (Helpers) ===
    # =========================================================================

    @Slot(QImage, str)
    def _update_thumbnail(self, image, image_path):
        """Slot callback dari ThumbnailLoader untuk menampilkan gambar thumbnail."""
        if image.isNull() or not self.scroll_area.widget(): return
        layout = self.scroll_area.widget().layout()
        if not layout: return

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget) and widget.image_path == image_path:
                widget.set_pixmap(QPixmap.fromImage(image))
                break

    def _create_placeholder_widget(self, html_text):
        """Membuat widget label untuk ditampilkan saat grid kosong."""
        label = QLabel(html_text)
        label.setTextFormat(Qt.TextFormat.RichText)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("QLabel { color: #888; font-size: 14px; }")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        return container