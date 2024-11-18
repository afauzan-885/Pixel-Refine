from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QIcon


class Sidebar(QWidget):
    def __init__(self, toggle_callback, switch_page_callback):
        super().__init__()
        self.expanded_width = 180
        self.collapsed_width = 70
        self.sidebar_expanded = True
        self.toggle_callback = toggle_callback
        self.switch_page_callback = switch_page_callback

        self.setStyleSheet(
            """
            QWidget {
                background-color: #e0e0e0;
                color: #333;
            }
        """
        )

        # Layout sidebar
        self.sidebar_layout = QVBoxLayout()
        self.setLayout(self.sidebar_layout)

        # Tombol toggle sidebar
        self.toggle_button = QPushButton("☰")
        self.toggle_button.setStyleSheet(
            """
            QPushButton {
                background-color: #c8d6e5;
                border: none;
                color: #333;
                font-size: 18px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #b2bec3;
            }
        """
        )
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.sidebar_layout.addWidget(self.toggle_button)

        # Tombol navigasi
        self.nav_buttons = []
        button_data = [
            ("Import Images", "resources/icon/Import_Images.png"),
            ("Global Alignment", "resources/icon/G_Alignment.svg"),
            ("Local Alignment", "resources/icon/L_Alignment.svg"),
            ("Stacking", "resources/icon/stack_layers.svg"),
            ("Tone Mapping", "resources/icon/Tone_Mapping.svg"),
        ]
        for i, (text, icon_path) in enumerate(button_data):
            btn = self.create_nav_button(text, icon_path, i)
            self.sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        self.sidebar_layout.addStretch()

        # Tombol Settings
        settings_button = self.create_nav_button(
            "Settings", "resources/icon/Setting.svg", len(button_data)
        )
        self.sidebar_layout.addWidget(settings_button)
        self.nav_buttons.append(settings_button)

        # Atur ukuran awal sidebar
        self.setFixedWidth(self.expanded_width)

    def create_nav_button(self, text, icon_path, index):
        """Create a navigation button."""
        btn = QPushButton(text)
        btn.setIcon(QIcon(icon_path))
        btn.setCheckable(True)
        btn.setStyleSheet(
            """
            QPushButton {
                qproperty-iconSize: 24px;
                text-align: left;
                padding: 10px;
                border: none;
                color: #333;
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #dfe6e9;
            }
            QPushButton:checked {
                background-color: #74b9ff;
                color: white;
                font-weight: bold;
            }
        """
        )
        btn.clicked.connect(lambda: self.switch_page_callback(index))
        btn.default_text = text
        return btn

    def toggle_sidebar(self):
        """Toggle the sidebar size."""
        self.sidebar_expanded = not self.sidebar_expanded
        for btn in self.nav_buttons:
            btn.setText(btn.default_text if self.sidebar_expanded else "")
        self.setFixedWidth(
            self.expanded_width if self.sidebar_expanded else self.collapsed_width
        )
        self.toggle_button.setText("☰" if self.sidebar_expanded else "←")
        self.toggle_callback()
