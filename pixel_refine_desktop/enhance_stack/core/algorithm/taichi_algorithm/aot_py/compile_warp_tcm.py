import taichi as ti
import os
import numpy as np
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import warp

def compile_warp_tcm():
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()
    arch = ti.vulkan
    if arch_str == "cuda": arch = ti.cuda
    elif arch_str == "cpu": arch = ti.x64
    
    ti.init(arch=arch)
    
    save_dir = os.path.join(os.path.dirname(__file__), "../aot_tcm")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "warp.tcm")

    module = ti.aot.Module(arch)

    # Define Vectorized Flow Arg (2D NDArray of Vec2)
    flow_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.types.vector(2, ti.f32), ndim=2)

    # 1. Warp Guided i32 (1-Channel) - Bilinear 1ch
    g_wg_1 = ti.graph.GraphBuilder()
    src_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    ref_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.i32, ndim=2)
    g_wg_1.dispatch(warp._warp_guided_i32_extreme_aot, src_1, flow_vec, dst_1, ref_1)
    module.add_graph("warp_guided_i32_1ch", g_wg_1.compile())
    
    # 2. Warp Guided i32 (3-Channel) - ULTRA (Vectorized)
    g_wg_3 = ti.graph.GraphBuilder()
    src_3_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
    dst_3_vec = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.i32), ndim=2)
    ref_1ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.i32, ndim=2) # Only need Green channel
    g_wg_3.dispatch(warp._warp_guided_i32_rgb_ultra_aot, src_3_vec, flow_vec, dst_3_vec, ref_1ch)
    module.add_graph("warp_guided_i32_3ch", g_wg_3.compile())
    
    # 3. Warp Naked i32 (1-Channel)
    g_wn_1 = ti.graph.GraphBuilder()
    g_wn_1.dispatch(warp._warp_naked_i32_extreme_aot, src_1, flow_vec, dst_1)
    module.add_graph("warp_naked_i32_1ch", g_wn_1.compile())
    
    # 4. Warp Naked i32 (3-Channel) - ULTRA (Vectorized)
    g_wn_3 = ti.graph.GraphBuilder()
    g_wn_3.dispatch(warp._warp_naked_i32_rgb_ultra_aot, src_3_vec, flow_vec, dst_3_vec)
    module.add_graph("warp_naked_i32_3ch", g_wn_3.compile())
    
    # 5. Extract Green Channel (Utility)
    g_ex = ti.graph.GraphBuilder()
    dst_1ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    g_ex.dispatch(warp._extract_green_i32_aot, src_3_vec, dst_1ch)
    module.add_graph("extract_green_i32", g_ex.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")

if __name__ == "__main__":
    compile_warp_tcm()
