"""
pixel_refine_mobile/core_logic/algorithm_processor.py
------------------------------------------------------
Algorithm processing thread.
Direct port from desktop's AlgorithmProcessorThread.
Same action dispatch map for API parity.
"""

from PySide6.QtCore import QThread, Signal


class AlgorithmProcessorThread(QThread):
    """
    Thread for executing algorithm processing pipeline.
    Takes a settings dict and sequentially runs selected algorithms.
    """

    progress_update = Signal(int, str)    # percent, message
    finished_processing = Signal()
    error_occurred = Signal(str)

    def __init__(self, batch_id: int, settings: dict, parent=None):
        super().__init__(parent)
        self.batch_id = batch_id
        self.settings = settings
        self._is_running = True
        self._is_cancelled = False

    def run(self):
        """Execute selected algorithms. Same dispatch as desktop."""
        try:
            total_categories = len([k for k, v in self.settings.items()
                                    if v and "No " not in v and v != "None"])
            completed = 0

            for category, algo_name in self.settings.items():
                if not self._is_running:
                    break

                # Skip "No X" or "None" selections
                if not algo_name or algo_name in ["None", "No Alignment",
                                                    "No Super Resolution",
                                                    "No Denoising"]:
                    continue

                completed += 1
                percent = int((completed / total_categories) * 100) if total_categories > 0 else 100
                self.progress_update.emit(percent, f"Running {category}: {algo_name}...")

                # Placeholder: dispatch to actual algorithm
                # In production, this would call running_orb, running_akaze, etc.
                self._execute_algorithm(category, algo_name)

            self.finished_processing.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def _execute_algorithm(self, category: str, algo_name: str):
        """
        Placeholder for actual algorithm execution.
        In production, this dispatches to running_* functions.

        Args:
            category: "alignment", "denoising", or "super_resolution"
            algo_name: Algorithm name (e.g., "AKAZE", "Similarity", "WSR")
        """
        # Placeholder — logs the action
        print(f"[AlgorithmProcessor] {category}/{algo_name} — placeholder execution")

        # Check for cancellation
        if self._is_cancelled:
            return

        # Simulate processing time
        import time
        time.sleep(0.5)

    def stop(self):
        """Request processing to stop."""
        self._is_running = False
        self._is_cancelled = True
