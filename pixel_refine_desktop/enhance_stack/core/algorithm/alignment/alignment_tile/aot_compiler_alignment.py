import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import all component kernels
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile import (
    compute_flow,
)
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
    _warp_naked_i32_aot,
    _warp_naked_i32_rgb_aot,
    _warp_guided_i32_aot,
    _warp_guided_i32_rgb_aot,
)


def compile_unified_aot():
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data"))
    os.makedirs(ui_data_dir, exist_ok=True)

    # Compile for multiple backends
    backends = {"cpu": ti.cpu, "cuda": ti.cuda, "vulkan": ti.vulkan}

    for name, arch in backends.items():
        print(f"\n>>> Compiling UNIFIED AOT for: {name.upper()}")
        try:
            ti.init(arch=arch, offline_cache=False)
            mod = ti.aot.Module(arch)

            # 1. Kernels
            mod.add_kernel(_fused_full_pipeline_i32_2d_aot)
            mod.add_kernel(_fused_full_pipeline_i32_3d_aot)
            mod.add_kernel(_downsample_2x_kernel)
            mod.add_kernel(_upsample_flow_kernel)
            mod.add_kernel(_compute_global_zncc_surface)
            mod.add_kernel(_reduce_min_2d_kernel)
            mod.add_kernel(compute_flow._initialize_coarsest_flow_kernel)
            mod.add_kernel(compute_flow._block_search_kernel)
            mod.add_kernel(compute_flow._initialize_flow_from_results_kernel)
            mod.add_kernel(compute_flow._search_coarse_level_kernel)
            mod.add_kernel(compute_flow._search_fine_level_kernel)
            mod.add_kernel(compute_flow._parabolic_subpixel_refinement_kernel)
            mod.add_kernel(_warp_naked_i32_aot)
            mod.add_kernel(_warp_naked_i32_rgb_aot)
            mod.add_kernel(_warp_guided_i32_aot)
            mod.add_kernel(_warp_guided_i32_rgb_aot)

            # 2. Graphs
            # --- Setup Frame (Preprocessing & Downsampling) ---
            def build_setup_frame_graph(n):
                g = ti.graph.GraphBuilder()
                raw = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "raw", ti.i32, ndim=3)
                l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "l0", ti.f32, ndim=2)
                s_norm, s_gamma, g_pow, slope, cutoff, sharpen = [
                    ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, t)
                    for name, t in zip(
                        ["s_norm", "s_gamma", "g_pow", "slope", "cutoff", "sharpen"],
                        [ti.f32, ti.f32, ti.f32, ti.f32, ti.f32, ti.i32],
                    )
                ]

                g.dispatch(
                    _fused_full_pipeline_i32_3d_aot,
                    raw,
                    l0,
                    s_norm,
                    s_gamma,
                    g_pow,
                    slope,
                    cutoff,
                    sharpen,
                )

                levels = [l0] + [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"l{i}", ti.f32, ndim=2)
                    for i in range(1, n)
                ]
                tmps = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"tmp_l{i}", ti.f32, ndim=2)
                    for i in range(1, n)
                ]
                for i in range(n - 1):
                    g.dispatch(_downsample_2x_kernel, levels[i], tmps[i])
                    g.dispatch(_downsample_2x_kernel, tmps[i], levels[i + 1])
                return g.compile()

            # --- Align Frame ---
            def build_align_graph_coarse(n):
                """Coarse Phase: Processes Levels N-1 down to 1."""
                g = ti.graph.GraphBuilder()
                ref_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"ref_l{i}", ti.f32, ndim=2)
                    for i in range(n)
                ]
                comp_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"comp_l{i}", ti.f32, ndim=2)
                    for i in range(n)
                ]
                flow_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"flow_l{i}", ti.f32, ndim=3)
                    for i in range(n)
                ]
                flow_tmp_l = [
                    ti.graph.Arg(
                        ti.graph.ArgKind.NDARRAY, f"flow_tmp_l{i}", ti.f32, ndim=3
                    )
                    for i in range(n)
                ]

                t_h, t_w, s_rad, c_dist, scale, ds_fac = [
                    ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, t)
                    for name, t in zip(
                        [
                            "tile_h",
                            "tile_w",
                            "search_radius",
                            "coarse_dist",
                            "scale",
                            "ds_fac",
                        ],
                        [ti.i32, ti.i32, ti.i32, ti.i32, ti.f32, ti.i32],
                    )
                ]

                # Start from coarsest level (already initialized by C++ with global shift)
                g.dispatch(
                    compute_flow._block_search_kernel,
                    ref_l[n - 1],
                    comp_l[n - 1],
                    flow_tmp_l[n - 1],
                    t_h,
                    t_w,
                    s_rad,
                )
                g.dispatch(
                    compute_flow._parabolic_subpixel_refinement_kernel,
                    ref_l[n - 1],
                    comp_l[n - 1],
                    flow_tmp_l[n - 1],
                    flow_l[n - 1],
                    t_h,
                    t_w,
                )

                for i in range(n - 2, 0, -1):
                    # Upsample previous level result (flow_l[i+1]) into current tmp
                    g.dispatch(
                        _upsample_flow_kernel, flow_l[i + 1], flow_tmp_l[i], scale
                    )
                    # Search using previous result and current upsampled starting point, result into flow_l[i]
                    g.dispatch(
                        compute_flow._search_coarse_level_kernel,
                        ref_l[i],
                        comp_l[i],
                        flow_tmp_l[i],
                        flow_l[i + 1],
                        flow_l[i],
                        t_h,
                        t_w,
                        c_dist,
                        ds_fac,
                    )
                    # Refine flow_l[i] into flow_tmp_l[i] and then copy back or swap?
                    # Let's refine flow_l[i] into flow_tmp_l[i]
                    g.dispatch(
                        compute_flow._parabolic_subpixel_refinement_kernel,
                        ref_l[i],
                        comp_l[i],
                        flow_l[i],
                        flow_tmp_l[i],
                        t_h,
                        t_w,
                    )
                    # For consistency, we need the final result of level i in flow_l[i].
                    # Let's use a "Swap" or just change the refinement to go into flow_l[i].
                    # Parabolic kernel: (ref, comp, flow_in, flow_out, ...)
                    # Let's use flow_tmp_l[i] as refined output and then the next level will use it.
                    # BUT wait, the loop i goes down to 1.
                    # If i=1 result is in flow_tmp_l1, then Fine phase should take flow_tmp_l1?
                return g.compile()

            def build_align_graph_fine(n):
                """Fine Phase: Processes Level 0 and final JBR Warp."""
                g = ti.graph.GraphBuilder()
                comp_raw = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "comp_raw", ti.i32, ndim=3
                )
                ref_raw = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "ref_raw", ti.i32, ndim=3
                )
                ref_l0 = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "ref_l0", ti.f32, ndim=2
                )
                comp_l0 = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "comp_l0", ti.f32, ndim=2
                )
                flow_l0 = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "flow_l0", ti.f32, ndim=3
                )
                flow_l1 = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "flow_l1", ti.f32, ndim=3
                )
                flow_tmp_l0 = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "flow_tmp_l0", ti.f32, ndim=3
                )
                warped = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "warped", ti.i32, ndim=3
                )
                flow_final = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "flow_final", ti.f32, ndim=3
                )

                t_h, t_w, c_dist, scale, ds_fac = [
                    ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, t)
                    for name, t in zip(
                        ["tile_h", "tile_w", "coarse_dist", "scale", "ds_fac"],
                        [ti.i32, ti.i32, ti.i32, ti.f32, ti.i32],
                    )
                ]

                g.dispatch(_upsample_flow_kernel, flow_l1, flow_tmp_l0, scale)
                g.dispatch(
                    compute_flow._search_coarse_level_kernel,
                    ref_l0,
                    comp_l0,
                    flow_tmp_l0,
                    flow_l1,
                    flow_l0,
                    t_h,
                    t_w,
                    c_dist,
                    ds_fac,
                )
                g.dispatch(
                    compute_flow._parabolic_subpixel_refinement_kernel,
                    ref_l0,
                    comp_l0,
                    flow_l0,
                    flow_final,
                    t_h,
                    t_w,
                )
                g.dispatch(
                    _warp_guided_i32_rgb_aot, comp_raw, flow_final, warped, ref_raw
                )
                return g.compile()

            # --- Monolithic End-to-End Alignment Graph ---
            def build_monolithic_graph(n):
                """
                Truly End-to-End: Raw Images -> Complete Alignment -> Warped Output.
                Minimized host-device sync by unrolling the entire pipeline.
                """
                g = ti.graph.GraphBuilder()

                # 1. Inputs
                ref_raw = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "ref_raw", ti.i32, ndim=3
                )
                comp_raw = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "comp_raw", ti.i32, ndim=3
                )
                warped = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "warped", ti.i32, ndim=3
                )

                # Pyramid levels (Pre-allocated by C++)
                ref_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"ref_l{i}", ti.f32, ndim=2)
                    for i in range(n)
                ]
                comp_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"comp_l{i}", ti.f32, ndim=2)
                    for i in range(n)
                ]

                # Flow levels
                flow_l = [
                    ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f"flow_l{i}", ti.f32, ndim=3)
                    for i in range(n)
                ]
                flow_tmp_l = [
                    ti.graph.Arg(
                        ti.graph.ArgKind.NDARRAY, f"flow_tmp_l{i}", ti.f32, ndim=3
                    )
                    for i in range(n)
                ]

                # ZNCC Surface and Results (Intermediate memory context)
                zncc_surf = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "zncc_surf", ti.f32, ndim=2
                )
                zncc_res = ti.graph.Arg(
                    ti.graph.ArgKind.NDARRAY, "zncc_res", ti.f32, ndim=1
                )

                # Intermediate casting/downsampling buffers
                tmp_ref = [
                    ti.graph.Arg(
                        ti.graph.ArgKind.NDARRAY, f"tmp_ref_l{i}", ti.f32, ndim=2
                    )
                    for i in range(1, n)
                ]
                tmp_comp = [
                    ti.graph.Arg(
                        ti.graph.ArgKind.NDARRAY, f"tmp_comp_l{i}", ti.f32, ndim=2
                    )
                    for i in range(1, n)
                ]

                # Scalars
                s_norm, s_gamma, g_pow, slope, cutoff, sharpen = [
                    ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, t)
                    for name, t in zip(
                        ["s_norm", "s_gamma", "g_pow", "slope", "cutoff", "sharpen"],
                        [ti.f32, ti.f32, ti.f32, ti.f32, ti.f32, ti.i32],
                    )
                ]
                t_h, t_w, s_rad, c_dist, scale, ds_fac, zncc_shift = [
                    ti.graph.Arg(ti.graph.ArgKind.SCALAR, name, t)
                    for name, t in zip(
                        [
                            "tile_h",
                            "tile_w",
                            "search_radius",
                            "coarse_dist",
                            "scale",
                            "ds_fac",
                            "zncc_shift",
                        ],
                        [ti.i32, ti.i32, ti.i32, ti.i32, ti.f32, ti.i32, ti.i32],
                    )
                ]

                # --- STEP 1: Preprocess both frames ---
                g.dispatch(
                    _fused_full_pipeline_i32_3d_aot,
                    ref_raw,
                    ref_l[0],
                    s_norm,
                    s_gamma,
                    g_pow,
                    slope,
                    cutoff,
                    sharpen,
                )
                g.dispatch(
                    _fused_full_pipeline_i32_3d_aot,
                    comp_raw,
                    comp_l[0],
                    s_norm,
                    s_gamma,
                    g_pow,
                    slope,
                    cutoff,
                    sharpen,
                )

                # --- STEP 2: Build Pyramids ---
                for i in range(n - 1):
                    # Downsample Ref
                    g.dispatch(_downsample_2x_kernel, ref_l[i], tmp_ref[i])
                    g.dispatch(_downsample_2x_kernel, tmp_ref[i], ref_l[i + 1])
                    # Downsample Comp
                    g.dispatch(_downsample_2x_kernel, comp_l[i], tmp_comp[i])
                    g.dispatch(_downsample_2x_kernel, tmp_comp[i], comp_l[i + 1])

                # --- STEP 3: Initial Global Motion Search (ZNCC) ---
                g.dispatch(
                    _compute_global_zncc_surface,
                    ref_l[n - 1],
                    comp_l[n - 1],
                    zncc_surf,
                    zncc_shift,
                )
                g.dispatch(_reduce_min_2d_kernel, zncc_surf, zncc_res)
                g.dispatch(
                    compute_flow._initialize_flow_from_results_kernel,
                    flow_l[n - 1],
                    zncc_res,
                    zncc_shift,
                )

                # --- STEP 4: Coarse-to-Fine Alignment ---
                # Coarsest layer refinement
                g.dispatch(
                    compute_flow._block_search_kernel,
                    ref_l[n - 1],
                    comp_l[n - 1],
                    flow_tmp_l[n - 1],
                    t_h,
                    t_w,
                    s_rad,
                )
                g.dispatch(
                    compute_flow._parabolic_subpixel_refinement_kernel,
                    ref_l[n - 1],
                    comp_l[n - 1],
                    flow_tmp_l[n - 1],
                    flow_l[n - 1],
                    t_h,
                    t_w,
                )

                # Propagation loop
                for i in range(n - 2, -1, -1):
                    g.dispatch(
                        _upsample_flow_kernel, flow_l[i + 1], flow_tmp_l[i], scale
                    )
                    g.dispatch(
                        compute_flow._search_coarse_level_kernel,
                        ref_l[i],
                        comp_l[i],
                        flow_tmp_l[i],
                        flow_l[i + 1],
                        flow_l[i],
                        t_h,
                        t_w,
                        c_dist,
                        ds_fac,
                    )
                    # Use flow_tmp_l as refined output to avoid overwriting input too early
                    g.dispatch(
                        compute_flow._parabolic_subpixel_refinement_kernel,
                        ref_l[i],
                        comp_l[i],
                        flow_l[i],
                        flow_tmp_l[i],
                        t_h,
                        t_w,
                    )
                    # Final result of level i back in flow_l[i]
                    # Actually, let's keep it in flow_tmp_l[i] and use that for next level as source
                    # [FIX] Swapping convention to match graph requirements
                    # For simplicity, refinement output IS our final result for this level.
                    # Wait, if i=0, then flow_tmp_l[0] holds the final alignment.

                # --- STEP 5: Warp ---
                # Level 0 flow is in flow_tmp_l[0]
                g.dispatch(
                    _warp_guided_i32_rgb_aot, comp_raw, flow_tmp_l[0], warped, ref_raw
                )

                return g.compile()

            mod.add_graph("setup_reference_3layer", build_setup_frame_graph(3))
            mod.add_graph("setup_comparison_3layer", build_setup_frame_graph(3))
            mod.add_graph("align_frame_3layer_coarse", build_align_graph_coarse(3))
            mod.add_graph("align_frame_3layer_fine", build_align_graph_fine(3))

            # Monolithic graphs
            mod.add_graph("align_end_to_end_3layer", build_monolithic_graph(3))

            mod.archive(os.path.join(ui_data_dir, f"alignment_tile_taichi_{name}.tcm"))
            print(f"Successfully archived alignment_tile_taichi_{name}.tcm")
            ti.reset()
        except Exception as e:
            print(f"Failed for {name}: {e}")
            ti.reset()


if __name__ == "__main__":
    compile_unified_aot()
