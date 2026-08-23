"""Bounded CABAC/intra-compressed HEVC neutral still-image profile.

This module is an interoperability step toward the general native HEVC
encoder.  It emits a real IDR slice using 16x16 intra DC prediction, zero
residuals, and CABAC; it is not a general image encoder.  Only planar 8-bit
4:2:0 frames whose three planes are entirely 128 are accepted.  Keeping that
restriction explicit lets the profile be externally decoded and measured
without pretending that arbitrary input pixels are supported.

The runtime uses only the standard library and local bitstream primitives.
FFmpeg is used only by verification code outside this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .hevc_aot import (
    HEVC_CHROMA_420,
    HEVC_NAL_IDR_N_LP,
    HEVC_NAL_PPS,
    HEVC_NAL_SPS,
    HEVC_NAL_VPS,
    HEVCBitWriter,
    HEVCCabacEncoder,
    HEVCProfileError,
    build_hvcc,
    build_nal_unit,
    build_pps_rbsp,
    build_vps_rbsp,
    cabac_context_from_init,
    main_profile_tier_level,
    parse_nal_unit,
)


HEVC_NEUTRAL_WIDTH = 16
HEVC_NEUTRAL_HEIGHT = 16
HEVC_NEUTRAL_BIT_DEPTH = 8
HEVC_NEUTRAL_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_NEUTRAL_MIN_DIMENSION = 16
HEVC_NEUTRAL_MAX_WIDTH = 4096
HEVC_NEUTRAL_MAX_HEIGHT = 4096
HEVC_NEUTRAL_VALUE = 128


class HEVCNeutralProfileError(HEVCProfileError):
    """Raised when input is outside the compressed neutral profile."""


class HEVCNeutralBitstreamError(HEVCNeutralProfileError):
    """Raised when the bounded compressed stream is malformed locally."""


def _validate_geometry(width: int, height: int) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("HEVC neutral dimensions must be integers")
    if not HEVC_NEUTRAL_MIN_DIMENSION <= width <= HEVC_NEUTRAL_MAX_WIDTH:
        raise HEVCNeutralProfileError("HEVC neutral width is outside the bounded profile")
    if not HEVC_NEUTRAL_MIN_DIMENSION <= height <= HEVC_NEUTRAL_MAX_HEIGHT:
        raise HEVCNeutralProfileError("HEVC neutral height is outside the bounded profile")
    if width % 16 or height % 16:
        raise HEVCNeutralProfileError("HEVC neutral dimensions must be multiples of 16")


def _sample_bytes(width: int, height: int) -> int:
    _validate_geometry(width, height)
    return width * height + 2 * (width // 2) * (height // 2)


def _validate_samples(samples: object, width: int, height: int) -> bytes:
    expected = _sample_bytes(width, height)
    if samples is None:
        return bytes((HEVC_NEUTRAL_VALUE,)) * expected
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("HEVC neutral samples must be a contiguous byte buffer") from exc
    if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
        raise TypeError("HEVC neutral samples must be a one-dimensional byte buffer")
    if view.nbytes != expected:
        raise HEVCNeutralProfileError(f"the profile requires exactly {expected} planar bytes")
    data = bytes(view)
    if data != bytes((HEVC_NEUTRAL_VALUE,)) * expected:
        raise HEVCNeutralProfileError("the compressed neutral profile accepts only sample value 128")
    return data


def _build_neutral_sps_rbsp(width: int, height: int) -> bytes:
    writer = HEVCBitWriter()
    ptl = main_profile_tier_level(153 if max(width, height) > 2048 else 120)
    writer.write(0, 4)
    writer.write(0, 3)
    writer.flag(1)
    ptl.write(writer)
    writer.ue(0)
    writer.ue(HEVC_CHROMA_420)
    writer.ue(width)
    writer.ue(height)
    writer.flag(0)  # conformance_window_flag
    writer.ue(0)  # bit_depth_luma_minus8
    writer.ue(0)  # bit_depth_chroma_minus8
    writer.ue(4)  # log2_max_pic_order_cnt_lsb_minus4
    writer.flag(0)  # sps_sub_layer_ordering_info_present_flag
    writer.ue(0)
    writer.ue(0)
    writer.ue(0)
    writer.ue(1)  # log2_min_luma_coding_block_size_minus3: 16x16
    writer.ue(0)  # log2_diff_max_min_luma_coding_block_size
    writer.ue(0)  # log2_min_luma_transform_block_size_minus2: 4x4
    writer.ue(2)  # log2_diff_max_min_luma_transform_block_size: max 16x16
    writer.ue(0)  # max_transform_hierarchy_depth_inter
    writer.ue(0)  # max_transform_hierarchy_depth_intra
    writer.flag(0)  # scaling_list_enabled_flag
    writer.flag(0)  # amp_enabled_flag
    writer.flag(0)  # sample_adaptive_offset_enabled_flag
    writer.flag(0)  # pcm_enabled_flag
    writer.ue(0)  # num_short_term_ref_pic_sets
    writer.flag(0)  # long_term_ref_pics_present_flag
    writer.flag(0)  # sps_temporal_mvp_enabled_flag
    writer.flag(1)  # strong_intra_smoothing_enabled_flag
    writer.flag(0)  # vui_parameters_present_flag
    writer.flag(0)  # sps_extension_present_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


def _build_neutral_slice_rbsp(width: int, height: int) -> bytes:
    writer = HEVCBitWriter()
    writer.flag(1)  # first_slice_segment_in_pic_flag
    writer.flag(0)  # no_output_of_prior_pics_flag for IDR_N_LP
    writer.ue(0)  # slice_pic_parameter_set_id
    writer.ue(2)  # slice_type = I
    writer.se(0)  # slice_qp_delta
    writer.flag(1)  # slice_loop_filter_across_slices_enabled_flag
    writer.flag(1)  # alignment_bit_equal_to_one
    while not writer.byte_aligned:
        writer.flag(0)

    # Use the shared HM-style queue/carry encoder.  The I_PCM profile has a
    # separate arithmetic-reset cadence; this compressed profile needs the
    # normal continuous CABAC queue across all syntax bins and bypass bins.
    encoder = HEVCCabacEncoder()
    part_mode = cabac_context_from_init(26, 184)
    prev_luma = cabac_context_from_init(26, 184)
    chroma_mode = cabac_context_from_init(26, 63)
    cbf_chroma = cabac_context_from_init(26, 94)
    cbf_luma = cabac_context_from_init(26, 141)
    block_count = (width // 16) * (height // 16)
    for index in range(block_count):
        encoder.encode_bin(part_mode, 1)  # PART_2Nx2N
        encoder.encode_bin(prev_luma, 0)  # prev_intra_luma_pred_flag = 0
        for _ in range(5):
            encoder.encode_bypass(0)  # rem_intra_luma_pred_mode = 0 -> DC mode
        encoder.encode_bin(chroma_mode, 0)  # chroma mode 4: use luma DC mode
        encoder.encode_bin(cbf_chroma, 0)  # cbf_cb = 0
        encoder.encode_bin(cbf_chroma, 0)  # cbf_cr = 0
        encoder.encode_bin(cbf_luma, 0)  # cbf_luma = 0
        encoder.encode_terminate(0 if index + 1 < block_count else 1)

    for value in encoder.flush():
        writer.write(value, 8)
    writer.rbsp_trailing_bits()
    return writer.bytes()


@dataclass(frozen=True)
class HEVCNeutralPicture:
    width: int
    height: int
    bit_depth: int
    chroma_format_idc: int
    nals: tuple[bytes, bytes, bytes, bytes]
    hvcc: bytes

    @property
    def annex_b(self) -> bytes:
        return b"".join(b"\x00\x00\x00\x01" + nal for nal in self.nals)


def build_hevc_neutral_picture(
    samples: object = None,
    width: int = HEVC_NEUTRAL_WIDTH,
    height: int = HEVC_NEUTRAL_HEIGHT,
) -> HEVCNeutralPicture:
    planar = _validate_samples(samples, width, height)
    ptl = main_profile_tier_level(153 if max(width, height) > 2048 else 120)
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(HEVC_NAL_SPS, _build_neutral_sps_rbsp(width, height))
    pps = build_nal_unit(HEVC_NAL_PPS, build_pps_rbsp())
    vcl = build_nal_unit(HEVC_NAL_IDR_N_LP, _build_neutral_slice_rbsp(width, height))
    hvcc = build_hvcc((vps, sps, pps), ptl=ptl, bit_depth=8, chroma_format_idc=HEVC_CHROMA_420)
    picture = HEVCNeutralPicture(width, height, 8, HEVC_CHROMA_420, (vps, sps, pps, vcl), hvcc)
    validate_hevc_neutral_annex_b(picture.annex_b, width=width, height=height)
    return picture


def encode_hevc_neutral_aot(
    samples: object = None,
    width: int = HEVC_NEUTRAL_WIDTH,
    height: int = HEVC_NEUTRAL_HEIGHT,
) -> bytes:
    return build_hevc_neutral_picture(samples, width, height).annex_b


def validate_hevc_neutral_annex_b(
    data: bytes | bytearray | memoryview,
    *,
    width: int | None = None,
    height: int | None = None,
) -> dict[str, object]:
    raw = bytes(data)
    nals: list[bytes] = []
    cursor = 0
    while cursor < len(raw):
        marker = raw.find(b"\x00\x00\x01", cursor)
        if marker < 0:
            break
        start = marker + 3
        next_marker = raw.find(b"\x00\x00\x01", start)
        end = len(raw) if next_marker < 0 else next_marker
        nal = raw[start:end].rstrip(b"\x00")
        if not nal:
            raise HEVCNeutralBitstreamError("neutral Annex-B stream contains an empty NAL")
        nals.append(nal)
        if next_marker < 0:
            break
        cursor = next_marker
    if len(nals) != 4:
        raise HEVCNeutralBitstreamError("neutral stream requires VPS, SPS, PPS, and one IDR NAL")
    parsed = tuple(parse_nal_unit(nal) for nal in nals)
    types = tuple(item.nal_unit_type for item in parsed)
    expected = (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS, HEVC_NAL_IDR_N_LP)
    if types != expected:
        raise HEVCNeutralBitstreamError(f"unexpected neutral NAL order: {types!r}")
    if (width is None) != (height is None):
        raise TypeError("neutral width and height must be supplied together")
    if width is not None:
        _validate_geometry(width, height)
    return {
        "nal_types": types,
        "nal_count": len(nals),
        "width": width,
        "height": height,
        "bit_depth": 8,
        "chroma_format_idc": HEVC_CHROMA_420,
        "compressed_intra_profile": True,
        "lossless_for_profile": True,
        "bytes": len(raw),
    }


def hevc_neutral_capability_report() -> Mapping[str, object]:
    return {
        "parameter_sets": True,
        "pixel_to_slice_encoder": True,
        "compressed_intra_profile": True,
        "lossless_for_profile": True,
        "general_encoder": False,
        "supported_profile": "16-aligned up to 4096x4096, 8-bit 4:2:0, all samples 128, DC intra + zero residual CABAC",
        "variable_dimensions": True,
        "variable_subsampling": False,
        "runtime_codec_dependencies": (),
        "external_decoder_validated_payload": True,
        "gpu_full_codec": False,
        "fail_closed": True,
    }


__all__ = [
    "HEVC_NEUTRAL_WIDTH",
    "HEVC_NEUTRAL_HEIGHT",
    "HEVC_NEUTRAL_VALUE",
    "HEVCNeutralProfileError",
    "HEVCNeutralBitstreamError",
    "HEVCNeutralPicture",
    "build_hevc_neutral_picture",
    "encode_hevc_neutral_aot",
    "validate_hevc_neutral_annex_b",
    "hevc_neutral_capability_report",
]
