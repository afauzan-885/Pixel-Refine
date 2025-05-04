from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QStackedWidget,
                              ) 
from UI.enhance_stack.batch_page_layout import BatchPageLayout
from UI.enhance_stack.single_page_layout import SinglePageLayout
from UI.resources.animation.animation_manager import SlideDirection, StackedWidgetAnimator
from UI.resources.animation.slide import slide
from UI.resources.animation.toast.toast_manager import ToastManager
from .components.top_bar import TopBar
from .logic.database_manager import DatabaseManager

class EnhanceStackPage(QWidget):
    """Halaman utama dengan efek transisi fade antar sub-halaman dan TopBar."""

    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.layout = QVBoxLayout(self)
        
        self.animator = StackedWidgetAnimator(self)
        self.toast_manager = ToastManager(self)

        self.top_bar = TopBar()
        self.layout.addWidget(self.top_bar)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget, 1)

        self.single_page_layout = SinglePageLayout(self.database_manager)
        self.batch_page_layout = BatchPageLayout()

        self.stacked_widget.addWidget(self.single_page_layout)
        self.stacked_widget.addWidget(self.batch_page_layout)
        self.stacked_widget.setCurrentWidget(self.single_page_layout)

        # --- Koneksi Sinyal ---
        self.top_bar.single_button.toggled.connect(self._handle_switch_request)
        self.top_bar.batch_button.toggled.connect(self._handle_switch_request)
        self.batch_page_layout.show_toast_requested.connect(self.toast_manager.show)
        
        self.top_bar.single_page_import_button.clicked.connect(self.single_page_layout.handle_import_button)
        self.top_bar.single_page_delete_button.clicked.connect(self.single_page_layout.handle_delete_button)
        self.top_bar.batch_page_import_button.clicked.connect(self.batch_page_layout.handle_batch_import_button)
        self.top_bar.batch_page_delete_button.clicked.connect(self.batch_page_layout.handle_delete_all_batches)
        self.top_bar.start_process_batch.clicked.connect(self.batch_page_layout.process_all_batches)
      
        self.top_bar.left_stack.setCurrentIndex(0)
        self.top_bar.right_stack.setCurrentIndex(0)


    def _handle_switch_request(self):
        """Dipanggil ketika tombol Single/Batch ditekan."""
        if self.top_bar.single_button.isChecked():
            target_main_widget = self.single_page_layout
            target_topbar_index = 0
            main_slide_direction = SlideDirection.RIGHT
        elif self.top_bar.batch_button.isChecked():
            target_main_widget = self.batch_page_layout
            target_topbar_index = 1
            main_slide_direction = SlideDirection.LEFT
        else:
            return

        slide(self.animator, self.stacked_widget, target_main_widget, main_slide_direction, duration=400)
        self.top_bar.left_stack.setCurrentIndex(target_topbar_index)
        self.top_bar.right_stack.setCurrentIndex(target_topbar_index)
