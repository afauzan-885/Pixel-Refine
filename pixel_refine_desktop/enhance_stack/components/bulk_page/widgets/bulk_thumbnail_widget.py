import weakref
from PySide6.QtWidgets import QLabel, QStackedWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.ui.resources.animations.fade import fade_in

def thumbnail_placeholder(list_layout, image_path, placeholders, retry_count=0):
    try:
        if list_layout is None:
            raise RuntimeError("Layout is None")
        parent = list_layout.parent()
    except RuntimeError:
        if retry_count < 3:
            QTimer.singleShot(100,
                              lambda: thumbnail_placeholder(list_layout, image_path, placeholders, retry_count + 1))
        return None

    placeholder_label = QLabel(language_config.LOADING_THUMBNAIL)
    placeholder_label.setFixedSize(80, 80)
    placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    placeholder_label.setStyleSheet(
        "background-color: lightgray; "
        "border: 1px solid gray; "
        "font-size: 12px; "
        "color: gray;"
    )

    stacked = QStackedWidget()
    stacked.setFixedSize(80, 80)
    stacked.addWidget(placeholder_label)
    stacked.image_path = image_path

    try:
        list_layout.addWidget(stacked)
    except RuntimeError:
        return None

    placeholders[image_path] = list_layout
    return stacked


def make_safe_callback(current_path, layout_ref):
    def safe_callback(image, image_path):
        layout = layout_ref() if layout_ref else None
        try:
            if layout is None or not hasattr(layout, "count") or layout.parent() is None:
                return
            show_thumbnail(layout, image, current_path, animator=None)
        except RuntimeError:
            pass
        except Exception:
            pass
    return safe_callback


def show_thumbnail(ref_layout, image, image_path, animator=None, retry_count=0):
    try:
        list_layout = ref_layout() if callable(ref_layout) else ref_layout
        if list_layout is None:
            raise RuntimeError("Layout is None")

        _ = list_layout.parent()
        count = list_layout.count()
        pixmap = QPixmap.fromImage(image)

        for i in range(count):
            item = list_layout.itemAt(i)
            widget = item.widget()

            if isinstance(widget, QStackedWidget) and getattr(widget, "image_path", None) == image_path:
                for j in range(widget.count()):
                    w = widget.widget(j)
                    if isinstance(w, QLabel) and w.pixmap() is not None and not w.pixmap().isNull():
                        return  
                    
                thumb_label = QLabel()
                thumb_label.setPixmap(pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))
                thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                thumb_label.setScaledContents(False)
                thumb_label.setMaximumHeight(80)
                thumb_label.setStyleSheet("background-color: lightgray; border: 1px solid gray;")

                widget.addWidget(thumb_label)
                widget.setCurrentWidget(thumb_label)

                if animator:
                    thumb_label.setGraphicsEffect(None)
                    fade_in(animator, thumb_label, widget)

                return

    except RuntimeError:
        if retry_count < 3:
            QTimer.singleShot(100, lambda: show_thumbnail(ref_layout, image, image_path, animator, retry_count + 1))
