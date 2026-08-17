"""
Horn-Schunck Optical Flow - Taichi GPU AOT
===========================================
Dense optical flow via Horn-Schunck variational method on GPU.
Based on: Horn & Schunck, "Determining Optical Flow", Artificial Intelligence 17 (1981).

OpenCV equivalent: cv2.calcOpticalFlowHS()

Algorithm:
  1. Compute image gradients Ix, Iy (central finite differences from averaged frame).
  2. Compute temporal gradient It = comp - ref.
  3. Initialize flow to zero (or upsample from coarser level).
  4. Run N Jacobi iterations per pixel:
       u_avg = average of 4 neighbors' u
       v_avg = average of 4 neighbors' v
       P = Ix*u_avg + Iy*v_avg + It
       D = alpha^2 + Ix^2 + Iy^2
       u = u_avg - Ix * P / D
       v = v_avg - Iy * P / D
  5. Coarse-to-fine pyramid with bicubic flow upsampling.

Parameters:
  alpha     : Smoothness weight (higher = smoother flow). Typical: 0.5-2.0 for [0,255] images.
  num_iters : Jacobi iterations per pyramid level. Typical: 10-50.

Graph pipeline (3-level pyramid):
  L2: compute_gradients + zero_init + N Jacobi iters
      → upsample → L1: compute_gradients + project_flow + N Jacobi iters
      → upsample → L0: compute_gradients + project_flow + N Jacobi iters
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass


# =============================================================================
# TAICHI KERNELS (only available when AOT_MODE=0)
# =============================================================================

if TAICHI_AVAILABLE:

    # =========================================================================
    # SECTION A: DEVICE MATH FUNCTIONS (@ti.func) — INFRASTRUCTURE
    # =========================================================================

    @ti.func
    def _bicubic_weight(x: ti.f32) -> ti.f32:
        """Weight function for bicubic interpolation (Catmull-Rom spline)."""
        abs_x = ti.abs(x)
        res = 0.0
        if abs_x <= 1.0:
            res = 1.5 * abs_x**3 - 2.5 * abs_x**2 + 1.0
        elif abs_x < 2.0:
            res = -0.5 * abs_x**3 + 2.5 * abs_x**2 - 4.0 * abs_x + 2.0
        return res

    @ti.func
    def _clamp_coord(val: ti.i32, lo: ti.i32, hi: ti.i32) -> ti.i32:
        """Boundary-safe coordinate clamp."""
        return ti.max(lo, ti.min(val, hi))

    # =========================================================================
    # SECTION B: HORN-SCHUNCK GRADIENT COMPUTATION
    # =========================================================================
    # No separate cost function needed. Horn-Schunck uses gradient-based
    # formulation (brightness constancy + smoothness regularization).

    @ti.func
    def _hs_compute_gradients_at(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y: ti.i32,
        x: ti.i32,
        h: ti.i32,
        w: ti.i32,
    ):
        """
        Compute Ix, Iy, It at pixel (y,x) using central finite differences.
        Gradients are computed from avg = (ref + comp) / 2, matching OpenCV HS.

        Returns (ix, iy, it) as a tuple.
        """
        # Clamp neighbor coordinates
        xp = _clamp_coord(x + 1, 0, w - 1)
        xm = _clamp_coord(x - 1, 0, w - 1)
        yp = _clamp_coord(y + 1, 0, h - 1)
        ym = _clamp_coord(y - 1, 0, h - 1)

        # Average frame: avg = (ref + comp) / 2
        avg_c  = (ref[y, x]  + comp[y, x])  * 0.5
        avg_xp = (ref[y, xp] + comp[y, xp]) * 0.5
        avg_xm = (ref[y, xm] + comp[y, xm]) * 0.5
        avg_yp = (ref[yp, x] + comp[yp, x]) * 0.5
        avg_ym = (ref[ym, x] + comp[ym, x]) * 0.5

        # Spatial gradients from averaged frame
        ix = (avg_xp - avg_xm) * 0.5
        iy = (avg_yp - avg_ym) * 0.5

        # Temporal gradient
        it = comp[y, x] - ref[y, x]

        return ix, iy, it

    # =========================================================================
    # SECTION C: HORN-SCHUNCK KERNELS
    # =========================================================================

    # --- Gradient computation kernel (for external dispatch / parity testing) ---

    @ti.kernel
    def _hs_compute_gradients_kernel(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        Ix: ti.types.ndarray(),
        Iy: ti.types.ndarray(),
        It: ti.types.ndarray(),
    ):
        """
        Compute spatial gradients (Ix, Iy) and temporal gradient (It).
        Uses central finite differences from avg = (ref + comp) / 2.

        INPUT:
            ref  : Reference image (H x W, f32)
            comp : Comparison image (H x W, f32)
        OUTPUT:
            Ix : Spatial x-gradient (H x W, f32)
            Iy : Spatial y-gradient (H x W, f32)
            It : Temporal gradient (H x W, f32)
        """
        h, w = ref.shape[0], ref.shape[1]
        for y, x in ti.ndrange(h, w):
            ix, iy, it = _hs_compute_gradients_at(ref, comp, y, x, h, w)
            Ix[y, x] = ix
            Iy[y, x] = iy
            It[y, x] = it

    # --- Single Jacobi step kernel (for external dispatch / parity testing) ---

    @ti.kernel
    def _hs_jacobi_step_kernel(
        Ix: ti.types.ndarray(),
        Iy: ti.types.ndarray(),
        It: ti.types.ndarray(),
        flow_src: ti.types.ndarray(),
        flow_dst: ti.types.ndarray(),
        alpha: ti.f32,
    ):
        """
        One Jacobi iteration step. Reads from flow_src, writes to flow_dst.
        For external dispatch: call N times with swapped src/dst buffers.

        INPUT:
            Ix, Iy, It : Precomputed gradients (H x W, f32)
            flow_src    : Input flow field (H x W x 2, f32)
            alpha       : Smoothness weight (f32)
        OUTPUT:
            flow_dst    : Updated flow field (H x W x 2, f32)
        """
        h, w = Ix.shape[0], Ix.shape[1]
        alpha_sq = alpha * alpha

        for y, x in ti.ndrange(h, w):
            # 4-neighbor average of flow_src
            u_avg = 0.0
            v_avg = 0.0
            for dy, dx in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                ny = _clamp_coord(y + dy, 0, h - 1)
                nx = _clamp_coord(x + dx, 0, w - 1)
                u_avg += flow_src[ny, nx, 0]
                v_avg += flow_src[ny, nx, 1]
            u_avg *= 0.25
            v_avg *= 0.25

            # Horn-Schunck update
            ix = Ix[y, x]
            iy = Iy[y, x]
            P = ix * u_avg + iy * v_avg + It[y, x]
            D = alpha_sq + ix * ix + iy * iy

            flow_dst[y, x, 0] = u_avg - ix * P / D
            flow_dst[y, x, 1] = v_avg - iy * P / D

    # --- Coarsest level kernel (in-kernel, self-contained) ---

    @ti.kernel
    def _hs_coarsest_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        flow_temp: ti.types.ndarray(),
        alpha: ti.f32,
        num_iters: ti.i32,
    ):
        """
        Entry point kernel at the coarsest pyramid level (L2).
        Computes gradients, initializes flow to zero, and runs N Jacobi iterations.

        INPUT:
            ref_layer  : Reference image at L2 (H x W, f32)
            comp_layer : Comparison image at L2 (H x W, f32)
            flow       : Flow field (H x W x 2, f32) — will be OVERWRITTEN
            flow_temp  : Temporary flow buffer (H x W x 2, f32)
            alpha      : Smoothness weight (f32)
            num_iters  : Number of Jacobi iterations (i32)
        OUTPUT:
            flow : Final flow field at L2 (result in flow, not flow_temp)
        """
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        alpha_sq = alpha * alpha

        for y, x in ti.ndrange(h, w):
            # 1. Compute gradients at this pixel
            ix, iy, it = _hs_compute_gradients_at(ref_layer, comp_layer, y, x, h, w)

            # 2. Initialize flow to zero
            flow[y, x, 0] = 0.0
            flow[y, x, 1] = 0.0
            flow_temp[y, x, 0] = 0.0
            flow_temp[y, x, 1] = 0.0

            # 3. Run N Jacobi iterations (sequential per pixel, parallel across pixels)
            # Note: This is a per-pixel Gauss-Seidel-like approach where each pixel
            # converges independently using its initial neighbor values.
            # For exact OpenCV parity, use external dispatch (_hs_jacobi_step_kernel).
            u = 0.0
            v = 0.0
            for _iter in range(num_iters):
                # 4-neighbor average from flow (which holds the latest values)
                u_avg = 0.0
                v_avg = 0.0
                for dy, dx in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    ny = _clamp_coord(y + dy, 0, h - 1)
                    nx = _clamp_coord(x + dx, 0, w - 1)
                    u_avg += flow[ny, nx, 0]
                    v_avg += flow[ny, nx, 1]
                u_avg *= 0.25
                v_avg *= 0.25

                # Horn-Schunck update
                P = ix * u_avg + iy * v_avg + it
                D = alpha_sq + ix * ix + iy * iy
                u = u_avg - ix * P / D
                v = v_avg - iy * P / D

                # Write back to flow for next iteration's neighbor reads
                flow[y, x, 0] = u
                flow[y, x, 1] = v

    # --- Refinement level kernel (in-kernel, self-contained) ---

    @ti.kernel
    def _hs_refinement_level_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        flow_temp: ti.types.ndarray(),
        previous_flow: ti.types.ndarray(),
        alpha: ti.f32,
        num_iters: ti.i32,
        downscale_factor: ti.i32,
    ):
        """
        Refinement kernel for mid (L1) and fine (L0) pyramid levels.
        Computes gradients, projects flow from coarser level, runs N Jacobi iterations.

        INPUT:
            ref_layer     : Reference image at current level (H x W, f32)
            comp_layer    : Comparison image at current level (H x W, f32)
            flow          : Flow field (H x W x 2, f32) — will be OVERWRITTEN
            flow_temp     : Temporary flow buffer (H x W x 2, f32)
            previous_flow : Flow field from coarser level (H_prev x W_prev x 2, f32)
            alpha         : Smoothness weight (f32)
            num_iters     : Number of Jacobi iterations (i32)
            downscale_factor : Ratio between current and previous level (typically 2)
        OUTPUT:
            flow : Refined flow field at current level
        """
        h, w = ref_layer.shape[0], ref_layer.shape[1]
        prev_h, prev_w = previous_flow.shape[0], previous_flow.shape[1]
        alpha_sq = alpha * alpha

        for y, x in ti.ndrange(h, w):
            # 1. Compute gradients at this pixel
            ix, iy, it = _hs_compute_gradients_at(ref_layer, comp_layer, y, x, h, w)

            # 2. Project flow from coarser level
            py = y // downscale_factor
            px = x // downscale_factor
            u = 0.0
            v = 0.0
            if py < prev_h and px < prev_w:
                u = previous_flow[py, px, 0] * float(downscale_factor)
                v = previous_flow[py, px, 1] * float(downscale_factor)

            # Initialize flow with projected values
            flow[y, x, 0] = u
            flow[y, x, 1] = v

            # 3. Run N Jacobi iterations
            for _iter in range(num_iters):
                # 4-neighbor average from flow
                u_avg = 0.0
                v_avg = 0.0
                for dy, dx in ti.static([(-1, 0), (1, 0), (0, -1), (0, 1)]):
                    ny = _clamp_coord(y + dy, 0, h - 1)
                    nx = _clamp_coord(x + dx, 0, w - 1)
                    u_avg += flow[ny, nx, 0]
                    v_avg += flow[ny, nx, 1]
                u_avg *= 0.25
                v_avg *= 0.25

                # Horn-Schunck update
                P = ix * u_avg + iy * v_avg + it
                D = alpha_sq + ix * ix + iy * iy
                u = u_avg - ix * P / D
                v = v_avg - iy * P / D

                # Write back to flow for next iteration
                flow[y, x, 0] = u
                flow[y, x, 1] = v

    # --- Utility kernels ---

    @ti.kernel
    def _hs_clear_flow_kernel(
        flow: ti.types.ndarray(),
    ):
        """Zero-initialize a flow field (H x W x 2)."""
        h, w = flow.shape[0], flow.shape[1]
        for y, x in ti.ndrange(h, w):
            flow[y, x, 0] = 0.0
            flow[y, x, 1] = 0.0

    @ti.kernel
    def _hs_copy_flow_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
    ):
        """Copy flow field from src to dst (both H x W x 2)."""
        h, w = src.shape[0], src.shape[1]
        for y, x in ti.ndrange(h, w):
            dst[y, x, 0] = src[y, x, 0]
            dst[y, x, 1] = src[y, x, 1]

    # =========================================================================
    # INFRASTRUCTURE: Flow Upsampling (DO NOT MODIFY)
    # =========================================================================

    @ti.kernel
    def _upsample_flow_bicubic_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        scale: ti.f32,
    ):
        """
        Upsamples motion vector field between pyramid levels via bicubic interpolation.
        Used by ALL optical flow paradigms. Do not replace this kernel.
        """
        h_src, w_src = src.shape[0], src.shape[1]
        h_dst, w_dst = dst.shape[0], dst.shape[1]

        for i, j in ti.ndrange(h_dst, w_dst):
            y_src = float(i) / scale
            x_src = float(j) / scale
            y_int = ti.floor(y_src, ti.i32)
            x_int = ti.floor(x_src, ti.i32)
            y_fract = y_src - float(y_int)
            x_fract = x_src - float(x_int)

            for k in ti.static(range(2)):
                val = 0.0
                for m in ti.static(range(-1, 3)):
                    for n in ti.static(range(-1, 3)):
                        yy = _clamp_coord(y_int + m, 0, h_src - 1)
                        xx = _clamp_coord(x_int + n, 0, w_src - 1)
                        w_m = _bicubic_weight(float(m) - y_fract)
                        w_n = _bicubic_weight(float(n) - x_fract)
                        val += src[yy, xx, k] * w_m * w_n
                dst[i, j, k] = val * scale
