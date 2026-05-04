import taichi as ti
import os
import sys

# Setup path to find taichi_algorithm
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set AOT Mode for the algorithm imports
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.bilinear_interpolation as bilinear

def compile_bilinear_tcm(arch=ti.vulkan, save_path="bilinear_vulkan.tcm"):
    print(f"\n>>> Compiling Bilinear AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Bilinear Resize 2D (Grayscale)
    g_resize_2d = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
    w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
    h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
    w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)
    
    g_resize_2d.dispatch(bilinear._bilinear_resize_kernel, src_2d, dst_2d, h_src, w_src, h_dst, w_dst)
    module.add_graph("bilinear_resize_f32_2d", g_resize_2d.compile())

    # 2. Bilinear Resize 3D (Color)
    g_resize_3d = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    
    g_resize_3d.dispatch(bilinear._bilinear_resize_kernel_3d, src_3d, dst_3d, h_src, w_src, h_dst, w_dst)
    module.add_graph("bilinear_resize_f32_3d", g_resize_3d.compile())

    # Archive the module
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
        save_path = os.path.abspath(os.path.join(assets_dir, f"bilinear_{suffix}.tcm"))
        try:
            compile_bilinear_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
