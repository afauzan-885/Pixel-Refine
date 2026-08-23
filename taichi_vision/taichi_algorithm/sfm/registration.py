"""Point-cloud registration, TSDF fusion, and calibrated projection glue.

The repository already contains point-cloud filtering, normals, plane sweep,
triangulation, and surface reconstruction kernels.  This module fills the
remaining orchestration gap with small, bounded reference implementations:

* point-to-plane ICP with a 6-DoF Lie-algebra update;
* chunked TSDF integration for calibrated depth frames;
* explicit camera projection and a quality-gated PnP wrapper.

NumPy remains the default/reference backend.  Explicit ``backend="taichi"``
selects bounded CPU-JIT kernels when imported with ``AOT_MODE=0``; no backend
is silently changed.  PnP delegates to the optional OpenCV reference solver
because the existing public ``solvePnP`` facade is intentionally only a
compatibility stub; unavailable dependencies fail with an actionable error
rather than returning a zero pose.
"""

from dataclasses import dataclass
import math
import os
import importlib
from typing import Any, Sequence

import numpy as np

from ..pipeline_common import PipelineReport, as_float32_matrix, timed_stage, update_stage_output


# Registration is intentionally NumPy by default.  The Taichi kernels below
# are opt-in so importing the SfM family in AOT mode does not initialise a JIT
# runtime or silently switch a caller's backend.  This mirrors the existing
# point-cloud/plane-sweep modules, which only expose JIT kernels in
# ``AOT_MODE=0``.
TAICHI_AVAILABLE = False
ti = None
if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except Exception:
        ti = None


def _normalise_backend(value: str, *, default: str = "numpy") -> str:
    """Validate a backend selector without changing the public default."""

    backend = default if value is None else str(value).strip().lower()
    if backend not in {"numpy", "taichi", "aot", "auto"}:
        raise ValueError("backend must be one of 'numpy', 'taichi', 'aot', or 'auto'")
    # ``auto`` remains conservative for these new kernels: only an explicit
    # ``backend='taichi'`` is allowed to opt into the JIT path.
    if backend == "auto":
        return "numpy"
    return backend


def _ensure_taichi_runtime() -> str:
    """Initialise a CPU JIT runtime when the application has not done so.

    ``AOT_MODE=0`` makes the Taichi module importable but does not guarantee
    that ``ti.init`` has run (the desktop AOT bridge can initialise its own
    renderer instead).  Explicit native callers therefore get a deterministic
    CPU runtime, while an already-initialised runtime is reused unchanged.
    The returned label is used in reports so a GPU/other runtime is not
    misrepresented as a CPU result.
    """

    if not TAICHI_AVAILABLE:
        raise RuntimeError(
            "backend='taichi' requires AOT_MODE=0 and an installed Taichi runtime"
        )
    runtime = ti.lang.impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        ti.init(arch=ti.cpu)
    try:
        arch = str(ti.lang.impl.get_runtime().prog.config().arch).lower()
    except Exception:
        arch = "unknown"
    return "taichi-cpu-jit" if "x64" in arch or "cpu" in arch else f"taichi-{arch}-jit"


