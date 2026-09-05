import os
import gc
import json
import traceback
import sqlite3
import tempfile
import numpy as np
import cv2
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt

from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    normalize_image,
    save_image,
    save_image_streaming,
    get_all_image_paths_for_single_process,
    cleanup_old_hdf5_files,
)
from pixel_refine_desktop.ui.views.settings.General.Language import language_config


def _create_splat_hr_accumulator(shape, directory=None):
    """Create paired disk-backed float32 HR numerator/denominator arrays."""
    if directory is None:
        directory = os.path.abspath(
            os.path.join("database", "cache", "splatting_sr")
        )
    os.makedirs(directory, exist_ok=True)
    numerator_path = None
    denominator_path = None
    numerator = None
    denominator = None
    try:
        handle, numerator_path = tempfile.mkstemp(
            prefix="splat_hr_",
            suffix=".numerator.f32",
            dir=directory,
        )
        os.close(handle)
        denominator_path = numerator_path.replace(
            ".numerator.f32", ".denominator.f32"
        )
        numerator = np.memmap(
            numerator_path,
            mode="w+",
            dtype=np.float32,
            shape=shape,
        )
        denominator = np.memmap(
            denominator_path,
            mode="w+",
            dtype=np.float32,
            shape=shape[:2],
        )
        numerator[...] = 0.0
        denominator[...] = 0.0
        numerator.flush()
        denominator.flush()
        return (numerator, denominator), (numerator_path, denominator_path)
    except Exception:
        for mapping in (numerator, denominator):
            if mapping is not None:
                try:
                    mapping._mmap.close()
                except Exception:
                    pass
        for path in (numerator_path, denominator_path):
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass
        raise


def _dispose_splat_hr_accumulator(accumulator, paths):
    """Close and remove temporary HR accumulator files."""
    for mapping in accumulator or ():
        if mapping is None:
            continue
        try:
            mapping.flush()
        except Exception:
            pass
        try:
            mapping._mmap.close()
        except Exception:
            pass
    for path in paths or ():
        try:
            os.remove(path)
        except OSError:
            pass


def _dispose_splat_result_memmap(result):
    """Release the output memmap and its paired denominator after saving."""
    if not isinstance(result, np.memmap):
        return
    numerator_path = str(getattr(result, "filename", "") or "")
    try:
        result.flush()
    except Exception:
        pass
    try:
        result._mmap.close()
    except Exception:
        pass
    if ".numerator.f32" not in numerator_path:
        return
    denominator_path = numerator_path.replace(
        ".numerator.f32", ".denominator.f32"
    )
    for path in (numerator_path, denominator_path):
        if path:
            try:
                os.remove(path)
            except OSError:
                pass


