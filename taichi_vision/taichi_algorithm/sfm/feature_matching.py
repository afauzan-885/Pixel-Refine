"""
BFMatcher (Brute-Force Matcher) — Taichi GPU
==============================================
GPU-accelerated brute-force descriptor matching untuk SfM pipeline.

Algorithm:
  1. Compute pairwise L2 (euclidean) atau Hamming distance antar descriptors
  2. kNN selection: top-k nearest neighbors per descriptor
  3. Lowe's ratio test: reject ambiguous matches
  4. Cross-check filter: keep only mutual best matches

Support:
  - L2 norm: untuk float descriptors (SIFT-like)
  - Hamming distance: untuk binary descriptors (AKAZE/ORB/BRIEF)
  - k=1 (single best) atau k=2 (ratio test)
  - Cross-validation (mutual matching)

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
    def compute_l2_distance_kernel(
        desc1: ti.types.ndarray(ti.f32, ndim=2),  # (N1, D)
        desc2: ti.types.ndarray(ti.f32, ndim=2),  # (N2, D)
        dist_out: ti.types.ndarray(ti.f32, ndim=2),  # (N1, N2)
        n1: int,
        n2: int,
        d: int,
    ):
        """Compute L2 distance matrix between two descriptor sets."""
        for i, j in ti.ndrange(n1, n2):
            sum_sq = ti.f32(0.0)
            for k in range(d):
                diff = desc1[i, k] - desc2[j, k]
                sum_sq += diff * diff
            dist_out[i, j] = ti.sqrt(sum_sq)

    @ti.kernel
    def compute_hamming_distance_kernel(
        desc1: ti.types.ndarray(ti.u8, ndim=2),   # (N1, D_bytes)
        desc2: ti.types.ndarray(ti.u8, ndim=2),   # (N2, D_bytes)
        dist_out: ti.types.ndarray(ti.i32, ndim=2),  # (N1, N2)
        n1: int,
        n2: int,
        d_bytes: int,
    ):
        """Compute Hamming distance matrix between binary descriptor sets.
        Uses popcount per byte (pre-computed LUT approach via bit ops)."""
        for i, j in ti.ndrange(n1, n2):
            total_bits = 0
            for k in range(d_bytes):
                xor_val = ti.cast(desc1[i, k] ^ desc2[j, k], ti.i32)
                # Brian Kernighan's bit counting
                cnt = 0
                v = xor_val
                while v != 0:
                    v = v & (v - 1)
                    cnt += 1
                total_bits += cnt
            dist_out[i, j] = total_bits

    @ti.kernel
    def knn_select_kernel(
        dist_matrix: ti.types.ndarray(ti.f32, ndim=2),  # (N1, N2)
        best_idx: ti.types.ndarray(ti.i32, ndim=2),      # (N1, K)
        best_dist: ti.types.ndarray(ti.f32, ndim=2),     # (N1, K)
        n1: int,
        n2: int,
        k: int,
    ):
        """Select top-K nearest neighbors per query descriptor.
        Uses iterative selection (K is small, typically 1-2)."""
        for i in range(n1):
            # Initialize best arrays with large values
            for ki in range(k):
                best_dist[i, ki] = 1e30
                best_idx[i, ki] = -1

            for j in range(n2):
                d = dist_matrix[i, j]
                # Insert into sorted top-K (insertion sort, K <= 8)
                for ki in range(k):
                    if d < best_dist[i, ki]:
                        # Shift remaining entries down
                        for kk in range(k - 1, ki, -1):
                            best_dist[i, kk] = best_dist[i, kk - 1]
                            best_idx[i, kk] = best_idx[i, kk - 1]
                        best_dist[i, ki] = d
                        best_idx[i, ki] = j
                        break

    @ti.kernel
    def knn_select_hamming_kernel(
        dist_matrix: ti.types.ndarray(ti.i32, ndim=2),  # (N1, N2)
        best_idx: ti.types.ndarray(ti.i32, ndim=2),      # (N1, K)
        best_dist: ti.types.ndarray(ti.i32, ndim=2),     # (N1, K)
        n1: int,
        n2: int,
        k: int,
    ):
        """Select top-K nearest neighbors for Hamming distance (integer)."""
        for i in range(n1):
            for ki in range(k):
                best_dist[i, ki] = 2147483647  # max int32
                best_idx[i, ki] = -1

            for j in range(n2):
                d = dist_matrix[i, j]
                for ki in range(k):
                    if d < best_dist[i, ki]:
                        for kk in range(k - 1, ki, -1):
                            best_dist[i, kk] = best_dist[i, kk - 1]
                            best_idx[i, kk] = best_idx[i, kk - 1]
                        best_dist[i, ki] = d
                        best_idx[i, ki] = j
                        break

    @ti.kernel
    def ratio_test_filter_kernel(
        best_dist: ti.types.ndarray(ti.f32, ndim=2),  # (N1, 2)
        match_out: ti.types.ndarray(ti.i32, ndim=2),   # (N1, 2) [query_idx, train_idx]
        match_dist_out: ti.types.ndarray(ti.f32, ndim=1),  # (N1,)
        best_idx: ti.types.ndarray(ti.i32, ndim=2),    # (N1, 2)
        n1: int,
        ratio_threshold: ti.f32,
    ) -> int:
        """Apply Lowe's ratio test and write accepted matches.
        Returns number of accepted matches via first element of match_dist_out.
        """
        accepted = 0
        for i in range(n1):
            d1 = best_dist[i, 0]
            d2 = best_dist[i, 1]
            if d1 < ratio_threshold * d2:
                idx = ti.atomic_add(accepted, 1)
                match_out[idx, 0] = i
                match_out[idx, 1] = best_idx[i, 0]
                match_dist_out[idx] = d1
        return accepted

    @ti.kernel
    def ratio_test_filter_hamming_kernel(
        best_dist: ti.types.ndarray(ti.i32, ndim=2),
        match_out: ti.types.ndarray(ti.i32, ndim=2),
        match_dist_out: ti.types.ndarray(ti.i32, ndim=1),
        best_idx: ti.types.ndarray(ti.i32, ndim=2),
        n1: int,
        ratio_threshold: ti.f32,
    ) -> int:
        """Ratio test for Hamming distance (integer)."""
        accepted = 0
        for i in range(n1):
            d1 = ti.cast(best_dist[i, 0], ti.f32)
            d2 = ti.cast(best_dist[i, 1], ti.f32)
            if d2 > 0.0 and d1 < ratio_threshold * d2:
                idx = ti.atomic_add(accepted, 1)
                match_out[idx, 0] = i
                match_out[idx, 1] = best_idx[i, 0]
                match_dist_out[idx] = best_dist[i, 0]
        return accepted

    @ti.kernel
    def cross_check_filter_kernel(
        matches_12: ti.types.ndarray(ti.i32, ndim=2),  # forward matches
        n_12: int,
        best_idx_21: ti.types.ndarray(ti.i32, ndim=2),  # reverse best-1
        match_out: ti.types.ndarray(ti.i32, ndim=2),     # filtered output
        match_dist_out: ti.types.ndarray(ti.f32, ndim=1),
        dist_12: ti.types.ndarray(ti.f32, ndim=1),
    ) -> int:
        """Cross-check: keep only mutual best matches.
        match_out[i] = [query_idx, train_idx] if best_idx_21[train_idx] == query_idx.
        """
        accepted = 0
        for i in range(n_12):
            qi = matches_12[i, 0]
            ti_idx = matches_12[i, 1]
            if ti_idx >= 0 and best_idx_21[ti_idx, 0] == qi:
                idx = ti.atomic_add(accepted, 1)
                match_out[idx, 0] = qi
                match_out[idx, 1] = ti_idx
                match_dist_out[idx] = dist_12[i]
        return accepted


# =============================================================================
# PYTHON API (JIT + AOT compatible)
# =============================================================================

def bfmatcher_l2(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
    """
    Brute-force matcher dengan L2 distance (untuk float descriptors).

    Args:
        desc1: (N1, D) float32 descriptors dari image 1
        desc2: (N2, D) float32 descriptors dari image 2
        k: jumlah nearest neighbors (1=single, 2=ratio test)
        ratio_threshold: Lowe's ratio threshold (default 0.75)
        cross_check: jika True, hanya keep mutual best matches

    Returns:
        matches: (M, 2) int32 array [query_idx, train_idx]
        distances: (M,) float32 matched distances
    """
    desc1 = np.ascontiguousarray(desc1.astype(np.float32))
    desc2 = np.ascontiguousarray(desc2.astype(np.float32))

    n1, d = desc1.shape
    n2, d2 = desc2.shape
    assert d == d2, f"Descriptor dimensions must match: {d} vs {d2}"

    if n1 == 0 or n2 == 0:
        return np.empty((0, 2), dtype=np.int32), np.empty(0, dtype=np.float32)

    if not TAICHI_AVAILABLE:
        return _bfmatcher_l2_numpy(desc1, desc2, k, ratio_threshold, cross_check)

    # GPU path
    dist_matrix = np.zeros((n1, n2), dtype=np.float32)
    compute_l2_distance_kernel(desc1, desc2, dist_matrix, n1, n2, d)

    if k == 1:
        best_idx = np.zeros((n1, 1), dtype=np.int32)
        best_dist = np.zeros((n1, 1), dtype=np.float32)
        knn_select_kernel(dist_matrix, best_idx, best_dist, n1, n2, 1)

        # Simple threshold filter (no ratio test for k=1)
        valid = best_dist[:, 0] < 1e10
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[:, 0][valid],
        ]).astype(np.int32)
        distances = best_dist[:, 0][valid].astype(np.float32)

    elif k == 2 and not cross_check:
        # Ratio test
        best_idx = np.zeros((n1, 2), dtype=np.int32)
        best_dist = np.zeros((n1, 2), dtype=np.float32)
        knn_select_kernel(dist_matrix, best_idx, best_dist, n1, n2, 2)

        # Allocate output (worst case: all matches pass)
        match_out = np.zeros((n1, 2), dtype=np.int32)
        match_dist_out = np.zeros(n1, dtype=np.float32)
        count = ratio_test_filter_kernel(
            best_dist, match_out, match_dist_out, best_idx, n1, ratio_threshold
        )

        matches = match_out[:count].copy()
        distances = match_dist_out[:count].copy()

    elif cross_check:
        # Forward: k=1
        best_idx_12 = np.zeros((n1, 1), dtype=np.int32)
        best_dist_12 = np.zeros((n1, 1), dtype=np.float32)
        knn_select_kernel(dist_matrix, best_idx_12, best_dist_12, n1, n2, 1)

        # Reverse: compute reverse distance matrix
        dist_matrix_t = np.zeros((n2, n1), dtype=np.float32)
        compute_l2_distance_kernel(desc2, desc1, dist_matrix_t, n2, n1, d)

        best_idx_21 = np.zeros((n2, 1), dtype=np.int32)
        best_dist_21 = np.zeros((n2, 1), dtype=np.float32)
        knn_select_kernel(dist_matrix_t, best_idx_21, best_dist_21, n2, n1, 1)

        # Cross-check filter
        matches_12 = np.column_stack([
            np.arange(n1, dtype=np.int32),
            best_idx_12[:, 0],
        ]).astype(np.int32)

        dist_12 = best_dist_12[:, 0].astype(np.float32)
        match_out = np.zeros((n1, 2), dtype=np.int32)
        match_dist_out = np.zeros(n1, dtype=np.float32)
        count = cross_check_filter_kernel(
            matches_12, n1, best_idx_21, match_out, match_dist_out, dist_12
        )

        matches = match_out[:count].copy()
        distances = match_dist_out[:count].copy()
    else:
        # k > 2 without cross_check: just do kNN
        best_idx = np.zeros((n1, k), dtype=np.int32)
        best_dist = np.zeros((n1, k), dtype=np.float32)
        knn_select_kernel(dist_matrix, best_idx, best_dist, n1, n2, k)

        # Return all k matches (flatten)
        rows = np.repeat(np.arange(n1), k)
        cols = best_idx.ravel()
        dists = best_dist.ravel()
        valid = cols >= 0
        matches = np.column_stack([rows[valid], cols[valid]]).astype(np.int32)
        distances = dists[valid].astype(np.float32)

    return matches, distances


def bfmatcher_hamming(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
    """
    Brute-force matcher dengan Hamming distance (untuk binary descriptors).

    Args:
        desc1: (N1, D_bytes) uint8 binary descriptors dari image 1
        desc2: (N2, D_bytes) uint8 binary descriptors dari image 2
        k: jumlah nearest neighbors
        ratio_threshold: Lowe's ratio threshold
        cross_check: mutual matching

    Returns:
        matches: (M, 2) int32 array [query_idx, train_idx]
        distances: (M,) int32 Hamming distances (bit count)
    """
    desc1 = np.ascontiguousarray(desc1.astype(np.uint8))
    desc2 = np.ascontiguousarray(desc2.astype(np.uint8))

    n1, d_bytes = desc1.shape
    n2, d2 = desc2.shape
    assert d_bytes == d2, f"Descriptor byte lengths must match: {d_bytes} vs {d2}"

    if n1 == 0 or n2 == 0:
        return np.empty((0, 2), dtype=np.int32), np.empty(0, dtype=np.int32)

    if not TAICHI_AVAILABLE:
        return _bfmatcher_hamming_numpy(desc1, desc2, k, ratio_threshold, cross_check)

    # GPU path
    dist_matrix = np.zeros((n1, n2), dtype=np.int32)
    compute_hamming_distance_kernel(desc1, desc2, dist_matrix, n1, n2, d_bytes)

    if k == 1:
        best_idx = np.zeros((n1, 1), dtype=np.int32)
        best_dist = np.full((n1, 1), 2147483647, dtype=np.int32)
        knn_select_hamming_kernel(dist_matrix, best_idx, best_dist, n1, n2, 1)

        valid = best_dist[:, 0] < 2147483647
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[:, 0][valid],
        ]).astype(np.int32)
        distances = best_dist[:, 0][valid]

    elif k == 2 and not cross_check:
        best_idx = np.zeros((n1, 2), dtype=np.int32)
        best_dist = np.full((n1, 2), 2147483647, dtype=np.int32)
        knn_select_hamming_kernel(dist_matrix, best_idx, best_dist, n1, n2, 2)

        # Ratio test for hamming (integer distances)
        match_out = np.zeros((n1, 2), dtype=np.int32)
        match_dist_out = np.zeros(n1, dtype=np.int32)
        count = ratio_test_filter_hamming_kernel(
            best_dist, match_out, match_dist_out, best_idx, n1, ratio_threshold
        )

        matches = match_out[:count].copy()
        distances = match_dist_out[:count].copy()

    elif cross_check:
        best_idx_12 = np.zeros((n1, 1), dtype=np.int32)
        best_dist_12 = np.full((n1, 1), 2147483647, dtype=np.int32)
        knn_select_hamming_kernel(dist_matrix, best_idx_12, best_dist_12, n1, n2, 1)

        dist_matrix_t = np.zeros((n2, n1), dtype=np.int32)
        compute_hamming_distance_kernel(desc2, desc1, dist_matrix_t, n2, n1, d_bytes)

        best_idx_21 = np.zeros((n2, 1), dtype=np.int32)
        best_dist_21 = np.full((n2, 1), 2147483647, dtype=np.int32)
        knn_select_hamming_kernel(dist_matrix_t, best_idx_21, best_dist_21, n2, n1, 1)

        matches_12 = np.column_stack([
            np.arange(n1, dtype=np.int32),
            best_idx_12[:, 0],
        ]).astype(np.int32)

        dist_12 = best_dist_12[:, 0].astype(np.float32)
        match_out = np.zeros((n1, 2), dtype=np.int32)
        match_dist_out = np.zeros(n1, dtype=np.float32)
        count = cross_check_filter_kernel(
            matches_12, n1, best_idx_21, match_out, match_dist_out, dist_12
        )

        matches = match_out[:count].astype(np.int32).copy()
        distances = match_dist_out[:count].astype(np.int32).copy()
    else:
        best_idx = np.zeros((n1, k), dtype=np.int32)
        best_dist = np.full((n1, k), 2147483647, dtype=np.int32)
        knn_select_hamming_kernel(dist_matrix, best_idx, best_dist, n1, n2, k)

        rows = np.repeat(np.arange(n1), k)
        cols = best_idx.ravel()
        dists = best_dist.ravel()
        valid = cols >= 0
        matches = np.column_stack([rows[valid], cols[valid]]).astype(np.int32)
        distances = dists[valid]

    return matches, distances


# =============================================================================
# NUMPY FALLBACK
# =============================================================================

def _bfmatcher_l2_numpy(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
    """Pure numpy fallback for L2 BFMatcher."""
    # Compute distance matrix
    # ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a.b
    sq1 = np.sum(desc1 ** 2, axis=1, keepdims=True)  # (N1, 1)
    sq2 = np.sum(desc2 ** 2, axis=1, keepdims=True)  # (N2, 1)
    dist_sq = sq1 + sq2.T - 2.0 * desc1 @ desc2.T
    dist_sq = np.maximum(dist_sq, 0.0)
    dist_matrix = np.sqrt(dist_sq).astype(np.float32)

    n1 = desc1.shape[0]
    n2 = desc2.shape[0]

    if k == 1:
        best_idx = np.argmin(dist_matrix, axis=1)
        best_dist = dist_matrix[np.arange(n1), best_idx]
        valid = best_dist < 1e10
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[valid].astype(np.int32),
        ]).astype(np.int32)
        distances = best_dist[valid].astype(np.float32)
        return matches, distances

    # k=2 ratio test
    part_idx = np.argpartition(dist_matrix, kth=min(k, n2 - 1), axis=1)[:, :k]
    part_dist = np.take_along_axis(dist_matrix, part_idx, axis=1)

    # Sort within k
    sort_order = np.argsort(part_dist, axis=1)
    best_idx = np.take_along_axis(part_idx, sort_order, axis=1)
    best_dist = np.take_along_axis(part_dist, sort_order, axis=1)

    if cross_check:
        # Reverse matching
        part_idx_r = np.argpartition(dist_matrix.T, kth=min(1, n1 - 1), axis=1)[:, :1]
        best_idx_21 = part_idx_r[:, 0]

        # Forward k=1
        f_idx = best_idx[:, 0]
        f_dist = best_dist[:, 0]
        mask = best_idx_21[f_idx] == np.arange(n1)
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[mask],
            f_idx[mask].astype(np.int32),
        ]).astype(np.int32)
        distances = f_dist[mask].astype(np.float32)
        return matches, distances

    # Ratio test
    if best_dist.shape[1] >= 2:
        d1 = best_dist[:, 0]
        d2 = best_dist[:, 1]
        mask = d1 < ratio_threshold * d2
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[mask],
            best_idx[:, 0][mask].astype(np.int32),
        ]).astype(np.int32)
        distances = d1[mask].astype(np.float32)
        return matches, distances
    else:
        valid = best_dist[:, 0] < 1e10
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[:, 0][valid].astype(np.int32),
        ]).astype(np.int32)
        distances = best_dist[:, 0][valid].astype(np.float32)
        return matches, distances


def _bfmatcher_hamming_numpy(desc1, desc2, k=2, ratio_threshold=0.75, cross_check=False):
    """Pure numpy fallback for Hamming BFMatcher."""
    n1 = desc1.shape[0]
    n2 = desc2.shape[0]

    # Compute Hamming distance using vectorized XOR + popcount
    # Reshape for broadcasting: (N1, 1, D) ^ (1, N2, D)
    xor = np.bitwise_xor(
        desc1[:, np.newaxis, :].astype(np.uint8),
        desc2[np.newaxis, :, :].astype(np.uint8),
    )
    # Popcount per byte using lookup table approach
    popcount_table = np.array([
        bin(i).count('1') for i in range(256)
    ], dtype=np.int32)
    dist_matrix = popcount_table[xor].sum(axis=2).astype(np.int32)  # (N1, N2)

    if k == 1:
        best_idx = np.argmin(dist_matrix, axis=1)
        best_dist = dist_matrix[np.arange(n1), best_idx]
        valid = best_dist < 2147483647
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[valid].astype(np.int32),
        ]).astype(np.int32)
        distances = best_dist[valid]
        return matches, distances

    part_idx = np.argpartition(dist_matrix, kth=min(k, n2 - 1), axis=1)[:, :k]
    part_dist = np.take_along_axis(dist_matrix, part_idx, axis=1)
    sort_order = np.argsort(part_dist, axis=1)
    best_idx = np.take_along_axis(part_idx, sort_order, axis=1)
    best_dist = np.take_along_axis(part_dist, sort_order, axis=1)

    if cross_check:
        part_idx_r = np.argpartition(dist_matrix.T, kth=min(1, n1 - 1), axis=1)[:, :1]
        best_idx_21 = part_idx_r[:, 0]
        f_idx = best_idx[:, 0]
        f_dist = best_dist[:, 0]
        mask = best_idx_21[f_idx] == np.arange(n1)
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[mask],
            f_idx[mask].astype(np.int32),
        ]).astype(np.int32)
        distances = f_dist[mask]
        return matches, distances

    if best_dist.shape[1] >= 2:
        d1 = best_dist[:, 0].astype(np.float32)
        d2 = best_dist[:, 1].astype(np.float32)
        mask = d1 < ratio_threshold * d2
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[mask],
            best_idx[:, 0][mask].astype(np.int32),
        ]).astype(np.int32)
        distances = best_dist[:, 0][mask]
        return matches, distances
    else:
        valid = best_dist[:, 0] < 2147483647
        matches = np.column_stack([
            np.arange(n1, dtype=np.int32)[valid],
            best_idx[:, 0][valid].astype(np.int32),
        ]).astype(np.int32)
        distances = best_dist[:, 0][valid]
        return matches, distances
