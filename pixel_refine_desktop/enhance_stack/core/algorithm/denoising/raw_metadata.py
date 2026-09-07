"""Reusable camera/DNG metadata extraction for sensor-native outputs.

This module deliberately contains no image-processing code.  It converts
metadata from the reference DNG into the native writer's IFD entry contract so
Average, SpatialFusion, and FusionNet can share the same output behavior.
"""

from fractions import Fraction
from pathlib import Path


_DNG_CAMERA_TAGS = {
    50710: (1, 3),   # CFAPlaneColor
    50711: (3, 1),   # CFALayout
    50713: (3, 2),   # BlackLevelRepeatDim
    50718: (5, 2),   # DefaultScale
    50721: (10, 9),  # ColorMatrix1
    50722: (10, 9),  # ColorMatrix2
    50723: (10, 9),  # CameraCalibration1
    50724: (10, 9),  # CameraCalibration2
    50727: (5, 3),   # AnalogBalance
    50728: (5, 3),   # AsShotNeutral
    50729: (5, 2),   # AsShotWhiteXY
    50730: (10, 1),  # BaselineExposure
    50731: (5, 1),   # BaselineNoise
    50732: (5, 1),   # BaselineSharpness
    50734: (5, 1),   # LinearResponseLimit
    50778: (3, 1),   # CalibrationIlluminant1
    50779: (3, 1),   # CalibrationIlluminant2
    37398: (1, 4),   # TIFF/EPStandardID
    # Optional camera look/profile payloads.  OpcodeList3 is intentionally
    # excluded because it could reapply a sensor correction after baking.
    50964: (10, None),  # ProfileHueSatMapData1
    50965: (10, None),  # ProfileHueSatMapData2
    51041: (12, None),  # ProfileLookTableData
}


def _ratio_pair(value) -> tuple[int, int]:
    numerator = getattr(value, "num", None)
    denominator = getattr(value, "den", None)
    if numerator is not None and denominator is not None:
        return int(numerator), max(1, int(denominator))
    fraction = Fraction(float(value)).limit_denominator(1_000_000)
    return int(fraction.numerator), int(fraction.denominator)


def _exif_values(value):
    raw = getattr(value, "values", None)
    if raw is None:
        return (value,)
    if isinstance(raw, (bytes, bytearray, str)):
        return (raw,)
    return tuple(raw)


def _exif_ascii(value) -> str:
    text = getattr(value, "printable", value)
    if isinstance(text, bytes):
        text = text.decode("ascii", errors="ignore")
    return str(text).rstrip("\x00")


def extract_dng_camera_tags(frame, output_shape: tuple[int, int]):
    """Extract camera colour/profile tags for a derived, baked DNG."""
    source_tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    entries = []
    for tag, (type_id, count) in _DNG_CAMERA_TAGS.items():
        if tag not in source_tags:
            continue
        value = source_tags[tag]
        resolved_count = count
        if resolved_count is None:
            if isinstance(value, (bytes, bytearray)):
                resolved_count = len(value)
            elif isinstance(value, (tuple, list)):
                resolved_count = len(value)
            else:
                resolved_count = 1
        entries.append((tag, type_id, int(resolved_count), value))

    height, width = map(int, output_shape)
    entries.extend(
        (
            (50719, 4, 2, (0, 0)),
            (50720, 4, 2, (width, height)),
            (50829, 4, 4, (0, 0, height, width)),
        )
    )
    return entries


