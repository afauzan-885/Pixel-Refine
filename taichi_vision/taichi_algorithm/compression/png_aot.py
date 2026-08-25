"""Dependency-free PNG encoder with Taichi row-filter acceleration.

The bitstream is intentionally implemented here instead of delegating to
zlib/libpng.  Both fixed- and dynamic-Huffman Deflate blocks are emitted by
the native path; the latter is the default because it is materially smaller
for photographic and filtered image data.  Pillow/zlib are used only by
external validation tests, never by this runtime module.
"""
from __future__ import annotations

import os
import struct
import math
from collections import deque
from pathlib import Path

import numpy as np

from .bitstream import BitReader, BitWriter, adler32, canonical_codes, crc32, reverse_bits


_LENGTH_BASE = (3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31,
                35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258)
_LENGTH_EXTRA = (0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
                 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0)
_DIST_BASE = (1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129,
              193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097,
              6145, 8193, 12289, 16385, 24577)
_DIST_EXTRA = (0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6,
               7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13)

_DEFAULT_MAX_PNG_CHUNK_BYTES = 256 * 1024 * 1024
_DEFAULT_MAX_PNG_SCANLINE_BYTES = 512 * 1024 * 1024
_PNG_FILTER_NAMES = ("none", "sub", "up", "average", "paeth")
_PNG_FILTER_NAME_TO_ID = {name: index for index, name in enumerate(_PNG_FILTER_NAMES)}
_DEFLATE_STRATEGIES = frozenset({"auto", "stored", "fixed", "dynamic"})
_DEFLATE_WINDOW_BYTES = 32768
_DEFLATE_POSITION_RING = _DEFLATE_WINDOW_BYTES + 1
_DEFLATE_MAX_SEARCH_DEPTH = 64


def _normalise_limit(name: str, value: int | None) -> int | None:
    if value is None:
        return None
    try:
        limit = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a non-negative integer or None") from exc
    if limit < 0:
        raise ValueError(f"{name} must be a non-negative integer or None")
    return limit


def _bounded_output(payload: bytes, limit: int | None, name: str) -> bytes:
    if limit is not None and len(payload) > limit:
        raise ValueError(f"{name} exceeds the configured limit")
    return payload


def _dispatch(*args, **kwargs):
    """Lazy AOT dispatch so importing container helpers stays side-effect free."""
    from taichi_vision.taichi_algorithm.aot_api.research import _dispatch as dispatch

    return dispatch(*args, **kwargs)


def _fixed_tables():
    lengths = {}
    lengths.update({symbol: 8 for symbol in range(0, 144)})
    lengths.update({symbol: 9 for symbol in range(144, 256)})
    lengths.update({symbol: 7 for symbol in range(256, 280)})
    lengths.update({symbol: 8 for symbol in range(280, 288)})
    literal = {symbol: (reverse_bits(code, size), size) for symbol, (code, size) in canonical_codes(lengths).items()}
    distances = {symbol: (reverse_bits(code, 5), 5) for symbol, (code, size) in canonical_codes({i: 5 for i in range(32)}).items()}
    return literal, distances


_FIXED_LITERAL, _FIXED_DISTANCE = _fixed_tables()


def _fixed_decode_map(table):
    return {(code, size): symbol for symbol, (code, size) in table.items()}


_FIXED_LITERAL_DECODE = _fixed_decode_map(_FIXED_LITERAL)
_FIXED_DISTANCE_DECODE = _fixed_decode_map(_FIXED_DISTANCE)


def _huffman_lengths(frequencies: list[int], max_bits: int = 15) -> list[int]:
    """Build bounded canonical code lengths from symbol frequencies.

    The image path normally produces a shallow tree.  The overflow repair is
    retained for adversarial histograms so a malformed Deflate tree cannot be
    generated merely by unusual input data.
    """
    import heapq

    active = [(int(freq), index, index) for index, freq in enumerate(frequencies) if freq > 0]
    lengths = [0] * len(frequencies)
    if not active:
        lengths[0] = 1
        return lengths
    if len(active) == 1:
        lengths[active[0][2]] = 1
        return lengths
    heapq.heapify(active)
    nodes = {}
    next_id = len(frequencies)
    order = len(frequencies)
    while len(active) > 1:
        first = heapq.heappop(active)
        second = heapq.heappop(active)
        node_id = next_id
        next_id += 1
        nodes[node_id] = (first[2], second[2])
        heapq.heappush(active, (first[0] + second[0], order, node_id))
        order += 1
    root = active[0][2]
    stack = [(root, 0)]
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
    # Preserve Kraft equality and the number of leaves while moving long
    # codes under the Deflate 15-bit limit.  Clamping first can create an
    # overfull tree for adversarial histograms.
    for bits in range(len(counts) - 1, max_bits, -1):
        while counts[bits] > 0:
            if counts[bits] < 2:
                raise ValueError("unable to bound Huffman tree")
            counts[bits] -= 2
            counts[bits - 1] += 1
            split = bits - 2
            while split > 0 and counts[split] == 0:
                split -= 1
            if split == 0:
                raise ValueError("unable to bound Huffman tree")
            counts[split] -= 1
            counts[split + 1] += 2
    ordered = sorted(
        (index for index, freq in enumerate(frequencies) if freq > 0),
        key=lambda index: (frequencies[index], index),
    )
    cursor = 0
    for bits in range(max_bits, 0, -1):
        for _ in range(counts[bits]):
            if cursor >= len(ordered):
                raise ValueError("invalid bounded Huffman histogram")
            lengths[ordered[cursor]] = bits
            cursor += 1
    if cursor != len(ordered):
        raise ValueError("incomplete bounded Huffman histogram")
    return lengths


