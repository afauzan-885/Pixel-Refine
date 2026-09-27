"""Streaming weighted HDR policy using the dedicated weighted-average TCM."""

from __future__ import annotations

import numpy as np

from .runtime import accumulate_weighted_aot, compute_weights_aot


_LAPLACIAN_4 = np.asarray(
    [[0.0, 1.0, 0.0], [1.0, -4.0, 1.0], [0.0, 1.0, 0.0]],
    dtype=np.float32,
)


def rgb_to_gray(rgb: np.ndarray) -> np.ndarray:
    """Convert RGB [0, 1] data to the luma used by the Taichi HDR weights."""
    image = np.ascontiguousarray(rgb, dtype=np.float32)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError(f"expected RGB [H, W, 3], got {image.shape}")
    return np.ascontiguousarray(
        image[..., 0] * 0.299
        + image[..., 1] * 0.587
        + image[..., 2] * 0.114,
        dtype=np.float32,
    )


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    """Decode the sRGB transfer curve for relative radiance output."""
    value = np.clip(np.asarray(rgb, dtype=np.float32), 0.0, 1.0)
    return np.ascontiguousarray(
        np.where(value <= 0.04045, value / 12.92, ((value + 0.055) / 1.055) ** 2.4),
        dtype=np.float32,
    )


def estimate_noise_taichi(gray: np.ndarray, session) -> float:
    """Estimate noise on Taichi's selected backend; failures stay explicit."""
    from taichi_vision import taichi_aot
    from taichi_vision.taichi_algorithm.enhancement.estimate_noise import (
        estimate_noise,
    )

    if min(gray.shape[:2]) < 8:
        return 1e-3

    gray_gpu = session.own(
        taichi_aot.upload(np.ascontiguousarray(gray, dtype=np.float32))
    )
    try:
        _, raw_sigma = estimate_noise(gray_gpu, session=session)
    finally:
        session.release_buffer(gray_gpu)
    return max(float(raw_sigma), 1e-3)


class WeightedHDRFusion:
    """O(HW) weighted accumulator; only one input frame is needed at a time."""

    def __init__(self, shape: tuple[int, int, int], *, radiance_enabled: bool):
        h, w, channels = (int(v) for v in shape)
        if h < 1 or w < 1 or channels != 3:
            raise ValueError(f"unsupported HDR frame shape: {shape}")
        self.shape = (h, w, channels)
        self.radiance_enabled = bool(radiance_enabled)
        self._ldr_sum = np.zeros(self.shape, dtype=np.float32)
        self._weight_sum_rgb = np.zeros(self.shape, dtype=np.float32)
        self._ones_rgb = np.ones(self.shape, dtype=np.float32)
        self._radiance_sum = (
            np.zeros(self.shape, dtype=np.float32)
            if self.radiance_enabled
            else None
        )
        self._frame_count = 0

    def add_frame(
        self,
        rgb: np.ndarray,
        *,
        noise_sigma: float,
        valid_mask: np.ndarray | None = None,
        policy_weight: np.ndarray | None = None,
        radiance_rgb: np.ndarray | None = None,
    ) -> np.ndarray:
        image = np.ascontiguousarray(rgb, dtype=np.float32)
        if image.shape != self.shape:
            raise ValueError(
                f"HDR frames must have identical shapes; expected {self.shape}, "
                f"got {image.shape}"
            )
        if not np.isfinite(image).all():
            raise ValueError("HDR frame contains non-finite values")

        from taichi_vision.taichi_algorithm.image_processing.extended_aot import (
            filter2d_aot,
        )

        gray = rgb_to_gray(image)
        laplacian = np.abs(filter2d_aot(gray, _LAPLACIAN_4)).astype(np.float32)
        weights = compute_weights_aot(
            image,
            laplacian,
            noise_sigma=max(float(noise_sigma), 1e-3),
            noise_power=2.0,
            exposure_sigma=0.2,
            exposure_power=1.0,
            detail_power=1.0,
            saturation_power=1.0,
        )

        if valid_mask is not None:
            if valid_mask.shape != weights.shape:
                raise ValueError("alignment validity mask must match the frame")
            weights *= np.asarray(valid_mask, dtype=np.float32)
        if policy_weight is not None:
            if policy_weight.shape != weights.shape:
                raise ValueError("patch policy map must match the frame")
            weights *= np.maximum(np.asarray(policy_weight, dtype=np.float32), 0.0)
        weights = np.ascontiguousarray(weights, dtype=np.float32)

        self._ldr_sum = accumulate_weighted_aot(image, weights, self._ldr_sum)
        self._weight_sum_rgb = accumulate_weighted_aot(
            self._ones_rgb, weights, self._weight_sum_rgb
        )

        if self.radiance_enabled:
            if radiance_rgb is None or radiance_rgb.shape != self.shape:
                raise ValueError("radiance-enabled fusion requires matching linear RGB")
            self._radiance_sum = accumulate_weighted_aot(
                np.ascontiguousarray(radiance_rgb, dtype=np.float32),
                weights,
                self._radiance_sum,
            )
        self._frame_count += 1
        return weights

    def finalize(self, reference_rgb: np.ndarray):
        if self._frame_count < 1:
            raise ValueError("cannot finalize an empty HDR fusion")
        reference = np.ascontiguousarray(reference_rgb, dtype=np.float32)
        if reference.shape != self.shape:
            raise ValueError("reference shape does not match accumulated frames")
        denominator = self._weight_sum_rgb[..., 0]
        ldr = reference.copy()
        np.divide(
            self._ldr_sum,
            denominator[..., None],
            out=ldr,
            where=denominator[..., None] > 1e-8,
        )
        ldr = np.clip(ldr, 0.0, 1.0).astype(np.float32, copy=False)

        radiance = None
        if self.radiance_enabled:
            radiance = np.zeros(self.shape, dtype=np.float32)
            np.divide(
                self._radiance_sum,
                denominator[..., None],
                out=radiance,
                where=denominator[..., None] > 1e-8,
            )
            radiance = np.maximum(radiance, 0.0).astype(np.float32, copy=False)
        return ldr, radiance


__all__ = [
    "WeightedHDRFusion",
    "estimate_noise_taichi",
    "rgb_to_gray",
    "srgb_to_linear",
]
