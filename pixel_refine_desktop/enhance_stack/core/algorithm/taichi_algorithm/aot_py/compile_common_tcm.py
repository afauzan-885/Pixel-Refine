import taichi as ti
import os
import numpy as np

def compile_common_tcm():
    arch_str = os.environ.get("PIXEL_REFINE_AOT_ARCH", "vulkan").lower()
    arch = ti.vulkan
    if arch_str == "cuda": arch = ti.cuda
    elif arch_str == "cpu": arch = ti.x64
    
    ti.init(arch=arch)
    
    save_dir = os.path.join(os.path.dirname(__file__), "../aot_tcm")
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "common.tcm")

    module = ti.aot.Module(arch)

    # --- Types ---
    vec3i = ti.types.vector(3, ti.i32)

    # --- Utility Kernels ---
    
    @ti.kernel
    def _copy_i32_2d(src: ti.types.ndarray(dtype=ti.i32, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2)):
        for i, j in src: dst[i, j] = src[i, j]

    @ti.kernel
    def _copy_vec3_2d(src: ti.types.ndarray(dtype=vec3i, ndim=2), dst: ti.types.ndarray(dtype=vec3i, ndim=2)):
        for i, j in src: dst[i, j] = src[i, j]

    @ti.kernel
    def _copy_f32_2d(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2)):
        for i, j in src: dst[i, j] = src[i, j]

    # 1-Dispatch Merge for 3 Channels (Maximum Efficiency)
    @ti.kernel
    def _merge_3ch_i32(c0: ti.types.ndarray(dtype=ti.i32, ndim=2), 
                       c1: ti.types.ndarray(dtype=ti.i32, ndim=2), 
                       c2: ti.types.ndarray(dtype=ti.i32, ndim=2), 
                       dst: ti.types.ndarray(dtype=vec3i, ndim=2)):
        for i, j in dst:
            dst[i, j] = vec3i(c0[i, j], c1[i, j], c2[i, j])

    # 1-Dispatch Split for 3 Channels
    @ti.kernel
    def _split_3ch_i32(src: ti.types.ndarray(dtype=vec3i, ndim=2),
                       c0: ti.types.ndarray(dtype=ti.i32, ndim=2),
                       c1: ti.types.ndarray(dtype=ti.i32, ndim=2),
                       c2: ti.types.ndarray(dtype=ti.i32, ndim=2)):
        for i, j in src:
            val = src[i, j]
            c0[i, j] = val[0]
            c1[i, j] = val[1]
            c2[i, j] = val[2]

    # Individual extract/insert as fallback
    @ti.kernel
    def _extract_ch_i32(src: ti.types.ndarray(dtype=vec3i, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2), ch: ti.i32):
        for i, j in dst:
            val = src[i, j]
            if ch == 0: dst[i, j] = val[0]
            elif ch == 1: dst[i, j] = val[1]
            else: dst[i, j] = val[2]

    @ti.kernel
    def _rgb2gray_i32(src: ti.types.ndarray(dtype=vec3i, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2)):
        for i, j in dst:
            val = src[i, j]
            dst[i, j] = (306 * val[0] + 601 * val[1] + 117 * val[2]) >> 10

    @ti.kernel
    def _absdiff_i32_2d(src1: ti.types.ndarray(dtype=ti.i32, ndim=2), src2: ti.types.ndarray(dtype=ti.i32, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2)):
        for i, j in dst: dst[i, j] = ti.abs(src1[i, j] - src2[i, j])

    # --- Add Graphs ---
    
    def add_g(name, kernel, *args):
        b = ti.graph.GraphBuilder()
        b.dispatch(kernel, *args)
        module.add_graph(name, b.compile())

    arg_i2 = lambda name: ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.i32, ndim=2)
    arg_v3 = lambda name: ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, vec3i, ndim=2)

    # 1. Copy
    add_g("copy_i32_2d", _copy_i32_2d, arg_i2("src"), arg_i2("dst"))
    add_g("copy_vec3_2d", _copy_vec3_2d, arg_v3("src"), arg_v3("dst"))
    
    arg_f2 = lambda name: ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=2)
    add_g("copy_f32_2d", _copy_f32_2d, arg_f2("src"), arg_f2("dst"))

    # 2. Merge 3-ch
    add_g("merge_3ch_i32", _merge_3ch_i32, arg_i2("c0"), arg_i2("c1"), arg_i2("c2"), arg_v3("dst"))

    # 3. Split 3-ch
    add_g("split_3ch_i32", _split_3ch_i32, arg_v3("src"), arg_i2("c0"), arg_i2("c1"), arg_i2("c2"))

    # 4. Utilities
    add_g("rgb2gray_i32", _rgb2gray_i32, arg_v3("src"), arg_i2("dst"))
    
    arg_scalar = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ch", ti.i32)
    add_g("extract_channel_i32", _extract_ch_i32, arg_v3("src"), arg_i2("dst"), arg_scalar)
    
    add_g("absdiff_i32_2d", _absdiff_i32_2d, arg_i2("src"), arg_i2("src2"), arg_i2("dst"))

    module.archive(save_path)
    print(f"Successfully compiled Common AOT to: {save_path}")

if __name__ == "__main__":
    compile_common_tcm()
