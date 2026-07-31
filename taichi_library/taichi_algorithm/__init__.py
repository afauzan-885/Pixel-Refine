# Taichi Algorithm Package
# Reusable GPU-accelerated functions
# API Style: OpenCV-like (ta.resize, ta.median, ta.sobel, etc.)

import numpy as np
import os
import importlib
from taichi_library.config import AOT_MODE

ti = None
if AOT_MODE == "0":
    try:
        ti = importlib.import_module("taichi")
    except ImportError:
        pass

# --- Core Imports ---
from . import common
from . import aot_wrapper

if AOT_MODE == "1":
    from .aot_wrapper import *
else:
    from .common import (
        split,
        merge,
        extract_channel,
        insert_channel,
        copy,
    )

    # --- Underlying Implementations ---
    from .interpolation.bilinear_interpolation import (
        bilinear_resize,
        sample_at_bilinear,
    )
    from .interpolation.nearest_interpolation import nearest_resize
    from .interpolation.bicubic_interpolation import (
        bicubic_resize,
        sample_at_bicubic,
        sample_at,
        cubic_hermite,
    )
    from .smoothing.box_filter import box_filter, box_filter_2d
    from .smoothing.median_filter import median_filter
    from .smoothing.gaussian import gaussian_blur as _gaussian_blur_impl
    from .math_ops.gradients import sobel as _sobel_impl
    from .math_ops.gradients import laplacian as _laplacian_impl
    from .alignment.ransac import ransac_flow_cleanup
    from .smoothing.bilateral_grid import bilateral_grid_filter
    from .pyramid.pyramid import (
        build_image_pyramid,
        build_image_pyramid_gpu,
        upsample_flow,
    )
    from .alignment.phase_correlation import phase_correlation
    from .pyramid.fft import fft2, ifft2
    from .alignment.ncc import zncc, match_template, global_translate_zncc
    from .interpolation.remap import remap
    from .demosaicing.Hamilton_demosaice import hamilton_demosaic
    from .demosaicing.arm_demosaice import arm_demosaic
    from .demosaicing.mlri_admm_demosaice import (
        mlri_admm_demosaic,
        mlri_admm_demosaic_1channel,
        mlri_admm_demosaic_half_res,
        mlri_admm_demosaic_rgb_half_res,
        mlri_admm_demosaic_3channel,
    )
    from .alignment.mtb import align_mtb
    from .image_processing.enhance_image import enhance_grayscale
    from .image_processing.color_convert import (
        cvtColor_extended,
        COLOR_BGR2HSV,
        COLOR_HSV2BGR,
        COLOR_BGR2LAB,
        COLOR_LAB2BGR,
        COLOR_BGR2YCrCb,
        COLOR_YCrCb2BGR,
    )
    from .image_processing.otsu import (
        otsu_threshold,
        THRESH_BINARY,
        THRESH_BINARY_INV,
        THRESH_OTSU,
    )
    from .smoothing.guided_filter import guided_filter
    from .image_processing.clahe import clahe
    from .image_processing.canny import canny
    from .image_processing.hough import hough_lines, hough_lines_with_canny
    from .denoising.nlm import non_local_means
    from .denoising.bm3d import hfcd_denoise, build_dct_matrix
    from .image_processing.inpaint import inpaint, INPAINT_TELEA, INPAINT_NS
    from .image_processing.seamless_clone import (
        seamless_clone,
        NORMAL_CLONE,
        MIXED_CLONE,
        MONOCHROME_TRANSFER,
    )
    from .optical_flow.farneback_flow import farneback_flow
    from .optical_flow.lucas_kanade import calcOpticalFlowPyrLK as lucas_kanade_flow
    from .image_processing.morphology import dilate, erode
    from .image_processing.filter2d import filter2d
    from .image_processing.normalize import (
        normalize,
        NORM_INF,
        NORM_L1,
        NORM_L2,
        NORM_MINMAX,
    )
    from .image_processing.copy_make_border import (
        copy_make_border,
        BORDER_CONSTANT,
        BORDER_REFLECT_101,
        BORDER_REPLICATE,
    )
    from .image_processing.threshold import (
        threshold,
        THRESH_BINARY,
        THRESH_BINARY_INV,
        THRESH_TRUNC,
        THRESH_TOZERO,
        THRESH_TOZERO_INV,
        THRESH_OTSU,
    )
    from .math_ops.ssim import ssim
    from .image_processing.histogram import histogram as gpu_histogram
    from .denoising.compute_spatial import compute_spatial_weight, NoiseEstimator
    from .image_processing.hdr_fusion import hdr_fuse, hdr_fuse_simple
    from .image_processing.tone_mapping import (
        reinhard_tone_map,
        srgb_gamma,
        local_tone_map,
        contrast_adjust,
        tone_map,
    )
    from .alignment.ransac import vsac_fundamental
    from .sfm.five_point_solver import solve_five_point
    from .sfm.cheirality_check import check_cheirality_minimal, check_cheirality_full
    from .sfm.triangulation import triangulate_adaptive
    from .sfm.feature_matching import bfmatcher_l2, bfmatcher_hamming
    from .sfm.bundle_adjustment import bundle_adjust_lm
    from .sfm.plane_sweep import plane_sweep_stereo, multi_view_plane_sweep
    from .sfm.point_cloud import (
        statistical_outlier_removal,
        radius_outlier_removal,
        voxel_downsample,
        estimate_normals,
        preprocess_point_cloud,
    )
    from .sfm.poisson_recon import poisson_reconstruct
    from .common import (
        svd_3x3_np,
        enforce_essential_np,
        hartley_normalize,
        denormalize_fundamental,
    )


