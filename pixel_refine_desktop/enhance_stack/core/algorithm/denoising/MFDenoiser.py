"""
MFDenoiser.py - denoising orchestration skeleton.

This file intentionally contains process structure only. Alignment and merging
algorithms are left as explicit extension points so the pipeline can be rebuilt
incrementally without triggering heavy GPU/AOT work.
"""

import json
import os
import gc
import sqlite3
from dataclasses import dataclass, field
from typing import Optional

import h5py
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox, QProgressBar, QVBoxLayout

from config import GENERAL_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    cleanup_old_hdf5_files,
    extract_exif,
    get_all_image_paths_for_single_process,
    is_hdf5_cache_valid,
    load_images_from_paths,
    resize_all_with_padding,
    resize_with_padding,
    save_image,
    save_linear_dng,
    save_to_hdf5,
    setup_balanced_batching,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.feature_matching_utils.feature_matching_post_process import (
    apply_global_crop,
    apply_non_crop,
    compute_global_crop_bounds,
    crop_image,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)
from resources.styles.stylesheet import PROGRESS_BAR


def _lang():
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    return language_config


def _progress(callback, percent, message):
    if callback:
        callback(int(percent), str(message))


def _frame_info(frame):
    if frame is None:
        return "None"
    shape = getattr(frame, "shape", None)
    dtype = getattr(frame, "dtype", None)
    return f"shape={shape}, dtype={dtype}"


class NoAlignmentAlgorithm:
    NAME = "No Alignment"
    KIND = "alignment"
    DESCRIPTION = "Skip alignment."

    def run(self, ctx, frames, batch_plan=None):
        print(f"[MFDenoiser][Alignment:No Alignment] Passing through {len(frames)} frame(s).")
        for idx, frame in enumerate(frames):
            print(f"[MFDenoiser][Alignment:No Alignment] frame_{idx}: {_frame_info(frame)}")
        return list(frames)


class NoDenoisingAlgorithm:
    NAME = "No Denoising"
    KIND = "denoising"
    DESCRIPTION = "Return the reference/aligned first frame unchanged."

    def run(self, ctx, frames, batch_plan=None):
        print(f"[MFDenoiser][Denoising:No Denoising] Received {len(frames)} frame(s). Returning frame_0.")
        if not frames:
            return None
        print(f"[MFDenoiser][Denoising:No Denoising] frame_0: {_frame_info(frames[0])}")
        return np.array(frames[0], copy=True)


