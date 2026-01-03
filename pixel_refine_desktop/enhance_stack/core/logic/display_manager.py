"""
Display Manager for Enhance Stack.

Utilities untuk mengelola clear_display logic,
termasuk membersihkan grid, preview, cache, dan threads.

Mirrored dari panorama/working_left_panel.py untuk consistency.
"""

import os
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt, QObject, QMutex, QMutexLocker, QThread
from PySide6.QtGui import QPixmap

# Generic UI Library
from pixel_refine_desktop.ui.resources.GenericUILibrary import ImageCompareItem

# Image loading helper for RAW support
from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import (
    load_and_display_image,
)


class DisplayThreadManager(QObject):
    """
    Singleton Manager for handling Display-related threads (e.g. Thumbnails).
    Prevents 'QThread destroyed while thread is still running' errors by
    holding strong references until finished() signal is emitted.
    """

    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = DisplayThreadManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._active_threads = set()  # Strong references
        self._mutex = QMutex()

    def register_thread(self, thread: QThread):
        """
        Register a thread to safely manage its lifecycle.
        Pass ownership logic to this manager until the thread finishes.
        """
        if not thread:
            return

        with QMutexLocker(self._mutex):
            self._active_threads.add(thread)

        # Connect finished signal to cleanup
        # Using lambda with bound method keeps 'self' alive (Singleton)
        thread.finished.connect(lambda: self._cleanup_thread(thread))

        # Also clean up if thread is already finished (race condition safety)
        if thread.isFinished():
            self._cleanup_thread(thread)

    def _cleanup_thread(self, thread):
        """Remove thread from active set, allowing it to be GC'd."""
        with QMutexLocker(self._mutex):
            if thread in self._active_threads:
                self._active_threads.discard(thread)

    def stop_all_threads(self):
        """
        Request interruption for all managed threads.
        NON-BLOCKING: Does not wait for threads to finish, keeps UI responsive.
        Threads will be cleaned up automatically when they finish in background.
        """
        with QMutexLocker(self._mutex):
            # Create a copy to iterate safely
            threads = list(self._active_threads)

        for thread in threads:
            if isinstance(thread, QThread) and thread.isRunning():
                thread.requestInterruption()
                thread.quit()
                # Do NOT wait() here to avoid freezing UI.
                # Do NOT clear from _active_threads here immediately.


def clear_grid_display(
    grid_layout,
    scroll_area,
    empty_state_widget,
    title="No Batch Selected",
    message="Select a batch from the list to view images.",
):
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
        message="Select a batch from the list to view images.",
    )

    # Clear preview
    clear_preview_display(left_panel.preview_scene)

    # Show grid view (hide preview)
    left_panel.show_grid()


