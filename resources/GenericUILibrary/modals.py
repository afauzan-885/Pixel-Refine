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
    QStyle,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QColor


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
        # Simpan size string untuk digunakan oleh to_qml()
        self._size_str = size

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

    def to_qml(self, indent=0):
        tab = "    " * indent
        title = self.windowTitle().replace("'", "\\'")
        # Gunakan size string yang sudah disimpan saat __init__ (small/medium/large)
        size_str = getattr(self, "_size_str", "medium")
        size_map = {"small": (320, 240), "medium": (480, 320), "large": (640, 480)}
        w, h = size_map.get(size_str, (480, 320))
        qml = f"{tab}Popup {{\n"
        qml += f"{tab}    id: modal\n"
        qml += f"{tab}    width: {w}   // size='{size_str}'\n"
        qml += f"{tab}    height: {h}\n"
        qml += f"{tab}    modal: true\n"
        qml += f"{tab}    anchors.centerIn: parent\n"
        qml += f"{tab}    background: Rectangle {{ color: genericTheme.bgPrimary; radius: genericTheme.radiusLg; border.color: genericTheme.borderColor; border.width: 1 }}\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 16\n"
        qml += f"{tab}        spacing: 12\n"
        qml += f"{tab}        Row {{ width: parent.width; Text {{ text: '{title}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }} }}\n"
        qml += f"{tab}        Item {{ width: 1; height: 1 }}\n"
        qml += f"{tab}        Column {{ width: parent.width; spacing: 10 }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


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

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Text {{ text: '{self.title_label.text()}'; font.bold: true; font.pixelSize: 16; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}    Item {{ Layout.fillWidth: true }}\n"
        qml += f"{tab}}}"
        return qml


class ModalBody(QWidget):
    """Modal body component"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

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

    def add_widget(self, widget, stretch=0):
        """Add widget to body"""
        self._qml_children.append(widget)
        self.layout.addWidget(widget, stretch)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    spacing: 10\n"
        qml += f"{tab}    width: parent.width\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


class ModalFooter(QWidget):
    """Modal footer component"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(5)
        layout.addStretch()

    def add_action(self, widget):
        """Add action widget"""
        self._qml_children.append(widget)
        self.layout().addWidget(widget)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    spacing: 5\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Item {{ Layout.fillWidth: true }}\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 1) + "\n"
        qml += f"{tab}}}"
        return qml


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

    def to_qml(self, indent=0):
        tab = "    " * indent
        msg = self.message_label.text().replace("'", "\\'")
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    anchors.fill: parent\n"
        qml += f"{tab}    color: '#80000000'\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        anchors.centerIn: parent\n"
        qml += f"{tab}        width: 250\n"
        qml += f"{tab}        height: 80\n"
        qml += f"{tab}        radius: genericTheme.radiusLg\n"
        qml += f"{tab}        color: 'white'\n"
        qml += f"{tab}        Text {{ text: '{msg}'; anchors.centerIn: parent; color: '#555' }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class Toast(QWidget):
    """
    Toast notification component

    Usage:
        toast = Toast("Success!", variant="success", parent=self)
        toast.show_toast(duration=3000)
    """

    def __init__(self, message="", variant="info", parent=None):
        super().__init__(parent)
        self._variant = variant

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

    def to_qml(self, indent=0):
        tab = "    " * indent
        msg = self.message_label.text().replace("'", "\\'")
        _variant = self._variant if hasattr(self, '_variant') else 'info'
        _theme_color = f"genericTheme.{_variant}" if _variant in ("primary", "success", "danger", "warning", "info") else "genericTheme.info"
        qml = f"{tab}Popup {{\n"
        qml += f"{tab}    width: 300\n"
        qml += f"{tab}    height: 50\n"
        qml += f"{tab}    anchors.centerIn: parent\n"
        qml += f"{tab}    Rectangle {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        radius: genericTheme.radiusMd\n"
        qml += f"{tab}        color: {_theme_color}\n"
        qml += f"{tab}        Text {{ text: '{msg}'; color: 'white'; font.bold: true; anchors.centerIn: parent }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    Timer {{ interval: 3000; running: true; onTriggered: parent.close() }}\n"
        qml += f"{tab}}}"
        return qml

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

    def to_qml(self, indent=0):
        tab = "    " * indent
        msg = self.message_label.text().replace("'", "\\'")
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    anchors.centerIn: parent\n"
        qml += f"{tab}    spacing: 10\n"
        qml += f"{tab}    BusyIndicator {{ running: true; width: 48; height: 48; anchors.horizontalCenter: parent.horizontalCenter }}\n"
        qml += f"{tab}    Text {{ text: '{msg}'; color: genericTheme.textSecondary; anchors.horizontalCenter: parent.horizontalCenter }}\n"
        qml += f"{tab}}}"
        return qml


