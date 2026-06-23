"""
Common Utilities for Taichi Algorithms
======================================
Shared functions for buffer management, type checking, and common operations.
"""

import numpy as np
import threading
import math

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

if not TAICHI_AVAILABLE:
    ti_thread = lambda f: f  # No-op in case of no Taichi
else:
    from .taichi_worker import ti_thread

AOT_MODE = os.environ.get("AOT_MODE", "1") == "1"
_AOT_ENGINE = None


def _get_aot():
    global _AOT_ENGINE
    if _AOT_ENGINE is None:
        try:
            from . import taichi_aot

            _AOT_ENGINE = taichi_aot
        except (ImportError, ValueError):
            try:
                import taichi_library.taichi_aot as taichi_aot

                _AOT_ENGINE = taichi_aot
            except ImportError:
                pass
    return _AOT_ENGINE


if TAICHI_AVAILABLE:

    # --- Interpolation Utilities ---
    @ti.func
    def reflect_idx(idx: int, size: int) -> int:
        """OpenCV BORDER_REFLECT_101 implementation."""
        res = idx
        if res < 0:
            res = -res
        if res >= size:
            res = 2 * (size - 1) - res
        return tm.clamp(res, 0, size - 1)

    @ti.func
    def quantize_subpixel(t: float) -> ti.f32:
        """OpenCV-compatible coordinate quantization (32 sub-pixel positions)."""
        return ti.floor(t * 32.0 + 0.5) / 32.0

    @ti.func
    def cubic_hermite_weights(t: float) -> ti.types.vector(4, ti.f32):
        """OpenCV-compatible Bicubic Weights (Catmull-Rom with a=-0.75 for f32)."""
        # t is assumed to be in [0, 1)
        w = ti.Vector([0.0, 0.0, 0.0, 0.0])
        a = -0.75

        # d = distance to neighbor
        # Neighbors are at index: -1, 0, 1, 2
        # Distances: t+1, t, 1-t, 2-t

        d = t
        # d0 = t+1 (range [1, 2])
        x = d + 1.0
        w[0] = a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a
        # d1 = t (range [0, 1])
        x = d
        w[1] = (a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0
        # d2 = 1-t (range [0, 1])
        x = 1.0 - d
        w[2] = (a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0
        # d3 = 2-t (range [1, 2])
        x = 2.0 - d
        w[3] = a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a

        # Explicit normalization to reach 1e-7+ precision
        # Even though mathematically they sum to 1, float precision can introduce tiny drifts.
        s = w[0] + w[1] + w[2] + w[3]
        return w / s

    @ti.func
    def reflect_idx_raw(idx: int, size: int) -> int:
        """OpenCV BORDER_REFLECT implementation (fedcba|abcdefgh|hgfedcb)."""
        res = idx
        if res < 0:
            res = -res - 1
        if res >= size:
            res = 2 * size - 1 - res
        return tm.clamp(res, 0, size - 1)

    @ti.func
    def bilinear_at(
        img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1
    ) -> float:
        """Bilinear interpolation with BORDER_REFLECT_101."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        ix0 = reflect_idx(ix, ww)
        iy0 = reflect_idx(iy, hh)
        ix1 = reflect_idx(ix + 1, ww)
        iy1 = reflect_idx(iy + 1, hh)

        v00 = img[iy0, ix0]
        v01 = img[iy0, ix1]
        v10 = img[iy1, ix0]
        v11 = img[iy1, ix1]

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx
        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def bilinear_at_vec3(
        img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1
    ) -> ti.types.vector(3, ti.f32):
        """Bilinear interpolation for vector(3, f32) fields with BORDER_REFLECT_101."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        ix0 = reflect_idx(ix, ww)
        iy0 = reflect_idx(iy, hh)
        ix1 = reflect_idx(ix + 1, ww)
        iy1 = reflect_idx(iy + 1, hh)

        v00 = img[iy0, ix0]
        v01 = img[iy0, ix1]
        v10 = img[iy1, ix0]
        v11 = img[iy1, ix1]

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx
        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def bicubic_at(
        img: ti.types.ndarray(), x: float, y: float, h: int = -1, w: int = -1
    ) -> float:
        """Bicubic interpolation with BORDER_REFLECT_101 and a=-0.75."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        wx = cubic_hermite_weights(fx)
        wy = cubic_hermite_weights(fy)

        res = 0.0
        for j in ti.static(range(4)):
            row_sum = 0.0
            row_iy = reflect_idx(iy - 1 + j, hh)
            for i in ti.static(range(4)):
                row_sum += img[row_iy, reflect_idx(ix - 1 + i, ww)] * wx[i]
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
        img: ti.types.ndarray(),
        x: float,
        y: float,
        h: int = -1,
        w: int = -1,
        c: int = 0,
    ) -> float:
        """Bilinear interpolation for 3ch with BORDER_REFLECT_101."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        ix0 = reflect_idx(ix, ww)
        iy0 = reflect_idx(iy, hh)
        ix1 = reflect_idx(ix + 1, ww)
        iy1 = reflect_idx(iy + 1, hh)

        v00 = float(img[iy0, ix0, c])
        v01 = float(img[iy0, ix1, c])
        v10 = float(img[iy1, ix0, c])
        v11 = float(img[iy1, ix1, c])

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx
        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def bicubic_at_channel(
        img: ti.types.ndarray(),
        x: float,
        y: float,
        h: int = -1,
        w: int = -1,
        c: int = 0,
    ) -> float:
        """Bicubic interpolation for 3ch with BORDER_REFLECT_101 and a=-0.75."""
        hh, ww = h, w
        if ti.static(isinstance(h, int) and h == -1):
            hh, ww = img.shape[0], img.shape[1]
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        wx = cubic_hermite_weights(fx)
        wy = cubic_hermite_weights(fy)

        res = 0.0
        for j in ti.static(range(4)):
            row_sum = 0.0
            row_iy = reflect_idx(iy - 1 + j, hh)
            for i in ti.static(range(4)):
                row_sum += img[row_iy, reflect_idx(ix - 1 + i, ww), c] * wx[i]
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
            dst[I] = src[I][channel]

    @ti.kernel
    def _insert_channel_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), channel: int
    ):
        for I in ti.grouped(src):
            dst[I][channel] = src[I]

    @ti.kernel
    def _absdiff_kernel(
        src1: ti.types.ndarray(), src2: ti.types.ndarray(), dst: ti.types.ndarray()
    ):
        for I in ti.grouped(src1):
            dst[I] = ti.abs(src1[I] - src2[I])

    @ti.kernel
    def _cvt_color_rgb_to_gray_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in dst:
            r = ti.cast(src[i, j][0], ti.f32)
            g = ti.cast(src[i, j][1], ti.f32)
            b = ti.cast(src[i, j][2], ti.f32)
            # OpenCV formula: Y = 0.299*R + 0.587*G + 0.114*B
            dst[i, j] = 0.299 * r + 0.587 * g + 0.114 * b

    @ti.kernel
    def _cvt_color_rgb_to_gray_i32_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray()
    ):
        for i, j in dst:
            r = ti.cast(src[i, j][0], ti.i32)
            g = ti.cast(src[i, j][1], ti.i32)
            b = ti.cast(src[i, j][2], ti.i32)
            # Integer Approximation: (306*R + 601*G + 117*B) >> 10
            # This is bit-perfect with common integer CV implementations
            dst[i, j] = (306 * r + 601 * g + 117 * b) >> 10

    @ti.kernel
    def _cvt_color_bgr_to_gray_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in dst:
            b = src[i, j][0]
            g = src[i, j][1]
            r = src[i, j][2]
            # OpenCV formula: Y = 0.299*R + 0.587*G + 0.114*B
            dst[i, j] = 0.299 * r + 0.587 * g + 0.114 * b

    @ti.kernel
    def _cvt_color_gray_to_rgb_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for i, j in src:
            val = src[i, j]
            dst[i, j][0] = val
            dst[i, j][1] = val
            dst[i, j][2] = val

    @ti.kernel
    def _generate_hanning_window_2d_kernel(
        dst: ti.types.ndarray(), H: int, W: int, exclude_boundary: int
    ):
        for i, j in dst:
            wy = 1.0
            if H > 1:
                if exclude_boundary == 1:
                    wy = 0.5 - 0.5 * ti.cos(
                        2.0 * 3.141592653589793 * float(i + 1) / float(H + 1)
                    )
                else:
                    wy = 0.5 - 0.5 * ti.cos(
                        2.0 * 3.141592653589793 * float(i) / float(H - 1)
                    )
            wx = 1.0
            if W > 1:
                if exclude_boundary == 1:
                    wx = 0.5 - 0.5 * ti.cos(
                        2.0 * 3.141592653589793 * float(j + 1) / float(W + 1)
                    )
                else:
                    wx = 0.5 - 0.5 * ti.cos(
                        2.0 * 3.141592653589793 * float(j) / float(W - 1)
                    )
            dst[i, j] = wy * wx

    @ti.kernel
    def _mean_division_kernel(
        sum_img: ti.types.ndarray(),
        sum_weight: ti.types.ndarray(),
        ref_img: ti.types.ndarray(),
        dst: ti.types.ndarray(),
    ):
        for i, j in sum_weight:
            w = sum_weight[i, j]
            if w > 1e-6:
                dst[i, j] = sum_img[i, j] / w
            else:
                dst[i, j] = ref_img[i, j]

    # =========================================================================
    # SfM MATH: Analytical 3x3 SVD, Essential Constraint, Hartley Normalization
    # =========================================================================

    @ti.func
    def _sym3_eigenvalues(
        S: ti.types.matrix(3, 3, ti.f32),
    ) -> ti.types.vector(3, ti.f32):
        """Analytical eigenvalues of 3x3 symmetric matrix (sorted descending)."""
        p1 = S[0, 1] * S[0, 1] + S[0, 2] * S[0, 2] + S[1, 2] * S[1, 2]
        e0 = S[0, 0]
        e1 = S[1, 1]
        e2 = S[2, 2]

        if p1 < 1e-14:
            ev0 = e0
            ev1 = e1
            ev2 = e2
            if ev0 < ev1:
                tmp = ev0
                ev0 = ev1
                ev1 = tmp
            if ev0 < ev2:
                tmp = ev0
                ev0 = ev2
                ev2 = tmp
            if ev1 < ev2:
                tmp = ev1
                ev1 = ev2
                ev2 = tmp
            return ti.Vector([ev0, ev1, ev2])

        q = (e0 + e1 + e2) / 3.0
        p2 = (e0 - q) * (e0 - q) + (e1 - q) * (e1 - q) + (e2 - q) * (e2 - q) + 2.0 * p1
        p = ti.sqrt(p2 / 6.0)

        b00 = (e0 - q) / p
        b11 = (e1 - q) / p
        b22 = (e2 - q) / p
        b01 = S[0, 1] / p
        b02 = S[0, 2] / p
        b12 = S[1, 2] / p

        det_B = (
            b00 * (b11 * b22 - b12 * b12)
            - b01 * (b01 * b22 - b02 * b12)
            + b02 * (b01 * b12 - b11 * b02)
        )
        r = det_B / 2.0
        r = ti.max(-1.0, ti.min(1.0, r))

        phi = ti.acos(r) / 3.0
        PI = 3.14159265358979323846
        eig0 = q + 2.0 * p * ti.cos(phi)
        eig2 = q + 2.0 * p * ti.cos(phi + (2.0 * PI / 3.0))
        eig1 = 3.0 * q - eig0 - eig2
        return ti.Vector([eig0, eig1, eig2])

    @ti.func
    def _sym3_eigenvector(
        S: ti.types.matrix(3, 3, ti.f32), eigenvalue: ti.f32
    ) -> ti.types.vector(3, ti.f32):
        """Compute eigenvector for given eigenvalue of 3x3 symmetric matrix via cross product."""
        r0 = ti.Vector([S[0, 0] - eigenvalue, S[0, 1], S[0, 2]])
        r1 = ti.Vector([S[0, 1], S[1, 1] - eigenvalue, S[1, 2]])
        r2 = ti.Vector([S[0, 2], S[1, 2], S[2, 2] - eigenvalue])

        c01 = r0.cross(r1)
        c02 = r0.cross(r2)
        c12 = r1.cross(r2)

        l01 = c01.norm_sqr()
        l02 = c02.norm_sqr()
        l12 = c12.norm_sqr()

        result = ti.Vector([0.0, 0.0, 1.0])
        max_l = l01
        if l02 > max_l:
            max_l = l02
        if l12 > max_l:
            max_l = l12

        if max_l > 1e-20:
            if max_l == l01:
                result = c01 / ti.sqrt(l01)
            elif max_l == l02:
                result = c02 / ti.sqrt(l02)
            else:
                result = c12 / ti.sqrt(l12)
        return result

    @ti.func
    def svd_3x3(A: ti.types.matrix(3, 3, ti.f32)):
        """
        Analytical SVD for 3x3 matrix via eigenvalue decomposition of A^T*A.
        Returns: (U, sigma, Vt) where A = U @ diag(sigma) @ Vt.
        """
        ATA = A.transpose() @ A

        eigenvalues = _sym3_eigenvalues(ATA)
        ev0 = ti.max(eigenvalues[0], 0.0)
        ev1 = ti.max(eigenvalues[1], 0.0)
        ev2 = ti.max(eigenvalues[2], 0.0)

        sigma0 = ti.sqrt(ev0)
        sigma1 = ti.sqrt(ev1)
        sigma2 = ti.sqrt(ev2)

        v0 = _sym3_eigenvector(ATA, eigenvalues[0])
        v1 = _sym3_eigenvector(ATA, eigenvalues[1])
        v2 = v0.cross(v1)
        v2_len = v2.norm()
        if v2_len > 1e-10:
            v2 = v2 / v2_len
        v1 = v2.cross(v0)
        v1_len = v1.norm()
        if v1_len > 1e-10:
            v1 = v1 / v1_len

        V = ti.Matrix.cols([v0, v1, v2])

        u0 = ti.Vector([1.0, 0.0, 0.0])
        u1 = ti.Vector([0.0, 1.0, 0.0])
        u2 = ti.Vector([0.0, 0.0, 1.0])
        if sigma0 > 1e-10:
            u0 = A @ v0 / sigma0
            u0_len = u0.norm()
            if u0_len > 1e-10:
                u0 = u0 / u0_len
        if sigma1 > 1e-10:
            u1 = A @ v1 / sigma1
            u1_len = u1.norm()
            if u1_len > 1e-10:
                u1 = u1 / u1_len
            u1 = u1 - (u0.dot(u1)) * u0
            u1_len = u1.norm()
            if u1_len > 1e-10:
                u1 = u1 / u1_len
        u2 = u0.cross(u1)
        u2_len = u2.norm()
        if u2_len > 1e-10:
            u2 = u2 / u2_len

        det_U = u0.dot(u1.cross(u2))
        if det_U < 0.0:
            u2 = -u2
            sigma2 = -sigma2

        U = ti.Matrix.cols([u0, u1, u2])
        sigma = ti.Vector([sigma0, sigma1, sigma2])
        Vt = V.transpose()
        return U, sigma, Vt

    @ti.func
    def enforce_essential(
        E: ti.types.matrix(3, 3, ti.f32),
    ) -> ti.types.matrix(3, 3, ti.f32):
        """Enforce essential matrix constraint: SVD -> force sigma = diag(1,1,0)."""
        U, sigma, Vt = svd_3x3(E)
        s_avg = (sigma[0] + sigma[1]) / 2.0
        S_new = ti.Matrix([[s_avg, 0.0, 0.0], [0.0, s_avg, 0.0], [0.0, 0.0, 0.0]])
        return U @ S_new @ Vt

    @ti.kernel
    def _hartley_normalize_kernel(
        pts: ti.types.ndarray(ti.f32, ndim=2),
        n_pts: int,
        T_out: ti.types.ndarray(ti.f32, ndim=2),
        pts_norm: ti.types.ndarray(ti.f32, ndim=2),
    ):
        """Hartley isotropic normalization: translate centroid to origin, scale avg distance to sqrt(2)."""
        cx = 0.0
        cy = 0.0
        for i in range(n_pts):
            cx += pts[i, 0]
            cy += pts[i, 1]
        cx /= float(n_pts)
        cy /= float(n_pts)

        avg_dist = 0.0
        for i in range(n_pts):
            dx = pts[i, 0] - cx
            dy = pts[i, 1] - cy
            avg_dist += ti.sqrt(dx * dx + dy * dy)
        avg_dist /= float(n_pts)
        s = 1.41421356 / (avg_dist + 1e-10)

        T_out[0, 0] = s
        T_out[0, 1] = 0.0
        T_out[0, 2] = -s * cx
        T_out[1, 0] = 0.0
        T_out[1, 1] = s
        T_out[1, 2] = -s * cy
        T_out[2, 0] = 0.0
        T_out[2, 1] = 0.0
        T_out[2, 2] = 1.0

        for i in range(n_pts):
            pts_norm[i, 0] = s * (pts[i, 0] - cx)
            pts_norm[i, 1] = s * (pts[i, 1] - cy)

    @ti.kernel
    def _denormalize_fundamental_kernel(
        F_norm: ti.types.ndarray(ti.f32, ndim=2),
        T1: ti.types.ndarray(ti.f32, ndim=2),
        T2: ti.types.ndarray(ti.f32, ndim=2),
        F_out: ti.types.ndarray(ti.f32, ndim=2),
    ):
        """Denormalize fundamental matrix: F = T2^T @ F_norm @ T1."""
        for i in range(3):
            for j in range(3):
                val = 0.0
                for k in ti.static(range(3)):
                    for l in ti.static(range(3)):
                        val += T2[k, i] * F_norm[k, l] * T1[l, j]
                F_out[i, j] = val


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
            return dst_field, True  # It's a temporary casted buffer
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
    AOT-Aware: Dispatches to AOT module if AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from taichi_library.taichi_aot.engine import TaichiGPUBuffer

            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)

            if len(img_v.shape) == 3 and img_v.shape[2] == 3:
                res_list = aot.split_3ch(img_v)
            else:
                c = img_v.shape[2] if len(img_v.shape) == 3 else 1
                res_list = []
                for i in range(c):
                    res_list.append(aot.extract_channel(img_v, i))

            if is_gpu:
                return tuple(res_list)
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
    AOT-Aware: Dispatches to AOT module if AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from taichi_library.taichi_aot.engine import TaichiGPUBuffer

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
                dst_buf = aot.engine.allocate(
                    (h, w, c), dtype=channels[0].dtype, is_vector=(c == 3)
                )
                for i, ch in enumerate(channels):
                    ch_v = ch if is_gpu else aot.upload(ch)
                    aot.insert_channel(ch_v, dst_buf, i)

            if is_gpu:
                return dst_buf
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
    AOT-Aware: Dispatches to AOT module if AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from taichi_library.taichi_aot.engine import TaichiGPUBuffer

            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)
            res_gpu = aot.extract_channel(img_v, ch)
            if is_gpu:
                return res_gpu
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
    AOT-Aware: Dispatches to AOT module if AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            from taichi_library.taichi_aot.engine import TaichiGPUBuffer

            is_gpu = isinstance(img, TaichiGPUBuffer)
            img_v = img if is_gpu else aot.upload(img)

            h, w = img_v.shape[0], img_v.shape[1]
            is_3d = len(img_v.shape) == 3
            dst_shape = (h, w, img_v.shape[2]) if is_3d else (h, w)
            dst_buf = aot.engine.allocate(dst_shape, dtype=img_v.dtype, is_vector=is_3d)
            aot.copy_field(img_v, dst_buf)

            if is_gpu:
                return dst_buf
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
    AOT-Aware: Dispatches to AOT module if AOT_MODE=1
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot and code in [COLOR_BGR2GRAY, COLOR_RGB2GRAY]:
            from taichi_library.taichi_aot.engine import TaichiGPUBuffer

            is_gpu = isinstance(src, TaichiGPUBuffer)
            src_v = src if is_gpu else aot.upload(src)
            res_gpu = aot.rgb2gray(src_v)
            if is_gpu:
                return res_gpu
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


