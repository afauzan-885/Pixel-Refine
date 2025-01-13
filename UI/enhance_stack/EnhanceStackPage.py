from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QVBoxLayout,
)

from UI.enhance_stack.single_page_layout import SinglePageLayout

from .components.top_bar import TopBar
from .logic.database_manager import DatabaseManager


class EnhanceStackPage(QWidget):
    """Main Burst Denoising Page with modular components."""

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.database_manager = DatabaseManager("pixel_refine_database.db")
        self.database_manager.create_database()

        # Add TopBar
        self.top_bar = TopBar()
        self.layout.addWidget(self.top_bar)

        # Initialize SinglePageLayout
        self.single_page_layout = SinglePageLayout()
        self.layout.addLayout(self.single_page_layout.layout)

        # Connect buttons directly to SinglePageLayout methods
        self.top_bar.import_button.clicked.connect(self.single_page_layout.handle_import_button)
        self.top_bar.delete_button.clicked.connect(self.single_page_layout.handle_delete_button)