class modal_confirm(QDialog):
    """
    A premium styled, frameless, custom confirmation dialog matching the exact layout of image 2.
    It contains a clean title bar (with title and icon, but no minimize/maximize/close system buttons),
    a blue query icon next to the confirmation message, action buttons at the bottom right,
    and a smooth fade-in animation.
    """
    def __init__(self, message="Are you sure?", parent=None):
        super().__init__(parent)
        self._drag_active = False
        self._drag_position = None
        self.setModal(True)
        # Frameless and transparent window background
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Set exact dialog size (matching standard confirm boxes with extra room for shadow margins)
        self.setFixedSize(440, 190)
        
        # Setup Fade-in Animation
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # margin for drop shadow
        
        # Card container widget for border, shadow and background
        self.container = QWidget(self)
        self.container.setObjectName("ConfirmContainer")
        self.container.setStyleSheet("""
            QWidget#ConfirmContainer {
                background-color: #F8FAFC; /* Clean off-white/light gray */
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
        """)
        
        # Drop shadow effect
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.container.setGraphicsEffect(shadow)
        
        # Container interior layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 12)
        container_layout.setSpacing(0)
        
        # 1. Custom Title Bar (matching Image 2 header style)
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)
        self.title_bar.setStyleSheet("""
             QWidget#TitleBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E2E8F0;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
        """)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(12, 0, 12, 0)
        
        # Title bar text (Logo Qt dihapus, hanya label tulisan)
        self.title_text = QLabel("Confirm Delete")
        self.title_text.setStyleSheet("font-family: 'Segoe UI', Arial; font-size: 12px; color: #1E293B; font-weight: 500; background-color: transparent;")
        title_layout.addWidget(self.title_text)
        title_layout.addStretch()
        
        container_layout.addWidget(self.title_bar)
        
        # 2. Content Layout (Side-by-side Icon and Text)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(18, 16, 18, 10)
        content_layout.setSpacing(14)
        
        # Blue question icon
        self.query_icon = QLabel()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
        self.query_icon.setPixmap(icon.pixmap(30, 30))
        self.query_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(self.query_icon)
        
        # Confirmation message label
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13.5px;
            color: #334155;
            line-height: 1.4;
        """)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(self.message_label, 1)
        
        container_layout.addWidget(content_widget, 1)
        
        # 3. Action Buttons (Yes/No)
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(18, 0, 18, 4)
        button_layout.setSpacing(8)
        button_layout.addStretch()

        from .theme import get_theme, create_button_style
        theme = get_theme()
        from .buttons import Button
        self.yes_button = Button("Yes", variant="primary")
        self.yes_button.setFixedWidth(32)
        self.yes_button.setStyleSheet(create_button_style("primary", theme) + " QPushButton { border: 1px solid #A9DFBF; padding: 2px; font-size: 8pt; }")
        self.yes_button.clicked.connect(self.accept)
        
        self.no_button = Button("No", variant="secondary")
        self.no_button.setFixedWidth(32)
        self.no_button.setStyleSheet(create_button_style("secondary", theme) + f" QPushButton {{ border: 1px solid {theme.border_color}; background-color: {theme.bg_secondary}; color: {theme.text_primary}; padding: 2px; font-size: 8pt; }}")
        self.no_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.no_button)
        
        container_layout.addWidget(button_widget)
        
        main_layout.addWidget(self.container)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos_in_title = self.title_bar.mapFrom(self, event.position().toPoint())
            if self.title_bar.rect().contains(pos_in_title):
                self._drag_active = True
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
                return
            
            # Click outside to close (reject)
            if not self.container.geometry().contains(event.position().toPoint()):
                self.reject()
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False
            event.accept()
            return
        super().mouseReleaseEvent(event)
        
    def showEvent(self, event):
        super().showEvent(event)
        self.fade_anim.start()
        
    @staticmethod
    def question(parent, message):
        """
        Static helper that shows the dialog and returns True if 'Yes' is clicked.
        """
        dialog = modal_confirm(message, parent)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

    def to_qml(self, indent=0):
        tab = "    " * indent
        msg = self.message_label.text().replace("'", "\\'")
        qml = f"{tab}Dialog {{\n"
        qml += f"{tab}    width: 400\n"
        qml += f"{tab}    height: 150\n"
        qml += f"{tab}    modal: true\n"
        qml += f"{tab}    anchors.centerIn: parent\n"
        qml += f"{tab}    title: 'Confirm'\n"
        qml += f"{tab}    Text {{ text: '{msg}'; wrapMode: Text.WordWrap; width: parent.width; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}    footer: Row {{\n"
        qml += f"{tab}        spacing: 8\n"
        qml += f"{tab}        Item {{ Layout.fillWidth: true }}\n"
        qml += f"{tab}        Button {{ text: 'Yes'; onClicked: parent.parent.accept() }}\n"
        qml += f"{tab}        Button {{ text: 'No'; onClicked: parent.parent.reject() }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


