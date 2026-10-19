"""
Display Manager for Enhance Stack.

Utilities untuk mengelola clear_display logic,
termasuk membersihkan grid, preview, cache, dan threads.

Mirrored dari panorama/working_left_panel.py untuk consistency.
"""

import os
from PySide6.QtCore import Qt, QObject, QMutex, QMutexLocker, QThread, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem

# Generic UI Library
from UILibrary import ImageCompareItem

# Image loading helper for RAW support
from pixel_refine_desktop.enhance_stack.core.logic.image_display_helper import (
    ComparisonImageLoaderThread,
)


class _ComparisonLoadReceiver(QObject):
    """Deliver worker results to the display panel's owning UI thread."""

    def __init__(self, display_panel, request_id, update_dropdown, perf_mark):
        super().__init__(display_panel)
        self.display_panel = display_panel
        self.request_id = request_id
        self.update_dropdown = update_dropdown
        self.perf_mark = perf_mark

    @Slot(QImage, QImage, str, str)
    def images_loaded(self, original, result, _original_path, result_path):
        _finish_comparison_load(
            self.display_panel,
            self.request_id,
            result_path,
            original,
            result,
            self.update_dropdown,
            self.perf_mark,
        )

    @Slot(int)
    def load_progress(self, percent):
        if self.request_id == getattr(
            self.display_panel, "_comparison_request_id", None
        ):
            self.display_panel._show_comparison_loading(self.request_id, percent)

    @Slot()
    def start_pending(self):
        _start_pending_comparison(self.display_panel)


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
    """Request an asynchronous decode, then install the comparison on the UI thread."""
    if not os.path.exists(image_path):
        print(f"[DisplayManager] Error: Result file not found at {image_path}")
        return

    from pixel_refine_desktop.app_core import perf_probe

    _mark = perf_probe.perf_mark("display_processed_result")

    # Initialize zoom states dict if not exists
    if not hasattr(display_panel, "zoom_states"):
        display_panel.zoom_states = {}

    # Save current state before replacing its scene.
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
    display_panel.preview_scene.clear()
    original_path = None
    if display_panel.logic.current_images:
        original_path = display_panel.logic.current_images[0].path
        print(f"[DisplayManager] Original image path: {original_path}")

    request_id = getattr(display_panel, "_comparison_request_id", 0) + 1
    display_panel._comparison_request_id = request_id
    display_panel._show_comparison_loading(request_id, 0)
    request = (request_id, image_path, original_path, update_dropdown, _mark)
    active = getattr(display_panel, "_comparison_loader_thread", None)
    if active is not None and active.isRunning():
        # Keep only the newest request and serialize full-resolution decoding
        # so rapidly switching results cannot multiply peak memory use.
        display_panel._pending_comparison_request = request
        receiver = getattr(display_panel, "_comparison_load_receiver", None)
        if receiver is not None:
            active.finished.connect(receiver.start_pending)
    else:
        _start_comparison_load(display_panel, request)

    display_panel.show_preview(show_dropdown=True)


def cancel_pending_comparison(display_panel):
    """Invalidate late loader results when the user leaves result preview."""
    display_panel._comparison_request_id = (
        getattr(display_panel, "_comparison_request_id", 0) + 1
    )
    display_panel._pending_comparison_request = None
    display_panel._hide_comparison_loading()


def _start_pending_comparison(display_panel):
    request = getattr(display_panel, "_pending_comparison_request", None)
    display_panel._pending_comparison_request = None
    active = getattr(display_panel, "_comparison_loader_thread", None)
    if request is not None and (active is None or not active.isRunning()):
        _start_comparison_load(display_panel, request)


def _start_comparison_load(display_panel, request):
    request_id, image_path, original_path, update_dropdown, perf_mark = request
    if not original_path or not os.path.exists(original_path):
        print(f"[DisplayManager] Original image unavailable: {original_path}")
        original_path = ""

    loader = ComparisonImageLoaderThread(
        original_path,
        image_path,
        batch_id=display_panel.current_batch_id,
    )
    display_panel._comparison_loader_thread = loader
    receiver = _ComparisonLoadReceiver(
        display_panel, request_id, update_dropdown, perf_mark
    )
    display_panel._comparison_load_receiver = receiver
    loader.load_progress.connect(receiver.load_progress)
    loader.images_loaded.connect(receiver.images_loaded)
    loader.error_occurred.connect(
        lambda message: print(f"[DisplayManager] {message}")
    )
    DisplayThreadManager.instance().register_thread(loader)
    loader.start()


def _finish_comparison_load(
    display_panel, request_id, image_path, original_image, result_image,
    update_dropdown, perf_mark,
):
    perf_mark.end()
    if (
        request_id != getattr(display_panel, "_comparison_request_id", None)
        or image_path != getattr(display_panel, "current_preview_path", None)
    ):
        return

    if result_image.isNull():
        print(f"[DisplayManager] Processed image could not be decoded: {image_path}")
        display_panel._hide_comparison_loading(request_id)
        return

    original_pixmap = (
        QPixmap.fromImage(original_image) if not original_image.isNull() else None
    )
    original_image = QImage()
    processed_pixmap = QPixmap.fromImage(result_image)
    result_image = QImage()
    if processed_pixmap.isNull():
        print(f"[DisplayManager] Processed image could not be converted: {image_path}")
        display_panel._hide_comparison_loading(request_id)
        return

    display_panel.preview_scene.clear()
    if original_pixmap is not None and not original_pixmap.isNull():
        print(
            f"[DisplayManager] Original pixmap loaded successfully: "
            f"{original_pixmap.width()}x{original_pixmap.height()}"
        )
        print(
            f"[DisplayManager] Processed pixmap loaded successfully: "
            f"{processed_pixmap.width()}x{processed_pixmap.height()}"
        )
        print("[DisplayManager] Creating ImageCompareItem for comparison mode")
        item = ImageCompareItem(
            original_pixmap,
            processed_pixmap,
            left_label="Asli",
            right_label="Diproses",
        )
        display_panel.preview_scene.addItem(item)
        display_panel.preview_scene.setSceneRect(item.boundingRect())
        is_comparison = True
        print("[DisplayManager] Comparison mode activated successfully")
    else:
        print("[DisplayManager] Showing processed image without comparison")
        item = QGraphicsPixmapItem(processed_pixmap)
        item.setShapeMode(QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        display_panel.preview_scene.addItem(item)
        display_panel.preview_scene.setSceneRect(item.boundingRect())
        is_comparison = False

    if image_path in display_panel.zoom_states and not is_comparison:
        display_panel.zoomable_preview.set_view_state(
            display_panel.zoom_states[image_path]
        )
    else:
        display_panel.zoomable_preview.reset_zoom()
        display_panel.zoomable_preview.zoom_to_fit()

    if update_dropdown and display_panel.logic.current_images:
        display_panel.save_overlay.show()
        display_panel.save_overlay.raise_()
        first_img_path = display_panel.logic.current_images[0].path
        results = display_panel.logic.detect_processed_results(first_img_path)
        display_panel.current_results_map = {r["name"]: r["path"] for r in results}
        block = display_panel.result_selector.blockSignals(True)
        display_panel.result_selector.clear()
        display_panel.result_selector.addItems(display_panel.current_results_map)
        for name, path in display_panel.current_results_map.items():
            if os.path.normpath(path) == os.path.normpath(image_path):
                display_panel.result_selector.setCurrentText(name)
                break
        display_panel.result_selector.blockSignals(block)

    display_panel.show_preview(show_dropdown=True)
    display_panel._show_comparison_loading(request_id, 100)
