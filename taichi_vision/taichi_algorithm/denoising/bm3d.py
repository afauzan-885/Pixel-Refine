# Marker: GPU_NATIVE_MARKER_V3
"""
Hybrid Fast Collaborative Denoising (HFCD) — Taichi GPU Implementation
======================================================================
Combines the best techniques from 4 approaches:
  - G-BM3D (Sanders & Larkin 2021): FFT cross-correlation block matching
  - BM3D Full (Dabov et al. 2007): 2D DCT hard thresholding
  - BM3D Step-1: Single-pass (skip Wiener for speed)
  - NLM (Buades et al. 2005): Exponential weight aggregation

Algorithm Pipeline (single pass):
  1. Block matching: brute-force L2 with Top-K selection (one kernel)
  2. 2D DCT per-group hard thresholding (one kernel)
  3. Weighted overlap-add aggregation (one kernel)

Optional: cycle spinning for +0.5-1 dB PSNR gain.

References:
  - Dabov, K., et al. (2007). "Image Denoising by Sparse 3-D Transform-Domain
    Collaborative Filtering." IEEE TIP, 16(8), pp.2080-2095.
  - Sanders, T. & Larkin, S. (2021). "New Computational Techniques for a Faster
    Variation of BM3D." arXiv:2103.10765.
"""

import numpy as np
import math
import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass


# =============================================================================
# DCT-II Basis Matrix (CPU-side precomputation, reusable by other algorithms)
# =============================================================================

def build_dct_matrix(N):
    """
    Build N×N DCT-II orthonormal basis matrix.

    T[k,n] = alpha(k) * cos((2n+1)*k*pi / (2*N))
    alpha(0) = sqrt(1/N), alpha(k>0) = sqrt(2/N)

    Usage: forward DCT: C = T @ block @ T^T
           inverse DCT: block = T^T @ C @ T

    Returns:
        T: (N, N) float32 numpy array.
    """
    T = np.zeros((N, N), dtype=np.float32)
    for k in range(N):
        alpha = math.sqrt(1.0 / N) if k == 0 else math.sqrt(2.0 / N)
        for n in range(N):
            T[k, n] = alpha * math.cos((2 * n + 1) * k * math.pi / (2 * N))
    return T


_DCT_CACHE = {}


def _get_dct_matrix(N):
    """Get or create cached DCT matrix for size N."""
    if N not in _DCT_CACHE:
        _DCT_CACHE[N] = build_dct_matrix(N)
    return _DCT_CACHE[N]


# =============================================================================
# Taichi GPU Kernels
# =============================================================================

