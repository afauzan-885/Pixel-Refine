"""Small dependency-free Deflate codec used by the native DNG byte API.

The encoder emits deterministic fixed- or dynamic-Huffman RFC 1951 blocks
using a greedy, bounded LZ77 search.  The search uses the Deflate 32 KiB
history, limits matches to 258 bytes, and retains only a bounded number of
recent candidates per three-byte probe.  Stored blocks remain available as an
explicit compatibility/diagnostic helper.  The decoder accepts stored,
fixed-Huffman, and dynamic-Huffman blocks so DNG files written by conforming
external encoders remain readable within the maintained strip profile.
"""
from __future__ import annotations

from collections import deque
import struct

from .bitstream import BitReader, BitWriter, adler32, canonical_codes, reverse_bits


_LENGTH_BASE = (
    3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
    35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258,
)
_LENGTH_EXTRA = (
    0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
    3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0,
)
_DIST_BASE = (
    1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129,
    193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097,
    6145, 8193, 12289, 16385, 24577,
)
_DIST_EXTRA = (
    0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
    7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13,
)

_DEFLATE_WINDOW_BYTES = 32768
_DEFLATE_MAX_MATCH = 258
_DEFLATE_MAX_SEARCH_DEPTH = 32


def _decode_table(lengths: list[int], *, max_bits: int = 15) -> dict[tuple[int, int], int]:
    if not any(lengths):
        raise ValueError("empty Deflate Huffman table")
    if max(lengths) > max_bits:
        raise ValueError("Deflate Huffman code exceeds maximum length")
    codes = canonical_codes(
        {symbol: length for symbol, length in enumerate(lengths) if length}
    )
    return {
        (reverse_bits(code, size), size): symbol
        for symbol, (code, size) in codes.items()
    }


def _fixed_tables() -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    literal_lengths = [0] * 288
    for symbol in range(0, 144):
        literal_lengths[symbol] = 8
    for symbol in range(144, 256):
        literal_lengths[symbol] = 9
    for symbol in range(256, 280):
        literal_lengths[symbol] = 7
    for symbol in range(280, 288):
        literal_lengths[symbol] = 8
    return _decode_table(literal_lengths), _decode_table([5] * 32)


_FIXED_LITERAL_DECODE, _FIXED_DISTANCE_DECODE = _fixed_tables()


def _fixed_encode_tables() -> tuple[dict[int, tuple[int, int]], dict[int, tuple[int, int]]]:
    """Return fixed Huffman codes in the LSB-first Deflate wire order."""
    literal_lengths: dict[int, int] = {}
    literal_lengths.update({symbol: 8 for symbol in range(0, 144)})
    literal_lengths.update({symbol: 9 for symbol in range(144, 256)})
    literal_lengths.update({symbol: 7 for symbol in range(256, 280)})
    literal_lengths.update({symbol: 8 for symbol in range(280, 288)})
    literal_codes = {
        symbol: (reverse_bits(code, size), size)
        for symbol, (code, size) in canonical_codes(literal_lengths).items()
    }
    distance_codes = {
        symbol: (reverse_bits(code, 5), 5)
        for symbol, (code, _size) in canonical_codes({symbol: 5 for symbol in range(32)}).items()
    }
    return literal_codes, distance_codes


_FIXED_LITERAL_ENCODE, _FIXED_DISTANCE_ENCODE = _fixed_encode_tables()


def _read_symbol(reader: BitReader, table: dict[tuple[int, int], int]) -> int:
    code = 0
    for size in range(1, 16):
        code |= reader.read(1) << (size - 1)
        symbol = table.get((code, size))
        if symbol is not None:
            return symbol
    raise ValueError("invalid Deflate Huffman symbol")


def _length_code(length: int) -> tuple[int, int, int]:
    """Return ``(symbol, extra_value, extra_width)`` for a match length."""
    if not 3 <= length <= _DEFLATE_MAX_MATCH:
        raise ValueError("Deflate match length out of range")
    for index, base in enumerate(_LENGTH_BASE):
        limit = base + ((1 << _LENGTH_EXTRA[index]) - 1)
        if length <= limit or index == len(_LENGTH_BASE) - 1:
            return 257 + index, length - base, _LENGTH_EXTRA[index]
    raise AssertionError("unreachable")


