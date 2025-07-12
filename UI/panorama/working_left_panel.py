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
    QStackedLayout
)
from PySide6.QtCore import Qt, Slot, Signal, QEvent, QPoint
from PySide6.QtGui import QPixmap, QImage, QMouseEvent

from UI.enhance_stack.components.batch_page_layout.thumbnail import (
    ThumbnailLoader,
    stop_process_thumbnails,
)
from UI.enhance_stack.logic.Zoomable_Handler import Zoomable


class ThumbnailWidget(QWidget):
    """Widget kustom untuk setiap thumbnail, menggunakan overlay untuk status seleksi."""
    clicked = Signal(str, QMouseEvent)
    double_clicked = Signal(str)

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._is_selected = False
        
        self.setFixedSize(110, 110)
        # Atur style dasar untuk border dan background di sini
        self.setObjectName("thumbnailWidget")
        # Kita akan pindahkan style ini ke QSS utama agar lebih konsisten
        
        # === PERUBAHAN UTAMA: Gunakan QStackedLayout ===
        stacked_layout = QStackedLayout(self)
        # Hapus margin agar overlay menutupi seluruh area
        stacked_layout.setContentsMargins(0, 0, 0, 0) 
        
        # Lapisan 1: Widget untuk menampung gambar (dengan padding)
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(5, 5, 5, 5)
        self.image_label = QLabel("...")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_layout.addWidget(self.image_label)
        
        # Lapisan 2: Widget overlay untuk efek seleksi
        self.overlay = QWidget(self)
        # Warna biru semi-transparan. #0078D4 adalah biru, 80 adalah alpha (sekitar 31%)
        self.overlay.setStyleSheet("background-color: rgba(0, 120, 212, 0.4); border-radius: 4px;")
        self.overlay.setVisible(False) # Awalnya tidak terlihat

        # Tambahkan kedua lapisan ke tumpukan. Overlay di atas gambar.
        stacked_layout.addWidget(image_container)
        stacked_layout.addWidget(self.overlay)
        
        # Set layout
        self.setLayout(stacked_layout)

    def set_pixmap(self, pixmap: QPixmap):
        self.image_label.setPixmap(
            pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                          Qt.TransformationMode.SmoothTransformation))
        self.image_label.setText("")

    def set_selected(self, selected: bool):
        """Mengontrol visibilitas lapisan overlay untuk menunjukkan seleksi."""
        self._is_selected = selected
        # Cukup tampilkan atau sembunyikan overlay
        self.overlay.setVisible(selected)

    def is_selected(self):
        return self._is_selected

    def mousePressEvent(self, event: QMouseEvent):
        self.clicked.emit(self.image_path, event)
        # super().mousePressEvent(event) # Tidak perlu dipanggil

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self.image_path)
        # super().mouseDoubleClickEvent(event) # Tidak perlu dipanggil
        
        