def _lz77_tokens(data: bytes, search_depth: int = 1):
    """Yield literal or ``(length, distance)`` tokens.

    ``search_depth=1`` is the fast path used by DNG and interactive PNG.  A
    bounded recent-position search improves the best-size mode.  Position
    storage is a real 32 KiB sliding window: unlike a dictionary that merely
    ignores old candidates, it cannot retain one key per byte of a large
    image.  The candidate cap is also bounded so an accidental large
    ``search_depth`` cannot turn this into an unbounded compressor search.
    """
    search_depth = min(max(1, int(search_depth)), _DEFLATE_MAX_SEARCH_DEPTH)
    positions: dict[bytes, deque[int]] = {}
    position_ring: list[tuple[int, bytes] | None] = [None] * _DEFLATE_POSITION_RING

    def remember(position: int) -> None:
        """Remember one 3-byte probe and evict positions outside the window."""
        key = data[position:position + 3]
        if len(key) != 3:
            return
        expired = position - _DEFLATE_POSITION_RING
        if expired >= 0:
            slot = position_ring[expired % _DEFLATE_POSITION_RING]
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
        position_ring[position % _DEFLATE_POSITION_RING] = (position, key)

    index = 0
    size = len(data)
    while index < size:
        key = data[index:index + 3] if index + 2 < size else b""
        candidates = positions.get(key, ()) if key else ()
        best_length, best_distance = 0, 0
        for previous in list(candidates)[-search_depth:][::-1]:
            distance = index - previous
            if distance <= 0 or distance > _DEFLATE_WINDOW_BYTES:
                continue
            maximum = min(258, size - index)
            length = 0
            while length < maximum:
                history = previous + length if length < distance else previous + (length % distance)
                if data[history] != data[index + length]:
                    break
                length += 1
            if length > best_length:
                best_length, best_distance = length, distance
            if length == maximum:
                break
        if best_length >= 3:
            yield best_length, best_distance
            end = min(size, index + best_length)
            for cursor in range(index, end):
                remember(cursor)
            index += best_length
            continue
        yield data[index]
        remember(index)
        index += 1


def _rle_code_lengths(lengths: list[int]):
    """Return Deflate code-length alphabet symbols and extra fields."""
    result = []
    index = 0
    while index < len(lengths):
        value = lengths[index]
        run_end = index + 1
        while run_end < len(lengths) and lengths[run_end] == value:
            run_end += 1
        run = run_end - index
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
        index = run_end
    return result


def deflate_dynamic(
    data: bytes,
    search_depth: int = 8,
    *,
    max_output_bytes: int | None = None,
) -> bytes:
    """Return a zlib-wrapped dynamic-Huffman Deflate stream.

    This is a bounded native encoder.  It deliberately emits one final block
    so the output remains deterministic and easy to validate.  The filter and
    LZ77 preparation are the expensive image-dependent parts; the bit writer
    is kept host-side because output cardinality is variable.
    """
    max_output_bytes = _normalise_limit("max_output_bytes", max_output_bytes)
    tokens = list(_lz77_tokens(data, search_depth=search_depth))
    literal_freq = [0] * 286
    distance_freq = [0] * 30
    for token in tokens:
        if isinstance(token, int):
            literal_freq[token] += 1
            continue
        length, distance = token
        literal_freq[_length_code(length)[0]] += 1
        distance_freq[_distance_code(distance)[0]] += 1
    literal_freq[256] += 1
    if not any(distance_freq):
        distance_freq[0] = 1
    literal_lengths = _huffman_lengths(literal_freq)
    distance_lengths = _huffman_lengths(distance_freq)

    # HLIT/HDIST are counts, not fixed-size arrays.  Emitting all 286 literal
    # and 30 distance entries is valid Deflate, but wastes a large header when
    # an image uses only a small alphabet (constant/gradient images are common
    # PNG inputs).  Keep the EOB symbol and the last used distance symbol, as
    # required by RFC 1951, and trim only the trailing zero-length entries.
    last_literal = max(index for index, length in enumerate(literal_lengths) if length)
    last_distance = max(index for index, length in enumerate(distance_lengths) if length)
    literal_lengths = literal_lengths[:max(257, last_literal + 1)]
    distance_lengths = distance_lengths[:max(1, last_distance + 1)]
    literal_codes = {symbol: (reverse_bits(code, size), size) for symbol, (code, size) in canonical_codes({i: n for i, n in enumerate(literal_lengths) if n}).items()}
    distance_codes = {symbol: (reverse_bits(code, size), size) for symbol, (code, size) in canonical_codes({i: n for i, n in enumerate(distance_lengths) if n}).items()}

    code_length_values = literal_lengths + distance_lengths
    code_length_tokens = _rle_code_lengths(code_length_values)
    code_length_freq = [0] * 19
    for symbol, _extra, _bits in code_length_tokens:
        code_length_freq[symbol] += 1
    code_length_lengths = _huffman_lengths(code_length_freq, max_bits=7)
    code_length_codes = {symbol: (reverse_bits(code, size), size) for symbol, (code, size) in canonical_codes({i: n for i, n in enumerate(code_length_lengths) if n}).items()}
    order = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)
    last = max(index for index, symbol in enumerate(order) if code_length_lengths[symbol] > 0)

    writer = BitWriter(lsb_first=True)
    writer.write(1, 1)
    writer.write(2, 2)
    writer.write(len(literal_lengths) - 257, 5)
    writer.write(len(distance_lengths) - 1, 5)
    writer.write(last - 3, 4)
    for symbol in order[:last + 1]:
        writer.write(code_length_lengths[symbol], 3)
    for symbol, extra, extra_bits in code_length_tokens:
        code, size = code_length_codes[symbol]
        writer.write(code, size)
        if extra_bits:
            writer.write(extra, extra_bits)
    for token in tokens:
        if isinstance(token, int):
            code, size = literal_codes[token]
            writer.write(code, size)
            continue
        length, distance = token
        symbol, extra, extra_bits = _length_code(length)
        code, size = literal_codes[symbol]
        writer.write(code, size)
        if extra_bits:
            writer.write(extra, extra_bits)
        symbol, extra, extra_bits = _distance_code(distance)
        code, size = distance_codes[symbol]
        writer.write(code, size)
        if extra_bits:
            writer.write(extra, extra_bits)
    code, size = literal_codes[256]
    writer.write(code, size)
    return _bounded_output(
        b"\x78\x9c" + writer.finish() + struct.pack(">I", adler32(data)),
        max_output_bytes,
        "Deflate output",
    )


