import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

import importlib.util

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian
gaussian_module = sys.modules["pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian"]

def compile_gaussian_aot(arch=ti.vulkan, save_path="gaussian_vulkan.tcm"):
    print(f"\n>>> Compiling GAUSSIAN AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    
    # Weights array is 1D
    weights_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=1)

    # 1. Blur X 1CH
    g_x1 = ti.graph.GraphBuilder()
    src_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_x1.dispatch(gaussian_module._gaussian_blur_x_1ch, src_1, dst_1, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_1ch_f32", g_x1.compile())

    # 2. Blur Y 1CH
    g_y1 = ti.graph.GraphBuilder()
    g_y1.dispatch(gaussian_module._gaussian_blur_y_1ch, src_1, dst_1, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_1ch_f32", g_y1.compile())

    # 3. Blur X 3CH
    g_x3 = ti.graph.GraphBuilder()
    src_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_x3.dispatch(gaussian_module._gaussian_blur_x_3ch, src_3, dst_3, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_3ch_f32", g_x3.compile())

    # 4. Blur Y 3CH
    g_y3 = ti.graph.GraphBuilder()
    g_y3.dispatch(gaussian_module._gaussian_blur_y_3ch, src_3, dst_3, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_3ch_f32", g_y3.compile())

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"gaussian_{suffix}.tcm"))
        try:
            compile_gaussian_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
