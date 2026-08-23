"""Small native JPEG lossless (SOF3) codec used by the DNG profile.

This is the predictive Huffman process from JPEG-1, not baseline JPEG and
not JPEG-LS.  It intentionally supports one interleaved grayscale component,
no restart markers, and point transform zero.  Pixel prediction and residual
preparation are deterministic numeric work; marker/entropy serialization is a
bounded standard-library boundary.
"""
from __future__ import annotations

import heapq
import struct
from collections.abc import Mapping

import numpy as np

from .bitstream import BitReader, BitWriter, canonical_codes


def _marker(code: int, payload: bytes = b"") -> bytes:
    if not 0 <= int(code) <= 255:
        raise ValueError("JPEG marker code is out of range")
    if not payload:
        return bytes((0xFF, code))
    if len(payload) > 65533:
        raise ValueError("JPEG marker payload exceeds the segment limit")
    return b"\xff" + bytes((code,)) + struct.pack(">H", len(payload) + 2) + payload


def _huffman_lengths(frequencies: list[int]) -> list[int]:
    active = [(int(value), symbol, symbol) for symbol, value in enumerate(frequencies) if int(value) > 0]
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
    stack = [(active[0][2], 0)]
    while stack:
        node, depth = stack.pop()
        if node < len(frequencies):
            lengths[node] = max(1, depth)
        else:
            left, right = nodes[node]
            stack.extend(((left, depth + 1), (right, depth + 1)))
    if max(lengths, default=0) > 16:
        # The maintained alphabet has only 17 categories, so this is an
        # adversarial/invalid frequency result rather than a normal image.
        raise ValueError("lossless JPEG Huffman tree exceeds 16 bits")
    return lengths


def _huffman_table(frequencies: list[int]):
    lengths = _huffman_lengths(frequencies)
    active = tuple(symbol for symbol, value in enumerate(frequencies) if int(value) > 0)
    codes = canonical_codes({symbol: lengths[symbol] for symbol in active})
    ordered = tuple(sorted(active, key=lambda symbol: (lengths[symbol], symbol)))
    bits = tuple(sum(1 for symbol in ordered if lengths[symbol] == size) for size in range(1, 17))
    payload = bytes(bits) + bytes(ordered)
    return codes, lengths, _marker(0xC4, b"\x00" + payload)


def _category(value: int) -> int:
    magnitude = abs(int(value))
    return 0 if magnitude == 0 else magnitude.bit_length()


def _encode_amplitude(value: int, category: int) -> int:
    if category == 0:
        return 0
    return int(value) if int(value) >= 0 else int(value) + (1 << int(category)) - 1


def _decode_amplitude(value: int, category: int) -> int:
    if category == 0:
        return 0
    threshold = 1 << (int(category) - 1)
    return int(value) if int(value) >= threshold else int(value) - ((1 << int(category)) - 1)


def _modulo_difference(sample: int, prediction: int) -> int:
    """JPEG lossless H.1.2 difference mapped to the signed 16-bit domain."""
    value = (int(sample) - int(prediction)) & 0xFFFF
    return value if value < 0x8000 else value - 0x10000


def _predict(samples: np.ndarray, y: int, x: int, predictor: int, initial: int) -> int:
    left = int(samples[y, x - 1]) if x else initial
    above = int(samples[y - 1, x]) if y else initial
    upper_left = int(samples[y - 1, x - 1]) if x and y else initial
    # JPEG-1 lossless has special line starts: the first line always uses the
    # horizontal predictor, while every later line starts from the sample
    # above.  The selected predictor applies after those boundary samples.
    if y == 0 or x == 0:
        return left if y == 0 else above
    if predictor == 1:
        return left
    if predictor == 2:
        return above
    if predictor == 3:
        return upper_left
    if predictor == 4:
        return left + above - upper_left
    if predictor == 5:
        return left + ((above - upper_left) >> 1)
    if predictor == 6:
        return above + ((left - upper_left) >> 1)
    if predictor == 7:
        return (left + above) >> 1
    raise ValueError("JPEG lossless predictor must be in [1, 7]")


