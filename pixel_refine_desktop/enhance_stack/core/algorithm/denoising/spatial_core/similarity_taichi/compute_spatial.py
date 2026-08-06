import numpy as np
import os
import shutil
import zipfile
import sys
import importlib

# If run directly for compilation, force JIT mode
if __name__ == "__main__":
    os.environ["AOT_MODE"] = "0"

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

calculate_hybrid_gradient_optimized = None
calculate_match_confidence = None

if TAICHI_AVAILABLE:
    # Support running directly or as a module
    if __name__ == "__main__" or __package__ is None:
        from block_matching import calculate_hybrid_gradient_optimized, calculate_match_confidence
    else:
        from .block_matching import calculate_hybrid_gradient_optimized, calculate_match_confidence
else:
    class DummyTi:
        i32 = "int"
        f32 = "float"
        def kernel(self, f): return f
        def func(self, f): return f
        class Types:
            def ndarray(self, *args, **kwargs): return "ndarray"
        types = Types()
    ti = DummyTi()

@ti.kernel
def precompute_gradients_kernel(
    img: ti.types.ndarray(),
    grad_x: ti.types.ndarray(),
    grad_y: ti.types.ndarray(),
    h: ti.i32,
    w: ti.i32
):
    """Precomputes Sobel DX and DY gradients for the entire image to avoid redundant calculations inside windows."""
    for y, x in ti.ndrange(h, w):
        if 0 < y < h - 1 and 0 < x < w - 1:
            gx_center = img[y, x + 1] - img[y, x - 1]
            gx_top = img[y - 1, x + 1] - img[y - 1, x - 1]
            gx_bottom = img[y + 1, x + 1] - img[y + 1, x - 1]
            grad_x[y, x] = (gx_center + gx_top + gx_bottom) * 0.333
            
            grad_y[y, x] = img[y + 1, x] - img[y - 1, x]
        else:
            grad_x[y, x] = 0.0
            grad_y[y, x] = 0.0

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
    coarse_grad_x: ti.types.ndarray(),
    coarse_grad_y: ti.types.ndarray(),
    ref_coarse_grad_x: ti.types.ndarray(),
    ref_coarse_grad_y: ti.types.ndarray(),
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
                current_coarse, reference_coarse,
                coarse_grad_x, coarse_grad_y,
                ref_coarse_grad_x, ref_coarse_grad_y,
                tile_y, tile_x,
                curr_h, curr_w, h_coarse, w_coarse,
                noise_sigma, 1.0, 1e-6, 0.0
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
    curr_grad_x: ti.types.ndarray(),
    curr_grad_y: ti.types.ndarray(),
    ref_grad_x: ti.types.ndarray(),
    ref_grad_y: ti.types.ndarray(),
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
    use_guidance: ti.i32,
    early_exit_threshold: ti.f32
):
    """Performs sliding window analysis for fine weight map accumulation on GPU."""
    pass_row_mod = pass_idx // 2
    pass_col_mod = pass_idx % 2
    
    num_rows = row_starts.shape[0]
    num_cols = col_starts.shape[0]
    
    limit_rows = (num_rows - pass_row_mod + 1) // 2
    limit_cols = (num_cols - pass_col_mod + 1) // 2
    for k, m in ti.ndrange(limit_rows, limit_cols):
        i = pass_row_mod + k * 2
        j = pass_col_mod + m * 2
        r = row_starts[i]
        c = col_starts[j]
        curr_h = ti.min(tile_h, h - r)
        curr_w = ti.min(tile_w, w - c)
        if curr_h > 0 and curr_w > 0:
            center_x = ti.min(c + curr_w // 2, w - 1)
            center_y = ti.min(r + curr_h // 2, h - 1)
            
            guidance_val = 1.0
            if use_guidance == 1:
                guidance_val = guidance_map[center_y, center_x]
                
            stab_val = 1.0
            if use_stability == 1:
                stab_val = stability_map[center_y, center_x]
                
            if guidance_val >= early_exit_threshold and stab_val >= early_exit_threshold:
                # Calculate local block contrast from reference patch
                ref_min = 1.0
                ref_max = 0.0
                # Highly optimized 5-point unrolled local contrast estimation (GPU register friendly)
                c_y = curr_h // 2
                c_x = curr_w // 2
                v0 = reference[r + c_y, c + c_x]
                v1 = reference[r, c]
                v2 = reference[r, c + curr_w - 1]
                v3 = reference[r + curr_h - 1, c]
                v4 = reference[r + curr_h - 1, c + curr_w - 1]
                
                ref_min = ti.min(v0, ti.min(v1, ti.min(v2, ti.min(v3, v4))))
                ref_max = ti.max(v0, ti.max(v1, ti.max(v2, ti.max(v3, v4))))
                contrast = ref_max - ref_min
                
                # Flat weight transition mapping with adaptive contrast limits based on local luma
                mean_luma = (v0 + v1 + v2 + v3 + v4) * 0.2
                contrast_limit = 0.12 * ti.max(0.05, mean_luma)
                contrast_range = 0.08 * ti.max(0.05, mean_luma)
                flat_weight = ti.max(0.0, ti.min(1.0, (contrast_limit - contrast) / contrast_range))
     
                mad_score = calculate_hybrid_gradient_optimized(
                    current, reference,
                    curr_grad_x, curr_grad_y,
                    ref_grad_x, ref_grad_y,
                    r, c, curr_h, curr_w, h, w,
                    noise_sigma, 1.0, 1e-6, flat_weight
                )
                
                confidence_fine = calculate_match_confidence(
                    mad_score, noise_sigma, motion_sensitivity, noise_offset_factor
                )
                
                final_conf = confidence_fine * guidance_val * stab_val
                
                if final_conf >= 1e-6:
                    for y, x in ti.ndrange(curr_h, curr_w):
                        wy = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(y) / float(tile_h - 1))) if tile_h > 1 else 1.0
                        wx = 0.5 * (1.0 - ti.cos(2.0 * 3.1415926535 * float(x) / float(tile_w - 1))) if tile_w > 1 else 1.0
                        wy = ti.max(wy, 1e-4)
                        wx = ti.max(wx, 1e-4)
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
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi is not available")
    print(f"\n>>> Compiling SPATIAL MERGING AOT for Vulkan")
    ti.init(arch=ti.vulkan, offline_cache=False)

    module = ti.aot.Module(ti.vulkan)

    # 0. Precompute Gradients Graph
    sym_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "img", dtype=ti.f32, ndim=2)
    sym_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grad_x", dtype=ti.f32, ndim=2)
    sym_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grad_y", dtype=ti.f32, ndim=2)
    sym_h_grad = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", dtype=ti.i32)
    sym_w_grad = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", dtype=ti.i32)

    g_grad = ti.graph.GraphBuilder()
    g_grad.dispatch(precompute_gradients_kernel, sym_img, sym_grad_x, sym_grad_y, sym_h_grad, sym_w_grad)
    module.add_graph("precompute_gradients", g_grad.compile())

    # Gradient symbols for reuse
    sym_curr_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "curr_grad_x", dtype=ti.f32, ndim=2)
    sym_curr_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "curr_grad_y", dtype=ti.f32, ndim=2)
    sym_ref_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_grad_x", dtype=ti.f32, ndim=2)
    sym_ref_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_grad_y", dtype=ti.f32, ndim=2)

    sym_coarse_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_grad_x", dtype=ti.f32, ndim=2)
    sym_coarse_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coarse_grad_y", dtype=ti.f32, ndim=2)
    sym_ref_coarse_grad_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_coarse_grad_x", dtype=ti.f32, ndim=2)
    sym_ref_coarse_grad_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_coarse_grad_y", dtype=ti.f32, ndim=2)

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
        sym_coarse_grad_x,
        sym_coarse_grad_y,
        sym_ref_coarse_grad_x,
        sym_ref_coarse_grad_y,
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
    sym_early_exit_threshold = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "early_exit_threshold", dtype=ti.f32)

    g_p2 = ti.graph.GraphBuilder()
    g_p2.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
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
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_fine_accum.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
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
    
    # 5b. Combined Fine Analysis 4 Passes
    g_4passes = ti.graph.GraphBuilder()
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    g_4passes.dispatch(
        phase2_fine_analysis_kernel,
        sym_current,
        sym_reference,
        sym_curr_grad_x,
        sym_curr_grad_y,
        sym_ref_grad_x,
        sym_ref_grad_y,
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
        sym_use_guidance,
        sym_early_exit_threshold
    )
    module.add_graph("generate_fine_weights_4passes", g_4passes.compile())

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


