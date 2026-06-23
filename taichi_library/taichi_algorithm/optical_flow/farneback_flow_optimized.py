# farneback_flow_optimized.py - Optimized Farneback Optical Flow with Aggressive Optimizations
#
# Optimizations for 5ms target on 512×512:
# 1. Half-resolution processing: Compute at 256×256, upscale flow to 512×512
# 2. Reduced parameters: win_size=5, iterations=1, levels=1-2
# 3. Optional refinement at full resolution (1 iteration)
#
# Usage:
#     fb = FarnebackFlowOptimized()
#     flow = fb.compute_flow(ref_f32, comp_f32)  # Returns 512×512 flow

import os
import sys
import numpy as np

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
    from .. import common
    from ..taichi_worker import ti_thread
except ImportError:
    pass


# =============================================================================
# Public API
# =============================================================================

class FarnebackFlowOptimized:
    """
    Optimized Farneback optical flow with hybrid approach.
    
    Optimization strategies:
    1. Hybrid pyramid: levels=1 coarse estimation + levels=2 refinement
    2. Reduced parameters: win_size=5, iterations=1-2
    3. Optional box filter for faster smoothing
    
    Usage:
        fb = FarnebackFlowOptimized()
        flow = fb.compute_flow(ref_f32, comp_f32)
    """
    
    def __init__(self, fast_mode=True):
        """
        Args:
            fast_mode: If True, use aggressive optimizations (faster, slightly less accurate)
                      If False, use balanced optimizations (slower, more accurate)
        """
        from taichi_library.taichi_aot.engine import AOTEngine
        
        self.engine = AOTEngine()
        
        # Load TCM modules
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tcm_dir = os.path.join(base_dir, "../../../aot_tcm")
        
        self.mod = self.engine.load(os.path.join(tcm_dir, "farneback_flow_vulkan.tcm"))
        self.pyramid_mod = self.engine.load(os.path.join(tcm_dir, "pyramid_vulkan.tcm"))
        
        self.fast_mode = fast_mode
        
        # Pre-compute constants
        if fast_mode:
            # Aggressive: smaller window, fewer iterations
            self.win_size = 5
            self.poly_n = 5
            self.poly_sigma = 1.2
            self.coarse_iters = 1
            self.fine_iters = 1
        else:
            # Balanced: larger window, more iterations
            self.win_size = 7
            self.poly_n = 5
            self.poly_sigma = 1.2
            self.coarse_iters = 2
            self.fine_iters = 1
        
        self._prepare_constants()
    
    def _prepare_constants(self):
        """Pre-compute and upload constant buffers."""
        import ctypes
        from taichi_library.taichi_algorithm.optical_flow.farneback_flow import (
            prepare_gaussian_constants,
            compute_smoothing_weights,
        )
        
        # Polynomial expansion constants
        g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(
            self.poly_n, self.poly_sigma
        )
        self.poly_radius = self.poly_n // 2
        self.ig11, self.ig03, self.ig33, self.ig55 = ig11, ig03, ig33, ig55
        
        self.g_gpu = self.engine.upload(g_w.astype(np.float32))
        self.xg_gpu = self.engine.upload(xg_w.astype(np.float32))
        self.xxg_gpu = self.engine.upload(xxg_w.astype(np.float32))
        
        # Smoothing weights
        smooth_w, smooth_radius = compute_smoothing_weights(self.win_size)
        self.smooth_radius = smooth_radius
        self.smooth_gpu = self.engine.upload(smooth_w.astype(np.float32))
    
    def _build_pyramid(self, img_gpu, n_levels):
        """Build image pyramid."""
        pyramid = [img_gpu]
        current = img_gpu
        for _ in range(n_levels - 1):
            h, w = current.shape[0], current.shape[1]
            next_h, next_w = h // 2, w // 2
            if next_h < 32 or next_w < 32:
                break
            next_buf = self.engine.allocate((next_h, next_w), dtype=np.float32)
            self.pyramid_mod.run("downsample_2x_f32", src=current, dst=next_buf)
            pyramid.append(next_buf)
            current = next_buf
        return pyramid
    
    def _run_iterations(self, ref_pyramid, comp_pyramid, flow_bufs, num_iters):
        """Run Farneback iterations at all pyramid levels."""
        num_levels = len(ref_pyramid)
        win_radius = self.win_size // 2
        
        # Per-level configuration
        level_configs = []
        for lvl in range(num_levels):
            if lvl >= num_levels - 1:  # Coarsest
                level_configs.append((num_iters, 1))  # poly_n=7
            elif lvl >= num_levels - 2:  # Second coarsest
                level_configs.append((max(1, num_iters - 1), 0))  # poly_n=5
            else:  # Finer
                level_configs.append((max(1, num_iters - 2), 0))  # poly_n=5
        
        poly_filters = {0: self.poly_filters_5, 1: self.poly_filters_7}
        
        # Coarse-to-fine
        for lvl in range(num_levels - 1, -1, -1):
            # Upsample flow from coarser level
            if lvl < num_levels - 1:
                self.mod.run("upsample_flow",
                            flow_coarse=flow_bufs[lvl + 1],
                            flow_fine=flow_bufs[lvl],
                            scale=2.0)
            
            # Run iterations at this level
            iters, poly_idx = level_configs[lvl]
            pf = poly_filters[poly_idx]
            
            # Use batched multi-iteration graphs
            remaining = iters
            while remaining > 0:
                if remaining >= 5:
                    batch_key = "farneback_multi_5"
                    batch_size = 5
                elif remaining >= 3:
                    batch_key = "farneback_multi_3"
                    batch_size = 3
                elif remaining >= 2:
                    batch_key = "farneback_multi_2"
                    batch_size = 2
                else:
                    batch_key = "farneback_iteration"
                    batch_size = 1
                
                self.mod.run(batch_key,
                            ref=ref_pyramid[lvl], comp=comp_pyramid[lvl],
                            flow=flow_bufs[lvl], warped_comp=self.warped_bufs[lvl],
                            tensors=self.tensor_bufs[lvl], smooth_tensors=self.smooth_bufs[lvl],
                            poly_filters=pf, gaussian_weights=self.smooth_gpu,
                            win_radius=int(win_radius), poly_n=int(self.poly_n))
                remaining -= batch_size
    
    def compute_flow(self, ref_f32, comp_f32, half_resolution=True, refine=True):
        """
        Compute optical flow between two float32 images.
        
        Args:
            ref_f32: Reference image (H, W) float32 [0, 255]
            comp_f32: Comparison image (H, W) float32 [0, 255]
            half_resolution: If True, compute at half resolution then upscale (faster)
            refine: If True and half_resolution=True, run 1 refinement iteration at full resolution
        
        Returns:
            flow: (H, W, 2) float32 flow field (OpenCV convention)
        """
        import cv2
        
        h, w = ref_f32.shape
        
        if half_resolution and h >= 256 and w >= 256:
            # HALF-RESOLUTION MODE
            # Step 1: Downsample to half resolution
            h_half, w_half = h // 2, w // 2
            ref_half = cv2.resize(ref_f32, (w_half, h_half), interpolation=cv2.INTER_AREA)
            comp_half = cv2.resize(comp_f32, (w_half, h_half), interpolation=cv2.INTER_AREA)
            
            # Step 2: Compute flow at half resolution
            flow_half = self._compute_flow_impl(ref_half, comp_half, n_levels=1)
            
            # Step 3: Upscale flow to full resolution
            flow_full = cv2.resize(flow_half, (w, h), interpolation=cv2.INTER_LINEAR)
            flow_full *= 2.0  # Scale flow values by 2x
            
            if refine:
                # Step 4: Optional refinement at full resolution (1 iteration)
                flow_full = self._refine_flow(ref_f32, comp_f32, flow_full)
            
            return flow_full
        else:
            # FULL RESOLUTION MODE
            return self._compute_flow_impl(ref_f32, comp_f32, n_levels=2)
    
    def _compute_flow_impl(self, ref_f32, comp_f32, n_levels=2):
        """
        Internal implementation for flow computation.
        
        Args:
            ref_f32: Reference image (H, W) float32 [0, 255]
            comp_f32: Comparison image (H, W) float32 [0, 255]
            n_levels: Number of pyramid levels
        
        Returns:
            flow: (H, W, 2) float32 flow field
        """
        import ctypes
        
        h, w = ref_f32.shape
        
        # Upload images
        ref_gpu = self.engine.upload(ref_f32.astype(np.float32))
        comp_gpu = self.engine.upload(comp_f32.astype(np.float32))
        
        # Prepare poly filters
        from taichi_library.taichi_algorithm.optical_flow.farneback_flow import (
            prepare_gaussian_constants,
            compute_smoothing_weights,
        )
        
        g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(
            self.poly_n, self.poly_sigma
        )
        
        self.g_gpu = self.engine.upload(g_w.astype(np.float32))
        self.xg_gpu = self.engine.upload(xg_w.astype(np.float32))
        self.xxg_gpu = self.engine.upload(xxg_w.astype(np.float32))
        
        # Smoothing weights
        smooth_w, smooth_radius = compute_smoothing_weights(self.win_size)
        self.smooth_gpu = self.engine.upload(smooth_w.astype(np.float32))
        
        # Build pyramids
        ref_pyramid = self._build_pyramid(ref_gpu, n_levels=n_levels)
        comp_pyramid = self._build_pyramid(comp_gpu, n_levels=n_levels)
        
        num_levels = len(ref_pyramid)
        win_radius = self.win_size // 2
        
        # Allocate scratch buffers
        warped_bufs = []
        tensor_bufs = []
        smooth_bufs = []
        flow_bufs = []
        
        for lvl in range(num_levels):
            h_l, w_l = ref_pyramid[lvl].shape[0], ref_pyramid[lvl].shape[1]
            flow_bufs.append(self.engine.allocate((h_l, w_l, 2), dtype=np.float32))
            warped_bufs.append(self.engine.allocate((h_l, w_l), dtype=np.float32))
            tensor_bufs.append(self.engine.allocate((h_l, w_l, 5), dtype=np.float32))
            smooth_bufs.append(self.engine.allocate((h_l, w_l, 5), dtype=np.float32))
        
        # Clear flow at coarsest level
        self.mod.run("farneback_clear_flow", flow=flow_bufs[-1])
        
        # Coarse-to-fine
        for lvl in range(num_levels - 1, -1, -1):
            # Upsample flow from coarser level
            if lvl < num_levels - 1:
                self.mod.run("upsample_flow",
                            flow_coarse=flow_bufs[lvl + 1],
                            flow_fine=flow_bufs[lvl],
                            scale=2.0)
            
            # Run iterations at this level
            for _ in range(self.coarse_iters):
                self.mod.run("farneback_iteration",
                            ref=ref_pyramid[lvl], comp=comp_pyramid[lvl],
                            flow=flow_bufs[lvl], warped_comp=warped_bufs[lvl],
                            tensors=tensor_bufs[lvl], smooth_tensors=smooth_bufs[lvl],
                            poly_filters=self.poly_filters_5, gaussian_weights=self.smooth_gpu,
                            win_radius=int(win_radius), poly_n=int(self.poly_n))
        
        # Download result
        self.engine.sync()
        flow_np = flow_bufs[0].to_numpy()
        
        # Cleanup
        for buf_list in [ref_pyramid, comp_pyramid, flow_bufs, 
                        warped_bufs, tensor_bufs, smooth_bufs]:
            for buf in buf_list:
                try:
                    buf.destroy()
                except Exception:
                    pass
        for buf in [ref_gpu, comp_gpu, self.g_gpu, self.xg_gpu, self.xxg_gpu, self.smooth_gpu]:
            try:
                buf.destroy()
            except Exception:
                pass
        
        return flow_np
    
    def _refine_flow(self, ref_f32, comp_f32, flow_init):
        """
        Refine flow at full resolution with 1 iteration.
        
        Args:
            ref_f32: Reference image (H, W) float32 [0, 255]
            comp_f32: Comparison image (H, W) float32 [0, 255]
            flow_init: Initial flow estimate (H, W, 2) float32
        
        Returns:
            flow: Refined flow (H, W, 2) float32
        """
        import ctypes
        
        h, w = ref_f32.shape
        
        # Upload images
        ref_gpu = self.engine.upload(ref_f32.astype(np.float32))
        comp_gpu = self.engine.upload(comp_f32.astype(np.float32))
        
        # Upload initial flow
        flow_gpu = self.engine.allocate((h, w, 2), dtype=np.float32)
        # Copy flow_init to GPU
        ptr = flow_gpu.map()
        ctypes.memmove(ptr, np.ascontiguousarray(flow_init).ctypes.data, flow_gpu.size_bytes)
        flow_gpu.unmap()
        
        # Prepare constants
        from taichi_library.taichi_algorithm.optical_flow.farneback_flow import (
            prepare_gaussian_constants,
            compute_smoothing_weights,
        )
        
        g_w, xg_w, xxg_w, ig11, ig03, ig33, ig55 = prepare_gaussian_constants(
            self.poly_n, self.poly_sigma
        )
        
        self.g_gpu = self.engine.upload(g_w.astype(np.float32))
        self.xg_gpu = self.engine.upload(xg_w.astype(np.float32))
        self.xxg_gpu = self.engine.upload(xxg_w.astype(np.float32))
        
        # Smoothing weights
        smooth_w, smooth_radius = compute_smoothing_weights(self.win_size)
        self.smooth_gpu = self.engine.upload(smooth_w.astype(np.float32))
        
        # Allocate scratch buffers
        warped_buf = self.engine.allocate((h, w), dtype=np.float32)
        tensor_buf = self.engine.allocate((h, w, 5), dtype=np.float32)
        smooth_buf = self.engine.allocate((h, w, 5), dtype=np.float32)
        
        win_radius = self.win_size // 2
        
        # Run 1 refinement iteration
        self.mod.run("farneback_iteration",
                    ref=ref_gpu, comp=comp_gpu,
                    flow=flow_gpu, warped_comp=warped_buf,
                    tensors=tensor_buf, smooth_tensors=smooth_buf,
                    poly_filters=self.poly_filters_5, gaussian_weights=self.smooth_gpu,
                    win_radius=int(win_radius), poly_n=int(self.poly_n))
        
        # Download result
        self.engine.sync()
        flow_np = flow_gpu.to_numpy()
        
        # Cleanup
        for buf in [ref_gpu, comp_gpu, flow_gpu, warped_buf, tensor_buf, smooth_buf,
                   self.g_gpu, self.xg_gpu, self.xxg_gpu, self.smooth_gpu]:
            try:
                buf.destroy()
            except Exception:
                pass
        
        return flow_np
