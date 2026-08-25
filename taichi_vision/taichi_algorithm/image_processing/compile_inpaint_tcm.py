"""
Compile Inpaint TCM Ã¢â‚¬â€ Fast Inpainting Kernels
===============================================
AOT compilation script for the inpainting kernels:
  - _init_distance_kernel: Initialize distance/boundary maps
  - _dilate_distance_kernel: Iterative distance expansion
  - _inpaint_level_kernel: 3-channel inpainting per level
  - _inpaint_level_1ch_kernel: 1-channel inpainting per level
  - _mark_filled_kernel: Mark filled pixels per level
  - _set_filled_kernel: Set initial filled mask
  - _copy_inpaint_3ch / _copy_inpaint_1ch: Copy operations

Usage:
  python compile_inpaint_tcm.py           # Compile all 3 backends
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
inpaint_mod = importlib.import_module(
    "taichi_vision.taichi_algorithm.image_processing.inpaint"
)

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_inpaint_aot(arch, save_path):
    """Compile all inpaint kernels into a single TCM module."""
    print(f"\n>>> Compiling INPAINT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # Common args
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    f32_2d = ti.graph.ArgKind.NDARRAY

    # --- 1. _init_distance_kernel ---
    mask = ti.graph.Arg(f32_2d, "mask", ti.f32, ndim=2)
    dist = ti.graph.Arg(f32_2d, "dist", ti.f32, ndim=2)
    boundary = ti.graph.Arg(f32_2d, "boundary", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._init_distance_kernel, mask, dist, boundary, h_arg, w_arg)
    module.add_graph("inpaint_init_distance_f32", g.compile())
    print("  Compiled: inpaint_init_distance_f32")

    # --- 2. _dilate_distance_kernel ---
    dist_in = ti.graph.Arg(f32_2d, "dist_in", ti.f32, ndim=2)
    dist_out = ti.graph.Arg(f32_2d, "dist_out", ti.f32, ndim=2)
    current_level = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "current_level", ti.f32)

    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._dilate_distance_kernel, dist_in, dist_out, h_arg, w_arg, current_level)
    module.add_graph("inpaint_dilate_distance_f32", g.compile())
    print("  Compiled: inpaint_dilate_distance_f32")

    # --- 3. _inpaint_level_kernel (3-channel) ---
    src_3d = ti.graph.Arg(f32_2d, "src", ti.f32, ndim=3)
    filled = ti.graph.Arg(f32_2d, "filled", ti.f32, ndim=2)
    target_level = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "target_level", ti.f32)
    inpaint_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inpaint_radius", ti.f32)

    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._inpaint_level_kernel, src_3d, dist, filled, h_arg, w_arg, target_level, inpaint_radius)
    module.add_graph("inpaint_level_3ch_f32", g.compile())
    print("  Compiled: inpaint_level_3ch_f32")

    # --- 4. _inpaint_level_1ch_kernel ---
    src_2d = ti.graph.Arg(f32_2d, "src", ti.f32, ndim=2)

    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._inpaint_level_1ch_kernel, src_2d, dist, filled, h_arg, w_arg, target_level, inpaint_radius)
    module.add_graph("inpaint_level_1ch_f32", g.compile())
    print("  Compiled: inpaint_level_1ch_f32")

    # --- 5. _mark_filled_kernel ---
    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._mark_filled_kernel, dist, filled, h_arg, w_arg, target_level)
    module.add_graph("inpaint_mark_filled_f32", g.compile())
    print("  Compiled: inpaint_mark_filled_f32")

    # --- 6. _set_filled_kernel ---
    g = ti.graph.GraphBuilder()
    g.dispatch(inpaint_mod._set_filled_kernel, mask, filled, h_arg, w_arg)
    module.add_graph("inpaint_set_filled_f32", g.compile())
    print("  Compiled: inpaint_set_filled_f32")

    # --- 7. Copy kernels ---
    g = ti.graph.GraphBuilder()
    s_3d = ti.graph.Arg(f32_2d, "s", ti.f32, ndim=3)
    d_3d = ti.graph.Arg(f32_2d, "d", ti.f32, ndim=3)
    g.dispatch(inpaint_mod._copy_inpaint_3ch, s_3d, d_3d, h_arg, w_arg)
    module.add_graph("inpaint_copy_3ch_f32", g.compile())
    print("  Compiled: inpaint_copy_3ch_f32")

    g = ti.graph.GraphBuilder()
    s_2d = ti.graph.Arg(f32_2d, "s", ti.f32, ndim=2)
    d_2d = ti.graph.Arg(f32_2d, "d", ti.f32, ndim=2)
    g.dispatch(inpaint_mod._copy_inpaint_1ch, s_2d, d_2d, h_arg, w_arg)
    module.add_graph("inpaint_copy_1ch_f32", g.compile())
    print("  Compiled: inpaint_copy_1ch_f32")

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
        save_path = os.path.join(ASSETS_DIR, f"inpaint_{suffix}.tcm")
        try:
            compile_inpaint_aot(arch, save_path)
            results.append(f"[PASS] inpaint_{suffix}")
        except Exception as e:
            print(f"[FAIL] inpaint_{suffix}: {e}")
            results.append(f"[FAIL] inpaint_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" INPAINT COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
