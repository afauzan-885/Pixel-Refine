from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt
from resources.GenericUILibrary import Button


class QuickBatchDialog(QDialog):
    """
    Custom dialog for creating a new batch with a 'Quick Create' option.
    """

    def __init__(self, default_name="New Batch", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Batch")
        self.setFixedWidth(350)
        self.setStyleSheet(
            """
            QDialog {
                background-color: #FFFFFF;
                border-radius: 8px;
            }
            QLabel {
                font-size: 11pt;
                color: #333333;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #DDDDDD;
                border-radius: 4px;
                font-size: 10pt;
                background-color: #F8F9FA;
            }
            QLineEdit:focus {
                border: 1px solid #2ECC71;
            }
            QCheckBox {
                font-size: 9pt;
                color: #666666;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Batch Name")
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(f"Example: {default_name}")
        self.name_input.setText(default_name)
        self.name_input.selectAll()
        layout.addWidget(self.name_input)

        # Quick Create Checkbox
        self.quick_create_cb = QCheckBox("Quick Create (Don't show this again)")
        layout.addWidget(self.quick_create_cb)

        layout.addSpacerItem(
            QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.cancel_btn = Button("Cancel", variant="secondary")
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = Button("Create", variant="primary")
        self.create_btn.clicked.connect(self.accept)
        self.create_btn.setDefault(True)

        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.create_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        """Return (name, skip_next_time)"""
        name = self.name_input.text().strip()
        return name, self.quick_create_cb.isChecked()
