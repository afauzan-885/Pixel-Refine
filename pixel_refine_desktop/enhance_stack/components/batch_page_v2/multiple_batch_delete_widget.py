from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt

class MultipleBatchDeleteWidget(QWidget):
    """
    Widget to confirm deletion of multiple batches.
    Emits signals for yes/no actions.
    """
    yes_clicked = Signal()
    no_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        main_layout.addWidget(self.message_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.yes_button = QPushButton("Ya, Hapus")
        self.yes_button.clicked.connect(self.yes_clicked)
        button_layout.addWidget(self.yes_button)

        self.no_button = QPushButton("Tidak, Batalkan")
        self.no_button.clicked.connect(self.no_clicked)
        button_layout.addWidget(self.no_button)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def set_batch_info(self, batch_names: list):
        """
        Sets the information about the batches to be deleted.

        Args:
            batch_names: A list of names of the batches selected for deletion.
        """
        count = len(batch_names)
        names_html = "<br>".join(f"- {name}" for name in batch_names)
        message = (
            f"<b>Batch Terpilih [{count}]</b><br><br>"
            f"{names_html}<br><br>"
            "Apakah Anda ingin menghapus batch tersebut?"
        )
        self.message_label.setText(message)
