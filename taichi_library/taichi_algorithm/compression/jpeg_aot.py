"""End-to-end baseline JPEG encoders backed by the compression TCM module.

Pixel/color conversion, DCT quantization, zig-zag, run-length, symbol, and
bit-packing stages are dispatched to AOT graphs.  Variable-length MCU ordering
and JFIF marker assembly remain host-side because their sizes are data
dependent and the container is a byte stream.
"""

from __future__ import annotations

import numpy as np

from taichi_library.taichi_algorithm.compression.kernels import JPEG_CHROMA_TABLE, JPEG_QUALITY_TABLE, JPEG_ZIGZAG
from taichi_library.taichi_algorithm.compression.jpeg_container import STANDARD_DHT, assemble_baseline_jfif, assemble_grayscale_jfif

from taichi_library.taichi_algorithm.aot_api.research import _as_f32, _dispatch


def _build_dct_basis():
    basis = np.empty((64, 64), dtype=np.float32)
    for v in range(8):
        for u in range(8):
            coefficient = v * 8 + u
            cv = 1.0 / np.sqrt(2.0) if v == 0 else 1.0
            cu = 1.0 / np.sqrt(2.0) if u == 0 else 1.0
            for y in range(8):
                for x in range(8):
                    basis[coefficient, y * 8 + x] = 0.25 * cu * cv * np.cos((2 * x + 1) * u * np.pi / 16.0) * np.cos((2 * y + 1) * v * np.pi / 16.0)
    return basis


_DCT_BASIS = _build_dct_basis()
_JPEG_ZIGZAG = np.asarray(JPEG_ZIGZAG, dtype=np.int32)


def _huffman_tables():
    tables = {}
    position = 0
    while position < len(STANDARD_DHT):
        table_id = STANDARD_DHT[position]
        counts = STANDARD_DHT[position + 1:position + 17]
        values = STANDARD_DHT[position + 17:position + 17 + sum(counts)]
        code, table = 0, {}
        cursor = 0
        for length, count in enumerate(counts, 1):
            for _ in range(count):
                table[values[cursor]] = (code, length)
                cursor += 1
                code += 1
            code <<= 1
        tables[table_id] = table
        position += 17 + sum(counts)
    return tables[0], tables[0x10], tables[1], tables[0x11]


def _code_arrays(table, size):
    codes = np.zeros(size, dtype=np.int32)
    lengths = np.zeros(size, dtype=np.int32)
    for symbol, (code, length) in table.items():
        if symbol < size:
            codes[symbol] = code
            lengths[symbol] = length
    return codes, lengths


def _pad_plane(plane, height, width):
    return np.pad(plane, ((0, height - plane.shape[0]), (0, width - plane.shape[1])), mode="edge").astype(np.float32, copy=False)


