import taichi as ti
import os
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.box_filter
box_filter_module = sys.modules["pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.box_filter"]

def compile_box_filter_aot(arch=ti.vulkan, save_path="box_filter_vulkan.tcm"):
    print(f"\n>>> Compiling BOX FILTER AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # Common Args
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    c_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "c", ti.i32)

    # 1. 2D Box Filter
    g_2d = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_2d.dispatch(box_filter_module._box_filter_2d_kernel, src_2d, dst_2d, h_arg, w_arg, radius_arg)
    module.add_graph("box_filter_2d_f32", g_2d.compile())

    # 2. 3D Box Filter
    g_3d = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_3d.dispatch(box_filter_module._box_filter_3d_kernel, src_3d, dst_3d, h_arg, w_arg, radius_arg, c_arg)
    module.add_graph("box_filter_3d_f32", g_3d.compile())

    # 3. Flow Box Filter (H, W, 2)
    g_flow = ti.graph.GraphBuilder()
    src_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_flow.dispatch(box_filter_module._box_filter_flow_kernel, src_flow, dst_flow, h_arg, w_arg, radius_arg)
    module.add_graph("box_filter_flow_f32", g_flow.compile())

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
        save_path = os.path.abspath(os.path.join(assets_dir, f"box_filter_{suffix}.tcm"))
        try:
            compile_box_filter_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
