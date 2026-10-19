"""Streaming local patch search for FusionNet Deep Analysis.

Patch distance selects nearby aligned candidates. It never contributes to the
fusion weight, which is supplied by WeightNet. Full-resolution RAW offsets are
even on both axes so source gathers remain on the same CFA phase.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
import threading
from typing import Any

import cv2
import numpy as np


@dataclass(frozen=True)
class CandidateOffset:
    name: str
    dx_full: int
    dy_full: int
    dx_proxy: int
    dy_proxy: int
    dx_align: int
    dy_align: int


@dataclass(frozen=True)
class CandidateSelection:
    """Top-K search result; indices are ``(K,H,W)`` and -1 means no match."""

    indices: np.ndarray
    valid: np.ndarray
    search_candidate_count: int


def cohere_candidate_selection(
    selection: CandidateSelection,
    offsets: tuple[CandidateOffset, ...] | list[CandidateOffset],
    *,
    cell_size: int = 10,
    patch_size: int = 5,
) -> CandidateSelection:
    """Make local candidate choices spatially coherent over patch cells.

    The search still ranks offsets independently at every pixel. Before those
    rank maps are used to assemble WeightNet inputs or CFA remap fields, sample
    one top-K decision at each patch-cell center and hold that decision across
    the cell. This prevents noise in flat areas from switching source offsets
    at pixel frequency while keeping the existing top-K search and ABI intact.
    """

    indices = np.asarray(selection.indices, dtype=np.int32)
    if indices.ndim != 3:
        raise ValueError("candidate selection indices must have shape (K,H,W)")
    if np.asarray(selection.valid).shape != indices.shape:
        raise ValueError("candidate selection validity must match index shape")
    if not offsets:
        raise ValueError("candidate offsets must not be empty")
    cell_size = int(cell_size)
    patch_size = int(patch_size)
    if cell_size <= 0 or patch_size <= 0:
        raise ValueError("cell_size and patch_size must be positive")

    rank_count, height, width = indices.shape
    if rank_count == 0 or height == 0 or width == 0:
        return CandidateSelection(
            indices=np.ascontiguousarray(indices.copy()),
            valid=np.zeros(indices.shape, dtype=bool),
            search_candidate_count=int(selection.search_candidate_count),
        )

    radius = patch_size // 2
    center_y = np.minimum(
        np.arange(0, height, cell_size, dtype=np.int32) + cell_size // 2,
        height - 1,
    )
    center_x = np.minimum(
        np.arange(0, width, cell_size, dtype=np.int32) + cell_size // 2,
        width - 1,
    )
    result_indices = np.empty_like(indices, dtype=np.int32)
    max_offset_x = max(abs(int(item.dx_proxy)) for item in offsets)
    max_offset_y = max(abs(int(item.dy_proxy)) for item in offsets)
    border_x = min(width, radius + max_offset_x)
    border_y = min(height, radius + max_offset_y)

    for rank in range(rank_count):
        sampled = indices[rank][center_y[:, None], center_x[None, :]]
        expanded = np.repeat(np.repeat(sampled, cell_size, axis=0), cell_size, axis=1)
        result_indices[rank] = expanded[:height, :width]

    # A conservative border makes every retained offset patch valid without
    # allocating full-resolution coordinate/validity temporaries per rank.
    # The center temporal candidate remains active at these edges.
    if border_y:
        result_indices[:, :border_y, :] = -1
        result_indices[:, height - border_y :, :] = -1
    if border_x:
        result_indices[:, :, :border_x] = -1
        result_indices[:, :, width - border_x :] = -1
    result_valid = result_indices >= 0

    return CandidateSelection(
        indices=result_indices,
        valid=result_valid,
        search_candidate_count=int(selection.search_candidate_count),
    )


def _nearest_even(value: float) -> int:
    result = int(round(float(value) / 2.0)) * 2
    if result == 0 and value:
        result = 2 if value > 0 else -2
    return result


def _positive_shape(shape: tuple[int, int], name: str) -> tuple[int, int]:
    height, width = int(shape[0]), int(shape[1])
    if height <= 0 or width <= 0:
        raise ValueError(f"{name} must be positive, got {(height, width)}")
    return height, width


def candidate_offsets(
    full_shape: tuple[int, int],
    proxy_shape: tuple[int, int],
    *,
    align_shape: tuple[int, int] | None = None,
    patch_width: int = 5,
    preserve_cfa_phase: bool = True,
) -> tuple[CandidateOffset, ...]:
    """Compatibility geometry for center and four cardinal offsets."""

    full_h, full_w = _positive_shape(full_shape, "full_shape")
    proxy_h, proxy_w = _positive_shape(proxy_shape, "proxy_shape")
    align_h, align_w = _positive_shape(
        align_shape or proxy_shape, "align_shape"
    )
    patch_width = int(patch_width)
    if patch_width <= 0:
        raise ValueError("patch_width must be positive")
    proxy_scale_x, proxy_scale_y = proxy_w / full_w, proxy_h / full_h
    align_scale_x, align_scale_y = align_w / full_w, align_h / full_h
    requested = (
        ("center", 0, 0),
        ("left", -patch_width, 0),
        ("right", patch_width, 0),
        ("up", 0, -patch_width),
        ("down", 0, patch_width),
    )
    resolved = []
    for name, dx_proxy, dy_proxy in requested:
        dx_full = (
            _nearest_even(dx_proxy / proxy_scale_x)
            if preserve_cfa_phase and dx_proxy
            else int(round(dx_proxy / proxy_scale_x))
        )
        dy_full = (
            _nearest_even(dy_proxy / proxy_scale_y)
            if preserve_cfa_phase and dy_proxy
            else int(round(dy_proxy / proxy_scale_y))
        )
        resolved.append(
            CandidateOffset(
                name=name,
                dx_full=dx_full,
                dy_full=dy_full,
                dx_proxy=int(round(dx_full * proxy_scale_x)),
                dy_proxy=int(round(dy_full * proxy_scale_y)),
                dx_align=int(round(dx_full * align_scale_x)),
                dy_align=int(round(dy_full * align_scale_y)),
            )
        )
    if preserve_cfa_phase and any(
        item.dx_full % 2 or item.dy_full % 2 for item in resolved
    ):
        raise ValueError("CFA candidate offsets must be even in full-resolution pixels")
    return tuple(resolved)


def search_candidate_offsets(
    full_shape: tuple[int, int],
    proxy_shape: tuple[int, int],
    *,
    align_shape: tuple[int, int] | None = None,
    search_radius: int = 5,
    patch_stride: int = 2,
    preserve_cfa_phase: bool = False,
) -> tuple[CandidateOffset, ...]:
    """Create a unique 2D offset pool within the WeightNet-grid search radius.

    The search grid is centered on zero and spaced by ``patch_stride``. Proxy
    offsets map to full-resolution integer offsets; RAW offsets are quantized
    to even sensor pixels, then mapped back to the proxy to keep geometry
    consistent with the CFA carrier gather.
    """

    full_h, full_w = _positive_shape(full_shape, "full_shape")
    proxy_h, proxy_w = _positive_shape(proxy_shape, "proxy_shape")
    align_h, align_w = _positive_shape(
        align_shape or proxy_shape, "align_shape"
    )
    search_radius = int(search_radius)
    patch_stride = int(patch_stride)
    if search_radius < 1:
        raise ValueError("search_radius must be at least 1")
    if patch_stride < 1:
        raise ValueError("patch_stride must be at least 1")

    max_step = (search_radius // patch_stride) * patch_stride
    if max_step == 0:
        steps = (-search_radius, search_radius)
    else:
        steps = tuple(range(-max_step, max_step + 1, patch_stride))
    proxy_scale_x, proxy_scale_y = proxy_w / full_w, proxy_h / full_h
    align_scale_x, align_scale_y = align_w / full_w, align_h / full_h
    unique: dict[tuple[int, int], CandidateOffset] = {}
    for requested_y in steps:
        for requested_x in steps:
            if requested_x == 0 and requested_y == 0:
                continue
            dx_full = (
                _nearest_even(requested_x / proxy_scale_x)
                if preserve_cfa_phase
                else int(round(requested_x / proxy_scale_x))
            )
            dy_full = (
                _nearest_even(requested_y / proxy_scale_y)
                if preserve_cfa_phase
                else int(round(requested_y / proxy_scale_y))
            )
            dx_proxy = int(round(dx_full * proxy_scale_x))
            dy_proxy = int(round(dy_full * proxy_scale_y))
            if dx_proxy == 0 and dy_proxy == 0:
                continue
            if preserve_cfa_phase and (dx_full % 2 or dy_full % 2):
                continue
            key = (dx_proxy, dy_proxy)
            candidate = CandidateOffset(
                name=f"offset_{dx_proxy}_{dy_proxy}",
                dx_full=dx_full,
                dy_full=dy_full,
                dx_proxy=dx_proxy,
                dy_proxy=dy_proxy,
                dx_align=int(round(dx_full * align_scale_x)),
                dy_align=int(round(dy_full * align_scale_y)),
            )
            current = unique.get(key)
            if current is None or (
                abs(dx_full * proxy_scale_x - requested_x)
                + abs(dy_full * proxy_scale_y - requested_y)
                < abs(current.dx_proxy - requested_x)
                + abs(current.dy_proxy - requested_y)
            ):
                unique[key] = candidate
    return tuple(unique[key] for key in sorted(unique, key=lambda point: (point[1], point[0])))


def validity_mask(shape: tuple[int, int], dx: int, dy: int) -> np.ndarray:
    """Mask destination pixels whose shifted source coordinate is in bounds."""

    height, width = _positive_shape(shape, "shape")
    dx, dy = int(dx), int(dy)
    valid = np.zeros((height, width), dtype=bool)
    y0, y1 = max(0, -dy), min(height, height - dy)
    x0, x1 = max(0, -dx), min(width, width - dx)
    if y0 < y1 and x0 < x1:
        valid[y0:y1, x0:x1] = True
    return valid


def shifted_candidate_view(
    image: np.ndarray,
    dx: int,
    dy: int,
    *,
    channel_first: bool = False,
) -> tuple[np.ndarray, np.ndarray]:
    """Copy one shifted view with ``out[y,x] = in[y+dy,x+dx]``."""

    source = np.asarray(image)
    if source.ndim not in (2, 3):
        raise ValueError(f"candidate image must be 2D or 3D, got {source.shape}")
    height, width = (
        (int(source.shape[-2]), int(source.shape[-1]))
        if channel_first and source.ndim == 3
        else (int(source.shape[0]), int(source.shape[1]))
    )
    dx, dy = int(dx), int(dy)
    mask = validity_mask((height, width), dx, dy)
    output = np.zeros_like(source)
    y0, y1 = max(0, -dy), min(height, height - dy)
    x0, x1 = max(0, -dx), min(width, width - dx)
    if y0 < y1 and x0 < x1:
        if channel_first and source.ndim == 3:
            output[:, y0:y1, x0:x1] = source[
                :, y0 + dy : y1 + dy, x0 + dx : x1 + dx
            ]
        else:
            output[y0:y1, x0:x1, ...] = source[
                y0 + dy : y1 + dy, x0 + dx : x1 + dx, ...
            ]
    return output, mask


def _luma_chw(image: np.ndarray) -> np.ndarray:
    values = np.asarray(image, dtype=np.float32)
    if values.ndim == 2:
        return values
    if values.ndim != 3:
        raise ValueError(f"patch search expects HW/HWC/CHW arrays, got {values.shape}")
    if values.shape[0] in (1, 3) and values.shape[-1] not in (1, 3):
        chw = values
    elif values.shape[-1] in (1, 3):
        chw = np.moveaxis(values, -1, 0)
    else:
        raise ValueError(f"patch search expects 1 or 3 channels, got {values.shape}")
    if chw.shape[0] == 1:
        return np.ascontiguousarray(chw[0])
    return np.ascontiguousarray(
        chw[0] * np.float32(0.299)
        + chw[1] * np.float32(0.587)
        + chw[2] * np.float32(0.114),
        dtype=np.float32,
    )


def patch_distance_map(
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    patch_size: int = 5,
    valid_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return local 5x5 luminance MSE for ranking and full-footprint validity."""

    reference_luma, candidate_luma = _luma_chw(reference), _luma_chw(candidate)
    if reference_luma.shape != candidate_luma.shape:
        raise ValueError("reference and candidate patch-search grids must match")
    patch_size = int(patch_size)
    if patch_size <= 0 or patch_size % 2 == 0:
        raise ValueError("patch_size must be a positive odd integer")
    if not np.isfinite(reference_luma).all() or not np.isfinite(candidate_luma).all():
        raise ValueError("patch-search inputs must be finite")
    height, width = reference_luma.shape
    if valid_mask is None:
        valid = np.ones((height, width), dtype=np.uint8)
    else:
        mask = np.asarray(valid_mask)
        if mask.shape != (height, width):
            raise ValueError("valid_mask must match the patch-search grid")
        valid = np.ascontiguousarray(mask != 0, dtype=np.uint8)

    radius = patch_size // 2
    target_valid = np.zeros((height, width), dtype=np.uint8)
    if height > 2 * radius and width > 2 * radius:
        target_valid[radius : height - radius, radius : width - radius] = 1
    footprint = np.ones((patch_size, patch_size), dtype=np.uint8)
    source_footprint_valid = cv2.erode(
        valid,
        footprint,
        borderType=cv2.BORDER_CONSTANT,
        borderValue=0,
    ).astype(bool)
    patch_valid = source_footprint_valid & target_valid.astype(bool)
    squared_difference = np.square(reference_luma - candidate_luma, dtype=np.float32)
    distance = cv2.boxFilter(
        squared_difference,
        ddepth=cv2.CV_32F,
        ksize=(patch_size, patch_size),
        normalize=True,
        borderType=cv2.BORDER_REFLECT_101,
    )
    distance[~patch_valid] = np.inf
    return np.ascontiguousarray(distance, dtype=np.float32), patch_valid


