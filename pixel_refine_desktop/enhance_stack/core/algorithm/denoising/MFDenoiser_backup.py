"""
MFDenoiser.py — Modular Multi-Frame Denoiser Orchestrator (Cleaned Version)

Manages the pipeline: Load → Align → Merge → PostProcess → Save.
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
    data_source: object = None
    reference_image: np.ndarray = None
    reference_float: np.ndarray = None
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
# Pluggable Alignment Backends
# ---------------------------------------------------------------------------
class FarnebackAlignment:
    """Taichi GPU AOT Farneback Optical Flow alignment backend."""

    def __init__(self, preset="robust", return_gpu=True):
        self.preset = preset
        self.return_gpu = return_gpu

    def _tile_to_gray255_gpu(self, tile_gpu, channels):
        from taichi_library import taichi_aot

        if channels == 3:
            gray_gpu = taichi_aot.cvtColor(tile_gpu, taichi_aot.COLOR_RGB2GRAY)
        else:
            gray_gpu = tile_gpu
        return taichi_aot.scale_f32(gray_gpu, 255.0, return_gpu=True)

    def align_tile(self, ref_tile, comp_tile, return_gpu=None):
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer

        if return_gpu is None:
            return_gpu = self.return_gpu
        h, w = ref_tile.shape[:2]
        channels = ref_tile.shape[2] if ref_tile.ndim == 3 else 1
        ref_is_gpu = isinstance(ref_tile, TaichiGPUBuffer)
        comp_is_gpu = isinstance(comp_tile, TaichiGPUBuffer)
        ref_gpu = (
            ref_tile
            if ref_is_gpu
            else taichi_aot.upload(ref_tile.astype(np.float32, copy=False))
        )
        comp_gpu = (
            comp_tile
            if comp_is_gpu
            else taichi_aot.upload(comp_tile.astype(np.float32, copy=False))
        )
        ref_gray_gpu = self._tile_to_gray255_gpu(ref_gpu, channels)
        comp_gray_gpu = self._tile_to_gray255_gpu(comp_gpu, channels)

        flow_gpu = taichi_aot.farneback_flow(
            ref_gray_gpu,
            comp_gray_gpu,
            pyr_scale=0.5,
            num_levels=3,
            win_size=15,
            num_iters=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
            preset=self.preset,
            return_gpu=True,
        )

        warped = taichi_aot.remap_with_flow(
            comp_gpu,
            flow_gpu,
            h,
            w,
            return_gpu=return_gpu,
        )

        for buf, owned in (
            (ref_gpu, not ref_is_gpu),
            (comp_gpu, not comp_is_gpu),
            (ref_gray_gpu, True),
            (comp_gray_gpu, True),
            (flow_gpu, True),
        ):
            if owned and buf is not None:
                try:
                    buf.destroy()
                except Exception:
                    pass

        if return_gpu:
            return warped
        return warped.astype(np.float32, copy=False)


class NoAlignment:
    """Alignment backend that returns comparison tiles unchanged."""

    def align_tile(self, ref_tile, comp_tile):
        return comp_tile


# ---------------------------------------------------------------------------
# Pluggable Merging Backends
# ---------------------------------------------------------------------------
class SimilarityMerge:
    """Similarity merging backend using Taichi GPU (Vulkan) AOT merging loop."""

    def merge_tiles(self, aligned_tiles, return_gpu=False):
        import cv2
        import numpy as np
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import AOTEngine, TaichiGPUBuffer
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            estimate_noise_in_python,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            generate_spatial_weights_taichi,
            accumulate_spatial_merging_taichi,
        )

        ref_tile = aligned_tiles[0]
        tile_h, tile_w = ref_tile.shape[:2]
        channels = ref_tile.shape[2] if ref_tile.ndim == 3 else 1

        def _to_gray_float(tile):
            if isinstance(tile, TaichiGPUBuffer):
                tile = tile.to_numpy()
            tile = tile.astype(np.float32, copy=False)
            if tile.ndim == 3:
                return (
                    0.299 * tile[..., 0] + 0.587 * tile[..., 1] + 0.114 * tile[..., 2]
                ).astype(np.float32, copy=False)
            return tile.copy()

        if ref_tile.ndim == 3:
            ref_gray = _to_gray_float(ref_tile)
        else:
            ref_gray = _to_gray_float(ref_tile)

        ref_noise_sigma = estimate_noise_in_python(ref_gray)
        if ref_noise_sigma is None or ref_noise_sigma < 1e-5:
            ref_noise_sigma = 0.01

        engine = AOTEngine()

        ref_gray_gpu = taichi_aot.upload(ref_gray)
        ref_tile_gpu = (
            ref_tile
            if isinstance(ref_tile, TaichiGPUBuffer)
            else taichi_aot.upload(ref_tile.copy())
        )
        sum_gpu = taichi_aot.upload(
            ref_tile.to_numpy()
            if isinstance(ref_tile, TaichiGPUBuffer)
            else ref_tile.copy()
        )

        weight_sum_full_gpu = taichi_aot.upload(
            np.ones((tile_h, tile_w), dtype=np.float32)
        )

        # Setup tiling for weight generation (16x16 with 0.3 overlap)
        tile_size_sub = 16
        overlap_sub = 0.3
        step_y = max(int(tile_size_sub * (1.0 - overlap_sub)), 1)
        step_x = max(int(tile_size_sub * (1.0 - overlap_sub)), 1)

        row_starts = np.arange(0, tile_h - tile_size_sub + 1, step_y, dtype=np.int32)
        if tile_h > tile_size_sub and (
            row_starts.size == 0 or row_starts[-1] != tile_h - tile_size_sub
        ):
            row_starts = np.append(row_starts, tile_h - tile_size_sub)
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))

        col_starts = np.arange(0, tile_w - tile_size_sub + 1, step_x, dtype=np.int32)
        if tile_w > tile_size_sub and (
            col_starts.size == 0 or col_starts[-1] != tile_w - tile_size_sub
        ):
            col_starts = np.append(col_starts, tile_w - tile_size_sub)
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        rows_gpu = taichi_aot.upload(row_starts)
        rows_gpu.dtype = np.int32
        cols_gpu = taichi_aot.upload(col_starts)
        cols_gpu.dtype = np.int32

        base_window_gpu = taichi_aot.hanning(
            (tile_size_sub, tile_size_sub), exclude_boundary=False
        )
        weight_work_gpu = engine.allocate(
            (tile_h, tile_w), dtype=np.float32, host_accessible=True
        )

        try:
            for comp_tile in aligned_tiles[1:]:
                # Check if already a TaichiGPUBuffer to avoid CPU-GPU upload overhead
                if isinstance(comp_tile, TaichiGPUBuffer):
                    comp_tile_gpu = comp_tile

                    # Compute grayscale of GPU buffer for weight estimation
                    if channels == 3:
                        comp_gray_gpu = taichi_aot.cvtColor(
                            comp_tile_gpu, taichi_aot.COLOR_RGB2GRAY
                        )
                    else:
                        comp_gray_gpu = comp_tile
                else:
                    comp_gray = _to_gray_float(comp_tile)
                    comp_gray_gpu = taichi_aot.upload(comp_gray)
                    comp_tile_gpu = taichi_aot.upload(comp_tile)

                generate_spatial_weights_taichi(
                    current_image=comp_gray_gpu,
                    reference_image=ref_gray_gpu,
                    weight_map_sum=weight_work_gpu,
                    base_window=base_window_gpu,
                    stability_map=None,
                    row_starts=rows_gpu,
                    col_starts=cols_gpu,
                    tile_h=tile_size_sub,
                    tile_w=tile_size_sub,
                    noise_sigma=ref_noise_sigma,
                    motion_sensitivity=150.0,
                    noise_offset_factor=0.15,
                    equalize_brightness=False,
                    buffer_provider="pool",
                    search_radius=3,
                    early_exit_threshold=0.05,
                )

                if not isinstance(comp_tile, TaichiGPUBuffer) or channels == 3:
                    comp_gray_gpu.destroy()

                accumulate_spatial_merging_taichi(
                    current_image_full=comp_tile_gpu.view_as_vector(False),
                    weight_map_work=weight_work_gpu,
                    final_image_sum=sum_gpu.view_as_vector(False),
                    weight_map_sum_full=weight_sum_full_gpu,
                    row_starts=rows_gpu,
                    col_starts=cols_gpu,
                    tile_h=tile_size_sub,
                    tile_w=tile_size_sub,
                    h_full=tile_h,
                    w_full=tile_w,
                    h_work=tile_h,
                    w_work=tile_w,
                )

                if not isinstance(comp_tile, TaichiGPUBuffer):
                    comp_tile_gpu.destroy()

            merged_tile_gpu = taichi_aot.mean_division(
                sum_gpu,
                weight_sum_full_gpu,
                ref_tile_gpu,
            )
            weight_map_gpu = taichi_aot.upload(
                np.ones((tile_h, tile_w), dtype=np.float32)
            )
            taichi_aot.engine.sync()
            if return_gpu:
                return merged_tile_gpu, weight_map_gpu

            merged_tile = merged_tile_gpu.to_numpy()
            weight_map = weight_map_gpu.to_numpy()
            merged_tile_gpu.destroy()
            weight_map_gpu.destroy()
            return merged_tile, weight_map

        finally:
            for buf in [
                weight_sum_full_gpu,
                base_window_gpu,
                rows_gpu,
                cols_gpu,
                weight_work_gpu,
                ref_gray_gpu,
                sum_gpu,
            ]:
                if buf:
                    try:
                        buf.destroy()
                    except:
                        pass
            if not isinstance(ref_tile, TaichiGPUBuffer):
                try:
                    ref_tile_gpu.destroy()
                except Exception:
                    pass
            # Do not unload modules here to preserve runtime cache
            pass


# ---------------------------------------------------------------------------
# MFDenoiser Algorithm — the orchestrator
# ---------------------------------------------------------------------------
class MFDenoiserAlgorithm:
    """
    Modular Multi-Frame Denoiser Orchestrator.
    """

    def __init__(self, db_path):
        self.db_path = db_path

    def close(self):
        """Release resources and free memory."""
        gc.collect()

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
            "similarity_spatial_overlap_percent": sim_config.get(
                "similarity_spatial_overlap_percent", 0.30
            ),
            "overlap": sim_config.get("similarity_spatial_overlap_percent", 0.30),
            # Ghost Rejection
            "similarity_spatial_motion_sensitivity": sim_config.get(
                "similarity_spatial_motion_sensitivity", 150.0
            ),
            "motion_sensitivity": sim_config.get(
                "similarity_spatial_motion_sensitivity", 150.0
            ),
            "similarity_spatial_noise_mad_offset_factor": sim_config.get(
                "similarity_spatial_noise_mad_offset_factor", 0.15
            ),
            "noise_offset_factor": sim_config.get(
                "similarity_spatial_noise_mad_offset_factor", 0.15
            ),
            # Workers
            "similarity_spatial_num_workers": sim_config.get(
                "similarity_spatial_num_workers", 1
            ),
            # Smart Fusion (AI)
            "similarity_smart_noise_alpha": sim_config.get(
                "similarity_smart_noise_alpha", 1.0
            ),
            "similarity_smart_noise_aware_enable": sim_config.get(
                "similarity_smart_noise_aware_enable", True
            ),
            "similarity_smart_noise_strength": sim_config.get(
                "similarity_smart_noise_strength", 100.0
            ),
            # Backend selection
            "merging_mode": sim_config.get("merging_mode", "spatial_fusion"),
            "alignment_backend": sim_config.get(
                "alignment_backend",
                sim_config.get("tile_based_alignment_backend", "taichi_gpu"),
            ),
            "optical_flow_type": sim_config.get("optical_flow_type", "farneback"),
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
                    print(f"[CacheValidation] HDF5 cache deleted: {ctx.hdf5_path}")
                except Exception as e:
                    print(f"[CacheValidation] Failed to delete HDF5 cache: {e}")

        # Khusus untuk similarity merging mode (atau mode tiling langsung), bypass cache HDF5 agar memuat path gambar asli langsung dari disk
        merging_mode = ctx.params.get("merging_mode", "average").lower()
        if merging_mode in ("similarity", "spatial_fusion", "spatial"):
            ctx.data_source = ctx.image_paths
        else:
            ctx.data_source = (
                ctx.hdf5_path if os.path.exists(ctx.hdf5_path) else ctx.image_paths
            )

        if isinstance(ctx.data_source, str) and ctx.data_source.endswith(".h5"):
            try:
                with h5py.File(ctx.data_source, "r") as f:
                    ctx.total_images = len(f.keys())
            except Exception as e:
                raise IOError(f"Failed to read HDF5: {e}")
        elif isinstance(ctx.data_source, list):
            ctx.total_images = len(ctx.data_source)

        if not ctx.total_images:
            return ctx

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

        ctx.reference_float = normalize_image(reference_image, reference_image.dtype)
        ctx.session_id = f"{ctx.output_name_base}_{time.strftime('%Y%m%d_%H%M%S')}"

        return ctx

    def _process_linear_placeholder(self, ctx):
        """Placeholder function for processing linear RAW mode."""
        print("[LinearMode] Routing to linear mode placeholder (Not supported yet)...")
        if ctx.update_progress:
            ctx.update_progress(
                100, "Linear RAW mode is not supported yet (placeholder)."
            )
        return None

    @staticmethod
    def _compute_tile_starts(full_size, tile_size, overlap=0.3):
        """Compute tile start positions for a dimension."""
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

    def _resolve_alignment_backend(self, ctx):
        backend = ctx.params.get("alignment_backend", "no_alignment")
        if isinstance(backend, str):
            backend_key = backend.lower()
            if backend_key in ("none", "off", "disabled", "no_alignment"):
                if not getattr(ctx, "_logged_alignment_backend", False):
                    print("[MFDenoiser] Alignment backend: none")
                    ctx._logged_alignment_backend = True
                return NoAlignment()
            if backend_key in ("farneback", "taichi_gpu", "gpu"):
                if not getattr(ctx, "_logged_alignment_backend", False):
                    print(f"[MFDenoiser] Alignment backend: {backend_key}")
                    ctx._logged_alignment_backend = True
                return FarnebackAlignment(
                    preset=ctx.params.get("farneback_preset", "robust"),
                    return_gpu=ctx.params.get("farneback_return_gpu", True),
                )
        if callable(backend) or hasattr(backend, "align_tile"):
            return backend
        return FarnebackAlignment()  # Fallback

    def _resolve_merge_backend(self, ctx):
        backend = ctx.params.get("merging_mode", "average")
        if isinstance(backend, str):
            backend = backend.lower()
            if backend == "average":
                from .Average import AverageMerge

                return AverageMerge()
            elif backend == "median":
                from .Median import MedianMerge

                return MedianMerge()
            elif backend in ("similarity", "spatial_fusion", "spatial"):
                return SimilarityMerge()
            else:
                raise ValueError(f"Unsupported merging mode: {backend}")
        if callable(backend) or hasattr(backend, "merge_tiles"):
            return backend
        raise ValueError("No valid merging backend could be resolved.")

    def run_tile_align(self, ctx, ref_tile, comp_tiles_list):
        """Align tiles using the resolved alignment backend."""
        backend = self._resolve_alignment_backend(ctx)
        aligned_tiles = []
        for comp_tile in comp_tiles_list:
            if hasattr(backend, "align_tile"):
                warped = backend.align_tile(ref_tile, comp_tile)
            else:
                # If backend is a simple callable function
                warped = backend(ref_tile, comp_tile)
            aligned_tiles.append(warped)
        return aligned_tiles

    def _run_average_gpu_chunked(
        self,
        ctx,
        frames,
        merge_backend,
        tile_size,
        overlap,
        x_starts,
    ):
        """Average GPU path using a banded accumulator to reduce peak VRAM."""
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer

        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
        out_shape = (
            (ctx.ref_h, ctx.ref_w, channels)
            if channels == 3
            else (ctx.ref_h, ctx.ref_w)
        )
        final_sum = np.zeros(out_shape, dtype=np.float32)
        final_weight = np.zeros((ctx.ref_h, ctx.ref_w), dtype=np.float32)

        chunk_count = int(ctx.params.get("gpu_accumulator_chunks", 4))
        chunk_count = max(1, min(chunk_count, ctx.ref_h))
        chunk_overlap_ratio = float(ctx.params.get("gpu_chunk_overlap", 0.25))
        base_chunk_h = int(np.ceil(ctx.ref_h / chunk_count))
        total_units = 0
        chunk_ranges = []
        for chunk_idx in range(chunk_count):
            core_start = chunk_idx * base_chunk_h
            core_end = min(ctx.ref_h, (chunk_idx + 1) * base_chunk_h)
            if core_start >= core_end:
                continue
            overlap_px = int(round((core_end - core_start) * chunk_overlap_ratio))
            ext_start = max(0, core_start - overlap_px)
            ext_end = min(ctx.ref_h, core_end + overlap_px)
            local_y_starts = self._compute_tile_starts(
                ext_end - ext_start, tile_size, overlap
            )
            chunk_ranges.append((ext_start, ext_end, local_y_starts))
            total_units += len(local_y_starts) * len(x_starts)

        tile_batch_size = int(ctx.params.get("gpu_tile_batch_size", 4))
        tile_batch_size = max(1, min(tile_batch_size, 8))
        processed_units = 0

        for ext_start, ext_end, local_y_starts in chunk_ranges:
            if ctx.stop_requested and ctx.stop_requested():
                return None, None, 0

            chunk_h = ext_end - ext_start
            acc_shape = (
                (chunk_h, ctx.ref_w, 3) if channels == 3 else (chunk_h, ctx.ref_w)
            )
            accumulator = taichi_aot.engine.allocate(acc_shape, dtype=np.float32)
            weight_accumulator = taichi_aot.engine.allocate(
                (chunk_h, ctx.ref_w), dtype=np.float32
            )
            zero_acc = taichi_aot.upload(np.zeros(acc_shape, dtype=np.float32))
            zero_weight = taichi_aot.upload(
                np.zeros((chunk_h, ctx.ref_w), dtype=np.float32)
            )
            taichi_aot.copy_field(zero_acc, accumulator)
            taichi_aot.copy_field(zero_weight, weight_accumulator)
            zero_acc.destroy()
            zero_weight.destroy()

            try:
                tile_jobs = []
                for y_idx, local_y in enumerate(local_y_starts):
                    for x_idx, x_start in enumerate(x_starts):
                        tile_jobs.append((y_idx, x_idx, local_y, x_start))

                def flush_stitch_batch(batch_items, hanning_win, unit_weight):
                    if not batch_items:
                        return
                    if any(
                        isinstance(tile_item, TaichiGPUBuffer)
                        for tile_item, _, _ in batch_items
                    ):
                        for tile_item, local_y_item, x_start_item in batch_items:
                            merge_backend.accumulate_tile_gpu(
                                tile_item,
                                hanning_win,
                                accumulator,
                                weight_accumulator,
                                local_y_item,
                                x_start_item,
                                unit_weight=unit_weight,
                            )
                        return
                    tiles_np = []
                    y0s = []
                    x0s = []
                    for tile_item, local_y_item, x_start_item in batch_items:
                        tiles_np.append(tile_item.astype(np.float32, copy=False))
                        y0s.append(local_y_item)
                        x0s.append(x_start_item)
                    batch_tiles = np.ascontiguousarray(np.stack(tiles_np, axis=0))
                    taichi_aot.stitch_tile_gpu(
                        batch_tiles,
                        unit_weight,
                        hanning_win,
                        accumulator,
                        weight_accumulator,
                        np.asarray(y0s, dtype=np.int32),
                        np.asarray(x0s, dtype=np.int32),
                    )

                def process_tile(local_y, x_start):
                    global_y = ext_start + local_y
                    tile_h = min(tile_size, ext_end - global_y)
                    tile_w = min(tile_size, ctx.ref_w - x_start)
                    if tile_h <= 0 or tile_w <= 0:
                        return

                    hanning_win = taichi_aot.hanning(
                        (tile_h, tile_w), exclude_boundary=False
                    )
                    unit_weight = taichi_aot.upload(
                        np.ones((tile_h, tile_w), dtype=np.float32)
                    )
                    ref_tile = frames[0][
                        global_y : global_y + tile_h, x_start : x_start + tile_w
                    ]
                    alignment_backend = self._resolve_alignment_backend(ctx)
                    stitch_batch = []

                    try:
                        stitch_batch.append((ref_tile, local_y, x_start))

                        for frame in frames[1:]:
                            comp_tile = frame[
                                global_y : global_y + tile_h,
                                x_start : x_start + tile_w,
                            ]
                            if hasattr(alignment_backend, "align_tile"):
                                warped_tile = alignment_backend.align_tile(
                                    ref_tile, comp_tile
                                )
                            else:
                                warped_tile = alignment_backend(ref_tile, comp_tile)

                            try:
                                if isinstance(warped_tile, TaichiGPUBuffer):
                                    flush_stitch_batch(
                                        stitch_batch, hanning_win, unit_weight
                                    )
                                    stitch_batch.clear()
                                    merge_backend.accumulate_tile_gpu(
                                        warped_tile,
                                        hanning_win,
                                        accumulator,
                                        weight_accumulator,
                                        local_y,
                                        x_start,
                                        unit_weight=unit_weight,
                                    )
                                else:
                                    stitch_batch.append((warped_tile, local_y, x_start))
                                    if len(stitch_batch) >= tile_batch_size:
                                        flush_stitch_batch(
                                            stitch_batch, hanning_win, unit_weight
                                        )
                                        stitch_batch.clear()
                            finally:
                                if isinstance(warped_tile, TaichiGPUBuffer):
                                    warped_tile.destroy()
                        flush_stitch_batch(stitch_batch, hanning_win, unit_weight)
                    finally:
                        unit_weight.destroy()
                        hanning_win.destroy()

                for y_parity in range(2):
                    for x_parity in range(2):
                        group = [
                            (local_y, x_start)
                            for y_idx, x_idx, local_y, x_start in tile_jobs
                            if y_idx % 2 == y_parity and x_idx % 2 == x_parity
                        ]
                        if not group:
                            continue

                        for local_y, x_start in group:
                            if ctx.stop_requested and ctx.stop_requested():
                                accumulator.destroy()
                                weight_accumulator.destroy()
                                return None, None, 0
                            process_tile(local_y, x_start)
                            processed_units += 1
                            if ctx.update_progress and total_units > 0:
                                prog = int(10 + (processed_units / total_units) * 80)
                                ctx.update_progress(
                                    prog,
                                    f"Processing chunked tile {processed_units}/{total_units}...",
                                )

                ref_chunk = ctx.reference_float[ext_start:ext_end]
                ref_gpu = taichi_aot.upload(ref_chunk.astype(np.float32, copy=False))
                normalized_gpu = taichi_aot.mean_division(
                    accumulator, weight_accumulator, ref_gpu
                )
                normalized_chunk = normalized_gpu.to_numpy()
                normalized_gpu.destroy()
                ref_gpu.destroy()
            finally:
                accumulator.destroy()
                weight_accumulator.destroy()

            blend = np.ones((chunk_h,), dtype=np.float32)
            overlap_px = max(1, int(round(base_chunk_h * chunk_overlap_ratio)))
            if ext_start > 0:
                fade_len = min(overlap_px, chunk_h)
                t = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
                blend[:fade_len] *= 0.5 - 0.5 * np.cos(np.pi * t)
            if ext_end < ctx.ref_h:
                fade_len = min(overlap_px, chunk_h)
                t = np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
                blend[-fade_len:] *= 0.5 - 0.5 * np.cos(np.pi * t)

            if channels == 3:
                final_sum[ext_start:ext_end] += normalized_chunk * blend[:, None, None]
            else:
                final_sum[ext_start:ext_end] += normalized_chunk * blend[:, None]
            final_weight[ext_start:ext_end] += blend[:, None]

        valid = final_weight > 1e-6
        final_normalized = np.zeros_like(final_sum)
        if channels == 3:
            np.divide(
                final_sum,
                final_weight[:, :, None],
                out=final_normalized,
                where=valid[:, :, None],
            )
            final_normalized[~valid] = ctx.reference_float[~valid]
        else:
            np.divide(final_sum, final_weight, out=final_normalized, where=valid)
            final_normalized[~valid] = ctx.reference_float[~valid]

        return (
            final_normalized,
            np.ones((ctx.ref_h, ctx.ref_w), dtype=np.float32),
            ctx.total_images,
        )

    def run_tile_merge(self, ctx):
        """Modular tile merging orchestrator working in continue_to_merge mode.

        Performs tile-by-tile alignment and merging in-memory using pluggable backends.
        """
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer

        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
        use_gpu_stitch = ctx.params.get("gpu_tile_stitch", True)
        tile_size = 512
        overlap = 0.3
        y_starts = self._compute_tile_starts(ctx.ref_h, tile_size, overlap)
        x_starts = self._compute_tile_starts(ctx.ref_w, tile_size, overlap)
        total_tiles = len(y_starts) * len(x_starts)

        # Resolve the merge backend
        merge_backend = self._resolve_merge_backend(ctx)
        use_chunked_gpu_accumulator = (
            use_gpu_stitch
            and hasattr(merge_backend, "accumulate_tile_gpu")
            and ctx.params.get("gpu_chunked_accumulator", True)
        )

        if use_gpu_stitch and not use_chunked_gpu_accumulator:
            acc_shape = (
                (ctx.ref_h, ctx.ref_w, 3) if channels == 3 else (ctx.ref_h, ctx.ref_w)
            )
            accumulator = taichi_aot.engine.allocate(acc_shape, dtype=np.float32)
            weight_accumulator = taichi_aot.engine.allocate(
                (ctx.ref_h, ctx.ref_w), dtype=np.float32
            )
            zero_acc = taichi_aot.upload(np.zeros(acc_shape, dtype=np.float32))
            zero_weight = taichi_aot.upload(
                np.zeros((ctx.ref_h, ctx.ref_w), dtype=np.float32)
            )
            taichi_aot.copy_field(zero_acc, accumulator)
            taichi_aot.copy_field(zero_weight, weight_accumulator)
            zero_acc.destroy()
            zero_weight.destroy()
        elif not use_gpu_stitch:
            accumulator = np.zeros((ctx.ref_h, ctx.ref_w, channels), dtype=np.float32)
            weight_accumulator = np.zeros((ctx.ref_h, ctx.ref_w), dtype=np.float32)
        else:
            accumulator = None
            weight_accumulator = None

        # Load all images ONCE to avoid repeated disk reads and demosaicing inside the loop
        if ctx.update_progress:
            ctx.update_progress(5, "Loading and preparing all frames...")
        batch_images = self._load_images(
            ctx.data_source,
            (0, ctx.total_images),
            ctx.stop_requested,
            linear_mode=ctx.is_linear_mode,
        )
        frames = []
        while batch_images:
            img = batch_images.pop(0)
            frames.append(normalize_image(img, ctx.ref_dtype))
            del img

        if use_chunked_gpu_accumulator:
            result = self._run_average_gpu_chunked(
                ctx,
                frames,
                merge_backend,
                tile_size,
                overlap,
                x_starts,
            )
            del frames
            gc.collect()
            return result

        processed_tiles = 0

        for y_start in y_starts:
            for x_start in x_starts:
                if ctx.stop_requested and ctx.stop_requested():
                    if use_gpu_stitch:
                        accumulator.destroy()
                        weight_accumulator.destroy()
                    return None, None, 0

                tile_h = min(tile_size, ctx.ref_h - y_start)
                tile_w = min(tile_size, ctx.ref_w - x_start)
                hanning_win = (
                    taichi_aot.hanning((tile_h, tile_w), exclude_boundary=False)
                    if use_gpu_stitch
                    else self._make_hanning_window(tile_h, tile_w)
                )

                # Extract tiles directly from in-memory frames
                comp_tiles = [
                    f[y_start : y_start + tile_h, x_start : x_start + tile_w]
                    for f in frames
                ]
                ref_tile = comp_tiles[0]

                if use_gpu_stitch and hasattr(merge_backend, "accumulate_tile_gpu"):
                    unit_weight = taichi_aot.upload(
                        np.ones((tile_h, tile_w), dtype=np.float32)
                    )
                    alignment_backend = self._resolve_alignment_backend(ctx)
                    try:
                        merge_backend.accumulate_tile_gpu(
                            ref_tile,
                            hanning_win,
                            accumulator,
                            weight_accumulator,
                            y_start,
                            x_start,
                            unit_weight=unit_weight,
                        )
                        for comp_tile in comp_tiles[1:]:
                            if ctx.stop_requested and ctx.stop_requested():
                                if isinstance(hanning_win, TaichiGPUBuffer):
                                    hanning_win.destroy()
                                unit_weight.destroy()
                                accumulator.destroy()
                                weight_accumulator.destroy()
                                return None, None, 0

                            if hasattr(alignment_backend, "align_tile"):
                                warped_tile = alignment_backend.align_tile(
                                    ref_tile, comp_tile
                                )
                            else:
                                warped_tile = alignment_backend(ref_tile, comp_tile)

                            try:
                                merge_backend.accumulate_tile_gpu(
                                    warped_tile,
                                    hanning_win,
                                    accumulator,
                                    weight_accumulator,
                                    y_start,
                                    x_start,
                                    unit_weight=unit_weight,
                                )
                            finally:
                                if isinstance(warped_tile, TaichiGPUBuffer):
                                    warped_tile.destroy()
                    finally:
                        unit_weight.destroy()
                        if isinstance(hanning_win, TaichiGPUBuffer):
                            hanning_win.destroy()

                    processed_tiles += 1
                    if ctx.update_progress and total_tiles > 0:
                        prog = int(10 + (processed_tiles / total_tiles) * 80)
                        ctx.update_progress(
                            prog, f"Processing tile {processed_tiles}/{total_tiles}..."
                        )
                    continue

                # Align comparison tiles against the reference tile
                aligned_batch = self.run_tile_align(ctx, ref_tile, comp_tiles[1:])
                aligned_tiles_all = [ref_tile] + aligned_batch

                if use_gpu_stitch and hasattr(merge_backend, "accumulate_tiles_gpu"):
                    merge_backend.accumulate_tiles_gpu(
                        aligned_tiles_all,
                        hanning_win,
                        accumulator,
                        weight_accumulator,
                        y_start,
                        x_start,
                    )

                    for item in aligned_batch:
                        if isinstance(item, TaichiGPUBuffer):
                            item.destroy()
                    if isinstance(hanning_win, TaichiGPUBuffer):
                        hanning_win.destroy()

                    processed_tiles += 1
                    if ctx.update_progress and total_tiles > 0:
                        prog = int(10 + (processed_tiles / total_tiles) * 80)
                        ctx.update_progress(
                            prog, f"Processing tile {processed_tiles}/{total_tiles}..."
                        )
                    continue

                # Call the pluggable merge backend
                if len(aligned_tiles_all) > 0:
                    if hasattr(merge_backend, "merge_tiles"):
                        try:
                            merged_tile, tile_weight = merge_backend.merge_tiles(
                                aligned_tiles_all,
                                return_gpu=use_gpu_stitch,
                            )
                        except TypeError:
                            merged_tile, tile_weight = merge_backend.merge_tiles(
                                aligned_tiles_all
                            )
                    else:
                        merged_tile, tile_weight = merge_backend(aligned_tiles_all)
                else:
                    merged_tile = ref_tile
                    tile_weight = np.ones((tile_h, tile_w), dtype=np.float32)

                # Release the GPU buffers allocated during tile alignment to prevent VRAM leak
                for item in aligned_batch:
                    if isinstance(item, TaichiGPUBuffer):
                        item.destroy()

                # Stitch using Hanning window blending
                roi_y = slice(y_start, y_start + tile_h)
                roi_x = slice(x_start, x_start + tile_w)

                if use_gpu_stitch:
                    owned_merged = not isinstance(merged_tile, TaichiGPUBuffer)
                    owned_weight = not isinstance(tile_weight, TaichiGPUBuffer)
                    merged_gpu = (
                        taichi_aot.upload(merged_tile.astype(np.float32, copy=False))
                        if owned_merged
                        else merged_tile
                    )
                    tile_weight_gpu = (
                        taichi_aot.upload(tile_weight.astype(np.float32, copy=False))
                        if owned_weight
                        else tile_weight
                    )
                    taichi_aot.stitch_tile_gpu(
                        merged_gpu,
                        tile_weight_gpu,
                        hanning_win,
                        accumulator,
                        weight_accumulator,
                        y_start,
                        x_start,
                    )
                    if owned_merged:
                        merged_gpu.destroy()
                    if owned_weight:
                        tile_weight_gpu.destroy()
                    if isinstance(hanning_win, TaichiGPUBuffer):
                        hanning_win.destroy()
                    if isinstance(merged_tile, TaichiGPUBuffer):
                        merged_tile.destroy()
                    if isinstance(tile_weight, TaichiGPUBuffer):
                        tile_weight.destroy()
                else:
                    if channels == 3 and merged_tile.ndim == 2:
                        merged_tile = merged_tile[..., np.newaxis]

                    if channels == 3:
                        accumulator[roi_y, roi_x] += (
                            merged_tile * hanning_win[..., np.newaxis]
                        )
                    else:
                        accumulator[roi_y, roi_x] += merged_tile * hanning_win

                    weight_accumulator[roi_y, roi_x] += hanning_win

                processed_tiles += 1
                if ctx.update_progress and total_tiles > 0:
                    prog = int(10 + (processed_tiles / total_tiles) * 80)
                    ctx.update_progress(
                        prog, f"Processing tile {processed_tiles}/{total_tiles}..."
                    )

        # Free loaded frames
        del frames
        gc.collect()

        return accumulator, weight_accumulator, ctx.total_images

    def normalize_result(self, ctx, sum_img, sum_weight, frame_count):
        """Normalize accumulated result and scale back to original bit-depth."""
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import TaichiGPUBuffer

        if sum_img is None or frame_count <= 0:
            channels = (
                ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
            )
            return np.zeros((ctx.ref_h, ctx.ref_w, channels), dtype=ctx.ref_dtype)

        if isinstance(sum_img, TaichiGPUBuffer):
            ref_gpu = taichi_aot.upload(
                ctx.reference_float.astype(np.float32, copy=False)
            )
            normalized_gpu = taichi_aot.mean_division(sum_img, sum_weight, ref_gpu)
            normalized = normalized_gpu.to_numpy()
            normalized_gpu.destroy()
            ref_gpu.destroy()
            sum_img.destroy()
            sum_weight.destroy()
        else:
            # Normalize: divide accumulated sum by the weight map
            valid_mask = sum_weight > 1e-6
            normalized = np.zeros_like(sum_img)
            if normalized.ndim == 3:
                np.divide(
                    sum_img,
                    sum_weight[:, :, np.newaxis],
                    out=normalized,
                    where=valid_mask[:, :, np.newaxis],
                )
            else:
                np.divide(sum_img, sum_weight, out=normalized, where=valid_mask)

            # Fallback: fill invalid/unmapped pixels with reference image float representation
            if not np.all(valid_mask):
                normalized[~valid_mask] = ctx.reference_float[~valid_mask]

        # Scale back to original bit-depth (e.g. uint8/uint16) atau pertahankan float [0..1]
        if np.issubdtype(ctx.ref_dtype, np.integer):
            max_val = np.iinfo(ctx.ref_dtype).max
        else:
            max_val = 1.0
        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
        if channels == 1:
            if normalized.ndim == 3:
                final_out = np.mean(normalized * max_val, axis=2)
            else:
                final_out = normalized * max_val
        else:
            final_out = normalized * max_val

        return np.clip(final_out, 0, max_val).astype(ctx.ref_dtype)

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

        if merging_mode is not None:
            ctx.params["merging_mode"] = merging_mode
        if output_suffix is not None:
            ctx.params["output_suffix"] = output_suffix

        # Stage 1: Load Data
        ctx = self.stage_load_data(ctx)
        if not ctx.total_images:
            if update_progress:
                update_progress(100, _lang().NO_IMAGE_PATH_PROCESSED_IMAGE)
            return None

        # Check Linear RAW Mode
        if ctx.is_linear_mode:
            if ctx.params.get("enable_linear_mode", False):
                return self._process_linear_placeholder(ctx)
            else:
                ctx.is_linear_mode = False

        # Stage 2: Merge (run_tile_merge handles both align and merge on-the-fly)
        if ctx.update_progress:
            merge_start = ctx.params.get("merge_progress_start", 0)
            ctx.update_progress(merge_start, "Merging frames...")

        sum_img, sum_weight, frame_count = self.run_tile_merge(ctx)
        if ctx.stop_requested and ctx.stop_requested():
            return None

        # Stage 4: Normalize Result
        if ctx.update_progress:
            ctx.update_progress(95, "Finalizing fusion...")
        result = self.normalize_result(ctx, sum_img, sum_weight, frame_count)

        # Stage 5: Save
        output_path = self.stage_save(ctx, result)
        return output_path

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
            from taichi_library.taichi_aot import allocate_pinned_numpy

            with h5py.File(data_source, "r") as h5f:
                # Sort keys numerically to ensure order like image_0, image_1, image_2... instead of alphabetical (e.g. image_10 before image_2)
                sorted_keys = sorted(
                    h5f.keys(),
                    key=lambda x: (
                        int(x.split("_")[1])
                        if "_" in x and x.split("_")[1].isdigit()
                        else x
                    ),
                )
                keys = sorted_keys[batch_start:batch_end]
                for key in keys:
                    if stop_requested and stop_requested():
                        break
                    ds = h5f[key]
                    pinned_arr = allocate_pinned_numpy(ds.shape, ds.dtype)
                    ds.read_direct(pinned_arr)
                    batch_images.append(pinned_arr)
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


def running_similarity(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
):
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode="similarity",
        output_suffix="similarity",
    )


if __name__ == "__main__":
    main("pixel_refine_database.db")
