import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_tile.compute_flow_kernels import (
    _downsample_2x_kernel,
    _compute_global_zncc_surface,
    _reduce_min_2d_kernel,
    _block_search_init_kernel,
    _block_search_refine_kernel
)

def compile_compute_flow_aot():
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    os.makedirs(ui_data_dir, exist_ok=True)

    arch = ti.vulkan
    print(f"\n>>> Compiling COMPUTE FLOW AOT for: VULKAN")
    
    ti.init(arch=arch, offline_cache=False)
    mod = ti.aot.Module(arch)

    # Define Graph Arguments
    g = ti.graph.GraphBuilder()
    
    # NDArrays for Pyramid (Ref & Comp)
    ref_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l0", ti.f32, ndim=2)
    ref_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l1", ti.f32, ndim=2)
    ref_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_l2", ti.f32, ndim=2)
    
    comp_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l0", ti.f32, ndim=2)
    comp_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l1", ti.f32, ndim=2)
    comp_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_l2", ti.f32, ndim=2)
    
    # Flows NDArrays (L0, L1, L2)
    flow_l0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l0", ti.f32, ndim=3)
    flow_l1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l1", ti.f32, ndim=3)
    flow_l2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_l2", ti.f32, ndim=3)
    
    # ZNCC Buffers
    zncc_surf = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_surf", ti.f32, ndim=2)
    zncc_res = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zncc_res", ti.f32, ndim=1)
    
    # Scalars
    zncc_shift = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "zncc_shift", ti.i32)
    tile_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
    tile_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
    search_rad = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "search_radius", ti.i32)
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32) # Usually 0.5 or 0.25

    # 1. Build Pyramid (L0 -> L1 -> L2)
    g.dispatch(_downsample_2x_kernel, ref_l0, ref_l1)
    g.dispatch(_downsample_2x_kernel, ref_l1, ref_l2)
    g.dispatch(_downsample_2x_kernel, comp_l0, comp_l1)
    g.dispatch(_downsample_2x_kernel, comp_l1, comp_l2)
    
    # 2. Global ZNCC on L2 (Initial Shift)
    g.dispatch(_compute_global_zncc_surface, ref_l2, comp_l2, zncc_surf, zncc_shift)
    g.dispatch(_reduce_min_2d_kernel, zncc_surf, zncc_res)
    
    # 3. Block Search L2 (Init)
    g.dispatch(_block_search_init_kernel, ref_l2, comp_l2, zncc_res, flow_l2, tile_h, tile_w, search_rad)
    
    # 4. Block Search L1 (Refine from L2)
    g.dispatch(_block_search_refine_kernel, ref_l1, comp_l1, flow_l2, flow_l1, tile_h, tile_w, search_rad, scale)
    
    # 5. Block Search L0 (Refine from L1)
    g.dispatch(_block_search_refine_kernel, ref_l0, comp_l0, flow_l1, flow_l0, tile_h, tile_w, search_rad, scale)

    # Compile Graph
    mod.add_graph("align_end_to_end_3layer", g.compile())

    # Save as FOLDER
    output_path = os.path.join(ui_data_dir, "compute_flow_vulkan")
    if os.path.exists(output_path):
        import shutil
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
    
    mod.save(output_path)
    print(f"Successfully saved Compute Flow AOT Module to: {output_path}")
    ti.reset()

if __name__ == "__main__":
    compile_compute_flow_aot()
