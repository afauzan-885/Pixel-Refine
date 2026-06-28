import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys

# Path resolution
file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_library.taichi_algorithm import area_interpolation as area

def compile_area_aot(arch, save_path):
    print(f"\n>>> Compiling INTER_AREA AOT for: {arch}")
    ti.init(arch=arch)
    module = ti.aot.Module(arch)
    
    # Arguments
    sh = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sh", ti.i32)
    sw = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sw", ti.i32)
    dh = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dh", ti.i32)
    dw = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dw", ti.i32)
    
    # 1. 1-Channel Graph
    g_1ch = ti.graph.GraphBuilder()
    src_1ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    dst_1ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    g_1ch.dispatch(area._inter_area_1ch_kernel, src_1ch, dst_1ch, sh, sw, dh, dw)
    module.add_graph("inter_area_f32", g_1ch.compile())

    # 2. Vec3 Graph
    g_3ch = ti.graph.GraphBuilder()
    src_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
    dst_3ch = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
    g_3ch.dispatch(area._inter_area_vec3_kernel, src_3ch, dst_3ch, sh, sw, dh, dw)
    module.add_graph("inter_area_vec3_f32", g_3ch.compile())

    module.archive(save_path)
    print(f"Archive saved to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    tcm_dir = "../aot_tcm"
    os.makedirs(tcm_dir, exist_ok=True)
    compile_area_aot(ti.vulkan, os.path.join(tcm_dir, "area_vulkan.tcm"))
    compile_area_aot(ti.cuda, os.path.join(tcm_dir, "area_cuda.tcm"))
    compile_area_aot(ti.cpu, os.path.join(tcm_dir, "area_cpu.tcm"))
