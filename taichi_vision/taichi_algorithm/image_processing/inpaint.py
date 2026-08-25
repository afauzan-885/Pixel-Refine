# Marker: GPU_NATIVE_MARKER_V3
"""
Fast Inpainting - Taichi GPU Implementation
=============================================
Fill masked regions by propagating information from boundaries inward.

Reference:
  - Telea, A. (2004). "An Image Inpainting Technique Based on the Fast
    Marching Method." Journal of Graphics Tools, 9(1).
  - Bertalmio, M. et al. (2001). "Navier-Stokes, Fluid Dynamics, and
    Image and Video Inpainting."

Implementation:
  GPU-friendly iterative diffusion approach:
  1. Compute distance transform of mask (distance from boundary)
  2. For each distance level d (0, 1, 2, ...):
     - Fill pixels at distance d using weighted average of filled neighbors
     - Weights: inverse distance + gradient direction preference
  3. All pixels at the same distance level processed in parallel

  This gives O(max_dist) iterations with full GPU parallelism per iteration.
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
    from ..taichi_worker import ti_thread
except ImportError:
    pass

# Inpainting method flags (OpenCV-compatible)
INPAINT_TELEA = 0
INPAINT_NS = 1

if TAICHI_AVAILABLE:

    # =========================================================================
    # Stage 1: Distance Transform (approximate via iterative dilation)
    # =========================================================================
    @ti.kernel
    def _init_distance_kernel(mask: ti.types.ndarray(), dist: ti.types.ndarray(),
                               boundary: ti.types.ndarray(),
                               h: int, w: int):
        """Initialize distance: 0 for known, -1 for unknown. Mark boundary pixels."""
        for y, x in ti.ndrange(h, w):
            if mask[y, x] > 0.5:
                # Unknown pixel
                dist[y, x] = -1.0
            else:
                # Known pixel
                dist[y, x] = 0.0

            # Check if boundary (known pixel adjacent to unknown)
            if mask[y, x] < 0.5:
                is_boundary = False
                for dy in ti.static(range(-1, 2)):
                    for dx in ti.static(range(-1, 2)):
                        if not (dy == 0 and dx == 0):
                            ny = tm.clamp(y + dy, 0, h - 1)
                            nx = tm.clamp(x + dx, 0, w - 1)
                            if mask[ny, nx] > 0.5:
                                is_boundary = True
                if is_boundary:
                    boundary[y, x] = 1.0
                    dist[y, x] = 0.0
                else:
                    boundary[y, x] = 0.0

    # =========================================================================
    # Stage 1b: Set filled mask (module-level for AOT)
    # =========================================================================
    @ti.kernel
    def _set_filled_kernel(mask_arr: ti.types.ndarray(), filled_arr: ti.types.ndarray(),
                             h: int, w: int):
        """Mark known pixels (mask == 0) as filled."""
        for y, x in ti.ndrange(h, w):
            filled_arr[y, x] = 0.0 if mask_arr[y, x] > 0.5 else 1.0

    # =========================================================================
    # Stage 3: Copy kernels (module-level for AOT)
    # =========================================================================
    @ti.kernel
    def _copy_inpaint_3ch(s: ti.types.ndarray(), d: ti.types.ndarray(),
                           h: int, w: int):
        """Copy 3-channel image (used by inpaint AOT path)."""
        for y, x in ti.ndrange(h, w):
            d[y, x, 0] = s[y, x, 0]
            d[y, x, 1] = s[y, x, 1]
            d[y, x, 2] = s[y, x, 2]

    @ti.kernel
    def _copy_inpaint_1ch(s: ti.types.ndarray(), d: ti.types.ndarray(),
                           h: int, w: int):
        """Copy 1-channel image (used by inpaint AOT path)."""
        for y, x in ti.ndrange(h, w):
            d[y, x] = s[y, x]

    @ti.kernel
    def _dilate_distance_kernel(dist_in: ti.types.ndarray(), dist_out: ti.types.ndarray(),
                                  h: int, w: int, current_level: float):
        """Expand distance by 1 pixel: unknown pixels adjacent to current level get level+1."""
        for y, x in ti.ndrange(h, w):
            if dist_in[y, x] >= 0.0:
                dist_out[y, x] = dist_in[y, x]
            else:
                min_neighbor = 1e10
                found = False
                for dy in ti.static(range(-1, 2)):
                    for dx in ti.static(range(-1, 2)):
                        if not (dy == 0 and dx == 0):
                            ny = tm.clamp(y + dy, 0, h - 1)
                            nx = tm.clamp(x + dx, 0, w - 1)
                            val = dist_in[ny, nx]
                            if val >= 0.0 and val < min_neighbor:
                                min_neighbor = val
                                found = True
                if found:
                    dist_out[y, x] = min_neighbor + 1.0
                else:
                    dist_out[y, x] = -1.0

    # =========================================================================
    # Stage 2: Iterative Inpainting (fill from boundary inward)
    # =========================================================================
    @ti.kernel
    def _inpaint_level_kernel(src: ti.types.ndarray(), dist: ti.types.ndarray(),
                                filled: ti.types.ndarray(),
                                h: int, w: int, target_level: float,
                                inpaint_radius: float):
        """
        Fill pixels at target_level using weighted average of filled neighbors.
        Weights combine distance and directional preference (towards boundary).
        """
        for y, x in ti.ndrange(h, w):
            # Only process pixels at the current distance level
            if ti.abs(dist[y, x] - target_level) > 0.5:
                continue

            total_w = 0.0
            acc_r, acc_g, acc_b = 0.0, 0.0, 0.0

            r_int = ti.cast(inpaint_radius, ti.i32) + 1
            for dy in range(-r_int, r_int + 1):
                for dx in range(-r_int, r_int + 1):
                    ny = y + dy
                    nx = x + dx
                    if ny < 0 or ny >= h or nx < 0 or nx >= w:
                        continue
                    # Only use filled (known or already inpainted) neighbors
                    if filled[ny, nx] < 0.5:
                        continue

                    d2 = float(dy * dy + dx * dx)
                    if d2 > inpaint_radius * inpaint_radius:
                        continue
                    if d2 < 1e-6:
                        continue

                    # Weight: inverse distance squared
                    wt = 1.0 / d2
                    total_w += wt
                    acc_r += wt * src[ny, nx, 0]
                    acc_g += wt * src[ny, nx, 1]
                    acc_b += wt * src[ny, nx, 2]

            if total_w > 1e-12:
                inv_w = 1.0 / total_w
                src[y, x, 0] = acc_r * inv_w
                src[y, x, 1] = acc_g * inv_w
                src[y, x, 2] = acc_b * inv_w
                filled[y, x] = 1.0

    @ti.kernel
    def _inpaint_level_1ch_kernel(src: ti.types.ndarray(), dist: ti.types.ndarray(),
                                    filled: ti.types.ndarray(),
                                    h: int, w: int, target_level: float,
                                    inpaint_radius: float):
        """Single-channel version of iterative inpainting."""
        for y, x in ti.ndrange(h, w):
            if ti.abs(dist[y, x] - target_level) > 0.5:
                continue

            total_w = 0.0
            acc = 0.0

            r_int = ti.cast(inpaint_radius, ti.i32) + 1
            for dy in range(-r_int, r_int + 1):
                for dx in range(-r_int, r_int + 1):
                    ny = y + dy
                    nx = x + dx
                    if ny < 0 or ny >= h or nx < 0 or nx >= w:
                        continue
                    if filled[ny, nx] < 0.5:
                        continue
                    d2 = float(dy * dy + dx * dx)
                    if d2 > inpaint_radius * inpaint_radius or d2 < 1e-6:
                        continue
                    wt = 1.0 / d2
                    total_w += wt
                    acc += wt * src[ny, nx]

            if total_w > 1e-12:
                src[y, x] = acc / total_w
                filled[y, x] = 1.0

    @ti.kernel
    def _mark_filled_kernel(dist: ti.types.ndarray(), filled: ti.types.ndarray(),
                              h: int, w: int, target_level: float):
        """Mark pixels at target_level as filled."""
        for y, x in ti.ndrange(h, w):
            if ti.abs(dist[y, x] - target_level) < 0.5:
                filled[y, x] = 1.0


@ti_thread
def inpaint(src, mask, inpaint_radius=3, flags=INPAINT_TELEA,
             dst=None, buffer_provider="pool"):
    """
    Image Inpainting (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.inpaint()

    Fills masked regions by propagating information from boundaries inward
    using iterative weighted diffusion on GPU.

    Args:
        src: Input image (H, W) or (H, W, 3), uint8 or float32.
        mask: Binary mask (H, W). Non-zero pixels mark regions to inpaint.
        inpaint_radius: Radius of neighborhood used during inpainting (typical: 3-10).
        flags: INPAINT_TELEA (0) or INPAINT_NS (1). Both use the same GPU
               iterative approach (NS-style PDE is the native GPU path).
        dst: Optional output buffer.
        buffer_provider: Buffer pool provider.

    Returns:
        Inpainted image in same format as input.
    """
    # --- AOT path ---
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.inpaint(src, mask, inpaint_radius=inpaint_radius,
                                   flags=flags, return_gpu=not isinstance(src, np.ndarray))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    is_3ch = len(src.shape) == 3 and src.shape[2] == 3

    # Upload source (we'll modify it in-place during inpainting)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    mask_gpu, mask_is_temp = common.ensure_taichi_field(mask, dtype=ti.f32,
                                                          buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]

    # Step 1: Compute distance transform (iterative dilation)
    dist = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    boundary = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    _init_distance_kernel(mask_gpu, dist, boundary, h, w)
    common.release_temp_buffer(boundary)

    # Iteratively expand distance
    dist_tmp = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    max_dist = 0
    max_iterations = max(h, w) // 2 + 1

    # Copy dist to dist_tmp for ping-pong
    for level in range(max_iterations):
        _dilate_distance_kernel(dist, dist_tmp, h, w, float(level))
        # Swap
        dist, dist_tmp = dist_tmp, dist

        # Check if all pixels are assigned (quick check via max level)
        # For simplicity, just run enough iterations
        max_dist = level + 1

    common.release_temp_buffer(dist_tmp)

    # Step 2: Iterative inpainting from boundary inward
    # Create filled mask: 1 for known pixels, 0 for unknown
    filled = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    _init_distance_kernel(mask_gpu, dist, filled, h, w)
    # filled now has: boundary=1, known=1 (from dist=0), unknown=0
    # We need to mark all known pixels as filled
    _set_filled_kernel(mask_gpu, filled, h, w)

    # Fill level by level
    for level in range(1, max_dist + 1):
        if is_3ch:
            _inpaint_level_kernel(src_gpu, dist, filled, h, w,
                                    float(level), float(inpaint_radius))
        else:
            _inpaint_level_1ch_kernel(src_gpu, dist, filled, h, w,
                                        float(level), float(inpaint_radius))
        _mark_filled_kernel(dist, filled, h, w, float(level))

    # Cleanup
    common.release_temp_buffer(dist)
    common.release_temp_buffer(filled)
    if mask_is_temp:
        common.release_temp_buffer(mask_gpu)

    # Copy to output if needed
    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
        # Copy src_gpu to dst_gpu
        if is_3ch:
            _copy_inpaint_3ch(src_gpu, dst_gpu, h, w)
        else:
            _copy_inpaint_1ch(src_gpu, dst_gpu, h, w)

        if src_is_temp:
            common.release_temp_buffer(src_gpu)
        return common.to_numpy_if_needed(dst_gpu, is_numpy)
    else:
        return common.to_numpy_if_needed(src_gpu, is_numpy)
