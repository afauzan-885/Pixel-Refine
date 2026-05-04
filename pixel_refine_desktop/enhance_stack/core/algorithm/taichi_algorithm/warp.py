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
    def sample_bicubic_fast(img: ti.template(), u: float, v: float) -> float:
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

    @ti.func
    def _guided_flow_at_i32_ref2d_turbo(
        flow: ti.template(),
        ref_i32: ti.template(),
        y: int,
        x: int,
    ) -> ti.types.vector(2, ti.f32):
        """Optimized 3x3 Guided Flow (Faster, minimal accuracy loss)"""
        h, w = flow.shape[0], flow.shape[1]
        inv_norm = 1.0 / 65535.0
        total_w = 1e-12
        sum_uv = ti.Vector([0.0, 0.0])
        center_val = float(ref_i32[y, x]) * inv_norm

        for dy in ti.static(range(-1, 2)):
            ny = tm.clamp(y + dy, 0, h - 1)
            for dx in ti.static(range(-1, 2)):
                nx = tm.clamp(x + dx, 0, w - 1)
                
                w_s = 0.4
                if ti.static(abs(dx) == 1 and abs(dy) == 1): w_s = 0.1
                elif ti.static(abs(dx) == 1 or abs(dy) == 1): w_s = 0.2

                val_neighbor = float(ref_i32[ny, nx]) * inv_norm
                diff = val_neighbor - center_val
                # Ultra-Fast Linear Approximation of Gaussian
                w_curr = w_s * tm.max(0.0, 1.0 - (diff * diff) * 60.0)
                sum_uv += flow[ny, nx] * w_curr
                total_w += w_curr

        return sum_uv / total_w

    @ti.func
    def _guided_flow_at_i32_ref3d_turbo(
        flow: ti.template(),
        ref_i32: ti.template(),
        y: int,
        x: int,
    ) -> ti.types.vector(2, ti.f32):
        """Optimized 3x3 Guided Flow for RGB (Uses Green)"""
        h, w = flow.shape[0], flow.shape[1]
        inv_norm = 1.0 / 65535.0
        total_w = 1e-12
        sum_uv = ti.Vector([0.0, 0.0])
        center_val = float(ref_i32[y, x, 1]) * inv_norm

        for dy in ti.static(range(-1, 2)):
            ny = tm.clamp(y + dy, 0, h - 1)
            for dx in ti.static(range(-1, 2)):
                nx = tm.clamp(x + dx, 0, w - 1)
                
                w_s = 0.4
                if ti.static(abs(dx) == 1 and abs(dy) == 1): w_s = 0.1
                elif ti.static(abs(dx) == 1 or abs(dy) == 1): w_s = 0.2

                val_neighbor = float(ref_i32[ny, nx, 1]) * inv_norm
                diff = val_neighbor - center_val
                # Ultra-Fast Linear Approximation of Gaussian
                w_curr = w_s * tm.max(0.0, 1.0 - (diff * diff) * 60.0)
                sum_uv += flow[ny, nx] * w_curr
                total_w += w_curr

        return sum_uv / total_w

    @ti.kernel
    def _warp_guided_i32_turbo_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
        ref: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = _guided_flow_at_i32_ref2d_turbo(flow, ref, y, x)
            u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
            res = sample_bicubic_fast(src, u_final, v_final)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_guided_i32_rgb_turbo_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=3),
        ref: ti.types.ndarray(dtype=ti.i32, ndim=3),
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = _guided_flow_at_i32_ref3d_turbo(flow, ref, y, x)
            u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
            
            # Fused Bicubic Sampling for RGB
            x0 = int(ti.floor(u_final))
            y0 = int(ti.floor(v_final))
            dx = u_final - float(x0)
            dy = v_final - float(y0)
            wx = bicubic_interpolation.cubic_hermite_weights(dx)
            wy = bicubic_interpolation.cubic_hermite_weights(dy)

            acc_r, acc_g, acc_b = 0.0, 0.0, 0.0
            for m in ti.static(range(4)):
                yy = reflect_idx(y0 + m - 1, h)
                for n in ti.static(range(4)):
                    xx = reflect_idx(x0 + n - 1, w)
                    w_total = wx[n] * wy[m]
                    acc_r += float(src[yy, xx, 0]) * w_total
                    acc_g += float(src[yy, xx, 1]) * w_total
                    acc_b += float(src[yy, xx, 2]) * w_total
            
            dst[y, x, 0] = ti.cast(tm.clamp(acc_r, 0.0, 65535.0), ti.i32)
            dst[y, x, 1] = ti.cast(tm.clamp(acc_g, 0.0, 65535.0), ti.i32)
            dst[y, x, 2] = ti.cast(tm.clamp(acc_b, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_guided_i32_extreme_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
        ref: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = _guided_flow_at_i32_ref2d_turbo(flow, ref, y, x)
            u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
            
            # Fast Bilinear Sampling
            ix = int(ti.floor(u_final))
            iy = int(ti.floor(v_final))
            ix0 = tm.clamp(ix, 0, w - 1)
            iy0 = tm.clamp(iy, 0, h - 1)
            ix1 = tm.clamp(ix + 1, 0, w - 1)
            iy1 = tm.clamp(iy + 1, 0, h - 1)
            fx = u_final - float(ix)
            fy = v_final - float(iy)
            
            v00 = float(src[iy0, ix0])
            v01 = float(src[iy0, ix1])
            v10 = float(src[iy1, ix0])
            v11 = float(src[iy1, ix1])
            
            res = tm.mix(tm.mix(v00, v01, fx), tm.mix(v10, v11, fx), fy)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_guided_i32_rgb_ultra_aot(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2),
        flow: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2),
        ref_g: ti.types.ndarray(dtype=ti.i32, ndim=2), # 1-Channel Green Guidance
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            guided_uv = ti.Vector([0.0, 0.0])
            inv_norm = 1.0 / 65535.0
            
            if y >= 1 and y < h - 1 and x >= 1 and x < w - 1:
                # --- FAST PATH (No Clamping) ---
                total_w = 1e-12
                sum_uv = ti.Vector([0.0, 0.0])
                center_val = float(ref_g[y, x]) * inv_norm
                
                # Star pattern
                sum_uv += flow[y, x] * 0.4
                total_w += 0.4
                
                # Pre-calculate K = 60.0 * (1/65535)^2 to avoid norm in loop
                K_val = 1.397e-8
                
                for dy, dx in ti.static([(0, 1), (0, -1), (1, 0), (-1, 0)]):
                    ny, nx = y + dy, x + dx
                    val_neighbor = float(ref_g[ny, nx])
                    diff = val_neighbor - float(ref_g[y, x])
                    w_curr = 0.15 * tm.max(0.0, 1.0 - (diff * diff) * K_val)
                    sum_uv += flow[ny, nx] * w_curr
                    total_w += w_curr
                
                guided_uv = sum_uv / total_w
            else:
                # --- SLOW PATH ---
                total_w = 1e-12
                sum_uv = ti.Vector([0.0, 0.0])
                for dy in ti.static(range(-1, 2)):
                    ny = tm.clamp(y + dy, 0, h - 1)
                    for dx in ti.static(range(-1, 2)):
                        nx = tm.clamp(x + dx, 0, w - 1)
                        sum_uv += flow[ny, nx] * 0.111
                        total_w += 0.111
                guided_uv = sum_uv / total_w

            u_final, v_final = float(x) + guided_uv[0], float(y) + guided_uv[1]
            
            # Manual Bilinear for max speed
            ix = int(ti.floor(u_final))
            iy = int(ti.floor(v_final))
            ix0, iy0 = tm.clamp(ix, 0, w - 1), tm.clamp(iy, 0, h - 1)
            ix1, iy1 = tm.clamp(ix + 1, 0, w - 1), tm.clamp(iy + 1, 0, h - 1)
            fx, fy = u_final - float(ix), v_final - float(iy)
            
            p00 = ti.cast(src[iy0, ix0], ti.f32)
            p01 = ti.cast(src[iy0, ix1], ti.f32)
            p10 = ti.cast(src[iy1, ix0], ti.f32)
            p11 = ti.cast(src[iy1, ix1], ti.f32)
            
            # Manual lerp
            res = p00 + (p01 - p00) * fx + (p10 - p00) * fy + (p00 - p01 - p10 + p11) * (fx * fy)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _warp_naked_i32_rgb_ultra_aot(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2),
        flow: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2),
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            uv = flow[y, x]
            u_final, v_final = float(x) + uv[0], float(y) + uv[1]
            
            ix = int(ti.floor(u_final))
            iy = int(ti.floor(v_final))
            
            if iy >= 0 and iy < h - 1 and ix >= 0 and ix < w - 1:
                # --- FAST PATH (No Clamping) ---
                fx, fy = u_final - float(ix), v_final - float(iy)
                p00 = ti.cast(src[iy, ix], ti.f32)
                p01 = ti.cast(src[iy, ix + 1], ti.f32)
                p10 = ti.cast(src[iy + 1, ix], ti.f32)
                p11 = ti.cast(src[iy + 1, ix + 1], ti.f32)
                res = p00 + (p01 - p00) * fx + (p10 - p00) * fy + (p00 - p01 - p10 + p11) * (fx * fy)
                dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)
            else:
                # --- SLOW PATH (With Clamping for Borders) ---
                ix0, iy0 = tm.clamp(ix, 0, w - 1), tm.clamp(iy, 0, h - 1)
                ix1, iy1 = tm.clamp(ix + 1, 0, w - 1), tm.clamp(iy + 1, 0, h - 1)
                fx, fy = u_final - float(ix), v_final - float(iy)
                p00 = ti.cast(src[iy0, ix0], ti.f32)
                p01 = ti.cast(src[iy0, ix1], ti.f32)
                p10 = ti.cast(src[iy1, ix0], ti.f32)
                p11 = ti.cast(src[iy1, ix1], ti.f32)
                res = p00 + (p01 - p00) * fx + (p10 - p00) * fy + (p00 - p01 - p10 + p11) * (fx * fy)
                dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    @ti.kernel
    def _extract_green_i32_aot(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.i32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        for y, x in ti.ndrange(src.shape[0], src.shape[1]):
            dst[y, x] = src[y, x][1]

    @ti.kernel
    def _warp_naked_i32_extreme_aot(
        src: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
        dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            uv = flow[y, x]
            u_final, v_final = float(x) + uv[0], float(y) + uv[1]
            
            ix = int(ti.floor(u_final))
            iy = int(ti.floor(v_final))
            ix0 = tm.clamp(ix, 0, w - 1)
            iy0 = tm.clamp(iy, 0, h - 1)
            ix1 = tm.clamp(ix + 1, 0, w - 1)
            iy1 = tm.clamp(iy + 1, 0, h - 1)
            fx = u_final - float(ix)
            fy = v_final - float(iy)
            
            v00 = float(src[iy0, ix0])
            v01 = float(src[iy0, ix1])
            v10 = float(src[iy1, ix0])
            v11 = float(src[iy1, ix1])
            
            res = tm.mix(tm.mix(v00, v01, fx), tm.mix(v10, v11, fx), fy)
            dst[y, x] = ti.cast(tm.clamp(res, 0.0, 65535.0), ti.i32)

    def record_warp_graph(g: ti.graph.GraphBuilder):
        """Record Warp Graph for AOT."""
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3)
        flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
        ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.i32, ndim=3)
        g.dispatch(_warp_guided_i32_rgb_aot, src, flow, dst, ref)

    def warp_image_gpu(
        src,
        flow,
        dst=None,
        buffer_provider="pool",
        enable_tiling=True,
        guidance=None,
        # === AOT RECORDING ARGUMENTS ===
        g=None,
        src_arg=None,
        flow_arg=None,
        dst_arg=None,
        ref_arg=None,
        is_rgb_aot=True,
    ):
        """Warp image on GPU with Optional Joint Bilateral Flow Refinement."""
        if not TAICHI_AVAILABLE: raise ImportError("Taichi not available")

        # --- AOT ROUTING ---
        import os
        if os.environ.get("PIXEL_REFINE_AOT_MODE") == "1":
            from pixel_refine_desktop.enhance_stack.core.algorithm import taichi_aot
            return taichi_aot.warp_image(src, flow, ref=guidance, return_gpu=True)

        if g is not None:
            if is_rgb_aot:
                target = _warp_guided_i32_rgb_aot if ref_arg is not None else _warp_naked_i32_rgb_aot
                if ref_arg is not None: g.dispatch(target, src_arg, flow_arg, dst_arg, ref_arg)
                else: g.dispatch(target, src_arg, flow_arg, dst_arg)
            else:
                target = _warp_guided_i32_aot if ref_arg is not None else _warp_naked_i32_aot
                if ref_arg is not None: g.dispatch(target, src_arg, flow_arg, dst_arg, ref_arg)
                else: g.dispatch(target, src_arg, flow_arg, dst_arg)
            return None

        h, w = src.shape[:2]
        src_gpu, src_is_temp = common.ensure_taichi_field(src, buffer_provider=buffer_provider)
        flow_gpu, flow_is_temp = common.ensure_taichi_field(flow, dtype=ti.f32, buffer_provider=buffer_provider)
        
        guidance_gpu, guidance_is_temp = None, False
        bits = 0
        if guidance is not None:
            g_dtype = getattr(guidance, "dtype", np.uint16)
            bits = 16 if g_dtype in [np.uint16, ti.u16] else 8
            guidance_gpu, guidance_is_temp = common.ensure_taichi_field(guidance, buffer_provider=buffer_provider)
        
        channels = 1 if len(src_gpu.shape) == 2 else (3 if src_gpu.shape[2] >= 3 else src_gpu.shape[2])
        src_ti_dtype = getattr(src_gpu, "dtype", ti.f32)
        target_dtype = ti.f32
        if src_ti_dtype in [ti.u16, ti.i32]: target_dtype = ti.u16
        elif src_ti_dtype == ti.u8: target_dtype = ti.u8

        if dst is None:
            shape = (h, w) if channels == 1 else (h, w, channels)
            dst = common.get_temp_buffer(shape, target_dtype, buffer_provider)

        if channels == 1:
            _warp_kernel_guided(src_gpu, flow_gpu, dst, guidance_gpu if guidance_gpu else src_gpu, h, w, int(guidance is not None), bits, target_dtype)
        else:
            _warp_kernel_guided_3ch(src_gpu, flow_gpu, dst, guidance_gpu if guidance_gpu else src_gpu, h, w, int(guidance is not None), bits, target_dtype)

        if src_is_temp: common.release_temp_buffer(src_gpu)
        if flow_is_temp: common.release_temp_buffer(flow_gpu)
        if guidance_is_temp: common.release_temp_buffer(guidance_gpu)
        return dst

else:

    def warp_image_gpu(
        src,
        flow,
        dst=None,
        buffer_provider="pool",
        enable_tiling=True,
        guidance=None,
        # === AOT RECORDING ARGUMENTS ===
        g=None,
        src_arg=None,
        flow_arg=None,
        dst_arg=None,
        ref_arg=None,
    ):
        raise ImportError("Taichi not available")