def _normalize_samples(samples, bits: int | None):
    data = np.asarray(samples)
    if data.ndim != 2 or data.size == 0 or data.dtype not in (np.uint8, np.uint16):
        raise ValueError("lossless JPEG input must be a non-empty 2D uint8 or uint16 array")
    selected_bits = int(bits or (8 if data.dtype == np.uint8 else 16))
    if not 2 <= selected_bits <= 16:
        raise ValueError("lossless JPEG precision must be in [2, 16]")
    if data.shape[0] > 65535 or data.shape[1] > 65535:
        raise ValueError("lossless JPEG dimensions must fit the SOF marker")
    if int(np.max(data)) >= (1 << selected_bits):
        raise ValueError("sample exceeds the selected lossless JPEG precision")
    return np.ascontiguousarray(data), selected_bits


def encode_lossless_jpeg(samples, *, bits: int | None = None, predictor: int = 1) -> bytes:
    """Encode one grayscale plane as a JPEG-1 lossless SOF3 stream."""
    data, precision = _normalize_samples(samples, bits)
    predictor = int(predictor)
    if not 1 <= predictor <= 7:
        raise ValueError("JPEG lossless predictor must be in [1, 7]")
    initial = 1 << (precision - 1)
    frequencies = [0] * 17
    residuals = np.empty(data.shape, dtype=np.int32)
    for y in range(data.shape[0]):
        for x in range(data.shape[1]):
            residual = _modulo_difference(int(data[y, x]), _predict(data, y, x, predictor, initial))
            residuals[y, x] = residual
            category = _category(residual)
            if category > 16:
                raise ValueError("lossless JPEG residual category exceeds precision")
            frequencies[category] += 1
    codes, _lengths, dht = _huffman_table(frequencies)
    writer = BitWriter(lsb_first=False)
    for residual in residuals.flat:
        residual = int(residual)
        category = _category(residual)
        code, size = codes[category]
        writer.write(code, size)
        # In the JPEG lossless extension, category 16 is the special
        # modulo-difference value -32768 and carries no following bits.
        if category and category != 16:
            writer.write(_encode_amplitude(residual, category), category)
    scan = bytearray()
    for value in writer.finish(fill=1):
        scan.append(value)
        if value == 0xFF:
            scan.append(0)
    height, width = map(int, data.shape)
    sof = bytes((precision,)) + struct.pack(">HH", height, width) + bytes((1, 1, 0x11, 0))
    sos = bytes((1, 1, 0, predictor, 0, 0))
    return b"\xff\xd8" + dht + _marker(0xC3, sof) + _marker(0xDA, sos) + bytes(scan) + b"\xff\xd9"


class _JpegBitReader:
    __slots__ = ("_reader",)

    def __init__(self, scan: bytes):
        self._reader = BitReader(scan, lsb_first=False)

    def read(self, count: int) -> int:
        return self._reader.read(int(count))

    def huffman(self, decode_map: Mapping[tuple[int, int], int]) -> int:
        code = 0
        for size in range(1, 17):
            code = (code << 1) | self.read(1)
            symbol = decode_map.get((code, size))
            if symbol is not None:
                return symbol
        raise ValueError("invalid JPEG lossless Huffman code")


def _parse_huffman(payload: bytes):
    if not payload:
        raise ValueError("empty JPEG DHT")
    table_id = payload[0]
    if table_id != 0:
        raise ValueError("only lossless JPEG DC table 0 is supported")
    if len(payload) < 17:
        raise ValueError("truncated JPEG DHT")
    counts = tuple(payload[1:17])
    total = sum(counts)
    if len(payload) != 17 + total or not total:
        raise ValueError("invalid JPEG DHT length")
    values = tuple(payload[17:])
    decode = {}
    code = 0
    cursor = 0
    for size, count in enumerate(counts, 1):
        for _ in range(count):
            decode[(code, size)] = values[cursor]
            code += 1
            cursor += 1
        code <<= 1
    return decode


