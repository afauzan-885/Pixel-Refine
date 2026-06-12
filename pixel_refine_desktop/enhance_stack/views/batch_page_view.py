"""
Batch Page View (MVC Hybrid).
Wraps legacy BatchPageLayout with a Bulk Mode header.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Signal

from pixel_refine_desktop.enhance_stack.components.bulk_page import BulkPageLayout # Legacy

class BatchPageView(QWidget):
    """
    Batch page view wrapping V1 (legacy) BatchPageLayout with a Bulk Mode header.
    """
    page_changed = Signal(int)  # Forward global navigation
    bulk_mode_toggled = Signal(bool)

    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 8, 5, 5)
        layout.setSpacing(5)

        # Bulk Mode Header
        self.legacy_header = QWidget()
        self.legacy_header.setFixedHeight(50)
        self.legacy_header.setObjectName("LegacyHeader")
        self.legacy_header.setStyleSheet("#LegacyHeader { background-color: #FFFFFF; border-radius: 4px; }")
        
        legacy_header_layout = QHBoxLayout(self.legacy_header)
        legacy_header_layout.setContentsMargins(10, 5, 10, 5)
        
        legacy_title = QLabel("Bulk Mode")
        legacy_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; padding: 5px;")
        legacy_header_layout.addWidget(legacy_title)
        
        legacy_header_layout.addStretch()
        
        # Bulk Mode Toggle Switch for Legacy Wrapper
        from pixel_refine_desktop.ui.resources.GenericUILibrary import ToggleSwitch, Button
        legacy_toggle_layout = QHBoxLayout()
        legacy_toggle_layout.setSpacing(6)
        
        legacy_toggle_label = QLabel("Bulk Mode")
        legacy_toggle_label.setStyleSheet("font-size: 11pt; color: #555; font-weight: 500;")
        legacy_toggle_layout.addWidget(legacy_toggle_label)
        
        self.legacy_bulk_switch = ToggleSwitch(self.legacy_header)
        self.legacy_bulk_switch.setChecked(True)
        self.legacy_bulk_switch.toggled.connect(self.bulk_mode_toggled.emit)
        legacy_toggle_layout.addWidget(self.legacy_bulk_switch)
        
        legacy_header_layout.addLayout(legacy_toggle_layout)
        legacy_header_layout.addStretch()
        
        # Process All Button
        # Uses QGraphicsOpacityEffect to visually hide without removing physical space
        # so that the toggle position remains stable.
        self.process_all_btn = Button("Process All Batch", variant="primary")
        self.process_all_btn.setFixedWidth(150)
        self.process_all_btn.clicked.connect(self._on_process_all_clicked)
        legacy_header_layout.addWidget(self.process_all_btn)

        # Apply opacity effect - starts invisible if no batches (updated after batch_layout init)
        self._process_all_opacity = QGraphicsOpacityEffect(self.process_all_btn)
        self._process_all_opacity.setOpacity(0.0)
        self.process_all_btn.setGraphicsEffect(self._process_all_opacity)

        layout.addWidget(self.legacy_header)

        # The V1 Batch Page Layout
        self.batch_layout = BulkPageLayout()
        layout.addWidget(self.batch_layout)

        # Wire data_changed from batch_layout to update button visibility
        self.batch_layout.data_changed.connect(self._update_process_all_visibility)

        # Set initial visibility after batch_layout is ready
        self._update_process_all_visibility()

    def _update_process_all_visibility(self):
        """Show or hide Process All Batch button based on whether any batch exists.
        Uses opacity=0/1 to hide/show WITHOUT removing physical space (toggle stays fixed)."""
        try:
            db_ids = self.batch_layout.database_manager.get_all_batch_ids()
            has_batches = len(db_ids) > 0
        except Exception:
            has_batches = False

        self._process_all_opacity.setOpacity(1.0 if has_batches else 0.0)
        # Also disable click when invisible to prevent accidental triggering
        self.process_all_btn.setEnabled(has_batches)

    def _on_process_all_clicked(self):
        if hasattr(self, "batch_layout") and hasattr(self.batch_layout, "process_all_batches"):
            self.batch_layout.process_all_batches()

