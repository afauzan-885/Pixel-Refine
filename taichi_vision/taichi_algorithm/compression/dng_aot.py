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
    if not 1 <= bits <= 16 or raw.dtype not in (np.uint8, np.uint16):
        raise ValueError("packed DNG samples require 1..16-bit integer data")
    if bits in (8, 16):
        if raw.size and int(np.max(raw)) >= (1 << bits):
            raise ValueError("DNG sample exceeds declared bit depth")
        return _row_bytes(raw, endian)
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


class _LosslessJpegBitReader:
    __slots__ = ("data", "offset")

    def __init__(self, data: bytes):
        self.data = memoryview(data).cast("B")
        self.offset = 0

    def read(self, count: int) -> int:
        count = int(count)
        if count < 0 or count > 16 or self.offset + count > len(self.data) * 8:
            raise ValueError("truncated lossless JPEG entropy data")
        value = 0
        for _ in range(count):
            byte_index, bit_index = divmod(self.offset, 8)
            value = (value << 1) | ((int(self.data[byte_index]) >> (7 - bit_index)) & 1)
            self.offset += 1
        return value

    @property
    def remaining(self) -> int:
        return len(self.data) * 8 - self.offset


def _parse_lossless_jpeg_huffman(payload: bytes, tables: dict[int, dict[tuple[int, int], int]]) -> None:
    cursor = 0
    while cursor < len(payload):
        if cursor + 17 > len(payload):
            raise ValueError("truncated lossless JPEG DHT marker")
        table_spec = payload[cursor]
        cursor += 1
        table_class, table_id = table_spec >> 4, table_spec & 15
        if table_class != 0 or table_id > 3 or table_id in tables:
            raise ValueError("unsupported or duplicate lossless JPEG Huffman table")
        counts = tuple(int(value) for value in payload[cursor:cursor + 16])
        cursor += 16
        total = sum(counts)
        if total <= 0 or total > 256 or cursor + total > len(payload):
            raise ValueError("invalid lossless JPEG Huffman table size")
        values = payload[cursor:cursor + total]
        cursor += total
        table: dict[tuple[int, int], int] = {}
        code = 0
        for length, count in enumerate(counts, 1):
            for value in values[sum(counts[:length - 1]) : sum(counts[:length - 1]) + count]:
                if code >= (1 << length):
                    raise ValueError("overfull lossless JPEG Huffman table")
                key = (length, code)
                if key in table:
                    raise ValueError("duplicate lossless JPEG Huffman code")
                table[key] = int(value)
                code += 1
            code <<= 1
        tables[table_id] = table
    if cursor != len(payload):
        raise ValueError("lossless JPEG DHT marker has trailing bytes")


def _lossless_jpeg_huffman_decode(reader: _LosslessJpegBitReader, table: dict[tuple[int, int], int]) -> int:
    code = 0
    for length in range(1, 17):
        code = (code << 1) | reader.read(1)
        symbol = table.get((length, code))
        if symbol is not None:
            return int(symbol)
    raise ValueError("invalid lossless JPEG Huffman code")


