from __future__ import annotations
from pixel_refine_desktop.ui.views.settings.General.Language import language_config
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
    QGraphicsPixmapItem,
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
from PySide6.QtGui import QPixmap, QColor, QAction, QImage
import os

# Generic UI Library
from resources.GenericUILibrary import (
    ImageCard,
    Button,
    IconButton,
    Container,
    OverlayContainer,
    OverlayPosition,
    ImageCompareItem,
)
from resources.GenericUILibrary.grids import GridContainer
from resources.animations.slide import slide
from resources.animations.animation_manager import (
    SlideDirection,
    StackedWidgetAnimator,
)
from resources.GenericUILibrary.forms import FormGroup
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
from pixel_refine_desktop.enhance_stack.core.logic.grid_manager import GridManager
from pixel_refine_desktop.enhance_stack.core.logic.ui_state_manager import (
    UIStateManager,
)
from pixel_refine_desktop.enhance_stack.core.logic.database_manager import DatabaseManager
from pixel_refine_desktop.enhance_stack.core.logic.drag_drop_handler import (
    DragDropHandler,
)
from pixel_refine_desktop.enhance_stack.core.logic.context_menu_handler import (
    ContextMenuHandler,
)

# Zoomable preview
from pixel_refine_desktop.enhance_stack.core.logic.Zoomable_Handler import Zoomable
from PySide6.QtWidgets import QGraphicsScene

# Animations
from resources.animations.animation_manager import (
    StackedWidgetAnimator,
    SlideDirection,
)
from resources.animations.slide import slide
from resources.animations.fade import fade_out, fade_in
from resources.animations.toast.toast_manager import (
    ToastManager,
    ToastPosition,
    ToastAnimation,
)

# Config untuk supported image formats
from config import SUPPORTED_FORMATS

# Import the new widget
from .multiple_batch_delete_widget import MultipleBatchDeleteWidget
from resources.GenericUILibrary import live_update
import numpy as np

class BurstCacheWorker(QThread):
    image_cached = Signal(str, QImage)  # (path, q_image)
    
    def __init__(self, paths, parent=None):
        super().__init__(parent)
        self.paths = paths
        self._is_cancelled = False
        
    def run(self):
        for path in self.paths:
            if self._is_cancelled:
                break
            try:
                # Load array using half_res helper logic
                ext = os.path.splitext(path)[1].lower()
                image_array = None
                
                # Check format
                if ext in SUPPORTED_FORMATS.get("jpg", []) + SUPPORTED_FORMATS.get("png", []) + SUPPORTED_FORMATS.get("tiff", []):
                    # Load with PIL
                    from PIL import Image, ImageOps
                    import cv2
                    with Image.open(path) as img:
                        img = ImageOps.exif_transpose(img)
                        if img.mode in ("RGBA", "LA", "P"):
                            img = img.convert("RGB")
                        elif img.mode == "L":
                            img = img.convert("RGB")
                        image_array = np.array(img)
                        # Resize to half resolution
                        h, w = image_array.shape[:2]
                        image_array = cv2.resize(image_array, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
                        # Convert to BGR for uniform channel format
                        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                        
                elif ext in SUPPORTED_FORMATS.get("raw", []):
                    from pixel_refine_desktop.enhance_stack.core.logic.multi_threading import load_raw_as_8bit_rgb_half_res
                    import cv2
                    img_rgb = load_raw_as_8bit_rgb_half_res(path)
                    image_array = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                
                if image_array is not None:
                    # Convert to QImage
                    height, width = image_array.shape[:2]
                    # Ensure we convert BGR to RGB for QImage
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
                    bytes_per_line = 3 * width
                    # Use QImage copy to duplicate bytes safely
                    q_image = QImage(
                        image_array.data.tobytes(),
                        width,
                        height,
                        bytes_per_line,
                        QImage.Format.Format_RGB888
                    ).copy()
                    
                    self.image_cached.emit(path, q_image)
            except Exception as e:
                print(f"Error pre-caching {path}: {e}")
                
    def cancel(self):
        self._is_cancelled = True


class BackgroundBatchPreloader(QThread):
    """
    Background thread untuk pre-generate thumbnail batch baru secara diam-diam.

    Dipanggil otomatis saat batch baru dibuat atau gambar baru diimpor.
    Menggunakan GlobalThumbnailCache dari thumbnail_processor agar saat user
    membuka batch tersebut, thumbnailnya sudah siap di RAM — tampil instan.

    Prioritas thread: LowestPriority sehingga tidak mengganggu rendering aktif.
    Throttle RAW: memanfaatkan RawDemosaicThrottle (maks 2 paralel) secara otomatis
    melalui process_thumbnail_logic.
    """
    thumbnail_preloaded = Signal(str, str)  # (batch_id, image_path)

    def __init__(self, batch_id, image_paths, parent=None):
        super().__init__(parent)
        self.batch_id = str(batch_id)
        self.image_paths = list(image_paths)
        self._is_cancelled = False
        self.setPriority(QThread.Priority.LowestPriority)

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        """Pre-load thumbnails ke GlobalThumbnailCache secara diam-diam di background."""
        try:
            from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
                get_global_cache,
                process_thumbnail_logic,
                convert_pil_to_qimage,
                get_thumbnail_repo,
            )
        except ImportError:
            return

        global_cache = get_global_cache()

        for path in self.image_paths:
            if self._is_cancelled:
                break

            # Skip jika sudah ada di L0 cache
            if global_cache.has(path):
                continue

            try:
                # Cek L2 disk cache dulu (lebih cepat dari decode)
                repo = get_thumbnail_repo()
                cached_disk = repo.get_thumbnail(path)
                if not cached_disk.isNull():
                    global_cache.put(path, cached_disk)
                    if not self._is_cancelled:
                        self.thumbnail_preloaded.emit(self.batch_id, path)
                    continue

                # Decode thumbnail (process_thumbnail_logic otomatis pakai RawDemosaicThrottle)
                pil_thumb = process_thumbnail_logic(path, (128, 128))
                if self._is_cancelled:
                    break
                if pil_thumb:
                    q_image = convert_pil_to_qimage(pil_thumb)
                    if not q_image.isNull():
                        # Simpan ke disk dan L0
                        repo.save_thumbnail(path, q_image)
                        global_cache.put(path, q_image)
                        if not self._is_cancelled:
                            self.thumbnail_preloaded.emit(self.batch_id, path)
            except Exception as e:
                if not self._is_cancelled:
                    print(f"[BackgroundBatchPreloader] Error pre-loading {path}: {e}")