def display_processed_result(display_panel, image_path, update_dropdown=True):
    """
    Refactored display_processed_result logic.
    Display processed result image in Compare Mode (Default).
    Loads Original + Processed into ComparisonGraphicsItem.
    """
    if not os.path.exists(image_path):
        print(f"[DisplayManager] Error: Result file not found at {image_path}")
        return

    # Initialize zoom states dict if not exists
    if not hasattr(display_panel, "zoom_states"):
        display_panel.zoom_states = {}

    # SAVE current state if we are switching from another valid preview
    if (
        hasattr(display_panel, "current_preview_path")
        and display_panel.current_preview_path
    ):
        # Only save if we strictly have a scene items
        if display_panel.preview_scene.items():
            display_panel.zoom_states[display_panel.current_preview_path] = (
                display_panel.zoomable_preview.get_view_state()
            )

    display_panel.current_preview_path = image_path
    print(f"[DisplayManager] Showing processed result (Compare Mode): {image_path}")

    # 1. Clear Preview Scene
    display_panel.preview_scene.clear()

    # 2. Determine Original Image - Use helper that supports RAW files
    original_pixmap = None
    original_path = None
    if display_panel.logic.current_images:
        original_path = display_panel.logic.current_images[0].path
        print(f"[DisplayManager] Original image path: {original_path}")
        if os.path.exists(original_path):
            # Use load_and_display_image with caching enabled for reference
            original_pixmap = load_and_display_image(
                original_path,
                max_width=4000,  # Reasonable size for comparison
                max_height=4000,
                is_reference=True,
                batch_id=display_panel.current_batch_id,
            )
            if original_pixmap is None or original_pixmap.isNull():
                print(
                    f"[DisplayManager] WARNING: Failed to load original pixmap from {original_path}"
                )
                original_pixmap = None
            else:
                print(
                    f"[DisplayManager] Original pixmap loaded successfully: {original_pixmap.width()}x{original_pixmap.height()}"
                )
        else:
            print(
                f"[DisplayManager] WARNING: Original image file not found: {original_path}"
            )

    # Load processed image - Use helper for consistency
    processed_pixmap = load_and_display_image(
        image_path, max_width=4000, max_height=4000
    )
    if processed_pixmap is None or processed_pixmap.isNull():
        print(
            f"[DisplayManager] WARNING: Failed to load processed pixmap from {image_path}"
        )
        processed_pixmap = None
    else:
        print(
            f"[DisplayManager] Processed pixmap loaded successfully: {processed_pixmap.width()}x{processed_pixmap.height()}"
        )

    item = None

    if original_pixmap and processed_pixmap:
        # --- FIX: Scale Original to Match Processed (1:1 Comparison) ---
        # Checks if dimensions differ (e.g. upscaling)
        if (
            original_pixmap.width() != processed_pixmap.width()
            or original_pixmap.height() != processed_pixmap.height()
        ):
            print(
                f"[DisplayManager] Scaling original ({original_pixmap.width()}x{original_pixmap.height()}) "
                f"to match processed ({processed_pixmap.width()}x{processed_pixmap.height()})"
            )
            original_pixmap = original_pixmap.scaled(
                processed_pixmap.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,  # Match exact size
                Qt.TransformationMode.SmoothTransformation,
            )

        # 3. Create Comparison Item (Reusable from GenericUILibrary)
        print(f"[DisplayManager] Creating ImageCompareItem for comparison mode")
        item = ImageCompareItem(
            original_pixmap,
            processed_pixmap,
            left_label="Asli",
            right_label="Diproses",
        )
        display_panel.preview_scene.addItem(item)
        display_panel.preview_scene.setSceneRect(item.boundingRect())
        print(f"[DisplayManager] Comparison mode activated successfully")
    else:
        # Fallback
        print(
            f"[DisplayManager] WARNING: Falling back to single image display (original_pixmap={original_pixmap is not None}, processed_pixmap={processed_pixmap is not None})"
        )
        display_panel.logic.display_preview(display_panel.zoomable_preview, image_path)
        if display_panel.preview_scene.items():
            item = display_panel.preview_scene.items()[0]

    # RESTORE State or Fit to View
    # For comparison mode, always fit to view on first display (ignore saved state)
    # This ensures the full comparison is visible when first shown
    if image_path in display_panel.zoom_states and not (
        original_pixmap and processed_pixmap
    ):
        # Only restore zoom state for single image view, not comparison mode
        print(
            f"[DisplayManager] Restoring zoom state for {os.path.basename(image_path)}"
        )
        display_panel.zoomable_preview.set_view_state(
            display_panel.zoom_states[image_path]
        )
    else:
        # Always fit to view for comparison mode or first view
        if original_pixmap and processed_pixmap:
            print(
                f"[DisplayManager] Comparison mode: fitting to view (ignoring saved zoom state)"
            )
        else:
            print(f"[DisplayManager] First view, fitting to view")
        # Reset first to ensure clean state then fit
        display_panel.zoomable_preview.reset_zoom()
        display_panel.zoomable_preview.zoom_to_fit()  # Uses scene rect

    # 3. Update Dropdown logic
    if update_dropdown and display_panel.logic.current_images:
        # Show save button since we are displaying a result
        display_panel.save_overlay.show()
        display_panel.save_overlay.raise_()
        first_img_path = display_panel.logic.current_images[0].path
        results = display_panel.logic.detect_processed_results(first_img_path)

        display_panel.current_results_map = {r["name"]: r["path"] for r in results}
        options = [r["name"] for r in results]

        block = display_panel.result_selector.blockSignals(True)
        display_panel.result_selector.clear()
        display_panel.result_selector.addItems(options)

        current_name = None
        for name, path in display_panel.current_results_map.items():
            if os.path.normpath(path) == os.path.normpath(image_path):
                current_name = name
                break

        if current_name:
            display_panel.result_selector.setCurrentText(current_name)

        display_panel.result_selector.blockSignals(block)

    display_panel.show_preview(show_dropdown=True)
