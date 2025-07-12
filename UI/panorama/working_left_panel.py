from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFrame,
    QLabel,
    QScrollArea,
    QGridLayout,
    QTabWidget,
    QComboBox,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QDialog,
    QGraphicsScene,
    QMenu,
    QStackedWidget,
)
from PIL import Image, ImageOps
from PIL.ImageQt import ImageQt
from PySide6.QtCore import Qt, Slot, Signal, QEvent, QPoint, QTimer, QSize
from PySide6.QtGui import (
    QPixmap,
    QImage,
    QMouseEvent,
    QPainter,
    QColor,
    QKeySequence,
    QIcon,
)

from UI.enhance_stack.components.batch_page_layout.thumbnail import (
    ThumbnailLoader,
    stop_process_thumbnails,
)
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable
from UI.panorama.display_area.display_panel import DisplayPanel


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


class WorkingLeftPanel(QWidget):
    rename_project_requested = Signal(int, str)
    selection_changed = Signal(int)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        # --- Variabel State ---
        self.current_project_id = None
        self.projects_exist = False
        self.thumbnail_threads = []
        self.selected_thumbnails = set()
        self.last_clicked_index = -1
        self.preview_stage = "grid"
        self.latest_successful_stage = "grid"

        # --- Setup Layout Utama ---
        left_panel_layout = QVBoxLayout(self)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(10)

        display_area = self._create_display_area()
        self.workflow_container = self.create_workflow_container()
        self.workflow_container.setVisible(False)  # Awalnya sembunyikan semua workflow

        left_panel_layout.addWidget(display_area, 1)  # Beri stretch factor 1
        left_panel_layout.addWidget(self.workflow_container)

        self.setAcceptDrops(True)
        self.clear_display()

    def _create_display_area(self):
        """Membuat area display utama yang berisi judul dan QStackedWidget."""
        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)

        # --- Header ---
        self.title_label = QLabel("No Project Selected")
        self.title_label.setObjectName("sectionTitle")
        self.title_label.installEventFilter(self)

        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton")
        self.import_button.setVisible(False)

        self.back_to_grid_button = QPushButton("Back to Import Images")
        self.back_to_grid_button.setVisible(False)

        self.import_button.clicked.connect(self.import_images)
        self.back_to_grid_button.clicked.connect(self.show_grid_view)

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

        return display_container

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

    def create_workflow_container(self):
        """Menciptakan kontainer elegan untuk tab dan tombol pratinjau."""
        container = QFrame()
        container.setObjectName("workflowContainer")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # --- Bagian Atas: Panel Tab ---
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._update_preview_button_state)

        alignment_content = self._create_alignment_tab_content()
        projection_content = self._create_projection_tab_content()
        blending_content = self._create_blending_tab_content()

        self.tab_widget.addTab(alignment_content, "Align gambar")
        self.tab_widget.addTab(projection_content, "Projection dan Crop")
        self.tab_widget.addTab(blending_content, "Blending")

        # --- Bagian Bawah: Area Tombol ---
        self.preview_button = QPushButton("Start Preview")
        self.preview_button.setVisible(False)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)

        # --- Gabungkan dengan Stretch Factor ---
        layout.addWidget(self.tab_widget, 3)
        layout.addLayout(button_layout, 1)

        return container

    def _create_alignment_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Alignment Algorithm:"))
        combo_layout = QHBoxLayout()
        self.combo_align = QComboBox()
        self.combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        self.combo_align.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "align_algorithm")
        )
        combo_layout.addWidget(self.combo_align)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        return content

    def _create_projection_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Projection Type:"))
        combo_layout = QHBoxLayout()
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        self.combo_proj.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "projection_type")
        )
        combo_layout.addWidget(self.combo_proj)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Set Region:"))
        button_layout = QHBoxLayout()
        btn_auto = QPushButton("Auto")
        btn_manual = QPushButton("Manual")
        button_layout.addWidget(btn_auto)
        button_layout.addWidget(btn_manual)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        return content

    def _create_blending_tab_content(self):
        content = QWidget()
        main_layout = QVBoxLayout(content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Blending Method:"))
        combo_layout_1 = QHBoxLayout()
        self.combo_blend = QComboBox()
        self.combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        self.combo_blend.currentTextChanged.connect(
            lambda v: self._on_workflow_setting_changed(v, "blending_method")
        )
        combo_layout_1.addWidget(self.combo_blend)
        combo_layout_1.addStretch()
        main_layout.addLayout(combo_layout_1)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Anti-ghosting:"))
        combo_layout_2 = QHBoxLayout()
        combo_ghost = QComboBox()
        combo_ghost.addItems(
            ["None", "Simple", "Dynamic"]
        )  # Anda mungkin ingin menyimpan referensi ini juga
        combo_layout_2.addWidget(combo_ghost)
        combo_layout_2.addStretch()
        main_layout.addLayout(combo_layout_2)
        main_layout.addStretch()
        return content

    def show_grid_view(self):
        self.preview_stage = "grid"
        self.display_stack.setCurrentWidget(self.grid_view_widget)
        if self.current_project_id:
            self.import_button.setVisible(True)
        self.back_to_grid_button.setVisible(False)
        self._update_preview_button_state()

    def show_preview_view(self):
        self.display_stack.setCurrentWidget(self.preview_view_widget)
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(True)
        self._update_preview_button_state()

    def _update_tab_states(self):
        tab_widget = self.tab_widget
        tab_widget.setTabEnabled(0, True)
        tab_widget.setTabEnabled(
            1, self.latest_successful_stage in ["aligned", "projected", "blended"]
        )
        tab_widget.setTabEnabled(
            2, self.latest_successful_stage in ["projected", "blended"]
        )

    def _update_preview_button_state(self):
        """
        Mengubah ikon, tooltip, dan fungsi tombol pratinjau berdasarkan konteks.
        """
        has_images = (
            self.scroll_area.widget()
            and isinstance(self.scroll_area.widget().layout(), QGridLayout)
            and self.scroll_area.widget().layout().count() > 0
        )
        is_visible = self.current_project_id is not None and (
            self.preview_stage != "grid" or has_images
        )

        self.preview_button.setVisible(is_visible)
        if not is_visible:
            return

        current_tab_index = self.tab_widget.currentIndex()

        # === PERUBAHAN UTAMA DI SINI ===

        # Definisikan path ikon dan teks tooltip
        actions = {
            0: {
                "icon_path": "UI/resources/icon/Align_Images.png",
                "tooltip": "Generate Alignment Preview",
                "slot": self.start_alignment_preview,
            },
            1: {
                "icon_path": "UI/resources/icon/Projection_crop.png",
                "tooltip": "Update Projection Preview",
                "slot": self.update_projection_preview,
            },
            2: {
                "icon_path": "UI/resources/icon/Blending.png",
                "tooltip": "Update Blending Preview",
                "slot": self.update_blending_preview,
            },
        }

        # Ambil aksi yang sesuai dengan tab saat ini
        action = actions.get(current_tab_index)

        if action:
            # Hapus teks dari tombol
            self.preview_button.setText("")

            # Atur ikon baru
            icon = QIcon(action["icon_path"])
            self.preview_button.setIcon(icon)
            # Atur ukuran ikon agar tidak terlalu besar di dalam tombol
            self.preview_button.setIconSize(QSize(32, 32))

            # Atur tooltip
            self.preview_button.setToolTip(action["tooltip"])

            # Hubungkan sinyal `clicked` ke slot yang benar
            try:
                self.preview_button.clicked.disconnect()
            except RuntimeError:
                pass  # Abaikan jika tidak ada koneksi sebelumnya
            self.preview_button.clicked.connect(action["slot"])

    # --- Dummy Functions untuk Simulasi Proses ---
    def start_alignment_preview(self):
        print("SIMULASI: Memulai proses alignment...")
        self.preview_label.setText("Processing Alignment...")
        self.show_preview_view()
        QTimer.singleShot(1500, self.on_alignment_finished)

    def on_alignment_finished(self):
        print("SIMULASI: Proses alignment selesai.")
        self.preview_label.setText("DUMMY ALIGNMENT RESULT")
        self.preview_stage = "aligned"
        self.latest_successful_stage = "aligned"
        self._update_tab_states()
        self.tab_widget.setCurrentIndex(1)

    def update_projection_preview(self):
        print("SIMULASI: Memperbarui proyeksi...")
        self.preview_label.setText("Updating Projection...")
        # (Dalam aplikasi nyata, Anda akan menjalankan thread di sini)
        QTimer.singleShot(1500, self.on_projection_finished)

    def update_projection_preview(self):
        print("SIMULASI: Memperbarui proyeksi...")
        self.preview_label.setText("Updating Projection...")
        QTimer.singleShot(1000, self.on_projection_finished)

    def on_projection_finished(self):
        print("SIMULASI: Proses proyeksi selesai.")
        self.preview_label.setText("DUMMY PROJECTION RESULT")
        self.preview_stage = "projected"
        self.latest_successful_stage = "projected"
        self._update_tab_states()
        self.tab_widget.setCurrentIndex(2)

    def update_blending_preview(self):
        print("SIMULASI: Memperbarui blending...")
        self.preview_label.setText("Updating Blending...")
        QTimer.singleShot(1000, self.on_blending_finished)

    def on_blending_finished(self):
        print("SIMULASI: Proses blending selesai.")
        self.preview_label.setText("DUMMY FINAL PREVIEW")
        self.preview_stage = "blended"
        self.latest_successful_stage = "blended"
        self._update_tab_states()

    @Slot()
    def clear_display(self):
        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        self.title_label.setText("No Project Selected")
        self.current_project_id = None
        self.import_button.setVisible(False)
        self.back_to_grid_button.setVisible(False)
        self.workflow_container.setVisible(False)
        self.preview_button.setVisible(False)
        self.preview_stage = "grid"
        self.latest_successful_stage = "grid"
        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()
        html_text = (
            "<p align='center'>Please select a project or create a new one.</p>"
            if self.projects_exist
            else "<p align='center'>No panorama projects found.<br>Click 'Add Pano' to create your first project.</p>"
        )
        placeholder = self._create_placeholder_widget(html_text)
        self.scroll_area.setWidget(placeholder)
        self.show_grid_view()

    def load_images_for_project(self, project_id):
        self.show_grid_view()
        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        image_paths = self.database_manager.get_images_for_project(project_id)
        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()
        if not image_paths:
            html_text = """<p align="center">No images in this project.<br><br>Drag & drop files here or use the 'Import Images' button.</p>"""
            placeholder = self._create_placeholder_widget(html_text)
            self.scroll_area.setWidget(placeholder)
        else:
            grid_widget = QWidget()
            grid_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            grid_widget.customContextMenuRequested.connect(self._show_context_menu)
            grid_layout = QGridLayout(grid_widget)
            grid_layout.setSpacing(10)
            grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            for i, path in enumerate(image_paths):
                row, col = i // 8, i % 8
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
        self._update_preview_button_state()

    @Slot(QImage, str)
    def _update_thumbnail(self, image, image_path):
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

    def keyPressEvent(self, event):
        """Menangani penekanan tombol keyboard."""
        if event.matches(QKeySequence.StandardKey.SelectAll):  # Cek untuk CTRL+A
            print("Ctrl+A pressed. Calling _select_all_images.")
            self._select_all_images()
            event.accept()
        elif event.key() == Qt.Key_Delete and self.selected_thumbnails:
            print("Delete key pressed. Calling delete_selected_images.")
            self.delete_selected_images()
            event.accept()
        else:
            super().keyPressEvent(event)

    @Slot(str, QMouseEvent)
    def _on_thumbnail_clicked(self, image_path, event):
        modifiers = event.modifiers()
        button = event.button()
        grid_layout = self.scroll_area.widget().layout()
        if not isinstance(grid_layout, QGridLayout):
            return

        clicked_widget = self.sender()  # Dapatkan widget yang memancarkan sinyal
        clicked_index = grid_layout.indexOf(clicked_widget)

        # === PERUBAHAN 2: Logika klik kanan yang disempurnakan ===
        if button == Qt.MouseButton.RightButton:
            if not clicked_widget.is_selected():
                for thumb in list(self.selected_thumbnails):
                    thumb.set_selected(False)
                self.selected_thumbnails.clear()
                clicked_widget.set_selected(True)
                self.selected_thumbnails.add(clicked_widget)
                self.last_clicked_index = clicked_index

        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            if clicked_widget.is_selected():
                clicked_widget.set_selected(False)
                self.selected_thumbnails.discard(clicked_widget)
            else:
                clicked_widget.set_selected(True)
                self.selected_thumbnails.add(clicked_widget)
            self.last_clicked_index = clicked_index

        elif (
            modifiers == Qt.KeyboardModifier.ShiftModifier
            and self.last_clicked_index != -1
        ):
            start = min(self.last_clicked_index, clicked_index)
            end = max(self.last_clicked_index, clicked_index)
            for thumb in list(self.selected_thumbnails):
                thumb.set_selected(False)
            self.selected_thumbnails.clear()
            for i in range(start, end + 1):
                widget = grid_layout.itemAt(i).widget()
                widget.set_selected(True)
                self.selected_thumbnails.add(widget)

        else:  # Klik biasa
            for thumb in list(self.selected_thumbnails):
                thumb.set_selected(False)
            self.selected_thumbnails.clear()
            clicked_widget.set_selected(True)
            self.selected_thumbnails.add(clicked_widget)
            self.last_clicked_index = clicked_index

        # Pancarkan sinyal bahwa seleksi telah berubah
        # self.selection_changed.emit(len(self.selected_thumbnails))

    @Slot(str)
    def _on_thumbnail_double_clicked(self, image_path):
        dialog = ImagePreviewDialog(image_path, self)
        dialog.exec()

    @Slot(QPoint)
    def _show_context_menu(self, pos):
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

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        self.title_label.setText(project_name)
        self.current_project_id = project_id
        self.workflow_container.setVisible(True)
        self.load_images_for_project(project_id)
        self._load_workflow_settings(project_id)
        self.latest_successful_stage = "grid"
        self._update_tab_states()
        self.tab_widget.setCurrentIndex(0)

    def _load_workflow_settings(self, project_id):
        settings = self.database_manager.get_project_workflow_settings(project_id)
        if settings:
            self.combo_align.setCurrentText(settings.get("align_algorithm", "AKAZE"))
            self.combo_proj.setCurrentText(
                settings.get("projection_type", "Cylindrical")
            )
            self.combo_blend.setCurrentText(
                settings.get("blending_method", "Multi-band")
            )

    @Slot(str)
    def _on_workflow_setting_changed(self, value, setting_key):
        if self.current_project_id:
            self.database_manager.save_project_workflow_setting(
                self.current_project_id, setting_key, value
            )

    @Slot(bool)
    def on_project_existence_changed(self, exists):
        self.projects_exist = exists
        if not self.current_project_id:
            self.clear_display()

    def eventFilter(self, watched_object, event):
        if (
            watched_object == self.title_label
            and event.type() == QEvent.MouseButtonDblClick
        ):
            if self.current_project_id:
                self.rename_project_requested.emit(
                    self.current_project_id, self.title_label.text()
                )
                return True
        return super().eventFilter(watched_object, event)

    def dragEnterEvent(self, event):
        if not self.current_project_id:
            event.ignore()
            return
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
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

    def import_images(self):
        if not self.current_project_id:
            QMessageBox.warning(
                self, "No Project", "Please select a project before importing images."
            )
            return
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Images for Panorama",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tif)",
        )
        if file_paths:
            self.process_imported_images(file_paths)

    def process_imported_images(self, file_paths):
        if not self.current_project_id:
            return
        success = self.database_manager.add_images_to_project(
            self.current_project_id, file_paths
        )
        if success:
            self.load_images_for_project(self.current_project_id)
        else:
            QMessageBox.critical(
                self, "Database Error", "Failed to save images to the project."
            )

    def workflow_panel(self):
        # === PERUBAHAN: Hubungkan sinyal `currentChanged` ===
        tab_widget = QTabWidget()
        tab_widget.currentChanged.connect(self._update_preview_button_state)
        tab_widget.addTab(self.alignment_tab(), "Align gambar")
        tab_widget.addTab(self.projection_tab(), "Projection dan Crop")
        tab_widget.addTab(self.blending_tab(), "Blending")
        return tab_widget

    def alignment_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(QLabel("Alignment Algorithm:"))
        combo_layout = QHBoxLayout()
        self.combo_align = QComboBox()
        self.combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        self.combo_align.currentTextChanged.connect(
            lambda value: self._on_workflow_setting_changed(value, "align_algorithm")
        )
        combo_layout.addWidget(self.combo_align)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)
        return tab_content

    def projection_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(QLabel("Projection Type:"))
        combo_layout = QHBoxLayout()
        self.combo_proj = QComboBox()
        self.combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        self.combo_proj.currentTextChanged.connect(
            lambda value: self._on_workflow_setting_changed(value, "projection_type")
        )
        combo_layout.addWidget(self.combo_proj)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)

        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Set Region:"))
        button_layout = QHBoxLayout()
        btn_auto = QPushButton("Auto")
        btn_manual = QPushButton("Manual")
        button_layout.addWidget(btn_auto)
        button_layout.addWidget(btn_manual)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        main_layout.addStretch()
        return tab_content

    def blending_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(QLabel("Blending Method:"))
        combo_layout_1 = QHBoxLayout()
        self.combo_blend = QComboBox()
        self.combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        self.combo_blend.currentTextChanged.connect(
            lambda value: self._on_workflow_setting_changed(value, "blending_method")
        )
        combo_layout_1.addWidget(self.combo_blend)
        combo_layout_1.addStretch()
        main_layout.addLayout(combo_layout_1)
        main_layout.addSpacing(10)
        main_layout.addWidget(QLabel("Anti-ghosting:"))
        combo_layout_2 = QHBoxLayout()
        combo_ghost = QComboBox()
        combo_ghost.addItems(["None", "Simple", "Dynamic"])
        combo_layout_2.addWidget(combo_ghost)
        combo_layout_2.addStretch()
        main_layout.addLayout(combo_layout_2)
        main_layout.addStretch()
        return tab_content

    def _select_all_images(self):
        """Memilih semua thumbnail di grid."""
        layout = self.scroll_area.widget().layout()
        if not isinstance(layout, QGridLayout):
            return

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if isinstance(widget, ThumbnailWidget):
                widget.set_selected(True)
                self.selected_thumbnails.add(widget)
       
    @Slot()
    def delete_selected_images(self):
        """Menghapus gambar yang dipilih dari DB dan UI."""
        if not self.selected_thumbnails:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to remove these {len(self.selected_thumbnails)} images from the project?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            paths_to_delete = [widget.image_path for widget in self.selected_thumbnails]
            success = self.database_manager.delete_images_from_project(
                self.current_project_id, paths_to_delete
            )
            if success:
                self.load_images_for_project(self.current_project_id)
            else:
                QMessageBox.critical(
                    self, "Database Error", "Failed to delete images from the project."
                )