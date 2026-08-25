"""Dependency-free RIFF/WebP helpers and a validated VP8L encoder.

The maintained lossless subset emits literal VP8L symbols and a bounded
exact-pixel LZ77 profile with canonical Huffman trees.  It also evaluates the
spec-defined subtract-green and predictor transforms when they can reduce the
stream.  The predictor transform uses a spec-defined auxiliary image and
deterministic per-block mode selection.  Color transform, color cache, lossy
VP8, animation, and the full target matrix remain separate production gates.
"""
from __future__ import annotations

import os
import struct
from pathlib import Path

import numpy as np

from .bitstream import BitWriter, canonical_codes, reverse_bits


_CODE_LENGTH_ORDER = (17, 18, 0, 1, 2, 3, 4, 5, 16, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)


def _bounded_huffman_lengths(frequencies: np.ndarray, max_bits: int = 15) -> list[int]:
    """Build a complete, bounded canonical tree for a VP8L alphabet."""
    import heapq

    values = [int(value) for value in np.asarray(frequencies).reshape(-1)]
    active = [(value, symbol, symbol) for symbol, value in enumerate(values) if value > 0]
    lengths = [0] * len(values)
    if not active:
        lengths[0] = 1
        return lengths
    if len(active) == 1:
        lengths[active[0][2]] = 1
        return lengths
    heapq.heapify(active)
    nodes = {}
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
            stack.append((left, depth + 1))
            stack.append((right, depth + 1))
    if max(lengths) <= max_bits:
        return lengths

    # VP8L accepts at most 15-bit prefix codes.  Merge pairs of overlong
    # leaves and split one shallower leaf so Kraft equality and the symbol
    # count remain unchanged; rebuilding from a capped histogram can still
    # produce an overfull tree for a highly skewed alphabet.
    counts = [0] * (max(max(lengths), max_bits) + 1)
    for length in lengths:
        if length:
            counts[length] += 1
    for bits in range(len(counts) - 1, max_bits, -1):
        while counts[bits] > 0:
            if counts[bits] < 2:
                raise ValueError("unable to bound VP8L Huffman tree")
            counts[bits] -= 2
            counts[bits - 1] += 1
            split = bits - 2
            while split > 0 and counts[split] == 0:
                split -= 1
            if split == 0:
                raise ValueError("unable to bound VP8L Huffman tree")
            counts[split] -= 1
            counts[split + 1] += 2
    ordered = sorted(
        (symbol for symbol, value in enumerate(values) if value > 0),
        key=lambda symbol: (values[symbol], symbol),
    )
    cursor = 0
    for bits in range(max_bits, 0, -1):
        for _ in range(counts[bits]):
            if cursor >= len(ordered):
                raise ValueError("invalid bounded VP8L Huffman histogram")
            lengths[ordered[cursor]] = bits
            cursor += 1
    if cursor != len(ordered):
        raise ValueError("incomplete bounded VP8L Huffman histogram")
    return lengths


def _canonical_lsb(lengths: list[int]) -> dict[int, tuple[int, int]]:
    return {
        # VP8L stores Huffman codes through an LSB-first bit writer.  The
        # decoder's lookup table is built from reversed canonical prefixes,
        # so the numeric value passed to BitWriter must be reversed within
        # the code length as well.
        symbol: (reverse_bits(code, size), size)
        for symbol, (code, size) in canonical_codes(
            {symbol: length for symbol, length in enumerate(lengths) if length > 0}
        ).items()
    }


def _write_prefix_code(writer: BitWriter, lengths: list[int]) -> dict[int, tuple[int, int]]:
    """Serialize one VP8L prefix tree and return its LSB-first codes."""
    active = [symbol for symbol, length in enumerate(lengths) if length > 0]
    if not active:
        lengths = [1] + [0] * (len(lengths) - 1)
        active = [0]
    if len(active) <= 2 and all(lengths[symbol] == 1 for symbol in active) and all(symbol < 256 for symbol in active):
        writer.write(1, 1)  # simple code-length code
        writer.write(len(active) - 1, 1)
        # VP8L uses a compact one-bit representation when the first symbol
        # is 0 or 1; otherwise it uses the eight-bit symbol form.  The second
        # symbol, when present, is always eight bits.
        if active[0] <= 1:
            writer.write(0, 1)
            writer.write(active[0], 1)
        else:
            writer.write(1, 1)
            writer.write(active[0], 8)
        if len(active) == 2:
            writer.write(active[1], 8)
        codes = _canonical_lsb(lengths)
        # A one-symbol VP8L tree is represented by a zero-bit code in the
        # image stream.  The serialized tree still carries a one-bit depth so
        # the decoder can construct its trivial table, but libwebp clears the
        # emitted symbol depth after storing that tree.
        if len(active) == 1:
            codes[active[0]] = (0, 0)
        return codes

    writer.write(0, 1)  # normal code-length code
    code_length_frequencies = np.bincount(np.asarray(lengths, dtype=np.int32), minlength=19)[:19]
    if int(np.count_nonzero(code_length_frequencies)) == 1:
        only = int(np.flatnonzero(code_length_frequencies)[0])
        companion = 0 if only != 0 else 1
        code_length_frequencies[companion] = 1
    code_length_lengths = _bounded_huffman_lengths(code_length_frequencies)
    active_code_lengths = [symbol for symbol, length in enumerate(code_length_lengths) if length > 0]
    positions = {symbol: index for index, symbol in enumerate(_CODE_LENGTH_ORDER)}
    if any(symbol not in positions for symbol in active_code_lengths):
        raise ValueError("invalid VP8L code-length symbol")
    # The serialized prefix is trimmed in the WebP storage order, not by the
    # numeric maximum of the symbols.
    num_code_lengths = max(4, max(positions[symbol] for symbol in active_code_lengths) + 1)
    writer.write(num_code_lengths - 4, 4)
    for symbol in _CODE_LENGTH_ORDER[:num_code_lengths]:
        writer.write(code_length_lengths[symbol], 3)
    code_length_codes = _canonical_lsb(code_length_lengths)
    writer.write(0, 1)  # use the complete alphabet for this channel
    for length in lengths:
        code, size = code_length_codes[int(length)]
        writer.write(code, size)
    codes = _canonical_lsb(lengths)
    if len(active) == 1:
        codes[active[0]] = (0, 0)
    return codes


