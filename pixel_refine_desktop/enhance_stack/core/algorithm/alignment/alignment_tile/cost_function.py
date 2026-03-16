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

@ti.func
def reflect_idx(idx: int, size: int) -> int:
    """Branchless BORDER_REFLECT_101 implementation for cost functions."""
    res = idx
    if res < 0:
        res = -res
    if res >= size:
        res = 2 * (size - 1) - res
    return tm.clamp(res, 0, size - 1)


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
        h_ref, w_ref = ref.shape[0], ref.shape[1]
        h_comp, w_comp = comp.shape[0], comp.shape[1]

        # Single pass for mean
        for r, c in ti.ndrange(tile_h, tile_w):
            img_y_ref = reflect_idx(y_ref + r, h_ref)
            img_x_ref = reflect_idx(x_ref + c, w_ref)
            img_y_comp = reflect_idx(y_comp + r, h_comp)
            img_x_comp = reflect_idx(x_comp + c, w_comp)
            sum_diff += ref[img_y_ref, img_x_ref] - comp[img_y_comp, img_x_comp]

        mean_diff = sum_diff / float(tile_h * tile_w)

        total_abs_diff = 0.0
        for r, c in ti.ndrange(tile_h, tile_w):
            img_y_ref = reflect_idx(y_ref + r, h_ref)
            img_x_ref = reflect_idx(x_ref + c, w_ref)
            img_y_comp = reflect_idx(y_comp + r, h_comp)
            img_x_comp = reflect_idx(x_comp + c, w_comp)
            diff = (
                ref[img_y_ref, img_x_ref] - comp[img_y_comp, img_x_comp]
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
        h_ref, w_ref = ref.shape[0], ref.shape[1]
        h_comp, w_comp = comp.shape[0], comp.shape[1]

        # Single pass for both sum and sum of squares
        for r, c in ti.ndrange(tile_h, tile_w):
            img_y_ref = reflect_idx(y_ref + r, h_ref)
            img_x_ref = reflect_idx(x_ref + c, w_ref)
            img_y_comp = reflect_idx(y_comp + r, h_comp)
            img_x_comp = reflect_idx(x_comp + c, w_comp)

            diff = float(ref[img_y_ref, img_x_ref] - comp[img_y_comp, img_x_comp])
            sum_diff += diff
            sum_sq_diff += diff * diff

        n = float(tile_h * tile_w)
        mean_diff = sum_diff / n

        # Variance formula: Mean(X^2) - Mean(X)^2
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
        h_ref, w_ref = ref.shape[0], ref.shape[1]
        h_comp, w_comp = comp.shape[0], comp.shape[1]

        for r, c in ti.ndrange(tile_h, tile_w):
            img_y_ref = reflect_idx(y_ref + r, h_ref)
            img_x_ref = reflect_idx(x_ref + c, w_ref)
            img_y_comp = reflect_idx(y_comp + r, h_comp)
            img_x_comp = reflect_idx(x_comp + c, w_comp)

            diff = ref[img_y_ref, img_x_ref] - comp[img_y_comp, img_x_comp]
            total_abs_diff += ti.abs(diff)

        return total_abs_diff / float(tile_h * tile_w)
