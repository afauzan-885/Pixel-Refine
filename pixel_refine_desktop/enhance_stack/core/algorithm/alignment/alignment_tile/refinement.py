"""
Refinement - Taichi GPU Implementation
======================================
GPU-accelerated subpixel refinement functions for optical flow.
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

try:
    from . import cost_function
except ImportError:
    # Facilitate standalone tests
    try:
        import cost_function
    except ImportError:
        cost_function = None

try:
    from ...taichi_algorithm import common
except ImportError:
    # Facilitate standalone tests
    try:
        import common
    except ImportError:
        common = None

# ============================================================================
# Constants
# ============================================================================
MAX_STACK_TILE_SIZE = 64


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _subpixel_refinement_parabolic_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        result_out: ti.types.ndarray(),
        tile_x: int,
        tile_y: int,
        dx: int,
        dy: int,
        tile_w: int,
        tile_h: int,
        h: int,
        w: int,
    ):
        """
        Integrated Subpixel Refinement:
        1. 3x3 Integer search using ZMCL cost.
        2. 3x3 Parabolic fitting using SAD cost around the best integer position.
        Matching C++ logic flow.
        """
        # Step 1: Integer search (3x3 ZMCL)
        min_cost = 1e10
        best_dx = dx
        best_dy = dy

        for ddy in ti.static(range(-1, 2)):
            for ddx in ti.static(range(-1, 2)):
                test_dx = dx + ddx
                test_dy = dy + ddy

                if (
                    tile_x + test_dx >= 0
                    and tile_y + test_dy >= 0
                    and tile_x + test_dx + tile_w <= w
                    and tile_y + test_dy + tile_h <= h
                ):
                    cost = cost_function.compute_zmsad_cost(
                        ref_layer,
                        comp_layer,
                        tile_y,
                        tile_x,
                        tile_y + test_dy,
                        tile_x + test_dx,
                        tile_h,
                        tile_w,
                    )
                    if cost < min_cost:
                        min_cost = cost
                        best_dx = test_dx
                        best_dy = test_dy

        # Step 2: Parabolic Refinement using SAD (3x3 grid around best_dx, best_dy)
        costs = ti.Vector([0.0] * 9)
        eval_idx = 0
        for ddy in ti.static(range(-1, 2)):
            for ddx in ti.static(range(-1, 2)):
                test_dx = best_dx + ddx
                test_dy = best_dy + ddy

                if (
                    tile_x + test_dx < 0
                    or tile_y + test_dy < 0
                    or tile_x + test_dx + tile_w > w
                    or tile_y + test_dy + tile_h > h
                ):
                    costs[eval_idx] = 1e10
                else:
                    costs[eval_idx] = cost_function.compute_zmssd_cost(
                        ref_layer,
                        comp_layer,
                        tile_y,
                        tile_x,
                        tile_y + test_dy,
                        tile_x + test_dx,
                        tile_h,
                        tile_w,
                    )
                eval_idx += 1

        # Parabolic fitting on the SAD surface
        center_cost = costs[4]
        left_cost = costs[3]
        right_cost = costs[5]
        top_cost = costs[1]
        bottom_cost = costs[7]

        delta_x = 0.0
        c_coeff_x = (right_cost + left_cost - 2.0 * center_cost) / 2.0
        if ti.abs(c_coeff_x) > 1e-6:
            b_coeff_x = (right_cost - left_cost) / 2.0
            delta_x = tm.clamp(-b_coeff_x / (2.0 * c_coeff_x), -0.5, 0.5)

        delta_y = 0.0
        c_coeff_y = (bottom_cost + top_cost - 2.0 * center_cost) / 2.0
        if ti.abs(c_coeff_y) > 1e-6:
            b_coeff_y = (bottom_cost - top_cost) / 2.0
            delta_y = tm.clamp(-b_coeff_y / (2.0 * c_coeff_y), -0.5, 0.5)

        # Confidence based on curvature (matching C++)
        curvature = ti.max(ti.abs(c_coeff_x), ti.abs(c_coeff_y))
        confidence = 0.5
        if curvature > 1e-6:
            confidence = tm.clamp(
                0.1 + (ti.log(curvature) / ti.log(10.0) + 3.0) * 0.2, 0.1, 0.9
            )

        result_out[0] = float(best_dx) + delta_x
        result_out[1] = float(best_dy) + delta_y
        result_out[2] = confidence

    @ti.kernel
    def _bicubic_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        result_out: ti.types.ndarray(),
        tile_x: int,
        tile_y: int,
        dx: float,
        dy: float,
        tile_w: int,
        tile_h: int,
        h: int,
        w: int,
    ):
        """
        Subpixel refinement using iterative bicubic sampling.
        Performs a local grid search for higher precision.
        """
        best_vx = dx
        best_vy = dy
        best_cost = 1e10

        # Initial step for local refinement (e.g. 0.5 pixel)
        step = 0.5

        # 3 iterations of local grid search (±step)
        for _ in ti.static(range(4)):
            best_local_vx = best_vx
            best_local_vy = best_vy

            for ddy in ti.static(range(-1, 2)):
                for ddx in ti.static(range(-1, 2)):
                    vx = best_vx + float(ddx) * step
                    vy = best_vy + float(ddy) * step

                    # Boundary check for tile center
                    if not (
                        tile_x + vx < 1.0
                        or tile_y + vy < 1.0
                        or tile_x + vx + tile_w > w - 2
                        or tile_y + vy + tile_h > h - 2
                    ):
                        # Evaluate SAD cost at (vx, vy) using bicubic interpolation
                        total_cost = 0.0
                        for r, c in ti.ndrange(tile_h, tile_w):
                            ref_val = ref_layer[tile_y + r, tile_x + c]
                            comp_val = common.bicubic_at(
                                comp_layer,
                                float(tile_x + c) + vx,
                                float(tile_y + r) + vy,
                            )
                            total_cost += ti.abs(ref_val - comp_val)

                        cost = total_cost / float(tile_w * tile_h)
                        if cost < best_cost:
                            best_cost = cost
                            best_local_vx = vx
                            best_local_vy = vy

            best_vx = best_local_vx
            best_vy = best_local_vy
            step *= 0.5  # Reduce step size for next iteration

        result_out[0] = best_vx
        result_out[1] = best_vy
        result_out[2] = 0.9  # High confidence for bicubic


# ============================================================================
# Python API (matching C++ function signatures)
# ============================================================================


def parabolic_refinement(
    ref_layer: np.ndarray,
    comp_layer: np.ndarray,
    x: int,
    y: int,
    dx: int,
    dy: int,
    tile_w: int,
    tile_h: int,
) -> tuple:
    """
    Parabolic fitting for subpixel refinement.
    Matching C++ parabolic_refinement().

    Args:
        ref_layer: Reference image (2D float32)
        comp_layer: Comparison image (2D float32)
        x, y: Tile top-left position in reference
        dx, dy: Integer displacement to refine
        tile_w, tile_h: Tile dimensions

    Returns:
        Tuple of (refined_flow, confidence)
        refined_flow: (x, y) subpixel displacement
        confidence: 0.0-1.0 confidence score
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = ref_layer.shape[:2]

    ref_gpu = ti.ndarray(ti.f32, shape=(h, w))
    comp_gpu = ti.ndarray(ti.f32, shape=(h, w))
    result_out = ti.ndarray(ti.f32, shape=(3,))

    ref_gpu.from_numpy(np.ascontiguousarray(ref_layer, dtype=np.float32))
    comp_gpu.from_numpy(np.ascontiguousarray(comp_layer, dtype=np.float32))

    return (result[0], result[1]), result[2]


