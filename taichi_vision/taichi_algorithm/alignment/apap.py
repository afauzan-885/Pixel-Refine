"""Adaptive local homography (APAP-style) refinement.

The implementation keeps the APAP contract explicit while remaining usable as
a deterministic reference path: local homographies are fitted at a sparse
source grid using Gaussian correspondence weights, then smoothly blended for
query points.  A global homography is retained as a fail-closed fallback for
cells with insufficient support or degenerate geometry.
"""

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np
import taichi as ti

from .quality import TransformEstimationError, estimate_homography, project_points, validate_correspondences

MAX_NATIVE_TPS_CONTROLS = 64
NATIVE_TPS_ITERATION_BUCKETS = (32, 64, 128, 256, 512, 1024, 2048)


@ti.kernel
def _solve_tps_pivoted_kernel(
    system: ti.types.ndarray(dtype=ti.f32, ndim=2),
    rhs: ti.types.ndarray(dtype=ti.f32, ndim=2),
    solution: ti.types.ndarray(dtype=ti.f32, ndim=2),
    status: ti.types.ndarray(dtype=ti.i32, ndim=1),
):
    """Solve the TPS KKT system with one target-side partial-pivot pass.

    Keeping the pivot sequence inside one kernel avoids constructing an AOT
    graph with one dispatch per elimination step. The loops are deliberately
    serialized because each pivot depends on the preceding matrix update.
    """
    size = system.shape[0]
    status[0] = 1
    ti.loop_config(serialize=True)
    for pivot in range(size):
        pivot_row = pivot
        pivot_abs = ti.abs(system[pivot, pivot])
        ti.loop_config(serialize=True)
        for row in range(pivot + 1, size):
            value = ti.abs(system[row, pivot])
            if value > pivot_abs:
                pivot_abs = value
                pivot_row = row
        if pivot_abs <= 1.0e-12 or pivot_abs != pivot_abs:
            status[0] = 0
        else:
            if pivot_row != pivot:
                for col in range(size):
                    ti.loop_config(serialize=True)
                    value = system[pivot, col]
                    system[pivot, col] = system[pivot_row, col]
                    system[pivot_row, col] = value
                for channel in ti.static(range(2)):
                    value = rhs[pivot, channel]
                    rhs[pivot, channel] = rhs[pivot_row, channel]
                    rhs[pivot_row, channel] = value

            diagonal = system[pivot, pivot]
            for col in range(pivot + 1, size):
                ti.loop_config(serialize=True)
                system[pivot, col] /= diagonal
            for channel in ti.static(range(2)):
                rhs[pivot, channel] /= diagonal
            system[pivot, pivot] = 1.0

            for row in range(size):
                if row != pivot:
                    factor = system[row, pivot]
                    system[row, pivot] = 0.0
                    for col in range(pivot + 1, size):
                        system[row, col] -= factor * system[pivot, col]
                    for channel in ti.static(range(2)):
                        rhs[row, channel] -= factor * rhs[pivot, channel]

    for row, channel in ti.ndrange(size, 2):
        solution[row, channel] = rhs[row, channel]


@ti.kernel
def _fit_apap_weighted_nodes_kernel(
    source: ti.types.ndarray(dtype=ti.f32, ndim=2),
    target: ti.types.ndarray(dtype=ti.f32, ndim=2),
    weights: ti.types.ndarray(dtype=ti.f32, ndim=2),
    homographies: ti.types.ndarray(dtype=ti.f32, ndim=2),
    support_counts: ti.types.ndarray(dtype=ti.i32, ndim=1),
    min_support: ti.i32,
):
    """Fit each normalized weighted homogeneous-DLT model on the active device."""
    for node in range(weights.shape[0]):
        normal = ti.Matrix.zero(ti.f32, 9, 9)
        eigenvectors = ti.Matrix.zero(ti.f32, 9, 9)
        for i in ti.static(range(9)):
            eigenvectors[i, i] = 1.0
        support = 0
        for point in range(source.shape[0]):
            weight = weights[node, point]
            if weight > 1.0e-3:
                support += 1
            if weight > 1.0e-10:
                x = source[point, 0]
                y = source[point, 1]
                u = target[point, 0]
                v = target[point, 1]
                row_x = ti.Vector([-x, -y, -1.0, 0.0, 0.0, 0.0, u * x, u * y, u])
                row_y = ti.Vector([0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v])
                for a in ti.static(range(9)):
                    for b in ti.static(range(9)):
                        normal[a, b] += weight * (
                            row_x[a] * row_x[b] + row_y[a] * row_y[b]
                        )

        support_counts[node] = support
        valid = support >= min_support
        # Symmetric Jacobi eigensolve: the smallest eigenvector of A.T @ A is
        # the same homogeneous weighted-DLT solution selected by NumPy's SVD.
        ti.loop_config(serialize=True)
        for sweep in range(16):
            for p in range(9):
                for q in range(p + 1, 9):
                    apq = normal[p, q]
                    if ti.abs(apq) > 1.0e-10:
                        app = normal[p, p]
                        aqq = normal[q, q]
                        tau = (aqq - app) / (2.0 * apq)
                        root = ti.sqrt(1.0 + tau * tau)
                        t = 1.0 / (tau + root)
                        if tau < 0.0:
                            t = -1.0 / (-tau + root)
                        c = ti.rsqrt(1.0 + t * t)
                        s = t * c
                        for k in range(9):
                            if k != p and k != q:
                                akp = normal[k, p]
                                akq = normal[k, q]
                                normal[k, p] = c * akp - s * akq
                                normal[p, k] = normal[k, p]
                                normal[k, q] = s * akp + c * akq
                                normal[q, k] = normal[k, q]
                            vkp = eigenvectors[k, p]
                            vkq = eigenvectors[k, q]
                            eigenvectors[k, p] = c * vkp - s * vkq
                            eigenvectors[k, q] = s * vkp + c * vkq
                        normal[p, p] = app - t * apq
                        normal[q, q] = aqq + t * apq
                        normal[p, q] = 0.0
                        normal[q, p] = 0.0

        min_index = 0
        min_value = normal[0, 0]
        for i in ti.static(range(1, 9)):
            if normal[i, i] < min_value:
                min_value = normal[i, i]
                min_index = i
        if min_value < -1.0e-4 or min_value != min_value:
            valid = False

        if valid:
            norm = 0.0
            for i in ti.static(range(9)):
                norm += eigenvectors[i, min_index] * eigenvectors[i, min_index]
            norm = ti.rsqrt(ti.max(norm, 1.0e-20))
            for index in ti.static(range(9)):
                homographies[node, index] = eigenvectors[index, min_index] * norm
        else:
            support_counts[node] = 0
            for index in ti.static(range(9)):
                homographies[node, index] = 0.0


@ti.kernel
def _map_apap_points_kernel(
    query: ti.types.ndarray(dtype=ti.f32, ndim=2),
    centers: ti.types.ndarray(dtype=ti.f32, ndim=2),
    homographies: ti.types.ndarray(dtype=ti.f32, ndim=2),
    support_counts: ti.types.ndarray(dtype=ti.i32, ndim=1),
    global_homography: ti.types.ndarray(dtype=ti.f32, ndim=2),
    output: ti.types.ndarray(dtype=ti.f32, ndim=2),
    sigma_x: ti.f32,
    sigma_y: ti.f32,
):
    """Evaluate the APAP local-homography field on the active device."""
    for index in range(query.shape[0]):
        x = query[index, 0]
        y = query[index, 1]
        total_weight = 0.0
        matrix = ti.Matrix.zero(ti.f32, 3, 3)
        for node in range(centers.shape[0]):
            if support_counts[node] > 0:
                dx = x - centers[node, 0]
                dy = y - centers[node, 1]
                weight = ti.exp(
                    -(dx * dx / (2.0 * sigma_x * sigma_x)
                    + dy * dy / (2.0 * sigma_y * sigma_y))
                )
                total_weight += weight
                scale = weight / ti.max(ti.abs(homographies[node, 8]), 1.0e-12)
                for row in ti.static(range(3)):
                    for col in ti.static(range(3)):
                        matrix[row, col] += scale * homographies[node, row * 3 + col]
        denominator = 0.0
        if total_weight > 1.0e-12:
            matrix /= total_weight
            denominator = matrix[2, 0] * x + matrix[2, 1] * y + matrix[2, 2]
        if ti.abs(denominator) <= 1.0e-12 or denominator != denominator:
            matrix = ti.Matrix([
                [global_homography[0, 0], global_homography[0, 1], global_homography[0, 2]],
                [global_homography[1, 0], global_homography[1, 1], global_homography[1, 2]],
                [global_homography[2, 0], global_homography[2, 1], global_homography[2, 2]],
            ])
            denominator = matrix[2, 0] * x + matrix[2, 1] * y + matrix[2, 2]
        mapped_x = (matrix[0, 0] * x + matrix[0, 1] * y + matrix[0, 2]) / denominator
        mapped_y = (matrix[1, 0] * x + matrix[1, 1] * y + matrix[1, 2]) / denominator
        if mapped_x != mapped_x or mapped_y != mapped_y:
            mapped_x = (global_homography[0, 0] * x + global_homography[0, 1] * y + global_homography[0, 2]) / (
                global_homography[2, 0] * x + global_homography[2, 1] * y + global_homography[2, 2]
            )
            mapped_y = (global_homography[1, 0] * x + global_homography[1, 1] * y + global_homography[1, 2]) / (
                global_homography[2, 0] * x + global_homography[2, 1] * y + global_homography[2, 2]
            )
        output[index, 0] = mapped_x
        output[index, 1] = mapped_y