def deflate_best(
    data: bytes,
    effort: str = "best",
    *,
    strategy: str = "auto",
    max_output_bytes: int | None = None,
) -> bytes:
    """Select a deterministic native Deflate strategy.

    ``strategy='auto'`` preserves the historical ``effort`` behavior while
    allowing the encoder to reject a dynamic block that is larger than a
    fixed or stored block.  Explicit strategies are useful for reproducible
    size/latency profiles and never invoke a system codec library.
    """
    effort = str(effort).lower()
    strategy = str(strategy).lower()
    if strategy not in _DEFLATE_STRATEGIES:
        raise ValueError("Deflate strategy must be auto, stored, fixed, or dynamic")
    max_output_bytes = _normalise_limit("max_output_bytes", max_output_bytes)
    if effort not in {"fast", "balanced", "best"}:
        raise ValueError("Deflate effort must be fast, balanced, or best")
    if strategy == "stored":
        return deflate_stored(data, max_output_bytes=max_output_bytes)
    if strategy == "fixed":
        return deflate_fixed(data, max_output_bytes=max_output_bytes)
    if strategy == "dynamic":
        depth = {"fast": 1, "balanced": 4, "best": 16}[effort]
        return deflate_dynamic(data, search_depth=depth, max_output_bytes=max_output_bytes)

    # Fast is intentionally one-pass.  Balanced uses dynamic Huffman because
    # it is normally smaller, while best compares the bounded candidates and
    # chooses the shortest deterministic stream.  Candidate streams are
    # built without the caller's limit so a larger candidate cannot abort a
    # valid smaller one before the final bound is checked.
    if effort == "fast":
        selected = deflate_fixed(data)
    elif effort == "balanced":
        dynamic = deflate_dynamic(data, search_depth=4)
        fixed = deflate_fixed(data)
        selected = min((dynamic, fixed), key=len)
    else:
        dynamic = deflate_dynamic(data, search_depth=16)
        fixed = deflate_fixed(data)
        stored = deflate_stored(data)
        selected = min((dynamic, fixed, stored), key=len)
    return _bounded_output(selected, max_output_bytes, "Deflate output")


def _length_code(length: int) -> tuple[int, int, int]:
    if not 3 <= length <= 258:
        raise ValueError("Deflate match length out of range")
    for index, base in enumerate(_LENGTH_BASE):
        limit = base + ((1 << _LENGTH_EXTRA[index]) - 1)
        if length <= limit or index == len(_LENGTH_BASE) - 1:
            return 257 + index, length - base, _LENGTH_EXTRA[index]
    raise AssertionError("unreachable")


def _distance_code(distance: int) -> tuple[int, int, int]:
    if not 1 <= distance <= 32768:
        raise ValueError("Deflate distance out of range")
    for index, base in enumerate(_DIST_BASE):
        limit = base + ((1 << _DIST_EXTRA[index]) - 1)
        if distance <= limit:
            return index, distance - base, _DIST_EXTRA[index]
    raise AssertionError("unreachable")


def _find_match(data: bytes, index: int, previous: int | None) -> tuple[int, int]:
    if previous is None or index - previous > 32768 or index + 2 >= len(data):
        return 0, 0
    length = 0
    distance = index - previous
    maximum = min(258, len(data) - index)
    while length < maximum:
        history_index = previous + length if length < distance else previous + (length % distance)
        if data[history_index] != data[index + length]:
            break
        length += 1
    return length, index - previous


def deflate_stored(data: bytes, *, max_output_bytes: int | None = None) -> bytes:
    """Return a zlib-wrapped stored Deflate stream without external codecs.

    Stored blocks are deliberately exposed as a safety/diagnostic strategy:
    they have predictable CPU cost and are useful when incompressible input
    would otherwise pay Huffman/LZ77 overhead.  They remain fully conforming
    PNG Deflate and are split at the RFC 1951 65535-byte block limit.
    """
    max_output_bytes = _normalise_limit("max_output_bytes", max_output_bytes)
    source = memoryview(bytes(data)).cast("B")
    output = bytearray(b"\x78\x01")
    if not source:
        # BFINAL=1, BTYPE=00, followed by five alignment zero bits.
        output.extend(b"\x01\x00\x00\xff\xff")
    else:
        offset = 0
        while offset < len(source):
            end = min(offset + 65535, len(source))
            final = end == len(source)
            output.append(1 if final else 0)
            size = end - offset
            output.extend(struct.pack("<HH", size, size ^ 0xFFFF))
            output.extend(source[offset:end])
            offset = end
    output.extend(struct.pack(">I", adler32(bytes(source))))
    return _bounded_output(bytes(output), max_output_bytes, "Deflate output")


def deflate_fixed(data: bytes, *, max_output_bytes: int | None = None) -> bytes:
    """Return a zlib-wrapped Deflate stream without importing zlib."""
    max_output_bytes = _normalise_limit("max_output_bytes", max_output_bytes)
    writer = BitWriter(lsb_first=True)
    writer.write(1, 1)  # final block
    writer.write(1, 2)  # fixed Huffman block
    for token in _lz77_tokens(data, search_depth=1):
        if isinstance(token, int):
            code, size = _FIXED_LITERAL[token]
            writer.write(code, size)
            continue
        length, distance = token
        length_symbol, length_extra, length_bits = _length_code(length)
        code, size = _FIXED_LITERAL[length_symbol]
        writer.write(code, size)
        if length_bits:
            writer.write(length_extra, length_bits)
        distance_symbol, distance_extra, distance_bits = _distance_code(distance)
        code, size = _FIXED_DISTANCE[distance_symbol]
        writer.write(code, size)
        if distance_bits:
            writer.write(distance_extra, distance_bits)
    code, size = _FIXED_LITERAL[256]
    writer.write(code, size)
    payload = writer.finish()
    return _bounded_output(
        b"\x78\x01" + payload + struct.pack(">I", adler32(data)),
        max_output_bytes,
        "Deflate output",
    )


