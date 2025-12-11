"""
Display Panel Component - Rewritten dengan pola Panorama.
Handles image grid dan full resolution preview dengan proper drag & drop support.

Adapted from: pixel_refine_desktop/ui/views/panorama/display_area/display_panel.py
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QFileDialog,
    QLabel,
)
from PySide6.QtCore import Slot, Signal, Qt
from PySide6.QtGui import QPixmap

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ImageCard,
    Button,
    Container,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.grids import GridContainer

# Display logic
from pixel_refine_desktop.enhance_stack.core.logic.display_logic import DisplayLogic

# Zoomable preview
from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable
from PySide6.QtWidgets import QGraphicsScene

# Animations
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide

# Config untuk supported image formats
from config import SUPPORTED_FORMATS


class DisplayPanel(QWidget):
    """
    Panel untuk menampilkan Grid images dan Preview.
    Menggunakan QStackedWidget untuk switch antara Grid View dan Preview View.
    Struktur: DisplayPanel (Logic) -> Container (Visual) -> Header + Stack
    """

    # Signals
    images_to_import_selected = Signal(
        list
    )  # Emitted with list of file paths saat drop

    def __init__(self, controller=None):
        super().__init__()

        # Setup Main Layout (Logic container)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Internal Visual Container (Card-like appearance)
        self.display_container = Container(padding=5)

        # Demo customization (Moved to inner container)
        # self.display_container.setAttribute(Qt.WA_StyledBackground, True)
        # self.display_container.setStyleSheet("background-color: #D9D8DA;") -> Removed as per request to clear header color

        self.controller = controller
        self.logic = DisplayLogic()  # Business logic
        self.current_batch_id = None
        self.selected_thumbnails = set()  # Track selected cards
        self.last_selected_card_id = None  # Track untuk range select
        self.all_cards = {}  # Map card_id -> card widget untuk range select

        # Build supported image extensions tuple dari config
        self.supported_extensions = self._build_supported_extensions()

        # Reference ke right panel untuk access create_new_batch
        self.right_panel = None

        # Track current placeholder widget helper
        self.placeholder_widget = None

        self._setup_ui()

        # Accept drops for image import
        self.setAcceptDrops(True)

        # Initialize display state
        self.clear_display()

    def _build_supported_extensions(self):
        """
        Build tuple dari supported image extensions dari config.SUPPORTED_FORMATS.

        Returns:
            tuple: Semua extensions dalam format tuple (e.g., ('.jpg', '.jpeg', '.png', ...))
        """
        extensions = []
        for format_name, ext_list in SUPPORTED_FORMATS.items():
            extensions.extend(ext_list)
        return tuple(extensions)

    def _build_file_filter(self):
        """
        Build file filter string untuk QFileDialog dari config.SUPPORTED_FORMATS.

        Returns:
            str: File filter string (e.g., "Images (*.jpg *.jpeg *.png ...)")
        """
        all_extensions = []
        for format_name, ext_list in SUPPORTED_FORMATS.items():
            all_extensions.extend(ext_list)

        # Create filter string: "Images (*.jpg *.jpeg *.png ...)"
        ext_string = " ".join([f"*{ext}" for ext in all_extensions])
        return f"Images ({ext_string})"

    def _create_placeholder_widget(
        self, html_text="", button_text=None, on_button_click=None
    ):
        """
        Membuat widget placeholder untuk ditampilkan saat grid kosong.
        Mengikuti pattern dari panorama dengan flexible layout.

        Args:
            html_text: Text HTML untuk ditampilkan
            button_text: Text untuk tombol (optional)
            on_button_click: Callback untuk button click (optional)

        Returns:
            QWidget: Container dengan layout stretch + label + button (jika ada)
        """
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Top stretch untuk vertical centering
        layout.addStretch()

        # Text label
        if html_text:
            label = QLabel(html_text)
            label.setTextFormat(Qt.TextFormat.RichText)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet("QLabel { color: #888; font-size: 14px; }")
            layout.addWidget(label)

        # Button (jika ada)
        if button_text and on_button_click:
            btn = Button(button_text, variant="secondary")
            btn.setFixedWidth(120)
            btn.clicked.connect(on_button_click)

            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)

        # Bottom stretch untuk vertical centering
        layout.addStretch()

        return container

    def _setup_ui(self):
        """Setup UI dengan stacked widget untuk grid dan preview mode."""
        self.display_container.main_layout.setContentsMargins(0, 0, 0, 0)
        self.display_container.main_layout.setSpacing(0)

        # === SHARED HEADER ===
        # Header ini berada di luar StackedWidget, sehingga selalu ada di atas.
        # Kita bisa menambah tombol lain di sini di masa depan.
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 10)
        self.header_layout.setSpacing(5)

        # Title Label (Optional, for context) or Spacer
        self.header_title = QLabel("")
        self.header_title.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #333;"
        )
        self.header_layout.addWidget(self.header_title)

        self.header_layout.addStretch()

        # Tools/Actions Area

        # 1. Back to Grid Button (Visible only in Preview)
        self.back_btn = Button("Back to Grid", variant="secondary")
        self.back_btn.setFixedWidth(120)
        self.back_btn.clicked.connect(self.show_grid)
        self.back_btn.setVisible(False)  # Hidden by default
        self.header_layout.addWidget(self.back_btn)

        # 2. Import Images Button (Visible in Grid)
        self.import_button = Button("Import Images", variant="secondary")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_images)
        self.import_button.setVisible(False)  # Hidden by default (controlled by logic)
        self.header_layout.addWidget(self.import_button)

        self.display_container.add_layout(self.header_layout)

        # =====================================================================
        # === CONTENT STACK ===
        # =====================================================================

        # Stacked Widget: Index 0 = Grid View, Index 1 = Preview View
        self.display_stack = QStackedWidget()

        # Apply Card styling to the content stack ONLY, so header remains clean
        self.display_stack.setAttribute(Qt.WA_StyledBackground, True)
        # Optional: Add padding/radius if needed to look like a card inside the panel
        self.display_stack.setStyleSheet(
            "background-color: #D9D8DA; border-radius: 8px;"
        )

        # --- INDEX 0: GRID VIEW ---
        self.grid_view_widget = QWidget()
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)
        grid_view_layout.setSpacing(10)
        # Note: Local header removed.

        # Content Stack: GridContainer vs Placeholder
        self.grid_content_stack = QStackedWidget()
        # Animator for grid content stack
        self.grid_animator = StackedWidgetAnimator(self.grid_content_stack)

        grid_view_layout.addWidget(self.grid_content_stack, 1)

        # GridContainer dengan responsive columns
        self.grid_container = GridContainer(
            item_width=100, spacing=10, wrap_mode="vertical", column_mode="responsive"
        )
        self.grid_container.setStyleSheet("QScrollArea { border: none; }")
        self.grid_content_stack.addWidget(self.grid_container)

        self.display_stack.addWidget(self.grid_view_widget)

        # --- INDEX 1: PREVIEW VIEW ---
        preview_wrapper = QWidget()
        preview_wrapper_layout = QVBoxLayout(preview_wrapper)
        preview_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        preview_wrapper_layout.setSpacing(10)
        # Note: Local header removed.

        # Zoomable Preview View
        self.preview_scene = QGraphicsScene()
        self.zoomable_preview = Zoomable(self.preview_scene, self)
        preview_wrapper_layout.addWidget(self.zoomable_preview)

        self.display_stack.addWidget(preview_wrapper)

        # Add Stack to Main Layout (via Container)
        self.display_container.add_widget(self.display_stack)

        # Add Container to Main Widget Layout
        self.main_layout.addWidget(self.display_container)

    def _set_placeholder(self, widget):
        """
        Set placeholder widget in stack.
        Safely removes previous placeholder if exists.

        Args:
            widget: Generic widget/container to show
        """
        # Remove old placeholder if exists and is different from new widget
        if self.placeholder_widget and self.placeholder_widget != widget:
            try:
                self.grid_content_stack.removeWidget(self.placeholder_widget)
                self.placeholder_widget.deleteLater()
            except RuntimeError:
                pass  # Widget already deleted
            self.placeholder_widget = None

        # Add and show new placeholder
        if widget:
            self.placeholder_widget = widget
            self.grid_content_stack.addWidget(widget)
            # Slide UP for showing placeholder (contextual: usually happens on clear or load empty)
            # Or use FADE if slide feels weird. But user asked for slide.
            # Logic: If coming from content -> Placeholder: Slide DOWN (Emptying)
            # If coming from another placeholder -> Placeholder: Slide LEFT/RIGHT?
            # Let's assume Grid -> Placeholder = Slide DOWN (Content leaves)
            slide(
                self.grid_animator,
                self.grid_content_stack,
                widget,
                SlideDirection.DOWN,
                duration=300,
            )
        else:
            # If default none, show grid
            # Placeholder -> Grid = Slide UP (Content arrives)
            slide(
                self.grid_animator,
                self.grid_content_stack,
                self.grid_container,
                SlideDirection.UP,
                duration=300,
            )

    # =========================================================================
    # === 1. PUBLIC SLOTS UNTUK MEMUAT DATA ===
    # =========================================================================

    @Slot(int, list)
    def load_batch(self, batch_id, images):
        """
        Load batch images ke grid.

        Args:
            batch_id: ID dari batch
            images: List of image objects dengan .id dan .path attributes
        """
        self.current_batch_id = batch_id
        self.logic.set_batch(batch_id, images)

        # Update Header Title
        self.header_title.setText(f"Batch: {batch_id}")
        self._clear_grid()
        self.logic.get_thumbnail_processor().stop_all()
        self.selected_thumbnails.clear()
        self.all_cards.clear()
        self.last_selected_card_id = None

        # Check if batch is empty
        if self.logic.is_batch_empty():
            # Show empty state but keep import button visible in header
            self.import_button.setVisible(True)
            self._show_empty_batch_state()
            self.show_grid()
            return

        # Show import button saat batch ada images
        self.import_button.setVisible(True)

        # Switch back to grid container using animation helper
        if self.grid_content_stack.currentWidget() != self.grid_container:
            self._set_placeholder(None)

        # Populate Grid dengan thumbnail asinkron
        for img in self.logic.current_images:
            if not hasattr(img, "id") or not hasattr(img, "path"):
                continue

            card = ImageCard(card_id=str(img.id), size=100)
            card.image_label.setText(f"Image {img.id}")
            card._image_path = img.path
            card.double_clicked.connect(self._on_card_double_clicked)
            card.clicked.connect(
                lambda cid, event, c=card: self._on_card_clicked(cid, event, c)
            )

            self.grid_container.add_item(card)
            self.all_cards[str(img.id)] = card  # Store reference untuk range select
            self.logic.register_grid_item(str(img.id), {"path": img.path})
            self._load_thumbnail_async(img.path, card)

        self.show_grid()

    @Slot()
    def clear_display(self):
        """
        Clear display ketika tidak ada batch yang dipilih.
        Reset ke state default dengan placeholder widget dan tombol "New Batch".
        """
        self.current_batch_id = None
        self.header_title.setText("")  # Clear header title
        self.logic.clear_all()
        self._clear_grid()
        self.selected_thumbnails.clear()
        self.all_cards.clear()
        self.last_selected_card_id = None

        # Hide import button saat no batch selected
        self.import_button.setVisible(False)

        # Create placeholder dengan "New Batch" button
        placeholder_html = "<p>Create a new batch to get started.</p>"
        placeholder = self._create_placeholder_widget(
            html_text=placeholder_html,
            button_text="New Batch",
            on_button_click=self._create_new_batch,
        )
        self._set_placeholder(placeholder)

        if self.preview_scene:
            self.preview_scene.clear()

        self.show_grid()

    def _show_empty_batch_state(self):
        """
        Show empty state ketika batch dipilih tapi belum ada images.
        Display pesan informatif + tombol untuk import images langsung.
        """
        # Create placeholder dengan "Browse Images" button
        placeholder_html = "<p>Drag and drop images ke sini,<br>atau gunakan tombol di atas untuk memilih dari folder.</p>"
        placeholder = self._create_placeholder_widget(html_text=placeholder_html)
        self._set_placeholder(placeholder)

    def _create_new_batch(self):
        """
        Call _create_new_batch dari right_panel untuk create batch baru.
        Right panel akan handle dialog input dan emit signal.
        """
        if self.right_panel:
            self.right_panel._create_new_batch()

    # =========================================================================
    # === 2. PUBLIC METHODS UNTUK VIEW CONTROL ===
    # =========================================================================

    def show_grid(self):
        """Switch ke Grid View."""
        self.display_stack.setCurrentIndex(0)

        # Update Header buttons
        self.back_btn.setVisible(False)

        if self.current_batch_id:
            self.import_button.setVisible(True)
        else:
            self.import_button.setVisible(False)

    def show_preview(self):
        """Switch ke Preview View."""
        self.display_stack.setCurrentIndex(1)

        # Update Header buttons
        self.back_btn.setVisible(True)
        self.import_button.setVisible(False)

    # =========================================================================
    # === 3. PRIVATE METHODS - GRID MANAGEMENT ===
    # =========================================================================

    def _clear_grid(self):
        """Remove all widgets from grid container."""
        self.grid_container.clear_items()

    def _clear_selection(self):
        """Deselect semua cards."""
        for card_id in list(self.selected_thumbnails):
            if card_id in self.all_cards:
                self.all_cards[card_id].deselect()
        self.selected_thumbnails.clear()

    def _select_range(self, start_card_id, end_card_id):
        """
        Select range antara dua cards.

        Args:
            start_card_id: ID card awal range
            end_card_id: ID card akhir range
        """
        # Get urutan dari grid untuk determine range
        card_ids_in_order = list(self.all_cards.keys())

        try:
            start_idx = card_ids_in_order.index(start_card_id)
            end_idx = card_ids_in_order.index(end_card_id)
        except ValueError:
            return  # Invalid IDs

        # Normalize indices untuk ascending order
        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        # Select semua cards dalam range
        for i in range(start_idx, end_idx + 1):
            card_id = card_ids_in_order[i]
            if card_id in self.all_cards:
                self.all_cards[card_id].select()
                self.selected_thumbnails.add(card_id)

    def _load_thumbnail_async(self, image_path, card_widget):
        """
        Load thumbnail asinkron untuk image card.

        Args:
            image_path: Path ke image file
            card_widget: ImageCard widget untuk display thumbnail
        """

        def on_thumbnail_ready(q_image, path):
            if card_widget is not None and not q_image.isNull():
                pixmap = QPixmap.fromImage(q_image)
                card_widget.set_image(pixmap)

        self.logic.load_thumbnail_async(image_path, on_thumbnail_ready)

    def _on_card_clicked(self, card_id, event, card_widget):
        """
        Handle click pada image card untuk selection dengan multi-select support.

        - Single Click: Toggle selection single item
        - Ctrl + Click: Add/remove individual item (multi-select)
        - Shift + Click: Select range dari last selected ke current

        Args:
            card_id: ID dari card
            event: QMouseEvent dari click
            card_widget: Card widget reference
        """
        modifiers = event.modifiers()

        # Single Click - Toggle single item (clear others)
        if modifiers == Qt.NoModifier:
            self._clear_selection()
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            self.last_selected_card_id = card_id

        # Ctrl + Click - Add/Remove item (multi-select)
        elif modifiers == Qt.ControlModifier:
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            else:
                self.selected_thumbnails.discard(card_id)
            self.last_selected_card_id = card_id

        # Shift + Click - Select range (multi-select range)
        elif modifiers == Qt.ShiftModifier:
            if self.last_selected_card_id and self.last_selected_card_id != card_id:
                self._select_range(self.last_selected_card_id, card_id)
            else:
                # Jika belum ada last_selected, treat seperti single click
                self._clear_selection()
                card_widget.select()
                self.selected_thumbnails.add(card_id)
                self.last_selected_card_id = card_id

    def _on_card_double_clicked(self, card_id):
        """
        Handle double-click pada image card untuk preview full resolution.

        Args:
            card_id: ID dari card yang di-click
        """
        sender = self.sender()
        if hasattr(sender, "_image_path"):
            self._display_image_preview(sender._image_path)

    def _display_image_preview(self, image_path):
        """
        Display single image preview di Zoomable view dengan full resolution.

        Args:
            image_path: Path ke image file untuk di-preview
        """
        if not self.logic.prepare_preview(image_path):
            return

        self.logic.display_preview(self.zoomable_preview, image_path)
        self.show_preview()

    # =========================================================================
    # === 4. PUBLIC HELPER METHODS ===
    # =========================================================================

    def remove_selected_images(self):
        """Remove currently selected images dari grid."""
        if self.selected_thumbnails:
            for card_id in list(self.selected_thumbnails):
                # Remove dari logic
                self.logic.unregister_grid_item(card_id)
            self.selected_thumbnails.clear()
            # Reload batch untuk refresh grid
            if self.current_batch_id and self.logic.current_images:
                self.load_batch(self.current_batch_id, self.logic.current_images)

    def get_selected_image_list(self):
        """Get list of selected image paths."""
        return [
            self.logic.grid_items[cid]["path"]
            for cid in self.selected_thumbnails
            if cid in self.logic.grid_items
        ]

    # =========================================================================
    # === 5. DRAG & DROP SUPPORT (Pola dari Panorama) ===
    # =========================================================================

    def dragEnterEvent(self, event):
        """Accept drag enter event jika ada image files dalam supported formats."""
        if not self.current_batch_id:
            event.ignore()
            return

        if event.mimeData().hasUrls():
            # Validate bahwa ada image files dalam supported formats
            has_images = any(
                url.toLocalFile().lower().endswith(self.supported_extensions)
                for url in event.mimeData().urls()
                if url.isLocalFile()
            )
            if has_images:
                event.acceptProposedAction()
                self.setStyleSheet(self.styleSheet() + "; border: 2px dashed #4CAF50;")
            else:
                event.ignore()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Reset style saat drag leave."""
        self.setStyleSheet(
            self.styleSheet().replace("; border: 2px dashed #4CAF50;", "")
        )
        event.accept()

    def dropEvent(self, event):
        """
        Handle drop event untuk image import.
        Emit signal dengan file paths untuk parent widget.
        """
        if not self.current_batch_id:
            event.ignore()
            return

        self.setStyleSheet(
            self.styleSheet().replace("; border: 2px dashed #4CAF50;", "")
        )

        if event.mimeData().hasUrls():
            # Filter valid image files dalam supported formats
            valid_files = [
                url.toLocalFile()
                for url in event.mimeData().urls()
                if url.isLocalFile()
                and url.toLocalFile().lower().endswith(self.supported_extensions)
            ]
            if valid_files:
                # Emit signal untuk parent widget handle
                self.images_to_import_selected.emit(valid_files)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

    @Slot()
    def import_images(self):
        """
        Membuka dialog file untuk impor gambar dengan format dari config.SUPPORTED_FORMATS.
        Mirip dengan panorama page import_images method.
        """
        if not self.current_batch_id:
            return

        # Build file filter string dari supported formats
        file_filter = self._build_file_filter()

        # Open file dialog untuk select multiple images
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", file_filter)

        if paths:
            # Emit signal dengan selected file paths
            self.images_to_import_selected.emit(paths)
