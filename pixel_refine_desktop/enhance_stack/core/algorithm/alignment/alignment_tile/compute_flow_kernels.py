import taichi as ti
import taichi.math as tm

@ti.func
def _compute_l1_cost(
    ref: ti.types.ndarray(),
    comp: ti.types.ndarray(),
    y_ref: int,
    x_ref: int,
    y_comp: int,
    x_comp: int,
    tile_h: int,
    tile_w: int,
) -> float:
    """Compute Sum of Absolute Differences (SAD / L1) cost."""
    h, w = ref.shape[0], ref.shape[1]
    total_abs_diff = 0.0
    for r, c in ti.ndrange(tile_h, tile_w):
        ry, rx = tm.clamp(y_ref + r, 0, h - 1), tm.clamp(x_ref + c, 0, w - 1)
        cy, cx = tm.clamp(y_comp + r, 0, h - 1), tm.clamp(x_comp + c, 0, w - 1)
        total_abs_diff += ti.abs(ref[ry, rx] - comp[cy, cx])
    return total_abs_diff / float(tile_h * tile_w)

@ti.kernel
def _downsample_2x_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray()):
    for i, j in dst:
        dst[i, j] = (src[2 * i, 2 * j] + src[2 * i + 1, 2 * j] +
                     src[2 * i, 2 * j + 1] + src[2 * i + 1, 2 * j + 1]) * 0.25

@ti.kernel
def _compute_global_zncc_surface(
    ref: ti.types.ndarray(),
    comp: ti.types.ndarray(),
    zncc_surf: ti.types.ndarray(),
    zncc_shift: int
):
    h, w = ref.shape[0], ref.shape[1]
    mean_r = 0.0
    sq_sum_r = 0.0
    for i, j in ti.ndrange(h, w):
        val = ref[i, j]
        mean_r += val
        sq_sum_r += val * val
    
    n = float(h * w)
    mean_r /= n
    var_r = ti.max(0.0, sq_sum_r - n * mean_r * mean_r)
    std_r = ti.sqrt(var_r)

    for dy, dx in ti.ndrange((-zncc_shift, zncc_shift + 1), (-zncc_shift, zncc_shift + 1)):
        mean_c = 0.0
        sq_sum_c = 0.0
        cross_sum = 0.0
        for i, j in ti.ndrange(h, w):
            y_c, x_c = tm.clamp(i + dy, 0, h - 1), tm.clamp(j + dx, 0, w - 1)
            val_c = comp[y_c, x_c]
            mean_c += val_c
            sq_sum_c += val_c * val_c
            cross_sum += ref[i, j] * val_c
            
        mean_c /= n
        var_c = ti.max(0.0, sq_sum_c - n * mean_c * mean_c)
        std_c = ti.sqrt(var_c)
        score = 0.0
        if std_r > 1e-5 and std_c > 1e-5:
            score = (cross_sum - n * mean_r * mean_c) / (std_r * std_c)
        zncc_surf[dy + zncc_shift, dx + zncc_shift] = -score

@ti.kernel
def _reduce_min_2d_kernel(surf: ti.types.ndarray(), res: ti.types.ndarray()):
    best_val = 1e10
    best_y, best_x = 0, 0
    h, w = surf.shape[0], surf.shape[1]
    shift_y, shift_x = h // 2, w // 2
    for i, j in surf:
        val = surf[i, j]
        if val < best_val:
            best_val = val
            best_y, best_x = i - shift_y, j - shift_x
    res[0] = float(best_y)
    res[1] = float(best_x)

@ti.kernel
def _block_search_init_kernel(
    ref: ti.types.ndarray(),
    comp: ti.types.ndarray(),
    global_shift: ti.types.ndarray(),
    flow_out: ti.types.ndarray(),
    tile_h: int,
    tile_w: int,
    search_radius: int
):
    """Initial layer block search using Global ZNCC shift with boundary hardening."""
    h, w = ref.shape[0], ref.shape[1]
    # Safety: Ensure tile size isn't larger than image
    th, tw = ti.min(tile_h, h), ti.min(tile_w, w)
    step_y, step_x = th // 2, tw // 2
    if step_y < 1: step_y = 1
    if step_x < 1: step_x = 1

    init_dy, init_dx = int(global_shift[0]), int(global_shift[1])

    for ty, tx in ti.ndrange((h - th + 1) // step_y, (w - tw + 1) // step_x):
        y, x = ty * step_y, tx * step_x
        best_cost = 1e10
        best_dx, best_dy = float(init_dx), float(init_dy)

        for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
            test_dy, test_dx = init_dy + dy, init_dx + dx
            # Boundary check for comp access
            if 0 <= y + test_dy < h - th + 1 and 0 <= x + test_dx < w - tw + 1:
                cost = _compute_l1_cost(ref, comp, y, x, y + test_dy, x + test_dx, th, tw)
                if cost < best_cost:
                    best_cost = cost
                    best_dx, best_dy = float(test_dx), float(test_dy)

        # Robust splatting
        for r, c in ti.ndrange(th, tw):
            if y + r < h and x + c < w:
                flow_out[y + r, x + c, 0] = best_dx
                flow_out[y + r, x + c, 1] = best_dy

@ti.kernel
def _block_search_refine_kernel(
    ref: ti.types.ndarray(),
    comp: ti.types.ndarray(),
    prev_flow: ti.types.ndarray(),
    flow_out: ti.types.ndarray(),
    tile_h: int,
    tile_w: int,
    search_radius: int,
    scale: float
):
    """Refinement layers with boundary hardening."""
    h, w = ref.shape[0], ref.shape[1]
    ph, pw = prev_flow.shape[0], prev_flow.shape[1]
    
    th, tw = ti.min(tile_h, h), ti.min(tile_w, w)
    step_y, step_x = th // 2, tw // 2
    if step_y < 1: step_y = 1
    if step_x < 1: step_x = 1

    for ty, tx in ti.ndrange((h - th + 1) // step_y, (w - tw + 1) // step_x):
        y, x = ty * step_y, tx * step_x
        
        # Safe initial flow sampling
        py, px = tm.clamp(int(y * scale), 0, ph - 1), tm.clamp(int(x * scale), 0, pw - 1)
        init_dx = prev_flow[py, px, 0] / scale
        init_dy = prev_flow[py, px, 1] / scale

        best_cost = 1e10
        best_dx, best_dy = init_dx, init_dy
        idx_dx, idx_dy = int(ti.round(init_dx)), int(ti.round(init_dy))

        for dy, dx in ti.ndrange((-search_radius, search_radius + 1), (-search_radius, search_radius + 1)):
            test_dy, test_dx = idx_dy + dy, idx_dx + dx
            if 0 <= y + test_dy < h - th + 1 and 0 <= x + test_dx < w - tw + 1:
                cost = _compute_l1_cost(ref, comp, y, x, y + test_dy, x + test_dx, th, tw)
                if cost < best_cost:
                    best_cost = cost
                    best_dx, best_dy = float(test_dx), float(test_dy)

        for r, c in ti.ndrange(th, tw):
            if y + r < h and x + c < w:
                flow_out[y + r, x + c, 0] = best_dx
                flow_out[y + r, x + c, 1] = best_dy
