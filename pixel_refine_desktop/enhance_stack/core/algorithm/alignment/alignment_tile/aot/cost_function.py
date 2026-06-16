# cost_function.py - Pure AOT Kernels for Alignment Costs
import taichi as ti

@ti.func
def compute_ssd_cost_func(ref: ti.template(), comp: ti.template(), 
                          y_ref: ti.i32, x_ref: ti.i32, 
                          y_comp: ti.i32, x_comp: ti.i32,
                          tile_h: ti.i32, tile_w: ti.i32,
                          stride: ti.template()) -> ti.f32:
    """
    Device-side function version of standard SSD (Sum of Squared Differences) for use inside other kernels.
    """
    sum_sq_diff = 0.0
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10
    
    if y_comp >= 0 and y_comp + tile_h <= h_comp and x_comp >= 0 and x_comp + tile_w <= w_comp:
        sample_count = 0.0
        for i, j in ti.ndrange((tile_h + stride - 1) // stride, (tile_w + stride - 1) // stride):
            diff = ref[y_ref + i * stride, x_ref + j * stride] - comp[y_comp + i * stride, x_comp + j * stride]
            sum_sq_diff += diff * diff
            sample_count += 1.0
        
        cost = sum_sq_diff / sample_count
        
    return ti.max(0.0, cost)

@ti.func
def compute_sad_cost_func(ref: ti.template(), comp: ti.template(), 
                          y_ref: ti.i32, x_ref: ti.i32, 
                          y_comp: ti.i32, x_comp: ti.i32,
                          tile_h: ti.i32, tile_w: ti.i32,
                          stride: ti.template()) -> ti.f32:
    """
    Device-side function version of standard SAD (Sum of Absolute Differences) for use inside other kernels.
    """
    sum_abs_diff = 0.0
    h_comp, w_comp = comp.shape[0], comp.shape[1]
    cost = 1e10
    
    if y_comp >= 0 and y_comp + tile_h <= h_comp and x_comp >= 0 and x_comp + tile_w <= w_comp:
        sample_count = 0.0
        for i, j in ti.ndrange((tile_h + stride - 1) // stride, (tile_w + stride - 1) // stride):
            diff = ref[y_ref + i * stride, x_ref + j * stride] - comp[y_comp + i * stride, x_comp + j * stride]
            sum_abs_diff += ti.abs(diff)
            sample_count += 1.0
            
        cost = sum_abs_diff / sample_count
        
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