@ti.kernel
def _build_tps_system_kernel(
    source: ti.types.ndarray(dtype=ti.f32, ndim=2),
    target: ti.types.ndarray(dtype=ti.f32, ndim=2),
    system: ti.types.ndarray(dtype=ti.f32, ndim=2),
    rhs: ti.types.ndarray(dtype=ti.f32, ndim=2),
    regularization: ti.f32,
):
    """Build the normalized TPS KKT system entirely on the active target."""
    count = source.shape[0]
    size = system.shape[0]
    for row, col in ti.ndrange(size, size):
        value = 0.0
        if row < count and col < count:
            dx = source[row, 0] - source[col, 0]
            dy = source[row, 1] - source[col, 1]
            radius_sq = dx * dx + dy * dy
            kernel_value = radius_sq * ti.log(ti.max(radius_sq, 1.0e-20))
            if row == col:
                kernel_value += regularization
            value = kernel_value
        elif row < count and col >= count:
            affine_index = col - count
            if affine_index == 0:
                value = source[row, 0]
            elif affine_index == 1:
                value = source[row, 1]
            else:
                value = 1.0
        elif row >= count and col < count:
            affine_index = row - count
            if affine_index == 0:
                value = source[col, 0]
            elif affine_index == 1:
                value = source[col, 1]
            else:
                value = 1.0
        system[row, col] = value

    for row, col in ti.ndrange(size, 2):
        rhs[row, col] = target[row, col] if row < count else 0.0


@ti.kernel
def _initialize_tps_minres_kernel(
    system: ti.types.ndarray(dtype=ti.f32, ndim=2),
    rhs: ti.types.ndarray(dtype=ti.f32, ndim=2),
    solution: ti.types.ndarray(dtype=ti.f32, ndim=2),
    residuals: ti.types.ndarray(dtype=ti.f32, ndim=2),
    directions: ti.types.ndarray(dtype=ti.f32, ndim=2),
    state: ti.types.ndarray(dtype=ti.f32, ndim=2),
    reductions: ti.types.ndarray(dtype=ti.f32, ndim=2),
):
    """Initialize two independent MINRES recurrences for the TPS KKT system."""
    size = system.shape[0]
    for channel in ti.static(range(2)):
        reductions[channel, 0] = 0.0
        state[channel, 0] = 0.0  # beta
        state[channel, 1] = 0.0  # old beta
        state[channel, 2] = 0.0  # dbar
        state[channel, 3] = 0.0  # epsln
        state[channel, 4] = 0.0  # phibar
        state[channel, 5] = -1.0  # cosine
        state[channel, 6] = 0.0  # sine
        state[channel, 7] = 0.0  # beta1
        state[channel, 8] = 0.0  # iteration
        state[channel, 9] = 1.0  # active
        state[channel, 10] = 0.0  # delta
        state[channel, 11] = 0.0  # old epsln
        state[channel, 12] = 0.0  # gamma
        state[channel, 13] = 0.0  # phi

    for row, channel in ti.ndrange(size, 2):
        value = rhs[row, channel]
        ti.atomic_add(reductions[channel, 0], value * value)
        solution[row, channel] = 0.0
        residuals[row, channel] = 0.0  # r_(k-1)
        residuals[row, channel + 2] = value  # r_k
        directions[row, channel] = 0.0  # w_(k-2)
        directions[row, channel + 2] = 0.0  # w_(k-1)

    for channel in ti.static(range(2)):
        beta1 = ti.sqrt(ti.max(reductions[channel, 0], 0.0))
        state[channel, 0] = beta1
        state[channel, 4] = beta1
        state[channel, 7] = beta1
        if beta1 <= 1.0e-20:
            state[channel, 9] = 0.0
        else:
            reductions[channel, 0] = beta1


@ti.kernel
def _tps_minres_step_kernel(
    system: ti.types.ndarray(dtype=ti.f32, ndim=2),
    rhs: ti.types.ndarray(dtype=ti.f32, ndim=2),
    solution: ti.types.ndarray(dtype=ti.f32, ndim=2),
    residuals: ti.types.ndarray(dtype=ti.f32, ndim=2),
    directions: ti.types.ndarray(dtype=ti.f32, ndim=2),
    products: ti.types.ndarray(dtype=ti.f32, ndim=2),
    state: ti.types.ndarray(dtype=ti.f32, ndim=2),
    reductions: ti.types.ndarray(dtype=ti.f32, ndim=2),
    tolerance: ti.f32,
):
    """One parallel matrix-vector and recurrence step for full-system MINRES."""
    size = system.shape[0]
    for channel in ti.static(range(2)):
        reductions[channel, 0] = 0.0  # v_k dot (A v_k)
        reductions[channel, 1] = 0.0  # ||r_(k+1)||^2

    for row, channel in ti.ndrange(size, 2):
        if state[channel, 9] > 0.5:
            beta = state[channel, 0]
            value = 0.0
            if beta > 1.0e-20:
                for col in range(size):
                    value += system[row, col] * residuals[col, channel + 2] / beta
                if state[channel, 8] > 0.5 and state[channel, 1] > 1.0e-20:
                    value -= (beta / state[channel, 1]) * residuals[row, channel]
            products[row, channel] = value
        else:
            products[row, channel] = 0.0

    for row, channel in ti.ndrange(size, 2):
        if state[channel, 9] > 0.5 and state[channel, 0] > 1.0e-20:
            v_value = residuals[row, channel + 2] / state[channel, 0]
            ti.atomic_add(reductions[channel, 0], v_value * products[row, channel])

    for row, channel in ti.ndrange(size, 2):
        if state[channel, 9] > 0.5:
            beta = state[channel, 0]
            alpha = reductions[channel, 0]
            old_r = residuals[row, channel + 2]
            new_r = products[row, channel]
            if beta > 1.0e-20:
                new_r -= (alpha / beta) * old_r
            residuals[row, channel] = old_r
            residuals[row, channel + 2] = new_r
            ti.atomic_add(reductions[channel, 1], new_r * new_r)

    for channel in ti.static(range(2)):
        if state[channel, 9] > 0.5:
            alpha = reductions[channel, 0]
            beta_next = ti.sqrt(ti.max(reductions[channel, 1], 0.0))
            beta = state[channel, 0]
            old_beta = state[channel, 1]
            cosine = state[channel, 5]
            sine = state[channel, 6]
            dbar = state[channel, 2]
            phibar = state[channel, 4]
            old_eps = state[channel, 3]
            delta = cosine * dbar + sine * alpha
            gbar = sine * dbar - cosine * alpha
            epsln = sine * beta_next
            dbar_next = -cosine * beta_next
            gamma = ti.sqrt(gbar * gbar + beta_next * beta_next)
            if gamma <= 1.0e-20 or gamma != gamma:
                state[channel, 9] = -1.0
            else:
                cosine_next = gbar / gamma
                sine_next = beta_next / gamma
                phi = cosine_next * phibar
                phibar_next = sine_next * phibar
                state[channel, 1] = beta
                state[channel, 0] = beta_next
                state[channel, 2] = dbar_next
                state[channel, 3] = epsln
                state[channel, 4] = phibar_next
                state[channel, 5] = cosine_next
                state[channel, 6] = sine_next
                state[channel, 8] += 1.0
                state[channel, 10] = delta
                state[channel, 11] = old_eps
                state[channel, 12] = gamma
                state[channel, 13] = phi
                if ti.abs(phibar_next) <= tolerance * ti.max(state[channel, 7], 1.0e-20):
                    state[channel, 9] = 2.0

    for row, channel in ti.ndrange(size, 2):
        if state[channel, 9] > 0.5:
            old_beta = ti.max(state[channel, 1], 1.0e-20)
            gamma = ti.max(state[channel, 12], 1.0e-20)
            old_eps = state[channel, 11]
            delta = state[channel, 10]
            phi = state[channel, 13]
            v_value = residuals[row, channel] / old_beta
            w_value = (
                v_value
                - old_eps * directions[row, channel]
                - delta * directions[row, channel + 2]
            ) / gamma
            solution[row, channel] += phi * w_value
            directions[row, channel] = directions[row, channel + 2]
            directions[row, channel + 2] = w_value
    for channel in ti.static(range(2)):
        if state[channel, 9] > 1.5:
            state[channel, 9] = 0.0


