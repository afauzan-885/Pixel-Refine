"""Hamilton-Adams GPU-Accelerated RAW Demosaicing (Strict C++ AOT-Only Module)

Dispatches hamilton_demosaic (linear + highlight recovery + DR compression)
or hamilton_demosaic_tonemapped (full sRGB) graphs via the AOT TCM engine.
"""

import os
import numpy as np


def hamilton(
    bayer, wb_r, wb_g1, wb_b, wb_g2, cmatrix,
    black_level, white_level, c00, c01, c10, c11,
    tonemapping=False, return_gpu=False, dst=None, buffer_provider="pool",
):
    """GPU-Accelerated 3-Pass Hamilton-Adams Demosaicing.

    Args:
        bayer:           Input RAW Bayer sensor image - NumPy array OR Taichi ndarray. (H, W)
        wb_r, wb_g1,
        wb_b, wb_g2:     Normalized White Balance gains for R, G1, B, G2.
        cmatrix:         3x3 Camera-to-sRGB conversion matrix.
        black_level:     Sensor black level (float).
        white_level:     Sensor white saturation level (float).
        c00, c01,
        c10, c11:        Bayer pattern 2x2 grid values (0=R, 1=G, 2=B, 3=G).
        tonemapping:     If True, applies sRGB color matrix & sigmoid tonemapping.
                         Default False (Linear output with DR compression).
        return_gpu:      If True, return GPU buffer instead of NumPy array.
        dst:             Optional pre-allocated destination buffer (H, W, 3).
        buffer_provider: Unused, kept for API compatibility.

    Returns:
        Demosaiced RGB image as NumPy float32 array (H, W, 3) or GPU buffer.
    """
    # Import engine primitives directly to avoid circular import through aot_api
    from taichi_library.taichi_aot.engine import (
        engine,
        InputArray,
        OutputArray,
    )
    from taichi_library.taichi_algorithm.aot_api import _mod

    bayer_buf = InputArray(bayer)
    cmatrix_buf = InputArray(cmatrix)

    h, w = bayer_buf.shape[:2]

    # Intermediate GPU buffers
    wb_bayer_buf = engine.allocate((h, w), dtype=np.float32)
    green_buf = engine.allocate((h, w), dtype=np.float32)

    # Destination output RGB float32 buffer
    if dst is not None and dst.shape == (h, w, 3) and dst.dtype == np.float32:
        dst_buf = dst
    else:
        dst_buf = OutputArray((h, w, 3), dtype=np.float32)

    # Select graph based on tonemapping flag
    graph_name = "hamilton_demosaic_tonemapped" if tonemapping else "hamilton_demosaic"

    _mod("hamilton").run(
        graph_name,
        bayer=bayer_buf,
        wb_bayer=wb_bayer_buf,
        green=green_buf,
        cmatrix=cmatrix_buf,
        dst=dst_buf,
        wb_r=float(wb_r),
        wb_g1=float(wb_g1),
        wb_b=float(wb_b),
        wb_g2=float(wb_g2),
        black=float(black_level),
        white=float(white_level),
        h=int(h),
        w=int(w),
        c00=int(c00),
        c01=int(c01),
        c10=int(c10),
        c11=int(c11),
    )

    engine.sync()

    # Cleanup intermediate buffers
    try:
        wb_bayer_buf.release()
    except Exception:
        pass
    try:
        green_buf.release()
    except Exception:
        pass
    if bayer_buf is not bayer and hasattr(bayer_buf, "release"):
        try:
            bayer_buf.release()
        except Exception:
            pass

    return dst_buf if return_gpu else dst_buf.to_numpy()


def hamilton_demosaic(*args, **kwargs):
    """Compatibility entrypoint for the historical public name."""
    return hamilton(*args, **kwargs)