def _distance_code(distance: int) -> tuple[int, int, int]:
    """Return ``(symbol, extra_value, extra_width)`` for a match distance."""
    if not 1 <= distance <= _DEFLATE_WINDOW_BYTES:
        raise ValueError("Deflate distance out of range")
    for index, base in enumerate(_DIST_BASE):
        limit = base + ((1 << _DIST_EXTRA[index]) - 1)
        if distance <= limit:
            return index, distance - base, _DIST_EXTRA[index]
    raise AssertionError("unreachable")


def _lz77_tokens(data: bytes, *, search_depth: int = _DEFLATE_MAX_SEARCH_DEPTH):
    """Yield literal bytes or greedy ``(length, distance)`` matches.

    Every probe bucket stores at most ``search_depth`` recent positions and
    the ring removes positions older than the RFC 1951 history window.  This
    bounds dictionary growth and candidate work for large DNG strips while
    preserving overlapping matches such as a repeated single byte.
    """
    search_depth = min(max(1, int(search_depth)), _DEFLATE_MAX_SEARCH_DEPTH)
    positions: dict[bytes, deque[int]] = {}
    position_ring: list[tuple[int, bytes] | None] = [None] * (_DEFLATE_WINDOW_BYTES + 1)
    size = len(data)

    def remember(position: int) -> None:
        if position + 2 >= size:
            return
        key = data[position:position + 3]
        expired = position - _DEFLATE_WINDOW_BYTES
        if expired >= 0:
            slot = position_ring[expired % len(position_ring)]
            if slot is not None and slot[0] == expired:
                old_key = slot[1]
                bucket = positions.get(old_key)
                if bucket is not None:
                    while bucket and bucket[0] <= expired:
                        bucket.popleft()
                    if not bucket:
                        positions.pop(old_key, None)
        bucket = positions.get(key)
        if bucket is None:
            bucket = deque(maxlen=search_depth)
            positions[key] = bucket
        bucket.append(position)
        position_ring[position % len(position_ring)] = (position, key)

    index = 0
    while index < size:
        key = data[index:index + 3] if index + 2 < size else b""
        candidates = positions.get(key, ()) if key else ()
        best_length, best_distance = 0, 0
        for previous in reversed(tuple(candidates)):
            distance = index - previous
            if distance <= 0 or distance > _DEFLATE_WINDOW_BYTES:
                continue
            maximum = min(_DEFLATE_MAX_MATCH, size - index)
            length = 0
            while length < maximum:
                history_index = previous + length if length < distance else previous + (length % distance)
                if data[history_index] != data[index + length]:
                    break
                length += 1
            if length > best_length:
                best_length, best_distance = length, distance
            if length == maximum:
                break
        if best_length >= 3:
            yield best_length, best_distance
            end = min(size, index + best_length)
            for position in range(index, end):
                remember(position)
            index = end
        else:
            yield data[index]
            remember(index)
            index += 1


def _bounded_output(payload: bytes, max_output_bytes: int | None) -> bytes:
    if max_output_bytes is None:
        return payload
    try:
        limit = int(max_output_bytes)
    except (TypeError, ValueError) as exc:
        raise ValueError("max_output_bytes must be a non-negative integer or None") from exc
    if limit < 0:
        raise ValueError("max_output_bytes must be a non-negative integer or None")
    if len(payload) > limit:
        raise ValueError("Deflate output exceeds the configured limit")
    return payload


def _read_dynamic_tables(
    reader: BitReader,
) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    literal_count = reader.read(5) + 257
    distance_count = reader.read(5) + 1
    code_length_count = reader.read(4) + 4
    if literal_count > 286 or distance_count > 32:
        raise ValueError("invalid Deflate dynamic table sizes")
    order = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)
    code_lengths = [0] * 19
    for symbol in order[:code_length_count]:
        code_lengths[symbol] = reader.read(3)
    code_table = _decode_table(code_lengths, max_bits=7)
    lengths: list[int] = []
    total = literal_count + distance_count
    while len(lengths) < total:
        symbol = _read_symbol(reader, code_table)
        if symbol <= 15:
            lengths.append(symbol)
        elif symbol == 16:
            if not lengths:
                raise ValueError("Deflate repeat has no previous code length")
            lengths.extend([lengths[-1]] * (reader.read(2) + 3))
        elif symbol == 17:
            lengths.extend([0] * (reader.read(3) + 3))
        elif symbol == 18:
            lengths.extend([0] * (reader.read(7) + 11))
        else:
            raise ValueError("invalid Deflate code-length symbol")
        if len(lengths) > total:
            raise ValueError("Deflate code-length repeat exceeds table")
    literal_lengths = lengths[:literal_count]
    distance_lengths = lengths[literal_count:]
    if literal_lengths[256] == 0:
        raise ValueError("Deflate literal table has no end-of-block symbol")
    return _decode_table(literal_lengths), _decode_table(distance_lengths)


