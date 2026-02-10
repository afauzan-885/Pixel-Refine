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
        Extremely fast and robust to uniform illumination changes.
        """
        # Pass 1: Compute mean difference
        sum_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            sum_diff += ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]

        mean_diff = sum_diff / float(tile_h * tile_w)

        # Pass 2: Sum of Absolute Differences with mean subtraction
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
        Provides a smoother "U-shaped" cost surface ideal for parabolic fitting.
        """
        # Pass 1: Compute mean difference
        sum_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            sum_diff += ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]

        mean_diff = sum_diff / float(tile_h * tile_w)

        # Pass 2: Sum of Squared Differences with mean subtraction
        total_sq_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            diff = (
                ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]
            ) - mean_diff
            total_sq_diff += diff * diff

        return total_sq_diff / float(tile_h * tile_w)
