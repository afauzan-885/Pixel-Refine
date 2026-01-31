"""
Gaussian Blur - Taichi GPU
==========================
Separable Gaussian Blur implementation.
"""

import numpy as np
from . import oom_guard

try:
    import taichi as ti
    import taichi.math as tm
    from . import common
    from .taichi_worker import ti_thread

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

if TAICHI_AVAILABLE:

    @ti.kernel
    def _gaussian_blur_x_1ch(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        for y, x in ti.ndrange(h, w):
            sum_val = 0.0
            total_weight = 0.0

            # Center
            center_w = weights[0]
            sum_val += src[y, x] * center_w
            total_weight += center_w

            # Neighbors
            for k in range(1, radius + 1):
                w_k = weights[k]

                # Left
                x_left = x - k
                if x_left < 0:
                    x_left = (
                        -x_left
                    )  # Reflect 101 approx for small radius, or just clamp
                # Standard clamp is safest
                x_left = tm.clamp(x - k, 0, w - 1)

                sum_val += src[y, x_left] * w_k

                # Right
                x_right = tm.clamp(x + k, 0, w - 1)
                sum_val += src[y, x_right] * w_k

                total_weight += 2.0 * w_k

            dst[y, x] = sum_val / total_weight

    @ti.kernel
    def _gaussian_blur_x_3ch(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        for y, x in ti.ndrange(h, w):
            sum_val = tm.vec3(0.0)
            total_weight = 0.0

            # Center
            center_w = weights[0]
            val = tm.vec3(src[y, x, 0], src[y, x, 1], src[y, x, 2])
            sum_val += val * center_w
            total_weight += center_w

            # Neighbors
            for k in range(1, radius + 1):
                w_k = weights[k]

                # Left
                x_left = tm.clamp(x - k, 0, w - 1)
                val = tm.vec3(src[y, x_left, 0], src[y, x_left, 1], src[y, x_left, 2])
                sum_val += val * w_k

                # Right
                x_right = tm.clamp(x + k, 0, w - 1)
                val = tm.vec3(
                    src[y, x_right, 0], src[y, x_right, 1], src[y, x_right, 2]
                )
                sum_val += val * w_k

                total_weight += 2.0 * w_k

            res = sum_val / total_weight
            dst[y, x, 0] = res[0]
            dst[y, x, 1] = res[1]
            dst[y, x, 2] = res[2]

    @ti.kernel
    def _gaussian_blur_y_1ch(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        for y, x in ti.ndrange(h, w):
            sum_val = 0.0
            total_weight = 0.0

            # Center
            center_w = weights[0]
            sum_val += src[y, x] * center_w
            total_weight += center_w

            # Neighbors
            for k in range(1, radius + 1):
                w_k = weights[k]

                # Up
                y_up = y - k
                if y_up < 0:
                    y_up = 0
                sum_val += src[y_up, x] * w_k

                # Down
                y_down = y + k
                if y_down >= h:
                    y_down = h - 1
                sum_val += src[y_down, x] * w_k

                total_weight += 2.0 * w_k

            dst[y, x] = sum_val / total_weight

    @ti.kernel
    def _gaussian_blur_y_3ch(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        for y, x in ti.ndrange(h, w):
            sum_val = tm.vec3(0.0)
            total_weight = 0.0

            # Center
            center_w = weights[0]
            val = tm.vec3(src[y, x, 0], src[y, x, 1], src[y, x, 2])
            sum_val += val * center_w
            total_weight += center_w

            # Neighbors
            for k in range(1, radius + 1):
                w_k = weights[k]

                # Up
                y_up = tm.clamp(y - k, 0, h - 1)
                val = tm.vec3(src[y_up, x, 0], src[y_up, x, 1], src[y_up, x, 2])
                sum_val += val * w_k

                # Down
                y_down = tm.clamp(y + k, 0, h - 1)
                val = tm.vec3(src[y_down, x, 0], src[y_down, x, 1], src[y_down, x, 2])
                sum_val += val * w_k

                total_weight += 2.0 * w_k

            res = sum_val / total_weight
            dst[y, x, 0] = res[0]
            dst[y, x, 1] = res[1]
            dst[y, x, 2] = res[2]


def compute_gaussian_weights(sigma, radius):
    """Compute 1D Gaussian kernel weights."""
    weights = []
    total = 0.0
    # Include center 0 and positive side
    for i in range(radius + 1):
        w = np.exp(-(i * i) / (2 * sigma * sigma))
        weights.append(w)
        if i == 0:
            total += w
        else:
            total += 2 * w

    # Normalize
    weights = np.array(weights) / total
    return weights


@ti_thread
def gaussian_blur(
    src,
    dst=None,
    sigma=1.0,
    kernel_size=None,
    buffer_provider="pool",
    enable_tiling=True,
):
    """
    Apply Gaussian blur.

    Args:
        src: Input image (numpy or Taichi field).
        dst: Optional output buffer.
        sigma: Gaussian sigma.
        kernel_size: Optional kernel size (default: 2*ceil(3*sigma)+1).
        buffer_provider: 'pool' or None.
        enable_tiling: Auto-tile large inputs.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # --- OpenCV Parity Logic ---
    # If sigma is 0 or negative, it must be calculated from kernel_size
    # If kernel_size is 0 or None, it must be calculated from sigma

    if sigma <= 0 and kernel_size is not None:
        # sigma = 0.3*((ksize-1)*0.5 - 1) + 0.8
        sigma = 0.3 * ((kernel_size - 1) * 0.5 - 1) + 0.8
        if sigma <= 0:
            sigma = 1.0  # Fallback

    if kernel_size is None or kernel_size <= 0:
        # radius = ceil(3*sigma) is our convention,
        # OpenCV uses a slightly different heuristic but this is close.
        radius = int(np.ceil(3 * sigma))
        kernel_size = 2 * radius + 1
    else:
        radius = kernel_size // 2

    if radius < 1:
        # No blur needed
        if dst is not None:
            if hasattr(src, "to_numpy") and hasattr(dst, "to_numpy"):
                common._copy_field_lowlevel(src, dst)
            else:
                dst[:] = src
        return src

    h, w = src.shape[:2]

    # Setup buffers
    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    # Determine channels
    channels = 1
    if len(src_gpu.shape) == 3:
        channels = src_gpu.shape[2]

    shape = (h, w, channels) if channels > 1 else (h, w)

    # Needs intermediate buffer for separable convolution
    temp_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)

    if dst is not None:
        dst_gpu = dst
    else:
        dst_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)

    # Compute weights
    weights_np = compute_gaussian_weights(sigma, radius)
    weights_gpu = ti.ndarray(dtype=ti.f32, shape=(radius + 1,))
    weights_gpu.from_numpy(weights_np.astype(np.float32))

    # Run passes
    # Run passes
    # Optimize: Use FP16 for intermediate buffer to save bandwidth?
    # Taichi casting is automatic.
    inter_dtype = ti.f16  # Force FP16

    # Needs intermediate buffer for separable convolution
    # Re-allocate temp with f16 if we want, but 'temp_gpu' was already alloc above as f32?
    # View file checks: 'temp_gpu = common.get_temp_buffer...'.
    # Logic in lines 265... is before this block.
    # I need to modify the allocation of temp_gpu.

    # Wait, 'temp_gpu' is allocated at line 265.
    # I should change that line. But I can't reach it easily here.
    # If I just release temp_gpu and re-alloc?
    common.release_temp_buffer(temp_gpu)
    temp_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)

    # Check if we can use f16 (some backends might not support storage well, but logic is fine)
    # Actually, for high quality, let's stick to f32 unless user allows.
    # But we can try to optimize the kernel loops first.

    if channels == 1:
        _gaussian_blur_x_1ch(src_gpu, temp_gpu, h, w, weights_gpu, radius)
        _gaussian_blur_y_1ch(temp_gpu, dst_gpu, h, w, weights_gpu, radius)
    else:
        # 3ch not vectorized yet (less critical for alignment which uses Gray)
        _gaussian_blur_x_3ch(src_gpu, temp_gpu, h, w, weights_gpu, radius)
        _gaussian_blur_y_3ch(temp_gpu, dst_gpu, h, w, weights_gpu, radius)

    # Cleanup intermediate
    common.release_temp_buffer(temp_gpu)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(
        dst_gpu, src_is_temp and dst is None
    )  # src_is_temp roughly implies input was numpy
