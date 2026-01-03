from PySide6.QtCore import QThread, Signal


class BaseAlgorithmWorker(QThread):
    """
    Generic background thread to execute algorithm logic.
    Provides standard signals and cancellation handling.
    """

    progress_updated = Signal(int, str)  # progress, message
    finished = Signal()
    error_occurred = Signal(str)

    def __init__(self, main_func, *args, **kwargs):
        """
        Initialize the worker.

        Args:
            main_func: The primary function to execute (e.g., AverageAlgorithm.main)
            *args, **kwargs: Arguments to pass to main_func
        """
        super().__init__()
        self.main_func = main_func
        self.args = args
        self.kwargs = kwargs
        self.stop_requested = False

    def run(self):
        """Execute the function and emit signals."""
        try:

            def update_progress(progress, message):
                self.progress_updated.emit(progress, message)

            def check_stop():
                return self.stop_requested

            # Inject callbacks into kwargs
            self.kwargs["update_progress"] = update_progress
            self.kwargs["stop_requested"] = check_stop

            # Execute
            self.main_func(*self.args, **self.kwargs)

            if not self.stop_requested:
                self.finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        """Request the worker to stop."""
        self.stop_requested = True
