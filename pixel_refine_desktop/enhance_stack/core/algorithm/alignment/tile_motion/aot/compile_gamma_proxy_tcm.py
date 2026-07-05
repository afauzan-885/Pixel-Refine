import taichi as ti
import os
import sys
import importlib

file_dir = os.path.dirname(os.path.abspath(__file__))
# 6 levels up to reach pixel_refine_desktop
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
# Relative import from the new aot folder
import gamma_proxy_kernels as kernels_mod

def compile_gamma_proxy_aot(arch=ti.vulkan, save_path="gamma_proxy_vulkan.tcm"):
    print(f"\n>>> Compiling GAMMA PROXY AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # Scalars
    scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    gamma_pow = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "gamma_pow", ti.f32)
    slope = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "slope", ti.f32)
    cutoff = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "cutoff", ti.f32)

    # 1. RGB Graph (FP32 vector source)
    builder_rgb = ti.graph.GraphBuilder()
    src_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    cmatrix_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "cmatrix", ti.f32, ndim=2)
    
    builder_rgb.dispatch(kernels_mod.gamma_proxy_rgb_kernel, 
                         src_rgb, dst_rgb, cmatrix_arg, scale, gamma_pow, slope, cutoff)
    module.add_graph("gamma_proxy_rgb", builder_rgb.compile())

    # 2. Single Channel Graph (FP32 source)
    builder_single = ti.graph.GraphBuilder()
    src_single = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_single = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    
    builder_single.dispatch(kernels_mod.gamma_proxy_single_kernel, 
                           src_single, dst_single, scale, gamma_pow, slope, cutoff)
    module.add_graph("gamma_proxy_single", builder_single.compile())

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 6 levels up to reach pixel_refine_desktop then into ui/data/aot_assets
    assets_dir = os.path.abspath(os.path.join(script_dir, "../../../../../../ui/data/aot_assets"))
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.join(assets_dir, f"gamma_proxy_{suffix}.tcm")
        try:
            compile_gamma_proxy_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