# --- Constants ---
INTER_LINEAR = 1
INTER_NEAREST = 0
INTER_CUBIC = 2

# Color Constants
COLOR_BGR2GRAY = common.COLOR_BGR2GRAY
COLOR_RGB2GRAY = common.COLOR_RGB2GRAY
COLOR_GRAY2BGR = common.COLOR_GRAY2BGR
COLOR_GRAY2RGB = common.COLOR_GRAY2RGB

# Extended Color Conversion Constants
# (Imported from color_convert module above)


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


OPTFLOW_USE_INITIAL_FLOW = 4
OPTFLOW_FARNEBACK_GAUSSIAN = 256


def calcOpticalFlowFarneback(
    prev,
    next,
    flow=None,
    pyr_scale=0.5,
    levels=3,
    winsize=15,
    iterations=3,
    poly_n=5,
    poly_sigma=1.2,
    flags=0,
    preset="opencv",
    return_diagnostics=False,
):
    """OpenCV-style dense Farneback optical flow backed by taichi_aot."""
    from taichi_library import taichi_aot

    if preset != "opencv" or return_diagnostics:
        raise ValueError("Taichi AOT Farneback supports the OpenCV preset without diagnostics")
    return taichi_aot.farneback_flow(
        prev,
        next,
        pyr_scale=pyr_scale,
        num_levels=levels,
        win_size=winsize,
        num_iters=iterations,
        poly_n=poly_n,
        poly_sigma=poly_sigma,
        flags=flags,
        flow_init=flow,
    )


def calcOpticalFlowPyrLK(
    prev,
    next,
    prevPts=None,
    nextPts=None,
    winSize=(13, 13),
    maxLevel=2,
    criteria=None,
    flags=0,
    minEigThreshold=1e-4,
    grid_step=48,
    border_margin=8,
    overlap=0.35,
    adaptive=False,
    adaptive_threshold=1,
    motion_mode="fast",
    dense_mode="smooth",
    max_flow_px=0.0,
    return_gpu=False,
    return_diagnostics=False,
):
    """OpenCV-style Lucas-Kanade entrypoint with internal grid dense flow."""
    return aot_wrapper.calcOpticalFlowPyrLK(
        prev,
        next,
        prevPts=prevPts,
        nextPts=nextPts,
        winSize=winSize,
        maxLevel=maxLevel,
        criteria=criteria,
        flags=flags,
        minEigThreshold=minEigThreshold,
        grid_step=grid_step,
        border_margin=border_margin,
        overlap=overlap,
        adaptive=adaptive,
        adaptive_threshold=adaptive_threshold,
        motion_mode=motion_mode,
        dense_mode=dense_mode,
        max_flow_px=max_flow_px,
        return_gpu=return_gpu,
        return_diagnostics=return_diagnostics,
    )


