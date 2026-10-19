"""Sparse Mesh Grid Warping Kernel & AOT Runtime for Taichi Vision.

Accelerates APAP and non-rigid field image warping by evaluating coordinate
transformations on a coarse sparse grid mesh (e.g. 33x33), followed by single-pass
bilinear interpolation directly on the GPU without intermediate full-resolution
coordinate buffer allocations (saving tens of megabytes of VRAM and memory bandwidth).
"""

import os
import numpy as np
import taichi as ti

@ti.func
def _catmull_rom_1d_vec2(A, B, C, D, t: ti.f32):
    """1D Catmull-Rom cubic spline interpolation for vector2 coordinates."""
    a = -A * 0.5 + B * 1.5 - C * 1.5 + D * 0.5
    b = A - B * 2.5 + C * 2.0 - D * 0.5
    c = -A * 0.5 + C * 0.5
    d = B
    return ((a * t + b) * t + c) * t + d


@ti.func
def _sparse_mesh_coordinate(
    mesh: ti.types.ndarray(),
    u: ti.f32,
    v: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
):
    u0 = int(ti.floor(u))
    v0 = int(ti.floor(v))
    wu = u - ti.floor(u)
    wv = v - ti.floor(v)
    c0 = ti.max(0, u0 - 1)
    c1 = ti.min(w_mesh_max, ti.max(0, u0))
    c2 = ti.min(w_mesh_max, ti.max(0, u0 + 1))
    c3 = ti.min(w_mesh_max, ti.max(0, u0 + 2))
    r0 = ti.max(0, v0 - 1)
    r1 = ti.min(h_mesh_max, ti.max(0, v0))
    r2 = ti.min(h_mesh_max, ti.max(0, v0 + 1))
    r3 = ti.min(h_mesh_max, ti.max(0, v0 + 2))
    row0 = _catmull_rom_1d_vec2(
        mesh[r0, c0], mesh[r0, c1], mesh[r0, c2], mesh[r0, c3], wu
    )
    row1 = _catmull_rom_1d_vec2(
        mesh[r1, c0], mesh[r1, c1], mesh[r1, c2], mesh[r1, c3], wu
    )
    row2 = _catmull_rom_1d_vec2(
        mesh[r2, c0], mesh[r2, c1], mesh[r2, c2], mesh[r2, c3], wu
    )
    row3 = _catmull_rom_1d_vec2(
        mesh[r3, c0], mesh[r3, c1], mesh[r3, c2], mesh[r3, c3], wu
    )
    return _catmull_rom_1d_vec2(row0, row1, row2, row3, wv)


