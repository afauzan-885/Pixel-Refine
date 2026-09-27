"""RGB carrier provider for the shared resident lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from ..contracts import FrameMetadata, ProviderFrame, SourceMode


class RGBFrameProvider:
    """Load RGB (or demosaiced RAW) carriers and bind the shared accumulator."""

    source_mode: SourceMode = "rgb"
    carrier_kind = "rgb"

    def __init__(self, image_paths: Sequence[str | Path], *, is_raw: bool = False):
        self.image_paths = tuple(str(path) for path in image_paths)
        if not self.image_paths:
            raise ValueError("RGBFrameProvider requires at least one source frame")
        self.is_raw = bool(is_raw)
        self.source_mode = "raw_rgb" if self.is_raw else "rgb"
        self._sum_gpu = None
        self._weight_sum_gpu = None

    def metadata(self, index: int = 0, *, shape=(), dtype="float32") -> FrameMetadata:
        return FrameMetadata(
            source_id=self.image_paths[int(index)],
            shape=tuple(int(value) for value in shape),
            dtype=str(dtype),
            color_model="normalized_rgb",
            carrier_kind="rgb",
        )

    def load_reference_gpu(self):
        """Load the reference through the canonical resident RGB loader."""
        from ..resident_pipeline import load_frame_to_gpu

        return load_frame_to_gpu(self.image_paths[0], is_raw=self.is_raw)

    def load_reference(self) -> ProviderFrame:
        carrier = self.load_reference_gpu()
        return ProviderFrame(
            carrier=carrier,
            metadata=self.metadata(shape=carrier.shape, dtype=carrier.dtype),
        )

    def load_support_host(self, index: int):
        """Load one support frame for the bounded host staging queue.

        The resident executor still owns resizing and GPU upload.  Keeping the
        source decode here gives RGB images and legacy demosaiced RAW frames a
        single provider boundary without changing the queue contract.
        """
        from ...fusionet_engine.weightnet_inference import load_rgb_linear_image

        return load_rgb_linear_image(self.image_paths[int(index)], is_raw=self.is_raw)

    def load_support(self, index: int) -> ProviderFrame:
        carrier = self.load_support_host(index)
        return ProviderFrame(
            carrier=carrier,
            metadata=self.metadata(index, shape=carrier.shape, dtype=carrier.dtype),
        )

    def source_path(self, index: int) -> str:
        return self.image_paths[int(index)]

    def bind_accumulator(self, sum_gpu, weight_sum_gpu) -> None:
        """Bind the shared resident RGB accumulator for carrier fusion."""
        self._sum_gpu = sum_gpu
        self._weight_sum_gpu = weight_sum_gpu

    def accumulate(self, frame, transform=None, weight_map=None) -> None:
        """Accumulate one already-warped RGB carrier through the shared graph."""
        if self._sum_gpu is None or self._weight_sum_gpu is None:
            raise RuntimeError("RGBFrameProvider accumulator is not bound")
        if weight_map is None:
            raise ValueError("RGBFrameProvider.accumulate requires weight_map")
        from ..resident_pipeline import _gpu_blend_frame

        _gpu_blend_frame(
            self._sum_gpu,
            self._weight_sum_gpu,
            frame,
            weight_map,
        )

    def close(self) -> None:
        self._sum_gpu = None
        self._weight_sum_gpu = None
        return None


__all__ = ["RGBFrameProvider"]
