import taichi as ti
import numpy as np
import os
import shutil
import zipfile
import sys

# Support running directly or as a module
if __name__ == "__main__" or __package__ is None:
    from block_matching import calculate_hybrid_gradient_optimized, calculate_match_confidence
else:
    from .block_matching import calculate_hybrid_gradient_optimized, calculate_match_confidence

@ti.kernel
def equalize_brightness_kernel(
    src: ti.types.ndarray(),
    ref: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32
):
    """Calculates global average ratio between src and ref and applies gain to dst."""
    sum_ref = 0.0
    sum_src = 0.0
    for i, j in ti.ndrange(h, w):
        sum_ref += ref[i, j]
        sum_src += src[i, j]
        
    ratio = 1.0
    if sum_src > 1e-5:
        ratio = sum_ref / sum_src
    
    # Clamp gain to [0.6, 1.8] to avoid extreme scaling
    ratio = ti.max(0.6, ti.min(1.8, ratio))
    
    for i, j in ti.ndrange(h, w):
        dst[i, j] = src[i, j] * ratio

@ti.kernel
def phase1_coarse_analysis_kernel(
    current_coarse: ti.types.ndarray(),
    reference_coarse: ti.types.ndarray(),
    coarse_confidence: ti.types.ndarray(),
    coarse_tile_h: ti.i32,
    coarse_tile_w: ti.i32,
    h_coarse: ti.i32,
    w_coarse: ti.i32,
    noise_sigma: ti.f32,
    motion_sensitivity: ti.f32,
    noise_offset_factor: ti.f32
):
    """Generates a coarse confidence map using hybrid gradient similarity."""
    for r, c in coarse_confidence:
        tile_y = r * coarse_tile_h
        tile_x = c * coarse_tile_w
        curr_h = ti.min(coarse_tile_h, h_coarse - tile_y)
        curr_w = ti.min(coarse_tile_w, w_coarse - tile_x)
        
        if curr_h > 0 and curr_w > 0:
            mad_score = calculate_hybrid_gradient_optimized(
                current_coarse, reference_coarse, tile_y, tile_x,
                curr_h, curr_w, h_coarse, w_coarse,
                noise_sigma, 1.0, 1e-6
            )
            
            diff_ratio = mad_score / ti.max(1e-6, noise_sigma)
            adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
            exponent = adjusted * motion_sensitivity * 0.5
            
            conf = 0.0
            if exponent <= 20.0:
                conf = 1.0 / (1.0 + ti.exp(exponent - 2.0))
                
            coarse_confidence[r, c] = conf
        else:
            coarse_confidence[r, c] = 0.0

@ti.kernel
def phase2_fine_analysis_kernel(
    current: ti.types.ndarray(),
    reference: ti.types.ndarray(),
    guidance_map: ti.types.ndarray(),
    stability_map: ti.types.ndarray(),
    weight_map_sum: ti.types.ndarray(),
    base_window: ti.i32, # Deprecated but kept for signature compatibility
    row_starts: ti.types.ndarray(),
    col_starts: ti.types.ndarray(),
    pass_idx: ti.i32,
    tile_h: ti.i32,
    tile_w: ti.i32,
    h: ti.i32,
    w: ti.i32,
    noise_sigma: ti.f32,
    motion_sensitivity: ti.f32,
    noise_offset_factor: ti.f32,
    use_stability: ti.i32,
    use_guidance: ti.i32
):
    """Performs sliding window analysis for fine weight map accumulation on GPU."""
    pass_row_mod = pass_idx // 2
    pass_col_mod = pass_idx % 2
    
    num_rows = row_starts.shape[0]
    num_cols = col_starts.shape[0]
    
    for i, j in ti.ndrange(num_rows, num_cols):
        if (i % 2 == pass_row_mod) and (j % 2 == pass_col_mod):
            r = row_starts[i]
            c = col_starts[j]
            curr_h = ti.min(tile_h, h - r)
            curr_w = ti.min(tile_w, w - c)
            
            if curr_h > 0 and curr_w > 0:
                mad_score = calculate_hybrid_gradient_optimized(
                    current, reference, r, c, curr_h, curr_w, h, w,
                    noise_sigma, 1.0, 1e-6
                )
                
                confidence_fine = calculate_match_confidence(
                    mad_score, noise_sigma, motion_sensitivity, noise_offset_factor
                )
                
                center_x = ti.min(c + curr_w // 2, w - 1)
                center_y = ti.min(r + curr_h // 2, h - 1)
                
                guidance_val = 1.0
                if use_guidance == 1:
                    guidance_val = guidance_map[center_y, center_x]
                    
                stab_val = 1.0
                if use_stability == 1:
                    stab_val = stability_map[center_y, center_x]
                    
                final_conf = confidence_fine * guidance_val * stab_val
                
                if final_conf >= 1e-6:
                    for y, x in ti.ndrange(curr_h, curr_w):
                        wy = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(y) / float(tile_h - 1))) if tile_h > 1 else 1.0
                        wx = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(x) / float(tile_w - 1))) if tile_w > 1 else 1.0
                        w_val = wy * wx
                        
                        weight_map_sum[r + y, c + x] += w_val * final_conf

