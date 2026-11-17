"""Dependency-free native DNG/TIFF container and lossless raw writer.

The maintained profile is a little-endian, strip-based mosaiced DNG with
8..16-bit samples, uncompressed/PackBits/fixed- or dynamic-Deflate storage, and a constrained
single-component DNG Lossless-JPEG (Compression=7) path.  The parser is strict
about bounds and returns the original CFA samples exactly.  Restart markers,
point transforms, BigTIFF, and multi-component JPEG strips remain explicit
unsupported gates.
"""
from __future__ import annotations

import os
import heapq
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .bitstream import BitWriter, packbits_decode, packbits_encode
from .dng_deflate import deflate_dynamic, deflate_fixed, deflate_stored, inflate_deflate


_TYPE_SIZE = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8, 6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}
_SUPPORTED_COMPRESSION = frozenset((1, 7, 8, 32773))
_LOSSLESS_JPEG_COMPRESSION = frozenset((7,))
_LOSSY_JPEG_COMPRESSION = frozenset((34892,))
_TILE_TAGS = frozenset((322, 323, 324, 325))


def _numpy():
    """Import NumPy only for the legacy ndarray compatibility surface."""
    import numpy as np

    return np


def _fmt(endian: str, code: str) -> str:
    return ("<" if endian == "II" else ">") + code


def _pack_value(value, type_id: int, count: int, endian: str) -> bytes:
    if type_id == 1 or type_id == 7:
        return bytes(value if isinstance(value, (bytes, bytearray)) else [int(x) & 255 for x in value])
    if type_id == 2:
        raw = value.encode("ascii") if isinstance(value, str) else bytes(value)
        return raw + (b"" if raw.endswith(b"\x00") else b"\x00")
    if type_id == 3:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}H"), *[int(x) & 0xFFFF for x in values])
    if type_id == 4:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}I"), *[int(x) & 0xFFFFFFFF for x in values])
    if type_id == 5:
        values = value if isinstance(value, (tuple, list)) else [value]
        flat = []
        for numerator, denominator in values:
            flat.extend((int(numerator), int(denominator)))
        return struct.pack(_fmt(endian, f"{count * 2}I"), *flat)
    if type_id == 10:
        values = value if isinstance(value, (tuple, list)) else [value]
        flat = []
        for numerator, denominator in values:
            flat.extend((int(numerator), int(denominator)))
        return struct.pack(_fmt(endian, f"{count * 2}i"), *flat)
    if type_id == 6:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}b"), *[int(x) for x in values])
    if type_id == 8:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}h"), *[int(x) for x in values])
    if type_id == 9:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}i"), *[int(x) for x in values])
    if type_id == 11:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}f"), *[float(x) for x in values])
    if type_id == 12:
        values = value if isinstance(value, (tuple, list)) else [value]
        return struct.pack(_fmt(endian, f"{count}d"), *[float(x) for x in values])
    raise ValueError(f"unsupported TIFF field type: {type_id}")


def _build_ifd(entries: list[tuple[int, int, int, object]], ifd_offset: int, strip_offsets, endian: str) -> bytes:
    entry_count = len(entries)
    directory_size = 2 + entry_count * 12 + 4
    cursor = ifd_offset + directory_size
    encoded: list[tuple[int, int, int, bytes, int | None]] = []
    for tag, type_id, count, value in entries:
        payload = _pack_value(value, type_id, count, endian)
        if tag == 273:
            offsets = strip_offsets if isinstance(strip_offsets, (tuple, list)) else (strip_offsets,)
            payload = _pack_value(offsets, type_id, count, endian)
        if len(payload) <= 4:
            encoded.append((tag, type_id, count, payload.ljust(4, b"\x00"), None))
        else:
            if cursor & 1:
                cursor += 1
            value_offset = cursor
            encoded.append((tag, type_id, count, payload, value_offset))
            cursor += len(payload)
    directory = bytearray(struct.pack(_fmt(endian, "H"), entry_count))
    for tag, type_id, count, payload, value_offset in encoded:
        directory.extend(struct.pack(_fmt(endian, "HHI"), tag, type_id, count))
        if value_offset is None:
            directory.extend(payload)
        else:
            directory.extend(struct.pack(_fmt(endian, "I"), value_offset))
    directory.extend(struct.pack(_fmt(endian, "I"), 0))
    out = bytearray(directory)
    for _tag, _type_id, _count, payload, value_offset in encoded:
        if value_offset is None:
            continue
        while ifd_offset + len(out) < value_offset:
            out.append(0)
        out.extend(payload)
        if len(out) & 1:
            out.append(0)
    return bytes(out)


def _metadata_ifd_entries(metadata: Mapping[str, Any], key: str) -> list[tuple[int, int, int, object]]:
    """Validate caller-supplied TIFF entries for the DNG or Exif IFD.

    The native writer owns image-layout tags; this narrowly scoped escape hatch
    preserves camera colour and capture metadata for derived RAW files.
    """
    entries = []
    for item in metadata.get(key, ()):
        if not isinstance(item, (tuple, list)) or len(item) != 4:
            raise ValueError(f"{key} entries must be (tag, type, count, value)")
        tag, type_id, count, value = item
        tag, type_id, count = int(tag), int(type_id), int(count)
        min_tag = 0 if key == "gps_tags" else 1
        if not min_tag <= tag <= 0xFFFF or type_id not in _TYPE_SIZE or count < 1:
            raise ValueError(f"invalid {key} TIFF entry: {item!r}")
        if type_id in (5, 10) and count == 1 and isinstance(value, (tuple, list)) and len(value) == 2:
            # The native reader represents a single RATIONAL/SRATIONAL as one
            # pair, while the TIFF encoder consumes a sequence of pairs.
            value = (value,)
        # Validate the value now, before IFD layout calculations.
        _pack_value(value, type_id, count, "II")
        entries.append((tag, type_id, count, value))
    if len({entry[0] for entry in entries}) != len(entries):
        raise ValueError(f"{key} contains duplicate TIFF tags")
    return entries


