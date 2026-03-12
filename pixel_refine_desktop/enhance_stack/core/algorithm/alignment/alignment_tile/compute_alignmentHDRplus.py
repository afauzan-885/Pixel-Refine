"""
Compute Alignment HDR+ - Taichi GPU Implementation
==================================================
Strict implementation of the HDR+ alignment algorithm (coarse-to-fine,
3-candidate upsampling, quadratic subpixel refinement) using Taichi GPU.
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

# Import submodule functions directly from taichi_algorithm
try:
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.pyramid import (
        build_image_pyramid_gpu_4x,
        upsample_flow_gpu,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm import (
        common,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
        ti_thread,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.phase_correlation import (
        phase_correlation as phase_correlation_gpu,
    )

    TAICHI_MODULES_AVAILABLE = True
except ImportError as e:
    print("TAICHI IMPORT ERROR in compute_alignmentHDRplus.py:", e)
    TAICHI_MODULES_AVAILABLE = False


# ============================================================================
# Constants
# ============================================================================
class HDRPlusConfig:
    FLOW_UPSCALE_FACTOR = 4.0
    MIN_TILE_SIZE = 8
    MIN_PYRAMID_LAYER_SIZE = 32
    SEARCH_RADIUS = 4
    SUBPIXEL_ENABLED = True


# ============================================================================
# Taichi Kernels & Functions
# ============================================================================

if TAICHI_AVAILABLE:

    @ti.func
    def _compute_l1_cost(
        ref: ti.types.ndarray(),
        comp: ti.types.ndarray(),
        y_ref: int,
        x_ref: int,
        y_comp: int,
        x_comp: int,
        tile_h: int,
        tile_w: int,
    ) -> float:
        """Compute Sum of Absolute Differences (SAD / L1) cost."""
        total_abs_diff = 0.0
        # Parallel-friendly loop structure for Taichi
        for r, c in ti.ndrange(tile_h, tile_w):
            total_abs_diff += ti.abs(
                ref[y_ref + r, x_ref + c] - comp[y_comp + r, x_comp + c]
            )
        return total_abs_diff / float(tile_h * tile_w)

    @ti.kernel
    def _initialize_flow_kernel(
        flow: ti.types.ndarray(), h: int, w: int, dx: float, dy: float
    ):
        for r, c in ti.ndrange(h, w):
            flow[r, c, 0] = dx
            flow[r, c, 1] = dy

    @ti.kernel
    def _hdrplus_upsample_candidate_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        upsampled_flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
    ):
        step_y, step_x = tile_h // 2, tile_w // 2

        for ty, tx in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y, x = ty * step_y, tx * step_x

            # Identify 3 Candidates: Self, Left Neighbor, Top Neighbor
            cands_dx = ti.Vector([0.0, 0.0, 0.0])
            cands_dy = ti.Vector([0.0, 0.0, 0.0])

            sy, sx = tm.clamp(y + step_y, 0, h - 1), tm.clamp(x + step_x, 0, w - 1)
            cands_dx[0] = upsampled_flow[sy, sx, 0]
            cands_dy[0] = upsampled_flow[sy, sx, 1]

            if x >= step_x:
                cands_dx[1] = upsampled_flow[sy, x - step_x, 0]
                cands_dy[1] = upsampled_flow[sy, x - step_x, 1]
            else:
                cands_dx[1], cands_dy[1] = cands_dx[0], cands_dy[0]

            if y >= step_y:
                cands_dx[2] = upsampled_flow[y - step_y, sx, 0]
                cands_dy[2] = upsampled_flow[y - step_y, sx, 1]
            else:
                cands_dx[2], cands_dy[2] = cands_dx[0], cands_dy[0]

            best_cost, best_dx, best_dy = 1e10, cands_dx[0], cands_dy[0]

            for i in ti.static(range(3)):
                idx_dx, idx_dy = int(ti.round(cands_dx[i])), int(ti.round(cands_dy[i]))
                comp_y, comp_x = y + idx_dy, x + idx_dx

                if 0 <= comp_y < h - tile_h + 1 and 0 <= comp_x < w - tile_w + 1:
                    cost = _compute_l1_cost(
                        ref_layer, comp_layer, y, x, comp_y, comp_x, tile_h, tile_w
                    )
                    if cost < best_cost:
                        best_cost, best_dx, best_dy = cost, cands_dx[i], cands_dy[i]

            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = best_dx
                    refined_flow[y + r, x + c, 1] = best_dy

    @ti.kernel
    def _hdrplus_local_search_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        initial_flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
        search_radius: int,
    ):
        step_y, step_x = tile_h // 2, tile_w // 2

        for ty, tx in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y, x = ty * step_y, tx * step_x
            sy, sx = tm.clamp(y + step_y, 0, h - 1), tm.clamp(x + step_x, 0, w - 1)
            init_dx, init_dy = int(ti.round(initial_flow[sy, sx, 0])), int(
                ti.round(initial_flow[sy, sx, 1])
            )

            best_cost, best_dx, best_dy = 1e10, float(init_dx), float(init_dy)

            for dy, dx in ti.ndrange(
                (-search_radius, search_radius + 1), (-search_radius, search_radius + 1)
            ):
                test_dy, test_dx = init_dy + dy, init_dx + dx
                comp_y, comp_x = y + test_dy, x + test_dx

                if 0 <= comp_y < h - tile_h + 1 and 0 <= comp_x < w - tile_w + 1:
                    cost = _compute_l1_cost(
                        ref_layer, comp_layer, y, x, comp_y, comp_x, tile_h, tile_w
                    )
                    if cost < best_cost:
                        best_cost, best_dx, best_dy = (
                            cost,
                            float(test_dx),
                            float(test_dy),
                        )

            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0] = best_dx
                    refined_flow[y + r, x + c, 1] = best_dy

    @ti.kernel
    def _hdrplus_subpixel_refinement_kernel(
        ref_layer: ti.types.ndarray(),
        comp_layer: ti.types.ndarray(),
        int_flow: ti.types.ndarray(),
        refined_flow: ti.types.ndarray(),
        h: int,
        w: int,
        tile_h: int,
        tile_w: int,
    ):
        fA11 = ti.Vector([0.25, -0.5, 0.25, 0.5, -1.0, 0.5, 0.25, -0.5, 0.25])
        fA22 = ti.Vector([0.25, 0.5, 0.25, -0.5, -1.0, -0.5, 0.25, 0.5, 0.25])
        fA12 = ti.Vector([0.25, 0.0, -0.25, 0.0, 0.0, 0.0, -0.25, 0.0, 0.25])
        fb1 = ti.Vector([-0.125, 0.0, 0.125, -0.25, 0.0, 0.25, -0.125, 0.0, 0.125])
        fb2 = ti.Vector([-0.125, -0.25, -0.125, 0.0, 0.0, 0.0, 0.125, 0.25, 0.125])

        step_y, step_x = tile_h // 2, tile_w // 2

        for ty, tx in ti.ndrange(
            (h - tile_h + 1) // step_y, (w - tile_w + 1) // step_x
        ):
            y, x = ty * step_y, tx * step_x
            sy, sx = tm.clamp(y + step_y, 0, h - 1), tm.clamp(x + step_x, 0, w - 1)
            idx_dx, idx_dy = int(ti.round(int_flow[sy, sx, 0])), int(
                ti.round(int_flow[sy, sx, 1])
            )

            costs = ti.Matrix.zero(ti.f32, 3, 3)
            for j, i in ti.ndrange((-1, 2), (-1, 2)):
                cy, cx = y + idx_dy + j, x + idx_dx + i
                if 0 <= cy < h - tile_h + 1 and 0 <= cx < w - tile_w + 1:
                    costs[j + 1, i + 1] = _compute_l1_cost(
                        ref_layer, comp_layer, y, x, cy, cx, tile_h, tile_w
                    )
                else:
                    costs[j + 1, i + 1] = 1e10

            A11, A12, A22, b1, b2 = 0.0, 0.0, 0.0, 0.0, 0.0
            for j, i in ti.static(ti.ndrange(3, 3)):
                d, k_idx = costs[j, i], j * 3 + i
                A11 += fA11[k_idx] * d
                A12 += fA12[k_idx] * d
                A22 += fA22[k_idx] * d
                b1 += fb1[k_idx] * d
                b2 += fb2[k_idx] * d

            A11, A22 = ti.max(0.0, A11), ti.max(0.0, A22)
            if A11 * A22 - A12**2 < 0:
                A12 = 0.0
            det = A11 * A22 - A12**2
            delta_x, delta_y = 0.0, 0.0
            if det > 1e-6:
                osvI = -(A11 * b2 - A12 * b1) / det
                osvJ = -(A22 * b1 - A12 * b2) / det
                if ti.sqrt(osvI**2 + osvJ**2) < 1.0:
                    delta_x, delta_y = osvI, osvJ

            final_dx, final_dy = float(idx_dx) + delta_x, float(idx_dy) + delta_y
            for r, c in ti.ndrange(tile_h, tile_w):
                if y + r < h and x + c < w:
                    refined_flow[y + r, x + c, 0], refined_flow[y + r, x + c, 1] = (
                        final_dx,
                        final_dy,
                    )


# ============================================================================
# Main Processing Logic
# ============================================================================


def process_single_layer_hdrplus(
    ref_layer_gpu,
    comp_layer_gpu,
    previous_flow_gpu,
    layer_index: int,
    total_layers: int,
    tile_h: int,
    tile_w: int,
) -> any:
    """Coarse-to-fine HDR+ layer processing."""
    h, w = ref_layer_gpu.shape[:2]
    is_coarsest = layer_index == total_layers - 1
    flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")

    if is_coarsest:
        global_dx, global_dy, global_conf = phase_correlation_gpu(
            ref_layer_gpu, comp_layer_gpu, max_shift=32
        )
        _initialize_flow_kernel(flow_gpu, h, w, float(global_dx), float(global_dy))
    else:
        upsample_flow_gpu(
            src_gpu=previous_flow_gpu,
            dst_gpu=flow_gpu,
            scale=HDRPlusConfig.FLOW_UPSCALE_FACTOR,
        )

    refined_flow_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider="pool")
    if not is_coarsest:
        _hdrplus_upsample_candidate_refinement_kernel(
            ref_layer_gpu,
            comp_layer_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            tile_h,
            tile_w,
        )
        common.copy_field(refined_flow_gpu, flow_gpu)

    _hdrplus_local_search_kernel(
        ref_layer_gpu,
        comp_layer_gpu,
        flow_gpu,
        refined_flow_gpu,
        h,
        w,
        tile_h,
        tile_w,
        HDRPlusConfig.SEARCH_RADIUS,
    )
    common.copy_field(refined_flow_gpu, flow_gpu)

    if HDRPlusConfig.SUBPIXEL_ENABLED:
        _hdrplus_subpixel_refinement_kernel(
            ref_layer_gpu,
            comp_layer_gpu,
            flow_gpu,
            refined_flow_gpu,
            h,
            w,
            tile_h,
            tile_w,
        )
        common.copy_field(refined_flow_gpu, flow_gpu)

    common.release_temp_buffer(refined_flow_gpu)
    return flow_gpu


@ti_thread
def compute_alignment_hdrplus(
    ref_work_data: np.ndarray,
    current_work_data: np.ndarray,
    tile_h: int = 16,
    tile_w: int = 16,
    n_layers: int = 3,
    return_confidence: bool = False,
) -> any:
    """Main interface for Taichi-based HDR+ Alignment."""
    if not TAICHI_AVAILABLE or not TAICHI_MODULES_AVAILABLE:
        raise ImportError("Taichi/Modules not ready")

    ti.sync()
    t_start = time.perf_counter()
    ref_gpu, ref_is_temp = common.ensure_taichi_field(ref_work_data, dtype=ti.f32)
    comp_gpu, comp_is_temp = common.ensure_taichi_field(current_work_data, dtype=ti.f32)

    ref_pyramid = build_image_pyramid_gpu_4x(ref_gpu, n_levels=n_layers)
    comp_pyramid = build_image_pyramid_gpu_4x(comp_gpu, n_levels=n_layers)

    actual_layers = min(len(ref_pyramid), len(comp_pyramid))
    flow_gpu = None

    for i in range(actual_layers - 1, -1, -1):
        prev_flow = flow_gpu
        flow_gpu = process_single_layer_hdrplus(
            ref_pyramid[i], comp_pyramid[i], prev_flow, i, actual_layers, tile_h, tile_w
        )
        if prev_flow is not None:
            common.release_temp_buffer(prev_flow)

    # Cleanup Pyramids
    for i, lvl in enumerate(ref_pyramid):
        if i > 0:
            common.release_temp_buffer(lvl)
    for i, lvl in enumerate(comp_pyramid):
        if i > 0:
            common.release_temp_buffer(lvl)
    if ref_is_temp:
        common.release_temp_buffer(ref_gpu)
    if comp_is_temp:
        common.release_temp_buffer(comp_gpu)

    ti.sync()
    t_total = (time.perf_counter() - t_start) * 1000
    print(f"[HDR+ Matcher] Alignment Time: {t_total:.2f}ms")
    return flow_gpu
