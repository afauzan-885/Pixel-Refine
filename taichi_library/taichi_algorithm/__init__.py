# Taichi Algorithm Package
# Reusable GPU-accelerated functions
# API Style: OpenCV-like (ta.resize, ta.median, ta.sobel, etc.)

import numpy as np
import os
import importlib

ti = None
if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
    except ImportError:
        pass

# --- Core Imports ---
from . import common
from .common import (
    split,
    merge,
    extract_channel,
    insert_channel,
    copy,
)

# --- Underlying Implementations ---
from .bilinear_interpolation import bilinear_resize, sample_at_bilinear
from .nearest_interpolation import nearest_resize
from .bicubic_interpolation import (
    bicubic_resize,
    sample_at_bicubic,
    sample_at,
    cubic_hermite,
)
from .box_filter import box_filter, box_filter_2d
from .median_filter import median_filter
from .gaussian import gaussian_blur as _gaussian_blur_impl
from .gradients import sobel as _sobel_impl
from .gradients import laplacian as _laplacian_impl
from .ransac import ransac_flow_cleanup
from .bilateral_grid import bilateral_grid_filter
from .pyramid import build_image_pyramid, build_image_pyramid_gpu, upsample_flow
from .phase_correlation import phase_correlation
from .fft import fft2, ifft2
from .ncc import zncc, match_template, global_translate_zncc
from .remap import remap
from .enhance_image import enhance_grayscale
from .Hamilton_demosaice import hamilton_demosaic

# --- Constants ---
INTER_LINEAR = 1
INTER_NEAREST = 0
INTER_CUBIC = 2

# Color Constants
COLOR_BGR2GRAY = common.COLOR_BGR2GRAY
COLOR_RGB2GRAY = common.COLOR_RGB2GRAY
COLOR_GRAY2BGR = common.COLOR_GRAY2BGR
COLOR_GRAY2RGB = common.COLOR_GRAY2RGB


# --- Helper: Universal Channel Handler ---
def _process_generic(func, src, *args, **kwargs):
    """
    Generic wrapper to handle Single-Channel (H, W) and Multi-Channel (H, W, C).
    Applies 'func' to each channel independently if input is multi-channel.
    """
    is_taichi_field = False
    if ti is not None:
        is_taichi_field = isinstance(src, (ti.Field, ti.MatrixField))
    if not isinstance(src, np.ndarray) and not is_taichi_field:
        # Try to handle as generic sequence if needed, but usually we expect numpy/taichi
        pass

    shape = src.shape
    is_3d = len(shape) == 3
    if not is_3d:
        # 2D case: Call directly
        return func(src, *args, **kwargs)

    # --- Multi-Channel Handling ---
    if ti is None:
        raise ImportError("Taichi is not available for JIT multi-channel processing")

    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
    h, w = shape[:2]
    c_count = shape[2]

    # Allocate output (we need to know what func returns? Usually same size image)
    # This wrapper assumes image-to-image filter.
    dst_gpu = common.get_temp_buffer(shape, ti.f32)

    # Temp buffer for single channel processing
    ch_buf_in = common.get_temp_buffer((h, w), ti.f32)
    ch_buf_out = common.get_temp_buffer((h, w), ti.f32)

    for c in range(c_count):
        # Extract (use low-level function)
        common._extract_channel_lowlevel(src_gpu, ch_buf_in, c)

        # Process
        # We pass 'dst=ch_buf_out' if the func supports it to avoid alloc
        # But 'func' might not take dst.
        # Let's assume standard signature: func(src, ..., dst=None)
        # Verify specific functions key args.

        # We'll rely on func returning a result, or writing to passed dst.
        res = func(ch_buf_in, *args, dst=ch_buf_out, **kwargs)

        # The result might be 'ch_buf_out' or a new buffer if func ignored dst.
        # Insert back
        # If func returns a numpy array (because logic in func decidied to download), that would be bad for perf.
        # But ensure_taichi_field inside func will see 'ch_buf_in' is a field, so it won't force numpy return
        # unless 'dst' logic forces it.

        # We need to make sure 'func' doesn't download.

        # Most implementations in this package:
        # return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
        # Here src_is_temp (inside func) will be False because we pass an existing field 'ch_buf_in'.
        # So it returns field (likely `res` is `ch_buf_out`).

        # Insert back (use low-level function)
        common._insert_channel_lowlevel(res, dst_gpu, c)

    # Cleanup temps
    common.release_temp_buffer(ch_buf_in)
    common.release_temp_buffer(ch_buf_out)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    # Download if input was numpy
    return common.to_numpy_if_needed(dst_gpu, isinstance(src, np.ndarray))


# --- Public API Wrappers ---


def resize(src, dsize, interpolation=INTER_LINEAR, dst=None):
    """
    Resize image with full GPU pipeline support.
    OpenCV-compatible: Same as cv2.resize()

    Args:
        src: Input image (H, W) or (H, W, C).
        dsize: Tuple (width, height). NOTE: OpenCV uses (width, height).
        interpolation: INTER_LINEAR (default), INTER_CUBIC.
        dst: Optional output buffer.
    """
    target_w, target_h = dsize

    if interpolation == INTER_CUBIC:
        return bicubic_resize(src, target_h, target_w)
    elif interpolation == INTER_NEAREST:
        return nearest_resize(src, target_h, target_w)
    else:
        return bilinear_resize(src, target_h, target_w, dst=dst)


