from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup

from UI.settings.General.Language import language_config

class TopBar(QWidget):
    """Top bar with Import, Switch (centered), and Delete buttons."""
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Gabungan stylesheet untuk tombol switch
        switch_button_style = """
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #95a5a6;
                color: white;
                border: none;
            }
            QPushButton:first-child {
                border-top-left-radius: 10px;
                border-bottom-left-radius: 10px;
            }
            QPushButton:last-child {
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QPushButton:checked {
                background-color: #2ecc71; /* Warna untuk tombol yang dipilih */
            }
        """

        # Import button
        self.import_button = QPushButton(language_config.TOPBAR_IMPORT_BUTTON_TEXT)
        self.import_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        # Switch buttons (Single/Batch)
        self.single_button = QPushButton("Single")
        self.single_button.setCheckable(True)
        self.single_button.setChecked(True)  # Default to "Single"
        self.single_button.setStyleSheet(switch_button_style)

        self.batch_button = QPushButton("Batch")
        self.batch_button.setCheckable(True)
        self.batch_button.setStyleSheet(switch_button_style)

        # Group the buttons to ensure only one is active at a time
        self.switch_group = QButtonGroup(self)
        self.switch_group.addButton(self.single_button)
        self.switch_group.addButton(self.batch_button)

        # Center layout for switch buttons
        self.switch_layout = QHBoxLayout()
        self.switch_layout.setSpacing(0)
        self.switch_layout.setContentsMargins(0, 0, 0, 0) 
        self.switch_layout.addWidget(self.single_button)
        self.switch_layout.addWidget(self.batch_button)

         # Optional: Hide the switch buttons for development purposes
        self.single_button.setVisible(False)  # Menyembunyikan tombol Single
        self.batch_button.setVisible(False)   # Menyembunyikan tombol Batch

        # Delete button
        self.delete_button = QPushButton(language_config.TOPBAR_DELETE_BUTTON_TEXT)
        self.delete_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 14px;
                background-color: #e74c3c;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        # Add widgets to the main layout
        self.layout.addWidget(self.import_button)
        self.layout.addStretch()
        self.layout.addLayout(self.switch_layout)  # Tambahkan switch layout (tetap tersembunyi)
        self.layout.addStretch()
        self.layout.addWidget(self.delete_button)
