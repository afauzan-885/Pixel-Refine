"""
Compute Flow - Taichi GPU Implementation
=========================================
Pure GPU-accelerated tile-based optical flow computation.

Matching C++ API: alignment_tile.cpp

Pipeline: Coarse-to-Fine Pyramid → Tile Matching → Median Filter
Note: All pyramid processing stays on GPU to minimize CPU-GPU transfer overhead.
"""

import numpy as np
import time

try:
    import taichi as ti
    import taichi.math as tm

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

# Import cost function helpers (GPU-compatible)
from . import cost_function

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

    FLOW_UPSCALE_FACTOR = 2.0
    MIN_TILE_SIZE = 8
    MIN_PYRAMID_LAYER_SIZE = 32
    EARLY_EXIT_COST = 0.0001
    ADAPTIVE_THRESHOLD = 0.005  # Threshold for expanding search area
    ENABLE_MEDIAN_FILTER = False  # Experiment: Disable median filter


# ============================================================================
# Taichi Kernels
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def _block_search_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        search_radius: int,
    ):
        """Perform a wide-area block search for initial alignment."""
        step_y = tile_h
        step_x = tile_w

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            best_cost = 1e10
            best_dx = 0.0
            best_dy = 0.0

            # Wide area exhaustive search
            for dy in range(-search_radius, search_radius + 1):
                for dx in range(-search_radius, search_radius + 1):
                    test_y = y + dy
                    test_x = x + dx

                    if (
                        test_y < 0
                        or test_x < 0
                        or test_y + tile_h > h
                        or test_x + tile_w > w
                    ):
                        continue

                    cost = cost_function.compute_zmssd_cost(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        test_y,
                        test_x,
                        tile_h,
                        tile_w,
                    )

                    if cost < best_cost:
                        best_cost = cost
                        best_dx = float(dx)
                        best_dy = float(dy)

            # Broadcast best match to all pixels in the tile
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = best_dx
                    refined_flow[y + r, x + c, 1] = best_dy

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
        adaptive_threshold: float,
    ):
        """Coarse level tile matching using ZM-SSD cost with adaptive search."""
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

                    cost = cost_function.compute_zmssd_cost(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        test_y,
                        test_x,
                        tile_h,
                        tile_w,
                    )

                    if cost < best_cost:
                        best_cost = cost
                        best_dx = init_dx + dx
                        best_dy = init_dy + dy

            # Adaptive Pass: If best_cost is high, expand search area (3x)
            if best_cost > adaptive_threshold:
                expanded_dist = search_dist * 3
                for dy in range(-expanded_dist, expanded_dist + 1):
                    for dx in range(-expanded_dist, expanded_dist + 1):
                        # Skip area already checked
                        if (
                            dy >= -search_dist
                            and dy <= search_dist
                            and dx >= -search_dist
                            and dx <= search_dist
                        ):
                            continue

                        test_y = y + init_dy + dy
                        test_x = x + init_dx + dx

                        if (
                            test_y < 0
                            or test_x < 0
                            or test_y + tile_h > h
                            or test_x + tile_w > w
                        ):
                            continue

                        cost = cost_function.compute_zmssd_cost(
                            ref_layer,
                            comp_layer,
                            y,
                            x,
                            test_y,
                            test_x,
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
        """Fine level tile matching using ZMSAD cost."""
        step_y = tile_h
        step_x = tile_w

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

                    cost = cost_function.compute_zmssd_cost(
                        ref_layer,
                        comp_layer,
                        y,
                        x,
                        test_y,
                        test_x,
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
    def _parabolic_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
    ):
        """Subpixel refinement using parabolic fitting on ZMSAD surface."""
        step_y = tile_h
        step_x = tile_w

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            # Get integer flow from previous search result
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            int_dx = int(ti.round(flow[center_y, center_x, 0]))
            int_dy = int(ti.round(flow[center_y, center_x, 1]))

            # Evaluate neighbors in X
            c_m1_x = (
                cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int_dy,
                    x + int_dx - 1,
                    tile_h,
                    tile_w,
                )
                if x + int_dx - 1 >= 0
                else 1e10
            )
            c_p1_x = (
                cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int_dy,
                    x + int_dx + 1,
                    tile_h,
                    tile_w,
                )
                if x + int_dx + 1 + tile_w <= w
                else 1e10
            )
            c_0_0 = cost_function.compute_zmssd_cost(
                ref_layer, comp_layer, y, x, y + int_dy, x + int_dx, tile_h, tile_w
            )

            # Evaluate neighbors in Y
            c_m1_y = (
                cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int_dy - 1,
                    x + int_dx,
                    tile_h,
                    tile_w,
                )
                if y + int_dy - 1 >= 0
                else 1e10
            )
            c_p1_y = (
                cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int_dy + 1,
                    x + int_dx,
                    tile_h,
                    tile_w,
                )
                if y + int_dy + 1 + tile_h <= h
                else 1e10
            )

            # Fit parabolas
            delta_x = 0.0
            denom_x = 2.0 * (c_p1_x + c_m1_x - 2.0 * c_0_0)
            if ti.abs(denom_x) > 1e-6:
                delta_x = -(c_p1_x - c_m1_x) / denom_x
            delta_x = tm.clamp(delta_x, -0.5, 0.5)

            delta_y = 0.0
            denom_y = 2.0 * (c_p1_y + c_m1_y - 2.0 * c_0_0)
            if ti.abs(denom_y) > 1e-6:
                delta_y = -(c_p1_y - c_m1_y) / denom_y
            delta_y = tm.clamp(delta_y, -0.5, 0.5)

            # Write result
            final_dx = float(int_dx) + delta_x
            final_dy = float(int_dy) + delta_y

            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = final_dx
                    refined_flow[y + r, x + c, 1] = final_dy


