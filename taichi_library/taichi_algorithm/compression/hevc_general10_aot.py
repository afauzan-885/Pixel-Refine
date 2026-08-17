"""Bounded compressed Main10 HEVC intra profile.

This module reuses the already validated CABAC/DC-intra syntax from the
8-bit bounded encoder, but supplies 10-bit planar samples and a Main 10
parameter set.  It intentionally accepts only constant-inside-CTU blocks with
validated DC references until a pixel-derived residual transform and nonzero-
QP path is qualified.  The input ABI is little-endian planar ``uint16`` bytes:
Y, Cb, then Cr, with 4:2:0 chroma.
"""

from __future__ import annotations

from typing import Mapping

from .hevc_aot import (
    HEVCBitReader,
    HEVCBitWriter,
    HEVC_CHROMA_420,
    HEVC_NAL_IDR_N_LP,
    HEVC_NAL_PPS,
    HEVC_NAL_SPS,
    HEVC_NAL_VPS,
    HEVCProfileTierLevel,
    build_hvcc,
    build_nal_unit,
    build_vps_rbsp,
    main_profile_tier_level,
)
from .hevc_general_aot import (
    HEVC_GENERAL_BIT_DEPTH,
    HEVC_GENERAL_MAX_HEIGHT,
    HEVC_GENERAL_MAX_WIDTH,
    HEVC_GENERAL_MIN_DIMENSION,
    HEVCGeneralBitstreamError,
    HEVCGeneralProfileError,
    HEVCGeneralPicture,
    _build_general_pps_rbsp,
    _build_general_slice_rbsp,
    _build_general_sps_rbsp,
    _validate_geometry,
    _validate_qp,
    validate_hevc_general_annex_b,
)


HEVC_GENERAL10_BIT_DEPTH = 10
HEVC_GENERAL10_BYTES_PER_SAMPLE = 2
HEVC_GENERAL10_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_GENERAL10_MAX_QP = 0