def _clip_splat_memmap_inplace(result, block_size):
    """Clamp a floating HR memmap without materializing the full image."""
    height, width = result.shape[:2]
    block_size = max(64, int(block_size))
    for y0 in range(0, height, block_size):
        y1 = min(height, y0 + block_size)
        for x0 in range(0, width, block_size):
            x1 = min(width, x0 + block_size)
            np.clip(
                result[y0:y1, x0:x1],
                0.0,
                1.0,
                out=result[y0:y1, x0:x1],
            )
    result.flush()


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

    def compute_spatial_weight_maps(
        self, lr_frames, noise_std=0.015, sensitivity=120.0
    ):
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
            local_mse = cv2.GaussianBlur(
                (diff * diff).astype(np.float32), (5, 5), sigmaX=1.0
            )

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
        alignment_images = [
            np.ascontiguousarray(frame, dtype=np.float32) for frame in frames
        ]
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
    def _build_lucas_kanade_params(config):
        """Translate the application LK settings to taichi_vision's API."""
        win_size = max(5, int(config.get("win_size", 13)))
        if win_size % 2 == 0:
            win_size += 1
        return {
            "winSize": (win_size, win_size),
            "maxLevel": max(0, int(config.get("max_level", 2))),
            "criteria": (
                3,
                max(1, int(config.get("iterations", 8))),
                float(config.get("epsilon", 0.03)),
            ),
            "grid_step": max(4, int(config.get("grid_step", 48))),
            "border_margin": max(0, int(config.get("border_margin", 8))),
            "motion_mode": str(config.get("motion_mode", "fast")),
            "dense_mode": "blocky_clamped",
            "max_flow_px": float(config.get("max_flow_px", 64.0)),
        }

    @staticmethod
    def _splat_flow_from_lk_flow(lk_flow):
        """Convert reference-to-current warp flow to source-to-output flow.

        ``calcOpticalFlowPyrLK(reference, current)`` returns the displacement
        used by ``remap_with_flow(current, lk_flow)``.  The splat graph instead
        evaluates ``source + flow`` in output coordinates, so it needs the
        inverse displacement for the original current frame.
        """
        flow = np.ascontiguousarray(lk_flow, dtype=np.float32)
        if flow.ndim != 3 or flow.shape[-1] != 2:
            raise ValueError(f"Lucas-Kanade flow must be HxWx2, got {flow.shape}")
        if not np.isfinite(flow).all():
            raise ValueError("Lucas-Kanade flow contains NaN or infinity")
        return np.ascontiguousarray(-flow, dtype=np.float32)

    @staticmethod
    def _warp_rgb_for_confidence(image, lk_flow):
        """Warp RGB only for WeightNet analysis using the already estimated LK flow."""
        image = np.asarray(image, dtype=np.float32)
        if image.ndim == 2:
            image = image[..., None]
        if image.ndim == 3 and image.shape[2] == 1:
            image = np.repeat(image, 3, axis=2)
        image = np.ascontiguousarray(image, dtype=np.float32)
        flow = np.ascontiguousarray(lk_flow, dtype=np.float32)
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(f"RGB frame must have shape (H,W,3), got {image.shape}")
        if flow.shape != image.shape[:2] + (2,):
            raise ValueError(
                f"LK flow shape {flow.shape} does not match RGB frame {image.shape}"
            )
        h, w = image.shape[:2]
        # Avoid ``mgrid`` here: at 12MP it creates two extra full-resolution
        # float32 planes before map_x/map_y are materialized. Broadcasted
        # coordinate vectors produce the same maps without that peak.
        x_coords = np.arange(w, dtype=np.float32)[None, :]
        y_coords = np.arange(h, dtype=np.float32)[:, None]
        map_x = np.empty((h, w), dtype=np.float32)
        map_y = np.empty((h, w), dtype=np.float32)
        np.add(x_coords, flow[..., 0], out=map_x)
        np.add(y_coords, flow[..., 1], out=map_y)
        aligned = np.empty_like(image, dtype=np.float32)
        for channel in range(3):
            aligned[..., channel] = cv2.remap(
                image[..., channel],
                map_x,
                map_y,
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )
        return aligned

    @staticmethod
    def _estimate_exposure_gain(reference, aligned_support):
        """Estimate support-to-reference gain after geometric alignment."""
        reference = np.asarray(reference, dtype=np.float32)
        support = np.asarray(aligned_support, dtype=np.float32)
        valid = (
            np.isfinite(reference)
            & np.isfinite(support)
            & (reference > np.float32(0.03))
            & (support > np.float32(0.03))
            & (reference < np.float32(0.98))
            & (support < np.float32(0.98))
        )
        if int(np.count_nonzero(valid)) < 32:
            return np.float32(1.0)
        ratios = reference[valid] / np.maximum(support[valid], np.float32(1.0e-4))
        ratios = ratios[np.isfinite(ratios)]
        if ratios.size < 32:
            return np.float32(1.0)
        gain = float(np.median(ratios))
        return np.float32(np.clip(gain, 0.5, 2.0))

    @classmethod
    def _estimate_lucas_kanade_pair(
        cls,
        reference,
        target,
        index,
        *,
        config,
        matching_scale=1.0,
        update_progress=None,
        stop_requested=None,
    ):
        """Return ``(lk_flow, warped_target)`` using taichi_vision directly."""
        if stop_requested and stop_requested():
            return None
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK

        reference = np.ascontiguousarray(reference, dtype=np.float32)
        target = np.ascontiguousarray(target, dtype=np.float32)
        if reference.ndim != 2 or target.shape != reference.shape:
            raise ValueError(
                f"Lucas-Kanade expects matching 2-D frames, got "
                f"{reference.shape} and {target.shape}"
            )
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

        if update_progress:
            update_progress(9, f"Lucas-Kanade alignment {index + 1}...")
        lk_flow = calcOpticalFlowPyrLK(
            np.ascontiguousarray(matching_reference, dtype=np.float32),
            np.ascontiguousarray(matching_target, dtype=np.float32),
            **cls._build_lucas_kanade_params(config),
        )
        if isinstance(lk_flow, tuple):
            lk_flow = lk_flow[0]
        lk_flow = np.asarray(lk_flow, dtype=np.float32)
        if lk_flow.ndim != 3 or lk_flow.shape[-1] != 2:
            raise RuntimeError(
                f"taichi_vision Lucas-Kanade returned unexpected flow shape "
                f"{lk_flow.shape}"
            )
        if matching_scale < 0.999:
            lk_flow = np.stack(
                [
                    cv2.resize(
                        lk_flow[..., axis], (w, h), interpolation=cv2.INTER_LINEAR
                    )
                    / np.float32(matching_scale)
                    for axis in range(2)
                ],
                axis=-1,
            )
        lk_flow = np.ascontiguousarray(lk_flow, dtype=np.float32)
        if lk_flow.shape != (h, w, 2) or not np.isfinite(lk_flow).all():
            raise RuntimeError(
                f"taichi_vision Lucas-Kanade returned invalid flow {lk_flow.shape}"
            )

        try:
            warped_target = taichi_aot.remap_with_flow(
                target,
                lk_flow,
                h,
                w,
                return_gpu=False,
            )
        except Exception as exc:
            active_arch = str(getattr(taichi_aot.engine, "arch", "")).lower()
            if active_arch != "cpu":
                raise
            # The CPU remap artifact may be quarantined after a runtime rebuild.
            # Keep recovery explicit and CPU-only; GPU paths must report native
            # remap failures instead of silently crossing backends.
            from .spatial_weight_pipeline import _numpy_remap_with_flow

            print(
                "[splattingSR] CPU taichi_aot remap unavailable; using explicit "
                f"NumPy warp recovery: {exc}"
            )
            warped_target = _numpy_remap_with_flow(target, lk_flow)
        warped_target = np.ascontiguousarray(warped_target, dtype=np.float32)
        if warped_target.shape != (h, w) or not np.isfinite(warped_target).all():
            raise RuntimeError(
                f"taichi_aot.remap_with_flow returned invalid warped frame "
                f"{warped_target.shape}"
            )
        return lk_flow, warped_target

    @staticmethod
    def _estimate_internal_block_matching_pair(
        matcher, config, reference, target, index, matching_scale=1.0
    ):
        """Return one dense LR flow plane from native block matching."""
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
        # SplatSR alignment is deliberately strict: the motion proxy must come
        # from the native BlockMatchingGPU graph.  Phase correlation and the
        # retired Lucas-Kanade path are not valid substitutes here.
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
                        cv2.resize(
                            pair[..., axis], (w, h), interpolation=cv2.INTER_LINEAR
                        )
                        / np.float32(matching_scale)
                        for axis in range(2)
                    ],
                    axis=-1,
                )
            return np.ascontiguousarray(pair)
        except Exception as exc:
            raise RuntimeError(
                f"native block-matching alignment failed for frame {index}: {exc}"
            ) from exc

    def run_splatting_sr(
        self,
        images,
        scale=2,
        update_progress=None,
        stop_requested=None,
        alignment_method="block_matching",
        num_iterations=None,
        weightnet_provider=None,
        refinement_iterations=0,
        refinement_step=0.1,
        refinement_regularization=0.1,
        exposure_normalization=True,
        release_input=False,
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
        refinement_iterations = max(int(refinement_iterations), 0)
        exposure_normalization = bool(exposure_normalization)
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
        rgb_frames = []
        reference_rgb = None
        weightnet_work_warp = os.environ.get(
            "SPLATSR_WEIGHTNET_WORK_WARP", "0"
        ).strip().lower() in {"1", "true", "yes", "on"}

        def normalized_rgb(image):
            image = np.asarray(image)
            normalized = np.asarray(
                normalize_image(image, image.dtype), dtype=np.float32
            )
            if normalized.ndim == 2:
                normalized = normalized[..., None]
            if normalized.ndim != 3 or normalized.shape[2] not in (1, 3):
                raise ValueError(
                    "weightnet_provider requires grayscale or RGB input frames"
                )
            if normalized.shape[2] == 1:
                normalized = np.repeat(normalized, 3, axis=2)
            return np.ascontiguousarray(normalized, dtype=np.float32)

        def infer_weightnet_confidence(support_rgb, lk_flow):
            """Use the resident-style work-resolution confidence bridge."""
            fast_path = getattr(
                weightnet_provider, "infer_aligned_support_with_flow", None
            )
            if weightnet_work_warp and callable(fast_path):
                return fast_path(reference_rgb, support_rgb, lk_flow)
            # Preserve compatibility with custom providers that only expose
            # the original full-resolution call contract.
            return weightnet_provider(
                reference_rgb,
                self._warp_rgb_for_confidence(support_rgb, lk_flow),
            )

        for image in images:
            if stop_requested and stop_requested():
                return None
            if color:
                yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
                ys.append(normalize_image(yuv[..., 0], dtype_ref)[..., 0])
                rgb_frames.append(normalize_image(image, dtype_ref))
            else:
                ys.append(normalize_image(image, dtype_ref)[..., 0])
        frames = np.ascontiguousarray(np.stack(ys, axis=0), dtype=np.float32)
        n, h, w = frames.shape
        splat_frames = (
            np.ascontiguousarray(np.stack(rgb_frames, axis=0), dtype=np.float32)
            if color
            else frames[..., None]
        )
        # Keep the resident-pipeline dual-buffer contract: v1 is an analysis
        # view for alignment/WeightNet only; the linear splat stack remains
        # untouched and is the sole reconstruction source.
        from taichi_vision import taichi_aot

        def analysis_rgb(frame):
            frame = np.asarray(frame, dtype=np.float32)
            if frame.ndim == 2:
                frame = frame[..., None]
            if frame.shape[2] == 1:
                frame = np.repeat(frame, 3, axis=2)
            return np.ascontiguousarray(frame, dtype=np.float32)

        analysis_reference_rgb = analysis_rgb(splat_frames[0])
        analysis_params = taichi_aot.analyze_auto_enhance_params(
            analysis_reference_rgb, mode="analysis"
        )
        analysis_reference_rgb = taichi_aot.AutoEnhance(
            analysis_reference_rgb,
            params=analysis_params,
        )
        analysis_reference_gray = cv2.cvtColor(
            analysis_reference_rgb, cv2.COLOR_RGB2GRAY
        )
        print(
            f"[splattingSR] AutoEnhance analysis v1 gain="
            f"{analysis_params.get('gain', 1.0):.2f}x; "
            "linear buffer retained for splatting"
        )

        def make_analysis_frame(index):
            analysis = taichi_aot.AutoEnhance(
                analysis_rgb(splat_frames[index]),
                params=analysis_params,
            )
            return (
                np.ascontiguousarray(analysis, dtype=np.float32),
                cv2.cvtColor(analysis, cv2.COLOR_RGB2GRAY),
            )

        if weightnet_provider is not None:
            # For RGB, use a view into the already-required splat stack.  The
            # previous path normalized the reference a second time, creating a
            # full-resolution copy before the larger stacks were complete.
            reference_rgb = (
                analysis_reference_rgb
            )
            print(
                "[splattingSR] WeightNet warp mode="
                f"{'work_resolution' if weightnet_work_warp else 'full_resolution_compat'}"
            )
        if color:
            del image, yuv
        else:
            del image, norm_img
        if release_input and hasattr(images, "clear"):
            # ``main`` owns this list and no longer needs the source arrays
            # after entering the reconstruction stage. Keep the public method
            # non-mutating by default for external callers.
            images.clear()
        # ``images``, ``ys`` and ``rgb_frames`` are only staging containers.
        # Release them before flow/WeightNet/native splatting starts so the
        # resident pipeline does not retain multiple full-resolution copies.
        del images, ys, rgb_frames, ref
        gc.collect()
        if update_progress:
            update_progress(8, "Estimating internal block-matching flow...")
        requested_alignment = str(alignment_method or "block_matching").strip().lower()
        if requested_alignment not in {
            "lucas_kanade",  # Legacy saved-session alias; no longer selected.
            "block_matching",
            "blockmatching",
            "bm",
            "internal",
        }:
            raise ValueError(
                "splattingSR requires internal taichi_vision block-matching "
                "alignment; external alignment is not supported"
            )
        if requested_alignment == "lucas_kanade":
            print(
                "[splattingSR] legacy alignment=lucas_kanade ignored; "
                "using block_matching"
            )
        # For large frames, stream one flow/confidence plane at a time.  The
        # previous full-frame path materialized flow[N,H,W,2] and confidence
        # [N,H,W] simultaneously, which can exceed system RAM while leaving
        # VRAM mostly idle during host-side preparation.
        import config as app_config

        block_settings = app_config.get_compute_block_settings()
        block_size = int(block_settings.get("block_size", 1024))
        threshold_mp = float(block_settings.get("threshold_mp", 12.0))
        block_mode = str(block_settings.get("mode", "auto")).strip().lower()
        frame_mp = (h * w) / 1.0e6
        block_enabled = bool(block_settings.get("enabled", True)) and (
            block_mode == "block" or (block_mode == "auto" and frame_mp >= threshold_mp)
        )
        if block_enabled:
            from .spatial_weight_pipeline import generate_spatial_weight_map_blockwise

            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
                BlockMatchingGPU,
            )

            matcher = BlockMatchingGPU()
            bm_config = matcher.load_config()
            cache = {}
            exposure_gains = np.ones(n, dtype=np.float32)
            exposure_ready = np.zeros(n, dtype=bool)
            exposure_ready[0] = True
            reference = frames[0]
            # Keep large-frame alignment bounded to a proxy, while preserving
            # the full-resolution flow contract after upsampling.
            flow_proxy_max = max(
                128,
                int(os.environ.get("SPLATSR_FLOW_PROXY_MAX", "256")),
            )
            flow_proxy_scale = min(1.0, flow_proxy_max / float(max(h, w)))
            # The proxy is not the final alignment product. Use a bounded
            # native block-matching configuration so a driver cannot spend an unbounded
            # amount of time building a deep pyramid for every burst frame.
            bm_config = dict(bm_config)
            bm_config.update(
                grid_step=max(64, int(bm_config.get("grid_step", 48))),
                max_level=0,
                iterations=1,
                motion_mode="fast",
                adaptive=False,
                strict=True,
            )
            print(
                f"[splattingSR] block_matching flow proxy="
                f"{flow_proxy_scale:.3f} ({max(32, int(h * flow_proxy_scale))}x"
                f"{max(32, int(w * flow_proxy_scale))})"
            )
            print(
                f"[splattingSR] block_matching mode={bm_config.get('mode', 'fast')} "
                f"grid_step={bm_config.get('grid_step')}"
            )

            def flow_provider(index):
                if index not in cache:
                    if index == 0:
                        cache[index] = (
                            np.zeros((h, w, 2), dtype=np.float32),
                            reference,
                            None,
                            analysis_reference_rgb,
                        )
                    else:
                        if update_progress:
                            update_progress(
                                9 + int((index / max(n - 1, 1)) * 12),
                                f"Block matching alignment {index + 1}/{n}...",
                            )
                        if exposure_normalization and not exposure_ready[index]:
                            # Photometric differences can be interpreted as
                            # motion by LK.  Normalize a robust global gain
                            # before alignment, then correct any residual gain
                            # again after the geometric warp below.
                            pre_gain = self._estimate_exposure_gain(
                                reference, frames[index]
                            )
                            exposure_gains[index] = pre_gain
                            if abs(float(pre_gain) - 1.0) > 1.0e-5:
                                frames[index] *= pre_gain
                                splat_frames[index] *= pre_gain
                        analysis_support, analysis_support_gray = make_analysis_frame(
                            index
                        )
                        alignment_flow = self._estimate_internal_block_matching_pair(
                            matcher,
                            bm_config,
                            analysis_reference_gray,
                            analysis_support_gray,
                            index,
                            matching_scale=flow_proxy_scale,
                        )
                        warped_analysis = self._warp_rgb_for_confidence(
                            analysis_support, alignment_flow
                        )
                        exposure_ready[index] = True
                        cache[index] = (
                            self._splat_flow_from_lk_flow(alignment_flow),
                            warped_analysis,
                            alignment_flow,
                            analysis_support,
                        )
                    if update_progress:
                        update_progress(
                            10 + int((index / max(n - 1, 1)) * 12),
                            f"Block matching flow/warp {index + 1}/{n}",
                        )
                return cache[index][0]

            def confidence_provider(index):
                if index not in cache:
                    flow_provider(index)
                _, warped, alignment_flow, analysis_support = cache[index]
                if index == 0:
                    cache.pop(index, None)
                    return np.ones((h, w), dtype=np.float32)
                # Match SpatialFusion: confidence is computed from the already
                # warped frame, so the weight stage must not warp a second time.
                if update_progress:
                    update_progress(
                        20 + int((index / max(n - 1, 1)) * 4),
                        f"SpatialFusion weight map {index + 1}/{n}",
                    )
                if weightnet_provider is not None:
                    result = infer_weightnet_confidence(
                        analysis_support, alignment_flow
                    )
                else:
                    warped_analysis_gray = cv2.cvtColor(
                        np.ascontiguousarray(warped, dtype=np.float32),
                        cv2.COLOR_RGB2GRAY,
                    )
                    result = generate_spatial_weight_map_blockwise(
                        analysis_reference_gray,
                        warped_analysis_gray,
                        None,
                        block_size=block_size,
                        halo=max(32, int(bm_config.get("win_size", 13))),
                        tile_size=min(256, block_size),
                        overlap=0.2,
                        motion_sensitivity=1.0,
                        noise_offset_factor=0.0,
                        noise_sigma=0.015,
                        early_exit_threshold=0.05,
                    )
                    del warped_analysis_gray
                # The stream asks for each flow before its confidence.  Once
                # this frame is accumulated, release its dense flow plane.
                cache.pop(index, None)
                return result

            def release_resident_flow_planes(indices):
                for index in indices:
                    cached = cache.get(index)
                    if cached is None:
                        continue
                    _, warped, alignment_flow, analysis_support = cached
                    cache[index] = (None, warped, alignment_flow, analysis_support)

            flow_provider.release_resident_flow_planes = (
                release_resident_flow_planes
            )

            print(
                f"[splattingSR] compute_block=enabled size={block_size}px "
                f"threshold={threshold_mp:g}MP; streaming resident flow/weights"
            )
            hr_accumulator = None
            hr_accumulator_paths = None
            try:
                from .spatial_splat_runtime import SpatialSplatAOT

                native_splat = SpatialSplatAOT()
                resident_batch_override = os.environ.get(
                    "SPLATSR_RESIDENT_BATCH_SIZE"
                )
                resident_batch_size = max(
                    1,
                    int(
                        resident_batch_override
                        if resident_batch_override is not None
                        else ("1" if frame_mp >= 8.0 else "2")
                    ),
                )
                print(
                    f"[splattingSR] resident splat batch="
                    f"{resident_batch_size} block={block_size}px"
                    f"{' (auto-large-frame)' if resident_batch_override is None and frame_mp >= 8.0 else ''}"
                )
                # Native output tiles are already bounded, but the old
                # stitching boundary still allocated a full HR numerator and
                # denominator in process RAM. Use disk-backed accumulators for
                # large RGB jobs so final normalization and save stay tiled.
                hr_bytes = (
                    h
                    * int(scale)
                    * w
                    * int(scale)
                    * 3
                    * np.dtype(np.float32).itemsize
                )
                use_disk_accumulator = (
                    bool(release_input)
                    and color
                    and np.issubdtype(dtype_ref, np.floating)
                    and refinement_iterations <= 0
                    and native_splat.backend != "cpu"
                    and hr_bytes >= 64 * 1024 * 1024
                )
                if use_disk_accumulator:
                    hr_accumulator, hr_accumulator_paths = _create_splat_hr_accumulator(
                        (h * int(scale), w * int(scale), 3)
                    )
                    print(
                        "[splattingSR] HR accumulator=memmap "
                        f"block={block_size}px estimate="
                        f"{(hr_bytes * 1.3333333) / (1024 * 1024):.1f}MB "
                        "(numerator+coverage)"
                    )
                result, _coverage = native_splat.run_streaming(
                    splat_frames,
                    flow_provider,
                    confidence_provider,
                    scale=scale,
                    block_size=block_size,
                    batch_size=resident_batch_size,
                    resident=True,
                    progress_callback=(
                        lambda done, total: (
                            update_progress(
                                24 + int((done / max(total, 1)) * 72),
                                f"Native splatting blocks {done}/{total}",
                            )
                            if update_progress
                            else None
                        )
                    ),
                    accumulator=hr_accumulator,
                )
                del _coverage
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
                    _dispose_splat_hr_accumulator(
                        hr_accumulator, hr_accumulator_paths
                    )
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
                _dispose_splat_hr_accumulator(
                    hr_accumulator, hr_accumulator_paths
                )
                hr_accumulator = None
                hr_accumulator_paths = None
                result, _ = robust_subpixel_splat_stream(
                    splat_frames,
                    flow_provider,
                    confidence_provider,
                    scale=scale,
                    block_size=block_size,
                    progress_callback=(
                        lambda done, total: (
                            update_progress(
                                24 + int((done / max(total, 1)) * 72),
                                f"Splatting blocks {done}/{total}",
                            )
                            if update_progress
                            else None
                        )
                    ),
                )
            if refinement_iterations > 0:
                from .spatial_splat_sr import iterative_optical_refine_stream

                print(
                    f"[splattingSR] optical refinement iterations="
                    f"{refinement_iterations} step={float(refinement_step):g} "
                    f"regularization={float(refinement_regularization):g}"
                )
                initial_luma = (
                    cv2.cvtColor(
                        np.ascontiguousarray(result, dtype=np.float32),
                        cv2.COLOR_RGB2GRAY,
                    )
                    if color
                    else np.asarray(result[..., 0], dtype=np.float32)
                )
                refined = iterative_optical_refine_stream(
                    frames,
                    flow_provider,
                    confidence_provider,
                    scale=scale,
                    block_size=block_size,
                    initial=initial_luma,
                    iterations=refinement_iterations,
                    step=refinement_step,
                    regularization=refinement_regularization,
                )
                if color:
                    current_luma = cv2.cvtColor(
                        np.ascontiguousarray(result, dtype=np.float32),
                        cv2.COLOR_RGB2GRAY,
                    )
                    result = np.ascontiguousarray(
                        result + (refined - current_luma)[..., None],
                        dtype=np.float32,
                    )
                else:
                    result = np.ascontiguousarray(refined[..., None], dtype=np.float32)
            cache.clear()
            # All flow/confidence work is complete. Drop closure references to
            # the full source/RGB stacks before final conversion or save.
            del flow_provider, confidence_provider, release_resident_flow_planes
            del (
                cache,
                reference,
                reference_rgb,
                splat_frames,
                frames,
                analysis_reference_rgb,
                analysis_reference_gray,
                analysis_params,
                analysis_rgb,
                make_analysis_frame,
            )
            gc.collect()
            if (
                isinstance(result, np.memmap)
                and color
                and np.issubdtype(dtype_ref, np.floating)
            ):
                _clip_splat_memmap_inplace(result, block_size)
                if hr_accumulator is not None:
                    # ``run_streaming`` returns the coverage map for API
                    # compatibility. Close that paired mapping here so the
                    # Windows file handle is gone before the writer removes
                    # the temporary files after save.
                    coverage_memmap = hr_accumulator[1]
                    try:
                        coverage_memmap.flush()
                    except Exception:
                        pass
                    try:
                        coverage_memmap._mmap.close()
                    except Exception:
                        pass
                return result
            if np.issubdtype(dtype_ref, np.integer):
                max_val = np.iinfo(dtype_ref).max
                if color:
                    return np.clip(result * max_val, 0, max_val).astype(dtype_ref)
                y_hr = np.clip(result[..., 0] * max_val, 0, max_val).astype(dtype_ref)
            else:
                if color:
                    return np.clip(result, 0.0, 1.0).astype(dtype_ref)
                y_hr = np.clip(result[..., 0], 0.0, 1.0).astype(dtype_ref)
            return y_hr

        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
            BlockMatchingGPU,
        )
        from .spatial_weight_pipeline import SpatialWeightMapGenerator

        matcher = BlockMatchingGPU()
        bm_config = matcher.load_config()
        bm_config = dict(bm_config)
        bm_config["strict"] = True
        splat_flow = np.zeros((n, h, w, 2), dtype=np.float32)
        confidence = np.ones((n, h, w), dtype=np.float32)

        # Follow SpatialFusion's ordering exactly: block matching -> warp -> spatial
        # confidence.  The raw frames and inverse flow are retained for the
        # final sub-pixel splat so the source is not interpolated twice.
        with SpatialWeightMapGenerator(
            analysis_reference_gray, tile_size=256, overlap=0.2, noise_sigma=0.015
        ) as weight_generator:
            for index in range(1, n):
                if stop_requested and stop_requested():
                    return None
                if update_progress:
                    update_progress(
                        9 + int((index / max(n - 1, 1)) * 10),
                        f"Block matching alignment {index + 1}/{n}...",
                    )
                pre_gain = np.float32(1.0)
                if exposure_normalization:
                    pre_gain = self._estimate_exposure_gain(
                        frames[0], frames[index]
                    )
                    if abs(float(pre_gain) - 1.0) > 1.0e-5:
                        frames[index] *= pre_gain
                        splat_frames[index] *= pre_gain
                analysis_support, analysis_support_gray = make_analysis_frame(index)
                alignment_flow = self._estimate_internal_block_matching_pair(
                    matcher,
                    bm_config,
                    analysis_reference_gray,
                    analysis_support_gray,
                    index,
                    matching_scale=1.0,
                )
                if alignment_flow is None:
                    return None
                splat_flow[index] = self._splat_flow_from_lk_flow(alignment_flow)
                warped_analysis = self._warp_rgb_for_confidence(
                    analysis_support, alignment_flow
                )
                if exposure_normalization:
                    gain = self._estimate_exposure_gain(
                        analysis_reference_rgb, warped_analysis
                    )
                    if abs(float(gain) - 1.0) > 1.0e-5:
                        frames[index] *= gain
                        splat_frames[index] *= gain
                        warped_analysis = np.ascontiguousarray(
                            warped_analysis * gain, dtype=np.float32
                        )
                if weightnet_provider is not None:
                    confidence[index] = infer_weightnet_confidence(
                        analysis_support, alignment_flow
                    )
                else:
                    confidence[index] = weight_generator.generate(warped_analysis)
                del analysis_support, analysis_support_gray, warped_analysis
                if update_progress:
                    update_progress(
                        20 + int((index / max(n - 1, 1)) * 4),
                        f"SpatialFusion weight map {index + 1}/{n}",
                    )
        try:
            from .spatial_splat_runtime import SpatialSplatAOT

            if update_progress:
                update_progress(20, "Running native GPU subpixel splatting...")
            result, _ = SpatialSplatAOT().run(
                splat_frames, confidence, splat_flow, scale=scale
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
                splat_frames,
                flow=splat_flow,
                confidence=confidence,
                scale=scale,
            )
        if refinement_iterations > 0:
            from .spatial_splat_sr import iterative_optical_refine

            print(
                f"[splattingSR] optical refinement iterations="
                f"{refinement_iterations} step={float(refinement_step):g} "
                f"regularization={float(refinement_regularization):g}"
            )
            initial_luma = (
                cv2.cvtColor(
                    np.ascontiguousarray(result, dtype=np.float32),
                    cv2.COLOR_RGB2GRAY,
                )
                if color
                else np.asarray(result[..., 0], dtype=np.float32)
            )
            refined = iterative_optical_refine(
                frames,
                splat_flow,
                confidence,
                scale=scale,
                initial=initial_luma,
                iterations=refinement_iterations,
                step=refinement_step,
                regularization=refinement_regularization,
            )
            if color:
                current_luma = cv2.cvtColor(
                    np.ascontiguousarray(result, dtype=np.float32),
                    cv2.COLOR_RGB2GRAY,
                )
                result = np.ascontiguousarray(
                    result + (refined - current_luma)[..., None],
                    dtype=np.float32,
                )
            else:
                result = np.ascontiguousarray(refined[..., None], dtype=np.float32)
        if np.issubdtype(dtype_ref, np.integer):
            max_val = np.iinfo(dtype_ref).max
            if color:
                return np.clip(result * max_val, 0, max_val).astype(dtype_ref)
            y_hr = np.clip(result[..., 0] * max_val, 0, max_val).astype(dtype_ref)
        else:
            if color:
                return np.clip(result, 0.0, 1.0).astype(dtype_ref)
            y_hr = np.clip(result[..., 0], 0.0, 1.0).astype(dtype_ref)
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
                dx, dy, _ = phase_correlation(
                    lr_frames[0], lr_frames[k], use_hanning=True
                )
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

                    tile_lr = lr_frames[
                        :, y_start : y_start + tile_h, x_start : x_start + tile_w
                    ]
                    tile_weight = weight_maps[
                        :, y_start : y_start + tile_h, x_start : x_start + tile_w
                    ]

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
                        btv_window=2,
                    )
                    solver.set_lr_data(tile_lr, tile_weight, shifts)

                    # Set initial estimate via bicubic upsampling
                    init_hr = cv2.resize(
                        tile_lr[0],
                        (tile_hr_w, tile_hr_h),
                        interpolation=cv2.INTER_CUBIC,
                    )
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
                    hr_accumulator[
                        y_hr_start : y_hr_start + tile_hr_h,
                        x_hr_start : x_hr_start + tile_hr_w,
                    ] += (
                        tile_hr_res * win
                    )
                    weight_accumulator[
                        y_hr_start : y_hr_start + tile_hr_h,
                        x_hr_start : x_hr_start + tile_hr_w,
                    ] += win

                    # Release solver resources
                    del solver
                    del tile_hr_res
                    del win
                    gc.collect()

                    processed_tiles += 1
                    if update_progress:
                        prog_val = 10 + int((processed_tiles / total_tiles) * 85)
                        update_progress(
                            prog_val,
                            f"Processing super-resolution tile {processed_tiles}/{total_tiles}...",
                        )

            # 5. Final Stitching normalization and scaling
            if update_progress:
                update_progress(98, "Stitching and normalizing tiles...")

            valid_mask = weight_accumulator > 1e-6
            final_hr = np.zeros_like(hr_accumulator)
            final_hr[valid_mask] = (
                hr_accumulator[valid_mask] / weight_accumulator[valid_mask]
            )

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