# -------------------------------------------------------------------------
# AOT Runtime Wrappers
# -------------------------------------------------------------------------
class SpatialScratchCache:
    """Reusable per-batch GPU scratch buffers for spatial analysis.

    The spatial algorithm is sequential per frame, so a scratch slot can be
    safely overwritten after the previous dispatch has completed.  Slots are
    keyed by purpose and shape; a resolution change transparently replaces
    only the incompatible slot.
    """

    def __init__(self):
        self._slots = {}
        self.reference_token = None

    def acquire(self, engine, name, shape, dtype=np.float32, **kwargs):
        shape = tuple(int(v) for v in shape)
        buf = self._slots.get(name)
        if buf is not None and tuple(buf.shape) == shape:
            return buf
        if buf is not None:
            try:
                buf.destroy()
            except Exception:
                pass
        buf = engine.allocate(shape, dtype=dtype, **kwargs)
        self._slots[name] = buf
        return buf

    def clear(self):
        for buf in self._slots.values():
            try:
                buf.destroy()
            except Exception:
                pass
        self._slots.clear()
        self.reference_token = None


def generate_spatial_weights_taichi(
    current_image,
    reference_image,
    weight_map_sum,
    base_window,
    stability_map,
    row_starts,
    col_starts,
    tile_h,
    tile_w,
    noise_sigma,
    motion_sensitivity,
    noise_offset_factor,
    equalize_brightness,
    buffer_provider,
    **kwargs,
):
    """
    Calculates the weight map for a single frame relative to the reference using Taichi AOT.
    """
    import taichi_library.taichi_aot as taichi_aot
    engine = taichi_aot.engine
    scratch = kwargs.get("scratch_cache")

    def _alloc(name, shape, dtype=np.float32, **alloc_kwargs):
        if scratch is not None:
            return scratch.acquire(engine, name, shape, dtype=dtype, **alloc_kwargs)
        return engine.allocate(shape, dtype=dtype, **alloc_kwargs)

    def _destroy(buf):
        if scratch is None and buf is not None:
            buf.destroy()

    # Load Module
    file_dir = os.path.dirname(os.path.abspath(__file__))
    cur = os.path.abspath(file_dir)
    while os.path.basename(cur) != "pixel_refine_desktop" and len(cur) > 4:
        cur = os.path.dirname(cur)
    tcm_path = os.path.abspath(os.path.join(cur, "ui/data/aot_assets/spatial_vulkan.tcm"))
    mod = engine.load(tcm_path)

    import time
    profile_hotspots = kwargs.get("profile_hotspots", False) or os.environ.get("PROFILE_SPATIAL", "0") == "1"
    hotspots = {}

    t_start = time.perf_counter()

    # 1. Reset weight map sum to 0
    zeros = np.zeros(weight_map_sum.shape, dtype=np.float32)
    from taichi_library.taichi_aot.engine import _LIB, _RUNTIME
    _LIB.write_to_gpu_buffer(_RUNTIME, weight_map_sum.handle, zeros.ctypes.data, weight_map_sum.size_bytes)

    if profile_hotspots:
        engine.sync()
        hotspots["1. Reset weight map"] = (time.perf_counter() - t_start) * 1000
        t_prev = time.perf_counter()
    else:
        t_prev = 0.0

    h, w = current_image.shape[0], current_image.shape[1]
    coarse_texture_boost = float(kwargs.get("coarse_texture_boost", 0.30))
    coarse_texture_radius = float(kwargs.get("coarse_texture_radius", 10.0))
    reference_token = (
        getattr(reference_image, "handle", id(reference_image)),
        int(h),
        int(w),
        round(coarse_texture_boost, 6),
        round(coarse_texture_radius, 6),
    )
    reference_cache_names = ["ref_l1", "ref_l2"]
    if coarse_texture_boost > 1e-6:
        reference_cache_names.append("ref_texture_boost")
    reuse_reference = (
        scratch is not None
        and scratch.reference_token == reference_token
        and all(name in scratch._slots for name in reference_cache_names)
    )

    # 2. Coarse texture boost for analysis only.  This never modifies the
    # source RGB frame or the output merge; it only improves texture evidence
    # used by the weight-map kernels.  The invariant reference result is
    # cached for the complete batch.
    curr_texture_boost = None
    if coarse_texture_boost > 1e-6:
        curr_texture_boost = _alloc("curr_texture_boost", (h, w), dtype=np.float32)
        taichi_aot.coarse_texture_boost_gpu(
            current_image,
            texture_amount=coarse_texture_boost,
            radius=coarse_texture_radius,
            dst=curr_texture_boost,
        )

        if reuse_reference:
            ref_texture_boost = scratch._slots["ref_texture_boost"]
        else:
            ref_texture_boost = _alloc("ref_texture_boost", (h, w), dtype=np.float32)
            taichi_aot.coarse_texture_boost_gpu(
                reference_image,
                texture_amount=coarse_texture_boost,
                radius=coarse_texture_radius,
                dst=ref_texture_boost,
            )
    else:
        curr_texture_boost = current_image
        ref_texture_boost = reference_image

    # 3. Brightness Equalization (Optional)
    analysis_input = curr_texture_boost
    analysis_reference = ref_texture_boost
    eq_temp = None
    if equalize_brightness:
        eq_temp = _alloc("equalize", (h, w), dtype=np.float32)
        mod.run("equalize_brightness", src=analysis_input, ref=analysis_reference, dst=eq_temp, h=int(h), w=int(w))
        analysis_input = eq_temp

    if profile_hotspots:
        engine.sync()
        hotspots["2. Brightness Equalization"] = (time.perf_counter() - t_prev) * 1000
        t_prev = time.perf_counter()

    # 4. Phase 1: Coarse Analysis for Guidance Map (Level 2: 1/4 Resolution)
    # Downscale in two steps (L0 -> L1 -> L2) to prevent aliasing
    curr_l0 = analysis_input
    curr_l1 = taichi_aot.resize(curr_l0, (w // 2, h // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                 dst=_alloc("curr_l1", (h // 2, w // 2)))
    curr_l2 = taichi_aot.resize(curr_l1, (w // 4, h // 4), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                 dst=_alloc("curr_l2", (h // 4, w // 4)))

    if reuse_reference:
        ref_l1 = scratch._slots["ref_l1"]
        ref_l2 = scratch._slots["ref_l2"]
    else:
        ref_l0 = analysis_reference
        ref_l1 = taichi_aot.resize(ref_l0, (w // 2, h // 2), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                   dst=_alloc("ref_l1", (h // 2, w // 2)))
        ref_l2 = taichi_aot.resize(ref_l1, (w // 4, h // 4), interpolation=taichi_aot.INTER_LINEAR, return_gpu=True,
                                   dst=_alloc("ref_l2", (h // 4, w // 4)))

    if profile_hotspots:
        engine.sync()
        hotspots["3a. Downscaling Pyramids"] = (time.perf_counter() - t_prev) * 1000
        t_prev = time.perf_counter()

    guidance_gpu = None
    level_conf_gpu = None
    curr_coarse_grad_x = None
    curr_coarse_grad_y = None
    ref_coarse_grad_x = None
    ref_coarse_grad_y = None

    try:
        # Run coarse analysis ONLY at the coarsest level (Level 2) to match C++
        curr_level = curr_l2
        ref_level = ref_l2

        h_level, w_level = curr_level.shape[0], curr_level.shape[1]

        # Allocate coarse gradients
        curr_coarse_grad_x = _alloc("curr_coarse_grad_x", (h_level, w_level))
        curr_coarse_grad_y = _alloc("curr_coarse_grad_y", (h_level, w_level))
        ref_coarse_grad_x = _alloc("ref_coarse_grad_x", (h_level, w_level))
        ref_coarse_grad_y = _alloc("ref_coarse_grad_y", (h_level, w_level))

        # Run precompute_gradients on coarse level
        mod.run("precompute_gradients", img=curr_level, grad_x=curr_coarse_grad_x, grad_y=curr_coarse_grad_y, h=int(h_level), w=int(w_level))
        if not reuse_reference:
            mod.run("precompute_gradients", img=ref_level, grad_x=ref_coarse_grad_x, grad_y=ref_coarse_grad_y, h=int(h_level), w=int(w_level))

        if profile_hotspots:
            engine.sync()
            hotspots["3b. Coarse Gradients Precompute"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        if scratch is not None and not reuse_reference:
            scratch.reference_token = reference_token

        scale_factor = h_level / h
        level_tile_h = max(8, int(tile_h * scale_factor))
        level_tile_w = max(8, int(tile_w * scale_factor))

        num_tiles_h = max(1, h_level // level_tile_h)
        num_tiles_w = max(1, w_level // level_tile_w)

        level_conf_gpu = _alloc("level_conf", (num_tiles_h, num_tiles_w))

        mod.run(
            "phase1_coarse_analysis",
            current_coarse=curr_level,
            reference_coarse=ref_level,
            coarse_grad_x=curr_coarse_grad_x,
            coarse_grad_y=curr_coarse_grad_y,
            ref_coarse_grad_x=ref_coarse_grad_x,
            ref_coarse_grad_y=ref_coarse_grad_y,
            coarse_confidence=level_conf_gpu,
            coarse_tile_h=int(level_tile_h),
            coarse_tile_w=int(level_tile_w),
            h_coarse=int(h_level),
            w_coarse=int(w_level),
            noise_sigma=float(noise_sigma),
            motion_sensitivity=float(motion_sensitivity),
            noise_offset_factor=float(noise_offset_factor),
        )

        if profile_hotspots:
            engine.sync()
            hotspots["3c. Phase 1 Coarse Analysis Kernel"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        # Upsample coarse tile grid to Level 2 resolution
        guidance_gpu = taichi_aot.resize(
            level_conf_gpu,
            (w_level, h_level),
            interpolation=taichi_aot.INTER_CUBIC,
            return_gpu=True,
            dst=_alloc("guidance_level", (h_level, w_level)),
        )

        # Final upsample from Level 2 resolution to full resolution
        if guidance_gpu is not None and (
            guidance_gpu.shape[0] != h or guidance_gpu.shape[1] != w
        ):
            final_guidance = taichi_aot.resize(
                guidance_gpu, (w, h), interpolation=taichi_aot.INTER_CUBIC, return_gpu=True
                , dst=_alloc("guidance_full", (h, w))
            )
            _destroy(guidance_gpu)
            guidance_gpu = final_guidance

        if profile_hotspots:
            engine.sync()
            hotspots["3d. Guidance Map Upsampling & Resize"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

    finally:
        # Cleanup pyramids and temp buffers
        _destroy(curr_l1)
        _destroy(curr_l2)
        _destroy(ref_l1)
        _destroy(ref_l2)
        if curr_coarse_grad_x is not None:
            _destroy(curr_coarse_grad_x)
        if curr_coarse_grad_y is not None:
            _destroy(curr_coarse_grad_y)
        if ref_coarse_grad_x is not None:
            _destroy(ref_coarse_grad_x)
        if ref_coarse_grad_y is not None:
            _destroy(ref_coarse_grad_y)
        if level_conf_gpu is not None:
            _destroy(level_conf_gpu)

        if profile_hotspots:
            engine.sync()
            hotspots["3e. Coarse Temp Cleanup"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

    # 4. Phase 2: Fine Analysis (Sliding Window MAD)
    use_stability = 1 if stability_map is not None else 0
    dummy_gpu = None
    if stability_map is None:
        dummy_gpu = _alloc("dummy_stability", (1, 1), dtype=np.float32)
        stability_map = dummy_gpu

    curr_grad_x = None
    curr_grad_y = None
    ref_grad_x = None
    ref_grad_y = None

    try:
        # Allocate fine gradients
        curr_grad_x = _alloc("curr_grad_x", (h, w))
        curr_grad_y = _alloc("curr_grad_y", (h, w))
        ref_grad_x = _alloc("ref_grad_x", (h, w))
        ref_grad_y = _alloc("ref_grad_y", (h, w))

        # Run precompute_gradients on fine level
        mod.run("precompute_gradients", img=analysis_input, grad_x=curr_grad_x, grad_y=curr_grad_y, h=int(h), w=int(w))
        if not reuse_reference:
            mod.run("precompute_gradients", img=analysis_reference, grad_x=ref_grad_x, grad_y=ref_grad_y, h=int(h), w=int(w))

        if profile_hotspots:
            engine.sync()
            hotspots["4a. Fine Gradients Precompute"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()

        # Extract early_exit_threshold from kwargs
        early_exit_threshold = float(kwargs.get("early_exit_threshold", 0.05))

        mod.run(
            "generate_fine_weights_4passes",
            current=analysis_input,
            reference=analysis_reference,
            curr_grad_x=curr_grad_x,
            curr_grad_y=curr_grad_y,
            ref_grad_x=ref_grad_x,
            ref_grad_y=ref_grad_y,
            guidance_map=guidance_gpu,
            stability_map=stability_map,
            weight_map_sum=weight_map_sum,
            base_window=0,
            row_starts=row_starts,
            col_starts=col_starts,
            pass_idx_0=0,
            pass_idx_1=1,
            pass_idx_2=2,
            pass_idx_3=3,
            tile_h=int(tile_h),
            tile_w=int(tile_w),
            h=int(h),
            w=int(w),
            noise_sigma=float(noise_sigma),
            motion_sensitivity=float(motion_sensitivity),
            noise_offset_factor=float(noise_offset_factor),
            use_stability=int(use_stability),
            use_guidance=1,
            early_exit_threshold=early_exit_threshold,
        )

        if profile_hotspots:
            engine.sync()
            hotspots["4b. Phase 2 Fine Analysis (4-Pass Kernel)"] = (time.perf_counter() - t_prev) * 1000
            t_prev = time.perf_counter()
    finally:
        if curr_grad_x is not None:
            _destroy(curr_grad_x)
        if curr_grad_y is not None:
            _destroy(curr_grad_y)
        if ref_grad_x is not None:
            _destroy(ref_grad_x)
        if ref_grad_y is not None:
            _destroy(ref_grad_y)
        if dummy_gpu is not None:
            _destroy(dummy_gpu)
        if guidance_gpu is not None:
            _destroy(guidance_gpu)
        if eq_temp is not None:
            _destroy(eq_temp)
        if coarse_texture_boost > 1e-6:
            _destroy(curr_texture_boost)
            if not reuse_reference:
                _destroy(ref_texture_boost)

        if profile_hotspots:
            engine.sync()
            hotspots["4c. Fine Cleanup"] = (time.perf_counter() - t_prev) * 1000
            total_t = (time.perf_counter() - t_start) * 1000
            print("\n" + "="*60)
            print(" SPATIAL FUSION HOTSPOT PROFILING (ms)")
            print("="*60)
            for k, v in hotspots.items():
                print(f" {k:<45} : {v:>8.2f} ms ({v/total_t*100.0:>5.1f}%)")
            print("-"*60)
            print(f" {'Total GPU Wrapper Time':<45} : {total_t:>8.2f} ms")
            print("="*60 + "\n")


def accumulate_spatial_merging_taichi(
    current_image_full,
    weight_map_work,
    final_image_sum,
    weight_map_sum_full,
    **kwargs,
):
    """
    Accumulates a frame into the global sum using its processed weight map using Taichi AOT.
    """
    import taichi_library.taichi_aot as taichi_aot
    engine = taichi_aot.engine

    # Load Module
    file_dir = os.path.dirname(os.path.abspath(__file__))
    cur = os.path.abspath(file_dir)
    while os.path.basename(cur) != "pixel_refine_desktop" and len(cur) > 4:
        cur = os.path.dirname(cur)
    tcm_path = os.path.abspath(os.path.join(cur, "ui/data/aot_assets/spatial_vulkan.tcm"))
    mod = engine.load(tcm_path)

    h_full, w_full = final_image_sum.shape[0], final_image_sum.shape[1]
    h_work, w_work = weight_map_work.shape[0], weight_map_work.shape[1]
    num_channels = final_image_sum.shape[2]

    mod.run(
        "accumulate_spatial_merging",
        current_image_full=current_image_full,
        weight_map_work=weight_map_work,
        final_image_sum=final_image_sum,
        weight_map_sum_full=weight_map_sum_full,
        h_full=int(h_full),
        w_full=int(w_full),
        h_work=int(h_work),
        w_work=int(w_work),
        num_channels=int(num_channels),
    )
