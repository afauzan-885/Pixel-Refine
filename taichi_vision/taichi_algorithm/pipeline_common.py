"""Shared contracts for the higher-level image and reconstruction pipelines.

The family modules in :mod:`taichi_algorithm` intentionally keep their
algorithm implementations local.  This module only owns the repetitive
boundary work that every pipeline needs: shape/dtype validation, grayscale
conversion, finite-value checks, stage timing, and a small, serialisable
report.  It does not import Taichi or select a backend, so it is safe to use
from compiler workers and backend-free tests.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import time
from typing import Any, Iterator, Mapping, Sequence

import numpy as np


def as_float32_image(value: Any, *, name: str = "image") -> np.ndarray:
    """Return a contiguous float32 grayscale/RGB image after validation."""

    array = np.ascontiguousarray(value, dtype=np.float32)
    if array.ndim not in (2, 3):
        raise ValueError(f"{name} must be HxW or HxWxC, got {array.shape}")
    if array.ndim == 3 and array.shape[2] not in (1, 3, 4):
        raise ValueError(f"{name} channel count must be 1, 3, or 4, got {array.shape}")
    if array.shape[0] < 1 or array.shape[1] < 1:
        raise ValueError(f"{name} must have non-empty spatial dimensions")
    return array


def as_float32_matrix(value: Any, shape: tuple[int, ...], *, name: str) -> np.ndarray:
    """Validate a small geometry matrix without changing its public dtype ABI."""

    array = np.ascontiguousarray(value, dtype=np.float32)
    if array.shape != shape:
        raise ValueError(f"{name} must have shape {shape}, got {array.shape}")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def as_gray_float32(image: Any, *, name: str = "image") -> np.ndarray:
    """Convert an HxW/HxWxC image to a contiguous float32 luminance plane."""

    array = as_float32_image(image, name=name)
    if array.ndim == 2 or array.shape[2] == 1:
        return array if array.ndim == 2 else array[..., 0]
    # Keep the same RGB convention used by the existing HDR and tone kernels.
    return np.ascontiguousarray(
        0.299 * array[..., 0] + 0.587 * array[..., 1] + 0.114 * array[..., 2],
        dtype=np.float32,
    )


def validate_same_shape(
    images: Sequence[Any],
    *,
    name: str = "images",
    channels: int | None = None,
) -> list[np.ndarray]:
    """Validate a non-empty stack and return contiguous float32 arrays."""

    if not images:
        raise ValueError(f"{name} must contain at least one image")
    arrays = [as_float32_image(image, name=f"{name}[{index}]") for index, image in enumerate(images)]
    shape = arrays[0].shape
    if any(array.shape != shape for array in arrays[1:]):
        raise ValueError(f"all {name} must have the same shape; first shape is {shape}")
    if channels is not None and (arrays[0].ndim != 3 or arrays[0].shape[2] != channels):
        raise ValueError(f"{name} must be HxWx{channels}, got {shape}")
    return arrays


def finite_fraction(value: Any) -> float:
    """Return the fraction of finite elements, safely handling empty arrays."""

    array = np.asarray(value)
    if array.size == 0:
        return 1.0
    return float(np.isfinite(array).mean())


def image_quality_metrics(reference: Any, candidate: Any) -> dict[str, float]:
    """Compute inexpensive, deterministic diagnostics for pipeline gates."""

    ref = as_float32_image(reference, name="reference")
    out = as_float32_image(candidate, name="candidate")
    if ref.shape != out.shape:
        raise ValueError(f"reference and candidate shapes differ: {ref.shape} vs {out.shape}")
    diff = np.asarray(out, dtype=np.float64) - np.asarray(ref, dtype=np.float64)
    abs_diff = np.abs(diff)
    mse = float(np.mean(diff * diff)) if diff.size else 0.0
    return {
        "finite_fraction": finite_fraction(out),
        "mean_abs_error": float(np.mean(abs_diff)) if diff.size else 0.0,
        "rmse": float(np.sqrt(mse)),
        "max_abs_error": float(np.max(abs_diff)) if diff.size else 0.0,
    }


@dataclass
class StageRecord:
    """Timing and output diagnostics for one pipeline stage."""

    name: str
    seconds: float
    output_shape: tuple[int, ...] | None = None
    output_dtype: str | None = None
    finite_fraction: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineReport:
    """Backend-neutral report shared by panorama/HDR/focus/3D pipelines."""

    pipeline: str
    backend: str = "unknown"
    device: str | None = None
    success: bool = True
    stages: list[StageRecord] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    @property
    def seconds(self) -> float:
        return float(sum(stage.seconds for stage in self.stages))

    def add_warning(self, message: str) -> None:
        self.warnings.append(str(message))

    def as_dict(self) -> dict[str, Any]:
        return {
            "pipeline": self.pipeline,
            "backend": self.backend,
            "device": self.device,
            "success": bool(self.success),
            "seconds": self.seconds,
            "stages": [
                {
                    "name": stage.name,
                    "seconds": stage.seconds,
                    "output_shape": stage.output_shape,
                    "output_dtype": stage.output_dtype,
                    "finite_fraction": stage.finite_fraction,
                    "metadata": dict(stage.metadata),
                }
                for stage in self.stages
            ],
            "metrics": dict(self.metrics),
            "warnings": list(self.warnings),
        }


@contextmanager
def timed_stage(
    report: PipelineReport,
    name: str,
    *,
    output: Any = None,
    metadata: Mapping[str, Any] | None = None,
) -> Iterator[None]:
    """Record one stage without imposing a backend or synchronization policy.

    The caller should pass ``output`` when it is available at entry time.  For
    stages that produce output inside the context, callers may update the
    resulting record themselves; this deliberately avoids wrapping or copying
    the algorithm's return value.
    """

    started = time.perf_counter()
    try:
        yield
    except Exception:
        report.success = False
        raise
    finally:
        value = output
        array = None if value is None else np.asarray(value)
        report.stages.append(
            StageRecord(
                name=str(name),
                seconds=float(time.perf_counter() - started),
                output_shape=None if array is None else tuple(int(v) for v in array.shape),
                output_dtype=None if array is None else str(array.dtype),
                finite_fraction=None if array is None else finite_fraction(array),
                metadata=dict(metadata or {}),
            )
        )


def update_stage_output(report: PipelineReport, stage_index: int, output: Any) -> None:
    """Attach output diagnostics to a previously recorded stage."""

    if stage_index < 0 or stage_index >= len(report.stages):
        raise IndexError("stage_index is out of range")
    array = np.asarray(output)
    record = report.stages[stage_index]
    record.output_shape = tuple(int(v) for v in array.shape)
    record.output_dtype = str(array.dtype)
    record.finite_fraction = finite_fraction(array)


def pressure_sizes(
    *,
    resolutions: Sequence[tuple[int, int]] = ((512, 512), (2048, 2048), (4096, 4096), (7072, 7072)),
    channels: int = 1,
    dtype: np.dtype = np.dtype(np.float32),
) -> list[dict[str, int]]:
    """Describe pressure cases without allocating large images.

    ``7072x7072`` is approximately 50 MP.  The benchmark runner can use this
    metadata to decide whether a case fits the configured host/device budget.
    """

    itemsize = int(np.dtype(dtype).itemsize)
    result = []
    for height, width in resolutions:
        if int(height) < 1 or int(width) < 1:
            raise ValueError("resolution dimensions must be positive")
        pixels = int(height) * int(width)
        result.append(
            {
                "height": int(height),
                "width": int(width),
                "pixels": pixels,
                "bytes": pixels * int(channels) * itemsize,
                "megapixels": int(round(pixels / 1_000_000.0)),
            }
        )
    return result


__all__ = [
    "PipelineReport",
    "StageRecord",
    "as_float32_image",
    "as_float32_matrix",
    "as_gray_float32",
    "validate_same_shape",
    "finite_fraction",
    "image_quality_metrics",
    "timed_stage",
    "update_stage_output",
    "pressure_sizes",
]
