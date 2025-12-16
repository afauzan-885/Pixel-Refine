from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
    QSplitter,
)
from PySide6.QtCore import Signal, Qt

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    Button,
    FormGroup,
)
from pixel_refine_desktop.enhance_stack.core.logic.algorithm_logic import AlgorithmLogic


class RightPanel(QWidget):
    """
    Batch List Panel for Enhance Stack.
    Displays a list of Batches (Projects).
    """

    batch_selected = Signal(int)  # Emits batch_id
    batch_selection_cleared = Signal()  # Emits when no batch selected
    algorithm_settings_changed = Signal(dict)  # Emits new settings

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller  # Needs BatchPageController
        self.logic = AlgorithmLogic()
        self._setup_ui()
        self._load_batches()

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
        batch_layout.addWidget(self.list_group)

        # ==========================
        # 2. ALGO CONTAINER (Bottom)
        # ==========================
        self.algo_container = QWidget()
        algo_layout = QVBoxLayout(self.algo_container)
        algo_layout.setContentsMargins(0, 10, 0, 0)  # Top padding near splitter
        algo_layout.setSpacing(10)

        # Algorithm List Logic
        algo_label = QLabel("AlgorithmList")
        algo_label.setStyleSheet(
            "font-weight: bold; margin-top: 5px; margin-bottom: 0px;"
        )
        algo_layout.addWidget(algo_label)

        # ScrollArea for Algo settings could be good, but assuming they fit for now.
        # Alignment FormGroup
        align_names = self.logic.get_algorithm_names("alignment")
        self.align_form = FormGroup("Alignment", input_type="select")
        self.align_form.add_options(align_names)
        if align_names:
            self.align_form.set_value(align_names[0])
        self.align_form.value_changed.connect(self._on_settings_changed)
        algo_layout.addWidget(self.align_form)

        # Super Resolution FormGroup
        sr_names = self.logic.get_algorithm_names("super_resolution")
        self.sr_form = FormGroup("Super Resolution", input_type="select")
        self.sr_form.add_options(sr_names)
        if sr_names:
            self.sr_form.set_value(sr_names[0])
        self.sr_form.value_changed.connect(self._on_settings_changed)
        algo_layout.addWidget(self.sr_form)

        # Denoising FormGroup
        denoise_names = self.logic.get_algorithm_names("denoising")
        self.denoise_form = FormGroup("Denoising", input_type="select")
        self.denoise_form.add_options(denoise_names)
        if denoise_names:
            self.denoise_form.set_value(denoise_names[0])
        self.denoise_form.value_changed.connect(self._on_settings_changed)
        algo_layout.addWidget(self.denoise_form)

        # Spacer inside algo container to push content up if resized large
        algo_layout.addStretch()

        # Process All Batch Button
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

    def resizeEvent(self, event):
        """Handle resize to adjust splitter ratio based on screen state context."""
        super().resizeEvent(event)

        # Responsive Logic:
        # User defined:
        # Default (Small/Normal) - Keep Default (let's say 50/50 or whatever splitter defaults to)
        # Full Screen (Large) - 3:1 Ratio (Batch:Algo)

        # Heuristic for "Full Screen": Height > 800px or Width > 1400px?
        # Or just check if windowState is Maximized?
        # Since I can't easily check window state from here reliably without parent chain,
        # I'll use a height threshold typical of maximized 1080p screens.

        current_height = self.height()

        # Assuming "Full Screen" means a large working area.
        # Let's say if height > 900px, we treat it as large mode.
        LARGE_MODE_THRESHOLD = 900

        if current_height > LARGE_MODE_THRESHOLD:
            # Calculate 3:1 ratio
            # Total parts = 4.
            # Top takes 3/4, Bottom takes 1/4
            total = current_height
            top_h = int(total * 0.75)
            bottom_h = total - top_h
            self.splitter.setSizes([top_h, bottom_h])
        else:
            # Default behavior / "Small"
            # Maybe 1:1 or just let it be?
            # User said "pertahankan rasion (gunakan default bawaan sekarang)"
            # Default behavior for QSplitter is usually proportional or respected sizeHints.
            # If we don't touch setSizes, it might drift.
            # Let's enforcing a balanced 1:1 or 60:40 roughly if it was previously forced.
            # However, if we only set it ONCE upon crossing threshold it's better.
            # But continuous resizeEvent runs often.

            # To be polite to the user's manual adjustment, we should strictly enforce only on significant mode changes?
            # But the requirement is "saat ukuran aplikasi paling kecil pertahankan... saat full screen menggunakan rasio 3:1"
            # It implies automatic snapping.

            pass

    def _on_settings_changed(self, _=None):
        """Emit current settings."""
        settings = {
            "alignment": self.align_form.get_value() or "",
            "super_resolution": self.sr_form.get_value() or "",
            "denoising": self.denoise_form.get_value() or "",
        }
        self.algorithm_settings_changed.emit(settings)
        # Also update local logic state if needed (though RightPanel is mainly selection UI)
        self.logic.set_settings(settings)

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

    def _on_selection_changed(self, selected_values):
        if selected_values:
            # Assuming single selection for main app logic for now, but list group supports multiple.
            # We take the first one or emit specific logic.
            # Layout connected to 'batch_selected' which expects int.
            self.batch_selected.emit(int(selected_values[0]))
        else:
            # No batch selected - clear display
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
