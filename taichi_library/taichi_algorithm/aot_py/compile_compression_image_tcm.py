"""Compile pure-Taichi compression preparation graphs to compression_image.tcm."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import taichi as ti

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import taichi_library.taichi_algorithm.compression.kernels as compression_kernels

from taichi_library.taichi_algorithm.compression.kernels import (
    JPEG_QUALITY_TABLE,
    JPEG_CHROMA_TABLE,
    JPEG_QUALITY_TABLE_FIELD,
    JPEG_ZIGZAG,
    quantize_dct_blocks_kernel,
    quantize_dct_chroma_blocks_kernel,
    subsample_422_kernel,
    subsample_420_kernel,
    rgb_to_ycbcr_kernel,
    zigzag_blocks_kernel,
    dc_difference_kernel,
    ac_rle_kernel,
    ac_symbol_kernel,
    category_amplitude_kernel,
    jpeg_symbol_histogram_kernel,
    canonical_huffman_codes_kernel,
    jpeg_pack_block_bits_kernel,
    jpeg_bits_to_bytes_kernel,
)


def compile_compression(arch=ti.cpu, output: str | None = None) -> str:
    output_path = Path(output or Path(__file__).parents[1] / "aot_tcm" / "compression_image.tcm")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ti.init(arch=arch, offline_cache=False)
    compression_kernels.JPEG_QUALITY_TABLE_FIELD = ti.field(dtype=ti.f32, shape=64)
    compression_kernels.JPEG_CHROMA_TABLE_FIELD = ti.field(dtype=ti.f32, shape=64)
    compression_kernels.JPEG_ZIGZAG_FIELD = ti.field(dtype=ti.i32, shape=64)
    JPEG_QUALITY_TABLE_FIELD = compression_kernels.JPEG_QUALITY_TABLE_FIELD
    for index, value in enumerate(JPEG_QUALITY_TABLE):
        JPEG_QUALITY_TABLE_FIELD[index] = float(value)
        compression_kernels.JPEG_CHROMA_TABLE_FIELD[index] = float(JPEG_CHROMA_TABLE[index])
    for index, value in enumerate(JPEG_ZIGZAG):
        compression_kernels.JPEG_ZIGZAG_FIELD[index] = int(value)
    module = ti.aot.Module(arch)

    rgb = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    ycbcr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    h = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h", ti.i32)
    w = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(rgb_to_ycbcr_kernel, rgb, ycbcr, h, w)
    module.add_graph("compression_rgb_to_ycbcr", builder.compile())

    plane = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    blocks = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=4)
    quality = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "quality", ti.i32)
    hb = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_blocks", ti.i32)
    wb = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_blocks", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(quantize_dct_blocks_kernel, plane, blocks, quality, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(quantize_dct_chroma_blocks_kernel, plane, blocks, quality, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize_chroma", builder.compile())

    subsample_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    subsample_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_422_kernel, subsample_src, subsample_dst, h, w)
    module.add_graph("compression_jpeg_subsample_422", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_420_kernel, subsample_src, subsample_dst, h, w)
    module.add_graph("compression_jpeg_subsample_420", builder.compile())

    zigzag = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=4)
    ordered = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(zigzag_blocks_kernel, zigzag, ordered, hb, wb)
    module.add_graph("compression_jpeg_zigzag", builder.compile())

    dc = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zigzag", ti.f32, ndim=3)
    differences = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(dc_difference_kernel, dc, differences, hb, wb)
    module.add_graph("compression_jpeg_dc_difference", builder.compile())

    runs = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "runs", ti.i32, ndim=3)
    values = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "values", ti.f32, ndim=3)
    counts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(ac_rle_kernel, dc, runs, values, counts, hb, wb)
    module.add_graph("compression_jpeg_ac_rle", builder.compile())

    values_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "values", ti.f32, ndim=1)
    categories_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=1)
    amplitudes_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=1)
    count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "count", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(category_amplitude_kernel, values_1d, categories_1d, amplitudes_1d, count)
    module.add_graph("compression_jpeg_category_amplitude", builder.compile())

    symbols = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=3)
    categories = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=3)
    amplitudes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(ac_symbol_kernel, runs, values, symbols, categories, amplitudes, counts, hb, wb)
    module.add_graph("compression_jpeg_ac_symbols", builder.compile())

    ac_counts = counts
    dc_hist = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_histogram", ti.i32, ndim=1)
    ac_hist = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_histogram", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_symbol_histogram_kernel, differences, symbols, ac_counts, dc_hist, ac_hist, hb, wb)
    module.add_graph("compression_jpeg_symbol_histogram", builder.compile())

    lengths = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "lengths", ti.i32, ndim=1)
    codes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "codes", ti.i32, ndim=1)
    symbol_count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "symbol_count", ti.i32)
    max_bits = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_bits", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(canonical_huffman_codes_kernel, lengths, codes, symbol_count, max_bits)
    module.add_graph("compression_jpeg_canonical_codes", builder.compile())

    ac_categories = categories
    ac_amplitudes = amplitudes
    dc_codes_pack = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_codes", ti.i32, ndim=1)
    dc_lengths_pack = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_lengths", ti.i32, ndim=1)
    ac_codes_pack = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_codes", ti.i32, ndim=1)
    ac_lengths_pack = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_lengths", ti.i32, ndim=1)
    bits = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bits", ti.i32, ndim=3)
    bit_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_count", ti.i32, ndim=2)
    max_output_bits = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bits", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_pack_block_bits_kernel, differences, symbols, ac_categories, ac_amplitudes, counts, dc_codes_pack, dc_lengths_pack, ac_codes_pack, ac_lengths_pack, bits, bit_count, hb, wb, max_output_bits)
    module.add_graph("compression_jpeg_pack_bits", builder.compile())

    packed_bits = bits
    packed_bit_count = bit_count
    output_bytes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.i32, ndim=3)
    output_count = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_count", ti.i32, ndim=2)
    max_output_bytes = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bytes", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_bits_to_bytes_kernel, packed_bits, packed_bit_count, output_bytes, output_count, hb, wb, max_output_bytes)
    module.add_graph("compression_jpeg_bits_to_bytes", builder.compile())

    module.archive(str(output_path))
    ti.reset()
    print(f"compiled {output_path}")
    return str(output_path)


if __name__ == "__main__":
    compile_compression()