def _read_huffman_symbol(reader: BitReader, table: dict[tuple[int, int], int]) -> int:
    code = 0
    for size in range(1, 16):
        code |= reader.read(1) << (size - 1)
        symbol = table.get((code, size))
        if symbol is not None:
            return symbol
    raise ValueError("invalid fixed-Huffman symbol")


def _decode_huffman_table(lengths: list[int], max_bits: int = 15) -> dict[tuple[int, int], int]:
    if not any(lengths):
        raise ValueError("empty Deflate Huffman table")
    if max(lengths) > max_bits:
        raise ValueError("Deflate Huffman code exceeds maximum length")
    codes = canonical_codes({index: length for index, length in enumerate(lengths) if length})
    return {(reverse_bits(code, size), size): symbol for symbol, (code, size) in codes.items()}


def _read_dynamic_tables(reader: BitReader):
    literal_count = reader.read(5) + 257
    distance_count = reader.read(5) + 1
    code_length_count = reader.read(4) + 4
    if literal_count > 286 or distance_count > 32:
        raise ValueError("invalid Deflate dynamic table sizes")
    order = (16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15)
    code_length_lengths = [0] * 19
    for symbol in order[:code_length_count]:
        code_length_lengths[symbol] = reader.read(3)
    code_length_table = _decode_huffman_table(code_length_lengths, max_bits=7)
    all_lengths = []
    total = literal_count + distance_count
    while len(all_lengths) < total:
        symbol = _read_huffman_symbol(reader, code_length_table)
        if symbol <= 15:
            all_lengths.append(symbol)
        elif symbol == 16:
            if not all_lengths:
                raise ValueError("Deflate repeat has no previous code length")
            repeat = reader.read(2) + 3
            all_lengths.extend([all_lengths[-1]] * repeat)
        elif symbol == 17:
            repeat = reader.read(3) + 3
            all_lengths.extend([0] * repeat)
        elif symbol == 18:
            repeat = reader.read(7) + 11
            all_lengths.extend([0] * repeat)
        else:
            raise ValueError("invalid Deflate code-length symbol")
        if len(all_lengths) > total:
            raise ValueError("Deflate code-length repeat exceeds table")
    literal_lengths = all_lengths[:literal_count]
    distance_lengths = all_lengths[literal_count:]
    if literal_lengths[256] == 0:
        raise ValueError("Deflate literal table has no end-of-block symbol")
    return _decode_huffman_table(literal_lengths), _decode_huffman_table(distance_lengths)


def inflate_deflate(
    stream: bytes,
    expected_size: int | None = None,
    *,
    max_output_size: int | None = None,
) -> bytes:
    """Decode stored, fixed, or dynamic-Huffman zlib Deflate data.

    ``max_output_size`` is an explicit decompression-bomb guard for callers
    that validate untrusted containers.  ``expected_size`` also acts as a
    hard cap because PNG/DNG callers know the exact strip or scanline size.
    """
    if expected_size is not None and int(expected_size) < 0:
        raise ValueError("Deflate expected size must be non-negative")
    if max_output_size is not None and int(max_output_size) < 0:
        raise ValueError("Deflate maximum output size must be non-negative")
    output_limit = None if max_output_size is None else int(max_output_size)
    if expected_size is not None:
        output_limit = int(expected_size) if output_limit is None else min(output_limit, int(expected_size))

    def ensure_capacity(additional: int) -> None:
        if output_limit is not None and len(output) + int(additional) > output_limit:
            raise ValueError("Deflate output exceeds the configured limit")

    if len(stream) < 6 or (stream[0] & 0x0F) != 8 or ((stream[0] << 8) | stream[1]) % 31:
        raise ValueError("invalid zlib wrapper")
    reader = BitReader(stream[2:-4], lsb_first=True)
    output = bytearray()
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
            literal_table, distance_table = _FIXED_LITERAL_DECODE, _FIXED_DISTANCE_DECODE
        elif block_type == 2:
            literal_table, distance_table = _read_dynamic_tables(reader)
        else:
            raise ValueError("reserved Deflate block type")
        while True:
            symbol = _read_huffman_symbol(reader, literal_table)
            if symbol < 256:
                ensure_capacity(1)
                output.append(symbol)
            elif symbol == 256:
                break
            elif 257 <= symbol <= 285:
                index = symbol - 257
                length = _LENGTH_BASE[index] + (reader.read(_LENGTH_EXTRA[index]) if _LENGTH_EXTRA[index] else 0)
                distance_symbol = _read_huffman_symbol(reader, distance_table)
                if distance_symbol >= len(_DIST_BASE):
                    raise ValueError("invalid Deflate distance symbol")
                distance = _DIST_BASE[distance_symbol] + (reader.read(_DIST_EXTRA[distance_symbol]) if _DIST_EXTRA[distance_symbol] else 0)
                if distance > len(output):
                    raise ValueError("Deflate distance exceeds output history")
                ensure_capacity(length)
                for _ in range(length):
                    output.append(output[-distance])
            else:
                raise ValueError("invalid Deflate length symbol")
    if expected_size is not None and len(output) != expected_size:
        raise ValueError("Deflate output length mismatch")
    if struct.unpack(">I", stream[-4:])[0] != adler32(bytes(output)):
        raise ValueError("Deflate Adler-32 mismatch")
    return bytes(output)


