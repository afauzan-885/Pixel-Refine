from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
    QSplitter,
    QScrollArea,
    QMenu,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionViewItem,
)
from PySide6.QtCore import Signal, Qt, QTimer, QEvent, QRect
from PySide6.QtGui import QColor, QFont
import json
import os
import config
from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import normalize_name


# Generic UI Library
from UILibrary import (
    ListGroup,
    Button,
    FormGroup,
    FeatureCard,
    FeatureCardGroup,
)
from UILibrary.mixins import SyncMixin

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
    BatchProcessDialog,
)
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic
from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import build_start_command
from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager
from pixel_refine_desktop.enhance_stack.core.logic.batch_selection_handler import (
    BatchSelectionHandler,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.card_content_sr import (
    get_card_content as get_sr_card_content,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.card_content import (
    get_card_content as get_denoising_card_content,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.HDR.card_content import (
    get_card_content as get_hdr_card_content,
)
from resources.animations.animation_manager import (
    HeightAnimator,
)


from UILibrary import live_update


class _BatchQueueItemDelegate(QStyledItemDelegate):
    """Paint queue status and cancel affordance inside a non-overlaid item row."""

    ACTION_WIDTH = 40
    CANCEL_BUTTON_SIZE = 16
    CANCEL_HIT_PADDING = 2
    CANCEL_VERTICAL_OFFSET = 2
    STATUS_MARKER_WIDTH = ACTION_WIDTH - 8
    STATUS_MARKER_HEIGHT = 6
    STATUS_MARKER_BOTTOM_INSET = 3

    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner

    def paint(self, painter, option, index):
        full_option = QStyleOptionViewItem(option)
        self.initStyleOption(full_option, index)
        widget = full_option.widget
        style = widget.style() if widget is not None else None

        # Draw the standard item background across the full row so native
        # selection and hover styling remain visible beneath the action area.
        background_option = QStyleOptionViewItem(full_option)
        background_option.text = ""
        if style is not None:
            style.drawControl(
                QStyle.ControlElement.CE_ItemViewItem,
                background_option,
                painter,
                widget,
            )

        text_option = QStyleOptionViewItem(full_option)
        text_option.rect.setRight(
            max(text_option.rect.left(), text_option.rect.right() - self.ACTION_WIDTH)
        )
        painter.save()
        painter.setClipRect(text_option.rect)
        super().paint(painter, text_option, index)
        painter.restore()

        batch_id = str(index.data(Qt.ItemDataRole.UserRole))
        state = self.owner._batch_queue_states.get(batch_id)
        if state is None:
            return

        rect = full_option.rect
        action_left = rect.right() - self.ACTION_WIDTH + 1
        action_rect = QRect(action_left, rect.top(), self.ACTION_WIDTH, rect.height())
        painter.save()
        painter.fillRect(action_rect, QColor("#FFFFFF"))
        painter.setPen(QColor("#D9E1E8"))
        painter.drawLine(action_left, rect.top() + 5, action_left, rect.bottom() - 5)

        status_colors = {
            "queued": "#EAB308",
            "running": "#3B82F6",
            "completed": "#22C55E",
            "cancelling": "#3B82F6",
        }
        status_color = status_colors.get(state)
        if status_color:
            status_marker = self.status_marker_rect(rect)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(status_color))
            painter.drawRect(status_marker)

        if state in ("queued", "running"):
            cancel_rect = self.cancel_button_rect(rect)
            painter.setBrush(QColor("#FFFFFF"))
            painter.setPen(QColor("#D9E1E8"))
            painter.drawRoundedRect(cancel_rect, 4, 4)
            cancel_font = QFont(full_option.font)
            if cancel_font.pointSizeF() > 0:
                cancel_font.setPointSizeF(cancel_font.pointSizeF() * 1.25)
            elif cancel_font.pixelSize() > 0:
                cancel_font.setPixelSize(round(cancel_font.pixelSize() * 1.25))
            cancel_font.setBold(True)
            painter.setFont(cancel_font)
            painter.setPen(QColor("#B42332"))
            painter.drawText(
                cancel_rect, Qt.AlignmentFlag.AlignCenter, "×"
            )
        painter.restore()

    @classmethod
    def cancel_button_rect(cls, row_rect):
        action_left = row_rect.right() - cls.ACTION_WIDTH + 1
        center_x = action_left + cls.ACTION_WIDTH // 2
        half = cls.CANCEL_BUTTON_SIZE // 2
        return QRect(
            center_x - half,
            row_rect.center().y() - half - cls.CANCEL_VERTICAL_OFFSET,
            cls.CANCEL_BUTTON_SIZE,
            cls.CANCEL_BUTTON_SIZE,
        )

    @classmethod
    def status_marker_rect(cls, row_rect):
        action_left = row_rect.right() - cls.ACTION_WIDTH + 1
        return QRect(
            action_left + (cls.ACTION_WIDTH - cls.STATUS_MARKER_WIDTH) // 2,
            row_rect.bottom() - cls.STATUS_MARKER_BOTTOM_INSET - cls.STATUS_MARKER_HEIGHT + 1,
            cls.STATUS_MARKER_WIDTH,
            cls.STATUS_MARKER_HEIGHT,
        )


@live_update
@live_update("refresh_responsive_layout", on_resize=True)
class RightPanel(QWidget, SyncMixin):
    """
    Batch List Panel for Enhance Stack.
    Displays a list of Batches (Projects).
    """

    batch_selected = Signal(int)  # Emits batch_id
    batch_selection_cleared = Signal()  # Emits when no batch selected
    algorithm_settings_changed = Signal(dict)  # Emits new settings
    process_command_changed = Signal(object)  # Card-supplied command, or None

    def __init__(self, controller=None, left_panel=None, store=None):
        super().__init__()
        self.controller = controller  # Needs BatchPageController
        self.left_panel = left_panel
        self.logic = AlgorithmLogic()
        self.height_animator = HeightAnimator(self)
        self.selection_handler = BatchSelectionHandler(self)
        self._is_collapsed = True  # Track state for resize logic
        self.current_batch_id = None  # Track active batch for JSON persistence
        self._is_syncing = False  # Flag to avoid recursion during sync
        self._last_emitted_settings = None

        self._layout_balance_timer = QTimer(self)
        self._layout_balance_timer.setSingleShot(True)
        self._layout_balance_timer.timeout.connect(self._balance_splitter_sizes)

        # Debounce timer for store sync (1 second delay to avoid rapid file writes)
        self._sync_store_timer = QTimer(self)
        self._sync_store_timer.setSingleShot(True)
        self._sync_store_timer.setInterval(1000)
        self._sync_store_timer.timeout.connect(self._save_batch_settings)

        # Debounce timer for rapid selection changes (Breathing Room)
        self._selection_timer = QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(self._do_handle_selection)
        self._pending_selection = None
        self._move_mode = False  # Track if we are in reorder 'Keyboard Move' mode
        self._batch_queue_states = {}
        self._completed_batch_ids = set()
        self._hover_cancel_batch_id = None
        self._active_process_dialog = None
        self._batch_status_timer = QTimer(self)
        self._batch_status_timer.setInterval(200)
        self._batch_status_timer.timeout.connect(self._sync_batch_queue_rows)
        self._batch_status_timer.start()
        algorithm_panel = getattr(self.left_panel, "algorithm_panel", None)
        if algorithm_panel is not None:
            algorithm_panel.processing_completed.connect(
                self._on_single_batch_processing_completed
            )

        # Coalesce bursty add/remove signals onto one event-loop tick: each run
        # of ``_update_process_all_btn_visibility`` costs a full LEFT JOIN over
        # every batch and image row, and a large import emits many signals.
        self._process_all_btn_timer = QTimer(self)
        self._process_all_btn_timer.setSingleShot(True)
        self._process_all_btn_timer.setInterval(0)
        self._process_all_btn_timer.timeout.connect(
            self._update_process_all_btn_visibility
        )

        # Real-time state binding
        if store:
            self.bind_store(store)

        self._setup_ui()
        # Defer the synchronous batch-list load to the next event-loop
        # tick so the panel constructor returns to the Qt event loop
        # immediately. The list_group renders a placeholder until the
        # tick fires; refresh_after_project_load() stays synchronous so
        # explicit user-initiated reloads (e.g. Open Project) still
        # block the calling slot as before.
        QTimer.singleShot(0, self._load_batches)

        if self.controller:
            self.controller.batch_created.connect(self._schedule_process_all_btn_update)
            self.controller.batch_deleted.connect(self._schedule_process_all_btn_update)
            self.controller.images_added.connect(
                lambda bid, count: self._schedule_process_all_btn_update()
            )
            self.controller.images_removed.connect(
                lambda bid, count: self._schedule_process_all_btn_update()
            )

        self._update_process_all_btn_visibility()

    def on_store_changed(self, key, value):
        """React to store changes (SyncMixin handles bindings)."""
        if self._is_syncing:
            return

        # 1. Let SyncMixin handle declarative bindings (dropdowns)
        super().on_store_changed(key, value)

        # 2. Additional logic for batch-wide state changes
        if self.current_batch_id:
            str_id = str(self.current_batch_id)
            if key is None or key == str_id:
                # Refresh entire UI state from store
                self._on_settings_changed(save_to_store=False)

    def _load_batch_settings(self, batch_id):
        """
        Load settings for specific batch from store.
        Uses SyncMixin scope to automate updates.
        """
        self.current_batch_id = batch_id

        # Set scope for all bindings to this batch
        self.set_scope(str(batch_id))

        # Trigger immediate refresh for all bindings in this scope
        # (SyncMixin.on_store_changed(None, ...) handles this)
        self._is_syncing = True
        try:
            self.on_store_changed(None, self.get_data())
            self._normalize_alignment_form_value()
        finally:
            self._is_syncing = False

        # Emit signal for adaptive UI (AlgorithmPanel) once cleanly
        self._on_settings_changed(save_to_store=False)

    def _normalize_alignment_form_value(self):
        raw_value = self.align_form.get_value()
        normalized = normalize_name("alignment", raw_value)
        if normalized and normalized != raw_value:
            self.align_form.set_value(normalized)

    def _save_batch_settings(self):
        """Save current UI values to store under the current batch scope."""
        if not self.current_batch_id or not self._store:
            return

        settings = {
            config.KEY_ALIGNMENT_ALGO: self.align_form.get_value(),
            config.KEY_SUPER_RESOLUTION_ALGO: self.sr_card.get_value(),
            config.KEY_DENOISING_ALGO: self.denoise_card.get_value(),
            config.KEY_HDR_ALGO: self.hdr_card.get_value(),
            config.KEY_CHECKBOX_ALIGN: self.align_form.get_value()
            not in ["None", "No Alignment"],
            config.KEY_CHECKBOX_SUPER_RES: self.sr_card.is_checked,
            config.KEY_CHECKBOX_DENOISING: self.denoise_card.is_checked,
            config.KEY_CHECKBOX_HDR: self.hdr_card.is_checked,
        }

        # Use logic module to update store
        batch_parameter_manager.update_batch_settings(
            self._store, self.current_batch_id, settings
        )

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Create Splitter
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(2)  # Static separator line, manual resizing disabled
        self.splitter.setStyleSheet(
            "QSplitter::handle { background-color: #e0e0e0; }"
        )

        # ==========================
        # 1. BATCH CONTAINER (Top)
        # ==========================
        self.batch_container = QWidget()
        batch_layout = QVBoxLayout(self.batch_container)
        batch_layout.setContentsMargins(0, 0, 0, 10)  # Bottom padding near splitter
        batch_layout.setSpacing(10)

        # Actions (moved to top)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)

        self.new_btn = Button(language_config.BTN_NEW_BATCH, variant="primary")
        self.new_btn.setFixedHeight(22)
        self.new_btn.setStyleSheet(self.new_btn.styleSheet() + " QPushButton { padding: 2px 4px; font-size: 8pt; }")
        self.new_btn.clicked.connect(self._create_new_batch)
        action_layout.addWidget(self.new_btn, 1)

        self.del_btn = Button(language_config.BTN_DELETE_BATCH, variant="danger")
        self.del_btn.setFixedHeight(22)
        self.del_btn.setStyleSheet(self.del_btn.styleSheet() + " QPushButton { padding: 2px 4px; font-size: 8pt; }")
        self.del_btn.clicked.connect(self._delete_batch)
        action_layout.addWidget(self.del_btn, 1)

        batch_layout.addLayout(action_layout)

        # Batch List
        self.list_group = ListGroup(reordering=True)
        # Batch names are edited through the context menu dialog. Prevent the
        # QListWidget's inline editor from covering the row and intercepting hover.
        self.list_group._list_widget.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        list_widget = self.list_group._list_widget
        list_widget.setObjectName("BatchQueueList")
        list_widget.setItemDelegate(_BatchQueueItemDelegate(self, list_widget))
        list_widget.setMouseTracking(True)
        list_widget.viewport().setMouseTracking(True)
        list_widget.viewport().installEventFilter(self)
        self._apply_batch_list_hover_style()
        self.list_group.selection_changed.connect(self._on_selection_changed)
        self.list_group.item_renamed.connect(self._on_batch_renamed)
        self.list_group.delete_key_pressed.connect(self._delete_batch)
        self.list_group.items_reordered.connect(self._on_batches_reordered)
        # Enable context menu for Move mode
        self.list_group.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_group.customContextMenuRequested.connect(
            self._show_batch_context_menu
        )
        batch_layout.addWidget(self.list_group)

        # ==========================
        # 2. ALGO CONTAINER (Bottom)
        # ==========================
        self.algo_container = QWidget()
        algo_layout = QVBoxLayout(self.algo_container)
        algo_layout.setContentsMargins(0, 0, 0, 0)
        algo_layout.setSpacing(5)

        # Algorithm List Logic Container (Scrollable Area)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(
            0, 5, 0, 5
        )
        self.scroll_content_layout.setSpacing(10)

        # algo_label = QLabel(language_config.LBL_ALGORITHM_SETTINGS)
        # algo_label.setStyleSheet(
        #     "font-weight: bold; margin-top: 5px; margin-bottom: 5px;"
        # )
        # self.scroll_content_layout.addWidget(algo_label)

        # Alignment FormGroup (keep hidden in background)
        align_names = self.logic.get_algorithm_names("alignment")
        self.align_form = FormGroup("Alignment", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])
        self.align_form.value_changed.connect(self._on_settings_changed)
        # self.scroll_content_layout.addWidget(self.align_form)
        self.add_binding("alignment_algo", self.align_form, fallback="No Alignment")

        # Super Resolution Feature Card
        sr_names = self.logic.get_algorithm_names("super_resolution")
        sr_content = get_sr_card_content(language_config)
        self.sr_card = FeatureCard(
            sr_content["name"],
            sr_content["description"],
            sr_names,
            "No Super Resolution",
            self,
        )
        self.sr_card.value_changed.connect(self._on_settings_changed)
        self.add_binding(
            "super_resolution_algo", self.sr_card, fallback="No Super Resolution"
        )

        # HDR Feature Card
        hdr_names = self.logic.get_algorithm_names("hdr")
        hdr_content = get_hdr_card_content(language_config)
        self.hdr_card = FeatureCard(
            hdr_content["name"],
            hdr_content["description"],
            hdr_names,
            "No HDR",
            self,
        )
        self.hdr_card.value_changed.connect(self._on_settings_changed)
        self.add_binding("hdr_algo", self.hdr_card, fallback="No HDR")

        # Multi-frame denoising card
        denoise_names = self.logic.get_algorithm_names("denoising")
        denoise_content = get_denoising_card_content(language_config)
        self.denoise_card = FeatureCard(
            denoise_content["name"],
            denoise_content["description"],
            denoise_names,
            "No Denoising",
            self,
        )
        self.denoise_card.value_changed.connect(self._on_settings_changed)
        self.add_binding("denoising_algo", self.denoise_card, fallback="No Denoising")

        self.card_group = FeatureCardGroup(columns=2, spacing=4)
        for card in (self.sr_card, self.hdr_card, self.denoise_card):
            self.card_group.add_card(card)
            card.checked_changed.connect(
                lambda checked, selected=card: self._on_card_checked(selected, checked)
            )
        self.card_group.installEventFilter(self)
        self.scroll_content.installEventFilter(self)
        self.splitter.installEventFilter(self)
        self.scroll_content_layout.addWidget(
            self.card_group, 0, Qt.AlignmentFlag.AlignTop
        )

        self.scroll_area.setWidget(self.scroll_content)

        # Add Scroll Area to Main Algo Layout
        algo_layout.addWidget(self.scroll_area)

        # Initialize Default Settings
        self._on_settings_changed()

        # Add widgets to splitter
        self.splitter.addWidget(self.batch_container)
        self.splitter.addWidget(self.algo_container)

        # Set Collapsible false to keep min sizes
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 0)
        # Disable manual splitter dragging between panels
        handle = self.splitter.handle(1)
        if handle:
            handle.setEnabled(False)
            handle.setCursor(Qt.CursorShape.ArrowCursor)

        # Keep the algorithm panel at its content height so the batch list
        # receives the remaining space and the cards sit just above the
        # Process All button. The algorithm area scrolls when space is short.
        list_widget = getattr(self.list_group, "_list_widget", None)
        if list_widget is not None:
            list_model = list_widget.model()
            if list_model is not None:
                list_model.rowsInserted.connect(
                    lambda *_: self._balance_splitter_sizes()
                )
                list_model.rowsRemoved.connect(
                    lambda *_: self._balance_splitter_sizes()
                )
                list_model.modelReset.connect(
                    lambda: self._balance_splitter_sizes()
                )

        QTimer.singleShot(0, self._balance_splitter_sizes)

        main_layout.addWidget(self.splitter)

        # Process All Batch Button (Fixed at the very bottom of RightPanel, below splitter)
        self.process_all_btn = Button(language_config.BTN_PROCESS_ALL_BATCH, variant="primary")
        self.process_all_btn.setFixedHeight(22)
        self.process_all_btn.setStyleSheet(self.process_all_btn.styleSheet() + " QPushButton { padding: 2px 4px; font-size: 8pt; }")
        self.process_all_btn.clicked.connect(self._on_process_all_clicked)
        main_layout.addWidget(self.process_all_btn)

        # Hide algo container initially until a batch is selected
        self.algo_container.setFixedHeight(0)
        self.algo_container.hide()

    def resizeEvent(self, event):
        """Handle resize to adjust splitter ratio based on screen state context."""
        super().resizeEvent(event)
        self.refresh_responsive_layout()
        self._layout_balance_timer.start(0)

    def showEvent(self, event):
        super().showEvent(event)
        self._layout_balance_timer.start(0)

    def refresh_responsive_layout(self):
        """
        Responsive layout refresher hooked via @live_update(..., on_resize=True).
        Ensures right panel maintains fixed and clean layout between batch container
        and algorithm panel across fullscreen and window resizing.
        """
        self._update_process_all_btn_scaling()
        self._balance_splitter_sizes()

    def _update_process_all_btn_scaling(self):
        """Dynamic scaling of process_all_btn height and font size based on window width."""
        if hasattr(self, "process_all_btn") and self.process_all_btn:
            window_width = self.window().width() if self.window() else 1000
            f = max(0.0, min(1.0, (window_width - 1000) / 920.0))
            
            btn_h = 22 + int(f * 10)  # scale from 22px to 32px
            self.process_all_btn.setFixedHeight(btn_h)
            
            font_size = 8.0 + f * 3.0  # scale from 8pt to 11pt
            from UILibrary.theme import get_theme, create_button_style, apply_style
            theme = get_theme()
            apply_style(self.process_all_btn, create_button_style("primary", theme).with_overrides(padding="2px 4px", font_size=f"{font_size:.1f}pt"))

    def _on_settings_changed(self, save_to_store=True):
        """Emit current settings and optionally save to persistence."""
        checked_cards = [
            card for card in (self.sr_card, self.hdr_card, self.denoise_card)
            if card.is_checked
        ]
        if len(checked_cards) > 1:
            # Repair older batch settings that enabled multiple operations.
            self._on_card_checked(checked_cards[-1], True)
            save_to_store = True
        self._balance_splitter_sizes()

        settings = self._collect_ui_settings()

        if settings == self._last_emitted_settings:
            if save_to_store and self.current_batch_id is not None:
                self._sync_store_timer.start()
            return

        self._publish_settings(settings)

        # Save to Store after a short debounce to avoid rapid file writes.
        if save_to_store and self.current_batch_id is not None:
            self._sync_store_timer.start()

    def _collect_ui_settings(self):
        """Read the current widgets directly, without relying on queued signals."""
        return {
            config.KEY_ALIGNMENT: self.align_form.get_value() or "",
            config.KEY_SUPER_RESOLUTION: self.sr_card.get_value() or "",
            config.KEY_DENOISING: self.denoise_card.get_value() or "",
            config.KEY_HDR: self.hdr_card.get_value() or "",
            config.KEY_CHECKBOX_ALIGN: self.align_form.get_value()
            not in ("", "None", "No Alignment"),
            config.KEY_CHECKBOX_SUPER_RES: bool(self.sr_card.is_checked),
            config.KEY_CHECKBOX_DENOISING: bool(self.denoise_card.is_checked),
            config.KEY_CHECKBOX_HDR: bool(self.hdr_card.is_checked),
        }

    def _publish_settings(self, settings):
        """Publish a fresh in-memory snapshot to the batch workflow."""
        self._last_emitted_settings = settings.copy()
        self.logic.set_settings(settings)
        self.algorithm_settings_changed.emit(settings)
        self.process_command_changed.emit(build_start_command(settings))

    def snapshot_settings_for_start(self):
        """Flush this batch's visible settings before the worker reads JSON."""
        checked_cards = [
            card for card in (self.sr_card, self.hdr_card, self.denoise_card)
            if card.is_checked
        ]
        if len(checked_cards) > 1:
            self._on_card_checked(checked_cards[-1], True)

        settings = self._collect_ui_settings()
        if settings != self._last_emitted_settings:
            self._publish_settings(settings)
        else:
            self.logic.set_settings(settings)

        self.flush_pending_batch_settings()
        return settings.copy()

    def _flush_active_alignment_parameter_page(self):
        """Write the active alignment page's current controls into the store."""
        display_panel = getattr(self.left_panel, "display_panel", None)
        parameter_panel = getattr(display_panel, "param_panel", None)
        if parameter_panel is None:
            return

        alignment_name = normalize_name("alignment", self.align_form.get_value())
        page_container = getattr(parameter_panel, "alignment_pages", {}).get(
            alignment_name
        )
        page = (
            page_container.widget()
            if hasattr(page_container, "widget")
            else page_container
        )
        flush = getattr(page, "flush_pending_config", None)
        if callable(flush):
            flush()

    def _flush_active_denoising_parameter_page(self):
        """Persist current denoising controls before dispatching the batch."""
        display_panel = getattr(self.left_panel, "display_panel", None)
        parameter_panel = getattr(display_panel, "param_panel", None)
        if parameter_panel is None:
            return

        denoising_name = self.denoise_card.get_value()
        get_page = getattr(parameter_panel, "_get_denoising_page", None)
        page_container = (
            get_page(denoising_name)
            if callable(get_page)
            else getattr(parameter_panel, "denoise_page_container", None)
        )
        page = (
            page_container.widget()
            if hasattr(page_container, "widget")
            else page_container
        )
        flush = getattr(page, "flush_pending_config", None)
        if callable(flush):
            flush()

    def flush_pending_batch_settings(self):
        """Synchronously persist card and algorithm settings for the active batch."""
        self._sync_store_timer.stop()
        was_syncing = self._is_syncing
        self._is_syncing = True
        try:
            self._flush_active_alignment_parameter_page()
            self._flush_active_denoising_parameter_page()
            self._save_batch_settings()
        finally:
            self._is_syncing = was_syncing

        store = getattr(self, "_store", None)
        save_to_file = getattr(store, "save_to_file", None)
        if callable(save_to_file):
            save_to_file()
        if self.current_batch_id is not None:
            store_path = getattr(store, "_file_path", None)
            if not store_path:
                raise RuntimeError(
                    "Cannot start batch processing because batch settings are not bound to a JSON file."
                )
            try:
                persisted = batch_parameter_manager.load_json_state(path=store_path)
                expected = json.loads(json.dumps(store.get(None)))
            except Exception as exc:
                raise RuntimeError(
                    "Cannot start batch processing because batch settings could not be verified after saving."
                ) from exc
            if persisted != expected:
                raise RuntimeError(
                    "Cannot start batch processing because batch settings were not fully written to JSON."
                )

    def get_current_settings(self):
        """Public accessor for settings."""
        return self.logic.get_settings()

    def _load_batches(self):
        """Load batches from controller."""
        if not self.controller:
            return []

        self._selection_timer.stop()
        self._pending_selection = None

        self.list_group.blockSignals(True)
        try:
            self.list_group.clear()
            self._batch_queue_states.clear()
            batches = self.controller.get_all_batches()
            self._completed_batch_ids.intersection_update(
                str(batch.id) for batch in batches
            )

            for batch in batches:
                item = self.list_group.add_item(batch.name, value=batch.id)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        finally:
            self.list_group.blockSignals(False)

        # The header shortcut is only useful for an empty project.  Keep this
        # synchronized here as well as in page_layout so project restores (and
        # other refreshes that do not emit batch_created/batch_deleted) cannot
        # leave a stale "New Batch" button visible.
        header_button = getattr(
            getattr(self.left_panel, "display_panel", None),
            "new_batch_header_btn",
            None,
        )
        if header_button is not None:
            header_button.setVisible(not batches)

        # Re-pin the algorithm cards to the bottom of the right panel
        # now that the list size has changed.
        QTimer.singleShot(0, self._balance_splitter_sizes)
        return batches

    def _sync_batch_queue_rows(self):
        """Refresh painted queue markers from the active processing owners."""
        states = {batch_id: "completed" for batch_id in self._completed_batch_ids}
        algorithm_panel = getattr(self.left_panel, "algorithm_panel", None)
        if algorithm_panel is not None and getattr(
            algorithm_panel, "_is_processing", False
        ):
            batch_id = getattr(algorithm_panel, "current_batch_id", None)
            if batch_id is not None:
                processor = getattr(algorithm_panel, "processor_thread", None)
                cancelled = bool(
                    processor is not None
                    and getattr(processor, "is_cancelled", lambda: False)()
                )
                states[str(batch_id)] = "cancelling" if cancelled else "running"
                self._completed_batch_ids.discard(str(batch_id))

        dialog = self._active_process_dialog
        if (
            dialog is not None
            and getattr(dialog, "processing_thread", None) is not None
            and dialog.processing_thread.isRunning()
        ):
            thread = getattr(dialog, "processing_thread", None)
            active_id = str(getattr(thread, "_active_batch_id", None))
            cancelled_ids = {
                str(cancelled_id)
                for cancelled_id in getattr(thread, "_cancelled_batch_ids", set())
            }
            for batch, _row in getattr(dialog, "panels_to_process_with_rows", ()):
                batch_id = getattr(batch, "id", None)
                key = str(batch_id)
                status_item = dialog.table_widget.item(_row, 2)
                if status_item is not None and status_item.text() == "Success":
                    states[key] = "completed"
                    self._completed_batch_ids.add(key)
                elif key in cancelled_ids:
                    states[key] = "cancelling" if key == active_id else "cancelled"
                elif key == active_id:
                    states[key] = "running"
                else:
                    states[key] = "queued"

        if states != self._batch_queue_states:
            self._batch_queue_states = states
            list_widget = self.list_group._list_widget
            if (
                self._hover_cancel_batch_id is not None
                and states.get(self._hover_cancel_batch_id)
                not in ("queued", "running")
            ):
                self._hover_cancel_batch_id = None
                list_widget.viewport().unsetCursor()
            for index in range(list_widget.count()):
                item = list_widget.item(index)
                state = states.get(str(item.data(Qt.ItemDataRole.UserRole)))
                item.setToolTip(
                    {
                        "queued": "Menunggu giliran · klik × untuk membatalkan",
                        "running": "Sedang diproses · klik × untuk membatalkan",
                        "cancelling": "Pembatalan sedang diproses",
                        "completed": "Proses selesai",
                    }.get(state, "")
                )
            self.list_group._list_widget.viewport().update()

    def _on_single_batch_processing_completed(self, completion_data):
        """Keep successful single-batch processing visible in the batch list."""
        batch_id = completion_data.get("batch_id")
        if batch_id is None:
            return
        batch_key = str(batch_id)
        if completion_data.get("is_cancelled"):
            self._completed_batch_ids.discard(batch_key)
        else:
            self._completed_batch_ids.add(batch_key)
        self._sync_batch_queue_rows()

    def _apply_batch_list_hover_style(self):
        """Use a muted green hover while keeping standard item hit-testing."""
        list_widget = getattr(getattr(self, "list_group", None), "_list_widget", None)
        if list_widget is None:
            return
        style = list_widget.styleSheet()
        marker = "QListWidget#BatchQueueList::item:hover"
        if marker in style:
            return
        list_widget.setStyleSheet(
            style
            + " QListWidget#BatchQueueList::item:hover:!selected "
            "{ background-color: #B5DCC2; }"
            + " QListWidget#BatchQueueList::item:selected:hover "
            "{ background-color: #39A96B; }"
        )

    def _cancel_batch_job(self, batch_id):
        """Cancel one queued batch or request cancellation of its active worker."""
        dialog = self._active_process_dialog
        if (
            dialog is not None
            and getattr(dialog, "processing_thread", None) is not None
            and dialog.processing_thread.isRunning()
        ):
            dialog.cancel_batch_by_id(batch_id)
            self._sync_batch_queue_rows()
            return

        algorithm_panel = getattr(self.left_panel, "algorithm_panel", None)
        if (
            algorithm_panel is not None
            and getattr(algorithm_panel, "_is_processing", False)
            and str(getattr(algorithm_panel, "current_batch_id", None)) == str(batch_id)
        ):
            algorithm_panel._on_cancel_requested()

    def _batch_cancel_rect(self, item):
        row_rect = self.list_group._list_widget.visualItemRect(item)
        return _BatchQueueItemDelegate.cancel_button_rect(row_rect).adjusted(
            -_BatchQueueItemDelegate.CANCEL_HIT_PADDING,
            -_BatchQueueItemDelegate.CANCEL_HIT_PADDING,
            _BatchQueueItemDelegate.CANCEL_HIT_PADDING,
            _BatchQueueItemDelegate.CANCEL_HIT_PADDING,
        )

    def _batch_item_at(self, viewport_pos):
        list_widget = self.list_group._list_widget
        item = list_widget.itemAt(viewport_pos)
        if item is None:
            return None
        batch_id = str(item.data(Qt.ItemDataRole.UserRole))
        if self._batch_queue_states.get(batch_id) not in ("queued", "running"):
            return None
        if self._batch_cancel_rect(item).contains(viewport_pos):
            return item
        return None

    def select_batch_sync(self, batch_id):
        """Select a batch synchronously and cancel any pending debounced selection."""
        if self.current_batch_id is not None and int(self.current_batch_id) != int(batch_id):
            self.flush_pending_batch_settings()
        self._selection_timer.stop()
        self._pending_selection = None

        self.list_group.blockSignals(True)
        try:
            selected = self.list_group.select_item_by_value(batch_id)
        finally:
            self.list_group.blockSignals(False)

        if selected:
            self.current_batch_id = int(batch_id)
            self.selection_handler.handle_selection([batch_id])
            return True
        return False

    def refresh_after_project_load(self):
        """Refresh project-backed batches and restore panel visibility."""
        batches = self._load_batches() or []
        if batches:
            self.setMaximumWidth(16777215)
            self.show()
        else:
            self.list_group.clear_selection()
            self.hide()
            self.setMaximumWidth(0)
        self._update_process_all_btn_visibility()

    def _create_new_batch(self):
        if not self.controller:
            return

        from pixel_refine_desktop.ui.views.settings.General.general_store import get_general_store
        store = get_general_store()
        show_confirm = store.get("show_new_batch_confirm")
        if show_confirm is None:
            show_confirm = True

        if show_confirm:
            from UILibrary.modals import modal_confirm
            from PySide6.QtWidgets import QDialog
            dialog = modal_confirm(
                message="Apakah Anda yakin ingin membuat batch baru?",
                parent=self,
                title="Create New Batch",
                show_checkbox=True,
                checkbox_text="Jangan tampilkan lagi"
            )
            # Connect checkbox toggled to saving setting in real-time
            dialog.checkbox.toggled.connect(
                lambda checked: store.set("show_new_batch_confirm", not checked)
            )
            
            result = dialog.exec()
            if result != QDialog.DialogCode.Accepted:
                return

        # Generate default name (Robust check for uniqueness)
        all_batches = self.controller.get_all_batches()
        existing_names = {b.name for b in all_batches}

        index = 1
        while f"Batch {index}" in existing_names:
            index += 1
        name = f"Batch {index}"

        # 4. Create Batch
        batch_id = self.controller.create_batch(name)
        if batch_id:
            item = self.list_group.add_item(name, value=batch_id)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            # Auto select new item untuk display di workspace
            self.list_group.reordering_animation = True
            self.list_group.select_item_by_value(batch_id)
            # Emit signal untuk load batch ke workspace
            self.batch_selected.emit(batch_id)

    def _delete_batch(self):
        if not self.controller:
            return

        selected_ids = self.list_group.get_selected_values()
        if not selected_ids:
            return

        from UILibrary import modal_confirm
        confirmed = modal_confirm.question(
            self,
            language_config.CONFIRM_BATCH_ALL_DELETE_BUTTON.format(len(selected_ids))
        )

        if confirmed:
            for bid in selected_ids:
                if self.controller.delete_batch(bid):
                    pass  # Handled by list reload or manual remove

            # Reload to sync
            self._load_batches()

            # Emit signal clearing selection if needed (handled by list group clearing usually)

    def _calculate_algo_target_h(self):
        """Return the natural algorithm content height, capped by list space."""
        handle_w = (
            max(0, self.splitter.handleWidth() or 0)
            if hasattr(self, "splitter") and self.splitter
            else 0
        )
        total_h = (
            self.splitter.height()
            if hasattr(self, "splitter") and self.splitter
            else 650
        )
        available = max(0, total_h - handle_w)

        desired_algo_h = self._algorithm_content_height()
        min_top_h = min(80, available)
        max_algo_h = max(0, available - min_top_h)
        return min(max_algo_h, desired_algo_h)

    def _algorithm_content_height(self):
        """Measure the card group at the current viewport width plus 5px padding."""
        if not hasattr(self, "scroll_content") or not hasattr(self, "card_group"):
            return 0

        content_hint = self.scroll_content.sizeHint().height()
        viewport_width = (
            self.scroll_area.viewport().width()
            if hasattr(self, "scroll_area") and self.scroll_area
            else 0
        )
        if viewport_width <= 0 and hasattr(self, "scroll_area"):
            viewport_width = self.scroll_area.width()

        if viewport_width > 0:
            group_height = max(
                self.card_group.heightForWidth(viewport_width),
                self.card_group.layout().heightForWidth(viewport_width),
            )
            margins = self.scroll_content_layout.contentsMargins()
            measured_height = (
                margins.top() + max(0, group_height) + margins.bottom()
            )
            if measured_height > 0:
                content_hint = measured_height

        return max(0, content_hint)

    def _on_card_checked(self, selected, checked):
        """Switch the active operation while keeping other card headers clickable."""
        if checked:
            for card in (self.sr_card, self.hdr_card, self.denoise_card):
                if card is not selected and card.is_checked:
                    card.set_value(card.fallback_val)
        self._layout_balance_timer.start(0)

    def eventFilter(self, watched, event):
        list_widget = getattr(self, "list_group", None)
        viewport = (
            list_widget._list_widget.viewport() if list_widget is not None else None
        )
        if watched is viewport:
            if event.type() == QEvent.Type.MouseMove:
                item = self._batch_item_at(event.position().toPoint())
                batch_id = (
                    str(item.data(Qt.ItemDataRole.UserRole)) if item is not None else None
                )
                if batch_id != self._hover_cancel_batch_id:
                    self._hover_cancel_batch_id = batch_id
                    watched.setCursor(
                        Qt.CursorShape.PointingHandCursor
                        if batch_id is not None
                        else Qt.CursorShape.ArrowCursor
                    )
                    watched.update()
            elif event.type() == QEvent.Type.Leave:
                if self._hover_cancel_batch_id is not None:
                    self._hover_cancel_batch_id = None
                    watched.unsetCursor()
                    watched.update()
            elif (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                item = self._batch_item_at(event.position().toPoint())
                if item is not None:
                    self._cancel_batch_job(item.data(Qt.ItemDataRole.UserRole))
                    return True
        if event.type() == QEvent.Type.LayoutRequest or (
            watched is getattr(self, "splitter", None)
            and event.type() == QEvent.Type.Resize
        ):
            if not getattr(self, "_balancing_layout", False):
                self._layout_balance_timer.start(0)
        return super().eventFilter(watched, event)

    def _balance_splitter_sizes(self):
        """Establish proportional ratio layout between batch container and algorithm panel."""
        if getattr(self, "_balancing_layout", False):
            return
        self._balancing_layout = True
        try:
            if not hasattr(self, "splitter") or self.splitter is None:
                return
            if not hasattr(self, "batch_container") or not hasattr(
                self, "algo_container"
            ):
                return

            # Disable manual resizing between the two panels
            try:
                handle = self.splitter.handle(1)
                if handle:
                    handle.setEnabled(False)
                    handle.setCursor(Qt.CursorShape.ArrowCursor)
            except Exception:
                pass

            total_h = self.splitter.height()
            if total_h <= 0:
                return

            # If collapsed, force top widget to 100% and bottom to 0
            if getattr(self, "_is_collapsed", False):
                try:
                    self.algo_container.setMinimumHeight(0)
                    self.algo_container.setMaximumHeight(0)
                except Exception:
                    pass
                self.splitter.setSizes([total_h, 0])
                return

            handle_w = max(0, self.splitter.handleWidth() or 0)
            available = max(0, total_h - handle_w)

            # The batch list receives every pixel beyond the natural card
            # height. Keep a small top minimum, then let QScrollArea handle
            # the algorithm content when the window is too short.
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setStretchFactor(1, 0)
            desired_algo_h = self._algorithm_content_height()
            min_top_h = min(80, available)
            max_algo_h = max(0, available - min_top_h)
            min_algo_h = min(desired_algo_h, max_algo_h)

            try:
                # Do not let the card content's natural height become the
                # panel's hard minimum; that would raise the main window's
                # minimum size and prevent QScrollArea from scrolling.
                scroll_min_h = self.scroll_area.minimumSizeHint().height()
                self.algo_container.setMinimumHeight(
                    min(max(0, scroll_min_h), max_algo_h)
                )
                self.algo_container.setMaximumHeight(min_algo_h)
            except Exception:
                pass

            bottom_h = min_algo_h
            top_h = max(min_top_h, available - bottom_h)

            self.splitter.setSizes([top_h, bottom_h])
        except Exception:
            # Layout rebalancing must never raise into the event loop.
            pass
        finally:
            self._balancing_layout = False

    def _schedule_process_all_btn_update(self, *_args):
        """Request a coalesced refresh of the Process All button state."""
        self._process_all_btn_timer.start()

    def _update_process_all_btn_visibility(self):
        """Show or hide Process All Batch button depending on if any batch contains images."""
        if not self.controller:
            self.process_all_btn.hide()
            return
        
        try:
            batches = self.controller.get_all_batches()
            has_batches_with_images = any(len(batch.images) > 0 for batch in batches)
            if has_batches_with_images:
                self.process_all_btn.show()
            else:
                self.process_all_btn.hide()
        except Exception as e:
            print(f"Error checking batch image counts: {e}")
            self.process_all_btn.hide()

    def _on_selection_changed(self, selected_values):
        """Immediately trigger selection change on next tick to eliminate UI lag."""
        self._pending_selection = selected_values
        self._selection_timer.start(0)  # Instantaneous next-tick dispatch

    def set_collapsed_state(self, collapsed):
        """Update internal collapsed state and animate height."""
        self._is_collapsed = collapsed
        if collapsed:
            self._layout_balance_timer.stop()
            self.height_animator.animate_height(self.algo_container, 0)
        else:
            self._layout_balance_timer.start(300)

    def _do_handle_selection(self):
        """Delegate handling to logical selection_handler."""
        if self._pending_selection is None:
            return

        selected_values = self._pending_selection
        self._pending_selection = None

        self.selection_handler.handle_selection(selected_values)

    def _on_process_all_clicked(self):
        """Open BatchProcessDialog for batch processing."""
        if not self.controller:
            return

        # Flush in-memory/debounced parameter and card values before workers
        # snapshot the per-batch JSON configuration.
        self.flush_pending_batch_settings()

        # # Import here to avoid circular imports
        # from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
        #     BatchProcessDialog,
        # )

        # Get all batches (you may need to adapt this based on your controller API)
        batches = self.controller.get_all_batches()

        if not batches:
            QMessageBox.information(
                self, language_config.MSG_WARNING_TITLE, language_config.MSG_NO_BATCHES_AVAILABLE
            )
            return

        # BatchProcessDialog now expects BatchModel objects
        # Pass self.parent() as batch_page_layout (may need adjustment)
        dialog = BatchProcessDialog(batches, self.parent(), self)
        self._active_process_dialog = dialog
        self._sync_batch_queue_rows()
        try:
            dialog.exec()
        finally:
            self._remember_successful_batch_rows(dialog)
            self._active_process_dialog = None
            self._sync_batch_queue_rows()

    def _remember_successful_batch_rows(self, dialog):
        """Retain successful Process All rows after its modal dialog closes."""
        table = getattr(dialog, "table_widget", None)
        if table is None:
            return
        for batch, row in getattr(dialog, "panels_to_process_with_rows", ()):
            status_item = table.item(row, 2)
            if status_item is not None and status_item.text() == "Success":
                self._completed_batch_ids.add(str(batch.id))
            else:
                self._completed_batch_ids.discard(str(batch.id))

    def _on_batch_renamed(self, batch_id, new_name):
        """Handle batch rename from ListGroup."""
        if not self.controller:
            return

        success = self.controller.update_batch_name(batch_id, new_name)

        if success:
            list_widget = self.list_group._list_widget
            blocked = list_widget.blockSignals(True)
            try:
                for index in range(list_widget.count()):
                    item = list_widget.item(index)
                    if str(item.data(Qt.ItemDataRole.UserRole)) == str(batch_id):
                        item.setText(new_name)
                        break
            finally:
                list_widget.blockSignals(blocked)
        else:
            # If update fails (e.g., validation error), reload batches to revert name
            QMessageBox.warning(
                self,
                language_config.MSG_WARNING_TITLE,
                language_config.MSG_RENAME_FAILED,
            )
            self._load_batches()

    def _on_batches_reordered(
        self, batch_ids, direction=None, start_idx=-1, target_idx=-1
    ):
        """Handle reordering from ListGroup (Drag & Drop)."""
        if self.controller:
            self.controller.reorder_batches(batch_ids)

        # Native Cascading Animation is now handled inside ListGroup
        pass

    def _show_batch_context_menu(self, pos):
        """Show context menu for batch items."""
        if not self.list_group.get_selected_values():
            return

        menu = QMenu(self)
        rename_act = menu.addAction("Rename batch")
        rename_act.triggered.connect(self._rename_selected_batch)

        menu.addSeparator()
        move_act = menu.addAction("Move batch")
        move_act.setCheckable(True)
        # Check if list_group is actually in move mode to reflect current state
        move_act.setChecked(self.list_group._move_mode)
        move_act.triggered.connect(self._toggle_move_mode)

        menu.addSeparator()
        del_act = menu.addAction("Delete Batch")
        del_act.triggered.connect(self._delete_batch)

        menu.exec_(self.list_group.mapToGlobal(pos))

    def _toggle_move_mode(self):
        # Sync from list_group state if possible, or toggle locally
        self._move_mode = not self.list_group._move_mode
        self.list_group.set_move_mode(self._move_mode)

    def _rename_selected_batch(self):
        """Rename the selected batch without opening an inline editor over its row."""
        selected = self.list_group._list_widget.selectedItems()
        if not selected:
            return
        item = selected[0]
        batch_id = item.data(Qt.ItemDataRole.UserRole)
        new_name, accepted = QInputDialog.getText(
            self, "Rename batch", "Batch name:", text=item.text()
        )
        if accepted and new_name.strip():
            self._on_batch_renamed(batch_id, new_name.strip())

    def retranslate_ui(self):
        """Update all text dynamically when language changes."""
        # Buttons
        if hasattr(self, "new_btn"):
            self.new_btn.setText(language_config.BTN_NEW_BATCH)
        if hasattr(self, "del_btn"):
            self.del_btn.setText(language_config.BTN_DELETE_BATCH)
        if hasattr(self, "process_all_btn"):
            self.process_all_btn.setText(language_config.BTN_PROCESS_ALL_BATCH)

        # Feature Cards
        if hasattr(self, "sr_card"):
            sr_content = get_sr_card_content(language_config)
            self.sr_card.title_lbl.setText(sr_content["name"])
            self.sr_card.desc_lbl.setText(sr_content["description"])
        if hasattr(self, "denoise_card"):
            denoise_content = get_denoising_card_content(language_config)
            self.denoise_card.title_lbl.setText(denoise_content["name"])
            self.denoise_card.desc_lbl.setText(denoise_content["description"])
        if hasattr(self, "hdr_card"):
            hdr_content = get_hdr_card_content(language_config)
            self.hdr_card.title_lbl.setText(hdr_content["name"])
            self.hdr_card.desc_lbl.setText(hdr_content["description"])

        self.list_group.set_move_mode(self._move_mode)
        if not self._move_mode:
            self._load_batches()  # Refresh style and order to be safe

        self._apply_batch_list_hover_style()
        self.update_theme()

    def update_theme(self):
        """Update styles of child cards and widgets dynamically on theme changes."""
        from resources.styles.stylesheet import SCROLL_AREA
        from PySide6.QtWidgets import QScrollArea
        # 1. Update Scroll Area
        if hasattr(self, "scroll_area"):
            self.scroll_area.setStyleSheet(SCROLL_AREA)
        # 2. Update Feature Cards
        for card in (
            getattr(self, "sr_card", None),
            getattr(self, "hdr_card", None),
            getattr(self, "denoise_card", None),
        ):
            if card is not None and hasattr(card, "update_theme"):
                card.update_theme()
        # 3. Update buttons
        from UILibrary.theme import get_theme, create_button_style, apply_style
        theme = get_theme()
        for btn in [self.new_btn, self.del_btn, self.process_all_btn]:
            if btn:
                apply_style(btn, create_button_style(btn.variant, theme).with_overrides(padding="4px 8px", font_size="8pt"))

        self._apply_batch_list_hover_style()
