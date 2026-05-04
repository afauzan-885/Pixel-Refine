"""
Common Utilities for Taichi Algorithms
======================================
Shared functions for buffer management, type checking, and common operations.
"""

import numpy as np
import threading

try:
    import taichi as ti
    import taichi.math as tm
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE

except ImportError:
    TAICHI_AVAILABLE = False
    from typing import Any

    ti: Any = None
    tm: Any = None
    ti_thread = lambda f: f  # No-op in case of no Taichi

if TAICHI_AVAILABLE:
    import os
    AOT_MODE = os.environ.get("PIXEL_REFINE_AOT_MODE") == "1"
    _AOT_ENGINE = None

    def _get_aot():
        global _AOT_ENGINE
        if _AOT_ENGINE is None:
            try:
                from . import taichi_aot
                _AOT_ENGINE = taichi_aot
            except (ImportError, ValueError):
                try:
                    import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot as taichi_aot
                    _AOT_ENGINE = taichi_aot
                except ImportError:
                    pass
        return _AOT_ENGINE

    # --- Interpolation Utilities ---
    @ti.func
    def cubic_weight(x: float) -> float:
        """Catmull-Rom spline weight function."""
        x = ti.abs(x)
        res = 0.0
        if x <= 1.0:
            res = 1.5 * x * x * x - 2.5 * x * x + 1.0
        elif x < 2.0:
            res = -0.5 * x * x * x + 2.5 * x * x - 4.0 * x + 2.0
        return res

    @ti.func
    def bilinear_at(img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1) -> float:
        """Bilinear interpolation at fractional coordinates with edge clamping. AOT-compatible."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))

        # Clamp to bounds
        ix0 = tm.clamp(ix, 0, ww - 1)
        iy0 = tm.clamp(iy, 0, hh - 1)
        ix1 = tm.clamp(ix + 1, 0, ww - 1)
        iy1 = tm.clamp(iy + 1, 0, hh - 1)

        fx = x - float(ix)
        fy = y - float(iy)

        v00 = img[iy0, ix0]
        v01 = img[iy0, ix1]
        v10 = img[iy1, ix0]
        v11 = img[iy1, ix1]

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx
        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def bicubic_at(img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1) -> float:
        """Bicubic interpolation at fractional coordinates using Catmull-Rom spline. AOT-compatible."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        # Boundary check - fallback to bilinear for edges (requires 2-pixel margin for bicubic)
        res = 0.0
        if x < 1.0 or y < 1.0 or x >= float(ww - 2) or y >= float(hh - 2):
            res = bilinear_at(img, x, y, hh, ww)
        else:
            ix = int(ti.floor(x))
            iy = int(ti.floor(y))
            fx = x - float(ix)
            fy = y - float(iy)

            # Pre-compute weights
            wx = ti.Vector(
                [
                    cubic_weight(fx + 1.0),
                    cubic_weight(fx),
                    cubic_weight(1.0 - fx),
                    cubic_weight(2.0 - fx),
                ]
            )
            wy = ti.Vector(
                [
                    cubic_weight(fy + 1.0),
                    cubic_weight(fy),
                    cubic_weight(1.0 - fy),
                    cubic_weight(2.0 - fy),
                ]
            )

            # 4x4 interpolation
            for j in ti.static(range(4)):
                row_sum = 0.0
                row_iy = iy - 1 + j
                for i in ti.static(range(4)):
                    row_sum += img[row_iy, ix - 1 + i] * wx[i]
                res += row_sum * wy[j]
        return res

    @ti.func
    def sample_green_normalized(
        img: ti.types.ndarray(), u: float, v: float, h: int, w: int, bits: int
    ) -> float:
        """
        Sample the GREEN channel from a 3-channel image and normalize it.
        Supports on-the-fly normalization from uint16 or other bit depths.
        """
        val = bilinear_at_3ch(img, u, v, h, w, 1)  # Channel 1 is Green
        norm_factor = 1.0
        if bits > 0:
            norm_factor = float((1 << bits) - 1)
        return val / norm_factor

    @ti.func
    def bilinear_at_3ch(
        img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1, c: int = 0
    ) -> float:
        """Bilinear interpolation for a specific channel of a 3-channel image."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))

        # Clamp to bounds
        ix0 = tm.clamp(ix, 0, ww - 1)
        iy0 = tm.clamp(iy, 0, hh - 1)
        ix1 = tm.clamp(ix + 1, 0, ww - 1)
        iy1 = tm.clamp(iy + 1, 0, hh - 1)

        fx = x - float(ix)
        fy = y - float(iy)

        v00 = float(img[iy0, ix0, c])
        v01 = float(img[iy0, ix1, c])
        v10 = float(img[iy1, ix0, c])
        v11 = float(img[iy1, ix1, c])

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx
        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def bicubic_at_channel(
        img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1, c: int = 0
    ) -> float:
        """Bicubic interpolation at fractional coordinates for a specific channel. AOT-compatible."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        res = 0.0
        if x < 1.0 or y < 1.0 or x >= float(ww - 2) or y >= float(hh - 2):
            res = bilinear_at_3ch(img, x, y, hh, ww, c)
        else:
            ix = int(ti.floor(x))
            iy = int(ti.floor(y))
            fx = x - float(ix)
            fy = y - float(iy)

            # Pre-compute weights
            wx = ti.Vector(
                [
                    cubic_weight(fx + 1.0),
                    cubic_weight(fx),
                    cubic_weight(1.0 - fx),
                    cubic_weight(2.0 - fx),
                ]
            )
            wy = ti.Vector(
                [
                    cubic_weight(fy + 1.0),
                    cubic_weight(fy),
                    cubic_weight(1.0 - fy),
                    cubic_weight(2.0 - fy),
                ]
            )

            # 4x4 interpolation
            for j in ti.static(range(4)):
                row_sum = 0.0
                row_iy = iy - 1 + j
                for i in ti.static(range(4)):
                    row_sum += img[row_iy, ix - 1 + i, c] * wx[i]
                res += row_sum * wy[j]
        return res

    @ti.kernel
    def _copy_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for I in ti.grouped(src):
            dst[I] = src[I]

    @ti.kernel
    def _extract_channel_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), channel: int
    ):
        for I in ti.grouped(dst):
            dst[I] = src[I, channel]

    @ti.kernel
    def _insert_channel_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), channel: int
    ):
        for I in ti.grouped(src):
            dst[I, channel] = src[I]

    @ti.kernel
    def _absdiff_kernel(
        src1: ti.types.ndarray(), src2: ti.types.ndarray(), dst: ti.types.ndarray()
    ):
        for I in ti.grouped(src1):
            dst[I] = ti.abs(src1[I] - src2[I])

    @ti.kernel
    def _cvt_color_rgb_to_gray_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in dst:
            r = src[i, j, 0]
            g = src[i, j, 1]
            b = src[i, j, 2]
            # OpenCV formula: Y = 0.299*R + 0.587*G + 0.114*B
            dst[i, j] = 0.299 * r + 0.587 * g + 0.114 * b

    @ti.kernel
    def _cvt_color_bgr_to_gray_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in dst:
            b = src[i, j, 0]
            g = src[i, j, 1]
            r = src[i, j, 2]
            # OpenCV formula: Y = 0.299*R + 0.587*G + 0.114*B
            dst[i, j] = 0.299 * r + 0.587 * g + 0.114 * b

    @ti.kernel
    def _cvt_color_gray_to_rgb_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in src:
            val = src[i, j]
            dst[i, j, 0] = val
            dst[i, j, 1] = val
            dst[i, j, 2] = val


