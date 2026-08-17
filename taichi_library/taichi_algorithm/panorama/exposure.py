"""Robust exposure compensation for overlapping panorama images.

The estimator works on already aligned images and optional valid masks.  It
fits a per-image, per-channel affine correction relative to a reference frame.
The NumPy path is the robust trimmed reference; ``backend="taichi"`` runs a
bounded CPU-JIT overlap reduction plus JIT application (without the percentile
trim), while an AOT artifact is not currently qualified and therefore
``backend="aot"`` fails closed.
"""

from dataclasses import dataclass
import importlib
import os
from typing import Any, Sequence

import numpy as np

from ..pipeline_common import as_float32_image, validate_same_shape


MAX_EXPOSURE_PIXELS = 55_000_000
DEFAULT_MAX_WORKING_BYTES = 1_500_000_000

try:
    _ti = importlib.import_module("taichi")
except ImportError:  # pragma: no cover - minimal installations
    _ti = None


def _ensure_taichi_cpu() -> Any:
    """Initialise/validate the explicit CPU JIT backend without AOT fallback."""

    if _ti is None:
        raise ImportError("backend='taichi' requires the taichi package")
    from taichi.lang import impl

    runtime = impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        _ti.init(arch=_ti.cpu, offline_cache=False)
    else:
        current_arch = getattr(getattr(_ti, "cfg", None), "arch", None)
        if current_arch != _ti.cpu:
            raise RuntimeError(
                f"backend='taichi' requires a CPU JIT runtime; current arch is {current_arch}"
            )
    return _ti


if _ti is not None:

    @_ti.kernel
    def _exposure_stats_kernel(
        stack: _ti.types.ndarray(dtype=_ti.f32, ndim=4),
        masks: _ti.types.ndarray(dtype=_ti.i32, ndim=3),
        stats: _ti.types.ndarray(dtype=_ti.f64, ndim=3),
        reference_index: _ti.i32,
    ):
        """Accumulate overlap sufficient statistics for affine compensation."""

        for frame, y, x, channel in _ti.ndrange(stack.shape[0], stack.shape[1], stack.shape[2], stack.shape[3]):
            if frame != reference_index and masks[frame, y, x] != 0 and masks[reference_index, y, x] != 0:
                target = _ti.cast(stack[frame, y, x, channel], _ti.f64)
                reference = _ti.cast(stack[reference_index, y, x, channel], _ti.f64)
                _ti.atomic_add(stats[frame, channel, 0], 1.0)
                _ti.atomic_add(stats[frame, channel, 1], target)
                _ti.atomic_add(stats[frame, channel, 2], reference)
                _ti.atomic_add(stats[frame, channel, 3], target * target)
                _ti.atomic_add(stats[frame, channel, 4], target * reference)

    @_ti.kernel
    def _apply_exposure_gray_kernel(
        src: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        dst: _ti.types.ndarray(dtype=_ti.f32, ndim=2),
        gain: _ti.f32,
        offset: _ti.f32,
        low: _ti.f32,
        high: _ti.f32,
        clip_enabled: _ti.i32,
    ):
        for y, x in _ti.ndrange(src.shape[0], src.shape[1]):
            value = src[y, x] * gain + offset
            if clip_enabled != 0:
                value = _ti.min(_ti.max(value, low), high)
            dst[y, x] = value

    @_ti.kernel
    def _apply_exposure_color_kernel(
        src: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        dst: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        gains: _ti.types.ndarray(dtype=_ti.f32, ndim=1),
        offsets: _ti.types.ndarray(dtype=_ti.f32, ndim=1),
        low: _ti.f32,
        high: _ti.f32,
        clip_enabled: _ti.i32,
    ):
        for y, x, channel in _ti.ndrange(src.shape[0], src.shape[1], src.shape[2]):
            value = src[y, x, channel] * gains[channel] + offsets[channel]
            if clip_enabled != 0:
                value = _ti.min(_ti.max(value, low), high)
            dst[y, x, channel] = value


@dataclass(frozen=True)
class ExposureCompensation:
    """Per-frame affine correction ``corrected = image * gain + offset``."""

    gains: np.ndarray
    offsets: np.ndarray
    reference_index: int
    mode: str
    backend: str
    overlap_counts: np.ndarray


