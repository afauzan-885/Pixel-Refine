"""Bounded SGM and PatchMatch-style regularisation for plane-sweep MVS.

This module deliberately composes the existing plane-sweep cost, winner and
bilateral-refinement leaves.  It does not introduce a second stereo cost
implementation.  The regularisers operate on the bounded cost volume in
host control flow so that the numerical contract is auditable and the memory
guard can run before an allocation is attempted.

``backend="numpy"`` is a deterministic reference path.  ``backend="taichi"``
uses the existing Taichi JIT plane-sweep/refinement kernels, while
``backend="aot"`` dispatches the target-qualified ``sfm_stereo`` cost/winner/
refine leaves and keeps SGM/PatchMatch orchestration on the host.  The latter
is therefore an explicit hybrid path, not a claim of a native SGM AOT graph.
"""

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from ..pipeline_common import PipelineReport, finite_fraction, timed_stage, update_stage_output
from . import plane_sweep as _plane_sweep

_ensure_taichi_runtime = _plane_sweep._ensure_taichi_runtime
_resolve_backend = _plane_sweep._resolve_backend
_sweep_single_depth_numpy = _plane_sweep._sweep_single_depth_numpy


DEFAULT_MAX_MVS_PIXELS = 4_000_000
_F32_BYTES = np.dtype(np.float32).itemsize


# SGM and PatchMatch have scan-order dependencies that are not expressible as
# an ordinary parallel ``ndrange``.  The explicit CPU-JIT kernels below use a
# serial scan inside Taichi, preserving the deterministic reference order
# while keeping the cost-volume memory on the native runtime.  AOT remains a
# separate capability because target-qualified graph support for these global
# recurrences is not available yet.
if _plane_sweep.TAICHI_AVAILABLE:
    _ti = _plane_sweep.ti

    @_ti.kernel
    def _sgm_path_kernel(
        cost: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        path: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        dy: _ti.i32,
        dx: _ti.i32,
        p1: _ti.f32,
        p2: _ti.f32,
    ):
        depths, height, width = cost.shape[0], cost.shape[1], cost.shape[2]
        _ti.loop_config(serialize=True)
        for yi in range(height):
            y = yi if dy >= 0 else height - 1 - yi
            for xi in range(width):
                x = xi if dx >= 0 else width - 1 - xi
                py = y - dy
                px = x - dx
                if py < 0 or py >= height or px < 0 or px >= width:
                    for depth_index in range(depths):
                        path[depth_index, y, x] = cost[depth_index, y, x]
                    continue
                minimum = path[0, py, px]
                for depth_index in range(1, depths):
                    minimum = _ti.min(minimum, path[depth_index, py, px])
                for depth_index in range(depths):
                    candidate = _ti.min(path[depth_index, py, px], minimum + p2)
                    if depth_index > 0:
                        candidate = _ti.min(candidate, path[depth_index - 1, py, px] + p1)
                    if depth_index + 1 < depths:
                        candidate = _ti.min(candidate, path[depth_index + 1, py, px] + p1)
                    path[depth_index, y, x] = (
                        cost[depth_index, y, x] + candidate - minimum
                    )

    @_ti.kernel
    def _patchmatch_iteration_kernel(
        cost: _ti.types.ndarray(dtype=_ti.f32, ndim=3),
        labels: _ti.types.ndarray(dtype=_ti.i32, ndim=2),
        iteration: _ti.i32,
        random_seed: _ti.i32,
    ):
        depths, height, width = cost.shape[0], cost.shape[1], cost.shape[2]
        _ti.loop_config(serialize=True)
        for yi in range(height):
            y = yi if (iteration & 1) == 0 else height - 1 - yi
            for xi in range(width):
                x = xi if (iteration & 1) == 0 else width - 1 - xi
                best = labels[y, x]
                best = _ti.min(_ti.max(best, 0), depths - 1)
                best_cost = cost[best, y, x]

                # Propagate the four already-visited neighbours.  The scan
                # is serial by design, so each candidate observes the same
                # updated labels as the NumPy implementation.
                if x > 0:
                    candidate = _ti.min(_ti.max(labels[y, x - 1], 0), depths - 1)
                    value = cost[candidate, y, x]
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                if x + 1 < width:
                    candidate = _ti.min(_ti.max(labels[y, x + 1], 0), depths - 1)
                    value = cost[candidate, y, x]
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                if y > 0:
                    candidate = _ti.min(_ti.max(labels[y - 1, x], 0), depths - 1)
                    value = cost[candidate, y, x]
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                if y + 1 < height:
                    candidate = _ti.min(_ti.max(labels[y + 1, x], 0), depths - 1)
                    value = cost[candidate, y, x]
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value

                # Deterministic integer hash in place of a host RNG.  This
                # bounds temporary memory at O(HW), even for 50 MP guards.
                for step in _ti.static(range(13)):
                    radius = depths // (1 << (step + 1))
                    radius = _ti.max(radius, 1)
                    state = (
                        random_seed
                        + iteration * 1103515245
                        + y * 12345
                        # 2654435761 modulo 2^32 represented as signed i32.
                        + x * -1640531535
                        + step * 7919
                    )
                    state = (state ^ (state >> 13)) * 1274126177
                    offset = state % (2 * radius + 1) - radius
                    candidate = _ti.min(_ti.max(best + offset, 0), depths - 1)
                    value = cost[candidate, y, x]
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                labels[y, x] = best


