"""
Copy Make Border - Taichi GPU
==============================
OpenCV-compatible border padding operations.
Parity: cv2.copyMakeBorder(src, top, bottom, left, right, borderType, value)

Usage (JIT):
    from taichi_library.taichi_algorithm import copy_make_border
    result = copy_make_border(src, top=10, bottom=10, left=10, right=10)
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from . import common
    from .taichi_worker import ti_thread
except ImportError:
    pass

# Border mode constants
BORDER_CONSTANT = 0
BORDER_REFLECT_101 = 1
BORDER_REFLECT = 2
BORDER_REPLICATE = 3
BORDER_WRAP = 4


if TAICHI_AVAILABLE:

    @ti.kernel
    def _pad_constant_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        new_h: ti.i32, new_w: ti.i32,
        top: ti.i32, left: ti.i32,
        value: ti.f32,
    ):
        """Pad with constant value."""
        for y, x in ti.ndrange(new_h, new_w):
            sy = y - top
            sx = x - left
            if sy >= 0 and sy < h and sx >= 0 and sx < w:
                dst[y, x] = src[sy, sx]
            else:
                dst[y, x] = value

    @ti.kernel
    def _pad_reflect101_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        new_h: ti.i32, new_w: ti.i32,
        top: ti.i32, left: ti.i32,
        value: ti.f32,
    ):
        """Pad with BORDER_REFLECT_101: gfedcb|abcdefgh|gfedcba"""
        for y, x in ti.ndrange(new_h, new_w):
            sy = y - top
            sx = x - left
            # Reflect_101 logic
            if sy < 0:
                sy = -sy
            if sy >= h:
                sy = 2 * (h - 1) - sy
            if sx < 0:
                sx = -sx
            if sx >= w:
                sx = 2 * (w - 1) - sx
            sy = tm.clamp(sy, 0, h - 1)
            sx = tm.clamp(sx, 0, w - 1)
            dst[y, x] = src[sy, sx]

    @ti.kernel
    def _pad_replicate_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        h: ti.i32, w: ti.i32,
        new_h: ti.i32, new_w: ti.i32,
        top: ti.i32, left: ti.i32,
        value: ti.f32,
    ):
        """Pad by replicating edge pixels: aaaaaa|abcdefgh|hhhhhhh"""
        for y, x in ti.ndrange(new_h, new_w):
            sy = tm.clamp(y - top, 0, h - 1)
            sx = tm.clamp(x - left, 0, w - 1)
            dst[y, x] = src[sy, sx]


@ti_thread
def copy_make_border(src, top=0, bottom=0, left=0, right=0,
                     border_mode='CONSTANT', value=0):
    """
    Pad image borders.
    Parity: cv2.copyMakeBorder(src, top, bottom, left, right, borderType, value)

    Args:
        src: Input image (H,W) float32.
        top, bottom, left, right: Number of pixels to add on each side.
        border_mode: 'CONSTANT', 'REFLECT_101', 'REFLECT', 'REPLICATE'.
        value: Fill value for CONSTANT mode.

    Returns:
        Padded image (H+top+bottom, W+left+right).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]
    new_h = h + top + bottom
    new_w = w + left + right

    dst_gpu = common.get_temp_buffer((new_h, new_w), ti.f32)

    # Map string to integer constant
    if isinstance(border_mode, str):
        mode_map = {
            'CONSTANT': BORDER_CONSTANT,
            'REFLECT_101': BORDER_REFLECT_101,
            'REFLECT': BORDER_REFLECT_101,  # REFLECT and REFLECT_101 use same logic
            'REPLICATE': BORDER_REPLICATE,
        }
        mode = mode_map.get(border_mode.upper(), BORDER_CONSTANT)
    else:
        mode = border_mode

    if mode == BORDER_CONSTANT:
        _pad_constant_kernel(src_gpu, dst_gpu, h, w, new_h, new_w, top, left, float(value))
    elif mode == BORDER_REFLECT_101:
        _pad_reflect101_kernel(src_gpu, dst_gpu, h, w, new_h, new_w, top, left, float(value))
    elif mode == BORDER_REPLICATE:
        _pad_replicate_kernel(src_gpu, dst_gpu, h, w, new_h, new_w, top, left, float(value))
    else:
        _pad_constant_kernel(src_gpu, dst_gpu, h, w, new_h, new_w, top, left, float(value))

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
