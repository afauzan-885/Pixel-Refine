"""
Lucas-Kanade Optical Flow - Grid Dense Variant
==============================================

OpenCV-inspired Lucas-Kanade tracking with internal grid point generation.
The public API intentionally mirrors cv2.calcOpticalFlowPyrLK, but returns a
dense flow map shaped (H, W, 2) for Pixel Refine alignment workflows.

Design notes:
  - No caller-supplied points are required.
  - Grid points are generated internally.
  - Sparse LK displacement is fused into a dense flow using weighted splatting.
  - Tile blending uses 35% overlap semantics through a Hanning-style weight.
"""

import importlib
import os

import numpy as np

try:
    import cv2
except ImportError:  # pragma: no cover - optional CPU fallback only
    cv2 = None

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass


DEFAULT_GRID_STEP = 48
DEFAULT_BORDER_MARGIN = 8
DEFAULT_OVERLAP = 0.35
DEFAULT_WIN_SIZE = 13
DEFAULT_MAX_LEVEL = 2
DEFAULT_ITERATIONS = 8
DEFAULT_EPSILON = 0.03
DEFAULT_ADAPTIVE = False
DEFAULT_ADAPTIVE_THRESHOLD = 1
DEFAULT_MOTION_MODE = "fast"


def _as_gray_f32(image):
    if image.ndim == 3:
        if cv2 is None:
            image = image.mean(axis=2)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.ascontiguousarray(image, dtype=np.float32)


def _cpu_grid_points(width, height, grid_step, border_margin):
    step = max(4, int(grid_step))
    margin = max(0, int(border_margin))
    x0 = min(margin, max(0, width - 1))
    y0 = min(margin, max(0, height - 1))
    x1 = max(x0 + 1, width - margin)
    y1 = max(y0 + 1, height - margin)
    xs = np.arange(x0, x1, step, dtype=np.float32)
    ys = np.arange(y0, y1, step, dtype=np.float32)
    if xs.size == 0 or ys.size == 0:
        return None
    gx, gy = np.meshgrid(xs, ys)
    return np.column_stack((gx.ravel(), gy.ravel())).reshape(-1, 1, 2)


def _cpu_dense_from_sparse(height, width, source, target, grid_step):
    flow = np.zeros((height, width, 2), dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)
    radius = max(2, int(round(grid_step * DEFAULT_OVERLAP)))
    displacement = target - source

    for (x_f, y_f), (dx, dy) in zip(source, displacement):
        cx = int(round(x_f))
        cy = int(round(y_f))
        y0 = max(0, cy - radius)
        y1 = min(height, cy + radius + 1)
        x0 = max(0, cx - radius)
        x1 = min(width, cx + radius + 1)
        for y in range(y0, y1):
            wy = 0.5 + 0.5 * np.cos(np.pi * (y - cy) / max(1, radius))
            for x in range(x0, x1):
                wx = 0.5 + 0.5 * np.cos(np.pi * (x - cx) / max(1, radius))
                weight = float(max(0.0, wx * wy))
                flow[y, x, 0] += dx * weight
                flow[y, x, 1] += dy * weight
                weights[y, x] += weight

    valid = weights > 1e-6
    if np.any(valid):
        flow[valid, 0] /= weights[valid]
        flow[valid, 1] /= weights[valid]
    if cv2 is not None:
        flow = cv2.GaussianBlur(flow, (5, 5), 0)
    return flow


def _cpu_calc_pyr_lk_dense(
    prev,
    next,
    grid_step=DEFAULT_GRID_STEP,
    border_margin=DEFAULT_BORDER_MARGIN,
    win_size=DEFAULT_WIN_SIZE,
    max_level=DEFAULT_MAX_LEVEL,
    criteria=None,
):
    if cv2 is None:
        raise ImportError("cv2 is required for CPU Lucas-Kanade fallback")

    prev_f = _as_gray_f32(prev)
    next_f = _as_gray_f32(next)
    height, width = prev_f.shape[:2]
    points = _cpu_grid_points(width, height, grid_step, border_margin)
    if points is None or len(points) < 4:
        return np.zeros((height, width, 2), dtype=np.float32)

    if criteria is None:
        criteria = (
            cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
            DEFAULT_ITERATIONS,
            DEFAULT_EPSILON,
        )

    win_size = max(5, int(win_size))
    if win_size % 2 == 0:
        win_size += 1
    next_points, status, _ = cv2.calcOpticalFlowPyrLK(
        prev_f.astype(np.uint8, copy=False),
        next_f.astype(np.uint8, copy=False),
        points,
        None,
        winSize=(win_size, win_size),
        maxLevel=max(0, int(max_level)),
        criteria=criteria,
    )
    if next_points is None or status is None:
        return np.zeros((height, width, 2), dtype=np.float32)

    valid = status.reshape(-1).astype(bool)
    source = points.reshape(-1, 2)[valid]
    target = next_points.reshape(-1, 2)[valid]
    if len(source) < 4:
        return np.zeros((height, width, 2), dtype=np.float32)
    return _cpu_dense_from_sparse(height, width, source, target, grid_step)


