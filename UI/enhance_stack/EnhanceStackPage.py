from PyQt6.QtWidgets import QVBoxLayout, QWidget, QStackedWidget

from UI.enhance_stack.batch_page_layout import BatchPageLayout
from UI.enhance_stack.components.batch_page_layout.combined_panel import CombinedPanel
from UI.enhance_stack.single_page_layout import SinglePageLayout

from .components.top_bar import TopBar
from .logic.database_manager import DatabaseManager

class EnhanceStackPage(QWidget):
    """Main Burst Denoising Page with modular components."""

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.database_manager = database_manager
        # Tambahkan daftar untuk menyimpan thread ThumbnailLoader
        self.thumbnail_threads = []

        self.top_bar = TopBar()
        self.layout.addWidget(self.top_bar)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.single_page_layout = SinglePageLayout(self.database_manager)
        self.batch_page_layout = BatchPageLayout()
        self.combined_panel_logic = CombinedPanel(self.database_manager)

        self.stacked_widget.addWidget(self.single_page_layout)
        self.stacked_widget.addWidget(self.batch_page_layout)

        self.stacked_widget.setCurrentWidget(self.single_page_layout)

        # Set awal, tampilkan Single Page, sembunyikan Batch Page UI
        self.top_bar.single_page_import_button.setVisible(True)
        self.top_bar.single_page_delete_button.setVisible(True)

        for widget in [self.top_bar.batch_page_import_button, self.top_bar.batch_page_delete_button,
                       self.top_bar.start_process_batch]:
            widget.setVisible(False)

        # Connect tombol switch
        self.top_bar.single_button.toggled.connect(self.switch_page)
        self.top_bar.batch_button.toggled.connect(self.switch_page)

        # Connect tombol Single Page
        self.top_bar.single_page_import_button.clicked.connect(self.single_page_layout.handle_import_button)
        self.top_bar.single_page_delete_button.clicked.connect(self.single_page_layout.handle_delete_button)

        # Connect tombol Batch Page
        self.top_bar.batch_page_import_button.clicked.connect(self.batch_page_layout.handle_batch_import_button)
        self.top_bar.batch_page_delete_button.clicked.connect(self.batch_page_layout.handle_delete_all_batches)
        self.top_bar.start_process_batch.clicked.connect(self.batch_page_layout.process_all_batches)
        
    def switch_page(self):
        """Switch halaman berdasarkan tombol yang dipilih."""
        if self.top_bar.single_button.isChecked():
            self.stacked_widget.setCurrentWidget(self.single_page_layout)

            # Tampilkan tombol import dan delete di mode Single
            self.top_bar.single_page_import_button.setVisible(True)
            self.top_bar.single_page_delete_button.setVisible(True)

            # Sembunyikan tombol import dan delete di mode Batch
            for widget in [self.top_bar.batch_page_import_button, self.top_bar.batch_page_delete_button,
                        self.top_bar.start_process_batch]:
                widget.setVisible(False)
        else:
            self.stacked_widget.setCurrentWidget(self.batch_page_layout)

            # Sembunyikan tombol import dan delete di mode Single
            self.top_bar.single_page_import_button.setVisible(False)
            self.top_bar.single_page_delete_button.setVisible(False)

            for widget in [self.top_bar.batch_page_import_button, self.top_bar.batch_page_delete_button,
                       self.top_bar.start_process_batch]:
                widget.setVisible(True)
