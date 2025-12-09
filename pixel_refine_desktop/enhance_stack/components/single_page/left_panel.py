from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QScrollArea,
    QLabel,
    QStackedWidget,
    QProgressBar,
    QGridLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ImageCard,
    EmptyState,
    FormGroup,
    Button,
    Theme,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config

# Backend logic helper
from pixel_refine_desktop.enhance_stack.models.algorithm_list import (
    get_algorithm_descriptions,
    get_algorithm_names,
    get_algorithm_options,
    get_category_display_name,
)

# Thumbnail processor
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
    ThumbnailBatchProcessor,
    create_thumbnail_placeholder,
    display_thumbnail_in_layout,
)

# Zoomable preview
from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable
from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import (
    display_image_in_zoomable,
    ImageLoaderThread,
)
from PySide6.QtWidgets import QGraphicsScene


class LeftPanel(QWidget):
    """
    Main Workspace Panel for Enhance Stack.
    Contains:
    1. Image Grid (Top) - Displays images in the selected batch.
    2. Workflow Settings (Bottom) - Parameter configurations (Alignment, Denoising, etc).
    """

    # Signals
    process_requested = Signal(dict)  # Emit settings dict
    previewImageRequested = Signal(list)  # Emit list of image paths
    imagesDropped = Signal(list)  # Added signal for drag and drop support if needed

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller  # BatchPageController or similar
        self.current_batch_id = None
        self.thumbnail_processor = ThumbnailBatchProcessor(thumbnail_size=(128, 128))
        self.thumbnail_threads = []
        self.image_loader_thread = None
        self._setup_ui()

        # Connect internal signal for view switching
        self.previewImageRequested.connect(lambda _: self.show_preview())

        # Accept drops for image import
        self.setAcceptDrops(True)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # --- 1. Top Section: Image Display (Stacked: Grid vs Preview) ---
        self.display_stack = QStackedWidget()

        # Mode 0: Grid View & Empty State
        self.grid_view_widget = QWidget()
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)

        # Grid Container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        self.grid_container = QWidget()
        self.grid_layout = QHBoxLayout(self.grid_container)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setWidget(self.grid_container)

        # Empty State
        self.empty_state = EmptyState(
            title="No Batch Selected",
            message="Select a batch from the list to view images.",
            button_text="Create New Batch",
        )
        # Note: 'Create New Batch' logic needs to be connected if reachable,
        # or we just rely on RightPanel. For now, button does nothing unless connected.

        self.empty_state.setVisible(True)
        self.scroll_area.setVisible(False)

        grid_view_layout.addWidget(self.empty_state)
        grid_view_layout.addWidget(self.scroll_area)

        self.display_stack.addWidget(self.grid_view_widget)

        # Mode 1: Preview View
        preview_wrapper = QWidget()
        preview_wrapper_layout = QVBoxLayout(preview_wrapper)
        preview_wrapper_layout.setContentsMargins(0, 0, 0, 0)

        # Back Button Header (layout tanpa wrapper widget)
        back_header_layout = QHBoxLayout()
        back_header_layout.setContentsMargins(0, 0, 0, 0)

        back_btn = Button("Back to Grid", variant="secondary")
        back_btn.setFixedWidth(120)
        back_btn.clicked.connect(self.show_grid)
        back_header_layout.addWidget(back_btn)
        back_header_layout.addStretch()

        preview_wrapper_layout.addLayout(back_header_layout)

        # Zoomable Preview View
        self.preview_scene = QGraphicsScene()
        self.zoomable_preview = Zoomable(self.preview_scene, self)
        preview_wrapper_layout.addWidget(self.zoomable_preview)

        self.display_stack.addWidget(preview_wrapper)

        # Add Stack to Main Layout (Flex 1)
        main_layout.addWidget(self.display_stack, 1)

        # --- 2. Bottom Section: Workflow Tabs ---
        self.tabs = QTabWidget()
        self.tabs.setFixedHeight(250)

        # Tab 1: Alignment & Super Resolution
        self.tabs.addTab(self._create_alignment_tab(), "Alignment & Resolution")

        # Tab 2: Denoising
        self.tabs.addTab(self._create_denoising_tab(), "Denoising")

        main_layout.addWidget(self.tabs, 0)  # Fixed height

        # --- 3. Process Section ---
        action_layout = QVBoxLayout()
        action_layout.setSpacing(5)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        action_layout.addWidget(self.progress_bar)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.process_btn = Button("Start Processing", variant="primary")
        self.process_btn.clicked.connect(self._on_process_clicked)
        btn_layout.addWidget(self.process_btn)

        action_layout.addLayout(btn_layout)

        main_layout.addLayout(action_layout)

    def _create_alignment_tab(self):
        """Create Alignment and Super Resolution settings tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        # Group 1: Alignment
        align_names = get_algorithm_names("alignment")

        self.align_form = FormGroup("Alignment Method", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])

        layout.addWidget(self.align_form)
        self.align_select = self.align_form.input

        # Group 2: Super Resolution
        sr_names = get_algorithm_names("super_resolution")

        self.sr_form = FormGroup("Super Resolution", input_type="select")
        self.sr_form.add_options(sr_names)
        if sr_names:
            self.sr_form.set_value(sr_names[0])

        layout.addWidget(self.sr_form)
        self.sr_select = self.sr_form.input

        layout.addStretch()
        return widget

    def _create_denoising_tab(self):
        """Create Denoising settings tab."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.setSpacing(20)

        # Group 1: Denoising
        denoise_names = get_algorithm_names("denoising")

        self.denoise_form = FormGroup("Denoising", input_type="select")
        self.denoise_form.add_options(denoise_names)
        if denoise_names:
            self.denoise_form.set_value(denoise_names[0])

        layout.addWidget(self.denoise_form)
        self.denoise_select = self.denoise_form.input

        layout.addStretch()
        return widget

    def show_grid(self):
        """Switch to Grid View."""
        self.display_stack.setCurrentIndex(0)

    def show_preview(self):
        """Switch to Preview View."""
        self.display_stack.setCurrentIndex(1)

    def load_batch(self, batch_id, images):
        """Load images from a batch into the grid."""
        self.current_batch_id = batch_id

        # Clear existing
        self._clear_grid()
        self.thumbnail_processor.stop_all()

        if not images:
            self.empty_state.set_text("Empty Batch", "This batch has no images yet.")
            self.empty_state.setVisible(True)
            self.scroll_area.setVisible(False)
            return

        self.empty_state.setVisible(False)
        self.scroll_area.setVisible(True)

        # Populate Grid dengan thumbnail asinkron
        for img in images:
            card = ImageCard(card_id=str(img.id), size=120)
            card.image_label.setText(f"Image {img.id}")

            # Store path untuk preview
            card._image_path = img.path
            card.double_clicked.connect(self._on_card_double_clicked)

            self.grid_layout.addWidget(card)

            # Process thumbnail asinkron
            if hasattr(img, 'path') and img.path:
                self._load_thumbnail_async(img.path, card)

    def _load_thumbnail_async(self, image_path, card_widget):
        """Load thumbnail asinkron untuk image card."""
        def on_thumbnail_ready(q_image, path):
            if not q_image.isNull() and card_widget is not None:
                # Convert QImage to QPixmap dan display
                pixmap = QPixmap.fromImage(q_image)
                card_widget.set_image(pixmap)

        self.thumbnail_processor.process_image(image_path, on_thumbnail_ready)

    def _on_card_double_clicked(self, card_id):
        """Handle double-click pada image card untuk preview."""
        sender = self.sender()
        if hasattr(sender, "_image_path"):
            self._display_image_preview(sender._image_path)

    def _display_image_preview(self, image_path):
        """
        Display single image preview di Zoomable view dengan full resolution.
        Support untuk zoom in/out dan pan dengan mouse.
        
        Features:
        - Async load image dari disk
        - Full resolution preview
        - Zoom in/out dengan mouse wheel
        - Pan dengan drag (klik dan geser)
        """
        # Stop previous loader jika masih berjalan
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()

        # Load dan display image di zoomable widget
        self.image_loader_thread = display_image_in_zoomable(
            self.zoomable_preview,
            image_path
        )

        # Show preview view
        self.show_preview()

    def _clear_grid(self):
        """Remove all widgets from grid layout."""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def remove_selected_images(self):
        """Remove currently selected images from logic/view (Placeholder)."""
        # In a real grid, iterate items and remove selected.
        # Here we just clear for safety or need Logic impl
        self._clear_grid()

    def get_select_image_list(self):
        """Get list of selected image paths."""
        # Placeholder: GenericUI ImageCard doesn't have selection state tracking built-in easily exposed potentially
        # Need to implement selection tracking in ImageCard or LeftPanel
        # For now return all or dummy
        return []

    def _on_process_clicked(self):
        """Collect settings and emit signal."""
        settings = {
            "alignment": self.align_select.currentText(),
            "super_resolution": self.sr_select.currentText(),
            "denoising": self.denoise_select.currentText(),
        }
        self.process_requested.emit(settings)

    def load_image_paths(self):
        """Refreshes the grid (used by on_import_complete)."""
        # Logic to fetch latest from DB or similar. Only stub needed if called by single_page_layout
        pass

    # Drag and drop support
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if files:
            self.imagesDropped.emit(files)