class BufferCache:
    """
    Simple pool for re-using Taichi fields to avoid allocation overhead and OOM.
    Keyed by (shape, dtype).
    """

    def __init__(self):
        self._pool = {}  # Key: (shape, dtype) -> List[ti.ndarray]
        self._active_allocations = 0
        self._lock = threading.Lock()

    def get_buffer(self, shape, dtype):
        key = (tuple(shape), dtype)
        with self._lock:
            if key not in self._pool:
                self._pool[key] = []

            if self._pool[key]:
                # Pop from pool
                return self._pool[key].pop()

            # Allocate new
            self._active_allocations += 1
        return ti.ndarray(dtype=dtype, shape=shape)

    def release_buffer(self, buf):
        if buf is None:
            return

        # Identify key
        shape = buf.shape
        dtype = buf.dtype
        key = (tuple(shape), dtype)

        with self._lock:
            if key not in self._pool:
                self._pool[key] = []

            self._pool[key].append(buf)

    def clear(self):
        """Release all held buffers and reset pool."""
        with self._lock:
            self._pool.clear()
            self._active_allocations = 0


# Global pool instance
_GLOBAL_CACHE = BufferCache()


@ti_thread
def get_temp_buffer(shape, dtype, buffer_provider=None):
    """
    Get a temporary Taichi field/ndarray, optionally from a buffer provider.

    Args:
        shape: Tuple of dimensions.
        dtype: Taichi data type (e.g., ti.f32).
        buffer_provider: Optional callable that returns a buffer.

    Returns:
        ti.ndarray or similar field.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # If buffer_provider is our cache, use it
    if buffer_provider == "pool":
        # ENABLED POOLING
        return _GLOBAL_CACHE.get_buffer(shape, dtype)

    if buffer_provider and buffer_provider != "pool":
        return buffer_provider(shape, dtype)

    # Default is allocation (safe but slow/leaky in loops)
    return ti.ndarray(dtype=dtype, shape=shape)


@ti_thread
def release_temp_buffer(buf):
    """Return buffer to pool if applicable."""
    if buf is None:
        return
    # ENABLED POOLING
    _GLOBAL_CACHE.release_buffer(buf)


def cleanup_cache():
    """Clear the global buffer cache to free GPU memory."""
    _GLOBAL_CACHE.clear()


@ti_thread
def ensure_taichi_field(arr, dtype=None, shape=None, buffer_provider=None):
    """
    Ensure the input is a Taichi field/ndarray.
    If numpy, uploads to a new GPU buffer (using provider if specified).

    Args:
        arr: Input array (numpy or taichi).
        dtype: Desired Taichi data type (if creating new).
        shape: Desired shape (if creating new).
        buffer_provider: 'pool' or callable.

    Returns:
        (field, is_created_temporarily)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Check if already a Taichi field (GPU buffer)
    if hasattr(arr, "shape") and not isinstance(arr, np.ndarray):
        # Check if dtype matches
        if dtype is not None and arr.dtype != dtype:
            # Type mismatch on GPU! Must cast.
            h_h, w_w = arr.shape[:2]
            is_gray = len(arr.shape) == 2
            shape_dst = (h_h, w_w) if is_gray else (h_h, w_w, 3)
            dst_field = get_temp_buffer(shape_dst, dtype, buffer_provider)
            # Use copy/cast kernel
            _copy_kernel(arr, dst_field)
            return dst_field, True # It's a temporary casted buffer
        return arr, False  # Already GPU and correct type (or no type requested)

    # Upload numpy to GPU
    arr_contiguous = np.ascontiguousarray(arr)

    # Mapping numpy dtypes to ti dtypes for better VRAM utilization
    actual_ti_dtype = dtype
    if actual_ti_dtype is None:
        if arr_contiguous.dtype == np.uint16:
            actual_ti_dtype = ti.u16
        elif arr_contiguous.dtype == np.uint8:
            actual_ti_dtype = ti.u8
        else:
            actual_ti_dtype = ti.f32

    # If we explicitly asked for f32 but have ints, cast them
    if actual_ti_dtype == ti.f32 and arr_contiguous.dtype != np.float32:
        arr_contiguous = arr_contiguous.astype(np.float32)
    elif actual_ti_dtype == ti.u16 and arr_contiguous.dtype != np.uint16:
        arr_contiguous = arr_contiguous.astype(np.uint16)

    # Use shape from arr if not provided
    if shape is None:
        shape = arr_contiguous.shape

    field = get_temp_buffer(shape, actual_ti_dtype, buffer_provider)
    field.from_numpy(arr_contiguous)
    return field, True


