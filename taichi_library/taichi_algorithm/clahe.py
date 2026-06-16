# Marker: GPU_NATIVE_MARKER_V3
"""
CLAHE - Contrast Limited Adaptive Histogram Equalization (Taichi GPU)
=====================================================================
Local contrast enhancement with noise amplification control.

Reference:
  - Zuiderveld, K. (1994). "Contrast Limited Adaptive Histogram Equalization."
    Graphics Gems IV, Academic Press, pp. 474-485.

Algorithm:
  1. Divide image into tiles (grid_size_x x grid_size_y)
  2. Compute local histogram per tile (256 bins)
  3. Clip histogram at clip_limit, redistribute excess uniformly
  4. Compute CDF -> LUT per tile
  5. Bilinear interpolation between 4 nearest tile LUTs

GPU Strategy:
  - Stage 1: Parallel histogram (one thread per pixel, atomics per tile)
  - Stage 2: Clip + redistribute + CDF (one thread per tile, sequential over bins)
  - Stage 3: Parallel interpolation (one thread per output pixel)
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
    from . import common
    from .taichi_worker import ti_thread
except ImportError:
    pass

if TAICHI_AVAILABLE:

    # =========================================================================
    # Stage 1: Parallel Histogram Computation
    # =========================================================================
    @ti.kernel
    def _clahe_histogram_kernel(src: ti.types.ndarray(),
                                 hist: ti.types.ndarray(),
                                 h: int, w: int,
                                 tile_h: int, tile_w: int,
                                 tiles_x: int, tiles_y: int):
        """Compute per-tile histogram. Each pixel atomically adds to its tile's bin."""
        for y, x in ti.ndrange(h, w):
            val = ti.cast(tm.clamp(src[y, x], 0.0, 255.0), ti.i32)
            # Determine which tile this pixel belongs to
            ty = ti.min(y // tile_h, tiles_y - 1)
            tx = ti.min(x // tile_w, tiles_x - 1)
            tile_idx = ty * tiles_x + tx
            ti.atomic_add(hist[tile_idx, val], 1)

    # =========================================================================
    # Stage 2: Clip + Redistribute + CDF (one thread per tile)
    # =========================================================================
    @ti.kernel
    def _clahe_clip_cdf_kernel(hist: ti.types.ndarray(),
                                 lut: ti.types.ndarray(),
                                 total_tiles: int, num_bins: int,
                                 clip_limit: int, tile_pixels: int):
        """Clip histogram, redistribute excess, compute CDF -> LUT per tile."""
        for t in range(total_tiles):
            # Step 1: Clip and count excess
            excess = 0
            for b in range(num_bins):
                if hist[t, b] > clip_limit:
                    excess += hist[t, b] - clip_limit
                    hist[t, b] = clip_limit

            # Step 2: Redistribute excess uniformly
            redist_batch = excess // num_bins
            residual = excess - redist_batch * num_bins

            for b in range(num_bins):
                hist[t, b] += redist_batch

            # Distribute residual one per bin, evenly spaced
            if residual > 0:
                step = ti.max(num_bins // residual, 1)
                b = 0
                r = residual
                while r > 0 and b < num_bins:
                    hist[t, b] += 1
                    r -= 1
                    b += step

            # Step 3: Compute CDF and scale to LUT
            scale = float(num_bins - 1) / float(tile_pixels)
            cdf = 0
            for b in range(num_bins):
                cdf += hist[t, b]
                lut_val = float(cdf) * scale
                lut[t, b] = ti.min(lut_val, float(num_bins - 1))

    # =========================================================================
    # Stage 3: Bilinear Interpolation Between Tile LUTs
    # =========================================================================
    @ti.kernel
    def _clahe_interpolate_kernel(src: ti.types.ndarray(),
                                    lut: ti.types.ndarray(),
                                    dst: ti.types.ndarray(),
                                    h: int, w: int,
                                    tile_h: int, tile_w: int,
                                    tiles_x: int, tiles_y: int):
        """Bilinear interpolation between 4 nearest tile LUTs."""
        for y, x in ti.ndrange(h, w):
            val = ti.cast(tm.clamp(src[y, x], 0.0, 255.0), ti.i32)

            # Compute tile center positions
            # Tile center for tile i: i * tile_w + tile_w/2
            # Find which tile column/row the pixel is between

            # Fractional tile position (relative to tile centers)
            # First tile center at tile_w/2, last at w - tile_w/2
            fx = (float(x) - float(tile_w) * 0.5) / float(tile_w)
            fy = (float(y) - float(tile_h) * 0.5) / float(tile_h)

            # Tile indices (floor and ceil)
            tx0 = ti.cast(ti.floor(fx), ti.i32)
            ty0 = ti.cast(ti.floor(fy), ti.i32)
            tx1 = tx0 + 1
            ty1 = ty0 + 1

            # Fractional weights
            wx = fx - float(tx0)
            wy = fy - float(ty0)

            # Clamp tile indices to valid range
            tx0 = tm.clamp(tx0, 0, tiles_x - 1)
            tx1 = tm.clamp(tx1, 0, tiles_x - 1)
            ty0 = tm.clamp(ty0, 0, tiles_y - 1)
            ty1 = tm.clamp(ty1, 0, tiles_y - 1)

            # Look up from 4 tile LUTs
            tile_tl = ty0 * tiles_x + tx0
            tile_tr = ty0 * tiles_x + tx1
            tile_bl = ty1 * tiles_x + tx0
            tile_br = ty1 * tiles_x + tx1

            v_tl = lut[tile_tl, val]
            v_tr = lut[tile_tr, val]
            v_bl = lut[tile_bl, val]
            v_br = lut[tile_br, val]

            # Bilinear interpolation
            top = v_tl * (1.0 - wx) + v_tr * wx
            bot = v_bl * (1.0 - wx) + v_br * wx
            result = top * (1.0 - wy) + bot * wy

            dst[y, x] = result


@ti_thread
def clahe(src, clip_limit=2.0, tile_grid_size=(8, 8), dst=None, buffer_provider="pool"):
    """
    CLAHE - Contrast Limited Adaptive Histogram Equalization (GPU-accelerated).
    OpenCV-compatible: Similar to cv2.createCLAHE(clipLimit, tileGridSize).apply()

    Args:
        src: Input grayscale image (H, W), uint8 or float32 [0, 255].
        clip_limit: Contrast clip limit (typical: 1.0 - 4.0, default 2.0).
                    Higher = more aggressive contrast, risk of noise amplification.
        tile_grid_size: Tuple (tiles_x, tiles_y) defining the grid.
                        Default (8, 8) = 64 tiles.
        dst: Optional output buffer (H, W).
        buffer_provider: Buffer pool provider.

    Returns:
        CLAHE-enhanced image in same format as input, values [0, 255].
    """
    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    is_numpy = isinstance(src, np.ndarray)
    src_gpu, src_is_temp = common.ensure_taichi_field(src, dtype=ti.f32,
                                                       buffer_provider=buffer_provider)
    h, w = src_gpu.shape[:2]
    tiles_x, tiles_y = tile_grid_size
    total_tiles = tiles_x * tiles_y
    num_bins = 256

    # Tile dimensions
    tile_h = (h + tiles_y - 1) // tiles_y
    tile_w = (w + tiles_x - 1) // tiles_x
    tile_pixels = tile_h * tile_w

    # Compute integer clip limit per tile
    beta = max(int(clip_limit * tile_pixels / num_bins), 1)

    # Allocate histogram and LUT
    hist_gpu = ti.ndarray(dtype=ti.i32, shape=(total_tiles, num_bins))
    hist_gpu.fill(0)
    lut_gpu = ti.ndarray(dtype=ti.f32, shape=(total_tiles, num_bins))

    # Stage 1: Compute histograms
    _clahe_histogram_kernel(src_gpu, hist_gpu, h, w, tile_h, tile_w, tiles_x, tiles_y)

    # Stage 2: Clip + redistribute + CDF
    _clahe_clip_cdf_kernel(hist_gpu, lut_gpu, total_tiles, num_bins, beta, tile_pixels)

    # Stage 3: Interpolate
    if dst is not None:
        dst_gpu, _ = common.ensure_taichi_field(dst, dtype=ti.f32,
                                                 buffer_provider=buffer_provider)
    else:
        dst_gpu = common.get_temp_buffer((h, w), ti.f32, buffer_provider)

    _clahe_interpolate_kernel(src_gpu, lut_gpu, dst_gpu, h, w,
                                tile_h, tile_w, tiles_x, tiles_y)

    if src_is_temp:
        common.release_temp_buffer(src_gpu)

    return common.to_numpy_if_needed(dst_gpu, is_numpy)
