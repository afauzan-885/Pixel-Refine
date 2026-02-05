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
    def _compute_gradients_kernel(
        img: ti.types.ndarray(),
        gx: ti.types.ndarray(),
        gy: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Compute 2D gradients using central difference."""
        for r, c in ti.ndrange(h, w):
            if c > 0 and c < w - 1:
                gx[r, c] = (img[r, c + 1] - img[r, c - 1]) * 0.5
            else:
                gx[r, c] = 0.0

            if r > 0 and r < h - 1:
                gy[r, c] = (img[r + 1, c] - img[r - 1, c]) * 0.5
            else:
                gy[r, c] = 0.0

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
        """Coarse level tile matching using ZMSAD cost."""
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

                    cost = cost_function.compute_zmsad_cost(
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

                    cost = cost_function.compute_zmsad_cost(
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
    def _iterative_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        gx_comp: ti.types.ndarray(),
        gy_comp: ti.types.ndarray(),
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

                    # Sample pre-calculated gradients
                    gv_x = common.bilinear_at(gx_comp, tx, ty)
                    gv_y = common.bilinear_at(gy_comp, tx, ty)

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
    ref_layer_gpu,  # ti.ndarray (GPU buffer from pyramid)
    comp_layer_gpu,  # ti.ndarray (GPU buffer from pyramid)
    gx_ref,  # ti.ndarray
    gy_ref,  # ti.ndarray
    gx_comp,  # ti.ndarray
    gy_comp,  # ti.ndarray
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

    ti.sync()
    t_start = time.perf_counter()

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

    ti.sync()
    t_init = (time.perf_counter() - t_start) * 1000
    init_label = "Initiation" if is_coarsest_layer else "Flow Upsampling"

    # 2. Match
    t_match_start = time.perf_counter()
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

    ti.sync()
    t_match = (time.perf_counter() - t_match_start) * 1000
    match_label = (
        "Tile Matching (Fine)" if is_finest_layer else "Tile Matching (Coarse)"
    )

    t_subpixel = 0.0
    if is_finest_layer:
        t_sub_start = time.perf_counter()
        # Subpixel Refinement
        common.copy_field(refined_flow_gpu, flow_gpu)
        _iterative_subpixel_refinement_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            refined_flow_gpu,
            gx_comp,
            gy_comp,
            h,
            w,
            current_tile_h,
            current_tile_w,
            max_iters=5,
        )
        ti.sync()
        t_subpixel = (time.perf_counter() - t_sub_start) * 1000

    # No cleanup of ref_gpu/comp_gpu - they're owned by pyramid
    common.release_temp_buffer(flow_gpu)

    # 3. Post-process (median filter only, no RANSAC)
    t_median_start = time.perf_counter()
    filtered_flow_gpu = common.get_temp_buffer(
        (h, w, 2), ti.f32, buffer_provider="pool"
    )
    median_filter_flow(
        src=refined_flow_gpu, dst=filtered_flow_gpu, kernel_size=3, enable_tiling=False
    )
    common.release_temp_buffer(refined_flow_gpu)
    ti.sync()
    t_median = (time.perf_counter() - t_median_start) * 1000

    t_total = (time.perf_counter() - t_start) * 1000

    layer_suffix = ""
    if is_coarsest_layer:
        layer_suffix = " (Coarsest)"
    elif is_finest_layer:
        layer_suffix = " (Finest)"

    print(f"Layer {layer_index}{layer_suffix}:")
    print(f" - {init_label}: {t_init:.2f}ms")
    print(f" - {match_label}: {t_match:.2f}ms")
    if is_finest_layer:
        print(f" - Subpixel Refinement (Gauss-Newton): {t_subpixel:.2f}ms")
    print(f" - Median Filter: {t_median:.2f}ms")
    print(f" Total Layer {layer_index}: {t_total:.2f}ms\n")

    # Return raw flow without RANSAC cleanup
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

    # Add Gradient Pyramids
    gx_ref_pyr = []
    gy_ref_pyr = []
    gx_comp_pyr = []
    gy_comp_pyr = []

    for i in range(len(ref_pyramid)):
        h_i, w_i = ref_pyramid[i].shape
        gx = common.get_temp_buffer((h_i, w_i), ti.f32, buffer_provider="pool")
        gy = common.get_temp_buffer((h_i, w_i), ti.f32, buffer_provider="pool")
        _compute_gradients_kernel(ref_pyramid[i], gx, gy, h_i, w_i)
        gx_ref_pyr.append(gx)
        gy_ref_pyr.append(gy)

    for i in range(len(current_pyramid)):
        h_i, w_i = current_pyramid[i].shape
        gx = common.get_temp_buffer((h_i, w_i), ti.f32, buffer_provider="pool")
        gy = common.get_temp_buffer((h_i, w_i), ti.f32, buffer_provider="pool")
        _compute_gradients_kernel(current_pyramid[i], gx, gy, h_i, w_i)
        gx_comp_pyr.append(gx)
        gy_comp_pyr.append(gy)

    actual_layers = min(len(ref_pyramid), len(current_pyramid))
    flow_gpu = None

    for i in range(actual_layers - 1, -1, -1):
        prev_flow = flow_gpu
        flow_gpu = process_single_layer(
            ref_pyramid[i],
            current_pyramid[i],
            gx_ref_pyr[i],
            gy_ref_pyr[i],
            gx_comp_pyr[i],
            gy_comp_pyr[i],
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
        common.release_temp_buffer(gx_ref_pyr[i])
        common.release_temp_buffer(gy_ref_pyr[i])
    for i in range(len(current_pyramid)):
        common.release_temp_buffer(current_pyramid[i])
        common.release_temp_buffer(gx_comp_pyr[i])
        common.release_temp_buffer(gy_comp_pyr[i])

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
