"""
Cost Function - Taichi GPU Implementation
==========================================
GPU-accelerated cost calculation functions for optical flow tile matching.

Matching C++ API: cost_function.cpp
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

# ============================================================================
# Constants (matching C++ cost_function.cpp)
# ============================================================================
NORMALIZATION_EPSILON = 1e-6
EPSILON_SQ = NORMALIZATION_EPSILON * NORMALIZATION_EPSILON

# Gradient weighting constants (matching C++ Similarity Module)
GRADIENT_WEIGHT_FACTOR = 1.4
SENSITIVITY = 150.0
STAB_EPSILON = 1e-6


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def _fast_tanh(x: float) -> float:
        """Fast tanh approximation (matching C++ fast_tanh_local)."""
        result = 0.0
        if x >= 3.0:
            result = 1.0
        elif x <= -3.0:
            result = -1.0
        else:
            x2 = x * x
            result = x * (27.0 + x2) / (27.0 + 9.0 * x2)
        return result

    @ti.func
    def compute_zmcl_cost(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y_ref: int,
        x_ref: int,
        y_comp: int,
        x_comp: int,
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
    ) -> float:
        """
        Compute Zero-Mean Correlation-Like (ZMCL) cost for a tile.
        Matches C++ calculate_fine_analysis / block_cost_zmcl_avx.
        """
        eps_sq = EPSILON_SQ
        gradient_weight_factor = GRADIENT_WEIGHT_FACTOR
        sensitivity = SENSITIVITY
        stab_epsilon = STAB_EPSILON

        # Pass 1: Compute mean difference
        sum_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            val_ref = ref[y_ref + r, x_ref + c]
            val_comp = comp[y_comp + r, x_comp + c]
            sum_diff += val_ref - val_comp

        mean_diff = sum_diff / float(tile_h * tile_w)

        # Pass 2: Compute weighted cost
        total_cost = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            row_ref = y_ref + r
            col_ref = x_ref + c
            row_comp = y_comp + r
            col_comp = x_comp + c

            # Gradient calculation (2D central difference, clamped)
            # Replicates simplified gradient logic from C++

            # Ref Gradient
            gx1 = 0.0
            gy1 = 0.0
            if col_ref > 0 and col_ref < w - 1:
                gx1 = ref[row_ref, col_ref + 1] - ref[row_ref, col_ref - 1]
            if row_ref > 0 and row_ref < h - 1:
                gy1 = ref[row_ref + 1, col_ref] - ref[row_ref - 1, col_ref]

            # Comp Gradient
            gx2 = 0.0
            gy2 = 0.0
            if col_comp > 0 and col_comp < w - 1:
                gx2 = comp[row_comp, col_comp + 1] - comp[row_comp, col_comp - 1]
            if row_comp > 0 and row_comp < h - 1:
                gy2 = comp[row_comp + 1, col_comp] - comp[row_comp - 1, col_comp]

            # Gradient magnitude
            mag1_sq = gx1 * gx1 + gy1 * gy1
            mag2_sq = gx2 * gx2 + gy2 * gy2
            min_mag_sq = ti.min(mag1_sq, mag2_sq)

            # Structure weight
            structure_weight = 1.0
            if (
                min_mag_sq > stab_epsilon
                and mag1_sq > stab_epsilon
                and mag2_sq > stab_epsilon
            ):
                dot = gx1 * gx2 + gy1 * gy2
                cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                score = ti.max(cos_sim, 0.0) * ti.sqrt(min_mag_sq)
                structure_weight = 1.0 + gradient_weight_factor * _fast_tanh(
                    score * sensitivity
                )

            # Zero-mean Charbonnier
            val_ref = ref[row_ref, col_ref]
            val_comp = comp[row_comp, col_comp]
            diff = (val_ref - val_comp) - mean_diff

            total_cost += ti.sqrt(diff * diff + eps_sq) * structure_weight

        return total_cost / float(tile_h * tile_w)

    @ti.kernel
    def _compute_mean_diff_kernel(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        mean_out: ti.types.ndarray(),
        length: int,
    ):
        """Compute mean difference between ref and comp tiles."""
        sum_diff = 0.0
        for i in range(length):
            sum_diff += ref[i] - comp[i]
        mean_out[0] = sum_diff / float(length)

    @ti.kernel
    def _block_cost_zmcl_kernel(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        cost_out: ti.types.ndarray(),
        mean_diff: float,
        length: int,
    ):
        """
        Zero-Mean Correlation Like (ZMCL) cost with gradient weighting.
        Matching C++ block_cost_zmcl_avx().

        Cost = sum( weight * Charbonnier(diff_zero_mean) )
        """
        eps_sq = EPSILON_SQ
        gradient_weight_factor = GRADIENT_WEIGHT_FACTOR
        sensitivity = SENSITIVITY
        stab_epsilon = STAB_EPSILON

        total_cost = 0.0

        # First pixel (no gradient)
        if length > 0:
            d = (ref[0] - comp[0]) - mean_diff
            total_cost += ti.sqrt(d * d + eps_sq)

        # Middle pixels with gradient weighting
        for i in range(1, length - 1):
            # 1D X-Gradient using central difference
            gx1 = ref[i + 1] - ref[i - 1]
            gx2 = comp[i + 1] - comp[i - 1]

            # 1D Gradient Magnitude
            mag1_sq = gx1 * gx1
            mag2_sq = gx2 * gx2
            min_mag_sq = ti.min(mag1_sq, mag2_sq)

            # Structure Weight (Cosine Similarity)
            structure_weight = 1.0

            if (
                min_mag_sq > stab_epsilon
                and mag1_sq > stab_epsilon
                and mag2_sq > stab_epsilon
            ):
                dot = gx1 * gx2  # Dot product in 1D
                cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                score = ti.max(cos_sim, 0.0) * ti.sqrt(min_mag_sq)
                structure_weight = 1.0 + gradient_weight_factor * _fast_tanh(
                    score * sensitivity
                )

            # Zero-Mean Difference
            diff = (ref[i] - comp[i]) - mean_diff

            # Weighted Charbonnier Cost
            total_cost += ti.sqrt(diff * diff + eps_sq) * structure_weight

        # Last pixel (no gradient)
        if length > 1:
            d = (ref[length - 1] - comp[length - 1]) - mean_diff
            total_cost += ti.sqrt(d * d + eps_sq)

        cost_out[0] = total_cost

    @ti.kernel
    def _block_cost_zmcl_2d_kernel(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        cost_out: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """
        2D ZMCL cost calculation for tile matching.
        More efficient for 2D tiles than flattening to 1D.
        """
        eps_sq = EPSILON_SQ
        gradient_weight_factor = GRADIENT_WEIGHT_FACTOR
        sensitivity = SENSITIVITY
        stab_epsilon = STAB_EPSILON

        # Pass 1: Compute mean difference
        sum_diff = 0.0
        for r, c in ti.ndrange(h, w):
            sum_diff += ref[r, c] - comp[r, c]
        mean_diff = sum_diff / float(h * w)

        # Pass 2: Compute weighted cost
        total_cost = 0.0
        for r, c in ti.ndrange(h, w):
            # Gradient calculation (2D Sobel-like)
            gx1 = 0.0
            gy1 = 0.0
            gx2 = 0.0
            gy2 = 0.0

            if c > 0 and c < w - 1:
                gx1 = ref[r, c + 1] - ref[r, c - 1]
                gx2 = comp[r, c + 1] - comp[r, c - 1]
            if r > 0 and r < h - 1:
                gy1 = ref[r + 1, c] - ref[r - 1, c]
                gy2 = comp[r + 1, c] - comp[r - 1, c]

            # Gradient magnitude
            mag1_sq = gx1 * gx1 + gy1 * gy1
            mag2_sq = gx2 * gx2 + gy2 * gy2
            min_mag_sq = ti.min(mag1_sq, mag2_sq)

            # Structure weight
            structure_weight = 1.0
            if (
                min_mag_sq > stab_epsilon
                and mag1_sq > stab_epsilon
                and mag2_sq > stab_epsilon
            ):
                dot = gx1 * gx2 + gy1 * gy2
                cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                score = ti.max(cos_sim, 0.0) * ti.sqrt(min_mag_sq)
                structure_weight = 1.0 + gradient_weight_factor * _fast_tanh(
                    score * sensitivity
                )

            # Zero-mean Charbonnier
            diff = (ref[r, c] - comp[r, c]) - mean_diff
            total_cost += ti.sqrt(diff * diff + eps_sq) * structure_weight

        cost_out[0] = total_cost / float(h * w)

    @ti.kernel
    def _block_cost_simple_kernel(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        cost_out: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Simple SAD cost for fast coarse search."""
        total = 0.0
        for r, c in ti.ndrange(h, w):
            total += ti.abs(ref[r, c] - comp[r, c])
        cost_out[0] = total / float(h * w)


