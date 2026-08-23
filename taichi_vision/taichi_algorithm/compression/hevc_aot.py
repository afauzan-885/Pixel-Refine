"""Small, dependency-free HEVC building blocks for the native HEIF path.

This module intentionally stops at the boundary where a pixel encoder would
have to emit a complete ``slice_segment_layer_rbsp``.  It provides the pieces
that are safe to share with that future encoder:

* strict bit-level RBSP readers and writers;
* HEVC NAL-unit headers and emulation-prevention handling;
* a constrained Main-profile VPS/SPS/PPS set for one layer, one temporal
  sub-layer, 8-bit 4:2:0 pictures;
* an ISO/IEC 14496-15 ``hvcC`` configuration record;
* the HEVC CABAC context transitions and arithmetic-register primitive.

``encode_hevc_intra_aot`` is deliberately fail-closed.  A parameter-set
sequence without a valid coded slice is not an image, and returning one as if
it were a finished HEIC payload would produce files that fail in decoders.
The function therefore raises :class:`HEVCEncoderUnavailable` until the
intra prediction, transform, slice syntax, and CABAC traversal are all wired
and externally decoded.

There are no runtime codec dependencies in this file.  The implementation is
host-side bitstream plumbing; it does not claim that the current module is a
complete HEVC encoder or that parameter sets alone are a decodable image.
"""
from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Mapping, Sequence


HEVC_NAL_TRAIL_R = 1
HEVC_NAL_IDR_W_RADL = 19
HEVC_NAL_IDR_N_LP = 20
HEVC_NAL_CRA_NUT = 21
HEVC_NAL_VPS = 32
HEVC_NAL_SPS = 33
HEVC_NAL_PPS = 34

HEVC_PROFILE_MAIN = 1
HEVC_CHROMA_420 = 1
HEVC_CHROMA_422 = 2
HEVC_CHROMA_444 = 3


class HEVCError(ValueError):
    """Base class for strict HEVC validation failures."""


class HEVCBitstreamError(HEVCError):
    """Raised when an RBSP, NAL unit, or configuration record is malformed."""


class HEVCProfileError(HEVCError):
    """Raised when an input is outside the deliberately small profile."""


class HEVCEncoderUnavailable(HEVCError):
    """The complete pixel-to-slice encoder is not enabled yet."""


