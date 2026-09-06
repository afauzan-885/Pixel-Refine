"""Common alignment-estimation contract for resident image pipelines.

Estimators operate on a disposable RGB proxy.  Consumers decide how to apply
the result: RGB Linear warps RGB buffers, whereas RAW Native warps each CFA
plane.  Keeping this contract free of image buffers prevents an estimator from
accidentally becoming a colour-domain fusion step.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class ResidentAlignmentEstimate:
    """One support-to-reference transform derived from an RGB proxy.

    Exactly one payload is present: a full-sensor homography or a dense flow
    buffer in proxy coordinates.  ``release`` transfers/ends ownership of a
    dense GPU flow buffer deterministically.
    """

    plan: str
    full_shape: tuple[int, int]
    proxy_shape: tuple[int, int]
    homography: np.ndarray | None = None
    flow_gpu: object | None = None

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
        for name in ("release", "destroy"):
            callback = getattr(flow, name, None)
            if callable(callback):
                callback()
                return

