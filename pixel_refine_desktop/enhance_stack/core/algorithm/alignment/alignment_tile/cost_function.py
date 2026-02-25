"""
Cost Function - Taichi GPU Implementation
==========================================
GPU-accelerated cost calculation functions for optical flow tile matching.
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
# Constants
# ============================================================================


# ============================================================================
# Helper Functions
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def fast_tanh(x: float) -> float:
        """
        Fast approximation of tanh for GPU performance.
        Based on the C++ implementation.
        """
        res = 0.0
        if x >= 3.0:
            res = 1.0
        elif x <= -3.0:
            res = -1.0
        else:
            x2 = x * x
            res = x * (27.0 + x2) / (27.0 + 9.0 * x2)
        return res


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def compute_zmsad_cost(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y_ref: int,
        x_ref: int,
        y_comp: int,
        x_comp: int,
        tile_h: int,
        tile_w: int,
    ) -> float:
        """
        Compute Zero-Mean Sum of Absolute Differences (ZMSAD) cost.
        Optimized to reduce memory passes.
        """
        sum_diff = 0.0
        # Single pass for mean
        for r, c in ti.ndrange(tile_h, tile_w):
            sum_diff += ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]

        mean_diff = sum_diff / float(tile_h * tile_w)

        total_abs_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            diff = (
                ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]
            ) - mean_diff
            total_abs_diff += ti.abs(diff)

        return total_abs_diff / float(tile_h * tile_w)

    @ti.func
    def compute_zmssd_cost(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y_ref: int,
        x_ref: int,
        y_comp: int,
        x_comp: int,
        tile_h: int,
        tile_w: int,
    ) -> float:
        """
        Compute Zero-Mean Sum of Squared Differences (ZM-SSD) cost.
        Optimized using single-pass variance formula: E[X^2] - (E[X])^2
        """
        sum_diff = 0.0
        sum_sq_diff = 0.0

        # Single pass for both sum and sum of squares
        for r, c in ti.ndrange(tile_h, tile_w):
            diff = float(ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c])
            sum_diff += diff
            sum_sq_diff += diff * diff

        n = float(tile_h * tile_w)
        mean_diff = sum_diff / n

        # Variance formula: Mean(X^2) - Mean(X)^2
        # Use ti.max(0.0, ...) to avoid precision issues resulting in negative values
        return ti.max(0.0, (sum_sq_diff / n) - (mean_diff * mean_diff))

    @ti.func
    def compute_zmcl_cost(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y_ref: int,
        x_ref: int,
        y_comp: int,
        x_comp: int,
        tile_h: int,
        tile_w: int,
    ) -> float:
        """
        Compute Zero-Mean Charbonnier cost with Gradient/Structure Weighting (ZMCL).
        This is a Taichi equivalent of the C++ block_cost_zmcl_avx.
        Returns the normalized cost (total_cost / tile_area).
        """
        eps_sq = 1e-12
        stab_epsilon = 1e-6
        gradient_weight_factor = 1.4
        sensitivity = 150.0

        sum_diff = 0.0
        n = float(tile_h * tile_w)

        # PASS 1: Calculate Mean Difference
        for r, c in ti.ndrange(tile_h, tile_w):
            sum_diff += float(ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c])

        mean_diff = sum_diff / n
        total_cost = 0.0

        # Constants for boundaries
        h_total, w_total = ref.shape[0], ref.shape[1]
        h_comp_total, w_comp_total = comp.shape[0], comp.shape[1]

        # Calculate safe boundaries OUTSIDE the loop for fast checking
        safe_r_start = ti.max(1, 1 - y_ref, 1 - y_comp)
        safe_c_start = ti.max(1, 1 - x_ref, 1 - x_comp)
        safe_r_end = ti.min(tile_h, h_total - 1 - y_ref, h_comp_total - 1 - y_comp)
        safe_c_end = ti.min(tile_w, w_total - 1 - x_ref, w_comp_total - 1 - x_comp)

        # PASS 2: Charbonnier + Gradient Weighting
        for r, c in ti.ndrange(tile_h, tile_w):
            ry = y_ref + r
            rx = x_ref + c
            cy = y_comp + r
            cx = x_comp + c

            charb_diff = float(ref[ry, rx] - comp[cy, cx]) - mean_diff
            charb_base = tm.sqrt(charb_diff * charb_diff + eps_sq)

            structure_weight = 1.0

            # Gradient calculation using Cross/Sobel-like approach
            # Using pre-calculated boundaries makes this `if` way faster
            if (
                r >= safe_r_start
                and r < safe_r_end
                and c >= safe_c_start
                and c < safe_c_end
            ):
                # Gradient X (Horizontal)
                gx1 = float(ref[ry, rx + 1] - ref[ry, rx - 1])
                gx2 = float(comp[cy, cx + 1] - comp[cy, cx - 1])

                # Gradient Y (Vertical) - making it 2D isotropic instead of 1D flattened
                gy1 = float(ref[ry + 1, rx] - ref[ry - 1, rx])
                gy2 = float(comp[cy + 1, cx] - comp[cy - 1, cx])

                # 2D Gradient Magnitude Squared
                mag1_sq = gx1 * gx1 + gy1 * gy1
                mag2_sq = gx2 * gx2 + gy2 * gy2
                min_mag_sq = mag1_sq if mag1_sq < mag2_sq else mag2_sq

                if (
                    min_mag_sq > stab_epsilon
                    and mag1_sq > stab_epsilon
                    and mag2_sq > stab_epsilon
                ):
                    dot = gx1 * gx2 + gy1 * gy2
                    cos_sim = dot / tm.sqrt(mag1_sq * mag2_sq)
                    score = (cos_sim if cos_sim > 0.0 else 0.0) * tm.sqrt(min_mag_sq)
                    structure_weight = 1.0 + gradient_weight_factor * fast_tanh(
                        score * sensitivity
                    )

            total_cost += charb_base * structure_weight

        return total_cost / n