def hevc_general10_sample_count(
    width: int,
    height: int,
) -> int:
    _validate_geometry(width, height)
    return width * height + 2 * (width // 2) * (height // 2)


def hevc_general10_sample_bytes(
    width: int = 16,
    height: int = 16,
) -> int:
    return hevc_general10_sample_count(width, height) * HEVC_GENERAL10_BYTES_PER_SAMPLE


def _main10_ptl(level_idc: int = 120) -> HEVCProfileTierLevel:
    base = main_profile_tier_level(level_idc)
    return HEVCProfileTierLevel(
        profile_space=base.profile_space,
        tier_flag=base.tier_flag,
        profile_idc=2,
        profile_compatibility_flags=0x60000000,
        constraint_indicator_flags=base.constraint_indicator_flags,
        level_idc=base.level_idc,
        max_sub_layers_minus1=base.max_sub_layers_minus1,
    )


def _read_plane_value(raw: bytes, index: int) -> int:
    offset = index * HEVC_GENERAL10_BYTES_PER_SAMPLE
    return int.from_bytes(raw[offset:offset + 2], "little")


def _validate_samples(
    samples: object,
    width: int,
    height: int,
) -> tuple[tuple[tuple[int, int, int], ...], str]:
    expected = hevc_general10_sample_bytes(width, height)
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("Main10 samples must be a contiguous little-endian uint16 byte buffer") from exc
    if view.ndim != 1 or not view.c_contiguous or view.nbytes != expected:
        raise HEVCGeneralProfileError(
            f"the {width}x{height} Main10 profile requires exactly {expected} bytes"
        )
    raw = view.cast("B").tobytes()
    sample_count = width * height + 2 * (width // 2) * (height // 2)
    values = tuple(_read_plane_value(raw, index) for index in range(sample_count))
    if any(value > 1023 for value in values):
        raise HEVCGeneralProfileError("Main10 samples must fit in ten bits")

    luma_count = width * height
    chroma_width = width // 2
    chroma_height = height // 2
    chroma_count = chroma_width * chroma_height
    planes = (
        values[:luma_count],
        values[luma_count:luma_count + chroma_count],
        values[luma_count + chroma_count:],
    )
    ctu_values: list[tuple[int, int, int]] = []
    for block_y in range(0, height, 16):
        for block_x in range(0, width, 16):
            plane_values: list[int] = []
            for plane_index, plane in enumerate(planes):
                if plane_index == 0:
                    plane_width, x0, y0 = width, block_x, block_y
                    block_width, block_height = 16, 16
                else:
                    plane_width, x0, y0 = chroma_width, block_x // 2, block_y // 2
                    block_width, block_height = 8, 8
                first = plane[y0 * plane_width + x0]
                for row in range(y0, y0 + block_height):
                    start = row * plane_width + x0
                    if any(value != first for value in plane[start:start + block_width]):
                        raise HEVCGeneralProfileError(
                            "compressed Main10 HEVC currently requires constant values inside each CTU block"
                        )
                plane_values.append(first)
            ctu_values.append(tuple(plane_values))

    profile = (
        "constant_planes"
        if len(set(planes[0])) == 1
        and len(set(planes[1])) == 1
        and len(set(planes[2])) == 1
        else "horizontal_ctu_stripes"
    )
    if profile != "constant_planes":
        ctu_columns = width // 16
        for ctu_y in range(1, height // 16):
            for ctu_x in range(1, ctu_columns):
                left = ctu_values[ctu_y * ctu_columns + ctu_x - 1]
                top = ctu_values[(ctu_y - 1) * ctu_columns + ctu_x]
                if left != top:
                    raise HEVCGeneralProfileError(
                        "multi-row compressed Main10 CTUs require matching top and left references"
                    )
        if height != 16:
            profile = "ctu_constant_blocks"
    return tuple(ctu_values), profile


def build_hevc_general10_picture(
    samples: object,
    width: int = 16,
    height: int = 16,
    *,
    qp: int = 0,
) -> HEVCGeneralPicture:
    _validate_geometry(width, height)
    _validate_qp(qp)
    if qp > HEVC_GENERAL10_MAX_QP:
        raise HEVCGeneralProfileError("only QP 0 is qualified for the Main10 bounded profile")
    ctu_values, _profile = _validate_samples(samples, width, height)
    ptl = _main10_ptl()
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(
        HEVC_NAL_SPS,
        _build_general_sps_rbsp(
            width,
            height,
            HEVC_CHROMA_420,
            bit_depth=HEVC_GENERAL10_BIT_DEPTH,
            ptl=ptl,
        ),
    )
    pps = build_nal_unit(HEVC_NAL_PPS, _build_general_pps_rbsp())
    vcl = build_nal_unit(
        HEVC_NAL_IDR_N_LP,
        _build_general_slice_rbsp(
            b"",
            width,
            height,
            qp,
            HEVC_CHROMA_420,
            ctu_values=ctu_values,
            dc_midpoint=1 << (HEVC_GENERAL10_BIT_DEPTH - 1),
            dc_level_divisor=4,
        ),
    )
    hvcc = build_hvcc(
        (vps, sps, pps),
        ptl=ptl,
        bit_depth=HEVC_GENERAL10_BIT_DEPTH,
        chroma_format_idc=HEVC_CHROMA_420,
    )
    picture = HEVCGeneralPicture(
        width,
        height,
        HEVC_GENERAL10_BIT_DEPTH,
        HEVC_CHROMA_420,
        (vps, sps, pps, vcl),
        hvcc,
    )
    validate_hevc_general_annex_b(
        picture.annex_b,
        width=width,
        height=height,
        chroma_format_idc=HEVC_CHROMA_420,
        bit_depth=HEVC_GENERAL10_BIT_DEPTH,
    )
    return picture


def encode_hevc_general10_aot(
    samples: object,
    width: int = 16,
    height: int = 16,
    *,
    qp: int = 0,
) -> bytes:
    return build_hevc_general10_picture(samples, width, height, qp=qp).annex_b


def hevc_general10_capability_report() -> Mapping[str, object]:
    return {
        "parameter_sets": True,
        "compressed_intra_profile": True,
        "bit_depth": 10,
        "chroma_formats": (HEVC_CHROMA_420,),
        "quantization": "QP 0 only",
        "arbitrary_pixels": False,
        "horizontal_ctu_stripes": True,
        "multi_row_ctu_constant_blocks": True,
        "runtime_codec_dependencies": (),
        "externally_decoded": True,
        "external_decoder_validated_payload": True,
        "gpu_full_codec": False,
        "limitations": (
            "constant-inside-CTU blocks with matching top/left references only",
            "general residual AC/transform derivation and nonzero QP remain disabled",
        ),
    }


__all__ = [
    "HEVC_GENERAL10_BIT_DEPTH",
    "HEVC_GENERAL10_CHROMA_FORMAT_IDC",
    "HEVC_GENERAL10_BYTES_PER_SAMPLE",
    "hevc_general10_sample_count",
    "hevc_general10_sample_bytes",
    "HEVCGeneralProfileError",
    "HEVCGeneralBitstreamError",
    "HEVCGeneralPicture",
    "build_hevc_general10_picture",
    "encode_hevc_general10_aot",
    "hevc_general10_capability_report",
]
