# Marker: GPU_NATIVE_MARKER_V3
"""
RANSAC - Taichi GPU Implementation
==================================
GPU-accelerated RANSAC for optical flow outlier removal.

Simple translation/affine model fitting with parallel inlier counting.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None


if TAICHI_AVAILABLE:

    @ti.kernel
    def _compute_mean_flow_kernel(
        flow: ti.types.ndarray(),
        mean_out: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Compute mean flow vector (simple translation model)."""
        sum_x = 0.0
        sum_y = 0.0
        count = 0.0

        for y, x in ti.ndrange(h, w):
            sum_x += flow[y, x, 0]
            sum_y += flow[y, x, 1]
            count += 1.0

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
            sorted_x[idx] = flow[y, x, 0]
            sorted_y[idx] = flow[y, x, 1]

    @ti.kernel
    def _count_inliers_kernel(
        flow: ti.types.ndarray(),
        model_x: float,
        model_y: float,
        threshold: float,
        inlier_mask: ti.types.ndarray(),
        h: int,
        w: int,
    ) -> int:
        """Count inliers that are within threshold of the model."""
        count = 0
        for y, x in ti.ndrange(h, w):
            dx = flow[y, x, 0] - model_x
            dy = flow[y, x, 1] - model_y
            dist = ti.sqrt(dx * dx + dy * dy)

            if dist < threshold:
                inlier_mask[y, x] = 1
                count += 1
            else:
                inlier_mask[y, x] = 0

        return count

    @ti.kernel
    def _compute_inlier_mean_kernel(
        flow: ti.types.ndarray(),
        inlier_mask: ti.types.ndarray(),
        mean_out: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Compute mean flow of inliers only."""
        sum_x = 0.0
        sum_y = 0.0
        count = 0.0

        for y, x in ti.ndrange(h, w):
            if inlier_mask[y, x] == 1:
                sum_x += flow[y, x, 0]
                sum_y += flow[y, x, 1]
                count += 1.0

        if count > 0:
            mean_out[0] = sum_x / count
            mean_out[1] = sum_y / count
        else:
            mean_out[0] = 0.0
            mean_out[1] = 0.0

    @ti.kernel
    def _apply_ransac_result_kernel(
        flow: ti.types.ndarray(),
        inlier_mask: ti.types.ndarray(),
        model_x: float,
        model_y: float,
        output: ti.types.ndarray(),
        h: int,
        w: int,
    ):
        """Replace outlier flow with model prediction."""
        for y, x in ti.ndrange(h, w):
            if inlier_mask[y, x] == 1:
                # Keep inlier values
                output[y, x, 0] = flow[y, x, 0]
                output[y, x, 1] = flow[y, x, 1]
            else:
                # Replace outlier with model
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