class HEVCBitWriter:
    """Bounded MSB-first bit writer used by HEVC syntax structures."""

    __slots__ = ("_data", "_bits")

    def __init__(self) -> None:
        self._data = bytearray()
        self._bits = 0

    @property
    def bit_count(self) -> int:
        return self._bits

    @property
    def byte_aligned(self) -> bool:
        return (self._bits & 7) == 0

    def write(self, value: int, width: int) -> None:
        if not isinstance(value, int) or not isinstance(width, int):
            raise TypeError("HEVC bit fields require integer values")
        if width < 0 or width > 64:
            raise ValueError("HEVC bit field width must be between 0 and 64")
        if width == 0:
            if value != 0:
                raise ValueError("a zero-width HEVC field must have value zero")
            return
        if value < 0 or value >= (1 << width):
            raise ValueError(f"value {value} does not fit in {width} bits")
        for shift in range(width - 1, -1, -1):
            if (self._bits & 7) == 0:
                self._data.append(0)
            if (value >> shift) & 1:
                self._data[-1] |= 1 << (7 - (self._bits & 7))
            self._bits += 1

    def flag(self, value: bool | int) -> None:
        if value not in (False, True, 0, 1):
            raise ValueError("HEVC flags must be zero or one")
        self.write(int(value), 1)

    def ue(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError("unsigned Exp-Golomb values must be non-negative integers")
        code_num = value + 1
        width = code_num.bit_length()
        self.write(0, width - 1)
        self.write(code_num, width)

    def se(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("signed Exp-Golomb values require integers")
        code_num = (value << 1) - 1 if value > 0 else -(value << 1)
        self.ue(code_num)

    def rbsp_trailing_bits(self) -> None:
        """Write ``rbsp_stop_one_bit`` followed by zero alignment bits."""
        self.flag(1)
        while not self.byte_aligned:
            self.flag(0)

    def byte_alignment(self) -> None:
        """Write HEVC ``alignment_bit_equal_to_one`` and zero bits."""
        self.rbsp_trailing_bits()

    def bytes(self) -> bytes:
        if not self.byte_aligned:
            raise HEVCBitstreamError("RBSP must be byte aligned before serialization")
        return bytes(self._data)


class HEVCBitReader:
    """Strict MSB-first reader with no implicit zero padding."""

    __slots__ = ("_data", "_bits")

    def __init__(self, data: bytes | bytearray | memoryview) -> None:
        self._data = bytes(data)
        self._bits = 0

    @property
    def bit_position(self) -> int:
        return self._bits

    @property
    def bits_remaining(self) -> int:
        return len(self._data) * 8 - self._bits

    @property
    def byte_aligned(self) -> bool:
        return (self._bits & 7) == 0

    def peek(self, width: int) -> int:
        position = self._bits
        value = self.read(width)
        self._bits = position
        return value

    def read(self, width: int) -> int:
        if not isinstance(width, int) or width < 0 or width > 64:
            raise ValueError("HEVC read width must be between 0 and 64")
        if width > self.bits_remaining:
            raise HEVCBitstreamError("truncated HEVC bit field")
        value = 0
        for _ in range(width):
            byte = self._data[self._bits >> 3]
            value = (value << 1) | ((byte >> (7 - (self._bits & 7))) & 1)
            self._bits += 1
        return value

    def flag(self) -> int:
        return self.read(1)

    def ue(self, *, max_value: int = (1 << 31) - 1) -> int:
        zeros = 0
        while True:
            if self.bits_remaining <= 0:
                raise HEVCBitstreamError("truncated unsigned Exp-Golomb value")
            if self.read(1):
                break
            zeros += 1
            if zeros > 31:
                raise HEVCBitstreamError("unsigned Exp-Golomb value is unreasonably large")
        suffix = self.read(zeros) if zeros else 0
        value = ((1 << zeros) - 1) + suffix
        if value > max_value:
            raise HEVCBitstreamError("unsigned Exp-Golomb value exceeds the configured bound")
        return value

    def se(self, *, max_abs: int = (1 << 30)) -> int:
        code_num = self.ue(max_value=(max_abs << 1))
        return (code_num + 1) // 2 if code_num & 1 else -(code_num // 2)

    def is_rbsp_trailing_bits(self) -> bool:
        if self.bits_remaining < 1 or self.peek(1) != 1:
            return False
        position = self._bits
        self.read(1)
        result = all(self.read(1) == 0 for _ in range(self.bits_remaining))
        self._bits = position
        return result

    def rbsp_trailing_bits(self) -> None:
        if self.bits_remaining < 1 or self.read(1) != 1:
            raise HEVCBitstreamError("missing rbsp_stop_one_bit")
        while self.bits_remaining:
            if self.read(1) != 0:
                raise HEVCBitstreamError("non-zero bits follow rbsp_stop_one_bit")


def rbsp_to_ebsp(rbsp: bytes | bytearray | memoryview, *, allow_final_zero: bool = False) -> bytes:
    """Apply HEVC emulation-prevention insertion to an already-byte-aligned RBSP."""
    source = bytes(rbsp)
    if not source:
        raise HEVCBitstreamError("an HEVC RBSP must not be empty")
    output = bytearray()
    zero_count = 0
    for value in source:
        if zero_count >= 2 and value <= 3:
            output.append(3)
            zero_count = 0
        output.append(value)
        if value == 0:
            zero_count += 1
        else:
            zero_count = 0
    if output and output[-1] == 0:
        if not allow_final_zero:
            raise HEVCBitstreamError(
                "RBSP ends in zero; cabac_zero_word handling is not enabled for this primitive"
            )
        if len(output) < 2 or output[-2] != 0:
            raise HEVCBitstreamError(
                "allow_final_zero requires a complete two-byte cabac_zero_word"
            )
        output.append(3)
    return bytes(output)


def ebsp_to_rbsp(ebsp: bytes | bytearray | memoryview) -> bytes:
    """Remove only valid HEVC emulation-prevention bytes, rejecting truncation."""
    source = bytes(ebsp)
    output = bytearray()
    zero_count = 0
    index = 0
    while index < len(source):
        value = source[index]
        if value == 3 and zero_count >= 2 and (
            index + 1 == len(source) or source[index + 1] <= 3
        ):
            index += 1
            zero_count = 0
            continue
        output.append(value)
        if value == 0:
            zero_count += 1
        else:
            zero_count = 0
        index += 1
    if not output:
        raise HEVCBitstreamError("an HEVC NAL payload has no RBSP bytes")
    return bytes(output)


@dataclass(frozen=True)
class HEVCNALUnit:
    """Parsed HEVC NAL unit without an Annex-B start-code prefix."""

    nal_unit_type: int
    nuh_layer_id: int
    nuh_temporal_id_plus1: int
    rbsp: bytes
    ebsp: bytes

    @property
    def temporal_id(self) -> int:
        return self.nuh_temporal_id_plus1 - 1

    @property
    def header(self) -> bytes:
        value = (
            (self.nal_unit_type << 9)
            | (self.nuh_layer_id << 3)
            | self.nuh_temporal_id_plus1
        )
        return struct.pack(">H", value)

    @property
    def raw(self) -> bytes:
        return self.header + self.ebsp

    @property
    def annex_b(self) -> bytes:
        return b"\x00\x00\x00\x01" + self.raw


def build_nal_unit(
    nal_unit_type: int,
    rbsp: bytes | bytearray | memoryview,
    *,
    nuh_layer_id: int = 0,
    temporal_id: int = 0,
    annex_b: bool = False,
) -> bytes:
    """Build one strict HEVC NAL unit from a byte-aligned RBSP."""
    if not isinstance(nal_unit_type, int) or not 0 <= nal_unit_type <= 63:
        raise ValueError("HEVC NAL unit type must fit in six bits")
    if not isinstance(nuh_layer_id, int) or not 0 <= nuh_layer_id <= 63:
        raise ValueError("HEVC nuh_layer_id must fit in six bits")
    if not isinstance(temporal_id, int) or not 0 <= temporal_id <= 6:
        raise ValueError("HEVC temporal_id must be between 0 and 6")
    ebsp = rbsp_to_ebsp(bytes(rbsp))
    header_value = (nal_unit_type << 9) | (nuh_layer_id << 3) | (temporal_id + 1)
    raw = struct.pack(">H", header_value) + ebsp
    return (b"\x00\x00\x00\x01" if annex_b else b"") + raw


def parse_nal_unit(data: bytes | bytearray | memoryview) -> HEVCNALUnit:
    """Parse one Annex-B or length-delimited HEVC NAL unit strictly."""
    raw = bytes(data)
    if raw.startswith(b"\x00\x00\x00\x01"):
        raw = raw[4:]
    elif raw.startswith(b"\x00\x00\x01"):
        raw = raw[3:]
    if len(raw) < 3:
        raise HEVCBitstreamError("HEVC NAL unit is shorter than its header and payload")
    header = struct.unpack(">H", raw[:2])[0]
    forbidden_zero_bit = (header >> 15) & 1
    nal_unit_type = (header >> 9) & 0x3F
    nuh_layer_id = (header >> 3) & 0x3F
    temporal_id_plus1 = header & 7
    if forbidden_zero_bit:
        raise HEVCBitstreamError("HEVC forbidden_zero_bit is set")
    if temporal_id_plus1 == 0:
        raise HEVCBitstreamError("HEVC nuh_temporal_id_plus1 must not be zero")
    ebsp = raw[2:]
    if raw[-1] == 0:
        raise HEVCBitstreamError("the last byte of an HEVC NAL unit must not be zero")
    for index in range(len(ebsp) - 2):
        if ebsp[index] == 0 and ebsp[index + 1] == 0 and ebsp[index + 2] <= 2:
            raise HEVCBitstreamError("HEVC NAL payload contains an unescaped start-code prefix")
    rbsp = ebsp_to_rbsp(ebsp)
    return HEVCNALUnit(nal_unit_type, nuh_layer_id, temporal_id_plus1, rbsp, ebsp)


@dataclass(frozen=True)
class HEVCProfileTierLevel:
    """General PTL fields for the one-sublayer profile used here."""

    profile_space: int = 0
    tier_flag: int = 0
    profile_idc: int = HEVC_PROFILE_MAIN
    profile_compatibility_flags: int = 0x60000000
    constraint_indicator_flags: int = 0xB00000000000
    level_idc: int = 120
    max_sub_layers_minus1: int = 0

    def validate(self) -> None:
        if not 0 <= self.profile_space <= 3:
            raise HEVCProfileError("profile_space must fit in two bits")
        if self.tier_flag not in (0, 1):
            raise HEVCProfileError("tier_flag must be zero or one")
        if not 0 <= self.profile_idc <= 31:
            raise HEVCProfileError("profile_idc must fit in five bits")
        if not 0 <= self.profile_compatibility_flags <= 0xFFFFFFFF:
            raise HEVCProfileError("profile compatibility flags must fit in 32 bits")
        if not 0 <= self.constraint_indicator_flags <= 0xFFFFFFFFFFFF:
            raise HEVCProfileError("constraint indicator flags must fit in 48 bits")
        if not 0 <= self.level_idc <= 255:
            raise HEVCProfileError("level_idc must fit in eight bits")
        if self.max_sub_layers_minus1 != 0:
            raise HEVCProfileError("the current primitive supports one temporal sub-layer only")

    def write(self, writer: HEVCBitWriter, *, profile_present: bool = True) -> None:
        self.validate()
        if profile_present:
            writer.write((self.profile_space << 6) | (self.tier_flag << 5) | self.profile_idc, 8)
            writer.write(self.profile_compatibility_flags, 32)
            writer.write(self.constraint_indicator_flags, 48)
        writer.write(self.level_idc, 8)


def main_profile_tier_level(level_idc: int = 120) -> HEVCProfileTierLevel:
    """Return the constrained 8-bit Main-profile PTL used by this module."""
    return HEVCProfileTierLevel(level_idc=level_idc)


def _validate_picture_geometry(width: int, height: int) -> None:
    if not isinstance(width, int) or not isinstance(height, int):
        raise TypeError("HEVC picture dimensions must be integers")
    if not 1 <= width <= 65535 or not 1 <= height <= 65535:
        raise HEVCProfileError("the small HEVC profile accepts dimensions from 1 to 65535")


def build_vps_rbsp(*, ptl: HEVCProfileTierLevel | None = None) -> bytes:
    """Build a one-layer, one-sublayer VPS RBSP."""
    ptl = ptl or main_profile_tier_level()
    if ptl.max_sub_layers_minus1 != 0:
        raise HEVCProfileError("the VPS primitive supports one temporal sub-layer only")
    writer = HEVCBitWriter()
    writer.write(0, 4)  # vps_video_parameter_set_id
    writer.write(3, 2)  # vps_reserved_three_2bits
    writer.write(0, 6)  # vps_max_layers_minus1
    writer.write(0, 3)  # vps_max_sub_layers_minus1
    writer.flag(1)  # vps_temporal_id_nesting_flag
    writer.write(0xFFFF, 16)
    ptl.write(writer)
    writer.flag(0)  # vps_sub_layer_ordering_info_present_flag
    writer.ue(0)  # vps_max_dec_pic_buffering_minus1
    writer.ue(0)  # vps_max_num_reorder_pics
    writer.ue(0)  # vps_max_latency_increase_plus1
    writer.write(0, 6)  # vps_max_layer_id
    writer.ue(0)  # vps_num_layer_sets_minus1
    writer.flag(0)  # vps_timing_info_present_flag
    writer.flag(0)  # vps_extension_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


def build_sps_rbsp(
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    chroma_format_idc: int = HEVC_CHROMA_420,
    ptl: HEVCProfileTierLevel | None = None,
) -> bytes:
    """Build the constrained Main 4:2:0 SPS used by the parameter-set API."""
    _validate_picture_geometry(width, height)
    if bit_depth != 8:
        raise HEVCProfileError("the initial HEVC profile is 8-bit only")
    if chroma_format_idc != HEVC_CHROMA_420:
        raise HEVCProfileError("the initial HEVC profile is 4:2:0 only")
    ptl = ptl or main_profile_tier_level()
    writer = HEVCBitWriter()
    writer.write(0, 4)  # sps_video_parameter_set_id
    writer.write(0, 3)  # sps_max_sub_layers_minus1
    writer.flag(1)  # sps_temporal_id_nesting_flag
    ptl.write(writer)
    writer.ue(0)  # sps_seq_parameter_set_id
    writer.ue(chroma_format_idc)
    writer.ue(width)
    writer.ue(height)
    writer.flag(0)  # conformance_window_flag
    writer.ue(bit_depth - 8)
    writer.ue(bit_depth - 8)
    writer.ue(4)  # log2_max_pic_order_cnt_lsb_minus4; 8-bit POC
    writer.flag(0)  # sps_sub_layer_ordering_info_present_flag
    writer.ue(0)  # sps_max_dec_pic_buffering_minus1
    writer.ue(0)  # sps_max_num_reorder_pics
    writer.ue(0)  # sps_max_latency_increase_plus1
    writer.ue(0)  # log2_min_luma_coding_block_size_minus3 = 8x8
    writer.ue(3)  # log2_diff_max_min_luma_coding_block_size = 64x64 CTU
    writer.ue(0)  # log2_min_luma_transform_block_size_minus2 = 4x4
    writer.ue(3)  # log2_diff_max_min_luma_transform_block_size = 32x32
    writer.ue(1)  # max_transform_hierarchy_depth_inter
    writer.ue(1)  # max_transform_hierarchy_depth_intra
    writer.flag(0)  # scaling_list_enabled_flag
    writer.flag(0)  # amp_enabled_flag
    writer.flag(1)  # sample_adaptive_offset_enabled_flag
    writer.flag(0)  # pcm_enabled_flag
    writer.ue(0)  # num_short_term_ref_pic_sets
    writer.flag(0)  # long_term_ref_pics_present_flag
    writer.flag(0)  # sps_temporal_mvp_enabled_flag
    writer.flag(1)  # strong_intra_smoothing_enabled_flag
    writer.flag(0)  # vui_parameters_present_flag
    writer.flag(0)  # sps_extension_present_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


def build_pps_rbsp() -> bytes:
    """Build a minimal PPS matching the single SPS/PPS IDs above."""
    writer = HEVCBitWriter()
    writer.ue(0)  # pps_pic_parameter_set_id
    writer.ue(0)  # pps_seq_parameter_set_id
    writer.flag(0)  # dependent_slice_segments_enabled_flag
    writer.flag(0)  # output_flag_present_flag
    writer.write(0, 3)  # num_extra_slice_header_bits
    writer.flag(0)  # sign_data_hiding_enabled_flag
    writer.flag(0)  # cabac_init_present_flag
    writer.ue(0)  # num_ref_idx_l0_default_active_minus1
    writer.ue(0)  # num_ref_idx_l1_default_active_minus1
    writer.se(0)  # init_qp_minus26
    writer.flag(0)  # constrained_intra_pred_flag
    writer.flag(0)  # transform_skip_enabled_flag
    writer.flag(0)  # cu_qp_delta_enabled_flag
    writer.se(0)  # pps_cb_qp_offset
    writer.se(0)  # pps_cr_qp_offset
    writer.flag(0)  # pps_slice_chroma_qp_offsets_present_flag
    writer.flag(0)  # weighted_pred_flag
    writer.flag(0)  # weighted_bipred_flag
    writer.flag(0)  # transquant_bypass_enabled_flag
    writer.flag(0)  # tiles_enabled_flag
    writer.flag(0)  # entropy_coding_sync_enabled_flag
    writer.flag(1)  # pps_loop_filter_across_slices_enabled_flag
    writer.flag(0)  # deblocking_filter_control_present_flag
    writer.flag(0)  # pps_scaling_list_data_present_flag
    writer.flag(0)  # lists_modification_present_flag
    writer.ue(0)  # log2_parallel_merge_level_minus2 = 2
    writer.flag(0)  # slice_segment_header_extension_present_flag
    writer.flag(0)  # pps_extension_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


@dataclass(frozen=True)
class HEVCParameterSets:
    """A validated parameter-set bundle suitable for HEIF ``hvcC`` packaging."""

    width: int
    height: int
    bit_depth: int
    chroma_format_idc: int
    ptl: HEVCProfileTierLevel
    vps: bytes
    sps: bytes
    pps: bytes
    hvcc: bytes

    @property
    def annex_b(self) -> bytes:
        return b"\x00\x00\x00\x01" + self.vps + b"\x00\x00\x00\x01" + self.sps + b"\x00\x00\x00\x01" + self.pps

    @property
    def nals(self) -> tuple[bytes, bytes, bytes]:
        return self.vps, self.sps, self.pps


def build_hvcc(
    parameter_sets: HEVCParameterSets | Sequence[bytes],
    *,
    ptl: HEVCProfileTierLevel | None = None,
    chroma_format_idc: int = HEVC_CHROMA_420,
    bit_depth: int = 8,
    array_completeness: bool = True,
) -> bytes:
    """Build an HEVCDecoderConfigurationRecord from VPS/SPS/PPS NALs.

    The NALs must include their two-byte headers and must not include Annex-B
    start codes.  A configuration record does not contain a coded picture.
    """
    if isinstance(parameter_sets, HEVCParameterSets):
        nals = parameter_sets.nals
        ptl = parameter_sets.ptl if ptl is None else ptl
        chroma_format_idc = parameter_sets.chroma_format_idc
        bit_depth = parameter_sets.bit_depth
    else:
        nals = tuple(bytes(item) for item in parameter_sets)
    if len(nals) != 3:
        raise HEVCBitstreamError("the small HEVC hvcC builder requires exactly VPS, SPS, and PPS")
    parsed = tuple(parse_nal_unit(item) for item in nals)
    if tuple(item.nal_unit_type for item in parsed) != (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS):
        raise HEVCBitstreamError("hvcC parameter sets must be ordered VPS, SPS, PPS")
    if ptl is None:
        ptl = main_profile_tier_level()
    ptl.validate()
    if chroma_format_idc not in (0, 1, 2, 3):
        raise HEVCProfileError("chroma_format_idc must fit in two bits")
    if bit_depth < 8 or bit_depth > 15:
        raise HEVCProfileError("HEVC hvcC bit depths must be between 8 and 15")
    arrays = bytearray()
    for parsed_nal in parsed:
        raw = parsed_nal.raw
        if len(raw) > 0xFFFF:
            raise HEVCBitstreamError("an hvcC NAL unit exceeds the 16-bit length field")
        array_header = (0x80 if array_completeness else 0) | parsed_nal.nal_unit_type
        arrays.extend(bytes((array_header, 0, 1)))
        arrays.extend(struct.pack(">H", len(raw)))
        arrays.extend(raw)
    record = bytearray()
    record.append(1)
    record.append((ptl.profile_space << 6) | (ptl.tier_flag << 5) | ptl.profile_idc)
    record.extend(struct.pack(">I", ptl.profile_compatibility_flags))
    record.extend(ptl.constraint_indicator_flags.to_bytes(6, "big"))
    record.append(ptl.level_idc)
    record.extend(struct.pack(">H", 0xF000))  # reserved=1111, min_spatial_segmentation_idc=0
    record.append(0xFC)  # reserved=111111, parallelismType=0
    record.append(0xFC | chroma_format_idc)
    record.append(0xF8 | (bit_depth - 8))
    record.append(0xF8 | (bit_depth - 8))
    record.extend(struct.pack(">H", 0))  # avgFrameRate
    record.append((0 << 6) | (1 << 3) | (1 << 2) | 3)
    record.append(3)
    record.extend(arrays)
    return bytes(record)


def build_hevc_parameter_sets(
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    chroma_format_idc: int = HEVC_CHROMA_420,
    level_idc: int = 120,
) -> HEVCParameterSets:
    """Build and internally round-trip a constrained VPS/SPS/PPS bundle."""
    _validate_picture_geometry(width, height)
    if bit_depth != 8:
        raise HEVCProfileError("only the 8-bit Main 4:2:0 profile is enabled")
    if chroma_format_idc != HEVC_CHROMA_420:
        raise HEVCProfileError("only the Main 4:2:0 profile is enabled")
    ptl = main_profile_tier_level(level_idc)
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(HEVC_NAL_SPS, build_sps_rbsp(width, height, bit_depth=bit_depth, chroma_format_idc=chroma_format_idc, ptl=ptl))
    pps = build_nal_unit(HEVC_NAL_PPS, build_pps_rbsp())
    bundle = HEVCParameterSets(width, height, bit_depth, chroma_format_idc, ptl, vps, sps, pps, b"")
    hvcc = build_hvcc(bundle)
    result = HEVCParameterSets(width, height, bit_depth, chroma_format_idc, ptl, vps, sps, pps, hvcc)
    parsed_hvcc = parse_hvcc(hvcc)
    if parsed_hvcc["nal_types"] != (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS):
        raise HEVCBitstreamError("internal hvcC round-trip did not preserve parameter-set order")
    return result


def parse_hvcc(data: bytes | bytearray | memoryview) -> dict[str, object]:
    """Strictly parse the subset of HEVCDecoderConfigurationRecord we emit."""
    raw = bytes(data)
    if len(raw) < 23:
        raise HEVCBitstreamError("truncated hvcC configuration record")
    if raw[0] != 1:
        raise HEVCBitstreamError("unsupported hvcC configurationVersion")
    profile_byte = raw[1]
    profile_space = profile_byte >> 6
    tier_flag = (profile_byte >> 5) & 1
    profile_idc = profile_byte & 0x1F
    compatibility = struct.unpack(">I", raw[2:6])[0]
    constraints = int.from_bytes(raw[6:12], "big")
    level_idc = raw[12]
    if raw[13] & 0xF0 != 0xF0:
        raise HEVCBitstreamError("hvcC min_spatial_segmentation_idc reserved bits are invalid")
    min_spatial_segmentation_idc = struct.unpack(">H", raw[13:15])[0] & 0x0FFF
    if raw[15] & 0xFC != 0xFC or raw[16] & 0xFC != 0xFC:
        raise HEVCBitstreamError("hvcC reserved bits are invalid")
    parallelism_type = raw[15] & 3
    chroma_format_idc = raw[16] & 3
    if raw[17] & 0xF8 != 0xF8 or raw[18] & 0xF8 != 0xF8:
        raise HEVCBitstreamError("hvcC bit-depth reserved bits are invalid")
    bit_depth_luma = 8 + (raw[17] & 7)
    bit_depth_chroma = 8 + (raw[18] & 7)
    avg_frame_rate = struct.unpack(">H", raw[19:21])[0]
    timing = raw[21]
    constant_frame_rate = timing >> 6
    num_temporal_layers = (timing >> 3) & 7
    temporal_id_nested = (timing >> 2) & 1
    length_size_minus_one = timing & 3
    array_count = raw[22]
    cursor = 23
    arrays: list[tuple[int, bool, tuple[bytes, ...]]] = []
    for _ in range(array_count):
        if cursor + 3 > len(raw):
            raise HEVCBitstreamError("truncated hvcC NAL-array header")
        array_header = raw[cursor]
        cursor += 1
        complete = bool(array_header & 0x80)
        if array_header & 0x40:
            raise HEVCBitstreamError("hvcC NAL-array reserved bit is set")
        nal_type = array_header & 0x3F
        count = struct.unpack(">H", raw[cursor:cursor + 2])[0]
        cursor += 2
        nals: list[bytes] = []
        for _ in range(count):
            if cursor + 2 > len(raw):
                raise HEVCBitstreamError("truncated hvcC NAL length")
            size = struct.unpack(">H", raw[cursor:cursor + 2])[0]
            cursor += 2
            if size < 3 or cursor + size > len(raw):
                raise HEVCBitstreamError("invalid hvcC NAL length")
            nal = raw[cursor:cursor + size]
            cursor += size
            parsed = parse_nal_unit(nal)
            if parsed.nal_unit_type != nal_type:
                raise HEVCBitstreamError("hvcC array type disagrees with its NAL header")
            nals.append(nal)
        arrays.append((nal_type, complete, tuple(nals)))
    if cursor != len(raw):
        raise HEVCBitstreamError("trailing bytes follow the hvcC arrays")
    all_nals = tuple(nal for _type, _complete, nals in arrays for nal in nals)
    return {
        "profile_space": profile_space,
        "tier_flag": tier_flag,
        "profile_idc": profile_idc,
        "profile_compatibility_flags": compatibility,
        "constraint_indicator_flags": constraints,
        "level_idc": level_idc,
        "min_spatial_segmentation_idc": min_spatial_segmentation_idc,
        "parallelism_type": parallelism_type,
        "chroma_format_idc": chroma_format_idc,
        "bit_depth_luma": bit_depth_luma,
        "bit_depth_chroma": bit_depth_chroma,
        "avg_frame_rate": avg_frame_rate,
        "constant_frame_rate": constant_frame_rate,
        "num_temporal_layers": num_temporal_layers,
        "temporal_id_nested": temporal_id_nested,
        "length_size_minus_one": length_size_minus_one,
        "arrays": tuple(arrays),
        "nal_types": tuple(parse_nal_unit(nal).nal_unit_type for nal in all_nals),
    }


# The HEVC M-coder tables are fixed by H.265 clause 9.3.  Keeping them local
# makes this module self-contained and avoids pulling a codec implementation
# into the runtime.
_RANGE_TAB_LPS: tuple[tuple[int, int, int, int], ...] = (
    (128, 176, 208, 240), (128, 167, 197, 227), (128, 158, 187, 216), (123, 150, 178, 205),
    (116, 142, 169, 195), (111, 135, 160, 185), (105, 128, 152, 175), (100, 122, 144, 166),
    (95, 116, 137, 158), (90, 110, 130, 150), (85, 104, 123, 142), (81, 99, 117, 135),
    (77, 94, 111, 128), (73, 89, 105, 122), (69, 85, 100, 116), (66, 80, 95, 110),
    (62, 76, 90, 104), (59, 72, 86, 99), (56, 69, 81, 94), (53, 65, 77, 89),
    (51, 62, 73, 85), (48, 59, 69, 80), (46, 56, 66, 76), (43, 53, 63, 72),
    (41, 50, 59, 69), (39, 48, 56, 65), (37, 45, 54, 62), (35, 43, 51, 59),
    (33, 41, 48, 56), (32, 39, 46, 53), (30, 37, 43, 50), (29, 35, 41, 48),
    (27, 33, 39, 45), (26, 31, 37, 43), (24, 30, 35, 41), (23, 28, 33, 39),
    (22, 27, 32, 37), (21, 26, 30, 35), (20, 24, 29, 33), (19, 23, 27, 31),
    (18, 22, 26, 30), (17, 21, 25, 28), (16, 20, 23, 27), (15, 19, 22, 25),
    (14, 18, 21, 24), (14, 17, 20, 23), (13, 16, 19, 22), (12, 15, 18, 21),
    (12, 14, 17, 20), (11, 14, 16, 19), (11, 13, 15, 18), (10, 12, 15, 17),
    (10, 12, 14, 16), (9, 11, 13, 15), (9, 11, 12, 14), (8, 10, 12, 14),
    (8, 9, 11, 13), (7, 9, 11, 12), (7, 9, 10, 12), (7, 8, 10, 11),
    (6, 8, 9, 11), (6, 7, 9, 10), (6, 7, 8, 9), (2, 2, 2, 2),
)
_TRANS_IDX_MPS: tuple[int, ...] = (
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
    17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32,
    33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
    49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 62, 63,
)
_TRANS_IDX_LPS: tuple[int, ...] = (
    0, 0, 1, 2, 2, 4, 4, 5, 6, 7, 8, 9, 9, 11, 11, 12,
    13, 13, 15, 15, 16, 16, 18, 18, 19, 19, 21, 21, 22, 22, 23, 24,
    24, 25, 26, 26, 27, 27, 28, 29, 29, 30, 30, 30, 31, 32, 32, 33,
    33, 33, 34, 34, 35, 35, 35, 36, 36, 36, 37, 37, 37, 38, 38, 63,
)


@dataclass
class HEVCCabacContext:
    """HEVC context state: ``pStateIdx`` plus the most-probable symbol."""

    state: int
    mps: int

    def __post_init__(self) -> None:
        if not 0 <= self.state <= 63:
            raise HEVCBitstreamError("CABAC pStateIdx must be between 0 and 63")
        if self.mps not in (0, 1):
            raise HEVCBitstreamError("CABAC MPS must be zero or one")

    def copy(self) -> "HEVCCabacContext":
        return HEVCCabacContext(self.state, self.mps)


def cabac_context_from_init(qp: int, init_value: int) -> HEVCCabacContext:
    """Apply H.265 context initialization to one 8-bit ``initValue``.

    ``initValue`` is not the final ``preCtxState``.  Its high and low nibbles
    first select the normative slope/offset pair (the HM and FFmpeg decoder
    implementations use this form), after which the result is converted to
    ``pStateIdx`` and ``valMps``.  Keeping that distinction explicit matters
    for the HEVC I_PCM slice path and avoids silently emitting a CABAC stream
    with the wrong context probability.
    """
    if not 0 <= qp <= 51:
        raise HEVCBitstreamError("CABAC QP must be between 0 and 51")
    if not 0 <= init_value <= 255:
        raise HEVCBitstreamError("CABAC init_value must fit in eight bits")
    slope = (init_value >> 4) * 5 - 45
    offset = ((init_value & 15) << 3) - 16
    pre_ctx_state = max(1, min(126, ((slope * qp) >> 4) + offset))
    if pre_ctx_state <= 63:
        return HEVCCabacContext(63 - pre_ctx_state, 0)
    return HEVCCabacContext(pre_ctx_state - 64, 1)


def cabac_lps_range(state: int, current_range: int) -> int:
    """Return ``rangeLPS`` for a normalized HEVC CABAC range."""
    if not 0 <= state <= 63:
        raise HEVCBitstreamError("CABAC state must be between 0 and 63")
    if not 256 <= current_range <= 511:
        raise HEVCBitstreamError("CABAC range must be normalized to 256..511")
    return _RANGE_TAB_LPS[state][(current_range >> 6) & 3]


def cabac_update_context(context: HEVCCabacContext, bin_value: int) -> HEVCCabacContext:
    """Return the exact next context state after one coded bin."""
    if bin_value not in (0, 1):
        raise HEVCBitstreamError("CABAC bins must be zero or one")
    result = context.copy()
    if bin_value == context.mps:
        result.state = _TRANS_IDX_MPS[context.state]
    else:
        if context.state == 0:
            result.mps ^= 1
        result.state = _TRANS_IDX_LPS[context.state]
    return result


class HEVCCabacEncoder:
    """The HEVC M-coder register primitive.

    This class intentionally exposes arithmetic coding only.  A caller still
    has to provide the normative slice syntax, context-index derivation,
    CABAC termination, and ``rbsp_slice_segment_trailing_bits`` before its
    output can be used as an HEVC picture.  ``flush`` follows the byte-queue
    convention used by the H.26x M-coder and returns only the arithmetic
    payload bytes.
    """

    __slots__ = (
        "low", "range", "queue", "bytes_outstanding", "output", "terminated", "flushed"
    )

    def __init__(self) -> None:
        self.low = 0
        self.range = 0x1FE
        self.queue = -9
        self.bytes_outstanding = 0
        self.output = bytearray()
        self.terminated = False
        self.flushed = False

    def _put_byte(self) -> None:
        if self.queue < 0:
            return
        out = self.low >> (self.queue + 10)
        self.low &= (0x400 << self.queue) - 1
        self.queue -= 8
        if out < 0 or out > 0x1FF:
            raise HEVCBitstreamError("CABAC byte queue produced an invalid carry")
        low_byte = out & 0xFF
        if low_byte == 0xFF:
            self.bytes_outstanding += 1
            return
        carry = out >> 8
        if carry:
            if not self.output:
                raise HEVCBitstreamError("CABAC carry escaped before a preceding byte")
            if self.output[-1] + carry > 0xFF:
                raise HEVCBitstreamError("CABAC carry overflowed a committed byte")
            self.output[-1] += carry
        while self.bytes_outstanding:
            self.output.append(0xFF if carry == 0 else 0x00)
            self.bytes_outstanding -= 1
        self.output.append(low_byte)

    def _renorm(self) -> None:
        while self.range < 256:
            self.range <<= 1
            self.low <<= 1
            self.queue += 1
            self._put_byte()

    def encode_bin(self, context: HEVCCabacContext, bin_value: int) -> None:
        if self.flushed or self.terminated:
            raise HEVCBitstreamError("CABAC cannot encode after termination or flush")
        if bin_value not in (0, 1):
            raise HEVCBitstreamError("CABAC bins must be zero or one")
        range_lps = cabac_lps_range(context.state, self.range)
        self.range -= range_lps
        if bin_value != context.mps:
            self.low += self.range
            self.range = range_lps
        updated = cabac_update_context(context, bin_value)
        context.state, context.mps = updated.state, updated.mps
        self._renorm()

    def encode_bypass(self, bin_value: int) -> None:
        if self.flushed or self.terminated:
            raise HEVCBitstreamError("CABAC cannot encode after termination or flush")
        if bin_value not in (0, 1):
            raise HEVCBitstreamError("CABAC bins must be zero or one")
        self.low <<= 1
        if bin_value:
            self.low += self.range
        self.queue += 1
        self._put_byte()

    def encode_terminate(self, bin_value: int = 1) -> None:
        if self.flushed:
            raise HEVCBitstreamError("CABAC cannot terminate after flush")
        if bin_value not in (0, 1):
            raise HEVCBitstreamError("CABAC termination bins must be zero or one")
        self.range -= 2
        if bin_value:
            self.terminated = True
        self._renorm()

    def flush(self) -> bytes:
        """Flush the arithmetic registers, without adding slice trailing bits."""
        if self.flushed:
            return bytes(self.output)
        if not self.terminated:
            raise HEVCBitstreamError("CABAC flush requires encode_terminate(1)")
        self.low += self.range - 2
        self.low |= 1
        self.low <<= 9
        self.queue += 9
        self._put_byte()
        self._put_byte()
        if self.queue < 0:
            self.low <<= -self.queue
        self.queue = 0
        self._put_byte()
        while self.bytes_outstanding:
            self.output.append(0xFF)
            self.bytes_outstanding -= 1
        self.flushed = True
        return bytes(self.output)


def hevc_capability_report() -> Mapping[str, object]:
    """Return an explicit machine-readable status for callers and audits."""
    return {
        "parameter_sets": True,
        "nal_and_rbsp": True,
        "hvcc": True,
        "cabac_context_and_registers": True,
        "pixel_to_slice_encoder": False,
        "supported_profile": "Main@L4.0, one layer, one temporal sub-layer, 8-bit 4:2:0",
        "runtime_codec_dependencies": (),
        "external_decoder_validated_payload": False,
        "fail_closed": True,
    }


def encode_hevc_intra_aot(
    samples: object,
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    chroma_format_idc: int = HEVC_CHROMA_420,
    quality: int | None = None,
    **_options: object,
) -> bytes:
    """Fail closed until a complete, externally validated slice encoder exists.

    ``samples`` is deliberately not inspected or coerced here.  Accepting it
    and returning VPS/SPS/PPS bytes would be an API-level lie: HEIF decoders
    require a coded VCL picture in addition to the parameter sets.
    """
    _validate_picture_geometry(width, height)
    if bit_depth != 8 or chroma_format_idc != HEVC_CHROMA_420:
        raise HEVCProfileError("only the 8-bit Main 4:2:0 profile is currently defined")
    if quality is not None and (not isinstance(quality, int) or not 0 <= quality <= 51):
        raise HEVCProfileError("HEVC quality/QP must be an integer between 0 and 51")
    raise HEVCEncoderUnavailable(
        "native HEVC pixel-to-slice encoding is not enabled: VPS/SPS/PPS and CABAC "
        "primitives are available, but no complete intra VCL payload is emitted"
    )


__all__ = [
    "HEVCError", "HEVCBitstreamError", "HEVCProfileError", "HEVCEncoderUnavailable",
    "HEVCBitWriter", "HEVCBitReader", "HEVCNALUnit", "HEVCProfileTierLevel",
    "HEVCParameterSets", "HEVCCabacContext", "HEVCCabacEncoder",
    "HEVC_NAL_VPS", "HEVC_NAL_SPS", "HEVC_NAL_PPS", "HEVC_NAL_IDR_W_RADL",
    "HEVC_NAL_IDR_N_LP", "HEVC_NAL_CRA_NUT", "HEVC_PROFILE_MAIN", "HEVC_CHROMA_420", "HEVC_CHROMA_422", "HEVC_CHROMA_444",
    "rbsp_to_ebsp", "ebsp_to_rbsp", "build_nal_unit", "parse_nal_unit",
    "main_profile_tier_level", "build_vps_rbsp", "build_sps_rbsp", "build_pps_rbsp",
    "build_hvcc", "build_hevc_parameter_sets", "parse_hvcc", "cabac_context_from_init",
    "cabac_lps_range", "cabac_update_context", "hevc_capability_report",
    "encode_hevc_intra_aot",
]
