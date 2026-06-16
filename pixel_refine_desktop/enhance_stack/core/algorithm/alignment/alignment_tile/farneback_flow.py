import taichi as ti
import os
import shutil
import zipfile

# ==============================================================================
# 1. MATH & UTILITIES (@ti.func)
# ==============================================================================
@ti.func
def bicubic_weight(x: ti.f32) -> ti.f32:
    abs_x = ti.abs(x)
    res = 0.0
    if abs_x <= 1.0:
        res = 1.5 * abs_x**3 - 2.5 * abs_x**2 + 1.0
    elif abs_x < 2.0:
        res = -0.5 * abs_x**3 + 2.5 * abs_x**2 - 4.0 * abs_x + 2.0
    return res

@ti.func
def sample_image(img: ti.template(), y: ti.f32, x: ti.f32) -> ti.f32:
    h, w = img.shape[0], img.shape[1]
    y_idx = ti.max(0.0, ti.min(y, float(h - 1.001)))
    x_idx = ti.max(0.0, ti.min(x, float(w - 1.001)))
    
    y0, x0 = ti.cast(ti.floor(y_idx), ti.i32), ti.cast(ti.floor(x_idx), ti.i32)
    y1, x1 = ti.min(y0 + 1, h - 1), ti.min(x0 + 1, w - 1)
    
    wy, wx = y_idx - float(y0), x_idx - float(x0)
    
    c00, c01 = img[y0, x0], img[y0, x1]
    c10, c11 = img[y1, x0], img[y1, x1]
    
    val_top = c00 * (1.0 - wx) + c01 * wx
    val_bottom = c10 * (1.0 - wx) + c11 * wx
    return val_top * (1.0 - wy) + val_bottom * wy

@ti.func
def gaussian_weight(r: ti.f32, sigma: ti.f32) -> ti.f32:
    return ti.exp(-(r * r) / (2.0 * sigma * sigma))

# ==============================================================================
# 2. FARNEBACK KERNELS (@ti.kernel)
# ==============================================================================

@ti.kernel
def warp_image_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    flow: ti.types.ndarray()
):
    h, w = dst.shape[0], dst.shape[1]
    for y, x in ti.ndrange(h, w):
        dx = flow[y, x, 0]
        dy = flow[y, x, 1]
        dst[y, x] = sample_image(src, float(y) + dy, float(x) + dx)

@ti.kernel
def compute_polynomial_expansion_kernel(
    img: ti.types.ndarray(),
    poly: ti.types.ndarray()
):
    h, w = img.shape[0], img.shape[1]
    for y, x in ti.ndrange(h, w):
        y_m = ti.max(y - 1, 0)
        y_p = ti.min(y + 1, h - 1)
        x_m = ti.max(x - 1, 0)
        x_p = ti.min(x + 1, w - 1)
        
        tl = img[y_m, x_m]; tm = img[y_m, x]; tr = img[y_m, x_p]
        ml = img[y,   x_m]; mm = img[y,   x]; mr = img[y,   x_p]
        bl = img[y_p, x_m]; bm = img[y_p, x]; br = img[y_p, x_p]
        
        dx = (tr + 2.0*mr + br) - (tl + 2.0*ml + bl)
        dy = (bl + 2.0*bm + br) - (tl + 2.0*tm + tr)
        
        dx *= 0.125
        dy *= 0.125
        
        dxx = mr - 2.0*mm + ml
        dyy = bm - 2.0*mm + tm
        dxy = (br - bl - tr + tl) * 0.25
        
        poly[y, x, 0] = dxx
        poly[y, x, 1] = dyy
        poly[y, x, 2] = dxy
        poly[y, x, 3] = dx
        poly[y, x, 4] = dy

@ti.kernel
def compute_tensors_kernel(
    poly_ref: ti.types.ndarray(),
    poly_comp: ti.types.ndarray(),
    tensors: ti.types.ndarray()
):
    h, w = poly_ref.shape[0], poly_ref.shape[1]
    for y, x in ti.ndrange(h, w):
        A_xx = (poly_ref[y, x, 0] + poly_comp[y, x, 0]) * 0.5
        A_yy = (poly_ref[y, x, 1] + poly_comp[y, x, 1]) * 0.5
        A_xy = (poly_ref[y, x, 2] + poly_comp[y, x, 2]) * 0.5
        
        db_x = -(poly_comp[y, x, 3] - poly_ref[y, x, 3]) * 0.5
        db_y = -(poly_comp[y, x, 4] - poly_ref[y, x, 4]) * 0.5
        
        G11 = A_xx * A_xx + A_xy * A_xy
        G12 = A_xx * A_xy + A_xy * A_yy
        G22 = A_xy * A_xy + A_yy * A_yy
        
        h1 = A_xx * db_x + A_xy * db_y
        h2 = A_xy * db_x + A_yy * db_y
        
        tensors[y, x, 0] = G11
        tensors[y, x, 1] = G12
        tensors[y, x, 2] = G22
        tensors[y, x, 3] = h1
        tensors[y, x, 4] = h2