def _lossless_jpeg_payload_decode(
    payload: bytes,
    expected_samples: int,
    expected_precision: int | None = None,
) -> Any:
    """Decode the maintained one-component T.81 process-14 profile."""
    np = _numpy()
    data = bytes(payload)
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("lossless JPEG strip must start with SOI")
    position = 2
    frame = None
    scan = None
    tables: dict[int, dict[tuple[int, int], int]] = {}
    restart_interval = 0
    entropy_start = None
    while position < len(data):
        if data[position] != 0xFF:
            raise ValueError("invalid lossless JPEG marker alignment")
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            raise ValueError("truncated lossless JPEG marker")
        marker = data[position]
        position += 1
        if marker == 0x00:
            raise ValueError("stuffed byte outside lossless JPEG entropy data")
        if marker == 0xD9:
            raise ValueError("lossless JPEG EOI appeared before SOS")
        if marker in range(0xD0, 0xD8) or marker == 0x01:
            raise ValueError("unexpected standalone marker in lossless JPEG header")
        if position + 2 > len(data):
            raise ValueError("truncated lossless JPEG marker length")
        segment_length = struct.unpack_from(">H", data, position)[0]
        if segment_length < 2 or position + segment_length > len(data):
            raise ValueError("lossless JPEG marker length is out of bounds")
        segment = data[position + 2 : position + segment_length]
        position += segment_length
        if marker == 0xC3:
            if frame is not None or len(segment) < 6:
                raise ValueError("invalid or duplicate lossless JPEG SOF3")
            precision = int(segment[0])
            height, width = struct.unpack_from(">HH", segment, 1)
            components = int(segment[5])
            if not 2 <= precision <= 16 or width <= 0 or height <= 0 or components != 1:
                raise ValueError("only one-component SOF3 lossless JPEG is supported")
            if len(segment) != 6 + components * 3:
                raise ValueError("lossless JPEG SOF3 length is invalid")
            component_id, sampling, table_id = segment[6:9]
            if sampling != 0x11 or table_id != 0:
                raise ValueError("subsampled lossless JPEG components are unsupported")
            frame = (precision, int(width), int(height), int(component_id))
        elif marker == 0xC4:
            _parse_lossless_jpeg_huffman(segment, tables)
        elif marker == 0xDD:
            if len(segment) != 2:
                raise ValueError("invalid lossless JPEG restart interval marker")
            restart_interval = struct.unpack(">H", segment)[0]
        elif marker == 0xDA:
            if scan is not None or len(segment) != 6 or frame is None:
                raise ValueError("invalid or duplicate lossless JPEG SOS")
            components, component_id, table_spec, selection, spectral_end, point = segment
            if components != 1 or component_id != frame[3] or table_spec & 0x0F != 0:
                raise ValueError("lossless JPEG SOS component/table is unsupported")
            if selection not in range(1, 8) or spectral_end != 0 or point != 0:
                raise ValueError("lossless JPEG predictor or point transform is unsupported")
            scan = (int(selection), int(table_spec >> 4))
            entropy_start = position
            break
        elif marker in (0xC0, 0xC1, 0xC2, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            raise ValueError("lossy or arithmetic JPEG frame in a lossless DNG strip")

    if frame is None or scan is None or entropy_start is None:
        raise ValueError("lossless JPEG strip is missing SOF3 or SOS")
    precision, width, height, _component_id = frame
    if restart_interval:
        raise ValueError("lossless JPEG restart markers are not yet supported")
    if expected_samples <= 0 or width * height != int(expected_samples):
        raise ValueError("lossless JPEG sample count does not match the TIFF strip")
    if expected_precision is not None and precision != int(expected_precision):
        raise ValueError("lossless JPEG precision does not match the TIFF bit depth")
    if scan[1] not in tables:
        raise ValueError("lossless JPEG SOS references a missing Huffman table")

    entropy = bytearray()
    position = entropy_start
    while position < len(data):
        value = data[position]
        position += 1
        if value != 0xFF:
            entropy.append(value)
            continue
        if position >= len(data):
            raise ValueError("truncated lossless JPEG entropy marker")
        marker = data[position]
        position += 1
        while marker == 0xFF:
            if position >= len(data):
                raise ValueError("truncated lossless JPEG fill marker")
            marker = data[position]
            position += 1
        if marker == 0x00:
            entropy.append(0xFF)
        elif marker == 0xD9:
            if position != len(data):
                raise ValueError("trailing bytes after lossless JPEG EOI")
            break
        elif marker in range(0xD0, 0xD8):
            raise ValueError("lossless JPEG restart markers are not yet supported")
        else:
            raise ValueError("unexpected marker inside lossless JPEG entropy data")
    else:
        raise ValueError("lossless JPEG strip is missing EOI")

    reader = _LosslessJpegBitReader(bytes(entropy))
    output = np.empty(int(expected_samples), dtype=np.uint16)
    selection = scan[0]
    initial = 1 << (precision - 1)
    mask = (1 << precision) - 1
    for index in range(int(expected_samples)):
        row, column = divmod(index, width)
        if row == 0:
            prediction = initial if column == 0 else int(output[index - 1])
        elif column == 0:
            prediction = int(output[index - width])
        else:
            left = int(output[index - 1])
            upper = int(output[index - width])
            diagonal = int(output[index - width - 1])
            if selection == 1:
                prediction = left
            elif selection == 2:
                prediction = upper
            elif selection == 3:
                prediction = diagonal
            elif selection == 4:
                prediction = left + upper - diagonal
            elif selection == 5:
                prediction = left + ((upper - diagonal) // 2)
            elif selection == 6:
                prediction = upper + ((left - diagonal) // 2)
            else:
                prediction = (left + upper) // 2
        category = _lossless_jpeg_huffman_decode(reader, tables[scan[1]])
        if category < 0 or category > 16:
            raise ValueError("lossless JPEG difference category exceeds the JPEG limit")
        if category == 0:
            delta = 0
        elif category == 16:
            delta = -32768
        else:
            amplitude = reader.read(category)
            delta = amplitude if amplitude >= (1 << (category - 1)) else amplitude - ((1 << category) - 1)
        value = prediction + int(delta)
        if not 0 <= value <= mask:
            value &= mask
        output[index] = value
    if reader.remaining > 7:
        raise ValueError("lossless JPEG entropy has excess data")
    while reader.remaining:
        if reader.read(1) != 1:
            raise ValueError("lossless JPEG entropy padding is not all ones")
    return output


def _unpack_packed_row(raw: bytes, width: int, bits: int) -> Any:
    """Vectorized unpack for the common packed Bayer widths.

    DNG 10/12/14-bit sensors are frequent in camera files.  The old scalar
    decoder was exact but performed one Python loop per sensor code, making a
    tiled 12MP read prohibitively slow.  Decode complete byte groups with
    NumPy and retain a tiny scalar tail for odd row widths.
    """
    np = _numpy()
    if bits not in (10, 12, 14):
        raise ValueError("vectorized packed-row decode supports 10, 12, or 14 bits")
    samples_per_group = {10: 4, 12: 2, 14: 4}[bits]
    bytes_per_group = {10: 5, 12: 3, 14: 7}[bits]
    full_groups = int(width) // samples_per_group
    full_samples = full_groups * samples_per_group
    encoded = np.frombuffer(raw, dtype=np.uint8)
    output = np.empty(int(width), dtype=np.uint16)
    if full_groups:
        grouped = encoded[: full_groups * bytes_per_group].reshape(
            full_groups, bytes_per_group
        ).astype(np.uint16, copy=False)
        if bits == 10:
            decoded = np.stack(
                (
                    (grouped[:, 0] << 2) | (grouped[:, 1] >> 6),
                    ((grouped[:, 1] & 0x3F) << 4) | (grouped[:, 2] >> 4),
                    ((grouped[:, 2] & 0x0F) << 6) | (grouped[:, 3] >> 2),
                    ((grouped[:, 3] & 0x03) << 8) | grouped[:, 4],
                ),
                axis=1,
            )
        elif bits == 12:
            decoded = np.stack(
                (
                    (grouped[:, 0] << 4) | (grouped[:, 1] >> 4),
                    ((grouped[:, 1] & 0x0F) << 8) | grouped[:, 2],
                ),
                axis=1,
            )
        else:  # 14-bit, four samples in seven bytes
            decoded = np.stack(
                (
                    (grouped[:, 0] << 6) | (grouped[:, 1] >> 2),
                    ((grouped[:, 1] & 0x03) << 12)
                    | (grouped[:, 2] << 4)
                    | (grouped[:, 3] >> 4),
                    ((grouped[:, 3] & 0x0F) << 10)
                    | (grouped[:, 4] << 2)
                    | (grouped[:, 5] >> 6),
                    ((grouped[:, 5] & 0x3F) << 8) | grouped[:, 6],
                ),
                axis=1,
            )
        output[:full_samples] = decoded.reshape(-1)
    remaining = int(width) - full_samples
    if remaining:
        position = full_groups * bytes_per_group
        accumulator = 0
        available = 0
        for index in range(remaining):
            while available < bits:
                if position >= encoded.size:
                    raise ValueError("packed DNG row is truncated")
                accumulator = (accumulator << 8) | int(encoded[position])
                position += 1
                available += 8
            available -= bits
            output[full_samples + index] = (accumulator >> available) & ((1 << bits) - 1)
            accumulator &= (1 << available) - 1 if available else 0
    return output


def _unpack_packed_row_region(
    raw: bytes,
    width: int,
    bits: int,
    x0: int,
    x1: int,
) -> Any:
    """Decode only the packed groups intersecting ``[x0, x1)``."""
    if bits not in (10, 12, 14) or (x0 == 0 and x1 == width):
        return _unpack_packed_row(raw, width, bits)[x0:x1]
    samples_per_group = {10: 4, 12: 2, 14: 4}[bits]
    bytes_per_group = {10: 5, 12: 3, 14: 7}[bits]
    group_start = x0 // samples_per_group
    group_end = min(
        (x1 + samples_per_group - 1) // samples_per_group,
        (width + samples_per_group - 1) // samples_per_group,
    )
    group_width = min(width, group_end * samples_per_group) - group_start * samples_per_group
    byte_start = group_start * bytes_per_group
    byte_end = byte_start + (group_width * bits + 7) // 8
    decoded = _unpack_packed_row(raw[byte_start:byte_end], group_width, bits)
    local_start = x0 - group_start * samples_per_group
    local_end = local_start + (x1 - x0)
    return decoded[local_start:local_end]


def _unpack_samples(raw: bytes, width: int, height: int, bits: int, endian: str = "II") -> Any:
    np = _numpy()
    expected = height * ((width * bits + 7) // 8)
    if width <= 0 or height <= 0 or not 1 <= bits <= 16 or len(raw) != expected:
        raise ValueError("DNG sample payload length or geometry is invalid")
    if bits == 8:
        return np.frombuffer(raw, dtype=np.uint8).reshape(height, width).copy()
    if bits == 16:
        dtype = ">u2" if endian == "MM" else "<u2"
        return np.frombuffer(raw, dtype=dtype).reshape(height, width).copy()
    row_size = (width * bits + 7) // 8
    output = np.empty((height, width), dtype=np.uint16)
    for y in range(height):
        row = raw[y * row_size:(y + 1) * row_size]
        if bits in (10, 12, 14):
            output[y] = _unpack_packed_row(row, width, bits)
            continue
        accumulator = 0
        available = 0
        position = 0
        for x in range(width):
            while available < bits:
                accumulator = (accumulator << 8) | row[position]
                position += 1
                available += 8
            available -= bits
            output[y, x] = (accumulator >> available) & ((1 << bits) - 1)
            accumulator &= (1 << available) - 1 if available else 0
    return output


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
        # Keep the container parser dependency-free.  Importing the AOT
        # dispatcher here would initialize a GPU context merely by importing
        # ``read_dng_aot``; predictor paths are the only callers that need it.
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


@dataclass(frozen=True)
class DNGFrame:
    width: int
    height: int
    bits_per_sample: int
    compression: int
    tags: dict[int, object]
    raw_bytes: bytes
    endian: str = "II"

    def raw_view(self) -> memoryview:
        """Return a zero-copy, read-only view of the decoded packed CFA rows."""
        return memoryview(self.raw_bytes)

    def samples(self) -> Any:
        """Materialize the complete sensor plane.

        ``sample_region`` is preferred by block/fusion callers because it
        avoids creating a second full-frame ndarray.  Keeping this method as
        the eager compatibility API is intentional: existing DNG callers
        expect a standalone native ``uint8``/``uint16`` array.
        """
        return _unpack_samples(
            self.raw_bytes, self.width, self.height, self.bits_per_sample, self.endian
        )

    def sample_region(
        self,
        y0: int,
        y1: int,
        x0: int,
        x1: int,
    ) -> Any:
        """Decode one sensor-domain region without demosaicing.

        The parser stores decoded strip rows in ``raw_bytes``.  This method
        decodes only the requested rows and columns, which lets RAW fusion
        stream tiles without materializing another full ``uint16`` frame.
        Packed 10/12/14-bit samples use the exact same row unpacker as the
        eager path, so bit depth and CFA samples remain lossless.
        """
        np = _numpy()
        y0, y1, x0, x1 = (int(y0), int(y1), int(x0), int(x1))
        if not (0 <= y0 <= y1 <= self.height and 0 <= x0 <= x1 <= self.width):
            raise ValueError("DNG sample region is outside the frame")
        if y0 == y1 or x0 == x1:
            dtype = np.uint8 if self.bits_per_sample <= 8 else np.uint16
            return np.empty((y1 - y0, x1 - x0), dtype=dtype)

        row_size = (self.width * self.bits_per_sample + 7) // 8
        output_dtype = np.uint8 if self.bits_per_sample <= 8 else np.uint16
        output = np.empty((y1 - y0, x1 - x0), dtype=output_dtype)
        for output_row, source_row in enumerate(range(y0, y1)):
            start = source_row * row_size
            row_bytes = self.raw_bytes[start : start + row_size]
            if len(row_bytes) != row_size:
                raise ValueError("decoded DNG sample row is truncated")
            if self.bits_per_sample == 8:
                row = np.frombuffer(row_bytes, dtype=np.uint8)
            elif self.bits_per_sample == 16:
                dtype = ">u2" if self.endian == "MM" else "<u2"
                row = np.frombuffer(row_bytes, dtype=dtype)
            else:
                # Decode one packed row only.  This avoids an HxW temporary
                # while retaining the parser's proven bit-order semantics.
                if self.bits_per_sample in (10, 12, 14):
                    row = _unpack_packed_row_region(
                        row_bytes,
                        self.width,
                        self.bits_per_sample,
                        x0,
                        x1,
                    )
                    output[output_row] = np.asarray(row, dtype=output_dtype)
                    continue
                row = _unpack_samples(
                    row_bytes, self.width, 1, self.bits_per_sample, self.endian
                )[0]
            output[output_row] = np.asarray(row[x0:x1], dtype=output_dtype)
        return output

    def iter_regions(
        self,
        block_size: int | tuple[int, int] = 512,
    ):
        """Yield ``(y0, y1, x0, x1, samples)`` sensor tiles.

        This is a small streaming primitive for pre-demosaic alignment and
        fusion.  It deliberately yields native integer samples and never
        applies white balance, normalization, or interpolation.
        """
        if isinstance(block_size, int):
            block_h = block_w = int(block_size)
        else:
            block_h, block_w = (int(block_size[0]), int(block_size[1]))
        if block_h <= 0 or block_w <= 0:
            raise ValueError("block_size must be positive")
        for y0 in range(0, self.height, block_h):
            y1 = min(self.height, y0 + block_h)
            for x0 in range(0, self.width, block_w):
                x1 = min(self.width, x0 + block_w)
                yield y0, y1, x0, x1, self.sample_region(y0, y1, x0, x1)

    def to_raw_frame(self, *, source_id: str = "", source_version: str = ""):
        """Adapt this container frame to the semantic pre-demosaic contract.

        The import is lazy to keep the container parser independent from the
        higher-level RAW pipeline and to avoid an import cycle during package
        startup.
        """
        from .raw_frame import RawMosaicFrame

        return RawMosaicFrame.from_dng(
            self, source_id=source_id, source_version=source_version
        )


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
    if data.ndim != 2 or data.dtype not in (np.uint8, np.uint16):
        raise ValueError("DNG raw input must be a 2D uint8 or uint16 array")
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
    if not 1 <= bits <= 16:
        raise ValueError("bits_per_sample must be between 1 and 16")
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
        (277, 3, 1, 1),
        (278, 4, 1, rows_per_strip),
        (279, 4, len(strips), strip_counts),
        (284, 3, 1, 1),
        (296, 3, 1, 2),
        (33421, 3, 2, (2, 2)),
        (33422, 1, 4, bytes(cfa)),
        (50706, 1, 4, bytes((1, 4, 0, 0))),
        (50707, 1, 4, bytes((1, 4, 0, 0))),
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
    entries.sort(key=lambda item: item[0])
    ifd_offset = 8
    # Build once with a conservative strip offset, then rebuild with the
    # actual end of the IFD/extra-value area.
    provisional = _build_ifd(entries, ifd_offset, tuple(0 for _ in strips), "II")
    strip_offset = ifd_offset + len(provisional)
    if strip_offset & 1:
        strip_offset += 1
    strip_offsets = []
    cursor = strip_offset
    for strip in strips:
        strip_offsets.append(cursor)
        cursor += len(strip)
    directory = _build_ifd(entries, ifd_offset, tuple(strip_offsets), "II")
    output = bytearray(b"II" + struct.pack("<H", 42) + struct.pack("<I", ifd_offset))
    output.extend(directory)
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
    if not 1 <= bits <= 16:
        raise ValueError("bits_per_sample must be between 1 and 16")
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
        (50706, 1, 4, bytes((1, 4, 0, 0))),
        (50707, 1, 4, bytes((1, 4, 0, 0))),
        (50708, 2, camera_model_count, camera_model),
        (50714, 3, 1, black_level),
        (50717, 4, 1, white_level),
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


def encode_dng_aot(
    raw,
    metadata: dict | None = None,
    compression: str = "packbits",
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
    return _encode_dng_array_legacy(
        raw, metadata, compression, predictor, bits_per_sample
    )


def save_dng_aot(raw, path: str | os.PathLike[str], metadata: dict | None = None, compression: str = "packbits", predictor: str = "none", bits_per_sample: int | None = None, *, width: int | None = None, height: int | None = None) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
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


def _read_value(data: bytes, offset: int, type_id: int, count: int, endian: str):
    size = _TYPE_SIZE.get(type_id)
    if size is None or count < 0 or offset < 0 or offset + size * count > len(data):
        raise ValueError("invalid TIFF field bounds")
    payload = data[offset:offset + size * count]
    if type_id in (1, 7):
        return payload
    if type_id == 2:
        return payload.rstrip(b"\x00").decode("ascii", errors="replace")
    if type_id == 3:
        values = struct.unpack(_fmt(endian, f"{count}H"), payload)
    elif type_id == 4:
        values = struct.unpack(_fmt(endian, f"{count}I"), payload)
    elif type_id == 5:
        raw = struct.unpack(_fmt(endian, f"{count * 2}I"), payload)
        values = tuple((raw[i], raw[i + 1]) for i in range(0, len(raw), 2))
    elif type_id == 6:
        values = struct.unpack(_fmt(endian, f"{count}b"), payload)
    elif type_id == 8:
        values = struct.unpack(_fmt(endian, f"{count}h"), payload)
    elif type_id == 9:
        values = struct.unpack(_fmt(endian, f"{count}i"), payload)
    elif type_id == 10:
        raw = struct.unpack(_fmt(endian, f"{count * 2}i"), payload)
        values = tuple((raw[i], raw[i + 1]) for i in range(0, len(raw), 2))
    elif type_id == 11:
        values = struct.unpack(_fmt(endian, f"{count}f"), payload)
    elif type_id == 12:
        values = struct.unpack(_fmt(endian, f"{count}d"), payload)
    else:
        raise ValueError(f"unsupported TIFF field type in reader: {type_id}")
    return values[0] if count == 1 else values


def _tag_scalar(tags: Mapping[int, object], tag: int, default=None):
    """Return a scalar TIFF tag, rejecting ambiguous multi-value fields."""
    if tag not in tags:
        return default
    value = tags[tag]
    if isinstance(value, tuple):
        if len(value) != 1:
            return None
        value = value[0]
    if isinstance(value, list):
        if len(value) != 1:
            return None
        value = value[0]
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return None


class DNGCapabilityError(ValueError):
    """Raised when a DNG layout is outside the maintained safe profile."""

    def __init__(self, message: str, report: "DNGCapabilityReport | None" = None):
        super().__init__(message)
        self.report = report


@dataclass(frozen=True)
class DNGCapabilityReport:
    """Static capability result for a DNG/TIFF header.

    The report is intentionally independent of decoding.  Applications can
    inspect a camera file and select a supported path before allocating a
    full RAW frame; unsupported lossless-JPEG and tiled layouts are reported
    explicitly instead of being routed through a guessed decoder.
    """

    width: int | None
    height: int | None
    bits_per_sample: int | None
    compression: int | None
    predictor: int | None
    uses_tiles: bool
    uses_subifd: bool
    has_strips: bool
    supported: bool
    profile: str
    reasons: tuple[str, ...]
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "bits_per_sample": self.bits_per_sample,
            "compression": self.compression,
            "predictor": self.predictor,
            "uses_tiles": self.uses_tiles,
            "uses_subifd": self.uses_subifd,
            "has_strips": self.has_strips,
            "supported": self.supported,
            "profile": self.profile,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
        }


def _read_tiff_tags_only(
    source: bytes | bytearray | memoryview | str | os.PathLike[str],
) -> tuple[str, dict[int, object]]:
    """Read only TIFF header/IFD metadata for capability inspection."""
    data = Path(source).read_bytes() if isinstance(source, (str, os.PathLike)) else bytes(source)
    if len(data) < 8 or data[:2] not in (b"II", b"MM"):
        raise ValueError("not a TIFF/DNG byte stream")
    endian = data[:2].decode("ascii")
    if struct.unpack(_fmt(endian, "H"), data[2:4])[0] != 42:
        raise ValueError("unsupported TIFF magic")
    ifd_offset = struct.unpack(_fmt(endian, "I"), data[4:8])[0]
    if ifd_offset < 8 or ifd_offset & 1 or ifd_offset + 2 > len(data):
        raise ValueError("IFD offset out of bounds")
    count = struct.unpack(_fmt(endian, "H"), data[ifd_offset:ifd_offset + 2])[0]
    ifd_end = ifd_offset + 2 + count * 12 + 4
    if ifd_end > len(data):
        raise ValueError("truncated IFD")
    tags: dict[int, object] = {}
    for index in range(count):
        start = ifd_offset + 2 + index * 12
        tag, type_id, value_count = struct.unpack(_fmt(endian, "HHI"), data[start:start + 8])
        if tag in tags:
            raise ValueError("duplicate TIFF tag")
        value_field = data[start + 8:start + 12]
        size = _TYPE_SIZE.get(type_id)
        if size is None:
            raise ValueError("unknown TIFF field type")
        payload_size = size * value_count
        value_offset = start + 8 if payload_size <= 4 else struct.unpack(_fmt(endian, "I"), value_field)[0]
        tags[tag] = _read_value(data, value_offset, type_id, value_count, endian)
    return endian, tags


def dng_capability_report(
    source: DNGFrame | Mapping[int, object] | bytes | bytearray | memoryview | str | os.PathLike[str],
) -> DNGCapabilityReport:
    """Return a fail-closed capability report without decoding pixel data."""
    if isinstance(source, DNGFrame):
        tags = dict(source.tags or {})
        width, height = int(source.width), int(source.height)
        bits = int(source.bits_per_sample)
    elif isinstance(source, Mapping):
        tags = dict(source)
        width = _tag_scalar(tags, 256, None)
        height = _tag_scalar(tags, 257, None)
        bits = _tag_scalar(tags, 258, None)
    else:
        _endian, tags = _read_tiff_tags_only(source)
        width = _tag_scalar(tags, 256, None)
        height = _tag_scalar(tags, 257, None)
        bits = _tag_scalar(tags, 258, None)
    compression = _tag_scalar(tags, 259, 1)
    predictor = _tag_scalar(tags, 317, 1)
    photometric = _tag_scalar(tags, 262, None)
    samples_per_pixel = _tag_scalar(tags, 277, 1)
    uses_tiles = any(tag in tags for tag in _TILE_TAGS)
    uses_subifd = 330 in tags
    has_strips = 273 in tags and 279 in tags
    reasons: list[str] = []
    warnings: list[str] = []
    if width is None or height is None or width <= 0 or height <= 0:
        reasons.append("missing or invalid image geometry")
    if bits is None or not 1 <= bits <= 16:
        reasons.append("only 1..16 bits per sample are supported")
    if compression is None:
        reasons.append("Compression tag is not a scalar")
    elif compression in _LOSSY_JPEG_COMPRESSION:
        reasons.append(f"DNG compression {compression} is lossy JPEG and is not supported")
    elif compression not in _SUPPORTED_COMPRESSION:
        reasons.append(f"DNG compression {compression} is not supported")
    if samples_per_pixel is None or samples_per_pixel != 1:
        reasons.append("the maintained native DNG path requires SamplesPerPixel=1")
    if uses_tiles:
        reasons.append("tiled TIFF/DNG layout is not supported; use strip-based input")
    if uses_subifd:
        if _tag_scalar(tags, 262, 0) == 32803 and 33422 in tags:
            warnings.append(
                "SubIFDs are present; the maintained path uses the first IFD "
                "because it is explicitly mosaiced RAW"
            )
        else:
            reasons.append(
                "SubIFDs are present and the first IFD is not explicitly mosaiced RAW"
            )
    if not has_strips:
        reasons.append("StripOffsets/StripByteCounts are required")
    if predictor is None:
        reasons.append("Predictor tag is not a scalar")
    elif predictor not in (1, 2):
        reasons.append(f"TIFF predictor {predictor} is not supported")
    if compression == 7:
        if bits is not None and not 8 <= bits <= 16:
            reasons.append("native DNG Lossless JPEG is maintained for 8..16 bits per sample")
        if photometric in (1, 6) and bits == 8:
            reasons.append(
                "Compression=7 with 8-bit BlackIsZero/YCbCr is baseline JPEG; "
                "the maintained path only decodes lossless CFA JPEG"
            )
        if 317 in tags and predictor != 1:
            reasons.append("TIFF Predictor must be absent or 1 for JPEG-compressed DNG")
        jpeg_proc = _tag_scalar(tags, 512, None)
        if 512 in tags and jpeg_proc not in (14,):
            reasons.append("JPEGProc must be 14 when present for lossless JPEG")
        jpeg_predictor = _tag_scalar(tags, 517, None)
        if 517 in tags and jpeg_predictor not in range(1, 8):
            reasons.append("JPEGLosslessPredictors must be 1..7 when present")
        point_transform = _tag_scalar(tags, 518, None)
        if 518 in tags and point_transform != 0:
            reasons.append("nonzero JPEGPointTransforms are not maintained")
    if has_strips:
        offsets = tags.get(273)
        counts = tags.get(279)
        offsets_len = len(offsets) if isinstance(offsets, tuple) else 1
        counts_len = len(counts) if isinstance(counts, tuple) else 1
        if offsets_len != counts_len:
            reasons.append("StripOffsets/StripByteCounts length mismatch")
    if compression in _LOSSLESS_JPEG_COMPRESSION:
        profile = "lossless_jpeg_strip_profile"
    elif compression in _LOSSY_JPEG_COMPRESSION:
        profile = "lossy_jpeg_unsupported"
    elif uses_tiles:
        profile = "tiled_unsupported"
    elif uses_subifd and reasons:
        profile = "subifd_unsupported"
    elif compression in _SUPPORTED_COMPRESSION and has_strips:
        profile = "portable_strip_profile"
    else:
        profile = "unsupported"
    return DNGCapabilityReport(
        width=width,
        height=height,
        bits_per_sample=bits,
        compression=compression,
        predictor=predictor,
        uses_tiles=uses_tiles,
        uses_subifd=uses_subifd,
        has_strips=has_strips,
        supported=not reasons,
        profile=profile,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
    )


def read_dng_aot(source: bytes | bytearray | memoryview | str | os.PathLike[str]) -> DNGFrame:
    data = Path(source).read_bytes() if isinstance(source, (str, os.PathLike)) else bytes(source)
    if len(data) < 8 or data[:2] not in (b"II", b"MM"):
        raise ValueError("not a TIFF/DNG byte stream")
    endian = data[:2].decode("ascii")
    if struct.unpack(_fmt(endian, "H"), data[2:4])[0] != 42:
        raise ValueError("unsupported TIFF magic")
    ifd_offset = struct.unpack(_fmt(endian, "I"), data[4:8])[0]
    if ifd_offset < 8 or ifd_offset & 1 or ifd_offset + 2 > len(data):
        raise ValueError("IFD offset out of bounds")
    count = struct.unpack(_fmt(endian, "H"), data[ifd_offset:ifd_offset + 2])[0]
    ifd_end = ifd_offset + 2 + count * 12 + 4
    if ifd_end > len(data):
        raise ValueError("truncated IFD")
    tags: dict[int, object] = {}
    for index in range(count):
        start = ifd_offset + 2 + index * 12
        tag, type_id, value_count = struct.unpack(_fmt(endian, "HHI"), data[start:start + 8])
        if tag in tags:
            raise ValueError("duplicate TIFF tag")
        value_field = data[start + 8:start + 12]
        size = _TYPE_SIZE.get(type_id)
        if size is None:
            raise ValueError("unknown TIFF field type")
        payload_size = size * value_count
        value_offset = start + 8 if payload_size <= 4 else struct.unpack(_fmt(endian, "I"), value_field)[0]
        tags[tag] = _read_value(data, value_offset, type_id, value_count, endian)
    capability = dng_capability_report(tags)
    if not capability.supported:
        raise DNGCapabilityError(
            "DNG input is outside the maintained strip/native profile: "
            + "; ".join(capability.reasons),
            report=capability,
        )
    required = {256, 257, 258, 273, 279}
    missing = required.difference(tags)
    if missing:
        raise ValueError(f"missing required TIFF tags: {sorted(missing)}")
    width = _tag_scalar(tags, 256, None)
    height = _tag_scalar(tags, 257, None)
    bits = _tag_scalar(tags, 258, None)
    if width is None or height is None or bits is None:
        raise ValueError("required TIFF geometry tags must be scalar")
    if width <= 0 or height <= 0 or not 1 <= bits <= 16:
        raise ValueError("invalid DNG image geometry or bit depth")
    compression = _tag_scalar(tags, 259, 1)
    if compression is None:
        raise ValueError("Compression tag must be scalar")
    row_size = (width * bits + 7) // 8
    offsets = tags[273] if isinstance(tags[273], tuple) else (tags[273],)
    counts = tags[279] if isinstance(tags[279], tuple) else (tags[279],)
    if not offsets or len(offsets) != len(counts):
        raise ValueError("StripOffsets/StripByteCounts length mismatch")
    rows_per_strip = _tag_scalar(tags, 278, height)
    if rows_per_strip is None:
        raise ValueError("RowsPerStrip must be scalar")
    expected_strip_count = (height + rows_per_strip - 1) // rows_per_strip if rows_per_strip > 0 else 0
    if rows_per_strip <= 0 or len(offsets) != expected_strip_count:
        raise ValueError("invalid RowsPerStrip or strip count")
    strip_ranges: list[tuple[int, int]] = []
    raw_parts = []
    for strip_index, (strip_offset, strip_count) in enumerate(zip(offsets, counts)):
        strip_offset, strip_count = int(strip_offset), int(strip_count)
        if strip_offset < 0 or strip_count <= 0 or strip_offset + strip_count > len(data):
            raise ValueError("strip bounds out of range")
        strip_range = (strip_offset, strip_offset + strip_count)
        if any(strip_range[0] < other_end and other_start < strip_range[1] for other_start, other_end in strip_ranges):
            raise ValueError("DNG strip payloads overlap")
        strip_ranges.append(strip_range)
        encoded = data[strip_offset:strip_offset + strip_count]
        first_row = strip_index * rows_per_strip
        if first_row >= height:
            raise ValueError("strip index exceeds image height")
        strip_rows = min(rows_per_strip, height - first_row)
        expected_strip = strip_rows * row_size
        if compression == 1:
            if len(encoded) != expected_strip:
                raise ValueError("uncompressed strip length mismatch")
            raw_parts.append(encoded)
        elif compression == 32773:
            rows = bytearray()
            cursor = 0
            for _ in range(strip_rows):
                row = bytearray()
                while len(row) < row_size:
                    if cursor >= len(encoded):
                        raise ValueError("truncated PackBits strip")
                    header = encoded[cursor]
                    cursor += 1
                    signed = header if header < 128 else header - 256
                    if signed >= 0:
                        size = signed + 1
                        if cursor + size > len(encoded) or len(row) + size > row_size:
                            raise ValueError("PackBits literal exceeds the strip row")
                        row.extend(encoded[cursor:cursor + size])
                        cursor += size
                    elif signed != -128:
                        size = 1 - signed
                        if cursor >= len(encoded) or len(row) + size > row_size:
                            raise ValueError("truncated PackBits repeat")
                        row.extend(encoded[cursor:cursor + 1] * size)
                        cursor += 1
                if len(row) != row_size:
                    raise ValueError("PackBits row size mismatch")
                rows.extend(row)
            if cursor != len(encoded):
                raise ValueError("trailing PackBits bytes in strip")
            raw_parts.append(bytes(rows))
        elif compression == 7:
            np = _numpy()
            decoded = _lossless_jpeg_payload_decode(
                encoded,
                expected_samples=strip_rows * width,
                expected_precision=bits,
            )
            decoded = decoded.reshape(strip_rows, width)
            if decoded.size and int(np.max(decoded)) >= (1 << bits):
                raise ValueError("lossless JPEG sample exceeds the TIFF bit depth")
            if bits <= 8:
                decoded = decoded.astype(np.uint8, copy=False)
            raw_parts.append(_pack_samples(decoded, bits, endian))
        elif compression == 8:
            raw_parts.append(inflate_deflate(encoded, expected_strip))
        else:
            # Guarded by ``capability`` above; keep this branch fail-closed if
            # a future code path changes the supported compression set.
            raise DNGCapabilityError(f"unsupported DNG compression tag: {compression}", report=capability)
    raw_bytes = b"".join(raw_parts)
    if compression not in _SUPPORTED_COMPRESSION:
        raise DNGCapabilityError(f"unsupported DNG compression tag: {compression}", report=capability)
    expected = height * row_size
    if len(raw_bytes) != expected:
        raise ValueError("decoded DNG sample length mismatch")
    predictor = _tag_scalar(tags, 317, 1)
    if predictor is None:
        raise ValueError("Predictor tag must be scalar")
    if compression == 7 and predictor != 1:
        raise DNGCapabilityError(
            "TIFF Predictor is not applied to a JPEG-compressed DNG strip",
            report=capability,
        )
    if predictor == 2:
        raw_bytes = _horizontal_predict_packed(
            raw_bytes, width, height, bits, inverse=True, endian=endian
        )
    elif predictor != 1:
        raise DNGCapabilityError(f"unsupported TIFF predictor: {predictor}", report=capability)
    return DNGFrame(width, height, bits, compression, tags, raw_bytes, endian)


def decode_dng_bytes(source: bytes | bytearray | memoryview) -> DNGFrame:
    """Decode a byte buffer to packed CFA rows without importing NumPy.

    The returned :class:`DNGFrame` keeps bytes in ``raw_bytes`` and exposes a
    zero-copy ``raw_view()``.  Calling the legacy ``samples()`` or
    ``sample_region()`` compatibility methods imports NumPy lazily.
    """
    if not isinstance(source, (bytes, bytearray, memoryview)):
        raise TypeError("source must be bytes, bytearray, or memoryview")
    return read_dng_aot(source)


__all__ = [
    "DNGFrame",
    "DNGCapabilityError",
    "DNGCapabilityReport",
    "dng_capability_report",
    "encode_dng_bytes",
    "decode_dng_bytes",
    "encode_dng_aot",
    "read_dng_aot",
    "save_dng_aot",
]
