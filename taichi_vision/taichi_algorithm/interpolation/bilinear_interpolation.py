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
            y_src = (float(r) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (float(c) + 0.5) * (float(w_src) / float(w_dst)) - 0.5

            y0 = int(ti.floor(y_src))
            x0 = int(ti.floor(x_src))
            
            y0_cl = tm.clamp(y0, 0, h_src - 1)
            x0_cl = tm.clamp(x0, 0, w_src - 1)
            y1_cl = tm.clamp(y0 + 1, 0, h_src - 1)
            x1_cl = tm.clamp(x0 + 1, 0, w_src - 1)

            wy = y_src - float(y0)
            wx = x_src - float(x0)

            q00 = src[y0_cl, x0_cl]
            q01 = src[y0_cl, x1_cl]
            q10 = src[y1_cl, x0_cl]
            q11 = src[y1_cl, x1_cl]

            r1 = tm.mix(float(q00), float(q01), wx)
            r2 = tm.mix(float(q10), float(q11), wx)
            dst[r, c] = tm.mix(r1, r2, wy)

    @ti.kernel
    def _bilinear_resize_kernel_3d(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c, ch in ti.ndrange(h_dst, w_dst, dst.shape[2]):
            y_src = (float(r) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (float(c) + 0.5) * (float(w_src) / float(w_dst)) - 0.5

            y0 = int(ti.floor(y_src))
            x0 = int(ti.floor(x_src))
            
            y0_cl = tm.clamp(y0, 0, h_src - 1)
            x0_cl = tm.clamp(x0, 0, w_src - 1)
            y1_cl = tm.clamp(y0 + 1, 0, h_src - 1)
            x1_cl = tm.clamp(x0 + 1, 0, w_src - 1)

            wy = y_src - float(y0)
            wx = x_src - float(x0)

            q00 = src[y0_cl, x0_cl, ch]
            q01 = src[y0_cl, x1_cl, ch]
            q10 = src[y1_cl, x0_cl, ch]
            q11 = src[y1_cl, x1_cl, ch]

            r1 = tm.mix(float(q00), float(q01), wx)
            r2 = tm.mix(float(q10), float(q11), wx)
            dst[r, c, ch] = tm.mix(r1, r2, wy)

    @ti.kernel
    def _bilinear_resize_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            y_src = (float(r) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x_src = (float(c) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            y0 = int(ti.floor(y_src))
            x0 = int(ti.floor(x_src))
            y0_cl = tm.clamp(y0, 0, h_src - 1)
            x0_cl = tm.clamp(x0, 0, w_src - 1)
            y1_cl = tm.clamp(y0 + 1, 0, h_src - 1)
            x1_cl = tm.clamp(x0 + 1, 0, w_src - 1)
            wy = y_src - float(y0)
            wx = x_src - float(x0)
            q00 = src[y0_cl, x0_cl]
            q01 = src[y0_cl, x1_cl]
            q10 = src[y1_cl, x0_cl]
            q11 = src[y1_cl, x1_cl]
            r1 = tm.mix(q00, q01, wx)
            r2 = tm.mix(q10, q11, wx)
            dst[r, c] = tm.mix(r1, r2, wy)

    @ti.kernel
    def _bilinear_resize_offset_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(),
        h_src: int, w_src: int, h_dst: int, w_dst: int,
        offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            y0, x0 = int(ti.floor(y)), int(ti.floor(x))
            fy, fx = y - float(y0), x - float(x0)
            ya, yb = tm.clamp(y0, 0, h_src - 1), tm.clamp(y0 + 1, 0, h_src - 1)
            xa, xb = tm.clamp(x0, 0, w_src - 1), tm.clamp(x0 + 1, 0, w_src - 1)
            dst[r, c] = tm.mix(tm.mix(float(src[ya, xa]), float(src[ya, xb]), fx), tm.mix(float(src[yb, xa]), float(src[yb, xb]), fx), fy)

    @ti.kernel
    def _bilinear_resize_offset_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int, w_src: int, h_dst: int, w_dst: int,
        offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            y0, x0 = int(ti.floor(y)), int(ti.floor(x))
            fy, fx = y - float(y0), x - float(x0)
            ya, yb = tm.clamp(y0, 0, h_src - 1), tm.clamp(y0 + 1, 0, h_src - 1)
            xa, xb = tm.clamp(x0, 0, w_src - 1), tm.clamp(x0 + 1, 0, w_src - 1)
            dst[r, c] = tm.mix(tm.mix(src[ya, xa], src[ya, xb], fx), tm.mix(src[yb, xa], src[yb, xb], fx), fy)

    @ti.kernel
    def _bilinear_resize_batch_offset_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        offsets: ti.types.ndarray(dtype=ti.i32, ndim=2),
        h_src: ti.i32,
        w_src: ti.i32,
        h_dst: ti.i32,
        w_dst: ti.i32,
    ):
        """Resize a bounded batch of output tiles in one dispatch."""
        for batch, r, c in ti.ndrange(dst.shape[0], dst.shape[1], dst.shape[2]):
            gr = r + offsets[batch, 0]
            gc = c + offsets[batch, 1]
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            y0, x0 = int(ti.floor(y)), int(ti.floor(x))
            fy, fx = y - float(y0), x - float(x0)
            ya, yb = tm.clamp(y0, 0, h_src - 1), tm.clamp(y0 + 1, 0, h_src - 1)
            xa, xb = tm.clamp(x0, 0, w_src - 1), tm.clamp(x0 + 1, 0, w_src - 1)
            dst[batch, r, c] = tm.mix(
                tm.mix(src[ya, xa], src[ya, xb], fx),
                tm.mix(src[yb, xa], src[yb, xb], fx),
                fy,
            )

    @ti.kernel
    def _bilinear_resize_batch_offset_kernel_vec3(
        src: ti.types.ndarray(
            dtype=ti.types.vector(3, ti.f32), ndim=2
        ),
        dst: ti.types.ndarray(
            dtype=ti.types.vector(3, ti.f32), ndim=3
        ),
        offsets: ti.types.ndarray(dtype=ti.i32, ndim=2),
        h_src: ti.i32,
        w_src: ti.i32,
        h_dst: ti.i32,
        w_dst: ti.i32,
    ):
        """Vector3 variant of the batched offset resize graph."""
        for batch, r, c in ti.ndrange(dst.shape[0], dst.shape[1], dst.shape[2]):
            gr = r + offsets[batch, 0]
            gc = c + offsets[batch, 1]
            y = (float(gr) + 0.5) * (float(h_src) / float(h_dst)) - 0.5
            x = (float(gc) + 0.5) * (float(w_src) / float(w_dst)) - 0.5
            y0, x0 = int(ti.floor(y)), int(ti.floor(x))
            fy, fx = y - float(y0), x - float(x0)
            ya, yb = tm.clamp(y0, 0, h_src - 1), tm.clamp(y0 + 1, 0, h_src - 1)
            xa, xb = tm.clamp(x0, 0, w_src - 1), tm.clamp(x0 + 1, 0, w_src - 1)
            dst[batch, r, c] = tm.mix(
                tm.mix(src[ya, xa], src[ya, xb], fx),
                tm.mix(src[yb, xa], src[yb, xb], fx),
                fy,
            )


def bilinear_resize(src, target_h: int, target_w: int, dst=None, buffer_provider="pool"):
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
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.resize(src, (target_w, target_h), interpolation=taichi_aot.INTER_LINEAR, return_gpu=hasattr(src, "to_numpy"), dst=dst)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from ..common import get_temp_buffer, release_temp_buffer, ensure_taichi_field

    # Detect input type
    is_taichi_input = hasattr(src, "to_numpy")

    @ti_thread
    def _run_gpu_resize(src_data, h_dst, w_dst, dst_data=None):
        src_gpu, src_is_temp = ensure_taichi_field(src_data, dtype=ti.f32, buffer_provider=buffer_provider)
        h_src, w_src = src_gpu.shape[:2]

        is_3d = len(src_gpu.shape) == 3
        c_count = src_gpu.shape[2] if is_3d else 1

        # Determine output buffer
        if dst_data is None:
            out_shape = (h_dst, w_dst, c_count) if is_3d else (h_dst, w_dst)
            dst_gpu = get_temp_buffer(out_shape, ti.f32, buffer_provider)
        else:
            # If dst provided, ensure it's on GPU for kernel
            dst_gpu, _ = ensure_taichi_field(dst_data, dtype=ti.f32, buffer_provider=buffer_provider)

        # Run appropriate kernel
        if is_3d:
            _bilinear_resize_kernel_3d(src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)
        else:
            _bilinear_resize_kernel(src_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)

        # Cleanup temp
        if src_is_temp:
            release_temp_buffer(src_gpu)

        # Download if input was NumPy
        if not is_taichi_input:
            res = dst_gpu.to_numpy()
            release_temp_buffer(dst_gpu)
            if dst_data is not None:
                dst_data[:] = res
                return dst_data
            return res

        return dst_gpu

    return _run_gpu_resize(src, target_h, target_w, dst)


# Legacy alias for backward compatibility
def bilinear_resize_gpu(src_gpu, target_h: int, target_w: int, dst_gpu=None):
    """
    DEPRECATED: Use bilinear_resize() instead.
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
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from .. import common

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
