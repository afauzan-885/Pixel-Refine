"""Per-pixel source selection for already aligned, demosaiced RGB brackets."""

from __future__ import annotations

import numpy as np


class HDRMaskFusion:
    """Select the brightest valid source at each pixel.

    Input frames must be same-size RGB arrays in [0, 1]. ``exposure_scale`` is
    the source exposure relative to the selected reference exposure. If
    exposure metadata is reliable, the selected sample is divided by this scale
    to express it at the reference exposure.

    The initial implementation uses a hard source mask. It rejects a candidate
    when any RGB channel reaches the saturation threshold, then prefers the
    candidate with the strongest remaining signal. If every candidate clips at
    a pixel, it retains the least-clipped candidate.
    """

    def __init__(
        self,
        shape: tuple[int, int, int],
        *,
        radiance_enabled: bool,
        saturation_threshold: float = 0.985,
    ):
        height, width, channels = (int(value) for value in shape)
        if height < 1 or width < 1 or channels != 3:
            raise ValueError(f"unsupported HDR frame shape: {shape}")
        threshold = float(saturation_threshold)
        if not np.isfinite(threshold) or not 0.0 < threshold <= 1.0:
            raise ValueError("saturation_threshold must be in (0, 1]")

        self.shape = (height, width, channels)
        self.radiance_enabled = bool(radiance_enabled)
        self.saturation_threshold = threshold
        self._best_signal = np.full((height, width), -np.inf, dtype=np.float32)
        self._best_fallback = np.full((height, width), -np.inf, dtype=np.float32)
        self._has_valid_sample = np.zeros((height, width), dtype=bool)
        self._selected_rgb = np.zeros(self.shape, dtype=np.float32)
        self._selected_radiance = (
            np.zeros(self.shape, dtype=np.float32)
            if self.radiance_enabled
            else None
        )
        self.source_map = np.full((height, width), -1, dtype=np.int32)
        self._frame_count = 0

    def add_frame(
        self,
        rgb: np.ndarray,
        *,
        exposure_scale: float = 1.0,
        valid_mask: np.ndarray | None = None,
    ) -> np.ndarray:
        """Add one aligned RGB frame and return its selected-pixel mask."""
        image = np.ascontiguousarray(rgb, dtype=np.float32)
        if image.shape != self.shape:
            raise ValueError(
                f"HDR frames must have identical shapes; expected {self.shape}, "
                f"got {image.shape}"
            )
        if not np.isfinite(image).all():
            raise ValueError("HDR frame contains non-finite values")
        if np.any(image < 0.0) or np.any(image > 1.0):
            raise ValueError("HDR mask input must be normalized to [0, 1]")

        scale = float(exposure_scale)
        if not np.isfinite(scale) or scale <= 0.0:
            raise ValueError("exposure_scale must be finite and positive")

        if valid_mask is None:
            valid = np.ones(self.shape[:2], dtype=bool)
        else:
            valid = np.asarray(valid_mask, dtype=bool)
            if valid.shape != self.shape[:2]:
                raise ValueError("alignment validity mask must match the frame")

        # One RGB decision preserves color by taking all channels from one frame.
        peak = np.max(image, axis=2)
        luminance = (
            image[..., 0] * 0.2126
            + image[..., 1] * 0.7152
            + image[..., 2] * 0.0722
        )
        unsaturated = valid & (peak < self.saturation_threshold)
        selected = unsaturated & (
            ~self._has_valid_sample | (luminance > self._best_signal)
        )
        fallback_selected = (
            valid
            & ~unsaturated
            & ~self._has_valid_sample
            & (-peak > self._best_fallback)
        )

        # Any unsaturated sample wins over clipped samples. If every available
        # sample clips, use the one whose brightest channel is least clipped.
        if np.any(selected):
            self._selected_rgb[selected] = image[selected]
            self._best_signal[selected] = luminance[selected]
            self.source_map[selected] = self._frame_count
            self._has_valid_sample[selected] = True
        if np.any(fallback_selected):
            self._selected_rgb[fallback_selected] = image[fallback_selected]
            self._best_fallback[fallback_selected] = -peak[fallback_selected]
            self.source_map[fallback_selected] = self._frame_count

        if self.radiance_enabled:
            normalized = image / np.float32(scale)
            if np.any(selected):
                self._selected_radiance[selected] = normalized[selected]
            if np.any(fallback_selected):
                self._selected_radiance[fallback_selected] = normalized[
                    fallback_selected
                ]

        self._frame_count += 1
        return selected | fallback_selected

    def finalize(self, reference_rgb: np.ndarray):
        """Return selected RGB pixels and optional relative-radiance values."""
        if self._frame_count < 1:
            raise ValueError("cannot finalize an empty HDR mask fusion")
        reference = np.ascontiguousarray(reference_rgb, dtype=np.float32)
        if reference.shape != self.shape:
            raise ValueError("reference shape does not match selected frames")

        missing = self.source_map < 0
        self._selected_rgb[missing] = reference[missing]
        ldr = np.clip(self._selected_rgb, 0.0, 1.0).astype(
            np.float32, copy=False
        )

        radiance = None
        if self.radiance_enabled:
            self._selected_radiance[missing] = reference[missing]
            radiance = np.maximum(self._selected_radiance, 0.0).astype(
                np.float32, copy=False
            )
        return ldr, radiance


__all__ = ["HDRMaskFusion"]
