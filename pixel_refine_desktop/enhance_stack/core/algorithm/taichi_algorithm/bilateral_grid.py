# Marker: GPU_NATIVE_MARKER_V3
"""
Bilateral Grid - Taichi GPU Implementation
==========================================
Fast, edge-preserving smoothing using a bilateral grid.
Ported from standalone script to modular function.
"""

import numpy as np

try:
    import taichi as ti
    import taichi.math as tm
    from . import common
    from .taichi_worker import ti_thread

    TAICHI_AVAILABLE = True
except ImportError:
    TAICHI_AVAILABLE = False
    ti = None
    tm = None

if TAICHI_AVAILABLE:

    @ti.func
    def compute_weights(idx: int, radius: int, sigma: float, weights: ti.template()):
        total = 0.0
        ti.loop_config(serialize=True)
        for j in range(-radius, radius + 1):
            val = ti.exp(-0.5 * (j / sigma) ** 2)
            weights[idx, j] = val
            total += val

        ti.loop_config(serialize=True)
        for j in range(-radius, radius + 1):
            weights[idx, j] /= total

    @ti.func
    def sample_grid_spatial(i, j, k, grid_blurred: ti.types.ndarray()):
        # g = grid_blurred # Assignment might be redundant or issue, use directly

        # Linear interpolation on grid
        # ...
        i_int = int(i)
        j_int = int(j)

        # Access 4 neighbors
        v00 = grid_blurred[i_int, j_int, k]
        v10 = grid_blurred[i_int + 1, j_int, k]
        v01 = grid_blurred[i_int, j_int + 1, k]
        v11 = grid_blurred[i_int + 1, j_int + 1, k]

        mix_i_0 = tm.mix(v00, v10, tm.fract(i))
        mix_i_1 = tm.mix(v01, v11, tm.fract(i))

        return tm.mix(mix_i_0, mix_i_1, tm.fract(j))

    @ti.func
    def sample_grid(i, j, k, grid_blurred: ti.types.ndarray()):
        k_int = int(k)
        val0 = sample_grid_spatial(i, j, k_int, grid_blurred)
        val1 = sample_grid_spatial(i, j, k_int + 1, grid_blurred)
        return tm.mix(val0, val1, tm.fract(k))

    @ti.kernel
    def _bilateral_grid_kernel(
        img: ti.types.ndarray(),
        grid: ti.types.ndarray(),
        grid_blurred: ti.types.ndarray(),
        weights: ti.types.ndarray(),
        s_s: int,
        s_r: int,
        sigma_s: float,
        sigma_r: float,
        grid_n: int,
        grid_m: int,
        grid_l: int,
    ):
        # 1. Fill Grid
        # (Cleared in Python host)

        for i, j in ti.ndrange(img.shape[0], img.shape[1]):
            # Assuming image is [H, W] single channel or processing per channel outside?
            # The original script processed per channel in a loop outside.
            # This kernel assumes 'img' is 2D (H,W) or we treat it as single channel here.
            # If passed 3D, we need to know which channel or handle 3D.
            # Let's assume input is 2D float32 or uint8 normalized?
            # Original: lum = img[i,j], img was passed as channel.

            lum = float(img[i, j])  # Ensure float

            # Grid coordinates
            gx = int(tm.round(i / s_s))
            gy = int(tm.round(j / s_s))
            gz = int(tm.round(lum / s_r))

            # Clamp to be safe
            gx = tm.clamp(gx, 0, grid_n - 1)
            gy = tm.clamp(gy, 0, grid_m - 1)
            gz = tm.clamp(gz, 0, grid_l - 1)

            grid[gx, gy, gz] += tm.vec2(lum, 1.0)

        # 2. Compute Weights
        # radius approximated by 3*sigma
        r_s = int(tm.ceil(sigma_s * 3.0))
        r_r = int(tm.ceil(sigma_r * 3.0))

        compute_weights(0, r_s, sigma_s, weights)
        compute_weights(1, r_r, sigma_r, weights)

        # 3. Blur Grid
        # Pass 1: x (i)
        for i, j, k in ti.ndrange(grid_n, grid_m, grid_l):
            l_begin = ti.max(0, i - r_s)
            l_end = ti.min(grid_n, i + r_s + 1)
            total = tm.vec2(0.0, 0.0)
            for l in range(l_begin, l_end):
                total += grid[l, j, k] * weights[0, i - l]
            grid_blurred[i, j, k] = total

        # Pass 2: y (j) - write back to grid
        for i, j, k in ti.ndrange(grid_n, grid_m, grid_l):
            l_begin = ti.max(0, j - r_s)
            l_end = ti.min(grid_m, j + r_s + 1)
            total = tm.vec2(0.0, 0.0)
            for l in range(l_begin, l_end):
                total += grid_blurred[i, l, k] * weights[0, j - l]
            grid[i, j, k] = total

        # Pass 3: z (k/range) - write back to grid_blurred
        for i, j, k in ti.ndrange(grid_n, grid_m, grid_l):
            l_begin = ti.max(0, k - r_r)
            l_end = ti.min(grid_l, k + r_r + 1)
            total = tm.vec2(0.0, 0.0)
            for l in range(l_begin, l_end):
                total += grid[i, j, l] * weights[1, k - l]
            grid_blurred[i, j, k] = total

        # 4. Slice (Sample)
        for i, j in ti.ndrange(img.shape[0], img.shape[1]):
            lum = float(img[i, j])

            # Trilinear sample
            sample = sample_grid(i / s_s, j / s_s, lum / s_r, grid_blurred)

            # Normalize
            res = 0.0
            if sample[1] > 0:
                res = sample[0] / sample[1]

            img[i, j] = (
                res  # Cast back to input type automatically usually, or explicit cast if needed
            )


