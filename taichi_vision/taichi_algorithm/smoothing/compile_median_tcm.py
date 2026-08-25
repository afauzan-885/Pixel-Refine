import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)


import importlib
med_mod = importlib.import_module("taichi_vision.taichi_algorithm.smoothing.median_filter")

def compile_median_aot(arch, save_path):
    print(f"\n>>> Compiling MEDIAN AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    actual_arch = ti.lang.impl.current_cfg().arch
    if actual_arch != arch:
        ti.reset()
        raise RuntimeError(f"requested {arch}, but Taichi initialized {actual_arch}")

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

    # Intel OpenGL's compiler is sensitive to the vector/confidence variants;
    # keep the exact grayscale 3x3 kernel available even when those optional
    # graphs cannot be lowered. The normal Vulkan/CPU build remains unchanged.
    if arch == ti.opengl and os.environ.get("PIXEL_REFINE_AOT_OPENGL_MINIMAL", "0") == "1":
        module.archive(save_path)
        print(f"Successfully compiled minimal OpenGL median artifact: {save_path}")
        ti.reset()
        return

    if arch == ti.opengl and os.environ.get("PIXEL_REFINE_AOT_OPENGL_RGB_ONLY", "0") == "1":
        g_med_rgb_3x3 = ti.graph.GraphBuilder()
        src_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
        dst_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
        g_med_rgb_3x3.dispatch(med_mod._median_filter_rgb_3x3_kernel, src_rgb, dst_rgb, h_arg, w_arg)
        module.add_graph("median_3ch_3x3_f32", g_med_rgb_3x3.compile())
        module.archive(save_path)
        print(f"Successfully compiled RGB-only OpenGL median candidate: {save_path}")
        ti.reset()
        return

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
    script_dir = file_dir
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
