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
    def _compute_global_zmssd_surface(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        cost_surface: ti.types.ndarray(),
        max_shift: int,
        h: int,
        w: int,
    ):
        """
        Computes the ZMSSD cost across a massive shift grid for global motion estimation.
        """
        for dy, dx in ti.ndrange(
            (-max_shift, max_shift + 1), (-max_shift, max_shift + 1)
        ):
            sum_diff = 0.0
            sum_sq_diff = 0.0
            count = 0.0

            # The evaluation window stays safely inside the image boundaries
            # to make sure all shifts are evaluating exactly the same number of pixels
            # and don't go out-of-bounds.
            for y in range(max_shift, h - max_shift):
                for x in range(max_shift, w - max_shift):
                    comp_y = y + dy
                    comp_x = x + dx

                    diff = float(ref[y, x] - comp[comp_y, comp_x])
                    sum_diff += diff
                    sum_sq_diff += diff * diff
                    count += 1.0

            if count > 0.0:
                mean = sum_diff / count
                zmssd = (sum_sq_diff / count) - (mean * mean)

                # Write to 2D cost surface mapping [-max_shift, max_shift] to [0, 2*max_shift]
                cost_surface[dy + max_shift, dx + max_shift] = zmssd
            else:
                cost_surface[dy + max_shift, dx + max_shift] = 1e10


def estimate_global_shift_taichi(
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

    _compute_global_zmssd_surface(ref_layer, comp_layer, cost_surface, max_shift, h, w)

    # Find the minimum cost location
    min_idx = np.unravel_index(np.argmin(cost_surface), cost_surface.shape)

    best_dy = int(min_idx[0]) - max_shift
    best_dx = int(min_idx[1]) - max_shift
    best_cost = float(cost_surface[min_idx[0], min_idx[1]])

    return best_dx, best_dy, best_cost
