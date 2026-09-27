"""
Bootstrap-like Card Components for PySide6
Provides reusable card containers
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QComboBox,
    QMenu,
    QStackedWidget,
    QSizePolicy,
    QStyle,
    QStylePainter,
    QStyleOptionComboBox,
)
from PySide6.QtCore import Qt, Signal, QTimer, QEvent, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QFont, QFontMetrics, QTextLayout, QTextOption, QPalette
from .mixins import RealtimeMixin
from .buttons import Button
from .theme import create_checkbox_style, create_select_style
from resources.animations.animation_manager import (
    HeightAnimator,
    StackedWidgetAnimator,
    AnimationType,
)


class Card(QFrame):
    """
    Bootstrap-like card component with header, body, and footer

    Usage:
        card = Card(title="User Profile")
        card.set_body_content("Content goes here")
        card.add_footer_widget(save_button)
    """

    def __init__(self, title="", bg_color=None, border_color=None, parent=None):
        super().__init__(parent)
        self._qml_children = []
        self._title = title

        self.setObjectName("displayContainer")  # Use existing style

        # Apply custom colors if provided
        if bg_color or border_color:
            self._apply_custom_colors(bg_color, border_color)

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Header
        self.header = QWidget()
        self.header_layout = QHBoxLayout(self.header)
        self.header_layout.setContentsMargins(0, 0, 0, 0)

        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("sectionTitle")
            self.header_layout.addWidget(self.title_label)
            self.header_layout.addStretch()
            self.main_layout.addWidget(self.header)
        else:
            self.title_label = QLabel("")

        # Body
        self.body = QWidget()
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(5)

        self.main_layout.addWidget(self.body, 1)

        # Footer
        self.footer = QWidget()
        self.footer_layout = QHBoxLayout(self.footer)
        self.footer_layout.setContentsMargins(0, 0, 0, 0)
        self.footer_layout.setSpacing(5)
        self.footer.setVisible(False)

        self.main_layout.addWidget(self.footer)

    def set_title(self, title):
        """Set card title"""
        self._title = title
        self.title_label.setText(title)
        self.header.setVisible(bool(title))

    def add_header_widget(self, widget):
        """Add widget to header (e.g., buttons)"""
        self.header_layout.addWidget(widget)

    def set_body_content(self, content):
        """Set body content (text or widget)"""
        # Clear existing body
        self._qml_children.clear()
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if isinstance(content, str):
            label = QLabel(content)
            label.setWordWrap(True)
            self.body_layout.addWidget(label)
        elif isinstance(content, QWidget):
            self._qml_children.append(content)
            self.body_layout.addWidget(content)

    def add_body_widget(self, widget, stretch=0):
        """Add widget to body"""
        self._qml_children.append(widget)
        self.body_layout.addWidget(widget, stretch)

    def add_footer_widget(self, widget):
        """Add widget to footer"""
        self.footer.setVisible(True)
        self.footer_layout.addWidget(widget)

    def clear_body(self):
        """Clear body content"""
        self._qml_children.clear()
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _apply_custom_colors(self, bg_color=None, border_color=None):
        """Apply custom colors via inline stylesheet"""
        if not bg_color:
            bg_color = "#FFFFFF"
        if not border_color:
            border_color = "#E8EDF2"

        style = f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """
        self.setStyleSheet(style)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: parent.width - 32\n"
        qml += f"{tab}    height: childrenRect.height + 32\n"
        qml += f"{tab}    color: genericTheme.bgPrimary\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: genericTheme.borderColor\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        x: 16\n"
        qml += f"{tab}        y: 16\n"
        qml += f"{tab}        width: parent.width - 32\n"
        qml += f"{tab}        spacing: 8\n"
        if self._title:
            qml += f"{tab}        Text {{ text: '{self._title}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }}\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class CardHeader(QWidget):
    """
    Card header component

    Usage:
        header = CardHeader(title="Settings")
        header.add_action(close_button)
    """

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self._title = title
        self._qml_children = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")

        layout.addWidget(self.title_label)
        layout.addStretch()

    def set_title(self, title):
        """Set header title"""
        self._title = title
        self.title_label.setText(title)

    def add_action(self, widget):
        """Add action widget (button, etc.)"""
        self._qml_children.append(widget)
        self.layout().addWidget(widget)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    spacing: 8\n"
        qml += f"{tab}    Text {{ text: '{self._title}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}    Item {{ Layout.fillWidth: true }}\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


