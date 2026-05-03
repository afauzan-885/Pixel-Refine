import taichi as ti
import os
import sys
import importlib
import math

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
ncc_mod = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.ncc"
)
fft_mod = importlib.import_module(
    "pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.fft"
)


def compile_ncc_aot(arch=ti.vulkan, save_path="ncc_vulkan.tcm"):
    print(f"\n>>> Compiling NCC AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)
    module = ti.aot.Module(arch)

    vec2_type = ti.types.vector(2, ti.f32)

    # 1. Define Standard Arguments for Graphs
    img_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    temp_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "template", ti.f32, ndim=2)
    dst_f32 = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    data_c = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "data", vec2_type, ndim=2)
    src_c = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", vec2_type, ndim=2)
    dst_c = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", vec2_type, ndim=2)
    row_max_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "row_max", ti.f32, ndim=2)
    peak_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "final_peak", ti.f32, ndim=2)

    # NDArrays for results
    sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_h", ti.f32, ndim=2)
    sq_sum_h = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_h", ti.f32, ndim=2)
    sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sum_2d", ti.f32, ndim=2)
    sq_sum_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sq_sum_2d", ti.f32, ndim=2)
    corr_r = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "corr_r", ti.f32, ndim=2)
    dst_coarse_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_coarse", ti.f32, ndim=2)
    dst_fine_v = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst_fine", ti.f32, ndim=2)

    # Scalars
    h_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    src_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_h", ti.i32)
    src_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "src_w", ti.i32)
    dst_h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_h", ti.i32)
    dst_w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "dst_w", ti.i32)
    bits = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "bits", ti.i32)
    n_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32)
    sl_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stage_len", ti.i32)
    inv_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_inverse", ti.i32)
    col_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_col", ti.i32)
    scale_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    sum_t_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sum_t", ti.f32)
    var_t_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "var_t_n", ti.f32)
    n_f_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_float", ti.f32)
    ht_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_temp", ti.i32)
    wt_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_temp", ti.i32)
    conj_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "conj_b", ti.i32)
    off_y = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_y", ti.i32)
    off_x = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "offset_x", ti.i32)
    stride_v = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stride", ti.i32)

    # 2. Build Graphs
    def add_g(name, kernel, *args):
        gb = ti.graph.GraphBuilder()
        gb.dispatch(kernel, *args)
        module.add_graph(name, gb.compile())

    add_g(
        "real_to_complex", fft_mod._real_to_complex_kernel, img_f32, dst_c, src_h, src_w
    )
    add_g("bit_reverse", fft_mod._bit_reverse_kernel, src_c, dst_c, bits, col_v)
    add_g("fft_stage", fft_mod._fft_stage_kernel, data_c, n_v, sl_v, inv_v, col_v)
    add_g(
        "complex_mul", fft_mod._complex_mul_kernel, src_c, dst_c, data_c, conj_v
    )  # Reuse args
    add_g(
        "complex_to_real", fft_mod._complex_to_real_kernel, src_c, dst_f32, dst_h, dst_w
    )
    add_g("normalize", fft_mod._normalize_kernel, data_c, scale_v)

    add_g(
        "integral_row_scan",
        ncc_mod._integral_image_row_scan_kernel,
        img_f32,
        sum_h,
        sq_sum_h,
        h_v,
        w_v,
    )
    add_g(
        "integral_col_scan",
        ncc_mod._integral_image_col_scan_kernel,
        sum_h,
        sq_sum_h,
        sum_2d,
        sq_sum_2d,
        h_v,
        w_v,
    )
    add_g(
        "assemble_zncc_fft",
        ncc_mod._assemble_zncc_fft_kernel,
        corr_r,
        sum_2d,
        sq_sum_2d,
        dst_f32,
        sum_t_v,
        var_t_v,
        n_f_v,
        ht_v,
        wt_v,
    )

    # 3. Spatial NCC (Legendary Path for small templates)
    add_g(
        "zncc_spatial",
        ncc_mod._zncc_spatial_kernel,
        img_f32,
        temp_f32,
        sum_2d,
        sq_sum_2d,
        dst_f32,
        sum_t_v,
        var_t_v,
        n_f_v,
        off_y,
        off_x,
        stride_v,
    )

    # 4. GPU Reduction (Zero-Transfer Argmax)
    add_g("reduce_row_max", ncc_mod._reduce_row_max_kernel, dst_f32, row_max_v)
    add_g("reduce_global_max", ncc_mod._reduce_global_max_kernel, row_max_v, peak_v)
    
    # 5. Spatial Refine
    add_g("zncc_refine", ncc_mod._zncc_spatial_refine_kernel, img_f32, temp_f32, sum_2d, sq_sum_2d, dst_fine_v, peak_v, sum_t_v, var_t_v, n_f_v, stride_v)

    # 6. ONE BIG GRAPH (The Legendary Path)
    gb = ti.graph.GraphBuilder()
    gb.dispatch(ncc_mod._integral_image_row_scan_kernel, img_f32, sum_h, sq_sum_h, h_v, w_v)
    gb.dispatch(ncc_mod._integral_image_col_scan_kernel, sum_h, sq_sum_h, sum_2d, sq_sum_2d, h_v, w_v)
    gb.dispatch(ncc_mod._zncc_spatial_kernel, img_f32, temp_f32, sum_2d, sq_sum_2d, dst_coarse_v, sum_t_v, var_t_v, n_f_v, off_y, off_x, stride_v)
    gb.dispatch(ncc_mod._reduce_row_max_kernel, dst_coarse_v, row_max_v)
    gb.dispatch(ncc_mod._reduce_global_max_kernel, row_max_v, peak_v)
    gb.dispatch(ncc_mod._zncc_spatial_refine_kernel, img_f32, temp_f32, sum_2d, sq_sum_2d, dst_fine_v, peak_v, sum_t_v, var_t_v, n_f_v, stride_v)
    module.add_graph("zncc_auto", gb.compile())

    module.archive(save_path)
    print(f"Successfully compiled NCC graphs to: {save_path}")
    ti.reset()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)

    archs = [(ti.vulkan, "vulkan"), (ti.cuda, "cuda"), (ti.cpu, "cpu")]
    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"ncc_{suffix}.tcm"))
        try:
            compile_ncc_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix}: {e}")
