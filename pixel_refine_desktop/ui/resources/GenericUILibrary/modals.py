"""
Bootstrap-like Modal and Overlay Components for PySide6
Provides dialog, modal, and overlay components
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QDialog,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve


class Modal(QDialog):
    """
    Bootstrap-like modal dialog

    Usage:
        modal = Modal(title="Confirm Action", parent=self)
        modal.set_body("Are you sure?")
        modal.add_footer_button("Cancel", variant="secondary")
        modal.add_footer_button("Confirm", variant="primary")
        modal.exec()
    """

    def __init__(self, title="", size="medium", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setModal(True)

        # Set size
        if size == "small":
            self.resize(400, 300)
        elif size == "large":
            self.resize(800, 600)
        else:  # medium
            self.resize(600, 400)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        self.header = ModalHeader(title, self)
        layout.addWidget(self.header)

        # Body
        self.body = ModalBody(self)
        layout.addWidget(self.body, 1)

        # Footer
        self.footer = ModalFooter(self)
        layout.addWidget(self.footer)

    def set_title(self, title):
        """Set modal title"""
        self.header.set_title(title)
        self.setWindowTitle(title)

    def set_body(self, content):
        """Set body content (text or widget)"""
        self.body.set_content(content)

    def add_body_widget(self, widget):
        """Add widget to body"""
        self.body.add_widget(widget)

    def add_footer_button(self, text, variant="secondary", callback=None):
        """Add button to footer"""
        import buttons

        btn = buttons.Button(text, variant=variant)

        if callback:
            btn.clicked.connect(callback)
        else:
            # Default: close on click
            btn.clicked.connect(self.accept)

        self.footer.add_action(btn)
        return btn


class ModalHeader(QWidget):
    """Modal header component"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("sectionTitle")

        layout.addWidget(self.title_label)
        layout.addStretch()

    def set_title(self, title):
        """Set title"""
        self.title_label.setText(title)


class ModalBody(QWidget):
    """Modal body component"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

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

    def add_widget(self, widget, stretch=0):
        """Add widget to body"""
        self.layout.addWidget(widget, stretch)


class ModalFooter(QWidget):
    """Modal footer component"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        layout.addStretch()

    def add_action(self, widget):
        """Add action widget"""
        self.layout().addWidget(widget)


class Overlay(QWidget):
    """
    Loading overlay component

    Usage:
        overlay = Overlay(parent=self)
        overlay.show_message("Processing...")
        overlay.hide()
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.message_label = QLabel("Loading...")
        self.message_label.setStyleSheet(
            """
            font-size: 18px;
            color: #555;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
        """
        )
        self.message_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.message_label)

        # Semi-transparent background
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.5);")

        # Initially hidden
        self.hide()

    def show_message(self, message):
        """Show overlay with message"""
        self.message_label.setText(message)
        self.show()
        self.raise_()

    def hide_overlay(self):
        """Hide overlay"""
        self.hide()


class Toast(QWidget):
    """
    Toast notification component

    Usage:
        toast = Toast("Success!", variant="success", parent=self)
        toast.show_toast(duration=3000)
    """

    def __init__(self, message="", variant="info", parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        self.message_label = QLabel(message)
        self.message_label.setStyleSheet(
            f"""
            background-color: {self._get_color(variant)};
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        """
        )

        layout.addWidget(self.message_label)

        # Animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)

    def _get_color(self, variant):
        """Get color based on variant"""
        colors = {
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f39c12",
            "info": "#3498db",
            "primary": "#0078d4",
        }
        return colors.get(variant, "#3498db")

    def show_toast(self, duration=3000):
        """Show toast for specified duration (ms)"""
        self.show()

        # Fade in
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.start()

        # Auto hide after duration
        from PySide6.QtCore import QTimer

        QTimer.singleShot(duration, self._hide_toast)

    def _hide_toast(self):
        """Hide toast with fade out"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.hide)
        self.fade_animation.start()


class LoadingSpinner(QWidget):
    """
    Simple loading indicator

    Usage:
        spinner = LoadingSpinner(message="Loading...")
    """

    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("font-size: 16px; color: #555;")
        self.message_label.setAlignment(Qt.AlignCenter)

        # Progress indicator (you can replace with actual spinner)
        self.progress_label = QLabel("⏳")
        self.progress_label.setStyleSheet("font-size: 32px;")
        self.progress_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.progress_label)
        layout.addWidget(self.message_label)

    def set_message(self, message):
        """Update loading message"""
        self.message_label.setText(message)
