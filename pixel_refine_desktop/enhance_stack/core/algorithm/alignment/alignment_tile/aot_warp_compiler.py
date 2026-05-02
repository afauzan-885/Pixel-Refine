import taichi as ti
import os
import sys

# Add project root to sys.path
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.warp import (
    warp_image_gpu
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
    _upsample_flow_kernel
)

def compile_warp_aot(arch=ti.vulkan, save_path="warp_vulkan.tcm"):
    ti.init(arch=arch, offline_cache=False)

    # Compile Module
    module = ti.aot.Module(arch)
    
    # Graph 1: Upsample
    up_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    up_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    up_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    
    g_up = ti.graph.GraphBuilder()
    # Use standard upsample from pyramid.py
    g_up.dispatch(_upsample_flow_kernel, up_src, up_dst, up_scale)
    module.add_graph("upsample_flow", g_up.compile())
    
    # Graph 2: Warp RGB Guided
    w_src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3)
    w_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
    w_dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    w_ref_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", ti.i32, ndim=3)
    
    g_warp_rgb = ti.graph.GraphBuilder()
    warp_image_gpu(
        None, None, g=g_warp_rgb, 
        src_arg=w_src_3d, flow_arg=w_flow, dst_arg=w_dst_3d, ref_arg=w_ref_3d,
        is_rgb_aot=True
    )
    module.add_graph("warp_rgb", g_warp_rgb.compile())

    # Graph 3: Warp Gray Guided (Optional, needed by some pipelines)
    w_src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    w_dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    w_ref_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "guide", ti.i32, ndim=2)
    
    g_warp_gray = ti.graph.GraphBuilder()
    warp_image_gpu(
        None, None, g=g_warp_gray, 
        src_arg=w_src_2d, flow_arg=w_flow, dst_arg=w_dst_2d, ref_arg=w_ref_2d,
        is_rgb_aot=False
    )
    module.add_graph("warp_gray", g_warp_gray.compile())
    
    module.archive(save_path)
    print(f"Successfully archived {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../../../../../", "ui", "data", "aot_assets")
    os.makedirs(assets_dir, exist_ok=True)
    save_path = os.path.abspath(os.path.join(assets_dir, "warp_vulkan.tcm"))
    compile_warp_aot(save_path=save_path)