@ti_thread
def to_numpy_if_needed(field, was_numpy, out=None):
    """
    Convert back to numpy if the original input was numpy, or if explicitly requested.

    Args:
        field: Taichi field.
        was_numpy: Boolean, true if we should return numpy.
        out: Optional numpy array to write into.

    Returns:
        Numpy array or Taichi field.
    """
    if was_numpy:
        if out is not None:
            out[:] = field.to_numpy()
            return out
        return field.to_numpy()
    return field


@ti_thread
def _copy_field_lowlevel(src, dst):
    """Low-level copy (requires pre-allocated dst)."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _copy_kernel(src, dst)


# Public API wrapper for copy_field
def copy_field(src, dst):
    """
    Copy Taichi field from src to dst (in-place).

    Args:
        src: Source Taichi field
        dst: Destination Taichi field (must be pre-allocated with same shape)
    """
    _copy_field_lowlevel(src, dst)


@ti_thread
def _extract_channel_lowlevel(src, dst, channel):
    """Low-level extract (requires pre-allocated dst)."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _extract_channel_kernel(src, dst, channel)


@ti_thread
def _insert_channel_lowlevel(src, dst, channel):
    """Low-level insert (requires pre-allocated dst)."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _insert_channel_kernel(src, dst, channel)


# --- High-Level OpenCV-Compatible Channel Operations ---


@ti_thread
def split(img):
    """
    Split multi-channel image into tuple of single-channel images.
    AOT-Aware: Dispatches to AOT module if PIXEL_REFINE_AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import TaichiGPUBuffer
            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)
            
            if len(img_v.shape) == 3 and img_v.shape[2] == 3:
                res_list = aot.split_3ch(img_v)
            else:
                c = img_v.shape[2] if len(img_v.shape) == 3 else 1
                res_list = []
                for i in range(c):
                    res_list.append(aot.extract_channel(img_v, i))
            
            if is_gpu: return tuple(res_list)
            return tuple([r.to_numpy() for r in res_list])

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(img, "to_numpy")

    # Get shape
    if is_taichi_input:
        shape = img.shape
    else:
        shape = img.shape
    h, w = shape[:2]
    c = shape[2] if len(shape) == 3 else 1

    channels = []

    if c == 1:
        # Single channel short-circuit
        return (copy(img),)

    if is_taichi_input:
        # GPU workflow - all on GPU
        for ch_idx in range(c):
            ch_field = get_temp_buffer((h, w), ti.f32)
            _extract_channel_lowlevel(img, ch_field, ch_idx)
            channels.append(ch_field)
    else:
        # NumPy workflow - upload once, extract all, download
        img_gpu, img_is_temp = ensure_taichi_field(img, dtype=ti.f32)

        for ch_idx in range(c):
            ch_gpu = get_temp_buffer((h, w), ti.f32)
            _extract_channel_lowlevel(img_gpu, ch_gpu, ch_idx)
            ch_array = ch_gpu.to_numpy()
            release_temp_buffer(ch_gpu)
            channels.append(ch_array)

        if img_is_temp:
            release_temp_buffer(img_gpu)

    return tuple(channels)


