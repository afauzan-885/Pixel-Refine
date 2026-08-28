import taichi as ti
import numpy as np
import os
import shutil
import zipfile
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.tile_motion.aot.cost_function import (
    compute_sad_cost_func,
    compute_ssd_cost_func,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.tile_motion.aot.refinement import (
    parabolic_refinement,
)

# Use standard SSD/SAD metrics as default stable configuration
compute_alignment_ssd = compute_ssd_cost_func
compute_alignment_sad = compute_sad_cost_func



@ti.func
def hanning_window_1d(idx: ti.i32, size: ti.i32) -> ti.f32:
    """Compute Hanning window value for 1D at given index"""
    val = 0.0
    if 0 <= idx < size:
        val = 0.5 - 0.5 * ti.cos(
            2.0 * 3.14159265359 * ti.cast(idx, ti.f32) / ti.cast(size - 1, ti.f32)
        )
    return val


@ti.func
def hanning_window_2d(
    row: ti.i32, col: ti.i32, tile_h: ti.i32, tile_w: ti.i32
) -> ti.f32:
    """Compute 2D Hanning window: product of 1D windows"""
    return hanning_window_1d(row, tile_h) * hanning_window_1d(col, tile_w)


@ti.func
def bicubic_weight(x: ti.f32):
    abs_x = ti.abs(x)
    res = 0.0
    if abs_x <= 1.0:
        res = 1.5 * abs_x**3 - 2.5 * abs_x**2 + 1.0
    elif abs_x < 2.0:
        res = -0.5 * abs_x**3 + 2.5 * abs_x**2 - 4.0 * abs_x + 2.0
    return res


@ti.func
def compute_tile_gradient_energy(
    img: ti.template(), y: ti.i32, x: ti.i32, tile_h: ti.i32, tile_w: ti.i32
) -> ti.f32:
    """Compute mean local gradient magnitude on the reference tile with fast striding."""
    h, w = img.shape[0], img.shape[1]
    grad_sum = 0.0
    count = 0.0
    num_r = (tile_h - 1) // 2
    num_c = (tile_w - 1) // 2
    for r_idx in range(num_r):
        r = r_idx * 2
        for c_idx in range(num_c):
            c = c_idx * 2
            py, px = y + r, x + c
            if py + 1 < h and px + 1 < w:
                gx = ti.abs(img[py, px + 1] - img[py, px])
                gy = ti.abs(img[py + 1, px] - img[py, px])
                grad_sum += gx + gy
                count += 1.0
    return grad_sum / ti.max(1.0, count)


@ti.func
def parabolic_refinement_gated(
    c_left: ti.f32, c_center: ti.f32, c_right: ti.f32, min_curvature: ti.f32
) -> ti.f32:
    """Parabolic subpixel refinement with curvature gating to eliminate noise jitter on flat areas."""
    delta = 0.0
    denom = 2.0 * (c_left - 2.0 * c_center + c_right)
    curv = ti.abs(c_left - c_center) + ti.abs(c_right - c_center)
    if ti.abs(denom) > 1e-6 and curv >= min_curvature:
        delta = (c_left - c_right) / denom
        delta = ti.max(-0.5, ti.min(0.5, delta))
    return delta


@ti.func
def compute_regularization_params(
    flow: ti.template(), y: ti.i32, x: ti.i32, tile_h: ti.i32, tile_w: ti.i32, grad_energy: ti.f32
):
    h_total, w_total = flow.shape[0], flow.shape[1]
    sum_dx, sum_dy, count = 0.0, 0.0, 0.0
    center_y, center_x = y + tile_h // 2, x + tile_w // 2
    for dy_idx, dx_idx in ti.ndrange((-1, 2), (-1, 2)):
        if dy_idx == 0 and dx_idx == 0:
            continue
        ny, nx = center_y + dy_idx * tile_h, center_x + dx_idx * tile_w
        if 0 <= ny < h_total and 0 <= nx < w_total:
            sum_dx += flow[ny, nx, 0]
            sum_dy += flow[ny, nx, 1]
            count += 1.0

    # Texture-adaptive base lambda: smoothly scales up when gradient energy drops below 0.01
    base_lambda = 10.0
    if grad_energy < 0.01:
        base_lambda += (0.01 - grad_energy) * 4000.0

    avg_dx, avg_dy, lambda_val = 0.0, 0.0, base_lambda
    if count > 0.0:
        avg_dx, avg_dy = sum_dx / count, sum_dy / count
        curr_dx, curr_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        diff_sq = (curr_dx - avg_dx) ** 2 + (curr_dy - avg_dy) ** 2
        if diff_sq > 9.0:
            lambda_val *= 3.0
    else:
        avg_dx, avg_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
    return avg_dx, avg_dy, lambda_val


@ti.kernel
def block_search_kernel(
    ref_layer: ti.types.ndarray(),
    comp_layer: ti.types.ndarray(),
    refined_flow: ti.types.ndarray(),
    tile_h: ti.i32,
    tile_w: ti.i32,
    max_search_radius: ti.i32,
):
    h, w = ref_layer.shape[0], ref_layer.shape[1]
    step_y, step_x = ti.max(1, tile_h // 2), ti.max(1, tile_w // 2)

    for tile_y_idx, tile_x_idx in ti.ndrange(
        (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
    ):
        y, x = ti.max(0, ti.min(tile_y_idx * step_y, h - tile_h)), ti.max(
            0, ti.min(tile_x_idx * step_x, w - tile_w)
        )

        grad_energy = compute_tile_gradient_energy(ref_layer, y, x, tile_h, tile_w)
        local_search_radius = max_search_radius
        best_cost, best_dx, best_dy = 1e10, 0.0, 0.0

        # Flat-region penalty scale to prevent spurious noise jumps in featureless sky
        flat_drift_penalty = 0.02 if grad_energy < 0.008 else 0.0

        for dy, dx in ti.ndrange(
            (-local_search_radius, local_search_radius + 1),
            (-local_search_radius, local_search_radius + 1),
        ):
            cost = compute_alignment_ssd(
                ref_layer, comp_layer, y, x, y + dy, x + dx, tile_h, tile_w, 1
            )
            if flat_drift_penalty > 0.0:
                cost += flat_drift_penalty * float(dx * dx + dy * dy)
            if dx == 0 and dy == 0:
                cost *= 0.99
            if cost < best_cost:
                best_cost, best_dx, best_dy = cost, float(dx), float(dy)

        # 🚀 TINGKAT 2: Evaluasi pemecahan menjadi 4 sub-blok (hanya jika ada tekstur cukup)
        sub_h, sub_w = tile_h // 2, tile_w // 2
        
        sub_cost0, sub_dx0, sub_dy0 = 1e10, best_dx, best_dy
        sub_cost1, sub_dx1, sub_dy1 = 1e10, best_dx, best_dy
        sub_cost2, sub_dx2, sub_dy2 = 1e10, best_dx, best_dy
        sub_cost3, sub_dx3, sub_dy3 = 1e10, best_dx, best_dy
        
        local_refine_dist = 2
        
        if grad_energy >= 0.008:
            # Pencarian Sub-blok 0
            for dy, dx in ti.ndrange((-local_refine_dist, local_refine_dist + 1), (-local_refine_dist, local_refine_dist + 1)):
                cand_dx = best_dx + float(dx)
                cand_dy = best_dy + float(dy)
                c_dy, c_dx = ti.cast(ti.round(cand_dy), ti.i32), ti.cast(ti.round(cand_dx), ti.i32)
                cost = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x, y + c_dy, x + c_dx, sub_h, sub_w, 1
                )
                if cost < sub_cost0:
                    sub_cost0, sub_dx0, sub_dy0 = cost, cand_dx, cand_dy

            # Pencarian Sub-blok 1
            for dy, dx in ti.ndrange((-local_refine_dist, local_refine_dist + 1), (-local_refine_dist, local_refine_dist + 1)):
                cand_dx = best_dx + float(dx)
                cand_dy = best_dy + float(dy)
                c_dy, c_dx = ti.cast(ti.round(cand_dy), ti.i32), ti.cast(ti.round(cand_dx), ti.i32)
                cost = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x + sub_w, y + c_dy, x + sub_w + c_dx, sub_h, sub_w, 1
                )
                if cost < sub_cost1:
                    sub_cost1, sub_dx1, sub_dy1 = cost, cand_dx, cand_dy

            # Pencarian Sub-blok 2
            for dy, dx in ti.ndrange((-local_refine_dist, local_refine_dist + 1), (-local_refine_dist, local_refine_dist + 1)):
                cand_dx = best_dx + float(dx)
                cand_dy = best_dy + float(dy)
                c_dy, c_dx = ti.cast(ti.round(cand_dy), ti.i32), ti.cast(ti.round(cand_dx), ti.i32)
                cost = compute_alignment_ssd(
                    ref_layer, comp_layer, y + sub_h, x, y + sub_h + c_dy, x + c_dx, sub_h, sub_w, 1
                )
                if cost < sub_cost2:
                    sub_cost2, sub_dx2, sub_dy2 = cost, cand_dx, cand_dy

            # Pencarian Sub-blok 3
            for dy, dx in ti.ndrange((-local_refine_dist, local_refine_dist + 1), (-local_refine_dist, local_refine_dist + 1)):
                cand_dx = best_dx + float(dx)
                cand_dy = best_dy + float(dy)
                c_dy, c_dx = ti.cast(ti.round(cand_dy), ti.i32), ti.cast(ti.round(cand_dx), ti.i32)
                cost = compute_alignment_ssd(
                    ref_layer, comp_layer, y + sub_h, x + sub_w, y + sub_h + c_dy, x + sub_w + c_dx, sub_h, sub_w, 1
                )
                if cost < sub_cost3:
                    sub_cost3, sub_dx3, sub_dy3 = cost, cand_dx, cand_dy

        avg_sub_cost = (sub_cost0 + sub_cost1 + sub_cost2 + sub_cost3) / 4.0

        if grad_energy >= 0.008 and avg_sub_cost < 0.85 * best_cost:
            sub_dx0 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y, x, y + int(sub_dy0), x + int(sub_dx0) - 1, sub_h, sub_w, 1),
                sub_cost0,
                compute_alignment_ssd(ref_layer, comp_layer, y, x, y + int(sub_dy0), x + int(sub_dx0) + 1, sub_h, sub_w, 1),
                0.00015
            )
            sub_dy0 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y, x, y + int(sub_dy0) - 1, x + int(sub_dx0), sub_h, sub_w, 1),
                sub_cost0,
                compute_alignment_ssd(ref_layer, comp_layer, y, x, y + int(sub_dy0) + 1, x + int(sub_dx0), sub_h, sub_w, 1),
                0.00015
            )
            for r, c in ti.ndrange(sub_h, sub_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0], refined_flow[y + r, x + c, 1] = -sub_dx0, sub_dy0

            sub_dx1 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y, x + sub_w, y + int(sub_dy1), x + sub_w + int(sub_dx1) - 1, sub_h, sub_w, 1),
                sub_cost1,
                compute_alignment_ssd(ref_layer, comp_layer, y, x + sub_w, y + int(sub_dy1), x + sub_w + int(sub_dx1) + 1, sub_h, sub_w, 1),
                0.00015
            )
            sub_dy1 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y, x + sub_w, y + int(sub_dy1) - 1, x + sub_w + int(sub_dx1), sub_h, sub_w, 1),
                sub_cost1,
                compute_alignment_ssd(ref_layer, comp_layer, y, x + sub_w, y + int(sub_dy1) + 1, x + sub_w + int(sub_dx1), sub_h, sub_w, 1),
                0.00015
            )
            for r, c in ti.ndrange(sub_h, sub_w):
                if y + r < h and x + sub_w + c < w:
                    refined_flow[y + r, x + sub_w + c, 0], refined_flow[y + r, x + sub_w + c, 1] = -sub_dx1, sub_dy1

            sub_dx2 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x, y + sub_h + int(sub_dy2), x + int(sub_dx2) - 1, sub_h, sub_w, 1),
                sub_cost2,
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x, y + sub_h + int(sub_dy2), x + int(sub_dx2) + 1, sub_h, sub_w, 1),
                0.00015
            )
            sub_dy2 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x, y + sub_h + int(sub_dy2) - 1, x + int(sub_dx2), sub_h, sub_w, 1),
                sub_cost2,
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x, y + sub_h + int(sub_dy2) + 1, x + int(sub_dx2), sub_h, sub_w, 1),
                0.00015
            )
            for r, c in ti.ndrange(sub_h, sub_w):
                if y + sub_h + r < h and x + c < w:
                    refined_flow[y + sub_h + r, x + c, 0], refined_flow[y + sub_h + r, x + c, 1] = -sub_dx2, sub_dy2

            sub_dx3 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x + sub_w, y + sub_h + int(sub_dy3), x + sub_w + int(sub_dx3) - 1, sub_h, sub_w, 1),
                sub_cost3,
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x + sub_w, y + sub_h + int(sub_dy3), x + sub_w + int(sub_dx3) + 1, sub_h, sub_w, 1),
                0.00015
            )
            sub_dy3 += parabolic_refinement_gated(
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x + sub_w, y + sub_h + int(sub_dy3) - 1, x + sub_w + int(sub_dx3), sub_h, sub_w, 1),
                sub_cost3,
                compute_alignment_ssd(ref_layer, comp_layer, y + sub_h, x + sub_w, y + sub_h + int(sub_dy3) + 1, x + sub_w + int(sub_dx3), sub_h, sub_w, 1),
                0.00015
            )
            for r, c in ti.ndrange(sub_h, sub_w):
                if y + sub_h + r < h and x + sub_w + c < w:
                    refined_flow[y + sub_h + r, x + sub_w + c, 0], refined_flow[y + sub_h + r, x + sub_w + c, 1] = -sub_dx3, sub_dy3
        else:
            if (
                -local_search_radius < best_dx < local_search_radius
                and -local_search_radius < best_dy < local_search_radius
                and grad_energy >= 0.008
            ):
                c0 = best_cost
                cx_m1 = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x, y + int(best_dy), x + int(best_dx) - 1, tile_h, tile_w, 1
                )
                cx_p1 = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x, y + int(best_dy), x + int(best_dx) + 1, tile_h, tile_w, 1
                )
                cy_m1 = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x, y + int(best_dy) - 1, x + int(best_dx), tile_h, tile_w, 1
                )
                cy_p1 = compute_alignment_ssd(
                    ref_layer, comp_layer, y, x, y + int(best_dy) + 1, x + int(best_dx), tile_h, tile_w, 1
                )
                best_dx += parabolic_refinement_gated(cx_m1, c0, cx_p1, 0.00015)
                best_dy += parabolic_refinement_gated(cy_m1, c0, cy_p1, 0.00015)
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0], refined_flow[y + r, x + c, 1] = (
                        -best_dx,
                        best_dy,
                    )