@ti.kernel
def _sparse_mesh_warp_2d_kernel(
    src: ti.types.ndarray(dtype=ti.f32, ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    """Single-pass Catmull-Rom bicubic spline sparse mesh warp for 2D images."""
    for r, c in dst:
        u = u_grid[c]
        v = v_grid[r]

        u0 = int(ti.floor(u))
        v0 = int(ti.floor(v))
        wu = u - ti.floor(u)
        wv = v - ti.floor(v)

        c0 = ti.max(0, u0 - 1)
        c1 = ti.min(w_mesh_max, ti.max(0, u0))
        c2 = ti.min(w_mesh_max, ti.max(0, u0 + 1))
        c3 = ti.min(w_mesh_max, ti.max(0, u0 + 2))

        r0 = ti.max(0, v0 - 1)
        r1 = ti.min(h_mesh_max, ti.max(0, v0))
        r2 = ti.min(h_mesh_max, ti.max(0, v0 + 1))
        r3 = ti.min(h_mesh_max, ti.max(0, v0 + 2))

        row0 = _catmull_rom_1d_vec2(mesh[r0, c0], mesh[r0, c1], mesh[r0, c2], mesh[r0, c3], wu)
        row1 = _catmull_rom_1d_vec2(mesh[r1, c0], mesh[r1, c1], mesh[r1, c2], mesh[r1, c3], wu)
        row2 = _catmull_rom_1d_vec2(mesh[r2, c0], mesh[r2, c1], mesh[r2, c2], mesh[r2, c3], wu)
        row3 = _catmull_rom_1d_vec2(mesh[r3, c0], mesh[r3, c1], mesh[r3, c2], mesh[r3, c3], wu)

        coord = _catmull_rom_1d_vec2(row0, row1, row2, row3, wv)
        src_x = coord[0]
        src_y = coord[1]

        if src_x >= 0.0 and src_x <= w_src_f and src_y >= 0.0 and src_y <= h_src_f:
            sx0 = int(ti.floor(src_x))
            sx1 = ti.min(sx0 + 1, w_src_max)
            sy0 = int(ti.floor(src_y))
            sy1 = ti.min(sy0 + 1, h_src_max)
            wsx = src_x - ti.floor(src_x)
            wsy = src_y - ti.floor(src_y)
            val = (1.0 - wsy) * ((1.0 - wsx) * src[sy0, sx0] + wsx * src[sy0, sx1]) + wsy * ((1.0 - wsx) * src[sy1, sx0] + wsx * src[sy1, sx1])
            dst[r, c] = val
        else:
            dst[r, c] = 0.0


@ti.kernel
def _sparse_mesh_warp_3d_kernel(
    src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    """Single-pass Catmull-Rom bicubic spline sparse mesh warp for 3D RGB images."""
    for r, c in dst:
        coord = _sparse_mesh_coordinate(
            mesh, u_grid[c], v_grid[r], w_mesh_max, h_mesh_max
        )
        src_x = coord[0]
        src_y = coord[1]

        if src_x >= 0.0 and src_x <= w_src_f and src_y >= 0.0 and src_y <= h_src_f:
            sx0 = int(ti.floor(src_x))
            sx1 = ti.min(sx0 + 1, w_src_max)
            sy0 = int(ti.floor(src_y))
            sy1 = ti.min(sy0 + 1, h_src_max)
            wsx = src_x - ti.floor(src_x)
            wsy = src_y - ti.floor(src_y)
            w00 = (1.0 - wsy) * (1.0 - wsx)
            w01 = (1.0 - wsy) * wsx
            w10 = wsy * (1.0 - wsx)
            w11 = wsy * wsx
            dst[r, c] = (
                w00 * src[sy0, sx0]
                + w01 * src[sy0, sx1]
                + w10 * src[sy1, sx0]
                + w11 * src[sy1, sx1]
            )
        else:
            dst[r, c] = ti.Vector([0.0, 0.0, 0.0])


@ti.func
def _sample_bilinear_scalar(
    img: ti.types.ndarray(),
    x: ti.f32,
    y: ti.f32,
    w_f: ti.f32,
    h_f: ti.f32,
    w_max: ti.i32,
    h_max: ti.i32,
) -> ti.f32:
    val = 0.0
    if x >= 0.0 and x <= w_f and y >= 0.0 and y <= h_f:
        x0 = int(ti.floor(x))
        x1 = ti.min(x0 + 1, w_max)
        y0 = int(ti.floor(y))
        y1 = ti.min(y0 + 1, h_max)
        fx = x - ti.floor(x)
        fy = y - ti.floor(y)
        val = (1.0 - fy) * ((1.0 - fx) * img[y0, x0] + fx * img[y0, x1]) + fy * (
            (1.0 - fx) * img[y1, x0] + fx * img[y1, x1]
        )
    return val


@ti.func
def _eval_point_cost(
    img: ti.types.ndarray(),
    ref: ti.types.ndarray(),
    sx: ti.f32,
    sy: ti.f32,
    rx: ti.f32,
    ry: ti.f32,
    w_f: ti.f32,
    h_f: ti.f32,
    w_max: ti.i32,
    h_max: ti.i32,
) -> ti.f32:
    # 5-point cross stencil for robust, ultra-fast structural matching
    cost = 0.0
    val_c = _sample_bilinear_scalar(img, sx, sy, w_f, h_f, w_max, h_max)
    ref_c = ref[int(ry), int(rx)]
    cost += ti.abs(val_c - ref_c) * 2.0

    val_l = _sample_bilinear_scalar(img, sx - 1.0, sy, w_f, h_f, w_max, h_max)
    ref_l = ref[int(ry), ti.max(0, int(rx) - 1)]
    cost += ti.abs(val_l - ref_l)

    val_r = _sample_bilinear_scalar(img, sx + 1.0, sy, w_f, h_f, w_max, h_max)
    ref_r = ref[int(ry), ti.min(w_max, int(rx) + 1)]
    cost += ti.abs(val_r - ref_r)

    val_u = _sample_bilinear_scalar(img, sx, sy - 1.0, w_f, h_f, w_max, h_max)
    ref_u = ref[ti.max(0, int(ry) - 1), int(rx)]
    cost += ti.abs(val_u - ref_u)

    val_d = _sample_bilinear_scalar(img, sx, sy + 1.0, w_f, h_f, w_max, h_max)
    ref_d = ref[ti.min(h_max, int(ry) + 1), int(rx)]
    cost += ti.abs(val_d - ref_d)

    return cost * (1.0 / 6.0)


@ti.func
def _rgb_luma(pixel):
    return pixel[0] * 0.2126 + pixel[1] * 0.7152 + pixel[2] * 0.0722


@ti.func
def _sample_bilinear_rgb(
    img: ti.types.ndarray(),
    x: ti.f32,
    y: ti.f32,
    w_f: ti.f32,
    h_f: ti.f32,
    w_max: ti.i32,
    h_max: ti.i32,
):
    value = ti.Vector([0.0, 0.0, 0.0])
    if x >= 0.0 and x <= w_f and y >= 0.0 and y <= h_f:
        x0 = int(ti.floor(x))
        x1 = ti.min(x0 + 1, w_max)
        y0 = int(ti.floor(y))
        y1 = ti.min(y0 + 1, h_max)
        fx = x - ti.floor(x)
        fy = y - ti.floor(y)
        value = (1.0 - fy) * (
            (1.0 - fx) * img[y0, x0] + fx * img[y0, x1]
        ) + fy * ((1.0 - fx) * img[y1, x0] + fx * img[y1, x1])
    return value


@ti.func
def _sample_bilinear_luma_rgb(
    img: ti.types.ndarray(),
    x: ti.f32,
    y: ti.f32,
    w_f: ti.f32,
    h_f: ti.f32,
    w_max: ti.i32,
    h_max: ti.i32,
):
    return _rgb_luma(
        _sample_bilinear_rgb(img, x, y, w_f, h_f, w_max, h_max)
    )


@ti.func
def _eval_point_cost_rgb(
    img: ti.types.ndarray(),
    ref: ti.types.ndarray(),
    sx: ti.f32,
    sy: ti.f32,
    rx: ti.f32,
    ry: ti.f32,
    w_f: ti.f32,
    h_f: ti.f32,
    w_max: ti.i32,
    h_max: ti.i32,
) -> ti.f32:
    cost = 0.0
    val_c = _sample_bilinear_luma_rgb(img, sx, sy, w_f, h_f, w_max, h_max)
    ref_c = _rgb_luma(ref[int(ry), int(rx)])
    cost += ti.abs(val_c - ref_c) * 2.0

    val_l = _sample_bilinear_luma_rgb(img, sx - 1.0, sy, w_f, h_f, w_max, h_max)
    ref_l = _rgb_luma(ref[int(ry), ti.max(0, int(rx) - 1)])
    cost += ti.abs(val_l - ref_l)
    val_r = _sample_bilinear_luma_rgb(img, sx + 1.0, sy, w_f, h_f, w_max, h_max)
    ref_r = _rgb_luma(ref[int(ry), ti.min(w_max, int(rx) + 1)])
    cost += ti.abs(val_r - ref_r)
    val_u = _sample_bilinear_luma_rgb(img, sx, sy - 1.0, w_f, h_f, w_max, h_max)
    ref_u = _rgb_luma(ref[ti.max(0, int(ry) - 1), int(rx)])
    cost += ti.abs(val_u - ref_u)
    val_d = _sample_bilinear_luma_rgb(img, sx, sy + 1.0, w_f, h_f, w_max, h_max)
    ref_d = _rgb_luma(ref[ti.min(h_max, int(ry) + 1), int(rx)])
    cost += ti.abs(val_d - ref_d)
    return cost * (1.0 / 6.0)


@ti.kernel
def _adaptive_refine_2d_kernel(
    ref: ti.types.ndarray(dtype=ti.f32, ndim=2),
    warped: ti.types.ndarray(dtype=ti.f32, ndim=2),
    mov: ti.types.ndarray(dtype=ti.f32, ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    x_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    y_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    cand_motions: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=1),
    num_cands: ti.i32,
    dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
    err_threshold: ti.f32,
    max_iters: ti.i32,
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    """Adaptive Search & Refine kernel: early exits on easy regions, iteratively refines hard regions."""
    for r, c in dst:
        val_w = warped[r, c]
        val_ref = ref[r, c]
        initial_err = ti.abs(val_w - val_ref)

        if initial_err <= err_threshold:
            # === EARLY EXIT 0 (Area Mudah: Selaras sempurna) ===
            dst[r, c] = val_w
        else:
            # === HARD REGION: Adaptive Search & Refine ===
            xf = x_grid[c]
            yf = y_grid[r]

            u = u_grid[c]
            v = v_grid[r]
            u0 = int(ti.floor(u))
            v0 = int(ti.floor(v))
            wu = u - ti.floor(u)
            wv = v - ti.floor(v)

            c0 = ti.max(0, u0 - 1)
            c1 = ti.min(w_mesh_max, ti.max(0, u0))
            c2 = ti.min(w_mesh_max, ti.max(0, u0 + 1))
            c3 = ti.min(w_mesh_max, ti.max(0, u0 + 2))

            r0 = ti.max(0, v0 - 1)
            r1 = ti.min(h_mesh_max, ti.max(0, v0))
            r2 = ti.min(h_mesh_max, ti.max(0, v0 + 1))
            r3 = ti.min(h_mesh_max, ti.max(0, v0 + 2))

            row0 = _catmull_rom_1d_vec2(mesh[r0, c0], mesh[r0, c1], mesh[r0, c2], mesh[r0, c3], wu)
            row1 = _catmull_rom_1d_vec2(mesh[r1, c0], mesh[r1, c1], mesh[r1, c2], mesh[r1, c3], wu)
            row2 = _catmull_rom_1d_vec2(mesh[r2, c0], mesh[r2, c1], mesh[r2, c2], mesh[r2, c3], wu)
            row3 = _catmull_rom_1d_vec2(mesh[r3, c0], mesh[r3, c1], mesh[r3, c2], mesh[r3, c3], wu)
            base_coord = _catmull_rom_1d_vec2(row0, row1, row2, row3, wv)

            best_sx = base_coord[0]
            best_sy = base_coord[1]
            best_cost = initial_err

            # Fast Hypothesis testing over dominant motion candidates
            for k in range(num_cands):
                m_vec = cand_motions[k]
                hyp_sx = xf + m_vec[0]
                hyp_sy = yf + m_vec[1]
                if best_cost > err_threshold and hyp_sx >= 0.0 and hyp_sx <= w_src_f and hyp_sy >= 0.0 and hyp_sy <= h_src_f:
                    val_hyp = _sample_bilinear_scalar(mov, hyp_sx, hyp_sy, w_src_f, h_src_f, w_src_max, h_src_max)
                    cost = ti.abs(val_hyp - val_ref)
                    if cost < best_cost:
                        best_cost = cost
                        best_sx = hyp_sx
                        best_sy = hyp_sy

            # EARLY EXIT 1: Jika kandidat layer langsung menyelesaikan ghosting
            if best_cost <= err_threshold:
                dst[r, c] = _sample_bilinear_scalar(mov, best_sx, best_sy, w_src_f, h_src_f, w_src_max, h_src_max)


            else:
                # Iterative Diamond Refinement (Maksimal 5x) untuk area paling sulit
                step = 2.0
                iters = 0
                best_cost_patch = _eval_point_cost(mov, ref, best_sx, best_sy, xf, yf, w_src_f, h_src_f, w_src_max, h_src_max)

                while iters < max_iters and best_cost_patch > err_threshold and step >= 0.25:
                    iters += 1
                    found_better = 0
                    improved_sx = best_sx
                    improved_sy = best_sy

                    for d_idx in ti.static(range(4)):
                        dx = 0.0
                        dy = 0.0
                        if ti.static(d_idx == 0):
                            dx = -step
                        elif ti.static(d_idx == 1):
                            dx = step
                        elif ti.static(d_idx == 2):
                            dy = -step
                        elif ti.static(d_idx == 3):
                            dy = step

                        test_sx = best_sx + dx
                        test_sy = best_sy + dy
                        if best_cost_patch > err_threshold and test_sx >= 0.0 and test_sx <= w_src_f and test_sy >= 0.0 and test_sy <= h_src_f:
                            cost_p = _eval_point_cost(mov, ref, test_sx, test_sy, xf, yf, w_src_f, h_src_f, w_src_max, h_src_max)
                            if cost_p < best_cost_patch:
                                best_cost_patch = cost_p
                                improved_sx = test_sx
                                improved_sy = test_sy
                                found_better = 1

                    if found_better == 1:
                        best_sx = improved_sx
                        best_sy = improved_sy
                    else:
                        step *= 0.5

                dst[r, c] = _sample_bilinear_scalar(mov, best_sx, best_sy, w_src_f, h_src_f, w_src_max, h_src_max)

@ti.func
def _refine_rgb_pixel(
    ref: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    warped_value: ti.types.vector(3, ti.f32),
    mov: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    cand_motions: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=1),
    num_cands: ti.i32,
    r: ti.i32,
    c: ti.i32,
    err_threshold: ti.f32,
    max_iters: ti.i32,
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    val_ref = _rgb_luma(ref[r, c])
    initial_err = ti.abs(_rgb_luma(warped_value) - val_ref)
    result = warped_value
    if initial_err > err_threshold:
        xf = ti.cast(c, ti.f32)
        yf = ti.cast(r, ti.f32)
        base_coord = _sparse_mesh_coordinate(
            mesh, u_grid[c], v_grid[r], w_mesh_max, h_mesh_max
        )
        best_sx = base_coord[0]
        best_sy = base_coord[1]
        best_cost = initial_err

        for k in range(num_cands):
            motion = cand_motions[k]
            hyp_sx = xf + motion[0]
            hyp_sy = yf + motion[1]
            if best_cost > err_threshold and hyp_sx >= 0.0 and hyp_sx <= w_src_f and hyp_sy >= 0.0 and hyp_sy <= h_src_f:
                cost = ti.abs(
                    _sample_bilinear_luma_rgb(
                        mov, hyp_sx, hyp_sy, w_src_f, h_src_f, w_src_max, h_src_max
                    ) - val_ref
                )
                if cost < best_cost:
                    best_cost = cost
                    best_sx = hyp_sx
                    best_sy = hyp_sy

        if best_cost <= err_threshold:
            result = _sample_bilinear_rgb(
                mov, best_sx, best_sy, w_src_f, h_src_f, w_src_max, h_src_max
            )
        else:
            step = 2.0
            iters = 0
            best_cost_patch = _eval_point_cost_rgb(
                mov, ref, best_sx, best_sy, xf, yf,
                w_src_f, h_src_f, w_src_max, h_src_max
            )
            while iters < max_iters and best_cost_patch > err_threshold and step >= 0.25:
                iters += 1
                found_better = 0
                improved_sx = best_sx
                improved_sy = best_sy
                for d_idx in ti.static(range(4)):
                    dx = 0.0
                    dy = 0.0
                    if ti.static(d_idx == 0):
                        dx = -step
                    elif ti.static(d_idx == 1):
                        dx = step
                    elif ti.static(d_idx == 2):
                        dy = -step
                    else:
                        dy = step
                    test_sx = best_sx + dx
                    test_sy = best_sy + dy
                    if best_cost_patch > err_threshold and test_sx >= 0.0 and test_sx <= w_src_f and test_sy >= 0.0 and test_sy <= h_src_f:
                        cost = _eval_point_cost_rgb(
                            mov, ref, test_sx, test_sy, xf, yf,
                            w_src_f, h_src_f, w_src_max, h_src_max
                        )
                        if cost < best_cost_patch:
                            best_cost_patch = cost
                            improved_sx = test_sx
                            improved_sy = test_sy
                            found_better = 1
                if found_better == 1:
                    best_sx = improved_sx
                    best_sy = improved_sy
                else:
                    step *= 0.5
            result = _sample_bilinear_rgb(
                mov, best_sx, best_sy, w_src_f, h_src_f, w_src_max, h_src_max
            )
    return result


@ti.kernel
def _adaptive_refine_3d_kernel(
    ref: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    warped: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    mov: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    cand_motions: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=1),
    num_cands: ti.i32,
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    err_threshold: ti.f32,
    max_iters: ti.i32,
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    """Refine a previously warped RGB image using bounded luma search."""
    for r, c in dst:
        dst[r, c] = _refine_rgb_pixel(
            ref, warped[r, c], mov, mesh, u_grid, v_grid,
            cand_motions, num_cands, r, c, err_threshold, max_iters,
            w_src_f, h_src_f, w_mesh_max, h_mesh_max, w_src_max, h_src_max,
        )


@ti.kernel
def _sparse_mesh_warp_3d_refine_kernel(
    ref: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    mesh: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=2),
    u_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    v_grid: ti.types.ndarray(dtype=ti.f32, ndim=1),
    cand_motions: ti.types.ndarray(dtype=ti.types.vector(2, ti.f32), ndim=1),
    num_cands: ti.i32,
    dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
    err_threshold: ti.f32,
    max_iters: ti.i32,
    w_src_f: ti.f32,
    h_src_f: ti.f32,
    w_mesh_max: ti.i32,
    h_mesh_max: ti.i32,
    w_src_max: ti.i32,
    h_src_max: ti.i32,
):
    """Warp and refine RGB in one frame pass to avoid an intermediate image."""
    for r, c in dst:
        coord = _sparse_mesh_coordinate(
            mesh, u_grid[c], v_grid[r], w_mesh_max, h_mesh_max
        )
        warped_value = _sample_bilinear_rgb(
            src, coord[0], coord[1], w_src_f, h_src_f, w_src_max, h_src_max
        )
        dst[r, c] = _refine_rgb_pixel(
            ref, warped_value, src, mesh, u_grid, v_grid,
            cand_motions, num_cands, r, c, err_threshold, max_iters,
            w_src_f, h_src_f, w_mesh_max, h_mesh_max, w_src_max, h_src_max,
        )



def compute_sparse_mesh(
    warp_func: object,
    dsize: tuple[int, int],
    mesh_shape: tuple[int, int] = (33, 33),
) -> np.ndarray:
    """Evaluate coordinate warp function on a sparse 2D grid mesh.

    Returns array of shape (mesh_h, mesh_w, 2) dtype float32.
    """
    out_w, out_h = int(dsize[0]), int(dsize[1])
    mesh_h, mesh_w = int(mesh_shape[0]), int(mesh_shape[1])

    gy, gx = np.mgrid[0 : out_h - 1 : complex(0, mesh_h), 0 : out_w - 1 : complex(0, mesh_w)]
    mesh_pts = np.column_stack([gx.ravel(), gy.ravel()]).astype(np.float64)

    if hasattr(warp_func, "map_points"):
        src_coords = warp_func.map_points(mesh_pts)
    elif callable(warp_func):
        src_coords = warp_func(mesh_pts)
    else:
        raise TypeError(f"warp_func must be callable or provide map_points, got {type(warp_func)}")

    mesh_2d = src_coords.reshape(mesh_h, mesh_w, 2).astype(np.float32)
    return np.ascontiguousarray(mesh_2d)


_AOT_MESH_MODULE = None


def _get_aot_mesh_module():
    """Load the APAP module through exact active-target resolution."""
    global _AOT_MESH_MODULE
    if _AOT_MESH_MODULE is not None:
        return _AOT_MESH_MODULE
    try:
        from taichi_vision.taichi_algorithm import aot_api
        from taichi_vision.taichi_aot.engine import engine

        module = aot_api.load_tcm("apap_native")
        _AOT_MESH_MODULE = (engine, module)
        return _AOT_MESH_MODULE
    except Exception as exc:
        try:
            target, _ = aot_api._module_loader.resolve_target()
            target_id = target.target_id
        except Exception:
            target_id = "unknown active target"
        raise RuntimeError(
            "Native APAP/mesh warp is unavailable for "
            f"{target_id}: target-qualified 'apap_native' TCM is required. "
            "No alternate backend, JIT, NumPy, or OpenCV fallback is allowed."
        ) from exc


def warp_image_sparse_mesh(
    image: np.ndarray,
    warp_func: object,
    dsize: tuple[int, int] | None = None,
    mesh_shape: tuple[int, int] = (33, 33),
    border_value: float = 0.0,
    ref_image: np.ndarray | None = None,
    cand_motions: np.ndarray | None = None,
    enable_adaptive_refine: bool = False,
    err_threshold: float = 0.04,
    max_refine_iters: int = 5,
    return_gpu: bool = False,
):
    """Warp image using sparse mesh acceleration on Taichi GPU or CPU.

    Supports optional single-pass Adaptive Search & Refine to eliminate motion
    boundary / occlusion parallax ghosting with early-exit convergence.

    Args:
        image: HxW (2D) or HxWx3 (3D) image array or TaichiGPUBuffer.
        warp_func: APAPWarp, AANAPWarp, or any coordinate mapping function.
        dsize: Output canvas (width, height). Defaults to input image dimensions.
        mesh_shape: Sparse grid resolution (mesh_h, mesh_w).
        border_value: Intensity for out-of-bounds pixels.
        ref_image: Optional reference frame for Adaptive Search & Refine.
        cand_motions: Dominant layer motion vectors (e.g. background and foreground).
        enable_adaptive_refine: Whether to execute the adaptive refine pass on hard regions.
        err_threshold: Photometric error below which early exit is triggered.
        max_refine_iters: Maximum local diamond search iterations for hard regions (default 5).
        return_gpu: Return the completed native output buffer without a host readback.

    Returns:
        A native output buffer when ``return_gpu`` is true; otherwise
        ``(warped_image, valid_mask)`` as NumPy arrays.
    """
    is_gpu_buf = hasattr(image, "to_numpy") and hasattr(image, "engine")
    img = None if is_gpu_buf else np.asarray(image)
    image_shape = tuple(image.shape) if is_gpu_buf else img.shape
    image_ndim = len(image_shape)
    image_dtype = np.dtype(image.dtype if is_gpu_buf else img.dtype)

    src_h, src_w = image_shape[:2]
    out_w, out_h = (src_w, src_h) if dsize is None else (int(dsize[0]), int(dsize[1]))
    adaptive_enabled = (
        enable_adaptive_refine
        and ref_image is not None
        and image_ndim in (2, 3)
    )
    if adaptive_enabled:
        ref_is_gpu = hasattr(ref_image, "to_numpy") and hasattr(ref_image, "engine")
        ref_shape = tuple(ref_image.shape) if ref_is_gpu else np.asarray(ref_image).shape
        expected_ref_shape = (out_h, out_w) if image_ndim == 2 else (out_h, out_w, 3)
        if ref_shape != expected_ref_shape:
            raise ValueError(
                "Adaptive APAP reference must match the output grid and image channels: "
                f"expected {expected_ref_shape}, got {ref_shape}"
            )

    # Native pure APAP can generate the vector mesh into a GPU buffer directly,
    # avoiding a GPU -> NumPy readback followed by an identical re-upload.
    mesh_h, mesh_w = (int(value) for value in mesh_shape)
    mesh_gpu = None
    mesh_builder = getattr(warp_func, "_map_mesh_buffer", None)
    if callable(mesh_builder):
        mesh_gpu = mesh_builder(
            (out_w, out_h),
            (mesh_h, mesh_w),
            allow_unsupported=adaptive_enabled,
        )
        mesh = None
    else:
        mesh = compute_sparse_mesh(warp_func, (out_w, out_h), mesh_shape=(mesh_h, mesh_w))

    # Precompute 1D coordinate sampling grids for zero-cast kernel execution
    u_grid = np.linspace(0.0, float(mesh_w - 1), out_w, dtype=np.float32)
    v_grid = np.linspace(0.0, float(mesh_h - 1), out_h, dtype=np.float32)

    w_src_f = float(src_w - 1)
    h_src_f = float(src_h - 1)
    w_mesh_max = int(mesh_w - 1)
    h_mesh_max = int(mesh_h - 1)
    w_src_max = int(src_w - 1)
    h_src_max = int(src_h - 1)

    # 1. Primary path: Precompiled Taichi AOT Module (Vulkan/CUDA/CPU/OpenGL)
    aot_bundle = _get_aot_mesh_module()
    if aot_bundle is not None:
        try:
            engine, mod = aot_bundle
            src_gpu = image if is_gpu_buf else engine.upload(np.ascontiguousarray(img, dtype=np.float32))
            if mesh_gpu is None:
                mesh_gpu = engine.upload(mesh)
            u_gpu = engine.upload(u_grid)
            v_gpu = engine.upload(v_grid)
            ref_gpu = x_gpu = y_gpu = cands_gpu = None
            cands_arr = None
            if adaptive_enabled:
                ref_is_gpu = hasattr(ref_image, "to_numpy") and hasattr(ref_image, "engine")
                if ref_is_gpu:
                    ref_gpu = ref_image
                else:
                    ref_f32 = np.ascontiguousarray(ref_image, dtype=np.float32)
                    ref_gpu = engine.upload(
                        ref_f32,
                        is_vector=image_ndim == 3,
                        vector_dim=3 if image_ndim == 3 else None,
                    )
                if image_ndim == 2:
                    x_gpu = engine.upload(np.arange(out_w, dtype=np.float32))
                    y_gpu = engine.upload(np.arange(out_h, dtype=np.float32))
                cands_arr = (
                    np.zeros((1, 2), dtype=np.float32)
                    if cand_motions is None
                    else np.ascontiguousarray(cand_motions, dtype=np.float32)
                )
                cands_gpu = engine.upload(cands_arr, is_vector=True, vector_dim=2)

            if image_ndim == 2:
                dst_gpu = engine.allocate((out_h, out_w), dtype=np.float32)
                mod.run(
                    "sparse_mesh_warp_2d_f32",
                    src=src_gpu,
                    mesh=mesh_gpu,
                    u_grid=u_gpu,
                    v_grid=v_gpu,
                    dst=dst_gpu,
                    w_src_f=w_src_f,
                    h_src_f=h_src_f,
                    w_mesh_max=w_mesh_max,
                    h_mesh_max=h_mesh_max,
                    w_src_max=w_src_max,
                    h_src_max=h_src_max,
                )
            elif image_ndim == 3 and image_shape[2] == 3:
                dst_gpu = engine.allocate(
                    (out_h, out_w, 3),
                    dtype=np.float32,
                    is_vector=True,
                    vector_dim=3,
                )
                if adaptive_enabled:
                    mod.run(
                        "sparse_mesh_warp_refine_3d_f32",
                        ref=ref_gpu,
                        src=src_gpu,
                        mesh=mesh_gpu,
                        u_grid=u_gpu,
                        v_grid=v_gpu,
                        cand_motions=cands_gpu,
                        num_cands=int(len(cands_arr)),
                        dst=dst_gpu,
                        err_threshold=float(err_threshold),
                        max_iters=int(max_refine_iters),
                        w_src_f=w_src_f,
                        h_src_f=h_src_f,
                        w_mesh_max=w_mesh_max,
                        h_mesh_max=h_mesh_max,
                        w_src_max=w_src_max,
                        h_src_max=h_src_max,
                    )
                else:
                    mod.run(
                        "sparse_mesh_warp_3d_f32",
                        src=src_gpu,
                        mesh=mesh_gpu,
                        u_grid=u_gpu,
                        v_grid=v_gpu,
                        dst=dst_gpu,
                        w_src_f=w_src_f,
                        h_src_f=h_src_f,
                        w_mesh_max=w_mesh_max,
                        h_mesh_max=h_mesh_max,
                        w_src_max=w_src_max,
                        h_src_max=h_src_max,
                    )
            else:
                raise ValueError(f"Unsupported image shape for Taichi mesh warp: {image_shape}")

            if adaptive_enabled and image_ndim == 2:
                # Each work item reads only the current warped pixel before
                # writing it, so the frame-sized output can be reused in place.
                mod.run(
                    "adaptive_refine_2d_f32",
                    ref=ref_gpu,
                    warped=dst_gpu,
                    mov=src_gpu,
                    mesh=mesh_gpu,
                    u_grid=u_gpu,
                    v_grid=v_gpu,
                    x_grid=x_gpu,
                    y_grid=y_gpu,
                    cand_motions=cands_gpu,
                    num_cands=int(len(cands_arr)),
                    dst=dst_gpu,
                    err_threshold=float(err_threshold),
                    max_iters=int(max_refine_iters),
                    w_src_f=w_src_f,
                    h_src_f=h_src_f,
                    w_mesh_max=w_mesh_max,
                    h_mesh_max=h_mesh_max,
                    w_src_max=w_src_max,
                    h_src_max=h_src_max,
                )

            if return_gpu:
                # Complete queued work before local source/mesh buffers leave
                # scope; the returned output then owns an independent result.
                engine.sync()
                return dst_gpu

            warped = dst_gpu.to_numpy()

            valid = np.isfinite(warped)
            valid &= warped != border_value
            if border_value != 0.0:
                warped[~valid] = border_value
            return warped.astype(image_dtype, copy=False), valid
        except Exception as exc:
            raise RuntimeError(
                "Native sparse APAP/mesh warp failed on the selected "
                "backend/device; no JIT, CPU, NumPy, or OpenCV fallback was used."
            ) from exc
    raise RuntimeError("Native APAP module loader returned no module unexpectedly")


def warp_apap(
    image,
    src_points: np.ndarray,
    dst_points: np.ndarray,
    dsize: tuple[int, int] | None = None,
    ref_image: np.ndarray | None = None,
    enable_adaptive_refine: bool = True,
    err_threshold: float = 0.04,
    max_refine_iters: int = 5,
    mesh_shape: tuple[int, int] = (33, 33),
    fit_grid_shape: tuple[int, int] | None = None,
    return_gpu: bool = False,
    global_homography: np.ndarray | None = None,
    sigma: float | tuple[float, float] | None = None,
):
    """High-level one-line API for APAP image warping with GPU Catmull-Rom & Adaptive Refine.

    Args:
        image: Source image to warp (2D grayscale or 3D RGB, uint8 or float32).
        src_points: Source keypoint coordinates (N, 2).
        dst_points: Corresponding destination keypoint coordinates (N, 2).
        dsize: Output image dimensions (width, height). Defaults to image shape.
        ref_image: Optional reference image for Adaptive Search & Refine in parallax zones.
        enable_adaptive_refine: Enables diamond-stencil search and refinement when ref_image is provided.
        err_threshold: Discrepancy threshold for early-exit on easy regions.
        max_refine_iters: Maximum refinement iterations on hard/occlusion regions (1 to 5).
        mesh_shape: Sparse grid resolution for mesh warping. Defaults to (33, 33).
        fit_grid_shape: Optional moving-homography grid. ``mesh_shape`` continues
            to control only the image-warp interpolation density.
        return_gpu: Return the native output buffer without copying it to host memory.
        global_homography: Optional source-to-destination control already
            estimated by the caller, reused for local-model quality checks.
        sigma: Optional APAP locality bandwidth, forwarded to the native fit.

    Returns:
        A GPU output buffer when ``return_gpu`` is true; otherwise
        ``(warped_image, valid_mask)`` as NumPy arrays.
    """
    from .apap import fit_apap

    apap_warp = fit_apap(
        src_points,
        dst_points,
        global_homography=global_homography,
        grid_shape=fit_grid_shape or (4, 4),
        sigma=sigma,
        enable_residual_spline=False,
    )
    return warp_image_sparse_mesh(
        image=image,
        warp_func=apap_warp,
        dsize=dsize,
        mesh_shape=mesh_shape,
        ref_image=ref_image,
        enable_adaptive_refine=enable_adaptive_refine,
        err_threshold=err_threshold,
        max_refine_iters=max_refine_iters,
        return_gpu=return_gpu,
    )
