"""
Compile Phase Correlation TCM Ã¢â‚¬â€ Phase Normalize Kernel
=======================================================
AOT compilation script for the phase_correlation module's normalize kernel.
The FFT module already handles the core FFT/IFFT/mul kernels via compile_fft_tcm.py.
This script compiles the 2-argument phase normalize kernel specific to phase_correlation.

Note: The full phase_correlation AOT pipeline is orchestrated in taichi_aot/__init__.py
using fft module graphs. This script compiles the standalone normalize kernel for
custom usage or testing.

Usage:
  python compile_phase_corr_tcm.py           # Compile all 3 backends
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
pc_mod = importlib.import_module("taichi_vision.taichi_algorithm.alignment.phase_correlation")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_phase_normalize(arch, save_path):
    """Compile the 2-argument phase normalize kernel: R = R / |R|."""
    print(f"\n>>> Compiling PHASE_NORMALIZE for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # R is complex (vec2): [real, imag]
    R = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "R", ti.math.vec2, ndim=2)
    # mag is scalar magnitude
    mag = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "mag", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(pc_mod._phase_normalize_kernel, R, mag)
    module.add_graph("phase_normalize_f32", g.compile())

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
        save_path = os.path.join(ASSETS_DIR, f"phase_corr_{suffix}.tcm")
        try:
            compile_phase_normalize(arch, save_path)
            results.append(f"[PASS] phase_corr_{suffix}")
        except Exception as e:
            print(f"[FAIL] phase_corr_{suffix}: {e}")
            results.append(f"[FAIL] phase_corr_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" PHASE CORRELATION COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
