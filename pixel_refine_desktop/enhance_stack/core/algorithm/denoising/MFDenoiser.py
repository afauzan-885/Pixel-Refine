"""
MFDenoiser.py - Multi-Frame Denoising High-Level Orchestrator.

Delegates multi-frame processing (preloading, alignment, weighting, and accumulation)
to the high-performance GPU-resident pipeline (resident_pipeline.py).
"""

import json
import os
import sqlite3
from dataclasses import dataclass, field
from typing import Optional
import numpy as np

from config import GENERAL_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
    get_all_image_paths_for_single_process,
    save_image,
    save_linear_dng,
    setup_balanced_batching,
)
from pixel_refine_desktop.enhance_stack.core.algorithm.base_worker import (
    BaseAlgorithmWorker,
)


def _lang():
    from pixel_refine_desktop.ui.views.settings.General.Language import language_config

    return language_config


def _progress(callback, percent, message="", **kwargs):
    if callback:
        if kwargs:
            callback(int(percent), message=message, **kwargs)
        else:
            callback(int(percent), str(message))


# ---------------------------------------------------------------------------
# Progress stage constants
# ---------------------------------------------------------------------------
# Every progress callback in MFDenoiser + resident_pipeline must report a
# monotonically non-decreasing percentage from these bands so the user
# sees a clean, ordered, accurate progress bar instead of jumps.
#
#   0  – 2   pipeline start (caller MFDenoiser)
#   2  – 5   memuat gambar (resident_pipeline phase 1)
#   5  – 25  alignment (resident_pipeline phase 2-4, plus per-frame updates)
#  25  – 90  weightmap + merging (resident_pipeline frame loop)
#  90  – 95  finalisasi GPU-resident fusion
#  95  – 100 save result + done
# ---------------------------------------------------------------------------
PROGRESS_PIPELINE_START = 0
PROGRESS_LOAD_IMAGES_MIN = 2
PROGRESS_LOAD_IMAGES_MAX = 5
PROGRESS_ALIGN_MIN = 5
PROGRESS_ALIGN_MAX = 25
PROGRESS_MERGE_MIN = 25
PROGRESS_MERGE_MAX = 90
PROGRESS_FINALIZE_MIN = 90
PROGRESS_FINALIZE_MAX = 95
PROGRESS_SAVE = 96
PROGRESS_DONE = 100


def _align_percent(i: int, total: int) -> int:
    """Map a frame index *i* / *total* (alignment loop) to the 5-25 band."""
    if total <= 0:
        return PROGRESS_ALIGN_MIN
    ratio = max(0.0, min(1.0, i / total))
    return int(PROGRESS_ALIGN_MIN + ratio * (PROGRESS_ALIGN_MAX - PROGRESS_ALIGN_MIN))


def _merge_percent(i: int, total: int) -> int:
    """Map a frame index *i* / *total* (merge / fusion loop) to the 25-90 band."""
    if total <= 0:
        return PROGRESS_MERGE_MIN
    ratio = max(0.0, min(1.0, i / total))
    return int(PROGRESS_MERGE_MIN + ratio * (PROGRESS_MERGE_MAX - PROGRESS_MERGE_MIN))


class NoAlignmentAlgorithm:
    NAME = "No Alignment"
    KIND = "alignment"
    DESCRIPTION = "Skip alignment."

    def run(self, ctx, frames, batch_plan=None):
        return list(frames) if frames else []


class NoDenoisingAlgorithm:
    NAME = "No Denoising"
    KIND = "denoising"
    DESCRIPTION = "Return the reference/aligned first frame unchanged."

    def run(self, ctx, frames, batch_plan=None):
        if not frames:
            return None
        return np.array(frames[0], copy=True)


