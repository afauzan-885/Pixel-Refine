"""DNG colour, capture EXIF, and GPS metadata helpers for RAW Native output."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path

import numpy as np


# Tags are copied only when their value is independent of the source strip
# layout.  The DNG writer owns geometry, CFA pattern, black/white, and
# orientation of the derived mosaic.
_DNG_CAMERA_TAGS = {
    50710: (1, 3), 50711: (3, 1), 50713: (3, 2), 50718: (5, 2),
    50721: (10, 9), 50722: (10, 9), 50723: (10, 9), 50724: (10, 9),
    50727: (5, 3), 50728: (5, 3), 50729: (5, 2), 50730: (10, 1),
    50731: (5, 1), 50732: (5, 1), 50734: (5, 1), 50778: (3, 1),
    50779: (3, 1), 37398: (1, 4), 50964: (10, None),
    50965: (10, None), 51041: (12, None),
}


def normalize_cfa_rgb_codes(cfa_pattern) -> tuple[int, int, int, int]:
    """Map legacy rawpy green-2 code ``3`` to the DNG green code ``1``."""
    normalized = tuple(1 if int(value) == 3 else int(value) for value in cfa_pattern)
    if len(normalized) != 4 or any(value < 0 or value > 2 for value in normalized):
        raise ValueError(f"unsupported DNG CFA RGB codes: {tuple(cfa_pattern)}")
    return normalized


def _ratio_pair(value) -> tuple[int, int]:
    numerator, denominator = getattr(value, "num", None), getattr(value, "den", None)
    if numerator is not None and denominator is not None:
        return int(numerator), max(1, int(denominator))
    fraction = Fraction(float(value)).limit_denominator(1_000_000)
    return int(fraction.numerator), int(fraction.denominator)


def _rational_float(value) -> float:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        denominator = float(value[1])
        return float(value[0]) / denominator if denominator else 0.0
    return float(value)


def _as_shot_neutral_gains(frame) -> np.ndarray | None:
    tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    values = tags.get(50728)
    if values is None:
        return None
    if isinstance(values, tuple) and len(values) == 2 and not isinstance(values[0], (tuple, list)):
        values = (values,)
    try:
        neutral = np.asarray([_rational_float(value) for value in values], dtype=np.float32)
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    if neutral.size < 3 or np.any(~np.isfinite(neutral[:3])) or np.any(neutral[:3] <= 1e-6):
        return None
    # DNG AsShotNeutral is inverse camera gain.  Normalize its green gain to
    # one and duplicate it over the two green Bayer sites.
    return np.asarray((neutral[1] / neutral[0], 1.0, neutral[1] / neutral[2], 1.0), dtype=np.float32)


def _dng_colour_matrix(frame) -> np.ndarray | None:
    tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    for tag in (50721, 50722):  # ColorMatrix1, then ColorMatrix2
        values = tags.get(tag)
        if values is None:
            continue
        if isinstance(values, tuple) and len(values) == 2 and not isinstance(values[0], (tuple, list)):
            values = (values,)
        try:
            matrix = np.asarray([_rational_float(value) for value in values], dtype=np.float32)
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if matrix.size == 9 and np.isfinite(matrix).all():
            return np.ascontiguousarray(matrix.reshape(3, 3), dtype=np.float32)
    return None


def _exif_values(value):
    values = getattr(value, "values", None)
    if values is None:
        return (value,)
    if isinstance(values, (bytes, bytearray, str)):
        return (values,)
    return tuple(values)


def _entry_from_exif_value(value, tag: int, type_id: int):
    """Translate an exifread value to the writer's explicit IFD tuple."""
    values = _exif_values(value)
    if type_id == 2:
        text = str(getattr(value, "printable", value)).rstrip("\x00")
        return tag, type_id, len(text.encode("ascii", "ignore")) + 1, text
    if type_id in (5, 10):
        encoded = tuple(_ratio_pair(item) for item in values)
    elif type_id in (1, 6, 7):
        if len(values) == 1 and isinstance(values[0], (bytes, bytearray)):
            encoded = bytes(values[0])
        else:
            encoded = tuple(int(item) for item in values)
    elif type_id in (3, 4, 8, 9):
        encoded = tuple(int(item) for item in values)
    elif type_id in (11, 12):
        encoded = tuple(float(item) for item in values)
    else:
        raise ValueError(f"unsupported EXIF TIFF type {type_id}")
    count = len(encoded)
    return tag, type_id, count, encoded


