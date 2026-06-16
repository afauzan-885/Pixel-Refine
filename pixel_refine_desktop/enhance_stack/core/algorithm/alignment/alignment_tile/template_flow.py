# template_flow.py - Generic Taichi Vulkan AOT Template for Optical Flow Algorithms
# This template provides a complete skeleton for building multi-level pyramid-based optical flow.
# You can customize the cost function and search logic inside the kernels below.

import taichi as ti
import numpy as np
import os
import shutil
import zipfile

# ==============================================================================
# 1. DEVICE MATH & COST FUNCTIONS (@ti.func)
# ==============================================================================
@ti.func
def bicubic_weight(x: ti.f32) -> ti.f32:
    """Weight function for bicubic interpolation."""
    abs_x = ti.abs(x)
    res = 0.0
    if abs_x <= 1.0:
        res = 1.5 * abs_x**3 - 2.5 * abs_x**2 + 1.0
    elif abs_x < 2.0:
        res = -0.5 * abs_x**3 + 2.5 * abs_x**2 - 4.0 * abs_x + 2.0
    return res


@ti.func
def custom_matching_cost(
    ref: ti.template(), 
    comp: ti.template(), 
    y_ref: ti.i32, 
    x_ref: ti.i32, 
    y_comp: ti.i32, 
    x_comp: ti.i32, 
    tile_h: ti.i32, 
    tile_w: ti.i32
) -> ti.f32:
    """
    CUSTOMIZABLE: Implement your matching metric here (SAD, SSD, NCC, Census, etc.).
    Returns a cost value where lower is better.
    """
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10  # High penalty default for out of bounds
    
    if 0 <= y_comp <= h_comp - tile_h and 0 <= x_comp <= w_comp - tile_w:
        sum_diff = 0.0
        for i, j in ti.ndrange(tile_h, tile_w):
            diff = ref[y_ref + i, x_ref + j] - comp[y_comp + i, x_comp + j]
            sum_diff += diff * diff  # SSD default example
        cost = sum_diff / float(tile_h * tile_w)
        
    return cost


