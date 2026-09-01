"""End-to-end baseline JPEG encoders backed by the compression TCM module.

Pixel/color conversion, DCT quantization, zig-zag, run-length, symbol, and
bit-packing stages are dispatched to AOT graphs.  Variable-length MCU ordering
and JFIF marker assembly remain host-side because their sizes are data
dependent and the container is a byte stream.
"""

from __future__ import annotations

import heapq
import os

import numpy as np

from taichi_vision.taichi_algorithm.compression.jpeg_tables import (
    JPEG_CHROMA_TABLE,
    JPEG_QUALITY_TABLE,
    JPEG_ZIGZAG,
)
from taichi_vision.taichi_algorithm.compression.jpeg_container import (
    STANDARD_DHT,
    assemble_baseline_jfif,
    assemble_grayscale_jfif,
    assemble_jfif,
    dht,
)

from taichi_vision.taichi_algorithm.aot_api.research import _as_f32, _dispatch

from .bitstream import BitWriter


JPEG_PRESETS = {
    # The preset names are policy profiles; quality remains an explicit
    # caller-controlled value so selecting a speed profile never silently
    # changes image fidelity.
    "ultra_fast": {"subsampling": "422", "huffman": "standard"},
    "fast": {"subsampling": "422", "huffman": "standard"},
    "medium": {"subsampling": "422", "huffman": "optimized"},
    "high": {"subsampling": "444", "huffman": "optimized"},
    "best": {"subsampling": "444", "huffman": "optimized"},
}


def _resolve_preset(preset, subsampling: str, huffman: str) -> tuple[str, str]:
    if preset is None:
        return str(subsampling), str(huffman).lower()
    key = str(preset).strip().lower().replace("-", "_").replace(" ", "_")
    try:
        selected = JPEG_PRESETS[key]
    except KeyError as exc:
        raise ValueError(f"unknown JPEG preset: {preset!r}; choose one of {tuple(JPEG_PRESETS)}") from exc
    return selected["subsampling"], selected["huffman"]


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


def _bounded_huffman_lengths(frequencies, max_bits=16):
    active = [(int(value), symbol, symbol) for symbol, value in enumerate(frequencies) if value > 0]
    lengths = [0] * len(frequencies)
    if not active:
        lengths[0] = 1
        return lengths
    if len(active) == 1:
        lengths[active[0][2]] = 1
        return lengths
    heapq.heapify(active)
    nodes = {}
    next_node = len(frequencies)
    order = len(frequencies)
    while len(active) > 1:
        left = heapq.heappop(active)
        right = heapq.heappop(active)
        nodes[next_node] = (left[2], right[2])
        heapq.heappush(active, (left[0] + right[0], order, next_node))
        order += 1
        next_node += 1
    lengths_stack = [(active[0][2], 0)]
    while lengths_stack:
        node, depth = lengths_stack.pop()
        if node < len(frequencies):
            lengths[node] = max(1, depth)
        else:
            left, right = nodes[node]
            lengths_stack.extend(((left, depth + 1), (right, depth + 1)))
    counts = [0] * (max(max(lengths), max_bits) + 1)
    for length in lengths:
        if length:
            counts[length] += 1

    # Length-limit a complete binary tree without first clamping long leaves.
    # For every pair of leaves at depth ``i`` we merge them at ``i - 1`` and
    # split one shallower leaf.  Each operation preserves both Kraft equality
    # and the number of leaves; the old implementation clamped first and could
    # produce an overfull tree for a large, skewed histogram.
    for length in range(len(counts) - 1, max_bits, -1):
        while counts[length] > 0:
            if counts[length] < 2:
                raise ValueError("unable to bound JPEG Huffman tree")
            counts[length] -= 2
            counts[length - 1] += 1
            split = length - 2
            while split > 0 and counts[split] == 0:
                split -= 1
            if split == 0:
                raise ValueError("unable to bound JPEG Huffman tree")
            counts[split] -= 1
            counts[split + 1] += 2
    ordered = sorted(
        (symbol for symbol, frequency in enumerate(frequencies) if frequency > 0),
        key=lambda symbol: (frequencies[symbol], symbol),
    )
    cursor = 0
    for length in range(max_bits, 0, -1):
        for _ in range(counts[length]):
            if cursor >= len(ordered):
                raise ValueError("invalid JPEG bounded Huffman histogram")
            lengths[ordered[cursor]] = length
            cursor += 1
    if cursor != len(ordered):
        raise ValueError("incomplete JPEG bounded Huffman histogram")
    return lengths


def _optimized_table(frequencies, table_class, table_id):
    original = [int(value) for value in frequencies]
    if any(value < 0 for value in original):
        raise ValueError("JPEG Huffman frequencies must be non-negative")
    if not any(original):
        # An AC histogram should normally contain EOB, but keep the table
        # builder total and safe when called directly with an empty sample.
        original[0] = 1
    # Add a synthetic, never-emitted leaf outside the JPEG symbol alphabet.
    # A full AC histogram may legitimately contain all 256 symbols (and a DC
    # histogram may contain every category), so selecting an unused in-range
    # symbol is not safe.  Keeping the dummy in the tree while constructing
    # canonical codes prevents an emitted code from becoming the forbidden
    # all-ones code; it is omitted only from the DHT payload afterwards.
    dummy = len(original)
    working = original[:] + [1]
    # Make the pseudo-leaf strictly less frequent than every real leaf.  If a
    # real symbol also has frequency one, the old tie-break put the pseudo
    # leaf in the middle of the canonical sequence; removing it then shifted
    # all subsequent codes and produced corrupt optimized scans.
    working = [value + 1 if value > 0 else 0 for value in working]
    working[dummy] = 1
    lengths = _bounded_huffman_lengths(working, max_bits=16)
    all_symbols = [symbol for symbol, value in enumerate(working) if value > 0]
    ordered = sorted(((symbol, lengths[symbol]) for symbol in all_symbols), key=lambda item: (item[1], item[0]))
    if ordered[-1][0] != dummy:
        raise ValueError("JPEG optimized pseudo-leaf is not the final canonical code")
    codes = {}
    code = 0
    previous = 0
    for symbol, length in ordered:
        code <<= length - previous
        codes[symbol] = (code, length)
        code += 1
        previous = length
    dummy_code, dummy_length = codes[dummy]
    if dummy_code != (1 << dummy_length) - 1:
        raise ValueError("JPEG optimized pseudo-leaf is not the reserved all-ones code")
    active_ordered = tuple(item for item in ordered if item[0] != dummy)
    bits = tuple(sum(1 for _symbol, length in active_ordered if length == size) for size in range(1, 17))
    values = tuple(symbol for symbol, _length in active_ordered)
    return {symbol: codes[symbol] for symbol, _length in active_ordered}, dht(bits, values, table_class, table_id)


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


