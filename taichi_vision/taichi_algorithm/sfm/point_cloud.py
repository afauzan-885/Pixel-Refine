"""
Point Cloud Processing — Taichi GPU
====================================
GPU-accelerated point cloud processing untuk 3D reconstruction pipeline.

Algoritma:
  1. Statistical Outlier Removal (SOR): filter noise berdasarkan rata-rata jarak k-nearest
  2. Voxel Grid Downsampling: reduce density dengan voxel averaging
  3. Normal Estimation: PCA-based normals dari k-nearest neighbors
  4. Radius Outlier Removal: filter berdasarkan jumlah tetangga dalam radius

Hybrid precision: Float32 compute, Int32 index storage.
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
    def compute_knn_distance_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),   # (N, 3)
        dist_out: ti.types.ndarray(ti.f32, ndim=2),  # (N, K)
        idx_out: ti.types.ndarray(ti.i32, ndim=2),   # (N, K)
        n: int,
        k: int,
    ):
        """Compute k-nearest neighbor distances per point (brute-force)."""
        for i in range(n):
            # Initialize top-K
            for ki in range(k):
                dist_out[i, ki] = 1e30
                idx_out[i, ki] = -1

            for j in range(n):
                if i == j:
                    continue
                dx = points[i, 0] - points[j, 0]
                dy = points[i, 1] - points[j, 1]
                dz = points[i, 2] - points[j, 2]
                d = ti.sqrt(dx * dx + dy * dy + dz * dz)

                # Insertion sort into top-K
                for ki in range(k):
                    if d < dist_out[i, ki]:
                        kk = k - 1
                        while kk > ki:
                            dist_out[i, kk] = dist_out[i, kk - 1]
                            idx_out[i, kk] = idx_out[i, kk - 1]
                            kk -= 1
                        dist_out[i, ki] = d
                        idx_out[i, ki] = j
                        break

    @ti.kernel
    def sor_filter_kernel(
        knn_dist: ti.types.ndarray(ti.f32, ndim=2),  # (N, K)
        keep_mask: ti.types.ndarray(ti.i32, ndim=1),  # (N,)
        n: int,
        k: int,
        std_multiplier: ti.f32,
    ):
        """Statistical Outlier Removal: mark points whose mean knn distance
        exceeds (global_mean + std_multiplier * global_std)."""
        # Pass 1: compute global mean dan std
        global_sum = ti.f32(0.0)
        global_sum_sq = ti.f32(0.0)
        for i in range(n):
            mean_d = ti.f32(0.0)
            for ki in range(k):
                mean_d += knn_dist[i, ki]
            mean_d /= ti.cast(k, ti.f32)
            global_sum += mean_d
            global_sum_sq += mean_d * mean_d

        global_mean = global_sum / ti.cast(n, ti.f32)
        global_var = global_sum_sq / ti.cast(n, ti.f32) - global_mean * global_mean
        global_std = ti.sqrt(ti.max(global_var, ti.f32(0.0)))
        threshold = global_mean + std_multiplier * global_std

        # Pass 2: filter
        for i in range(n):
            mean_d = ti.f32(0.0)
            for ki in range(k):
                mean_d += knn_dist[i, ki]
            mean_d /= ti.cast(k, ti.f32)
            keep_mask[i] = 1 if mean_d < threshold else 0

    @ti.kernel
    def radius_outlier_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),   # (N, 3)
        keep_mask: ti.types.ndarray(ti.i32, ndim=1), # (N,)
        n: int,
        radius: ti.f32,
        min_neighbors: int,
    ):
        """Radius Outlier Removal: keep points with >= min_neighbors within radius."""
        for i in range(n):
            count = 0
            for j in range(n):
                if i == j:
                    continue
                dx = points[i, 0] - points[j, 0]
                dy = points[i, 1] - points[j, 1]
                dz = points[i, 2] - points[j, 2]
                d = ti.sqrt(dx * dx + dy * dy + dz * dz)
                if d < radius:
                    count += 1
            keep_mask[i] = 1 if count >= min_neighbors else 0

    @ti.kernel
    def voxel_hash_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),     # (N, 3)
        voxel_indices: ti.types.ndarray(ti.i32, ndim=1),  # (N,)
        n: int,
        voxel_size: ti.f32,
    ):
        """Compute voxel hash index per point.
        Uses Cantor pairing function on quantized coordinates."""
        for i in range(n):
            vx = ti.cast(ti.floor(points[i, 0] / voxel_size), ti.i32)
            vy = ti.cast(ti.floor(points[i, 1] / voxel_size), ti.i32)
            vz = ti.cast(ti.floor(points[i, 2] / voxel_size), ti.i32)
            # Cantor pairing for 3D using i32
            h1 = (vx + vy) * (vx + vy + 1) // 2 + vy
            voxel_indices[i] = (h1 + vz) * (h1 + vz + 1) // 2 + vz

    @ti.kernel
    def accumulate_voxel_sums_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),       # (N, 3)
        sorted_voxel_idx: ti.types.ndarray(ti.i64, ndim=1),  # (N,)
        voxel_sum: ti.types.ndarray(ti.f64, ndim=2),    # (max_voxels, 3)
        voxel_count: ti.types.ndarray(ti.i32, ndim=1),  # (max_voxels,)
        n: int,
        max_voxels: int,
    ):
        """Accumulate point sums per voxel using hash-to-slot mapping."""
        for i in range(n):
            # Map hash to slot (simple modulo)
            slot = ti.cast(
                ti.abs(sorted_voxel_idx[i]) % ti.cast(max_voxels, ti.i64),
                ti.i32,
            )
            ti.atomic_add(voxel_sum[slot, 0], ti.cast(points[i, 0], ti.f64))
            ti.atomic_add(voxel_sum[slot, 1], ti.cast(points[i, 1], ti.f64))
            ti.atomic_add(voxel_sum[slot, 2], ti.cast(points[i, 2], ti.f64))
            ti.atomic_add(voxel_count[slot], 1)

    @ti.kernel
    def compute_normals_pca_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),     # (N, 3)
        knn_idx: ti.types.ndarray(ti.i32, ndim=2),    # (N, K)
        normals_out: ti.types.ndarray(ti.f32, ndim=2), # (N, 3)
        n: int,
        k: int,
    ):
        """Compute normals via PCA of k-nearest neighbors.
        Normal = eigenvector of smallest eigenvalue of covariance matrix."""
        for i in range(n):
            # Compute centroid of neighbors
            cx = ti.f32(0.0)
            cy = ti.f32(0.0)
            cz = ti.f32(0.0)
            valid_count = 0
            for ki in range(k):
                j = knn_idx[i, ki]
                if j >= 0:
                    cx += points[j, 0]
                    cy += points[j, 1]
                    cz += points[j, 2]
                    valid_count += 1

            if valid_count < 3:
                normals_out[i, 0] = 0.0
                normals_out[i, 1] = 0.0
                normals_out[i, 2] = 1.0
                continue

            inv_n = 1.0 / ti.cast(valid_count, ti.f32)
            cx *= inv_n
            cy *= inv_n
            cz *= inv_n

            # Build covariance matrix (3x3 symmetric)
            c00 = ti.f32(0.0)
            c01 = ti.f32(0.0)
            c02 = ti.f32(0.0)
            c11 = ti.f32(0.0)
            c12 = ti.f32(0.0)
            c22 = ti.f32(0.0)
            for ki in range(k):
                j = knn_idx[i, ki]
                if j >= 0:
                    dx = points[j, 0] - cx
                    dy = points[j, 1] - cy
                    dz = points[j, 2] - cz
                    c00 += dx * dx
                    c01 += dx * dy
                    c02 += dx * dz
                    c11 += dy * dy
                    c12 += dy * dz
                    c22 += dz * dz

            # Power iteration for smallest eigenvector (3x3)
            # Start with random-ish vector
            nx = ti.f32(0.577)
            ny = ti.f32(0.577)
            nz = ti.f32(0.577)

            for _iter in range(20):
                # Inverse iteration: solve (C - mu*I) * v = v_prev
                # Approximate: v_new = C * v (then subtract from v for smallest)
                r0 = c00 * nx + c01 * ny + c02 * nz
                r1 = c01 * nx + c11 * ny + c12 * nz
                r2 = c02 * nx + c12 * ny + c22 * nz

                # v_new = C*v - lambda*v (deflation for smallest)
                norm = ti.sqrt(r0 * r0 + r1 * r1 + r2 * r2)
                if norm > 1e-10:
                    r0 /= norm
                    r1 /= norm
                    r2 /= norm

                # Orthogonalize against current estimate
                dot = r0 * nx + r1 * ny + r2 * nz
                nx = nx - dot * r0
                ny = ny - dot * r1
                nz = nz - dot * r2

                # Renormalize
                norm2 = ti.sqrt(nx * nx + ny * ny + nz * nz)
                if norm2 > 1e-10:
                    nx /= norm2
                    ny /= norm2
                    nz /= norm2

            normals_out[i, 0] = nx
            normals_out[i, 1] = ny
            normals_out[i, 2] = nz


# =============================================================================
# PYTHON API (JIT + AOT compatible)
# =============================================================================

def _resolve_backend(value=None):
    """Select point-cloud leaf without allowing import-time AOT state to leak."""
    backend = "auto" if value is None else str(value).strip().lower()
    if backend not in {"auto", "numpy", "taichi"}:
        raise ValueError("backend must be one of 'auto', 'numpy', or 'taichi'")
    if backend == "auto":
        return "taichi" if TAICHI_AVAILABLE else "numpy"
    if backend == "taichi":
        if not TAICHI_AVAILABLE:
            raise RuntimeError("backend='taichi' requires AOT_MODE=0 and Taichi")
        runtime = ti.lang.impl.get_runtime()
        if getattr(runtime, "prog", None) is None:
            ti.init(arch=ti.cpu)
    return backend

def statistical_outlier_removal(points, k=20, std_multiplier=2.0, *, backend=None):
    """
    Statistical Outlier Removal (SOR).

    Args:
        points: (N, 3) float32 point cloud
        k: jumlah nearest neighbors untuk statistik
        std_multiplier: threshold = mean + std_multiplier * std

    Returns:
        filtered_points: (M, 3) float32 filtered point cloud
        keep_indices: (M,) int32 indices ke original points
    """
    points = np.ascontiguousarray(points.astype(np.float32))
    n = points.shape[0]

    if n == 0:
        return points.copy(), np.empty(0, dtype=np.int32)

    if n < k + 1:
        return points.copy(), np.arange(n, dtype=np.int32)

    selected_backend = _resolve_backend(backend)
    if selected_backend == "numpy":
        return _sor_numpy(points, k, std_multiplier)

    # GPU path
    knn_dist = np.zeros((n, k), dtype=np.float32)
    knn_idx = np.zeros((n, k), dtype=np.int32)
    compute_knn_distance_kernel(points, knn_dist, knn_idx, n, k)

    keep_mask = np.zeros(n, dtype=np.int32)
    sor_filter_kernel(knn_dist, keep_mask, n, k, std_multiplier)

    keep_indices = np.where(keep_mask > 0)[0].astype(np.int32)
    return points[keep_indices].copy(), keep_indices


def radius_outlier_removal(points, radius=0.1, min_neighbors=5, *, backend=None):
    """
    Radius Outlier Removal (ROR).

    Args:
        points: (N, 3) float32 point cloud
        radius: search radius
        min_neighbors: minimum tetangga dalam radius

    Returns:
        filtered_points: (M, 3) float32
        keep_indices: (M,) int32
    """
    points = np.ascontiguousarray(points.astype(np.float32))
    n = points.shape[0]

    if n == 0:
        return points.copy(), np.empty(0, dtype=np.int32)

    selected_backend = _resolve_backend(backend)
    if selected_backend == "numpy":
        return _ror_numpy(points, radius, min_neighbors)

    keep_mask = np.zeros(n, dtype=np.int32)
    radius_outlier_kernel(points, keep_mask, n, radius, min_neighbors)

    keep_indices = np.where(keep_mask > 0)[0].astype(np.int32)
    return points[keep_indices].copy(), keep_indices


def voxel_downsample(points, voxel_size=0.01, *, backend=None):
    """
    Voxel Grid Downsampling: reduce point density.

    Args:
        points: (N, 3) float32 point cloud
        voxel_size: ukuran voxel (dalam satuan yang sama dengan points)

    Returns:
        downsampled: (M, 3) float32 point cloud
    """
    points = np.ascontiguousarray(points.astype(np.float32))
    n = points.shape[0]

    if n == 0:
        return points.copy()

    selected_backend = _resolve_backend(backend)
    if selected_backend == "numpy":
        return _voxel_downsample_numpy(points, voxel_size)

    # GPU path: compute voxel hash, then aggregate via numpy (hash table)
    voxel_indices = np.zeros(n, dtype=np.int32)
    voxel_hash_kernel(points, voxel_indices, n, voxel_size)

    # Use numpy for grouping (more robust than GPU atomic hash table)
    # Sort by voxel index
    sort_idx = np.argsort(voxel_indices)
    sorted_indices = voxel_indices[sort_idx]

    # Find unique voxels
    unique_voxels, inverse_idx, counts = np.unique(
        sorted_indices, return_inverse=True, return_counts=True
    )

    # Average points per voxel
    n_voxels = len(unique_voxels)
    sorted_points = points[sort_idx]

    # Accumulate using numpy bincount
    sum_x = np.bincount(inverse_idx, weights=sorted_points[:, 0], minlength=n_voxels)
    sum_y = np.bincount(inverse_idx, weights=sorted_points[:, 1], minlength=n_voxels)
    sum_z = np.bincount(inverse_idx, weights=sorted_points[:, 2], minlength=n_voxels)

    downsampled = np.column_stack([
        sum_x / counts,
        sum_y / counts,
        sum_z / counts,
    ]).astype(np.float32)

    return downsampled


def estimate_normals(points, k=20, *, backend=None):
    """
    Normal estimation via PCA dari k-nearest neighbors.

    Args:
        points: (N, 3) float32 point cloud
        k: jumlah nearest neighbors

    Returns:
        normals: (N, 3) float32 unit normals
    """
    points = np.ascontiguousarray(points.astype(np.float32))
    n = points.shape[0]

    if n == 0:
        return np.empty((0, 3), dtype=np.float32)

    if n < k + 1:
        k = min(k, n - 1)

    if k < 3:
        return np.tile([0.0, 0.0, 1.0], (n, 1)).astype(np.float32)

    selected_backend = _resolve_backend(backend)
    if selected_backend == "numpy":
        return _estimate_normals_numpy(points, k)

    # GPU path: compute KNN first
    knn_dist = np.zeros((n, k), dtype=np.float32)
    knn_idx = np.zeros((n, k), dtype=np.int32)
    compute_knn_distance_kernel(points, knn_dist, knn_idx, n, k)

    # Compute normals via PCA
    normals = np.zeros((n, 3), dtype=np.float32)
    compute_normals_pca_kernel(points, knn_idx, normals, n, k)

    # Normalize
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)
    normals = normals / norms

    return normals.astype(np.float32)


def preprocess_point_cloud(points, voxel_size=0.01, sor_k=20, sor_std=2.0, *, backend=None):
    """
    Full preprocessing pipeline: SOR + voxel downsample + normal estimation.

    Args:
        points: (N, 3) float32 raw point cloud
        voxel_size: voxel size untuk downsampling
        sor_k: K untuk SOR
        sor_std: std multiplier untuk SOR

    Returns:
        filtered_points: (M, 3) float32
        normals: (M, 3) float32
        keep_indices: (M,) int32
    """
    # Step 1: Statistical outlier removal
    selected_backend = _resolve_backend(backend)
    filtered, indices = statistical_outlier_removal(
        points, k=sor_k, std_multiplier=sor_std, backend=selected_backend
    )

    if len(filtered) == 0:
        return filtered, np.empty((0, 3), dtype=np.float32), indices

    # Step 2: Voxel downsample
    downsampled = voxel_downsample(filtered, voxel_size=voxel_size, backend=selected_backend)

    if len(downsampled) == 0:
        return downsampled, np.empty((0, 3), dtype=np.float32), np.empty(0, dtype=np.int32)

    # Step 3: Normal estimation
    normals = estimate_normals(
        downsampled, k=min(20, len(downsampled) - 1), backend=selected_backend
    )

    return downsampled, normals, indices


# =============================================================================
# NUMPY FALLBACK
# =============================================================================

def _sor_numpy(points, k=20, std_multiplier=2.0):
    """Pure numpy SOR fallback."""
    from scipy.spatial import cKDTree
    n = points.shape[0]
    tree = cKDTree(points)
    dists, _ = tree.query(points, k=k + 1)  # +1 karena termasuk diri sendiri
    mean_dists = dists[:, 1:].mean(axis=1)  # exclude self-distance

    global_mean = mean_dists.mean()
    global_std = mean_dists.std()
    threshold = global_mean + std_multiplier * global_std

    keep_mask = mean_dists < threshold
    keep_indices = np.where(keep_mask)[0].astype(np.int32)
    return points[keep_indices].copy(), keep_indices


def _ror_numpy(points, radius=0.1, min_neighbors=5):
    """Pure numpy ROR fallback."""
    from scipy.spatial import cKDTree
    tree = cKDTree(points)
    neighbors = tree.query_ball_point(points, radius)
    counts = np.array([len(nb) - 1 for nb in neighbors])  # -1 untuk exclude self
    keep_mask = counts >= min_neighbors
    keep_indices = np.where(keep_mask)[0].astype(np.int32)
    return points[keep_indices].copy(), keep_indices


def _voxel_downsample_numpy(points, voxel_size):
    """Pure numpy voxel downsample fallback."""
    voxel_idx = np.floor(points / voxel_size).astype(np.int64)
    # Cantor pairing hash
    h1 = (voxel_idx[:, 0] + voxel_idx[:, 1]) * (voxel_idx[:, 0] + voxel_idx[:, 1] + 1) // 2 + voxel_idx[:, 1]
    hash_val = (h1 + voxel_idx[:, 2]) * (h1 + voxel_idx[:, 2] + 1) // 2 + voxel_idx[:, 2]

    unique_hashes, inverse, counts = np.unique(hash_val, return_inverse=True, return_counts=True)
    n_voxels = len(unique_hashes)
    sum_x = np.bincount(inverse, weights=points[:, 0], minlength=n_voxels)
    sum_y = np.bincount(inverse, weights=points[:, 1], minlength=n_voxels)
    sum_z = np.bincount(inverse, weights=points[:, 2], minlength=n_voxels)

    return np.column_stack([
        sum_x / counts,
        sum_y / counts,
        sum_z / counts,
    ]).astype(np.float32)


def _estimate_normals_numpy(points, k=20):
    """Pure numpy normal estimation fallback via SVD."""
    from scipy.spatial import cKDTree
    n = points.shape[0]
    tree = cKDTree(points)
    _, idx = tree.query(points, k=k + 1)
    idx = idx[:, 1:]  # exclude self

    normals = np.zeros((n, 3), dtype=np.float32)
    for i in range(n):
        neighbors = points[idx[i]]
        centroid = neighbors.mean(axis=0)
        cov = (neighbors - centroid).T @ (neighbors - centroid) / k
        eigvals, eigvecs = np.linalg.eigh(cov)
        normals[i] = eigvecs[:, 0]  # smallest eigenvalue

    # Normalize
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)
    return (normals / norms).astype(np.float32)
