"""Shared per-frame execution runtime for image algorithms."""

from .contracts import (
    PipelineCancelledError,
    PipelineExecutionContext,
    PipelineOptions,
    PipelineRecipe,
    PipelineSource,
)
from .runtime import (
    IN_PROCESSING_MAX,
    IN_PROCESSING_MIN,
    IN_PROCESSING_SETTING_KEY,
    PREFETCH_MAX,
    PREFETCH_MIN,
    PREFETCH_SETTING_KEY,
    InProcessingLease,
    PipelineRuntime,
    current_pipeline_runtime,
    normalize_in_processing_depth,
    normalize_prefetch_depth,
    resolve_in_processing_depth,
    resolve_prefetch_depth,
    runtime_entrypoint,
)

__all__ = [
    "IN_PROCESSING_MAX",
    "IN_PROCESSING_MIN",
    "IN_PROCESSING_SETTING_KEY",
    "PREFETCH_MAX",
    "PREFETCH_MIN",
    "PREFETCH_SETTING_KEY",
    "PipelineCancelledError",
    "PipelineExecutionContext",
    "PipelineOptions",
    "PipelineRecipe",
    "InProcessingLease",
    "PipelineRuntime",
    "PipelineSource",
    "current_pipeline_runtime",
    "normalize_in_processing_depth",
    "normalize_prefetch_depth",
    "resolve_in_processing_depth",
    "resolve_prefetch_depth",
    "runtime_entrypoint",
]
