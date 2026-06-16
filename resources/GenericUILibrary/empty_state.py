from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from .theme import get_theme
from .buttons import Button


class EmptyState(QWidget):
    """
    A friendly component to display when there is no content to show.
    Supports optional title, description message, and an optional action button.

    Usage:
        # With title
        empty = EmptyState(
            title="No Projects",
            message="Create a new project to get started.",
            button_text="Create Project",
            on_click=self.handle_create
        )
        
        # Without title (message only)
        empty = EmptyState(
            message="Drag and drop images here.",
            button_text="Browse",
            button_variant="secondary",
            on_click=self.handle_browse
        )
    """

    def __init__(
        self,
        title: str = None,
        message: str = "",
        button_text: str = None,
        button_variant: str = "primary",
        on_click=None,
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # Title (optional)
        theme = get_theme()
        if title:
            self.title_label = QLabel(title)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setStyleSheet(
                f"""
                font-size: 18px;
                font-weight: bold;
                color: {theme.text_primary};
            """
            )
            layout.addWidget(self.title_label)
        else:
            self.title_label = None

        # Message
        if message:
            self.message_label = QLabel(message)
            self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.message_label.setWordWrap(True)
            self.message_label.setStyleSheet(
                f"""
                font-size: 14px;
                color: {theme.text_secondary};
            """
            )
            layout.addWidget(self.message_label)
        else:
            self.message_label = None

        # Action Button
        if button_text:
            self.action_button = Button(button_text, variant=button_variant)
            self.action_button.setFixedWidth(150)  # Friendly width
            if on_click:
                self.action_button.clicked.connect(on_click)

            # Container for button to center it properly if needed, though alignment handles it
            layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignCenter)
        else:
            self.action_button = None

    def set_text(self, title: str = None, message: str = ""):
        """Update the text content."""
        if title and self.title_label:
            self.title_label.setText(title)
        elif title and not self.title_label:
            # Create title label if it doesn't exist
            theme = get_theme()
            self.title_label = QLabel(title)
            self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.title_label.setStyleSheet(
                f"""
                font-size: 18px;
                font-weight: bold;
                color: {theme.text_primary};
            """
            )
            # Insert at beginning of layout
            self.layout().insertWidget(0, self.title_label)
        
        if message and self.message_label:
            self.message_label.setText(message)
        elif message and not self.message_label:
            # Create message label if it doesn't exist
            theme = get_theme()
            self.message_label = QLabel(message)
            self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.message_label.setWordWrap(True)
            self.message_label.setStyleSheet(
                f"""
                font-size: 14px;
                color: {theme.text_secondary};
            """
            )
            # Insert after title (or at position 1 if title exists)
            insert_pos = 1 if self.title_label else 0
            self.layout().insertWidget(insert_pos, self.message_label)

    def to_qml(self, indent=0):
        tab = "    " * indent
        # button_text, button_variant, on_click
        title_text = self.title_label.text() if self.title_label else ""
        msg_text = self.message_label.text() if self.message_label else ""
        btn_text = self.action_button.text() if self.action_button else ""
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    anchors.centerIn: parent\n"
        qml += f"{tab}    spacing: 15\n"
        if title_text:
            qml += f"{tab}    Text {{ text: '{title_text}'; font.bold: true; font.pixelSize: 18; horizontalAlignment: Text.AlignHCenter; color: genericTheme.textPrimary }}\n"
        if msg_text:
            qml += f"{tab}    Text {{ text: '{msg_text}'; font.pixelSize: 14; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.WordWrap; width: 300; color: genericTheme.textSecondary }}\n"
        if btn_text:
            qml += f"{tab}    Rectangle {{\n"
            qml += f"{tab}        width: 150\n"
            qml += f"{tab}        height: 40\n"
            qml += f"{tab}        radius: genericTheme.radiusMd\n"
            qml += f"{tab}        color: genericTheme.primary\n"
            qml += f"{tab}        anchors.horizontalCenter: parent.horizontalCenter\n"
            qml += f"{tab}        Text {{ text: '{btn_text}'; color: 'white'; font.bold: true; anchors.centerIn: parent }}\n"
            qml += f"{tab}        MouseArea {{ anchors.fill: parent; onClicked: appBridge.openTool('{btn_text}') }}\n"
            qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
