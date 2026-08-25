import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys
import importlib

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

box_filter_mod = importlib.import_module(
    "taichi_vision.taichi_algorithm.smoothing.box_filter"
)

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

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

    # --- VECTOR 3D GRAPHS (New Standard) ---
    src_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    tmp_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tmp", ti.types.vector(3, ti.f32), ndim=2)
    dst_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)

    g_3x3_vec3 = ti.graph.GraphBuilder()
    g_3x3_vec3.dispatch(box_filter_mod._box_filter_3x3_vec3_f32_kernel, src_vec3, dst_vec3, h_arg, w_arg)
    module.add_graph("box_filter_fused_3x3_vec3_f32", g_3x3_vec3.compile())

    g_sep_vec3 = ti.graph.GraphBuilder()
    g_sep_vec3.dispatch(box_filter_mod._box_blur_h_vec3_f32_kernel, src_vec3, tmp_vec3, h_arg, w_arg, radius_arg)
    g_sep_vec3.dispatch(box_filter_mod._box_blur_v_vec3_f32_kernel, tmp_vec3, dst_vec3, h_arg, w_arg, radius_arg)
    module.add_graph("box_filter_separable_generic_vec3_f32", g_sep_vec3.compile())

    # --- 1-CHANNEL GRAYSCALE GRAPHS ---
    src_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    tmp_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tmp", ti.f32, ndim=2)
    dst_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)

    g_3x3_1ch = ti.graph.GraphBuilder()
    g_3x3_1ch.dispatch(box_filter_mod._box_filter_3x3_1ch_f32_unrolled_kernel, src_1d, dst_1d, h_arg, w_arg)
    module.add_graph("box_filter_fused_3x3_1ch_f32", g_3x3_1ch.compile())

    g_sep_1ch = ti.graph.GraphBuilder()
    g_sep_1ch.dispatch(box_filter_mod._box_blur_h_generic_1ch_kernel, src_1d, tmp_1d, h_arg, w_arg, radius_arg)
    g_sep_1ch.dispatch(box_filter_mod._box_blur_v_generic_1ch_kernel, tmp_1d, dst_1d, h_arg, w_arg, radius_arg)
    module.add_graph("box_filter_separable_generic_1ch_f32", g_sep_1ch.compile())
    
    archive_module(module, save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"box_filter_{suffix}.tcm"))
        try:
            compile_box_filter_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
