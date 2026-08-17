"""Immutable, pre-demosaic RAW frame contract.

The container parser in :mod:`dng_aot` deliberately remains small and
format-oriented.  This module is the semantic boundary used by alignment,
fusion, weight-map, and demosaic code.  It keeps sensor codes in their native
integer representation until a caller explicitly asks for a normalized
headroom view.

The class is backend-neutral.  It does not allocate a Taichi field and does
not silently choose a CPU fallback; callers may pass its views to the normal
AOT dispatcher or to a backend-specific tile reader.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Sequence, Tuple

import numpy as np


_CFA_SIZE = 4
_DEFAULT_CFA = (1, 0, 0, 1)  # DNG/RGGB-style numeric codes: G/R/B/G.
_DEFAULT_ACTIVE_AREA = (0, 0, 0, 0)


def _tuple_floats(value: Any, *, length: int, name: str) -> tuple[float, ...]:
    if np.isscalar(value):
        values = (float(value),) * length
    else:
        try:
            values = tuple(float(item) for item in value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{name} must be a scalar or {length}-item sequence") from exc
        if len(values) == 1:
            values = values * length
    if len(values) != length:
        raise ValueError(f"{name} must contain exactly {length} values")
    if not all(np.isfinite(item) for item in values):
        raise ValueError(f"{name} must contain finite values")
    return values


def _tuple_ints(value: Any, *, length: int, name: str) -> tuple[int, ...]:
    try:
        values = tuple(int(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain {length} integers") from exc
    if len(values) != length:
        raise ValueError(f"{name} must contain exactly {length} values")
    return values


def _rational_to_float(value: Any) -> float:
    """Convert common TIFF rational representations without losing metadata."""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        numerator, denominator = value
        denominator = float(denominator)
        if denominator == 0:
            return 0.0
        return float(numerator) / denominator
    return float(value)


def _rational_sequence(value: Any) -> tuple[float, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple) and len(value) == 2 and all(np.isscalar(item) for item in value):
        return (_rational_to_float(value),)
    if isinstance(value, (tuple, list)):
        return tuple(_rational_to_float(item) for item in value)
    return (_rational_to_float(value),)


def _parse_active_area(value: Any, height: int, width: int) -> tuple[int, int, int, int]:
    """Return ``(top, left, bottom, right)`` in sensor coordinates."""
    if value is None:
        return (0, 0, int(height), int(width))
    try:
        top, left, bottom, right = (int(item) for item in value)
    except (TypeError, ValueError) as exc:
        raise ValueError("active_area must contain top,left,bottom,right") from exc
    if not (0 <= top <= bottom <= int(height) and 0 <= left <= right <= int(width)):
        raise ValueError("active_area is outside the RAW frame")
    return top, left, bottom, right


@dataclass(frozen=True)
class RawMosaicFrame:
    """Validated semantic representation of a pre-demosaic sensor frame.

    ``samples`` remains ``uint8`` or ``uint16`` exactly as supplied.  A
    normalized view is explicitly ``float32`` and deliberately does not clamp
    values above one: highlight recovery needs that headroom.  The dataclass
    is immutable at the contract level; callers should treat the underlying
    array as read-only and use a new frame for transformed data.
    """

    samples: np.ndarray
    bits_per_sample: int
    cfa_pattern: tuple[int, int, int, int] = _DEFAULT_CFA
    phase_origin: tuple[int, int] = (0, 0)
    black_level: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)
    white_level: tuple[float, float, float, float] = (65535.0,) * 4
    active_area: tuple[int, int, int, int] = _DEFAULT_ACTIVE_AREA
    white_balance: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0)
    exposure_scale: float = 1.0
    orientation: int = 1
    source_id: str = ""
    source_version: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        array = np.asarray(self.samples)
        if array.ndim != 2:
            raise ValueError("RAW mosaic samples must be a 2D array")
        if array.dtype not in (np.dtype(np.uint8), np.dtype(np.uint16)):
            raise TypeError("RAW mosaic samples must use uint8 or uint16")
        if not array.flags.c_contiguous:
            array = np.ascontiguousarray(array)
        if array.size == 0:
            raise ValueError("RAW mosaic samples must not be empty")
        bits = int(self.bits_per_sample)
        native_bits = 8 if array.dtype == np.uint8 else 16
        if not 1 <= bits <= native_bits:
            raise ValueError(f"bits_per_sample must be between 1 and {native_bits}")
        object.__setattr__(self, "samples", array)
        object.__setattr__(self, "bits_per_sample", bits)
        object.__setattr__(self, "cfa_pattern", _tuple_ints(self.cfa_pattern, length=4, name="cfa_pattern"))
        phase = _tuple_ints(self.phase_origin, length=2, name="phase_origin")
        if any(item not in (0, 1) for item in phase):
            raise ValueError("phase_origin values must be 0 or 1")
        object.__setattr__(self, "phase_origin", phase)
        object.__setattr__(self, "black_level", _tuple_floats(self.black_level, length=4, name="black_level"))
        object.__setattr__(self, "white_level", _tuple_floats(self.white_level, length=4, name="white_level"))
        for index, (black, white) in enumerate(zip(self.black_level, self.white_level)):
            if white <= black:
                raise ValueError(f"white_level[{index}] must be greater than black_level[{index}]")
        area = self.active_area
        if tuple(area) == _DEFAULT_ACTIVE_AREA:
            area = (0, 0, int(array.shape[0]), int(array.shape[1]))
        else:
            area = _parse_active_area(area, int(array.shape[0]), int(array.shape[1]))
        object.__setattr__(self, "active_area", area)
        object.__setattr__(self, "white_balance", _tuple_floats(self.white_balance, length=4, name="white_balance"))
        exposure = float(self.exposure_scale)
        if not np.isfinite(exposure) or exposure <= 0:
            raise ValueError("exposure_scale must be finite and positive")
        object.__setattr__(self, "exposure_scale", exposure)
        orientation = int(self.orientation)
        if orientation not in (1, 2, 3, 4, 5, 6, 7, 8):
            raise ValueError("orientation must be a TIFF orientation value from 1 to 8")
        object.__setattr__(self, "orientation", orientation)
        object.__setattr__(self, "source_id", str(self.source_id or ""))
        object.__setattr__(self, "source_version", str(self.source_version or ""))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata or {})))

    @classmethod
    def from_samples(
        cls,
        samples: Any,
        *,
        bits_per_sample: Optional[int] = None,
        cfa_pattern: Sequence[int] = _DEFAULT_CFA,
        phase_origin: Sequence[int] = (0, 0),
        black_level: Any = 0.0,
        white_level: Any = None,
        active_area: Sequence[int] | None = None,
        white_balance: Any = (1.0, 1.0, 1.0, 1.0),
        exposure_scale: float = 1.0,
        orientation: int = 1,
        source_id: str = "",
        source_version: str = "",
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> "RawMosaicFrame":
        array = np.asarray(samples)
        if array.dtype not in (np.dtype(np.uint8), np.dtype(np.uint16)):
            raise TypeError("RAW mosaic samples must use uint8 or uint16")
        bits = int(bits_per_sample or (8 if array.dtype == np.uint8 else 16))
        default_white = (float((1 << bits) - 1),) * 4
        return cls(
            array,
            bits,
            tuple(cfa_pattern),
            tuple(phase_origin),
            black_level=black_level,
            white_level=default_white if white_level is None else white_level,
            active_area=(0, 0, 0, 0) if active_area is None else tuple(active_area),
            white_balance=white_balance,
            exposure_scale=exposure_scale,
            orientation=orientation,
            source_id=source_id,
            source_version=source_version,
            metadata=metadata or {},
        )

    @classmethod
    def from_dng(cls, frame: Any, *, source_id: str = "", source_version: str = "") -> "RawMosaicFrame":
        """Adapt a parsed :class:`DNGFrame` without demosaicing or float conversion."""
        tags = dict(getattr(frame, "tags", {}) or {})
        samples = frame.samples()
        bits = int(getattr(frame, "bits_per_sample", tags.get(258, 16)))
        cfa = tags.get(33422, _DEFAULT_CFA)
        if isinstance(cfa, (bytes, bytearray)):
            cfa = tuple(int(item) for item in cfa[:4])
        else:
            cfa = tuple(int(item) for item in cfa)
        black = _rational_sequence(tags.get(50714, 0.0))
        white = _rational_sequence(tags.get(50717, (1 << bits) - 1))
        wb = _rational_sequence(tags.get(50728, (1.0, 1.0, 1.0, 1.0)))
        area = tags.get(50829)
        metadata = {
            "dng_tags": tags,
            "compression": int(getattr(frame, "compression", tags.get(259, 1))),
            "endian": str(getattr(frame, "endian", "II")),
        }
        if 50706 in tags:
            metadata["dng_version"] = tags[50706]
        return cls.from_samples(
            samples,
            bits_per_sample=bits,
            cfa_pattern=cfa if len(cfa) == 4 else _DEFAULT_CFA,
            black_level=black or 0.0,
            white_level=white or ((1 << bits) - 1,),
            active_area=area,
            white_balance=wb if len(wb) == 4 else (1.0, 1.0, 1.0, 1.0),
            orientation=int(tags.get(274, 1)),
            source_id=source_id,
            source_version=source_version,
            metadata=metadata,
        )

    @classmethod
    def from_dng_region(
        cls,
        frame: Any,
        y0: int,
        y1: int,
        x0: int,
        x1: int,
        *,
        source_id: str = "",
        source_version: str = "",
    ) -> "RawMosaicFrame":
        """Adapt one DNG sensor tile without materializing the full frame.

        The tile's ``phase_origin`` is shifted by its absolute origin.  That
        detail is essential for odd-aligned block grids: normalization and
        green-guide extraction must see the same CFA plane as the full-frame
        path.  No RGB conversion or float staging occurs here.
        """
        y0, y1, x0, x1 = (int(y0), int(y1), int(x0), int(x1))
        if not (0 <= y0 <= y1 <= int(frame.height) and 0 <= x0 <= x1 <= int(frame.width)):
            raise ValueError("DNG RAW region is outside the frame")
        tags = dict(getattr(frame, "tags", {}) or {})
        samples = frame.sample_region(y0, y1, x0, x1)
        bits = int(getattr(frame, "bits_per_sample", tags.get(258, 16)))
        cfa = tags.get(33422, _DEFAULT_CFA)
        if isinstance(cfa, (bytes, bytearray)):
            cfa = tuple(int(item) for item in cfa[:4])
        else:
            cfa = tuple(int(item) for item in cfa)
        black = _rational_sequence(tags.get(50714, 0.0))
        white = _rational_sequence(tags.get(50717, (1 << bits) - 1))
        wb = _rational_sequence(tags.get(50728, (1.0, 1.0, 1.0, 1.0)))
        base_phase = tuple(int(item) & 1 for item in tags.get("phase_origin", (0, 0)))
        full_area = _parse_active_area(
            tags.get(50829), int(frame.height), int(frame.width)
        )
        intersection_top = max(y0, full_area[0])
        intersection_left = max(x0, full_area[1])
        intersection_bottom = max(intersection_top, min(y1, full_area[2]))
        intersection_right = max(intersection_left, min(x1, full_area[3]))
        tile_area = (
            intersection_top - y0,
            intersection_left - x0,
            intersection_bottom - y0,
            intersection_right - x0,
        )
        # A tile outside the DNG active area remains valid sensor storage but
        # has no active samples; represent that explicitly rather than
        # silently treating the whole tile as active.
        tile_area = tuple(
            min(max(int(value), 0), limit)
            for value, limit in zip(
                tile_area,
                (int(y1 - y0), int(x1 - x0), int(y1 - y0), int(x1 - x0)),
            )
        )
        metadata = {
            "dng_tags": tags,
            "compression": int(getattr(frame, "compression", tags.get(259, 1))),
            "endian": str(getattr(frame, "endian", "II")),
            "region_origin": (y0, x0),
            "full_shape": (int(frame.height), int(frame.width)),
        }
        if 50706 in tags:
            metadata["dng_version"] = tags[50706]
        return cls.from_samples(
            samples,
            bits_per_sample=bits,
            cfa_pattern=cfa if len(cfa) == 4 else _DEFAULT_CFA,
            # Keep absolute CFA phase when this tile is normalized locally.
            phase_origin=((base_phase[0] + y0) & 1, (base_phase[1] + x0) & 1),
            black_level=black or 0.0,
            white_level=white or ((1 << bits) - 1,),
            active_area=tile_area,
            white_balance=wb if len(wb) == 4 else (1.0, 1.0, 1.0, 1.0),
            orientation=int(tags.get(274, 1)),
            source_id=source_id,
            source_version=source_version,
            metadata=metadata,
        )

    @property
    def height(self) -> int:
        return int(self.samples.shape[0])

    @property
    def width(self) -> int:
        return int(self.samples.shape[1])

    @property
    def shape(self) -> tuple[int, int]:
        return self.samples.shape

    @property
    def dtype(self) -> np.dtype:
        return self.samples.dtype

    @property
    def nbytes(self) -> int:
        return int(self.samples.nbytes)

    def cache_key(self, *, include_source: bool = True) -> str:
        """Return a stable metadata key without hashing all sensor pixels."""
        payload = {
            "shape": self.shape,
            "dtype": self.samples.dtype.str,
            "bits": self.bits_per_sample,
            "cfa": self.cfa_pattern,
            "phase": self.phase_origin,
            "black": self.black_level,
            "white": self.white_level,
            "active": self.active_area,
            "wb": self.white_balance,
            "exposure": self.exposure_scale,
            "orientation": self.orientation,
            "source_id": self.source_id if include_source else "",
            "source_version": self.source_version if include_source else "",
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha1(encoded).hexdigest()

    def phase_index(self, row: int, column: int) -> int:
        """Return the CFA plane index at an absolute sensor coordinate."""
        row_phase = (int(row) + self.phase_origin[0]) & 1
        col_phase = (int(column) + self.phase_origin[1]) & 1
        return row_phase * 2 + col_phase

    def plane(self, index: int) -> np.ndarray:
        """Return a strided CFA plane view; no demosaic or copy is performed."""
        index = int(index)
        if not 0 <= index < 4:
            raise ValueError("CFA plane index must be in [0, 3]")
        row_phase, col_phase = divmod(index, 2)
        row_phase = (row_phase - self.phase_origin[0]) & 1
        col_phase = (col_phase - self.phase_origin[1]) & 1
        return self.samples[row_phase::2, col_phase::2]

    def normalized_headroom(self, *, apply_white_balance: bool = False) -> np.ndarray:
        """Return float32 black-normalized values without upper clamping."""
        samples = self.samples.astype(np.float32, copy=False)
        output = np.empty_like(samples, dtype=np.float32)
        for index in range(4):
            row_phase, col_phase = divmod(index, 2)
            row_phase = (row_phase - self.phase_origin[0]) & 1
            col_phase = (col_phase - self.phase_origin[1]) & 1
            denom = max(float(self.white_level[index] - self.black_level[index]), 1e-12)
            values = (samples[row_phase::2, col_phase::2] - float(self.black_level[index])) / denom
            values = np.maximum(values, 0.0)
            if apply_white_balance:
                values = values * float(self.white_balance[index])
            output[row_phase::2, col_phase::2] = values
        output *= np.float32(self.exposure_scale)
        return output

    def normalized_headroom_region(
        self,
        y0: int,
        y1: int,
        x0: int,
        x1: int,
        *,
        apply_white_balance: bool = False,
    ) -> np.ndarray:
        """Normalize one sensor-domain region without materializing the frame.

        The phase calculation uses absolute sensor coordinates.  Consequently
        a block beginning at an odd row/column never silently changes CFA
        phase, which is the common source of seams in tiled RAW pipelines.
        """
        y0, y1, x0, x1 = int(y0), int(y1), int(x0), int(x1)
        if not (0 <= y0 <= y1 <= self.height and 0 <= x0 <= x1 <= self.width):
            raise ValueError("RAW region is outside the frame")
        source = self.samples[y0:y1, x0:x1].astype(np.float32, copy=False)
        output = np.empty(source.shape, dtype=np.float32)
        local_rows = np.arange(y1 - y0, dtype=np.intp)
        local_cols = np.arange(x1 - x0, dtype=np.intp)
        for index in range(4):
            plane_row, plane_col = divmod(index, 2)
            rows = local_rows[((local_rows + y0 + self.phase_origin[0]) & 1) == plane_row]
            cols = local_cols[((local_cols + x0 + self.phase_origin[1]) & 1) == plane_col]
            if rows.size == 0 or cols.size == 0:
                continue
            denom = max(float(self.white_level[index] - self.black_level[index]), 1e-12)
            values = (source[np.ix_(rows, cols)] - float(self.black_level[index])) / denom
            values = np.maximum(values, 0.0)
            if apply_white_balance:
                values = values * float(self.white_balance[index])
            output[np.ix_(rows, cols)] = values
        output *= np.float32(self.exposure_scale)
        return output

    def green_guide(self, *, apply_white_balance: bool = True) -> np.ndarray:
        """Build a CFA-phase-aware half-resolution guide without RGB demosaic."""
        normalized = self.normalized_headroom(apply_white_balance=apply_white_balance)
        green_indices = [index for index, value in enumerate(self.cfa_pattern) if int(value) == 1]

        def normalized_plane(index: int) -> np.ndarray:
            plane_row, plane_col = divmod(int(index), 2)
            row_phase = (plane_row - self.phase_origin[0]) & 1
            col_phase = (plane_col - self.phase_origin[1]) & 1
            return normalized[row_phase::2, col_phase::2]

        if len(green_indices) != 2:
            return normalized_plane(0).astype(np.float32, copy=False)
        planes = [normalized_plane(index).astype(np.float32, copy=False) for index in green_indices]
        # Use the common dimensions for odd sensor sizes.  The phase is kept
        # explicit; no interpolation across a missing CFA sample is performed.
        height = min(item.shape[0] for item in planes)
        width = min(item.shape[1] for item in planes)
        return ((planes[0][:height, :width] + planes[1][:height, :width]) * 0.5).astype(np.float32, copy=False)


def raw_frame_from_dng(frame: Any, *, source_id: str = "", source_version: str = "") -> RawMosaicFrame:
    """Compatibility helper for callers that already own a ``DNGFrame``."""
    return RawMosaicFrame.from_dng(frame, source_id=source_id, source_version=source_version)


__all__ = ["RawMosaicFrame", "raw_frame_from_dng"]
