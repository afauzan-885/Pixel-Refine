import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import importlib
ransac_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ransac")

def compile_ransac_aot(arch, save_path):
    print(f"\n>>> Compiling RANSAC AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)

    # 1. Compute Mean Flow
    g_mean = ti.graph.GraphBuilder()
    flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.types.vector(2, ti.f32), ndim=2)
    mean_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mean_out", ti.f32, ndim=1)
    g_mean.dispatch(ransac_mod._compute_mean_flow_kernel, flow, mean_out, h_arg, w_arg)
    module.add_graph("ransac_mean_flow_f32", g_mean.compile())

    # 2. Count Inliers
    g_count = ti.graph.GraphBuilder()
    mx = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "model_x", ti.f32)
    my = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "model_y", ti.f32)
    thr = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)
    mask = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_mask", ti.i32, ndim=2)
    g_count.dispatch(ransac_mod._count_inliers_kernel, flow, mx, my, thr, mask, h_arg, w_arg)
    module.add_graph("ransac_count_inliers_f32", g_count.compile())

    # 3. Apply Result
    g_apply = ti.graph.GraphBuilder()
    output = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.types.vector(2, ti.f32), ndim=2)
    g_apply.dispatch(ransac_mod._apply_ransac_result_kernel, flow, mask, mx, my, output, h_arg, w_arg)
    module.add_graph("ransac_apply_f32", g_apply.compile())

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"ransac_{suffix}.tcm"))
        try:
            compile_ransac_aot(arch, save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
