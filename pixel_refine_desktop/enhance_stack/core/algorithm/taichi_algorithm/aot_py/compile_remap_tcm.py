import taichi as ti
import os
import sys

# Setup path to find taichi_algorithm
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Set AOT Mode for the algorithm imports
os.environ["PIXEL_REFINE_AOT_MODE"] = "1"

from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.remap import (
    _remap_kernel, _remap_kernel_vec3,
    _build_flow_maps_kernel, _build_flow_maps_from_2ch_kernel,
    _smooth_flow_kernel, _smooth_flow_y_kernel,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.enhance_image import (
    _enhance_grayscale_kernel,
)

def compile_remap_tcm(arch=ti.vulkan, save_path="remap_vulkan.tcm"):
    print(f"\n>>> Compiling Remap AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # Common scalar args shared by remap and flow-map graphs
    h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
    w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
    h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
    w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)
    map_x = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_x", ti.f32, ndim=2)
    map_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_y", ti.f32, ndim=2)

    # 1. Remap 2D (Grayscale)
    g_remap_2d = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_remap_2d.dispatch(_remap_kernel, src_2d, map_x, map_y, dst_2d, h_src, w_src, h_dst, w_dst)
    module.add_graph("remap_f32_2d", g_remap_2d.compile())

    # 2. Remap 3D (Color / Vector3)
    g_remap_3d = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    g_remap_3d.dispatch(_remap_kernel_vec3, src_3d, map_x, map_y, dst_3d, h_src, w_src, h_dst, w_dst)
    module.add_graph("remap_f32_3d", g_remap_3d.compile())

    # 3. Build Flow Maps from separate dx/dy (2D each)
    g_build_maps = ti.graph.GraphBuilder()
    dx_arg    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dx",    ti.f32, ndim=2)
    dy_arg    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dy",    ti.f32, ndim=2)
    mx_out    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_x", ti.f32, ndim=2)
    my_out    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_y", ti.f32, ndim=2)
    h_flow_a  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_flow", ti.i32)
    w_flow_a  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_flow", ti.i32)
    h_dst_b   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst",  ti.i32)
    w_dst_b   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst",  ti.i32)
    scale_x_a = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_x", ti.f32)
    scale_y_a = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_y", ti.f32)
    g_build_maps.dispatch(
        _build_flow_maps_kernel, dx_arg, dy_arg, mx_out, my_out,
        h_flow_a, w_flow_a, h_dst_b, w_dst_b, scale_x_a, scale_y_a,
    )
    module.add_graph("build_flow_maps", g_build_maps.compile())

    # 4. Smooth Flow (Gaussian separable blur on 2-channel flow field H,W,2)
    h_arg     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_a  = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    weights_a = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=1)
    flow_src  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    flow_dst  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)

    g_smooth_x = ti.graph.GraphBuilder()
    g_smooth_x.dispatch(_smooth_flow_kernel, flow_src, flow_dst, h_arg, w_arg, weights_a, radius_a)
    module.add_graph("smooth_flow_x", g_smooth_x.compile())

    g_smooth_y = ti.graph.GraphBuilder()
    g_smooth_y.dispatch(_smooth_flow_y_kernel, flow_src, flow_dst, h_arg, w_arg, weights_a, radius_a)
    module.add_graph("smooth_flow_y", g_smooth_y.compile())

    # 5. Build Flow Maps from 2-channel flow (H,W,2) — no extract_channel needed
    g_bfm_2ch = ti.graph.GraphBuilder()
    flow_2ch  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", ti.f32, ndim=3)
    mx_2ch    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_x", ti.f32, ndim=2)
    my_2ch    = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "map_y", ti.f32, ndim=2)
    h_f_2ch   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_flow", ti.i32)
    w_f_2ch   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_flow", ti.i32)
    h_d_2ch   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst",  ti.i32)
    w_d_2ch   = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst",  ti.i32)
    sx_2ch    = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_x", ti.f32)
    sy_2ch    = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale_y", ti.f32)
    g_bfm_2ch.dispatch(
        _build_flow_maps_from_2ch_kernel, flow_2ch, mx_2ch, my_2ch,
        h_f_2ch, w_f_2ch, h_d_2ch, w_d_2ch, sx_2ch, sy_2ch,
    )
    module.add_graph("build_flow_maps_from_2ch", g_bfm_2ch.compile())

    # 6. Grayscale Image Enhancement (1D LUT & Micro-Contrast)
    g_enhance = ti.graph.GraphBuilder()
    enh_src   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    enh_blur  = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "blur", ti.f32, ndim=2)
    enh_lut   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "lut", ti.f32, ndim=1)
    enh_dst   = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    enh_mc    = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "micro_contrast", ti.f32)
    enh_h     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    enh_w     = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    g_enhance.dispatch(
        _enhance_grayscale_kernel, enh_src, enh_blur, enh_lut, enh_dst, enh_mc, enh_h, enh_w
    )
    module.add_graph("enhance_grayscale", g_enhance.compile())

    # Archive the module
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
        save_path = os.path.abspath(os.path.join(assets_dir, f"remap_{suffix}.tcm"))
        try:
            compile_remap_tcm(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
