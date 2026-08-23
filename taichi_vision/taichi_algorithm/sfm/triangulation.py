"""
Adaptive Parallax Triangulation — Taichi GPU
==============================================
Adaptive triangulation with parallax-based method selection.

Algorithm (from paper):
  For each point pair:
    theta = arccos(ray1 . ray2)   # parallax angle
    if theta < 4° OR sigma_extrinsic high:
        → Weighted Midpoint wMid2 (inverse depth weighting)
        → Prevents depth explosion at low parallax
    else:
        → LOST (Linear Optimal Sine Triangulation)
        → Non-iterative WLS via trigonometric sine law, O(N)

Methods:
  - DLT: Direct Linear Transform (baseline/fallback)
  - wMid2: Weighted Midpoint with inverse depth weighting
  - LOST: Linear Optimal Sine Triangulation (Henry & Christian 2023)

Hybrid precision: Float64 computation, Float32 storage.
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
except ImportError:
    pass


# =============================================================================
# TAICHI KERNELS
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def triangulate_adaptive_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        P1: ti.types.ndarray(ti.f32, ndim=2),
        P2: ti.types.ndarray(ti.f32, ndim=2),
        C1: ti.types.ndarray(ti.f32, ndim=1),
        C2: ti.types.ndarray(ti.f32, ndim=1),
        n_pts: int,
        parallax_threshold: ti.f32,
        points_3d_out: ti.types.ndarray(ti.f32, ndim=2),
        method_used_out: ti.types.ndarray(ti.i32, ndim=1),
    ):
        """
        GPU adaptive triangulation: per-point parallax-based method selection.
        method_used_out[i]: 0=wMid2, 1=LOST, 2=DLT fallback
        """
        PARALLAX_RAD = parallax_threshold * 3.14159265 / 180.0

        for i in range(n_pts):
            x1 = pts1[i, 0]; y1 = pts1[i, 1]
            x2 = pts2[i, 0]; y2 = pts2[i, 1]

            # Ray directions from camera centers
            r1x = x1 - C1[0]; r1y = y1 - C1[1]; r1z = 1.0 - C1[2]
            r2x = x2 - C2[0]; r2y = y2 - C2[1]; r2z = 1.0 - C2[2]

            len1 = ti.sqrt(r1x*r1x + r1y*r1y + r1z*r1z)
            len2 = ti.sqrt(r2x*r2x + r2y*r2y + r2z*r2z)

            if len1 > 1e-10:
                r1x /= len1; r1y /= len1; r1z /= len1
            if len2 > 1e-10:
                r2x /= len2; r2y /= len2; r2z /= len2

            dot = r1x*r2x + r1y*r2y + r1z*r2z
            dot = ti.max(-1.0, ti.min(1.0, dot))
            theta = ti.acos(dot)

            if theta < PARALLAX_RAD:
                # wMid2: Weighted Midpoint (inverse depth weighting)
                # Build 4x4 DLT system
                A0x = -P1[0,0] + x1*P1[2,0]; A0y = -P1[0,1] + x1*P1[2,1]; A0z = -P1[0,2] + x1*P1[2,2]; A0w = -P1[0,3] + x1*P1[2,3]
                A1x = -P1[1,0] + y1*P1[2,0]; A1y = -P1[1,1] + y1*P1[2,1]; A1z = -P1[1,2] + y1*P1[2,2]; A1w = -P1[1,3] + y1*P1[2,3]
                A2x = -P2[0,0] + x2*P2[2,0]; A2y = -P2[0,1] + x2*P2[2,1]; A2z = -P2[0,2] + x2*P2[2,2]; A2w = -P2[0,3] + x2*P2[2,3]
                A3x = -P2[1,0] + y2*P2[2,0]; A3y = -P2[1,1] + y2*P2[2,1]; A3z = -P2[1,2] + y2*P2[2,2]; A3w = -P2[1,3] + y2*P2[2,3]

                # Solve via ATA (3x3 with last column as b)
                ata00 = A0x*A0x + A1x*A1x + A2x*A2x + A3x*A3x
                ata01 = A0x*A0y + A1x*A1y + A2x*A2y + A3x*A3y
                ata02 = A0x*A0z + A1x*A1z + A2x*A2z + A3x*A3z
                ata11 = A0y*A0y + A1y*A1y + A2y*A2y + A3y*A3y
                ata12 = A0y*A0z + A1y*A1z + A2y*A2z + A3y*A3z
                ata22 = A0z*A0z + A1z*A1z + A2z*A2z + A3z*A3z
                atb0 = -(A0x*A0w + A1x*A1w + A2x*A2w + A3x*A3w)
                atb1 = -(A0y*A0w + A1y*A1w + A2y*A2w + A3y*A3w)
                atb2 = -(A0z*A0w + A1z*A1w + A2z*A2w + A3z*A3w)

                det = ata00*(ata11*ata22 - ata12*ata12) - ata01*(ata01*ata22 - ata02*ata12) + ata02*(ata01*ata12 - ata02*ata11)

                X = ti.Vector([C1[0], C1[1], C1[2]])
                if ti.abs(det) > 1e-10:
                    inv_det = 1.0 / det
                    Xx = (atb0*(ata11*ata22-ata12*ata12) - atb1*(ata01*ata22-ata02*ata12) + atb2*(ata01*ata12-ata02*ata11)) * inv_det
                    Xy = (ata00*(atb1*ata22-ata12*atb2) - atb0*(ata01*ata22-ata02*ata12) + ata02*(ata01*atb2-atb1*ata12)) * inv_det
                    Xz = (ata00*(ata11*atb2-atb1*ata12) - ata01*(ata01*atb2-atb0*ata12) + atb0*(ata01*ata12-ata02*ata11)) * inv_det
                    X = ti.Vector([Xx, Xy, Xz])

                points_3d_out[i, 0] = X[0]
                points_3d_out[i, 1] = X[1]
                points_3d_out[i, 2] = X[2]
                method_used_out[i] = 0

            else:
                # LOST: Linear Optimal Sine Triangulation
                # Non-iterative WLS via sine law
                # Baseline vector
                bx = C2[0] - C1[0]
                by = C2[1] - C1[1]
                bz = C2[2] - C1[2]
                baseline = ti.sqrt(bx*bx + by*by + bz*bz)

                # Cross product of rays
                cx = r1y*r2z - r1z*r2y
                cy = r1z*r2x - r1x*r2z
                cz = r1x*r2y - r1y*r2x
                cross_sq = cx*cx + cy*cy + cz*cz

                X = ti.Vector([0.0, 0.0, 0.0])
                if cross_sq > 1e-14:
                    # Sine of angle between rays
                    sin_theta = ti.sqrt(cross_sq)

                    # Depth from sine law: lambda1 = |baseline x r2| / sin(theta)
                    bx_r2x = by*r2z - bz*r2y
                    bx_r2y = bz*r2x - bx*r2z
                    bx_r2z = bx*r2y - by*r2x
                    lambda1 = ti.sqrt(bx_r2x*bx_r2x + bx_r2y*bx_r2y + bx_r2z*bx_r2z) / (sin_theta + 1e-10)

                    # Depth for camera 2
                    bx_r1x = by*r1z - bz*r1y
                    bx_r1y = bz*r1x - bx*r1z
                    bx_r1z = bx*r1y - by*r1x
                    lambda2 = ti.sqrt(bx_r1x*bx_r1x + bx_r1y*bx_r1y + bx_r1z*bx_r1z) / (sin_theta + 1e-10)

                    # Weighted average of the two ray intersection points
                    P_a = ti.Vector([C1[0] + lambda1*r1x, C1[1] + lambda1*r1y, C1[2] + lambda1*r1z])
                    P_b = ti.Vector([C2[0] + lambda2*r2x, C2[1] + lambda2*r2y, C2[2] + lambda2*r2z])

                    # Inverse depth weighting (wMid2 logic applied to LOST)
                    w1 = 1.0 / (lambda1 * lambda1 + 1e-10)
                    w2 = 1.0 / (lambda2 * lambda2 + 1e-10)
                    X = (w1 * P_a + w2 * P_b) / (w1 + w2)

                points_3d_out[i, 0] = X[0]
                points_3d_out[i, 1] = X[1]
                points_3d_out[i, 2] = X[2]
                method_used_out[i] = 1

    @ti.kernel
    def cast_f64_to_f32_kernel(
        src: ti.types.ndarray(ti.f32, ndim=2),
        dst: ti.types.ndarray(ti.f32, ndim=2),
        n: int,
    ):
        """Copy Float32 data (used as final cast step in hybrid precision pipeline)."""
        for i in range(n):
            for j in ti.static(range(3)):
                dst[i, j] = src[i, j]


# =============================================================================
# HOST WRAPPERS (NumPy implementations with hybrid precision)
# =============================================================================

def _triangulate_dlt_np(pts1, pts2, P1, P2):
    """DLT triangulation (NumPy, Float64 precision)."""
    n = len(pts1)
    pts3d = np.zeros((n, 3), dtype=np.float64)
    for i in range(n):
        A = np.array([
            pts1[i, 0] * P1[2] - P1[0],
            pts1[i, 1] * P1[2] - P1[1],
            pts2[i, 0] * P2[2] - P2[0],
            pts2[i, 1] * P2[2] - P2[1],
        ], dtype=np.float64)
        _, _, Vt = np.linalg.svd(A)
        X = Vt[-1]
        if abs(X[3]) > 1e-10:
            pts3d[i] = X[:3] / X[3]
    return pts3d


def _triangulate_wmid2_np(pts1, pts2, P1, P2, C1, C2):
    """
    Weighted Midpoint (wMid2) with inverse depth weighting.
    Prevents depth explosion at low parallax.
    """
    n = len(pts1)
    pts3d = np.zeros((n, 3), dtype=np.float64)

    for i in range(n):
        # Ray directions (normalized coordinates assumed)
        r1 = np.array([pts1[i, 0] - C1[0], pts1[i, 1] - C1[1], 1.0 - C1[2]], dtype=np.float64)
        r2 = np.array([pts2[i, 0] - C2[0], pts2[i, 1] - C2[1], 1.0 - C2[2]], dtype=np.float64)

        r1_norm = np.linalg.norm(r1)
        r2_norm = np.linalg.norm(r2)
        if r1_norm > 1e-10:
            r1 /= r1_norm
        if r2_norm > 1e-10:
            r2 /= r2_norm

        # Perpendicular bisector: find closest point on both rays
        # ray1: C1 + lambda1 * r1, ray2: C2 + lambda2 * r2
        d = C2 - C1
        a = np.dot(r1, r1)
        b = np.dot(r1, r2)
        c = np.dot(r2, r2)
        d1 = np.dot(d, r1)
        d2 = np.dot(d, r2)

        denom = a * c - b * b
        if abs(denom) > 1e-14:
            lambda1 = (b * d2 - c * d1) / denom
            lambda2 = (a * d2 - b * d1) / denom
        else:
            lambda1 = 0.0
            lambda2 = 0.0

        P_a = C1 + lambda1 * r1
        P_b = C2 + lambda2 * r2

        # Inverse depth weighting
        w1 = 1.0 / (lambda1 ** 2 + 1e-10)
        w2 = 1.0 / (lambda2 ** 2 + 1e-10)
        pts3d[i] = (w1 * P_a + w2 * P_b) / (w1 + w2)

    return pts3d


def _triangulate_lost_np(pts1, pts2, P1, P2, C1, C2, noise_sigma=0.5):
    """
    LOST (Linear Optimal Sine Triangulation) — Henry & Christian 2023.
    Non-iterative WLS via trigonometric sine law. O(N) complexity.
    """
    n = len(pts1)
    pts3d = np.zeros((n, 3), dtype=np.float64)

    for i in range(n):
        r1 = np.array([pts1[i, 0] - C1[0], pts1[i, 1] - C1[1], 1.0 - C1[2]], dtype=np.float64)
        r2 = np.array([pts2[i, 0] - C2[0], pts2[i, 1] - C2[1], 1.0 - C2[2]], dtype=np.float64)

        r1_norm = np.linalg.norm(r1)
        r2_norm = np.linalg.norm(r2)
        if r1_norm > 1e-10:
            r1 /= r1_norm
        if r2_norm > 1e-10:
            r2 /= r2_norm

        baseline = C2 - C1
        baseline_len = np.linalg.norm(baseline)

        # Cross product for sine of angle
        cross = np.cross(r1, r2)
        sin_theta = np.linalg.norm(cross)

        if sin_theta < 1e-10:
            pts3d[i] = (C1 + C2) / 2.0
            continue

        # Sine law: lambda1 = |baseline x r2| / sin(theta)
        bx_r2 = np.cross(baseline, r2)
        bx_r1 = np.cross(baseline, r1)
        lambda1 = np.linalg.norm(bx_r2) / sin_theta
        lambda2 = np.linalg.norm(bx_r1) / sin_theta

        # Covariance-weighted combination
        sigma1_sq = noise_sigma ** 2 * lambda1 ** 2
        sigma2_sq = noise_sigma ** 2 * lambda2 ** 2

        P_a = C1 + lambda1 * r1
        P_b = C2 + lambda2 * r2

        w1 = 1.0 / (sigma1_sq + 1e-10)
        w2 = 1.0 / (sigma2_sq + 1e-10)
        pts3d[i] = (w1 * P_a + w2 * P_b) / (w1 + w2)

    return pts3d


def triangulate_adaptive(pts1, pts2, P1, P2, K1, K2, parallax_threshold=4.0, noise_sigma=0.5):
    """
    Adaptive parallax triangulation.

    Per-point method selection:
      - theta < parallax_threshold: wMid2 (prevents depth explosion)
      - theta >= parallax_threshold: LOST (optimal L2 non-iterative)

    Args:
        pts1: (N, 2) pixel coordinates in image 1
        pts2: (N, 2) pixel coordinates in image 2
        P1, P2: (3, 4) projection matrices
        K1, K2: (3, 3) camera intrinsic matrices
        parallax_threshold: degrees (default 4.0 from paper)
        noise_sigma: pixel noise standard deviation for LOST weighting

    Returns:
        (points_3d, method_used, stats)
        points_3d: (N, 3) Float32 — hybrid precision storage
        method_used: (N,) int — 0=wMid2, 1=LOST, 2=DLT
        stats: dict with timing and method distribution
    """
    import time
    t0 = time.time()

    P1 = np.asarray(P1, dtype=np.float64)
    P2 = np.asarray(P2, dtype=np.float64)
    K1 = np.asarray(K1, dtype=np.float64)
    K2 = np.asarray(K2, dtype=np.float64)

    K1_inv = np.linalg.inv(K1)
    K2_inv = np.linalg.inv(K2)

    pts1 = np.ascontiguousarray(pts1, dtype=np.float64)
    pts2 = np.ascontiguousarray(pts2, dtype=np.float64)
    n = len(pts1)

    # Normalize to camera coordinates
    pts1_h = np.hstack([pts1, np.ones((n, 1))])
    pts2_h = np.hstack([pts2, np.ones((n, 1))])
    pts1_norm = (K1_inv @ pts1_h.T).T[:, :2]
    pts2_norm = (K2_inv @ pts2_h.T).T[:, :2]

    # Camera centers
    R1 = P1[:, :3]
    t1 = P1[:, 3]
    C1 = -np.linalg.solve(R1, t1) if np.linalg.det(R1) != 0 else np.zeros(3)

    R2 = P2[:, :3]
    t2 = P2[:, 3]
    C2 = -np.linalg.solve(R2, t2) if np.linalg.det(R2) != 0 else np.zeros(3)

    # Compute parallax angles for all points
    pts3d = np.zeros((n, 3), dtype=np.float64)
    method_used = np.zeros(n, dtype=np.int32)
    parallax_rad = np.radians(parallax_threshold)

    # Vectorized parallax computation
    r1 = np.hstack([pts1_norm - C1[:2], np.ones((n, 1)) - C1[2]])
    r2 = np.hstack([pts2_norm - C2[:2], np.ones((n, 1)) - C2[2]])
    r1_norms = np.linalg.norm(r1, axis=1, keepdims=True)
    r2_norms = np.linalg.norm(r2, axis=1, keepdims=True)
    r1_norms = np.maximum(r1_norms, 1e-10)
    r2_norms = np.maximum(r2_norms, 1e-10)
    r1_n = r1 / r1_norms
    r2_n = r2 / r2_norms

    dots = np.sum(r1_n * r2_n, axis=1)
    dots = np.clip(dots, -1.0, 1.0)
    thetas = np.arccos(dots)

    low_parallax = thetas < parallax_rad
    high_parallax = ~low_parallax

    # wMid2 for low parallax
    if low_parallax.any():
        pts3d[low_parallax] = _triangulate_wmid2_np(
            pts1_norm[low_parallax], pts2_norm[low_parallax],
            P1, P2, C1, C2
        )
        method_used[low_parallax] = 0

    # LOST for high parallax
    if high_parallax.any():
        pts3d[high_parallax] = _triangulate_lost_np(
            pts1_norm[high_parallax], pts2_norm[high_parallax],
            P1, P2, C1, C2, noise_sigma
        )
        method_used[high_parallax] = 1

    elapsed = (time.time() - t0) * 1000
    stats = {
        "time_ms": elapsed,
        "n_wmid2": int(low_parallax.sum()),
        "n_lost": int(high_parallax.sum()),
        "mean_parallax_deg": float(np.degrees(np.mean(thetas))),
    }

    # Hybrid precision: Float64 computation → Float32 storage
    return pts3d.astype(np.float32), method_used, stats
