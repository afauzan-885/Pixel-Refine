import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gradients
gradients = sys.modules["pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.gradients"]

def compile_gradients_aot(arch=ti.vulkan, save_path="gradients_vulkan.tcm"):
    print(f"\n>>> Compiling GRADIENTS AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)

    # 1. Sobel (Grayscale)
    g_sobel = ti.graph.GraphBuilder()
    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_dx = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_dx", ti.f32, ndim=2)
    dst_dy = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_dy", ti.f32, ndim=2)
    g_sobel.dispatch(gradients._sobel_kernel, src, dst_dx, dst_dy, h_arg, w_arg)
    module.add_graph("sobel_f32", g_sobel.compile())

    # 1b. Sobel (RGB / Vector3)
    g_sobel_v3 = ti.graph.GraphBuilder()
    src_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_dx_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_dx", ti.f32, ndim=2)
    dst_dy_v3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_dy", ti.f32, ndim=2)
    g_sobel_v3.dispatch(gradients._sobel_kernel_vec3, src_v3, dst_dx_v3, dst_dy_v3, h_arg, w_arg)
    module.add_graph("sobel_vec3_f32", g_sobel_v3.compile())

    # 2. Laplacian
    g_laplacian = ti.graph.GraphBuilder()
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_laplacian.dispatch(gradients._laplacian_kernel, src, dst, h_arg, w_arg)
    module.add_graph("laplacian_f32", g_laplacian.compile())

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"gradients_{suffix}.tcm"))
        try:
            compile_gradients_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
