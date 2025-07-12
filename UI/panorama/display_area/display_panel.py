# display_panel.py

from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QPoint,
    QEvent,
    QSize,
    QModelIndex,
    QItemSelectionModel,
)
from PySide6.QtGui import (
    QImage,
    QPixmap,
    QPainter,
    QColor,
    QMouseEvent,
    QKeySequence,
    QIcon,
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
)

# === SEMUA KELAS TERKAIT THUMBNAIL & PREVIEW PINDAH KE SINI ===
# (ImagePreviewDialog, ThumbnailWidget)
# Ini logis karena mereka adalah bagian dari 'display'

# Kelas-kelas ini (ImagePreviewDialog, ThumbnailWidget, dan dependensi lainnya seperti
# ThumbnailLoader dan Zoomable) harus didefinisikan di sini atau diimpor
# ke dalam file ini jika mereka berada di file utilitas terpisah.
# Untuk contoh ini, saya akan menempatkan definisi yang relevan langsung di sini.
# Pastikan Anda mengimpor dependensi yang diperlukan seperti Image, ImageOps, ImageQt dari Pillow.

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

# Asumsikan ThumbnailLoader dan Zoomable sudah ada dan bisa diimpor
# from .thumbnail_loader import ThumbnailLoader, stop_process_thumbnails
# from .zoomable_view import Zoomable


