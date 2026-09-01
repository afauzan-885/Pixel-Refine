"""Pure Taichi JPEG preparation kernels for the compression AOT module."""
import os

import taichi as ti

from .jpeg_tables import JPEG_CHROMA_TABLE, JPEG_QUALITY_TABLE, JPEG_ZIGZAG

JPEG_QUALITY_TABLE_FIELD = None
JPEG_CHROMA_TABLE_FIELD = None
JPEG_ZIGZAG_FIELD = None


@ti.kernel
def rgb_to_ycbcr_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
    """BT.601 RGB uint-range float conversion; output is Y,Cb,Cr in [0,255]."""
    for y, x in ti.ndrange(h, w):
        r = src[y, x, 0]
        g = src[y, x, 1]
        b = src[y, x, 2]
        dst[y, x, 0] = 0.299 * r + 0.587 * g + 0.114 * b
        dst[y, x, 1] = -0.168736 * r - 0.331264 * g + 0.5 * b + 128.0
        dst[y, x, 2] = 0.5 * r - 0.418688 * g - 0.081312 * b + 128.0


@ti.func
def _jpeg_y_value(src: ti.types.ndarray(), y: ti.i32, x: ti.i32) -> ti.f32:
    return 0.299 * src[y, x, 0] + 0.587 * src[y, x, 1] + 0.114 * src[y, x, 2]


@ti.func
def _jpeg_cb_value(src: ti.types.ndarray(), y: ti.i32, x: ti.i32) -> ti.f32:
    return -0.168736 * src[y, x, 0] - 0.331264 * src[y, x, 1] + 0.5 * src[y, x, 2] + 128.0


@ti.func
def _jpeg_cr_value(src: ti.types.ndarray(), y: ti.i32, x: ti.i32) -> ti.f32:
    return 0.5 * src[y, x, 0] - 0.418688 * src[y, x, 1] - 0.081312 * src[y, x, 2] + 128.0


@ti.kernel
def rgb_to_ycbcr_422_pair_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), y_dst: ti.types.ndarray(dtype=ti.f32, ndim=2), chroma_dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32):
    """Convert RGB and average Cb/Cr in one pass for JPEG 4:2:2."""
    for y, x in ti.ndrange(h, w):
        y_dst[y, x] = _jpeg_y_value(src, y, x)
        if x % 2 == 0:
            chroma_dst[y, x // 2, 0] = 0.5 * (_jpeg_cb_value(src, y, x) + _jpeg_cb_value(src, y, x + 1))
            chroma_dst[y, x // 2, 1] = 0.5 * (_jpeg_cr_value(src, y, x) + _jpeg_cr_value(src, y, x + 1))


@ti.kernel
def rgb_to_ycbcr_420_pair_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), y_dst: ti.types.ndarray(dtype=ti.f32, ndim=2), chroma_dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32):
    """Convert RGB and average Cb/Cr in one pass for JPEG 4:2:0."""
    for y, x in ti.ndrange(h, w):
        y_dst[y, x] = _jpeg_y_value(src, y, x)
        if y % 2 == 0 and x % 2 == 0:
            cb_sum = 0.0
            cr_sum = 0.0
            for dy, dx in ti.ndrange(2, 2):
                sample_y = y + dy
                sample_x = x + dx
                cb_sum += _jpeg_cb_value(src, sample_y, sample_x)
                cr_sum += _jpeg_cr_value(src, sample_y, sample_x)
            chroma_dst[y // 2, x // 2, 0] = 0.25 * cb_sum
            chroma_dst[y // 2, x // 2, 1] = 0.25 * cr_sum


@ti.kernel
def subsample_chroma_422_pair_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32):
    """Reduce Cb/Cr together for 4:2:2 and avoid duplicate graph dispatch."""
    for y, x, channel in ti.ndrange(h, w // 2, 2):
        source_channel = channel + 1
        dst[y, x, channel] = 0.5 * (src[y, 2 * x, source_channel] + src[y, 2 * x + 1, source_channel])


@ti.kernel
def subsample_chroma_420_pair_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32):
    """Reduce Cb/Cr together for 4:2:0 and avoid duplicate graph dispatch."""
    for y, x, channel in ti.ndrange(h // 2, w // 2, 2):
        source_channel = channel + 1
        dst[y, x, channel] = 0.25 * (
            src[2 * y, 2 * x, source_channel]
            + src[2 * y, 2 * x + 1, source_channel]
            + src[2 * y + 1, 2 * x, source_channel]
            + src[2 * y + 1, 2 * x + 1, source_channel]
        )


@ti.kernel
def webp_prepare_argb_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), dst: ti.types.ndarray(dtype=ti.f32, ndim=3), h: ti.i32, w: ti.i32, channels: ti.i32):
    """Normalize gray/RGB/RGBA samples to the VP8L ARGB channel order."""
    for y, x in ti.ndrange(h, w):
        red = 0.0
        green = 0.0
        blue = 0.0
        alpha = 255.0
        if channels == 1:
            gray = src[y, x, 0]
            red = gray
            green = gray
            blue = gray
            alpha = 255.0
        elif channels == 2:
            gray = src[y, x, 0]
            red = gray
            green = gray
            blue = gray
            alpha = src[y, x, 1]
        elif channels == 3:
            red = src[y, x, 0]
            green = src[y, x, 1]
            blue = src[y, x, 2]
            alpha = 255.0
        else:
            red = src[y, x, 0]
            green = src[y, x, 1]
            blue = src[y, x, 2]
            alpha = src[y, x, 3]
        dst[y, x, 0] = alpha
        dst[y, x, 1] = red
        dst[y, x, 2] = green
        dst[y, x, 3] = blue


