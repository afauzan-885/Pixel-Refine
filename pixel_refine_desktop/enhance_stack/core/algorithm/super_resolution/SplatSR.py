import os
import gc
import time
import traceback
import sqlite3
import h5py
import numpy as np
import cv2
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    extract_all_metadata,
    normalize_image,
    save_image,
    setup_balanced_batching,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    resize_all_with_padding,
    cleanup_old_hdf5_files,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config

class SplatSRAlgorithm:

    def __init__(self, db_path, hdf5_path="database/align/aligned_images.h5"):
        self.db_path = db_path
        self.hdf5_path = hdf5_path

        hdf5_folder = os.path.dirname(self.hdf5_path)
        if not os.path.exists(hdf5_folder):
            os.makedirs(hdf5_folder)

    def get_all_image_paths_for_batch_process(self, batch_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT images.path 
                FROM batch_process_image
                JOIN images ON batch_process_image.image_id_batch = images.id
                WHERE batch_process_image.batch_id = ?
                ORDER BY batch_process_image.is_reference_batch DESC, images.path ASC
            """,
                (batch_id,),
            )
            return [row[0] for row in cursor.fetchall()]

    def compute_spatial_weight_maps(self, lr_frames, noise_std=0.015, sensitivity=120.0):
        """
        Computes Spatial Weight Maps (W_k) relative to reference frame Y_ref (lr_frames[0]).
        Matches the concept of tile rejection / ghosting suppression using Local-MSE window calculation.
        """
        # Handle potential 4D shape: (num_frames, h, w, channels)
        if lr_frames.ndim == 4:
            num_frames, h, w, channels = lr_frames.shape
            # Create a 3D grayscale representation for weight calculation
            lr_gray = np.zeros((num_frames, h, w), dtype=np.float32)
            for k in range(num_frames):
                lr_gray[k] = cv2.cvtColor(lr_frames[k], cv2.COLOR_RGB2GRAY)
            ref_frame = lr_gray[0]
            weight_maps = np.ones((num_frames, h, w), dtype=np.float32)
        else:
            num_frames, h, w = lr_frames.shape
            ref_frame = lr_frames[0]
            weight_maps = np.ones_like(lr_frames)
            lr_gray = lr_frames
        
        # Calculate local window differences
        for k in range(1, num_frames):
            diff = lr_gray[k] - ref_frame

            # Compute Local MSE via Gaussian Blur
            local_mse = cv2.GaussianBlur((diff * diff).astype(np.float32), (5, 5), sigmaX=1.0)
            
            # Tile rejection mapping formula
            # Areas with high Local-MSE (movement/misalignment) get weights near 0
            w_k = np.exp(-local_mse / (noise_std * noise_std * 2.0))
            # Smooth out and clamp
            w_k = np.clip(w_k * sensitivity, 0.0, 1.0)
            weight_maps[k] = w_k
            
        return weight_maps

    def _estimate_internal_block_matching_flow(
        self, frames, update_progress=None, stop_requested=None
    ):
        """Estimate burst motion with the same BlockMatchingGPU path as SpatialFusion.

        This is deliberately an internal stage of SplatSR: it does not invoke the
        application's external alignment/HDF5 pipeline.  The returned vectors use
        the SplatSR contract ``[..., 0] = dx`` and ``[..., 1] = dy`` in LR pixels.
        If a block-matching graph is unavailable, phase correlation is used only as
        an explicit same-backend recovery and is logged as such.
        """
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
            BlockMatchingGPU,
        )

        n, h, w = frames.shape
        flow = np.zeros((n, h, w, 2), dtype=np.float32)
        if n <= 1:
            return flow
        matcher = BlockMatchingGPU()
        config = matcher.load_config()
        print(
            "[splattingSR] internal alignment=block_matching "
            f"mode={config.get('mode', 'fast')} grid_step={config.get('grid_step')}"
        )
        for k in range(1, n):
            if stop_requested and stop_requested():
                return None
            flow[k] = self._estimate_internal_block_matching_pair(
                matcher, config, frames[0], frames[k], k
            )
            if update_progress:
                update_progress(
                    8 + int((k / max(n - 1, 1)) * 8),
                    f"Block-matching alignment {k}/{n - 1}...",
                )
        return flow

    @staticmethod
    def _estimate_spatial_alignment_flow(
        frames, *, update_progress=None, stop_requested=None, proxy_scale=1.0
    ):
        """Reuse SpatialFusion's alignment graph and return dense full-res flow."""
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.alignment_core import (
            perform_alignment_gpu,
        )

        n, h, w = frames.shape
        work_h = max(64, int(round(h * proxy_scale)))
        work_w = max(64, int(round(w * proxy_scale)))
        work_h -= work_h % 2
        work_w -= work_w % 2
        alignment_images = [np.ascontiguousarray(frame, dtype=np.float32) for frame in frames]
        result = perform_alignment_gpu(
            alignment_images,
            np.ascontiguousarray(frames[0], dtype=np.float32),
            work_h,
            work_w,
            16,
            16,
            np.float32,
            update_progress=update_progress,
            stop_requested=stop_requested,
            save_align_image=False,
            harvest_alignment=False,
            return_format="flow_only",
            optical_flow_type="alignment_tile",
            proxy_scale=proxy_scale,
            return_flow=True,
            full_h_ref=h,
            full_w_ref=w,
        )
        if not isinstance(result, tuple) or len(result) != 2:
            raise RuntimeError("SpatialFusion alignment did not return dense flow")
        success, captured = result
        if not success:
            raise RuntimeError("SpatialFusion alignment reported failure")
        flow = np.zeros((n, h, w, 2), dtype=np.float32)
        for index in range(1, n):
            plane = captured.get(index)
            if plane is None:
                raise RuntimeError(f"SpatialFusion alignment omitted frame {index}")
            flow[index] = np.asarray(plane, dtype=np.float32)
        return flow

    @staticmethod
    def _estimate_internal_block_matching_pair(
        matcher, config, reference, target, index, matching_scale=1.0
    ):
        """Return one dense LR flow plane, with explicit same-backend recovery."""
        h, w = reference.shape
        matching_scale = float(max(1.0e-3, min(1.0, matching_scale)))
        if matching_scale < 0.999:
            proxy_h = max(32, int(round(h * matching_scale)))
            proxy_w = max(32, int(round(w * matching_scale)))
            matching_reference = cv2.resize(
                reference, (proxy_w, proxy_h), interpolation=cv2.INTER_AREA
            )
            matching_target = cv2.resize(
                target, (proxy_w, proxy_h), interpolation=cv2.INTER_AREA
            )
        else:
            matching_reference, matching_target = reference, target
        # Vulkan on older hybrid GPUs has a large one-time graph/queue latency
        # for BlockMatchingGPU (observed even at 192x256).  Splatting only
        # needs a bounded motion proxy, so use OpenCV phase correlation for
        # that case.  The result is expanded to the same dense flow contract;
        # CUDA/OpenGL and an explicit override still use the native matcher.
        try:
            from taichi_vision.taichi_aot import engine as active_engine
            active_arch = str(getattr(active_engine, "arch", "")).lower()
        except Exception:
            active_arch = ""
        use_phase_proxy = (
            matching_scale < 0.999
            and active_arch == "vulkan"
            and os.environ.get("SPLATSR_VULKAN_NATIVE_FLOW", "0") != "1"
        )
        if use_phase_proxy:
            try:
                if max(
                    float(np.std(matching_reference)),
                    float(np.std(matching_target)),
                ) < 1.0e-5:
                    dx = dy = 0.0
                    response = 0.0
                else:
                    (dx, dy), response = cv2.phaseCorrelate(
                        np.ascontiguousarray(matching_reference, dtype=np.float32),
                        np.ascontiguousarray(matching_target, dtype=np.float32),
                    )
                    # A phase peak outside the configured motion envelope is
                    # an ambiguous/low-texture result, not a valid warp.
                    max_flow = float(config.get("max_flow_px", 48.0))
                    max_proxy_flow = max_flow * float(matching_scale)
                    dx = float(np.clip(dx, -max_proxy_flow, max_proxy_flow))
                    dy = float(np.clip(dy, -max_proxy_flow, max_proxy_flow))
                pair = np.empty((h, w, 2), dtype=np.float32)
                pair[..., 0] = np.float32(dx) / np.float32(matching_scale)
                pair[..., 1] = np.float32(dy) / np.float32(matching_scale)
                print(
                    f"[splattingSR] Vulkan proxy flow=phase_correlation "
                    f"frame={index} response={float(response):.3f}"
                )
                return pair
            except Exception as exc:
                print(f"[splattingSR] phase proxy failed; trying native flow: {exc}")
        try:
            pair = matcher.calculate_flow(
                np.ascontiguousarray(matching_reference, dtype=np.float32),
                np.ascontiguousarray(matching_target, dtype=np.float32),
                config,
            )
            pair = np.asarray(pair, dtype=np.float32)
            if pair.ndim != 3 or pair.shape[-1] != 2 or not np.isfinite(pair).all():
                raise ValueError(f"unexpected flow shape {pair.shape}")
            if pair.shape[:2] != (h, w):
                pair = np.stack(
                    [
                        cv2.resize(pair[..., axis], (w, h), interpolation=cv2.INTER_LINEAR)
                        / np.float32(matching_scale)
                        for axis in range(2)
                    ],
                    axis=-1,
                )
            return np.ascontiguousarray(pair)
        except Exception as exc:
            print(
                f"[splattingSR] block_matching frame {index} failed; "
                f"same-backend phase recovery: {exc}"
            )
            from taichi_vision.taichi_aot import phase_correlation

            dx, dy, _ = phase_correlation(
                matching_reference, matching_target, use_hanning=True
            )
            pair = np.empty((h, w, 2), dtype=np.float32)
            pair[..., 0] = np.float32(dx) / np.float32(matching_scale)
            pair[..., 1] = np.float32(dy) / np.float32(matching_scale)
            return pair

    def run_splatting_sr(
        self,
        images,
        scale=2,
        update_progress=None,
        stop_requested=None,
        alignment_method="block_matching",
        num_iterations=None,
    ):
        """Confidence-guided subpixel splatting reconstruction.

        Confidence generation and high-resolution reconstruction are kept as
        separate stages.  The native AOT graph is attempted first; while its
        ABI qualification is still pending, the deterministic NumPy oracle is
        used as an explicit, logged recovery path rather than silently using
        the retired iterative weighted-mean solver.
        """
        # ``num_iterations`` belongs to the retired iterative SR API.  Keep
        # accepting it so existing callers and saved sessions remain
        # compatible; the confidence-guided splat path is non-iterative.
        del num_iterations
        from .spatial_splat_sr import (
            robust_subpixel_splat,
            robust_subpixel_splat_stream,
        )

        if not images:
            return None
        ref = images[0]
        dtype_ref = ref.dtype
        color = ref.ndim == 3 and ref.shape[2] == 3
        ys = []
        chroma = None
        for image in images:
            if stop_requested and stop_requested():
                return None
            if color:
                yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
                if chroma is None:
                    chroma = (yuv[..., 1], yuv[..., 2])
                ys.append(normalize_image(yuv[..., 0], dtype_ref)[..., 0])
            else:
                ys.append(normalize_image(image, dtype_ref)[..., 0])
        frames = np.ascontiguousarray(np.stack(ys).astype(np.float32))
        n, h, w = frames.shape
        if update_progress:
            update_progress(8, "Estimating internal block-matching flow...")
        if str(alignment_method or "block_matching").strip().lower() != "block_matching":
            raise ValueError(
                "splattingSR requires internal block_matching alignment; "
                "external alignment is not supported"
            )
        # For large frames, stream one flow/confidence plane at a time.  The
        # previous full-frame path materialized flow[N,H,W,2] and confidence
        # [N,H,W] simultaneously, which can exceed system RAM while leaving
        # VRAM mostly idle during host-side preparation.
        import config as app_config
        block_settings = app_config.get_compute_block_settings()
        block_size = int(block_settings.get("block_size", 1024))
        threshold_mp = float(block_settings.get("threshold_mp", 12.0))
        block_enabled = bool(block_settings.get("enabled", True)) and (
            (h * w) / 1.0e6 >= threshold_mp
        )
        if block_enabled:
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import BlockMatchingGPU
            from .spatial_weight_pipeline import generate_spatial_weight_map_blockwise

            matcher = BlockMatchingGPU()
            matcher_config = matcher.load_config()
            cache = {}
            reference = frames[0]
            # Motion estimation is only a low-resolution control signal for
            # splatting.  Dispatching Lucas-Kanade on a 1024px proxy can take
            # tens of seconds on MX150/Vulkan and leaves the watchdog with no
            # heartbeat.  Keep the proxy bounded to 256px (the dense flow is
            # upsampled back to the source resolution below).
            flow_proxy_max = max(
                128,
                int(os.environ.get("SPLATSR_FLOW_PROXY_MAX", "256")),
            )
            flow_proxy_scale = min(1.0, flow_proxy_max / float(max(h, w)))
            # The proxy is not the final alignment product.  Use a bounded
            # fast LK configuration so a driver cannot spend an unbounded
            # amount of time building a deep pyramid for every burst frame.
            matcher_config = dict(matcher_config)
            matcher_config.update(
                grid_step=max(64, int(matcher_config.get("grid_step", 48))),
                win_size=min(13, int(matcher_config.get("win_size", 13))),
                max_level=0,
                iterations=1,
                motion_mode="fast",
                adaptive=False,
            )
            print(
                f"[splattingSR] block_matching flow proxy="
                f"{flow_proxy_scale:.3f} ({max(32, int(h * flow_proxy_scale))}x"
                f"{max(32, int(w * flow_proxy_scale))})"
            )

            def flow_provider(index):
                if index not in cache:
                    if index == 0:
                        cache[index] = np.zeros((h, w, 2), dtype=np.float32)
                    else:
                        if update_progress:
                            update_progress(
                                9 + int((index / max(n - 1, 1)) * 12),
                                f"SpatialFusion alignment {index + 1}/{n}...",
                            )
                        # Process one source frame at a time.  This is the
                        # same SpatialFusion alignment graph, but avoids
                        # retaining the complete burst flow tensor in RAM.
                        try:
                            pair_flow = self._estimate_spatial_alignment_flow(
                                np.ascontiguousarray(
                                    frames[[0, index]], dtype=np.float32
                                ),
                                update_progress=update_progress,
                                stop_requested=stop_requested,
                                proxy_scale=flow_proxy_scale,
                            )
                            cache[index] = np.ascontiguousarray(
                                pair_flow[1], dtype=np.float32
                            )
                            print(
                                f"[splattingSR] alignment=SpatialFusion frame {index + 1}/{n}"
                            )
                        except Exception as exc:
                            print(
                                f"[splattingSR] SpatialFusion frame {index + 1} "
                                f"unavailable; same-backend block matcher recovery: {exc}"
                            )
                            cache[index] = self._estimate_internal_block_matching_pair(
                                matcher,
                                matcher_config,
                                reference,
                                frames[index],
                                index,
                                matching_scale=flow_proxy_scale,
                            )
                    if update_progress:
                        update_progress(
                            10 + int((index / max(n - 1, 1)) * 12),
                            f"Block-matching flow {index + 1}/{n}",
                        )
                return cache[index]

            def confidence_provider(index):
                flow_plane = flow_provider(index)
                if index == 0:
                    return np.ones((h, w), dtype=np.float32)
                # Use the exact SpatialFusion AOT weight stage.  It is
                # evaluated blockwise so the reference pyramid, gradients,
                # and weight accumulator never occupy full-frame residency.
                if update_progress:
                    update_progress(
                        20 + int((index / max(n - 1, 1)) * 4),
                        f"SpatialFusion weight map {index + 1}/{n}",
                    )
                result = generate_spatial_weight_map_blockwise(
                    reference,
                    frames[index],
                    flow_plane,
                    block_size=block_size,
                    halo=max(32, int(matcher_config.get("win_size", 13))),
                    tile_size=min(256, block_size),
                    overlap=0.2,
                    motion_sensitivity=1.0,
                    noise_offset_factor=0.0,
                    noise_sigma=0.015,
                    early_exit_threshold=0.05,
                )
                # The stream asks for each flow before its confidence.  Once
                # this frame is accumulated, release its dense flow plane.
                cache.pop(index, None)
                return result

            print(
                f"[splattingSR] compute_block=enabled size={block_size}px "
                f"threshold={threshold_mp:g}MP; streaming flow/compute_spatial weights"
            )
            try:
                from .spatial_splat_runtime import SpatialSplatAOT

                native_splat = SpatialSplatAOT()
                result, _ = native_splat.run_streaming(
                    frames[..., None],
                    flow_provider,
                    confidence_provider,
                    scale=scale,
                    block_size=block_size,
                    progress_callback=(
                        lambda done, total: update_progress(
                            24 + int((done / max(total, 1)) * 72),
                            f"Native splatting blocks {done}/{total}",
                        )
                        if update_progress
                        else None
                    ),
                )
                print(
                    f"[splattingSR] native block splat backend={native_splat.backend} "
                    f"size={block_size}px"
                )
            except Exception as native_error:
                try:
                    from taichi_vision.taichi_aot import get_engine

                    active_backend = str(getattr(get_engine(), "arch", "cpu")).lower()
                except Exception:
                    active_backend = "cpu"
                if active_backend != "cpu":
                    raise RuntimeError(
                        "Native block splatting is unavailable for the active "
                        f"{active_backend} backend: {native_error}. Rebuild "
                        "spatial_splat_<backend>.tcm with the active bridge or "
                        "disable compute blocks to use the native full-frame graph."
                    ) from native_error
                print(
                    "[splattingSR] CPU native block graph unavailable; using "
                    f"explicit CPU oracle recovery: {native_error}"
                )
                result, _ = robust_subpixel_splat_stream(
                    frames[..., None],
                    flow_provider,
                    confidence_provider,
                    scale=scale,
                    block_size=block_size,
                    progress_callback=(
                        lambda done, total: update_progress(
                            24 + int((done / max(total, 1)) * 72),
                            f"Splatting blocks {done}/{total}",
                        )
                        if update_progress
                        else None
                    ),
                )
            cache.clear()
            # The caller may retain the original colour images for UI/cache
            # purposes.  Release this large luminance stack before upsampling
            # chroma so host RAM does not grow across repeated runs.
            del frames
            gc.collect()
            if np.issubdtype(dtype_ref, np.integer):
                max_val = np.iinfo(dtype_ref).max
                y_hr = np.clip(result[..., 0] * max_val, 0, max_val).astype(dtype_ref)
            else:
                y_hr = np.clip(result[..., 0], 0.0, 1.0).astype(dtype_ref)
            if color:
                cr = cv2.resize(chroma[0], (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
                cb = cv2.resize(chroma[1], (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
                return cv2.cvtColor(cv2.merge([y_hr, cr, cb]), cv2.COLOR_YCrCb2RGB)
            return y_hr

        try:
            flow = self._estimate_spatial_alignment_flow(
                frames,
                update_progress=update_progress,
                stop_requested=stop_requested,
                proxy_scale=1.0,
            )
            print("[splattingSR] alignment=SpatialFusion shared flow")
        except Exception as exc:
            print(
                f"[splattingSR] shared SpatialFusion alignment unavailable; "
                f"using bounded same-backend flow fallback: {exc}"
            )
            flow = self._estimate_internal_block_matching_flow(
                frames, update_progress=update_progress, stop_requested=stop_requested
            )
        if flow is None:
            return None
        # Use the exact SpatialFusion AOT weight stage before splatting.  The
        # flow is used only to warp the analysis view; the original frames and
        # flow remain the inputs to the sub-pixel splat accumulator.
        from .spatial_weight_pipeline import SpatialWeightMapGenerator

        with SpatialWeightMapGenerator(
            frames[0], tile_size=256, overlap=0.2, noise_sigma=0.015
        ) as weight_generator:
            confidence = np.stack(
                [
                    np.ones((h, w), dtype=np.float32)
                    if index == 0
                    else weight_generator.generate(frames[index], flow[index])
                    for index in range(n)
                ],
                axis=0,
            )
        try:
            from .spatial_splat_runtime import SpatialSplatAOT
            if update_progress:
                update_progress(20, "Running native GPU subpixel splatting...")
            result, _ = SpatialSplatAOT().run(
                frames[..., None], confidence, flow, scale=scale
            )
        except Exception as native_error:
            try:
                from taichi_vision.taichi_aot import get_engine

                active_backend = str(getattr(get_engine(), "arch", "cpu")).lower()
            except Exception:
                active_backend = "cpu"
            if active_backend != "cpu":
                raise RuntimeError(
                    "Native full-frame splatting is unavailable for the active "
                    f"{active_backend} backend: {native_error}. Rebuild "
                    "spatial_splat_<backend>.tcm with the active bridge."
                ) from native_error
            print(
                "[splattingSR] CPU native graph unavailable; using explicit "
                f"CPU oracle recovery: {native_error}"
            )
            if update_progress:
                update_progress(20, "Native splat ABI unavailable; using CPU oracle...")
            result, _ = robust_subpixel_splat(
                frames[..., None], flow=flow, confidence=confidence, scale=scale
            )
        if np.issubdtype(dtype_ref, np.integer):
            max_val = np.iinfo(dtype_ref).max
            y_hr = np.clip(result[..., 0] * max_val, 0, max_val).astype(dtype_ref)
        else:
            y_hr = np.clip(result[..., 0], 0.0, 1.0).astype(dtype_ref)
        if color:
            cr = cv2.resize(chroma[0], (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
            cb = cv2.resize(chroma[1], (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)
            return cv2.cvtColor(cv2.merge([y_hr, cr, cb]), cv2.COLOR_YCrCb2RGB)
        return y_hr


    def run_super_resolution(
        self,
        images,
        scale=2,
        num_iterations=120,
        update_progress=None,
        stop_requested=None,
        total_overall_images=None,
        images_processed_so_far=0,
    ):
        if not isinstance(images, list) or not images:
            return None

        from .splat_sr import TaichiSplatSR

        try:
            ref_image = images[0]
            dtype_ref = ref_image.dtype
            h_ref, w_ref = ref_image.shape[:2]
            
            is_color = ref_image.ndim == 3 and ref_image.shape[2] == 3
            if is_color:
                # Convert reference image to YCrCb to extract Cb and Cr channels
                ref_ycbcr = cv2.cvtColor(ref_image, cv2.COLOR_RGB2YCrCb)
                _, cr_ref, cb_ref = cv2.split(ref_ycbcr)
            
            # Normalize to float32 range [0.0, 1.0]
            lr_frames = []
            for img in images:
                if stop_requested and stop_requested():
                    return None
                if is_color:
                    # Convert to YCrCb and extract Y (luminance) channel for super resolution
                    img_yuv = cv2.cvtColor(img, cv2.COLOR_RGB2YCrCb)
                    y_channel = img_yuv[:, :, 0]
                    norm_img = normalize_image(y_channel, dtype_ref)[:, :, 0]
                else:
                    norm_img = normalize_image(img, dtype_ref)
                    if norm_img.ndim == 3:
                        norm_img = norm_img[:, :, 0]
                lr_frames.append(norm_img)
                
            lr_frames = np.array(lr_frames)
            num_frames = len(lr_frames)
            
            # 1. Estimate real sub-pixel shifts using Taichi AOT Phase Correlation
            from taichi_vision.taichi_aot import phase_correlation
            if update_progress:
                update_progress(3, "Estimating sub-pixel shifts...")
                
            shifts = np.zeros((num_frames, 2), dtype=np.float32)
            for k in range(1, num_frames):
                if stop_requested and stop_requested():
                    return None
                dx, dy, _ = phase_correlation(lr_frames[0], lr_frames[k], use_hanning=True)
                shifts[k] = [dy * scale, dx * scale]

            # 2. Compute Spatial Weight Maps for Ghosting Rejection
            if update_progress:
                update_progress(5, "Calculating spatial similarity weight maps...")
            weight_maps = self.compute_spatial_weight_maps(lr_frames)

            # 3. Setup Tiling and Accumulators
            lr_h, lr_w = lr_frames[0].shape[:2]
            hr_h, hr_w = lr_h * scale, lr_w * scale
            
            hr_accumulator = np.zeros((hr_h, hr_w), dtype=np.float32)
            weight_accumulator = np.zeros((hr_h, hr_w), dtype=np.float32)
            
            tile_size = 512
            overlap = 0.3
            
            tile_h = min(tile_size, lr_h)
            tile_w = min(tile_size, lr_w)
            
            step_y = int(tile_h * (1.0 - overlap)) if tile_h < lr_h else lr_h
            step_x = int(tile_w * (1.0 - overlap)) if tile_w < lr_w else lr_w
            
            y_starts = []
            y = 0
            while y + tile_h <= lr_h:
                y_starts.append(y)
                if y + tile_h == lr_h:
                    break
                y = min(y + step_y, lr_h - tile_h)
                
            x_starts = []
            x = 0
            while x + tile_w <= lr_w:
                x_starts.append(x)
                if x + tile_w == lr_w:
                    break
                x = min(x + step_x, lr_w - tile_w)
                
            total_tiles = len(y_starts) * len(x_starts)
            processed_tiles = 0

            # 4. Iterate over tiles
            for y_start in y_starts:
                for x_start in x_starts:
                    if stop_requested and stop_requested():
                        return None
                        
                    tile_lr = lr_frames[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
                    tile_weight = weight_maps[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
                    
                    tile_hr_h = tile_h * scale
                    tile_hr_w = tile_w * scale
                    
                    # Create SR solver (AOT engine handles GPU allocation)
                    solver = TaichiSplatSR(
                        lr_shape=(tile_h, tile_w),
                        hr_shape=(tile_hr_h, tile_hr_w),
                        num_frames=num_frames,
                        scale=scale,
                        alpha=0.7,
                        beta=0.005,
                        btv_window=2
                    )
                    solver.set_lr_data(tile_lr, tile_weight, shifts)
                            
                    # Set initial estimate via bicubic upsampling
                    init_hr = cv2.resize(tile_lr[0], (tile_hr_w, tile_hr_h), interpolation=cv2.INTER_CUBIC)
                    if init_hr.ndim == 3:
                        init_hr = init_hr[:, :, 0]
                        
                    solver.set_initial_hr(init_hr)
                    
                    # Iterative Optimization Loop for Tile
                    for step_idx in range(num_iterations):
                        if stop_requested and stop_requested():
                            return None
                        if step_idx > 0 and step_idx % 25 == 0:
                            solver.beta *= 0.90
                        solver.step(lam=0.001)
                        
                    tile_hr_res = solver.get_hr_image()
                    
                    # Generate Hanning window for tile stitching
                    win_y = np.hanning(tile_hr_h + 2)[1:-1].astype(np.float32)
                    win_x = np.hanning(tile_hr_w + 2)[1:-1].astype(np.float32)
                    win = np.outer(win_y, win_x)
                        
                    # Accumulate to global high-resolution buffers
                    y_hr_start = y_start * scale
                    x_hr_start = x_start * scale
                    hr_accumulator[y_hr_start:y_hr_start+tile_hr_h, x_hr_start:x_hr_start+tile_hr_w] += tile_hr_res * win
                    weight_accumulator[y_hr_start:y_hr_start+tile_hr_h, x_hr_start:x_hr_start+tile_hr_w] += win
                    
                    # Release solver resources
                    del solver
                    del tile_hr_res
                    del win
                    gc.collect()
                    
                    processed_tiles += 1
                    if update_progress:
                        prog_val = 10 + int((processed_tiles / total_tiles) * 85)
                        update_progress(prog_val, f"Processing super-resolution tile {processed_tiles}/{total_tiles}...")

            # 5. Final Stitching normalization and scaling
            if update_progress:
                update_progress(98, "Stitching and normalizing tiles...")
                
            valid_mask = weight_accumulator > 1e-6
            final_hr = np.zeros_like(hr_accumulator)
            final_hr[valid_mask] = hr_accumulator[valid_mask] / weight_accumulator[valid_mask]
            
            max_val = np.iinfo(dtype_ref).max
            final_result = np.clip(final_hr * max_val, 0, max_val).astype(dtype_ref)
            
            if is_color:
                # Upscale chrominance channels to match high-resolution shape
                cb_hr = cv2.resize(cb_ref, (hr_w, hr_h), interpolation=cv2.INTER_CUBIC)
                cr_hr = cv2.resize(cr_ref, (hr_w, hr_h), interpolation=cv2.INTER_CUBIC)
                # Merge back to YCrCb and convert to RGB
                yuv_hr = cv2.merge([final_result, cr_hr, cb_hr])
                final_color = cv2.cvtColor(yuv_hr, cv2.COLOR_YCrCb2RGB)
                return final_color
                
            return final_result

        except Exception as e:
            traceback.print_exc()
            raise e


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
):
    try:
        if update_progress:
            update_progress(0, "Initiating splattingSR process...")

        image_processor = SplatSRAlgorithm(db_path)
        align_dir = os.path.join("database", "align")
        output_folder_stack = "database/stack"
        os.makedirs(output_folder_stack, exist_ok=True)

        image_paths = []
        if single_process:
            hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            image_paths = get_all_image_paths_for_single_process(db_path)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else "single_process"
            # SplattingSR owns alignment internally.  Never consume an
            # externally aligned HDF5 product here; doing so would align the
            # burst before the internal BlockMatchingGPU stage.
            data_source = image_paths
        else:
            if batch_id is None:
                raise ValueError("Batch ID must be provided for batch processing.")
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = image_processor.get_all_image_paths_for_batch_process(batch_id)
            ref_name = os.path.splitext(os.path.basename(image_paths[0]))[0] if image_paths else f"batch_{batch_id}"
            # Keep the raw/session image order and let the internal
            # BlockMatchingGPU stage estimate motion.  The SpatialFusion
            # HDF5 alignment cache is deliberately not an input to SplatSR.
            data_source = image_paths

        cleanup_old_hdf5_files(hdf5_path)

        output_name_safe = "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip() or "sr_result"
        output_path = os.path.join(output_folder_stack, f"{output_name_safe}_splattingSR.tif")

        # Load images
        if update_progress:
            update_progress(5, "Loading image files...")
            
        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as h5f:
                keys = list(h5f.keys())
                images = [np.array(h5f[key]) for key in keys]
        else:
            images = load_images_from_paths(image_paths, stop_requested)

        # Run process
        final_result = image_processor.run_splatting_sr(
            images,
            scale=2,
            num_iterations=120,
            update_progress=update_progress,
            stop_requested=stop_requested
        )

        if final_result is not None:
            save_success = save_image(final_result, output_path, reference_image_path=image_paths[0] if image_paths else None)
            final_message = f"Process finished successfully: {os.path.basename(output_path)}" if save_success else "Failed to save result image."
            if update_progress:
                update_progress(100, final_message)
        else:
            if update_progress:
                update_progress(100, "Failed to run super resolution.")

    except Exception as e:
        traceback.print_exc()
        if update_progress:
            update_progress(0, f"Error: {str(e)}")


def running_splatting_sr(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    controller = getattr(parent, "controller", None)
    db_path = getattr(controller, "db_path", None)
    db_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not db_path:
        raise RuntimeError(
            "A session database is required for splattingSR. "
            "Set PIXEL_REFINE_SESSION_DB or pass db_path explicitly."
        )

    if batch_id is not None and progress_callback is not None:
        main(
            db_path=db_path,
            update_progress=progress_callback,
            stop_requested=stop_callback,
            single_process=False,
            batch_id=batch_id,
        )
        return

    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle("splattingSR")
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

    layout = QVBoxLayout(dialog)
    label = QLabel("Starting processing...")
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    worker = BaseAlgorithmWorker(
        main,
        db_path,
        single_process=single_process,
        batch_id=batch_id,
    )
    worker.progress_updated.connect(lambda progress, message: (progress_bar.setValue(progress), label.setText(message)))

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)
    worker.error_occurred.connect(lambda err: (QMessageBox.critical(dialog, "Error", f"Error occurred: {err}"), dialog.close(), worker.quit(), worker.wait()))

    dialog.closeEvent = lambda ev: ev.accept() if process_finished else (ev.accept() if not worker.isRunning() else (worker.stop(), worker.quit(), worker.wait(), ev.accept()) if QMessageBox.question(dialog, "Cancel Process", "Do you want to cancel?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes else ev.ignore())
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    db_path = os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not db_path:
        raise SystemExit(
            "Set PIXEL_REFINE_SESSION_DB before running splattingSR directly."
        )
    main(db_path)
