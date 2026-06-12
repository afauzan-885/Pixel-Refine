from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve

class SkeletonLoader(QWidget):
    """
    A Bootstrap-like Skeleton Loader component for asynchronous visual placeholders.
    Creates a simple gray layout with pulsing animation.
    """
    def __init__(self, height=100, border_radius=6, parent=None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #E8E8E8;
                border-radius: {border_radius}px;
                border: 1px solid #D8D8D8;
            }}
        """)
        
        # Add opacity effect for pulse animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0.6)
        
        # Setup pulsing animation
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0.4)
        self.anim.setEndValue(0.8)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Loop animation infinitely
        self.anim_group = QSequentialAnimationGroup(self)
        self.anim_group.addAnimation(self.anim)
        
        # Reverse animation for pulse loop
        self.anim_rev = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_rev.setDuration(800)
        self.anim_rev.setStartValue(0.8)
        self.anim_rev.setEndValue(0.4)
        self.anim_rev.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim_group.addAnimation(self.anim_rev)
        
        self.anim_group.setLoopCount(-1)
        self.anim_group.start()
