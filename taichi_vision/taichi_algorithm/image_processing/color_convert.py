# Marker: GPU_NATIVE_MARKER_V3
"""
Color Space Conversions - Taichi GPU Implementation
====================================================
Extended color space conversions: BGR <-> HSV, BGR <-> LAB, BGR <-> YCrCb.
All conversions are per-pixel (embarrassingly parallel) with branchless GPU formulations.

Reference:
  - OpenCV cvtColor() documentation
  - CIE 1976 LAB standard
  - BT.601 YCrCb standard
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

# --- Color Conversion Constants ---
COLOR_BGR2HSV = 40
COLOR_HSV2BGR = 54
COLOR_BGR2LAB = 44
COLOR_LAB2BGR = 56
COLOR_BGR2YCrCb = 36
COLOR_YCrCb2BGR = 38

if TAICHI_AVAILABLE:

    # =========================================================================
    # BGR -> HSV (Branchless formulation)
    # =========================================================================
    @ti.kernel
    def _bgr2hsv_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert BGR [0,255] to HSV [H:0-180, S:0-255, V:0-255] (OpenCV convention).
        """
        for y, x in ti.ndrange(h, w):
            b = src[y, x, 0]
            g = src[y, x, 1]
            r = src[y, x, 2]

            cmax = ti.max(r, ti.max(g, b))
            cmin = ti.min(r, ti.min(g, b))
            delta = cmax - cmin

            # Value
            v_out = cmax

            # Saturation
            s_out = 0.0
            if cmax > 0.0:
                s_out = (delta / cmax) * 255.0

            # Hue (branchless with conditional offsets)
            hue = 0.0
            if delta > 0.0:
                # Determine which channel is max
                if r >= g and r >= b:
                    hue = 60.0 * ((g - b) / delta)
                    if hue < 0.0:
                        hue += 360.0
                elif g >= r and g >= b:
                    hue = 60.0 * ((b - r) / delta + 2.0)
                else:
                    hue = 60.0 * ((r - g) / delta + 4.0)

            # OpenCV convention: H in [0, 180]
            h_out = hue * 0.5

            dst[y, x, 0] = h_out
            dst[y, x, 1] = s_out
            dst[y, x, 2] = v_out

    # =========================================================================
    # HSV -> BGR
    # =========================================================================
    @ti.kernel
    def _hsv2bgr_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert HSV [H:0-180, S:0-255, V:0-255] back to BGR [0,255].
        """
        for y, x in ti.ndrange(h, w):
            h_in = src[y, x, 0] * 2.0  # Scale back to [0, 360]
            s_in = src[y, x, 1] / 255.0  # Normalize to [0, 1]
            v_in = src[y, x, 2]  # V in [0, 255]

            c = v_in * s_in
            h_prime = h_in / 60.0
            x_val = c * (1.0 - ti.abs(ti.math.mod(h_prime, 2.0) - 1.0))
            m = v_in - c

            r1, g1, b1 = 0.0, 0.0, 0.0
            if h_prime < 1.0:
                r1, g1, b1 = c, x_val, 0.0
            elif h_prime < 2.0:
                r1, g1, b1 = x_val, c, 0.0
            elif h_prime < 3.0:
                r1, g1, b1 = 0.0, c, x_val
            elif h_prime < 4.0:
                r1, g1, b1 = 0.0, x_val, c
            elif h_prime < 5.0:
                r1, g1, b1 = x_val, 0.0, c
            else:
                r1, g1, b1 = c, 0.0, x_val

            dst[y, x, 0] = b1 + m  # B
            dst[y, x, 1] = g1 + m  # G
            dst[y, x, 2] = r1 + m  # R

    # =========================================================================
    # BGR -> YCrCb (BT.601, purely linear - no branching)
    # =========================================================================
    @ti.kernel
    def _bgr2ycrcb_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert BGR [0,255] to YCrCb [0,255] using BT.601 coefficients.
        """
        for y, x in ti.ndrange(h, w):
            b = src[y, x, 0]
            g = src[y, x, 1]
            r = src[y, x, 2]

            y_out = 0.299 * r + 0.587 * g + 0.114 * b
            cr = (0.5 * r - 0.4187 * g - 0.0813 * b) + 128.0
            cb = (-0.1687 * r - 0.3313 * g + 0.5 * b) + 128.0

            dst[y, x, 0] = y_out
            dst[y, x, 1] = tm.clamp(cr, 0.0, 255.0)
            dst[y, x, 2] = tm.clamp(cb, 0.0, 255.0)

    # =========================================================================
    # YCrCb -> BGR
    # =========================================================================
    @ti.kernel
    def _ycrcb2bgr_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert YCrCb [0,255] back to BGR [0,255].
        """
        for y, x in ti.ndrange(h, w):
            y_val = src[y, x, 0]
            cr = src[y, x, 1] - 128.0
            cb = src[y, x, 2] - 128.0

            r = y_val + 1.402 * cr
            g = y_val - 0.3441 * cb - 0.7141 * cr
            b = y_val + 1.772 * cb

            dst[y, x, 0] = tm.clamp(b, 0.0, 255.0)
            dst[y, x, 1] = tm.clamp(g, 0.0, 255.0)
            dst[y, x, 2] = tm.clamp(r, 0.0, 255.0)

    # =========================================================================
    # BGR -> LAB (CIE 1976, via XYZ intermediate)
    # =========================================================================
    @ti.func
    def _lab_f(t: float) -> float:
        """CIE LAB nonlinear mapping f(t)."""
        # Piecewise: t^(1/3) if t > 0.008856, else 7.787*t + 16/116
        # AOT-compatible: use ti.select() instead of if/return
        threshold = 0.008856
        branch_a = ti.pow(ti.max(t, 1e-10), 1.0 / 3.0)  # Avoid pow(0, x)
        branch_b = 7.787 * t + 16.0 / 116.0
        return ti.select(t > threshold, branch_a, branch_b)

    @ti.func
    def _lab_f_inv(t: float) -> float:
        """Inverse CIE LAB mapping."""
        # AOT-compatible: use ti.select()
        threshold = 6.0 / 29.0
        branch_a = t * t * t
        branch_b = (t - 16.0 / 116.0) / 7.787
        return ti.select(t > threshold, branch_a, branch_b)

    @ti.kernel
    def _bgr2lab_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert BGR [0,255] to CIE LAB.
        Output: L [0,255], a [0,255] (centered at 128), b [0,255] (centered at 128).
        Uses D65 white point: Xn=0.95047, Yn=1.0, Zn=1.08883.
        """
        for y, x in ti.ndrange(h, w):
            # sRGB to linear
            b_srgb = src[y, x, 0] / 255.0
            g_srgb = src[y, x, 1] / 255.0
            r_srgb = src[y, x, 2] / 255.0

            # sRGB gamma decode (AOT-compatible with ti.select)
            r_lin = ti.select(r_srgb > 0.04045,
                              ti.pow((r_srgb + 0.055) / 1.055, 2.4),
                              r_srgb / 12.92)
            g_lin = ti.select(g_srgb > 0.04045,
                              ti.pow((g_srgb + 0.055) / 1.055, 2.4),
                              g_srgb / 12.92)
            b_lin = ti.select(b_srgb > 0.04045,
                              ti.pow((b_srgb + 0.055) / 1.055, 2.4),
                              b_srgb / 12.92)

            # RGB to XYZ (D65)
            x_xyz = 0.4124564 * r_lin + 0.3575761 * g_lin + 0.1804375 * b_lin
            y_xyz = 0.2126729 * r_lin + 0.7151522 * g_lin + 0.0721750 * b_lin
            z_xyz = 0.0193339 * r_lin + 0.1191920 * g_lin + 0.9503041 * b_lin

            # Normalize by D65 white point
            fx = _lab_f(x_xyz / 0.95047)
            fy = _lab_f(y_xyz / 1.0)
            fz = _lab_f(z_xyz / 1.08883)

            # LAB
            l_out = 116.0 * fy - 16.0
            a_out = 500.0 * (fx - fy)
            b_out = 200.0 * (fy - fz)

            # Map to [0, 255] range (OpenCV convention for 8-bit)
            dst[y, x, 0] = tm.clamp(l_out * 255.0 / 100.0, 0.0, 255.0)
            dst[y, x, 1] = tm.clamp(a_out + 128.0, 0.0, 255.0)
            dst[y, x, 2] = tm.clamp(b_out + 128.0, 0.0, 255.0)

    # =========================================================================
    # LAB -> BGR
    # =========================================================================
    @ti.kernel
    def _lab2bgr_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
        """
        Convert CIE LAB back to BGR [0,255].
        Input: L [0,255], a [0,255] (centered at 128), b [0,255] (centered at 128).
        """
        for y, x in ti.ndrange(h, w):
            # Unmap from [0, 255]
            l_out = src[y, x, 0] * 100.0 / 255.0
            a_out = src[y, x, 1] - 128.0
            b_out = src[y, x, 2] - 128.0

            # LAB to XYZ
            fy = (l_out + 16.0) / 116.0
            fx = a_out / 500.0 + fy
            fz = fy - b_out / 200.0

            x_xyz = 0.95047 * _lab_f_inv(fx)
            y_xyz = 1.0 * _lab_f_inv(fy)
            z_xyz = 1.08883 * _lab_f_inv(fz)

            # XYZ to linear RGB
            r_lin = 3.2404542 * x_xyz - 1.5371385 * y_xyz - 0.4985314 * z_xyz
            g_lin = -0.9692660 * x_xyz + 1.8760108 * y_xyz + 0.0415560 * z_xyz
            b_lin = 0.0556434 * x_xyz - 0.2040259 * y_xyz + 1.0572252 * z_xyz

            # Linear RGB to sRGB (gamma encode, AOT-compatible)
            r_srgb = ti.select(r_lin > 0.0031308,
                               1.055 * ti.pow(ti.max(r_lin, 1e-10), 1.0 / 2.4) - 0.055,
                               12.92 * r_lin)
            g_srgb = ti.select(g_lin > 0.0031308,
                               1.055 * ti.pow(ti.max(g_lin, 1e-10), 1.0 / 2.4) - 0.055,
                               12.92 * g_lin)
            b_srgb = ti.select(b_lin > 0.0031308,
                               1.055 * ti.pow(ti.max(b_lin, 1e-10), 1.0 / 2.4) - 0.055,
                               12.92 * b_lin)

            dst[y, x, 0] = tm.clamp(b_srgb * 255.0, 0.0, 255.0)
            dst[y, x, 1] = tm.clamp(g_srgb * 255.0, 0.0, 255.0)
            dst[y, x, 2] = tm.clamp(r_srgb * 255.0, 0.0, 255.0)


