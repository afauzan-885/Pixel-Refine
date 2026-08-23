"""
Bundle Adjustment — Taichi GPU
================================
GPU-accelerated Levenberg-Marquardt untuk joint optimization
camera poses dan 3D points yang meminimalkan reprojection error.

Algorithm:
  1. Compute reprojection error: e = x_obs - project(R, t, X)
  2. Compute Jacobians J_R, J_t, J_X secara paralel di GPU
  3. Build normal equations: J^T J + λ diag(J^T J) Δ = -J^T e
  4. Schur Complement trick: eliminate 3D points → solve camera block
  5. Update: X_new = X + ΔX, pose_new = pose ⊞ Δpose
  6. Levenberg-Marquardt damping: λ up/down berdasarkan cost reduction

Camera Model:
  - Pinhole: u = fx * X/Z + cx, v = fy * Y/Z + cy
  - Rotation: axis-angle (3 params) → Rodrigues → R (3x3)
  - Translation: 3 params
  - Per-camera: 6 DOF (3 rot + 3 trans)
  - Per-point: 3 DOF (X, Y, Z)

Hybrid precision: Float64 computation (accumulators), Float32 storage.
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

    @ti.func
    def rodrigues_axis_angle(axis: ti.template(), angle: ti.f32):
        """Convert axis-angle rotation to 3x3 rotation matrix.
        Returns R as flat array [9]."""
        kx = axis[0]; ky = axis[1]; kz = axis[2]
        norm = ti.sqrt(kx * kx + ky * ky + kz * kz + 1e-10)
        kx /= norm; ky /= norm; kz /= norm

        c = ti.cos(angle)
        s = ti.sin(angle)
        t = 1.0 - c

        R00 = t * kx * kx + c
        R01 = t * kx * ky - s * kz
        R02 = t * kx * kz + s * ky
        R10 = t * kx * ky + s * kz
        R11 = t * ky * ky + c
        R12 = t * ky * kz - s * kx
        R20 = t * kx * kz - s * ky
        R21 = t * ky * kz + s * kx
        R22 = t * kz * kz + c

        return R00, R01, R02, R10, R11, R12, R20, R21, R22

    @ti.func
    def rodrigues_jacobian(axis: ti.template(), angle: ti.f32):
        """Compute Jacobian dR/d(axis_angle) w.r.t. the 3-axis-angle parameters.
        Returns dR/d_angle as 9x3 matrix (flattened column-major).
        For small angle: dR/dθ ≈ [skew(R * e_i)] for each axis i.
        """
        R00, R01, R02, R10, R11, R12, R20, R21, R22 = rodrigues_axis_angle(axis, angle)

        # dR/dω = skew(e_i) * R for axis i
        # dR/dωx = [[0,0,0],[0,0,-1],[0,1,0]] * R
        dR_dwx = ti.Matrix([
            [0.0, 0.0, 0.0],
            [-R20, -R21, -R22],
            [R10, R11, R12]
        ])
        # dR/dωy = [[0,0,1],[0,0,0],[-1,0,0]] * R
        dR_dwy = ti.Matrix([
            [R20, R21, R22],
            [0.0, 0.0, 0.0],
            [-R00, -R01, -R02]
        ])
        # dR/dωz = [[0,-1,0],[1,0,0],[0,0,0]] * R
        dR_dwz = ti.Matrix([
            [-R10, -R11, -R12],
            [R00, R01, R02],
            [0.0, 0.0, 0.0]
        ])

        return dR_dwx, dR_dwy, dR_dwz, R00, R01, R02, R10, R11, R12, R20, R21, R22

    @ti.kernel
    def compute_reprojection_errors_kernel(
        cameras: ti.types.ndarray(ti.f32, ndim=2),     # (n_cam, 9) [ax,ay,az, angle, tx,ty,tz, fx|cx, fy|cy]
        points_3d: ti.types.ndarray(ti.f32, ndim=2),   # (n_pts, 3)
        observations: ti.types.ndarray(ti.i32, ndim=2), # (n_obs, 2) [cam_idx, pt_idx]
        observed_2d: ti.types.ndarray(ti.f32, ndim=2),  # (n_obs, 2) [u, v]
        errors_out: ti.types.ndarray(ti.f32, ndim=1),   # (n_obs*2,)
        n_obs: int,
    ):
        """Compute reprojection error for each observation.
        Error = observed_2d - project(R*X + t).
        """
        for o in range(n_obs):
            ci = observations[o, 0]
            pi = observations[o, 1]

            # Camera params
            ax = cameras[ci, 0]; ay = cameras[ci, 1]; az = cameras[ci, 2]
            angle = cameras[ci, 3]
            tx = cameras[ci, 4]; ty = cameras[ci, 5]; tz = cameras[ci, 6]
            fx = cameras[ci, 7]; fy = cameras[ci, 8]
            cx_val = cameras[ci, 9] if cameras.shape[1] > 9 else 0.0
            cy_val = cameras[ci, 10] if cameras.shape[1] > 10 else 0.0

            # Normalize axis
            norm = ti.sqrt(ax * ax + ay * ay + az * az + 1e-10)
            kx = ax / norm; ky = ay / norm; kz = az / norm

            # Rodrigues
            R00, R01, R02, R10, R11, R12, R20, R21, R22 = rodrigues_axis_angle(
                ti.Vector([kx, ky, kz]), angle
            )

            # Transform: X_cam = R * X_world + t
            X = points_3d[pi, 0]; Y = points_3d[pi, 1]; Z = points_3d[pi, 2]
            Xc = R00 * X + R01 * Y + R02 * Z + tx
            Yc = R10 * X + R11 * Y + R12 * Z + ty
            Zc = R20 * X + R21 * Y + R22 * Z + tz

            # Project
            if ti.abs(Zc) > 1e-10:
                u_pred = fx * Xc / Zc + cx_val
                v_pred = fy * Yc / Zc + cy_val
                errors_out[o * 2 + 0] = observed_2d[o, 0] - u_pred
                errors_out[o * 2 + 1] = observed_2d[o, 1] - v_pred
            else:
                errors_out[o * 2 + 0] = 0.0
                errors_out[o * 2 + 1] = 0.0

    @ti.kernel
    def build_jtj_jte_kernel(
        cameras: ti.types.ndarray(ti.f32, ndim=2),       # (n_cam, N_cam_params)
        points_3d: ti.types.ndarray(ti.f32, ndim=2),     # (n_pts, 3)
        observations: ti.types.ndarray(ti.i32, ndim=2),   # (n_obs, 2)
        observed_2d: ti.types.ndarray(ti.f32, ndim=2),    # (n_obs, 2)
        JtJ_cam: ti.types.ndarray(ti.f32, ndim=3),        # (n_cam, 6, 6) per-camera Hessian block
        JtJ_pt: ti.types.ndarray(ti.f32, ndim=3),         # (n_pts, 3, 3) per-point Hessian block
        JtJ_cp: ti.types.ndarray(ti.f32, ndim=4),         # (n_cam, n_pts, 6, 3) cross-term (sparse)
        Jte_cam: ti.types.ndarray(ti.f32, ndim=2),        # (n_cam, 6)
        Jte_pt: ti.types.ndarray(ti.f32, ndim=2),         # (n_pts, 3)
        n_obs: int,
        n_cam: int,
        n_pts: int,
    ):
        """Build normal equations: J^T J dan J^T e.
        Uses Schur complement structure: cameras then points.
        """
        for o in range(n_obs):
            ci = observations[o, 0]
            pi = observations[o, 1]

            # Camera params
            ax = cameras[ci, 0]; ay = cameras[ci, 1]; az = cameras[ci, 2]
            angle = cameras[ci, 3]
            tx = cameras[ci, 4]; ty = cameras[ci, 5]; tz = cameras[ci, 6]
            fx = cameras[ci, 7]; fy = cameras[ci, 8]
            cx_val = cameras[ci, 9] if cameras.shape[1] > 9 else 0.0
            cy_val = cameras[ci, 10] if cameras.shape[1] > 10 else 0.0

            norm = ti.sqrt(ax * ax + ay * ay + az * az + 1e-10)
            kx = ax / norm; ky = ay / norm; kz = az / norm

            dR_dwx, dR_dwy, dR_dwz, R00, R01, R02, R10, R11, R12, R20, R21, R22 = (
                rodrigues_jacobian(ti.Vector([kx, ky, kz]), angle)
            )

            X = points_3d[pi, 0]; Y = points_3d[pi, 1]; Z = points_3d[pi, 2]
            Xc = R00 * X + R01 * Y + R02 * Z + tx
            Yc = R10 * X + R11 * Y + R12 * Z + ty
            Zc = R20 * X + R21 * Y + R22 * Z + tz

            if ti.abs(Zc) < 1e-10:
                continue

            inv_Z = 1.0 / Zc
            inv_Z2 = inv_Z * inv_Z

            # Reprojection error
            u_pred = fx * Xc * inv_Z + cx_val
            v_pred = fy * Yc * inv_Z + cy_val
            eu = observed_2d[o, 0] - u_pred
            ev = observed_2d[o, 1] - v_pred

            # Jacobian w.r.t. Xc, Yc, Zc (projected)
            # du/dXc = fx/Z, du/dZc = -fx*Xc/Z^2, etc.
            du_dXc = fx * inv_Z
            du_dZc = -fx * Xc * inv_Z2
            dv_dYc = fy * inv_Z
            dv_dZc = -fy * Yc * inv_Z2

            # Jacobian w.r.t. rotation (3 params ωx, ωy, ωz)
            # d(Xc)/dωx = dR_dwx * [X,Y,Z]
            dXc_dwx = dR_dwx[0, 0] * X + dR_dwx[0, 1] * Y + dR_dwx[0, 2] * Z
            dYc_dwx = dR_dwx[1, 0] * X + dR_dwx[1, 1] * Y + dR_dwx[1, 2] * Z
            dZc_dwx = dR_dwx[2, 0] * X + dR_dwx[2, 1] * Y + dR_dwx[2, 2] * Z

            dXc_dwy = dR_dwy[0, 0] * X + dR_dwy[0, 1] * Y + dR_dwy[0, 2] * Z
            dYc_dwy = dR_dwy[1, 0] * X + dR_dwy[1, 1] * Y + dR_dwy[1, 2] * Z
            dZc_dwy = dR_dwy[2, 0] * X + dR_dwy[2, 1] * Y + dR_dwy[2, 2] * Z

            dXc_dwz = dR_dwz[0, 0] * X + dR_dwz[0, 1] * Y + dR_dwz[0, 2] * Z
            dYc_dwz = dR_dwz[1, 0] * X + dR_dwz[1, 1] * Y + dR_dwz[1, 2] * Z
            dZc_dwz = dR_dwz[2, 0] * X + dR_dwz[2, 1] * Y + dR_dwz[2, 2] * Z

            # du/dωx = du/dXc * dXc/dωx + du/dZc * dZc/dωx
            du_dwx = du_dXc * dXc_dwx + du_dZc * dZc_dwx
            dv_dwx = dv_dYc * dYc_dwx + dv_dZc * dZc_dwx
            du_dwy = du_dXc * dXc_dwy + du_dZc * dZc_dwy
            dv_dwy = dv_dYc * dYc_dwy + dv_dZc * dZc_dwy
            du_dwz = du_dXc * dXc_dwz + du_dZc * dZc_dwz
            dv_dwz = dv_dYc * dYc_dwz + dv_dZc * dZc_dwz

            # du/dtx = du/dXc * 1, dv/dty = dv/dYc * 1, du/dtz = du/dZc * 1
            du_dtx = du_dXc
            dv_dty = dv_dYc
            du_dtz = du_dZc
            dv_dtz = dv_dZc

            # Jacobian w.r.t. 3D point: dXc/dX = R00, R01, R02 etc.
            du_dX = du_dXc * R00 + du_dZc * R20
            du_dY = du_dXc * R01 + du_dZc * R21
            du_dZ = du_dXc * R02 + du_dZc * R22
            dv_dX = dv_dYc * R10 + dv_dZc * R20
            dv_dY = dv_dYc * R11 + dv_dZc * R21
            dv_dZ = dv_dYc * R12 + dv_dZc * R22

            # Camera Jacobian: J_c = [[du_dwx, du_dwy, du_dwz, du_dtx, du_dty, du_dtz],
            #                          [dv_dwx, dv_dwy, dv_dwz, dv_dtx, dv_dty, dv_dtz]]
            # Point Jacobian: J_p = [[du_dX, du_dY, du_dZ],
            #                         [dv_dX, dv_dY, dv_dZ]]

            # Accumulate J^T J (camera block) and J^T e (camera)
            for i in range(6):
                Ji_u = 0.0; Ji_v = 0.0
                if i == 0: Ji_u = du_dwx; Ji_v = dv_dwx
                elif i == 1: Ji_u = du_dwy; Ji_v = dv_dwy
                elif i == 2: Ji_u = du_dwz; Ji_v = dv_dwz
                elif i == 3: Ji_u = du_dtx; Ji_v = 0.0
                elif i == 4: Ji_u = 0.0; Ji_v = dv_dty
                elif i == 5: Ji_u = du_dtz; Ji_v = dv_dtz

                # J^T e
                ti.atomic_add(Jte_cam[ci, i], Ji_u * eu + Ji_v * ev)

                # J^T J diagonal block (camera)
                for j in range(6):
                    Jj_u = 0.0; Jj_v = 0.0
                    if j == 0: Jj_u = du_dwx; Jj_v = dv_dwx
                    elif j == 1: Jj_u = du_dwy; Jj_v = dv_dwy
                    elif j == 2: Jj_u = du_dwz; Jj_v = dv_dwz
                    elif j == 3: Jj_u = du_dtx; Jj_v = 0.0
                    elif j == 4: Jj_u = 0.0; Jj_v = dv_dty
                    elif j == 5: Jj_u = du_dtz; Jj_v = dv_dtz

                    ti.atomic_add(JtJ_cam[ci, i, j], Ji_u * Jj_u + Ji_v * Jj_v)

            # Accumulate J^T J (point block) and J^T e (point)
            Jp = ti.Matrix([
                [du_dX, du_dY, du_dZ],
                [dv_dX, dv_dY, dv_dZ]
            ])

            for i in range(3):
                ti.atomic_add(Jte_pt[pi, i], Jp[0, i] * eu + Jp[1, i] * ev)
                for j in range(3):
                    ti.atomic_add(JtJ_pt[pi, i, j], Jp[0, i] * Jp[0, j] + Jp[1, i] * Jp[1, j])

            # Cross-term: camera-point block (for Schur complement)
            for i in range(6):
                Ji_u = 0.0; Ji_v = 0.0
                if i == 0: Ji_u = du_dwx; Ji_v = dv_dwx
                elif i == 1: Ji_u = du_dwy; Ji_v = dv_dwy
                elif i == 2: Ji_u = du_dwz; Ji_v = dv_dwz
                elif i == 3: Ji_u = du_dtx; Ji_v = 0.0
                elif i == 4: Ji_u = 0.0; Ji_v = dv_dty
                elif i == 5: Ji_u = du_dtz; Ji_v = dv_dtz

                for j in range(3):
                    val = Ji_u * Jp[0, j] + Ji_v * Jp[1, j]
                    ti.atomic_add(JtJ_cp[ci, pi, i, j], val)

    @ti.kernel
    def apply_point_update_kernel(
        points_3d: ti.types.ndarray(ti.f32, ndim=2),    # (n_pts, 3)
        delta_pts: ti.types.ndarray(ti.f64, ndim=2),    # (n_pts, 3)
        n_pts: int,
        damping: ti.f32,
    ):
        """Apply damped update to 3D points."""
        for i in range(n_pts):
            points_3d[i, 0] += ti.cast(delta_pts[i, 0] * damping, ti.f32)
            points_3d[i, 1] += ti.cast(delta_pts[i, 1] * damping, ti.f32)
            points_3d[i, 2] += ti.cast(delta_pts[i, 2] * damping, ti.f32)

    @ti.kernel
    def apply_camera_update_kernel(
        cameras: ti.types.ndarray(ti.f32, ndim=2),      # (n_cam, N_params)
        delta_cam: ti.types.ndarray(ti.f64, ndim=2),    # (n_cam, 6)
        n_cam: int,
        damping: ti.f32,
    ):
        """Apply damped update to camera parameters (axis-angle + translation)."""
        for i in range(n_cam):
            # Update rotation (axis-angle)
            cameras[i, 0] += ti.cast(delta_cam[i, 0] * damping, ti.f32)
            cameras[i, 1] += ti.cast(delta_cam[i, 1] * damping, ti.f32)
            cameras[i, 2] += ti.cast(delta_cam[i, 2] * damping, ti.f32)
            # Update angle (scalar)
            cameras[i, 3] += ti.cast(delta_cam[i, 3] * damping, ti.f32)
            # Update translation
            cameras[i, 4] += ti.cast(delta_cam[i, 4] * damping, ti.f32)
            cameras[i, 5] += ti.cast(delta_cam[i, 5] * damping, ti.f32)
            cameras[i, 6] += ti.cast(delta_cam[i, 6] * damping, ti.f32)

    @ti.kernel
    def compute_total_cost_kernel(
        errors: ti.types.ndarray(ti.f32, ndim=1),
        n_obs: int,
    ) -> ti.f32:
        """Compute sum of squared reprojection errors."""
        cost = ti.f32(0.0)
        for i in range(n_obs * 2):
            cost += errors[i] * errors[i]
        return cost


# =============================================================================
# PYTHON API
# =============================================================================

def bundle_adjust_lm(
    cameras,       # (n_cam, N_params) float32 — [ax,ay,az, angle, tx,ty,tz, fx, fy, cx, cy]
    points_3d,     # (n_pts, 3) float32
    observations,  # (n_obs, 2) int32 — [cam_idx, pt_idx]
    observed_2d,   # (n_obs, 2) float32 — [u, v]
    max_iterations=50,
    lambda_init=1e-3,
    lambda_factor=10.0,
    convergence_thresh=1e-6,
    fx=None, fy=None, cx=None, cy=None,
):
    """
    Bundle Adjustment via Levenberg-Marquardt.

    Args:
        cameras: (n_cam, 7+) float32 — per-camera [ax,ay,az, angle, tx,ty,tz, ...]
        points_3d: (n_pts, 3) float32
        observations: (n_obs, 2) int32 — [cam_idx, pt_idx]
        observed_2d: (n_obs, 2) float32 — [u, v]
        max_iterations: maximum LM iterations
        lambda_init: initial damping parameter
        lambda_factor: factor to increase/decrease lambda
        convergence_thresh: stop when cost change < threshold
        fx, fy, cx, cy: camera intrinsics (scalar, shared across all cameras)

    Returns:
        cameras_opt: optimized cameras
        points_3d_opt: optimized 3D points
        final_cost: final reprojection error (RMSE)
        n_iterations: number of iterations performed
    """
    cameras = np.ascontiguousarray(cameras.astype(np.float32))
    points_3d = np.ascontiguousarray(points_3d.astype(np.float32))
    observations = np.ascontiguousarray(observations.astype(np.int32))
    observed_2d = np.ascontiguousarray(observed_2d.astype(np.float32))

    n_cam = cameras.shape[0]
    n_pts = points_3d.shape[0]
    n_obs = observations.shape[0]

    if n_obs == 0 or n_cam == 0 or n_pts == 0:
        return cameras, points_3d, 0.0, 0

    if not TAICHI_AVAILABLE:
        return _bundle_adjust_lm_numpy(
            cameras, points_3d, observations, observed_2d,
            max_iterations, lambda_init, lambda_factor, convergence_thresh,
            fx, fy, cx, cy
        )

    # Inject intrinsics into camera array if provided
    if fx is not None:
        # Ensure cameras has at least 11 columns
        if cameras.shape[1] < 11:
            new_cams = np.zeros((n_cam, 11), dtype=np.float32)
            new_cams[:, :cameras.shape[1]] = cameras
            cameras = new_cams
        cameras[:, 7] = fx
        cameras[:, 8] = fy if fy is not None else fx
        cameras[:, 9] = cx if cx is not None else 0.0
        cameras[:, 10] = cy if cy is not None else 0.0

    # GPU buffers
    errors_buf = np.zeros(n_obs * 2, dtype=np.float32)
    lam = lambda_init
    prev_cost = 1e20

    n_iter = 0
    for iteration in range(max_iterations):
        n_iter = iteration + 1

        # 1. Compute current cost
        compute_reprojection_errors_kernel(
            cameras, points_3d, observations, observed_2d, errors_buf, n_obs
        )
        current_cost = compute_total_cost_kernel(errors_buf, n_obs)

        # Check convergence
        if iteration > 0 and abs(prev_cost - current_cost) < convergence_thresh:
            break

        # 2. Build normal equations
        JtJ_cam = np.zeros((n_cam, 6, 6), dtype=np.float64)
        JtJ_pt = np.zeros((n_pts, 3, 3), dtype=np.float64)
        JtJ_cp = np.zeros((n_cam, n_pts, 6, 3), dtype=np.float64)
        Jte_cam = np.zeros((n_cam, 6), dtype=np.float64)
        Jte_pt = np.zeros((n_pts, 3), dtype=np.float64)

        build_jtj_jte_kernel(
            cameras, points_3d, observations, observed_2d,
            JtJ_cam, JtJ_pt, JtJ_cp,
            Jte_cam, Jte_pt,
            n_obs, n_cam, n_pts,
        )

        # 3. Schur Complement: eliminate points
        # S = JtJ_cam - sum_pts(JtJ_cp * inv(JtJ_pt) * JtJ_cp^T)
        # b = Jte_cam - sum_pts(JtJ_cp * inv(JtJ_pt) * Jte_pt)

        # Precompute point inverses
        pt_inv = np.zeros((n_pts, 3, 3), dtype=np.float64)
        for p in range(n_pts):
            try:
                pt_inv[p] = np.linalg.inv(JtJ_pt[p] + lam * np.eye(3))
            except np.linalg.LinAlgError:
                pt_inv[p] = np.eye(3) * (1.0 / (1.0 + lam))

        # Build Schur complement system for cameras
        S = JtJ_cam.copy()
        b_cam = Jte_cam.copy()

        for c in range(n_cam):
            for p in range(n_pts):
                Ecp = JtJ_cp[c, p]  # (6, 3)
                if np.abs(Ecp).sum() < 1e-15:
                    continue
                # S[c] -= Ecp * inv(P[p]) * Ecp^T
                S[c] -= Ecp @ pt_inv[p] @ Ecp.T
                # b_cam[c] -= Ecp * inv(P[p]) * Jte_pt[p]
                b_cam[c] -= Ecp @ pt_inv[p] @ Jte_pt[p]

        # Add LM damping to S diagonal
        for c in range(n_cam):
            diag_vals = np.diag(S[c]).copy()
            S[c] += lam * np.diag(diag_vals + 1e-10)

        # 4. Solve camera deltas
        delta_cam = np.zeros((n_cam, 6), dtype=np.float64)
        for c in range(n_cam):
            try:
                delta_cam[c] = np.linalg.solve(S[c], b_cam[c])
            except np.linalg.LinAlgError:
                delta_cam[c] = 0.0

        # 5. Back-substitute for point deltas
        delta_pts = np.zeros((n_pts, 3), dtype=np.float64)
        for p in range(n_pts):
            rhs = Jte_pt[p].copy()
            for c in range(n_cam):
                Ecp = JtJ_cp[c, p]
                if np.abs(Ecp).sum() < 1e-15:
                    continue
                rhs -= Ecp.T @ delta_cam[c]
            delta_pts[p] = pt_inv[p] @ rhs

        # 6. Trial update and evaluate
        cameras_trial = cameras.copy()
        points_trial = points_3d.copy()

        apply_camera_update_kernel(cameras_trial, delta_cam, n_cam, 1.0)
        apply_point_update_kernel(points_trial, delta_pts, n_pts, 1.0)

        compute_reprojection_errors_kernel(
            cameras_trial, points_trial, observations, observed_2d, errors_buf, n_obs
        )
        trial_cost = compute_total_cost_kernel(errors_buf, n_obs)

        # 7. Accept or reject
        if trial_cost < current_cost:
            # Accept: decrease lambda
            cameras = cameras_trial
            points_3d = points_trial
            lam = max(lam / lambda_factor, 1e-10)
            prev_cost = current_cost
        else:
            # Reject: increase lambda
            lam = min(lam * lambda_factor, 1e10)

    # Final cost
    compute_reprojection_errors_kernel(
        cameras, points_3d, observations, observed_2d, errors_buf, n_obs
    )
    final_cost = np.sqrt(compute_total_cost_kernel(errors_buf, n_obs) / n_obs)

    return cameras, points_3d, float(final_cost), n_iter


# =============================================================================
# NUMPY FALLBACK
# =============================================================================

def _bundle_adjust_lm_numpy(
    cameras, points_3d, observations, observed_2d,
    max_iterations, lambda_init, lambda_factor, convergence_thresh,
    fx, fy, cx, cy
):
    """Pure numpy fallback for bundle adjustment."""
    n_cam = cameras.shape[0]
    n_pts = points_3d.shape[0]
    n_obs = observations.shape[0]

    lam = lambda_init
    prev_cost = 1e20
    n_iter = 0

    for iteration in range(max_iterations):
        n_iter = iteration + 1

        # Compute errors
        total_cost = 0.0
        errors = np.zeros(n_obs * 2, dtype=np.float32)
        for o in range(n_obs):
            ci = observations[o, 0]
            pi = observations[o, 1]
            ax, ay, az, angle, tx, ty, tz = cameras[ci, :7]
            _fx = cameras[ci, 7] if cameras.shape[1] > 7 else (fx or 1.0)
            _fy = cameras[ci, 8] if cameras.shape[1] > 8 else (fy or _fx)
            _cx = cameras[ci, 9] if cameras.shape[1] > 9 else (cx or 0.0)
            _cy = cameras[ci, 10] if cameras.shape[1] > 10 else (cy or 0.0)

            norm = np.sqrt(ax**2 + ay**2 + az**2 + 1e-10)
            k = np.array([ax, ay, az]) / norm
            K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
            R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K

            X = points_3d[pi]
            Xc = R @ X + np.array([tx, ty, tz])

            if abs(Xc[2]) < 1e-10:
                continue

            u_pred = _fx * Xc[0] / Xc[2] + _cx
            v_pred = _fy * Xc[1] / Xc[2] + _cy
            eu = observed_2d[o, 0] - u_pred
            ev = observed_2d[o, 1] - v_pred
            errors[o * 2] = eu
            errors[o * 2 + 1] = ev
            total_cost += eu**2 + ev**2

        rmse = np.sqrt(total_cost / max(n_obs, 1))

        if iteration > 0 and abs(prev_cost - total_cost) < convergence_thresh:
            break
        prev_cost = total_cost

        # Simplified: use numerical gradient for update direction
        # (Full analytical Jacobian is in the Taichi kernel above)
        eps = 1e-4
        grad_cam = np.zeros_like(cameras)
        grad_pts = np.zeros_like(points_3d)

        # Numerical gradient for cameras (rotation + translation only)
        for c in range(n_cam):
            for p_idx in range(min(7, cameras.shape[1])):
                cameras[c, p_idx] += eps
                cost_plus = _compute_cost_np(cameras, points_3d, observations, observed_2d, fx, fy, cx, cy)
                cameras[c, p_idx] -= eps
                grad_cam[c, p_idx] = (cost_plus - total_cost) / eps

        # Numerical gradient for points
        for p in range(n_pts):
            for dim in range(3):
                points_3d[p, dim] += eps
                cost_plus = _compute_cost_np(cameras, points_3d, observations, observed_2d, fx, fy, cx, cy)
                points_3d[p, dim] -= eps
                grad_pts[p, dim] = (cost_plus - total_cost) / eps

        # Gradient descent step with LM damping
        step = 1.0 / (lam + 1.0)
        cameras[:, :7] -= step * 1e-6 * grad_cam[:, :7]
        points_3d -= step * 1e-6 * grad_pts

    return cameras, points_3d, float(rmse), n_iter


def _compute_cost_np(cameras, points_3d, observations, observed_2d, fx, fy, cx, cy):
    """Compute total reprojection cost (numpy)."""
    total = 0.0
    for o in range(observations.shape[0]):
        ci = observations[o, 0]
        pi = observations[o, 1]
        ax, ay, az, angle, tx, ty, tz = cameras[ci, :7]
        _fx = cameras[ci, 7] if cameras.shape[1] > 7 else (fx or 1.0)
        _fy = cameras[ci, 8] if cameras.shape[1] > 8 else (fy or _fx)
        _cx = cameras[ci, 9] if cameras.shape[1] > 9 else (cx or 0.0)
        _cy = cameras[ci, 10] if cameras.shape[1] > 10 else (cy or 0.0)

        norm = np.sqrt(ax**2 + ay**2 + az**2 + 1e-10)
        k = np.array([ax, ay, az]) / norm
        K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
        R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K

        X = points_3d[pi]
        Xc = R @ X + np.array([tx, ty, tz])
        if abs(Xc[2]) < 1e-10:
            continue
        u_pred = _fx * Xc[0] / Xc[2] + _cx
        v_pred = _fy * Xc[1] / Xc[2] + _cy
        total += (observed_2d[o, 0] - u_pred)**2 + (observed_2d[o, 1] - v_pred)**2
    return total
