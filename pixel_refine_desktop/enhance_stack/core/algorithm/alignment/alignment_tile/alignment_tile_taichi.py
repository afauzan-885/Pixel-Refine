"""
Taichi Dual Backend Architecture - JIT & AOT Support
====================================================
This module provides a unified interface for image alignment:
1. DEVELOPMENT Mode (JIT): Uses Taichi Python kernels (Just-in-Time).
2. PRODUCTION Mode (AOT): Uses C++ Modular TiRT Backend (Ahead-of-Time).

Controlled by os.environ["PIXEL_REFINE_BACKEND"]
"""

import os
import numpy as np
import ctypes
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
    ti_thread,
)

# --- JIT Dependencies ---
try:
    import taichi as ti
    from ...taichi_algorithm import common, warp, preprocess, bilinear_interpolation
    from .compute_flow import compute_alignment_flow

    TAICHI_JIT_AVAILABLE = True
except ImportError:
    TAICHI_JIT_AVAILABLE = False
    ti = None

# Global flag for other modules to detect if Taichi-based alignment is supported
# It's True if either JIT is possible or if we are in PRODUCTION mode (AOT)
TAICHI_AVAILABLE = TAICHI_JIT_AVAILABLE or (
    os.environ.get("PIXEL_REFINE_BACKEND") == "PRODUCTION"
)


