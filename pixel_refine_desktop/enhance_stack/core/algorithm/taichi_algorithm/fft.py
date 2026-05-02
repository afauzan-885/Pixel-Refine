"""
Efficient 2D FFT Implementation in Taichi
=========================================
Provides high-performance Fast Fourier Transform (FFT) and Inverse FFT (IFFT)
optimized for GPU execution using Radix-2 Cooley-Tukey algorithm.
"""

import numpy as np
import math
import os

try:
    import taichi as ti
    import taichi.math as tm
    from .taichi_worker import ti_thread, TAICHI_AVAILABLE
    from . import common
except ImportError:
    TAICHI_AVAILABLE = False


if TAICHI_AVAILABLE:

    @ti.func
    def reverse_bits(n: int, bits: int) -> int:
        res = 0
        for i in range(bits):
            res = (res << 1) | (n & 1)
            n >>= 1
        return res

    @ti.kernel
    def _bit_reverse_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), bits: int, is_col: int
    ):
        """Reorder elements according to bit-reversal permutation."""
        for i, j in ti.ndrange(src.shape[0], src.shape[1]):
            if is_col == 0:
                # Row-wise bit reversal
                target_j = reverse_bits(j, bits)
                dst[i, target_j] = src[i, j]
            else:
                # Column-wise bit reversal
                target_i = reverse_bits(i, bits)
                dst[target_i, j] = src[i, j]

    @ti.kernel
    def _fft_stage_kernel(
        data: ti.types.ndarray(), n: int, stage_len: int, is_inverse: int, is_col: int
    ):
        """Radix-2 Butterfly operation for a single FFT stage."""
        half_len = stage_len // 2
        angle_sign = 1.0 if is_inverse == 1 else -1.0

        for i, j in ti.ndrange(data.shape[0], data.shape[1]):
            idx = j if is_col == 0 else i
            if (idx % stage_len) < half_len:
                # Butterfly pair indices
                idx0 = idx
                idx1 = idx + half_len

                # Twiddle factor
                angle = 2.0 * math.pi * (idx % half_len) / stage_len
                w = tm.vec2(ti.cos(angle), angle_sign * ti.sin(angle))

                # Load values
                v0 = tm.vec2(0.0, 0.0)
                v1 = tm.vec2(0.0, 0.0)

                if is_col == 0:
                    v0 = data[i, idx0]
                    v1 = data[i, idx1]
                else:
                    v0 = data[idx0, j]
                    v1 = data[idx1, j]

                # Complex multiplication: (a+bi)(c+di) = (ac-bd) + (ad+bc)i
                v1_twiddled = tm.vec2(v1.x * w.x - v1.y * w.y, v1.x * w.y + v1.y * w.x)

                # Store results back
                if is_col == 0:
                    data[i, idx0] = v0 + v1_twiddled
                    data[i, idx1] = v0 - v1_twiddled
                else:
                    data[idx0, j] = v0 + v1_twiddled
                    data[idx1, j] = v0 - v1_twiddled

    @ti.kernel
    def _normalize_kernel(data: ti.types.ndarray(), scale: float):
        for I in ti.grouped(data):
            data[I] *= scale

    @ti.kernel
    def _real_to_complex_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), src_h: int, src_w: int
    ):
        for i, j in dst:
            if i < src_h and j < src_w:
                dst[i, j] = tm.vec2(src[i, j], 0.0)
            else:
                dst[i, j] = tm.vec2(0.0, 0.0)

    @ti.kernel
    def _complex_to_real_kernel(
        src: ti.types.ndarray(), dst: ti.types.ndarray(), dst_h: int, dst_w: int
    ):
        for i, j in src:
            if i < dst_h and j < dst_w:
                dst[i, j] = src[i, j].x

    @ti.kernel
    def _complex_to_mag_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
        for I in ti.grouped(dst):
            dst[I] = ti.sqrt(src[I].x ** 2 + src[I].y ** 2)

    @ti.kernel
    def _complex_mul_kernel(
        a: ti.types.ndarray(),
        b: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        conj_b: int,
    ):
        for I in ti.grouped(a):
            va = a[I]
            vb = b[I]
            if conj_b == 1:
                vb = tm.vec2(vb.x, -vb.y)

            # Complex multiplication
            dst[I] = tm.vec2(va.x * vb.x - va.y * vb.y, va.x * vb.y + va.y * vb.x)

    def _is_power_of_two(n):
        return (n > 0) and (n & (n - 1) == 0)

    def _next_power_of_two(n):
        return 1 << (n - 1).bit_length()

    @ti_thread
    def fft_1d_gpu(data_gpu, is_inverse=False, is_col=False):
        """Internal 1D FFT on rows or columns of a 2D field."""
        h, w = data_gpu.shape
        n = h if is_col else w
        if not _is_power_of_two(n):
            raise ValueError(f"FFT size must be power of two, got {n}")

        bits = int(math.log2(n))

        # 1. Bit Reversal
        temp_gpu = common.get_temp_buffer((h, w), ti.types.vector(2, ti.f32))
        _bit_reverse_kernel(data_gpu, temp_gpu, bits, 1 if is_col else 0)
        common.copy_field(temp_gpu, data_gpu)
        common.release_temp_buffer(temp_gpu)

        # 2. Butterfly Stages
        for stage in range(1, bits + 1):
            stage_len = 1 << stage
            _fft_stage_kernel(
                data_gpu, n, stage_len, 1 if is_inverse else 0, 1 if is_col else 0
            )

        if is_inverse:
            _normalize_kernel(data_gpu, 1.0 / n)

    @ti_thread
    def fft2(src):
        """
        Compute 2D Fast Fourier Transform.
        Supports both NumPy and Taichi ndarray.
        Automatically pads to power of two if needed.
        """
        # --- AOT ROUTING ---
        if os.environ.get("PIXEL_REFINE_AOT_MODE") == "1":
            from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
            return taichi_aot.fft2(src)
            
        src_gpu, is_temp = common.ensure_taichi_field(src, dtype=ti.f32)
        h, w = src_gpu.shape[:2]

        target_h = _next_power_of_two(h)
        target_w = _next_power_of_two(w)

        # Prepare complex field (vec2)
        complex_gpu = common.get_temp_buffer(
            (target_h, target_w), ti.types.vector(2, ti.f32)
        )
        _real_to_complex_kernel(src_gpu, complex_gpu, h, w)

        # Row-wise FFT
        fft_1d_gpu(complex_gpu, is_inverse=False, is_col=False)

        # Column-wise FFT
        fft_1d_gpu(complex_gpu, is_inverse=False, is_col=True)

        if is_temp:
            common.release_temp_buffer(src_gpu)

        return complex_gpu

    @ti_thread
    def ifft2(complex_gpu, target_shape=None):
        """
        Compute Inverse 2D Fast Fourier Transform.
        Returns a real (float32) field or NumPy array.
        """
        # --- AOT ROUTING ---
        if os.environ.get("PIXEL_REFINE_AOT_MODE") == "1":
            from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
            return taichi_aot.ifft2(complex_gpu, target_shape=target_shape)
            
        # Column-wise IFFT
        fft_1d_gpu(complex_gpu, is_inverse=True, is_col=True)

        # Row-wise IFFT
        fft_1d_gpu(complex_gpu, is_inverse=True, is_col=False)

        h, w = complex_gpu.shape
        out_h, out_w = target_shape if target_shape else (h, w)

        res_gpu = common.get_temp_buffer((out_h, out_w), ti.f32)
        _complex_to_real_kernel(complex_gpu, res_gpu, out_h, out_w)

        return res_gpu
