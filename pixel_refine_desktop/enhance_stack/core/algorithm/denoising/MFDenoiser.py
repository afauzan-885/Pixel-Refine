"""
MFDenoiser.py — Modular Multi-Frame Denoiser Orchestrator

Replaces the monolithic Similarity.py as the primary denoising orchestrator.
Manages the pipeline: Load → Align → Merge → PostProcess → Save.
Each stage is pluggable via ctx.params — swap algorithms without touching this file.

Similarity.py is kept as backup.
"""

import os
import gc
import json
import time
import traceback
import sqlite3
import h5py
import numpy as np
import cv2
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from PySide6.QtWidgets import QMessageBox, QVBoxLayout, QDialog, QProgressBar, QLabel
from PySide6.QtCore import Qt

# --- Shared Utilities ---
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from resources.styles.stylesheet import PROGRESS_BAR
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    normalize_image,
    save_image,
    calculate_auto_scale,
    calculate_scale_from_gt_proxy,
    save_linear_dng,
    get_all_image_paths_for_single_process,
    load_images_from_paths,
    resize_all_with_padding,
    cleanup_old_hdf5_files,
    is_hdf5_cache_valid,
    estimate_noise_in_python,
)

# language_config and load_similarity_config imported lazily inside methods to avoid circular imports


def _lang():
    """Lazy import of language_config to break circular import chain."""
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    return language_config


# ---------------------------------------------------------------------------
# Pipeline Context — carries state between stages
# ---------------------------------------------------------------------------
@dataclass
class PipelineContext:
    db_path: str
    image_paths: list = field(default_factory=list)
    data_source: object = None  # HDF5 path (str) or list of file paths
    reference_image: np.ndarray = None  # Original dtype (uint8/uint16)
    reference_float: np.ndarray = None  # Normalized float32 [0, 1]
    ref_h: int = 0
    ref_w: int = 0
    ref_dtype: object = None
    output_name_base: str = ""
    total_images: int = 0
    is_linear_mode: bool = False
    proxy_scale: float = 1.0
    hdf5_path: str = ""
    params: dict = field(default_factory=dict)
    session_id: str = ""
    update_progress: object = None
    stop_requested: object = None
    single_process: bool = True
    batch_id: object = None


# ---------------------------------------------------------------------------
# Tile Processor Interface
# ---------------------------------------------------------------------------
@dataclass
class TileContext:
    """Context passed to processor.process_tile() for each tile position."""

    tile_y: int
    tile_x: int
    tile_h: int
    tile_w: int
    frame_tiles: np.ndarray  # (num_frames, tile_h, tile_w, C) float32
    source_h: int
    source_w: int
    tile_idx: int
    total_tiles: int
    update_progress: object = None
    stop_requested: object = None


class TileProcessor(ABC):
    """Interface for pluggable per-tile processors.

    Implementors focus ONLY on: receive tile data -> run algorithm -> return result.
    MFDenoiser handles all tiling infrastructure.
    """

    @abstractmethod
    def setup(self, ctx: PipelineContext, shared_data: dict) -> None:
        """One-time initialization before the tile loop.

        Compute global data needed by all tiles (weight maps, shifts, etc.)
        and store in shared_data dict.
        """
        pass

    @abstractmethod
    def get_output_size(self, tile_h: int, tile_w: int) -> tuple:
        """Return output tile dimensions for a given input tile size.

        Returns:
            (out_h, out_w) — dimensions of the tile returned by process_tile.
            Denoising: (tile_h, tile_w)       — 1:1
            Super-Res: (tile_h*scale, tile_w*scale) — e.g. 2:1
        """
        pass

    @abstractmethod
    def process_tile(self, tile_ctx: TileContext, shared_data: dict) -> tuple:
        """Process a single tile and return the weighted result.

        The returned tuple must be (weighted_sum, weight_map):
          - weighted_sum: np.ndarray of shape (out_h, out_w) or (out_h, out_w, C), float32
          - weight_map: np.ndarray of shape (out_h, out_w), float32 (per-frame weights)

        MFDenoiser multiplies both by the Hanning window and accumulates.
        """
        pass

    def preprocess_batch(self, batch_float: list, shared_data: dict) -> None:
        """Called after each batch is loaded, before the tile loop.

        Override to compute batch-specific data (e.g. sub-pixel shifts, weight maps).
        Default: no-op.

        Args:
            batch_float: List of normalized float32 images for this batch.
            shared_data: Mutable dict shared across process_tile calls.
        """
        pass

    def teardown(self) -> None:
        """Cleanup after the tile loop completes. Default: no-op."""
        pass


