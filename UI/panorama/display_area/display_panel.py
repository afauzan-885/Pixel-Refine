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

from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt

from UI.enhance_stack.components.batch_page_layout.thumbnail import (
    ThumbnailLoader,
    stop_process_thumbnails,
)
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable


class ImagePreviewDialog(QDialog):
    """Dialog yang menampilkan gambar dengan orientasi dan ukuran awal yang benar."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {image_path}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        scene = QGraphicsScene(self)
        self.view = Zoomable(scene, self)
        layout.addWidget(self.view)

        # === PERUBAHAN 2: Gunakan Pillow untuk memuat gambar dengan benar ===
        pixmap = self.load_pixmap_with_correct_orientation(image_path)

        if pixmap and not pixmap.isNull():
            scene.addPixmap(pixmap)
            # fitInView akan bekerja dengan benar sekarang karena dimensi pixmap sudah tepat
            self.view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            # Tampilkan pesan error jika gambar gagal dimuat
            error_label = QLabel(f"Failed to load image:\n{image_path}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

    # === PERUBAHAN 3: Fungsi pembantu baru untuk logika pemuatan ===
    def load_pixmap_with_correct_orientation(self, image_path: str) -> QPixmap | None:
        """
        Membuka file gambar menggunakan Pillow, menerapkan orientasi EXIF,
        dan mengonversinya menjadi QPixmap.
        """
        try:
            # 1. Buka dengan Pillow
            pil_image = Image.open(image_path)

            # 2. Terapkan orientasi dari metadata EXIF
            oriented_pil_image = ImageOps.exif_transpose(pil_image)

            # 3. Konversi dari gambar Pillow ke QImage
            qimage = ImageQt(oriented_pil_image)

            # 4. Konversi dari QImage ke QPixmap
            return QPixmap.fromImage(qimage)

        except Exception as e:
            print(f"Error loading image with Pillow for preview: {e}")
            return None


class ThumbnailWidget(QWidget):
    """Widget kustom untuk setiap thumbnail, menggunakan paintEvent untuk seleksi."""

    clicked = Signal(str, QMouseEvent)
    double_clicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._is_selected = False

        self.setFixedSize(110, 110)
        self.setObjectName("thumbnailWidget")  # Ini akan mengambil style dari QSS utama

        # Layout kembali sederhana
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        self.image_label = QLabel("Loading...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

    def set_pixmap(self, pixmap: QPixmap):
        scaled_pixmap = pixmap.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setText("")

    def set_selected(self, selected: bool):
        """
        Mengubah status seleksi dan memicu penggambaran ulang (repaint).
        """
        if self._is_selected != selected:
            self._is_selected = selected
            self.update()

    def is_selected(self):
        return self._is_selected

    def paintEvent(self, event):
        """
        Menggambar widget. Jika terpilih, gambar lapisan overlay di atasnya.
        """
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

    # --- Logika Internal & Event Handling ---

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
            if not clicked_widget.is_selected():
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

        # self.selection_changed.emit(len(self.selected_thumbnails)) # Aktifkan jika perlu

    def _clear_selection(self):
        """Membatalkan pilihan semua thumbnail."""
        for thumb in list(self.selected_thumbnails):
            thumb.set_selected(False)
        self.selected_thumbnails.clear()

    def _select_one_thumbnail(self, widget):
        """Memilih satu thumbnail saja."""
        widget.set_selected(True)
        self.selected_thumbnails.add(widget)

    def _toggle_thumbnail_selection(self, widget):
        """Menambah atau mengurangi satu thumbnail dari seleksi."""
        if widget.is_selected():
            widget.set_selected(False)
            self.selected_thumbnails.discard(widget)
        else:
            widget.set_selected(True)
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
        if self.current_project_id and event.mimeData().hasUrls():
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
            self.process_imported_images(image_paths)

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
            and self.current_project_id
        ):
            self.rename_project_requested.emit(
                self.current_project_id, self.title_label.text()
            )
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
