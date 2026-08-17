"""Geometry validation and robust transform estimation for image alignment.

The low-level Taichi kernels in :mod:`alignment.ransac` already provide the
device-side primitives used by the public AOT facade.  This module owns the
small, deterministic host-side contract around those primitives: point
validation, model fitting, reprojection diagnostics, and fail-closed quality
gates.  Keeping this contract local means panorama and other callers do not
each grow a slightly different RANSAC/``NaN`` handling implementation.

The NumPy implementation is deliberately a reference/fallback path.  A
caller may pass a device-backed estimator (for example
``taichi_aot.find_homography``) and still use :func:`evaluate_transform` for
the same quality gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np


class TransformEstimationError(ValueError):
    """Raised when a transform cannot be estimated safely."""


@dataclass(frozen=True)
class TransformQuality:
    """Serializable diagnostics used to accept or reject a transform."""

    model: str
    total_points: int
    inliers: int
    inlier_ratio: float
    median_error: float
    p95_error: float
    max_error: float
    spatial_coverage: float
    condition_number: float
    determinant: float
    valid: bool
    reason: str = ""

    def as_dict(self) -> dict[str, float | int | bool | str]:
        return {
            "model": self.model,
            "total_points": self.total_points,
            "inliers": self.inliers,
            "inlier_ratio": self.inlier_ratio,
            "median_error": self.median_error,
            "p95_error": self.p95_error,
            "max_error": self.max_error,
            "spatial_coverage": self.spatial_coverage,
            "condition_number": self.condition_number,
            "determinant": self.determinant,
            "valid": self.valid,
            "reason": self.reason,
        }


def validate_correspondences(
    source: np.ndarray,
    target: np.ndarray,
    *,
    min_points: int = 3,
    name: str = "correspondences",
) -> tuple[np.ndarray, np.ndarray]:
    """Return finite ``float64`` point pairs with a strict shape contract."""

    src = np.ascontiguousarray(source, dtype=np.float64)
    dst = np.ascontiguousarray(target, dtype=np.float64)
    if src.ndim != 2 or dst.ndim != 2 or src.shape[1:] != (2,) or dst.shape[1:] != (2,):
        raise ValueError(f"{name} must contain Nx2 arrays, got {src.shape} and {dst.shape}")
    if src.shape[0] != dst.shape[0]:
        raise ValueError(f"{name} point counts differ: {src.shape[0]} vs {dst.shape[0]}")
    finite = np.isfinite(src).all(axis=1) & np.isfinite(dst).all(axis=1)
    src, dst = src[finite], dst[finite]
    if src.shape[0] < int(min_points):
        raise TransformEstimationError(
            f"{name} needs at least {int(min_points)} finite pairs; got {src.shape[0]}"
        )
    return src, dst


def project_points(points: np.ndarray, transform: np.ndarray, *, model: str = "homography") -> np.ndarray:
    """Project ``Nx2`` points through a 3x3 affine or projective matrix."""

    pts = np.ascontiguousarray(points, dtype=np.float64)
    matrix = np.asarray(transform, dtype=np.float64)
    if pts.ndim != 2 or pts.shape[1:] != (2,):
        raise ValueError(f"points must have shape (N, 2), got {pts.shape}")
    if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
        raise ValueError("transform must be a finite 3x3 matrix")
    homog = np.column_stack((pts, np.ones(len(pts), dtype=np.float64)))
    projected = homog @ matrix.T
    if model.lower() in {"affine", "similarity", "translation"}:
        return projected[:, :2]
    denom = projected[:, 2]
    out = np.full((len(pts), 2), np.nan, dtype=np.float64)
    good = np.abs(denom) > np.finfo(np.float64).eps
    out[good] = projected[good, :2] / denom[good, None]
    return out


def _spatial_coverage(points: np.ndarray, *, grid_size: int = 4) -> float:
    """Fraction of occupied cells in a normalized source-point grid."""

    if len(points) == 0:
        return 0.0
    lo = np.min(points, axis=0)
    hi = np.max(points, axis=0)
    span = hi - lo
    if np.any(span <= np.finfo(np.float64).eps):
        return 0.0
    normalized = np.clip((points - lo) / span, 0.0, 1.0 - np.finfo(np.float64).eps)
    cells = np.floor(normalized * int(grid_size)).astype(np.int32)
    occupied = np.unique(cells[:, 0] * int(grid_size) + cells[:, 1])
    return float(len(occupied)) / float(int(grid_size) ** 2)


def evaluate_transform(
    source: np.ndarray,
    target: np.ndarray,
    transform: np.ndarray,
    *,
    model: str = "homography",
    inlier_mask: np.ndarray | None = None,
    reprojection_threshold: float = 3.0,
    min_inliers: int = 4,
    min_inlier_ratio: float = 0.25,
    min_spatial_coverage: float = 0.05,
    max_median_error: float = 3.0,
    max_p95_error: float = 8.0,
    max_condition_number: float = 1.0e12,
) -> TransformQuality:
    """Compute residual and degeneracy diagnostics and apply a quality gate.

    The gate is intentionally conservative for panorama use: a transform with
    many matches concentrated on one edge is rejected even when its average
    reprojection error is small.  Callers can lower the thresholds explicitly
    for controlled laboratory scenes.
    """

    raw_src = np.ascontiguousarray(source, dtype=np.float64)
    raw_dst = np.ascontiguousarray(target, dtype=np.float64)
    if raw_src.ndim != 2 or raw_dst.ndim != 2 or raw_src.shape[1:] != (2,) or raw_dst.shape[1:] != (2,):
        raise ValueError(f"source and target must contain Nx2 arrays, got {raw_src.shape} and {raw_dst.shape}")
    if raw_src.shape[0] != raw_dst.shape[0]:
        raise ValueError("source and target point counts differ")
    finite_rows = np.isfinite(raw_src).all(axis=1) & np.isfinite(raw_dst).all(axis=1)
    src, dst = validate_correspondences(raw_src[finite_rows], raw_dst[finite_rows], min_points=1)
    projected = project_points(src, transform, model=model)
    errors = np.linalg.norm(projected - dst, axis=1)
    finite = np.isfinite(errors)
    threshold = max(float(reprojection_threshold), np.finfo(np.float64).eps)
    if inlier_mask is None:
        mask = finite & (errors <= threshold)
    else:
        raw = np.asarray(inlier_mask).reshape(-1).astype(bool)
        if raw.shape[0] != raw_src.shape[0]:
            raise ValueError("inlier_mask length does not match correspondences")
        mask = raw[finite_rows] & finite

    selected = errors[mask]
    inliers = int(selected.size)
    ratio = float(inliers) / float(max(len(src), 1))
    median = float(np.median(selected)) if inliers else float("inf")
    p95 = float(np.percentile(selected, 95.0)) if inliers else float("inf")
    maximum = float(np.max(selected)) if inliers else float("inf")
    coverage = _spatial_coverage(src[mask] if inliers else src)

    matrix = np.asarray(transform, dtype=np.float64)
    try:
        condition = float(np.linalg.cond(matrix))
    except np.linalg.LinAlgError:
        condition = float("inf")
    determinant = float(np.linalg.det(matrix[:2, :2]))

    reason = ""
    valid = True
    if not np.isfinite(matrix).all() or not np.isfinite(errors).any():
        valid, reason = False, "non-finite transform or projection"
    elif inliers < int(min_inliers):
        valid, reason = False, f"too few inliers ({inliers} < {int(min_inliers)})"
    elif ratio < float(min_inlier_ratio):
        valid, reason = False, f"inlier ratio {ratio:.3f} < {float(min_inlier_ratio):.3f}"
    elif coverage < float(min_spatial_coverage):
        valid, reason = False, f"spatial coverage {coverage:.3f} < {float(min_spatial_coverage):.3f}"
    elif median > float(max_median_error):
        valid, reason = False, f"median reprojection error {median:.3f} > {float(max_median_error):.3f}"
    elif p95 > float(max_p95_error):
        valid, reason = False, f"p95 reprojection error {p95:.3f} > {float(max_p95_error):.3f}"
    elif not np.isfinite(condition) or condition > float(max_condition_number):
        valid, reason = False, f"ill-conditioned transform ({condition:.3g})"
    elif abs(determinant) <= 1.0e-12:
        valid, reason = False, "singular transform"

    return TransformQuality(
        model=str(model),
        total_points=int(len(src)),
        inliers=inliers,
        inlier_ratio=ratio,
        median_error=median,
        p95_error=p95,
        max_error=maximum,
        spatial_coverage=coverage,
        condition_number=condition,
        determinant=determinant,
        valid=bool(valid),
        reason=reason,
    )


def accept_transform(*args, **kwargs) -> bool:
    """Return only the boolean result of :func:`evaluate_transform`.

    This convenience form is useful at application boundaries where the full
    metrics are already logged separately.
    """

    return bool(evaluate_transform(*args, **kwargs).valid)


def estimate_translation(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Robust translation estimate using the component-wise median offset."""

    src, dst = validate_correspondences(source, target, min_points=1)
    delta = np.median(dst - src, axis=0)
    matrix = np.eye(3, dtype=np.float64)
    matrix[:2, 2] = delta
    return matrix


