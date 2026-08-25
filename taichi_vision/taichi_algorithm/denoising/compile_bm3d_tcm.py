"""
Compile BM3D TCM Ã¢â‚¬â€ Hybrid Fast Collaborative Denoising (HFCD)
=============================================================
AOT compilation script for BM3D/HFCD denoising kernels.
All kernels use runtime scalar args (not ti.template), so 1 graph per kernel.

Graphs compiled:
  - bm3d_block_match_f32  : Block matching + Top-K + extraction
  - bm3d_dct_filter_f32   : 2D DCT hard thresholding per group
  - bm3d_aggregate_f32    : Weighted overlap-add aggregation
  - bm3d_normalize_f32    : Normalize output by weight sum
  - bm3d_zero_f32         : Zero-fill a 2D buffer
  - bm3d_shift_f32        : Circular shift
  - bm3d_accumulate_f32   : Accumulate src into dst
  - bm3d_scale_f32        : Scale buffer by constant

Usage:
  python compile_bm3d_tcm.py           # Compile all 3 backends
  set PIXEL_REFINE_AOT_ARCH=vulkan && python ... # Compile vulkan only
"""
import os
os.environ["AOT_MODE"] = "0"
os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

import taichi as ti
import sys
import importlib

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import algorithm module (JIT mode)
bm3d_mod = importlib.import_module("taichi_vision.taichi_algorithm.denoising.bm3d")

ASSETS_DIR = os.path.join(file_dir, "../aot_tcm")


