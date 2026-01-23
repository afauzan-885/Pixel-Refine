"""
Refinement - Taichi GPU Implementation
======================================
GPU-accelerated subpixel refinement functions for optical flow.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm

    try:
        from ...taichi_algorithm import common
    except (ImportError, ValueError):
        # Fallback for standalone script execution
        from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import (
            common,
        )

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
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
    def _parabolic_refinement_kernel(
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
        Parabolic fitting on 3x3 grid for subpixel refinement.
        Matching C++ parabolic_refinement().

        result_out: [refined_dx, refined_dy, confidence]
        """
        tile_area_inv = 1.0 / float(tile_w * tile_h)

        # Evaluate 9 points on 3x3 grid
        costs = ti.Vector([0.0] * 9)  # Row-major: [-1,-1], [0,-1], [1,-1], ...

        eval_idx = 0
        for ddy in ti.static(range(-1, 2)):
            for ddx in ti.static(range(-1, 2)):
                test_dx = dx + ddx
                test_dy = dy + ddy

                # Boundary check
                if (
                    tile_x + test_dx < 0
                    or tile_y + test_dy < 0
                    or tile_x + test_dx + tile_w > w
                    or tile_y + test_dy + tile_h > h
                ):
                    costs[eval_idx] = 1e10  # Large cost for out-of-bounds
                else:
                    # Calculate SAD cost
                    total_cost = 0.0
                    for r, c in ti.ndrange(tile_h, tile_w):
                        ref_val = ref_layer[tile_y + r, tile_x + c]
                        comp_val = comp_layer[
                            tile_y + test_dy + r, tile_x + test_dx + c
                        ]
                        total_cost += ti.abs(ref_val - comp_val)
                    costs[eval_idx] = total_cost * tile_area_inv

                eval_idx += 1

        # Parabolic fitting
        center_cost = costs[4]  # [0, 0]
        left_cost = costs[3]  # [-1, 0]
        right_cost = costs[5]  # [1, 0]
        top_cost = costs[1]  # [0, -1]
        bottom_cost = costs[7]  # [0, 1]

        # X-direction fit
        delta_x = 0.0
        c_coeff_x = (right_cost + left_cost - 2.0 * center_cost) / 2.0
        if ti.abs(c_coeff_x) > 1e-6:
            b_coeff_x = (right_cost - left_cost) / 2.0
            delta_x = -b_coeff_x / (2.0 * c_coeff_x)
            delta_x = tm.clamp(delta_x, -0.5, 0.5)

        # Y-direction fit
        delta_y = 0.0
        c_coeff_y = (bottom_cost + top_cost - 2.0 * center_cost) / 2.0
        if ti.abs(c_coeff_y) > 1e-6:
            b_coeff_y = (bottom_cost - top_cost) / 2.0
            delta_y = -b_coeff_y / (2.0 * c_coeff_y)
            delta_y = tm.clamp(delta_y, -0.5, 0.5)

        # Compute confidence from curvature
        curvature = ti.max(ti.abs(c_coeff_x), ti.abs(c_coeff_y))
        confidence = 0.5
        if curvature > 1e-6:
            confidence = tm.clamp(
                0.1 + (ti.log(curvature) / ti.log(10.0) + 3.0) * 0.2, 0.1, 0.9
            )

        result_out[0] = float(dx) + delta_x
        result_out[1] = float(dy) + delta_y
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

    @ti.kernel
    def _integer_search_3x3_kernel(
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
        3x3 integer search around initial position.
        result_out: [best_dx, best_dy, min_cost]
        """
        min_cost = 1e10
        best_dx = dx
        best_dy = dy

        for ddy in ti.static(range(-1, 2)):
            for ddx in ti.static(range(-1, 2)):
                test_dx = dx + ddx
                test_dy = dy + ddy

                comp_x = tile_x + test_dx
                comp_y = tile_y + test_dy

                # Boundary check
                if not (
                    comp_x < 0
                    or comp_y < 0
                    or comp_x + tile_w > w
                    or comp_y + tile_h > h
                ):
                    # Compute SAD
                    total_cost = 0.0
                    for r, c in ti.ndrange(tile_h, tile_w):
                        ref_val = ref_layer[tile_y + r, tile_x + c]
                        comp_val = comp_layer[comp_y + r, comp_x + c]
                        total_cost += ti.abs(ref_val - comp_val)

                    if total_cost < min_cost:
                        min_cost = total_cost
                        best_dx = test_dx
                        best_dy = test_dy

        result_out[0] = float(best_dx)
        result_out[1] = float(best_dy)
        result_out[2] = min_cost / float(tile_w * tile_h)


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

    _parabolic_refinement_kernel(
        ref_gpu, comp_gpu, result_out, x, y, dx, dy, tile_w, tile_h, h, w
    )

    result = result_out.to_numpy()
    refined_flow = (result[0], result[1])
    confidence = result[2]

    return refined_flow, confidence


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

    # Boundary check
    if x < 0 or y < 0 or x + tile_w > w or y + tile_h > h:
        return (float(dx), float(dy))

    ref_gpu = ti.ndarray(ti.f32, shape=(h, w))
    comp_gpu = ti.ndarray(ti.f32, shape=(h, w))
    search_result = ti.ndarray(ti.f32, shape=(3,))
    refine_result = ti.ndarray(ti.f32, shape=(3,))

    ref_gpu.from_numpy(np.ascontiguousarray(ref_layer, dtype=np.float32))
    comp_gpu.from_numpy(np.ascontiguousarray(comp_layer, dtype=np.float32))

    # Step 1: Integer 3x3 search
    _integer_search_3x3_kernel(
        ref_gpu, comp_gpu, search_result, x, y, dx, dy, tile_w, tile_h, h, w
    )

    search_res = search_result.to_numpy()
    best_dx = float(search_res[0])
    best_dy = float(search_res[1])

    # Step 2: Bicubic Iterative Refinement (Higher precision)
    _bicubic_subpixel_refinement_kernel(
        ref_gpu, comp_gpu, refine_result, x, y, best_dx, best_dy, tile_w, tile_h, h, w
    )

    result = refine_result.to_numpy()
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

    # Step 1: Integer search
    _integer_search_3x3_kernel(
        ref_gpu, comp_gpu, search_result_gpu, x, y, dx, dy, tile_w, tile_h, h, w
    )

    # Note: For full GPU-native, caller should read search_result and call parabolic
    # This version does integer search only for efficiency in pipeline
