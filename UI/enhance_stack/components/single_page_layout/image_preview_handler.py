from PyQt6.QtWidgets import QLabel, QGraphicsPixmapItem
from PyQt6.QtCore import Qt, QTimer
from UI.settings.General.Language import language_config
from UI.enhance_stack.logic.multi_threading import RawImageProcessingThread

def handle_image_ready(layout_instance, pixmap):
    """Tangani hasil gambar yang diproses."""
    layout_instance.original_pixmap = pixmap
    fit_image_to_panel(layout_instance)

def handle_image_error(layout_instance, error_message):
    """Tangani error selama pemrosesan."""
    layout_instance.preview_scene.clear()
    label = QLabel(error_message)
    label.setWordWrap(True)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout_instance.preview_scene.addWidget(label)

def update_preview_panel(layout_instance, selected_paths):
    """Perbarui panel pratinjau berdasarkan gambar yang dipilih."""
    layout_instance.preview_scene.clear()

    if hasattr(layout_instance, "raw_thread") and layout_instance.raw_thread.isRunning():
        layout_instance.raw_thread.stop()
        layout_instance.raw_thread.quit()
        return

    if selected_paths:
        label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_LOADING_IMAGE)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        proxy = layout_instance.preview_scene.addWidget(label)
        image_status_info(layout_instance, proxy)

        layout_instance.preview_timer = QTimer()
        layout_instance.preview_timer.setSingleShot(True)
        layout_instance.preview_timer.timeout.connect(lambda: start_image_processing(layout_instance, selected_paths))
        layout_instance.preview_timer.start(1000)
    else:
        layout_instance.original_pixmap = None
        label = QLabel(language_config.UPDATE_PREVIEW_PANEL_MESSAGE_NO_IMAGE_SELECTED)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        proxy = layout_instance.preview_scene.addWidget(label)
        image_status_info(layout_instance, proxy)

def start_image_processing(layout_instance, selected_paths):
    """Mulai proses pemrosesan gambar RAW."""
    layout_instance.raw_thread = RawImageProcessingThread(selected_paths, batch_size=1, delay_ms=0)
    layout_instance.raw_thread.result_signal.connect(lambda pixmap: handle_image_ready(layout_instance, pixmap))
    layout_instance.raw_thread.error_signal.connect(lambda error: handle_image_error(layout_instance, error))
    layout_instance.raw_thread.start()

def image_status_info(layout_instance, proxy):
    """Pusatkan widget di tengah scene."""
    scene_width = layout_instance.preview_scene.sceneRect().width()
    scene_height = layout_instance.preview_scene.sceneRect().height()
    widget_width = proxy.size().width()
    widget_height = proxy.size().height()

    center_x = (scene_width - widget_width) / 2
    center_y = (scene_height - widget_height) / 2
    proxy.setPos(center_x, center_y)

def fit_image_to_panel(layout_instance):
    """Sesuaikan gambar agar pas di panel pratinjau."""
    if layout_instance.original_pixmap:
        view_size = layout_instance.preview_view.size()
        max_width = view_size.width()
        max_height = view_size.height()

        scaled_pixmap = layout_instance.original_pixmap.scaled(
            max_width, max_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        display_image(layout_instance, scaled_pixmap)

def display_image(layout_instance, pixmap):
    """Tampilkan gambar di panel pratinjau."""
    layout_instance.preview_scene.clear()
    layout_instance.pixmap_item = QGraphicsPixmapItem(pixmap)
    layout_instance.preview_scene.addItem(layout_instance.pixmap_item)
    layout_instance.preview_scene.setSceneRect(layout_instance.pixmap_item.boundingRect())
