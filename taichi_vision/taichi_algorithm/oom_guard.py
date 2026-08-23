"""
OOM Guard
=========
Provides safe execution of Taichi algorithms on arbitrary resolution images
by using Tiled Processing (Chunking) with overlap support.

Ensures seamless results identical to full-frame processing.
"""

import math
import numpy as np


import subprocess
import shutil
import psutil


def get_available_vram_mb():
    """
    Get available VRAM in MB.
    Tries nvidia-smi, then assumes a conservative default if failed.
    """
    try:
        # Check if nvidia-smi exists
        if shutil.which("nvidia-smi"):
            # Run nvidia-smi to get free memory
            # format: memory.free
            result = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.free",
                    "--format=csv,noheader,nounits",
                ],
                encoding="utf-8",
            )
            # Take the first GPU if multiple
            free_mb = int(result.strip().split("\n")[0])
            return free_mb
    except Exception:
        pass

    # TODO: Add specific checks for AMD/Intel if needed (e.g. via vulkano/wgpu if accessible)
    # For now, return a conservative fallback or None to indicate "Unknown"
    # If Unknown, fall back to fixed threshold strategy.
    return None


def should_tile(
    image, channels=3, dtype_size=4, safety_factor=0.8, fixed_threshold=30000000
):
    """
    Determine if tiling is necessary based on available VRAM.

    Args:
        image: Numpy array or Tuple (H, W, ...).
        channels: Channels if image is shape tuple or verification needed.
        dtype_size: Bytes per pixel per channel (float32 = 4).
        safety_factor: Fraction of free VRAM we are allowed to use.
        fixed_threshold: Fallback threshold in pixels (default 30MP).
    """
    # Determine pixels
    if isinstance(image, np.ndarray):
        h, w = image.shape[:2]
        # Trust image.size for total elements (H*W*C)
        total_elements = image.size
        # Correct channels if 2D
        if len(image.shape) == 2:
            total_elements = h * w * channels  # Assume expansion happens?
            # Actually, if input is Gray (1ch) and we process it as Gray, size is H*W.
            # If we process Gray -> RGB, we need 3x.
            # Usually input size is a good proxy for buffer needs (input + output + temp).
            # A safe heuristic: We need alloc for Input + Output + Temp.
            # Total mem ~= 3 * ImageSize.
            pass
    elif isinstance(image, (tuple, list)):
        h, w = image[0], image[1]
        total_elements = h * w * channels
    else:
        return True  # Safer to tile if unknown

    # Calculate required memory for this operation roughly
    # (Input + Output + Local Temp) ~ 3x - 4x size.
    estimated_need_mb = (total_elements * dtype_size * 4) / (1024 * 1024)

    available_mb = get_available_vram_mb()

    if available_mb is not None:
        # Adaptive Check
        if estimated_need_mb < (available_mb * safety_factor):
            return False  # Safe to run Native
        else:
            return True  # Must Tile

    # Fallback to fixed threshold if VRAM unknown
    # fixed_threshold is in Pixels (e.g. 30M pixels)
    # Map pixels to estimated need? No, fixed threshold assumes "standard GPU".
    # User asked for adaptive. If adaptive fails, we stick to 30MP rule.
    return (total_elements / channels) > fixed_threshold