def _normalize_webp_argb(image: np.ndarray) -> tuple[np.ndarray, int, int]:
    data = np.asarray(image)
    if data.dtype != np.uint8:
        raise ValueError("native WebP lossless input must be uint8")
    if data.ndim == 2:
        data = data[..., None]
    if data.ndim != 3 or data.shape[2] not in (1, 2, 3, 4):
        raise ValueError("WebP input must be HxW, HxWx2, HxWx3, or HxWx4")
    height, width, channels = map(int, data.shape)
    if not 1 <= width <= 16384 or not 1 <= height <= 16384:
        raise ValueError("WebP dimensions must be between 1 and 16384")
    if channels == 1:
        gray = data[..., 0]
        alpha = np.full_like(gray, 255)
        red = green = blue = gray
    elif channels == 2:
        gray, alpha = data[..., 0], data[..., 1]
        red = green = blue = gray
    elif channels == 3:
        red, green, blue = (data[..., index] for index in range(3))
        alpha = np.full((height, width), 255, dtype=np.uint8)
    else:
        red, green, blue, alpha = (data[..., index] for index in range(4))
    argb = np.stack((alpha, red, green, blue), axis=-1).astype(np.uint8, copy=False)
    if os.environ.get("WEBP_USE_AOT_PREP", "0") == "1":
        try:
            from taichi_vision.taichi_algorithm.aot_api.research import _dispatch

            result = _dispatch(
                "compression_image",
                "compression_webp_prepare_argb",
                # The AOT ndarray ABI records the extent of every dimension
                # used by a graph.  Keep the channel extent stable at four
                # while passing the logical source channel count as a scalar;
                # otherwise gray/RG/ RGB/RGBA calls cannot share one graph.
                inputs={
                    "src": np.ascontiguousarray(
                        np.pad(
                            np.asarray(data, dtype=np.float32),
                            ((0, 0), (0, 0), (0, 4 - channels)),
                            mode="constant",
                        )
                    )
                },
                outputs={"dst": np.empty((height, width, 4), dtype=np.float32)},
                scalars={"h": height, "w": width, "channels": channels},
                plain_ndarray=False,
            )
            prepared = result["dst"] if isinstance(result, dict) else result
            argb = np.clip(np.rint(np.asarray(prepared)), 0.0, 255.0).astype(np.uint8)
        except Exception as exc:
            if os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") != "1":
                raise RuntimeError(
                    "compression_webp_prepare_argb is unavailable for the selected AOT target; "
                    "compile the matching compression_image.tcm or set "
                    "AOT_ALLOW_HOST_FALLBACK=1 for an explicit reference run"
                ) from exc
    return np.ascontiguousarray(argb), width, height


def _vp8l_prefix_encode(value: int) -> tuple[int, int, int]:
    """Return the VP8L prefix symbol, extra-bit count, and extra value."""
    value = int(value)
    if value < 1:
        raise ValueError("VP8L prefix values must be positive")
    if value <= 4:
        return value - 1, 0, 0
    reduced = value - 1
    highest_bit = reduced.bit_length() - 1
    extra_bits = highest_bit - 1
    second_highest_bit = (reduced >> extra_bits) & 1
    code = 2 * highest_bit + second_highest_bit
    extra_value = reduced & ((1 << extra_bits) - 1)
    return code, extra_bits, extra_value


def _vp8l_pack_argb(argb: np.ndarray) -> np.ndarray:
    channels = argb.reshape(-1, 4).astype(np.uint32, copy=False)
    return (
        (channels[:, 0] << 24)
        | (channels[:, 1] << 16)
        | (channels[:, 2] << 8)
        | channels[:, 3]
    )


def _vp8l_subtract_green_argb(argb: np.ndarray) -> np.ndarray:
    """Apply the reversible VP8L subtract-green forward transform.

    VP8L stores residual ``R - G`` and ``B - G`` values modulo 256.  The
    decoder's type-2 transform adds the decoded green component back to both
    channels, so the operation is lossless for every uint8 ARGB pixel.  Keep
    the transform in a separate array: the source image is also used for the
    non-transformed candidate and must never be modified in place.
    """
    source = np.asarray(argb, dtype=np.uint8)
    if source.ndim != 3 or source.shape[-1] != 4:
        raise ValueError("VP8L subtract-green input must be an HxWx4 ARGB array")
    transformed = np.array(source, dtype=np.uint8, copy=True)
    green = source[..., 2].astype(np.int16, copy=False)
    transformed[..., 1] = ((source[..., 1].astype(np.int16) - green) & 0xFF).astype(np.uint8)
    transformed[..., 3] = ((source[..., 3].astype(np.int16) - green) & 0xFF).astype(np.uint8)
    return transformed