@ti.kernel
def gaussian_filter_tensors_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    win_size: ti.i32,
    sigma: ti.f32
):
    h, w = src.shape[0], src.shape[1]
    radius = win_size // 2
    for y, x in ti.ndrange(h, w):
        sum_G11, sum_G12, sum_G22, sum_h1, sum_h2 = 0.0, 0.0, 0.0, 0.0, 0.0
        weight_sum = 0.0
        
        for dy, dx in ti.ndrange((-radius, radius + 1), (-radius, radius + 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                r_sq = float(dx * dx + dy * dy)
                w_val = gaussian_weight(ti.sqrt(r_sq), sigma)
                
                sum_G11 += src[ny, nx, 0] * w_val
                sum_G12 += src[ny, nx, 1] * w_val
                sum_G22 += src[ny, nx, 2] * w_val
                sum_h1  += src[ny, nx, 3] * w_val
                sum_h2  += src[ny, nx, 4] * w_val
                weight_sum += w_val
                
        dst[y, x, 0] = sum_G11 / weight_sum
        dst[y, x, 1] = sum_G12 / weight_sum
        dst[y, x, 2] = sum_G22 / weight_sum
        dst[y, x, 3] = sum_h1 / weight_sum
        dst[y, x, 4] = sum_h2 / weight_sum

@ti.kernel
def update_flow_kernel(
    tensors: ti.types.ndarray(),
    flow: ti.types.ndarray()
):
    h, w = tensors.shape[0], tensors.shape[1]
    for y, x in ti.ndrange(h, w):
        G11 = tensors[y, x, 0]
        G12 = tensors[y, x, 1]
        G22 = tensors[y, x, 2]
        h1  = tensors[y, x, 3]
        h2  = tensors[y, x, 4]
        
        det = G11 * G22 - G12 * G12
        
        dx, dy = 0.0, 0.0
        if det > 1e-6:
            dx = (G22 * h1 - G12 * h2) / det
            dy = (G11 * h2 - G12 * h1) / det
            
        flow[y, x, 0] += dx
        flow[y, x, 1] += dy

@ti.kernel
def upsample_flow_kernel(
    src: ti.types.ndarray(), 
    dst: ti.types.ndarray(), 
    scale: ti.f32
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
                    yy = ti.max(0, ti.min(y_int + m, h_src - 1))
                    xx = ti.max(0, ti.min(x_int + n, w_src - 1))
                    w_m = bicubic_weight(float(m) - y_fract)
                    w_n = bicubic_weight(float(n) - x_fract)
                    val += src[yy, xx, k] * w_m * w_n
            dst[i, j, k] = val * scale

# ==============================================================================
# 3. AOT GRAPH COMPILATION ENTRYPOINT
# ==============================================================================
def compile_farneback_flow():
    ti.init(arch=ti.vulkan)
    module = ti.aot.Module(ti.vulkan)
    
    sym_ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", dtype=ti.f32, ndim=2)
    sym_comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", dtype=ti.f32, ndim=2)
    sym_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", dtype=ti.f32, ndim=3)
    
    sym_warped_comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "warped_comp", dtype=ti.f32, ndim=2)
    sym_poly_ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "poly_ref", dtype=ti.f32, ndim=3)
    sym_poly_comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "poly_comp", dtype=ti.f32, ndim=3)
    sym_tensors = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tensors", dtype=ti.f32, ndim=3)
    sym_smooth_tensors = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "smooth_tensors", dtype=ti.f32, ndim=3)
    
    sym_win_size = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "win_size", dtype=ti.i32)
    sym_sigma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma", dtype=ti.f32)

    g_builder = ti.graph.GraphBuilder()
    
    g_builder.dispatch(warp_image_kernel, sym_comp, sym_warped_comp, sym_flow)
    g_builder.dispatch(compute_polynomial_expansion_kernel, sym_ref, sym_poly_ref)
    g_builder.dispatch(compute_polynomial_expansion_kernel, sym_warped_comp, sym_poly_comp)
    g_builder.dispatch(compute_tensors_kernel, sym_poly_ref, sym_poly_comp, sym_tensors)
    g_builder.dispatch(gaussian_filter_tensors_kernel, sym_tensors, sym_smooth_tensors, sym_win_size, sym_sigma)
    g_builder.dispatch(update_flow_kernel, sym_smooth_tensors, sym_flow)

    module.add_graph("farneback_iteration", g_builder.compile())
    
    sym_flow_coarse = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_coarse", dtype=ti.f32, ndim=3)
    sym_flow_fine = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_fine", dtype=ti.f32, ndim=3)
    sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.f32)
    
    upsample_builder = ti.graph.GraphBuilder()
    upsample_builder.dispatch(upsample_flow_kernel, sym_flow_coarse, sym_flow_fine, sym_scale)
    module.add_graph("upsample_flow", upsample_builder.compile())

    tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_aot_farneback"))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    module.save(tmp_dir)
    
    out_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../../ui/data/aot_assets")
    )
    tcm_path = os.path.join(out_dir, "farneback_flow_vulkan.tcm")
    
    with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as tcm_zip:
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                tcm_zip.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), tmp_dir),
                )
    shutil.rmtree(tmp_dir)
    print(f"Farneback Optical Flow template compiled and packaged to: {tcm_path}")

if __name__ == "__main__":
    compile_farneback_flow()
