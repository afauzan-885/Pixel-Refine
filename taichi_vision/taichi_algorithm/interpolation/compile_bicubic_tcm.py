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

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:
    from aot_artifact import archive_module

# Set AOT Mode globally before importing taichi_worker or related scripts

from taichi_vision.taichi_algorithm.interpolation import bicubic_interpolation as bicubic


def compile_bicubic_aot(arch=ti.vulkan, save_path="bicubic_interpolation_vulkan.tcm"):
    print(f"\n>>> Compiling BICUBIC AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    # Compile Module
    module = ti.aot.Module(arch)

    # Common Scalar Args
    h_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_src", ti.i32)
    w_src = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_src", ti.i32)
    h_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_dst", ti.i32)
    w_dst = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_dst", ti.i32)
    n_samples = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_samples", ti.i32)

    # 1. Graph: Bicubic Resize (Grayscale / 2D)
    g_resize_2d = ti.graph.GraphBuilder()
    src_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)

    bicubic.bicubic_resize(
        g=g_resize_2d,
        src_arg=src_2d,
        dst_arg=dst_2d,
        h_src_arg=h_src,
        w_src_arg=w_src,
        h_dst_arg=h_dst,
        w_dst_arg=w_dst,
        is_rgb_aot=False,
    )
    module.add_graph("bicubic_resize_f32_2d", g_resize_2d.compile())

    # 2. Graph: Bicubic Resize (RGB / Vector3)
    g_resize_3d = ti.graph.GraphBuilder()
    src_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)

    bicubic.bicubic_resize(
        g=g_resize_3d,
        src_arg=src_3d,
        dst_arg=dst_3d,
        h_src_arg=h_src,
        w_src_arg=w_src,
        h_dst_arg=h_dst,
        w_dst_arg=w_dst,
        is_rgb_aot=True,
    )
    module.add_graph("bicubic_resize_f32_3d", g_resize_3d.compile())

    # 3. Graph: Bicubic Sampling (Grayscale / 2D)
    g_sample_2d = ti.graph.GraphBuilder()
    src_s2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    coords_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coords", ti.f32, ndim=2)
    results_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.f32, ndim=1)

    g_sample_2d.dispatch(
        bicubic._bicubic_sample_kernel_2d,
        src_s2d,
        coords_2d,
        results_2d,
        n_samples,
        h_src,
        w_src,
    )
    module.add_graph("bicubic_sample_f32_2d", g_sample_2d.compile())

    # 4. Graph: Bicubic Sampling (RGB / Vector3)
    g_sample_3d = ti.graph.GraphBuilder()
    src_s3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    coords_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coords", ti.f32, ndim=2)
    results_3d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "results", ti.types.vector(3, ti.f32), ndim=1)

    g_sample_3d.dispatch(
        bicubic._bicubic_sample_kernel_vec3,
        src_s3d,
        coords_3d,
        results_3d,
        n_samples,
        h_src,
        w_src,
    )
    module.add_graph("bicubic_sample_f32_3d", g_sample_3d.compile())

    offset_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_y", ti.i32)
    offset_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_x", ti.i32)
    g_tile_2d = ti.graph.GraphBuilder()
    g_tile_2d.dispatch(bicubic._bicubic_resize_offset_kernel_2d, src_2d, dst_2d, h_src, w_src, h_dst, w_dst, offset_y, offset_x)
    module.add_graph("bicubic_resize_offset_f32_2d", g_tile_2d.compile())
    g_tile_3d = ti.graph.GraphBuilder()
    g_tile_3d.dispatch(bicubic._bicubic_resize_offset_kernel_vec3, src_3d, dst_3d, h_src, w_src, h_dst, w_dst, offset_y, offset_x)
    module.add_graph("bicubic_resize_offset_f32_3d", g_tile_3d.compile())

    # Archive the module
    archive_module(module, save_path)
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
        save_path = os.path.abspath(os.path.join(assets_dir, f"bicubic_{suffix}.tcm"))
        try:
            compile_bicubic_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
