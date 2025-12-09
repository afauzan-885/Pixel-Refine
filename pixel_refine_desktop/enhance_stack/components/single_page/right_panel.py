from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QMessageBox,
)
from PySide6.QtCore import Signal, Qt

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import (
    ListGroup,
    Button,
    Theme,
    EmptyState,
)


class RightPanel(QWidget):
    """
    Batch List Panel for Enhance Stack.
    Displays a list of Batches (Projects).
    """

    batch_selected = Signal(int)  # Emits batch_id

    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller  # Needs BatchPageController
        self._setup_ui()
        self._load_batches()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Actions (moved to top)
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)

        self.new_btn = Button("New Batch", variant="primary")
        self.new_btn.clicked.connect(self._create_new_batch)
        # Using stretch or specific size policy if needed for 50/50,
        # but QHBoxLayout with equal widgets usually splits them if they expand.
        # Generic Button usually hugs content, so let's set them to expand for 50/50.
        # Assuming Button inherits QPushButton/QWidget, we can set size policy.
        # However, for simplicity and ensuring they fill, we can add them to layout.
        # To enforce 50/50, we can add them with stretch 1 each.

        action_layout.addWidget(self.new_btn, 1)

        self.del_btn = Button("Delete Batch", variant="danger")
        self.del_btn.clicked.connect(self._delete_batch)
        action_layout.addWidget(self.del_btn, 1)

        main_layout.addLayout(action_layout)

        # Header (Below buttons now)
        header_label = QLabel("Batches")
        header_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 5px;"
        )
        main_layout.addWidget(header_label)

        # Batch List
        self.list_group = ListGroup()
        self.list_group.selection_changed.connect(self._on_selection_changed)
        main_layout.addWidget(self.list_group)

    def _load_batches(self):
        """Load batches from controller."""
        if not self.controller:
            return

        self.list_group.clear()
        batches = self.controller.get_all_batches()

        for batch in batches:
            self.list_group.add_item(batch.name, value=batch.id)

        if self.list_group.count > 0:
            self.list_group.select_first()

    def _create_new_batch(self):
        if not self.controller:
            return

        name, ok = QInputDialog.getText(self, "New Batch", "Enter batch name:")
        if ok and name:
            batch_id = self.controller.create_batch(name)
            if batch_id:
                self.list_group.add_item(name, value=batch_id)
                # Auto select new item?

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