@ti_thread
def merge(channels):
    """
    Merge separate channels into multi-channel image.
    AOT-Aware: Dispatches to AOT module if PIXEL_REFINE_AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import TaichiGPUBuffer
            is_gpu = isinstance(channels[0], TaichiGPUBuffer)
            h, w = channels[0].shape[0], channels[0].shape[1]
            c = len(channels)
            if c == 3:
                c0 = channels[0] if is_gpu else aot.upload(channels[0])
                c1 = channels[1] if is_gpu else aot.upload(channels[1])
                c2 = channels[2] if is_gpu else aot.upload(channels[2])
                dst_buf = aot.merge_3ch(c0, c1, c2)
            else:
                # Fallback for other channel counts
                dst_buf = aot.engine.allocate((h, w, c), dtype=channels[0].dtype, is_vector=(c==3))
                for i, ch in enumerate(channels):
                    ch_v = ch if is_gpu else aot.upload(ch)
                    aot.insert_channel(ch_v, dst_buf, i)
            
            if is_gpu: return dst_buf
            return dst_buf.to_numpy()

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    if not channels:
        raise ValueError("channels list cannot be empty")

    if len(channels) == 1:
        # Single channel short-circuit
        return copy(channels[0])

    # Detect input type from first channel
    first_ch = channels[0]
    is_taichi_input = hasattr(first_ch, "to_numpy")

    # Get shape
    shape_2d = first_ch.shape[:2]
    h, w = shape_2d
    num_channels = len(channels)

    # Validate shapes
    for i, ch in enumerate(channels):
        if ch.shape[:2] != shape_2d:
            raise ValueError(
                f"Channel {i} has shape {ch.shape[:2]}, expected {shape_2d}"
            )

    # Create output
    if is_taichi_input:
        # GPU workflow
        merged = ti.ndarray(dtype=ti.f32, shape=(h, w, num_channels))
        for ch_idx, ch_field in enumerate(channels):
            _insert_channel_lowlevel(ch_field, merged, ch_idx)
        return merged
    else:
        # NumPy workflow
        merged_np = np.zeros((h, w, num_channels), dtype=np.float32)
        merged_gpu = ti.ndarray(dtype=ti.f32, shape=(h, w, num_channels))

        for ch_idx, ch_array in enumerate(channels):
            ch_gpu, _ = ensure_taichi_field(ch_array, dtype=ti.f32)
            _insert_channel_lowlevel(ch_gpu, merged_gpu, ch_idx)

        merged_np = merged_gpu.to_numpy()
        return merged_np


@ti_thread
def extract_channel(img, ch):
    """
    Extract single channel from multi-channel image.
    AOT-Aware: Dispatches to AOT module if PIXEL_REFINE_AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import TaichiGPUBuffer
            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)
            res_gpu = aot.extract_channel(img_v, ch)
            if is_gpu: return res_gpu
            res_np = res_gpu.to_numpy()
            return res_np

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(img, "to_numpy")

    shape = img.shape
    h, w = shape[:2]
    c = shape[2] if len(shape) == 3 else 1

    if ch >= c:
        raise ValueError(
            f"Channel index {ch} out of bounds for image with {c} channels"
        )

    if c == 1 and ch == 0:
        return copy(img)

    if is_taichi_input:
        # GPU workflow
        ch_field = get_temp_buffer((h, w), ti.f32)
        _extract_channel_lowlevel(img, ch_field, ch)
        return ch_field
    else:
        # NumPy workflow
        img_gpu, img_is_temp = ensure_taichi_field(img, dtype=ti.f32)
        ch_gpu = get_temp_buffer((h, w), ti.f32)
        _extract_channel_lowlevel(img_gpu, ch_gpu, ch)
        res = ch_gpu.to_numpy()
        release_temp_buffer(ch_gpu)
        if img_is_temp:
            release_temp_buffer(img_gpu)
        return res


