import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import importlib
ncc_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc")

def compile_ncc_aot(arch, save_path):
    print(f"\n>>> Compiling NCC AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # Hybrid ZNCC Map (Parallel Integral + Spatial Correlation)
    g_zncc = ti.graph.GraphBuilder()
    img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "image", ti.f32, ndim=2)
    template = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "template", ti.f32, ndim=2)
    
    # Intermediate buffers (must be passed from Python)
    sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_h", ti.f32, ndim=2)
    sq_sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_h", ti.f32, ndim=2)
    sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_2d", ti.f32, ndim=2)
    sq_sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_2d", ti.f32, ndim=2)
    corr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "corr", ti.f32, ndim=2)
    
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    h_img = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_img", ti.i32)
    w_img = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_img", ti.i32)
    h_temp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_temp", ti.i32)
    w_temp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_temp", ti.i32)
    
    # Template stats (Passed as scalars from Python to avoid re-calculating per pixel)
    sum_t = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sum_t", ti.f32)
    var_t_n = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "var_t_n", ti.f32)
    n_pixels = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_pixels", ti.f32)
    stride = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride", ti.i32)
    
    # Execution Flow
    g_zncc.dispatch(ncc_mod._integral_image_row_scan_kernel, img, sum_h, sq_sum_h, h_img, w_img)
    g_zncc.dispatch(ncc_mod._integral_image_col_scan_kernel, sum_h, sq_sum_h, sum_2d, sq_sum_2d, h_img, w_img)
    g_zncc.dispatch(ncc_mod._compute_correlation_kernel, img, template, corr, h_img, w_img, h_temp, w_temp, stride)
    g_zncc.dispatch(ncc_mod._assemble_zncc_kernel, corr, sum_2d, sq_sum_2d, dst, sum_t, var_t_n, n_pixels, h_temp, w_temp, stride)
    
    module.add_graph("zncc_map_f32", g_zncc.compile())


    # 2. Global ZNCC Surface
    g_surf = ti.graph.GraphBuilder()
    ref = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.f32, ndim=2)
    comp = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp", ti.f32, ndim=2)
    cost = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cost_surface", ti.f32, ndim=2)
    max_shift = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_shift", ti.i32)
    
    g_surf.dispatch(ncc_mod._compute_global_zncc_surface, ref, comp, cost, max_shift)
    module.add_graph("zncc_surface_f32", g_surf.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu")
    ]
    
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"ncc_{suffix}.tcm"))
        try:
            compile_ncc_aot(arch, save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
