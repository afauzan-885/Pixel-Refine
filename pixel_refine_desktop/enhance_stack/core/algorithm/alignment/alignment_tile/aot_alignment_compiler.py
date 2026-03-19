import taichi as ti
import os
import sys

# Add the project root to sys.path to allow relative imports
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the kernels directly to avoid shadowing
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile import (
    compute_flow,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
    _downsample_2x_kernel,
    _upsample_flow_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc import (
    _compute_global_zncc_surface,
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
    target_archs = {"cuda": ti.cuda, "vulkan": ti.vulkan, "cpu": ti.cpu}

    for arch_name, arch_ti in target_archs.items():
        print(f"\n{'='*50}")
        print(f"Compiling AOT for Architecture: {arch_name.upper()}")
        print(f"{'='*50}")

        try:
            # ==========================================
            # MODULE 1: PREPROCESS
            # ==========================================
            ti.init(arch=arch_ti, offline_cache=False)
            print(" - Processing [PREPROCESS] Module...")
            mod_preproc = ti.aot.Module(arch_ti)
            mod_preproc.add_kernel(_fused_full_pipeline_i32_2d_aot)
            mod_preproc.add_kernel(_fused_full_pipeline_i32_3d_aot)
            mod_preproc.archive(
                os.path.join(ui_data_dir, f"preprocess_{arch_name}.tcm")
            )
            ti.reset()

            # ==========================================
            # MODULE 2: COMPUTE FLOW
            # ==========================================
            ti.init(arch=arch_ti, offline_cache=False)
            print(" - Processing [COMPUTE_FLOW] Module...")
            mod_flow = ti.aot.Module(arch_ti)
            mod_flow.add_kernel(compute_flow._block_search_kernel)
            mod_flow.add_kernel(compute_flow._initialize_coarsest_flow_kernel)
            mod_flow.add_kernel(compute_flow._search_coarse_level_kernel)
            mod_flow.add_kernel(compute_flow._search_fine_level_kernel)
            mod_flow.add_kernel(compute_flow._parabolic_subpixel_refinement_kernel)
            mod_flow.add_kernel(_downsample_2x_kernel)
            mod_flow.add_kernel(_upsample_flow_kernel)
            mod_flow.add_kernel(_compute_global_zncc_surface)
            mod_flow.archive(os.path.join(ui_data_dir, f"compute_flow_{arch_name}.tcm"))
            ti.reset()

            # ==========================================
            # MODULE 3: WARP
            # ==========================================
            ti.init(arch=arch_ti, offline_cache=False)
            print(" - Processing [WARP] Module...")
            mod_warp = ti.aot.Module(arch_ti)
            mod_warp.add_kernel(_warp_guided_i32_aot)
            mod_warp.add_kernel(_warp_guided_i32_rgb_aot)
            mod_warp.archive(os.path.join(ui_data_dir, f"warp_{arch_name}.tcm"))
            ti.reset()

            print(
                f"[SUCCESS] {arch_name.upper()} AOT Compilation Finished (3 Modules)."
            )

        except Exception as e:
            print(f"[ERROR] Failed to compile for {arch_name.upper()}: {e}")
            ti.reset()

    print("\n" + "=" * 50)
    print("Multi-Architecture Modular AOT Export Completed!")
    print(f"Output directory: {ui_data_dir}")
    print("=" * 50)


if __name__ == "__main__":
    compile_aot()
