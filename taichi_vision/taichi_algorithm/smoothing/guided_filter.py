# Marker: GPU_NATIVE_MARKER_V3
"""
Guided Image Filter - Taichi GPU Implementation
================================================
Edge-preserving smoothing via local linear regression (O(N) complexity).

Reference:
  - He, K., Sun, J., Tang, X. (2010). "Guided Image Filtering."
    ECCV 2010; IEEE TPAMI 2012.

Algorithm:
  For guidance image I and input p, the output q is a local linear model:
      q_i = a_k * I_i + b_k   for all i in window w_k

  Coefficients via linear ridge regression:
      a_k = cov(I, p)_k / (var(I)_k + epsilon)
      b_k = mean(p)_k - a_k * mean(I)_k

  Final output averages overlapping windows:
      q_i = mean_a_i * I_i + mean_b_i

  All statistics computed via box filters -> O(N) regardless of radius.
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
    from .box_filter import box_filter
except ImportError:
    pass

if TAICHI_AVAILABLE:

    # =========================================================================
    # Element-wise Kernels for Guided Filter Pipeline
    # =========================================================================

    @ti.kernel
    def _gf_mul_kernel(a: ti.types.ndarray(), b: ti.types.ndarray(),
                        dst: ti.types.ndarray(), h: int, w: int):
        """Element-wise multiply: dst = a * b"""
        for y, x in ti.ndrange(h, w):
            dst[y, x] = a[y, x] * b[y, x]

    @ti.kernel
    def _gf_compute_var_cov_kernel(mean_I: ti.types.ndarray(), mean_p: ti.types.ndarray(),
                                     mean_II: ti.types.ndarray(), mean_Ip: ti.types.ndarray(),
                                     var_I: ti.types.ndarray(), cov_Ip: ti.types.ndarray(),
                                     h: int, w: int):
        """Compute variance and covariance from moments."""
        for y, x in ti.ndrange(h, w):
            mI = mean_I[y, x]
            mp = mean_p[y, x]
            var_I[y, x] = mean_II[y, x] - mI * mI
            cov_Ip[y, x] = mean_Ip[y, x] - mI * mp

    @ti.kernel
    def _gf_compute_var_kernel(mean_I: ti.types.ndarray(),
                               mean_II: ti.types.ndarray(),
                               var_I: ti.types.ndarray(), h: int, w: int):
        """Portable variance pass with reduced descriptor pressure."""
        for y, x in ti.ndrange(h, w):
            mI = mean_I[y, x]
            var_I[y, x] = mean_II[y, x] - mI * mI

    @ti.kernel
    def _gf_compute_cov_kernel(mean_I: ti.types.ndarray(),
                               mean_p: ti.types.ndarray(),
                               mean_Ip: ti.types.ndarray(),
                               cov_Ip: ti.types.ndarray(), h: int, w: int):
        """Portable covariance pass with reduced descriptor pressure."""
        for y, x in ti.ndrange(h, w):
            cov_Ip[y, x] = (
                mean_Ip[y, x] - mean_I[y, x] * mean_p[y, x]
            )

    @ti.kernel
    def _gf_compute_ab_kernel(var_I: ti.types.ndarray(), cov_Ip: ti.types.ndarray(),
                                mean_I: ti.types.ndarray(), mean_p: ti.types.ndarray(),
                                a: ti.types.ndarray(), b: ti.types.ndarray(),
                                epsilon: float, h: int, w: int):
        """Compute linear coefficients a and b."""
        for y, x in ti.ndrange(h, w):
            a_val = cov_Ip[y, x] / (var_I[y, x] + epsilon)
            a[y, x] = a_val
            b[y, x] = mean_p[y, x] - a_val * mean_I[y, x]

    @ti.kernel
    def _gf_compute_a_kernel(var_I: ti.types.ndarray(),
                             cov_Ip: ti.types.ndarray(),
                             a: ti.types.ndarray(), epsilon: float,
                             h: int, w: int):
        """Portable linear-slope pass with reduced descriptor pressure."""
        for y, x in ti.ndrange(h, w):
            a[y, x] = cov_Ip[y, x] / (var_I[y, x] + epsilon)

    @ti.kernel
    def _gf_compute_b_kernel(mean_I: ti.types.ndarray(),
                             mean_p: ti.types.ndarray(),
                             a: ti.types.ndarray(), b: ti.types.ndarray(),
                             h: int, w: int):
        """Portable linear-intercept pass with reduced descriptor pressure."""
        for y, x in ti.ndrange(h, w):
            b[y, x] = mean_p[y, x] - a[y, x] * mean_I[y, x]

    @ti.kernel
    def _gf_output_kernel(mean_a: ti.types.ndarray(), mean_b: ti.types.ndarray(),
                            I: ti.types.ndarray(), dst: ti.types.ndarray(),
                            h: int, w: int):
        """Final output: q = mean_a * I + mean_b"""
        for y, x in ti.ndrange(h, w):
            dst[y, x] = mean_a[y, x] * I[y, x] + mean_b[y, x]

    # =========================================================================
    # 3-Channel (RGB) Guided Filter Kernels
    # =========================================================================

    @ti.kernel
    def _gf_mul_3ch_kernel(src: ti.types.ndarray(), guide: ti.types.ndarray(),
                             dst_Ip0: ti.types.ndarray(), dst_Ip1: ti.types.ndarray(),
                             dst_Ip2: ti.types.ndarray(), h: int, w: int):
        """Compute I*R, I*G, I*B for 3-channel guided filter."""
        for y, x in ti.ndrange(h, w):
            I_val = guide[y, x]
            dst_Ip0[y, x] = I_val * src[y, x, 0]
            dst_Ip1[y, x] = I_val * src[y, x, 1]
            dst_Ip2[y, x] = I_val * src[y, x, 2]

    @ti.kernel
    def _gf_compute_ab_3ch_kernel(var_I: ti.types.ndarray(),
                                    mean_I: ti.types.ndarray(),
                                    mean_p0: ti.types.ndarray(),
                                    mean_p1: ti.types.ndarray(),
                                    mean_p2: ti.types.ndarray(),
                                    mean_Ip0: ti.types.ndarray(),
                                    mean_Ip1: ti.types.ndarray(),
                                    mean_Ip2: ti.types.ndarray(),
                                    a0: ti.types.ndarray(), a1: ti.types.ndarray(), a2: ti.types.ndarray(),
                                    b0: ti.types.ndarray(), b1: ti.types.ndarray(), b2: ti.types.ndarray(),
                                    epsilon: float, h: int, w: int):
        """Compute per-channel a, b coefficients for 3ch."""
        for y, x in ti.ndrange(h, w):
            vI = var_I[y, x]
            mI = mean_I[y, x]
            denom = 1.0 / (vI + epsilon)

            cov0 = mean_Ip0[y, x] - mI * mean_p0[y, x]
            cov1 = mean_Ip1[y, x] - mI * mean_p1[y, x]
            cov2 = mean_Ip2[y, x] - mI * mean_p2[y, x]

            a0[y, x] = cov0 * denom
            a1[y, x] = cov1 * denom
            a2[y, x] = cov2 * denom

            b0[y, x] = mean_p0[y, x] - a0[y, x] * mI
            b1[y, x] = mean_p1[y, x] - a1[y, x] * mI
            b2[y, x] = mean_p2[y, x] - a2[y, x] * mI

    @ti.kernel
    def _gf_output_3ch_kernel(mean_a0: ti.types.ndarray(), mean_a1: ti.types.ndarray(),
                                mean_a2: ti.types.ndarray(),
                                mean_b0: ti.types.ndarray(), mean_b1: ti.types.ndarray(),
                                mean_b2: ti.types.ndarray(),
                                I: ti.types.ndarray(), dst: ti.types.ndarray(),
                                h: int, w: int):
        """Final output for 3ch: q_c = mean_a_c * I + mean_b_c"""
        for y, x in ti.ndrange(h, w):
            I_val = I[y, x]
            dst[y, x, 0] = mean_a0[y, x] * I_val + mean_b0[y, x]
            dst[y, x, 1] = mean_a1[y, x] * I_val + mean_b1[y, x]
            dst[y, x, 2] = mean_a2[y, x] * I_val + mean_b2[y, x]


def _box_filter_1ch(src_gpu, radius, buffer_provider):
    """Helper: apply separable box filter on a single-channel GPU buffer."""
    h, w = src_gpu.shape[:2]
    ksize = radius * 2 + 1

    # Use the existing box_filter on 2D data
    # box_filter expects (H,W) or (H,W,3) — pass 2D directly
    tmp = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    result = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    # Horizontal pass
    from .box_filter import _box_blur_h_generic_1ch_kernel, _box_blur_v_generic_1ch_kernel
    _box_blur_h_generic_1ch_kernel(src_gpu, tmp, h, w, radius)
    _box_blur_v_generic_1ch_kernel(tmp, result, h, w, radius)

    common.release_temp_buffer(tmp)
    return result


@ti_thread
def guided_filter(guide, src, radius=8, epsilon=1e-4, dst=None, buffer_provider="pool"):
    """
    Guided Image Filter (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.ximgproc.guidedFilter()

    Edge-preserving smoothing where the output follows the edges of the
    guidance image rather than the input image.

    Args:
        guide: Guidance image (H, W) grayscale, float32 [0,1] or [0,255].
               If src is 3ch, guide can be 1ch (grayscale guidance).
        src:   Input image (H, W) or (H, W, 3), float32.
        radius: Filter radius (half-window size). Larger = broader smoothing.
                Typical: 2-8 for smoothing, 15-20 for HDR/matting.
        epsilon: Regularization parameter. Larger = more smoothing in flat areas.
                 Typical: 1e-4 for [0,1] images, 0.01*255^2 for [0,255].
        dst: Optional output buffer.
        buffer_provider: Buffer pool provider.

    Returns:
        Filtered image in same format as input.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    is_3ch = len(src.shape) == 3 and src.shape[2] == 3

    # Upload inputs
    guide_gpu, guide_is_temp = common.ensure_taichi_field(guide, dtype=ti.f32,
                                                            buffer_provider=buffer_provider)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                        buffer_provider=buffer_provider)
    h, w = guide_gpu.shape[:2]

    # Normalize guide to [0, 1] if it seems to be in [0, 255]
    # (We work in whatever range the user provides; epsilon should match)

    # --- Allocate intermediates ---
    II_buf = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    mean_I = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    # Step 1: mean_I = box(guide)
    mean_I_result = _box_filter_1ch(guide_gpu, radius, buffer_provider)
    # Copy result (box_filter returns a new buffer)
    common._extract_channel_lowlevel(mean_I_result, mean_I, 0) if len(mean_I_result.shape) > 2 else None
    if len(mean_I_result.shape) == 2:
        # Direct copy via kernel or reuse
        mean_I = mean_I_result
        common.release_temp_buffer(II_buf)
        II_buf = None

    # Step 2: mean_II = box(guide * guide)
    II_prod = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    _gf_mul_kernel(guide_gpu, guide_gpu, II_prod, h, w)
    mean_II = _box_filter_1ch(II_prod, radius, buffer_provider)
    common.release_temp_buffer(II_prod)

    if is_3ch:
        # ---- 3-Channel Path ----
        # Extract channels
        ch0 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        ch1 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        ch2 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        common._extract_channel_lowlevel(src_gpu, ch0, 0)
        common._extract_channel_lowlevel(src_gpu, ch1, 1)
        common._extract_channel_lowlevel(src_gpu, ch2, 2)

        # mean_p per channel
        mean_p0 = _box_filter_1ch(ch0, radius, buffer_provider)
        mean_p1 = _box_filter_1ch(ch1, radius, buffer_provider)
        mean_p2 = _box_filter_1ch(ch2, radius, buffer_provider)

        # I * p per channel
        Ip0 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        Ip1 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        Ip2 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        _gf_mul_3ch_kernel(src_gpu, guide_gpu, Ip0, Ip1, Ip2, h, w)

        mean_Ip0 = _box_filter_1ch(Ip0, radius, buffer_provider)
        mean_Ip1 = _box_filter_1ch(Ip1, radius, buffer_provider)
        mean_Ip2 = _box_filter_1ch(Ip2, radius, buffer_provider)
        common.release_temp_buffer(Ip0)
        common.release_temp_buffer(Ip1)
        common.release_temp_buffer(Ip2)

        # Compute var_I
        var_I = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        cov_dummy = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

        # var_I = mean_II - mean_I * mean_I (reuse cov_Ip slot as dummy)
        _gf_compute_var_cov_kernel(mean_I, mean_p0, mean_II, mean_Ip0,
                                     var_I, cov_dummy, h, w)
        common.release_temp_buffer(cov_dummy)

        # Compute a, b per channel
        a0 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        a1 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        a2 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        b0 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        b1 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        b2 = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

        _gf_compute_ab_3ch_kernel(var_I, mean_I,
                                    mean_p0, mean_p1, mean_p2,
                                    mean_Ip0, mean_Ip1, mean_Ip2,
                                    a0, a1, a2, b0, b1, b2,
                                    epsilon, h, w)

        # Clean up intermediates
        for buf in [ch0, ch1, ch2, mean_p0, mean_p1, mean_p2,
                     mean_Ip0, mean_Ip1, mean_Ip2, var_I, mean_II]:
            common.release_temp_buffer(buf)

        # Mean of coefficients via box filter
        mean_a0 = _box_filter_1ch(a0, radius, buffer_provider)
        mean_a1 = _box_filter_1ch(a1, radius, buffer_provider)
        mean_a2 = _box_filter_1ch(a2, radius, buffer_provider)
        mean_b0 = _box_filter_1ch(b0, radius, buffer_provider)
        mean_b1 = _box_filter_1ch(b1, radius, buffer_provider)
        mean_b2 = _box_filter_1ch(b2, radius, buffer_provider)

        for buf in [a0, a1, a2, b0, b1, b2]:
            common.release_temp_buffer(buf)

        # Final output
        if dst is not None:
            dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                     buffer_provider=buffer_provider)
        else:
            dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)

        _gf_output_3ch_kernel(mean_a0, mean_a1, mean_a2,
                                mean_b0, mean_b1, mean_b2,
                                guide_gpu, dst_gpu, h, w)

        for buf in [mean_a0, mean_a1, mean_a2, mean_b0, mean_b1, mean_b2]:
            common.release_temp_buffer(buf)

    else:
        # ---- 1-Channel Path ----
        # mean_p = box(src)
        mean_p = _box_filter_1ch(src_gpu, radius, buffer_provider)

        # mean_Ip = box(guide * src)
        Ip_buf = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        _gf_mul_kernel(guide_gpu, src_gpu, Ip_buf, h, w)
        mean_Ip = _box_filter_1ch(Ip_buf, radius, buffer_provider)
        common.release_temp_buffer(Ip_buf)

        # var_I = mean_II - mean_I^2, cov_Ip = mean_Ip - mean_I * mean_p
        var_I = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        cov_Ip = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        _gf_compute_var_cov_kernel(mean_I, mean_p, mean_II, mean_Ip,
                                     var_I, cov_Ip, h, w)

        for buf in [mean_II, mean_Ip]:
            common.release_temp_buffer(buf)

        # a = cov_Ip / (var_I + eps), b = mean_p - a * mean_I
        a_buf = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        b_buf = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
        _gf_compute_ab_kernel(var_I, cov_Ip, mean_I, mean_p,
                                a_buf, b_buf, epsilon, h, w)

        for buf in [var_I, cov_Ip]:
            common.release_temp_buffer(buf)

        # mean_a = box(a), mean_b = box(b)
        mean_a = _box_filter_1ch(a_buf, radius, buffer_provider)
        mean_b = _box_filter_1ch(b_buf, radius, buffer_provider)
        common.release_temp_buffer(a_buf)
        common.release_temp_buffer(b_buf)

        # Final output: q = mean_a * guide + mean_b
        if dst is not None:
            dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                     buffer_provider=buffer_provider)
        else:
            dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

        _gf_output_kernel(mean_a, mean_b, guide_gpu, dst_gpu, h, w)

        for buf in [mean_a, mean_b]:
            common.release_temp_buffer(buf)

    # Cleanup inputs
    if guide_is_temp:
        common.release_temp_buffer(guide_gpu)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, is_numpy)
