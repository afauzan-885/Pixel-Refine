"""
pixel_refine_mobile/core/app_bridge.py
---------------------------------------
Bridge antara QML dan logika Python untuk versi Mobile.

Identik dengan pola signal-slot yang digunakan di Desktop,
sehingga handler yang sama bisa dipakai di kedua platform.

Cara pakai:
    from pixel_refine_mobile.core.app_bridge import AppBridge
    bridge = AppBridge()
    bridge.tool_requested.connect(on_tool_requested)
"""

from PySide6.QtCore import QObject, Signal, Slot, Property


class AppBridge(QObject):
    """
    Bridge data antara QML (Mobile) dan Python.

    Signal:
        tool_requested(str)  — dipancarkan saat user menekan tombol di QML.
                               Setara dengan clicked.connect() di Desktop.
        progress_changed(int)— dipancarkan saat loading progress berubah.

    Slot (dapat dipanggil dari QML):
        openTool(name)       — membuka tool berdasarkan nama.
        setProgress(value)   — update progress bar.
    """

    # ── Signals ───────────────────────────────────────────────────────────────
    tool_requested   = Signal(str)    # dipancarkan oleh openTool()
    progress_changed = Signal(int)    # alias untuk loadingProgressChanged

    # ── Internal ──────────────────────────────────────────────────────────────
    loadingProgressChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading_progress = 0

    # ── Property: loadingProgress (dengan NOTIFY agar QML bisa bind) ──────────
    def _get_progress(self) -> int:
        return self._loading_progress

    def _set_progress(self, val: int):
        if self._loading_progress != val:
            self._loading_progress = val
            self.loadingProgressChanged.emit(val)
            self.progress_changed.emit(val)

    loadingProgress = Property(
        int,
        _get_progress,
        _set_progress,
        notify=loadingProgressChanged,
    )

    # ── Slots (dipanggil dari QML via MouseArea.onClicked, dll.) ──────────────

    @Slot(str)
    def openTool(self, tool_name: str):
        """
        Dipanggil dari QML saat user menekan tombol.
        Memancarkan sinyal tool_requested ke handler Python.

        Contoh di QML:
            MouseArea { onClicked: appBridge.openTool("Denoising") }

        Contoh connect di Python (identik dengan Desktop):
            bridge.tool_requested.connect(on_tool_click)
        """
        self.tool_requested.emit(tool_name)

    @Slot(int)
    def setProgress(self, value: int):
        """Update loading progress dari Python atau QML."""
        self._set_progress(value)
