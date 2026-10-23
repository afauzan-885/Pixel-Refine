"""Virtualized, widget-free batch rows for Bulk Mode."""

from functools import lru_cache

from PySide6.QtCore import QAbstractListModel, QEvent, QModelIndex, QRect, QSize, Qt, Signal, QTimer
from PySide6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter, QPen
from PySide6.QtWidgets import QListView, QStyledItemDelegate, QToolTip, QWidget
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_names
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from UILibrary import ScrollContainer
from UILibrary.theme import create_button_style, get_theme

_ROW_ICON_PATHS = (
    "resources/assets/icons/add-image_black.png",
    "resources/assets/icons/play-preview_black.png",
    "resources/assets/icons/delete-image_black.png",
)


@lru_cache(maxsize=None)
def _available_combo_names(category):
    """Cache lightweight catalog labels without loading algorithm implementations."""
    return tuple(get_names(category, context="batch", include_disabled=True))


class _ThumbnailStripCanvas(QWidget):
    """Paint all previews into one scrollable canvas instead of one QLabel each."""

    def __init__(self, record, parent=None):
        super().__init__(parent)
        self.record = record
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.refresh_content()

    @staticmethod
    def _width_for(path, record):
        image = record.get("thumbnails", {}).get(path)
        if image is not None and not image.isNull() and image.height() > 0:
            return max(1, round(image.width() * 80 / image.height()))
        return 80

    def refresh_content(self):
        widths = [self._width_for(path, self.record) for path in self.record.get("paths", ())]
        content_width = 12 + sum(widths) + max(0, len(widths) - 1) * 10
        self.setFixedSize(max(1, content_width), 80)
        if self.parentWidget() is not None:
            self.parentWidget().setFixedSize(self.size())
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        x = 12
        loading_text = getattr(language_config, "LOADING_THUMBNAIL", "Loading...")
        for path in self.record.get("paths", ()):
            image = self.record.get("thumbnails", {}).get(path)
            if image is not None and not image.isNull() and image.height() > 0:
                width = max(1, round(image.width() * 80 / image.height()))
                painter.drawImage(QRect(x, 0, width, 80), image)
                x += width + 10
                continue

            placeholder = QRect(x, 0, 80, 80)
            painter.setPen(QPen(QColor("#D5DEE8"), 1))
            painter.setBrush(QColor("#E9EEF2"))
            painter.drawRoundedRect(placeholder, 3, 3)
            if path in self.record.get("thumbnail_loading", ()):
                painter.setPen(QColor("#718096"))
                painter.drawText(placeholder.adjusted(3, 3, -3, -3),
                                 Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                                 loading_text)
            x += 90


