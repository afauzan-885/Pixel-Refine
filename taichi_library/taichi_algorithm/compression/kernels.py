"""Pure Taichi JPEG preparation kernels for the compression AOT module."""
import os

import taichi as ti


JPEG_QUALITY_TABLE = (16, 11, 10, 16, 24, 40, 51, 61,
                      12, 12, 14, 19, 26, 58, 60, 55,
                      14, 13, 16, 24, 40, 57, 69, 56,
                      14, 17, 22, 29, 51, 87, 80, 62,
                      18, 22, 37, 56, 68, 109, 103, 77,
                      24, 35, 55, 64, 81, 104, 113, 92,
                      49, 64, 78, 87, 103, 121, 120, 101,
                      72, 92, 95, 98, 112, 100, 103, 99)
JPEG_CHROMA_TABLE = (17, 18, 24, 47, 99, 99, 99, 99,
                     18, 21, 26, 66, 99, 99, 99, 99,
                     24, 26, 56, 99, 99, 99, 99, 99,
                     47, 66, 99, 99, 99, 99, 99, 99,
                     99, 99, 99, 99, 99, 99, 99, 99,
                     99, 99, 99, 99, 99, 99, 99, 99,
                     99, 99, 99, 99, 99, 99, 99, 99,
                     99, 99, 99, 99, 99, 99, 99, 99)
JPEG_QUALITY_TABLE_FIELD = None
JPEG_CHROMA_TABLE_FIELD = None
JPEG_ZIGZAG_FIELD = None

JPEG_ZIGZAG = (0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5,
               12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14,
               21, 28, 35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23,
               30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60,
               61, 54, 47, 55, 62, 63)


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
    previous = 0.0
    for index in range(h_blocks * w_blocks):
        by = index // w_blocks
        bx = index - by * w_blocks
        current = zigzag[by, bx, 0]
        dc_diff[index] = current - previous
        previous = current


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
        # Last token is EOB; a JPEG writer can omit it for a full block.
        runs[by, bx, count] = 0
        values[by, bx, count] = 0
        token_count[by, bx] = count + 1


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


def jpeg_prepare_blocks(src, dst, quality: int):
    """JIT convenience wrapper; AOT callers use the registered graph."""
    h, w = src.shape[:2]
    rgb_to_ycbcr_kernel(src, dst, h, w)