# ============================================================================
# Helper Functions
# ============================================================================


def process_single_layer(
    ref_layer_gpu,  # ti.ndarray (GPU buffer from pyramid)
    comp_layer_gpu,  # ti.ndarray (GPU buffer from pyramid)
    previous_flow_gpu,  # ti.ndarray or None
    layer_index: int,
    total_layers: int,
    tile_h: int,
    tile_w: int,
    base_search_dist: float,
) -> any:  # Returns ti.ndarray (GPU)
    """
    Process tile matching for a single pyramid layer.
    All inputs are assumed to be GPU buffers (ti.ndarray) from build_image_pyramid_gpu.
    This eliminates CPU-GPU transfer overhead.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_coarsest_layer = layer_index == total_layers - 1
    is_finest_layer = layer_index == 0

    h, w = ref_layer_gpu.shape[:2]

    # Direct GPU usage - inputs are already GPU buffers from pyramid
    ref_gpu = ref_layer_gpu
    comp_gpu = comp_layer_gpu

    # ti.sync()
    t_start = 0.0  # time.perf_counter()

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

    # ti.sync()
    t_init = 0.0  # (time.perf_counter() - t_start) * 1000
    init_label = "Initiation" if is_coarsest_layer else "Flow Upsampling"

    # 2. Match
    # t_match_start = time.perf_counter()
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
    elif is_coarsest_layer:
        # For coarsest layer, perform wide-area block search to establish global motion
        search_radius = max(4, int(base_search_dist * 2))
        _block_search_kernel(
            ref_gpu,
            comp_gpu,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
            search_radius,
        )
    else:
        # Coarse layers: use search_dist
        depth_factor = 1.0 / (2.0 ** (total_layers - layer_index - 1))
        current_search_dist = max(1, int(base_search_dist * depth_factor))

        # Adaptive logic only for L2 and coarser
        adaptive_thresh = 1e10  # Disabled by default
        if layer_index >= 2:
            adaptive_thresh = ImageAlignmentConfig.ADAPTIVE_THRESHOLD

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
            adaptive_thresh,
        )

    # ti.sync()
    t_match = 0.0  # (time.perf_counter() - t_match_start) * 1000
    # match_label = (
    #     "Tile Matching (Fine)" if is_finest_layer else "Tile Matching (Coarse)"
    # )

    t_subpixel = 0.0
    if not is_finest_layer:
        # t_sub_start = time.perf_counter()
        # Parabolic Subpixel Refinement (Fast subpixel correction for coarse levels)
        common.copy_field(refined_flow_gpu, flow_gpu)
        _parabolic_subpixel_refinement_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
        )
        # ti.sync()
        t_subpixel = 0.0  # (time.perf_counter() - t_sub_start) * 1000

    # No cleanup of ref_gpu/comp_gpu - they're owned by pyramid
    common.release_temp_buffer(flow_gpu)

    # 3. Post-process (median filter only, no RANSAC)
    # t_median_start = time.perf_counter()
    # 4. Median Filter (Optional)
    if ImageAlignmentConfig.ENABLE_MEDIAN_FILTER:
        median_flow_gpu = median_filter_flow(
            src=refined_flow_gpu,
            dst=common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool"),
            kernel_size=3,
            enable_tiling=False,
        )
        common.release_temp_buffer(refined_flow_gpu)
        flow_gpu = median_flow_gpu
    else:
        # Just swap buffers or reuse refined_flow_gpu as the output
        # Since refined_flow_gpu is a robust buffer (from pool), we can use it.
        # But process_single_layer typically returns 'flow_gpu' which is passed to next layer.
        # We need to ensure we return a valid buffer that won't be double-freed or leaked.
        # refined_flow_gpu is the new result.
        flow_gpu = refined_flow_gpu
    # ti.sync()
    t_median = 0.0  # (time.perf_counter() - t_median_start) * 1000

    # t_total = (time.perf_counter() - t_start) * 1000

    # layer_suffix = ""
    # if is_coarsest_layer:
    #     layer_suffix = " (Coarsest)"
    # elif is_finest_layer:
    #     layer_suffix = " (Finest)"

    # print(f"Layer {layer_index}{layer_suffix}:")
    # print(f" - {init_label}: {t_init:.2f}ms")
    # print(f" - {match_label}: {t_match:.2f}ms")
    # if not is_finest_layer:
    #     print(f" - Subpixel Refinement (Parabolic): {t_subpixel:.2f}ms")
    # print(f" - Median Filter: {t_median:.2f}ms")
    # print(f" Total Layer {layer_index}: {t_total:.2f}ms\n")

    # Return raw flow without RANSAC cleanup
    return flow_gpu


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

    ti.sync()
    t_total_start = time.perf_counter()

    ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_work_data, dtype=ti.f32)
    comp_gpu, comp_is_temp = common.ensure_taichi_field(current_work_data, dtype=ti.f32)

    print("Pyramid Initiation:")
    t_pyr_ref_start = time.perf_counter()
    ref_pyramid = build_image_pyramid_gpu(
        ref_gpu,
        n_levels=n_layers,
        min_size=ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
    )
    ti.sync()
    t_pyr_ref = (time.perf_counter() - t_pyr_ref_start) * 1000
    print(f" - Ref: {t_pyr_ref:.2f}ms")

    t_pyr_comp_start = time.perf_counter()
    current_pyramid = build_image_pyramid_gpu(
        comp_gpu,
        n_levels=n_layers,
        min_size=ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
    )
    ti.sync()
    t_pyr_comp = (time.perf_counter() - t_pyr_comp_start) * 1000
    print(f" - Comp: {t_pyr_comp:.2f}ms\n")

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

    # No final RANSAC cleanup - return raw flow

    # Release Buffers
    for i in range(len(ref_pyramid)):
        common.release_temp_buffer(ref_pyramid[i])
    for i in range(len(current_pyramid)):
        common.release_temp_buffer(current_pyramid[i])

    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)

    ti.sync()
    t_total = (time.perf_counter() - t_total_start) * 1000
    print(f"Total Alignment Time: {t_total:.2f}ms\n")

    return flow_gpu


def free_flow_memory(flow_data):
    """Free flow memory (no-op in Python)."""
    pass
