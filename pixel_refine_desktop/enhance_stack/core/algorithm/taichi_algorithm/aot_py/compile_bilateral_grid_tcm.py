import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Path injection for project root
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)


import pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.bilateral_grid as bg

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
    grid_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grid", ti.types.vector(2, ti.f32), ndim=3)
    g_clear.dispatch(bg._bg_clear_grid, grid_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_clear", g_clear.compile())

    # 2. Splat Graph
    g_splat = ti.graph.GraphBuilder()
    src_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    g_splat.dispatch(bg._bg_splat, src_arg, grid_arg, s_s_arg, s_r_arg, h_arg, w_arg, gn_arg, gm_arg, gl_arg)
    module.add_graph("bg_splat", g_splat.compile())

    # 3. Blur Graphs (X, Y, Z)
    g_blur_x = ti.graph.GraphBuilder()
    dst_grid_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_grid", ti.types.vector(2, ti.f32), ndim=3)
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

    module.archive(save_path)
    print(f"Archive saved to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    tcm_dir = "../aot_tcm"
    os.makedirs(tcm_dir, exist_ok=True)
    compile_bg_aot(ti.vulkan, os.path.join(tcm_dir, "bilateral_grid_vulkan.tcm"))
    compile_bg_aot(ti.cuda, os.path.join(tcm_dir, "bilateral_grid_cuda.tcm"))
