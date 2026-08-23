"""Warp Affine - Taichi GPU
============================
GPU-accelerated affine transformation (cv2.warpAffine equivalent).
Uses inverse mapping with bilinear interpolation.
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

if TAICHI_AVAILABLE:
    from ..interpolation.remap import bilinear_at, bilinear_at_3ch

    @ti.kernel
    def _warp_affine_kernel_2d(
        src: ti.types.ndarray(),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        """Affine warp for grayscale (2D). M_inv is 2x3 inverse affine matrix."""
        for r, c in ti.ndrange(h_dst, w_dst):
            src_x = M_inv[0, 0] * float(c) + M_inv[0, 1] * float(r) + M_inv[0, 2]
            src_y = M_inv[1, 0] * float(c) + M_inv[1, 1] * float(r) + M_inv[1, 2]
            dst[r, c] = bilinear_at(src, src_x, src_y, h_src, w_src)

    @ti.kernel
    def _warp_affine_kernel_3d(
        src: ti.types.ndarray(),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
        n_ch: int,
    ):
        """Affine warp for multi-channel (3D)."""
        for r, c, ch in ti.ndrange(h_dst, w_dst, n_ch):
            src_x = M_inv[0, 0] * float(c) + M_inv[0, 1] * float(r) + M_inv[0, 2]
            src_y = M_inv[1, 0] * float(c) + M_inv[1, 1] * float(r) + M_inv[1, 2]
            dst[r, c, ch] = bilinear_at_3ch(src, src_x, src_y, h_src, w_src, ch)


@ti_thread
def warpAffine(src, M, dsize, dst=None, buffer_provider="pool"):
    """GPU-accelerated affine warp (mirrors cv2.warpAffine).

    Args:
        src: Input image (H, W) or (H, W, C).
        M: 2x3 affine transformation matrix (float32).
        dsize: (width, height) of output.
        dst: Optional output buffer.

    Returns:
        Warped image.
    """
    from ..common import get_temp_buffer, release_temp_buffer, ensure_taichi_field

    M_np = np.asarray(M, dtype=np.float32)
    w_dst, h_dst = dsize

    # Compute inverse affine: embed in 3x3, invert, extract 2x3
    M_3x3 = np.eye(3, dtype=np.float32)
    M_3x3[:2, :] = M_np
    try:
        M_inv_3x3 = np.linalg.inv(M_3x3)
    except np.linalg.LinAlgError:
        M_inv_3x3 = np.eye(3, dtype=np.float32)
    M_inv_np = M_inv_3x3[:2, :].astype(np.float32)

    is_taichi_input = hasattr(src, "to_numpy")

    src_gpu, src_temp = ensure_taichi_field(src, dtype=ti.f32, buffer_provider=buffer_provider)
    minv_gpu, minv_temp = ensure_taichi_field(M_inv_np, dtype=ti.f32, buffer_provider=buffer_provider)

    h_src, w_src = src_gpu.shape[:2]
    is_3d = len(src_gpu.shape) == 3
    c_count = src_gpu.shape[2] if is_3d else 1

    if dst is None:
        out_shape = (h_dst, w_dst, c_count) if is_3d else (h_dst, w_dst)
        dst_gpu = get_temp_buffer(out_shape, ti.f32, buffer_provider)
    else:
        dst_gpu, _ = ensure_taichi_field(dst, dtype=ti.f32, buffer_provider=buffer_provider)

    if is_3d:
        _warp_affine_kernel_3d(src_gpu, minv_gpu, dst_gpu, h_src, w_src, h_dst, w_dst, c_count)
    else:
        _warp_affine_kernel_2d(src_gpu, minv_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)

    if src_temp:
        release_temp_buffer(src_gpu)
    if minv_temp:
        release_temp_buffer(minv_gpu)

    if not is_taichi_input:
        result = dst_gpu.to_numpy()
        release_temp_buffer(dst_gpu)
        if dst is not None:
            dst[:] = result
            return dst
        return result

    return dst_gpu


__all__ = ["warpAffine"]
