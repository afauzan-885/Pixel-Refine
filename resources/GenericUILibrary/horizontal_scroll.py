"""
Horizontal Scroll Components for PySide6
Provides horizontal scrollable rows for mobile UI patterns
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)
from PySide6.QtCore import Qt


class HorizontalScrollRow(QWidget):
    """
    A horizontally scrollable row of child widgets.

    Usage:
        scroll_row = HorizontalScrollRow(spacing=8)
        scroll_row.add_widget(card1)
        scroll_row.add_widget(card2)
        layout.add_widget(scroll_row)
    """

    def __init__(self, spacing=8, parent=None):
        super().__init__(parent)
        self._qml_children = []
        self._spacing = spacing

        # Outer layout (no margins)
        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setStyleSheet("background: transparent;")

        # Inner container widget
        self._container = QWidget()
        self._container.setStyleSheet("background: transparent;")
        self._inner_layout = QHBoxLayout(self._container)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(spacing)

        self._scroll.setWidget(self._container)
        outer_layout.addWidget(self._scroll)

    def add_widget(self, widget, stretch=0):
        """Add a widget to the horizontal scroll row."""
        self._qml_children.append(widget)
        self._inner_layout.addWidget(widget, stretch)

    def add_stretch(self):
        """Add stretch at the end."""
        self._inner_layout.addStretch()

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Flickable {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: 100\n"
        qml += f"{tab}    contentWidth: childrenRect.width\n"
        qml += f"{tab}    contentHeight: height\n"
        qml += f"{tab}    clip: true\n"
        qml += f"{tab}    flickableDirection: Flickable.HorizontalFlick\n"
        qml += f"{tab}    boundsBehavior: Flickable.StopAtBounds\n"
        qml += f"{tab}    Row {{\n"
        qml += f"{tab}        spacing: {self._spacing}\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class BatchCard(QFrame):
    """
    A card component for batch display in horizontal scroll.

    Usage:
        batch = BatchCard(name="Batch 1", image_count=10)
        batch.clicked.connect(on_batch_click)
        scroll_row.add_widget(batch)
    """

    def __init__(self, name="Batch", image_count=0, parent=None):
        super().__init__(parent)
        self._name = name
        self._image_count = image_count
        self._qml_children = []

        self.setFixedSize(120, 90)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E8EDF2;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #2ECC71;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Batch name label
        from PySide6.QtWidgets import QLabel
        self._name_label = QLabel(name)
        self._name_label.setStyleSheet("font-weight: bold; font-size: 10pt; color: #2C3E50;")
        layout.addWidget(self._name_label)

    def set_name(self, name):
        self._name = name
        self._name_label.setText(name)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: 120\n"
        qml += f"{tab}    height: 90\n"
        qml += f"{tab}    color: genericTheme.bgPrimary\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: genericTheme.borderColor\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        anchors.margins: 8\n"
        qml += f"{tab}        spacing: 4\n"
        qml += f"{tab}        Text {{ text: '{self._name}'; font.bold: true; font.pixelSize: 12; color: genericTheme.textPrimary }}\n"
        qml += f"{tab}        Rectangle {{ width: parent.width; height: 50; color: genericTheme.bgSecondary; radius: 4 }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        onClicked: appBridge.openTool('{self._name}')\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class NewBatchCard(QFrame):
    """
    A special card for creating new batches (with + icon).

    Usage:
        new_batch = NewBatchCard()
        new_batch.clicked.connect(on_new_batch)
        scroll_row.add_widget(new_batch)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []

        self.setFixedSize(90, 90)
        self.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border: 2px dashed #2ECC71;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: #E8F5E9;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        from PySide6.QtWidgets import QLabel
        self._plus_label = QLabel("+")
        self._plus_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2ECC71;")
        layout.addWidget(self._plus_label)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: 90\n"
        qml += f"{tab}    height: 90\n"
        qml += f"{tab}    color: '#F0FDF4'\n"
        qml += f"{tab}    radius: genericTheme.radiusLg\n"
        qml += f"{tab}    border.color: '#2ECC71'\n"
        qml += f"{tab}    border.width: 2\n"
        qml += f"{tab}    Text {{\n"
        qml += f"{tab}        text: '+'\n"
        qml += f"{tab}        font.pixelSize: 28\n"
        qml += f"{tab}        font.bold: true\n"
        qml += f"{tab}        color: '#2ECC71'\n"
        qml += f"{tab}        anchors.centerIn: parent\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    MouseArea {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        onClicked: appBridge.openTool('NewBatch')\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
