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
    from ..taichi_worker import ti_thread
except ImportError:
    pass

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
        """OpenCV-compatible Bicubic Weights (Catmull-Rom with a=-0.75)."""
        t = ti.abs(t)
        w = ti.Vector([0.0, 0.0, 0.0, 0.0])
        # W(x) = (a+2)|x|^3 - (a+3)|x|^2 + 1 for |x| <= 1
        # W(x) = a|x|^3 - 5a|x|^2 + 8a|x| - 4a for 1 < |x| < 2
        a = -0.75
        
        # We need weights for t-1, t, t+1, t+2 (relative to floor)
        # But actually for floor-1, floor, floor+1, floor+2 relative to sample point
        # Let d = x - floor(x). Points are at -1-d, -d, 1-d, 2-d relative to x.
        # |x-p| values: |d+1|, |d|, |1-d|, |2-d|
        
        d = t
        # p0: |d+1|
        x = d + 1.0
        w[0] = a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a
        # p1: |d|
        x = d
        w[1] = (a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0
        # p2: |1-d|
        x = 1.0 - d
        w[2] = (a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0
        # p3: |2-d|
        x = 2.0 - d
        w[3] = a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a
        
        return w

    @ti.kernel
    def _bicubic_resize_kernel_2d(
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

            w_x = cubic_hermite_weights(dx)
            w_y = cubic_hermite_weights(dy)

            val = 0.0
            for m in ti.static(range(-1, 3)):
                row_res = 0.0
                yy = tm.clamp(y_int + m, 0, h_src - 1)
                for n in ti.static(range(-1, 3)):
                    xx = tm.clamp(x_int + n, 0, w_src - 1)
                    row_res += src[yy, xx] * w_x[n + 1]
                val += row_res * w_y[m + 1]
            
            dst[r, c] = val

    @ti.kernel
    def _bicubic_resize_kernel_3d(
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

            w_x = cubic_hermite_weights(dx)
            w_y = cubic_hermite_weights(dy)

            for ch in ti.static(range(3)):
                val = 0.0
                for m in ti.static(range(-1, 3)):
                    row_res = 0.0
                    yy = tm.clamp(y_int + m, 0, h_src - 1)
                    for n in ti.static(range(-1, 3)):
                        xx = tm.clamp(x_int + n, 0, w_src - 1)
                        row_res += src[yy, xx, ch] * w_x[n + 1]
                    val += row_res * w_y[m + 1]
                dst[r, c, ch] = val

    @ti.kernel
    def _bicubic_resize_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
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
            w_x = cubic_hermite_weights(dx)
            w_y = cubic_hermite_weights(dy)
            val = ti.Vector([0.0, 0.0, 0.0])
            for m in ti.static(range(-1, 3)):
                row_res = ti.Vector([0.0, 0.0, 0.0])
                yy = tm.clamp(y_int + m, 0, h_src - 1)
                for n in ti.static(range(-1, 3)):
                    xx = tm.clamp(x_int + n, 0, w_src - 1)
                    row_res += src[yy, xx] * w_x[n + 1]
                val += row_res * w_y[m + 1]
            dst[r, c] = val

    @ti.kernel
    def _bicubic_resize_offset_kernel_2d(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), h_src: int, w_src: int,
        h_dst: int, w_dst: int, offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            xi, yi = int(ti.floor(x)), int(ti.floor(y))
            wx, wy = cubic_hermite_weights(x - xi), cubic_hermite_weights(y - yi)
            val = 0.0
            for j in ti.static(range(-1, 3)):
                row = 0.0
                yy = tm.clamp(yi + j, 0, h_src - 1)
                for i in ti.static(range(-1, 3)):
                    row += src[yy, tm.clamp(xi + i, 0, w_src - 1)] * wx[i + 1]
                val += row * wy[j + 1]
            dst[r, c] = val

    @ti.kernel
    def _bicubic_resize_offset_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int, w_src: int, h_dst: int, w_dst: int,
        offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            xi, yi = int(ti.floor(x)), int(ti.floor(y))
            wx, wy = cubic_hermite_weights(x - xi), cubic_hermite_weights(y - yi)
            val = ti.Vector([0.0, 0.0, 0.0])
            for j in ti.static(range(-1, 3)):
                row = ti.Vector([0.0, 0.0, 0.0])
                yy = tm.clamp(yi + j, 0, h_src - 1)
                for i in ti.static(range(-1, 3)):
                    row += src[yy, tm.clamp(xi + i, 0, w_src - 1)] * wx[i + 1]
                val += row * wy[j + 1]
            dst[r, c] = val

    @ti.kernel
    def _bicubic_sample_kernel_2d(
        src: ti.types.ndarray(),
        coords: ti.types.ndarray(),
        results: ti.types.ndarray(),
        n_samples: int,
        h_src: int,
        w_src: int,
    ):
        for i in range(n_samples):
            x_src = coords[i, 0]
            y_src = coords[i, 1]

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
            results[i] = val

    @ti.kernel
    def _bicubic_sample_kernel_3d(
        src: ti.types.ndarray(),
        coords: ti.types.ndarray(),
        results: ti.types.ndarray(),
        n_samples: int,
        h_src: int,
        w_src: int,
    ):
        for i in range(n_samples):
            x_src = coords[i, 0]
            y_src = coords[i, 1]

            x_int = int(ti.floor(x_src))
            y_int = int(ti.floor(y_src))
            dx = x_src - x_int
            dy = y_src - y_int

            for ch in ti.static(range(3)):
                col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])
                for m in range(-1, 3):
                    p = ti.Vector([0.0, 0.0, 0.0, 0.0])
                    y_idx = tm.clamp(y_int + m, 0, h_src - 1)
                    for n in range(-1, 3):
                        x_idx = tm.clamp(x_int + n, 0, w_src - 1)
                        p[n + 1] = src[y_idx, x_idx, ch]
                    col_results[m + 1] = cubic_hermite(p[0], p[1], p[2], p[3], dx)

                val = cubic_hermite(
                    col_results[0], col_results[1], col_results[2], col_results[3], dy
                )
                results[i, ch] = val

    @ti.kernel
    def _bicubic_sample_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        coords: ti.types.ndarray(),
        results: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=1),
        n_samples: int,
        h_src: int,
        w_src: int,
    ):
        for i in range(n_samples):
            x_src = coords[i, 0]
            y_src = coords[i, 1]
            x_int = int(ti.floor(x_src))
            y_int = int(ti.floor(y_src))
            dx = x_src - x_int
            dy = y_src - y_int
            col_results = ti.Matrix([[0.0, 0.0, 0.0] for _ in range(4)]) # 4x3 matrix
            for m in range(4):
                p = ti.Matrix([[0.0, 0.0, 0.0] for _ in range(4)])
                y_idx = tm.clamp(y_int + m - 1, 0, h_src - 1)
                for n in range(4):
                    x_idx = tm.clamp(x_int + n - 1, 0, w_src - 1)
                    p[n, 0] = src[y_idx, x_idx][0]
                    p[n, 1] = src[y_idx, x_idx][1]
                    p[n, 2] = src[y_idx, x_idx][2]
                
                # Manual hermite for vector
                vec_p0 = ti.Vector([p[0,0], p[0,1], p[0,2]])
                vec_p1 = ti.Vector([p[1,0], p[1,1], p[1,2]])
                vec_p2 = ti.Vector([p[2,0], p[2,1], p[2,2]])
                vec_p3 = ti.Vector([p[3,0], p[3,1], p[3,2]])
                
                res_m = cubic_hermite(vec_p0, vec_p1, vec_p2, vec_p3, dx)
                col_results[m, 0] = res_m[0]
                col_results[m, 1] = res_m[1]
                col_results[m, 2] = res_m[2]

            val = cubic_hermite(
                ti.Vector([col_results[0,0], col_results[0,1], col_results[0,2]]),
                ti.Vector([col_results[1,0], col_results[1,1], col_results[1,2]]),
                ti.Vector([col_results[2,0], col_results[2,1], col_results[2,2]]),
                ti.Vector([col_results[3,0], col_results[3,1], col_results[3,2]]),
                dy
            )
            results[i] = val


def bicubic_resize(
    src=None, 
    target_h: int = 0, 
    target_w: int = 0, 
    dst=None, 
    buffer_provider="pool",
    # === AOT RECORDING ARGUMENTS ===
    g=None,
    src_arg=None,
    dst_arg=None,
    h_src_arg=None,
    w_src_arg=None,
    h_dst_arg=None,
    w_dst_arg=None,
    is_rgb_aot=False,
):
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
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.resize(src, (target_w, target_h), interpolation=taichi_aot.INTER_CUBIC, return_gpu=hasattr(src, "to_numpy"), dst=dst)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from .. import common

    if g is not None:
        if is_rgb_aot:
            target = _bicubic_resize_kernel_vec3
        else:
            target = _bicubic_resize_kernel_2d
        g.dispatch(target, src_arg, dst_arg, h_src_arg, w_src_arg, h_dst_arg, w_dst_arg)
        return None

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
        if is_3d:
            _bicubic_resize_kernel_3d(src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)
        else:
            _bicubic_resize_kernel_2d(src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)

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

    from .. import common

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

if not TAICHI_AVAILABLE:
    def cubic_hermite(*args, **kwargs):
        raise ImportError("Taichi JIT is not available")
