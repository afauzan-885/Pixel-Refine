"""Bounded AV1/AVIF bitstream primitives.

This module deliberately owns the part of an AV1 encoder that can be made
small, auditable, and dependency-free first: OBU framing, the reduced still
picture sequence header, the AV1 codec configuration record, and strict
validation of the one-item AVIF profile used by :mod:`avif_aot`.

It is important not to confuse this with a complete AV1 encoder.  AV1 tile
coding contains a range/arithmetic coder, adaptive CDF state, block
partitioning, intra prediction, transform selection, and coefficient coding.
Those pieces are not guessed here.  The generic assembly helpers are useful
for inspecting a separately qualified frame/tile payload, but the public
AVIF integration is stricter: it accepts only the decoder-qualified tiny
constant profile returned by ``encode_av1_tiny_constant``.  Unsupported or
malformed data is rejected rather than being packaged as an apparently valid
AVIF file.

The implementation uses only the Python standard library.  It is the
host-side variable-length companion to the numeric Taichi stages; no libaom,
dav1d, libavif, NumPy, or other codec runtime is imported.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


# AV1 OBU type values from the AV1 bitstream specification.
OBU_RESERVED = 0
OBU_SEQUENCE_HEADER = 1
OBU_TEMPORAL_DELIMITER = 2
OBU_FRAME_HEADER = 3
OBU_TILE_GROUP = 4
OBU_METADATA = 5
OBU_FRAME = 6
OBU_REDUNDANT_FRAME_HEADER = 7
OBU_TILE_LIST = 8
OBU_PADDING = 15

_MAX_DIMENSION = 1 << 16
_MAX_OBU_COUNT = 4096
_MAX_OBU_PAYLOAD = 256 * 1024 * 1024
_MAX_LEB128_BYTES = 8

# AV1 color-description constants used by color_config().  The default
# builder intentionally leaves the description absent so that the AVIF nclx
# property can describe the color space without creating a contradictory
# in-bitstream identity-matrix shortcut.
_CP_BT_709 = 1
_TC_SRGB = 13
_MC_IDENTITY = 0

# Decoder-qualified smoke profile.  These are the range-coded bytes for one
# 16x16, 8-bit, 4:2:0 frame with Y=Cb=Cr=128.  The bytes were generated once
# with an external encoder for validation and then decoded to an exact
# 384-byte YUV420 frame.  They are deliberately not presented as a general
# pixel encoder.
_TINY_CONSTANT_SEQUENCE = bytes.fromhex("18 0c ff da 00 80")
_TINY_CONSTANT_FRAME = bytes.fromhex("17 80 00 00 48 00 10 05")


class AV1Error(ValueError):
    """Base class for malformed or unsupported native AV1 profiles."""


class AV1MalformedError(AV1Error):
    """The byte stream violates a bounded AV1/OBU syntax invariant."""


class AV1UnsupportedProfileError(AV1Error):
    """The bytes are recognizable but outside the constrained profile."""


@dataclass(frozen=True)
class AV1StillProfile:
    """Parameters for the reduced-still sequence-header profile.

    This describes the sequence header only.  It does not fabricate a tile
    payload, because a tile payload is not a sequence-header field and cannot
    be made decoder-safe by padding arbitrary bytes into an OBU.
    """

    width: int
    height: int
    bit_depth: int = 8
    chroma: str = "420"
    seq_profile: int | None = None
    seq_level_idx: int = 0
    color_range: int = 1
    chroma_sample_position: int = 0
    color_description: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class AV1SequenceHeader:
    """Parsed fields required by the constrained AVIF image-item profile."""

    seq_profile: int
    seq_level_idx: int
    seq_tier: int
    still_picture: bool
    reduced_still_picture_header: bool
    width: int
    height: int
    frame_width_bits: int
    frame_height_bits: int
    use_128x128_superblock: bool
    enable_filter_intra: bool
    enable_intra_edge_filter: bool
    enable_superres: bool
    enable_cdef: bool
    enable_restoration: bool
    bit_depth: int
    high_bitdepth: bool
    twelve_bit: bool
    monochrome: bool
    num_planes: int
    color_range: int
    color_description_present: bool
    color_primaries: int
    transfer_characteristics: int
    matrix_coefficients: int
    subsampling_x: int
    subsampling_y: int
    chroma_sample_position: int
    separate_uv_delta_q: int
    film_grain_params_present: bool
    raw_payload: bytes = b""


@dataclass(frozen=True)
class AV1CodecConfiguration:
    """AV1CodecConfigurationRecord fields (the payload of an ``av1C`` box)."""

    seq_profile: int
    seq_level_idx: int
    seq_tier: int
    high_bitdepth: bool
    twelve_bit: bool
    monochrome: bool
    chroma_subsampling_x: int
    chroma_subsampling_y: int
    chroma_sample_position: int
    initial_presentation_delay: int | None
    config_obus: bytes = b""
    raw: bytes = b""

    @property
    def bit_depth(self) -> int:
        if not self.high_bitdepth:
            return 8
        if self.seq_profile == 2 and self.twelve_bit:
            return 12
        return 10


@dataclass(frozen=True)
class AV1OBU:
    """One parsed low-overhead AV1 OBU."""

    offset: int
    obu_type: int
    extension_flag: bool
    has_size_field: bool
    temporal_id: int
    spatial_id: int
    payload: bytes
    header_size: int
    size_field_size: int


@dataclass(frozen=True)
class AV1ImagePayloadInfo:
    """Structural result for a constrained one-item AVIF payload.

    ``structural_only`` is always true in this module.  The range-coded tile
    syntax is bounded by the OBU/container checks but is intentionally not
    decoded here.  A full production gate must additionally run an external
    decoder parity check over the exact pixel input.
    """

    sequence_header: AV1SequenceHeader
    obus: tuple[AV1OBU, ...]
    codec_configuration: bytes
    frame_obu_count: int
    frame_header_count: int
    tile_group_count: int
    structural_only: bool = True


class _BitWriter:
    __slots__ = ("_data", "_bits")

    def __init__(self) -> None:
        self._data = bytearray()
        self._bits = 0

    @property
    def bit_count(self) -> int:
        return len(self._data) * 8 + self._bits

    def write(self, value: int, width: int) -> None:
        value = int(value)
        width = int(width)
        if width < 0 or width > 64:
            raise ValueError("bit width is out of range")
        if width == 0:
            if value:
                raise ValueError("non-zero value does not fit zero bits")
            return
        if value < 0 or value >= (1 << width):
            raise ValueError("bit value does not fit requested width")
        for shift in range(width - 1, -1, -1):
            self._data.append(0) if self._bits == 0 else None
            if (value >> shift) & 1:
                self._data[-1] |= 1 << (7 - self._bits)
            self._bits = (self._bits + 1) & 7

    def trailing_bits(self) -> bytes:
        # AV1 trailing_bits() is a one followed by zeroes to the next byte.
        self.write(1, 1)
        while self._bits:
            self.write(0, 1)
        return bytes(self._data)


class _BitReader:
    __slots__ = ("_data", "_position")

    def __init__(self, data: bytes) -> None:
        self._data = bytes(data)
        self._position = 0

    @property
    def position(self) -> int:
        return self._position

    @property
    def remaining(self) -> int:
        return len(self._data) * 8 - self._position

    def read(self, width: int) -> int:
        width = int(width)
        if width < 0 or width > 64 or width > self.remaining:
            raise AV1MalformedError("AV1 bitstream underflow")
        value = 0
        for _ in range(width):
            byte_index, bit_index = divmod(self._position, 8)
            value = (value << 1) | ((self._data[byte_index] >> (7 - bit_index)) & 1)
            self._position += 1
        return value

    def trailing_bits(self) -> None:
        if self.remaining <= 0 or self.read(1) != 1:
            raise AV1MalformedError("AV1 trailing_one_bit is missing")
        while self.remaining:
            if self.read(1) != 0:
                raise AV1MalformedError("non-zero AV1 trailing padding")


def _require_int(name: str, value: int, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}]")
    return value


def _encode_leb128(value: int) -> bytes:
    value = _require_int("LEB128 value", value, 0, (1 << 56) - 1)
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _decode_leb128(data: memoryview, offset: int, end: int) -> tuple[int, int, int]:
    value = 0
    shift = 0
    for count in range(1, _MAX_LEB128_BYTES + 1):
        if offset >= end:
            raise AV1MalformedError("truncated AV1 LEB128 size")
        byte = int(data[offset])
        offset += 1
        value |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            # The AV1 syntax uses a bounded unsigned LEB128.  Refuse a
            # non-minimal spelling so a payload has one canonical framing.
            if count > 1 and value < (1 << (7 * (count - 1))):
                raise AV1MalformedError("non-canonical AV1 LEB128 size")
            return value, offset, count
        shift += 7
    raise AV1MalformedError("AV1 LEB128 size exceeds eight bytes")


def _canonical_chroma(chroma: str) -> str:
    if not isinstance(chroma, str):
        raise TypeError("chroma must be a string")
    value = chroma.strip().lower().replace(":", "")
    aliases = {
        "400": "400",
        "mono": "400",
        "monochrome": "400",
        "gray": "400",
        "420": "420",
        "yuv420": "420",
        "422": "422",
        "yuv422": "422",
        "444": "444",
        "yuv444": "444",
    }
    try:
        return aliases[value]
    except KeyError as exc:
        raise ValueError("chroma must be 400, 420, 422, or 444") from exc


def make_av1_still_profile(
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    chroma: str = "420",
    seq_profile: int | None = None,
    seq_level_idx: int = 0,
    color_range: int = 1,
    chroma_sample_position: int = 0,
    color_description: tuple[int, int, int] | None = None,
) -> AV1StillProfile:
    """Validate and return a reduced-still AV1 profile descriptor.

    The supported profile mapping follows AV1's profile/color-config rules:
    profile 0 for 4:2:0, profile 1 for 4:4:4, and profile 2 for 4:2:2.
    Profile 2 is also used for 12-bit 4:2:0/4:4:4.  This function constructs
    headers only; it never claims to encode pixels.
    """

    width = _require_int("width", width, 1, _MAX_DIMENSION)
    height = _require_int("height", height, 1, _MAX_DIMENSION)
    bit_depth = _require_int("bit_depth", bit_depth, 8, 12)
    if bit_depth not in (8, 10, 12):
        raise ValueError("AV1 bit_depth must be 8, 10, or 12")
    chroma = _canonical_chroma(chroma)
    seq_level_idx = _require_int("seq_level_idx", seq_level_idx, 0, 31)
    color_range = _require_int("color_range", color_range, 0, 1)
    chroma_sample_position = _require_int("chroma_sample_position", chroma_sample_position, 0, 3)
    if color_description is not None:
        if not isinstance(color_description, tuple) or len(color_description) != 3:
            raise TypeError("color_description must be a three-item tuple")
        color_description = tuple(
            _require_int("color description field", item, 0, 255) for item in color_description
        )
    if chroma == "400":
        inferred_profile = 2 if bit_depth == 12 else 0
    elif chroma == "420":
        inferred_profile = 0 if bit_depth <= 10 else 2
    elif chroma == "422":
        inferred_profile = 2
    else:
        inferred_profile = 1 if bit_depth <= 10 else 2
    if seq_profile is None:
        seq_profile = inferred_profile
    seq_profile = _require_int("seq_profile", seq_profile, 0, 2)
    if seq_profile != inferred_profile:
        raise AV1UnsupportedProfileError(
            f"profile {seq_profile} is incompatible with {bit_depth}-bit {chroma}"
        )
    if seq_profile == 1 and chroma == "400":
        raise AV1UnsupportedProfileError("AV1 profile 1 cannot signal monochrome")
    if bit_depth == 12 and seq_profile != 2:
        raise AV1UnsupportedProfileError("12-bit AV1 requires profile 2")
    return AV1StillProfile(
        width=width,
        height=height,
        bit_depth=bit_depth,
        chroma=chroma,
        seq_profile=seq_profile,
        seq_level_idx=seq_level_idx,
        color_range=color_range,
        chroma_sample_position=chroma_sample_position,
        color_description=color_description,
    )


def _profile_from_header_fields(header: AV1SequenceHeader) -> AV1StillProfile:
    if header.monochrome:
        chroma = "400"
    elif header.subsampling_x and header.subsampling_y:
        chroma = "420"
    elif header.subsampling_x:
        chroma = "422"
    else:
        chroma = "444"
    description = None
    if header.color_description_present:
        description = (
            header.color_primaries,
            header.transfer_characteristics,
            header.matrix_coefficients,
        )
    return AV1StillProfile(
        width=header.width,
        height=header.height,
        bit_depth=header.bit_depth,
        chroma=chroma,
        seq_profile=header.seq_profile,
        seq_level_idx=header.seq_level_idx,
        color_range=header.color_range,
        chroma_sample_position=header.chroma_sample_position,
        color_description=description,
    )


def build_sequence_header(profile: AV1StillProfile) -> bytes:
    """Serialize a reduced-still sequence-header payload (without OBU header)."""

    if not isinstance(profile, AV1StillProfile):
        raise TypeError("profile must be an AV1StillProfile")
    checked = make_av1_still_profile(
        profile.width,
        profile.height,
        bit_depth=profile.bit_depth,
        chroma=profile.chroma,
        seq_profile=profile.seq_profile,
        seq_level_idx=profile.seq_level_idx,
        color_range=profile.color_range,
        chroma_sample_position=profile.chroma_sample_position,
        color_description=profile.color_description,
    )
    width_bits = max(1, (checked.width - 1).bit_length())
    height_bits = max(1, (checked.height - 1).bit_length())
    if width_bits > 16 or height_bits > 16:
        raise ValueError("AV1 sequence-header dimensions exceed 16-bit field widths")
    writer = _BitWriter()
    writer.write(checked.seq_profile, 3)
    writer.write(1, 1)  # still_picture
    writer.write(1, 1)  # reduced_still_picture_header
    writer.write(checked.seq_level_idx, 5)
    writer.write(width_bits - 1, 4)
    writer.write(height_bits - 1, 4)
    writer.write(checked.width - 1, width_bits)
    writer.write(checked.height - 1, height_bits)
    writer.write(0, 1)  # use_128x128_superblock
    writer.write(0, 1)  # enable_filter_intra
    writer.write(0, 1)  # enable_intra_edge_filter
    # The reduced-still syntax infers the inter tools and order-hint fields.
    writer.write(0, 1)  # enable_superres
    writer.write(0, 1)  # enable_cdef
    writer.write(0, 1)  # enable_restoration

    high_bitdepth = int(checked.bit_depth > 8)
    writer.write(high_bitdepth, 1)
    if checked.seq_profile == 2 and high_bitdepth:
        writer.write(int(checked.bit_depth == 12), 1)
    if checked.seq_profile == 1:
        monochrome = 0
    else:
        monochrome = int(checked.chroma == "400")
        writer.write(monochrome, 1)

    description = checked.color_description
    writer.write(int(description is not None), 1)
    if description is not None:
        writer.write(description[0], 8)
        writer.write(description[1], 8)
        writer.write(description[2], 8)

    if monochrome:
        writer.write(checked.color_range, 1)
    else:
        # The identity-matrix shortcut infers full-range 4:4:4.  It is only
        # valid for the 4:4:4 profile, so reject contradictory combinations.
        identity_shortcut = description == (_CP_BT_709, _TC_SRGB, _MC_IDENTITY)
        if identity_shortcut:
            if checked.chroma != "444" or checked.color_range != 1:
                raise AV1UnsupportedProfileError(
                    "identity color description requires full-range 4:4:4"
                )
        else:
            writer.write(checked.color_range, 1)
            if checked.chroma == "420":
                subsampling_x, subsampling_y = 1, 1
            elif checked.chroma == "422":
                subsampling_x, subsampling_y = 1, 0
            else:
                subsampling_x, subsampling_y = 0, 0
            if checked.seq_profile == 2 and checked.bit_depth == 12:
                writer.write(subsampling_x, 1)
                if subsampling_x:
                    writer.write(subsampling_y, 1)
            elif checked.seq_profile == 0:
                # Profile 0 is constrained to 4:2:0.
                if (subsampling_x, subsampling_y) != (1, 1):
                    raise AV1UnsupportedProfileError("profile 0 requires 4:2:0")
            elif checked.seq_profile == 1:
                if (subsampling_x, subsampling_y) != (0, 0):
                    raise AV1UnsupportedProfileError("profile 1 requires 4:4:4")
            else:
                # Profile 2 at 8/10 bits is 4:2:2.
                if (subsampling_x, subsampling_y) != (1, 0):
                    raise AV1UnsupportedProfileError("8/10-bit profile 2 requires 4:2:2")
            if subsampling_x and subsampling_y:
                writer.write(checked.chroma_sample_position, 2)
    if not monochrome:
        writer.write(0, 1)  # separate_uv_delta_q
    writer.write(0, 1)  # film_grain_params_present
    return writer.trailing_bits()


def parse_sequence_header(payload: bytes | bytearray | memoryview) -> AV1SequenceHeader:
    """Parse and strictly validate the reduced-still sequence header payload."""

    raw = bytes(payload)
    if not raw:
        raise AV1MalformedError("empty AV1 sequence-header payload")
    reader = _BitReader(raw)
    seq_profile = reader.read(3)
    still_picture = bool(reader.read(1))
    reduced = bool(reader.read(1))
    if seq_profile > 2:
        raise AV1UnsupportedProfileError("reserved AV1 sequence profile")
    if not reduced:
        raise AV1UnsupportedProfileError(
            "only reduced_still_picture_header AV1 sequences are accepted"
        )
    if not still_picture:
        raise AV1MalformedError("reduced AV1 header requires still_picture=1")
    seq_level_idx = reader.read(5)
    seq_tier = 0
    frame_width_bits = reader.read(4) + 1
    frame_height_bits = reader.read(4) + 1
    width = reader.read(frame_width_bits) + 1
    height = reader.read(frame_height_bits) + 1
    if width > _MAX_DIMENSION or height > _MAX_DIMENSION:
        raise AV1UnsupportedProfileError("AV1 dimensions exceed the constrained profile")
    use_128 = bool(reader.read(1))
    enable_filter_intra = bool(reader.read(1))
    enable_intra_edge_filter = bool(reader.read(1))
    enable_superres = bool(reader.read(1))
    enable_cdef = bool(reader.read(1))
    enable_restoration = bool(reader.read(1))

    high_bitdepth = bool(reader.read(1))
    if seq_profile == 2 and high_bitdepth:
        twelve_bit = bool(reader.read(1))
        bit_depth = 12 if twelve_bit else 10
    else:
        twelve_bit = False
        bit_depth = 10 if high_bitdepth else 8
    if seq_profile == 1:
        monochrome = False
    else:
        monochrome = bool(reader.read(1))
    num_planes = 1 if monochrome else 3

    color_description_present = bool(reader.read(1))
    if color_description_present:
        color_primaries = reader.read(8)
        transfer_characteristics = reader.read(8)
        matrix_coefficients = reader.read(8)
    else:
        color_primaries = 2
        transfer_characteristics = 2
        matrix_coefficients = 2

    if monochrome:
        color_range = reader.read(1)
        subsampling_x, subsampling_y = 1, 1
        chroma_sample_position = 0
        separate_uv_delta_q = 0
    elif (
        color_primaries == _CP_BT_709
        and transfer_characteristics == _TC_SRGB
        and matrix_coefficients == _MC_IDENTITY
    ):
        color_range = 1
        subsampling_x, subsampling_y = 0, 0
        chroma_sample_position = 0
        separate_uv_delta_q = reader.read(1)
    else:
        color_range = reader.read(1)
        if seq_profile == 0:
            subsampling_x, subsampling_y = 1, 1
        elif seq_profile == 1:
            subsampling_x, subsampling_y = 0, 0
        elif bit_depth == 12:
            subsampling_x = reader.read(1)
            subsampling_y = reader.read(1) if subsampling_x else 0
        else:
            subsampling_x, subsampling_y = 1, 0
        chroma_sample_position = reader.read(2) if subsampling_x and subsampling_y else 0
        separate_uv_delta_q = reader.read(1)
    film_grain_params_present = bool(reader.read(1))
    reader.trailing_bits()

    if seq_profile == 0 and not monochrome and (subsampling_x, subsampling_y) != (1, 1):
        raise AV1MalformedError("profile 0 must be 4:2:0")
    if seq_profile == 1 and monochrome:
        raise AV1MalformedError("profile 1 cannot signal monochrome")
    if seq_profile == 1 and (subsampling_x, subsampling_y) != (0, 0):
        raise AV1MalformedError("profile 1 must be 4:4:4")
    if seq_profile == 2 and bit_depth <= 10 and not monochrome and (subsampling_x, subsampling_y) != (1, 0):
        raise AV1MalformedError("8/10-bit profile 2 must be 4:2:2")
    return AV1SequenceHeader(
        seq_profile=seq_profile,
        seq_level_idx=seq_level_idx,
        seq_tier=seq_tier,
        still_picture=still_picture,
        reduced_still_picture_header=reduced,
        width=width,
        height=height,
        frame_width_bits=frame_width_bits,
        frame_height_bits=frame_height_bits,
        use_128x128_superblock=use_128,
        enable_filter_intra=enable_filter_intra,
        enable_intra_edge_filter=enable_intra_edge_filter,
        enable_superres=enable_superres,
        enable_cdef=enable_cdef,
        enable_restoration=enable_restoration,
        bit_depth=bit_depth,
        high_bitdepth=high_bitdepth,
        twelve_bit=twelve_bit,
        monochrome=monochrome,
        num_planes=num_planes,
        color_range=color_range,
        color_description_present=color_description_present,
        color_primaries=color_primaries,
        transfer_characteristics=transfer_characteristics,
        matrix_coefficients=matrix_coefficients,
        subsampling_x=subsampling_x,
        subsampling_y=subsampling_y,
        chroma_sample_position=chroma_sample_position,
        separate_uv_delta_q=separate_uv_delta_q,
        film_grain_params_present=film_grain_params_present,
        raw_payload=raw,
    )


def build_obu(
    obu_type: int,
    payload: bytes | bytearray | memoryview = b"",
    *,
    temporal_id: int = 0,
    spatial_id: int = 0,
    extension: bool = False,
    has_size_field: bool = True,
) -> bytes:
    """Build one canonical low-overhead OBU."""

    obu_type = _require_int("obu_type", obu_type, 1, 15)
    if obu_type in {OBU_RESERVED, *range(9, 15)}:
        raise AV1UnsupportedProfileError("reserved AV1 OBU type")
    temporal_id = _require_int("temporal_id", temporal_id, 0, 7)
    spatial_id = _require_int("spatial_id", spatial_id, 0, 3)
    raw = bytes(payload)
    if len(raw) > _MAX_OBU_PAYLOAD:
        raise ValueError("AV1 OBU payload exceeds the safety limit")
    if not has_size_field and obu_type != OBU_PADDING:
        raise AV1UnsupportedProfileError("the constrained writer always uses OBU size fields")
    header = (obu_type << 3) | (int(bool(extension)) << 2) | (int(bool(has_size_field)) << 1)
    out = bytearray((header,))
    if extension:
        out.append((temporal_id << 5) | (spatial_id << 3))
    if has_size_field:
        out.extend(_encode_leb128(len(raw)))
    out.extend(raw)
    return bytes(out)


def build_sequence_header_obu(profile: AV1StillProfile) -> bytes:
    """Build a sequence-header OBU for ``profile``."""

    return build_obu(OBU_SEQUENCE_HEADER, build_sequence_header(profile))


def encode_av1_tiny_constant(
    *,
    width: int = 16,
    height: int = 16,
    bit_depth: int = 8,
    chroma: str = "420",
    y: int = 128,
    cb: int = 128,
    cr: int = 128,
) -> bytes:
    """Return the only native pixel profile currently qualified.

    This is intentionally a tiny constant-frame encoder, not a general AV1
    image encoder.  It accepts exactly one 16x16 8-bit 4:2:0 constant frame.
    Rejecting every other input prevents the AVIF layer from treating an
    arbitrary opaque tile range as an image.
    """

    if (width, height, bit_depth, _canonical_chroma(chroma)) != (16, 16, 8, "420"):
        raise AV1UnsupportedProfileError(
            "the qualified native AV1 profile is limited to a 16x16 8-bit 4:2:0 frame"
        )
    for name, value in (("y", y), ("cb", cb), ("cr", cr)):
        _require_int(name, value, 0, 255)
        if value != 128:
            raise AV1UnsupportedProfileError(
                "the qualified native AV1 profile is limited to Y=Cb=Cr=128"
            )
    payload = (
        build_obu(OBU_TEMPORAL_DELIMITER)
        + build_obu(OBU_SEQUENCE_HEADER, _TINY_CONSTANT_SEQUENCE)
        + build_obu(OBU_FRAME, _TINY_CONSTANT_FRAME)
    )
    # Structural validation is still useful here, but the exact-profile gate
    # in the AVIF integration is what prevents other opaque payloads.
    validate_av1_image_payload(payload, 16, 16, bit_depth=8)
    return payload


def parse_obus(
    data: bytes | bytearray | memoryview,
    *,
    max_obus: int = _MAX_OBU_COUNT,
    max_payload: int = _MAX_OBU_PAYLOAD,
    allow_last_without_size: bool = False,
) -> tuple[AV1OBU, ...]:
    """Parse low-overhead OBUs with bounded, canonical framing checks."""

    raw = memoryview(bytes(data))
    max_obus = _require_int("max_obus", max_obus, 1, _MAX_OBU_COUNT)
    max_payload = _require_int("max_payload", max_payload, 1, _MAX_OBU_PAYLOAD)
    result: list[AV1OBU] = []
    offset = 0
    while offset < len(raw):
        if len(result) >= max_obus:
            raise AV1MalformedError("AV1 OBU count exceeds the safety limit")
        start = offset
        header = int(raw[offset])
        offset += 1
        if header & 0x80:
            raise AV1MalformedError("AV1 OBU forbidden bit is set")
        obu_type = (header >> 3) & 0x0F
        extension_flag = bool((header >> 2) & 1)
        has_size_field = bool((header >> 1) & 1)
        if header & 1:
            raise AV1MalformedError("AV1 OBU reserved bit is set")
        if obu_type == OBU_RESERVED or 9 <= obu_type <= 14:
            raise AV1UnsupportedProfileError(f"reserved AV1 OBU type {obu_type}")
        temporal_id = spatial_id = 0
        header_size = 1
        if extension_flag:
            if offset >= len(raw):
                raise AV1MalformedError("truncated AV1 OBU extension header")
            extension = int(raw[offset])
            offset += 1
            header_size += 1
            if extension & 0x07:
                raise AV1MalformedError("AV1 OBU extension reserved bits are set")
            temporal_id = extension >> 5
            spatial_id = (extension >> 3) & 0x03
        size_field_size = 0
        if has_size_field:
            payload_size, offset, size_field_size = _decode_leb128(raw, offset, len(raw))
            if payload_size > max_payload:
                raise AV1MalformedError("AV1 OBU payload exceeds the safety limit")
            end = offset + payload_size
            if end > len(raw):
                raise AV1MalformedError("AV1 OBU payload extends beyond the input")
        else:
            if not allow_last_without_size or offset >= len(raw):
                raise AV1UnsupportedProfileError(
                    "OBU size-less framing is disabled for the constrained profile"
                )
            end = len(raw)
        payload = bytes(raw[offset:end])
        if obu_type == OBU_TEMPORAL_DELIMITER and payload:
            raise AV1MalformedError("temporal delimiter OBU must have an empty payload")
        result.append(
            AV1OBU(
                offset=start,
                obu_type=obu_type,
                extension_flag=extension_flag,
                has_size_field=has_size_field,
                temporal_id=temporal_id,
                spatial_id=spatial_id,
                payload=payload,
                header_size=header_size,
                size_field_size=size_field_size,
            )
        )
        offset = end
        if not has_size_field:
            break
    if offset != len(raw):
        raise AV1MalformedError("trailing bytes after AV1 OBU sequence")
    return tuple(result)


def parse_av1c(data: bytes | bytearray | memoryview) -> AV1CodecConfiguration:
    """Parse an AV1CodecConfigurationRecord (without the ``av1C`` box header)."""

    raw = bytes(data)
    if len(raw) < 4:
        raise AV1MalformedError("truncated AV1CodecConfigurationRecord")
    first, second, third, fourth = raw[:4]
    if (first >> 7) != 1 or (first & 0x7F) != 1:
        raise AV1MalformedError("unsupported AV1CodecConfigurationRecord marker/version")
    seq_profile = second >> 5
    seq_level_idx = second & 0x1F
    if seq_profile > 2:
        raise AV1UnsupportedProfileError("reserved AV1 codec configuration profile")
    if fourth & 0xE0:
        raise AV1MalformedError("AV1CodecConfigurationRecord reserved bits are set")
    initial_present = bool((fourth >> 4) & 1)
    initial_delay = (fourth & 0x0F) if initial_present else None
    if not initial_present and (fourth & 0x0F):
        raise AV1MalformedError("AV1CodecConfigurationRecord reserved bits are set")
    configuration = AV1CodecConfiguration(
        seq_profile=seq_profile,
        seq_level_idx=seq_level_idx,
        seq_tier=(third >> 7) & 1,
        high_bitdepth=bool((third >> 6) & 1),
        twelve_bit=bool((third >> 5) & 1),
        monochrome=bool((third >> 4) & 1),
        chroma_subsampling_x=(third >> 3) & 1,
        chroma_subsampling_y=(third >> 2) & 1,
        chroma_sample_position=third & 0x03,
        initial_presentation_delay=initial_delay,
        config_obus=raw[4:],
        raw=raw,
    )
    if configuration.twelve_bit and not configuration.high_bitdepth:
        raise AV1MalformedError("AV1 twelve_bit requires high_bitdepth")
    if configuration.config_obus:
        config_obus = parse_obus(configuration.config_obus)
        if any(item.obu_type == OBU_SEQUENCE_HEADER for item in config_obus):
            raise AV1UnsupportedProfileError(
                "sequence headers in av1C configOBUs are not used by this AVIF profile"
            )
    return configuration


def build_av1c(
    sequence: AV1SequenceHeader | AV1StillProfile,
    *,
    config_obus: bytes = b"",
    initial_presentation_delay: int | None = None,
) -> bytes:
    """Build the four-byte AV1CodecConfigurationRecord prefix and config OBUs."""

    if isinstance(sequence, AV1StillProfile):
        sequence = parse_sequence_header(build_sequence_header(sequence))
    if not isinstance(sequence, AV1SequenceHeader):
        raise TypeError("sequence must be an AV1SequenceHeader or AV1StillProfile")
    if initial_presentation_delay is not None:
        initial_presentation_delay = _require_int(
            "initial_presentation_delay", initial_presentation_delay, 0, 15
        )
    config_obus = bytes(config_obus)
    if config_obus:
        parsed = parse_obus(config_obus)
        if any(item.obu_type == OBU_SEQUENCE_HEADER for item in parsed):
            raise AV1UnsupportedProfileError(
                "sequence headers in av1C configOBUs are disabled for one-item AVIF"
            )
    first = 0x81
    second = (sequence.seq_profile << 5) | sequence.seq_level_idx
    third = (
        (sequence.seq_tier << 7)
        | (int(sequence.high_bitdepth) << 6)
        | (int(sequence.twelve_bit) << 5)
        | (int(sequence.monochrome) << 4)
        | (int(sequence.subsampling_x) << 3)
        | (int(sequence.subsampling_y) << 2)
        | sequence.chroma_sample_position
    )
    fourth = 0 if initial_presentation_delay is None else 0x10 | initial_presentation_delay
    return bytes((first, second, third, fourth)) + config_obus


def assemble_av1_still_payload(
    profile: AV1StillProfile | AV1SequenceHeader,
    frame_payload: bytes | bytearray | memoryview,
    *,
    frame_obu_type: int = OBU_FRAME,
) -> bytes:
    """Assemble a sequence header and an already-coded frame OBU.

    ``frame_payload`` is the complete payload of an ``OBU_FRAME`` (or an
    ``OBU_FRAME_HEADER`` when using the explicit header/tile-group form).  It
    is intentionally not interpreted as raw pixels.  The returned bytes are
    passed through the same fail-closed structural validator used by AVIF.
    """

    if isinstance(profile, AV1SequenceHeader):
        profile = _profile_from_header_fields(profile)
    if not isinstance(profile, AV1StillProfile):
        raise TypeError("profile must be an AV1StillProfile or AV1SequenceHeader")
    if frame_obu_type not in {OBU_FRAME, OBU_FRAME_HEADER}:
        raise ValueError("frame_obu_type must be OBU_FRAME or OBU_FRAME_HEADER")
    frame = bytes(frame_payload)
    if not frame:
        raise AV1MalformedError("coded AV1 frame payload must not be empty")
    result = build_sequence_header_obu(profile) + build_obu(frame_obu_type, frame)
    # A separate frame header must be followed by a tile group.  The combined
    # OBU form contains both structures and is the default.
    if frame_obu_type == OBU_FRAME_HEADER:
        raise AV1UnsupportedProfileError(
            "explicit frame-header assembly requires a separately coded tile group; "
            "use assemble_av1_obus for that form"
        )
    validate_av1_image_payload(
        result,
        profile.width,
        profile.height,
        bit_depth=profile.bit_depth,
    )
    return result


def assemble_av1_obus(
    profile: AV1StillProfile | AV1SequenceHeader,
    frame_header_payload: bytes,
    tile_group_payloads: Iterable[bytes],
) -> bytes:
    """Assemble the explicit frame-header/tile-group OBU form.

    Only one tile group is accepted in the constrained one-item profile.  A
    caller that needs multiple tiles must first add a fully qualified tile
    parser and profile; silently concatenating opaque ranges would be unsafe.
    """

    if isinstance(profile, AV1SequenceHeader):
        profile = _profile_from_header_fields(profile)
    if not isinstance(profile, AV1StillProfile):
        raise TypeError("profile must be an AV1StillProfile or AV1SequenceHeader")
    groups = tuple(bytes(item) for item in tile_group_payloads)
    if len(groups) != 1 or not groups[0]:
        raise AV1UnsupportedProfileError("the constrained profile requires exactly one tile group")
    if not frame_header_payload:
        raise AV1MalformedError("coded AV1 frame-header payload must not be empty")
    result = (
        build_sequence_header_obu(profile)
        + build_obu(OBU_FRAME_HEADER, frame_header_payload)
        + build_obu(OBU_TILE_GROUP, groups[0])
    )
    validate_av1_image_payload(
        result,
        profile.width,
        profile.height,
        bit_depth=profile.bit_depth,
    )
    return result


def _check_codec_configuration(
    sequence: AV1SequenceHeader,
    codec_config: bytes | bytearray | memoryview | None,
) -> bytes:
    derived = build_av1c(sequence)
    if codec_config is None:
        return derived
    raw = bytes(codec_config)
    config = parse_av1c(raw)
    expected = (
        sequence.seq_profile,
        sequence.seq_level_idx,
        sequence.seq_tier,
        sequence.high_bitdepth,
        sequence.twelve_bit,
        sequence.monochrome,
        sequence.subsampling_x,
        sequence.subsampling_y,
        sequence.chroma_sample_position,
    )
    actual = (
        config.seq_profile,
        config.seq_level_idx,
        config.seq_tier,
        config.high_bitdepth,
        config.twelve_bit,
        config.monochrome,
        config.chroma_subsampling_x,
        config.chroma_subsampling_y,
        config.chroma_sample_position,
    )
    if actual != expected:
        raise AV1MalformedError("av1C configuration does not match the sequence header")
    return raw


def validate_av1_image_payload(
    payload: bytes | bytearray | memoryview,
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    codec_config: bytes | bytearray | memoryview | None = None,
    max_obus: int = 64,
    require_native_payload: bool = False,
) -> AV1ImagePayloadInfo:
    """Fail-closed validation for the native one-item AVIF AV1 profile.

    Accepted structure:

    ``sequence_header OBU, frame OBU``

    or the explicit form:

    ``sequence_header OBU, frame_header OBU, one tile_group OBU``.

    Metadata, temporal delimiters, extensions, redundant headers, tile lists,
    reserved OBUs, multiple frames, and size-less framing are rejected.  The
    frame/tile payload is treated as opaque range-coded data; therefore this
    result is structural validation, not a substitute for decoder parity.  A
    caller packaging an AVIF through the native integration must additionally
    pass ``require_native_payload=True``; at present that gate admits only the
    decoder-qualified tiny constant profile returned by
    :func:`encode_av1_tiny_constant`.
    """

    width = _require_int("width", width, 1, _MAX_DIMENSION)
    height = _require_int("height", height, 1, _MAX_DIMENSION)
    bit_depth = _require_int("bit_depth", bit_depth, 8, 12)
    if bit_depth not in (8, 10, 12):
        raise ValueError("AV1 bit_depth must be 8, 10, or 12")
    obus = parse_obus(payload, max_obus=max_obus, allow_last_without_size=False)
    if not obus:
        raise AV1MalformedError("AV1 image payload contains no OBUs")
    if any(item.extension_flag or not item.has_size_field for item in obus):
        raise AV1UnsupportedProfileError("constrained AVIF OBUs cannot use extensions or size-less framing")
    # AV1 low-overhead samples commonly begin with one empty temporal
    # delimiter.  AVIF recommends omitting it, but does not make its presence
    # a reason to reinterpret the following valid sequence.  Permit exactly
    # that leading delimiter and reject delimiters elsewhere below.
    sequence_index = 0
    if obus[0].obu_type == OBU_TEMPORAL_DELIMITER:
        sequence_index = 1
    if sequence_index >= len(obus) or obus[sequence_index].obu_type != OBU_SEQUENCE_HEADER:
        raise AV1MalformedError("AVIF image payload must start with a sequence header OBU")
    sequence_count = sum(item.obu_type == OBU_SEQUENCE_HEADER for item in obus)
    if sequence_count != 1:
        raise AV1MalformedError("one-item AVIF payload must contain exactly one sequence header")
    sequence = parse_sequence_header(obus[sequence_index].payload)
    if sequence.width != width or sequence.height != height:
        raise AV1MalformedError("AV1 sequence dimensions do not match AVIF ispe dimensions")
    if sequence.bit_depth != bit_depth:
        raise AV1MalformedError("AV1 sequence bit depth does not match AVIF pixi")

    allowed = {
        OBU_SEQUENCE_HEADER,
        OBU_TEMPORAL_DELIMITER,
        OBU_FRAME,
        OBU_FRAME_HEADER,
        OBU_TILE_GROUP,
    }
    if any(item.obu_type not in allowed for item in obus):
        raise AV1UnsupportedProfileError("OBU type is outside the constrained AVIF image-item profile")
    frame_obus = [item for item in obus if item.obu_type == OBU_FRAME]
    frame_headers = [item for item in obus if item.obu_type == OBU_FRAME_HEADER]
    tile_groups = [item for item in obus if item.obu_type == OBU_TILE_GROUP]
    if frame_obus and (frame_headers or tile_groups):
        raise AV1MalformedError("combined and explicit AV1 frame forms cannot be mixed")
    if len(frame_obus) == 1:
        if len(frame_obus[0].payload) < 2:
            raise AV1MalformedError("combined AV1 frame OBU has no frame/tile payload")
    elif len(frame_headers) == 1 and len(tile_groups) == 1:
        if obus.index(frame_headers[0]) > obus.index(tile_groups[0]):
            raise AV1MalformedError("AV1 tile group precedes its frame header")
        if not frame_headers[0].payload or not tile_groups[0].payload:
            raise AV1MalformedError("AV1 frame header/tile group payload must not be empty")
    else:
        raise AV1MalformedError(
            "one-item AVIF requires exactly one combined frame OBU or one frame-header/tile-group pair"
        )
    if any(item.obu_type == OBU_SEQUENCE_HEADER for item in obus[sequence_index + 1:]):
        raise AV1MalformedError("duplicate AV1 sequence header")
    if any(item.temporal_id or item.spatial_id for item in obus):
        raise AV1UnsupportedProfileError("layered AV1 OBUs are outside the constrained AVIF profile")
    delimiters = [index for index, item in enumerate(obus) if item.obu_type == OBU_TEMPORAL_DELIMITER]
    if delimiters and delimiters != [0]:
        raise AV1UnsupportedProfileError(
            "only one optional leading temporal delimiter is allowed in the constrained AVIF profile"
        )
    if require_native_payload:
        if (width, height, bit_depth) != (16, 16, 8) or bytes(payload) != encode_av1_tiny_constant():
            raise AV1UnsupportedProfileError(
                "no native AV1 pixel-to-tile encoder is qualified for this payload; "
                "AVIF packaging is restricted to encode_av1_tiny_constant()"
            )
    configuration = _check_codec_configuration(sequence, codec_config)
    return AV1ImagePayloadInfo(
        sequence_header=sequence,
        obus=obus,
        codec_configuration=configuration,
        frame_obu_count=len(frame_obus),
        frame_header_count=len(frame_headers),
        tile_group_count=len(tile_groups),
    )


def av1_image_payload_report(
    payload: bytes | bytearray | memoryview,
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    codec_config: bytes | bytearray | memoryview | None = None,
) -> Mapping[str, object]:
    """Return a serializable structural report, raising on invalid input."""

    info = validate_av1_image_payload(
        payload,
        width,
        height,
        bit_depth=bit_depth,
        codec_config=codec_config,
    )
    sequence = info.sequence_header
    return {
        "valid": True,
        "structural_only": info.structural_only,
        "width": sequence.width,
        "height": sequence.height,
        "bit_depth": sequence.bit_depth,
        "seq_profile": sequence.seq_profile,
        "chroma_subsampling": (
            "400" if sequence.monochrome else
            "420" if (sequence.subsampling_x and sequence.subsampling_y) else
            "422" if sequence.subsampling_x else "444"
        ),
        "obu_types": tuple(item.obu_type for item in info.obus),
        "frame_obu_count": info.frame_obu_count,
        "frame_header_count": info.frame_header_count,
        "tile_group_count": info.tile_group_count,
        "codec_configuration": info.codec_configuration,
    }


__all__ = [
    "AV1Error",
    "AV1MalformedError",
    "AV1UnsupportedProfileError",
    "AV1StillProfile",
    "AV1SequenceHeader",
    "AV1CodecConfiguration",
    "AV1OBU",
    "AV1ImagePayloadInfo",
    "OBU_SEQUENCE_HEADER",
    "OBU_TEMPORAL_DELIMITER",
    "OBU_FRAME_HEADER",
    "OBU_TILE_GROUP",
    "OBU_METADATA",
    "OBU_FRAME",
    "OBU_REDUNDANT_FRAME_HEADER",
    "OBU_TILE_LIST",
    "OBU_PADDING",
    "make_av1_still_profile",
    "build_sequence_header",
    "parse_sequence_header",
    "build_sequence_header_obu",
    "encode_av1_tiny_constant",
    "build_obu",
    "parse_obus",
    "parse_av1c",
    "build_av1c",
    "assemble_av1_still_payload",
    "assemble_av1_obus",
    "validate_av1_image_payload",
    "av1_image_payload_report",
]
