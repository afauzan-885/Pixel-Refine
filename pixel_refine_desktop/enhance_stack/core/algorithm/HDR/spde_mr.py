"""Public SPDE-MR orchestrator for the streaming HDR pipeline."""

from __future__ import annotations

from pixel_refine_desktop.enhance_stack.core.algorithm.catalog import get_spec
from .SPDE.core import (
    PATCH_SIZE,
    PATCH_STRIDE,
    STRUCTURE_CORRELATION_MIN,
    SPDEMRFusion,
    score_patches,
)
from .card_content import SPDE_MR_NAME




class SPDEMRAlgorithm:
    """Expose the patch HDR option and delegate fusion work to ``HDR/SPDE``."""

    SPEC = get_spec("hdr", "spde_mr")
    NAME = SPEC.implementation_name
    KIND = SPEC.category
    DESCRIPTION = SPEC.description
    CARD_CATEGORIES = ("hdr",)

    def create_fusion(self, reference_rgb, *, radiance_enabled: bool):
        return SPDEMRFusion(reference_rgb, radiance_enabled=radiance_enabled)

    def run(self, ctx, frames, batch_plan=None):
        """Pass the frame stream to the shared HDR pipeline entry point."""
        from .HDR import _run_array_frames

        return _run_array_frames(self, ctx, frames)


__all__ = [
    "PATCH_SIZE",
    "PATCH_STRIDE",
    "STRUCTURE_CORRELATION_MIN",
    "SPDEMRAlgorithm",
    "SPDEMRFusion",
    "score_patches",
]