def compile_bm3d_aot(arch, save_path):
    """Compile all BM3D/HFCD kernels into a single TCM module."""
    print(f"\n>>> Compiling BM3D for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # ---- Common Arg declarations ----
    NDARRAY = ti.graph.ArgKind.NDARRAY
    SCALAR = ti.graph.ArgKind.SCALAR

    # ndarray args (ndim only Ã¢â‚¬â€ dtype inferred at dispatch)
    src_2d = ti.graph.Arg(NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(NDARRAY, "dst", ti.f32, ndim=2)
    data_2d = ti.graph.Arg(NDARRAY, "data", ti.f32, ndim=2)
    output_2d = ti.graph.Arg(NDARRAY, "output", ti.f32, ndim=2)
    weight_sum_2d = ti.graph.Arg(NDARRAY, "weight_sum", ti.f32, ndim=2)
    groups_4d = ti.graph.Arg(NDARRAY, "groups", ti.f32, ndim=4)
    filtered_4d = ti.graph.Arg(NDARRAY, "filtered", ti.f32, ndim=4)
    temp_4d = ti.graph.Arg(NDARRAY, "temp_buf", ti.f32, ndim=4)
    match_y_2d = ti.graph.Arg(NDARRAY, "match_y", ti.i32, ndim=2)
    match_x_2d = ti.graph.Arg(NDARRAY, "match_x", ti.i32, ndim=2)
    valid_2d = ti.graph.Arg(NDARRAY, "valid_mask", ti.i32, ndim=2)
    refs_2d = ti.graph.Arg(NDARRAY, "ref_positions", ti.i32, ndim=2)
    group_weights_1d = ti.graph.Arg(NDARRAY, "group_weights", ti.f32, ndim=1)
    T_dct_2d = ti.graph.Arg(NDARRAY, "T_dct", ti.f32, ndim=2)

    # scalar args
    num_refs_arg = ti.graph.Arg(SCALAR, "num_refs", ti.i32)
    K_arg = ti.graph.Arg(SCALAR, "K", ti.i32)
    N_arg = ti.graph.Arg(SCALAR, "N", ti.i32)
    search_r_arg = ti.graph.Arg(SCALAR, "search_r", ti.i32)
    H_arg = ti.graph.Arg(SCALAR, "H", ti.i32)
    W_arg = ti.graph.Arg(SCALAR, "W", ti.i32)
    sigma_arg = ti.graph.Arg(SCALAR, "sigma", ti.f32)
    lambda_arg = ti.graph.Arg(SCALAR, "lambda_3d", ti.f32)
    scale_arg = ti.graph.Arg(SCALAR, "scale", ti.f32)
    sy_arg = ti.graph.Arg(SCALAR, "sy", ti.i32)
    sx_arg = ti.graph.Arg(SCALAR, "sx", ti.i32)

    # ---- Graph 1: Block Matching ----
    g = ti.graph.GraphBuilder()
    if arch == ti.vulkan:
        g.dispatch(
            bm3d_mod._block_match_and_extract_portable_kernel,
            src_2d, groups_4d, match_y_2d, match_x_2d, refs_2d,
            num_refs_arg, K_arg, N_arg, search_r_arg, H_arg, W_arg
        )
    else:
        g.dispatch(
            bm3d_mod._block_match_and_extract_kernel,
            src_2d, groups_4d, match_y_2d, match_x_2d, valid_2d, refs_2d,
            num_refs_arg, K_arg, N_arg, search_r_arg, H_arg, W_arg
        )
    module.add_graph("bm3d_block_match_f32", g.compile())
    print("  Compiled: bm3d_block_match_f32")

    # ---- Graph 2: DCT Hard Thresholding ----
    g = ti.graph.GraphBuilder()
    if arch == ti.vulkan:
        g.dispatch(
            bm3d_mod._dct_forward_threshold_portable_kernel,
            groups_4d, group_weights_1d, T_dct_2d, temp_4d,
            num_refs_arg, K_arg, N_arg, sigma_arg, lambda_arg
        )
        g.dispatch(
            bm3d_mod._dct_inverse_portable_kernel,
            groups_4d, filtered_4d, T_dct_2d, temp_4d,
            num_refs_arg, K_arg, N_arg
        )
    else:
        g.dispatch(
            bm3d_mod._collaborative_dct_filter_kernel,
            groups_4d, filtered_4d, group_weights_1d, T_dct_2d, temp_4d,
            num_refs_arg, K_arg, N_arg, sigma_arg, lambda_arg
        )
    module.add_graph("bm3d_dct_filter_f32", g.compile())
    print("  Compiled: bm3d_dct_filter_f32")

    # ---- Graph 3: Aggregation ----
    g = ti.graph.GraphBuilder()
    if arch == ti.vulkan:
        g.dispatch(
            bm3d_mod._aggregate_values_portable_kernel,
            filtered_4d, group_weights_1d, match_y_2d, match_x_2d,
            output_2d, num_refs_arg, K_arg, N_arg, H_arg, W_arg
        )
        g.dispatch(
            bm3d_mod._aggregate_weights_portable_kernel,
            group_weights_1d, match_y_2d, match_x_2d, weight_sum_2d,
            num_refs_arg, K_arg, N_arg, H_arg, W_arg
        )
    else:
        g.dispatch(
            bm3d_mod._aggregate_kernel,
            filtered_4d, group_weights_1d, match_y_2d, match_x_2d, valid_2d,
            output_2d, weight_sum_2d,
            num_refs_arg, K_arg, N_arg, H_arg, W_arg
        )
    module.add_graph("bm3d_aggregate_f32", g.compile())
    print("  Compiled: bm3d_aggregate_f32")

    # ---- Graph 4: Normalize ----
    g = ti.graph.GraphBuilder()
    g.dispatch(
        bm3d_mod._normalize_kernel,
        output_2d, weight_sum_2d, src_2d, H_arg, W_arg
    )
    module.add_graph("bm3d_normalize_f32", g.compile())
    print("  Compiled: bm3d_normalize_f32")

    # ---- Graph 5: Zero ----
    g = ti.graph.GraphBuilder()
    g.dispatch(bm3d_mod._zero_kernel, dst_2d, H_arg, W_arg)
    module.add_graph("bm3d_zero_f32", g.compile())
    print("  Compiled: bm3d_zero_f32")

    # ---- Graph 6: Circular Shift ----
    g = ti.graph.GraphBuilder()
    g.dispatch(
        bm3d_mod._circular_shift_kernel,
        src_2d, dst_2d, H_arg, W_arg, sy_arg, sx_arg
    )
    module.add_graph("bm3d_shift_f32", g.compile())
    print("  Compiled: bm3d_shift_f32")

    # ---- Graph 7: Accumulate ----
    g = ti.graph.GraphBuilder()
    g.dispatch(bm3d_mod._accumulate_kernel, dst_2d, src_2d, H_arg, W_arg)
    module.add_graph("bm3d_accumulate_f32", g.compile())
    print("  Compiled: bm3d_accumulate_f32")

    # ---- Graph 8: Scale ----
    g = ti.graph.GraphBuilder()
    g.dispatch(bm3d_mod._scale_kernel, data_2d, scale_arg, H_arg, W_arg)
    module.add_graph("bm3d_scale_f32", g.compile())
    print("  Compiled: bm3d_scale_f32")

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
        save_path = os.path.join(ASSETS_DIR, f"bm3d_{suffix}.tcm")
        try:
            compile_bm3d_aot(arch, save_path)
            results.append(f"[PASS] bm3d_{suffix}")
        except Exception as e:
            print(f"[FAIL] bm3d_{suffix}: {e}")
            results.append(f"[FAIL] bm3d_{suffix}: {e}")

    print("\n" + "=" * 60)
    print(" BM3D COMPILATION SUMMARY")
    print("=" * 60)
    for r in results:
        print(r)
    print(f"\nPassed: {sum(1 for r in results if r.startswith('[PASS]'))}/{len(results)}")
