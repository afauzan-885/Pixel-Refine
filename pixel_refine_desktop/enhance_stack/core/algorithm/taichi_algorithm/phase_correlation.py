"""
Global Spatial Search (Pseudo-Phase Correlation) - Taichi GPU Implementation
============================================================================
Provides an extremely fast global shift estimator using exhaustive spatial ZMSSD on
the coarsest pyramid layer. Acts as a replacement for OpenCV's CPU phaseCorrelate.
"""

import numpy as np

try:
    import taichi as ti

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None

if TAICHI_AVAILABLE:

    @ti.kernel
    def _compute_global_zncc_surface(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        cost_surface: ti.types.ndarray(),
        max_shift: int,
        h: int,
        w: int,
    ):
        """
        Computes the ZNCC (Zero-mean Normalized Cross-Correlation) cost across a shift grid.
        ZNCC is highly robust to illumination changes and is a spatial approximation of phase correlation.
        Cost is defined as (1.0 - ZNCC), so 0.0 means perfect match.
        """
        for dy, dx in ti.ndrange(
            (-max_shift, max_shift + 1), (-max_shift, max_shift + 1)
        ):
            # Pass 1: Calculate Means
            sum_ref = 0.0
            sum_comp = 0.0
            count = 0.0

            for y in range(max_shift, h - max_shift):
                for x in range(max_shift, w - max_shift):
                    comp_y = y + dy
                    comp_x = x + dx

                    sum_ref += float(ref[y, x])
                    sum_comp += float(comp[comp_y, comp_x])
                    count += 1.0

            if count > 0.0:
                mean_ref = sum_ref / count
                mean_comp = sum_comp / count

                # Pass 2: Calculate ZNCC
                numerator = 0.0
                sum_sq_ref = 0.0
                sum_sq_comp = 0.0

                for y in range(max_shift, h - max_shift):
                    for x in range(max_shift, w - max_shift):
                        comp_y = y + dy
                        comp_x = x + dx

                        val_ref = float(ref[y, x]) - mean_ref
                        val_comp = float(comp[comp_y, comp_x]) - mean_comp

                        numerator += val_ref * val_comp
                        sum_sq_ref += val_ref * val_ref
                        sum_sq_comp += val_comp * val_comp

                denominator = ti.sqrt(sum_sq_ref * sum_sq_comp)

                # Protect against division by zero (e.g. flat textureless regions)
                if denominator > 1e-6:
                    zncc = numerator / denominator
                    # Convert correlation [-1, 1] to cost [0, 2] where 0 is best
                    # Max correlation (1.0) -> Cost (0.0)
                    cost_surface[dy + max_shift, dx + max_shift] = 1.0 - zncc
                else:
                    cost_surface[dy + max_shift, dx + max_shift] = 1e10
            else:
                cost_surface[dy + max_shift, dx + max_shift] = 1e10


def phase_correlation(
    ref_layer: np.ndarray, comp_layer: np.ndarray, max_shift: int = 16
):
    """
    Estimates the dominant global translation (dx, dy) between two 2D images.
    Returns:
        (best_dx, best_dy, best_cost)
    """
    if not TAICHI_AVAILABLE:
        raise RuntimeError("Taichi is not available")

    h, w = ref_layer.shape[:2]

    # Pre-allocate cost surface
    size = 2 * max_shift + 1
    cost_surface = np.full((size, size), 1e10, dtype=np.float32)

    _compute_global_zncc_surface(ref_layer, comp_layer, cost_surface, max_shift, h, w)

    # Find the minimum cost location
    min_idx = np.unravel_index(np.argmin(cost_surface), cost_surface.shape)

    best_dy = int(min_idx[0]) - max_shift
    best_dx = int(min_idx[1]) - max_shift
    best_cost = float(cost_surface[min_idx[0], min_idx[1]])

    return best_dx, best_dy, best_cost
