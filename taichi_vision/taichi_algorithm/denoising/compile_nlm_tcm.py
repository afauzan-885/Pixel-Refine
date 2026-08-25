"""
Compile NLM TCM Ã¢â‚¬â€ Non-Local Means Denoising (Fixed-Parameter Variants)
========================================================================
AOT compilation script for NLM kernels with hardcoded search/patch radii.

Variants compiled:
  1ch: search_r=3 patch_r=1, search_r=5 patch_r=2, search_r=7 patch_r=3
  3ch: search_r=3 patch_r=1, search_r=5 patch_r=2, search_r=7 patch_r=3

Usage:
  python compile_nlm_tcm.py           # Compile all 3 backends
  set PIXEL_REFINE_AOT_ARCH=vulkan && python ... # Compile vulkan only
"""
import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys
import importlib

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import algorithm module (JIT mode)
nlm_mod = importlib.import_module("taichi_vision.taichi_algorithm.denoising.nlm")

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import normalize_tcm
except ImportError:  # Direct script execution.
    from aot_artifact import normalize_tcm

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


# --- Kernel registry: (graph_name, kernel_func, suffix_label) ---
NLM_KERNELS_1CH = [
    ("nlm_1ch_s3_p1_f32", nlm_mod._nlm_1ch_s3_p1),
    ("nlm_1ch_s5_p2_f32", nlm_mod._nlm_1ch_s5_p2),
    ("nlm_1ch_s7_p3_f32", nlm_mod._nlm_1ch_s7_p3),
]

NLM_KERNELS_3CH = [
    ("nlm_3ch_s3_p1_f32", nlm_mod._nlm_3ch_s3_p1),
    ("nlm_3ch_s5_p2_f32", nlm_mod._nlm_3ch_s5_p2),
    ("nlm_3ch_s7_p3_f32", nlm_mod._nlm_3ch_s7_p3),
]


def compile_nlm_aot(arch, save_path):
    """Compile all NLM fixed-parameter variants into a single TCM module."""
    print(f"\n>>> Compiling NLM for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # Common graph args for 1-channel kernels
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    h_param_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_param", ti.f32)
    refinement_strength_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "refinement_strength", ti.f32)
    shrinkage_strength_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "shrinkage_strength", ti.f32)

    # Compile 1-channel variants
    for graph_name, kernel_func in NLM_KERNELS_1CH:
        g = ti.graph.GraphBuilder()
        g.dispatch(kernel_func, src_2d, dst_2d, h_arg, w_arg, h_param_arg, refinement_strength_arg, shrinkage_strength_arg)
        module.add_graph(graph_name, g.compile())
        print(f"  Compiled: {graph_name}")

    # Common graph args for 3-channel kernels
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    yuv_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "yuv", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    # Compile 3-channel variants
    for graph_name, kernel_func in NLM_KERNELS_3CH:
        g = ti.graph.GraphBuilder()
        g.dispatch(nlm_mod._precompute_yuv, src_3d, yuv_3d, h_arg, w_arg)
        g.dispatch(kernel_func, src_3d, yuv_3d, dst_3d, h_arg, w_arg, h_param_arg, refinement_strength_arg, shrinkage_strength_arg)
        module.add_graph(graph_name, g.compile())
        print(f"  Compiled: {graph_name}")

    module.archive(save_path)
    normalize_tcm(save_path)
    print(f"  Saved: {save_path}")
    ti.reset()


if __name__ == "__main__":
    os.makedirs(ASSETS_DIR, exist_ok=True)

    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "all").lower()
    if arch_str == "vulkan":
        archs = [(ti.vulkan, "vulkan")]
    elif arch_str == "cuda":
        archs = [(ti.cuda, "cuda")]
    elif arch_str == "cpu":
        archs = [(ti.cpu, "cpu")]
    else:
        archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]

    results = []
    for arch, suffix in archs:
        save_path = os.path.join(ASSETS_DIR, f"nlm_{suffix}.tcm")
        try:
            compile_nlm_aot(arch, save_path)
            results.append(f"[PASS] nlm_{suffix}")
        except Exception as e:
            print(f"[FAIL] nlm_{suffix}: {e}")
            results.append(f"[FAIL] nlm_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" NLM COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