@ti.kernel
def webp_histogram_argb_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=3), hist: ti.types.ndarray(dtype=ti.i32, ndim=2), h: ti.i32, w: ti.i32):
    """Accumulate literal VP8L ARGB channel histograms on the device."""
    for y, x in ti.ndrange(h, w):
        green = ti.cast(src[y, x, 2], ti.i32)
        red = ti.cast(src[y, x, 1], ti.i32)
        blue = ti.cast(src[y, x, 3], ti.i32)
        alpha = ti.cast(src[y, x, 0], ti.i32)
        green = ti.max(0, ti.min(255, green))
        red = ti.max(0, ti.min(255, red))
        blue = ti.max(0, ti.min(255, blue))
        alpha = ti.max(0, ti.min(255, alpha))
        ti.atomic_add(hist[0, green], 1)
        ti.atomic_add(hist[1, red], 1)
        ti.atomic_add(hist[2, blue], 1)
        ti.atomic_add(hist[3, alpha], 1)


@ti.kernel
def av1_dc_predict_residual_4x4_kernel(
    src: ti.types.ndarray(dtype=ti.i32, ndim=2),
    residual: ti.types.ndarray(dtype=ti.i32, ndim=2),
    reconstructed: ti.types.ndarray(dtype=ti.i32, ndim=2),
    height: ti.i32,
    width: ti.i32,
):
    """Build an AV1 lossless DC_PRED residual plane in 4x4 block order.

    This is deliberately a numeric preparation graph, not an AV1 tile
    serializer.  The block size and edge rules match the first native
    lossless intra profile: the prediction uses the reconstructed top and
    left edges, which are equal to ``src`` when the residual is lossless.
    Missing edges use the 8-bit midpoint (128).  Keeping the residual and
    reconstruction outputs together makes the exactness invariant observable
    on every backend without introducing a cross-block write dependency.
    """
    for y, x in ti.ndrange(height, width):
        by = y // 4
        bx = x // 4
        y0 = by * 4
        x0 = bx * 4
        top_count = ti.min(4, width - x0)
        left_count = ti.min(4, height - y0)
        top_sum = 0
        left_sum = 0
        for offset in range(4):
            if by > 0 and offset < top_count:
                top_sum += src[y0 - 1, x0 + offset]
            if bx > 0 and offset < left_count:
                left_sum += src[y0 + offset, x0 - 1]
        ref_count = 0
        ref_sum = 0
        if by > 0:
            ref_count += top_count
            ref_sum += top_sum
        if bx > 0:
            ref_count += left_count
            ref_sum += left_sum
        dc = 128
        if ref_count > 0:
            dc = (ref_sum + ref_count // 2) // ref_count
        delta = src[y, x] - dc
        residual[y, x] = delta
        reconstructed[y, x] = dc + delta


@ti.kernel
def quantize_dct_blocks_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), quality: int, h_blocks: int, w_blocks: int):
    """Forward 8x8 DCT plus baseline JPEG luminance quantization.

    ``src`` is planar Y with shape (H,W); ``dst`` is (block_y,block_x,8,8).
    The entropy coder and JFIF writer are subsequent stages.
    """
    scale = ti.select(quality < 50, 5000 // ti.max(quality, 1), 200 - 2 * quality)
    for by, bx, v, u in ti.ndrange(h_blocks, w_blocks, 8, 8):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * ti.cos((2.0 * x + 1.0) * u * 3.14159265 / 16.0) * ti.cos((2.0 * y + 1.0) * v * 3.14159265 / 16.0)
        cu = ti.select(u == 0, 0.70710678, 1.0)
        cv = ti.select(v == 0, 0.70710678, 1.0)
        q = (JPEG_QUALITY_TABLE_FIELD[v * 8 + u] * scale + 50) // 100
        q = ti.max(q, 1)
        dst[by, bx, v, u] = ti.round(0.25 * cu * cv * total / q)


@ti.kernel
def quantize_dct_chroma_blocks_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), quality: int, h_blocks: int, w_blocks: int):
    """Forward DCT and JPEG chroma quantization for one padded plane."""
    scale = ti.select(quality < 50, 5000 // ti.max(quality, 1), 200 - 2 * quality)
    for by, bx, v, u in ti.ndrange(h_blocks, w_blocks, 8, 8):
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * ti.cos((2.0 * x + 1.0) * u * 3.14159265 / 16.0) * ti.cos((2.0 * y + 1.0) * v * 3.14159265 / 16.0)
        cu = ti.select(u == 0, 0.70710678, 1.0)
        cv = ti.select(v == 0, 0.70710678, 1.0)
        q = (JPEG_CHROMA_TABLE_FIELD[v * 8 + u] * scale + 50) // 100
        q = ti.max(q, 1)
        dst[by, bx, v, u] = ti.round(0.25 * cu * cv * total / q)


@ti.kernel
def jpeg_quantize_dct_zigzag_flat2d_kernel(src: ti.types.ndarray(dtype=ti.f32, ndim=2), dst: ti.types.ndarray(dtype=ti.f32, ndim=2), quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1), basis: ti.types.ndarray(dtype=ti.f32, ndim=2), order: ti.types.ndarray(dtype=ti.i32, ndim=1), h_blocks: ti.i32, w_blocks: ti.i32):
    """Fuse JPEG DCT/quantization and natural-to-zig-zag reordering."""
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        natural = order[k]
        total = 0.0
        for y, x in ti.ndrange(8, 8):
            sample = src[by * 8 + y, bx * 8 + x] - 128.0
            total += sample * basis[natural, y * 8 + x]
        q = ti.max(quant_table[natural], 1.0)
        dst[by, bx * 64 + k] = ti.round(total / q)


