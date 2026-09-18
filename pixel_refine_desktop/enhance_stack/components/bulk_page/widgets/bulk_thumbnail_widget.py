from resources.animations.fade import fade_in
import weakref
from PySide6.QtWidgets import QLabel, QStackedWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QTimer
from pixel_refine_desktop.ui.views.settings.General.Language import language_config

# Keep retry behavior shared by placeholder/display paths and the batch queue.
THUMBNAIL_RETRY_DELAY_MS = 100
MAX_THUMBNAIL_RETRIES = 3


def thumbnail_placeholder(list_layout, image_path, placeholders, text=None, retry_count=0):
    try:
        if list_layout is None:
            raise RuntimeError("Layout is None")
        parent = list_layout.parent()
    except RuntimeError:
        if retry_count < MAX_THUMBNAIL_RETRIES:
            QTimer.singleShot(
                THUMBNAIL_RETRY_DELAY_MS,
                lambda: thumbnail_placeholder(
                    list_layout, image_path, placeholders, text=text, retry_count=retry_count + 1
                ),
            )
        return None

    display_text = text if text is not None else language_config.LOADING_THUMBNAIL
    placeholder_label = QLabel(display_text)
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
    stacked.placeholder_label = placeholder_label
    stacked.image_path = image_path

    try:
        list_layout.addWidget(stacked)
    except RuntimeError:
        return None

    if placeholders is not None:
        placeholders[image_path] = stacked
    return stacked


def make_safe_callback(current_path, layout_ref, placeholders=None):
    def safe_callback(image, image_path):
        layout = layout_ref() if layout_ref else None
        try:
            if (
                layout is None
                or not hasattr(layout, "count")
                or layout.parent() is None
            ):
                return
            show_thumbnail(layout, image, current_path, animator=None, placeholders=placeholders)
        except RuntimeError:
            pass
        except Exception:
            pass

    return safe_callback


def show_thumbnail(ref_layout, image, image_path, animator=None, retry_count=0, placeholders=None):
    if image is None or image.isNull():
        return False

    try:
        list_layout = ref_layout() if callable(ref_layout) else ref_layout
        if list_layout is None:
            raise RuntimeError("Layout is None")

        _ = list_layout.parent()
        pixmap = QPixmap.fromImage(image)
        if pixmap.height() != 80:
            pixmap = pixmap.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation)

        target_widget = None
        if placeholders is not None:
            candidate = placeholders.get(image_path)
            if candidate is not None:
                try:
                    if isinstance(candidate, QStackedWidget) and getattr(candidate, "image_path", None) == image_path:
                        target_widget = candidate
                except RuntimeError:
                    target_widget = None

        if target_widget is None:
            count = list_layout.count()
            for i in range(count):
                item = list_layout.itemAt(i)
                widget = item.widget()
                if (
                    isinstance(widget, QStackedWidget)
                    and getattr(widget, "image_path", None) == image_path
                ):
                    target_widget = widget
                    break

        if target_widget is not None:
            for j in range(target_widget.count()):
                w = target_widget.widget(j)
                if (
                    isinstance(w, QLabel)
                    and w.pixmap() is not None
                    and not w.pixmap().isNull()
                ):
                    return True

            thumb_label = QLabel()
            thumb_label.setPixmap(pixmap)
            thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            thumb_label.setScaledContents(False)
            thumb_label.setMaximumHeight(80)
            thumb_label.setStyleSheet(
                "background-color: lightgray; border: 1px solid gray;"
            )

            target_widget.addWidget(thumb_label)
            target_widget.setCurrentWidget(thumb_label)

            if animator:
                thumb_label.setGraphicsEffect(None)
                fade_in(animator, thumb_label, target_widget)

            return True

    except RuntimeError:
        if retry_count < MAX_THUMBNAIL_RETRIES:
            QTimer.singleShot(
                THUMBNAIL_RETRY_DELAY_MS,
                lambda: show_thumbnail(
                    ref_layout, image, image_path, animator, retry_count + 1, placeholders=placeholders
                ),
            )
    return False