def _read_exif(path: str | Path):
    try:
        import exifread

        with Path(path).open("rb") as stream:
            return exifread.process_file(stream, details=True, strict=False)
    except Exception:
        return {}


def extract_capture_exif(path: str | Path):
    """Preserve safe capture EXIF in its own IFD, never in the root IFD."""
    source = _read_exif(path)
    layout_tags = {
        254, 255, 256, 257, 258, 259, 262, 273, 274, 277, 278, 279,
        284, 296, 317, 322, 323, 324, 325, 330, 338, 34665, 34853,
        513, 514,
    }
    entries, seen = [], set()
    for name, value in source.items():
        if not str(name).startswith("EXIF ") or str(name).startswith("EXIF SubIFD"):
            continue
        try:
            tag, type_id = int(getattr(value, "tag")), int(getattr(value, "field_type"))
            if tag in layout_tags or tag in seen or type_id not in range(1, 13):
                continue
            entries.append(_entry_from_exif_value(value, tag, type_id))
            seen.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    return entries


def extract_gps_tags(path: str | Path):
    """Preserve GPS entries in a dedicated GPS IFD."""
    source = _read_exif(path)
    entries, seen = [], set()
    for name, value in source.items():
        if not str(name).startswith("GPS "):
            continue
        try:
            tag, type_id = int(getattr(value, "tag")), int(getattr(value, "field_type"))
            if not 0 <= tag <= 0xFFFF or tag in seen or type_id not in range(1, 13):
                continue
            entries.append(_entry_from_exif_value(value, tag, type_id))
            seen.add(tag)
        except (TypeError, ValueError, OverflowError, ZeroDivisionError):
            continue
    return entries


def extract_dng_camera_tags(frame, output_shape: tuple[int, int]):
    """Copy colour/profile tags and rebuild geometry tied to the new mosaic."""
    source_tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    entries = []
    for tag, (type_id, count) in _DNG_CAMERA_TAGS.items():
        if tag not in source_tags:
            continue
        value = source_tags[tag]
        resolved_count = count
        if resolved_count is None:
            resolved_count = len(value) if isinstance(value, (bytes, bytearray, tuple, list)) else 1
        entries.append((tag, type_id, int(resolved_count), value))
    height, width = (int(output_shape[0]), int(output_shape[1]))
    entries.extend(((50719, 4, 2, (0, 0)), (50720, 4, 2, (width, height)), (50829, 4, 4, (0, 0, height, width))))
    return entries


def extract_root_capture_tags(frame):
    source_tags = dict(getattr(frame, "metadata", {}).get("dng_tags", {}) or {})
    entries = []
    for tag, type_id in ((282, 5), (283, 5), (305, 2), (306, 2)):
        if tag not in source_tags:
            continue
        value = source_tags[tag]
        if type_id == 5:
            value = (value,) if isinstance(value, tuple) and len(value) == 2 and not isinstance(value[0], tuple) else value
            entries.append((tag, type_id, len(value), value))
        else:
            text = str(value).rstrip("\x00")
            entries.append((tag, type_id, len(text.encode("ascii", "ignore")) + 1, text))
    return entries


def extract_source_dng_metadata(frame, output_shape, *, source_path: str | Path = "") -> dict:
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


