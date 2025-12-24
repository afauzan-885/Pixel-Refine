from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
    QSplitter,
    QScrollArea,
)
from PySide6.QtCore import Signal, Qt, QTimer
import json
import os


# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    Button,
    FormGroup,
)
from pixel_refine_desktop.ui.resources.GenericUILibrary.mixins import SyncMixin

from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
    BatchProcessDialog,
)
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic
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
        self._is_collapsed = True  # Track state for resize logic
        self.current_batch_id = None  # Track active batch for JSON persistence
        self._is_syncing = False  # Flag to avoid recursion during sync

        # Debounce timer for rapid selection changes (Breathing Room)
        self._selection_timer = QTimer(self)
        self._selection_timer.setSingleShot(True)
        self._selection_timer.timeout.connect(self._do_handle_selection)
        self._pending_selection = None

        # Real-time state binding
        if store:
            self.bind_store(store)

        self._setup_ui()
        self._load_batches()

    def _get_json_path(self):
        """Return absolute path to batch_parameter.json."""
        return os.path.join("database", "align", "batch_parameter.json")

    def _load_json_state(self):
        """Read JSON state safely."""
        path = self._get_json_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[RightPanel] Error loading JSON: {e}")
        return {}

    def _save_json_state(self, all_data):
        """Write JSON state safely."""
        path = self._get_json_path()
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                json.dump(all_data, f, indent=4)
        except IOError as e:
            print(f"[RightPanel] Error saving JSON: {e}")

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
        if not self.current_batch_id:
            return

        str_id = str(self.current_batch_id)
        settings = {
            "alignment_algo": self.align_form.get_value(),
            "super_resolution_algo": self.sr_form.get_value(),
            "denoising_algo": self.denoise_form.get_value(),
            "checkbox_align_images": self.align_form.get_value()
            not in ["None", "No Alignment"],
            "checkbox_super_resolution": self.sr_form.get_value()
            not in ["None", "No Super Resolution"],
            "checkbox_denoising": self.denoise_form.get_value()
            not in ["None", "No Denoising"],
        }

        # Save to store
        # Use silent_set to update individual keys within the scope efficiently
        # This prevents the "625.625" nesting issue if str_id was misused
        self._store.update_bulk(
            {
                f"{str_id}.alignment_algo": settings["alignment_algo"],
                f"{str_id}.super_resolution_algo": settings["super_resolution_algo"],
                f"{str_id}.denoising_algo": settings["denoising_algo"],
                f"{str_id}.checkbox_align_images": settings["checkbox_align_images"],
                f"{str_id}.checkbox_super_resolution": settings[
                    "checkbox_super_resolution"
                ],
                f"{str_id}.checkbox_denoising": settings["checkbox_denoising"],
            },
            save=True,
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
        self.list_group = ListGroup()
        self.list_group.selection_changed.connect(self._on_selection_changed)
        self.list_group.item_renamed.connect(self._on_batch_renamed)
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

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(
            0, 5, 10, 5
        )  # Margin for scrollbar space
        self.scroll_content_layout.setSpacing(10)

        algo_label = QLabel("Algorithm Settings")
        algo_label.setStyleSheet(
            "font-weight: bold; margin-top: 5px; margin-bottom: 5px;"
        )
        self.scroll_content_layout.addWidget(algo_label)

        # Alignment FormGroup
        align_names = self.logic.get_algorithm_names("alignment")
        self.align_form = FormGroup("Alignment", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])
        self.align_form.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.align_form)

        # Declarative Bindings: Link to Store via SyncMixin
        self.add_binding("alignment_algo", self.align_form, fallback="No Alignment")

        # Super Resolution FormGroup
        sr_names = self.logic.get_algorithm_names("super_resolution")
        self.sr_form = FormGroup("Super Resolution", input_type="select")
        self.sr_form.add_options(sr_names)
        if sr_names:
            self.sr_form.set_value(sr_names[0])
        self.sr_form.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.sr_form)
        self.add_binding(
            "super_resolution_algo", self.sr_form, fallback="No Super Resolution"
        )

        # Denoising FormGroup
        denoise_names = self.logic.get_algorithm_names("denoising")
        self.denoise_form = FormGroup("Denoising", input_type="select")
        self.denoise_form.add_options(denoise_names)
        if denoise_names:
            self.denoise_form.set_value(denoise_names[0])
        self.denoise_form.value_changed.connect(self._on_settings_changed)
        self.scroll_content_layout.addWidget(self.denoise_form)
        self.add_binding("denoising_algo", self.denoise_form, fallback="No Denoising")

        self.scroll_content_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_content)

        # Add Scroll Area to Main Algo Layout
        algo_layout.addWidget(self.scroll_area)

        # Process All Batch Button (Fixed at bottom)
        self.process_all_btn = Button("Process All Batch", variant="primary")
        self.process_all_btn.clicked.connect(self._on_process_all_clicked)
        algo_layout.addWidget(self.process_all_btn)

        # Initialize Default Settings
        self._on_settings_changed()

        # Add widgets to splitter
        self.splitter.addWidget(self.batch_container)
        self.splitter.addWidget(self.algo_container)

        # Set Collapsible false to keep min sizes
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        main_layout.addWidget(self.splitter)

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

    def _on_settings_changed(self, save_to_store=True):
        """Emit current settings and optionally save to persistence."""
        settings = {
            "alignment": self.align_form.get_value() or "",
            "super_resolution": self.sr_form.get_value() or "",
            "denoising": self.denoise_form.get_value() or "",
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

        name, ok = QInputDialog.getText(self, "New Batch", "Enter batch name:")
        if ok and name:
            batch_id = self.controller.create_batch(name)
            if batch_id:
                self.list_group.add_item(name, value=batch_id)
                # Auto select new item untuk display di workspace
                self.list_group.select_item_by_value(batch_id)
                # Emit signal untuk load batch ke workspace
                self.batch_selected.emit(batch_id)

    def _delete_batch(self):
        if not self.controller:
            return

        selected_ids = self.list_group.get_selected_values()
        if not selected_ids:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(selected_ids)} selected batch(es)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for bid in selected_ids:
                if self.controller.delete_batch(bid):
                    pass  # Handled by list reload or manual remove

            # Reload to sync
            self._load_batches()

            # Emit signal clearing selection if needed (handled by list group clearing usually)

    def _calculate_algo_target_h(self):
        """Calculate dynamic target height based on content but capped at 280px."""
        # Force a layout update to get accurate sizeHint
        # Use the stored layout reference directly
        if self.scroll_content_layout:
            self.scroll_content_layout.activate()
        content_h = self.scroll_content.sizeHint().height()

        # Add overhead for button and margins (approx 80px)
        # Header (30) + Button (45) + Margins/Spacing (15)
        total_h = content_h + 80

        # Clamp between 150 and 280
        return max(150, min(total_h, 280))

    def _on_selection_changed(self, selected_values):
        """Buffer selection change to prevent UI lag during rapid clicking."""
        self._pending_selection = selected_values
        self._selection_timer.start(100)  # 300ms breathing room

    def _do_handle_selection(self):
        """Actual logic for handling batch selection after debounce."""
        if self._pending_selection is None:
            return

        selected_values = self._pending_selection
        self._pending_selection = None

        if not self.left_panel or not self.left_panel.display_panel:
            return

        # Case 1: Multiple items selected
        if len(selected_values) > 1:
            self._is_collapsed = True
            self.height_animator.animate_height(self.algo_container, 0)
            QTimer.singleShot(300, lambda: self.splitter.setSizes([10000, 0]))

            selected_labels = self.list_group.get_selected_labels()
            self.left_panel.display_panel.show_delete_confirmation(
                selected_values, selected_labels
            )

        # Case 2: One item selected
        elif len(selected_values) == 1:
            self._is_collapsed = False
            target_h = self._calculate_algo_target_h()
            self.height_animator.animate_height(self.algo_container, target_h)
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setStretchFactor(1, 1)

            batch_id = int(selected_values[0])
            self.current_batch_id = batch_id  # Update tracking ID

            # Load settings from JSON for this batch
            self._load_batch_settings(batch_id)

            # Safely get the batch name from the selected item's label
            selected_labels = self.list_group.get_selected_labels()
            batch_name = selected_labels[0] if selected_labels else ""

            self.left_panel.display_panel.set_header_title(f"Batch: {batch_name}")
            self.batch_selected.emit(batch_id)

        # Case 3: No items selected
        else:
            self._is_collapsed = True
            self.height_animator.animate_height(self.algo_container, 0)
            self.splitter.setStretchFactor(1, 0)
            self.splitter.setStretchFactor(0, 1)
            QTimer.singleShot(300, lambda: self.splitter.setSizes([10000, 0]))

            self.left_panel.display_panel.set_header_title("No batch selected")
            self.current_batch_id = None  # Clear tracking
            self.batch_selection_cleared.emit()

    def _on_process_all_clicked(self):
        """Open BatchProcessDialog for batch processing."""
        if not self.controller:
            return

        # Import here to avoid circular imports
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.batch_process_dialog import (
            BatchProcessDialog,
        )

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
