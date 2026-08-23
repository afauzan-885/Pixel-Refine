"""Bounded, validated orchestration for the existing SfM/MVS primitives.

The low-level modules in :mod:`sfm` intentionally expose individual kernels
and numerical routines.  Applications still need a small amount of glue to
make those routines safe to compose: strict input validation, pose selection,
reprojection/cheirality gates, confidence values, and a memory budget before
allocating a plane-sweep volume.  This module owns that glue only; it does not
reimplement an estimator or a point-cloud kernel.

The API is backend-neutral.  Plane sweep keeps its historical
``backend="auto"`` selection, while callers may force ``backend="numpy"``,
explicitly require the existing Taichi JIT kernels with ``backend="taichi"``,
or dispatch the target-qualified research ``sfm_stereo`` leaves with
``backend="aot"``.
Reports retain the requested selector and quality diagnostics without claiming
an unobserved device.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Any, Sequence

import numpy as np

from ..pipeline_common import (
    PipelineReport,
    as_float32_matrix,
    as_gray_float32,
    finite_fraction,
    timed_stage,
    update_stage_output,
)
from .cheirality_check import check_cheirality_full, check_cheirality_minimal
from .five_point_solver import solve_five_point
from ..alignment.ransac import vsac_fundamental
from ..common import enforce_essential_np
from .plane_sweep import multi_view_plane_sweep, plane_sweep_stereo
from .point_cloud import preprocess_point_cloud
from .poisson_recon import poisson_reconstruct
from .triangulation import _triangulate_dlt_np, triangulate_adaptive


_EMPTY_POINTS = np.empty((0, 3), dtype=np.float32)
_EMPTY_FACES = np.empty((0, 3), dtype=np.int32)


@dataclass(frozen=True)
class PairwiseSfMConfig:
    """Quality gates and bounded work controls for :func:`reconstruct_pair`.

    ``max_hypotheses`` does not change the underlying five-point solver.  It
    only controls how many deterministic five-point subsets are evaluated
    before selecting the pose with the largest geometrically valid consensus.
    """

    reprojection_threshold_px: float = 2.0
    min_inlier_count: int = 8
    min_inlier_ratio: float = 0.2
    min_cheirality_ratio: float = 0.6
    parallax_threshold_deg: float = 4.0
    noise_sigma: float = 0.5
    max_hypotheses: int = 8
    sample_seed: int = 0


@dataclass
class PairwiseSfMResult:
    """Output of a pairwise calibrated SfM step.

    ``points_3d`` and all per-point arrays correspond to ``inlier_indices``;
    the original correspondence order is preserved by that index array.
    A failed quality gate returns empty arrays and ``success=False`` instead
    of silently returning an untrusted pose.
    """

    success: bool
    essential: np.ndarray | None = None
    rotation: np.ndarray | None = None
    translation: np.ndarray | None = None
    points_3d: np.ndarray = field(default_factory=lambda: _EMPTY_POINTS.copy())
    inlier_indices: np.ndarray = field(
        default_factory=lambda: np.empty(0, dtype=np.int32)
    )
    inlier_mask: np.ndarray = field(
        default_factory=lambda: np.empty(0, dtype=bool)
    )
    reprojection_error_px: np.ndarray = field(
        default_factory=lambda: np.empty(0, dtype=np.float32)
    )
    parallax_deg: np.ndarray = field(
        default_factory=lambda: np.empty(0, dtype=np.float32)
    )
    confidence: np.ndarray = field(
        default_factory=lambda: np.empty(0, dtype=np.float32)
    )
    report: PipelineReport = field(
        default_factory=lambda: PipelineReport("sfm_pair")
    )


@dataclass
class MVSResult:
    """Bounded dense-depth result from plane sweep."""

    depth: np.ndarray
    confidence: np.ndarray
    report: PipelineReport


@dataclass
class PointCloudResult:
    """Result of point-cloud filtering, normals, and optional meshing."""

    points: np.ndarray
    normals: np.ndarray
    source_keep_indices: np.ndarray
    vertices: np.ndarray = field(default_factory=lambda: _EMPTY_POINTS.copy())
    faces: np.ndarray = field(default_factory=lambda: _EMPTY_FACES.copy())
    report: PipelineReport = field(
        default_factory=lambda: PipelineReport("point_cloud")
    )


@dataclass
class SequenceSfMResult:
    """Validated camera-chain result for a calibrated image sequence."""

    success: bool
    poses_world_to_camera: list[np.ndarray]
    pair_results: list[PairwiseSfMResult]
    report: PipelineReport


def _as_correspondences(value: Any, *, name: str) -> np.ndarray:
    array = np.ascontiguousarray(value, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 2:
        raise ValueError(f"{name} must have shape (N, 2), got {array.shape}")
    if array.shape[0] == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def _as_intrinsics(value: Any, *, name: str) -> np.ndarray:
    matrix = np.asarray(as_float32_matrix(value, (3, 3), name=name), dtype=np.float64)
    if matrix[0, 0] <= 0 or matrix[1, 1] <= 0:
        raise ValueError(f"{name} focal lengths must be positive")
    if abs(matrix[2, 2]) < 1e-12:
        raise ValueError(f"{name}[2,2] must be non-zero")
    return matrix


def _normalise_points(points: np.ndarray, K: np.ndarray) -> np.ndarray:
    homogeneous = np.concatenate(
        [points, np.ones((points.shape[0], 1), dtype=np.float64)], axis=1
    )
    return (np.linalg.inv(K) @ homogeneous.T).T[:, :2]


def _spread_sample_indices(points: np.ndarray, *, seed: int = 0) -> np.ndarray:
    """Choose five spatially separated points deterministically.

    A five-point solver is sensitive to a clustered sample.  The first four
    points are selected from the extrema of the two diagonal directions; a
    seeded farthest-point pass fills any duplicate/extreme slots.  This is a
    sampling policy, not another essential-matrix implementation.
    """

    n = int(points.shape[0])
    if n < 5:
        raise ValueError("at least five correspondences are required")

    scores = (
        np.sum(points, axis=1),
        points[:, 0] - points[:, 1],
    )
    candidate = [
        int(np.argmin(scores[0])),
        int(np.argmax(scores[0])),
        int(np.argmin(scores[1])),
        int(np.argmax(scores[1])),
    ]
    selected: list[int] = []
    for index in candidate:
        if index not in selected:
            selected.append(index)

    # Farthest-point completion protects collinear/extreme duplicate cases.
    if selected:
        distances = np.min(
            np.sum((points[:, None, :] - points[np.asarray(selected)][None, :, :]) ** 2, axis=2),
            axis=1,
        )
    else:
        center = np.mean(points, axis=0)
        distances = np.sum((points - center) ** 2, axis=1)
    rng = np.random.default_rng(int(seed))
    tie_noise = rng.uniform(0.0, 1e-12, size=n)
    while len(selected) < 5:
        distances[np.asarray(selected, dtype=np.int32)] = -np.inf
        index = int(np.argmax(distances + tie_noise))
        if index in selected:
            break
        selected.append(index)
        distances = np.minimum(
            distances,
            np.sum((points - points[index]) ** 2, axis=1),
        )

    if len(selected) < 5:
        for index in range(n):
            if index not in selected:
                selected.append(index)
            if len(selected) == 5:
                break
    return np.asarray(selected[:5], dtype=np.int32)


def _projection_matrix(rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
    return np.concatenate(
        [np.asarray(rotation, dtype=np.float64), np.asarray(translation, dtype=np.float64).reshape(3, 1)],
        axis=1,
    )


def _estimate_all_point_essential(q1: np.ndarray, q2: np.ndarray) -> np.ndarray | None:
    """Estimate a calibrated essential matrix from all normalized matches.

    This is a bounded, deterministic consensus fallback for a weak native
    VSAC mask.  It is not used as the primary minimal solver: the existing
    five-point/VSAC candidates are evaluated first.  The normalized
    eight-point estimate is still subjected to the same cheirality,
    reprojection, and inlier-ratio gates before it can be selected.
    """

    first = np.asarray(q1, dtype=np.float64)
    second = np.asarray(q2, dtype=np.float64)
    if first.ndim != 2 or second.ndim != 2 or first.shape != second.shape:
        raise ValueError("normalized correspondence arrays must have equal shape (N, 2)")
    if first.shape[0] < 8 or not np.isfinite(first).all() or not np.isfinite(second).all():
        return None
    design = np.column_stack(
        [
            second[:, 0] * first[:, 0],
            second[:, 0] * first[:, 1],
            second[:, 0],
            second[:, 1] * first[:, 0],
            second[:, 1] * first[:, 1],
            second[:, 1],
            first[:, 0],
            first[:, 1],
            np.ones(first.shape[0], dtype=np.float64),
        ]
    )
    try:
        _, _, vt = np.linalg.svd(design, full_matrices=False)
        candidate = enforce_essential_np(vt[-1].reshape(3, 3))
    except (np.linalg.LinAlgError, ValueError):
        return None
    return np.asarray(candidate, dtype=np.float64) if np.isfinite(candidate).all() else None


def _project_points(
    points_3d: np.ndarray,
    K: np.ndarray,
    rotation: np.ndarray,
    translation: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    camera = (np.asarray(rotation, dtype=np.float64) @ points_3d.T).T
    camera += np.asarray(translation, dtype=np.float64).reshape(1, 3)
    depth = camera[:, 2]
    projected = np.full((len(points_3d), 2), np.nan, dtype=np.float64)
    valid = np.isfinite(depth) & (np.abs(depth) > 1e-12)
    if np.any(valid):
        image = (K @ camera[valid].T).T
        projected[valid] = image[:, :2] / image[:, 2:3]
    return projected, depth


def _parallax_for_points(
    points_3d: np.ndarray,
    rotation: np.ndarray,
    translation: np.ndarray,
) -> np.ndarray:
    """Return the angle between the two camera rays for each 3D point."""

    # P1=[I|0], P2=[R|t] has camera centres C1=0 and C2=-R^T t.
    c1 = np.zeros(3, dtype=np.float64)
    c2 = -np.asarray(rotation, dtype=np.float64).T @ np.asarray(translation, dtype=np.float64)
    ray1 = points_3d - c1
    ray2 = points_3d - c2
    n1 = np.linalg.norm(ray1, axis=1)
    n2 = np.linalg.norm(ray2, axis=1)
    denom = np.maximum(n1 * n2, 1e-12)
    cosine = np.sum(ray1 * ray2, axis=1) / denom
    cosine = np.clip(cosine, -1.0, 1.0)
    result = np.degrees(np.arccos(cosine))
    result[~np.isfinite(result)] = 0.0
    return result.astype(np.float32)


def _triangulate_checked(
    points1: np.ndarray,
    points2: np.ndarray,
    q1: np.ndarray,
    q2: np.ndarray,
    K1: np.ndarray,
    K2: np.ndarray,
    P1: np.ndarray,
    P2: np.ndarray,
    rotation: np.ndarray,
    translation: np.ndarray,
    parallax_threshold_deg: float,
    noise_sigma: float,
) -> tuple[np.ndarray, str, int]:
    """Run adaptive triangulation and fail closed to projection-matrix DLT.

    The adaptive implementation is retained as the fast path for its
    documented normalized-ray regime.  A historical camera-2 orientation
    limitation can produce a geometrically valid-looking but high-residual
    cloud for arbitrary rotations, so every result is checked by reprojection
    before it is accepted.  The DLT helper is the same full-frame reference
    implementation used by the cheirality module.
    """

    dlt = np.asarray(_triangulate_dlt_np(q1, q2, P1, P2), dtype=np.float64)
    dlt_1, _ = _project_points(dlt, K1, np.eye(3), np.zeros(3))
    dlt_2, _ = _project_points(dlt, K2, rotation, translation)
    dlt_error = 0.5 * np.sqrt(
        np.sum((dlt_1 - points1) ** 2, axis=1)
        + np.sum((dlt_2 - points2) ** 2, axis=1)
    )
    dlt_finite = np.isfinite(dlt_error) & np.isfinite(dlt).all(axis=1)

    try:
        adaptive, _, _ = triangulate_adaptive(
            points1,
            points2,
            P1,
            P2,
            K1,
            K2,
            parallax_threshold=parallax_threshold_deg,
            noise_sigma=noise_sigma,
        )
        adaptive = np.asarray(adaptive, dtype=np.float64)
        adaptive_1, _ = _project_points(adaptive, K1, np.eye(3), np.zeros(3))
        adaptive_2, _ = _project_points(adaptive, K2, rotation, translation)
        adaptive_error = 0.5 * np.sqrt(
            np.sum((adaptive_1 - points1) ** 2, axis=1)
            + np.sum((adaptive_2 - points2) ** 2, axis=1)
        )
        adaptive_finite = np.isfinite(adaptive_error) & np.isfinite(adaptive).all(axis=1)
    except Exception:
        adaptive = None
        adaptive_error = np.full(len(points1), np.inf, dtype=np.float64)
        adaptive_finite = np.zeros(len(points1), dtype=bool)

    use_adaptive = adaptive_finite & (~dlt_finite | (adaptive_error < dlt_error))
    selected = dlt.copy()
    if adaptive is not None and np.any(use_adaptive):
        selected[use_adaptive] = adaptive[use_adaptive]
    fallback_count = int(np.count_nonzero(~use_adaptive))
    method = "adaptive" if fallback_count == 0 else "dlt_fallback"
    return selected, method, fallback_count


def _failure_pair_result(report: PipelineReport, warning: str) -> PairwiseSfMResult:
    report.success = False
    report.add_warning(warning)
    return PairwiseSfMResult(success=False, report=report)


def reconstruct_pair(
    points1: Any,
    points2: Any,
    K1: Any,
    K2: Any,
    *,
    config: PairwiseSfMConfig | None = None,
    backend: str = "auto",
) -> PairwiseSfMResult:
    """Estimate a calibrated pair pose and triangulate trusted points.

    ``backend="numpy"`` explicitly selects the maintained host/reference pose
    solver.  ``backend="aot"`` is fail-closed because the repository has only
    lower-level geometry leaves, not a complete five-point decomposition and
    pose-selection graph.  Existing functions perform the numerical work:
    ``solve_five_point`` supplies
    essential candidates, the cheirality module selects a valid decomposition,
    and the existing DLT helper triangulates arbitrary relative rotations.
    This wrapper adds deterministic hypotheses, reprojection and positive
    depth gates, and a confidence score suitable for downstream fusion.
    """

    backend_name = str(backend).strip().lower()
    if backend_name not in {"auto", "numpy", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', or 'aot'")
    if backend_name == "aot":
        raise NotImplementedError(
            "reconstruct_pair has no complete target-qualified AOT pose solver; "
            "use backend='numpy' explicitly or compose the sfm_geometry leaves"
        )

    cfg = config or PairwiseSfMConfig()
    if cfg.reprojection_threshold_px <= 0:
        raise ValueError("reprojection_threshold_px must be positive")
    if cfg.min_inlier_count < 1 or not (0.0 < cfg.min_inlier_ratio <= 1.0):
        raise ValueError("invalid inlier quality gates")
    if not (0.0 < cfg.min_cheirality_ratio <= 1.0):
        raise ValueError("min_cheirality_ratio must be in (0, 1]")
    if cfg.max_hypotheses < 1:
        raise ValueError("max_hypotheses must be positive")

    report = PipelineReport("sfm_pair", backend=f"sfm-pair-{backend_name}")
    if backend_name == "auto" and os.environ.get("AOT_MODE", "0") == "1":
        # The complete pose solver is not a qualified AOT graph.  Historical
        # ``auto`` therefore keeps its host reference path, but the boundary
        # must be observable instead of looking like native AOT execution.
        report.add_warning(
            "backend_boundary=host-reference: auto pairwise SfM uses the "
            "maintained NumPy/OpenCV pose selector; use backend='numpy' "
            "to make that choice explicit"
        )
        report.metrics["backend_fallback_count"] = 1.0
    p1 = _as_correspondences(points1, name="points1")
    p2 = _as_correspondences(points2, name="points2")
    if len(p1) != len(p2):
        raise ValueError(f"points1 and points2 lengths differ: {len(p1)} vs {len(p2)}")
    if len(p1) < 5:
        raise ValueError("at least five point correspondences are required")
    k1 = _as_intrinsics(K1, name="K1")
    k2 = _as_intrinsics(K2, name="K2")
    report.metrics["n_matches"] = float(len(p1))
    # ``triangulate_adaptive`` is attempted through ``_triangulate_checked``;
    # its historical wMid2/LOST path assumes identity camera orientation when
    # it builds rays, so arbitrary-rotation pairs fall back to projection-
    # matrix DLT after a reprojection check.
    q1_all = _normalise_points(p1, k1)
    q2_all = _normalise_points(p2, k2)

    # Generate a bounded set of spatially separated hypotheses.  The solver
    # itself consumes exactly five rows, so every call receives one sample.
    with timed_stage(report, "essential_candidates"):
        base = _spread_sample_indices(p1, seed=cfg.sample_seed)
        samples = [base]
        if cfg.max_hypotheses > 1 and len(p1) > 5:
            rng = np.random.default_rng(int(cfg.sample_seed))
            for _ in range(int(cfg.max_hypotheses) - 1):
                samples.append(rng.choice(len(p1), size=5, replace=False).astype(np.int32))

        candidates: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, int]] = []
        P1 = _projection_matrix(np.eye(3), np.zeros(3))
        for sample_indices in samples:
            try:
                essential_candidates = solve_five_point(
                    p1[sample_indices], p2[sample_indices], k1, k2
                )
            except Exception:
                continue
            for essential in essential_candidates:
                try:
                    valid_pose, rotation, translation = check_cheirality_minimal(
                        essential,
                        k1,
                        k2,
                        p1[sample_indices],
                        p2[sample_indices],
                    )
                except Exception:
                    continue
                if not valid_pose or rotation is None or translation is None:
                    continue
                rotation = np.asarray(rotation, dtype=np.float64)
                translation = np.asarray(translation, dtype=np.float64).reshape(3)
                P2 = _projection_matrix(rotation, translation)
                try:
                    _, cheirality_mask = check_cheirality_full(
                        rotation, translation, k1, k2, p1, p2
                    )
                    points_3d, triangulation_method, fallback_count = _triangulate_checked(
                        p1,
                        p2,
                        q1_all,
                        q2_all,
                        k1,
                        k2,
                        P1,
                        P2,
                        rotation,
                        translation,
                        cfg.parallax_threshold_deg,
                        cfg.noise_sigma,
                    )
                except Exception:
                    continue
                points_3d = np.asarray(points_3d, dtype=np.float64)
                projected1, depth1 = _project_points(points_3d, k1, np.eye(3), np.zeros(3))
                projected2, depth2 = _project_points(points_3d, k2, rotation, translation)
                errors = np.sqrt(
                    np.sum((projected1 - p1) ** 2, axis=1)
                    + np.sum((projected2 - p2) ** 2, axis=1)
                ) * 0.5
                finite = np.isfinite(errors) & np.isfinite(points_3d).all(axis=1)
                positive = np.asarray(cheirality_mask, dtype=bool) & (depth1 > 0.0) & (depth2 > 0.0)
                inliers = finite & positive & (errors <= cfg.reprojection_threshold_px)
                inlier_count = int(np.count_nonzero(inliers))
                if inlier_count == 0:
                    median_error = float("inf")
                else:
                    median_error = float(np.median(errors[inliers]))
                candidates.append(
                    (
                        np.asarray(essential, dtype=np.float64),
                        rotation,
                        translation,
                        points_3d,
                        inliers,
                        median_error,
                        inlier_count,
                        "five_point",
                        triangulation_method,
                        fallback_count,
                        int(np.count_nonzero(positive)),
                    )
                )

        # A minimal five-point sample can be unlucky even when the complete
        # correspondence set has a strong geometric consensus.  Reuse the
        # existing all-point VSAC/Fundamental implementation as a bounded
        # fallback, convert F -> E with the calibrated intrinsics, and run the
        # exact same cheirality/reprojection gates before accepting it.
        best_count = max((item[6] for item in candidates), default=0)
        # A candidate can have enough reprojection inliers for the generic
        # ratio gate while still failing the stricter positive-depth gate
        # used by the final result.  In that case the all-point VSAC path is
        # still required; otherwise an unlucky minimal sample becomes the
        # selected pose and no robust recovery is attempted.
        best_ratio = best_count / max(len(p1), 1)
        if (
            best_count < int(cfg.min_inlier_count)
            or best_ratio < float(cfg.min_inlier_ratio)
            or best_ratio < float(cfg.min_cheirality_ratio)
            # A complete, clean correspondence set deserves the all-point
            # consensus check even when an unlucky minimal sample already
            # clears the coarse ratio gates.  VSAC is bounded by the matcher
            # count and remains a fallback when its target backend is absent.
            or best_count < len(p1)
        ):
            try:
                fundamental, fundamental_mask, _ = vsac_fundamental(
                    p1.astype(np.float32),
                    p2.astype(np.float32),
                    threshold=float(cfg.reprojection_threshold_px),
                    n_hypotheses=min(1024, max(64, len(p1) * 2)),
                )
                fundamental_mask = np.asarray(fundamental_mask, dtype=bool).reshape(-1)
                if fundamental_mask.shape[0] == len(p1) and int(np.count_nonzero(fundamental_mask)) >= 5:
                    essential = enforce_essential_np(k2.T @ np.asarray(fundamental, dtype=np.float64) @ k1)
                    sample_pool = np.flatnonzero(fundamental_mask).astype(np.int32)
                    sample_indices = sample_pool[:5]
                    valid_pose, rotation, translation = check_cheirality_minimal(
                        essential, k1, k2, p1[sample_indices], p2[sample_indices]
                    )
                    if valid_pose and rotation is not None and translation is not None:
                        rotation = np.asarray(rotation, dtype=np.float64)
                        translation = np.asarray(translation, dtype=np.float64).reshape(3)
                        P2 = _projection_matrix(rotation, translation)
                        _, cheirality_mask = check_cheirality_full(
                            rotation, translation, k1, k2, p1, p2
                        )
                        points_3d, triangulation_method, fallback_count = _triangulate_checked(
                            p1,
                            p2,
                            q1_all,
                            q2_all,
                            k1,
                            k2,
                            P1,
                            P2,
                            rotation,
                            translation,
                            cfg.parallax_threshold_deg,
                            cfg.noise_sigma,
                        )
                        projected1, depth1 = _project_points(
                            points_3d, k1, np.eye(3), np.zeros(3)
                        )
                        projected2, depth2 = _project_points(
                            points_3d, k2, rotation, translation
                        )
                        errors = 0.5 * np.sqrt(
                            np.sum((projected1 - p1) ** 2, axis=1)
                            + np.sum((projected2 - p2) ** 2, axis=1)
                        )
                        finite = np.isfinite(errors) & np.isfinite(points_3d).all(axis=1)
                        positive = np.asarray(cheirality_mask, dtype=bool) & (depth1 > 0.0) & (depth2 > 0.0)
                        inliers = fundamental_mask & finite & positive & (
                            errors <= cfg.reprojection_threshold_px
                        )
                        inlier_count = int(np.count_nonzero(inliers))
                        median_error = float(np.median(errors[inliers])) if inlier_count else float("inf")
                        candidates.append(
                            (
                                np.asarray(essential, dtype=np.float64),
                                rotation,
                                translation,
                                np.asarray(points_3d, dtype=np.float64),
                                inliers,
                                median_error,
                                inlier_count,
                                "vsac_fundamental",
                                triangulation_method,
                                fallback_count,
                                int(np.count_nonzero(positive)),
                            )
                        )
            except Exception:
                # VSAC is a fallback quality path; an unavailable optional
                # backend leaves the already evaluated minimal hypotheses
                # intact and fail-closed below.
                pass

        # Native VSAC implementations can be conservative on a perfectly
        # consistent, low-noise set (for example, a graphics backend may
        # retain only a subset of a planar-looking consensus).  Evaluate one
        # deterministic all-point normalized eight-point candidate as a
        # numerical oracle.  It is still selected only through the ordinary
        # cheirality/reprojection gates below; no mask is promoted blindly.
        try:
            essential = _estimate_all_point_essential(q1_all, q2_all)
            if essential is not None:
                sample_indices = _spread_sample_indices(p1, seed=cfg.sample_seed)
                valid_pose, rotation, translation = check_cheirality_minimal(
                    essential, k1, k2, p1[sample_indices], p2[sample_indices]
                )
                if valid_pose and rotation is not None and translation is not None:
                    rotation = np.asarray(rotation, dtype=np.float64)
                    translation = np.asarray(translation, dtype=np.float64).reshape(3)
                    P2 = _projection_matrix(rotation, translation)
                    _, cheirality_mask = check_cheirality_full(
                        rotation, translation, k1, k2, p1, p2
                    )
                    points_3d, triangulation_method, fallback_count = _triangulate_checked(
                        p1,
                        p2,
                        q1_all,
                        q2_all,
                        k1,
                        k2,
                        P1,
                        P2,
                        rotation,
                        translation,
                        cfg.parallax_threshold_deg,
                        cfg.noise_sigma,
                    )
                    projected1, depth1 = _project_points(
                        points_3d, k1, np.eye(3), np.zeros(3)
                    )
                    projected2, depth2 = _project_points(
                        points_3d, k2, rotation, translation
                    )
                    errors = 0.5 * np.sqrt(
                        np.sum((projected1 - p1) ** 2, axis=1)
                        + np.sum((projected2 - p2) ** 2, axis=1)
                    )
                    finite = np.isfinite(errors) & np.isfinite(points_3d).all(axis=1)
                    positive = np.asarray(cheirality_mask, dtype=bool) & (depth1 > 0.0) & (depth2 > 0.0)
                    inliers = finite & positive & (errors <= cfg.reprojection_threshold_px)
                    inlier_count = int(np.count_nonzero(inliers))
                    median_error = float(np.median(errors[inliers])) if inlier_count else float("inf")
                    candidates.append(
                        (
                            np.asarray(essential, dtype=np.float64),
                            rotation,
                            translation,
                            np.asarray(points_3d, dtype=np.float64),
                            inliers,
                            median_error,
                            inlier_count,
                            "eight_point_all",
                            triangulation_method,
                            fallback_count,
                            int(np.count_nonzero(positive)),
                        )
                    )
        except Exception:
            # The all-point oracle is deliberately optional; minimal hypotheses
            # remain the authoritative path when a degenerate set is supplied.
            pass

    if not candidates:
        return _failure_pair_result(report, "no essential-matrix hypothesis passed cheirality")

    # Maximize consensus, then use the median reprojection error as a stable
    # tie-breaker.  This avoids accepting a numerically perfect tiny subset.
    selected = max(candidates, key=lambda item: (item[6], -item[5]))
    (
        essential,
        rotation,
        translation,
        points_3d_all,
        inlier_mask,
        median_error,
        inlier_count,
        pose_method,
        triangulation_method,
        fallback_count,
        positive_count,
    ) = selected
    cheirality_count = int(positive_count)
    ratio = inlier_count / max(len(p1), 1)
    if inlier_count < int(cfg.min_inlier_count) or ratio < float(cfg.min_inlier_ratio):
        report.metrics.update(
            {
                "n_inliers": float(inlier_count),
                "inlier_ratio": float(ratio),
            }
        )
        return _failure_pair_result(report, "reprojection consensus did not meet SfM quality gates")

    inlier_indices = np.flatnonzero(inlier_mask).astype(np.int32)
    points_3d = points_3d_all[inlier_mask].astype(np.float32)
    p1_in = p1[inlier_mask]
    p2_in = p2[inlier_mask]
    proj1, _ = _project_points(points_3d, k1, np.eye(3), np.zeros(3))
    proj2, _ = _project_points(points_3d, k2, rotation, translation)
    errors = (
        0.5
        * np.sqrt(np.sum((proj1 - p1_in) ** 2, axis=1) + np.sum((proj2 - p2_in) ** 2, axis=1))
    ).astype(np.float32)
    parallax = _parallax_for_points(points_3d.astype(np.float64), rotation, translation)

    # Confidence combines geometric residual and parallax.  It is deliberately
    # bounded in [0,1] and is a gate/weight, not an accuracy claim.
    residual_conf = np.exp(
        -0.5 * (errors.astype(np.float64) / max(cfg.reprojection_threshold_px, 1e-6)) ** 2
    )
    parallax_conf = np.clip(
        parallax.astype(np.float64) / max(float(cfg.parallax_threshold_deg), 1e-6),
        0.0,
        1.0,
    )
    confidence = (residual_conf * parallax_conf).astype(np.float32)
    finite = np.isfinite(confidence) & np.isfinite(errors) & np.isfinite(parallax)
    confidence[~finite] = 0.0

    report.metrics.update(
        {
            "n_inliers": float(inlier_count),
            "inlier_ratio": float(ratio),
            "median_reprojection_error_px": float(np.median(errors)) if len(errors) else float("inf"),
            "mean_parallax_deg": float(np.mean(parallax)) if len(parallax) else 0.0,
            "cheirality_ratio": float(cheirality_count / max(len(p1), 1)),
            "confidence_mean": float(np.mean(confidence)) if len(confidence) else 0.0,
            "triangulation_fallback_count": float(fallback_count),
        }
    )
    report.warnings.append(f"triangulation_method={triangulation_method}")
    report.warnings.append(f"pose_method={pose_method}")
    if report.metrics["cheirality_ratio"] < float(cfg.min_cheirality_ratio):
        return _failure_pair_result(report, "positive-depth ratio did not meet the SfM quality gate")

    return PairwiseSfMResult(
        success=True,
        essential=essential.astype(np.float64),
        rotation=rotation.astype(np.float64),
        translation=translation.astype(np.float64),
        points_3d=points_3d,
        inlier_indices=inlier_indices,
        inlier_mask=inlier_mask.astype(bool),
        reprojection_error_px=errors,
        parallax_deg=parallax,
        confidence=confidence,
        report=report,
    )


def _validate_mvs_inputs(
    ref_img: Any,
    target_images: Sequence[Any],
    K_ref: Any,
    K_targets: Sequence[Any],
    R_rels: Sequence[Any],
    t_rels: Sequence[Any],
) -> tuple[np.ndarray, list[np.ndarray], np.ndarray, list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    if not target_images:
        raise ValueError("target_images must contain at least one image")
    if not (len(target_images) == len(K_targets) == len(R_rels) == len(t_rels)):
        raise ValueError("target image and pose lists must have equal lengths")
    reference = as_gray_float32(ref_img, name="ref_img")
    targets = [as_gray_float32(image, name=f"target_images[{i}]") for i, image in enumerate(target_images)]
    if any(image.shape != reference.shape for image in targets):
        raise ValueError("all target images must match ref_img spatial shape")
    k_ref = _as_intrinsics(K_ref, name="K_ref")
    k_targets = [_as_intrinsics(value, name=f"K_targets[{i}]") for i, value in enumerate(K_targets)]
    rotations = [np.asarray(as_float32_matrix(value, (3, 3), name=f"R_rels[{i}]") , dtype=np.float64) for i, value in enumerate(R_rels)]
    translations: list[np.ndarray] = []
    for i, value in enumerate(t_rels):
        translation = np.ascontiguousarray(value, dtype=np.float64).reshape(-1)
        if translation.shape != (3,) or not np.isfinite(translation).all():
            raise ValueError(f"t_rels[{i}] must be finite shape (3,)")
        translations.append(translation)
    if any(
        not np.isfinite(rotation).all()
        or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-3)
        or np.linalg.det(rotation) <= 0.0
        for rotation in rotations
    ):
        raise ValueError("R_rels must contain finite proper SO(3) rotations")
    return reference, targets, k_ref, k_targets, rotations, translations


def run_plane_sweep_mvs(
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
) -> MVSResult:
    """Run single-/multi-view plane sweep with an allocation quality gate."""

    if not (np.isfinite(depth_min) and np.isfinite(depth_max)) or depth_min <= 0 or depth_max <= depth_min:
        raise ValueError("depth range must satisfy 0 < depth_min < depth_max")
    if int(n_depths) < 2 or int(n_depths) > 4096:
        raise ValueError("n_depths must be in [2, 4096]")
    if int(patch_radius) < 0 or int(patch_radius) > 32:
        raise ValueError("patch_radius must be in [0, 32]")
    if depth_spacing not in {"linear", "log"}:
        raise ValueError("depth_spacing must be 'linear' or 'log'")
    backend_name = str(backend).strip().lower()
    if backend_name not in {"auto", "numpy", "taichi", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', 'taichi', or 'aot'")
    if int(max_volume_bytes) <= 0:
        raise ValueError("max_volume_bytes must be positive")

    reference, targets, k_ref, k_targets, rotations, translations = _validate_mvs_inputs(
        ref_img, target_images, K_ref, K_targets, R_rels, t_rels
    )
    h, w = reference.shape
    # plane_sweep allocates one total cost volume and one working volume.  A
    # conservative 2x float32 estimate prevents an accidental 50 MP request
    # from exhausting host/device memory before the low-level routine starts.
    estimated_bytes = int(n_depths) * int(h) * int(w) * np.dtype(np.float32).itemsize * 2
    if estimated_bytes > int(max_volume_bytes):
        raise MemoryError(
            f"plane-sweep volume requires about {estimated_bytes} bytes, "
            f"limit is {int(max_volume_bytes)}"
        )

    report = PipelineReport("mvs_plane_sweep", backend=f"plane-sweep-{backend_name}")
    report.metrics.update(
        {
            "height": float(h),
            "width": float(w),
            "n_views": float(len(targets)),
            "n_depths": float(n_depths),
            "estimated_volume_bytes": float(estimated_bytes),
        }
    )
    stage_index = len(report.stages)
    with timed_stage(report, "plane_sweep"):
        if len(targets) == 1:
            depth, confidence = plane_sweep_stereo(
                reference,
                targets[0],
                k_ref.astype(np.float32),
                k_targets[0].astype(np.float32),
                rotations[0].astype(np.float32),
                translations[0].astype(np.float32),
                depth_min=float(depth_min),
                depth_max=float(depth_max),
                n_depths=int(n_depths),
                patch_radius=int(patch_radius),
                depth_spacing=depth_spacing,
                backend=backend_name,
            )
        else:
            depth, confidence = multi_view_plane_sweep(
                reference,
                targets,
                k_ref.astype(np.float32),
                [value.astype(np.float32) for value in k_targets],
                [value.astype(np.float32) for value in rotations],
                [value.astype(np.float32) for value in translations],
                depth_min=float(depth_min),
                depth_max=float(depth_max),
                n_depths=int(n_depths),
                patch_radius=int(patch_radius),
                backend=backend_name,
            )
    depth = np.ascontiguousarray(depth, dtype=np.float32)
    confidence = np.ascontiguousarray(confidence, dtype=np.float32)
    if depth.shape != reference.shape or confidence.shape != reference.shape:
        report.success = False
        report.add_warning("plane-sweep returned an unexpected depth/confidence shape")
        raise RuntimeError(report.warnings[-1])
    if not np.isfinite(depth).all() or not np.isfinite(confidence).all():
        report.success = False
        report.add_warning("plane-sweep returned non-finite depth/confidence values")
        raise RuntimeError(report.warnings[-1])
    update_stage_output(report, stage_index, depth)
    report.metrics.update(
        {
            "depth_valid_fraction": float(np.mean(depth > 0.0)),
            "confidence_mean": float(np.mean(confidence)) if confidence.size else 0.0,
            "confidence_finite_fraction": finite_fraction(confidence),
        }
    )
    return MVSResult(depth=depth, confidence=confidence, report=report)


def run_point_cloud_pipeline(
    points: Any,
    *,
    voxel_size: float = 0.01,
    sor_k: int = 20,
    sor_std: float = 2.0,
    build_surface: bool = False,
    grid_resolution: int = 64,
    solver_iterations: int = 50,
    iso_threshold: float = 0.5,
    dilate_radius: int = 2,
    max_grid_voxels: int = 256 ** 3,
    max_points: int = 5_000_000,
    backend: str = "auto",
) -> PointCloudResult:
    """Filter a cloud, estimate normals, and optionally run Poisson meshing.

    The guard is intentionally before ``poisson_reconstruct``: its grid is
    dense by design and therefore must never be allowed to grow implicitly
    from a 50 MP depth map.
    """

    backend_name = str(backend).strip().lower()
    if backend_name not in {"auto", "numpy", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', or 'aot'")
    # Preserve the historical auto path (the reference orchestration) while
    # making AOT an explicit, fail-closed choice.  No AOT artifact is silently
    # substituted with NumPy when the caller requests backend='aot'.
    effective_backend = "numpy" if backend_name == "auto" else backend_name
    cloud = np.ascontiguousarray(points, dtype=np.float32)
    if cloud.ndim != 2 or cloud.shape[1] != 3:
        raise ValueError(f"points must have shape (N, 3), got {cloud.shape}")
    if not np.isfinite(cloud).all():
        raise ValueError("points contains non-finite values")
    if float(voxel_size) <= 0 or not np.isfinite(voxel_size):
        raise ValueError("voxel_size must be positive")
    if int(sor_k) < 1 or float(sor_std) < 0:
        raise ValueError("invalid SOR parameters")
    if int(grid_resolution) < 4 or int(grid_resolution) > 1024:
        raise ValueError("grid_resolution must be in [4, 1024]")
    if int(solver_iterations) < 1:
        raise ValueError("solver_iterations must be positive")
    if int(max_grid_voxels) < 1:
        raise ValueError("max_grid_voxels must be positive")
    if int(max_points) < 1:
        raise ValueError("max_points must be positive")
    if len(cloud) > int(max_points):
        raise MemoryError(
            f"point-cloud input has {len(cloud)} points, limit is {int(max_points)}"
        )

    report = PipelineReport("point_cloud", backend=f"point-cloud-{backend_name}")
    report.metrics["n_input_points"] = float(len(cloud))
    if len(cloud) == 0:
        report.add_warning("empty point cloud")
        return PointCloudResult(
            points=cloud.copy(),
            normals=np.empty((0, 3), dtype=np.float32),
            source_keep_indices=np.empty(0, dtype=np.int32),
            report=report,
        )

    stage_index = len(report.stages)
    with timed_stage(report, "point_cloud_preprocess"):
        if effective_backend == "aot":
            try:
                from ..aot_api.research_pipeline import point_cloud_preprocess_aot

                filtered, normals, keep_indices = point_cloud_preprocess_aot(
                    cloud,
                    voxel_size=float(voxel_size),
                    sor_k=int(sor_k),
                    sor_std=float(sor_std),
                    normal_k=min(20, max(1, len(cloud) - 1)),
                )
            except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                raise NotImplementedError(
                    "point-cloud AOT requires target-qualified sfm_point_cloud artifacts; "
                    "use backend='numpy' explicitly"
                ) from exc
        else:
            filtered, normals, keep_indices = preprocess_point_cloud(
                cloud,
                voxel_size=float(voxel_size),
                sor_k=int(sor_k),
                sor_std=float(sor_std),
                backend="numpy",
            )
    filtered = np.ascontiguousarray(filtered, dtype=np.float32)
    normals = np.ascontiguousarray(normals, dtype=np.float32)
    keep_indices = np.ascontiguousarray(keep_indices, dtype=np.int32)
    if filtered.shape != normals.shape:
        raise RuntimeError("point-cloud preprocessing returned mismatched points/normals")
    if not np.isfinite(filtered).all() or (normals.size and not np.isfinite(normals).all()):
        raise RuntimeError("point-cloud preprocessing returned non-finite values")
    update_stage_output(report, stage_index, filtered)
    report.metrics.update(
        {
            "n_output_points": float(len(filtered)),
            "retained_fraction": float(len(filtered) / max(len(cloud), 1)),
        }
    )

    vertices = _EMPTY_POINTS.copy()
    faces = _EMPTY_FACES.copy()
    if build_surface and len(filtered):
        estimated_grid = int(grid_resolution) ** 3
        if estimated_grid > int(max_grid_voxels):
            raise MemoryError(
                f"Poisson grid has {estimated_grid} voxels, limit is {int(max_grid_voxels)}"
            )
        stage_index = len(report.stages)
        with timed_stage(report, "poisson_surface"):
            if effective_backend == "aot":
                try:
                    from ..aot_api.research_pipeline import poisson_reconstruct_aot

                    vertices, faces = poisson_reconstruct_aot(
                        filtered,
                        normals,
                        grid_resolution=int(grid_resolution),
                        solver_iterations=int(solver_iterations),
                        iso_threshold=float(iso_threshold),
                        dilate_radius=int(dilate_radius),
                    )
                except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                    raise NotImplementedError(
                        "Poisson AOT requires target-qualified sfm_poisson artifacts; "
                        "use backend='numpy' explicitly"
                    ) from exc
            else:
                vertices, faces = poisson_reconstruct(
                    filtered,
                    normals,
                    grid_resolution=int(grid_resolution),
                    solver_iterations=int(solver_iterations),
                    iso_threshold=float(iso_threshold),
                    dilate_radius=int(dilate_radius),
                )
        vertices = np.ascontiguousarray(vertices, dtype=np.float32)
        faces = np.ascontiguousarray(faces, dtype=np.int32)
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise RuntimeError("Poisson returned invalid vertices")
        if faces.ndim != 2 or faces.shape[1] != 3:
            raise RuntimeError("Poisson returned invalid faces")
        update_stage_output(report, stage_index, vertices)
        report.metrics.update(
            {"n_vertices": float(len(vertices)), "n_faces": float(len(faces))}
        )

    return PointCloudResult(
        points=filtered,
        normals=normals,
        source_keep_indices=keep_indices,
        vertices=vertices,
        faces=faces,
        report=report,
    )


def run_sgm_mvs(*args: Any, **kwargs: Any) -> MVSResult:
    """Compatibility wrapper for bounded SGM regularisation of plane sweep.

    The implementation lives in :mod:`sfm.mvs_regularization` so the legacy
    plane-sweep source remains the single owner of its cost/winner/refinement
    leaves.  Importing lazily avoids a module cycle during family discovery.
    """

    from .mvs_regularization import run_sgm_mvs as _run_sgm_mvs

    return _run_sgm_mvs(*args, **kwargs)


def run_patchmatch_mvs(*args: Any, **kwargs: Any) -> MVSResult:
    """Compatibility wrapper for bounded PatchMatch-style MVS."""

    from .mvs_regularization import run_patchmatch_mvs as _run_patchmatch_mvs

    return _run_patchmatch_mvs(*args, **kwargs)


def reconstruct_sequence(
    pair_correspondences: Sequence[tuple[Any, Any]],
    intrinsics: Sequence[Any],
    *,
    config: PairwiseSfMConfig | None = None,
    max_pairs: int = 256,
) -> SequenceSfMResult:
    """Chain bounded pairwise SfM poses over a calibrated image sequence.

    ``pair_correspondences[i]`` contains the reference/moving image-keypoint
    coordinates for frames ``i`` and ``i+1``.  Each pair is quality-gated by
    :func:`reconstruct_pair`; a failed pair stops the chain and returns
    ``success=False`` with the trusted prefix only.  The translation scale is
    the normalized scale returned by the calibrated essential estimate, so a
    metric scale must be supplied by the caller later (for example from a
    known baseline or depth sensor).
    """

    pairs = list(pair_correspondences)
    if not pairs:
        raise ValueError("pair_correspondences must contain at least one pair")
    if int(max_pairs) < 1 or len(pairs) > int(max_pairs):
        raise ValueError(f"pair_correspondences length must be in [1, {int(max_pairs)}]")
    cameras = list(intrinsics)
    if len(cameras) != len(pairs) + 1:
        raise ValueError("intrinsics must contain one matrix per sequence frame")
    # Validate all intrinsics before running a potentially expensive first
    # hypothesis, keeping malformed sequence input fail-closed.
    matrices = [_as_intrinsics(value, name=f"intrinsics[{index}]") for index, value in enumerate(cameras)]
    report = PipelineReport("sfm_sequence")
    poses: list[np.ndarray] = [np.eye(4, dtype=np.float64)]
    results: list[PairwiseSfMResult] = []
    for index, correspondence in enumerate(pairs):
        if not isinstance(correspondence, (tuple, list)) or len(correspondence) != 2:
            raise ValueError(f"pair_correspondences[{index}] must be (points_i, points_i+1)")
        with timed_stage(report, f"pair_{index}"):
            result = reconstruct_pair(
                correspondence[0],
                correspondence[1],
                matrices[index],
                matrices[index + 1],
                config=config,
            )
        results.append(result)
        report.warnings.extend(f"pair_{index}: {warning}" for warning in result.report.warnings)
        if not result.success or result.rotation is None or result.translation is None:
            report.success = False
            report.add_warning(f"sequence stopped at pair {index}: quality gate failed")
            break
        relative = np.eye(4, dtype=np.float64)
        relative[:3, :3] = np.asarray(result.rotation, dtype=np.float64)
        relative[:3, 3] = np.asarray(result.translation, dtype=np.float64).reshape(3)
        poses.append(relative @ poses[-1])
    report.metrics.update(
        {
            "requested_pairs": float(len(pairs)),
            "trusted_pairs": float(len(results)),
            "trusted_frames": float(len(poses)),
        }
    )
    success = bool(report.success and len(results) == len(pairs))
    report.success = success
    return SequenceSfMResult(
        success=success,
        poses_world_to_camera=[np.ascontiguousarray(pose) for pose in poses],
        pair_results=results,
        report=report,
    )


__all__ = [
    "PairwiseSfMConfig",
    "PairwiseSfMResult",
    "MVSResult",
    "PointCloudResult",
    "SequenceSfMResult",
    "reconstruct_pair",
    "reconstruct_sequence",
    "run_plane_sweep_mvs",
    "run_sgm_mvs",
    "run_patchmatch_mvs",
    "run_point_cloud_pipeline",
]
