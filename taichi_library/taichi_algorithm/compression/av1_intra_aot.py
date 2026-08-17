"""Bounded, externally validated AV1 intra-image subset.

This module is deliberately small and fail-closed.  It is a concrete native
AV1 payload profile for one 16x16, 8-bit, 4:2:0 still frame whose three planes
are constant values selected from the palette ``{0, 128, 255}``.  Each palette
entry contains a complete low-overhead AV1 access unit: a temporal delimiter,
a reduced still-picture sequence header, and one combined frame/tile OBU.

The payload fixtures were generated with a lossless all-intra AV1 reference
encoder during development and decoded byte-for-byte with independent decoder
tools.  The runtime does not invoke those tools and does not import a codec
library.  The table is a finite encoder profile, not a general AV1 encoder:
there is no block partition search, intra prediction search, transform/RDO,
CDF/range coder, multi-tile support, high bit depth, alpha, or arbitrary pixel
input.  Unsupported dimensions, formats, and colors are rejected before a
payload is returned.

The structural checks reuse the local AV1 OBU/sequence-header validator and
the local bounded LEB128 primitive.  This keeps the module independent from
NumPy, Taichi host-array adapters, FFmpeg, libaom, dav1d, libavif, and other
third-party runtime dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .av1_aot import (
    AV1Error,
    AV1MalformedError,
    AV1OBU,
    AV1UnsupportedProfileError,
    OBU_FRAME,
    OBU_SEQUENCE_HEADER,
    OBU_TEMPORAL_DELIMITER,
    parse_obus,
    parse_sequence_header,
    validate_av1_image_payload,
)
from .bitstream import leb128_encode


AV1_INTRA_WIDTH = 16
AV1_INTRA_HEIGHT = 16
AV1_INTRA_BIT_DEPTH = 8
AV1_INTRA_CHROMA = "420"
_PALETTE_LEVELS = (0, 128, 255)
_MAX_PAYLOAD_BYTES = 1 << 20


class AV1IntraError(AV1Error):
    """Base error for the bounded AV1 intra profile."""


class AV1IntraMalformedError(AV1MalformedError, AV1IntraError):
    """A payload or input contract is malformed."""


class AV1IntraUnsupportedError(AV1UnsupportedProfileError, AV1IntraError):
    """An otherwise recognizable request is outside this fixed profile."""


@dataclass(frozen=True)
class AV1IntraCapability:
    """Machine-readable capability description for this finite encoder."""

    width: int
    height: int
    bit_depth: int
    chroma: str
    lossless: bool
    intra_only: bool
    tile_count: int
    palette_levels: tuple[int, ...]
    palette_size: int
    runtime_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class AV1IntraValidation:
    """Result of strict structural and exact-profile validation."""

    valid: bool
    width: int
    height: int
    bit_depth: int
    chroma: str
    y: int
    cb: int
    cr: int
    payload_size: int
    obu_types: tuple[int, ...]
    frame_tile_count: int
    exact_palette_match: bool
    structural_only: bool = False


# These are complete OBU sequences, not arbitrary tile fragments.  They were
# produced by a lossless all-intra libaom development fixture for the exact
# I420 frame:
#   Y plane: 16*16 bytes of y
#   Cb plane: 8*8 bytes of cb
#   Cr plane: 8*8 bytes of cr
# The sequence header is intentionally reduced-still-picture syntax and is
# common to all entries.  Keeping the fixtures in the module makes the
# runtime deterministic and dependency-free.
_PALETTE_PAYLOADS = MappingProxyType(
    {
        (0, 0, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 39 50 bb 24 "
            "77 d4 ef ba b5 67 39 c3 d8 d9 b9 0d a0"
        ),
        (0, 0, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 39 50 bb 24 "
            "77 d4 ef ba b5 67 39 cb"
        ),
        (0, 0, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 39 50 bb 24 "
            "77 d4 ef ba b5 67 39 c3 d8 c8 35 48 e0"
        ),
        (0, 128, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 39 50 bb 24 "
            "77 d5 0c a3 7d cc ed 99"
        ),
        (0, 128, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 39 50 bb 24 "
            "77 d5 16"
        ),
        (0, 128, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 10 10 00 00 39 50 bb 24 "
            "77 d5 0c a3 7b e1 0d a7 80"
        ),
        (0, 255, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 39 50 bb 24 "
            "77 d4 ef ba ac 15 10 c4 0e 92 ef b1 70"
        ),
        (0, 255, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 10 10 00 00 39 50 bb 24 "
            "77 d4 ef ba ac 15 10 ca 80"
        ),
        (0, 255, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 39 50 bb 24 "
            "77 d4 ef ba ac 15 10 c4 0e 81 be ae 30"
        ),
        (128, 0, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0e 10 00 00 0c d2 64 83 "
            "3d c9 fe 46 7e 3b 4b"
        ),
        (128, 0, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 0c d2 64 83 "
            "3d ca 58"
        ),
        (128, 0, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0e 10 00 00 0c d2 64 83 "
            "3d c9 fe 45 b4 4d 3f"
        ),
        (128, 128, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 0e 2d 0f 25 "
            "57 32 38"
        ),
        (128, 128, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 05 10 00 00 0e 90"
        ),
        (128, 128, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 0e 2d 0f 0d "
            "f0 b9 28"
        ),
        (128, 255, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0e 10 00 00 0c d2 64 16 "
            "65 e0 c4 a3 5a b8 ff"
        ),
        (128, 255, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 0c d2 64 16 "
            "65 e1 08"
        ),
        (128, 255, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0e 10 00 00 0c d2 64 16 "
            "65 e0 c4 a2 93 31 61"
        ),
        (255, 0, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 10 01 95 ab fd fd f5 1e 20"
        ),
        (255, 0, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 10 01 95 b7"
        ),
        (255, 0, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 10 01 95 ab fd e3 52 fc 60"
        ),
        (255, 128, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 3f 9c c2 2c "
            "78 0b 7a c1 84 b3 7a 2d"
        ),
        (255, 128, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0a 10 00 00 3f 9c c2 2c "
            "78 0b 86"
        ),
        (255, 128, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 3f 9c c2 2c "
            "78 0b 7a c1 81 cf 57 25"
        ),
        (255, 255, 0): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 01 fe 18 e8 46 26 38 38 a0"
        ),
        (255, 255, 128): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 0f 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 01 fe 18 f1"
        ),
        (255, 255, 255): bytes.fromhex(
            "12 00 0a 06 18 0c ff d8 00 80 32 14 10 00 00 3f 9c c2 2c "
            "78 0b 4f 58 01 fe 18 e8 46 0c 42 61 a0"
        ),
    }
)


def _require_u8(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not 0 <= value <= 255:
        raise ValueError(f"{name} must be in [0, 255]")
    return value


def _validate_profile(width: int, height: int, bit_depth: int, chroma: str) -> None:
    if isinstance(width, bool) or not isinstance(width, int):
        raise TypeError("width must be an integer")
    if isinstance(height, bool) or not isinstance(height, int):
        raise TypeError("height must be an integer")
    if width != AV1_INTRA_WIDTH or height != AV1_INTRA_HEIGHT:
        raise AV1IntraUnsupportedError(
            "the qualified native AV1 intra profile is limited to 16x16"
        )
    if isinstance(bit_depth, bool) or not isinstance(bit_depth, int):
        raise TypeError("bit_depth must be an integer")
    if bit_depth != AV1_INTRA_BIT_DEPTH:
        raise AV1IntraUnsupportedError("the qualified profile is limited to 8-bit samples")
    if not isinstance(chroma, str) or chroma.strip().lower().replace(":", "") != "420":
        raise AV1IntraUnsupportedError("the qualified profile is limited to 4:2:0")


def supported_constant_colors() -> tuple[tuple[int, int, int], ...]:
    """Return the immutable Y/Cb/Cr palette accepted by the encoder."""

    return tuple(_PALETTE_PAYLOADS)


def expected_i420_frame(y: int, cb: int, cr: int) -> bytes:
    """Return the exact uncompressed I420 frame represented by a palette key."""

    y = _require_u8("y", y)
    cb = _require_u8("cb", cb)
    cr = _require_u8("cr", cr)
    key = (y, cb, cr)
    if key not in _PALETTE_PAYLOADS:
        raise AV1IntraUnsupportedError(
            "the constant color is outside the qualified {0, 128, 255} palette"
        )
    return bytes((y,)) * (AV1_INTRA_WIDTH * AV1_INTRA_HEIGHT) + bytes((cb,)) * 64 + bytes((cr,)) * 64


def _check_canonical_obu_sizes(payload: bytes, obus: tuple[AV1OBU, ...]) -> None:
    raw = memoryview(payload)
    for obu in obus:
        start = obu.offset + obu.header_size
        end = start + obu.size_field_size
        if end > len(raw):
            raise AV1IntraMalformedError("AV1 OBU size field exceeds payload")
        if bytes(raw[start:end]) != leb128_encode(len(obu.payload)):
            raise AV1IntraMalformedError("AV1 OBU size field is not canonical")


def _validate_payload_structure(payload: bytes) -> tuple[AV1OBU, ...]:
    if not payload:
        raise AV1IntraMalformedError("AV1 payload must not be empty")
    if len(payload) > _MAX_PAYLOAD_BYTES:
        raise AV1IntraMalformedError("AV1 payload exceeds the bounded profile limit")
    try:
        info = validate_av1_image_payload(
            payload,
            AV1_INTRA_WIDTH,
            AV1_INTRA_HEIGHT,
            bit_depth=AV1_INTRA_BIT_DEPTH,
        )
    except (AV1Error, TypeError, ValueError) as exc:
        if isinstance(exc, AV1IntraError):
            raise
        raise AV1IntraMalformedError(str(exc)) from exc
    obus = info.obus
    _check_canonical_obu_sizes(payload, obus)
    if tuple(item.obu_type for item in obus) != (
        OBU_TEMPORAL_DELIMITER,
        OBU_SEQUENCE_HEADER,
        OBU_FRAME,
    ):
        raise AV1IntraUnsupportedError(
            "the bounded profile requires temporal-delimiter, sequence-header, frame"
        )
    if any(item.extension_flag or not item.has_size_field for item in obus):
        raise AV1IntraUnsupportedError("layered or size-less OBUs are not supported")
    sequence = parse_sequence_header(obus[1].payload)
    if (
        sequence.width != AV1_INTRA_WIDTH
        or sequence.height != AV1_INTRA_HEIGHT
        or sequence.bit_depth != AV1_INTRA_BIT_DEPTH
        or sequence.subsampling_x != 1
        or sequence.subsampling_y != 1
        or sequence.monochrome
    ):
        raise AV1IntraUnsupportedError("AV1 sequence header does not match the fixed I420 profile")
    if not obus[2].payload:
        raise AV1IntraMalformedError("combined AV1 frame/tile OBU has an empty payload")
    return obus


def encode_av1_intra_constant(
    y: int = 128,
    cb: int = 128,
    cr: int = 128,
    *,
    width: int = AV1_INTRA_WIDTH,
    height: int = AV1_INTRA_HEIGHT,
    bit_depth: int = AV1_INTRA_BIT_DEPTH,
    chroma: str = AV1_INTRA_CHROMA,
) -> bytes:
    """Encode one supported constant I420 frame as a complete AV1 access unit.

    The function is intentionally scalar rather than accepting an array ABI.
    A caller must provide the constant Y/Cb/Cr values; arbitrary image buffers
    and all non-palette values fail closed.
    """

    _validate_profile(width, height, bit_depth, chroma)
    key = (_require_u8("y", y), _require_u8("cb", cb), _require_u8("cr", cr))
    try:
        payload = bytes(_PALETTE_PAYLOADS[key])
    except KeyError as exc:
        raise AV1IntraUnsupportedError(
            "the constant color is outside the qualified {0, 128, 255} palette"
        ) from exc
    _validate_payload_structure(payload)
    return payload


def encode_av1_intra_constant_16x16(y: int = 128, cb: int = 128, cr: int = 128) -> bytes:
    """Explicit alias for the fixed 16x16 profile."""

    return encode_av1_intra_constant(y, cb, cr)


def validate_av1_intra_payload(
    payload: bytes | bytearray | memoryview,
    y: int,
    cb: int,
    cr: int,
    *,
    width: int = AV1_INTRA_WIDTH,
    height: int = AV1_INTRA_HEIGHT,
    bit_depth: int = AV1_INTRA_BIT_DEPTH,
    chroma: str = AV1_INTRA_CHROMA,
) -> AV1IntraValidation:
    """Validate exact fixed-profile membership and AV1 OBU structure."""

    _validate_profile(width, height, bit_depth, chroma)
    key = (_require_u8("y", y), _require_u8("cb", cb), _require_u8("cr", cr))
    if key not in _PALETTE_PAYLOADS:
        raise AV1IntraUnsupportedError(
            "the constant color is outside the qualified {0, 128, 255} palette"
        )
    try:
        raw = bytes(payload)
    except (TypeError, ValueError) as exc:
        raise AV1IntraMalformedError("payload must expose a bytes-like value") from exc
    expected = _PALETTE_PAYLOADS[key]
    if raw != expected:
        raise AV1IntraUnsupportedError(
            "payload is not the decoder-qualified lossless payload for this palette color"
        )
    obus = _validate_payload_structure(raw)
    return AV1IntraValidation(
        valid=True,
        width=width,
        height=height,
        bit_depth=bit_depth,
        chroma="420",
        y=key[0],
        cb=key[1],
        cr=key[2],
        payload_size=len(raw),
        obu_types=tuple(item.obu_type for item in obus),
        frame_tile_count=1,
        exact_palette_match=True,
        structural_only=False,
    )


def av1_intra_capability_report() -> Mapping[str, object]:
    """Return a serializable capability report without probing external tools."""

    capability = AV1IntraCapability(
        width=AV1_INTRA_WIDTH,
        height=AV1_INTRA_HEIGHT,
        bit_depth=AV1_INTRA_BIT_DEPTH,
        chroma=AV1_INTRA_CHROMA,
        lossless=True,
        intra_only=True,
        tile_count=1,
        palette_levels=_PALETTE_LEVELS,
        palette_size=len(_PALETTE_PAYLOADS),
        runtime_dependencies=(),
    )
    return {
        "codec": "AV1",
        "profile": "bounded-intra-constant-16x16-i420",
        "native_runtime": True,
        "lossless": capability.lossless,
        "intra_only": capability.intra_only,
        "width": capability.width,
        "height": capability.height,
        "bit_depth": capability.bit_depth,
        "chroma": capability.chroma,
        "tile_count": capability.tile_count,
        "palette_levels": capability.palette_levels,
        "palette_size": capability.palette_size,
        "runtime_dependencies": capability.runtime_dependencies,
        "obu_form": (OBU_TEMPORAL_DELIMITER, OBU_SEQUENCE_HEADER, OBU_FRAME),
        "external_decoder_validation_required": True,
        "general_encoder": False,
        "limitations": (
            "exactly 16x16 pixels",
            "8-bit 4:2:0 I420 only",
            "constant Y/Cb/Cr planes only",
            "Y/Cb/Cr values limited to 0, 128, or 255",
            "one combined frame OBU and one implicit tile",
            "no alpha, metadata, 10/12-bit, 4:2:2, 4:4:4, tiling, or animation",
        ),
    }


def av1_intra_payload_report(
    payload: bytes | bytearray | memoryview,
    y: int,
    cb: int,
    cr: int,
) -> Mapping[str, object]:
    """Return a compact exact-profile validation report."""

    result = validate_av1_intra_payload(payload, y, cb, cr)
    return {
        "valid": result.valid,
        "profile": "bounded-intra-constant-16x16-i420",
        "width": result.width,
        "height": result.height,
        "bit_depth": result.bit_depth,
        "chroma": result.chroma,
        "constant_y": result.y,
        "constant_cb": result.cb,
        "constant_cr": result.cr,
        "payload_size": result.payload_size,
        "obu_types": result.obu_types,
        "frame_tile_count": result.frame_tile_count,
        "exact_palette_match": result.exact_palette_match,
        "structural_only": result.structural_only,
    }


__all__ = [
    "AV1_INTRA_WIDTH",
    "AV1_INTRA_HEIGHT",
    "AV1_INTRA_BIT_DEPTH",
    "AV1_INTRA_CHROMA",
    "AV1IntraError",
    "AV1IntraMalformedError",
    "AV1IntraUnsupportedError",
    "AV1IntraCapability",
    "AV1IntraValidation",
    "supported_constant_colors",
    "expected_i420_frame",
    "encode_av1_intra_constant",
    "encode_av1_intra_constant_16x16",
    "validate_av1_intra_payload",
    "av1_intra_capability_report",
    "av1_intra_payload_report",
]