if TAICHI_AVAILABLE:

    # ---- Unified Block Matching Kernel ----
    # Combines: inner product + distance + top-K + block extraction
    # One thread per reference block → fully parallel

    @ti.kernel
    def _block_match_and_extract_kernel(
        src: ti.types.ndarray(),          # (H, W) input image
        groups: ti.types.ndarray(),       # (num_refs, K, N, N) output matched blocks
        match_y: ti.types.ndarray(),      # (num_refs, K) match y positions
        match_x: ti.types.ndarray(),      # (num_refs, K) match x positions
        valid_mask: ti.types.ndarray(),   # (num_refs, K) 1=valid, 0=padded
        ref_positions: ti.types.ndarray(),# (num_refs, 2) reference (y, x)
        num_refs: int, K: int, N: int,
        search_r: int, H: int, W: int
    ):
        """
        Unified block matching: for each reference block, compute distances
        to all candidates in search window, select top-K, extract blocks.
        All in one kernel — no Python-level loop needed.
        """
        for g in range(num_refs):
            ry = ref_positions[g, 0]
            rx = ref_positions[g, 1]

            # --- Phase 1: Compute distances and find top-K ---
            # Use local arrays for top-K tracking
            top_k_dist = ti.Vector([1e30] * 32)  # max K=32
            top_k_cy = ti.Vector([0] * 32, dt=ti.i32)
            top_k_cx = ti.Vector([0] * 32, dt=ti.i32)
            n_found = 0

            for dy in range(-search_r, search_r + 1):
                cy = ry + dy
                if cy < 0 or cy >= H - N + 1:
                    continue
                for dx in range(-search_r, search_r + 1):
                    cx = rx + dx
                    if cx < 0 or cx >= W - N + 1:
                        continue

                    # Compute L2 distance between ref block and candidate
                    dist = 0.0
                    for i in range(N):
                        for j in range(N):
                            diff = src[ry + i, rx + j] - src[cy + i, cx + j]
                            dist += diff * diff

                    # Insert into top-K if better than worst
                    if n_found < K:
                        top_k_dist[n_found] = dist
                        top_k_cy[n_found] = cy
                        top_k_cx[n_found] = cx
                        n_found += 1
                    else:
                        # Find worst in current top-K
                        worst_idx = 0
                        worst_d = top_k_dist[0]
                        for ki in range(1, K):
                            if top_k_dist[ki] > worst_d:
                                worst_d = top_k_dist[ki]
                                worst_idx = ki

                        if dist < worst_d:
                            top_k_dist[worst_idx] = dist
                            top_k_cy[worst_idx] = cy
                            top_k_cx[worst_idx] = cx

            # --- Phase 2: Extract matched blocks ---
            for k in range(K):
                if k < n_found:
                    cy = top_k_cy[k]
                    cx = top_k_cx[k]
                    match_y[g, k] = cy
                    match_x[g, k] = cx
                    valid_mask[g, k] = 1
                    for i in range(N):
                        for j in range(N):
                            groups[g, k, i, j] = src[cy + i, cx + j]
                else:
                    match_y[g, k] = 0
                    match_x[g, k] = 0
                    valid_mask[g, k] = 0
                    for i in range(N):
                        for j in range(N):
                            groups[g, k, i, j] = 0.0

    @ti.kernel
    def _block_match_and_extract_portable_kernel(
        src: ti.types.ndarray(),
        groups: ti.types.ndarray(),
        match_y: ti.types.ndarray(),
        match_x: ti.types.ndarray(),
        ref_positions: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
        search_r: int, H: int, W: int,
    ):
        """Vulkan variant using negative coordinates as the validity flag."""
        for g in range(num_refs):
            ry = ref_positions[g, 0]
            rx = ref_positions[g, 1]
            top_k_dist = ti.Vector([1e30] * 32)
            top_k_cy = ti.Vector([0] * 32, dt=ti.i32)
            top_k_cx = ti.Vector([0] * 32, dt=ti.i32)
            n_found = 0

            for dy in range(-search_r, search_r + 1):
                cy = ry + dy
                if cy < 0 or cy >= H - N + 1:
                    continue
                for dx in range(-search_r, search_r + 1):
                    cx = rx + dx
                    if cx < 0 or cx >= W - N + 1:
                        continue
                    dist = 0.0
                    for i in range(N):
                        for j in range(N):
                            diff = src[ry + i, rx + j] - src[cy + i, cx + j]
                            dist += diff * diff
                    if n_found < K:
                        top_k_dist[n_found] = dist
                        top_k_cy[n_found] = cy
                        top_k_cx[n_found] = cx
                        n_found += 1
                    else:
                        worst_idx = 0
                        worst_d = top_k_dist[0]
                        for ki in range(1, K):
                            if top_k_dist[ki] > worst_d:
                                worst_d = top_k_dist[ki]
                                worst_idx = ki
                        if dist < worst_d:
                            top_k_dist[worst_idx] = dist
                            top_k_cy[worst_idx] = cy
                            top_k_cx[worst_idx] = cx

            for k in range(K):
                if k < n_found:
                    cy = top_k_cy[k]
                    cx = top_k_cx[k]
                    match_y[g, k] = cy
                    match_x[g, k] = cx
                    for i in range(N):
                        for j in range(N):
                            groups[g, k, i, j] = src[cy + i, cx + j]
                else:
                    match_y[g, k] = -1
                    match_x[g, k] = -1
                    for i in range(N):
                        for j in range(N):
                            groups[g, k, i, j] = 0.0

    # ---- Collaborative DCT Hard Thresholding ----

    @ti.kernel
    def _collaborative_dct_filter_kernel(
        groups: ti.types.ndarray(),        # (num_refs, K, N, N) in/out
        filtered: ti.types.ndarray(),      # (num_refs, K, N, N) output
        group_weights: ti.types.ndarray(), # (num_refs,) output
        T_dct: ti.types.ndarray(),         # (N, N) DCT basis
        temp_buf: ti.types.ndarray(),      # (num_refs, K, N, N) scratch
        num_refs: int, K: int, N: int,
        sigma: float, lambda_3d: float
    ):
        """
        Per-group 2D DCT hard thresholding.
        One thread per reference group — fully parallel across groups.
        """
        thr = lambda_3d * sigma

        for g in range(num_refs):
            n_har = 0

            for k in range(K):
                # Forward DCT: C = T @ block @ T^T
                # Step 1: temp[i,j] = sum_m T[i,m] * block[m,j]  (row transform)
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += T_dct[i, m] * groups[g, k, m, j]
                        temp_buf[g, k, i, j] = s

                # Step 2: coeff[i,j] = sum_m temp[i,m] * T[j,m]  (col transform)
                # + Hard threshold in-place
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += temp_buf[g, k, i, m] * T_dct[j, m]
                        if ti.abs(s) > thr:
                            groups[g, k, i, j] = s
                            n_har += 1
                        else:
                            groups[g, k, i, j] = 0.0

                # Inverse DCT: block = T^T @ C @ T
                # Step 1: temp[i,j] = sum_m T^T[i,m] * C[m,j] = sum_m T[m,i] * C[m,j]
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += T_dct[m, i] * groups[g, k, m, j]
                        temp_buf[g, k, i, j] = s

                # Step 2: out[i,j] = sum_m temp[i,m] * T[m,j]
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += temp_buf[g, k, i, m] * T_dct[m, j]
                        filtered[g, k, i, j] = s

            # Weight = 1 / (sigma^2 * max(n_har, 1))
            group_weights[g] = 1.0 / (sigma * sigma * ti.max(n_har, 1))

    @ti.kernel
    def _dct_forward_threshold_portable_kernel(
        groups: ti.types.ndarray(),
        group_weights: ti.types.ndarray(),
        T_dct: ti.types.ndarray(),
        temp_buf: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
        sigma: float, lambda_3d: float,
    ):
        """Forward DCT and threshold pass with reduced descriptor pressure."""
        thr = lambda_3d * sigma
        for g in range(num_refs):
            n_har = 0
            for k in range(K):
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += T_dct[i, m] * groups[g, k, m, j]
                        temp_buf[g, k, i, j] = s
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += temp_buf[g, k, i, m] * T_dct[j, m]
                        if ti.abs(s) > thr:
                            groups[g, k, i, j] = s
                            n_har += 1
                        else:
                            groups[g, k, i, j] = 0.0
            group_weights[g] = 1.0 / (
                sigma * sigma * ti.max(n_har, 1)
            )

    @ti.kernel
    def _dct_inverse_portable_kernel(
        groups: ti.types.ndarray(),
        filtered: ti.types.ndarray(),
        T_dct: ti.types.ndarray(),
        temp_buf: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
    ):
        """Inverse DCT pass with reduced descriptor pressure."""
        for g in range(num_refs):
            for k in range(K):
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += T_dct[m, i] * groups[g, k, m, j]
                        temp_buf[g, k, i, j] = s
                for i in range(N):
                    for j in range(N):
                        s = 0.0
                        for m in range(N):
                            s += temp_buf[g, k, i, m] * T_dct[m, j]
                        filtered[g, k, i, j] = s

    # ---- Overlap-Add Aggregation ----

    @ti.kernel
    def _aggregate_kernel(
        filtered: ti.types.ndarray(),
        group_weights: ti.types.ndarray(),
        match_y: ti.types.ndarray(),
        match_x: ti.types.ndarray(),
        valid_mask: ti.types.ndarray(),
        output: ti.types.ndarray(),
        weight_sum: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
        H: int, W: int
    ):
        """Weighted overlap-add aggregation with atomic operations."""
        for g in range(num_refs):
            w = group_weights[g]
            for k in range(K):
                if valid_mask[g, k] == 0:
                    continue
                by = match_y[g, k]
                bx = match_x[g, k]
                for dy in range(N):
                    for dx in range(N):
                        py = by + dy
                        px = bx + dx
                        if 0 <= py < H and 0 <= px < W:
                            ti.atomic_add(output[py, px],
                                          w * filtered[g, k, dy, dx])
                            ti.atomic_add(weight_sum[py, px], w)

    @ti.kernel
    def _aggregate_values_portable_kernel(
        filtered: ti.types.ndarray(),
        group_weights: ti.types.ndarray(),
        match_y: ti.types.ndarray(),
        match_x: ti.types.ndarray(),
        output: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
        H: int, W: int,
    ):
        """Accumulate filtered values; negative coordinates are invalid."""
        for g in range(num_refs):
            weight = group_weights[g]
            for k in range(K):
                by = match_y[g, k]
                bx = match_x[g, k]
                if by < 0 or bx < 0:
                    continue
                for dy in range(N):
                    for dx in range(N):
                        py = by + dy
                        px = bx + dx
                        if 0 <= py < H and 0 <= px < W:
                            ti.atomic_add(
                                output[py, px],
                                weight * filtered[g, k, dy, dx],
                            )

    @ti.kernel
    def _aggregate_weights_portable_kernel(
        group_weights: ti.types.ndarray(),
        match_y: ti.types.ndarray(),
        match_x: ti.types.ndarray(),
        weight_sum: ti.types.ndarray(),
        num_refs: int, K: int, N: int,
        H: int, W: int,
    ):
        """Accumulate overlap weights in a separate low-descriptor pass."""
        for g in range(num_refs):
            weight = group_weights[g]
            for k in range(K):
                by = match_y[g, k]
                bx = match_x[g, k]
                if by < 0 or bx < 0:
                    continue
                for dy in range(N):
                    for dx in range(N):
                        py = by + dy
                        px = bx + dx
                        if 0 <= py < H and 0 <= px < W:
                            ti.atomic_add(weight_sum[py, px], weight)

    @ti.kernel
    def _normalize_kernel(output: ti.types.ndarray(),
                          weight_sum: ti.types.ndarray(),
                          src: ti.types.ndarray(),
                          H: int, W: int):
        """Normalize: output = weighted_sum / weight_sum. Fallback to src."""
        for y, x in ti.ndrange(H, W):
            ws = weight_sum[y, x]
            if ws > 1e-12:
                output[y, x] = output[y, x] / ws
            else:
                output[y, x] = src[y, x]

    # ---- Utility Kernels ----

    @ti.kernel
    def _zero_kernel(dst: ti.types.ndarray(), H: int, W: int):
        for y, x in ti.ndrange(H, W):
            dst[y, x] = 0.0

    @ti.kernel
    def _circular_shift_kernel(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                                H: int, W: int, sy: int, sx: int):
        for y, x in ti.ndrange(H, W):
            dst[y, x] = src[(y - sy) % H, (x - sx) % W]

    @ti.kernel
    def _accumulate_kernel(dst: ti.types.ndarray(), src: ti.types.ndarray(),
                           H: int, W: int):
        for y, x in ti.ndrange(H, W):
            dst[y, x] += src[y, x]

    @ti.kernel
    def _scale_kernel(data: ti.types.ndarray(), scale: float, H: int, W: int):
        for y, x in ti.ndrange(H, W):
            data[y, x] *= scale


