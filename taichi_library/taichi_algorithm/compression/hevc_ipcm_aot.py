"""Bounded, lossless HEVC I_PCM profile for the native HEIF path.

This is a deliberately bounded interoperability milestone, not the general
HEVC encoder.  It emits one 8-bit planar 4:2:0, 4:2:2, or 4:4:4 IDR picture
made from 16x16 I_PCM coding blocks for format-aligned dimensions up to
4096x4096.  Non-16-aligned dimensions are padded at the final CTU edge and
cropped with the SPS conformance window, so the decoded visible samples
remain exact.  The samples are carried verbatim; there is no prediction,
transform, quantization, or rate-distortion decision yet.

The profile is kept in its own module so callers cannot mistake it for the
unfinished compressed HEVC path in :mod:`hevc_aot`.  It uses only the Python
standard library and the local HEVC bitstream primitives.  FFmpeg/x265 is
used only by the verification harness, never at runtime here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .hevc_aot import (
    HEVC_CHROMA_420,
    HEVC_CHROMA_422,
    HEVC_CHROMA_444,
    HEVC_NAL_IDR_N_LP,
    HEVC_NAL_PPS,
    HEVC_NAL_SPS,
    HEVC_NAL_VPS,
    HEVCBitWriter,
    HEVCBitReader,
    HEVCBitstreamError,
    HEVCProfileError,
    HEVCCabacContext,
    build_hvcc,
    build_nal_unit,
    build_pps_rbsp,
    build_vps_rbsp,
    cabac_context_from_init,
    main_profile_tier_level,
    parse_nal_unit,
)


HEVC_IPCM_WIDTH = 16
HEVC_IPCM_HEIGHT = 16
HEVC_IPCM_BIT_DEPTH = 8
HEVC_IPCM_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_IPCM_LUMA_SAMPLES = HEVC_IPCM_WIDTH * HEVC_IPCM_HEIGHT
HEVC_IPCM_CHROMA_WIDTH = HEVC_IPCM_WIDTH // 2
HEVC_IPCM_CHROMA_HEIGHT = HEVC_IPCM_HEIGHT // 2
HEVC_IPCM_SAMPLE_BYTES = HEVC_IPCM_LUMA_SAMPLES + 2 * HEVC_IPCM_CHROMA_WIDTH * HEVC_IPCM_CHROMA_HEIGHT
HEVC_IPCM_MIN_DIMENSION = 16
HEVC_IPCM_MAX_WIDTH = 4096
HEVC_IPCM_MAX_HEIGHT = 4096


class HEVCIPCMProfileError(HEVCProfileError):
    """Raised when input is outside the validated I_PCM profile."""


class HEVCIPCMBitstreamError(HEVCIPCMProfileError):
    """Raised when an emitted I_PCM stream fails strict local validation."""


def _validate_chroma_format(chroma_format_idc: int) -> tuple[int, int]:
    if type(chroma_format_idc) is not int or chroma_format_idc not in (
        HEVC_CHROMA_420,
        HEVC_CHROMA_422,
        HEVC_CHROMA_444,
    ):
        raise HEVCIPCMProfileError(
            "HEVC I_PCM chroma_format_idc must be 1 (4:2:0), 2 (4:2:2), or 3 (4:4:4)"
        )
    sub_width = 2 if chroma_format_idc in (HEVC_CHROMA_420, HEVC_CHROMA_422) else 1
    sub_height = 2 if chroma_format_idc == HEVC_CHROMA_420 else 1
    return sub_width, sub_height


def _plane_dimensions(width: int, height: int, chroma_format_idc: int) -> tuple[int, int]:
    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    return (width + sub_width - 1) // sub_width, (height + sub_height - 1) // sub_height


def _validate_ipcm_geometry(
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("HEVC I_PCM dimensions must be integers")
    if not (HEVC_IPCM_MIN_DIMENSION <= width <= HEVC_IPCM_MAX_WIDTH):
        raise HEVCIPCMProfileError(
            f"HEVC I_PCM width must be between {HEVC_IPCM_MIN_DIMENSION} and "
            f"{HEVC_IPCM_MAX_WIDTH}"
        )
    if not (HEVC_IPCM_MIN_DIMENSION <= height <= HEVC_IPCM_MAX_HEIGHT):
        raise HEVCIPCMProfileError(
            f"HEVC I_PCM height must be between {HEVC_IPCM_MIN_DIMENSION} and "
            f"{HEVC_IPCM_MAX_HEIGHT}"
        )
    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    # The public planar layout uses complete chroma samples.  4:2:0 requires
    # even width and height; 4:2:2 requires only even width.  4:4:4 has no
    # visible parity restriction.  Coding blocks are padded internally.
    if width % sub_width or height % sub_height:
        raise HEVCIPCMProfileError(
            "HEVC I_PCM dimensions must align with the selected chroma format"
        )


def _coded_dimension(value: int) -> int:
    """Return the smallest 16-pixel coding extent covering ``value``."""

    return ((value + HEVC_IPCM_MIN_DIMENSION - 1) // HEVC_IPCM_MIN_DIMENSION) * HEVC_IPCM_MIN_DIMENSION


def _conformance_window(
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> tuple[int, int, int, int, int, int]:
    """Return coded extents and crop offsets for the selected chroma format."""

    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    coded_width = _coded_dimension(width)
    coded_height = _coded_dimension(height)
    if (coded_width - width) % sub_width or (coded_height - height) % sub_height:
        raise HEVCIPCMProfileError("visible dimensions cannot be represented by the HEVC conformance window")
    return (
        coded_width,
        coded_height,
        0,
        (coded_width - width) // sub_width,
        0,
        (coded_height - height) // sub_height,
    )


def hevc_ipcm_sample_bytes(
    width: int = HEVC_IPCM_WIDTH,
    height: int = HEVC_IPCM_HEIGHT,
    *,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> int:
    """Return the planar byte count for the bounded I_PCM geometry."""

    _validate_ipcm_geometry(width, height, chroma_format_idc)
    chroma_width, chroma_height = _plane_dimensions(width, height, chroma_format_idc)
    return width * height + 2 * chroma_width * chroma_height


def _build_ipcm_sps_rbsp(
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> bytes:
    """Build an SPS whose 16x16 minimum and maximum coding block is PCM."""

    _validate_ipcm_geometry(width, height, chroma_format_idc)
    coded_width, coded_height, conf_left, conf_right, conf_top, conf_bottom = _conformance_window(width, height, chroma_format_idc)
    writer = HEVCBitWriter()
    ptl = main_profile_tier_level()
    writer.write(0, 4)  # sps_video_parameter_set_id
    writer.write(0, 3)  # sps_max_sub_layers_minus1
    writer.flag(1)  # sps_temporal_id_nesting_flag
    ptl.write(writer)
    writer.ue(0)  # sps_seq_parameter_set_id
    writer.ue(chroma_format_idc)  # chroma_format_idc
    if chroma_format_idc == HEVC_CHROMA_444:
        writer.flag(0)  # separate_colour_plane_flag
    writer.ue(coded_width)
    writer.ue(coded_height)
    has_conformance_window = any((conf_left, conf_right, conf_top, conf_bottom))
    writer.flag(int(has_conformance_window))  # conformance_window_flag
    if has_conformance_window:
        # For 4:2:0, one window unit covers two luma samples horizontally
        # and vertically (SubWidthC/SubHeightC = 2).
        writer.ue(conf_left)
        writer.ue(conf_right)
        writer.ue(conf_top)
        writer.ue(conf_bottom)
    writer.ue(0)  # bit_depth_luma_minus8
    writer.ue(0)  # bit_depth_chroma_minus8
    writer.ue(4)  # log2_max_pic_order_cnt_lsb_minus4
    writer.flag(0)  # sps_sub_layer_ordering_info_present_flag
    writer.ue(0)  # sps_max_dec_pic_buffering_minus1
    writer.ue(0)  # sps_max_num_reorder_pics
    writer.ue(0)  # sps_max_latency_increase_plus1
    writer.ue(1)  # log2_min_luma_coding_block_size_minus3 = 16x16
    writer.ue(0)  # log2_diff_max_min_luma_coding_block_size
    writer.ue(0)  # log2_min_luma_transform_block_size_minus2
    writer.ue(0)  # log2_diff_max_min_luma_transform_block_size
    writer.ue(0)  # max_transform_hierarchy_depth_inter
    writer.ue(0)  # max_transform_hierarchy_depth_intra
    writer.flag(0)  # scaling_list_enabled_flag
    writer.flag(0)  # amp_enabled_flag
    writer.flag(0)  # sample_adaptive_offset_enabled_flag
    writer.flag(1)  # pcm_enabled_flag
    writer.write(7, 4)  # pcm_sample_bit_depth_luma_minus1 = 8-bit
    writer.write(7, 4)  # pcm_sample_bit_depth_chroma_minus1 = 8-bit
    writer.ue(1)  # log2_min_pcm_luma_coding_block_size_minus3 = 16x16
    writer.ue(0)  # log2_diff_max_min_pcm_luma_coding_block_size
    writer.flag(1)  # pcm_loop_filter_disabled_flag
    writer.ue(0)  # num_short_term_ref_pic_sets
    writer.flag(0)  # long_term_ref_pics_present_flag
    writer.flag(0)  # sps_temporal_mvp_enabled_flag
    writer.flag(1)  # strong_intra_smoothing_enabled_flag
    writer.flag(0)  # vui_parameters_present_flag
    writer.flag(0)  # sps_extension_present_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


def _validate_samples(
    samples: object,
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> bytes:
    expected = hevc_ipcm_sample_bytes(width, height, chroma_format_idc=chroma_format_idc)
    if samples is None:
        raise TypeError("HEVC I_PCM samples are required")
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("HEVC I_PCM samples must be a bytes-like planar Y/Cb/Cr buffer") from exc
    if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
        raise TypeError("HEVC I_PCM samples must be a one-dimensional contiguous byte buffer")
    if view.nbytes != expected:
        raise HEVCIPCMProfileError(
            f"the {width}x{height} selected-chroma profile requires {expected} bytes"
        )
    return bytes(view)


# H.265 Table 9-5 renormalization shifts, used by the HM-style CABAC encoder.
_CABAC_RENORM_SHIFT = (6, 5, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2, 2,
                       1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)


class _IpcmCabacEncoder:
    """Minimal HM-compatible CABAC writer for part_mode/termination bins."""

    __slots__ = ("low", "range", "bits_left", "buffered_byte", "buffered", "sink")

    def __init__(self) -> None:
        self.low = 0
        self.range = 510
        self.bits_left = 23
        self.buffered_byte = 0xFF
        self.buffered = 0
        self.sink = HEVCBitWriter()

    def _write_out(self) -> None:
        lead_byte = self.low >> (24 - self.bits_left)
        self.bits_left += 8
        self.low &= 0xFFFFFFFF >> self.bits_left
        if lead_byte == 0xFF:
            self.buffered += 1
            return
        if self.buffered:
            carry = lead_byte >> 8
            self.sink.write(self.buffered_byte + carry, 8)
            self.buffered_byte = lead_byte & 0xFF
            value = (0xFF + carry) & 0xFF
            while self.buffered > 1:
                self.sink.write(value, 8)
                self.buffered -= 1
            return
        self.buffered = 1
        # HM keeps the lead byte in an 8-bit register.  The high bit is a
        # carry indicator handled only when a buffered byte already exists;
        # retaining it here can make the final bit writer receive values
        # larger than one byte after a bypass-heavy CABAC sequence.
        self.buffered_byte = lead_byte & 0xFF

    def _test_and_write_out(self) -> None:
        if self.bits_left < 12:
            self._write_out()

    def encode_bin(self, context: HEVCCabacContext, value: int) -> None:
        if value not in (0, 1):
            raise HEVCIPCMBitstreamError("HEVC I_PCM CABAC bins must be zero or one")
        from .hevc_aot import cabac_lps_range, cabac_update_context

        lps = cabac_lps_range(context.state, self.range)
        self.range -= lps
        if value != context.mps:
            shifts = _CABAC_RENORM_SHIFT[lps >> 3]
            self.low = ((self.low + self.range) << shifts) & 0xFFFFFFFF
            self.range = lps << shifts
        else:
            if self.range < 256:
                self.low = (self.low << 1) & 0xFFFFFFFF
                self.range <<= 1
                self.bits_left -= 1
        updated = cabac_update_context(context, value)
        context.state, context.mps = updated.state, updated.mps
        self._test_and_write_out()

    def encode_bypass(self, value: int) -> None:
        if value not in (0, 1):
            raise HEVCIPCMBitstreamError("HEVC I_PCM bypass bins must be zero or one")
        self.low = (self.low << 1) & 0xFFFFFFFF
        if value:
            self.low = (self.low + self.range) & 0xFFFFFFFF
        self.bits_left -= 1
        self._test_and_write_out()

    def encode_terminate(self, value: int = 1) -> None:
        if value not in (0, 1):
            raise HEVCIPCMBitstreamError("HEVC I_PCM termination bins must be zero or one")
        self.range -= 2
        if value:
            self.low = ((self.low + self.range) << 7) & 0xFFFFFFFF
            self.range = 256
            self.bits_left -= 7
        elif self.range < 256:
            self.low = (self.low << 1) & 0xFFFFFFFF
            self.range <<= 1
            self.bits_left -= 1
        self._test_and_write_out()

    def finish(self) -> bytes:
        if self.low >> (32 - self.bits_left):
            self.sink.write(self.buffered_byte + 1, 8)
            while self.buffered > 1:
                self.sink.write(0, 8)
                self.buffered -= 1
            self.low = (self.low - (1 << (32 - self.bits_left))) & 0xFFFFFFFF
        else:
            if self.buffered:
                self.sink.write(self.buffered_byte, 8)
            while self.buffered > 1:
                self.sink.write(0xFF, 8)
                self.buffered -= 1
        self.sink.write(self.low >> 8, 24 - self.bits_left)
        return self.sink.bytes()


def _cabac_part_and_pcm_prefix(
    context: HEVCCabacContext,
    *,
    end_of_slice_before: int | None = None,
) -> bytes:
    # initValue=184 is the first PART_MODE context for an I slice.  At QP 26,
    # H.265 context initialization yields pStateIdx=0, valMps=1.  The context
    # is retained across 16x16 CTUs; PCM resets only the arithmetic registers,
    # not CABAC context state.
    encoder = _IpcmCabacEncoder()
    if end_of_slice_before is not None:
        encoder.encode_terminate(end_of_slice_before)
    encoder.encode_bin(context, 1)  # PART_2Nx2N
    encoder.encode_terminate()  # pcm_flag=1
    return encoder.finish()


def _cabac_end_of_slice(value: int = 1) -> bytes:
    encoder = _IpcmCabacEncoder()
    encoder.encode_terminate(value)  # end_of_slice_segment_flag
    return encoder.finish()


def _iter_ipcm_blocks(
    samples: bytes,
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
):
    luma_size = width * height
    chroma_width, chroma_height = _plane_dimensions(width, height, chroma_format_idc)
    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    coded_width, coded_height, *_ = _conformance_window(width, height, chroma_format_idc)
    chroma_block_width = HEVC_IPCM_MIN_DIMENSION // sub_width
    chroma_block_height = HEVC_IPCM_MIN_DIMENSION // sub_height
    cb_offset = luma_size
    cr_offset = cb_offset + chroma_width * chroma_height
    for block_y in range(0, coded_height, HEVC_IPCM_MIN_DIMENSION):
        for block_x in range(0, coded_width, HEVC_IPCM_MIN_DIMENSION):
            block = bytearray()
            for row in range(HEVC_IPCM_MIN_DIMENSION):
                source_y = min(block_y + row, height - 1)
                for column in range(HEVC_IPCM_MIN_DIMENSION):
                    source_x = min(block_x + column, width - 1)
                    block.append(samples[source_y * width + source_x])
            chroma_x = block_x // sub_width
            chroma_y = block_y // sub_height
            for offset in (cb_offset, cr_offset):
                for row in range(chroma_block_height):
                    source_y = min(chroma_y + row, chroma_height - 1)
                    for column in range(chroma_block_width):
                        source_x = min(chroma_x + column, chroma_width - 1)
                        block.append(samples[offset + source_y * chroma_width + source_x])
            yield bytes(block)


def _build_ipcm_slice_rbsp(
    samples: bytes,
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> bytes:
    writer = HEVCBitWriter()
    writer.flag(1)  # first_slice_segment_in_pic_flag
    writer.flag(0)  # no_output_of_prior_pics_flag for IDR_N_LP
    writer.ue(0)  # slice_pic_parameter_set_id
    writer.ue(2)  # slice_type = I
    writer.se(0)  # slice_qp_delta
    writer.flag(1)  # slice_loop_filter_across_slices_enabled_flag (PPS enables it)
    writer.flag(1)  # alignment_bit_equal_to_one
    while not writer.byte_aligned:
        writer.flag(0)

    # PCM sample syntax resets the CABAC arithmetic registers after each raw
    # block.  The PART_MODE context itself remains live across those resets.
    context = cabac_context_from_init(26, 184)
    blocks = tuple(_iter_ipcm_blocks(samples, width, height, chroma_format_idc))
    for index, block in enumerate(blocks):
        prefix = _cabac_part_and_pcm_prefix(
            context,
            end_of_slice_before=None if index == 0 else 0,
        )
        for value in prefix:
            writer.write(value, 8)
        # encodePCMAlignBits(): one alignment-one bit, then zero alignment bits.
        writer.flag(1)
        while not writer.byte_aligned:
            writer.flag(0)
        for value in block:
            writer.write(value, 8)

    # The final CTU terminates the slice after its PCM payload.  Non-final CTUs
    # emitted end_of_slice_segment_flag=0 as the prefix of the next segment.
    for value in _cabac_end_of_slice(1):
        writer.write(value, 8)
    writer.rbsp_trailing_bits()
    return writer.bytes()


def _sps_dimensions(nal: bytes) -> tuple[int, int, int]:
    parsed = parse_nal_unit(nal)
    if parsed.nal_unit_type != HEVC_NAL_SPS:
        raise HEVCIPCMBitstreamError("the I_PCM SPS NAL has an unexpected type")
    reader = HEVCBitReader(parsed.rbsp)
    reader.read(4)  # sps_video_parameter_set_id
    max_sub_layers_minus1 = reader.read(3)
    reader.read(1)  # sps_temporal_id_nesting_flag
    if max_sub_layers_minus1 != 0:
        raise HEVCIPCMBitstreamError("the bounded I_PCM validator expects one temporal sub-layer")
    reader.read(8)  # general_profile_space/tier/profile_idc
    reader.read(32)  # general_profile_compatibility_flags
    reader.read(48)  # general_constraint_indicator_flags
    reader.read(8)  # general_level_idc
    reader.ue()  # sps_seq_parameter_set_id
    chroma_format_idc = reader.ue(max_value=3)
    if chroma_format_idc == HEVC_CHROMA_444:
        if reader.read(1) != 0:
            raise HEVCIPCMBitstreamError("separate colour planes are outside the bounded I_PCM profile")
    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    coded_width = reader.ue(max_value=HEVC_IPCM_MAX_WIDTH)
    coded_height = reader.ue(max_value=HEVC_IPCM_MAX_HEIGHT)
    conformance_window_flag = reader.read(1)
    if conformance_window_flag:
        conf_left = reader.ue()
        conf_right = reader.ue()
        conf_top = reader.ue()
        conf_bottom = reader.ue()
        width = coded_width - sub_width * (conf_left + conf_right)
        height = coded_height - sub_height * (conf_top + conf_bottom)
    else:
        width, height = coded_width, coded_height
    return width, height, chroma_format_idc


@dataclass(frozen=True)
class HEVCIPCMPicture:
    """One complete, exact, externally decodable I_PCM picture."""

    width: int
    height: int
    bit_depth: int
    chroma_format_idc: int
    nals: tuple[bytes, bytes, bytes, bytes]
    hvcc: bytes

    @property
    def annex_b(self) -> bytes:
        return b"".join(b"\x00\x00\x00\x01" + nal for nal in self.nals)

    @property
    def vcl_nal(self) -> bytes:
        return self.nals[-1]


def build_hevc_ipcm_picture(
    samples: object,
    width: int = HEVC_IPCM_WIDTH,
    height: int = HEVC_IPCM_HEIGHT,
    *,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> HEVCIPCMPicture:
    _validate_ipcm_geometry(width, height, chroma_format_idc)
    planar = _validate_samples(samples, width, height, chroma_format_idc)
    ptl = main_profile_tier_level(153 if max(width, height) > 2048 else 120)
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(HEVC_NAL_SPS, _build_ipcm_sps_rbsp(width, height, chroma_format_idc))
    pps = build_nal_unit(HEVC_NAL_PPS, build_pps_rbsp())
    slice_rbsp = _build_ipcm_slice_rbsp(planar, width, height, chroma_format_idc)
    vcl = build_nal_unit(HEVC_NAL_IDR_N_LP, slice_rbsp)
    hvcc = build_hvcc((vps, sps, pps), ptl=ptl, bit_depth=8, chroma_format_idc=chroma_format_idc)
    picture = HEVCIPCMPicture(
        width,
        height,
        HEVC_IPCM_BIT_DEPTH,
        chroma_format_idc,
        (vps, sps, pps, vcl),
        hvcc,
    )
    validate_hevc_ipcm_annex_b(
        picture.annex_b,
        width=width,
        height=height,
        chroma_format_idc=chroma_format_idc,
    )
    return picture


def encode_hevc_ipcm_aot(
    samples: object,
    width: int = HEVC_IPCM_WIDTH,
    height: int = HEVC_IPCM_HEIGHT,
    *,
    chroma_format_idc: int = HEVC_IPCM_CHROMA_FORMAT_IDC,
) -> bytes:
    """Return a complete bounded 8-bit lossless HEVC I_PCM stream."""

    return build_hevc_ipcm_picture(
        samples,
        width=width,
        height=height,
        chroma_format_idc=chroma_format_idc,
    ).annex_b


def validate_hevc_ipcm_annex_b(
    data: bytes | bytearray | memoryview,
    *,
    width: int | None = None,
    height: int | None = None,
    chroma_format_idc: int | None = None,
) -> dict[str, object]:
    if (width is None) != (height is None):
        raise TypeError("HEVC I_PCM width and height must be provided together")
    raw = bytes(data)
    if not raw:
        raise HEVCIPCMBitstreamError("HEVC I_PCM Annex-B data is empty")
    nals: list[bytes] = []
    cursor = 0
    while cursor < len(raw):
        marker = raw.find(b"\x00\x00\x01", cursor)
        if marker < 0:
            break
        start = marker + 3
        if marker > 0 and raw[marker - 1] == 0:
            start = marker + 3
        next_marker = raw.find(b"\x00\x00\x01", start)
        end = len(raw) if next_marker < 0 else next_marker
        nal = raw[start:end].rstrip(b"\x00")
        if not nal:
            raise HEVCIPCMBitstreamError("HEVC I_PCM stream contains an empty NAL")
        nals.append(nal)
        if next_marker < 0:
            break
        cursor = next_marker
    if len(nals) != 4:
        raise HEVCIPCMBitstreamError("the I_PCM profile requires VPS, SPS, PPS, and one IDR NAL")
    parsed = tuple(parse_nal_unit(nal) for nal in nals)
    types = tuple(item.nal_unit_type for item in parsed)
    if types != (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS, HEVC_NAL_IDR_N_LP):
        raise HEVCIPCMBitstreamError(f"unexpected I_PCM NAL order: {types!r}")
    parsed_width, parsed_height, parsed_chroma = _sps_dimensions(nals[1])
    if width is None:
        width, height = parsed_width, parsed_height
    expected_chroma = parsed_chroma if chroma_format_idc is None else chroma_format_idc
    _validate_ipcm_geometry(width, height, expected_chroma)
    if (parsed_width, parsed_height) != (width, height):
        raise HEVCIPCMBitstreamError(
            f"SPS geometry {parsed_width}x{parsed_height} disagrees with expected {width}x{height}"
        )
    if parsed_chroma != expected_chroma:
        raise HEVCIPCMBitstreamError("I_PCM SPS chroma does not match the requested profile")
    return {
        "nal_types": types,
        "nal_count": len(nals),
        "width": width,
        "height": height,
        "bit_depth": HEVC_IPCM_BIT_DEPTH,
        "chroma_format_idc": parsed_chroma,
        "lossless_ipcm": True,
        "bytes": len(raw),
    }


def hevc_ipcm_capability_report() -> Mapping[str, object]:
    return {
        "parameter_sets": True,
        "pixel_to_slice_encoder": True,
        "lossless_ipcm": True,
        "general_encoder": False,
        "supported_profile": "format-aligned dimensions up to 4096x4096, Main, 8-bit 4:2:0/4:2:2/4:4:4, padded 16x16 IDR I_PCM slice with SPS conformance window",
        "variable_dimensions": True,
        "variable_subsampling": True,
        "chroma_formats": (HEVC_CHROMA_420, HEVC_CHROMA_422, HEVC_CHROMA_444),
        "runtime_codec_dependencies": (),
        "external_decoder_validated_payload": True,
        "gpu_full_codec": False,
        "fail_closed": True,
    }


__all__ = [
    "HEVC_IPCM_WIDTH",
    "HEVC_IPCM_HEIGHT",
    "HEVC_IPCM_BIT_DEPTH",
    "HEVC_IPCM_CHROMA_FORMAT_IDC",
    "HEVC_CHROMA_422",
    "HEVC_CHROMA_444",
    "HEVC_IPCM_SAMPLE_BYTES",
    "HEVC_IPCM_MIN_DIMENSION",
    "HEVC_IPCM_MAX_WIDTH",
    "HEVC_IPCM_MAX_HEIGHT",
    "HEVCIPCMProfileError",
    "HEVCIPCMBitstreamError",
    "HEVCIPCMPicture",
    "hevc_ipcm_sample_bytes",
    "build_hevc_ipcm_picture",
    "encode_hevc_ipcm_aot",
    "validate_hevc_ipcm_annex_b",
    "hevc_ipcm_capability_report",
]
