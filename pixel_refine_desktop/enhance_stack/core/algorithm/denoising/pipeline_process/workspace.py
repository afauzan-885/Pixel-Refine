"""Reusable host staging workspaces for WeightNet readback and upload.

Both workspaces register themselves with the resident component lifecycle so
their host arrays are released together with the owning session.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer

from .facade import api as _facade


__all__ = [
    "_WeightNetReadbackWorkspace",
    "_WeightNetUploadWorkspace",
]


class _WeightNetReadbackWorkspace:
    """Reuse host arrays across the serialized WeightNet support loop."""

    def __init__(self, shape: tuple[int, int], *, channels: int = 3):
        height, width = (max(1, int(shape[0])), max(1, int(shape[1])))
        self.channels = int(channels)
        if self.channels not in (1, 3):
            raise ValueError(f"WeightNet staging supports 1 or 3 channels, got {channels}")
        self.hwc = np.empty(
            (height, width) if self.channels == 1 else (height, width, self.channels),
            dtype=np.float32,
        )
        self.chw = np.empty((self.channels, height, width), dtype=np.float32)
        _facade()._own_component(self)

    def close(self):
        self.hwc = None
        self.chw = None

    def read(
        self,
        gpu_buffer: TaichiGPUBuffer,
        *,
        transfer_map: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        expected_shape = self.hwc.shape
        if (
            tuple(int(value) for value in getattr(gpu_buffer, "shape", ()))
            != expected_shape
            or np.dtype(getattr(gpu_buffer, "dtype", np.float32))
            != np.dtype(np.float32)
        ):
            raw = gpu_buffer.to_numpy()
            support_chw = np.ascontiguousarray(
                raw[None, ...] if raw.ndim == 2 else np.transpose(raw, (2, 0, 1)),
                dtype=np.float32,
            )
        else:
            gpu_buffer.to_numpy(out=self.hwc)
            if self.channels == 1:
                np.copyto(self.chw[0], self.hwc)
            else:
                np.copyto(self.chw, np.transpose(self.hwc, (2, 0, 1)))
            support_chw = self.chw
        if transfer_map is not None:
            support_chw = _facade().apply_precomputed_transfer_map(
                support_chw, transfer_map
            )
        return support_chw

    def readback(self, gpu_buffer: TaichiGPUBuffer) -> np.ndarray:
        """Read HWC data into the reusable host slot without transposing."""
        expected_shape = self.hwc.shape
        if (
            tuple(int(value) for value in getattr(gpu_buffer, "shape", ()))
            == expected_shape
            and np.dtype(getattr(gpu_buffer, "dtype", np.float32))
            == np.dtype(np.float32)
        ):
            gpu_buffer.to_numpy(out=self.hwc)
            return self.hwc
        return gpu_buffer.to_numpy()

    def as_chw(self, hwc: np.ndarray) -> np.ndarray:
        """Copy one HWC readback into the reusable CHW bridge slot."""
        if hwc is not self.hwc:
            chw = hwc[None, ...] if hwc.ndim == 2 else np.transpose(hwc, (2, 0, 1))
            return np.ascontiguousarray(chw, dtype=np.float32)
        if self.channels == 1:
            np.copyto(self.chw[0], self.hwc)
        else:
            np.copyto(self.chw, np.transpose(self.hwc, (2, 0, 1)))
        return self.chw


class _WeightNetUploadWorkspace:
    """Reuse the HWC host staging array used to upload each weight map."""

    def __init__(self, shape: tuple[int, int], *, channels: int = 3):
        height, width = (max(1, int(shape[0])), max(1, int(shape[1])))
        self.shape = (height, width)
        self.channels = int(channels)
        if self.channels not in (1, 3):
            raise ValueError(f"WeightNet upload staging supports 1 or 3 channels, got {channels}")
        self.hwc = (
            None
            if self.channels == 1
            else np.empty((height, width, 3), dtype=np.float32)
        )
        _facade()._own_component(self)

    def close(self):
        self.hwc = None

    def stage(self, weight_chw: np.ndarray) -> np.ndarray:
        array = np.asarray(weight_chw, dtype=np.float32)
        if self.channels == 1:
            if array.ndim == 3 and array.shape[0] == 1:
                array = array[0]
            if array.ndim != 2 or tuple(array.shape) != self.shape:
                raise ValueError(
                    f"Scalar weight map shape {array.shape} does not match "
                    f"workspace {self.shape}"
                )
            # The scalar inference result is already contiguous and upload()
            # consumes it immediately; pass a view instead of staging a second
            # full-resolution host copy.
            return array
        if array.ndim == 3 and array.shape[0] == 3:
            if tuple(array.shape[1:]) != self.hwc.shape[:2]:
                raise ValueError(
                    f"Weight map shape {array.shape} does not match "
                    f"workspace {self.hwc.shape[:2]}"
                )
            np.copyto(self.hwc, np.transpose(array, (1, 2, 0)))
            return self.hwc
        if array.ndim == 3 and array.shape[0] == 1:
            if tuple(array.shape[1:]) != self.hwc.shape[:2]:
                raise ValueError(
                    f"Weight map shape {array.shape} does not match "
                    f"workspace {self.hwc.shape[:2]}"
                )
            np.copyto(self.hwc, array[0, :, :, None])
            return self.hwc
        if array.ndim == 2 and tuple(array.shape) == self.hwc.shape[:2]:
            np.copyto(self.hwc, array[:, :, None])
            return self.hwc
        return np.ascontiguousarray(np.transpose(array, (1, 2, 0)), dtype=np.float32)