class ImagePreviewDialog(QDialog):
    """Dialog sederhana untuk menampilkan gambar dengan kemampuan zoom."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview - {image_path}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout(self)
        scene = QGraphicsScene(self)
        self.view = Zoomable(scene, self)
        layout.addWidget(self.view)

        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scene.addPixmap(pixmap)
            self.view.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)


class WorkingLeftPanel(QWidget):
    rename_project_requested = Signal(int, str)
    selection_changed = Signal(int)

    def __init__(self, database_manager, parent=None):
        super().__init__(parent)
        self.database_manager = database_manager

        self.current_project_id = None
        self.projects_exist = False
        self.thumbnail_threads = []
        self.selected_thumbnails = set()
        self.last_clicked_index = -1

        left_panel_layout = QVBoxLayout(self)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(10)

        display_area = self._create_display_area()
        workflow_panel = self.workflow_panel()
        workflow_panel.setMaximumHeight(270)

        left_panel_layout.addWidget(display_area, 3)
        left_panel_layout.addWidget(workflow_panel, 1)

        self.setAcceptDrops(True)
        self.clear_display()

    def _create_display_area(self):
        display_container = QFrame()
        display_container.setObjectName("displayContainer")
        container_layout = QVBoxLayout(display_container)

        self.title_label = QLabel("No Project Selected")
        self.title_label.setObjectName("sectionTitle")
        self.title_label.installEventFilter(self)

        self.import_button = QPushButton("Import Images")
        self.import_button.setObjectName("importButton")
        self.import_button.setVisible(False)
        self.import_button.clicked.connect(self.import_images)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.import_button)
        container_layout.addLayout(header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        container_layout.addWidget(self.scroll_area)

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

    @Slot()
    def clear_display(self):
        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()

        self.title_label.setText("No Project Selected")
        self.current_project_id = None
        self.import_button.setVisible(False)

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        if self.projects_exist:
            html_text = "<p align='center'>Please select a panorama project from the list on the right.</p>"
        else:
            html_text = "<p align='center'>No panorama projects found.<br>Click 'Add Pano' to create your first project.</p>"

        placeholder = self._create_placeholder_widget(html_text)
        self.scroll_area.setWidget(placeholder)
        self.selection_changed.emit(0)  # Beri tahu panel kanan tidak ada yang dipilih

    def load_images_for_project(self, project_id):
        stop_process_thumbnails(self.thumbnail_threads)
        self.selected_thumbnails.clear()
        self.selection_changed.emit(0)  # Reset seleksi

        if self.scroll_area.widget():
            self.scroll_area.takeWidget().deleteLater()

        image_paths = self.database_manager.get_images_for_project(project_id)

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
            # Jika item yang diklik kanan belum terpilih,
            # bersihkan seleksi lain dan pilih hanya item ini.
            if not clicked_widget.is_selected():
                # Deselect semua dulu
                for thumb in list(self.selected_thumbnails):
                    thumb.set_selected(False)
                self.selected_thumbnails.clear()
                # Select yang diklik kanan
                clicked_widget.set_selected(True)
                self.selected_thumbnails.add(clicked_widget)
                self.last_clicked_index = clicked_index

        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            # Seleksi CTRL: Toggle
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
        self.selection_changed.emit(len(self.selected_thumbnails))

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
        # Nonaktifkan jika tidak ada yang dipilih
        delete_action.setEnabled(len(self.selected_thumbnails) > 0)

        # Tambahkan aksi lain jika perlu
        menu.addSeparator()
        select_all_action = menu.addAction("Select All")

        # Hubungkan aksi
        delete_action.triggered.connect(self.delete_selected_images)
        select_all_action.triggered.connect(self._select_all_images)

        menu.exec(grid_widget.mapToGlobal(pos))

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
        self.selection_changed.emit(len(self.selected_thumbnails))

    @Slot()  # === PERUBAHAN 3: Jadikan slot publik untuk dipanggil dari panel kanan ===
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

    @Slot(int, str)
    def update_display_for_project(self, project_id, project_name):
        self.title_label.setText(project_name)
        self.current_project_id = project_id
        self.import_button.setVisible(True)
        self.load_images_for_project(project_id)

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
        tab_widget = QTabWidget()
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
        combo_align = QComboBox()
        combo_align.addItems(["AKAZE", "ORB", "SIFT", "BRISK"])
        combo_layout.addWidget(combo_align)
        combo_layout.addStretch()
        main_layout.addLayout(combo_layout)

        # main_layout.addSpacing(10)
        # main_layout.addWidget(QLabel("Parameter 1:"))
        # main_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        # main_layout.addSpacing(5)
        # main_layout.addWidget(QLabel("Parameter 2:"))
        # main_layout.addWidget(QSlider(Qt.Orientation.Horizontal))
        # main_layout.addStretch()
        return tab_content

    def projection_tab(self):
        tab_content = QWidget()
        main_layout = QVBoxLayout(tab_content)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(QLabel("Projection Type:"))
        combo_layout = QHBoxLayout()
        combo_proj = QComboBox()
        combo_proj.addItems(["Planar", "Cylindrical", "Spherical", "Fisheye"])
        combo_layout.addWidget(combo_proj)
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
        combo_blend = QComboBox()
        combo_blend.addItems(["Multi-band", "Feathering", "No Blending"])
        combo_layout_1.addWidget(combo_blend)
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