def inflate_fixed(
    stream: bytes,
    expected_size: int | None = None,
    *,
    max_output_size: int | None = None,
) -> bytes:
    """Backward-compatible name for the internal Deflate validator."""
    return inflate_deflate(stream, expected_size, max_output_size=max_output_size)


def _paeth(a: int, b: int, c: int) -> int:
    estimate = a + b - c
    pa, pb, pc = abs(estimate - a), abs(estimate - b), abs(estimate - c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def _normalise_filter_strategy(value: str | int) -> str:
    if isinstance(value, (int, np.integer)):
        index = int(value)
        if not 0 <= index < len(_PNG_FILTER_NAMES):
            raise ValueError("PNG filter strategy integer must be in the range 0..4")
        return _PNG_FILTER_NAMES[index]
    strategy = str(value).strip().lower().replace("-", "_")
    aliases = {
        "minimum": "adaptive",
        "minimum_sum": "adaptive",
        "min_sum": "adaptive",
        "heuristic": "adaptive",
    }
    strategy = aliases.get(strategy, strategy)
    if strategy not in _PNG_FILTER_NAME_TO_ID and strategy != "adaptive":
        raise ValueError(
            "PNG filter strategy must be adaptive, none, sub, up, average, or paeth"
        )
    return strategy


def _filter_rows_host(
    raw: np.ndarray,
    bytes_per_pixel: int,
    filter_strategy: str = "adaptive",
) -> tuple[np.ndarray, np.ndarray]:
    height, row_bytes = raw.shape
    filter_strategy = _normalise_filter_strategy(filter_strategy)
    candidates = (
        range(5)
        if filter_strategy == "adaptive"
        else (_PNG_FILTER_NAME_TO_ID[filter_strategy],)
    )
    output = np.empty_like(raw, dtype=np.int32)
    types = np.empty(height, dtype=np.int32)
    for y in range(height):
        best_cost = None
        best_type = 0
        best = None
        for candidate in candidates:
            row = np.empty(row_bytes, dtype=np.int32)
            cost = 0
            for x in range(row_bytes):
                value = int(raw[y, x])
                left = int(raw[y, x - bytes_per_pixel]) if x >= bytes_per_pixel else 0
                above = int(raw[y - 1, x]) if y else 0
                upper_left = int(raw[y - 1, x - bytes_per_pixel]) if y and x >= bytes_per_pixel else 0
                predictor = (0, left, above, (left + above) // 2, _paeth(left, above, upper_left))[candidate]
                residual = (value - predictor) & 255
                row[x] = residual
                cost += min(residual, 256 - residual)
            if best_cost is None or cost < best_cost:
                best_cost, best_type, best = cost, candidate, row
        types[y] = best_type
        output[y] = best
    return output, types


def _filter_rows(
    raw: np.ndarray,
    bytes_per_pixel: int,
    filter_strategy: str = "adaptive",
) -> tuple[np.ndarray, np.ndarray]:
    filter_strategy = _normalise_filter_strategy(filter_strategy)
    filter_selector = (
        -1
        if filter_strategy == "adaptive"
        else _PNG_FILTER_NAME_TO_ID[filter_strategy]
    )
    try:
        result = _dispatch(
            "compression_image",
            "compression_png_filter_rows",
            inputs={"src": np.ascontiguousarray(raw, dtype=np.int32)},
            outputs={"dst": np.empty_like(raw, dtype=np.int32), "filter_types": np.empty(raw.shape[0], dtype=np.int32)},
            scalars={
                "height": raw.shape[0],
                "row_bytes": raw.shape[1],
                "bytes_per_pixel": bytes_per_pixel,
                "filter_selector": filter_selector,
            },
            plain_ndarray=False,
        )
        return np.asarray(result["dst"], dtype=np.int32), np.asarray(result["filter_types"], dtype=np.int32)
    except Exception as exc:
        # A production AOT call must not silently move the image stage to the
        # host.  Developers can opt into the reference implementation for
        # isolated algorithm work, but the error remains visible by default.
        if os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") != "1":
            raise RuntimeError(
                "compression_png_filter_rows is unavailable for the selected AOT target; "
                "compile the matching compression_image.tcm or set "
                "AOT_ALLOW_HOST_FALLBACK=1 for an explicit reference run"
            ) from exc
        return _filter_rows_host(raw, bytes_per_pixel, filter_strategy)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    if len(kind) != 4:
        raise ValueError("PNG chunk type must be four bytes")
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc32(kind + payload))


def parse_png_aot(
    data: bytes | bytearray | str | os.PathLike[str],
    *,
    max_chunks: int = 4096,
    max_chunk_bytes: int | None = _DEFAULT_MAX_PNG_CHUNK_BYTES,
    max_scanline_bytes: int | None = _DEFAULT_MAX_PNG_SCANLINE_BYTES,
) -> dict:
    """Validate a native PNG structure and a bounded IDAT scanline stream."""
    raw = Path(data).read_bytes() if isinstance(data, (str, os.PathLike)) else bytes(data)
    signature = b"\x89PNG\r\n\x1a\n"
    if len(raw) < len(signature) or raw[:8] != signature:
        raise ValueError("not a PNG stream")
    if max_chunks <= 0:
        raise ValueError("PNG chunk limit must be positive")
    max_chunk_bytes = _normalise_limit("max_chunk_bytes", max_chunk_bytes)
    max_scanline_bytes = _normalise_limit("max_scanline_bytes", max_scanline_bytes)
    offset = 8
    chunks = []
    idat_parts = []
    seen_idat = False
    seen_iend = False
    ihdr = None
    palette = None
    transparency = None
    idat_closed = False
    seen_plte = False
    seen_trns = False
    while offset < len(raw):
        if len(chunks) >= max_chunks:
            raise ValueError("PNG chunk limit exceeded")
        if len(raw) - offset < 12:
            raise ValueError("truncated PNG chunk")
        length = struct.unpack(">I", raw[offset:offset + 4])[0]
        if max_chunk_bytes is not None and length > max_chunk_bytes:
            raise ValueError("PNG chunk exceeds the configured limit")
        kind = raw[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        if payload_end > len(raw) or crc_end > len(raw):
            raise ValueError("PNG chunk exceeds file bounds")
        payload = raw[payload_start:payload_end]
        expected_crc = struct.unpack(">I", raw[payload_end:crc_end])[0]
        if crc32(kind + payload) != expected_crc:
            raise ValueError("PNG chunk CRC mismatch")
        chunks.append((kind, payload))
        if not chunks[:-1] and kind != b"IHDR":
            raise ValueError("PNG IHDR must be the first chunk")
        if kind == b"IHDR":
            if ihdr is not None or len(payload) != 13:
                raise ValueError("invalid PNG IHDR")
            width, height, bit_depth, color_type, compression_method, filter_method, interlace = struct.unpack(">IIBBBBB", payload)
            if width <= 0 or height <= 0 or compression_method != 0 or filter_method != 0 or interlace != 0:
                raise ValueError("unsupported PNG geometry or method")
            valid_depths = {
                0: (1, 2, 4, 8, 16),
                2: (8, 16),
                3: (1, 2, 4, 8),
                4: (8, 16),
                6: (8, 16),
            }
            if color_type not in valid_depths or bit_depth not in valid_depths[color_type]:
                raise ValueError("unsupported PNG color type or bit depth")
            ihdr = (width, height, bit_depth, color_type)
        elif kind == b"PLTE":
            if seen_plte or seen_idat or ihdr is None or len(payload) == 0 or len(payload) % 3 or len(payload) > 768:
                raise ValueError("invalid PNG palette placement or length")
            if ihdr[3] in (0, 4):
                raise ValueError("PNG palette is invalid for grayscale color types")
            if ihdr[3] == 3 and len(payload) // 3 > (1 << ihdr[2]):
                raise ValueError("PNG palette exceeds indexed bit depth")
            palette = payload
            seen_plte = True
        elif kind == b"tRNS":
            if seen_idat or seen_trns or ihdr is None or not payload:
                raise ValueError("invalid PNG tRNS placement or multiplicity")
            if ihdr[3] == 3 and palette is None:
                raise ValueError("indexed PNG tRNS requires PLTE first")
            transparency = payload
            seen_trns = True
        elif kind == b"IDAT":
            if ihdr is None or seen_iend or idat_closed:
                raise ValueError("PNG IDAT is out of order")
            seen_idat = True
            idat_parts.append(payload)
        elif kind == b"IEND":
            if seen_iend or payload or not seen_idat:
                raise ValueError("invalid PNG IEND")
            seen_iend = True
        elif seen_idat:
            # PNG IDAT chunks must form one consecutive run.  Ancillary
            # chunks may appear around that run, but never inside it.
            idat_closed = True
        offset = crc_end
        if seen_iend and offset != len(raw):
            raise ValueError("PNG has trailing data after IEND")
    if ihdr is None or not seen_idat or not seen_iend:
        raise ValueError("PNG is missing IHDR, IDAT, or IEND")
    width, height, bit_depth, color_type = ihdr
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color_type]
    if color_type == 3 and palette is None:
        raise ValueError("indexed PNG is missing PLTE")
    if transparency is not None:
        if color_type == 3 and (palette is None or len(transparency) > len(palette) // 3):
            raise ValueError("PNG palette transparency exceeds entries")
        if color_type == 0 and len(transparency) != 2:
            raise ValueError("invalid grayscale PNG tRNS")
        if color_type == 2 and len(transparency) != 6:
            raise ValueError("invalid RGB PNG tRNS")
        if color_type in (4, 6):
            raise ValueError("PNG tRNS is invalid for alpha color types")
    row_bytes = (width * channels * bit_depth + 7) // 8
    expected_scanline_bytes = (row_bytes + 1) * height
    if max_scanline_bytes is not None and expected_scanline_bytes > max_scanline_bytes:
        raise ValueError("PNG scanline payload exceeds the configured limit")
    scanlines = inflate_deflate(
        b"".join(idat_parts),
        expected_size=expected_scanline_bytes,
        max_output_size=max_scanline_bytes,
    )
    filter_stride = row_bytes + 1
    if any(scanlines[row * filter_stride] > 4 for row in range(height)):
        raise ValueError("PNG scanline contains an invalid filter type")
    return {
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_type,
        "channels": channels,
        "chunks": tuple(kind for kind, _payload in chunks),
        "scanline_bytes": len(scanlines),
    }


def _as_png_bytes(image):
    data = np.asarray(image)
    if data.ndim == 2:
        data = data[..., None]
    if data.ndim != 3 or data.shape[2] not in (1, 2, 3, 4):
        raise ValueError("PNG input must be HxW, HxWx2, HxWx3, or HxWx4")
    if data.dtype not in (np.uint8, np.uint16):
        raise ValueError("PNG input dtype must be uint8 or uint16")
    height, width, channels = data.shape
    if height <= 0 or width <= 0:
        raise ValueError("PNG input dimensions must be positive")
    bit_depth = 8 if data.dtype == np.uint8 else 16
    if bit_depth == 16:
        data = data.astype(">u2", copy=False)
    else:
        data = np.ascontiguousarray(data, dtype=np.uint8)
    raw = data.view(np.uint8).reshape(height, width * channels * (bit_depth // 8)).astype(np.int32, copy=False)
    return data, raw, height, width, channels, bit_depth


def _palette_bytes(value) -> bytes:
    if isinstance(value, (bytes, bytearray, memoryview)):
        palette = bytes(value)
    else:
        array = np.asarray(value)
        if array.ndim != 2 or array.shape[1] != 3:
            raise ValueError("PNG palette must have shape (entries, 3)")
        if array.dtype.kind not in "ui" or np.any(array < 0) or np.any(array > 255):
            raise ValueError("PNG palette values must be integers in [0, 255]")
        palette = np.ascontiguousarray(array, dtype=np.uint8).tobytes()
    if len(palette) == 0 or len(palette) % 3 or len(palette) > 256 * 3:
        raise ValueError("PNG palette must contain 1..256 RGB entries")
    return palette


def _png_keyword(value) -> bytes:
    keyword = str(value).encode("latin-1")
    if not 1 <= len(keyword) <= 79 or b"\x00" in keyword:
        raise ValueError("PNG keyword must be 1..79 bytes without NUL")
    return keyword


def _png_transparency_bytes(value, channels: int, bit_depth: int, palette: bytes | None) -> bytes:
    """Normalise PNG ``tRNS`` metadata for indexed/gray/RGB images."""
    if palette is not None:
        if isinstance(value, (bytes, bytearray, memoryview)):
            result = bytes(value)
        else:
            try:
                result = bytes(int(item) for item in value)
            except (TypeError, ValueError) as exc:
                raise TypeError("PNG palette tRNS must be bytes or an iterable of alpha values") from exc
        if not result:
            raise ValueError("PNG palette tRNS must contain at least one alpha value")
        if len(result) > len(palette) // 3:
            raise ValueError("PNG tRNS palette alpha exceeds palette entries")
        return result

    if channels not in (1, 3):
        raise ValueError("PNG tRNS is supported only for grayscale, RGB, or indexed images")
    expected = channels
    sample_limit = (1 << bit_depth) - 1
    if isinstance(value, (bytes, bytearray, memoryview)):
        result = bytes(value)
        if len(result) != expected * 2:
            raise ValueError(f"PNG tRNS requires {expected * 2} bytes for this color type")
        return result
    if channels == 1:
        if isinstance(value, (tuple, list, np.ndarray)):
            values = tuple(value)
        else:
            values = (value,)
    else:
        try:
            values = tuple(value)
        except TypeError as exc:
            raise TypeError("RGB PNG tRNS must be an iterable of three sample values") from exc
    if len(values) != expected:
        raise ValueError(f"PNG tRNS requires {expected} sample values")
    samples = []
    for sample in values:
        sample = int(sample)
        if not 0 <= sample <= sample_limit:
            raise ValueError("PNG tRNS sample is outside the image bit depth")
        samples.append(sample)
    return b"".join(struct.pack(">H", sample) for sample in samples)


def encode_png_aot(
    image,
    metadata: dict | None = None,
    compression: str = "dynamic",
    effort: str = "best",
    max_output_bytes: int | None = None,
    filter_strategy: str | int = "adaptive",
    deflate_strategy: str | None = None,
) -> bytes:
    """Encode RGB/gray 8/16-bit data to a lossless PNG stream.

    ``compression='dynamic'`` is the backward-compatible request for the
    adaptive ``deflate_strategy='auto'`` profile.  ``filter_strategy`` may be
    ``adaptive`` (the default), or one of the five PNG filters.  Adaptive and
    forced modes use the same TCM graph with a validated scalar selector.
    ``deflate_strategy`` accepts ``auto``,
    ``stored``, ``fixed``, or ``dynamic``; the old ``compression='fixed'``
    spelling remains supported.
    """
    compression = str(compression).lower()
    if compression not in {"fixed", "dynamic", "stored"}:
        raise ValueError("PNG compression must be fixed, dynamic, or stored")
    filter_strategy = _normalise_filter_strategy(filter_strategy)
    if deflate_strategy is None:
        deflate_strategy = {
            "fixed": "fixed",
            "dynamic": "auto",
            "stored": "stored",
        }[compression]
    else:
        deflate_strategy = str(deflate_strategy).lower()
    if deflate_strategy not in _DEFLATE_STRATEGIES:
        raise ValueError("PNG Deflate strategy must be auto, stored, fixed, or dynamic")
    max_output_bytes = _normalise_limit("max_output_bytes", max_output_bytes)
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("PNG metadata must be a mapping")
    if metadata and "icc" in metadata and "srgb" in metadata:
        raise ValueError("PNG metadata cannot contain both iCCP and sRGB color profiles")
    data, raw, height, width, channels, bit_depth = _as_png_bytes(image)
    palette = _palette_bytes(metadata["palette"]) if metadata and "palette" in metadata else None
    transparency = (
        _png_transparency_bytes(metadata["trns"], channels, bit_depth, palette)
        if metadata and "trns" in metadata
        else None
    )
    if palette is not None:
        if bit_depth != 8 or channels != 1:
            raise ValueError("indexed PNG output requires an 8-bit single-channel input")
        if np.any(data[..., 0] >= len(palette) // 3):
            raise ValueError("indexed PNG sample exceeds the supplied palette")
    elif transparency is not None and channels not in (1, 3):
        raise ValueError("PNG tRNS is invalid for images with an alpha channel")
    bytes_per_pixel = 1 if palette is not None else channels * (bit_depth // 8)
    filtered, filter_types = _filter_rows(raw, bytes_per_pixel, filter_strategy)
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(int(filter_types[y]))
        scanlines.extend(int(value) & 255 for value in filtered[y])
    color_type = {1: 0, 2: 4, 3: 2, 4: 6}[channels]
    if palette is not None:
        color_type = 3
    output = bytearray(b"\x89PNG\r\n\x1a\n")

    def append_chunk(kind: bytes, payload: bytes) -> None:
        chunk = _chunk(kind, payload)
        if max_output_bytes is not None and len(output) + len(chunk) > max_output_bytes:
            raise ValueError("PNG output exceeds the configured limit")
        output.extend(chunk)

    append_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, bit_depth, color_type, 0, 0, 0))
    if palette is not None:
        append_chunk(b"PLTE", palette)
    if transparency is not None:
        append_chunk(b"tRNS", transparency)
    resolution_written = False
    for key, value in (metadata or {}).items():
        if key in {"palette", "trns"}:
            continue
        if key == "text":
            if not isinstance(value, dict):
                raise TypeError("PNG text metadata must be a mapping")
            for text_key, text_value in value.items():
                append_chunk(b"tEXt", _png_keyword(text_key) + b"\x00" + str(text_value).encode("latin-1"))
        elif key == "itxt":
            if not isinstance(value, dict):
                raise TypeError("PNG iTXt metadata must be a mapping")
            for text_key, text_value in value.items():
                keyword = _png_keyword(text_key)
                if isinstance(text_value, tuple) and len(text_value) == 3:
                    language, translated, text_value = text_value
                else:
                    language, translated = "", ""
                payload = (
                    keyword + b"\x00\x00\x00" + str(language).encode("ascii") + b"\x00"
                    + str(translated).encode("utf-8") + b"\x00" + str(text_value).encode("utf-8")
                )
                append_chunk(b"iTXt", payload)
        elif key == "exif":
            exif = bytes(value)
            append_chunk(b"eXIf", exif)
        elif key == "gamma":
            gamma = float(value)
            if not math.isfinite(gamma) or gamma <= 0.0:
                raise ValueError("PNG gamma must be a finite positive number")
            scaled = int(round(gamma * 100000.0))
            if not 0 < scaled <= 0xFFFFFFFF:
                raise ValueError("PNG gamma is outside the gAMA range")
            append_chunk(b"gAMA", struct.pack(">I", scaled))
        elif key == "srgb":
            intent = int(value)
            if intent not in (0, 1, 2, 3):
                raise ValueError("PNG sRGB rendering intent must be in the range 0..3")
            append_chunk(b"sRGB", bytes((intent,)))
        elif key == "icc":
            profile_name = "Pixel Refine ICC"
            profile = value
            if isinstance(value, tuple) and len(value) == 2:
                profile_name, profile = value
            profile_name = str(profile_name).encode("latin-1")
            if not profile_name or len(profile_name) > 79 or b"\x00" in profile_name:
                raise ValueError("PNG ICC profile name must be 1..79 bytes without NUL")
            profile_stream = deflate_best(bytes(profile), effort="balanced")
            append_chunk(b"iCCP", profile_name + b"\x00\x00" + profile_stream)
        elif key == "phys":
            if resolution_written:
                raise ValueError("PNG metadata may contain only one pHYs chunk")
            if len(value) != 3:
                raise ValueError("PNG phys metadata must be (pixels_per_unit_x, pixels_per_unit_y, unit)")
            x_ppu, y_ppu, unit = (int(part) for part in value)
            if min(x_ppu, y_ppu) < 0 or unit not in (0, 1):
                raise ValueError("PNG phys values are out of range")
            append_chunk(b"pHYs", struct.pack(">IIB", x_ppu, y_ppu, unit))
            resolution_written = True
        elif key == "dpi":
            if resolution_written:
                raise ValueError("PNG metadata may contain only one pHYs chunk")
            if len(value) != 2:
                raise ValueError("PNG dpi metadata must be (x_dpi, y_dpi)")
            x_dpi, y_dpi = (int(part) for part in value)
            if min(x_dpi, y_dpi) < 0 or max(x_dpi, y_dpi) > 0xFFFFFFFF:
                raise ValueError("PNG dpi values are out of range")
            # Convert pixels/inch to pixels/metre, rounded to the nearest
            # integer as required by pHYs.  Keep zero as zero for explicit
            # unknown-resolution metadata.
            x_ppm = int(round(x_dpi * 39.37007874015748))
            y_ppm = int(round(y_dpi * 39.37007874015748))
            if max(x_ppm, y_ppm) > 0xFFFFFFFF:
                raise ValueError("PNG dpi conversion exceeds pHYs range")
            append_chunk(b"pHYs", struct.pack(">IIB", x_ppm, y_ppm, 1))
            resolution_written = True
        elif key == "time":
            if len(value) != 6:
                raise ValueError("PNG time metadata must be (year, month, day, hour, minute, second)")
            year, month, day, hour, minute, second = (int(part) for part in value)
            if not 0 <= year <= 0xFFFF or not 1 <= month <= 12 or not 1 <= day <= 31:
                raise ValueError("PNG time date is out of range")
            if not 0 <= hour <= 23 or not 0 <= minute <= 59 or not 0 <= second <= 60:
                raise ValueError("PNG time clock is out of range")
            append_chunk(b"tIME", struct.pack(">H5B", year, month, day, hour, minute, second))
        else:
            raise ValueError(f"unsupported PNG metadata key: {key}")
    idat_limit = None
    if max_output_bytes is not None:
        idat_limit = max_output_bytes - len(output) - 24
        if idat_limit < 0:
            raise ValueError("PNG output limit is smaller than the container header")
    compressed = deflate_best(
        bytes(scanlines),
        effort,
        strategy=deflate_strategy,
        max_output_bytes=idat_limit,
    )
    append_chunk(b"IDAT", compressed)
    append_chunk(b"IEND", b"")
    return bytes(output)


def save_png_aot(
    image,
    path: str | os.PathLike[str],
    metadata: dict | None = None,
    compression: str = "dynamic",
    effort: str = "best",
    max_output_bytes: int | None = None,
    filter_strategy: str | int = "adaptive",
    deflate_strategy: str | None = None,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(
        encode_png_aot(
            image,
            metadata,
            compression,
            effort,
            max_output_bytes,
            filter_strategy,
            deflate_strategy,
        )
    )
    temporary.replace(target)


__all__ = [
    "deflate_stored",
    "deflate_fixed",
    "deflate_dynamic",
    "deflate_best",
    "inflate_deflate",
    "inflate_fixed",
    "parse_png_aot",
    "encode_png_aot",
    "save_png_aot",
]
