"""
Joint Bilateral Guidance - Taichi GPU Implementation
=====================================================
Highly optimized standalone module for refining flow or weight maps 
using a reference image as guidance.

Process: Joint Bilateral Refinement (JBR)
Logic: 5x5 window, spatial Gaussian weighting + range color similarity weighting.
"""

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
    
    @ti.func
    def _compute_jbr_weight(dx: int, dy: int, diff: float) -> float:
        """
        Compute Joint Bilateral weight for a neighbor.
        Combined Spatial Gaussian (sigma=1.0) and Range (sigma=0.02) weights.
        """
        # Spatial Gaussian weights (Precomputed for 5x5 sigma=1.0)
        w_s = 0.0
        adx, ady = abs(dx), abs(dy)
        if adx == 2:
            if ady == 2: w_s = 0.002969
            elif ady == 1: w_s = 0.013306
            else: w_s = 0.021938
        elif adx == 1:
            if ady == 2: w_s = 0.013306
            elif ady == 1: w_s = 0.059634
            else: w_s = 0.098320
        else:
            if ady == 2: w_s = 0.021938
            elif ady == 1: w_s = 0.098320
            else: w_s = 0.162103
            
        # Range weight: exp(-(diff^2) / (2 * 0.02^2)) => exp(-diff^2 * 1250.0)
        # Note: Warp.py used 50.0 which corresponds to larger sigma. 
        # C++ uses 1/0.02 which is 50.0 if applied BEFORE squaring? 
        # Warp.py: ti.exp(-(diff * diff) * 50.0)
        return w_s * ti.exp(-(diff * diff) * 50.0)

    @ti.kernel
    def joint_bilateral_refinement_i32_2d_kernel(
        flow_in: ti.types.ndarray(dtype=ti.f32, ndim=3),
        ref_i32: ti.types.ndarray(dtype=ti.i32, ndim=2),
        flow_out: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: int,
        w: int,
        inv_norm: float,
    ):
        """
        Standalone JBR Kernel for Grayscale Reference.
        Refines a 2D flow field (u, v) using grayscale guidance.
        """
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12
            sum_u, sum_v = 0.0, 0.0
            center_val = float(ref_i32[y, x]) * inv_norm

            for dy in ti.static(range(-2, 3)):
                ny = tm.clamp(y + dy, 0, h - 1)
                for dx in ti.static(range(-2, 3)):
                    nx = tm.clamp(x + dx, 0, w - 1)

                    val_neighbor = float(ref_i32[ny, nx]) * inv_norm
                    diff = val_neighbor - center_val
                    
                    w_curr = _compute_jbr_weight(dx, dy, diff)
                    
                    sum_u += flow_in[ny, nx, 0] * w_curr
                    sum_v += flow_in[ny, nx, 1] * w_curr
                    total_w += w_curr

            flow_out[y, x, 0] = sum_u / total_w
            flow_out[y, x, 1] = sum_v / total_w

    @ti.kernel
    def joint_bilateral_refinement_i32_3d_kernel(
        flow_in: ti.types.ndarray(dtype=ti.f32, ndim=3),
        ref_i32: ti.types.ndarray(dtype=ti.i32, ndim=3),
        flow_out: ti.types.ndarray(dtype=ti.f32, ndim=3),
        h: int,
        w: int,
        inv_norm: float,
    ):
        """
        Standalone JBR Kernel for RGB Reference (Uses Green Channel).
        """
        for y, x in ti.ndrange(h, w):
            total_w = 1e-12
            sum_u, sum_v = 0.0, 0.0
            center_val = float(ref_i32[y, x, 1]) * inv_norm

            for dy in ti.static(range(-2, 3)):
                ny = tm.clamp(y + dy, 0, h - 1)
                for dx in ti.static(range(-2, 3)):
                    nx = tm.clamp(x + dx, 0, w - 1)

                    val_neighbor = float(ref_i32[ny, nx, 1]) * inv_norm
                    diff = val_neighbor - center_val
                    
                    w_curr = _compute_jbr_weight(dx, dy, diff)
                    
                    sum_u += flow_in[ny, nx, 0] * w_curr
                    sum_v += flow_in[ny, nx, 1] * w_curr
                    total_w += w_curr

            flow_out[y, x, 0] = sum_u / total_w
            flow_out[y, x, 1] = sum_v / total_w

    def apply_joint_bilateral_refinement_gpu(flow_in, reference, buffer_provider="pool"):
        """
        Python wrapper for JBR process.
        """
        if not TAICHI_AVAILABLE:
            raise ImportError("Taichi not available")

        h, w = flow_in.shape[:2]
        
        # Ensure inputs are on GPU
        flow_gpu, flow_is_temp = common.ensure_taichi_field(flow_in, dtype=ti.f32, buffer_provider=buffer_provider)
        ref_gpu, ref_is_temp = common.ensure_taichi_field(reference, dtype=ti.i32, buffer_provider=buffer_provider)
        
        # Prepare output
        flow_out_gpu = common.get_temp_buffer((h, w, 2), ti.f32, buffer_provider)
        
        # Determine normalization
        inv_norm = 1.0 / 65535.0 # Default for u16/i32 parity
        
        # Dispatch
        if len(ref_gpu.shape) == 2:
            joint_bilateral_refinement_i32_2d_kernel(flow_gpu, ref_gpu, flow_out_gpu, h, w, inv_norm)
        else:
            joint_bilateral_refinement_i32_3d_kernel(flow_gpu, ref_gpu, flow_out_gpu, h, w, inv_norm)
        
        # Cleanup
        if flow_is_temp: common.release_temp_buffer(flow_gpu)
        if ref_is_temp: common.release_temp_buffer(ref_gpu)
        
        return flow_out_gpu

else:
    def apply_joint_bilateral_refinement_gpu(*args, **kwargs):
        raise ImportError("Taichi not available")