def _env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return bool(default)
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _is_raw_path(path):
    return os.path.splitext(str(path))[1].lower() in {
        ".dng",
        ".cr2",
        ".cr3",
        ".nef",
        ".arw",
        ".orf",
        ".rw2",
        ".pef",
        ".raf",
        ".srw",
    }


def _mfd_linear_mode(path):
    """Mirror MFDenoiser's RAW -> Linear DNG output switch."""
    if os.path.splitext(str(path))[1].lower() not in {
        ".dng",
        ".cr2",
        ".cr3",
        ".nef",
        ".arw",
    }:
        return False
    try:
        import config as app_config

        with open(app_config.GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as handle:
            settings = json.load(handle)
        return bool(settings.get("enable_linear_mode", False))
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def _load_mfdenoiser_frames(image_paths, stop_requested=None, update_progress=None):
    """Load SplatSR inputs through the same RGB-linear MFDenoiser loader."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        load_rgb_linear_image,
    )
    from taichi_vision import taichi_aot

    frames = []
    target_shape = None
    total = len(image_paths)
    for index, path in enumerate(image_paths):
        if stop_requested and stop_requested():
            return None
        frame = load_rgb_linear_image(path)
        frame = np.ascontiguousarray(frame, dtype=np.float32)
        if target_shape is None:
            target_shape = frame.shape[:2]
        elif frame.shape[:2] != target_shape:
            frame = taichi_aot.resize(
                frame,
                (target_shape[1], target_shape[0]),
                interpolation=taichi_aot.INTER_LINEAR,
            )
            frame = np.ascontiguousarray(frame, dtype=np.float32)
        frames.append(frame)
        if update_progress:
            update_progress(
                5 + int(((index + 1) / max(total, 1)) * 3),
                f"Loading image {index + 1}/{total}...",
            )
    return frames


def _save_mfd_compatible_result(result, output_path, reference_image_path=None):
    """Use the same output dtype/tone/DNG contract as MFDenoiser."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
        save_linear_dng,
        save_linear_dng_streaming,
    )

    if isinstance(result, np.memmap):
        try:
            tile_size = int(os.environ.get("SPLATSR_OUTPUT_TILE_SIZE", "1024"))
            if reference_image_path and _mfd_linear_mode(reference_image_path):
                dng_path = os.path.splitext(output_path)[0] + ".dng"
                return save_linear_dng_streaming(
                    result,
                    dng_path,
                    reference_image_path=reference_image_path,
                    tile_size=tile_size,
                )
            return save_image_streaming(
                result,
                output_path,
                reference_image_path=reference_image_path,
                apply_tonemapping=bool(
                    reference_image_path and _is_raw_path(reference_image_path)
                ),
                tile_size=tile_size,
            )
        finally:
            _dispose_splat_result_memmap(result)

    result = np.asarray(result)
    if np.issubdtype(result.dtype, np.floating):
        result_u16 = np.clip(result * 65535.0 + 0.5, 0.0, 65535.0).astype(
            np.uint16
        )
    elif result.dtype != np.uint16:
        result_u16 = np.clip(result, 0, 65535).astype(np.uint16)
    else:
        result_u16 = result

    if reference_image_path and _mfd_linear_mode(reference_image_path):
        dng_path = os.path.splitext(output_path)[0] + ".dng"
        return save_linear_dng(
            result_u16,
            dng_path,
            reference_image_path=reference_image_path,
        )

    return save_image(
        result_u16,
        output_path,
        reference_image_path=reference_image_path,
        apply_tonemapping=bool(
            reference_image_path and _is_raw_path(reference_image_path)
        ),
    )


