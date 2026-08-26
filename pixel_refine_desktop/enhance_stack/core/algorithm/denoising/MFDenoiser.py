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
import difflib
import re
from dataclasses import dataclass, field
from typing import Optional

import h5py
import numpy as np
from config import GENERAL_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    cleanup_old_hdf5_files,
    build_alignment_cache_key,
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
    write_alignment_cache_attrs,
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
        print(
            f"[MFDenoiser][Alignment:No Alignment] Passing through {len(frames)} frame(s)."
        )
        for idx, frame in enumerate(frames):
            print(
                f"[MFDenoiser][Alignment:No Alignment] frame_{idx}: {_frame_info(frame)}"
            )
        return list(frames)


class NoDenoisingAlgorithm:
    NAME = "No Denoising"
    KIND = "denoising"
    DESCRIPTION = "Return the reference/aligned first frame unchanged."

    def run(self, ctx, frames, batch_plan=None):
        print(
            f"[MFDenoiser][Denoising:No Denoising] Received {len(frames)} frame(s). Returning frame_0."
        )
        if not frames:
            return None
        print(f"[MFDenoiser][Denoising:No Denoising] frame_0: {_frame_info(frames[0])}")
        return np.array(frames[0], copy=True)


class SimilarityFusionDenoisingAlgorithm:
    NAME = "Similarity Fusion"
    KIND = "denoising"
    DESCRIPTION = "Run the backend-neutral Taichi AOT similarity fusion pipeline."

    def run(self, ctx, frames, batch_plan=None):
        raise RuntimeError(
            "Similarity Fusion must be launched through MFDenoiser.running_similarity."
        )


class FarnebackAliasAlgorithm:
    NAME = "Farneback"
    KIND = "alignment"
    DESCRIPTION = "Dense Farneback optical flow alignment."

    def run(self, ctx, frames, batch_plan=None):
        return get_alignment_registry()["Farneback Optical Flow"].run(
            ctx, frames, batch_plan=batch_plan
        )


class BlockMatchingGPUAliasAlgorithm:
    NAME = "Block Matching GPU"
    KIND = "alignment"
    DESCRIPTION = "Tile-based GPU block matching optical flow alignment."

    def run(self, ctx, frames, batch_plan=None):
        return get_alignment_registry()["Block Matching GPU Optical Flow"].run(
            ctx, frames, batch_plan=batch_plan
        )


class RAFTAliasAlgorithm:
    NAME = "RAFT"
    KIND = "alignment"
    DESCRIPTION = "ONNX RAFT optical flow alignment."

    def run(self, ctx, frames, batch_plan=None):
        return get_alignment_registry()["RAFT Optical Flow"].run(
            ctx, frames, batch_plan=batch_plan
        )


