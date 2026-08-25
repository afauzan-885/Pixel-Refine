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
    from .. import common
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
                sum_x += flow[iy, ix, 0]
                sum_y += flow[iy, ix, 1]
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
            sorted_x[idx] = flow[y, x, 0]
            sorted_y[idx] = flow[y, x, 1]

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
        model_x, model_y = model[0], model[1]
        for y, x in ti.ndrange((h + stride - 1) // stride, (w + stride - 1) // stride):
            iy, ix = y * stride, x * stride
            if iy < h and ix < w:
                dx = flow[iy, ix, 0] - model_x
                dy = flow[iy, ix, 1] - model_y
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
                    sum_x += flow[iy, ix, 0]
                    sum_y += flow[iy, ix, 1]
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
                output[y, x, 0] = flow[y, x, 0]
                output[y, x, 1] = flow[y, x, 1]
            else:
                # Replace outlier with model
                output[y, x, 0] = model_x
                output[y, x, 1] = model_y

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

    # =========================================================================
    # GPU MAGSAC++ HOMOGRAPHY SOLVER (KUSTOM)
    # Paralel GPU RANSAC + Tukey's Biweight soft scoring + Weighted Least Squares
    # =========================================================================

    @ti.func
    def _lcg_rand(seed: ti.u32) -> ti.u32:
        return seed * 1664525 + 1013904223

    @ti.func
    def _solve_8x8(M: ti.types.matrix(8, 8, ti.f32), b: ti.types.vector(8, ti.f32)) -> ti.types.vector(8, ti.f32):
        A = ti.Matrix([[0.0] * 9 for _ in range(8)])
        for r in ti.static(range(8)):
            for c in ti.static(range(8)):
                A[r, c] = M[r, c]
            A[r, 8] = b[r]

        is_singular = 0
        for col in ti.static(range(8)):
            max_val = ti.abs(A[col, col])
            max_row = col
            for row in range(col + 1, 8):
                v = ti.abs(A[row, col])
                if v > max_val:
                    max_val = v
                    max_row = row

            if max_row != col:
                for c in ti.static(range(9)):
                    tmp = A[col, c]
                    A[col, c] = A[max_row, c]
                    A[max_row, c] = tmp

            pivot = A[col, col]
            if ti.abs(pivot) < 1e-9:
                is_singular = 1

            if is_singular == 0:
                for c in range(col, 9):
                    A[col, c] /= pivot
                for row in range(col + 1, 8):
                    factor = A[row, col]
                    for c in range(col, 9):
                        A[row, c] -= factor * A[col, c]

        x = ti.Vector([0.0] * 8)
        if is_singular == 0:
            for step in range(8):
                row = 7 - step
                x[row] = A[row, 8]
                for c in range(row + 1, 8):
                    x[row] -= A[row, c] * x[c]
        return x

    @ti.func
    def _build_and_solve_homography(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        i0: int, i1: int, i2: int, i3: int,
        n_pts: int
    ) -> ti.types.matrix(3, 3, ti.f32):
        M = ti.Matrix([[0.0] * 8 for _ in range(8)])
        b_vec = ti.Vector([0.0] * 8)
        indices = ti.Vector([i0, i1, i2, i3])
        for r in range(4):
            idx = indices[r]
            x1 = pts1[idx, 0]; y1 = pts1[idx, 1]
            x2 = pts2[idx, 0]; y2 = pts2[idx, 1]

            row0 = r * 2
            M[row0, 0] = x1; M[row0, 1] = y1; M[row0, 2] = 1.0
            M[row0, 3] = 0.0; M[row0, 4] = 0.0; M[row0, 5] = 0.0
            M[row0, 6] = -x2 * x1; M[row0, 7] = -x2 * y1
            b_vec[row0] = x2

            row1 = r * 2 + 1
            M[row1, 0] = 0.0; M[row1, 1] = 0.0; M[row1, 2] = 0.0
            M[row1, 3] = x1;  M[row1, 4] = y1;  M[row1, 5] = 1.0
            M[row1, 6] = -y2 * x1; M[row1, 7] = -y2 * y1
            b_vec[row1] = y2

        h = _solve_8x8(M, b_vec)
        H = ti.Matrix([[0.0] * 3 for _ in range(3)])
        H[0, 0] = h[0]; H[0, 1] = h[1]; H[0, 2] = h[2]
        H[1, 0] = h[3]; H[1, 1] = h[4]; H[1, 2] = h[5]
        H[2, 0] = h[6]; H[2, 1] = h[7]; H[2, 2] = 1.0
        return H

    @ti.func
    def _check_collinear(pts: ti.types.ndarray(ti.f32, ndim=2), i0: int, i1: int, i2: int, i3: int) -> bool:
        eps = 10.0
        collinear = False
        
        x0, y0 = pts[i0, 0], pts[i0, 1]
        x1, y1 = pts[i1, 0], pts[i1, 1]
        x2, y2 = pts[i2, 0], pts[i2, 1]
        x3, y3 = pts[i3, 0], pts[i3, 1]
        
        a1 = ti.abs(x0*(y1 - y2) + x1*(y2 - y0) + x2*(y0 - y1))
        a2 = ti.abs(x0*(y1 - y3) + x1*(y3 - y0) + x3*(y0 - y1))
        a3 = ti.abs(x0*(y2 - y3) + x2*(y3 - y0) + x3*(y0 - y2))
        a4 = ti.abs(x1*(y2 - y3) + x2*(y3 - y1) + x3*(y1 - y2))
        
        if a1 < eps or a2 < eps or a3 < eps or a4 < eps:
            collinear = True
        return collinear

    @ti.kernel
    def ransac_homography_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        n_pts: int,
        n_hypotheses: int,
        reproj_threshold: ti.f32,
        H_candidates: ti.types.ndarray(ti.f32, ndim=2),
        inlier_counts: ti.types.ndarray(ti.i32, ndim=1),
        seed_offset: int
    ):
        thresh_sq = reproj_threshold * reproj_threshold

        for hyp_idx in range(n_hypotheses):
            seed = _lcg_rand(ti.u32(hyp_idx) + ti.u32(seed_offset) + ti.u32(2654435769))

            # progressive/random sampling with collinearity check
            i0 = 0; i1 = 0; i2 = 0; i3 = 0
            for retry in range(5):
                seed = _lcg_rand(seed)
                i0 = int(seed % ti.u32(n_pts))
                seed = _lcg_rand(seed)
                i1 = int(seed % ti.u32(n_pts))
                for _ in range(8):
                    if i1 == i0:
                        seed = _lcg_rand(seed)
                        i1 = int(seed % ti.u32(n_pts))
                seed = _lcg_rand(seed)
                i2 = int(seed % ti.u32(n_pts))
                for _ in range(8):
                    if i2 == i0 or i2 == i1:
                        seed = _lcg_rand(seed)
                        i2 = int(seed % ti.u32(n_pts))
                seed = _lcg_rand(seed)
                i3 = int(seed % ti.u32(n_pts))
                for _ in range(8):
                    if i3 == i0 or i3 == i1 or i3 == i2:
                        seed = _lcg_rand(seed)
                        i3 = int(seed % ti.u32(n_pts))
                
                if not _check_collinear(pts1, i0, i1, i2, i3):
                    break

            H = _build_and_solve_homography(pts1, pts2, i0, i1, i2, i3, n_pts)

            # Hitung konsensus dengan soft-scoring Tukey's Biweight (MAGSAC++)
            score_acc = 0.0
            for pt_idx in range(n_pts):
                x1 = pts1[pt_idx, 0]; y1 = pts1[pt_idx, 1]
                x2 = pts2[pt_idx, 0]; y2 = pts2[pt_idx, 1]

                denom = H[2, 0] * x1 + H[2, 1] * y1 + H[2, 2]
                proj_x = (H[0, 0] * x1 + H[0, 1] * y1 + H[0, 2]) / (denom + 1e-9)
                proj_y = (H[1, 0] * x1 + H[1, 1] * y1 + H[1, 2]) / (denom + 1e-9)

                dx = proj_x - x2
                dy = proj_y - y2
                err_sq = dx * dx + dy * dy

                if err_sq < thresh_sq:
                    diff = 1.0 - err_sq / thresh_sq
                    score_acc += diff * diff

            inlier_counts[hyp_idx] = int(score_acc * 1000.0)

            H_candidates[hyp_idx, 0] = H[0, 0]
            H_candidates[hyp_idx, 1] = H[0, 1]
            H_candidates[hyp_idx, 2] = H[0, 2]
            H_candidates[hyp_idx, 3] = H[1, 0]
            H_candidates[hyp_idx, 4] = H[1, 1]
            H_candidates[hyp_idx, 5] = H[1, 2]
            H_candidates[hyp_idx, 6] = H[2, 0]
            H_candidates[hyp_idx, 7] = H[2, 1]
            H_candidates[hyp_idx, 8] = H[2, 2]

    @ti.kernel
    def find_best_candidate_kernel(
        H_candidates: ti.types.ndarray(ti.f32, ndim=2),
        inlier_counts: ti.types.ndarray(ti.i32, ndim=1),
        n_hypotheses: int,
        H_best_out: ti.types.ndarray(ti.f32, ndim=1)
    ):
        for _ in range(1):
            best_val = -1
            best_idx = 0
            for i in range(n_hypotheses):
                if inlier_counts[i] > best_val:
                    best_val = inlier_counts[i]
                    best_idx = i
            for j in ti.static(range(9)):
                H_best_out[j] = H_candidates[best_idx, j]

    @ti.kernel
    def refine_homography_iterative_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        H_best: ti.types.ndarray(ti.f32, ndim=1),
        n_pts: int,
        reproj_threshold: ti.f32,
        max_ref_iters: int,
        early_stop_thresh: ti.f32,
        H_refined_out: ti.types.ndarray(ti.f32, ndim=1)
    ):
        H = ti.Matrix([[0.0] * 3 for _ in range(3)])
        for j in ti.static(range(9)):
            H[j // 3, j % 3] = H_best[j]
            
        thresh_sq = reproj_threshold * reproj_threshold
        
        for _ in range(1):
            prev_mean_err = 1e9
            
            for iter_idx in range(max_ref_iters):
                ATA = ti.Matrix([[0.0] * 8 for _ in range(8)])
                ATb = ti.Vector([0.0] * 8)
                
                inliers_count = 0
                sum_err = 0.0
                
                for i in range(n_pts):
                    x1 = pts1[i, 0]; y1 = pts1[i, 1]
                    x2 = pts2[i, 0]; y2 = pts2[i, 1]
                    
                    denom = H[2, 0] * x1 + H[2, 1] * y1 + H[2, 2]
                    proj_x = (H[0, 0] * x1 + H[0, 1] * y1 + H[0, 2]) / (denom + 1e-9)
                    proj_y = (H[1, 0] * x1 + H[1, 1] * y1 + H[1, 2]) / (denom + 1e-9)
                    
                    dx = proj_x - x2
                    dy = proj_y - y2
                    err_sq = dx * dx + dy * dy
                    
                    if err_sq < thresh_sq:
                        inliers_count += 1
                        sum_err += ti.sqrt(err_sq)
                        
                        row_x = ti.Vector([x1, y1, 1.0, 0.0, 0.0, 0.0, -x2*x1, -x2*y1])
                        row_y = ti.Vector([0.0, 0.0, 0.0, x1, y1, 1.0, -y2*x1, -y2*y1])
                        
                        for r in ti.static(range(8)):
                            for c in ti.static(range(8)):
                                ATA[r, c] += row_x[r] * row_x[c] + row_y[r] * row_y[c]
                            ATb[r] += row_x[r] * x2 + row_y[r] * y2
                            
                if inliers_count < 4:
                    break
                    
                mean_err = sum_err / float(inliers_count)
                
                if mean_err < early_stop_thresh or ti.abs(mean_err - prev_mean_err) < 1e-4:
                    break
                prev_mean_err = mean_err
                
                h_new = _solve_8x8(ATA, ATb)
                H[0, 0] = h_new[0]; H[0, 1] = h_new[1]; H[0, 2] = h_new[2]
                H[1, 0] = h_new[3]; H[1, 1] = h_new[4]; H[1, 2] = h_new[5]
                H[2, 0] = h_new[6]; H[2, 1] = h_new[7]; H[2, 2] = 1.0
                
            for j in ti.static(range(9)):
                H_refined_out[j] = H[j // 3, j % 3]

    @ti.kernel
    def generate_inlier_mask_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        H_best: ti.types.ndarray(ti.f32, ndim=1),
        n_pts: int,
        reproj_threshold: ti.f32,
        mask_out: ti.types.ndarray(ti.i32, ndim=1)
    ):
        for i in range(n_pts):
            x1 = pts1[i, 0]; y1 = pts1[i, 1]
            x2 = pts2[i, 0]; y2 = pts2[i, 1]

            denom = H_best[6] * x1 + H_best[7] * y1 + H_best[8]
            proj_x = (H_best[0] * x1 + H_best[1] * y1 + H_best[2]) / (denom + 1e-9)
            proj_y = (H_best[3] * x1 + H_best[4] * y1 + H_best[5]) / (denom + 1e-9)

            dx = proj_x - x2
            dy = proj_y - y2
            err = dx * dx + dy * dy

            mask_out[i] = 1 if err < reproj_threshold * reproj_threshold else 0

    @ti.kernel
    def refine_homography_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        mask: ti.types.ndarray(ti.i32, ndim=1),
        n_pts: int,
        reproj_threshold: ti.f32,
        ATA_out: ti.types.ndarray(ti.f32, ndim=2),
        ATb_out: ti.types.ndarray(ti.f32, ndim=1)
    ):
        for idx in range(64):
            ATA_out[idx // 8, idx % 8] = 0.0
        for idx in range(8):
            ATb_out[idx] = 0.0

        ti.sync()

        for i in range(n_pts):
            if mask[i] == 1:
                x1 = pts1[i, 0]; y1 = pts1[i, 1]
                x2 = pts2[i, 0]; y2 = pts2[i, 1]

                row_x = ti.Vector([x1, y1, 1.0, 0.0, 0.0, 0.0, -x2*x1, -x2*y1])
                row_y = ti.Vector([0.0, 0.0, 0.0, x1, y1, 1.0, -y2*x1, -y2*y1])
                weight = 1.0

                for r in ti.static(range(8)):
                    for c in ti.static(range(8)):
                        ti.atomic_add(ATA_out[r, c], weight * (row_x[r] * row_x[c] + row_y[r] * row_y[c]))
                    ti.atomic_add(ATb_out[r], weight * (row_x[r] * x2 + row_y[r] * y2))

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

    # =========================================================================
    # GPU VSAC FUNDAMENTAL MATRIX SOLVER
    # 8-point algorithm + Sampson distance + VSAC independent inlier classification
    # =========================================================================

    @ti.func
    def _solve_9x9_homogeneous(M: ti.types.matrix(9, 9, ti.f32)) -> ti.types.vector(9, ti.f32):
        """Solve Mx=0 via Gaussian elimination with partial pivoting. x[8]=1."""
        A = ti.Matrix([[0.0] * 10 for _ in range(9)])
        for r in ti.static(range(9)):
            for c in ti.static(range(9)):
                A[r, c] = M[r, c]
            A[r, 9] = 0.0

        is_singular = 0
        for col in ti.static(range(8)):
            max_val = ti.abs(A[col, col])
            max_row = col
            for row in range(col + 1, 9):
                v = ti.abs(A[row, col])
                if v > max_val:
                    max_val = v
                    max_row = row
            if max_row != col:
                for c in ti.static(range(10)):
                    tmp = A[col, c]
                    A[col, c] = A[max_row, c]
                    A[max_row, c] = tmp
            pivot = A[col, col]
            if ti.abs(pivot) < 1e-9:
                is_singular = 1
            if is_singular == 0:
                for c in range(col, 10):
                    A[col, c] /= pivot
                for row in range(col + 1, 9):
                    factor = A[row, col]
                    for c in range(col, 10):
                        A[row, c] -= factor * A[col, c]

        x = ti.Vector([0.0] * 9)
        x[8] = 1.0
        if is_singular == 0:
            for step in ti.static(range(8)):
                row = 7 - step
                x[row] = A[row, 9]
                for c in range(row + 1, 8):
                    x[row] -= A[row, c] * x[c]
        return x

    @ti.kernel
    def ransac_fundamental_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        n_pts: int,
        n_hypotheses: int,
        threshold: ti.f32,
        F_candidates: ti.types.ndarray(ti.f32, ndim=2),
        scores: ti.types.ndarray(ti.i32, ndim=1),
        seed_offset: int,
    ):
        """Parallel RANSAC for fundamental matrix via 8-point algorithm on GPU."""
        thresh_sq = threshold * threshold

        for hyp_idx in range(n_hypotheses):
            seed = _lcg_rand(ti.u32(hyp_idx) + ti.u32(seed_offset) + ti.u32(2654435769))

            idx = ti.Vector([0] * 8)
            for s in ti.static(range(8)):
                seed = _lcg_rand(seed)
                candidate = int(seed % ti.u32(n_pts))
                for prev in range(s):
                    for _ in range(8):
                        if candidate == idx[prev]:
                            seed = _lcg_rand(seed)
                            candidate = int(seed % ti.u32(n_pts))
                idx[s] = candidate

            ATA = ti.Matrix([[0.0] * 9 for _ in range(9)])
            for s in ti.static(range(8)):
                i = idx[s]
                x1 = pts1[i, 0]; y1 = pts1[i, 1]
                x2 = pts2[i, 0]; y2 = pts2[i, 1]
                a = ti.Vector([x2*x1, x2*y1, x2, y2*x1, y2*y1, y2, x1, y1, 1.0])
                for r in ti.static(range(9)):
                    for c in ti.static(range(9)):
                        ATA[r, c] += a[r] * a[c]

            f = _solve_9x9_homogeneous(ATA)
            F = ti.Matrix([[f[0], f[1], f[2]], [f[3], f[4], f[5]], [f[6], f[7], f[8]]])

            score_acc = 0.0
            for pt_idx in range(n_pts):
                x1 = pts1[pt_idx, 0]; y1 = pts1[pt_idx, 1]
                x2 = pts2[pt_idx, 0]; y2 = pts2[pt_idx, 1]
                c_val = x2*(F[0,0]*x1 + F[0,1]*y1 + F[0,2]) + y2*(F[1,0]*x1 + F[1,1]*y1 + F[1,2]) + (F[2,0]*x1 + F[2,1]*y1 + F[2,2])
                Fx1_0 = F[0,0]*x1 + F[0,1]*y1 + F[0,2]
                Fx1_1 = F[1,0]*x1 + F[1,1]*y1 + F[1,2]
                Ftx2_0 = F[0,0]*x2 + F[1,0]*y2 + F[2,0]
                Ftx2_1 = F[0,1]*x2 + F[1,1]*y2 + F[2,1]
                denom = Fx1_0*Fx1_0 + Fx1_1*Fx1_1 + Ftx2_0*Ftx2_0 + Ftx2_1*Ftx2_1 + 1e-12
                sampson = c_val * c_val / denom

                if sampson < thresh_sq:
                    diff = 1.0 - sampson / thresh_sq
                    score_acc += diff * diff

            scores[hyp_idx] = int(score_acc * 1000.0)
            F_candidates[hyp_idx, 0] = F[0,0]; F_candidates[hyp_idx, 1] = F[0,1]; F_candidates[hyp_idx, 2] = F[0,2]
            F_candidates[hyp_idx, 3] = F[1,0]; F_candidates[hyp_idx, 4] = F[1,1]; F_candidates[hyp_idx, 5] = F[1,2]
            F_candidates[hyp_idx, 6] = F[2,0]; F_candidates[hyp_idx, 7] = F[2,1]; F_candidates[hyp_idx, 8] = F[2,2]

    @ti.kernel
    def generate_fundamental_inlier_mask_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        F_best: ti.types.ndarray(ti.f32, ndim=1),
        n_pts: int,
        threshold: ti.f32,
        mask_out: ti.types.ndarray(ti.i32, ndim=1),
    ):
        """Generate inlier mask using Sampson distance for best fundamental matrix."""
        thresh_sq = threshold * threshold
        F00 = F_best[0]; F01 = F_best[1]; F02 = F_best[2]
        F10 = F_best[3]; F11 = F_best[4]; F12 = F_best[5]
        F20 = F_best[6]; F21 = F_best[7]; F22 = F_best[8]
        for i in range(n_pts):
            x1 = pts1[i, 0]; y1 = pts1[i, 1]
            x2 = pts2[i, 0]; y2 = pts2[i, 1]
            c_val = x2*(F00*x1 + F01*y1 + F02) + y2*(F10*x1 + F11*y1 + F12) + (F20*x1 + F21*y1 + F22)
            Fx1_0 = F00*x1 + F01*y1 + F02
            Fx1_1 = F10*x1 + F11*y1 + F12
            Ftx2_0 = F00*x2 + F10*y2 + F20
            Ftx2_1 = F01*x2 + F11*y2 + F21
            denom = Fx1_0*Fx1_0 + Fx1_1*Fx1_1 + Ftx2_0*Ftx2_0 + Ftx2_1*Ftx2_1 + 1e-12
            sampson = c_val * c_val / denom
            mask_out[i] = 1 if sampson < thresh_sq else 0

    @ti.kernel
    def vsac_classify_independent_kernel(
        pts1: ti.types.ndarray(ti.f32, ndim=2),
        pts2: ti.types.ndarray(ti.f32, ndim=2),
        F_arr: ti.types.ndarray(ti.f32, ndim=1),
        n_pts: int,
        threshold: ti.f32,
        epipole_thresh: ti.f32,
        indep_count_out: ti.types.ndarray(ti.i32, ndim=1),
    ):
        """VSAC: Count independent inliers — exclude points too close to epipoles."""
        thresh_sq = threshold * threshold
        F00 = F_arr[0]; F01 = F_arr[1]; F02 = F_arr[2]
        F10 = F_arr[3]; F11 = F_arr[4]; F12 = F_arr[5]
        F20 = F_arr[6]; F21 = F_arr[7]; F22 = F_arr[8]
        total = 0
        for i in range(n_pts):
            x1 = pts1[i, 0]; y1 = pts1[i, 1]
            x2 = pts2[i, 0]; y2 = pts2[i, 1]
            c_val = x2*(F00*x1 + F01*y1 + F02) + y2*(F10*x1 + F11*y1 + F12) + (F20*x1 + F21*y1 + F22)
            Fx1_0 = F00*x1 + F01*y1 + F02
            Fx1_1 = F10*x1 + F11*y1 + F12
            Ftx2_0 = F00*x2 + F10*y2 + F20
            Ftx2_1 = F01*x2 + F11*y2 + F21
            denom = Fx1_0*Fx1_0 + Fx1_1*Fx1_1 + Ftx2_0*Ftx2_0 + Ftx2_1*Ftx2_1 + 1e-12
            sampson = c_val * c_val / denom
            if sampson < thresh_sq:
                l2_sq_1 = Ftx2_0*Ftx2_0 + Ftx2_1*Ftx2_1
                l2_sq_2 = Fx1_0*Fx1_0 + Fx1_1*Fx1_1
                if l2_sq_1 > epipole_thresh and l2_sq_2 > epipole_thresh:
                    total += 1
        indep_count_out[0] = total


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
        from taichi_vision import taichi_aot
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
    model_buf = common.get_temp_buffer((2,), ti.f32, buffer_provider)
    output_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    # Step 1: Initial model
    _compute_mean_flow_kernel(flow_gpu, mean_out, h, w, 1)
    mean_out_np = mean_out.to_numpy()
    model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 2: Iterative refinement
    best_inlier_count = 0
    best_model_x, best_model_y = model_x, model_y

    for _ in range(n_iterations):
        model_buf.from_numpy(np.asarray([model_x, model_y], dtype=np.float32))
        _count_inliers_kernel(flow_gpu, model_buf, threshold, inlier_mask, h, w, 1)
        inlier_count = int(np.sum(inlier_mask.to_numpy()))

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_model_x, best_model_y = model_x, model_y

        _compute_inlier_mean_kernel(flow_gpu, inlier_mask, mean_out, h, w, 1)
        mean_out_np = mean_out.to_numpy()
        model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 3+4: Final pass and apply
    model_buf.from_numpy(np.asarray([best_model_x, best_model_y], dtype=np.float32))
    _count_inliers_kernel(flow_gpu, model_buf, threshold, inlier_mask, h, w, 1)
    _apply_ransac_result_kernel(
        flow_gpu, inlier_mask, model_buf, output_gpu, h, w
    )

    # Release temporary buffers
    common.release_temp_buffer(inlier_mask)
    common.release_temp_buffer(mean_out)
    common.release_temp_buffer(model_buf)

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
    model_buf = common.get_temp_buffer((2,), ti.f32, buffer_provider)
    output_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

    # Step 1: Compute global motion (median - robust to outliers)
    # For GPU efficiency, we use mean as approximation to median
    _compute_mean_flow_kernel(flow_gpu, mean_out, h, w, 1)
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
        model_buf.from_numpy(np.asarray([model_x, model_y], dtype=np.float32))
        _count_inliers_kernel(flow_gpu, model_buf, threshold, inlier_mask, h, w, 1)
        inlier_count = int(np.sum(inlier_mask.to_numpy()))

        if inlier_count > best_inlier_count:
            best_inlier_count = inlier_count
            best_model_x, best_model_y = model_x, model_y

        _compute_inlier_mean_kernel(flow_gpu, inlier_mask, mean_out, h, w, 1)
        mean_out_np = mean_out.to_numpy()
        model_x, model_y = float(mean_out_np[0]), float(mean_out_np[1])

    # Step 4: Final pass and selective apply
    model_buf.from_numpy(np.asarray([best_model_x, best_model_y], dtype=np.float32))
    _count_inliers_kernel(flow_gpu, model_buf, threshold, inlier_mask, h, w, 1)
    _selective_ransac_apply_kernel(
        flow_gpu, motion_mask, inlier_mask, best_model_x, best_model_y, output_gpu, h, w
    )

    # Release temporary buffers
    common.release_temp_buffer(motion_mask)
    common.release_temp_buffer(inlier_mask)
    common.release_temp_buffer(mean_out)
    common.release_temp_buffer(model_buf)

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


