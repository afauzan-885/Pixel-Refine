"""
Compile MTB TCM Ã¢â‚¬â€ Median Threshold Bitmap Alignment
=====================================================
AOT compilation script for the MTB alignment kernels:
  - _compute_histogram: GPU histogram for median computation
  - _compute_bitmaps: Bitmap + Exclusion map generation
  - _compute_mtb_error_to_buf: AOT-compatible error computation (buffer output)

Usage:
  python compile_mtb_tcm.py           # Compile all 3 backends
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
mtb_mod = importlib.import_module("taichi_vision.taichi_algorithm.alignment.mtb")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_mtb_histogram(arch, module):
    """Compile MTB histogram kernel."""
    img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "img", ti.f32, ndim=2)
    hist = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hist", ti.i32, ndim=1)

    g = ti.graph.GraphBuilder()
    g.dispatch(mtb_mod._compute_histogram, img, hist)
    module.add_graph("mtb_histogram_f32", g.compile())
    print("  Compiled: mtb_histogram_f32")


def compile_mtb_bitmaps(arch, module):
    """Compile MTB bitmap + exclusion map generation kernel."""
    img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "img", ti.f32, ndim=2)
    bitmap = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bitmap", ti.i32, ndim=2)
    exclusion = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "exclusion", ti.i32, ndim=2)
    median_val = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "median_val", ti.f32)
    tolerance = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tolerance", ti.f32)

    g = ti.graph.GraphBuilder()
    g.dispatch(mtb_mod._compute_bitmaps, img, bitmap, exclusion, median_val, tolerance)
    module.add_graph("mtb_bitmaps_f32", g.compile())
    print("  Compiled: mtb_bitmaps_f32")


def compile_mtb_error(arch, module):
    """Compile MTB error computation kernel (buffer-output version for AOT)."""
    bitmap1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bitmap1", ti.i32, ndim=2)
    excl1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "exclusion1", ti.i32, ndim=2)
    bitmap2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bitmap2", ti.i32, ndim=2)
    excl2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "exclusion2", ti.i32, ndim=2)
    error_buf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "error_buf", ti.i32, ndim=1)
    dx = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dx", ti.i32)
    dy = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dy", ti.i32)

    g = ti.graph.GraphBuilder()
    g.dispatch(mtb_mod._compute_mtb_error_to_buf, bitmap1, excl1, bitmap2, excl2, error_buf, dx, dy)
    module.add_graph("mtb_error_f32", g.compile())
    print("  Compiled: mtb_error_f32")


def compile_mtb_aot(arch, save_path):
    """Compile all MTB kernels into a single TCM module."""
    print(f"\n>>> Compiling MTB for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    compile_mtb_histogram(arch, module)
    compile_mtb_bitmaps(arch, module)
    compile_mtb_error(arch, module)

    module.archive(save_path)
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
        save_path = os.path.join(ASSETS_DIR, f"mtb_{suffix}.tcm")
        try:
            compile_mtb_aot(arch, save_path)
            results.append(f"[PASS] mtb_{suffix}")
        except Exception as e:
            print(f"[FAIL] mtb_{suffix}: {e}")
            results.append(f"[FAIL] mtb_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" MTB COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