class ImagePreviewDialog(QDialog):
    """Dialog yang menampilkan gambar dengan orientasi dan ukuran awal yang benar."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {image_path}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        scene = QGraphicsScene(self)
        # Asumsikan 'Zoomable' adalah QGraphicsView kustom Anda
        # self.view = Zoomable(scene, self)
        # layout.addWidget(self.view)

        pixmap = self.load_pixmap_with_correct_orientation(image_path)

        if pixmap and not pixmap.isNull():
            scene.addPixmap(pixmap)
            # self.view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            error_label = QLabel(f"Failed to load image:\n{image_path}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

    def load_pixmap_with_correct_orientation(self, image_path: str) -> QPixmap | None:
        try:
            pil_image = Image.open(image_path)
            oriented_pil_image = ImageOps.exif_transpose(pil_image)
            qimage = ImageQt(oriented_pil_image)
            return QPixmap.fromImage(qimage)
        except Exception as e:
            print(f"Error loading image with Pillow for preview: {e}")
            return None


class ThumbnailWidget(QWidget):
    """Widget kustom untuk setiap thumbnail."""
    clicked = Signal(str, QMouseEvent)
    double_clicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._is_selected = False
        self.setFixedSize(110, 110)
        self.setObjectName("thumbnailWidget")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

    def set_pixmap(self, pixmap: QPixmap):
        scaled_pixmap = pixmap.scaled(
            100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")

    def set_selected(self, selected: bool):
        if self._is_selected != selected:
            self._is_selected = selected
            self.update()

    def is_selected(self):
        return self._is_selected

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._is_selected:
            painter = QPainter(self)
            overlay_color = QColor(0, 120, 212, 128)
            painter.setBrush(overlay_color)
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.image_path, event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.image_path)


class DisplayPanel(QFrame):
    # Sinyal yang akan dikirim ke kelas koordinator (WorkingLeftPanel)
    import_requested = Signal()
    back_to_grid_requested = Signal()
    images_dropped = Signal(list)
    rename_project_requested = Signal()
    thumbnail_clicked = Signal(str, QMouseEvent)
    thumbnail_double_clicked = Signal(str)
    delete_selected_requested = Signal()
    select_all_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("displayContainer")
        self.setAcceptDrops(True)

        # === Variabel State Internal ===
        self.thumbnail_threads = [] # Anda perlu mengimpor ThumbnailLoader dan stop_process_thumbnails
        self.selected_thumbnails = set()

        container_layout = QVBoxLayout(self)

        # --- Header ---
        self.title_label = QLabel("No Project Selected")
        self.title_label.setObjectName("sectionTitle")
        self.title_label.installEventFilter(self)

        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton")
        self.import_button.setVisible(False)
        self.import_button.clicked.connect(self.import_requested.emit)

        self.back_to_grid_button = QPushButton("Back to Import Images")
        self.back_to_grid_button.setVisible(False)
        self.back_to_grid_button.clicked.connect(self.back_to_grid_requested.emit)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.import_button)
        header_layout.addWidget(self.back_to_grid_button)
        container_layout.addLayout(header_layout)

        # --- Stack untuk menukar Grid dan Preview ---
        self.display_stack = QStackedWidget()
        container_layout.addWidget(self.display_stack)

        # Halaman 0: Grid View
        self.grid_view_widget = QWidget()
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        grid_view_layout.addWidget(self.scroll_area)

        # Halaman 1: Preview View
        self.preview_view_widget = QWidget()
        preview_view_layout = QVBoxLayout(self.preview_view_widget)
        self.preview_label = QLabel("Panorama preview will appear here.")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_view_layout.addWidget(self.preview_label)

        self.display_stack.addWidget(self.grid_view_widget)
        self.display_stack.addWidget(self.preview_view_widget)

    # --- Metode Publik untuk dikontrol oleh WorkingLeftPanel ---

    def set_title(self, text):
        self.title_label.setText(text)

    def get_title(self):
        return self.title_label.text()
        
    def show_import_button(self, visible):
        self.import_button.setVisible(visible)

    def show_back_to_grid_button(self, visible):
        self.back_to_grid_button.setVisible(visible)

    def show_grid_view(self):
        self.display_stack.setCurrentWidget(self.grid_view_widget)

    def show_preview_view(self, text=None):
        if text:
            self.preview_label.setText(text)
        self.display_stack.setCurrentWidget(self.preview_view_widget)
        
    def set_preview_text(self, text):
        self.preview_label.setText(text)

    def _create_placeholder_widget(self, html_text):
        placeholder_label = QLabel()
        placeholder_label.setTextFormat(Qt.TextFormat.RichText)
        placeholder_label.setText(html_text)
        placeholder_label.setWordWrap(True)
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(
            "QLabel { color: #777; font-size: 16px; border: none; background-color: transparent; padding: 20px; }"
        )
        container_widget = QWidget()
        v_layout = QVBoxLayout(container_widget)
        v_layout.addStretch(1)
        v_layout.addWidget(placeholder_label)
        v_layout.addStretch(1)
        return container_widget

    def clear_grid(self, placeholder_html):
        # stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()
        placeholder = self._create_placeholder_widget(placeholder_html)
        self.scroll_area.setWidget(placeholder)

    def populate_grid(self, image_paths, database_manager):
        # stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        
        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        if not image_paths:
            html_text = """<p align="center">No images in this project.<br><br>Drag & drop files here or use the 'Import Images' button.</p>"""
            placeholder = self._create_placeholder_widget(html_text)
            self.scroll_area.setWidget(placeholder)
            return False # Mengindikasikan tidak ada gambar

        grid_widget = QWidget()
        grid_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        grid_widget.customContextMenuRequested.connect(self._show_context_menu)
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(10)
        grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        for i, path in enumerate(image_paths):
            row, col = i // 8, i % 8
            thumbnail_widget = ThumbnailWidget(path)
            # Hubungkan sinyal dari widget ke sinyal panel ini
            thumbnail_widget.clicked.connect(self.thumbnail_clicked.emit)
            thumbnail_widget.double_clicked.connect(self.thumbnail_double_clicked.emit)
            grid_layout.addWidget(thumbnail_widget, row, col)
            
            # Logika threading tetap sama
            # thread = ThumbnailLoader(path)
            # thread.thumbnail_ready.connect(self._update_thumbnail)
            # thread.start()
            # self.thumbnail_threads.append(thread)

        self.scroll_area.setWidget(grid_widget)
        return True # Mengindikasikan ada gambar

    @Slot(QImage, str)
    def _update_thumbnail(self, image, image_path):
        # Logika ini tetap sama
        if image.isNull() or not self.scroll_area.widget(): return
        layout = self.scroll_area.widget().layout()
        if not isinstance(layout, QGridLayout): return

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget) and widget.image_path == image_path:
                widget.set_pixmap(QPixmap.fromImage(image))
                break

    def get_selected_thumbnail_widgets(self):
        return self.selected_thumbnails
        
    def get_grid_layout(self):
        if self.scroll_area.widget() and isinstance(self.scroll_area.widget().layout(), QGridLayout):
            return self.scroll_area.widget().layout()
        return None

    # --- Penanganan Event ---
    def eventFilter(self, watched_object, event):
        if (
            watched_object == self.title_label
            and event.type() == QEvent.MouseButtonDblClick
        ):
            self.rename_project_requested.emit()
            return True
        return super().eventFilter(watched_object, event)
        
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        image_paths = [
            url.toLocalFile() for url in urls
            if url.isLocalFile() and url.toLocalFile().lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tif"))
        ]
        if image_paths:
            self.images_dropped.emit(image_paths)

    @Slot(QPoint)
    def _show_context_menu(self, pos):
        grid_widget = self.scroll_area.widget()
        if not grid_widget: return

        menu = QMenu(self)
        delete_action = menu.addAction(f"Delete Selected Image(s)")
        delete_action.setEnabled(len(self.selected_thumbnails) > 0)
        menu.addSeparator()
        select_all_action = menu.addAction("Select All")

        delete_action.triggered.connect(self.delete_selected_requested.emit)
        select_all_action.triggered.connect(self.select_all_requested.emit)

        menu.exec(grid_widget.mapToGlobal(pos))