# ---------------------------------------------------------------------------
# MFDenoiser Algorithm — the orchestrator
# ---------------------------------------------------------------------------
class MFDenoiserAlgorithm:
    """
    Modular Multi-Frame Denoiser Orchestrator.
    Coordinates data loading, alignment, merging, post-processing, and saving.
    Each pipeline stage is pluggable via ctx.params.
    """

    def __init__(self, db_path):
        self.db_path = db_path

    def close(self):
        """Release resources and free memory."""
        gc.collect()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_image_paths(self, batch_id=None):
        """Fetch image paths from database."""
        if batch_id is None:
            return get_all_image_paths_for_single_process(self.db_path)
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

    def _load_params(self):
        """Load algorithm parameters from config files.

        Single truth source — reads from the same config used by Similarity.py's main().
        This ensures MFDenoiser and Similarity share identical parameter behavior.
        """
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
            load_similarity_config,
        )
        from config import GENERAL_SETTINGS_FILE

        sim_config = load_similarity_config()

        # === Spatial Fusion Parameters (shared with Similarity.py) ===
        tile_val = sim_config.get("similarity_spatial_tile_size", 16)
        params = {
            # Tiling
            "similarity_spatial_tile_size": tile_val,
            "tile_size": (tile_val, tile_val),
            "similarity_spatial_overlap_percent": sim_config.get("similarity_spatial_overlap_percent", 0.30),
            "overlap": sim_config.get("similarity_spatial_overlap_percent", 0.30),

            # Ghost Rejection
            "similarity_spatial_motion_sensitivity": sim_config.get("similarity_spatial_motion_sensitivity", 150.0),
            "motion_sensitivity": sim_config.get("similarity_spatial_motion_sensitivity", 150.0),
            "similarity_spatial_noise_mad_offset_factor": sim_config.get("similarity_spatial_noise_mad_offset_factor", 0.15),
            "noise_offset_factor": sim_config.get("similarity_spatial_noise_mad_offset_factor", 0.15),

            # Workers
            "similarity_spatial_num_workers": sim_config.get("similarity_spatial_num_workers", 1),

            # Smart Fusion (AI)
            "similarity_smart_noise_alpha": sim_config.get("similarity_smart_noise_alpha", 1.0),
            "similarity_smart_noise_aware_enable": sim_config.get("similarity_smart_noise_aware_enable", True),
            "similarity_smart_noise_strength": sim_config.get("similarity_smart_noise_strength", 100.0),

            # Backend selection
            "merging_mode": sim_config.get("merging_mode", "spatial_fusion"),
            "alignment_backend": sim_config.get("alignment_backend", "taichi_gpu"),
            "optical_flow_type": sim_config.get("optical_flow_type", "alignment_tile"),

            # Processing
            "use_multi_core": sim_config.get("use_multi_core", True),

            # Spatial Fusion specific
            "early_exit_threshold": sim_config.get("early_exit_threshold", 0.05),
            "equalize_brightness": sim_config.get("equalize_brightness", False),
        }

        # Load linear mode from general settings
        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general = json.load(f)
                params["enable_linear_mode"] = general.get("enable_linear_mode", False)
        except (IOError, json.JSONDecodeError):
            params["enable_linear_mode"] = False

        return params

    # ------------------------------------------------------------------
    # Tiling Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _compute_tile_starts(full_size, tile_size, overlap=0.3):
        """Compute tile start positions for a dimension.

        Ensures tiles always reach the edge with no gaps, deduplicated.
        """
        if tile_size >= full_size:
            return np.array([0], dtype=np.int32)
        step = max(int(tile_size * (1.0 - overlap)), 1)
        starts = []
        y = 0
        while y + tile_size <= full_size:
            starts.append(y)
            if y + tile_size == full_size:
                break
            y = min(y + step, full_size - tile_size)
        return np.array(starts, dtype=np.int32)

    @staticmethod
    def _make_hanning_window(h, w):
        """Generate 2D Hanning window for tile stitching."""
        win_y = np.hanning(h).astype(np.float32)
        win_x = np.hanning(w).astype(np.float32)
        return np.outer(win_y, win_x)

    @staticmethod
    def _compute_work_resolution(ref_h, ref_w, target_mp=12.5e6):
        """Compute working resolution, downscaling if exceeding target megapixels."""
        if (ref_h * ref_w) > target_mp:
            scale = np.sqrt(target_mp / (ref_h * ref_w))
            wh = int(ref_h * scale)
            ww = int(ref_w * scale)
        else:
            wh, ww = ref_h, ref_w
        return (wh // 2) * 2, (ww // 2) * 2

    # ------------------------------------------------------------------
    # Universal Tiled Merge
    # ------------------------------------------------------------------
    def _run_tiled_merge(self, processor, ctx, use_original_resolution=False):
        """Universal tiled merge: processor.setup() + tile loop + Hanning stitching.

        MFDenoiser owns the tile grid, extraction, Hanning window, accumulation,
        and final stitching. The processor only implements process_tile().

        Args:
            processor: TileProcessor instance.
            ctx: PipelineContext.
            use_original_resolution: If True, skip work-resolution downscaling and
                merge at the original image dimensions. Used by Average to preserve
                full-quality output.

        Returns: (sum_img, sum_weight, frame_count)
        """
        if use_original_resolution:
            work_h, work_w = ctx.ref_h, ctx.ref_w
        else:
            work_h, work_w = self._compute_work_resolution(ctx.ref_h, ctx.ref_w)

        print(
            f"[TRACE] _run_tiled_merge: use_original_resolution={use_original_resolution}, ref=({ctx.ref_h}x{ctx.ref_w}), work=({work_h}x{work_w})"
        )

        tile_size = ctx.params.get("similarity_spatial_tile_size", 512)
        tile_h = min(tile_size, work_h)
        tile_w = min(tile_size, work_w)
        overlap = ctx.params.get("similarity_spatial_overlap_percent", 0.3)

        y_starts = self._compute_tile_starts(work_h, tile_h, overlap)
        x_starts = self._compute_tile_starts(work_w, tile_w, overlap)
        total_tiles = len(y_starts) * len(x_starts)

        # Query processor for output dimensions
        out_h, out_w = processor.get_output_size(tile_h, tile_w)
        out_scale_y = out_h / tile_h
        out_scale_x = out_w / tile_w

        out_full_h = int(work_h * out_scale_y)
        out_full_w = int(work_w * out_scale_x)
        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1

        accumulator = np.zeros((out_full_h, out_full_w, channels), dtype=np.float32)
        weight_accumulator = np.zeros((out_full_h, out_full_w), dtype=np.float32)
        hanning_win = self._make_hanning_window(out_h, out_w)

        # Processor setup
        shared_data = {}
        processor.setup(ctx, shared_data)

        # Progress
        merge_start = ctx.params.get("merge_progress_start", 0)
        merge_end = ctx.params.get("merge_progress_end", 95)

        frame_count = 0
        try:
            # Determine batch size
            max_batch = 8
            total = ctx.total_images

            for batch_start in range(0, total, max_batch):
                if ctx.stop_requested and ctx.stop_requested():
                    break

                batch_end = min(batch_start + max_batch, total)
                batch_images = self._load_images(
                    ctx.data_source,
                    (batch_start, batch_end),
                    ctx.stop_requested,
                    linear_mode=ctx.is_linear_mode,
                )
                if not batch_images:
                    continue

                # Normalize batch to float32
                batch_float = [
                    normalize_image(img, ctx.ref_dtype) for img in batch_images
                ]

                # Let processor compute batch-specific data (shifts, weight maps, etc.)
                processor.preprocess_batch(batch_float, shared_data)

                processed_tiles = 0
                for y_start in y_starts:
                    for x_start in x_starts:
                        if ctx.stop_requested and ctx.stop_requested():
                            return None, None, 0

                        # Extract tiles from all frames in batch
                        frame_tiles = np.stack(
                            [
                                f[
                                    y_start : y_start + tile_h,
                                    x_start : x_start + tile_w,
                                ]
                                for f in batch_float
                            ]
                        )  # (batch_N, tile_h, tile_w, C)

                        tile_ctx = TileContext(
                            tile_y=y_start,
                            tile_x=x_start,
                            tile_h=tile_h,
                            tile_w=tile_w,
                            frame_tiles=frame_tiles,
                            source_h=work_h,
                            source_w=work_w,
                            tile_idx=processed_tiles,
                            total_tiles=total_tiles,
                            update_progress=ctx.update_progress,
                            stop_requested=ctx.stop_requested,
                        )

                        tile_result = processor.process_tile(tile_ctx, shared_data)
                        if tile_result is None:
                            processed_tiles += 1
                            continue

                        # Unpack (weighted_sum, weight_map)
                        if isinstance(tile_result, tuple) and len(tile_result) == 2:
                            tile_sum, tile_weight = tile_result
                        else:
                            tile_sum = tile_result
                            tile_weight = np.ones((out_h, out_w), dtype=np.float32)

                        # Ensure numpy float32
                        if hasattr(tile_sum, "to_numpy"):
                            tile_sum = tile_sum.to_numpy()
                        tile_sum = np.asarray(tile_sum, dtype=np.float32)
                        if hasattr(tile_weight, "to_numpy"):
                            tile_weight = tile_weight.to_numpy()
                        tile_weight = np.asarray(tile_weight, dtype=np.float32)

                        # Map to output accumulator
                        out_y = int(y_start * out_scale_y)
                        out_x = int(x_start * out_scale_x)
                        roi_y = slice(out_y, out_y + out_h)
                        roi_x = slice(out_x, out_x + out_w)

                        # Hanning-weighted accumulation
                        if tile_sum.ndim == 3:
                            win_3d = hanning_win[..., np.newaxis]
                            accumulator[roi_y, roi_x] += tile_sum * win_3d
                        else:
                            accumulator[roi_y, roi_x] += (
                                tile_sum[..., np.newaxis] * hanning_win[..., np.newaxis]
                            )

                        # Accumulate weight: per_frame_weight * hanning_window
                        weight_accumulator[roi_y, roi_x] += tile_weight * hanning_win

                        processed_tiles += 1
                        if ctx.update_progress and total_tiles > 0:
                            frac = (batch_start + processed_tiles) / total
                            prog = int(merge_start + frac * (merge_end - merge_start))
                            ctx.update_progress(
                                prog, f"Merging tile {processed_tiles}/{total_tiles}..."
                            )

                frame_count += len(batch_images)
                del batch_images, batch_float
                gc.collect()

        finally:
            processor.teardown()

        return accumulator, weight_accumulator, frame_count

    # ------------------------------------------------------------------
    # Stage 1: Load Data
    # ------------------------------------------------------------------
    def stage_load_data(self, ctx):
        """Load images, detect linear mode, calculate proxy scale."""
        align_dir = os.path.join("database", "align")

        if ctx.single_process:
            ctx.hdf5_path = os.path.join(align_dir, "aligned_images.h5")
            ctx.image_paths = self._get_image_paths(batch_id=None)
        else:
            ctx.hdf5_path = os.path.join(
                align_dir, f"aligned_image_batch_{ctx.batch_id}.h5"
            )
            ctx.image_paths = self._get_image_paths(batch_id=ctx.batch_id)

        ref_name = (
            os.path.splitext(os.path.basename(ctx.image_paths[0]))[0]
            if ctx.image_paths
            else "mf_denoiser"
        )
        ctx.output_name_base = ref_name

        # Cleanup old HDF5 files
        cleanup_old_hdf5_files(ctx.hdf5_path)

        # Validate HDF5 cache against current reference image
        ref_image_path_current = ctx.image_paths[0] if ctx.image_paths else ""
        if os.path.exists(ctx.hdf5_path) and ref_image_path_current:
            if not is_hdf5_cache_valid(ctx.hdf5_path, ref_image_path_current):
                try:
                    os.remove(ctx.hdf5_path)
                    print(
                        f"[CacheValidation] HDF5 cache deleted (ref changed): {ctx.hdf5_path}"
                    )
                except Exception as e:
                    print(f"[CacheValidation] Failed to delete HDF5 cache: {e}")

        ctx.data_source = (
            ctx.hdf5_path if os.path.exists(ctx.hdf5_path) else ctx.image_paths
        )

        # Count total images
        if isinstance(ctx.data_source, str) and ctx.data_source.endswith(".h5"):
            print(_lang().PROCESSING_IMAGE_FROM_HDF5.format(ctx.data_source))
            try:
                with h5py.File(ctx.data_source, "r") as f:
                    ctx.total_images = len(f.keys())
            except Exception as e:
                raise IOError(f"Failed to read HDF5: {e}")
        elif isinstance(ctx.data_source, list):
            ctx.total_images = len(ctx.data_source)

        if not ctx.total_images:
            return ctx

        # Load reference image (first image)
        is_linear = ctx.params.get("enable_linear_mode", False)
        if ctx.image_paths:
            _, ext = os.path.splitext(ctx.image_paths[0])
            if is_linear and ext.lower() in (".dng", ".cr2", ".cr3", ".nef", ".arw"):
                ctx.is_linear_mode = True

        ref_res = self._load_images(
            ctx.data_source,
            (0, 1),
            ctx.stop_requested,
            linear_mode=ctx.is_linear_mode,
            capture_ref_proxy=ctx.is_linear_mode,
        )
        if ctx.is_linear_mode and isinstance(ref_res, tuple):
            reference_image, ref_proxy_gt = ref_res
        elif isinstance(ref_res, list) and len(ref_res) > 0:
            reference_image, ref_proxy_gt = ref_res[0], None
        else:
            reference_image, ref_proxy_gt = None, None

        if reference_image is None:
            ctx.total_images = 0
            return ctx

        ctx.reference_image = reference_image
        ctx.ref_dtype = reference_image.dtype
        ctx.ref_h, ctx.ref_w = reference_image.shape[:2]

        # Auto-scale for Linear Mode
        if ctx.is_linear_mode:
            if ref_proxy_gt is not None:
                ctx.proxy_scale = calculate_scale_from_gt_proxy(
                    reference_image, ref_proxy_gt, reference_image.dtype
                )
            else:
                ctx.proxy_scale = calculate_auto_scale(
                    normalize_image(reference_image, reference_image.dtype),
                    target_mean=0.25,
                )

        # Normalize reference to float32
        ctx.reference_float = normalize_image(reference_image, reference_image.dtype)

        # Generate unique session ID
        ctx.session_id = f"{ctx.output_name_base}_{time.strftime('%Y%m%d_%H%M%S')}"

        return ctx

    # ------------------------------------------------------------------
    # Stage 2: Align (pluggable)
    # ------------------------------------------------------------------
    def stage_align(self, ctx):
        """Run alignment if images are not already aligned (no HDF5 cache)."""
        is_hdf5 = isinstance(ctx.data_source, str) and ctx.data_source.endswith(".h5")
        if is_hdf5:
            ctx.params["enable_alignment"] = False
            return ctx

        backend = ctx.params.get("alignment_backend", "taichi_gpu")
        if backend == "none":
            return ctx
        if callable(backend):
            return backend(ctx)

        # Default: Taichi GPU alignment
        return self._align_taichi_gpu(ctx)

    def _align_taichi_gpu(self, ctx):
        """Run Taichi GPU alignment and write results to HDF5."""
        if ctx.update_progress:
            ctx.update_progress(0, "Running alignment (Taichi GPU) to create HDF5...")

        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)

        # Load all images for alignment (Progress 0–25%)
        images_for_align = self._load_images(
            ctx.image_paths,
            (0, len(ctx.image_paths)),
            ctx.stop_requested,
            linear_mode=ctx.is_linear_mode,
            alignment_mode=False,
            update_progress=ctx.update_progress,
            progress_start=0,
            progress_end=25,
        )

        with h5py.File(ctx.hdf5_path, "w") as h5f:
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                save_to_hdf5,
                extract_exif,
            )

            # Store reference image path for cache validation
            h5f.attrs["ref_image_path"] = ctx.image_paths[0] if ctx.image_paths else ""
            save_to_hdf5(
                h5f, "image_0", ctx.reference_image, extract_exif(ctx.image_paths[0])
            )

            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_pipeline import (
                process_in_gpu,
            )

            process_in_gpu(
                images=images_for_align,
                reference_image_float=ctx.reference_float,
                ref_image_h=ctx.ref_h,
                ref_image_w=ctx.ref_w,
                ref_dtype=ctx.ref_dtype,
                work_res_h=ctx.ref_h,
                work_res_w=ctx.ref_w,
                tile_h=ctx.params.get("tile_size", (16, 16))[0],
                tile_w=ctx.params.get("tile_size", (16, 16))[1],
                update_progress=ctx.update_progress,
                stop_requested=ctx.stop_requested,
                p_align_start=25,
                p_align_end=50,
                is_linear_mode=ctx.is_linear_mode,
                proxy_scale=ctx.proxy_scale,
                h5_file_handle=h5f,
                image_paths=ctx.image_paths,
                reference_image=ctx.reference_image,
                alignment_only=True,
                optical_flow_type=ctx.params.get("optical_flow_type", "alignment_tile"),
            )

        del images_for_align
        gc.collect()

        # Re-check data source to load the newly created H5
        ctx.data_source = (
            ctx.hdf5_path if os.path.exists(ctx.hdf5_path) else ctx.image_paths
        )
        ctx.params["enable_alignment"] = False
        ctx.params["merge_progress_start"] = 50
        ctx.params["merge_progress_end"] = 95
        return ctx

    # ------------------------------------------------------------------
    # Stage 3: Merge (pluggable via processor)
    # ------------------------------------------------------------------
    def stage_merge(self, ctx):
        """Run the merge/denoise backend using the universal tiler.

        Returns (sum_img, sum_weight, frame_count).
        """
        backend = ctx.params.get("merging_mode", "spatial")

        if backend == "spatial_fusion":
            # GPU AOT spatial fusion — uses compute_spatial Taichi AOT kernels
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion_processor import (
                SpatialFusionProcessor,
            )

            processor = SpatialFusionProcessor(
                motion_sensitivity=ctx.params.get("motion_sensitivity", 150.0),
                noise_offset_factor=ctx.params.get("noise_offset_factor", 0.15),
                early_exit_threshold=ctx.params.get("early_exit_threshold", 0.05),
            )
            frame_count, sum_img, sum_weight, ref_noise_sigma = processor.process(
                images=None,  # Will load from data_source
                reference_image_float=ctx.reference_float,
                ref_h=ctx.ref_h,
                ref_w=ctx.ref_w,
                ref_dtype=ctx.ref_dtype,
                work_res_h=ctx.ref_h,
                work_res_w=ctx.ref_w,
                update_progress=ctx.update_progress,
                stop_requested=ctx.stop_requested,
                is_linear_mode=ctx.is_linear_mode,
                proxy_scale=getattr(ctx, "proxy_scale", 1.0),
                data_source=ctx.data_source,
                image_paths=ctx.image_paths,
            )
            return sum_img, sum_weight, frame_count

        elif backend == "average":
            print(
                "[TRACE] MFDenoiser.stage_merge: backend='average', using AverageDenoiseProcessor"
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.average_denoise_processor import (
                AverageDenoiseProcessor,
            )

            processor = AverageDenoiseProcessor()
            return self._run_tiled_merge(processor, ctx, use_original_resolution=True)
        elif backend == "smart":
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.smart_fusion.smart_denoise_processor import (
                SmartDenoiseProcessor,
            )

            processor = SmartDenoiseProcessor()
        elif backend == "super_resolution":
            from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.sr_processor import (
                SuperResolutionProcessor,
            )

            processor = SuperResolutionProcessor(
                scale=ctx.params.get("sr_scale", 2),
                num_iterations=ctx.params.get("sr_iterations", 120),
            )
        else:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_denoise_processor import (
                SpatialDenoiseProcessor,
            )

            processor = SpatialDenoiseProcessor()

        return self._run_tiled_merge(processor, ctx)

    # ------------------------------------------------------------------
    # Stage 4: Post-Process (pluggable)
    # ------------------------------------------------------------------
    def stage_postprocess(self, ctx, sum_img, sum_weight, frame_count):
        """Normalize accumulated result and apply optional denoise."""
        if sum_img is None or frame_count <= 0:
            channels = (
                ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
            )
            return np.zeros((ctx.ref_h, ctx.ref_w, channels), dtype=ctx.ref_dtype)

        # Normalize: divide by weight
        valid_mask = sum_weight > 1e-6
        normalized = np.zeros_like(sum_img)
        np.divide(
            sum_img,
            sum_weight[:, :, np.newaxis],
            out=normalized,
            where=valid_mask[:, :, np.newaxis],
        )

        # Fallback: fill invalid pixels with reference image (resize to work resolution if needed)
        if not np.all(valid_mask):
            work_h, work_w = sum_weight.shape[:2]
            ref_h, ref_w = ctx.reference_float.shape[:2]
            if (work_h, work_w) != (ref_h, ref_w):
                ref_resized = cv2.resize(
                    ctx.reference_float, (work_w, work_h), interpolation=cv2.INTER_AREA
                )
            else:
                ref_resized = ctx.reference_float
            normalized[~valid_mask] = ref_resized[~valid_mask]

        # Pluggable post-processor
        postprocessor = ctx.params.get("postprocessor", "adaptive_box")
        if callable(postprocessor):
            normalized = postprocessor(ctx, normalized)
        elif postprocessor == "adaptive_box":
            normalized = self._postprocess_adaptive_box(ctx, normalized)
        # else: "none" — skip post-processing

        # Scale back to original bit-depth
        max_val = np.iinfo(ctx.ref_dtype).max
        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
        if channels == 1:
            final_out = np.mean(normalized * max_val, axis=2)
        else:
            final_out = normalized * max_val

        return np.clip(final_out, 0, max_val).astype(ctx.ref_dtype)

    def _postprocess_adaptive_box(self, ctx, normalized):
        """Adaptive box-filter high-frequency denoise based on noise estimation."""
        ref_gray = cv2.cvtColor(ctx.reference_float, cv2.COLOR_BGR2GRAY)
        est_noise = estimate_noise_in_python(ref_gray)

        if est_noise >= 0.20:
            print(
                f"[Denoise] Noise detected (sigma={est_noise:.4f}). Applying Adaptive HF Denoise..."
            )
            lf = cv2.boxFilter(
                normalized, ddepth=-1, ksize=(3, 3), borderType=cv2.BORDER_REFLECT
            )
            hf = normalized - lf
            alpha = np.clip(0.15 + (est_noise - 0.20) * 0.5, 0.15, 0.45)
            hf_clean = hf * (1.0 - alpha)
            normalized = lf + hf_clean
            print(f"  [Denoise] Damped HF noise by {alpha*100:.1f}%")

        return normalized

    # ------------------------------------------------------------------
    # Stage 5: Save
    # ------------------------------------------------------------------
    def stage_save(self, ctx, result_image):
        """Save the final result to disk. Returns output path."""
        output_folder = "database/stack"
        os.makedirs(output_folder, exist_ok=True)
        safe_name = (
            "".join(
                c for c in ctx.output_name_base if c.isalnum() or c in ("_", "-")
            ).rstrip()
            or "stack"
        )
        output_suffix = ctx.params.get("output_suffix", "mf_denoiser")
        output_path = os.path.join(output_folder, f"{safe_name}_{output_suffix}.tif")

        if ctx.is_linear_mode:
            output_path = save_linear_dng(
                result_image,
                os.path.splitext(output_path)[0] + ".dng",
                reference_image_path=ctx.image_paths[0] if ctx.image_paths else None,
            )
        else:
            save_image(
                result_image,
                output_path,
                reference_image_path=ctx.image_paths[0] if ctx.image_paths else None,
            )
        return output_path

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------
    def run_pipeline(
        self,
        single_process=True,
        batch_id=None,
        update_progress=None,
        stop_requested=None,
        merging_mode=None,
        output_suffix=None,
    ):
        """Execute the full pipeline: Load → Align → Merge → PostProcess → Save."""
        ctx = PipelineContext(
            db_path=self.db_path,
            single_process=single_process,
            batch_id=batch_id,
            update_progress=update_progress,
            stop_requested=stop_requested,
        )
        ctx.params = self._load_params()

        # Inject caller-provided overrides into params
        if merging_mode is not None:
            ctx.params["merging_mode"] = merging_mode
        if output_suffix is not None:
            ctx.params["output_suffix"] = output_suffix

        # Stage 1: Load
        ctx = self.stage_load_data(ctx)
        if not ctx.total_images:
            if update_progress:
                update_progress(100, _lang().NO_IMAGE_PATH_PROCESSED_IMAGE)
            return None

        # Stage 2: Align
        ctx = self.stage_align(ctx)
        if ctx.stop_requested and ctx.stop_requested():
            return None

        # Stage 3: Merge
        if ctx.update_progress:
            merge_start = ctx.params.get("merge_progress_start", 0)
            ctx.update_progress(merge_start, "Merging frames...")

        sum_img, sum_weight, frame_count = self.stage_merge(ctx)
        if ctx.stop_requested and ctx.stop_requested():
            return None

        # Stage 4: Post-Process
        if ctx.update_progress:
            ctx.update_progress(95, "Finalizing fusion...")
        result = self.stage_postprocess(ctx, sum_img, sum_weight, frame_count)

        # Stage 5: Save
        output_path = self.stage_save(ctx, result)
        return output_path

    # ------------------------------------------------------------------
    # Image Loading Utility
    # ------------------------------------------------------------------
    @staticmethod
    def _load_images(
        data_source,
        batch_indices,
        stop_requested=None,
        linear_mode=True,
        capture_ref_proxy=False,
        alignment_mode=False,
        update_progress=None,
        progress_start=0,
        progress_end=100,
    ):
        """Load a batch of images from HDF5 or filesystem."""
        batch_start, batch_end = batch_indices
        batch_images = []
        ref_proxy = None

        if isinstance(data_source, str) and data_source.endswith(".h5"):
            with h5py.File(data_source, "r") as h5f:
                keys = list(h5f.keys())[batch_start:batch_end]
                batch_images = [
                    np.array(h5f[key])
                    for key in keys
                    if not (stop_requested and stop_requested())
                ]
        elif isinstance(data_source, list):
            batch_paths = data_source[batch_start:batch_end]
            load_res = load_images_from_paths(
                batch_paths,
                stop_requested,
                linear_mode=linear_mode,
                capture_ref_proxy=capture_ref_proxy,
                alignment_mode=alignment_mode,
                update_progress=update_progress,
                progress_start=progress_start,
                progress_end=progress_end,
            )
            if capture_ref_proxy and isinstance(load_res, tuple):
                batch_images, ref_proxy = load_res
            else:
                batch_images = load_res

            resize_res = resize_all_with_padding(
                batch_images,
                method="preserve",
                stop_requested=stop_requested,
                force_even=True,
            )
            if resize_res and resize_res[0]:
                batch_images = resize_res[0]

        if capture_ref_proxy:
            return batch_images, ref_proxy
        return batch_images


# ---------------------------------------------------------------------------
# Module-level entry points
# ---------------------------------------------------------------------------
def main(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    progress_bar=None,
    merging_mode=None,
    output_suffix=None,
):
    """Main execution block."""
    start_time = time.perf_counter()
    processor = None
    try:
        if update_progress:
            update_progress(0, _lang().RUN_IMAGE_PROCESS_STARTED)

        processor = MFDenoiserAlgorithm(db_path)
        output_path = processor.run_pipeline(
            single_process=single_process,
            batch_id=batch_id,
            update_progress=update_progress,
            stop_requested=stop_requested,
            merging_mode=merging_mode,
            output_suffix=output_suffix,
        )

        if output_path and update_progress:
            update_progress(100, f"Process Finished: {os.path.basename(output_path)}")

    except Exception as e:
        print(f"Error in MFDenoiser main: {e}")
        traceback.print_exc()
        if update_progress:
            update_progress(0, f"Error: {str(e)}")
    finally:
        elapsed = time.perf_counter() - start_time
        print(f"\n[MFDenoiser] Completed in {elapsed:.2f}s\n")
        if processor:
            processor.close()
        gc.collect()


def running_mf_denoiser(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    merging_mode=None,
    output_suffix=None,
):
    """UI Entry point for MF Denoiser."""

    # === BATCH MODE (no GUI dialog) ===
    if batch_id is not None and progress_callback is not None:
        try:
            main(
                db_path="pixel_refine_database.db",
                update_progress=progress_callback,
                stop_requested=stop_callback,
                single_process=False,
                batch_id=batch_id,
                merging_mode=merging_mode,
                output_suffix=output_suffix,
            )
        except Exception as e:
            raise e
        return

    # === SINGLE MODE (with GUI dialog) ===
    process_finished = False
    dialog = QDialog(parent)
    dialog.setWindowTitle(_lang().WINDOW_TITLE_SIMILARITY)
    dialog.setModal(True)
    dialog.setFixedSize(300, 90)
    dialog.setWindowFlags(
        Qt.WindowType.Window
        | Qt.WindowType.CustomizeWindowHint
        | Qt.WindowType.WindowTitleHint
        | Qt.WindowType.WindowCloseButtonHint
    )

    layout = QVBoxLayout(dialog)
    label = QLabel(_lang().WINDOW_START_PROCESSING)
    layout.addWidget(label)

    progress_bar = QProgressBar()
    progress_bar.setRange(0, 100)
    progress_bar.setValue(0)
    progress_bar.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(progress_bar)

    worker = BaseAlgorithmWorker(
        main,
        "pixel_refine_database.db",
        single_process=single_process,
        batch_id=batch_id,
        merging_mode=merging_mode,
        output_suffix=output_suffix,
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

    def error_handler(error):
        QMessageBox.critical(
            dialog, "Error", _lang().RUN_ERROR_STATUS.format(error=error)
        )
        dialog.close()
        worker.quit()
        worker.wait()

    worker.error_occurred.connect(error_handler)

    def on_dialog_close(event):
        if process_finished:
            event.accept()
        elif worker.isRunning():
            reply = QMessageBox.question(
                dialog,
                "Cancel Process",
                _lang().CANCEL_PROCESSING,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                worker.stop()
                worker.quit()
                worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    dialog.closeEvent = on_dialog_close
    worker.start()
    dialog.exec()


# Backward-compatible alias — existing callers can still import running_similarity
running_similarity = running_mf_denoiser


if __name__ == "__main__":
    main("pixel_refine_database.db")