if TAICHI_AVAILABLE:

    @ti.func
    def _round_to_nearest_even(value):
        """Match NumPy ``rint`` for projected pixel coordinates.

        The reference TSDF path uses ``np.rint`` (ties-to-even).  The former
        ``floor(value + 0.5)`` expression rounded half-way values away from
        zero, so otherwise identical JIT/AOT and NumPy integrations could
        sample adjacent depth pixels at exact half-pixel projections.  Keep
        this helper backend-portable: it uses only floor, scalar casts, and a
        low-bit parity check (no Python round or unsupported dynamic helper).
        """

        lower_f = ti.floor(value)
        lower = ti.cast(lower_f, ti.i32)
        fraction = value - lower_f
        odd = (lower & 1) != 0
        # Keep boolean composition out of bitwise operators: Vulkan SPIR-V
        # validation rejects OpBitwiseAnd when Taichi lowers bool operands.
        use_upper = ti.select(
            fraction > 0.5,
            True,
            ti.select(fraction == 0.5, odd, False),
        )
        return ti.select(use_upper, lower + 1, lower)

    @ti.kernel
    def _icp_accumulate_kernel(
        source: ti.types.ndarray(dtype=ti.f32, ndim=2),
        target: ti.types.ndarray(dtype=ti.f32, ndim=2),
        normals: ti.types.ndarray(dtype=ti.f32, ndim=2),
        rotation: ti.types.ndarray(dtype=ti.f32, ndim=2),
        translation: ti.types.ndarray(dtype=ti.f32, ndim=1),
        max_distance_sq: ti.f32,
        jtj: ti.types.ndarray(dtype=ti.f32, ndim=2),
        jtr: ti.types.ndarray(dtype=ti.f32, ndim=1),
        residuals: ti.types.ndarray(dtype=ti.f32, ndim=1),
        correspondences: ti.types.ndarray(dtype=ti.i32, ndim=1),
    ):
        """Bounded brute-force nearest-neighbour and normal-equation kernel.

        The kernel deliberately computes one correspondence per source point
        and accumulates a 6x6 system.  A host-side 6x6 solve then performs the
        Lie update, keeping temporary device memory O(N + M) rather than
        materialising an N-by-M distance matrix.
        """

        n_source = source.shape[0]
        n_target = target.shape[0]
        for i in range(n_source):
            px = rotation[0, 0] * source[i, 0] + rotation[0, 1] * source[i, 1] + rotation[0, 2] * source[i, 2] + translation[0]
            py = rotation[1, 0] * source[i, 0] + rotation[1, 1] * source[i, 1] + rotation[1, 2] * source[i, 2] + translation[1]
            pz = rotation[2, 0] * source[i, 0] + rotation[2, 1] * source[i, 1] + rotation[2, 2] * source[i, 2] + translation[2]
            best_sq = ti.f32(1e30)
            best_j = -1
            for j in range(n_target):
                dx = px - target[j, 0]
                dy = py - target[j, 1]
                dz = pz - target[j, 2]
                distance_sq = dx * dx + dy * dy + dz * dz
                if distance_sq < best_sq:
                    best_sq = distance_sq
                    best_j = j
            if best_j < 0 or best_sq > max_distance_sq:
                correspondences[i] = -1
                residuals[i] = 0.0
                continue

            nx = normals[best_j, 0]
            ny = normals[best_j, 1]
            nz = normals[best_j, 2]
            # n dot (target - p)
            residual = nx * (target[best_j, 0] - px) + ny * (target[best_j, 1] - py) + nz * (target[best_j, 2] - pz)
            # [p x n, n] is the point-to-plane Jacobian used by the NumPy path.
            jac0 = py * nz - pz * ny
            jac1 = pz * nx - px * nz
            jac2 = px * ny - py * nx
            jac3 = nx
            jac4 = ny
            jac5 = nz
            j0 = jac0
            j1 = jac1
            j2 = jac2
            j3 = jac3
            j4 = jac4
            j5 = jac5
            # Explicit 6x6 accumulation avoids unsupported dynamic local arrays
            # on older Taichi CPU backends.
            ti.atomic_add(jtr[0], j0 * residual)
            ti.atomic_add(jtr[1], j1 * residual)
            ti.atomic_add(jtr[2], j2 * residual)
            ti.atomic_add(jtr[3], j3 * residual)
            ti.atomic_add(jtr[4], j4 * residual)
            ti.atomic_add(jtr[5], j5 * residual)
            ti.atomic_add(jtj[0, 0], j0 * j0)
            ti.atomic_add(jtj[0, 1], j0 * j1)
            ti.atomic_add(jtj[0, 2], j0 * j2)
            ti.atomic_add(jtj[0, 3], j0 * j3)
            ti.atomic_add(jtj[0, 4], j0 * j4)
            ti.atomic_add(jtj[0, 5], j0 * j5)
            ti.atomic_add(jtj[1, 0], j1 * j0)
            ti.atomic_add(jtj[1, 1], j1 * j1)
            ti.atomic_add(jtj[1, 2], j1 * j2)
            ti.atomic_add(jtj[1, 3], j1 * j3)
            ti.atomic_add(jtj[1, 4], j1 * j4)
            ti.atomic_add(jtj[1, 5], j1 * j5)
            ti.atomic_add(jtj[2, 0], j2 * j0)
            ti.atomic_add(jtj[2, 1], j2 * j1)
            ti.atomic_add(jtj[2, 2], j2 * j2)
            ti.atomic_add(jtj[2, 3], j2 * j3)
            ti.atomic_add(jtj[2, 4], j2 * j4)
            ti.atomic_add(jtj[2, 5], j2 * j5)
            ti.atomic_add(jtj[3, 0], j3 * j0)
            ti.atomic_add(jtj[3, 1], j3 * j1)
            ti.atomic_add(jtj[3, 2], j3 * j2)
            ti.atomic_add(jtj[3, 3], j3 * j3)
            ti.atomic_add(jtj[3, 4], j3 * j4)
            ti.atomic_add(jtj[3, 5], j3 * j5)
            ti.atomic_add(jtj[4, 0], j4 * j0)
            ti.atomic_add(jtj[4, 1], j4 * j1)
            ti.atomic_add(jtj[4, 2], j4 * j2)
            ti.atomic_add(jtj[4, 3], j4 * j3)
            ti.atomic_add(jtj[4, 4], j4 * j4)
            ti.atomic_add(jtj[4, 5], j4 * j5)
            ti.atomic_add(jtj[5, 0], j5 * j0)
            ti.atomic_add(jtj[5, 1], j5 * j1)
            ti.atomic_add(jtj[5, 2], j5 * j2)
            ti.atomic_add(jtj[5, 3], j5 * j3)
            ti.atomic_add(jtj[5, 4], j5 * j4)
            ti.atomic_add(jtj[5, 5], j5 * j5)
            correspondences[i] = best_j
            residuals[i] = residual

    @ti.kernel
    def _tsdf_integrate_kernel(
        depth: ti.types.ndarray(dtype=ti.f32, ndim=2),
        intrinsics: ti.types.ndarray(dtype=ti.f32, ndim=2),
        rotation: ti.types.ndarray(dtype=ti.f32, ndim=2),
        translation: ti.types.ndarray(dtype=ti.f32, ndim=1),
        origin: ti.types.ndarray(dtype=ti.f32, ndim=1),
        voxel_size: ti.f32,
        truncation: ti.f32,
        max_weight: ti.i32,
        tsdf: ti.types.ndarray(dtype=ti.f32, ndim=3),
        weights: ti.types.ndarray(dtype=ti.i32, ndim=3),
    ):
        """Integrate one frame; each voxel is an independent bounded update."""

        nz, ny, nx = tsdf.shape[0], tsdf.shape[1], tsdf.shape[2]
        image_h, image_w = depth.shape[0], depth.shape[1]
        for z, y, x in ti.ndrange(nz, ny, nx):
            wx = origin[0] + (ti.cast(x, ti.f32) + 0.5) * voxel_size
            wy = origin[1] + (ti.cast(y, ti.f32) + 0.5) * voxel_size
            wz = origin[2] + (ti.cast(z, ti.f32) + 0.5) * voxel_size
            cx = rotation[0, 0] * wx + rotation[0, 1] * wy + rotation[0, 2] * wz + translation[0]
            cy = rotation[1, 0] * wx + rotation[1, 1] * wy + rotation[1, 2] * wz + translation[1]
            cz = rotation[2, 0] * wx + rotation[2, 1] * wy + rotation[2, 2] * wz + translation[2]
            if cz <= 1e-8:
                continue
            u = intrinsics[0, 0] * cx / cz + intrinsics[0, 2]
            v = intrinsics[1, 1] * cy / cz + intrinsics[1, 2]
            # Keep JIT/AOT sampling identical to the NumPy reference's
            # ``np.rint`` contract, including ties-to-even.
            px = _round_to_nearest_even(u)
            py = _round_to_nearest_even(v)
            # Keep bounds checks as nested scalar branches.  Some older
            # Taichi Vulkan/OpenGL lowerings combine Python ``or`` chains
            # into boolean ``OpBitwiseAnd`` instructions, which SPIR-V
            # rejects even though the source expression is logically valid.
            if px < 0:
                continue
            if px >= image_w:
                continue
            if py < 0:
                continue
            if py >= image_h:
                continue
            measured = depth[py, px]
            # Depth frames are finite-validated on the host before launch;
            # checking positivity here also rejects the invalid-value sentinel
            # used by depth sensors without relying on backend-specific helpers.
            if measured <= 0.0:
                continue
            signed_distance = measured - cz
            if ti.abs(signed_distance) > truncation:
                continue
            value = ti.max(-1.0, ti.min(1.0, signed_distance / truncation))
            old_weight = weights[z, y, x]
            new_weight = ti.min(old_weight + 1, max_weight)
            if new_weight > 0:
                tsdf[z, y, x] = (tsdf[z, y, x] * ti.cast(old_weight, ti.f32) + value) / ti.cast(new_weight, ti.f32)
                weights[z, y, x] = new_weight


