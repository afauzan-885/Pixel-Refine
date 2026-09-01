"""Compile pure-Taichi compression preparation graphs to a target artifact."""
import os
import sys
from pathlib import Path

# Compiler workers must load kernel definitions without constructing the
# native AOT bridge first.  The public wrapper uses this project-specific flag
# (AOT_COMPILE_ONLY alone is a legacy suite-level marker) to avoid claiming an
# OpenGL context before Taichi's compiler initializes it.
os.environ.setdefault("PIXEL_REFINE_AOT_COMPILE_ONLY", "1")

import taichi as ti

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import taichi_vision.taichi_algorithm.compression.kernels as compression_kernels

from taichi_vision.taichi_algorithm.compression.kernels import (
    JPEG_QUALITY_TABLE,
    JPEG_CHROMA_TABLE,
    JPEG_QUALITY_TABLE_FIELD,
    JPEG_ZIGZAG,
    quantize_dct_blocks_kernel,
    quantize_dct_chroma_blocks_kernel,
    subsample_422_kernel,
    subsample_420_kernel,
    subsample_chroma_422_pair_kernel,
    subsample_chroma_420_pair_kernel,
    rgb_to_ycbcr_422_pair_kernel,
    rgb_to_ycbcr_420_pair_kernel,
    rgb_to_ycbcr_kernel,
    webp_prepare_argb_kernel,
    webp_histogram_argb_kernel,
    zigzag_blocks_kernel,
    dc_difference_kernel,
    ac_rle_kernel,
    ac_symbol_kernel,
    category_amplitude_kernel,
    jpeg_symbol_histogram_kernel,
    canonical_huffman_codes_kernel,
    jpeg_pack_block_bits_kernel,
    jpeg_pack_block_bytes_flat2d_kernel,
    jpeg_scatter_block_bits_kernel,
    jpeg_bits_to_bytes_kernel,
    jpeg_quantize_dct_zigzag_flat2d_kernel,
    jpeg_prepare_tokens_flat2d_kernel,
    jpeg_fused_transform_tokens_histogram_2d,
    png_filter_rows_kernel,
    dng_delta_rows_kernel,
    dng_undelta_rows_kernel,
    hevc_dc_level_kernel,
    av1_dc_predict_residual_4x4_kernel,
)


@ti.kernel
def _quantize_dct_blocks_flat_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1), basis: ti.types.ndarray(dtype=ti.f32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    """Portable block layout: (block_y, block_x, 64), not a 4D vector ABI."""

    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * basis[k, y * 8 + x]
        q = ti.max(quant_table[k], 1.0)
        dst[by, bx, k] = ti.round(total / q)


@ti.kernel
def _quantize_dct_chroma_blocks_flat_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1), basis: ti.types.ndarray(dtype=ti.f32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * basis[k, y * 8 + x]
        q = ti.max(quant_table[k], 1.0)
        dst[by, bx, k] = ti.round(total / q)


@ti.kernel
def _quantize_dct_blocks_flat2d_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1), basis: ti.types.ndarray(dtype=ti.f32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    """Same DCT adapter with every block stored as a 64-wide 2D row."""

    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * basis[k, y * 8 + x]
        q = ti.max(quant_table[k], 1.0)
        dst[by, bx * 64 + k] = ti.round(total / q)


@ti.kernel
def _quantize_dct_chroma_blocks_flat2d_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1), basis: ti.types.ndarray(dtype=ti.f32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * basis[k, y * 8 + x]
        q = ti.max(quant_table[k], 1.0)
        dst[by, bx * 64 + k] = ti.round(total / q)


@ti.kernel
def _zigzag_blocks_flat_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        dst[by, bx, k] = src[by, bx, compression_kernels.JPEG_ZIGZAG_FIELD[k]]


@ti.kernel
def _zigzag_blocks_flat2d_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), order: ti.types.ndarray(dtype=ti.i32, ndim=1), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        dst[by, bx * 64 + k] = src[by, bx * 64 + order[k]]


@ti.kernel
def _dc_difference_flat2d_kernel(zigzag: ti.types.ndarray(dtype=ti.f32, ndim=2), dc_diff: ti.types.ndarray(dtype=ti.f32, ndim=1), h_blocks: ti.i32, w_blocks: ti.i32):
    for index in range(h_blocks * w_blocks):
        by = index // w_blocks
        bx = index - by * w_blocks
        current = zigzag[by, bx * 64]
        previous = 0.0
        if index > 0:
            previous_by = (index - 1) // w_blocks
            previous_bx = (index - 1) - previous_by * w_blocks
            previous = zigzag[previous_by, previous_bx * 64]
        dc_diff[index] = current - previous


