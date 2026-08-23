# Marker: GPU_NATIVE_MARKER_V3
"""
Canny Edge Detector - Taichi GPU Implementation
================================================
Multi-stage edge detection with non-maximum suppression and hysteresis.

Reference:
  - Canny, J. (1986). "A Computational Approach to Edge Detection."
    IEEE Transactions on Pattern Analysis and Machine Intelligence, PAMI-8(6).

Pipeline:
  1. Gaussian blur (pre-smoothing)
  2. Sobel gradients (Gx, Gy)
  3. Gradient magnitude + direction
  4. Non-Maximum Suppression (NMS) — thin edges
  5. Double thresholding — classify strong/weak edges
  6. Hysteresis — promote weak edges connected to strong ones (iterative GPU)
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
    from ..math_ops.gradients import sobel as _sobel_impl
    from ..smoothing.gaussian import gaussian_blur as _gaussian_impl
except ImportError:
    pass

# Edge state constants
_STRONG = 255.0
_WEAK = 128.0

if TAICHI_AVAILABLE:

    # =========================================================================
    # Stage 3: Magnitude then NMS. These must remain separate dispatches:
    # NMS reads neighbouring magnitudes, so fusing them races on GPU.
    # =========================================================================
    @ti.kernel
    def _canny_magnitude_kernel(gx: ti.types.ndarray(), gy: ti.types.ndarray(),
                                 mag: ti.types.ndarray(),
                                 h: int, w: int):
        for y, x in ti.ndrange(h, w):
            dx = gx[y, x]
            dy = gy[y, x]
            # OpenCV's default Canny mode uses the L1 gradient norm
            # (L2gradient=False). Keep this explicit so all backends share
            # the same threshold domain and edge topology.
            mag[y, x] = ti.abs(dx) + ti.abs(dy)

    @ti.kernel
    def _canny_nms_kernel(gx: ti.types.ndarray(), gy: ti.types.ndarray(),
                          mag: ti.types.ndarray(), nms: ti.types.ndarray(),
                          h: int, w: int):
        """
        Compute gradient magnitude and apply Non-Maximum Suppression.
        NMS quantizes gradient direction to 4 angles (0, 45, 90, 135 degrees)
        and suppresses non-maximum pixels along the gradient direction.
        """
        for y, x in ti.ndrange(h, w):
            dx = gx[y, x]
            dy = gy[y, x]
            m = ti.abs(dx) + ti.abs(dy)
            if m < 1e-6:
                nms[y, x] = 0.0
                continue

            # Quantize direction to the same four sectors used by OpenCV.
            # Avoid atan2 here: besides being cheaper on OpenGL, the signed
            # diagonal test below keeps the gradient direction consistent.
            ax = ti.abs(dx)
            ay = ti.abs(dy)
            n1 = 0.0
            n2 = 0.0
            tg22 = 0.41421356237

            if ax > ay * (1.0 / tg22):
                # Gradient near 0 degrees: compare left/right.
                lx = tm.clamp(x - 1, 0, w - 1)
                rx = tm.clamp(x + 1, 0, w - 1)
                n1 = mag[y, lx]
                n2 = mag[y, rx]
            elif ay > ax * (1.0 / tg22):
                # Gradient near 90 degrees: compare up/down.
                ty2 = tm.clamp(y - 1, 0, h - 1)
                by = tm.clamp(y + 1, 0, h - 1)
                n1 = mag[ty2, x]
                n2 = mag[by, x]
            elif dx * dy >= 0.0:
                # Gradient near +45 degrees: top-left/bottom-right.
                n1 = mag[tm.clamp(y - 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]
                n2 = mag[tm.clamp(y + 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]
            else:
                # Gradient near -45 degrees: top-right/bottom-left.
                n1 = mag[tm.clamp(y - 1, 0, h - 1), tm.clamp(x + 1, 0, w - 1)]
                n2 = mag[tm.clamp(y + 1, 0, h - 1), tm.clamp(x - 1, 0, w - 1)]

            # Suppress if not local maximum.  Graphics backends can differ by
            # a few ulps in Sobel values (for example SPIR-V versus LLVM), so
            # an exact comparison can flip a plateau pixel and change the
            # binary hysteresis topology.  A small normalized-space epsilon
            # makes ties deterministic while remaining far below the public
            # threshold tolerance.
            nms_epsilon = 1e-6
            if m + nms_epsilon >= n1 and m + nms_epsilon >= n2:
                nms[y, x] = m
            else:
                nms[y, x] = 0.0

    # =========================================================================
    # Stage 4: Double Thresholding
    # =========================================================================
    @ti.kernel
    def _canny_threshold_kernel(nms: ti.types.ndarray(), edges: ti.types.ndarray(),
                                 low_thresh: float, high_thresh: float,
                                 h: int, w: int):
        """Classify pixels as STRONG, WEAK, or suppressed."""
        for y, x in ti.ndrange(h, w):
            val = nms[y, x]
            if val >= high_thresh:
                edges[y, x] = 255.0  # STRONG
            elif val >= low_thresh:
                edges[y, x] = 128.0  # WEAK
            else:
                edges[y, x] = 0.0    # SUPPRESSED

    # =========================================================================
    # Stage 5: Hysteresis — Iterative Weak-to-Strong Promotion
    # =========================================================================
    @ti.kernel
    def _canny_hysteresis_kernel(edges: ti.types.ndarray(), changed: ti.types.ndarray(),
                                   h: int, w: int):
        """
        One iteration of hysteresis: promote WEAK pixels adjacent to STRONG pixels.
        Sets changed[0] = 1 if any pixel was promoted.
        """
        for y, x in ti.ndrange(h, w):
            if edges[y, x] == 128.0:  # WEAK
                # Check 8-connected neighbors for STRONG
                promote = False
                for dy in ti.static(range(-1, 2)):
                    for dx in ti.static(range(-1, 2)):
                        # Skip center pixel without using continue (AOT restriction)
                        if not (dy == 0 and dx == 0):
                            ny = tm.clamp(y + dy, 0, h - 1)
                            nx = tm.clamp(x + dx, 0, w - 1)
                            if edges[ny, nx] == 255.0:
                                promote = True
                if promote:
                    edges[y, x] = 255.0
                    changed[0] = 1

    @ti.kernel
    def _canny_finalize_kernel(edges: ti.types.ndarray(), dst: ti.types.ndarray(),
                                 h: int, w: int):
        """Finalize: STRONG -> 255, everything else -> 0."""
        for y, x in ti.ndrange(h, w):
            if edges[y, x] == 255.0:
                dst[y, x] = 255.0
            else:
                dst[y, x] = 0.0


@ti_thread
def canny(src, low_threshold=50.0, high_threshold=150.0,
           aperture_size=3, dst=None, buffer_provider="pool"):
    """
    Canny Edge Detector (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.Canny()

    Args:
        src: Input grayscale image (H, W), uint8 or float32.
        low_threshold: Lower threshold for hysteresis (weak edges).
        high_threshold: Upper threshold for hysteresis (strong edges).
                        Typically 2-3x low_threshold.
        aperture_size: Sobel aperture size (currently only 3 supported).
        dst: Optional output buffer (H, W).
        buffer_provider: Buffer pool provider.

    Returns:
        Binary edge map with values {0, 255}.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]

    # Step 1: Gaussian pre-smoothing (light blur to reduce noise)
    blurred = _gaussian_impl(src_gpu, dst=None, sigma=1.0, kernel_size=5)

    # Step 2: Sobel gradients
    gx, gy = _sobel_impl(blurred)

    # Step 3: Magnitude + NMS
    mag = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    nms = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    _canny_mag_nms_kernel(gx, gy, mag, nms, h, w)

    # Step 4: Double thresholding
    edges = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    _canny_threshold_kernel(nms, edges, low_threshold, high_threshold, h, w)

    # Clean up intermediates
    for buf in [mag, nms]:
        common.release_temp_buffer(buf)
    # Release sobel outputs if they are temp buffers
    if hasattr(gx, 'shape'):
        common.release_temp_buffer(gx)
    if hasattr(gy, 'shape'):
        common.release_temp_buffer(gy)

    # Step 5: Hysteresis (iterative — max 256 passes to handle any edge length)
    changed = ti.ndarray(dtype=ti.i32, shape=(1,))
    max_iterations = 256
    for _ in range(max_iterations):
        changed.fill(0)
        _canny_hysteresis_kernel(edges, changed, h, w)
        # Check if any changes occurred
        if changed.to_numpy()[0] == 0:
            break

    # Step 6: Finalize
    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    _canny_finalize_kernel(edges, dst_gpu, h, w)

    # Cleanup
    common.release_temp_buffer(edges)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, is_numpy)
