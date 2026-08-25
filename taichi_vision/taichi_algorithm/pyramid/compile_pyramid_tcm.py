import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Add project root to sys.path to allow imports
file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set AOT Mode globally before importing taichi_worker or related scripts

from taichi_vision.taichi_algorithm.pyramid import pyramid

def compile_pyramid_aot(arch=ti.vulkan, save_path="pyramid_vulkan.tcm"):
    print(f"\n>>> Compiling PYRAMID AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Graph: Downsample 2x (Grayscale / Flow / Any 2D)
    # Note: pyramid._downsample_2x_kernel takes 2D f32 arrays
    g_down = ti.graph.GraphBuilder()
    src_d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    g_down.dispatch(pyramid._downsample_2x_kernel, src_d, dst_d)
    module.add_graph("downsample_2x_f32", g_down.compile())

    # 1.5 Graph: Downsample 2x 3-Channel
    g_down_3ch = ti.graph.GraphBuilder()
    src_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_down_3ch.dispatch(pyramid._downsample_2x_kernel_3ch, src_3ch, dst_3ch)
    module.add_graph("downsample_2x_3ch_f32", g_down_3ch.compile())

    offset_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_y", ti.i32)
    offset_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_x", ti.i32)
    g_down_offset = ti.graph.GraphBuilder()
    g_down_offset.dispatch(pyramid._downsample_2x_offset_kernel, src_d, dst_d, offset_y, offset_x)
    module.add_graph("downsample_2x_offset_f32", g_down_offset.compile())
    g_down_offset_3ch = ti.graph.GraphBuilder()
    g_down_offset_3ch.dispatch(pyramid._downsample_2x_offset_kernel_3ch, src_3ch, dst_3ch, offset_y, offset_x)
    module.add_graph("downsample_2x_offset_3ch_f32", g_down_offset_3ch.compile())

    # 2. Graph: Upsample Flow (3D array, HxWx2 usually but declared as 3D)
    g_up = ti.graph.GraphBuilder()
    src_u = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_u = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    
    g_up.dispatch(pyramid._upsample_flow_kernel, src_u, dst_u, scale)
    module.add_graph("upsample_flow_f32", g_up.compile())

    # Archive
    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = file_dir
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu")
    ]
    
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"pyramid_{suffix}.tcm"))
        try:
            compile_pyramid_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
