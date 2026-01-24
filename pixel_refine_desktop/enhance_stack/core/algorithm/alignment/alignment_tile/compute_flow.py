"""
Compute Flow - Taichi GPU Implementation
=========================================
GPU-accelerated tile-based optical flow computation.

Matching C++ API: alignment_tile.cpp

Pipeline: Coarse-to-Fine Pyramid → Tile Matching → RANSAC Cleanup
"""

print("[DEBUG] Loading compute_flow.py (Updated: ZMCL Cost + Fix Imports)")

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
from .cost_function import (
    compute_zmcl_cost,
)

# Import submodule functions directly to avoid package-level shadowing
try:
    from ...taichi_algorithm.pyramid import (
        build_image_pyramid,
        build_image_pyramid_gpu,
        upsample_flow,
        upsample_flow_gpu,
    )
    from ...taichi_algorithm.ransac import (
        ransac_flow_cleanup,
        ransac_flow_cleanup_local,
    )
    from ...taichi_algorithm.box_filter import box_filter_flow
    from ...taichi_algorithm.median_filter import median_filter_flow

    # common might be useful
    from ...taichi_algorithm import common

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
        """
        Coarse level tile matching with grid search.
        Now uses ZMCL cost instead of simple SAD.
        """
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

            # Grid search
            best_cost = 1e10
            best_dx = init_dx
            best_dy = init_dy

            for dy in range(-search_dist, search_dist + 1):
                for dx in range(-search_dist, search_dist + 1):
                    test_y = y + init_dy + dy
                    test_x = x + init_dx + dx

                    # Boundary check
                    if (
                        test_y < 0
                        or test_x < 0
                        or test_y + tile_h > h
                        or test_x + tile_w > w
                    ):
                        continue

                    # Calculate ZMCL Cost (Robust)
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

                    # Early Exit: If cost is extremely low, we likely found a perfect match
                    if best_cost < ImageAlignmentConfig.EARLY_EXIT_COST:
                        break
                if best_cost < ImageAlignmentConfig.EARLY_EXIT_COST:
                    break

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
        """
        Fine level tile matching with 9-point search + parabolic refinement.
        Now uses ZMCL cost instead of SAD.
        """
        step_y = tile_h
        step_x = tile_w

        for tile_y, tile_x in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y = tile_y * step_y
            x = tile_x * step_x

            # Get initial flow
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            init_dx = int(ti.round(flow[center_y, center_x, 0]))
            init_dy = int(ti.round(flow[center_y, center_x, 1]))

            # 9-point search
            costs = ti.Vector([0.0] * 9)
            best_cost = 1e10
            best_dx = init_dx
            best_dy = init_dy

            cost_idx = 0
            for ddy in ti.static(range(-1, 2)):
                for ddx in ti.static(range(-1, 2)):
                    check_dx = init_dx + ddx
                    check_dy = init_dy + ddy

                    test_y = y + check_dy
                    test_x = x + check_dx

                    if (
                        test_y < 0
                        or test_x < 0
                        or test_y + tile_h > h
                        or test_x + tile_w > w
                    ):
                        costs[cost_idx] = 1e10
                    else:
                        # ZMCL Cost
                        # Use imported compute_zmcl_cost
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
                        costs[cost_idx] = cost

                        if cost < best_cost:
                            best_cost = cost
                            best_dx = check_dx
                            best_dy = check_dy

                    cost_idx += 1

            # Soft-Argmin / Cost-Weighted Refinement
            # Instead of just parabolic fitting, we use a weighted average of candidates
            # based on their costs. This is more robust to noise than local fitting.

            final_dx = float(best_dx)
            final_dy = float(best_dy)

            # Find min and max cost in 3x3 to normalize weights
            min_c = 1e10
            max_c = -1e10
            for i in ti.static(range(9)):
                if costs[i] < min_c:
                    min_c = costs[i]
                if costs[i] > max_c and costs[i] < 1e9:
                    max_c = costs[i]

            if max_c > min_c:
                sum_w = 0.0
                sum_dx = 0.0
                sum_dy = 0.0

                # We use a sharp exponential weighting (Soft-Argmin)
                # k factor determines how much we trust the best candidate
                k = 50.0

                idx = 0
                for ddy in ti.static(range(-1, 2)):
                    for ddx in ti.static(range(-1, 2)):
                        c_val = costs[idx]
                        if c_val < 1e9:
                            # Weight = exp(-k * (cost - min_cost) / (max_cost - min_cost))
                            # Normalized to prevent overflow/underflow
                            weight = ti.exp(
                                -k * (c_val - min_c) / (ti.max(max_c - min_c, 1e-6))
                            )
                            sum_w += weight
                            sum_dx += weight * float(init_dx + ddx)
                            sum_dy += weight * float(init_dy + ddy)
                        idx += 1

                if sum_w > 1e-6:
                    final_dx = sum_dx / sum_w
                    final_dy = sum_dy / sum_w

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
        """
        Precise iterative subpixel refinement using bicubic interpolation.
        Minimizes SAD/MSE logic using local gradient approximation.
        """
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

            # Iterative optimization (Gauss-Newton)
            for _ in range(max_iters):
                sum_gv2_x = 0.0
                sum_gv2_y = 0.0
                sum_diff_gv_x = 0.0
                sum_diff_gv_y = 0.0

                # Use consistent stride to reduce GPU load (1/4 sampling)
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

                # update step
                alpha = 0.6  # Damping factor
                if sum_gv2_x > 1e-6:
                    curr_dx -= alpha * sum_diff_gv_x / sum_gv2_x
                if sum_gv2_y > 1e-6:
                    curr_dy -= alpha * sum_diff_gv_y / sum_gv2_y

                # Stability clamp
                curr_dx = tm.clamp(curr_dx, -50.0, 50.0)
                curr_dy = tm.clamp(curr_dy, -50.0, 50.0)

            # Write high-precision result
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
    Keeps data on GPU to minimize transfer overhead.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_coarsest_layer = layer_index == total_layers - 1
    is_finest_layer = layer_index == 0

    h, w = ref_layer.shape[:2]

    # 4. Upload Images to GPU (Must happen per layer as they come from CPU pyramid)
    # Optimization: Use pooled buffers, or use existing GPU fields if provided
    ref_gpu = None
    comp_gpu = None
    ref_is_temp = False
    comp_is_temp = False

    # Check if inputs are Taichi fields (duck typing)
    if (
        hasattr(ref_layer, "dtype")
        and hasattr(ref_layer, "shape")
        and not isinstance(ref_layer, np.ndarray)
    ):
        ref_gpu = ref_layer
    else:
        ref_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider="pool")
        ref_gpu.from_numpy(np.ascontiguousarray(ref_layer, dtype=np.float32))
        ref_is_temp = True

    if (
        hasattr(comp_layer, "dtype")
        and hasattr(comp_layer, "shape")
        and not isinstance(comp_layer, np.ndarray)
    ):
        comp_gpu = comp_layer
    else:
        comp_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider="pool")
        comp_gpu.from_numpy(np.ascontiguousarray(comp_layer, dtype=np.float32))
        comp_is_temp = True

    # 1. Initialize/Upsample flow (ON GPU)
    # This buffer will be returned (conceptually), but we need a target for upsample
    flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")

    if is_coarsest_layer:
        # Zero initialization
        _initialize_coarsest_flow_kernel(flow_gpu, h, w)
    else:
        # GPU Upsample
        if previous_flow_gpu is None:
            _initialize_coarsest_flow_kernel(flow_gpu, h, w)
        else:
            # Upsample from previous level (smaller) to current (larger)
            upsample_flow_gpu(
                src_gpu=previous_flow_gpu,
                dst_gpu=flow_gpu,
                scale=ImageAlignmentConfig.FLOW_UPSCALE_FACTOR,
            )

    # 2. Clamp tile size
    current_tile_h = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_h, h))
    current_tile_w = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_w, w))

    # 3. Adaptive search distance
    # Adaptive Search: Use a wider search for coarse layers, and progressively tighter
    # but more focused search for finer layers.
    if is_coarsest_layer:
        current_search_dist = int(base_search_dist)
    else:
        # Base factor + decay based on layer depth
        depth_factor = 1.0 / (2.0 ** (total_layers - layer_index - 1))
        current_search_dist = max(1, int(base_search_dist * depth_factor))

        # Optional: could further reduce search_dist if previous level confidence was high
        # For now, keeping it robustly tied to pyramid depth.

    # Allocate refined flow
    refined_flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")
    # Initialize refined flow with current guess
    _initialize_coarsest_flow_kernel(refined_flow_gpu, h, w)

    # 5. Tile matching
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

        # Iterative Refinement Pass for maximum precision
        # Reuse flow_gpu as input (copy from refined_flow_gpu)
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
            max_iters=2,  # 2 iterations is faster and sufficient for most use cases
        )
    else:
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

    # Release input images and initial flow (intermediate)
    common.release_temp_buffer(ref_gpu)
    common.release_temp_buffer(comp_gpu)
    common.release_temp_buffer(flow_gpu)

    # 6. Post-processing filters (GPU)
    # Create temp filtering buffer
    filtered_flow_gpu = common.get_temp_buffer(
        (h, w, 2), ti.f32, buffer_provider="pool"
    )

    from ...taichi_algorithm.median_filter import median_filter_flow

    median_filter_flow(
        src=refined_flow_gpu, dst=filtered_flow_gpu, kernel_size=3, enable_tiling=False
    )

    # Release refined_flow as we now have filtered result
    common.release_temp_buffer(refined_flow_gpu)

    # 7. RANSAC for coarse layers (GPU)
    if layer_index >= total_layers - 2:
        # GPU Ransac
        # ransac_flow_cleanup might allocate its own buffers.
        # We should check if it uses pool? It creates ti.ndarray internally in current impl.
        # Ideally ransac should also use pool, but let's assume it returns a new valid buffer.
        # To strictly use pool, we might need to modify ransac, but for now let's reuse what we can.
        ransac_out_gpu = ransac_flow_cleanup(
            filtered_flow_gpu, threshold=3.0, n_iterations=10
        )
        common.release_temp_buffer(filtered_flow_gpu)
        return ransac_out_gpu
    else:
        return filtered_flow_gpu


