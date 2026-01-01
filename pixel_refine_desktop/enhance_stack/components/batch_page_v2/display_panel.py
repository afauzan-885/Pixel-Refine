from __future__ import annotations
import shutil

from pixel_refine_desktop.ui.views.settings.views.settings_view import SettingsView

"""
Display Panel Component - Rewritten dengan pola Panorama.
Handles image grid dan full resolution preview dengan proper drag & drop support.

Adapted from: pixel_refine_desktop/ui/views/panorama/display_area/display_panel.py
"""

from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QFileDialog,
    QLabel,
    QComboBox,
    QGraphicsScene,
    QMenu,
)
from PySide6.QtCore import (
    Slot,
    Signal,
    Qt,
    QPoint,
    QSize,
    QThread,
    QObject,
    QTimer,
    QRect,
    QPropertyAnimation,
    QEasingCurve,
)
from typing import Optional, TYPE_CHECKING, Any
from PySide6.QtGui import QPixmap, QColor, QAction
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

# Logic
from pixel_refine_desktop.enhance_stack.core.logic.display_logic import DisplayLogic
from pixel_refine_desktop.enhance_stack.core.logic import display_manager
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    ProcessManager,
    ProcessManager,
    is_widget_alive,
)
from pixel_refine_desktop.enhance_stack.core.logic.selection_manager import (
    SelectionManager,
)
from pixel_refine_desktop.enhance_stack.core.logic.deletion_manager import (
    DeletionManager,
)
from pixel_refine_desktop.enhance_stack.core.logic.import_manager import (
    ImportManager,
)

# Zoomable preview
from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable
from PySide6.QtWidgets import QGraphicsScene