# =========================================================================
# Public API
# =========================================================================
def cvtColor_extended(src, code, dst=None, buffer_provider="pool"):
    """
    Extended color space conversion (GPU-accelerated).
    Supports HSV, LAB, YCrCb in addition to existing BGR<->Gray.

    Args:
        src: Input image (H, W, 3) uint8 or float32.
        code: Conversion code (COLOR_BGR2HSV, COLOR_HSV2BGR, etc.)
        dst: Optional output buffer.
        buffer_provider: Buffer pool provider.

    Returns:
        Converted image in same format as input.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]

    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
    else:
        dst_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)

    # Dispatch kernel based on conversion code
    if code == COLOR_BGR2HSV:
        _bgr2hsv_kernel(src_gpu, dst_gpu, h, w)
    elif code == COLOR_HSV2BGR:
        _hsv2bgr_kernel(src_gpu, dst_gpu, h, w)
    elif code == COLOR_BGR2YCrCb:
        _bgr2ycrcb_kernel(src_gpu, dst_gpu, h, w)
    elif code == COLOR_YCrCb2BGR:
        _ycrcb2bgr_kernel(src_gpu, dst_gpu, h, w)
    elif code == COLOR_BGR2LAB:
        _bgr2lab_kernel(src_gpu, dst_gpu, h, w)
    elif code == COLOR_LAB2BGR:
        _lab2bgr_kernel(src_gpu, dst_gpu, h, w)
    else:
        raise ValueError(f"Unsupported color conversion code: {code}")

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, is_numpy)
