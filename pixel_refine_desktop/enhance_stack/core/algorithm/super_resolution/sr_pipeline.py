"""Backward-compatible API for the Splat SR runtime orchestrator."""

from .splat_SR import (
    build_reliability_provider,
    run_splat_sr_pipeline as _run_splat_sr_pipeline,
)


def run_splat_sr_pipeline(
    image_paths,
    *,
    scale=2,
    weight_source="compute_spatial",
    alignment_method="farneback",
    reliability_provider=None,
    block_size=None,
    block_overlap=None,
    refinement_iterations=0,
    refinement_step=0.1,
    refinement_regularization=0.1,
    exposure_normalization=True,
    output_path=None,
    update_progress=None,
    stop_requested=None,
    prefetch_depth=None,
):
    """Keep the former callback names and route them into PipelineRuntime."""
    return _run_splat_sr_pipeline(
        image_paths,
        scale=scale,
        weight_source=weight_source,
        alignment_method=alignment_method,
        reliability_provider=reliability_provider,
        block_size=block_size,
        block_overlap=block_overlap,
        refinement_iterations=refinement_iterations,
        refinement_step=refinement_step,
        refinement_regularization=refinement_regularization,
        exposure_normalization=exposure_normalization,
        output_path=output_path,
        prefetch_depth=prefetch_depth,
        progress_callback=update_progress,
        stop_event=stop_requested,
    )


__all__ = ["build_reliability_provider", "run_splat_sr_pipeline"]
