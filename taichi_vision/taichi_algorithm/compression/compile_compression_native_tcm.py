"""Standalone TCM compiler for the native GPU JPEG pipeline.

This compiler avoids the package-level circular import by loading kernel
modules directly through importlib, making it safe to run in isolation.
"""
import os
import sys
from pathlib import Path
import types
import importlib.util

os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import taichi as ti

# Create package context to avoid circular import
_compression_pkg = types.ModuleType("taichi_vision.taichi_algorithm.compression")
_compression_pkg.__path__ = [str(Path(__file__).resolve().parent)]
sys.modules["taichi_vision.taichi_algorithm.compression"] = _compression_pkg


def _load_submodule(name: str, file_stem: str):
    """Load a submodule from the compression package without triggering
    the full taichi_vision package init chain."""
    module_path = Path(__file__).resolve().parent / f"{file_stem}.py"
    full_name = f"taichi_vision.taichi_algorithm.compression.{file_stem}"
    spec = importlib.util.spec_from_file_location(full_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    setattr(_compression_pkg, file_stem, module)
    return module


# Load dependencies first
_tables = _load_submodule("jpeg_tables", "jpeg_tables")
_kernels = _load_submodule("kernels", "kernels")


def compile_compression_cpu(output: str | None = None) -> str:
    """Compile the compression TCM for CPU backend with the fused kernel."""
    output = output or str(
        PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" /
        "cpu_x86_64_windows" / "compression_image_cpu_x86_64_windows.tcm"
    )
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ti.init(arch=ti.cpu, offline_cache=False)

    # Set up field constants
    _kernels.JPEG_QUALITY_TABLE_FIELD = ti.field(
        dtype=ti.f32, shape=len(_tables.JPEG_QUALITY_TABLE)
    )
    _kernels.JPEG_CHROMA_TABLE_FIELD = ti.field(
        dtype=ti.f32, shape=len(_tables.JPEG_CHROMA_TABLE)
    )
    _kernels.JPEG_ZIGZAG_FIELD = ti.field(
        dtype=ti.i32, shape=len(_tables.JPEG_ZIGZAG)
    )
    for i, v in enumerate(_tables.JPEG_QUALITY_TABLE):
        _kernels.JPEG_QUALITY_TABLE_FIELD[i] = v
    for i, v in enumerate(_tables.JPEG_CHROMA_TABLE):
        _kernels.JPEG_CHROMA_TABLE_FIELD[i] = v
    for i, v in enumerate(_tables.JPEG_ZIGZAG):
        _kernels.JPEG_ZIGZAG_FIELD[i] = v

    hb_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_blocks", ti.i32)
    wb_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_blocks", ti.i32)

    module = ti.aot.Module()

    # ===== Existing graphs (preserved for backward compatibility) =====

    # RGB to YCbCr
    src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.rgb_to_ycbcr_kernel, src, dst, hb_arg, wb_arg)
    module.add_graph("compression_rgb_to_ycbcr", builder.compile())

    # RGB to YCbCr 422 pair (fused)
    y_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "y_dst", ti.f32, ndim=2)
    chroma_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "chroma_dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.rgb_to_ycbcr_422_pair_kernel, src, y_dst, chroma_dst, hb_arg, wb_arg)
    module.add_graph("compression_rgb_to_ycbcr_422_pair", builder.compile())

    # RGB to YCbCr 420 pair (fused)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.rgb_to_ycbcr_420_pair_kernel, src, y_dst, chroma_dst, hb_arg, wb_arg)
    module.add_graph("compression_rgb_to_ycbcr_420_pair", builder.compile())

    # Chroma subsampling
    sub_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    sub_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.subsample_chroma_422_pair_kernel, sub_src, sub_dst, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_subsample_422_pair", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.subsample_chroma_420_pair_kernel, sub_src, sub_dst, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_subsample_420_pair", builder.compile())

    # DCT + quantization + zigzag (fused)
    plane_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    quant_table = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "quant_table", ti.f32, ndim=1)
    basis = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "basis", ti.f32, ndim=2)
    order = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "order", ti.i32, ndim=1)
    quant_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_quantize_dct_zigzag_flat2d_kernel, plane_src, quant_dst, quant_table, basis, order, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_dct_quantize_zigzag_2d", builder.compile())

    # DCT + quantization (separate)
    dct_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels._quantize_dct_blocks_flat2d_kernel, plane_src, dct_dst, quant_table, basis, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_dct_quantize_2d", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels._quantize_dct_chroma_blocks_flat2d_kernel, plane_src, dct_dst, quant_table, basis, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_dct_quantize_chroma_2d", builder.compile())

    # Zigzag
    zig_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    zig_order = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "order", ti.i32, ndim=1)
    zig_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels._zigzag_blocks_flat2d_kernel, zig_src, zig_dst, zig_order, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_zigzag_2d", builder.compile())

    # DC difference
    dc_zigzag = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zigzag", ti.f32, ndim=2)
    dc_diff_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels._dc_difference_flat2d_kernel, dc_zigzag, dc_diff_out, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_dc_difference_2d", builder.compile())

    # AC RLE
    ac_runs = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "runs", ti.i32, ndim=2)
    ac_values = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "values", ti.f32, ndim=2)
    ac_token_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.ac_rle_kernel, dc_zigzag, ac_runs, ac_values, ac_token_count, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_ac_rle_2d", builder.compile())

    # AC symbols
    ac_symbol_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=3)
    ac_cat_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=3)
    ac_amp_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.ac_symbol_kernel, ac_runs, ac_values, ac_symbol_out, ac_cat_out, ac_amp_out, ac_token_count, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_ac_symbols_2d", builder.compile())

    # Prepare tokens (fused: DC diff + AC RLE + symbols)
    tok_ordered = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ordered", ti.f32, ndim=2)
    tok_dc_diff = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    tok_symbols = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=2)
    tok_categories = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=2)
    tok_amplitudes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=2)
    tok_token_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_prepare_tokens_flat2d_kernel, tok_ordered, tok_dc_diff, tok_symbols, tok_categories, tok_amplitudes, tok_token_count, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_prepare_tokens_2d", builder.compile())

    # Symbol histogram
    hist_dc_diff = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    hist_symbols = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=2)
    hist_counts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    hist_dc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_histogram", ti.i32, ndim=1)
    hist_ac = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_histogram", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_symbol_histogram_kernel, hist_dc_diff, hist_symbols, hist_counts, hist_dc, hist_ac, hb_arg, wb_arg)
    module.add_graph("compression_jpeg_symbol_histogram_2d", builder.compile())

    # ===== New fused kernel: DCT+quant+zigzag + tokens + histogram =====
    # This is the key optimization: eliminates all intermediate GPU↔CPU transfers
    # by chaining all transform stages in a single GPU dispatch.
    fused_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    fused_quant = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "quant_table", ti.f32, ndim=1)
    fused_basis = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "basis", ti.f32, ndim=2)
    fused_order = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "order", ti.i32, ndim=1)
    fused_dc_values = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_values", ti.f32, ndim=1)
    fused_symbols = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=2)
    fused_categories = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=2)
    fused_amplitudes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=2)
    fused_token_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    fused_dc_histogram = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_histogram", ti.i32, ndim=1)
    fused_ac_histogram = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_histogram", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        _kernels.jpeg_fused_transform_tokens_histogram_2d,
        fused_src, fused_quant, fused_basis, fused_order,
        fused_dc_values, fused_symbols, fused_categories, fused_amplitudes,
        fused_token_count, fused_dc_histogram, fused_ac_histogram,
        hb_arg, wb_arg,
    )
    module.add_graph("compression_jpeg_fused_transform_tokens_histogram_2d", builder.compile())

    # ===== Bit packing graphs =====
    max_output_bits_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bits", ti.i32)
    max_output_bytes_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bytes", ti.i32)
    pack_dc_diff = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    pack_symbols = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_symbols", ti.i32, ndim=2)
    pack_categories = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_categories", ti.i32, ndim=2)
    pack_amplitudes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_amplitudes", ti.i32, ndim=2)
    pack_counts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_counts", ti.i32, ndim=2)
    dc_codes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_codes", ti.i32, ndim=1)
    dc_lengths = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_lengths", ti.i32, ndim=1)
    ac_codes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_codes", ti.i32, ndim=1)
    ac_lengths = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_lengths", ti.i32, ndim=1)

    pack_bits_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bits", ti.i32, ndim=2)
    pack_bits_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_pack_block_bits_flat2d_kernel, pack_dc_diff, pack_symbols, pack_categories, pack_amplitudes, pack_counts, dc_codes, dc_lengths, ac_codes, ac_lengths, pack_bits_out, pack_bits_count, hb_arg, wb_arg, max_output_bits_arg)
    module.add_graph("compression_jpeg_pack_bits_2d", builder.compile())

    pack_bytes_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.i32, ndim=2)
    pack_bytes_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_pack_block_bytes_flat2d_kernel, pack_dc_diff, pack_symbols, pack_categories, pack_amplitudes, pack_counts, dc_codes, dc_lengths, ac_codes, ac_lengths, pack_bytes_out, pack_bytes_count, hb_arg, wb_arg, max_output_bytes_arg)
    module.add_graph("compression_jpeg_pack_bytes_2d", builder.compile())

    # Scatter block bits
    scatter_block_bytes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "block_bytes", ti.i32, ndim=2)
    scatter_block_counts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "block_counts", ti.i32, ndim=1)
    scatter_offsets = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_offsets", ti.i32, ndim=1)
    scatter_output_bits = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_bits", ti.i32, ndim=1)
    scatter_block_count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "block_count", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_scatter_block_bits_kernel, scatter_block_bytes, scatter_block_counts, scatter_offsets, scatter_output_bits, scatter_block_count, max_output_bytes_arg)
    module.add_graph("compression_jpeg_scatter_block_bits", builder.compile())

    # Bits to bytes
    bits_to_bytes_bits = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bits", ti.i32, ndim=1)
    bits_to_bytes_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_count", ti.i32, ndim=1)
    bits_to_bytes_out = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.i32, ndim=1)
    bits_to_bytes_out_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_count", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_bits_to_bytes_kernel, bits_to_bytes_bits, bits_to_bytes_count, bits_to_bytes_out, bits_to_bytes_out_count, hb_arg, wb_arg, max_output_bytes_arg)
    module.add_graph("compression_jpeg_bits_to_bytes", builder.compile())

    # Pack block bytes flat2d (fused bit pack)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.jpeg_pack_block_bytes_flat2d_kernel, pack_dc_diff, pack_symbols, pack_categories, pack_amplitudes, pack_counts, dc_codes, dc_lengths, ac_codes, ac_lengths, pack_bytes_out, pack_bytes_count, hb_arg, wb_arg, max_output_bytes_arg)
    module.add_graph("compression_jpeg_pack_bytes_flat2d", builder.compile())

    # WebP graphs
    webp_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    webp_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.webp_prepare_argb_kernel, webp_src, webp_dst, hb_arg, wb_arg)
    module.add_graph("compression_webp_prepare_argb", builder.compile())

    webp_hist = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hist", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.webp_histogram_argb_kernel, webp_dst, webp_hist, hb_arg, wb_arg)
    module.add_graph("compression_webp_histogram_argb", builder.compile())

    # PNG filter rows
    png_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    png_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    png_filter_types = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "filter_types", ti.i32, ndim=1)
    png_row_bytes = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "row_bytes", ti.i32)
    png_bpp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "bytes_per_pixel", ti.i32)
    png_filter_selector = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "filter_selector", ti.i32)
    height_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "height", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.png_filter_rows_kernel, png_src, png_dst, png_filter_types, height_arg, png_row_bytes, png_bpp, png_filter_selector)
    module.add_graph("compression_png_filter_rows", builder.compile())

    # DNG delta rows
    dng_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dng_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    dng_height = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "height", ti.i32)
    dng_width = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "width", ti.i32)
    dng_modulus = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "modulus", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.dng_delta_rows_kernel, dng_src, dng_dst, dng_height, dng_width, dng_modulus)
    module.add_graph("compression_dng_delta_rows", builder.compile())

    # DNG undelta rows
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.dng_undelta_rows_kernel, dng_src, dng_dst, dng_height, dng_width, dng_modulus)
    module.add_graph("compression_dng_undelta_rows", builder.compile())

    # HEVC DC level
    hevc_residuals = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "residuals", ti.i32, ndim=1)
    hevc_levels = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "levels", ti.i32, ndim=1)
    hevc_count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "count", ti.i32)
    hevc_block_size = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "block_size", ti.i32)
    hevc_divisor = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "level_divisor", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.hevc_dc_level_kernel, hevc_residuals, hevc_levels, hevc_count, hevc_block_size, hevc_divisor)
    module.add_graph("compression_hevc_dc_levels", builder.compile())

    # AV1 DC predict
    av1_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    av1_residual = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "residual", ti.i32, ndim=2)
    av1_recon = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "reconstructed", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_kernels.av1_dc_predict_residual_4x4_kernel, av1_src, av1_residual, av1_recon, dng_height, dng_width)
    module.add_graph("compression_av1_dc_predict_residual_4x4", builder.compile())

    module.archive(str(output_path))
    ti.reset()
    print(f"Compiled {output_path}")
    return str(output_path)


if __name__ == "__main__":
    compile_compression_cpu()