def _quantize_plane(plane, quality, chroma=False):
    h, w = plane.shape
    hb, wb = h // 8, w // 8
    graph = "compression_jpeg_dct_quantize_chroma_2d" if chroma else "compression_jpeg_dct_quantize_2d"
    base_table = JPEG_CHROMA_TABLE if chroma else JPEG_QUALITY_TABLE
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    quant_table = np.asarray([max(1, min(255, (value * scale + 50) // 100)) for value in base_table], dtype=np.float32)
    raw = _dispatch(
        "compression_image",
        graph,
        inputs={"src": np.ascontiguousarray(plane), "quant_table": quant_table, "basis": _DCT_BASIS},
        outputs={"dst": ((hb, wb * 64), np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    return _dispatch(
        "compression_image",
        "compression_jpeg_zigzag_2d",
        inputs={"src": raw, "order": _JPEG_ZIGZAG},
        outputs={"dst": ((hb, wb * 64), np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )


def _pack_plane_bits(ordered, dc_table, ac_table):
    hb, wb = ordered.shape[0], ordered.shape[1] // 64
    dc_diff = _dispatch(
        "compression_image",
        "compression_jpeg_dc_difference_2d",
        inputs={"zigzag": ordered},
        outputs={"dc_diff": np.zeros(hb * wb, dtype=np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    runs = np.zeros((hb, wb * 64), dtype=np.int32)
    values = np.zeros((hb, wb * 64), dtype=np.float32)
    token_count = np.zeros((hb, wb), dtype=np.int32)
    rle = _dispatch(
        "compression_image",
        "compression_jpeg_ac_rle_2d",
        inputs={"zigzag": ordered},
        outputs={"runs": runs, "values": values, "token_count": token_count},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    symbols = np.zeros((hb, wb * 64), dtype=np.int32)
    categories = np.zeros((hb, wb * 64), dtype=np.int32)
    amplitudes = np.zeros((hb, wb * 64), dtype=np.int32)
    symbol_data = _dispatch(
        "compression_image",
        "compression_jpeg_ac_symbols_2d",
        inputs={"runs": rle["runs"], "values": rle["values"], "token_count": rle["token_count"]},
        outputs={"symbols": symbols, "categories": categories, "amplitudes": amplitudes},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    dc_codes, dc_lengths = _code_arrays(dc_table, 16)
    ac_codes, ac_lengths = _code_arrays(ac_table, 256)
    packed = _dispatch(
        "compression_image",
        "compression_jpeg_pack_bits_2d",
        inputs={
            "dc_diff": dc_diff,
            "ac_symbols": symbol_data["symbols"],
            "ac_categories": symbol_data["categories"],
            "ac_amplitudes": symbol_data["amplitudes"],
            "ac_counts": rle["token_count"],
            "dc_codes": dc_codes,
            "dc_lengths": dc_lengths,
            "ac_codes": ac_codes,
            "ac_lengths": ac_lengths,
        },
        outputs={"bits": np.zeros((hb, wb * 4096), dtype=np.int32), "bit_count": np.zeros((hb, wb), dtype=np.int32)},
        scalars={"h_blocks": hb, "w_blocks": wb, "max_output_bits": 4096},
        plain_ndarray=False,
    )
    return [[packed["bits"][by, bx * 4096: bx * 4096 + int(packed["bit_count"][by, bx])].tolist() for bx in range(wb)] for by in range(hb)]


def _append_bits(target, block_bits):
    for block in block_bits:
        target.extend(int(value) & 1 for value in block)


def _bits_to_scan(bits):
    while len(bits) % 8:
        bits.append(1)
    stream = bytearray()
    for start in range(0, len(bits), 8):
        value = sum(bits[start + offset] << (7 - offset) for offset in range(8))
        stream.append(value)
        if value == 0xFF:
            stream.append(0)
    return bytes(stream)


def _quality_tables(quality):
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    luma = tuple(max(1, min(255, (value * scale + 50) // 100)) for value in JPEG_QUALITY_TABLE)
    chroma = tuple(max(1, min(255, (value * scale + 50) // 100)) for value in JPEG_CHROMA_TABLE)
    return luma, chroma


def _normalize_rgb(image):
    data = np.asarray(image)
    if data.ndim != 3 or data.shape[2] != 3:
        raise ValueError("RGB JPEG input must have shape (height, width, 3)")
    result = data.astype(np.float32)
    if np.issubdtype(data.dtype, np.floating) and float(np.max(result, initial=0.0)) <= 1.0:
        result *= 255.0
    return np.ascontiguousarray(result)


def encode_grayscale_aot(image, quality=75):
    data = np.asarray(image)
    if data.ndim != 2:
        raise ValueError("grayscale JPEG input must be 2D")
    quality = int(quality)
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")
    source = data.astype(np.float32)
    if np.issubdtype(data.dtype, np.floating) and float(np.max(source, initial=0.0)) <= 1.0:
        source *= 255.0
    height, width = source.shape
    padded = _pad_plane(source, (height + 7) // 8 * 8, (width + 7) // 8 * 8)
    dc_luma, ac_luma, _, _ = _huffman_tables()
    bits = _pack_plane_bits(_quantize_plane(padded, quality), dc_luma, ac_luma)
    flat = []
    _append_bits(flat, [block for row in bits for block in row])
    luma, _ = _quality_tables(quality)
    return assemble_grayscale_jfif(_bits_to_scan(flat), width, height, luma)


def encode_rgb_aot(image, quality=75, subsampling="444"):
    data = _normalize_rgb(image)
    quality = int(quality)
    subsampling = str(subsampling)
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")
    if subsampling not in {"444", "422", "420"}:
        raise ValueError("subsampling must be 444, 422, or 420")
    height, width = data.shape[:2]
    block_height = 16 if subsampling == "420" else 8
    block_width = 16 if subsampling in {"422", "420"} else 8
    padded_height = (height + block_height - 1) // block_height * block_height
    padded_width = (width + block_width - 1) // block_width * block_width
    padded_rgb = np.pad(data, ((0, padded_height - height), (0, padded_width - width), (0, 0)), mode="edge").astype(np.float32)
    ycbcr = _dispatch(
        "compression_image",
        "compression_rgb_to_ycbcr",
        inputs={"src": padded_rgb},
        outputs={"dst": np.empty_like(padded_rgb)},
        scalars={"h": padded_height, "w": padded_width},
    )
    y_plane = ycbcr[..., 0]
    cb_plane = ycbcr[..., 1]
    cr_plane = ycbcr[..., 2]
    if subsampling == "422":
        cb_plane = _dispatch("compression_image", "compression_jpeg_subsample_422", inputs={"src": cb_plane}, outputs={"dst": np.empty((padded_height, padded_width // 2), np.float32)}, scalars={"h": padded_height, "w": padded_width})
        cr_plane = _dispatch("compression_image", "compression_jpeg_subsample_422", inputs={"src": cr_plane}, outputs={"dst": np.empty((padded_height, padded_width // 2), np.float32)}, scalars={"h": padded_height, "w": padded_width})
    elif subsampling == "420":
        cb_plane = _dispatch("compression_image", "compression_jpeg_subsample_420", inputs={"src": cb_plane}, outputs={"dst": np.empty((padded_height // 2, padded_width // 2), np.float32)}, scalars={"h": padded_height, "w": padded_width})
        cr_plane = _dispatch("compression_image", "compression_jpeg_subsample_420", inputs={"src": cr_plane}, outputs={"dst": np.empty((padded_height // 2, padded_width // 2), np.float32)}, scalars={"h": padded_height, "w": padded_width})
    y_blocks = _quantize_plane(y_plane, quality)
    cb_blocks = _quantize_plane(cb_plane, quality, chroma=True)
    cr_blocks = _quantize_plane(cr_plane, quality, chroma=True)
    dc_luma, ac_luma, dc_chroma, ac_chroma = _huffman_tables()
    y_bits = _pack_plane_bits(y_blocks, dc_luma, ac_luma)
    cb_bits = _pack_plane_bits(cb_blocks, dc_chroma, ac_chroma)
    cr_bits = _pack_plane_bits(cr_blocks, dc_chroma, ac_chroma)
    scan_bits = []
    y_hb, y_wb = y_blocks.shape[0], y_blocks.shape[1] // 64
    c_hb, c_wb = cb_blocks.shape[0], cb_blocks.shape[1] // 64
    if subsampling == "444":
        for by in range(y_hb):
            for bx in range(y_wb):
                _append_bits(scan_bits, [y_bits[by][bx], cb_bits[by][bx], cr_bits[by][bx]])
        sampling = 0x11
    elif subsampling == "422":
        for by in range(c_hb):
            for bx in range(c_wb):
                _append_bits(scan_bits, [y_bits[by][2 * bx], y_bits[by][2 * bx + 1], cb_bits[by][bx], cr_bits[by][bx]])
        sampling = 0x21
    else:
        for by in range(c_hb):
            for bx in range(c_wb):
                _append_bits(scan_bits, [y_bits[2 * by][2 * bx], y_bits[2 * by][2 * bx + 1], y_bits[2 * by + 1][2 * bx], y_bits[2 * by + 1][2 * bx + 1], cb_bits[by][bx], cr_bits[by][bx]])
        sampling = 0x22
    luma, chroma = _quality_tables(quality)
    return assemble_baseline_jfif(_bits_to_scan(scan_bits), width, height, luma, chroma, sampling)


def jpeg_encode_aot(image, quality=75, subsampling="444", grayscale=False):
    data = np.asarray(image)
    if grayscale or data.ndim == 2:
        return encode_grayscale_aot(data, quality)
    return encode_rgb_aot(data, quality, subsampling)


__all__ = ["encode_grayscale_aot", "encode_rgb_aot", "jpeg_encode_aot"]