def median(src, ksize, dst=None):
    """
    Apply Median filter.
    OpenCV-compatible: Same as cv2.medianBlur()
    """
    # Median implementation might still need 3D support in its kernel
    # If not supported, _process_generic handles it.
    return _process_generic(median_filter, src, kernel_size=ksize, dst=dst)


def gaussian(src, ksize, sigmaX=0, sigmaY=0, dst=None):
    """
    Apply Gaussian Blur.
    OpenCV-compatible: Same as cv2.GaussianBlur()

    Args:
        src: Input image.
        ksize: Tuple (w, h) or int.
        sigmaX: Standard deviation in X.
        sigmaY: Standard deviation in Y (ignored for now, uses sigmaX).
        dst: Optional output buffer.
    """
    ks = ksize[0] if isinstance(ksize, tuple) else ksize
    return _gaussian_blur_impl(src, dst=dst, sigma=sigmaX, kernel_size=ks)


def box(src, ksize, dst=None):
    """
    Apply Box Filter (mean blur).
    OpenCV-compatible: Same as cv2.blur() or cv2.boxFilter()
    """
    ks = ksize[0] if isinstance(ksize, tuple) else ksize
    return box_filter(src, dst=dst, kernel_size=ks)


def sobel(src, dx, dy, ksize=3):
    """
    Apply Sobel operator.
    Args:
        dx: order of derivative x.
        dy: order of derivative y.
    Returns:
        The requested derivative map.
    """
    # logic: call _sobel_impl which returns (grad_x, grad_y)
    # We need to handle this specially because _process_generic expects func to return 1 image.

    # We can wrap sobel to return just one.

    def _sobel_wrapper(img, dst=None):
        # We ignore dst here for the internal call, we handle result selection
        gx, gy = _sobel_impl(img)
        if dx >= 1 and dy == 0:
            return gx
        elif dx == 0 and dy >= 1:
            return gy
        else:
            # Combined? OpenCV usually separates.
            # If user asks both, we return weighted?
            # For now return Gx + Gy or Magnitude?
            # OpenCV 'sobel' returns one output.
            # If dx=1, dy=1 -> mixed partial?
            # Let's support dx=1,dy=0 and dx=0,dy=1 primarily.
            return gx  # Default fallthrough

    return _process_generic(_sobel_wrapper, src)


def laplacian(src, ksize=1):
    """Laplacian operator."""
    return _process_generic(_laplacian_impl, src)


def bilateral(src, d, sigmaColor, sigmaSpace):
    """
    Bilateral Filter.
    Args:
        d: Diameter (mapped to s_s/spatial step loosely or ignored if using grid params).
           OpenCV uses 'd'. Taichi bilateral grid uses s_s, s_r.
           Let's map: sigmaSpace -> sigma_s. sigmaColor -> sigma_r.
           d -> s_s (spatial step)? actually s_s controls grid coarseness.
    """
    # Mapping OpenCV params to Bilateral Grid
    # OpenCV: bilateralFilter(src, d, sigmaColor, sigmaSpace)
    # Grid: s_s (spatial bin size), s_r (range bin size), sigma_s, sigma_r

    # We'll use reasonable defaults for bin sizes based on sigmas or d.
    # s_s approx sigmaSpace or d.
    # s_r approx sigmaColor.

    _s_s = max(int(sigmaSpace), 4)
    _s_r = max(int(sigmaColor), 4)

    return bilateral_grid_filter(
        src, s_s=_s_s, s_r=_s_r, sigma_s=sigmaSpace, sigma_r=sigmaColor
    )


def ransac(flow, threshold=3.0):
    """
    Apply RANSAC to flow field.
    Args:
        flow: Optical flow field (H, W, 2).
        threshold: Inlier threshold.
    """
    # RANSAC expects 2-channel flow (vector field).
    # Do NOT use _process_generic which splits channels.
    return ransac_flow_cleanup(flow, threshold=threshold)


# --- Core Utilities ---
cvtColor = common.cvtColor
absdiff = common.absdiff


def ncc(image, template):
    """
    Simplified Normalized Cross-Correlation (ZNCC) interface.
    Plug-and-play template matching using Spatial backend.
    """
    return zncc(image, template)


__all__ = [
    "INTER_LINEAR",
    "INTER_NEAREST",
    "INTER_CUBIC",
    "COLOR_BGR2GRAY",
    "COLOR_RGB2GRAY",
    "COLOR_GRAY2BGR",
    "COLOR_GRAY2RGB",
    "resize",
    "median",
    "gaussian",
    "box",
    "sobel",
    "laplacian",
    "bilateral",
    "ransac",
    "cvtColor",
    "absdiff",
    "remap",
    # Pyramid APIs
    "build_image_pyramid",
    "build_image_pyramid_gpu",
    "upsample_flow",
    # Bicubic Interpolation APIs
    "sample_at_bicubic",
    "sample_at",
    "cubic_hermite",
    # Bilinear Interpolation APIs
    "sample_at_bilinear",
    # Channel Operations
    "split",
    "merge",
    "extract_channel",
    "insert_channel",
    "copy",
    "phase_correlation",
    "fft2",
    "ifft2",
    "zncc",
    "match_template",
    "global_translate_zncc",
    "ncc",
    "enhance_grayscale",
    "hamilton_demosaic",
]
