"""
app_bridge.py
-------------
Bridge between QML and Python logic for Mobile.
Stores current tool state for screen navigation.
"""

from PySide6.QtCore import QObject, Signal, Slot, Property


class AppBridge(QObject):
    """
    Bridge data between QML (Mobile) and Python.

    Signals:
        tool_requested(str)  — Emitted when user taps a tool button.
        progress_changed(int)— Emitted when loading progress changes.
    """

    tool_requested = Signal(str)
    progress_changed = Signal(int)

    loadingProgressChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading_progress = 0
        self._current_tool = "Home"

    def _get_progress(self) -> int:
        return self._loading_progress

    def _set_progress(self, val: int):
        if self._loading_progress != val:
            self._loading_progress = val
            self.loadingProgressChanged.emit(val)
            self.progress_changed.emit(val)

    loadingProgress = Property(
        int, _get_progress, _set_progress, notify=loadingProgressChanged,
    )

    @Slot(str)
    def openTool(self, tool_name: str):
        """Called from QML when user taps a tool button."""
        self._current_tool = tool_name
        self.tool_requested.emit(tool_name)

    @Slot(int)
    def setProgress(self, value: int):
        """Update loading progress from Python or QML."""
        self._set_progress(value)

    @property
    def current_tool(self):
        return self._current_tool
