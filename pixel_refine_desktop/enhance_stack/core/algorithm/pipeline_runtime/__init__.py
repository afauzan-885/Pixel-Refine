"""Shared per-frame execution runtime for image algorithms."""

from .contracts import (
    PipelineCancelledError,
    PipelineExecutionContext,
    PipelineOptions,
    PipelineRecipe,
    PipelineSource,
)
from .runtime import (
    PREFETCH_MAX,
    PREFETCH_MIN,
    PREFETCH_SETTING_KEY,
    PipelineRuntime,
    current_pipeline_runtime,
    normalize_prefetch_depth,
    resolve_prefetch_depth,
    runtime_entrypoint,
)

__all__ = [
    "PREFETCH_MAX",
    "PREFETCH_MIN",
    "PREFETCH_SETTING_KEY",
    "PipelineCancelledError",
    "PipelineExecutionContext",
    "PipelineOptions",
    "PipelineRecipe",
    "PipelineRuntime",
    "PipelineSource",
    "current_pipeline_runtime",
    "normalize_prefetch_depth",
    "resolve_prefetch_depth",
    "runtime_entrypoint",
]
