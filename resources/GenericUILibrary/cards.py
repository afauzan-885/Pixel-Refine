"""
Bootstrap-like Card Components for PySide6
Provides reusable card containers
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QComboBox,
    QCheckBox,
    QPushButton,
    QGridLayout,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush
from .mixins import RealtimeMixin
from .theme import create_checkbox_style, create_select_style
from resources.animations.animation_manager import (
    HeightAnimator,
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
        qml += f"{tab}    height: {120 + len(self._qml_children) * 50}\n"
        qml += f"{tab}    color: genericTheme.bgPrimary\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: genericTheme.borderColor\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 16\n"
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


class FeatureCard(QFrame, RealtimeMixin):
    """
    A premium toggleable card component for algorithms.
    """

    value_changed = Signal(str)

    def __init__(
        self,
        title,
        description,
        options,
        fallback_val,
        parent=None,
        adaptive_directions=None,
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

        # Setup debouncing timer (200ms) to prevent rapid signal spamming
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(200)
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
        self.combo = QComboBox()
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

    def _emit_debounced_value(self):
        self.value_changed.emit(self.get_value())

    def setChecked(self, checked):
        if self.is_checked != checked:
            self.is_checked = checked
            self.switch_indicator.setChecked(checked)

            # Smoothly animate options expansion using HeightAnimator
            if checked:
                self.option_widget.show()
                target_h = self.option_widget.sizeHint().height()
                self.height_animator.animate_height(self.option_widget, target_h)
            else:
                self.height_animator.animate_height(self.option_widget, 0)

            self.update_styles()
            self._debounce_timer.start()

            # Request parent right panel to recalculate layout height if bottom expansion active
            if "bottom" in self.adaptive_directions:
                parent_panel = self.parentWidget()
                while parent_panel:
                    if hasattr(parent_panel, "algo_container") and hasattr(
                        parent_panel, "_calculate_algo_target_h"
                    ):
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
            self.setChecked(not self.is_checked)
        super().mousePressEvent(event)

    def _on_combo_changed(self, text):
        if self.is_checked:
            self._debounce_timer.start()

    def get_value(self):
        if self.is_checked:
            return self.combo.currentText()
        return self.fallback_val

    def set_value(self, val):
        self.blockSignals(True)
        if val == self.fallback_val or not val:
            self.setChecked(False)
        else:
            self.setChecked(True)
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
        qml += f"{tab}    height: contentCol.height + 14\n"
        qml += f"{tab}    color: {bg}\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: {border}\n"
        qml += f"{tab}    border.width: {2 if self.is_checked else 1}\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        id: contentCol\n"
        qml += f"{tab}        x: 8\n"
        qml += f"{tab}        y: 6\n"
        qml += f"{tab}        width: parent.width - 16\n"
        qml += f"{tab}        spacing: 4\n"
        qml += f"{tab}        Row {{\n"
        qml += f"{tab}            spacing: 8\n"
        qml += f"{tab}            Rectangle {{\n"
        qml += f"{tab}                id: toggleCapsule\n"
        qml += f"{tab}                width: 36\n"
        qml += f"{tab}                height: 20\n"
        qml += f"{tab}                radius: 10\n"
        qml += f"{tab}                color: toggleCapsule.checked ? '#2ECC71' : '#BDC3C7'\n"
        qml += f"{tab}                property bool checked: {checked}\n"
        qml += f"{tab}                anchors.verticalCenter: parent.verticalCenter\n"
        qml += f"{tab}                Rectangle {{\n"
        qml += f"{tab}                    x: toggleCapsule.checked ? 18 : 2\n"
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