@ti_thread
def insert_channel(src, dst, ch):
    """
    Insert single channel into multi-channel image (in-place).

    OpenCV-compatible: Same as cv2.insertChannel()

    **Full GPU Pipeline Support:**
    - Works with both NumPy and Taichi field inputs
    - Modifies dst in-place

    Args:
        src: Single-channel image (H, W) - NumPy or Taichi field
        dst: Multi-channel image (H, W, C) - modified in-place
        ch: Channel index (0, 1, 2, ...)

    Example:
        >>> # NumPy workflow
        >>> ta.insert_channel(green_modified, rgb, ch=1)
        >>> # Same as: cv2.insertChannel(green_modified, rgb, 1)

        >>> # GPU workflow (in-place on GPU!)
        >>> ta.insert_channel(green_gpu, rgb_gpu, ch=1)
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input types
    is_src_taichi = hasattr(src, "to_numpy")
    is_dst_taichi = hasattr(dst, "to_numpy")

    shape_dst = dst.shape
    c_dst = shape_dst[2] if len(shape_dst) == 3 else 1

    if ch >= c_dst:
        raise ValueError(
            f"Channel index {ch} out of bounds for destination with {c_dst} channels"
        )

    if c_dst == 1 and ch == 0:
        # Simple copy/assignment for single channel
        if is_dst_taichi:
            _copy_field_lowlevel(src, dst)
        else:
            dst[:] = src
        return

    if is_src_taichi and is_dst_taichi:
        # Both on GPU - direct operation
        _insert_channel_lowlevel(src, dst, ch)
    elif not is_src_taichi and not is_dst_taichi:
        # Both NumPy - need GPU round-trip
        src_gpu, _ = ensure_taichi_field(src, dtype=ti.f32)
        dst_gpu, _ = ensure_taichi_field(dst, dtype=ti.f32)
        _insert_channel_lowlevel(src_gpu, dst_gpu, ch)
        # Copy back to NumPy
        dst[:] = dst_gpu.to_numpy()
    else:
        raise ValueError(
            "src and dst must be the same type (both NumPy or both Taichi)"
        )


@ti_thread
def copy(img):
    """
    Copy image (auto-allocates output).
    AOT-Aware: Dispatches to AOT module if PIXEL_REFINE_AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import TaichiGPUBuffer
            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)
            
            h, w = img_v.shape[0], img_v.shape[1]
            is_3d = len(img_v.shape) == 3
            dst_shape = (h, w, img_v.shape[2]) if is_3d else (h, w)
            dst_buf = aot.engine.allocate(dst_shape, dtype=img_v.dtype, is_vector=is_3d)
            aot.copy_field(img_v, dst_buf)
            
            if is_gpu: return dst_buf
            res_np = dst_buf.to_numpy()
            return res_np

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Detect input type
    is_taichi_input = hasattr(img, "to_numpy")

    if is_taichi_input:
        # GPU workflow
        img_copy = ti.ndarray(dtype=ti.f32, shape=img.shape)
        _copy_field_lowlevel(img, img_copy)
        return img_copy
    else:
        # NumPy workflow - just use NumPy's copy
        return img.copy()


