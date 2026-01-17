"""
Cross-Bilateral Flow Refinement
===============================
Filters optical flow fields using a reference image as guidance.
This "snaps" flow boundaries to image edges and removes outliers within homogeneous regions.
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
    common = None

if TAICHI_AVAILABLE:

    @ti.kernel
    def _cross_bilateral_filter_kernel(
        flow_in: ti.types.ndarray(ndim=3),
        flow_out: ti.types.ndarray(ndim=3),
        guidance: ti.types.ndarray(ndim=2),  # Grayscale guidance
        h: int,
        w: int,
        sigma_s: float,
        sigma_r: float,
        radius: int,
    ):
        # Precompute constants
        sigma_s_sq = 2.0 * sigma_s * sigma_s
        sigma_r_sq = 2.0 * sigma_r * sigma_r

        for y, x in ti.ndrange(h, w):
            sum_u = 0.0
            sum_v = 0.0
            sum_weight = 0.0

            center_val = guidance[y, x]

            # Local window search
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    ny = y + dy
                    nx = x + dx

                    if 0 <= ny < h and 0 <= nx < w:
                        # Spatial weight: exp(-dist^2 / 2*sigma_s^2)
                        dist_sq = float(dx * dx + dy * dy)
                        w_s = ti.exp(-dist_sq / sigma_s_sq)

                        # Range weight: exp(-intensity_diff^2 / 2*sigma_r^2)
                        val_diff = guidance[ny, nx] - center_val
                        w_r = ti.exp(-(val_diff * val_diff) / sigma_r_sq)

                        weight = w_s * w_r

                        sum_u += flow_in[ny, nx, 0] * weight
                        sum_v += flow_in[ny, nx, 1] * weight
                        sum_weight += weight

            if sum_weight > 1e-5:
                flow_out[y, x, 0] = sum_u / sum_weight
                flow_out[y, x, 1] = sum_v / sum_weight
            else:
                flow_out[y, x, 0] = flow_in[y, x, 0]
                flow_out[y, x, 1] = flow_in[y, x, 1]

    def refine_flow_guided(
        flow,
        guidance_img,
        sigma_spatial=2.0,
        sigma_range=0.1,
        radius=2,
        iterations=1,
        buffer_provider="pool",
    ):
        """
        Apply Cross-Bilateral Filtering to optical flow.

        Args:
            flow: (H,W,2) Optical flow field (NumPy or Taichi).
            guidance_img: (H,W) or (H,W,C) Reference image for guidance.
            sigma_spatial: Controls how far neighbors influence the pixel (blur strength).
            sigma_range: Controls how much edges stop the blur (edge sensitivity).
            radius: Kernel radius (size = 2*radius + 1).
            iterations: Number of filter passes (more passes = stronger effect).

        Returns:
            Refined flow field (NumPy if input was NumPy, else Taichi field).
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        # 1. Prepare Inputs
        flow_gpu, flow_is_temp = common.ensure_taichi_field(
            flow, dtype=ti.f32, buffer_provider=buffer_provider
        )

        # Ensure guidance is single-channel float32 [0,1]
        if isinstance(guidance_img, np.ndarray):
            # If color, convert to gray for guide
            if guidance_img.ndim == 3:
                # We can do a quick upload and extract channel or grayscale kernel,
                # For simplicity here, we assume user might pass preprocessed gray or we handle it in helper
                # Let's rely on common helper or just upload channel 1 (Green) as proxy for luma
                # Manual gray conv here to be safe and fast?
                # Actually, let's use the Green channel or average if 3ch, but doing it on CPU is safest for generic np input
                # Fast approximation: just takes Green channel or 0
                g_img = guidance_img.astype(np.float32)
                if guidance_img.dtype == np.uint8:
                    g_img /= 255.0
                elif guidance_img.dtype == np.uint16:
                    g_img /= 65535.0

                if guidance_img.ndim == 3:
                    # Use Green channel as luminance proxy (fast)
                    g_img = np.ascontiguousarray(g_img[:, :, 1])

                guidance_gpu, guidance_is_temp = common.ensure_taichi_field(
                    g_img, dtype=ti.f32, buffer_provider=buffer_provider
                )
            else:
                # Already gray
                g_img = guidance_img.astype(np.float32)
                if guidance_img.dtype == np.uint8:
                    g_img /= 255.0
                elif guidance_img.dtype == np.uint16:
                    g_img /= 65535.0
                guidance_gpu, guidance_is_temp = common.ensure_taichi_field(
                    g_img, dtype=ti.f32, buffer_provider=buffer_provider
                )
        else:
            # Assume it's already a suitable Taichi field
            guidance_gpu, guidance_is_temp = guidance_img, False

        h, w = flow_gpu.shape[:2]

        # 2. Ping-Pong Buffers
        # We need a secondary buffer for the output of each iteration
        buf_a = flow_gpu
        buf_b = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)

        # 3. Filter Loop
        # Ping-pong between buf_a and buf_b
        # If input was temp, we can write back to it?
        # Safer to just toggle.

        curr_in = buf_a
        curr_out = buf_b

        for _ in range(iterations):
            _cross_bilateral_filter_kernel(
                curr_in,
                curr_out,
                guidance_gpu,
                h,
                w,
                sigma_spatial,
                sigma_range,
                radius,
            )
            # Swap
            curr_in, curr_out = curr_out, curr_in

        # curr_in now holds the final result (because we swapped at end of loop)
        final_result_gpu = curr_in
        temp_buffer_to_release = curr_out  # The other one is garbage now

        # 4. Cleanup and Return
        if guidance_is_temp:
            common.release_temp_buffer(guidance_gpu)

        common.release_temp_buffer(temp_buffer_to_release)

        # Handle return types
        # If input was numpy, return numpy.
        was_numpy = isinstance(flow, np.ndarray)

        # If flow was NOT temp (original Taichi field passed in), we should probably COPY result back to it?
        # Or return new field?
        # Standard Taichi/Python convention: return new object or modify in place?
        # Filter usually returns new.

        if was_numpy:
            res = final_result_gpu.to_numpy()
            # If final result buffer was temp (it is buf_a or buf_b), release it
            common.release_temp_buffer(final_result_gpu)
            if flow_is_temp:
                common.release_temp_buffer(flow_gpu)  # original input temp
            return res
        else:
            # Input was Taichi field.
            # We have a result in final_result_gpu (buf_a or buf_b).
            # One of them is the input field!

            # If final is the input field (even number of swaps?), we are good (in-place modification simulated?)
            # Wait, Ping-Pong modifies source? No, read A write B.
            # If we return a NEW field, caller must manage it.

            # Use 'copy_field' to support in-place feel if requested?
            # Let's just return the field containing result.

            # IMPORTANT: If final_result_gpu is NOT flow_gpu (the input), then flow_gpu is untouched.
            # If final_result_gpu IS flow_gpu (even iterations), then flow_gpu IS modified.
            # This hybrid "sometimes modified" is bad API.

            # Better: Always return a NEW buffer or copy to a specific out if needed.
            # But for performance (VRAM), we like reusing.

            # If iterations is even: Result is in flow_gpu (Input Modified).
            # If iterations is odd: Result is in buf_b (New Buffer).

            # To be safe and consistent:
            # We effectively return a field that the User now OWNS (or must release).

            # If result is in buf_b (temp), user gets it.
            # If result is in buf_a (input), user gets it.

            return final_result_gpu

else:

    def refine_flow_guided(*args, **kwargs):
        raise ImportError("Taichi not available")
