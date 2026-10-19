"""RAW-native result container and minimal, interoperable DNG persistence.

The result keeps the fused Bayer mosaic in normalized sensor space.  The GUI
uses ``preview_rgb`` only; it is never fed back into RAW accumulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from .metadata import (
    _apply_baked_orientation,
    _baked_cfa_pattern,
    extract_source_dng_metadata,
    normalize_cfa_rgb_codes,
)


@dataclass
class RawPipelineResult:
    """One Bayer-domain fusion result plus its one-time RGB preview."""

    normalized_mosaic: np.ndarray
    preview_rgb: np.ndarray
    reference_frame: object
    source_paths: Sequence[str | Path]
    report: dict | None = None

    def quantized_mosaic(self, bits_per_sample: int | None = None) -> np.ndarray:
        """Encode the normalized result at the requested sensor-code precision."""
        normalized = np.asarray(self.normalized_mosaic, dtype=np.float32)
        frame = self.reference_frame
        if normalized.shape != tuple(frame.shape):
            raise ValueError("RAW Native result shape no longer matches its reference CFA")
        if not np.isfinite(normalized).all():
            raise ValueError("RAW Native result contains non-finite sensor values")
        bits = int(frame.bits_per_sample if bits_per_sample is None else bits_per_sample)
        if not 1 <= bits <= 16:
            raise ValueError("DNG output bit depth must be between 1 and 16")
        maximum = (1 << bits) - 1
        dtype = np.uint8 if bits <= 8 else np.uint16
        values = normalized / np.float32(frame.exposure_scale)
        return np.clip(np.rint(values * np.float32(maximum)), 0, maximum).astype(dtype)

    def save_dng(self, path: str | Path) -> str:
        """Write a self-contained derived DNG.

        The writer has a scalar black/white-level ABI, so sensor values are
        encoded as canonical normalized code values (black=0, white=max).
        Camera colour tags, EXIF, and GPS are injected into their proper IFDs.
        """
        from taichi_vision.taichi_algorithm.compression import save_dng_aot

        frame = self.reference_frame
        bits = 16
        mosaic = _apply_baked_orientation(
            self.quantized_mosaic(bits_per_sample=bits), int(frame.orientation)
        )
        metadata = {
            "cfa_pattern": normalize_cfa_rgb_codes(_baked_cfa_pattern(frame)),
            "orientation": 1,
            "black_level": 0,
            "white_level": (1 << bits) - 1,
            "rows_per_strip": min(256, int(frame.height)),
        }
        source_path = getattr(frame, "source_id", "") or (
            str(self.source_paths[0]) if self.source_paths else ""
        )
        metadata.update(
            extract_source_dng_metadata(frame, mosaic.shape, source_path=source_path)
        )

        target = Path(path)
        save_dng_aot(
            mosaic,
            target,
            metadata=metadata,
            # Keep RAW Native exports on the tested path: this writer's
            # Deflate DNG currently fails the project's LibRaw round-trip.
            compression="none",
            bits_per_sample=bits,
        )
        return str(target)


__all__ = ["RawPipelineResult"]
