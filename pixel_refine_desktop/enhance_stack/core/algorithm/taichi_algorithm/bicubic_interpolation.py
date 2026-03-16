import numpy as np
import taichi as ti
import taichi.math as tm
from .taichi_worker import ti_thread, TAICHI_AVAILABLE

if TAICHI_AVAILABLE:
    # ... (Kernels remain the same but will be executed via @ti_thread)
    @ti.func
    def cubic_hermite(A, B, C, D, t):
        a = -A / 2.0 + (3.0 * B) / 2.0 - (3.0 * C) / 2.0 + D / 2.0
        b = A - (5.0 * B) / 2.0 + 2.0 * C - D / 2.0
        c = -A / 2.0 + C / 2.0
        d = B
        return a * t * t * t + b * t * t + c * t + d

    @ti.func
    def cubic_hermite_weights(t):
        """Precalculate the 4 weights for cubic hermite interpolation."""
        t2 = t * t
        t3 = t2 * t
        w0 = -0.5 * t3 + t2 - 0.5 * t
        w1 = 1.5 * t3 - 2.5 * t2 + 1.0
        w2 = -1.5 * t3 + 2.0 * t2 + 0.5 * t
        w3 = 0.5 * t3 - 0.5 * t2
        return ti.Vector([w0, w1, w2, w3])

    @ti.kernel
    def _bicubic_resize_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = (r + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (c + 0.5) * (float(w_src) / float(w_dst)) - 0.5

            x_int = int(ti.floor(x_src))
            y_int = int(ti.floor(y_src))

            dx = x_src - x_int
            dy = y_src - y_int

            col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])
            for m in range(-1, 3):
                p = ti.Vector([0.0, 0.0, 0.0, 0.0])
                y_idx = tm.clamp(y_int + m, 0, h_src - 1)
                for n in range(-1, 3):
                    x_idx = tm.clamp(x_int + n, 0, w_src - 1)
                    p[n + 1] = src[y_idx, x_idx]
                col_results[m + 1] = cubic_hermite(p[0], p[1], p[2], p[3], dx)

            val = cubic_hermite(
                col_results[0], col_results[1], col_results[2], col_results[3], dy
            )
            dst[r, c] = val


def bicubic_resize(src, target_h: int, target_w: int, dst=None, buffer_provider="pool"):
    """
    Smart bicubic resize API that auto-detects input type and returns appropriate output.

    **Full GPU Pipeline Support:**
    - If input is Taichi field → stays on GPU, returns Taichi field
    - If input is NumPy array → uploads to GPU, processes, downloads to NumPy

    All Taichi operations are synchronized via @ti_thread.

    Args:
        src: Input image (NumPy array or Taichi field)
        target_h: Target height
        target_w: Target width
        dst: Optional pre-allocated output buffer
        buffer_provider: Pool provider for GPU allocations

    Returns:
        Resized image (same type as input unless dst is provided)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from . import common

    # Detect input type
    is_taichi_input = hasattr(src, "to_numpy")

    @ti_thread
    def _run_gpu_bicubic_resize(src_data, h_dst, w_dst, dst_data=None):
        src_gpu, src_is_temp = common.ensure_taichi_field(
            src_data, dtype=ti.f32, buffer_provider=buffer_provider
        )
        h_src, w_src = src_gpu.shape[:2]

        is_3d = len(src_gpu.shape) == 3
        c_count = src_gpu.shape[2] if is_3d else 1

        # Determine output buffer
        if dst_data is None:
            if is_taichi_input:
                # Input is GPU → output should be GPU field from pool
                shape = (h_dst, w_dst, c_count) if is_3d else (h_dst, w_dst)
                dst_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)
            else:
                # Input is NumPy → output will be NumPy (allocated as temp GPU buffer)
                dst_gpu = np.zeros((h_dst, w_dst), dtype=np.float32)
        else:
            dst_gpu, _ = common.ensure_taichi_field(
                dst_data, dtype=ti.f32, buffer_provider=buffer_provider
            )

        # Run kernel (works with both NumPy and Taichi fields)
        _bicubic_resize_kernel(src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)

        # Cleanup temp src
        if src_is_temp:
            common.release_temp_buffer(src_gpu)

        if not is_taichi_input:
            # If input was NumPy, dst_gpu is likely NumPy or result was written to NumPy
            # If dst_gpu is a field, we need to download it
            if hasattr(dst_gpu, "to_numpy"):
                res = dst_gpu.to_numpy()
                common.release_temp_buffer(dst_gpu)
                return res
            return dst_gpu

        return dst_gpu

    return _run_gpu_bicubic_resize(src, target_h, target_w, dst)


def sample_at_bicubic(img, x, y, channel=None):
    """
    Sample image at fractional coordinates using bicubic interpolation.

    High-level API for point-wise bicubic sampling - perfect for:
    - Warping with optical flow
    - Subpixel refinement in alignment
    - Custom geometric transformations

    Args:
        img: Input image (H, W) for grayscale or (H, W, C) for color
        x: X coordinate (can be fractional, e.g., 10.5)
        y: Y coordinate (can be fractional, e.g., 20.3)
        channel: Optional channel index for multi-channel images (0, 1, 2, etc.)
                If None and image is multi-channel, returns all channels as array

    Returns:
        Interpolated pixel value(s) at (x, y)

    Note:
        For faster (but lower quality) sampling, use ta.sample_at_bilinear()

    Example:
        >>> # Single point sampling for warping
        >>> value = ta.sample_at_bicubic(image, 10.5, 20.3)
        >>>
        >>> # Sample specific channel (e.g., green channel)
        >>> green_val = ta.sample_at_bicubic(rgb_image, 10.5, 20.3, channel=1)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from . import common

    # Use common.bicubic_at for the actual implementation
    # This is a user-friendly wrapper
    if len(img.shape) == 2:
        # Grayscale image
        return common.bicubic_at(img, x, y)
    elif len(img.shape) == 3:
        # Multi-channel image
        if channel is not None:
            # Sample specific channel
            return common.bicubic_at(img[:, :, channel], x, y)
        else:
            # Sample all channels
            return np.array(
                [common.bicubic_at(img[:, :, c], x, y) for c in range(img.shape[2])]
            )
    else:
        raise ValueError(f"Unsupported image shape: {img.shape}")


# Alias for backward compatibility and convenience
def sample_at(img, x, y, channel=None):
    """
    Alias for sample_at_bicubic() for backward compatibility.

    Note: Use sample_at_bicubic() for explicit algorithm specification.
    """
    return sample_at_bicubic(img, x, y, channel)


# Legacy alias
def bicubic_resize_gpu(src_gpu, target_h: int, target_w: int, dst_gpu=None):
    return bicubic_resize(src_gpu, target_h, target_w, dst_gpu)