def calcOpticalFlowPyrLKGrid(
    prev,
    next,
    winSize=(17, 17),
    maxLevel=2,
    criteria=None,
    grid_step=16,
    border_margin=8,
    motion_mode="fast",
    return_diagnostics=False,
):
    """Lucas-Kanade compact grid flow entrypoint for CPU-like densification."""
    return aot_wrapper.calcOpticalFlowPyrLKGrid(
        prev,
        next,
        winSize=winSize,
        maxLevel=maxLevel,
        criteria=criteria,
        grid_step=grid_step,
        border_margin=border_margin,
        motion_mode=motion_mode,
        return_diagnostics=return_diagnostics,
    )


# --- Core Utilities ---
cvtColor = common.cvtColor
absdiff = common.absdiff


def ncc(image, template):
    """
    Simplified Normalized Cross-Correlation (ZNCC) interface.
    Plug-and-play template matching using Spatial backend.
    """
    return zncc(image, template)


# --- AOT Math Ops ---
# Keep these API names aligned with the experimental wrapper while preserving
# the existing taichi_algorithm import surface in both AOT and JIT modes.
ta = aot_wrapper.ta
array = aot_wrapper.array
gpu_abs = aot_wrapper.gpu_abs
gpu_sqrt = aot_wrapper.gpu_sqrt
gpu_log = aot_wrapper.gpu_log
gpu_exp = aot_wrapper.gpu_exp
gpu_square = aot_wrapper.gpu_square
gpu_power = aot_wrapper.gpu_power
gpu_clip = aot_wrapper.gpu_clip
gpu_where = aot_wrapper.gpu_where
gpu_sum = aot_wrapper.gpu_sum
gpu_max = aot_wrapper.gpu_max
gpu_min = aot_wrapper.gpu_min
gpu_mean = aot_wrapper.gpu_mean
gpu_std = aot_wrapper.gpu_std
gpu_matmul = aot_wrapper.gpu_matmul
gpu_mat3_inv = aot_wrapper.gpu_mat3_inv
gpu_mat3_det = aot_wrapper.gpu_mat3_det
gpu_sort = aot_wrapper.gpu_sort
gpu_argsort = aot_wrapper.gpu_argsort
gpu_unique = aot_wrapper.gpu_unique
gpu_meshgrid = aot_wrapper.gpu_meshgrid
abs = aot_wrapper.gpu_abs
sqrt = aot_wrapper.gpu_sqrt
log = aot_wrapper.gpu_log
exp = aot_wrapper.gpu_exp
square = aot_wrapper.gpu_square
power = aot_wrapper.gpu_power
clip = aot_wrapper.gpu_clip
where = aot_wrapper.gpu_where
sum = aot_wrapper.gpu_sum
max = aot_wrapper.gpu_max
min = aot_wrapper.gpu_min
mean = aot_wrapper.gpu_mean
std = aot_wrapper.gpu_std
matmul = aot_wrapper.matmul
mat3_inv = aot_wrapper.gpu_mat3_inv
mat3_det = aot_wrapper.gpu_mat3_det
sort = aot_wrapper.gpu_sort
argsort = aot_wrapper.gpu_argsort
unique = aot_wrapper.gpu_unique
meshgrid = aot_wrapper.gpu_meshgrid