@ti_thread
def bilateral_grid_filter(
    img,
    dst=None,
    s_s: int = 16,
    s_r: int = 16,
    sigma_s: float = 1.0,
    sigma_r: float = 1.0,
    buffer_provider="pool",
):
    """
    Apply Bilateral Grid filter.

    Args:
        img: Input image (H, W) or (H, W, C).
        dst: Optional output buffer.
        s_s: Spatial step (grid size divisor). Larger = coarser/faster.
        s_r: Range step (intensity bin divisor). Larger = coarser/faster.
        sigma_s: Spatial sigma (blur strength).
        sigma_r: Range sigma (blur strength).
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # Handle Color Images by processing channels independently
    # This matches the reference implementation logic
    is_multichannel = len(img.shape) == 3 and img.shape[2] > 1

    # Grid dimensions
    h, w = img.shape[:2]

    # Calculate grid size
    # padding added (+s_s) to avoid boundary issues during sampling
    grid_n = (h + s_s - 1) // s_s + 2  # Added padding margin just in case
    grid_m = (w + s_s - 1) // s_s + 2

    # Assuming input is 0-255 range?
    # Original script loop: channels = [img[:,:,c]...], processed as 0-255 uint8 usually.
    # grid_l determined by range. if float 0-1, s_r should be small. if 0-255, s_r ~16.
    # Let's assume input matches expected s_r.
    # Max value estimation:
    # If float 0..1, max is 1. grid_l = (1 + s_r)/s_r ?
    # Usually bilateral grid is used on 0-255.
    # We should detect or document this.

    # For robust implementation, let's assume valid range is covered by s_r * grid_l
    # If s_r=16, grid_l=16 -> covers 256.
    grid_l = 256 // s_r + 2  # +2 padding

    # Allocating fields
    # Dynamic allocation per call (since grid size depends on image size/params)
    # This might use a lot of memory for large images if not managed.

    # Use 'ti.root' or dynamic fields?
    # For now, we instantiate distinct fields.
    # CAUTION: Repeated allocation in Taichi can be slow if not re-using fields.
    # Ideally we'd use a SNodeTree or reused fields if sizes match.
    # Given the complexity, let's just allocate scalar fields for now.

    # However, 'ti.field' is global! We cannot allocate it inside a function easily repeatedly
    # without managing 'ti.root' resets which deletes everything.
    # BUT, we can use 'ti.ndarray' (DeviceAllocations) which are temporary!
    # The original script used 'ti.Vector.field' which is global.
    # We MUST use 'ti.Vector.ndarray' or 'ti.ndarray' with vector dim?
    # Taichi ndarrays are meant to be passed to kernels. They are backed by memory on device.
    # Constructing a 3D Vector ndarray:

    # grid shape: (grid_n, grid_m, grid_l)
    # vector size: 2

    grid_shape = (grid_n, grid_m, grid_l)

    # Create ndarrays
    # Note: ti.Vector.ndarray requires shape
    grid = ti.Vector.ndarray(n=2, dtype=ti.f32, shape=grid_shape)
    grid_blurred = ti.Vector.ndarray(n=2, dtype=ti.f32, shape=grid_shape)

    grid.fill(0)
    grid_blurred.fill(0)

    # Weights: (2, max_radius * 2 + 1)
    # We need enough space. Say 256 width is safe.
    weights = ti.ndarray(dtype=ti.f32, shape=(2, 512))

    # Prepare Input/Output
    src_gpu, src_is_temp = common.ensure_taichi_field(
        img, dtype=ti.f32, buffer_provider=buffer_provider
    )

    if dst is None:
        if is_multichannel:
            dst_gpu = common.get_temp_buffer(img.shape, ti.f32, buffer_provider)
        else:
            dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)
    else:
        dst_gpu = dst

    # Process
    if not is_multichannel:
        # 1 Channel
        # Copy src to dst initially because kernel reads/writes in place or we need dual buffer?
        # The kernel reads 'img' and writes 'img'.
        # We should probably copy src to dst first, then filter 'dst'.
        # Or modify kernel to read 'src' write 'dst'?
        # Original kernel: 'lum = img[i,j]', then 'img[i,j] = result'. In-place.

        # We'll copy src to dst, then run kernel on dst inplace.
        common._copy_field_lowlevel(src_gpu, dst_gpu)

        _bilateral_grid_kernel(
            dst_gpu,
            grid,
            grid_blurred,
            weights,
            s_s,
            s_r,
            sigma_s,
            sigma_r,
            grid_n,
            grid_m,
            grid_l,
        )
    else:
        # 3 Channels
        # We need to process each channel independently.
        # But 'img' passed to kernel is 2D.
        # We can write a 3ch kernel or just loop here?
        # Looping here means extracting channel?
        # 'common' doesn't easily expose channel extraction kernel yet?
        # Or we can write a wrapper kernel that extracts channel.

        # Let's write a simple helper kernel for 3ch extraction/insertion if needed,
        # OR just adapt the kernel to handle channel index.

        # Actually simplest is to adapt _bilateral_grid_kernel to take channel index.
        # But that requires modifying it to read (i,j,c).

        # Let's try to do it efficiently.
        pass  # To be implemented if we want pure 3ch support in one go.
        # For now, let's just loop locally if possible?
        # We can't easily loop over channels with 'dst_gpu' being 3D and kernel expecting 2D.

        # Hack solution: Use ti.ndarray for temp single channel?
        temp_ch = ti.ndarray(dtype=ti.f32, shape=(h, w))

        for c in range(3):
            # Extract channel
            common._extract_channel_lowlevel(src_gpu, temp_ch, c)

            # Filter
            _bilateral_grid_kernel(
                temp_ch,
                grid,
                grid_blurred,
                weights,
                s_s,
                s_r,
                sigma_s,
                sigma_r,
                grid_n,
                grid_m,
                grid_l,
            )

            # Insert back
            common._insert_channel_lowlevel(temp_ch, dst_gpu, c)

    # Cleanup
    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    # grid and grid_blurred ndarrays are automatically freed by Python GC when out of scope.

    return common.to_numpy_if_needed(dst_gpu, src_is_temp and dst is None)
