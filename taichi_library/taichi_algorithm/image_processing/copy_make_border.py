"""
Copy Make Border - Taichi GPU
==============================
OpenCV-compatible border padding operations.
Parity: cv2.copyMakeBorder(src, top, bottom, left, right, borderType, value)
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
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass

# OpenCV-compatible Border Type constants
BORDER_CONSTANT = 0
BORDER_REPLICATE = 1
BORDER_REFLECT = 2
BORDER_WRAP = 3
BORDER_REFLECT_101 = 4
BORDER_TRANSPARENT = 5
BORDER_REFLECT101 = BORDER_REFLECT_101
BORDER_DEFAULT = BORDER_REFLECT_101

if TAICHI_AVAILABLE:

    # --- 2D Kernels ---
    @ti.kernel
    def _pad_constant_kernel_2d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
        value: float,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]
            if sy >= 0 and sy < h and sx >= 0 and sx < w:
                dst[y, x] = src[sy, sx]
            else:
                dst[y, x] = value

    @ti.kernel
    def _pad_reflect101_kernel_2d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = ti.abs(sy)
            diff_y = val_y - (h - 1)
            clamp_y = ti.max(0, diff_y)
            ry = val_y - 2 * clamp_y

            val_x = ti.abs(sx)
            diff_x = val_x - (w - 1)
            clamp_x = ti.max(0, diff_x)
            rx = val_x - 2 * clamp_x

            dst[y, x] = src[tm.clamp(ry, 0, h - 1), tm.clamp(rx, 0, w - 1)]

    @ti.kernel
    def _pad_reflect_kernel_2d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = sy
            val_y = ti.select(val_y < 0, -val_y - 1, val_y)
            val_y = ti.select(val_y >= h, 2 * h - 1 - val_y, val_y)
            ry = tm.clamp(val_y, 0, h - 1)

            val_x = sx
            val_x = ti.select(val_x < 0, -val_x - 1, val_x)
            val_x = ti.select(val_x >= w, 2 * w - 1 - val_x, val_x)
            rx = tm.clamp(val_x, 0, w - 1)

            dst[y, x] = src[ry, rx]

    @ti.kernel
    def _pad_replicate_kernel_2d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = tm.clamp(y - top, 0, src.shape[0] - 1)
            sx = tm.clamp(x - left, 0, src.shape[1] - 1)
            dst[y, x] = src[sy, sx]

    @ti.kernel
    def _pad_wrap_kernel_2d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = (y - top) % src.shape[0]
            sx = (x - left) % src.shape[1]
            dst[y, x] = src[sy, sx]

    # --- 3D Kernels ---
    @ti.kernel
    def _pad_constant_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
        val_r: float, val_g: float, val_b: float,
    ):
        for y, x, c in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]
            if sy >= 0 and sy < h and sx >= 0 and sx < w:
                dst[y, x, c] = src[sy, sx, c]
            else:
                fill_val = 0.0
                if c == 0: fill_val = val_r
                elif c == 1: fill_val = val_g
                elif c == 2: fill_val = val_b
                dst[y, x, c] = fill_val

    @ti.kernel
    def _pad_reflect101_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x, c in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = ti.abs(sy)
            diff_y = val_y - (h - 1)
            clamp_y = ti.max(0, diff_y)
            ry = val_y - 2 * clamp_y

            val_x = ti.abs(sx)
            diff_x = val_x - (w - 1)
            clamp_x = ti.max(0, diff_x)
            rx = val_x - 2 * clamp_x

            dst[y, x, c] = src[tm.clamp(ry, 0, h - 1), tm.clamp(rx, 0, w - 1), c]

    @ti.kernel
    def _pad_reflect_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x, c in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = sy
            val_y = ti.select(val_y < 0, -val_y - 1, val_y)
            val_y = ti.select(val_y >= h, 2 * h - 1 - val_y, val_y)
            ry = tm.clamp(val_y, 0, h - 1)

            val_x = sx
            val_x = ti.select(val_x < 0, -val_x - 1, val_x)
            val_x = ti.select(val_x >= w, 2 * w - 1 - val_x, val_x)
            rx = tm.clamp(val_x, 0, w - 1)

            dst[y, x, c] = src[ry, rx, c]

    @ti.kernel
    def _pad_replicate_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x, c in dst:
            sy = tm.clamp(y - top, 0, src.shape[0] - 1)
            sx = tm.clamp(x - left, 0, src.shape[1] - 1)
            dst[y, x, c] = src[sy, sx, c]

    @ti.kernel
    def _pad_wrap_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x, c in dst:
            sy = (y - top) % src.shape[0]
            sx = (x - left) % src.shape[1]
            dst[y, x, c] = src[sy, sx, c]

    # --- 3D Vector Kernels for AOT (ndim=2 vector array) ---
    @ti.kernel
    def _pad_constant_kernel_3d_vector(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
        val_r: float, val_g: float, val_b: float,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]
            if sy >= 0 and sy < h and sx >= 0 and sx < w:
                dst[y, x] = src[sy, sx]
            else:
                dst[y, x] = ti.Vector([val_r, val_g, val_b])

    @ti.kernel
    def _pad_reflect101_kernel_3d_vector(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = ti.abs(sy)
            diff_y = val_y - (h - 1)
            clamp_y = ti.max(0, diff_y)
            ry = val_y - 2 * clamp_y

            val_x = ti.abs(sx)
            diff_x = val_x - (w - 1)
            clamp_x = ti.max(0, diff_x)
            rx = val_x - 2 * clamp_x

            dst[y, x] = src[tm.clamp(ry, 0, h - 1), tm.clamp(rx, 0, w - 1)]

    @ti.kernel
    def _pad_reflect_kernel_3d_vector(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = y - top
            sx = x - left
            h, w = src.shape[0], src.shape[1]

            val_y = sy
            val_y = ti.select(val_y < 0, -val_y - 1, val_y)
            val_y = ti.select(val_y >= h, 2 * h - 1 - val_y, val_y)
            ry = tm.clamp(val_y, 0, h - 1)

            val_x = sx
            val_x = ti.select(val_x < 0, -val_x - 1, val_x)
            val_x = ti.select(val_x >= w, 2 * w - 1 - val_x, val_x)
            rx = tm.clamp(val_x, 0, w - 1)

            dst[y, x] = src[ry, rx]

    @ti.kernel
    def _pad_replicate_kernel_3d_vector(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = tm.clamp(y - top, 0, src.shape[0] - 1)
            sx = tm.clamp(x - left, 0, src.shape[1] - 1)
            dst[y, x] = src[sy, sx]

    @ti.kernel
    def _pad_wrap_kernel_3d_vector(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        top: ti.i32, left: ti.i32,
    ):
        for y, x in dst:
            sy = (y - top) % src.shape[0]
            sx = (x - left) % src.shape[1]
            dst[y, x] = src[sy, sx]


@ti_thread
def copyMakeBorder(src, top, bottom, left, right, borderType=BORDER_REFLECT_101, dst=None, value=0):
    """
    OpenCV-compatible copyMakeBorder API.
    Pads image borders natively on the GPU supporting multiple datatypes (uint8, uint16, float32)
    and both 2D and 3D (multi-channel) arrays.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Keep original format, ensure contiguous layout
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=None)
    h, w = src_gpu.shape[:2]
    new_h = h + top + bottom
    new_w = w + left + right
    is_3d = len(src_gpu.shape) == 3

    if dst is not None:
        dst_gpu, dst_is_temp = common.ensure_taichi_field(dst, dtype=src_gpu.dtype)
    else:
        dst_shape = (new_h, new_w, src_gpu.shape[2]) if is_3d else (new_h, new_w)
        dst_gpu = common.get_temp_buffer(dst_shape, src_gpu.dtype)
        dst_is_temp = True

    # Map string modes to integer constants if passed as string
    if isinstance(borderType, str):
        mode_map = {
            'CONSTANT': BORDER_CONSTANT,
            'REPLICATE': BORDER_REPLICATE,
            'REFLECT': BORDER_REFLECT,
            'WRAP': BORDER_WRAP,
            'REFLECT_101': BORDER_REFLECT_101,
            'REFLECT101': BORDER_REFLECT_101,
            'DEFAULT': BORDER_REFLECT_101,
        }
        mode = mode_map.get(borderType.upper(), BORDER_REFLECT_101)
    else:
        mode = borderType

    # Dispatch to appropriate kernel
    if not is_3d:
        if mode == BORDER_CONSTANT:
            _pad_constant_kernel_2d(src_gpu, dst_gpu, top, left, float(value))
        elif mode == BORDER_REFLECT_101:
            _pad_reflect101_kernel_2d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_REFLECT:
            _pad_reflect_kernel_2d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_REPLICATE:
            _pad_replicate_kernel_2d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_WRAP:
            _pad_wrap_kernel_2d(src_gpu, dst_gpu, top, left)
        else:
            _pad_constant_kernel_2d(src_gpu, dst_gpu, top, left, float(value))
    else:
        val_r, val_g, val_b = 0.0, 0.0, 0.0
        if isinstance(value, (int, float)):
            val_r = float(value)
        elif isinstance(value, (tuple, list)):
            if len(value) > 0: val_r = float(value[0])
            if len(value) > 1: val_g = float(value[1])
            if len(value) > 2: val_b = float(value[2])

        if mode == BORDER_CONSTANT:
            _pad_constant_kernel_3d(src_gpu, dst_gpu, top, left, val_r, val_g, val_b)
        elif mode == BORDER_REFLECT_101:
            _pad_reflect101_kernel_3d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_REFLECT:
            _pad_reflect_kernel_3d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_REPLICATE:
            _pad_replicate_kernel_3d(src_gpu, dst_gpu, top, left)
        elif mode == BORDER_WRAP:
            _pad_wrap_kernel_3d(src_gpu, dst_gpu, top, left)
        else:
            _pad_constant_kernel_3d(src_gpu, dst_gpu, top, left, val_r, val_g, val_b)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    if dst is not None:
        if dst_is_temp:
            common.to_numpy_if_needed(dst_gpu, True, out=dst)
            common.release_temp_buffer(dst_gpu)
        return dst

    res = common.to_numpy_if_needed(dst_gpu, not hasattr(src, "to_numpy"))
    if dst_is_temp:
        common.release_temp_buffer(dst_gpu)
    return res


# Backward-compatible alias
copy_make_border = copyMakeBorder
