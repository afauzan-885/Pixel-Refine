import taichi as ti
import os
import sys
import importlib

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
box_filter_mod = importlib.import_module("pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.box_filter")

def compile_box_filter_aot(arch=ti.vulkan, save_path="box_filter_vulkan.tcm"):
    print(f"\n>>> Compiling BOX FILTER (Fused 3x3 Restoration) AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)

    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    tmp_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tmp", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    # 1. Fused 3x3 Pass (Legendary 38 FPS Path)
    g_3x3_3ch = ti.graph.GraphBuilder()
    g_3x3_3ch.dispatch(box_filter_mod._box_filter_3x3_3ch_f32_unrolled_kernel, src_3d, dst_3d, h_arg, w_arg)
    module.add_graph("box_filter_fused_3x3_3ch_f32", g_3x3_3ch.compile())

    # 2. Generic Separable Pass (Optimized O(R) Coalesced)
    g_sep_3ch = ti.graph.GraphBuilder()
    g_sep_3ch.dispatch(box_filter_mod._box_blur_h_generic_3ch_kernel, src_3d, tmp_3d, h_arg, w_arg, radius_arg)
    g_sep_3ch.dispatch(box_filter_mod._box_blur_v_generic_3ch_kernel, tmp_3d, dst_3d, h_arg, w_arg, radius_arg)
    module.add_graph("box_filter_separable_generic_3ch_f32", g_sep_3ch.compile())
    
    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"box_filter_{suffix}.tcm"))
        try:
            compile_box_filter_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
