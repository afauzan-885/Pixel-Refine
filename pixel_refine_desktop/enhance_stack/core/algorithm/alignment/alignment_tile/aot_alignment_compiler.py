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
            # 1. Module COMPUTE_FLOW
            # ---------------------------------------------------------
            ti.init(arch=arch_ti, offline_cache=False)
            print(f" - Processing [COMPUTE_FLOW] Module...")
            mod_flow = ti.aot.Module(arch_ti)
            
            # Kernels
            mod_flow.add_kernel(compute_flow._block_search_kernel)
            mod_flow.add_kernel(compute_flow._initialize_coarsest_flow_kernel)
            mod_flow.add_kernel(compute_flow._search_coarse_level_kernel)
            mod_flow.add_kernel(compute_flow._search_fine_level_kernel)
            mod_flow.add_kernel(compute_flow._parabolic_subpixel_refinement_kernel)
            mod_flow.add_kernel(compute_flow._initialize_flow_from_results_kernel)
            mod_flow.add_kernel(_downsample_2x_kernel)
            mod_flow.add_kernel(_upsample_flow_kernel)
            mod_flow.add_kernel(_compute_global_zncc_surface)
            mod_flow.add_kernel(_reduce_min_2d_kernel)

            # Graph
            builder = ti.graph.GraphBuilder()
            ref_l = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'ref_l{i}', ti.f32, ndim=2) for i in range(3)]
            comp_l = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'comp_l{i}', ti.f32, ndim=2) for i in range(3)]
            flow_l = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'flow_l{i}', ti.f32, ndim=3) for i in range(3)]
            flow_tmp_l = [ti.graph.Arg(ti.graph.ArgKind.NDARRAY, f'flow_tmp_l{i}', ti.f32, ndim=3) for i in range(3)]
            zncc_surface = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'zncc_surface', ti.f32, ndim=2)
            zncc_results = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, 'zncc_results', ti.f32, ndim=1)
            zncc_max_shift = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'zncc_max_shift', ti.i32)
            h_l = [ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'h_l{i}', ti.i32) for i in range(3)]
            w_l = [ti.graph.Arg(ti.graph.ArgKind.SCALAR, f'w_l{i}', ti.i32) for i in range(3)]
            tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'tile_h', ti.i32)
            tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'tile_w', ti.i32)
            search_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'search_radius', ti.i32)
            scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'scale', ti.f32)
            downscale_factor = ti.graph.Arg(ti.graph.ArgKind.SCALAR, 'downscale_factor', ti.i32)

            # 1a. Coarse-to-Fine Graph (Standard Alignment)
            # builder = ti.graph.GraphBuilder()
            # for i in range(2):
            #     builder.dispatch(_downsample_2x_kernel, ref_l[i], ref_l[i+1], h_l[i], w_l[i], h_l[i+1], w_l[i+1])
            #     builder.dispatch(_downsample_2x_kernel, comp_l[i], comp_l[i+1], h_l[i], w_l[i], h_l[i+1], w_l[i+1])
            
            # builder.dispatch(_compute_global_zncc_surface, ref_l[2], comp_l[2], zncc_surface, zncc_max_shift, h_l[2], w_l[2])
            # builder.dispatch(_reduce_min_2d_kernel, zncc_surface, zncc_results, h_l[2], w_l[2])
            # builder.dispatch(compute_flow._initialize_flow_from_results_kernel, flow_l[2], zncc_results, h_l[2], w_l[2])
            # builder.dispatch(compute_flow._block_search_kernel, ref_l[2], comp_l[2], flow_tmp_l[2], h_l[2], w_l[2], tile_h, tile_w, search_radius)
            # builder.dispatch(compute_flow._parabolic_subpixel_refinement_kernel, ref_l[2], comp_l[2], flow_tmp_l[2], flow_l[2], h_l[2], w_l[2], tile_h, tile_w)
            # builder.dispatch(_upsample_flow_kernel, flow_l[2], flow_tmp_l[1], h_l[2], w_l[2], h_l[1], w_l[1], scale)
            
            # builder.dispatch(compute_flow._search_coarse_level_kernel, ref_l[1], comp_l[1], flow_tmp_l[1], flow_l[2], flow_l[1], h_l[1], w_l[1], tile_h, tile_w, h_l[2], w_l[2], downscale_factor, search_radius)
            # builder.dispatch(compute_flow._parabolic_subpixel_refinement_kernel, ref_l[1], comp_l[1], flow_l[1], flow_tmp_l[1], h_l[1], w_l[1], tile_h, tile_w)
            # builder.dispatch(_upsample_flow_kernel, flow_l[1], flow_tmp_l[0], h_l[1], w_l[1], h_l[0], w_l[0], scale)
            # builder.dispatch(compute_flow._search_fine_level_kernel, ref_l[0], comp_l[0], flow_l[0], flow_l[1], flow_l[0], h_l[0], w_l[0], tile_h, tile_w, h_l[1], w_l[1], downscale_factor)
            
            # mod_flow.add_graph("compute_flow_3layer", builder.compile())
            print("Kernels added, skipping graph.")
            mod_flow.save(ui_data_dir, "compute_flow_dbg")
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
            print(f"[ERROR] Logic failed for {arch_name}: {e}")
            traceback.print_exc()
            ti.reset()
            continue

if __name__ == "__main__":
    compile_aot()
