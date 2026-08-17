"""Native HEIF/HEIC item/container layer.

This module deliberately separates ISO-BMFF packaging from the HEVC intra
payload encoder.  It can package a validated HEVC payload today; the pixel to
HEVC encoder is implemented in subsequent milestones and must provide a
complete VPS/SPS/PPS + slice stream before the HEIC API is promoted.
"""
from __future__ import annotations

import os
from pathlib import Path

from .hevc_aot import parse_hvcc, parse_nal_unit
from .isobmff import box, colr_nclx, ftyp, full_box, iinf, iloc, iprp, parse_boxes, pitm, pixi


def _heif_ispe(width: int, height: int) -> bytes:
    """Build an ImageSpatialExtentsProperty with one FullBox header.

    Keep this HEIF-local for now: the shared ISO-BMFF helper is also consumed
    by AVIF, which is outside this change's authorized scope.
    """

    if not 1 <= width <= 0xFFFFFFFF or not 1 <= height <= 0xFFFFFFFF:
        raise ValueError("invalid HEIF image dimensions")
    return full_box(
        "ispe",
        0,
        0,
        width.to_bytes(4, "big") + height.to_bytes(4, "big"),
    )


def _handler() -> bytes:
    return full_box("hdlr", 0, 0, b"\x00\x00\x00\x00pict" + b"\x00" * 12 + b"Pixel Refine\x00")


def _hevc_nals_from_payload(payload: bytes, length_size: int) -> tuple[bytes, ...]:
    """Parse Annex-B or hvcC length-prefixed NAL units without decoding VCL."""
    # A length-prefixed item can legitimately contain an emulation-prevention
    # sequence in its NAL payload.  Only treat the data as Annex-B when the
    # first bytes are an actual start-code prefix; searching the whole item
    # misclassifies valid hvcC payloads whose SPS/slice happens to contain
    # 00 00 01 later in the stream.
    if payload.startswith(b"\x00\x00\x00\x01") or payload.startswith(b"\x00\x00\x01"):
        nals: list[bytes] = []
        cursor = 0
        while True:
            marker = payload.find(b"\x00\x00\x01", cursor)
            if marker < 0:
                break
            start = marker + 3
            if marker > 0 and payload[marker - 1] == 0:
                start = marker + 3
            next_marker = payload.find(b"\x00\x00\x01", start)
            end = len(payload) if next_marker < 0 else next_marker
            nal = payload[start:end].rstrip(b"\x00")
            if not nal:
                raise ValueError("HEVC Annex-B payload contains an empty NAL unit")
            parse_nal_unit(nal)
            nals.append(nal)
            if next_marker < 0:
                break
            cursor = next_marker
        if nals:
            return tuple(nals)
    if not 1 <= length_size <= 4:
        raise ValueError("HEVC hvcC length size is invalid")
    nals = []
    cursor = 0
    while cursor < len(payload):
        if cursor + length_size > len(payload):
            raise ValueError("truncated HEVC length-prefixed NAL unit")
        size = int.from_bytes(payload[cursor:cursor + length_size], "big")
        cursor += length_size
        if size < 2 or cursor + size > len(payload):
            raise ValueError("invalid HEVC length-prefixed NAL unit")
        nal = payload[cursor:cursor + size]
        cursor += size
        parse_nal_unit(nal)
        nals.append(nal)
    if not nals:
        raise ValueError("HEVC item payload contains no NAL units")
    return tuple(nals)


def _validate_hevc_item(payload: bytes, codec_config: bytes, bit_depth: int) -> None:
    try:
        config = parse_hvcc(codec_config)
        nal_types = set(config["nal_types"])
        if not {32, 33, 34}.issubset(nal_types):
            raise ValueError("hvcC must carry VPS, SPS, and PPS parameter sets")
        if int(config["bit_depth_luma"]) != bit_depth or int(config["bit_depth_chroma"]) != bit_depth:
            raise ValueError("HEIF pixi depth does not match hvcC bit depth")
        _hevc_nals_from_payload(payload, int(config["length_size_minus_one"]) + 1)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid HEVC item payload/configuration: {exc}") from exc


