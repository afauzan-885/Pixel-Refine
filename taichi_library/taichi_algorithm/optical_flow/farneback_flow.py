"""
Farneback Optical Flow - Taichi GPU (From Scratch, OpenCV-Parity)
=================================================================
Based on: Gunnar Farnebäck, "Two-Frame Motion Estimation Based on Polynomial
Expansion", SCIA 2003.

Algorithm:
  1. Separable polynomial expansion (vertical + horizontal) for both images.
  2. Build constraint tensors G (2x2) and h (2-vec) from averaged A matrices
     and delta-b with flow prior.
  3. Gaussian-smooth the tensors spatially.
  4. Solve G*d = h per pixel via Cramer's rule.
  5. Coarse-to-fine pyramid with iterative refinement.

Parity target: cv2.calcOpticalFlowFarneback (OpenCV 4.x, optflowgf.cpp).
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


# =============================================================================
# CPU Constants (pure NumPy, no Taichi needed)
# =============================================================================

def prepare_gaussian_constants(poly_n, poly_sigma=1.2):
    """
    Compute separable polynomial expansion weights and inverse Gram matrix
    constants.  Direct port of OpenCV FarnebackPrepareGaussian (optflowgf.cpp
    lines 60-113).

    Returns
    -------
    g   : ndarray (radius+1,) float32  – Gaussian half-kernel (positive side)
    xg  : ndarray (radius+1,) float32  – x*g(x) half-kernel
    xxg : ndarray (radius+1,) float32  – x²*g(x) half-kernel
    ig11, ig03, ig33, ig55 : float     – inverse Gram matrix constants
    """
    n = poly_n // 2  # radius
    if poly_sigma < 1e-10:
        poly_sigma = n * 0.3

    # Full 1-D kernel [-n .. +n]
    x = np.arange(-n, n + 1, dtype=np.float64)
    g_full = np.exp(-x ** 2 / (2.0 * poly_sigma ** 2))
    g_full /= g_full.sum()
    xg_full = x * g_full
    xxg_full = x ** 2 * g_full

    # Build the 6x6 Gram matrix for basis [1, x, y, x², y², xy]
    # Exploiting symmetry: G[i,j] = G[j,i]
    G = np.zeros((6, 6), dtype=np.float64)
    for iy in range(-n, n + 1):
        for ix in range(-n, n + 1):
            w = g_full[iy + n] * g_full[ix + n]
            x2 = float(ix * ix)
            x4 = x2 * x2
            y2 = float(iy * iy)
            G[0, 0] += w
            G[1, 1] += w * x2          # = G[2,2]
            G[3, 3] += w * x4          # = G[4,4]
            G[5, 5] += w * x2 * y2
    # Fill symmetric entries
    G[2, 2] = G[1, 1]
    G[0, 3] = G[1, 1]     # sum(w * x^2) = sum(w * y^2)
    G[3, 0] = G[0, 3]
    G[0, 4] = G[0, 3]     # same by symmetry
    G[4, 0] = G[0, 4]
    G[4, 4] = G[3, 3]
    G[3, 4] = G[5, 5]     # sum(w * x^2 * y^2)
    G[4, 3] = G[3, 4]

    invG = np.linalg.inv(G)
    ig11 = float(invG[1, 1])
    ig03 = float(invG[0, 3])
    ig33 = float(invG[3, 3])
    ig55 = float(invG[5, 5])

    # Return only positive half [0..n]
    return (
        g_full[n:].astype(np.float32),
        xg_full[n:].astype(np.float32),
        xxg_full[n:].astype(np.float32),
        ig11, ig03, ig33, ig55,
    )


def compute_smoothing_weights(win_size):
    """Gaussian half-kernel for tensor smoothing.
    sigma = (win_size // 2) * 0.3  (OpenCV convention)."""
    radius = win_size // 2
    sigma = radius * 0.3
    if sigma < 1e-10:
        sigma = 1.0
    weights = []
    total = 0.0
    for i in range(radius + 1):
        w = np.exp(-(i * i) / (2.0 * sigma * sigma))
        weights.append(w)
        total += w if i == 0 else 2.0 * w
    weights = np.array(weights, dtype=np.float32) / total
    # Pad to max radius (20) for static unrolling
    if len(weights) < 21:
        padded = np.zeros(21, dtype=np.float32)
        padded[: len(weights)] = weights
        weights = padded
    return weights, radius


# =============================================================================
# Taichi Kernels (only available when AOT_MODE=0)
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def _border_weight(d: ti.i32) -> ti.f32:
        """Lookup border weight for distance d (0-4) from OpenCV."""
        w = 1.0
        if d == 0:
            w = 0.14
        elif d == 1:
            w = 0.14
        elif d == 2:
            w = 0.4472
        elif d == 3:
            w = 0.4472
        elif d == 4:
            w = 0.4472
        return w

    @ti.func
    def _border_scale(y: ti.i32, x: ti.i32, h: ti.i32, w: ti.i32) -> ti.f32:
        """OpenCV-style multiplicative border suppression."""
        sy = 1.0
        sx = 1.0
        dy = ti.min(y, h - 1 - y)
        dx = ti.min(x, w - 1 - x)
        if dy < 5:
            sy = _border_weight(dy)
        if dx < 5:
            sx = _border_weight(dx)
        return sy * sx

    # -----------------------------------------------------------------
    # 1. Polynomial Expansion — Separable (vertical then horizontal)
    # -----------------------------------------------------------------

    @ti.kernel
    def _poly_exp_vertical_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        g: ti.types.ndarray(dtype=ti.f32, ndim=1),
        xg: ti.types.ndarray(dtype=ti.f32, ndim=1),
        xxg: ti.types.ndarray(dtype=ti.f32, ndim=1),
        radius: ti.i32,
    ):
        """Vertical separable pass.
        Output: dst[y,x,0] = Gaussian-weighted sum
                dst[y,x,1] = odd moment (y-derivative proxy)
                dst[y,x,2] = even moment (y² proxy)
        Uses CLAMP boundary (matching OpenCV optflowgf.cpp lines 151-152).
        """
        for y, x in ti.ndrange(h, w):
            s0 = src[y, x] * g[0]   # sum
            s1 = 0.0                 # odd (y-deriv)
            s2 = src[y, x] * xxg[0]  # even (y²)
            for k in ti.static(range(1, 12)):
                if k <= radius:
                    # Use CLAMP boundary like OpenCV
                    ty = ti.max(0, ti.min(y - k, h - 1))
                    by = ti.max(0, ti.min(y + k, h - 1))
                    top = src[ty, x]
                    bot = src[by, x]
                    s0 += g[k] * (top + bot)
                    s1 += xg[k] * (bot - top)
                    s2 += xxg[k] * (top + bot)
            dst[y, x, 0] = s0
            dst[y, x, 1] = s1
            dst[y, x, 2] = s2

    @ti.kernel
    def _poly_exp_horizontal_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        g: ti.types.ndarray(dtype=ti.f32, ndim=1),
        xg: ti.types.ndarray(dtype=ti.f32, ndim=1),
        xxg: ti.types.ndarray(dtype=ti.f32, ndim=1),
        ig11: ti.f32,
        ig03: ti.f32,
        ig33: ti.f32,
        ig55: ti.f32,
        radius: ti.i32,
    ):
        """Horizontal pass + inverse Gram projection.
        Input : src from vertical pass (H,W,3)
        Output: dst[y,x,:] = [b_y, b_x, A_yy, A_xx, A_xy]
        Uses CLAMP boundary (matching OpenCV optflowgf.cpp lines 168-172).
        """
        for y, x in ti.ndrange(h, w):
            b1 = src[y, x, 0] * g[0]
            b2 = 0.0
            b3 = src[y, x, 1] * g[0]
            b4 = 0.0
            b5 = src[y, x, 2] * g[0]
            b6 = 0.0
            for k in ti.static(range(1, 12)):
                if k <= radius:
                    # Use CLAMP boundary like OpenCV
                    lx = ti.max(0, ti.min(x - k, w - 1))
                    rx = ti.max(0, ti.min(x + k, w - 1))
                    l0 = src[y, lx, 0]
                    r0 = src[y, rx, 0]
                    l1 = src[y, lx, 1]
                    r1 = src[y, rx, 1]
                    l2 = src[y, lx, 2]
                    r2 = src[y, rx, 2]
                    tg = r0 + l0
                    b1 += tg * g[k]
                    b4 += tg * xxg[k]
                    b2 += (r0 - l0) * xg[k]
                    b3 += (r1 + l1) * g[k]
                    b6 += (r1 - l1) * xg[k]
                    b5 += (r2 + l2) * g[k]

            # Apply inverse Gram matrix constants
            dst[y, x, 0] = b3 * ig11          # b_y
            dst[y, x, 1] = b2 * ig11          # b_x
            dst[y, x, 2] = b1 * ig03 + b5 * ig33  # A_yy
            dst[y, x, 3] = b1 * ig03 + b4 * ig33  # A_xx
            dst[y, x, 4] = b6 * ig55          # A_xy

    # -----------------------------------------------------------------
    # 2. Tensor Construction (FarnebackUpdateMatrices equivalent)
    # -----------------------------------------------------------------

    @ti.kernel
    def _compute_tensors_kernel(
        R0: ti.types.ndarray(dtype=ti.f32, ndim=3),
        R1: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        M: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
    ):
        """Build constraint tensor M per pixel.
        R0: ref poly expansion   (H,W,5) = [b_y, b_x, A_yy, A_xx, A_xy]
        R1: comp poly expansion  (H,W,5)
        flow: current flow       (H,W,2) = [dx, dy]
        M:  output tensor        (H,W,5) = [G00, G01, G11, h0, h1]

        Follows OpenCV FarnebackUpdateMatrices (optflowgf.cpp lines 217-311).
        """
        for y, x in ti.ndrange(h, w):
            dx = flow[y, x, 0]
            dy = flow[y, x, 1]

            # Sample R1 at warped position (y+dy, x+dx) using bilinear
            fx = float(x) + dx
            fy = float(y) + dy

            ix = ti.cast(ti.floor(fx), ti.i32)
            iy = ti.cast(ti.floor(fy), ti.i32)
            frac_x = fx - float(ix)
            frac_y = fy - float(iy)

            # Check if within bounds (OpenCV-style)
            in_bounds = (ix >= 0) and (ix < w - 1) and (iy >= 0) and (iy < h - 1)
            
            r2 = 0.0
            r3 = 0.0
            r4 = 0.0
            r5 = 0.0
            r6 = 0.0
            
            if in_bounds:
                # Bilinear interpolation (CLAMP boundary like OpenCV)
                w00 = (1.0 - frac_x) * (1.0 - frac_y)
                w01 = frac_x * (1.0 - frac_y)
                w10 = (1.0 - frac_x) * frac_y
                w11 = frac_x * frac_y

                # Interpolate all 5 channels of R1
                r2 = R1[iy, ix, 0] * w00 + R1[iy, ix+1, 0] * w01 + R1[iy+1, ix, 0] * w10 + R1[iy+1, ix+1, 0] * w11
                r3 = R1[iy, ix, 1] * w00 + R1[iy, ix+1, 1] * w01 + R1[iy+1, ix, 1] * w10 + R1[iy+1, ix+1, 1] * w11
                r4 = R1[iy, ix, 2] * w00 + R1[iy, ix+1, 2] * w01 + R1[iy+1, ix, 2] * w10 + R1[iy+1, ix+1, 2] * w11
                r5 = R1[iy, ix, 3] * w00 + R1[iy, ix+1, 3] * w01 + R1[iy+1, ix, 3] * w10 + R1[iy+1, ix+1, 3] * w11
                r6 = R1[iy, ix, 4] * w00 + R1[iy, ix+1, 4] * w01 + R1[iy+1, ix, 4] * w10 + R1[iy+1, ix+1, 4] * w11
                
                # Average A matrices (OpenCV convention)
                r4 = (R0[y, x, 2] + r4) * 0.5    # A_yy
                r5 = (R0[y, x, 3] + r5) * 0.5    # A_xx
                r6 = (R0[y, x, 4] + r6) * 0.25   # A_xy
                
                # Delta b + A * d_0
                r2 = (R0[y, x, 0] - r2) * 0.5    # delta_b_y
                r3 = (R0[y, x, 1] - r3) * 0.5    # delta_b_x
                r2 += r4 * dy + r6 * dx
                r3 += r6 * dy + r5 * dx
            else:
                # Out of bounds: use only R0 values (OpenCV behavior)
                r4 = R0[y, x, 2]
                r5 = R0[y, x, 3]
                r6 = R0[y, x, 4] * 0.5    # Note: 0.5, not 0.25 for out-of-bounds!
                # r2 and r3 need to be computed from R0 (OpenCV line 286-287)
                r2 = (R0[y, x, 0] - 0.0) * 0.5    # delta_b_y
                r3 = (R0[y, x, 1] - 0.0) * 0.5    # delta_b_x
                # Add flow prior
                r2 += r4 * dy + r6 * dx
                r3 += r6 * dy + r5 * dx

            # Border suppression
            scale = _border_scale(y, x, h, w)
            r2 *= scale
            r3 *= scale
            r4 *= scale
            r5 *= scale
            r6 *= scale

            # G matrix and h vector
            M[y, x, 0] = r4 * r4 + r6 * r6           # G[0,0]
            M[y, x, 1] = (r4 + r5) * r6               # G[0,1]
            M[y, x, 2] = r5 * r5 + r6 * r6            # G[1,1]
            M[y, x, 3] = r4 * r2 + r6 * r3            # h[0]
            M[y, x, 4] = r6 * r2 + r5 * r3            # h[1]

    # -----------------------------------------------------------------
    # 3. Gaussian Smoothing of 5-channel Tensors (separable)
    # -----------------------------------------------------------------
    # Note: OpenCV Farneback uses Gaussian blur when OPTFLOW_FARNEBACK_GAUSSIAN flag is set
    # This matches FarnebackUpdateFlow_GaussianBlur in optflowgf.cpp.
    # sigma = m * 0.3 where m = winSize/2

    @ti.kernel
    def _gaussian_blur_x_5ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        weights: ti.types.ndarray(dtype=ti.f32, ndim=1),
        radius: ti.i32,
    ):
        """Horizontal Gaussian blur on 5-channel tensor.
        Uses Gaussian weights for smoothing, matching OpenCV's default behavior.
        """
        for y, x in ti.ndrange(h, w):
            a0 = src[y, x, 0] * weights[0]
            a1 = src[y, x, 1] * weights[0]
            a2 = src[y, x, 2] * weights[0]
            a3 = src[y, x, 3] * weights[0]
            a4 = src[y, x, 4] * weights[0]
            for k in ti.static(range(1, 21)):
                if k <= radius:
                    wk = weights[k]
                    lx = common.reflect_idx(x - k, w)
                    rx = common.reflect_idx(x + k, w)
                    a0 += (src[y, lx, 0] + src[y, rx, 0]) * wk
                    a1 += (src[y, lx, 1] + src[y, rx, 1]) * wk
                    a2 += (src[y, lx, 2] + src[y, rx, 2]) * wk
                    a3 += (src[y, lx, 3] + src[y, rx, 3]) * wk
                    a4 += (src[y, lx, 4] + src[y, rx, 4]) * wk
            # Weights pre-normalized by compute_smoothing_weights() — no division needed
            dst[y, x, 0] = a0
            dst[y, x, 1] = a1
            dst[y, x, 2] = a2
            dst[y, x, 3] = a3
            dst[y, x, 4] = a4

    @ti.kernel
    def _gaussian_blur_y_5ch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
        weights: ti.types.ndarray(dtype=ti.f32, ndim=1),
        radius: ti.i32,
    ):
        """Vertical Gaussian blur on 5-channel tensor.
        Uses Gaussian weights for smoothing, matching OpenCV's default behavior.
        """
        for y, x in ti.ndrange(h, w):
            a0 = src[y, x, 0] * weights[0]
            a1 = src[y, x, 1] * weights[0]
            a2 = src[y, x, 2] * weights[0]
            a3 = src[y, x, 3] * weights[0]
            a4 = src[y, x, 4] * weights[0]
            for k in ti.static(range(1, 21)):
                if k <= radius:
                    wk = weights[k]
                    ty = common.reflect_idx(y - k, h)
                    by = common.reflect_idx(y + k, h)
                    a0 += (src[ty, x, 0] + src[by, x, 0]) * wk
                    a1 += (src[ty, x, 1] + src[by, x, 1]) * wk
                    a2 += (src[ty, x, 2] + src[by, x, 2]) * wk
                    a3 += (src[ty, x, 3] + src[by, x, 3]) * wk
                    a4 += (src[ty, x, 4] + src[by, x, 4]) * wk
            # Weights pre-normalized by compute_smoothing_weights() — no division needed
            dst[y, x, 0] = a0
            dst[y, x, 1] = a1
            dst[y, x, 2] = a2
            dst[y, x, 3] = a3
            dst[y, x, 4] = a4

    # -----------------------------------------------------------------
    # 4. Flow Update — Solve 2x2 system per pixel
    # -----------------------------------------------------------------

    @ti.kernel
    def _update_flow_kernel(
        M: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: ti.i32,
        w: ti.i32,
    ):
        """Solve G*d = h at each pixel using Cramer's rule.
        Regularization epsilon = 1e-3 (OpenCV line 564).
        """
        for y, x in ti.ndrange(h, w):
            g11 = M[y, x, 0]
            g12 = M[y, x, 1]
            g22 = M[y, x, 2]
            hh1 = M[y, x, 3]
            hh2 = M[y, x, 4]

            det = g11 * g22 - g12 * g12
            idet = 1.0 / (det + 1e-3)

            # Solve for flow update
            # The system solves for [d_y, d_x] where d_y is y-component and d_x is x-component
            # Using Cramer's rule: d_y = (g22*hh1 - g12*hh2)/det, d_x = (g11*hh2 - g12*hh1)/det
            # We store: flow[0] = d_x (horizontal), flow[1] = d_y (vertical) - OpenCV convention
            flow[y, x, 0] = (g11 * hh2 - g12 * hh1) * idet  # dx
            flow[y, x, 1] = (g22 * hh1 - g12 * hh2) * idet  # dy

    # -----------------------------------------------------------------
    # 5. Utility Kernels
    # -----------------------------------------------------------------

    @ti.kernel
    def _clear_flow_kernel(flow: ti.types.ndarray(dtype=ti.f32, ndim=3)):
        h, w = flow.shape[0], flow.shape[1]
        for y, x in ti.ndrange(h, w):
            flow[y, x, 0] = 0.0
            flow[y, x, 1] = 0.0