# ============================================================================
# 1. PRODUCTION BACKEND (AOT via C++ TiRT Bridge)
# ============================================================================
class AlignmentTileTaichiAOT:
    """Production-ready AOT alignment backend using C++ TiRT Bridge."""

    def __init__(self, data_dir=None, arch="vulkan"):
        self.arch = arch
        # Jika data_dir tidak diberikan, asumsikan default
        if data_dir is None:
            # Let's find pixel_refine_desktop folder reliably
            curr = os.path.abspath(__file__)
            # Go up until we find enhance_stack or reached root
            while "enhance_stack" in curr:
                curr = os.path.dirname(curr)
            
            # Now curr should be pixel_refine_desktop folder
            data_dir = os.path.join(curr, "ui", "data")

        self.data_dir = data_dir
        # Path DLL di ui/data
        self.lib_path = os.path.abspath(os.path.join(data_dir, "preprocessing_aot.dll"))
        # Path AOT Module di ui/data/aot_assets/preprocess
        self.aot_module_path = os.path.abspath(os.path.join(data_dir, "aot_assets", "preprocess"))

        self.lib = None
        self.initialized = False
        self.ref_img_gpu = None
        self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0

        # Try to load the library
        try:
            if os.path.exists(self.lib_path):
                self.lib = ctypes.CDLL(self.lib_path)

                # Define function signatures
                if hasattr(self.lib, "init_taichi_aot_runtime"):
                    self.lib.init_taichi_aot_runtime.argtypes = [ctypes.c_char_p]
                    self.lib.init_taichi_aot_runtime.restype = ctypes.c_int

                if hasattr(self.lib, "compute_preprocess_aot"):
                    self.lib.compute_preprocess_aot.argtypes = [
                        ctypes.POINTER(ctypes.c_int32),  # src_ptr
                        ctypes.POINTER(ctypes.c_float),  # dst_ptr
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int,  # src h, w, c
                        ctypes.c_int,
                        ctypes.c_int,  # dst h, w
                        ctypes.c_float, # scale_norm
                        ctypes.c_int,   # apply_gamma
                        ctypes.c_float, # scale_gamma
                        ctypes.c_float, # gamma_pow
                        ctypes.c_float, # slope
                        ctypes.c_float, # cutoff
                        ctypes.c_int,   # use_sharpen
                    ]
                    self.lib.compute_preprocess_aot.restype = ctypes.c_int

                # Initialize runtime if supported
                if hasattr(self.lib, "init_taichi_aot_runtime"):
                    res = self.lib.init_taichi_aot_runtime(
                        self.aot_module_path.encode("utf-8")
                    )
                    if res == 0:
                        self.initialized = True
                        print(
                            f"[TaichiAOT] Mode: PRODUCTION (AOT) initialized on {self.arch.upper()}"
                        )
                    else:
                        print(f"[TaichiAOT] Initialization failed with code: {res}")

                # Configure Modular TiRT signatures
                if hasattr(self.lib, "set_preprocess_config_modular_tirt"):
                    self.lib.set_preprocess_config_modular_tirt.argtypes = [ctypes.c_float, ctypes.c_int]
                    self.lib.set_preprocess_config_modular_tirt.restype = ctypes.c_int

                if hasattr(self.lib, "set_alignment_config_modular_tirt"):
                    self.lib.set_alignment_config_modular_tirt.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int]
                    self.lib.set_alignment_config_modular_tirt.restype = ctypes.c_int

                if hasattr(self.lib, "init_alignment_modular_tirt"):
                    res = self.lib.init_alignment_modular_tirt(self.arch.encode("utf-8"), self.data_dir.encode("utf-8"))
                    if res == 0:
                        self.initialized = True
            else:
                print(f"[TaichiAOT] DLL not found at: {self.lib_path}")
        except Exception as e:
            print(f"[TaichiAOT] Error loading AOT bridge: {e}")

    def set_reference(self, ref_img, work_h, work_w, is_linear=False, proxy_scale=1.0, use_sharpen=False, **kwargs):
        """Preprocess reference image using AOT GPU pipeline."""
        if not self.initialized:
            return
        
        self.ref_img_gpu, _ = common.ensure_taichi_field(ref_img, buffer_provider="pool")
        self.work_h, self.work_w = work_h, work_w
        # Parity logic: For hybrid AOT-JIT, we still need ref_work_res for JIT compute_flow
        # but in production TiRT it would all be in C++.
        # Let's perform JIT preprocessing for now to ensure flow works.
        self.ref_work_res = preprocess.preprocess_pipeline_gpu(
            ref_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(work_h, work_w),
            buffer_provider="pool", return_numpy=False
        )

    def compute_alignment_and_warp(self, comp_img, tile_h, tile_w, n_layers, is_linear=False, proxy_scale=1.0, use_sharpen=False, search_dist=2.0, return_format="numpy_u16", **kwargs):
        if not self.initialized or self.ref_work_res is None:
            return None

        full_h, full_w = comp_img.shape[:2]
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")

        # Preprocess Comparison frame
        comp_work_res = preprocess.preprocess_pipeline_gpu(
            comp_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(self.work_h, self.work_w),
            buffer_provider="pool", return_numpy=False
        )

        # Compute Flow (JIT)
        flow_low_gpu = compute_alignment_flow(self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist)
        common.release_temp_buffer(comp_work_res)

        if flow_low_gpu is None:
            common.release_temp_buffer(comp_img_gpu)
            return None

        # Upsample Flow (JIT)
        flow_full_gpu = common.get_temp_buffer((full_h, full_w, 2), ti.f32, buffer_provider="pool")
        self._resize_flow_gpu(flow_low_gpu, flow_full_gpu, full_w / self.work_w, full_h / self.work_h)
        common.release_temp_buffer(flow_low_gpu)

        # Warp (JIT)
        warped_img_gpu = warp.warp_image_gpu(comp_img_gpu, flow_full_gpu, guidance=self.ref_img_gpu)
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)

        # Dispatch output
        is_taichi_ndarray = hasattr(warped_img_gpu, "to_numpy")
        if return_format == "numpy_f32":
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.float32) / 65535.0
            if is_taichi_ndarray: common.release_temp_buffer(warped_img_gpu)
            return result
        else: # "numpy_u16"
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.uint16)
            if is_taichi_ndarray: common.release_temp_buffer(warped_img_gpu)
            return result

    def _resize_flow_gpu(self, src, dst, sx, sy):
        @ti.kernel
        def _resize_k(s: ti.types.ndarray(), d: ti.types.ndarray(), x: float, y: float):
            for r, c in ti.ndrange(d.shape[0], d.shape[1]):
                u, v = (c + 0.5) / d.shape[1], (r + 0.5) / d.shape[0]
                sr, sc = v * s.shape[0] - 0.5, u * s.shape[1] - 0.5
                r0, c0 = int(ti.floor(sr)), int(ti.floor(sc))
                fr, fc = sr - r0, sc - c0
                r0, r1 = ti.max(0, ti.min(r0, s.shape[0] - 2)), ti.max(0, ti.min(r0 + 1, s.shape[0] - 1))
                c0, c1 = ti.max(0, ti.min(c0, s.shape[1] - 2)), ti.max(0, ti.min(c0 + 1, s.shape[1] - 1))
                for i in ti.static(range(2)):
                    v00, v01, v10, v11 = s[r0, c0, i], s[r0, c1, i], s[r1, c0, i], s[r1, c1, i]
                    val = v00*(1-fc)*(1-fr) + v01*fc*(1-fr) + v10*(1-fc)*fr + v11*fc*fr
                    d[r, c, i] = val * (x if i == 0 else y)
        _resize_k(src, dst, sx, sy)

    def clear_data(self):
        if self.ref_img_gpu: common.release_temp_buffer(self.ref_img_gpu); self.ref_img_gpu = None
        if self.ref_work_res: common.release_temp_buffer(self.ref_work_res); self.ref_work_res = None
        common.cleanup_cache()


