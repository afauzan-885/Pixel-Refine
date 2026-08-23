"""Small end-to-end grayscale JPEG parity pipeline driven by Taichi kernels."""
from __future__ import annotations

import taichi as ti

from . import kernels
from .jpeg_container import STANDARD_DHT, assemble_grayscale_jfif


def _huffman_maps():
    maps = {}
    pos = 0
    while pos < len(STANDARD_DHT):
        table_id = STANDARD_DHT[pos]
        bits = STANDARD_DHT[pos + 1:pos + 17]
        n = sum(bits)
        values = STANDARD_DHT[pos + 17:pos + 17 + n]
        code, table = 0, {}
        index = 0
        for length, count in enumerate(bits, 1):
            for _ in range(count):
                table[values[index]] = (code, length)
                index += 1
                code += 1
            code <<= 1
        maps[table_id] = table
        pos += 17 + n
    return maps[0], maps[0x10]


def _amplitude_bits(value: int, category: int) -> int:
    return value if value >= 0 else (1 << category) - 1 + value


def _pack_block(dc: int, ac_values: list[tuple[int, int]]) -> list[int]:
    dc_table, ac_table = _huffman_maps()
    previous = 0
    output = []
    bits = []

    def emit(code: int, length: int):
        bits.extend((code >> i) & 1 for i in range(length - 1, -1, -1))

    delta = dc - previous
    category = abs(delta).bit_length()
    code, length = dc_table[category]
    emit(code, length)
    if category:
        emit(_amplitude_bits(delta, category), category)
    for run, value in ac_values:
        if value == 0:
            emit(ac_table[0][0], ac_table[0][1])
            break
        while run >= 16:
            emit(ac_table[0xF0][0], ac_table[0xF0][1]); run -= 16
        category = abs(value).bit_length()
        code, length = ac_table[(run << 4) | category]
        emit(code, length); emit(_amplitude_bits(value, category), category)
    return bits


def encode_grayscale_taichi(image, quality: int = 75) -> bytes:
    """Encode a padded uint8 grayscale image through the Taichi block stages."""
    if image.ndim != 2:
        raise ValueError("image must be a 2D Taichi-compatible grayscale array")
    h = (image.shape[0] + 7) // 8 * 8
    w = (image.shape[1] + 7) // 8 * 8
    # The current orchestration accepts a Taichi-compatible host array. The
    # compression kernels themselves use only Taichi fields and kernels.
    padded = ti.field(ti.f32, shape=(h, w))
    for y in range(h):
        for x in range(w):
            sy = min(y, image.shape[0] - 1)
            sx = min(x, image.shape[1] - 1)
            padded[y, x] = float(image[sy, sx])
    hb, wb = h // 8, w // 8
    ti.init(arch=ti.cpu, offline_cache=False)
    kernels.JPEG_QUALITY_TABLE_FIELD = ti.field(ti.f32, shape=64)
    for index, value in enumerate(kernels.JPEG_QUALITY_TABLE):
        kernels.JPEG_QUALITY_TABLE_FIELD[index] = float(value)
    kernels.JPEG_ZIGZAG_FIELD = ti.field(ti.i32, shape=64)
    for index, value in enumerate(kernels.JPEG_ZIGZAG):
        kernels.JPEG_ZIGZAG_FIELD[index] = int(value)
    blocks = ti.field(ti.f32, shape=(hb, wb, 8, 8))
    ordered = ti.field(ti.f32, shape=(hb, wb, 64))
    kernels.quantize_dct_blocks_kernel(padded, blocks, quality, hb, wb); kernels.zigzag_blocks_kernel(blocks, ordered, hb, wb)
    ti.reset()
    previous = 0
    all_bits = []
    for by in range(hb):
        for bx in range(wb):
            values = [int(round(ordered[by, bx, k])) for k in range(64)]
            dc = values[0] - previous
            previous = values[0]
            ac = []
            run = 0
            for value in values[1:]:
                if value == 0:
                    run += 1
                else:
                    ac.append((run, value))
                    run = 0
            ac.append((0, 0))
            all_bits.extend(_pack_block(dc, ac))
    while len(all_bits) % 8:
        all_bits.append(1)
    stream = bytearray()
    for start in range(0, len(all_bits), 8):
        byte = sum(all_bits[start + i] << (7 - i) for i in range(8))
        stream.append(byte)
        if byte == 0xFF:
            stream.append(0)
    q = tuple(max(1, min(255, (v * (5000 // quality if quality < 50 else 200 - 2 * quality) + 50) // 100)) for v in kernels.JPEG_QUALITY_TABLE)
    return assemble_grayscale_jfif(bytes(stream), image.shape[1], image.shape[0], q)