def extract_capture_exif(path: str | Path):
    """Extract standard capture EXIF into native writer IFD entries.

    EXIF is optional: a missing parser or malformed optional field returns the
    entries that can be safely decoded instead of aborting RAW fusion.
    """
    try:
        import exifread

        with Path(path).open("rb") as stream:
            source = exifread.process_file(stream, details=False, strict=False)
    except Exception:
        return []

    fields = (
        ("EXIF ExposureTime", 33434, 5),
        ("EXIF FNumber", 33437, 5),
        ("EXIF FocalLength", 37386, 5),
        ("EXIF MaxApertureValue", 37381, 5),
        ("EXIF DigitalZoomRatio", 41988, 5),
        ("EXIF ExposureBiasValue", 37380, 10),
        ("EXIF SubjectDistance", 37382, 10),
        ("EXIF ExposureProgram", 34850, 3),
        ("EXIF ISOSpeedRatings", 34855, 3),
        ("EXIF SensitivityType", 34864, 3),
        ("EXIF MeteringMode", 37383, 3),
        ("EXIF LightSource", 37384, 3),
        ("EXIF Flash", 37385, 3),
        ("EXIF SensingMethod", 41495, 3),
        ("EXIF CustomRendered", 41985, 3),
        ("EXIF ExposureMode", 41986, 3),
        ("EXIF WhiteBalance", 41987, 3),
        ("EXIF FocalLengthIn35mmFilm", 41989, 3),
        ("EXIF SceneCaptureType", 41990, 3),
        ("EXIF GainControl", 41991, 3),
        ("EXIF Contrast", 41992, 3),
        ("EXIF Saturation", 41993, 3),
        ("EXIF Sharpness", 41994, 3),
        ("EXIF SubjectDistanceRange", 41996, 3),
        ("EXIF ColorSpace", 40961, 3),
        ("EXIF PixelXDimension", 40962, 4),
        ("EXIF PixelYDimension", 40963, 4),
        ("EXIF FileSource", 41728, 1),
        ("EXIF SceneType", 41729, 1),
        ("EXIF FlashPixVersion", 40960, 7),
        ("EXIF SubSecTimeOriginal", 37521, 2),
        ("EXIF SubSecTimeDigitized", 37522, 2),
        ("EXIF SubSecTime", 37520, 2),
        ("EXIF BodySerialNumber", 42033, 2),
        ("EXIF LensMake", 42035, 2),
        ("EXIF LensModel", 42036, 2),
        ("EXIF LensSerialNumber", 42037, 2),
        ("EXIF ImageUniqueID", 42016, 2),
        ("EXIF OwnerName", 42032, 2),
        ("EXIF DateTimeOriginal", 36867, 2),
        ("EXIF DateTimeDigitized", 36868, 2),
    )
    entries = []
    seen = set()
    for name, tag, type_id in fields:
        value = source.get(name)
        if value is None or tag in seen:
            continue
        try:
            values = _exif_values(value)
            if type_id in (5, 10):
                encoded = tuple(_ratio_pair(item) for item in values)
                entries.append((tag, type_id, len(encoded), encoded))
            elif type_id in (1, 3, 4):
                encoded = tuple(int(item) for item in values)
                if type_id == 1:
                    encoded = bytes(item & 0xFF for item in encoded)
                entries.append(
                    (tag, type_id, len(encoded), encoded[0] if len(encoded) == 1 else encoded)
                )
            elif type_id == 7:
                if len(values) == 1 and isinstance(values[0], (bytes, bytearray)):
                    raw = bytes(values[0])
                else:
                    raw = bytes(int(item) & 0xFF for item in values)
                entries.append((tag, type_id, len(raw), raw))
            elif type_id == 2:
                text = _exif_ascii(value)
                entries.append((tag, type_id, len(text.encode("ascii", "ignore")) + 1, text))
            seen.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    # Preserve additional EXIF fields not covered by the stable named list.
    # exifread exposes the original numeric tag and TIFF field type, allowing
    # the native DNG writer to retain vendor/capture fields without converting
    # them through strings. Pointer tags are excluded because the writer owns
    # the generated Exif IFD layout.
    reserved = {entry[0] for entry in entries} | {34665, 34853}
    for name, value in source.items():
        if not str(name).startswith("EXIF "):
            continue
        tag = getattr(value, "tag", None)
        type_id = getattr(value, "field_type", None)
        if tag is None or type_id is None:
            continue
        try:
            tag, type_id = int(tag), int(type_id)
            if tag in reserved or type_id not in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12):
                continue
            values = _exif_values(value)
            if type_id == 2:
                text = _exif_ascii(value)
                entry = (tag, type_id, len(text.encode("ascii", "ignore")) + 1, text)
            elif type_id in (5, 10):
                encoded = tuple(_ratio_pair(item) for item in values)
                entry = (tag, type_id, len(encoded), encoded)
            elif type_id in (1, 6, 7):
                if len(values) == 1 and isinstance(values[0], (bytes, bytearray)):
                    raw = bytes(values[0])
                    entry = (tag, type_id, len(raw), raw)
                else:
                    encoded = tuple(int(item) for item in values)
                    entry = (tag, type_id, len(encoded), encoded)
            elif type_id in (3, 4, 8, 9, 11, 12):
                encoded = tuple(
                    float(item) if type_id in (11, 12) else int(item)
                    for item in values
                )
                entry = (tag, type_id, len(encoded), encoded)
            else:
                continue
            # Validate using the same packing rules as the DNG writer.
            entries.append(entry)
            reserved.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    return entries