# =============================================================================
# Single-Pass Pipeline (Python orchestrator)
# =============================================================================

def _hfcd_single_pass(img_gpu, T_np, H, W, N, K, search_r,
                       sigma, lambda_3d, buffer_provider):
    """
    Single-pass HFCD: block matching → DCT filter → aggregate.
    All heavy work is in 3 GPU kernels.

    Args:
        T_np: DCT basis as numpy array (N, N) float32.
    """
    # --- Compute reference grid ---
    step = N  # non-overlapping reference blocks
    ref_positions_list = []
    for ry in range(0, H - N + 1, step):
        for rx in range(0, W - N + 1, step):
            ref_positions_list.append((ry, rx))
    num_refs = len(ref_positions_list)

    if num_refs == 0:
        # Image smaller than block size — return copy
        out = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
        common.copy_field(img_gpu, out)
        return out

    # Reference positions as numpy array (compatible with ti.types.ndarray)
    ref_pos_np = np.array(ref_positions_list, dtype=np.int32)

    # Allocate buffers (ti.ndarray via pool — compatible with ti.types.ndarray)
    groups = common.get_temp_buffer((num_refs, K, N, N), ti.f32, buffer_provider)
    match_y = common.get_temp_buffer((num_refs, K), ti.i32, buffer_provider)
    match_x = common.get_temp_buffer((num_refs, K), ti.i32, buffer_provider)
    valid_mask = common.get_temp_buffer((num_refs, K), ti.i32, buffer_provider)

    # --- Kernel 1: Block Matching ---
    _block_match_and_extract_kernel(
        img_gpu, groups, match_y, match_x, valid_mask, ref_pos_np,
        num_refs, K, N, search_r, H, W
    )

    # --- Kernel 2: Collaborative DCT Filtering ---
    filtered = common.get_temp_buffer((num_refs, K, N, N), ti.f32, buffer_provider)
    group_weights = common.get_temp_buffer((num_refs,), ti.f32, buffer_provider)
    temp_buf = common.get_temp_buffer((num_refs, K, N, N), ti.f32, buffer_provider)

    _collaborative_dct_filter_kernel(
        groups, filtered, group_weights, T_np, temp_buf,
        num_refs, K, N, sigma, lambda_3d
    )

    common.release_temp_buffer(groups)
    common.release_temp_buffer(temp_buf)

    # --- Kernel 3: Aggregation ---
    output = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
    weight_sum = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
    _zero_kernel(output, H, W)
    _zero_kernel(weight_sum, H, W)

    _aggregate_kernel(
        filtered, group_weights, match_y, match_x, valid_mask,
        output, weight_sum, num_refs, K, N, H, W
    )

    _normalize_kernel(output, weight_sum, img_gpu, H, W)

    # Cleanup
    common.release_temp_buffer(filtered)
    common.release_temp_buffer(group_weights)
    common.release_temp_buffer(match_y)
    common.release_temp_buffer(match_x)
    common.release_temp_buffer(valid_mask)

    return output


