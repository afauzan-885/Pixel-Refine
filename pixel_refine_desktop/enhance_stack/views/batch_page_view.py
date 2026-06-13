"""
Batch Page View (MVC Hybrid).
Wraps legacy BatchPageLayout with a Bulk Mode header.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Signal

from pixel_refine_desktop.ui.views.settings.General.Language import language_config
from pixel_refine_desktop.enhance_stack.components.bulk_page import BulkPageLayout # Legacy
from pixel_refine_desktop.ui.resources.GenericUILibrary import realtime_update, Button

@realtime_update
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
        
        self.legacy_title = QLabel(language_config.LBL_BULK_MODE)
        self.legacy_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #333; padding: 5px;")
        legacy_header_layout.addWidget(self.legacy_title)
        
        legacy_header_layout.addStretch()
        
        # Bulk Mode Button (replacing switch)
        from PySide6.QtWidgets import QPushButton
        self.bulk_mode_btn = QPushButton(language_config.LBL_BULK_MODE, self.legacy_header)
        self.bulk_mode_btn.setObjectName("BulkModeBtn")
        
        # Soft Teal style for active Bulk Mode
        self.bulk_mode_btn.setStyleSheet("""
            QPushButton#BulkModeBtn {
                background-color: #E6F4EA;
                color: #137333;
                border: 1px solid #A3E2B8;
                border-radius: 15px;
                padding: 5px 15px;
                font-size: 10.5pt;
                font-weight: 600;
            }
            QPushButton#BulkModeBtn:hover {
                background-color: #D2EBD9;
            }
            QPushButton#BulkModeBtn:pressed {
                background-color: #C1E2CB;
            }
        """)
        self.bulk_mode_btn.clicked.connect(self._on_bulk_btn_clicked)
        legacy_header_layout.addWidget(self.bulk_mode_btn)
        
        legacy_header_layout.addStretch()
        
        # Process All Button
        # Uses QGraphicsOpacityEffect to visually hide without removing physical space
        # so that the toggle position remains stable.
        self.process_all_btn = Button(language_config.BTN_PROCESS_ALL_BATCH, variant="primary")
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

    def _on_bulk_btn_clicked(self):
        # When clicked in Bulk View, transition back to Batch (Tunggal) Mode
        self.bulk_mode_toggled.emit(False)

    def retranslate_ui(self):
        """Update all text dynamically when language changes."""
        if hasattr(self, "legacy_title"):
            self.legacy_title.setText(language_config.LBL_BULK_MODE)
        if hasattr(self, "bulk_mode_btn"):
            self.bulk_mode_btn.setText(language_config.LBL_BULK_MODE)
        if hasattr(self, "process_all_btn"):
            self.process_all_btn.setText(language_config.BTN_PROCESS_ALL_BATCH)
        # Refresh inner layout translations if it has retranslate_ui
        if hasattr(self, "batch_layout") and hasattr(self.batch_layout, "retranslate_ui"):
            try:
                self.batch_layout.retranslate_ui()
            except Exception:
                pass


