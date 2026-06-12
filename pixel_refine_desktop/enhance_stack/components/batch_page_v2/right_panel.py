from .quick_batch_dialog import QuickBatchDialog
from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager
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
)
from PySide6.QtCore import Signal, Qt, QTimer
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    StackedWidgetAnimator,
)
import json
import os


# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    Button,
    FormGroup,
    FeatureCard,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.mixins import SyncMixin

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
    BatchProcessDialog,
)
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic
from pixel_refine_desktop.enhance_stack.core.logic import batch_parameter_manager
from pixel_refine_desktop.enhance_stack.core.logic.batch_selection_handler import (
    BatchSelectionHandler,
)
from pixel_refine_desktop.ui.resources.animations.animation_manager import (
    HeightAnimator,
)


class RightPanel(QWidget, SyncMixin):
    """
    Batch List Panel for Enhance Stack.
    Displays a list of Batches (Projects).
    """

    batch_selected = Signal(int)  # Emits batch_id
    batch_selection_cleared = Signal()  # Emits when no batch selected
    algorithm_settings_changed = Signal(dict)  # Emits new settings

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

        # Debounce timer for rapid selection changes (Breathing Room)
        self._selection_timer = QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(self._do_handle_selection)
        self._pending_selection = None
        self._move_mode = False  # Track if we are in reorder 'Keyboard Move' mode

        # Real-time state binding
        if store:
            self.bind_store(store)

        self._setup_ui()
        self._load_batches()

        if self.controller:
            self.controller.batch_created.connect(self._update_process_all_btn_visibility)
            self.controller.batch_deleted.connect(self._update_process_all_btn_visibility)
            self.controller.images_added.connect(lambda bid, count: self._update_process_all_btn_visibility())
            self.controller.images_removed.connect(lambda bid, count: self._update_process_all_btn_visibility())

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
                self.algorithm_settings_changed.emit(self.get_current_settings())

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
        self.on_store_changed(None, self.get_data())

        # Emit signal for adaptive UI (AlgorithmPanel)
        self._on_settings_changed(save_to_store=False)

    def _save_batch_settings(self):
        """Save current UI values to store under the current batch scope."""
        if not self.current_batch_id or not self._store:
            return

        settings = {
            "alignment_algo": self.align_form.get_value(),
            "super_resolution_algo": self.sr_card.get_value(),
            "denoising_algo": self.denoise_card.get_value(),
            "checkbox_align_images": self.align_form.get_value()
            not in ["None", "No Alignment"],
            "checkbox_super_resolution": self.sr_card.is_checked,
            "checkbox_denoising": self.denoise_card.is_checked,
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
        self.splitter.setHandleWidth(10)  # Make handle visible/grabbable
        self.splitter.setStyleSheet(
            "QSplitter::handle { background-color: #e0e0e0; border-radius: 2px; }"
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

        self.new_btn = Button("New Batch", variant="primary")
        self.new_btn.clicked.connect(self._create_new_batch)
        action_layout.addWidget(self.new_btn, 1)

        self.del_btn = Button("Delete Batch", variant="danger")
        self.del_btn.clicked.connect(self._delete_batch)
        action_layout.addWidget(self.del_btn, 1)

        batch_layout.addLayout(action_layout)

        # Batch List
        self.list_group = ListGroup(reordering=True)
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
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(
            0, 5, 0, 5
        )
        self.scroll_content_layout.setSpacing(10)

        algo_label = QLabel("Algorithm Settings")
        algo_label.setStyleSheet(
            "font-weight: bold; margin-top: 5px; margin-bottom: 5px;"
        )
        self.scroll_content_layout.addWidget(algo_label)

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
        self.sr_card = FeatureCard(
            "SUPER RESOLUTION",
            "Upscale stack resolution dynamically using high-quality interpolation.",
            sr_names,
            "No Super Resolution",
            self,
        )
        self.sr_card.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.sr_card)
        self.add_binding(
            "super_resolution_algo", self.sr_card, fallback="No Super Resolution"
        )

        # Denoising Feature Card
        denoise_names = self.logic.get_algorithm_names("denoising")
        self.denoise_card = FeatureCard(
            "DENOISING",
            "Reduce noise and clean image details while preserving edges.",
            denoise_names,
            "No Denoising",
            self,
        )
        self.denoise_card.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.denoise_card)
        self.add_binding("denoising_algo", self.denoise_card, fallback="No Denoising")

        self.scroll_content_layout.addStretch()
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

        main_layout.addWidget(self.splitter)

        # Process All Batch Button (Fixed at the very bottom of RightPanel, below splitter)
        self.process_all_btn = Button("Process All Batch", variant="primary")
        self.process_all_btn.clicked.connect(self._on_process_all_clicked)
        main_layout.addWidget(self.process_all_btn)

        # Hide algo container initially until a batch is selected
        self.algo_container.setFixedHeight(0)
        self.algo_container.hide()

    def resizeEvent(self, event):
        """Handle resize to adjust splitter ratio based on screen state context."""
        super().resizeEvent(event)

        # If collapsed, force top widget to 100%
        if self._is_collapsed:
            self.splitter.setSizes([self.height(), 0])
            return

        # Dynamically set height of algo container based on current layout requirements
        self.algo_container.setFixedHeight(self._calculate_algo_target_h())

        # Optimization for Large Displays (Maximised)
        current_height = self.height()
        LARGE_MODE_THRESHOLD = 900

        if current_height > LARGE_MODE_THRESHOLD:
            # Calculate 3:1 ratio
            top_h = int(current_height * 0.75)
            bottom_h = current_height - top_h
            self.splitter.setSizes([top_h, bottom_h])
        else:
            # For smaller screens, let splitter handle it or force 1:1 if needed
            pass

    def _update_cards_mutually_exclusive_state(self):
        """Enforce mutual exclusivity between Super Resolution and Denoising using the disable state."""
        self.sr_card.blockSignals(True)
        self.denoise_card.blockSignals(True)
        try:
            if self.denoise_card.is_checked:
                self.sr_card.setChecked(False)
                self.sr_card.setEnabled(False)
            else:
                self.sr_card.setEnabled(True)

            if self.sr_card.is_checked:
                self.denoise_card.setChecked(False)
                self.denoise_card.setEnabled(False)
            else:
                self.denoise_card.setEnabled(True)
        finally:
            self.sr_card.blockSignals(False)
            self.denoise_card.blockSignals(False)

    def _on_settings_changed(self, save_to_store=True):
        """Emit current settings and optionally save to persistence."""
        self._update_cards_mutually_exclusive_state()

        settings = {
            "alignment": self.align_form.get_value() or "",
            "super_resolution": self.sr_card.get_value() or "",
            "denoising": self.denoise_card.get_value() or "",
        }

        # 1. Emit realtime signal for UI adaptation
        self.algorithm_settings_changed.emit(settings)

        # 2. Update local logic
        # settings is Dict[str, str], which is compatible with Dict[str, Optional[str]]
        self.logic.set_settings(settings)  # type: ignore
        # Note: logic.set_settings returns bool, but we ignore it here

        # 3. Save to Store if triggered by user interaction
        if save_to_store and self.current_batch_id is not None:
            self._save_batch_settings()

    def get_current_settings(self):
        """Public accessor for settings."""
        return self.logic.get_settings()

    def _load_batches(self):
        """Load batches from controller."""
        if not self.controller:
            return

        self.list_group.clear()
        batches = self.controller.get_all_batches()

        for batch in batches:
            self.list_group.add_item(batch.name, value=batch.id)

    def _create_new_batch(self):
        if not self.controller:
            return

        # 1. Load preferences from batch_parameter.json
        all_params = batch_parameter_manager.load_json_state()
        quick_create_enabled = all_params.get("quick_batch_creation", False)

        # 2. Generate default name (Robust check for uniqueness)
        all_batches = self.controller.get_all_batches()
        existing_names = {b.name for b in all_batches}

        index = 1
        while f"Batch {index}" in existing_names:
            index += 1
        default_name = f"Batch {index}"

        name = default_name
        should_save_preference = False

        # 3. Decision: Show Dialog or Quick Create
        if not quick_create_enabled:
            dialog = QuickBatchDialog(default_name=default_name, parent=self)
            if dialog.exec():
                name, skip_next = dialog.get_data()
                if not name:
                    name = default_name

                if skip_next:
                    # Save preference to JSON
                    all_params["quick_batch_creation"] = True
                    batch_parameter_manager.save_json_state(data=all_params)
            else:
                return  # User cancelled

        # 4. Create Batch
        batch_id = self.controller.create_batch(name)
        if batch_id:
            self.list_group.add_item(name, value=batch_id)
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

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Delete {len(selected_ids)} selected batch(es)?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            for bid in selected_ids:
                if self.controller.delete_batch(bid):
                    pass  # Handled by list reload or manual remove

            # Reload to sync
            self._load_batches()

            # Emit signal clearing selection if needed (handled by list group clearing usually)

    def _calculate_algo_target_h(self):
        """Calculate dynamic target height based on content but capped at 360px."""
        # Force a layout update to get accurate sizeHint
        # Use the stored layout reference directly
        if self.scroll_content_layout:
            self.scroll_content_layout.activate()
        content_h = self.scroll_content.sizeHint().height()

        # Add overhead for button and margins (approx 80px)
        # Header (30) + Button (45) + Margins/Spacing (15)
        total_h = content_h + 80

        # Clamp between 150 and 360
        return max(150, min(total_h, 360))

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
        """Buffer selection change to prevent UI lag during rapid clicking."""
        self._pending_selection = selected_values
        self._selection_timer.start(150)  # 200ms breathing room

    def set_collapsed_state(self, collapsed):
        """Update internal collapsed state and animate height."""
        self._is_collapsed = collapsed
        if collapsed:
            self.height_animator.animate_height(self.algo_container, 0)

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

        # # Import here to avoid circular imports
        # from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
        #     BatchProcessDialog,
        # )

        # Get all batches (you may need to adapt this based on your controller API)
        batches = self.controller.get_all_batches()

        if not batches:
            QMessageBox.information(
                self, "No Batches", "There are no batches available to process."
            )
            return

        # BatchProcessDialog now expects BatchModel objects
        # Pass self.parent() as batch_page_layout (may need adjustment)
        dialog = BatchProcessDialog(batches, self.parent(), self)
        dialog.exec()

    def _on_batch_renamed(self, batch_id, new_name):
        """Handle batch rename from ListGroup."""
        if not self.controller:
            return

        success = self.controller.update_batch_name(batch_id, new_name)

        if not success:
            # If update fails (e.g., validation error), reload batches to revert name
            QMessageBox.warning(
                self,
                "Rename Failed",
                "Could not rename the batch. The name may be invalid or already in use.",
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
        if not self._move_mode:
            self._load_batches()  # Refresh style and order to be safe
