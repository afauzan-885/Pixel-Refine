from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup

from UI.resources.stylesheet import stylesheet
from UI.settings.General.Language import language_config

class TopBar(QWidget):
    """Top bar with Import, Switch (centered), and Delete buttons."""
    def __init__(self):
        super().__init__()
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Import button (Single Page Layout)
        self.single_page_import_button = QPushButton(language_config.TOPBAR_SINGLE_IMPORT_BUTTON_TEXT)
        self.batch_page_import_button = QPushButton(language_config.TOPBAR_BATCH_IMPORT_BUTTON_TEXT)
        self.single_page_import_button.setStyleSheet(stylesheet.IMPORT_BUTTON)
        self.batch_page_import_button.setStyleSheet(stylesheet.IMPORT_BUTTON)

        # Switch buttons (Single/Batch)
        self.single_button = QPushButton("Single")
        self.single_button.setCheckable(True)
        self.single_button.setChecked(True)
        self.single_button.setStyleSheet(stylesheet.SWITCH_BUTTON)

        self.batch_button = QPushButton("Batch")
        self.batch_button.setCheckable(True)
        self.batch_button.setStyleSheet(stylesheet.SWITCH_BUTTON)

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

        # Hide the switch buttons for development purposes
        self.single_button.setVisible(True)
        self.batch_button.setVisible(True) 

        # Delete button
        self.single_page_delete_button = QPushButton(language_config.TOPBAR_SINGLE_DELETE_BUTTON_TEXT)
        self.batch_page_delete_button = QPushButton(language_config.TOPBAR_BATCH_DELETE_BUTTON_TEXT)
        self.single_page_delete_button.setStyleSheet(stylesheet.DELETE_BUTTON)
        self.batch_page_delete_button.setStyleSheet(stylesheet.DELETE_BUTTON)

        # Add widgets to the main layout
        self.layout.addWidget(self.single_page_import_button)
        self.layout.addWidget(self.batch_page_import_button)
        self.layout.addStretch()
        self.layout.addLayout(self.switch_layout)  # Tambahkan switch layout (tetap tersembunyi)
        self.layout.addStretch()
        self.layout.addWidget(self.single_page_delete_button)
        self.layout.addWidget(self.batch_page_delete_button)
