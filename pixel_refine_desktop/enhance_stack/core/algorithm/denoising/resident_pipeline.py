"""Format-agnostic entry point for GPU-resident multi-frame processing.

Processors own decoding, pixel representation, fusion, and format-specific
output. This module selects a processor and preserves the historical imports.
"""

from __future__ import annotations

from . import rgb_linear_resident as _rgb_linear
from .raw_native_resident import RawNativePipelineNotReadyError, RawNativeResidentProcessor


def normalize_processing_format(value) -> str:
    """Return one canonical process format without guessing a fallback."""
    normalized = str(value or "RGB Linear").strip().casefold().replace("_", " ")
    if normalized in {"rgb linear", "rgb", "linear rgb"}:
        return "RGB Linear"
    if normalized in {"raw native", "native raw", "raw"}:
        return "RAW Native"
    raise ValueError(
        f"Unsupported processing format {value!r}; use 'RGB Linear' or 'RAW Native'."
    )


def get_configured_processing_format() -> str:
    """Read the General Settings default without coupling callers to Qt/UI."""
    try:
        from pixel_refine_desktop.ui.views.settings.General.general_store import (
            get_general_store,
        )

        return normalize_processing_format(
            get_general_store().get("processing_format", "RGB Linear")
        )
    except Exception:
        # Headless tools and isolated tests retain the existing RGB route.
        return "RGB Linear"


def resolve_resident_processor(processing_format=None):
    """Resolve a processor; no image pixels are decoded at this layer."""
    if processing_format is None:
        processing_format = get_configured_processing_format()
    canonical = normalize_processing_format(processing_format)
    if canonical == "RAW Native":
        return RawNativeResidentProcessor()
    return _rgb_linear.RGBLinearResidentProcessor()


def run_gpu_resident_pipeline(
    image_paths,
    session=None,
    *,
    weight_engine="fusionet",
    alignment_plan="optical_flow",
    alignment_config=None,
    spatial_config=None,
    work_scale=0.50,
    tile_size=512,
    overlap=0.30,
    ghost_penalty=1.0,
    ghost_cutoff=0.05,
    chroma_sensitivity=6.0,
    is_raw=False,
    storage_mode="direct",
    accumulation_mode="auto",
    alignment_only=False,
    batch_queue=3,
    auto_params=None,
    stop_event=None,
    progress_callback=None,
    accumulation_block_size=None,
    processing_format=None,
):
    """Dispatch a uniform resident request to its selected processor."""
    processor = resolve_resident_processor(processing_format)
    return processor.run(
        image_paths,
        session,
        weight_engine=weight_engine,
        alignment_plan=alignment_plan,
        alignment_config=alignment_config,
        spatial_config=spatial_config,
        work_scale=work_scale,
        tile_size=tile_size,
        overlap=overlap,
        ghost_penalty=ghost_penalty,
        ghost_cutoff=ghost_cutoff,
        chroma_sensitivity=chroma_sensitivity,
        is_raw=is_raw,
        storage_mode=storage_mode,
        accumulation_mode=accumulation_mode,
        alignment_only=alignment_only,
        batch_queue=batch_queue,
        auto_params=auto_params,
        stop_event=stop_event,
        progress_callback=progress_callback,
        accumulation_block_size=accumulation_block_size,
    )


run_resident_pipeline = run_gpu_resident_pipeline

# Compatibility exports for callers that still import RGB helpers here.
get_memory_telemetry_str = _rgb_linear.get_memory_telemetry_str
preflight_resident_dependencies = _rgb_linear.preflight_resident_dependencies
load_frame_to_gpu = _rgb_linear.load_frame_to_gpu
create_resident_aligner = _rgb_linear.create_resident_aligner


def __getattr__(name):
    return getattr(_rgb_linear, name)


__all__ = [
    "RawNativePipelineNotReadyError",
    "RawNativeResidentProcessor",
    "create_resident_aligner",
    "get_configured_processing_format",
    "get_memory_telemetry_str",
    "load_frame_to_gpu",
    "normalize_processing_format",
    "preflight_resident_dependencies",
    "resolve_resident_processor",
    "run_gpu_resident_pipeline",
    "run_resident_pipeline",
]
