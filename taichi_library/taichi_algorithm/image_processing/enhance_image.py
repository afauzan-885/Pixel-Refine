"""Grayscale Image Enhancement (1D LUT & Micro-Contrast) - Taichi GPU"""

import os
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
    @ti.kernel
    def _enhance_grayscale_kernel(
        src: ti.types.ndarray(),
        blur: ti.types.ndarray(),
        lut: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        micro_contrast: float,
        clarity: float,
        noise_coring: float,
        h: int,
        w: int,
    ):
        for r, c in ti.ndrange(h, w):
            val = src[r, c]
            b_val = blur[r, c]
            
            # 1. Contrast-Aware Halo-Free Detail Shaping with Noise Coring
            diff = val - b_val
            abs_diff = ti.abs(diff)
            
            # Apply smooth coring to prevent noise amplification
            attenuation = 1.0
            if abs_diff < noise_coring:
                if noise_coring > 0.0:
                    attenuation = abs_diff / noise_coring
                else:
                    attenuation = 0.0
            
            shaped_diff = (diff * attenuation) / (1.0 + abs_diff * 5.0)  # 5.0 halo suppression coefficient
            
            # 2. Midtone-targeted local contrast (Clarity bell curve: peaks at 0.5, zero at 0 and 1)
            midtone_mask = 16.0 * val * val * (1.0 - val) * (1.0 - val)
            
            # Combine Micro-contrast (high frequencies) and Clarity (midtones local contrast)
            enhanced = val + shaped_diff * micro_contrast + shaped_diff * clarity * midtone_mask
            
            # 3. Global contrast enhancement (1D LUT lookup)
            lut_idx = ti.cast(ti.math.clamp(enhanced * 255.0, 0.0, 255.0), ti.i32)
            dst[r, c] = lut[lut_idx]


def enhance_grayscale(src, blur, lut, micro_contrast=2.93, clarity=0.0, noise_coring=0.0, dst=None, buffer_provider="pool"):
    """
    GPU-accelerated Grayscale Image Enhancement (1D LUT & Micro-Contrast & Clarity).
    Applies detail-boosting (micro-contrast) via difference from blurred image,
    clarity via midtone-targeted local contrast,
    and shapes global contrast via a 1D Look-Up Table (LUT) - all in a single GPU pass.

    All Taichi operations are synchronized via @ti_thread.

    Args:
        src:             Input luma image - NumPy array OR Taichi ndarray. (H, W)
        blur:            Blurred luma image - NumPy array OR Taichi ndarray. (H, W)
        lut:             1D Look-Up Table (256 elements) - NumPy array OR Taichi ndarray.
        micro_contrast:  Scale factor to boost high-frequency details. Calibrated default: 2.93.
        clarity:         Local contrast clarity factor.
        noise_coring:    Threshold to suppress low-amplitude noise boosting.
        dst:             Optional pre-allocated output buffer (H, W).
        buffer_provider: Optional buffer pool provider ("pool" or None).

    Returns:
        Enhanced grayscale image in the same format as input (NumPy or Taichi).
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        from ..common import _get_aot
        aot = _get_aot()
        if aot and hasattr(aot, "enhance_grayscale"):
            is_taichi = hasattr(src, "to_numpy") or hasattr(blur, "to_numpy") or hasattr(lut, "to_numpy")
            # Fallback to passing available parameters to AOT
            res_buf = aot.enhance_grayscale(src, blur, lut, float(micro_contrast), float(clarity), return_gpu=is_taichi)
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

    is_taichi_input = hasattr(src, "to_numpy") or hasattr(blur, "to_numpy") or hasattr(lut, "to_numpy")

    @ti_thread
    def _run_gpu_enhance(src_data, blur_data, lut_data, dst_data=None):
        src_gpu, src_is_temp = ensure_taichi_field(src_data, dtype=ti.f32, buffer_provider=buffer_provider)
        blur_gpu, blur_is_temp = ensure_taichi_field(blur_data, dtype=ti.f32, buffer_provider=buffer_provider)
        lut_gpu, lut_is_temp = ensure_taichi_field(lut_data, dtype=ti.f32, buffer_provider=buffer_provider)

        h, w = src_gpu.shape[:2]

        if dst_data is None:
            dst_gpu = get_temp_buffer((h, w), ti.f32, buffer_provider)
        else:
            dst_gpu, _ = ensure_taichi_field(dst_data, dtype=ti.f32, buffer_provider=buffer_provider)

        _enhance_grayscale_kernel(src_gpu, blur_gpu, lut_gpu, dst_gpu, float(micro_contrast), float(clarity), float(noise_coring), h, w)

        # Clean up temporaries
        if src_is_temp:
            release_temp_buffer(src_gpu)
        if blur_is_temp:
            release_temp_buffer(blur_gpu)
        if lut_is_temp:
            release_temp_buffer(lut_gpu)

        # Download if input was NumPy
        if not is_taichi_input:
            res = dst_gpu.to_numpy()
            release_temp_buffer(dst_gpu)
            if dst_data is not None:
                dst_data[:] = res
                return dst_data
            return res

        return dst_gpu

    return _run_gpu_enhance(src, blur, lut, dst)
