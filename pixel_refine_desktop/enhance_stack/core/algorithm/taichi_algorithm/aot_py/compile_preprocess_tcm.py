import taichi as ti
import os
import sys
import importlib
import numpy as np

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
kernels_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess_kernels")

def compile_preprocess_aot(arch=ti.vulkan, save_path="preprocess_vulkan.tcm"):
    print(f"\n>>> Compiling PREPROCESS AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # 1. RGB Graph (Int32 source)
    builder_rgb = ti.graph.GraphBuilder()
    src_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
    dst_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    # Scalars
    scale_norm = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_norm", ti.f32)
    apply_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "apply_gamma", ti.i32)
    scale_gamma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_gamma", ti.f32)
    gamma_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
    slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
    cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)
    use_sharpen = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "use_sharpen", ti.i32)

    builder_rgb.dispatch(kernels_mod._fused_full_pipeline_kernel_aot, 
                         src_rgb, dst_rgb, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)
    module.add_graph("preprocess_rgb", builder_rgb.compile())

    # 2. Gray Graph (Int32 source)
    builder_gray = ti.graph.GraphBuilder()
    src_gray = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst_gray = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    builder_gray.dispatch(kernels_mod._fused_full_pipeline_gray_kernel_aot, 
                          src_gray, dst_gray, scale_norm, apply_gamma, scale_gamma, gamma_pow, slope, cutoff, use_sharpen)
    module.add_graph("preprocess_gray", builder_gray.compile())

    # 3. U8/U16 variants if needed (Optional, but good for direct load)
    # For now, preprocess.py casts everything to i32, so we only need i32 graphs.

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # The project expects it in ui/data/aot_assets or aot_tcm
    # preprocess.py looks in ui/data/aot_assets
    assets_dir = os.path.abspath(os.path.join(script_dir, "../../../../ui/data/aot_assets"))
    os.makedirs(assets_dir, exist_ok=True)
    
    # Also compile to aot_tcm for comprehensive testing
    tcm_dir = os.path.abspath(os.path.join(script_dir, "../aot_tcm"))
    os.makedirs(tcm_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.join(assets_dir, f"preprocess_{suffix}.tcm")
        try:
            compile_preprocess_aot(arch=arch, save_path=save_path)
            # Copy to aot_tcm too
            import shutil
            shutil.copy2(save_path, os.path.join(tcm_dir, f"preprocess_{suffix}.tcm"))
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