def compute_alignment_flow(
    ref_work_data: np.ndarray,
    current_work_data: np.ndarray,
    tile_h: int = 16,
    tile_w: int = 16,
    n_layers: int = 3,
    search_dist: float = 2.0,
) -> np.ndarray:
    """
    Compute alignment flow between reference and comparison images.
    Matching C++ compute_alignment_flow().

    Args:
        ref_work_data: Reference image (H, W) float32 grayscale
        current_work_data: Comparison image (H, W) float32 grayscale
        tile_h, tile_w: Tile size for matching
        n_layers: Number of pyramid layers
        search_dist: Base search distance

    Returns:
        Flow field (H, W, 2) with (dx, dy) per pixel
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    if not TAICHI_MODULES_AVAILABLE:
        raise ImportError("Taichi algorithm modules not available")

    # 1. Prepare Inputs on GPU
    # Check if inputs are already taichi fields
    ref_is_temp = False
    if (
        hasattr(ref_work_data, "dtype")
        and hasattr(ref_work_data, "shape")
        and not isinstance(ref_work_data, np.ndarray)
    ):
        ref_gpu = ref_work_data
    else:
        # Upload
        ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_work_data, dtype=ti.f32)

    comp_is_temp = False
    if (
        hasattr(current_work_data, "dtype")
        and hasattr(current_work_data, "shape")
        and not isinstance(current_work_data, np.ndarray)
    ):
        comp_gpu = current_work_data
    else:
        comp_gpu, comp_is_temp = common.ensure_taichi_field(
            current_work_data, dtype=ti.f32
        )

    work_h, work_w = ref_gpu.shape[:2]

    # 2. Build Pyramids on GPU
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

    # Actual number of layers (may be less due to min_size)
    actual_layers = min(len(ref_pyramid), len(current_pyramid))

    # Coarse-to-fine processing
    # Coarse-to-fine processing
    flow_gpu = None

    # We need to hold reference to the result of each layer
    # flow_gpu will be updated in each iteration

    for i in range(actual_layers - 1, -1, -1):
        ref_layer = ref_pyramid[i]
        comp_layer = current_pyramid[i]

        prev_flow = flow_gpu
        flow_gpu = process_single_layer(
            ref_layer,
            comp_layer,
            prev_flow,
            i,
            actual_layers,
            tile_h,
            tile_w,
            search_dist,
        )
        # BUGFIX: Release the previous level flow buffer now that upsample is done
        if prev_flow is not None:
            common.release_temp_buffer(prev_flow)

    # Final post-processing: Spatial local RANSAC cleanup
    # Perform on GPU before download
    if flow_gpu is not None:
        old_flow = flow_gpu
        flow_gpu = ransac_flow_cleanup_local(
            old_flow, block_size=64, threshold=2.0, n_iterations=5
        )
        # BUGFIX: Release the flow buffer used as input to RANSAC
        common.release_temp_buffer(old_flow)
        # Optimization: Return GPU handle instead of numpy
        # Cleanup
        for i in range(1, len(ref_pyramid)):
            common.release_temp_buffer(ref_pyramid[i])
        for i in range(1, len(current_pyramid)):
            common.release_temp_buffer(current_pyramid[i])

        if ref_is_temp:
            common.release_temp_buffer(ref_gpu)
        if comp_is_temp:
            common.release_temp_buffer(comp_gpu)

        return flow_gpu
    else:
        # Fallback for empty pyramid (unlikely)
        # Manually create a GPU buffer of zeros to match return type
        flow_gpu = common.get_temp_buffer(
            (work_h, work_w, 2), ti.f32, buffer_provider="pool"
        )
        _initialize_coarsest_flow_kernel(flow_gpu, work_h, work_w)
        return flow_gpu


def free_flow_memory(flow_data):
    """
    Free flow memory (Python version - no-op, handled by GC).
    Matching C++ free_flow_memory().
    """
    pass
