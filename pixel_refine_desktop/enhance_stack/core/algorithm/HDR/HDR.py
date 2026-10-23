"""MFDenoiser-compatible HDR contracts and desktop pipeline entrypoint."""

from __future__ import annotations

from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_spec

from .card_content import CARD_CONTENT, CARD_NAME, LEGACY_CARD_NAME
from .hdr_mask_pipeline import HDRMaskFusion
from .hdr_fusion import WeightedHDRFusion
from .spde_mr import SPDEMRAlgorithm, SPDEMRFusion




class WeightedHDRAlgorithm:
    """Streaming weighted fusion over already aligned RGB frames."""

    SPEC = get_spec("hdr", "weighted")
    NAME = SPEC.implementation_name
    LEGACY_NAME = SPEC.aliases[0]
    KIND = SPEC.category
    DESCRIPTION = SPEC.description
    CARD_CATEGORIES = ("hdr",)

    def run(self, ctx, frames, batch_plan=None):
        """Fuse an iterable of same-size, already-aligned RGB frames.

        The desktop batch runner adds reference selection, MTB alignment, and
        output handling; this MFDenoiser-shaped method remains useful to callers
        that provide their own streaming source.
        """
        return _run_array_frames(self, ctx, frames)


class HDRMaskAlgorithm:
    """Select one exposure source per output pixel using a hard mask."""

    SPEC = get_spec("hdr", "mask")
    NAME = SPEC.implementation_name
    KIND = SPEC.category
    DESCRIPTION = SPEC.description
    CARD_CATEGORIES = ("hdr",)

    def create_fusion(self, reference_rgb, *, radiance_enabled: bool):
        return HDRMaskFusion(
            reference_rgb.shape,
            radiance_enabled=radiance_enabled,
        )

    def run(self, ctx, frames, batch_plan=None):
        """Fuse an iterable of already-aligned, demosaiced RGB frames."""
        return _run_array_frames(self, ctx, frames)


def _run_array_frames(algorithm, ctx, frames):
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineRuntime,
    )
    from .runtime_recipe import HDRArraySource, HDRFusionRecipe

    cancel_callback = getattr(ctx, "check_cancelled", None)
    stop_event = (
        None
        if callable(cancel_callback)
        else getattr(ctx, "stop_event", None)
    )
    source = HDRArraySource(frames)
    recipe = HDRFusionRecipe(
        analyses=None,
        selected_index=0,
        support_paths=None,
        effective_exposures=None,
        is_spde_mr=isinstance(algorithm, SPDEMRAlgorithm),
        is_hdr_mask=isinstance(algorithm, HDRMaskAlgorithm),
        align_support=False,
        cancel_callback=cancel_callback,
        include_radiance=False,
    )
    runtime = PipelineRuntime(
        prefetch_depth=0,
        stop_event=stop_event,
        progress_callback=getattr(ctx, "progress_callback", None),
        session=getattr(ctx, "session", None),
    )
    return runtime.execute(
        source,
        recipe,
        source.support_indices(),
        own_reference=False,
    )


def running_hdr_fusion(
    parent=None,
    *,
    single_process=False,
    batch_id=1,
    algorithm_name=None,
    progress_callback=None,
    stop_callback=None,
    db_path=None,
):
    """Run selected HDR algorithm over the active batch using one-frame reads."""
    from .streaming_pipeline import run_hdr_batch

    return run_hdr_batch(
        parent=parent,
        single_process=single_process,
        batch_id=batch_id,
        algorithm_name=algorithm_name or CARD_NAME,
        progress_callback=progress_callback,
        stop_callback=stop_callback,
        db_path=db_path,
    )


__all__ = [
    "HDRMaskAlgorithm",
    "SPDEMRAlgorithm",
    "SPDEMRFusion",
    "WeightedHDRAlgorithm",
    "WeightedHDRFusion",
    "running_hdr_fusion",
]
