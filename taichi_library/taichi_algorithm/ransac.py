# Marker: GPU_NATIVE_MARKER_V3
"""
RANSAC - Taichi GPU Implementation
==================================
GPU-accelerated RANSAC for optical flow outlier removal.

Simple translation/affine model fitting with parallel inlier counting.
"""

import numpy as np

import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from . import common
except ImportError:
    pass


if TAICHI_AVAILABLE:

    @ti.kernel
    def _compute_mean_flow_kernel(
        flow: ti.types.ndarray(),
        mean_out: ti.types.ndarray(),
        h: int,
        w: int,
        stride: int,
    ):
        """Compute mean flow vector with stride."""
        sum_x = 0.0
        sum_y = 0.0
        count = 0.0
        for y, x in ti.ndrange((h + stride - 1) // stride, (w + stride - 1) // stride):
            iy, ix = y * stride, x * stride
            if iy < h and ix < w:
                sum_x += flow[iy, ix][0]
                sum_y += flow[iy, ix][1]
                count += 1.0
        if count > 0:
            mean_out[0] = sum_x / count
            mean_out[1] = sum_y / count

    @ti.kernel
    def _compute_median_flow_kernel(
        flow: ti.types.ndarray(),
        sorted_x: ti.types.ndarray(),
        sorted_y: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Copy flow values to separate arrays for sorting."""
        for y, x in ti.ndrange(h, w):
            idx = y * w + x
            sorted_x[idx] = flow[y, x][0]
            sorted_y[idx] = flow[y, x][1]

    @ti.kernel
    def _count_inliers_kernel(
        flow: ti.types.ndarray(),
        model: ti.types.ndarray(),
        threshold: float,
        inlier_mask: ti.types.ndarray(),
        h: int,
        w: int,
        stride: int,
    ):
        """Update inlier mask with stride support."""
        model_x, model_y = model[0], model[1]
        for y, x in ti.ndrange((h + stride - 1) // stride, (w + stride - 1) // stride):
            iy, ix = y * stride, x * stride
            if iy < h and ix < w:
                dx = flow[iy, ix][0] - model_x
                dy = flow[iy, ix][1] - model_y
                if dx * dx + dy * dy < threshold * threshold:
                    inlier_mask[iy, ix] = 1
                else:
                    inlier_mask[iy, ix] = 0

    @ti.kernel
    def _compute_inlier_mean_kernel(
        flow: ti.types.ndarray(),
        inlier_mask: ti.types.ndarray(),
        mean_out: ti.types.ndarray(),
        h: int,
        w: int,
        stride: int,
    ):
        """Compute mean flow of inliers with stride support."""
        sum_x = 0.0
        sum_y = 0.0
        count = 0.0
        for y, x in ti.ndrange((h + stride - 1) // stride, (w + stride - 1) // stride):
            iy, ix = y * stride, x * stride
            if iy < h and ix < w:
                if inlier_mask[iy, ix] == 1:
                    sum_x += flow[iy, ix][0]
                    sum_y += flow[iy, ix][1]
                    count += 1.0
        if count > 0:
            mean_out[0] = sum_x / count
            mean_out[1] = sum_y / count

    @ti.kernel
    def _apply_ransac_result_kernel(
        flow: ti.types.ndarray(),
        inlier_mask: ti.types.ndarray(),
        model: ti.types.ndarray(), # [model_x, model_y]
        output: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Replace outlier flow with model prediction."""
        model_x, model_y = model[0], model[1]
        for y, x in ti.ndrange(h, w):
            if inlier_mask[y, x] == 1:
                # Keep inlier values
                output[y, x][0] = flow[y, x][0]
                output[y, x][1] = flow[y, x][1]
            else:
                # Replace outlier with model
                output[y, x][0] = model_x
                output[y, x][1] = model_y

    # ===== MOTION-AWARE RANSAC KERNELS =====
    @ti.kernel
    def _detect_local_motion_kernel(
        flow: ti.types.ndarray(),
        motion_mask: ti.types.ndarray(),
        global_dx: float,
        global_dy: float,
        threshold: float,
        h: int,
        w: int,
    ):
        """
        Detect pixels with motion significantly different from global motion.
        motion_mask: 1 = local motion (protect), 0 = global motion (allow RANSAC)
        """
        for y, x in ti.ndrange(h, w):
            dx = flow[y, x, 0] - global_dx
            dy = flow[y, x, 1] - global_dy
            deviation = ti.sqrt(dx * dx + dy * dy)

            if deviation > threshold:
                motion_mask[y, x] = 1  # Local motion - protect from RANSAC
            else:
                motion_mask[y, x] = 0  # Global motion - allow RANSAC

    @ti.kernel
    def _selective_ransac_apply_kernel(
        flow: ti.types.ndarray(),
        motion_mask: ti.types.ndarray(),
        inlier_mask: ti.types.ndarray(),
        model_x: float,
        model_y: float,
        output: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """
        Apply RANSAC result only to global motion regions.
        Local motion regions keep their original flow.
        """
        for y, x in ti.ndrange(h, w):
            if motion_mask[y, x] == 1:
                # Local motion - keep original flow (moving objects)
                output[y, x, 0] = flow[y, x, 0]
                output[y, x, 1] = flow[y, x, 1]
            else:
                # Global motion - apply RANSAC
                if inlier_mask[y, x] == 1:
                    # Inlier: keep original
                    output[y, x, 0] = flow[y, x, 0]
                    output[y, x, 1] = flow[y, x, 1]
                else:
                    # Outlier: replace with model
                    output[y, x, 0] = model_x
                    output[y, x, 1] = model_y

    # --- LOCAL RANSAC KERNELS (MOVED HERE TO FIX SCOPE) ---
    @ti.kernel
    def _local_ransac_init_means(
        flow: ti.types.ndarray(),
        block_means: ti.types.ndarray(),
        block_counts_buffer: ti.types.ndarray(),
        h: int,
        w: int,
        block_size: int,
    ):
        for y, x in ti.ndrange(h, w):
            by = y // block_size
            bx = x // block_size

            # Atomic add to global memory (high contention but better than PCI-e sync)
            ti.atomic_add(block_means[by, bx, 0], flow[y, x, 0])
            ti.atomic_add(block_means[by, bx, 1], flow[y, x, 1])
            ti.atomic_add(block_counts_buffer[by, bx], 1.0)

    @ti.kernel
    def _local_ransac_normalize_means(
        block_means: ti.types.ndarray(),
        block_counts_buffer: ti.types.ndarray(),
        grid_h: int,
        grid_w: int,
    ):
        for by, bx in ti.ndrange(grid_h, grid_w):
            count = block_counts_buffer[by, bx]
            if count > 0:
                block_means[by, bx, 0] /= count
                block_means[by, bx, 1] /= count
            else:
                block_means[by, bx, 0] = 0.0
                block_means[by, bx, 1] = 0.0

    @ti.kernel
    def _local_ransac_count_inliers(
        flow: ti.types.ndarray(),
        block_models: ti.types.ndarray(),
        inlier_counts: ti.types.ndarray(),
        inlier_sums: ti.types.ndarray(),  # reusing for next mean calc
        threshold: float,
        h: int,
        w: int,
        block_size: int,
    ):
        for y, x in ti.ndrange(h, w):
            by = y // block_size
            bx = x // block_size

            model_x = block_models[by, bx, 0]
            model_y = block_models[by, bx, 1]

            dx = flow[y, x, 0] - model_x
            dy = flow[y, x, 1] - model_y

            if dx * dx + dy * dy < threshold * threshold:
                ti.atomic_add(inlier_counts[by, bx], 1)
                # Accumulate for next mean update here to save a pass
                ti.atomic_add(inlier_sums[by, bx, 0], flow[y, x, 0])
                ti.atomic_add(inlier_sums[by, bx, 1], flow[y, x, 1])

    @ti.kernel
    def _local_ransac_update_best(
        block_models: ti.types.ndarray(),  # Current models
        inlier_counts: ti.types.ndarray(),  # Current counts
        inlier_sums: ti.types.ndarray(),  # Current sums (for next iter)
        best_models: ti.types.ndarray(),
        best_counts: ti.types.ndarray(),
        next_models: ti.types.ndarray(),  # Output for next iter
        grid_h: int,
        grid_w: int,
    ):
        for by, bx in ti.ndrange(grid_h, grid_w):
            count = inlier_counts[by, bx]

            # Update Best
            if count > best_counts[by, bx]:
                best_counts[by, bx] = count
                best_models[by, bx, 0] = block_models[by, bx, 0]
                best_models[by, bx, 1] = block_models[by, bx, 1]

            # Prepare Next Model (Mean of Inliers)
            if count > 0:
                next_models[by, bx, 0] = inlier_sums[by, bx, 0] / count
                next_models[by, bx, 1] = inlier_sums[by, bx, 1] / count
            else:
                next_models[by, bx, 0] = block_models[by, bx, 0]
                next_models[by, bx, 1] = block_models[by, bx, 1]

    @ti.kernel
    def _local_ransac_apply(
        flow: ti.types.ndarray(),
        best_models: ti.types.ndarray(),
        output: ti.types.ndarray(),
        threshold: float,
        h: int,
        w: int,
        block_size: int,
    ):
        for y, x in ti.ndrange(h, w):
            by = y // block_size
            bx = x // block_size

            model_x = best_models[by, bx, 0]
            model_y = best_models[by, bx, 1]

            dx = flow[y, x, 0] - model_x
            dy = flow[y, x, 1] - model_y

            if dx * dx + dy * dy < threshold * threshold:
                # Keep
                output[y, x, 0] = flow[y, x, 0]
                output[y, x, 1] = flow[y, x, 1]
            else:
                # Replace
                output[y, x, 0] = model_x
                output[y, x, 1] = model_y


def ransac_flow_cleanup(
    flow,  # Can be np.ndarray or ti.ndarray
    threshold: float = 3.0,
    n_iterations: int = 10,
    buffer_provider="pool",
):
    """
    RANSAC-based outlier removal for optical flow.
    Supports both NumPy and Taichi ndarrays natively.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_library import taichi_aot
        return taichi_aot.ransac_flow_cleanup(flow, threshold=threshold, return_gpu=hasattr(flow, "to_numpy"))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = flow.shape[:2]

    # Handle Input
    is_numpy = isinstance(flow, np.ndarray)
    flow_gpu = flow
    if is_numpy:
        flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
        flow_gpu.from_numpy(flow.astype(np.float32))

    # Allocate buffers on GPU via pool
    inlier_mask = common.get_temp_buffer((h, w), ti.i32, buffer_provider)
    mean_out = common.get_temp_buffer((2,), ti.f32, buffer_provider)
    output_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    # Step 1: Initial model
    _compute_mean_flow_kernel(flow_gpu, mean_out, h, w)
    mean_out_np = mean_out.to_numpy()
    model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 2: Iterative refinement
    best_inlier_count = 0
    best_model_x, best_model_y = model_x, model_y

    for _ in range(n_iterations):
        inlier_count = _count_inliers_kernel(
            flow_gpu, model_x, model_y, threshold, inlier_mask, h, w
        )

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_model_x, best_model_y = model_x, model_y

        _compute_inlier_mean_kernel(flow_gpu, inlier_mask, mean_out, h, w)
        mean_out_np = mean_out.to_numpy()
        model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 3+4: Final pass and apply
    _count_inliers_kernel(
        flow_gpu, best_model_x, best_model_y, threshold, inlier_mask, h, w
    )
    _apply_ransac_result_kernel(
        flow_gpu, inlier_mask, best_model_x, best_model_y, output_gpu, h, w
    )

    # Release temporary buffers
    common.release_temp_buffer(inlier_mask)
    common.release_temp_buffer(mean_out)

    if is_numpy:
        result = output_gpu.to_numpy()
        common.release_temp_buffer(flow_gpu)
        common.release_temp_buffer(output_gpu)
        return result

    # If input was not numpy, we return the GPU buffer (it's up to caller to release it)
    return output_gpu


def ransac_flow_cleanup_motion_aware(
    flow,  # Can be np.ndarray or ti.ndarray
    threshold: float = 3.0,
    motion_threshold: float = 2.0,
    n_iterations: int = 10,
    buffer_provider="pool",
):
    """
    Motion-aware RANSAC: Preserves local motion while cleaning global outliers.

    Args:
        flow: Input flow field
        threshold: RANSAC inlier threshold for global motion
        motion_threshold: Deviation threshold to classify local vs global motion
        n_iterations: Number of RANSAC iterations
        buffer_provider: Buffer allocation strategy

    Returns:
        Cleaned flow with local motion preserved
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = flow.shape[:2]

    # Handle Input
    is_numpy = isinstance(flow, np.ndarray)
    flow_gpu = flow
    if is_numpy:
        flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
        flow_gpu.from_numpy(flow.astype(np.float32))

    # Allocate buffers
    motion_mask = common.get_temp_buffer((h, w), ti.i32, buffer_provider)
    inlier_mask = common.get_temp_buffer((h, w), ti.i32, buffer_provider)
    mean_out = common.get_temp_buffer((2,), ti.f32, buffer_provider)
    output_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    # Step 1: Compute global motion (median - robust to outliers)
    # For GPU efficiency, we use mean as approximation to median
    _compute_mean_flow_kernel(flow_gpu, mean_out, h, w)
    mean_out_np = mean_out.to_numpy()
    global_dx, global_dy = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 2: Detect local motion regions
    _detect_local_motion_kernel(
        flow_gpu, motion_mask, global_dx, global_dy, motion_threshold, h, w
    )

    # Step 3: Run RANSAC on global motion regions
    model_x, model_y = global_dx, global_dy
    best_inlier_count = 0
    best_model_x, best_model_y = model_x, model_y

    for _ in range(n_iterations):
        inlier_count = _count_inliers_kernel(
            flow_gpu, model_x, model_y, threshold, inlier_mask, h, w
        )

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_model_x, best_model_y = model_x, model_y

        _compute_inlier_mean_kernel(flow_gpu, inlier_mask, mean_out, h, w)
        mean_out_np = mean_out.to_numpy()
        model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 4: Final pass and selective apply
    _count_inliers_kernel(
        flow_gpu, best_model_x, best_model_y, threshold, inlier_mask, h, w
    )
    _selective_ransac_apply_kernel(
        flow_gpu, motion_mask, inlier_mask, best_model_x, best_model_y, output_gpu, h, w
    )

    # Release temporary buffers
    common.release_temp_buffer(motion_mask)
    common.release_temp_buffer(inlier_mask)
    common.release_temp_buffer(mean_out)

    if is_numpy:
        result = output_gpu.to_numpy()
        common.release_temp_buffer(flow_gpu)
        common.release_temp_buffer(output_gpu)
        return result

    # If input was not numpy, return GPU buffer
    return output_gpu


def ransac_flow_cleanup_local(
    flow,
    block_size: int = 64,
    threshold: float = 2.0,
    n_iterations: int = 5,
    buffer_provider="pool",
):
    """
    Local RANSAC - GPU Accelerated.
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    h, w = flow.shape[:2]

    # Handle Input
    is_numpy = isinstance(flow, np.ndarray)
    flow_gpu = flow
    if is_numpy:
        flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
        flow_gpu.from_numpy(flow.astype(np.float32))

    output_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    # Grid sizes
    grid_h = (h + block_size - 1) // block_size
    grid_w = (w + block_size - 1) // block_size

    # Allocations
    # Current State
    current_models = common.get_temp_buffer(
        (grid_h, grid_w, 2), ti.f32, buffer_provider
    )
    inlier_counts = common.get_temp_buffer((grid_h, grid_w), ti.i32, buffer_provider)
    inlier_sums = common.get_temp_buffer((grid_h, grid_w, 2), ti.f32, buffer_provider)

    # Best State
    best_models = common.get_temp_buffer((grid_h, grid_w, 2), ti.f32, buffer_provider)
    best_counts = common.get_temp_buffer((grid_h, grid_w), ti.i32, buffer_provider)
    best_counts.fill(-1)

    # Helper for init
    block_counts_buf = common.get_temp_buffer((grid_h, grid_w), ti.f32, buffer_provider)

    # 1. Initial Mean
    block_counts_buf.fill(0)
    current_models.fill(0)
    _local_ransac_init_means(
        flow_gpu, current_models, block_counts_buf, h, w, block_size
    )
    _local_ransac_normalize_means(current_models, block_counts_buf, grid_h, grid_w)

    # 2. Iterations
    for _ in range(n_iterations):
        # Reset counters
        inlier_counts.fill(0)
        inlier_sums.fill(0)

        # Count Inliers & Accumulate Sums
        _local_ransac_count_inliers(
            flow_gpu,
            current_models,
            inlier_counts,
            inlier_sums,
            threshold,
            h,
            w,
            block_size,
        )

        # Update Best & Compute Next Model
        _local_ransac_update_best(
            current_models,
            inlier_counts,
            inlier_sums,
            best_models,
            best_counts,
            current_models,
            grid_h,
            grid_w,
        )

    # 3. Apply
    _local_ransac_apply(flow_gpu, best_models, output_gpu, threshold, h, w, block_size)

    # Cleanup internal temp buffers
    common.release_temp_buffer(current_models)
    common.release_temp_buffer(inlier_counts)
    common.release_temp_buffer(inlier_sums)
    common.release_temp_buffer(best_models)
    common.release_temp_buffer(best_counts)
    common.release_temp_buffer(block_counts_buf)

    if is_numpy:
        result = output_gpu.to_numpy()
        common.release_temp_buffer(flow_gpu)
        common.release_temp_buffer(output_gpu)
        return result

    common.release_temp_buffer(block_counts_buf)

    if is_numpy:
        result = output_gpu.to_numpy()
        common.release_temp_buffer(flow_gpu)
        common.release_temp_buffer(output_gpu)
        return result

    return output_gpu