def select_topk_candidates(
    reference_chw: np.ndarray,
    candidate_chw: np.ndarray,
    offsets: tuple[CandidateOffset, ...] | list[CandidateOffset],
    *,
    max_neighbors: int = 4,
    patch_size: int = 5,
    stop_event=None,
) -> CandidateSelection:
    """Rank candidate offsets independently at each target pixel, streaming pool."""

    reference = np.asarray(reference_chw, dtype=np.float32)
    candidate = np.asarray(candidate_chw, dtype=np.float32)
    if reference.ndim != 3 or candidate.shape != reference.shape:
        raise ValueError("patch selection inputs must be matching CHW arrays")
    max_neighbors = int(max_neighbors)
    if max_neighbors <= 0:
        raise ValueError("max_neighbors must be positive")
    effective_k = min(max_neighbors, len(offsets))
    height, width = reference.shape[-2:]
    if effective_k == 0:
        return CandidateSelection(
            indices=np.empty((0, height, width), dtype=np.int32),
            valid=np.empty((0, height, width), dtype=bool),
            search_candidate_count=0,
        )

    best_distance = np.full((effective_k, height, width), np.inf, dtype=np.float32)
    best_index = np.full((effective_k, height, width), -1, dtype=np.int32)
    best_valid = np.zeros((effective_k, height, width), dtype=bool)
    visited = 0
    for candidate_index, offset in enumerate(offsets):
        if _is_stopped(stop_event):
            break
        shifted, geometric_valid = shifted_candidate_view(
            candidate, offset.dx_proxy, offset.dy_proxy, channel_first=True
        )
        distance, valid = patch_distance_map(
            reference,
            shifted,
            patch_size=patch_size,
            valid_mask=geometric_valid,
        )
        visited += 1
        carry_distance = distance
        carry_index = np.full((height, width), candidate_index, dtype=np.int32)
        carry_valid = valid
        for rank in range(effective_k):
            improve = carry_valid & (carry_distance < best_distance[rank])
            if not np.any(improve):
                continue
            displaced_distance = np.where(improve, best_distance[rank], np.inf)
            displaced_index = np.where(improve, best_index[rank], -1)
            displaced_valid = np.where(improve, best_valid[rank], False)
            best_distance[rank] = np.where(
                improve, carry_distance, best_distance[rank]
            )
            best_index[rank] = np.where(improve, carry_index, best_index[rank])
            best_valid[rank] = np.where(improve, carry_valid, best_valid[rank])
            carry_distance = np.where(improve, displaced_distance, carry_distance)
            carry_index = np.where(improve, displaced_index, carry_index)
            carry_valid = np.where(improve, displaced_valid, carry_valid)
    indices = best_index
    valid = best_valid & (indices >= 0)
    indices[~valid] = -1
    return CandidateSelection(indices=indices, valid=valid, search_candidate_count=visited)