# ============================================================================
# Python API (matching C++ function signatures)
# ============================================================================


def calculate_fine_analysis(ref: np.ndarray, comp: np.ndarray) -> float:
    """
    Calculate ZMCL cost between two 1D or 2D arrays.
    Matching C++ calculate_fine_analysis().

    Args:
        ref: Reference tile (flattened or 2D)
        comp: Comparison tile (same shape as ref)

    Returns:
        Normalized cost value
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    if ref is None or comp is None or ref.size == 0:
        return 0.0

    # Ensure float32
    ref = np.ascontiguousarray(ref, dtype=np.float32)
    comp = np.ascontiguousarray(comp, dtype=np.float32)

    cost_out = ti.ndarray(ti.f32, shape=(1,))

    if ref.ndim == 1:
        # 1D path (matching original C++)
        length = ref.shape[0]
        ref_gpu = ti.ndarray(ti.f32, shape=(length,))
        comp_gpu = ti.ndarray(ti.f32, shape=(length,))
        mean_out = ti.ndarray(ti.f32, shape=(1,))

        ref_gpu.from_numpy(ref)
        comp_gpu.from_numpy(comp)

        _compute_mean_diff_kernel(ref_gpu, comp_gpu, mean_out, length)
        mean_diff = mean_out.to_numpy()[0]

        _block_cost_zmcl_kernel(ref_gpu, comp_gpu, cost_out, mean_diff, length)
        return cost_out.to_numpy()[0] / length
    else:
        # 2D path (optimized)
        h, w = ref.shape[:2]
        ref_gpu = ti.ndarray(ti.f32, shape=(h, w))
        comp_gpu = ti.ndarray(ti.f32, shape=(h, w))

        ref_gpu.from_numpy(ref.reshape(h, w))
        comp_gpu.from_numpy(comp.reshape(h, w))

        _block_cost_zmcl_2d_kernel(ref_gpu, comp_gpu, cost_out, h, w)
        return cost_out.to_numpy()[0]


def calculate_fine_analysis_gpu(
    ref_gpu, comp_gpu, cost_out_gpu, h: int, w: int
) -> None:
    """
    GPU-native version: Calculate ZMCL cost directly on GPU buffers.
    Result written to cost_out_gpu[0].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _block_cost_zmcl_2d_kernel(ref_gpu, comp_gpu, cost_out_gpu, h, w)


def calculate_simple_cost_gpu(ref_gpu, comp_gpu, cost_out_gpu, h: int, w: int) -> None:
    """
    GPU-native simple SAD cost for fast coarse search.
    Result written to cost_out_gpu[0].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")
    _block_cost_simple_kernel(ref_gpu, comp_gpu, cost_out_gpu, h, w)