@ti_thread
def hanning(shape, exclude_boundary=False, dtype=np.float32):
    """
    Generate 2D Hanning window directly on GPU.
    exclude_boundary: If True, behaves like np.hanning(M + 2)[1:-1]
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            return aot.hanning(shape, exclude_boundary, dtype)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = shape
    dst = get_temp_buffer((h, w), ti.f32)
    _generate_hanning_window_2d_kernel(dst, h, w, 1 if exclude_boundary else 0)
    return dst


@ti_thread
def mean_division(sum_img, sum_weight, ref_img, dst=None):
    """
    Perform final mean division and fallback on GPU.
    """
    if AOT_MODE:
        aot = _get_aot()
        if aot:
            return aot.mean_division(sum_img, sum_weight, ref_img, dst)

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_taichi_input = hasattr(sum_img, "to_numpy")

    sum_img_gpu, s_temp = ensure_taichi_field(sum_img, dtype=ti.f32)
    sum_weight_gpu, sw_temp = ensure_taichi_field(sum_weight, dtype=ti.f32)
    ref_img_gpu, r_temp = ensure_taichi_field(ref_img, dtype=ti.f32)

    if dst is None:
        dst_gpu = get_temp_buffer(sum_img_gpu.shape, ti.f32)
    else:
        dst_gpu, _ = ensure_taichi_field(dst, dtype=ti.f32)

    _mean_division_kernel(sum_img_gpu, sum_weight_gpu, ref_img_gpu, dst_gpu)

    if s_temp:
        release_temp_buffer(sum_img_gpu)
    if sw_temp:
        release_temp_buffer(sum_weight_gpu)
    if r_temp:
        release_temp_buffer(ref_img_gpu)

    if not is_taichi_input:
        res = dst_gpu.to_numpy()
        release_temp_buffer(dst_gpu)
        if dst is not None:
            dst[:] = res
            return dst
        return res

    return dst_gpu


# NumPy-like aliases for JIT/AOT consistency
hanning = hanning
divide = mean_division


# =========================================================================
# SfM Host Wrappers (NumPy fallbacks for algebraic solvers)
# =========================================================================


def svd_3x3_np(A):
    """SVD 3x3 via NumPy (Float64 precision). Returns (U, sigma, Vt)."""
    A64 = np.asarray(A, dtype=np.float64)
    U, S, Vt = np.linalg.svd(A64)
    return U.astype(np.float32), S.astype(np.float32), Vt.astype(np.float32)


def enforce_essential_np(E):
    """Enforce essential matrix constraint via NumPy SVD."""
    E64 = np.asarray(E, dtype=np.float64)
    U, S, Vt = np.linalg.svd(E64)
    s_avg = (S[0] + S[1]) / 2.0
    S_new = np.diag([s_avg, s_avg, 0.0])
    return (U @ S_new @ Vt).astype(np.float64)


def hartley_normalize(pts, n_pts=None):
    """
    Hartley isotropic normalization (NumPy).
    Translate centroid to origin, scale avg distance to sqrt(2).
    Returns: (T, pts_normalized) where T is the 3x3 transform matrix.
    """
    pts = np.ascontiguousarray(pts, dtype=np.float64)
    if n_pts is None:
        n_pts = len(pts)
    centroid = pts[:n_pts].mean(axis=0)
    diff = pts[:n_pts] - centroid
    avg_dist = np.mean(np.sqrt(np.sum(diff**2, axis=1)))
    s = math.sqrt(2.0) / (avg_dist + 1e-10)
    T = np.array(
        [
            [s, 0.0, -s * centroid[0]],
            [0.0, s, -s * centroid[1]],
            [0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    pts_h = np.hstack([pts[:n_pts], np.ones((n_pts, 1))])
    pts_norm = (T @ pts_h.T).T[:, :2]
    return T, np.ascontiguousarray(pts_norm, dtype=np.float64)


def denormalize_fundamental(F_norm, T1, T2):
    """Denormalize fundamental matrix: F = T2^T @ F_norm @ T1."""
    return (T2.T @ F_norm @ T1).astype(np.float64)


class SfMDataError(Exception):
    """Custom exception for SfM data validation errors with user-friendly hints."""

    def __init__(self, message, hint=None, field=None, repair_suggestion=None):
        self.hint = hint
        self.field = field
        self.repair_suggestion = repair_suggestion
        full_msg = f"[SfM Error] {message}"
        if hint:
            full_msg += f"\n  Hint: {hint}"
        if field:
            full_msg += f"\n  Field: {field}"
        if repair_suggestion:
            full_msg += f"\n  Suggestion: {repair_suggestion}"
        super().__init__(full_msg)


def ensure_contiguous_f32(data, name="data"):
    """Auto-repair: ensure array is contiguous float32. Handles int8/16/32, uint8/16, float64."""
    if data is None:
        raise SfMDataError(
            f"Input '{name}' is None",
            hint="Provide a valid numpy array",
            field=name,
            repair_suggestion="Pass a non-empty numpy array",
        )
    if not isinstance(data, np.ndarray):
        try:
            data = np.asarray(data)
        except Exception:
            raise SfMDataError(
                f"Cannot convert '{name}' to numpy array",
                hint=f"Got type: {type(data).__name__}",
                field=name,
            )
    if data.size == 0:
        raise SfMDataError(
            f"Input '{name}' is empty (size=0)",
            hint="Provide at least 1 element",
            field=name,
        )
    if np.any(np.isnan(data)):
        data = np.nan_to_num(data, nan=0.0)
    if np.any(np.isinf(data)):
        data = np.clip(data, -1e6, 1e6)
    data = np.ascontiguousarray(data, dtype=np.float32)
    return data


def ensure_contiguous_f64(data, name="data"):
    """Auto-repair: ensure array is contiguous float64."""
    if data is None:
        raise SfMDataError(
            f"Input '{name}' is None", hint="Provide a valid numpy array", field=name
        )
    if not isinstance(data, np.ndarray):
        try:
            data = np.asarray(data)
        except Exception:
            raise SfMDataError(
                f"Cannot convert '{name}' to numpy array",
                hint=f"Got type: {type(data).__name__}",
                field=name,
            )
    if data.size == 0:
        raise SfMDataError(f"Input '{name}' is empty (size=0)", field=name)
    if np.any(np.isnan(data)):
        data = np.nan_to_num(data, nan=0.0)
    if np.any(np.isinf(data)):
        data = np.clip(data, -1e10, 1e10)
    data = np.ascontiguousarray(data, dtype=np.float64)
    return data


def validate_point_correspondences(pts1, pts2, min_points=8, name="points"):
    """
    Validate and auto-repair point correspondences.
    Handles: wrong dtype, non-contiguous, 1D->2D reshape, mismatched lengths, NaN/Inf.
    """
    pts1 = ensure_contiguous_f32(pts1, f"{name}_1")
    pts2 = ensure_contiguous_f32(pts2, f"{name}_2")

    if pts1.ndim == 1:
        n = len(pts1) // 2
        if n >= min_points:
            pts1 = pts1.reshape(n, 2)
        else:
            raise SfMDataError(
                f"Cannot reshape {name}_1: 1D array with {len(pts1)} elements",
                hint=f"Expected at least {min_points*2} elements for {min_points} points",
                field=f"{name}_1",
            )
    if pts2.ndim == 1:
        n = len(pts2) // 2
        if n >= min_points:
            pts2 = pts2.reshape(n, 2)
        else:
            raise SfMDataError(
                f"Cannot reshape {name}_2: 1D array with {len(pts2)} elements",
                field=f"{name}_2",
            )

    if pts1.ndim != 2 or pts1.shape[1] != 2:
        raise SfMDataError(
            f"{name}_1 must be (N, 2), got shape {pts1.shape}",
            hint="Reshape to (N, 2) - each row is [x, y]",
            field=f"{name}_1",
        )
    if pts2.ndim != 2 or pts2.shape[1] != 2:
        raise SfMDataError(
            f"{name}_2 must be (N, 2), got shape {pts2.shape}", field=f"{name}_2"
        )

    if len(pts1) != len(pts2):
        min_len = min(len(pts1), len(pts2))
        pts1 = pts1[:min_len]
        pts2 = pts2[:min_len]

    if len(pts1) < min_points:
        raise SfMDataError(
            f"Need at least {min_points} points, got {len(pts1)}",
            hint=f"Provide more feature correspondences (current: {len(pts1)})",
            field=name,
            repair_suggestion=f"Need {min_points - len(pts1)} more points",
        )

    return pts1, pts2


def validate_intrinsic_matrix(K, name="K"):
    """Validate and auto-repair camera intrinsic matrix."""
    K = ensure_contiguous_f64(K, name)
    if K.shape == (9,):
        K = K.reshape(3, 3)
    if K.shape != (3, 3):
        raise SfMDataError(
            f"Camera intrinsic matrix must be 3x3, got {K.shape}",
            hint="Expected: [[fx, 0, cx], [0, fy, cy], [0, 0, 1]]",
            field=name,
        )
    if K[2, 2] == 0:
        raise SfMDataError(
            f"K[2,2] is zero - invalid intrinsic matrix",
            hint="K[2,2] should be 1.0 for standard cameras",
            field=name,
            repair_suggestion="Set K[2,2] = 1.0",
        )
    if K[0, 0] <= 0 or K[1, 1] <= 0:
        raise SfMDataError(
            f"Focal length must be positive: fx={K[0,0]}, fy={K[1,1]}",
            hint="Check your camera calibration parameters",
            field=name,
        )
    return K


def validate_essential_matrix(E, name="E"):
    """Validate and auto-repair essential matrix (enforce rank-2 constraint)."""
    E = ensure_contiguous_f64(E, name)
    if E.shape == (9,):
        E = E.reshape(3, 3)
    if E.shape != (3, 3):
        raise SfMDataError(
            f"Essential matrix must be 3x3, got {E.shape}",
            hint="Expected a 3x3 fundamental/essential matrix",
            field=name,
        )
    rank = np.linalg.matrix_rank(E, tol=1e-6)
    if rank > 2:
        E = enforce_essential_np(E)
    norm = np.linalg.norm(E)
    if norm < 1e-10:
        raise SfMDataError(
            f"Essential matrix is near-zero (norm={norm:.2e})",
            hint="The point correspondences may be degenerate",
            field=name,
            repair_suggestion="Check that points span at least 2 dimensions",
        )
    return E


def validate_rotation_matrix(R, name="R"):
    """Validate and auto-repair rotation matrix (enforce SO(3))."""
    R = ensure_contiguous_f64(R, name)
    if R.shape != (3, 3):
        raise SfMDataError(f"Rotation matrix must be 3x3, got {R.shape}", field=name)
    det = np.linalg.det(R)
    if abs(det) < 1e-6:
        raise SfMDataError(
            f"Rotation matrix is near-singular (det={det:.2e})",
            hint="The decomposition may have failed",
            field=name,
        )
    if det < 0:
        R = -R
    U, _, Vt = np.linalg.svd(R)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        R[:, -1] *= -1
    return R


def safe_sfm_call(func, *args, **kwargs):
    """
    Execute an SfM function with comprehensive error handling.
    Catches all errors, auto-repairs where possible, provides user-friendly messages.
    """
    try:
        return func(*args, **kwargs)
    except SfMDataError:
        raise
    except ValueError as e:
        msg = str(e)
        if "shape" in msg.lower() or "dimension" in msg.lower():
            raise SfMDataError(
                f"Data shape mismatch: {msg}",
                hint="Check that all input arrays have compatible shapes",
                repair_suggestion="Use np.ascontiguousarray() and verify ndim",
            ) from e
        raise SfMDataError(
            f"Value error: {msg}", hint="Check input data ranges and types"
        ) from e
    except np.linalg.LinAlgError as e:
        raise SfMDataError(
            f"Linear algebra failure: {e}",
            hint="Matrix may be singular or ill-conditioned",
            repair_suggestion="Add regularization or check for degenerate configurations",
        ) from e
    except MemoryError:
        raise SfMDataError(
            f"Out of memory",
            hint="Reduce input size or use smaller image resolution",
            repair_suggestion="Try downsampling images or reducing point count",
        )
    except Exception as e:
        raise SfMDataError(
            f"Unexpected error: {type(e).__name__}: {e}",
            hint="Check input data validity and try again",
        ) from e