@ti.kernel
def accumulate_spatial_merging_kernel(
    current_image_full: ti.types.ndarray(),
    weight_map_work: ti.types.ndarray(),
    final_image_sum: ti.types.ndarray(),
    weight_map_sum_full: ti.types.ndarray(),
    h_full: ti.i32,
    w_full: ti.i32,
    h_work: ti.i32,
    w_work: ti.i32,
    num_channels: ti.i32
):
    """Bilinearly interpolates work resolution weights to full resolution and accumulates frames."""
    for i, j in ti.ndrange(h_full, w_full):
        # Map full-res coordinates to work-res coordinates (floating point)
        y_work_f = float(i) * float(h_work) / float(h_full)
        x_work_f = float(j) * float(w_work) / float(w_full)
        
        # Bilinear interpolation bounds
        y0 = ti.cast(ti.floor(y_work_f), ti.i32)
        x0 = ti.cast(ti.floor(x_work_f), ti.i32)
        y1 = ti.min(y0 + 1, h_work - 1)
        x1 = ti.min(x0 + 1, w_work - 1)
        y0 = ti.max(0, y0)
        x0 = ti.max(0, x0)
        
        wy = y_work_f - float(y0)
        wx = x_work_f - float(x0)
        
        # Compute bilinearly interpolated weight
        w_val = (
            (1.0 - wy) * (1.0 - wx) * weight_map_work[y0, x0] +
            (1.0 - wy) * wx * weight_map_work[y0, x1] +
            wy * (1.0 - wx) * weight_map_work[y1, x0] +
            wy * wx * weight_map_work[y1, x1]
        )
        
        weight_map_sum_full[i, j] += w_val
        for c in range(num_channels):
            final_image_sum[i, j, c] += current_image_full[i, j, c] * w_val

