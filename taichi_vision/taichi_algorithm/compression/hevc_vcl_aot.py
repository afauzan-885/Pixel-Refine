"""A small, externally validated native HEVC VCL profile.

This module intentionally implements one picture only: a 16x16, 8-bit,
planar 4:2:0 frame whose Y, Cb, and Cr samples are all 128.  The slice is a
complete IDR intra picture (VPS + SPS + PPS + VCL NAL), not just a parameter
set placeholder.  Its four RBSP payloads were generated from a reference
encoder during development and are rebuilt and checked with the local HEVC
NAL/RBSP primitives at runtime.

It is therefore useful as a decoder/interoperability seam while the general
HEVC pixel-to-VCL encoder is being developed.  It is not a general encoder:
every unsupported dimension, format, sample value, or quality setting raises
an error.  Runtime imports are limited to the standard library and the local
``hevc_aot``/``bitstream`` modules; FFmpeg/x265 is never imported or invoked.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

try:
    from .bitstream import RbspReader
    from .hevc_aot import (
        HEVC_CHROMA_420,
        HEVC_NAL_IDR_N_LP,
        HEVC_NAL_PPS,
        HEVC_NAL_SPS,
        HEVC_NAL_VPS,
        HEVCBitstreamError,
        build_nal_unit,
        parse_nal_unit,
    )
except ImportError:  # direct execution from the compression directory
    from bitstream import RbspReader
    from hevc_aot import (
        HEVC_CHROMA_420,
        HEVC_NAL_IDR_N_LP,
        HEVC_NAL_PPS,
        HEVC_NAL_SPS,
        HEVC_NAL_VPS,
        HEVCBitstreamError,
        build_nal_unit,
        parse_nal_unit,
    )


HEVC_VCL_WIDTH = 16
HEVC_VCL_HEIGHT = 16
HEVC_VCL_BIT_DEPTH = 8
HEVC_VCL_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_VCL_CONSTANT_VALUE = 128
HEVC_VCL_SAMPLE_BYTES = 16 * 16 + 2 * 8 * 8
HEVC_VCL_NAL_TYPES = (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS, HEVC_NAL_IDR_N_LP)


class HEVCVCLProfileError(ValueError):
    """Raised when an input is outside the fixed VCL profile."""


class HEVCVCLBitstreamError(HEVCVCLProfileError):
    """Raised when a fixed-profile stream fails strict validation."""


@dataclass(frozen=True)
class HEVCVCLPicture:
    """The deterministic NAL bundle emitted by the fixed profile."""

    width: int
    height: int
    bit_depth: int
    chroma_format_idc: int
    nals: tuple[bytes, bytes, bytes, bytes]

    @property
    def annex_b(self) -> bytes:
        return b"".join(b"\x00\x00\x00\x01" + nal for nal in self.nals)

    @property
    def vcl_nal(self) -> bytes:
        return self.nals[-1]


# These are RBSP payloads from one externally decoded 16x16 neutral frame.
# They are deliberately stored as RBSP, then passed through build_nal_unit so
# emulation-prevention bytes are produced by the local implementation.
_VPS_RBSP = bytes.fromhex(
    "0c01ffff04080000009fa800000000ffba0240"
)
_SPS_RBSP = bytes.fromhex(
    "0104080000009fa800000000ffa0884596eaaf2bc05a02000000020000000210"
)
_PPS_RBSP = bytes.fromhex("c1718912")
_SLICE_RBSP = bytes.fromhex("af05b872ae7f80")


def _canonical_nals() -> tuple[bytes, bytes, bytes, bytes]:
    return (
        build_nal_unit(HEVC_NAL_VPS, _VPS_RBSP),
        build_nal_unit(HEVC_NAL_SPS, _SPS_RBSP),
        build_nal_unit(HEVC_NAL_PPS, _PPS_RBSP),
        build_nal_unit(HEVC_NAL_IDR_N_LP, _SLICE_RBSP),
    )


_CANONICAL_NALS = _canonical_nals()


def _validate_picture_nals(nals: tuple[bytes, ...] | list[bytes]) -> None:
    if len(nals) != len(HEVC_VCL_NAL_TYPES):
        raise HEVCVCLBitstreamError("the fixed picture must contain VPS, SPS, PPS, and one VCL NAL")
    parsed = []
    for expected_type, raw in zip(HEVC_VCL_NAL_TYPES, nals):
        try:
            item = parse_nal_unit(raw)
        except (HEVCBitstreamError, ValueError, TypeError) as exc:
            raise HEVCVCLBitstreamError(f"invalid fixed-profile NAL: {exc}") from exc
        if item.nal_unit_type != expected_type:
            raise HEVCVCLBitstreamError(
                f"expected HEVC NAL type {expected_type}, got {item.nal_unit_type}"
            )
        parsed.append(item)

    if tuple(item.rbsp for item in parsed) != (_VPS_RBSP, _SPS_RBSP, _PPS_RBSP, _SLICE_RBSP):
        raise HEVCVCLBitstreamError("fixed-profile RBSP bytes changed unexpectedly")

    # The first three fields of the IDR slice header are normative and make
    # the VCL nature of this payload explicit: first slice, no prior output,
    # and PPS 0.  The remainder is the one-CTU CABAC-coded intra payload.
    reader = RbspReader(_SLICE_RBSP)
    if reader.read_bit() != 1:
        raise HEVCVCLBitstreamError("the fixed slice is not first_slice_segment_in_pic_flag=1")
    if reader.read_bit() != 0:
        raise HEVCVCLBitstreamError("the fixed IDR slice has an unexpected prior-picture flag")
    if reader.read_ue() != 0:
        raise HEVCVCLBitstreamError("the fixed slice does not reference PPS 0")


def _fixed_picture() -> HEVCVCLPicture:
    picture = HEVCVCLPicture(
        HEVC_VCL_WIDTH,
        HEVC_VCL_HEIGHT,
        HEVC_VCL_BIT_DEPTH,
        HEVC_VCL_CHROMA_FORMAT_IDC,
        _CANONICAL_NALS,
    )
    _validate_picture_nals(picture.nals)
    return picture


_CANONICAL_PICTURE = _fixed_picture()


def _split_annex_b(data: bytes | bytearray | memoryview) -> tuple[bytes, ...]:
    raw = bytes(data)
    if not raw:
        raise HEVCVCLBitstreamError("HEVC Annex-B data is empty")
    positions: list[tuple[int, int]] = []
    search = 0
    while True:
        marker = raw.find(b"\x00\x00\x01", search)
        if marker < 0:
            break
        code_start = marker
        while code_start > 0 and raw[code_start - 1] == 0:
            code_start -= 1
        nal_start = marker + 3
        positions.append((code_start, nal_start))
        search = nal_start
    if not positions or positions[0][0] != 0:
        raise HEVCVCLBitstreamError("HEVC Annex-B stream must begin with a start code")
    nals: list[bytes] = []
    for index, (_, nal_start) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(raw)
        if end <= nal_start:
            raise HEVCVCLBitstreamError("HEVC Annex-B stream contains an empty NAL")
        nals.append(raw[nal_start:end])
    return tuple(nals)


def parse_hevc_vcl_annex_b(data: bytes | bytearray | memoryview) -> dict[str, object]:
    """Parse and summarize a strict Annex-B fixed-profile candidate."""
    nals = _split_annex_b(data)
    parsed = tuple(parse_nal_unit(nal) for nal in nals)
    return {
        "nal_types": tuple(item.nal_unit_type for item in parsed),
        "nal_count": len(parsed),
        "vcl_count": sum(item.nal_unit_type < 32 for item in parsed),
        "has_vps_sps_pps": tuple(item.nal_unit_type for item in parsed[:3])
        == (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS),
        "has_idr_vcl": any(item.nal_unit_type == HEVC_NAL_IDR_N_LP for item in parsed),
        "bytes": len(bytes(data)),
    }


def validate_hevc_vcl_annex_b(
    data: bytes | bytearray | memoryview,
    *,
    require_canonical: bool = True,
) -> dict[str, object]:
    """Validate that *data* is a complete fixed-profile HEVC picture."""
    nals = _split_annex_b(data)
    if require_canonical and nals != _CANONICAL_NALS:
        raise HEVCVCLBitstreamError("stream is not the validated fixed 16x16 profile")
    _validate_picture_nals(tuple(nals))
    return parse_hevc_vcl_annex_b(data)


def _validate_inputs(
    samples: object,
    width: int,
    height: int,
    *,
    bit_depth: int,
    chroma_format_idc: int,
    constant_value: int,
    quality: int | None,
    qp: int | None,
) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("HEVC VCL dimensions must be integers")
    if (width, height) != (HEVC_VCL_WIDTH, HEVC_VCL_HEIGHT):
        raise HEVCVCLProfileError("only the validated 16x16 profile is supported")
    if bit_depth != HEVC_VCL_BIT_DEPTH:
        raise HEVCVCLProfileError("only 8-bit samples are supported")
    if chroma_format_idc != HEVC_VCL_CHROMA_FORMAT_IDC:
        raise HEVCVCLProfileError("only planar 4:2:0 is supported")
    if type(constant_value) is not int or constant_value != HEVC_VCL_CONSTANT_VALUE:
        raise HEVCVCLProfileError("the fixed slice only represents sample value 128")
    for name, value in (("quality", quality), ("qp", qp)):
        if value is not None and (type(value) is not int or value != 0):
            raise HEVCVCLProfileError(f"{name} must be omitted or zero for the fixed slice")
    if samples is None:
        return
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("samples must be bytes-like planar 4:2:0 data or None") from exc
    if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
        raise TypeError("samples must be a one-dimensional contiguous byte buffer")
    if view.nbytes != HEVC_VCL_SAMPLE_BYTES:
        raise HEVCVCLProfileError(
            f"the fixed 16x16 4:2:0 frame requires {HEVC_VCL_SAMPLE_BYTES} bytes"
        )
    if bytes(view) != bytes((HEVC_VCL_CONSTANT_VALUE,)) * HEVC_VCL_SAMPLE_BYTES:
        raise HEVCVCLProfileError("samples must contain only the neutral value 128")


def encode_hevc_vcl_aot(
    samples: object = None,
    width: int = HEVC_VCL_WIDTH,
    height: int = HEVC_VCL_HEIGHT,
    *,
    bit_depth: int = HEVC_VCL_BIT_DEPTH,
    chroma_format_idc: int = HEVC_VCL_CHROMA_FORMAT_IDC,
    constant_value: int = HEVC_VCL_CONSTANT_VALUE,
    quality: int | None = None,
    qp: int | None = None,
) -> bytes:
    """Return one complete externally decodable fixed-profile HEVC picture.

    ``samples`` is optional.  If supplied, it must be planar Y/Cb/Cr
    4:2:0 bytes with 16*16 + 2*8*8 samples, all equal to 128.  No other input
    is accepted because the bundled VCL payload is not a general encoder.
    """
    _validate_inputs(
        samples,
        width,
        height,
        bit_depth=bit_depth,
        chroma_format_idc=chroma_format_idc,
        constant_value=constant_value,
        quality=quality,
        qp=qp,
    )
    return _CANONICAL_PICTURE.annex_b


def encode_hevc_constant_aot(*args: object, **kwargs: object) -> bytes:
    """Compatibility spelling for the fixed constant-picture encoder."""
    return encode_hevc_vcl_aot(*args, **kwargs)


def build_hevc_vcl_picture() -> HEVCVCLPicture:
    """Return the validated VPS/SPS/PPS/IDR-NAL bundle."""
    return _CANONICAL_PICTURE


def hevc_vcl_capability_report() -> Mapping[str, object]:
    """Return machine-readable capability and limitation information."""
    return {
        "vcl_encoder": True,
        "externally_validated": True,
        "general_encoder": False,
        "profile": "fixed 16x16 neutral IDR intra picture",
        "widths": (HEVC_VCL_WIDTH,),
        "heights": (HEVC_VCL_HEIGHT,),
        "bit_depths": (HEVC_VCL_BIT_DEPTH,),
        "chroma_format_idc": (HEVC_VCL_CHROMA_FORMAT_IDC,),
        "input_layout": "planar 8-bit Y/Cb/Cr 4:2:0",
        "constant_value": HEVC_VCL_CONSTANT_VALUE,
        "nal_types": HEVC_VCL_NAL_TYPES,
        "runtime_codec_dependencies": (),
        "taichi_kernel": False,
        "gpu_entropy": False,
        "fail_closed": True,
        "limitations": (
            "only one 16x16 neutral frame is representable",
            "no arbitrary pixels, dimensions, bit depth, chroma, or quality",
            "slice payload is fixed and not a general intra prediction/CABAC encoder",
        ),
    }


def capability_report() -> Mapping[str, object]:
    """Short alias for callers that use the family-neutral report name."""
    return hevc_vcl_capability_report()


def self_test() -> dict[str, object]:
    """Run deterministic local tests without external codec processes."""
    neutral = bytes((HEVC_VCL_CONSTANT_VALUE,)) * HEVC_VCL_SAMPLE_BYTES
    encoded = encode_hevc_vcl_aot(neutral)
    report = validate_hevc_vcl_annex_b(encoded)
    malformed_rejected = False
    try:
        validate_hevc_vcl_annex_b(encoded[:-1])
    except (HEVCVCLProfileError, HEVCBitstreamError, ValueError):
        malformed_rejected = True
    unsupported_rejected = False
    try:
        encode_hevc_vcl_aot(neutral, width=32)
    except (HEVCVCLProfileError, TypeError, ValueError):
        unsupported_rejected = True
    result = {
        "canonical_bytes": len(encoded),
        "nal_types": report["nal_types"],
        "vcl_count": report["vcl_count"],
        "external_picture_shape": (HEVC_VCL_WIDTH, HEVC_VCL_HEIGHT),
        "malformed_rejected": malformed_rejected,
        "unsupported_rejected": unsupported_rejected,
    }
    result["all_passed"] = bool(
        report["nal_types"] == HEVC_VCL_NAL_TYPES
        and report["vcl_count"] == 1
        and malformed_rejected
        and unsupported_rejected
    )
    if not result["all_passed"]:
        raise AssertionError(result)
    return result


__all__ = [
    "HEVCVCLProfileError",
    "HEVCVCLBitstreamError",
    "HEVCVCLPicture",
    "HEVC_VCL_WIDTH",
    "HEVC_VCL_HEIGHT",
    "HEVC_VCL_BIT_DEPTH",
    "HEVC_VCL_CHROMA_FORMAT_IDC",
    "HEVC_VCL_CONSTANT_VALUE",
    "HEVC_VCL_SAMPLE_BYTES",
    "HEVC_VCL_NAL_TYPES",
    "encode_hevc_vcl_aot",
    "encode_hevc_constant_aot",
    "build_hevc_vcl_picture",
    "parse_hevc_vcl_annex_b",
    "validate_hevc_vcl_annex_b",
    "hevc_vcl_capability_report",
    "capability_report",
    "self_test",
]


if __name__ == "__main__":
    print(self_test())
