import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess import (
    preprocess_pipeline_gpu
)

def compile_preprocess_aot():
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    os.makedirs(ui_data_dir, exist_ok=True)

    arch = ti.vulkan
    print(f"\n>>> Compiling PREPROCESS AOT for: VULKAN")
    
    ti.init(arch=arch, offline_cache=False)
    mod = ti.aot.Module(arch)

    # 1. Graphs
    # Graph for 3D (RGB) preprocessing
    g_rgb = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    s_norm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_norm", ti.f32)
    apply_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_gamma", ti.i32)
    s_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_gamma", ti.f32)
    g_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
    slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
    cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)
    sharpen = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_sharpen", ti.i32)
    
    preprocess_pipeline_gpu(
        None, g=g_rgb, src_arg=src_3d, dst_arg=dst_2d,
        scale_norm_arg=s_norm, apply_gamma_arg=apply_gamma,
        scale_gamma_arg=s_gamma, gamma_pow_arg=g_pow,
        slope_arg=slope, cutoff_arg=cutoff, sharpen_arg=sharpen,
        is_rgb_aot=True
    )
    mod.add_graph("preprocess_rgb", g_rgb.compile())

    # Graph for 2D (Gray) preprocessing
    g_gray = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst_2d_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    preprocess_pipeline_gpu(
        None, g=g_gray, src_arg=src_2d, dst_arg=dst_2d_out,
        scale_norm_arg=s_norm, apply_gamma_arg=apply_gamma,
        scale_gamma_arg=s_gamma, gamma_pow_arg=g_pow,
        slope_arg=slope, cutoff_arg=cutoff, sharpen_arg=sharpen,
        is_rgb_aot=False
    )
    mod.add_graph("preprocess_gray", g_gray.compile())

    archive_path = os.path.join(ui_data_dir, "preprocess_vulkan.tcm")
    mod.archive(archive_path)
    print(f"Successfully archived {archive_path}")
    ti.reset()

if __name__ == "__main__":
    compile_preprocess_aot()