def _row_bytes(raw: Any, endian: str) -> bytes:
    np = _numpy()
    if raw.dtype == np.uint8:
        return np.ascontiguousarray(raw, dtype=np.uint8).tobytes()
    if raw.dtype != np.uint16:
        raise ValueError("DNG raw samples must be uint8 or uint16")
    dtype = ">u2" if endian == "MM" else "<u2"
    return raw.astype(dtype, copy=False).tobytes(order="C")


def _pack_samples(raw: Any, bits: int, endian: str) -> bytes:
    np = _numpy()
    if not 1 <= bits <= 32:
        raise ValueError("packed DNG samples require 1..32-bit integer data")
    if bits <= 16 and raw.dtype not in (np.uint8, np.uint16):
        raise ValueError("packed DNG samples require 1..16-bit integer data")
    if bits > 16 and raw.dtype not in (np.uint16, np.uint32):
        raise ValueError("24/32-bit DNG samples require uint16 or uint32 input")
    if bits in (8, 16):
        if raw.size and int(np.max(raw)) >= (1 << bits):
            raise ValueError("DNG sample exceeds declared bit depth")
        dtype = np.uint8 if bits == 8 else np.uint16
        return _row_bytes(np.ascontiguousarray(raw, dtype=dtype), endian)
    if bits == 24:
        if raw.size and int(np.max(raw)) >= (1 << 24):
            raise ValueError("DNG sample exceeds declared 24-bit depth")
        codes = np.ascontiguousarray(raw, dtype=np.uint32)
        little = endian == "II"
        view = codes.astype("<u4" if little else ">u4", copy=False).view(np.uint8)
        view = np.ascontiguousarray(view).reshape(-1, 4)
        return (view[:, :3] if little else view[:, 1:]).tobytes()
    if bits == 32:
        return np.ascontiguousarray(raw, dtype=np.uint32).astype(
            "<u4" if endian == "II" else ">u4", copy=False
        ).tobytes()
    row_bits = raw.shape[1] * bits
    row_size = (row_bits + 7) // 8
    output = bytearray()
    for row in raw:
        accumulator = 0
        count = 0
        for value in row:
            integer = int(value)
            if integer < 0 or integer >= (1 << bits):
                raise ValueError("DNG sample exceeds declared bit depth")
            accumulator = (accumulator << bits) | integer
            count += bits
            while count >= 8:
                count -= 8
                output.append((accumulator >> count) & 255)
                accumulator &= (1 << count) - 1 if count else 0
        if count:
            output.append((accumulator << (8 - count)) & 255)
        if len(output) % row_size:
            raise AssertionError("packed DNG row size mismatch")
    return bytes(output)


def _jpeg_marker(code: int, payload: bytes = b"") -> bytes:
    """Build one ISO/IEC 10918 marker without relying on a JPEG library."""
    code = int(code)
    if not 0 <= code <= 255 or code in (0x00, 0xFF):
        raise ValueError("invalid JPEG marker code")
    if not payload:
        return bytes((0xFF, code))
    if len(payload) > 65533:
        raise ValueError("JPEG marker payload exceeds the 64 KiB limit")
    return b"\xff" + bytes((code,)) + struct.pack(">H", len(payload) + 2) + bytes(payload)


def _bounded_jpeg_huffman_lengths(frequencies, max_bits: int = 16) -> list[int]:
    """Return bounded canonical code lengths for a small JPEG alphabet.

    Lossless JPEG uses only the DC magnitude categories 0..16.  The synthetic
    leaf is retained while building the tree so no emitted symbol receives an
    all-ones codeword, as required by the JPEG Huffman construction.  This is
    the same bounded-tree rule used by the maintained baseline JPEG path, kept
    local so importing the DNG container never initializes that encoder.
    """
    values = [int(value) for value in frequencies]
    active = [(value, symbol, symbol) for symbol, value in enumerate(values) if value > 0]
    lengths = [0] * len(values)
    if not active:
        lengths[0] = 1
        return lengths
    if len(active) == 1:
        lengths[active[0][2]] = 1
        return lengths
    heapq.heapify(active)
    nodes: dict[int, tuple[int, int]] = {}
    next_node = len(values)
    order = len(values)
    while len(active) > 1:
        left = heapq.heappop(active)
        right = heapq.heappop(active)
        nodes[next_node] = (left[2], right[2])
        heapq.heappush(active, (left[0] + right[0], order, next_node))
        order += 1
        next_node += 1
    stack = [(active[0][2], 0)]
    while stack:
        node, depth = stack.pop()
        if node < len(values):
            lengths[node] = max(1, depth)
        else:
            left, right = nodes[node]
            stack.extend(((left, depth + 1), (right, depth + 1)))

    counts = [0] * (max(max(lengths), max_bits) + 1)
    for length in lengths:
        if length:
            counts[length] += 1
    # Merge pairs of overlong leaves and split a shallower leaf.  Both
    # operations preserve Kraft equality and leaf count, unlike clamping
    # lengths before repairing the tree.
    for length in range(len(counts) - 1, max_bits, -1):
        while counts[length] > 0:
            if counts[length] < 2:
                raise ValueError("unable to bound lossless JPEG Huffman tree")
            counts[length] -= 2
            counts[length - 1] += 1
            split = length - 2
            while split > 0 and counts[split] == 0:
                split -= 1
            if split == 0:
                raise ValueError("unable to bound lossless JPEG Huffman tree")
            counts[split] -= 1
            counts[split + 1] += 2

    ordered = sorted(
        (symbol for symbol, value in enumerate(values) if value > 0),
        key=lambda symbol: (values[symbol], symbol),
    )
    cursor = 0
    for length in range(max_bits, 0, -1):
        for _ in range(counts[length]):
            if cursor >= len(ordered):
                raise ValueError("invalid bounded lossless JPEG Huffman histogram")
            lengths[ordered[cursor]] = length
            cursor += 1
    if cursor != len(ordered):
        raise ValueError("incomplete bounded lossless JPEG Huffman histogram")
    return lengths


