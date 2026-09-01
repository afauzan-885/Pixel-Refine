from typing import Dict, List, Any
from PySide6.QtCore import QObject, QTimer, QThread


class ProcessManager(QObject):
    """
    Centralized manager for background tasks, timers, and animations.
    Ensures that switching contexts (e.g., batches) cleans up previous tasks.
    """

    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ProcessManager()
        return cls._instance

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks: Dict[str, List[Any]] = {}  # context_id -> [tasks]
        self._timers: Dict[str, List[QTimer]] = {}
        self._threads: Dict[str, List[QThread]] = {}

    def register_timer(self, context_id: str, timer: QTimer):
        """Register a timer to a specific context (e.g., 'batch_123')."""
        if context_id not in self._timers:
            self._timers[context_id] = []
        self._timers[context_id].append(timer)

    def register_thread(self, context_id: str, thread: QThread):
        """Register a thread to a specific context."""
        if context_id not in self._threads:
            self._threads[context_id] = []
        self._threads[context_id].append(thread)

    def cancel_context(self, context_id: str):
        """Cancel all tasks associated with a context."""
        # 1. Stop Timers
        if context_id in self._timers:
            for timer in self._timers[context_id]:
                try:
                    timer.stop()
                except RuntimeError:
                    pass
            self._timers[context_id].clear()

        # 2. Stop Threads
        if context_id in self._threads:
            for thread in self._threads[context_id]:
                try:
                    if thread.isRunning():
                        # Use requestInterruption if the thread supports it
                        if hasattr(thread, "requestInterruption"):
                            thread.requestInterruption()
                        # Some threads might have a stop() method
                        if hasattr(thread, "stop") and callable(thread.stop):  # type: ignore
                            thread.stop()  # type: ignore
                        thread.quit()
                        # Removed thread.wait(500) to avoid blocking UI thread
                except RuntimeError:
                    pass
            self._threads[context_id].clear()


def is_widget_alive(widget):
    """Safe check for PySide6 C++ objects."""
    if widget is None:
        return False
    try:
        # Pengecekan paling aman: akses parent()
        _ = widget.parent()
        return True
    except (RuntimeError, AttributeError):
        return False