def _next_marker(data: bytes, offset: int) -> tuple[int, int]:
    while offset < len(data) and data[offset] != 0xFF:
        offset += 1
    if offset >= len(data):
        raise ValueError("JPEG marker is truncated")
    while offset < len(data) and data[offset] == 0xFF:
        offset += 1
    if offset >= len(data) or data[offset] == 0:
        raise ValueError("invalid JPEG marker")
    return data[offset], offset + 1


def decode_lossless_jpeg(stream: bytes | bytearray) -> np.ndarray:
    """Decode the maintained one-component, no-restart SOF3 profile."""
    data = bytes(stream)
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG stream")
    offset = 2
    huffman = None
    precision = width = height = predictor = None
    scan = None
    while offset < len(data):
        marker, offset = _next_marker(data, offset)
        if marker == 0xD9:
            raise ValueError("JPEG ended before SOS")
        if marker in (0xD8,) or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            raise ValueError("truncated JPEG marker length")
        length = struct.unpack(">H", data[offset:offset + 2])[0]
        if length < 2 or offset + length > len(data):
            raise ValueError("JPEG marker exceeds stream bounds")
        payload = data[offset + 2:offset + length]
        offset += length
        if marker == 0xC4:
            huffman = _parse_huffman(payload)
        elif marker == 0xC3:
            if len(payload) != 9 or payload[0] < 2 or payload[0] > 16 or payload[5] != 1:
                raise ValueError("unsupported lossless JPEG frame header")
            precision = int(payload[0])
            height, width = struct.unpack(">HH", payload[1:5])
            if payload[6:] != b"\x01\x11\x00":
                raise ValueError("unsupported lossless JPEG component layout")
        elif marker == 0xDA:
            if len(payload) != 6 or payload[:3] != b"\x01\x01\x00" or payload[4:] != b"\x00\x00":
                raise ValueError("unsupported lossless JPEG scan header")
            predictor = int(payload[3])
            scan_start = offset
            scan_bytes = bytearray()
            cursor = scan_start
            while cursor < len(data):
                value = data[cursor]
                cursor += 1
                if value != 0xFF:
                    scan_bytes.append(value)
                    continue
                if cursor >= len(data):
                    raise ValueError("truncated JPEG scan escape")
                escaped = data[cursor]
                cursor += 1
                if escaped == 0:
                    scan_bytes.append(0xFF)
                    continue
                if escaped == 0xD9:
                    scan = bytes(scan_bytes)
                    offset = cursor
                    break
                raise ValueError("restart markers are not supported by this lossless JPEG profile")
            else:
                raise ValueError("JPEG scan has no EOI")
            break
    if huffman is None or precision is None or width is None or height is None or scan is None or predictor is None:
        raise ValueError("incomplete lossless JPEG stream")
    if width <= 0 or height <= 0 or not 1 <= predictor <= 7:
        raise ValueError("invalid lossless JPEG geometry or predictor")
    reader = _JpegBitReader(scan)
    initial = 1 << (precision - 1)
    output = np.empty((height, width), dtype=np.uint8 if precision <= 8 else np.uint16)
    limit = 1 << precision
    for y in range(height):
        for x in range(width):
            category = reader.huffman(huffman)
            if category > 16:
                raise ValueError("lossless JPEG category exceeds precision")
            if category == 16:
                difference = -32768
            else:
                amplitude = reader.read(category) if category else 0
                difference = _decode_amplitude(amplitude, category)
            value = (_predict(output, y, x, predictor, initial) + difference) & 0xFFFF
            if not 0 <= value < limit:
                raise ValueError("lossless JPEG reconstructed sample is out of range")
            output[y, x] = value
    return output


__all__ = ["encode_lossless_jpeg", "decode_lossless_jpeg"]
