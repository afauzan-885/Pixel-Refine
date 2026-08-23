"""Adaptive local homography (APAP-style) refinement.

The implementation keeps the APAP contract explicit while remaining usable as
a deterministic reference path: local homographies are fitted at a sparse
source grid using Gaussian correspondence weights, then smoothly blended for
query points.  A global homography is retained as a fail-closed fallback for
cells with insufficient support or degenerate geometry.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .quality import TransformEstimationError, estimate_homography, project_points, validate_correspondences


def _weighted_homography(source: np.ndarray, target: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """Weighted normalized-DLT solve used for one APAP grid node."""

    src, dst = validate_correspondences(source, target, min_points=4)
    w = np.asarray(weights, dtype=np.float64).reshape(-1)
    if len(w) != len(src):
        raise ValueError("weights length does not match correspondences")
    keep = np.isfinite(w) & (w > 1.0e-10)
    if int(keep.sum()) < 4:
        raise TransformEstimationError("APAP node has fewer than four weighted controls")
    return estimate_homography(src[keep], dst[keep], weights=w[keep])


@dataclass
class APAPWarp:
    """Sparse local-homography field with global fallback."""

    source_points: np.ndarray
    target_points: np.ndarray
    centers: np.ndarray
    homographies: np.ndarray
    global_homography: np.ndarray
    sigma: float
    support_counts: np.ndarray

    def map_points(self, points: np.ndarray) -> np.ndarray:
        query = np.ascontiguousarray(points, dtype=np.float64)
        if query.ndim != 2 or query.shape[1:] != (2,):
            raise ValueError(f"points must have shape (N, 2), got {query.shape}")
        if len(query) == 0:
            return np.empty((0, 2), dtype=np.float64)
        delta = query[:, None, :] - self.centers[None, :, :]
        radius_sq = np.sum(delta * delta, axis=2)
        weights = np.exp(-radius_sq / (2.0 * max(float(self.sigma), 1.0e-8) ** 2))
        weights *= (self.support_counts[None, :] > 0)
        sums = np.sum(weights, axis=1)
        outputs = np.empty((len(query), 2), dtype=np.float64)
        for i, point in enumerate(query):
            if sums[i] <= 1.0e-12:
                outputs[i] = project_points(point[None, :], self.global_homography)[0]
                continue
            # Homography interpolation is performed in matrix space, then
            # normalised.  Invalid local nodes are already masked above.
            matrix = np.sum(self.homographies * weights[i, :, None, None], axis=0) / sums[i]
            if not np.isfinite(matrix).all() or abs(matrix[2, 2]) <= 1.0e-12:
                matrix = self.global_homography
            else:
                matrix = matrix / matrix[2, 2]
            mapped = project_points(point[None, :], matrix)[0]
            if np.isfinite(mapped).all():
                outputs[i] = mapped
            else:
                outputs[i] = project_points(point[None, :], self.global_homography)[0]
        return outputs

    __call__ = map_points


def fit_apap(
    source: np.ndarray,
    target: np.ndarray,
    *,
    global_homography: np.ndarray | None = None,
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | None = None,
    min_support: int = 4,
    max_controls_per_node: int = 64,
) -> APAPWarp:
    """Fit an APAP-style local homography field.

    ``source``/``target`` are expected to be inlier correspondences from the
    global RANSAC gate.  If a node is under-supported, its local model simply
    falls back to ``global_homography``; this prevents local extrapolation from
    manufacturing a panorama seam in texture-poor areas.
    """

    src, dst = validate_correspondences(source, target, min_points=4, name="APAP correspondences")
    if global_homography is None:
        global_homography = estimate_homography(src, dst)
    global_homography = np.asarray(global_homography, dtype=np.float64)
    if global_homography.shape != (3, 3) or not np.isfinite(global_homography).all():
        raise ValueError("global_homography must be a finite 3x3 matrix")
    if abs(global_homography[2, 2]) <= 1.0e-12:
        raise TransformEstimationError("global_homography is singular")
    global_homography = global_homography / global_homography[2, 2]

    rows, cols = max(int(grid_shape[0]), 1), max(int(grid_shape[1]), 1)
    lo = np.min(src, axis=0)
    hi = np.max(src, axis=0)
    if np.any(hi <= lo):
        raise TransformEstimationError("APAP source points have zero spatial extent")
    xs = np.linspace(lo[0], hi[0], cols)
    ys = np.linspace(lo[1], hi[1], rows)
    centers = np.stack(np.meshgrid(xs, ys), axis=-1).reshape(-1, 2)
    if sigma is None:
        sigma = max(float(np.linalg.norm(hi - lo)) / max(float(max(rows, cols)), 1.0), 1.0)
    sigma = max(float(sigma), 1.0e-8)

    homographies = np.repeat(global_homography[None, :, :], len(centers), axis=0)
    supports = np.zeros(len(centers), dtype=np.int32)
    for index, center in enumerate(centers):
        dist_sq = np.sum((src - center[None, :]) ** 2, axis=1)
        weights = np.exp(-dist_sq / (2.0 * sigma * sigma))
        # Keep the nearest controls bounded so a dense feature set does not
        # turn each local solve into an unbounded host-side workload.
        if len(weights) > int(max_controls_per_node):
            nearest = np.argpartition(dist_sq, int(max_controls_per_node) - 1)[: int(max_controls_per_node)]
            weights = np.where(np.isin(np.arange(len(weights)), nearest), weights, 0.0)
        supports[index] = int(np.count_nonzero(weights > 1.0e-3))
        if supports[index] < int(min_support):
            continue
        try:
            homographies[index] = _weighted_homography(src, dst, weights)
        except (ValueError, np.linalg.LinAlgError, TransformEstimationError):
            supports[index] = 0
    return APAPWarp(
        source_points=np.ascontiguousarray(src),
        target_points=np.ascontiguousarray(dst),
        centers=np.ascontiguousarray(centers),
        homographies=np.ascontiguousarray(homographies),
        global_homography=np.ascontiguousarray(global_homography),
        sigma=sigma,
        support_counts=supports,
    )


__all__ = ["APAPWarp", "fit_apap"]
