import argparse
import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Path injection for project root
file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
# aot_py -> taichi_algorithm -> taichi_vision -> project root
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import taichi_vision.taichi_algorithm.smoothing.bilateral_grid as bg

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module
except ImportError:  # Direct script execution.
    from aot_artifact import archive_module

def compile_bg_aot(arch, save_path):
    print(f"\n>>> Compiling Bilateral Grid AOT for: {arch}")
    ti.init(arch=arch)
    module = ti.aot.Module(arch)
    
    # Common arguments
    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    gn_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gn", ti.i32)
    gm_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gm", ti.i32)
    gl_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gl", ti.i32)
    s_s_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "s_s", ti.i32)
    s_r_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "s_r", ti.i32)
    rad_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    sig_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma", ti.f32)

    # 1. Clear Grid Graph
    g_clear = ti.graph.GraphBuilder()
    # ``grid[i, j, k]`` is a vec2 in the kernels; encoding it as scalar f32
    # rank-4 makes the component access ``[0]`` appear as a fifth index to
    # Taichi's graph validator.  Keep the public HxWxLx2 buffer ABI via a
    # vector2 rank-3 ndarray descriptor.
    grid_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "grid", ti.types.vector(2, ti.f32), ndim=3
    )
    g_clear.dispatch(bg._bg_clear_grid, grid_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_clear", g_clear.compile())

    # 2. Splat Graph
    g_splat = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    g_splat.dispatch(bg._bg_splat, src_arg, grid_arg, s_s_arg, s_r_arg, h_arg, w_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_splat", g_splat.compile())

    # 3. Blur Graphs (X, Y, Z)
    g_blur_x = ti.graph.GraphBuilder()
    dst_grid_arg = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "dst_grid", ti.types.vector(2, ti.f32), ndim=3
    )
    g_blur_x.dispatch(bg._bg_blur_x, grid_arg, dst_grid_arg, rad_arg, sig_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_blur_x", g_blur_x.compile())

    g_blur_y = ti.graph.GraphBuilder()
    g_blur_y.dispatch(bg._bg_blur_y, grid_arg, dst_grid_arg, rad_arg, sig_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_blur_y", g_blur_y.compile())

    g_blur_z = ti.graph.GraphBuilder()
    g_blur_z.dispatch(bg._bg_blur_z, grid_arg, dst_grid_arg, rad_arg, sig_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_blur_z", g_blur_z.compile())

    # 4. Slice Graph
    g_slice = ti.graph.GraphBuilder()
    dst_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_slice.dispatch(bg._bg_slice, src_arg, grid_arg, dst_arg, s_s_arg, s_r_arg, h_arg, w_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_slice", g_slice.compile())

    archive_module(module, save_path)
    print(f"Archive saved to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile Bilateral Grid AOT modules")
    parser.add_argument(
        "--backend",
        action="append",
        choices=("cpu", "vulkan", "opengl", "gles", "cuda"),
        help=(
            "Backend to compile; may be supplied more than once "
            "(default: cpu, vulkan, cuda)"
        ),
    )
    requested = parser.parse_args().backend or ["cpu", "vulkan", "cuda"]
    tcm_dir = os.path.abspath(os.path.join(file_dir, "..", "aot_tcm"))
    os.makedirs(tcm_dir, exist_ok=True)
    arches = {
        "cpu": ti.cpu,
        "vulkan": ti.vulkan,
        "opengl": ti.opengl,
        "gles": ti.gles,
        "cuda": ti.cuda,
    }
    for backend in requested:
        compile_bg_aot(arches[backend], os.path.join(tcm_dir, f"bilateral_grid_{backend}.tcm"))