def _quantize_plane(plane, quality, chroma=False, resident=False):
    h, w = plane.shape
    hb, wb = h // 8, w // 8
    graph = "compression_jpeg_dct_quantize_chroma_2d" if chroma else "compression_jpeg_dct_quantize_2d"
    base_table = JPEG_CHROMA_TABLE if chroma else JPEG_QUALITY_TABLE
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    quant_table = np.asarray([max(1, min(255, (value * scale + 50) // 100)) for value in base_table], dtype=np.float32)
    dct_mode = os.environ.get("JPEG_DCT_MODE", "fused").strip().lower()
    if dct_mode not in {"fused", "legacy"}:
        raise ValueError("JPEG_DCT_MODE must be 'fused' or 'legacy'")
    source = np.ascontiguousarray(plane)
    if dct_mode == "fused":
        return _dispatch(
            "compression_image",
            "compression_jpeg_dct_quantize_zigzag_2d",
            inputs={"src": source, "quant_table": quant_table, "basis": _DCT_BASIS, "order": _JPEG_ZIGZAG},
            outputs={"dst": ((hb, wb * 64), np.float32)},
            scalars={"h_blocks": hb, "w_blocks": wb},
            plain_ndarray=False,
            return_gpu=bool(resident),
        )
    raw = _dispatch(
        "compression_image",
        graph,
        inputs={"src": source, "quant_table": quant_table, "basis": _DCT_BASIS},
        outputs={"dst": ((hb, wb * 64), np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
        return_gpu=bool(resident),
    )
    try:
        ordered = _dispatch(
            "compression_image",
            "compression_jpeg_zigzag_2d",
            inputs={"src": raw, "order": _JPEG_ZIGZAG},
            outputs={"dst": ((hb, wb * 64), np.float32)},
            scalars={"h_blocks": hb, "w_blocks": wb},
            plain_ndarray=False,
            return_gpu=bool(resident),
        )
    except Exception:
        if hasattr(raw, "destroy"):
            raw.destroy()
        raise
    if resident:
        raw.destroy()
        return ordered
    return ordered


def _quantize_plane_gpu_chained(plane, quality, chroma=False):
    """GPU-resident JPEG pipeline: DCT+quant+zigzag → tokens → histogram.

    This function chains multiple GPU dispatches while keeping intermediate
    results on GPU (using return_gpu=True), minimizing GPU↔CPU round-trips.
    Returns (dc_diff, symbols, categories, amplitudes, token_count,
    dc_histogram, ac_histogram) ready for host-side Huffman coding.

    This is the optimized path for 12MP realtime compression on GPU.
    """
    h, w = plane.shape
    hb, wb = h // 8, w // 8
    base_table = JPEG_CHROMA_TABLE if chroma else JPEG_QUALITY_TABLE
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    quant_table = np.asarray([max(1, min(255, (value * scale + 50) // 100)) for value in base_table], dtype=np.float32)
    source = np.ascontiguousarray(plane)

    # Stage 1: DCT + quantization + zigzag (GPU resident)
    ordered_gpu = _dispatch(
        "compression_image",
        "compression_jpeg_dct_quantize_zigzag_2d",
        inputs={"src": source, "quant_table": quant_table, "basis": _DCT_BASIS, "order": _JPEG_ZIGZAG},
        outputs={"dst": ((hb, wb * 64), np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
        return_gpu=True,
    )

    # Stage 2: Token preparation (GPU resident)
    prepared_gpu = _dispatch(
        "compression_image",
        "compression_jpeg_prepare_tokens_2d",
        inputs={"ordered": ordered_gpu},
        outputs={
            "dc_diff": ((hb * wb,), np.float32),
            "symbols": ((hb, wb * 64), np.int32),
            "categories": ((hb, wb * 64), np.int32),
            "amplitudes": ((hb, wb * 64), np.int32),
            "token_count": ((hb, wb), np.int32),
        },
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
        return_gpu=True,
    )

    # Stage 3: Histogram (GPU resident)
    histogram_gpu = _dispatch(
        "compression_image",
        "compression_jpeg_symbol_histogram_2d",
        inputs={
            "dc_diff": prepared_gpu["dc_diff"],
            "symbols": prepared_gpu["symbols"],
            "token_count": prepared_gpu["token_count"],
        },
        outputs={
            "dc_histogram": np.zeros(16, dtype=np.int32),
            "ac_histogram": np.zeros(256, dtype=np.int32),
        },
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
        return_gpu=True,
    )

    # Read back results from GPU to CPU (only once at the end)
    dc_diff = np.asarray(prepared_gpu["dc_diff"].to_numpy(), dtype=np.float32)
    symbols = np.asarray(prepared_gpu["symbols"].to_numpy(), dtype=np.int32)
    categories = np.asarray(prepared_gpu["categories"].to_numpy(), dtype=np.int32)
    amplitudes = np.asarray(prepared_gpu["amplitudes"].to_numpy(), dtype=np.int32)
    token_count = np.asarray(prepared_gpu["token_count"].to_numpy(), dtype=np.int32)
    dc_histogram = np.asarray(histogram_gpu["dc_histogram"].to_numpy(), dtype=np.int64)
    ac_histogram = np.asarray(histogram_gpu["ac_histogram"].to_numpy(), dtype=np.int64)

    # Release GPU buffers
    ordered_gpu.destroy()
    prepared_gpu["dc_diff"].destroy()
    prepared_gpu["symbols"].destroy()
    prepared_gpu["categories"].destroy()
    prepared_gpu["amplitudes"].destroy()
    prepared_gpu["token_count"].destroy()
    histogram_gpu["dc_histogram"].destroy()
    histogram_gpu["ac_histogram"].destroy()

    return dc_diff, symbols, categories, amplitudes, token_count, dc_histogram, ac_histogram


def _materialize_ordered(value):
    if hasattr(value, "to_numpy"):
        try:
            return np.ascontiguousarray(value.to_numpy(), dtype=np.float32)
        finally:
            value.destroy()
    return value


def _prepare_plane_tokens(ordered):
    hb, wb = ordered.shape[0], ordered.shape[1] // 64
    token_mode = os.environ.get("JPEG_TOKEN_MODE", "fused").strip().lower()
    if token_mode not in {"fused", "legacy"}:
        raise ValueError("JPEG_TOKEN_MODE must be 'fused' or 'legacy'")
    if token_mode == "fused":
        prepared = _dispatch(
            "compression_image",
            "compression_jpeg_prepare_tokens_2d",
            inputs={"ordered": ordered},
            outputs={
                "dc_diff": ((hb * wb,), np.float32),
                "symbols": ((hb, wb * 64), np.int32),
                "categories": ((hb, wb * 64), np.int32),
                "amplitudes": ((hb, wb * 64), np.int32),
                "token_count": ((hb, wb), np.int32),
            },
            scalars={"h_blocks": hb, "w_blocks": wb},
            plain_ndarray=False,
        )
        return (
            prepared["dc_diff"],
            prepared["symbols"],
            prepared["categories"],
            prepared["amplitudes"],
            prepared["token_count"],
        )
    dc_diff = _dispatch(
        "compression_image",
        "compression_jpeg_dc_difference_2d",
        inputs={"zigzag": ordered},
        outputs={"dc_diff": ((hb * wb,), np.float32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    rle = _dispatch(
        "compression_image",
        "compression_jpeg_ac_rle_2d",
        inputs={"zigzag": ordered},
        outputs={
            "runs": ((hb, wb * 64), np.int32),
            "values": ((hb, wb * 64), np.float32),
            "token_count": ((hb, wb), np.int32),
        },
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    symbol_data = _dispatch(
        "compression_image",
        "compression_jpeg_ac_symbols_2d",
        inputs={"runs": rle["runs"], "values": rle["values"], "token_count": rle["token_count"]},
        outputs={
            "symbols": ((hb, wb * 64), np.int32),
            "categories": ((hb, wb * 64), np.int32),
            "amplitudes": ((hb, wb * 64), np.int32),
        },
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    return dc_diff, symbol_data["symbols"], symbol_data["categories"], symbol_data["amplitudes"], rle["token_count"]


def _plane_histogram(ordered, prepared=None, *, return_prepared=False):
    if prepared is None:
        prepared = _prepare_plane_tokens(ordered)
    dc_diff, symbols, _categories, _amplitudes, token_count = prepared
    hb, wb = ordered.shape[0], ordered.shape[1] // 64
    result = _dispatch(
        "compression_image",
        "compression_jpeg_symbol_histogram_2d",
        inputs={"dc_diff": dc_diff, "symbols": symbols, "token_count": token_count},
        outputs={"dc_histogram": np.zeros(16, dtype=np.int32), "ac_histogram": np.zeros(256, dtype=np.int32)},
        scalars={"h_blocks": hb, "w_blocks": wb},
        plain_ndarray=False,
    )
    histograms = (
        np.asarray(result["dc_histogram"], dtype=np.int64),
        np.asarray(result["ac_histogram"], dtype=np.int64),
    )
    if return_prepared:
        return histograms[0], histograms[1], prepared
    return histograms


def _pack_plane_bits(ordered, dc_table, ac_table, prepared=None):
    hb, wb = ordered.shape[0], ordered.shape[1] // 64
    if prepared is None:
        prepared = _prepare_plane_tokens(ordered)
    dc_diff, symbols, categories, amplitudes, token_count = prepared
    dc_codes, dc_lengths = _code_arrays(dc_table, 16)
    ac_codes, ac_lengths = _code_arrays(ac_table, 256)
    # A 12 MP 4:2:0 frame has 98,304 luma blocks.  Keeping 4096 int32
    # candidates per block would require roughly 3 GiB.  Process a few block
    # rows at a time and retain only packed bytes plus exact bit counts.
    max_output_bits = 2048
    max_output_bytes = max_output_bits // 8
    block_bytes = np.zeros((hb * wb, max_output_bytes), dtype=np.uint8)
    block_counts = np.zeros(hb * wb, dtype=np.int32)
    # The temporary i32 graph output is bounded per chunk.  A larger default
    # amortizes graph-dispatch and host-copy overhead on 12 MP frames while
    # allowing low-VRAM deployments to select a smaller deterministic tile.
    # Default to processing all rows at once for maximum throughput.
    try:
        requested_chunk_rows = int(os.environ.get("JPEG_PACK_CHUNK_ROWS", str(hb)))
    except ValueError as exc:
        raise ValueError("JPEG_PACK_CHUNK_ROWS must be a positive integer") from exc
    if requested_chunk_rows <= 0:
        raise ValueError("JPEG_PACK_CHUNK_ROWS must be a positive integer")
    chunk_rows = max(1, min(hb, requested_chunk_rows))
    for first_row in range(0, hb, chunk_rows):
        rows = min(chunk_rows, hb - first_row)
        first = first_row * wb
        last = (first_row + rows) * wb
        common_inputs = {
            "dc_diff": np.ascontiguousarray(dc_diff[first:last]),
            "ac_symbols": np.ascontiguousarray(symbols[first_row:first_row + rows]),
            "ac_categories": np.ascontiguousarray(categories[first_row:first_row + rows]),
            "ac_amplitudes": np.ascontiguousarray(amplitudes[first_row:first_row + rows]),
            "ac_counts": np.ascontiguousarray(token_count[first_row:first_row + rows]),
            "dc_codes": dc_codes,
            "dc_lengths": dc_lengths,
            "ac_codes": ac_codes,
            "ac_lengths": ac_lengths,
        }
        pack_mode = os.environ.get("JPEG_PACK_MODE", "bytes").strip().lower()
        if pack_mode not in {"bytes", "bits"}:
            raise ValueError("JPEG_PACK_MODE must be 'bytes' or 'bits'")
        if pack_mode == "bytes":
            packed = _dispatch(
                "compression_image",
                "compression_jpeg_pack_bytes_2d",
                inputs=common_inputs,
                outputs={
                    "output": ((rows, wb * max_output_bytes), np.int32),
                    "output_count": ((rows, wb), np.int32),
                },
                scalars={"h_blocks": rows, "w_blocks": wb, "max_output_bytes": max_output_bytes},
                plain_ndarray=False,
            )
            counts = np.asarray(packed["output_count"], dtype=np.int32).reshape(-1)
            if np.any((counts + 7) // 8 > max_output_bytes):
                raise RuntimeError("JPEG block byte buffer overflow; increase the bounded block capacity")
            raw_bytes = np.asarray(packed["output"], dtype=np.int32).reshape(rows * wb, max_output_bytes)
            block_bytes[first:last] = raw_bytes.astype(np.uint8, copy=False)
        else:
            packed = _dispatch(
                "compression_image",
                "compression_jpeg_pack_bits_2d",
                inputs=common_inputs,
                outputs={
                    "bits": ((rows, wb * max_output_bits), np.int32),
                    "bit_count": ((rows, wb), np.int32),
                },
                scalars={"h_blocks": rows, "w_blocks": wb, "max_output_bits": max_output_bits},
                plain_ndarray=False,
            )
            counts = np.asarray(packed["bit_count"], dtype=np.int32).reshape(-1)
            if np.any(counts >= max_output_bits):
                raise RuntimeError("JPEG block bit buffer overflow; increase the bounded block capacity")
            bits = np.asarray(packed["bits"], dtype=np.uint8).reshape(rows, wb, max_output_bits)
            block_bytes[first:last] = np.packbits(bits, axis=2, bitorder="big").reshape(rows * wb, max_output_bytes)
        block_counts[first:last] = counts
    return block_bytes, block_counts


def _append_packed_block(writer: BitWriter, block_bytes: np.ndarray, bit_count: int, index: int) -> None:
    count = int(bit_count)
    if count < 0 or count > block_bytes.shape[1] * 8:
        raise ValueError("invalid packed JPEG block bit count")
    writer.write_bytes_msb(block_bytes[index], count)


def _bits_to_scan(writer: BitWriter) -> bytes:
    raw = writer.finish(fill=1)
    stream = bytearray()
    for value in raw:
        stream.append(value)
        if value == 0xFF:
            stream.append(0)
    return bytes(stream)


def _normalize_restart_interval(value) -> int:
    if value is None:
        return 0
    if isinstance(value, bool):
        raise TypeError("restart_interval must be an integer MCU count")
    try:
        interval = int(value)
    except (TypeError, ValueError) as exc:
        raise TypeError("restart_interval must be an integer MCU count") from exc
    if interval != value or not 0 <= interval <= 65535:
        raise ValueError("restart_interval must be in [0, 65535]")
    return interval


def _component_scan_order(block_rows: int, block_cols: int, subsampling: str, component: str) -> tuple[tuple[int, int], ...]:
    """Return ``(linear_block, mcu_index)`` pairs in JPEG scan order."""

    if subsampling == "444" or component != "y":
        return tuple(
            (by * block_cols + bx, by * block_cols + bx)
            for by in range(block_rows)
            for bx in range(block_cols)
        )
    if subsampling == "422":
        mcu_cols = block_cols // 2
        return tuple(
            (by * block_cols + 2 * bx + dx, by * mcu_cols + bx)
            for by in range(block_rows)
            for bx in range(block_cols // 2)
            for dx in range(2)
        )
    if subsampling == "420":
        mcu_cols = block_cols // 2
        return tuple(
            # ``by`` indexes MCU rows, while the luma block grid has two
            # 8x8 rows per MCU.  The previous expression advanced by only
            # one luma row per MCU row, which left the second MCU row's DC
            # predictor attached to the wrong blocks whenever a restart
            # boundary crossed that region.
            ((2 * by + row) * block_cols + 2 * bx + dx,
             by * mcu_cols + bx)
            for by in range(block_rows // 2)
            for bx in range(mcu_cols)
            for row in range(2)
            for dx in range(2)
        )
    raise ValueError("subsampling must be 444, 422, or 420")


def _prepare_scan_tokens(ordered, prepared, subsampling, component, restart_interval):
    """Reset DC prediction at restart boundaries using the native token set."""
    # 4:2:0 luma is interleaved in MCU order (two luma rows per MCU), which
    # differs from the plane's ordinary row-major block order even when no
    # restart markers are requested.  Its DC differences therefore need the
    # scan-order remap unconditionally; the other current component layouts
    # retain row-major order when restart markers are disabled.
    if not restart_interval and not (subsampling == "420" and component == "y"):
        return prepared
    dc_diff, symbols, categories, amplitudes, token_count = prepared
    dc = np.asarray(dc_diff, dtype=np.float32).copy()
    rows, cols = ordered.shape[0], ordered.shape[1] // 64
    previous = 0.0
    previous_mcu = -1
    for linear, mcu_index in _component_scan_order(rows, cols, subsampling, component):
        block_y, block_x = divmod(linear, cols)
        if restart_interval and mcu_index != previous_mcu and mcu_index % int(restart_interval) == 0:
            previous = 0.0
        current = float(ordered[block_y, block_x * 64])
        dc[linear] = current - previous
        previous = current
        previous_mcu = mcu_index
    return dc, symbols, categories, amplitudes, token_count
def _restart_checkpoint(parts: list[bytes], writer: BitWriter, mcu_index: int, total_mcus: int, interval: int) -> BitWriter:
    if interval > 0 and (mcu_index + 1) < total_mcus and (mcu_index + 1) % interval == 0:
        parts.append(_bits_to_scan(writer))
        restart_number = ((mcu_index + 1) // interval - 1) % 8
        parts.append(bytes((0xFF, 0xD0 + restart_number)))
        return BitWriter(lsb_first=False)
    return writer


def _finish_scan(parts: list[bytes], writer: BitWriter) -> bytes:
    parts.append(_bits_to_scan(writer))
    return b"".join(parts)


def _scatter_scan_blocks_native(block_bytes, block_counts) -> bytes:
    """Concatenate packed JPEG blocks through one native scatter graph."""
    block_bytes = np.asarray(block_bytes)
    counts = np.ascontiguousarray(block_counts, dtype=np.int32).reshape(-1)
    if block_bytes.ndim != 2 or block_bytes.shape[0] != counts.size:
        raise ValueError("JPEG packed blocks and bit counts have incompatible shapes")
    if counts.size == 0:
        return b""
    max_bits = int(block_bytes.shape[1]) * 8
    if np.any(counts < 0) or np.any(counts > max_bits):
        raise ValueError("JPEG packed block bit count is outside its bounded buffer")
    try:
        chunk_blocks = int(os.environ.get("JPEG_SCATTER_CHUNK_BLOCKS", "2048"))
    except ValueError as exc:
        raise ValueError("JPEG_SCATTER_CHUNK_BLOCKS must be a positive integer") from exc
    if chunk_blocks <= 0:
        raise ValueError("JPEG_SCATTER_CHUNK_BLOCKS must be a positive integer")

    # Keep the arithmetic graph bounded on Vulkan/OpenGL.  A BitWriter carries
    # the final partial byte between chunks, so chunking does not introduce a
    # byte boundary or change the JPEG output.
    scan_writer = BitWriter(lsb_first=False)
    for first in range(0, counts.size, chunk_blocks):
        last = min(counts.size, first + chunk_blocks)
        chunk_counts = np.ascontiguousarray(counts[first:last], dtype=np.int32)
        offsets = np.zeros(chunk_counts.size, dtype=np.int32)
        if chunk_counts.size > 1:
            prefix = np.cumsum(chunk_counts[:-1], dtype=np.int64)
            if int(prefix[-1]) > 0x7FFFFFFF:
                raise ValueError("JPEG scan chunk exceeds the native scatter bound")
            offsets[1:] = prefix.astype(np.int32, copy=False)
        total_bits = int(offsets[-1]) + int(chunk_counts[-1])
        if total_bits <= 0:
            continue
        max_chunk_bytes = max(1, (int(np.max(chunk_counts)) + 7) // 8)
        # The graph ABI currently uses i32 block bytes.  Convert only the
        # active chunk instead of materializing a full-frame uint8->i32 copy;
        # for a 12 MP frame this avoids retaining roughly 250 MB of converted
        # block storage alongside the original packed buffer.
        chunk_block_bytes = np.ascontiguousarray(block_bytes[first:last], dtype=np.int32)
        scattered = _dispatch(
            "compression_image",
            "compression_jpeg_scatter_block_bits",
            inputs={
                "block_bytes": chunk_block_bytes,
                "block_counts": chunk_counts,
                "bit_offsets": offsets,
            },
            outputs={"output_bits": ((total_bits,), np.int32)},
            scalars={"block_count": int(chunk_counts.size), "max_output_bytes": max_chunk_bytes},
            plain_ndarray=False,
        )
        bits = np.asarray(scattered, dtype=np.uint8).reshape(-1)
        scan_writer.write_bytes_msb(bytes(np.packbits(bits, bitorder="big")), total_bits)
    return _bits_to_scan(scan_writer)


def _interleave_scan_blocks_native(y_bits, cb_bits, cr_bits, subsampling: str, y_hb: int, y_wb: int, c_hb: int, c_wb: int):
    """Return packed blocks in JPEG MCU order for a non-restart scan."""
    y_bytes, y_counts = (np.asarray(y_bits[0]), np.asarray(y_bits[1]))
    cb_bytes, cb_counts = (np.asarray(cb_bits[0]), np.asarray(cb_bits[1]))
    cr_bytes, cr_counts = (np.asarray(cr_bits[0]), np.asarray(cr_bits[1]))
    max_bytes = y_bytes.shape[1]
    if cb_bytes.shape[1] != max_bytes or cr_bytes.shape[1] != max_bytes:
        raise ValueError("JPEG block buffers must have a common bounded byte width")
    if subsampling == "444":
        block_count = y_bytes.shape[0]
        packed = np.empty((block_count * 3, max_bytes), dtype=np.uint8)
        counts = np.empty(block_count * 3, dtype=np.int32)
        packed[0::3] = y_bytes
        packed[1::3] = cb_bytes
        packed[2::3] = cr_bytes
        counts[0::3] = y_counts
        counts[1::3] = cb_counts
        counts[2::3] = cr_counts
        return packed, counts
    if subsampling == "422":
        y_group = y_bytes.reshape(c_hb, c_wb, 2, max_bytes)
        y_count_group = y_counts.reshape(c_hb, c_wb, 2)
        packed_grid = np.empty((c_hb, c_wb, 4, max_bytes), dtype=np.uint8)
        count_grid = np.empty((c_hb, c_wb, 4), dtype=np.int32)
        packed_grid[:, :, :2] = y_group
        packed_grid[:, :, 2] = cb_bytes.reshape(c_hb, c_wb, max_bytes)
        packed_grid[:, :, 3] = cr_bytes.reshape(c_hb, c_wb, max_bytes)
        count_grid[:, :, :2] = y_count_group
        count_grid[:, :, 2] = cb_counts.reshape(c_hb, c_wb)
        count_grid[:, :, 3] = cr_counts.reshape(c_hb, c_wb)
        packed = packed_grid.reshape(-1, max_bytes)
        counts = count_grid.reshape(-1)
        return packed, counts
    if subsampling == "420":
        y_grid = y_bytes.reshape(y_hb, y_wb, max_bytes)
        y_count_grid = y_counts.reshape(y_hb, y_wb)
        packed_grid = np.empty((c_hb, c_wb, 6, max_bytes), dtype=np.uint8)
        count_grid = np.empty((c_hb, c_wb, 6), dtype=np.int32)
        packed_grid[:, :, 0] = y_grid[0::2, 0::2]
        packed_grid[:, :, 1] = y_grid[0::2, 1::2]
        packed_grid[:, :, 2] = y_grid[1::2, 0::2]
        packed_grid[:, :, 3] = y_grid[1::2, 1::2]
        packed_grid[:, :, 4] = cb_bytes.reshape(c_hb, c_wb, max_bytes)
        packed_grid[:, :, 5] = cr_bytes.reshape(c_hb, c_wb, max_bytes)
        count_grid[:, :, 0] = y_count_grid[0::2, 0::2]
        count_grid[:, :, 1] = y_count_grid[0::2, 1::2]
        count_grid[:, :, 2] = y_count_grid[1::2, 0::2]
        count_grid[:, :, 3] = y_count_grid[1::2, 1::2]
        count_grid[:, :, 4] = cb_counts.reshape(c_hb, c_wb)
        count_grid[:, :, 5] = cr_counts.reshape(c_hb, c_wb)
        packed = packed_grid.reshape(-1, max_bytes)
        counts = count_grid.reshape(-1)
        return packed, counts
    raise ValueError(f"unsupported JPEG scan subsampling: {subsampling!r}")


def _native_scan_pack_enabled(block_count: int, restart_interval: int) -> bool:
    if restart_interval:
        return False
    mode = os.environ.get("JPEG_NATIVE_SCAN_PACK", "auto").strip().lower()
    if mode not in {"auto", "0", "1"}:
        raise ValueError("JPEG_NATIVE_SCAN_PACK must be 'auto', '0', or '1'")
    if mode == "1":
        return True
    if mode == "0":
        return False
    # The graph removes Python block concatenation and was measured at about
    # 28.4 s for a 12 MP 4:2:0 scan when explicitly enabled on the active
    # NVIDIA OpenGL target. Keep auto conservative because scatter materializes a
    # native bit buffer and can become dramatically slower under memory
    # pressure.  Large scans can opt in with JPEG_NATIVE_SCAN_PACK=1; low-
    # memory deployments can force the established path with =0.
    try:
        auto_limit = int(os.environ.get("JPEG_NATIVE_SCAN_AUTO_MAX_BLOCKS", "32768"))
    except ValueError as exc:
        raise ValueError("JPEG_NATIVE_SCAN_AUTO_MAX_BLOCKS must be a positive integer") from exc
    if auto_limit <= 0:
        raise ValueError("JPEG_NATIVE_SCAN_AUTO_MAX_BLOCKS must be a positive integer")
    return int(block_count) <= auto_limit


def _quality_tables(quality):
    scale = 5000 // quality if quality < 50 else 200 - 2 * quality
    luma = tuple(max(1, min(255, (value * scale + 50) // 100)) for value in JPEG_QUALITY_TABLE)
    chroma = tuple(max(1, min(255, (value * scale + 50) // 100)) for value in JPEG_CHROMA_TABLE)
    return luma, chroma


def _normalize_jpeg_samples(image, error_message):
    data = np.asarray(image)
    if data.size == 0 or data.shape[0] <= 0 or data.shape[1] <= 0:
        raise ValueError(error_message)
    result = data.astype(np.float32)
    if np.issubdtype(data.dtype, np.floating) and float(np.min(result)) >= 0.0 and float(np.max(result)) <= 1.0:
        result *= 255.0
    if not np.all(np.isfinite(result)) or float(np.min(result)) < 0.0 or float(np.max(result)) > 255.0:
        raise ValueError("JPEG samples must be finite values in [0, 255]")
    return np.ascontiguousarray(result)


def _normalize_rgb(image):
    data = np.asarray(image)
    if data.ndim != 3 or data.shape[2] != 3:
        raise ValueError("RGB JPEG input must have shape (height, width, 3)")
    return _normalize_jpeg_samples(data, "RGB JPEG input must have shape (height, width, 3)")


def encode_grayscale_aot(image, quality=75, huffman="standard", *, preset=None, metadata=None, restart_interval=0):
    data = np.asarray(image)
    if data.ndim != 2:
        raise ValueError("grayscale JPEG input must be 2D")
    quality = int(quality)
    restart_interval = _normalize_restart_interval(restart_interval)
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")
    _ignored_subsampling, huffman = _resolve_preset(preset, "444", huffman)
    if huffman not in {"standard", "optimized"}:
        raise ValueError("huffman must be standard or optimized")
    source = _normalize_jpeg_samples(data, "grayscale JPEG input must be a non-empty 2D image")
    height, width = source.shape
    padded = _pad_plane(source, (height + 7) // 8 * 8, (width + 7) // 8 * 8)
    resident = os.environ.get("JPEG_RESIDENT_INTERMEDIATES", "0") == "1"
    ordered = _materialize_ordered(_quantize_plane(padded, quality, resident=resident))
    prepared = None
    if restart_interval:
        prepared = _prepare_scan_tokens(
            ordered,
            _prepare_plane_tokens(ordered),
            "444",
            "y",
            restart_interval,
        )
    if huffman == "optimized":
        dc_hist, ac_hist, prepared = _plane_histogram(ordered, prepared=prepared, return_prepared=True)
        dc_luma, dc_marker = _optimized_table(dc_hist, 0, 0)
        ac_luma, ac_marker = _optimized_table(ac_hist, 1, 0)
        huffman_markers = dc_marker + ac_marker
    else:
        dc_luma, ac_luma, _, _ = _huffman_tables()
        huffman_markers = None
    block_bytes, block_counts = _pack_plane_bits(ordered, dc_luma, ac_luma, prepared=prepared)
    if _native_scan_pack_enabled(block_bytes.shape[0], restart_interval):
        scan_data = _scatter_scan_blocks_native(block_bytes, block_counts)
    else:
        scan_parts: list[bytes] = []
        scan_writer = BitWriter(lsb_first=False)
        for index in range(block_bytes.shape[0]):
            _append_packed_block(scan_writer, block_bytes, block_counts[index], index)
            scan_writer = _restart_checkpoint(scan_parts, scan_writer, index, block_bytes.shape[0], restart_interval)
        scan_data = _finish_scan(scan_parts, scan_writer)
    luma, _ = _quality_tables(quality)
    if huffman_markers is None:
        return assemble_grayscale_jfif(scan_data, width, height, luma, metadata=metadata, restart_interval=restart_interval)
    return assemble_jfif(scan_data, width, height, luma, luma, huffman_markers, 0x11, 1, metadata=metadata, restart_interval=restart_interval)


def encode_rgb_aot(image, quality=75, subsampling="444", huffman="standard", *, preset=None, metadata=None, restart_interval=0):
    data = _normalize_rgb(image)
    quality = int(quality)
    restart_interval = _normalize_restart_interval(restart_interval)
    subsampling, huffman = _resolve_preset(preset, subsampling, huffman)
    subsampling = str(subsampling)
    if not 1 <= quality <= 100:
        raise ValueError("quality must be in [1, 100]")
    if subsampling not in {"444", "422", "420"}:
        raise ValueError("subsampling must be 444, 422, or 420")
    huffman = str(huffman).lower()
    if huffman not in {"standard", "optimized"}:
        raise ValueError("huffman must be standard or optimized")
    height, width = data.shape[:2]
    block_height = 16 if subsampling == "420" else 8
    block_width = 16 if subsampling in {"422", "420"} else 8
    padded_height = (height + block_height - 1) // block_height * block_height
    padded_width = (width + block_width - 1) // block_width * block_width
    padded_rgb = np.pad(data, ((0, padded_height - height), (0, padded_width - width), (0, 0)), mode="edge").astype(np.float32)
    color_mode = os.environ.get("JPEG_COLOR_MODE", "fused").strip().lower()
    if color_mode not in {"fused", "legacy"}:
        raise ValueError("JPEG_COLOR_MODE must be 'fused' or 'legacy'")
    if subsampling in {"422", "420"} and color_mode == "fused":
        fused_graph = "compression_rgb_to_ycbcr_422_pair" if subsampling == "422" else "compression_rgb_to_ycbcr_420_pair"
        chroma_shape = (
            (padded_height, padded_width // 2, 2)
            if subsampling == "422"
            else (padded_height // 2, padded_width // 2, 2)
        )
        fused = _dispatch(
            "compression_image",
            fused_graph,
            inputs={"src": padded_rgb},
            outputs={
                "y_dst": ((padded_height, padded_width), np.float32),
                "chroma_dst": (chroma_shape, np.float32),
            },
            scalars={"h": padded_height, "w": padded_width},
        )
        y_plane = fused["y_dst"]
        chroma_pair = fused["chroma_dst"]
        cb_plane, cr_plane = chroma_pair[..., 0], chroma_pair[..., 1]
    else:
        ycbcr = _dispatch(
            "compression_image",
            "compression_rgb_to_ycbcr",
            inputs={"src": padded_rgb},
            outputs={"dst": (padded_rgb.shape, np.float32)},
            scalars={"h": padded_height, "w": padded_width},
        )
        y_plane = ycbcr[..., 0]
        cb_plane = ycbcr[..., 1]
        cr_plane = ycbcr[..., 2]
        if subsampling == "422":
            chroma_pair = _dispatch(
                "compression_image",
                "compression_jpeg_subsample_422_pair",
                inputs={"src": ycbcr},
                outputs={"dst": ((padded_height, padded_width // 2, 2), np.float32)},
                scalars={"h": padded_height, "w": padded_width},
            )
            cb_plane, cr_plane = chroma_pair[..., 0], chroma_pair[..., 1]
        elif subsampling == "420":
            chroma_pair = _dispatch(
                "compression_image",
                "compression_jpeg_subsample_420_pair",
                inputs={"src": ycbcr},
                outputs={"dst": ((padded_height // 2, padded_width // 2, 2), np.float32)},
                scalars={"h": padded_height, "w": padded_width},
            )
            cb_plane, cr_plane = chroma_pair[..., 0], chroma_pair[..., 1]
    resident = os.environ.get("JPEG_RESIDENT_INTERMEDIATES", "0") == "1"
    y_blocks = _materialize_ordered(_quantize_plane(y_plane, quality, resident=resident))
    cb_blocks = _materialize_ordered(_quantize_plane(cb_plane, quality, chroma=True, resident=resident))
    cr_blocks = _materialize_ordered(_quantize_plane(cr_plane, quality, chroma=True, resident=resident))
    y_prepared = cb_prepared = cr_prepared = None
    if restart_interval or subsampling == "420":
        y_prepared = _prepare_scan_tokens(
            y_blocks,
            _prepare_plane_tokens(y_blocks),
            subsampling,
            "y",
            restart_interval,
        )
        cb_prepared = _prepare_scan_tokens(
            cb_blocks,
            _prepare_plane_tokens(cb_blocks),
            subsampling,
            "c",
            restart_interval,
        )
        cr_prepared = _prepare_scan_tokens(
            cr_blocks,
            _prepare_plane_tokens(cr_blocks),
            subsampling,
            "c",
            restart_interval,
        )
    if huffman == "optimized":
        y_dc_hist, y_ac_hist, y_prepared = _plane_histogram(y_blocks, prepared=y_prepared, return_prepared=True)
        cb_dc_hist, cb_ac_hist, cb_prepared = _plane_histogram(cb_blocks, prepared=cb_prepared, return_prepared=True)
        cr_dc_hist, cr_ac_hist, cr_prepared = _plane_histogram(cr_blocks, prepared=cr_prepared, return_prepared=True)
        dc_luma, y_dc_marker = _optimized_table(y_dc_hist, 0, 0)
        ac_luma, y_ac_marker = _optimized_table(y_ac_hist, 1, 0)
        dc_chroma, c_dc_marker = _optimized_table(cb_dc_hist + cr_dc_hist, 0, 1)
        ac_chroma, c_ac_marker = _optimized_table(cb_ac_hist + cr_ac_hist, 1, 1)
        huffman_markers = y_dc_marker + y_ac_marker + c_dc_marker + c_ac_marker
    else:
        dc_luma, ac_luma, dc_chroma, ac_chroma = _huffman_tables()
        huffman_markers = None
    y_bits = _pack_plane_bits(y_blocks, dc_luma, ac_luma, prepared=y_prepared)
    cb_bits = _pack_plane_bits(cb_blocks, dc_chroma, ac_chroma, prepared=cb_prepared)
    cr_bits = _pack_plane_bits(cr_blocks, dc_chroma, ac_chroma, prepared=cr_prepared)
    y_bytes, y_counts = y_bits
    cb_bytes, cb_counts = cb_bits
    cr_bytes, cr_counts = cr_bits
    y_hb, y_wb = y_blocks.shape[0], y_blocks.shape[1] // 64
    c_hb, c_wb = cb_blocks.shape[0], cb_blocks.shape[1] // 64
    if _native_scan_pack_enabled(y_bytes.shape[0] + cb_bytes.shape[0] + cr_bytes.shape[0], restart_interval):
        packed_blocks, packed_counts = _interleave_scan_blocks_native(
            y_bits,
            cb_bits,
            cr_bits,
            subsampling,
            y_hb,
            y_wb,
            c_hb,
            c_wb,
        )
        scan_data = _scatter_scan_blocks_native(packed_blocks, packed_counts)
        sampling = {"444": 0x11, "422": 0x21, "420": 0x22}[subsampling]
    else:
        scan_parts: list[bytes] = []
        scan_writer = BitWriter(lsb_first=False)
        if subsampling == "444":
            for by in range(y_hb):
                for bx in range(y_wb):
                    index = by * y_wb + bx
                    _append_packed_block(scan_writer, y_bytes, y_counts[index], index)
                    _append_packed_block(scan_writer, cb_bytes, cb_counts[index], index)
                    _append_packed_block(scan_writer, cr_bytes, cr_counts[index], index)
                    scan_writer = _restart_checkpoint(scan_parts, scan_writer, index, y_hb * y_wb, restart_interval)
            sampling = 0x11
        elif subsampling == "422":
            for by in range(c_hb):
                for bx in range(c_wb):
                    mcu_index = by * c_wb + bx
                    _append_packed_block(scan_writer, y_bytes, y_counts[by * y_wb + 2 * bx], by * y_wb + 2 * bx)
                    _append_packed_block(scan_writer, y_bytes, y_counts[by * y_wb + 2 * bx + 1], by * y_wb + 2 * bx + 1)
                    _append_packed_block(scan_writer, cb_bytes, cb_counts[by * c_wb + bx], by * c_wb + bx)
                    _append_packed_block(scan_writer, cr_bytes, cr_counts[by * c_wb + bx], by * c_wb + bx)
                    scan_writer = _restart_checkpoint(scan_parts, scan_writer, mcu_index, c_hb * c_wb, restart_interval)
            sampling = 0x21
        else:
            for by in range(c_hb):
                for bx in range(c_wb):
                    mcu_index = by * c_wb + bx
                    y_index = 2 * by * y_wb + 2 * bx
                    _append_packed_block(scan_writer, y_bytes, y_counts[y_index], y_index)
                    _append_packed_block(scan_writer, y_bytes, y_counts[y_index + 1], y_index + 1)
                    _append_packed_block(scan_writer, y_bytes, y_counts[y_index + y_wb], y_index + y_wb)
                    _append_packed_block(scan_writer, y_bytes, y_counts[y_index + y_wb + 1], y_index + y_wb + 1)
                    c_index = by * c_wb + bx
                    _append_packed_block(scan_writer, cb_bytes, cb_counts[c_index], c_index)
                    _append_packed_block(scan_writer, cr_bytes, cr_counts[c_index], c_index)
                    scan_writer = _restart_checkpoint(scan_parts, scan_writer, mcu_index, c_hb * c_wb, restart_interval)
            sampling = 0x22
        scan_data = _finish_scan(scan_parts, scan_writer)
    luma, chroma = _quality_tables(quality)
    if huffman_markers is None:
        return assemble_baseline_jfif(scan_data, width, height, luma, chroma, sampling, metadata=metadata, restart_interval=restart_interval)
    return assemble_jfif(scan_data, width, height, luma, chroma, huffman_markers, sampling, 3, metadata=metadata, restart_interval=restart_interval)


def jpeg_encode_aot(image, quality=75, subsampling="444", grayscale=False, huffman="standard", *, preset=None, metadata=None, restart_interval=0):
    data = np.asarray(image)
    if grayscale or data.ndim == 2:
        return encode_grayscale_aot(data, quality, huffman, preset=preset, metadata=metadata, restart_interval=restart_interval)
    return encode_rgb_aot(data, quality, subsampling, huffman, preset=preset, metadata=metadata, restart_interval=restart_interval)


__all__ = ["JPEG_PRESETS", "encode_grayscale_aot", "encode_rgb_aot", "jpeg_encode_aot"]