def build_heif_payload(payload: bytes, width: int, height: int, *, bit_depth: int = 8, codec: str = "hvc1", codec_config: bytes = b"", metadata: dict | None = None) -> bytes:
    """Package one already-encoded HEVC/HEIF item without third-party codecs."""
    payload = bytes(payload)
    if not payload:
        raise ValueError("HEIF item payload must not be empty")
    if codec not in {"hvc1", "unci"}:
        raise ValueError("HEIF codec must be hvc1 or unci")
    if codec == "hvc1" and not codec_config:
        raise ValueError("hvcC configuration is required for an HEVC item")
    if codec == "hvc1":
        _validate_hevc_item(payload, bytes(codec_config), bit_depth)
    if metadata is not None and not isinstance(metadata, dict):
        raise TypeError("HEIF metadata must be a mapping")
    brands = ("mif1", "heic", "hevc") if codec == "hvc1" else ("mif1", "heif")
    file_type = ftyp("heic" if codec == "hvc1" else "heif", 0, brands)
    properties = [_heif_ispe(width, height), pixi(bit_depth, 3), colr_nclx()]
    if codec == "hvc1":
        properties.append(box("hvcC", bytes(codec_config)))
    meta_payload = _handler() + pitm(1) + iinf(1, codec) + iloc(1, 0, len(payload)) + iprp(1, tuple(properties))
    meta = full_box("meta", 0, 0, meta_payload)
    extent_offset = len(file_type) + len(meta) + 8
    meta_payload = _handler() + pitm(1) + iinf(1, codec) + iloc(1, extent_offset, len(payload)) + iprp(1, tuple(properties))
    meta = full_box("meta", 0, 0, meta_payload)
    output = file_type + meta + box("mdat", payload)
    if metadata:
        # Metadata boxes are added only through explicit future item-property
        # adapters; silently discarding a caller's metadata would be unsafe.
        raise ValueError("HEIF metadata mapping is not enabled yet")
    return output


def package_heic_aot(payload: bytes, width: int, height: int, bit_depth: int = 8, codec_config: bytes = b"") -> bytes:
    return build_heif_payload(payload, width, height, bit_depth=bit_depth, codec="hvc1", codec_config=codec_config)


def package_heic_image_aot(
    samples: object,
    width: int,
    height: int,
    *,
    bit_depth: int = 8,
    chroma_format_idc: int = 1,
    mode: str = "auto",
) -> bytes:
    """Encode a planar HEIC image using the strongest qualified profile.

    ``auto`` selects the compressed DC-intra profile when its explicitly
    qualified constraints match the input and falls back to the arbitrary
    sample-exact I_PCM profile otherwise.  ``compressed`` fails closed when
    the input is outside the bounded residual profile; ``lossless`` always
    selects I_PCM.  The fallback is intentionally lossless and never silently
    changes pixel values or bit depth.
    """

    selected = str(mode).strip().lower().replace("-", "_")
    if selected not in {"auto", "compressed", "lossless"}:
        raise ValueError("HEIC mode must be auto, compressed, or lossless")
    if bit_depth == 8:
        if selected == "lossless":
            return package_heic_ipcm_aot(
                samples,
                width=width,
                height=height,
                chroma_format_idc=chroma_format_idc,
            )
        try:
            return package_heic_flat_aot(
                samples,
                width=width,
                height=height,
                chroma_format_idc=chroma_format_idc,
            )
        except Exception as exc:
            from .hevc_aot import HEVCProfileError

            if selected == "compressed" or not isinstance(exc, HEVCProfileError):
                raise
            return package_heic_ipcm_aot(
                samples,
                width=width,
                height=height,
                chroma_format_idc=chroma_format_idc,
            )
    if bit_depth == 10:
        if selected == "lossless":
            return package_heic_ipcm10_aot(samples, width=width, height=height)
        try:
            return package_heic_flat_aot(
                samples,
                width=width,
                height=height,
                chroma_format_idc=chroma_format_idc,
                bit_depth=10,
            )
        except Exception as exc:
            from .hevc_aot import HEVCProfileError

            if selected == "compressed" or not isinstance(exc, HEVCProfileError):
                raise
            if chroma_format_idc != 1:
                raise ValueError(
                    "lossless Main10 fallback currently supports only 4:2:0"
                ) from exc
            return package_heic_ipcm10_aot(samples, width=width, height=height)
    raise ValueError("HEIC bit_depth must be 8 or 10")


def package_heic_vcl_aot(samples: object = None) -> bytes:
    """Package the externally validated fixed 16x16 HEVC VCL profile.

    HEIF item data uses hvcC-length-prefixed NAL units.  The standalone VCL
    profile exposes Annex-B for stream validation, so this adapter performs
    only the standards-required NAL length conversion before containerizing.
    It remains intentionally bounded to the neutral 16x16 profile.
    """

    from .hevc_aot import build_hvcc
    from .hevc_vcl_aot import build_hevc_vcl_picture, encode_hevc_vcl_aot

    picture = build_hevc_vcl_picture()
    # Validate the caller's optional planar frame through the fixed encoder.
    encode_hevc_vcl_aot(samples)
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    codec_config = build_hvcc(picture.nals[:3])
    return package_heic_aot(payload, picture.width, picture.height, picture.bit_depth, codec_config)


