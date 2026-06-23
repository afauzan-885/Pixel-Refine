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

    def align_tile(self, ref_tile, comp_tile):
        import numpy as np
        from taichi_library import taichi_aot

        # Conv to float32 [0..255] for farneback_flow input
        if ref_tile.ndim == 3:
            # RGB to Gray
            ref_gray = (
                0.299 * ref_tile[..., 0] + 
                0.587 * ref_tile[..., 1] + 
                0.114 * ref_tile[..., 2]
            ).astype(np.float32) * 255.0
        else:
            ref_gray = ref_tile.astype(np.float32) * 255.0

        if comp_tile.ndim == 3:
            comp_gray = (
                0.299 * comp_tile[..., 0] + 
                0.587 * comp_tile[..., 1] + 
                0.114 * comp_tile[..., 2]
            ).astype(np.float32) * 255.0
        else:
            comp_gray = comp_tile.astype(np.float32) * 255.0

        h, w = ref_tile.shape[:2]

        # Hitung optical flow dengan Taichi AOT Farneback GPU (mengembalikan numpy array)
        flow_np = taichi_aot.farneback_flow(
            ref_gray,
            comp_gray,
            pyr_scale=0.5,
            num_levels=3,
            win_size=15,
            num_iters=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )

        # Lakukan warping (remap) di GPU secara langsung menggunakan flow_np
        # return_gpu=True agar output warped tetap berada di VRAM
        warped_gpu = taichi_aot.remap_with_flow(
            comp_tile.astype(np.float32),
            flow_np,
            h,
            w,
            return_gpu=True,
        )

        return warped_gpu


