"""Remap (Image Warping) - Taichi GPU"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from ..taichi_worker import ti_thread
except ImportError:
    pass

if TAICHI_AVAILABLE:
    from ..common import bilinear_at, bilinear_at_3ch, bilinear_at_vec3

    @ti.kernel
    def _smooth_flow_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        """Separable Gaussian blur pass for a 2-channel flow field (H, W, 2).

        Processes both channels in a single kernel to avoid repeated kernel launches.
        Used for X-pass and Y-pass separately (call twice: x-pass then y-pass).
        This is the X-pass variant: blurs along the column axis.
        """
        for r, c, ch in ti.ndrange(h, w, 2):
            acc = 0.0
            w_sum = 0.0
            for k in range(-radius, radius + 1):
                cc = ti.min(ti.max(c + k, 0), w - 1)
                wk = weights[k + radius]
                acc += src[r, cc, ch] * wk
                w_sum += wk
            dst[r, c, ch] = acc / (w_sum + 1e-12)

    @ti.kernel
    def _smooth_flow_y_kernel(
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h: int,
        w: int,
        weights: ti.types.ndarray(),
        radius: int,
    ):
        """Y-pass Gaussian blur for 2-channel flow field (H, W, 2)."""
        for r, c, ch in ti.ndrange(h, w, 2):
            acc = 0.0
            w_sum = 0.0
            for k in range(-radius, radius + 1):
                rr = ti.min(ti.max(r + k, 0), h - 1)
                wk = weights[k + radius]
                acc += src[rr, c, ch] * wk
                w_sum += wk
            dst[r, c, ch] = acc / (w_sum + 1e-12)

    @ti.kernel
    def _build_flow_maps_from_2ch_kernel(
        flow: ti.types.ndarray(),
        map_x: ti.types.ndarray(),
        map_y: ti.types.ndarray(),
        h_flow: int,
        w_flow: int,
        h_dst: int,
        w_dst: int,
        scale_x: float,
        scale_y: float,
    ):
        """Build map_x and map_y from a smoothed 2-channel flow field (H_flow, W_flow, 2).

        Combines bilinear upsampling, scale, and identity grid offset in one pass.
        Avoids extracting individual channels from the flow field.

        Channel 0 = dx (horizontal displacement)
        Channel 1 = dy (vertical displacement)
        """
        for r, c in ti.ndrange(h_dst, w_dst):
            # Map full-res pixel to flow-space coordinates
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)

            # Bilinear sample each channel from the 3D flow tensor
            sampled_dx = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 0)
            sampled_dy = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 1)

            map_x[r, c] = float(c) + sampled_dx * scale_x
            map_y[r, c] = float(r) + sampled_dy * scale_y

    @ti.kernel
    def _build_flow_maps_kernel(
        dx: ti.types.ndarray(),
        dy: ti.types.ndarray(),
        map_x: ti.types.ndarray(),
        map_y: ti.types.ndarray(),
        h_flow: int,
        w_flow: int,
        h_dst: int,
        w_dst: int,
        scale_x: float,
        scale_y: float,
    ):
        """Build map_x and map_y from separate low-res dx/dy flow channels (2D each).

        Performs bilinear upsample of the flow field to (h_dst, w_dst),
        scales the displacement vectors, and adds the identity grid
        (pixel coordinates) — all in a single GPU pass.
        """
        for r, c in ti.ndrange(h_dst, w_dst):
            # Normalized flow coordinates (maps full-res pixel to flow space)
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)

            # Bilinear sample the low-res flow
            sampled_dx = bilinear_at(dx, fx, fy, h_flow, w_flow)
            sampled_dy = bilinear_at(dy, fx, fy, h_flow, w_flow)

            # Scale and add identity grid offset
            map_x[r, c] = float(c) + sampled_dx * scale_x
            map_y[r, c] = float(r) + sampled_dy * scale_y

    @ti.kernel
    def _remap_kernel(
        src: ti.types.ndarray(),
        map_x: ti.types.ndarray(),
        map_y: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            dst[r, c] = bilinear_at(src, map_x[r, c], map_y[r, c], h_src, w_src)

    @ti.kernel
    def _remap_kernel_3d(
        src: ti.types.ndarray(),
        map_x: ti.types.ndarray(),
        map_y: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c, ch in ti.ndrange(h_dst, w_dst, dst.shape[2]):
            dst[r, c, ch] = bilinear_at_3ch(
                src, map_x[r, c], map_y[r, c], h_src, w_src, ch
            )

    @ti.kernel
    def _remap_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        map_x: ti.types.ndarray(),
        map_y: ti.types.ndarray(),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            dst[r, c] = bilinear_at_vec3(src, map_x[r, c], map_y[r, c], h_src, w_src)

    @ti.kernel
    def _remap_with_flow_kernel(
        src: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
        h_flow: int,
        w_flow: int,
        scale_x: float,
        scale_y: float,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)
            sampled_dx = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 0)
            sampled_dy = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 1)
            src_x = float(c) + sampled_dx * scale_x
            src_y = float(r) + sampled_dy * scale_y
            dst[r, c] = bilinear_at(src, src_x, src_y, h_src, w_src)

    @ti.kernel
    def _remap_with_flow_kernel_vec3(
        src: ti.types.ndarray(),
        flow: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
        h_flow: int,
        w_flow: int,
        scale_x: float,
        scale_y: float,
    ):
        for r, c in ti.ndrange(h_dst, w_dst):
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)
            sampled_dx = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 0)
            sampled_dy = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 1)
            src_x = float(c) + sampled_dx * scale_x
            src_y = float(r) + sampled_dy * scale_y
            dst[r, c] = bilinear_at_vec3(src, src_x, src_y, h_src, w_src)

    @ti.kernel
    def _remap_with_flow_offset_kernel(
        src: ti.types.ndarray(), flow: ti.types.ndarray(), dst: ti.types.ndarray(),
        h_src: int, w_src: int, h_dst: int, w_dst: int,
        h_flow: int, w_flow: int, scale_x: float, scale_y: float,
        offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            fx = float(gc) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(gr) * float(h_flow - 1) / float(h_dst - 1)
            dx = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 0)
            dy = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 1)
            dst[r, c] = bilinear_at(
                src, float(gc) + dx * scale_x, float(gr) + dy * scale_y,
                h_src, w_src,
            )

    @ti.kernel
    def _remap_with_flow_offset_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        flow: ti.types.ndarray(),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int, w_src: int, h_dst: int, w_dst: int,
        h_flow: int, w_flow: int, scale_x: float, scale_y: float,
        offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            fx = float(gc) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(gr) * float(h_flow - 1) / float(h_dst - 1)
            dx = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 0)
            dy = bilinear_at_3ch(flow, fx, fy, h_flow, w_flow, 1)
            dst[r, c] = bilinear_at_vec3(
                src, float(gc) + dx * scale_x, float(gr) + dy * scale_y,
                h_src, w_src,
            )

    @ti.kernel
    def _remap_with_flow_batch_kernel(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        n_items: ti.i32,
        h_src: ti.i32,
        w_src: ti.i32,
        h_dst: ti.i32,
        w_dst: ti.i32,
        h_flow: ti.i32,
        w_flow: ti.i32,
        scale_x: ti.f32,
        scale_y: ti.f32,
    ):
        for n, r, c in ti.ndrange(n_items, h_dst, w_dst):
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)
            x0 = int(ti.floor(fx))
            y0 = int(ti.floor(fy))
            x1 = ti.min(x0 + 1, w_flow - 1)
            y1 = ti.min(y0 + 1, h_flow - 1)
            wx = fx - float(x0)
            wy = fy - float(y0)
            dx00 = flow[n, y0, x0, 0]
            dx01 = flow[n, y0, x1, 0]
            dx10 = flow[n, y1, x0, 0]
            dx11 = flow[n, y1, x1, 0]
            dy00 = flow[n, y0, x0, 1]
            dy01 = flow[n, y0, x1, 1]
            dy10 = flow[n, y1, x0, 1]
            dy11 = flow[n, y1, x1, 1]
            sampled_dx = (dx00 * (1.0 - wx) + dx01 * wx) * (1.0 - wy) + (
                dx10 * (1.0 - wx) + dx11 * wx
            ) * wy
            sampled_dy = (dy00 * (1.0 - wx) + dy01 * wx) * (1.0 - wy) + (
                dy10 * (1.0 - wx) + dy11 * wx
            ) * wy
            src_x = float(c) + sampled_dx * scale_x
            src_y = float(r) + sampled_dy * scale_y
            sx0 = int(ti.floor(src_x))
            sy0 = int(ti.floor(src_y))
            frac_x = src_x - float(sx0)
            frac_y = src_y - float(sy0)
            sx0 = ti.min(ti.max(sx0, 0), w_src - 1)
            sy0 = ti.min(ti.max(sy0, 0), h_src - 1)
            sx1 = ti.min(sx0 + 1, w_src - 1)
            sy1 = ti.min(sy0 + 1, h_src - 1)
            v00 = src[n, sy0, sx0]
            v01 = src[n, sy0, sx1]
            v10 = src[n, sy1, sx0]
            v11 = src[n, sy1, sx1]
            dst[n, r, c] = (v00 * (1.0 - frac_x) + v01 * frac_x) * (1.0 - frac_y) + (
                v10 * (1.0 - frac_x) + v11 * frac_x
            ) * frac_y

    @ti.kernel
    def _remap_with_flow_batch_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.f32, ndim=4),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=4),
        n_items: ti.i32,
        h_src: ti.i32,
        w_src: ti.i32,
        h_dst: ti.i32,
        w_dst: ti.i32,
        h_flow: ti.i32,
        w_flow: ti.i32,
        scale_x: ti.f32,
        scale_y: ti.f32,
    ):
        for n, r, c, ch in ti.ndrange(n_items, h_dst, w_dst, 3):
            fx = float(c) * float(w_flow - 1) / float(w_dst - 1)
            fy = float(r) * float(h_flow - 1) / float(h_dst - 1)
            x0 = int(ti.floor(fx))
            y0 = int(ti.floor(fy))
            x1 = ti.min(x0 + 1, w_flow - 1)
            y1 = ti.min(y0 + 1, h_flow - 1)
            wx = fx - float(x0)
            wy = fy - float(y0)
            dx00 = flow[n, y0, x0, 0]
            dx01 = flow[n, y0, x1, 0]
            dx10 = flow[n, y1, x0, 0]
            dx11 = flow[n, y1, x1, 0]
            dy00 = flow[n, y0, x0, 1]
            dy01 = flow[n, y0, x1, 1]
            dy10 = flow[n, y1, x0, 1]
            dy11 = flow[n, y1, x1, 1]
            sampled_dx = (dx00 * (1.0 - wx) + dx01 * wx) * (1.0 - wy) + (
                dx10 * (1.0 - wx) + dx11 * wx
            ) * wy
            sampled_dy = (dy00 * (1.0 - wx) + dy01 * wx) * (1.0 - wy) + (
                dy10 * (1.0 - wx) + dy11 * wx
            ) * wy
            src_x = float(c) + sampled_dx * scale_x
            src_y = float(r) + sampled_dy * scale_y
            sx0 = int(ti.floor(src_x))
            sy0 = int(ti.floor(src_y))
            frac_x = src_x - float(sx0)
            frac_y = src_y - float(sy0)
            sx0 = ti.min(ti.max(sx0, 0), w_src - 1)
            sy0 = ti.min(ti.max(sy0, 0), h_src - 1)
            sx1 = ti.min(sx0 + 1, w_src - 1)
            sy1 = ti.min(sy0 + 1, h_src - 1)
            v00 = src[n, sy0, sx0, ch]
            v01 = src[n, sy0, sx1, ch]
            v10 = src[n, sy1, sx0, ch]
            v11 = src[n, sy1, sx1, ch]
            dst[n, r, c, ch] = (v00 * (1.0 - frac_x) + v01 * frac_x) * (
                1.0 - frac_y
            ) + (v10 * (1.0 - frac_x) + v11 * frac_x) * frac_y

    @ti.kernel
    def _warp_perspective_kernel(
        src: ti.types.ndarray(),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        """Warp Perspective Bilinear untuk gambar Grayscale (2D)."""
        for r, c in ti.ndrange(h_dst, w_dst):
            # Proyeksi homogen menggunakan matriks invers M_inv (3x3)
            u = M_inv[0, 0] * float(c) + M_inv[0, 1] * float(r) + M_inv[0, 2]
            v = M_inv[1, 0] * float(c) + M_inv[1, 1] * float(r) + M_inv[1, 2]
            w = M_inv[2, 0] * float(c) + M_inv[2, 1] * float(r) + M_inv[2, 2]

            src_x = u / (w + 1e-9)
            src_y = v / (w + 1e-9)

            dst[r, c] = bilinear_at(src, src_x, src_y, h_src, w_src)

    @ti.kernel
    def _warp_perspective_kernel_3d(
        src: ti.types.ndarray(),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        """Warp Perspective Bilinear untuk gambar Multi-channel (3D)."""
        for r, c, ch in ti.ndrange(h_dst, w_dst, dst.shape[2]):
            u = M_inv[0, 0] * float(c) + M_inv[0, 1] * float(r) + M_inv[0, 2]
            v = M_inv[1, 0] * float(c) + M_inv[1, 1] * float(r) + M_inv[1, 2]
            w = M_inv[2, 0] * float(c) + M_inv[2, 1] * float(r) + M_inv[2, 2]

            src_x = u / (w + 1e-9)
            src_y = v / (w + 1e-9)

            dst[r, c, ch] = bilinear_at_3ch(src, src_x, src_y, h_src, w_src, ch)

    @ti.kernel
    def _warp_perspective_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int,
        w_src: int,
        h_dst: int,
        w_dst: int,
    ):
        """Warp Perspective Bilinear untuk gambar Vector3 (3D)."""
        for r, c in ti.ndrange(h_dst, w_dst):
            u = M_inv[0, 0] * float(c) + M_inv[0, 1] * float(r) + M_inv[0, 2]
            v = M_inv[1, 0] * float(c) + M_inv[1, 1] * float(r) + M_inv[1, 2]
            w = M_inv[2, 0] * float(c) + M_inv[2, 1] * float(r) + M_inv[2, 2]

            src_x = u / (w + 1e-9)
            src_y = v / (w + 1e-9)

            dst[r, c] = bilinear_at_vec3(src, src_x, src_y, h_src, w_src)

    @ti.kernel
    def _warp_perspective_offset_kernel(
        src: ti.types.ndarray(), M_inv: ti.types.ndarray(), dst: ti.types.ndarray(),
        h_src: int, w_src: int, offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            u = M_inv[0, 0] * float(gc) + M_inv[0, 1] * float(gr) + M_inv[0, 2]
            v = M_inv[1, 0] * float(gc) + M_inv[1, 1] * float(gr) + M_inv[1, 2]
            z = M_inv[2, 0] * float(gc) + M_inv[2, 1] * float(gr) + M_inv[2, 2]
            dst[r, c] = bilinear_at(src, u / (z + 1e-9), v / (z + 1e-9), h_src, w_src)

    @ti.kernel
    def _warp_perspective_offset_kernel_vec3(
        src: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        M_inv: ti.types.ndarray(),
        dst: ti.types.ndarray(dtype=ti.types.vector(3, ti.f32), ndim=2),
        h_src: int, w_src: int, offset_y: int, offset_x: int,
    ):
        for r, c in ti.ndrange(dst.shape[0], dst.shape[1]):
            gr, gc = r + offset_y, c + offset_x
            u = M_inv[0, 0] * float(gc) + M_inv[0, 1] * float(gr) + M_inv[0, 2]
            v = M_inv[1, 0] * float(gc) + M_inv[1, 1] * float(gr) + M_inv[1, 2]
            z = M_inv[2, 0] * float(gc) + M_inv[2, 1] * float(gr) + M_inv[2, 2]
            dst[r, c] = bilinear_at_vec3(src, u / (z + 1e-9), v / (z + 1e-9), h_src, w_src)


def remap(src, map_x, map_y, dst=None, buffer_provider="pool"):
    """
    GPU-accelerated Remap (Warping) API.
    Interpolates input src using coordinate maps map_x and map_y.

    All Taichi operations are synchronized via @ti_thread.

    Args:
        src: Input image - can be NumPy array OR Taichi ndarray. (H, W) or (H, W, C)
        map_x: Coordinate map for X coordinates - NumPy array OR Taichi ndarray. (H_dst, W_dst)
        map_y: Coordinate map for Y coordinates - NumPy array OR Taichi ndarray. (H_dst, W_dst)
        dst: Optional pre-allocated output buffer.
        buffer_provider: Optional buffer pool provider ("pool" or None).

    Returns:
        Warped image in the same format as input (NumPy or Taichi).
    """
    import os

    if os.environ.get("AOT_MODE", "1") == "1":
        from ..common import _get_aot

        aot = _get_aot()
        if aot and hasattr(aot, "remap"):
            is_taichi = (
                hasattr(src, "to_numpy")
                or hasattr(map_x, "to_numpy")
                or hasattr(map_y, "to_numpy")
            )
            res_buf = aot.remap(src, map_x, map_y, return_gpu=is_taichi)
            if dst is not None:
                if is_taichi:
                    from ..common import copy_field

                    copy_field(res_buf, dst)
                else:
                    dst[:] = res_buf
                return dst
            return res_buf

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from ..common import get_temp_buffer, release_temp_buffer, ensure_taichi_field

    is_taichi_input = (
        hasattr(src, "to_numpy")
        or hasattr(map_x, "to_numpy")
        or hasattr(map_y, "to_numpy")
    )

    @ti_thread
    def _run_gpu_remap(src_data, mx_data, my_data, dst_data=None):
        src_gpu, src_is_temp = ensure_taichi_field(
            src_data, dtype=ti.f32, buffer_provider=buffer_provider
        )
        mx_gpu, mx_is_temp = ensure_taichi_field(
            mx_data, dtype=ti.f32, buffer_provider=buffer_provider
        )
        my_gpu, my_is_temp = ensure_taichi_field(
            my_data, dtype=ti.f32, buffer_provider=buffer_provider
        )

        h_src, w_src = src_gpu.shape[:2]
        h_dst, w_dst = mx_gpu.shape[:2]
        is_3d = len(src_gpu.shape) == 3
        c_count = src_gpu.shape[2] if is_3d else 1

        # Determine output buffer
        if dst_data is None:
            out_shape = (h_dst, w_dst, c_count) if is_3d else (h_dst, w_dst)
            dst_gpu = get_temp_buffer(out_shape, ti.f32, buffer_provider)
        else:
            dst_gpu, _ = ensure_taichi_field(
                dst_data, dtype=ti.f32, buffer_provider=buffer_provider
            )

        # Run kernel
        if is_3d:
            _remap_kernel_3d(
                src_gpu, mx_gpu, my_gpu, dst_gpu, h_src, w_src, h_dst, w_dst
            )
        else:
            _remap_kernel(src_gpu, mx_gpu, my_gpu, dst_gpu, h_src, w_src, h_dst, w_dst)

        # Cleanup temps
        if src_is_temp:
            release_temp_buffer(src_gpu)
        if mx_is_temp:
            release_temp_buffer(mx_gpu)
        if my_is_temp:
            release_temp_buffer(my_gpu)

        # Download if input was NumPy
        if not is_taichi_input:
            res = dst_gpu.to_numpy()
            release_temp_buffer(dst_gpu)
            if dst_data is not None:
                dst_data[:] = res
                return dst_data
            return res

        return dst_gpu

    return _run_gpu_remap(src, map_x, map_y, dst)


def remap_with_flow(src, flow, full_h, full_w, dst=None, buffer_provider="pool"):
    """
    Fused GPU-accelerated Remap with Flow API.
    Interpolates input src using 2-channel flow field, on-the-fly interpolating flow.

    All Taichi operations are synchronized via @ti_thread.
    """
    import os

    if os.environ.get("AOT_MODE", "1") == "1":
        from ..common import _get_aot

        aot = _get_aot()
        if aot and hasattr(aot, "remap_with_flow"):
            is_taichi = hasattr(src, "to_numpy") or hasattr(flow, "to_numpy")
            res_buf = aot.remap_with_flow(
                src, flow, full_h, full_w, return_gpu=is_taichi, dst=dst
            )
            return res_buf

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from ..common import get_temp_buffer, release_temp_buffer, ensure_taichi_field

    is_taichi_input = hasattr(src, "to_numpy") or hasattr(flow, "to_numpy")

    @ti_thread
    def _run_gpu_remap_with_flow(src_data, flow_data, dst_data=None):
        src_gpu, src_is_temp = ensure_taichi_field(
            src_data, dtype=ti.f32, buffer_provider=buffer_provider
        )
        flow_gpu, flow_is_temp = ensure_taichi_field(
            flow_data, dtype=ti.f32, buffer_provider=buffer_provider
        )

        h_src, w_src = src_gpu.shape[:2]
        h_flow, w_flow = flow_gpu.shape[:2]
        is_3d = len(src_gpu.shape) == 3
        c_count = src_gpu.shape[2] if is_3d else 1

        scale_x = float(full_w) / float(w_flow)
        scale_y = float(full_h) / float(h_flow)

        # Determine output buffer
        if dst_data is None:
            out_shape = (full_h, full_w, c_count) if is_3d else (full_h, full_w)
            dst_gpu = get_temp_buffer(out_shape, ti.f32, buffer_provider)
        else:
            dst_gpu, _ = ensure_taichi_field(
                dst_data, dtype=ti.f32, buffer_provider=buffer_provider
            )

        # Run kernel
        if is_3d:
            _remap_with_flow_kernel_vec3(
                src_gpu,
                flow_gpu,
                dst_gpu,
                h_src,
                w_src,
                full_h,
                full_w,
                h_flow,
                w_flow,
                scale_x,
                scale_y,
            )
        else:
            _remap_with_flow_kernel(
                src_gpu,
                flow_gpu,
                dst_gpu,
                h_src,
                w_src,
                full_h,
                full_w,
                h_flow,
                w_flow,
                scale_x,
                scale_y,
            )

        # Cleanup temps
        if src_is_temp:
            release_temp_buffer(src_gpu)
        if flow_is_temp:
            release_temp_buffer(flow_gpu)

        # Download if input was NumPy
        if not is_taichi_input:
            res = dst_gpu.to_numpy()
            release_temp_buffer(dst_gpu)
            if dst_data is not None:
                dst_data[:] = res
                return dst_data
            return res

        return dst_gpu

    return _run_gpu_remap_with_flow(src, flow, dst)


def warp_perspective(src, M, dsize, dst=None, buffer_provider="pool"):
    """
    GPU-accelerated Warp Perspective API.
    API menyerupai cv2.warpPerspective(src, M, dsize).

    Menghitung inversi matriks transformasi M di CPU, kemudian memproyeksikan
    setiap piksel output kembali ke koordinat input secara on-the-fly di GPU.

    Args:
        src: NumPy array atau Taichi GPU buffer.
        M: Matriks homografi 3x3 (float32/float64).
        dsize: Tuple ukuran hasil warping (width, height).
        dst: Buffer output opsional.
    """
    import os

    if os.environ.get("AOT_MODE", "1") == "1":
        from ..common import _get_aot

        aot = _get_aot()
        if aot and hasattr(aot, "warp_perspective"):
            is_taichi = hasattr(src, "to_numpy") or hasattr(M, "to_numpy")
            res_buf = aot.warp_perspective(src, M, dsize, return_gpu=is_taichi, dst=dst)
            return res_buf

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    from ..common import get_temp_buffer, release_temp_buffer, ensure_taichi_field

    is_taichi_input = hasattr(src, "to_numpy")
    w_dst, h_dst = dsize

    # Hitung invers matriks homografi di CPU (M_inv = M^-1)
    M_np = np.asarray(M, dtype=np.float32)
    try:
        M_inv_np = np.linalg.inv(M_np)
    except np.linalg.LinAlgError:
        M_inv_np = np.eye(3, dtype=np.float32)

    @ti_thread
    def _run_gpu_warp(src_data, m_inv_data, dst_data=None):
        src_gpu, src_is_temp = ensure_taichi_field(
            src_data, dtype=ti.f32, buffer_provider=buffer_provider
        )
        # Upload matriks invers 3x3 ke GPU
        minv_gpu, minv_is_temp = ensure_taichi_field(
            m_inv_data, dtype=ti.f32, buffer_provider=buffer_provider
        )

        h_src, w_src = src_gpu.shape[:2]
        is_3d = len(src_gpu.shape) == 3
        c_count = src_gpu.shape[2] if is_3d else 1

        if dst_data is None:
            out_shape = (h_dst, w_dst, c_count) if is_3d else (h_dst, w_dst)
            dst_gpu = get_temp_buffer(out_shape, ti.f32, buffer_provider)
        else:
            dst_gpu, _ = ensure_taichi_field(
                dst_data, dtype=ti.f32, buffer_provider=buffer_provider
            )

        # Dispatch kernel yang sesuai
        if is_3d:
            _warp_perspective_kernel_3d(
                src_gpu, minv_gpu, dst_gpu, h_src, w_src, h_dst, w_dst
            )
        else:
            _warp_perspective_kernel(
                src_gpu, minv_gpu, dst_gpu, h_src, w_src, h_dst, w_dst
            )

        if src_is_temp:
            release_temp_buffer(src_gpu)
        if minv_is_temp:
            release_temp_buffer(minv_gpu)

        if not is_taichi_input:
            res = dst_gpu.to_numpy()
            release_temp_buffer(dst_gpu)
            if dst_data is not None:
                dst_data[:] = res
                return dst_data
            return res

        return dst_gpu

    return _run_gpu_warp(src, M_inv_np, dst)
