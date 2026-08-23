"""Bounded lossless 10-bit HEVC Main10 I_PCM profile.

This is a deliberately narrow interoperability milestone for HEIC.  It
emits one IDR picture made from 16x16 I_PCM coding blocks, supports planar
4:2:0 even dimensions, and stores samples as little-endian
unsigned 16-bit values in the public buffer contract.  Only the low ten bits
of every value are significant.  There is no prediction, transform,
quantization, or rate-distortion decision in this profile.

The bitstream/container implementation uses only the standard library and
the local HEVC primitives.  External decoders are used only by verification.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .hevc_aot import (
    HEVC_CHROMA_420,
    HEVCBitReader,
    HEVCBitWriter,
    HEVCProfileError,
    HEVC_NAL_IDR_N_LP,
    HEVC_NAL_PPS,
    HEVC_NAL_SPS,
    HEVC_NAL_VPS,
    HEVCProfileTierLevel,
    build_hvcc,
    build_nal_unit,
    build_pps_rbsp,
    build_vps_rbsp,
    cabac_context_from_init,
    main_profile_tier_level,
    parse_nal_unit,
)
from .hevc_ipcm_aot import _cabac_end_of_slice, _cabac_part_and_pcm_prefix


HEVC_IPCM10_WIDTH = 16
HEVC_IPCM10_HEIGHT = 16
HEVC_IPCM10_BIT_DEPTH = 10
HEVC_IPCM10_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_IPCM10_MIN_DIMENSION = 16
HEVC_IPCM10_MAX_WIDTH = 4096
HEVC_IPCM10_MAX_HEIGHT = 4096
HEVC_IPCM10_BYTES_PER_SAMPLE = 2


class HEVCIPCM10ProfileError(HEVCProfileError):
    """Raised when input is outside the bounded Main10 I_PCM profile."""


class HEVCIPCM10BitstreamError(HEVCIPCM10ProfileError):
    """Raised when a local Main10 I_PCM invariant is violated."""


def _validate_geometry(width: int, height: int) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("HEVC Main10 I_PCM dimensions must be integers")
    if not HEVC_IPCM10_MIN_DIMENSION <= width <= HEVC_IPCM10_MAX_WIDTH:
        raise HEVCIPCM10ProfileError("HEVC Main10 I_PCM width is outside the bounded profile")
    if not HEVC_IPCM10_MIN_DIMENSION <= height <= HEVC_IPCM10_MAX_HEIGHT:
        raise HEVCIPCM10ProfileError("HEVC Main10 I_PCM height is outside the bounded profile")
    if width % 2 or height % 2:
        raise HEVCIPCM10ProfileError(
            "HEVC Main10 I_PCM 4:2:0 dimensions must be even; CTU padding handles 16 alignment"
        )


def _coded_dimension(value: int) -> int:
    return ((value + 15) // 16) * 16


def _conformance_window(width: int, height: int) -> tuple[int, int, int, int, int, int]:
    coded_width = _coded_dimension(width)
    coded_height = _coded_dimension(height)
    return (
        coded_width,
        coded_height,
        0,
        (coded_width - width) // 2,
        0,
        (coded_height - height) // 2,
    )


def hevc_ipcm10_sample_count(width: int = HEVC_IPCM10_WIDTH, height: int = HEVC_IPCM10_HEIGHT) -> int:
    _validate_geometry(width, height)
    return width * height + 2 * (width // 2) * (height // 2)


def hevc_ipcm10_buffer_bytes(width: int = HEVC_IPCM10_WIDTH, height: int = HEVC_IPCM10_HEIGHT) -> int:
    return hevc_ipcm10_sample_count(width, height) * HEVC_IPCM10_BYTES_PER_SAMPLE


def _validate_samples(samples: object, width: int, height: int) -> tuple[bytes, tuple[int, ...]]:
    expected = hevc_ipcm10_buffer_bytes(width, height)
    if samples is None:
        raise TypeError("HEVC Main10 I_PCM samples are required")
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("HEVC Main10 I_PCM samples must be a bytes-like LE u16 buffer") from exc
    if view.ndim != 1 or not view.c_contiguous or view.nbytes != expected:
        raise HEVCIPCM10ProfileError(
            f"the {width}x{height} profile requires exactly {expected} contiguous bytes"
        )
    raw = view.cast("B").tobytes()
    values = tuple(int.from_bytes(raw[index:index + 2], "little") for index in range(0, expected, 2))
    if any(value > 1023 for value in values):
        raise HEVCIPCM10ProfileError("Main10 I_PCM samples must fit in ten bits")
    return raw, values


def _main10_ptl(level_idc: int) -> HEVCProfileTierLevel:
    base = main_profile_tier_level(level_idc)
    # profile_idc=2 is Main 10.  The compatibility flags retain Main/Main10
    # compatibility bits used by the existing constrained VPS builder.
    return HEVCProfileTierLevel(
        profile_space=base.profile_space,
        tier_flag=base.tier_flag,
        profile_idc=2,
        profile_compatibility_flags=0x60000000,
        constraint_indicator_flags=base.constraint_indicator_flags,
        level_idc=base.level_idc,
        max_sub_layers_minus1=base.max_sub_layers_minus1,
    )


def _build_sps_rbsp(width: int, height: int, ptl: HEVCProfileTierLevel) -> bytes:
    coded_width, coded_height, conf_left, conf_right, conf_top, conf_bottom = _conformance_window(width, height)
    writer = HEVCBitWriter()
    writer.write(0, 4)
    writer.write(0, 3)
    writer.flag(1)
    ptl.write(writer)
    writer.ue(0)
    writer.ue(HEVC_CHROMA_420)
    writer.ue(coded_width)
    writer.ue(coded_height)
    has_conformance_window = any((conf_left, conf_right, conf_top, conf_bottom))
    writer.flag(int(has_conformance_window))
    if has_conformance_window:
        writer.ue(conf_left)
        writer.ue(conf_right)
        writer.ue(conf_top)
        writer.ue(conf_bottom)
    writer.ue(2)  # bit_depth_luma_minus8 = 10-bit
    writer.ue(2)  # bit_depth_chroma_minus8 = 10-bit
    writer.ue(4)
    writer.flag(0)
    writer.ue(0)
    writer.ue(0)
    writer.ue(0)
    writer.ue(1)  # 16x16 minimum coding block
    writer.ue(0)
    writer.ue(0)
    writer.ue(0)
    writer.ue(0)
    writer.ue(0)
    writer.flag(0)
    writer.flag(0)
    writer.flag(0)
    writer.flag(1)  # pcm_enabled_flag
    writer.write(9, 4)  # pcm_sample_bit_depth_luma_minus1 = 10
    writer.write(9, 4)  # pcm_sample_bit_depth_chroma_minus1 = 10
    writer.ue(1)
    writer.ue(0)
    writer.flag(1)
    writer.ue(0)
    writer.flag(0)
    writer.flag(0)
    writer.flag(1)
    writer.flag(0)
    writer.flag(0)
    writer.rbsp_trailing_bits()
    return writer.bytes()


def _iter_blocks(values: tuple[int, ...], width: int, height: int):
    luma_size = width * height
    chroma_width = width // 2
    chroma_height = height // 2
    coded_width, coded_height, *_ = _conformance_window(width, height)
    cb_offset = luma_size
    cr_offset = cb_offset + chroma_width * chroma_height
    for block_y in range(0, coded_height, 16):
        for block_x in range(0, coded_width, 16):
            block: list[int] = []
            for row in range(16):
                source_y = min(block_y + row, height - 1)
                for column in range(16):
                    source_x = min(block_x + column, width - 1)
                    block.append(values[source_y * width + source_x])
            chroma_x = block_x // 2
            chroma_y = block_y // 2
            for offset in (cb_offset, cr_offset):
                for row in range(8):
                    source_y = min(chroma_y + row, chroma_height - 1)
                    for column in range(8):
                        source_x = min(chroma_x + column, chroma_width - 1)
                        block.append(values[offset + source_y * chroma_width + source_x])
            yield tuple(block)


def _build_slice_rbsp(values: tuple[int, ...], width: int, height: int) -> bytes:
    writer = HEVCBitWriter()
    writer.flag(1)
    writer.flag(0)
    writer.ue(0)
    writer.ue(2)
    writer.se(0)
    writer.flag(1)
    writer.flag(1)
    while not writer.byte_aligned:
        writer.flag(0)

    context = cabac_context_from_init(26, 184)
    blocks = tuple(_iter_blocks(values, width, height))
    for index, block in enumerate(blocks):
        for value in _cabac_part_and_pcm_prefix(
            context,
            end_of_slice_before=None if index == 0 else 0,
        ):
            writer.write(value, 8)
        writer.flag(1)
        while not writer.byte_aligned:
            writer.flag(0)
        for value in block:
            writer.write(value, 10)
    for value in _cabac_end_of_slice(1):
        writer.write(value, 8)
    writer.rbsp_trailing_bits()
    return writer.bytes()


@dataclass(frozen=True)
class HEVCIPCM10Picture:
    width: int
    height: int
    bit_depth: int
    chroma_format_idc: int
    nals: tuple[bytes, bytes, bytes, bytes]
    hvcc: bytes

    @property
    def annex_b(self) -> bytes:
        return b"".join(b"\x00\x00\x00\x01" + nal for nal in self.nals)


def build_hevc_ipcm10_picture(
    samples: object,
    width: int = HEVC_IPCM10_WIDTH,
    height: int = HEVC_IPCM10_HEIGHT,
) -> HEVCIPCM10Picture:
    _validate_geometry(width, height)
    _raw, values = _validate_samples(samples, width, height)
    ptl = _main10_ptl(153 if max(width, height) > 2048 else 120)
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(HEVC_NAL_SPS, _build_sps_rbsp(width, height, ptl))
    pps = build_nal_unit(HEVC_NAL_PPS, build_pps_rbsp())
    vcl = build_nal_unit(HEVC_NAL_IDR_N_LP, _build_slice_rbsp(values, width, height))
    hvcc = build_hvcc((vps, sps, pps), ptl=ptl, bit_depth=10, chroma_format_idc=HEVC_CHROMA_420)
    picture = HEVCIPCM10Picture(width, height, 10, HEVC_CHROMA_420, (vps, sps, pps, vcl), hvcc)
    validate_hevc_ipcm10_annex_b(picture.annex_b, width=width, height=height)
    return picture


def encode_hevc_ipcm10_aot(samples: object, width: int = HEVC_IPCM10_WIDTH, height: int = HEVC_IPCM10_HEIGHT) -> bytes:
    return build_hevc_ipcm10_picture(samples, width=width, height=height).annex_b


def _sps_info(nal: bytes) -> tuple[int, int, int, int]:
    parsed = parse_nal_unit(nal)
    if parsed.nal_unit_type != HEVC_NAL_SPS:
        raise HEVCIPCM10BitstreamError("Main10 I_PCM SPS has an unexpected NAL type")
    reader = HEVCBitReader(parsed.rbsp)
    reader.read(4)
    if reader.read(3) != 0:
        raise HEVCIPCM10BitstreamError("Main10 validator expects one temporal sub-layer")
    reader.read(1)
    reader.read(8)
    reader.read(32)
    reader.read(48)
    reader.read(8)
    reader.ue()
    chroma = reader.ue(max_value=3)
    coded_width = reader.ue(max_value=HEVC_IPCM10_MAX_WIDTH)
    coded_height = reader.ue(max_value=HEVC_IPCM10_MAX_HEIGHT)
    conformance_window_flag = reader.flag()
    if conformance_window_flag:
        conf_left = reader.ue()
        conf_right = reader.ue()
        conf_top = reader.ue()
        conf_bottom = reader.ue()
        if chroma == HEVC_CHROMA_420:
            width = coded_width - 2 * (conf_left + conf_right)
            height = coded_height - 2 * (conf_top + conf_bottom)
        else:
            raise HEVCIPCM10BitstreamError("Main10 validator supports only 4:2:0 cropping")
    else:
        width, height = coded_width, coded_height
    bit_depth_luma = 8 + reader.ue(max_value=7)
    bit_depth_chroma = 8 + reader.ue(max_value=7)
    return width, height, chroma, bit_depth_luma if bit_depth_luma == bit_depth_chroma else -1


def validate_hevc_ipcm10_annex_b(
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
            raise HEVCIPCM10BitstreamError("Main10 Annex-B stream contains an empty NAL")
        nals.append(nal)
        if next_marker < 0:
            break
        cursor = next_marker
    if len(nals) != 4:
        raise HEVCIPCM10BitstreamError("Main10 stream requires VPS, SPS, PPS, and one IDR NAL")
    parsed_types = tuple(parse_nal_unit(nal).nal_unit_type for nal in nals)
    expected = (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS, HEVC_NAL_IDR_N_LP)
    if parsed_types != expected:
        raise HEVCIPCM10BitstreamError(f"unexpected Main10 NAL order: {parsed_types!r}")
    parsed_width, parsed_height, chroma, bit_depth = _sps_info(nals[1])
    if width is None or height is None:
        width, height = parsed_width, parsed_height
    _validate_geometry(width, height)
    if (parsed_width, parsed_height, chroma, bit_depth) != (width, height, HEVC_CHROMA_420, 10):
        raise HEVCIPCM10BitstreamError("Main10 SPS does not match the bounded 10-bit 4:2:0 profile")
    return {
        "nal_types": parsed_types,
        "nal_count": len(nals),
        "width": width,
        "height": height,
        "bit_depth": 10,
        "chroma_format_idc": HEVC_CHROMA_420,
        "lossless_ipcm": True,
        "bytes": len(raw),
    }


def hevc_ipcm10_capability_report() -> Mapping[str, object]:
    return {
        "parameter_sets": True,
        "pixel_to_slice_encoder": True,
        "lossless_ipcm": True,
        "general_encoder": False,
        "supported_profile": "even dimensions up to 4096x4096, Main10, 10-bit 4:2:0, padded 16x16 IDR I_PCM slice with SPS conformance window",
        "variable_dimensions": True,
        "variable_subsampling": False,
        "runtime_codec_dependencies": (),
        "external_decoder_validated_payload": True,
        "gpu_full_codec": False,
        "fail_closed": True,
    }


__all__ = [
    "HEVC_IPCM10_WIDTH",
    "HEVC_IPCM10_HEIGHT",
    "HEVC_IPCM10_BIT_DEPTH",
    "HEVC_IPCM10_CHROMA_FORMAT_IDC",
    "HEVC_IPCM10_MIN_DIMENSION",
    "HEVC_IPCM10_MAX_WIDTH",
    "HEVC_IPCM10_MAX_HEIGHT",
    "HEVCIPCM10ProfileError",
    "HEVCIPCM10BitstreamError",
    "HEVCIPCM10Picture",
    "hevc_ipcm10_sample_count",
    "hevc_ipcm10_buffer_bytes",
    "build_hevc_ipcm10_picture",
    "encode_hevc_ipcm10_aot",
    "validate_hevc_ipcm10_annex_b",
    "hevc_ipcm10_capability_report",
]