__all__ = [
    "INTER_LINEAR",
    "INTER_NEAREST",
    "INTER_CUBIC",
    "COLOR_BGR2GRAY",
    "COLOR_RGB2GRAY",
    "COLOR_GRAY2BGR",
    "COLOR_GRAY2RGB",
    # Extended color conversions
    "COLOR_BGR2HSV",
    "COLOR_HSV2BGR",
    "COLOR_BGR2LAB",
    "COLOR_LAB2BGR",
    "COLOR_BGR2YCrCb",
    "COLOR_YCrCb2BGR",
    "cvtColor_extended",
    # Thresholding
    "THRESH_BINARY",
    "THRESH_BINARY_INV",
    "THRESH_OTSU",
    "otsu_threshold",
    # Inpainting flags
    "INPAINT_TELEA",
    "INPAINT_NS",
    # Seamless clone flags
    "NORMAL_CLONE",
    "MIXED_CLONE",
    "MONOCHROME_TRANSFER",
    # Core API
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
    # New algorithms
    "guided_filter",
    "clahe",
    "canny",
    "hough_lines",
    "hough_lines_with_canny",
    "non_local_means",
    "hfcd_denoise",
    "build_dct_matrix",
    "inpaint",
    "seamless_clone",
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
    "arm_demosaic",
    "mlri_admm_demosaic",
    "mlri_admm_demosaic_1channel",
    "mlri_admm_demosaic_half_res",
    "mlri_admm_demosaic_rgb_half_res",
    "mlri_admm_demosaic_3channel",
    "align_mtb",
    "farneback_flow",
    "calcOpticalFlowFarneback",
    "calcOpticalFlowPyrLK",
    "calcOpticalFlowPyrLKGrid",
    "OPTFLOW_USE_INITIAL_FLOW",
    "OPTFLOW_FARNEBACK_GAUSSIAN",
    "dilate",
    "erode",
    # New native GPU modules
    "filter2d",
    "normalize",
    "NORM_INF",
    "NORM_L1",
    "NORM_L2",
    "NORM_MINMAX",
    "copy_make_border",
    "BORDER_CONSTANT",
    "BORDER_REFLECT_101",
    "BORDER_REPLICATE",
    "threshold",
    "THRESH_BINARY",
    "THRESH_BINARY_INV",
    "THRESH_TRUNC",
    "THRESH_TOZERO",
    "THRESH_TOZERO_INV",
    "THRESH_OTSU",
    "ssim",
    "gpu_histogram",
    "compute_spatial_weight",
    "NoiseEstimator",
    "hdr_fuse",
    "hdr_fuse_simple",
    "reinhard_tone_map",
    "srgb_gamma",
    "local_tone_map",
    "contrast_adjust",
    "tone_map",
    # SfM Pipeline
    "vsac_fundamental",
    "solve_five_point",
    "check_cheirality_minimal",
    "check_cheirality_full",
    "triangulate_adaptive",
    "bfmatcher_l2",
    "bfmatcher_hamming",
    "bundle_adjust_lm",
    "plane_sweep_stereo",
    "multi_view_plane_sweep",
    "statistical_outlier_removal",
    "radius_outlier_removal",
    "voxel_downsample",
    "estimate_normals",
    "preprocess_point_cloud",
    "poisson_reconstruct",
    "svd_3x3_np",
    "enforce_essential_np",
    "hartley_normalize",
    "denormalize_fundamental",
    "aot_wrapper",
    "ta",
    "array",
    # Math Ops GPU
    "gpu_abs",
    "gpu_sqrt",
    "gpu_log",
    "gpu_exp",
    "gpu_square",
    "gpu_power",
    "gpu_clip",
    "gpu_where",
    "gpu_sum",
    "gpu_max",
    "gpu_min",
    "gpu_mean",
    "gpu_std",
    "gpu_matmul",
    "gpu_mat3_inv",
    "gpu_mat3_det",
    "gpu_sort",
    "gpu_argsort",
    "gpu_unique",
    "gpu_meshgrid",
    # NumPy-like Math Ops aliases
    "abs",
    "sqrt",
    "log",
    "exp",
    "square",
    "power",
    "clip",
    "where",
    "sum",
    "max",
    "min",
    "mean",
    "std",
    "matmul",
    "mat3_inv",
    "mat3_det",
    "sort",
    "argsort",
    "unique",
    "meshgrid",
]
