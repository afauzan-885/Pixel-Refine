"""Batch-native Lucas--Kanade kernels.

The regular LK graphs operate on one tile at a time.  These kernels add a
leading batch dimension while keeping the numerical body of the established
graphs unchanged.  The runtime groups only tiles with identical read shapes,
so no padding or cross-tile state is introduced.
"""

import importlib
import os

if os.environ.get("AOT_MODE", "1") == "0":
    ti = importlib.import_module("taichi")
    common = importlib.import_module("taichi_vision.taichi_algorithm.common")
else:  # pragma: no cover - runtime loads the compiled TCM archive
    ti = None
    common = None


if ti is not None:

    @ti.func
    def _batch_clamp(v: ti.i32, lo: ti.i32, hi: ti.i32) -> ti.i32:
        return ti.max(lo, ti.min(v, hi))

    @ti.func
    def _batch_reflect_idx(v: ti.i32, n: ti.i32) -> ti.i32:
        # Branchless BORDER_REFLECT_101, matching common.reflect_idx.  A
        # branchless form is required because Taichi 1.7.4 does not permit an
        # early return from a non-static conditional inside a ti.func.
        value = ti.abs(v)
        diff = value - (n - 1)
        reflected = value - 2 * ti.max(0, diff)
        return ti.max(0, ti.min(reflected, n - 1))

    @ti.func
    def _batch_sample(
        image: ti.types.ndarray(),
        batch: ti.i32,
        y: ti.f32,
        x: ti.f32,
        height: ti.i32,
        width: ti.i32,
    ) -> ti.f32:
        x0 = _batch_clamp(ti.cast(ti.floor(x), ti.i32), 0, width - 1)
        y0 = _batch_clamp(ti.cast(ti.floor(y), ti.i32), 0, height - 1)
        x1 = _batch_clamp(x0 + 1, 0, width - 1)
        y1 = _batch_clamp(y0 + 1, 0, height - 1)
        fx = x - ti.cast(x0, ti.f32)
        fy = y - ti.cast(y0, ti.f32)
        v00 = image[batch, y0, x0]
        v01 = image[batch, y0, x1]
        v10 = image[batch, y1, x0]
        v11 = image[batch, y1, x1]
        return (1.0 - fy) * ((1.0 - fx) * v00 + fx * v01) + fy * (
            (1.0 - fx) * v10 + fx * v11
        )

    @ti.func
    def _batch_read_i32(
        image: ti.types.ndarray(),
        batch: ti.i32,
        y: ti.i32,
        x: ti.i32,
        height: ti.i32,
        width: ti.i32,
    ) -> ti.f32:
        return image[
            batch,
            _batch_clamp(y, 0, height - 1),
            _batch_clamp(x, 0, width - 1),
        ]

    @ti.func
    def _batch_sample_flow(
        flow: ti.types.ndarray(),
        batch: ti.i32,
        y: ti.f32,
        x: ti.f32,
        height: ti.i32,
        width: ti.i32,
        channel: ti.i32,
    ) -> ti.f32:
        x0 = _batch_clamp(ti.cast(ti.floor(x), ti.i32), 0, width - 1)
        y0 = _batch_clamp(ti.cast(ti.floor(y), ti.i32), 0, height - 1)
        x1 = _batch_clamp(x0 + 1, 0, width - 1)
        y1 = _batch_clamp(y0 + 1, 0, height - 1)
        fx = x - ti.cast(x0, ti.f32)
        fy = y - ti.cast(y0, ti.f32)
        v00 = flow[batch, y0, x0, channel]
        v01 = flow[batch, y0, x1, channel]
        v10 = flow[batch, y1, x0, channel]
        v11 = flow[batch, y1, x1, channel]
        return (1.0 - fy) * ((1.0 - fx) * v00 + fx * v01) + fy * (
            (1.0 - fx) * v10 + fx * v11
        )

    @ti.func
    def _batch_cubic_weight(t: ti.f32) -> ti.f32:
        # Catmull-Rom style cubic, matching common.cubic_hermite_weights used
        # by the scalar flow upsample graph.
        a = -0.75
        t2 = t * t
        t3 = t2 * t
        return ti.Vector([
            a * (-t3 + 2.0 * t2 - t),
            (a + 2.0) * t3 - (a + 3.0) * t2 + 1.0,
            -(a + 2.0) * t3 + (2.0 * a + 3.0) * t2 - a * t,
            a * (t3 - t2),
        ])

    @ti.func
    def _batch_bicubic_flow(
        flow: ti.types.ndarray(),
        batch: ti.i32,
        x: ti.f32,
        y: ti.f32,
        height: ti.i32,
        width: ti.i32,
        channel: ti.i32,
    ) -> ti.f32:
        ix = ti.cast(ti.floor(x), ti.i32)
        iy = ti.cast(ti.floor(y), ti.i32)
        wx = _batch_cubic_weight(x - ti.cast(ix, ti.f32))
        wy = _batch_cubic_weight(y - ti.cast(iy, ti.f32))
        value = 0.0
        for j in ti.static(range(4)):
            row = 0.0
            sy = _batch_reflect_idx(iy - 1 + j, height)
            for i in ti.static(range(4)):
                sx = _batch_reflect_idx(ix - 1 + i, width)
                row += flow[batch, sy, sx, channel] * wx[i]
            value += row * wy[j]
        return value

    @ti.kernel
    def _batch_downsample_2x_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
    ):
        batch = src.shape[0]
        height = src.shape[1]
        width = src.shape[2]
        weights = ti.static([1.0, 4.0, 6.0, 4.0, 1.0])
        for b, r, c in ti.ndrange(batch, dst.shape[1], dst.shape[2]):
            y_src = r * 2
            x_src = c * 2
            value = 0.0
            for j in ti.static(range(-2, 3)):
                for i in ti.static(range(-2, 3)):
                    sy = _batch_reflect_idx(y_src + j, height)
                    sx = _batch_reflect_idx(x_src + i, width)
                    value += src[b, sy, sx] * weights[j + 2] * weights[i + 2]
            dst[b, r, c] = value / 256.0

    @ti.kernel
    def _batch_upsample_flow_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=4),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
        scale: ti.f32,
    ):
        batch = src.shape[0]
        height = src.shape[1]
        width = src.shape[2]
        dst_height = dst.shape[1]
        dst_width = dst.shape[2]
        for b, r, c in ti.ndrange(batch, dst_height, dst_width):
            x = ti.cast(c, ti.f32) * ti.cast(width, ti.f32) / ti.cast(dst_width, ti.f32)
            y = ti.cast(r, ti.f32) * ti.cast(height, ti.f32) / ti.cast(dst_height, ti.f32)
            dst[b, r, c, 0] = _batch_bicubic_flow(src, b, x, y, height, width, 0) * scale
            dst[b, r, c, 1] = _batch_bicubic_flow(src, b, x, y, height, width, 1) * scale

    @ti.kernel
    def _batch_zero_flow_kernel(flow: ti.types.ndarray(dtype=ti.f32, ndim=4)):
        for b, y, x in ti.ndrange(flow.shape[0], flow.shape[1], flow.shape[2]):
            flow[b, y, x, 0] = 0.0
            flow[b, y, x, 1] = 0.0

    @ti.kernel
    def _batch_grid_track_kernel(
        prev: ti.types.ndarray(dtype=ti.f32, ndim=3),
        next: ti.types.ndarray(dtype=ti.f32, ndim=3),
        init_flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        grid_flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        grid_meta: ti.types.ndarray(dtype=ti.f32, ndim=4),
        grid_step: ti.i32,
        border_margin: ti.i32,
        win_radius: ti.i32,
        iterations: ti.i32,
        epsilon: ti.f32,
    ):
        batch = prev.shape[0]
        height = prev.shape[1]
        width = prev.shape[2]
        grid_height = grid_flow.shape[1]
        grid_width = grid_flow.shape[2]

        for b, gy, gx in ti.ndrange(batch, grid_height, grid_width):
            px = ti.cast(border_margin + gx * grid_step, ti.f32)
            py = ti.cast(border_margin + gy * grid_step, ti.f32)
            max_flow = ti.cast(grid_step * 2 + win_radius * 2, ti.f32)
            max_step = ti.cast(ti.max(2, grid_step), ti.f32)
            grid_flow[b, gy, gx, 0] = 0.0
            grid_flow[b, gy, gx, 1] = 0.0
            grid_flow[b, gy, gx, 2] = 0.0
            grid_meta[b, gy, gx, 0] = 0.0
            grid_meta[b, gy, gx, 1] = 0.0
            grid_meta[b, gy, gx, 2] = 2.0
            grid_meta[b, gy, gx, 3] = 0.0
            if px < ti.cast(width - border_margin, ti.f32) and py < ti.cast(
                height - border_margin, ti.f32
            ):
                dx = _batch_sample_flow(init_flow, b, py, px, height, width, 0)
                dy = _batch_sample_flow(init_flow, b, py, px, height, width, 1)
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
                            (-win_radius, win_radius + 1),
                            (-win_radius, win_radius + 1),
                        ):
                            yy_i = border_margin + gy * grid_step + oy
                            xx_i = border_margin + gx * grid_step + ox
                            yy = ti.cast(yy_i, ti.f32)
                            xx = ti.cast(xx_i, ti.f32)
                            nx = xx + dx
                            ny = yy + dy
                            ix = (
                                _batch_read_i32(prev, b, yy_i, xx_i + 1, height, width)
                                - _batch_read_i32(prev, b, yy_i, xx_i - 1, height, width)
                            ) * 0.5
                            iy = (
                                _batch_read_i32(prev, b, yy_i + 1, xx_i, height, width)
                                - _batch_read_i32(prev, b, yy_i - 1, xx_i, height, width)
                            ) * 0.5
                            err = _batch_sample(next, b, ny, nx, height, width) - _batch_read_i32(
                                prev, b, yy_i, xx_i, height, width
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
                    grid_flow[b, gy, gx, 0] = dx
                    grid_flow[b, gy, gx, 1] = dy
                    grid_flow[b, gy, gx, 2] = 1.0
                    motion2 = dx * dx + dy * dy
                    med_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.04
                    high_thr = ti.cast(grid_step * grid_step, ti.f32) * 0.20
                    cls = 0.0
                    if motion2 > med_thr or residual > 10.0:
                        cls = 1.0
                    if motion2 > high_thr or residual > 22.0 or det_last < 1e-3:
                        cls = 2.0
                    grid_meta[b, gy, gx, 0] = residual
                    grid_meta[b, gy, gx, 1] = det_last
                    grid_meta[b, gy, gx, 2] = cls
                    grid_meta[b, gy, gx, 3] = motion2

    @ti.kernel
    def _batch_dense_interpolate_kernel(
        grid_flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        flow_out: ti.types.ndarray(dtype=ti.f32, ndim=4),
        grid_step: ti.i32,
        border_margin: ti.i32,
        overlap: ti.f32,
    ):
        # Smoothstep is the established dense interpolation path.  Keep the
        # overlap argument in the ABI for parity with the scalar graph.
        batch = grid_flow.shape[0]
        grid_height = grid_flow.shape[1]
        grid_width = grid_flow.shape[2]
        height = flow_out.shape[1]
        width = flow_out.shape[2]
        inv_step = 1.0 / ti.cast(grid_step, ti.f32)
        for b, y, x in ti.ndrange(batch, height, width):
            gx_f = ti.cast(x - border_margin, ti.f32) * inv_step
            gy_f = ti.cast(y - border_margin, ti.f32) * inv_step
            gx0 = _batch_clamp(ti.cast(ti.floor(gx_f), ti.i32), 0, grid_width - 1)
            gy0 = _batch_clamp(ti.cast(ti.floor(gy_f), ti.i32), 0, grid_height - 1)
            gx1 = _batch_clamp(gx0 + 1, 0, grid_width - 1)
            gy1 = _batch_clamp(gy0 + 1, 0, grid_height - 1)
            fx_raw = ti.max(0.0, ti.min(gx_f - ti.cast(gx0, ti.f32), 1.0))
            fy_raw = ti.max(0.0, ti.min(gy_f - ti.cast(gy0, ti.f32), 1.0))
            sx = fx_raw * fx_raw * (3.0 - 2.0 * fx_raw)
            sy = fy_raw * fy_raw * (3.0 - 2.0 * fy_raw)
            w00 = (1.0 - sx) * (1.0 - sy) * grid_flow[b, gy0, gx0, 2]
            w01 = sx * (1.0 - sy) * grid_flow[b, gy0, gx1, 2]
            w10 = (1.0 - sx) * sy * grid_flow[b, gy1, gx0, 2]
            w11 = sx * sy * grid_flow[b, gy1, gx1, 2]
            total = w00 + w01 + w10 + w11
            if total > 1e-6:
                flow_out[b, y, x, 0] = (
                    grid_flow[b, gy0, gx0, 0] * w00
                    + grid_flow[b, gy0, gx1, 0] * w01
                    + grid_flow[b, gy1, gx0, 0] * w10
                    + grid_flow[b, gy1, gx1, 0] * w11
                ) / total
                flow_out[b, y, x, 1] = (
                    grid_flow[b, gy0, gx0, 1] * w00
                    + grid_flow[b, gy0, gx1, 1] * w01
                    + grid_flow[b, gy1, gx0, 1] * w10
                    + grid_flow[b, gy1, gx1, 1] * w11
                ) / total
            else:
                flow_out[b, y, x, 0] = 0.0
                flow_out[b, y, x, 1] = 0.0

    @ti.kernel
    def _batch_scatter_core_kernel(
        flow_batch: ti.types.ndarray(dtype=ti.f32, ndim=4),
        flow_out: ti.types.ndarray(dtype=ti.f32, ndim=3),
        offsets: ti.types.ndarray(dtype=ti.i32, ndim=2),
    ):
        """Copy each packed tile's valid core into one resident frame.

        ``offsets[b]`` is ``(src_y, src_x, dst_y, dst_x, height, width)``.
        The kernel is deliberately independent for every output pixel: cores
        are non-overlapping by construction, so no inter-tile atomics or
        barriers are required.  This is the final pre-communication step for
        the batch path and lets the host perform one readback for all tiles.
        """
        batch = flow_batch.shape[0]
        tile_height = flow_batch.shape[1]
        tile_width = flow_batch.shape[2]
        for b, y, x, channel in ti.ndrange(
            batch, tile_height, tile_width, 2
        ):
            core_height = offsets[b, 4]
            core_width = offsets[b, 5]
            if y < core_height and x < core_width:
                src_y = offsets[b, 0] + y
                src_x = offsets[b, 1] + x
                dst_y = offsets[b, 2] + y
                dst_x = offsets[b, 3] + x
                if (
                    src_y >= 0
                    and src_y < tile_height
                    and src_x >= 0
                    and src_x < tile_width
                    and dst_y >= 0
                    and dst_y < flow_out.shape[0]
                    and dst_x >= 0
                    and dst_x < flow_out.shape[1]
                ):
                    flow_out[dst_y, dst_x, channel] = flow_batch[
                        b, src_y, src_x, channel
                    ]