class _ThumbnailScrollContainer(ScrollContainer):
    """GenericUI scroll area with natural wheel-to-horizontal behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BulkThumbnailScrollContainer")
        self.setWidgetResizable(False)
        self.setFrameShape(ScrollContainer.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet(
            "QScrollArea#BulkThumbnailScrollContainer { background: transparent; border: 0; }"
        )

    def wheelEvent(self, event):
        bar = self.horizontalScrollBar()
        if bar.maximum() > bar.minimum():
            delta = event.angleDelta().x() or event.angleDelta().y()
            bar.setValue(bar.value() - delta)
            event.accept()
            return
        super().wheelEvent(event)


class BulkBatchListModel(QAbstractListModel):
    BatchIdRole = Qt.ItemDataRole.UserRole + 1
    RecordRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.records = []

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.records)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.records):
            return None
        record = self.records[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return f"Batch {index.row() + 1}  -  ({len(record['paths'])} images)"
        if role == self.BatchIdRole:
            return record["id"]
        if role == self.RecordRole:
            return record
        return None

    def replace_records(self, records):
        self.beginResetModel()
        self.records = records
        self.endResetModel()

    def record_for_id(self, batch_id):
        return next((row for row in self.records if row["id"] == batch_id), None)


class BulkBatchDelegate(QStyledItemDelegate):
    action = Signal(str, object, object)

    HEIGHT = 115
    ROW_GAP = 8
    SPACING = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self._icons = tuple(QIcon(path) for path in _ROW_ICON_PATHS)
        self.refresh_button_styles()

    def refresh_button_styles(self):
        """Cache GenericUI button colors used by the original row controls."""
        theme = get_theme()
        styles = tuple(
            create_button_style(variant, theme)
            for variant in ("success", "primary", "danger")
        )
        self._button_styles = tuple(style.base for style in styles)
        self._button_hover_backgrounds = tuple(
            style.states["hover"]["background"] for style in styles
        )
        self._hovered_control = None

    @staticmethod
    def control_at(point, item_rect):
        """Return the row action under the pointer, if it is on a button."""
        x = point.x() - item_rect.left()
        y = point.y() - item_rect.top()
        if x < 2 or x >= 23:
            return None
        for i, action in enumerate(("add", "preview", "delete")):
            button_rect = QRect(2, 10 + i * 35, 21, 21)
            if button_rect.contains(x, y):
                return action
        return None

    def set_hovered_control(self, row, action):
        hovered = (row, action) if action is not None else None
        if hovered == self._hovered_control:
            return False
        previous = self._hovered_control
        self._hovered_control = hovered
        return previous

    @staticmethod
    def tooltip_for_action(action):
        return {
            "add": language_config.ADD_IMAGE_BUTTON,
            "preview": language_config.PREVIEW_IMAGE_BUTTON,
            "delete": language_config.DELETE_IMAGE_BUTTON,
        }.get(action, "")

    @staticmethod
    def option_layout(record, content, font):
        labels = (language_config.PARAMETER_BATCH_ALIGNMENT,
                  language_config.PARAMETER_BATCH_DENOISING,
                  language_config.PARAMETER_BATCH_SUPER_RESOLUTION)
        metrics = QFontMetrics(font)
        label_width = max(metrics.horizontalAdvance(label) for label in labels)
        natural_width = max(112, label_width + 42)
        max_width = max(1, content.width() // 2)
        panel_width = min(natural_width, max_width)
        area = QRect(content.right() - panel_width + 1, content.top() + 25,
                     panel_width, content.height() - 27)
        row_height = max(21, metrics.height() + 4)
        content_width = label_width + 38
        content_height = 10 + len(labels) * row_height
        horizontal = vertical = False
        for _ in range(3):
            client = area.adjusted(1, 1, -1 - (7 if vertical else 0),
                                   -1 - (7 if horizontal else 0))
            next_horizontal = content_width > client.width()
            next_vertical = content_height > client.height()
            if (next_horizontal, next_vertical) == (horizontal, vertical):
                break
            horizontal, vertical = next_horizontal, next_vertical
        client = area.adjusted(1, 1, -1 - (7 if vertical else 0),
                               -1 - (7 if horizontal else 0))
        max_x = max(0, content_width - client.width())
        max_y = max(0, content_height - client.height())
        record["option_scroll_x"] = min(max(0, record.get("option_scroll_x", 0)), max_x)
        record["option_scroll_y"] = min(max(0, record.get("option_scroll_y", 0)), max_y)
        h_track = QRect(client.left(), area.bottom() - 6, client.width(), 4) if horizontal else QRect()
        v_track = QRect(area.right() - 6, client.top(), 4, client.height()) if vertical else QRect()
        h_handle = QRect()
        v_handle = QRect()
        if horizontal:
            handle_width = min(h_track.width(), max(10, int(h_track.width() * client.width() / content_width)))
            handle_travel = max(0, h_track.width() - handle_width)
            handle_x = h_track.left() + (int(handle_travel * record["option_scroll_x"] / max_x) if max_x else 0)
            h_handle = QRect(handle_x, h_track.top(), handle_width, h_track.height())
        if vertical:
            handle_height = min(v_track.height(), max(10, int(v_track.height() * client.height() / content_height)))
            handle_travel = max(0, v_track.height() - handle_height)
            handle_y = v_track.top() + (int(handle_travel * record["option_scroll_y"] / max_y) if max_y else 0)
            v_handle = QRect(v_track.left(), handle_y, v_track.width(), handle_height)
        return {
            "area": area, "client": client, "labels": labels, "metrics": metrics,
            "row_height": row_height, "content_width": content_width,
            "content_height": content_height, "max_x": max_x, "max_y": max_y,
            "horizontal": horizontal, "vertical": vertical,
            "h_track": h_track, "h_handle": h_handle,
            "v_track": v_track, "v_handle": v_handle,
        }

    @staticmethod
    def combo_layout(record, content, option_layout, font):
        """Return fixed-width combo rectangles sized for the longest available option."""
        combo_specs = (("checkbox_align_images", "alignment_algo", "alignment"),
                       ("checkbox_super_resolution", "super_resolution_algo", "super_resolution"),
                       ("checkbox_denoising", "denoising_algo", "denoising"))
        empty_labels = {"alignment": "No Alignment", "denoising": "No Denoising",
                        "super_resolution": "No Super Resolution"}
        state = record["state"]
        enabled = [spec for spec in combo_specs if state.get(spec[0], False)]
        area = QRect(content.left() + 8, content.top() + 29,
                     max(1, option_layout["area"].left() - content.left() - 16),
                     content.height() - 34)
        height = min(22, max(18, (area.height() - 4) // max(1, len(enabled))))
        metrics = QFontMetrics(font)
        values = []
        for _, algo_key, category in enabled:
            value = state.get(algo_key)
            if not value or value == "None":
                value = empty_labels[category]
            values.append((category, str(value)))
        available_names = tuple(
            name
            for category in ("alignment", "super_resolution", "denoising")
            for name in _available_combo_names(category)
        )
        widest_label = max(available_names, key=metrics.horizontalAdvance, default="")
        # One stable width for every combo and batch. It accounts for every
        # selectable label, so changing the selection cannot resize the column.
        width = min(area.width(), max(1, metrics.horizontalAdvance(widest_label) + 35))
        rectangles = []
        for combo_index, (category, value) in enumerate(values):
            rect = QRect(area.left(), area.top() + combo_index * (height + 4), width, height)
            rectangles.append((category, value, rect))
        return rectangles

    @staticmethod
    def combo_panel_rect(record, content, option_layout, font):
        """Background panel around the dropdown column, sized to its fixed width."""
        enabled = any(record["state"].get(key, False) for key in (
            "checkbox_align_images", "checkbox_super_resolution", "checkbox_denoising",
        ))
        if not enabled:
            return QRect()
        combo_rects = BulkBatchDelegate.combo_layout(record, content, option_layout, font)
        if not combo_rects:
            return QRect()
        combo = combo_rects[0][2]
        return QRect(combo.left() - 4, content.top() + 26, combo.width() + 8,
                     content.height() - 29)

    @staticmethod
    def _paint_scrollbar(painter, track, handle):
        if track.isNull():
            return
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#DDE4EA"))
        painter.drawRoundedRect(track, 2, 2)
        painter.setBrush(QColor("#8997A3"))
        painter.drawRoundedRect(handle, 2, 2)

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), self.HEIGHT + self.ROW_GAP)

    def paint(self, painter, option, index):
        model = index.model()
        if not isinstance(model, BulkBatchListModel) or not 0 <= index.row() < len(model.records):
            return
        # Read the backing record directly: QVariant conversion of a Python
        # dict returned by data() can produce a copy, hiding newly cached QImages.
        record = model.records[index.row()]
        r = QRect(option.rect.left(), option.rect.top(), option.rect.width(), self.HEIGHT)
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Match CombinedPanel's original geometry: a 430px-minimum parameter
        # column (stretch 1) beside the thumbnail pane (stretch 2).
        left_w = min(max(430, r.width() // 3), max(1, int(r.width() * 0.55)))
        rail_w, rail_gap, panel_gap = 26, 5, 8
        content = QRect(r.left() + rail_w + rail_gap, r.top(), left_w - rail_w - rail_gap, r.height())
        right = QRect(r.left() + left_w + panel_gap, r.top(), r.right() - (r.left() + left_w + panel_gap) + 1, r.height())

        painter.setPen(QPen(QColor("#DDE6EF"), 1))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(content, 6, 6)
        painter.drawRoundedRect(right, 6, 6)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#28C76F"))
        painter.drawRoundedRect(QRect(content.left(), content.top(), content.width(), 24), 4, 4)
        painter.setPen(QColor("#FFFFFF"))
        header_font = QFont(painter.font())
        header_font.setPointSize(8)
        header_font.setBold(True)
        painter.setFont(header_font)
        painter.drawText(QRect(content.left() + 5, content.top(), content.width() - 10, 24), Qt.AlignmentFlag.AlignCenter,
                         language_config.BATCH_LABEL_FORMAT.format(index.row() + 1, len(record["paths"])))
        painter.setFont(option.font)

        # Lightweight add / preview / delete controls; no per-row QWidget is created.
        for i, style in enumerate(self._button_styles):
            y = r.top() + 10 + i * 35
            box = QRect(r.left() + 2, y, 21, 21)
            painter.setPen(QPen(QColor(style["border_color"]), style["border_width"]))
            hovered = self._hovered_control == (index.row(), ("add", "preview", "delete")[i])
            background = self._button_hover_backgrounds[i] if hovered else style["background"]
            painter.setBrush(QColor(background))
            radius = style["radius"]
            painter.drawRoundedRect(box, radius, radius)
            icon_rect = QRect(box.center().x() - 7, box.center().y() - 7, 14, 14)
            self._icons[i].paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)

        state = record["state"]
        option_layout = self.option_layout(record, content, option.font)
        option_area = option_layout["area"]
        painter.setPen(QPen(QColor("#E2E8F0"), 1))
        painter.setBrush(QColor("#F4F7F9"))
        painter.drawRoundedRect(option_area, 2, 2)
        option_client = option_layout["client"]
        painter.save()
        painter.setClipRect(option_client)
        option_top = option_client.top() + 5 - record["option_scroll_y"]
        option_left = option_client.left() - record["option_scroll_x"]
        checkbox_rows = ("checkbox_align_images", "checkbox_denoising", "checkbox_super_resolution")
        for i, (key, label) in enumerate(zip(checkbox_rows, option_layout["labels"])):
            y = option_top + i * option_layout["row_height"]
            checked = bool(state.get(key, False))
            painter.setPen(QPen(QColor("#D4DEE7"), 1))
            painter.setBrush(QColor("#28C76F") if checked else QColor("#FFFFFF"))
            painter.drawEllipse(QRect(option_left + 7, y + 3, 13, 13))
            painter.setPen(QColor("#18324F"))
            painter.drawText(option_left + 29, y + option_layout["metrics"].ascent() + 2, label)
        painter.restore()
        self._paint_scrollbar(painter, option_layout["h_track"], option_layout["h_handle"])
        self._paint_scrollbar(painter, option_layout["v_track"], option_layout["v_handle"])

        # Same vertical combo stack as CombinedPanel: alignment, super resolution,
        # denoising. Hidden (unchecked) combos collapse out of the stack.
        combo_panel = self.combo_panel_rect(record, content, option_layout, option.font)
        if not combo_panel.isNull():
            painter.setPen(QPen(QColor("#E2E8F0"), 1))
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawRoundedRect(combo_panel, 4, 4)
        for category, value, combo_rect in self.combo_layout(record, content, option_layout, option.font):
            painter.setPen(QPen(QColor("#D5DEE8"), 1))
            painter.setBrush(QColor("#FFFFFF"))
            painter.drawRoundedRect(combo_rect, 4, 4)
            painter.setPen(QColor("#17375E"))
            painter.drawText(combo_rect.adjusted(6, 0, -20, 0), Qt.AlignmentFlag.AlignVCenter, str(value))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor("#D5DEE8"))
            painter.drawRoundedRect(QRect(combo_rect.right() - 17, combo_rect.top() + 3, 13, combo_rect.height() - 6), 2, 2)
            painter.setPen(QColor("#FFFFFF"))
            painter.drawText(QRect(combo_rect.right() - 17, combo_rect.top() + 1, 13, combo_rect.height() - 2),
                             Qt.AlignmentFlag.AlignCenter, "⌄")

        if not record.get("_thumbnail_scroll_widget", False):
            thumbs = record.get("thumbnails", {})
            x = right.left() + 12
            for path in record["paths"]:
                image = thumbs.get(path)
                if image is not None and not image.isNull() and image.height() > 0:
                    width = max(1, round(image.width() * 80 / image.height()))
                    drawn = QRect(x, right.center().y() - 40, width, 80)
                    painter.drawImage(drawn, image)
                    x += width + 10
                else:
                    placeholder = QRect(x, right.center().y() - 40, 80, 80)
                    painter.setPen(QPen(QColor("#D5DEE8"), 1))
                    painter.setBrush(QColor("#E9EEF2"))
                    painter.drawRoundedRect(placeholder, 3, 3)
                    if path in record.get("thumbnail_loading", ()):
                        painter.setPen(QColor("#718096"))
                        painter.drawText(placeholder.adjusted(3, 3, -3, -3),
                                         Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                                         getattr(language_config, "LOADING_THUMBNAIL", "Loading..."))
                    x += 90
        painter.restore()

    def editorEvent(self, event, model, option, index):
        if event.type() != QEvent.Type.MouseButtonRelease or event.button() != Qt.MouseButton.LeftButton:
            return False
        record = index.data(BulkBatchListModel.RecordRole)
        if not record:
            return False
        x, y = event.position().toPoint().x(), event.position().toPoint().y()
        rel_y = y - option.rect.top()
        action = self.control_at(event.position().toPoint(), option.rect)
        if action:
            self.action.emit(action, record["id"], None)
            return True
        rel_x = x - option.rect.left()
        left_w = min(max(430, option.rect.width() // 3), max(1, int(option.rect.width() * 0.55)))
        content_x = 31
        content = QRect(option.rect.left() + content_x, option.rect.top(), left_w - content_x, self.HEIGHT)
        option_layout = self.option_layout(record, content, option.font)
        point = event.position().toPoint()
        client = option_layout["client"]
        if client.contains(point):
            option_left = client.left() - record["option_scroll_x"]
            option_top = client.top() + 5 - record["option_scroll_y"]
            keys = ("checkbox_align_images", "checkbox_denoising", "checkbox_super_resolution")
            for row_index, label in enumerate(option_layout["labels"]):
                row_top = option_top + row_index * option_layout["row_height"]
                indicator_rect = QRect(option_left + 7, row_top + 3, 13, 13)
                label_rect = QRect(option_left + 29, row_top + 2,
                                   option_layout["metrics"].horizontalAdvance(label),
                                   option_layout["metrics"].height())
                if indicator_rect.contains(point) or label_rect.contains(point):
                    self.action.emit("toggle", record["id"], row_index)
                    return True

        for category, _, combo_rect in self.combo_layout(record, content, option_layout, option.font):
            if combo_rect.contains(point):
                self.action.emit("choose", record["id"], category)
                return True
        return False


class BulkBatchListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BulkBatchListView")
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QListView.ScrollMode.ScrollPerPixel)
        self.setSelectionMode(QListView.SelectionMode.NoSelection)
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        self.setSpacing(BulkBatchDelegate.SPACING)
        self.setUniformItemSizes(True)
        self.setFrameShape(QListView.Shape.NoFrame)
        self.setStyleSheet("QListView { background: transparent; border: 0; }")
        self._thumbnail_scrollers = {}
        self._thumbnail_sync_timer = QTimer(self)
        self._thumbnail_sync_timer.setSingleShot(True)
        self._thumbnail_sync_timer.timeout.connect(self.sync_thumbnail_scrollers)
        self.verticalScrollBar().valueChanged.connect(self.schedule_thumbnail_sync)

    def setModel(self, model):
        old_model = self.model()
        if old_model is not None:
            try:
                old_model.modelReset.disconnect(self.schedule_thumbnail_sync)
            except (RuntimeError, TypeError):
                pass
        super().setModel(model)
        if model is not None:
            model.modelReset.connect(self.schedule_thumbnail_sync)
        self.schedule_thumbnail_sync()

    def schedule_thumbnail_sync(self, *_args):
        if hasattr(self, "_thumbnail_sync_timer"):
            self._thumbnail_sync_timer.start(0)

    @staticmethod
    def _thumbnail_scroll_rect(index_rect, row_width):
        left_w = min(max(430, row_width // 3), max(1, int(row_width * 0.55)))
        right = QRect(index_rect.left() + left_w + 8, index_rect.top(),
                      index_rect.right() - (index_rect.left() + left_w + 8) + 1,
                      BulkBatchDelegate.HEIGHT)
        return right.adjusted(8, 8, -8, -12)

    def _make_thumbnail_scroller(self, record, geometry):
        scroller = _ThumbnailScrollContainer(self.viewport())
        scroller.setGeometry(geometry)
        scroller.container_layout.setContentsMargins(0, 0, 0, 0)
        scroller.container_layout.setSpacing(0)
        scroller.container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        canvas = _ThumbnailStripCanvas(record)
        scroller.set_widget(canvas)
        scroller.container.setFixedSize(canvas.size())
        scroller.horizontalScrollBar().valueChanged.connect(
            lambda value, row=record: row.__setitem__("thumbnail_scroll_x", value)
        )
        scroller.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        return scroller, canvas

    def sync_thumbnail_scrollers(self):
        if self.model() is None:
            return
        visible = {}
        viewport_rect = self.viewport().rect()
        row_pitch = BulkBatchDelegate.HEIGHT + BulkBatchDelegate.ROW_GAP
        scroll_value = self.verticalScrollBar().value()
        first = max(0, scroll_value // row_pitch)
        last = min(self.model().rowCount(), (scroll_value + viewport_rect.height()) // row_pitch + 2)
        for row in range(first, last):
            index = self.model().index(row, 0)
            index_rect = self.visualRect(index)
            if index_rect.isNull() or not index_rect.intersects(viewport_rect):
                continue
            record = self.model().records[row]
            geometry = self._thumbnail_scroll_rect(index_rect, index_rect.width())
            if geometry.width() <= 0 or geometry.height() <= 0:
                continue
            visible[id(record)] = (record, geometry, index)

        for record_key in tuple(self._thumbnail_scrollers):
            if record_key in visible:
                continue
            scroller, canvas, record = self._thumbnail_scrollers.pop(record_key)
            record["thumbnail_scroll_x"] = scroller.horizontalScrollBar().value()
            record["_thumbnail_scroll_widget"] = False
            scroller.hide()
            scroller.deleteLater()

        for record_key, (record, geometry, index) in visible.items():
            existing = self._thumbnail_scrollers.get(record_key)
            if existing is None:
                scroller, canvas = self._make_thumbnail_scroller(record, geometry)
                self._thumbnail_scrollers[record_key] = (scroller, canvas, record)
                scroller.horizontalScrollBar().setValue(record.get("thumbnail_scroll_x", 0))
            else:
                scroller, canvas, _ = existing
                canvas.record = record
                canvas.refresh_content()
                scroller.container.setFixedSize(canvas.size())
                scroller.setGeometry(geometry)
            record["_thumbnail_scroll_widget"] = True
            scroller.show()
            scroller.raise_()
            self.viewport().update(self.visualRect(index))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.schedule_thumbnail_sync()

    def refresh_thumbnail_record(self, record):
        existing = self._thumbnail_scrollers.get(id(record))
        if existing is not None:
            existing[1].refresh_content()
            existing[0].updateGeometry()
            self.schedule_thumbnail_sync()

    def _option_geometry_for_index(self, index):
        if not index.isValid() or not 0 <= index.row() < len(self.model().records):
            return None
        record = self.model().records[index.row()]
        item_rect = self.visualRect(index)
        row = QRect(item_rect.left(), item_rect.top(), item_rect.width(), BulkBatchDelegate.HEIGHT)
        left_w = min(max(430, row.width() // 3), max(1, int(row.width() * 0.55)))
        content = QRect(row.left() + 31, row.top(), left_w - 31, row.height())
        layout = self.itemDelegate().option_layout(record, content, self.font())
        return record, row, layout

    def _apply_option_scroll(self, row, axis, value):
        if not 0 <= row < self.model().rowCount():
            return
        index = self.model().index(row, 0)
        geometry = self._option_geometry_for_index(index)
        if geometry is None:
            return
        record, _, layout = geometry
        key, maximum = ("option_scroll_x", layout["max_x"]) if axis == "x" else ("option_scroll_y", layout["max_y"])
        record[key] = max(0, min(maximum, int(value)))
        self.viewport().update(self.visualRect(index))

    def _scrollbar_at(self, point, index):
        geometry = self._option_geometry_for_index(index)
        if geometry is None:
            return None
        record, _, layout = geometry
        for axis, track_key, handle_key in (("x", "h_track", "h_handle"), ("y", "v_track", "v_handle")):
            track, handle = layout[track_key], layout[handle_key]
            if not track.isNull() and track.contains(point):
                return record, layout, axis, track, handle
        return None

    def mouseMoveEvent(self, event):
        if getattr(self, "_option_scroll_drag", None) is not None:
            row, axis, grab_offset = self._option_scroll_drag
            index = self.model().index(row, 0)
            geometry = self._option_geometry_for_index(index)
            if geometry:
                record, _, layout = geometry
                track = layout["h_track"] if axis == "x" else layout["v_track"]
                handle = layout["h_handle"] if axis == "x" else layout["v_handle"]
                maximum = layout["max_x"] if axis == "x" else layout["max_y"]
                pointer = event.position().toPoint().x() if axis == "x" else event.position().toPoint().y()
                track_start = track.left() if axis == "x" else track.top()
                handle_length = handle.width() if axis == "x" else handle.height()
                travel = max(1, (track.width() if axis == "x" else track.height()) - handle_length)
                value = round(max(0, min(travel, pointer - track_start - grab_offset)) * maximum / travel)
                self._apply_option_scroll(row, axis, value)
            return
        index = self.indexAt(event.position().toPoint())
        action = None
        if index.isValid():
            action = self.itemDelegate().control_at(
                event.position().toPoint(), self.visualRect(index)
            )
        previous = self.itemDelegate()._hovered_control
        hovered = (index.row(), action) if index.isValid() and action else None
        self.itemDelegate().set_hovered_control(index.row() if index.isValid() else -1, action)
        if previous is not None:
            old_index = self.model().index(previous[0], 0)
            self.viewport().update(self.visualRect(old_index))
        if action is not None and index.isValid():
            self.viewport().update(self.visualRect(index))
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            if previous != hovered:
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    self.itemDelegate().tooltip_for_action(action),
                    self,
                )
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            QToolTip.hideText()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            point = event.position().toPoint()
            index = self.indexAt(point)
            if index.isValid():
                scrollbar = self._scrollbar_at(point, index)
                if scrollbar:
                    _, layout, axis, track, handle = scrollbar
                    pointer = point.x() if axis == "x" else point.y()
                    handle_start = handle.left() if axis == "x" else handle.top()
                    handle_length = handle.width() if axis == "x" else handle.height()
                    if handle.contains(point):
                        self._option_scroll_drag = (index.row(), axis, pointer - handle_start)
                    else:
                        track_start = track.left() if axis == "x" else track.top()
                        travel = max(1, (track.width() if axis == "x" else track.height()) - handle_length)
                        maximum = layout["max_x"] if axis == "x" else layout["max_y"]
                        value = round(max(0, min(travel, pointer - track_start - handle_length // 2)) * maximum / travel)
                        self._apply_option_scroll(index.row(), axis, value)
                        self._option_scroll_drag = (index.row(), axis, handle_length // 2)
                    event.accept()
                    return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if getattr(self, "_option_scroll_drag", None) is not None:
            self._option_scroll_drag = None
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        point = event.position().toPoint()
        index = self.indexAt(point)
        if index.isValid():
            geometry = self._option_geometry_for_index(index)
            if geometry:
                record, _, layout = geometry
                if layout["area"].contains(point):
                    axis = "x" if event.modifiers() & Qt.KeyboardModifier.ShiftModifier else "y"
                    maximum = layout["max_x"] if axis == "x" else layout["max_y"]
                    if maximum:
                        current = record.get("option_scroll_x" if axis == "x" else "option_scroll_y", 0)
                        direction = -1 if event.angleDelta().y() > 0 else 1
                        self._apply_option_scroll(index.row(), axis, current + direction * 36)
                        event.accept()
                        return
        super().wheelEvent(event)

    def leaveEvent(self, event):
        previous = self.itemDelegate()._hovered_control
        self.itemDelegate().set_hovered_control(-1, None)
        if previous is not None:
            old_index = self.model().index(previous[0], 0)
            self.viewport().update(self.visualRect(old_index))
        self.setCursor(Qt.CursorShape.ArrowCursor)
        QToolTip.hideText()
        super().leaveEvent(event)

    def update_content_height(self, row_count, viewport_height):
        # QListView reserves one spacing before and after every item.
        content_height = row_count * (BulkBatchDelegate.HEIGHT + BulkBatchDelegate.ROW_GAP)
        self.setFixedHeight(max(viewport_height, content_height))
