"""
pixel_refine_mobile/controllers/processing_controller.py
--------------------------------------------------------
Image processing controller.
Desktop equivalent: ImageProcessingController + AlgorithmProcessorThread.
"""

from PySide6.QtCore import QObject, Signal
from pixel_refine_mobile.core_logic.algorithm_processor import AlgorithmProcessorThread


class ProcessingController(QObject):
    """Controller for image processing operations."""

    processing_started = Signal(int)           # batch_id
    processing_progress = Signal(int, int, str)  # percent, items_left, message
    processing_completed = Signal(int, str)    # batch_id, result_path
    processing_error = Signal(int, str)        # batch_id, error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._thread = None
        self._is_running = False

    def start_processing(self, batch_id: int, settings: dict):
        """
        Start algorithm processing for a batch.
        settings format: {"alignment": "AKAZE", "super_resolution": "WSR", "denoising": "Similarity"}
        Identical to desktop's AlgorithmProcessorThread(batch_id, settings).
        """
        if self._is_running:
            print("[ProcessingController] Already processing, ignoring start request")
            return

        self._is_running = True
        self.processing_started.emit(batch_id)

        self._thread = AlgorithmProcessorThread(
            batch_id=batch_id,
            settings=settings,
            parent=self,
        )
        self._thread.progress_update.connect(
            lambda pct, msg: self.processing_progress.emit(batch_id, 0, msg)
        )
        self._thread.finished_processing.connect(
            lambda: self._on_finished(batch_id)
        )
        self._thread.error_occurred.connect(
            lambda err: self._on_error(batch_id, err)
        )
        self._thread.start()

    def cancel_processing(self):
        """Cancel current processing."""
        if self._thread and self._is_running:
            self._thread.stop()
            self._is_running = False

    def _on_finished(self, batch_id: int):
        self._is_running = False
        self.processing_completed.emit(batch_id, "")

    def _on_error(self, batch_id: int, error: str):
        self._is_running = False
        self.processing_error.emit(batch_id, error)

    @property
    def is_running(self) -> bool:
        return self._is_running