def compile_spatial_tcm():
    print(f"\n>>> Compiling SPATIAL MERGING AOT for Vulkan")
    ti.init(arch=ti.vulkan, offline_cache=False)

    module = ti.aot.Module(ti.vulkan)

    # 1. Equalize Brightness Graph
    sym_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype=ti.f32, ndim=2)
    sym_ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", dtype=ti.f32, ndim=2)
    sym_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype=ti.f32, ndim=2)
    sym_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)

    g_eq = ti.graph.GraphBuilder()
    g_eq.dispatch(equalize_brightness_kernel, sym_src, sym_ref, sym_dst, sym_h, sym_w)
    module.add_graph("equalize_brightness", g_eq.compile())

    # 2. Phase 1 Coarse Analysis Graph
    sym_curr_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current_coarse", dtype=ti.f32, ndim=2)
    sym_ref_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference_coarse", dtype=ti.f32, ndim=2)
    sym_coarse_conf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_confidence", dtype=ti.f32, ndim=2)
    sym_coarse_tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_tile_h", dtype=ti.i32)
    sym_coarse_tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "coarse_tile_w", dtype=ti.i32)
    sym_h_coarse = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_coarse", dtype=ti.i32)
    sym_w_coarse = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_coarse", dtype=ti.i32)
    sym_noise_sigma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "noise_sigma", dtype=ti.f32)
    sym_motion_sens = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "motion_sensitivity", dtype=ti.f32)
    sym_noise_offset = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "noise_offset_factor", dtype=ti.f32)

    g_p1 = ti.graph.GraphBuilder()
    g_p1.dispatch(
        phase1_coarse_analysis_kernel,
        sym_curr_coarse,
        sym_ref_coarse,
        sym_coarse_conf,
        sym_coarse_tile_h,
        sym_coarse_tile_w,
        sym_h_coarse,
        sym_w_coarse,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset
    )
    module.add_graph("phase1_coarse_analysis", g_p1.compile())

    # 3. Phase 2 Fine Analysis Graph (Individual)
    sym_current = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current", dtype=ti.f32, ndim=2)
    sym_reference = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reference", dtype=ti.f32, ndim=2)
    sym_guidance_map = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guidance_map", dtype=ti.f32, ndim=2)
    sym_stability_map = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "stability_map", dtype=ti.f32, ndim=2)
    sym_weight_map_sum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_sum", dtype=ti.f32, ndim=2)
    sym_base_window = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "base_window", dtype=ti.i32)
    sym_row_starts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "row_starts", dtype=ti.i32, ndim=1)
    sym_col_starts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "col_starts", dtype=ti.i32, ndim=1)
    sym_pass_idx = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx", dtype=ti.i32)
    sym_tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", dtype=ti.i32)
    sym_tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", dtype=ti.i32)
    sym_h_fine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w_fine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)
    sym_use_stability = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_stability", dtype=ti.i32)
    sym_use_guidance = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_guidance", dtype=ti.i32)

    g_p2 = ti.graph.GraphBuilder()
    g_p2.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_guidance_map,
        sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts,
        sym_col_starts,
        sym_pass_idx,
        sym_tile_h,
        sym_tile_w,
        sym_h_fine,
        sym_w_fine,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset,
        sym_use_stability,
        sym_use_guidance
    )
    module.add_graph("phase2_fine_analysis", g_p2.compile())

    # 4. Accumulate Spatial Merging Graph (Individual)
    sym_curr_img_full = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "current_image_full", dtype=ti.f32, ndim=3)
    sym_weight_work = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_work", dtype=ti.f32, ndim=2)
    sym_final_img_sum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "final_image_sum", dtype=ti.f32, ndim=3)
    sym_weight_sum_full = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_map_sum_full", dtype=ti.f32, ndim=2)
    sym_h_full = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_full", dtype=ti.i32)
    sym_w_full = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_full", dtype=ti.i32)
    sym_h_work = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_work", dtype=ti.i32)
    sym_w_work = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_work", dtype=ti.i32)
    sym_num_channels = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "num_channels", dtype=ti.i32)

    g_accum = ti.graph.GraphBuilder()
    g_accum.dispatch(
        accumulate_spatial_merging_kernel,
        sym_curr_img_full,
        sym_weight_work,
        sym_final_img_sum,
        sym_weight_sum_full,
        sym_h_full,
        sym_w_full,
        sym_h_work,
        sym_w_work,
        sym_num_channels
    )
    module.add_graph("accumulate_spatial_merging", g_accum.compile())

    # 5. Combined Fine Analysis and Accumulate Graph
    sym_pass_idx_0 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_0", dtype=ti.i32)
    sym_pass_idx_1 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_1", dtype=ti.i32)
    sym_pass_idx_2 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_2", dtype=ti.i32)
    sym_pass_idx_3 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "pass_idx_3", dtype=ti.i32)

    g_fine_accum = ti.graph.GraphBuilder()
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_guidance_map,
        sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts,
        sym_col_starts,
        sym_pass_idx_0,
        sym_tile_h,
        sym_tile_w,
        sym_h_fine,
        sym_w_fine,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset,
        sym_use_stability,
        sym_use_guidance
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_guidance_map,
        sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts,
        sym_col_starts,
        sym_pass_idx_1,
        sym_tile_h,
        sym_tile_w,
        sym_h_fine,
        sym_w_fine,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset,
        sym_use_stability,
        sym_use_guidance
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_guidance_map,
        sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts,
        sym_col_starts,
        sym_pass_idx_2,
        sym_tile_h,
        sym_tile_w,
        sym_h_fine,
        sym_w_fine,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset,
        sym_use_stability,
        sym_use_guidance
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_guidance_map,
        sym_stability_map,
        sym_weight_map_sum,
        sym_base_window,
        sym_row_starts,
        sym_col_starts,
        sym_pass_idx_3,
        sym_tile_h,
        sym_tile_w,
        sym_h_fine,
        sym_w_fine,
        sym_noise_sigma,
        sym_motion_sens,
        sym_noise_offset,
        sym_use_stability,
        sym_use_guidance
    )
    g_fine_accum.dispatch(
        accumulate_spatial_merging_kernel,
        sym_curr_img_full,
        sym_weight_map_sum, # weight_map_work
        sym_final_img_sum,
        sym_weight_sum_full,
        sym_h_full,
        sym_w_full,
        sym_h_work,
        sym_w_work,
        sym_num_channels
    )
    module.add_graph("fine_analysis_and_accumulate", g_fine_accum.compile())

    # Save AOT module to temporary directory, package into ZIP (.tcm), and cleanup
    file_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.abspath(os.path.join(file_dir, "tmp_aot_spatial"))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)

    # Find the pixel_refine_desktop root folder to ensure correct assets output path
    cur = os.path.abspath(file_dir)
    while os.path.basename(cur) != "pixel_refine_desktop" and len(cur) > 4:
        cur = os.path.dirname(cur)
    out_dir = os.path.abspath(os.path.join(cur, "ui/data/aot_assets"))
    os.makedirs(out_dir, exist_ok=True)
    tcm_path = os.path.join(out_dir, "spatial_vulkan.tcm")

    with zipfile.ZipFile(tcm_path, 'w', zipfile.ZIP_DEFLATED) as tcm_zip:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                tcm_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), tmp_dir))
    
    shutil.rmtree(tmp_dir)
    print(f"Spatial AOT packaged successfully to: {tcm_path}")

if __name__ == "__main__":
    compile_spatial_tcm()
