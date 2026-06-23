"""
Workplace - General Workspace UI Framework
============================================
Clone dari enhance_stack batch_page_v2 UI shell.
Seluruh layout, widget, animasi, dan struktur UI di-clone tanpa logic spesifik.

Setiap komponen adalah UI shell yang bisa digunakan oleh modul manapun
(enhance_stack, 3d_reconstruction, dll) dengan inject logic masing-masing.

Komponen:
- WorkspaceDisplayPanel: Header + Grid + Preview + Playback + Sidebar + Overlays
- WorkspaceLeftPanel: DisplayPanel + ParameterPanel (atas-bawah, collapsible)
- WorkspaceRightPanel: Splitter (ItemList + Settings cards)
- WorkspaceParameterPanel: Parameter Stack + Progress + Process/Cancel button
- WorkspacePageLayout: LeftPanel + RightPanel (kiri-kanan, visibility animation)
- WorkspaceView: Main container (QStackedWidget + animation + toast)
"""

from .workspace_display_panel import WorkspaceDisplayPanel
from .workspace_left_panel import WorkspaceLeftPanel
from .workspace_right_panel import WorkspaceRightPanel
from .workspace_parameter_panel import WorkspaceParameterPanel
from .workspace_page_layout import WorkspacePageLayout
from .workspace_view import WorkspaceView

__all__ = [
    "WorkspaceDisplayPanel",
    "WorkspaceLeftPanel",
    "WorkspaceRightPanel",
    "WorkspaceParameterPanel",
    "WorkspacePageLayout",
    "WorkspaceView",
]
