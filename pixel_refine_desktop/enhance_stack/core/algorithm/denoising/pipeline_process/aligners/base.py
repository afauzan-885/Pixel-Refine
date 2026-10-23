"""Resident aligner primitives shared by the dense-flow aligners.

The passthrough aligner and the reusable resident-flow buffer mixin live here so
every flow aligner inherits the same single-destination buffer lifecycle.
"""

from __future__ import annotations

import numpy as np

from taichi_vision.taichi_aot import TaichiGPUBuffer, get_engine

from ..facade import api as _facade

__all__ = ["NoAlignmentGPUAligner", "_ResidentFlowBufferMixin"]


class NoAlignmentGPUAligner:
    """Pass-through aligner when no alignment is requested."""

    def __init__(self, ref_frame, **kwargs):
        pass

    def align_frame(
        self,
        supp_linear_gpu,
        *,
        analysis_frame_gpu=None,
        secondary_frame_to_warp=None,
        stop_event=None,
        return_gpu=True,
        return_transform: bool = False,
    ):
        if stop_event is not None:
            if hasattr(stop_event, "is_set") and stop_event.is_set():
                raise RuntimeError("Alignment cancelled.")
            elif callable(stop_event) and stop_event():
                raise RuntimeError("Alignment cancelled.")
        if return_transform:
            return supp_linear_gpu, secondary_frame_to_warp, None
        return supp_linear_gpu, secondary_frame_to_warp

    def close(self):
        pass


class _ResidentFlowBufferMixin:
    """Own one reusable dense-flow destination for a resident aligner."""

    def _init_resident_flow_buffer(self):
        self._resident_flow_buffer = None
        self._resident_quantized_flow_buffer = None

    def _ensure_resident_flow_buffer(self, shape):
        expected = tuple(int(value) for value in shape)
        current = getattr(self, "_resident_flow_buffer", None)
        if (
            current is not None
            and getattr(current, "handle", None) is not None
            and tuple(int(value) for value in getattr(current, "shape", ()))
            == expected
            and np.dtype(getattr(current, "dtype", np.float32))
            == np.dtype(np.float32)
        ):
            return current
        if current is not None and hasattr(current, "destroy"):
            _facade()._destroy_work_item(current)
        self._resident_flow_buffer = _facade()._managed_api(get_engine()).allocate(
            expected,
            dtype=np.float32,
            is_vector=False,
        )
        return self._resident_flow_buffer

    @staticmethod
    def _normalize_resident_flow(result, destination):
        if isinstance(result, tuple):
            result = result[0]
        if result is None:
            raise RuntimeError("Optical-flow backend returned no resident flow")
        if getattr(result, "handle", None) != getattr(destination, "handle", None):
            from taichi_vision.taichi_algorithm.common import copy_field

            copy_field(result, destination)
            if hasattr(result, "destroy"):
                _facade()._destroy_work_item(result)
        return destination

    def _resident_flow_view(self, owner=None):
        if owner is None:
            owner = getattr(self, "_resident_flow_buffer", None)
        if owner is None or getattr(owner, "handle", None) is None:
            return None
        view = TaichiGPUBuffer(
            owner.size_bytes,
            owner.handle,
            owner.shape,
            dtype=owner.dtype,
            is_vector=owner.is_vector,
            engine=owner.engine,
            is_owner=False,
            host_accessible=owner.host_accessible,
            vector_dim=owner.vector_dim,
        )
        view._parent_ref = owner
        return view

    def _close_resident_flow_buffer(self):
        owners = (
            getattr(self, "_resident_flow_buffer", None),
            getattr(self, "_resident_quantized_flow_buffer", None),
        )
        self._resident_flow_buffer = None
        self._resident_quantized_flow_buffer = None
        for owner in owners:
            if owner is not None and hasattr(owner, "destroy"):
                _facade()._destroy_work_item(owner)

    def _store_quantized_flow(self, taichi_aot, flow_quant):
        """Keep quantized remap flow separate from the AOT ndarray destination."""
        quantized = taichi_aot.upload(flow_quant, is_vector=True)
        previous = getattr(self, "_resident_quantized_flow_buffer", None)
        if previous is not None and previous is not quantized:
            # The previous flow may still be consumed by resident accumulation.
            taichi_aot.engine.sync()
            _facade()._destroy_work_item(previous)
        self._resident_quantized_flow_buffer = quantized
        return quantized
