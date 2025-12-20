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
    QComboBox,
    QGraphicsScene,
)
from PySide6.QtCore import Slot, Signal, Qt, QPoint, QSize
from PySide6.QtGui import QPixmap, QColor
import os

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ImageCard,
    Button,
    IconButton,
    Container,
    OverlayContainer,
    OverlayPosition,
    ImageCompareItem,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.grids import GridContainer
from pixel_refine_desktop.ui.resources.GenericUILibrary.forms import FormGroup
from pixel_refine_desktop.ui.components.common.sidebar import Sidebar

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

# Import the new widget
from .multiple_batch_delete_widget import MultipleBatchDeleteWidget


class DisplayPanel(QWidget):
    """
    Panel untuk menampilkan Grid images dan Preview.
    Menggunakan QStackedWidget untuk switch antara Grid View dan Preview View.
    Struktur: DisplayPanel (Logic) -> QStackedLayout (Overlay support)
              -> Layer 0: Content Widget -> Container -> Header + Stack
              -> Layer 1: Overlay Widget -> Floating Progress Bar
              -> Layer 2: Sidebar Overlay
    """

    # Signals
    images_to_import_selected = Signal(list)
    page_changed = Signal(int)  # For global navigation

    def __init__(self, controller=None):
        super().__init__()

        # Setup Main Layout (Logic container)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 8, 0, 5)

        # Internal Visual Container (Card-like appearance)
        self.display_container = Container(padding=5)
        # White base layer - will show through transparent display_stack
        self.display_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True
        )
        self.display_container.setObjectName("DisplayContainerBase")
        self.display_container.setStyleSheet(
            """
            #DisplayContainerBase {
                background-color: #FFFFFF;
            }
        """
        )

        self.controller = controller
        self.logic = DisplayLogic()
        self.current_batch_id = None
        self.current_batch_name = None
        self.selected_thumbnails = set()
        self.last_selected_card_id = None
        self.all_cards = {}

        self.supported_extensions = self._build_supported_extensions()
        self.right_panel = None
        self.placeholder_widget = None

        self._setup_ui()
        self._setup_sidebar()  # New Sidebar Integration

        self.setAcceptDrops(True)
        self.clear_display()

    def _setup_ui(self):
        """Setup UI dengan stacked widget untuk grid dan preview mode."""
        self.display_container.main_layout.setContentsMargins(0, 0, 0, 0)
        self.display_container.main_layout.setSpacing(0)

        # === SHARED HEADER ===
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 5, 10, 0)
        self.header_layout.setSpacing(10)

        # 0. Sidebar Toggle Button (New)
        self.toggle_btn = Button("☰", variant="ghost")  # Minimalist style
        self.toggle_btn.setFixedWidth(40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.header_layout.addWidget(self.toggle_btn)

        # Title Label
        self.header_title = QLabel("")
        self.header_title.setStyleSheet(
            "font-weight: bold; font-size: 16px; color: #333; padding: 5px;"
        )
        self.header_layout.addWidget(self.header_title)
        self.header_layout.addStretch()

        # Tools/Actions Area

        # 0. Result Dropdown (Direct QComboBox for correct alignment)
        self.result_selector = QComboBox()
        self.result_selector.setFixedWidth(100)
        # Customize styling for white dropdown
        self.result_selector.setStyleSheet(
            """
            QComboBox {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px 8px;
                color: #333333;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666666;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #333333;
                selection-background-color: #E0E0E0;
                selection-color: #000000;
            }
        """
        )
        self.result_selector.currentTextChanged.connect(self._on_result_changed)
        self.result_selector.setVisible(False)
        self.header_layout.addWidget(self.result_selector)

        # 1. Back to Grid Button
        self.back_btn = Button("Back to Grid", variant="secondary")
        self.back_btn.setFixedWidth(120)
        self.back_btn.clicked.connect(self.show_grid)
        self.back_btn.setVisible(False)
        self.header_layout.addWidget(self.back_btn)

        # 2. Preview Process Button (Shortcut from Grid)
        self.preview_process_btn = IconButton(
            icon_path="pixel_refine_desktop/ui/resources/assets/icons/play-preview.png",
            variant="primary",
        )
        self.preview_process_btn.setToolTip("Image Process")
        self.preview_process_btn.setFixedWidth(40)
        self.preview_process_btn.clicked.connect(self._on_preview_process_clicked)
        self.preview_process_btn.setVisible(False)
        self.header_layout.addWidget(self.preview_process_btn)

        # 3. Import Images Button
        self.import_button = Button("Import Images", variant="secondary")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_images)
        self.import_button.setVisible(False)
        self.header_layout.addWidget(self.import_button)

        self.display_container.add_layout(self.header_layout)

        # =====================================================================
        # === CONTENT STACK ===
        # =====================================================================

        # Stacked Widget: Index 0 = Grid View, Index 1 = Preview View
        self.display_stack = QStackedWidget()

        self.display_stack.setContentsMargins(
            10, 10, 10, 10
        )  # Margin for the white border effect
        self.display_stack.setStyleSheet(
            "background-color: transparent; border-radius: 2px;"
        )

        # --- INDEX 0: GRID VIEW ---
        self.grid_view_widget = QWidget()
        # Inner content gets a slightly darker background to make the white border visible
        self.grid_view_widget.setStyleSheet(
            "background-color: #F0F0F0; border-radius: 4px;"
        )
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(
            0, 0, 0, 0
        )  # 10px margin for transparent background
        grid_view_layout.setSpacing(0)
        # Note: Local header removed.

        # Content Stack: GridContainer vs Placeholder
        self.grid_content_stack = QStackedWidget()
        # Animator for grid content stack
        self.grid_animator = StackedWidgetAnimator(self.grid_content_stack)

        grid_view_layout.addWidget(self.grid_content_stack, 1)

        # GridContainer dengan responsive columns
        self.grid_container = GridContainer(
            item_width=100, spacing=5, wrap_mode="vertical", column_mode="responsive"
        )
        self.grid_container.setStyleSheet("QScrollArea { border: none; }")
        self.grid_content_stack.addWidget(self.grid_container)

        self.display_stack.addWidget(self.grid_view_widget)

        # --- INDEX 1: PREVIEW VIEW ---
        preview_wrapper = QWidget()
        preview_wrapper_layout = QVBoxLayout(preview_wrapper)
        preview_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        preview_wrapper_layout.setSpacing(10)

        # Zoomable Preview View (Directly added, no more stack or controls)
        self.preview_scene = QGraphicsScene()
        self.zoomable_preview = Zoomable(self.preview_scene, self)
        preview_wrapper_layout.addWidget(self.zoomable_preview)

        # Connect scroll/zoom to update (Force redraw for sticky labels in Comparison mode)
        # This is safe to connect once here because the scene persists.
        self.zoomable_preview.horizontalScrollBar().valueChanged.connect(
            self.preview_scene.update
        )
        self.zoomable_preview.verticalScrollBar().valueChanged.connect(
            self.preview_scene.update
        )

        self.display_stack.addWidget(preview_wrapper)

        # --- FLOATING SAVE BUTTON (For Processed Results) ---
        self.save_overlay = OverlayContainer(
            parent=preview_wrapper,
            position=OverlayPosition.BOTTOM_RIGHT,
            margin=0,
            shadow_enabled=True,
        )
        # 1. Inisialisasi seperti biasa
        self.save_btn = IconButton(
            text="",
            icon_path="pixel_refine_desktop/ui/resources/assets/icons/image-save.png",
            variant="secondary",
            text_tooltip="Saving",
            square_size=35,
        )

        # 2. PAKSA gaya via Stylesheet (Menghilangkan background & Memperbaiki Tooltip)
        self.save_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent !important;
                border: none !important;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 10) !important; /* Efek hover halus */
                border-radius: 4px;
            }
            QToolTip {
                background-color: #FFF9C4; /* Kuning Kertas */
                color: #202020;            /* Warna teks hitam agar terlihat */
                border: 1px solid #D4C489;
                padding: 2px;
                border-radius: 3px;
                font-family: sans-serif;
            }
        """
        )

        # 3. Pastikan ukuran icon pas di tengah kotak 35px
        self.save_btn.setIconSize(QSize(24, 24))

        # Lanjutkan sisa kodenya
        self.save_btn.clicked.connect(self._on_save_clicked)
        self.save_overlay.set_content(self.save_btn)
        self.save_overlay.hide()

        # --- INDEX 2: MULTIPLE BATCH DELETE CONFIRMATION ---
        self._setup_delete_confirmation_widget()

        # Add Stack to Main Layout (via Container)
        self.display_container.add_widget(self.display_stack)

        # Add Container to Main Widget Layout
        self.main_layout.addWidget(self.display_container)

    def _setup_sidebar(self):
        """Initialize Floating Sidebar."""
        pages = [
            (
                "Enhance Stack",
                "pixel_refine_desktop/ui/resources/assets/icons/enhance_stack.png",
            ),
            # ("Panorama", "pixel_refine_desktop/ui/resources/assets/icons/panorama.png"), # Removed
            ("Settings", "pixel_refine_desktop/ui/resources/assets/icons/setting.png"),
        ]

        # Create Sidebar
        # Parent must be self (DisplayPanel) to float relative to it
        self.sidebar = Sidebar(pages=pages, parent=self)
        self.sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.sidebar.page_changed.connect(
            self._handle_sidebar_navigation
        )  # custom handler

        self.sidebar_overlay = OverlayContainer(
            parent=self.display_container,  # Anchor to the container logic
            position=OverlayPosition.TOP_LEFT,
            margin=5,
            smart_positioning=False,  # We want it consistently on left
            close_on_click_outside=True,
            # Sidebar Visuals: Shadow Only (45 deg)
            shadow_enabled=True,
            shadow_blur_radius=20,
            shadow_offset=QPoint(4, 4),  # 45 degrees approx (positive X, positive Y)
            shadow_color=QColor(0, 0, 0, 80),
        )
        self.sidebar_overlay.set_content(self.sidebar)

        # Setup Settings Overlay
        self._setup_settings_overlay()

        # Hidden by default
        self.sidebar_overlay.hide()

        # Set default active page (Enhance Stack)
        self.sidebar.set_current_page(0)

    def _setup_settings_overlay(self):
        """Setup independent overlay for Settings View."""
        from pixel_refine_desktop.ui.views.settings.views.settings_view import (
            SettingsView,
        )

        # Create container centered
        # Settings Visuals: Shadow 270 deg (Down), Blur 35%, Dim 25%
        # Blur radius ~20px (approximation for 35% feel)
        # Dim opacity 0.25
        # Shadow Offset (0, 10) for 270 deg (Down)

        # NOTE: Initial parent is self.display_container, but will be reparented to global window on show.
        self.settings_overlay = OverlayContainer(
            parent=self.display_container,
            position=OverlayPosition.CENTER,
            margin=20,
            smart_positioning=False,
            close_on_click_outside=True,
            dim_background=True,
            dim_opacity=0.50,
            blur_background=True,
            blur_radius=2,  # 35% estimate
            shadow_enabled=True,
            shadow_blur_radius=30,
            shadow_offset=QPoint(0, 8),  # Downwards (270 deg)
            shadow_color=QColor(0, 0, 0, 100),
        )

        # Init Settings View
        # Use controller's db_path if available
        db_path = (
            self.controller.db_path
            if self.controller and hasattr(self.controller, "db_path")
            else ":memory:"
        )
        self.settings_view = SettingsView(db_path, parent=self)

        # Optimize settings view size for overlay
        self.settings_view.setMinimumSize(600, 500)
        self.settings_view.setStyleSheet("background-color: white; border-radius: 8px;")

        self.settings_overlay.set_content(self.settings_view)
        self.settings_overlay.hide()

    def _handle_sidebar_navigation(self, index: int):
        """
        Handle navigation from sidebar.
        Intercepts Settings (index 2) to show overlay.
        Forwards others (0, 1) to main window.
        """

        if index == 1:  # Settings Index (Now at 1)
            self.show_settings()
            # Close sidebar for better UX (optional, but cleaner)
            self.sidebar_overlay.hide()
            # Reset sidebar selection to 0 (since we stay on page 0 contextually)
            # This keeps the "Enhance Stack" highlighted even accessing Settings
            self.sidebar.set_current_page(0)

        elif index == 0:
            self.page_changed.emit(index)
            # Close sidebar for better UX
            self.sidebar_overlay.hide()

    def show_settings(self):
        """Show settings overlay with FADE animation."""

        # Reparent to global window to cover EVERYTHING (Left/Right panels too)
        # Check if we have a top window
        top_window = self.window()
        if top_window and top_window != self:
            # Reparent only if not already correct (optimization)
            if self.settings_overlay.parent() != top_window:
                self.settings_overlay.setParent(top_window)
                # Force resize to window
                self.settings_overlay.resize(top_window.size())
                self.settings_overlay.move(0, 0)

        # self.settings_overlay.show()
        # self.settings_overlay.raise_()
        self.settings_overlay.show()
        self.settings_overlay.raise_()

    def toggle_sidebar(self):
        """Toggle floating sidebar visibility with animation."""
        is_visible = self.sidebar_overlay.isVisible()
        if is_visible:
            # Hide with FADE
            self.sidebar_overlay.hide()
        else:
            # Show with FADE
            self.sidebar_overlay.show()
            self.sidebar_overlay.raise_()

    def _build_supported_extensions(self):

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
        layout.setContentsMargins(5, 5, 5, 5)
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
    def load_batch(self, batch_id, images, batch_name=None):
        """
        Load batch images ke grid.

        Args:
            batch_id: ID dari batch
            images: List of image objects dengan .id dan .path attributes
            batch_name: Nama dari batch (optional)
        """
        self.current_batch_id = batch_id
        self.current_batch_name = batch_name
        self.logic.set_batch(batch_id, images)

        # Update Header Title
        display_name = batch_name if batch_name else str(batch_id)
        self.header_title.setText(f"{display_name}")
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
        self.current_batch_name = None
        self.header_title.setText("No batch selected")  # Clear header title
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
        if modifiers == Qt.KeyboardModifier.NoModifier:
            self._clear_selection()
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            self.last_selected_card_id = card_id

        # Ctrl + Click - Add/Remove item (multi-select)
        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            else:
                self.selected_thumbnails.discard(card_id)
            self.last_selected_card_id = card_id

        # Shift + Click - Select range (multi-select range)
        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
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

        # Explicitly HIDE result selector for single image preview (as requested)
        self.result_selector.setVisible(False)
        self.save_overlay.hide()  # Hide save button for original image

        self.logic.display_preview(self.zoomable_preview, image_path)
        self.show_preview()

    # =========================================================================
    # === 4. PUBLIC HELPER METHODS ===
    # =========================================================================

    def _on_preview_process_clicked(self):
        """Handle 'Preview Process' button click from Grid."""
        # Try to find last processed result for current batch
        if not self.logic.current_images:
            return

        first_img_path = self.logic.current_images[0].path
        results = self.logic.detect_processed_results(first_img_path)

        if results:
            # Default to first available result
            self.display_processed_result(results[0]["path"])
        else:
            print("[DisplayPanel] No results found to preview.")

    def _on_result_changed(self, value):
        """Handle dropdown selection change."""
        if hasattr(self, "current_results_map") and value in self.current_results_map:
            path = self.current_results_map[value]
            self.display_processed_result(path, update_dropdown=False)

    def display_processed_result(self, image_path, update_dropdown=True):
        """
        Display processed result image in Compare Mode (Default).
        Loads Original + Processed into ComparisonGraphicsItem.
        """
        if not os.path.exists(image_path):
            print(f"[DisplayPanel] Error: Result file not found at {image_path}")
            return

        # Initialize zoom states dict if not exists
        if not hasattr(self, "zoom_states"):
            self.zoom_states = {}

        # SAVE current state if we are switching from another valid preview
        if hasattr(self, "current_preview_path") and self.current_preview_path:
            # Only save if we strictly have a scene items
            if self.preview_scene.items():
                self.zoom_states[self.current_preview_path] = (
                    self.zoomable_preview.get_view_state()
                )

        self.current_preview_path = image_path
        print(f"[DisplayPanel] Showing processed result (Compare Mode): {image_path}")

        # 1. Clear Preview Scene
        self.preview_scene.clear()

        # 2. Determine Original Image
        original_pixmap = None
        if self.logic.current_images:
            original_path = self.logic.current_images[0].path
            if os.path.exists(original_path):
                original_pixmap = QPixmap(original_path)

        processed_pixmap = QPixmap(image_path)
        item = None

        if original_pixmap and processed_pixmap:
            # 3. Create Comparison Item (Reusable from GenericUILibrary)
            item = ImageCompareItem(
                original_pixmap,
                processed_pixmap,
                left_label="Asli",
                right_label="Diproses",
            )
            self.preview_scene.addItem(item)
            self.preview_scene.setSceneRect(item.boundingRect())

            # NOTE: Scroll connections moved to _setup_ui to avoid RuntimeWarnings
            # that occur when trying to disconnect non-existent connections.

        else:
            # Fallback
            self.logic.display_preview(self.zoomable_preview, image_path)
            if self.preview_scene.items():
                item = self.preview_scene.items()[0]

        # RESTORE State or Fit to View
        if image_path in self.zoom_states:
            print(
                f"[DisplayPanel] Restoring zoom state for {os.path.basename(image_path)}"
            )
            self.zoomable_preview.set_view_state(self.zoom_states[image_path])
        else:
            print(f"[DisplayPanel] First view, fitting to view")
            # Reset first to ensure clean state then fit
            self.zoomable_preview.reset_zoom()
            self.zoomable_preview.zoom_to_fit()  # Uses scene rect

        # 3. Update Dropdown logic
        if update_dropdown and self.logic.current_images:
            # Show save button since we are displaying a result
            self.save_overlay.show()
            self.save_overlay.raise_()
            first_img_path = self.logic.current_images[0].path
            results = self.logic.detect_processed_results(first_img_path)

            self.current_results_map = {r["name"]: r["path"] for r in results}
            options = [r["name"] for r in results]

            block = self.result_selector.blockSignals(True)
            self.result_selector.clear()
            self.result_selector.addItems(options)

            current_name = None
            for name, path in self.current_results_map.items():
                if os.path.normpath(path) == os.path.normpath(image_path):
                    current_name = name
                    break

            if current_name:
                self.result_selector.setCurrentText(current_name)

            self.result_selector.blockSignals(block)

        self.show_preview()

    def check_result_availability(self):
        """Check if results exist for current batch and update 'Preview Process' button."""
        if not self.logic.current_images:
            self.preview_process_btn.setVisible(False)
            return

        first_img_path = self.logic.current_images[0].path
        results = self.logic.detect_processed_results(first_img_path)
        self.preview_process_btn.setVisible(bool(results))

    def show_grid(self):
        """Switch ke Grid View."""
        # Save state before exiting preview
        if hasattr(self, "current_preview_path") and self.current_preview_path:
            if hasattr(self, "zoomable_preview") and self.preview_scene.items():
                if not hasattr(self, "zoom_states"):
                    self.zoom_states = {}
                self.zoom_states[self.current_preview_path] = (
                    self.zoomable_preview.get_view_state()
                )

        self.display_stack.setCurrentIndex(0)

        # Update Header buttons
        self.back_btn.setVisible(False)
        self.result_selector.setVisible(False)  # Hide dropdown
        self.save_overlay.hide()  # Hide save button on grid
        self.check_result_availability()  # Update preview button visibility

        if self.current_batch_id:
            self.import_button.setVisible(True)
        else:
            self.import_button.setVisible(False)

    def show_preview(self):
        """Switch ke Preview View."""
        self.display_stack.setCurrentIndex(1)
        self.back_btn.setVisible(True)
        self.result_selector.setVisible(True)  # Show dropdown
        self.import_button.setVisible(False)
        self.preview_process_btn.setVisible(False)

    def remove_selected_images(self):
        """Remove currently selected images dari grid."""
        if self.selected_thumbnails:
            for card_id in list(self.selected_thumbnails):
                # Remove dari logic
                self.logic.unregister_grid_item(card_id)
            self.selected_thumbnails.clear()
            # Reload batch untuk refresh grid
            # Reload batch untuk refresh grid
            if self.current_batch_id and self.logic.current_images:
                self.load_batch(
                    self.current_batch_id,
                    self.logic.current_images,
                    self.current_batch_name,
                )

    def get_selected_image_list(self):
        """Get list of selected image paths."""
        return [
            self.logic.grid_items[cid]["path"]
            for cid in self.selected_thumbnails
            if cid in self.logic.grid_items
        ]

    def set_header_title(self, text: str):
        """Sets the text of the header title."""
        self.header_title.setText(text)

    def _on_save_clicked(self):
        """Handle floating save button click."""
        if hasattr(self, "current_preview_path") and self.current_preview_path:
            import shutil

            # Open save file dialog
            filename = os.path.basename(self.current_preview_path)
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Processed Image",
                filename,
                "Images (*.png *.jpg *.tif *.tiff)",
            )

            if save_path:
                try:
                    shutil.copy2(self.current_preview_path, save_path)
                    from PySide6.QtWidgets import QMessageBox

                    QMessageBox.information(
                        self, "Success", f"Image saved successfully to:\n{save_path}"
                    )
                except Exception as e:
                    from PySide6.QtWidgets import QMessageBox

                    QMessageBox.critical(self, "Error", f"Failed to save image: {e}")

    def _setup_delete_confirmation_widget(self):
        """Create and configure the delete confirmation widget."""
        self.delete_confirmation_widget = MultipleBatchDeleteWidget()
        self.display_stack.addWidget(self.delete_confirmation_widget)

        # Connect signals
        self.delete_confirmation_widget.no_clicked.connect(self.show_grid)
        self.delete_confirmation_widget.yes_clicked.connect(
            self._delete_confirmed_batches
        )

    def show_delete_confirmation(self, batch_ids: list, batch_names: list):
        """
        Switch to the delete confirmation view and pass batch info.

        Args:
            batch_ids: List of batch IDs to be deleted.
            batch_names: List of batch names to display.
        """
        self._batch_ids_to_delete = batch_ids
        self.delete_confirmation_widget.set_batch_info(batch_names)
        self.display_stack.setCurrentIndex(2)  # Index 2 for delete confirmation

        # Update header
        self.set_header_title("Confirm Deletion")
        self.back_btn.setVisible(False)
        self.import_button.setVisible(False)
        self.preview_process_btn.setVisible(False)
        self.result_selector.setVisible(False)

    def _delete_confirmed_batches(self):
        """Handle the actual deletion after confirmation."""
        if hasattr(self, "_batch_ids_to_delete") and self.controller:
            for batch_id in self._batch_ids_to_delete:
                self.controller.delete_batch(batch_id)

            # Refresh the batch list in the right panel
            if self.right_panel:
                self.right_panel._load_batches()

            self.show_grid()
            self.clear_display()  # Go back to the initial state

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
