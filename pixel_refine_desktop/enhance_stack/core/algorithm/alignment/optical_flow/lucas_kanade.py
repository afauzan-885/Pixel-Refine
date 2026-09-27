import json
import os
import time
import gc

import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_block_flow,
    to_flow_gray_u8,
)


DEFAULT_LUCAS_KANADE_CONFIG = {
    "backend": "auto",
    "mode": "high",
    "conservative_vram": True,
}

LUCAS_KANADE_PRESETS = {
    "fast": {
        # 32x32 grid step for high responsiveness and low memory footprint.
        "grid_step": 32,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 13,
        "max_level": 1,
        "iterations": 8,
        "epsilon": 0.05,
        "overlap": 0.50,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.50,
        "max_flow_px": 48.0,
        "dense_mode": "smooth",
        "smooth": True,
    },
    "balance": {
        # 16x16 grid step for optimal quality-performance balance.
        "grid_step": 16,
        "border_margin": 8,
        "point_workers": 2,
        "win_size": 17,
        "max_level": 2,
        "iterations": 16,
        "epsilon": 0.015,
        "overlap": 0.50,
        "motion_mode": "fast",
        "adaptive": False,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.50,
        "max_flow_px": 64.0,
        "dense_mode": "smooth",
        "smooth": True,
    },
    "high": {
        # 2x2 ultra-dense micro-grid for highest spatial accuracy, capturing fine details.
        "grid_step": 2,
        "border_margin": 8,
        "point_workers": 4,
        "win_size": 25,
        "max_level": 3,
        "iterations": 32,
        "epsilon": 0.005,
        "overlap": 0.50,
        "motion_mode": "auto",
        "adaptive": True,
        "adaptive_threshold": 1,
        "use_multi_core": False,
        "tile_overlap": 0.50,
        "max_flow_px": 96.0,
        "dense_mode": "smooth",
        "smooth": True,
    },
}

LUCAS_KANADE_PRESETS["medium"] = LUCAS_KANADE_PRESETS["balance"]
# Backward compatibility mapping
LUCAS_KANADE_GPU_PRESETS = LUCAS_KANADE_PRESETS
LUCAS_KANADE_CPU_PRESETS = LUCAS_KANADE_PRESETS


def _allocate_float_buffer_like(taichi_aot, image, host_accessible=False):
    is_color = image.ndim == 3
    return taichi_aot.engine.allocate(
        image.shape,
        dtype=np.float32,
        is_vector=is_color,
        vector_dim=3 if is_color else 1,
        host_accessible=host_accessible,
    )


