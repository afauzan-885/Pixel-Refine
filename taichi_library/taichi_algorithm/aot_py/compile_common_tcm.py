import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import os
import sys
import importlib

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

common_mod = importlib.import_module("taichi_library.taichi_algorithm.common")
common_mod = importlib.reload(common_mod)

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

    def add_gray_scaled_i32(name, kernel, is_vec=True):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.i32), ndim=2)
        else:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
        inv_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "inv_scale", ti.f32)
        builder.dispatch(kernel, src, dst, inv_scale)
        module.add_graph(name, builder.compile())

    add_gray_scaled_i32(
        "rgb2gray_f32_scaled_i32",
        common_mod._rgb_to_gray_f32_scaled_i32_kernel,
        is_vec=True,
    )
    add_gray_scaled_i32(
        "bgr2gray_f32_scaled_i32",
        common_mod._bgr_to_gray_f32_scaled_i32_kernel,
        is_vec=True,
    )
    add_gray_scaled_i32(
        "gray_f32_scaled_i32",
        common_mod._gray_f32_scaled_i32_kernel,
        is_vec=False,
    )

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

    add_hanning_window("hanning")
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

    # 7. Scale Kernels
    def add_scale(name, is_vec=False):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, ti.f32), ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, ti.f32), ndim=2)
            builder.dispatch(common_mod._scale_f32_vec3_kernel, src, dst, ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32))
        else:
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
            builder.dispatch(common_mod._scale_f32_2d_kernel, src, dst, ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32))
        module.add_graph(name, builder.compile())

    add_scale("scale_f32_2d")
    add_scale("scale_vec3_f32", is_vec=True)

    # 8. Tile Stitching Kernels
    def add_stitch(name, is_vec=False):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            tile = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile", ti.types.vector(3, ti.f32), ndim=2)
            accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accum", ti.types.vector(3, ti.f32), ndim=2)
            kernel = common_mod._stitch_tile_vec3_kernel
        else:
            tile = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile", ti.f32, ndim=2)
            accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accum", ti.f32, ndim=2)
            kernel = common_mod._stitch_tile_f32_kernel
        tile_weight = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile_weight", ti.f32, ndim=2)
        hanning = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hanning", ti.f32, ndim=2)
        weight_accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_accum", ti.f32, ndim=2)
        y0 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "y0", ti.i32)
        x0 = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "x0", ti.i32)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        builder.dispatch(kernel, tile, tile_weight, hanning, accum, weight_accum, y0, x0, h, w)
        module.add_graph(name, builder.compile())

    add_stitch("stitch_tile_f32")
    add_stitch("stitch_tile_vec3", is_vec=True)

    def add_stitch_batch(name, is_vec=False):
        builder = ti.graph.GraphBuilder()
        if is_vec:
            tiles = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile", ti.f32, ndim=4)
            accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accum", ti.f32, ndim=3)
            kernel = common_mod._stitch_tile_batch_vec3_kernel
        else:
            tiles = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile", ti.f32, ndim=3)
            accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "accum", ti.f32, ndim=2)
            kernel = common_mod._stitch_tile_batch_f32_kernel
        tile_weight = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "tile_weight", ti.f32, ndim=2)
        hanning = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hanning", ti.f32, ndim=2)
        weight_accum = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_accum", ti.f32, ndim=2)
        y0s = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "y0s", ti.i32, ndim=1)
        x0s = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "x0s", ti.i32, ndim=1)
        n_tiles = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_tiles", ti.i32)
        h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
        w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
        builder.dispatch(
            kernel,
            tiles,
            tile_weight,
            hanning,
            accum,
            weight_accum,
            y0s,
            x0s,
            n_tiles,
            h,
            w,
        )
        module.add_graph(name, builder.compile())

    add_stitch_batch("stitch_tile_batch_f32")
    add_stitch_batch("stitch_tile_batch_vec3", is_vec=True)

    # 9. copyMakeBorder Kernels (Fusing copy_make_border into common.tcm)
    border_mod = importlib.import_module("taichi_library.taichi_algorithm.copy_make_border")
    
    def add_border_2d(dtype_name, dtype):
        # 2D Constant
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype, ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
        top = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "top", ti.i32)
        left = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "left", ti.i32)
        val = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "value", ti.f32)
        builder.dispatch(border_mod._pad_constant_kernel_2d, src, dst, top, left, val)
        module.add_graph(f"pad_constant_2d_{dtype_name}", builder.compile())

        # 2D Others (Reflect101, Reflect, Replicate, Wrap)
        for mode, kernel in [
            ("reflect101", border_mod._pad_reflect101_kernel_2d),
            ("reflect", border_mod._pad_reflect_kernel_2d),
            ("replicate", border_mod._pad_replicate_kernel_2d),
            ("wrap", border_mod._pad_wrap_kernel_2d),
        ]:
            builder = ti.graph.GraphBuilder()
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", dtype, ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", dtype, ndim=2)
            top = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "top", ti.i32)
            left = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "left", ti.i32)
            builder.dispatch(kernel, src, dst, top, left)
            module.add_graph(f"pad_{mode}_2d_{dtype_name}", builder.compile())

    def add_border_3d(dtype_name, dtype):
        # 3D Constant (takes val_r, val_g, val_b)
        builder = ti.graph.GraphBuilder()
        src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
        dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
        top = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "top", ti.i32)
        left = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "left", ti.i32)
        val_r = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "val_r", ti.f32)
        val_g = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "val_g", ti.f32)
        val_b = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "val_b", ti.f32)
        builder.dispatch(border_mod._pad_constant_kernel_3d_vector, src, dst, top, left, val_r, val_g, val_b)
        module.add_graph(f"pad_constant_3d_{dtype_name}", builder.compile())

        # 3D Others
        for mode, kernel in [
            ("reflect101", border_mod._pad_reflect101_kernel_3d_vector),
            ("reflect", border_mod._pad_reflect_kernel_3d_vector),
            ("replicate", border_mod._pad_replicate_kernel_3d_vector),
            ("wrap", border_mod._pad_wrap_kernel_3d_vector),
        ]:
            builder = ti.graph.GraphBuilder()
            src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.types.vector(3, dtype), ndim=2)
            dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.types.vector(3, dtype), ndim=2)
            top = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "top", ti.i32)
            left = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "left", ti.i32)
            builder.dispatch(kernel, src, dst, top, left)
            module.add_graph(f"pad_{mode}_3d_{dtype_name}", builder.compile())

    # Compile for f32, i32 types
    for dtype_name, dtype in [("f32", ti.f32), ("i32", ti.i32)]:
        add_border_2d(dtype_name, dtype)
        add_border_3d(dtype_name, dtype)

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
