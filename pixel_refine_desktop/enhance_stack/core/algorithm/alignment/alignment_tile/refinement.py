# refinement.py - Pure AOT Kernels for Flow Refinement
# Reference: alignment_tile.cpp (_parabolic_subpixel_refinement_kernel)

import taichi as ti

@ti.func
def parabolic_refinement(c_m1, c_0, c_p1):
    """
    Sub-pixel refinement using parabolic fitting.
    Returns delta offset in range [-0.5, 0.5]
    """
    delta = 0.0
    denom = 2.0 * (c_p1 + c_m1 - 2.0 * c_0)
    if ti.abs(denom) > 1e-6:
        delta = -(c_p1 - c_m1) / denom
    return ti.max(-0.5, ti.min(0.5, delta))

@ti.kernel
def apply_parabolic_refinement_kernel(flow: ti.types.ndarray(), 
                                     costs: ti.types.ndarray(),
                                     refined_flow: ti.types.ndarray()):
    # Placeholder for sub-pixel refinement integration
    pass
