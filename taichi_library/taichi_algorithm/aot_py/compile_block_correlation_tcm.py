import os
os.environ["AOT_MODE"] = "0"

import taichi as ti
import sys

file_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(file_dir, "../../../../../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from taichi_library.alignment.alignment_tile.compute_block_correlation import (
    _initialize_flow_pc_kernel,
    _upsample_grid_flow_kernel,
    _extract_blocks_and_window_kernel,
    _batch_complex_mul_kernel,
    _batch_phase_normalize_kernel,
    _batch_complex_to_mag_kernel,
    _peak_detection_and_save_grid_kernel,
    _batch_bit_reverse_kernel,
    _batch_fft_stage_kernel,
    _batch_normalize_kernel,
)

def compile_block_correlation_aot(arch=ti.vulkan, save_path="block_correlation_vulkan.tcm"):
    print(f"\n>>> Compiling Block Phase Correlation AOT for: {arch}")
    ti.init(arch=arch, offline_cache=False)

    module = ti.aot.Module(arch)

    # 1. Initialize Flow PC Graph
    g_init = ti.graph.GraphBuilder()
    grid_flow_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "grid_flow", ti.f32, ndim=3)
    n_tiles_y_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_tiles_y", ti.i32)
    n_tiles_x_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n_tiles_x", ti.i32)
    val_x_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "val_x", ti.f32)
    val_y_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "val_y", ti.f32)
    g_init.dispatch(_initialize_flow_pc_kernel, grid_flow_arg, n_tiles_y_arg, n_tiles_x_arg, val_x_arg, val_y_arg)
    module.add_graph("initialize_flow_pc", g_init.compile())

    # 2. Upsample Grid Flow Graph
    g_up = ti.graph.GraphBuilder()
    src_flow_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst_flow_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    scale_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", ti.f32)
    g_up.dispatch(_upsample_grid_flow_kernel, src_flow_arg, dst_flow_arg, scale_arg)
    module.add_graph("upsample_grid_flow", g_up.compile())

    # 3. Extract Blocks and Window Graph
    g_extract = ti.graph.GraphBuilder()
    ref_layer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_layer", ti.f32, ndim=2)
    comp_layer_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_layer", ti.f32, ndim=2)
    ref_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ref_blocks", ti.math.vec2, ndim=3)
    comp_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "comp_blocks", ti.math.vec2, ndim=3)
    tile_h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_h", ti.i32)
    tile_w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "tile_w", ti.i32)
    block_size_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "block_size", ti.i32)
    step_y_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_y", ti.i32)
    step_x_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "step_x", ti.i32)
    g_extract.dispatch(
        _extract_blocks_and_window_kernel,
        ref_layer_arg, comp_layer_arg, grid_flow_arg,
        ref_blocks_arg, comp_blocks_arg,
        tile_h_arg, tile_w_arg, block_size_arg,
        step_y_arg, step_x_arg
    )
    module.add_graph("extract_blocks_and_window", g_extract.compile())

    # 4. Batch FFT Graph components
    # 4a. Batch Bit Reverse
    g_br = ti.graph.GraphBuilder()
    src_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.math.vec2, ndim=3)
    dst_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.math.vec2, ndim=3)
    bits_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "bits", ti.i32)
    is_col_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_col", ti.i32)
    g_br.dispatch(_batch_bit_reverse_kernel, src_blocks_arg, dst_blocks_arg, bits_arg, is_col_arg)
    module.add_graph("batch_bit_reverse", g_br.compile())

    # 4b. Batch FFT Stage
    g_fs = ti.graph.GraphBuilder()
    data_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "data", ti.math.vec2, ndim=3)
    n_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "n", ti.i32)
    stage_len_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "stage_len", ti.i32)
    is_inverse_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "is_inverse", ti.i32)
    g_fs.dispatch(_batch_fft_stage_kernel, data_blocks_arg, n_arg, stage_len_arg, is_inverse_arg, is_col_arg)
    module.add_graph("batch_fft_stage", g_fs.compile())

    # 4c. Batch Normalize
    g_norm = ti.graph.GraphBuilder()
    g_norm.dispatch(_batch_normalize_kernel, data_blocks_arg, scale_arg)
    module.add_graph("batch_normalize", g_norm.compile())

    # 5. Batch Complex Mul Graph
    g_cmul = ti.graph.GraphBuilder()
    a_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "a", ti.math.vec2, ndim=3)
    b_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "b", ti.math.vec2, ndim=3)
    conj_b_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "conj_b", ti.i32)
    g_cmul.dispatch(_batch_complex_mul_kernel, a_blocks_arg, b_blocks_arg, dst_blocks_arg, conj_b_arg)
    module.add_graph("batch_complex_mul", g_cmul.compile())

    # 6. Batch Phase Normalize Graph
    g_pnorm = ti.graph.GraphBuilder()
    g_pnorm.dispatch(_batch_phase_normalize_kernel, data_blocks_arg)
    module.add_graph("batch_phase_normalize", g_pnorm.compile())

    # 7. Batch Complex to Mag Graph
    g_cmag = ti.graph.GraphBuilder()
    mag_blocks_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    g_cmag.dispatch(_batch_complex_to_mag_kernel, src_blocks_arg, mag_blocks_arg)
    module.add_graph("batch_complex_to_mag", g_cmag.compile())

    # 8. Peak Detection and Save Grid Graph
    g_peak = ti.graph.GraphBuilder()
    g_peak.dispatch(_peak_detection_and_save_grid_kernel, mag_blocks_arg, grid_flow_arg, block_size_arg)
    module.add_graph("peak_detection_and_save_grid", g_peak.compile())

    module.archive(save_path)
    print(f"Successfully compiled Block Phase Correlation and archived to: {save_path}")
    ti.reset()

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(script_dir, "../aot_tcm")
    os.makedirs(assets_dir, exist_ok=True)

    archs = [
        (ti.vulkan, "vulkan"),
        (ti.cuda, "cuda"),
        (ti.cpu, "cpu")
    ]

    for arch, suffix in archs:
        save_path = os.path.abspath(os.path.join(assets_dir, f"block_correlation_{suffix}.tcm"))
        try:
            compile_block_correlation_aot(arch=arch, save_path=save_path)
        except Exception as e:
            print(f"Skipping {suffix} due to error: {e}")
