"""
Bootstrap-like Progress Bar Components for PySide6
Provides various progress bar styles with animations
"""

import sys
import os
import math

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient

# Try to import existing progress components
try:
    from pixel_refine_desktop.ui.resources.animations.loading.circular_progress import (
        CircularProgress,
    )
    from pixel_refine_desktop.ui.resources.animations.loading.modern_progress_bar import (
        ModernProgressBar,
    )

    CUSTOM_PROGRESS_AVAILABLE = True
except ImportError:
    CUSTOM_PROGRESS_AVAILABLE = False


class ProgressBar(QWidget):
    """
    Modern progress bar with multiple styles

    Styles:
    - linear: Standard horizontal bar
    - striped: Striped pattern
    - animated: Animated stripes
    - gradient: Gradient color
    - circular: Circular progress

    Usage:
        progress = ProgressBar(style="animated", variant="primary")
        progress.set_value(50)
    """

    value_changed = Signal(int)

    def __init__(
        self,
        style="linear",
        variant="primary",
        show_label=True,
        minimalist=False,
        parent=None,
    ):
        super().__init__(parent)

        self.style_type = style
        self.variant = variant
        self.show_label = show_label
        self.minimalist = minimalist  # New minimalist mode
        self._value = 0
        self._max_value = 100

        # Override show_label if minimalist
        if self.minimalist:
            self.show_label = False

        # Setup UI
        self._setup_ui()

        # Animation for animated stripes
        if style == "animated":
            self._setup_animation()

    def _setup_ui(self):
        """Setup UI based on style"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        if self.style_type == "circular":
            # Use circular progress if available
            if CUSTOM_PROGRESS_AVAILABLE:
                self.progress_widget = CircularProgress(self)
            else:
                self.progress_widget = CircularProgressFallback(self)
            layout.addWidget(
                self.progress_widget, alignment=Qt.AlignmentFlag.AlignCenter
            )
        else:
            # Linear progress bar
            if self.style_type in ["linear", "striped", "animated", "gradient"]:
                if CUSTOM_PROGRESS_AVAILABLE and self.style_type == "linear":
                    self.progress_widget = ModernProgressBar(self)
                    self.progress_widget.setBarColor(self._get_variant_color())
                else:
                    self.progress_widget = CustomProgressBar(
                        style=self.style_type, variant=self.variant, parent=self
                    )
            else:
                self.progress_widget = QProgressBar(self)
                self.progress_widget.setTextVisible(False)
                self._apply_stylesheet()

            # Set height based on minimalist mode
            height = 4 if self.minimalist else 20
            self.progress_widget.setMinimumHeight(height)
            if self.minimalist:
                self.progress_widget.setMaximumHeight(height)

            layout.addWidget(self.progress_widget)

            # Label
            if self.show_label:
                self.label = QLabel("0%")
                self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.label.setStyleSheet("font-weight: bold; color: #666;")
                layout.addWidget(self.label)

    def _setup_animation(self):
        """Setup animation for animated stripes"""
        if hasattr(self.progress_widget, "start_animation"):
            self.progress_widget.start_animation()

    def _get_variant_color(self):
        """Get color based on variant"""
        colors = {
            "primary": QColor("#2ECC71"),
            "success": QColor("#2ECC71"),
            "danger": QColor("#E74C3C"),
            "warning": QColor("#F39C12"),
            "info": QColor("#3498DB"),
        }
        return colors.get(self.variant, QColor("#2ECC71"))

    def _apply_stylesheet(self):
        """Apply stylesheet to standard QProgressBar"""
        color = self._get_variant_color().name()
        self.progress_widget.setStyleSheet(
            f"""
            QProgressBar {{
                border: 1px solid #E8EDF2;
                border-radius: 10px;
                background-color: #F5F8FA;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 9px;
            }}
        """
        )

    def set_value(self, value):
        """Set progress value (0-100)"""
        self._value = max(0, min(value, self._max_value))

        if hasattr(self.progress_widget, "setValue"):
            self.progress_widget.setValue(self._value)

        if self.show_label and hasattr(self, "label"):
            self.label.setText(f"{self._value}%")

        self.value_changed.emit(self._value)

    def get_value(self):
        """Get current value"""
        return self._value

    def set_max_value(self, max_value):
        """Set maximum value"""
        self._max_value = max_value
        if hasattr(self.progress_widget, "setMaximum"):
            self.progress_widget.setMaximum(max_value)

    # --- Compatibility Methods for QProgressBar replacement ---
    def setValue(self, value):
        """Alias for set_value for QProgressBar compatibility."""
        self.set_value(value)

    def setRange(self, min_val, max_val):
        """Alias for set_max_value for QProgressBar compatibility."""
        # Note: We currently assume min is always 0 in this component
        self.set_max_value(max_val)

    def setVisible(self, visible):
        """Ensure setVisible works on the main widget."""
        super().setVisible(visible)

    def animate_to(self, target_value, duration=1000):
        """Animate progress to target value"""
        from PySide6.QtCore import QTimer

        start_value = self._value
        steps = 30  # Number of animation steps
        step_duration = duration // steps
        value_increment = (target_value - start_value) / steps

        self._animation_step = 0
        self._animation_target = target_value
        self._animation_start = start_value
        self._animation_increment = value_increment

        # Use timer for smooth animation
        self._animation_timer = QTimer(self)
        self._animation_timer.timeout.connect(self._update_animation)
        self._animation_timer.start(step_duration)

    def _update_animation(self):
        """Update animation step"""
        self._animation_step += 1

        if self._animation_step >= 30:
            # Animation complete
            self.set_value(int(self._animation_target))
            self._animation_timer.stop()
        else:
            # Update value
            new_value = self._animation_start + (
                self._animation_increment * self._animation_step
            )
            self.set_value(int(new_value))


class CustomProgressBar(QWidget):
    """Custom painted progress bar with stripes and gradients"""

    def __init__(self, style="linear", variant="primary", parent=None):
        super().__init__(parent)
        self.style_type = style
        self.variant = variant
        self._value = 0
        self._stripe_offset = 0

        self.setMinimumHeight(20)

        # Animation timer for stripes
        if style == "animated":
            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self._animate_stripes)

    def setValue(self, value):
        """Set value"""
        self._value = max(0, min(value, 100))
        self.update()

    def value(self):
        """Get value"""
        return self._value

    def start_animation(self):
        """Start stripe animation"""
        if hasattr(self, "animation_timer"):
            self.animation_timer.start(50)  # 50ms interval

    def _animate_stripes(self):
        """Animate stripe offset"""
        self._stripe_offset = (self._stripe_offset + 1) % 20
        self.update()

    def _get_variant_color(self):
        """Get color based on variant"""
        colors = {
            "primary": QColor("#2ECC71"),
            "success": QColor("#2ECC71"),
            "danger": QColor("#E74C3C"),
            "warning": QColor("#F39C12"),
            "info": QColor("#3498DB"),
        }
        return colors.get(self.variant, QColor("#2ECC71"))

    def paintEvent(self, event):
        """Custom paint"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        radius = height / 2

        # Background
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#F5F8FA"))
        painter.drawRoundedRect(0, 0, width, height, radius, radius)

        # Progress
        if self._value > 0:
            progress_width = (self._value / 100.0) * width

            if self.style_type == "gradient":
                # Gradient fill
                gradient = QLinearGradient(0, 0, progress_width, 0)
                base_color = self._get_variant_color()
                gradient.setColorAt(0, base_color.lighter(120))
                gradient.setColorAt(1, base_color)
                painter.setBrush(QBrush(gradient))
            else:
                painter.setBrush(self._get_variant_color())

            painter.drawRoundedRect(0, 0, progress_width, height, radius, radius)

            # Stripes
            if self.style_type in ["striped", "animated"]:
                painter.setBrush(QColor(255, 255, 255, 50))
                stripe_width = 20
                for i in range(int(progress_width / stripe_width) + 2):
                    x = i * stripe_width - self._stripe_offset
                    if x < progress_width:
                        points = [(x, 0), (x + 10, 0), (x, height), (x - 10, height)]
                        from PySide6.QtCore import QPoint
                        from PySide6.QtGui import QPolygon

                        polygon = QPolygon(
                            [QPoint(int(p[0]), int(p[1])) for p in points]
                        )
                        painter.drawPolygon(polygon)


