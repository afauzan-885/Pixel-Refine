"""Resident-buffer wrappers for FusionNet multi-patch AOT graphs."""

from __future__ import annotations

import numpy as np


TOPK_GRAPH = "deno_multi_patch_topk_f32_v1"
DENSE_FLOW_GRAPH = "deno_multi_patch_compose_dense_flow_f32_v1"


def select_multi_patch_topk_aot(reference, candidate, offsets, max_neighbors=4, cell_size=1):
    """Return resident ``(K,ceil(H/cell),ceil(W/cell))`` candidate indices."""
    from taichi_vision.taichi_algorithm.aot_api import TaichiGPUBuffer, _mod, engine

    owned = []
    try:
        if isinstance(reference, TaichiGPUBuffer):
            reference_buffer = reference
        else:
            reference_buffer = engine.upload(
                np.ascontiguousarray(reference, dtype=np.float32), is_vector=False
            )
            owned.append(reference_buffer)
        if isinstance(candidate, TaichiGPUBuffer):
            candidate_buffer = candidate
        else:
            candidate_buffer = engine.upload(
                np.ascontiguousarray(candidate, dtype=np.float32), is_vector=False
            )
            owned.append(candidate_buffer)
        if reference_buffer.is_vector:
            reference_buffer = reference_buffer.view_as_vector(False)
        if candidate_buffer.is_vector:
            candidate_buffer = candidate_buffer.view_as_vector(False)

        if len(reference_buffer.shape) != 3 or tuple(reference_buffer.shape) != tuple(candidate_buffer.shape):
            raise ValueError("multi-patch AOT inputs must be matching CHW buffers")
        channels, height, width = (int(value) for value in reference_buffer.shape)
        offset_array = np.ascontiguousarray(offsets, dtype=np.int32)
        if offset_array.ndim != 2 or offset_array.shape[1] != 2:
            raise ValueError("offsets must have shape (N,2)")
        neighbor_count = min(int(max_neighbors), int(offset_array.shape[0]))
        cell_size = int(cell_size)
        if not 1 <= neighbor_count <= 16:
            raise ValueError("max_neighbors must be between 1 and 16")
        if cell_size <= 0:
            raise ValueError("cell_size must be positive")
        offsets_buffer = engine.upload(offset_array, is_vector=False)
        owned.append(offsets_buffer)
        indices = engine.allocate(
            (neighbor_count, (height + cell_size - 1) // cell_size,
             (width + cell_size - 1) // cell_size), dtype=np.int32
        )
        owned.append(indices)
        _mod("multi_patch").run(
            TOPK_GRAPH,
            reference=reference_buffer,
            candidate=candidate_buffer,
            offsets=offsets_buffer,
            indices=indices,
            height=height,
            width=width,
            channels=channels,
            candidate_count=int(offset_array.shape[0]),
            neighbor_count=neighbor_count,
            cell_size=cell_size,
        )
        # Transfer ownership of the result to the caller.
        owned.remove(indices)
        return indices
    finally:
        for buffer in reversed(owned):
            try:
                buffer.destroy()
            except Exception:
                pass


def compose_multi_patch_dense_flow_aot(
    rank_indices, offsets, base_flow, *, full_shape
):
    """Compose one rank map with a resident dense flow; return vector flow GPU buffer."""
    from taichi_vision.taichi_algorithm.aot_api import TaichiGPUBuffer, _mod, engine

    if not isinstance(base_flow, TaichiGPUBuffer):
        raise TypeError("base_flow must be a resident TaichiGPUBuffer")
    indices_host = np.ascontiguousarray(rank_indices, dtype=np.int32)
    if indices_host.ndim != 2:
        raise ValueError("rank_indices must be a 2D map")
    offsets_host = np.ascontiguousarray(offsets, dtype=np.int32)
    if offsets_host.ndim != 2 or offsets_host.shape[1] != 2:
        raise ValueError("offsets must have shape (N,2)")
    if len(base_flow.shape) != 3 or int(base_flow.shape[-1]) != 2:
        raise ValueError("base_flow must have shape (H,W,2)")

    flow_height, flow_width = (int(value) for value in base_flow.shape[:2])
    index_height, index_width = (int(value) for value in indices_host.shape)
    full_height, full_width = (int(value) for value in full_shape)
    if min(flow_height, flow_width, full_height, full_width) <= 0:
        raise ValueError("flow and full-resolution shapes must be positive")
    indices_buffer = engine.upload(indices_host, is_vector=False)
    offsets_buffer = engine.upload(offsets_host, is_vector=False)
    output_flow = engine.allocate((flow_height, flow_width, 2), is_vector=True)
    try:
        flow_arg = base_flow.view_as_vector(False) if base_flow.is_vector else base_flow
        output_arg = output_flow.view_as_vector(False)
        _mod("multi_patch").run(
            DENSE_FLOW_GRAPH,
            rank_indices=indices_buffer,
            offsets=offsets_buffer,
            base_flow=flow_arg,
            output_flow=output_arg,
            index_height=index_height,
            index_width=index_width,
            flow_height=flow_height,
            flow_width=flow_width,
            full_height=full_height,
            full_width=full_width,
            candidate_count=int(offsets_host.shape[0]),
        )
        return output_flow
    except Exception:
        output_flow.destroy()
        raise
    finally:
        indices_buffer.destroy()
        offsets_buffer.destroy()