# ---------------------------------------------------------------------------
# Pluggable Merging Backends
# ---------------------------------------------------------------------------
class SimilarityMerge:
    """Similarity merging backend using Taichi GPU (Vulkan) AOT merging loop."""

    def merge_tiles(self, aligned_tiles):
        import cv2
        import numpy as np
        from taichi_library import taichi_aot
        from taichi_library.taichi_aot.engine import AOTEngine, TaichiGPUBuffer
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import estimate_noise_in_python
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            generate_spatial_weights_taichi,
            accumulate_spatial_merging_taichi,
        )

        ref_tile = aligned_tiles[0]
        tile_h, tile_w = ref_tile.shape[:2]
        channels = ref_tile.shape[2] if ref_tile.ndim == 3 else 1

        if ref_tile.ndim == 3:
            ref_gray = taichi_aot.cvtColor((ref_tile * 255).astype(np.uint8), taichi_aot.COLOR_RGB2GRAY).astype(np.float32) / 255.0
        else:
            ref_gray = ref_tile.copy()

        ref_noise_sigma = estimate_noise_in_python(ref_gray)
        if ref_noise_sigma is None or ref_noise_sigma < 1e-5:
            ref_noise_sigma = 0.01

        engine = AOTEngine()

        ref_gray_gpu = taichi_aot.upload(ref_gray)
        sum_gpu = taichi_aot.upload(ref_tile.copy())
        
        weight_sum_full_gpu = taichi_aot.upload(np.ones((tile_h, tile_w), dtype=np.float32))

        # Setup tiling for weight generation (16x16 with 0.3 overlap)
        tile_size_sub = 16
        overlap_sub = 0.3
        step_y = max(int(tile_size_sub * (1.0 - overlap_sub)), 1)
        step_x = max(int(tile_size_sub * (1.0 - overlap_sub)), 1)

        row_starts = np.arange(0, tile_h - tile_size_sub + 1, step_y, dtype=np.int32)
        if tile_h > tile_size_sub and (row_starts.size == 0 or row_starts[-1] != tile_h - tile_size_sub):
            row_starts = np.append(row_starts, tile_h - tile_size_sub)
        row_starts = np.ascontiguousarray(np.unique(row_starts).astype(np.int32))

        col_starts = np.arange(0, tile_w - tile_size_sub + 1, step_x, dtype=np.int32)
        if tile_w > tile_size_sub and (col_starts.size == 0 or col_starts[-1] != tile_w - tile_size_sub):
            col_starts = np.append(col_starts, tile_w - tile_size_sub)
        col_starts = np.ascontiguousarray(np.unique(col_starts).astype(np.int32))

        rows_gpu = taichi_aot.upload(row_starts)
        rows_gpu.dtype = np.int32
        cols_gpu = taichi_aot.upload(col_starts)
        cols_gpu.dtype = np.int32

        base_window_gpu = taichi_aot.hanning((tile_size_sub, tile_size_sub), exclude_boundary=False)
        weight_work_gpu = engine.allocate((tile_h, tile_w), dtype=np.float32, host_accessible=True)

        try:
            for comp_tile in aligned_tiles[1:]:
                # Check if already a TaichiGPUBuffer to avoid CPU-GPU upload overhead
                if isinstance(comp_tile, TaichiGPUBuffer):
                    comp_tile_gpu = comp_tile
                    
                    # Compute grayscale of GPU buffer for weight estimation
                    # If it's a vector3, we convert it to grayscale on GPU
                    if channels == 3:
                        # Grab numpy array fallback or compute directly if possible
                        # To keep it simple and robust, we download only the gray representation or cast
                        comp_np = comp_tile.to_numpy()
                        comp_gray = taichi_aot.cvtColor((comp_np * 255).astype(np.uint8), taichi_aot.COLOR_RGB2GRAY).astype(np.float32) / 255.0
                        comp_gray_gpu = taichi_aot.upload(comp_gray)
                    else:
                        comp_gray_gpu = comp_tile
                else:
                    if comp_tile.ndim == 3:
                        comp_gray = taichi_aot.cvtColor((comp_tile * 255).astype(np.uint8), taichi_aot.COLOR_RGB2GRAY).astype(np.float32) / 255.0
                    else:
                        comp_gray = comp_tile.copy()

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

            # Download and divide
            sum_np = sum_gpu.to_numpy()
            weight_sum_np = weight_sum_full_gpu.to_numpy()

            valid_mask = weight_sum_np > 1e-6
            merged_tile = np.zeros_like(sum_np)
            if sum_np.ndim == 3:
                np.divide(sum_np, weight_sum_np[..., np.newaxis], out=merged_tile, where=valid_mask[..., np.newaxis])
                mask_3d = np.repeat(~valid_mask[..., np.newaxis], channels, axis=2)
                merged_tile[mask_3d] = ref_tile[mask_3d]
            else:
                np.divide(sum_np, weight_sum_np, out=merged_tile, where=valid_mask)
                merged_tile[~valid_mask] = ref_tile[~valid_mask]

            weight_map = np.ones((tile_h, tile_w), dtype=np.float32)
            return merged_tile, weight_map

        finally:
            for buf in [
                sum_gpu,
                weight_sum_full_gpu,
                base_window_gpu,
                rows_gpu,
                cols_gpu,
                weight_work_gpu,
                ref_gray_gpu,
            ]:
                if buf:
                    try:
                        buf.destroy()
                    except:
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
            "alignment_backend": sim_config.get("alignment_backend", "taichi_gpu"),
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
        backend = ctx.params.get("alignment_backend", "farneback")
        if isinstance(backend, str):
            if backend.lower() == "farneback":
                return FarnebackAlignment()
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

    def run_tile_merge(self, ctx):
        """Modular tile merging orchestrator working in continue_to_merge mode.

        Performs tile-by-tile alignment and merging in-memory using pluggable backends.
        """
        channels = ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
        accumulator = np.zeros((ctx.ref_h, ctx.ref_w, channels), dtype=np.float32)
        weight_accumulator = np.zeros((ctx.ref_h, ctx.ref_w), dtype=np.float32)

        tile_size = 512
        overlap = 0.3
        y_starts = self._compute_tile_starts(ctx.ref_h, tile_size, overlap)
        x_starts = self._compute_tile_starts(ctx.ref_w, tile_size, overlap)
        total_tiles = len(y_starts) * len(x_starts)

        # Resolve the merge backend
        merge_backend = self._resolve_merge_backend(ctx)

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

        processed_tiles = 0

        for y_start in y_starts:
            for x_start in x_starts:
                if ctx.stop_requested and ctx.stop_requested():
                    return None, None, 0

                tile_h = min(tile_size, ctx.ref_h - y_start)
                tile_w = min(tile_size, ctx.ref_w - x_start)
                hanning_win = self._make_hanning_window(tile_h, tile_w)

                # Extract tiles directly from in-memory frames
                comp_tiles = [
                    f[y_start : y_start + tile_h, x_start : x_start + tile_w]
                    for f in frames
                ]
                ref_tile = comp_tiles[0]

                # Align comparison tiles against the reference tile
                aligned_batch = self.run_tile_align(ctx, ref_tile, comp_tiles[1:])
                aligned_tiles_all = [ref_tile] + aligned_batch

                # Call the pluggable merge backend
                if len(aligned_tiles_all) > 0:
                    if hasattr(merge_backend, "merge_tiles"):
                        merged_tile, tile_weight = merge_backend.merge_tiles(
                            aligned_tiles_all
                        )
                    else:
                        merged_tile, tile_weight = merge_backend(aligned_tiles_all)
                else:
                    merged_tile = ref_tile
                    tile_weight = np.ones((tile_h, tile_w), dtype=np.float32)

                # Release the GPU buffers allocated during tile alignment to prevent VRAM leak
                from taichi_library.taichi_aot.engine import TaichiGPUBuffer
                for item in aligned_batch:
                    if isinstance(item, TaichiGPUBuffer):
                        item.destroy()

                # Stitch using Hanning window blending
                roi_y = slice(y_start, y_start + tile_h)
                roi_x = slice(x_start, x_start + tile_w)

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
        if sum_img is None or frame_count <= 0:
            channels = (
                ctx.reference_image.shape[2] if ctx.reference_image.ndim == 3 else 1
            )
            return np.zeros((ctx.ref_h, ctx.ref_w, channels), dtype=ctx.ref_dtype)

        # Normalize: divide accumulated sum by the weight map
        valid_mask = sum_weight > 1e-6
        normalized = np.zeros_like(sum_img)
        np.divide(
            sum_img,
            sum_weight[:, :, np.newaxis],
            out=normalized,
            where=valid_mask[:, :, np.newaxis],
        )

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
            final_out = np.mean(normalized * max_val, axis=2)
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
                sorted_keys = sorted(h5f.keys(), key=lambda x: int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else x)
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
