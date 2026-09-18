"""Common alignment-estimation contract for resident image pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


_FUSIONNET_ALIGNMENT_ALIASES = {
    "block flow": "optical flow",
    "compute flow": "optical flow",
    "flownet": "optical flow",
    "optical flow": "optical flow",
    "dense optical flow": "optical flow",
    "block matching": "block matching gpu",
    "block matching gpu": "block matching gpu",
    "blockmatching": "block matching gpu",
    "block align": "block matching gpu",
    "bm": "block matching gpu",
    "no alignment": "no alignment",
    "none": "no alignment",
    "off": "no alignment",
    "": "no alignment",
}


def resolve_fusionnet_alignment_plan(value: str) -> str:
    """Return the canonical alignment plan for FusionNet."""
    normalized = str(value or "").strip().casefold().replace("_", " ").replace("-", " ")
    return _FUSIONNET_ALIGNMENT_ALIASES.get(normalized, normalized)


@dataclass
class ResidentAlignmentEstimate:
    """One support-to-reference transform derived from an RGB proxy."""

    plan: str
    full_shape: Tuple[int, int]
    proxy_shape: Tuple[int, int]
    homography: Optional[np.ndarray] = None
    flow_gpu: Optional[object] = None

    def __post_init__(self) -> None:
        if (self.homography is None) == (self.flow_gpu is None):
            raise ValueError(
                "ResidentAlignmentEstimate requires exactly one transform payload"
            )
        if self.homography is not None:
            matrix = np.asarray(self.homography, dtype=np.float32)
            if matrix.shape != (3, 3):
                raise ValueError(f"homography must have shape (3, 3), got {matrix.shape}")
            self.homography = np.ascontiguousarray(matrix)

    @property
    def kind(self) -> str:
        return "homography" if self.homography is not None else "dense_flow"

    def release(self) -> None:
        """Release an owned dense-flow buffer, if this estimate owns one."""
        flow = self.flow_gpu
        self.flow_gpu = None
        if flow is None:
            return
        for name in ("destroy", "release"):
            callback = getattr(flow, name, None)
            if callable(callback):
                try:
                    callback()
                except Exception:
                    pass
                return


__all__ = [
    "ResidentAlignmentEstimate",
    "resolve_fusionnet_alignment_plan",
]