# ==============================================================================
# 2. COMPUTE KERNELS (@ti.kernel)
# ==============================================================================
@ti.kernel
def initial_coarse_search_kernel(
    ref_layer: ti.types.ndarray(),
    comp_layer: ti.types.ndarray(),
    flow: ti.types.ndarray(),
    tile_h: ti.i32,
    tile_w: ti.i32,
    search_radius: ti.i32,
):
    """
    Level-2 / Coarsest scale search kernel. Performs full-range block search.
    """
    h, w = ref_layer.shape[0], ref_layer.shape[1]
    step_y, step_x = tile_h, tile_w  # Customize stride/overlap here

    for tile_y_idx, tile_x_idx in ti.ndrange(
        (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
    ):
        y = ti.max(0, ti.min(tile_y_idx * step_y, h - tile_h))
        x = ti.max(0, ti.min(tile_x_idx * step_x, w - tile_w))

        best_cost = 1e10
        best_dx = 0.0
        best_dy = 0.0

        for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
            cost = custom_matching_cost(ref_layer, comp_layer, y, x, y + dy, x + dx, tile_h, tile_w)
            if cost < best_cost:
                best_cost, best_dx, best_dy = cost, float(dx), float(dy)

        # Assign motion vector to all pixels in the tile
        for r, c in ti.ndrange(tile_h, tile_w):
            if y + r < h and x + c < w:
                flow[y + r, x + c, 0] = -best_dx
                flow[y + r, x + c, 1] = best_dy


@ti.kernel
def hierarchical_refine_kernel(
    ref_layer: ti.types.ndarray(),
    comp_layer: ti.types.ndarray(),
    flow: ti.types.ndarray(),
    previous_flow: ti.types.ndarray(),
    tile_h: ti.i32,
    tile_w: ti.i32,
    search_radius: ti.i32,
    downscale_factor: ti.i32,
):
    """
    Level-1 & Level-0 refinement kernel. Searches locally around the projected initial vectors.
    """
    h, w = ref_layer.shape[0], ref_layer.shape[1]
    prev_h, prev_w = previous_flow.shape[0], previous_flow.shape[1]
    step_y, step_x = tile_h, tile_w

    for tile_y_idx, tile_x_idx in ti.ndrange(
        (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
    ):
        y = ti.max(0, ti.min(tile_y_idx * step_y, h - tile_h))
        x = ti.max(0, ti.min(tile_x_idx * step_x, w - tile_w))
        center_y, center_x = y + tile_h // 2, x + tile_w // 2

        # 1. Project parent flow vectors to this level
        proj_dx = 0.0
        proj_dy = 0.0
        cy, cx = center_y // downscale_factor, center_x // downscale_factor
        if cy < prev_h and cx < prev_w:
            proj_dx = previous_flow[cy, cx, 0] * float(downscale_factor)
            proj_dy = previous_flow[cy, cx, 1] * float(downscale_factor)

        # 2. Local refinement around the projected vector
        best_cost = 1e10
        best_dx = proj_dx
        best_dy = proj_dy
        init_dx = ti.cast(ti.round(-proj_dx), ti.i32)
        init_dy = ti.cast(ti.round(proj_dy), ti.i32)

        for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
            cand_dy = init_dy + dy
            cand_dx = init_dx + dx
            cost = custom_matching_cost(ref_layer, comp_layer, y, x, y + cand_dy, x + cand_dx, tile_h, tile_w)
            if cost < best_cost:
                best_cost, best_dx, best_dy = cost, float(-cand_dx), float(cand_dy)

        # Assign motion vector to all pixels in the tile
        for r, c in ti.ndrange(tile_h, tile_w):
            if y + r < h and x + c < w:
                flow[y + r, x + c, 0] = best_dx
                flow[y + r, x + c, 1] = best_dy


@ti.kernel
def upsample_flow_bicubic_kernel(
    src: ti.types.ndarray(), 
    dst: ti.types.ndarray(), 
    scale: ti.f32
):
    """Upsamples motion vectors hierarchically between layers using bicubic interpolation."""
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
                    yy = ti.max(0, ti.min(y_int + m, h_src - 1))
                    xx = ti.max(0, ti.min(x_int + n, w_src - 1))
                    w_m = bicubic_weight(float(m) - y_fract)
                    w_n = bicubic_weight(float(n) - x_fract)
                    val += src[yy, xx, k] * w_m * w_n
            dst[i, j, k] = val * scale


# ==============================================================================
# 3. AOT GRAPH COMPILATION ENTRYPOINT
# ==============================================================================
def compile_template_flow():
    ti.init(arch=ti.vulkan)
    module = ti.aot.Module(ti.vulkan)

    # Define inputs for the 3-Layer Pyramid
    sym_ref_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l0", dtype=ti.f32, ndim=2)
    sym_ref_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l1", dtype=ti.f32, ndim=2)
    sym_ref_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l2", dtype=ti.f32, ndim=2)
    
    sym_comp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l0", dtype=ti.f32, ndim=2)
    sym_comp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l1", dtype=ti.f32, ndim=2)
    sym_comp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l2", dtype=ti.f32, ndim=2)
    
    sym_flow_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l0", dtype=ti.f32, ndim=3)
    sym_flow_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l1", dtype=ti.f32, ndim=3)
    sym_flow_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l2", dtype=ti.f32, ndim=3)

    sym_tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", dtype=ti.i32)
    sym_tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", dtype=ti.i32)
    sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32)
    sym_search_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "search_radius", dtype=ti.i32)
    sym_downscale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "downscale", dtype=ti.i32)

    g_builder = ti.graph.GraphBuilder()

    # Step 1: Initial Search at Coarsest Level L2
    g_builder.dispatch(
        initial_coarse_search_kernel,
        sym_ref_l2,
        sym_comp_l2,
        sym_flow_l2,
        sym_tile_h,
        sym_tile_w,
        sym_search_radius,
    )
    
    # Step 2: Upsample Flow from L2 to L1
    g_builder.dispatch(
        upsample_flow_bicubic_kernel, 
        sym_flow_l2, 
        sym_flow_l1, 
        sym_scale
    )
    
    # Step 3: Refine Flow at Level L1
    g_builder.dispatch(
        hierarchical_refine_kernel,
        sym_ref_l1,
        sym_comp_l1,
        sym_flow_l1,
        sym_flow_l2,
        sym_tile_h,
        sym_tile_w,
        sym_search_radius,
        sym_downscale,
    )
    
    # Step 4: Upsample Flow from L1 to L0
    g_builder.dispatch(
        upsample_flow_bicubic_kernel, 
        sym_flow_l1, 
        sym_flow_l0, 
        sym_scale
    )
    
    # Step 5: Final Refinement at Original Scale L0
    g_builder.dispatch(
        hierarchical_refine_kernel,
        sym_ref_l0,
        sym_comp_l0,
        sym_flow_l0,
        sym_flow_l1,
        sym_tile_h,
        sym_tile_w,
        sym_search_radius,
        sym_downscale,
    )

    module.add_graph("align_generic_3layer", g_builder.compile())

    # Build AOT Package directory
    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_aot_template"))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    
    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../../ui/data/aot_assets")
    )
    tcm_path = os.path.join(out_dir, "template_flow_vulkan.tcm")
    
    # Compress files into a Zip file (.tcm)
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as tcm_zip:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                tcm_zip.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), tmp_dir),
                )
    shutil.rmtree(tmp_dir)
    print(f"Generic Optical Flow template compiled and packaged to: {tcm_path}")


if __name__ == "__main__":
    compile_template_flow()
