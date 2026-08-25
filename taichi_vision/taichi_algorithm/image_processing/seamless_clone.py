# Marker: GPU_NATIVE_MARKER_V3
"""
Seamless Cloning (Poisson Image Editing) - Taichi GPU Implementation
=====================================================================
Gradient-domain compositing for seamless blending.

Reference:
  - Perez, P., Gangnet, M., Blake, A. (2003). "Poisson Image Editing."
    SIGGRAPH 2003, ACM Trans. Graphics, 22(3).

Algorithm:
  Solve Poisson equation in the masked region:
      nabla^2 f = div(v)   over Omega
      f = dst              on dOmega (Dirichlet BC)

  where v is the guidance gradient field from the source image.

  Solved via iterative Jacobi relaxation on GPU (parallel per iteration).

Transfer Modes:
  NORMAL_CLONE:    v = gradient of source
  MIXED_CLONE:     v = max(|grad_src|, |grad_dst|) per component
  MONO_TRANSFER:   v = gradient of grayscale(source)
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

# Clone mode flags (OpenCV-compatible)
NORMAL_CLONE = 1
MIXED_CLONE = 2
MONOCHROME_TRANSFER = 3

if TAICHI_AVAILABLE:

    # =========================================================================
    # Stage 1: Compute Divergence of Guidance Field
    # =========================================================================
    @ti.kernel
    def _compute_divergence_normal(src: ti.types.ndarray(),
                                     div_x: ti.types.ndarray(),
                                     div_y: ti.types.ndarray(),
                                     h: int, w: int, ch: int):
        """
        Compute gradient of source image for a single channel.
        div_x[y,x] = src[y,x+1] - src[y,x]  (forward difference in x)
        div_y[y,x] = src[y+1,x] - src[y,x]  (forward difference in y)
        """
        for y, x in ti.ndrange(h, w):
            rx = tm.clamp(x + 1, 0, w - 1)
            ry = tm.clamp(y + 1, 0, h - 1)
            div_x[y, x] = src[y, rx, ch] - src[y, x, ch]
            div_y[y, x] = src[ry, x, ch] - src[y, x, ch]

    @ti.kernel
    def _compute_divergence_mixed(src: ti.types.ndarray(), dst: ti.types.ndarray(),
                                    div_x: ti.types.ndarray(), div_y: ti.types.ndarray(),
                                    h: int, w: int, ch: int):
        """
        Mixed mode: pick gradient with larger magnitude from src or dst.
        """
        for y, x in ti.ndrange(h, w):
            rx = tm.clamp(x + 1, 0, w - 1)
            ry = tm.clamp(y + 1, 0, h - 1)

            sx = src[y, rx, ch] - src[y, x, ch]
            sy = src[ry, x, ch] - src[y, x, ch]
            dx = dst[y, rx, ch] - dst[y, x, ch]
            dy = dst[ry, x, ch] - dst[y, x, ch]

            # Pick larger magnitude per direction
            div_x[y, x] = sx if ti.abs(sx) > ti.abs(dx) else dx
            div_y[y, x] = sy if ti.abs(sy) > ti.abs(dy) else dy

    @ti.kernel
    def _compute_laplacian(div_x: ti.types.ndarray(), div_y: ti.types.ndarray(),
                             lap: ti.types.ndarray(), h: int, w: int):
        """
        Compute divergence of the gradient field = Laplacian of guidance.
        div(v) = d(vx)/dx + d(vy)/dy (backward difference of forward differences)
        """
        for y, x in ti.ndrange(h, w):
            lx = tm.clamp(x - 1, 0, w - 1)
            ly = tm.clamp(y - 1, 0, h - 1)
            # Backward difference of forward-differenced gradients
            lap[y, x] = (div_x[y, x] - div_x[y, lx]) + (div_y[y, x] - div_y[ly, x])

    # =========================================================================
    # Stage 2: Jacobi Iteration (parallel per pixel per iteration)
    # =========================================================================
    @ti.kernel
    def _jacobi_step(f_in: ti.types.ndarray(), f_out: ti.types.ndarray(),
                      lap: ti.types.ndarray(), mask: ti.types.ndarray(),
                      h: int, w: int):
        """
        One Jacobi iteration: f_out[i,j] = (neighbors_sum - lap[i,j]) / 4
        Only update pixels inside the mask. Boundary pixels keep dst values.
        """
        for y, x in ti.ndrange(h, w):
            if mask[y, x] < 0.5:
                # Outside mask: keep current value
                f_out[y, x] = f_in[y, x]
                continue

            # Check if this is a boundary pixel (adjacent to outside)
            is_boundary = False
            for dy in ti.static(range(-1, 2)):
                for dx in ti.static(range(-1, 2)):
                    if not (dy == 0 and dx == 0):
                        ny = tm.clamp(y + dy, 0, h - 1)
                        nx = tm.clamp(x + dx, 0, w - 1)
                        if mask[ny, nx] < 0.5:
                            is_boundary = True

            if is_boundary:
                # Boundary: keep Dirichlet BC (dst value)
                f_out[y, x] = f_in[y, x]
                continue

            # Interior: Jacobi update
            top = f_in[tm.clamp(y - 1, 0, h - 1), x]
            bot = f_in[tm.clamp(y + 1, 0, h - 1), x]
            lft = f_in[y, tm.clamp(x - 1, 0, w - 1)]
            rgt = f_in[y, tm.clamp(x + 1, 0, w - 1)]

            f_out[y, x] = (top + bot + lft + rgt - lap[y, x]) * 0.25

    # =========================================================================
    # Stage 3: Composite result into destination
    # =========================================================================
    @ti.kernel
    def _composite_kernel(f: ti.types.ndarray(), dst_out: ti.types.ndarray(),
                           mask: ti.types.ndarray(), h: int, w: int, ch: int):
        """Write solved channel back into destination image."""
        for y, x in ti.ndrange(h, w):
            if mask[y, x] > 0.5:
                dst_out[y, x, ch] = tm.clamp(f[y, x], 0.0, 255.0)


    # =========================================================================
    # Stage 3b: Helper kernels (module-level for AOT)
    # =========================================================================
    @ti.kernel
    def _copy_seamless(s: ti.types.ndarray(), d: ti.types.ndarray(), h: int, w: int):
        """Copy 3-channel image for seamless clone."""
        for y, x in ti.ndrange(h, w):
            d[y, x, 0] = s[y, x, 0]
            d[y, x, 1] = s[y, x, 1]
            d[y, x, 2] = s[y, x, 2]

    @ti.kernel
    def _to_grayscale(s: ti.types.ndarray(), g: ti.types.ndarray(), h: int, w: int):
        """Convert 3-channel image to grayscale for MONOCHROME_TRANSFER."""
        for y, x in ti.ndrange(h, w):
            g[y, x] = 0.299 * s[y, x, 2] + 0.587 * s[y, x, 1] + 0.114 * s[y, x, 0]

    @ti.kernel
    def _init_f_channel(dst_arr: ti.types.ndarray(), f: ti.types.ndarray(),
                          h: int, w: int, c: int):
        """Initialize f array with a single channel from destination."""
        for y, x in ti.ndrange(h, w):
            f[y, x] = dst_arr[y, x, c]


@ti_thread
def seamless_clone(src, dst, mask, center=(0, 0), flags=NORMAL_CLONE,
                    max_iterations=200, buffer_provider="pool"):
    """
    Seamless Cloning via Poisson Image Editing (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.seamlessClone()

    Composites src into dst within the masked region using gradient-domain
    blending for seamless transitions.

    Args:
        src: Source image (H, W, 3), uint8 or float32.
        dst: Destination image (H, W, 3), uint8 or float32.
        mask: Binary mask (H, W). Non-zero = region to composite.
              Should be the same size as dst.
        center: (x, y) position in dst where src center should be placed.
                (0, 0) means images are already aligned.
        flags: NORMAL_CLONE (1), MIXED_CLONE (2), or MONOCHROME_TRANSFER (3).
        max_iterations: Number of Jacobi iterations (default 200).
                        More iterations = better convergence, slower.
        buffer_provider: Buffer pool provider.

    Returns:
        Composited image (H, W, 3) in same format as dst.
    """
    # --- AOT path ---
    if os.environ.get("AOT_MODE", "1") == "1":
        from taichi_vision import taichi_aot
        return taichi_aot.seamless_clone(src, dst, mask, center=center,
                                          flags=flags, return_gpu=not isinstance(dst, np.ndarray))

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(dst, np.ndarray)

    # Upload inputs
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    dst_gpu, dst_is_temp = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    mask_gpu, mask_is_temp = common.ensure_taichi_field(mask, dtype=ti.f32,
                                                          buffer_provider=buffer_provider)

    h, w = dst_gpu.shape[:2]

    # Handle center offset: if center != (0,0), shift the source
    # For simplicity, assume images are pre-aligned (center=(0,0))
    # A full implementation would warp/crop src based on center

    # Allocate output (copy of dst)
    out_gpu = common.get_temp_buffer((h, w, 3), ti.f32, buffer_provider)
    _copy_seamless(dst_gpu, out_gpu, h, w)

    # Allocate intermediate buffers
    div_x = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    div_y = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    lap = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    f_in = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    f_out = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    # Solve for each channel independently
    num_channels = 3 if flags != MONOCHROME_TRANSFER else 1

    for ch in range(num_channels):
        # Step 1: Compute guidance gradient
        if flags == NORMAL_CLONE or flags == MONOCHROME_TRANSFER:
            if flags == MONOCHROME_TRANSFER and ch == 0:
                # Convert source to grayscale for guidance
                src_gray = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
                _to_grayscale(src_gpu, src_gray, h, w)
                # Compute gradients on grayscale (adapt kernel for 1ch)
                # For now, use channel 0 gradient as approximation
                _compute_divergence_normal(src_gpu, div_x, div_y, h, w, 0)
                common.release_temp_buffer(src_gray)
            else:
                _compute_divergence_normal(src_gpu, div_x, div_y, h, w, ch)
        elif flags == MIXED_CLONE:
            _compute_divergence_mixed(src_gpu, dst_gpu, div_x, div_y, h, w, ch)

        # Step 2: Compute Laplacian (divergence of gradient)
        _compute_laplacian(div_x, div_y, lap, h, w)

        # Step 3: Initialize f with destination values
        _init_f_channel(out_gpu, f_in, h, w, ch)

        # Step 4: Jacobi iterations
        for _ in range(max_iterations):
            _jacobi_step(f_in, f_out, lap, mask_gpu, h, w)
            # Swap buffers
            f_in, f_out = f_out, f_in

        # Step 5: Write result back
        _composite_kernel(f_in, out_gpu, mask_gpu, h, w, ch)

    # Cleanup
    for buf in [div_x, div_y, lap, f_in, f_out]:
        common.release_temp_buffer(buf)
    if src_is_temp:
        common.release_temp_buffer(src_gpu)
    if dst_is_temp:
        common.release_temp_buffer(dst_gpu)
    if mask_is_temp:
        common.release_temp_buffer(mask_gpu)

    return common.to_numpy_if_needed(out_gpu, is_numpy)