@dataclass(frozen=True)
class _MVSRegularizationConfig:
    """Validated controls shared by SGM and PatchMatch paths."""

    depth_min: float
    depth_max: float
    n_depths: int
    patch_radius: int
    depth_spacing: str
    max_volume_bytes: int
    max_pixels: int


def _depth_hypotheses(config: _MVSRegularizationConfig) -> np.ndarray:
    if config.depth_spacing == "log":
        values = np.logspace(
            np.log10(max(config.depth_min, 0.01)),
            np.log10(config.depth_max),
            config.n_depths,
            dtype=np.float32,
        )
    else:
        values = np.linspace(
            config.depth_min,
            config.depth_max,
            config.n_depths,
            dtype=np.float32,
        )
    if not np.isfinite(values).all() or np.any(values <= 0.0):
        raise ValueError("depth hypotheses must be finite and positive")
    return np.ascontiguousarray(values, dtype=np.float32)


def _validate_config(
    *,
    depth_min: float,
    depth_max: float,
    n_depths: int,
    patch_radius: int,
    depth_spacing: str,
    max_volume_bytes: int,
    max_pixels: int,
) -> _MVSRegularizationConfig:
    if not np.isfinite(depth_min) or not np.isfinite(depth_max):
        raise ValueError("depth range must be finite")
    if float(depth_min) <= 0.0 or float(depth_max) <= float(depth_min):
        raise ValueError("depth range must satisfy 0 < depth_min < depth_max")
    count = int(n_depths)
    if count < 2 or count > 4096:
        raise ValueError("n_depths must be in [2, 4096]")
    radius = int(patch_radius)
    if radius < 0 or radius > 32:
        raise ValueError("patch_radius must be in [0, 32]")
    spacing = str(depth_spacing).strip().lower()
    if spacing not in {"linear", "log"}:
        raise ValueError("depth_spacing must be 'linear' or 'log'")
    if int(max_volume_bytes) <= 0:
        raise ValueError("max_volume_bytes must be positive")
    if int(max_pixels) < 1:
        raise ValueError("max_pixels must be positive")
    return _MVSRegularizationConfig(
        depth_min=float(depth_min),
        depth_max=float(depth_max),
        n_depths=count,
        patch_radius=radius,
        depth_spacing=spacing,
        max_volume_bytes=int(max_volume_bytes),
        max_pixels=int(max_pixels),
    )


def _estimate_bytes(
    pixels: int,
    n_depths: int,
    *,
    n_views: int,
    method: str,
) -> int:
    """Conservative resident-byte estimate used before any cost allocation."""

    volume = int(pixels) * int(n_depths) * int(_F32_BYTES)
    # Base volume + one per-view working volume.  SGM keeps one aggregate and
    # one directional path volume; PatchMatch only needs labels/candidates.
    if method == "sgm":
        factor = 4
    else:
        factor = 2
    # Account for at least one target volume even when callers pass an empty
    # sequence (which is rejected later by the shared validator).
    return int(volume * (factor + max(int(n_views), 1)))