def gather_rank_candidate(
    source_chw: np.ndarray,
    offsets: tuple[CandidateOffset, ...] | list[CandidateOffset],
    rank_indices: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Gather one per-location candidate rank from its source proxy."""

    source = np.asarray(source_chw, dtype=np.float32)
    indices = np.asarray(rank_indices, dtype=np.int32)
    if source.ndim != 3 or indices.shape != source.shape[-2:]:
        raise ValueError("rank indices must match the source CHW grid")
    height, width = indices.shape
    valid = indices >= 0
    output = np.zeros_like(source)
    yy, xx = np.indices((height, width), dtype=np.int32)
    for candidate_index, offset in enumerate(offsets):
        selected = indices == candidate_index
        if not np.any(selected):
            continue
        source_y = yy[selected] + int(offset.dy_proxy)
        source_x = xx[selected] + int(offset.dx_proxy)
        if (
            np.any(source_y < 0)
            or np.any(source_y >= height)
            or np.any(source_x < 0)
            or np.any(source_x >= width)
        ):
            raise ValueError("selected candidate offset points outside source proxy")
        output[:, selected] = source[:, source_y, source_x]
    return output, valid


def candidate_flow_from_indices(
    rank_indices: np.ndarray,
    offsets: tuple[CandidateOffset, ...] | list[CandidateOffset],
    *,
    full_shape: tuple[int, int],
    flow_shape: tuple[int, int],
    base_transform: Any = None,
) -> np.ndarray:
    """Compose one dynamic rank offset with a RAW alignment transform.

    For a dense flow, the base field is sampled at the shifted target location,
    then the selected offset is added. For a homography, the inverse mapping is
    evaluated at target+offset and represented as a dense flow in flow-grid
    pixels. The output matches ``remap_accumulate_cfa_weighted_taichi``'s flow
    convention.
    """

    from taichi_vision.taichi_algorithm.denoising.resident_weightnet import ResidentRank
    if isinstance(rank_indices, ResidentRank):
        return rank_indices.flow(full_shape=full_shape, flow_shape=flow_shape, base_transform=base_transform)
    full_h, full_w = _positive_shape(full_shape, "full_shape")
    flow_h, flow_w = _positive_shape(flow_shape, "flow_shape")
    indices = np.asarray(rank_indices, dtype=np.int32)
    if indices.ndim != 2:
        raise ValueError("rank_indices must be a 2D map")
    if base_transform is not None:
        matrix_or_flow = np.asarray(base_transform, dtype=np.float32)
        if matrix_or_flow.ndim == 3:
            if matrix_or_flow.shape[-1] != 2:
                raise ValueError("dense alignment transform must have shape (H,W,2)")
            flow_h, flow_w = _positive_shape(matrix_or_flow.shape[:2], "base flow shape")
        elif matrix_or_flow.shape != (3, 3):
            raise ValueError("alignment transform must be a homography or dense flow")
    else:
        matrix_or_flow = None

    selected = cv2.resize(
        indices,
        (flow_w, flow_h),
        interpolation=cv2.INTER_NEAREST,
    ).astype(np.int32, copy=False)
    dx_full = np.zeros((flow_h, flow_w), dtype=np.float32)
    dy_full = np.zeros((flow_h, flow_w), dtype=np.float32)
    for candidate_index, offset in enumerate(offsets):
        mask = selected == candidate_index
        dx_full[mask] = np.float32(offset.dx_full)
        dy_full[mask] = np.float32(offset.dy_full)

    # remap_accumulate_cfa_weighted_taichi scales these values by full/flow.
    dx_flow = dx_full * np.float32(flow_w / full_w)
    dy_flow = dy_full * np.float32(flow_h / full_h)
    if matrix_or_flow is None:
        return np.ascontiguousarray(np.stack((dx_flow, dy_flow), axis=-1))

    if matrix_or_flow.ndim == 3:
        base = matrix_or_flow
        if base.shape[:2] != (flow_h, flow_w):
            raise ValueError("dense transform shape differs from its flow grid")
        yy, xx = np.indices((flow_h, flow_w), dtype=np.float32)
        map_x, map_y = xx + dx_flow, yy + dy_flow
        shifted_x = cv2.remap(
            base[..., 0], map_x, map_y, cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=0,
        )
        shifted_y = cv2.remap(
            base[..., 1], map_x, map_y, cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT, borderValue=0,
        )
        return np.ascontiguousarray(
            np.stack((shifted_x + dx_flow, shifted_y + dy_flow), axis=-1),
            dtype=np.float32,
        )

    try:
        inverse = np.linalg.inv(matrix_or_flow).astype(np.float32, copy=False)
    except np.linalg.LinAlgError as exc:
        raise ValueError("alignment homography is singular") from exc
    yy, xx = np.indices((flow_h, flow_w), dtype=np.float32)
    target_x = xx * np.float32(full_w / flow_w) + dx_full
    target_y = yy * np.float32(full_h / flow_h) + dy_full
    denominator = (
        inverse[2, 0] * target_x
        + inverse[2, 1] * target_y
        + inverse[2, 2]
    )
    if np.any(np.abs(denominator) < 1.0e-8):
        raise ValueError("homography maps candidate target through infinity")
    source_x = (
        inverse[0, 0] * target_x
        + inverse[0, 1] * target_y
        + inverse[0, 2]
    ) / denominator
    source_y = (
        inverse[1, 0] * target_x
        + inverse[1, 1] * target_y
        + inverse[1, 2]
    ) / denominator
    base_target_x = xx * np.float32(full_w / flow_w)
    base_target_y = yy * np.float32(full_h / flow_h)
    flow_x = (source_x - base_target_x) * np.float32(flow_w / full_w)
    flow_y = (source_y - base_target_y) * np.float32(flow_h / full_h)
    return np.ascontiguousarray(np.stack((flow_x, flow_y), axis=-1), dtype=np.float32)


def iter_candidate_offsets(offsets, stop_event=None):
    """Yield candidate offsets in order and stop before the next on cancellation."""

    for offset in offsets:
        if _is_stopped(stop_event):
            return
        yield offset


def _is_stopped(stop_event) -> bool:
    if stop_event is None:
        return False
    if callable(stop_event):
        return bool(stop_event())
    return bool(stop_event.is_set()) if hasattr(stop_event, "is_set") else False


def normalize_weighted_accumulator(
    numerator: np.ndarray,
    denominator: np.ndarray,
    reference: np.ndarray,
) -> np.ndarray:
    """Normalize weighted sums, using reference wherever weight is zero."""

    values = np.asarray(numerator, dtype=np.float32)
    weights = np.asarray(denominator, dtype=np.float32)
    fallback = np.asarray(reference, dtype=np.float32)
    if values.shape != fallback.shape:
        raise ValueError("numerator and reference must have matching shapes")
    if weights.shape == values.shape:
        expanded = weights
    elif values.ndim == 3 and weights.shape == values.shape[:2]:
        expanded = weights[..., None]
    elif values.ndim == 3 and weights.shape == (*values.shape[:2], 1):
        expanded = weights
    else:
        raise ValueError("denominator must align with numerator")
    output = np.array(fallback, dtype=np.float32, copy=True)
    np.divide(values, expanded, out=output, where=expanded > 0.0)
    return output


class CandidateTelemetry:
    """Small per-support timer kept separate from backend device telemetry."""

    def __init__(self) -> None:
        self.candidate_count = 0
        self.search_candidate_count = 0
        self._stage_seconds: dict[str, float] = {}
        self._lock = threading.Lock()

    def record(self, stage: str, started_at: float) -> None:
        elapsed = max(0.0, time.perf_counter() - float(started_at))
        with self._lock:
            self._stage_seconds[stage] = self._stage_seconds.get(stage, 0.0) + elapsed

    def candidate(self) -> None:
        with self._lock:
            self.candidate_count += 1

    def searched(self, count: int) -> None:
        with self._lock:
            self.search_candidate_count += int(count)

    def summary(self) -> dict[str, float | int]:
        with self._lock:
            return {
                "candidate_count": int(self.candidate_count),
                "search_candidate_count": int(self.search_candidate_count),
                **{f"{stage}_ms": 1000.0 * seconds for stage, seconds in self._stage_seconds.items()},
            }


__all__ = [
    "CandidateOffset",
    "CandidateSelection",
    "CandidateTelemetry",
    "cohere_candidate_selection",
    "candidate_flow_from_indices",
    "candidate_offsets",
    "gather_rank_candidate",
    "iter_candidate_offsets",
    "normalize_weighted_accumulator",
    "patch_distance_map",
    "search_candidate_offsets",
    "select_topk_candidates",
    "shifted_candidate_view",
    "validity_mask",
]
