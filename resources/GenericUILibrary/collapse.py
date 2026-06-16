"""
Bootstrap-like Collapse and Accordion Components for PySide6
Provides collapsible panels and accordion widgets
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, Slot


class Collapse(QWidget):
    """
    Collapsible panel with animation

    Usage:
        collapse = Collapse(title="Advanced Settings")
        collapse.set_content(settings_widget)
        collapse.toggled.connect(on_toggle)
    """

    toggled = Signal(bool)  # is_expanded

    def __init__(self, title="", expanded=False, parent=None):
        super().__init__(parent)

        self.is_expanded = expanded
        self._title = title
        self._qml_child = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toggle button
        self.toggle_btn = QPushButton(title)
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(expanded)
        self.toggle_btn.clicked.connect(self.toggle)

        layout.addWidget(self.toggle_btn)

        # Content container
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(10, 5, 10, 5)
        self.content_layout.setSpacing(5)

        layout.addWidget(self.content_container)

        # Animation
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Initial state
        if not expanded:
            self.content_container.setMaximumHeight(0)
        else:
            self.content_container.setMaximumHeight(16777215)

    def set_title(self, title):
        """Set collapse title"""
        self.toggle_btn.setText(title)

    def set_content(self, widget):
        """Set content widget"""
        # Clear existing
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._qml_child = widget
        # Add new widget
        self.content_layout.addWidget(widget)

    def add_widget(self, widget):
        """Add widget to content"""
        self._qml_child = widget
        self.content_layout.addWidget(widget)

    @Slot()
    def toggle(self):
        """Toggle collapse state"""
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.expand()
        else:
            self.collapse_panel()

    def expand(self):
        """Expand panel"""
        self.is_expanded = True
        self.toggle_btn.setChecked(True)

        # Get target height
        target_height = self.content_container.sizeHint().height()
        if target_height == 0:
            target_height = 200  # Fallback

        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        self.animation.start()

        self.toggled.emit(True)

    def collapse_panel(self):
        """Collapse panel"""
        self.is_expanded = False
        self.toggle_btn.setChecked(False)

        current_height = self.content_container.height()

        self.animation.setStartValue(current_height)
        self.animation.setEndValue(0)
        self.animation.start()

        self.toggled.emit(False)

    def to_qml(self, indent=0):
        tab = "    " * indent
        expanded = str(self.is_expanded).lower()
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        height: 40\n"
        qml += f"{tab}        color: genericTheme.bgPrimary\n"
        qml += f"{tab}        Text {{ text: '{self._title}'; anchors.verticalCenter: parent.verticalCenter; anchors.left: parent.left; anchors.leftMargin: 10; font.bold: true; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}        MouseArea {{ anchors.fill: parent; onClicked: content.visible = !content.visible }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        id: content\n"
        qml += f"{tab}        visible: {expanded}\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        leftPadding: 10\n"
        qml += f"{tab}        rightPadding: 10\n"
        qml += f"{tab}        topPadding: 5\n"
        qml += f"{tab}        bottomPadding: 5\n"
        if self._qml_child and hasattr(self._qml_child, "to_qml"):
            qml += self._qml_child.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class Accordion(QWidget):
    """
    Accordion with multiple collapsible items (only one open at a time)

    Usage:
        accordion = Accordion()
        accordion.add_item("Section 1", widget1)
        accordion.add_item("Section 2", widget2)
        accordion.item_expanded.connect(on_expand)
    """

    item_expanded = Signal(int, str)  # index, title

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        self.items = []
        self.current_expanded = -1

    def add_item(self, title, widget=None):
        """Add accordion item"""
        item = AccordionItem(title, widget)
        item.toggled.connect(
            lambda expanded, idx=len(self.items): self._on_item_toggled(idx, expanded)
        )

        self.items.append(item)
        self.layout.addWidget(item)

        return len(self.items) - 1

    def expand_item(self, index):
        """Expand specific item"""
        if 0 <= index < len(self.items):
            # Collapse current
            if self.current_expanded >= 0 and self.current_expanded != index:
                self.items[self.current_expanded].collapse_panel()

            # Expand new
            self.items[index].expand()
            self.current_expanded = index

    def collapse_all(self):
        """Collapse all items"""
        for item in self.items:
            item.collapse_panel()
        self.current_expanded = -1

    def _on_item_toggled(self, index, expanded):
        """Handle item toggle"""
        if expanded:
            # Collapse others
            for i, item in enumerate(self.items):
                if i != index:
                    item.collapse_panel()

            self.current_expanded = index
            title = self.items[index].get_title()
            self.item_expanded.emit(index, title)
        else:
            self.current_expanded = -1

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    spacing: 5\n"
        for item in self.items:
            if hasattr(item, "to_qml"):
                qml += item.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


class AccordionItem(QFrame):
    """
    Individual accordion item

    Usage:
        item = AccordionItem("Title", content_widget)
        item.toggled.connect(on_toggle)
    """

    toggled = Signal(bool)

    def __init__(self, title="", widget=None, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.StyledPanel)
        self.is_expanded = False
        self._title = title
        self._qml_child = widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = QPushButton(f"▶ {title}")
        self.header.setCheckable(True)
        self.header.clicked.connect(self.toggle)
        self.header.setStyleSheet(
            """
            QPushButton {
                text-align: left;
                padding: 10px;
                background-color: #FFFFFF;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:checked {
                background-color: #d0d0d0;
            }
        """
        )

        layout.addWidget(self.header)

        # Content
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(10, 10, 10, 10)

        if widget:
            self.content_layout.addWidget(widget)

        layout.addWidget(self.content_container)

        # Animation
        self.animation = QPropertyAnimation(self.content_container, b"maximumHeight")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Initial state
        self.content_container.setMaximumHeight(0)

    def get_title(self):
        """Get item title"""
        text = self.header.text()
        return text.replace("▶ ", "").replace("▼ ", "")

    def set_content(self, widget):
        """Set content widget"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._qml_child = widget
        self.content_layout.addWidget(widget)

    def toggle(self):
        """Toggle item"""
        if self.is_expanded:
            self.collapse_panel()
        else:
            self.expand()

    def expand(self):
        """Expand item"""
        self.is_expanded = True
        self.header.setChecked(True)
        self.header.setText(f"▼ {self.get_title()}")

        target_height = self.content_container.sizeHint().height()
        if target_height == 0:
            target_height = 150

        self.animation.setStartValue(0)
        self.animation.setEndValue(target_height)
        self.animation.start()

        self.toggled.emit(True)

    def collapse_panel(self):
        """Collapse item"""
        self.is_expanded = False
        self.header.setChecked(False)
        self.header.setText(f"▶ {self.get_title()}")

        current_height = self.content_container.height()

        self.animation.setStartValue(current_height)
        self.animation.setEndValue(0)
        self.animation.start()

        self.toggled.emit(False)

    def to_qml(self, indent=0):
        tab = "    " * indent
        # widget:
        _ = getattr(self, "widget", None)
        expanded = str(self.is_expanded).lower()
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        height: 40\n"
        qml += f"{tab}        color: genericTheme.bgPrimary\n"
        qml += f"{tab}        border.color: genericTheme.borderColor\n"
        qml += f"{tab}        border.width: 1\n"
        qml += f"{tab}        Text {{ text: '{self._title}'; anchors.verticalCenter: parent.verticalCenter; anchors.left: parent.left; anchors.leftMargin: 10; font.bold: true; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}        MouseArea {{ anchors.fill: parent; onClicked: content.visible = !content.visible }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        id: content\n"
        qml += f"{tab}        visible: {expanded}\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        leftPadding: 10\n"
        qml += f"{tab}        rightPadding: 10\n"
        qml += f"{tab}        topPadding: 10\n"
        qml += f"{tab}        bottomPadding: 10\n"
        if self._qml_child and hasattr(self._qml_child, "to_qml"):
            qml += self._qml_child.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
