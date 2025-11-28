from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot, QPropertyAnimation, QEasingCurve

from .viewer_panel import ViewerPanel
from .config_panel import ConfigPanel

class WorkspaceLayout(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10) # Beri sedikit jarak antar panel atas dan bawah

        # 1. Viewer (Atas)
        self.viewer = ViewerPanel()
        
        # 2. Config Area (Bawah - Collapsible)
        self.config_container = QWidget()
        # Container wrapper agar animasi smooth
        self.config_layout = QVBoxLayout(self.config_container)
        self.config_layout.setContentsMargins(0, 0, 0, 0)
        
        self.config_panel = ConfigPanel()
        self.config_layout.addWidget(self.config_panel)
        
        # Init State
        self.config_container.setFixedHeight(0)
        self.is_config_open = False

        layout.addWidget(self.viewer, 1)
        layout.addWidget(self.config_container, 0)

        # Animasi
        self.anim = QPropertyAnimation(self.config_container, b"maximumHeight")
        self.anim.setDuration(350)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)

    @Slot(bool)
    def toggle_config_panel(self, show: bool):
        if self.is_config_open == show: return
        self.is_config_open = show
        
        start_h = self.config_container.height()
        target_h = self.config_panel.sizeHint().height() if show else 0
        if target_h == 0 and show: target_h = 250 # Fallback height

        self.config_container.setMaximumHeight(start_h) # Prepare animation
        
        self.anim.setStartValue(start_h)
        self.anim.setEndValue(target_h)
        self.anim.start()
        
        if show:
            self.config_container.setMinimumHeight(0)
            def on_finished():
                self.config_container.setMinimumHeight(target_h)
                self.config_container.setMaximumHeight(16777215) # Remove max constraint
                self.anim.finished.disconnect(on_finished)
            self.anim.finished.connect(on_finished)
        else:
            self.config_container.setMinimumHeight(0)