import taichi as ti
import os
import numpy as np
import sys

# Ensure project root is in path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import warp_kernels as warp

def compile_warp_aot(arch):
    print(f"\n>>> Compiling WARP AOT (f32/i32) for: {arch}")
    ti.init(arch=arch)
    
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../aot_tcm"))
    os.makedirs(save_dir, exist_ok=True)
    suffix = "vulkan"
    if arch == ti.cuda: suffix = "cuda"
    elif arch == ti.x64: suffix = "cpu"
    save_path = os.path.join(save_dir, f"warp_{suffix}.tcm")

    module = ti.aot.Module(arch)

    # Arguments
    flow_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
    
    # --- i32 GRAPHS ---
    
    # 1. Warp Guided i32 (3-Channel)
    g_wg_i32_3 = ti.graph.GraphBuilder()
    src_i32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
    dst_i32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.i32), ndim=2)
    ref_i32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.types.vector(3, ti.i32), ndim=2)
    g_wg_i32_3.dispatch(warp._warp_guided_i32_rgb_aot, src_i32_3, flow_arg, dst_i32_3, ref_i32_3)
    module.add_graph("warp_guided_i32_3ch", g_wg_i32_3.compile())
    
    # 2. Warp Naked i32 (3-Channel)
    g_wn_i32_3 = ti.graph.GraphBuilder()
    g_wn_i32_3.dispatch(warp._warp_naked_i32_rgb_aot, src_i32_3, flow_arg, dst_i32_3)
    module.add_graph("warp_naked_i32_3ch", g_wn_i32_3.compile())

    # --- f32 GRAPHS (High Precision) ---
    
    # 3. Warp Guided f32 (3-Channel)
    g_wg_f32_3 = ti.graph.GraphBuilder()
    src_f32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_f32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    ref_f32_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.types.vector(3, ti.f32), ndim=2)
    g_wg_f32_3.dispatch(warp._warp_guided_f32_rgb_aot, src_f32_3, flow_arg, dst_f32_3, ref_f32_3)
    module.add_graph("warp_guided_f32_3ch", g_wg_f32_3.compile())
    
    # 4. Warp Naked f32 (3-Channel)
    g_wn_f32_3 = ti.graph.GraphBuilder()
    g_wn_f32_3.dispatch(warp._warp_naked_f32_rgb_aot, src_f32_3, flow_arg, dst_f32_3)
    module.add_graph("warp_naked_f32_3ch", g_wn_f32_3.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    archs = [ti.vulkan, ti.cuda, ti.x64]
    for arch in archs:
        try:
            compile_warp_aot(arch)
        except Exception as e:
            print(f"Failed to compile for {arch}: {e}")
            ti.reset()
