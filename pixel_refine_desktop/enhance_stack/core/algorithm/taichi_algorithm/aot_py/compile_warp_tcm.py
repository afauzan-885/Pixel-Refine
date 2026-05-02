import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp
warp = sys.modules["pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp"]

def compile_warp_aot(arch=ti.vulkan, save_path="warp_vulkan.tcm"):
    print(f"\n>>> Compiling WARP AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    flow_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)

    # 1. Warp Guided i32 (1-Channel)
    g_wg_1 = ti.graph.GraphBuilder()
    src_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dst_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    ref_1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.i32, ndim=2)
    g_wg_1.dispatch(warp._warp_guided_i32_aot, src_1, flow_arg, dst_1, ref_1)
    module.add_graph("warp_guided_i32_1ch", g_wg_1.compile())

    # 2. Warp Guided i32 (3-Channel)
    g_wg_3 = ti.graph.GraphBuilder()
    src_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3)
    dst_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    ref_3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref", ti.i32, ndim=3)
    g_wg_3.dispatch(warp._warp_guided_i32_rgb_aot, src_3, flow_arg, dst_3, ref_3)
    module.add_graph("warp_guided_i32_3ch", g_wg_3.compile())

    # 3. Warp Naked i32 (1-Channel)
    g_wn_1 = ti.graph.GraphBuilder()
    g_wn_1.dispatch(warp._warp_naked_i32_aot, src_1, flow_arg, dst_1)
    module.add_graph("warp_naked_i32_1ch", g_wn_1.compile())

    # 4. Warp Naked i32 (3-Channel)
    g_wn_3 = ti.graph.GraphBuilder()
    g_wn_3.dispatch(warp._warp_naked_i32_rgb_aot, src_3, flow_arg, dst_3)
    module.add_graph("warp_naked_i32_3ch", g_wn_3.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu")
    ]
    
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"warp_{suffix}.tcm"))
        try:
            compile_warp_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