def _validate_volume_budget(
    shape: tuple[int, int],
    n_depths: int,
    *,
    n_views: int,
    config: _MVSRegularizationConfig,
    method: str,
) -> int:
    pixels = int(shape[0]) * int(shape[1])
    if pixels < 1 or pixels > config.max_pixels:
        raise ValueError(
            f"MVS input has {pixels:,} pixels; maximum is {config.max_pixels:,}"
        )
    estimate = _estimate_bytes(
        pixels,
        int(n_depths),
        n_views=int(n_views),
        method=method,
    )
    if estimate > config.max_volume_bytes:
        raise MemoryError(
            f"{method} MVS requires about {estimate} bytes, "
            f"limit is {config.max_volume_bytes}"
        )
    return estimate


def _build_cost_volume(
    reference: np.ndarray,
    targets: Sequence[np.ndarray],
    k_ref: np.ndarray,
    k_targets: Sequence[np.ndarray],
    rotations: Sequence[np.ndarray],
    translations: Sequence[np.ndarray],
    depths: np.ndarray,
    *,
    patch_radius: int,
    selected_backend: str,
    use_taichi: bool,
) -> np.ndarray:
    """Compose the existing per-view plane-sweep leaves into one volume."""

    h, w = reference.shape
    total = np.zeros((len(depths), h, w), dtype=np.float32)
    for target, k_target, rotation, translation in zip(
        targets, k_targets, rotations, translations
    ):
        if selected_backend == "aot":
            try:
                from ..aot_api.research import sfm_sweep_depths_aot

                volume = sfm_sweep_depths_aot(
                    reference,
                    target,
                    np.ascontiguousarray(k_ref, dtype=np.float32),
                    np.ascontiguousarray(k_target, dtype=np.float32),
                    np.ascontiguousarray(rotation, dtype=np.float32),
                    np.ascontiguousarray(translation, dtype=np.float32),
                    depths,
                    patch_radius=int(patch_radius),
                )
            except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                raise NotImplementedError(
                    "SGM/PatchMatch MVS AOT requires target-qualified sfm_stereo "
                    "cost artifacts; use backend='numpy' or 'taichi' explicitly"
                ) from exc
            volume = np.ascontiguousarray(volume, dtype=np.float32)
        elif use_taichi:
            volume = np.empty((len(depths), h, w), dtype=np.float32)
            _plane_sweep.sweep_all_depths_kernel(
                reference,
                target,
                np.ascontiguousarray(k_ref, dtype=np.float32),
                np.ascontiguousarray(k_target, dtype=np.float32),
                np.ascontiguousarray(rotation, dtype=np.float32),
                np.ascontiguousarray(translation, dtype=np.float32),
                depths,
                int(len(depths)),
                int(h),
                int(w),
                int(patch_radius),
                volume,
            )
        else:
            volume = np.empty((len(depths), h, w), dtype=np.float32)
            for index, depth in enumerate(depths):
                volume[index] = _sweep_single_depth_numpy(
                    reference,
                    target,
                    k_ref,
                    k_target,
                    rotation,
                    translation,
                    float(depth),
                    int(patch_radius),
                )
        if volume.shape != total.shape or not np.isfinite(volume).all():
            raise RuntimeError("plane-sweep cost leaf returned non-finite or invalid volume")
        total += volume
    total /= float(max(len(targets), 1))
    if not np.isfinite(total).all():
        raise RuntimeError("aggregated plane-sweep cost volume is non-finite")
    return np.ascontiguousarray(total, dtype=np.float32)


def _sgm_path(cost: np.ndarray, dy: int, dx: int, p1: float, p2: float) -> np.ndarray:
    """Accumulate one SGM path with bounded float32 working storage."""

    directions = (int(dy), int(dx))
    if directions == (0, 0):
        raise ValueError("SGM direction must be non-zero")
    depths, height, width = cost.shape
    path = np.empty_like(cost, dtype=np.float32)
    y_values = range(height) if dy >= 0 else range(height - 1, -1, -1)
    x_values = range(width) if dx >= 0 else range(width - 1, -1, -1)
    p1 = float(p1)
    p2 = float(p2)
    for y in y_values:
        for x in x_values:
            py = y - dy
            px = x - dx
            current = cost[:, y, x]
            if py < 0 or py >= height or px < 0 or px >= width:
                path[:, y, x] = current
                continue
            previous = path[:, py, px]
            minimum = float(np.min(previous))
            candidate = np.full(depths, np.float32(minimum + p2), dtype=np.float32)
            candidate = np.minimum(candidate, previous)
            if depths > 1:
                candidate[1:] = np.minimum(candidate[1:], previous[:-1] + np.float32(p1))
                candidate[:-1] = np.minimum(candidate[:-1], previous[1:] + np.float32(p1))
            # Subtracting the previous minimum is the standard SGM
            # normalisation and prevents path costs growing with image size.
            path[:, y, x] = current + candidate - np.float32(minimum)
    return path


