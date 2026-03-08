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
    def compute_l1_cost(
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
        Compute Sum of Absolute Differences (SAD / L1) cost.
        This is the standard HDR+ alignment cost metric.
        Simple, fast, and robust to noise.
        """
        total_abs_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            diff = ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]
            total_abs_diff += ti.abs(diff)

        return total_abs_diff / float(tile_h * tile_w)