# Animations
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from pixel_refine_desktop.ui.resources.animations.slide import slide
from pixel_refine_desktop.ui.resources.animations.fade import fade_out, fade_in
from pixel_refine_desktop.ui.resources.animations.toast.toast_manager import (
    ToastManager,
    ToastPosition,
    ToastAnimation,
)

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

    # Internal Signals for Thread Safety (Proxy)
    # Digunakan untuk melempar eksekusi dari background thread kembali ke Main Thread
    _worker_finished_proxy_signal = Signal(object, int)  # (worker_ref, count)
    _worker_error_proxy_signal = Signal(object, str)  # (worker_ref, error_msg)

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
        # Managers
        self.selection_manager = SelectionManager(self)
        self.deletion_manager = DeletionManager(self)
        self.deletion_manager.deletion_finished.connect(self._on_deletion_finished)
        self.deletion_manager.deletion_error.connect(self._on_deletion_error)
        self.import_manager = ImportManager(self)

        # State
        self.current_batch_id = None
        self.current_batch_name = None
        self.total_image_count = 0
        self.all_cards = {}  # Map card_id -> ImageCard widget

        # NOTE: Selection and Deletion state moved to managers
        # self.selected_thumbnails, self.active_deletions etc are now in managers.

        # Restoring missing attributes
        self.current_preview_path = None
        self.current_results_map = {}
        self.zoom_states = {}
        self.toast = ToastManager(self)
        self.total_image_count = (
            0  # To track total images independently of UI population
        )
        self.active_deletions = {}  # {batch_id: [paths]} for resume logic

        self.supported_extensions = self._build_supported_extensions()
        if TYPE_CHECKING:
            from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import (
                RightPanel,
            )
        self.right_panel: Any = None
        self.placeholder_widget = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()
        self._setup_sidebar()  # New Sidebar Integration

        # Connect Thumbnail Progress
        self.logic.get_thumbnail_processor().progress_updated.connect(
            self._on_thumbnail_progress
        )

        # Lazy loading timer
        self.lazy_load_timer = QTimer(self)
        self.lazy_load_timer.setSingleShot(True)
        self.lazy_load_timer.setInterval(100)  # 100ms debounce
        self.lazy_load_timer.timeout.connect(self._check_visible_cards)

        # Connect internal proxy signals
        # self._worker_finished_proxy_signal.connect(self._on_worker_finished)
        # self._worker_error_proxy_signal.connect(self._on_worker_error)

        self.setAcceptDrops(True)
        self.clear_display()

    def _setup_ui(self):
        """Setup UI dengan stacked widget untuk grid dan preview mode."""
        self.display_container.main_layout.setContentsMargins(0, 0, 0, 0)
        self.display_container.main_layout.setSpacing(0)

        # --- Tambahkan Drop Overlay (Letakkan setelah display_stack) ---
        self.drop_overlay = QLabel(self)
        self.drop_overlay.setObjectName("DropOverlay")
        self.drop_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_overlay.setHidden(True)  # Sembunyi secara default

        # Styling Overlay (Background semi-transparan dan teks putih besar)
        self.drop_overlay.setStyleSheet(
            """
            #DropOverlay {
                background-color: rgba(46, 204, 113, 180); /* Hijau transparan */
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 10px;
                margin: 20px;
            }
        """
        )

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
        self.import_button.clicked.connect(self.import_manager.import_images)
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

        # GridContainer dengan responsive columns (Matched to ImageCard size 110)
        self.grid_container = GridContainer(
            item_width=110, spacing=10, wrap_mode="vertical", column_mode="responsive"
        )
        self.grid_container.setStyleSheet("QScrollArea { border: none; }")

        # Connect scroll signals for Lazy Loading
        self.grid_container.verticalScrollBar().valueChanged.connect(
            self._on_scroll_changed
        )
        self.grid_container.verticalScrollBar().rangeChanged.connect(
            self._on_scroll_changed
        )

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

    # --- LAZY LOADING SYSTEM ---

    def _on_scroll_changed(self):
        """Triggered when scrollbar moves or range changes."""
        if not self.lazy_load_timer.isActive():
            self.lazy_load_timer.start()

    def _check_visible_cards(self):
        """Mendeteksi kartu yang terlihat di viewport dan memuat thumbnail-nya secara lazy."""
        if not self.all_cards or self.grid_container.isHidden():
            return

        # 1. Dapatkan area yang terlihat (viewport)
        viewport = self.grid_container.viewport()
        visible_region = viewport.rect()

        # Buffer untuk smooth scrolling (opsional: tambahkan margin ke visible_region)
        to_load = []

        for card_id, card in self.all_cards.items():
            try:
                # Periksa apakah kartu terlihat di dalam viewport
                # Map card top-left ke koordinat viewport
                card_pos = card.mapTo(viewport, QPoint(0, 0))
                card_rect = QRect(card_pos, card.size())

                if visible_region.intersects(card_rect):
                    # Kartu terlihat, cek apakah perlu dimuat
                    if (
                        card._is_loading or not card.has_image()
                    ) and not card._is_fetching:
                        card._is_fetching = True
                        to_load.append((card._image_path, card))
                else:
                    # Kartu tidak terlihat, kita bisa mengosongkan memori jika perlu
                    # card.unload_image() # Opsional: Aktifkan jika ingin sangat hemat RAM
                    pass
            except Exception:
                continue

        # 2. PROSES LOAD (Hanya yang terlihat)
        if to_load:
            pairs = []
            for path, card in to_load:

                def make_callback(c):
                    return lambda q_img, p: self._on_thumbnail_ready(q_img, p, c)

                pairs.append((path, make_callback(card)))

            self.logic.load_thumbnails_bulk_async(pairs)

    # =========================================================================
    # === 1. PUBLIC SLOTS UNTUK MEMUAT DATA ===
    # =========================================================================

    @Slot(int, list)
    def load_batch(self, batch_id, images, batch_name=None):
        """
        Load batch images ke grid secara progresif (pure lazy loading).
        """
        self.current_preview_path = None
        self.current_batch_id = batch_id
        self.current_batch_name = batch_name

        # Hide old batch toast
        self.toast.hide()
        self.logic.set_batch(batch_id, images)

        # Set exact count tracked from backend data
        # START ZOMBIE LOGIC: If we have pending deletions, we need to add them to the grid
        # so they can fade out properly.
        current_images_ids = {str(img.id) for img in images}

        pending_zombies = []
        if batch_id in self.active_deletions:
            for path in self.active_deletions[batch_id]:
                idx = os.path.basename(path)
                if idx not in current_images_ids:
                    # Create a zombie image object
                    class ZombieImg:
                        def __init__(self, p):
                            self.path = p
                            self.id = os.path.basename(p)

                    pending_zombies.append(ZombieImg(path))

        # Merge real images with zombies for visual consistency
        # Zombies go first? Or last? Doesn't matter much for deletion, but maybe last.
        # However, to maintain index stability, let's append.
        visual_images = list(images) + pending_zombies

        self.total_image_count = len(visual_images)

        # Update Header Title segera dengan jumlah gambar yang akan dimuat
        self._update_header_title()

        # 0. Cancel any existing processes/animations for previous state
        ProcessManager.instance().cancel_context("display_populate")
        ProcessManager.instance().cancel_context("display_sequential_removal")
        self.grid_animator.stop_all()

        # Stop & Flush batch sebelumnya, lalu siapkan stats untuk batch baru (Toast Fix)
        # Sembunyikan toast batch lama secara eksplisit - User Request: "Pindah batch hilangkan saja"
        self.toast.hide()
        processor = self.logic.get_thumbnail_processor()
        processor.stop_all()
        processor.reset_stats(self.current_batch_id, self.total_image_count)

        self._clear_grid()
        self.grid_container.set_batch_update(True)

        # Update Header Title (Setelah state dibersihkan, agar count akurat)
        self._update_header_title(count=self.total_image_count)

        # Check if batch is empty (visually)
        if not visual_images:
            # Show empty state but keep import button visible in header
            self.import_button.setVisible(True)
            self._show_empty_batch_state()
            self.show_grid()
            return

        self.import_button.setVisible(True)
        self.show_grid()

        # Switch back to grid container using animation helper
        if self.grid_content_stack.currentWidget() != self.grid_container:
            self._set_placeholder(None)

        # Resume deletion simulation if there are pending deletions for this batch
        self.deletion_manager.resume_deletion_simulation(batch_id)

        # Prepare incremental population to avoid UI freeze
        self._populate_queue = list(visual_images)
        if hasattr(self, "_populate_timer") and self._populate_timer.isActive():
            self._populate_timer.stop()

        self._populate_timer = QTimer(self)
        self._populate_timer.timeout.connect(self._process_incremental_population)

        # Register to ProcessManager
        ProcessManager.instance().register_timer(
            "display_populate", self._populate_timer
        )

        # Start population: 10 images per 30ms (Smooth & Fast)
        self._populate_timer.start(30)

    def _process_incremental_population(self):
        """Slots to add images to grid in chunks to avoid UI hang."""
        if not hasattr(self, "_populate_queue") or not self._populate_queue:
            self._populate_timer.stop()
            self.grid_container.set_batch_update(False)
            # Final check for thumbnails
            self._check_visible_cards()
            return

        # Add 10 images per tick
        CHUNK_SIZE = 15
        for _ in range(CHUNK_SIZE):
            if not self._populate_queue:
                break

            img = self._populate_queue.pop(0)

            # Check if this is a Zombie (pending deletion)
            # Assumption: Zombie object created in load_batch has a distinct attribute or we check path
            is_zombie = (
                hasattr(img, "__class__") and img.__class__.__name__ == "ZombieImg"
            )

            card = ImageCard(card_id=str(img.id), size=110)
            card._image_path = img.path

            if not is_zombie:
                card.double_clicked.connect(self._on_card_double_clicked)
                card.clicked.connect(
                    lambda cid, event, c=card: self._on_card_clicked(cid, event, c)
                )

                self.all_cards[str(img.id)] = card
                self.grid_container.add_item(card)
                self.logic.register_grid_item(str(img.id), {"path": img.path})
            else:
                self.all_cards[str(img.id)] = card
                self.grid_container.add_item(card)
                # ZOMBIE LOGIC: Immediately queue for removal via Manager (resuming stream)
                self.deletion_manager.queue_zombie_card(str(img.id), card)

        # TRIGER PEMUATAN THUMBNAIL DINAMIS (Toast Fix: Mulai sekarang, jangan tunggu beres semua)
        self._check_visible_cards()

        # Update progress header
        self._update_header_title()

    @Slot()
    def clear_display(self):
        """
        Clear display ketika tidak ada batch yang dipilih.
        Reset ke state default dengan placeholder widget dan tombol "New Batch".
        """
        self.current_batch_id = None
        self.current_batch_name = None

        # Hide any active toast when batch is unselected
        self.toast.hide()

        # 0. Cancel all pending populations and removals
        ProcessManager.instance().cancel_context("display_populate")
        ProcessManager.instance().cancel_context("display_sequential_removal")

        self._update_header_title()  # Clear header title
        # self._update_cross_batch_toast()  # Check other batches
        self.logic.clear_all()
        self._clear_grid()
        self.selection_manager.clear()
        self.all_cards.clear()
        # self.last_selected_card_id = None # Handled by manager
        # self.selection_anchor_id = None # Handled by manager

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
    # === 3. PRIVATE METHODS - GRID MANAGEMENT ===
    # =========================================================================

    def _clear_grid(self):
        """Remove all widgets from grid container."""
        # Tambahan: Hentikan semua animasi yang berjalan pada grid sebelum clear
        self.grid_animator.stop_all()
        self.grid_container.clear_items()

    def _clear_selection(self):
        """Deselect semua cards via Manager."""
        self.selection_manager.clear_selection()

    def _select_range(self, start_card_id, end_card_id):
        """Select range via Manager."""
        self.selection_manager.select_range(start_card_id, end_card_id)

    def _is_widget_in_viewport(self, widget):
        """
        Cek apakah widget berada di dalam viewport GridContainer.
        Digunakan untuk optimasi animasi (Viewport-Aware Animation).
        """
        if not is_widget_alive(widget) or not widget.isVisible():
            return False

        try:
            # Akses viewport dari QScrollArea di dalam GridContainer
            viewport = self.grid_container.viewport()
            if not viewport:
                return False

            # Ambil area yang terlihat (0,0, w, h)
            visible_rect = viewport.rect()

            # Map posisi widget (local) ke posisi viewport
            # mapTo(parent, pos) sangat akurat untuk nested widget
            widget_pos = widget.mapTo(viewport, QPoint(0, 0))
            widget_rect = QRect(widget_pos, widget.size())

            # Cek apakah kotak widget bersinggungan dengan kotak viewport
            return visible_rect.intersects(widget_rect)
        except Exception:
            return False

    def _load_thumbnail_async(self, image_path, card_widget):
        """
        Load thumbnail asinkron untuk image card dengan Viewport-Aware Animation.
        """
        self.logic.load_thumbnail_async(
            image_path, lambda img, p: self._on_thumbnail_ready(img, p, card_widget)
        )

    def _on_thumbnail_ready(self, q_image, path, card_widget):
        """Callback when thumbnail is ready, updates card with animation."""
        if card_widget is not None and is_widget_alive(card_widget):
            # Selalu panggil set_image untuk membersihkan status loading
            # Jika q_image null, ImageCard akan menampilkan placeholder '!'
            pixmap = QPixmap.fromImage(q_image) if not q_image.isNull() else QPixmap()
            card_widget.set_image(pixmap)

            # Sembunyikan progress jika sudah dimuat (mencegah double fetch)
            card_widget._is_fetching = False

            # LOGIKA BARU: Cek Viewport untuk optimasi animasi
            is_visible = self._is_widget_in_viewport(card_widget)
            fade_in(
                self.grid_animator,
                card_widget,
                duration=300,
                skip_animation_if_not_visible=not is_visible,
            )

    def _on_card_clicked(self, card_id, event, card_widget):
        """Handle click via Manager."""
        self.selection_manager.handle_card_clicked(card_id, event, card_widget)

    def _on_thumbnail_progress(self, batch_id, decode_pct, save_pct):
        """Update toast progress for thumbnail creation and saving."""
        # 1. ISOLASI BATCH: Hanya update jika batch_id cocok dengan tampilan aktif
        if str(batch_id) != str(self.current_batch_id):
            return

        # 2. Hanya tampilkan jika proses cukup besar
        if decode_pct >= 100 and save_pct >= 100:
            # Selesai: Tampilkan pesan sukses singkat
            self.toast.show_message(
                "Semua thumbnail berhasil diproses.",
                duration=3000,
                position=ToastPosition.BOTTOM_RIGHT,
            )
        elif decode_pct == 0 and save_pct == 0:
            # Belum mulai atau kosong
            pass
        else:
            # Sedang Berjalan:
            # CEK CACHING: Jika sejak awal sudah 100% tanpa perlu dekoding (L1/L2 hits)
            # Karena _update_progress dipanggil setelah process_batch (yang mengupdate hits)
            # Jika progres langsung tinggi tanpa interaksi worker, kita anggap caching.
            is_pure_cache = decode_pct >= 100  # Jika dari L1/L2 hits langsung 100%

            if is_pure_cache:
                msg = "Caching berhasil"
                self.toast.show_message(
                    msg, duration=2000, position=ToastPosition.BOTTOM_RIGHT
                )
            else:
                msg = f"Membuat {decode_pct}% - Menyimpan {save_pct}%"
                self.toast.show_progress(msg, position=ToastPosition.BOTTOM_RIGHT)

    def _on_card_double_clicked(self, card_id):
        """
        Handle double-click pada image card untuk preview full resolution.

        Args:
            card_id: ID dari card yang di-click
        """
        sender = self.sender()
        image_path = getattr(sender, "_image_path", None)
        if image_path:
            self._display_image_preview(image_path)

    def _select_all_images(self):
        """Select all via Manager."""
        self.selection_manager.select_all()

    def _refresh_current_batch(self):
        """Helper to re-load current batch settings from controller/db."""
        if not self.current_batch_id or not self.controller:
            return

        batch = self.controller.get_batch(self.current_batch_id)
        if batch:
            self.load_batch(
                self.current_batch_id, batch.images, self.current_batch_name
            )

    def keyPressEvent(self, event):
        """Handle keyboard events (Delete key, Ctrl+A, and Arrow navigation)."""
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key.Key_Delete:
            self._handle_delete_action()
        elif modifiers == Qt.KeyboardModifier.ControlModifier and key == Qt.Key.Key_A:
            self._select_all_images()
        elif key in (
            Qt.Key.Key_Left,
            Qt.Key.Key_Right,
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
        ):
            shift_held = modifiers == Qt.KeyboardModifier.ShiftModifier
            self._navigate_selection(key, shift_held)
        elif key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._handle_enter_press()
        else:
            super().keyPressEvent(event)

    def _handle_enter_press(self):
        """Handle Enter key to show preview for single selection."""
        if self.display_stack.currentIndex() != 0:
            return

        if len(self.selection_manager.selected_thumbnails) == 1:
            card_id = list(self.selection_manager.selected_thumbnails)[0]
            if card_id in self.all_cards:
                card = self.all_cards[card_id]
                image_path = getattr(card, "_image_path", None)
                if image_path:
                    self._display_image_preview(image_path)

    def _navigate_selection(self, key, shift_held):
        """Navigate via Manager."""
        self.selection_manager.navigate_selection(key, shift_held)

    def contextMenuEvent(self, event):
        """Handle right-click context menu pada area grid."""
        # Hanya tampilkan menu jika di dalam Grid View dan ada batch terpilih
        if self.display_stack.currentIndex() != 0 or not self.current_batch_id:
            return

        # Check if right click hits a card
        card_under_mouse = None
        for card_id, card in self.all_cards.items():
            if card.underMouse():
                card_under_mouse = card
                break

        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #F0F0F0;
                color: #000000;
            }
            QMenu::separator {
                height: 1px;
                background: #E0E0E0;
                margin: 5px 0px;
            }
        """
        )

        # 1. Select Reference Image (Only if exactly one card is right-clicked)
        if card_under_mouse:
            ref_path = card_under_mouse._image_path
            action_ref = QAction("Select Reference Image", self)
            action_ref.triggered.connect(lambda: self._set_as_reference(ref_path))
            menu.addAction(action_ref)
            menu.addSeparator()

        # 2. Delete Selected Images
        if self.selection_manager.selected_thumbnails:
            action_del = QAction(
                f"Delete Images ({len(self.selection_manager.selected_thumbnails)})",
                self,
            )
            action_del.triggered.connect(self._handle_delete_action)
            menu.addAction(action_del)

        if not menu.isEmpty():
            menu.exec(event.globalPos())

    def _set_as_reference(self, image_path):
        """Set image as reference via controller."""
        if self.current_batch_id and self.controller:
            if self.controller.set_reference_image(self.current_batch_id, image_path):
                self._refresh_current_batch()

    def _handle_delete_action(self):
        """Handle deletion via Manager."""
        self.deletion_manager.request_deletion(
            self.selection_manager.get_selected_ids()
        )

    @Slot(int)
    def on_batch_import_started(self, batch_id):
        """Delegate to ImportManager."""
        self.import_manager.on_batch_import_started(batch_id)

    @Slot(int)
    def on_batch_import_finished(self, batch_id):
        """Delegate to ImportManager."""
        self.import_manager.on_batch_import_finished(batch_id)

    @Slot(int, str, str)
    def add_single_image_to_grid(self, batch_id, batch_name, image_path):
        """Delegate to ImportManager."""
        self.import_manager.add_single_image_to_grid(batch_id, batch_name, image_path)

    def _on_deletion_finished(self, count):
        """Handle completion of image deletion."""
        # Refresh current batch settings from DB if needed
        # (Though DeletionManager now handles UI removal progressively)
        self._refresh_current_batch()

    def _on_deletion_error(self, error_message):
        """Handle error during image deletion."""
        # No need to show toast here, DeletionManager does it.
        # Just refresh to be safe.
        self._refresh_current_batch()

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
        display_manager.display_processed_result(self, image_path, update_dropdown)

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
        """Remove currently selected images dari grid via Logic."""
        if self.selection_manager.selected_thumbnails:
            for card_id in list(self.selection_manager.selected_thumbnails):
                # Remove dari logic
                self.logic.unregister_grid_item(card_id)
            self.selection_manager.selected_thumbnails.clear()
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
            for cid in self.selection_manager.selected_thumbnails
            if cid in self.logic.grid_items
        ]

    def set_header_title(self, text: str):
        """Sets the text of the header title."""
        self.header_title.setText(text)

    def _update_header_title(self, count=None):
        """Helper to update header title with batch name and image count."""
        if not self.current_batch_id:
            self.header_title.setText("No batch selected")
            return

        display_name = (
            self.current_batch_name
            if self.current_batch_name
            else str(self.current_batch_id)
        )

        # Prioritaskan parameter count jika diberikan, jika tidak gunakan total_image_count
        actual_count = count if count is not None else self.total_image_count
        self.header_title.setText(f"{display_name}: ({actual_count} image)")

    def _on_save_clicked(self):
        """Handle floating save button click."""
        if hasattr(self, "current_preview_path") and self.current_preview_path:

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

                    QMessageBox.information(
                        self, "Success", f"Image saved successfully to:\n{save_path}"
                    )
                except Exception as e:

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
    # === 5. DRAG & DROP SUPPORT ===
    # =========================================================================

    # Overide resizeEvent untuk memastikan overlay selalu menutupi area display
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "drop_overlay"):
            self.drop_overlay.resize(self.size())

    def dragEnterEvent(self, event):
        if not self.current_batch_id:
            event.ignore()
            return

        if event.mimeData().hasUrls():
            # Hitung jumlah file yang sedang di-hover
            file_count = len(
                [url for url in event.mimeData().urls() if url.isLocalFile()]
            )

            if file_count > 0:
                event.acceptProposedAction()
                # Tampilkan overlay dan update teks
                self.drop_overlay.setText(f"Jatuhkan {file_count} gambar di sini")
                self.drop_overlay.show()
                self.drop_overlay.raise_()  # Pastikan di paling atas
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_overlay.hide()
        event.accept()

    def dropEvent(self, event):
        self.drop_overlay.hide()
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