def _regularize_sgm(
    cost: np.ndarray,
    *,
    directions: int,
    p1: float,
    p2: float,
) -> np.ndarray:
    if directions not in {4, 8}:
        raise ValueError("directions must be 4 or 8")
    if not np.isfinite(p1) or not np.isfinite(p2) or p1 < 0.0 or p2 < p1:
        raise ValueError("SGM penalties must satisfy 0 <= p1 <= p2 and be finite")
    cardinal = ((0, 1), (1, 0), (0, -1), (-1, 0))
    diagonal = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    chosen = cardinal if directions == 4 else cardinal + diagonal
    aggregate = np.zeros_like(cost, dtype=np.float32)
    for dy, dx in chosen:
        aggregate += _sgm_path(cost, dy, dx, float(p1), float(p2))
    aggregate /= np.float32(len(chosen))
    if not np.isfinite(aggregate).all():
        raise RuntimeError("SGM regularisation produced non-finite costs")
    return aggregate


def _regularize_sgm_taichi(
    cost: np.ndarray,
    *,
    directions: int,
    p1: float,
    p2: float,
) -> np.ndarray:
    """Run the scan-order SGM recurrence on the active Taichi JIT runtime."""

    if not _plane_sweep.TAICHI_AVAILABLE:
        raise RuntimeError("Taichi SGM requires AOT_MODE=0 and an installed Taichi runtime")
    _ensure_taichi_runtime()
    if directions not in {4, 8}:
        raise ValueError("directions must be 4 or 8")
    if not np.isfinite(p1) or not np.isfinite(p2) or p1 < 0.0 or p2 < p1:
        raise ValueError("SGM penalties must satisfy 0 <= p1 <= p2 and be finite")
    cardinal = ((0, 1), (1, 0), (0, -1), (-1, 0))
    diagonal = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    chosen = cardinal if directions == 4 else cardinal + diagonal
    aggregate = np.zeros_like(cost, dtype=np.float32)
    native_cost = np.ascontiguousarray(cost, dtype=np.float32)
    path = np.empty_like(native_cost, dtype=np.float32)
    for dy, dx in chosen:
        _sgm_path_kernel(
            native_cost,
            path,
            np.int32(dy),
            np.int32(dx),
            np.float32(p1),
            np.float32(p2),
        )
        aggregate += path
    try:
        _plane_sweep.ti.sync()
    except Exception:
        pass
    aggregate /= np.float32(len(chosen))
    if not np.isfinite(aggregate).all():
        raise RuntimeError("Taichi SGM regularisation produced non-finite costs")
    return np.ascontiguousarray(aggregate, dtype=np.float32)


def _regularize_sgm_aot(
    cost: np.ndarray,
    *,
    directions: int,
    p1: float,
    p2: float,
) -> np.ndarray:
    """Dispatch each SGM scan path through the target-qualified AOT leaf.

    SGM direction aggregation remains intentionally on the host because it is
    a small orchestration reduction; the recurrence itself executes in the
    same selected AOT backend.  Missing graph names propagate as an explicit
    ``NotImplementedError`` from the research API rather than falling back to
    a NumPy/JIT path.
    """

    if directions not in {4, 8}:
        raise ValueError("directions must be 4 or 8")
    if not np.isfinite(p1) or not np.isfinite(p2) or p1 < 0.0 or p2 < p1:
        raise ValueError("SGM penalties must satisfy 0 <= p1 <= p2 and be finite")
    cardinal = ((0, 1), (1, 0), (0, -1), (-1, 0))
    diagonal = ((1, 1), (1, -1), (-1, 1), (-1, -1))
    chosen = cardinal if directions == 4 else cardinal + diagonal
    from ..aot_api.research import sfm_sgm_path_aot

    aggregate = np.zeros_like(cost, dtype=np.float32)
    for dy, dx in chosen:
        path = sfm_sgm_path_aot(
            cost,
            dy=int(dy),
            dx=int(dx),
            p1=float(p1),
            p2=float(p2),
        )
        path = np.ascontiguousarray(path, dtype=np.float32)
        if path.shape != cost.shape or not np.isfinite(path).all():
            raise RuntimeError("AOT SGM path returned non-finite or invalid output")
        aggregate += path
    aggregate /= np.float32(len(chosen))
    return np.ascontiguousarray(aggregate, dtype=np.float32)


