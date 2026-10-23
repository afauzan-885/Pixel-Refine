# cost_function.py - Pure AOT Kernels for Alignment Costs
import taichi as ti

@ti.func
def compute_ssd_cost_func(ref: ti.template(), comp: ti.template(), 
                          y_ref: ti.i32, x_ref: ti.i32, 
                          y_comp: ti.i32, x_comp: ti.i32,
                          tile_h: ti.i32, tile_w: ti.i32,
                          stride: ti.template(),
                          max_cost_threshold: ti.f32 = 1e10) -> ti.f32:
    """
    Device-side function version of standard SSD (Sum of Squared Differences) for use inside other kernels.
    Includes early-distortion termination when partial sum exceeds max_cost_threshold.
    """
    sum_sq_diff = 0.0
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10
    
    if y_comp >= 0 and y_comp + tile_h <= h_comp and x_comp >= 0 and x_comp + tile_w <= w_comp:
        n_i = (tile_h + stride - 1) // stride
        n_j = (tile_w + stride - 1) // stride
        total_samples = float(n_i * n_j)
        threshold_sum = max_cost_threshold * total_samples
        
        for i in range(n_i):
            for j in range(n_j):
                diff = ref[y_ref + i * stride, x_ref + j * stride] - comp[y_comp + i * stride, x_comp + j * stride]
                sum_sq_diff += diff * diff
            if sum_sq_diff >= threshold_sum:
                sum_sq_diff = 1e10 * total_samples
                break
        
        cost = sum_sq_diff / total_samples
        
    return ti.max(0.0, cost)

@ti.func
def compute_sad_cost_func(ref: ti.template(), comp: ti.template(), 
                          y_ref: ti.i32, x_ref: ti.i32, 
                          y_comp: ti.i32, x_comp: ti.i32,
                          tile_h: ti.i32, tile_w: ti.i32,
                          stride: ti.template(),
                          max_cost_threshold: ti.f32 = 1e10) -> ti.f32:
    """
    Device-side function version of standard SAD (Sum of Absolute Differences) for use inside other kernels.
    Includes early-distortion termination when partial sum exceeds max_cost_threshold.
    """
    sum_abs_diff = 0.0
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10
    
    if y_comp >= 0 and y_comp + tile_h <= h_comp and x_comp >= 0 and x_comp + tile_w <= w_comp:
        n_i = (tile_h + stride - 1) // stride
        n_j = (tile_w + stride - 1) // stride
        total_samples = float(n_i * n_j)
        threshold_sum = max_cost_threshold * total_samples
        
        for i in range(n_i):
            for j in range(n_j):
                diff = ref[y_ref + i * stride, x_ref + j * stride] - comp[y_comp + i * stride, x_comp + j * stride]
                sum_abs_diff += ti.abs(diff)
            if sum_abs_diff >= threshold_sum:
                sum_abs_diff = 1e10 * total_samples
                break
            
        cost = sum_abs_diff / total_samples
        
    return ti.max(0.0, cost)

@ti.kernel
def compute_ssd_kernel(ref: ti.types.ndarray(), comp: ti.types.ndarray(), 
                       h: ti.i32, w: ti.i32,
                       y_ref: ti.i32, x_ref: ti.i32, 
                       y_comp: ti.i32, x_comp: ti.i32,
                       tile_h: ti.i32, tile_w: ti.i32) -> ti.f32:
    """
    Exposed kernel for Python-side verification.
    """
    return compute_ssd_cost_func(ref, comp, y_ref, x_ref, y_comp, x_comp, tile_h, tile_w, 2)