def extract_demosaic_parameters(path: str | Path, cfa_pattern, *, frame=None) -> dict:
    """Get camera WB and colour matrix for a normalized fused CFA preview."""
    camera_wb = np.empty(0, dtype=np.float32)
    daylight_wb = np.empty(0, dtype=np.float32)
    cmatrix = None
    try:
        import rawpy
        with rawpy.imread(str(path)) as raw:
            camera_wb = np.asarray(raw.camera_whitebalance, dtype=np.float32).reshape(-1)
            daylight_wb = np.asarray(getattr(raw, "daylight_whitebalance", ()), dtype=np.float32).reshape(-1)
            candidate = np.ascontiguousarray(raw.color_matrix[:, :3], dtype=np.float32)
            if candidate.shape == (3, 3) and np.isfinite(candidate).all():
                cmatrix = candidate
    except Exception:
        # A valid DNG may be outside LibRaw's decode support.  Its own DNG
        # tags are still enough to produce a colour-managed preview.
        pass

    def valid_wb(values):
        return values.size == 4 and np.isfinite(values).all() and np.all(values > 0.01)

    if valid_wb(camera_wb):
        wb, wb_source = camera_wb, "camera"
    else:
        from_dng = _as_shot_neutral_gains(frame) if frame is not None else None
        if from_dng is not None:
            wb, wb_source = from_dng, "AsShotNeutral"
        elif valid_wb(daylight_wb):
            wb, wb_source = daylight_wb, "daylight"
        else:
            wb, wb_source = np.ones(4, dtype=np.float32), "neutral"
    if wb[3] <= 0.01:
        wb[3] = wb[1]
    wb /= max(float((wb[1] + wb[3]) * 0.5), 1e-6)

    if cmatrix is None:
        cmatrix = _dng_colour_matrix(frame) if frame is not None else None
    if cmatrix is None:
        raise ValueError("camera ColorMatrix is unavailable")
    cfa = normalize_cfa_rgb_codes(cfa_pattern)
    return {
        "wb_r": float(wb[0]), "wb_g1": float(wb[1]),
        "wb_b": float(wb[2]), "wb_g2": float(wb[3]),
        "cmatrix": cmatrix, "black_level": 0.0, "white_level": 1.0,
        "c00": cfa[0], "c01": cfa[1], "c10": cfa[2], "c11": cfa[3],
        "white_balance_source": wb_source,
    }


def carrier_demosaic_parameters(frame) -> dict:
    """Hamilton demosaic parameters for an already-decoded carrier mosaic.

    ``extract_demosaic_parameters`` describes a *normalized* preview and consults
    an external RAW reader for camera WB and colour matrix.  The RAW Native
    analysis proxy instead consumes the carrier exactly as decoded, so it needs
    the sensor's own integer black/white contract -- the same one
    ``_normalized_for_rgb_parity`` applies -- and can take white balance and the
    colour matrix from the DNG tags the provider already parsed.  Nothing here
    re-opens the file or requires a third-party decoder.
    """

    gains = _as_shot_neutral_gains(frame)
    if gains is None:
        fallback = np.asarray(
            tuple(getattr(frame, "white_balance", ()) or ()), dtype=np.float32
        ).reshape(-1)
        gains = (
            fallback
            if fallback.size == 4
            and np.isfinite(fallback).all()
            and np.all(fallback > 0.01)
            else np.ones(4, dtype=np.float32)
        )
    wb = np.asarray(gains, dtype=np.float32)
    if wb[3] <= 0.01:
        wb = wb.copy()
        wb[3] = wb[1]

    matrix = _dng_colour_matrix(frame)
    if matrix is None:
        raise ValueError("carrier ColorMatrix is unavailable")
    cfa = normalize_cfa_rgb_codes(frame.cfa_pattern)
    return {
        "wb_r": float(wb[0]),
        "wb_g1": float(wb[1]),
        "wb_b": float(wb[2]),
        "wb_g2": float(wb[3]),
        "cmatrix": matrix,
        "black_level": float(int(float(tuple(frame.black_level)[0]))),
        "white_level": float(int(float(tuple(frame.white_level)[0]))),
        "c00": cfa[0],
        "c01": cfa[1],
        "c10": cfa[2],
        "c11": cfa[3],
    }


def _apply_baked_orientation(image: np.ndarray, orientation: int) -> np.ndarray:
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
    height, width = frame.shape

    def source_coordinate(row, col):
        orientation = int(frame.orientation)
        if orientation == 2: return row, width - 1 - col
        if orientation == 3: return height - 1 - row, width - 1 - col
        if orientation == 4: return height - 1 - row, col
        if orientation == 5: return height - 1 - col, width - 1 - row
        if orientation == 6: return height - 1 - col, row
        if orientation == 7: return col, row
        if orientation == 8: return col, width - 1 - row
        return row, col

    return tuple(int(frame.cfa_pattern[frame.phase_index(*source_coordinate(y, x))]) for y, x in ((0, 0), (0, 1), (1, 0), (1, 1)))


__all__ = [
    "extract_capture_exif", "extract_gps_tags", "extract_dng_camera_tags",
    "extract_root_capture_tags", "extract_source_dng_metadata",
    "extract_demosaic_parameters", "normalize_cfa_rgb_codes",
    "_apply_baked_orientation", "_baked_cfa_pattern",
]
