from PyQt6.QtWidgets import QGraphicsPixmapItem, QLabel
from PyQt6.QtCore import Qt, QEvent, QTimer

from UI.settings.General.Language import language_config
from .multi_threading import RawImageProcessingThread


def handle_image_ready(self, pixmap):
    """Tangani hasil gambar yang diproses."""
    self.original_pixmap = pixmap
    self.zoom_scale = 1.0
    self.fit_image_to_panel()


def handle_image_error(self, error_message):
    """Tangani error selama pemrosesan."""
    self.preview_scene.clear()
    label = QLabel(error_message)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.preview_scene.addWidget(label)


def update_preview_panel(self, selected_paths):
    
    self.preview_scene.clear()  # Hapus semua elemen dari scene sebelumnya

    if hasattr(self, "raw_thread") and self.raw_thread.isRunning():
        # Hentikan thread jika masih berjalan
        self.raw_thread.stop()
        self.raw_thread.quit
        return

    if selected_paths:
        # Tampilkan pesan loading sementara gambar diproses
        label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tambahkan label ke scene dengan QGraphicsProxyWidget
        proxy = self.preview_scene.addWidget(label)
        self.image_status_info(proxy)

        # Tambahkan jeda waktu 2 detik sebelum memulai proses gambar
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)  # Timer berjalan sekali
        self.preview_timer.timeout.connect(
            lambda: self.start_image_processing(selected_paths)
        )
        self.preview_timer.start(1000)
    else:
        self.original_pixmap = None

        # Tampilkan pesan bahwa tidak ada gambar yang dipilih
        label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Tambahkan label ke scene dengan QGraphicsProxyWidget
        proxy = self.preview_scene.addWidget(label)
        image_status_info(proxy)  # Pusatkan widget di scene


def start_image_processing(self, selected_paths):
    """Mulai proses pemrosesan gambar RAW setelah jeda."""
    # Mulai thread pemrosesan gambar RAW
    self.raw_thread = RawImageProcessingThread(selected_paths, batch_size=1, delay_ms=0)
    self.raw_thread.result_signal.connect(self.handle_image_ready)
    self.raw_thread.error_signal.connect(self.handle_image_error)
    self.raw_thread.start()


def image_status_info(self, proxy):
    """
    Center the widget (QGraphicsProxyWidget) in the center of the scene.
    """
    scene_width = self.preview_scene.sceneRect().width()
    scene_height = self.preview_scene.sceneRect().height()

    widget_width = proxy.size().width()
    widget_height = proxy.size().height()

    # Hitung posisi tengah
    center_x = (scene_width - widget_width) / 2
    center_y = (scene_height - widget_height) / 2

    # Set posisi widget
    proxy.setPos(center_x, center_y)


def fit_image_to_panel(self):
    """Scales the image to fit the preview panel, limiting resolution to optimize performance."""
    if self.original_pixmap:
        # Tentukan ukuran tampilan
        view_size = self.preview_view.size()

        # Batasi ukuran maksimum gambar untuk di-render
        max_width = view_size.width()
        max_height = view_size.height()

        # Pastikan gambar tidak melampaui resolusi tampilan
        scaled_pixmap = self.original_pixmap.scaled(
            max_width,
            max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.display_image(scaled_pixmap)


def scale_image(self):
    """Scales the image based on the current zoom factor, with a resolution limit."""
    if self.original_pixmap:
        # Batasi ukuran maksimum gambar berdasarkan zoom
        scaled_width = int(self.original_pixmap.width() * self.zoom_scale)
        scaled_height = int(self.original_pixmap.height() * self.zoom_scale)

        # Terapkan pembatasan
        scaled_pixmap = self.original_pixmap.scaled(
            scaled_width,
            scaled_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.display_image(scaled_pixmap)


def display_image(self, pixmap):
    """Displays the given pixmap in the graphics view."""
    self.preview_scene.clear()
    self.pixmap_item = QGraphicsPixmapItem(pixmap)
    self.preview_scene.addItem(self.pixmap_item)
    self.preview_scene.setSceneRect(self.pixmap_item.boundingRect())


def handler_zoom(self, source, event):
    """
    Handles mouse wheel events for zoom in/out and dragging.

    Args:
        self: Reference to the `EnhanceStackPage` self.
        source: The source widget that triggered the event.
        event: The event to be handled.
    """
    if source == self.preview_view.viewport():
        if event.type() == QEvent.Type.Wheel:  # Zoom
            if event.angleDelta().y() > 0:  # Scroll up: Zoom in
                self.zoom_scale *= 1.1
            else:  # Scroll down: Zoom out
                self.zoom_scale /= 1.1
                self.zoom_scale = max(
                    0.1, self.zoom_scale
                )  # Prevent negative or zero scale
            self.scale_image()
            return True

        elif (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            # Record the start position for dragging
            self.drag_start_pos = event.pos()
            return True

        elif (
            event.type() == QEvent.Type.MouseMove
            and event.buttons() == Qt.MouseButton.LeftButton
        ):
            # Drag the view
            if self.drag_start_pos:
                delta = event.pos() - self.drag_start_pos
                self.preview_view.horizontalScrollBar().setValue(
                    self.preview_view.horizontalScrollBar().value() - delta.x()
                )
                self.preview_view.verticalScrollBar().setValue(
                    self.preview_view.verticalScrollBar().value() - delta.y()
                )
                self.drag_start_pos = event.pos()  # Update drag start position
            return True

        elif (
            event.type() == QEvent.Type.MouseButtonRelease
            and event.button() == Qt.MouseButton.LeftButton
        ):
            # Reset the drag start position
            self.drag_start_pos = None
            return True

    return False
