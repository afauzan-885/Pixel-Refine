"""
Progress Panel - Reusable progress bar widget.
Can be used across different pages for showing operation progress.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QPushButton
from PySide6.QtCore import Signal, Qt


class ProgressPanel(QWidget):
    """
    Reusable progress panel with progress bar, status label, and optional cancel button.
    """
    
    cancel_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # Progress bar and cancel button row
        progress_row = QHBoxLayout()
        progress_row.setSpacing(8)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        progress_row.addWidget(self.progress_bar, 1)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setVisible(False)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        progress_row.addWidget(self.cancel_button)
        
        layout.addLayout(progress_row)
        
        # Remaining items label
        self.remaining_label = QLabel("")
        self.remaining_label.setObjectName("remainingLabel")
        self.remaining_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.remaining_label)
    
    def update_progress(self, value: int, message: str = "", remaining: int = -1):
        """
        Update progress display.
        
        Args:
            value: Progress value (0-100)
            message: Status message
            remaining: Number of items remaining (-1 to hide)
        """
        self.progress_bar.setValue(value)
        
        if message:
            self.status_label.setText(message)
        
        if remaining >= 0:
            self.remaining_label.setText(f"{remaining} items remaining")
            self.remaining_label.setVisible(True)
        else:
            self.remaining_label.setVisible(False)
    
    def reset(self):
        """Reset progress to initial state."""
        self.progress_bar.setValue(0)
        self.status_label.setText("Ready")
        self.remaining_label.setText("")
        self.remaining_label.setVisible(False)
    
    def set_cancelable(self, cancelable: bool):
        """
        Enable or disable cancel button.
        
        Args:
            cancelable: Whether operation can be canceled
        """
        self.cancel_button.setVisible(cancelable)