@dataclass
class ICPResult:
    """Point-to-plane ICP result and quality diagnostics."""

    success: bool
    transform: np.ndarray
    correspondences: np.ndarray
    residuals: np.ndarray
    fitness: float
    converged: bool
    iterations: int
    report: PipelineReport


@dataclass
class TSDFResult:
    """A bounded TSDF volume and integration report."""

    tsdf: np.ndarray
    weights: np.ndarray
    origin: np.ndarray
    voxel_size: float
    report: PipelineReport


@dataclass
class PnPResult:
    """Pose returned by :func:`solve_pnp_checked`."""

    success: bool
    rotation: np.ndarray
    translation: np.ndarray
    inlier_mask: np.ndarray
    reprojection_error_px: np.ndarray
    report: PipelineReport


def _points3(value: Any, *, name: str, allow_empty: bool = False) -> np.ndarray:
    array = np.ascontiguousarray(value, dtype=np.float64)
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError(f"{name} must have shape (N, 3), got {array.shape}")
    if not allow_empty and len(array) == 0:
        raise ValueError(f"{name} must not be empty")
    if not np.isfinite(array).all():
        raise ValueError(f"{name} contains non-finite values")
    return array


def _normals3(value: Any, *, name: str) -> np.ndarray:
    normals = _points3(value, name=name)
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    if np.any(lengths < 1e-12):
        raise ValueError(f"{name} contains zero-length normals")
    return normals / lengths


def _as_transform(value: Any, *, name: str = "transform") -> np.ndarray:
    transform = np.asarray(value, dtype=np.float64)
    if transform.shape != (4, 4) or not np.isfinite(transform).all():
        raise ValueError(f"{name} must be finite shape (4, 4)")
    if not np.allclose(transform[3], [0.0, 0.0, 0.0, 1.0], atol=1e-6):
        raise ValueError(f"{name} last row must be [0, 0, 0, 1]")
    rotation = transform[:3, :3]
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-3) or np.linalg.det(rotation) <= 0:
        raise ValueError(f"{name} rotation must be a proper SO(3) matrix")
    return np.ascontiguousarray(transform)


def _rodrigues(vector: np.ndarray) -> np.ndarray:
    """Small-angle Rodrigues update without an external geometry package."""

    vector = np.asarray(vector, dtype=np.float64).reshape(3)
    theta = float(np.linalg.norm(vector))
    skew = np.array(
        [[0.0, -vector[2], vector[1]], [vector[2], 0.0, -vector[0]], [-vector[1], vector[0], 0.0]],
        dtype=np.float64,
    )
    if theta < 1e-12:
        return np.eye(3) + skew
    scale = math.sin(theta) / theta
    scale2 = (1.0 - math.cos(theta)) / (theta * theta)
    return np.eye(3) + scale * skew + scale2 * (skew @ skew)