# ============================================================================
# 2. DEVELOPMENT BACKEND (JIT via Python)
# ============================================================================
class AlignmentTileTaichiJIT:
    """Original JIT-based alignment using Taichi Python Kernels."""

    def __init__(self):
        if not TAICHI_JIT_AVAILABLE:
            raise ImportError("Taichi JIT components not found.")
        self.ref_img_gpu = None
        self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0

    def set_reference(self, ref_img, work_h, work_w, is_linear=False, proxy_scale=1.0, use_sharpen=False, **kwargs):
        self.ref_img_gpu, _ = common.ensure_taichi_field(ref_img, buffer_provider="pool")
        self.ref_work_res = preprocess.preprocess_pipeline_gpu(
            ref_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(work_h, work_w),
            buffer_provider="pool", return_numpy=False
        )
        self.work_h, self.work_w = work_h, work_w

    def compute_alignment_and_warp(self, comp_img, tile_h, tile_w, n_layers, is_linear=False, proxy_scale=1.0, use_sharpen=False, search_dist=2.0, return_format="numpy_u16", **kwargs):
        if self.ref_work_res is None: return None
        full_h, full_w = comp_img.shape[:2]
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")
        comp_work_res = preprocess.preprocess_pipeline_gpu(
            comp_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(self.work_h, self.work_w),
            buffer_provider="pool", return_numpy=False
        )
        flow_low_gpu = compute_alignment_flow(self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist)
        common.release_temp_buffer(comp_work_res)
        if flow_low_gpu is None: common.release_temp_buffer(comp_img_gpu); return None
        flow_full_gpu = common.get_temp_buffer((full_h, full_w, 2), ti.f32, buffer_provider="pool")
        self._resize_flow_gpu(flow_low_gpu, flow_full_gpu, full_w / self.work_w, full_h / self.work_h)
        common.release_temp_buffer(flow_low_gpu)
        warped_img_gpu = warp.warp_image_gpu(comp_img_gpu, flow_full_gpu, guidance=None)
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)
        is_taichi_ndarray = hasattr(warped_img_gpu, "to_numpy")
        if return_format == "numpy_f32":
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.float32) / 65535.0
            if is_taichi_ndarray: common.release_temp_buffer(warped_img_gpu)
            return result
        else:
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.uint16)
            if is_taichi_ndarray: common.release_temp_buffer(warped_img_gpu)
            return result

    def _resize_flow_gpu(self, src, dst, sx, sy):
        @ti.kernel
        def _resize_k(s: ti.types.ndarray(), d: ti.types.ndarray(), x: float, y: float):
            for r, c in ti.ndrange(d.shape[0], d.shape[1]):
                u, v = (c + 0.5) / d.shape[1], (r + 0.5) / d.shape[0]
                sr, sc = v * s.shape[0] - 0.5, u * s.shape[1] - 0.5
                r0, c0 = int(ti.floor(sr)), int(ti.floor(sc))
                fr, fc = sr - r0, sc - c0
                r0, r1 = ti.max(0, ti.min(r0, s.shape[0] - 2)), ti.max(0, ti.min(r0 + 1, s.shape[0] - 1))
                c0, c1 = ti.max(0, ti.min(c0, s.shape[1] - 2)), ti.max(0, ti.min(c0 + 1, s.shape[1] - 1))
                for i in ti.static(range(2)):
                    v00, v01, v10, v11 = s[r0, c0, i], s[r0, c1, i], s[r1, c0, i], s[r1, c1, i]
                    val = v00*(1-fc)*(1-fr) + v01*fc*(1-fr) + v10*(1-fc)*fr + v11*fc*fr
                    d[r, c, i] = val * (x if i == 0 else y)
        _resize_k(src, dst, sx, sy)

    def clear_data(self):
        if self.ref_img_gpu: common.release_temp_buffer(self.ref_img_gpu); self.ref_img_gpu = None
        if self.ref_work_res: common.release_temp_buffer(self.ref_work_res); self.ref_work_res = None
        common.cleanup_cache()


# ============================================================================
# 3. DISPATCHER & GLOBAL INTERFACE
# ============================================================================
_PROCESSOR = None

def _get_processor():
    global _PROCESSOR
    if _PROCESSOR is None:
        mode = os.environ.get("PIXEL_REFINE_BACKEND", "DEVELOPMENT")
        best_arch = "vulkan"
        try:
            import taichi as ti
            if ti._lib.core.is_cuda_available(): best_arch = "cuda"
            elif not ti._lib.core.is_vulkan_available(): best_arch = "cpu"
        except: pass

        if mode == "PRODUCTION":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, "../../../../../", "ui", "data")
            data_dir = os.path.abspath(data_dir)
            _PROCESSOR = AlignmentTileTaichiAOT(data_dir, arch=best_arch)
        else:
            _PROCESSOR = AlignmentTileTaichiJIT()
            print(f"[Taichi] Mode: DEVELOPMENT (JIT) on {best_arch.upper()}")
    return _PROCESSOR

@ti_thread
def set_reference_hybrid_taichi(ref_img, work_h, work_w, **kwargs):
    _get_processor().set_reference(ref_img, work_h=work_h, work_w=work_w, **kwargs)

@ti_thread
def compute_alignment_and_warp_hybrid_taichi(comp_img, tile_h, tile_w, n_layers, align_lib, return_format="numpy_u16", **kwargs):
    return _get_processor().compute_alignment_and_warp(comp_img, tile_h, tile_w, n_layers, return_format=return_format, **kwargs)

@ti_thread
def clear_taichi_cache():
    if _PROCESSOR:
        _PROCESSOR.clear_data()
