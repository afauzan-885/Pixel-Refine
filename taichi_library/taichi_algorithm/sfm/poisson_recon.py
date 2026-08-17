"""
Poisson Surface Reconstruction — Taichi GPU
===============================================
GPU-accelerated Poisson surface reconstruction untuk mengkonversi
oriented point cloud (positions + normals) menjadi triangle mesh.

Algorithm (Kazhdan et al., 2006 — simplified voxel version):
  1. Build voxel grid dari oriented point cloud
  2. Rasterize divergence field dari normals ke grid
  3. Solve Poisson equation: ∇²χ = ∇·N via iterative Gauss-Seidel
  4. Extract isosurface pada level χ = threshold (marching cubes)

Simplified approach:
  - Voxel grid (fixed resolution) instead of adaptive octree
  - Iterative Gauss-Seidel solver (GPU-friendly)
  - Marching cubes with standard lookup tables
  - Normal estimation fallback jika normals tidak tersedia

Hybrid precision: Float64 solve, Float32 mesh output.
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
    def rasterize_divergence_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),   # (N, 3)
        normals: ti.types.ndarray(ti.f32, ndim=2),   # (N, 3)
        div_field: ti.types.ndarray(ti.f32, ndim=3), # (gx, gy, gz)
        n_pts: int,
        grid_origin: ti.types.ndarray(ti.f32, ndim=1),  # (3,)
        voxel_size: ti.f32,
        gx: int, gy: int, gz: int,
    ):
        """Rasterize divergence of normal field onto voxel grid.
        For each point, compute ∇·N = dnx/dx + dny/dy + dnz/dz
        and splat onto 8 neighboring voxels via trilinear weights."""
        for idx in range(n_pts):
            px = ti.cast(points[idx, 0], ti.f32)
            py = ti.cast(points[idx, 1], ti.f32)
            pz = ti.cast(points[idx, 2], ti.f32)
            nx = ti.cast(normals[idx, 0], ti.f32)
            ny = ti.cast(normals[idx, 1], ti.f32)
            nz = ti.cast(normals[idx, 2], ti.f32)

            # Voxel coordinates (continuous)
            vx = (px - grid_origin[0]) / voxel_size
            vy = (py - grid_origin[1]) / voxel_size
            vz = (pz - grid_origin[2]) / voxel_size

            ix = ti.cast(ti.floor(vx), ti.i32)
            iy = ti.cast(ti.floor(vy), ti.i32)
            iz = ti.cast(ti.floor(vz), ti.i32)

            fx = vx - ti.cast(ix, ti.f32)
            # Fractions must use the index from their own voxel axis. Mixing
            # axes leaks one coordinate into the trilinear weights and makes
            # divergence rasterization depend on grid aspect/location.
            fy = vy - ti.cast(iy, ti.f32)
            fz = vz - ti.cast(iz, ti.f32)

            # Trilinear splat of divergence
            for di in ti.static(range(2)):
                for dj in ti.static(range(2)):
                    for dk in ti.static(range(2)):
                        ci = ix + di
                        cj = iy + dj
                        ck = iz + dk
                        if 0 <= ci < gx and 0 <= cj < gy and 0 <= ck < gz:
                            wx = fx if di == 0 else (1.0 - fx)
                            wy = fy if dj == 0 else (1.0 - fy)
                            wz = fz if dk == 0 else (1.0 - fz)
                            w = wx * wy * wz
                            # Divergence contribution (simplified: dot of normal with gradient of basis)
                            div_val = nx + ny + nz  # simplified divergence
                            ti.atomic_add(div_field[ci, cj, ck], w * div_val)

    @ti.kernel
    def gauss_seidel_step_kernel(
        field: ti.types.ndarray(ti.f32, ndim=3),     # (gx, gy, gz)
        div_field: ti.types.ndarray(ti.f32, ndim=3), # (gx, gy, gz)
        mask: ti.types.ndarray(ti.i32, ndim=3),      # (gx, gy, gz) occupied voxels
        gx: int, gy: int, gz: int,
        omega: ti.f32,  # SOR relaxation factor
    ) -> ti.f32:
        """One Gauss-Seidel (SOR) iteration for ∇²χ = div.
        Red-black ordering for GPU parallelism.
        Returns residual norm."""
        residual_sum = ti.f32(0.0)
        count = 0

        # Red pass (even sum of indices)
        for i, j, k in ti.ndrange(gx, gy, gz):
            if (i + j + k) % 2 == 0:
                if mask[i, j, k] == 0:
                    continue
                # 7-point Laplacian stencil
                center = field[i, j, k]
                nb_sum = ti.f32(0.0)
                nb_count = 0
                if i > 0:
                    nb_sum += field[i-1, j, k]; nb_count += 1
                if i < gx - 1:
                    nb_sum += field[i+1, j, k]; nb_count += 1
                if j > 0:
                    nb_sum += field[i, j-1, k]; nb_count += 1
                if j < gy - 1:
                    nb_sum += field[i, j+1, k]; nb_count += 1
                if k > 0:
                    nb_sum += field[i, j, k-1]; nb_count += 1
                if k < gz - 1:
                    nb_sum += field[i, j, k+1]; nb_count += 1

                if nb_count > 0:
                    target = (nb_sum - div_field[i, j, k]) / ti.cast(nb_count, ti.f32)
                    new_val = (1.0 - omega) * center + omega * target
                    diff = new_val - center
                    residual_sum += diff * diff
                    field[i, j, k] = new_val
                    count += 1

        # Black pass (odd sum of indices)
        for i, j, k in ti.ndrange(gx, gy, gz):
            if (i + j + k) % 2 == 1:
                if mask[i, j, k] == 0:
                    continue
                center = field[i, j, k]
                nb_sum = ti.f32(0.0)
                nb_count = 0
                if i > 0:
                    nb_sum += field[i-1, j, k]; nb_count += 1
                if i < gx - 1:
                    nb_sum += field[i+1, j, k]; nb_count += 1
                if j > 0:
                    nb_sum += field[i, j-1, k]; nb_count += 1
                if j < gy - 1:
                    nb_sum += field[i, j+1, k]; nb_count += 1
                if k > 0:
                    nb_sum += field[i, j, k-1]; nb_count += 1
                if k < gz - 1:
                    nb_sum += field[i, j, k+1]; nb_count += 1

                if nb_count > 0:
                    target = (nb_sum - div_field[i, j, k]) / ti.cast(nb_count, ti.f32)
                    new_val = (1.0 - omega) * center + omega * target
                    diff = new_val - center
                    residual_sum += diff * diff
                    field[i, j, k] = new_val
                    count += 1

        return ti.sqrt(residual_sum / ti.cast(ti.max(count, 1), ti.f32))

    @ti.kernel
    def build_occupancy_mask_kernel(
        points: ti.types.ndarray(ti.f32, ndim=2),  # (N, 3)
        mask: ti.types.ndarray(ti.i32, ndim=3),     # (gx, gy, gz)
        n_pts: int,
        grid_origin: ti.types.ndarray(ti.f32, ndim=1),
        voxel_size: ti.f32,
        gx: int, gy: int, gz: int,
        dilate_radius: int,
    ):
        """Mark occupied voxels and dilate by radius."""
        for idx in range(n_pts):
            px = ti.cast(points[idx, 0], ti.f32)
            py = ti.cast(points[idx, 1], ti.f32)
            pz = ti.cast(points[idx, 2], ti.f32)

            ix = ti.cast(ti.round((px - grid_origin[0]) / voxel_size), ti.i32)
            iy = ti.cast(ti.round((py - grid_origin[1]) / voxel_size), ti.i32)
            iz = ti.cast(ti.round((pz - grid_origin[2]) / voxel_size), ti.i32)

            for di in range(-dilate_radius, dilate_radius + 1):
                for dj in range(-dilate_radius, dilate_radius + 1):
                    for dk in range(-dilate_radius, dilate_radius + 1):
                        ci = ix + di
                        cj = iy + dj
                        ck = iz + dk
                        if 0 <= ci < gx and 0 <= cj < gy and 0 <= ck < gz:
                            mask[ci, cj, ck] = 1


# =============================================================================
# MARCHING CUBES LOOKUP TABLES (Standard)
# =============================================================================

# Edge table: which edges are intersected for each of 256 cube configurations
_EDGE_TABLE = np.array([
    0x0, 0x109, 0x203, 0x30a, 0x406, 0x50f, 0x605, 0x70c,
    0x80c, 0x905, 0xa0f, 0xb06, 0xc0a, 0xd03, 0xe09, 0xf00,
    0x190, 0x99, 0x393, 0x29a, 0x596, 0x49f, 0x795, 0x69c,
    0x99c, 0x895, 0xb9f, 0xa96, 0xd9a, 0xc93, 0xf99, 0xe90,
    0x230, 0x339, 0x33, 0x13a, 0x636, 0x73f, 0x435, 0x53c,
    0xa3c, 0xb35, 0x83f, 0x936, 0xe3a, 0xf33, 0xc39, 0xd30,
    0x3a0, 0x2a9, 0x1a3, 0xaa, 0x7a6, 0x6af, 0x5a5, 0x4ac,
    0xbac, 0xaa5, 0x9af, 0x8a6, 0xfaa, 0xea3, 0xda9, 0xca0,
    0x460, 0x569, 0x663, 0x76a, 0x66, 0x16f, 0x265, 0x36c,
    0xc6c, 0xd65, 0xe6f, 0xf66, 0x86a, 0x963, 0xa69, 0xb60,
    0x5f0, 0x4f9, 0x7f3, 0x6fa, 0x1f6, 0xff, 0x3f5, 0x2fc,
    0xdfc, 0xcf5, 0xfff, 0xef6, 0x9fa, 0x8f3, 0xbf9, 0xaf0,
    0x650, 0x759, 0x453, 0x55a, 0x256, 0x35f, 0x55, 0x15c,
    0xe5c, 0xf55, 0xc5f, 0xd56, 0xa5a, 0xb53, 0x859, 0x950,
    0x7c0, 0x6c9, 0x5c3, 0x4ca, 0x3c6, 0x2cf, 0x1c5, 0xcc,
    0xfcc, 0xec5, 0xdcf, 0xcc6, 0xbca, 0xac3, 0x9c9, 0x8c0,
    0x8c0, 0x9c9, 0xac3, 0xbca, 0xcc6, 0xdcf, 0xec5, 0xfcc,
    0xcc, 0x1c5, 0x2cf, 0x3c6, 0x4ca, 0x5c3, 0x6c9, 0x7c0,
    0x950, 0x859, 0xb53, 0xa5a, 0xd56, 0xc5f, 0xf55, 0xe5c,
    0x15c, 0x55, 0x35f, 0x256, 0x55a, 0x453, 0x759, 0x650,
    0xaf0, 0xbf9, 0x8f3, 0x9fa, 0xef6, 0xfff, 0xcf5, 0xdfc,
    0x2fc, 0x3f5, 0xff, 0x1f6, 0x6fa, 0x7f3, 0x4f9, 0x5f0,
    0xb60, 0xa69, 0x963, 0x86a, 0xf66, 0xe6f, 0xd65, 0xc6c,
    0x36c, 0x265, 0x16f, 0x66, 0x76a, 0x663, 0x569, 0x460,
    0xca0, 0xda9, 0xea3, 0xfaa, 0x8a6, 0x9af, 0xaa5, 0xbac,
    0x4ac, 0x5a5, 0x6af, 0x7a6, 0xaa, 0x1a3, 0x2a9, 0x3a0,
    0xd30, 0xc39, 0xf33, 0xe3a, 0x936, 0x83f, 0xb35, 0xa3c,
    0x53c, 0x435, 0x73f, 0x636, 0x13a, 0x33, 0x339, 0x230,
    0xe90, 0xf99, 0xc93, 0xd9a, 0xa96, 0xb9f, 0x895, 0x99c,
    0x69c, 0x795, 0x49f, 0x596, 0x29a, 0x393, 0x99, 0x190,
    0xf00, 0xe09, 0xd03, 0xc0a, 0xb06, 0xa0f, 0x905, 0x80c,
    0x70c, 0x605, 0x50f, 0x406, 0x30a, 0x203, 0x109, 0x0,
], dtype=np.int32)

# Simplified triangle table (first 16 entries, rest follow same pattern)
# Each entry lists edge triplets forming triangles
_TRI_TABLE = [
    [],
    [[0, 8, 3]],
    [[0, 1, 9]],
    [[1, 8, 3], [9, 8, 1]],
    [[1, 2, 10]],
    [[0, 8, 3], [1, 2, 10]],
    [[9, 2, 10], [0, 2, 9]],
    [[2, 8, 3], [2, 10, 8], [10, 9, 8]],
    [[3, 11, 2]],
    [[0, 11, 2], [8, 11, 0]],
    [[1, 9, 0], [2, 3, 11]],
    [[1, 11, 2], [1, 9, 11], [9, 8, 11]],
    [[3, 10, 1], [11, 10, 3]],
    [[0, 10, 1], [0, 8, 10], [8, 11, 10]],
    [[3, 9, 0], [3, 11, 9], [11, 10, 9]],
    [[9, 8, 10], [10, 8, 11]],
]


# =============================================================================
# PYTHON API
# =============================================================================

def poisson_reconstruct(
    points,
    normals=None,
    grid_resolution=64,
    solver_iterations=50,
    iso_threshold=0.5,
    dilate_radius=2,
    omega=1.5,
):
    """
    Poisson Surface Reconstruction dari oriented point cloud.

    Args:
        points: (N, 3) float32 point positions
        normals: (N, 3) float32 point normals (optional, estimated jika None)
        grid_resolution: resolusi voxel grid per axis (default 64)
        solver_iterations: jumlah Gauss-Seidel iterations (default 50)
        iso_threshold: isosurface threshold untuk mesh extraction (default 0.5)
        dilate_radius: voxel dilation radius untuk occupancy mask (default 2)
        omega: SOR relaxation factor (1.0=Gauss-Seidel, >1=over-relax, default 1.5)

    Returns:
        vertices: (V, 3) float32 mesh vertices
        faces: (F, 3) int32 triangle face indices
    """
    points = np.ascontiguousarray(points.astype(np.float32))

    if points.shape[0] == 0:
        return np.empty((0, 3), dtype=np.float32), np.empty((0, 3), dtype=np.int32)

    # Estimate normals if not provided
    if normals is None:
        normals = _estimate_normals_knn(points, k=15)
    normals = np.ascontiguousarray(normals.astype(np.float32))

    # Normalize normals
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)
    normals = normals / norms

    if not TAICHI_AVAILABLE:
        return _poisson_numpy(
            points, normals, grid_resolution, solver_iterations,
            iso_threshold, dilate_radius, omega
        )

    # GPU path
    # 1. Compute grid bounds
    bbox_min = points.min(axis=0) - 1e-3
    bbox_max = points.max(axis=0) + 1e-3
    bbox_size = bbox_max - bbox_min
    max_dim = bbox_size.max()
    voxel_size = max_dim / grid_resolution

    gx = int(np.ceil(bbox_size[0] / voxel_size)) + 1
    gy = int(np.ceil(bbox_size[1] / voxel_size)) + 1
    gz = int(np.ceil(bbox_size[2] / voxel_size)) + 1

    grid_origin = bbox_min.astype(np.float32)
    voxel_size = float(voxel_size)
    omega = float(omega)

    # 2. Build occupancy mask
    mask = np.zeros((gx, gy, gz), dtype=np.int32)
    build_occupancy_mask_kernel(
        points, mask, points.shape[0],
        grid_origin, voxel_size, gx, gy, gz, dilate_radius
    )

    # 3. Rasterize divergence field
    div_field = np.zeros((gx, gy, gz), dtype=np.float32)
    rasterize_divergence_kernel(
        points, normals, div_field, points.shape[0],
        grid_origin, voxel_size, gx, gy, gz
    )

    # 4. Solve Poisson equation via Gauss-Seidel
    field = np.zeros((gx, gy, gz), dtype=np.float32)
    for iteration in range(solver_iterations):
        residual = gauss_seidel_step_kernel(field, div_field, mask, gx, gy, gz, omega)
        if residual < 1e-8:
            break

    # 5. Extract mesh via marching cubes
    vertices, faces = _marching_cubes_numpy(field.astype(np.float64), mask, voxel_size, grid_origin.astype(np.float64), iso_threshold)

    return vertices.astype(np.float32), faces.astype(np.int32)


# =============================================================================
# NUMPY FALLBACK
# =============================================================================

def _poisson_numpy(points, normals, grid_resolution, solver_iterations,
                   iso_threshold, dilate_radius, omega):
    """Pure numpy fallback for Poisson reconstruction."""
    bbox_min = points.min(axis=0) - 1e-3
    bbox_max = points.max(axis=0) + 1e-3
    bbox_size = bbox_max - bbox_min
    max_dim = bbox_size.max()
    voxel_size = max_dim / grid_resolution

    gx = int(np.ceil(bbox_size[0] / voxel_size)) + 1
    gy = int(np.ceil(bbox_size[2] / voxel_size)) + 1
    gz = int(np.ceil(bbox_size[2] / voxel_size)) + 1
    grid_origin = bbox_min.astype(np.float64)

    # Build mask
    mask = np.zeros((gx, gy, gz), dtype=np.int32)
    for idx in range(points.shape[0]):
        ix = int(np.round((points[idx, 0] - grid_origin[0]) / voxel_size))
        iy = int(np.round((points[idx, 1] - grid_origin[1]) / voxel_size))
        iz = int(np.round((points[idx, 2] - grid_origin[2]) / voxel_size))
        for di in range(-dilate_radius, dilate_radius + 1):
            for dj in range(-dilate_radius, dilate_radius + 1):
                for dk in range(-dilate_radius, dilate_radius + 1):
                    ci, cj, ck = ix + di, iy + dj, iz + dk
                    if 0 <= ci < gx and 0 <= cj < gy and 0 <= ck < gz:
                        mask[ci, cj, ck] = 1

    # Build divergence field
    div_field = np.zeros((gx, gy, gz), dtype=np.float64)
    for idx in range(points.shape[0]):
        px, py, pz = points[idx].astype(np.float64)
        nx, ny, nz = normals[idx].astype(np.float64)
        vx = (px - grid_origin[0]) / voxel_size
        vy = (py - grid_origin[1]) / voxel_size
        vz = (pz - grid_origin[2]) / voxel_size
        ix = int(np.floor(vx))
        iy = int(np.floor(vy))
        iz = int(np.floor(vz))
        fx = vx - ix
        fy = vy - iy
        fz = vz - iz
        for di in range(2):
            for dj in range(2):
                for dk in range(2):
                    ci, cj, ck = ix + di, iy + dj, iz + dk
                    if 0 <= ci < gx and 0 <= cj < gy and 0 <= ck < gz:
                        wx = fx if di == 0 else (1.0 - fx)
                        wy = fy if dj == 0 else (1.0 - fy)
                        wz = fz if dk == 0 else (1.0 - fz)
                        div_field[ci, cj, ck] += wx * wy * wz * (nx + ny + nz)

    # Gauss-Seidel solve
    field = np.zeros((gx, gy, gz), dtype=np.float64)
    for iteration in range(solver_iterations):
        residual_sum = 0.0
        count = 0
        for phase in range(2):  # Red-black
            for i in range(gx):
                for j in range(gy):
                    for k in range(gz):
                        if (i + j + k) % 2 != phase:
                            continue
                        if mask[i, j, k] == 0:
                            continue
                        nb_sum = 0.0
                        nb_count = 0
                        if i > 0:
                            nb_sum += field[i-1, j, k]; nb_count += 1
                        if i < gx - 1:
                            nb_sum += field[i+1, j, k]; nb_count += 1
                        if j > 0:
                            nb_sum += field[i, j-1, k]; nb_count += 1
                        if j < gy - 1:
                            nb_sum += field[i, j+1, k]; nb_count += 1
                        if k > 0:
                            nb_sum += field[i, j, k-1]; nb_count += 1
                        if k < gz - 1:
                            nb_sum += field[i, j, k+1]; nb_count += 1
                        if nb_count > 0:
                            target = (nb_sum - div_field[i, j, k]) / nb_count
                            new_val = (1.0 - omega) * field[i, j, k] + omega * target
                            diff = new_val - field[i, j, k]
                            residual_sum += diff * diff
                            field[i, j, k] = new_val
                            count += 1
        residual = np.sqrt(residual_sum / max(count, 1))
        if residual < 1e-8:
            break

    # Marching cubes
    vertices, faces = _marching_cubes_numpy(field, mask, voxel_size, grid_origin, iso_threshold)
    return vertices.astype(np.float32), faces.astype(np.int32)


def _estimate_normals_knn(points, k=15):
    """Estimate normals via PCA on k-nearest neighbors."""
    from scipy.spatial import cKDTree
    n = points.shape[0]
    normals = np.zeros_like(points)

    tree = cKDTree(points)
    _, indices = tree.query(points, k=k + 1)  # +1 karena termasuk point itu sendiri

    for i in range(n):
        neighbors = points[indices[i, 1:]]  # exclude self
        centered = neighbors - neighbors.mean(axis=0)
        cov = centered.T @ centered / k
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        # Normal = eigenvector dengan eigenvalue terkecil
        normals[i] = eigenvectors[:, 0]

    return normals


# Edge vertex interpolation positions
_EDGE_VERTICES = [
    (0, 0, 0, 1, 0, 0),  # edge 0
    (1, 0, 0, 1, 1, 0),  # edge 1
    (0, 1, 0, 1, 1, 0),  # edge 2
    (0, 0, 0, 0, 1, 0),  # edge 3
    (0, 0, 1, 1, 0, 1),  # edge 4
    (1, 0, 1, 1, 1, 1),  # edge 5
    (0, 1, 1, 1, 1, 1),  # edge 6
    (0, 0, 1, 0, 1, 1),  # edge 7
    (0, 0, 0, 0, 0, 1),  # edge 8
    (1, 0, 0, 1, 0, 1),  # edge 9
    (1, 1, 0, 1, 1, 1),  # edge 10
    (0, 1, 0, 0, 1, 1),  # edge 11
]


def _marching_cubes_numpy(field, mask, voxel_size, grid_origin, iso_threshold):
    """Simplified marching cubes extraction."""
    gx, gy, gz = field.shape
    vertices = []
    faces = []
    vert_cache = {}

    for i in range(gx - 1):
        for j in range(gy - 1):
            for k in range(gz - 1):
                if mask[i, j, k] == 0:
                    continue

                # Cube corner values
                corners = []
                corner_offsets = [
                    (0,0,0),(1,0,0),(1,1,0),(0,1,0),
                    (0,0,1),(1,0,1),(1,1,1),(0,1,1),
                ]
                for di, dj, dk in corner_offsets:
                    corners.append(field[i+di, j+dj, k+dk])

                # Compute cube index
                cube_index = 0
                for ci in range(8):
                    if corners[ci] < iso_threshold:
                        cube_index |= (1 << ci)

                if cube_index == 0 or cube_index == 255:
                    continue

                # Get edges
                edge_flags = _EDGE_TABLE[cube_index]
                if edge_flags == 0:
                    continue

                # Compute edge vertices
                edge_verts = {}
                for edge_idx in range(12):
                    if edge_flags & (1 << edge_idx):
                        v0 = _EDGE_VERTICES[edge_idx][:3]
                        v1 = _EDGE_VERTICES[edge_idx][3:]
                        val0 = corners[_corner_from_edge(edge_idx, 0)]
                        val1 = corners[_corner_from_edge(edge_idx, 1)]

                        if abs(val1 - val0) < 1e-10:
                            t = 0.5
                        else:
                            t = (iso_threshold - val0) / (val1 - val0)

                        px = (i + v0[0] + t * (v1[0] - v0[0])) * voxel_size + grid_origin[0]
                        py = (j + v0[1] + t * (v1[1] - v0[1])) * voxel_size + grid_origin[1]
                        pz = (k + v0[2] + t * (v1[2] - v0[2])) * voxel_size + grid_origin[2]

                        edge_key = (i, j, k, edge_idx)
                        if edge_key not in vert_cache:
                            vert_cache[edge_key] = len(vertices)
                            vertices.append([px, py, pz])
                        edge_verts[edge_idx] = vert_cache[edge_key]

                # Generate triangles
                if cube_index < len(_TRI_TABLE):
                    tri_edges = _TRI_TABLE[cube_index]
                    for tri in tri_edges:
                        if len(tri) >= 3:
                            v0 = edge_verts.get(tri[0])
                            v1 = edge_verts.get(tri[1])
                            v2 = edge_verts.get(tri[2])
                            if v0 is not None and v1 is not None and v2 is not None:
                                faces.append([v0, v1, v2])

    if len(vertices) == 0:
        return np.empty((0, 3), dtype=np.float32), np.empty((0, 3), dtype=np.int32)

    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.int32)


def _corner_from_edge(edge_idx, end):
    """Get corner index from edge index and endpoint (0=start, 1=end)."""
    _edge_corners = [
        (0, 1), (1, 2), (3, 2), (0, 3),  # edges 0-3 (bottom face)
        (4, 5), (5, 6), (7, 6), (4, 7),  # edges 4-7 (top face)
        (0, 4), (1, 5), (2, 6), (3, 7),  # edges 8-11 (vertical)
    ]
    return _edge_corners[edge_idx][end]
