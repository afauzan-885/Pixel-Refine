"""
WorkspacePageLayout - General Page Layout
==========================================
Clone dari enhance_stack page_layout.py UI shell.
Left panel (stretch 4) + Right panel (stretch 1) dengan
panel visibility animation.

Layout Structure:
┌──────────────────────────────────────────────┐
│                                              │
│  ┌────────────────────────┐ ┌──────────────┐ │
│  │                        │ │              │ │
│  │  WorkspaceLeftPanel    │ │ RightPanel   │ │
│  │  (stretch 4)           │ │ (stretch 1)  │ │
│  │                        │ │              │ │
│  └────────────────────────┘ └──────────────┘ │
│                                              │
└──────────────────────────────────────────────┘
"""

from __future__ import annotations
from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer
from typing import Any


def _animate_panel_visibility(panel: QWidget, visible: bool):
    """Fade a panel in or out smoothly without removing it from layout."""
    effect = panel.graphicsEffect()
    if not isinstance(effect, QGraphicsOpacityEffect):
        effect = QGraphicsOpacityEffect(panel)
        panel.setGraphicsEffect(effect)

    start_val = 1.0 if not visible else 0.0
    end_val = 0.0 if not visible else 1.0

    anim = QPropertyAnimation(effect, b"opacity", panel)
    anim.setDuration(280)
    anim.setStartValue(start_val)
    anim.setEndValue(end_val)
    anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

    if visible:
        panel.setMaximumWidth(16777215)
        panel.show()

    def on_finished():
        if not visible:
            panel.hide()
            panel.setMaximumWidth(0)

    anim.finished.connect(on_finished)
    anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)


class WorkspacePageLayout(QWidget):
    """
    General page layout - clone dari enhance_stack page_layout.

    Menyediakan layout kiri (workspace) + kanan (sidebar) dengan
    visibility animation. Subclass inject panel via constructor atau override.
    """

    page_changed = Signal(int)

    def __init__(self, left_panel=None, right_panel=None, parent=None):
        super().__init__(parent)

        self.workspace_panel = left_panel
        self.batch_panel = right_panel

        self.single_page_layout = QHBoxLayout()
        self.single_page_layout.setSpacing(0)
        self.single_page_layout.setContentsMargins(0, 0, 0, 0)

        # Layout utama
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        if self.workspace_panel:
            self.single_page_layout.addWidget(self.workspace_panel, 4)
        if self.batch_panel:
            self.single_page_layout.addWidget(self.batch_panel, 1)

        main_layout.addLayout(self.single_page_layout)

        # Wire right panel visibility to batch existence
        if self.batch_panel:
            QTimer.singleShot(0, self._set_initial_right_panel_visibility)

    def _set_initial_right_panel_visibility(self):
        """Set right panel visibility awal tanpa animasi."""
        if not self.batch_panel:
            return
        if not self._should_show_right_panel():
            self.batch_panel.hide()
            self.batch_panel.setMaximumWidth(0)

    def _should_show_right_panel(self) -> bool:
        """Kondisi awal apakah right panel tampil. Override di subclass."""
        return True

    def _update_right_panel_visibility(self, has_data: bool):
        """Show/hide right panel berdasarkan apakah ada data."""
        if not self.batch_panel:
            return
        currently_visible = (
            self.batch_panel.isVisible() and self.batch_panel.maximumWidth() != 0
        )
        if has_data and not currently_visible:
            _animate_panel_visibility(self.batch_panel, True)
        elif not has_data and currently_visible:
            _animate_panel_visibility(self.batch_panel, False)

    def show_right_panel(self, animated=True):
        """Tampilkan right panel."""
        if animated:
            _animate_panel_visibility(self.batch_panel, True)
        else:
            self.batch_panel.show()
            self.batch_panel.setMaximumWidth(16777215)

    def hide_right_panel(self, animated=True):
        """Sembunyikan right panel."""
        if animated:
            _animate_panel_visibility(self.batch_panel, False)
        else:
            self.batch_panel.hide()
            self.batch_panel.setMaximumWidth(0)
