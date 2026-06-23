"""
WorkspaceRightPanel - General Right Panel
==========================================
Clone dari enhance_stack RightPanel UI shell.
Seluruh layout, widget, animasi, dan struktur UI di-clone tanpa logic spesifik.

UI yang di-clone:
- QSplitter vertikal (item list atas + settings container bawah)
- Action buttons (New + Delete)
- ListGroup dengan reordering, rename, context menu
- Settings container dengan QScrollArea
- Process All button di bawah splitter
- Collapse state management
- Height animator
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSplitter,
    QScrollArea,
    QMenu,
)
from PySide6.QtCore import Signal, Qt, QTimer

from resources.GenericUILibrary import (
    ListGroup,
    Button,
)
from resources.animations.animation_manager import HeightAnimator


class WorkspaceRightPanel(QWidget):
    """
    General right panel - UI clone dari enhance_stack RightPanel.

    Menyediakan seluruh UI shell (splitter, list, settings container,
    process all button) tanpa logic spesifik. Logic bisa di-inject nanti.

    Layout Structure:
    ┌──────────────────────────────┐
    │  [+] [Delete]   Actions     │
    ├──────────────────────────────┤
    │  ┌────────────────────────┐  │
    │  │  ListGroup             │  │ ← Top: Item list
    │  │  (reordering, rename)  │  │
    │  ├────────────────────────┤  │
    │  │  Settings Container    │  │ ← Bottom: Settings cards
    │  │  (injectable content)  │  │
    │  └────────────────────────┘  │
    ├──────────────────────────────┤
    │  [Process All]               │
    └──────────────────────────────┘
    """

    # Signals
    item_selected = Signal(int)
    selection_cleared = Signal()
    settings_changed = Signal(dict)

    def __init__(self, controller=None, left_panel=None, store=None):
        super().__init__()
        self.controller = controller
        self.left_panel = left_panel
        self.store = store
        self.current_item_id = None
        self._is_collapsed = True
        self._move_mode = False
        self.height_animator = HeightAnimator(self)

        # Debounce timer
        self._selection_timer = QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(self._do_handle_selection)
        self._pending_selection = None

        self._setup_ui()

    def _setup_ui(self):
        """Setup UI layout (cloned dari RightPanel)."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(10)
        self.splitter.setStyleSheet(
            "QSplitter::handle { background-color: #e0e0e0; border-radius: 2px; }"
        )

        # === ITEM CONTAINER (Top) ===
        self.item_container = QWidget()
        item_layout = QVBoxLayout(self.item_container)
        item_layout.setContentsMargins(0, 0, 0, 10)
        item_layout.setSpacing(10)

        # Action Buttons
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)

        self.new_btn = Button("New", variant="primary")
        self.new_btn.setFixedHeight(22)
        self.new_btn.setStyleSheet(
            self.new_btn.styleSheet()
            + " QPushButton { padding: 2px 4px; font-size: 8pt; }"
        )
        self.new_btn.clicked.connect(self._on_create_clicked)
        action_layout.addWidget(self.new_btn, 1)

        self.del_btn = Button("Delete", variant="danger")
        self.del_btn.setFixedHeight(22)
        self.del_btn.setStyleSheet(
            self.del_btn.styleSheet()
            + " QPushButton { padding: 2px 4px; font-size: 8pt; }"
        )
        self.del_btn.clicked.connect(self._on_delete_clicked)
        action_layout.addWidget(self.del_btn, 1)

        item_layout.addLayout(action_layout)

        # ListGroup
        self.list_group = ListGroup(reordering=True)
        self.list_group.selection_changed.connect(self._on_selection_changed_debounced)
        self.list_group.item_renamed.connect(self._on_item_renamed_wrapper)
        self.list_group.delete_key_pressed.connect(self._on_delete_clicked)
        self.list_group.items_reordered.connect(self._on_items_reordered_wrapper)
        self.list_group.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_group.customContextMenuRequested.connect(self._show_context_menu)
        item_layout.addWidget(self.list_group)

        # === SETTINGS CONTAINER (Bottom) ===
        self.settings_container = QWidget()
        settings_layout = QVBoxLayout(self.settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(5)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 5, 0, 5)
        self.scroll_content_layout.setSpacing(10)

        # === INJECTION POINT: Subclass populates settings here ===
        self._populate_settings()
        self.scroll_content_layout.addStretch()

        self.scroll_area.setWidget(self.scroll_content)
        settings_layout.addWidget(self.scroll_area)

        # Add to splitter
        self.splitter.addWidget(self.item_container)
        self.splitter.addWidget(self.settings_container)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        main_layout.addWidget(self.splitter)

        # === PROCESS ALL BUTTON ===
        self.process_all_btn = Button("Process All", variant="primary")
        self.process_all_btn.setFixedHeight(22)
        self.process_all_btn.setStyleSheet(
            self.process_all_btn.styleSheet()
            + " QPushButton { padding: 2px 4px; font-size: 8pt; }"
        )
        self.process_all_btn.clicked.connect(self._on_process_all_clicked)
        main_layout.addWidget(self.process_all_btn)

        # Hide settings container initially
        self.settings_container.setFixedHeight(0)
        self.settings_container.hide()

    # =========================================================================
    # === INJECTION POINTS (Subclass override untuk isi konten) ===
    # =========================================================================

    def _populate_settings(self):
        """
        Populasi settings area dengan module-specific widgets.
        Subclass HARUS override untuk menambahkan FeatureCards, FormGroups, dll.

        Contoh:
            self.card_a = FeatureCard("TITLE", "desc", options, default, self)
            self.scroll_content_layout.addWidget(self.card_a)
        """
        # Placeholder label
        placeholder = QLabel("Settings will appear here")
        placeholder.setStyleSheet("color: #999; font-style: italic;")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_content_layout.addWidget(placeholder)

    def _load_items(self):
        """Load items dari controller/database ke ListGroup. Subclass HARUS override."""
        pass

    # =========================================================================
    # === EVENT HANDLERS (Generic UI behavior) ===
    # =========================================================================

    def _on_selection_changed_debounced(self, selected_values):
        """Buffer selection change untuk prevent UI lag."""
        self._pending_selection = selected_values
        self._selection_timer.start(150)

    def _do_handle_selection(self):
        """Delegate handling ke selection handler."""
        if self._pending_selection is None:
            return
        selected_values = self._pending_selection
        self._pending_selection = None

        if not selected_values:
            self.selection_cleared.emit()
            self.settings_container.setFixedHeight(0)
            self.settings_container.hide()
            return

        item_id = selected_values[0]
        self.current_item_id = item_id

        # Show settings container dengan animasi
        self.settings_container.show()
        target_h = self._calculate_settings_target_h()
        self.settings_container.setFixedHeight(target_h)

        self.item_selected.emit(item_id)

    def _on_create_clicked(self):
        """Handle create button. Subclass BISA override."""
        pass

    def _on_delete_clicked(self):
        """Handle delete button. Subclass BISA override."""
        selected_ids = self.list_group.get_selected_values()
        if not selected_ids:
            return
        # Subclass handles actual deletion

    def _on_item_renamed_wrapper(self, item_id, new_name):
        """Handle item rename dari ListGroup."""
        pass

    def _on_items_reordered_wrapper(self, item_ids, direction=None, start_idx=-1, target_idx=-1):
        """Handle reordering dari ListGroup."""
        pass

    def _on_process_all_clicked(self):
        """Handle process all button. Subclass BISA override."""
        pass

    def _show_context_menu(self, pos):
        """Show context menu untuk item."""
        if not self.list_group.get_selected_values():
            return

        menu = QMenu(self)
        move_act = menu.addAction("Move item")
        move_act.setCheckable(True)
        move_act.setChecked(self.list_group._move_mode)
        move_act.triggered.connect(self._toggle_move_mode)

        menu.addSeparator()
        del_act = menu.addAction("Delete Item")
        del_act.triggered.connect(self._on_delete_clicked)

        menu.exec_(self.list_group.mapToGlobal(pos))

    def _toggle_move_mode(self):
        self._move_mode = not self.list_group._move_mode
        self.list_group.set_move_mode(self._move_mode)

    # =========================================================================
    # === COLLAPSE MANAGEMENT ===
    # =========================================================================

    def set_collapsed_state(self, collapsed: bool):
        """Update collapsed state dan animate height."""
        self._is_collapsed = collapsed
        if collapsed:
            self.height_animator.animate_height(self.settings_container, 0)

    def resizeEvent(self, event):
        """Handle resize untuk adjust splitter ratio."""
        super().resizeEvent(event)

        if self._is_collapsed:
            self.splitter.setSizes([self.height(), 0])
            return

        self.settings_container.setFixedHeight(self._calculate_settings_target_h())

        current_height = self.height()
        if current_height > 900:
            top_h = int(current_height * 0.75)
            bottom_h = current_height - top_h
            self.splitter.setSizes([top_h, bottom_h])

    def _calculate_settings_target_h(self) -> int:
        """Calculate dynamic target height untuk settings container."""
        if self.scroll_content_layout:
            self.scroll_content_layout.activate()
        content_h = self.scroll_content.sizeHint().height()
        total_h = content_h + 80
        return max(150, min(total_h, 360))

    # =========================================================================
    # === THEME & LANGUAGE ===
    # =========================================================================

    def retranslate_ui(self):
        """Update text saat language berubah. Subclass BISA override."""
        pass

    def update_theme(self):
        """Update styles saat theme berubah. Subclass BISA override."""
        from resources.styles.stylesheet import SCROLL_AREA
        if hasattr(self, "scroll_area"):
            self.scroll_area.setStyleSheet(SCROLL_AREA)
