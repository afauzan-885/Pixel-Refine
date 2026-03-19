import taichi as ti
import os
import sys
import numpy as np

# Add the project root to sys.path to allow relative imports
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the kernels directly to avoid shadowing
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile import compute_flow
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import _downsample_2x_kernel, _upsample_flow_kernel
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc import _compute_global_zncc_surface
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.preprocess import _fused_full_pipeline_kernel
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp import _warp_kernel_guided, _warp_kernel_guided_3ch

def compile_aot():
    # Determine Output Directory
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data"))
    os.makedirs(ui_data_dir, exist_ok=True)
    
    # Target Architectures
    target_archs = {
        "cuda": ti.cuda,
        "vulkan": ti.vulkan,
        "cpu": ti.cpu
    }

    for arch_name, arch_ti in target_archs.items():
        print(f"\n{'='*50}")
        print(f"Compiling AOT for Architecture: {arch_name.upper()}")
        print(f"{'='*50}")
        
        try:
            # Initialize Taichi for specific arch
            ti.init(arch=arch_ti, offline_cache=False) # Disable cache for AOT generation
            
            # Create AOT Module
            module = ti.aot.Module(arch_ti)
            
            # 1. Alignment Kernels (compute_flow.py)
            print(" - Adding Alignment Kernels...")
            module.add_kernel(compute_flow._block_search_kernel)
            module.add_kernel(compute_flow._initialize_coarsest_flow_kernel)
            module.add_kernel(compute_flow._search_coarse_level_kernel)
            module.add_kernel(compute_flow._search_fine_level_kernel)
            module.add_kernel(compute_flow._parabolic_subpixel_refinement_kernel)
            
            # 2. Support Kernels (Pyramid / Warp / NCC)
            print(" - Adding Support Kernels...")
            module.add_kernel(_downsample_2x_kernel)
            module.add_kernel(_upsample_flow_kernel)
            module.add_kernel(_compute_global_zncc_surface)
            module.add_kernel(_fused_full_pipeline_kernel)
            
            # Warp Kernels require specific template instantiations if they use ti.template()
            # If they don't use templates anymore, add them directly.
            # Based on common usage in Pixel Refine:
            # module.add_kernel(_warp_kernel_guided)
            
            # 3. Save TCM Archive
            tcm_filename = f"compute_flow_{arch_name}.tcm"
            tcm_path = os.path.join(ui_data_dir, tcm_filename)
            print(f" - Saving Archive: {tcm_path}")
            module.archive(tcm_path)
            
            ti.reset() # Reset Taichi for next architecture
            print(f"[SUCCESS] {arch_name.upper()} AOT Compilation Finished.")
            
        except Exception as e:
            print(f"[ERROR] Failed to compile for {arch_name.upper()}: {e}")
            ti.reset()

    print("\n" + "="*50)
    print("Multi-Architecture AOT Export Completed!")
    print(f"Output directory: {ui_data_dir}")
    print("="*50)

if __name__ == "__main__":
    compile_aot()

if __name__ == "__main__":
    compile_aot()