def subpixel_refinement(
    ref_layer: np.ndarray,
    comp_layer: np.ndarray,
    x: int,
    y: int,
    dx: int,
    dy: int,
    tile_w: int,
    tile_h: int,
) -> tuple:
    """
    Combined integer search + parabolic refinement.
    Matching C++ subpixel_refinement().

    Args:
        ref_layer: Reference image (2D float32)
        comp_layer: Comparison image (2D float32)
        x, y: Tile top-left position in reference
        dx, dy: Initial integer displacement
        tile_w, tile_h: Tile dimensions

    Returns:
        Tuple (refined_dx, refined_dy) with subpixel accuracy
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = ref_layer.shape[:2]

    # Initialize GPU buffers if they don't exist
    ref_gpu = ti.ndarray(ti.f32, shape=(h, w))
    comp_gpu = ti.ndarray(ti.f32, shape=(h, w))
    result_out = ti.ndarray(ti.f32, shape=(3,))

    ref_gpu.from_numpy(np.ascontiguousarray(ref_layer, dtype=np.float32))
    comp_gpu.from_numpy(np.ascontiguousarray(comp_layer, dtype=np.float32))

    # Boundary check
    if x < 0 or y < 0 or x + tile_w > w or y + tile_h > h:
        return (float(dx), float(dy))

    # Combined Integer Search + Parabolic Refinement in one kernel
    _subpixel_refinement_parabolic_kernel(
        ref_gpu, comp_gpu, result_out, x, y, dx, dy, tile_w, tile_h, h, w
    )

    result = result_out.to_numpy()
    return (result[0], result[1])


def subpixel_refinement_gpu(
    ref_gpu,
    comp_gpu,
    search_result_gpu,
    refine_result_gpu,
    x: int,
    y: int,
    dx: int,
    dy: int,
    tile_w: int,
    tile_h: int,
    h: int,
    w: int,
) -> None:
    """
    GPU-native version: Performs refinement directly on GPU buffers.
    Results written to search_result_gpu and refine_result_gpu.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Integrated subpixel refinement
    _subpixel_refinement_parabolic_kernel(
        ref_gpu,
        comp_gpu,
        refine_result_gpu,
        x,
        y,
        dx,
        dy,
        tile_w,
        tile_h,
        h,
        w,
    )
