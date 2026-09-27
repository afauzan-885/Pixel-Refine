"""MFDenoiser-compatible HDR contracts and desktop pipeline entrypoint."""

from __future__ import annotations

from itertools import chain

from .card_content import CARD_CONTENT, CARD_NAME, LEGACY_CARD_NAME
from .hdr_fusion import WeightedHDRFusion, estimate_noise_taichi, rgb_to_gray
from .spde_mr import SPDEMRAlgorithm, SPDEMRFusion


class WeightedHDRAlgorithm:
    """Streaming weighted fusion over already aligned RGB frames."""

    NAME = CARD_NAME
    LEGACY_NAME = LEGACY_CARD_NAME
    KIND = "hdr"
    DESCRIPTION = CARD_CONTENT["description"]
    CARD_CATEGORIES = ("hdr",)

    def run(self, ctx, frames, batch_plan=None):
        """Fuse an iterable of same-size, already-aligned RGB frames.

        The desktop batch runner adds reference selection, MTB alignment, and
        output handling; this MFDenoiser-shaped method remains useful to callers
        that provide their own streaming source.
        """
        return _run_array_frames(self, ctx, frames)


def _run_array_frames(algorithm, ctx, frames):
    from pixel_refine_desktop.enhance_stack.core.algorithm.pipeline_runtime import (
        PipelineRuntime,
    )

    iterator = iter(frames)
    try:
        reference = next(iterator)
    except StopIteration as exc:
        raise ValueError("HDR fusion requires at least one frame") from exc

    stop_event = getattr(ctx, "stop_event", None)
    external_session = getattr(ctx, "session", None)
    runtime = None
    if external_session is None:
        runtime = PipelineRuntime(
            prefetch_depth=0,
            stop_event=stop_event,
            progress_callback=getattr(ctx, "progress_callback", None),
        )
        session = runtime.ensure_session()
    else:
        session = external_session

    try:
        import numpy as np

        reference = np.ascontiguousarray(reference, dtype=np.float32)
        radiance_enabled = False
        if isinstance(algorithm, SPDEMRAlgorithm):
            fusion = algorithm.create_fusion(
                reference, radiance_enabled=radiance_enabled
            )
        else:
            fusion = WeightedHDRFusion(reference.shape, radiance_enabled=False)
        for index, image in enumerate(chain((reference,), iterator)):
            if hasattr(ctx, "check_cancelled"):
                ctx.check_cancelled()
            elif stop_event is not None:
                stopped = (
                    stop_event.is_set()
                    if hasattr(stop_event, "is_set")
                    else stop_event()
                    if callable(stop_event)
                    else bool(stop_event)
                )
                if stopped:
                    raise RuntimeError("HDR fusion was cancelled")
            image = np.ascontiguousarray(image, dtype=np.float32)
            noise = estimate_noise_taichi(rgb_to_gray(image), session)
            if isinstance(algorithm, SPDEMRAlgorithm):
                fusion.add_spde_frame(
                    image,
                    noise_sigma=noise,
                    is_reference=index == 0,
                )
            else:
                fusion.add_frame(image, noise_sigma=noise)
        return fusion.finalize(reference)[0]
    finally:
        if runtime is not None:
            runtime.close()


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
    "SPDEMRAlgorithm",
    "SPDEMRFusion",
    "WeightedHDRAlgorithm",
    "WeightedHDRFusion",
    "running_hdr_fusion",
]
