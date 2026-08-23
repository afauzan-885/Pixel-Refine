"""Focus-stack orchestration with explicit AOT/host backend boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from ..pipeline_common import (
    PipelineReport,
    as_float32_image,
    finite_fraction,
    timed_stage,
    update_stage_output,
    validate_same_shape,
)
from .measures import focus_measure


MAX_POLICY_PIXELS = 55_000_000


def _normalise_scores(scores: np.ndarray, percentile_low: float, percentile_high: float) -> np.ndarray:
    low = np.percentile(scores, float(percentile_low), axis=(1, 2), keepdims=True)
    high = np.percentile(scores, float(percentile_high), axis=(1, 2), keepdims=True)
    span = np.maximum(high - low, 1e-6)
    return np.clip((scores - low) / span, 0.0, 1.0).astype(np.float32)


def _smooth_score_maps(scores: np.ndarray, radius: int) -> np.ndarray:
    if int(radius) <= 0:
        return scores
    from .measures import _box_mean

    return np.stack([_box_mean(score, int(radius)) for score in scores], axis=0).astype(np.float32)


@dataclass
class FocusStackResult:
    """Optional diagnostics returned by :func:`focus_stack`."""

    image: np.ndarray
    focus_index: np.ndarray
    confidence: np.ndarray
    scores: np.ndarray
    report: PipelineReport


def focus_stack(
    frames,
    *,
    method: str = "tenengrad",
    radius: int = 2,
    backend: str = "aot",
    max_working_bytes: int = 1_500_000_000,
    smooth_radius: int = 1,
    score_power: float = 1.0,
    percentile_low: float = 2.0,
    percentile_high: float = 98.0,
    return_result: bool = False,
):
    """Build an all-in-focus image from an aligned focus bracket.

    Derivative maps are dispatched through existing AOT Sobel/Laplacian graphs
    when ``backend="aot"``.  Label smoothing, confidence construction, and
    weighted fusion remain host orchestration because they involve a variable
    number of input frames and reductions.  ``backend="numpy"`` is an
    explicit reference mode; it is not an automatic fallback.
    """

    backend_name = str(backend).lower()
    if backend_name not in {"aot", "taichi", "numpy"}:
        raise ValueError("backend must be 'aot', 'taichi', or the explicit host backend 'numpy'")
    if isinstance(frames, np.ndarray):
        frames = [frames] if frames.ndim <= 2 else list(frames)
    arrays = validate_same_shape(frames, name="frames")
    if int(max_working_bytes) <= 0:
        raise ValueError("max_working_bytes must be positive")
    if int(arrays[0].shape[0] * arrays[0].shape[1]) > MAX_POLICY_PIXELS:
        raise ValueError(
            f"focus stack policy input exceeds the bounded {MAX_POLICY_PIXELS:,}-pixel limit"
        )
    if any(array.ndim == 3 and array.shape[2] not in (1, 3) for array in arrays):
        raise ValueError("focus frames must be grayscale, RGB, or single-channel images")
    if not all(np.isfinite(array).all() for array in arrays):
        raise ValueError("focus frames must contain only finite values")
    if not np.isfinite(float(score_power)) or float(score_power) <= 0.0:
        raise ValueError("score_power must be finite and positive")
    if not 0.0 <= float(percentile_low) < float(percentile_high) <= 100.0:
        raise ValueError("percentile_low/high must satisfy 0 <= low < high <= 100")

    # Scores, smoothed labels, and the fused input stack coexist.  This
    # estimate is intentionally conservative and is checked before the first
    # AOT/host measure dispatch, which keeps a 50 MP pressure run bounded.
    pixels = int(arrays[0].shape[0]) * int(arrays[0].shape[1])
    channels = 1 if arrays[0].ndim == 2 else int(arrays[0].shape[2])
    estimated_working_bytes = int(
        len(arrays) * pixels * (channels * 4 + 4 * 3) + pixels * (4 * 3)
    )
    if estimated_working_bytes > int(max_working_bytes):
        raise MemoryError(
            f"focus stack requires about {estimated_working_bytes} bytes of working memory; "
            f"limit is {int(max_working_bytes)}"
        )

    report = PipelineReport(pipeline="focus_stack", backend=backend_name)
    if arrays[0].shape[0] * arrays[0].shape[1] > 16_000_000:
        report.add_warning(
            "focus labels/fusion are host orchestration; 16+ MP runtime/pressure must be benchmarked on the target"
        )
    if backend_name == "numpy":
        report.add_warning("explicit host reference backend; no AOT graph was dispatched")
    elif backend_name == "taichi":
        report.add_warning("explicit CPU-JIT focus leaves; host label/fusion orchestration remains active")

    with timed_stage(report, "focus_measure"):
        score_maps = [
            focus_measure(frame, method=method, radius=radius, backend=backend_name)
            for frame in arrays
        ]
        scores = np.stack(score_maps, axis=0).astype(np.float32)
    update_stage_output(report, len(report.stages) - 1, scores)

    scores = _normalise_scores(scores, percentile_low, percentile_high)
    if float(score_power) != 1.0:
        scores = np.power(scores, float(score_power), dtype=np.float32)
    scores = _smooth_score_maps(scores, smooth_radius)

    # The soft map is used for fusion, while the hard map is useful for depth-
    # from-focus diagnostics.  A confidence floor prevents a flat/blurred
    # patch from becoming a black hole in the result.
    focus_index = np.argmax(scores, axis=0).astype(np.int32)
    max_score = np.max(scores, axis=0)
    total_score = np.sum(scores, axis=0)
    confidence = np.clip(max_score / np.maximum(total_score, 1e-6), 0.0, 1.0).astype(np.float32)
    weights = scores / np.maximum(total_score[None, ...], 1e-6)

    with timed_stage(report, "fuse"):
        if arrays[0].ndim == 2:
            result = np.sum(weights * np.stack(arrays, axis=0), axis=0)
        else:
            result = np.sum(weights[..., None] * np.stack(arrays, axis=0), axis=0)
        result = np.clip(result, 0.0, 1.0).astype(np.float32)
    update_stage_output(report, len(report.stages) - 1, result)
    report.metrics["finite_fraction"] = finite_fraction(result)
    report.metrics["mean_confidence"] = float(np.mean(confidence))
    report.metrics["focus_levels"] = float(len(arrays))
    report.metrics["estimated_working_bytes"] = float(estimated_working_bytes)

    if return_result:
        return FocusStackResult(
            image=np.ascontiguousarray(result),
            focus_index=focus_index,
            confidence=confidence,
            scores=scores,
            report=report,
        )
    return np.ascontiguousarray(result)


__all__ = ["FocusStackResult", "focus_measure", "focus_stack"]