@ti.kernel
def search_coarse_level_kernel(
    ref_layer: ti.types.ndarray(),
    comp_layer: ti.types.ndarray(),
    flow: ti.types.ndarray(),
    previous_flow: ti.types.ndarray(),
    refined_flow: ti.types.ndarray(),
    tile_h: ti.i32,
    tile_w: ti.i32,
    search_dist: ti.i32,
    downscale_factor: ti.i32,
):
    h, w = ref_layer.shape[0], ref_layer.shape[1]
    prev_h, prev_w = previous_flow.shape[0], previous_flow.shape[1]
    step_y, step_x = ti.max(1, tile_h // 2), ti.max(1, tile_w // 2)
    tile_area_inv = 1.0 / float(tile_h * tile_w)
    neighbor_offsets = ti.static(
        [
            [-1, 0],
            [1, 0],
            [0, -1],
            [0, 1],
            [-1, -1],
            [1, -1],
            [-1, 1],
            [1, 1],
            [-2, 0],
            [2, 0],
            [0, -2],
            [0, 2],
            [-2, -2],
            [2, -2],
            [-2, 2],
            [2, 2],
        ]
    )
    for tile_y_idx, tile_x_idx in ti.ndrange(
        (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
    ):
        y, x = ti.max(0, ti.min(tile_y_idx * step_y, h - tile_h)), ti.max(
            0, ti.min(tile_x_idx * step_x, w - tile_w)
        )
        center_y, center_x = y + tile_h // 2, x + tile_w // 2

        # 🚀 Texture Gradient Energy Calculation
        grad_energy = compute_tile_gradient_energy(ref_layer, y, x, tile_h, tile_w)
        spatial_mean_dx, spatial_mean_dy, spatial_weight = (
            compute_regularization_params(flow, y, x, tile_h, tile_w, grad_energy)
        )
        init_dx, init_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        best_cand_dx, best_cand_dy, best_cand_cost = (
            ti.round(init_dx, ti.i32),
            ti.round(init_dy, ti.i32),
            1e10,
        )

        # Flat-region fast lock (bypass noise hunting on featureless sky/walls)
        if grad_energy < 0.001:
            final_dx = spatial_mean_dx
            final_dy = spatial_mean_dy
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = -final_dx
                    refined_flow[y + r, x + c, 1] = final_dy
        else:
            for i in range(18):
                cand_dx, cand_dy = best_cand_dx, best_cand_dy
                if i > 0 and i < 17:
                    for idx in ti.static(range(16)):
                        if i - 1 == idx:
                            nx, ny = (
                                center_x + neighbor_offsets[idx][0] * tile_w,
                                center_y + neighbor_offsets[idx][1] * tile_h,
                            )
                            if 0 <= ny < h and 0 <= nx < w:
                                cand_dx, cand_dy = ti.round(
                                    flow[ny, nx, 0], ti.i32
                                ), ti.round(flow[ny, nx, 1], ti.i32)
                elif i == 17 and prev_h > 1 and prev_w > 1:
                    cy, cx = center_y // downscale_factor, center_x // downscale_factor
                    if cy < prev_h and cx < prev_w:
                        cand_dx, cand_dy = ti.round(
                            previous_flow[cy, cx, 0] * downscale_factor, ti.i32
                        ), ti.round(previous_flow[cy, cx, 1] * downscale_factor, ti.i32)
                cost = (
                    compute_alignment_sad(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        y + cand_dy,
                        x + cand_dx,
                        tile_h,
                        tile_w,
                        2,
                    )
                    * tile_area_inv
                )
                if cost < best_cand_cost:
                    best_cand_cost, best_cand_dx, best_cand_dy = cost, cand_dx, cand_dy

            best_total_cost, final_dx, final_dy = (
                1e10,
                float(best_cand_dx),
                float(best_cand_dy),
            )
            
            local_search_dist = ti.max(1, search_dist // 2)

            if best_cand_cost >= 0.003:
                for dy, dx in ti.ndrange(
                    (-local_search_dist, local_search_dist + 1), (-local_search_dist, local_search_dist + 1)
                ):
                    cur_dx, cur_dy = best_cand_dx + dx, best_cand_dy + dy
                    visual_cost = (
                        compute_alignment_sad(
                            ref_layer,
                            comp_layer,
                            y,
                            x,
                            y + cur_dy,
                            x + cur_dx,
                            tile_h,
                            tile_w,
                            1,
                        )
                        * tile_area_inv
                    )
                    dist_sq = (float(cur_dx) - spatial_mean_dx) ** 2 + (
                        float(cur_dy) - spatial_mean_dy
                    ) ** 2
                    total_cost = visual_cost + (spatial_weight * dist_sq * 0.1)
                    if total_cost < best_total_cost:
                        best_total_cost, final_dx, final_dy = (
                            total_cost,
                            float(cur_dx),
                            float(cur_dy),
                        )
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0], refined_flow[y + r, x + c, 1] = (
                        -final_dx,
                        final_dy,
                    )


@ti.kernel
def search_fine_level_kernel(
    ref_layer: ti.types.ndarray(),
    comp_layer: ti.types.ndarray(),
    flow: ti.types.ndarray(),
    previous_flow: ti.types.ndarray(),
    refined_flow: ti.types.ndarray(),
    tile_h: ti.i32,
    tile_w: ti.i32,
    downscale_factor: ti.i32,
):
    h, w = ref_layer.shape[0], ref_layer.shape[1]
    prev_h, prev_w = previous_flow.shape[0], previous_flow.shape[1]
    step_y, step_x = ti.max(1, tile_h // 2), ti.max(1, tile_w // 2)
    tile_area_inv = 1.0 / float(tile_h * tile_w)
    neighbor_offsets = ti.static(
        [
            [-1, 0],
            [1, 0],
            [0, -1],
            [0, 1],
            [-1, -1],
            [1, -1],
            [-1, 1],
            [1, 1],
            [-2, 0],
            [2, 0],
            [0, -2],
            [0, 2],
            [-2, -2],
            [2, -2],
            [-2, 2],
            [2, 2],
        ]
    )
    for tile_y_idx, tile_x_idx in ti.ndrange(
        (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
    ):
        y, x = ti.max(0, ti.min(tile_y_idx * step_y, h - tile_h)), ti.max(
            0, ti.min(tile_x_idx * step_x, w - tile_w)
        )
        center_y, center_x = y + tile_h // 2, x + tile_w // 2

        # 🚀 Texture Gradient Energy Calculation
        grad_energy = compute_tile_gradient_energy(ref_layer, y, x, tile_h, tile_w)
        spatial_mean_dx, spatial_mean_dy, spatial_weight = (
            compute_regularization_params(flow, y, x, tile_h, tile_w, grad_energy)
        )
        init_dx, init_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        best_cand_dx, best_cand_dy, best_cand_cost = (
            ti.round(init_dx, ti.i32),
            ti.round(init_dy, ti.i32),
            1e10,
        )

        # Flat-region fast lock (bypass noise hunting on featureless sky/walls)
        if grad_energy < 0.001:
            final_dx = spatial_mean_dx
            final_dy = spatial_mean_dy
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = -final_dx
                    refined_flow[y + r, x + c, 1] = final_dy
        else:
            for i in range(18):
                cand_dx, cand_dy = best_cand_dx, best_cand_dy
                if i > 0 and i < 17:
                    for idx in ti.static(range(16)):
                        if i - 1 == idx:
                            nx, ny = (
                                center_x + neighbor_offsets[idx][0] * tile_w,
                                center_y + neighbor_offsets[idx][1] * tile_h,
                            )
                            if 0 <= ny < h and 0 <= nx < w:
                                cand_dx, cand_dy = ti.round(
                                    flow[ny, nx, 0], ti.i32
                                ), ti.round(flow[ny, nx, 1], ti.i32)
                elif i == 17 and prev_h > 1 and prev_w > 1:
                    cy, cx = center_y // downscale_factor, center_x // downscale_factor
                    if cy < prev_h and cx < prev_w:
                        cand_dx, cand_dy = ti.round(
                            previous_flow[cy, cx, 0] * downscale_factor, ti.i32
                        ), ti.round(previous_flow[cy, cx, 1] * downscale_factor, ti.i32)
                cost = (
                    compute_alignment_sad(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        y + cand_dy,
                        x + cand_dx,
                        tile_h,
                        tile_w,
                        2,
                    )
                    * tile_area_inv
                )
                if cost < best_cand_cost:
                    best_cand_cost, best_cand_dx, best_cand_dy = cost, cand_dx, cand_dy

            best_total_cost, final_dx, final_dy = (
                1e10,
                float(best_cand_dx),
                float(best_cand_dy),
            )
            if best_cand_cost >= 0.0001:
                for dy, dx in ti.ndrange((-1, 2), (-1, 2)):
                    cur_dx, cur_dy = best_cand_dx + dx, best_cand_dy + dy
                    visual_cost = (
                        compute_alignment_sad(
                            ref_layer,
                            comp_layer,
                            y,
                            x,
                            y + cur_dy,
                            x + cur_dx,
                            tile_h,
                            tile_w,
                            1,
                        )
                        * tile_area_inv
                    )
                    dist_sq = (float(cur_dx) - spatial_mean_dx) ** 2 + (
                        float(cur_dy) - spatial_mean_dy
                    ) ** 2
                    total_cost = visual_cost + (spatial_weight * dist_sq * 0.05)
                    if total_cost < best_total_cost:
                        best_total_cost, final_dx, final_dy = (
                            total_cost,
                            float(cur_dx),
                            float(cur_dy),
                        )
            int_dx, int_dy = ti.round(final_dx, ti.i32), ti.round(final_dy, ti.i32)
            c0 = compute_alignment_sad(
                ref_layer, comp_layer, y, x, y + int_dy, x + int_dx, tile_h, tile_w, 1
            )
            c_m1_x = compute_alignment_sad(
                ref_layer, comp_layer, y, x, y + int_dy, x + int_dx - 1, tile_h, tile_w, 1
            )
            c_p1_x = compute_alignment_sad(
                ref_layer, comp_layer, y, x, y + int_dy, x + int_dx + 1, tile_h, tile_w, 1
            )
            c_m1_y = compute_alignment_sad(
                ref_layer, comp_layer, y, x, y + int_dy - 1, x + int_dx, tile_h, tile_w, 1
            )
            c_p1_y = compute_alignment_sad(
                ref_layer, comp_layer, y, x, y + int_dy + 1, x + int_dx, tile_h, tile_w, 1
            )
            final_dx = float(int_dx) + parabolic_refinement_gated(
                c_m1_x, c0, c_p1_x, 0.00015
            )
            final_dy = float(int_dy) + parabolic_refinement_gated(
                c_m1_y, c0, c_p1_y, 0.00015
            )
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0], refined_flow[y + r, x + c, 1] = (
                        -final_dx,
                        final_dy,
                    )


@ti.kernel
def upsample_flow_bicubic_kernel(
    src: ti.types.ndarray(), dst: ti.types.ndarray(), scale: ti.f32
):
    h_src, w_src = src.shape[0], src.shape[1]
    h_dst, w_dst = dst.shape[0], dst.shape[1]
    for i, j in ti.ndrange(h_dst, w_dst):
        y_src, x_src = float(i) / scale, float(j) / scale
        y_int, x_int = ti.floor(y_src, ti.i32), ti.floor(x_src, ti.i32)
        y_fract, x_fract = y_src - float(y_int), x_src - float(x_int)
        for k in ti.static(range(2)):
            val = 0.0
            for m in ti.static(range(-1, 3)):
                for n in ti.static(range(-1, 3)):
                    yy, xx = ti.max(0, ti.min(y_int + m, h_src - 1)), ti.max(
                        0, ti.min(x_int + n, w_src - 1)
                    )
                    w_m, w_n = bicubic_weight(float(m) - y_fract), bicubic_weight(
                        float(n) - x_fract
                    )
                    val += src[yy, xx, k] * w_m * w_n
            dst[i, j, k] = val * scale


# 🚀 SEKARANG PERBARUI FUNGSI GRAPH COMPILATION AGAR MENGENAL NDARRAY BARU
def compile_compute_flow(arch=None, suffix="vulkan"):
    if arch is None:
        arch = ti.vulkan
    ti.init(arch=arch)
    module = ti.aot.Module(arch)

    sym_ref_l0, sym_ref_l1, sym_ref_l2 = (
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l0", dtype=ti.f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l1", dtype=ti.f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l2", dtype=ti.f32, ndim=2),
    )
    sym_comp_l0, sym_comp_l1, sym_comp_l2 = (
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l0", dtype=ti.f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l1", dtype=ti.f32, ndim=2),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l2", dtype=ti.f32, ndim=2),
    )
    sym_flow_l0, sym_flow_l1, sym_flow_l2 = (
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l0", dtype=ti.f32, ndim=3),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l1", dtype=ti.f32, ndim=3),
        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l2", dtype=ti.f32, ndim=3),
    )

    sym_max_search_radius = ti.graph.Arg(
        ti.graph.ArgKind.SCALAR, "max_search_radius", dtype=ti.i32
    )

    sym_tile_h, sym_tile_w, sym_scale = (
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", dtype=ti.i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", dtype=ti.i32),
        ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32),
    )
    sym_search_dist, sym_downscale = ti.graph.Arg(
        ti.graph.ArgKind.SCALAR, "search_dist", dtype=ti.i32
    ), ti.graph.Arg(ti.graph.ArgKind.SCALAR, "downscale", dtype=ti.i32)

    g_builder = ti.graph.GraphBuilder()

    # block_search_kernel di Level 2 (1/4 skala)
    g_builder.dispatch(
        block_search_kernel,
        sym_ref_l2,
        sym_comp_l2,
        sym_flow_l2,
        sym_tile_h,
        sym_tile_w,
        sym_max_search_radius,
    )
    g_builder.dispatch(
        upsample_flow_bicubic_kernel, sym_flow_l2, sym_flow_l1, sym_scale
    )
    g_builder.dispatch(
        search_coarse_level_kernel,
        sym_ref_l1,
        sym_comp_l1,
        sym_flow_l1,
        sym_flow_l2,
        sym_flow_l1,
        sym_tile_h,
        sym_tile_w,
        sym_search_dist,
        sym_downscale,
    )
    g_builder.dispatch(
        upsample_flow_bicubic_kernel, sym_flow_l1, sym_flow_l0, sym_scale
    )
    g_builder.dispatch(
        search_fine_level_kernel,
        sym_ref_l0,
        sym_comp_l0,
        sym_flow_l0,
        sym_flow_l1,
        sym_flow_l0,
        sym_tile_h,
        sym_tile_w,
        sym_downscale,
    )

    module.add_graph("align_end_to_end_3layer", g_builder.compile())

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../../"))
    target_dirs = [
        os.path.join(project_root, "taichi_vision/taichi_algorithm/aot_tcm"),
        os.path.join(project_root, f"taichi_vision/taichi_algorithm/aot_tcm/{suffix}_x86_64_windows"),
        os.path.join(project_root, "pixel_refine_desktop/ui/data/aot_assets"),
    ]

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"tmp_aot_flow_{suffix}"))
    if os.path.exists(tmp_dir):
        try:
            shutil.rmtree(tmp_dir)
        except Exception:
            pass
    os.makedirs(tmp_dir, exist_ok=True)
    module.save(tmp_dir)

    for out_dir in target_dirs:
        os.makedirs(out_dir, exist_ok=True)
        tcm_name = (
            f"compute_flow_{suffix}_x86_64_windows.tcm"
            if "taichi_vision" in out_dir
            else f"compute_flow_{suffix}.tcm"
        )
        tcm_path = os.path.join(out_dir, tcm_name)
        with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as tcm_zip:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    tcm_zip.write(
                        os.path.join(root, file),
                        os.path.relpath(os.path.join(root, file), tmp_dir),
                    )
        print(f"3-Layer OBG packaged to: {tcm_path}")

    try:
        shutil.rmtree(tmp_dir)
    except Exception:
        pass


if __name__ == "__main__":
    compile_compute_flow(ti.vulkan, "vulkan")


