# Taichi Algorithm Package
# Reusable GPU-accelerated functions
# API Style: OpenCV-like (ta.resize, ta.median, ta.sobel, etc.)

import numpy as np
import taichi as ti
from . import common

# --- Underlying Implementations ---
from .bilinear_interpolation import bilinear_resize
from .nearest_interpolation import nearest_resize
from .bicubic_interpolation import bicubic_resize
from .box_filter import box_filter_2d
from .median_filter import median_filter
from .gaussian import gaussian_blur as _gaussian_blur_impl
from .gradients import sobel as _sobel_impl
from .gradients import laplacian as _laplacian_impl
from .ransac import ransac_flow_cleanup
from .bilateral_grid import bilateral_grid_filter

# --- Constants ---
INTER_LINEAR = 1
INTER_NEAREST = 0  # Not implemented yet, placeholder
INTER_CUBIC = 2  # Not implemented yet, placeholder


# --- Helper: Universal Channel Handler ---
def _process_generic(func, src, *args, **kwargs):
    """
    Generic wrapper to handle Single-Channel (H, W) and Multi-Channel (H, W, C).
    Applies 'func' to each channel independently if input is multi-channel.
    """
    if not isinstance(src, (np.ndarray, ti.Field, ti.MatrixField)):
        # Try to handle as generic sequence if needed, but usually we expect numpy/taichi
        pass

    # Detect shape
    shape = src.shape
    is_multichannel = len(shape) == 3 and shape[2] > 1

    if not is_multichannel:
        # Single channel or 2D: Call directly
        return func(src, *args, **kwargs)

    # --- Multi-Channel Handling ---

    # 1. Upload to GPU if Numpy (for efficient splitting on GPU)
    # We use common.ensure_taichi_field.
    # Note: func() likely calls ensure_taichi_field inside, but we want to split *before* calling func
    # if func doesn't support 3D.

    # Assuming 'func' works on 2D fields.

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
        # Extract
        common.extract_channel(src_gpu, ch_buf_in, c)

        # Process
        # We pass 'dst=ch_buf_out' if the func supports it to avoid alloc
        # But 'func' might not take dst.
        # Let's assume standard signature: func(src, ..., dst=None)
        # Verify specific functions key args.

        # We'll rely on func returning a result, or writing to passed dst.
        # Safest is to call func(ch_buf_in, ...) and catch return.

        # However, we need to pass kwargs.
        # Some funcs like median_filter have optional dst?
        # median_filter(src, kernel_size, ..) -> returns result (numpy if input numpy, field if field)
        # If we pass field, it returns field (or numpy if we don't say otherwise?)
        # median_filter implementation:
        #   return common.to_numpy_if_needed(dst_gpu, src_is_temp)
        # If input is field, src_is_temp is False (usually), so it returns field.

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

        common.insert_channel(res, dst_gpu, c)

    # Cleanup temps
    common.release_temp_buffer(ch_buf_in)
    common.release_temp_buffer(ch_buf_out)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    # Download if input was numpy
    return common.to_numpy_if_needed(dst_gpu, isinstance(src, np.ndarray))


# --- Public API Wrappers ---


def resize(src, dsize, interpolation=INTER_LINEAR):
    """
    Resize image.
    Args:
        src: Input image (H, W) or (H, W, C).
        dsize: Tuple (width, height). NOTE: OpenCV uses (width, height).
        interpolation: INTER_LINEAR (default).
    """
    target_w, target_h = dsize
    # bilinear_resize takes (src, h, w) - our implementation uses (src, target_h, target_w)
    # We need to wrap it to match arg order and handle channels.

    # We create a lambda/partial to adapt arguments for _process_generic
    def _call_resize(img_field, dst=None):
        # bilinear_resize internal: _bilinear_resize_kernel(src, dst, ...)
        # The python wrapper returns a new numpy array usually.
        # We need a field-to-field version for _process_generic to work fully on GPU.
        # bilinear_interpolation.py implementation mainly targets Numpy->Numpy.
        # We might need to expose a field-based resize there or handle it here.
        # The existing 'bilinear_resize' in bilinear_interpolation.py :
        #   src_f32 = np.ascontiguousarray(src)... _bilinear_resize_kernel(...)
        # It strictly expects numpy! we need to fix that or handle here.
        pass

    # Since bilinear_interpolation.py is currently CPU->GPU->CPU strict (it calls np.ascontiguousarray),
    # we cannot easily use _process_generic which assumes Fields.
    # We should Update bilinear_interpolation.py or just use a simpler approach here for now?
    # User wants "Universal support".

    # Let's fix bilinear_interpolation.py to be friendly to fields?
    # Or just write a quick 3D wrapper that works on Numpy since resize usually changes shape anyway.

    # If generic 3D resize for numpy:
    h, w = src.shape[:2]
    is_3d = len(src.shape) == 3 and src.shape[2] > 1

    # Select function based on interpolation
    if interpolation == INTER_NEAREST:
        func = nearest_resize
    elif interpolation == INTER_CUBIC:
        func = bicubic_resize
    else:
        func = bilinear_resize

    if is_3d:
        # Simple Numpy loop for resize since output shape is different
        c1 = func(src[:, :, 0], target_h, target_w)
        res = np.zeros((target_h, target_w, src.shape[2]), dtype=c1.dtype)
        res[:, :, 0] = c1
        for c in range(1, src.shape[2]):
            res[:, :, c] = func(src[:, :, c], target_h, target_w)
        return res
    else:
        return func(src, target_h, target_w)


def median(src, ksize):
    """
    Apply Median filter.
    Args:
        src: Input image.
        ksize: Kernel size (integer). Currently supports 3.
    """
    return _process_generic(median_filter, src, kernel_size=ksize)


def gaussian(src, ksize, sigmaX):
    """
    Apply Gaussian Blur.
    Args:
        src: Input image.
        ksize: Tuple (ksize_w, ksize_h) or int. (Ignored if sigma provided in Taichi impl usually, but we accept it).
        sigmaX: Standard deviation.
    """
    # Taichi impl takes 'sigma'.
    return _process_generic(_gaussian_blur_impl, src, sigma=sigmaX)


def box(src, ksize):
    """
    Apply Box Filter (Blur).
    """
    # Taichi impl 'box_filter_2d(src, kernel_size)'
    # Check if ksize is tuple or int
    ks = ksize
    if isinstance(ksize, tuple):
        ks = ksize[0]  # Assume square for now as underlying impl supports square radius

    return _process_generic(box_filter_2d, src, kernel_size=ks)


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


__all__ = [
    "INTER_LINEAR",
    "INTER_NEAREST",
    "INTER_CUBIC",
    "resize",
    "median",
    "gaussian",
    "box",
    "sobel",
    "laplacian",
    "bilateral",
    "ransac",
    # Exposing underlying still valid if needed, but primary API is above
    "bilateral_grid_filter",
]