def vsac_fundamental(pts1, pts2, confidence=0.999, threshold=1.0, max_lo=1, n_hypotheses=1024):
    """
    GPU-accelerated VSAC for fundamental matrix estimation.

    Uses 8-point algorithm on GPU for hypothesis generation, Sampson distance
    for scoring, and VSAC independent inlier classification for robustness
    against degenerate dominant-plane configurations.

    Args:
        pts1, pts2: (N, 2) point correspondences. Accepts float32/float64/int, list, or ndarray.
        confidence: RANSAC confidence level (default 0.999)
        threshold: Inlier Sampson distance threshold (default 1.0)
        max_lo: Number of local optimization passes (default 1)
        n_hypotheses: Number of parallel RANSAC hypotheses on GPU (default 1024)

    Returns:
        (F, inlier_mask, stats)
        F: (3, 3) fundamental matrix (float64)
        inlier_mask: (N,) boolean mask of inliers
        stats: dict with timing and quality metrics
    """
    import time
    t0 = time.time()

    # Robust auto-repair: validate and repair point correspondences
    pts1, pts2 = common.validate_point_correspondences(pts1, pts2, min_points=8, name="vsac_points")
    n_pts = len(pts1)

    if n_pts < 8:
        return np.eye(3, dtype=np.float64), np.zeros(n_pts, dtype=np.bool_), {"error": "Need >= 8 points"}

    if os.environ.get("AOT_MODE", "1") == "1" or not TAICHI_AVAILABLE:
        try:
            import cv2
            F_cv, mask = cv2.findFundamentalMat(pts1, pts2, cv2.FM_RANSAC, threshold, confidence)
            if F_cv is not None and F_cv.shape == (3, 3):
                inlier_mask = mask.ravel().astype(np.bool_)
                return F_cv.astype(np.float64), inlier_mask, {"time_ms": (time.time() - t0) * 1000, "n_inliers": int(inlier_mask.sum())}
        except Exception:
            pass
        return np.eye(3, dtype=np.float64), np.zeros(n_pts, dtype=np.bool_), {"error": "No backend available"}

    pts1_gpu = ti.ndarray(dtype=ti.f32, shape=(n_pts, 2))
    pts2_gpu = ti.ndarray(dtype=ti.f32, shape=(n_pts, 2))
    pts1_gpu.from_numpy(pts1)
    pts2_gpu.from_numpy(pts2)

    F_candidates = ti.ndarray(dtype=ti.f32, shape=(n_hypotheses, 9))
    scores = ti.ndarray(dtype=ti.i32, shape=(n_hypotheses,))

    ransac_fundamental_kernel(pts1_gpu, pts2_gpu, n_pts, n_hypotheses, threshold, F_candidates, scores, 42)

    F_cand_np = F_candidates.to_numpy()
    scores_np = scores.to_numpy()
    best_idx = int(np.argmax(scores_np))
    F_best = F_cand_np[best_idx].reshape(3, 3).astype(np.float64)

    F_best_flat = ti.ndarray(dtype=ti.f32, shape=(9,))
    F_best_flat.from_numpy(F_best.astype(np.float32).ravel())
    mask_gpu = ti.ndarray(dtype=ti.i32, shape=(n_pts,))
    generate_fundamental_inlier_mask_kernel(pts1_gpu, pts2_gpu, F_best_flat, n_pts, threshold, mask_gpu)
    inlier_mask = mask_gpu.to_numpy().astype(np.bool_)

    if max_lo > 0 and inlier_mask.sum() >= 8:
        pts1_in = pts1[inlier_mask]
        pts2_in = pts2[inlier_mask]
        if len(pts1_in) >= 8:
            pts1_in_gpu = ti.ndarray(dtype=ti.f32, shape=(len(pts1_in), 2))
            pts2_in_gpu = ti.ndarray(dtype=ti.f32, shape=(len(pts2_in), 2))
            pts1_in_gpu.from_numpy(pts1_in)
            pts2_in_gpu.from_numpy(pts2_in)
            F_refined = ti.ndarray(dtype=ti.f32, shape=(1, 9))
            scores_refined = ti.ndarray(dtype=ti.i32, shape=(1,))
            ransac_fundamental_kernel(pts1_in_gpu, pts2_in_gpu, len(pts1_in), 1, threshold, F_refined, scores_refined, 999)
            F_refined_np = F_refined.to_numpy().reshape(3, 3).astype(np.float64)
            if scores_refined.to_numpy()[0] > scores_np[best_idx]:
                F_best = F_refined_np

    indep_count_gpu = ti.ndarray(dtype=ti.i32, shape=(1,))
    F_best_flat2 = ti.ndarray(dtype=ti.f32, shape=(9,))
    F_best_flat2.from_numpy(F_best.astype(np.float32).ravel())
    vsac_classify_independent_kernel(pts1_gpu, pts2_gpu, F_best_flat2, n_pts, threshold, 1e-4, indep_count_gpu)
    n_independent = int(indep_count_gpu.to_numpy()[0])

    elapsed = (time.time() - t0) * 1000
    stats = {
        "time_ms": elapsed,
        "n_inliers": int(inlier_mask.sum()),
        "n_independent": n_independent,
        "inlier_ratio": float(inlier_mask.sum()) / max(n_pts, 1),
    }
    return F_best, inlier_mask, stats
