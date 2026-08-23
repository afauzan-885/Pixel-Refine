"""Regularised thin-plate-spline (TPS) refinement for image alignment.

TPS is intentionally a refinement layer.  It must be fitted from inlier
correspondences after a global affine/homography gate; this module therefore
does not silently discard bad control points or extrapolate an unconstrained
warp.  Coordinates are normalised before solving the TPS system so large
images (including 50 MP frames) do not make the small host-side solve
ill-conditioned.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .quality import TransformEstimationError, validate_correspondences


def _normalizer(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    center = np.mean(points, axis=0)
    scale = float(np.sqrt(np.mean(np.sum((points - center) ** 2, axis=1))))
    scale = max(scale, 1.0e-8)
    normalized = (points - center[None, :]) / scale
    return normalized, center, scale


def _kernel(points_a: np.ndarray, points_b: np.ndarray) -> np.ndarray:
    delta = points_a[:, None, :] - points_b[None, :, :]
    radius_sq = np.sum(delta * delta, axis=2)
    # U(r) = r^2 log(r^2); using log1p keeps coincident control points finite.
    return radius_sq * np.log(np.maximum(radius_sq, 1.0e-20))


@dataclass
class TPSWarp:
    """Fitted TPS map from source coordinates to destination coordinates."""

    control_points: np.ndarray
    weights: np.ndarray
    affine: np.ndarray
    source_center: np.ndarray
    source_scale: float
    destination_center: np.ndarray
    destination_scale: float
    regularization: float
    condition_number: float

    def map_points(self, points: np.ndarray) -> np.ndarray:
        """Evaluate the fitted map for an ``Nx2`` point array."""

        query = np.ascontiguousarray(points, dtype=np.float64)
        if query.ndim != 2 or query.shape[1:] != (2,):
            raise ValueError(f"points must have shape (N, 2), got {query.shape}")
        query_n = (query - self.source_center[None, :]) / self.source_scale
        radial = _kernel(query_n, self.control_points)
        affine_terms = np.column_stack((query_n, np.ones(len(query_n), dtype=np.float64)))
        mapped_n = radial @ self.weights + affine_terms @ self.affine
        return mapped_n * self.destination_scale + self.destination_center[None, :]

    __call__ = map_points

    def displacement(self, points: np.ndarray) -> np.ndarray:
        query = np.ascontiguousarray(points, dtype=np.float64)
        return self.map_points(query) - query

    def jacobian_determinants(
        self,
        bounds: tuple[float, float, float, float],
        *,
        grid_shape: tuple[int, int] = (8, 8),
    ) -> np.ndarray:
        """Approximate local Jacobian determinants on a regular source grid."""

        xmin, ymin, xmax, ymax = map(float, bounds)
        rows, cols = (max(int(grid_shape[0]), 2), max(int(grid_shape[1]), 2))
        xs = np.linspace(xmin, xmax, cols)
        ys = np.linspace(ymin, ymax, rows)
        grid = np.stack(np.meshgrid(xs, ys), axis=-1)
        mapped = self.map_points(grid.reshape(-1, 2)).reshape(rows, cols, 2)
        dx = max((xmax - xmin) / max(cols - 1, 1), 1.0e-8)
        dy = max((ymax - ymin) / max(rows - 1, 1), 1.0e-8)
        dfdx = np.gradient(mapped, dx, axis=1, edge_order=1)
        dfdy = np.gradient(mapped, dy, axis=0, edge_order=1)
        return dfdx[..., 0] * dfdy[..., 1] - dfdx[..., 1] * dfdy[..., 0]


@dataclass(frozen=True)
class TPSQuality:
    """Quality gate result for a fitted TPS map."""

    valid: bool
    condition_number: float
    control_points: int
    max_displacement: float
    foldover_fraction: float
    reason: str = ""

    def as_dict(self) -> dict[str, float | int | bool | str]:
        return {
            "valid": self.valid,
            "condition_number": self.condition_number,
            "control_points": self.control_points,
            "max_displacement": self.max_displacement,
            "foldover_fraction": self.foldover_fraction,
            "reason": self.reason,
        }


def fit_tps(
    source: np.ndarray,
    target: np.ndarray,
    *,
    regularization: float = 1.0e-3,
    max_condition_number: float = 1.0e12,
) -> TPSWarp:
    """Fit a regularised TPS map with normalised coordinates.

    At least three non-collinear control points are required.  Duplicate or
    nearly collinear points are rejected rather than producing a warp that can
    fold over the panorama canvas.
    """

    src, dst = validate_correspondences(source, target, min_points=3, name="TPS control points")
    if float(regularization) < 0.0:
        raise ValueError("regularization must be non-negative")
    if np.unique(src, axis=0).shape[0] < 3:
        raise TransformEstimationError("TPS control points contain duplicates")
    centered = src - np.mean(src, axis=0)
    if np.linalg.matrix_rank(centered) < 2:
        raise TransformEstimationError("TPS control points are collinear")

    src_n, src_center, src_scale = _normalizer(src)
    dst_n, dst_center, dst_scale = _normalizer(dst)
    n = len(src_n)
    K = _kernel(src_n, src_n)
    # The affine null-space constraints remain exact; regularisation only
    # damps the radial coefficients.
    K = K + np.eye(n, dtype=np.float64) * float(regularization)
    P = np.column_stack((src_n, np.ones(n, dtype=np.float64)))
    system = np.zeros((n + 3, n + 3), dtype=np.float64)
    system[:n, :n] = K
    system[:n, n:] = P
    system[n:, :n] = P.T
    rhs = np.zeros((n + 3, 2), dtype=np.float64)
    rhs[:n] = dst_n
    try:
        condition = float(np.linalg.cond(system))
        solution = np.linalg.solve(system, rhs)
    except np.linalg.LinAlgError as exc:
        raise TransformEstimationError("TPS linear system is singular") from exc
    if not np.isfinite(solution).all() or not np.isfinite(condition):
        raise TransformEstimationError("TPS solve produced non-finite coefficients")
    if condition > float(max_condition_number):
        raise TransformEstimationError(
            f"TPS system is ill-conditioned ({condition:.3g} > {float(max_condition_number):.3g})"
        )
    return TPSWarp(
        control_points=np.ascontiguousarray(src_n),
        weights=np.ascontiguousarray(solution[:n]),
        affine=np.ascontiguousarray(solution[n:]),
        source_center=np.asarray(src_center, dtype=np.float64),
        source_scale=float(src_scale),
        destination_center=np.asarray(dst_center, dtype=np.float64),
        destination_scale=float(dst_scale),
        regularization=float(regularization),
        condition_number=condition,
    )


def assess_tps(
    warp: TPSWarp,
    *,
    source_bounds: tuple[float, float, float, float] | None = None,
    max_displacement: float | None = None,
    max_condition_number: float = 1.0e12,
    min_jacobian: float = 1.0e-6,
    grid_shape: tuple[int, int] = (8, 8),
) -> TPSQuality:
    """Apply displacement/conditioning/fold-over safeguards to a TPS map."""

    if source_bounds is None:
        # Control points are in normalised coordinates; map a conservative
        # box around them when the caller does not provide image dimensions.
        points = warp.control_points * warp.source_scale + warp.source_center[None, :]
        lo = np.min(points, axis=0)
        hi = np.max(points, axis=0)
        source_bounds = (float(lo[0]), float(lo[1]), float(hi[0]), float(hi[1]))
    xmin, ymin, xmax, ymax = map(float, source_bounds)
    if xmax <= xmin or ymax <= ymin:
        return TPSQuality(False, warp.condition_number, len(warp.control_points), float("inf"), 1.0, "invalid source bounds")

    rows, cols = max(int(grid_shape[0]), 2), max(int(grid_shape[1]), 2)
    xs = np.linspace(xmin, xmax, cols)
    ys = np.linspace(ymin, ymax, rows)
    grid = np.stack(np.meshgrid(xs, ys), axis=-1).reshape(-1, 2)
    displacement = np.linalg.norm(warp.displacement(grid), axis=1)
    max_disp = float(np.max(displacement)) if displacement.size else 0.0
    determinants = warp.jacobian_determinants(source_bounds, grid_shape=(rows, cols))
    foldovers = np.count_nonzero(~np.isfinite(determinants) | (determinants <= float(min_jacobian)))
    fold_fraction = float(foldovers) / float(max(determinants.size, 1))

    valid = True
    reason = ""
    if not np.isfinite(warp.condition_number) or warp.condition_number > float(max_condition_number):
        valid, reason = False, "TPS system is ill-conditioned"
    elif max_displacement is not None and max_disp > float(max_displacement):
        valid, reason = False, f"displacement {max_disp:.3f} exceeds {float(max_displacement):.3f}"
    elif foldovers:
        valid, reason = False, f"{int(foldovers)} grid cells fail Jacobian orientation"
    return TPSQuality(
        valid=bool(valid),
        condition_number=float(warp.condition_number),
        control_points=int(len(warp.control_points)),
        max_displacement=max_disp,
        foldover_fraction=fold_fraction,
        reason=reason,
    )


def fit_tps_checked(
    source: np.ndarray,
    target: np.ndarray,
    *,
    regularization: float = 1.0e-3,
    source_bounds: tuple[float, float, float, float] | None = None,
    max_displacement: float | None = None,
    max_condition_number: float = 1.0e12,
) -> tuple[TPSWarp, TPSQuality]:
    """Fit TPS and return its quality result for a caller-selected fallback."""

    warp = fit_tps(
        source,
        target,
        regularization=regularization,
        max_condition_number=max_condition_number,
    )
    quality = assess_tps(
        warp,
        source_bounds=source_bounds,
        max_displacement=max_displacement,
        max_condition_number=max_condition_number,
    )
    return warp, quality


__all__ = ["TPSWarp", "TPSQuality", "fit_tps", "assess_tps", "fit_tps_checked"]
