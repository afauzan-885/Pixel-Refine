"""
Warp - Taichi GPU Implementation
================================
GPU-accelerated image warping using optical flow.
Features:
- Bicubic Interpolation (Catmull-Rom) for high precision.
- Joint Bilateral Flow Refinement (Guidance) to align flow with reference edges.
- Reflection Padding.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common, bicubic_interpolation

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None
    common = None
    bicubic_interpolation = None

if TAICHI_AVAILABLE:

    @ti.func
    def reflect_idx(idx: int, size: int) -> int:
        """Branchless BORDER_REFLECT_101 implementation."""
        res = idx
        if res < 0:
            res = -res
        if res >= size:
            res = 2 * (size - 1) - res
        return tm.clamp(res, 0, size - 1)

    @ti.func
    def sample_bicubic(
        img: ti.types.ndarray(ndim=2), u: float, v: float, h: int, w: int
    ) -> float:
        """Sample single-channel image with Bicubic interpolation using cubic_hermite."""
        x0 = int(ti.floor(u))
        y0 = int(ti.floor(v))
        dx = u - float(x0)
        dy = v - float(y0)

        col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])

        for m in range(-1, 3):  # y offset
            p = ti.Vector([0.0, 0.0, 0.0, 0.0])
            y_idx = reflect_idx(y0 + m, h)

            for n in range(-1, 3):  # x offset
                x_idx = reflect_idx(x0 + n, w)
                p[n + 1] = img[y_idx, x_idx]

            # Use user's existing cubic_hermite function
            col_results[m + 1] = bicubic_interpolation.cubic_hermite(
                p[0], p[1], p[2], p[3], dx
            )

        return bicubic_interpolation.cubic_hermite(
            col_results[0], col_results[1], col_results[2], col_results[3], dy
        )

    @ti.func
    def sample_bicubic_3ch(
        img: ti.types.ndarray(ndim=3), u: float, v: float, h: int, w: int, c: int
    ) -> float:
        """Sample specific channel of 3-channel image with Bicubic interpolation."""
        x0 = int(ti.floor(u))
        y0 = int(ti.floor(v))
        dx = u - float(x0)
        dy = v - float(y0)

        col_results = ti.Vector([0.0, 0.0, 0.0, 0.0])

        for m in range(-1, 3):
            p = ti.Vector([0.0, 0.0, 0.0, 0.0])
            y_idx = reflect_idx(y0 + m, h)
            for n in range(-1, 3):
                x_idx = reflect_idx(x0 + n, w)
                p[n + 1] = img[y_idx, x_idx, c]

            col_results[m + 1] = bicubic_interpolation.cubic_hermite(
                p[0], p[1], p[2], p[3], dx
            )

        return bicubic_interpolation.cubic_hermite(
            col_results[0], col_results[1], col_results[2], col_results[3], dy
        )

    @ti.kernel
    def _warp_kernel_guided(
        src: ti.types.ndarray(dtype=ti.f32, ndim=2),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=2),
        ref: ti.types.ndarray(dtype=ti.f32, ndim=2),  # Guidance Image
        h: int,
        w: int,
        use_guidance: int,
    ):
        for y, x in ti.ndrange(h, w):
            # Joint Bilateral Upsampling for Flow
            # We smooth the flow based on the Reference Image structure
            # to align flow boundaries with object boundaries.

            u_final, v_final = 0.0, 0.0

            if use_guidance:
                # 3x3 Window weighted by Reference intensity difference
                total_w = 0.0
                sum_u = 0.0
                sum_v = 0.0

                center_val = ref[y, x]

                # Small window sufficient for local refinement
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            # Spatial weight (simple box/gaussian)
                            w_s = 1.0  # Box is fine for 3x3

                            # Range weight (intensity difference)
                            # sigma_r approx 0.1 for 0-1 range
                            diff = ti.abs(ref[ny, nx] - center_val)
                            w_r = ti.exp(-(diff * diff) / 0.01)  # sigma_r = 0.1

                            w_curr = w_s * w_r

                            sum_u += flow[ny, nx, 0] * w_curr
                            sum_v += flow[ny, nx, 1] * w_curr
                            total_w += w_curr

                if total_w > 0:
                    u_final = x + sum_u / total_w
                    v_final = y + sum_v / total_w
                else:
                    u_final = x + flow[y, x, 0]
                    v_final = y + flow[y, x, 1]
            else:
                u_final = x + flow[y, x, 0]
                v_final = y + flow[y, x, 1]

            dst[y, x] = sample_bicubic(src, u_final, v_final, h, w)

    @ti.kernel
    def _warp_kernel_guided_3ch(
        src: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=3),
        dst: ti.types.ndarray(dtype=ti.f32, ndim=3),
        ref: ti.types.ndarray(dtype=ti.f32, ndim=2),  # Guidance (Grayscale)
        h: int,
        w: int,
        use_guidance: int,
    ):
        for y, x in ti.ndrange(h, w):
            u_final, v_final = 0.0, 0.0

            if use_guidance:
                total_w = 0.0
                sum_u = 0.0
                sum_v = 0.0
                center_val = ref[y, x]  # Ref is usually single channel intensity

                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w:
                            diff = ti.abs(ref[ny, nx] - center_val)
                            w_r = ti.exp(-(diff * diff) / 0.01)
                            sum_u += flow[ny, nx, 0] * w_r
                            sum_v += flow[ny, nx, 1] * w_r
                            total_w += w_r

                if total_w > 0:
                    u_final = x + sum_u / total_w
                    v_final = y + sum_v / total_w
                else:
                    u_final = x + flow[y, x, 0]
                    v_final = y + flow[y, x, 1]
            else:
                u_final = x + flow[y, x, 0]
                v_final = y + flow[y, x, 1]

            for c in ti.static(range(3)):
                dst[y, x, c] = sample_bicubic_3ch(src, u_final, v_final, h, w, c)

    def warp_image_gpu(
        src, flow, dst=None, buffer_provider="pool", enable_tiling=True, guidance=None
    ):
        """
        Warp image using optical flow on GPU with Bicubic Interpolation and
        Optional Joint Bilateral Flow Refinement (if guidance image is provided).

        Args:
            guidance: Optional single-channel reference image (H, W).
                     If provided, flow is smoothed respecting guidance edges.
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        h, w = src.shape[:2]

        src_gpu, src_is_temp = common.ensure_taichi_field(
            src, dtype=ti.f32, buffer_provider=buffer_provider
        )
        flow_gpu, flow_is_temp = common.ensure_taichi_field(
            flow, dtype=ti.f32, buffer_provider=buffer_provider
        )

        use_guidance = 0
        guidance_gpu = None
        guidance_is_temp = False

        if guidance is not None:
            use_guidance = 1
            guidance_gpu, guidance_is_temp = common.ensure_taichi_field(
                guidance, dtype=ti.f32, buffer_provider=buffer_provider
            )
        else:
            # Create a dummy 1x1 buffer to satisfy kernel signature (Taichi requirement)
            # Won't be accessed if use_guidance=0
            guidance_gpu = common.get_temp_buffer((1, 1), ti.f32, buffer_provider)
            guidance_is_temp = True

        channels = 1 if len(src_gpu.shape) == 2 else src_gpu.shape[2]

        if dst is None:
            shape = (h, w) if channels == 1 else (h, w, 3)
            dst_gpu = common.get_temp_buffer(shape, ti.f32, buffer_provider)
        else:
            dst_gpu = dst

        if channels == 1:
            _warp_kernel_guided(
                src_gpu, flow_gpu, dst_gpu, guidance_gpu, h, w, use_guidance
            )
        else:
            _warp_kernel_guided_3ch(
                src_gpu, flow_gpu, dst_gpu, guidance_gpu, h, w, use_guidance
            )

        # Cleanup
        if src_is_temp:
            common.release_temp_buffer(src_gpu)
        if flow_is_temp:
            common.release_temp_buffer(flow_gpu)
        if guidance_is_temp:
            common.release_temp_buffer(guidance_gpu)

        res = common.to_numpy_if_needed(dst_gpu, dst is None)
        if dst is None:
            common.release_temp_buffer(dst_gpu)

        return res

else:

    def warp_image_gpu(
        src, flow, dst=None, buffer_provider="pool", enable_tiling=True, guidance=None
    ):
        raise ImportError("Taichi not available")
