"""Public streaming Splat SR orchestrator backed by PipelineRuntime."""

from __future__ import annotations

import os
from typing import Sequence

from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
    PipelineCancelledError,
    PipelineRuntime,
    current_pipeline_runtime,
    runtime_entrypoint,
)


def build_reliability_provider(
    *,
    tile_size: int | None = None,
    overlap: float | None = None,
    motion_sensitivity: float | None = None,
    noise_sigma: float | None = None,
    session=None,
):
    """Build the shared compute_spatial reliability provider."""
    from .splat_sr.reliability_confidence import ReliabilityConfidenceProvider

    if tile_size is None:
        tile_size = int(os.environ.get("SPLATSR_RELIABILITY_TILE", "16"))
    if overlap is None:
        overlap = float(os.environ.get("SPLATSR_RELIABILITY_OVERLAP", "0.35"))
    return ReliabilityConfidenceProvider(
        tile_size=tile_size,
        overlap=overlap,
        motion_sensitivity=motion_sensitivity,
        noise_sigma=noise_sigma,
        session=session,
    )


@runtime_entrypoint
def run_splat_sr_pipeline(
    image_paths: Sequence[str],
    *,
    scale: int = 2,
    weight_source: str = "compute_spatial",
    alignment_method: str = "farneback",
    reliability_provider=None,
    block_size: int | None = None,
    block_overlap: float | None = None,
    refinement_iterations: int = 0,
    refinement_step: float = 0.1,
    refinement_regularization: float = 0.1,
    exposure_normalization: bool = True,
    output_path: str | None = None,
    prefetch_depth: int | None = None,
    progress_callback=None,
    stop_event=None,
):
    """Stream one support at a time and save with the existing MFD contract."""
    del prefetch_depth  # Snapshotted by runtime_entrypoint before this call.
    if not image_paths:
        raise ValueError("run_splat_sr_pipeline requires at least one image path")
    if isinstance(image_paths, (str, os.PathLike)):
        paths = (os.fspath(image_paths),)
    else:
        paths = tuple(os.fspath(path) for path in image_paths)
    if not paths:
        raise ValueError("run_splat_sr_pipeline requires at least one image path")

    from .splat_sr.streaming_pipeline import ImagePathSource, SplatSRRecipe
    from .splat_sr.legacy import _save_mfd_compatible_result

    if block_size is None:
        block_size = int(os.environ.get("SPLATSR_HANN_BLOCK", "1024"))
    if block_overlap is None:
        block_overlap = float(os.environ.get("SPLATSR_HANN_OVERLAP", "0.25"))

    source = ImagePathSource(paths)
    recipe = SplatSRRecipe(
        paths,
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
    )
    recipe.compute_gate = source.compute_gate
    runtime = current_pipeline_runtime()
    if runtime is None:
        # Only possible for direct undecorated/test invocation; normally the
        # decorator snapshots the Performance setting and owns this runtime.
        runtime = PipelineRuntime(
            prefetch_depth=0,
            stop_event=stop_event,
            progress_callback=progress_callback,
        )
    result = None
    try:
        try:
            result = runtime.execute(
                source,
                recipe,
                range(1, len(paths)),
            )
        except PipelineCancelledError:
            return None
        if result is None:
            return None

        if output_path is None:
            base = os.path.splitext(os.path.basename(paths[0]))[0]
            safe = "".join(c for c in base if c.isalnum() or c in ("_", "-")).rstrip()
            output_dir = os.path.join("database", "stack")
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(
                output_dir, f"{safe or 'sr_result'}_splattingSR.tif"
            )
        return _save_mfd_compatible_result(
            result,
            output_path,
            reference_image_path=paths[0],
        )
    finally:
        if result is not None and hasattr(result, "close"):
            result.close()
        # execute() closes its session; this covers the direct-call branch and
        # remains idempotent for the decorated job runtime.
        runtime.close()


__all__ = ["build_reliability_provider", "run_splat_sr_pipeline"]