# --- Color Conversion Const ---
COLOR_BGR2GRAY = 6
COLOR_RGB2GRAY = 7
COLOR_GRAY2BGR = 8
COLOR_GRAY2RGB = 8  # Gray to BGR/RGB is identical for grayscale


@ti_thread
def cvtColor(src, code, dst=None):
    """
    Convert image color space.
    AOT-Aware: Dispatches to AOT module if PIXEL_REFINE_AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot and code in [COLOR_BGR2GRAY, COLOR_RGB2GRAY]:
            from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_aot.engine import TaichiGPUBuffer
            is_gpu = isinstance(src, TaichiGPUBuffer)
            src_v = src if is_gpu else aot.upload(src)
            res_gpu = aot.rgb2gray(src_v)
            if is_gpu: return res_gpu
            return res_gpu.to_numpy()

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_taichi_input = hasattr(src, "to_numpy")
    src_gpu, src_is_temp = ensure_taichi_field(src, dtype=ti.f32)
    h, w = src_gpu.shape[:2]

    # Handle output shape
    if code in [COLOR_BGR2GRAY, COLOR_RGB2GRAY]:
        out_shape = (h, w)
    else:
        out_shape = (h, w, 3)

    if dst is None:
        dst_gpu = get_temp_buffer(out_shape, ti.f32)
    else:
        # If dst provided, ensure it's on GPU for the kernel
        dst_gpu, _ = ensure_taichi_field(dst, dtype=ti.f32)

    if code == COLOR_BGR2GRAY:
        _cvt_color_bgr_to_gray_kernel(src_gpu, dst_gpu)
    elif code == COLOR_RGB2GRAY:
        _cvt_color_rgb_to_gray_kernel(src_gpu, dst_gpu)
    elif code in [COLOR_GRAY2BGR, COLOR_GRAY2RGB]:
        _cvt_color_gray_to_rgb_kernel(src_gpu, dst_gpu)
    else:
        raise ValueError(f"Unsupported color conversion code: {code}")

    # Cleanup temp src
    if src_is_temp:
        release_temp_buffer(src_gpu)

    # Handle back to numpy if needed
    if not is_taichi_input:
        res = dst_gpu.to_numpy()
        release_temp_buffer(dst_gpu)
        if dst is not None:
            dst[:] = res
            return dst
        return res

    return dst_gpu


@ti_thread
def absdiff(src1, src2, dst=None):
    """
    Calculate absolute difference between two images.
    OpenCV-compatible: Same as cv2.absdiff()
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_taichi_input = hasattr(src1, "to_numpy")
    src1_gpu, s1_temp = ensure_taichi_field(src1, dtype=ti.f32)
    src2_gpu, s2_temp = ensure_taichi_field(src2, dtype=ti.f32)

    if dst is None:
        dst_gpu = get_temp_buffer(src1_gpu.shape, ti.f32)
    else:
        dst_gpu, _ = ensure_taichi_field(dst, dtype=ti.f32)

    _absdiff_kernel(src1_gpu, src2_gpu, dst_gpu)

    if s1_temp:
        release_temp_buffer(src1_gpu)
    if s2_temp:
        release_temp_buffer(src2_gpu)

    if not is_taichi_input:
        res = dst_gpu.to_numpy()
        release_temp_buffer(dst_gpu)
        if dst is not None:
            dst[:] = res
            return dst
        return res

    return dst_gpu