def _vp8l_half_towards_zero(values: np.ndarray) -> np.ndarray:
    """Divide signed values by two with the VP8L/C integer rule."""
    values = np.asarray(values, dtype=np.int16)
    return np.where(values < 0, -((-values) // 2), values // 2)


def _vp8l_average2(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """VP8L Average2: component-wise floor((a + b) / 2)."""
    return ((np.asarray(first, dtype=np.uint16) + np.asarray(second, dtype=np.uint16)) >> 1).astype(np.uint8)


def _vp8l_predictor_residual(argb: np.ndarray, mode: int) -> np.ndarray:
    """Apply one of the fourteen reversible VP8L predictor modes.

    The returned image is the encoded residual, not the prediction.  Border
    handling and the right-edge TR rule mirror the WebP lossless bitstream
    specification, including the special 0xff000000 top-left predictor.
    """
    source = np.asarray(argb, dtype=np.uint8)
    if source.ndim != 3 or source.shape[-1] != 4:
        raise ValueError("VP8L predictor input must be an HxWx4 ARGB array")
    mode = int(mode)
    if mode < 0 or mode > 13:
        raise ValueError("VP8L predictor mode must be in the range 0..13")
    height, width = map(int, source.shape[:2])
    prediction = np.empty_like(source)
    prediction[0, 0] = np.asarray((255, 0, 0, 0), dtype=np.uint8)
    if width > 1:
        prediction[0, 1:] = source[0, :-1]
    if height > 1:
        prediction[1:, 0] = source[:-1, 0]
    if height > 1 and width > 1:
        left = source[1:, :-1]
        top = source[:-1, 1:]
        top_left = source[:-1, :-1]
        top_right = np.empty_like(left)
        if width > 2:
            top_right[:, :-1] = source[:-1, 2:]
        # The rightmost-column TR pixel is the leftmost pixel of the current
        # row, as required by the VP8L border rule.
        top_right[:, -1] = source[1:, 0]

        if mode == 0:
            interior = np.zeros_like(left)
            interior[..., 0] = 255
        elif mode == 1:
            interior = left
        elif mode == 2:
            interior = top
        elif mode == 3:
            interior = top_right
        elif mode == 4:
            interior = top_left
        elif mode == 5:
            interior = _vp8l_average2(_vp8l_average2(left, top_right), top)
        elif mode == 6:
            interior = _vp8l_average2(left, top_left)
        elif mode == 7:
            interior = _vp8l_average2(left, top)
        elif mode == 8:
            interior = _vp8l_average2(top_left, top)
        elif mode == 9:
            interior = _vp8l_average2(top, top_right)
        elif mode == 10:
            interior = _vp8l_average2(
                _vp8l_average2(left, top_left),
                _vp8l_average2(top, top_right),
            )
        elif mode == 11:
            # Select(L, T, TL): ties select T.  The estimate cancels in the
            # distance comparison, leaving the equivalent expression below.
            distance_to_left = np.abs(top.astype(np.int16) - top_left.astype(np.int16)).sum(axis=-1)
            distance_to_top = np.abs(left.astype(np.int16) - top_left.astype(np.int16)).sum(axis=-1)
            interior = np.where((distance_to_left < distance_to_top)[..., None], left, top)
        elif mode == 12:
            interior = np.clip(
                left.astype(np.int16) + top.astype(np.int16) - top_left.astype(np.int16),
                0,
                255,
            ).astype(np.uint8)
        else:
            average = _vp8l_average2(left, top).astype(np.int16)
            delta = average - top_left.astype(np.int16)
            interior = np.clip(average + _vp8l_half_towards_zero(delta), 0, 255).astype(np.uint8)
        prediction[1:, 1:] = interior
    residual = (source.astype(np.int16) - prediction.astype(np.int16)) & 0xFF
    return residual.astype(np.uint8)


def _vp8l_block_scores(residual: np.ndarray, block_size: int) -> np.ndarray:
    """Estimate residual entropy cost with a bounded, vectorized score."""
    height, width = map(int, residual.shape[:2])
    blocks_y = (height + block_size - 1) // block_size
    blocks_x = (width + block_size - 1) // block_size
    signed = residual.astype(np.int16)
    signed = np.where(signed > 127, signed - 256, signed)
    score = np.abs(signed).sum(axis=-1, dtype=np.int64)
    padded = np.pad(
        score,
        ((0, blocks_y * block_size - height), (0, blocks_x * block_size - width)),
        mode="constant",
    )
    return padded.reshape(blocks_y, block_size, blocks_x, block_size).sum(axis=(1, 3), dtype=np.int64)


def _vp8l_predictor_forward(argb: np.ndarray, effort: str) -> tuple[np.ndarray, np.ndarray, int]:
    """Build a reversible predictor residual and its auxiliary mode image.

    ``size_bits`` is deliberately bounded by effort.  Smaller blocks allow
    more local modes but cost more auxiliary image data; the final candidate
    comparison still rejects the transform when that overhead is not useful.
    """
    source = np.ascontiguousarray(argb, dtype=np.uint8)
    effort = str(effort).lower()
    if effort == "best":
        size_bits, modes = 4, tuple(range(14))
    elif effort == "fast":
        size_bits, modes = 5, (1, 2, 5, 7, 8, 9, 10, 11, 12, 13)
    else:
        size_bits, modes = 6, (1, 2, 5, 7, 11, 12, 13)
    block_size = 1 << size_bits
    height, width = map(int, source.shape[:2])
    blocks_y = (height + block_size - 1) // block_size
    blocks_x = (width + block_size - 1) // block_size
    best_score = np.full((blocks_y, blocks_x), np.iinfo(np.int64).max, dtype=np.int64)
    best_mode = np.zeros((blocks_y, blocks_x), dtype=np.uint8)
    best_residual = np.zeros_like(source)
    for mode in modes:
        residual = _vp8l_predictor_residual(source, mode)
        score = _vp8l_block_scores(residual, block_size)
        select = score < best_score
        if not np.any(select):
            continue
        block_selection = np.repeat(np.repeat(select, block_size, axis=0), block_size, axis=1)
        block_selection = block_selection[:height, :width]
        best_residual = np.where(block_selection[..., None], residual, best_residual)
        best_score = np.where(select, score, best_score)
        best_mode = np.where(select, np.uint8(mode), best_mode)

    # Predictor metadata is itself an entropy-coded image.  Only the green
    # component carries the mode; the other components are fixed values.
    mode_image = np.zeros((blocks_y, blocks_x, 4), dtype=np.uint8)
    mode_image[..., 0] = 255
    mode_image[..., 2] = best_mode
    return np.ascontiguousarray(best_residual), mode_image, size_bits


def _vp8l_write_auxiliary_literal_image(writer: BitWriter, argb: np.ndarray) -> None:
    """Write a no-transform, no-cache literal image used by VP8L metadata."""
    pixels = np.asarray(argb, dtype=np.uint8).reshape(-1, 4)
    if pixels.size == 0:
        raise ValueError("VP8L auxiliary image must not be empty")
    # Auxiliary images have the entropy-coded-image form: color-cache info,
    # then five prefix trees and literal pixels.  They do not contain an
    # image header or a meta-prefix bit.
    writer.write(0, 1)
    histograms = [
        np.bincount(pixels[:, 2], minlength=256),
        np.bincount(pixels[:, 1], minlength=256),
        np.bincount(pixels[:, 3], minlength=256),
        np.bincount(pixels[:, 0], minlength=256),
        np.asarray([1] + [0] * 39, dtype=np.int64),
    ]
    lengths = [
        _bounded_huffman_lengths(np.pad(histograms[0], (0, 24))),
        _bounded_huffman_lengths(histograms[1]),
        _bounded_huffman_lengths(histograms[2]),
        _bounded_huffman_lengths(histograms[3]),
        _bounded_huffman_lengths(histograms[4]),
    ]
    codes = [_write_prefix_code(writer, tree) for tree in lengths]
    for alpha, red, green, blue in pixels:
        for value, table in ((green, codes[0]), (red, codes[1]), (blue, codes[2]), (alpha, codes[3])):
            code, size = table[int(value)]
            writer.write(code, size)


def _vp8l_write_image_header(
    writer: BitWriter,
    width: int,
    height: int,
    pixels: np.ndarray,
    *,
    subtract_green: bool,
    predictor_modes: np.ndarray | None = None,
    predictor_bits: int | None = None,
    alpha_is_used: bool | None = None,
) -> None:
    """Write the VP8L header and the optional transform chain."""
    writer.write(width - 1, 14)
    writer.write(height - 1, 14)
    if alpha_is_used is None:
        # Kept as a safe default for internal callers that already hold the
        # final encoded pixels.  Public payload builders pass the source-image
        # alpha explicitly because predictor residuals are not alpha pixels.
        alpha_is_used = bool(np.any(pixels[:, 0] != 255))
    writer.write(1 if alpha_is_used else 0, 1)
    writer.write(0, 3)  # VP8L version
    if predictor_modes is not None:
        if predictor_bits is None or not 2 <= int(predictor_bits) <= 9:
            raise ValueError("VP8L predictor transform size_bits must be in the range 2..9")
        writer.write(1, 1)  # transform present
        writer.write(0, 2)  # PREDICTOR_TRANSFORM
        writer.write(int(predictor_bits) - 2, 3)
        _vp8l_write_auxiliary_literal_image(writer, predictor_modes)
    if subtract_green:
        writer.write(1, 1)  # transform present
        writer.write(2, 2)  # SUBTRACT_GREEN_TRANSFORM
        writer.write(0, 1)  # end of transform chain
    else:
        writer.write(0, 1)  # no transforms
    writer.write(0, 1)  # no color cache
    writer.write(0, 1)  # one meta prefix-code group


def _webp_literal_histograms(argb: np.ndarray) -> list[np.ndarray]:
    """Return VP8L literal histograms, optionally using the matching TCM graph."""
    if os.environ.get("WEBP_USE_AOT_HIST", "0") == "1":
        try:
            from taichi_vision.taichi_algorithm.aot_api.research import _dispatch

            height, width = argb.shape[:2]
            source = np.ascontiguousarray(argb, dtype=np.float32)
            result = _dispatch(
                "compression_image",
                "compression_webp_histogram_argb",
                inputs={"src": source},
                outputs={"hist": np.zeros((4, 256), dtype=np.int32)},
                scalars={"h": int(height), "w": int(width)},
                plain_ndarray=False,
            )
            hist = np.asarray(result["hist"] if isinstance(result, dict) else result, dtype=np.int64)
            if hist.shape != (4, 256) or not np.array_equal(hist.sum(axis=1), np.full(4, height * width, dtype=np.int64)):
                raise RuntimeError("invalid VP8L histogram output from AOT graph")
            return [hist[index] for index in range(4)]
        except Exception as exc:
            if os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") != "1":
                raise RuntimeError(
                    "compression_webp_histogram_argb is unavailable for the selected AOT target; "
                    "compile the matching compression_image.tcm or set "
                    "AOT_ALLOW_HOST_FALLBACK=1 for an explicit reference run"
                ) from exc
    pixels = argb.reshape(-1, 4)
    return [
        np.bincount(pixels[:, 2], minlength=256),
        np.bincount(pixels[:, 1], minlength=256),
        np.bincount(pixels[:, 3], minlength=256),
        np.bincount(pixels[:, 0], minlength=256),
    ]


def _vp8l_lz_tokens(argb: np.ndarray, effort: str) -> list[tuple[int, int, int]]:
    """Greedy exact-pixel LZ77 tokenization for the no-transform profile."""
    packed = _vp8l_pack_argb(argb)
    pixel_count = int(packed.size)
    if pixel_count == 0:
        return []
    if effort == "fast":
        window, max_candidates = 4096, 4
    else:
        window, max_candidates = 32768, 16
    max_match = 4096
    history: dict[int, list[int]] = {}
    tokens: list[tuple[int, int, int]] = []

    def add_position(position: int) -> None:
        key = int(packed[position])
        entries = history.setdefault(key, [])
        entries.append(position)
        if len(entries) > max_candidates:
            del entries[:-max_candidates]
        expired = position - window
        if expired >= 0:
            old_key = int(packed[expired])
            old_entries = history.get(old_key)
            if old_entries:
                if old_entries[0] == expired:
                    del old_entries[0]
                else:
                    try:
                        old_entries.remove(expired)
                    except ValueError:
                        pass
                if not old_entries:
                    history.pop(old_key, None)

    position = 0
    while position < pixel_count:
        best_length = 0
        best_distance = 0
        candidates = history.get(int(packed[position]), ())
        for candidate in reversed(candidates):
            distance = position - candidate
            if distance < 1 or distance > window:
                continue
            length = 0
            while (
                length < max_match
                and position + length < pixel_count
                and int(packed[candidate + length]) == int(packed[position + length])
            ):
                length += 1
            if length > best_length:
                best_length = length
                best_distance = distance
                if length == max_match:
                    break
        # Two-pixel matches are legal but generally lose to their four
        # literal channel symbols once the two prefix trees are included.
        if best_length >= 3:
            tokens.append((1, best_length, best_distance))
            for offset in range(best_length):
                add_position(position + offset)
            position += best_length
        else:
            tokens.append((0, position, 0))
            add_position(position)
            position += 1
    return tokens


def _vp8l_apply_transforms(
    argb: np.ndarray,
    *,
    subtract_green: bool,
    predictor_plan: tuple[np.ndarray, np.ndarray, int] | None,
) -> tuple[np.ndarray, np.ndarray | None, int | None]:
    """Apply the forward transform chain and return its serialized metadata."""
    if predictor_plan is None:
        transformed = np.ascontiguousarray(argb, dtype=np.uint8)
        predictor_modes = None
        predictor_bits = None
    else:
        transformed, predictor_modes, predictor_bits = predictor_plan
        transformed = np.ascontiguousarray(transformed, dtype=np.uint8)
        predictor_modes = np.ascontiguousarray(predictor_modes, dtype=np.uint8)
        if transformed.shape != argb.shape or transformed.ndim != 3 or transformed.shape[-1] != 4:
            raise ValueError("invalid VP8L predictor residual shape")
        if predictor_modes.ndim != 3 or predictor_modes.shape[-1] != 4 or predictor_modes.size == 0:
            raise ValueError("invalid VP8L predictor metadata image")
    if subtract_green:
        transformed = _vp8l_subtract_green_argb(transformed)
    return transformed, predictor_modes, predictor_bits


def _vp8l_lz_payload_from_argb(
    argb: np.ndarray,
    width: int,
    height: int,
    effort: str,
    *,
    subtract_green: bool = False,
    predictor_plan: tuple[np.ndarray, np.ndarray, int] | None = None,
) -> bytes:
    alpha_is_used = bool(np.any(np.asarray(argb, dtype=np.uint8)[..., 0] != 255))
    argb, predictor_modes, predictor_bits = _vp8l_apply_transforms(
        argb,
        subtract_green=subtract_green,
        predictor_plan=predictor_plan,
    )
    pixels = argb.reshape(-1, 4)
    tokens = _vp8l_lz_tokens(argb, effort)
    green_histogram = np.zeros(280, dtype=np.int64)
    red_histogram = np.zeros(256, dtype=np.int64)
    blue_histogram = np.zeros(256, dtype=np.int64)
    alpha_histogram = np.zeros(256, dtype=np.int64)
    distance_histogram = np.zeros(40, dtype=np.int64)
    for kind, value, distance in tokens:
        if kind == 0:
            alpha, red, green, blue = pixels[value]
            green_histogram[int(green)] += 1
            red_histogram[int(red)] += 1
            blue_histogram[int(blue)] += 1
            alpha_histogram[int(alpha)] += 1
        else:
            length_code, _, _ = _vp8l_prefix_encode(value)
            distance_code, _, _ = _vp8l_prefix_encode(120 + distance)
            green_histogram[256 + length_code] += 1
            distance_histogram[distance_code] += 1
    lengths = [
        _bounded_huffman_lengths(green_histogram),
        _bounded_huffman_lengths(red_histogram),
        _bounded_huffman_lengths(blue_histogram),
        _bounded_huffman_lengths(alpha_histogram),
        _bounded_huffman_lengths(distance_histogram),
    ]
    writer = BitWriter(lsb_first=True)
    _vp8l_write_image_header(
        writer,
        width,
        height,
        pixels,
        subtract_green=subtract_green,
        predictor_modes=predictor_modes,
        predictor_bits=predictor_bits,
        alpha_is_used=alpha_is_used,
    )
    codes = [_write_prefix_code(writer, tree) for tree in lengths]
    for kind, value, distance in tokens:
        if kind == 0:
            alpha, red, green, blue = pixels[value]
            for channel_value, table in ((green, codes[0]), (red, codes[1]), (blue, codes[2]), (alpha, codes[3])):
                code, size = table[int(channel_value)]
                writer.write(code, size)
        else:
            length_code, length_bits, length_extra = _vp8l_prefix_encode(value)
            code, size = codes[0][256 + length_code]
            writer.write(code, size)
            writer.write(length_extra, length_bits)
            distance_code, distance_bits, distance_extra = _vp8l_prefix_encode(120 + distance)
            code, size = codes[4][distance_code]
            writer.write(code, size)
            writer.write(distance_extra, distance_bits)
    return b"\x2f" + writer.finish(fill=0)


def _vp8l_lz_payload(
    image: np.ndarray,
    effort: str,
    *,
    subtract_green: bool = False,
    predictor_plan: tuple[np.ndarray, np.ndarray, int] | None = None,
) -> bytes:
    argb, width, height = _normalize_webp_argb(image)
    return _vp8l_lz_payload_from_argb(
        argb,
        width,
        height,
        effort,
        subtract_green=subtract_green,
        predictor_plan=predictor_plan,
    )


def _vp8l_literal_payload_from_argb(
    argb: np.ndarray,
    width: int,
    height: int,
    *,
    subtract_green: bool = False,
    predictor_plan: tuple[np.ndarray, np.ndarray, int] | None = None,
) -> bytes:
    """Encode an arbitrary ARGB image as a valid VP8L literal stream.

    The literal profile disables color cache and LZ77.  It may carry the
    spec-defined predictor and subtract-green transforms; the transform chain
    is selected by the caller and compared against the untransformed stream
    before packaging.
    """
    alpha_is_used = bool(np.any(np.asarray(argb, dtype=np.uint8)[..., 0] != 255))
    argb, predictor_modes, predictor_bits = _vp8l_apply_transforms(
        argb,
        subtract_green=subtract_green,
        predictor_plan=predictor_plan,
    )
    pixels = argb.reshape(-1, 4)
    histograms = _webp_literal_histograms(argb) + [
        np.asarray([1] + [0] * 39, dtype=np.int64),  # distance, unused
    ]
    # Prefix #1 includes 24 LZ77 length symbols even though this baseline
    # emits only literals.  Its full alphabet is therefore 280 symbols.
    lengths = [
        _bounded_huffman_lengths(np.pad(histograms[0], (0, 24))),
        _bounded_huffman_lengths(histograms[1]),
        _bounded_huffman_lengths(histograms[2]),
        _bounded_huffman_lengths(histograms[3]),
        _bounded_huffman_lengths(histograms[4]),
    ]
    writer = BitWriter(lsb_first=True)
    _vp8l_write_image_header(
        writer,
        width,
        height,
        pixels,
        subtract_green=subtract_green,
        predictor_modes=predictor_modes,
        predictor_bits=predictor_bits,
        alpha_is_used=alpha_is_used,
    )
    codes = [_write_prefix_code(writer, tree) for tree in lengths]
    for alpha, red, green, blue in pixels:
        for value, table in ((green, codes[0]), (red, codes[1]), (blue, codes[2]), (alpha, codes[3])):
            code, size = table[int(value)]
            writer.write(code, size)
    return b"\x2f" + writer.finish(fill=0)


def _vp8l_literal_payload(
    image: np.ndarray,
    *,
    subtract_green: bool = False,
    predictor_plan: tuple[np.ndarray, np.ndarray, int] | None = None,
) -> bytes:
    argb, width, height = _normalize_webp_argb(image)
    return _vp8l_literal_payload_from_argb(
        argb,
        width,
        height,
        subtract_green=subtract_green,
        predictor_plan=predictor_plan,
    )


def encode_webp_lossless_aot(image, *, effort: str = "baseline", metadata: dict | None = None) -> bytes:
    """Encode a uint8 gray/RGB/RGBA image to a native VP8L WebP stream.

    Every effort evaluates literal, predictor, and subtract-green candidates;
    ``fast`` and ``best`` additionally add greedy exact-pixel LZ77 references
    with different bounded search budgets.  The smallest standard VP8L stream
    is retained, so the predictor transform cannot make a result larger than
    the previous candidates.
    """
    if str(effort).lower() not in {"baseline", "fast", "best"}:
        raise ValueError("WebP lossless effort must be baseline, fast, or best")
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("WebP metadata must be a mapping")
    normalized_effort = str(effort).lower()
    source, source_width, source_height = _normalize_webp_argb(image)
    predictor_plan = _vp8l_predictor_forward(source, normalized_effort)
    candidates = [
        _vp8l_literal_payload_from_argb(source, source_width, source_height),
        _vp8l_literal_payload_from_argb(source, source_width, source_height, subtract_green=True),
        _vp8l_literal_payload_from_argb(
            source,
            source_width,
            source_height,
            predictor_plan=predictor_plan,
        ),
        _vp8l_literal_payload_from_argb(
            source,
            source_width,
            source_height,
            subtract_green=True,
            predictor_plan=predictor_plan,
        ),
    ]
    if normalized_effort != "baseline":
        candidates.extend((
            _vp8l_lz_payload_from_argb(source, source_width, source_height, normalized_effort),
            _vp8l_lz_payload_from_argb(
                source,
                source_width,
                source_height,
                normalized_effort,
                subtract_green=True,
            ),
            _vp8l_lz_payload_from_argb(
                source,
                source_width,
                source_height,
                normalized_effort,
                predictor_plan=predictor_plan,
            ),
            _vp8l_lz_payload_from_argb(
                source,
                source_width,
                source_height,
                normalized_effort,
                subtract_green=True,
                predictor_plan=predictor_plan,
            ),
        ))
    # A short image or a high-entropy image can lose bytes to the extra
    # transform/distance trees.  Keep the strictly smallest valid profile.
    payload = min(candidates, key=len)
    data = np.asarray(image)
    height, width = (data.shape[0], data.shape[1]) if data.ndim >= 2 else (0, 0)
    channels = int(data.shape[2]) if data.ndim == 3 else 1
    return build_webp_payload(payload, width, height, lossless=True, metadata=metadata, alpha=channels in (2, 4))

def _chunk(kind: bytes, payload: bytes) -> bytes:
    if len(kind) != 4:
        raise ValueError("WebP chunk type must be four bytes")
    padding = b"\x00" if len(payload) & 1 else b""
    return kind + struct.pack("<I", len(payload)) + payload + padding


def _vp8x_payload(width: int, height: int, *, alpha: bool, metadata: dict[str, bytes]) -> bytes:
    """Build the 10-byte extended WebP canvas/feature header."""
    flags = 0
    if "icc" in metadata:
        flags |= 0x20
    if alpha:
        flags |= 0x10
    if "exif" in metadata:
        flags |= 0x08
    if "xmp" in metadata:
        flags |= 0x04
    return bytes((flags, 0, 0, 0)) + (width - 1).to_bytes(3, "little") + (height - 1).to_bytes(3, "little")


def _riff(chunks: tuple[bytes, ...]) -> bytes:
    body = b"WEBP" + b"".join(chunks)
    return b"RIFF" + struct.pack("<I", len(body)) + body


def build_webp_payload(payload: bytes, width: int, height: int, *, lossless: bool = True, metadata: dict | None = None, alpha: bool = False) -> bytes:
    """Package one already-encoded VP8 or VP8L payload.

    ``payload`` must include the codec-specific frame header.  No external
    encoder or decoder is called here.
    """
    width, height = int(width), int(height)
    if not 1 <= width <= 16384 or not 1 <= height <= 16384:
        raise ValueError("WebP dimensions must be between 1 and 16384")
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("WebP metadata must be a mapping")
    payload = bytes(payload)
    fourcc = b"VP8L" if lossless else b"VP8 "
    if lossless:
        if len(payload) < 6 or payload[0] != 0x2F:
            raise ValueError("WebP lossless payload is missing the VP8L signature or entropy data")
        encoded_width = 1 + (payload[1] | ((payload[2] & 0x3F) << 8))
        encoded_height = 1 + (((payload[2] >> 6) | (payload[3] << 2) | ((payload[4] & 0x0F) << 10)))
        if (encoded_width, encoded_height) != (width, height):
            raise ValueError("VP8L payload dimensions do not match container dimensions")
        if ((payload[4] >> 5) & 0x07) != 0:
            raise ValueError("unsupported VP8L version")
    elif len(payload) < 10:
        raise ValueError("WebP lossy payload is missing the VP8 frame header")
    normalized_metadata: dict[str, bytes] = {}
    for key, value in (metadata or {}).items():
        normalized_key = str(key).lower()
        if normalized_key not in {"icc", "exif", "xmp"}:
            raise ValueError(f"unsupported WebP metadata key: {key}")
        normalized_metadata[normalized_key] = bytes(value)
    chunks = []
    if normalized_metadata:
        chunks.append(_chunk(b"VP8X", _vp8x_payload(width, height, alpha=bool(alpha), metadata=normalized_metadata)))
        if "icc" in normalized_metadata:
            chunks.append(_chunk(b"ICCP", normalized_metadata["icc"]))
    chunks.append(_chunk(fourcc, payload))
    if "exif" in normalized_metadata:
        chunks.append(_chunk(b"EXIF", normalized_metadata["exif"]))
    if "xmp" in normalized_metadata:
        chunks.append(_chunk(b"XMP ", normalized_metadata["xmp"]))
    return _riff(tuple(chunks))


def package_webp_aot(payload: bytes, width: int, height: int, *, lossless: bool = True, metadata: dict | None = None, alpha: bool = False) -> bytes:
    return build_webp_payload(payload, width, height, lossless=lossless, metadata=metadata, alpha=alpha)


def save_webp_aot(payload: bytes, path: str | os.PathLike[str], width: int, height: int, *, lossless: bool = True, metadata: dict | None = None, alpha: bool = False) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(package_webp_aot(payload, width, height, lossless=lossless, metadata=metadata, alpha=alpha))
    temporary.replace(target)


def save_webp_lossless_aot(image, path: str | os.PathLike[str], *, effort: str = "baseline", metadata: dict | None = None) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(encode_webp_lossless_aot(image, effort=effort, metadata=metadata))
    temporary.replace(target)


def parse_webp_aot(data: bytes | bytearray | str | os.PathLike[str], *, max_chunks: int = 4096):
    raw = Path(data).read_bytes() if isinstance(data, (str, os.PathLike)) else bytes(data)
    if max_chunks <= 0:
        raise ValueError("WebP chunk limit must be positive")
    if len(raw) < 12 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
        raise ValueError("not a WebP RIFF stream")
    declared = struct.unpack("<I", raw[4:8])[0]
    if declared != len(raw) - 8:
        raise ValueError("WebP RIFF length mismatch")
    chunks = []
    offset = 12
    while offset < len(raw):
        if len(chunks) >= max_chunks:
            raise ValueError("WebP chunk limit exceeded")
        if len(raw) - offset < 8:
            raise ValueError("truncated WebP chunk header")
        kind = raw[offset:offset + 4]
        size = struct.unpack("<I", raw[offset + 4:offset + 8])[0]
        end = offset + 8 + size
        if end > len(raw):
            raise ValueError("WebP chunk exceeds file bounds")
        chunks.append((kind, offset, size, raw[offset + 8:end]))
        if size & 1:
            if end >= len(raw) or raw[end] != 0:
                raise ValueError("WebP chunk padding is missing")
            offset = end + 1
        else:
            offset = end
    image_chunks = [item for item in chunks if item[0] in (b"VP8 ", b"VP8L")]
    if len(image_chunks) != 1:
        raise ValueError("WebP stream has no image chunk")
    vp8x_chunks = [item for item in chunks if item[0] == b"VP8X"]
    metadata_chunks = {item[0] for item in chunks if item[0] in (b"ICCP", b"EXIF", b"XMP ")}
    for metadata_kind in (b"ICCP", b"EXIF", b"XMP "):
        if sum(1 for item in chunks if item[0] == metadata_kind) > 1:
            raise ValueError("WebP metadata chunks must not be duplicated")
    if metadata_chunks and len(vp8x_chunks) != 1:
        raise ValueError("WebP metadata requires exactly one VP8X chunk")
    if len(vp8x_chunks) > 1:
        raise ValueError("WebP stream contains multiple VP8X chunks")
    if vp8x_chunks and chunks[0][0] != b"VP8X":
        raise ValueError("VP8X must precede WebP metadata and image chunks")
    vp8x_dimensions = None
    if vp8x_chunks:
        vp8x_payload = vp8x_chunks[0][3]
        if len(vp8x_payload) != 10:
            raise ValueError("invalid VP8X payload length")
        flags = vp8x_payload[0]
        if flags & 0xC1:
            raise ValueError("VP8X reserved flags are not zero")
        if flags & 0x02:
            raise ValueError("animated WebP is not supported by this parser")
        vp8x_dimensions = (
            1 + int.from_bytes(vp8x_payload[4:7], "little"),
            1 + int.from_bytes(vp8x_payload[7:10], "little"),
        )
        if vp8x_dimensions[0] > 16384 or vp8x_dimensions[1] > 16384:
            raise ValueError("VP8X dimensions exceed the native profile")
        expected_flags = {
            b"ICCP": 0x20,
            b"EXIF": 0x08,
            b"XMP ": 0x04,
        }
        for kind, flag in expected_flags.items():
            if bool(flags & flag) != (kind in metadata_chunks):
                raise ValueError("VP8X metadata flags do not match WebP chunks")
    lossless = [item for item in chunks if item[0] == b"VP8L"]
    if lossless:
        payload = lossless[0][3]
        if len(payload) < 6 or payload[0] != 0x2F:
            raise ValueError("invalid VP8L payload or missing entropy data")
        width = 1 + (payload[1] | ((payload[2] & 0x3F) << 8))
        height = 1 + (((payload[2] >> 6) | (payload[3] << 2) | ((payload[4] & 0x0F) << 10)))
        if not 1 <= width <= 16384 or not 1 <= height <= 16384:
            raise ValueError("invalid VP8L dimensions")
        if ((payload[4] >> 5) & 0x07) != 0:
            raise ValueError("unsupported VP8L version")
        if vp8x_dimensions is not None and vp8x_dimensions != (width, height):
            raise ValueError("VP8X and VP8L dimensions do not match")
        if vp8x_chunks and (payload[4] & 0x10) and not (vp8x_chunks[0][3][0] & 0x10):
            raise ValueError("VP8X alpha flag is missing for an alpha VP8L stream")
    return tuple(chunks)


__all__ = [
    "build_webp_payload", "package_webp_aot", "save_webp_aot",
    "encode_webp_lossless_aot", "save_webp_lossless_aot", "parse_webp_aot",
]