@ti.kernel
def _ac_rle_flat2d_kernel(zigzag: ti.types.ndarray(dtype=ti.f32, ndim=2), runs: ti.types.ndarray(dtype=ti.i32, ndim=2), values: ti.types.ndarray(dtype=ti.f32, ndim=2), token_count: ti.types.ndarray(dtype=ti.i32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        base = bx * 64
        run = 0
        count = 0
        for k in range(1, 64):
            value = zigzag[by, base + k]
            if value == 0:
                run += 1
            else:
                # JPEG represents runs of 16 zero AC coefficients with the
                # ZRL symbol (0xF0); a raw run value of 16+ would overflow
                # the 8-bit Huffman symbol domain.
                for _ in range(4):
                    if run >= 16:
                        runs[by, base + count] = 15
                        values[by, base + count] = 0
                        count += 1
                        run -= 16
                runs[by, base + count] = run
                values[by, base + count] = value
                count += 1
                run = 0
        # Omit EOB when the last non-zero coefficient already occupies AC
        # position 63; otherwise the decoder consumes the EOB as the next
        # block's header.  For trailing zeros (or an all-zero AC block), EOB
        # remains required by the JPEG scan syntax.
        if run > 0 or count == 0:
            runs[by, base + count] = 0
            values[by, base + count] = 0
            count += 1
        token_count[by, bx] = count


@ti.kernel
def _ac_symbol_flat2d_kernel(runs: ti.types.ndarray(dtype=ti.i32, ndim=2), values: ti.types.ndarray(dtype=ti.f32, ndim=2), symbols: ti.types.ndarray(dtype=ti.i32, ndim=2), categories: ti.types.ndarray(dtype=ti.i32, ndim=2), amplitudes: ti.types.ndarray(dtype=ti.i32, ndim=2), token_count: ti.types.ndarray(dtype=ti.i32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        base = bx * 64
        for i in range(64):
            if i < token_count[by, bx]:
                value = ti.cast(values[by, base + i], ti.i32)
                size = compression_kernels.jpeg_category(value)
                run = runs[by, base + i]
                symbols[by, base + i] = ti.select(size == 0, ti.select(run == 0, 0, 0xF0), run * 16 + size)
                categories[by, base + i] = size
                amplitudes[by, base + i] = compression_kernels.jpeg_amplitude(value, size)


@ti.kernel
def _jpeg_symbol_histogram_flat2d_kernel(dc_diff: ti.types.ndarray(dtype=ti.f32, ndim=1), ac_symbols: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_counts: ti.types.ndarray(dtype=ti.i32, ndim=2), dc_histogram: ti.types.ndarray(dtype=ti.i32, ndim=1), ac_histogram: ti.types.ndarray(dtype=ti.i32, ndim=1), h_blocks: ti.i32, w_blocks: ti.i32):
    for index in range(h_blocks * w_blocks):
        category = compression_kernels.jpeg_category(ti.cast(dc_diff[index], ti.i32))
        ti.atomic_add(dc_histogram[category], 1)
        by = index // w_blocks
        bx = index - by * w_blocks
        base = bx * 64
        for i in range(64):
            if i < ac_counts[by, bx]:
                ti.atomic_add(ac_histogram[ac_symbols[by, base + i]], 1)


@ti.kernel
def _jpeg_pack_block_bits_flat2d_kernel(dc_diff: ti.types.ndarray(dtype=ti.f32, ndim=1), ac_symbols: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_categories: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_amplitudes: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_counts: ti.types.ndarray(dtype=ti.i32, ndim=2), dc_codes: ti.types.ndarray(dtype=ti.i32, ndim=1), dc_lengths: ti.types.ndarray(dtype=ti.i32, ndim=1), ac_codes: ti.types.ndarray(dtype=ti.i32, ndim=1), ac_lengths: ti.types.ndarray(dtype=ti.i32, ndim=1), bits: ti.types.ndarray(dtype=ti.i32, ndim=2), bit_count: ti.types.ndarray(dtype=ti.i32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32, max_output_bits: ti.i32):
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        linear = by * w_blocks + bx
        base = bx * max_output_bits
        position = 0
        dc_category = compression_kernels.jpeg_category(ti.cast(dc_diff[linear], ti.i32))
        dc_code = dc_codes[dc_category]
        dc_length = dc_lengths[dc_category]
        dc_amplitude = compression_kernels.jpeg_amplitude(ti.cast(dc_diff[linear], ti.i32), dc_category)
        for bit_index in range(16):
            if bit_index < dc_length and position < max_output_bits:
                shift = dc_length - bit_index - 1
                bits[by, base + position] = (dc_code >> shift) & 1
                position += 1
        for bit_index in range(12):
            if bit_index < dc_category and position < max_output_bits:
                shift = dc_category - bit_index - 1
                bits[by, base + position] = (dc_amplitude >> shift) & 1
                position += 1
        for token in range(64):
            if token < ac_counts[by, bx]:
                symbol = ac_symbols[by, bx * 64 + token]
                length = ac_lengths[symbol]
                code = ac_codes[symbol]
                for bit_index in range(16):
                    if bit_index < length and position < max_output_bits:
                        shift = length - bit_index - 1
                        bits[by, base + position] = (code >> shift) & 1
                        position += 1
                size = ac_categories[by, bx * 64 + token]
                amplitude = ac_amplitudes[by, bx * 64 + token]
                for bit_index in range(12):
                    if bit_index < size and position < max_output_bits:
                        shift = size - bit_index - 1
                        bits[by, base + position] = (amplitude >> shift) & 1
                        position += 1
        bit_count[by, bx] = position


def compile_compression(arch=ti.cpu, output: str | None = None) -> str:
    if output is None:
        target_id = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
        if not target_id:
            backend_name = (
                "cpu" if arch == ti.cpu else
                "vulkan" if arch == ti.vulkan else
                "opengl" if arch == ti.opengl else
                "gles" if arch == ti.gles else
                "cuda"
            )
            defaults = {
                "cpu": "cpu_x86_64_windows" if os.name == "nt" else "cpu_x86_64_linux",
                "vulkan": "vulkan_x86_64_windows" if os.name == "nt" else "vulkan_x86_64_linux",
                "opengl": "opengl_x86_64_windows" if os.name == "nt" else "opengl_x86_64_linux",
                "gles": "gles_arm64_android" if os.name == "nt" else "gles_arm64_linux",
                "cuda": "cuda_x86_64_windows_nvidia" if os.name == "nt" else "cuda_arm64_linux_nvidia",
            }
            target_id = defaults[backend_name]
        # The family compiler is also invoked by the target-suite launcher
        # with only PIXEL_REFINE_TARGET_VARIANT set.  Select the matching
        # Taichi backend before ti.init; writing a Vulkan/OpenGL archive from
        # the default CPU arch would create a target-named but invalid TCM.
        target_backend = target_id.split("_", 1)[0].lower()
        target_arch = {
            "cpu": ti.cpu,
            "vulkan": ti.vulkan,
            "opengl": ti.opengl,
            "gles": ti.gles,
            "cuda": ti.cuda,
        }.get(target_backend)
        if target_arch is not None and arch == ti.cpu and target_backend != "cpu":
            arch = target_arch
        output = Path(__file__).parents[1] / "aot_tcm" / target_id / f"compression_image_{target_id}.tcm"
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ti.init(arch=arch, offline_cache=False)
    actual_arch = ti.lang.impl.current_cfg().arch
    if actual_arch != arch:
        ti.reset()
        raise RuntimeError(f"requested {arch}, but Taichi initialized {actual_arch}; refusing a mislabeled compression TCM")
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

    fused_y = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "y_dst", ti.f32, ndim=2)
    fused_chroma = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "chroma_dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(rgb_to_ycbcr_422_pair_kernel, rgb, fused_y, fused_chroma, h, w)
    module.add_graph("compression_rgb_to_ycbcr_422_pair", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(rgb_to_ycbcr_420_pair_kernel, rgb, fused_y, fused_chroma, h, w)
    module.add_graph("compression_rgb_to_ycbcr_420_pair", builder.compile())

    webp_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    webp_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    webp_channels = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "channels", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(webp_prepare_argb_kernel, webp_src, webp_dst, h, w, webp_channels)
    module.add_graph("compression_webp_prepare_argb", builder.compile())

    webp_hist = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hist", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(webp_histogram_argb_kernel, webp_src, webp_hist, h, w)
    module.add_graph("compression_webp_histogram_argb", builder.compile())

    plane = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    blocks = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    quant_table = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "quant_table", ti.f32, ndim=1)
    basis = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "basis", ti.f32, ndim=2)
    hb = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "h_blocks", ti.i32)
    wb = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "w_blocks", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_quantize_dct_blocks_flat_kernel, plane, blocks, quant_table, basis, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize", builder.compile())

    builder = ti.graph.GraphBuilder()
    builder.dispatch(_quantize_dct_chroma_blocks_flat_kernel, plane, blocks, quant_table, basis, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize_chroma", builder.compile())

    blocks_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_quantize_dct_blocks_flat2d_kernel, plane, blocks_2d, quant_table, basis, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize_2d", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_quantize_dct_chroma_blocks_flat2d_kernel, plane, blocks_2d, quant_table, basis, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize_chroma_2d", builder.compile())

    dct_order_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "order", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_quantize_dct_zigzag_flat2d_kernel, plane, blocks_2d, quant_table, basis, dct_order_2d, hb, wb)
    module.add_graph("compression_jpeg_dct_quantize_zigzag_2d", builder.compile())

    subsample_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    subsample_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_422_kernel, subsample_src, subsample_dst, h, w)
    module.add_graph("compression_jpeg_subsample_422", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_420_kernel, subsample_src, subsample_dst, h, w)
    module.add_graph("compression_jpeg_subsample_420", builder.compile())

    chroma_pair_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    chroma_pair_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_chroma_422_pair_kernel, chroma_pair_src, chroma_pair_dst, h, w)
    module.add_graph("compression_jpeg_subsample_422_pair", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(subsample_chroma_420_pair_kernel, chroma_pair_src, chroma_pair_dst, h, w)
    module.add_graph("compression_jpeg_subsample_420_pair", builder.compile())

    zigzag = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=3)
    ordered = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=3)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_zigzag_blocks_flat_kernel, zigzag, ordered, hb, wb)
    module.add_graph("compression_jpeg_zigzag", builder.compile())

    zigzag_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.f32, ndim=2)
    ordered_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.f32, ndim=2)
    order_1d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "order", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_zigzag_blocks_flat2d_kernel, zigzag_2d, ordered_2d, order_1d, hb, wb)
    module.add_graph("compression_jpeg_zigzag_2d", builder.compile())

    dc_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "zigzag", ti.f32, ndim=2)
    dc_diff_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_dc_difference_flat2d_kernel, dc_2d, dc_diff_2d, hb, wb)
    module.add_graph("compression_jpeg_dc_difference_2d", builder.compile())

    runs_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "runs", ti.i32, ndim=2)
    values_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "values", ti.f32, ndim=2)
    counts_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_ac_rle_flat2d_kernel, dc_2d, runs_2d, values_2d, counts_2d, hb, wb)
    module.add_graph("compression_jpeg_ac_rle_2d", builder.compile())

    symbols_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=2)
    categories_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=2)
    amplitudes_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_ac_symbol_flat2d_kernel, runs_2d, values_2d, symbols_2d, categories_2d, amplitudes_2d, counts_2d, hb, wb)
    module.add_graph("compression_jpeg_ac_symbols_2d", builder.compile())

    token_ordered_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ordered", ti.f32, ndim=2)
    token_dc_diff_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_diff", ti.f32, ndim=1)
    token_symbols_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "symbols", ti.i32, ndim=2)
    token_categories_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "categories", ti.i32, ndim=2)
    token_amplitudes_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "amplitudes", ti.i32, ndim=2)
    token_counts_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "token_count", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_prepare_tokens_flat2d_kernel, token_ordered_2d, token_dc_diff_2d, token_symbols_2d, token_categories_2d, token_amplitudes_2d, token_counts_2d, hb, wb)
    module.add_graph("compression_jpeg_prepare_tokens_2d", builder.compile())

    dc_histogram_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dc_histogram", ti.i32, ndim=1)
    ac_histogram_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_histogram", ti.i32, ndim=1)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_jpeg_symbol_histogram_flat2d_kernel, dc_diff_2d, symbols_2d, counts_2d, dc_histogram_2d, ac_histogram_2d, hb, wb)
    module.add_graph("compression_jpeg_symbol_histogram_2d", builder.compile())

    # Fully fused JPEG pipeline: DCT+quant+zigzag → tokens → histogram
    # This eliminates all intermediate GPU↔CPU round-trips by combining
    # all transform stages into a single GPU dispatch.
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
        jpeg_fused_transform_tokens_histogram_2d,
        fused_src, fused_quant, fused_basis, fused_order,
        fused_dc_values, fused_symbols, fused_categories, fused_amplitudes,
        fused_token_count, fused_dc_histogram, fused_ac_histogram,
        hb, wb,
    )
    module.add_graph("compression_jpeg_fused_transform_tokens_histogram_2d", builder.compile())

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

    png_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    png_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    png_filter_types = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "filter_types", ti.i32, ndim=1)
    png_height = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "height", ti.i32)
    png_row_bytes = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "row_bytes", ti.i32)
    png_bpp = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "bytes_per_pixel", ti.i32)
    png_filter_selector = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "filter_selector", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        png_filter_rows_kernel,
        png_src,
        png_dst,
        png_filter_types,
        png_height,
        png_row_bytes,
        png_bpp,
        png_filter_selector,
    )
    module.add_graph("compression_png_filter_rows", builder.compile())

    dng_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    dng_dst = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "dst", ti.i32, ndim=2)
    dng_height = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "height", ti.i32)
    dng_width = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "width", ti.i32)
    dng_modulus = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "modulus", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(dng_delta_rows_kernel, dng_src, dng_dst, dng_height, dng_width, dng_modulus)
    module.add_graph("compression_dng_delta_rows", builder.compile())
    builder = ti.graph.GraphBuilder()
    builder.dispatch(dng_undelta_rows_kernel, dng_src, dng_dst, dng_height, dng_width, dng_modulus)
    module.add_graph("compression_dng_undelta_rows", builder.compile())

    hevc_residuals = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "residuals", ti.i32, ndim=1)
    hevc_levels = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "levels", ti.i32, ndim=1)
    hevc_count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "count", ti.i32)
    hevc_block_size = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "block_size", ti.i32)
    hevc_level_divisor = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "level_divisor", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        hevc_dc_level_kernel,
        hevc_residuals,
        hevc_levels,
        hevc_count,
        hevc_block_size,
        hevc_level_divisor,
    )
    module.add_graph("compression_hevc_dc_levels", builder.compile())

    av1_src = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "src", ti.i32, ndim=2)
    av1_residual = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "residual", ti.i32, ndim=2)
    av1_reconstructed = ti.graph.Arg(
        ti.graph.ArgKind.NDARRAY, "reconstructed", ti.i32, ndim=2
    )
    av1_height = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "height", ti.i32)
    av1_width = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "width", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        av1_dc_predict_residual_4x4_kernel,
        av1_src,
        av1_residual,
        av1_reconstructed,
        av1_height,
        av1_width,
    )
    module.add_graph("compression_av1_dc_predict_residual_4x4", builder.compile())

    bits_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bits", ti.i32, ndim=2)
    bit_count_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_count", ti.i32, ndim=2)
    pack_ac_symbols_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_symbols", ti.i32, ndim=2)
    pack_ac_categories_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_categories", ti.i32, ndim=2)
    pack_ac_amplitudes_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_amplitudes", ti.i32, ndim=2)
    pack_ac_counts_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "ac_counts", ti.i32, ndim=2)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(_jpeg_pack_block_bits_flat2d_kernel, dc_diff_2d, pack_ac_symbols_2d, pack_ac_categories_2d, pack_ac_amplitudes_2d, pack_ac_counts_2d, dc_codes_pack, dc_lengths_pack, ac_codes_pack, ac_lengths_pack, bits_2d, bit_count_2d, hb, wb, max_output_bits)
    module.add_graph("compression_jpeg_pack_bits_2d", builder.compile())

    raw_output_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output", ti.i32, ndim=2)
    raw_output_count_2d = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_count", ti.i32, ndim=2)
    max_output_bytes_2d = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bytes", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(jpeg_pack_block_bytes_flat2d_kernel, dc_diff_2d, pack_ac_symbols_2d, pack_ac_categories_2d, pack_ac_amplitudes_2d, pack_ac_counts_2d, dc_codes_pack, dc_lengths_pack, ac_codes_pack, ac_lengths_pack, raw_output_2d, raw_output_count_2d, hb, wb, max_output_bytes_2d)
    module.add_graph("compression_jpeg_pack_bytes_2d", builder.compile())

    scatter_block_bytes = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "block_bytes", ti.i32, ndim=2)
    scatter_block_counts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "block_counts", ti.i32, ndim=1)
    scatter_offsets = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "bit_offsets", ti.i32, ndim=1)
    scatter_output_bits = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "output_bits", ti.i32, ndim=1)
    scatter_block_count = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "block_count", ti.i32)
    scatter_max_output_bytes = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "max_output_bytes", ti.i32)
    builder = ti.graph.GraphBuilder()
    builder.dispatch(
        jpeg_scatter_block_bits_kernel,
        scatter_block_bytes,
        scatter_block_counts,
        scatter_offsets,
        scatter_output_bits,
        scatter_block_count,
        scatter_max_output_bytes,
    )
    module.add_graph("compression_jpeg_scatter_block_bits", builder.compile())

    module.archive(str(output_path))
    ti.reset()
    print(f"compiled {output_path}")
    return str(output_path)


def compile_compression_aot(arch=ti.cpu, save_path: str | None = None) -> str:
    """Backend-suite adapter using the standard ``save_path`` convention."""

    return compile_compression(arch=arch, output=save_path)


if __name__ == "__main__":
    compile_compression()