class CircularProgressFallback(QWidget):
    """Fallback circular progress if custom not available"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self.setMinimumSize(100, 100)

    def setValue(self, value):
        """Set value"""
        self._value = max(0, min(value, 100))
        self.update()

    def value(self):
        """Get value"""
        return self._value

    def paintEvent(self, event):
        """Paint circular progress"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)

        # Center
        center_x = width / 2
        center_y = height / 2
        radius = side / 2 - 10

        # Background circle
        painter.setPen(QPen(QColor("#E8EDF2"), 8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(
            int(center_x - radius),
            int(center_y - radius),
            int(radius * 2),
            int(radius * 2),
        )

        # Progress arc
        if self._value > 0:
            painter.setPen(
                QPen(
                    QColor("#2ECC71"), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap
                )
            )
            span_angle = int(360 * 16 * (self._value / 100.0))
            painter.drawArc(
                int(center_x - radius),
                int(center_y - radius),
                int(radius * 2),
                int(radius * 2),
                90 * 16,
                -span_angle,
            )

        # Text
        painter.setPen(QColor("#333333"))
        font = QFont("Segoe UI", int(side * 0.15), QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(
            0, 0, width, height, Qt.AlignmentFlag.AlignCenter, f"{self._value}%"
        )


class IndeterminateProgress(QWidget):
    """
    Indeterminate progress indicator (loading animation)

    Usage:
        progress = IndeterminateProgress(style="spinner")
        progress.start()
        progress.stop()
    """

    def __init__(self, style="spinner", size=40, parent=None):
        super().__init__(parent)
        self.style_type = style
        self._angle = 0
        self._running = False

        self.setFixedSize(size, size)

        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self._update_animation)

    def start(self):
        """Start animation"""
        self._running = True
        self.animation_timer.start(50)
        self.show()

    def stop(self):
        """Stop animation"""
        self._running = False
        self.animation_timer.stop()
        self.hide()

    def _update_animation(self):
        """Update animation"""
        self._angle = (self._angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        """Paint spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        side = min(width, height)

        painter.translate(width / 2, height / 2)
        painter.rotate(self._angle)

        # Draw spinner dots
        num_dots = 12
        dot_radius = side * 0.08
        circle_radius = side / 2 - dot_radius * 2

        for i in range(num_dots):
            angle_rad = math.radians(i * (360 / num_dots))
            x = circle_radius * math.cos(angle_rad)
            y = circle_radius * math.sin(angle_rad)

            # Fade effect
            opacity = int(255 * (i / num_dots))
            painter.setBrush(QColor(46, 204, 113, opacity))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(
                int(x - dot_radius / 2),
                int(y - dot_radius / 2),
                int(dot_radius),
                int(dot_radius),
            )


class ProgressGroup(QWidget):
    """
    Group of stacked progress bars

    Usage:
        group = ProgressGroup()
        group.add_progress("Task 1", 75, variant="success")
        group.add_progress("Task 2", 50, variant="info")
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.progress_bars = []

    def add_progress(self, label, value=0, variant="primary", style="linear"):
        """Add a progress bar to the group"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(3)

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-weight: bold; color: #333;")
        container_layout.addWidget(label_widget)

        # Progress bar
        progress = ProgressBar(style=style, variant=variant, show_label=False)
        progress.set_value(value)
        container_layout.addWidget(progress)

        # Value label
        value_label = QLabel(f"{value}%")
        value_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        value_label.setStyleSheet("color: #666; font-size: 10pt;")
        container_layout.addWidget(value_label)

        self.layout.addWidget(container)
        self.progress_bars.append(
            {
                "container": container,
                "progress": progress,
                "label": label_widget,
                "value_label": value_label,
            }
        )

        return progress

    def update_progress(self, index, value):
        """Update progress bar value by index"""
        if 0 <= index < len(self.progress_bars):
            bar = self.progress_bars[index]
            bar["progress"].set_value(value)
            bar["value_label"].setText(f"{value}%")

    def clear(self):
        """Clear all progress bars"""
        for bar in self.progress_bars:
            bar["container"].deleteLater()
        self.progress_bars.clear()
