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
        build_image_pyramid_gpu_4x,
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
except ImportError as e:
    print("TAICHI IMPORT ERROR in compute_flow.py:", e)
    TAICHI_MODULES_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================
class ImageAlignmentConfig:
    """Configuration constants matching C++ namespace."""

    DEFAULT_DOWNSCALE_FACTOR = 4  # Default for HDR+ style
    MIN_TILE_SIZE = 8
    MIN_PYRAMID_LAYER_SIZE = 32
    EARLY_EXIT_COST = 0.0001
    ADAPTIVE_THRESHOLD = 0.005  # Threshold for expanding search area
    ENABLE_MEDIAN_FILTER = False  # Enable median filter for robust motion suppression


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
            (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
        ):
            y = tm.clamp(tile_y * step_y, 0, h - tile_h)
            x = tm.clamp(tile_x * step_x, 0, w - tile_w)

            best_cost = 1e10
            best_dx = 0.0
            best_dy = 0.0

            # 1. Integer Search with Zero-Motion Bias
            # We give a slight preference (bias) to (0,0) shift
            bias_weight = 0.999  # Slightly favor smaller costs at (0,0)

            for dy in range(-search_radius, search_radius + 1):
                for dx in range(-search_radius, search_radius + 1):
                    test_y = y + dy
                    test_x = x + dx

                    if (
                        test_y <= -tile_h
                        or test_x <= -tile_w
                        or test_y >= h
                        or test_x >= w
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

                    # Apply bias to (0,0)
                    if dx == 0 and dy == 0:
                        cost *= bias_weight

                    if cost < best_cost:
                        best_cost = cost
                        best_dx = float(dx)
                        best_dy = float(dy)

            # 2. Subpixel Refinement (Parabolic Fitting)
            # Find subpixel peak using 4-neighbors if not on search boundary
            if (
                -search_radius < best_dx < search_radius
                and -search_radius < best_dy < search_radius
            ):
                # Sample 4 neighbors
                c0 = best_cost
                cx_m1 = cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int(best_dy),
                    x + int(best_dx) - 1,
                    tile_h,
                    tile_w,
                )
                cx_p1 = cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int(best_dy),
                    x + int(best_dx) + 1,
                    tile_h,
                    tile_w,
                )
                cy_m1 = cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int(best_dy) - 1,
                    x + int(best_dx),
                    tile_h,
                    tile_w,
                )
                cy_p1 = cost_function.compute_zmssd_cost(
                    ref_layer,
                    comp_layer,
                    y,
                    x,
                    y + int(best_dy) + 1,
                    x + int(best_dx),
                    tile_h,
                    tile_w,
                )

                # Parabolic fit: x = x_int - (f(x+1) - f(x-1)) / (2 * (f(x+1) + f(x-1) - 2*f(x)))
                denom_x = 2.0 * (cx_p1 + cx_m1 - 2.0 * c0)
                if ti.abs(denom_x) > 1e-6:
                    best_dx -= (cx_p1 - cx_m1) / denom_x

                denom_y = 2.0 * (cy_p1 + cy_m1 - 2.0 * c0)
                if ti.abs(denom_y) > 1e-6:
                    best_dy -= (cy_p1 - cy_m1) / denom_y

            # Broadcast best match to all pixels in the tile
            for r, c in ti.ndrange(tile_h, tile_w):
                idx_y, idx_x = y + r, x + c
                if idx_y < h and idx_x < w:
                    refined_flow[idx_y, idx_x, 0] = best_dx
                    refined_flow[idx_y, idx_x, 1] = best_dy

    @ti.kernel
    def _initialize_coarsest_flow_kernel(
        flow: ti.types.ndarray(),
        h: int,
        w: int,
        init_dx: float,
        init_dy: float,
    ):
        """Initialize flow to starting values for coarsest level."""
        for r, c in ti.ndrange(h, w):
            flow[r, c, 0] = init_dx
            flow[r, c, 1] = init_dy

    @ti.func
    def _compute_regularization_params(
        flow: ti.types.ndarray(),
        y: int,
        x: int,
        tile_h: int,
        tile_w: int,
        h_total: int,
        w_total: int,
    ) -> ti.types.vector(3, ti.f32):
        """
        Compute spatial regularization parameters from guide flow (upsampled prev level).
        Returns: [avg_dx, avg_dy, weight]
        """
        sum_dx = 0.0
        sum_dy = 0.0
        sum_sq_diff = 0.0
        count = 0.0

        # Sample 3x3 neighbors of the tile
        # Since 'flow' is at pixel level, we step by tile size
        step_y = tile_h
        step_x = tile_w

        # Center index for flow sampling (center of the tile)
        center_y = y + tile_h // 2
        center_x = x + tile_w // 2

        # 1. Compute Mean
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue  # Skip center (self)

                # Neighbor tile center
                ny = center_y + dy * step_y
                nx = center_x + dx * step_x

                if ny >= 0 and ny < h_total and nx >= 0 and nx < w_total:
                    val_x = flow[ny, nx, 0]
                    val_y = flow[ny, nx, 1]
                    sum_dx += val_x
                    sum_dy += val_y
                    count += 1.0

        avg_dx = 0.0
        avg_dy = 0.0
        variance = 0.0
        lambda_val = 1.5  # Base lambda from C++

        if count > 0:
            avg_dx = sum_dx / count
            avg_dy = sum_dy / count

            # 2. Compute Variance
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    if dy == 0 and dx == 0:
                        continue

                    ny = center_y + dy * step_y
                    nx = center_x + dx * step_x

                    if ny >= 0 and ny < h_total and nx >= 0 and nx < w_total:
                        val_x = flow[ny, nx, 0]
                        val_y = flow[ny, nx, 1]
                        dist = (val_x - avg_dx) ** 2 + (val_y - avg_dy) ** 2
                        sum_sq_diff += dist

            variance = sum_sq_diff / count

            # 3. Adaptive Lambda
            if variance > 5.0:
                lambda_val *= 0.5
            elif variance < 0.5:
                lambda_val *= 1.5

        else:
            # No neighbors (isolated) -> fallback to center flow
            avg_dx = flow[center_y, center_x, 0]
            avg_dy = flow[center_y, center_x, 1]

        # Adaptive weight based on neighbor count (Edge/Corner mitigation)
        # If we have fewer neighbors, increase regularization to prevent erratic motion
        weight = lambda_val * 0.1
        # Edge/Corner Robustness: Increase regularization if we have fewer neighbors
        if count < 8.0:
            weight *= 2.0  # More aggressive regularization at boundaries
        if count < 4.0:
            weight *= 4.0  # Extreme regularization at corners

        return ti.Vector([avg_dx, avg_dy, weight])

    @ti.kernel
    def _search_coarse_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        previous_flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        search_dist: int,
        prev_h: int,
        prev_w: int,
        downscale_factor: int,
    ):
        """Coarse level tile matching using ZM-SSD cost with Spatial Regularization."""
        step_y = tile_h
        step_x = tile_w
        tile_area_inv = 1.0 / float(tile_h * tile_w)

        for tile_y, tile_x in ti.ndrange(
            (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
        ):
            y = tm.clamp(tile_y * step_y, 0, h - tile_h)
            x = tm.clamp(tile_x * step_x, 0, w - tile_w)

            # Get regularization params from neighbors
            reg_params = _compute_regularization_params(
                flow, y, x, tile_h, tile_w, h, w
            )
            spatial_mean_x = reg_params[0]
            spatial_mean_y = reg_params[1]
            spatial_weight = reg_params[2]

            # Get initial flow from upsampled previous level
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            init_dx_val = flow[center_y, center_x, 0]
            init_dy_val = flow[center_y, center_x, 1]
            init_dx = int(ti.round(init_dx_val))
            init_dy = int(ti.round(init_dy_val))

            # --- Candidate Spatial Neighbors Strategy ---
            best_cand_cost = 1e10
            best_cand_dx = init_dx
            best_cand_dy = init_dy

            # Multi-Stage Adaptive Search Offsets (Radius 1 & 2)
            # 0-3: Cardinal, 4-7: Diagonal, 8-15: Extended Radius 2
            neighbor_offsets = ti.Matrix([
                [-1, 0], [1, 0], [0, -1], [0, 1],       # 0-3: Cardinal
                [-1, -1], [1, -1], [-1, 1], [1, 1],     # 4-7: Diagonal
                [-2, 0], [2, 0], [0, -2], [0, 2],       # 8-11: Ext Cardinal
                [-2, -2], [2, -2], [-2, 2], [2, 2]      # 12-15: Ext Diagonal
            ])

            # Use a larger vector for 18 candidates: Center, 16 Neighbors, Coarse
            cands_dx = ti.Vector([init_dx] * 18)
            cands_dy = ti.Vector([init_dy] * 18)

            # 1-16: Spatial Neighbors
            for i in ti.static(range(16)):
                nx = center_x + neighbor_offsets[i, 0] * step_x
                ny = center_y + neighbor_offsets[i, 1] * step_y
                if nx >= 0 and nx < w and ny >= 0 and ny < h:
                    cands_dx[i + 1] = int(ti.round(flow[ny, nx, 0]))
                    cands_dy[i + 1] = int(ti.round(flow[ny, nx, 1]))

            # 17: Coarse Projection Candidate (Fallback)
            if prev_h > 1 and prev_w > 1:
                coarse_y = center_y // downscale_factor
                coarse_x = center_x // downscale_factor
                if coarse_y < prev_h and coarse_x < prev_w:
                    cands_dx[17] = int(ti.round(previous_flow[coarse_y, coarse_x, 0] * float(downscale_factor)))
                    cands_dy[17] = int(ti.round(previous_flow[coarse_y, coarse_x, 1] * float(downscale_factor)))

            # --- MULTI-STAGE ADAPTIVE EVALUATION ---
            # Stage 1: Basic (6 Candidates: Center, Coarse, 4 Cardinal)
            for i in ti.static(range(6)):
                cand_idx = i
                if i == 5: cand_idx = 17 # Use Coarse Fallback as the 6th in Stage 1
                
                check_y = y + cands_dy[cand_idx]
                check_x = x + cands_dx[cand_idx]
                
                # Unique Check
                is_unique = True
                for j in ti.static(range(i)):
                    prev_idx = j
                    if j == 5: prev_idx = 17
                    if cands_dx[cand_idx] == cands_dx[prev_idx] and cands_dy[cand_idx] == cands_dy[prev_idx]:
                        is_unique = False
                
                if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                    cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                    if cost < best_cand_cost:
                        best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[cand_idx], cands_dy[cand_idx]

            # Stage 2: Quality (Next 4: Diagonals)
            if best_cand_cost > 0.005:
                for i in ti.static(range(6, 10)):
                    check_y, check_x = y + cands_dy[i], x + cands_dx[i]
                    is_unique = True
                    for j in ti.static(range(6)): # Check against Stage 1
                        prev_idx = j
                        if j == 5: prev_idx = 17
                        if cands_dx[i] == cands_dx[prev_idx] and cands_dy[i] == cands_dy[prev_idx]: is_unique = False
                    
                    if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                        cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                        if cost < best_cand_cost:
                            best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[i], cands_dy[i]

            # Stage 3: Robustness (Next 8: Radius 2)
            if best_cand_cost > 0.01:
                for i in ti.static(range(10, 18)):
                    check_y, check_x = y + cands_dy[i], x + cands_dx[i]
                    is_unique = True
                    for j in ti.static(range(10)): # Check against Stage 1 & 2
                        prev_idx = j
                        if j == 5: prev_idx = 17
                        if cands_dx[i] == cands_dx[prev_idx] and cands_dy[i] == cands_dy[prev_idx]: is_unique = False
                    
                    if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                        cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                        if cost < best_cand_cost:
                            best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[i], cands_dy[i]

            init_dx, init_dy = best_cand_dx, best_cand_dy
            # --------------------------------------------

            best_total_cost = 1e10
            best_dx = float(init_dx)
            best_dy = float(init_dy)

            # Early Exit Optimization
            if best_cand_cost >= 0.001:
                # Primary Search
                for dy in range(-search_dist, search_dist + 1):
                    cur_dy = init_dy + dy
                    for dx in range(-search_dist, search_dist + 1):
                        cur_dx = init_dx + dx
                        test_y = y + cur_dy
                        test_x = x + cur_dx

                        if (
                            test_y <= -tile_h
                            or test_x <= -tile_w
                            or test_y >= h
                            or test_x >= w
                        ):
                            continue

                        raw_cost_ssd = cost_function.compute_zmssd_cost(
                            ref_layer,
                            comp_layer,
                            y,
                            x,
                            test_y,
                            test_x,
                            tile_h,
                            tile_w,
                        )
                        visual_cost = raw_cost_ssd * tile_area_inv

                        # 2. Spatial Penalty
                        # Squared Euclidean Distance from Spatial Mean
                        dist_sq = (float(cur_dx) - spatial_mean_x) ** 2 + (
                            float(cur_dy) - spatial_mean_y
                        ) ** 2

                        # C++ Logic: Confidence Boost
                        dynamic_weight = spatial_weight
                        if visual_cost < 0.01:
                            dynamic_weight *= 0.1
                        elif visual_cost > 0.1:
                            dynamic_weight *= 3.0

                        # 3. Boundary Penalty: Slightly penalize movements that push the tile out
                        boundary_penalty = 0.0
                        if test_y < 0 or test_y + tile_h > h or test_x < 0 or test_x + tile_w > w:
                            dist_y = tm.max(0.0, float(-test_y), float(test_y + tile_h - h))
                            dist_x = tm.max(0.0, float(-test_x), float(test_x + tile_w - w))
                            boundary_penalty = (dist_y + dist_x) * 0.01

                        total_cost = visual_cost + (dynamic_weight * dist_sq) + boundary_penalty

                        if total_cost < best_total_cost:
                            best_total_cost = total_cost
                            best_dx = float(cur_dx)
                            best_dy = float(cur_dy)

            # Write result
            for r, c in ti.ndrange(tile_h, tile_w):
                idx_y, idx_x = y + r, x + c
                if idx_y < h and idx_x < w:
                    refined_flow[idx_y, idx_x, 0] = best_dx
                    refined_flow[idx_y, idx_x, 1] = best_dy

    @ti.kernel
    def _search_fine_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        previous_flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        prev_h: int,
        prev_w: int,
        downscale_factor: int,
    ):
        """Fine level tile matching using ZMSAD cost with Spatial Regularization."""
        step_y = tile_h
        step_x = tile_w
        tile_area_inv = 1.0 / float(tile_h * tile_w)

        for tile_y, tile_x in ti.ndrange(
            (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
        ):
            y = tm.clamp(tile_y * step_y, 0, h - tile_h)
            x = tm.clamp(tile_x * step_x, 0, w - tile_w)

            # Get regularization params
            reg_params = _compute_regularization_params(
                flow, y, x, tile_h, tile_w, h, w
            )
            spatial_mean_x = reg_params[0]
            spatial_mean_y = reg_params[1]
            spatial_weight = reg_params[2]

            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            init_dx = int(ti.round(flow[center_y, center_x, 0]))
            init_dy = int(ti.round(flow[center_y, center_x, 1]))

            # --- Candidate Spatial Neighbors Strategy ---
            best_cand_cost = 1e10
            best_cand_dx = init_dx
            best_cand_dy = init_dy

            # Multi-Stage Adaptive Search Offsets (Radius 1 & 2)
            # 0-3: Cardinal, 4-7: Diagonal, 8-15: Extended Radius 2
            neighbor_offsets = ti.Matrix([
                [-1, 0], [1, 0], [0, -1], [0, 1],       # 0-3: Cardinal
                [-1, -1], [1, -1], [-1, 1], [1, 1],     # 4-7: Diagonal
                [-2, 0], [2, 0], [0, -2], [0, 2],       # 8-11: Ext Cardinal
                [-2, -2], [2, -2], [-2, 2], [2, 2]      # 12-15: Ext Diagonal
            ])

            # Use a larger vector for 18 candidates: Center, 16 Neighbors, Coarse
            cands_dx = ti.Vector([init_dx] * 18)
            cands_dy = ti.Vector([init_dy] * 18)

            # 1-16: Spatial Neighbors
            for i in ti.static(range(16)):
                nx = center_x + neighbor_offsets[i, 0] * step_x
                ny = center_y + neighbor_offsets[i, 1] * step_y
                if nx >= 0 and nx < w and ny >= 0 and ny < h:
                    cands_dx[i + 1] = int(ti.round(flow[ny, nx, 0]))
                    cands_dy[i + 1] = int(ti.round(flow[ny, nx, 1]))

            # 17: Coarse Projection Candidate (Fallback)
            if prev_h > 1 and prev_w > 1:
                coarse_y = center_y // downscale_factor
                coarse_x = center_x // downscale_factor
                if coarse_y < prev_h and coarse_x < prev_w:
                    cands_dx[17] = int(ti.round(previous_flow[coarse_y, coarse_x, 0] * float(downscale_factor)))
                    cands_dy[17] = int(ti.round(previous_flow[coarse_y, coarse_x, 1] * float(downscale_factor)))

            # --- MULTI-STAGE ADAPTIVE EVALUATION ---
            # Stage 1: Basic (6 Candidates: Center, Coarse, 4 Cardinal)
            for i in ti.static(range(6)):
                cand_idx = i
                if i == 5: cand_idx = 17 # Use Coarse Fallback as the 6th in Stage 1
                
                check_y = y + cands_dy[cand_idx]
                check_x = x + cands_dx[cand_idx]
                
                is_unique = True
                for j in ti.static(range(i)):
                    prev_idx = j
                    if j == 5: prev_idx = 17
                    if cands_dx[cand_idx] == cands_dx[prev_idx] and cands_dy[cand_idx] == cands_dy[prev_idx]:
                        is_unique = False
                
                if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                    cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                    if cost < best_cand_cost:
                        best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[cand_idx], cands_dy[cand_idx]

            # Stage 2: Quality (Next 4: Diagonals)
            if best_cand_cost > 0.005:
                for i in ti.static(range(6, 10)):
                    check_y, check_x = y + cands_dy[i], x + cands_dx[i]
                    is_unique = True
                    for j in ti.static(range(6)):
                        prev_idx = j
                        if j == 5: prev_idx = 17
                        if cands_dx[i] == cands_dx[prev_idx] and cands_dy[i] == cands_dy[prev_idx]: is_unique = False
                    
                    if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                        cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                        if cost < best_cand_cost:
                            best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[i], cands_dy[i]

            # Stage 3: Robustness (Next 8: Radius 2)
            if best_cand_cost > 0.01:
                for i in ti.static(range(10, 18)):
                    check_y, check_x = y + cands_dy[i], x + cands_dx[i]
                    is_unique = True
                    for j in ti.static(range(10)):
                        prev_idx = j
                        if j == 5: prev_idx = 17
                        if cands_dx[i] == cands_dx[prev_idx] and cands_dy[i] == cands_dy[prev_idx]: is_unique = False
                    
                    if is_unique and not (check_y <= -tile_h or check_x <= -tile_w or check_y >= h or check_x >= w):
                        cost = cost_function.compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w) * tile_area_inv
                        if cost < best_cand_cost:
                            best_cand_cost, best_cand_dx, best_cand_dy = cost, cands_dx[i], cands_dy[i]

            init_dx, init_dy = best_cand_dx, best_cand_dy
            # --------------------------------------------

            best_total_cost = 1e10
            final_dx = float(init_dx)
            final_dy = float(init_dy)

            # Early Exit Optimization
            if best_cand_cost >= 0.001:
                # Local 3x3 search around current guess
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        cur_dy = init_dy + dy
                        cur_dx = init_dx + dx
                        test_y = y + cur_dy
                        test_x = x + cur_dx

                        if (
                            test_y <= -tile_h
                            or test_x <= -tile_w
                            or test_y >= h
                            or test_x >= w
                        ):
                            continue

                        raw_cost_ssd = cost_function.compute_zmssd_cost(
                            ref_layer,
                            comp_layer,
                            y,
                            x,
                            test_y,
                            test_x,
                            tile_h,
                            tile_w,
                        )
                        visual_cost = raw_cost_ssd * tile_area_inv

                        # 2. Spatial Penalty
                        dist_sq = (float(cur_dx) - spatial_mean_x) ** 2 + (
                            float(cur_dy) - spatial_mean_y
                        ) ** 2

                        dynamic_weight = spatial_weight
                        if visual_cost < 0.01:
                            dynamic_weight *= 0.1
                        elif visual_cost > 0.1:
                            dynamic_weight *= 3.0

                        # 3. Boundary Penalty: Slightly penalize movements that push the tile out
                        boundary_penalty = 0.0
                        if test_y < 0 or test_y + tile_h > h or test_x < 0 or test_x + tile_w > w:
                            dist_y = tm.max(0.0, float(-test_y), float(test_y + tile_h - h))
                            dist_x = tm.max(0.0, float(-test_x), float(test_x + tile_w - w))
                            boundary_penalty = (dist_y + dist_x) * 0.01

                        total_cost = visual_cost + (dynamic_weight * dist_sq) + boundary_penalty

                        if total_cost < best_total_cost:
                            best_total_cost = total_cost
                            final_dx = float(cur_dx)
                            final_dy = float(cur_dy)

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
            (h + step_y - 1) // step_y, (w + step_x - 1) // step_x
        ):
            y = tm.clamp(tile_y * step_y, 0, h - tile_h)
            x = tm.clamp(tile_x * step_x, 0, w - tile_w)

            # Get integer flow from previous search result
            center_y = y + tile_h // 2
            center_x = x + tile_w // 2
            int_dx = int(ti.round(flow[center_y, center_x, 0]))
            int_dy = int(ti.round(flow[center_y, center_x, 1]))

            # Evaluate neighbors in X
            c_m1_x = cost_function.compute_zmssd_cost(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int_dy,
                x + int_dx - 1,
                tile_h,
                tile_w,
            )

            c_p1_x = cost_function.compute_zmssd_cost(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int_dy,
                x + int_dx + 1,
                tile_h,
                tile_w,
            )

            c_0_0 = cost_function.compute_zmssd_cost(
                ref_layer, comp_layer, y, x, y + int_dy, x + int_dx, tile_h, tile_w
            )

            # Evaluate neighbors in Y
            c_m1_y = cost_function.compute_zmssd_cost(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int_dy - 1,
                x + int_dx,
                tile_h,
                tile_w,
            )

            c_p1_y = cost_function.compute_zmssd_cost(
                ref_layer,
                comp_layer,
                y,
                x,
                y + int_dy + 1,
                x + int_dx,
                tile_h,
                tile_w,
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
    downscale_factor: int = 4,
) -> any:  # Returns ti.ndarray (GPU)
    """
    Process tile matching for a single pyramid layer.
    All inputs are assumed to be GPU buffers (ti.ndarray) from build_image_pyramid_gpu.
    This eliminates CPU-GPU transfer overhead.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = ref_layer_gpu.shape[:2]
    is_coarsest_layer = layer_index == total_layers - 1
    is_finest_layer = layer_index == 0

    # Direct GPU usage - inputs are already GPU buffers from pyramid
    ref_gpu = ref_layer_gpu
    comp_gpu = comp_layer_gpu

    # ti.sync()
    t_start = 0.0  # time.perf_counter()

    # 1. Initialize/Upsample flow
    flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")

    if is_coarsest_layer:
        from ... import taichi_algorithm as ta

        global_dx, global_dy, global_conf = ta.global_translate_zncc(
            ref_layer_gpu, comp_layer_gpu, max_shift=32
        )
        # Output global shift to console for debugging
        print(
            f"[Global Shift] Detected Initial Motion Prior: ({global_dx}, {global_dy}) Confidence: {global_conf:.4f}"
        )
        _initialize_coarsest_flow_kernel(
            flow_gpu, h, w, float(global_dx), float(global_dy)
        )
    else:
        if previous_flow_gpu is None:
            _initialize_coarsest_flow_kernel(flow_gpu, h, w, 0.0, 0.0)
        else:
            # Scalable upscale factor between pyramid levels
            upsample_flow_gpu(
                src_gpu=previous_flow_gpu,
                dst_gpu=flow_gpu,
                scale=float(downscale_factor),
            )

    # ti.sync()
    t_init = 0.0  # (time.perf_counter() - t_start) * 1000
    init_label = "Initiation" if is_coarsest_layer else "Flow Upsampling"

    # 2. Match
    # t_match_start = time.perf_counter()
    current_tile_h = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_h, h))
    current_tile_w = max(ImageAlignmentConfig.MIN_TILE_SIZE, min(tile_w, w))

    refined_flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")
    _initialize_coarsest_flow_kernel(refined_flow_gpu, h, w, 0.0, 0.0)

    # Safe previous flow dummy buffer if layer 0 is the coarsest
    safe_prev_flow = previous_flow_gpu
    prev_h = 1
    prev_w = 1
    if safe_prev_flow is None:
        # Create a tiny 1x1 dummy to avoid Taichi NdArray signature NoneType panic
        safe_prev_flow = ti.ndarray(dtype=ti.f32, shape=(1, 1, 2))
    else:
        prev_h = safe_prev_flow.shape[0]
        prev_w = safe_prev_flow.shape[1]

    if is_finest_layer:
        _search_fine_level_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            safe_prev_flow,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
            prev_h,
            prev_w,
            downscale_factor,
        )
    elif is_coarsest_layer:
        # HDR+ style: wide-area block search at coarsest level (±4px at 1/64 res = ±256px full res)
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
        # HDR+ style: coarse layers with ±4px search (each level covers 4× more range)
        current_search_dist = max(2, int(base_search_dist))

        _search_coarse_level_kernel(
            ref_gpu,
            comp_gpu,
            flow_gpu,
            safe_prev_flow,
            refined_flow_gpu,
            h,
            w,
            current_tile_h,
            current_tile_w,
            current_search_dist,
            prev_h,
            prev_w,
            downscale_factor,
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
    downscale_factor: int = 4,
    min_pyramid_size: int = ImageAlignmentConfig.MIN_PYRAMID_LAYER_SIZE,
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

    print(f"Pyramid Initiation ({downscale_factor}x):")
    t_pyr_ref_start = time.perf_counter()
    ref_pyramid = build_image_pyramid_gpu(
        ref_gpu,
        n_levels=n_layers,
        min_size=min_pyramid_size,
        downscale_factor=downscale_factor,
    )
    ti.sync()
    t_pyr_ref = (time.perf_counter() - t_pyr_ref_start) * 1000
    print(f" - Ref Pyramid: {t_pyr_ref:.2f}ms ({len(ref_pyramid)} levels)")
    for lvl_i, lvl in enumerate(ref_pyramid):
        print(f"   Level {lvl_i}: {lvl.shape[0]}x{lvl.shape[1]}")

    t_pyr_comp_start = time.perf_counter()
    current_pyramid = build_image_pyramid_gpu(
        comp_gpu,
        n_levels=n_layers,
        min_size=min_pyramid_size,
        downscale_factor=downscale_factor,
    )
    ti.sync()
    t_pyr_comp = (time.perf_counter() - t_pyr_comp_start) * 1000
    print(f" - Comp Pyramid: {t_pyr_comp:.2f}ms\n")

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
            downscale_factor,
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