def _build_weightnet_provider():
    """Build the WeightNet confidence provider used by the SR route."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
        DEFAULT_WEIGHTNET_ONNX,
    )
    from .weightnet_confidence import WeightNetConfidenceProvider

    model_path = os.environ.get("SPLATSR_WEIGHTNET_MODEL", str(DEFAULT_WEIGHTNET_ONNX))
    runtime = os.environ.get("SPLATSR_WEIGHTNET_RUNTIME", "auto")
    tile_size = int(os.environ.get("SPLATSR_WEIGHTNET_TILE", "256"))
    work_scale = float(os.environ.get("SPLATSR_WEIGHTNET_WORK_SCALE", "0.50"))
    provider = WeightNetConfidenceProvider(
        model_path=model_path,
        runtime=runtime,
        tile_size=tile_size,
        work_scale=work_scale,
        overlap=float(os.environ.get("SPLATSR_WEIGHTNET_OVERLAP", "0.30")),
        ghost_penalty=float(
            os.environ.get("SPLATSR_WEIGHTNET_GHOST_PENALTY", "1.0")
        ),
        ghost_cutoff=float(
            os.environ.get("SPLATSR_WEIGHTNET_GHOST_CUTOFF", "0.05")
        ),
        chroma_sensitivity=float(
            os.environ.get("SPLATSR_WEIGHTNET_CHROMA_SENSITIVITY", "1.0")
        ),
    )
    print(
        f"[splattingSR] WeightNet confidence enabled runtime={runtime} "
        f"providers={provider.providers} model={model_path} "
        f"reference_cache_tiles={provider.reference_cache_tiles}"
    )
    return provider


def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
    use_weightnet=None,
    weightnet_provider=None,
    refinement_iterations=None,
    refinement_step=0.1,
    refinement_regularization=0.1,
    exposure_normalization=None,
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
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else "single_process"
            )
            # SplattingSR owns alignment internally.  Never consume an
            # externally aligned HDF5 product here; doing so would align the
            # burst before the internal Lucas-Kanade stage.
            data_source = image_paths
        else:
            if batch_id is None:
                raise ValueError("Batch ID must be provided for batch processing.")
            hdf5_path = os.path.join(align_dir, f"aligned_image_batch_{batch_id}.h5")
            image_paths = image_processor.get_all_image_paths_for_batch_process(
                batch_id
            )
            ref_name = (
                os.path.splitext(os.path.basename(image_paths[0]))[0]
                if image_paths
                else f"batch_{batch_id}"
            )
            # Keep the raw/session image order and let the internal
            # Lucas-Kanade stage estimates motion.  The SpatialFusion
            # HDF5 alignment cache is deliberately not an input to SplatSR.
            data_source = image_paths

        cleanup_old_hdf5_files(hdf5_path)

        output_name_safe = (
            "".join(c for c in ref_name if c.isalnum() or c in ("_", "-")).rstrip()
            or "sr_result"
        )
        output_path = os.path.join(
            output_folder_stack, f"{output_name_safe}_splattingSR.tif"
        )

        # Load images
        if update_progress:
            update_progress(5, "Loading image files...")

        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as h5f:
                keys = list(h5f.keys())
                images = [np.array(h5f[key]) for key in keys]
        else:
            images = _load_mfdenoiser_frames(
                image_paths,
                stop_requested=stop_requested,
                update_progress=update_progress,
            )

        if not images:
            if update_progress:
                update_progress(100, "Failed to load input images.")
            return None

        if weightnet_provider is None and (
            _env_flag("SPLATSR_USE_WEIGHTNET", default=True)
            if use_weightnet is None
            else bool(use_weightnet)
        ):
            weightnet_provider = _build_weightnet_provider()
        if refinement_iterations is None:
            refinement_iterations = int(
                os.environ.get("SPLATSR_REFINEMENT_ITERATIONS", "0")
            )
        refinement_step = float(
            os.environ.get("SPLATSR_REFINEMENT_STEP", str(refinement_step))
        )
        refinement_regularization = float(
            os.environ.get(
                "SPLATSR_REFINEMENT_REGULARIZATION",
                str(refinement_regularization),
            )
        )
        if exposure_normalization is None:
            exposure_normalization = _env_flag(
                "SPLATSR_EXPOSURE_NORMALIZATION", default=True
            )

        # Run process
        final_result = image_processor.run_splatting_sr(
            images,
            scale=2,
            num_iterations=120,
            update_progress=update_progress,
            stop_requested=stop_requested,
            weightnet_provider=weightnet_provider,
            refinement_iterations=refinement_iterations,
            refinement_step=refinement_step,
            refinement_regularization=refinement_regularization,
            exposure_normalization=exposure_normalization,
            release_input=True,
        )

        if final_result is not None:
            if isinstance(final_result, np.memmap) and update_progress:
                update_progress(97, "Writing HR output tiles...")
            saved_path = _save_mfd_compatible_result(
                final_result,
                output_path,
                reference_image_path=image_paths[0] if image_paths else None,
            )
            final_message = (
                f"Process finished successfully: {os.path.basename(saved_path)}"
                if saved_path
                else "Failed to save result image."
            )
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
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

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
    worker.progress_updated.connect(
        lambda progress, message: (
            progress_bar.setValue(progress),
            label.setText(message),
        )
    )

    def finish_handler():
        nonlocal process_finished
        process_finished = True
        dialog.close()
        worker.quit()
        worker.wait()

    worker.finished.connect(finish_handler)
    worker.error_occurred.connect(
        lambda err: (
            QMessageBox.critical(dialog, "Error", f"Error occurred: {err}"),
            dialog.close(),
            worker.quit(),
            worker.wait(),
        )
    )

    dialog.closeEvent = lambda ev: (
        ev.accept()
        if process_finished
        else (
            ev.accept()
            if not worker.isRunning()
            else (
                (worker.stop(), worker.quit(), worker.wait(), ev.accept())
                if QMessageBox.question(
                    dialog,
                    "Cancel Process",
                    "Do you want to cancel?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
                else ev.ignore()
            )
        )
    )
    worker.start()
    dialog.exec()


if __name__ == "__main__":
    db_path = os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not db_path:
        raise SystemExit(
            "Set PIXEL_REFINE_SESSION_DB before running splattingSR directly."
        )
    main(db_path)
