"""
Block Matching (BM) Optical Flow with Parabolic Fit
===================================================

An optimized hybrid optical flow algorithm that combines integer block matching (SAD)
with clamped parabolic fit sub-pixel estimation using dynamic window sizes.
"""

import importlib
import os
import numpy as np

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass


if TAICHI_AVAILABLE or os.environ.get("AOT_MODE", "1") == "1":
    import taichi as ti

    @ti.func
    def _bm_clamp(v: ti.i32, lo: ti.i32, hi: ti.i32) -> ti.i32:
        return ti.max(lo, ti.min(v, hi))

    @ti.func
    def _bm_sample(
        img: ti.types.ndarray(), y: ti.f32, x: ti.f32, h: ti.i32, w: ti.i32
    ) -> ti.f32:
        x0 = _bm_clamp(ti.cast(ti.floor(x), ti.i32), 0, w - 1)
        y0 = _bm_clamp(ti.cast(ti.floor(y), ti.i32), 0, h - 1)
        x1 = _bm_clamp(x0 + 1, 0, w - 1)
        y1 = _bm_clamp(y0 + 1, 0, h - 1)
        fx = x - ti.cast(x0, ti.f32)
        fy = y - ti.cast(y0, ti.f32)
        v00 = img[y0, x0]
        v01 = img[y0, x1]
        v10 = img[y1, x0]
        v11 = img[y1, x1]
        return (1.0 - fy) * ((1.0 - fx) * v00 + fx * v01) + fy * (
            (1.0 - fx) * v10 + fx * v11
        )

    @ti.func
    def _bm_read_i32(
        img: ti.types.ndarray(), y: ti.i32, x: ti.i32, h: ti.i32, w: ti.i32
    ) -> ti.f32:
        yy = _bm_clamp(y, 0, h - 1)
        xx = _bm_clamp(x, 0, w - 1)
        return img[yy, xx]

    @ti.kernel
    def _bm_zero_flow_kernel(flow: ti.types.ndarray()):
        h = flow.shape[0]
        w = flow.shape[1]
        for y, x in ti.ndrange(h, w):
            flow[y, x, 0] = 0.0
            flow[y, x, 1] = 0.0

    @ti.kernel
    def _bm_zero_stats_kernel(stats: ti.types.ndarray()):
        n = stats.shape[0]
        for i in range(n):
            stats[i] = 0.0

    @ti.func
    def _bm_patch_sad_5point(
        prev: ti.types.ndarray(),
        next: ti.types.ndarray(),
        cy: ti.i32,
        cx: ti.i32,
        fy: ti.i32,
        fx: ti.i32,
        h: ti.i32,
        w: ti.i32,
        win_radius: ti.i32,
    ) -> ti.types.vector(5, ti.f32):
        # Single-pass 5-point stencil accumulator in registers:
        # [0]=center, [1]=left, [2]=right, [3]=up, [4]=down
        sad_vec = ti.Vector([0.0, 0.0, 0.0, 0.0, 0.0])
        half_r = win_radius // 2
        for oy_i in range(-half_r, half_r + 1):
            oy = oy_i * 2
            yy_i = cy + oy
            for ox_i in range(-half_r, half_r + 1):
                ox = ox_i * 2
                xx_i = cx + ox
                p_val = _bm_read_i32(prev, yy_i, xx_i, h, w)
                
                # Center
                sad_vec[0] += ti.abs(_bm_read_i32(next, yy_i + fy, xx_i + fx, h, w) - p_val)
                # Left (fx - 1)
                sad_vec[1] += ti.abs(_bm_read_i32(next, yy_i + fy, xx_i + fx - 1, h, w) - p_val)
                # Right (fx + 1)
                sad_vec[2] += ti.abs(_bm_read_i32(next, yy_i + fy, xx_i + fx + 1, h, w) - p_val)
                # Up (fy - 1)
                sad_vec[3] += ti.abs(_bm_read_i32(next, yy_i + fy - 1, xx_i + fx, h, w) - p_val)
                # Down (fy + 1)
                sad_vec[4] += ti.abs(_bm_read_i32(next, yy_i + fy + 1, xx_i + fx, h, w) - p_val)
        return sad_vec

    @ti.func
    def _bm_patch_sad(
        prev: ti.types.ndarray(),
        next: ti.types.ndarray(),
        cy: ti.i32,
        cx: ti.i32,
        shift_y: ti.i32,
        shift_x: ti.i32,
        h: ti.i32,
        w: ti.i32,
        win_radius: ti.i32,
    ) -> ti.f32:
        sad = 0.0
        half_r = win_radius // 2
        for oy_i in range(-half_r, half_r + 1):
            oy = oy_i * 2
            yy_i = cy + oy
            for ox_i in range(-half_r, half_r + 1):
                ox = ox_i * 2
                xx_i = cx + ox
                diff = _bm_read_i32(next, yy_i + shift_y, xx_i + shift_x, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                sad += ti.abs(diff)
        return sad

    @ti.kernel
    def _bm_grid_track_kernel(
        prev: ti.types.ndarray(),
        next: ti.types.ndarray(),
        prev_grid_flow: ti.types.ndarray(),
        grid_flow: ti.types.ndarray(),
        grid_meta: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
        win_radius: ti.i32,
        has_prev_flow: ti.i32,
        epsilon: ti.f32,
    ):
        h = prev.shape[0]
        w = prev.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]

        pts_side = (win_radius * 2) // 2 + 1
        inv_patch_area = 1.0 / ti.cast(pts_side * pts_side, ti.f32)
        
        # Adaptive Tri-Tier Thresholds (Normalized to [0.0, 1.0] intensity)
        tau_low = 0.020    # 2.0% average pixel delta -> Tier 1 (Candidate evaluation only)
        tau_high = 0.080   # 8.0% average pixel delta -> Tier 2 (Micro 3x3 search) vs Tier 3 (Full bounded)

        for gy, gx in ti.ndrange(grid_h, grid_w):
            px = ti.cast(border_margin + gx * grid_step, ti.f32)
            py = ti.cast(border_margin + gy * grid_step, ti.f32)
            grid_flow[gy, gx, 0] = 0.0
            grid_flow[gy, gx, 1] = 0.0
            grid_flow[gy, gx, 2] = 0.0
            grid_meta[gy, gx, 0] = 0.0
            grid_meta[gy, gx, 1] = 0.0
            grid_meta[gy, gx, 2] = 2.0
            grid_meta[gy, gx, 3] = 0.0

            if px < ti.cast(w - border_margin, ti.f32) and py < ti.cast(h - border_margin, ti.f32):
                center_y = border_margin + gy * grid_step
                center_x = border_margin + gx * grid_step

                init_dx = 0
                init_dy = 0
                if has_prev_flow == 1:
                    cgx = _bm_clamp(gx >> 1, 0, prev_grid_flow.shape[1] - 1)
                    cgy = _bm_clamp(gy >> 1, 0, prev_grid_flow.shape[0] - 1)
                    init_dx = ti.cast(ti.round(prev_grid_flow[cgy, cgx, 0] * 2.0), ti.i32)
                    init_dy = ti.cast(ti.round(prev_grid_flow[cgy, cgx, 1] * 2.0), ti.i32)

                best_cy = init_dy
                best_cx = init_dx
                baseline_sad = _bm_patch_sad(
                    prev, next, center_y, center_x, init_dy, init_dx, h, w, win_radius
                )
                initial_norm_sad = baseline_sad * inv_patch_area
                best_sad = baseline_sad

                # === ADAPTIVE TRI-TIER SEARCH ===
                if has_prev_flow == 1 and initial_norm_sad <= tau_low:
                    # TIER 1: Error Rendah (Tebakan Coarse Sangat Bagus)
                    # Lewati semua integer search, gunakan langsung tebakan untuk subpixel fit
                    best_cy = init_dy
                    best_cx = init_dx
                elif has_prev_flow == 1 and initial_norm_sad <= tau_high:
                    # TIER 2: Error Menengah (Mikro Search 3x3 di sekitar tebakan)
                    for foy_s, fox_s in ti.static(((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1))):
                        soy = init_dy + foy_s
                        sox = init_dx + fox_s
                        sad = _bm_patch_sad(prev, next, center_y, center_x, soy, sox, h, w, win_radius)
                        if sad < best_sad:
                            best_sad = sad
                            best_cy = soy
                            best_cx = sox
                else:
                    # TIER 3: Error Tinggi / Base Level (Full Coarse Diamond Search + Fine Refinement)
                    for coy_s, cox_s in ti.static(((-2, 0), (2, 0), (0, -2), (0, 2))):
                        soy = init_dy + coy_s
                        sox = init_dx + cox_s
                        sad = _bm_patch_sad(prev, next, center_y, center_x, soy, sox, h, w, win_radius)
                        if sad < best_sad:
                            best_sad = sad
                            best_cy = soy
                            best_cx = sox

                    # Fine Diamond around best coarse
                    best_fy_tmp = best_cy
                    best_fx_tmp = best_cx
                    for foy_s, fox_s in ti.static(((-1, 0), (1, 0), (0, -1), (0, 1))):
                        soy = best_cy + foy_s
                        sox = best_cx + fox_s
                        sad = _bm_patch_sad(prev, next, center_y, center_x, soy, sox, h, w, win_radius)
                        if sad < best_sad:
                            best_sad = sad
                            best_fy_tmp = soy
                            best_fx_tmp = sox
                    best_cy = best_fy_tmp
                    best_cx = best_fx_tmp

                # === SINGLE-PASS 5-POINT SUB-PIXEL PARABOLIC FIT ===
                stencil = _bm_patch_sad_5point(
                    prev, next, center_y, center_x, best_cy, best_cx, h, w, win_radius
                )
                sad_center = stencil[0]
                sad_left = stencil[1]
                sad_right = stencil[2]
                sad_up = stencil[3]
                sad_down = stencil[4]

                dx_offset = 0.0
                denom_x = sad_right - 2.0 * sad_center + sad_left
                if ti.abs(denom_x) > 1e-4:
                    dx_offset = -0.5 * (sad_right - sad_left) / denom_x
                    dx_offset = ti.max(-0.5, ti.min(0.5, dx_offset))

                dy_offset = 0.0
                denom_y = sad_down - 2.0 * sad_center + sad_up
                if ti.abs(denom_y) > 1e-4:
                    dy_offset = -0.5 * (sad_down - sad_up) / denom_y
                    dy_offset = ti.max(-0.5, ti.min(0.5, dy_offset))

                dx = ti.cast(best_cx, ti.f32) + dx_offset
                dy = ti.cast(best_cy, ti.f32) + dy_offset

                # Parallax & Physical Motion Clamping
                max_flow = ti.cast(grid_step * 2 + win_radius * 2, ti.f32)
                dx = ti.max(-max_flow, ti.min(max_flow, dx))
                dy = ti.max(-max_flow, ti.min(max_flow, dy))

                residual = sad_center * inv_patch_area

                grid_flow[gy, gx, 0] = dx
                grid_flow[gy, gx, 1] = dy
                grid_flow[gy, gx, 2] = 1.0

                motion2 = dx * dx + dy * dy
                med_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.04
                high_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.20
                cls = 0.0
                if motion2 > med_thr or residual > 0.05:
                    cls = 1.0
                if motion2 > high_thr or residual > 0.12:
                    cls = 2.0
                grid_meta[gy, gx, 0] = residual
                grid_meta[gy, gx, 1] = 1.0
                grid_meta[gy, gx, 2] = cls
                grid_meta[gy, gx, 3] = motion2

    @ti.kernel
    def _bm_adaptive_refine_kernel(
        prev: ti.types.ndarray(),
        next: ti.types.ndarray(),
        grid_flow: ti.types.ndarray(),
        grid_meta: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
        win_radius: ti.i32,
        iterations: ti.i32,
        epsilon: ti.f32,
        class_threshold: ti.i32,
    ):
        h = prev.shape[0]
        w = prev.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]

        pts_side = (win_radius * 2) // 2 + 1
        inv_patch_area = 1.0 / ti.cast(pts_side * pts_side, ti.f32)

        for gy, gx in ti.ndrange(grid_h, grid_w):
            cls = ti.cast(grid_meta[gy, gx, 2], ti.i32)
            if cls >= class_threshold and grid_flow[gy, gx, 2] > 0.5:
                center_y = border_margin + gy * grid_step
                center_x = border_margin + gx * grid_step

                dx_init = grid_flow[gy, gx, 0]
                dy_init = grid_flow[gy, gx, 1]
                best_fx = ti.cast(ti.round(dx_init), ti.i32)
                best_fy = ti.cast(ti.round(dy_init), ti.i32)

                stencil = _bm_patch_sad_5point(
                    prev, next, center_y, center_x, best_fy, best_fx, h, w, win_radius
                )
                sad_center = stencil[0]
                sad_left = stencil[1]
                sad_right = stencil[2]
                sad_up = stencil[3]
                sad_down = stencil[4]

                dx_offset = 0.0
                denom_x = sad_right - 2.0 * sad_center + sad_left
                if ti.abs(denom_x) > 1e-4:
                    dx_offset = -0.5 * (sad_right - sad_left) / denom_x
                    dx_offset = ti.max(-0.5, ti.min(0.5, dx_offset))

                dy_offset = 0.0
                denom_y = sad_down - 2.0 * sad_center + sad_up
                if ti.abs(denom_y) > 1e-4:
                    dy_offset = -0.5 * (sad_down - sad_up) / denom_y
                    dy_offset = ti.max(-0.5, ti.min(0.5, dy_offset))

                dx = ti.cast(best_fx, ti.f32) + dx_offset
                dy = ti.cast(best_fy, ti.f32) + dy_offset

                max_flow = ti.cast(grid_step * 2 + win_radius * 2, ti.f32)
                dx = ti.max(-max_flow, ti.min(max_flow, dx))
                dy = ti.max(-max_flow, ti.min(max_flow, dy))

                residual = sad_center * inv_patch_area

                grid_flow[gy, gx, 0] = dx
                grid_flow[gy, gx, 1] = dy
                grid_meta[gy, gx, 0] = residual
                grid_meta[gy, gx, 3] = dx * dx + dy * dy

    @ti.kernel
    def _bm_motion_stats_kernel(
        grid_flow: ti.types.ndarray(),
        grid_meta: ti.types.ndarray(),
        stats: ti.types.ndarray(),
    ):
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]
        for gy, gx in ti.ndrange(grid_h, grid_w):
            if grid_flow[gy, gx, 2] > 0.5:
                cls = grid_meta[gy, gx, 2]
                ti.atomic_add(stats[0], 1.0)
                if cls < 0.5:
                    ti.atomic_add(stats[1], 1.0)
                elif cls < 1.5:
                    ti.atomic_add(stats[2], 1.0)
                else:
                    ti.atomic_add(stats[3], 1.0)
                ti.atomic_add(stats[4], grid_meta[gy, gx, 0])
                ti.atomic_add(stats[5], grid_meta[gy, gx, 3])

    @ti.kernel
    def _bm_dense_interpolate_kernel(
        grid_flow: ti.types.ndarray(),
        flow_out: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
        overlap: ti.f32,
    ):
        # Content-Aware Fast Anisotropic Dense Interpolation
        h = flow_out.shape[0]
        w = flow_out.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]
        inv_step = 1.0 / ti.cast(grid_step, ti.f32)

        for y, x in ti.ndrange(h, w):
            gx_f = (ti.cast(x - border_margin, ti.f32)) * inv_step
            gy_f = (ti.cast(y - border_margin, ti.f32)) * inv_step
            gx0 = _bm_clamp(ti.cast(ti.floor(gx_f), ti.i32), 0, grid_w - 1)
            gy0 = _bm_clamp(ti.cast(ti.floor(gy_f), ti.i32), 0, grid_h - 1)
            gx1 = _bm_clamp(gx0 + 1, 0, grid_w - 1)
            gy1 = _bm_clamp(gy0 + 1, 0, grid_h - 1)
            
            f00_x = grid_flow[gy0, gx0, 0]
            f00_y = grid_flow[gy0, gx0, 1]
            f01_x = grid_flow[gy0, gx1, 0]
            f01_y = grid_flow[gy0, gx1, 1]
            f10_x = grid_flow[gy1, gx0, 0]
            f10_y = grid_flow[gy1, gx0, 1]
            f11_x = grid_flow[gy1, gx1, 0]
            f11_y = grid_flow[gy1, gx1, 1]

            fx_raw = ti.max(0.0, ti.min(gx_f - ti.cast(gx0, ti.f32), 1.0))
            fy_raw = ti.max(0.0, ti.min(gy_f - ti.cast(gy0, ti.f32), 1.0))

            # Variance check across 4 neighbor grid cells
            diff_max = ti.max(
                ti.abs(f00_x - f01_x) + ti.abs(f00_y - f01_y),
                ti.abs(f00_x - f10_x) + ti.abs(f00_y - f10_y),
                ti.abs(f00_x - f11_x) + ti.abs(f00_y - f11_y)
            )

            if diff_max < 0.25:
                # Fast Path: Area homogen / gerakan seragam (Linear Bilinear cepat)
                w00 = (1.0 - fx_raw) * (1.0 - fy_raw)
                w01 = fx_raw * (1.0 - fy_raw)
                w10 = (1.0 - fx_raw) * fy_raw
                w11 = fx_raw * fy_raw
                flow_out[y, x, 0] = f00_x * w00 + f01_x * w01 + f10_x * w10 + f11_x * w11
                flow_out[y, x, 1] = f00_y * w00 + f01_y * w01 + f10_y * w10 + f11_y * w11
            else:
                # Anisotropic Smooth Path: Menjaga ketajaman tepi dan kurva kontur
                sx = fx_raw * fx_raw * (3.0 - 2.0 * fx_raw)
                sy = fy_raw * fy_raw * (3.0 - 2.0 * fy_raw)
                w00 = (1.0 - sx) * (1.0 - sy) * grid_flow[gy0, gx0, 2]
                w01 = sx * (1.0 - sy) * grid_flow[gy0, gx1, 2]
                w10 = (1.0 - sx) * sy * grid_flow[gy1, gx0, 2]
                w11 = sx * sy * grid_flow[gy1, gx1, 2]
                wt = w00 + w01 + w10 + w11

                if wt > 1e-6:
                    inv_wt = 1.0 / wt
                    flow_out[y, x, 0] = (f00_x * w00 + f01_x * w01 + f10_x * w10 + f11_x * w11) * inv_wt
                    flow_out[y, x, 1] = (f00_y * w00 + f01_y * w01 + f10_y * w10 + f11_y * w11) * inv_wt
                else:
                    flow_out[y, x, 0] = 0.0
                    flow_out[y, x, 1] = 0.0

    @ti.kernel
    def _bm_dense_blocky_kernel(
        grid_flow: ti.types.ndarray(),
        flow_out: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
    ):
        h = flow_out.shape[0]
        w = flow_out.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]
        inv_step = 1.0 / ti.cast(grid_step, ti.f32)

        for y, x in ti.ndrange(h, w):
            gx_f = ti.cast(x - border_margin, ti.f32) * inv_step
            gy_f = ti.cast(y - border_margin, ti.f32) * inv_step
            gx = _bm_clamp(ti.cast(ti.floor(gx_f + 0.5), ti.i32), 0, grid_w - 1)
            gy = _bm_clamp(ti.cast(ti.floor(gy_f + 0.5), ti.i32), 0, grid_h - 1)

            if grid_flow[gy, gx, 2] > 0.5:
                flow_out[y, x, 0] = grid_flow[gy, gx, 0]
                flow_out[y, x, 1] = grid_flow[gy, gx, 1]
            else:
                flow_out[y, x, 0] = 0.0
                flow_out[y, x, 1] = 0.0

    @ti.kernel
    def _bm_dense_blocky_clamped_kernel(
        grid_flow: ti.types.ndarray(),
        flow_out: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
        max_flow_px: ti.f32,
    ):
        h = flow_out.shape[0]
        w = flow_out.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]
        inv_step = 1.0 / ti.cast(grid_step, ti.f32)

        for y, x in ti.ndrange(h, w):
            gx_f = ti.cast(x - border_margin, ti.f32) * inv_step
            gy_f = ti.cast(y - border_margin, ti.f32) * inv_step
            gx = _bm_clamp(ti.cast(ti.floor(gx_f + 0.5), ti.i32), 0, grid_w - 1)
            gy = _bm_clamp(ti.cast(ti.floor(gy_f + 0.5), ti.i32), 0, grid_h - 1)

            fx = 0.0
            fy = 0.0
            if grid_flow[gy, gx, 2] > 0.5:
                fx = grid_flow[gy, gx, 0]
                fy = grid_flow[gy, gx, 1]

            if max_flow_px > 0.0:
                fx = ti.max(-max_flow_px, ti.min(max_flow_px, fx))
                fy = ti.max(-max_flow_px, ti.min(max_flow_px, fy))

            flow_out[y, x, 0] = fx
            flow_out[y, x, 1] = fy
