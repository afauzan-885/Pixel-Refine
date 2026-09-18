"""Reusable camera/DNG metadata extraction and Bayer CFA geometry helpers.

Contains metadata extraction and orientation transformation utilities for
sensor-native RAW processing and DNG persistence.
"""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Sequence, Tuple

import numpy as np


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
    """Extract standard capture EXIF into native writer IFD entries."""
    try:
        import exifread

        with Path(path).open("rb") as stream:
            source = exifread.process_file(stream, details=True, strict=False)
    except Exception:
        return []

    entries = []
    seen = set()
    named_tags = (
        ("EXIF ExposureTime", 33434, 5),
        ("EXIF FNumber", 33437, 5),
        ("EXIF ExposureProgram", 34850, 3),
        ("EXIF ISOSpeedRatings", 34855, 3),
        ("EXIF SensitivityType", 34864, 3),
        ("EXIF StandardOutputSensitivity", 34865, 4),
        ("EXIF RecommendedExposureIndex", 34866, 4),
        ("EXIF ISOSpeed", 34867, 4),
        ("EXIF DateTimeOriginal", 36867, 2),
        ("EXIF DateTimeDigitized", 36868, 2),
        ("EXIF OffsetTime", 36880, 2),
        ("EXIF OffsetTimeOriginal", 36881, 2),
        ("EXIF OffsetTimeDigitized", 36882, 2),
        ("EXIF ShutterSpeedValue", 37377, 10),
        ("EXIF ApertureValue", 37378, 5),
        ("EXIF BrightnessValue", 37379, 10),
        ("EXIF ExposureBiasValue", 37380, 10),
        ("EXIF MaxApertureValue", 37381, 5),
        ("EXIF MeteringMode", 37383, 3),
        ("EXIF LightSource", 37384, 3),
        ("EXIF Flash", 37385, 3),
        ("EXIF FocalLength", 37386, 5),
        ("EXIF SubSecTime", 37520, 2),
        ("EXIF SubSecTimeOriginal", 37521, 2),
        ("EXIF SubSecTimeDigitized", 37522, 2),
        ("EXIF FocalLengthIn35mmFilm", 41989, 3),
        ("EXIF SceneCaptureType", 41990, 3),
        ("EXIF BodySerialNumber", 42033, 2),
        ("EXIF LensSpecification", 42034, 5),
        ("EXIF LensMake", 42035, 2),
        ("EXIF LensModel", 42036, 2),
        ("EXIF LensSerialNumber", 42037, 2),
    )

    for name, tag, type_id in named_tags:
        if name not in source:
            continue
        value = source[name]
        try:
            values = _exif_values(value)
            if type_id in (5, 10):
                encoded = tuple(_ratio_pair(item) for item in values)
                entries.append((tag, type_id, len(encoded), encoded))
            elif type_id in (3, 4):
                encoded = tuple(int(item) for item in values)
                entries.append((tag, type_id, len(encoded), encoded))
            elif type_id in (1, 7):
                raw = bytes(values[0]) if len(values) == 1 and isinstance(values[0], (bytes, bytearray)) else bytes(int(v) for v in values)
                entries.append((tag, type_id, len(raw), raw))
            elif type_id == 2:
                text = _exif_ascii(value)
                entries.append((tag, type_id, len(text.encode("ascii", "ignore")) + 1, text))
            seen.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue

    tiff_layout_tags = {
        254, 255, 256, 257, 258, 259, 262, 273, 274, 277, 278, 279, 284, 296,
        317, 322, 323, 324, 325, 330, 338, 513, 514,
    }
    reserved = {entry[0] for entry in entries} | {34665, 34853} | tiff_layout_tags
    for name, value in source.items():
        if not str(name).startswith("EXIF ") or str(name).startswith("EXIF SubIFD"):
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
            entries.append(entry)
            reserved.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    return entries


def extract_gps_tags(path: str | Path):
    """Extract GPS IFD entries without flattening them into EXIF."""
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
    """Extract the camera demosaic contract for a fused mosaic preview."""
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


def _apply_baked_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
    """Apply TIFF orientation transform to a 2D Bayer mosaic."""
    if orientation == 2:
        return np.fliplr(image)
    if orientation == 3:
        return np.rot90(image, 2)
    if orientation == 4:
        return np.flipud(image)
    if orientation == 5:
        return np.rot90(np.fliplr(image), -1)
    if orientation == 6:
        return np.rot90(image, -1)
    if orientation == 7:
        return np.rot90(np.fliplr(image), 1)
    if orientation == 8:
        return np.rot90(image, 1)
    return image


def _baked_cfa_pattern(frame) -> tuple[int, int, int, int]:
    """Return the output CFA tile after applying TIFF orientation to samples."""
    height, width = frame.shape

    def source_coordinate(row: int, column: int) -> tuple[int, int]:
        orientation = int(frame.orientation)
        if orientation == 2:
            return row, width - 1 - column
        if orientation == 3:
            return height - 1 - row, width - 1 - column
        if orientation == 4:
            return height - 1 - row, column
        if orientation == 5:
            return height - 1 - column, width - 1 - row
        if orientation == 6:
            return height - 1 - column, row
        if orientation == 7:
            return column, row
        if orientation == 8:
            return column, width - 1 - row
        return row, column

    return tuple(
        int(frame.cfa_pattern[frame.phase_index(*source_coordinate(row, column))])
        for row, column in ((0, 0), (0, 1), (1, 0), (1, 1))
    )


def _plane_slice(frame, index: int) -> tuple[slice, slice]:
    """Return row and column slices for the 2x2 Bayer phase plane index (0=TL, 1=TR, 2=BL, 3=BR)."""
    plane_row, plane_col = divmod(int(index), 2)
    row = (plane_row - int(frame.phase_origin[0])) & 1
    col = (plane_col - int(frame.phase_origin[1])) & 1
    return slice(row, None, 2), slice(col, None, 2)


def _plane_homography(matrix: np.ndarray, frame, index: int) -> np.ndarray:
    """Conjugate a sensor-pixel homography into one half-resolution CFA plane."""
    row_slice, col_slice = _plane_slice(frame, index)
    origin_x, origin_y = int(col_slice.start), int(row_slice.start)
    plane_to_sensor = np.array(
        [[2.0, 0.0, origin_x], [0.0, 2.0, origin_y], [0.0, 0.0, 1.0]],
        dtype=np.float32,
    )
    return np.ascontiguousarray(
        np.linalg.inv(plane_to_sensor) @ np.asarray(matrix, dtype=np.float32) @ plane_to_sensor,
        dtype=np.float32,
    )


__all__ = [
    "extract_capture_exif",
    "extract_gps_tags",
    "extract_dng_camera_tags",
    "extract_root_capture_tags",
    "extract_demosaic_parameters",
    "extract_source_dng_metadata",
    "_apply_baked_orientation",
    "_baked_cfa_pattern",
    "_plane_slice",
    "_plane_homography",
]
