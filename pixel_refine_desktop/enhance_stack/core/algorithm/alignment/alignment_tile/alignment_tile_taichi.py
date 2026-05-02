"""
Taichi Modular AOT Architecture - Production Backend (Final Optimized)
======================================================================
1. Zero Python-Taichi dependency (Pure ctypes).
2. Zero-copy GPU memory sharing.
3. Optimized RAM usage (Device-local internal buffers).
4. Multi-layer pyramid alignment & upsampled warping.
"""

import os
import numpy as np
import ctypes
import importlib.util
from pixel_refine_desktop.enhance_stack.core.algorithm.taichi_algorithm.taichi_worker import (
    ti_thread,
)


def _is_taichi_available():
    if os.environ.get("PIXEL_REFINE_BACKEND") == "PRODUCTION":
        return True
    return importlib.util.find_spec("taichi") is not None


TAICHI_AVAILABLE = _is_taichi_available()


class AlignmentTileTaichiAOT:
    """Production-ready AOT alignment backend (Pure ctypes)."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            curr = os.path.dirname(os.path.abspath(__file__))
            while "enhance_stack" in curr:
                curr = os.path.dirname(curr)
            data_dir = os.path.abspath(os.path.join(curr, "ui", "data"))
        self.data_dir = data_dir

        # DLL & TCM Paths
        self.preprocess_dll = os.path.join(data_dir, "preprocessing_aot.dll")
        self.flow_dll       = os.path.join(data_dir, "compute_flow_aot.dll")
        self.warp_dll       = os.path.join(data_dir, "warp_aot.dll")
        self.aot_assets     = os.path.join(data_dir, "aot_assets")

        self.initialized = False
        self.runtime = None

        # Persistent Ref Pyramid state
        self.ref_raw_gpu         = None
        self.ref_pyramid_handles = None   # ctypes array of 3 void*
        self.ref_pyramid_h       = None   # ctypes c_int array [3]
        self.ref_pyramid_w       = None   # ctypes c_int array [3]
        self.tmp_ref_l           = [None, None]  # 2 intermediate downsampling buffers
        self.work_h, self.work_w = 0, 0

        try:
            self._load_and_init()
            self.initialized = True
            print("[TaichiAOT] Modular Production Backend (Vulkan) initialized.")
        except Exception as e:
            print(f"[TaichiAOT] Critical Error: {e}")

    # ──────────────────────────────────────────────────────────────────────────
    # Internal: Load DLLs and initialize Taichi runtime
    # ──────────────────────────────────────────────────────────────────────────
    def _load_and_init(self):
        self.dll_pre  = ctypes.CDLL(self.preprocess_dll)
        self.dll_flow = ctypes.CDLL(self.flow_dll)
        self.dll_warp = ctypes.CDLL(self.warp_dll)

        # ── Preprocess DLL signatures ─────────────────────────────────────────
        self.dll_pre.init_taichi_runtime.restype = ctypes.c_void_p

        self.dll_pre.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.dll_pre.load_aot_module.restype  = ctypes.c_void_p

        self.dll_pre.allocate_gpu_buffer.argtypes = [
            ctypes.c_void_p, ctypes.c_uint64, ctypes.c_int,
        ]
        self.dll_pre.allocate_gpu_buffer.restype = ctypes.c_void_p

        self.dll_pre.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

        self.dll_pre.write_to_gpu_buffer.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64,
        ]

        self.dll_pre.run_preprocess_aot.argtypes = [
            ctypes.c_void_p,   # runtime
            ctypes.c_void_p,   # module
            ctypes.c_char_p,   # graph_name
            ctypes.c_void_p,   # src_mem
            ctypes.c_int,      # src_h
            ctypes.c_int,      # src_w
            ctypes.c_int,      # src_c
            ctypes.c_void_p,   # dst_mem
            ctypes.c_int,      # dst_h
            ctypes.c_int,      # dst_w
            ctypes.c_float,    # scale_norm
            ctypes.c_int,      # apply_gamma
            ctypes.c_float,    # scale_gamma
            ctypes.c_float,    # gamma_pow
            ctypes.c_float,    # slope
            ctypes.c_float,    # cutoff
            ctypes.c_int,      # use_sharpen
        ]

        # ── Flow DLL signature ────────────────────────────────────────────────
        self.dll_flow.run_compute_flow_aot.argtypes = [
            ctypes.c_void_p,                  # 1.  runtime_ptr
            ctypes.c_void_p,                  # 2.  module_ptr
            ctypes.c_char_p,                  # 3.  graph_name
            ctypes.POINTER(ctypes.c_void_p),  # 4.  ref_pyramid   (void**)
            ctypes.POINTER(ctypes.c_int),     # 5.  ref_h         (int*)
            ctypes.POINTER(ctypes.c_int),     # 6.  ref_w         (int*)
            ctypes.POINTER(ctypes.c_void_p),  # 7.  comp_pyramid  (void**)
            ctypes.POINTER(ctypes.c_int),     # 8.  comp_h        (int*)
            ctypes.POINTER(ctypes.c_int),     # 9.  comp_w        (int*)
            ctypes.POINTER(ctypes.c_void_p),  # 10. flow_pyramid  (void**)
            ctypes.POINTER(ctypes.c_void_p),  # 11. flow_tmp      (void**)
            ctypes.c_void_p,                  # 12. tmp_ref_l1
            ctypes.c_void_p,                  # 13. tmp_ref_l2
            ctypes.c_void_p,                  # 14. tmp_comp_l1
            ctypes.c_void_p,                  # 15. tmp_comp_l2
            ctypes.c_void_p,                  # 16. zncc_surf
            ctypes.c_void_p,                  # 17. zncc_res
            ctypes.c_int,                     # 18. tile_h
            ctypes.c_int,                     # 19. tile_w
            ctypes.c_int,                     # 20. search_radius
            ctypes.c_int,                     # 21. coarse_dist
            ctypes.c_float,                   # 22. scale
            ctypes.c_int,                     # 23. ds_fac
            ctypes.c_int,                     # 24. zncc_shift
            ctypes.c_int,                     # 25. step_y
            ctypes.c_int,                     # 26. step_x
        ]

        # ── Warp DLL signature ────────────────────────────────────────────────
        self.dll_warp.run_warp_aot.argtypes = [
            ctypes.c_void_p,  # runtime
            ctypes.c_void_p,  # module
            ctypes.c_char_p,  # graph_name (unused by bridge, kept for API compat)
            ctypes.c_void_p,  # src_mem
            ctypes.c_void_p,  # flow_low_mem
            ctypes.c_void_p,  # flow_full_mem
            ctypes.c_void_p,  # dst_mem
            ctypes.c_void_p,  # guide_mem
            ctypes.c_int,     # h
            ctypes.c_int,     # w
            ctypes.c_int,     # c
            ctypes.c_int,     # work_h
            ctypes.c_int,     # work_w
        ]

        self.dll_warp.read_from_gpu_buffer.argtypes = [
            ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint64,
        ]

        # ── Init Runtime & Load Modules ───────────────────────────────────────
        self.runtime  = self.dll_pre.init_taichi_runtime()
        self.mod_pre  = self.dll_pre.load_aot_module(
            self.runtime,
            os.path.join(self.aot_assets, "preprocess_vulkan.tcm").encode(),
        )
        self.mod_flow = self.dll_pre.load_aot_module(
            self.runtime,
            os.path.join(self.aot_assets, "compute_flow_vulkan.tcm").encode(),
        )
        self.mod_warp = self.dll_pre.load_aot_module(
            self.runtime,
            os.path.join(self.aot_assets, "warp_vulkan.tcm").encode(),
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Helper: wrap a raw integer GPU handle as a proper ctypes void*
    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _as_voidp(val):
        """Convert a raw integer GPU handle to ctypes.c_void_p."""
        return ctypes.c_void_p(int(val))

    # ──────────────────────────────────────────────────────────────────────────
    # Public API: set_reference
    # ──────────────────────────────────────────────────────────────────────────
    def set_reference(
        self, ref_img, work_h, work_w, is_linear=False, use_sharpen=False, **kwargs
    ):
        if not self.initialized:
            return
        h, w = ref_img.shape[:2]
        c = ref_img.shape[2] if len(ref_img.shape) > 2 else 1
        self.work_h, self.work_w = work_h, work_w

        # ── Allocate & upload raw source image ───────────────────────────────
        raw_size = h * w * c * 4
        if not self.ref_raw_gpu:
            self.ref_raw_gpu = self.dll_pre.allocate_gpu_buffer(self.runtime, raw_size, 1)

        ref_i32 = np.ascontiguousarray(ref_img.astype(np.int32))
        self.dll_pre.write_to_gpu_buffer(
            self.runtime, self.ref_raw_gpu, ref_i32.ctypes.data, raw_size
        )

        # ── Allocate ref pyramid buffers (once per resolution) ────────────────
        h_l = [work_h, work_h // 4, work_h // 16]
        w_l = [work_w, work_w // 4, work_w // 16]

        if not self.ref_pyramid_handles:
            p_handles = [
                self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[0] * w_l[0] * 4, 1),  # L0
                self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[1] * w_l[1] * 4, 0),  # L1
                self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[2] * w_l[2] * 4, 0),  # L2
            ]
            self.ref_pyramid_handles = (ctypes.c_void_p * 3)(*p_handles)
            self.tmp_ref_l = [
                self.dll_pre.allocate_gpu_buffer(
                    self.runtime, (h_l[i] // 2) * (w_l[i] // 2) * 4, 0
                )
                for i in range(2)
            ]

        # Always refresh metadata arrays (safe if resolution unchanged)
        self.ref_pyramid_h = (ctypes.c_int * 3)(*h_l)
        self.ref_pyramid_w = (ctypes.c_int * 3)(*w_l)

        # ── GPU Preprocessing (AOT) — identical math to preprocess_pipeline_gpu
        scale_norm  = 65535.0 if np.issubdtype(ref_img.dtype, np.integer) else 1.0
        apply_gamma = 1 if is_linear else 0
        scale_gamma = float(kwargs.get("proxy_scale", 1.0))

        # ref_pyramid_handles[0] is an int inside the ctypes array — wrap it.
        dst_l0_ptr = self._as_voidp(self.ref_pyramid_handles[0])

        self.dll_pre.run_preprocess_aot(
            self.runtime,
            self.mod_pre,
            b"preprocess_rgb",
            self._as_voidp(self.ref_raw_gpu),  # src
            ctypes.c_int(h),
            ctypes.c_int(w),
            ctypes.c_int(c),
            dst_l0_ptr,                         # dst (L0 of ref pyramid)
            ctypes.c_int(work_h),
            ctypes.c_int(work_w),
            ctypes.c_float(scale_norm),
            ctypes.c_int(apply_gamma),
            ctypes.c_float(scale_gamma),
            ctypes.c_float(2.2),               # gamma_pow
            ctypes.c_float(4.5),               # slope
            ctypes.c_float(0.018),             # cutoff
            ctypes.c_int(1 if use_sharpen else 0),
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Public API: compute_alignment_and_warp
    # ──────────────────────────────────────────────────────────────────────────
    def compute_alignment_and_warp(
        self,
        comp_img,
        tile_h,
        tile_w,
        search_dist=16.0,
        n_layers=3,
        return_format="numpy_u16",
        **kwargs,
    ):
        if not self.initialized:
            return None

        # Safety: reference must be set before calling this
        if self.ref_pyramid_handles is None or self.tmp_ref_l[0] is None:
            print("[TaichiAOT] Error: Reference pyramid not initialized. Call set_reference first.")
            return None

        fh, fw = comp_img.shape[:2]
        c = comp_img.shape[2] if len(comp_img.shape) > 2 else 1

        # ── Pyramid dimension lists ───────────────────────────────────────────
        h_l = [self.work_h, self.work_h // 4, self.work_h // 16]
        w_l = [self.work_w, self.work_w // 4, self.work_w // 16]

        # ── Allocate comparison raw buffer ────────────────────────────────────
        raw_size = fh * fw * c * 4
        cb_raw   = self.dll_pre.allocate_gpu_buffer(self.runtime, raw_size, 1)
        comp_i32 = np.ascontiguousarray(comp_img.astype(np.int32))
        self.dll_pre.write_to_gpu_buffer(
            self.runtime, cb_raw, comp_i32.ctypes.data, raw_size
        )

        # ── Comparison pyramid buffers ────────────────────────────────────────
        cp_h = [
            self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[0] * w_l[0] * 4, 1),  # L0
            self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[1] * w_l[1] * 4, 0),  # L1
            self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[2] * w_l[2] * 4, 0),  # L2
        ]
        c_pyramid = (ctypes.c_void_p * 3)(*cp_h)

        # ── Flow & temp flow buffers ──────────────────────────────────────────
        f_h = [
            self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[i] * w_l[i] * 2 * 4, 0)
            for i in range(3)
        ]
        ft_h = [
            self.dll_pre.allocate_gpu_buffer(self.runtime, h_l[i] * w_l[i] * 2 * 4, 0)
            for i in range(3)
        ]
        f_pyramid  = (ctypes.c_void_p * 3)(*f_h)
        ft_pyramid = (ctypes.c_void_p * 3)(*ft_h)

        # ── Intermediate downsampling buffers (for comp) ──────────────────────
        tc_l = [
            self.dll_pre.allocate_gpu_buffer(
                self.runtime, (h_l[i] // 2) * (w_l[i] // 2) * 4, 0
            )
            for i in range(2)
        ]

        # ── ZNCC buffers ──────────────────────────────────────────────────────
        # host_accessible=1 is REQUIRED to read back results to CPU for motion estimation
        z_surf = self.dll_pre.allocate_gpu_buffer(self.runtime, 65 * 65 * 4, 1)
        z_res  = self.dll_pre.allocate_gpu_buffer(self.runtime, 3 * 4, 1) # [val, y, x]

        # Collect all temp buffers for cleanup at the end
        _temp_bufs = cp_h + f_h + ft_h + tc_l + [cb_raw, z_surf, z_res]

        # ── GPU Preprocessing (AOT) for comparison image ──────────────────────
        scale_norm  = 65535.0 if np.issubdtype(comp_img.dtype, np.integer) else 1.0
        is_linear   = kwargs.get("is_linear", False)
        apply_gamma = 1 if is_linear else 0
        scale_gamma = float(kwargs.get("proxy_scale", 1.0))
        use_sharpen = kwargs.get("use_sharpen", False)

        self.dll_pre.run_preprocess_aot(
            self.runtime,
            self.mod_pre,
            b"preprocess_rgb",
            self._as_voidp(cb_raw),          # src
            ctypes.c_int(fh),
            ctypes.c_int(fw),
            ctypes.c_int(c),
            self._as_voidp(cp_h[0]),         # dst (L0 of comp pyramid)
            ctypes.c_int(self.work_h),
            ctypes.c_int(self.work_w),
            ctypes.c_float(scale_norm),
            ctypes.c_int(apply_gamma),
            ctypes.c_float(scale_gamma),
            ctypes.c_float(2.2),             # gamma_pow
            ctypes.c_float(4.5),             # slope
            ctypes.c_float(0.018),           # cutoff
            ctypes.c_int(1 if use_sharpen else 0),
        )

        # ── Compute Flow (Monolithic AOT graph) ───────────────────────────────
        comp_h_arr = (ctypes.c_int * 3)(*h_l)
        comp_w_arr = (ctypes.c_int * 3)(*w_l)
        radius     = int(search_dist * 2)
        dist       = int(search_dist)
        ds_fac     = 4

        self.dll_flow.run_compute_flow_aot(
            self.runtime,                              # 1
            self.mod_flow,                             # 2
            b"align_end_to_end_3layer",                # 3
            self.ref_pyramid_handles,                  # 4  void**
            self.ref_pyramid_h,                        # 5  int*
            self.ref_pyramid_w,                        # 6  int*
            c_pyramid,                                 # 7  void**
            comp_h_arr,                                # 8  int*
            comp_w_arr,                                # 9  int*
            f_pyramid,                                 # 10 void**
            ft_pyramid,                                # 11 void**
            self._as_voidp(self.tmp_ref_l[0]),        # 12
            self._as_voidp(self.tmp_ref_l[1]),        # 13
            self._as_voidp(tc_l[0]),                  # 14
            self._as_voidp(tc_l[1]),                  # 15
            self._as_voidp(z_surf),                   # 16
            self._as_voidp(z_res),                    # 17
            ctypes.c_int(tile_h),                     # 18
            ctypes.c_int(tile_w),                     # 19
            ctypes.c_int(radius),                     # 20
            ctypes.c_int(dist),                       # 21
            ctypes.c_float(4.0),                      # 22 scale
            ctypes.c_int(ds_fac),                     # 23
            ctypes.c_int(32),                         # 24 zncc_shift
            ctypes.c_int(tile_h // 2),                # 25 step_y
            ctypes.c_int(tile_w // 2),                # 26 step_x
        )

        # ── Warp (Upsample flow → warp comp image) ────────────────────────────
        dst_raw = self.dll_pre.allocate_gpu_buffer(self.runtime, raw_size, 1)
        f_full  = self.dll_pre.allocate_gpu_buffer(self.runtime, fh * fw * 2 * 4, 0)

        self.dll_warp.run_warp_aot(
            self.runtime,
            self.mod_warp,
            b"warp_ops",                           # unused by bridge, kept for API compat
            self._as_voidp(cb_raw),               # src
            self._as_voidp(f_h[0]),               # flow_low (work-res)
            self._as_voidp(f_full),               # flow_full (full-res upsample target)
            self._as_voidp(dst_raw),              # dst
            self._as_voidp(self.ref_raw_gpu),     # guide (reference image)
            ctypes.c_int(fh),
            ctypes.c_int(fw),
            ctypes.c_int(c),
            ctypes.c_int(self.work_h),
            ctypes.c_int(self.work_w),
        )

        # ── Download result to CPU ────────────────────────────────────────────
        res = np.zeros((fh, fw, c), dtype=np.int32)
        self.dll_warp.read_from_gpu_buffer(
            self.runtime, dst_raw, res.ctypes.data, raw_size
        )

        # ── Cleanup all temp GPU buffers ──────────────────────────────────────
        for buf in _temp_bufs + [dst_raw, f_full]:
            if buf:
                self.dll_pre.free_gpu_buffer(self.runtime, buf)

        return (
            res.astype(np.uint16)
            if return_format == "numpy_u16"
            else res.astype(np.float32) / 65535.0
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Public API: clear_data
    # ──────────────────────────────────────────────────────────────────────────
    def clear_data(self):
        if self.ref_raw_gpu:
            self.dll_pre.free_gpu_buffer(self.runtime, self.ref_raw_gpu)
            self.ref_raw_gpu = None

        if self.ref_pyramid_handles:
            for h in self.ref_pyramid_handles:
                if h:
                    self.dll_pre.free_gpu_buffer(self.runtime, h)
            self.ref_pyramid_handles = None

        for buf in self.tmp_ref_l:
            if buf:
                self.dll_pre.free_gpu_buffer(self.runtime, buf)
        self.tmp_ref_l = [None, None]

        self.ref_pyramid_h = None
        self.ref_pyramid_w = None


# ──────────────────────────────────────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────────────────────────────────────
_PROCESSOR = None


def _get_processor():
    global _PROCESSOR
    requested_backend = os.environ.get("PIXEL_REFINE_BACKEND", "DEVELOPMENT")

    needs_init = _PROCESSOR is None
    if _PROCESSOR is not None:
        from .alignment_tile_taichi_jit_wrapper import AlignmentTileTaichiJIT
        is_jit = isinstance(_PROCESSOR, AlignmentTileTaichiJIT)
        if requested_backend == "PRODUCTION" and is_jit:
            _PROCESSOR.clear_data()
            needs_init = True
        elif requested_backend == "DEVELOPMENT" and not is_jit:
            _PROCESSOR.clear_data()
            needs_init = True

    if needs_init:
        if requested_backend == "PRODUCTION":
            _PROCESSOR = AlignmentTileTaichiAOT()
        else:
            from .alignment_tile_taichi_jit_wrapper import AlignmentTileTaichiJIT
            _PROCESSOR = AlignmentTileTaichiJIT()

    return _PROCESSOR


@ti_thread
def set_reference_hybrid_taichi(ref_img, work_h, work_w, **kwargs):
    _get_processor().set_reference(ref_img, work_h=work_h, work_w=work_w, **kwargs)


@ti_thread
def compute_alignment_and_warp_hybrid_taichi(
    comp_img, tile_h, tile_w, n_layers, align_lib, return_format="numpy_u16", **kwargs
):
    return _get_processor().compute_alignment_and_warp(
        comp_img,
        tile_h,
        tile_w,
        n_layers=n_layers,
        return_format=return_format,
        **kwargs,
    )


@ti_thread
def clear_taichi_cache():
    if _PROCESSOR:
        _PROCESSOR.clear_data()
