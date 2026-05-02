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
    thr = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "threshold", ti.f32)

    # 1. Main Fused RANSAC Graph
    g_fused = ti.graph.GraphBuilder()
    flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.types.vector(2, ti.f32), ndim=2)
    mask = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "inlier_mask", ti.i32, ndim=2)
    model = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "model", ti.f32, ndim=1) # [x, y]
    output = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.types.vector(2, ti.f32), ndim=2)

    st_refine = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_refine", ti.i32)
    st_final = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride_final", ti.i32)

    # Step A: Initial Model (Mean of all flow - Sparse)
    g_fused.dispatch(ransac_mod._compute_mean_flow_kernel, flow, model, h_arg, w_arg, st_refine)

    # Step B: Iterative Refinement (Unrolled 5 iterations - Sparse)
    for _ in range(5):
        g_fused.dispatch(ransac_mod._count_inliers_kernel, flow, model, thr, mask, h_arg, w_arg, st_refine)
        g_fused.dispatch(ransac_mod._compute_inlier_mean_kernel, flow, mask, model, h_arg, w_arg, st_refine)

    # Step C: Final Apply (Full Resolution)
    g_fused.dispatch(ransac_mod._count_inliers_kernel, flow, model, thr, mask, h_arg, w_arg, st_final)
    g_fused.dispatch(ransac_mod._apply_ransac_result_kernel, flow, mask, model, output, h_arg, w_arg)

    module.add_graph("ransac_flow_cleanup_f32", g_fused.compile())

    module.archive(save_path)
    print(f"Successfully compiled fused graph to: {save_path}")
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
