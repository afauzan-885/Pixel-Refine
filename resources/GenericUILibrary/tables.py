"""
Bootstrap-like Table Component for PySide6
Provides a standardized data table with styling and utility methods.
"""

from PySide6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class DataTable(QTableWidget):
    """
    Standardized Table Widget with convenient APIs for batch processing lists.

    Usage:
        table = DataTable(columns=["Name", "Status", "Details"])
        table.add_row(["Item 1", "Pending", "Simple job"])
    """

    def __init__(self, columns=None, parent=None):
        super().__init__(parent)

        # General Setup
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setShowGrid(False)  # Cleaner look
        self.verticalHeader().setVisible(False)

        # Styling
        self.setStyleSheet(
            """
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                gridline-color: #dee2e6;
                selection-background-color: #e9ecef;
                selection-color: #212529;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f2f2f2;
            }
            QTableWidget::item:selected {
                background-color: #e9ecef;
                color: #212529;
            }
        """
        )

        # Columns
        if columns:
            self.setup_columns(columns)

    def setup_columns(self, headers):
        """Set headers and initialize column count."""
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        # Default header resizing
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

    def clear_rows(self):
        """Clear all rows but keep headers."""
        self.setRowCount(0)

    def add_row_items(self, items):
        """
        Add a row with a list of QTableWidgetItem or widgets.
        Returns the index of the new row.
        """
        row = self.rowCount()
        self.insertRow(row)

        for col, item in enumerate(items):
            if isinstance(item, QTableWidgetItem):
                self.setItem(row, col, item)
            elif isinstance(item, QWidget):
                self.setCellWidget(row, col, item)
            elif isinstance(item, str):
                self.setItem(row, col, QTableWidgetItem(item))
            elif item is None:
                self.setItem(row, col, QTableWidgetItem(""))

        return row

    def set_row_color(self, row, color: QColor):
        """Set background color for an entire row."""
        # Convert QColor to css string if needed for stylesheets
        if color == Qt.GlobalColor.transparent:
            color_str = "transparent"
        else:
            color_str = color.name()

        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                item.setBackground(color)

            # Handle widgets (like checkboxes or custom layouts)
            widget = self.cellWidget(row, col)
            if widget:
                # Apply background to the widget container
                widget.setStyleSheet(
                    f"background-color: {color_str}; border-radius: 0px;"
                )
                # And ensure labels inside are transparent so they inherit
                for child in widget.findChildren(QLabel):
                    child.setStyleSheet("background-color: transparent;")

    def get_cell_widget(self, row, col):
        """Safe wrapper to get cell widget."""
        return self.cellWidget(row, col)

    def resize_columns_to_content(self, target_cols=None):
        """Resize specific columns to content."""
        if target_cols:
            for col in target_cols:
                self.horizontalHeader().setSectionResizeMode(
                    col, QHeaderView.ResizeMode.ResizeToContents
                )
        else:
            self.resizeColumnsToContents()

    def to_qml(self, indent=0):
        tab = "    " * indent
        # columns:
        col_count = self.columnCount()
        row_count = self.rowCount()
        headers = []
        for c in range(col_count):
            h_item = self.horizontalHeaderItem(c)
            headers.append(h_item.text() if h_item else "")
        qml = f"{tab}Rectangle {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    height: {44 + min(row_count, 50) * 30}\n"
        qml += f"{tab}    border.color: '#dee2e6'\n"
        qml += f"{tab}    border.width: 1\n"
        qml += f"{tab}    radius: 4\n"
        qml += f"{tab}    clip: true\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        anchors.fill: parent\n"
        qml += f"{tab}        spacing: 0\n"
        # Header row
        qml += f"{tab}        Rectangle {{\n"
        qml += f"{tab}            width: parent.width\n"
        qml += f"{tab}            height: 44\n"
        qml += f"{tab}            color: '#f8f9fa'\n"
        qml += f"{tab}            Rectangle {{ anchors.bottom: parent.bottom; width: parent.width; height: 2; color: '#dee2e6' }}\n"
        qml += f"{tab}            Row {{\n"
        qml += f"{tab}                anchors.fill: parent\n"
        for h in headers:
            qml += f"{tab}                Text {{ text: '{h}'; font.bold: true; width: parent.width / {col_count}; color: '#495057'; verticalAlignment: Text.AlignVCenter; leftPadding: 8; anchors.verticalCenter: parent.verticalCenter }}\n"
        qml += f"{tab}            }}\n"
        qml += f"{tab}        }}\n"
        # Data rows
        for r in range(min(row_count, 50)):
            bg = "'#ffffff'" if r % 2 == 0 else "'#f8f9fa'"
            qml += f"{tab}        Rectangle {{\n"
            qml += f"{tab}            width: parent.width\n"
            qml += f"{tab}            height: 30\n"
            qml += f"{tab}            color: {bg}\n"
            qml += f"{tab}            Rectangle {{ anchors.bottom: parent.bottom; width: parent.width; height: 1; color: '#f2f2f2' }}\n"
            qml += f"{tab}            Row {{\n"
            qml += f"{tab}                anchors.fill: parent\n"
            for c in range(col_count):
                item = self.item(r, c)
                cell_text = item.text() if item else ""
                cell_text = cell_text.replace("'", "\\'")
                qml += f"{tab}                Text {{ text: '{cell_text}'; width: parent.width / {col_count}; verticalAlignment: Text.AlignVCenter; leftPadding: 5; color: genericTheme.textPrimary; anchors.verticalCenter: parent.verticalCenter }}\n"
            qml += f"{tab}            }}\n"
            qml += f"{tab}        }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml
