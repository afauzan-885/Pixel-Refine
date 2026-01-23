"""
Common Utilities for Taichi Algorithms
======================================
Shared functions for buffer management, type checking, and common operations.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    from typing import Any

    ti: Any = None
    tm: Any = None

if TAICHI_AVAILABLE:

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
    def bilinear_at(img: ti.types.ndarray(), x: float, y: float) -> float:
        """Bilinear interpolation at fractional coordinates with edge clamping."""
        h, w = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))

        # Clamp to bounds
        ix0 = tm.clamp(ix, 0, w - 1)
        iy0 = tm.clamp(iy, 0, h - 1)
        ix1 = tm.clamp(ix + 1, 0, w - 1)
        iy1 = tm.clamp(iy + 1, 0, h - 1)

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
    def bicubic_at(img: ti.types.ndarray(), x: float, y: float) -> float:
        """Bicubic interpolation at fractional coordinates using Catmull-Rom spline."""
        h, w = img.shape[0], img.shape[1]
        # Boundary check - fallback to bilinear for edges
        res = 0.0
        if x < 1.0 or y < 1.0 or x >= float(w - 2) or y >= float(h - 2):
            res = bilinear_at(img, x, y)
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


class BufferCache:
    """
    Simple pool for re-using Taichi fields to avoid allocation overhead and OOM.
    Keyed by (shape, dtype).
    """

    def __init__(self):
        self._pool = {}  # Key: (shape, dtype) -> List[ti.ndarray]
        self._active_allocations = 0

    def get_buffer(self, shape, dtype):
        key = (tuple(shape), dtype)
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

        if key not in self._pool:
            self._pool[key] = []

        self._pool[key].append(buf)

    def clear(self):
        """Release all held buffers and reset pool."""
        self._pool.clear()
        self._active_allocations = 0


# Global pool instance
_GLOBAL_CACHE = BufferCache()


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


def release_temp_buffer(buf):
    """Return buffer to pool if applicable."""
    if buf is None:
        return
    # ENABLED POOLING
    _GLOBAL_CACHE.release_buffer(buf)


def cleanup_cache():
    """Clear the global buffer cache to free GPU memory."""
    _GLOBAL_CACHE.clear()


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

    if isinstance(arr, np.ndarray):
        if dtype is None:
            dtype = ti.f32  # Default
        if shape is None:
            shape = arr.shape

        field = get_temp_buffer(shape, dtype, buffer_provider)

        # Sanity check for pooled buffers (if pooling were enabled)
        if field.shape != shape:
            release_temp_buffer(field)
            field = ti.ndarray(dtype=dtype, shape=shape)

        # Ensure contiguous array for Taichi compatibility and dtype match
        # This prevents crashes when passing sliced arrays (e.g. img[:,:,0])
        arr_contiguous = np.ascontiguousarray(arr)
        if dtype == ti.f32 and arr_contiguous.dtype != np.float32:
            arr_contiguous = arr_contiguous.astype(np.float32)

        field.from_numpy(arr_contiguous)
        return field, True

    return arr, False


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
            field.to_numpy(out)
            return out
        return field.to_numpy()
    return field


def copy_field(src, dst):
    """Copy contents of src field/ndarray to dst."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _copy_kernel(src, dst)


def extract_channel(src, dst, channel):
    """Extract a specific channel from src (H,W,C) to dst (H,W)."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _extract_channel_kernel(src, dst, channel)


def insert_channel(src, dst, channel):
    """Insert dst (H,W) into src (H,W,C) at valid channel index."""
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _insert_channel_kernel(src, dst, channel)
