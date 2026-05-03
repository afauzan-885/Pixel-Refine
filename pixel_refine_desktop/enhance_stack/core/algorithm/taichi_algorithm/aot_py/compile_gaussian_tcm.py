import taichi as ti
import os
import sys
import importlib

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
gaussian_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gaussian")

def compile_gaussian_aot(arch=ti.vulkan, save_path="gaussian_vulkan.tcm"):
    print(f"\n>>> Compiling GAUSSIAN BLUR (Interleaved Scalar) AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    weights_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=1)

    # 3-Channel (3D Scalar)
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    
    g_x_3ch = ti.graph.GraphBuilder()
    g_x_3ch.dispatch(gaussian_mod._gaussian_blur_x_3ch_f32_kernel, src_3d, dst_3d, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_3ch_f32", g_x_3ch.compile())

    g_y_3ch = ti.graph.GraphBuilder()
    g_y_3ch.dispatch(gaussian_mod._gaussian_blur_y_3ch_f32_kernel, src_3d, dst_3d, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_3ch_f32", g_y_3ch.compile())

    # 1-Channel (2D Scalar)
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    g_x_1ch = ti.graph.GraphBuilder()
    g_x_1ch.dispatch(gaussian_mod._gaussian_blur_x_1ch_f32_kernel, src_2d, dst_2d, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_1ch_f32", g_x_1ch.compile())

    g_y_1ch = ti.graph.GraphBuilder()
    g_y_1ch.dispatch(gaussian_mod._gaussian_blur_y_1ch_f32_kernel, src_2d, dst_2d, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_1ch_f32", g_y_1ch.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"gaussian_{suffix}.tcm"))
        try:
            compile_gaussian_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
