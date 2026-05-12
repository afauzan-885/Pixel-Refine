# cost_function.py - Pure AOT Kernels for Alignment Costs
# Reference: alignment_tile.cpp (calculate_fine_analysis)

import taichi as ti

@ti.func
def compute_zmssd_cost_func(ref: ti.template(), comp: ti.template(), 
                           y_ref: ti.i32, x_ref: ti.i32, 
                           y_comp: ti.i32, x_comp: ti.i32,
                           tile_h: ti.i32, tile_w: ti.i32) -> ti.f32:
    """
    Device-side function version of ZMSSD for use inside other kernels.
    Mirroring C++ compute_zmssd_cost logic.
    """
    sum_diff = 0.0
    sum_sq_diff = 0.0
    num_pix = float(tile_h * tile_w)
    
    # Check boundaries for safety (Mirroring C++ safety check)
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10 # High penalty for out of bounds
    
    if y_comp >= 0 and y_comp + tile_h <= h_comp and x_comp >= 0 and x_comp + tile_w <= w_comp:
        for i, j in ti.ndrange(tile_h, tile_w):
            diff = ref[y_ref + i, x_ref + j] - comp[y_comp + i, x_comp + j]
            sum_diff += diff
            sum_sq_diff += diff * diff
        
        mean_diff = sum_diff / num_pix
        # Variance formula: Mean(diff^2) - Mean(diff)^2
        cost = (sum_sq_diff / num_pix) - (mean_diff * mean_diff)
        
    return ti.max(0.0, cost)

@ti.kernel
def compute_zmssd_kernel(ref: ti.types.ndarray(), comp: ti.types.ndarray(), 
                        h: ti.i32, w: ti.i32,
                        y_ref: ti.i32, x_ref: ti.i32, 
                        y_comp: ti.i32, x_comp: ti.i32,
                        tile_h: ti.i32, tile_w: ti.i32) -> ti.f32:
    """
    Exposed kernel for Python-side verification.
    """
    return compute_zmssd_cost_func(ref, comp, y_ref, x_ref, y_comp, x_comp, tile_h, tile_w)
