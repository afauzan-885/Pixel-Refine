# shared_kernels.py - Reusable @ti.kernel for Optical Flow Algorithms
# Contains pyramid-level kernels shared across all flow paradigms.
# Import this module in your algorithm file:
#   from .aot.shared_kernels import upsample_flow_bicubic_kernel, downsample_2x_kernel

import taichi as ti
from .shared_math import bicubic_weight, clamp_coord


@ti.kernel
def upsample_flow_bicubic_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
    scale: ti.f32,
):
    """
    Upsamples motion vector field hierarchically between pyramid levels
    using bicubic interpolation.
    
    Used by ALL optical flow paradigms when building multi-level pyramids.
    
    Args:
        src: Source flow field at lower resolution (H_src x W_src x 2)
        dst: Destination flow field at higher resolution (H_dst x W_dst x 2)
        scale: Upsampling scale factor (typically 2.0 for 2x pyramid)
    """
    h_src, w_src = src.shape[0], src.shape[1]
    h_dst, w_dst = dst.shape[0], dst.shape[1]

    for i, j in ti.ndrange(h_dst, w_dst):
        # Map destination coordinates to source space
        y_src = float(i) / scale
        x_src = float(j) / scale

        # Integer and fractional parts for bicubic interpolation
        y_int = ti.floor(y_src, ti.i32)
        x_int = ti.floor(x_src, ti.i32)
        y_fract = y_src - float(y_int)
        x_fract = x_src - float(x_int)

        # Interpolate both flow components (u, v) using bicubic kernel
        for k in ti.static(range(2)):
            val = 0.0
            for m in ti.static(range(-1, 3)):
                for n in ti.static(range(-1, 3)):
                    yy = clamp_coord(y_int + m, 0, h_src - 1)
                    xx = clamp_coord(x_int + n, 0, w_src - 1)
                    w_m = bicubic_weight(float(m) - y_fract)
                    w_n = bicubic_weight(float(n) - x_fract)
                    val += src[yy, xx, k] * w_m * w_n
            dst[i, j, k] = val * scale


@ti.kernel
def downsample_2x_kernel(
    src: ti.types.ndarray(),
    dst: ti.types.ndarray(),
):
    """
    Downsamples an image or field by factor 2 using box averaging.
    Useful for building image pyramids at compile-time or for
    algorithms that need coarser input representations.
    
    Args:
        src: Source field (H x W) or (H x W x C)
        dst: Downsampled output (H/2 x W/2) or (H/2 x W/2 x C)
    """
    for i, j in dst:
        dst[i, j] = (
            src[2 * i, 2 * j]
            + src[2 * i + 1, 2 * j]
            + src[2 * i, 2 * j + 1]
            + src[2 * i + 1, 2 * j + 1]
        ) * 0.25