if TAICHI_AVAILABLE:

    @ti.func
    def _lk_clamp(v: ti.i32, lo: ti.i32, hi: ti.i32) -> ti.i32:
        return ti.max(lo, ti.min(v, hi))

    @ti.func
    def _lk_sample(
        img: ti.types.ndarray(), y: ti.f32, x: ti.f32, h: ti.i32, w: ti.i32
    ) -> ti.f32:
        x0 = _lk_clamp(ti.cast(ti.floor(x), ti.i32), 0, w - 1)
        y0 = _lk_clamp(ti.cast(ti.floor(y), ti.i32), 0, h - 1)
        x1 = _lk_clamp(x0 + 1, 0, w - 1)
        y1 = _lk_clamp(y0 + 1, 0, h - 1)
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
    def _lk_read_i32(
        img: ti.types.ndarray(), y: ti.i32, x: ti.i32, h: ti.i32, w: ti.i32
    ) -> ti.f32:
        yy = _lk_clamp(y, 0, h - 1)
        xx = _lk_clamp(x, 0, w - 1)
        return img[yy, xx]

    @ti.func
    def _lk_sample_flow(
        flow: ti.types.ndarray(),
        y: ti.f32,
        x: ti.f32,
        h: ti.i32,
        w: ti.i32,
        ch: ti.i32,
    ) -> ti.f32:
        x0 = _lk_clamp(ti.cast(ti.floor(x), ti.i32), 0, w - 1)
        y0 = _lk_clamp(ti.cast(ti.floor(y), ti.i32), 0, h - 1)
        x1 = _lk_clamp(x0 + 1, 0, w - 1)
        y1 = _lk_clamp(y0 + 1, 0, h - 1)
        fx = x - ti.cast(x0, ti.f32)
        fy = y - ti.cast(y0, ti.f32)
        v00 = flow[y0, x0, ch]
        v01 = flow[y0, x1, ch]
        v10 = flow[y1, x0, ch]
        v11 = flow[y1, x1, ch]
        return (1.0 - fy) * ((1.0 - fx) * v00 + fx * v01) + fy * (
            (1.0 - fx) * v10 + fx * v11
        )

    @ti.kernel
    def _lk_zero_flow_kernel(flow: ti.types.ndarray()):
        h = flow.shape[0]
        w = flow.shape[1]
        for y, x in ti.ndrange(h, w):
            flow[y, x, 0] = 0.0
            flow[y, x, 1] = 0.0

    @ti.kernel
    def _lk_zero_stats_kernel(stats: ti.types.ndarray()):
        n = stats.shape[0]
        for i in range(n):
            stats[i] = 0.0

    @ti.kernel
    def _lk_grid_track_kernel(
        prev: ti.types.ndarray(),
        next: ti.types.ndarray(),
        init_flow: ti.types.ndarray(),
        grid_flow: ti.types.ndarray(),
        grid_meta: ti.types.ndarray(),
        grid_step: ti.i32,
        border_margin: ti.i32,
        win_radius: ti.i32,
        iterations: ti.i32,
        epsilon: ti.f32,
    ):
        h = prev.shape[0]
        w = prev.shape[1]
        grid_h = grid_flow.shape[0]
        grid_w = grid_flow.shape[1]

        for gy, gx in ti.ndrange(grid_h, grid_w):
            px = ti.cast(border_margin + gx * grid_step, ti.f32)
            py = ti.cast(border_margin + gy * grid_step, ti.f32)
            max_flow = ti.cast(grid_step * 2 + win_radius * 2, ti.f32)
            max_step = ti.cast(ti.max(2, grid_step), ti.f32)
            grid_flow[gy, gx, 0] = 0.0
            grid_flow[gy, gx, 1] = 0.0
            grid_flow[gy, gx, 2] = 0.0
            grid_meta[gy, gx, 0] = 0.0
            grid_meta[gy, gx, 1] = 0.0
            grid_meta[gy, gx, 2] = 2.0
            grid_meta[gy, gx, 3] = 0.0
            if px < ti.cast(w - border_margin, ti.f32) and py < ti.cast(
                h - border_margin, ti.f32
            ):
                dx = _lk_sample_flow(init_flow, py, px, h, w, 0)
                dy = _lk_sample_flow(init_flow, py, px, h, w, 1)
                valid = 1
                active = 1
                residual = 0.0
                det_last = 0.0

                for _it in range(iterations):
                    if active == 1:
                        gxx = 0.0
                        gxy = 0.0
                        gyy = 0.0
                        bx = 0.0
                        by = 0.0
                        err_abs = 0.0

                        for oy, ox in ti.ndrange(
                            (-win_radius, win_radius + 1), (-win_radius, win_radius + 1)
                        ):
                            yy_i = border_margin + gy * grid_step + oy
                            xx_i = border_margin + gx * grid_step + ox
                            yy = ti.cast(yy_i, ti.f32)
                            xx = ti.cast(xx_i, ti.f32)
                            nx = xx + dx
                            ny = yy + dy
                            ix = (
                                _lk_read_i32(prev, yy_i, xx_i + 1, h, w)
                                - _lk_read_i32(prev, yy_i, xx_i - 1, h, w)
                            ) * 0.5
                            iy = (
                                _lk_read_i32(prev, yy_i + 1, xx_i, h, w)
                                - _lk_read_i32(prev, yy_i - 1, xx_i, h, w)
                            ) * 0.5
                            err = _lk_sample(next, ny, nx, h, w) - _lk_read_i32(
                                prev, yy_i, xx_i, h, w
                            )
                            gxx += ix * ix
                            gxy += ix * iy
                            gyy += iy * iy
                            bx += ix * err
                            by += iy * err
                            err_abs += ti.abs(err)

                        det = gxx * gyy - gxy * gxy
                        det_last = ti.abs(det)
                        patch_area = ti.cast(
                            (win_radius * 2 + 1) * (win_radius * 2 + 1), ti.f32
                        )
                        residual = err_abs / patch_area
                        if ti.abs(det) < 1e-4:
                            valid = 0
                            active = 0
                        else:
                            inv_det = 1.0 / det
                            step_x = (-gyy * bx + gxy * by) * inv_det
                            step_y = (gxy * bx - gxx * by) * inv_det
                            step_x = ti.max(-max_step, ti.min(max_step, step_x))
                            step_y = ti.max(-max_step, ti.min(max_step, step_y))
                            dx += step_x
                            dy += step_y
                            dx = ti.max(-max_flow, ti.min(max_flow, dx))
                            dy = ti.max(-max_flow, ti.min(max_flow, dy))
                            if step_x * step_x + step_y * step_y < epsilon * epsilon:
                                active = 0

                if valid == 1:
                    grid_flow[gy, gx, 0] = dx
                    grid_flow[gy, gx, 1] = dy
                    grid_flow[gy, gx, 2] = 1.0
                    motion2 = dx * dx + dy * dy
                    med_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.04
                    high_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.20
                    cls = 0.0
                    if motion2 > med_thr or residual > 10.0:
                        cls = 1.0
                    if motion2 > high_thr or residual > 22.0 or det_last < 1e-3:
                        cls = 2.0
                    grid_meta[gy, gx, 0] = residual
                    grid_meta[gy, gx, 1] = det_last
                    grid_meta[gy, gx, 2] = cls
                    grid_meta[gy, gx, 3] = motion2

    @ti.kernel
    def _lk_adaptive_refine_kernel(
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

        for gy, gx in ti.ndrange(grid_h, grid_w):
            cls = ti.cast(grid_meta[gy, gx, 2], ti.i32)
            if cls >= class_threshold and grid_flow[gy, gx, 2] > 0.5:
                max_flow = ti.cast(grid_step * 2 + win_radius * 2, ti.f32)
                max_step = ti.cast(ti.max(2, grid_step), ti.f32)
                dx = grid_flow[gy, gx, 0]
                dy = grid_flow[gy, gx, 1]
                active = 1
                valid = 1
                residual = grid_meta[gy, gx, 0]
                det_last = grid_meta[gy, gx, 1]

                for _it in range(iterations):
                    if active == 1:
                        gxx = 0.0
                        gxy = 0.0
                        gyy = 0.0
                        bx = 0.0
                        by = 0.0
                        err_abs = 0.0

                        for oy, ox in ti.ndrange(
                            (-win_radius, win_radius + 1), (-win_radius, win_radius + 1)
                        ):
                            yy_i = border_margin + gy * grid_step + oy
                            xx_i = border_margin + gx * grid_step + ox
                            yy = ti.cast(yy_i, ti.f32)
                            xx = ti.cast(xx_i, ti.f32)
                            nx = xx + dx
                            ny = yy + dy
                            ix = (
                                _lk_read_i32(prev, yy_i, xx_i + 1, h, w)
                                - _lk_read_i32(prev, yy_i, xx_i - 1, h, w)
                            ) * 0.5
                            iy = (
                                _lk_read_i32(prev, yy_i + 1, xx_i, h, w)
                                - _lk_read_i32(prev, yy_i - 1, xx_i, h, w)
                            ) * 0.5
                            err = _lk_sample(next, ny, nx, h, w) - _lk_read_i32(
                                prev, yy_i, xx_i, h, w
                            )
                            gxx += ix * ix
                            gxy += ix * iy
                            gyy += iy * iy
                            bx += ix * err
                            by += iy * err
                            err_abs += ti.abs(err)

                        det = gxx * gyy - gxy * gxy
                        det_last = ti.abs(det)
                        patch_area = ti.cast(
                            (win_radius * 2 + 1) * (win_radius * 2 + 1), ti.f32
                        )
                        residual = err_abs / patch_area
                        if ti.abs(det) < 1e-4:
                            valid = 0
                            active = 0
                        else:
                            inv_det = 1.0 / det
                            step_x = (-gyy * bx + gxy * by) * inv_det
                            step_y = (gxy * bx - gxx * by) * inv_det
                            step_x = ti.max(-max_step, ti.min(max_step, step_x))
                            step_y = ti.max(-max_step, ti.min(max_step, step_y))
                            dx += step_x
                            dy += step_y
                            dx = ti.max(-max_flow, ti.min(max_flow, dx))
                            dy = ti.max(-max_flow, ti.min(max_flow, dy))
                            if step_x * step_x + step_y * step_y < epsilon * epsilon:
                                active = 0

                if valid == 1:
                    grid_flow[gy, gx, 0] = dx
                    grid_flow[gy, gx, 1] = dy
                    grid_meta[gy, gx, 0] = residual
                    grid_meta[gy, gx, 1] = det_last
                    grid_meta[gy, gx, 3] = dx * dx + dy * dy

    @ti.kernel
    def _lk_motion_stats_kernel(
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
    def _lk_dense_interpolate_kernel(
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
            gx0 = _lk_clamp(ti.cast(ti.floor(gx_f), ti.i32), 0, grid_w - 1)
            gy0 = _lk_clamp(ti.cast(ti.floor(gy_f), ti.i32), 0, grid_h - 1)
            gx1 = _lk_clamp(gx0 + 1, 0, grid_w - 1)
            gy1 = _lk_clamp(gy0 + 1, 0, grid_h - 1)
            fx_raw = ti.max(0.0, ti.min(gx_f - ti.cast(gx0, ti.f32), 1.0))
            fy_raw = ti.max(0.0, ti.min(gy_f - ti.cast(gy0, ti.f32), 1.0))

            # Full bilinear interpolation between compact grid vectors.
            # Smoothstep is used as a polynomial Hanning-like transition:
            # cheap on GPU and no trig/accumulator pass.
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
    def _lk_dense_blocky_kernel(
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
            gx = _lk_clamp(ti.cast(ti.floor(gx_f + 0.5), ti.i32), 0, grid_w - 1)
            gy = _lk_clamp(ti.cast(ti.floor(gy_f + 0.5), ti.i32), 0, grid_h - 1)

            if grid_flow[gy, gx, 2] > 0.5:
                flow_out[y, x, 0] = grid_flow[gy, gx, 0]
                flow_out[y, x, 1] = grid_flow[gy, gx, 1]
            else:
                best_x = 0.0
                best_y = 0.0
                found = 0
                best_dist = 999999.0
                for oy, ox in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                    ny = _lk_clamp(gy + oy, 0, grid_h - 1)
                    nx = _lk_clamp(gx + ox, 0, grid_w - 1)
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
    def _lk_dense_blocky_clamped_kernel(
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
            gx = _lk_clamp(ti.cast(ti.floor(gx_f + 0.5), ti.i32), 0, grid_w - 1)
            gy = _lk_clamp(ti.cast(ti.floor(gy_f + 0.5), ti.i32), 0, grid_h - 1)

            fx = 0.0
            fy = 0.0
            if grid_flow[gy, gx, 2] > 0.5:
                fx = grid_flow[gy, gx, 0]
                fy = grid_flow[gy, gx, 1]
            else:
                found = 0
                best_dist = 999999.0
                for oy, ox in ti.static(ti.ndrange((-1, 2), (-1, 2))):
                    ny = _lk_clamp(gy + oy, 0, grid_h - 1)
                    nx = _lk_clamp(gx + ox, 0, grid_w - 1)
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


def calcOpticalFlowPyrLK(
    prev,
    next,
    prevPts=None,
    nextPts=None,
    winSize=(13, 13),
    maxLevel=2,
    criteria=None,
    flags=0,
    minEigThreshold=1e-4,
    grid_step=DEFAULT_GRID_STEP,
    border_margin=DEFAULT_BORDER_MARGIN,
    overlap=DEFAULT_OVERLAP,
    adaptive=DEFAULT_ADAPTIVE,
    adaptive_threshold=DEFAULT_ADAPTIVE_THRESHOLD,
    motion_mode=DEFAULT_MOTION_MODE,
    dense_mode="smooth",
    return_diagnostics=False,
    buffer_provider="pool",
):
    """Dense grid Lucas-Kanade flow with cv2-like name and no point setup."""
    if not TAICHI_AVAILABLE:
        result = _cpu_calc_pyr_lk_dense(
            prev,
            next,
            grid_step=grid_step,
            border_margin=border_margin,
            win_size=winSize[0] if isinstance(winSize, tuple) else winSize,
            max_level=maxLevel,
            criteria=criteria,
        )
        if return_diagnostics:
            return result, {
                "motion_mode": str(motion_mode or "fast").lower(),
                "selected_max_level": int(maxLevel),
                "backend": "cpu_fallback",
            }
        return result

    from taichi_vision.taichi_algorithm import common

    prev_np = _as_gray_f32(prev)
    next_np = _as_gray_f32(next)
    h, w = prev_np.shape[:2]
    win = winSize[0] if isinstance(winSize, tuple) else int(winSize)
    win_radius = max(2, int(win) // 2)
    if criteria is None:
        iterations = DEFAULT_ITERATIONS
        epsilon = DEFAULT_EPSILON
    else:
        iterations = int(criteria[1])
        epsilon = float(criteria[2])

    prev_gpu, prev_temp = common.ensure_taichi_field(
        prev_np, dtype=ti.f32, buffer_provider=buffer_provider
    )
    next_gpu, next_temp = common.ensure_taichi_field(
        next_np, dtype=ti.f32, buffer_provider=buffer_provider
    )
    grid_step_i = max(4, int(grid_step))
    margin_i = max(0, int(border_margin))
    grid_w = max(1, (w - 2 * margin_i + grid_step_i - 1) // grid_step_i)
    grid_h = max(1, (h - 2 * margin_i + grid_step_i - 1) // grid_step_i)
    init_flow = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
    grid_flow = common.get_temp_buffer((grid_h, grid_w, 3), ti.f32, buffer_provider)
    grid_meta = common.get_temp_buffer((grid_h, grid_w, 4), ti.f32, buffer_provider)
    flow_out = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    _lk_zero_flow_kernel(init_flow)
    _lk_grid_track_kernel(
        prev_gpu,
        next_gpu,
        init_flow,
        grid_flow,
        grid_meta,
        grid_step_i,
        margin_i,
        win_radius,
        max(1, int(iterations)),
        float(epsilon),
    )
    if adaptive:
        _lk_adaptive_refine_kernel(
            prev_gpu,
            next_gpu,
            grid_flow,
            grid_meta,
            grid_step_i,
            margin_i,
            win_radius + 2,
            max(1, int(iterations) + 2),
            float(epsilon),
            max(1, int(adaptive_threshold)),
        )
    _lk_dense_interpolate_kernel(
        grid_flow, flow_out, grid_step_i, margin_i, float(overlap)
    )
    ti.sync()
    result = flow_out.to_numpy()

    if prev_temp:
        common.release_temp_buffer(prev_gpu)
    if next_temp:
        common.release_temp_buffer(next_gpu)
    common.release_temp_buffer(init_flow)
    common.release_temp_buffer(grid_flow)
    common.release_temp_buffer(grid_meta)
    common.release_temp_buffer(flow_out)
    return result
