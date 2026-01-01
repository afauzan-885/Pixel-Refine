"""
Display Logic - Core business logic untuk DisplayPanel.
Handles: Grid management, thumbnail loading, preview display.
Separated dari UI untuk better maintainability dan testability.
"""

from pathlib import Path

# Thumbnail processor
from pixel_refine_desktop.enhance_stack.core.logic.thumbnail_processor import (
    ThumbnailBatchProcessor,
)

# Image display helper
from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import (
    display_image_in_zoomable,
    ImageLoaderThread,
)


class DisplayLogic:
    """
    Core logic untuk image display dan grid management.

    Responsibilities:
    - Manage batch state
    - Load thumbnails
    - Handle preview display
    - Manage grid items
    """

    def __init__(self):
        """Initialize display logic."""
        self.current_batch_id = None
        self.current_images = []
        self.thumbnail_processor = ThumbnailBatchProcessor(thumbnail_size=(128, 128))
        self.image_loader_thread = None
        self.last_preview_info = None
        self.grid_items = {}  # Map card_id -> image info

    def set_batch(self, batch_id, images):
        """
        Set current batch.

        Args:
            batch_id: ID dari batch
            images: List of image objects dengan .id dan .path attributes
        """
        self.current_batch_id = batch_id
        self.current_images = images if images else []
        self.grid_items.clear()

    def get_batch_info(self):
        """
        Get current batch info.

        Returns:
            dict: {'batch_id': int, 'images': list, 'count': int}
        """
        return {
            "batch_id": self.current_batch_id,
            "images": self.current_images,
            "count": len(self.current_images) if self.current_images else 0,
        }

    def is_batch_empty(self):
        """
        Check if current batch is empty.

        Returns:
            bool: True jika batch kosong atau tidak ada batch
        """
        return not self.current_images

    def load_thumbnail_async(self, image_path, callback):
        """
        Load thumbnail asinkron untuk image.

        Args:
            image_path: Path ke image file
            callback: Callable(QImage, str) - Called ketika thumbnail ready
        """
        self.thumbnail_processor.process_image(image_path, callback)

    def load_thumbnails_bulk_async(self, path_callback_pairs: list):
        """
        Load multiple thumbnails in bulk for maximum efficiency.
        path_callback_pairs: list of (image_path, callback)
        """
        if not path_callback_pairs:
            return

        image_paths = [p for p, c in path_callback_pairs]

        # Mapping path -> multiple callbacks (just in case)
        path_to_callbacks = {}
        for path, callback in path_callback_pairs:
            if path not in path_to_callbacks:
                path_to_callbacks[path] = []
            path_to_callbacks[path].append(callback)

        def bulk_callback(q_image, path):
            if path in path_to_callbacks:
                for cb in path_to_callbacks[path]:
                    if cb:
                        cb(q_image, path)

        self.thumbnail_processor.process_batch(image_paths, bulk_callback)

    def prepare_preview(self, image_path):
        """
        Prepare untuk preview display.

        Args:
            image_path: Path ke image untuk di-preview

        Returns:
            bool: True jika ready, False jika error
        """
        if not image_path or not Path(image_path).exists():
            return False

        self.last_preview_info = {"image_path": image_path, "timestamp": None}
        return True

    def display_preview(self, zoomable_widget, image_path):
        """
        Display preview di zoomable widget.

        Args:
            zoomable_widget: Zoomable widget untuk display
            image_path: Path ke image

        Returns:
            ImageLoaderThread: Thread yang loading image
        """
        # Stop previous loader jika masih berjalan
        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()

        # Load dan display image di zoomable widget
        self.image_loader_thread = display_image_in_zoomable(
            zoomable_widget, image_path
        )

        return self.image_loader_thread

    def register_grid_item(self, card_id, image_info):
        """
        Register card item untuk tracking.

        Args:
            card_id: ID dari card
            image_info: dict dengan image information
        """
        self.grid_items[card_id] = image_info

    def unregister_grid_item(self, card_id):
        """
        Unregister card item.

        Args:
            card_id: ID dari card
        """
        if card_id in self.grid_items:
            del self.grid_items[card_id]

    def get_grid_item_count(self):
        """
        Get jumlah items di grid.

        Returns:
            int: Jumlah grid items
        """
        return len(self.grid_items)

    def clear_all(self):
        """Clear semua state dan stop background tasks."""
        self.current_batch_id = None
        self.current_images.clear()
        self.grid_items.clear()
        self.last_preview_info = None
        self.thumbnail_processor.stop_all()

        if self.image_loader_thread and self.image_loader_thread.isRunning():
            self.image_loader_thread.quit()
            self.image_loader_thread.wait()

    def get_thumbnail_processor(self):
        """
        Get thumbnail processor instance.

        Returns:
            ThumbnailBatchProcessor: Current thumbnail processor
        """
        return self.thumbnail_processor

    def validate_image_path(self, image_path):
        """
        Validate image path.

        Args:
            image_path: Path ke image

        Returns:
            bool: True jika path valid
        """
        if not image_path:
            return False

        path = Path(image_path)
        return path.exists() and path.is_file()

    def get_selected_images(self):
        """
        Get list of selected images.

        Note: Requires selection tracking in ImageCard.
        For now returns current batch.

        Returns:
            list: List of selected image paths
        """
        return [img.path for img in self.current_images if hasattr(img, "path")]

    def detect_processed_results(self, original_path):
        """
        Detect processed result files related to an original image.
        Assumes naming convention: [OriginalName]_[Process].tif

        Args:
            original_path: Path to original image

        Returns:
            list: List of dicts {'name': 'Process Name', 'path': str}
        """
        if not original_path:
            return []

        import os
        import glob

        results = []
        original_name = os.path.splitext(os.path.basename(original_path))[0]
        # Safe name logic match
        safe_name = "".join(
            c for c in original_name if c.isalnum() or c in ("_", "-")
        ).rstrip()

        stack_dir = os.path.join("database", "stack")
        if not os.path.exists(stack_dir):
            return []

        # Search pattern
        pattern = os.path.join(stack_dir, f"{safe_name}_*.tif")
        matches = glob.glob(pattern)

        for path in matches:
            filename = os.path.basename(path)
            # Extract suffix: safe_name_SUFFIX.tif
            # Be careful if safe_name contains underscores
            if filename.startswith(safe_name + "_"):
                suffix_part = filename[
                    len(safe_name) + 1 :
                ]  # remove prefix and underscore
                process_name = os.path.splitext(suffix_part)[0]  # remove extension

                # Format name nicer
                display_name = process_name.replace("_", " ").title()

                results.append({"name": display_name, "path": os.path.abspath(path)})

        return sorted(results, key=lambda x: x["name"])
