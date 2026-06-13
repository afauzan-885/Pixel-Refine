import taichi as ti
import numpy as np
import os
import shutil
import zipfile
from .aot.cost_function import compute_zmssd_cost_func
from .aot.refinement import parabolic_refinement


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
def compute_regularization_params(
    flow: ti.template(), y: ti.i32, x: ti.i32, tile_h: ti.i32, tile_w: ti.i32
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
    avg_dx, avg_dy, lambda_val = 0.0, 0.0, 10.0  # Very strong for production stability
    if count > 0.0:
        avg_dx, avg_dy = sum_dx / count, sum_dy / count
        curr_dx, curr_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        diff_sq = (curr_dx - avg_dx) ** 2 + (curr_dy - avg_dy) ** 2
        if diff_sq > 9.0:
            lambda_val *= 4.0
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

        # 🚀 Perhitungan matematika berbasis Mean Absolute Difference (MAD) pada offset (0, 0)
        mad = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            y_ref, x_ref = y + r, x + c
            if 0 <= y_ref < h and 0 <= x_ref < w:
                mad += ti.abs(ref_layer[y_ref, x_ref] - comp_layer[y_ref, x_ref])
        mad /= ti.cast(tile_h * tile_w, ti.f32)

        # Normalisasi otomatis rentang piksel (jika input menggunakan rentang [0, 255])
        normalized_mad = mad
        if mad > 1.0:
            normalized_mad = mad / 255.0

        # Radius pencarian dinamis secara matematis
        local_search_radius = 0
        if normalized_mad >= 0.005:
            # Penskalaan linier: jika normalized_mad = 0.1, radius = 8
            val = normalized_mad * 80.0
            local_search_radius = ti.cast(ti.min(ti.cast(max_search_radius, ti.f32), ti.round(val)), ti.i32)

        best_cost, best_dx, best_dy = 1e10, 0.0, 0.0

        # Jika area statis (perbedaan temporal sangat kecil), local_search_radius bernilai 0
        for dy, dx in ti.ndrange(
            (-local_search_radius, local_search_radius + 1),
            (-local_search_radius, local_search_radius + 1),
        ):
            windowed_cost = 0.0
            window_sum = 0.0
            for r, c in ti.ndrange(tile_h, tile_w):
                y_ref, x_ref = y + r, x + c
                y_comp, x_comp = y + r + dy, x + c + dx
                if (
                    0 <= y_ref < h
                    and 0 <= x_ref < w
                    and 0 <= y_comp < h
                    and 0 <= x_comp < w
                ):
                    win = hanning_window_2d(r, c, tile_h, tile_w)
                    diff = ref_layer[y_ref, x_ref] - comp_layer[y_comp, x_comp]
                    windowed_cost += win * diff * diff
                    window_sum += win
            if window_sum > 1e-6:
                windowed_cost /= window_sum
            else:
                windowed_cost = 1e10

            if dx == 0 and dy == 0:
                windowed_cost *= 0.99
            if windowed_cost < best_cost:
                best_cost, best_dx, best_dy = windowed_cost, float(dx), float(dy)

        # ... (Sisa sub-pixel parabolic refinement Anda tetap sama di bawah) ...
        if (
            -local_search_radius < best_dx < local_search_radius
            and -local_search_radius < best_dy < local_search_radius
        ):
            c0 = best_cost
            cx_m1 = compute_zmssd_cost_func(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int(best_dy),
                x + int(best_dx) - 1,
                tile_h,
                tile_w,
                1,
            )
            cx_p1 = compute_zmssd_cost_func(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int(best_dy),
                x + int(best_dx) + 1,
                tile_h,
                tile_w,
                1,
            )
            cy_m1 = compute_zmssd_cost_func(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int(best_dy) - 1,
                x + int(best_dx),
                tile_h,
                tile_w,
                1,
            )
            cy_p1 = compute_zmssd_cost_func(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int(best_dy) + 1,
                x + int(best_dx),
                tile_h,
                tile_w,
                1,
            )
            best_dx += parabolic_refinement(cx_m1, c0, cx_p1)
            best_dy += parabolic_refinement(cy_m1, c0, cy_p1)
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
    # 50% overlap: step = tile_size / 2
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
        spatial_mean_dx, spatial_mean_dy, spatial_weight = (
            compute_regularization_params(flow, y, x, tile_h, tile_w)
        )
        init_dx, init_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        best_cand_dx, best_cand_dy, best_cand_cost = (
            ti.round(init_dx, ti.i32),
            ti.round(init_dy, ti.i32),
            1e10,
        )
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
                compute_zmssd_cost_func(
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
            for dy, dx in ti.ndrange(
                (-search_dist, search_dist + 1), (-search_dist, search_dist + 1)
            ):
                cur_dx, cur_dy = best_cand_dx + dx, best_cand_dy + dy
                visual_cost = (
                    compute_zmssd_cost_func(
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
    # 50% overlap: step = tile_size / 2
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
        spatial_mean_dx, spatial_mean_dy, spatial_weight = (
            compute_regularization_params(flow, y, x, tile_h, tile_w)
        )
        init_dx, init_dy = flow[center_y, center_x, 0], flow[center_y, center_x, 1]
        best_cand_dx, best_cand_dy, best_cand_cost = (
            ti.round(init_dx, ti.i32),
            ti.round(init_dy, ti.i32),
            1e10,
        )
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
                compute_zmssd_cost_func(
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
                    compute_zmssd_cost_func(
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
        c0 = compute_zmssd_cost_func(
            ref_layer, comp_layer, y, x, y + int_dy, x + int_dx, tile_h, tile_w, 1
        )
        c_m1_x = compute_zmssd_cost_func(
            ref_layer, comp_layer, y, x, y + int_dy, x + int_dx - 1, tile_h, tile_w, 1
        )
        c_p1_x = compute_zmssd_cost_func(
            ref_layer, comp_layer, y, x, y + int_dy, x + int_dx + 1, tile_h, tile_w, 1
        )
        c_m1_y = compute_zmssd_cost_func(
            ref_layer, comp_layer, y, x, y + int_dy - 1, x + int_dx, tile_h, tile_w, 1
        )
        c_p1_y = compute_zmssd_cost_func(
            ref_layer, comp_layer, y, x, y + int_dy + 1, x + int_dx, tile_h, tile_w, 1
        )
        final_dx, final_dy = float(int_dx) + parabolic_refinement(
            c_m1_x, c0, c_p1_x
        ), float(int_dy) + parabolic_refinement(c_m1_y, c0, c_p1_y)
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
def compile_compute_flow():
    ti.init(arch=ti.vulkan)
    module = ti.aot.Module(ti.vulkan)

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

    # block_search_kernel sekarang menghitung radius dinamis secara matematis dengan batas sym_max_search_radius
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

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_aot_flow"))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../../ui/data/aot_assets")
    )
    tcm_path = os.path.join(out_dir, "compute_flow_vulkan.tcm")
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as tcm_zip:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                tcm_zip.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), tmp_dir),
                )
    shutil.rmtree(tmp_dir)
    print(f"3-Layer OBG (High Precision Refined) packaged to: {tcm_path}")


if __name__ == "__main__":
    compile_compute_flow()