@live_update
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

        self.controller = controller
        self.logic = DisplayLogic()

        # Managers
        self.selection_manager = SelectionManager(self)
        self.deletion_manager = DeletionManager(self)
        self.deletion_manager.deletion_finished.connect(self._on_deletion_finished)
        self.deletion_manager.deletion_error.connect(self._on_deletion_error)
        self.import_manager = ImportManager(self)
        self.grid_manager = GridManager(self)
        self.ui_state_manager = UIStateManager(self)
        self.drag_drop_handler = DragDropHandler(self)
        self.context_menu_handler = ContextMenuHandler(self)

        # State
        self.current_batch_id = None
        self.total_image_count = 0
        self._success_toast_shown = False
        self._is_checking_thumbnails = False  # Toast sequencing flag
        self.current_batch_name = None
        self.all_cards = {}  # Map card_id -> ImageCard widget

        # Restoring missing attributes
        self.current_preview_path = None
        self.current_results_map = {}
        self.zoom_states = {}
        self.playback_cache = {}
        self.cache_worker = None
        self.toast = ToastManager(self)
        self.active_deletions = {}  # {batch_id: [paths]} for resume logic
        self.right_panel: Any = None
        self.placeholder_widget = None
        # Track active background preloaders (satu per batch_id)
        self._bg_preloaders: dict = {}  # batch_id (str) -> BackgroundBatchPreloader
        

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()
        self._setup_sidebar()  # New Sidebar Integration
        self._setup_param_overlay()

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

        # Connect import_finished -> background pre-loader (otomatis, silent)
        self.import_manager.import_finished.connect(self._start_background_preload)

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
        self.header_layout.setSpacing(0)  # Spacing handled by sub-layouts

        # Left Column Layout (Sidebar toggle + Title)
        self.left_header_layout = QHBoxLayout()
        self.left_header_layout.setContentsMargins(0, 0, 0, 0)
        self.left_header_layout.setSpacing(10)
        self.left_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # 0. Sidebar Toggle Button (New)
        self.toggle_btn = Button("☰", object_name="SidebarToggleBtn")
        self.toggle_btn.setFixedWidth(40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.left_header_layout.addWidget(self.toggle_btn)

        # Title Label
        self.header_title = QLabel("")
        self.header_title.setObjectName("DisplayHeaderTitle")
        self.left_header_layout.addWidget(self.header_title)
        
        # Center Column Layout (Bulk Mode Dynamic Button centered)
        self.center_header_layout = QHBoxLayout()
        self.center_header_layout.setContentsMargins(0, 0, 0, 0)
        self.center_header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Bulk Mode Dynamic Button
        from PySide6.QtWidgets import QPushButton
        self.is_bulk_mode = False
        
        self.bulk_mode_btn = QPushButton(language_config.LBL_BATCH_MODE, self)
        self.bulk_mode_btn.setObjectName("BulkModeBtn")
        
        # Initial Slate/Gray style (Batch mode)
        self.bulk_mode_btn.setStyleSheet("""
            QPushButton#BulkModeBtn {
                background-color: #F1F3F4;
                color: #5F6368;
                border: 1px solid #DADCE0;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 10.5pt;
                font-weight: 600;
            }
            QPushButton#BulkModeBtn:hover {
                background-color: #E8EAED;
            }
            QPushButton#BulkModeBtn:pressed {
                background-color: #D2D4D7;
            }
        """)
        
        # Add opacity effect for text fading transition
        opacity_effect = QGraphicsOpacityEffect(self.bulk_mode_btn)
        self.bulk_mode_btn.setGraphicsEffect(opacity_effect)
        self.center_header_layout.addWidget(self.bulk_mode_btn)
        
        # Right Column Layout (Tools and Actions aligned to the right)
        self.right_header_layout = QHBoxLayout()
        self.right_header_layout.setContentsMargins(0, 0, 0, 0)
        self.right_header_layout.setSpacing(10)
        self.right_header_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

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
        self.right_header_layout.addWidget(self.result_selector)

        # 1. Back to Grid Button
        self.back_btn = Button(language_config.BTN_BACK_TO_GRID, variant="secondary")
        self.back_btn.setFixedWidth(120)
        self.back_btn.clicked.connect(self.show_grid)
        self.back_btn.setVisible(False)
        self.right_header_layout.addWidget(self.back_btn)

        # 2. Preview Process Button (Shortcut from Grid)
        self.preview_process_btn = IconButton(
            icon_path="resources/assets/icons/play-preview.png",
            variant="primary",
        )
        self.preview_process_btn.setToolTip("Image Process")
        self.preview_process_btn.setFixedWidth(40)
        self.preview_process_btn.clicked.connect(self._on_preview_process_clicked)
        self.preview_process_btn.setVisible(False)
        self.right_header_layout.addWidget(self.preview_process_btn)


        # 3.5. Import Images Button
        self.import_button = Button(language_config.TOPBAR_BATCH_IMPORT_BUTTON_TEXT, object_name="ImportImageBtn")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_manager.import_images)
        self.import_button.setVisible(False)
        self.right_header_layout.addWidget(self.import_button)

        # 4. New Batch button (shown ONLY when no batches exist / right panel is hidden)
        self.new_batch_header_btn = Button(language_config.BTN_NEW_BATCH, variant="primary")
        self.new_batch_header_btn.setFixedWidth(110)
        self.new_batch_header_btn.setFixedHeight(25)
        self.new_batch_header_btn.setStyleSheet(self.new_batch_header_btn.styleSheet() + " QPushButton { padding: 4px 8px; font-size: 8pt; }")
        self.new_batch_header_btn.clicked.connect(self._create_new_batch)
        self.new_batch_header_btn.setVisible(False)  # Hidden by default; shown from page_layout
        self.right_header_layout.addWidget(self.new_batch_header_btn)

        # Assemble the header columns with equal stretch factors (1, 1, 1) to force center centering
        self.header_layout.addLayout(self.left_header_layout, 1)
        self.header_layout.addLayout(self.center_header_layout, 1)
        self.header_layout.addLayout(self.right_header_layout, 1)

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
        # Make the background transparent to focus on the inner green box placeholder
        self.grid_view_widget.setStyleSheet(
            "background-color: transparent; border-radius: 4px;"
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

        # Connect Selection Change

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

        # Playback controls container (Floating over preview_wrapper)
        self.controls_bar = QWidget()
        self.controls_bar.setObjectName("ControlsBar")
        self.controls_bar.setStyleSheet("""
            #ControlsBar {
                background-color: transparent;
                border: none;
            }
        """)
        
        self.controls_bar_layout = QHBoxLayout(self.controls_bar)
        self.controls_bar_layout.setContentsMargins(8, 4, 8, 4)
        self.controls_bar_layout.setSpacing(8)
        self.controls_bar_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # SizePolicy: Shrink to fit content dynamically
        from PySide6.QtWidgets import QSizePolicy as _SP
        self.controls_bar.setSizePolicy(_SP.Policy.Minimum, _SP.Policy.Minimum)

        # Initialize playback buttons (using emojis as requested, wrapping tightly with size 36x36)
        from PySide6.QtWidgets import QPushButton
        
        self.prev_frame_btn = QPushButton("⏮")
        # No fixed size — button auto-sizes to emoji font via CSS padding
        self.prev_frame_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                padding: 4px 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 15);
                border-radius: 6px;
            }
        """)
        self.prev_frame_btn.setFixedSize(36, 36)
        self.prev_frame_btn.clicked.connect(self._show_prev_frame)

        self.play_btn = QPushButton("▶")
        # No fixed size — button auto-sizes to emoji font
        self.play_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                padding: 4px 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 15);
                border-radius: 6px;
            }
        """)
        self.play_btn.setFixedSize(36, 36)
        self.play_btn.clicked.connect(self._toggle_playback)

        self.next_frame_btn = QPushButton("⏭")
        # No fixed size — button auto-sizes to emoji font
        self.next_frame_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 18px;
                padding: 4px 6px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 15);
                border-radius: 6px;
            }
        """)
        self.next_frame_btn.setFixedSize(36, 36)
        self.next_frame_btn.clicked.connect(self._show_next_frame)

        # Center layout for playback buttons (wrapped in container to collapse properly when hidden)
        self.playback_container = QWidget()
        self.playback_container.setStyleSheet("background: transparent;")
        playback_layout = QHBoxLayout(self.playback_container)
        playback_layout.setContentsMargins(0, 0, 0, 0)
        playback_layout.setSpacing(4)
        playback_layout.addWidget(self.prev_frame_btn)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.next_frame_btn)

        self.controls_bar_layout.addWidget(self.playback_container)
        
        self.save_btn_ref = Button("Save", variant="secondary")
        self.save_btn_ref.setFixedSize(80, 32)
        self.save_btn_ref.clicked.connect(self._on_save_clicked)
        
        self.start_btn_ref = Button("▶ Start", variant="primary")
        from resources.GenericUILibrary.theme import get_theme, create_button_style
        theme = get_theme()
        self.start_btn_ref.setStyleSheet(
            create_button_style(self.start_btn_ref.variant, theme)
            + """
            QPushButton {
                padding: 5px;
                font-size: 10pt;
            }
        """
        )
        self.start_btn_ref.setFixedSize(110, 32)
        self.start_btn_ref.setVisible(False)
        self.is_start_button_mode = False
        
        self.controls_bar_layout.addWidget(self.start_btn_ref)
        self.controls_bar_layout.addWidget(self.save_btn_ref)

        self.controls_overlay = OverlayContainer(
            parent=self,
            position=OverlayPosition.BOTTOM_CENTER,
            margin=15,
            shadow_enabled=True,
        )
        self.controls_overlay.set_content(self.controls_bar)
        self.controls_overlay.hide()
        self.save_overlay = self.controls_overlay

        self.display_stack.addWidget(preview_wrapper)

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
                "resources/assets/icons/enhance_stack.png",
            ),
            # ("Panorama", "resources/assets/icons/panorama.png"), # Removed
            ("Settings", "resources/assets/icons/setting.png"),
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
        self.settings_view.setObjectName("SettingsViewDialog")

        self.settings_overlay.set_content(self.settings_view)
        self.settings_overlay.hide()

    def _setup_param_overlay(self):
        """Setup independent overlay for Switchable Parameter Panel."""
        from .switchable_parameter_panel import SwitchableParameterPanel
        self.param_overlay = OverlayContainer(
            parent=self.display_container,
            position=OverlayPosition.BOTTOM_RIGHT,
            margin=(10, 20),
            smart_positioning=False,
            close_on_click_outside=False,
            dim_background=False,
            blur_background=False,
            shadow_enabled=True,
            shadow_blur_radius=20,
            shadow_offset=QPoint(0, 4),
            shadow_color=QColor(0, 0, 0, 80),
        )
        self.param_overlay.setStyleSheet("""
            #OverlayContainer {
                background: transparent;
                background-color: transparent;
                border: none;
            }
            #OverlayContentWrapper {
                background: transparent;
                background-color: transparent;
                border: none;
            }
        """)
        self.param_panel = SwitchableParameterPanel(parent=self, store=self.right_panel._store if self.right_panel else None)
        self.param_overlay.set_content(self.param_panel)
        self.param_overlay.hide()

    def toggle_param_overlay(self):
        if self.param_overlay.isVisible():
            self.param_overlay.hide()
        else:
            # Sync settings from right panel before showing
            if self.right_panel:
                current_settings = self.right_panel.get_current_settings()
                self.param_panel.update_settings_state(current_settings)
            
            self.param_overlay.show()
            self.param_overlay.raise_()

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
        """Toggle floating sidebar visibility directly without fade animation."""
        is_visible = self.sidebar_overlay.isVisible()
        if is_visible:
            self.sidebar_overlay.hide()
        else:
            self.sidebar_overlay.show()
            self.sidebar_overlay.raise_()

    def _create_placeholder_widget(
        self, html_text="", button_text=None, on_button_click=None
    ):
        """Delegate to UIStateManager."""
        return self.ui_state_manager.create_placeholder_widget(
            html_text, button_text, on_button_click
        )

    def _set_placeholder(self, widget):
        """Delegate to UIStateManager."""
        self.ui_state_manager.set_placeholder(widget)

    # --- LAZY LOADING SYSTEM ---

    def _on_scroll_changed(self):
        """Triggered when scrollbar moves or range changes."""
        if not self.lazy_load_timer.isActive():
            self.lazy_load_timer.start()

    def _check_visible_cards(self):
        """Delegate to DisplayLogic for lazy loading."""
        to_load = self.logic.check_visible_cards(
            self.all_cards, self.grid_container, lambda: self.grid_container.viewport()
        )

        if to_load:
            pairs = []
            for path, card in to_load:

                def make_callback(c):
                    return lambda q_img, p: self._on_thumbnail_ready(q_img, p, c)

                pairs.append((path, card, make_callback))

            self.logic.load_visible_thumbnails(pairs)

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
        self._success_toast_shown = False

        # Update Header Title segera dengan jumlah gambar yang akan dimuat
        self._update_header_title()

        # 0. Cancel any existing processes/animations for previous state
        self._reset_population_state()

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

        # Show param overlay based on setting state (collapsed by default)
        if self.right_panel:
            current_settings = self.right_panel.get_current_settings()
            self.param_panel.active_tab = None
            self.param_panel.set_expanded(False)
            self.param_panel._update_styles("transparent")
            self.param_panel.update_settings_state(current_settings)

        # Check if batch is empty (visually)
        if not visual_images:
            # Show empty state but keep import button visible in header
            self.grid_container.set_batch_update(False)
            self.import_button.setVisible(True)
            self._show_empty_batch_state()
            self.show_grid()
            return

        self.import_button.setVisible(True)
        self.show_grid()
        self.grid_manager.stop_staged_timer()
        self._real_paths_for_sync = [img.path for img in images if hasattr(img, "path")]
        self.grid_manager.set_sync_paths(self._real_paths_for_sync)

        # Switch back to grid container using animation helper
        if self.grid_content_stack.currentWidget() != self.grid_container:
            self._set_placeholder(None)

        # Resume deletion simulation if there are pending deletions for this batch
        self.deletion_manager.resume_deletion_simulation(batch_id)

        # Delegate incremental population to GridManager
        self.grid_manager.populate_grid_incremental(visual_images)

        # Aktifkan watchdog recovery untuk retry thumbnail yang tertinggal
        self.grid_manager.start_recovery_timer()
        
        # Start preloading burst sequence images in background
        if hasattr(self, "cache_worker") and self.cache_worker is not None:
            try:
                self.cache_worker.cancel()
                self.cache_worker.wait()
            except Exception:
                pass
        
        self.playback_cache.clear()
        
        paths = [img.path for img in images if hasattr(img, "path") and img.path]
        if paths:
            self.cache_worker = BurstCacheWorker(paths, self)
            self.cache_worker.image_cached.connect(self._on_image_pre_cached)
            self.cache_worker.start()

        self.update_save_button_state()

    @Slot()
    def clear_display(self):
        """
        Clear display ketika tidak ada batch yang dipilih.
        Reset ke state default dengan placeholder widget dan tombol "New Batch".
        """
        self.current_batch_id = None

        # Hide any active toast when batch is unselected
        self.toast.hide()

        # 0. Cancel and reset
        self._reset_population_state()

        self._update_header_title()  # Clear header title
        # self._update_cross_batch_toast()  # Check other batches
        self.logic.clear_all()
        self._clear_grid()

        # Hide import button saat no batch selected
        self.import_button.setVisible(False)
        if hasattr(self, "param_overlay"):
            self.param_overlay.hide()

        # Show "No batch selected" state with folder link callback
        self.ui_state_manager.show_no_batch_state(self._create_new_batch, self._import_images_to_new_batch)

        if self.preview_scene:
            self.preview_scene.clear()

        self.show_grid()
        self.update_save_button_state()

        pass

    def _import_images_to_new_batch(self):
        """Handle clicking the folder icon when no batch is selected. Imports images into a new batch."""
        if not self.controller or not self.right_panel:
            return

        file_filter = self.import_manager._build_file_filter()
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Select Images to Import to New Batch", "", file_filter
        )

        if not paths:
            return

        # 1. Create a new batch automatically with unique sequential name
        all_batches = self.controller.get_all_batches()
        existing_names = {b.name for b in all_batches}
        index = 1
        while f"Batch {index}" in existing_names:
            index += 1
        name = f"Batch {index}"

        batch_id = self.controller.create_batch(name)
        if batch_id:
            # 2. Select it in RightPanel list group so it loads
            self.right_panel.list_group.add_item(name, value=batch_id)
            self.right_panel.list_group.select_item_by_value(batch_id)

            # 3. Instantiate DatabaseManager and start background import process immediately
            db_mgr = DatabaseManager(self.controller.db_path)
            self.import_manager.handle_batch_import(
                controller=self.controller,
                database_manager=db_mgr,
                file_paths=paths,
                batch_id=batch_id
            )

    def _reset_population_state(self):
        """Unified method to stop all pending populating tasks and clear tracking."""
        ProcessManager.instance().cancel_context("display_populate")
        ProcessManager.instance().cancel_context("display_sequential_removal")
        self.grid_animator.stop_all()
        self.all_cards.clear()
        self.selection_manager.clear()
        self.logic.grid_items.clear()
        self.grid_manager.stop_staged_timer()  # Menghentikan staged + recovery timer

    def _show_empty_batch_state(self):
        """Delegate to UIStateManager."""
        self.ui_state_manager.show_empty_batch_state()

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
        """Delegate to GridManager."""
        self.grid_manager.clear_grid()

    def _clear_selection(self):
        """Deselect semua cards via Manager."""
        self.selection_manager.clear_selection()

    def _select_range(self, start_card_id, end_card_id):
        """Select range via Manager."""
        self.selection_manager.select_range(start_card_id, end_card_id)

    def _is_widget_in_viewport(self, widget):
        """Delegate to GridManager."""
        return self.grid_manager.is_widget_in_viewport(widget)

    def _load_thumbnail_async(self, image_path, card_widget):
        """
        Load thumbnail asinkron untuk image card dengan Viewport-Aware Animation.
        """
        self.logic.load_thumbnail_async(
            image_path, lambda img, p: self._on_thumbnail_ready(img, p, card_widget)
        )

    def _on_thumbnail_ready(self, q_image, path, card_widget):
        """Callback when thumbnail is ready, updates card directly (No Fade-In)."""
        if card_widget is not None and is_widget_alive(card_widget):
            # Kirim QImage langsung (Pixel-Perfect) guna menghindari bug gambar terpotong
            card_widget.set_image(q_image)

            # Sembunyikan progress jika sudah dimuat (mencegah double fetch)
            card_widget._is_fetching = False

    def _on_card_clicked(self, card_id, event, card_widget):
        """Handle click via Manager."""
        self.selection_manager.handle_card_clicked(card_id, event, card_widget)

    def _on_thumbnail_progress(self, batch_id, decode_pct, save_pct):
        """Update toast progress for thumbnail creation and saving."""
        # 1. ISOLASI BATCH: Hanya update jika batch_id cocok dengan tampilan aktif
        if str(batch_id) != str(self.current_batch_id):
            return

        if decode_pct >= 100 and save_pct >= 100:
            if not self._success_toast_shown:
                # Selesai: Tampilkan pesan sukses singkat
                self.toast.show_message(
                    "Semua thumbnail berhasil diproses.",
                    duration=3000,
                    position=ToastPosition.BOTTOM_RIGHT,
                    priority="NORMAL",
                    single_mode=True,  # Clear previous process status
                )
                self._success_toast_shown = True
        elif decode_pct == 0 and save_pct == 0:
            pass
        else:
            # Update progress: "Membuat X% - Menyimpan Y%"
            message = f"Membuat {decode_pct}% - Menyimpan {save_pct}%"
            self.toast.show_progress(
                message,
                position=ToastPosition.BOTTOM_RIGHT,
                priority="NORMAL",
                category="thumbnail_process",
                single_mode=True,  # FORCE SINGLE MODE to prevent chaining/stacking!
            )

    def _on_card_double_clicked(self, card_id):
        """
        Handle double-click pada image card untuk preview full resolution.

        Args:
            card_id: ID dari card yang di-click
        """
        # Better robustness: gunakan card_id untuk mencari path di logic
        if card_id in self.logic.grid_items:
            image_path = self.logic.grid_items[card_id].get("path")
            if image_path:
                self._display_image_preview(image_path)
        else:
            # Fallback (sekadar berjaga-jaga)
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
        """Delegate to SelectionManager."""
        image_path = self.selection_manager.handle_enter_press()
        if image_path:
            self._display_image_preview(image_path)

    def _navigate_selection(self, key, shift_held):
        """Navigate via Manager."""
        self.selection_manager.navigate_selection(key, shift_held)

    def contextMenuEvent(self, event):
        """Delegate to ContextMenuHandler."""
        # Only show menu if in Grid View and batch is selected
        if self.display_stack.currentIndex() != 0 or not self.current_batch_id:
            return

        # Find card under mouse
        card_under_mouse = self.context_menu_handler.find_card_under_mouse()

        # Create and show menu
        menu = self.context_menu_handler.create_context_menu(card_under_mouse)
        if not menu.isEmpty():
            menu.exec(event.globalPos())

    def _set_as_reference(self, image_path):
        """Delegate to ContextMenuHandler."""
        self.context_menu_handler.set_as_reference(image_path)

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

    def _enter_preview_mode(self):
        """Masuk ke Preview Mode: tampilkan tombol playback, sembunyikan tombol Save."""
        self.update_controls_visibility_and_states()

    def _enter_result_mode(self):
        """Masuk ke Result Mode: tampilkan tombol Save, sembunyikan tombol playback."""
        # Stop playback dulu kalau sedang berjalan
        if hasattr(self, "playback_timer") and self.playback_timer.isActive():
            self.playback_timer.stop()
            self.is_playing = False
            if hasattr(self, "play_btn"):
                self.play_btn.setText("▶")
        self.update_controls_visibility_and_states()

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

        self.logic.display_preview(self.zoomable_preview, image_path)
        self.show_preview(show_dropdown=False)
        # Masuk ke Preview Mode: tampilkan playback controls, sembunyikan Save
        self._enter_preview_mode()

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
        # Masuk ke Result Mode: sembunyikan playback controls, tampilkan Save
        self._enter_result_mode()
        self.update_save_button_state()

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
        # Stop playback if playing
        if hasattr(self, "playback_timer") and self.playback_timer.isActive():
            self.playback_timer.stop()
            self.is_playing = False
            self.play_btn.setText("▶")

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
        self.check_result_availability()  # Update preview button visibility

        if self.current_batch_id:
            self.import_button.setVisible(True)
        else:
            self.import_button.setVisible(False)
            
        self.update_controls_visibility_and_states()

    def show_preview(self, show_dropdown=True):
        """Switch ke Preview View."""
        self.display_stack.setCurrentIndex(1)
        self.back_btn.setVisible(True)
        self.result_selector.setVisible(show_dropdown)  # Only show if requested
        self.import_button.setVisible(False)
        self.preview_process_btn.setVisible(False)
        self.update_controls_visibility_and_states()

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
        """Delegate to UIStateManager."""
        self.ui_state_manager.update_header_title(
            self.current_batch_id, self.current_batch_name, count
        )

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
                        self, language_config.MSG_SUCCESS_TITLE, f"{language_config.MSG_SUCCESS_SAVE}\n{save_path}"
                    )
                except Exception as e:

                    QMessageBox.critical(self, language_config.MSG_ERROR_TITLE, f"{language_config.MSG_FAILED_SAVE_IMAGE} {e}")

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

    def _get_bulk_mode_btn_stylesheet(self, is_bulk, font_size):
        from resources.GenericUILibrary.theme import get_theme
        theme = get_theme()
        if is_bulk:
            return f"""
                QPushButton#BulkModeBtn {{
                    background-color: {theme.primary}2D;
                    color: {theme.primary};
                    border: 1px solid {theme.primary};
                    border-radius: 15px;
                    padding: 5px 15px;
                    font-size: {font_size:.1f}pt;
                    font-weight: 600;
                }}
                QPushButton#BulkModeBtn:hover {{
                    background-color: {theme.primary}4D;
                }}
                QPushButton#BulkModeBtn:pressed {{
                    background-color: {theme.primary}6D;
                }}
            """
        else:
            return f"""
                QPushButton#BulkModeBtn {{
                    background-color: {theme.bg_secondary};
                    color: {theme.text_secondary};
                    border: 1px solid {theme.border_color};
                    border-radius: 15px;
                    padding: 5px 15px;
                    font-size: {font_size:.1f}pt;
                    font-weight: 600;
                }}
                QPushButton#BulkModeBtn:hover {{
                    background-color: {theme.hover_overlay};
                }}
                QPushButton#BulkModeBtn:pressed {{
                    background-color: {theme.active_overlay};
                }}
            """

    # Overide resizeEvent untuk memastikan overlay selalu menutupi area display
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "drop_overlay"):
            self.drop_overlay.resize(self.size())
            
        if hasattr(self, "bulk_mode_btn") and self.bulk_mode_btn:
            w = self.width()
            f = max(0.0, min(1.0, (w - 600) / 800.0))
            font_size = 10.5 + f * 4.5
            self.bulk_mode_btn.setStyleSheet(self._get_bulk_mode_btn_stylesheet(self.is_bulk_mode, font_size))
            
        if hasattr(self, "param_panel"):
            self.param_panel.refresh_responsive_layout()

    def dragEnterEvent(self, event):
        """Delegate to DragDropHandler."""
        should_accept, file_count = self.drag_drop_handler.handle_drag_enter(
            event.mimeData()
        )

        if should_accept:
            event.acceptProposedAction()
            # Show overlay and update text
            self.drop_overlay.setText(f"{language_config.LBL_DRAG_DROP_HERE} ({file_count})")
            self.drop_overlay.show()
            self.drop_overlay.raise_()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_overlay.hide()
        event.accept()

    def dropEvent(self, event):
        """Delegate to DragDropHandler."""
        self.drop_overlay.hide()

        should_accept, valid_files = self.drag_drop_handler.handle_drop(
            event.mimeData()
        )

        if should_accept:
            # Emit signal for parent widget to handle
            self.images_to_import_selected.emit(valid_files)
            event.acceptProposedAction()
        else:
            event.ignore()

    def retranslate_ui(self):
        """Update all text dynamically when language changes."""
        # 1. Update Bulk Mode Button
        if hasattr(self, "bulk_mode_btn"):
            target_text = language_config.LBL_BATCH_MODE if self.is_bulk_mode else language_config.LBL_BULK_MODE
            self.bulk_mode_btn.setText(target_text)
            
        # 2. Update Header Title
        if hasattr(self, "ui_state_manager"):
            self.ui_state_manager.update_header_title(
                batch_id=self.current_batch_id,
                batch_name=self.current_batch_name,
                count=self.total_image_count
            )
            
        # 3. Update Action Buttons
        if hasattr(self, "import_button"):
            self.import_button.setText(language_config.TOPBAR_BATCH_IMPORT_BUTTON_TEXT)
        if hasattr(self, "back_btn"):
            self.back_btn.setText(language_config.BTN_BACK_TO_GRID)
        if hasattr(self, "new_batch_header_btn"):
            self.new_batch_header_btn.setText(language_config.BTN_NEW_BATCH)
            
        # 4. If placeholder is currently active, recreate it to update its HTML text
        if hasattr(self, "placeholder_widget") and self.placeholder_widget is not None:
            if not self.current_batch_id:
                # No batch selected state
                self.clear_display()
            else:
                # Empty batch state
                self.ui_state_manager.show_empty_batch_state()

    def animate_mode_change(self, is_bulk):
        """Animasi perubahan teks tombol mode secara elegan dengan efek fade."""
        # 1. Tentukan teks target
        target_text = language_config.LBL_BATCH_MODE if is_bulk else language_config.LBL_BULK_MODE
        
        # Calculate dynamic font size based on current width
        w = self.width()
        f = max(0.0, min(1.0, (w - 600) / 800.0))
        font_size = 10.5 + f * 4.5
        style_sheet = self._get_bulk_mode_btn_stylesheet(is_bulk, font_size)
            
        # 3. Setup opacity effect jika belum ada
        effect = self.bulk_mode_btn.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.bulk_mode_btn)
            self.bulk_mode_btn.setGraphicsEffect(effect)
            
        # 4. Jalankan animasi fade-out
        self._mode_fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._mode_fade_anim.setDuration(120)
        self._mode_fade_anim.setStartValue(1.0)
        self._mode_fade_anim.setEndValue(0.0)
        
        def swap_content():
            self.bulk_mode_btn.setText(target_text)
            self.bulk_mode_btn.setStyleSheet(style_sheet)
            # Jalankan animasi fade-in
            self._mode_fade_in = QPropertyAnimation(effect, b"opacity", self)
            self._mode_fade_in.setDuration(120)
            self._mode_fade_in.setStartValue(0.0)
            self._mode_fade_in.setEndValue(1.0)
            self._mode_fade_in.start()
            
        self._mode_fade_anim.finished.connect(swap_content)
        self._mode_fade_anim.start()

    def _on_image_pre_cached(self, path, q_image):
        """Callback when an image is successfully pre-loaded and decoded in the background."""
        pixmap = QPixmap.fromImage(q_image)
        self.playback_cache[path] = pixmap

    def _start_background_preload(self, batch_id):
        """
        Dipanggil otomatis setelah import batch selesai (import_manager.import_finished).

        Meluncurkan BackgroundBatchPreloader pada prioritas terendah untuk memuat
        semua thumbnail batch ke GlobalThumbnailCache diam-diam di background.
        Hasilnya: saat user mengklik batch tersebut, thumbnail sudah di RAM — instan.

        Maks 1 preloader per batch_id. Jika preloader sebelumnya masih berjalan, ia di-cancel
        dulu sebelum preloader baru dimulai (karena gambar mungkin berubah).
        """
        try:
            batch_id_str = str(batch_id)

            # Hentikan preloader lama jika masih berjalan
            old_preloader = self._bg_preloaders.pop(batch_id_str, None)
            if old_preloader is not None:
                old_preloader.cancel()
                # Tidak perlu wait() — thread berjalan di LowestPriority, biarkan selesai sendiri

            # Ambil semua path gambar untuk batch ini
            paths = []
            try:
                if hasattr(self, "controller") and self.controller:
                    images = self.controller.get_images(batch_id)
                    paths = [img.path for img in images if hasattr(img, "path") and img.path]
            except Exception:
                pass

            if not paths:
                return

            # Buat dan mulai preloader baru
            preloader = BackgroundBatchPreloader(batch_id_str, paths, self)
            preloader.thumbnail_preloaded.connect(self._on_bg_thumbnail_preloaded)
            preloader.finished.connect(
                lambda bid=batch_id_str: self._bg_preloaders.pop(bid, None)
            )
            self._bg_preloaders[batch_id_str] = preloader
            preloader.start()
            print(f"[BackgroundPreloader] Started for batch {batch_id_str} ({len(paths)} images)")
        except Exception as e:
            print(f"[BackgroundPreloader] Error starting for batch {batch_id}: {e}")

    def _on_bg_thumbnail_preloaded(self, batch_id: str, image_path: str):
        """
        Dipanggil saat satu thumbnail berhasil di-preload ke GlobalThumbnailCache.
        Jika batch ini sedang aktif ditampilkan, update card-nya secara langsung.
        """
        if str(batch_id) != str(self.current_batch_id):
            return  # Batch tidak aktif, cukup cache di L0 — tidak perlu update UI

        # Cari card yang sesuai dan update thumbnail-nya jika belum ter-load
        for card_id, card in self.all_cards.items():
            try:
                if hasattr(card, "_image_path") and card._image_path == image_path:
                    if not card.has_thumbnail():
                        from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import get_global_cache
                        q_img = get_global_cache().get(image_path)
                        if q_img and not q_img.isNull():
                            card.set_thumbnail(QPixmap.fromImage(q_img))
                    break
            except Exception:
                pass

    def _toggle_playback(self):
        """Toggle play/pause state for preview burst sequence."""
        if not hasattr(self, "playback_timer"):
            self.playback_timer = QTimer(self)
            self.playback_timer.setInterval(120)  # ~8 FPS (120ms interval)
            self.playback_timer.timeout.connect(self._show_next_frame)
            self.is_playing = False

        if self.is_playing:
            self.playback_timer.stop()
            self.play_btn.setText("▶")
            self.is_playing = False
        else:
            self.playback_timer.start()
            self.play_btn.setText("⏸")
            self.is_playing = True
        self.update_controls_visibility_and_states()

    def _get_current_image_index(self):
        """Get the index of the currently shown preview image in the batch list."""
        if not self.logic.current_images or not hasattr(self, "current_preview_path") or not self.current_preview_path:
            return 0
        
        for i, img in enumerate(self.logic.current_images):
            if os.path.normpath(img.path) == os.path.normpath(self.current_preview_path):
                return i
        return 0

    def _show_next_frame(self):
        """Show the next frame in the burst sequence."""
        if not self.logic.current_images:
            return
        current_idx = self._get_current_image_index()
        next_idx = (current_idx + 1) % len(self.logic.current_images)
        next_path = self.logic.current_images[next_idx].path
        self._display_fast_preview(next_path)

    def _show_prev_frame(self):
        """Show the previous frame in the burst sequence."""
        if not self.logic.current_images:
            return
        current_idx = self._get_current_image_index()
        prev_idx = (current_idx - 1) % len(self.logic.current_images)
        prev_path = self.logic.current_images[prev_idx].path
        self._display_fast_preview(prev_path)

    def _display_fast_preview(self, image_path):
        """High-efficiency loader specifically for burst previews using preloaded cache or Hamilton Adams half-res demosaicing."""
        if not self.logic.prepare_preview(image_path):
            return
            
        self.current_preview_path = image_path
        
        # Stop previous loader thread
        if self.logic.image_loader_thread and self.logic.image_loader_thread.isRunning():
            self.logic.image_loader_thread.quit()
            self.logic.image_loader_thread.wait()
            
        # Check if we have preloaded cache for zero-flicker instant rendering
        if image_path in self.playback_cache:
            pixmap = self.playback_cache[image_path]
            self.preview_scene.clear()
            
            # Create and add pixmap item
            pixmap_item = QGraphicsPixmapItem(pixmap)
            pixmap_item.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
            self.preview_scene.addItem(pixmap_item)
            
            # Set scene rect
            self.preview_scene.setSceneRect(pixmap_item.boundingRect())
            
            # Fit in view
            self.zoomable_preview.fitInView(
                self.preview_scene.itemsBoundingRect(), Qt.AspectRatioMode.KeepAspectRatio
            )
        else:
            # Fallback loader
            from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import display_image_in_zoomable
            self.logic.image_loader_thread = display_image_in_zoomable(
                self.zoomable_preview, image_path, half_res=True
            )
            
        self.show_preview(show_dropdown=False)
        # Burst/frame preview selalu masuk Preview Mode
        self._enter_preview_mode()

    def set_start_button_mode(self, active: bool):
        self.is_start_button_mode = active
        self.update_controls_visibility_and_states()

    def update_save_button_state(self):
        self.update_controls_visibility_and_states()

    def update_controls_visibility_and_states(self):
        if not hasattr(self, "start_btn_ref"):
            return

        is_grid = (self.display_stack.currentIndex() == 0)

        # Dynamic styling for controls_bar based on whether we are in preview or grid/thumbnail mode
        if hasattr(self, "controls_bar"):
            if is_grid:
                self.controls_bar.setStyleSheet("""
                    #ControlsBar {
                        background-color: transparent;
                        border: none;
                    }
                """)
            else:
                self.controls_bar.setStyleSheet("""
                    #ControlsBar {
                        background-color: rgba(255, 255, 255, 220);
                        border: 1px solid rgba(0, 0, 0, 40);
                        border-radius: 8px;
                    }
                """)

        # 1. Start button visibility and enabled state
        if self.is_start_button_mode:
            self.start_btn_ref.setVisible(True)
            is_playing = hasattr(self, "is_playing") and self.is_playing
            self.start_btn_ref.setEnabled(not is_playing)
        else:
            self.start_btn_ref.setVisible(False)

        # 2. Play buttons visibility (⏮, ▶, ⏭) (controlled via container for proper collapse)
        show_playback = not is_grid
        if hasattr(self, "playback_container"):
            self.playback_container.setVisible(show_playback)

        # 3. Save button visibility and state
        has_results = False
        if self.logic.current_images:
            first_img_path = self.logic.current_images[0].path
            results = self.logic.detect_processed_results(first_img_path)
            if results:
                has_results = True

        if has_results:
            self.save_btn_ref.setEnabled(True)
            self.save_btn_ref.setStyleSheet("""
                QPushButton {
                    background-color: #555555;
                    color: #FFFFFF;
                    border: 1px solid #333333;
                    border-radius: 4px;
                    font-weight: bold;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #666666;
                }
                QPushButton:pressed {
                    background-color: #444444;
                }
            """)
            self.save_btn_ref.setVisible(not is_grid)
            if not is_grid and self.display_stack.currentIndex() == 1:
                # If we are in preview view and has_results, ensure we trigger result mode internally
                pass
        else:
            self.save_btn_ref.setEnabled(False)
            self.save_btn_ref.setStyleSheet("""
                QPushButton {
                    background-color: #D3D3D3;
                    color: #888888;
                    border: 1px solid #C0C0C0;
                    border-radius: 4px;
                    padding: 5px;
                }
            """)
            self.save_btn_ref.setVisible(False)

        # 4. Overall overlay visibility
        if hasattr(self, "controls_overlay"):
            if self.is_start_button_mode or not is_grid:
                self.controls_overlay.show()
                self.controls_bar.adjustSize()
                self.controls_overlay.adjustSize()
                self.controls_overlay._update_position()
                self.controls_overlay.raise_()
            else:
                self.controls_overlay.hide()
