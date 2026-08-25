import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys
import importlib

file_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "aot_py"))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

gaussian_mod = importlib.import_module("taichi_vision.taichi_algorithm.smoothing.gaussian")

try:
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import normalize_tcm
except ImportError:  # Direct script execution.
    from aot_artifact import normalize_tcm

def compile_gaussian_tcm():
    # The suite worker sets AOT_ARCH/TARGET_BACKEND.  Prefer the explicit
    # project override, then those worker markers, so a CPU migration can
    # never silently emit a Vulkan archive into a CPU-qualified directory.
    arch_str = (
        os.environ.get("PIXEL_REFINE_AOT_ARCH")
        or os.environ.get("TARGET_BACKEND")
        or os.environ.get("AOT_ARCH")
        or "vulkan"
    ).lower()
    arch = ti.vulkan
    if arch_str == "cuda": arch = ti.cuda
    elif arch_str == "cpu": arch = ti.x64
    elif arch_str == "opengl": arch = ti.opengl
    elif arch_str == "gles": arch = ti.gles
    
    print(f"\n>>> Compiling GAUSSIAN BLUR AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    
    save_dir = os.environ.get(
        "PIXEL_REFINE_AOT_TCM_ROOT",
        os.path.join(file_dir, "../aot_tcm"),
    )
    os.makedirs(save_dir, exist_ok=True)
    suffix = "vulkan"
    if arch == ti.cuda: suffix = "cuda"
    elif arch == ti.x64: suffix = "cpu"
    elif arch == ti.opengl: suffix = "opengl"
    elif arch == ti.gles: suffix = "gles"
    save_path = os.path.join(save_dir, f"gaussian_{suffix}.tcm")

    # Gaussian kernels and weights are f32/i32. Do not advertise Float64:
    # doing so needlessly excludes Vulkan devices lacking shaderFloat64.
    module = ti.aot.Module(arch)

    h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    radius_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", ti.i32)
    weights_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weights", ti.f32, ndim=1)

    # 3-Channel f32 (3D Scalar)
    src_3d_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_3d_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    
    g_x_3ch_f32 = ti.graph.GraphBuilder()
    g_x_3ch_f32.dispatch(gaussian_mod._gaussian_blur_x_3ch_f32_kernel, src_3d_f32, dst_3d_f32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_3ch_f32", g_x_3ch_f32.compile())

    g_y_3ch_f32 = ti.graph.GraphBuilder()
    g_y_3ch_f32.dispatch(gaussian_mod._gaussian_blur_y_3ch_f32_kernel, src_3d_f32, dst_3d_f32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_3ch_f32", g_y_3ch_f32.compile())

    # 1-Channel f32 (2D Scalar)
    src_2d_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_2d_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    g_x_1ch_f32 = ti.graph.GraphBuilder()
    g_x_1ch_f32.dispatch(gaussian_mod._gaussian_blur_x_1ch_f32_kernel, src_2d_f32, dst_2d_f32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_1ch_f32", g_x_1ch_f32.compile())

    g_y_1ch_f32 = ti.graph.GraphBuilder()
    g_y_1ch_f32.dispatch(gaussian_mod._gaussian_blur_y_1ch_f32_kernel, src_2d_f32, dst_2d_f32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_1ch_f32", g_y_1ch_f32.compile())
    
    # --- VECTOR 3D GRAPHS (New Standard) ---
    src_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_vec3 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    
    g_x_vec3_f32 = ti.graph.GraphBuilder()
    g_x_vec3_f32.dispatch(gaussian_mod._gaussian_blur_x_vec3_f32_kernel, src_vec3, dst_vec3, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_vec3_f32", g_x_vec3_f32.compile())
    
    g_y_vec3_f32 = ti.graph.GraphBuilder()
    g_y_vec3_f32.dispatch(gaussian_mod._gaussian_blur_y_vec3_f32_kernel, src_vec3, dst_vec3, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_vec3_f32", g_y_vec3_f32.compile())

    # --- i32 GRAPHS (Optional but included for parity) ---
    src_3d_i32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=3)
    dst_3d_i32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=3)
    
    g_x_3ch_i32 = ti.graph.GraphBuilder()
    g_x_3ch_i32.dispatch(gaussian_mod._gaussian_blur_x_3ch_i32_kernel, src_3d_i32, dst_3d_i32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_x_3ch_i32", g_x_3ch_i32.compile())

    g_y_3ch_i32 = ti.graph.GraphBuilder()
    g_y_3ch_i32.dispatch(gaussian_mod._gaussian_blur_y_3ch_i32_kernel, src_3d_i32, dst_3d_i32, h_arg, w_arg, weights_arg, radius_arg)
    module.add_graph("gaussian_blur_y_3ch_i32", g_y_3ch_i32.compile())

    module.archive(save_path)
    normalize_tcm(save_path)
    print(f"Successfully compiled and archived to: {save_path}")

if __name__ == "__main__":
    compile_gaussian_tcm()