def _nearest_indices(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Nearest neighbours with scipy acceleration and a deterministic fallback."""

    try:
        from scipy.spatial import cKDTree

        distances, indices = cKDTree(target).query(source, k=1)
        return np.asarray(indices, dtype=np.int32), np.asarray(distances, dtype=np.float64)
    except Exception:
        # This fallback is intentionally chunked to avoid constructing an
        # N_source x N_target distance matrix for a large cloud.
        indices = np.empty(len(source), dtype=np.int32)
        distances = np.empty(len(source), dtype=np.float64)
        # Bound both dimensions.  A single 16k x 250k distance matrix would
        # otherwise exceed tens of gigabytes when scipy is unavailable.
        source_chunk = max(1, min(512, len(source)))
        target_chunk = max(1, min(2048, len(target)))
        for start in range(0, len(source), source_chunk):
            stop = min(len(source), start + source_chunk)
            source_block = source[start:stop]
            best_squared = np.full(stop - start, np.inf, dtype=np.float64)
            best_indices = np.zeros(stop - start, dtype=np.int32)
            for target_start in range(0, len(target), target_chunk):
                target_stop = min(len(target), target_start + target_chunk)
                delta = source_block[:, None, :] - target[target_start:target_stop][None, :, :]
                squared = np.sum(delta * delta, axis=2)
                local = np.argmin(squared, axis=1)
                local_squared = squared[np.arange(stop - start), local]
                improved = local_squared < best_squared
                best_squared[improved] = local_squared[improved]
                best_indices[improved] = (target_start + local[improved]).astype(np.int32)
            indices[start:stop] = best_indices
            distances[start:stop] = np.sqrt(best_squared)
        return indices, distances


def _point_to_plane_icp_native(
    source: np.ndarray,
    target: np.ndarray,
    normals: np.ndarray,
    transform: np.ndarray,
    *,
    selected_backend: str,
    max_iterations: int,
    max_correspondence_distance: float,
    convergence_tolerance: float,
    min_correspondences: int,
    max_kernel_pairs: int,
) -> ICPResult:
    """Run ICP with a bounded native accumulator.

    ``selected_backend`` is deliberately explicit: ``taichi`` invokes the
    family-local JIT kernel while ``aot`` dispatches the target-qualified
    ``sfm_registration`` graph.  The host-side least-squares update is shared
    because it is a small global solve and keeps both paths numerically
    identical.  An unavailable AOT graph raises an actionable error instead of
    silently changing the requested backend.
    """

    if selected_backend not in {"taichi", "aot"}:
        raise ValueError("selected_backend must be 'taichi' or 'aot'")
    if selected_backend == "taichi":
        backend_label = _ensure_taichi_runtime()
    else:
        backend_label = "aot"
    pair_count = int(len(source)) * int(len(target))
    if pair_count > int(max_kernel_pairs):
        raise MemoryError(
            f"Taichi ICP brute-force correspondence budget exceeded ({pair_count} pairs, "
            f"limit {int(max_kernel_pairs)})"
        )

    source32 = np.ascontiguousarray(source, dtype=np.float32)
    target32 = np.ascontiguousarray(target, dtype=np.float32)
    normals32 = np.ascontiguousarray(normals, dtype=np.float32)
    report = PipelineReport("icp_point_to_plane", backend=backend_label)
    report.metrics.update(
        {
            "n_source": float(len(source)),
            "n_target": float(len(target)),
            "kernel_pairs": float(pair_count),
        }
    )
    previous_rmse = float("inf")
    converged = False
    last_indices = np.empty(0, dtype=np.int32)
    last_residuals = np.empty(0, dtype=np.float64)
    last_fitness = 0.0
    iterations = 0
    stage_index = len(report.stages)
    with timed_stage(report, "icp_iterations"):
        for iteration in range(int(max_iterations)):
            iterations = iteration + 1
            source32_out = source32  # keep ndarray storage stable for the JIT call
            target32_out = target32
            normals32_out = normals32
            rotation32 = np.ascontiguousarray(transform[:3, :3], dtype=np.float32)
            translation32 = np.ascontiguousarray(transform[:3, 3], dtype=np.float32)
            jtj = np.zeros((6, 6), dtype=np.float32)
            jtr = np.zeros(6, dtype=np.float32)
            residuals = np.zeros(len(source), dtype=np.float32)
            correspondences = np.full(len(source), -1, dtype=np.int32)
            if selected_backend == "taichi":
                _icp_accumulate_kernel(
                    source32_out,
                    target32_out,
                    normals32_out,
                    rotation32,
                    translation32,
                    np.float32(float(max_correspondence_distance) ** 2),
                    jtj,
                    jtr,
                    residuals,
                    correspondences,
                )
            else:
                try:
                    from ..aot_api.research import sfm_icp_accumulate_aot

                    accumulated = sfm_icp_accumulate_aot(
                        source32_out,
                        target32_out,
                        normals32_out,
                        rotation32,
                        translation32,
                        max_distance_sq=float(max_correspondence_distance) ** 2,
                    )
                except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                    raise NotImplementedError(
                        "point-to-plane ICP AOT requires the target-qualified "
                        "sfm_registration accumulator artifact"
                    ) from exc
                jtj[...] = np.ascontiguousarray(accumulated["jtj"], dtype=np.float32)
                jtr[...] = np.ascontiguousarray(accumulated["jtr"], dtype=np.float32)
                residuals[...] = np.ascontiguousarray(accumulated["residuals"], dtype=np.float32)
                correspondences[...] = np.ascontiguousarray(accumulated["correspondences"], dtype=np.int32)
            valid = correspondences >= 0
            n_valid = int(np.count_nonzero(valid))
            if n_valid < int(min_correspondences):
                break
            # Solve the direct 6-column system on the host, matching the
            # NumPy reference's conditioning.  The kernel still performs the
            # expensive bounded nearest-neighbour search; solving J^T J
            # directly here would square the condition number and destabilise
            # planar/radial clouds even when the direct least-squares solve is
            # well behaved.
            transformed = (transform[:3, :3] @ source.T).T + transform[:3, 3]
            matched_normals = normals[correspondences[valid]]
            points = transformed[valid]
            jacobian = np.concatenate([np.cross(points, matched_normals), matched_normals], axis=1)
            direct_residuals = np.sum(matched_normals * (target[correspondences[valid]] - points), axis=1)
            try:
                update, _, _, _ = np.linalg.lstsq(jacobian, direct_residuals, rcond=None)
            except np.linalg.LinAlgError:
                break
            if not np.isfinite(update).all():
                break
            delta_rotation = _rodrigues(update[:3])
            delta_transform = np.eye(4, dtype=np.float64)
            delta_transform[:3, :3] = delta_rotation
            delta_transform[:3, 3] = update[3:]
            transform = delta_transform @ transform
            valid_residuals = direct_residuals.astype(np.float64)
            rmse = float(np.sqrt(np.mean(valid_residuals * valid_residuals))) if n_valid else float("inf")
            last_indices = correspondences[valid].astype(np.int32)
            last_residuals = valid_residuals
            last_fitness = float(n_valid / max(len(source), 1))
            if abs(previous_rmse - rmse) <= float(convergence_tolerance) or float(np.linalg.norm(update)) <= float(convergence_tolerance):
                converged = True
                break
            previous_rmse = rmse
    update_stage_output(report, stage_index, transform)
    success = bool(len(last_residuals) >= int(min_correspondences) and np.isfinite(last_residuals).all())
    if not success:
        report.add_warning("ICP did not find enough valid point-to-plane correspondences")
    if not converged:
        report.add_warning("ICP reached its iteration/conditioning limit before convergence")
    report.metrics.update(
        {
            "iterations": float(iterations),
            "fitness": float(last_fitness),
            "rmse": float(np.sqrt(np.mean(last_residuals * last_residuals))) if len(last_residuals) else float("inf"),
        }
    )
    return ICPResult(
        success=success,
        transform=transform.astype(np.float64),
        correspondences=last_indices,
        residuals=last_residuals.astype(np.float32),
        fitness=float(last_fitness),
        converged=converged,
        iterations=iterations,
        report=report,
    )


def point_to_plane_icp(
    source_points: Any,
    target_points: Any,
    target_normals: Any,
    *,
    init_transform: Any | None = None,
    max_iterations: int = 30,
    max_correspondence_distance: float = 0.1,
    convergence_tolerance: float = 1e-6,
    min_correspondences: int = 6,
    max_points: int = 250_000,
    backend: str = "numpy",
    max_kernel_pairs: int = 25_000_000,
) -> ICPResult:
    """Align ``source_points`` to ``target_points`` using point-to-plane ICP.

    The nearest-neighbour search is bounded by ``max_points`` because the
    fallback search is quadratic.  No downsampling is performed implicitly;
    callers should use :func:`sfm.point_cloud.preprocess_point_cloud` first.
    The returned transform maps source coordinates into target coordinates.
    """

    backend_name = _normalise_backend(backend)
    source = _points3(source_points, name="source_points")
    target = _points3(target_points, name="target_points")
    normals = _normals3(target_normals, name="target_normals")
    if len(target) != len(normals):
        raise ValueError("target_points and target_normals lengths differ")
    if len(source) > int(max_points) or len(target) > int(max_points):
        raise MemoryError(
            f"ICP point budget exceeded ({len(source)} source/{len(target)} target, "
            f"limit {int(max_points)})"
        )
    if int(max_iterations) < 1 or float(max_correspondence_distance) <= 0:
        raise ValueError("invalid ICP iteration/distance parameters")
    if int(min_correspondences) < 6:
        raise ValueError("min_correspondences must be at least 6 for a 6-DoF update")
    if float(convergence_tolerance) <= 0:
        raise ValueError("convergence_tolerance must be positive")
    if int(max_kernel_pairs) < 1:
        raise ValueError("max_kernel_pairs must be positive")

    transform = np.eye(4, dtype=np.float64) if init_transform is None else _as_transform(init_transform)
    if backend_name in {"taichi", "aot"}:
        return _point_to_plane_icp_native(
            source,
            target,
            normals,
            transform,
            selected_backend=backend_name,
            max_iterations=int(max_iterations),
            max_correspondence_distance=float(max_correspondence_distance),
            convergence_tolerance=float(convergence_tolerance),
            min_correspondences=int(min_correspondences),
            max_kernel_pairs=int(max_kernel_pairs),
        )
    report = PipelineReport("icp_point_to_plane", backend="numpy-reference")
    report.metrics.update({"n_source": float(len(source)), "n_target": float(len(target))})
    previous_rmse = float("inf")
    converged = False
    last_indices = np.empty(0, dtype=np.int32)
    last_residuals = np.empty(0, dtype=np.float64)
    last_fitness = 0.0
    iterations = 0

    stage_index = len(report.stages)
    with timed_stage(report, "icp_iterations"):
        for iteration in range(int(max_iterations)):
            iterations = iteration + 1
            rotation = transform[:3, :3]
            translation = transform[:3, 3]
            transformed = (rotation @ source.T).T + translation
            indices, distances = _nearest_indices(transformed, target)
            valid = np.isfinite(distances) & (distances <= float(max_correspondence_distance))
            if int(np.count_nonzero(valid)) < int(min_correspondences):
                break
            matched = target[indices[valid]]
            matched_normals = normals[indices[valid]]
            points = transformed[valid]
            residuals = np.sum(matched_normals * (matched - points), axis=1)
            # Linearized point-to-plane equation: n^T (w x p + v) = r.
            jacobian = np.concatenate([np.cross(points, matched_normals), matched_normals], axis=1)
            try:
                update, _, _, _ = np.linalg.lstsq(jacobian, residuals, rcond=None)
            except np.linalg.LinAlgError:
                break
            if not np.isfinite(update).all():
                break
            delta_rotation = _rodrigues(update[:3])
            delta_transform = np.eye(4, dtype=np.float64)
            delta_transform[:3, :3] = delta_rotation
            delta_transform[:3, 3] = update[3:]
            transform = delta_transform @ transform
            rmse = float(np.sqrt(np.mean(residuals * residuals))) if len(residuals) else float("inf")
            last_indices = indices[valid].astype(np.int32)
            last_residuals = residuals.astype(np.float64)
            last_fitness = float(np.mean(valid))
            if abs(previous_rmse - rmse) <= float(convergence_tolerance) or float(np.linalg.norm(update)) <= float(convergence_tolerance):
                converged = True
                break
            previous_rmse = rmse
    update_stage_output(report, stage_index, transform)

    if len(last_residuals) >= int(min_correspondences) and np.isfinite(last_residuals).all():
        success = True
    else:
        success = False
        report.add_warning("ICP did not find enough valid point-to-plane correspondences")
    report.metrics.update(
        {
            "iterations": float(iterations),
            "fitness": float(last_fitness),
            "rmse": float(np.sqrt(np.mean(last_residuals * last_residuals))) if len(last_residuals) else float("inf"),
        }
    )
    if not converged:
        report.add_warning("ICP reached its iteration/conditioning limit before convergence")
    return ICPResult(
        success=success,
        transform=transform.astype(np.float64),
        correspondences=last_indices,
        residuals=last_residuals.astype(np.float32),
        fitness=float(last_fitness),
        converged=converged,
        iterations=iterations,
        report=report,
    )


def _validate_depth_frames(
    depth_images: Sequence[Any],
    intrinsics: Sequence[Any],
    poses_world_to_camera: Sequence[Any],
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    if not depth_images:
        raise ValueError("depth_images must contain at least one frame")
    if not (len(depth_images) == len(intrinsics) == len(poses_world_to_camera)):
        raise ValueError("depth images, intrinsics, and poses must have equal lengths")
    images: list[np.ndarray] = []
    matrices: list[np.ndarray] = []
    poses: list[np.ndarray] = []
    shape: tuple[int, int] | None = None
    for index, (depth, K, pose) in enumerate(zip(depth_images, intrinsics, poses_world_to_camera)):
        image = np.ascontiguousarray(depth, dtype=np.float32)
        if image.ndim != 2 or image.size == 0:
            raise ValueError(f"depth_images[{index}] must be non-empty HxW")
        if not np.isfinite(image).all():
            raise ValueError(f"depth_images[{index}] contains non-finite values")
        if shape is None:
            shape = image.shape
        elif image.shape != shape:
            raise ValueError("all depth images must have the same shape")
        matrices.append(np.asarray(as_float32_matrix(K, (3, 3), name=f"intrinsics[{index}]"), dtype=np.float64))
        if matrices[-1][0, 0] <= 0 or matrices[-1][1, 1] <= 0:
            raise ValueError("intrinsic focal lengths must be positive")
        poses.append(_as_transform(pose, name=f"poses_world_to_camera[{index}]"))
        images.append(image)
    return images, matrices, poses


def _integrate_tsdf_native(
    images: list[np.ndarray],
    matrices: list[np.ndarray],
    poses: list[np.ndarray],
    *,
    voxel_size: float,
    truncation: float,
    origin: np.ndarray,
    shape: tuple[int, int, int],
    max_voxels: int,
    selected_backend: str,
) -> TSDFResult:
    """Integrate frames using one bounded native kernel launch per frame."""

    if selected_backend not in {"taichi", "aot"}:
        raise ValueError("selected_backend must be 'taichi' or 'aot'")
    backend_label = _ensure_taichi_runtime() if selected_backend == "taichi" else "aot"
    voxel_count = int(np.prod(shape, dtype=np.int64))
    if voxel_count > int(max_voxels):
        raise MemoryError(f"TSDF grid has {voxel_count} voxels, limit is {int(max_voxels)}")

    tsdf = np.ones(shape, dtype=np.float32)
    # Taichi CPU kernels use i32 accumulation for broad backend support; the
    # public result remains uint16, matching the NumPy/reference contract.
    weights_i32 = np.zeros(shape, dtype=np.int32)
    origin32 = np.ascontiguousarray(origin, dtype=np.float32)
    report = PipelineReport("tsdf_integrate", backend=backend_label)
    report.metrics.update(
        {
            "n_frames": float(len(images)),
            "grid_voxels": float(voxel_count),
            "estimated_bytes": float(voxel_count * (np.dtype(np.float32).itemsize + np.dtype(np.int32).itemsize)),
        }
    )
    integrated_before = weights_i32.copy()
    stage_index = len(report.stages)
    with timed_stage(report, "tsdf_frames"):
        for image, K, pose in zip(images, matrices, poses):
            if selected_backend == "taichi":
                _tsdf_integrate_kernel(
                    np.ascontiguousarray(image, dtype=np.float32),
                    np.ascontiguousarray(K, dtype=np.float32),
                    np.ascontiguousarray(pose[:3, :3], dtype=np.float32),
                    np.ascontiguousarray(pose[:3, 3], dtype=np.float32),
                    origin32,
                    np.float32(voxel_size),
                    np.float32(truncation),
                    np.int32(np.iinfo(np.uint16).max),
                    tsdf,
                    weights_i32,
                )
            else:
                try:
                    from ..aot_api.research import sfm_tsdf_integrate_aot

                    accumulated = sfm_tsdf_integrate_aot(
                        image,
                        K,
                        pose[:3, :3],
                        pose[:3, 3],
                        origin,
                        tsdf,
                        weights_i32,
                        voxel_size=float(voxel_size),
                        truncation=float(truncation),
                        max_weight=int(np.iinfo(np.uint16).max),
                    )
                except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                    raise NotImplementedError(
                        "TSDF AOT requires the target-qualified sfm_registration "
                        "integration artifact"
                    ) from exc
                tsdf[...] = np.ascontiguousarray(accumulated["tsdf"], dtype=np.float32)
                weights_i32[...] = np.ascontiguousarray(accumulated["weights"], dtype=np.int32)
    weights = np.clip(weights_i32, 0, np.iinfo(np.uint16).max).astype(np.uint16)
    integrated = int(np.sum(weights_i32 - integrated_before, dtype=np.int64))
    update_stage_output(report, stage_index, tsdf)
    report.metrics.update(
        {
            "integrated_samples": float(integrated),
            "observed_voxel_fraction": float(np.mean(weights > 0)),
        }
    )
    return TSDFResult(
        tsdf=tsdf,
        weights=weights,
        origin=origin.astype(np.float32),
        voxel_size=float(voxel_size),
        report=report,
    )


def integrate_tsdf(
    depth_images: Sequence[Any],
    intrinsics: Sequence[Any],
    poses_world_to_camera: Sequence[Any],
    *,
    voxel_size: float = 0.02,
    truncation: float = 0.08,
    origin: Any = (0.0, 0.0, 0.0),
    grid_shape: tuple[int, int, int] = (128, 128, 128),
    max_voxels: int = 256 ** 3,
    chunk_voxels: int = 1_000_000,
    backend: str = "numpy",
) -> TSDFResult:
    """Integrate calibrated depth frames into a bounded TSDF volume.

    ``poses_world_to_camera`` use ``X_camera = R @ X_world + t``.  The volume
    layout is ``(z, y, x)`` and ``origin`` is the world-space corner of voxel
    ``(0, 0, 0)``.  A chunked projection loop keeps peak temporary memory
    bounded independently of the total voxel count.
    """

    backend_name = _normalise_backend(backend)
    if not np.isfinite(voxel_size) or float(voxel_size) <= 0:
        raise ValueError("voxel_size must be positive")
    if not np.isfinite(truncation) or float(truncation) <= 0:
        raise ValueError("truncation must be positive")
    if len(grid_shape) != 3 or any(int(value) < 1 for value in grid_shape):
        raise ValueError("grid_shape must contain three positive dimensions")
    shape = tuple(int(value) for value in grid_shape)
    voxel_count = int(np.prod(shape, dtype=np.int64))
    if voxel_count > int(max_voxels):
        raise MemoryError(f"TSDF grid has {voxel_count} voxels, limit is {int(max_voxels)}")
    if int(chunk_voxels) < 1:
        raise ValueError("chunk_voxels must be positive")
    origin_array = np.ascontiguousarray(origin, dtype=np.float64).reshape(-1)
    if origin_array.shape != (3,) or not np.isfinite(origin_array).all():
        raise ValueError("origin must be finite shape (3,)")

    images, matrices, poses = _validate_depth_frames(depth_images, intrinsics, poses_world_to_camera)
    if backend_name in {"taichi", "aot"}:
        return _integrate_tsdf_native(
            images,
            matrices,
            poses,
            voxel_size=float(voxel_size),
            truncation=float(truncation),
            origin=origin_array,
            shape=shape,
            max_voxels=int(max_voxels),
            selected_backend=backend_name,
        )
    report = PipelineReport("tsdf_integrate", backend="numpy-reference")
    report.metrics.update(
        {
            "n_frames": float(len(images)),
            "grid_voxels": float(voxel_count),
            "estimated_bytes": float(voxel_count * (np.dtype(np.float32).itemsize + np.dtype(np.uint16).itemsize)),
        }
    )
    # float32 TSDF and uint16 weights are sufficient for the bounded reference
    # path and keep the volume below 6 bytes/voxel (including alignment).
    tsdf = np.ones(shape, dtype=np.float32)
    weights = np.zeros(shape, dtype=np.uint16)
    nx, ny, nz = shape[2], shape[1], shape[0]
    flat_total = voxel_count
    chunk_size = min(int(chunk_voxels), flat_total)
    integrated = 0
    stage_index = len(report.stages)
    with timed_stage(report, "tsdf_frames"):
        for image, K, pose in zip(images, matrices, poses):
            rotation = pose[:3, :3]
            translation = pose[:3, 3]
            for start in range(0, flat_total, chunk_size):
                indices = np.arange(start, min(flat_total, start + chunk_size), dtype=np.int64)
                z_idx = indices // (ny * nx)
                rem = indices - z_idx * ny * nx
                y_idx = rem // nx
                x_idx = rem - y_idx * nx
                world = origin_array + float(voxel_size) * (
                    np.stack([x_idx, y_idx, z_idx], axis=1).astype(np.float64) + 0.5
                )
                camera = (rotation @ world.T).T + translation
                depth = camera[:, 2]
                valid = np.isfinite(depth) & (depth > 1e-8)
                image_h, image_w = image.shape
                projected = np.zeros((len(world), 2), dtype=np.float64)
                if np.any(valid):
                    image_points = (K @ camera[valid].T).T
                    projected[valid] = image_points[:, :2] / image_points[:, 2:3]
                px = np.rint(projected[:, 0]).astype(np.int64)
                py = np.rint(projected[:, 1]).astype(np.int64)
                valid &= (px >= 0) & (px < image_w) & (py >= 0) & (py < image_h)
                if not np.any(valid):
                    continue
                measured = np.zeros(len(world), dtype=np.float64)
                measured[valid] = image[py[valid], px[valid]]
                valid &= np.isfinite(measured) & (measured > 0.0)
                signed_distance = measured - depth
                valid &= np.abs(signed_distance) <= float(truncation)
                if not np.any(valid):
                    continue
                values = np.clip(signed_distance[valid] / float(truncation), -1.0, 1.0).astype(np.float32)
                flat_tsdf = tsdf.reshape(-1)
                flat_weights = weights.reshape(-1)
                flat_id = indices[valid]
                old_weight = flat_weights[flat_id].astype(np.float32)
                new_weight = np.minimum(old_weight + 1.0, np.iinfo(np.uint16).max)
                flat_tsdf[flat_id] = (flat_tsdf[flat_id] * old_weight + values) / np.maximum(new_weight, 1.0)
                flat_weights[flat_id] = new_weight.astype(np.uint16)
                integrated += int(np.count_nonzero(valid))
    update_stage_output(report, stage_index, tsdf)
    report.metrics.update(
        {
            "integrated_samples": float(integrated),
            "observed_voxel_fraction": float(np.mean(weights > 0)),
        }
    )
    return TSDFResult(
        tsdf=tsdf,
        weights=weights,
        origin=origin_array.astype(np.float32),
        voxel_size=float(voxel_size),
        report=report,
    )


def project_points(
    points_3d: Any,
    K: Any,
    rotation: Any | None = None,
    translation: Any | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Project 3D points and return ``(pixels, positive-depth-mask)``."""

    points = _points3(points_3d, name="points_3d", allow_empty=True)
    intrinsics = np.asarray(as_float32_matrix(K, (3, 3), name="K"), dtype=np.float64)
    if intrinsics[0, 0] <= 0 or intrinsics[1, 1] <= 0:
        raise ValueError("K focal lengths must be positive")
    R = (
        np.eye(3, dtype=np.float64)
        if rotation is None
        else np.asarray(as_float32_matrix(rotation, (3, 3), name="rotation"), dtype=np.float64)
    )
    t = (
        np.zeros(3, dtype=np.float64)
        if translation is None
        else np.asarray(translation, dtype=np.float64).reshape(-1)
    )
    if t.shape != (3,) or not np.isfinite(t).all():
        raise ValueError("translation must be finite shape (3,)")
    camera = (R @ points.T).T + t.reshape(1, 3)
    depth = camera[:, 2]
    projected = np.full((len(points), 2), np.nan, dtype=np.float32)
    valid = np.isfinite(depth) & (depth > 1e-8)
    if np.any(valid):
        pixels = (intrinsics @ camera[valid].T).T
        projected[valid] = (pixels[:, :2] / pixels[:, 2:3]).astype(np.float32)
    return projected, valid


def solve_pnp_checked(
    object_points: Any,
    image_points: Any,
    K: Any,
    *,
    reprojection_threshold_px: float = 3.0,
    confidence: float = 0.999,
    max_iterations: int = 100,
    min_inlier_ratio: float = 0.5,
) -> PnPResult:
    """Solve PnP through the optional OpenCV reference backend with gates."""

    object_array = _points3(object_points, name="object_points")
    image_array = np.ascontiguousarray(image_points, dtype=np.float64)
    if image_array.ndim != 2 or image_array.shape != (len(object_array), 2):
        raise ValueError(f"image_points must have shape ({len(object_array)}, 2)")
    if not np.isfinite(image_array).all():
        raise ValueError("image_points contains non-finite values")
    if len(object_array) < 4:
        raise ValueError("PnP requires at least four correspondences")
    intrinsics = np.asarray(as_float32_matrix(K, (3, 3), name="K"), dtype=np.float64)
    if intrinsics[0, 0] <= 0 or intrinsics[1, 1] <= 0:
        raise ValueError("K focal lengths must be positive")
    if not (0.0 < float(confidence) < 1.0) or int(max_iterations) < 1:
        raise ValueError("invalid PnP solver parameters")
    if not (0.0 < float(min_inlier_ratio) <= 1.0):
        raise ValueError("min_inlier_ratio must be in (0, 1]")
    if not np.isfinite(reprojection_threshold_px) or float(reprojection_threshold_px) <= 0:
        raise ValueError("reprojection_threshold_px must be positive")

    report = PipelineReport("pnp", backend="opencv-reference")
    report.metrics["n_points"] = float(len(object_array))
    try:
        import cv2
    except Exception as exc:
        report.success = False
        report.add_warning("OpenCV is unavailable; no PnP reference backend is installed")
        raise ImportError(report.warnings[-1]) from exc

    stage_index = len(report.stages)
    with timed_stage(report, "solve_pnp"):
        flags = cv2.SOLVEPNP_ITERATIVE if len(object_array) >= 6 else cv2.SOLVEPNP_AP3P
        success, rvec, tvec, inliers = cv2.solvePnPRansac(
            object_array.astype(np.float64),
            image_array.astype(np.float64),
            intrinsics,
            None,
            flags=flags,
            reprojectionError=float(reprojection_threshold_px),
            confidence=float(confidence),
            iterationsCount=int(max_iterations),
        )
        if not success:
            report.success = False
            report.add_warning("OpenCV solvePnPRansac did not find a pose")
            return PnPResult(
                success=False,
                rotation=np.eye(3, dtype=np.float64),
                translation=np.zeros(3, dtype=np.float64),
                inlier_mask=np.zeros(len(object_array), dtype=bool),
                reprojection_error_px=np.full(len(object_array), np.inf, dtype=np.float32),
                report=report,
            )
        rotation, _ = cv2.Rodrigues(rvec)
        translation = np.asarray(tvec, dtype=np.float64).reshape(3)
    projected, valid = project_points(object_array, intrinsics, rotation, translation)
    errors = np.linalg.norm(projected.astype(np.float64) - image_array, axis=1)
    errors[~valid] = np.inf
    inlier_mask = np.isfinite(errors) & (errors <= float(reprojection_threshold_px))
    if inliers is not None:
        explicit = np.zeros(len(object_array), dtype=bool)
        explicit[np.asarray(inliers, dtype=np.int32).reshape(-1)] = True
        inlier_mask &= explicit
    report.metrics.update(
        {
            "n_inliers": float(np.count_nonzero(inlier_mask)),
            "inlier_ratio": float(np.mean(inlier_mask)),
            "median_reprojection_error_px": float(np.median(errors[inlier_mask])) if np.any(inlier_mask) else float("inf"),
        }
    )
    if np.count_nonzero(inlier_mask) < 4 or float(np.mean(inlier_mask)) < float(min_inlier_ratio):
        report.success = False
        report.add_warning("PnP reprojection quality gate rejected the returned pose")
    update_stage_output(report, stage_index, errors)
    return PnPResult(
        success=bool(report.success),
        rotation=np.asarray(rotation, dtype=np.float64),
        translation=translation,
        inlier_mask=inlier_mask,
        reprojection_error_px=errors.astype(np.float32),
        report=report,
    )


__all__ = [
    "ICPResult",
    "TSDFResult",
    "PnPResult",
    "point_to_plane_icp",
    "integrate_tsdf",
    "project_points",
    "solve_pnp_checked",
]