def deflate_stored(data: bytes | bytearray | memoryview) -> bytes:
    """Return a zlib-wrapped stream containing bounded stored blocks."""
    source = memoryview(data).cast("B")
    output = bytearray(b"\x78\x01")
    if not source:
        output.extend(b"\x01\x00\x00\xff\xff")
    else:
        offset = 0
        while offset < len(source):
            end = min(offset + 65535, len(source))
            output.append(1 if end == len(source) else 0)
            size = end - offset
            output.extend(struct.pack("<HH", size, size ^ 0xFFFF))
            output.extend(source[offset:end])
            offset = end
    output.extend(struct.pack(">I", adler32(bytes(source))))
    return bytes(output)


def deflate_fixed(
    data: bytes | bytearray | memoryview,
    *,
    max_output_bytes: int | None = None,
    search_depth: int = _DEFLATE_MAX_SEARCH_DEPTH,
) -> bytes:
    """Return a zlib-wrapped fixed-Huffman Deflate stream with greedy LZ77.

    The encoder is deliberately dependency-free and deterministic.  It emits
    a single final fixed-Huffman block, uses only the RFC 1951 32 KiB history,
    and caps per-probe search depth at ``_DEFLATE_MAX_SEARCH_DEPTH``.  The
    optional output bound provides a fail-closed size guard for callers that
    allocate a fixed strip budget.
    """
    source = bytes(memoryview(data).cast("B"))
    writer = BitWriter(lsb_first=True)
    writer.write(1, 1)  # BFINAL=1
    writer.write(1, 2)  # BTYPE=01, fixed Huffman
    for token in _lz77_tokens(source, search_depth=search_depth):
        if isinstance(token, int):
            code, size = _FIXED_LITERAL_ENCODE[token]
            writer.write(code, size)
            continue
        length, distance = token
        symbol, extra, extra_bits = _length_code(length)
        code, size = _FIXED_LITERAL_ENCODE[symbol]
        writer.write(code, size)
        if extra_bits:
            writer.write(extra, extra_bits)
        symbol, extra, extra_bits = _distance_code(distance)
        code, size = _FIXED_DISTANCE_ENCODE[symbol]
        writer.write(code, size)
        if extra_bits:
            writer.write(extra, extra_bits)
    code, size = _FIXED_LITERAL_ENCODE[256]
    writer.write(code, size)
    payload = b"\x78\x01" + writer.finish() + struct.pack(">I", adler32(source))
    return _bounded_output(payload, max_output_bytes)


def _huffman_lengths(frequencies: list[int], max_bits: int = 15) -> list[int]:
    """Build bounded canonical lengths for a Deflate alphabet."""

    import heapq

    active = [
        (int(frequency), index, index)
        for index, frequency in enumerate(frequencies)
        if frequency > 0
    ]
    lengths = [0] * len(frequencies)
    if not active:
        lengths[0] = 1
        return lengths
    if len(active) == 1:
        lengths[active[0][2]] = 1
        return lengths
    heapq.heapify(active)
    nodes: dict[int, tuple[int, int]] = {}
    next_id = len(frequencies)
    order = len(frequencies)
    while len(active) > 1:
        left = heapq.heappop(active)
        right = heapq.heappop(active)
        nodes[next_id] = (left[2], right[2])
        heapq.heappush(active, (left[0] + right[0], order, next_id))
        next_id += 1
        order += 1
    stack = [(active[0][2], 0)]
    while stack:
        node, depth = stack.pop()
        if node < len(frequencies):
            lengths[node] = max(1, depth)
        else:
            left, right = nodes[node]
            stack.append((left, depth + 1))
            stack.append((right, depth + 1))

    counts = [0] * (max(max(lengths), max_bits) + 1)
    for length in lengths:
        if length:
            counts[length] += 1
    for bits in range(len(counts) - 1, max_bits, -1):
        while counts[bits] > 0:
            if counts[bits] < 2:
                raise ValueError("unable to bound Deflate Huffman tree")
            counts[bits] -= 2
            counts[bits - 1] += 1
            split = bits - 2
            while split > 0 and counts[split] == 0:
                split -= 1
            if split == 0:
                raise ValueError("unable to bound Deflate Huffman tree")
            counts[split] -= 1
            counts[split + 1] += 2
    ordered = sorted(
        (index for index, frequency in enumerate(frequencies) if frequency > 0),
        key=lambda index: (frequencies[index], index),
    )
    cursor = 0
    for bits in range(max_bits, 0, -1):
        for _ in range(counts[bits]):
            if cursor >= len(ordered):
                raise ValueError("invalid Deflate Huffman histogram")
            lengths[ordered[cursor]] = bits
            cursor += 1
    if cursor != len(ordered):
        raise ValueError("incomplete Deflate Huffman histogram")
    return lengths


