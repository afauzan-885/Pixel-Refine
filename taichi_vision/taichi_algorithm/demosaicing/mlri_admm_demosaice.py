"""MLRI-ADMM GPU-Accelerated RAW Demosaicing (Strict C++ AOT-Only Module)"""

import os
import numpy as np

def mlri_admm_demosaic(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    dst=None, buffer_provider="pool"
):
    """GPU-Accelerated MLRI-ADMM Demosaicing (RAW to sRGB via strict C++ AOT).
    
    Args:
        bayer:           Input RAW Bayer sensor image - NumPy array OR Taichi ndarray. (H, W)
        wb_r, wb_g1,
        wb_b, wb_g2:     Normalized White Balance gains for R, G1, B, G2.
        cmatrix:         3x3 Camera-to-sRGB conversion matrix.
        black_level:     Sensor black level (float).
        white_level:     Sensor white saturation level (float).
        c00, c01,
        c10, c11:        Bayer pattern 2x2 grid values (0=R, 1=G, 2=B, 3=G).
        dst:             Optional pre-allocated destination buffer (H, W, 3).
        buffer_provider: Unused, kept for API compatibility.
        
    Returns:
        Demosaiced RGB image in the same format as input (NumPy or Taichi).
    """
    from ..common import _get_aot
    aot = _get_aot()
    if not aot or not hasattr(aot, "mlri_admm_demosaic"):
        import taichi_vision.taichi_aot as ta_aot
        aot = ta_aot
        
    is_taichi = hasattr(bayer, "to_numpy") or hasattr(cmatrix, "to_numpy")
    res_buf = aot.mlri_admm_demosaic(
        bayer, float(wb_r), float(wb_g1), float(wb_b), float(wb_g2),
        cmatrix, float(black_level), float(white_level),
        int(c00), int(c01), int(c10), int(c11),
        return_gpu=is_taichi,
        dst=dst
    )
    return res_buf

mlri_admm = mlri_admm_demosaic



def mlri_admm_demosaic_1channel(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    dst=None, buffer_provider="pool"
):
    """Fast Green-Only MLRI-ADMM Demosaic to Grayscale 1-channel."""
    from ..common import _get_aot
    aot = _get_aot()
    if not aot or not hasattr(aot, "mlri_admm_demosaic_1channel"):
        import taichi_vision.taichi_aot as ta_aot
        aot = ta_aot
        
    is_taichi = hasattr(bayer, "to_numpy")
    res_buf = aot.mlri_admm_demosaic_1channel(
        bayer, float(wb_r), float(wb_g1), float(wb_b), float(wb_g2),
        float(black_level), float(white_level),
        int(c00), int(c01), int(c10), int(c11),
        return_gpu=is_taichi,
        dst=dst
    )
    return res_buf


def mlri_admm_demosaic_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2,
    black_level, white_level, c00, c01, c10, c11,
    dst=None, buffer_provider="pool"
):
    """Bypass MLRI-ADMM: Green Sub-Sampling to 1/2 size grayscale."""
    from ..common import _get_aot
    aot = _get_aot()
    if not aot or not hasattr(aot, "mlri_admm_demosaic_half_res"):
        import taichi_vision.taichi_aot as ta_aot
        aot = ta_aot
        
    is_taichi = hasattr(bayer, "to_numpy")
    res_buf = aot.mlri_admm_demosaic_half_res(
        bayer, float(wb_r), float(wb_g1), float(wb_b), float(wb_g2),
        float(black_level), float(white_level),
        int(c00), int(c01), int(c10), int(c11),
        return_gpu=is_taichi,
        dst=dst
    )
    return res_buf


def mlri_admm_demosaic_rgb_half_res(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    dst=None, buffer_provider="pool"
):
    """Bypass MLRI-ADMM: RGB Direct Sub-Sampling to 1/2 size RGB."""
    from ..common import _get_aot
    aot = _get_aot()
    if not aot or not hasattr(aot, "mlri_admm_demosaic_rgb_half_res"):
        import taichi_vision.taichi_aot as ta_aot
        aot = ta_aot
        
    is_taichi = hasattr(bayer, "to_numpy") or hasattr(cmatrix, "to_numpy")
    res_buf = aot.mlri_admm_demosaic_rgb_half_res(
        bayer, float(wb_r), float(wb_g1), float(wb_b), float(wb_g2),
        cmatrix, float(black_level), float(white_level),
        int(c00), int(c01), int(c10), int(c11),
        return_gpu=is_taichi,
        dst=dst
    )
    return res_buf


def mlri_admm_demosaic_3channel(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    dst=None, buffer_provider="pool"
):
    """Full-Luma MLRI-ADMM Demosaic to Grayscale 1-channel."""
    from ..common import _get_aot
    aot = _get_aot()
    if not aot or not hasattr(aot, "mlri_admm_demosaic_3channel"):
        import taichi_vision.taichi_aot as ta_aot
        aot = ta_aot
        
    is_taichi = hasattr(bayer, "to_numpy") or hasattr(cmatrix, "to_numpy")
    res_buf = aot.mlri_admm_demosaic_3channel(
        bayer, float(wb_r), float(wb_g1), float(wb_b), float(wb_g2),
        cmatrix, float(black_level), float(white_level),
        int(c00), int(c01), int(c10), int(c11),
        return_gpu=is_taichi,
        dst=dst
    )
    return res_buf