def estimate_affine(source: np.ndarray, target: np.ndarray, *, weights: np.ndarray | None = None) -> np.ndarray:
    """Least-squares 2-D affine estimate with finite/rank checks."""

    src, dst = validate_correspondences(source, target, min_points=3)
    design = np.column_stack((src, np.ones(len(src), dtype=np.float64)))
    if weights is not None:
        w = np.asarray(weights, dtype=np.float64).reshape(-1)
        if len(w) != len(src):
            raise ValueError("weights length does not match correspondences")
        scale = np.sqrt(np.clip(w, 0.0, None))[:, None]
        design = design * scale
        dst = dst * scale
    if np.linalg.matrix_rank(design) < 3:
        raise TransformEstimationError("affine correspondences are rank deficient")
    coeff, _, rank, _ = np.linalg.lstsq(design, dst, rcond=None)
    if int(rank) < 3 or not np.isfinite(coeff).all():
        raise TransformEstimationError("affine least-squares solve failed")
    matrix = np.eye(3, dtype=np.float64)
    matrix[:2, :] = coeff.T
    return matrix


def _normalize_points(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    center = np.mean(points, axis=0)
    radius = np.sqrt(np.mean(np.sum((points - center) ** 2, axis=1)))
    scale = np.sqrt(2.0) / max(float(radius), 1.0e-12)
    transform = np.array(
        [[scale, 0.0, -scale * center[0]], [0.0, scale, -scale * center[1]], [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    homogeneous = np.column_stack((points, np.ones(len(points), dtype=np.float64)))
    normalized = homogeneous @ transform.T
    return normalized[:, :2], transform


def estimate_homography(source: np.ndarray, target: np.ndarray, *, weights: np.ndarray | None = None) -> np.ndarray:
    """Normalized DLT homography estimate with optional row weights."""

    src, dst = validate_correspondences(source, target, min_points=4)
    src_n, src_t = _normalize_points(src)
    dst_n, dst_t = _normalize_points(dst)
    rows = []
    for (x, y), (u, v) in zip(src_n, dst_n):
        rows.append([-x, -y, -1.0, 0.0, 0.0, 0.0, u * x, u * y, u])
        rows.append([0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v])
    design = np.asarray(rows, dtype=np.float64)
    if weights is not None:
        w = np.asarray(weights, dtype=np.float64).reshape(-1)
        if len(w) != len(src):
            raise ValueError("weights length does not match correspondences")
        design *= np.repeat(np.sqrt(np.clip(w, 0.0, None)), 2)[:, None]
    if np.linalg.matrix_rank(design) < 8:
        raise TransformEstimationError("homography correspondences are rank deficient")
    _, singular_values, vh = np.linalg.svd(design, full_matrices=False)
    if singular_values[-1] > max(singular_values[0], 1.0) * 1.0e-10:
        # A non-zero smallest singular value is normal for noisy data; only a
        # clearly rank-deficient design should be rejected above.
        pass
    h = vh[-1].reshape(3, 3)
    try:
        matrix = np.linalg.inv(dst_t) @ h @ src_t
    except np.linalg.LinAlgError as exc:
        raise TransformEstimationError("homography denormalization failed") from exc
    if abs(matrix[2, 2]) <= 1.0e-12 or not np.isfinite(matrix).all():
        raise TransformEstimationError("homography solve produced an invalid matrix")
    return matrix / matrix[2, 2]


def ransac_transform(
    source: np.ndarray,
    target: np.ndarray,
    *,
    model: str = "homography",
    reprojection_threshold: float = 3.0,
    iterations: int = 512,
    seed: int = 0,
    quality_kwargs: dict[str, float | int] | None = None,
) -> tuple[np.ndarray, np.ndarray, TransformQuality]:
    """Deterministic NumPy RANSAC reference for affine/homography alignment."""

    src, dst = validate_correspondences(source, target, min_points=3 if model in {"affine", "similarity"} else 4)
    key = str(model).lower()
    if key in {"translation", "shift"}:
        matrix = estimate_translation(src, dst)
        errors = np.linalg.norm(project_points(src, matrix, model="translation") - dst, axis=1)
        mask = np.isfinite(errors) & (errors <= float(reprojection_threshold))
        options = dict(quality_kwargs or {})
        options.setdefault("min_inliers", 3)
        quality = evaluate_transform(src, dst, matrix, model="translation", inlier_mask=mask, **options)
        return matrix, mask, quality
    if key in {"similarity", "affine"}:
        sample_size, fit = 3, estimate_affine
        key = "affine"
    elif key in {"homography", "projective"}:
        sample_size, fit = 4, estimate_homography
        key = "homography"
    else:
        raise ValueError(f"unsupported transform model: {model!r}")

    rng = np.random.default_rng(int(seed))
    threshold = max(float(reprojection_threshold), np.finfo(np.float64).eps)
    best_matrix: np.ndarray | None = None
    best_mask: np.ndarray | None = None
    best_score: tuple[int, float] = (-1, float("inf"))
    for _ in range(max(int(iterations), 1)):
        indices = rng.choice(len(src), size=sample_size, replace=False)
        try:
            matrix = fit(src[indices], dst[indices])
        except (ValueError, np.linalg.LinAlgError, TransformEstimationError):
            continue
        projected = project_points(src, matrix, model=key)
        errors = np.linalg.norm(projected - dst, axis=1)
        mask = np.isfinite(errors) & (errors <= threshold)
        count = int(mask.sum())
        median = float(np.median(errors[mask])) if count else float("inf")
        score = (count, median)
        if count > best_score[0] or (count == best_score[0] and median < best_score[1]):
            best_score = score
            best_matrix, best_mask = matrix, mask

    if best_matrix is None or best_mask is None or int(best_mask.sum()) < sample_size:
        raise TransformEstimationError(f"RANSAC could not find a valid {key} model")
    try:
        refined = fit(src[best_mask], dst[best_mask])
    except (ValueError, np.linalg.LinAlgError, TransformEstimationError):
        refined = best_matrix
    errors = np.linalg.norm(project_points(src, refined, model=key) - dst, axis=1)
    final_mask = np.isfinite(errors) & (errors <= threshold)
    options = dict(quality_kwargs or {})
    options.setdefault("min_inliers", sample_size)
    quality = evaluate_transform(
        src,
        dst,
        refined,
        model=key,
        inlier_mask=final_mask,
        reprojection_threshold=threshold,
        **options,
    )
    return refined, final_mask, quality


def choose_best_transform(
    source: np.ndarray,
    target: np.ndarray,
    *,
    models: Iterable[str] = ("translation", "affine", "homography"),
    reprojection_threshold: float = 3.0,
    iterations: int = 512,
    seed: int = 0,
    quality_kwargs: dict[str, float | int] | None = None,
) -> tuple[np.ndarray, np.ndarray, TransformQuality]:
    """Try increasingly expressive models and return the best gated result."""

    candidates: list[tuple[np.ndarray, np.ndarray, TransformQuality]] = []
    for offset, model in enumerate(models):
        try:
            candidate = ransac_transform(
                source,
                target,
                model=model,
                reprojection_threshold=reprojection_threshold,
                iterations=iterations,
                seed=seed + offset * 104729,
                quality_kwargs=quality_kwargs,
            )
        except (ValueError, TransformEstimationError, np.linalg.LinAlgError):
            continue
        candidates.append(candidate)
    if not candidates:
        raise TransformEstimationError("no transform model passed estimation")
    valid = [candidate for candidate in candidates if candidate[2].valid]
    pool = valid or candidates
    # Prefer the simplest model when errors are comparable.  Homography is
    # selected only when it provides a materially better residual/inlier ratio.
    order = {"translation": 0, "affine": 1, "homography": 2}
    return min(
        pool,
        key=lambda item: (
            round(item[2].median_error / max(item[2].inlier_ratio, 1.0e-9), 6),
            order.get(item[2].model, 99),
        ),
    )


__all__ = [
    "TransformEstimationError",
    "TransformQuality",
    "validate_correspondences",
    "project_points",
    "evaluate_transform",
    "accept_transform",
    "estimate_translation",
    "estimate_affine",
    "estimate_homography",
    "ransac_transform",
    "choose_best_transform",
]
