"""
Bootstrap-like Tab Components for PySide6
Provides tabbed navigation components with animations
"""

import sys
import os

# Add project root to path for animation imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QStackedWidget, QTabBar
from PySide6.QtCore import Signal, QPropertyAnimation, QEasingCurve, Qt, QTimer
from PySide6.QtGui import QColor

# Import animations
try:
    from resources.animations.animation_manager import (
        StackedWidgetAnimator,
        AnimationType,
        SlideDirection,
    )

    ANIMATIONS_AVAILABLE = True
except ImportError:
    ANIMATIONS_AVAILABLE = False


class AnimatedTabContainer(QTabWidget):
    """
    Tab container with fade and slide animations

    Features:
    - Fade animation for tab bar
    - Slide animation for tab content

    Usage:
        tabs = AnimatedTabContainer()
        tabs.add_tab("Settings", settings_widget)
        tabs.add_tab("Profile", profile_widget)
        tabs.tab_changed.connect(on_tab_change)
    """

    tab_changed = Signal(int, str)  # index, title

    def __init__(self, enable_animations=True, parent=None):
        super().__init__(parent)

        self.enable_animations = enable_animations and ANIMATIONS_AVAILABLE
        self.previous_index = 0

        # Setup animator if animations available
        if self.enable_animations:
            self.animator = StackedWidgetAnimator()
            # Replace internal QStackedWidget with animated one
            self._setup_animated_stack()

        # Connect signal
        self.currentChanged.connect(self._on_tab_changed)

    def _setup_animated_stack(self):
        """Setup animated stacked widget for tab content"""
        # Get the internal stacked widget
        self.stack = self.findChild(QStackedWidget)
        if self.stack:
            # Store reference for animations
            self._animated_stack = self.stack

    def add_tab(self, title, widget=None):
        """Add a tab with animation support"""
        if widget is None:
            widget = QWidget()

        index = self.addTab(widget, title)
        return index

    def remove_tab(self, index):
        """Remove tab by index"""
        self.removeTab(index)

    def get_current_tab(self):
        """Get current tab index and title"""
        index = self.currentIndex()
        title = self.tabText(index)
        return (index, title)

    def set_current_tab(self, index):
        """Set current tab by index with animation"""
        if self.enable_animations and hasattr(self, "_animated_stack"):
            # Determine slide direction
            direction = (
                SlideDirection.LEFT
                if index > self.currentIndex()
                else SlideDirection.RIGHT
            )

            # Animate transition
            current_widget = self.widget(index)
            if current_widget:
                # Use slide animation for content
                anim_type = (
                    AnimationType.SLIDE_LEFT
                    if direction == SlideDirection.LEFT
                    else AnimationType.SLIDE_RIGHT
                )

                self.animator.transition_in(
                    self._animated_stack,
                    current_widget,
                    animation_type=anim_type,
                    duration_out=150,
                    duration_in=250,
                    curve_out=QEasingCurve.Type.Linear,
                    curve_in=QEasingCurve.Type.OutExpo,
                )

        self.setCurrentIndex(index)

    def _on_tab_changed(self, index):
        """Handle tab change with animations"""
        if index >= 0:
            title = self.tabText(index)

            # Animate tab bar (fade effect)
            if self.enable_animations:
                self._animate_tab_bar(index)

            # Animate content (slide effect)
            if (
                self.enable_animations
                and hasattr(self, "_animated_stack")
                and self.previous_index != index
            ):
                direction = (
                    SlideDirection.LEFT
                    if index > self.previous_index
                    else SlideDirection.RIGHT
                )
                current_widget = self.widget(index)

                if current_widget:
                    anim_type = (
                        AnimationType.SLIDE_LEFT
                        if direction == SlideDirection.LEFT
                        else AnimationType.SLIDE_RIGHT
                    )

                    self.animator.transition_in(
                        self._animated_stack,
                        current_widget,
                        animation_type=anim_type,
                        duration_out=150,
                        duration_in=250,
                        curve_out=QEasingCurve.Type.Linear,
                        curve_in=QEasingCurve.Type.OutExpo,
                    )

            self.previous_index = index
            self.tab_changed.emit(index, title)

    def _animate_tab_bar(self, index):
        """Animate tab bar with fade effect"""
        tab_bar = self.tabBar()
        if tab_bar:
            # Create fade animation for tab bar
            self.tab_bar_animation = QPropertyAnimation(tab_bar, b"opacity")
            self.tab_bar_animation.setDuration(200)
            self.tab_bar_animation.setStartValue(0.7)
            self.tab_bar_animation.setEndValue(1.0)
            self.tab_bar_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
            self.tab_bar_animation.start()

    def to_qml(self, indent=0):
        tab = "    " * indent
        anim_enabled = getattr(self, "enable_animations", True)
        qml = f"{tab}Column {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    TabBar {{\n"
        qml += f"{tab}        id: tabBar\n"
        qml += f"{tab}        width: parent.width\n"
        for i in range(self.count()):
            title = self.tabText(i).replace("'", "\\'")
            qml += f"{tab}        TabButton {{ text: '{title}' }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}    StackLayout {{\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        currentIndex: tabBar.currentIndex\n"
        # Tambahkan animasi transisi jika enable_animations=True
        if anim_enabled:
            qml += f"{tab}        Behavior on currentIndex {{\n"
            qml += f"{tab}            NumberAnimation {{ duration: 250; easing.type: Easing.OutExpo }}\n"
            qml += f"{tab}        }}\n"
        for i in range(self.count()):
            w = self.widget(i)
            if w and hasattr(w, "to_qml"):
                qml += w.to_qml(indent + 2) + "\n"
            else:
                qml += f"{tab}        Item {{ }}\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


# Alias for backward compatibility
TabContainer = AnimatedTabContainer


class TabPane(QWidget):
    """
    Individual tab pane content

    Usage:
        pane = TabPane()
        pane.add_widget(content_widget)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._qml_children = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

    def add_widget(self, widget, stretch=0):
        """Add widget to pane"""
        self._qml_children.append(widget)
        self.layout.addWidget(widget, stretch)

    def set_content(self, widget):
        """Set pane content (replaces existing)"""
        # Clear existing
        self._qml_children.clear()
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add new widget
        self._qml_children.append(widget)
        self.layout.addWidget(widget)

    def to_qml(self, indent=0):
        tab = "    " * indent
        qml = f"{tab}Item {{\n"
        qml += f"{tab}    width: parent.width\n"
        qml += f"{tab}    Column {{\n"
        qml += f"{tab}        width: parent.width\n"
        qml += f"{tab}        spacing: 10\n"
        for child in self._qml_children:
            if hasattr(child, "to_qml"):
                qml += child.to_qml(indent + 2) + "\n"
        qml += f"{tab}    }}\n"
        qml += f"{tab}}}"
        return qml


class SimpleTabs(QWidget):
    """
    Simple tab implementation with custom styling

    Usage:
        tabs = SimpleTabs()
        tabs.add_tab("Tab 1", widget1)
        tabs.add_tab("Tab 2", widget2)
    """

    tab_changed = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_widget = AnimatedTabContainer()
        self.tab_widget.tab_changed.connect(
            lambda idx, title: self.tab_changed.emit(idx, title)
        )

        layout.addWidget(self.tab_widget)

    def add_tab(self, title, widget=None):
        """Add tab"""
        if widget is None:
            widget = TabPane()

        return self.tab_widget.addTab(widget, title)

    def get_tab_widget(self, index):
        """Get tab widget by index"""
        return self.tab_widget.widget(index)

    def to_qml(self, indent=0):
        return self.tab_widget.to_qml(indent)