class LucasKanade:
    NAME = "Lucas Kanade Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Unified Taichi AOT Lucas-Kanade optical flow alignment for all backends."
    GPU_MODULES = ("common", "lucas_kanade", "pyramid", "remap")
    DEVICE_RESERVATION = "lucas_kanade_frame"
    _gpu_remap_disabled = False
    _reported_gpu_remap_disabled = False

    def __init__(self):
        self._tile_buffers = None
        self._current_ref_id = None
        self._download_float_buffer = None

    def __del__(self):
        try:
            self._cleanup_tile_buffers()
        except Exception:
            pass

    @staticmethod
    def _normalize_mode(mode):
        value = str(mode or "fast").strip().lower()
        if value in ("balanced", "balance mode", "balance", "normal", "medium"):
            return "balance"
        if value == "auto":
            return "high"
        if value not in LUCAS_KANADE_PRESETS:
            return "high"
        return value

    @staticmethod
    def _resolve_mode_config(config):
        mode = LucasKanade._normalize_mode(config.get("mode", "high"))
        resolved = LUCAS_KANADE_PRESETS[mode].copy()
        for key, value in config.items():
            if key != "mode":
                resolved[key] = value
        resolved["mode"] = mode
        return resolved

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = DEFAULT_LUCAS_KANADE_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                # Check modern and legacy section keys
                config.update(params.get("LucasKanade", {}))
                config.update(params.get("LucasKanadeGPU", {}))
                config.update(params.get("LucasKanade_BATCH", {}))
        except Exception as exc:
            print(f"[LucasKanade] Failed to load config: {exc}")
        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_params = batch_parameter_manager.load_json_state().get(
                    str(batch_id), {}
                )
                section = batch_params.get("lucas_kanade_params", {})
                if not section:
                    section = batch_params.get("lucas_kanade_gpu_params", {})
                if isinstance(section, dict):
                    config.update(section)
            except Exception as exc:
                print(f"[LucasKanade] Failed to load batch config: {exc}")
        return LucasKanade._resolve_mode_config(config)

    @staticmethod
    def load_lucas_kanade_config(config_filename=None):
        return LucasKanade.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_config_for_batch(config_filename=None):
        return LucasKanade.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_gpu_config(config_filename=None):
        return LucasKanade.load_config(config_filename=config_filename)

    @staticmethod
    def load_lucas_kanade_gpu_config_for_batch(config_filename=None):
        return LucasKanade.load_config(config_filename=config_filename)

    def _cleanup_tile_buffers(self, *, keep_reference=False):
        if not self._tile_buffers:
            return
        remaining = {}
        for idx, bufs in tuple(self._tile_buffers.items()):
            retained = {}
            for name, buf in bufs.items():
                if keep_reference and name in ("ref_gray_gpu", "reference_pyramid"):
                    retained[name] = buf
                    continue
                self._release_tile_value(buf)
            if retained:
                remaining[idx] = retained
        self._tile_buffers = remaining or None
        if self._tile_buffers is None:
            self._current_ref_id = None

    @classmethod
    def _release_tile_value(cls, value):
        """Release a tile buffer or a resident pyramid owned by that tile."""
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                cls._release_tile_value(item)
            return
        release = getattr(value, "release", None)
        destroy = getattr(value, "destroy", None)
        if callable(release):
            try:
                release()
                return
            except Exception:
                pass
        if callable(destroy):
            try:
                destroy()
                return
            except Exception:
                pass

    def _cleanup_tile_buffer(self, tile_idx, *, keep_reference=False):
        if not self._tile_buffers:
            return
        bufs = self._tile_buffers.pop(tile_idx, None)
        if not bufs:
            return
        retained = {}
        for name, buf in bufs.items():
            if keep_reference and name in ("ref_gray_gpu", "reference_pyramid"):
                retained[name] = buf
                continue
            self._release_tile_value(buf)
        if retained:
            self._tile_buffers[tile_idx] = retained

    @staticmethod
    def _vram_cleanup(reason="", *, clear_pool=True):
        try:
            from taichi_vision import taichi_aot

            engine = getattr(taichi_aot, "engine", None)
            if engine is not None:
                if hasattr(engine, "sync"):
                    engine.sync()
                if clear_pool and hasattr(engine, "buffer_pool") and engine.buffer_pool:
                    engine.buffer_pool.clear()
        except Exception as exc:
            print(f"[LucasKanade] VRAM cleanup skipped ({reason}): {exc}")
        if clear_pool:
            gc.collect()

    def _init_tile_buffers(self, reference, tiles, config):
        return {
            idx: self._init_tile_buffer(reference, tile, config)
            for idx, tile in enumerate(tiles)
        }

    def _init_tile_buffer(self, reference, tile, config=None, reuse_reference=None):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_aot import get_engine

        engine = get_engine()
        rx0, ry0, rx1, ry1 = tile["roi"]
        roi_h, roi_w = ry1 - ry0, rx1 - rx0
        ref_roi = reference[ry0:ry1, rx0:rx1]
        if reuse_reference and reuse_reference.get("ref_gray_gpu") is not None:
            ref_gray_gpu = reuse_reference["ref_gray_gpu"]
        elif hasattr(ref_roi, "handle"):
            if getattr(ref_roi, "is_vector", False):
                ref_gray_gpu = taichi_aot.cvtColor(ref_roi, taichi_aot.COLOR_RGB2GRAY)
            else:
                ref_gray_gpu = ref_roi
        else:
            if ref_roi.ndim == 3:
                ref_color_gpu = taichi_aot.upload(
                    np.ascontiguousarray(ref_roi, dtype=np.float32), is_vector=True
                )
                ref_gray_gpu = taichi_aot.cvtColor(ref_color_gpu, taichi_aot.COLOR_RGB2GRAY)
                ref_color_gpu.release()
            else:
                ref_gray_gpu = taichi_aot.upload(
                    np.ascontiguousarray(ref_roi, dtype=np.float32), is_vector=False
                )
        is_color = reference.ndim == 3
        shape = (roi_h, roi_w, 3) if is_color else (roi_h, roi_w)
        target_gpu = engine.allocate(
            shape, dtype=np.float32, is_vector=is_color,
            vector_dim=3 if is_color else 1, host_accessible=True,
        )
        target_gray_gpu = engine.allocate(
            (roi_h, roi_w), dtype=np.float32, is_vector=False,
            host_accessible=True,
        )
        hanning_gpu = taichi_aot.upload(
            taichi_aot.generate_hanning_window_2d(
                (roi_h, roi_w), exclude_boundary=True
            ),
            is_vector=False,
        )
        vx0, vy0, vx1, vy1 = tile["valid"]
        oy0, ox0 = vy0 - ry0, vx0 - rx0
        oy1, ox1 = vy1 - ry0, vx1 - rx0
        mask_cpu = np.zeros((roi_h, roi_w), dtype=np.float32)
        mask_cpu[oy0:oy1, ox0:ox1] = 1.0

        cache_reference_pyramid = bool(
            (config or {}).get(
                "cache_reference_pyramid",
                not bool((config or {}).get("conservative_vram", True)),
            )
        )
        reference_pyramid = (
            reuse_reference.get("reference_pyramid")
            if reuse_reference
            else None
        )
        if (
            reference_pyramid is None
            and cache_reference_pyramid
            and (rx0, ry0, rx1, ry1) == (
                0,
                0,
                int(reference.shape[1]),
                int(reference.shape[0]),
            )
        ):
            candidate_pyramid = None
            try:
                from taichi_vision.taichi_algorithm.pyramid.pyramid import (
                    build_image_pyramid_gpu,
                )

                candidate_pyramid = build_image_pyramid_gpu(
                    ref_gray_gpu,
                    n_levels=max(1, int((config or {}).get("max_level", 2)) + 1),
                    min_size=32,
                )
                reference_pyramid = candidate_pyramid
            except Exception:
                try:
                    for level in candidate_pyramid[1:]:
                        self._release_tile_value(level)
                except Exception:
                    pass
                reference_pyramid = None
        buffers = {
            "ref_gray_gpu": ref_gray_gpu,
            "reference_pyramid": reference_pyramid,
            "target_gpu": target_gpu,
            "target_gray_gpu": target_gray_gpu,
            "target_host": np.empty(shape, dtype=np.float32),
            "target_gray_host": np.empty((roi_h, roi_w), dtype=np.float32),
            "hanning_gpu": hanning_gpu,
            "mask_gpu": taichi_aot.upload(mask_cpu, is_vector=False),
            "warped_gpu": engine.allocate(
                shape, dtype=np.float32, is_vector=is_color,
                vector_dim=3 if is_color else 1,
            ),
        }
        return buffers

    def _build_lk_params(self, config):
        win_size = max(5, int(config.get("win_size", 13)))
        if win_size % 2 == 0:
            win_size += 1

        smooth = config.get("smooth", None)
        if smooth is not None:
            dense_mode = "smooth" if bool(smooth) else "blocky_clamped"
            overlap = 0.50 if bool(smooth) else 0.0
        else:
            dense_mode = str(config.get("dense_mode", "smooth"))
            overlap = float(config.get("overlap", 0.50))

        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(config.get("iterations", 8))),
                float(config.get("epsilon", 0.03)),
            ),
            "grid_step": max(1, int(config.get("grid_step", 16))),
            "border_margin": max(0, int(config.get("border_margin", 8))),
            "overlap": overlap,
            "adaptive": bool(config.get("adaptive", False)),
            "adaptive_threshold": max(
                1, int(config.get("adaptive_threshold", 1))
            ),
            "motion_mode": str(config.get("motion_mode", "fast")),
            "dense_mode": dense_mode,
            "max_flow_px": float(config.get("max_flow_px", 64.0)),
        }
    def calculate_flow(
        self,
        reference_gray,
        target_gray,
        config,
        point_executor=None,
        return_gpu=False,
    ):
        """Run the full-frame Taichi AOT Lucas-Kanade implementation."""
        if return_gpu:
            return self._calculate_flow_gpu_buffer(reference_gray, target_gray, config)

        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        lk_params = self._build_lk_params(config)

        try:
            flow = calcOpticalFlowPyrLK(
                np.ascontiguousarray(reference_gray, dtype=np.float32),
                np.ascontiguousarray(target_gray, dtype=np.float32),
                **lk_params,
            )
            if isinstance(flow, tuple):
                flow = flow[0]
            if flow is not None:
                flow_arr = np.asarray(flow, dtype=np.float32)
                expected = (*reference_gray.shape[:2], 2)
                if flow_arr.shape == expected and np.isfinite(flow_arr).all():
                    return np.ascontiguousarray(flow_arr)
        except Exception as exc:
            print(
                f"[LucasKanade] Dense AOT flow failed, falling back to grid flow: {exc}"
            )

        return self._calculate_flow_grid_fallback(
            reference_gray,
            target_gray,
            config,
            lk_params,
        )

    def _calculate_flow_gpu_buffer(
        self, reference_gray, target_gray, config, reference_pyramid=None
    ):
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        flow_kwargs = self._build_lk_params(config)
        flow_kwargs["return_gpu"] = True
        if reference_pyramid is not None:
            flow_kwargs["reference_pyramid"] = reference_pyramid
        flow = calcOpticalFlowPyrLK(reference_gray, target_gray, **flow_kwargs)
        if isinstance(flow, tuple):
            flow = flow[0]
        if flow is None or not hasattr(flow, "shape"):
            raise RuntimeError("Lucas Kanade AOT did not return a GPU flow buffer")
        return flow

    def _calculate_flow_host_native(self, reference_gray, target_gray, config):
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK
        params = self._build_lk_params(config)
        params["criteria"] = (
            3,
            min(2, int(params["criteria"][1])),
            float(params["criteria"][2]),
        )
        params["maxLevel"] = min(1, int(params["maxLevel"]))
        params["motion_mode"] = "fast"
        if max(reference_gray.shape[:2]) > 768:
            params["maxLevel"] = 0
            params["grid_step"] = max(64, int(params["grid_step"]))
        flow = calcOpticalFlowPyrLK(
            np.ascontiguousarray(reference_gray, dtype=np.float32),
            np.ascontiguousarray(target_gray, dtype=np.float32),
            **params, return_gpu=False,
        )
        if isinstance(flow, tuple):
            flow = flow[0]
        return np.ascontiguousarray(flow, dtype=np.float32)

    def _align_frame_opengl_native(self, reference, target, config,
                                   matching_reference=None, matching_target=None):
        from taichi_vision import taichi_aot
        matching_reference = reference if matching_reference is None else matching_reference
        matching_target = target if matching_target is None else matching_target
        reference_gray = to_flow_gray_u8(matching_reference).astype(np.float32, copy=False)
        target_gray = to_flow_gray_u8(matching_target).astype(np.float32, copy=False)
        flow = self._calculate_flow_host_native(reference_gray, target_gray, config)
        expected = (*reference.shape[:2], 2)
        if flow.shape != expected or not np.isfinite(flow).all():
            raise RuntimeError(f"OpenGL native flow returned {flow.shape}, expected {expected}")
        return taichi_aot.remap_with_flow(
            np.ascontiguousarray(target), flow,
            int(reference.shape[0]), int(reference.shape[1]), return_gpu=False,
        )

    def align_frame(
        self,
        reference,
        target,
        config=None,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
        matching_reference=None,
        matching_target=None,
        return_gpu=False,
        target_for_warping=None,
    ):
        config = config or self.load_config()
        if reference is None or target is None:
            return None
        matching_reference = reference if matching_reference is None else matching_reference
        matching_target = target if matching_target is None else matching_target

        try:
            from taichi_vision import taichi_aot
            if str(getattr(taichi_aot.engine, "arch", "")).lower() == "opengl":
                return self._align_frame_opengl_native(
                    reference, target, config,
                    matching_reference=matching_reference,
                    matching_target=matching_target,
                )
        except Exception:
            raise

        if LucasKanade._gpu_remap_disabled:
            if not LucasKanade._reported_gpu_remap_disabled:
                print(
                    "[LucasKanade] GPU remap path disabled after previous failure; "
                    "using the Taichi Vision host/remap compatibility path."
                )
                LucasKanade._reported_gpu_remap_disabled = True
            return self._align_frame_host_fallback(
                reference,
                target,
                config=config,
                stop_requested=stop_requested,
                tile_executor=tile_executor,
                point_executor=point_executor,
                target_for_warping=target_for_warping,
            )

        try:
            from taichi_vision import taichi_aot

            with taichi_aot.engine.reserve_device_execution(self.DEVICE_RESERVATION):
                for module_name in self.GPU_MODULES:
                    taichi_aot._mod(module_name)
                taichi_aot.engine.sync()
                if not bool(config.get("retain_native_pool", False)):
                    taichi_aot.engine.buffer_pool.clear()
                res = self._align_frame_gpu_flow_remap(
                    reference,
                    target,
                    config,
                    stop_requested=stop_requested,
                    matching_reference=matching_reference,
                    matching_target=matching_target,
                    return_gpu=return_gpu,
                )
            if bool(config.get("conservative_vram", True)):
                self._cleanup_tile_buffers(
                    keep_reference=bool(config.get("cache_reference_pyramid", False))
                )
            self._vram_cleanup(
                "frame-complete",
                clear_pool=not bool(config.get("retain_native_pool", False)),
            )
            return res
        except Exception as exc:
            self._cleanup_tile_buffers()
            self._vram_cleanup("frame-error", clear_pool=True)

            LucasKanade._gpu_remap_disabled = True
            print(
                f"[LucasKanade] GPU remap path failed, falling back to Taichi host remap: {exc}"
            )
            return self._align_frame_host_fallback(
                reference,
                target,
                config=config,
                stop_requested=stop_requested,
                tile_executor=tile_executor,
                point_executor=point_executor,
                target_for_warping=target_for_warping,
            )

    def _align_frame_host_fallback(
        self,
        reference,
        target,
        config,
        stop_requested=None,
        tile_executor=None,
        point_executor=None,
        target_for_warping=None,
    ):
        fallback_config = dict(config)
        fallback_config["use_multi_core"] = True
        fallback_config["point_workers"] = max(
            2,
            int(fallback_config.get("point_workers", 2)),
        )

        def flow_func(reference_gray, target_gray):
            return self.calculate_flow(
                reference_gray,
                target_gray,
                fallback_config,
                point_executor=point_executor,
            )

        halo = int(fallback_config.get("win_size", 15)) + int(
            fallback_config.get("max_flow_px", 64.0)
        )
        return align_with_block_flow(
            reference,
            target,
            flow_func,
            halo=halo,
            use_multi_core=True,
            stop_requested=stop_requested,
            executor=tile_executor,
            target_for_warping=target_for_warping,
        )

    # Legacy alias
    _align_frame_cpu_fallback = _align_frame_host_fallback

    def _align_frame_gpu_flow_remap(
        self,
        reference,
        target,
        config,
        stop_requested=None,
        matching_reference=None,
        matching_target=None,
        return_gpu=False,
    ):
        from taichi_vision import taichi_aot

        t_total = time.perf_counter()
        profile = {
            "cpu_gray": 0.0,
            "prepare": 0.0,
            "gpu_upload": 0.0,
            "upload_color": 0.0,
            "upload_gray": 0.0,
            "flow_calc": 0.0,
            "warp": 0.0,
            "stitch": 0.0,
            "division": 0.0,
            "download": 0.0,
            "readback": 0.0,
            "dtype_restore": 0.0,
            "division_download": 0.0,
        }

        matching_reference = reference if matching_reference is None else matching_reference
        matching_target = target if matching_target is None else matching_target
        height, width = reference.shape[:2]
        tiles = self._build_tiles(width, height, config)
        single_full_frame_tile = (
            len(tiles) == 1
            and tiles[0]["roi"] == (0, 0, width, height)
            and tiles[0]["valid"] == (0, 0, width, height)
        )
        conservative_vram = bool(config.get("conservative_vram", True))

        ref_id = config.get("_reference_cache_key", id(matching_reference))
        if self._tile_buffers is None or self._current_ref_id != ref_id:
            self._cleanup_tile_buffers()
            self._tile_buffers = (
                {} if conservative_vram
                else self._init_tile_buffers(matching_reference, tiles, config)
            )
            self._current_ref_id = ref_id

        t_prepare = time.perf_counter()
        target_gray_full = (
            None
            if single_full_frame_tile
            else to_flow_gray_u8(matching_target).astype(np.float32, copy=False)
        )
        profile["prepare"] += time.perf_counter() - t_prepare

        accumulator = weights = None
        buffers = []
        if not single_full_frame_tile:
            accumulator, weights = self._create_gpu_accumulators(target)
            buffers = [accumulator, weights]

        pending_stitch = []
        pending_stitch_bytes = 0
        device_budget = taichi_aot.engine.get_device_block_cache().max_bytes
        stitch_batch_budget = max(1, device_budget // 2)

        def flush_stitch_batch():
            nonlocal pending_stitch_bytes
            if not pending_stitch:
                return
            fence_start = time.perf_counter()
            taichi_aot.engine.sync()
            profile["stitch"] += time.perf_counter() - fence_start
            for pending_idx in pending_stitch:
                self._cleanup_tile_buffer(
                    pending_idx,
                    keep_reference=bool(config.get("cache_reference_pyramid", False)),
                )
            pending_stitch.clear()
            pending_stitch_bytes = 0

        try:
            for idx, tile in enumerate(tiles):
                if stop_requested and stop_requested():
                    return None

                tile_buffers = self._tile_buffers.get(idx)
                if tile_buffers is None or "target_gpu" not in tile_buffers:
                    retained_reference = (
                        tile_buffers
                        if tile_buffers is not None
                        and tile_buffers.get("ref_gray_gpu") is not None
                        else None
                    )
                    if tile_buffers is not None:
                        self._cleanup_tile_buffer(idx, keep_reference=True)
                    self._tile_buffers[idx] = self._init_tile_buffer(
                        matching_reference,
                        tile,
                        config,
                        reuse_reference=retained_reference,
                    )

                warped_gpu = self._warp_tile_gpu(
                    tile,
                    reference,
                    target,
                    config,
                    profile=profile,
                    tile_idx=idx,
                    target_gray_full=target_gray_full,
                )
                if warped_gpu is None:
                    continue

                if single_full_frame_tile:
                    if return_gpu:
                        return warped_gpu

                    result = self._download_restore_dtype(
                        warped_gpu,
                        target.dtype,
                        profile,
                    )
                    return result

                t_stitch = time.perf_counter()
                self._accumulate_tile_gpu(
                    taichi_aot,
                    accumulator,
                    weights,
                    tile,
                    warped_gpu,
                    self._tile_buffers[idx]["hanning_gpu"],
                    self._tile_buffers[idx]["mask_gpu"],
                )
                profile["stitch"] += time.perf_counter() - t_stitch
                if conservative_vram:
                    pending_stitch.append(idx)
                    pending_stitch_bytes += sum(
                        int(getattr(value, "size_bytes", 0))
                        for value in self._tile_buffers[idx].values()
                    )
                    if pending_stitch_bytes >= stitch_batch_budget:
                        flush_stitch_batch()

            flush_stitch_batch()

            if return_gpu:
                return accumulator

            result = self._download_restore_dtype(
                accumulator,
                target.dtype,
                profile,
            )
            profile["division_download"] = profile["division"] + profile["download"]
            return result
        finally:
            taichi_aot.engine.sync()
            for pending_idx in list(pending_stitch):
                self._cleanup_tile_buffer(
                    pending_idx,
                    keep_reference=bool(config.get("cache_reference_pyramid", False)),
                )
            for buffer in buffers:
                if buffer is not None and hasattr(buffer, "release"):
                    buffer.release()

    @staticmethod
    def _build_tiles(width, height, config):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_aot.block import BlockGrid

        runtime_config = taichi_aot.get_block_config()
        if not runtime_config.enabled:
            return [{
                "roi": (0, 0, width, height),
                "valid": (0, 0, width, height),
                "block_index": 0,
            }]

        block_size = runtime_config.normalized_size()
        win_radius = max(2, int(config.get("win_size", 15)) // 2)
        motion_halo = int(np.ceil(float(config.get("max_flow_px", 64.0))))
        overlap_halo = int(max(block_size) * float(config.get("tile_overlap", 0.20)))
        halo = max(win_radius + motion_halo, overlap_halo)
        grid = BlockGrid((height, width), size=block_size, halo=halo)
        blocks = [
            {
                "roi": (block.read_x0, block.read_y0, block.read_x1, block.read_y1),
                "valid": (block.x0, block.y0, block.x1, block.y1),
                "block_index": block.index,
            }
            for block in grid
        ]
        return blocks

    @staticmethod
    def _create_gpu_accumulators(target):
        from taichi_vision import taichi_aot

        is_color = target.ndim == 3
        accumulator = taichi_aot.upload(
            np.zeros(target.shape, dtype=np.float32),
            is_vector=is_color,
        )
        weights = taichi_aot.upload(
            np.zeros(target.shape[:2], dtype=np.float32),
            is_vector=False,
        )
        return accumulator, weights

    def _download_restore_dtype(self, gpu_buffer, dtype, profile):
        t_download = time.perf_counter()
        read_buffer = gpu_buffer

        if (
            self._download_float_buffer is None
            or self._download_float_buffer.shape != read_buffer.shape
            or self._download_float_buffer.dtype != read_buffer.dtype
        ):
            self._download_float_buffer = np.empty(
                read_buffer.shape, dtype=read_buffer.dtype
            )

        t_readback = time.perf_counter()
        image = read_buffer.to_numpy(out=self._download_float_buffer)
        profile["readback"] += time.perf_counter() - t_readback

        t_restore = time.perf_counter()
        if np.issubdtype(dtype, np.integer):
            info = np.iinfo(dtype)
            np.clip(image, info.min, info.max, out=image)
            result = np.empty(image.shape, dtype=dtype)
            np.copyto(result, image, casting="unsafe")
        elif image.dtype == dtype:
            result = image.copy()
        else:
            result = image.astype(dtype, copy=False)
        profile["dtype_restore"] += time.perf_counter() - t_restore
        profile["download"] += time.perf_counter() - t_download
        return result

    def _warp_tile_gpu(
        self,
        tile,
        reference,
        target,
        config,
        profile=None,
        tile_idx=None,
        target_gray_full=None,
    ):
        from taichi_vision import taichi_aot

        rx0, ry0, rx1, ry1 = tile["roi"]
        ref_roi = reference[ry0:ry1, rx0:rx1]
        target_roi_original = target[ry0:ry1, rx0:rx1]

        if tile_idx is not None and self._tile_buffers is not None:
            bufs = self._tile_buffers[tile_idx]
            target_gpu = bufs["target_gpu"]
            ref_gray_gpu = bufs["ref_gray_gpu"]
            target_gray_gpu = bufs["target_gray_gpu"]
            warped_gpu = bufs["warped_gpu"]
            target_host = bufs["target_host"]
            target_gray_host = bufs["target_gray_host"]

            from taichi_vision.taichi_aot.engine import _LIB, _RUNTIME

            t0 = time.perf_counter()
            target_gray_view = (
                target_gray_full[ry0:ry1, rx0:rx1]
                if target_gray_full is not None
                else None
            )
            if profile is not None and target_gray_view is not None:
                profile["cpu_gray"] += time.perf_counter() - t0

            t0 = time.perf_counter()
            if hasattr(target_roi_original, "handle"):
                target_gpu = target_roi_original
                color_elapsed = 0.0
            else:
                np.copyto(target_host, target_roi_original, casting="unsafe")
                _LIB.write_to_gpu_buffer(
                    _RUNTIME,
                    target_gpu.handle,
                    target_host.ctypes.data,
                    target_gpu.nbytes,
                )
                color_elapsed = time.perf_counter() - t0

            t0 = time.perf_counter()
            if target_gray_view is not None:
                np.copyto(target_gray_host, target_gray_view, casting="unsafe")
                _LIB.write_to_gpu_buffer(
                    _RUNTIME,
                    target_gray_gpu.handle,
                    target_gray_host.ctypes.data,
                    target_gray_gpu.nbytes,
                )
            else:
                target_gray_gpu = taichi_aot.cvtColor(target_gpu, taichi_aot.COLOR_RGB2GRAY)
            gray_elapsed = time.perf_counter() - t0

            taichi_aot.engine.sync()
            if profile is not None:
                profile["upload_color"] += color_elapsed
                profile["upload_gray"] += gray_elapsed
                profile["gpu_upload"] += color_elapsed + gray_elapsed

            t0 = time.perf_counter()
            flow_gpu = self._calculate_flow_gpu_buffer(
                ref_gray_gpu,
                target_gray_gpu,
                config,
                reference_pyramid=bufs.get("reference_pyramid"),
            )
            taichi_aot.engine.sync()
            if bool(config.get("conservative_vram", True)):
                taichi_aot.engine.buffer_pool.clear()
            if profile is not None:
                profile["flow_calc"] += time.perf_counter() - t0

            t0 = time.perf_counter()
            roi_h, roi_w = ref_gray_gpu.shape[:2]
            taichi_aot.remap_with_flow(
                target_gpu,
                flow_gpu,
                roi_h,
                roi_w,
                dst=warped_gpu,
                return_gpu=True,
            )
            taichi_aot.engine.sync()
            if profile is not None:
                profile["warp"] += time.perf_counter() - t0

            if flow_gpu is not None and hasattr(flow_gpu, "release"):
                flow_gpu.release()

            return warped_gpu

        # Fallback if tile_idx is not provided (for standalone testing)
        ref_gpu = None
        target_gpu = None
        ref_gray_gpu = None
        target_gray_gpu = None
        flow_gpu = None

        try:
            target_gpu = taichi_aot.upload(
                target_roi_original.astype(np.float32, copy=False),
                is_vector=target_roi_original.ndim == 3,
            )
            ref_gray_cpu = to_flow_gray_u8(ref_roi).astype(np.float32, copy=False)
            target_gray_cpu = to_flow_gray_u8(target_roi_original).astype(
                np.float32, copy=False
            )
            ref_gray_gpu = taichi_aot.upload(ref_gray_cpu, is_vector=False)
            target_gray_gpu = taichi_aot.upload(target_gray_cpu, is_vector=False)

            indices = np.linspace(0.0, 1.0, 256, dtype=np.float32)
            s_curve = 0.5 - 0.5 * np.cos(np.pi * indices)
            lut_cpu = (1.0 - 0.50) * indices + 0.50 * s_curve
            lut_gpu = taichi_aot.upload(lut_cpu, is_vector=False)

            ref_blur_gpu = taichi_aot.box_filter(ref_gray_gpu, kernel_size=5, return_gpu=True)
            target_blur_gpu = taichi_aot.box_filter(target_gray_gpu, kernel_size=5, return_gpu=True)

            ref_gray_enhanced = taichi_aot.enhance_grayscale(
                ref_gray_gpu,
                ref_blur_gpu,
                lut_gpu,
                micro_contrast=0.30,
                clarity=0.30,
                return_gpu=True,
            )
            target_gray_enhanced = taichi_aot.enhance_grayscale(
                target_gray_gpu,
                target_blur_gpu,
                lut_gpu,
                micro_contrast=0.30,
                clarity=0.30,
                return_gpu=True,
            )

            taichi_aot.engine.sync()

            flow_gpu = self._calculate_flow_gpu_buffer(
                ref_gray_enhanced,
                target_gray_enhanced,
                config,
            )
            taichi_aot.engine.sync()

            roi_h, roi_w = ref_gray_gpu.shape[:2]
            warped_roi = taichi_aot.remap_with_flow(
                target_gpu,
                flow_gpu,
                roi_h,
                roi_w,
                return_gpu=True,
            )
            taichi_aot.engine.sync()
        finally:
            if flow_gpu is not None and hasattr(flow_gpu, "release"):
                flow_gpu.release()
            if ref_gray_gpu is not None and hasattr(ref_gray_gpu, "release"):
                ref_gray_gpu.release()
            if target_gray_gpu is not None and hasattr(target_gray_gpu, "release"):
                target_gray_gpu.release()
            if ref_gpu is not None and hasattr(ref_gpu, "release"):
                ref_gpu.release()
            if target_gpu is not None and hasattr(target_gpu, "release"):
                target_gpu.release()

        return warped_roi

    @staticmethod
    def _accumulate_tile_gpu(
        taichi_aot, accumulator, weights, tile, warped_gpu, hanning_gpu, mask_gpu
    ):
        rx0, ry0, _rx1, _ry1 = tile["roi"]
        taichi_aot.stitch_tile_normalized(
            warped_gpu,
            mask_gpu,
            hanning_gpu,
            accumulator,
            weights,
            ry0,
            rx0,
        )

    def _calculate_flow_grid_fallback(
        self, reference_gray, target_gray, config, lk_params
    ):
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLKGrid

        grid_result = calcOpticalFlowPyrLKGrid(
            reference_gray,
            target_gray,
            winSize=lk_params["winSize"],
            maxLevel=lk_params["maxLevel"],
            criteria=lk_params["criteria"],
            grid_step=max(1, int(config.get("grid_step", 48))),
            border_margin=max(0, int(config.get("border_margin", 8))),
            motion_mode=str(config.get("motion_mode", "fast")),
        )
        if isinstance(grid_result, tuple):
            grid_result = grid_result[0]
        if not grid_result or "grid_flow" not in grid_result:
            height, width = reference_gray.shape[:2]
            return np.zeros((height, width, 2), dtype=np.float32)
        return self._dense_from_aot_grid(reference_gray.shape[:2], grid_result)

    def _dense_from_aot_grid(self, shape, grid_result):
        height, width = shape
        grid_flow = np.asarray(grid_result["grid_flow"], dtype=np.float32)
        grid_h, grid_w = grid_flow.shape[:2]
        if grid_h <= 0 or grid_w <= 0:
            return np.zeros((height, width, 2), dtype=np.float32)

        valid = grid_flow[..., 2] > 0.5
        compact = np.zeros((grid_h, grid_w, 2), dtype=np.float32)
        compact[..., 0] = np.where(valid, grid_flow[..., 0], 0.0)
        compact[..., 1] = np.where(valid, grid_flow[..., 1], 0.0)

        if not np.any(valid):
            return np.zeros((height, width, 2), dtype=np.float32)

        valid_f = valid.astype(np.float32)

        def box_blur(array):
            padded = np.pad(array, ((1, 1), (1, 1)), mode="edge")
            return sum(
                padded[dy : dy + array.shape[0], dx : dx + array.shape[1]]
                for dy in range(3)
                for dx in range(3)
            ) / 9.0

        for _ in range(3):
            missing = valid_f <= 0
            if not np.any(missing):
                break
            blurred_weight = box_blur(valid_f)
            can_fill = missing & (blurred_weight > 1e-6)
            if not np.any(can_fill):
                break
            for channel in (0, 1):
                blurred_flow = box_blur(compact[..., channel] * valid_f)
                compact[..., channel][can_fill] = (
                    blurred_flow[can_fill] / blurred_weight[can_fill]
                )
            valid_f[can_fill] = 1.0

        from taichi_vision import taichi_aot

        compact_gpu = taichi_aot.upload(compact, is_vector=True, vector_dim=2)
        try:
            flow = taichi_aot.resize(
                compact_gpu,
                (width, height),
                interpolation=taichi_aot.INTER_NEAREST,
                return_gpu=False,
            )
        finally:
            compact_gpu.destroy()
        return np.ascontiguousarray(flow, dtype=np.float32)

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)


# Canonical Aliases
LucasKanadeFlow = LucasKanade
LucasKanadeGPU = LucasKanade
LucasKanadeCPU = LucasKanade
