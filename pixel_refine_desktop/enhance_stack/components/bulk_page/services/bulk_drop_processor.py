"""
Background processor for bulk drag-and-drop imports.

The drop event itself must return to the Qt event loop immediately to keep
the UI responsive. This module provides a QThread that performs the
expensive validation (per-file os.stat, extension filtering) off the UI
thread and then dispatches the validated chunk back to the existing
import pipeline.
"""
from __future__ import annotations

import os

from PIL import Image
from PySide6.QtCore import QThread, Signal

from config import SUPPORTED_FORMATS

# Pre-compute extension sets once at import time. Re-computing these per
# drop event in a tight loop was a measurable source of allocation churn.
_SUPPORTED_EXTS: frozenset = frozenset(
    ext.lower() for fmt_list in SUPPORTED_FORMATS.values() for ext in fmt_list
)
_TIFF_EXTS: tuple = tuple(
    ext.lower() for ext in SUPPORTED_FORMATS.get("tiff", [])
)
_NON_TIFF_EXTS: tuple = tuple(
    ext.lower()
    for fmt, ext_list in SUPPORTED_FORMATS.items()
    if fmt != "tiff"
    for ext in ext_list
)

_TIFF_COMPRESSIONS_TO_CONVERT = frozenset({
    "tiff_lzw",
    "tiff_zip",
    "packbits",
    "jpeg",
    "lzw",
})


class BulkDropProcessor(QThread):
    """Validate dropped paths and prepare an import chunk off the UI thread.

    Emits :pyattr:`prepared` on the UI thread with the list of paths that
    are safe to feed to the existing import pipeline. The drop event
    itself only needs to start this thread and return.
    """

    prepared = Signal(list)            # (filtered_image_paths)
    failed = Signal(str)               # (error_message)

    def __init__(self, image_paths: list, parent=None):
        super().__init__(parent)
        self._paths = list(image_paths)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        try:
            # Dedupe while preserving order so the user sees paths in the
            # same sequence they dropped them.
            unique_files = list(dict.fromkeys(self._paths))
            valid: list = []
            for path in unique_files:
                if self._cancelled:
                    return
                if not path:
                    continue
                ext = os.path.splitext(path)[1].lower()
                if ext not in _SUPPORTED_EXTS:
                    continue
                # Cheap existence check; the import worker also tolerates
                # missing files but skipping them here keeps the queue short.
                if os.path.isfile(path):
                    valid.append(path)

            if self._cancelled:
                return
            self.prepared.emit(valid)
        except Exception as exc:  # pragma: no cover - defensive
            self.failed.emit(str(exc))


def sniff_tiff_needs_conversion(path: str) -> bool:
    """Return True if the TIFF at *path* uses a compression that must be
    re-encoded before the import pipeline accepts it.

    Lives at module scope so the drop processor can call it without
    paying a function-lookup cost per file. Raises nothing: corrupt TIFFs
    are reported as not-needing-conversion and the importer will surface
    the actual error.
    """
    try:
        with Image.open(path) as img:
            compression = img.info.get("compression", "none").lower()
            return compression in _TIFF_COMPRESSIONS_TO_CONVERT
    except Exception:
        return False
