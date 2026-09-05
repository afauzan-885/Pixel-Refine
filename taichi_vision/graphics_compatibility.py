"""Conservative runtime policy for legacy desktop graphics drivers.

The compatibility profile keeps execution on the selected GPU backend.  It
changes memory and scheduling policy only; it never substitutes CPU work.
"""

from __future__ import annotations

import os


_FALSE_VALUES = {"0", "false", "off", "disabled", "strict"}
_TRUE_VALUES = {"1", "true", "on", "enabled", "legacy", "compat"}


def graphics_compatibility_enabled(backend: str, vendor: str) -> bool:
    """Return whether conservative graphics execution should be used.

    ``auto`` is intentionally conservative for Intel desktop graphics, where
    old Windows Vulkan/OpenGL drivers commonly expose valid compute support
    but reject device-local host mapping or large recorded SSBO sequences.
    Other vendors keep the normal path unless explicitly opted in.
    """

    backend_name = str(backend or "").strip().lower()
    vendor_name = str(vendor or "").strip().lower()
    if backend_name not in {"vulkan", "opengl"}:
        return False

    raw = os.environ.get(
        "PIXEL_REFINE_GFX_COMPAT_MODE",
        os.environ.get("PIXEL_REFINE_INTEL_GFX_COMPAT", "auto"),
    )
    mode = str(raw or "auto").strip().lower()
    if mode in _FALSE_VALUES:
        return False
    if mode in _TRUE_VALUES:
        return True
    return mode == "auto" and "intel" in vendor_name


def graphics_compatibility_label(backend: str, vendor: str) -> str:
    """Return a stable diagnostic label for the active policy."""

    if not graphics_compatibility_enabled(backend, vendor):
        return "native"
    return "legacy-host-visible-direct"
