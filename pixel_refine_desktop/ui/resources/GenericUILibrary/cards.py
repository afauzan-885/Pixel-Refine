"""
Bootstrap-like Card Components for PySide6
Provides reusable card containers
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt


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

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()

        if title:
            self.main_layout.addWidget(self.header)

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
        self.title_label.setText(title)
        self.header.setVisible(bool(title))

    def add_header_widget(self, widget):
        """Add widget to header (e.g., buttons)"""
        self.header_layout.addWidget(widget)

    def set_body_content(self, content):
        """Set body content (text or widget)"""
        # Clear existing body
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if isinstance(content, str):
            label = QLabel(content)
            label.setWordWrap(True)
            self.body_layout.addWidget(label)
        elif isinstance(content, QWidget):
            self.body_layout.addWidget(content)

    def add_body_widget(self, widget, stretch=0):
        """Add widget to body"""
        self.body_layout.addWidget(widget, stretch)

    def add_footer_widget(self, widget):
        """Add widget to footer"""
        self.footer.setVisible(True)
        self.footer_layout.addWidget(widget)

    def clear_body(self):
        """Clear body content"""
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


class CardHeader(QWidget):
    """
    Card header component

    Usage:
        header = CardHeader(title="Settings")
        header.add_action(close_button)
    """

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 5)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")

        layout.addWidget(self.title_label)
        layout.addStretch()

    def set_title(self, title):
        """Set header title"""
        self.title_label.setText(title)

    def add_action(self, widget):
        """Add action widget (button, etc.)"""
        self.layout().addWidget(widget)


class CardBody(QWidget):
    """
    Card body component

    Usage:
        body = CardBody()
        body.add_widget(content_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

    def add_widget(self, widget, stretch=0):
        """Add widget to body"""
        self.layout.addWidget(widget, stretch)

    def set_content(self, content):
        """Set content (text or widget)"""
        # Clear existing
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if isinstance(content, str):
            label = QLabel(content)
            label.setWordWrap(True)
            self.layout.addWidget(label)
        elif isinstance(content, QWidget):
            self.layout.addWidget(content)


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

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        if align == "right":
            layout.addStretch()

        self.align = align

    def add_action(self, widget):
        """Add action widget"""
        if self.align == "left":
            self.layout().insertWidget(0, widget)
        else:
            self.layout().addWidget(widget)


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

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(spacing)

    def add_card(self, card, stretch=1):
        """Add card to group"""
        self.layout.addWidget(card, stretch)
