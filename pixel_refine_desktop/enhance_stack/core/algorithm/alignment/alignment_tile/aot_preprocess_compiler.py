import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess_kernels import (
    _fused_full_pipeline_kernel_aot,
    _fused_full_pipeline_gray_kernel_aot
)

def compile_preprocess_aot():
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    os.makedirs(ui_data_dir, exist_ok=True)

    arch = ti.vulkan
    print(f"\n>>> Compiling PREPROCESS STABLE AOT for: VULKAN")
    
    ti.init(arch=arch, offline_cache=False)
    mod = ti.aot.Module(arch)

    # 1. RGB Graph (i32)
    g_rgb = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    s_norm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_norm", ti.f32)
    apply_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_gamma", ti.i32)
    s_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_gamma", ti.f32)
    g_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
    slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
    cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)
    u_sharp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_sharpen", ti.i32)
    
    g_rgb.dispatch(_fused_full_pipeline_kernel_aot, src_3d, dst_2d, s_norm, apply_gamma, s_gamma, g_pow, slope, cutoff, u_sharp)
    mod.add_graph("preprocess_rgb", g_rgb.compile())

    # 2. Gray Graph (i32)
    g_gray = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    g_gray.dispatch(_fused_full_pipeline_gray_kernel_aot, src_2d, dst_2d, s_norm, apply_gamma, s_gamma, g_pow, slope, cutoff, u_sharp)
    mod.add_graph("preprocess_gray", g_gray.compile())

    # Simpan sebagai FOLDER
    output_path = os.path.join(ui_data_dir, "preprocess_vulkan")
    if os.path.exists(output_path):
        import shutil
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
    
    mod.save(output_path)
    print(f"Successfully saved Stable AOT Module to: {output_path}")
    ti.reset()

if __name__ == "__main__":
    compile_preprocess_aot()
