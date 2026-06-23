"""
WorkspaceDisplayPanel - General Display Panel
===============================================
Clone dari enhance_stack DisplayPanel UI shell.
Seluruh layout, widget, animasi, dan struktur UI di-clone tanpa logic spesifik.

UI yang di-clone:
- 3-kolom header (sidebar toggle, title, mode toggle, action buttons)
- Content stack (Grid View, Preview View, Delete Confirmation)
- GridContainer responsive dengan lazy loading support
- Zoomable preview dengan floating playback controls bar
- Drop overlay (drag & drop)
- Sidebar overlay (floating navigation)
- Settings overlay (centered modal)
- Toast manager
- Bulk mode animated button
"""

from __future__ import annotations
import os
import shutil

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
    QSizePolicy,
    QPushButton,
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
from typing import Optional, Any
from PySide6.QtGui import QPixmap, QColor, QAction, QImage

from resources.GenericUILibrary import (
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
from resources.animations.fade import fade_out, fade_in
from resources.animations.toast.toast_manager import (
    ToastManager,
    ToastPosition,
    ToastAnimation,
)
from pixel_refine_desktop.ui.components.common.sidebar import Sidebar


class WorkspaceDisplayPanel(QWidget):
    """
    General display panel - UI clone dari enhance_stack DisplayPanel.

    Menyediakan seluruh UI shell (header, grid, preview, playback, sidebar,
    overlays, toast) tanpa logic spesifik. Logic bisa di-inject nanti.

    Layout Structure:
    ┌──────────────────────────────────────────────┐
    │  DisplayContainer                            │
    │  ┌────────────────────────────────────────┐  │
    │  │ Header (3-kolom)                       │  │
    │  │ [☰] Title        [Mode]    [Actions]   │  │
    │  ├────────────────────────────────────────┤  │
    │  │ Content Stack                          │  │
    │  │ Index 0: Grid View                     │  │
    │  │ Index 1: Preview View (Zoomable)       │  │
    │  │ Index 2: Delete Confirmation           │  │
    │  └────────────────────────────────────────┘  │
    │  Overlay Layer:                              │
    │  - Drop Overlay (drag & drop)               │
    │  - Controls Overlay (playback buttons)       │
    │  - Sidebar Overlay (floating nav)            │
    │  - Settings Overlay (centered modal)         │
    └──────────────────────────────────────────────┘
    """

    # Signals
    images_to_import_selected = Signal(list)
    page_changed = Signal(int)

    def __init__(self, controller=None):
        super().__init__()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 8, 0, 5)

        # Internal Container
        self.display_container = Container(padding=5)
        self.display_container.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground, True
        )
        self.display_container.setObjectName("DisplayContainerBase")

        self.controller = controller

        # State
        self.current_batch_id = None
        self.current_batch_name = None
        self.total_image_count = 0
        self.all_cards = {}
        self.placeholder_widget = None
        self.right_panel = None

        # Toast
        self.toast = ToastManager(self)

        # Sidebar references (akan di-setup di _setup_sidebar)
        self.sidebar = None
        self.sidebar_overlay = None
        self.settings_overlay = None
        self.settings_view = None

        # Playback state
        self.is_playing = False
        self.playback_timer = None
        self.playback_cache = {}
        self.current_preview_path = None
        self.is_bulk_mode = False
        self.is_start_button_mode = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._setup_ui()
        self._setup_sidebar()
        self.setAcceptDrops(True)
        self.clear_display()

    # =========================================================================
    # === UI SETUP (CLONED FROM DisplayPanel) ===
    # =========================================================================

    def _setup_ui(self):
        """Setup UI dengan stacked widget untuk grid dan preview mode."""
        self.display_container.main_layout.setContentsMargins(0, 0, 0, 0)
        self.display_container.main_layout.setSpacing(0)

        # Drop Overlay
        self.drop_overlay = QLabel(self)
        self.drop_overlay.setObjectName("DropOverlay")
        self.drop_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_overlay.setHidden(True)
        self.drop_overlay.setStyleSheet("""
            #DropOverlay {
                background-color: rgba(46, 204, 113, 180);
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 10px;
                margin: 20px;
            }
        """)

        # === SHARED HEADER ===
        self._setup_header()

        # === CONTENT STACK ===
        self.display_stack = QStackedWidget()
        self.display_stack.setContentsMargins(10, 10, 10, 10)
        self.display_stack.setStyleSheet(
            "background-color: transparent; border-radius: 2px;"
        )

        # Index 0: Grid View
        self._setup_grid_view()

        # Index 1: Preview View
        self._setup_preview_view()

        # Index 2: Delete Confirmation Placeholder
        self._setup_delete_confirmation_placeholder()

        # Add Stack to Container
        self.display_container.add_widget(self.display_stack)

        # Add Container to Main Layout
        self.main_layout.addWidget(self.display_container)

    def _setup_header(self):
        """Setup 3-kolom header (cloned dari DisplayPanel)."""
        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(10, 5, 10, 0)
        self.header_layout.setSpacing(0)

        # Left Column: Sidebar toggle + Title
        self.left_header_layout = QHBoxLayout()
        self.left_header_layout.setContentsMargins(0, 0, 0, 0)
        self.left_header_layout.setSpacing(10)
        self.left_header_layout.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.toggle_btn = Button("☰", object_name="SidebarToggleBtn")
        self.toggle_btn.setFixedWidth(40)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.left_header_layout.addWidget(self.toggle_btn)

        self.header_title = QLabel("")
        self.header_title.setObjectName("DisplayHeaderTitle")
        self.left_header_layout.addWidget(self.header_title)

        # Center Column: Bulk Mode Dynamic Button
        self.center_header_layout = QHBoxLayout()
        self.center_header_layout.setContentsMargins(0, 0, 0, 0)
        self.center_header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.bulk_mode_btn = QPushButton("Batch Mode", self)
        self.bulk_mode_btn.setObjectName("BulkModeBtn")
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
        opacity_effect = QGraphicsOpacityEffect(self.bulk_mode_btn)
        self.bulk_mode_btn.setGraphicsEffect(opacity_effect)
        self.center_header_layout.addWidget(self.bulk_mode_btn)

        # Right Column: Action Buttons
        self.right_header_layout = QHBoxLayout()
        self.right_header_layout.setContentsMargins(0, 0, 0, 0)
        self.right_header_layout.setSpacing(10)
        self.right_header_layout.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # Result Dropdown
        self.result_selector = QComboBox()
        self.result_selector.setFixedWidth(100)
        self.result_selector.setStyleSheet("""
            QComboBox {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 4px 8px;
                color: #333333;
            }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #666666;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF; color: #333333;
                selection-background-color: #E0E0E0; selection-color: #000000;
            }
        """)
        self.result_selector.setVisible(False)
        self.right_header_layout.addWidget(self.result_selector)

        # Back to Grid Button
        self.back_btn = Button("Back to Grid", variant="secondary")
        self.back_btn.setFixedWidth(120)
        self.back_btn.clicked.connect(self.show_grid)
        self.back_btn.setVisible(False)
        self.right_header_layout.addWidget(self.back_btn)

        # Preview Process Button
        self.preview_process_btn = IconButton(
            icon_path="resources/assets/icons/play-preview.png",
            variant="primary",
        )
        self.preview_process_btn.setToolTip("Image Process")
        self.preview_process_btn.setFixedWidth(40)
        self.preview_process_btn.setVisible(False)
        self.right_header_layout.addWidget(self.preview_process_btn)

        # Import Button
        self.import_button = Button("Import", object_name="ImportImageBtn")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self._on_import_clicked)
        self.import_button.setVisible(False)
        self.right_header_layout.addWidget(self.import_button)

        # New Batch button (shown ONLY when no batches exist)
        self.new_batch_header_btn = Button("New Batch", variant="primary")
        self.new_batch_header_btn.setFixedWidth(110)
        self.new_batch_header_btn.setFixedHeight(25)
        self.new_batch_header_btn.setStyleSheet(
            self.new_batch_header_btn.styleSheet()
            + " QPushButton { padding: 4px 8px; font-size: 8pt; }"
        )
        self.new_batch_header_btn.setVisible(False)
        self.right_header_layout.addWidget(self.new_batch_header_btn)

        # Assemble header (1, 1, 1 stretch for center alignment)
        self.header_layout.addLayout(self.left_header_layout, 1)
        self.header_layout.addLayout(self.center_header_layout, 1)
        self.header_layout.addLayout(self.right_header_layout, 1)

        self.display_container.add_layout(self.header_layout)

    def _setup_grid_view(self):
        """Setup grid view dengan responsive GridContainer."""
        self.grid_view_widget = QWidget()
        self.grid_view_widget.setStyleSheet(
            "background-color: transparent; border-radius: 4px;"
        )
        grid_view_layout = QVBoxLayout(self.grid_view_widget)
        grid_view_layout.setContentsMargins(0, 0, 0, 0)
        grid_view_layout.setSpacing(0)

        # Content Stack: GridContainer vs Placeholder
        self.grid_content_stack = QStackedWidget()
        self.grid_animator = StackedWidgetAnimator(self.grid_content_stack)

        grid_view_layout.addWidget(self.grid_content_stack, 1)

        # GridContainer responsive
        self.grid_container = GridContainer(
            item_width=110, spacing=10,
            wrap_mode="vertical", column_mode="responsive",
        )
        self.grid_container.setStyleSheet("QScrollArea { border: none; }")

        self.grid_content_stack.addWidget(self.grid_container)
        self.display_stack.addWidget(self.grid_view_widget)

    def _setup_preview_view(self):
        """Setup preview view dengan Zoomable dan floating controls."""
        preview_wrapper = QWidget()
        preview_wrapper_layout = QVBoxLayout(preview_wrapper)
        preview_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        preview_wrapper_layout.setSpacing(10)

        # Zoomable Preview
        self.preview_scene = QGraphicsScene()
        # Placeholder: subclass akan inject Zoomable viewer di sini
        self.zoomable_preview = QWidget()  # Placeholder
        preview_wrapper_layout.addWidget(self.zoomable_preview)

        # Playback Controls Bar (floating)
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
        self.controls_bar.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        # Playback buttons
        self.prev_frame_btn = QPushButton("⏮")
        self.prev_frame_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; font-size: 18px; padding: 4px 6px; }
            QPushButton:hover { background-color: rgba(0, 0, 0, 15); border-radius: 6px; }
        """)
        self.prev_frame_btn.setFixedSize(36, 36)

        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; font-size: 18px; padding: 4px 6px; }
            QPushButton:hover { background-color: rgba(0, 0, 0, 15); border-radius: 6px; }
        """)
        self.play_btn.setFixedSize(36, 36)

        self.next_frame_btn = QPushButton("⏭")
        self.next_frame_btn.setStyleSheet("""
            QPushButton { background: transparent; border: none; font-size: 18px; padding: 4px 6px; }
            QPushButton:hover { background-color: rgba(0, 0, 0, 15); border-radius: 6px; }
        """)
        self.next_frame_btn.setFixedSize(36, 36)

        # Playback container
        self.playback_container = QWidget()
        self.playback_container.setStyleSheet("background: transparent;")
        playback_layout = QHBoxLayout(self.playback_container)
        playback_layout.setContentsMargins(0, 0, 0, 0)
        playback_layout.setSpacing(4)
        playback_layout.addWidget(self.prev_frame_btn)
        playback_layout.addWidget(self.play_btn)
        playback_layout.addWidget(self.next_frame_btn)

        self.controls_bar_layout.addWidget(self.playback_container)

        # Start Button
        self.start_btn_ref = Button("▶ Start", variant="primary")
        self.start_btn_ref.setFixedSize(110, 32)
        self.start_btn_ref.setVisible(False)
        self.controls_bar_layout.addWidget(self.start_btn_ref)

        # Save Button
        self.save_btn_ref = Button("Save", variant="secondary")
        self.save_btn_ref.setFixedSize(80, 32)
        self.controls_bar_layout.addWidget(self.save_btn_ref)

        # Controls Overlay
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

    def _setup_delete_confirmation_placeholder(self):
        """Setup delete confirmation placeholder. Subclass bisa override."""
        self.delete_confirmation_widget = QWidget()
        delete_layout = QVBoxLayout(self.delete_confirmation_widget)
        delete_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        placeholder_label = QLabel("Confirm Deletion")
        placeholder_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        delete_layout.addWidget(placeholder_label)

        self.display_stack.addWidget(self.delete_confirmation_widget)

    def _setup_sidebar(self):
        """Initialize floating sidebar."""
        pages = [
            ("Workspace", "resources/assets/icons/enhance_stack.png"),
            ("Settings", "resources/assets/icons/setting.png"),
        ]

        self.sidebar = Sidebar(pages=pages, parent=self)
        self.sidebar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.sidebar.page_changed.connect(self._handle_sidebar_navigation)

        self.sidebar_overlay = OverlayContainer(
            parent=self.display_container,
            position=OverlayPosition.TOP_LEFT,
            margin=5,
            smart_positioning=False,
            close_on_click_outside=True,
            shadow_enabled=True,
            shadow_blur_radius=20,
            shadow_offset=QPoint(4, 4),
            shadow_color=QColor(0, 0, 0, 80),
        )
        self.sidebar_overlay.set_content(self.sidebar)
        self.sidebar_overlay.hide()

        self.sidebar.set_current_page(0)

    # =========================================================================
    # === COMMON UI METHODS ===
    # =========================================================================

    def set_header_title(self, text: str):
        """Sets the text of the header title."""
        self.header_title.setText(text)

    def show_grid(self):
        """Switch ke Grid View."""
        if hasattr(self, "playback_timer") and self.playback_timer and self.playback_timer.isActive():
            self.playback_timer.stop()
            self.is_playing = False
            self.play_btn.setText("▶")

        self.display_stack.setCurrentIndex(0)
        self.back_btn.setVisible(False)
        self.result_selector.setVisible(False)

        if self.current_batch_id:
            self.import_button.setVisible(True)
        else:
            self.import_button.setVisible(False)

        self.update_controls_visibility_and_states()

    def show_preview(self, show_dropdown=True):
        """Switch ke Preview View."""
        self.display_stack.setCurrentIndex(1)
        self.back_btn.setVisible(True)
        self.result_selector.setVisible(show_dropdown)
        self.import_button.setVisible(False)
        self.preview_process_btn.setVisible(False)
        self.update_controls_visibility_and_states()

    def clear_display(self):
        """Clear display ke empty state. Subclass HARUS implement logic-nya."""
        self.current_batch_id = None
        self.current_batch_name = None
        self.total_image_count = 0
        self.set_header_title("")
        self.import_button.setVisible(False)
        self.show_grid()

    def toggle_sidebar(self):
        """Toggle floating sidebar visibility."""
        if self.sidebar_overlay:
            is_visible = self.sidebar_overlay.isVisible()
            if is_visible:
                self.sidebar_overlay.hide()
            else:
                self.sidebar_overlay.show()
                self.sidebar_overlay.raise_()

    def _handle_sidebar_navigation(self, index: int):
        """Handle navigation dari sidebar. Subclass BISA override."""
        if index == 1:  # Settings
            self.show_settings()
            self.sidebar_overlay.hide()
            self.sidebar.set_current_page(0)
        elif index == 0:
            self.page_changed.emit(index)
            self.sidebar_overlay.hide()

    def show_settings(self):
        """Show settings overlay. Subclass BISA override untuk custom settings view."""
        if self.settings_overlay:
            top_window = self.window()
            if top_window and top_window != self:
                if self.settings_overlay.parent() != top_window:
                    self.settings_overlay.setParent(top_window)
                    self.settings_overlay.resize(top_window.size())
                    self.settings_overlay.move(0, 0)
            self.settings_overlay.show()
            self.settings_overlay.raise_()

    def _on_import_clicked(self):
        """Handle import button click. Subclass HARUS implement file filter."""
        file_filter = self._get_import_filter()
        paths, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", file_filter)
        if paths:
            self.images_to_import_selected.emit(paths)

    def _get_import_filter(self) -> str:
        """Return file dialog filter. Subclass HARUS override."""
        return "All Files (*)"

    def animate_mode_change(self, is_bulk):
        """Animasi perubahan teks bulk mode button."""
        target_text = "Batch Mode" if is_bulk else "Bulk Mode"

        w = self.width()
        f = max(0.0, min(1.0, (w - 600) / 800.0))
        font_size = 10.5 + f * 4.5
        style_sheet = self._get_bulk_mode_btn_stylesheet(is_bulk, font_size)

        effect = self.bulk_mode_btn.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect(self.bulk_mode_btn)
            self.bulk_mode_btn.setGraphicsEffect(effect)

        self._mode_fade_anim = QPropertyAnimation(effect, b"opacity", self)
        self._mode_fade_anim.setDuration(120)
        self._mode_fade_anim.setStartValue(1.0)
        self._mode_fade_anim.setEndValue(0.0)

        def swap_content():
            self.bulk_mode_btn.setText(target_text)
            self.bulk_mode_btn.setStyleSheet(style_sheet)
            self._mode_fade_in = QPropertyAnimation(effect, b"opacity", self)
            self._mode_fade_in.setDuration(120)
            self._mode_fade_in.setStartValue(0.0)
            self._mode_fade_in.setEndValue(1.0)
            self._mode_fade_in.start()

        self._mode_fade_anim.finished.connect(swap_content)
        self._mode_fade_anim.start()

    def _get_bulk_mode_btn_stylesheet(self, is_bulk, font_size):
        """Generate stylesheet untuk bulk mode button."""
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
            """

    def update_controls_visibility_and_states(self):
        """Update visibility playback controls, save, start buttons."""
        if not hasattr(self, "start_btn_ref"):
            return

        is_grid = (self.display_stack.currentIndex() == 0)

        if hasattr(self, "controls_bar"):
            if is_grid:
                self.controls_bar.setStyleSheet("""
                    #ControlsBar { background-color: transparent; border: none; }
                """)
            else:
                self.controls_bar.setStyleSheet("""
                    #ControlsBar {
                        background-color: rgba(255, 255, 255, 220);
                        border: 1px solid rgba(0, 0, 0, 40);
                        border-radius: 8px;
                    }
                """)

        if self.is_start_button_mode:
            self.start_btn_ref.setVisible(True)
            is_playing = hasattr(self, "is_playing") and self.is_playing
            self.start_btn_ref.setEnabled(not is_playing)
        else:
            self.start_btn_ref.setVisible(False)

        show_playback = not is_grid
        if hasattr(self, "playback_container"):
            self.playback_container.setVisible(show_playback)

        self.save_btn_ref.setVisible(not is_grid)

        if hasattr(self, "controls_overlay"):
            if self.is_start_button_mode or not is_grid:
                self.controls_overlay.show()
                self.controls_bar.adjustSize()
                self.controls_overlay.adjustSize()
                self.controls_overlay._update_position()
                self.controls_overlay.raise_()
            else:
                self.controls_overlay.hide()

    # =========================================================================
    # === DRAG & DROP (Generic) ===
    # =========================================================================

    def dragEnterEvent(self, event):
        """Handle drag enter."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_count = len([u for u in urls if u.toLocalFile()])
            if file_count > 0:
                event.acceptProposedAction()
                self.drop_overlay.setText(f"Drop files here ({file_count})")
                self.drop_overlay.show()
                self.drop_overlay.raise_()
                return
        event.ignore()

    def dragLeaveEvent(self, event):
        self.drop_overlay.hide()
        event.accept()

    def dropEvent(self, event):
        """Handle drop."""
        self.drop_overlay.hide()
        if event.mimeData().hasUrls():
            valid_files = [
                u.toLocalFile()
                for u in event.mimeData().urls()
                if u.toLocalFile() and os.path.isfile(u.toLocalFile())
            ]
            if valid_files:
                self.images_to_import_selected.emit(valid_files)
                event.acceptProposedAction()
                return
        event.ignore()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "drop_overlay"):
            self.drop_overlay.resize(self.size())
        if hasattr(self, "bulk_mode_btn") and self.bulk_mode_btn:
            w = self.width()
            f = max(0.0, min(1.0, (w - 600) / 800.0))
            font_size = 10.5 + f * 4.5
            self.bulk_mode_btn.setStyleSheet(
                self._get_bulk_mode_btn_stylesheet(self.is_bulk_mode, font_size)
            )

    # =========================================================================
    # === RETRANSLATE ===
    # =========================================================================

    def retranslate_ui(self):
        """Update semua teks saat language berubah. Subclass BISA override."""
        if hasattr(self, "bulk_mode_btn"):
            self.bulk_mode_btn.setText(
                "Batch Mode" if self.is_bulk_mode else "Bulk Mode"
            )
        if hasattr(self, "import_button"):
            self.import_button.setText("Import")
        if hasattr(self, "back_btn"):
            self.back_btn.setText("Back to Grid")
        if hasattr(self, "new_batch_header_btn"):
            self.new_batch_header_btn.setText("New Batch")
