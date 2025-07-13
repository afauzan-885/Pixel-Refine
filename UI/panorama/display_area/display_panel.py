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
    QPainter,
    QColor,
    QMouseEvent,
    QKeySequence,
    QPen
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
    QDialog,
    QGraphicsScene,
    QMessageBox,
    QFileDialog,
    QApplication
)

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from UI.enhance_stack.components.batch_page_layout.thumbnail import (
    ThumbnailLoader,
    stop_process_thumbnails,
)
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable
from UI.panorama.logic.processing_view import ProcessingView
from UI.resources.animation.animation_manager import StackedWidgetAnimator

class ImagePreviewDialog(QDialog):
    """Dialog yang menampilkan gambar dengan orientasi dan ukuran awal yang benar."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {image_path}")
        
        # <<< PERUBAHAN KUNCI ADA DI SINI >>>
        self.set_adaptive_initial_size()

        # Kode sisa __init__ tetap sama
        layout = QVBoxLayout(self)
        self.scene = QGraphicsScene(self)
        self.view = Zoomable(self.scene, self)
        layout.addWidget(self.view)

        self.pixmap_item = None
        pixmap = self.load_pixmap_with_correct_orientation(image_path)

        if pixmap and not pixmap.isNull():
            self.pixmap_item = self.scene.addPixmap(pixmap)
        else:
            error_label = QLabel(f"Failed to load image:\n{image_path}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.removeWidget(self.view)
            self.view.deleteLater()
            layout.addWidget(error_label)
            
    def set_adaptive_initial_size(self, width_ratio: float = 0.3, height_ratio: float = 0.5):
        """
        Mengatur ukuran dan posisi awal dialog agar relatif terhadap ukuran layar.
        """
        # 1. Dapatkan layar utama tempat aplikasi berjalan
        primary_screen = QApplication.primaryScreen()
        if not primary_screen:
            # Fallback jika tidak ada layar utama terdeteksi
            self.resize(800, 600)
            return

        # 2. Dapatkan geometri area yang tersedia di layar (tidak termasuk taskbar, dll.)
        available_geometry = primary_screen.availableGeometry()
        screen_width = available_geometry.width()
        screen_height = available_geometry.height()

        # 3. Hitung ukuran dialog berdasarkan rasio
        dialog_width = int(screen_width * width_ratio)
        dialog_height = int(screen_height * height_ratio)

        # 4. Atur ukuran dialog
        self.resize(dialog_width, dialog_height)
        
        # 5. Pusatkan dialog di tengah layar
        # Hitung posisi x dan y agar jendela berada di tengah
        x = available_geometry.x() + (screen_width - dialog_width) / 2
        y = available_geometry.y() + (screen_height - dialog_height) / 2
        self.move(int(x), int(y))
        
        # Atur ukuran minimum agar pengguna tidak bisa membuatnya terlalu kecil
        self.setMinimumSize(int(screen_width * 0.4), int(screen_height * 0.4))

    def load_pixmap_with_correct_orientation(self, image_path: str) -> QPixmap | None:
        """
        Membuka file gambar menggunakan Pillow, menerapkan orientasi EXIF,
        dan mengonversinya menjadi QPixmap.
        """
        try:
            pil_image = Image.open(image_path)
            oriented_pil_image = ImageOps.exif_transpose(pil_image)
            qimage = ImageQt(oriented_pil_image)
            return QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"Error loading image with Pillow for preview: {e}")
            return None

    # <<< PERBAIKAN KUNCI ADA DI SINI >>>
    def showEvent(self, event):
        """
        Dipanggil secara otomatis oleh Qt setelah dialog ditampilkan.
        Ini adalah tempat yang tepat untuk melakukan 'fitInView'.
        """
        # Selalu panggil implementasi parent terlebih dahulu
        super().showEvent(event)

        # Hanya lakukan fit jika pixmap berhasil dimuat
        if self.pixmap_item:
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event):
        """
        Opsional, tapi sangat disarankan: Lakukan fitInView lagi saat jendela di-resize.
        """
        super().resizeEvent(event)
        if self.pixmap_item:
            self.view.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
            

class ThumbnailWidget(QWidget):
    """Widget kustom untuk setiap thumbnail, menggunakan paintEvent untuk seleksi."""
    back_to_preview_requested = Signal() 
    clicked = Signal(str, QMouseEvent)
    double_clicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._is_selected = False

        self.setFixedSize(110, 110)
        self.setObjectName("thumbnailWidget")

        self.has_valid_preview = False
        layout = QVBoxLayout(self)
        # Beri sedikit margin agar border tidak menempel pada gambar
        layout.setContentsMargins(5, 5, 5, 5) 
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

    # Metode untuk menerima gambar dari thread
    def set_pixmap(self, pixmap: QPixmap):
        if not pixmap.isNull():
            self.pixmap = pixmap.scaled(
                100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(self.pixmap)
            
    def is_selected(self) -> bool:
        """Getter: Mengembalikan status terpilih."""
        return self._is_selected

    def set_selected(self, selected: bool):
        """
        Setter: Mengatur status terpilih dan memicu penggambaran ulang.
        """
        # Hanya proses jika status benar-benar berubah
        if self._is_selected != selected:
            self._is_selected = selected
            self.update() 
    
    def paintEvent(self, event):
        """
        Menggambar widget. Dipanggil secara otomatis oleh Qt saat 'update()' dipanggil.
        """
        # Selalu panggil implementasi parent terlebih dahulu
        super().paintEvent(event)

        # Hanya gambar efek visual jika widget ini sedang terpilih
        if self._is_selected:
            painter = QPainter(self)
            # Aktifkan antialiasing agar sudut-sudut terlihat lebih halus
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            # --- Definisikan Warna & Pena ---
            overlay_color = QColor(173, 216, 230, 128)

            # Warna border: Biru tua (misal: 0, 84, 166)
            border_color = QColor(0, 84, 166)
            
            # Siapkan pena (stroke) untuk border
            border_pen = QPen(border_color)
            border_pen.setWidth(2) # Ketebalan 5px

            # --- Atur Painter ---
            painter.setPen(border_pen)
            painter.setBrush(overlay_color)

            # --- Gambar Persegi Panjang ---
            pen_half_width = border_pen.width() / 2.0
            draw_rect = self.rect().adjusted(
                pen_half_width, pen_half_width, 
                -pen_half_width, -pen_half_width
            )
            
            # Gambar persegi panjang dengan sudut membulat agar lebih manis
            painter.drawRoundedRect(draw_rect, 4.0, 4.0)


    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.image_path, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.image_path)


class DisplayPanel(QWidget):
    # Sinyal yang akan dikirim ke kontroler/induk
    rename_project_requested = Signal(str)
    images_to_import_selected = Signal(list)
    images_to_delete_selected = Signal(list)
    selection_count_changed = Signal(int)
    back_to_grid_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Variabel State Lokal ---
        self.animator = StackedWidgetAnimator(self) 
        self.thumbnail_threads = []
        self.selected_thumbnails = set()
        self.last_clicked_index = -1
        self.project_id = None
        self.project_name = "No Project Selected"

        self._setup_ui()
        self.setAcceptDrops(True)
        self.clear_display(True)  # True untuk pesan "Tidak ada proyek"

    def _setup_ui(self):
        """Membangun semua elemen UI statis untuk panel ini."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)

        # Header
        self.title_label = QLabel()
        self.title_label.setObjectName("sectionTitle")
        self.title_label.installEventFilter(self)

        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton")
        self.import_button.clicked.connect(self.import_images)

        self.back_to_grid_button = QPushButton("Back to Import Images")
        self.back_to_grid_button.clicked.connect(self.back_to_grid_requested.emit)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.import_button)
        header_layout.addWidget(self.back_to_grid_button)
        container_layout.addLayout(header_layout)

        # Stack untuk menukar Grid dan Preview
        self.display_stack = QStackedWidget()
        container_layout.addWidget(self.display_stack)

        # View Grid
        self.grid_view_widget = QWidget()
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        grid_view_layout.addWidget(self.scroll_area)
        
        processing_container = QWidget()
        processing_layout = QVBoxLayout(processing_container)
        processing_layout.setContentsMargins(50, 50, 50, 50) # Margin
        self.processing_view = ProcessingView() # Widget kita
        processing_layout.addWidget(self.processing_view)

        # Halaman 2: Hasil Preview (Label seperti sebelumnya)
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tambahkan halaman-halaman baru ini ke display_stack
        self.display_stack.addWidget(self.grid_view_widget)
        self.display_stack.addWidget(processing_container)
        self.display_stack.addWidget(self.result_label)

        # View Preview
        self.preview_view_widget = QWidget()
        preview_layout = QVBoxLayout(self.preview_view_widget)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)

        self.display_stack.addWidget(self.grid_view_widget)
        self.display_stack.addWidget(self.preview_view_widget)

        main_layout.addWidget(display_container)

    # --- Slot Publik (Dipanggil oleh Kontroler) ---

    @Slot(int, str, list)
    def load_project(self, project_id, project_name, image_paths):
        """Memuat data proyek dan gambar ke dalam UI."""
        self.project_id = project_id
        self.project_name = project_name
        self.title_label.setText(project_name)

        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        if not image_paths:
            html_text = """<p align="center">No images in this project.<br><br>Drag & drop files here or use the 'Import Images' button.</p>"""
            self.scroll_area.setWidget(self._create_placeholder_widget(html_text))
        else:
            grid_widget = QWidget()
            grid_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            grid_widget.customContextMenuRequested.connect(self._show_context_menu)
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(10)
            grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            for i, path in enumerate(image_paths):
                row, col = i // 8, i % 8  # Asumsi 8 kolom
                thumbnail_widget = ThumbnailWidget(path)
                thumbnail_widget.clicked.connect(self._on_thumbnail_clicked)
                thumbnail_widget.double_clicked.connect(
                    self._on_thumbnail_double_clicked
                )
                grid_layout.addWidget(thumbnail_widget, row, col)
                thread = ThumbnailLoader(path)
                thread.thumbnail_ready.connect(self._update_thumbnail)
                thread.start()
                self.thumbnail_threads.append(thread)
            self.scroll_area.setWidget(grid_widget)

        self.show_grid_view()
        self.selection_count_changed.emit(0)

    @Slot(bool)
    def clear_display(self, no_projects_exist=False):
        """Membersihkan tampilan ke kondisi awal."""
        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        self.title_label.setText("No Project Selected")
        self.project_id = None

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        html_text = (
            "<p align='center'>No panorama projects found.<br>Click 'Add Pano' to create your first project.</p>"
            if no_projects_exist
            else "<p align='center'>Please select a project or create a new one.</p>"
        )
        self.scroll_area.setWidget(self._create_placeholder_widget(html_text))
        self.show_grid_view()
        self.selection_count_changed.emit(0)
        
    @Slot(str)
    def show_processing_view(self, title: str):
        """Beralih ke tampilan progress dan set judul awalnya."""
        self.processing_view.update_progress(title, 0)
        # Ambil widget kontainer dari stack
        processing_container = self.processing_view.parentWidget()
        self.display_stack.setCurrentWidget(processing_container)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)

    @Slot(str, int)
    def update_processing_progress(self, title: str, value: int):
        """Memperbarui progress di tampilan progress."""
        self.processing_view.update_progress(title, value)

    @Slot(str)
    def show_preview_result(self, message: str):
        """Beralih ke tampilan hasil dan tampilkan pesan."""
        self.result_label.setText(message)
        self.display_stack.setCurrentWidget(self.result_label)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)

    @Slot(str)
    def show_preview_message(self, message):
        """Menampilkan pesan di area preview."""
        self.preview_label.setText(message)
        self.display_stack.setCurrentWidget(self.preview_view_widget)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)

    @Slot()
    def show_grid_view(self):
        """Beralih ke tampilan grid."""
        self.display_stack.setCurrentWidget(self.grid_view_widget)
        self.import_button.setVisible(self.project_id is not None)
        self.back_to_grid_button.setVisible(False)

    def import_images(self):
        if not self.project_id:
            return
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.tif)"
        )
        if file_paths:
            self.images_to_import_selected.emit(file_paths)

    def delete_selected_images(self):
        if not self.selected_thumbnails:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to remove these {len(self.selected_thumbnails)} images?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            paths_to_delete = [widget.image_path for widget in self.selected_thumbnails]
            self.images_to_delete_selected.emit(paths_to_delete)

    @Slot(str, QMouseEvent)
    def _on_thumbnail_clicked(self, image_path, event):
        """Menangani logika kompleks untuk seleksi thumbnail."""
        modifiers = event.modifiers()
        button = event.button()
        grid_layout = self.scroll_area.widget().layout()
        if not isinstance(grid_layout, QGridLayout):
            return

        clicked_widget = self.sender()
        clicked_index = grid_layout.indexOf(clicked_widget)

        if button == Qt.MouseButton.RightButton:
            if not clicked_widget.is_selected(): # Panggilan fungsi is_selected()
                self._clear_selection()
                self._select_one_thumbnail(clicked_widget)
        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            self._toggle_thumbnail_selection(clicked_widget)
        elif (
            modifiers == Qt.KeyboardModifier.ShiftModifier
            and self.last_clicked_index != -1
        ):
            self._select_range(clicked_index)
        else:
            self._clear_selection()
            self._select_one_thumbnail(clicked_widget)

        self.last_clicked_index = clicked_index

    def _clear_selection(self):
        """Membatalkan pilihan semua thumbnail."""
        for thumb in list(self.selected_thumbnails):
            thumb.set_selected(False) # Panggil metode setter
        self.selected_thumbnails.clear()

    def _select_one_thumbnail(self, widget):
        """Memilih satu thumbnail saja."""
        widget.set_selected(True)
        self.selected_thumbnails.add(widget)

    def _toggle_thumbnail_selection(self, widget):
        """Menambah atau mengurangi satu thumbnail dari seleksi."""
        if widget.is_selected():
            widget.set_selected(False) # Panggil metode setter
            self.selected_thumbnails.discard(widget)
        else:
            widget.set_selected(True) # Panggil metode setter
            self.selected_thumbnails.add(widget)

    def _select_range(self, clicked_index):
        """Memilih rentang thumbnail (untuk Shift+klik)."""
        start = min(self.last_clicked_index, clicked_index)
        end = max(self.last_clicked_index, clicked_index)
        self._clear_selection()
        layout = self.scroll_area.widget().layout()
        for i in range(start, end + 1):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.set_selected(True)
                self.selected_thumbnails.add(widget)

    def _select_all_images(self):
        """Memilih semua thumbnail di grid."""
        layout = self.scroll_area.widget().layout()
        if not isinstance(layout, QGridLayout):
            return

        self._clear_selection()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.set_selected(True)
                self.selected_thumbnails.add(widget)

    @Slot(str)
    def _on_thumbnail_double_clicked(self, image_path):
        """Menampilkan dialog preview gambar saat double-click."""
        dialog = ImagePreviewDialog(image_path, self)
        dialog.exec()

    @Slot(QPoint)
    def _show_context_menu(self, pos):
        """Menampilkan menu klik-kanan pada grid."""
        grid_widget = self.scroll_area.widget()
        if not grid_widget:
            return

        menu = QMenu(self)
        delete_action = menu.addAction(f"Delete Selected Image(s)")
        delete_action.setEnabled(len(self.selected_thumbnails) > 0)
        menu.addSeparator()
        select_all_action = menu.addAction("Select All")

        delete_action.triggered.connect(self.delete_selected_images)
        select_all_action.triggered.connect(self._select_all_images)

        menu.exec(grid_widget.mapToGlobal(pos))

    @Slot(QImage, str)
    def _update_thumbnail(self, image, image_path):
        """Slot untuk menerima gambar thumbnail dari thread dan menampilkannya."""
        if image.isNull() or not self.scroll_area.widget():
            return
        layout = self.scroll_area.widget().layout()
        if not isinstance(layout, QGridLayout):
            return

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget) and widget.image_path == image_path:
                widget.set_pixmap(QPixmap.fromImage(image))
                break

    def dragEnterEvent(self, event):
        """Menerima event drag jika berisi URL file dan ada proyek yang aktif."""
        # PERBAIKAN: Gunakan self.project_id yang dimiliki oleh DisplayPanel
        if self.project_id is not None and event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Memproses file yang di-drop ke dalam widget."""
        urls = event.mimeData().urls()
        image_paths = [
            url.toLocalFile()
            for url in urls
            if url.isLocalFile()
            and url.toLocalFile()
            .lower()
            .endswith((".png", ".jpg", ".jpeg", ".bmp", ".tif"))
        ]
        if image_paths:
            # PERBAIKAN: Pancarkan sinyal dengan membawa daftar path gambar
            self.images_to_import_selected.emit(image_paths)

    def keyPressEvent(self, event):
        """Menangani shortcut keyboard (Ctrl+A, Delete)."""
        if event.matches(QKeySequence.StandardKey.SelectAll):
            self._select_all_images()
            event.accept()
        elif event.key() == Qt.Key_Delete and self.selected_thumbnails:
            self.delete_selected_images()
            event.accept()
        else:
            super().keyPressEvent(event)

    def eventFilter(self, watched_object, event):
        """Memfilter event, khususnya double-click pada judul untuk rename."""
        if (
            watched_object == self.title_label
            and event.type() == QEvent.MouseButtonDblClick
            and self.project_id is not None 
        ):
            self.rename_project_requested.emit(self.title_label.text()) 
            return True
        return super().eventFilter(watched_object, event)

    def _create_placeholder_widget(self, html_text):
        """Membuat widget placeholder standar."""
        placeholder_label = QLabel(html_text)
        placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        placeholder_label.setWordWrap(True)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet("QLabel { color: #777; font-size: 16px; }")
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.addStretch(1)
        v_layout.addWidget(placeholder_label)
        v_layout.addStretch(1)
        return container