class LucasKanadeAliasAlgorithm:
    NAME = "Lucas Kanade"
    KIND = "alignment"
    DESCRIPTION = "Lucas Kanade optical flow alignment with switchable CPU/GPU backend."

    NAME = "Lucas Kanade"
    KIND = "alignment"
    DESCRIPTION = "Lucas Kanade optical flow alignment with switchable CPU/GPU backend."

    def _resolve_delegate(self, batch_id=None):
        try:
            config = get_alignment_registry()["Lucas Kanade Optical Flow"].load_config(
                batch_id=batch_id
            )
            backend = str(config.get("backend", "cpu")).strip().lower()
        except Exception as exc:
            print(f"[LucasKanadeAlias] Failed to load backend config: {exc}")
            backend = "cpu"

        registry = get_alignment_registry()
        if backend == "gpu":
            return registry["Lucas Kanade GPU Optical Flow"]
        return registry["Lucas Kanade Optical Flow"]

    def run(self, ctx, frames, batch_plan=None):
        return self._resolve_delegate(batch_id=getattr(ctx, "batch_id", None)).run(
            ctx, frames, batch_plan=batch_plan
        )


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
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching_gpu import (
        BlockMatchingGPU,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.raft_flow import (
        RAFTFlow,
    )

    algorithms = [
        NoAlignmentAlgorithm(),
        ORBAlgorithm(),
        AKAZEAlgorithm(),
        LightGlueAlgorithm(),
        FarnebackFlowCPU(),
        LucasKanadeCPU(),
        LucasKanadeGPU(),
        BlockMatchingGPU(),
        RAFTFlow(),
        FarnebackAliasAlgorithm(),
        LucasKanadeAliasAlgorithm(),
        BlockMatchingGPUAliasAlgorithm(),
        RAFTAliasAlgorithm(),
    ]
    return {algo.NAME: algo for algo in algorithms}


def get_denoising_registry():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
        AverageDenoisingAlgorithm,
        merge_average_from_hdf5,
        merge_average_from_paths,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.SpatiaFusion import (
        SpatialFusionDenoisingAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.weightnet import (
        FusionNetDenoisingAlgorithm,
    )

    algorithms = [
        NoDenoisingAlgorithm(),
        AverageDenoisingAlgorithm(),
        SpatialFusionDenoisingAlgorithm(),
        FusionNetDenoisingAlgorithm(),
    ]
    return {algo.NAME: algo for algo in algorithms}


def get_available_algorithms(category):
    if category == "alignment":
        return get_alignment_registry()
    if category == "denoising":
        return get_denoising_registry()
    return {}


def get_algorithm_options(category):
    if category == "alignment":
        descriptions = {
            name: getattr(algo, "DESCRIPTION", name)
            for name, algo in get_available_algorithms(category).items()
        }
        ordered_names = [
            "No Alignment",
            "ORB",
            "AKAZE",
            "Light Glue",
            "Farneback",
            "Lucas Kanade",
            "Block Matching GPU",
            "RAFT",
        ]
        return [(name, descriptions.get(name, name)) for name in ordered_names]

    return [
        (name, getattr(algo, "DESCRIPTION", name))
        for name, algo in get_available_algorithms(category).items()
    ]


def get_algorithm_names(category):
    if category == "alignment":
        return [
            "No Alignment",
            "ORB",
            "AKAZE",
            "Light Glue",
            "Farneback",
            "Lucas Kanade",
            "Block Matching GPU",
            "RAFT",
        ]
    return list(get_available_algorithms(category).keys())


def _normalize_algorithm_name(name):
    return str(name or "").strip().casefold()


def _canonical_algorithm_key(name):
    value = _normalize_algorithm_name(name)
    value = value.replace("_", " ").replace("-", " ")
    value = re.sub(r"\s+", " ", value).strip()
    replacements = {
        "optical flow": "",
        "gpu optical flow": "gpu",
        "cpu optical flow": "cpu",
        "block matching gpu": "block matching gpu",
        "lightglue": "light glue",
        "light glue": "light glue",
        "lucaskanade": "lucas kanade",
        "lucas kanade gpu": "lucas kanade gpu",
        "lucas kanade cpu": "lucas kanade cpu",
        "noalignment": "no alignment",
    }
    for src, dst in replacements.items():
        value = value.replace(src, dst)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace("balance mode", "medium")
    value = value.replace("balanced", "medium")
    return value


def _build_algorithm_alias_map(registry):
    alias_map = {}
    explicit_aliases = {
        "farneback optical flow": "Farneback Optical Flow",
        "farneback": "Farneback",
        "lucas kanade optical flow": "Lucas Kanade Optical Flow",
        "lucas kanade gpu optical flow": "Lucas Kanade GPU Optical Flow",
        "lucas kanade": "Lucas Kanade",
        "lucas kanade gpu": "Lucas Kanade GPU Optical Flow",
        "lucas kanade cpu": "Lucas Kanade Optical Flow",
        "block matching gpu optical flow": "Block Matching GPU Optical Flow",
        "block matching gpu": "Block Matching GPU",
        "blockmatchinggpu": "Block Matching GPU",
        "raft optical flow": "RAFT Optical Flow",
        "raft": "RAFT",
        "lightglue": "Light Glue",
        "light glue": "Light Glue",
        "akaze": "AKAZE",
        "orb": "ORB",
        "no alignment": "No Alignment",
        "noalignment": "No Alignment",
        "none": "No Denoising",
        "no denoising": "No Denoising",
        "average": "Average",
        "similarity": "Similarity",
        "fusionnet": "FusionNet",
        "weightnet": "FusionNet",
        "spatial ai": "FusionNet",
    }
    for alias, target in explicit_aliases.items():
        if target in registry:
            alias_map[_canonical_algorithm_key(alias)] = target

    for name in registry.keys():
        alias_map[_canonical_algorithm_key(name)] = name
        alias_map[_normalize_algorithm_name(name)] = name
    return alias_map


def _resolve_algorithm(registry, requested_name, fallback_name):
    if requested_name in registry:
        return registry[requested_name]

    normalized = _normalize_algorithm_name(requested_name)
    for name, algorithm in registry.items():
        if _normalize_algorithm_name(name) == normalized:
            return algorithm

    alias_map = _build_algorithm_alias_map(registry)
    canonical_requested = _canonical_algorithm_key(requested_name)
    alias_target = alias_map.get(canonical_requested)
    if alias_target and alias_target in registry:
        print(
            f"[MFDenoiser][Registry] Alias-resolved '{requested_name}' -> '{alias_target}'"
        )
        return registry[alias_target]

    choices = list(alias_map.keys())
    fuzzy_match = difflib.get_close_matches(
        canonical_requested, choices, n=1, cutoff=0.72
    )
    if fuzzy_match:
        alias_target = alias_map.get(fuzzy_match[0])
        if alias_target and alias_target in registry:
            print(
                f"[MFDenoiser][Registry] Fuzzy-resolved '{requested_name}' -> "
                f"'{alias_target}' via '{fuzzy_match[0]}'"
            )
            return registry[alias_target]

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
    alignment_cache_key: str = ""
    alignment_cache_payload: str = ""
    alignment_selection_name: str = "No Alignment"
    alignment_effective_name: str = "No Alignment"
    alignment_runtime_snapshot: dict = field(default_factory=dict)
    compute_runtime: dict = field(default_factory=dict)
    # Alignment orchestration state.  The reference belongs to the pipeline,
    # while comparison frames belong to a short-lived AlignmentBatchJob.
    alignment_reference: Optional[np.ndarray] = None
    alignment_reference_ready: bool = False
    alignment_batch_size: int = 0
    alignment_batches_processed: int = 0
    alignment_prefetch_active: bool = False
    alignment_prefetch_start: int = -1
    alignment_prefetch_end: int = -1
    alignment_prefetch_frames: dict = field(default_factory=dict)


@dataclass
class AlignmentBatchJob:
    """A bounded alignment workload owned by :class:`MFDenoiserAlgorithm`.

    Alignment implementations receive this job as data only.  They must not
    open/close HDF5, load paths, or retain the comparison frames after the job
    returns.  ``reference`` is deliberately separate and owned by the parent
    pipeline so it can remain stable across all jobs.
    """

    start_index: int
    end_index: int
    paths: list = field(default_factory=list)
    frames: list = field(default_factory=list)
    reference: Optional[np.ndarray] = None
    target_dims: tuple = (0, 0)
    config: dict = field(default_factory=dict)

    @property
    def size(self):
        return max(0, self.end_index - self.start_index)


class MFDenoiserAlgorithm:
    """Main orchestrator for future multi-frame denoising modes."""

    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
        if not self.db_path:
            raise RuntimeError(
                "A session database is required. Set PIXEL_REFINE_SESSION_DB "
                "or pass db_path explicitly."
            )

    @staticmethod
    def _configure_compute_runtime(ctx, frame_shape=None):
        """Connect this pipeline to the shared adaptive block/VRAM runtime."""
        # Keep full-frame for backends with sufficient residency, but do not
        # force a 12--50 MP OpenGL/GLES graph beyond its admission budget.
        # The decision is runtime-derived and remains below the public API;
        # unsupported individual graphs still use their same-backend
        # full-frame path rather than silently switching to CPU.
        mode = "full_frame"
        block_enabled = False
        ctx.params["processing_mode"] = mode
        import config as app_config

        block_settings = app_config.get_compute_block_settings()

        # The UI tile size controls denoising neighbourhoods; it must not
        # silently redefine the resident compute-block size used by all AOT
        # stages.  Use the shared application policy instead.
        block_size = int(block_settings.get("block_size", 1024))
        block_size = max(64, block_size)
        block_size = max(64, (block_size // 16) * 16)

        try:
            from taichi_vision import taichi_aot

            engine = taichi_aot.get_engine()
            backend = str(getattr(engine, "arch", "")).strip().lower()
            memory = taichi_aot.get_memory_status(force=True)
            pipeline_limit = int(memory.get("pipeline_resident_limit", 0) or 0)
            pressure = str(memory.get("pressure", "healthy")).lower()
            policy = (
                os.environ.get(
                    "PIXEL_REFINE_MFDENOISER_BLOCK",
                    block_settings.get("mode", "block"),
                )
                .strip()
                .lower()
            )
            if policy in {"1", "true", "on", "block", "always", "tile", "tiled"}:
                block_enabled = bool(block_settings.get("enabled", True))
            elif policy in {"0", "false", "off", "full", "frame", "full_frame"}:
                block_enabled = False
            elif frame_shape is not None:
                frame_mp = (int(frame_shape[0]) * int(frame_shape[1])) / 1_000_000.0
                block_enabled = bool(block_settings.get("enabled", True)) and (
                    frame_mp > float(block_settings.get("threshold_mp", 12.0))
                )
            else:
                # OpenGL/GLES desktop paths do not expose a reliable device
                # heap budget.  Use bounded tiles whenever the resident limit
                # is below the measured 768 MiB safe full-frame floor or the
                # governor reports pressure; CUDA/Vulkan remain full-frame by
                # default when their graph fits.
                block_enabled = backend in {"opengl", "gles"} and (
                    pressure != "healthy"
                    or (pipeline_limit > 0 and pipeline_limit < 768 * 1024**2)
                )
            mode = "block" if block_enabled else "full_frame"
            ctx.params["processing_mode"] = mode
            print(
                f"[MFDenoiser][Compute] mode={mode} backend={backend} "
                f"pressure={pressure} pipeline_limit={pipeline_limit // (1024 * 1024)}MB"
            )

            current = taichi_aot.get_block_config()
            host_cache_limit = (
                current.cache_bytes
                if current.cache_bytes is not None
                else 512 * 1024 * 1024
            )
            config = taichi_aot.set_block_mode(
                enabled=block_enabled,
                size=block_size,
                threshold_bytes=0 if block_enabled else current.threshold_bytes,
                cache_entries=max(2048, current.cache_entries),
                cache_bytes=host_cache_limit,
                adaptive_memory=True,
                device_cache_enabled=block_enabled,
                device_cache_bytes=current.device_cache_bytes,
            )
            memory = taichi_aot.get_memory_status(force=True)
            ctx.compute_runtime = {
                "available": True,
                "block_enabled": config.enabled,
                "block_size": config.normalized_size(),
                "host_cache_bytes": memory["host_cache_budget"],
                "device_cache_bytes": (
                    config.device_cache_bytes if config.device_cache_enabled else 0
                ),
                "pressure": memory["pressure"],
            }
            print(f"[MFDenoiser][Compute] native runtime={ctx.compute_runtime}")
        except Exception as exc:
            ctx.compute_runtime = {
                "available": False,
                "block_enabled": False,
                "reason": str(exc),
            }
            print(
                "[MFDenoiser][Compute] Native block runtime unavailable; "
                f"continuing with legacy execution: {exc}"
            )
        return ctx.compute_runtime

    @staticmethod
    def _report_compute_runtime(ctx):
        if not ctx.compute_runtime.get("available"):
            return
        try:
            from taichi_vision import taichi_aot

            stats = taichi_aot.get_block_cache_stats()
            device = stats.get("device", {})
            print(
                "[MFDenoiser][Compute] cache "
                f"ram_hits={stats.get('hits', 0)} "
                f"vram_hits={device.get('hits', 0)} "
                f"vram_entries={device.get('entries', 0)} "
                f"vram_bytes={device.get('size_bytes', 0)}"
            )
        except Exception as exc:
            print(f"[MFDenoiser][Compute] telemetry unavailable: {exc}")

    def _build_fallback_alignment_snapshot(self, ctx):
        requested_name = str(
            ctx.params.get("alignment_plan", "No Alignment") or "No Alignment"
        )
        return {
            "batch_id": ctx.batch_id,
            "alignment_algo": requested_name,
            "alignment_active": requested_name not in ("", "None", "No Alignment"),
            "reference_path": "",
            "params_key": "",
            "params": {},
            "raw_batch_entry": {},
        }

    def _build_alignment_cache_metadata(self, ctx):
        from pixel_refine_desktop.enhance_stack.core.logic import (
            batch_parameter_manager,
        )

        snapshot = batch_parameter_manager.get_batch_alignment_runtime_snapshot(
            ctx.batch_id
        )
        runtime_requested_name = str(
            ctx.params.get("alignment_plan", "No Alignment") or "No Alignment"
        )
        runtime_alignment_active = runtime_requested_name not in (
            "",
            "None",
            "No Alignment",
        )

        if not snapshot:
            snapshot = self._build_fallback_alignment_snapshot(ctx)
        elif runtime_alignment_active and str(
            snapshot.get("alignment_algo", "No Alignment")
        ) in (
            "",
            "None",
            "No Alignment",
        ):
            print(
                f"[MFDenoiser][CacheMeta] Batch snapshot reported "
                f"'{snapshot.get('alignment_algo')}', overriding with runtime "
                f"alignment '{runtime_requested_name}'."
            )
            snapshot = {
                **snapshot,
                **self._build_fallback_alignment_snapshot(ctx),
                "raw_batch_entry": snapshot.get("raw_batch_entry", {}),
                "reference_path": snapshot.get("reference_path", ""),
            }
        ctx.alignment_runtime_snapshot = snapshot

        requested_name = str(
            runtime_requested_name
            if runtime_alignment_active
            else (
                snapshot.get("alignment_algo")
                or ctx.params.get("alignment_plan", "No Alignment")
            )
            or "No Alignment"
        )
        registry = get_alignment_registry()
        effective_name = requested_name
        config = {}

        if requested_name == "Lucas Kanade":
            cpu_algorithm = registry["Lucas Kanade Optical Flow"]
            snapshot_params = dict(snapshot.get("params", {}) or {})
            gpu_snapshot_params = dict(snapshot_params.pop("gpu_params", {}) or {})
            cpu_config = dict(cpu_algorithm.load_config(batch_id=ctx.batch_id))
            cpu_config.update(snapshot_params)
            backend = str(cpu_config.get("backend", "cpu")).strip().lower()
            if backend == "gpu":
                effective_algorithm = registry["Lucas Kanade GPU Optical Flow"]
                config = effective_algorithm.load_config(batch_id=ctx.batch_id)
                config = dict(config)
                config["backend"] = "gpu"
                config.update(gpu_snapshot_params)
            else:
                effective_algorithm = registry["Lucas Kanade Optical Flow"]
                config = effective_algorithm.load_config(batch_id=ctx.batch_id)
                config = dict(config)
                config["backend"] = "cpu"
            effective_name = effective_algorithm.NAME
            config.update(snapshot_params)
        elif requested_name == "Farneback":
            effective_algorithm = registry["Farneback Optical Flow"]
            effective_name = effective_algorithm.NAME
            config = effective_algorithm.load_config(batch_id=ctx.batch_id)
            config = dict(config)
            config.update(snapshot.get("params", {}))
        elif requested_name == "Block Matching GPU":
            effective_algorithm = registry["Block Matching GPU Optical Flow"]
            effective_name = effective_algorithm.NAME
            config = effective_algorithm.load_config(batch_id=ctx.batch_id)
            config = dict(config)
            config.update(snapshot.get("params", {}))
        elif requested_name == "RAFT":
            effective_algorithm = registry["RAFT Optical Flow"]
            effective_name = effective_algorithm.NAME
            config = effective_algorithm.load_config(batch_id=ctx.batch_id)
            config = dict(config)
            config.update(snapshot.get("params", {}))
        else:
            effective_algorithm = _resolve_algorithm(
                registry, requested_name, "No Alignment"
            )
            effective_name = effective_algorithm.NAME
            if hasattr(effective_algorithm, "load_config"):
                try:
                    config = effective_algorithm.load_config(batch_id=ctx.batch_id)
                except TypeError:
                    config = effective_algorithm.load_config()
                config = dict(config or {})
                config.update(snapshot.get("params", {}))

        cache_key, cache_payload = build_alignment_cache_key(requested_name, config)
        ctx.alignment_selection_name = requested_name
        ctx.alignment_effective_name = effective_name
        ctx.alignment_cache_key = cache_key
        ctx.alignment_cache_payload = cache_payload
        print(
            f"[MFDenoiser][CacheMeta] selection={requested_name} "
            f"effective={effective_name} key={cache_key} batch_id={ctx.batch_id}"
        )
        return ctx

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
            "batch_size": int(
                config.get(
                    "mfdenoiser_batch_size",
                    config.get("ai_batch_size", 15),
                )
            ),
            "h5_write_batch_size": int(config.get("mfdenoiser_h5_write_batch_size", 4)),
            "use_alignment_cache": bool(
                config.get("mfdenoiser_use_alignment_cache", False)
            ),
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
        if not ctx.image_paths:
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
        """Create comparison-frame batches; reference frame is kept separate."""
        batch_size = max(1, int(ctx.params.get("batch_size", 6)))
        comparison_paths = ctx.image_paths[1:]
        comparison_plan = setup_balanced_batching(
            comparison_paths,
            _lang(),
            max_batch_size=batch_size,
        )
        # The batching helper works on a zero-based comparison list. Convert
        # its ranges back to the global image-path indices while reserving
        # index 0 exclusively for the persistent reference frame.
        ctx.batch_plan = [(start + 1, end + 1) for start, end in comparison_plan]
        print(f"[MFDenoiser][Batch] batch_size={batch_size} plan={ctx.batch_plan}")
        return ctx.batch_plan

    def _prepare_alignment_reference(self, ctx):
        """Load and normalize the immutable alignment reference once.

        This is intentionally separate from ``_load_single_frame`` so future
        GPU backends can attach a persistent reference pyramid/buffer here,
        without making the alignment algorithms aware of pipeline policy.
        """
        if ctx.alignment_reference_ready and ctx.alignment_reference is not None:
            return ctx.alignment_reference
        if not ctx.image_paths:
            return None

        reference = self._load_single_frame(ctx, ctx.image_paths[0])
        if reference is None:
            return None
        resize_res = resize_all_with_padding(
            [reference],
            method="preserve",
            stop_requested=ctx.stop_requested,
            force_even=True,
        )
        if resize_res and resize_res[0]:
            reference = resize_res[0][0]

        ctx.alignment_reference = reference
        ctx.alignment_reference_ready = True
        ctx.reference_image = reference
        ctx.ref_dtype = reference.dtype
        ctx.ref_h, ctx.ref_w = reference.shape[:2]
        print(
            f"[MFDenoiser][Batch] persistent reference ready "
            f"{_frame_info(reference)}"
        )
        return reference

    def _load_alignment_batch(self, ctx, batch_range):
        """Load one bounded comparison batch, excluding the reference frame."""
        start, end = batch_range
        first_target = max(1, int(start))
        if first_target >= end:
            return AlignmentBatchJob(
                start_index=first_target,
                end_index=first_target,
                reference=ctx.alignment_reference,
                target_dims=(ctx.ref_h, ctx.ref_w),
            )

        paths = ctx.image_paths[first_target:end]
        frames = []
        if paths:
            if getattr(ctx, "use_tonemapped_loading", False):
                frames = [
                    self._load_single_frame_tonemapped(ctx, path)
                    for path in paths
                    if not (ctx.stop_requested and ctx.stop_requested())
                ]
            else:
                load_res = load_images_from_paths(
                    paths,
                    ctx.stop_requested,
                    linear_mode=ctx.is_linear_mode,
                    capture_ref_proxy=False,
                    update_progress=None,
                )
                frames = load_res[0] if isinstance(load_res, tuple) else load_res
            resize_res = resize_all_with_padding(
                frames,
                method="preserve",
                stop_requested=ctx.stop_requested,
                force_even=True,
            )
            if resize_res and resize_res[0]:
                frames = resize_res[0]

        job = AlignmentBatchJob(
            start_index=first_target,
            end_index=end,
            paths=paths,
            frames=frames or [],
            reference=ctx.alignment_reference,
            target_dims=(ctx.ref_h, ctx.ref_w),
        )
        print(
            f"[MFDenoiser][Batch] loaded alignment job "
            f"indices={job.start_index}:{job.end_index} frames={len(job.frames)}"
        )
        return job

    def _begin_alignment_prefetch(self, ctx):
        """Enable bounded prefetch for legacy per-frame alignment APIs."""
        self._prepare_alignment_reference(ctx)
        ctx.alignment_batch_size = max(1, int(ctx.params.get("batch_size", 8)))
        ctx.alignment_prefetch_active = True
        ctx.alignment_prefetch_start = -1
        ctx.alignment_prefetch_end = -1
        ctx.alignment_prefetch_frames.clear()
        ctx.alignment_batches_processed = 0
        print(
            f"[MFDenoiser][Batch] prefetch enabled batch_size="
            f"{ctx.alignment_batch_size} total={ctx.total_images}"
        )
        # Prime the first bounded buffer before the backend starts requesting
        # individual frames. Subsequent batches are swapped in on demand.
        if ctx.batch_plan:
            first_start, _ = ctx.batch_plan[0]
            self._prefetch_frame_for_path(ctx, ctx.image_paths[first_start])

    def _prefetch_frame_for_path(self, ctx, path):
        """Return a preloaded frame, refilling the bounded batch when needed."""
        try:
            index = ctx.image_paths.index(path)
        except ValueError:
            return None
        if index == 0:
            return ctx.alignment_reference

        batch = next(
            (
                (int(batch_start), int(batch_end))
                for batch_start, batch_end in (ctx.batch_plan or [])
                if int(batch_start) <= index < int(batch_end)
            ),
            None,
        )
        if batch is None:
            batch_size = max(1, ctx.alignment_batch_size)
            start = 1 + ((index - 1) // batch_size) * batch_size
            end = min(ctx.total_images, start + batch_size)
        else:
            start, end = batch
            start = max(1, start)
        if not (
            ctx.alignment_prefetch_start <= index < ctx.alignment_prefetch_end
            and path in ctx.alignment_prefetch_frames
        ):
            ctx.alignment_prefetch_frames.clear()
            job = self._load_alignment_batch(ctx, (start, end))
            ctx.alignment_prefetch_start = start
            ctx.alignment_prefetch_end = end
            ctx.alignment_prefetch_frames.update(
                (frame_path, frame) for frame_path, frame in zip(job.paths, job.frames)
            )
            ctx.alignment_batches_processed += 1
            print(
                f"[MFDenoiser][Batch] active batch "
                f"{start}:{end} ({len(ctx.alignment_prefetch_frames)} frames)"
            )
        return ctx.alignment_prefetch_frames.get(path)

    def _end_alignment_prefetch(self, ctx):
        """Release the current comparison batch but retain no alignment state."""
        if ctx.alignment_prefetch_active:
            ctx.alignment_prefetch_frames.clear()
            ctx.alignment_prefetch_active = False
            ctx.alignment_prefetch_start = -1
            ctx.alignment_prefetch_end = -1
            gc.collect()
            print(
                f"[MFDenoiser][Batch] prefetch released "
                f"batches={ctx.alignment_batches_processed}"
            )

    @staticmethod
    def _release_alignment_batch(job):
        """Release comparison-frame ownership without touching the reference."""
        job.frames.clear()
        job.paths.clear()
        gc.collect()

    def _can_stream_load_for_merge(self, ctx, alignment_algorithm):
        """Return True when images can stay as paths until the merge stage."""
        merge_name = _normalize_algorithm_name(
            ctx.params.get("merge_plan", "No Denoising")
        )
        alignment_name = _normalize_algorithm_name(
            getattr(
                alignment_algorithm,
                "NAME",
                ctx.params.get("alignment_plan", "No Alignment"),
            )
        )
        return merge_name == "average" and alignment_name == "no alignment"

    def _is_no_alignment_requested(self, ctx):
        """Return True when the batch explicitly disables alignment."""
        alignment_name = str(
            ctx.params.get("alignment_plan", "No Alignment") or "No Alignment"
        ).strip()
        return alignment_name.casefold() == "no alignment"

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

        if self._is_no_alignment_requested(ctx):
            ctx.use_hdf5_cache = False
            ctx.cache_is_valid = False
            ctx.needs_alignment = False
            print(
                "[MFDenoiser][Cache] alignment disabled by batch parameter; "
                "bypassing HDF5 alignment cache."
            )
            return ctx

        cleanup_old_hdf5_files(ctx.hdf5_path)

        ref_path = ctx.image_paths[0] if ctx.image_paths else ""
        ctx = self._build_alignment_cache_metadata(ctx)
        ctx.cache_is_valid = (
            ctx.use_hdf5_cache
            and bool(ref_path)
            and os.path.exists(ctx.hdf5_path)
            and is_hdf5_cache_valid(
                ctx.hdf5_path,
                ref_path,
                expected_alignment_name=ctx.alignment_selection_name,
                expected_cache_key=ctx.alignment_cache_key,
            )
        )
        ctx.needs_alignment = not ctx.cache_is_valid
        print(
            f"[MFDenoiser][Cache] use={ctx.use_hdf5_cache} valid={ctx.cache_is_valid} "
            f"needs_alignment={ctx.needs_alignment} hdf5_path={ctx.hdf5_path}"
        )
        if ctx.cache_is_valid:
            print(f"[MFDenoiser] Alignment cache valid: {ctx.hdf5_path}")
        elif ctx.use_hdf5_cache:
            print(
                f"[MFDenoiser] Alignment cache will be rebuilt later: {ctx.hdf5_path}"
            )
        return ctx

    def _load_single_frame_tonemapped(self, ctx, path, target_dims=None):
        import rawpy

        try:
            with rawpy.imread(path) as raw:
                rgb_linear = raw.postprocess(
                    demosaic_algorithm=rawpy.DemosaicAlgorithm.DCB,
                    use_camera_wb=True,
                    no_auto_bright=True,
                    gamma=(1, 1),
                    output_bps=16,
                    output_color=rawpy.ColorSpace.raw,
                    user_flip=0,
                )
                img_f32 = rgb_linear.astype(np.float32) / 65535.0
                cmatrix = raw.color_matrix[:, :3].astype(np.float32)
                sRGB = np.matmul(img_f32, cmatrix.T)
                sRGB = sRGB / np.sqrt(1.0 + sRGB * sRGB)
                sRGB = np.clip(sRGB, 0.0, 1.0)
                t = np.sqrt(sRGB)
                gamma_rgb = t * (
                    1.30547177 + t * (-0.78947190 + t * (0.79064221 - 0.30664208 * t))
                )
                gamma_rgb = np.clip(gamma_rgb, 0.0, 1.0)
                rgb = (gamma_rgb * 65535.0).astype(np.uint16)
                bgr = rgb
                if bgr.flags["WRITEABLE"]:
                    b_channel = bgr[:, :, 0].copy()
                    bgr[:, :, 0] = bgr[:, :, 2]
                    bgr[:, :, 2] = b_channel
                frame = bgr
        except Exception as e:
            print(
                f"[MFDenoiser] Custom tone mapping failed for {path}: {e}. Falling back to default loader."
            )
            frame = self._load_single_frame(ctx, path, target_dims=None)

        if target_dims is not None and frame.shape[:2] != tuple(target_dims):
            frame = resize_with_padding(frame, target_dims)
        return frame

    def _load_single_frame(self, ctx, path, target_dims=None):
        if getattr(ctx, "alignment_prefetch_active", False):
            reference_path = ctx.image_paths[0] if ctx.image_paths else None
            if path != reference_path:
                prefetched = self._prefetch_frame_for_path(ctx, path)
                if prefetched is not None:
                    frame = prefetched
                    if target_dims is not None and frame.shape[:2] != tuple(
                        target_dims
                    ):
                        frame = resize_with_padding(frame, target_dims)
                    return frame
        if getattr(ctx, "use_tonemapped_loading", False):
            return self._load_single_frame_tonemapped(
                ctx, path, target_dims=target_dims
            )
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
            print(
                f"[MFDenoiser][FeatureMatching] using valid HDF5 cache: {ctx.hdf5_path}"
            )
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

        # Load reference tone-mapped for keypoint detection calculations
        reference_tonemapped = self._load_single_frame_tonemapped(
            ctx, ctx.image_paths[0], target_dims=target_dims
        )

        _progress(
            ctx.update_progress, 25, f"Planning feature matching: {algorithm.NAME}"
        )
        self._begin_alignment_prefetch(ctx)
        ctx.use_tonemapped_loading = True
        try:
            motion_plan = algorithm.build_motion_plan(
                ctx,
                reference_tonemapped,
                target_dims,
                self,
                config,
            )
        finally:
            ctx.use_tonemapped_loading = False
        # Motion estimation may use a tone-mapped representation.  Rebuild a
        # bounded raw-frame prefetch for the subsequent warp/crop pass.
        self._end_alignment_prefetch(ctx)
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
                print(
                    "[MFDenoiser][FeatureMatching] global crop unavailable, using non-crop."
                )
                global_crop = False

        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)
        if os.path.exists(ctx.hdf5_path):
            os.remove(ctx.hdf5_path)

        saved_count = 0
        self._begin_alignment_prefetch(ctx)
        with h5py.File(ctx.hdf5_path, "w") as h5f:
            write_alignment_cache_attrs(
                h5f,
                ref_image_path=ctx.image_paths[0],
                alignment_selection=ctx.alignment_selection_name,
                alignment_algorithm=ctx.alignment_effective_name or algorithm.NAME,
                alignment_process="feature_matching",
                cache_key=ctx.alignment_cache_key,
                cache_payload=ctx.alignment_cache_payload,
            )
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
                        print(
                            f"[MFDenoiser][FeatureMatching] failed to load image_{index}: {path}"
                        )
                        continue
                    motion_item = motion_by_index.get(index)
                    aligned = (
                        apply_global_crop(frame, motion_item, crop_bounds, config)
                        if global_crop
                        else apply_non_crop(frame, motion_item, config)
                    )
                    del frame

                if aligned is None:
                    print(
                        f"[MFDenoiser][FeatureMatching] skipped image_{index}: no aligned output"
                    )
                    continue

                save_to_hdf5(h5f, f"image_{index}", aligned, extract_exif(path))
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
        self._end_alignment_prefetch(ctx)
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
        effective_alignment_name = (
            getattr(ctx, "alignment_effective_name", "") or alignment_name
        )
        registry = get_alignment_registry()
        algorithm = _resolve_algorithm(
            registry, effective_alignment_name, "No Alignment"
        )
        print(
            f"[MFDenoiser][Align] selected={alignment_name} "
            f"effective={effective_alignment_name} resolved={algorithm.NAME} "
            f"input_frames={len(ctx.frames)} batch_plan={batch_plan}"
        )
        _progress(ctx.update_progress, 25, f"Running alignment: {algorithm.NAME}")
        if self._is_no_alignment_requested(ctx):
            ctx.aligned_frames = list(ctx.frames)
            ctx.data_source = "frames"
            ctx.needs_alignment = False
            print(
                "[MFDenoiser][Align] No Alignment requested; using loaded frames "
                "directly without HDF5."
            )
            return ctx
        if ctx.cache_is_valid:
            print(f"[MFDenoiser][Align] using valid HDF5 cache: {ctx.hdf5_path}")
            ctx.aligned_frames = []
            ctx.frames = []
            ctx.data_source = ctx.hdf5_path
            ctx.needs_alignment = False
            return ctx
        if hasattr(algorithm, "build_flow_alignment"):
            # Dense flow owns large pyramids and accumulators. Drop reusable
            # output tiles from earlier stages so they cannot compete for VRAM.
            try:
                from taichi_vision import taichi_aot

                taichi_aot.engine.sync()
                taichi_aot.engine.get_device_block_cache().clear()
                print("[MFDenoiser][Align] released prior VRAM cache for dense flow")
            except Exception as exc:
                print(f"[MFDenoiser][Align] VRAM cache release skipped: {exc}")
            reference = self._prepare_alignment_reference(ctx)
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
            self._begin_alignment_prefetch(ctx)
            try:
                result_ctx = algorithm.build_flow_alignment(
                    ctx,
                    reference,
                    (ctx.ref_h, ctx.ref_w),
                    self,
                    config,
                )
            finally:
                self._end_alignment_prefetch(ctx)
            if result_ctx.clear_raw or result_ctx.params.get("clear_raw", True):
                result_ctx.frames = []
                result_ctx.aligned_frames = []
                gc.collect()
            return result_ctx
        feature_result = self.feature_matching_process(
            ctx, algorithm, batch_plan=batch_plan
        )
        if feature_result is not None:
            return feature_result
        ctx.aligned_frames = algorithm.run(ctx, ctx.frames, batch_plan=batch_plan)
        print(f"[MFDenoiser][Align] output_frames={len(ctx.aligned_frames)}")
        for idx, frame in enumerate(ctx.aligned_frames):
            print(f"[MFDenoiser][Align] aligned_frame_{idx}: {_frame_info(frame)}")
        ctx.needs_alignment = False
        return ctx

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
        if algorithm.NAME == "Average":
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
                merge_average_from_hdf5,
                merge_average_from_paths,
            )
        if algorithm.NAME == "Average" and merge_average_from_hdf5(
            ctx, progress_callback=ctx.update_progress
        ):
            return ctx
        if algorithm.NAME == "Average" and merge_average_from_paths(
            ctx,
            load_single_frame=self._load_single_frame,
            progress_callback=ctx.update_progress,
            batch_plan=batch_plan,
        ):
            return ctx

        # Alignment backends release their in-memory outputs after writing
        # HDF5. No-Denoising must still produce the persisted reference.
        if algorithm.NAME == "No Denoising":
            if (
                getattr(ctx, "hdf5_path", None)
                and os.path.exists(ctx.hdf5_path)
                and getattr(ctx, "data_source", "") == ctx.hdf5_path
            ):
                with h5py.File(ctx.hdf5_path, "r") as h5f:
                    if "image_0" in h5f:
                        ctx.result_image = np.array(h5f["image_0"])
            elif ctx.reference_image is not None:
                ctx.result_image = np.array(ctx.reference_image, copy=True)
            elif ctx.image_paths:
                ctx.result_image = self._load_single_frame(ctx, ctx.image_paths[0])
            print(
                f"[MFDenoiser][Merge] No Denoising reference="
                f"{_frame_info(ctx.result_image)}"
            )
            return ctx

        frames = ctx.aligned_frames or ctx.frames
        ctx.result_image = algorithm.run(ctx, frames, batch_plan=batch_plan)
        if (
            ctx.result_image is not None
            and algorithm.NAME not in {"FusionNet", "Similarity", "Similarity Fusion"}
        ):
            try:
                from taichi_vision import taichi_aot

                if bool(getattr(ctx, "is_linear_mode", False)):
                    img_f32 = ctx.result_image.astype(np.float32, copy=False)
                    max_v = float(np.max(img_f32)) if img_f32.size > 0 else 1.0
                    if max_v > 1.5:
                        img_f32 = img_f32 / (65535.0 if max_v > 255.0 else 255.0)
                    auto_params = taichi_aot.analyze_auto_enhance_params(img_f32)
                    img_tm = taichi_aot.AutoEnhance(img_f32, params=auto_params)
                    if max_v > 255.0 or ctx.result_image.dtype == np.uint16:
                        ctx.result_image = np.clip(img_tm * 65535.0 + 0.5, 0, 65535).astype(
                            np.uint16
                        )
                    elif max_v > 1.0:
                        ctx.result_image = np.clip(img_tm * 255.0 + 0.5, 0, 255).astype(
                            np.uint8
                        )
                    else:
                        ctx.result_image = np.clip(img_tm * 65535.0 + 0.5, 0, 65535).astype(
                            np.uint16
                        )
            except Exception as e_tm:
                print(f"[MFDenoiser] Tone mapping result image warning: {e_tm}")
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
        print(
            f"[MFDenoiser][Save] output_path={output_path} result={_frame_info(ctx.result_image)}"
        )

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
        batch_size=None,
        h5_write_batch_size=None,
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
        if batch_size is not None:
            ctx.params["batch_size"] = max(1, int(batch_size))
        if h5_write_batch_size is not None:
            ctx.params["h5_write_batch_size"] = max(1, int(h5_write_batch_size))
        if alignment_backend is not None:
            ctx.params["alignment_plan"] = alignment_backend
        if clear_raw is not None:
            ctx.params["clear_raw"] = bool(clear_raw)
        ctx.clear_raw = bool(ctx.params.get("clear_raw", True))
        self._configure_compute_runtime(ctx)
        print(
            f"[MFDenoiser][Pipeline] start single_process={single_process} batch_id={batch_id} "
            f"alignment={ctx.params.get('alignment_plan')} denoising={ctx.params.get('merge_plan')} "
            f"batch_size={ctx.params.get('batch_size')} "
            f"output_suffix={ctx.params.get('output_suffix')}"
        )

        ctx = self.prepare_input_paths(ctx)
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
        alignment_name_for_load = getattr(
            ctx, "alignment_effective_name", ""
        ) or ctx.params.get("alignment_plan", "No Alignment")
        alignment_algo_for_load = _resolve_algorithm(
            get_alignment_registry(),
            alignment_name_for_load,
            "No Alignment",
        )
        if not ctx.cache_is_valid and not (
            hasattr(alignment_algo_for_load, "build_motion_plan")
            or hasattr(alignment_algo_for_load, "build_flow_alignment")
            or self._can_stream_load_for_merge(ctx, alignment_algo_for_load)
        ):
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
            # The MP threshold can be evaluated deterministically after the
            # first decoded frame is available.
            if getattr(ctx, "ref_h", None) and getattr(ctx, "ref_w", None):
                self._configure_compute_runtime(ctx, (ctx.ref_h, ctx.ref_w))
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
        self._report_compute_runtime(ctx)
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
    batch_size=None,
    h5_write_batch_size=None,
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
        batch_size=batch_size,
        h5_write_batch_size=h5_write_batch_size,
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
    batch_size=None,
    h5_write_batch_size=None,
    alignment_backend=None,
    clear_raw=None,
    db_path=None,
):
    # Desktop sessions use a private SQLite database (also when a .prf
    # project is opened). Resolve it from the owning controller or session
    # environment; never fall back to a shared public database.
    if not db_path:
        controller = getattr(parent, "controller", None)
        db_path = getattr(controller, "db_path", None)
    db_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not db_path:
        raise RuntimeError(
            "A session database is required for MFDenoiser. "
            "Set PIXEL_REFINE_SESSION_DB or pass db_path explicitly."
        )

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
            batch_size=batch_size,
            h5_write_batch_size=h5_write_batch_size,
            alignment_backend=alignment_backend,
            clear_raw=clear_raw,
        )

    from resources.GenericUILibrary import ProgressModal

    dialog = ProgressModal(
        title="MFDenoiser Processing",
        message="Initializing MFDenoiser pipeline...",
        parent=parent,
        on_cancel_callback=stop_callback,
    )

    def update_progress(percent, message=""):
        dialog.set_progress(percent, message)
        if message:
            dialog.append_log(message)

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
        batch_size=batch_size,
        h5_write_batch_size=h5_write_batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )

    def on_finished():
        dialog.accept()

    def on_error(error):
        dialog.reject()

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
    batch_size=None,
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
        batch_size=batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )


def running_fusionnet(
    parent=None,
    single_process=None,
    batch_id=None,
    progress_callback=None,
    stop_callback=None,
    merging_mode=None,
    output_suffix=None,
    batch_size=None,
    alignment_backend=None,
    clear_raw=None,
):
    return running_mf_denoiser(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        merging_mode=merging_mode or "FusionNet",
        output_suffix=output_suffix or "weightnet",
        batch_size=batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )


running_weightnet = running_fusionnet


if __name__ == "__main__":
    session_db = os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not session_db:
        raise SystemExit(
            "Set PIXEL_REFINE_SESSION_DB before running MFDenoiser directly."
        )
    _run_pipeline_entry(session_db)