def get_safe_tile_size(channels=3, safety_factor=0.8):
    """
    Calculate maximum safe tile size based on available VRAM.
    Returns size (width/height) as int.
    """
    available_mb = get_available_vram_mb()
    if available_mb is None:
        # Fallback to standard 2048 if detection fails
        return 2048

    # Available Memory (Bytes)
    available_bytes = available_mb * 1024 * 1024 * safety_factor

    # Needs per pixel (Float32 = 4 bytes)
    # 1. Input Tile (Tile + Halo) ~ Tile
    # 2. Output Tile
    # 3. Temp Buffer (assume 1-2 intermediates)
    # Total ~ 4-5 buffers * channels * 4 bytes
    # Safe estimation: 5 buffers (Input, Output, Temp1, Temp2, Overhead)
    bytes_per_pixel = 4 * channels * 5

    max_pixels = available_bytes / bytes_per_pixel
    max_side = int(math.sqrt(max_pixels))

    # Align to 128 for GPU efficiency
    max_side = (max_side // 128) * 128

    # Clamp
    # Clamp to smaller sizes for better UI responsiveness on single-GPU desktops
    # 1024-1536 is the "sweet spot" for MX150/Internal GPU fluid display.
    return max(768, min(max_side, 1536))


def execute_tiled(
    func,
    src: np.ndarray,
    overlap: int = 64,
    tile_size=None,
    progress_callback=None,
    **kwargs,
):
    """
    Execute a Taichi function on a large image using tiling.

    Args:
        func: The GPU function to call (e.g. gaussian_blur).
        src: Input NumPy array (H, W, C).
        overlap: Pixels of overlap to ensure seamless edges (kernel radius).
        tile_size: Base size of tiles. If None, calc dynamically.
        **kwargs: Arguments passed to func.

    Returns:
        np.ndarray: The processed image (same shape as src).
    """
    h, w = src.shape[:2]

    # Determine Tile Size
    if tile_size is None:
        # Estimate channels from src
        ch = 1
        if len(src.shape) == 3:
            ch = src.shape[2]
        tile_size = get_safe_tile_size(channels=ch)

    # If image is small enough, run directly
    if h <= tile_size and w <= tile_size:
        return func(src, **kwargs)

    # Prepare output CPU buffer
    # Determine output shape (assuming same number of channels as input or specified?)
    # Most filters preserve channels. Warp preserves channels.
    # Gradients might change channels (1 -> 2).
    # We run one tile to sniff output shape if needed, or assume src shape.
    # Let's run a small dummy probe if unsure?
    # Better: Inspect src shape.

    # ISSUE: We don't know output channels of func without running it.
    # Hack: Run a tiny 8x8 corner to determine output shape/dtype.
    probe_tile = src[:16, :16].copy()
    probe_res = func(probe_tile, **kwargs)

    # Handle tuple return (e.g., Sobel returns dx, dy)
    is_tuple_return = isinstance(probe_res, tuple)

    if is_tuple_return:
        out_buffers = []
        for res_item in probe_res:
            # Ensure probe result is numpy
            if hasattr(res_item, "to_numpy"):
                res_item = res_item.to_numpy()

            out_shape = list(src.shape)
            # Update channels based on probe
            if len(res_item.shape) == 3:
                out_shape[2] = res_item.shape[2]
            elif len(res_item.shape) == 2:
                out_shape = out_shape[:2]  # Output is single channel/grayscale

            out_buffers.append(np.zeros(out_shape, dtype=res_item.dtype))
    else:
        # Single return
        if hasattr(probe_res, "to_numpy"):
            probe_res = probe_res.to_numpy()

        out_shape = list(src.shape)
        if len(probe_res.shape) == 3:
            out_shape[2] = probe_res.shape[2]
        elif len(probe_res.shape) == 2:
            out_shape = out_shape[:2]

        # System RAM Check
        required_ram_bytes = np.prod(out_shape) * probe_res.itemsize
        if is_tuple_return:
            # Just heuristic for first buffer, or multiply by len(probe_res)?
            # Usually similar size.
            required_ram_bytes *= len(probe_res)

        available_ram = psutil.virtual_memory().available
        if required_ram_bytes > available_ram * 0.9:  # 90% margin
            raise MemoryError(
                f"Insufficient System RAM for Tiled Output. Needed: {required_ram_bytes/1e6:.1f}MB, Available: {available_ram/1e6:.1f}MB"
            )

        out_buffers = [np.zeros(out_shape, dtype=probe_res.dtype)]

    # Tiling Loop
    x_steps = math.ceil(w / tile_size)
    y_steps = math.ceil(h / tile_size)

    total_tiles = x_steps * y_steps
    tiles_done = 0

    for y_i in range(y_steps):
        for x_i in range(x_steps):
            # 1. Define Core Tile (The area we want to WRITE)
            x_start = x_i * tile_size
            y_start = y_i * tile_size
            x_end = min(x_start + tile_size, w)
            y_end = min(y_start + tile_size, h)

            curr_w = x_end - x_start
            curr_h = y_end - y_start

            # 2. Define Input Tile with Halo (The area we need to READ)
            x_in_start = max(x_start - overlap, 0)
            y_in_start = max(y_start - overlap, 0)
            x_in_end = min(x_end + overlap, w)
            y_in_end = min(y_end + overlap, h)

            # Extract input tile
            if len(src.shape) == 3:
                tile_in = src[y_in_start:y_in_end, x_in_start:x_in_end, :]
            else:
                tile_in = src[y_in_start:y_in_end, x_in_start:x_in_end]

            # 3. Process Tile
            # Note: We must ensure the func returns a clean numpy/field without keeping memory
            tile_out_raw = func(tile_in, **kwargs)

            # 4. Handle Return and Crop
            # Calculate where the "Core" is relative to the "Input Tile"
            rel_x_start = x_start - x_in_start
            rel_y_start = y_start - y_in_start
            rel_x_end = rel_x_start + curr_w
            rel_y_end = rel_y_start + curr_h

            outputs_to_process = tile_out_raw if is_tuple_return else (tile_out_raw,)

            for buffer_idx, tile_res in enumerate(outputs_to_process):
                # Ensure numpy
                if hasattr(tile_res, "to_numpy"):
                    tile_res = tile_res.to_numpy()
                elif hasattr(tile_res, "to_torch"):  # Just in case
                    tile_res = tile_res.cpu().numpy()

                # Crop and Write to main buffer
                if len(tile_res.shape) == 3:
                    # Check shape match, sometimes output is smaller? No, algorithms preserve size (except pyramid)
                    # Assuming size is preserved relative to input tile
                    crop = tile_res[rel_y_start:rel_y_end, rel_x_start:rel_x_end, :]
                    out_buffers[buffer_idx][y_start:y_end, x_start:x_end, :] = crop
                else:
                    crop = tile_res[rel_y_start:rel_y_end, rel_x_start:rel_x_end]
                    out_buffers[buffer_idx][y_start:y_end, x_start:x_end] = crop

            # 5. Progress Signaling
            tiles_done += 1
            if progress_callback:
                try:
                    progress_callback(tiles_done / total_tiles)
                except:
                    pass

            # Cleanup explicitly if possible?
            # The loop scope should handle it in Python, but we can trust the GC.

    if is_tuple_return:
        return tuple(out_buffers)
    else:
        return out_buffers[0]
