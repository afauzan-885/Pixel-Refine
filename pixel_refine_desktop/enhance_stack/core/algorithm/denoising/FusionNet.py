"""Thin FusionNet adapter for the resident ONNX WeightNet pipeline.

FusionNet owns product-level parameter resolution and output conversion only.
The resident pipeline owns frame residency, Taichi alignment, ONNX weight-map
inference, and normalized accumulation.  This mirrors ``SpatialFusion`` while
retaining WeightNet's proven decoupled Encoder + Attention ONNX models.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from config import GENERAL_SETTINGS_FILE

from ._common_helpers import active_backend, restore_output_dtype
from .resident_alignment import resolve_fusionnet_alignment_plan
from .fusionet_engine.weightnet_inference import (
    DEFAULT_WEIGHTNET_ONNX,
    RAW_EXTENSIONS,
    load_weightnet_onnx,
    run_weightnet_inference,
)


def _read_onnx_runtime() -> str:
    """Read the user preference without making the adapter depend on Qt."""
    try:
        with open(GENERAL_SETTINGS_FILE, "r", encoding="utf-8") as handle:
            runtime = str(json.load(handle).get("onnx_runtime", "auto")).strip().lower()
    except (OSError, json.JSONDecodeError):
        runtime = "auto"
    return runtime if runtime in {"auto", "dml", "cpu"} else "auto"


def _is_stopped(stop_requested) -> bool:
    if stop_requested is None:
        return False
    if callable(stop_requested):
        return bool(stop_requested())
    if hasattr(stop_requested, "is_set"):
        return bool(stop_requested.is_set())
    return False


class FusionNetDenoisingAlgorithm:
    """ONNX WeightNet fusion adapter sharing SpatialFusion's routing contract."""

    NAME = "FusionNet"
    KIND = "denoising"
    DESCRIPTION = "ONNX WeightNet multi-frame fusion with resident Taichi alignment."

    DEFAULT_CONFIG = {
        "work_scale": 0.75,
        "tile_size": 256,
        "tile_overlap": 0.30,
        "ghost_penalty": 1.5,
        "ghost_cutoff": 0.05,
        "chroma_sensitivity": 10.0,
        "onnx_runtime": "auto",
    }
    _SUPPORTED_TILES = {256, 512, 1024}

    def _resolve_config(self, ctx) -> dict:
        """Merge persisted batch parameters over FusionNet's stable defaults."""
        params = getattr(ctx, "params", {}) or {}
        config = dict(self.DEFAULT_CONFIG)
        aliases = {
            "work_scale": ("weightnet_work_scale", "work_scale"),
            "tile_size": ("fusionnet_tile_size", "weightnet_tile_size", "tile_size"),
            "tile_overlap": ("tile_overlap", "overlap"),
            "ghost_penalty": ("ghost_penalty",),
            "ghost_cutoff": ("ghost_cutoff",),
            "chroma_sensitivity": ("chroma_sensitivity",),
            "onnx_runtime": ("onnx_runtime",),
        }
        nested = params.get("fusionnet_params")
        if isinstance(nested, dict):
            params = {**params, **nested}
        for target, names in aliases.items():
            for name in names:
                if params.get(name) is not None:
                    config[target] = params[name]
                    break

        config["work_scale"] = float(config["work_scale"])
        config["tile_size"] = int(config["tile_size"])
        config["tile_overlap"] = float(config["tile_overlap"])
        config["ghost_penalty"] = float(config["ghost_penalty"])
        config["ghost_cutoff"] = float(config["ghost_cutoff"])
        config["chroma_sensitivity"] = float(config["chroma_sensitivity"])
        config["onnx_runtime"] = str(
            config["onnx_runtime"] or _read_onnx_runtime()
        ).lower()

        if not 0.05 <= config["work_scale"] <= 1.0:
            raise ValueError("FusionNet work_scale must be within [0.05, 1.0].")
        if config["tile_size"] not in self._SUPPORTED_TILES:
            raise ValueError(
                "FusionNet tile_size must match an exported ONNX profile: "
                f"{sorted(self._SUPPORTED_TILES)}."
            )
        if not 0.0 <= config["tile_overlap"] < 1.0:
            raise ValueError("FusionNet tile_overlap must be within [0.0, 1.0).")
        if config["onnx_runtime"] not in {"auto", "dml", "cpu"}:
            raise ValueError("FusionNet onnx_runtime must be 'auto', 'dml', or 'cpu'.")
        return config

    @staticmethod
    def _is_raw(ctx, image_paths) -> bool:
        return bool(getattr(ctx, "is_linear_mode", False)) or any(
            Path(path).suffix.lower() in RAW_EXTENSIONS for path in (image_paths or ())
        )

    def _run_resident(self, ctx, image_paths, config):
        """Load the stable ONNX pair once and dispatch the uniform resident request."""
        from .resident_pipeline import run_resident_pipeline

        stop_requested = getattr(ctx, "stop_requested", None)
        if _is_stopped(stop_requested):
            return None

        is_raw = self._is_raw(ctx, image_paths)
        params = getattr(ctx, "params", {}) or {}
        requested_alignment = getattr(
            ctx, "alignment_selection_name", None
        ) or params.get("alignment_plan", "No Alignment")
        alignment_plan = resolve_fusionnet_alignment_plan(requested_alignment)
        runtime = (
            config["onnx_runtime"]
            if config["onnx_runtime"] != "auto"
            else _read_onnx_runtime()
        )
        session = load_weightnet_onnx(
            DEFAULT_WEIGHTNET_ONNX,
            runtime=runtime,
            patch_size=config["tile_size"],
        )
        batch_queue = int(params.get("batch_queue", params.get("batch_size", 3)))

        print(
            f"[FusionNet] ONNX resident pipeline: backend={active_backend()} "
            f"frames={len(image_paths)} raw={is_raw} tile={config['tile_size']} "
            f"runtime={runtime} alignment={alignment_plan}"
        )
        result, mean_alpha = run_resident_pipeline(
            image_paths,
            session=session,
            weight_engine="fusionet",
            alignment_plan=alignment_plan,
            alignment_config=params.get("alignment_params", {}),
            work_scale=config["work_scale"],
            tile_size=config["tile_size"],
            overlap=config["tile_overlap"],
            ghost_penalty=config["ghost_penalty"],
            ghost_cutoff=config["ghost_cutoff"],
            chroma_sensitivity=config["chroma_sensitivity"],
            is_raw=is_raw,
            storage_mode="direct",
            accumulation_mode="full",
            batch_queue=batch_queue,
            stop_event=stop_requested,
            progress_callback=getattr(ctx, "update_progress", None),
            processing_format=params.get("processing_format", "RGB Linear"),
        )
        if result is None:
            return None
        from .Average import RawNativeAverageResult

        if isinstance(result, RawNativeAverageResult):
            # The DNG/TIFF decision remains owned by MFDenoiser.save_process.
            # The preview is display-only; sensor data stays in the result.
            ctx.raw_native_result = result
            result = result.preview_rgb
        dtype = getattr(ctx, "ref_dtype", np.uint16 if is_raw else np.uint8)
        return restore_output_dtype(result, dtype), mean_alpha

    def _run_memory_legacy(self, ctx, frames, config):
        """Keep the public in-memory contract on the maintained WeightNet helper."""
        if not frames:
            return None
        result, mean_alpha = run_weightnet_inference(
            frames=frames,
            is_raw=bool(getattr(ctx, "is_linear_mode", False)),
            model_path=DEFAULT_WEIGHTNET_ONNX,
            work_scale=config["work_scale"],
            tile_size=config["tile_size"],
            overlap=config["tile_overlap"],
            ghost_penalty=config["ghost_penalty"],
            ghost_cutoff=config["ghost_cutoff"],
            stop_event=getattr(ctx, "stop_requested", None),
            progress_callback=getattr(ctx, "update_progress", None),
        )
        dtype = getattr(ctx, "ref_dtype", np.asarray(frames[0]).dtype)
        return restore_output_dtype(result, dtype), mean_alpha

    def run(self, ctx, frames=None, batch_plan=None):
        """Process file bursts resident; retain a tested helper for memory callers."""
        config = self._resolve_config(ctx)
        image_paths = tuple(getattr(ctx, "image_paths", None) or ())
        if len(image_paths) >= 2:
            outcome = self._run_resident(ctx, image_paths, config)
        else:
            outcome = self._run_memory_legacy(ctx, frames, config)
        if outcome is None:
            return None

        result, mean_alpha = outcome
        print(
            f"[FusionNet] finished backend={active_backend()} "
            f"shape={result.shape} dtype={result.dtype} mean_alpha={mean_alpha:.4f}"
        )
        return result


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
    db_path=None,
):
    """Facade delegating to ``running_mf_denoiser`` with FusionNet selected."""
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
        running_mf_denoiser,
    )

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
        db_path=db_path,
    )
