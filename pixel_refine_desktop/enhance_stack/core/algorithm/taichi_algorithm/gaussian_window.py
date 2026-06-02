"""Gaussian Window - Taichi GPU"""

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


if TAICHI_AVAILABLE:

    @ti.kernel
    def _create_gaussian_kernel(
        window: ti.types.ndarray(), h: int, w: int, sigma: float
    ):
        center_y = h / 2.0
        center_x = w / 2.0
        for y, x in ti.ndrange(h, w):
            dy = float(y) - center_y
            dx = float(x) - center_x
            dist_sq = dy * dy + dx * dx
            window[y, x] = tm.exp(-dist_sq / (2.0 * sigma * sigma))


def create_gaussian_window(height: int, width: int, sigma: float = None):
    """Supports both NumPy and Taichi ndarrays."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    if sigma is None:
        sigma = max(height, width) / 6.0

    dst_gpu = ti.ndarray(dtype=ti.f32, shape=(height, width))
    _create_gaussian_kernel(dst_gpu, height, width, sigma)

    # By default, for simplicity, we return NumPy unless we add a _gpu version later
    return dst_gpu.to_numpy()