def get_alignment_registry():
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.AKAZE import (
        AKAZEAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.Light_Glue import (
        LightGlueAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.ORB import (
        ORBAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow_cpu import (
        FarnebackFlowCPU,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_cpu import (
        LucasKanadeCPU,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_gpu import (
        LucasKanadeGPU,
    )

    algorithms = [
        NoAlignmentAlgorithm(),
        ORBAlgorithm(),
        AKAZEAlgorithm(),
        LightGlueAlgorithm(),
        FarnebackFlowCPU(),
        LucasKanadeCPU(),
        LucasKanadeGPU(),
    ]
    return {algo.NAME: algo for algo in algorithms}


def get_denoising_registry():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
        AverageDenoisingAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_fusion import (
        SpatialFusionDenoisingAlgorithm,
    )

    algorithms = [
        NoDenoisingAlgorithm(),
        AverageDenoisingAlgorithm(),
        SpatialFusionDenoisingAlgorithm(),
    ]
    return {algo.NAME: algo for algo in algorithms}


def get_available_algorithms(category):
    if category == "alignment":
        return get_alignment_registry()
    if category == "denoising":
        return get_denoising_registry()
    return {}


def get_algorithm_options(category):
    return [
        (name, getattr(algo, "DESCRIPTION", name))
        for name, algo in get_available_algorithms(category).items()
    ]


def get_algorithm_names(category):
    return list(get_available_algorithms(category).keys())


def _normalize_algorithm_name(name):
    return str(name or "").strip().casefold()


def _resolve_algorithm(registry, requested_name, fallback_name):
    if requested_name in registry:
        return registry[requested_name]

    normalized = _normalize_algorithm_name(requested_name)
    for name, algorithm in registry.items():
        if _normalize_algorithm_name(name) == normalized:
            return algorithm

    fallback = registry[fallback_name]
    print(
        f"[MFDenoiser][Registry] Unknown algorithm '{requested_name}', "
        f"falling back to '{fallback.NAME}'. Available={list(registry.keys())}"
    )
    return fallback


@dataclass
class PipelineContext:
    db_path: str
    image_paths: list = field(default_factory=list)
    frames: list = field(default_factory=list)
    aligned_frames: list = field(default_factory=list)
    result_image: Optional[np.ndarray] = None
    reference_image: Optional[np.ndarray] = None
    ref_dtype: object = None
    ref_h: int = 0
    ref_w: int = 0
    output_name_base: str = "stack"
    total_images: int = 0
    hdf5_path: str = ""
    use_hdf5_cache: bool = False
    cache_is_valid: bool = False
    needs_alignment: bool = True
    batch_plan: list = field(default_factory=list)
    params: dict = field(default_factory=dict)
    is_linear_mode: bool = False
    update_progress: object = None
    stop_requested: object = None
    single_process: bool = True
    batch_id: object = None
    clear_raw: bool = True


class MFDenoiserAlgorithm:
    """Main orchestrator for future multi-frame denoising modes."""

    def __init__(self, db_path="pixel_refine_database.db"):
        self.db_path = db_path

    def _get_image_paths(self, batch_id=None):
        if batch_id is None:
            return get_all_image_paths_for_single_process(self.db_path)

        conn = sqlite3.connect(self.db_path)
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
        paths = [row[0] for row in cursor.fetchall()]
        conn.close()
        return paths

    def _load_params(self):
        try:
            from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
                load_similarity_config,
            )

            config = load_similarity_config()
        except Exception:
            config = {}

        params = {
            "processing_mode": config.get("mfdenoiser_processing_mode", "auto"),
            "tile_size": int(config.get("tile_based_tile_size", 256)),
            "tile_overlap": float(config.get("tile_based_overlap_percent", 0.20)),
            "alignment_plan": config.get("mfdenoiser_alignment_plan", "No Alignment"),
            "merge_plan": config.get("mfdenoiser_merge_plan", "No Denoising"),
            "batch_size": int(config.get("mfdenoiser_batch_size", 15)),
            "use_alignment_cache": bool(config.get("mfdenoiser_use_alignment_cache", False)),
            "clear_raw": bool(config.get("mfdenoiser_clear_raw", True)),
            "output_suffix": "mf_denoiser",
        }
        print(f"[MFDenoiser][Config] params={params}")

        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general = json.load(f)
                params["enable_linear_mode"] = general.get("enable_linear_mode", False)
        except (OSError, json.JSONDecodeError):
            params["enable_linear_mode"] = False

        return params

    def load_process(self, ctx):
        """Load input frames and initialize shared pipeline metadata."""
        self.prepare_input_paths(ctx)
        if not ctx.image_paths:
            return ctx

        _progress(ctx.update_progress, 0, "Loading frames...")
        load_res = load_images_from_paths(
            ctx.image_paths,
            ctx.stop_requested,
            linear_mode=ctx.is_linear_mode,
            capture_ref_proxy=False,
            update_progress=ctx.update_progress,
            progress_start=0,
            progress_end=20,
        )
        frames = load_res[0] if isinstance(load_res, tuple) else load_res
        if not frames:
            ctx.total_images = 0
            print("[MFDenoiser][Load] No frames loaded.")
            return ctx

        resize_res = resize_all_with_padding(
            frames,
            method="preserve",
            stop_requested=ctx.stop_requested,
            force_even=True,
        )
        if resize_res and resize_res[0]:
            if ctx.params.get("clear_raw", True):
                del frames
                gc.collect()
            frames = resize_res[0]

        ctx.frames = frames
        ctx.reference_image = frames[0]
        ctx.ref_dtype = ctx.reference_image.dtype
        ctx.ref_h, ctx.ref_w = ctx.reference_image.shape[:2]
        print(f"[MFDenoiser][Load] loaded_frames={len(ctx.frames)}")
        for idx, frame in enumerate(ctx.frames):
            print(f"[MFDenoiser][Load] frame_{idx}: {_frame_info(frame)}")
        return ctx

    def prepare_input_paths(self, ctx):
        """Load only paths and shared metadata; image arrays stay unloaded."""
        ctx.image_paths = self._get_image_paths(
            ctx.batch_id if not ctx.single_process else None
        )
        ctx.total_images = len(ctx.image_paths)
        print(
            f"[MFDenoiser][Load] mode={'single' if ctx.single_process else 'batch'} "
            f"batch_id={ctx.batch_id} paths={ctx.total_images}"
        )
        for idx, path in enumerate(ctx.image_paths):
            print(f"[MFDenoiser][Load] path_{idx}: {path}")
        if not ctx.image_paths:
            return ctx

        ref_name = os.path.splitext(os.path.basename(ctx.image_paths[0]))[0]
        ctx.output_name_base = ref_name or "stack"

        is_linear = ctx.params.get("enable_linear_mode", False)
        _, ext = os.path.splitext(ctx.image_paths[0])
        ctx.is_linear_mode = bool(
            is_linear and ext.lower() in (".dng", ".cr2", ".cr3", ".nef", ".arw")
        )
        return ctx

    def build_batch_plan(self, ctx):
        """Create batch ranges. The plan is owned by run_pipeline orchestration."""
        batch_size = max(1, int(ctx.params.get("batch_size", 15)))
        ctx.batch_plan = setup_balanced_batching(
            ctx.total_images,
            _lang(),
            max_batch_size=batch_size,
        )
        print(f"[MFDenoiser][Batch] batch_size={batch_size} plan={ctx.batch_plan}")
        return ctx.batch_plan

    def _can_stream_load_for_merge(self, ctx, alignment_algorithm):
        """Return True when images can stay as paths until the merge stage."""
        merge_name = _normalize_algorithm_name(ctx.params.get("merge_plan", "No Denoising"))
        alignment_name = _normalize_algorithm_name(
            getattr(alignment_algorithm, "NAME", ctx.params.get("alignment_plan", "No Alignment"))
        )
        return merge_name == "average" and alignment_name == "no alignment"

    def prepare_alignment_cache_policy(self, ctx):
        """Resolve HDF5 cache path and decide whether alignment is needed."""
        align_dir = os.path.join("database", "align")
        os.makedirs(align_dir, exist_ok=True)
        ctx.hdf5_path = (
            os.path.join(align_dir, "aligned_images.h5")
            if ctx.single_process
            else os.path.join(align_dir, f"aligned_image_batch_{ctx.batch_id}.h5")
        )
        ctx.use_hdf5_cache = bool(ctx.params.get("use_alignment_cache", False))

        cleanup_old_hdf5_files(ctx.hdf5_path)

        ref_path = ctx.image_paths[0] if ctx.image_paths else ""
        ctx.cache_is_valid = (
            ctx.use_hdf5_cache
            and bool(ref_path)
            and os.path.exists(ctx.hdf5_path)
            and is_hdf5_cache_valid(ctx.hdf5_path, ref_path)
        )
        ctx.needs_alignment = not ctx.cache_is_valid
        print(
            f"[MFDenoiser][Cache] use={ctx.use_hdf5_cache} valid={ctx.cache_is_valid} "
            f"needs_alignment={ctx.needs_alignment} hdf5_path={ctx.hdf5_path}"
        )
        if ctx.cache_is_valid:
            print(f"[MFDenoiser] Alignment cache valid: {ctx.hdf5_path}")
        elif ctx.use_hdf5_cache:
            print(f"[MFDenoiser] Alignment cache will be rebuilt later: {ctx.hdf5_path}")
        return ctx

    def _load_single_frame(self, ctx, path, target_dims=None):
        load_res = load_images_from_paths(
            [path],
            ctx.stop_requested,
            linear_mode=ctx.is_linear_mode,
            capture_ref_proxy=False,
        )
        frames = load_res[0] if isinstance(load_res, tuple) else load_res
        if not frames:
            return None
        frame = frames[0]
        if ctx.params.get("clear_raw", True):
            del frames
            del load_res
            gc.collect()
        if target_dims is not None and frame.shape[:2] != tuple(target_dims):
            resized = resize_with_padding(frame, target_dims)
            if ctx.params.get("clear_raw", True):
                del frame
                gc.collect()
            frame = resized
        return frame

    def _average_accumulate(self, sum_image, count, frame):
        if frame is None:
            return sum_image, count
        if sum_image is None:
            sum_image = np.zeros(frame.shape, dtype=np.float32)
        sum_image += frame.astype(np.float32, copy=False)
        return sum_image, count + 1

    def _average_finalize(self, ctx, sum_image, count):
        if sum_image is None or count <= 0:
            return None
        result = sum_image / float(count)
        dtype = ctx.ref_dtype or getattr(ctx.reference_image, "dtype", result.dtype)
        if np.issubdtype(dtype, np.integer):
            info = np.iinfo(dtype)
            result = np.clip(result, info.min, info.max)
        return result.astype(dtype, copy=False)

    def feature_matching_process(self, ctx, algorithm, batch_plan=None):
        """Run feature-matching alignment as a pure alignment stage.

        The algorithm only produces a motion/keypoint plan. MFDenoiser owns the
        post-process policy: transform estimation, warp/crop, HDF5 persistence,
        and cleanup.
        """
        if not hasattr(algorithm, "build_motion_plan"):
            return None
        if not ctx.image_paths:
            return ctx
        if ctx.cache_is_valid:
            print(f"[MFDenoiser][FeatureMatching] using valid HDF5 cache: {ctx.hdf5_path}")
            ctx.aligned_frames = []
            ctx.frames = []
            ctx.data_source = ctx.hdf5_path
            ctx.needs_alignment = False
            return ctx

        config = (
            algorithm.load_config(batch_id=ctx.batch_id)
            if hasattr(algorithm, "load_config")
            else {}
        )
        print(
            f"[MFDenoiser][FeatureMatching] start algorithm={algorithm.NAME} "
            f"hdf5_path={ctx.hdf5_path}"
        )

        reference = self._load_single_frame(ctx, ctx.image_paths[0])
        if reference is None:
            print("[MFDenoiser][FeatureMatching] failed to load reference frame.")
            ctx.aligned_frames = []
            return ctx

        resize_res = resize_all_with_padding(
            [reference],
            method="preserve",
            stop_requested=ctx.stop_requested,
            force_even=True,
        )
        if resize_res and resize_res[0]:
            reference = resize_res[0][0]

        ctx.reference_image = reference
        ctx.ref_dtype = reference.dtype
        ctx.ref_h, ctx.ref_w = reference.shape[:2]
        target_dims = (ctx.ref_h, ctx.ref_w)

        _progress(ctx.update_progress, 25, f"Planning feature matching: {algorithm.NAME}")
        motion_plan = algorithm.build_motion_plan(
            ctx,
            reference,
            target_dims,
            self,
            config,
        )
        ctx.motion_plan = motion_plan
        motion_by_index = {item["index"]: item for item in motion_plan}

        crop_bounds = None
        global_crop = bool(config.get("enable_cropping", False)) and not bool(
            config.get("keep_edges", False)
        )
        if global_crop:
            crop_bounds = compute_global_crop_bounds(
                motion_plan[1:],
                reference.shape[1],
                reference.shape[0],
                config,
            )
            if crop_bounds is None:
                print("[MFDenoiser][FeatureMatching] global crop unavailable, using non-crop.")
                global_crop = False

        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)
        if os.path.exists(ctx.hdf5_path):
            os.remove(ctx.hdf5_path)

        saved_count = 0
        with h5py.File(ctx.hdf5_path, "w") as h5f:
            h5f.attrs["ref_image_path"] = ctx.image_paths[0]
            h5f.attrs["alignment_algorithm"] = algorithm.NAME
            h5f.attrs["alignment_process"] = "feature_matching"
            h5f.attrs["global_crop"] = bool(global_crop)

            for index, path in enumerate(ctx.image_paths):
                if ctx.stop_requested and ctx.stop_requested():
                    print("[MFDenoiser][FeatureMatching] stopped by user.")
                    break

                if index == 0:
                    aligned = (
                        crop_image(reference, crop_bounds)
                        if global_crop
                        else np.array(reference, copy=True)
                    )
                else:
                    frame = self._load_single_frame(ctx, path, target_dims=target_dims)
                    if frame is None:
                        print(f"[MFDenoiser][FeatureMatching] failed to load image_{index}: {path}")
                        continue
                    motion_item = motion_by_index.get(index)
                    aligned = (
                        apply_global_crop(frame, motion_item, crop_bounds, config)
                        if global_crop
                        else apply_non_crop(frame, motion_item, config)
                    )
                    del frame

                if aligned is None:
                    print(f"[MFDenoiser][FeatureMatching] skipped image_{index}: no aligned output")
                    continue

                save_to_hdf5(h5f, f"image_{index}", aligned, extract_exif(path))
                h5f.flush()
                saved_count += 1
                print(
                    f"[MFDenoiser][FeatureMatching] saved image_{index} "
                    f"{_frame_info(aligned)}"
                )
                del aligned
                gc.collect()

                progress = 55 + int(((index + 1) / max(1, ctx.total_images)) * 35)
                _progress(
                    ctx.update_progress,
                    progress,
                    f"Applied feature matching {index + 1}/{ctx.total_images}",
                )

        ctx.aligned_frames = []
        ctx.frames = []
        ctx.data_source = ctx.hdf5_path
        ctx.needs_alignment = False
        print(
            f"[MFDenoiser][FeatureMatching] finished saved={saved_count} "
            f"hdf5_path={ctx.hdf5_path}"
        )
        del reference
        gc.collect()
        return ctx

    def align_process(self, ctx, batch_plan=None):
        """Alignment stage placeholder.

        Future intended structure:
        1. optional feature matching for pre-global warp,
        2. optional optical flow refinement,
        3. optional persistence of aligned frames to cache/HDF5.

        For now this stage deliberately performs no alignment.
        """
        alignment_name = ctx.params.get("alignment_plan", "No Alignment")
        registry = get_alignment_registry()
        algorithm = _resolve_algorithm(registry, alignment_name, "No Alignment")
        print(
            f"[MFDenoiser][Align] selected={alignment_name} resolved={algorithm.NAME} "
            f"input_frames={len(ctx.frames)} batch_plan={batch_plan}"
        )
        _progress(ctx.update_progress, 25, f"Running alignment: {algorithm.NAME}")
        if ctx.cache_is_valid:
            # Cache loading will be wired here when real alignment persistence exists.
            print("[MFDenoiser] Cache is valid, but cache loading is still a placeholder.")
        if hasattr(algorithm, "build_flow_alignment"):
            reference = self._load_single_frame(ctx, ctx.image_paths[0])
            if reference is None:
                ctx.aligned_frames = []
                return ctx
            resize_res = resize_all_with_padding(
                [reference],
                method="preserve",
                stop_requested=ctx.stop_requested,
                force_even=True,
            )
            if resize_res and resize_res[0]:
                resized_reference = resize_res[0][0]
                if ctx.clear_raw or ctx.params.get("clear_raw", True):
                    del reference
                    gc.collect()
                reference = resized_reference
            ctx.reference_image = reference
            ctx.ref_dtype = reference.dtype
            ctx.ref_h, ctx.ref_w = reference.shape[:2]
            config = (
                algorithm.load_config(batch_id=ctx.batch_id)
                if hasattr(algorithm, "load_config")
                else {}
            )
            result_ctx = algorithm.build_flow_alignment(
                ctx,
                reference,
                (ctx.ref_h, ctx.ref_w),
                self,
                config,
            )
            if result_ctx.clear_raw or result_ctx.params.get("clear_raw", True):
                result_ctx.frames = []
                result_ctx.aligned_frames = []
                gc.collect()
            return result_ctx
        feature_result = self.feature_matching_process(ctx, algorithm, batch_plan=batch_plan)
        if feature_result is not None:
            return feature_result
        ctx.aligned_frames = algorithm.run(ctx, ctx.frames, batch_plan=batch_plan)
        print(f"[MFDenoiser][Align] output_frames={len(ctx.aligned_frames)}")
        for idx, frame in enumerate(ctx.aligned_frames):
            print(f"[MFDenoiser][Align] aligned_frame_{idx}: {_frame_info(frame)}")
        ctx.needs_alignment = False
        return ctx

    def _merge_average_from_hdf5(self, ctx):
        alignment_name = _normalize_algorithm_name(ctx.params.get("alignment_plan", "No Alignment"))
        if alignment_name == "no alignment":
            return False
        if not ctx.hdf5_path or not os.path.exists(ctx.hdf5_path):
            return False
        print(f"[MFDenoiser][Merge] Average streaming aligned HDF5: {ctx.hdf5_path}")
        sum_image = None
        count = 0
        with h5py.File(ctx.hdf5_path, "r") as h5f:
            image_keys = sorted(
                [key for key in h5f.keys() if key.startswith("image_")],
                key=lambda item: int(item.split("_", 1)[1]),
            )
            for idx, key in enumerate(image_keys):
                if ctx.stop_requested and ctx.stop_requested():
                    break
                frame = h5f[key][...]
                print(f"[MFDenoiser][Merge] hdf5_{key}: {_frame_info(frame)}")
                sum_image, count = self._average_accumulate(sum_image, count, frame)
                del frame
                gc.collect()
                _progress(
                    ctx.update_progress,
                    60 + int(((idx + 1) / max(1, len(image_keys))) * 30),
                    f"Merging aligned frame {idx + 1}/{len(image_keys)}",
                )
        ctx.result_image = self._average_finalize(ctx, sum_image, count)
        print(f"[MFDenoiser][Merge] Average HDF5 count={count} result={_frame_info(ctx.result_image)}")
        del sum_image
        gc.collect()
        return True

    def _merge_average_from_paths(self, ctx, batch_plan=None):
        alignment_name = _normalize_algorithm_name(ctx.params.get("alignment_plan", "No Alignment"))
        if alignment_name != "no alignment":
            return False
        if not ctx.image_paths:
            return False
        print(
            f"[MFDenoiser][Merge] Average streaming paths: "
            f"frames={len(ctx.image_paths)} batch_plan={batch_plan}"
        )
        sum_image = None
        count = 0
        target_dims = None
        for idx, path in enumerate(ctx.image_paths):
            if ctx.stop_requested and ctx.stop_requested():
                break
            frame = self._load_single_frame(ctx, path, target_dims=target_dims)
            if frame is None:
                continue
            if target_dims is None:
                target_dims = frame.shape[:2]
                ctx.reference_image = frame
                ctx.ref_dtype = frame.dtype
                ctx.ref_h, ctx.ref_w = frame.shape[:2]
            print(f"[MFDenoiser][Merge] average_path_{idx}: {_frame_info(frame)}")
            sum_image, count = self._average_accumulate(sum_image, count, frame)
            if idx > 0 or ctx.reference_image is not frame:
                del frame
            gc.collect()
            _progress(
                ctx.update_progress,
                60 + int(((idx + 1) / max(1, len(ctx.image_paths))) * 30),
                f"Merging frame {idx + 1}/{len(ctx.image_paths)}",
            )
        ctx.result_image = self._average_finalize(ctx, sum_image, count)
        print(f"[MFDenoiser][Merge] Average path count={count} result={_frame_info(ctx.result_image)}")
        del sum_image
        gc.collect()
        return True

    def merge_process(self, ctx, batch_plan=None):
        """Merge stage placeholder.

        Future intended structure:
        - full-frame merge path,
        - tile merge path with flexible tile size/overlap,
        - optional streaming/batching for memory control.

        For now this stage returns the reference frame unchanged.
        """
        denoising_name = ctx.params.get("merge_plan", "No Denoising")
        registry = get_denoising_registry()
        algorithm = _resolve_algorithm(registry, denoising_name, "No Denoising")
        print(
            f"[MFDenoiser][Merge] selected={denoising_name} resolved={algorithm.NAME} "
            f"input_frames={len(ctx.aligned_frames or ctx.frames)} batch_plan={batch_plan}"
        )
        _progress(ctx.update_progress, 60, f"Running denoising: {algorithm.NAME}")
        if algorithm.NAME == "Average" and self._merge_average_from_hdf5(ctx):
            return ctx
        if algorithm.NAME == "Average" and self._merge_average_from_paths(ctx, batch_plan=batch_plan):
            return ctx
        frames = ctx.aligned_frames or ctx.frames
        ctx.result_image = algorithm.run(ctx, frames, batch_plan=batch_plan)
        print(f"[MFDenoiser][Merge] result={_frame_info(ctx.result_image)}")
        return ctx

    def save_process(self, ctx):
        """Save the current pipeline result."""
        if ctx.result_image is None:
            print("[MFDenoiser][Save] No result image to save.")
            return None

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
        print(f"[MFDenoiser][Save] output_path={output_path} result={_frame_info(ctx.result_image)}")

        if ctx.is_linear_mode:
            return save_linear_dng(
                ctx.result_image,
                os.path.splitext(output_path)[0] + ".dng",
                reference_image_path=ctx.image_paths[0] if ctx.image_paths else None,
            )

        save_image(
            ctx.result_image,
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
        processing_mode=None,
        tile_size=None,
        tile_overlap=None,
        alignment_backend=None,
        clear_raw=None,
    ):
        """Main orchestration entry point for MFDenoiser."""
        ctx = PipelineContext(
            db_path=self.db_path,
            single_process=single_process,
            batch_id=batch_id,
            update_progress=update_progress,
            stop_requested=stop_requested,
        )
        ctx.params = self._load_params()
        if merging_mode is not None:
            ctx.params["merge_plan"] = merging_mode
        if output_suffix is not None:
            ctx.params["output_suffix"] = output_suffix
        if processing_mode is not None:
            ctx.params["processing_mode"] = processing_mode
        if tile_size is not None:
            ctx.params["tile_size"] = int(tile_size)
        if tile_overlap is not None:
            ctx.params["tile_overlap"] = float(tile_overlap)
        if alignment_backend is not None:
            ctx.params["alignment_plan"] = alignment_backend
        if clear_raw is not None:
            ctx.params["clear_raw"] = bool(clear_raw)
        ctx.clear_raw = bool(ctx.params.get("clear_raw", True))
        print(
            f"[MFDenoiser][Pipeline] start single_process={single_process} batch_id={batch_id} "
            f"alignment={ctx.params.get('alignment_plan')} denoising={ctx.params.get('merge_plan')} "
            f"output_suffix={ctx.params.get('output_suffix')}"
        )

        alignment_name_for_load = ctx.params.get("alignment_plan", "No Alignment")
        alignment_algo_for_load = _resolve_algorithm(
            get_alignment_registry(),
            alignment_name_for_load,
            "No Alignment",
        )
        if (
            hasattr(alignment_algo_for_load, "build_motion_plan")
            or self._can_stream_load_for_merge(ctx, alignment_algo_for_load)
        ):
            ctx = self.prepare_input_paths(ctx)
        else:
            ctx = self.load_process(ctx)
        if not ctx.total_images:
            _progress(
                update_progress,
                100,
                getattr(
                    _lang(), "NO_IMAGE_PATH_PROCESSED_IMAGE", "No image to process."
                ),
            )
            return None
        if stop_requested and stop_requested():
            return None

        ctx = self.prepare_alignment_cache_policy(ctx)
        batch_plan = self.build_batch_plan(ctx)

        # run_pipeline owns the high-level policy. Later, cache/HDF5 can be
        # enabled here and delegated to align_process helpers.
        ctx = self.align_process(ctx, batch_plan=batch_plan)
        if stop_requested and stop_requested():
            return None

        ctx = self.merge_process(ctx, batch_plan=batch_plan)
        if stop_requested and stop_requested():
            return None

        _progress(update_progress, 95, "Saving MFDenoiser result...")
        output_path = self.save_process(ctx)
        print(f"[MFDenoiser][Pipeline] finished output_path={output_path}")
        _progress(update_progress, 100, "MFDenoiser pipeline skeleton finished.")
        return output_path


def _run_pipeline_entry(
    db_path,
    update_progress=None,
    stop_requested=None,
    single_process=None,
    batch_id=None,
    merging_mode=None,
    output_suffix=None,
    processing_mode=None,
    tile_size=None,
    tile_overlap=None,
    alignment_backend=None,
    clear_raw=None,
):
    processor = MFDenoiserAlgorithm(db_path)
    return processor.run_pipeline(
        single_process=True if single_process is None else single_process,
        batch_id=batch_id,
        update_progress=update_progress,
        stop_requested=stop_requested,
        merging_mode=merging_mode,
        output_suffix=output_suffix,
        processing_mode=processing_mode,
        tile_size=tile_size,
        tile_overlap=tile_overlap,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )


def running_mf_denoiser(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    merging_mode=None,
    output_suffix=None,
    processing_mode=None,
    tile_size=None,
    tile_overlap=None,
    alignment_backend=None,
    clear_raw=None,
):
    db_path = "pixel_refine_database.db"

    if batch_id is not None and progress_callback is not None:
        return _run_pipeline_entry(
            db_path,
            update_progress=progress_callback,
            stop_requested=stop_callback,
            single_process=False,
            batch_id=batch_id,
            merging_mode=merging_mode,
            output_suffix=output_suffix,
            processing_mode=processing_mode,
            tile_size=tile_size,
            tile_overlap=tile_overlap,
            alignment_backend=alignment_backend,
            clear_raw=clear_raw,
        )

    dialog = QDialog(parent)
    dialog.setWindowTitle("MFDenoiser")
    dialog.setWindowModality(Qt.WindowModal)
    layout = QVBoxLayout(dialog)
    label = QLabel("Processing MFDenoiser...")
    progress = QProgressBar()
    progress.setRange(0, 100)
    progress.setStyleSheet(PROGRESS_BAR)
    layout.addWidget(label)
    layout.addWidget(progress)

    def update_progress(percent, message=""):
        progress.setValue(int(percent))
        label.setText(str(message))

    worker = BaseAlgorithmWorker(
        _run_pipeline_entry,
        db_path,
        update_progress=update_progress,
        stop_requested=stop_callback,
        single_process=True if single_process is None else single_process,
        batch_id=batch_id,
        merging_mode=merging_mode,
        output_suffix=output_suffix,
        processing_mode=processing_mode,
        tile_size=tile_size,
        tile_overlap=tile_overlap,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )

    def on_finished():
        dialog.accept()
        QMessageBox.information(parent, "MFDenoiser", "Processing finished.")

    def on_error(error):
        dialog.reject()
        QMessageBox.critical(parent, "MFDenoiser Error", str(error))

    worker.finished.connect(on_finished)
    worker.error_occurred.connect(on_error)
    worker.start()
    dialog.exec()
    return worker


def running_similarity(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    merging_mode=None,
    output_suffix=None,
    alignment_backend=None,
    clear_raw=None,
):
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode=merging_mode or "similarity",
        output_suffix=output_suffix or "similarity",
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )


if __name__ == "__main__":
    _run_pipeline_entry("pixel_refine_database.db")
