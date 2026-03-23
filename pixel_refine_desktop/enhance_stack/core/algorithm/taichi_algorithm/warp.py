"""
Warp - Taichi GPU Implementation
================================
GPU-accelerated image warping using optical flow.
Features:
- Bicubic Interpolation (Catmull-Rom) for high precision.
- Joint Bilateral Flow Refinement (Guidance) to align flow with reference edges.
- Reflection Padding.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common, bicubic_interpolation

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    common = None
    bicubic_interpolation = None

if TAICHI_AVAILABLE:
    # Precomputed 5x5 Gaussian weights (sigma=1.0)
    GAUSSIAN_SPATIAL_WEIGHTS = ti.Matrix(
        [
            [0.002969, 0.013306, 0.021938, 0.013306, 0.002969],
            [0.013306, 0.059634, 0.098320, 0.059634, 0.013306],
            [0.021938, 0.098320, 0.162103, 0.098320, 0.021938],
            [0.013306, 0.059634, 0.098320, 0.059634, 0.013306],
            [0.002969, 0.013306, 0.021938, 0.013306, 0.002969],
        ]
    )

    @ti.func
    def reflect_idx(idx: int, size: int) -> int:
        """Branchless BORDER_REFLECT_101 implementation."""
        res = idx
        if res < 0:
            res = -res
        if res >= size:
            res = 2 * (size - 1) - res
        return tm.clamp(res, 0, size - 1)

    @ti.func
    def sample_bicubic_fast(
        img: ti.template(), u: float, v: float
    ) -> float:
        """Optimized Bicubic sampling with precomputed weights."""
        h, w = img.shape[0], img.shape[1]
        x0 = int(ti.floor(u))
        y0 = int(ti.floor(v))
        dx = u - float(x0)
        dy = v - float(y0)

        wx = bicubic_interpolation.cubic_hermite_weights(dx)
        wy = bicubic_interpolation.cubic_hermite_weights(dy)

        res = 0.0
        for m in ti.static(range(4)):
            y_idx = reflect_idx(y0 + m - 1, h)
            row_res = 0.0
            for n in ti.static(range(4)):
                x_idx = reflect_idx(x0 + n - 1, w)
                row_res += img[y_idx, x_idx] * wx[n]
            res += row_res * wy[m]
        return res

    @ti.func
    def sample_bicubic_3ch_fast(
        img: ti.template(), u: float, v: float, c: int
    ) -> float:
        """Optimized 3-channel Bicubic sampling."""
        h, w = img.shape[0], img.shape[1]
        x0 = int(ti.floor(u))
        y0 = int(ti.floor(v))
        dx = u - float(x0)
        dy = v - float(y0)

        wx = bicubic_interpolation.cubic_hermite_weights(dx)
        wy = bicubic_interpolation.cubic_hermite_weights(dy)

        res = 0.0
        for m in ti.static(range(4)):
            y_idx = reflect_idx(y0 + m - 1, h)
            row_res = 0.0
            for n in ti.static(range(4)):
                x_idx = reflect_idx(x0 + n - 1, w)
                row_res += img[y_idx, x_idx, c] * wx[n]
            res += row_res * wy[m]
        return res

    @ti.func
    def _guided_flow_at_i32_ref2d(
        flow: ti.template(),
        ref_i32: ti.template(),
        y: int,
        x: int,
    ) -> ti.types.vector(2, ti.f32):
        """
        AOT-friendly guided flow aggregation:
        - fixed ref dtype/shape (i32, 2D)
        - no template args / dynamic shape checks
        """
        h, w = flow.shape[0], flow.shape[1]
        inv_norm = 1.0 / 65535.0
        total_w = 1e-12
        sum_u, sum_v = 0.0, 0.0
        center_val = float(ref_i32[y, x]) * inv_norm

        for dy in ti.static(range(-2, 3)):
            ny = tm.clamp(y + dy, 0, h - 1)
            for dx in ti.static(range(-2, 3)):
                nx = tm.clamp(x + dx, 0, w - 1)

                w_s = 0.0
                if ti.static(abs(dx) == 2):
                    if ti.static(abs(dy) == 2):
                        w_s = 0.002969
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.013306
                    else:
                        w_s = 0.021938
                elif ti.static(abs(dx) == 1):
                    if ti.static(abs(dy) == 2):
                        w_s = 0.013306
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.059634
                    else:
                        w_s = 0.098320
                else:
                    if ti.static(abs(dy) == 2):
                        w_s = 0.021938
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.098320
                    else:
                        w_s = 0.162103

                val_neighbor = float(ref_i32[ny, nx]) * inv_norm
                diff = val_neighbor - center_val
                w_curr = w_s * ti.exp(-(diff * diff) * 50.0)
                sum_u += flow[ny, nx, 0] * w_curr
                sum_v += flow[ny, nx, 1] * w_curr
                total_w += w_curr

        return ti.Vector([sum_u / total_w, sum_v / total_w])

    @ti.func
    def _guided_flow_at_i32_ref3d(
        flow: ti.template(),
        ref_i32: ti.template(),
        y: int,
        x: int,
    ) -> ti.types.vector(2, ti.f32):
        """
        AOT-friendly guided flow aggregation for RGB reference (uses green channel).
        """
        h, w = flow.shape[0], flow.shape[1]
        inv_norm = 1.0 / 65535.0
        total_w = 1e-12
        sum_u, sum_v = 0.0, 0.0
        center_val = float(ref_i32[y, x, 1]) * inv_norm

        for dy in ti.static(range(-2, 3)):
            ny = tm.clamp(y + dy, 0, h - 1)
            for dx in ti.static(range(-2, 3)):
                nx = tm.clamp(x + dx, 0, w - 1)

                w_s = 0.0
                if ti.static(abs(dx) == 2):
                    if ti.static(abs(dy) == 2):
                        w_s = 0.002969
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.013306
                    else:
                        w_s = 0.021938
                elif ti.static(abs(dx) == 1):
                    if ti.static(abs(dy) == 2):
                        w_s = 0.013306
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.059634
                    else:
                        w_s = 0.098320
                else:
                    if ti.static(abs(dy) == 2):
                        w_s = 0.021938
                    elif ti.static(abs(dy) == 1):
                        w_s = 0.098320
                    else:
                        w_s = 0.162103

                val_neighbor = float(ref_i32[ny, nx, 1]) * inv_norm
                diff = val_neighbor - center_val
                w_curr = w_s * ti.exp(-(diff * diff) * 50.0)
                sum_u += flow[ny, nx, 0] * w_curr
                sum_v += flow[ny, nx, 1] * w_curr
                total_w += w_curr

        return ti.Vector([sum_u / total_w, sum_v / total_w])

    @ti.kernel
    def _warp_guided_i32_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
        ref: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        """
        Public fixed-signature kernel for AOT export.
        Keeping this in warp.py avoids reimplementing warp logic in aot_alignment_compiler.py.
        """
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = _guided_flow_at_i32_ref2d(flow, ref, y, x)
            u_final = float(x) + guided_uv[0]
            v_final = float(y) + guided_uv[1]
            res = sample_bicubic_fast(src, u_final, v_final)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_guided_i32_rgb_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=3),
        ref: ti.types.ndarray(dtype=ti.i32, ndim=3),
    ):
        """
        Public fixed-signature kernel for RGB AOT export.
        """
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = _guided_flow_at_i32_ref3d(flow, ref, y, x)
            u_final = float(x) + guided_uv[0]
            v_final = float(y) + guided_uv[1]
            for c in ti.static(range(3)):
                res = sample_bicubic_3ch_fast(src, u_final, v_final, c)
                dst[y, x, c] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_naked_i32_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        """
        Naked Warp Kernel (Grayscale) - Optimized for pre-refined flow.
        No guidance window, pure bicubic sampling.
        """
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            u_final = float(x) + flow[y, x, 0]
            v_final = float(y) + flow[y, x, 1]
            res = sample_bicubic_fast(src, u_final, v_final)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_naked_i32_rgb_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=3),
    ):
        """
        Naked Warp Kernel (RGB) - Optimized for pre-refined flow.
        """
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            u_final = float(x) + flow[y, x, 0]
            v_final = float(y) + flow[y, x, 1]
            for c in ti.static(range(3)):
                res = sample_bicubic_3ch_fast(src, u_final, v_final, c)
                dst[y, x, c] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    # Kernels handling normalization and casting internally

    @ti.kernel
    def _warp_kernel_guided(
        src: ti.types.ndarray(ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(ndim=2),
        ref: ti.types.ndarray(),  # Guidance Image
        h: int,
        w: int,
        use_guidance: ti.template(),
        bits: int,
        target_dtype: ti.template(),
    ):

        inv_norm = 1.0
        if bits > 0:
            inv_norm = 1.0 / float((1 << bits) - 1)

        for y, x in ti.ndrange(h, w):
            u_final, v_final = 0.0, 0.0

            if ti.static(use_guidance):
                # Joint Bilateral Refinement (Micro-Optimized)
                total_w = 1e-12
                sum_u, sum_v = 0.0, 0.0

                center_val = 0.0
                if ti.static(len(ref.shape) == 2):
                    center_val = float(ref[y, x]) * inv_norm
                else:
                    center_val = float(ref[y, x, 1]) * inv_norm

                # Manually unrolled 5x5 window
                for dy in ti.static(range(-2, 3)):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    for dx in ti.static(range(-2, 3)):
                        nx = tm.clamp(x + dx, 0, w - 1)

                        # Spatial Gaussian Weight (Resolved at compile time)
                        w_s = 0.0
                        if ti.static(abs(dx) == 2):
                            if ti.static(abs(dy) == 2):
                                w_s = 0.002969
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.013306
                            else:
                                w_s = 0.021938
                        elif ti.static(abs(dx) == 1):
                            if ti.static(abs(dy) == 2):
                                w_s = 0.013306
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.059634
                            else:
                                w_s = 0.098320
                        else:
                            if ti.static(abs(dy) == 2):
                                w_s = 0.021938
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.098320
                            else:
                                w_s = 0.162103

                        val_neighbor = 0.0
                        if ti.static(len(ref.shape) == 2):
                            val_neighbor = float(ref[ny, nx]) * inv_norm
                        else:
                            val_neighbor = float(ref[ny, nx, 1]) * inv_norm

                        diff = val_neighbor - center_val
                        # Exponential range weight (Optimized 1/0.02 = 50.0)
                        w_curr = w_s * ti.exp(-(diff * diff) * 50.0)

                        sum_u += flow[ny, nx, 0] * w_curr
                        sum_v += flow[ny, nx, 1] * w_curr
                        total_w += w_curr

                u_final = float(x) + sum_u / total_w
                v_final = float(y) + sum_v / total_w
            else:
                u_final = float(x) + flow[y, x, 0]
                v_final = float(y) + flow[y, x, 1]

            res = sample_bicubic_fast(src, u_final, v_final)
            if ti.static(target_dtype == ti.u16):
                dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.u16)
            elif ti.static(target_dtype == ti.u8):
                dst[y, x] = ti.cast(tm.clamp(res, 0.0, 255.0), ti.u8)
            else:
                dst[y, x] = res

    @ti.kernel
    def _warp_kernel_guided_3ch(
        src: ti.types.ndarray(ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(ndim=3),
        ref: ti.types.ndarray(),
        h: int,
        w: int,
        use_guidance: ti.template(),
        bits: int,
        target_dtype: ti.template(),
    ):

        inv_norm = 1.0
        if bits > 0:
            inv_norm = 1.0 / float((1 << bits) - 1)

        for y, x in ti.ndrange(h, w):
            u_final, v_final = 0.0, 0.0

            if ti.static(use_guidance):
                # Joint Bilateral Refinement (Micro-Optimized)
                total_w = 1e-12
                sum_u, sum_v = 0.0, 0.0

                center_val = 0.0
                if ti.static(len(ref.shape) == 2):
                    center_val = float(ref[y, x]) * inv_norm
                else:
                    center_val = float(ref[y, x, 1]) * inv_norm

                for dy in ti.static(range(-2, 3)):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    for dx in ti.static(range(-2, 3)):
                        nx = tm.clamp(x + dx, 0, w - 1)

                        # Spatial Gaussian Weight
                        w_s = 0.0
                        if ti.static(abs(dx) == 2):
                            if ti.static(abs(dy) == 2):
                                w_s = 0.002969
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.013306
                            else:
                                w_s = 0.021938
                        elif ti.static(abs(dx) == 1):
                            if ti.static(abs(dy) == 2):
                                w_s = 0.013306
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.059634
                            else:
                                w_s = 0.098320
                        else:
                            if ti.static(abs(dy) == 2):
                                w_s = 0.021938
                            elif ti.static(abs(dy) == 1):
                                w_s = 0.098320
                            else:
                                w_s = 0.162103

                        val_neighbor = 0.0
                        if ti.static(len(ref.shape) == 2):
                            val_neighbor = float(ref[ny, nx]) * inv_norm
                        else:
                            val_neighbor = float(ref[ny, nx, 1]) * inv_norm

                        diff = val_neighbor - center_val
                        # Optimized exponent
                        w_curr = w_s * ti.exp(-(diff * diff) * 50.0)
                        sum_u += flow[ny, nx, 0] * w_curr
                        sum_v += flow[ny, nx, 1] * w_curr
                        total_w += w_curr

                u_final = float(x) + sum_u / total_w
                v_final = float(y) + sum_v / total_w
            else:
                u_final = float(x) + flow[y, x, 0]
                v_final = float(y) + flow[y, x, 1]

            for c in ti.static(range(3)):
                res = sample_bicubic_3ch_fast(src, u_final, v_final, c)
                if ti.static(target_dtype == ti.u16):
                    dst[y, x, c] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.u16)
                elif ti.static(target_dtype == ti.u8):
                    dst[y, x, c] = ti.cast(tm.clamp(res, 0.0, 255.0), ti.u8)
                else:
                    dst[y, x, c] = res

    def warp_image_gpu(
        src, flow, dst=None, buffer_provider="pool", enable_tiling=True, guidance=None
    ):
        """
        Warp image on GPU with Optional Joint Bilateral Flow Refinement.
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        h, w = src.shape[:2]

        src_gpu, src_is_temp = common.ensure_taichi_field(
            src, buffer_provider=buffer_provider
        )
        flow_gpu, flow_is_temp = common.ensure_taichi_field(
            flow, dtype=ti.f32, buffer_provider=buffer_provider
        )

        src_ti_dtype = getattr(src_gpu, "dtype", ti.f32)

        use_guidance = 0
        guidance_gpu = None
        guidance_is_temp = False
        bits = 0

        if guidance is not None:
            use_guidance = 1
            g_dtype = getattr(guidance, "dtype", None)
            if g_dtype in [np.uint16, ti.u16]:
                bits = 16
            elif g_dtype in [np.uint8, ti.u8]:
                bits = 8

            guidance_gpu, guidance_is_temp = common.ensure_taichi_field(
                guidance, buffer_provider=buffer_provider
            )
        else:
            guidance_gpu = common.get_temp_buffer((1, 1), ti.f32, buffer_provider)
            guidance_is_temp = True

        channels = 1 if len(src_gpu.shape) == 2 else src_gpu.shape[2]
        res_gpu = None
        created_dst = False
        target_dtype = src_ti_dtype

        if (
            dst is not None
            and hasattr(dst, "shape")
            and not isinstance(dst, np.ndarray)
        ):
            res_gpu = dst
            target_dtype = dst.dtype
        else:
            res_gpu = common.get_temp_buffer(
                src_gpu.shape, src_ti_dtype, buffer_provider
            )
            created_dst = True

        if channels == 1:
            _warp_kernel_guided(
                src_gpu,
                flow_gpu,
                res_gpu,
                guidance_gpu,
                h,
                w,
                use_guidance,
                bits,
                target_dtype,
            )
        else:
            _warp_kernel_guided_3ch(
                src_gpu,
                flow_gpu,
                res_gpu,
                guidance_gpu,
                h,
                w,
                use_guidance,
                bits,
                target_dtype,
            )

        if src_is_temp:
            common.release_temp_buffer(src_gpu)
        if flow_is_temp:
            common.release_temp_buffer(flow_gpu)
        if guidance_is_temp:
            common.release_temp_buffer(guidance_gpu)

        res = common.to_numpy_if_needed(res_gpu, dst is None)
        if created_dst and dst is None:
            common.release_temp_buffer(res_gpu)

        return res

else:

    def warp_image_gpu(
        src, flow, dst=None, buffer_provider="pool", enable_tiling=True, guidance=None
    ):
        raise ImportError("Taichi not available")