def _rle_code_lengths(lengths: list[int]) -> list[tuple[int, int, int]]:
    """RLE the literal/distance code lengths for RFC 1951."""

    result: list[tuple[int, int, int]] = []
    index = 0
    while index < len(lengths):
        value = lengths[index]
        end = index + 1
        while end < len(lengths) and lengths[end] == value:
            end += 1
        run = end - index
        if value == 0:
            while run >= 11:
                count = min(run, 138)
                result.append((18, count - 11, 7))
                run -= count
            if run >= 3:
                count = min(run, 10)
                result.append((17, count - 3, 3))
                run -= count
            result.extend((0, 0, 0) for _ in range(run))
        else:
            result.append((value, 0, 0))
            run -= 1
            while run >= 3:
                count = min(run, 6)
                result.append((16, count - 3, 2))
                run -= count
            result.extend((value, 0, 0) for _ in range(run))
        index = end
    return result


def deflate_dynamic(
    data: bytes | bytearray | memoryview,
    *,
    max_output_bytes: int | None = None,
    search_depth: int = _DEFLATE_MAX_SEARCH_DEPTH,
) -> bytes:
    """Return a deterministic zlib-wrapped dynamic-Huffman Deflate stream."""

    source = bytes(memoryview(data).cast("B"))
    tokens = list(_lz77_tokens(source, search_depth=search_depth))
    literal_freq = [0] * 286
    distance_freq = [0] * 30
    for token in tokens:
        if isinstance(token, int):
            literal_freq[token] += 1
        else:
            length, distance = token
            literal_freq[_length_code(length)[0]] += 1
            distance_freq[_distance_code(distance)[0]] += 1
    literal_freq[256] += 1
    if not any(distance_freq):
        distance_freq[0] = 1

    literal_lengths = _huffman_lengths(literal_freq)
    distance_lengths = _huffman_lengths(distance_freq)
    last_literal = max(index for index, length in enumerate(literal_lengths) if length)
    last_distance = max(index for index, length in enumerate(distance_lengths) if length)
    literal_lengths = literal_lengths[:max(257, last_literal + 1)]
    distance_lengths = distance_lengths[:max(1, last_distance + 1)]
    literal_codes = {
        symbol: (reverse_bits(code, size), size)
        for symbol, (code, size) in canonical_codes(
            {index: length for index, length in enumerate(literal_lengths) if length}
        ).items()
    }
    distance_codes = {
        symbol: (reverse_bits(code, size), size)
        for symbol, (code, size) in canonical_codes(
            {index: length for index, length in enumerate(distance_lengths) if length}
        ).items()
    }

    code_length_tokens = _rle_code_lengths(literal_lengths + distance_lengths)
    code_length_freq = [0] * 19
    for symbol, _extra, _width in code_length_tokens:
        code_length_freq[symbol] += 1
    code_length_lengths = _huffman_lengths(code_length_freq, max_bits=7)
    code_length_codes = {
        symbol: (reverse_bits(code, size), size)
        for symbol, (code, size) in canonical_codes(
            {index: length for index, length in enumerate(code_length_lengths) if length}
        ).items()
    }
    order = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)
    last_code_length = max(
        index for index, symbol in enumerate(order) if code_length_lengths[symbol] > 0
    )

    writer = BitWriter(lsb_first=True)
    writer.write(1, 1)  # BFINAL
    writer.write(2, 2)  # BTYPE=dynamic
    writer.write(len(literal_lengths) - 257, 5)
    writer.write(len(distance_lengths) - 1, 5)
    writer.write(last_code_length - 3, 4)
    for symbol in order[:last_code_length + 1]:
        writer.write(code_length_lengths[symbol], 3)
    for symbol, extra, width in code_length_tokens:
        code, size = code_length_codes[symbol]
        writer.write(code, size)
        if width:
            writer.write(extra, width)
    for token in tokens:
        if isinstance(token, int):
            code, size = literal_codes[token]
            writer.write(code, size)
            continue
        length, distance = token
        symbol, extra, width = _length_code(length)
        code, size = literal_codes[symbol]
        writer.write(code, size)
        if width:
            writer.write(extra, width)
        symbol, extra, width = _distance_code(distance)
        code, size = distance_codes[symbol]
        writer.write(code, size)
        if width:
            writer.write(extra, width)
    code, size = literal_codes[256]
    writer.write(code, size)
    payload = b"\x78\x9c" + writer.finish() + struct.pack(">I", adler32(source))
    return _bounded_output(payload, max_output_bytes)