# =============================================================================
# Public API (JIT execution path)
# =============================================================================

@ti_thread
def farneback_flow(
    ref_gray,
    comp_gray,
    pyr_scale=0.5,
    num_levels=3,
    win_size=15,
    num_iters=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    flow_init=None,
    buffer_provider="pool",
):
    """
    Compute Farneback dense optical flow between two grayscale images.
    OpenCV-compatible: matches cv2.calcOpticalFlowFarneback() output.

    Parameters
    ----------
    ref_gray  : ndarray (H, W) float32 – reference (previous) frame [0, 255] range
    comp_gray : ndarray (H, W) float32 – comparison (next) frame [0, 255] range

    NOTE: Input images must be float32 in [0, 255] range (matching OpenCV's
    internal representation after uint8 conversion). If your images are in
    [0, 1], multiply by 255 first.
    pyr_scale : float – pyramid scale factor (default 0.5 = 2x pyramid)
    num_levels: int   – number of pyramid levels
    win_size  : int   – smoothing window size (must be odd)
    num_iters : int   – iterations per pyramid level
    poly_n    : int   – polynomial expansion neighborhood (5 or 7)
    poly_sigma: float – polynomial expansion sigma
    flags     : int   – OPTFLOW_FARNEBACK_GAUSSIAN = 256 (always Gaussian here)
    flow_init : ndarray (H,W,2) or None – initial flow estimate

    Returns
    -------
    flow : ndarray (H, W, 2) float32
           flow[:,:,0] = dx (horizontal), flow[:,:,1] = dy (vertical)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available for JIT Farneback flow")

    from ..pyramid import pyramid as pyr_mod

    # --- Prepare inputs ---
    ref_np = np.ascontiguousarray(ref_gray, dtype=np.float32)
    comp_np = np.ascontiguousarray(comp_gray, dtype=np.float32)
    h_orig, w_orig = ref_np.shape

    ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_np, dtype=ti.f32, buffer_provider=buffer_provider)
    comp_gpu, comp_is_temp = common.ensure_taichi_field(comp_np, dtype=ti.f32, buffer_provider=buffer_provider)

    # --- Build pyramids ---
    downscale_factor = 1.0 / pyr_scale  # e.g. 0.5 -> 2.0
    ref_pyr = pyr_mod.build_image_pyramid_gpu(
        ref_gpu, n_levels=num_levels, min_size=32,
        downscale_factor=downscale_factor, buffer_provider=buffer_provider,
    )
    comp_pyr = pyr_mod.build_image_pyramid_gpu(
        comp_gpu, n_levels=num_levels, min_size=32,
        downscale_factor=downscale_factor, buffer_provider=buffer_provider,
    )
    actual_levels = len(ref_pyr)

    # --- Pre-compute constants ---
    g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(poly_n, poly_sigma)
    smooth_w, smooth_radius = compute_smoothing_weights(win_size)
    poly_radius = poly_n // 2

    # Upload constants
    g_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    g_gpu.from_numpy(g_w)
    xg_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    xg_gpu.from_numpy(xg_w)
    xxg_gpu = ti.ndarray(dtype=ti.f32, shape=(poly_radius + 1,))
    xxg_gpu.from_numpy(xxg_w)
    smooth_gpu = ti.ndarray(dtype=ti.f32, shape=(smooth_radius + 1,))
    _smooth_slice = smooth_w[: smooth_radius + 1].copy()
    # Renormalize after slicing (smooth_w is padded to 21 elements with zeros)
    _smooth_total = _smooth_slice[0] + 2.0 * float(np.sum(_smooth_slice[1:]))
    if _smooth_total > 1e-10:
        _smooth_slice = _smooth_slice / _smooth_total
    smooth_gpu.from_numpy(_smooth_slice)

    # --- Coarse-to-fine ---
    prev_flow = None

    for lvl in range(actual_levels - 1, -1, -1):
        ref_lvl = ref_pyr[lvl]
        comp_lvl = comp_pyr[lvl]
        hl = ref_lvl.shape[0]
        wl = ref_lvl.shape[1]

        # Allocate flow buffer for this level
        flow_lvl = common.get_temp_buffer((hl, wl, 2), ti.f32, buffer_provider)

        if prev_flow is not None:
            # Upsample flow from coarser level
            scale_up = float(ref_lvl.shape[0]) / float(prev_flow.shape[0])
            pyr_mod.upsample_flow_gpu(prev_flow, flow_lvl, float(scale_up))
        elif flow_init is not None and lvl == 0:
            fi, fi_temp = common.ensure_taichi_field(flow_init, dtype=ti.f32, buffer_provider=buffer_provider)
            common._copy_kernel(fi, flow_lvl)
            if fi_temp:
                common.release_temp_buffer(fi)
        else:
            _clear_flow_kernel(flow_lvl)

        # Polynomial expansion of both images at this level
        vert_buf = common.get_temp_buffer((hl, wl, 3), ti.f32, buffer_provider)
        R0 = common.get_temp_buffer((hl, wl, 5), ti.f32, buffer_provider)
        R1 = common.get_temp_buffer((hl, wl, 5), ti.f32, buffer_provider)

        _poly_exp_vertical_kernel(ref_lvl, vert_buf, hl, wl, g_gpu, xg_gpu, xxg_gpu, poly_radius)
        _poly_exp_horizontal_kernel(vert_buf, R0, hl, wl, g_gpu, xg_gpu, xxg_gpu,
                                     ig11, ig03, ig33, ig55, poly_radius)
        _poly_exp_vertical_kernel(comp_lvl, vert_buf, hl, wl, g_gpu, xg_gpu, xxg_gpu, poly_radius)
        _poly_exp_horizontal_kernel(vert_buf, R1, hl, wl, g_gpu, xg_gpu, xxg_gpu,
                                     ig11, ig03, ig33, ig55, poly_radius)
        common.release_temp_buffer(vert_buf)

        # Iterative refinement
        M = common.get_temp_buffer((hl, wl, 5), ti.f32, buffer_provider)
        M_smooth = common.get_temp_buffer((hl, wl, 5), ti.f32, buffer_provider)

        for _it in range(num_iters):
            _compute_tensors_kernel(R0, R1, flow_lvl, M, hl, wl)
            _gaussian_blur_x_5ch_kernel(M, M_smooth, hl, wl, smooth_gpu, smooth_radius)
            _gaussian_blur_y_5ch_kernel(M_smooth, M, hl, wl, smooth_gpu, smooth_radius)
            _update_flow_kernel(M, flow_lvl, hl, wl)

        common.release_temp_buffer(M)
        common.release_temp_buffer(M_smooth)
        common.release_temp_buffer(R0)
        common.release_temp_buffer(R1)

        prev_flow = flow_lvl

    # --- Download result ---
    ti.sync()
    flow_np = prev_flow.to_numpy()

    # --- Cleanup ---
    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)
    for lvl_buf in ref_pyr[1:]:  # skip level 0 (same as ref_gpu)
        common.release_temp_buffer(lvl_buf)
    for lvl_buf in comp_pyr[1:]:
        common.release_temp_buffer(lvl_buf)
    # Release all flow buffers except the final one
    # (prev_flow IS the level-0 flow we want to keep until downloaded)
    common.release_temp_buffer(prev_flow)

    return flow_np
