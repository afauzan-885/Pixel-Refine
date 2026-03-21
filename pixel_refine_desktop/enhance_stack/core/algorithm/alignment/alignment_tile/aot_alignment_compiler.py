import taichi as ti
import os
import sys

# Add the project root to sys.path to allow relative imports
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the kernels directly
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile import compute_flow
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
    _downsample_2x_kernel,
    _upsample_flow_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc import (
    _compute_global_zncc_surface,
    _reduce_min_2d_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess import (
    _fused_full_pipeline_i32_2d_aot,
    _fused_full_pipeline_i32_3d_aot,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp import (
    _warp_guided_i32_aot,
    _warp_guided_i32_rgb_aot,
)


def compile_aot():
    # Determine Output Directory
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data"))
    os.makedirs(ui_data_dir, exist_ok=True)

    # Target Architectures
    target_archs = {"cpu": ti.cpu}

    for arch_name, arch_ti in target_archs.items():
        print(f"\n{'='*50}")
        print(f"Compiling AOT for Architecture: {arch_name.upper()}")
        print(f"{'='*50}")

        try:
            # ---------------------------------------------------------
            # 1. Module COMPUTE_FLOW — 4-Layer Coarse-to-Fine Graph
            # ---------------------------------------------------------
            # Pipeline (4x downscale per level, 4 levels total):
            #   Level 0: full resolution  [H    × W   ]
            #   Level 1: 1/4  res         [H/4  × W/4 ]
            #   Level 2: 1/16 res         [H/16 × W/16]
            #   Level 3: 1/64 res         [H/64 × W/64]  ← coarsest
            #
            # Each level transition uses cascaded 2x Gaussian × 2 (→ net 4x).
            # Intermediate half-size scratch buffers (tmp_ref_l, tmp_comp_l) are
            # passed as explicit graph args so caller pre-allocates them once.
            #
            # Buffer ping-pong strategy (AOT-friendly):
            #   flow_tmp_l[i] = block/coarse search output (integer)
            #                   OR upsampled guide from coarser level
            #   flow_l[i]     = parabolic-refined output (subpixel)
            #
            # CALLER responsibility (C++ side):
            #   Pre-allocate all NDArrays once based on input image size.
            #   Call graph.run({...}) for each burst frame pair.
            #   Final output: flow_l[0]  (shape=[H, W, 2], dtype=f32)
            # ---------------------------------------------------------
            ti.init(arch=arch_ti, offline_cache=False)
            print(f" - Processing [COMPUTE_FLOW] Module (4-layer, 4x downscale graph)...")
            mod_flow = ti.aot.Module(arch_ti)

            # --- Register all kernels ---
            mod_flow.add_kernel(compute_flow._block_search_kernel)
            mod_flow.add_kernel(compute_flow._initialize_coarsest_flow_kernel)
            mod_flow.add_kernel(compute_flow._initialize_flow_from_results_kernel)
            mod_flow.add_kernel(compute_flow._search_coarse_level_kernel)
            mod_flow.add_kernel(compute_flow._search_fine_level_kernel)
            mod_flow.add_kernel(compute_flow._parabolic_subpixel_refinement_kernel)
            mod_flow.add_kernel(_downsample_2x_kernel)
            mod_flow.add_kernel(_upsample_flow_kernel)
            mod_flow.add_kernel(_compute_global_zncc_surface)
            mod_flow.add_kernel(_reduce_min_2d_kernel)

            # --- Graph Args ---
            # Pyramid image buffers (f32, 2D) — final levels
            #   ref_l[i] / comp_l[i]         = 4 pyramid levels  (caller pre-allocates)
            #   tmp_ref_l[j] / tmp_comp_l[j] = 3 half-size scratch buffers (0-based, j=0..2)
            #     j=0: H/2   × W/2   (middle step L0→L1)
            #     j=1: H/8   × W/8   (middle step L1→L2)
            #     j=2: H/32  × W/32  (middle step L2→L3)
            ref_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'ref_l{i}', ti.f32, ndim=2)
                for i in range(4)
            ]
            comp_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'comp_l{i}', ti.f32, ndim=2)
                for i in range(4)
            ]
            tmp_ref_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'tmp_ref_l{i}', ti.f32, ndim=2)
                for i in range(1, 4)   # names: tmp_ref_l1, tmp_ref_l2, tmp_ref_l3
            ]
            tmp_comp_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'tmp_comp_l{i}', ti.f32, ndim=2)
                for i in range(1, 4)
            ]
            # Flow buffers (f32, 3D: H×W×2)
            #   flow_l[i]     = refined (subpixel) flow at level i
            #   flow_tmp_l[i] = intermediate flow at level i (pre-refinement / upsample target)
            flow_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'flow_l{i}', ti.f32, ndim=3)
                for i in range(4)
            ]
            flow_tmp_l = [
                ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'flow_tmp_l{i}', ti.f32, ndim=3)
                for i in range(4)
            ]
            # ZNCC global search buffers (coarsest level only)
            zncc_surface = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY, 'zncc_surface', ti.f32, ndim=2
            )
            zncc_results = ti.graph.Arg(
                ti.graph.ArgKind.NDARRAY, 'zncc_results', ti.f32, ndim=1
            )  # layout: [best_cost, best_y_raw, best_x_raw]

            # Scalar args — final pyramid level dimensions
            h_l = [ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'h_l{i}', ti.i32) for i in range(4)]
            w_l = [ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'w_l{i}', ti.i32) for i in range(4)]
            # Scalar args — half-step intermediate dimensions
            #   h_half[j] = h_l[j] / 2,  w_half[j] = w_l[j] / 2   (j = 0..2)
            h_half = [
                ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'h_half{i}', ti.i32) for i in range(1, 4)
            ]
            w_half = [
                ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'w_half{i}', ti.i32) for i in range(1, 4)
            ]
            # Tile, search, and scale scalars
            tile_h          = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'tile_h',           ti.i32)
            tile_w          = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'tile_w',           ti.i32)
            search_radius   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'search_radius',    ti.i32)
            coarse_dist     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'coarse_dist',      ti.i32)
            zncc_max_shift  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'zncc_max_shift',   ti.i32)
            zncc_surf_size  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'zncc_surf_size',   ti.i32)
            # scale = 4.0 (upsample flow 4x between levels), downscale_factor = 4
            scale           = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'scale',            ti.f32)
            downscale_factor= ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'downscale_factor', ti.i32)

            # --- Build the Computation Graph ---
            builder = ti.graph.GraphBuilder()

            # == STEP 1: Build 4x pyramid via cascaded 2× downsamples ==
            # Transition i→i+1: level_i → tmp_half → level_i+1  (net 4×)
            # Caller must provide:
            #   h_l[i] / w_l[i]     = dims of level i  (H / 4^i)
            #   h_half[j] / w_half[j] = h_l[j] / 2  (j = i, 0-based)
            for i in range(3):
                j = i   # index into tmp_ref_l / h_half (0-based)
                # First 2x: level i → half-size scratch
                builder.dispatch(
                    _downsample_2x_kernel,
                    ref_l[i], tmp_ref_l[j],
                    h_l[i], w_l[i], h_half[j], w_half[j],
                )
                builder.dispatch(
                    _downsample_2x_kernel,
                    comp_l[i], tmp_comp_l[j],
                    h_l[i], w_l[i], h_half[j], w_half[j],
                )
                # Second 2x: half-size scratch → level i+1  (net 4x)
                builder.dispatch(
                    _downsample_2x_kernel,
                    tmp_ref_l[j], ref_l[i + 1],
                    h_half[j], w_half[j], h_l[i + 1], w_l[i + 1],
                )
                builder.dispatch(
                    _downsample_2x_kernel,
                    tmp_comp_l[j], comp_l[i + 1],
                    h_half[j], w_half[j], h_l[i + 1], w_l[i + 1],
                )

            # == STEP 2: Level 3 (coarsest) — ZNCC global init + Block Search ==
            # 2a. Compute ZNCC cost surface over ±zncc_max_shift (GPU-only)
            builder.dispatch(
                _compute_global_zncc_surface,
                ref_l[3], comp_l[3], zncc_surface,
                zncc_max_shift,
                h_l[3], w_l[3], h_l[3], w_l[3],
            )
            # 2b. Reduce: find (dy, dx) of minimum cost on GPU — no CPU readback needed
            builder.dispatch(
                _reduce_min_2d_kernel,
                zncc_surface, zncc_results,
                zncc_surf_size, zncc_surf_size,
            )
            # 2c. Fill flow_l[3] with global shift as warm start
            builder.dispatch(
                compute_flow._initialize_flow_from_results_kernel,
                flow_l[3], zncc_results,
                h_l[3], w_l[3], zncc_max_shift,
            )
            # 2d. Wide-area block search → flow_tmp_l[3]
            builder.dispatch(
                compute_flow._block_search_kernel,
                ref_l[3], comp_l[3], flow_tmp_l[3],
                h_l[3], w_l[3], tile_h, tile_w, search_radius,
            )
            # 2e. Subpixel refinement → flow_l[3]  (refined flow at L3)
            builder.dispatch(
                compute_flow._parabolic_subpixel_refinement_kernel,
                ref_l[3], comp_l[3],
                flow_tmp_l[3], flow_l[3],
                h_l[3], w_l[3], tile_h, tile_w,
            )

            # == STEP 3: Level 2 — Coarse search with spatial regularisation ==
            # 3a. Upsample refined L3 flow → flow_tmp_l[2] as guide  (scale=4.0)
            builder.dispatch(
                _upsample_flow_kernel,
                flow_l[3], flow_tmp_l[2],
                h_l[3], w_l[3], h_l[2], w_l[2], scale,
            )
            # 3b. Multi-stage coarse search → flow_l[2]
            builder.dispatch(
                compute_flow._search_coarse_level_kernel,
                ref_l[2], comp_l[2],
                flow_tmp_l[2], flow_l[3], flow_l[2],
                h_l[2], w_l[2], tile_h, tile_w,
                coarse_dist, h_l[3], w_l[3], downscale_factor,
            )
            # 3c. Subpixel refinement → flow_tmp_l[2]  (refined flow at L2)
            builder.dispatch(
                compute_flow._parabolic_subpixel_refinement_kernel,
                ref_l[2], comp_l[2],
                flow_l[2], flow_tmp_l[2],
                h_l[2], w_l[2], tile_h, tile_w,
            )

            # == STEP 4: Level 1 — Coarse search ==
            # 4a. Upsample refined L2 flow → flow_tmp_l[1] as guide
            builder.dispatch(
                _upsample_flow_kernel,
                flow_tmp_l[2], flow_tmp_l[1],
                h_l[2], w_l[2], h_l[1], w_l[1], scale,
            )
            # 4b. Coarse search → flow_l[1]
            builder.dispatch(
                compute_flow._search_coarse_level_kernel,
                ref_l[1], comp_l[1],
                flow_tmp_l[1], flow_tmp_l[2], flow_l[1],
                h_l[1], w_l[1], tile_h, tile_w,
                coarse_dist, h_l[2], w_l[2], downscale_factor,
            )
            # 4c. Subpixel refinement → flow_tmp_l[1]  (refined flow at L1)
            builder.dispatch(
                compute_flow._parabolic_subpixel_refinement_kernel,
                ref_l[1], comp_l[1],
                flow_l[1], flow_tmp_l[1],
                h_l[1], w_l[1], tile_h, tile_w,
            )

            # == STEP 5: Level 0 (finest) — Fine local search, ±1 px ==
            # 5a. Upsample refined L1 flow → flow_tmp_l[0] as guide
            builder.dispatch(
                _upsample_flow_kernel,
                flow_tmp_l[1], flow_tmp_l[0],
                h_l[1], w_l[1], h_l[0], w_l[0], scale,
            )
            # 5b. Fine local search → flow_l[0]  ← FINAL OUTPUT (full-res, subpixel)
            builder.dispatch(
                compute_flow._search_fine_level_kernel,
                ref_l[0], comp_l[0],
                flow_tmp_l[0], flow_tmp_l[1], flow_l[0],
                h_l[0], w_l[0], tile_h, tile_w,
                h_l[1], w_l[1], downscale_factor,
            )

            mod_flow.add_graph("compute_flow_4layer", builder.compile())
            print(" - Graph [compute_flow_4layer] compiled successfully.")
            mod_flow.archive(os.path.join(ui_data_dir, f"compute_flow_{arch_name}.tcm"))
            ti.reset()

            # ---------------------------------------------------------
            # 2. Module PREPROCESS
            # ---------------------------------------------------------
            ti.init(arch=arch_ti, offline_cache=False)
            print(f" - Processing [PREPROCESS] Module...")
            mod_preproc = ti.aot.Module(arch_ti)
            mod_preproc.add_kernel(_fused_full_pipeline_i32_2d_aot)
            mod_preproc.add_kernel(_fused_full_pipeline_i32_3d_aot)
            mod_preproc.archive(os.path.join(ui_data_dir, f"preprocess_{arch_name}.tcm"))
            ti.reset()

            # ---------------------------------------------------------
            # 3. Module WARP
            # ---------------------------------------------------------
            ti.init(arch=arch_ti, offline_cache=False)
            print(f" - Processing [WARP] Module...")
            mod_warp = ti.aot.Module(arch_ti)
            mod_warp.add_kernel(_warp_guided_i32_aot)
            mod_warp.add_kernel(_warp_guided_i32_rgb_aot)
            mod_warp.archive(os.path.join(ui_data_dir, f"warp_{arch_name}.tcm"))
            ti.reset()

        except Exception as e:
            import traceback
            print(f"[ERROR] Compilation failed for {arch_name}: {e}")
            traceback.print_exc()
            ti.reset()
            continue


if __name__ == "__main__":
    compile_aot()
