"""Native AVIF item/container layer around a validated AV1 payload."""
from __future__ import annotations

import os
from pathlib import Path

from .av1_aot import validate_av1_image_payload
from .isobmff import box, colr_nclx, ftyp, full_box, iinf, iloc, iprp, ispe, parse_boxes, pitm, pixi


def _handler() -> bytes:
    return full_box("hdlr", 0, 0, b"\x00\x00\x00\x00pict" + b"\x00" * 12 + b"Pixel Refine\x00")


def _validate_native_av1_payload(payload: bytes, width: int, height: int, bit_depth: int, codec_config: bytes | None = None):
    """Accept only the externally validated native AV1 profiles.

    The original neutral 16x16 fixture remains compatible.  The bounded
    palette profile adds 26 other constant I420 frames without opening the
    container API to arbitrary third-party AV1 payloads.
    """

    try:
        return validate_av1_image_payload(
            payload,
            width,
            height,
            bit_depth=bit_depth,
            codec_config=codec_config,
            require_native_payload=True,
        )
    except ValueError as original_error:
        if (int(width), int(height), int(bit_depth)) != (16, 16, 8):
            raise
        from .av1_intra_aot import supported_constant_colors, validate_av1_intra_payload

        for y, cb, cr in supported_constant_colors():
            try:
                validate_av1_intra_payload(payload, y, cb, cr)
            except ValueError:
                continue
            return validate_av1_image_payload(
                payload,
                width,
                height,
                bit_depth=bit_depth,
                codec_config=codec_config,
                require_native_payload=False,
            )
        raise original_error


def build_avif_payload(payload: bytes, width: int, height: int, *, bit_depth: int = 8, codec_config: bytes = b"\x81\x00\x00\x00", metadata: dict | None = None) -> bytes:
    """Package a single AV1 item; ``payload`` must be a valid AV1 sequence."""
    payload = bytes(payload)
    if not payload:
        raise ValueError("AVIF item payload must not be empty")
    if not codec_config:
        raise ValueError("av1C configuration is required")
    if len(codec_config) < 4:
        raise ValueError("av1C configuration must contain four bytes")
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("AVIF metadata must be a mapping")
    # The historical default is a four-byte placeholder that did not carry
    # the chroma flags of the actual sequence.  Keep the call signature and
    # positional behavior intact, but derive a matching record when that
    # exact legacy default is used.  Explicit non-default configurations must
    # match the sequence header and are rejected on any mismatch.
    legacy_default_config = codec_config == b"\x81\x00\x00\x00"
    info = _validate_native_av1_payload(
        payload,
        width,
        height,
        bit_depth,
        None if legacy_default_config else codec_config,
    )
    if legacy_default_config:
        codec_config = info.codec_configuration
    file_type = ftyp("avif", 0, ("mif1", "avif", "miaf"))
    properties = [
        ispe(width, height),
        pixi(bit_depth, info.sequence_header.num_planes),
        colr_nclx(full_range=bool(info.sequence_header.color_range)),
        box("av1C", bytes(codec_config)),
    ]
    meta_payload = _handler() + pitm(1) + iinf(1, "av01") + iloc(1, 0, len(payload)) + iprp(1, tuple(properties))
    meta = full_box("meta", 0, 0, meta_payload)
    extent_offset = len(file_type) + len(meta) + 8
    meta_payload = _handler() + pitm(1) + iinf(1, "av01") + iloc(1, extent_offset, len(payload)) + iprp(1, tuple(properties))
    meta = full_box("meta", 0, 0, meta_payload)
    if metadata:
        raise ValueError("AVIF metadata mapping is not enabled yet")
    return file_type + meta + box("mdat", payload)


def package_avif_aot(payload: bytes, width: int, height: int, bit_depth: int = 8, codec_config: bytes = b"\x81\x00\x00\x00") -> bytes:
    return build_avif_payload(payload, width, height, bit_depth=bit_depth, codec_config=codec_config)


def save_avif_aot(payload: bytes, path: str | os.PathLike[str], width: int, height: int, bit_depth: int = 8, codec_config: bytes = b"\x81\x00\x00\x00") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(package_avif_aot(payload, width, height, bit_depth, codec_config))
    temporary.replace(target)


def parse_avif_aot(data: bytes | bytearray | str | os.PathLike[str]):
    raw = Path(data).read_bytes() if isinstance(data, (str, os.PathLike)) else bytes(data)
    top = parse_boxes(raw)
    ftyp_box = next((item for item in top if item.type == b"ftyp"), None)
    meta_box = next((item for item in top if item.type == b"meta"), None)
    mdat_boxes = [item for item in top if item.type == b"mdat"]
    if ftyp_box is None or meta_box is None or len(mdat_boxes) != 1:
        raise ValueError("not an AVIF container")
    if len(ftyp_box.payload) < 8:
        raise ValueError("truncated AVIF file-type box")
    brands = [ftyp_box.payload[:4]] + [ftyp_box.payload[index:index + 4] for index in range(8, len(ftyp_box.payload), 4)]
    if not any(brand in {b"avif", b"mif1", b"miaf"} for brand in brands):
        raise ValueError("AVIF file-type brands are missing")
    if len(meta_box.payload) < 4:
        raise ValueError("truncated AVIF meta box")
    meta_children = parse_boxes(meta_box.payload[4:], max_depth=15)
    properties = []
    for item in meta_children:
        if item.type != b"iprp":
            continue
        for iprp_child in parse_boxes(item.payload, max_depth=14):
            if iprp_child.type == b"ipco":
                properties.extend(parse_boxes(iprp_child.payload, max_depth=13))
    ispe_property = next((item for item in properties if item.type == b"ispe"), None)
    pixi_property = next((item for item in properties if item.type == b"pixi"), None)
    av1c_property = next((item for item in properties if item.type == b"av1C"), None)
    if ispe_property is None or pixi_property is None or av1c_property is None:
        raise ValueError("AVIF image properties are incomplete")
    if len(ispe_property.payload) != 16 or ispe_property.payload[4:8] != b"\x00\x00\x00\x00":
        raise ValueError("invalid AVIF ispe property")
    width = int.from_bytes(ispe_property.payload[8:12], "big")
    height = int.from_bytes(ispe_property.payload[12:16], "big")
    if len(pixi_property.payload) < 6:
        raise ValueError("invalid AVIF pixi property")
    channels = pixi_property.payload[4]
    bit_depth = pixi_property.payload[5]
    if channels < 1 or len(pixi_property.payload) != 5 + channels:
        raise ValueError("invalid AVIF pixi channel list")
    if any(value != bit_depth for value in pixi_property.payload[5:]):
        raise ValueError("AVIF pixi channel depths must match in the constrained profile")
    _validate_native_av1_payload(
        mdat_boxes[0].payload,
        width,
        height,
        bit_depth=bit_depth,
        codec_config=av1c_property.payload,
    )
    return top


__all__ = ["build_avif_payload", "package_avif_aot", "save_avif_aot", "parse_avif_aot"]
