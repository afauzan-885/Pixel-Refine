"""
Grid Manager - Handles all grid-related operations for DisplayPanel.
Manages grid population, incremental loading, and viewport detection.
"""

from PySide6.QtCore import QTimer, QPoint, QRect
from PySide6.QtWidgets import QWidget
from typing import Optional, Callable, List, Dict, Any
from pixel_refine_desktop.enhance_stack.core.logic.process_manager import (
    ProcessManager,
    is_widget_alive,
)


class GridManager:
    """Manages grid operations including population and viewport detection."""

    def __init__(self, parent_panel):
        """
        Initialize GridManager.

        Args:
            parent_panel: Reference to DisplayPanel for accessing UI components
        """
        self.panel = parent_panel
        self._populate_queue = []
        self._populate_timer = None
        self._real_paths_for_sync = []

        # Staged load timer (Extreme Optimization for Massive Batch)
        self.staged_load_timer = QTimer(self.panel)
        self.staged_load_timer.setSingleShot(True)
        self.staged_load_timer.setInterval(3000)  # 3s "breathing room"
        self.staged_load_timer.timeout.connect(self._start_background_sync)

    def clear_grid(self):
        """Remove all widgets from grid container."""
        # Stop all animations before clearing
        self.panel.grid_animator.stop_all()

        # Ensure batch update is OFF so rendering can happen
        self.panel.grid_container.set_batch_update(False)
        self.panel.grid_container.clear_items()

    def populate_grid_incremental(self, visual_images: List[Any]):
        """
        Start incremental population of grid with images.

        Args:
            visual_images: List of image objects to populate
        """
        # Prepare incremental population to avoid UI freeze
        self._populate_queue = list(visual_images)

        if self._populate_timer and self._populate_timer.isActive():
            self._populate_timer.stop()

        self._populate_timer = QTimer(self.panel)
        self._populate_timer.timeout.connect(self._process_incremental_population)

        # Register to ProcessManager
        ProcessManager.instance().register_timer(
            "display_populate", self._populate_timer
        )

        # Start population: 15 images per 30ms (Smooth & Fast)
        self._populate_timer.start(30)

    def _process_incremental_population(self):
        """Slots to add images to grid in chunks to avoid UI hang."""
        if not self._populate_queue:
            self._populate_timer.stop()
            self.panel.grid_container.set_batch_update(False)
            # Final check for thumbnails (Prioritas Viewport Selesai)
            self.panel._check_visible_cards()

            # Start "Breathing Room" timer sebelum sinkronisasi latar belakang masif
            if self._real_paths_for_sync:
                self.staged_load_timer.start()
            return

        # Add 15 images per tick
        CHUNK_SIZE = 15
        for _ in range(CHUNK_SIZE):
            if not self._populate_queue:
                break

            img = self._populate_queue.pop(0)

            # Check if this is a Zombie (pending deletion)
            is_zombie = (
                hasattr(img, "__class__") and img.__class__.__name__ == "ZombieImg"
            )

            from pixel_refine_desktop.ui.resources.GenericUILibrary import ImageCard

            card = ImageCard(card_id=str(img.id), size=110)
            card._image_path = img.path

            if not is_zombie:
                card.double_clicked.connect(self.panel._on_card_double_clicked)
                card.clicked.connect(
                    lambda cid, event, c=card: self.panel._on_card_clicked(
                        cid, event, c
                    )
                )

                self.panel.all_cards[str(img.id)] = card
                self.panel.grid_container.add_item(card)
                self.panel.logic.register_grid_item(str(img.id), {"path": img.path})
            else:
                self.panel.all_cards[str(img.id)] = card
                self.panel.grid_container.add_item(card)
                # ZOMBIE LOGIC: Immediately queue for removal via Manager
                self.panel.deletion_manager.queue_zombie_card(str(img.id), card)

        # Update progress header (delegates to UIStateManager)
        self.panel._update_header_title()

        # Prioritaskan viewport secara agresif selama populasi
        if len(self._populate_queue) % 3 == 0:  # Tiap 3 ticks
            self.panel._check_visible_cards()

    def _start_background_sync(self):
        """Trigger background synchronization after breathing room ends."""
        if self._real_paths_for_sync:
            # print(
            #     f"[GridManager] Background Sync Stage started for {len(self._real_paths_for_sync)} images."
            # )
            self.panel.logic.load_thumbnails_bulk_async(
                [(p, None) for p in self._real_paths_for_sync]
            )
            self._real_paths_for_sync = []  # Clear memory

    def set_sync_paths(self, paths: List[str]):
        """
        Set paths for background sync.

        Args:
            paths: List of image paths to sync
        """
        self._real_paths_for_sync = paths

    def stop_staged_timer(self):
        """Stop the staged load timer."""
        self.staged_load_timer.stop()

    def is_widget_in_viewport(self, widget: QWidget) -> bool:
        """
        Check if widget is visible in GridContainer viewport.
        Used for viewport-aware animation optimization.

        Args:
            widget: Widget to check

        Returns:
            True if widget is in viewport, False otherwise
        """
        if not is_widget_alive(widget) or not widget.isVisible():
            return False

        try:
            # Access viewport from QScrollArea inside GridContainer
            viewport = self.panel.grid_container.viewport()
            if not viewport:
                return False

            # Get visible area (0,0, w, h)
            visible_rect = viewport.rect()

            # Map widget position (local) to viewport position
            widget_pos = widget.mapTo(viewport, QPoint(0, 0))
            widget_rect = QRect(widget_pos, widget.size())

            # Check if widget rect intersects with viewport rect
            return visible_rect.intersects(widget_rect)
        except Exception:
            return False
