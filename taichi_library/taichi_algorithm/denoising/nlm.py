# Marker: GPU_NATIVE_MARKER_V3
"""
Non-Local Means Denoising - Taichi GPU Implementation
======================================================
State-of-the-art denoising exploiting image self-similarity.

Reference:
  - Buades, A., Coll, B., Morel, J.M. (2005). "A Non-Local Algorithm for
    Image Denoising." CVPR 2005, pp. 60-65.

Algorithm:
  For each pixel p, search a window B(p,R) for patches similar to N(p):
    NL[u](p) = sum_q w(p,q) * u(q)
    w(p,q) = (1/Z(p)) * exp(-||N(p) - N(q)||^2 / h^2)

  Patch distance ||N(p)-N(q)||^2 is computed over (2f+1)x(2f+1) patches.

GPU Strategy:
  - Embarrassingly parallel: one thread per output pixel.
  - Each thread iterates over search window, computes patch distances, weights.
  - Complexity: O(N * R^2 * f^2) but fully parallel across pixels.

AOT Support:
  Fixed-parameter kernel variants are provided for AOT compilation.
  The ti.template() kernels are JIT-only. AOT graphs use the fixed variants
  with hardcoded search_radius/patch_radius values.

  Supported AOT variants:
    - search_r=3,  patch_r=1  (fast, coarse)
    - search_r=5,  patch_r=2  (balanced)
    - search_r=7,  patch_r=3  (quality)
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

    # =========================================================================
    # NLM Kernel — Grayscale (1-channel) — JIT version with ti.template()
    # =========================================================================
    @ti.kernel
    def _nlm_1ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                          h: int, w: int,
                          search_radius: ti.template(), patch_radius: ti.template(),
                          h_param: float):
        """
        Non-Local Means for grayscale images.
        Each thread computes the denoised value for one pixel.
        """
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = (2 * patch_radius + 1) * (2 * patch_radius + 1)

        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            total_value = 0.0

            # Search window
            for dy in range(-search_radius, search_radius + 1):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-search_radius, search_radius + 1):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue

                    # Compute patch distance between N(y,x) and N(qy,qx)
                    dist = 0.0
                    for py in range(-patch_radius, patch_radius + 1):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-patch_radius, patch_radius + 1):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            diff = src[sy, sx] - src[ty, tx]
                            dist += diff * diff

                    dist /= float(patch_size)

                    # Weight
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    total_value += wt * src[qy, qx]

            if total_weight > 1e-12:
                dst[y, x] = total_value / total_weight
            else:
                dst[y, x] = src[y, x]

    # =========================================================================
    # NLM Kernel — 3-channel (RGB) — JIT version with ti.template()
    # =========================================================================
    @ti.kernel
    def _nlm_3ch_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                          h: int, w: int,
                          search_radius: ti.template(), patch_radius: ti.template(),
                          h_param: float):
        """
        Non-Local Means for 3-channel images.
        Patch distance uses all 3 channels.
        """
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = (2 * patch_radius + 1) * (2 * patch_radius + 1) * 3

        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            acc0, acc1, acc2 = 0.0, 0.0, 0.0

            for dy in range(-search_radius, search_radius + 1):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-search_radius, search_radius + 1):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue

                    dist = 0.0
                    for py in range(-patch_radius, patch_radius + 1):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-patch_radius, patch_radius + 1):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            for c in ti.static(range(3)):
                                diff = src[sy, sx, c] - src[ty, tx, c]
                                dist += diff * diff

                    dist /= float(patch_size)
                    wt = ti.exp(-dist * inv_h2)

                    total_weight += wt
                    acc0 += wt * src[qy, qx, 0]
                    acc1 += wt * src[qy, qx, 1]
                    acc2 += wt * src[qy, qx, 2]

            if total_weight > 1e-12:
                inv_w = 1.0 / total_weight
                dst[y, x, 0] = acc0 * inv_w
                dst[y, x, 1] = acc1 * inv_w
                dst[y, x, 2] = acc2 * inv_w
            else:
                dst[y, x, 0] = src[y, x, 0]
                dst[y, x, 1] = src[y, x, 1]
                dst[y, x, 2] = src[y, x, 2]

    # =========================================================================
    # AOT-compatible Fixed-Parameter Kernels
    # These have hardcoded search_radius / patch_radius for AOT graph dispatch.
    # =========================================================================

    # --- 1ch AOT variants ---

    @ti.kernel
    def _nlm_1ch_s3_p1(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 1ch: search_r=3, patch_r=1 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 9.0  # (2*1+1)^2
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            total_value = 0.0
            for dy in range(-3, 4):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-3, 4):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-1, 2):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-1, 2):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            diff = src[sy, sx] - src[ty, tx]
                            dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    total_value += wt * src[qy, qx]
            if total_weight > 1e-12:
                dst[y, x] = total_value / total_weight
            else:
                dst[y, x] = src[y, x]

    @ti.kernel
    def _nlm_1ch_s5_p2(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 1ch: search_r=5, patch_r=2 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 25.0  # (2*2+1)^2
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            total_value = 0.0
            for dy in range(-5, 6):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-5, 6):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-2, 3):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-2, 3):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            diff = src[sy, sx] - src[ty, tx]
                            dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    total_value += wt * src[qy, qx]
            if total_weight > 1e-12:
                dst[y, x] = total_value / total_weight
            else:
                dst[y, x] = src[y, x]

    @ti.kernel
    def _nlm_1ch_s7_p3(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 1ch: search_r=7, patch_r=3 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 49.0  # (2*3+1)^2
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            total_value = 0.0
            for dy in range(-7, 8):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-7, 8):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-3, 4):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-3, 4):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            diff = src[sy, sx] - src[ty, tx]
                            dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    total_value += wt * src[qy, qx]
            if total_weight > 1e-12:
                dst[y, x] = total_value / total_weight
            else:
                dst[y, x] = src[y, x]

    # --- 3ch AOT variants ---

    @ti.kernel
    def _nlm_3ch_s3_p1(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 3ch: search_r=3, patch_r=1 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 27.0  # (2*1+1)^2 * 3
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            acc0, acc1, acc2 = 0.0, 0.0, 0.0
            for dy in range(-3, 4):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-3, 4):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-1, 2):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-1, 2):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            for c in ti.static(range(3)):
                                diff = src[sy, sx, c] - src[ty, tx, c]
                                dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    acc0 += wt * src[qy, qx, 0]
                    acc1 += wt * src[qy, qx, 1]
                    acc2 += wt * src[qy, qx, 2]
            if total_weight > 1e-12:
                inv_w = 1.0 / total_weight
                dst[y, x, 0] = acc0 * inv_w
                dst[y, x, 1] = acc1 * inv_w
                dst[y, x, 2] = acc2 * inv_w
            else:
                dst[y, x, 0] = src[y, x, 0]
                dst[y, x, 1] = src[y, x, 1]
                dst[y, x, 2] = src[y, x, 2]

    @ti.kernel
    def _nlm_3ch_s5_p2(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 3ch: search_r=5, patch_r=2 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 75.0  # (2*2+1)^2 * 3
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            acc0, acc1, acc2 = 0.0, 0.0, 0.0
            for dy in range(-5, 6):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-5, 6):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-2, 3):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-2, 3):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            for c in ti.static(range(3)):
                                diff = src[sy, sx, c] - src[ty, tx, c]
                                dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    acc0 += wt * src[qy, qx, 0]
                    acc1 += wt * src[qy, qx, 1]
                    acc2 += wt * src[qy, qx, 2]
            if total_weight > 1e-12:
                inv_w = 1.0 / total_weight
                dst[y, x, 0] = acc0 * inv_w
                dst[y, x, 1] = acc1 * inv_w
                dst[y, x, 2] = acc2 * inv_w
            else:
                dst[y, x, 0] = src[y, x, 0]
                dst[y, x, 1] = src[y, x, 1]
                dst[y, x, 2] = src[y, x, 2]

    @ti.kernel
    def _nlm_3ch_s7_p3(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                         h: int, w: int, h_param: float):
        """NLM 3ch: search_r=7, patch_r=3 (AOT-fixed)"""
        inv_h2 = 1.0 / (h_param * h_param)
        patch_size = 147.0  # (2*3+1)^2 * 3
        for y, x in ti.ndrange(h, w):
            total_weight = 0.0
            acc0, acc1, acc2 = 0.0, 0.0, 0.0
            for dy in range(-7, 8):
                qy = y + dy
                if qy < 0 or qy >= h:
                    continue
                for dx in range(-7, 8):
                    qx = x + dx
                    if qx < 0 or qx >= w:
                        continue
                    dist = 0.0
                    for py in range(-3, 4):
                        sy = tm.clamp(y + py, 0, h - 1)
                        ty = tm.clamp(qy + py, 0, h - 1)
                        for px in range(-3, 4):
                            sx = tm.clamp(x + px, 0, w - 1)
                            tx = tm.clamp(qx + px, 0, w - 1)
                            for c in ti.static(range(3)):
                                diff = src[sy, sx, c] - src[ty, tx, c]
                                dist += diff * diff
                    dist /= patch_size
                    wt = ti.exp(-dist * inv_h2)
                    total_weight += wt
                    acc0 += wt * src[qy, qx, 0]
                    acc1 += wt * src[qy, qx, 1]
                    acc2 += wt * src[qy, qx, 2]
            if total_weight > 1e-12:
                inv_w = 1.0 / total_weight
                dst[y, x, 0] = acc0 * inv_w
                dst[y, x, 1] = acc1 * inv_w
                dst[y, x, 2] = acc2 * inv_w
            else:
                dst[y, x, 0] = src[y, x, 0]
                dst[y, x, 1] = src[y, x, 1]
                dst[y, x, 2] = src[y, x, 2]


# =========================================================================
# AOT dispatch mapping: (search_r, patch_r) -> kernel function
# =========================================================================
_NLM_1CH_AOT = {
    (3, 1): _nlm_1ch_s3_p1 if TAICHI_AVAILABLE else None,
    (5, 2): _nlm_1ch_s5_p2 if TAICHI_AVAILABLE else None,
    (7, 3): _nlm_1ch_s7_p3 if TAICHI_AVAILABLE else None,
}

_NLM_3CH_AOT = {
    (3, 1): _nlm_3ch_s3_p1 if TAICHI_AVAILABLE else None,
    (5, 2): _nlm_3ch_s5_p2 if TAICHI_AVAILABLE else None,
    (7, 3): _nlm_3ch_s7_p3 if TAICHI_AVAILABLE else None,
}

# JIT dispatch table (ti.template() variants)
_NLM_1CH_VARIANTS = {}
_NLM_3CH_VARIANTS = {}


def _get_nlm_1ch_kernel(search_r, patch_r):
    """Get or create NLM kernel for specific parameters (Taichi JIT specializes)."""
    key = (search_r, patch_r)
    if key not in _NLM_1CH_VARIANTS:
        _NLM_1CH_VARIANTS[key] = _nlm_1ch_kernel
    return _NLM_1CH_VARIANTS[key]


def _get_nlm_3ch_kernel(search_r, patch_r):
    key = (search_r, patch_r)
    if key not in _NLM_3CH_VARIANTS:
        _NLM_3CH_VARIANTS[key] = _nlm_3ch_kernel
    return _NLM_3CH_VARIANTS[key]


@ti_thread
def non_local_means(src, h_param=10.0, search_window=7, patch_size=5,
                     dst=None, buffer_provider="pool"):
    """
    Non-Local Means Denoising (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.fastNlMeansDenoising()

    Args:
        src: Input image (H, W) or (H, W, 3), uint8 or float32.
        h_param: Filtering strength. Higher = more smoothing.
                 Controls the exponential weight decay. Typical: 5-15.
                 Rule of thumb: h ≈ k * noise_sigma, k in [0.4, 0.8].
        search_window: Half-size of search window R. Search area = (2R+1)^2.
                       Typical: 7 (i.e., 15x15 search area).
        patch_size: Half-size of comparison patch f. Patch = (2f+1)^2.
                    Typical: 3 (i.e., 7x7 patch) or 2 (5x5).
        dst: Optional output buffer.
        buffer_provider: Buffer pool provider.

    Returns:
        Denoised image in same format as input.
    """
    is_numpy = isinstance(src, np.ndarray)

    # --- Auto-cast: normalize integer types to float32 [0,1] ---
    orig_dtype = src.dtype if is_numpy else np.float32
    if is_numpy and src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
    elif is_numpy and src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0

    is_3ch = len(src.shape) == 3 and src.shape[2] == 3

    search_r = search_window
    patch_r = patch_size

    # --- AOT path: use pre-compiled fixed-parameter kernels ---
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_library import taichi_aot
        return taichi_aot.non_local_means(
            src, h_param=h_param, search_window=search_r,
            patch_size=patch_r, return_gpu=not is_numpy
        )

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]

    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
    elif is_3ch:
        dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    # Choose kernel: JIT ti.template() variant
    if is_3ch:
        kernel = _get_nlm_3ch_kernel(search_r, patch_r)
    else:
        kernel = _get_nlm_1ch_kernel(search_r, patch_r)

    kernel(src_gpu, dst_gpu, h, w, search_r, patch_r, h_param)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    result = common.to_numpy_if_needed(dst_gpu, is_numpy)

    # --- Auto-cast back to original dtype ---
    if isinstance(result, np.ndarray):
        if orig_dtype == np.uint8:
            return np.clip(result * 255.0, 0, 255).astype(np.uint8)
        elif orig_dtype == np.uint16:
            return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result
