import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys
import importlib

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

common_mod = importlib.import_module("taichi_library.taichi_algorithm.common")

def compile_common_aot(arch=ti.vulkan, save_path="common_vulkan.tcm"):
    print(f"\n>>> Compiling COMMON UTILS AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    # 1. Copy Kernels
    def add_copy(name, dtype, is_vec=False):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        else:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype, ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        builder.dispatch(common_mod._copy_kernel, src, dst)
        module.add_graph(name, builder.compile())

    add_copy("copy_f32_2d", ti.f32)
    add_copy("copy_i32_2d", ti.i32)
    add_copy("copy_vec3_2d", ti.f32, is_vec=True)
    add_copy("copy_vec3_i32_2d", ti.i32, is_vec=True)

    # 2. Channel Kernels
    def add_extract(name, dtype):
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        ch = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ch", ti.i32)
        builder.dispatch(common_mod._extract_channel_kernel, src, dst, ch)
        module.add_graph(name, builder.compile())

    add_extract("extract_channel_f32", ti.f32)
    add_extract("extract_channel_i32", ti.i32)

    def add_insert(name, dtype):
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        ch = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "ch", ti.i32)
        builder.dispatch(common_mod._insert_channel_kernel, src, dst, ch)
        module.add_graph(name, builder.compile())

    add_insert("insert_channel_f32", ti.f32)
    add_insert("insert_channel_i32", ti.i32)

    def add_split_3ch(name, dtype):
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
        c0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c0", dtype, ndim=2)
        c1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c1", dtype, ndim=2)
        c2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c2", dtype, ndim=2)
        # Using custom lambda to dispatch 3 times
        @ti.kernel
        def split_kernel(s: ti.types.ndarray(), c0: ti.types.ndarray(), c1: ti.types.ndarray(), c2: ti.types.ndarray()):
            for i, j in c0:
                c0[i, j] = s[i, j][0]
                c1[i, j] = s[i, j][1]
                c2[i, j] = s[i, j][2]
        builder.dispatch(split_kernel, src, c0, c1, c2)
        module.add_graph(name, builder.compile())

    add_split_3ch("split_3ch_f32", ti.f32)
    add_split_3ch("split_3ch_i32", ti.i32)

    def add_merge_3ch(name, dtype):
        builder = ti.graph.GraphBuilder()
        c0 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c0", dtype, ndim=2)
        c1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c1", dtype, ndim=2)
        c2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "c2", dtype, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        @ti.kernel
        def merge_kernel(c0: ti.types.ndarray(), c1: ti.types.ndarray(), c2: ti.types.ndarray(), d: ti.types.ndarray()):
            for i, j in c0:
                d[i, j] = ti.Vector([c0[i, j], c1[i, j], c2[i, j]])
        builder.dispatch(merge_kernel, c0, c1, c2, dst)
        module.add_graph(name, builder.compile())

    add_merge_3ch("merge_3ch_f32", ti.f32)
    add_merge_3ch("merge_3ch_i32", ti.i32)

    # 3. Color Kernels
    def add_cvt(name, kernel, dtype):
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        builder.dispatch(kernel, src, dst)
        module.add_graph(name, builder.compile())

    add_cvt("rgb2gray_f32", common_mod._cvt_color_rgb_to_gray_kernel, ti.f32)
    add_cvt("rgb2gray_i32", common_mod._cvt_color_rgb_to_gray_i32_kernel, ti.i32)
    add_cvt("bgr2gray_f32", common_mod._cvt_color_bgr_to_gray_kernel, ti.f32)

    # 4. Math Kernels
    def add_absdiff(name, dtype):
        builder = ti.graph.GraphBuilder()
        src1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src1", dtype, ndim=2)
        src2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src2", dtype, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        builder.dispatch(common_mod._absdiff_kernel, src1, src2, dst)
        module.add_graph(name, builder.compile())

    add_absdiff("absdiff_f32_2d", ti.f32)
    add_absdiff("absdiff_i32_2d", ti.i32)

    def add_absdiff_vec3(name, dtype):
        builder = ti.graph.GraphBuilder()
        src1 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src1", ti.types.vector(3, dtype), ndim=2)
        src2 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src2", ti.types.vector(3, dtype), ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        builder.dispatch(common_mod._absdiff_kernel, src1, src2, dst)
        module.add_graph(name, builder.compile())

    add_absdiff_vec3("absdiff_vec3_f32", ti.f32)

    # 5. Hanning Window Kernel
    def add_hanning_window(name):
        builder = ti.graph.GraphBuilder()
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "H", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "W", ti.i32)
        exclude_boundary = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "exclude_boundary", ti.i32)
        builder.dispatch(common_mod._generate_hanning_window_2d_kernel, dst, h, w, exclude_boundary)
        module.add_graph(name, builder.compile())

    add_hanning_window("generate_hanning_window_2d")

    # 6. Mean Division Kernels
    def add_mean_division(name, dtype, is_vec=False):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            sum_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_img", ti.types.vector(3, dtype), ndim=2)
            ref_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_img", ti.types.vector(3, dtype), ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        else:
            sum_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_img", dtype, ndim=2)
            ref_img = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_img", dtype, ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        sum_weight = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_weight", dtype, ndim=2)
        builder.dispatch(common_mod._mean_division_kernel, sum_img, sum_weight, ref_img, dst)
        module.add_graph(name, builder.compile())

    add_mean_division("mean_division_f32", ti.f32, is_vec=False)
    add_mean_division("mean_division_vec3_f32", ti.f32, is_vec=True)

    module.archive(save_path)
    print(f"Successfully compiled and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)
    
    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"common_{suffix}.tcm"))
        try:
            compile_common_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
