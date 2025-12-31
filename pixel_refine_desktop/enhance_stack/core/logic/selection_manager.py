from PySide6.QtCore import QObject, Qt
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    is_widget_alive,
)


class SelectionManager(QObject):
    """
    Manages selection logic for DisplayPanel's grid.
    Handles click, multi-select (Ctrl/Shift), and keyboard navigation.
    """

    def __init__(self, display_panel):
        super().__init__()
        self.panel = display_panel

        # State
        self.selected_thumbnails = set()
        self.last_selected_card_id = None
        self.selection_anchor_id = None

    def clear(self):
        """Reset selection state completely."""
        self.clear_selection()
        self.selected_thumbnails.clear()
        self.last_selected_card_id = None
        self.selection_anchor_id = None

    def clear_selection(self):
        """Deselect all visible cards visually."""
        # Clean visually
        for card_id in list(self.selected_thumbnails):
            if card_id in self.panel.all_cards:
                card = self.panel.all_cards[card_id]
                if is_widget_alive(card):
                    try:
                        card.deselect()
                    except RuntimeError:
                        pass
        self.selected_thumbnails.clear()

    def select_range(self, start_card_id, end_card_id):
        """Select range between two cards."""
        card_ids_in_order = list(self.panel.all_cards.keys())

        try:
            start_idx = card_ids_in_order.index(start_card_id)
            end_idx = card_ids_in_order.index(end_card_id)
        except ValueError:
            return

        if start_idx > end_idx:
            start_idx, end_idx = end_idx, start_idx

        for i in range(start_idx, end_idx + 1):
            card_id = card_ids_in_order[i]
            if card_id in self.panel.all_cards:
                self.panel.all_cards[card_id].select()
                self.selected_thumbnails.add(card_id)

    def select_all(self):
        """Select all images in current batch."""
        self.clear_selection()

        for card_id, card in self.panel.all_cards.items():
            card.select()
            self.selected_thumbnails.add(card_id)

        if self.panel.all_cards:
            last_id = list(self.panel.all_cards.keys())[-1]
            self.last_selected_card_id = last_id
            self.selection_anchor_id = (
                list(self.panel.all_cards.keys())[0]
                if not self.selection_anchor_id
                else self.selection_anchor_id
            )

    def handle_card_clicked(self, card_id, event, card_widget):
        """Handle click event from ImageCard."""
        modifiers = event.modifiers()

        # Single Click
        if modifiers == Qt.KeyboardModifier.NoModifier:
            self.clear_selection()
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            self.last_selected_card_id = card_id
            self.selection_anchor_id = card_id

        # Ctrl + Click
        elif modifiers == Qt.KeyboardModifier.ControlModifier:
            card_widget.toggle_selection()
            if card_widget.is_selected():
                self.selected_thumbnails.add(card_id)
            else:
                self.selected_thumbnails.discard(card_id)
            self.last_selected_card_id = card_id
            self.selection_anchor_id = card_id

        # Shift + Click
        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
            if self.selection_anchor_id and self.selection_anchor_id != card_id:
                self.clear_selection()
                self.select_range(self.selection_anchor_id, card_id)
                self.last_selected_card_id = card_id
            else:
                self.clear_selection()
                card_widget.select()
                self.selected_thumbnails.add(card_id)
                self.last_selected_card_id = card_id
                self.selection_anchor_id = card_id

        # Focus panel to ensure keyboard events work immediately
        self.panel.setFocus()

    def navigate_selection(self, key, shift_held):
        """Handle arrow key navigation."""
        if (
            self.panel.display_stack.currentIndex() != 0
            or not self.panel.current_batch_id
        ):
            return

        if not self.panel.all_cards:
            return

        card_ids_in_order = list(self.panel.all_cards.keys())
        total_items = len(card_ids_in_order)

        # 1. Determine starting point
        current_id = self.last_selected_card_id
        if not current_id or current_id not in card_ids_in_order:
            current_id = card_ids_in_order[0]
            current_idx = 0
        else:
            current_idx = card_ids_in_order.index(current_id)

        # 2. Calculate target index
        columns = self.panel.grid_container.columns
        new_idx = current_idx

        if key == Qt.Key.Key_Left:
            new_idx = max(0, current_idx - 1)
        elif key == Qt.Key.Key_Right:
            new_idx = min(total_items - 1, current_idx + 1)
        elif key == Qt.Key.Key_Up:
            new_idx = max(0, current_idx - columns)
        elif key == Qt.Key.Key_Down:
            new_idx = min(total_items - 1, current_idx + columns)

        if new_idx == current_idx:
            return

        new_id = card_ids_in_order[new_idx]
        new_card = self.panel.all_cards[new_id]

        # 3. Perform Selection
        if shift_held:
            if not self.selection_anchor_id:
                self.selection_anchor_id = current_id
            self.clear_selection()
            self.select_range(self.selection_anchor_id, new_id)
        else:
            self.clear_selection()
            new_card.select()
            self.selected_thumbnails.add(new_id)
            self.selection_anchor_id = new_id

        self.last_selected_card_id = new_id
        self.panel.grid_container.ensureWidgetVisible(new_card)

    def get_selected_ids(self):
        return list(self.selected_thumbnails)