class CardBody(QWidget):
    """
    Card body component

    Usage:
        body = CardBody()
        body.add_widget(content_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

    def add_widget(self, widget, stretch=0):
        """Add widget to body"""
        self._qml_children.append(widget)
        self.layout.addWidget(widget, stretch)

    def set_content(self, content):
        """Set content (text or widget)"""
        # Clear existing
        self._qml_children.clear()
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if isinstance(content, str):
            label = QLabel(content)
            label.setWordWrap(True)
            self.layout.addWidget(label)
        elif isinstance(content, QWidget):
            self._qml_children.append(content)
            self.layout.addWidget(content)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    spacing: 5\n"
        qml += f"{tab}    width: parent.width\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


class CardFooter(QWidget):
    """
    Card footer component

    Usage:
        footer = CardFooter()
        footer.add_action(save_button)
        footer.add_action(cancel_button)
    """

    def __init__(self, align="right", parent=None):
        super().__init__(parent)
        self._qml_children = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        if align == "right":
            layout.addStretch()

        self.align = align

    def add_action(self, widget):
        """Add action widget"""
        self._qml_children.append(widget)
        if self.align == "left":
            self.layout().insertWidget(0, widget)
        else:
            self.layout().addWidget(widget)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    spacing: 5\n"
        qml += f"{tab}    width: parent.width\n"
        if self.align == "right":
            qml += f"{tab}    Item {{ Layout.fillWidth: true }}\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


class CardGroup(QWidget):
    """
    Group of cards in a row

    Usage:
        group = CardGroup()
        group.add_card(card1)
        group.add_card(card2)
    """

    def __init__(self, spacing=10, parent=None):
        super().__init__(parent)
        self._qml_children = []
        self._spacing = spacing

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

    def add_card(self, card, stretch=1):
        """Add card to group"""
        self._qml_children.append(card)
        self.layout.addWidget(card, stretch)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    spacing: {self._spacing}\n"
        qml += f"{tab}    width: parent.width\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


from .buttons import ToggleSwitch


class FeatureCardGroup(QWidget):
    """Arrange ordered feature cards in columns, filling the final partial row.

    With three cards and two columns, the first two share the top row and
    the last card spans the bottom row. Callers only supply the card order.
    """

    def __init__(self, columns=2, spacing=10, parent=None):
        super().__init__(parent)
        if columns < 1:
            raise ValueError("columns must be positive")
        self.columns = columns
        self._cards = []
        self._geometry_timer = QTimer(self)
        self._geometry_timer.setSingleShot(True)
        self._geometry_timer.setInterval(0)
        self._geometry_timer.timeout.connect(self._refresh_geometry)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(spacing)
        group_policy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        group_policy.setHeightForWidth(True)
        self.setSizePolicy(group_policy)
        for column in range(columns):
            self.grid_layout.setColumnStretch(column, 1)

    def add_card(self, card):
        """Append a card and automatically distribute the final row."""
        self._cards.append(card)
        card._feature_card_header_layout = card.main_layout.itemAt(0).layout()
        card._feature_card_show_toggle = False
        card._configure_group_content()
        card.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        card.installEventFilter(self)
        for label in (card.title_lbl, card.desc_lbl, card.algorithm_lbl):
            label.setTextFormat(Qt.TextFormat.PlainText)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            label.installEventFilter(self)
        card.value_changed.connect(lambda *_: self._geometry_timer.start())
        card_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card_policy.setHeightForWidth(True)
        card.setSizePolicy(card_policy)
        card.setMinimumWidth(0)
        card.title_lbl.setWordWrap(True)
        card.title_lbl.setMinimumWidth(0)
        title_policy = QSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        title_policy.setHeightForWidth(True)
        card.title_lbl.setSizePolicy(title_policy)
        card.combo.setMinimumWidth(0)
        card.combo.setMinimumContentsLength(0)
        card.combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )

        while self.grid_layout.count():
            self.grid_layout.takeAt(0)
        for index, widget in enumerate(self._cards):
            row, column = divmod(index, self.columns)
            span = self.columns - column if index == len(self._cards) - 1 else 1
            self.grid_layout.addWidget(widget, row, column, 1, span)
            # Rows follow the tallest card's content. Surplus viewport space
            # belongs to the scroll area, not inside the cards.
            self.grid_layout.setRowStretch(row, 0)
        self._geometry_timer.start()

    def sizeHint(self):
        """Keep wrapped text visible without stretching the card rows."""
        hint = super().sizeHint()
        height = self.heightForWidth(self.width())
        if height >= 0:
            hint.setHeight(height)
        return hint

    def minimumSizeHint(self):
        hint = super().minimumSizeHint()
        hint.setHeight(self.heightForWidth(self.width()))
        return hint

    def heightForWidth(self, width):
        spacing = self.grid_layout.spacing()
        cell_width = max(0, (width - spacing * (self.columns - 1)) // self.columns)
        heights = {}
        for index, card in enumerate(self._cards):
            row, column = divmod(index, self.columns)
            card_width = (
                width - column * (cell_width + spacing)
                if index == len(self._cards) - 1
                else cell_width
            )
            height = card.heightForWidth(max(0, card_width))
            heights[row] = max(heights.get(row, 0), height)
        return sum(heights.values()) + spacing * max(0, len(heights) - 1)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.size().width() != event.oldSize().width():
            self._geometry_timer.start()

    def _refresh_geometry(self):
        row_heights = {}
        changed = False
        for card in self._cards:
            changed = card._refresh_group_text_geometry() or changed
        for index, card in enumerate(self._cards):
            row = index // self.columns
            height = card.heightForWidth(card.width())
            row_heights[row] = max(row_heights.get(row, 0), height)
        for row, height in row_heights.items():
            height = max(0, height)
            if self.grid_layout.rowMinimumHeight(row) != height:
                self.grid_layout.setRowMinimumHeight(row, height)
                changed = True
        if changed:
            self.updateGeometry()

    def eventFilter(self, watched, event):
        if event.type() in (
            QEvent.Type.Resize, QEvent.Type.FontChange,
            QEvent.Type.StyleChange, QEvent.Type.LayoutRequest,
        ):
            self._geometry_timer.start()
        return super().eventFilter(watched, event)


class FeatureCardSelect(QComboBox):
    """Keep the selected name readable within the card using up to two lines."""

    def __init__(self, parent=None, minimum_font_px=8, maximum_font_px=12):
        super().__init__(parent)
        self.set_font_size_range(minimum_font_px, maximum_font_px)
        self.currentTextChanged.connect(self.setToolTip)

    def set_font_size_range(self, minimum_px, maximum_px):
        if not 0 < minimum_px <= maximum_px:
            raise ValueError("Font sizes must satisfy 0 < minimum <= maximum")
        self.minimum_font_px = int(minimum_px)
        self.maximum_font_px = int(maximum_px)
        font = QFont(self.font())
        font.setPixelSize(self.maximum_font_px)
        self.setMinimumHeight(2 * QFontMetrics(font).lineSpacing() + 8)
        self.view().setStyleSheet(f"font-size: {self.maximum_font_px}px;")
        self.updateGeometry()
        self.update()

    def _selected_lines(self, width):
        text = self.currentText()
        for size in range(self.maximum_font_px, self.minimum_font_px - 1, -1):
            font = QFont(self.font())
            font.setPixelSize(size)
            layout = QTextLayout(text, font)
            option = QTextOption()
            option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
            layout.setTextOption(option)
            layout.beginLayout()
            lines = []
            starts = []
            for _ in range(3):
                line = layout.createLine()
                if not line.isValid():
                    break
                line.setLineWidth(max(1, width))
                starts.append(line.textStart())
                lines.append(text[line.textStart():line.textStart() + line.textLength()].strip())
            layout.endLayout()
            if len(lines) <= 2:
                return font, lines
        lines[1] = QFontMetrics(font).elidedText(
            text[starts[1]:], Qt.TextElideMode.ElideRight, max(1, width)
        )
        return font, lines[:2]

    def paintEvent(self, event):
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.ComplexControl.CC_ComboBox, option)
        rect = self.style().subControlRect(
            QStyle.ComplexControl.CC_ComboBox, option,
            QStyle.SubControl.SC_ComboBoxEditField, self
        ).adjusted(2, 0, -2, 0)
        font, lines = self._selected_lines(rect.width())
        painter.setFont(font)
        group = QPalette.ColorGroup.Active if self.isEnabled() else QPalette.ColorGroup.Disabled
        painter.setPen(option.palette.color(group, QPalette.ColorRole.Text))
        painter.setClipRect(rect)
        metrics = QFontMetrics(font)
        top = rect.top() + (rect.height() - len(lines) * metrics.lineSpacing()) // 2
        for index, line in enumerate(lines):
            painter.drawText(rect.left(), top + metrics.ascent() + index * metrics.lineSpacing(), line)

    def showPopup(self):
        font = QFont(self.font())
        font.setPixelSize(self.maximum_font_px)
        metrics = QFontMetrics(font)
        width = max((metrics.horizontalAdvance(self.itemText(i)) for i in range(self.count())), default=0)
        self.view().setMinimumWidth(max(self.width(), width + 28))
        super().showPopup()


class FeatureCard(QFrame, RealtimeMixin):
    """
    A premium toggleable card component for algorithms.
    """

    value_changed = Signal(str)
    checked_changed = Signal(bool)

    def __init__(
        self,
        title,
        description,
        options,
        fallback_val,
        parent=None,
        adaptive_directions=None,
        dropdown_font_min_px=8,
        dropdown_font_max_px=12,
    ):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("featureCard")

        self.is_checked = False
        self.fallback_val = fallback_val
        self.options = [
            opt
            for opt in options
            if opt not in ["No Denoising", "No Super Resolution", "No Alignment"]
        ]
        self._last_click_time = 0

        if adaptive_directions is None:
            adaptive_directions = ["bottom"]
        self.adaptive_directions = adaptive_directions

        # Keep selector-to-UI propagation below the 100ms interaction budget;
        # persistence has its own independent debounce in RightPanel.
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(50)
        self._debounce_timer.timeout.connect(self._emit_debounced_value)

        # Apply adaptive size policies based on direction
        h_policy = (
            QSizePolicy.Policy.Expanding
            if "right" in self.adaptive_directions
            else QSizePolicy.Policy.Preferred
        )
        v_policy = QSizePolicy.Policy.Preferred
        self.setSizePolicy(h_policy, v_policy)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 6, 8, 6)
        self.main_layout.setSpacing(4)

        # Header layout
        header_layout = QHBoxLayout()

        # Premium animated toggle switch (replacing QCheckBox indicator)
        self.switch_indicator = ToggleSwitch(self)
        self.switch_indicator.toggled.connect(self.setChecked)
        header_layout.addWidget(self.switch_indicator)

        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(
            "font-weight: bold; font-size: 11pt; color: #2C3E50; background: transparent;"
        )
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()

        self.main_layout.addLayout(header_layout)

        # Description
        self.desc_lbl = QLabel(description)
        self.desc_lbl.setStyleSheet(
            "color: #7F8C8D; font-size: 9.5pt; background: transparent;"
        )
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setMinimumWidth(0)
        self.main_layout.addWidget(self.desc_lbl)

        # Collapsible Selection container
        self.option_widget = QWidget()
        option_layout = QVBoxLayout(self.option_widget)
        option_layout.setContentsMargins(0, 5, 0, 0)
        option_layout.setSpacing(4)

        # Dropdown selection container (replacing option grid buttons)
        self.combo = FeatureCardSelect(
            minimum_font_px=dropdown_font_min_px,
            maximum_font_px=dropdown_font_max_px,
        )
        self.combo.addItems(self.options)
        self.combo.setStyleSheet(create_select_style())
        self.combo.currentTextChanged.connect(self._on_combo_changed)
        option_layout.addWidget(self.combo)

        self.main_layout.addWidget(self.option_widget)
        self.option_widget.setVisible(False)

        # Setup height animator from library
        self.height_animator = HeightAnimator(self)

        self.update_styles()

    def setEnabled(self, enabled):
        super().setEnabled(enabled)
        self.switch_indicator.setEnabled(enabled)
        self.combo.setEnabled(enabled)
        self.update_styles()

        # Apply visual semi-transparency for disabled state
        if not enabled:
            from PySide6.QtWidgets import QGraphicsOpacityEffect

            effect = self.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(self)
                self.setGraphicsEffect(effect)
            effect.setOpacity(0.5)
        else:
            self.setGraphicsEffect(None)

    def resizeEvent(self, event):
        if event:
            super().resizeEvent(event)
        import config
        from resources.GenericUILibrary.theme import get_theme

        theme = get_theme()

        threshold = getattr(config, "FEATURE_CARD_COLLAPSE_THRESHOLD", 230)

        # Adjust font sizes dynamically based on current card width
        w = self.width()
        if w < 180:
            title_sz = 9
            desc_sz = 8
        elif w < 230:
            title_sz = 10
            desc_sz = 8.5
        else:
            title_sz = 11
            desc_sz = 9.5

        self.title_lbl.setStyleSheet(
            f"font-weight: bold; font-size: {title_sz}pt; color: {theme.card_text_title}; background: transparent;"
        )
        self.desc_lbl.setStyleSheet(
            f"color: {theme.card_text_desc}; font-size: {desc_sz}pt; background: transparent;"
        )
        if hasattr(self, "algorithm_lbl"):
            self.algorithm_lbl.setStyleSheet(
                f"color: {theme.card_text_title}; font-size: {desc_sz}pt; font-weight: 600; background: transparent;"
            )
        self._refresh_group_text_geometry()

    def _group_text_heights(self, width):
        """Measure plain wrapped text without stale fixed label heights."""
        margins = self.main_layout.contentsMargins()
        text_width = max(1, width - margins.left() - margins.right() - 2 * self.frameWidth())
        heights = []
        for label in (self.title_lbl, self.desc_lbl, self.algorithm_lbl):
            label.ensurePolished()
            metrics = QFontMetrics(label.font())
            height = metrics.boundingRect(
                0, 0, max(1, text_width - self.help_btn.width() - 5)
                if label is self.title_lbl else text_width, 16777215,
                int(Qt.TextFlag.TextWordWrap), label.text(),
            ).height()
            heights.append(max(metrics.height(), height))
        return [max(heights[0], self.help_btn.height()), max(heights[1:])]

    def _refresh_group_text_geometry(self):
        if not hasattr(self, "body_stack"):
            return False
        changed = False
        for label, height in zip(
            (self.title_lbl, self.body_stack), self._group_text_heights(self.width())
        ):
            if label.minimumHeight() != height or label.maximumHeight() != height:
                label.setFixedHeight(height)
                changed = True
        if changed:
            self.updateGeometry()
        self.help_btn.setToolTip(self.desc_lbl.text())
        return changed

    def _configure_group_content(self):
        """Own title/help placement and a stable description/selection viewport."""
        header = self._feature_card_header_layout
        self.switch_indicator.hide()
        header.removeWidget(self.switch_indicator)
        if header.count() and header.itemAt(header.count() - 1).spacerItem():
            header.takeAt(header.count() - 1)
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(5)
        header.setStretch(0, 1)
        self.help_btn = Button("?", variant="ghost", object_name="FeatureCardHelpButton", parent=self)
        self.help_btn.setFixedSize(18, 18)
        self.help_btn.setStyleSheet("""
            QPushButton#FeatureCardHelpButton {
                background-color: #E8F3F9; color: #0078D4;
                border: 1px solid #B8D8EA; border-radius: 9px;
                padding: 0px; font-size: 11px; font-weight: bold;
            }
            QPushButton#FeatureCardHelpButton:hover {
                background-color: #D5ECF8; border-color: #0078D4;
            }
            QPushButton#FeatureCardHelpButton:pressed { background-color: #B8D8EA; }
        """)
        self.help_btn.clicked.connect(lambda: self._set_group_body(True))
        header.addWidget(self.help_btn, 0, Qt.AlignmentFlag.AlignTop)
        self.main_layout.removeWidget(self.desc_lbl)
        self.algorithm_lbl = QLabel(self.combo.currentText(), self)
        self.algorithm_lbl.setWordWrap(True)
        self.algorithm_lbl.setMinimumWidth(0)
        self.algorithm_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.body_stack = QStackedWidget(self)
        self.body_stack.addWidget(self.desc_lbl)
        self.body_stack.addWidget(self.algorithm_lbl)
        self.body_animator = StackedWidgetAnimator(self)
        self.main_layout.insertWidget(1, self.body_stack)
        self.main_layout.setAlignment(Qt.AlignmentFlag(0))
        self.main_layout.addStretch(1)
        self.option_widget.setFixedHeight(0)
        self.option_widget.hide()
        self._showing_description = not self.is_checked
        self.body_stack.setCurrentWidget(self.desc_lbl if self._showing_description else self.algorithm_lbl)
        self.resizeEvent(None)

    def _set_group_body(self, show_description, animate=True):
        if not hasattr(self, "body_stack"):
            return
        self._refresh_group_text_geometry()
        self._showing_description = bool(show_description or not self.is_checked)
        target = self.desc_lbl if self._showing_description else self.algorithm_lbl
        if animate:
            self.body_animator.transition_in(
                self.body_stack, target,
                AnimationType.SLIDE_LEFT if self._showing_description else AnimationType.SLIDE_RIGHT,
                duration_out=100, duration_in=160,
            )
        else:
            self.body_animator.stop_all()
            self.body_stack.setCurrentWidget(target)
            target.move(0, 0)

    def _activate_group_card(self):
        if self.is_checked and self._showing_description:
            self._set_group_body(False)
        else:
            self._show_group_options()

    def heightForWidth(self, width):
        if not hasattr(self, "_feature_card_header_layout"):
            return super().heightForWidth(width)
        margins = self.main_layout.contentsMargins()
        return (
            sum(self._group_text_heights(width)) + margins.top() + margins.bottom()
            + self.main_layout.spacing() + 2 * self.frameWidth()
        )

    def _emit_debounced_value(self):
        self.value_changed.emit(self.get_value())

    def setChecked(self, checked, animate=True):
        # Grouped cards share row heights; keep their content compact and
        # update options synchronously instead of resizing the parent grid.
        if hasattr(self, "_feature_card_header_layout"):
            animate = False
        if self.is_checked != checked:
            self.is_checked = checked
            self.switch_indicator.setChecked(checked)

            # Smoothly animate options expansion using HeightAnimator if animate=True
            if hasattr(self, "_feature_card_header_layout"):
                self.option_widget.setFixedHeight(0)
                self.option_widget.hide()
            elif checked:
                self.option_widget.show()
                target_h = self.option_widget.sizeHint().height()
                if animate:
                    self.height_animator.animate_height(self.option_widget, target_h)
                else:
                    self.option_widget.setFixedHeight(target_h)
            else:
                if animate:
                    self.height_animator.animate_height(self.option_widget, 0)
                else:
                    self.option_widget.setFixedHeight(0)
                    self.option_widget.hide()

            self.update_styles()
            self._set_group_body(not checked, animate=False)
            self.checked_changed.emit(checked)
            if animate:
                self._debounce_timer.start()
            else:
                self._emit_debounced_value()

            # Request parent right panel to recalculate layout height if bottom expansion active
            if "bottom" in self.adaptive_directions:
                parent_panel = self.parentWidget()
                while parent_panel:
                    if hasattr(parent_panel, "algo_container"):
                        if hasattr(parent_panel, "_balance_splitter_sizes"):
                            if animate:
                                QTimer.singleShot(
                                    260, parent_panel._balance_splitter_sizes
                                )
                            else:
                                parent_panel._balance_splitter_sizes()
                        elif hasattr(parent_panel, "_calculate_algo_target_h"):
                            parent_panel.algo_container.setFixedHeight(
                                parent_panel._calculate_algo_target_h()
                            )
                        break
                    parent_panel = parent_panel.parentWidget()

    def mousePressEvent(self, event):
        if not self.isEnabled():
            super().mousePressEvent(event)
            return

        import time

        current_time = time.time()
        if current_time - getattr(self, "_last_click_time", 0) < 0.25:
            event.accept()
            return
        self._last_click_time = current_time

        pos = event.position().toPoint()
        child = self.childAt(pos)
        # If clicked inside option widget or on the toggle switch, let children handle it
        if child and (
            child == self.switch_indicator or self.option_widget.isAncestorOf(child)
        ):
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, "_feature_card_header_layout"):
                self._activate_group_card()
            else:
                self.setChecked(not self.is_checked)
        super().mousePressEvent(event)

    def _show_group_options(self):
        """Use the card as the selector instead of reserving an inline dropdown."""
        if not self.is_checked:
            self.setChecked(True)
        menu = QMenu(self)
        for index in range(self.combo.count()):
            action = menu.addAction(self.combo.itemText(index))
            action.setCheckable(True)
            action.setChecked(index == self.combo.currentIndex())
            action.triggered.connect(
                lambda _checked=False, selected=index: self.combo.setCurrentIndex(selected)
            )
        menu.addSeparator()
        off_action = menu.addAction(self.fallback_val)
        off_action.triggered.connect(lambda: self.setChecked(False))
        def release_menu():
            if getattr(self, "_options_menu", None) is menu:
                self._options_menu = None
            menu.deleteLater()

        menu.aboutToHide.connect(release_menu)
        self._options_menu = menu
        menu.popup(self.mapToGlobal(QPoint(0, self.height())))

    def keyPressEvent(self, event):
        if hasattr(self, "_feature_card_header_layout") and event.key() in (
            Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter,
        ):
            self._activate_group_card()
            event.accept()
            return
        super().keyPressEvent(event)

    def _on_combo_changed(self, text):
        if hasattr(self, "algorithm_lbl"):
            self.algorithm_lbl.setText(text)
            self._refresh_group_text_geometry()
            if self.is_checked:
                self._set_group_body(False)
        if self.is_checked:
            self._debounce_timer.start()

    def get_value(self):
        if self.is_checked:
            return self.combo.currentText()
        return self.fallback_val

    def set_value(self, val):
        self.blockSignals(True)
        if val == self.fallback_val or not val:
            self.setChecked(False, animate=False)
        else:
            self.setChecked(True, animate=False)
            idx = self.combo.findText(val)
            if idx >= 0:
                self.combo.setCurrentIndex(idx)
        self.blockSignals(False)

    def update_styles(self):
        from resources.GenericUILibrary.theme import get_theme

        theme = get_theme()
        if not self.isEnabled():
            self.setStyleSheet(
                f"""
                QFrame#featureCard {{
                    background-color: {theme.card_disabled_bg};
                    border: 1px solid {theme.card_disabled_border};
                    border-radius: 8px;
                }}
                QLabel {{
                    color: {theme.text_muted};
                }}
            """
            )
        elif self.is_checked:
            self.setStyleSheet(
                f"""
                QFrame#featureCard {{
                    background-color: {theme.card_checked_bg};
                    border: 2px solid {theme.card_checked_border};
                    border-radius: 8px;
                }}
                QLabel {{
                    color: {theme.card_text_title};
                }}
            """
            )
        else:
            self.setStyleSheet(
                f"""
                QFrame#featureCard {{
                    background-color: {theme.card_unchecked_bg};
                    border: 1px solid {theme.card_unchecked_border};
                    border-radius: 8px;
                }}
                QLabel {{
                    color: {theme.card_text_title};
                }}
            """
            )

    def update_theme(self):
        """Update styles dynamically when theme switches."""
        self.update_styles()
        self.resizeEvent(None)
        if hasattr(self, "combo"):
            from resources.GenericUILibrary.theme import create_select_style

            self.combo.setStyleSheet(create_select_style())

    def to_qml(self, indent=0):
        tab = "    " * indent
        title = self.title_lbl.text()
        desc = self.desc_lbl.text()
        # description, fallback_val, adaptive_directions:
        _ = getattr(self, "fallback_val", None)
        _ = getattr(self, "adaptive_directions", None)
        checked = str(self.is_checked).lower()
        options_str = "[" + ", ".join(f"'{o}'" for o in self.options) + "]"
        bg = "'#F0FDF4'" if self.is_checked else "'#FFFFFF'"
        border = "'#2ECC71'" if self.is_checked else "'#E8EDF2'"
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: childrenRect.height + 14\n"
        qml += f"{tab}    color: {bg}\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: {border}\n"
        qml += f"{tab}    border.width: {2 if self.is_checked else 1}\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        x: 8\n"
        qml += f"{tab}        y: 6\n"
        qml += f"{tab}        width: parent.width - 16\n"
        qml += f"{tab}        spacing: 4\n"
        qml += f"{tab}        Row {{\n"
        qml += f"{tab}            spacing: 8\n"
        qml += f"{tab}            Rectangle {{\n"
        qml += f"{tab}                width: 36\n"
        qml += f"{tab}                height: 20\n"
        qml += f"{tab}                radius: 10\n"
        qml += f"{tab}                color: parent.checked ? '#2ECC71' : '#BDC3C7'\n"
        qml += f"{tab}                property bool checked: {checked}\n"
        qml += f"{tab}                anchors.verticalCenter: parent.verticalCenter\n"
        qml += f"{tab}                Rectangle {{\n"
        qml += f"{tab}                    x: parent.checked ? 18 : 2\n"
        qml += f"{tab}                    y: 2\n"
        qml += f"{tab}                    width: 16\n"
        qml += f"{tab}                    height: 16\n"
        qml += f"{tab}                    radius: 8\n"
        qml += f"{tab}                    color: '#FFFFFF'\n"
        qml += f"{tab}                    Behavior on x {{ NumberAnimation {{ duration: 150 }} }}\n"
        qml += f"{tab}                }}\n"
        qml += f"{tab}                MouseArea {{\n"
        qml += f"{tab}                    anchors.fill: parent\n"
        qml += f"{tab}                    onClicked: parent.checked = !parent.checked\n"
        qml += f"{tab}                }}\n"
        qml += f"{tab}            }}\n"
        qml += f"{tab}            Text {{ text: '{title}'; font.bold: true; font.pointSize: 11; color: '#2C3E50'; anchors.verticalCenter: parent.verticalCenter }}\n"
        qml += f"{tab}        }}\n"
        qml += f"{tab}        Text {{ text: '{desc}'; font.pointSize: 9.5; color: '#2C3E50'; wrapMode: Text.WordWrap; width: parent.width }}\n"
        qml += f"{tab}        ComboBox {{\n"
        qml += f"{tab}            model: {options_str}\n"
        qml += f"{tab}            visible: {checked}\n"
        qml += f"{tab}            width: parent.width\n"
        qml += f"{tab}        }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