def inflate_deflate(
    stream: bytes | bytearray | memoryview,
    expected_size: int,
) -> bytes:
    """Decode a bounded zlib/Deflate stream without a codec dependency."""
    data = bytes(stream)
    expected_size = int(expected_size)
    if expected_size < 0:
        raise ValueError("Deflate expected size must be non-negative")
    if len(data) < 6:
        raise ValueError("truncated zlib wrapper")
    cmf, flags = data[0], data[1]
    if (cmf & 0x0F) != 8 or (cmf >> 4) > 7 or ((cmf << 8) | flags) % 31:
        raise ValueError("invalid zlib wrapper")
    if flags & 0x20:
        raise ValueError("preset-dictionary Deflate is unsupported")

    reader = BitReader(data[2:-4], lsb_first=True)
    output = bytearray()

    def ensure_capacity(count: int) -> None:
        if count < 0 or len(output) + count > expected_size:
            raise ValueError("Deflate output exceeds the expected strip size")

    final = 0
    while not final:
        final = reader.read(1)
        block_type = reader.read(2)
        if block_type == 0:
            reader.align()
            size = reader.read(16)
            inverse = reader.read(16)
            if size ^ inverse != 0xFFFF:
                raise ValueError("invalid stored Deflate block length")
            ensure_capacity(size)
            for _ in range(size):
                output.append(reader.read(8))
            continue
        if block_type == 1:
            literal_table = _FIXED_LITERAL_DECODE
            distance_table = _FIXED_DISTANCE_DECODE
        elif block_type == 2:
            literal_table, distance_table = _read_dynamic_tables(reader)
        else:
            raise ValueError("reserved Deflate block type")

        while True:
            symbol = _read_symbol(reader, literal_table)
            if symbol < 256:
                ensure_capacity(1)
                output.append(symbol)
                continue
            if symbol == 256:
                break
            if not 257 <= symbol <= 285:
                raise ValueError("invalid Deflate length symbol")
            index = symbol - 257
            length = _LENGTH_BASE[index]
            if _LENGTH_EXTRA[index]:
                length += reader.read(_LENGTH_EXTRA[index])
            distance_symbol = _read_symbol(reader, distance_table)
            if distance_symbol >= len(_DIST_BASE):
                raise ValueError("invalid Deflate distance symbol")
            distance = _DIST_BASE[distance_symbol]
            if _DIST_EXTRA[distance_symbol]:
                distance += reader.read(_DIST_EXTRA[distance_symbol])
            if distance > len(output):
                raise ValueError("Deflate distance exceeds output history")
            ensure_capacity(length)
            for _ in range(length):
                output.append(output[-distance])

    if len(output) != expected_size:
        raise ValueError("Deflate output length mismatch")
    if struct.unpack(">I", data[-4:])[0] != adler32(bytes(output)):
        raise ValueError("Deflate Adler-32 mismatch")
    return bytes(output)


__all__ = ["deflate_stored", "deflate_fixed", "deflate_dynamic", "inflate_deflate"]
