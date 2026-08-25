"""
Compile Nearest Interpolation TCM Ã¢â‚¬â€ Nearest Neighbor Resize
============================================================
AOT compilation script for the nearest-neighbor interpolation kernel.

Usage:
  python compile_nearest_tcm.py           # Compile all 3 backends
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
nearest_mod = importlib.import_module("taichi_vision.taichi_algorithm.interpolation.nearest_interpolation")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_nearest_resize(arch, save_path):
    """Compile nearest-neighbor resize kernel."""
    print(f"\n>>> Compiling NEAREST_RESIZE for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
    w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
    h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
    w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)

    g = ti.graph.GraphBuilder()
    g.dispatch(nearest_mod._nearest_resize_kernel, src, dst, h_src, w_src, h_dst, w_dst)
    module.add_graph("nearest_resize_f32", g.compile())

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
        save_path = os.path.join(ASSETS_DIR, f"nearest_{suffix}.tcm")
        try:
            compile_nearest_resize(arch, save_path)
            results.append(f"[PASS] nearest_{suffix}")
        except Exception as e:
            print(f"[FAIL] nearest_{suffix}: {e}")
            results.append(f"[FAIL] nearest_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" NEAREST INTERPOLATION COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
