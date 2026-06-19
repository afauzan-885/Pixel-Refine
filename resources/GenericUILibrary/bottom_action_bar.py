"""
Bottom Action Bar Component for PySide6
Provides a bottom navigation bar with icons and action button
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon


class BottomActionBar(QWidget):
    """
    A bottom action bar with navigation items and a primary action button.

    Usage:
        action_bar = BottomActionBar()
        action_bar.add_nav_item("Home", "home_icon.png", on_home)
        action_bar.add_nav_item("Denoiser", "denoiser_icon.png", on_denoiser)
        action_bar.set_primary_action("Start", on_start)
        layout.addWidget(action_bar)
    """

    nav_clicked = Signal(str)
    primary_action_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []
        self._nav_items = []
        self._primary_action_text = "Start"
        self._is_running = False

        # Set fixed height for bottom bar
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-top: 1px solid #E8EDF2;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 4, 8, 4)
        main_layout.setSpacing(4)

        # Nav items container (scrollable)
        self._nav_container = QWidget()
        self._nav_container.setStyleSheet("background: transparent;")
        self._nav_layout = QHBoxLayout(self._nav_container)
        self._nav_layout.setContentsMargins(0, 0, 0, 0)
        self._nav_layout.setSpacing(2)

        main_layout.addWidget(self._nav_container, 1)

        # Primary action button (circular)
        self._primary_btn = QPushButton(self._primary_action_text)
        self._primary_btn.setFixedSize(50, 50)
        self._primary_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                font-size: 9pt;
            }
            QPushButton:hover {
                background-color: #27AE60;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        self._primary_btn.clicked.connect(self._on_primary_clicked)
        main_layout.addWidget(self._primary_btn)

    def add_nav_item(self, name, icon_path=None, callback=None):
        """Add a navigation item to the bar."""
        item_widget = QWidget()
        item_widget.setStyleSheet("background: transparent;")
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(4, 2, 4, 2)
        item_layout.setSpacing(2)

        # Icon (placeholder if no path)
        icon_label = QLabel("📱" if not icon_path else "")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 16pt; background: transparent;")
        item_layout.addWidget(icon_label)

        # Name label
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-size: 8pt; color: #666666; background: transparent;")
        item_layout.addWidget(name_label)

        # Store reference
        self._nav_items.append({
            "name": name,
            "widget": item_widget,
            "callback": callback
        })

        self._nav_layout.addWidget(item_widget)

        return item_widget

    def set_primary_action(self, text, callback=None):
        """Set the primary action button text and callback."""
        self._primary_action_text = text
        self._primary_btn.setText(text)

    def set_running_state(self, is_running):
        """Update button appearance based on running state."""
        self._is_running = is_running
        if is_running:
            self._primary_btn.setText("Stop")
            self._primary_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #C0392B;
                }
            """)
        else:
            self._primary_btn.setText("Start")
            self._primary_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2ECC71;
                    color: white;
                    border: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #27AE60;
                }
            """)

    def _on_primary_clicked(self):
        """Handle primary action button click."""
        self.primary_action_clicked.emit()

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: 60\n"
        qml += f"{tab}    color: genericTheme.bgPrimary\n"
        qml += f"{tab}    border.color: genericTheme.borderColor\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    Row {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 8\n"
        qml += f"{tab}        spacing: 4\n"

        # Nav items
        for item in self._nav_items:
            qml += f"{tab}        Column {{\n"
            qml += f"{tab}            spacing: 2\n"
            qml += f"{tab}            Text {{ text: '📱'; font.pixelSize: 16; anchors.horizontalCenter: parent.horizontalCenter }}\n"
            qml += f"{tab}            Text {{ text: '{item['name']}'; font.pixelSize: 8; color: genericTheme.textSecondary; anchors.horizontalCenter: parent.horizontalCenter }}\n"
            qml += f"{tab}            MouseArea {{\n"
            qml += f"{tab}                anchors.fill: parent\n"
            qml += f"{tab}                onClicked: appBridge.openTool('{item['name']}')\n"
            qml += f"{tab}            }}\n"
            qml += f"{tab}        }}\n"

        # Primary action button
        btn_color = "'#E74C3C'" if self._is_running else "'#2ECC71'"
        btn_text = "'Stop'" if self._is_running else "'Start'"
        qml += f"{tab}        Rectangle {{\n"
        qml += f"{tab}            width: 50\n"
        qml += f"{tab}            height: 50\n"
        qml += f"{tab}            radius: 25\n"
        qml += f"{tab}            color: {btn_color}\n"
        qml += f"{tab}            Text {{\n"
        qml += f"{tab}                text: {btn_text}\n"
        qml += f"{tab}                color: 'white'\n"
        qml += f"{tab}                font.bold: true\n"
        qml += f"{tab}                font.pixelSize: 10\n"
        qml += f"{tab}                anchors.centerIn: parent\n"
        qml += f"{tab}            }}\n"
        qml += f"{tab}            MouseArea {{\n"
        qml += f"{tab}                anchors.fill: parent\n"
        qml += f"{tab}                onClicked: appBridge.openTool('{self._primary_action_text}')\n"
        qml += f"{tab}            }}\n"
        qml += f"{tab}        }}\n"

        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
