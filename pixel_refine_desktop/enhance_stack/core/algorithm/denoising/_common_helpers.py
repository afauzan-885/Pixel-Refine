"""Shared helpers for denoising adapters (Average, SpatialFusion, etc.).

Centralises:
- ``_active_backend`` — resolve the backend selected by Performance Settings.
- ``_restore_output_dtype`` — convert a float32 accumulator to the original
  pixel data type with safe integer scaling.
- ``_frame_info`` — short string describing a frame's shape and dtype.
"""

import numpy as np


def frame_info(frame):
    """Return a compact ``shape=..., dtype=...`` description for *frame*."""
    if frame is None:
        return "None"
    return f"shape={getattr(frame, 'shape', None)}, dtype={getattr(frame, 'dtype', None)}"


def active_backend():
    """Resolve the backend selected by Performance Settings at call time."""
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            get_backend_arch,
        )

        configured = str(get_backend_arch() or "").strip().lower()
        if configured in {"cpu", "cuda", "vulkan", "opengl", "gles"}:
            return configured
    except Exception:
        pass
    try:
        from taichi_vision import taichi_aot

        return str(getattr(taichi_aot.engine, "arch", "cpu")).strip().lower()
    except Exception:
        return "cpu"


def restore_output_dtype(image, dtype=np.uint16):
    """Convert a float32 accumulator to the original integer pixel type."""
    if image is None:
        return None
    image_f32 = np.ascontiguousarray(image, dtype=np.float32)
    if dtype is None or not np.issubdtype(dtype, np.integer):
        dtype = np.uint16
    info = np.iinfo(dtype)
    max_val = float(np.nanmax(image_f32)) if image_f32.size > 0 else 1.0
    if max_val <= 1.5:
        image_f32 = image_f32 * float(info.max)
    image_clipped = np.clip(image_f32 + 0.5, float(info.min), float(info.max))
    return image_clipped.astype(dtype, copy=False)
