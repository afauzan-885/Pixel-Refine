from PyQt6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget

from UI.enhance_stack.batch_page_layout import BatchPageLayout
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

        # Gunakan QStackedWidget untuk switch antara halaman Single & Batch
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        # Tambahkan SinglePageLayout dan BatchPageLayout ke dalam stacked_widget
        self.single_page_layout = SinglePageLayout()
        self.batch_page_layout = BatchPageLayout()

        self.stacked_widget.addWidget(self.single_page_layout)
        self.stacked_widget.addWidget(self.batch_page_layout)

        # Set tampilan awal ke SinglePageLayout
        self.stacked_widget.setCurrentWidget(self.single_page_layout)

        # **Atur visibilitas tombol secara default**
        self.top_bar.single_page_import_button.setVisible(True)
        self.top_bar.single_page_delete_button.setVisible(True)
        self.top_bar.batch_page_import_button.setVisible(False)
        self.top_bar.batch_page_delete_button.setVisible(False)

        # Connect tombol switch dari TopBar ke metode switch_page
        self.top_bar.single_button.toggled.connect(self.switch_page)
        self.top_bar.batch_button.toggled.connect(self.switch_page)

        # Connect buttons directly to SinglePageLayout methods
        self.top_bar.single_page_import_button.clicked.connect(self.single_page_layout.handle_import_button)
        self.top_bar.single_page_delete_button.clicked.connect(self.single_page_layout.handle_delete_button)
        
        self.top_bar.batch_page_import_button.clicked.connect(self.batch_page_layout.handle_import_button)

    def switch_page(self):
        """Switch halaman berdasarkan tombol yang dipilih."""
        if self.top_bar.single_button.isChecked():
            self.stacked_widget.setCurrentWidget(self.single_page_layout)

            # Tampilkan tombol import dan delete di mode Single
            self.top_bar.single_page_import_button.setVisible(True)
            self.top_bar.single_page_delete_button.setVisible(True)

            # Sembunyikan tombol import dan delete di mode Batch
            self.top_bar.batch_page_import_button.setVisible(False)
            self.top_bar.batch_page_delete_button.setVisible(False)
        else:
            self.stacked_widget.setCurrentWidget(self.batch_page_layout)

            # Sembunyikan tombol import dan delete di mode Single
            self.top_bar.single_page_import_button.setVisible(False)
            self.top_bar.single_page_delete_button.setVisible(False)

            # Tampilkan tombol import dan delete di mode Batch
            self.top_bar.batch_page_import_button.setVisible(True)
            self.top_bar.batch_page_delete_button.setVisible(True)
