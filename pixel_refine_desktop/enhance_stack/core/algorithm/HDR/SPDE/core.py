"""SPDE-MR's streaming fusion policy around the compiled Taichi score maps."""

from __future__ import annotations

import numpy as np

from ..weighted_average.core import WeightedHDRFusion, rgb_to_gray
from .runtime import score_patch_maps_aot


PATCH_SIZE = 8
PATCH_STRIDE = 4
STRUCTURE_CORRELATION_MIN = 0.8
EXPOSURE_CENTER = 0.5
EXPOSURE_SIGMA = 0.2


def _score_patch_maps(
    reference_gray: np.ndarray,
    frame_gray: np.ndarray,
    *,
    patch_size: int = PATCH_SIZE,
    stride: int = PATCH_STRIDE,
    structure_threshold: float = STRUCTURE_CORRELATION_MIN,
    valid_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return E×C×S, stable-structure, and fusion-policy maps from Taichi AOT."""
    reference = np.ascontiguousarray(reference_gray, dtype=np.float32)
    frame = np.ascontiguousarray(frame_gray, dtype=np.float32)
    if reference.ndim != 2 or frame.shape != reference.shape:
        raise ValueError("SPDE-MR requires same-size grayscale reference and frame")
    if patch_size != PATCH_SIZE or stride != PATCH_STRIDE:
        raise ValueError("the initial SPDE-MR contract uses 8x8 patches at stride 4")
    height, width = reference.shape
    if height < patch_size or width < patch_size:
        raise ValueError("SPDE-MR needs frames at least 8x8 pixels")
    return score_patch_maps_aot(
        reference,
        frame,
        valid_mask=valid_mask,
        patch_size=patch_size,
        stride=stride,
        exposure_center=EXPOSURE_CENTER,
        exposure_sigma=EXPOSURE_SIGMA,
        structure_threshold=structure_threshold,
    )


def score_patches(
    reference_gray: np.ndarray,
    frame_gray: np.ndarray,
    *,
    patch_size: int = PATCH_SIZE,
    stride: int = PATCH_STRIDE,
    structure_threshold: float = STRUCTURE_CORRELATION_MIN,
) -> tuple[np.ndarray, np.ndarray]:
    """Return full-resolution patch quality and stable-structure maps."""
    quality, stable, _ = _score_patch_maps(
        reference_gray,
        frame_gray,
        patch_size=patch_size,
        stride=stride,
        structure_threshold=structure_threshold,
    )
    return quality, stable


class SPDEMRFusion(WeightedHDRFusion):
    """Weighted HDR with patch correlation rejection and single-frame priority."""

    def __init__(self, reference_rgb: np.ndarray, *, radiance_enabled: bool):
        reference = np.ascontiguousarray(reference_rgb, dtype=np.float32)
        super().__init__(reference.shape, radiance_enabled=radiance_enabled)
        self.reference_gray = rgb_to_gray(reference)
        self._dynamic = np.zeros(reference.shape[:2], dtype=bool)
        self._best_quality = np.full(reference.shape[:2], -1.0, dtype=np.float32)
        self._best_rgb = np.empty_like(reference)
        self._best_radiance = (
            np.empty_like(reference) if radiance_enabled else None
        )

    def add_spde_frame(
        self,
        rgb: np.ndarray,
        *,
        noise_sigma: float,
        valid_mask: np.ndarray | None = None,
        radiance_rgb: np.ndarray | None = None,
        is_reference: bool = False,
    ) -> None:
        image = np.ascontiguousarray(rgb, dtype=np.float32)
        valid = None
        if valid_mask is not None:
            valid = np.asarray(valid_mask, dtype=bool)
            if valid.shape != self._dynamic.shape:
                raise ValueError("alignment validity mask must match the frame")
        quality, stable, policy_weight = _score_patch_maps(
            self.reference_gray,
            rgb_to_gray(image),
            valid_mask=valid,
        )

        if not is_reference:
            if valid is None:
                self._dynamic |= ~stable
            else:
                self._dynamic |= valid & ~stable
        self.add_frame(
            image,
            noise_sigma=noise_sigma,
            valid_mask=valid,
            policy_weight=policy_weight,
            radiance_rgb=radiance_rgb,
        )

        better = quality > self._best_quality
        np.copyto(self._best_rgb, image, where=better[..., None])
        self._best_quality[better] = quality[better]
        if self.radiance_enabled:
            if radiance_rgb is None:
                raise ValueError("radiance-enabled SPDE-MR needs each linear frame")
            np.copyto(
                self._best_radiance,
                np.asarray(radiance_rgb, dtype=np.float32),
                where=better[..., None],
            )

    def finalize(self, reference_rgb: np.ndarray):
        ldr, radiance = super().finalize(reference_rgb)
        if np.any(self._dynamic):
            np.copyto(ldr, self._best_rgb, where=self._dynamic[..., None])
            if radiance is not None:
                np.copyto(
                    radiance,
                    self._best_radiance,
                    where=self._dynamic[..., None],
                )
        return ldr, radiance


__all__ = [
    "PATCH_SIZE",
    "PATCH_STRIDE",
    "STRUCTURE_CORRELATION_MIN",
    "SPDEMRFusion",
    "score_patches",
]
