import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_vision.taichi_algorithm.alignment.ncc import NCC

def compile_ncc_aot(arch, save_path):
    print(f"\n>>> Compiling NCC AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    
    ncc_mod = NCC()
    module = ti.aot.Module(arch)

    def add_g(name, kernel, *args):
        builder = ti.graph.GraphBuilder()
        builder.dispatch(kernel, *args)
        module.add_graph(name, builder.compile())
    
    # 1. Argument Definitions
    img_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    temp_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "template", ti.f32, ndim=2)
    sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_h", ti.f32, ndim=2)
    sq_sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_h", ti.f32, ndim=2)
    sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_2d", ti.f32, ndim=2)
    sq_sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_2d", ti.f32, ndim=2)
    dst_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    row_max_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "row_max", ti.f32, ndim=2)
    peak_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "final_peak", ti.f32, ndim=2)
    
    h_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    sum_t_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sum_t", ti.f32)
    var_t_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "var_t_n", ti.f32)
    n_f_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_float", ti.f32)
    stride_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride", ti.i32)

    # 2. Graph Construction
    # Integral Images
    add_g("integral_row_scan", ncc_mod._integral_image_row_scan_kernel, 
          img_f32, sum_h, sq_sum_h, h_v, w_v)
    add_g("integral_col_scan", ncc_mod._integral_image_col_scan_kernel,
          sum_h, sq_sum_h, sum_2d, sq_sum_2d, h_v, w_v)
    
    # Spatial ZNCC
    add_g("zncc_spatial", ncc_mod._zncc_spatial_kernel,
          img_f32, temp_f32, sum_2d, sq_sum_2d, dst_f32,
          sum_t_v, var_t_v, n_f_v, stride_v)
    
    # Reduction
    add_g("reduce_row_max", ncc_mod._reduce_row_max_kernel, dst_f32, row_max_v)
    add_g("reduce_global_max", ncc_mod._reduce_global_max_kernel, row_max_v, peak_v)

    module.archive(save_path)
    print(f"Successfully compiled NCC graphs to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"ncc_{suffix}.tcm"))
        try:
            compile_ncc_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
