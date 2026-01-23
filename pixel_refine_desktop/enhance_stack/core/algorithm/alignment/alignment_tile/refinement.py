"""
Refinement - Taichi GPU Implementation
======================================
GPU-accelerated subpixel refinement functions for optical flow.

Matching C++ API: refinement.cpp
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
MAX_STACK_TILE_SIZE = 64


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def _cubic_weight(x: float) -> float:
        """
        Catmull-Rom spline weight function.
        Matching C++ cubic_weight().
        """
        x = ti.abs(x)
        result = 0.0
        if x <= 1.0:
            result = 1.5 * x * x * x - 2.5 * x * x + 1.0
        elif x < 2.0:
            result = -0.5 * x * x * x + 2.5 * x * x - 4.0 * x + 2.0
        return result

    @ti.func
    def _bilinear_at(
        img: ti.types.ndarray(), x: float, y: float, h: int, w: int
    ) -> float:
        """Bilinear interpolation at fractional coordinates."""
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))

        if ix < 0 or iy < 0 or ix >= w - 1 or iy >= h - 1:
            # Clamp to edge
            ix = tm.clamp(ix, 0, w - 1)
            iy = tm.clamp(iy, 0, h - 1)
            return img[iy, ix]

        fx = x - float(ix)
        fy = y - float(iy)

        v00 = img[iy, ix]
        v01 = img[iy, ix + 1]
        v10 = img[iy + 1, ix]
        v11 = img[iy + 1, ix + 1]

        top = v00 * (1.0 - fx) + v01 * fx
        bottom = v10 * (1.0 - fx) + v11 * fx

        return top * (1.0 - fy) + bottom * fy

    @ti.func
    def _bicubic_at(
        img: ti.types.ndarray(), x: float, y: float, h: int, w: int
    ) -> float:
        """
        Bicubic interpolation at fractional coordinates.
        Matching C++ bicubic_at_optimized().
        """
        # Boundary check - fallback to bilinear for edges
        if x < 1.0 or y < 1.0 or x >= float(w - 2) or y >= float(h - 2):
            return _bilinear_at(img, x, y, h, w)

        # Integer and fractional parts
        ix = int(ti.floor(x))
        iy = int(ti.floor(y))
        fx = x - float(ix)
        fy = y - float(iy)

        # Pre-compute weights
        wx0 = _cubic_weight(fx + 1.0)
        wx1 = _cubic_weight(fx)
        wx2 = _cubic_weight(1.0 - fx)
        wx3 = _cubic_weight(2.0 - fx)

        wy0 = _cubic_weight(fy + 1.0)
        wy1 = _cubic_weight(fy)
        wy2 = _cubic_weight(1.0 - fy)
        wy3 = _cubic_weight(2.0 - fy)

        # 4x4 neighborhood interpolation
        result = 0.0
        base_x = ix - 1

        # Row 0 (iy - 1)
        row_sum = (
            img[iy - 1, base_x] * wx0
            + img[iy - 1, base_x + 1] * wx1
            + img[iy - 1, base_x + 2] * wx2
            + img[iy - 1, base_x + 3] * wx3
        )
        result += row_sum * wy0

        # Row 1 (iy)
        row_sum = (
            img[iy, base_x] * wx0
            + img[iy, base_x + 1] * wx1
            + img[iy, base_x + 2] * wx2
            + img[iy, base_x + 3] * wx3
        )
        result += row_sum * wy1

        # Row 2 (iy + 1)
        row_sum = (
            img[iy + 1, base_x] * wx0
            + img[iy + 1, base_x + 1] * wx1
            + img[iy + 1, base_x + 2] * wx2
            + img[iy + 1, base_x + 3] * wx3
        )
        result += row_sum * wy2

        # Row 3 (iy + 2)
        row_sum = (
            img[iy + 2, base_x] * wx0
            + img[iy + 2, base_x + 1] * wx1
            + img[iy + 2, base_x + 2] * wx2
            + img[iy + 2, base_x + 3] * wx3
        )
        result += row_sum * wy3

        return result

    @ti.kernel
    def _compute_sad_bicubic_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        cost_out: ti.types.ndarray(),
        tile_x: int,
        tile_y: int,
        flow_x: float,
        flow_y: float,
        tile_w: int,
        tile_h: int,
        h: int,
        w: int,
    ):
        """
        Compute SAD with bicubic interpolation.
        Matching C++ compute_sad_with_bicubic_avx().
        """
        sad_total = 0.0

        for r, c in ti.ndrange(tile_h, tile_w):
            ref_val = ref_layer[tile_y + r, tile_x + c]
            comp_x = float(tile_x + c) + flow_x
            comp_y = float(tile_y + r) + flow_y
            comp_val = _bicubic_at(comp_layer, comp_x, comp_y, h, w)
            sad_total += ti.abs(ref_val - comp_val)

        cost_out[0] = sad_total / float(tile_w * tile_h)

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
                if (
                    comp_x < 0
                    or comp_y < 0
                    or comp_x + tile_w > w
                    or comp_y + tile_h > h
                ):
                    continue

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
    best_dx = int(search_res[0])
    best_dy = int(search_res[1])

    # Step 2: Parabolic refinement
    _parabolic_refinement_kernel(
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