def package_heic_ipcm_aot(
    samples: object,
    width: int = 16,
    height: int = 16,
    chroma_format_idc: int = 1,
) -> bytes:
    """Package the bounded, lossless multi-CTU HEVC I_PCM profile."""

    from .hevc_ipcm_aot import build_hevc_ipcm_picture

    picture = build_hevc_ipcm_picture(
        samples,
        width=width,
        height=height,
        chroma_format_idc=chroma_format_idc,
    )
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    return package_heic_aot(
        payload,
        picture.width,
        picture.height,
        picture.bit_depth,
        picture.hvcc,
    )


def package_heic_neutral_aot(
    samples: object = None,
    width: int = 16,
    height: int = 16,
) -> bytes:
    """Package the bounded CABAC/intra-compressed neutral HEVC profile.

    The profile is intentionally fail-closed: it accepts only an all-128
    planar 8-bit 4:2:0 frame.  It is useful as a real compressed HEVC seam,
    but it is not a general-purpose HEIC encoder.
    """

    from .hevc_neutral_aot import build_hevc_neutral_picture

    picture = build_hevc_neutral_picture(samples, width=width, height=height)
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    return package_heic_aot(
        payload,
        picture.width,
        picture.height,
        picture.bit_depth,
        picture.hvcc,
    )


def package_heic_flat_aot(
    samples: object,
    width: int = 16,
    height: int = 16,
    *,
    chroma_format_idc: int = 1,
    bit_depth: int = 8,
    sparse_chroma_coeff: tuple[int, int, int] | None = None,
    sparse_chroma_coefficients: tuple[tuple[int, int, int], ...] | None = None,
) -> bytes:
    """Package the backward-compatible bounded DC-only HEVC profile.

    The historical name remains public.  In addition to constant planes, the
    encoder now accepts externally qualified CTU-constant profiles, including
    one-row stripes and multi-row pictures with matching DC references.
    Use :func:`package_heic_ctu_stripes_aot` when selecting that profile
    explicitly.  ``sparse_chroma_coeff`` and ``sparse_chroma_coefficients`` are
    experimental AC syntax probes, not a general pixel-derived residual path.
    """

    if bit_depth == 10:
        if (
            chroma_format_idc != 1
            or sparse_chroma_coeff is not None
            or sparse_chroma_coefficients is not None
        ):
            raise ValueError("the bounded compressed Main10 profile supports only 4:2:0")
        from .hevc_general10_aot import build_hevc_general10_picture

        picture = build_hevc_general10_picture(samples, width=width, height=height)
    elif bit_depth == 8:
        from .hevc_general_aot import build_hevc_general_picture

        picture = build_hevc_general_picture(
            samples,
            width=width,
            height=height,
            chroma_format_idc=chroma_format_idc,
            sparse_chroma_coeff=sparse_chroma_coeff,
            sparse_chroma_coefficients=sparse_chroma_coefficients,
        )
    else:
        raise ValueError("the bounded compressed HEIC profile supports only 8-bit or 10-bit samples")
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    return package_heic_aot(
        payload,
        picture.width,
        picture.height,
        picture.bit_depth,
        picture.hvcc,
    )


def package_heic_ctu_stripes_aot(
    samples: object,
    width: int = 32,
    height: int = 16,
    *,
    chroma_format_idc: int = 1,
) -> bytes:
    """Package the bounded non-constant horizontal CTU-stripe HEVC profile.

    Every 16x16 luma CTU and corresponding format-aligned Cb/Cr block may
    carry an independent constant value.  The profile is deliberately one
    CTU high; arbitrary per-pixel AC residual coding remains fail-closed.
    """

    if height != 16:
        raise ValueError("the HEVC CTU-stripe HEIC profile must be 16 pixels high")
    from .hevc_general_aot import build_hevc_general_picture

    picture = build_hevc_general_picture(
        samples,
        width=width,
        height=height,
        chroma_format_idc=chroma_format_idc,
    )
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    return package_heic_aot(
        payload,
        picture.width,
        picture.height,
        picture.bit_depth,
        picture.hvcc,
    )


def package_heic_ipcm10_aot(
    samples: object,
    width: int = 16,
    height: int = 16,
) -> bytes:
    """Package the bounded lossless 10-bit Main10 4:2:0 I_PCM profile."""

    from .hevc_ipcm10_aot import build_hevc_ipcm10_picture

    picture = build_hevc_ipcm10_picture(samples, width=width, height=height)
    payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    return package_heic_aot(
        payload,
        picture.width,
        picture.height,
        picture.bit_depth,
        picture.hvcc,
    )


