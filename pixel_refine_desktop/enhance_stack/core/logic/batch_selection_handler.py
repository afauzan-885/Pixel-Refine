from PySide6.QtCore import QObject, QTimer, Signal
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


class BatchSelectionHandler(QObject):
    """
    Handles the logic for batch selection in RightPanel.
    Coordinates between RightPanel and DisplayPanel.
    """

    def __init__(self, right_panel):
        super().__init__()
        self.right_panel = right_panel

        # Dedicated timer for delayed splitter adjustments to prevent race conditions
        self._splitter_timer = QTimer(self)
        self._splitter_timer.setSingleShot(True)
        self._splitter_timer.timeout.connect(self._finish_layout_adjustment)

    def handle_selection(self, selected_values):
        """
        Main logic for handling selection changes.
        """
        if (
            not self.right_panel.left_panel
            or not self.right_panel.left_panel.display_panel
        ):
            return

        display_panel = self.right_panel.left_panel.display_panel

        # Case 1: Multiple items selected
        if len(selected_values) > 1:
            self.right_panel.set_collapsed_state(True)
            self._splitter_timer.start(300)

            selected_labels = self.right_panel.list_group.get_selected_labels()
            display_panel.show_delete_confirmation(selected_values, selected_labels)

        # Case 2: One item selected
        elif len(selected_values) == 1:
            self._splitter_timer.stop()  # Cancel any pending collapse
            self.right_panel.set_collapsed_state(False)

            target_h = self.right_panel._calculate_algo_target_h()
            self.right_panel.height_animator.animate_height(
                self.right_panel.algo_container, target_h
            )
            self.right_panel.splitter.setStretchFactor(0, 1)
            self.right_panel.splitter.setStretchFactor(1, 1)

            batch_id = int(selected_values[0])
            self.right_panel.current_batch_id = batch_id

            # Load settings from JSON/Store for this batch
            self.right_panel._load_batch_settings(batch_id)

            # Update Header Title
            selected_labels = self.right_panel.list_group.get_selected_labels()
            batch_name = selected_labels[0] if selected_labels else ""
            display_panel.set_header_title(f"Batch: {batch_name}")

            # Emit signal
            self.right_panel.batch_selected.emit(batch_id)

        # Case 3: No items selected
        else:
            self.right_panel.set_collapsed_state(True)
            self.right_panel.splitter.setStretchFactor(1, 0)
            self.right_panel.splitter.setStretchFactor(0, 1)
            self._splitter_timer.start(300)

            display_panel.set_header_title(language_config.MSG_NO_BATCH_SELECTED)
            self.right_panel.current_batch_id = None
            self.right_panel.batch_selection_cleared.emit()

    def _finish_layout_adjustment(self):
        """Finalize splitter sizes but ONLY if we are still in collapsed state."""
        if self.right_panel._is_collapsed:
            self.right_panel.splitter.setSizes([10000, 0])
