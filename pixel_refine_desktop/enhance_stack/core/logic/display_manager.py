"""
Display Manager for Enhance Stack.

Utilities untuk mengelola clear_display logic,
termasuk membersihkan grid, preview, cache, dan threads.

Mirrored dari panorama/working_left_panel.py untuk consistency.
"""

from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt


def clear_grid_display(grid_layout, scroll_area, empty_state_widget, title="No Batch Selected", message="Select a batch from the list to view images."):
    """
    Clear grid view dan tampilkan empty state.
    
    Args:
        grid_layout: QHBoxLayout containing grid items
        scroll_area: QScrollArea widget
        empty_state_widget: EmptyState widget untuk tampilan kosong
        title: Title untuk empty state
        message: Message untuk empty state
    """
    # Clear grid items
    while grid_layout.count() > 0:
        item = grid_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
    
    # Show empty state
    empty_state_widget.set_text(title, message)
    empty_state_widget.setVisible(True)
    scroll_area.setVisible(False)


def clear_preview_display(preview_scene):
    """
    Clear preview/zoom view.
    
    Args:
        preview_scene: QGraphicsScene untuk preview
    """
    if preview_scene:
        preview_scene.clear()


def reset_display_state(left_panel):
    """
    Reset semua display state di left panel.
    
    Args:
        left_panel: LeftPanel instance
    """
    left_panel.current_batch_id = None
    left_panel.last_preview_info = None
    
    # Clear grid
    clear_grid_display(
        left_panel.grid_layout,
        left_panel.scroll_area,
        left_panel.empty_state,
        title="No Batch Selected",
        message="Select a batch from the list to view images."
    )
    
    # Clear preview
    clear_preview_display(left_panel.preview_scene)
    
    # Show grid view (hide preview)
    left_panel.show_grid()