@ti.kernel
def subsample_422_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
    for y, x in ti.ndrange(h, w // 2):
        dst[y, x] = 0.5 * (src[y, x * 2] + src[y, x * 2 + 1])


@ti.kernel
def subsample_420_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h: int, w: int):
    for y, x in ti.ndrange(h // 2, w // 2):
        dst[y, x] = 0.25 * (src[y * 2, x * 2] + src[y * 2, x * 2 + 1] + src[y * 2 + 1, x * 2] + src[y * 2 + 1, x * 2 + 1])


@ti.kernel
def zigzag_blocks_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(), h_blocks: int, w_blocks: int):
    """Convert quantized 8x8 blocks to JPEG zig-zag order."""
    for by, bx, k in ti.ndrange(h_blocks, w_blocks, 64):
        linear = JPEG_ZIGZAG_FIELD[k]
        dst[by, bx, k] = src[by, bx, linear // 8, linear - (linear // 8) * 8]


@ti.kernel
def dc_difference_kernel(zigzag: ti.types.ndarray(), dc_diff: ti.types.ndarray(), h_blocks: int, w_blocks: int):
    """Emit sequential DC differences for the luminance scan."""
    for index in range(h_blocks * w_blocks):
        by = index // w_blocks
        bx = index - by * w_blocks
        current = zigzag[by, bx, 0]
        # Do not carry a mutable loop-local predictor: GPU backends may
        # parallelize range loops.  The row-major predecessor is directly
        # addressable, which keeps this graph race-free on CPU and Vulkan.
        previous = 0.0
        if index > 0:
            previous_by = (index - 1) // w_blocks
            previous_bx = (index - 1) - previous_by * w_blocks
            previous = zigzag[previous_by, previous_bx, 0]
        dc_diff[index] = current - previous


@ti.kernel
def ac_rle_kernel(zigzag: ti.types.ndarray(), runs: ti.types.ndarray(), values: ti.types.ndarray(), token_count: ti.types.ndarray(), h_blocks: int, w_blocks: int):
    """Emit fixed-capacity AC run/value tokens; EOB is represented by run=0,value=0."""
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        run = 0
        count = 0
        for k in range(1, 64):
            value = zigzag[by, bx, k]
            if value == 0:
                run += 1
            else:
                for _ in range(4):
                    if run >= 16:
                        runs[by, bx, count] = 15
                        values[by, bx, count] = 0
                        count += 1
                        run -= 16
                runs[by, bx, count] = run
                values[by, bx, count] = value
                count += 1
                run = 0
        # EOB is required when the block ends with zero coefficients.  If the
        # final non-zero coefficient is exactly coefficient 63, the block is
        # already complete and JPEG requires omitting EOB; otherwise its bits
        # would be consumed as the next block's header by a decoder.
        if run > 0 or count == 0:
            runs[by, bx, count] = 0
            values[by, bx, count] = 0
            count += 1
        token_count[by, bx] = count


@ti.func
def jpeg_category(value: ti.i32) -> ti.i32:
    magnitude = ti.abs(value)
    category = 0
    for bit in ti.static(range(12)):
        if magnitude >= (1 << bit):
            category = bit + 1
    return category


@ti.func
def jpeg_amplitude(value: ti.i32, category: ti.i32) -> ti.i32:
    negative = (1 << category) - 1 + value
    return ti.select(value >= 0, value, negative)


@ti.kernel
def category_amplitude_kernel(values: ti.types.ndarray(), categories: ti.types.ndarray(), amplitudes: ti.types.ndarray(), count: int):
    """Convert signed quantized values into JPEG category/amplitude pairs."""
    for i in range(count):
        value = ti.cast(values[i], ti.i32)
        category = jpeg_category(value)
        categories[i] = category
        amplitudes[i] = jpeg_amplitude(value, category)


@ti.kernel
def ac_symbol_kernel(runs: ti.types.ndarray(), values: ti.types.ndarray(), symbols: ti.types.ndarray(), categories: ti.types.ndarray(), amplitudes: ti.types.ndarray(), token_count: ti.types.ndarray(), h_blocks: int, w_blocks: int):
    """Build baseline JPEG AC symbols (RUN<<4 | SIZE) and amplitudes."""
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        for i in range(64):
            if i < token_count[by, bx]:
                value = ti.cast(values[by, bx, i], ti.i32)
                size = jpeg_category(value)
                run = runs[by, bx, i]
                symbols[by, bx, i] = ti.select(size == 0, ti.select(run == 0, 0, 0xF0), run * 16 + size)
                categories[by, bx, i] = size
                amplitudes[by, bx, i] = jpeg_amplitude(value, size)


@ti.kernel
def jpeg_prepare_tokens_flat2d_kernel(ordered: ti.types.ndarray(dtype=ti.f32, ndim=2), dc_diff: ti.types.ndarray(dtype=ti.f32, ndim=1), symbols: ti.types.ndarray(dtype=ti.i32, ndim=2), categories: ti.types.ndarray(dtype=ti.i32, ndim=2), amplitudes: ti.types.ndarray(dtype=ti.i32, ndim=2), token_count: ti.types.ndarray(dtype=ti.i32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32):
    """Fuse DC differences, AC RLE, and AC symbol preparation."""
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        linear = by * w_blocks + bx
        current_dc = ordered[by, bx * 64]
        previous_dc = 0.0
        if bx > 0:
            previous_dc = ordered[by, (bx - 1) * 64]
        elif by > 0:
            previous_dc = ordered[by - 1, (w_blocks - 1) * 64]
        dc_diff[linear] = current_dc - previous_dc

        run = 0
        count = 0
        for k in range(1, 64):
            value = ti.cast(ordered[by, bx * 64 + k], ti.i32)
            if value == 0:
                run += 1
            else:
                for _ in range(4):
                    if run >= 16:
                        symbols[by, bx * 64 + count] = 0xF0
                        categories[by, bx * 64 + count] = 0
                        amplitudes[by, bx * 64 + count] = 0
                        count += 1
                        run -= 16
                size = jpeg_category(value)
                symbols[by, bx * 64 + count] = run * 16 + size
                categories[by, bx * 64 + count] = size
                amplitudes[by, bx * 64 + count] = jpeg_amplitude(value, size)
                count += 1
                run = 0
        if run > 0 or count == 0:
            symbols[by, bx * 64 + count] = 0
            categories[by, bx * 64 + count] = 0
            amplitudes[by, bx * 64 + count] = 0
            count += 1
        token_count[by, bx] = count


@ti.kernel
def jpeg_symbol_histogram_kernel(dc_diff: ti.types.ndarray(), ac_symbols: ti.types.ndarray(), ac_counts: ti.types.ndarray(), dc_histogram: ti.types.ndarray(), ac_histogram: ti.types.ndarray(), h_blocks: int, w_blocks: int):
    """Count JPEG DC categories and AC symbols for optimized Huffman coding."""
    for index in range(h_blocks * w_blocks):
        category = jpeg_category(ti.cast(dc_diff[index], ti.i32))
        ti.atomic_add(dc_histogram[category], 1)
        by = index // w_blocks
        bx = index - by * w_blocks
        for i in range(64):
            if i < ac_counts[by, bx]:
                symbol = ac_symbols[by, bx, i]
                ti.atomic_add(ac_histogram[symbol], 1)


@ti.kernel
def canonical_huffman_codes_kernel(lengths: ti.types.ndarray(), codes: ti.types.ndarray(), symbol_count: int, max_bits: int):
    """Generate canonical Huffman codes from a supplied length table."""
    for symbol in range(symbol_count):
        length = lengths[symbol]
        code = 0
        rank = 0
        for candidate_length in range(1, max_bits + 1):
            if candidate_length <= length:
                count_previous = 0
                rank = 0
                for candidate in range(symbol_count):
                    if lengths[candidate] == candidate_length - 1:
                        count_previous += 1
                    if lengths[candidate] == length and candidate < symbol:
                        rank += 1
                code = (code + count_previous) << 1
        code += rank
        codes[symbol] = code


@ti.kernel
def jpeg_pack_block_bits_kernel(dc_diff: ti.types.ndarray(), ac_symbols: ti.types.ndarray(), ac_categories: ti.types.ndarray(), ac_amplitudes: ti.types.ndarray(), ac_counts: ti.types.ndarray(), dc_codes: ti.types.ndarray(), dc_lengths: ti.types.ndarray(), ac_codes: ti.types.ndarray(), ac_lengths: ti.types.ndarray(), bits: ti.types.ndarray(), bit_count: ti.types.ndarray(), h_blocks: int, w_blocks: int, max_output_bits: int):
    """Pack one luminance JPEG block into a fixed bit buffer, MSB first."""
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        linear = by * w_blocks + bx
        position = 0
        dc_category = jpeg_category(ti.cast(dc_diff[linear], ti.i32))
        dc_code = dc_codes[dc_category]
        dc_length = dc_lengths[dc_category]
        dc_amplitude = jpeg_amplitude(ti.cast(dc_diff[linear], ti.i32), dc_category)
        for bit_index in range(16):
            if bit_index < dc_length and position < max_output_bits:
                shift = dc_length - bit_index - 1
                bits[by, bx, position] = (dc_code >> shift) & 1
                position += 1
        for bit_index in range(12):
            if bit_index < dc_category and position < max_output_bits:
                shift = dc_category - bit_index - 1
                bits[by, bx, position] = (dc_amplitude >> shift) & 1
                position += 1
        for token in range(64):
            if token < ac_counts[by, bx]:
                symbol = ac_symbols[by, bx, token]
                length = ac_lengths[symbol]
                code = ac_codes[symbol]
                for bit_index in range(16):
                    if bit_index < length and position < max_output_bits:
                        shift = length - bit_index - 1
                        bits[by, bx, position] = (code >> shift) & 1
                        position += 1
                size = ac_categories[by, bx, token]
                amplitude = ac_amplitudes[by, bx, token]
                for bit_index in range(12):
                    if bit_index < size and position < max_output_bits:
                        shift = size - bit_index - 1
                        bits[by, bx, position] = (amplitude >> shift) & 1
                        position += 1
        bit_count[by, bx] = position


@ti.kernel
def jpeg_pack_block_bytes_flat2d_kernel(dc_diff: ti.types.ndarray(dtype=ti.f32, ndim=1), ac_symbols: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_categories: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_amplitudes: ti.types.ndarray(dtype=ti.i32, ndim=2), ac_counts: ti.types.ndarray(dtype=ti.i32, ndim=2), dc_codes: ti.types.ndarray(dtype=ti.i32, ndim=1), dc_lengths: ti.types.ndarray(dtype=ti.i32, ndim=1), ac_codes: ti.types.ndarray(dtype=ti.i32, ndim=1), ac_lengths: ti.types.ndarray(dtype=ti.i32, ndim=1), output: ti.types.ndarray(dtype=ti.i32, ndim=2), output_count: ti.types.ndarray(dtype=ti.i32, ndim=2), h_blocks: ti.i32, w_blocks: ti.i32, max_output_bytes: ti.i32):
    """Pack JPEG block tokens directly to raw bytes.

    The legacy path materialized one i32 value for every bit and then ran a
    second host-side ``packbits`` pass.  This kernel keeps the same MSB-first
    semantics but emits one i32 byte at a time.  The bytes are deliberately
    *not* 0xFF-stuffed: block boundaries are not byte aligned, so stuffing is
    performed once after the complete scan has been assembled.
    """
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        linear = by * w_blocks + bx
        base = bx * max_output_bytes
        accumulator = 0
        accumulator_bits = 0
        byte_count = 0
        position = 0

        dc_category = jpeg_category(ti.cast(dc_diff[linear], ti.i32))
        dc_code = dc_codes[dc_category]
        dc_length = dc_lengths[dc_category]
        dc_amplitude = jpeg_amplitude(ti.cast(dc_diff[linear], ti.i32), dc_category)
        for bit_index in range(16):
            if bit_index < dc_length:
                shift = dc_length - bit_index - 1
                accumulator = (accumulator << 1) | ((dc_code >> shift) & 1)
                accumulator_bits += 1
                position += 1
                if accumulator_bits == 8:
                    if byte_count < max_output_bytes:
                        output[by, base + byte_count] = accumulator
                    byte_count += 1
                    accumulator = 0
                    accumulator_bits = 0
        for bit_index in range(12):
            if bit_index < dc_category:
                shift = dc_category - bit_index - 1
                accumulator = (accumulator << 1) | ((dc_amplitude >> shift) & 1)
                accumulator_bits += 1
                position += 1
                if accumulator_bits == 8:
                    if byte_count < max_output_bytes:
                        output[by, base + byte_count] = accumulator
                    byte_count += 1
                    accumulator = 0
                    accumulator_bits = 0

        for token in range(64):
            if token < ac_counts[by, bx]:
                symbol = ac_symbols[by, bx * 64 + token]
                length = ac_lengths[symbol]
                code = ac_codes[symbol]
                for bit_index in range(16):
                    if bit_index < length:
                        shift = length - bit_index - 1
                        accumulator = (accumulator << 1) | ((code >> shift) & 1)
                        accumulator_bits += 1
                        position += 1
                        if accumulator_bits == 8:
                            if byte_count < max_output_bytes:
                                output[by, base + byte_count] = accumulator
                            byte_count += 1
                            accumulator = 0
                            accumulator_bits = 0
                size = ac_categories[by, bx * 64 + token]
                amplitude = ac_amplitudes[by, bx * 64 + token]
                for bit_index in range(12):
                    if bit_index < size:
                        shift = size - bit_index - 1
                        accumulator = (accumulator << 1) | ((amplitude >> shift) & 1)
                        accumulator_bits += 1
                        position += 1
                        if accumulator_bits == 8:
                            if byte_count < max_output_bytes:
                                output[by, base + byte_count] = accumulator
                            byte_count += 1
                            accumulator = 0
                            accumulator_bits = 0
        if accumulator_bits > 0:
            if byte_count < max_output_bytes:
                output[by, base + byte_count] = accumulator << (8 - accumulator_bits)
            byte_count += 1
        output_count[by, bx] = position


@ti.kernel
def jpeg_scatter_block_bits_kernel(
    block_bytes: ti.types.ndarray(dtype=ti.i32, ndim=2),
    block_counts: ti.types.ndarray(dtype=ti.i32, ndim=1),
    bit_offsets: ti.types.ndarray(dtype=ti.i32, ndim=1),
    output_bits: ti.types.ndarray(dtype=ti.i32, ndim=1),
    block_count: ti.i32,
    max_output_bytes: ti.i32,
):
    """Scatter independently packed JPEG blocks into one scan bitstream.

    ``block_counts`` excludes the byte padding emitted in each temporary block
    buffer.  Prefix offsets therefore make every destination bit unique, so
    the kernel is safe to execute in parallel on CPU, Vulkan, or CUDA without
    atomics.  The host only performs the compact prefix sum and final
    byte-packing; it no longer concatenates one variable-length block at a
    time in Python.
    """
    for block, bit_index in ti.ndrange(block_count, max_output_bytes * 8):
        count = block_counts[block]
        if bit_index < count:
            source_byte = block_bytes[block, bit_index // 8]
            source_bit = (source_byte >> (7 - (bit_index % 8))) & 1
            output_bits[bit_offsets[block] + bit_index] = source_bit


@ti.kernel
def jpeg_bits_to_bytes_kernel(bits: ti.types.ndarray(), bit_count: ti.types.ndarray(), output: ti.types.ndarray(), output_count: ti.types.ndarray(), h_blocks: int, w_blocks: int, max_output_bytes: int):
    """Pack MSB-first bits and insert JPEG 0x00 after each emitted 0xFF."""
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        count = bit_count[by, bx]
        byte_count = 0
        accumulator = 0
        accumulator_bits = 0
        for bit_index in range(4096):
            if bit_index < count:
                accumulator = (accumulator << 1) | bits[by, bx, bit_index]
                accumulator_bits += 1
                if accumulator_bits == 8:
                    if byte_count < max_output_bytes:
                        output[by, bx, byte_count] = accumulator
                        byte_count += 1
                        if accumulator == 255 and byte_count < max_output_bytes:
                            output[by, bx, byte_count] = 0
                            byte_count += 1
                    accumulator = 0
                    accumulator_bits = 0
        if accumulator_bits > 0 and byte_count < max_output_bytes:
            output[by, bx, byte_count] = accumulator << (8 - accumulator_bits)
            byte_count += 1
        output_count[by, bx] = byte_count


@ti.kernel
def png_filter_rows_kernel(
    src: ti.types.ndarray(dtype=ti.i32, ndim=2),
    dst: ti.types.ndarray(dtype=ti.i32, ndim=2),
    filter_types: ti.types.ndarray(dtype=ti.i32, ndim=1),
    height: ti.i32,
    row_bytes: ti.i32,
    bytes_per_pixel: ti.i32,
    filter_selector: ti.i32,
):
    """Apply adaptive or forced PNG row filtering in one TCM graph.

    ``filter_selector`` is ``-1`` for the lowest-cost adaptive choice and
    ``0..4`` for None, Sub, Up, Average, or Paeth respectively.  Runtime
    callers validate the scalar before dispatch, so every row always has at
    least one eligible candidate.
    """
    for y in range(height):
        best_filter = 0
        best_cost = 2147483647
        for candidate in range(5):
            if filter_selector < 0 or candidate == filter_selector:
                cost = 0
                for x in range(row_bytes):
                    raw = src[y, x]
                    left = 0
                    above = 0
                    upper_left = 0
                    if x >= bytes_per_pixel:
                        left = src[y, x - bytes_per_pixel]
                    if y > 0:
                        above = src[y - 1, x]
                        if x >= bytes_per_pixel:
                            upper_left = src[y - 1, x - bytes_per_pixel]
                    estimate = left + above - upper_left
                    average = (left + above) // 2
                    paeth = left
                    if abs(estimate - above) < abs(estimate - left):
                        paeth = above
                    if abs(estimate - upper_left) < abs(estimate - paeth):
                        paeth = upper_left
                    predictor = ti.select(candidate == 0, 0, ti.select(candidate == 1, left, ti.select(candidate == 2, above, ti.select(candidate == 3, average, paeth))))
                    residual = (raw - predictor) & 255
                    cost += ti.min(residual, 256 - residual)
                if cost < best_cost:
                    best_cost = cost
                    best_filter = candidate
        filter_types[y] = best_filter
        for x in range(row_bytes):
            raw = src[y, x]
            left = 0
            above = 0
            upper_left = 0
            if x >= bytes_per_pixel:
                left = src[y, x - bytes_per_pixel]
            if y > 0:
                above = src[y - 1, x]
                if x >= bytes_per_pixel:
                    upper_left = src[y - 1, x - bytes_per_pixel]
            estimate = left + above - upper_left
            average = (left + above) // 2
            paeth = left
            if abs(estimate - above) < abs(estimate - left):
                paeth = above
            if abs(estimate - upper_left) < abs(estimate - paeth):
                paeth = upper_left
            predictor = ti.select(best_filter == 0, 0, ti.select(best_filter == 1, left, ti.select(best_filter == 2, above, ti.select(best_filter == 3, average, paeth))))
            dst[y, x] = (raw - predictor) & 255


@ti.kernel
def dng_delta_rows_kernel(src: ti.types.ndarray(dtype=ti.i32, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2), height: ti.i32, width: ti.i32, modulus: ti.i32):
    """TIFF Predictor=2 horizontal differencing on integer CFA samples."""
    for y, x in ti.ndrange(height, width):
        previous = 0
        if x > 0:
            previous = src[y, x - 1]
        dst[y, x] = (src[y, x] - previous) % modulus


@ti.kernel
def dng_undelta_rows_kernel(src: ti.types.ndarray(dtype=ti.i32, ndim=2), dst: ti.types.ndarray(dtype=ti.i32, ndim=2), height: ti.i32, width: ti.i32, modulus: ti.i32):
    """Inverse TIFF Predictor=2 horizontal differencing."""
    for y in range(height):
        running = 0
        for x in range(width):
            running = (running + src[y, x]) % modulus
            dst[y, x] = running


@ti.kernel
def hevc_dc_level_kernel(
    residuals: ti.types.ndarray(dtype=ti.i32, ndim=1),
    levels: ti.types.ndarray(dtype=ti.i32, ndim=1),
    count: ti.i32,
    block_size: ti.i32,
    level_divisor: ti.i32,
):
    """Map bounded HEVC QP-0 DC residuals to transform levels.

    The integer rule is shared by the validated 8-bit and Main10 DC-intra
    profiles.  ``level_divisor=1`` is the 8-bit path; Main10 uses the
    separately-qualified divisor four.  CABAC serialization remains a
    bounded host-side stage until the full residual graph is migrated.
    """
    denominator = 5 * ti.max(level_divisor, 1)
    numerator_scale = block_size * 8
    for index in range(count):
        numerator = residuals[index] * numerator_scale
        if numerator >= 0:
            levels[index] = (numerator + denominator // 2) // denominator
        else:
            levels[index] = -((-numerator + denominator // 2) // denominator)


@ti.kernel
def jpeg_fused_transform_tokens_histogram_2d(
    src: ti.types.ndarray(dtype=ti.f32, ndim=2),
    quant_table: ti.types.ndarray(dtype=ti.f32, ndim=1),
    basis: ti.types.ndarray(dtype=ti.f32, ndim=2),
    order: ti.types.ndarray(dtype=ti.i32, ndim=1),
    dc_values: ti.types.ndarray(dtype=ti.f32, ndim=1),
    symbols: ti.types.ndarray(dtype=ti.i32, ndim=2),
    categories: ti.types.ndarray(dtype=ti.i32, ndim=2),
    amplitudes: ti.types.ndarray(dtype=ti.i32, ndim=2),
    token_count: ti.types.ndarray(dtype=ti.i32, ndim=2),
    dc_histogram: ti.types.ndarray(dtype=ti.i32, ndim=1),
    ac_histogram: ti.types.ndarray(dtype=ti.i32, ndim=1),
    h_blocks: ti.i32,
    w_blocks: ti.i32,
):
    """Fully fused JPEG pipeline: DCT+quant+zigzag → tokens → histogram.

    This kernel combines all JPEG transform stages into a single GPU dispatch,
    eliminating intermediate GPU↔CPU round-trips.  Each block processes:
    1. Forward 8×8 DCT with quantization and zigzag reordering
    2. Store DC value for host-side differential coding
    3. AC run-length encoding with symbol generation
    4. Histogram accumulation for Huffman coding

    The outputs are ready for host-side DC differential coding, Huffman tree
    construction, and bitstream assembly.  DC differential coding is done on
    host because it requires sequential processing (each block's DC depends
    on the previous block's DC).
    """
    for by, bx in ti.ndrange(h_blocks, w_blocks):
        # Stage 1: DCT + quantization + zigzag (fused)
        # Store zigzag-ordered coefficients in a local array
        zigzag_block = ti.Vector([0.0] * 64, ti.f32)
        for k in range(64):
            natural = order[k]
            total = 0.0
            for y, x in ti.ndrange(8, 8):
                sample = src[by * 8 + y, bx * 8 + x] - 128.0
                total += sample * basis[natural, y * 8 + x]
            q = ti.max(quant_table[natural], 1.0)
            zigzag_block[k] = ti.round(total / q)

        # Stage 2: Store DC value for host-side differential coding
        linear = by * w_blocks + bx
        dc_values[linear] = zigzag_block[0]

        # Stage 3: AC RLE + symbol generation
        run = 0
        count = 0
        for k in range(1, 64):
            value = ti.cast(zigzag_block[k], ti.i32)
            if value == 0:
                run += 1
            else:
                # Handle ZRL (zero run length >= 16)
                for _ in range(4):
                    if run >= 16:
                        symbols[by, bx * 64 + count] = 0xF0
                        categories[by, bx * 64 + count] = 0
                        amplitudes[by, bx * 64 + count] = 0
                        count += 1
                        run -= 16
                # Emit AC coefficient
                size = jpeg_category(value)
                symbols[by, bx * 64 + count] = run * 16 + size
                categories[by, bx * 64 + count] = size
                amplitudes[by, bx * 64 + count] = jpeg_amplitude(value, size)
                count += 1
                run = 0
        # EOB (End of Block)
        if run > 0 or count == 0:
            symbols[by, bx * 64 + count] = 0
            categories[by, bx * 64 + count] = 0
            amplitudes[by, bx * 64 + count] = 0
            count += 1
        token_count[by, bx] = count

        # Stage 4: Histogram accumulation (AC only, DC histogram done on host)
        for i in range(64):
            if i < count:
                symbol = symbols[by, bx * 64 + i]
                ti.atomic_add(ac_histogram[symbol], 1)


def jpeg_prepare_blocks(src, dst, quality: int):
    """JIT convenience wrapper; AOT callers use the registered graph."""
    h, w = src.shape[:2]
    rgb_to_ycbcr_kernel(src, dst, h, w)
