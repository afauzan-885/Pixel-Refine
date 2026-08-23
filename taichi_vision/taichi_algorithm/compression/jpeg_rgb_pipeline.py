"""End-to-end baseline RGB JPEG path using Taichi for pixel/block preparation."""
from __future__ import annotations

import taichi as ti

from . import kernels
from .jpeg_container import STANDARD_DHT, assemble_baseline_jfif


def _tables():
    out = {}
    p = 0
    while p < len(STANDARD_DHT):
        ident = STANDARD_DHT[p]
        counts = STANDARD_DHT[p + 1:p + 17]
        values = STANDARD_DHT[p + 17:p + 17 + sum(counts)]
        code = 0
        table = {}
        n = 0
        for length, count in enumerate(counts, 1):
            for _ in range(count):
                table[values[n]] = (code, length)
                code += 1
                n += 1
            code <<= 1
        out[ident] = table
        p += 17 + sum(counts)
    return out[0], out[0x10], out[1], out[0x11]


def _emit(bits, code, length):
    bits.extend((code >> i) & 1 for i in range(length - 1, -1, -1))


def _block_bits(values, previous, dc_table, ac_table):
    bits = []
    delta = values[0] - previous
    category = abs(delta).bit_length()
    _emit(bits, *dc_table[category])
    if category:
        _emit(bits, delta if delta >= 0 else (1 << category) - 1 + delta, category)
    run = 0
    for value in values[1:]:
        if value == 0:
            run += 1
            continue
        while run >= 16:
            _emit(bits, *ac_table[0xF0])
            run -= 16
        size = abs(value).bit_length()
        _emit(bits, *ac_table[(run << 4) | size])
        _emit(bits, value if value >= 0 else (1 << size) - 1 + value, size)
        run = 0
    if run:
        _emit(bits, *ac_table[0])
    return bits, values[0]


def _plane_blocks(plane, quality, chroma=False):
    h = (plane.shape[0] + 7) // 8 * 8
    w = (plane.shape[1] + 7) // 8 * 8
    padded = ti.ndarray(dtype=ti.f32, shape=(h, w))
    for y in range(h):
        for x in range(w):
            padded[y, x] = float(plane[min(y, plane.shape[0] - 1), min(x, plane.shape[1] - 1)])
    hb, wb = h // 8, w // 8
    raw = ti.ndarray(dtype=ti.f32, shape=(hb, wb, 8, 8))
    ordered = ti.ndarray(dtype=ti.f32, shape=(hb, wb, 64))
    if chroma:
        kernels.quantize_dct_chroma_blocks_kernel(padded, raw, quality, hb, wb)
    else:
        kernels.quantize_dct_blocks_kernel(padded, raw, quality, hb, wb)
    kernels.zigzag_blocks_kernel(raw, ordered, hb, wb)
    values = [[[int(round(ordered[by, bx, k])) for k in range(64)] for bx in range(wb)] for by in range(hb)]
    return values


def encode_rgb_taichi(image, quality: int = 75, subsampling: str = "444") -> bytes:
    """Encode an RGB host array as baseline JFIF.

    ``444`` is production-tested here.  ``422`` and ``420`` are rejected until
    MCU interleaving is enabled, preventing silently malformed JPEG streams.
    """
    if not hasattr(image, "shape") or len(image.shape) != 3 or image.shape[2] != 3:
        raise ValueError("image must have shape (height, width, 3)")
    if not 1 <= int(quality) <= 100:
        raise ValueError("quality must be in [1, 100]")
    if subsampling not in ("444", "422", "420"):
        raise ValueError("subsampling must be 444, 422, or 420")
    if subsampling != "444":
        raise NotImplementedError("422/420 MCU interleaving is not enabled yet")
    h, w = image.shape[:2]
    ti.init(arch=ti.cpu, offline_cache=False)
    kernels.JPEG_QUALITY_TABLE_FIELD = ti.field(ti.f32, shape=64)
    kernels.JPEG_CHROMA_TABLE_FIELD = ti.field(ti.f32, shape=64)
    kernels.JPEG_ZIGZAG_FIELD = ti.field(ti.i32, shape=64)
    for i in range(64):
        kernels.JPEG_QUALITY_TABLE_FIELD[i] = kernels.JPEG_QUALITY_TABLE[i]
        kernels.JPEG_CHROMA_TABLE_FIELD[i] = kernels.JPEG_CHROMA_TABLE[i]
        kernels.JPEG_ZIGZAG_FIELD[i] = kernels.JPEG_ZIGZAG[i]
    src = ti.ndarray(dtype=ti.f32, shape=(h, w, 3))
    ycbcr = ti.ndarray(dtype=ti.f32, shape=(h, w, 3))
    for y in range(h):
        for x in range(w):
            for c in range(3):
                src[y, x, c] = float(image[y, x, c])
    kernels.rgb_to_ycbcr_kernel(src, ycbcr, h, w)
    planes = []
    for c in range(3):
        plane = ti.ndarray(dtype=ti.f32, shape=(h, w))
        for y in range(h):
            for x in range(w):
                plane[y, x] = ycbcr[y, x, c]
        planes.append(plane)
    y_blocks = _plane_blocks(planes[0], quality, False)
    cb_blocks = _plane_blocks(planes[1], quality, True)
    cr_blocks = _plane_blocks(planes[2], quality, True)
    ti.reset()
    dc_y, ac_y, dc_c, ac_c = _tables()
    bits = []
    previous = [0, 0, 0]
    for by in range(len(y_blocks)):
        for bx in range(len(y_blocks[0])):
            for component, blocks, dct, act in ((0, y_blocks, dc_y, ac_y), (1, cb_blocks, dc_c, ac_c), (2, cr_blocks, dc_c, ac_c)):
                part, previous[component] = _block_bits(blocks[by][bx], previous[component], dct, act)
                bits.extend(part)
    while len(bits) % 8:
        bits.append(1)
    stream = bytearray()
    for start in range(0, len(bits), 8):
        value = sum(bits[start + i] << (7 - i) for i in range(8))
        stream.append(value)
        if value == 255:
            stream.append(0)
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    luma = tuple(max(1, min(255, (v * scale + 50) // 100)) for v in kernels.JPEG_QUALITY_TABLE)
    chroma = tuple(max(1, min(255, (v * scale + 50) // 100)) for v in kernels.JPEG_CHROMA_TABLE)
    return assemble_baseline_jfif(bytes(stream), w, h, luma, chroma, 0x11)