def _backend_name(backend: str) -> str:
    value = str(backend).lower()
    if value not in {"numpy", "taichi", "aot"}:
        raise ValueError("backend must be 'numpy', 'taichi', or 'aot'")
    if value == "aot":
        raise NotImplementedError(
            "exposure compensation has no qualified AOT artifact; use backend='numpy' or 'taichi' explicitly"
        )
    return value


def _taichi_estimate_from_stats(
    arrays: Sequence[np.ndarray],
    masks: Sequence[np.ndarray],
    *,
    reference_index: int,
    mode: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Estimate affine parameters from a Taichi overlap reduction."""

    taichi = _ensure_taichi_cpu()
    channel_count = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    stack = np.stack(
        [array if array.ndim == 3 else array[..., None] for array in arrays],
        axis=0,
    ).astype(np.float32, copy=False)
    mask_stack = np.stack(masks, axis=0).astype(np.int32, copy=False)
    stats = np.zeros((len(arrays), channel_count, 5), dtype=np.float64)
    _exposure_stats_kernel(stack, mask_stack, stats, int(reference_index))
    taichi.sync()
    gains = np.ones((len(arrays), channel_count), dtype=np.float32)
    offsets = np.zeros((len(arrays), channel_count), dtype=np.float32)
    counts = np.rint(stats[:, :, 0]).astype(np.int64).max(axis=1)
    for frame in range(len(arrays)):
        if frame == int(reference_index):
            continue
        for channel in range(channel_count):
            count, sum_target, sum_reference, sum_target_sq, sum_cross = stats[frame, channel]
            if count < 8.0:
                continue
            if mode == "gain":
                gain = sum_cross / sum_target_sq if sum_target_sq > 1.0e-12 else 1.0
                offset = 0.0
            else:
                determinant = sum_target_sq * count - sum_target * sum_target
                if determinant <= 1.0e-12:
                    gain, offset = 1.0, 0.0
                else:
                    gain = (sum_cross * count - sum_target * sum_reference) / determinant
                    offset = (sum_target_sq * sum_reference - sum_target * sum_cross) / determinant
            gains[frame, channel] = max(float(gain), 1.0e-6) if np.isfinite(gain) else 1.0
            offsets[frame, channel] = float(offset) if np.isfinite(offset) else 0.0
    return gains, offsets, counts


def _apply_taichi(
    arrays: Sequence[np.ndarray],
    gains: np.ndarray,
    offsets: np.ndarray,
    *,
    clip: tuple[float, float] | None,
) -> list[np.ndarray]:
    """Apply affine corrections with elementwise CPU-JIT kernels."""

    taichi = _ensure_taichi_cpu()
    if clip is None:
        low, high, enabled = 0.0, 0.0, 0
    else:
        low, high, enabled = float(clip[0]), float(clip[1]), 1
    result: list[np.ndarray] = []
    for index, image in enumerate(arrays):
        if image.ndim == 2:
            output = np.empty_like(image, dtype=np.float32)
            _apply_exposure_gray_kernel(
                image,
                output,
                float(gains[index, 0]),
                float(offsets[index, 0]),
                low,
                high,
                enabled,
            )
        else:
            output = np.empty_like(image, dtype=np.float32)
            frame_gains = np.ascontiguousarray(gains[index], dtype=np.float32)
            frame_offsets = np.ascontiguousarray(offsets[index], dtype=np.float32)
            _apply_exposure_color_kernel(
                image,
                output,
                frame_gains,
                frame_offsets,
                low,
                high,
                enabled,
            )
        result.append(np.ascontiguousarray(output, dtype=np.float32))
    taichi.sync()
    return result


def _validate_budget(images: Sequence[np.ndarray], max_pixels: int, max_working_bytes: int) -> None:
    pixels = int(images[0].shape[0]) * int(images[0].shape[1])
    if pixels < 1 or pixels > int(max_pixels):
        raise ValueError(f"exposure compensation has {pixels:,} pixels; maximum is {int(max_pixels):,}")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    # The Taichi path materialises the complete frame stack and mask stack;
    # include every frame in the preflight rather than only one pair.
    channels = 1 if images[0].ndim == 2 else int(images[0].shape[2])
    frame_count = len(images)
    estimate = pixels * (channels * 4 * (frame_count + 2) + frame_count)
    estimate += frame_count * channels * 5 * np.dtype(np.float64).itemsize
    if estimate > int(max_working_bytes):
        raise MemoryError(
            f"exposure compensation requires about {estimate} bytes, limit is {int(max_working_bytes)}"
        )


def _as_masks(masks: Any, n: int, shape: tuple[int, int]) -> list[np.ndarray]:
    if masks is None:
        return [np.ones(shape, dtype=bool) for _ in range(n)]
    if len(masks) != n:
        raise ValueError("masks length must match images")
    result = []
    for index, mask in enumerate(masks):
        array = np.asarray(mask, dtype=bool)
        if array.shape != shape:
            raise ValueError(f"masks[{index}] must have shape {shape}, got {array.shape}")
        result.append(array)
    return result


def _channels(image: np.ndarray) -> np.ndarray:
    if image.ndim == 2:
        return image[..., None]
    return image if image.shape[2] != 1 else image[..., :1]


def _sample_indices(indices: np.ndarray, max_samples: int) -> np.ndarray:
    if int(max_samples) < 16:
        raise ValueError("max_samples must be at least 16")
    if len(indices) <= int(max_samples):
        return indices
    # Evenly spaced selection is deterministic and avoids depending on a
    # global RNG state for reproducible panorama brightness.
    positions = np.linspace(0, len(indices) - 1, int(max_samples), dtype=np.int64)
    return indices[positions]


def _robust_affine(reference: np.ndarray, target: np.ndarray, mode: str) -> tuple[float, float]:
    """Fit one channel after symmetric 5/95-percentile trimming."""

    reference = np.asarray(reference, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    finite = np.isfinite(reference) & np.isfinite(target)
    reference, target = reference[finite], target[finite]
    if len(reference) < 8:
        return 1.0, 0.0
    residual_ref = np.percentile(reference, (2.0, 98.0))
    residual_tgt = np.percentile(target, (2.0, 98.0))
    keep = (
        (reference >= residual_ref[0])
        & (reference <= residual_ref[1])
        & (target >= residual_tgt[0])
        & (target <= residual_tgt[1])
    )
    reference, target = reference[keep], target[keep]
    if len(reference) < 8:
        return 1.0, 0.0
    if mode == "gain":
        denominator = float(np.dot(target, target))
        gain = float(np.dot(reference, target) / denominator) if denominator > 1.0e-12 else 1.0
        return max(gain, 1.0e-6), 0.0
    design = np.column_stack((target, np.ones(len(target), dtype=np.float64)))
    try:
        gain, offset = np.linalg.lstsq(design, reference, rcond=None)[0]
    except np.linalg.LinAlgError:
        return 1.0, 0.0
    if not np.isfinite(gain) or gain <= 1.0e-6:
        gain = 1.0
    if not np.isfinite(offset):
        offset = 0.0
    return float(gain), float(offset)


def estimate_exposure_compensation(
    images: Sequence[Any],
    *,
    masks: Sequence[Any] | None = None,
    reference_index: int = 0,
    mode: str = "gain_bias",
    max_samples: int = 200_000,
    backend: str = "numpy",
    max_pixels: int = MAX_EXPOSURE_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> ExposureCompensation:
    """Estimate robust gains/offsets that map each image to a reference.

    ``masks[i]`` marks pixels valid in image ``i`` after geometric warping.
    Frames with no overlap retain the identity correction and report a zero
    overlap count.  This is deliberate: inventing a brightness transform from
    unrelated regions is worse than exposing an unresolved seam to the caller.
    """

    backend_name = _backend_name(backend)
    arrays = validate_same_shape(images, name="images")
    _validate_budget(arrays, int(max_pixels), int(max_working_bytes))
    if not all(np.isfinite(array).all() for array in arrays):
        raise ValueError("images must contain only finite values")
    if mode not in {"gain", "gain_bias"}:
        raise ValueError("mode must be 'gain' or 'gain_bias'")
    n = len(arrays)
    if not 0 <= int(reference_index) < n:
        raise ValueError("reference_index is out of range")
    reference_index = int(reference_index)
    valid_masks = _as_masks(masks, n, arrays[0].shape[:2])
    channel_count = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    if backend_name == "taichi":
        gains, offsets, overlap_counts = _taichi_estimate_from_stats(
            arrays,
            valid_masks,
            reference_index=reference_index,
            mode=mode,
        )
        return ExposureCompensation(
            gains=np.ascontiguousarray(gains),
            offsets=np.ascontiguousarray(offsets),
            reference_index=reference_index,
            mode=str(mode),
            backend=backend_name,
            overlap_counts=np.ascontiguousarray(overlap_counts),
        )
    gains = np.ones((n, channel_count), dtype=np.float32)
    offsets = np.zeros((n, channel_count), dtype=np.float32)
    overlap_counts = np.zeros(n, dtype=np.int64)
    ref_channels = _channels(arrays[reference_index])
    for index, array in enumerate(arrays):
        if index == reference_index:
            continue
        overlap = valid_masks[reference_index] & valid_masks[index]
        flat_indices = np.flatnonzero(overlap.ravel())
        overlap_counts[index] = int(len(flat_indices))
        if len(flat_indices) < 8:
            continue
        flat_indices = _sample_indices(flat_indices, int(max_samples))
        target_channels = _channels(array)
        for channel in range(channel_count):
            ref_values = ref_channels[..., channel].ravel()[flat_indices]
            target_values = target_channels[..., channel].ravel()[flat_indices]
            gains[index, channel], offsets[index, channel] = _robust_affine(
                ref_values,
                target_values,
                mode,
            )
    return ExposureCompensation(
        gains=np.ascontiguousarray(gains),
        offsets=np.ascontiguousarray(offsets),
        reference_index=reference_index,
        mode=str(mode),
        backend=backend_name,
        overlap_counts=np.ascontiguousarray(overlap_counts),
    )


def apply_exposure_compensation(
    images: Sequence[Any],
    compensation: ExposureCompensation,
    *,
    clip: tuple[float, float] | None = None,
    backend: str = "numpy",
) -> list[np.ndarray]:
    """Apply a previously estimated correction without re-estimating it."""

    backend_name = _backend_name(backend)
    arrays = validate_same_shape(images, name="images")
    gains = np.asarray(compensation.gains, dtype=np.float32)
    offsets = np.asarray(compensation.offsets, dtype=np.float32)
    if gains.ndim != 2 or offsets.shape != gains.shape or gains.shape[0] != len(arrays):
        raise ValueError("compensation gains/offsets shape must be (frame_count, channel_count)")
    channel_count = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    if gains.shape[1] != channel_count:
        raise ValueError("compensation channel count does not match images")
    if clip is not None:
        if len(clip) != 2 or not np.isfinite(clip).all() or float(clip[0]) >= float(clip[1]):
            raise ValueError("clip must be a finite increasing (low, high) pair")
        low, high = float(clip[0]), float(clip[1])
    else:
        low = high = 0.0
    if backend_name == "taichi":
        return _apply_taichi(arrays, gains, offsets, clip=None if clip is None else (low, high))
    result: list[np.ndarray] = []
    for index, image in enumerate(arrays):
        if image.ndim == 2:
            corrected = image * gains[index, 0] + offsets[index, 0]
        else:
            corrected = image * gains[index][None, None, :] + offsets[index][None, None, :]
        if clip is not None:
            corrected = np.clip(corrected, low, high)
        result.append(np.ascontiguousarray(corrected, dtype=np.float32))
    return result


def compensate_exposure(
    images: Sequence[Any],
    *,
    masks: Sequence[Any] | None = None,
    reference_index: int = 0,
    mode: str = "gain_bias",
    max_samples: int = 200_000,
    clip: tuple[float, float] | None = None,
    backend: str = "numpy",
    max_pixels: int = MAX_EXPOSURE_PIXELS,
    max_working_bytes: int = DEFAULT_MAX_WORKING_BYTES,
) -> tuple[list[np.ndarray], ExposureCompensation]:
    """Estimate and apply robust exposure compensation in one call."""

    compensation = estimate_exposure_compensation(
        images,
        masks=masks,
        reference_index=reference_index,
        mode=mode,
        max_samples=max_samples,
        backend=backend,
        max_pixels=max_pixels,
        max_working_bytes=max_working_bytes,
    )
    return apply_exposure_compensation(images, compensation, backend=backend, clip=clip), compensation


__all__ = [
    "ExposureCompensation",
    "estimate_exposure_compensation",
    "apply_exposure_compensation",
    "compensate_exposure",
]
