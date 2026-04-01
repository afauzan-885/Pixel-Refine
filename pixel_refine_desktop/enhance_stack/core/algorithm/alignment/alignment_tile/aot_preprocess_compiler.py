import taichi as ti
import os
import sys
import numpy as np

# Menambahkan root project ke sys.path agar bisa mengimport modul internal
# Struktur: pixel_refine_desktop/enhance_stack/core/algorithm/alignment/alignment_tile/aot_preprocess_compiler.py
# Berarti naik 6 tingkat ke folder induk Pixel Refine
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../../../../../../"))
sys.path.append(project_root)

try:
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess import (
        _fused_full_pipeline_i32_3d_aot,
        _fused_full_pipeline_i32_2d_aot
    )
    print("[AOT Compiler] Kernels imported successfully from preprocess.py")
except ImportError as e:
    print(f"[AOT Compiler] Error importing kernels: {e}")
    sys.exit(1)

def compile_preprocess_aot(target_arch=ti.vulkan, output_dir="aot_assets/preprocess"):
    """
    Mengompilasi pipeline preprocessing (fused) ke dalam modul AOT.
    Mendukung input RGB (3D) dan Grayscale (2D).
    """
    ti.init(arch=target_arch)
    print(f"[AOT Compiler] Initialized Taichi for {target_arch}")

    # 1. Bangun Grafik untuk Preprocessing RGB (3D)
    builder_3d = ti.graph.GraphBuilder()
    
    # Definisikan Argumen Grafik
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3) # Input: RGB i32
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2) # Output: Gray f32
    
    # Hyperparameters as Scalar Arguments
    src_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_h", ti.i32)
    src_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_w", ti.i32)
    dst_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_h", ti.i32)
    dst_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_w", ti.i32)
    
    scale_norm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_norm", ti.f32)
    apply_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_gamma", ti.i32)
    scale_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_gamma", ti.f32)
    gamma_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
    slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
    cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)
    use_sharpen = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_sharpen", ti.i32)

    # Catat eksekusi kernel ke dalam grafik
    builder_3d.dispatch(
        _fused_full_pipeline_i32_3d_aot, 
        src_3d, dst_3d, 
        src_h, src_w, dst_h, dst_w,
        scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen
    )
    
    graph_rgb = builder_3d.compile()
    print("[AOT Compiler] RGB Preprocess Graph compiled.")

    # 2. Bangun Grafik untuk Preprocessing Grayscale (2D)
    builder_2d = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    builder_2d.dispatch(
        _fused_full_pipeline_i32_2d_aot, 
        src_2d, dst_2d, 
        src_h, src_w, dst_h, dst_w,
        scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen
    )
    
    graph_gray = builder_2d.compile()
    print("[AOT Compiler] Grayscale Preprocess Graph compiled.")

    # 3. Ekspor ke Modul AOT
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        
    mod = ti.aot.Module(target_arch)
    mod.add_graph("preprocess_rgb", graph_rgb)
    mod.add_graph("preprocess_gray", graph_gray)
    
    mod.save(output_dir)
    print(f"[AOT Compiler] AOT Module saved to: {output_dir}")

if __name__ == "__main__":
    # Tentukan output dir: pixel_refine_desktop/ui/data/aot_assets/preprocess
    # script_dir: .../alignment_tile
    # target: script_dir/../../../../../ui/data/aot_assets/preprocess
    default_out = os.path.join(script_dir, "../../../../../", "ui", "data", "aot_assets", "preprocess")
    default_out = os.path.abspath(default_out)
    
    compile_preprocess_aot(target_arch=ti.cuda, output_dir=default_out)