def heic_ipcm_capability_report():
    from .hevc_ipcm_aot import hevc_ipcm_capability_report

    report = dict(hevc_ipcm_capability_report())
    report.update({
        "heif_container": True,
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_neutral_capability_report():
    from .hevc_neutral_aot import hevc_neutral_capability_report

    report = dict(hevc_neutral_capability_report())
    report.update({
        "heif_container": True,
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_flat_capability_report():
    from .hevc_general_aot import hevc_general_capability_report

    report = dict(hevc_general_capability_report())
    report.update({
        "heif_container": True,
        "compressed_bit_depths": (8,),
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_flat10_capability_report():
    from .hevc_general10_aot import hevc_general10_capability_report

    report = dict(hevc_general10_capability_report())
    report.update({
        "heif_container": True,
        "compressed_bit_depths": (10,),
        "item_data_format": "hvcC-length-prefixed Main10 NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_ctu_stripes_capability_report():
    from .hevc_general_aot import hevc_general_capability_report

    report = dict(hevc_general_capability_report())
    report.update({
        "heif_container": True,
        "selected_profile": "horizontal_ctu_stripes",
        "multi_row_ctu_constant_blocks": bool(
            report.get("multi_row_ctu_constant_blocks", False)
        ),
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_ipcm10_capability_report():
    from .hevc_ipcm10_aot import hevc_ipcm10_capability_report

    report = dict(hevc_ipcm10_capability_report())
    report.update({
        "heif_container": True,
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def heic_vcl_capability_report():
    from .hevc_vcl_aot import hevc_vcl_capability_report

    report = dict(hevc_vcl_capability_report())
    report.update({
        "heif_container": True,
        "item_data_format": "hvcC-length-prefixed NAL units",
        "external_container_decoder_validation_required": True,
    })
    return report


def save_heic_aot(payload: bytes, path: str | os.PathLike[str], width: int, height: int, bit_depth: int = 8, codec_config: bytes = b"") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(package_heic_aot(payload, width, height, bit_depth, codec_config))
    temporary.replace(target)


def parse_heif_aot(data: bytes | bytearray | str | os.PathLike[str]):
    raw = Path(data).read_bytes() if isinstance(data, (str, os.PathLike)) else bytes(data)
    top = parse_boxes(raw)
    ftyp_box = next((item for item in top if item.type == b"ftyp"), None)
    meta_box = next((item for item in top if item.type == b"meta"), None)
    mdat_boxes = [item for item in top if item.type == b"mdat"]
    if ftyp_box is None or meta_box is None or not mdat_boxes:
        raise ValueError("not an HEIF/HEIC container")
    if len(ftyp_box.payload) < 8:
        raise ValueError("truncated HEIF file-type box")
    brands = [ftyp_box.payload[:4]] + [ftyp_box.payload[index:index + 4] for index in range(8, len(ftyp_box.payload), 4)]
    if not any(brand in {b"heic", b"heif", b"mif1"} for brand in brands):
        raise ValueError("HEIF file-type brands are missing")
    if len(meta_box.payload) < 4:
        raise ValueError("truncated HEIF meta box")
    meta_children = parse_boxes(meta_box.payload[4:], max_depth=15)
    hvc_properties = []
    for item in meta_children:
        if item.type != b"iprp":
            continue
        for iprp_child in parse_boxes(item.payload, max_depth=14):
            if iprp_child.type != b"ipco":
                continue
            hvc_properties.extend(
                child for child in parse_boxes(iprp_child.payload, max_depth=13)
                if child.type == b"hvcC"
            )
    if hvc_properties:
        config = parse_hvcc(hvc_properties[0].payload)
        if not {32, 33, 34}.issubset(set(config["nal_types"])):
            raise ValueError("HEIF hvcC is missing VPS/SPS/PPS")
        _hevc_nals_from_payload(mdat_boxes[0].payload, int(config["length_size_minus_one"]) + 1)
    return top


__all__ = [
    "build_heif_payload",
    "package_heic_aot",
    "package_heic_image_aot",
    "package_heic_vcl_aot",
    "package_heic_ipcm_aot",
    "package_heic_neutral_aot",
    "package_heic_flat_aot",
    "package_heic_ctu_stripes_aot",
    "package_heic_ipcm10_aot",
    "heic_vcl_capability_report",
    "heic_ipcm_capability_report",
    "heic_neutral_capability_report",
    "heic_flat_capability_report",
    "heic_flat10_capability_report",
    "heic_ctu_stripes_capability_report",
    "heic_ipcm10_capability_report",
    "save_heic_aot",
    "parse_heif_aot",
]