@ti.kernel
def _map_tps_points_kernel(
    query: ti.types.ndarray(dtype=ti.f32, ndim=2),
    controls: ti.types.ndarray(dtype=ti.f32, ndim=2),
    weights: ti.types.ndarray(dtype=ti.f32, ndim=2),
    affine: ti.types.ndarray(dtype=ti.f32, ndim=2),
    output: ti.types.ndarray(dtype=ti.f32, ndim=2),
    source_center_x: ti.f32,
    source_center_y: ti.f32,
    source_scale: ti.f32,
    destination_center_x: ti.f32,
    destination_center_y: ti.f32,
    destination_scale: ti.f32,
):
    """Evaluate the regularized TPS map through the active target TCM."""
    for index in range(query.shape[0]):
        x = (query[index, 0] - source_center_x) / source_scale
        y = (query[index, 1] - source_center_y) / source_scale
        mapped_x = x * affine[0, 0] + y * affine[1, 0] + affine[2, 0]
        mapped_y = x * affine[0, 1] + y * affine[1, 1] + affine[2, 1]
        for control in range(controls.shape[0]):
            dx = x - controls[control, 0]
            dy = y - controls[control, 1]
            radius_sq = dx * dx + dy * dy
            basis = radius_sq * ti.log(ti.max(radius_sq, 1.0e-20))
            mapped_x += basis * weights[control, 0]
            mapped_y += basis * weights[control, 1]
        output[index, 0] = mapped_x * destination_scale + destination_center_x
        output[index, 1] = mapped_y * destination_scale + destination_center_y


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


