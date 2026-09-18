"""Container for Sensor-Native RAW Fusion results and DNG persistence."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, Tuple

import numpy as np

from .raw_metadata import (
    _apply_baked_orientation,
    _baked_cfa_pattern,
    extract_source_dng_metadata,
)


@dataclass
class RawNativeResult:
    """Sensor-native RAW fusion product with single-demosaic preview.

    Attributes:
        normalized_mosaic: 2D float32 array of fused Bayer mosaic normalized to [0, 1].
        preview_rgb: 3D array (H, W, 3) of high-quality Hamilton demosaic for GUI display.
        reference_frame: RawMosaicFrame representation of the reference DNG.
        source_paths: Sequence of source image file paths.
        report: Optional alignment/fusion report metrics.
        linear_rgb: Optional raw linear RGB array if requested.
        output_format: "RAW Native" or "RGB Linear".
    """

    normalized_mosaic: np.ndarray
    preview_rgb: np.ndarray
    reference_frame: object
    source_paths: Sequence[str | Path]
    report: object = None
    linear_rgb: np.ndarray | None = None
    output_format: str = "RAW Native"

    def _quantized_mosaic(self) -> np.ndarray:
        """Encode normalized CFA values back to sensor integer code space."""
        frame = self.reference_frame
        maximum_code = (1 << int(frame.bits_per_sample)) - 1
        output = np.empty(frame.shape, dtype=frame.samples.dtype)
        normalized = np.asarray(self.normalized_mosaic, dtype=np.float32)
        if not np.isfinite(normalized).all():
            raise ValueError(
                "RAW Native fusion produced non-finite sensor samples; "
                "refusing to encode a corrupted derived DNG."
            )
        values = normalized / np.float32(frame.exposure_scale)
        output[...] = np.clip(
            np.rint(values * np.float32(maximum_code)), 0, maximum_code
        ).astype(output.dtype)
        return output

    def baked_oriented_mosaic(self) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """Bake source orientation into mosaic pixels and matching CFA pattern."""
        mosaic = _apply_baked_orientation(
            self._quantized_mosaic(), int(self.reference_frame.orientation)
        )
        return np.ascontiguousarray(mosaic), _baked_cfa_pattern(self.reference_frame)

    def save_dng(self, path: str | Path) -> str:
        """Persist a derived sensor-native mosaiced DNG with complete camera metadata."""
        from taichi_vision.taichi_algorithm.compression import save_dng_aot

        frame = self.reference_frame
        mosaic, cfa_pattern = self.baked_oriented_mosaic()
        source_path = getattr(frame, "source_id", "") or (
            str(self.source_paths[0]) if self.source_paths else ""
        )
        metadata = {
            "cfa_pattern": cfa_pattern,
            "orientation": 1,
            "black_level": 0,
            "white_level": (1 << int(frame.bits_per_sample)) - 1,
            "rows_per_strip": min(256, int(frame.height)),
        }
        metadata.update(
            extract_source_dng_metadata(
                frame, mosaic.shape, source_path=source_path
            )
        )
        target = Path(path)
        save_dng_aot(
            mosaic,
            target,
            metadata=metadata,
            compression="none",
            bits_per_sample=int(frame.bits_per_sample),
        )
        return str(target)

    def save_linear_tiff(self, path: str | Path) -> str:
        """Persist the one-demosaic RGB-linear result without display tone-mapping."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            save_image,
        )

        rgb = self.linear_rgb if self.linear_rgb is not None else self.preview_rgb
        encoded = np.clip(np.asarray(rgb, dtype=np.float32), 0.0, 1.0)
        if encoded.max() <= 1.0:
            encoded = np.rint(encoded * 65535.0).astype(np.uint16)
        else:
            encoded = np.clip(encoded, 0.0, 65535.0).astype(np.uint16)

        if not save_image(encoded, str(path), reference_image_path=None):
            raise OSError(f"Failed to save RGB Linear TIFF: {path}")

        source_path = getattr(self.reference_frame, "source_id", "") or (
            str(self.source_paths[0]) if self.source_paths else ""
        )
        if source_path:
            try:
                from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                    _copy_output_metadata,
                )

                _copy_output_metadata(source_path, str(path))
            except Exception as exc:
                print(f"[RawNativeResult] TIFF metadata preservation note: {exc}")
        return str(path)


__all__ = ["RawNativeResult"]
