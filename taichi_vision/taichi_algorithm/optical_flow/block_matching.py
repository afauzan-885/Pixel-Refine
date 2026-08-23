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

        # Use stride to sample window sparsely for speed
        stride = 2

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
                init_dx = 0
                init_dy = 0
                if has_prev_flow == 1:
                    cgx = _bm_clamp(gx, 0, prev_grid_flow.shape[1] - 1)
                    cgy = _bm_clamp(gy, 0, prev_grid_flow.shape[0] - 1)
                    init_dx = ti.cast(ti.round(prev_grid_flow[cgy, cgx, 0] * 2.0), ti.i32)
                    init_dy = ti.cast(ti.round(prev_grid_flow[cgy, cgx, 1] * 2.0), ti.i32)

                # 1. Coarse Integer Search (Cross Pattern, 5 points)
                best_cy = init_dy
                best_cx = init_dx
                best_coarse_sad = 1e30

                for coy_s, cox_s in ti.static(((0, 0), (-2, 0), (2, 0), (0, -2), (0, 2))):
                    soy = init_dy + coy_s
                    sox = init_dx + cox_s
                    sad = 0.0
                    
                    # Loop over win_radius dynamically with stride
                    oy = -win_radius
                    while oy <= win_radius:
                        ox = -win_radius
                        while ox <= win_radius:
                            yy_i = border_margin + gy * grid_step + oy
                            xx_i = border_margin + gx * grid_step + ox
                            diff = _bm_read_i32(next, yy_i + soy, xx_i + sox, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                            sad += ti.abs(diff)
                            ox += stride
                        oy += stride

                    if sad < best_coarse_sad:
                        best_coarse_sad = sad
                        best_cy = soy
                        best_cx = sox

                # 2. Fine Integer Search (Cross Pattern around best coarse, 5 points)
                best_fy = best_cy
                best_fx = best_cx
                best_fine_sad = 1e30

                for foy_s, fox_s in ti.static(((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))):
                    soy = best_cy + foy_s
                    sox = best_cx + fox_s
                    sad = 0.0
                    
                    oy = -win_radius
                    while oy <= win_radius:
                        ox = -win_radius
                        while ox <= win_radius:
                            yy_i = border_margin + gy * grid_step + oy
                            xx_i = border_margin + gx * grid_step + ox
                            diff = _bm_read_i32(next, yy_i + soy, xx_i + sox, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                            sad += ti.abs(diff)
                            ox += stride
                        oy += stride

                    if sad < best_fine_sad:
                        best_fine_sad = sad
                        best_fy = soy
                        best_fx = sox

                # 3. 2D Parabolic Fit sub-pixel refinement
                sad_center = best_fine_sad
                sad_left = 0.0
                sad_right = 0.0
                sad_up = 0.0
                sad_down = 0.0

                # Evaluate Left (best_fx - 1, best_fy)
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy, xx_i + best_fx - 1, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_left += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Right (best_fx + 1, best_fy)
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy, xx_i + best_fx + 1, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_right += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Up (best_fx, best_fy - 1)
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy - 1, xx_i + best_fx, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_up += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Down (best_fx, best_fy + 1)
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy + 1, xx_i + best_fx, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_down += ti.abs(diff)
                        ox += stride
                    oy += stride

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

                # Calculate approximate number of points evaluated
                pts_side = (win_radius * 2) // stride + 1
                patch_area = ti.cast(pts_side * pts_side, ti.f32)
                residual = sad_center / patch_area

                grid_flow[gy, gx, 0] = dx
                grid_flow[gy, gx, 1] = dy
                grid_flow[gy, gx, 2] = 1.0

                motion2 = dx * dx + dy * dy
                med_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.04
                high_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.20
                cls = 0.0
                if motion2 > med_thr or residual > 10.0:
                    cls = 1.0
                if motion2 > high_thr or residual > 22.0:
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
        stride = 2

        for gy, gx in ti.ndrange(grid_h, grid_w):
            cls = ti.cast(grid_meta[gy, gx, 2], ti.i32)
            if cls >= class_threshold and grid_flow[gy, gx, 2] > 0.5:
                dx_init = grid_flow[gy, gx, 0]
                dy_init = grid_flow[gy, gx, 1]
                best_fx = ti.cast(ti.round(dx_init), ti.i32)
                best_fy = ti.cast(ti.round(dy_init), ti.i32)

                sad_center = 0.0
                sad_left = 0.0
                sad_right = 0.0
                sad_up = 0.0
                sad_down = 0.0

                # Evaluate Center
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy, xx_i + best_fx, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_center += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Left
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy, xx_i + best_fx - 1, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_left += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Right
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy, xx_i + best_fx + 1, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_right += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Up
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy - 1, xx_i + best_fx, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_up += ti.abs(diff)
                        ox += stride
                    oy += stride

                # Evaluate Down
                oy = -win_radius
                while oy <= win_radius:
                    ox = -win_radius
                    while ox <= win_radius:
                        yy_i = border_margin + gy * grid_step + oy
                        xx_i = border_margin + gx * grid_step + ox
                        diff = _bm_read_i32(next, yy_i + best_fy + 1, xx_i + best_fx, h, w) - _bm_read_i32(prev, yy_i, xx_i, h, w)
                        sad_down += ti.abs(diff)
                        ox += stride
                    oy += stride

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

                pts_side = (win_radius * 2) // stride + 1
                patch_area = ti.cast(pts_side * pts_side, ti.f32)
                residual = sad_center / patch_area

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
            fx_raw = ti.max(0.0, ti.min(gx_f - ti.cast(gx0, ti.f32), 1.0))
            fy_raw = ti.max(0.0, ti.min(gy_f - ti.cast(gy0, ti.f32), 1.0))

            sx = fx_raw * fx_raw * (3.0 - 2.0 * fx_raw)
            sy = fy_raw * fy_raw * (3.0 - 2.0 * fy_raw)
            w00 = (1.0 - sx) * (1.0 - sy) * grid_flow[gy0, gx0, 2]
            w01 = sx * (1.0 - sy) * grid_flow[gy0, gx1, 2]
            w10 = (1.0 - sx) * sy * grid_flow[gy1, gx0, 2]
            w11 = sx * sy * grid_flow[gy1, gx1, 2]
            wt = w00 + w01 + w10 + w11

            if wt > 1e-6:
                flow_out[y, x, 0] = (
                    grid_flow[gy0, gx0, 0] * w00
                    + grid_flow[gy0, gx1, 0] * w01
                    + grid_flow[gy1, gx0, 0] * w10
                    + grid_flow[gy1, gx1, 0] * w11
                ) / wt
                flow_out[y, x, 1] = (
                    grid_flow[gy0, gx0, 1] * w00
                    + grid_flow[gy0, gx1, 1] * w01
                    + grid_flow[gy1, gx0, 1] * w10
                    + grid_flow[gy1, gx1, 1] * w11
                ) / wt
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
                best_x = 0.0
                best_y = 0.0
                found = 0
                best_dist = 999999.0
                for oy, ox in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                    ny = _bm_clamp(gy + oy, 0, grid_h - 1)
                    nx = _bm_clamp(gx + ox, 0, grid_w - 1)
                    if grid_flow[ny, nx, 2] > 0.5:
                        dy = ti.cast(oy, ti.f32)
                        dx = ti.cast(ox, ti.f32)
                        dist = dx * dx + dy * dy
                        if found == 0 or dist < best_dist:
                            found = 1
                            best_dist = dist
                            best_x = grid_flow[ny, nx, 0]
                            best_y = grid_flow[ny, nx, 1]
                flow_out[y, x, 0] = best_x
                flow_out[y, x, 1] = best_y

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
            else:
                found = 0
                best_dist = 999999.0
                for oy, ox in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                    ny = _bm_clamp(gy + oy, 0, grid_h - 1)
                    nx = _bm_clamp(gx + ox, 0, grid_w - 1)
                    if grid_flow[ny, nx, 2] > 0.5:
                        dy = ti.cast(oy, ti.f32)
                        dx = ti.cast(ox, ti.f32)
                        dist = dx * dx + dy * dy
                        if found == 0 or dist < best_dist:
                            found = 1
                            best_dist = dist
                            fx = grid_flow[ny, nx, 0]
                            fy = grid_flow[ny, nx, 1]

            if max_flow_px > 0.0:
                mag = ti.sqrt(fx * fx + fy * fy)
                if mag > max_flow_px:
                    scale = max_flow_px / ti.max(mag, 1e-6)
                    fx *= scale
                    fy *= scale
            flow_out[y, x, 0] = fx
            flow_out[y, x, 1] = fy
