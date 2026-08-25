"""
Gradients - Taichi GPU
======================
Sobel and Laplacian edge detection.
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
except ImportError:
    pass

if TAICHI_AVAILABLE:

    @ti.kernel
    def _sobel_kernel(
        src: ti.types.ndarray(),
        dst_dx: ti.types.ndarray(),
        dst_dy: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        for y, x in ti.ndrange(h, w):
            # Sobel X kernel
            # -1 0 1
            # -2 0 2
            # -1 0 1

            # Sobel Y kernel
            # -1 -2 -1
            #  0  0  0
            #  1  2  1

            gx = 0.0
            gy = 0.0

            # 3x3 Loop for Grayscale (Extendable to RGB later if needed, but usually Grayscale)
            # Assuming src is grayscale here for simplicity of gradients

            # Top Row
            val_tl = src[tm.clamp(y - 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]
            val_tm = src[tm.clamp(y - 1, 0, h - 1), x]
            val_tr = src[tm.clamp(y - 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]

            # Middle Row
            val_ml = src[y, tm.clamp(x - 1, 0, w - 1)]
            # val_mm = src[y, x] # Center not used
            val_mr = src[y, tm.clamp(x + 1, 0, w - 1)]

            # Bottom Row
            val_bl = src[tm.clamp(y + 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]
            val_bm = src[tm.clamp(y + 1, 0, h - 1), x]
            val_br = src[tm.clamp(y + 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]

            gx = (val_tr + 2 * val_mr + val_br) - (val_tl + 2 * val_ml + val_bl)
            gy = (val_bl + 2 * val_bm + val_br) - (val_tl + 2 * val_tm + val_tr)

            dst_dx[y, x] = gx
            dst_dy[y, x] = gy

    @ti.kernel
    def _sobel_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst_dx: ti.types.ndarray(),
        dst_dy: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        for y, x in ti.ndrange(h, w):
            # RGB weights for grayscale conversion: 0.299R + 0.587G + 0.114B
            weights = ti.Vector([0.299, 0.587, 0.114])

            gx = ti.Vector([0.0, 0.0, 0.0])
            gy = ti.Vector([0.0, 0.0, 0.0])

            # Top Row
            val_tl = src[tm.clamp(y - 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]
            val_tm = src[tm.clamp(y - 1, 0, h - 1), x]
            val_tr = src[tm.clamp(y - 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]

            # Middle Row
            val_ml = src[y, tm.clamp(x - 1, 0, w - 1)]
            val_mr = src[y, tm.clamp(x + 1, 0, w - 1)]

            # Bottom Row
            val_bl = src[tm.clamp(y + 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]
            val_bm = src[tm.clamp(y + 1, 0, h - 1), x]
            val_br = src[tm.clamp(y + 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]

            gx = (val_tr + 2 * val_mr + val_br) - (val_tl + 2 * val_ml + val_bl)
            gy = (val_bl + 2 * val_bm + val_br) - (val_tl + 2 * val_tm + val_tr)

            # Dot product with weights to get grayscale gradient
            dst_dx[y, x] = gx.dot(weights)
            dst_dy[y, x] = gy.dot(weights)

    @ti.kernel
    def _laplacian_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int
    ):
        for y, x in ti.ndrange(h, w):
            # Laplacian 3x3
            #  0  1  0
            #  1 -4  1
            #  0  1  0

            val_c = src[y, x]
            val_u = src[tm.clamp(y - 1, 0, h - 1), x]
            val_d = src[tm.clamp(y + 1, 0, h - 1), x]
            val_l = src[y, tm.clamp(x - 1, 0, w - 1)]
            val_r = src[y, tm.clamp(x + 1, 0, w - 1)]

            dst[y, x] = val_u + val_d + val_l + val_r - 4.0 * val_c


def sobel(src, dst_dx=None, dst_dy=None, buffer_provider="pool", enable_tiling=True):
    """
    Compute Sobel gradients.
    Returns (dx, dy).
    Caller responsible for releasing if pool used.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        dx, dy = taichi_aot.sobel(src, return_gpu=True)
        # Handle copying if user passed specific dst_dx/dy or needs numpy (fallback logic)
        # To keep it safe, if dst_dx is None we return GPU buffer
        if dst_dx is None and dst_dy is None:
            return dx, dy
        else:
            return dx.to_numpy(), dy.to_numpy()

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # OOM Guard Trigger
    from .. import oom_guard

    if enable_tiling and isinstance(src, np.ndarray) and oom_guard.should_tile(src):

        # Sobel needs 1px neighbour, overlap 16 is plenty safe
        return oom_guard.execute_tiled(
            sobel,
            src,
            overlap=16,
            dst_dx=dst_dx,
            dst_dy=dst_dy,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]
    # Assume single channel for gradients usually
    if len(src.shape) == 3 and src.shape[2] != 1:
        # Warn or error? For now assume user passed grayscale or processes channel 0
        pass

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst_dx is None:
        dx_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    else:
        dx_gpu = dst_dx

    if dst_dy is None:
        dy_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    else:
        dy_gpu = dst_dy

    _sobel_kernel(src_gpu, dx_gpu, dy_gpu, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    dx_np = common.to_numpy_if_needed(
        dx_gpu, src_is_temp and dst_dx is None
    )  # returns numpy if input was numpy
    dy_np = common.to_numpy_if_needed(dy_gpu, src_is_temp and dst_dy is None)

    return dx_np, dy_np


def laplacian(src, dst=None, buffer_provider="pool", enable_tiling=True):
    """
    Compute Laplacian.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        res = taichi_aot.laplacian(src, return_gpu=True)
        if dst is None:
            return res
        return res.to_numpy()

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # OOM Guard Trigger
    if enable_tiling and isinstance(src, np.ndarray) and src.size > 2048 * 2048 * 3:
        from .. import oom_guard

        return oom_guard.execute_tiled(
            laplacian,
            src,
            overlap=16,
            dst=dst,
            buffer_provider=buffer_provider,
            enable_tiling=False,
        )

    h, w = src.shape[:2]

    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is None:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    else:
        dst_gpu = dst

    _laplacian_kernel(src_gpu, dst_gpu, h, w)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
