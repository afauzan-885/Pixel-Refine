# shared_math.py - Device-side Math Functions for Optical Flow Algorithms
# Reusable @ti.func utilities shared across all flow paradigms.
# Import this module in your algorithm file:
#   from .aot.shared_math import bicubic_weight, clamp_coord, bilinear_sample

import taichi as ti


@ti.func
def bicubic_weight(x: ti.f32) -> ti.f32:
    """
    Weight function for bicubic interpolation (Catmull-Rom spline).
    Used for upsampling flow fields between pyramid levels.
    
    Args:
        x: Distance from sample point (typically in range [-2, 2])
    Returns:
        Bicubic weight value
    """
    abs_x = ti.abs(x)
    res = 0.0
    if abs_x <= 1.0:
        res = 1.5 * abs_x**3 - 2.5 * abs_x**2 + 1.0
    elif abs_x < 2.0:
        res = -0.5 * abs_x**3 + 2.5 * abs_x**2 - 4.0 * abs_x + 2.0
    return res


@ti.func
def clamp_coord(val: ti.i32, lo: ti.i32, hi: ti.i32) -> ti.i32:
    """
    Boundary-safe coordinate clamp. Prevents out-of-bounds memory access.
    
    Args:
        val: Coordinate value to clamp
        lo: Minimum bound (inclusive)
        hi: Maximum bound (inclusive)
    Returns:
        Clamped coordinate within [lo, hi]
    """
    return ti.max(lo, ti.min(val, hi))


@ti.func
def bilinear_sample(
    field: ti.types.ndarray(),
    y: ti.f32,
    x: ti.f32,
    h: ti.i32,
    w: ti.i32,
) -> ti.f32:
    """
    Generic sub-pixel sampling using bilinear interpolation.
    Useful for variational methods (Horn-Schunck, Lucas-Kanade) that need
    to sample flow/gradient fields at non-integer coordinates.
    
    Args:
        field: 2D input field (height x width)
        y, x: Sub-pixel coordinates to sample at
        h, w: Field dimensions
    Returns:
        Interpolated value at (y, x)
    """
    y_int = ti.floor(y, ti.i32)
    x_int = ti.floor(x, ti.i32)
    y_frac = y - float(y_int)
    x_frac = x - float(x_int)

    # Clamp integer coordinates to valid range
    y0 = clamp_coord(y_int, 0, h - 1)
    y1 = clamp_coord(y_int + 1, 0, h - 1)
    x0 = clamp_coord(x_int, 0, w - 1)
    x1 = clamp_coord(x_int + 1, 0, w - 1)

    # Bilinear interpolation
    val = (
        field[y0, x0] * (1.0 - y_frac) * (1.0 - x_frac)
        + field[y1, x0] * y_frac * (1.0 - x_frac)
        + field[y0, x1] * (1.0 - y_frac) * x_frac
        + field[y1, x1] * y_frac * x_frac
    )
    return val
