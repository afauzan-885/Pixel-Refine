"""
Compile Seamless Clone TCM Ã¢â‚¬â€ Poisson Image Editing Kernels
============================================================
AOT compilation script for the seamless cloning kernels:
  - _compute_divergence_normal: Source gradient computation
  - _compute_divergence_mixed: Mixed gradient computation
  - _compute_laplacian: Divergence of gradient field
  - _jacobi_step: Jacobi relaxation iteration
  - _composite_kernel: Write solved channel back
  - _copy_seamless: Copy 3-channel image
  - _to_grayscale: Convert to grayscale for MONOCHROME_TRANSFER
  - _init_f_channel: Initialize f from destination channel

Usage:
  python compile_seamless_clone_tcm.py           # Compile all 3 backends
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
sc_mod = importlib.import_module("taichi_vision.taichi_algorithm.image_processing.seamless_clone")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_seamless_clone_aot(arch, save_path):
    """Compile all seamless clone kernels into a single TCM module."""
    print(f"\n>>> Compiling SEAMLESS_CLONE for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # Common args
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    ch_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ch", ti.i32)

    f32_2d = ti.graph.ArgKind.NDARRAY
    f32_3d = ti.graph.ArgKind.NDARRAY

    # --- 1. _compute_divergence_normal ---
    src_3d = ti.graph.Arg(f32_3d, "src", ti.f32, ndim=3)
    div_x = ti.graph.Arg(f32_2d, "div_x", ti.f32, ndim=2)
    div_y = ti.graph.Arg(f32_2d, "div_y", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._compute_divergence_normal, src_3d, div_x, div_y, h_arg, w_arg, ch_arg)
    module.add_graph("seamless_divergence_normal_f32", g.compile())
    print("  Compiled: seamless_divergence_normal_f32")

    # --- 2. _compute_divergence_mixed ---
    dst_3d = ti.graph.Arg(f32_3d, "dst", ti.f32, ndim=3)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._compute_divergence_mixed, src_3d, dst_3d, div_x, div_y, h_arg, w_arg, ch_arg)
    module.add_graph("seamless_divergence_mixed_f32", g.compile())
    print("  Compiled: seamless_divergence_mixed_f32")

    # --- 3. _compute_laplacian ---
    lap = ti.graph.Arg(f32_2d, "lap", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._compute_laplacian, div_x, div_y, lap, h_arg, w_arg)
    module.add_graph("seamless_laplacian_f32", g.compile())
    print("  Compiled: seamless_laplacian_f32")

    # --- 4. _jacobi_step ---
    f_in = ti.graph.Arg(f32_2d, "f_in", ti.f32, ndim=2)
    f_out = ti.graph.Arg(f32_2d, "f_out", ti.f32, ndim=2)
    mask = ti.graph.Arg(f32_2d, "mask", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._jacobi_step, f_in, f_out, lap, mask, h_arg, w_arg)
    module.add_graph("seamless_jacobi_step_f32", g.compile())
    print("  Compiled: seamless_jacobi_step_f32")

    # --- 5. _composite_kernel ---
    f = ti.graph.Arg(f32_2d, "f", ti.f32, ndim=2)
    dst_out = ti.graph.Arg(f32_3d, "dst_out", ti.f32, ndim=3)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._composite_kernel, f, dst_out, mask, h_arg, w_arg, ch_arg)
    module.add_graph("seamless_composite_f32", g.compile())
    print("  Compiled: seamless_composite_f32")

    # --- 6. _copy_seamless ---
    s_3d = ti.graph.Arg(f32_3d, "s", ti.f32, ndim=3)
    d_3d = ti.graph.Arg(f32_3d, "d", ti.f32, ndim=3)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._copy_seamless, s_3d, d_3d, h_arg, w_arg)
    module.add_graph("seamless_copy_f32", g.compile())
    print("  Compiled: seamless_copy_f32")

    # --- 7. _to_grayscale ---
    s_3d2 = ti.graph.Arg(f32_3d, "s", ti.f32, ndim=3)
    g_2d = ti.graph.Arg(f32_2d, "g", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._to_grayscale, s_3d2, g_2d, h_arg, w_arg)
    module.add_graph("seamless_to_grayscale_f32", g.compile())
    print("  Compiled: seamless_to_grayscale_f32")

    # --- 8. _init_f_channel ---
    dst_arr = ti.graph.Arg(f32_3d, "dst_arr", ti.f32, ndim=3)
    f_arr = ti.graph.Arg(f32_2d, "f_arr", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(sc_mod._init_f_channel, dst_arr, f_arr, h_arg, w_arg, ch_arg)
    module.add_graph("seamless_init_f_channel_f32", g.compile())
    print("  Compiled: seamless_init_f_channel_f32")

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
        save_path = os.path.join(ASSETS_DIR, f"seamless_clone_{suffix}.tcm")
        try:
            compile_seamless_clone_aot(arch, save_path)
            results.append(f"[PASS] seamless_clone_{suffix}")
        except Exception as e:
            print(f"[FAIL] seamless_clone_{suffix}: {e}")
            results.append(f"[FAIL] seamless_clone_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" SEAMLESS CLONE COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