def _lossless_jpeg_huffman_table(frequencies, mode: str = "optimized"):
    """Return ``symbol -> (code, length)`` and one DC DHT marker."""
    mode = str(mode).strip().lower()
    if mode not in {"standard", "optimized"}:
        raise ValueError("jpeg_huffman must be standard or optimized")
    if len(frequencies) != 17:
        raise ValueError("lossless JPEG needs 17 magnitude categories")
    if mode == "standard":
        lengths = [4, 4] + [5] * 15
    else:
        # JPEG's pseudo-leaf is not serialized.  Give every real category a
        # count of at least one, matching the DNG SDK's safe small-alphabet
        # construction and avoiding one-symbol Huffman tables on flat raws.
        working = [max(1, int(value)) for value in frequencies] + [1]
        lengths = _bounded_jpeg_huffman_lengths(working)[:17]
    ordered = sorted(range(17), key=lambda symbol: (lengths[symbol], symbol))
    codes: dict[int, tuple[int, int]] = {}
    code = 0
    previous = 0
    for symbol in ordered:
        length = int(lengths[symbol])
        code <<= length - previous
        if code >= (1 << length):
            raise ValueError("lossless JPEG Huffman code is overfull")
        codes[symbol] = (code, length)
        code += 1
        previous = length
    bits = tuple(sum(1 for symbol in ordered if lengths[symbol] == length) for length in range(1, 17))
    values = tuple(ordered)
    dht_payload = bytes((0,)) + bytes(bits) + bytes(values)
    return codes, _jpeg_marker(0xC4, dht_payload)


def _lossless_jpeg_delta(sample: int, predictor: int) -> int:
    """DNG's signed-16 modulo difference used by the JPEG lossless path."""
    return ((int(sample) - int(predictor) + 32768) & 0xFFFF) - 32768