def filter_apap_correspondences(
    reference_points: np.ndarray,
    support_points: np.ndarray,
    support_to_reference: np.ndarray,
    *,
    residual_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Keep plausible feature matches while retaining moderate local motion.

    A global RANSAC inlier mask is too strict for APAP: it removes matches
    from locally moving/parallax regions. This wider residual gate keeps those
    matches but still rejects gross descriptor mismatches before local fitting.
    """
    ref, supp = validate_correspondences(
        reference_points,
        support_points,
        min_points=4,
        name="APAP feature correspondences",
    )
    projected = project_points(supp, support_to_reference)
    residual = np.linalg.norm(projected - ref, axis=1)
    keep = np.isfinite(residual) & (residual <= max(float(residual_threshold), 0.0))
    if int(keep.sum()) < 4:
        raise TransformEstimationError(
            "APAP residual gate retained fewer than four feature matches"
        )
    return np.ascontiguousarray(ref[keep]), np.ascontiguousarray(supp[keep])


@dataclass
class APAPWarp:
    """Sparse local-homography field with global fallback and non-rigid residual support."""

    source_points: np.ndarray
    target_points: np.ndarray
    centers: np.ndarray
    homographies: np.ndarray
    global_homography: np.ndarray
    sigma: float | tuple[float, float]
    support_counts: np.ndarray
    residual_field: object | None = None
    native: bool = False

    def to_flow(
        self,
        flow_shape: tuple[int, int],
        *,
        full_shape: tuple[int, int],
    ) -> np.ndarray:
        """Encode this inverse map for the existing AOT flow consumers.

        Nodes cover the reference image including both endpoints, matching
        remap/CFA interpolation. Displacements use flow-grid pixel units;
        consumers scale them by full_width/flow_width and full_height/flow_height.
        The small field preserves local geometry without a full-resolution map.
        """
        flow_h, flow_w = (int(value) for value in flow_shape)
        full_h, full_w = (int(value) for value in full_shape)
        if min(flow_h, flow_w, full_h, full_w) < 2:
            raise ValueError("APAP flow and full shapes must have at least two pixels per axis")
        xx, yy = np.meshgrid(
            np.linspace(0.0, full_w - 1.0, flow_w),
            np.linspace(0.0, full_h - 1.0, flow_h),
        )
        query = np.column_stack((xx.ravel(), yy.ravel()))
        mapped = self.map_points(query)
        if not np.isfinite(mapped).all():
            raise TransformEstimationError("APAP produced non-finite flow coordinates")
        flow = (mapped - query).reshape(flow_h, flow_w, 2)
        flow *= np.array((flow_w / full_w, flow_h / full_h))
        return np.ascontiguousarray(flow, dtype=np.float32)

    def map_points(self, points: np.ndarray) -> np.ndarray:
        query = np.ascontiguousarray(points, dtype=np.float64)
        if query.ndim != 2 or query.shape[1:] != (2,):
            raise ValueError(f"points must have shape (N, 2), got {query.shape}")
        if len(query) == 0:
            return np.empty((0, 2), dtype=np.float64)
        if self.native:
            if isinstance(self.residual_field, APAPNativeTPSWarp):
                return self.residual_field.map_points(query)
            if self.residual_field is not None:
                raise RuntimeError(
                    "Native APAP received a non-native residual model; "
                    "provide target-native APAP residual graphs."
                )
            return _map_apap_points_native(self, query)
        if self.residual_field is not None:
            return self.residual_field.map_points(query)
        n_query = len(query)
        global_mapped = project_points(query, self.global_homography)

        delta = query[:, None, :] - self.centers[None, :, :]
        if isinstance(self.sigma, (tuple, list, np.ndarray)):
            sig_x = max(float(self.sigma[0]), 1.0e-8)
            sig_y = max(float(self.sigma[1]), 1.0e-8)
            radius_sq = (delta[:, :, 0] ** 2) / (2.0 * sig_x * sig_x) + (delta[:, :, 1] ** 2) / (2.0 * sig_y * sig_y)
            weights = np.exp(-radius_sq)
        else:
            sig = max(float(self.sigma), 1.0e-8)
            radius_sq = np.sum(delta * delta, axis=2) / (2.0 * sig * sig)
            weights = np.exp(-radius_sq)

        weights *= (self.support_counts[None, :] > 0)
        sums = np.sum(weights, axis=1)

        valid_sum = sums > 1.0e-12
        if not np.any(valid_sum):
            return global_mapped

        safe_sums = np.where(valid_sum, sums, 1.0)
        matrices = np.einsum('nm,mij->nij', weights, self.homographies) / safe_sums[:, None, None]
        m_22 = matrices[:, 2, 2]
        valid_matrix = valid_sum & np.isfinite(matrices).all(axis=(1, 2)) & (np.abs(m_22) > 1.0e-12)

        norm_matrices = np.zeros((n_query, 3, 3), dtype=np.float64)
        norm_matrices[valid_matrix] = matrices[valid_matrix] / m_22[valid_matrix, None, None]
        norm_matrices[~valid_matrix] = self.global_homography

        homog = np.column_stack((query, np.ones(n_query, dtype=np.float64)))
        projected = np.einsum('nij,nj->ni', norm_matrices, homog)
        denom = projected[:, 2]
        good_denom = np.abs(denom) > np.finfo(np.float64).eps
        outputs = np.where(
            good_denom[:, None],
            projected[:, :2] / np.where(good_denom, denom, 1.0)[:, None],
            global_mapped,
        )
        finite_out = np.isfinite(outputs).all(axis=1)
        outputs = np.where(finite_out[:, None], outputs, global_mapped)
        return outputs

    __call__ = map_points


@dataclass
class APAPNativeTPSWarp:
    """TPS coefficients fitted and evaluated by the active APAP TCM graphs."""

    control_points: np.ndarray
    weights: np.ndarray
    affine: np.ndarray
    source_center: np.ndarray
    source_scale: float
    destination_center: np.ndarray
    destination_scale: float
    regularization: float
    condition_estimate: float

    def map_points(self, points: np.ndarray) -> np.ndarray:
        query = np.ascontiguousarray(points, dtype=np.float64)
        if query.ndim != 2 or query.shape[1:] != (2,):
            raise ValueError(f"points must have shape (N, 2), got {query.shape}")
        if len(query) == 0:
            return np.empty((0, 2), dtype=np.float64)
        return _map_apap_tps_points_native(self, query)

    __call__ = map_points


def _estimate_similarity(source: np.ndarray, target: np.ndarray, *, weights: np.ndarray | None = None) -> np.ndarray:
    """Least-squares 2-D similarity estimate (scale, rotation, translation)."""
    src, dst = validate_correspondences(source, target, min_points=2)
    n = len(src)
    A = np.zeros((2 * n, 4), dtype=np.float64)
    b = np.zeros(2 * n, dtype=np.float64)
    A[0::2, 0] = src[:, 0]; A[0::2, 1] = -src[:, 1]; A[0::2, 2] = 1.0; b[0::2] = dst[:, 0]
    A[1::2, 0] = src[:, 1]; A[1::2, 1] = src[:, 0]; A[1::2, 3] = 1.0; b[1::2] = dst[:, 1]
    if weights is not None:
        w = np.asarray(weights, dtype=np.float64).reshape(-1)
        w_scale = np.repeat(np.sqrt(np.clip(w, 0.0, None)), 2)[:, None]
        A = A * w_scale
        b = b * w_scale[:, 0]
    try:
        coeff, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
        a, b_val, tx, ty = coeff
        return np.array([
            [a, -b_val, tx],
            [b_val, a, ty],
            [0.0, 0.0, 1.0]
        ], dtype=np.float64)
    except Exception:
        matrix = np.eye(3, dtype=np.float64)
        matrix[:2, 2] = np.mean(dst - src, axis=0)
        return matrix


@dataclass
class AANAPWarp:
    """Adaptive As-Natural-As-Possible Warp (Lin et al. 2015).

    Higher-precision alternative to APAP: combines moving DLT homography in the
    overlap region with global similarity transform in non-overlapping regions,
    preventing projective distortion and shape expansion in multi-row stitching.
    """

    source_points: np.ndarray
    target_points: np.ndarray
    apap_warp: APAPWarp
    global_similarity: np.ndarray
    overlap_bounds: tuple[float, float, float, float]  # min_x, min_y, max_x, max_y
    transition_sigma: float = 100.0

    def map_points(self, points: np.ndarray) -> np.ndarray:
        query = np.ascontiguousarray(points, dtype=np.float64)
        if query.ndim != 2 or query.shape[1:] != (2,):
            raise ValueError(f"points must have shape (N, 2), got {query.shape}")
        if len(query) == 0:
            return np.empty((0, 2), dtype=np.float64)

        # 1. Evaluate APAP moving homographies
        apap_pts = self.apap_warp.map_points(query)

        # 2. Evaluate Global Similarity
        sim_pts = project_points(query, self.global_similarity, model="similarity")

        # 3. Compute distance to overlap bounding region
        min_x, min_y, max_x, max_y = self.overlap_bounds
        dx = np.maximum(0.0, np.maximum(min_x - query[:, 0], query[:, 0] - max_x))
        dy = np.maximum(0.0, np.maximum(min_y - query[:, 1], query[:, 1] - max_y))
        dist_sq = dx * dx + dy * dy

        # 4. Smooth natural blending weight: 1.0 in overlap -> 0.0 outside
        mu = np.exp(-dist_sq / (2.0 * max(float(self.transition_sigma), 1.0) ** 2))[:, None]

        out = mu * apap_pts + (1.0 - mu) * sim_pts
        return np.where(np.isfinite(out), out, sim_pts)

    __call__ = map_points



def _fit_apap_numpy_reference(
    source: np.ndarray,
    target: np.ndarray,
    *,
    global_homography: np.ndarray | None = None,
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | tuple[float, float] | None = None,
    min_support: int = 4,
    max_controls_per_node: int = 64,
    enable_residual_spline: bool = True,
) -> APAPWarp:
    """Fit an APAP-style local homography field.

    ``source``/``target`` should be descriptor-filtered, locally plausible
    correspondences. For APAP, retaining moderate residuals from a global
    homography is important because those matches carry parallax/local-motion
    information. Callers should reject gross mismatches before fitting.
    Supports anisotropic sigma (sigma_x, sigma_y) for multi-row and multi-column grids.
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

    span = hi - lo
    if sigma is None:
        sig_x = max(float(span[0]) / max(float(cols), 1.0), 1.0)
        sig_y = max(float(span[1]) / max(float(rows), 1.0), 1.0)
        sigma = (sig_x, sig_y)
    elif isinstance(sigma, (tuple, list, np.ndarray)):
        sigma = (max(float(sigma[0]), 1.0e-8), max(float(sigma[1]), 1.0e-8))
    else:
        sigma = max(float(sigma), 1.0e-8)

    homographies = np.repeat(global_homography[None, :, :], len(centers), axis=0)
    supports = np.zeros(len(centers), dtype=np.int32)

    for index, center in enumerate(centers):
        delta = src - center[None, :]
        if isinstance(sigma, tuple):
            dist_sq = (delta[:, 0] ** 2) / (2.0 * sigma[0] ** 2) + (delta[:, 1] ** 2) / (2.0 * sigma[1] ** 2)
            weights = np.exp(-dist_sq)
        else:
            dist_sq = np.sum(delta ** 2, axis=1)
            weights = np.exp(-dist_sq / (2.0 * sigma * sigma))

        if len(weights) > int(max_controls_per_node):
            nearest = np.argpartition(dist_sq, int(max_controls_per_node) - 1)[: int(max_controls_per_node)]
            weights = np.where(np.isin(np.arange(len(weights)), nearest), weights, 0.0)
        supports[index] = int(np.count_nonzero(weights > 1.0e-3))
        if supports[index] < int(min_support):
            continue
        try:
            H_cand = _weighted_homography(src, dst, weights)
            mapped_cand = project_points(src, H_cand)
            loc_mask = weights > 1.0e-3
            err_cand = float(np.mean(np.linalg.norm(mapped_cand[loc_mask] - dst[loc_mask], axis=1)))
            if np.isfinite(err_cand) and err_cand < 50.0:
                homographies[index] = H_cand
            else:
                supports[index] = 0
        except (ValueError, np.linalg.LinAlgError, TransformEstimationError):
            supports[index] = 0

    warp = APAPWarp(
        source_points=np.ascontiguousarray(src),
        target_points=np.ascontiguousarray(dst),
        centers=np.ascontiguousarray(centers),
        homographies=np.ascontiguousarray(homographies),
        global_homography=np.ascontiguousarray(global_homography),
        sigma=sigma,
        support_counts=supports,
        residual_field=None,
    )
    if enable_residual_spline and len(src) >= 4:
        mapped_check = warp.map_points(src)
        err_check = float(np.mean(np.linalg.norm(mapped_check - dst, axis=1)))
        if err_check > 0.05:
            try:
                from .tps import fit_tps_checked
                res_field, q = fit_tps_checked(src, dst, regularization=1e-5)
                if q.valid:
                    warp.residual_field = res_field
            except Exception:
                pass
    return warp


def fit_apap_reference(
    source: np.ndarray,
    target: np.ndarray,
    *,
    global_homography: np.ndarray | None = None,
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | tuple[float, float] | None = None,
    min_support: int = 4,
    max_controls_per_node: int = 64,
    enable_residual_spline: bool = True,
) -> APAPWarp:
    """Return the preserved NumPy APAP oracle for deterministic parity tests."""
    return _fit_apap_numpy_reference(
        source,
        target,
        global_homography=global_homography,
        grid_shape=grid_shape,
        sigma=sigma,
        min_support=min_support,
        max_controls_per_node=max_controls_per_node,
        enable_residual_spline=enable_residual_spline,
    )


def _load_apap_native_module():
    from taichi_vision.taichi_algorithm import aot_api

    try:
        return aot_api.load_tcm("apap_native")
    except Exception as exc:
        try:
            target, _ = aot_api._module_loader.resolve_target()
            target_id = target.target_id
        except Exception:
            target_id = str(aot_api.backend_info().get("arch", "unknown"))
        raise RuntimeError(
            "APAP native execution requires target-qualified module "
            f"'apap_native' with algn_apap_fit_weighted_f32 and "
            f"algn_apap_map_points_f32 for active target {target_id!r}. "
            "Compile the matching alignment TCM; no CPU/NumPy fallback is used."
        ) from exc


def _normalize_points_for_native(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    center = np.mean(points, axis=0)
    radius = np.sqrt(np.mean(np.sum((points - center) ** 2, axis=1)))
    scale = np.sqrt(2.0) / max(float(radius), 1.0e-12)
    transform = np.array(
        [[scale, 0.0, -scale * center[0]],
         [0.0, scale, -scale * center[1]],
         [0.0, 0.0, 1.0]],
        dtype=np.float64,
    )
    normalized = project_points(points, transform, model="affine")
    return normalized, transform


def _normalize_tps_points(points: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    center = np.mean(points, axis=0)
    scale = max(
        float(np.sqrt(np.mean(np.sum((points - center[None, :]) ** 2, axis=1)))),
        1.0e-8,
    )
    normalized = (points - center[None, :]) / scale
    return np.ascontiguousarray(normalized), np.asarray(center), scale


def _sample_tps_control_indices(
    source: np.ndarray, target: np.ndarray, limit: int
) -> np.ndarray:
    """Select spatial coverage plus high-local-motion TPS controls deterministically."""
    points = np.ascontiguousarray(source, dtype=np.float64)
    target = np.ascontiguousarray(target, dtype=np.float64)
    count = len(points)
    if count <= limit:
        return np.arange(count, dtype=np.int64)
    lo = np.min(points, axis=0)
    span = np.maximum(np.max(points, axis=0) - lo, 1.0e-12)
    normalized = (points - lo[None, :]) / span[None, :]
    center = np.mean(normalized, axis=0)
    first = int(np.argmin(np.sum((normalized - center[None, :]) ** 2, axis=1)))
    spatial_count = limit - max(4, limit // 4)
    selected = np.empty(spatial_count, dtype=np.int64)
    selected[0] = first
    min_distance_sq = np.sum((normalized - normalized[first][None, :]) ** 2, axis=1)
    min_distance_sq[first] = -1.0
    for index in range(1, spatial_count):
        next_index = int(np.argmax(min_distance_sq))
        selected[index] = next_index
        distance_sq = np.sum((normalized - normalized[next_index][None, :]) ** 2, axis=1)
        min_distance_sq = np.minimum(min_distance_sq, distance_sq)
        min_distance_sq[selected[: index + 1]] = -1.0

    # Keep a quarter of the controls near the strongest residual motion so a
    # localized deformation is not averaged away by uniform spatial coverage.
    motion = target - points
    motion -= np.median(motion, axis=0, keepdims=True)
    motion_strength = np.linalg.norm(motion, axis=1)
    motion_order = np.argsort(-motion_strength, kind="stable")
    output = selected.tolist()
    selected_set = set(output)
    for candidate in motion_order:
        candidate_index = int(candidate)
        if candidate_index not in selected_set:
            output.append(candidate_index)
            selected_set.add(candidate_index)
            if len(output) == limit:
                break
    return np.asarray(output, dtype=np.int64)


def _map_apap_points_native(warp: APAPWarp, points: np.ndarray) -> np.ndarray:
    from taichi_vision.taichi_algorithm import aot_api

    module = _load_apap_native_module()
    query = np.ascontiguousarray(points, dtype=np.float32)
    centers = np.ascontiguousarray(warp.centers, dtype=np.float32)
    matrices = np.ascontiguousarray(warp.homographies.reshape(-1, 9), dtype=np.float32)
    supports = np.ascontiguousarray(warp.support_counts, dtype=np.int32)
    global_h = np.ascontiguousarray(warp.global_homography, dtype=np.float32)
    sigma_x, sigma_y = (
        (float(warp.sigma[0]), float(warp.sigma[1]))
        if isinstance(warp.sigma, (tuple, list, np.ndarray))
        else (float(warp.sigma), float(warp.sigma))
    )
    buffers = [
        aot_api.upload(query),
        aot_api.upload(centers),
        aot_api.upload(matrices),
        aot_api.upload(supports),
        aot_api.upload(global_h),
        aot_api.upload(np.zeros((len(query), 2), dtype=np.float32)),
    ]
    try:
        module.run(
            "algn_apap_map_points_f32",
            query=buffers[0], centers=buffers[1], homographies=buffers[2],
            support_counts=buffers[3], global_homography=buffers[4], output=buffers[5],
            sigma_x=sigma_x, sigma_y=sigma_y,
        )
        result = buffers[5].to_numpy()
    except Exception as exc:
        raise RuntimeError(
            "APAP native field evaluation failed on the active backend/device. "
            "No CPU/NumPy fallback is used."
        ) from exc
    return np.asarray(result, dtype=np.float64)


def _map_apap_tps_points_native(warp: APAPNativeTPSWarp, points: np.ndarray) -> np.ndarray:
    from taichi_vision.taichi_algorithm import aot_api

    module = _load_apap_native_module()
    query = aot_api.upload(np.ascontiguousarray(points, dtype=np.float32))
    controls = aot_api.upload(np.ascontiguousarray(warp.control_points, dtype=np.float32))
    weights = aot_api.upload(np.ascontiguousarray(warp.weights, dtype=np.float32))
    affine = aot_api.upload(np.ascontiguousarray(warp.affine, dtype=np.float32))
    output = aot_api.upload(np.zeros((len(points), 2), dtype=np.float32))
    try:
        module.run(
            "algn_apap_tps_map_f32",
            query=query,
            controls=controls,
            weights=weights,
            affine=affine,
            output=output,
            source_center_x=float(warp.source_center[0]),
            source_center_y=float(warp.source_center[1]),
            source_scale=float(warp.source_scale),
            destination_center_x=float(warp.destination_center[0]),
            destination_center_y=float(warp.destination_center[1]),
            destination_scale=float(warp.destination_scale),
        )
        mapped = output.to_numpy()
    except Exception as exc:
        raise RuntimeError(
            "APAP native TPS evaluation failed on the selected backend/device; "
            "no NumPy/OpenCV or CPU solver fallback was used."
        ) from exc
    return np.asarray(mapped, dtype=np.float64)


def _fit_apap_tps_native(
    source: np.ndarray,
    target: np.ndarray,
    *,
    regularization: float = 1.0e-5,
    max_condition_number: float = 1.0e12,
) -> APAPNativeTPSWarp | None:
    """Fit and quality-check the optional TPS residual through target TCM graphs."""
    from taichi_vision.taichi_algorithm import aot_api
    src, dst = validate_correspondences(
        source, target, min_points=3, name="TPS control points"
    )
    all_src = src
    if float(regularization) < 0.0:
        raise ValueError("regularization must be non-negative")
    if np.unique(src, axis=0).shape[0] < 3:
        raise TransformEstimationError("TPS control points contain duplicates")
    if np.linalg.matrix_rank(src - np.mean(src, axis=0)) < 2:
        raise TransformEstimationError("TPS control points are collinear")
    control_indices = _sample_tps_control_indices(
        src, dst, MAX_NATIVE_TPS_CONTROLS
    )
    src = np.ascontiguousarray(src[control_indices])
    dst = np.ascontiguousarray(dst[control_indices])
    count = len(src)
    size = count + 3
    if count > MAX_NATIVE_TPS_CONTROLS:
        raise RuntimeError(
            "Native APAP TPS supports at most "
            f"{MAX_NATIVE_TPS_CONTROLS} controls; received {count}. "
            "Compile a larger target-qualified TPS graph for this workload."
        )

    src_norm, src_center, src_scale = _normalize_tps_points(src)
    dst_norm, dst_center, dst_scale = _normalize_tps_points(dst)
    module = _load_apap_native_module()
    source_buffer = aot_api.upload(np.ascontiguousarray(src_norm, dtype=np.float32))
    target_buffer = aot_api.upload(np.ascontiguousarray(dst_norm, dtype=np.float32))
    system = aot_api.upload(np.zeros((size, size), dtype=np.float32))
    rhs = aot_api.upload(np.zeros((size, 2), dtype=np.float32))
    solution = aot_api.upload(np.zeros((size, 2), dtype=np.float32))
    status = aot_api.upload(np.zeros((1,), dtype=np.int32))
    try:
        module.run(
            "algn_apap_tps_pivoted_f32",
            source=source_buffer,
            target=target_buffer,
            system=system,
            rhs=rhs,
            solution=solution,
            status=status,
            regularization=float(regularization),
        )
        coefficients = solution.to_numpy().astype(np.float64)
        solver_status = status.to_numpy()
        system_np = system.to_numpy().astype(np.float64)
    except Exception as exc:
        raise RuntimeError(
            "APAP native TPS fitting failed on the selected backend/device; "
            "no NumPy/CPU fitting fallback was used."
        ) from exc

    if int(solver_status[0]) == 0:
        raise RuntimeError(
            "Native APAP TPS pivoted solve found a singular KKT pivot; "
            "the requested TPS residual was not dropped."
        )
    condition_estimate = float(np.linalg.cond(system_np))
    if not np.isfinite(coefficients).all() or not np.isfinite(condition_estimate):
        raise RuntimeError("Native APAP TPS solve produced non-finite coefficients")
    if condition_estimate > float(max_condition_number):
        raise RuntimeError(
            "Native APAP TPS condition estimate exceeds the supported limit "
            f"({condition_estimate:.3g} > {float(max_condition_number):.3g}); "
            "refusing to drop the requested residual."
        )

    warp = APAPNativeTPSWarp(
        control_points=np.ascontiguousarray(src_norm, dtype=np.float32),
        weights=np.ascontiguousarray(coefficients[:count], dtype=np.float32),
        affine=np.ascontiguousarray(coefficients[count : count + 3], dtype=np.float32),
        source_center=np.asarray(src_center, dtype=np.float64),
        source_scale=float(src_scale),
        destination_center=np.asarray(dst_center, dtype=np.float64),
        destination_scale=float(dst_scale),
        regularization=float(regularization),
        condition_estimate=condition_estimate,
    )

    # Match the existing TPS fold-over quality gate. Coordinate evaluation
    # remains on the selected TCM; only the small 8x8 Jacobian check is host-side.
    lo = np.min(all_src, axis=0)
    hi = np.max(all_src, axis=0)
    if np.any(hi <= lo):
        raise TransformEstimationError("TPS source bounds are degenerate")
    xs = np.linspace(lo[0], hi[0], 8)
    ys = np.linspace(lo[1], hi[1], 8)
    grid = np.stack(np.meshgrid(xs, ys), axis=-1)
    mapped = warp.map_points(grid.reshape(-1, 2)).reshape(8, 8, 2)
    dx = max(float(hi[0] - lo[0]) / 7.0, 1.0e-8)
    dy = max(float(hi[1] - lo[1]) / 7.0, 1.0e-8)
    dfdx = np.gradient(mapped, dx, axis=1, edge_order=1)
    dfdy = np.gradient(mapped, dy, axis=0, edge_order=1)
    determinants = dfdx[..., 0] * dfdy[..., 1] - dfdx[..., 1] * dfdy[..., 0]
    if np.any(~np.isfinite(determinants) | (determinants <= 1.0e-6)):
        raise RuntimeError(
            "Native APAP TPS failed the existing Jacobian orientation gate; "
            "refusing to return an unrefined APAP field."
        )
    return warp


def fit_apap(
    source: np.ndarray,
    target: np.ndarray,
    *,
    global_homography: np.ndarray | None = None,
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | tuple[float, float] | None = None,
    min_support: int = 4,
    max_controls_per_node: int = 64,
    enable_residual_spline: bool = True,
) -> APAPWarp:
    """Fit the APAP node models through the active target-qualified Taichi graph.

    The NumPy solver remains available explicitly as :func:`fit_apap_reference`.
    This production entry point fails clearly when the selected target has no
    compatible APAP graph.
    """
    from taichi_vision.taichi_algorithm import aot_api

    src64, dst64 = validate_correspondences(
        source, target, min_points=4, name="APAP correspondences"
    )
    if global_homography is None:
        global_homography = estimate_homography(src64, dst64)
    global_h = np.asarray(global_homography, dtype=np.float64)
    if global_h.shape != (3, 3) or not np.isfinite(global_h).all():
        raise ValueError("global_homography must be a finite 3x3 matrix")
    if abs(global_h[2, 2]) <= 1.0e-12:
        raise TransformEstimationError("global_homography is singular")
    global_h /= global_h[2, 2]

    rows, cols = max(int(grid_shape[0]), 1), max(int(grid_shape[1]), 1)
    lo = np.min(src64, axis=0)
    hi = np.max(src64, axis=0)
    if np.any(hi <= lo):
        raise TransformEstimationError("APAP source points have zero spatial extent")
    xs = np.linspace(lo[0], hi[0], cols)
    ys = np.linspace(lo[1], hi[1], rows)
    centers = np.stack(np.meshgrid(xs, ys), axis=-1).reshape(-1, 2)
    span = hi - lo
    if sigma is None:
        sigma = (
            max(float(span[0]) / max(float(cols), 1.0), 1.0),
            max(float(span[1]) / max(float(rows), 1.0), 1.0),
        )
    elif isinstance(sigma, (tuple, list, np.ndarray)):
        sigma = (max(float(sigma[0]), 1.0e-8), max(float(sigma[1]), 1.0e-8))
    else:
        sigma = max(float(sigma), 1.0e-8)
    sx, sy = (sigma if isinstance(sigma, tuple) else (sigma, sigma))

    # Preserve the established Gaussian and nearest-control policy. Only the
    # weighted normalized-DLT solve moves to the native graph.
    delta = src64[None, :, :] - centers[:, None, :]
    dist_sq = (delta[..., 0] ** 2) / (2.0 * sx * sx) + (delta[..., 1] ** 2) / (2.0 * sy * sy)
    weights = np.exp(-dist_sq)
    if len(src64) > int(max_controls_per_node):
        nearest = np.argpartition(dist_sq, int(max_controls_per_node) - 1, axis=1)[:, :int(max_controls_per_node)]
        keep = np.zeros_like(weights, dtype=bool)
        np.put_along_axis(keep, nearest, True, axis=1)
        weights = np.where(keep, weights, 0.0)

    src_norm, src_transform = _normalize_points_for_native(src64)
    dst_norm, dst_transform = _normalize_points_for_native(dst64)
    module = _load_apap_native_module()
    src_buffer = aot_api.upload(np.ascontiguousarray(src_norm, dtype=np.float32))
    dst_buffer = aot_api.upload(np.ascontiguousarray(dst_norm, dtype=np.float32))
    weight_buffer = aot_api.upload(np.ascontiguousarray(weights, dtype=np.float32))
    h_buffer = aot_api.upload(np.zeros((len(centers), 9), dtype=np.float32))
    support_buffer = aot_api.upload(np.zeros((len(centers),), dtype=np.int32))
    try:
        module.run(
            "algn_apap_fit_weighted_f32",
            source=src_buffer,
            target=dst_buffer,
            weights=weight_buffer,
            homographies=h_buffer,
            support_counts=support_buffer,
            min_support=int(min_support),
        )
        local_norm = h_buffer.to_numpy().astype(np.float64).reshape(-1, 3, 3)
        supports = support_buffer.to_numpy().astype(np.int32)
    except Exception as exc:
        raise RuntimeError(
            "APAP native weighted fitting failed on the active backend/device. "
            "No CPU/NumPy fallback is used."
        ) from exc

    dst_inverse = np.linalg.inv(dst_transform)
    homographies = np.repeat(global_h[None, :, :], len(centers), axis=0)
    valid_support = supports >= int(min_support)
    for index in np.flatnonzero(valid_support):
        candidate = dst_inverse @ local_norm[index] @ src_transform
        if not np.isfinite(candidate).all() or abs(candidate[2, 2]) <= 1.0e-12:
            supports[index] = 0
            continue
        candidate /= candidate[2, 2]
        mapped = project_points(src64, candidate)
        local = weights[index] > 1.0e-3
        error = float(np.mean(np.linalg.norm(mapped[local] - dst64[local], axis=1)))
        if np.isfinite(error) and error < 50.0:
            homographies[index] = candidate
        else:
            supports[index] = 0

    warp = APAPWarp(
        source_points=np.ascontiguousarray(src64),
        target_points=np.ascontiguousarray(dst64),
        centers=np.ascontiguousarray(centers),
        homographies=np.ascontiguousarray(homographies),
        global_homography=np.ascontiguousarray(global_h),
        sigma=sigma,
        support_counts=np.ascontiguousarray(supports),
        residual_field=None,
        native=True,
    )
    if enable_residual_spline and len(src64) >= 4:
        mapped_check = warp.map_points(src64)
        err_check = float(np.mean(np.linalg.norm(mapped_check - dst64, axis=1)))
        if err_check > 0.05:
            try:
                warp.residual_field = _fit_apap_tps_native(
                    src64,
                    dst64,
                    regularization=1.0e-5,
                )
            except TransformEstimationError:
                # Match the existing algorithmic policy for degenerate TPS
                # controls: keep the APAP model. Native/runtime errors above
                # this layer are deliberately not caught or rerouted.
                warp.residual_field = None
    return warp


def fit_aanap(
    source: np.ndarray,
    target: np.ndarray,
    *,
    global_homography: np.ndarray | None = None,
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | tuple[float, float] | None = None,
    transition_sigma: float | None = None,
    min_support: int = 4,
    max_controls_per_node: int = 64,
    enable_residual_spline: bool = True,
) -> AANAPWarp:
    """Fit an Adaptive As-Natural-As-Possible (AANAP) warp field.

    Combines Moving DLT homography with global similarity regularization outside
    overlap to preserve natural perspective and prevent shape distortion.
    """
    src, dst = validate_correspondences(source, target, min_points=4, name="AANAP correspondences")
    apap = fit_apap_reference(
        src, dst,
        global_homography=global_homography,
        grid_shape=grid_shape,
        sigma=sigma,
        min_support=min_support,
        max_controls_per_node=max_controls_per_node,
        enable_residual_spline=enable_residual_spline,
    )
    sim = _estimate_similarity(src, dst)
    min_x, min_y = np.min(src, axis=0)
    max_x, max_y = np.max(src, axis=0)
    diag = float(np.linalg.norm([max_x - min_x, max_y - min_y]))
    if transition_sigma is None:
        transition_sigma = max(diag * 0.5, 10.0)

    return AANAPWarp(
        source_points=np.ascontiguousarray(src),
        target_points=np.ascontiguousarray(dst),
        apap_warp=apap,
        global_similarity=np.ascontiguousarray(sim),
        overlap_bounds=(float(min_x), float(min_y), float(max_x), float(max_y)),
        transition_sigma=float(transition_sigma),
    )


def warp_image(
    image: np.ndarray,
    inverse_warp: Callable[[np.ndarray], np.ndarray] | APAPWarp | AANAPWarp,
    dsize: tuple[int, int] | None = None,
    border_value: float = 0.0,
    use_sparse_mesh: bool = True,
    mesh_shape: tuple[int, int] = (33, 33),
) -> tuple[np.ndarray, np.ndarray]:
    """Warp an image using an inverse coordinate mapping field.

    Supports Taichi GPU/AOT accelerated Sparse Mesh Grid Warping to achieve
    sub-millisecond coordinate remapping without intermediate full-resolution
    buffer allocations.

    Args:
        image: Source image array of shape (H, W) or (H, W, C).
        inverse_warp: Mapping function or warp object that maps destination
            coordinates (x_dst, y_dst) to source coordinates (x_src, y_src).
        dsize: (width, height) of the output canvas. If None, uses image's (W, H).
        border_value: Fill value for samples outside the valid image boundary.
        use_sparse_mesh: Whether to use accelerated sparse mesh interpolation.
        mesh_shape: Grid resolution for sparse mesh (default: 33x33).

    Returns:
        (warped, valid_mask): Warped image and boolean validity mask of shape (H, W).
    """
    if use_sparse_mesh:
        from .mesh_warp import warp_image_sparse_mesh
        return warp_image_sparse_mesh(
            image,
            inverse_warp,
            dsize=dsize,
            mesh_shape=mesh_shape,
            border_value=border_value,
        )

    img = np.asarray(image)
    src_h, src_w = img.shape[:2]
    out_w, out_h = (src_w, src_h) if dsize is None else (int(dsize[0]), int(dsize[1]))

    xx, yy = np.meshgrid(np.arange(out_w, dtype=np.float64), np.arange(out_h, dtype=np.float64))
    query = np.column_stack((xx.ravel(), yy.ravel()))

    if hasattr(inverse_warp, "map_points"):
        if len(query) > 65536:
            chunks = []
            for k in range(0, len(query), 65536):
                chunks.append(inverse_warp.map_points(query[k : k + 65536]))
            src_coords = np.vstack(chunks)
        else:
            src_coords = inverse_warp.map_points(query)
    elif callable(inverse_warp):
        if len(query) > 65536:
            chunks = []
            for k in range(0, len(query), 65536):
                chunks.append(inverse_warp(query[k : k + 65536]))
            src_coords = np.vstack(chunks)
        else:
            src_coords = inverse_warp(query)
    else:
        raise TypeError("inverse_warp must be callable or possess map_points")

    map_x = src_coords[:, 0].reshape(out_h, out_w).astype(np.float32)
    map_y = src_coords[:, 1].reshape(out_h, out_w).astype(np.float32)

    valid = (
        (map_x >= 0.0)
        & (map_x <= float(src_w - 1))
        & (map_y >= 0.0)
        & (map_y <= float(src_h - 1))
        & np.isfinite(map_x)
        & np.isfinite(map_y)
    )

    try:
        import cv2

        warped = cv2.remap(
            img.astype(np.float32),
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=border_value,
        )
        return warped, valid
    except Exception:
        x0 = np.clip(np.floor(map_x).astype(np.int64), 0, src_w - 1)
        x1 = np.clip(x0 + 1, 0, src_w - 1)
        y0 = np.clip(np.floor(map_y).astype(np.int64), 0, src_h - 1)
        y1 = np.clip(y0 + 1, 0, src_h - 1)

        wx = map_x - x0.astype(np.float32)
        wy = map_y - y0.astype(np.float32)

        if img.ndim == 2:
            ia = img[y0, x0]
            ib = img[y0, x1]
            ic = img[y1, x0]
            id_ = img[y1, x1]
            top = ia + (ib - ia) * wx
            bot = ic + (id_ - ic) * wx
            warped = top + (bot - top) * wy
            warped[~valid] = border_value
        else:
            wx_3d = wx[..., None]
            wy_3d = wy[..., None]
            ia = img[y0, x0]
            ib = img[y0, x1]
            ic = img[y1, x0]
            id_ = img[y1, x1]
            top = ia + (ib - ia) * wx_3d
            bot = ic + (id_ - ic) * wx_3d
            warped = top + (bot - top) * wy_3d
            warped[~valid] = border_value
        return warped.astype(img.dtype), valid


def align_burst_stack(
    images: Sequence[np.ndarray],
    *,
    reference_index: int = 0,
    method: str = "aanap",
    grid_shape: tuple[int, int] = (4, 4),
    sigma: float | tuple[float, float] | None = None,
    guided_matches: Sequence[tuple[np.ndarray, np.ndarray] | None] | None = None,
    detector: str = "orb",
    max_features: int = 1500,
    reprojection_threshold: float = 3.0,
) -> tuple[list[np.ndarray], list[dict[str, object]]]:
    """Align a burst stack of images to a single reference frame.

    Suitable for multi-frame burst noise reduction, HDR stacking, and
    super-resolution without canvas growth.

    Args:
        images: Sequence of images (all of identical shape HxW or HxWxC).
        reference_index: Index of the reference anchor frame (0-indexed).
        method: Alignment model ('aanap', 'apap', 'tps', or 'homography').
        grid_shape: Moving DLT grid resolution for APAP/AANAP.
        sigma: Kernel bandwidth parameter for local DLT weighting.
        guided_matches: Optional sequence of known ground truth keypoint pairs
            (pts_ref, pts_mov) for each frame to bypass automatic detection.
        detector: Feature detector ('orb' or 'akaze').
        max_features: Maximum keypoints to detect per frame.
        reprojection_threshold: Inlier distance threshold for RANSAC.

    Returns:
        (aligned_stack, reports):
            aligned_stack: List of warped images registered to reference coordinate system.
            reports: Metadata per frame (inliers, rmse, method, status).
    """
    if len(images) == 0:
        return [], []
    if reference_index < 0 or reference_index >= len(images):
        raise ValueError(f"reference_index {reference_index} out of range [0, {len(images)-1}]")

    ref_img = images[reference_index]
    ref_h, ref_w = ref_img.shape[:2]

    aligned_stack: list[np.ndarray] = []
    reports: list[dict[str, object]] = []

    import cv2
    from .tps import fit_tps_checked

    feat = None
    matcher = None
    kp_ref = None
    desc_ref = None

    if guided_matches is None:
        if ref_img.ndim == 3 and ref_img.shape[2] == 3:
            ref_gray = cv2.cvtColor(ref_img.astype(np.float32), cv2.COLOR_BGR2GRAY)
        else:
            ref_gray = ref_img.astype(np.float32)
        ref_u8 = np.clip(ref_gray * 255.0 if ref_gray.max() <= 1.01 else ref_gray, 0, 255).astype(np.uint8)

        if str(detector).lower() == "akaze":
            feat = cv2.AKAZE_create()
        else:
            feat = cv2.ORB_create(nfeatures=max_features)

        kp_ref, desc_ref = feat.detectAndCompute(ref_u8, None)
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    for idx, img in enumerate(images):
        if idx == reference_index:
            aligned_stack.append(img)
            reports.append({
                "frame": idx,
                "is_reference": True,
                "inliers": len(kp_ref) if kp_ref is not None else 0,
                "method": "identity",
                "status": "success",
            })
            continue

        inliers_ref = []
        inliers_mov = []
        H_global = np.eye(3, dtype=np.float64)

        if guided_matches is not None and idx < len(guided_matches) and guided_matches[idx] is not None:
            p_ref, p_mov = guided_matches[idx]
            inliers_ref = np.ascontiguousarray(p_ref, dtype=np.float64)
            inliers_mov = np.ascontiguousarray(p_mov, dtype=np.float64)
            try:
                H_global = estimate_homography(inliers_ref, inliers_mov)
            except Exception:
                H_global = np.eye(3, dtype=np.float64)
        else:
            if img.ndim == 3 and img.shape[2] == 3:
                mov_gray = cv2.cvtColor(img.astype(np.float32), cv2.COLOR_BGR2GRAY)
            else:
                mov_gray = img.astype(np.float32)
            mov_u8 = np.clip(mov_gray * 255.0 if mov_gray.max() <= 1.01 else mov_gray, 0, 255).astype(np.uint8)

            kp_mov, desc_mov = feat.detectAndCompute(mov_u8, None)

            if desc_ref is not None and desc_mov is not None and len(desc_ref) >= 4 and len(desc_mov) >= 4:
                raw_matches = matcher.knnMatch(desc_ref, desc_mov, k=2)
                good_matches = [m for m, n in raw_matches if m.distance < 0.75 * n.distance] if raw_matches else []

                if len(good_matches) >= 4:
                    pts_ref = np.float64([kp_ref[m.queryIdx].pt for m in good_matches])
                    pts_mov = np.float64([kp_mov[m.trainIdx].pt for m in good_matches])

                    H_cand, mask = cv2.findHomography(pts_ref, pts_mov, cv2.RANSAC, reprojection_threshold)
                    if H_cand is not None and mask is not None:
                        keep = mask.ravel() == 1
                        if int(keep.sum()) >= 4:
                            inliers_ref = pts_ref[keep]
                            inliers_mov = pts_mov[keep]
                            H_global = H_cand

        if len(inliers_ref) >= 4:
            m_lower = str(method).lower()
            if m_lower == "tps":
                inv_warp, _ = fit_tps_checked(inliers_ref, inliers_mov, regularization=1e-4)
                used_method = "tps"
            elif m_lower == "aanap":
                inv_warp = fit_aanap(inliers_ref, inliers_mov, global_homography=H_global, grid_shape=grid_shape, sigma=sigma)
                used_method = "aanap"
            elif m_lower == "apap":
                inv_warp = fit_apap_reference(inliers_ref, inliers_mov, global_homography=H_global, grid_shape=grid_shape, sigma=sigma)
                used_method = "apap"
            else:
                inv_warp = lambda pts: project_points(pts, H_global)
                used_method = "homography"

            warped_img, _ = warp_image(img, inv_warp, dsize=(ref_w, ref_h))
            aligned_stack.append(warped_img)
            reports.append({
                "frame": idx,
                "is_reference": False,
                "inliers": len(inliers_ref),
                "method": used_method,
                "status": "success",
            })
        else:
            aligned_stack.append(img)
            reports.append({
                "frame": idx,
                "is_reference": False,
                "inliers": 0,
                "method": "fallback_identity",
                "status": "warning_unaligned",
            })

    return aligned_stack, reports


def align_multi_image_panorama(
    images: Sequence[np.ndarray],
    *,
    grid_layout: tuple[int, int] | None = None,
    method: str = "aanap",
    sub_grid_shape: tuple[int, int] = (4, 4),
    blend: str = "feather",
) -> tuple[np.ndarray, dict[str, object]]:
    """Generic multi-image panorama stitching for single-row or multi-row configurations.

    Supports N > 2 images:
    - If grid_layout is None or (1, N): single-row chain alignment.
    - If grid_layout is (R, C): multi-row 2D grid alignment.

    Args:
        images: Sequence of N input images (HxW or HxWxC).
        grid_layout: (rows, cols) dimensions, or None for sequential single-row.
        method: Alignment model ('aanap', 'apap', or None).
        sub_grid_shape: Moving DLT grid resolution per cell.
        blend: Blending mode ('feather' or 'average').

    Returns:
        (panorama_canvas, info_dict): Composed panorama and alignment diagnostics.
    """
    if len(images) == 0:
        raise ValueError("images sequence cannot be empty")
    if len(images) == 1:
        return images[0], {"status": "single_image", "method": method}

    from ..panorama.stitch import stitch_panorama

    refine_choice = method if str(method).lower() in {"aanap", "apap"} else None

    if grid_layout is None or int(grid_layout[0]) <= 1:
        canvas = stitch_panorama(images, refine=refine_choice, blend=blend)
        return canvas, {
            "status": "success",
            "layout": "single_row",
            "image_count": len(images),
            "method": method,
        }

    rows, cols = int(grid_layout[0]), int(grid_layout[1])
    if rows * cols != len(images):
        raise ValueError(
            f"grid_layout {grid_layout} product {rows*cols} does not match image count {len(images)}"
        )

    row_panoramas = []
    for r in range(rows):
        row_imgs = images[r * cols : (r + 1) * cols]
        if len(row_imgs) == 1:
            row_panoramas.append(row_imgs[0])
        else:
            row_canvas = stitch_panorama(row_imgs, refine=refine_choice, blend=blend)
            row_panoramas.append(row_canvas)

    final_canvas = stitch_panorama(row_panoramas, refine=refine_choice, blend=blend)
    return final_canvas, {
        "status": "success",
        "layout": f"multi_row_{rows}x{cols}",
        "image_count": len(images),
        "method": method,
    }


__all__ = [
    "APAPWarp",
    "AANAPWarp",
    "fit_apap",
    "fit_apap_reference",
    "fit_aanap",
    "warp_image",
    "warp_image_sparse_mesh",
    "compute_sparse_mesh",
    "align_burst_stack",
    "align_multi_image_panorama",
]