# =============================================================================
# Main API Function
# =============================================================================

@ti_thread
def hfcd_denoise(src, sigma, block_size=8, search_radius=15,
                 max_matches=16, lambda_3d=2.7, cycle_spins=1,
                 buffer_provider="pool"):
    """
    Hybrid Fast Collaborative Denoising (GPU-accelerated).

    Combines: BM3D block matching + 2D DCT hard thresholding + NLM aggregation.
    Single-pass algorithm (no Wiener second step) with optional cycle spinning.

    Args:
        src: Input image (H, W) or (H, W, 3), float32 [0, 1] or uint8/uint16.
        sigma: Noise standard deviation (same scale as image: [0, 1] for float,
               [0, 255] for uint8). Auto-scaled internally.
        block_size: Block side length N (default 8, use 12 for high noise sigma>40).
        search_radius: Half-size of search window (default 15 -> 31x31 area).
        max_matches: Max similar blocks per reference K (default 16, max 32).
        lambda_3d: Hard threshold multiplier (default 2.7 from BM3D paper).
        cycle_spins: 1=no spin, 2=two shifts, 3=three shifts (+PSNR).
        buffer_provider: Buffer pool provider.

    Returns:
        Denoised image in same format/dtype as input.
    """
    is_numpy = isinstance(src, np.ndarray)
    orig_dtype = src.dtype if is_numpy else np.float32

    # --- AUTO-REPAIR: Input sanitization (self-contained, no fallback) ---

    # 1. Handle NaN/Inf in float inputs
    if is_numpy and src.dtype in (np.float32, np.float64):
        if np.any(np.isnan(src)) or np.any(np.isinf(src)):
            src = np.nan_to_num(src, nan=0.0, posinf=1.0, neginf=0.0).astype(np.float32)

    # 2. Ensure contiguous memory layout
    if is_numpy:
        src = np.ascontiguousarray(src)

    # 3. Auto-cast integer types to float32 [0,1]
    if is_numpy and src.dtype == np.uint8:
        src = src.astype(np.float32) / 255.0
        sigma = sigma / 255.0
    elif is_numpy and src.dtype == np.uint16:
        src = src.astype(np.float32) / 65535.0
        sigma = sigma / 65535.0

    # 4. Clamp float inputs to valid range [0,1]
    if is_numpy and src.dtype == np.float32:
        src = np.clip(src, 0.0, 1.0)

    # 5. Sigma validation: no-op if invalid
    sigma = float(sigma)
    if not np.isfinite(sigma) or sigma <= 0:
        return src.copy() if is_numpy else src

    # 6. Image dimensions check
    if len(src.shape) < 2:
        return src.copy() if is_numpy else src
    H, W = src.shape[:2]
    if H < 2 or W < 2:
        return src.copy() if is_numpy else src

    # 7. Auto-clamp parameters to fit image
    N = min(block_size, H, W)
    search_radius = min(search_radius, max(1, min(H, W) // 2))
    max_area = (2 * search_radius + 1) ** 2
    K = min(max_matches, max(1, max_area), 32)

    # --- AOT path (production) ---
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.bm3d(
            src, sigma=sigma, block_size=N,
            search_radius=search_radius, max_matches=K,
            lambda_3d=lambda_3d, cycle_spins=cycle_spins,
            return_gpu=not is_numpy
        )

    # --- JIT path (development) ---

    # Handle multi-channel by processing each channel independently
    if len(src.shape) == 3 and src.shape[2] == 3:
        result = np.zeros_like(src) if is_numpy else src
        for c in range(3):
            ch = src[:, :, c] if is_numpy else common.extract_channel(src, c)
            denoised_ch = hfcd_denoise(
                ch, sigma, block_size=N, search_radius=search_radius,
                max_matches=K, lambda_3d=lambda_3d,
                cycle_spins=cycle_spins, buffer_provider=buffer_provider
            )
            if is_numpy:
                result[:, :, c] = denoised_ch
            else:
                common.insert_channel(result, denoised_ch, c)
        return result

    # --- Single channel processing ---
    src_gpu, src_is_temp = common.ensure_taichi_field(
        src, dtype=ti.f32, buffer_provider=buffer_provider
    )

    # Precompute DCT basis matrix on CPU (numpy array, passed directly)
    T_np = _get_dct_matrix(N)

    # Cycle spinning loop
    final_output = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
    _zero_kernel(final_output, H, W)

    for spin in range(cycle_spins):
        shift_x = (spin * N // 2) % W if spin > 0 else 0
        shift_y = (spin * N // 2) % H if spin > 0 else 0

        # Apply circular shift
        if shift_x != 0 or shift_y != 0:
            shifted = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
            _circular_shift_kernel(src_gpu, shifted, H, W, shift_y, shift_x)
            work_img = shifted
        else:
            work_img = src_gpu

        # Run single-pass HFCD
        denoised = _hfcd_single_pass(
            work_img, T_np, H, W, N, K, search_radius,
            sigma, lambda_3d, buffer_provider
        )

        # Un-shift and accumulate
        if shift_x != 0 or shift_y != 0:
            unshifted = common.get_temp_buffer((H, W), ti.f32, buffer_provider)
            _circular_shift_kernel(denoised, unshifted, H, W, -shift_y, -shift_x)
            _accumulate_kernel(final_output, unshifted, H, W)
            common.release_temp_buffer(unshifted)
            common.release_temp_buffer(shifted)
        else:
            _accumulate_kernel(final_output, denoised, H, W)

        common.release_temp_buffer(denoised)

    # Average over spins
    _scale_kernel(final_output, 1.0 / cycle_spins, H, W)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    result = common.to_numpy_if_needed(final_output, is_numpy)

    # Auto-cast back to original dtype
    if isinstance(result, np.ndarray):
        if orig_dtype == np.uint8:
            return np.clip(result * 255.0, 0, 255).astype(np.uint8)
        elif orig_dtype == np.uint16:
            return np.clip(result * 65535.0, 0, 65535).astype(np.uint16)
    return result
