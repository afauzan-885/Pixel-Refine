"""Bilinear Interpolation - Taichi GPU"""

import numpy as np
import taichi as ti
import taichi.math as tm
from .taichi_worker import ti_thread, TAICHI_AVAILABLE


if TAICHI_AVAILABLE:

    @ti.kernel
    def _bilinear_resize_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = r * (float(h_src) / float(h_dst))
            x_src = c * (float(w_src) / float(w_dst))

            y0 = int(ti.floor(y_src))
            x0 = int(ti.floor(x_src))
            y1 = ti.min(y0 + 1, h_src - 1)
            x1 = ti.min(x0 + 1, w_src - 1)

            wy = y_src - float(y0)
            wx = x_src - float(x0)

            q00, q01 = src[y0, x0], src[y0, x1]
            q10, q11 = src[y1, x0], src[y1, x1]

            r1 = tm.mix(q00, q01, wx)
            r2 = tm.mix(q10, q11, wx)
            dst[r, c] = tm.mix(r1, r2, wy)


def bilinear_resize(src, target_h: int, target_w: int, dst=None):
    """
    Smart bilinear resize API that auto-detects input type and returns appropriate output.

    **Full GPU Pipeline Support:**
    - If input is Taichi field → stays on GPU, returns Taichi field
    - If input is NumPy array → uploads to GPU, processes, downloads to NumPy

    All Taichi operations are synchronized via @ti_thread.

    Args:
        src: Input image - can be NumPy array OR Taichi ndarray
        target_h: Target height
        target_w: Target width
        dst: Optional pre-allocated output buffer (must match input type)

    Returns:
        Resized image in the same format as input (NumPy or Taichi)

    Examples:
        >>> # CPU path (NumPy → NumPy)
        >>> img_np = np.random.rand(100, 100).astype(np.float32)
        >>> resized_np = bilinear_resize(img_np, 50, 50)
        >>> type(resized_np)  # numpy.ndarray

        >>> # GPU path (Taichi → Taichi) - ZERO COPY!
        >>> img_gpu = ti.ndarray(dtype=ti.f32, shape=(100, 100))
        >>> resized_gpu = bilinear_resize(img_gpu, 50, 50)
        >>> type(resized_gpu)  # taichi.lang.ndarray.ScalarNdarray

        >>> # Chain operations on GPU (FAST!)
        >>> upscaled = bilinear_resize(img_gpu, 200, 200)  # Stays on GPU
        >>> blurred = gaussian(upscaled, ksize=5, sigmaX=2.0)  # Stays on GPU
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(src, "to_numpy")

    @ti_thread
    def _run_gpu_resize(src_data, h_dst, w_dst, dst_data=None):
        h_src, w_src = src_data.shape[:2]

        # Prepare source data for GPU
        if is_taichi_input:
            # Already on GPU - use directly (ZERO COPY!)
            src_gpu = src_data
        else:
            # NumPy input - need to upload to GPU
            src_gpu = np.ascontiguousarray(src_data, dtype=np.float32)

        # Determine output buffer
        if dst_data is None:
            if is_taichi_input:
                # Input is GPU → output should be GPU field
                dst_data = ti.ndarray(dtype=ti.f32, shape=(h_dst, w_dst))
            else:
                # Input is NumPy → output will be NumPy (allocated as temp GPU buffer)
                dst_data = np.zeros((h_dst, w_dst), dtype=np.float32)

        # Run kernel (works with both NumPy and Taichi fields)
        _bilinear_resize_kernel(src_gpu, dst_data, h_src, w_src, h_dst, w_dst)

        return dst_data

    return _run_gpu_resize(src, target_h, target_w, dst)


# Legacy alias for backward compatibility
def bilinear_resize_gpu(src_gpu, target_h: int, target_w: int, dst_gpu=None):
    """
    DEPRECATED: Use bilinear_resize() instead.
    This function is kept for backward compatibility only.
    """
    return bilinear_resize(src_gpu, target_h, target_w, dst_gpu)


def bilinear_upsample_2x(src: np.ndarray) -> np.ndarray:
    h, w = src.shape[:2]
    return bilinear_resize(src, h * 2, w * 2)


def bilinear_downsample_2x(src: np.ndarray) -> np.ndarray:
    h, w = src.shape[:2]
    return bilinear_resize(src, h // 2, w // 2)


def sample_at_bilinear(img, x, y, channel=None):
    """
    Sample image at fractional coordinates using bilinear interpolation.

    High-level API for point-wise bilinear sampling - perfect for:
    - Fast warping with optical flow
    - Real-time transformations
    - When speed is more important than quality

    Args:
        img: Input image (H, W) for grayscale or (H, W, C) for color
        x: X coordinate (can be fractional, e.g., 10.5)
        y: Y coordinate (can be fractional, e.g., 20.3)
        channel: Optional channel index for multi-channel images (0, 1, 2, etc.)
                If None and image is multi-channel, returns all channels as array

    Returns:
        Interpolated pixel value(s) at (x, y)

    Note:
        Bilinear is faster but lower quality than bicubic.
        Use ta.sample_at() for bicubic (higher quality).

    Example:
        >>> # Single point sampling
        >>> value = ta.sample_at_bilinear(image, 10.5, 20.3)
        >>>
        >>> # Sample specific channel (e.g., green channel)
        >>> green_val = ta.sample_at_bilinear(rgb_image, 10.5, 20.3, channel=1)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from . import common

    # Use common.bilinear_at for the actual implementation
    if len(img.shape) == 2:
        # Grayscale image
        return common.bilinear_at(img, x, y)
    elif len(img.shape) == 3:
        # Multi-channel image
        if channel is not None:
            # Sample specific channel
            return common.bilinear_at(img[:, :, channel], x, y)
        else:
            # Sample all channels
            return np.array(
                [common.bilinear_at(img[:, :, c], x, y) for c in range(img.shape[2])]
            )
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")
