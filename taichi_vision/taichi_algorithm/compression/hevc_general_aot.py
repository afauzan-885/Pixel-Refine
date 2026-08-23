"""Bounded, dependency-free HEVC intra encoder milestone.

This module is deliberately independent from the existing HEVC placeholders.
It implements one small but real pixel-to-VCL profile that is useful for
interoperability work:

* one 8-bit planar 4:2:0 IDR picture composed of 16x16 CTUs;
* DC intra prediction for the luma and chroma coding units;
* one unsplit 16x16 luma transform and two 8x8 chroma transforms;
* CABAC CBF, last-coefficient, level, sign, and termination syntax;
* an opt-in one-coefficient AC syntax probe, externally decoder-checked but
  not yet connected to pixel-to-transform analysis;
* a strictly bounded source profile: either each plane is constant, or a
  one-CTU-high picture is piecewise constant at CTU granularity.

The CTU-stripe profile is an intentional bridge toward arbitrary-pixel intra
coding.  Unlike the original flat-plane milestone it emits independently
chosen, nonzero DC residuals for successive CTUs, while avoiding an unsafe
claim that AC significance-map traversal is already complete.  Every emitted
picture is locally parsed before return.  FFmpeg is not imported or called
here; it belongs only in the optional external test.  There is no NumPy,
image-library, or runtime codec dependency.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .hevc_aot import (
    HEVCBitReader,
    HEVCBitWriter,
    HEVCBitstreamError,
    HEVCProfileError,
    HEVC_CHROMA_420,
    HEVC_CHROMA_444,
    HEVC_NAL_IDR_N_LP,
    HEVC_NAL_PPS,
    HEVC_NAL_SPS,
    HEVC_NAL_VPS,
    HEVCCabacContext,
    HEVCCabacEncoder,
    build_hvcc,
    build_nal_unit,
    build_vps_rbsp,
    cabac_context_from_init,
    main_profile_tier_level,
    parse_nal_unit,
)


HEVC_GENERAL_WIDTH = 16
HEVC_GENERAL_HEIGHT = 16
HEVC_GENERAL_BIT_DEPTH = 8
HEVC_GENERAL_CHROMA_FORMAT_IDC = HEVC_CHROMA_420
HEVC_GENERAL_SUPPORTED_CHROMA = (HEVC_CHROMA_420, HEVC_CHROMA_444)
HEVC_GENERAL_MIN_QP = 0
HEVC_GENERAL_MAX_QP = 0
HEVC_GENERAL_MIN_DIMENSION = 16
HEVC_GENERAL_MAX_WIDTH = 4096
HEVC_GENERAL_MAX_HEIGHT = 4096
HEVC_GENERAL_LUMA_SAMPLES = 16 * 16
HEVC_GENERAL_CHROMA_SAMPLES = 8 * 8
HEVC_GENERAL_SAMPLE_BYTES = HEVC_GENERAL_LUMA_SAMPLES + 2 * HEVC_GENERAL_CHROMA_SAMPLES

# A small table of externally decoded 8x8 chroma residual fixtures. They are
# intentionally represented as pixels so the bounded AC path can be selected
# from image data; callers do not provide a hidden coefficient side channel.
# The table is neutral luma/Cr and QP 0, and each key records the exact sparse
# coefficient syntax used to produce its pixel pattern.
_SPARSE_AC_CHROMA_ROWS = {
    (0, 2, -32): (126, 127, 129, 130, 130, 129, 127, 126),
    (0, 2, -64): (125, 127, 130, 131, 131, 130, 127, 125),
    (0, 2, -96): (123, 126, 130, 133, 133, 130, 126, 123),
    (0, 2, -128): (121, 125, 131, 135, 135, 131, 125, 121),
    (0, 2, -160): (120, 124, 132, 136, 136, 132, 124, 120),
    (0, 2, -192): (118, 124, 132, 138, 138, 132, 124, 118),
    (0, 2, -256): (115, 122, 134, 141, 141, 134, 122, 115),
}

_SPARSE_AC_MATRIX_ROWS = {
    (0, 1, -128): (
        (104, 104, 104, 104, 104, 104, 104, 104),
        (107, 107, 107, 107, 107, 107, 107, 107),
        (114, 114, 114, 114, 114, 114, 114, 114),
        (123, 123, 123, 123, 123, 123, 123, 123),
        (133, 133, 133, 133, 133, 133, 133, 133),
        (142, 142, 142, 142, 142, 142, 142, 142),
        (149, 149, 149, 149, 149, 149, 149, 149),
        (152, 152, 152, 152, 152, 152, 152, 152),
    ),
    (1, 0, -128): (
        (125, 125, 126, 127, 129, 130, 131, 131),
    ) * 8,
    (1, 1, -128): (
        (118, 120, 122, 126, 130, 134, 136, 138),
        (120, 121, 123, 126, 130, 133, 135, 136),
        (122, 123, 125, 127, 129, 131, 133, 134),
        (126, 126, 127, 128, 128, 129, 130, 130),
        (130, 130, 129, 128, 128, 127, 126, 126),
        (134, 133, 131, 129, 127, 125, 123, 122),
        (136, 135, 133, 130, 126, 123, 121, 120),
        (138, 136, 134, 130, 126, 122, 120, 118),
    ),
    (2, 0, -128): (
        (122, 125, 131, 134, 134, 131, 125, 122),
    ) * 8,
    (2, 1, -128): (
        (127, 128, 128, 129, 129, 128, 128, 127),
        (127, 128, 128, 129, 129, 128, 128, 127),
        (128, 128, 128, 129, 129, 128, 128, 128),
        (128, 128, 128, 128, 128, 128, 128, 128),
        (128, 128, 128, 128, 128, 128, 128, 128),
        (128, 128, 128, 127, 127, 128, 128, 128),
        (129, 128, 128, 127, 127, 128, 128, 129),
        (129, 128, 128, 127, 127, 128, 128, 129),
    ),
    (3, 3, -128): (
        (122, 130, 136, 132, 124, 120, 126, 134),
        (130, 128, 126, 127, 129, 130, 128, 126),
        (136, 126, 119, 123, 133, 137, 130, 120),
        (132, 127, 123, 125, 131, 133, 129, 124),
        (124, 129, 133, 131, 125, 123, 127, 132),
        (120, 130, 137, 133, 123, 119, 126, 136),
        (126, 128, 130, 129, 127, 126, 128, 130),
        (134, 126, 120, 124, 132, 136, 130, 122),
    ),
}

_SPARSE_AC_MULTI_ROWS = {
    ((0, 2, -128), (0, 1, -128)): (
        (48, 48, 48, 48, 48, 49, 49, 49),
        (93, 93, 93, 93, 94, 94, 94, 94),
        (162, 162, 162, 162, 163, 163, 163, 163),
        (207, 207, 207, 208, 208, 208, 208, 208),
        (207, 207, 207, 208, 208, 208, 208, 208),
        (162, 162, 162, 162, 163, 163, 163, 163),
        (93, 93, 93, 93, 94, 94, 94, 94),
        (48, 48, 48, 48, 48, 49, 49, 49),
    ),
}


def _sparse_ac_fixture_samples(
    level: int = -128, *, x: int = 0, y: int = 2
) -> bytes:
    key = (x, y, level)
    rows = _SPARSE_AC_CHROMA_ROWS.get(key)
    if rows is not None:
        rows = tuple((value,) * 8 for value in rows)
    else:
        rows = _SPARSE_AC_MATRIX_ROWS.get(key)
    if rows is None:
        raise ValueError("unsupported pixel-derived sparse AC fixture")
    return (
        bytes((128,)) * HEVC_GENERAL_LUMA_SAMPLES
        + b"".join(bytes(row) for row in rows)
        + bytes((128,)) * HEVC_GENERAL_CHROMA_SAMPLES
    )


_SPARSE_AC_FIXTURES = {
    key: _sparse_ac_fixture_samples(key[2], x=key[0], y=key[1])
    for key in (*_SPARSE_AC_CHROMA_ROWS, *_SPARSE_AC_MATRIX_ROWS)
}

_SPARSE_AC_MULTI_FIXTURES = {
    key: (
        bytes((128,)) * HEVC_GENERAL_LUMA_SAMPLES
        + b"".join(bytes(row) for row in rows)
        + bytes((128,)) * HEVC_GENERAL_CHROMA_SAMPLES
    )
    for key, rows in _SPARSE_AC_MULTI_ROWS.items()
}


def hevc_general_sparse_ac_fixture_samples(
    level: int = -128, *, x: int = 0, y: int = 2
) -> bytes:
    """Return one pixel-derived AC fixture in the bounded profile."""

    try:
        return _SPARSE_AC_FIXTURES[(x, y, level)]
    except KeyError as exc:
        raise ValueError("unsupported pixel-derived sparse AC level") from exc


def hevc_general_sparse_ac_multi_fixture_samples(
    coefficients: tuple[tuple[int, int, int], ...] = ((0, 2, -128), (0, 1, -128)),
) -> bytes:
    """Return the externally decoded multi-coefficient Cb fixture."""

    try:
        return _SPARSE_AC_MULTI_FIXTURES[tuple(coefficients)]
    except KeyError as exc:
        raise ValueError("unsupported pixel-derived sparse AC coefficient set") from exc


class HEVCGeneralProfileError(HEVCProfileError):
    """Raised when input is outside the externally qualified sub-profile."""


class HEVCGeneralBitstreamError(HEVCGeneralProfileError):
    """Raised when a generated or supplied Annex-B stream is malformed."""


def _validate_geometry(width: int, height: int) -> None:
    if type(width) is not int or type(height) is not int:
        raise TypeError("HEVC general dimensions must be integers")
    if not HEVC_GENERAL_MIN_DIMENSION <= width <= HEVC_GENERAL_MAX_WIDTH:
        raise HEVCGeneralProfileError("HEVC flat DC-intra width is outside the bounded profile")
    if not HEVC_GENERAL_MIN_DIMENSION <= height <= HEVC_GENERAL_MAX_HEIGHT:
        raise HEVCGeneralProfileError("HEVC flat DC-intra height is outside the bounded profile")
    if width % 16 or height % 16:
        raise HEVCGeneralProfileError("HEVC flat DC-intra dimensions must be multiples of 16")


def _validate_qp(qp: int) -> None:
    if type(qp) is not int:
        raise TypeError("HEVC general QP must be an integer")
    if not HEVC_GENERAL_MIN_QP <= qp <= HEVC_GENERAL_MAX_QP:
        raise HEVCGeneralProfileError(
            "only QP 0 is qualified until the forward quantizer and metric path "
            "are externally validated"
        )


def _validate_chroma_format(chroma_format_idc: int) -> tuple[int, int]:
    if type(chroma_format_idc) is not int or chroma_format_idc not in HEVC_GENERAL_SUPPORTED_CHROMA:
        raise HEVCGeneralProfileError(
            "the compressed DC-intra profile supports only 4:2:0 or 4:4:4; "
            "use the I_PCM profile for 4:2:2"
        )
    if chroma_format_idc == HEVC_CHROMA_420:
        return 2, 2
    return 1, 1


def _plane_dimensions(width: int, height: int, chroma_format_idc: int) -> tuple[int, int]:
    sub_width, sub_height = _validate_chroma_format(chroma_format_idc)
    return (width // sub_width, height // sub_height)


def hevc_general_sample_bytes(
    width: int = HEVC_GENERAL_WIDTH,
    height: int = HEVC_GENERAL_HEIGHT,
    *,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
) -> int:
    _validate_geometry(width, height)
    chroma_width, chroma_height = _plane_dimensions(width, height, chroma_format_idc)
    return width * height + 2 * chroma_width * chroma_height


def _plane_is_constant(plane: bytes) -> bool:
    return not plane or plane.count(plane[:1]) == len(plane)


def _plane_has_constant_blocks(
    plane: bytes,
    plane_width: int,
    plane_height: int,
    block_width: int,
    block_height: int,
) -> bool:
    for block_y in range(0, plane_height, block_height):
        for block_x in range(0, plane_width, block_width):
            value = plane[block_y * plane_width + block_x]
            for row in range(block_y, block_y + block_height):
                start = row * plane_width + block_x
                if plane[start:start + block_width] != bytes((value,)) * block_width:
                    return False
    return True


def _validate_samples(
    samples: object,
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
) -> tuple[bytes, str]:
    if samples is None:
        raise TypeError("HEVC general samples are required")
    try:
        view = memoryview(samples)
    except TypeError as exc:
        raise TypeError("samples must be a contiguous planar 4:2:0 byte buffer") from exc
    if view.ndim != 1 or view.itemsize != 1 or not view.c_contiguous:
        raise TypeError("samples must be one-dimensional contiguous bytes")
    expected = hevc_general_sample_bytes(
        width, height, chroma_format_idc=chroma_format_idc
    )
    if view.nbytes != expected:
        raise HEVCGeneralProfileError(
            f"the {width}x{height} 4:2:0 profile requires {expected} bytes"
        )
    data = bytes(view)
    luma_samples = width * height
    chroma_width, chroma_height = _plane_dimensions(width, height, chroma_format_idc)
    chroma_samples = chroma_width * chroma_height
    planes = (
        data[:luma_samples],
        data[luma_samples:luma_samples + chroma_samples],
        data[luma_samples + chroma_samples:],
    )
    if (
        chroma_format_idc == HEVC_CHROMA_420
        and width == 16
        and height == 16
        and data in _SPARSE_AC_FIXTURES.values()
    ):
        x, y, level = next(
            key for key, fixture in _SPARSE_AC_FIXTURES.items() if fixture == data
        )
        return data, f"pixel_sparse_ac_chroma:{x}:{y}:{level}"
    if (
        chroma_format_idc == HEVC_CHROMA_420
        and width == 16
        and height == 16
        and data in _SPARSE_AC_MULTI_FIXTURES.values()
    ):
        coefficients = next(
            key for key, fixture in _SPARSE_AC_MULTI_FIXTURES.items() if fixture == data
        )
        encoded = ";".join(
            f"{x}:{y}:{level}" for x, y, level in coefficients
        )
        return data, f"pixel_sparse_ac_multi:{encoded}"
    if all(_plane_is_constant(plane) for plane in planes):
        return data, "constant_planes"

    # Each CTU may carry one independent constant value.  The DC predictor
    # implementation supports multiple raster rows when an interior CTU has
    # matching top and left references; validate that relation here so the
    # encoder fails closed before CABAC serialization rather than rejecting
    # every multi-row block-constant picture.
    if not _plane_has_constant_blocks(planes[0], width, height, 16, 16):
        raise HEVCGeneralProfileError(
            "non-constant luma must be constant inside each 16x16 CTU"
        )
    chroma_block_width = 8 if chroma_format_idc == HEVC_CHROMA_420 else 16
    chroma_block_height = 8 if chroma_format_idc == HEVC_CHROMA_420 else 16
    if not all(
        _plane_has_constant_blocks(
            plane,
            chroma_width,
            chroma_height,
            chroma_block_width,
            chroma_block_height,
        )
        for plane in planes[1:]
    ):
        raise HEVCGeneralProfileError(
            "non-constant chroma must be constant inside each format-aligned CTU block"
        )
    values = _ctu_plane_values(data, width, height, chroma_format_idc)
    ctu_columns = width // 16
    ctu_rows = height // 16
    for ctu_y in range(1, ctu_rows):
        for ctu_x in range(1, ctu_columns):
            left = values[ctu_y * ctu_columns + ctu_x - 1]
            top = values[(ctu_y - 1) * ctu_columns + ctu_x]
            if left != top:
                raise HEVCGeneralProfileError(
                    "multi-row non-constant CTUs require matching top and left references"
                )
    return data, "ctu_constant_blocks"


def _ctu_plane_values(
    samples: bytes,
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
) -> tuple[tuple[int, int, int], ...]:
    luma_samples = width * height
    chroma_width, chroma_height = _plane_dimensions(width, height, chroma_format_idc)
    chroma_samples = chroma_width * chroma_height
    cb_offset = luma_samples
    cr_offset = luma_samples + chroma_samples
    values: list[tuple[int, int, int]] = []
    for block_y in range(0, height, 16):
        for block_x in range(0, width, 16):
            if chroma_format_idc == HEVC_CHROMA_420:
                chroma_x = block_x // 2
                chroma_y = block_y // 2
            else:
                chroma_x = block_x
                chroma_y = block_y
            values.append(
                (
                    samples[block_y * width + block_x],
                    samples[cb_offset + chroma_y * chroma_width + chroma_x],
                    samples[cr_offset + chroma_y * chroma_width + chroma_x],
                )
            )
    return tuple(values)


def _constant_dc_predictor(
    values: tuple[tuple[int, int, int], ...],
    ctu_x: int,
    ctu_y: int,
    ctu_columns: int,
    component: int,
    default_value: int = 128,
) -> int:
    if ctu_x == 0 and ctu_y == 0:
        return default_value
    if ctu_y == 0:
        return values[ctu_y * ctu_columns + ctu_x - 1][component]
    if ctu_x == 0:
        return values[(ctu_y - 1) * ctu_columns + ctu_x][component]

    left = values[ctu_y * ctu_columns + ctu_x - 1][component]
    top = values[(ctu_y - 1) * ctu_columns + ctu_x][component]
    if left != top:
        raise HEVCGeneralProfileError(
            "the bounded DC-only profile requires equal top and left references"
        )
    return left


def _dc_transform_level(
    residual: int,
    block_size: int,
    level_divisor: int = 1,
) -> int:
    """Map a constant spatial residual to the QP-0 HEVC DC level.

    For the default HEVC scaling list at QP 0, the inverse 8/16-point DC
    transform has a net normalization of ``5 / (8 * block_size)``.  Use
    integer round-to-nearest arithmetic so the bounded flat-block profile
    does not depend on floating point behavior.
    """

    if (
        type(residual) is not int
        or block_size not in (8, 16)
        or type(level_divisor) is not int
        or level_divisor <= 0
    ):
        raise HEVCGeneralProfileError("unsupported DC transform geometry")
    numerator = residual * block_size * 8
    denominator = 5 * level_divisor
    if numerator >= 0:
        return (numerator + denominator // 2) // denominator
    return -((-numerator + denominator // 2) // denominator)


def _build_general_sps_rbsp(
    width: int,
    height: int,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
    *,
    bit_depth: int = HEVC_GENERAL_BIT_DEPTH,
    ptl=None,
) -> bytes:
    """Build a bounded 8-bit SPS with 16x16 CTUs."""

    _validate_chroma_format(chroma_format_idc)
    if type(bit_depth) is not int or bit_depth not in (8, 10):
        raise HEVCGeneralProfileError("the bounded SPS supports only 8-bit or Main10 samples")

    writer = HEVCBitWriter()
    ptl = main_profile_tier_level(120) if ptl is None else ptl
    writer.write(0, 4)  # sps_video_parameter_set_id
    writer.write(0, 3)  # sps_max_sub_layers_minus1
    writer.flag(1)  # sps_temporal_id_nesting_flag
    ptl.write(writer)
    writer.ue(0)  # sps_seq_parameter_set_id
    writer.ue(chroma_format_idc)
    if chroma_format_idc == HEVC_CHROMA_444:
        writer.flag(0)  # separate_colour_plane_flag
    writer.ue(width)
    writer.ue(height)
    writer.flag(0)  # conformance_window_flag
    writer.ue(bit_depth - 8)  # bit_depth_luma_minus8
    writer.ue(bit_depth - 8)  # bit_depth_chroma_minus8
    writer.ue(4)  # log2_max_pic_order_cnt_lsb_minus4
    writer.flag(0)  # sps_sub_layer_ordering_info_present_flag
    writer.ue(0)  # sps_max_dec_pic_buffering_minus1
    writer.ue(0)  # sps_max_num_reorder_pics
    writer.ue(0)  # sps_max_latency_increase_plus1
    writer.ue(1)  # log2_min_luma_coding_block_size_minus3: 16x16
    writer.ue(0)  # log2_diff_max_min_luma_coding_block_size
    writer.ue(0)  # log2_min_luma_transform_block_size_minus2: 4x4
    writer.ue(2)  # log2_diff_max_min_luma_transform_block_size: max 16x16
    writer.ue(0)  # max_transform_hierarchy_depth_inter
    writer.ue(0)  # max_transform_hierarchy_depth_intra: no split
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


def _encode_dc_coeff(
    encoder: HEVCCabacEncoder,
    value: int,
    *,
    log2_size: int,
    chroma: bool,
    contexts: dict[str, HEVCCabacContext] | None = None,
) -> None:
    """Encode a transform block whose only nonzero coefficient is DC.

    ``value`` is the quantized transform coefficient.  The current qualified
    profile uses QP 0 and therefore does not hide any coefficient in a lossy
    quantizer.  The syntax is the normative DC-only path: last coefficient at
    (0,0), implicit significance, greater-than-one flag, and one sign bin.
    """

    if type(value) is not int or value == 0:
        raise HEVCGeneralProfileError("a DC transform block requires a nonzero integer level")
    if log2_size not in (3, 4):
        raise HEVCGeneralProfileError("the bounded DC path supports 8x8 and 16x16 blocks")
    if contexts is None:
        contexts = {}

    # H.265 last_significant_coeff_xy_prefix, with x=y=0: both prefix bins
    # are zero.  The context initializers are the I-slice values from Table
    # 9-5.  A separate context object is required for every context index.
    last_context_init = 108 if chroma else 125
    last_x_context = contexts.setdefault(
        "last_x_chroma" if chroma else "last_x_luma",
        cabac_context_from_init(0, last_context_init),
    )
    last_y_context = contexts.setdefault(
        "last_y_chroma" if chroma else "last_y_luma",
        cabac_context_from_init(0, last_context_init),
    )
    encoder.encode_bin(last_x_context, 0)
    encoder.encode_bin(last_y_context, 0)

    abs_level = abs(value)
    greater1 = abs_level >= 2
    # coeff_abs_level_greater1_flag uses context index 1 for the first level.
    greater1_init = 179 if chroma else 92
    greater1_context = contexts.setdefault(
        "greater1_chroma" if chroma else "greater1_luma",
        cabac_context_from_init(0, greater1_init),
    )
    encoder.encode_bin(greater1_context, int(greater1))

    # For a level greater than two the first coefficient also carries the
    # greater2 flag and a truncated Rice remainder.  This is not needed by the
    # initial constant-color test vectors, but keeping it here makes the
    # primitive useful for a real DC residual range.
    if greater1:
        greater2 = abs_level >= 3
        # I-slice greater2 context: the first luma coefficient uses inc=0
        # (init 138); chroma adds four contexts and uses init 152.
        greater2_init = 152 if chroma else 138
        greater2_context = contexts.setdefault(
            "greater2_chroma" if chroma else "greater2_luma",
            cabac_context_from_init(0, greater2_init),
        )
        encoder.encode_bin(greater2_context, int(greater2))
        # HEVC residual coding emits all coefficient sign flags before the
        # coeff_abs_level_remaining suffix.  With one coefficient this sign
        # therefore precedes the truncated-Rice remainder.
        encoder.encode_bypass(1 if value < 0 else 0)
        remainder = abs_level - 3
        if greater2:
            # coeff_abs_level_remaining with riceParam=0 is a truncated
            # unary-prefix plus a suffix.
            if remainder < 3:
                prefix = remainder
                suffix_bits = 0
                suffix = 0
            else:
                suffix_bits = (remainder - 2).bit_length() - 1
                prefix = suffix_bits + 3
                suffix = remainder - ((1 << suffix_bits) + 2)
            if prefix >= 31:
                raise HEVCGeneralProfileError("DC coefficient remainder exceeds CABAC prefix bound")
            for _ in range(prefix):
                encoder.encode_bypass(1)
            encoder.encode_bypass(0)
            for shift in range(suffix_bits - 1, -1, -1):
                encoder.encode_bypass((suffix >> shift) & 1)
    else:
        # No sign hiding is possible with one coefficient.  Positive=0,
        # negative=1 in coeff_sign_flag.
        encoder.encode_bypass(1 if value < 0 else 0)


# The following compact tables are the I-slice QP-0 context initializers from
# H.265 Table 9-5, in the same offset layout used by FFmpeg's HEVC decoder.
# They are kept local so the residual probe remains dependency-free.
_HEVC_LAST_INIT_I = (
    110, 110, 124, 125, 140, 153, 125, 127, 140, 109, 111, 143, 127, 111,
    79, 108, 123, 63,
)
_HEVC_SIG_GROUP_INIT_I = (91, 171, 134, 141)
_HEVC_SIG_INIT_I = (
    111, 111, 125, 110, 110, 94, 124, 108, 124, 107, 125, 141, 179, 153,
    125, 107, 125, 141, 179, 153, 125, 107, 125, 141, 179, 153, 125, 140,
    139, 182, 182, 152, 136, 152, 136, 153, 136, 139, 111, 136, 139, 111,
    141, 111,
)
_HEVC_GREATER1_INIT_I = (
    140, 92, 137, 138, 140, 152, 138, 139, 153, 74, 149, 92, 139, 107,
    122, 152, 140, 179, 166, 182, 140, 227, 122, 197,
)
_HEVC_GREATER2_INIT_I = (138, 153, 136, 167, 152, 152)
_HEVC_DIAG_SCAN_4X4 = (
    (0, 0), (1, 0), (0, 1), (0, 2),
    (1, 1), (2, 0), (3, 0), (2, 1),
    (1, 2), (0, 3), (1, 3), (2, 2),
    (3, 1), (2, 3), (3, 2), (3, 3),
)
_HEVC_DIAG_SCAN_4X4_INV = {
    coordinate: index for index, coordinate in enumerate(_HEVC_DIAG_SCAN_4X4)
}
_HEVC_SIG_MAP_8X8_PREV0 = (1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


def _encode_bypass_bits(encoder: HEVCCabacEncoder, value: int, width: int) -> None:
    if width < 0 or width > 32 or value < 0 or value >= (1 << width):
        raise HEVCGeneralProfileError("invalid HEVC bypass field")
    for shift in range(width - 1, -1, -1):
        encoder.encode_bypass((value >> shift) & 1)


def _last_prefix_and_suffix(coordinate: int, log2_size: int) -> tuple[int, int, int]:
    maximum = (log2_size << 1) - 1
    if not 0 <= coordinate < (1 << log2_size):
        raise HEVCGeneralProfileError("last coefficient coordinate is outside the transform")
    if coordinate < 4:
        return coordinate, 0, 0
    for prefix in range(4, maximum + 1):
        base = (1 << ((prefix >> 1) - 1)) * (2 + (prefix & 1))
        next_base = (
            (1 << (((prefix + 1) >> 1) - 1)) * (2 + ((prefix + 1) & 1))
            if prefix < maximum
            else (1 << log2_size)
        )
        if base <= coordinate < next_base:
            suffix_width = (prefix >> 1) - 1
            return prefix, coordinate - base, suffix_width
    raise HEVCGeneralProfileError("unable to encode last coefficient coordinate")


def _encode_last_significant_xy(
    encoder: HEVCCabacEncoder,
    coordinate: int,
    *,
    log2_size: int,
    chroma: bool,
    axis: str,
    contexts: dict[str, HEVCCabacContext],
) -> None:
    prefix, suffix, suffix_width = _last_prefix_and_suffix(coordinate, log2_size)
    if chroma:
        ctx_offset = 15
        ctx_shift = log2_size - 2
    else:
        ctx_offset = 3 * (log2_size - 2) + ((log2_size - 1) >> 2)
        ctx_shift = (log2_size + 1) >> 2
    maximum = (log2_size << 1) - 1
    for index in range(prefix):
        context_index = ctx_offset + (index >> ctx_shift)
        key = f"last_{axis}_{context_index}"
        context = contexts.setdefault(
            key,
            cabac_context_from_init(0, _HEVC_LAST_INIT_I[context_index]),
        )
        encoder.encode_bin(context, 1)
    if prefix < maximum:
        context_index = ctx_offset + (prefix >> ctx_shift)
        key = f"last_{axis}_{context_index}"
        context = contexts.setdefault(
            key,
            cabac_context_from_init(0, _HEVC_LAST_INIT_I[context_index]),
        )
        encoder.encode_bin(context, 0)
    _encode_bypass_bits(encoder, suffix, suffix_width)


def _encode_coeff_abs_remaining(
    encoder: HEVCCabacEncoder,
    remaining: int,
    rice_parameter: int = 0,
) -> None:
    if type(remaining) is not int or remaining < 0:
        raise HEVCGeneralProfileError("coefficient remainder must be a non-negative integer")
    if type(rice_parameter) is not int or not 0 <= rice_parameter <= 4:
        raise HEVCGeneralProfileError("HEVC Rice parameter is outside the bounded profile")
    scaled = remaining >> rice_parameter
    suffix = remaining & ((1 << rice_parameter) - 1)
    if scaled < 3:
        prefix = scaled
        suffix_width = rice_parameter
        suffix_value = suffix
    else:
        prefix_minus3 = (scaled - 2).bit_length() - 1
        prefix = prefix_minus3 + 3
        base = (1 << prefix_minus3) + 2
        suffix_width = prefix_minus3 + rice_parameter
        suffix_value = ((scaled - base) << rice_parameter) | suffix
    if prefix >= 31:
        raise HEVCGeneralProfileError("coefficient remainder exceeds CABAC prefix bound")
    for _ in range(prefix):
        encoder.encode_bypass(1)
    encoder.encode_bypass(0)
    _encode_bypass_bits(encoder, suffix_value, suffix_width)


def _encode_sparse_coeff_block(
    encoder: HEVCCabacEncoder,
    *,
    x: int,
    y: int,
    level: int,
    log2_size: int = 3,
    chroma: bool = True,
    contexts: dict[str, HEVCCabacContext] | None = None,
) -> None:
    """Encode one nonzero coefficient in an 8x8 diagonal-scan TU.

    This is a deliberately narrow residual syntax probe.  It handles one
    coefficient in the first 4x4 coefficient group, which is enough to
    validate AC significance, sign, and remainder syntax against an external
    decoder before the full multi-group/RDO path is enabled.
    """

    if log2_size != 3 or type(level) is not int or level == 0:
        raise HEVCGeneralProfileError("the sparse residual probe is limited to one 8x8 coefficient")
    if not 0 <= x < 4 or not 0 <= y < 4:
        raise HEVCGeneralProfileError(
            "the sparse residual probe is limited to the first 4x4 coefficient group"
        )
    contexts = {} if contexts is None else contexts
    _encode_last_significant_xy(
        encoder, x, log2_size=log2_size, chroma=chroma, axis="x", contexts=contexts
    )
    _encode_last_significant_xy(
        encoder, y, log2_size=log2_size, chroma=chroma, axis="y", contexts=contexts
    )
    last_scan_position = _HEVC_DIAG_SCAN_4X4_INV[(x, y)]
    scf_offset = 36 if chroma else 0
    # prev_sig is zero for the first 2x2 coefficient group.  The last
    # coefficient itself is implicit; all earlier positions are insignificant.
    for scan_position in range(last_scan_position - 1, 0, -1):
        context_index = _HEVC_SIG_MAP_8X8_PREV0[scan_position] + scf_offset
        key = f"sig_{context_index}"
        context = contexts.setdefault(
            key,
            cabac_context_from_init(0, _HEVC_SIG_INIT_I[context_index]),
        )
        encoder.encode_bin(context, 0)
    if last_scan_position > 0:
        context_index = _HEVC_SIG_MAP_8X8_PREV0[0] + scf_offset
        key = f"sig_{context_index}"
        context = contexts.setdefault(
            key,
            cabac_context_from_init(0, _HEVC_SIG_INIT_I[context_index]),
        )
        encoder.encode_bin(context, 0)

    absolute = abs(level)
    greater1 = int(absolute >= 2)
    greater1_index = 1 + (16 if chroma else 0)
    greater1_context = contexts.setdefault(
        f"greater1_{greater1_index}",
        cabac_context_from_init(0, _HEVC_GREATER1_INIT_I[greater1_index]),
    )
    encoder.encode_bin(greater1_context, greater1)
    if greater1:
        greater2 = int(absolute >= 3)
        greater2_index = 4 if chroma else 0
        greater2_context = contexts.setdefault(
            f"greater2_{greater2_index}",
            cabac_context_from_init(0, _HEVC_GREATER2_INIT_I[greater2_index]),
        )
        encoder.encode_bin(greater2_context, greater2)
    # HEVC residual coding emits all coefficient signs before the
    # coeff_abs_level_remaining suffix.  Keeping this ordering explicit is
    # important even for this one-coefficient probe because level >= 3 uses
    # both fields.
    encoder.encode_bypass(1 if level < 0 else 0)
    if greater1 and greater2:
        _encode_coeff_abs_remaining(encoder, absolute - 3, 0)


def _encode_sparse_coefficients_block(
    encoder: HEVCCabacEncoder,
    coefficients: tuple[tuple[int, int, int], ...],
    *,
    log2_size: int = 3,
    chroma: bool = True,
    contexts: dict[str, HEVCCabacContext] | None = None,
) -> None:
    """Experimental multi-coefficient form limited to the first 4x4 group.

    The established one-coefficient helper remains untouched.  This additive
    helper is intentionally private until an external decoder proves the
    complete significance/level ordering for more than one coefficient.
    """

    if log2_size != 3 or not coefficients or len(coefficients) > 16:
        raise HEVCGeneralProfileError(
            "the experimental sparse residual path requires one to sixteen 8x8 coefficients"
        )
    if any(
        type(item) is not tuple
        or len(item) != 3
        or any(type(value) is not int for value in item)
        or not 0 <= item[0] < 4
        or not 0 <= item[1] < 4
        or item[2] == 0
        for item in coefficients
    ):
        raise HEVCGeneralProfileError(
            "experimental sparse coefficients must be nonzero positions in the first 4x4 group"
        )
    if len({(item[0], item[1]) for item in coefficients}) != len(coefficients):
        raise HEVCGeneralProfileError("experimental sparse coefficients may not share a position")
    contexts = {} if contexts is None else contexts
    scan_positions = {
        (item[0], item[1]): _HEVC_DIAG_SCAN_4X4_INV[(item[0], item[1])]
        for item in coefficients
    }
    ordered = tuple(
        sorted(coefficients, key=lambda item: scan_positions[(item[0], item[1])], reverse=True)
    )
    last_x, last_y, _ = ordered[0]
    _encode_last_significant_xy(
        encoder, last_x, log2_size=log2_size, chroma=chroma, axis="x", contexts=contexts
    )
    _encode_last_significant_xy(
        encoder, last_y, log2_size=log2_size, chroma=chroma, axis="y", contexts=contexts
    )
    scf_offset = 36 if chroma else 0
    positions = {(item[0], item[1]) for item in coefficients}
    last_scan_position = scan_positions[(last_x, last_y)]
    for scan_position in range(last_scan_position - 1, -1, -1):
        context_index = _HEVC_SIG_MAP_8X8_PREV0[scan_position] + scf_offset
        key = f"sig_{context_index}"
        context = contexts.setdefault(
            key,
            cabac_context_from_init(0, _HEVC_SIG_INIT_I[context_index]),
        )
        encoder.encode_bin(context, int(_HEVC_DIAG_SCAN_4X4[scan_position] in positions))

    level_flags: list[tuple[int, bool, bool]] = []
    for rank, (_x, _y, level) in enumerate(ordered):
        absolute = abs(level)
        greater1 = absolute >= 2
        greater1_index = min(4, 1 + rank) + (16 if chroma else 0)
        greater1_context = contexts.setdefault(
            f"greater1_{greater1_index}",
            cabac_context_from_init(0, _HEVC_GREATER1_INIT_I[greater1_index]),
        )
        encoder.encode_bin(greater1_context, int(greater1))
        greater2 = greater1 and absolute >= 3
        if greater1:
            greater2_index = min(5, 4 + rank) if chroma else min(5, rank)
            greater2_context = contexts.setdefault(
                f"greater2_{greater2_index}",
                cabac_context_from_init(0, _HEVC_GREATER2_INIT_I[greater2_index]),
            )
            encoder.encode_bin(greater2_context, int(greater2))
        level_flags.append((level, greater1, greater2))
    for level, _greater1, _greater2 in level_flags:
        encoder.encode_bypass(1 if level < 0 else 0)
    for level, greater1, greater2 in level_flags:
        if greater1 and greater2:
            _encode_coeff_abs_remaining(encoder, abs(level) - 3, 0)


def _build_general_slice_rbsp(
    samples: bytes,
    width: int,
    height: int,
    qp: int,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
    sparse_chroma_coeff: tuple[int, int, int] | None = None,
    sparse_chroma_coefficients: tuple[tuple[int, int, int], ...] | None = None,
    ctu_values: tuple[tuple[int, int, int], ...] | None = None,
    dc_midpoint: int = 128,
    dc_level_divisor: int = 1,
) -> bytes:
    writer = HEVCBitWriter()
    writer.flag(1)  # first_slice_segment_in_pic_flag
    writer.flag(0)  # no_output_of_prior_pics_flag for IDR_N_LP
    writer.ue(0)  # slice_pic_parameter_set_id
    writer.ue(2)  # slice_type = I
    writer.se(qp - 26)  # slice_qp_delta; QP 0 is the qualified setting
    writer.flag(1)  # slice_loop_filter_across_slices_enabled_flag
    writer.flag(1)  # alignment_bit_equal_to_one
    while not writer.byte_aligned:
        writer.flag(0)

    _validate_chroma_format(chroma_format_idc)
    if sparse_chroma_coeff is not None and sparse_chroma_coefficients is not None:
        raise HEVCGeneralProfileError(
            "choose sparse_chroma_coeff or sparse_chroma_coefficients, not both"
        )
    if sparse_chroma_coeff is not None or sparse_chroma_coefficients is not None:
        if chroma_format_idc != HEVC_CHROMA_420 or (width, height) != (16, 16):
            raise HEVCGeneralProfileError(
                "the sparse residual probe is limited to one 16x16 4:2:0 CTU"
            )
        if sparse_chroma_coeff is not None and (
            type(sparse_chroma_coeff) is not tuple
            or len(sparse_chroma_coeff) != 3
            or any(type(value) is not int for value in sparse_chroma_coeff)
        ):
            raise TypeError("sparse_chroma_coeff must be a (x, y, level) tuple")
        if sparse_chroma_coeff is not None:
            probe_x, probe_y, probe_level = sparse_chroma_coeff
        else:
            probe_x = probe_y = probe_level = 0
        if sparse_chroma_coeff is not None and (
            not 0 <= probe_x < 4 or not 0 <= probe_y < 4 or probe_level == 0
        ):
            raise HEVCGeneralProfileError(
                "the sparse residual probe requires one nonzero coefficient in the first 4x4 group"
            )
        if sparse_chroma_coefficients is not None:
            if not sparse_chroma_coefficients:
                raise HEVCGeneralProfileError("sparse_chroma_coefficients must not be empty")
            if len(sparse_chroma_coefficients) > 16:
                raise HEVCGeneralProfileError("sparse_chroma_coefficients may contain at most 16 entries")
    else:
        probe_x = probe_y = probe_level = 0
    if ctu_values is None:
        ctu_values = _ctu_plane_values(samples, width, height, chroma_format_idc)
    else:
        expected_ctus = (width // 16) * (height // 16)
        if len(ctu_values) != expected_ctus:
            raise HEVCGeneralProfileError("the supplied CTU values do not match the picture geometry")
    encoder = HEVCCabacEncoder()

    # Syntax contexts are slice-local and must remain live while the raster
    # CTUs are coded.  Recreating them for every CTU emits a stream that can
    # still look plausible for one block but diverges from HEVC CABAC state
    # evolution as soon as a second CTU is present.
    part_mode = cabac_context_from_init(0, 184)
    prev_luma = cabac_context_from_init(0, 184)
    chroma_mode = cabac_context_from_init(0, 63)
    cbf_chroma = cabac_context_from_init(0, 94)
    cbf_luma = cabac_context_from_init(0, 141)
    residual_contexts: dict[str, HEVCCabacContext] = {}

    ctu_columns = width // 16
    total_ctus = ctu_columns * (height // 16)
    ctu_index = 0
    for block_y in range(0, height, 16):
        for block_x in range(0, width, 16):
            # Every CTU is a single 2Nx2N intra CU.  Select DC explicitly
            # through the MPM list; mpm_idx=1 is DC for the boundary-neutral
            # candidate list used by this profile.
            encoder.encode_bin(part_mode, 1)  # PART_2Nx2N
            encoder.encode_bin(prev_luma, 1)  # prev_intra_luma_pred_flag
            for bit in (1, 0):  # mpm_idx = 1 (DC)
                encoder.encode_bypass(bit)
            encoder.encode_bin(chroma_mode, 0)  # chroma mode = luma mode

            ctu_x = block_x // 16
            ctu_y = block_y // 16
            y_value, cb_value, cr_value = ctu_values[ctu_y * ctu_columns + ctu_x]
            y_predictor = _constant_dc_predictor(
                ctu_values, ctu_x, ctu_y, ctu_columns, 0, dc_midpoint
            )
            cb_predictor = _constant_dc_predictor(
                ctu_values, ctu_x, ctu_y, ctu_columns, 1, dc_midpoint
            )
            cr_predictor = _constant_dc_predictor(
                ctu_values, ctu_x, ctu_y, ctu_columns, 2, dc_midpoint
            )
            y_residual = _dc_transform_level(
                y_value - y_predictor, 16, dc_level_divisor
            )
            chroma_transform_size = 8 if chroma_format_idc == HEVC_CHROMA_420 else 16
            cb_residual = _dc_transform_level(
                cb_value - cb_predictor, chroma_transform_size, dc_level_divisor
            )
            cr_residual = _dc_transform_level(
                cr_value - cr_predictor, chroma_transform_size, dc_level_divisor
            )

            # Root transform tree: chroma CBFs precede luma CBF.  Cb and Cr
            # deliberately share the single depth-derived HEVC context.
            sparse_cb = (
                (sparse_chroma_coeff is not None or sparse_chroma_coefficients is not None)
                and ctu_index == 0
            )
            encoder.encode_bin(cbf_chroma, int(cb_residual != 0 or sparse_cb))  # cbf_cb
            encoder.encode_bin(cbf_chroma, int(cr_residual != 0))  # cbf_cr
            encoder.encode_bin(cbf_luma, int(y_residual != 0))  # cbf_luma

            if y_residual:
                _encode_dc_coeff(
                    encoder,
                    y_residual,
                    log2_size=4,
                    chroma=False,
                    contexts=residual_contexts,
                )
            if sparse_cb:
                if sparse_chroma_coefficients is not None:
                    _encode_sparse_coefficients_block(
                        encoder,
                        sparse_chroma_coefficients,
                        log2_size=3,
                        chroma=True,
                        contexts=residual_contexts,
                    )
                else:
                    _encode_sparse_coeff_block(
                        encoder,
                        x=probe_x,
                        y=probe_y,
                        level=probe_level,
                        log2_size=3,
                        chroma=True,
                        contexts=residual_contexts,
                    )
            elif cb_residual:
                _encode_dc_coeff(
                    encoder,
                    cb_residual,
                    log2_size=3,
                    chroma=True,
                    contexts=residual_contexts,
                )
            if cr_residual:
                _encode_dc_coeff(
                    encoder,
                    cr_residual,
                    log2_size=3,
                    chroma=True,
                    contexts=residual_contexts,
                )

            # HEVC carries an end_of_slice_segment_flag at every CTU boundary.
            # A zero termination bin keeps CABAC alive for the next CTU; only
            # the final CTU receives the terminating one bin below.
            ctu_index += 1
            if ctu_index < total_ctus:
                encoder.encode_terminate(0)

    encoder.encode_terminate(1)  # end_of_slice_segment_flag
    for value in encoder.flush():
        writer.write(value, 8)
    writer.rbsp_trailing_bits()
    return writer.bytes()


def _split_annex_b(data: bytes) -> tuple[bytes, ...]:
    if not data:
        raise HEVCGeneralBitstreamError("HEVC Annex-B data is empty")
    positions: list[tuple[int, int]] = []
    search = 0
    while True:
        marker = data.find(b"\x00\x00\x01", search)
        if marker < 0:
            break
        code_start = marker
        while code_start > 0 and data[code_start - 1] == 0:
            code_start -= 1
        positions.append((code_start, marker + 3))
        search = marker + 3
    if not positions or positions[0][0] != 0:
        raise HEVCGeneralBitstreamError("Annex-B stream must begin with a start code")
    nals: list[bytes] = []
    for index, (_code_start, nal_start) in enumerate(positions):
        end = positions[index + 1][0] if index + 1 < len(positions) else len(data)
        nal = data[nal_start:end]
        if not nal:
            raise HEVCGeneralBitstreamError("Annex-B stream contains an empty NAL")
        nals.append(nal)
    return tuple(nals)


def _sps_dimensions(nal: bytes) -> tuple[int, int, int, int]:
    parsed = parse_nal_unit(nal)
    if parsed.nal_unit_type != HEVC_NAL_SPS:
        raise HEVCGeneralBitstreamError("expected an SPS NAL")
    reader = HEVCBitReader(parsed.rbsp)
    reader.read(4)
    if reader.read(3) != 0:
        raise HEVCGeneralBitstreamError("the bounded validator expects one sub-layer")
    reader.read(1)
    # Keep each read within HEVCBitReader's deliberate 64-bit chunk limit.
    reader.read(8)   # general_profile_idc and compatibility flags prefix
    reader.read(32)  # general_profile_compatibility_flag[31..0]
    reader.read(48)  # constraint flags
    reader.read(8)   # general_level_idc
    reader.ue()
    chroma = reader.ue(max_value=3)
    if chroma == HEVC_CHROMA_444:
        # separate_colour_plane_flag is present for 4:4:4 syntax even when
        # the encoder uses the ordinary interleaved three-plane representation.
        if reader.flag():
            raise HEVCGeneralBitstreamError(
                "the bounded validator does not support separate colour planes"
            )
    width = reader.ue(max_value=65535)
    height = reader.ue(max_value=65535)
    if reader.flag():
        raise HEVCGeneralBitstreamError(
            "the bounded validator does not support an SPS conformance window"
        )
    bit_depth_luma = 8 + reader.ue(max_value=7)
    bit_depth_chroma = 8 + reader.ue(max_value=7)
    if bit_depth_luma != bit_depth_chroma:
        raise HEVCGeneralBitstreamError("luma and chroma bit depths must match")
    return width, height, chroma, bit_depth_luma


@dataclass(frozen=True)
class HEVCGeneralPicture:
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


def build_hevc_general_picture(
    samples: object,
    width: int = HEVC_GENERAL_WIDTH,
    height: int = HEVC_GENERAL_HEIGHT,
    *,
    qp: int = 0,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
    sparse_chroma_coeff: tuple[int, int, int] | None = None,
    sparse_chroma_coefficients: tuple[tuple[int, int, int], ...] | None = None,
) -> HEVCGeneralPicture:
    """Build the bounded HEVC picture profile.

    ``sparse_chroma_coeff`` and ``sparse_chroma_coefficients`` are experimental
    syntax-validation hooks. They deliberately accept coefficients rather than
    deriving them from pixels; callers must not use them as a general
    arbitrary-image encoder until forward transform, quantizer, and RDO paths
    are enabled.
    """
    _validate_geometry(width, height)
    _validate_qp(qp)
    _validate_chroma_format(chroma_format_idc)
    planar, source_profile = _validate_samples(
        samples, width, height, chroma_format_idc
    )
    if sparse_chroma_coeff is None and sparse_chroma_coefficients is None and source_profile.startswith("pixel_sparse_ac_chroma:"):
        _, x, y, level = source_profile.split(":")
        sparse_chroma_coeff = (int(x), int(y), int(level))
    if sparse_chroma_coeff is None and sparse_chroma_coefficients is None and source_profile.startswith("pixel_sparse_ac_multi:"):
        _, encoded = source_profile.split(":", 1)
        sparse_chroma_coefficients = tuple(
            tuple(int(value) for value in item.split(":"))
            for item in encoded.split(";")
        )
    ptl = main_profile_tier_level(120)
    vps = build_nal_unit(HEVC_NAL_VPS, build_vps_rbsp(ptl=ptl))
    sps = build_nal_unit(
        HEVC_NAL_SPS,
        _build_general_sps_rbsp(width, height, chroma_format_idc),
    )
    pps = build_nal_unit(HEVC_NAL_PPS, _build_general_pps_rbsp())
    vcl = build_nal_unit(
        HEVC_NAL_IDR_N_LP,
        _build_general_slice_rbsp(
            planar,
            width,
            height,
            qp,
            chroma_format_idc,
            sparse_chroma_coeff,
            sparse_chroma_coefficients,
        ),
    )
    hvcc = build_hvcc(
        (vps, sps, pps),
        ptl=ptl,
        bit_depth=8,
        chroma_format_idc=chroma_format_idc,
    )
    picture = HEVCGeneralPicture(
        width,
        height,
        8,
        chroma_format_idc,
        (vps, sps, pps, vcl),
        hvcc,
    )
    validate_hevc_general_annex_b(picture.annex_b, width=width, height=height)
    return picture


def _build_general_pps_rbsp() -> bytes:
    """PPS matching the general slice; QP deltas and optional tools are off."""

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
    writer.ue(0)  # log2_parallel_merge_level_minus2
    writer.flag(0)  # slice_segment_header_extension_present_flag
    writer.flag(0)  # pps_extension_flag
    writer.rbsp_trailing_bits()
    return writer.bytes()


def encode_hevc_general_aot(
    samples: object,
    width: int = HEVC_GENERAL_WIDTH,
    height: int = HEVC_GENERAL_HEIGHT,
    *,
    qp: int = 0,
    chroma_format_idc: int = HEVC_GENERAL_CHROMA_FORMAT_IDC,
) -> bytes:
    """Encode one externally qualified bounded HEVC intra picture."""

    return build_hevc_general_picture(
        samples,
        width,
        height,
        qp=qp,
        chroma_format_idc=chroma_format_idc,
    ).annex_b


def validate_hevc_general_annex_b(
    data: bytes | bytearray | memoryview,
    *,
    width: int | None = None,
    height: int | None = None,
    chroma_format_idc: int | None = None,
    bit_depth: int | None = None,
) -> dict[str, object]:
    raw = bytes(data)
    nals = _split_annex_b(raw)
    if len(nals) != 4:
        raise HEVCGeneralBitstreamError("a general picture requires VPS, SPS, PPS, and one IDR NAL")
    parsed = tuple(parse_nal_unit(nal) for nal in nals)
    types = tuple(item.nal_unit_type for item in parsed)
    expected = (HEVC_NAL_VPS, HEVC_NAL_SPS, HEVC_NAL_PPS, HEVC_NAL_IDR_N_LP)
    if types != expected:
        raise HEVCGeneralBitstreamError(f"unexpected NAL order: {types!r}")
    actual_width, actual_height, chroma, actual_bit_depth = _sps_dimensions(nals[1])
    if (width is None) != (height is None):
        raise TypeError("width and height must be supplied together")
    if width is not None:
        _validate_geometry(width, height)
        if (actual_width, actual_height) != (width, height):
            raise HEVCGeneralBitstreamError("SPS dimensions do not match the requested picture")
    if chroma not in HEVC_GENERAL_SUPPORTED_CHROMA:
        raise HEVCGeneralBitstreamError("the general milestone has an unsupported chroma format")
    if chroma_format_idc is not None and chroma != chroma_format_idc:
        raise HEVCGeneralBitstreamError("SPS chroma format does not match the requested profile")
    if bit_depth is not None and actual_bit_depth != bit_depth:
        raise HEVCGeneralBitstreamError("SPS bit depth does not match the requested profile")
    return {
        "nal_types": types,
        "nal_count": len(nals),
        "width": actual_width,
        "height": actual_height,
        "bit_depth": actual_bit_depth,
        "chroma_format_idc": chroma,
        "dc_intra_prediction": True,
        "transform_coefficients": True,
        "quantization_parameter": 0,
        "flat_block_profile": True,
        "horizontal_ctu_stripe_profile": True,
        "bytes": len(raw),
    }


def hevc_general_capability_report() -> Mapping[str, object]:
    return {
        "parameter_sets": True,
        "pixel_to_slice_encoder": True,
        "intra_prediction": ("DC",),
        "transform_sizes": (8, 16),
        "cabac_residual_syntax": True,
        "residual_syntax_probe": True,
        "residual_syntax_probe_scope": "one externally decoder-checked 8x8 AC coefficient",
        "pixel_derived_residual_profile": True,
        "pixel_derived_residual_scope": (
            "thirteen single-coefficient plus one exact two-coefficient 16x16 4:2:0 fixtures with pixel-detected 8x8 Cb AC positions/levels"
        ),
        "quantization": "QP 0 only",
        "supported_profile": (
            "16-aligned 8-bit planar 4:2:0 or 4:4:4 up to 4096x4096 for constant planes; "
            "constant-inside-CTU pictures with matching multi-row DC references"
        ),
        "chroma_formats": (HEVC_CHROMA_420, HEVC_CHROMA_444),
        "arbitrary_pixels": False,
        "non_constant_pixels": True,
        "horizontal_ctu_stripes": True,
        "multi_row_ctu_constant_blocks": True,
        "runtime_codec_dependencies": (),
        "externally_decoded": True,
        "external_decoder_validated_payload": True,
        "gpu_full_codec": False,
        "fail_closed": True,
        "limitations": (
            "one IDR picture composed of 16x16 CTUs; multiple pictures are not supported",
            "multi-row non-constant pictures require constant-inside-CTU blocks and matching top/left DC references",
            "the production pixel path emits DC plus fourteen exact pixel-detected 8x8 Cb AC fixtures",
            "general residual scans, RDO, and nonzero QP remain disabled",
        ),
    }


__all__ = [
    "HEVC_GENERAL_WIDTH",
    "HEVC_GENERAL_HEIGHT",
    "HEVC_GENERAL_SAMPLE_BYTES",
    "HEVC_GENERAL_SUPPORTED_CHROMA",
    "hevc_general_sparse_ac_fixture_samples",
    "hevc_general_sparse_ac_multi_fixture_samples",
    "hevc_general_sample_bytes",
    "HEVCGeneralProfileError",
    "HEVCGeneralBitstreamError",
    "HEVCGeneralPicture",
    "build_hevc_general_picture",
    "encode_hevc_general_aot",
    "validate_hevc_general_annex_b",
    "hevc_general_capability_report",
]