def _regularize_patchmatch(
    cost: np.ndarray,
    *,
    iterations: int,
    random_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic discrete PatchMatch propagation over depth hypotheses."""

    if int(iterations) < 1 or int(iterations) > 32:
        raise ValueError("iterations must be in [1, 32]")
    depths, height, width = cost.shape
    labels = np.argmin(cost, axis=0).astype(np.int32, copy=False)
    rng = np.random.default_rng(int(random_seed))
    for iteration in range(int(iterations)):
        y_values = range(height) if iteration % 2 == 0 else range(height - 1, -1, -1)
        x_values = range(width) if iteration % 2 == 0 else range(width - 1, -1, -1)
        for y in y_values:
            for x in x_values:
                best = int(labels[y, x])
                best_cost = float(cost[best, y, x])
                candidates = [best]
                if x > 0:
                    candidates.append(int(labels[y, x - 1]))
                if x + 1 < width:
                    candidates.append(int(labels[y, x + 1]))
                if y > 0:
                    candidates.append(int(labels[y - 1, x]))
                if y + 1 < height:
                    candidates.append(int(labels[y + 1, x]))
                for candidate in candidates:
                    candidate = max(0, min(depths - 1, int(candidate)))
                    value = float(cost[candidate, y, x])
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                radius = max(depths // 2, 1)
                while radius >= 1:
                    candidate = best + int(rng.integers(-radius, radius + 1))
                    candidate = max(0, min(depths - 1, candidate))
                    value = float(cost[candidate, y, x])
                    if value < best_cost or (value == best_cost and candidate < best):
                        best, best_cost = candidate, value
                    radius //= 2
                labels[y, x] = np.int32(best)
    if np.any(labels < 0) or np.any(labels >= depths):
        raise RuntimeError("PatchMatch produced an invalid depth label")
    selected_cost = np.take_along_axis(cost, labels[None, ...], axis=0)[0]
    if not np.isfinite(selected_cost).all():
        raise RuntimeError("PatchMatch produced non-finite costs")
    return labels, np.ascontiguousarray(selected_cost, dtype=np.float32)


def _regularize_patchmatch_taichi(
    cost: np.ndarray,
    *,
    iterations: int,
    random_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Run deterministic PatchMatch propagation with O(HW) native storage."""

    if not _plane_sweep.TAICHI_AVAILABLE:
        raise RuntimeError("Taichi PatchMatch requires AOT_MODE=0 and an installed Taichi runtime")
    _ensure_taichi_runtime()
    if int(iterations) < 1 or int(iterations) > 32:
        raise ValueError("iterations must be in [1, 32]")
    native_cost = np.ascontiguousarray(cost, dtype=np.float32)
    labels = np.argmin(native_cost, axis=0).astype(np.int32, copy=False)
    for iteration in range(int(iterations)):
        _patchmatch_iteration_kernel(
            native_cost,
            labels,
            np.int32(iteration),
            np.int32(int(random_seed)),
        )
    try:
        _plane_sweep.ti.sync()
    except Exception:
        pass
    if np.any(labels < 0) or np.any(labels >= native_cost.shape[0]):
        raise RuntimeError("Taichi PatchMatch produced an invalid depth label")
    selected_cost = np.take_along_axis(native_cost, labels[None, ...], axis=0)[0]
    if not np.isfinite(selected_cost).all():
        raise RuntimeError("Taichi PatchMatch produced non-finite costs")
    return np.ascontiguousarray(labels, dtype=np.int32), np.ascontiguousarray(selected_cost, dtype=np.float32)


def _regularize_patchmatch_aot(
    cost: np.ndarray,
    *,
    iterations: int,
    random_seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Dispatch deterministic PatchMatch iterations through the AOT leaf."""

    if int(iterations) < 1 or int(iterations) > 32:
        raise ValueError("iterations must be in [1, 32]")
    from ..aot_api.research import sfm_patchmatch_iteration_aot

    native_cost = np.ascontiguousarray(cost, dtype=np.float32)
    labels = np.argmin(native_cost, axis=0).astype(np.int32, copy=False)
    for iteration in range(int(iterations)):
        labels = np.ascontiguousarray(
            sfm_patchmatch_iteration_aot(
                native_cost,
                labels,
                iteration=int(iteration),
                random_seed=int(random_seed),
            ),
            dtype=np.int32,
        )
    if np.any(labels < 0) or np.any(labels >= native_cost.shape[0]):
        raise RuntimeError("AOT PatchMatch produced an invalid depth label")
    selected_cost = np.take_along_axis(native_cost, labels[None, ...], axis=0)[0]
    if not np.isfinite(selected_cost).all():
        raise RuntimeError("AOT PatchMatch produced non-finite costs")
    return labels, np.ascontiguousarray(selected_cost, dtype=np.float32)


def _winner_from_cost(cost: np.ndarray, depths: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    labels = np.argmin(cost, axis=0).astype(np.int32, copy=False)
    depth = np.take(depths, labels).astype(np.float32, copy=False)
    if cost.shape[0] > 1:
        two = np.partition(cost, 1, axis=0)
        confidence = (two[1] - two[0]).astype(np.float32, copy=False)
    else:
        confidence = np.zeros_like(depth, dtype=np.float32)
    return np.ascontiguousarray(depth), np.ascontiguousarray(confidence)


def _bilateral_numpy(depth: np.ndarray, guide: np.ndarray) -> np.ndarray:
    """Small bounded NumPy counterpart for the existing 5x5 JIT leaf."""

    height, width = depth.shape
    output = np.empty_like(depth, dtype=np.float32)
    sigma_s = 5.0
    sigma_r = 0.1
    for y in range(height):
        for x in range(width):
            total = 0.0
            weight_sum = 0.0
            center = float(guide[y, x])
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    yy = y + dy
                    xx = x + dx
                    if 0 <= yy < height and 0 <= xx < width:
                        spatial = np.exp(-(dy * dy + dx * dx) / (2.0 * sigma_s * sigma_s))
                        delta = float(guide[yy, xx]) - center
                        range_weight = np.exp(-(delta * delta) / (2.0 * sigma_r * sigma_r))
                        weight = float(spatial * range_weight)
                        total += weight * float(depth[yy, xx])
                        weight_sum += weight
            output[y, x] = np.float32(total / weight_sum if weight_sum > 1.0e-10 else depth[y, x])
    return output


def _refine_depth(depth: np.ndarray, guide: np.ndarray, *, selected_backend: str, use_taichi: bool) -> np.ndarray:
    if selected_backend == "aot":
        try:
            from ..aot_api.research import sfm_bilateral_refine_depth_aot

            value = sfm_bilateral_refine_depth_aot(depth, guide, sigma_s=5.0, sigma_r=0.1)
        except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
            raise NotImplementedError(
                "SGM/PatchMatch AOT refinement requires sfm_stereo bilateral artifact"
            ) from exc
        return np.ascontiguousarray(value, dtype=np.float32)
    if use_taichi:
        refined = np.empty_like(depth, dtype=np.float32)
        _plane_sweep.bilateral_refine_depth_kernel(
            np.ascontiguousarray(depth, dtype=np.float32),
            np.ascontiguousarray(guide, dtype=np.float32),
            int(depth.shape[0]),
            int(depth.shape[1]),
            5.0,
            0.1,
            refined,
        )
        # The caller selected a JIT backend; synchronize the same kernel before
        # exposing a host array to avoid stale output on asynchronous runtimes.
        try:
            import taichi as ti

            ti.sync()
        except Exception:
            pass
        return np.ascontiguousarray(refined, dtype=np.float32)
    return _bilateral_numpy(depth, guide)


def _run_regularized_mvs(
    method: str,
    ref_img: Any,
    target_images: Sequence[Any],
    K_ref: Any,
    K_targets: Sequence[Any],
    R_rels: Sequence[Any],
    t_rels: Sequence[Any],
    *,
    depth_min: float,
    depth_max: float,
    n_depths: int,
    patch_radius: int,
    depth_spacing: str,
    backend: str,
    max_volume_bytes: int,
    max_pixels: int,
    min_valid_fraction: float,
    refine: bool,
    directions: int,
    p1: float,
    p2: float,
    iterations: int,
    random_seed: int,
) -> Any:
    if method not in {"sgm", "patchmatch"}:
        raise ValueError("method must be 'sgm' or 'patchmatch'")
    if not np.isfinite(min_valid_fraction) or not 0.0 <= float(min_valid_fraction) <= 1.0:
        raise ValueError("min_valid_fraction must be in [0, 1]")
    config = _validate_config(
        depth_min=depth_min,
        depth_max=depth_max,
        n_depths=n_depths,
        patch_radius=patch_radius,
        depth_spacing=depth_spacing,
        max_volume_bytes=max_volume_bytes,
        max_pixels=max_pixels,
    )
    selected, use_taichi = _resolve_backend(backend)
    # The backend resolver intentionally initialises the same Taichi runtime as
    # plane_sweep.  Keep an explicit call here for clarity when a future
    # resolver returns a lazy JIT selection.
    if use_taichi:
        _ensure_taichi_runtime()
    from .reconstruction_pipeline import MVSResult, _validate_mvs_inputs

    reference, targets, k_ref, k_targets, rotations, translations = _validate_mvs_inputs(
        ref_img,
        target_images,
        K_ref,
        K_targets,
        R_rels,
        t_rels,
    )
    depths = _depth_hypotheses(config)
    estimate = _validate_volume_budget(
        reference.shape,
        len(depths),
        n_views=len(targets),
        config=config,
        method=method,
    )
    report = PipelineReport(
        f"mvs_{method}",
        backend=f"{method}-{selected}" if selected != "aot" else f"{method}-aot-hybrid",
    )
    report.metrics.update(
        {
            "height": float(reference.shape[0]),
            "width": float(reference.shape[1]),
            "n_views": float(len(targets)),
            "n_depths": float(len(depths)),
            "estimated_volume_bytes": float(estimate),
        }
    )
    with timed_stage(report, "plane_sweep_cost"):
        cost = _build_cost_volume(
            reference,
            targets,
            k_ref,
            k_targets,
            rotations,
            translations,
            depths,
            patch_radius=config.patch_radius,
            selected_backend=selected,
            use_taichi=use_taichi,
        )
    if method == "sgm":
        with timed_stage(report, "sgm_regularization"):
            regularized = (
                _regularize_sgm_taichi(
                    cost,
                    directions=int(directions),
                    p1=float(p1),
                    p2=float(p2),
                )
                if use_taichi
                else _regularize_sgm_aot(
                    cost,
                    directions=int(directions),
                    p1=float(p1),
                    p2=float(p2),
                )
                if selected == "aot"
                else _regularize_sgm(
                    cost,
                    directions=int(directions),
                    p1=float(p1),
                    p2=float(p2),
                )
            )
        depth, confidence = _winner_from_cost(regularized, depths)
    else:
        with timed_stage(report, "patchmatch_regularization"):
            labels, regularized = (
                _regularize_patchmatch_taichi(
                    cost,
                    iterations=int(iterations),
                    random_seed=int(random_seed),
                )
                if use_taichi
                else _regularize_patchmatch_aot(
                    cost,
                    iterations=int(iterations),
                    random_seed=int(random_seed),
                )
                if selected == "aot"
                else _regularize_patchmatch(
                    cost,
                    iterations=int(iterations),
                    random_seed=int(random_seed),
                )
            )
            depth = np.take(depths, labels).astype(np.float32, copy=False)
            # PatchMatch retains the best local label while confidence compares
            # it against the second-best plane-sweep hypothesis at the pixel.
            if cost.shape[0] > 1:
                second = np.partition(cost, 1, axis=0)[1]
                confidence = np.ascontiguousarray(second - regularized, dtype=np.float32)
            else:
                confidence = np.zeros_like(depth, dtype=np.float32)
    # Winner selection is kept as a host reduction because SGM/PatchMatch
    # regularisation has changed the cost volume; the existing AOT winner leaf
    # accepts a full volume but would undo the bounded host regularisation.
    if refine:
        with timed_stage(report, "bilateral_refine"):
            depth = _refine_depth(
                depth,
                reference,
                selected_backend=selected,
                use_taichi=use_taichi,
            )
    depth = np.ascontiguousarray(depth, dtype=np.float32)
    confidence = np.ascontiguousarray(confidence, dtype=np.float32)
    if depth.shape != reference.shape or confidence.shape != reference.shape:
        report.success = False
        raise RuntimeError(f"{method} MVS returned an unexpected depth/confidence shape")
    if not np.isfinite(depth).all() or not np.isfinite(confidence).all():
        report.success = False
        raise RuntimeError(f"{method} MVS returned non-finite output")
    valid_fraction = float(np.mean(depth > 0.0)) if depth.size else 0.0
    confidence_fraction = finite_fraction(confidence)
    if valid_fraction < float(min_valid_fraction):
        report.success = False
        report.add_warning(
            f"{method} depth valid fraction {valid_fraction:.4f} is below "
            f"the configured minimum {float(min_valid_fraction):.4f}"
        )
        raise RuntimeError(report.warnings[-1])
    if report.stages:
        update_stage_output(report, len(report.stages) - 1, depth)
    report.metrics.update(
        {
            "depth_valid_fraction": valid_fraction,
            "confidence_mean": float(np.mean(confidence)) if confidence.size else 0.0,
            "confidence_finite_fraction": confidence_fraction,
            "regularized_cost_mean": float(np.mean(regularized)),
            "regularized_cost_finite_fraction": finite_fraction(regularized),
        }
    )
    return MVSResult(depth=depth, confidence=confidence, report=report)


def run_sgm_mvs(
    ref_img: Any,
    target_images: Sequence[Any],
    K_ref: Any,
    K_targets: Sequence[Any],
    R_rels: Sequence[Any],
    t_rels: Sequence[Any],
    *,
    depth_min: float = 0.1,
    depth_max: float = 100.0,
    n_depths: int = 64,
    patch_radius: int = 3,
    depth_spacing: str = "linear",
    backend: str = "auto",
    max_volume_bytes: int = 512 * 1024 * 1024,
    max_pixels: int = DEFAULT_MAX_MVS_PIXELS,
    directions: int = 4,
    p1: float = 0.02,
    p2: float = 0.20,
    min_valid_fraction: float = 0.0,
    refine: bool = True,
) -> Any:
    """Run bounded semi-global matching on an existing plane-sweep volume."""

    return _run_regularized_mvs(
        "sgm",
        ref_img,
        target_images,
        K_ref,
        K_targets,
        R_rels,
        t_rels,
        depth_min=depth_min,
        depth_max=depth_max,
        n_depths=n_depths,
        patch_radius=patch_radius,
        depth_spacing=depth_spacing,
        backend=backend,
        max_volume_bytes=max_volume_bytes,
        max_pixels=max_pixels,
        min_valid_fraction=min_valid_fraction,
        refine=refine,
        directions=directions,
        p1=p1,
        p2=p2,
        iterations=1,
        random_seed=0,
    )


def run_patchmatch_mvs(
    ref_img: Any,
    target_images: Sequence[Any],
    K_ref: Any,
    K_targets: Sequence[Any],
    R_rels: Sequence[Any],
    t_rels: Sequence[Any],
    *,
    depth_min: float = 0.1,
    depth_max: float = 100.0,
    n_depths: int = 64,
    patch_radius: int = 3,
    depth_spacing: str = "linear",
    backend: str = "auto",
    max_volume_bytes: int = 512 * 1024 * 1024,
    max_pixels: int = DEFAULT_MAX_MVS_PIXELS,
    iterations: int = 2,
    random_seed: int = 0,
    min_valid_fraction: float = 0.0,
    refine: bool = True,
) -> Any:
    """Run deterministic discrete PatchMatch propagation on plane-sweep costs."""

    return _run_regularized_mvs(
        "patchmatch",
        ref_img,
        target_images,
        K_ref,
        K_targets,
        R_rels,
        t_rels,
        depth_min=depth_min,
        depth_max=depth_max,
        n_depths=n_depths,
        patch_radius=patch_radius,
        depth_spacing=depth_spacing,
        backend=backend,
        max_volume_bytes=max_volume_bytes,
        max_pixels=max_pixels,
        min_valid_fraction=min_valid_fraction,
        refine=refine,
        directions=4,
        p1=0.0,
        p2=0.0,
        iterations=iterations,
        random_seed=random_seed,
    )


__all__ = [
    "DEFAULT_MAX_MVS_PIXELS",
    "run_sgm_mvs",
    "run_patchmatch_mvs",
]