def extract_gps_tags(path: str | Path):
    """Extract GPS IFD entries without flattening them into EXIF.

    GPS tags use a separate TIFF IFD.  Keeping them separate is important:
    putting the relative GPS tag numbers into the EXIF IFD produces a file that
    may open, but is not interpreted as geolocation metadata by RAW software.
    """
    try:
        import exifread

        with Path(path).open("rb") as stream:
            source = exifread.process_file(stream, details=True, strict=False)
    except Exception:
        return []

    entries = []
    for name, value in source.items():
        if not str(name).startswith("GPS "):
            continue
        tag = getattr(value, "tag", None)
        type_id = getattr(value, "field_type", None)
        if tag is None or type_id is None:
            continue
        try:
            tag, type_id = int(tag), int(type_id)
            if not 0 <= tag <= 0xFFFF or type_id not in range(1, 13):
                continue
            values = _exif_values(value)
            if type_id == 2:
                text = _exif_ascii(value)
                entry = (tag, type_id, len(text.encode("ascii", "ignore")) + 1, text)
            elif type_id in (5, 10):
                encoded = tuple(_ratio_pair(item) for item in values)
                entry = (tag, type_id, len(encoded), encoded)
            elif type_id in (1, 6, 7):
                if len(values) == 1 and isinstance(values[0], (bytes, bytearray)):
                    raw = bytes(values[0])
                    entry = (tag, type_id, len(raw), raw)
                else:
                    encoded = tuple(int(item) for item in values)
                    entry = (tag, type_id, len(encoded), encoded)
            elif type_id in (3, 4, 8, 9, 11, 12):
                encoded = tuple(
                    float(item) if type_id in (11, 12) else int(item)
                    for item in values
                )
                entry = (tag, type_id, len(encoded), encoded)
            else:
                continue
            entries.append(entry)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    # A malformed file can expose the same numeric GPS tag more than once.
    # The native writer requires unique tags in an IFD.
    return list({entry[0]: entry for entry in entries}.values())


def extract_root_capture_tags(frame):
    """Extract safe root-IFD identity and resolution fields."""
    source_tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    entries = []
    for tag, type_id in ((282, 5), (283, 5), (305, 2), (306, 2)):
        if tag not in source_tags:
            continue
        value = source_tags[tag]
        if type_id == 5:
            if isinstance(value, tuple) and len(value) == 2 and not isinstance(value[0], (tuple, list)):
                value = (value,)
            entries.append((tag, type_id, len(value), value))
        else:
            text = str(value).rstrip("\x00")
            entries.append((tag, type_id, len(text.encode("ascii", "ignore")) + 1, text))
    return entries


def extract_source_dng_metadata(
    frame,
    output_shape: tuple[int, int],
    *,
    source_path: str | Path = "",
) -> dict:
    """Build reusable writer metadata shared by every RAW-native algorithm."""
    source_tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    metadata = {
        "camera_model": str(source_tags.get(50708, "Pixel Refine RAW Native")),
        "dng_extra_tags": extract_dng_camera_tags(frame, output_shape),
        "ifd0_tags": extract_root_capture_tags(frame),
        "exif_tags": extract_capture_exif(source_path) if source_path else [],
        "gps_tags": extract_gps_tags(source_path) if source_path else [],
    }
    if 271 in source_tags:
        metadata["make"] = str(source_tags[271])
    if 272 in source_tags:
        metadata["model"] = str(source_tags[272])
    return metadata


def extract_demosaic_parameters(path: str | Path, cfa_pattern=None) -> dict:
    """Extract the camera demosaic contract for a fused mosaic preview.

    The input file is used only as a metadata source; callers may pass a
    different, already-fused Bayer array to ``taichi_aot.demosaic``.  This
    keeps RGB Linear output color-aware without changing RAW accumulation.
    """
    import numpy as np
    import rawpy

    with rawpy.imread(str(path)) as raw:
        wb = np.asarray(raw.camera_whitebalance, dtype=np.float32)
        if wb.size == 4:
            if wb[3] <= 0.01:
                wb[3] = wb[1]
            wb /= max(float((wb[1] + wb[3]) / 2.0), 1e-6)
        else:
            wb = np.asarray((1.5, 1.0, 2.0, 1.0), dtype=np.float32)
        cfa = tuple(
            int(value)
            for value in (cfa_pattern or (
                raw.raw_colors[0, 0], raw.raw_colors[0, 1],
                raw.raw_colors[1, 0], raw.raw_colors[1, 1],
            ))
        )
        return {
            "wb_r": float(wb[0]),
            "wb_g1": float(wb[1]),
            "wb_b": float(wb[2]),
            "wb_g2": float(wb[3]),
            "cmatrix": np.ascontiguousarray(raw.color_matrix[:, :3], dtype=np.float32),
            "black_level": float(raw.black_level_per_channel[0]),
            "white_level": float(raw.white_level),
            "c00": cfa[0],
            "c01": cfa[1],
            "c10": cfa[2],
            "c11": cfa[3],
        }


__all__ = [
    "extract_capture_exif",
    "extract_gps_tags",
    "extract_dng_camera_tags",
    "extract_root_capture_tags",
    "extract_demosaic_parameters",
    "extract_source_dng_metadata",
]
