import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import kernels from the NEW kernel source file
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp_kernels import (
    _warp_guided_i32_rgb_aot,
    _warp_naked_i32_rgb_aot
)

def compile_warp_aot():
    ui_data_dir = os.path.abspath(os.path.join(file_dir, "../../../../../ui/data/aot_assets"))
    os.makedirs(ui_data_dir, exist_ok=True)

    arch = ti.vulkan
    print(f"\n>>> Compiling WARP AOT for: VULKAN")
    
    ti.init(arch=arch, offline_cache=False)
    mod = ti.aot.Module(arch)

    # 1. Warp Guided i32 3ch
    g_guided = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
    flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.i32), ndim=2)
    ref_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.types.vector(3, ti.i32), ndim=2)
    
    g_guided.dispatch(_warp_guided_i32_rgb_aot, src_3d, flow, dst_3d, ref_3d)
    mod.add_graph("warp_guided_i32_3ch", g_guided.compile())

    # 2. Warp Naked i32 3ch
    g_naked = ti.graph.GraphBuilder()
    g_naked.dispatch(_warp_naked_i32_rgb_aot, src_3d, flow, dst_3d)
    mod.add_graph("warp_naked_i32_3ch", g_naked.compile())

    # Simpan sebagai FOLDER (Lebih stabil untuk C-API Vulkan)
    output_path = os.path.join(ui_data_dir, "warp_vulkan")
    if os.path.exists(output_path):
        import shutil
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)
    
    mod.save(output_path)
    print(f"Successfully saved AOT Module to: {output_path}")
    ti.reset()

if __name__ == "__main__":
    compile_warp_aot()