def get_alignment_registry():
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.AKAZE import (
        AKAZEAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.Light_Glue import (
        LightGlueAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.feature_matching.OFB import (
        OFBAlgorithm,
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
        OFBAlgorithm(),
        ORBAlgorithm(),
        AKAZEAlgorithm(),
        LightGlueAlgorithm(),
        FarnebackFlowCPU(),
        LucasKanadeCPU(),
        LucasKanadeGPU(),
        BlockMatchingGPU(),
        RAFTFlow(),
    ]
    return {algo.NAME: algo for algo in algorithms}


def get_denoising_registry():
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Average import (
        AverageDenoisingAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.SpatialFusion import (
        SpatialFusionDenoisingAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.FusionNet import (
        FusionNetDenoisingAlgorithm,
    )
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.Median import (
        MedianDenoisingAlgorithm,
    )

    algorithms = [
        NoDenoisingAlgorithm(),
        AverageDenoisingAlgorithm(),
        SpatialFusionDenoisingAlgorithm(),
        FusionNetDenoisingAlgorithm(),
        MedianDenoisingAlgorithm(),
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
            "OFB",
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
    """Derive the display order from :func:`get_algorithm_options`."""
    return [name for name, _ in get_algorithm_options(category)]


def _normalize_algorithm_name(name):
    return str(name or "").strip().casefold()


def _resolve_algorithm(registry, requested_name, fallback_name):
    if requested_name in registry:
        return registry[requested_name]

    normalized = _normalize_algorithm_name(requested_name)
    for name, algorithm in registry.items():
        if _normalize_algorithm_name(name) == normalized:
            return algorithm

    # Common aliases
    aliases = {
        "ofb": "OFB",
        "orb": "OFB",
        "akaze": "AKAZE",
        "light glue": "Light Glue",
        "lightglue": "Light Glue",
        "farneback": "Farneback Optical Flow",
        "farneback optical flow": "Farneback Optical Flow",
        "lucas kanade": "Lucas Kanade Optical Flow",
        "lucas kanade optical flow": "Lucas Kanade Optical Flow",
        "lucas kanade gpu": "Lucas Kanade GPU Optical Flow",
        "lucas kanade gpu optical flow": "Lucas Kanade GPU Optical Flow",
        "block matching gpu": "Block Matching GPU",
        "block_matching_gpu": "Block Matching GPU",
        "raft": "RAFT Optical Flow",
        "average": "Average",
        "median": "Median",
        "similarity": "Similarity",
        "spatial fusion": "Similarity",
        "fusionnet": "FusionNet",
        "spatial ai": "FusionNet",
        "no alignment": "No Alignment",
        "no denoising": "No Denoising",
    }
    target = aliases.get(normalized)
    if target and target in registry:
        return registry[target]

    return registry[fallback_name]


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
    batch_plan: list = field(default_factory=list)
    params: dict = field(default_factory=dict)
    is_linear_mode: bool = False
    update_progress: object = None
    stop_requested: object = None
    single_process: bool = True
    batch_id: object = None
    clear_raw: bool = True
    alignment_selection_name: str = "No Alignment"
    alignment_effective_name: str = "No Alignment"
    compute_runtime: dict = field(default_factory=dict)


class MFDenoiserAlgorithm:
    """High-level Orchestrator for multi-frame denoising modes."""

    def __init__(self, db_path=None):
        self.db_path = db_path or os.environ.get("PIXEL_REFINE_SESSION_DB")
        if not self.db_path:
            raise RuntimeError(
                "A session database is required. Set PIXEL_REFINE_SESSION_DB "
                "or pass db_path explicitly."
            )

    @staticmethod
    def _configure_compute_runtime(ctx, frame_shape=None):
        """Connect pipeline to the shared adaptive block/VRAM runtime."""
        try:
            from taichi_vision import taichi_aot

            engine = taichi_aot.get_engine()
            backend = str(getattr(engine, "arch", "")).strip().lower()
            memory = taichi_aot.get_memory_status(force=True)
            pipeline_limit = int(memory.get("pipeline_resident_limit", 0) or 0)
            pressure = str(memory.get("pressure", "healthy")).lower()

            ctx.compute_runtime = {
                "available": True,
                "backend": backend,
                "pressure": pressure,
                "pipeline_limit_mb": pipeline_limit // (1024 * 1024),
            }
            print(
                f"[MFDenoiser] Compute Backend: {backend.upper()} (VRAM Limit: {pipeline_limit // (1024 * 1024)}MB, Pressure: {pressure})"
            )
        except Exception as exc:
            ctx.compute_runtime = {"available": False, "reason": str(exc)}
        return ctx.compute_runtime

    @staticmethod
    def _report_compute_runtime(ctx):
        if not ctx.compute_runtime.get("available"):
            return
        try:
            from taichi_vision import taichi_aot

            stats = taichi_aot.get_block_cache_stats()
            device = stats.get("device", {})
            pass
        except Exception:
            pass

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

    def _load_params(self, batch_id=None):
        try:
            from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
                load_similarity_config,
            )

            config = load_similarity_config()
        except Exception:
            config = {}

        params = config.copy()
        params.update(
            {
                "processing_mode": config.get("mfdenoiser_processing_mode", "auto"),
                "tile_size": int(config.get("tile_based_tile_size", 256)),
                "tile_overlap": float(config.get("tile_based_overlap_percent", 0.20)),
                "alignment_plan": config.get(
                    "mfdenoiser_alignment_plan", "No Alignment"
                ),
                "merge_plan": config.get("mfdenoiser_merge_plan", "No Denoising"),
                "batch_size": int(
                    config.get(
                        "mfdenoiser_batch_size",
                        config.get("ai_batch_size", 15),
                    )
                ),
                "clear_raw": bool(config.get("mfdenoiser_clear_raw", True)),
                "output_suffix": "mf_denoiser",
            }
        )

        if batch_id is not None:
            try:
                from pixel_refine_desktop.enhance_stack.core.logic import (
                    batch_parameter_manager,
                )

                batch_data = batch_parameter_manager.load_json_state()
                b_str = str(batch_id)
                if b_str in batch_data and isinstance(batch_data[b_str], dict):
                    b_cfg = batch_data[b_str]
                    if "similarity_params" in b_cfg and isinstance(
                        b_cfg["similarity_params"], dict
                    ):
                        params.update(b_cfg["similarity_params"])
                    alignment_params = b_cfg.get("alignment_params")
                    if isinstance(alignment_params, dict):
                        params["alignment_params"] = alignment_params.copy()
                    else:
                        block_matching_params = b_cfg.get("block_matching_gpu_params")
                        if isinstance(block_matching_params, dict):
                            params["alignment_params"] = block_matching_params.copy()
            except Exception:
                pass

        pass

        try:
            if os.path.exists(GENERAL_SETTINGS_FILE):
                with open(GENERAL_SETTINGS_FILE, "r") as f:
                    general = json.load(f)
                params["enable_linear_mode"] = general.get("enable_linear_mode", False)
        except (OSError, json.JSONDecodeError):
            params["enable_linear_mode"] = False

        return params

    def prepare_input_paths(self, ctx):
        """Load paths and shared metadata without keeping all image arrays in memory."""
        ctx.image_paths = self._get_image_paths(
            ctx.batch_id if not ctx.single_process else None
        )
        ctx.total_images = len(ctx.image_paths)
        print(
            f"[MFDenoiser] Loaded {ctx.total_images} frames ({'Single' if ctx.single_process else 'Batch ' + str(ctx.batch_id)})"
        )
        # Individual image paths suppressed for clean console output
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
        """Create comparison-frame batch plan."""
        batch_size = max(1, int(ctx.params.get("batch_size", 6)))
        comparison_paths = ctx.image_paths[1:]
        comparison_plan = setup_balanced_batching(
            comparison_paths,
            _lang(),
            max_batch_size=batch_size,
        )
        ctx.batch_plan = [(start + 1, end + 1) for start, end in comparison_plan]
        pass
        return ctx.batch_plan

    def align_process(self, ctx, batch_plan=None):
        """Alignment stage coordinator.

        The actual alignment work and per-frame progress callbacks live
        inside ``resident_pipeline.run_gpu_resident_pipeline`` (which
        already reports percentages in the 5-25 band). This method
        only records the selected algorithm on the context and emits a
        single announcement on the same band so the user immediately
        sees *which* alignment algorithm is about to run.
        """
        alignment_name = ctx.params.get("alignment_plan", "No Alignment")
        registry = get_alignment_registry()
        algorithm = _resolve_algorithm(registry, alignment_name, "No Alignment")
        ctx.alignment_selection_name = alignment_name
        ctx.alignment_effective_name = algorithm.NAME

        pass
        return ctx

    def merge_process(self, ctx, batch_plan=None):
        """Execute the selected denoising/merging algorithm.

        The heavy per-frame progress is emitted by
        ``resident_pipeline.run_gpu_resident_pipeline`` (band 5-90).
        """
        denoising_name = ctx.params.get("merge_plan", "No Denoising")
        registry = get_denoising_registry()
        algorithm = _resolve_algorithm(registry, denoising_name, "No Denoising")
        pass

        if algorithm.NAME == "No Denoising":
            if ctx.image_paths:
                from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.resident_pipeline import (
                    load_frame_to_gpu,
                )

                ref_gpu = load_frame_to_gpu(
                    ctx.image_paths[0], is_raw=ctx.is_linear_mode
                )
                ref_np = ref_gpu.to_numpy()
                ref_gpu.destroy()
                scale = 65535.0 if ctx.is_linear_mode else 255.0
                ctx.result_image = np.clip(ref_np * scale + 0.5, 0, scale).astype(
                    np.uint16 if ctx.is_linear_mode else np.uint8
                )
            return ctx

        frames = ctx.aligned_frames or ctx.frames
        ctx.result_image = algorithm.run(ctx, frames, batch_plan=batch_plan)
        pass
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
        raw_native_result = getattr(ctx, "raw_native_result", None)
        if raw_native_result is not None:
            raw_output_path = os.path.splitext(output_path)[0] + ".dng"
            raw_native_result.save_dng(raw_output_path)
            print(f"[MFDenoiser] Saved RAW Native DNG to: {raw_output_path}")
            return raw_output_path

        print(f"[MFDenoiser] Saved output to: {output_path}")

        if ctx.is_linear_mode:
            return save_linear_dng(
                ctx.result_image,
                os.path.splitext(output_path)[0] + ".dng",
                reference_image_path=ctx.image_paths[0] if ctx.image_paths else None,
            )

        # Apply tone mapping only on RAW input (linear sensor data).
        # For standard non-RAW images (JPG, PNG, sRGB TIFF), tone mapping is already baked in,
        # so we disable tone mapping to prevent double tone mapping (oversaturation / blown highlights).
        is_raw_input = False
        if ctx.image_paths:
            _, ext = os.path.splitext(ctx.image_paths[0])
            is_raw_input = ext.lower() in (
                ".dng",
                ".cr2",
                ".cr3",
                ".nef",
                ".arw",
                ".orf",
                ".rw2",
                ".pef",
                ".raf",
            )

        save_image(
            ctx.result_image,
            output_path,
            reference_image_path=ctx.image_paths[0] if ctx.image_paths else None,
            apply_tonemapping=is_raw_input,
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
        ctx.params = self._load_params(batch_id=batch_id)
        # General Settings owns the default processing domain. A batch-level
        # value remains authoritative so saved jobs can opt in explicitly.
        if "processing_format" not in ctx.params:
            try:
                from pixel_refine_desktop.ui.views.settings.General.general_store import (
                    get_general_store,
                )

                ctx.params["processing_format"] = get_general_store().get(
                    "processing_format", "RGB Linear"
                )
            except Exception:
                ctx.params["processing_format"] = "RGB Linear"
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
        if alignment_backend is not None:
            ctx.params["alignment_plan"] = alignment_backend
        if clear_raw is not None:
            ctx.params["clear_raw"] = bool(clear_raw)
        ctx.clear_raw = bool(ctx.params.get("clear_raw", True))

        self._configure_compute_runtime(ctx)
        print(
            f"[MFDenoiser] Pipeline Start: Alignment='{ctx.params.get('alignment_plan')}' | Merge='{ctx.params.get('merge_plan')}'"
        )

        # Stage 0: pipeline start
        _progress(
            update_progress,
            PROGRESS_PIPELINE_START,
            ui="Memulai proses...",
            console=f"MFDenoiser start: alignment={ctx.params.get('alignment_plan')}, denoising={ctx.params.get('merge_plan')}",
        )

        ctx = self.prepare_input_paths(ctx)
        if not ctx.total_images:
            _progress(
                update_progress,
                PROGRESS_DONE,
                ui="Tidak ada gambar.",
                console=getattr(
                    _lang(), "NO_IMAGE_PATH_PROCESSED_IMAGE", "No image to process."
                ),
            )
            return None
        if stop_requested and stop_requested():
            return None

        # Stage 1: announce that we are about to enumerate the
        # comparison batch plan. Real image loading happens inside the
        # GPU-resident pipeline (band 2-5).
        _progress(
            update_progress,
            PROGRESS_LOAD_IMAGES_MIN,
            ui="Memuat daftar gambar...",
            console=f"Memuat {ctx.total_images} gambar untuk pemrosesan batch...",
        )

        batch_plan = self.build_batch_plan(ctx)
        ctx = self.align_process(ctx, batch_plan=batch_plan)
        if stop_requested and stop_requested():
            return None

        ctx = self.merge_process(ctx, batch_plan=batch_plan)
        if (stop_requested and stop_requested()) or ctx.result_image is None:
            print("[MFDenoiser][Pipeline] Execution aborted (cancelled or no output).")
            return None

        # Stage 5: save the merged result. We move the bar to the
        # ``PROGRESS_SAVE`` slot (96%) and let ``save_process`` complete
        # before the final 100% announcement below.
        _progress(
            update_progress,
            PROGRESS_SAVE,
            ui="Menyimpan gambar...",
            console="Menyimpan hasil rekonstruksi MFDenoiser...",
        )
        output_path = self.save_process(ctx)
        self._report_compute_runtime(ctx)
        pass
        _progress(
            update_progress,
            PROGRESS_DONE,
            ui="Selesai.",
            console=f"MFDenoiser selesai: {output_path}",
        )
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
        output_suffix=output_suffix or "fusionet",
        batch_size=batch_size,
        alignment_backend=alignment_backend,
        clear_raw=clear_raw,
    )


if __name__ == "__main__":
    session_db = os.environ.get("PIXEL_REFINE_SESSION_DB")
    if not session_db:
        raise SystemExit(
            "Set PIXEL_REFINE_SESSION_DB before running MFDenoiser directly."
        )
    _run_pipeline_entry(session_db)