def _lossless_jpeg_prediction(samples: Any, row: int, column: int, selection: int, initial: int) -> int:
    """Return the T.81 predictor, including the mandatory image-edge rules."""
    if row == 0:
        return initial if column == 0 else int(samples[row, column - 1])
    if column == 0:
        return int(samples[row - 1, column])
    left = int(samples[row, column - 1])
    upper = int(samples[row - 1, column])
    diagonal = int(samples[row - 1, column - 1])
    if selection == 1:
        return left
    if selection == 2:
        return upper
    if selection == 3:
        return diagonal
    if selection == 4:
        return left + upper - diagonal
    if selection == 5:
        return left + ((upper - diagonal) // 2)
    if selection == 6:
        return upper + ((left - diagonal) // 2)
    if selection == 7:
        return (left + upper) // 2
    raise ValueError("lossless JPEG predictor selection must be 1..7")


def _iter_lossless_jpeg_deltas(samples: Any, selection: int, precision: int):
    initial = 1 << (precision - 1)
    for row in range(samples.shape[0]):
        for column in range(samples.shape[1]):
            prediction = _lossless_jpeg_prediction(samples, row, column, selection, initial)
            yield _lossless_jpeg_delta(int(samples[row, column]), prediction)


def _lossless_jpeg_payload(samples: Any, precision: int, selection: int, huffman: str) -> bytes:
    """Encode one complete single-component SOF3 JPEG datastream."""
    np = _numpy()
    data = np.asarray(samples)
    if data.ndim != 2 or data.dtype not in (np.uint8, np.uint16):
        raise ValueError("lossless JPEG samples must be a 2D uint8 or uint16 array")
    height, width = map(int, data.shape)
    precision = int(precision)
    selection = int(selection)
    if not 2 <= precision <= 16 or height <= 0 or width <= 0:
        raise ValueError("lossless JPEG precision or geometry is invalid")
    if height > 65535 or width > 65535:
        raise ValueError("lossless JPEG dimensions must fit 16-bit JPEG fields")
    if selection not in range(1, 8):
        raise ValueError("lossless JPEG predictor selection must be 1..7")
    if data.size and int(np.max(data)) >= (1 << precision):
        raise ValueError("DNG sample exceeds the lossless JPEG precision")

    frequencies = [0] * 17
    for delta in _iter_lossless_jpeg_deltas(data, selection, precision):
        category = abs(int(delta)).bit_length()
        if category > 16:
            raise ValueError("lossless JPEG difference exceeds 16 bits")
        frequencies[category] += 1
    codes, dht = _lossless_jpeg_huffman_table(frequencies, huffman)

    writer = BitWriter()
    for delta in _iter_lossless_jpeg_deltas(data, selection, precision):
        category = abs(int(delta)).bit_length()
        code, code_length = codes[category]
        writer.write(code, code_length)
        # ISO lossless JPEG gives the 16-bit negative half-range value a
        # special representation: category 16 and no amplitude bits.
        if category and delta != -32768:
            amplitude = int(delta) if delta >= 0 else int(delta) + (1 << category) - 1
            writer.write(amplitude, category)
    entropy = writer.finish(fill=1)
    stuffed = bytearray()
    for value in entropy:
        stuffed.append(value)
        if value == 0xFF:
            stuffed.append(0)

    sof_payload = bytes((precision,)) + struct.pack(">HH", height, width) + bytes((1, 0, 0x11, 0))
    sos_payload = bytes((1, 0, 0, selection, 0, 0))
    return b"\xff\xd8" + _jpeg_marker(0xC3, sof_payload) + dht + _jpeg_marker(0xDA, sos_payload) + bytes(stuffed) + b"\xff\xd9"


def _packbits_rows(raw_bytes: bytes, row_size: int, height: int) -> bytes:
    return b"".join(packbits_encode(raw_bytes[y * row_size:(y + 1) * row_size]) for y in range(height))


def _byte_buffer(value: bytes | bytearray | memoryview, name: str) -> bytes:
    if not isinstance(value, (bytes, bytearray, memoryview)):
        raise TypeError(f"{name} must be bytes, bytearray, or memoryview")
    try:
        return bytes(memoryview(value).cast("B"))
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must be a contiguous byte buffer") from exc


def _packed_row_values(row: bytes, width: int, bits: int, endian: str = "II") -> list[int]:
    width, bits = int(width), int(bits)
    expected = (width * bits + 7) // 8
    if width <= 0 or not 1 <= bits <= 16 or len(row) != expected:
        raise ValueError("packed DNG row length or geometry is invalid")
    if bits == 8:
        return list(row)
    if bits == 16:
        code = "<" if endian == "II" else ">"
        return list(struct.unpack(code + f"{width}H", row))
    values: list[int] = []
    accumulator = 0
    available = 0
    position = 0
    mask = (1 << bits) - 1
    for _ in range(width):
        while available < bits:
            accumulator = (accumulator << 8) | row[position]
            position += 1
            available += 8
        available -= bits
        values.append((accumulator >> available) & mask)
        accumulator &= (1 << available) - 1 if available else 0
    if available and accumulator:
        raise ValueError("packed DNG row has nonzero padding bits")
    return values


def _pack_integer_row(values: list[int], bits: int, endian: str = "II") -> bytes:
    bits = int(bits)
    if not 1 <= bits <= 16:
        raise ValueError("bits_per_sample must be between 1 and 16")
    limit = 1 << bits
    integers = [int(value) for value in values]
    if any(value < 0 or value >= limit for value in integers):
        raise ValueError("DNG sample exceeds declared bit depth")
    if bits == 8:
        return bytes(integers)
    if bits == 16:
        code = "<" if endian == "II" else ">"
        return struct.pack(code + f"{len(integers)}H", *integers)
    output = bytearray()
    accumulator = 0
    available = 0
    for value in integers:
        accumulator = (accumulator << bits) | value
        available += bits
        while available >= 8:
            available -= 8
            output.append((accumulator >> available) & 255)
            accumulator &= (1 << available) - 1 if available else 0
    if available:
        output.append((accumulator << (8 - available)) & 255)
    return bytes(output)


def _horizontal_predict_packed(
    payload: bytes,
    width: int,
    height: int,
    bits: int,
    *,
    inverse: bool,
    endian: str = "II",
) -> bytes:
    row_size = (int(width) * int(bits) + 7) // 8
    if len(payload) != row_size * int(height):
        raise ValueError("DNG sample payload length or geometry is invalid")
    modulus = 1 << int(bits)
    output = bytearray()
    for row_index in range(int(height)):
        start = row_index * row_size
        values = _packed_row_values(payload[start:start + row_size], width, bits, endian)
        if inverse:
            running = 0
            transformed = []
            for value in values:
                running = (running + value) % modulus
                transformed.append(running)
        else:
            previous = 0
            transformed = []
            for value in values:
                transformed.append((value - previous) % modulus)
                previous = value
        output.extend(_pack_integer_row(transformed, bits, endian))
    return bytes(output)


def _delta_samples(data: Any, inverse: bool = False, bit_depth: int | None = None) -> Any:
    np = _numpy()
    modulus = 1 << (bit_depth or (8 * data.dtype.itemsize))
    graph = "compression_dng_undelta_rows" if inverse else "compression_dng_delta_rows"
    try:
        # Keep the container writer dependency-free.  Importing the AOT
        # dispatcher here would initialize a GPU context merely by importing
        # the writer; predictor paths are the only callers that need it.
        from taichi_vision.taichi_algorithm.aot_api.research import _dispatch

        result = _dispatch(
            "compression_image",
            graph,
            inputs={"src": np.ascontiguousarray(data, dtype=np.int32)},
            outputs={"dst": np.empty(data.shape, dtype=np.int32)},
            scalars={"height": data.shape[0], "width": data.shape[1], "modulus": modulus},
            plain_ndarray=False,
        )
        array = result["dst"] if isinstance(result, dict) else result
        return np.asarray(array, dtype=np.int32).astype(data.dtype, copy=False)
    except Exception as exc:
        if os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") != "1":
            raise RuntimeError(
                f"{graph} is unavailable for the selected AOT target; compile the "
                "matching compression_image.tcm or set AOT_ALLOW_HOST_FALLBACK=1 "
                "for an explicit reference run"
            ) from exc
        output = np.empty_like(data)
        for y in range(data.shape[0]):
            running = 0
            for x in range(data.shape[1]):
                if inverse:
                    running = (running + int(data[y, x])) % modulus
                    output[y, x] = running
                else:
                    previous = int(data[y, x - 1]) if x else 0
                    output[y, x] = (int(data[y, x]) - previous) % modulus
        return output


def _encode_dng_array_legacy(raw, metadata: dict | None = None, compression: str = "packbits", predictor: str = "none", bits_per_sample: int | None = None) -> bytes:
    """Write a minimal interoperable mosaiced DNG without external codecs.

    ``compression="lossless_jpeg"`` writes TIFF/DNG Compression=7 using a
    complete single-component ISO SOF3 stream per strip.  The maintained
    profile is exact and intentionally bounded: JPEG predictor 1..7 and
    optimized/standard DC Huffman tables are available, while point
    transforms, restart markers, and multi-component interleaving are not
    emitted.
    """
    np = _numpy()
    data = np.asarray(raw)
    if data.ndim != 2 or data.dtype not in (np.uint8, np.uint16, np.uint32):
        raise ValueError("DNG raw input must be a 2D uint8, uint16, or uint32 array")
    compression = str(compression).strip().lower().replace("-", "_")
    if compression in {"jpeg", "jpeg_lossless", "losslessjpeg"}:
        compression = "lossless_jpeg"
    if compression in {"dynamic_deflate", "deflate_best"}:
        compression = "deflate_dynamic"
    if compression not in {"none", "packbits", "deflate", "deflate_dynamic", "lossless_jpeg"}:
        raise ValueError("supported DNG compression modes are none, packbits, deflate, deflate_dynamic, and lossless_jpeg")
    if predictor not in {"none", "horizontal"}:
        raise ValueError("predictor must be none or horizontal")
    metadata = dict(metadata or {})
    height, width = map(int, data.shape)
    bits = int(bits_per_sample or (8 if data.dtype == np.uint8 else 16))
    orientation = int(metadata.get("orientation", 1))
    if orientation not in range(1, 9):
        raise ValueError("orientation must be a TIFF orientation value from 1 to 8")
    if not 1 <= bits <= 32:
        raise ValueError("bits_per_sample must be between 1 and 32")
    if compression == "lossless_jpeg" and not 8 <= bits <= 16:
        raise ValueError("DNG Lossless JPEG requires 8..16-bit integer samples")
    if compression == "lossless_jpeg":
        jpeg_predictor = metadata.get("jpeg_predictor", 1)
        if isinstance(jpeg_predictor, str):
            aliases = {
                "left": 1,
                "horizontal": 1,
                "above": 2,
                "vertical": 2,
                "diagonal": 3,
                "paeth": 4,
                "jpeg1": 1,
                "jpeg2": 2,
                "jpeg3": 3,
                "jpeg4": 4,
                "jpeg5": 5,
                "jpeg6": 6,
                "jpeg7": 7,
            }
            try:
                jpeg_predictor = aliases[jpeg_predictor.strip().lower()]
            except KeyError as exc:
                raise ValueError("jpeg_predictor must be an integer 1..7 or a supported alias") from exc
        jpeg_predictor = int(jpeg_predictor)
        if jpeg_predictor not in range(1, 8):
            raise ValueError("jpeg_predictor must be between 1 and 7")
        jpeg_huffman = str(metadata.get("jpeg_huffman", "optimized")).strip().lower()
        if jpeg_huffman not in {"standard", "optimized"}:
            raise ValueError("jpeg_huffman must be standard or optimized")
        if "jpeg_point_transform" in metadata and int(metadata["jpeg_point_transform"]) != 0:
            raise ValueError("lossless DNG JPEG currently requires jpeg_point_transform=0")
        raw_bytes = None
    else:
        jpeg_predictor = 1
        jpeg_huffman = "optimized"
        encoded_samples = _delta_samples(data, inverse=False, bit_depth=bits) if predictor == "horizontal" else data
        raw_bytes = _pack_samples(encoded_samples, bits, "II")
    row_size = (width * bits + 7) // 8
    rows_per_strip = int(metadata.get("rows_per_strip", height))
    if not 1 <= rows_per_strip <= height:
        raise ValueError("rows_per_strip must be between 1 and image height")
    strips = []
    for first_row in range(0, height, rows_per_strip):
        strip_rows = min(rows_per_strip, height - first_row)
        if compression == "lossless_jpeg":
            strip = _lossless_jpeg_payload(
                data[first_row:first_row + strip_rows],
                bits,
                jpeg_predictor,
                jpeg_huffman,
            )
        else:
            strip_raw = raw_bytes[first_row * row_size:(first_row + strip_rows) * row_size]
        if compression == "none":
            strip = strip_raw
        elif compression == "packbits":
            strip = _packbits_rows(strip_raw, row_size, strip_rows)
        elif compression == "deflate":
            strip = deflate_fixed(strip_raw)
        elif compression == "deflate_dynamic":
            strip = deflate_dynamic(strip_raw)
        strips.append(strip)
    strip_counts = tuple(len(strip) for strip in strips)
    compression_tag = {
        "none": 1,
        "packbits": 32773,
        "deflate": 8,
        "deflate_dynamic": 8,
        "lossless_jpeg": 7,
    }[compression]
    cfa_values = tuple(int(x) for x in metadata.get("cfa_pattern", (1, 0, 0, 1)))
    if any(value < 0 or value > 255 for value in cfa_values):
        raise ValueError("cfa_pattern values must fit in one byte")
    cfa = cfa_values
    if len(cfa) != 4:
        raise ValueError("cfa_pattern must contain four byte values")
    black_level = int(metadata.get("black_level", 0))
    white_level = int(metadata.get("white_level", (1 << bits) - 1))
    if not 0 <= black_level <= 65535:
        raise ValueError("black_level must fit a TIFF SHORT")
    if not 0 <= white_level <= 0xFFFFFFFF:
        raise ValueError("white_level must fit a TIFF LONG")
    entries: list[tuple[int, int, int, object]] = [
        (254, 4, 1, 0),
        (256, 4, 1, width),
        (257, 4, 1, height),
        (258, 3, 1, bits),
        (259, 3, 1, compression_tag),
        (262, 3, 1, 32803),
        (266, 3, 1, 1),
        (273, 4, len(strips), tuple(0 for _ in strips)),
        # Derived images are written with their orientation baked into the
        # samples.  Emit the explicit identity tag so readers do not have to
        # guess whether an absent tag means "already oriented".
        (274, 3, 1, orientation),
        (277, 3, 1, 1),
        (278, 4, 1, rows_per_strip),
        (279, 4, len(strips), strip_counts),
        (284, 3, 1, 1),
        (296, 3, 1, 2),
        (33421, 3, 2, (2, 2)),
        (33422, 1, 4, bytes(cfa)),
        (50706, 1, 4, bytes((1, 7, 0, 0))),
        (50707, 1, 4, bytes((1, 7, 0, 0))),
        (50708, 2, len(str(metadata.get("camera_model", "Pixel Refine Native")).encode("ascii")) + 1, metadata.get("camera_model", "Pixel Refine Native")),
        (50714, 3, 1, black_level),
        (50717, 4, 1, white_level),
    ]
    if predictor == "horizontal":
        if compression == "lossless_jpeg":
            raise ValueError("TIFF horizontal predictor is not used with DNG Lossless JPEG; use jpeg_predictor")
        entries.append((317, 3, 1, 2))
    if compression == "lossless_jpeg":
        # The complete JPEG datastream carries its own DHT.  These legacy TIFF
        # fields are retained as truthful process metadata; no abbreviated
        # stream or external codec table is implied.
        entries.extend(
            (
                (512, 3, 1, 14),
                (515, 3, 1, 0),
                (517, 3, 1, jpeg_predictor),
                (518, 3, 1, 0),
            )
        )
    if "make" in metadata:
        make = str(metadata["make"])
        entries.append((271, 2, len(make.encode("ascii")) + 1, make))
    if "model" in metadata:
        model = str(metadata["model"])
        entries.append((272, 2, len(model.encode("ascii")) + 1, model))
    if "xmp" in metadata:
        xmp = bytes(metadata["xmp"])
        entries.append((700, 7, len(xmp), xmp))
    ifd0_entries = _metadata_ifd_entries(metadata, "ifd0_tags")
    reserved_tags = {entry[0] for entry in entries}
    collisions = reserved_tags.intersection(entry[0] for entry in ifd0_entries)
    if collisions:
        raise ValueError(f"ifd0_tags cannot replace native layout tags: {sorted(collisions)}")
    entries.extend(ifd0_entries)
    extra_entries = _metadata_ifd_entries(metadata, "dng_extra_tags")
    reserved_tags = {entry[0] for entry in entries}
    collisions = reserved_tags.intersection(entry[0] for entry in extra_entries)
    if collisions:
        raise ValueError(f"dng_extra_tags cannot replace native layout tags: {sorted(collisions)}")
    entries.extend(extra_entries)
    exif_entries = _metadata_ifd_entries(metadata, "exif_tags")
    gps_entries = _metadata_ifd_entries(metadata, "gps_tags")
    if exif_entries:
        entries.append((34665, 4, 1, 0))  # patched after its IFD is laid out
    if gps_entries:
        entries.append((34853, 4, 1, 0))  # patched after its IFD is laid out
    entries.sort(key=lambda item: item[0])
    ifd_offset = 8
    # Build the root IFD once with a placeholder Exif pointer.  The pointer is
    # inline, so replacing it does not change layout.
    provisional = _build_ifd(entries, ifd_offset, tuple(0 for _ in strips), "II")
    exif_offset = ifd_offset + len(provisional)
    if exif_offset & 1:
        exif_offset += 1
    exif_directory = _build_ifd(exif_entries, exif_offset, (), "II") if exif_entries else b""
    gps_offset = exif_offset + len(exif_directory)
    if gps_offset & 1:
        gps_offset += 1
    gps_directory = _build_ifd(gps_entries, gps_offset, (), "II") if gps_entries else b""
    strip_offset = gps_offset + len(gps_directory)
    if strip_offset & 1:
        strip_offset += 1
    strip_offsets = []
    cursor = strip_offset
    for strip in strips:
        strip_offsets.append(cursor)
        cursor += len(strip)
    if exif_entries:
        entries = [
            (tag, type_id, count, exif_offset if tag == 34665 else value)
            for tag, type_id, count, value in entries
        ]
    if gps_entries:
        entries = [
            (tag, type_id, count, gps_offset if tag == 34853 else value)
            for tag, type_id, count, value in entries
        ]
    directory = _build_ifd(entries, ifd_offset, tuple(strip_offsets), "II")
    output = bytearray(b"II" + struct.pack("<H", 42) + struct.pack("<I", ifd_offset))
    output.extend(directory)
    while len(output) < exif_offset:
        output.append(0)
    output.extend(exif_directory)
    while len(output) < gps_offset:
        output.append(0)
    output.extend(gps_directory)
    while len(output) < strip_offset:
        output.append(0)
    for strip in strips:
        output.extend(strip)
    return bytes(output)


def encode_dng_bytes(
    raw: bytes | bytearray | memoryview,
    *,
    width: int,
    height: int,
    bits_per_sample: int,
    metadata: dict | None = None,
    compression: str = "packbits",
    predictor: str = "none",
) -> bytes:
    """Encode tightly packed CFA rows without importing NumPy.

    The byte ABI matches TIFF/DNG strip sample packing: 8-bit samples are one
    byte each, 16-bit samples are little-endian unsigned words, and other bit
    depths are packed most-significant-bit first with each row byte-aligned.
    ``none``, row-bounded ``PackBits``, and dependency-free fixed- or
    dynamic-Huffman LZ77 ``Deflate`` are supported.  Lossless JPEG remains on
    the ndarray compatibility path.
    """
    width, height, bits = int(width), int(height), int(bits_per_sample)
    if width <= 0 or height <= 0 or width > 0xFFFFFFFF or height > 0xFFFFFFFF:
        raise ValueError("DNG width and height must fit positive TIFF LONG values")
    if not 1 <= bits <= 32:
        raise ValueError("bits_per_sample must be between 1 and 32")
    compression = str(compression).strip().lower().replace("-", "_")
    if compression in {"jpeg", "jpeg_lossless", "losslessjpeg", "lossless_jpeg"}:
        raise ValueError(
            "the NumPy-free byte API supports none, packbits, deflate, and deflate_dynamic; "
            "lossless JPEG remains on encode_dng_aot ndarray input"
        )
    if compression in {"dynamic_deflate", "deflate_best"}:
        compression = "deflate_dynamic"
    if compression not in {"none", "packbits", "deflate", "deflate_dynamic"}:
        raise ValueError("supported byte-API DNG compression modes are none, packbits, deflate, and deflate_dynamic")
    predictor = str(predictor).strip().lower()
    if predictor not in {"none", "horizontal"}:
        raise ValueError("predictor must be none or horizontal")

    metadata = dict(metadata or {})
    orientation = int(metadata.get("orientation", 1))
    if orientation not in range(1, 9):
        raise ValueError("orientation must be a TIFF orientation value from 1 to 8")
    row_size = (width * bits + 7) // 8
    packed = _byte_buffer(raw, "raw")
    if len(packed) != row_size * height:
        raise ValueError("packed DNG byte input length does not match width, height, and bit depth")
    # Validate row padding even when no predictor is requested.  Canonical
    # zero padding prevents two byte streams from representing the same CFA.
    for row_index in range(height):
        start = row_index * row_size
        _packed_row_values(packed[start:start + row_size], width, bits, "II")
    if predictor == "horizontal":
        packed = _horizontal_predict_packed(
            packed, width, height, bits, inverse=False, endian="II"
        )

    rows_per_strip = int(metadata.get("rows_per_strip", height))
    if not 1 <= rows_per_strip <= height:
        raise ValueError("rows_per_strip must be between 1 and image height")
    strips: list[bytes] = []
    for first_row in range(0, height, rows_per_strip):
        strip_rows = min(rows_per_strip, height - first_row)
        strip_raw = packed[first_row * row_size:(first_row + strip_rows) * row_size]
        if compression == "none":
            strip = strip_raw
        elif compression == "packbits":
            strip = _packbits_rows(strip_raw, row_size, strip_rows)
        elif compression == "deflate":
            strip = deflate_fixed(strip_raw)
        else:
            strip = deflate_dynamic(strip_raw)
        strips.append(strip)

    cfa = tuple(int(value) for value in metadata.get("cfa_pattern", (1, 0, 0, 1)))
    if len(cfa) != 4 or any(value < 0 or value > 255 for value in cfa):
        raise ValueError("cfa_pattern must contain four byte values")
    black_level = int(metadata.get("black_level", 0))
    white_level = int(metadata.get("white_level", (1 << bits) - 1))
    if not 0 <= black_level <= 65535:
        raise ValueError("black_level must fit a TIFF SHORT")
    if not 0 <= white_level <= 0xFFFFFFFF:
        raise ValueError("white_level must fit a TIFF LONG")
    camera_model = str(metadata.get("camera_model", "Pixel Refine Native"))
    camera_model_count = len(camera_model.encode("ascii")) + 1
    strip_counts = tuple(len(strip) for strip in strips)
    entries: list[tuple[int, int, int, object]] = [
        (254, 4, 1, 0),
        (256, 4, 1, width),
        (257, 4, 1, height),
        (258, 3, 1, bits),
        (259, 3, 1, {"none": 1, "deflate": 8, "deflate_dynamic": 8, "packbits": 32773}[compression]),
        (262, 3, 1, 32803),
        (266, 3, 1, 1),
        (273, 4, len(strips), tuple(0 for _ in strips)),
        (277, 3, 1, 1),
        (278, 4, 1, rows_per_strip),
        (279, 4, len(strips), strip_counts),
        (284, 3, 1, 1),
        (296, 3, 1, 2),
        (33421, 3, 2, (2, 2)),
        (33422, 1, 4, bytes(cfa)),
        (50706, 1, 4, bytes((1, 7, 0, 0))),
        (50707, 1, 4, bytes((1, 7, 0, 0))),
        (50708, 2, camera_model_count, camera_model),
        (50714, 3, 1, black_level),
        (50717, 4, 1, white_level),
        (274, 3, 1, orientation),
    ]
    if predictor == "horizontal":
        entries.append((317, 3, 1, 2))
    for tag, key in ((271, "make"), (272, "model")):
        if key in metadata:
            text = str(metadata[key])
            entries.append((tag, 2, len(text.encode("ascii")) + 1, text))
    if "xmp" in metadata:
        xmp = _byte_buffer(metadata["xmp"], "xmp")
        entries.append((700, 7, len(xmp), xmp))
    ifd0_entries = _metadata_ifd_entries(metadata, "ifd0_tags")
    reserved_tags = {entry[0] for entry in entries}
    collisions = reserved_tags.intersection(entry[0] for entry in ifd0_entries)
    if collisions:
        raise ValueError(f"ifd0_tags cannot replace native layout tags: {sorted(collisions)}")
    entries.extend(ifd0_entries)
    entries.sort(key=lambda item: item[0])

    ifd_offset = 8
    provisional = _build_ifd(entries, ifd_offset, tuple(0 for _ in strips), "II")
    strip_offset = ifd_offset + len(provisional)
    if strip_offset & 1:
        strip_offset += 1
    strip_offsets: list[int] = []
    cursor = strip_offset
    for strip in strips:
        strip_offsets.append(cursor)
        cursor += len(strip)
        if cursor > 0xFFFFFFFF:
            raise ValueError("classic TIFF/DNG output exceeds the 4 GiB offset limit")
    directory = _build_ifd(entries, ifd_offset, tuple(strip_offsets), "II")
    output = bytearray(b"II" + struct.pack("<H", 42) + struct.pack("<I", ifd_offset))
    output.extend(directory)
    while len(output) < strip_offset:
        output.append(0)
    for strip in strips:
        output.extend(strip)
    return bytes(output)


def _rust_dng_writer():
    """Return the native writer functions when the Rust extension is present."""
    try:
        import taichi
    except ImportError:
        return None
    native = getattr(taichi, "taichi_python", None)
    if native is None:
        return None
    encode = getattr(native, "encode_dng", None)
    write = getattr(native, "write_dng", None)
    if encode is None or write is None:
        return None
    return encode, write


def _rust_dng_input(raw, *, bits_per_sample: int | None):
    np = _numpy()
    array = np.asarray(raw)
    if array.ndim != 2:
        raise ValueError("DNG raw input must be a 2D array")
    if array.dtype not in (np.uint8, np.uint16, np.uint32):
        raise ValueError("DNG raw input must use uint8, uint16, or uint32")
    if bits_per_sample is not None and not 1 <= int(bits_per_sample) <= 32:
        raise ValueError("bits_per_sample must be between 1 and 32")
    contiguous = np.ascontiguousarray(array)
    return memoryview(contiguous).cast("B"), int(contiguous.shape[1]), int(contiguous.shape[0]), str(contiguous.dtype)


def encode_dng_aot(
    raw,
    metadata: dict | None = None,
    compression: str = "lossless_jpeg",
    predictor: str = "none",
    bits_per_sample: int | None = None,
    *,
    width: int | None = None,
    height: int | None = None,
) -> bytes:
    """Encode ndarray-compatible input or dispatch a packed byte buffer."""
    if isinstance(raw, (bytes, bytearray, memoryview)):
        options = dict(metadata or {})
        resolved_width = width if width is not None else options.pop("width", None)
        resolved_height = height if height is not None else options.pop("height", None)
        resolved_bits = bits_per_sample
        if resolved_bits is None:
            resolved_bits = options.pop("bits_per_sample", None)
        if resolved_width is None or resolved_height is None or resolved_bits is None:
            raise ValueError(
                "packed byte input requires width, height, and bits_per_sample"
            )
        return encode_dng_bytes(
            raw,
            width=int(resolved_width),
            height=int(resolved_height),
            bits_per_sample=int(resolved_bits),
            metadata=options,
            compression=compression,
            predictor=predictor,
        )
    if width is not None or height is not None:
        raise ValueError("width and height are only valid for packed byte input")
    native = _rust_dng_writer()
    if native is not None:
        encode, _write = native
        buffer, resolved_width, resolved_height, dtype = _rust_dng_input(
            raw, bits_per_sample=bits_per_sample
        )
        return bytes(
            encode(
                buffer,
                resolved_width,
                resolved_height,
                dtype,
                dict(metadata or {}),
                str(compression),
                str(predictor),
                bits_per_sample,
            )
        )
    return _encode_dng_array_legacy(
        raw, metadata, compression, predictor, bits_per_sample
    )


def save_dng_aot(raw, path: str | os.PathLike[str], metadata: dict | None = None, compression: str = "lossless_jpeg", predictor: str = "none", bits_per_sample: int | None = None, *, width: int | None = None, height: int | None = None) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    native = _rust_dng_writer()
    if native is not None and not isinstance(raw, (bytes, bytearray, memoryview)):
        _encode, write = native
        buffer, resolved_width, resolved_height, dtype = _rust_dng_input(
            raw, bits_per_sample=bits_per_sample
        )
        write(
            str(target),
            buffer,
            resolved_width,
            resolved_height,
            dtype,
            dict(metadata or {}),
            str(compression),
            str(predictor),
            bits_per_sample,
        )
        return
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(
        encode_dng_aot(
            raw,
            metadata,
            compression,
            predictor,
            bits_per_sample,
            width=width,
            height=height,
        )
    )
    temporary.replace(target)


__all__ = [
    "encode_dng_bytes",
    "encode_dng_aot",
    "save_dng_aot",
]
