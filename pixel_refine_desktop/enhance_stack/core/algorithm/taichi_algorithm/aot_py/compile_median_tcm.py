import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import importlib
med_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.median_filter")

def compile_median_aot(arch, save_path):
    print(f"\n>>> Compiling MEDIAN AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)

    # 1. Median Filter 3x3 (Grayscale)
    g_med_3x3 = ti.graph.GraphBuilder()
    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_med_3x3.dispatch(med_mod._median_filter_3x3_kernel, src, dst, h_arg, w_arg)
    print("Compiling median_3x3_f32...")
    module.add_graph("median_3x3_f32", g_med_3x3.compile())

    # 2. Median Filter Flow 3x3 (Vec2)
    g_med_flow_3x3 = ti.graph.GraphBuilder()
    src_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(2, ti.f32), ndim=2)
    dst_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(2, ti.f32), ndim=2)
    g_med_flow_3x3.dispatch(med_mod._median_filter_flow_3x3_kernel, src_flow, dst_flow, h_arg, w_arg)
    print("Compiling median_flow_3x3_f32...")
    module.add_graph("median_flow_3x3_f32", g_med_flow_3x3.compile())
    
    # 2b. Median Filter RGB 3x3 (3D Scalar)
    g_med_rgb_3x3 = ti.graph.GraphBuilder()
    src_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_med_rgb_3x3.dispatch(med_mod._median_filter_rgb_3x3_kernel, src_rgb, dst_rgb, h_arg, w_arg)
    print("Compiling median_3ch_3x3_f32...")
    module.add_graph("median_3ch_3x3_f32", g_med_rgb_3x3.compile())

    # 3. Confidence Weighted Median Flow
    g_conf_med = ti.graph.GraphBuilder()
    conf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "conf", ti.f32, ndim=2)
    g_conf_med.dispatch(med_mod._confidence_weighted_median_flow_kernel, src_flow, conf, dst_flow, h_arg, w_arg)
    print("Compiling conf_weighted_median_flow_f32...")
    module.add_graph("conf_weighted_median_flow_f32", g_conf_med.compile())

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"median_filter_{suffix}.tcm"))
        try:
            compile_median_aot(arch, save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
