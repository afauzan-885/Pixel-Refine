import os
import time
import numpy as np
import taichi as ti
from ...taichi_algorithm import common, warp, preprocess
from .compute_flow import compute_alignment_flow

class AlignmentTileTaichiJIT:
    """Original JIT-based alignment using Taichi Python Kernels."""

    def __init__(self):
        self.ref_img_gpu = None
        self.ref_work_res = None
        self.work_h = 0
        self.work_w = 0

    def set_reference(self, ref_img, work_h, work_w, is_linear=False, proxy_scale=1.0, use_sharpen=False, **kwargs):
        t0 = time.perf_counter()
        h, w = ref_img.shape[:2]
        c = ref_img.shape[2] if len(ref_img.shape) > 2 else 1
        print(f"[PreprocessJIT] set_reference src=({h},{w},c={c}) -> work=({work_h},{work_w}) "
              f"is_linear={is_linear} sharpen={use_sharpen} scale={proxy_scale:.3f}")

        self.ref_img_gpu, _ = common.ensure_taichi_field(ref_img, buffer_provider="pool")
        self.ref_work_res = preprocess.preprocess_pipeline_gpu(
            ref_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(work_h, work_w),
            buffer_provider="pool", return_numpy=False
        )
        self.work_h, self.work_w = work_h, work_w
        ms = (time.perf_counter() - t0) * 1000
        print(f"[PreprocessJIT] Done in {ms:.2f} ms")

    def compute_alignment_and_warp(self, comp_img, tile_h, tile_w, n_layers, is_linear=False, proxy_scale=1.0, use_sharpen=False, search_dist=2.0, return_format="numpy_u16", **kwargs):
        if self.ref_work_res is None:
            print("[AlignJIT] Error: ref_work_res is None. Call set_reference first.")
            return None

        full_h, full_w = comp_img.shape[:2]
        c = comp_img.shape[2] if len(comp_img.shape) > 2 else 1

        # ── Preprocessing ─────────────────────────────────────────────────────
        t_pre = time.perf_counter()
        print(f"[PreprocessJIT] comp src=({full_h},{full_w},c={c}) -> work=({self.work_h},{self.work_w}) "
              f"is_linear={is_linear} sharpen={use_sharpen}")
        comp_img_gpu, _ = common.ensure_taichi_field(comp_img, buffer_provider="pool")
        comp_work_res = preprocess.preprocess_pipeline_gpu(
            comp_img, normalize=True, apply_gamma=is_linear, extract_green=True,
            use_sharpen=use_sharpen, scale=proxy_scale, target_size=(self.work_h, self.work_w),
            buffer_provider="pool", return_numpy=False
        )
        print(f"[PreprocessJIT] Done in {(time.perf_counter() - t_pre)*1000:.2f} ms")

        # ── Compute Flow ──────────────────────────────────────────────────────
        t_flow = time.perf_counter()
        print(f"[ComputeFlowJIT] work=({self.work_h},{self.work_w}) tile=({tile_h},{tile_w}) "
              f"n_layers={n_layers} search_dist={search_dist}")
        flow_low_gpu = compute_alignment_flow(self.ref_work_res, comp_work_res, tile_h, tile_w, n_layers, search_dist)
        common.release_temp_buffer(comp_work_res)
        ms_flow = (time.perf_counter() - t_flow) * 1000
        print(f"[ComputeFlowJIT] Done in {ms_flow:.2f} ms | flow shape: {flow_low_gpu.shape if flow_low_gpu is not None else 'None'}")

        if flow_low_gpu is None:
            common.release_temp_buffer(comp_img_gpu)
            return None

        # ── Upsample Flow ─────────────────────────────────────────────────────
        t_up = time.perf_counter()
        sx, sy = full_w / self.work_w, full_h / self.work_h
        print(f"[WarpJIT] upsample flow ({self.work_h},{self.work_w}) -> ({full_h},{full_w}) ratio=({sx:.3f},{sy:.3f})")
        flow_full_gpu = common.get_temp_buffer((full_h, full_w, 2), ti.f32, buffer_provider="pool")
        self._resize_flow_gpu(flow_low_gpu, flow_full_gpu, sx, sy)
        common.release_temp_buffer(flow_low_gpu)
        print(f"[WarpJIT] Upsample done in {(time.perf_counter() - t_up)*1000:.2f} ms")

        # ── Warp ──────────────────────────────────────────────────────────────
        t_warp = time.perf_counter()
        print(f"[WarpJIT] warping comp ({full_h},{full_w},c={c})")
        warped_img_gpu = warp.warp_image_gpu(comp_img_gpu, flow_full_gpu, guidance=None)
        common.release_temp_buffer(comp_img_gpu)
        common.release_temp_buffer(flow_full_gpu)
        print(f"[WarpJIT] Done in {(time.perf_counter() - t_warp)*1000:.2f} ms")

        # ── Output format ─────────────────────────────────────────────────────
        is_taichi_ndarray = hasattr(warped_img_gpu, "to_numpy")
        if return_format == "numpy_f32":
            raw = warped_img_gpu.to_numpy() if is_taichi_ndarray else warped_img_gpu
            result = raw.astype(np.float32) / 65535.0
            if is_taichi_ndarray: common.release_temp_buffer(warped_img_gpu)
            return result
        else:  # "numpy_u16"
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
