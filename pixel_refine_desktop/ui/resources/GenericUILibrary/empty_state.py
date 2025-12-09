from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from .theme import get_theme
from .buttons import Button


class EmptyState(QWidget):
    """
    A friendly component to display when there is no content to show.
    Supports a title, description message, and an optional action button.

    Usage:
        empty = EmptyState(
            title="No Projects",
            message="Create a new project to get started.",
            button_text="Create Project",
            on_click=self.handle_create
        )
    """

    def __init__(
        self,
        title: str,
        message: str = "",
        button_text: str = None,
        on_click=None,
        parent=None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        # Title
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
        layout.addWidget(self.title_label)

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

        # Action Button
        if button_text:
            self.action_button = Button(button_text, variant="primary")
            self.action_button.setFixedWidth(150)  # Friendly width
            if on_click:
                self.action_button.clicked.connect(on_click)

            # Container for button to center it properly if needed, though alignment handles it
            layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignCenter)
        else:
            self.action_button = None

    def set_text(self, title: str, message: str = ""):
        """Update the text content."""
        self.title_label.setText(title)
        if hasattr(self, "message_label"):
            self.message_label.setText(message)
