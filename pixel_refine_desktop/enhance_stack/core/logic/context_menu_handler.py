"""
Context Menu Handler - Handles context menu operations for image grid.
Manages right-click menu creation and actions like set reference and delete.
"""

from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
from typing import Optional, Any
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    is_widget_alive,
)


class ContextMenuHandler:
    """Handles context menu operations for image grid."""

    def __init__(self, parent_panel):
        """
        Initialize ContextMenuHandler.

        Args:
            parent_panel: Reference to DisplayPanel for accessing UI components
        """
        self.panel = parent_panel

    def create_context_menu(self, card_under_mouse: Optional[Any]) -> QMenu:
        """
        Create context menu for grid area.

        Args:
            card_under_mouse: ImageCard widget under mouse, or None

        Returns:
            QMenu: Configured context menu
        """
        menu = QMenu(self.panel)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 25px 5px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #F0F0F0;
                color: #000000;
            }
            QMenu::separator {
                height: 1px;
                background: #E0E0E0;
                margin: 5px 0px;
            }
        """
        )

        from pixel_refine_desktop.ui.views.settings.General.Language import language_config
        # 1. Select Reference Image (Only if exactly one card is right-clicked)
        if card_under_mouse:
            ref_path = card_under_mouse._image_path
            action_ref = QAction(language_config.CORE_SELECT_REF_IMAGE, self.panel)
            action_ref.triggered.connect(lambda: self.set_as_reference(ref_path))
            menu.addAction(action_ref)
            menu.addSeparator()

        # 2. Delete Selected Images
        if self.panel.selection_manager.selected_thumbnails:
            action_del = QAction(
                f"{language_config.CORE_DELETE_IMAGES} ({len(self.panel.selection_manager.selected_thumbnails)})",
                self.panel,
            )
            action_del.triggered.connect(self.panel._handle_delete_action)
            menu.addAction(action_del)

        return menu

    def set_as_reference(self, image_path: str):
        """
        Set image as reference via controller.

        Args:
            image_path: Path to image to set as reference
        """
        if self.panel.current_batch_id and self.panel.controller:
            if self.panel.controller.set_reference_image(
                self.panel.current_batch_id, image_path
            ):
                self.panel._refresh_current_batch()

    def find_card_under_mouse(self) -> Optional[Any]:
        """
        Find card widget under mouse cursor.

        Returns:
            ImageCard widget under mouse, or None
        """
        for card_id, card in self.panel.all_cards.items():
            # Safety check: ensure widget is still alive before accessing
            if is_widget_alive(card):
                try:
                    if card.underMouse():
                        return card
                except RuntimeError:
                    # Widget was deleted between check and access
                    continue
        return None
