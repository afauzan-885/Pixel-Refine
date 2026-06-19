"""
Dot Indicator Component for PySide6
Provides pagination dot indicators for mobile UI
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor


class DotIndicator(QWidget):
    """
    A row of dots indicating current page/position.

    Usage:
        dots = DotIndicator(count=6, active_index=0)
        dots.index_changed.connect(on_page_change)
        layout.addWidget(dots)
    """

    index_changed = Signal(int)

    def __init__(self, count=6, active_index=0, parent=None):
        super().__init__(parent)
        self._count = count
        self._active_index = active_index
        self._dot_size = 8
        self._spacing = 6
        self._qml_children = []

        # Calculate fixed size
        total_width = count * self._dot_size + (count - 1) * self._spacing
        self.setFixedSize(total_width + 4, self._dot_size + 4)

    @property
    def active_index(self):
        return self._active_index

    @active_index.setter
    def active_index(self, index):
        if 0 <= index < self._count:
            self._active_index = index
            self.update()

    def set_count(self, count):
        """Update the number of dots."""
        self._count = count
        if self._active_index >= count:
            self._active_index = max(0, count - 1)
        total_width = count * self._dot_size + (count - 1) * self._spacing
        self.setFixedSize(total_width + 4, self._dot_size + 4)
        self.update()

    def mousePressEvent(self, event):
        """Handle click on dots to change active index."""
        x = event.position().x()
        for i in range(self._count):
            dot_x = 2 + i * (self._dot_size + self._spacing)
            if dot_x <= x <= dot_x + self._dot_size:
                if self._active_index != i:
                    self._active_index = i
                    self.update()
                    self.index_changed.emit(i)
                break

    def paintEvent(self, event):
        """Draw the dots."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for i in range(self._count):
            x = 2 + i * (self._dot_size + self._spacing)
            y = 2

            if i == self._active_index:
                color = QColor("#2ECC71")  # Active: green
            else:
                color = QColor("#BDC3C7")  # Inactive: gray

            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(x, y, self._dot_size, self._dot_size)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Row {{\n"
        qml += f"{tab}    spacing: 6\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    anchors.horizontalCenter: parent.horizontalCenter\n"
        qml += f"{tab}    property int activeIndex: {self._active_index}\n"
        for i in range(self._count):
            qml += f"{tab}    Rectangle {{\n"
            qml += f"{tab}        width: 8\n"
            qml += f"{tab}        height: 8\n"
            qml += f"{tab}        radius: 4\n"
            qml += f"{tab}        color: index === activeIndex ? '#2ECC71' : '#BDC3C7'\n"
            qml += f"{tab}        MouseArea {{\n"
            qml += f"{tab}            anchors.fill: parent\n"
            qml += f"{tab}            onClicked: activeIndex = {i}\n"
            qml += f"{tab}        }}\n"
            qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
