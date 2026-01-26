"""
Compute Flow - Taichi GPU Implementation
=========================================
GPU-accelerated tile-based optical flow computation.

Matching C++ API: alignment_tile.cpp

Pipeline: Coarse-to-Fine Pyramid → Tile Matching → RANSAC Cleanup
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

# Import cost function helpers (GPU-compatible)
from .cost_function import compute_zmcl_cost

# Import submodule functions directly to avoid package-level shadowing
try:
    from ...taichi_algorithm.pyramid import (
        build_image_pyramid_gpu,
        upsample_flow_gpu,
    )
    from ...taichi_algorithm.ransac import (
        ransac_flow_cleanup_local,
        ransac_flow_cleanup_motion_aware,
    )
    from ...taichi_algorithm.median_filter import median_filter_flow

    # common might be useful
    from ...taichi_algorithm import common
    from ...taichi_algorithm.taichi_worker import ti_thread

    TAICHI_MODULES_AVAILABLE = True
except ImportError:
    TAICHI_MODULES_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================
class ImageAlignmentConfig:
    """Configuration constants matching C++ namespace."""

    NORMALIZATION_EPSILON = 1e-6
    EPSILON_SQ = 1e-12
    GRADIENT_WEIGHT_FACTOR = 1.4
    SENSITIVITY = 150.0
    STAB_EPSILON = 1e-6
    FLOW_UPSCALE_FACTOR = 2.0
    MIN_TILE_SIZE = 8
    MIN_PYRAMID_LAYER_SIZE = 32
    EARLY_EXIT_COST = 0.008


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _initialize_coarsest_flow_kernel(
        flow: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Initialize flow to zeros for coarsest level."""
        for r, c in ti.ndrange(h, w):
            flow[r, c, 0] = 0.0
            flow[r, c, 1] = 0.0

    @ti.kernel
    def _search_coarse_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        search_dist: int,
    ):
        """Coarse level tile matching using ZMCL cost."""
        step_y = tile_h
        step_x = tile_w

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            # Get initial flow from upsampled previous level
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            init_dx = int(ti.round(flow[center_y, center_x, 0]))
            init_dy = int(ti.round(flow[center_y, center_x, 1]))

            best_cost = 1e10
            best_dx = init_dx
            best_dy = init_dy

            for dy in range(-search_dist, search_dist + 1):
                for dx in range(-search_dist, search_dist + 1):
                    test_y = y + init_dy + dy
                    test_x = x + init_dx + dx

                    if (
                        test_y < 0
                        or test_x < 0
                        or test_y + tile_h > h
                        or test_x + tile_w > w
                    ):
                        continue

                    cost = compute_zmcl_cost(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        test_y,
                        test_x,
                        h,
                        w,
                        tile_h,
                        tile_w,
                    )

                    if cost < best_cost:
                        best_cost = cost
                        best_dx = init_dx + dx
                        best_dy = init_dy + dy

            # Write result
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = float(best_dx)
                    refined_flow[y + r, x + c, 1] = float(best_dy)

    @ti.kernel
    def _search_fine_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
    ):
        """Fine level tile matching (matching C++ processFineLayer)."""
        step_y = tile_h // 2
        step_x = tile_w // 2

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            init_dx = int(ti.round(flow[center_y, center_x, 0]))
            init_dy = int(ti.round(flow[center_y, center_x, 1]))

            best_cost = 1e10
            final_dx = float(init_dx)
            final_dy = float(init_dy)

            # Local 3x3 search around current guess
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    test_y = y + init_dy + dy
                    test_x = x + init_dx + dx

                    if (
                        test_y < 0
                        or test_x < 0
                        or test_y + tile_h > h
                        or test_x + tile_w > w
                    ):
                        continue

                    cost = compute_zmcl_cost(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        test_y,
                        test_x,
                        h,
                        w,
                        tile_h,
                        tile_w,
                    )

                    if cost < best_cost:
                        best_cost = cost
                        final_dx = float(init_dx + dx)
                        final_dy = float(init_dy + dy)

            # Write result
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = final_dx
                    refined_flow[y + r, x + c, 1] = final_dy

    @ti.kernel
    def _iterative_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        max_iters: int,
    ):
        """Iterative subpixel refinement using Gauss-Newton optimization."""
        step_y = tile_h
        step_x = tile_w

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            # Get initial flow guess
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            curr_dx = flow[center_y, center_x, 0]
            curr_dy = flow[center_y, center_x, 1]

            # Optimization Loop
            for _ in range(max_iters):
                sum_gv2_x = 0.0
                sum_gv2_y = 0.0
                sum_diff_gv_x = 0.0
                sum_diff_gv_y = 0.0

                stride = 2
                for ir, ic in ti.ndrange(tile_h // stride, tile_w // stride):
                    r = ir * stride
                    c = ic * stride
                    ref_val = ref_layer[y + r, x + c]
                    tx = float(x + c) + curr_dx
                    ty = float(y + r) + curr_dy

                    comp_val = common.bicubic_at(comp_layer, tx, ty)

                    # Finite difference for local gradient on comp_layer
                    eps = 0.2
                    gv_x = (
                        common.bilinear_at(comp_layer, tx + eps, ty)
                        - common.bilinear_at(comp_layer, tx - eps, ty)
                    ) / (2.0 * eps)
                    gv_y = (
                        common.bilinear_at(comp_layer, tx, ty + eps)
                        - common.bilinear_at(comp_layer, tx, ty - eps)
                    ) / (2.0 * eps)

                    diff = comp_val - ref_val
                    sum_gv2_x += gv_x * gv_x
                    sum_gv2_y += gv_y * gv_y
                    sum_diff_gv_x += diff * gv_x
                    sum_diff_gv_y += diff * gv_y

                # Simple GN Update (alpha damping = 0.5)
                alpha = 0.5
                if sum_gv2_x > 1e-6:
                    curr_dx -= alpha * sum_diff_gv_x / sum_gv2_x
                if sum_gv2_y > 1e-6:
                    curr_dy -= alpha * sum_diff_gv_y / sum_gv2_y

                # Stability clamp
                curr_dx = tm.clamp(curr_dx, -50.0, 50.0)
                curr_dy = tm.clamp(curr_dy, -50.0, 50.0)

            # Write result
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = curr_dx
                    refined_flow[y + r, x + c, 1] = curr_dy


# ============================================================================
# Helper Functions
# ============================================================================


def process_single_layer(
    ref_layer: np.ndarray,
    comp_layer: np.ndarray,
    previous_flow_gpu,  # ti.ndarray or None
    layer_index: int,
    total_layers: int,
    tile_h: int,
    tile_w: int,
    base_search_dist: float,
) -> any:  # Returns ti.ndarray (GPU)
    """
    Process tile matching for a single pyramid layer.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_coarsest_layer = layer_index == total_layers - 1
    is_finest_layer = layer_index == 0

    h, w = ref_layer.shape[:2]

    # Upload images to GPU if needed
    ref_gpu = None
    comp_gpu = None
    ref_is_temp = False
    comp_is_temp = False

    if hasattr(ref_layer, "shape") and not isinstance(ref_layer, np.ndarray):
        ref_gpu = ref_layer
    else:
        ref_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider="pool")
        ref_gpu.from_numpy(np.ascontiguousarray(ref_layer, dtype=np.float32))
        ref_is_temp = True

    if hasattr(comp_layer, "shape") and not isinstance(comp_layer, np.ndarray):
        comp_gpu = comp_layer
    else:
        comp_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider="pool")
        comp_gpu.from_numpy(np.ascontiguousarray(comp_layer, dtype=np.float32))
        comp_is_temp = True

    # 1. Initialize/Upsample flow
    flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")

    if is_coarsest_layer:
        _initialize_coarsest_flow_kernel(flow_gpu, h, w)
    else:
        if previous_flow_gpu is None:
            _initialize_coarsest_flow_kernel(flow_gpu, h, w)
        else:
            upsample_flow_gpu(
                src_gpu=previous_flow_gpu,
                dst_gpu=flow_gpu,
                scale=ImageAlignmentConfig.FLOW_UPSCALE_FACTOR,
            )

    # 2. Match
    current_tile_h = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_h, h))
    current_tile_w = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_w, w))

    refined_flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")
    _initialize_coarsest_flow_kernel(refined_flow_gpu, h, w)

    if is_finest_layer:
        _search_fine_level_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
        )

        # Subpixel Refinement
        common.copy_field(refined_flow_gpu, flow_gpu)
        _iterative_subpixel_refinement_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
            max_iters=5,
        )
    else:
        # Coarse layers: use search_dist
        depth_factor = 1.0 / (2.0 ** (total_layers - layer_index - 1))
        current_search_dist = max(1, int(base_search_dist * depth_factor))

        _search_coarse_level_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
            current_search_dist,
        )

    # Cleanup
    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)
    common.release_temp_buffer(flow_gpu)

    # 3. Post-process
    filtered_flow_gpu = common.get_temp_buffer(
        (h, w, 2), ti.f32, buffer_provider="pool"
    )
    median_filter_flow(
        src=refined_flow_gpu, dst=filtered_flow_gpu, kernel_size=3, enable_tiling=False
    )
    common.release_temp_buffer(refined_flow_gpu)

    # 4. RANSAC
    if layer_index >= 2:
        threshold = max(1.5, 4.0 - (layer_index * 0.8))
        iterations = max(5, 15 - (layer_index * 2))
        motion_threshold = max(1.5, 2.5 - (layer_index * 0.3))

        ransac_out_gpu = ransac_flow_cleanup_motion_aware(
            filtered_flow_gpu,
            threshold=threshold,
            motion_threshold=motion_threshold,
            n_iterations=iterations,
        )
        common.release_temp_buffer(filtered_flow_gpu)
        return ransac_out_gpu
    else:
        return filtered_flow_gpu


@ti_thread
def compute_alignment_flow(
    ref_work_data: np.ndarray,
    current_work_data: np.ndarray,
    tile_h: int = 16,
    tile_w: int = 16,
    n_layers: int = 3,
    search_dist: float = 2.0,
    return_confidence: bool = False,
) -> any:
    """
    Compute alignment flow - Stable Version.
    """
    if not TAICHI_AVAILABLE or not TAICHI_MODULES_AVAILABLE:
        raise ImportError("Taichi not ready")

    ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_work_data, dtype=ti.f32)
    comp_gpu, comp_is_temp = common.ensure_taichi_field(current_work_data, dtype=ti.f32)

    ref_pyramid = build_image_pyramid_gpu(
        ref_gpu,
        n_levels=n_layers,
        min_size=ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
    )
    current_pyramid = build_image_pyramid_gpu(
        comp_gpu,
        n_levels=n_layers,
        min_size=ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
    )

    actual_layers = min(len(ref_pyramid), len(current_pyramid))
    flow_gpu = None

    for i in range(actual_layers - 1, -1, -1):
        prev_flow = flow_gpu
        flow_gpu = process_single_layer(
            ref_pyramid[i],
            current_pyramid[i],
            prev_flow,
            i,
            actual_layers,
            tile_h,
            tile_w,
            search_dist,
        )
        if prev_flow is not None:
            common.release_temp_buffer(prev_flow)

    # Final cleanup
    if flow_gpu is not None:
        old_flow = flow_gpu
        flow_gpu = ransac_flow_cleanup_local(
            old_flow, block_size=64, threshold=2.0, n_iterations=3
        )
        common.release_temp_buffer(old_flow)

    for i in range(1, len(ref_pyramid)):
        common.release_temp_buffer(ref_pyramid[i])
    for i in range(1, len(current_pyramid)):
        common.release_temp_buffer(current_pyramid[i])

    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)

    return flow_gpu


def free_flow_memory(flow_data):
    """Free flow memory (no-op in Python)."""
    pass
