"""Resident aligner factory and pipeline-runtime bookkeeping helpers."""

from __future__ import annotations

from functools import wraps
from typing import Optional, Tuple

from taichi_vision.taichi_aot import TaichiGPUBuffer

from ....pipeline_runtime import current_pipeline_runtime
from ..facade import api as _facade

__all__ = [
    "create_resident_aligner",
    "_component_factory",
    "_buffer_session",
    "_managed_api",
    "_track_gpu_result",
    "_own_component",
    "_export_result",
    "_destroy_work_item",
    "_destroy_work_item_except",
]


def _component_factory(factory):
    @wraps(factory)
    def build(*args, **kwargs):
        return _facade()._own_component(factory(*args, **kwargs))
    return build


@_component_factory
def create_resident_aligner(
    alignment_plan: str,
    ref_analysis_gpu: TaichiGPUBuffer,
    *,
    work_scale: float = 0.50,
    full_shape: Optional[Tuple[int, int]] = None,
    alignment_config: Optional[dict] = None,
    noise_score: Optional[float] = None,
):
    """Factory creating the appropriate GPU-resident aligner instance."""
    from ....catalog import get_spec

    spec = get_spec("alignment", alignment_plan or "none", context="resident")
    route = spec.resident_route
    if route == "none":
        print("[GPU Pipeline] Aligner: No Alignment (Bypass)")
        return _facade().NoAlignmentGPUAligner(ref_analysis_gpu)
    elif route in ("ofb", "akaze"):
        print(f"[GPU Pipeline] Aligner: Feature Matching ({spec.name})")
        return _facade().FeatureMatchingGPUAligner(
            ref_analysis_gpu,
            feature_type=route,
            work_scale=work_scale,
            full_shape=full_shape,
            feature_config=alignment_config,
        )
    elif route == "block_matching":
        print("[GPU Pipeline] Aligner: Block Matching GPU")
        return _facade().BlockMatchingResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "lucas_kanade":
        print("[GPU Pipeline] Aligner: Lucas Kanade GPU")
        return _facade().LucasKanadeResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "farneback":
        return _facade().FarnebackResidentAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            alignment_config=alignment_config,
        )
    elif route == "block_flow":
        print(f"[GPU Pipeline] Aligner: Dense Optical Flow Adaptive Multi-Tile ({spec.name})")
        from ...fusionet_engine.flownet_inference import AOTOpticalFlowAligner

        smooth = _facade()._parse_bool((alignment_config or {}).get("smooth", True), default=True)

        return AOTOpticalFlowAligner(
            ref_analysis_gpu,
            work_scale=work_scale,
            full_shape=full_shape,
            tile_size=32,
            noise_score=noise_score,
            smooth=smooth,
            adaptive=True,
        )

    raise ValueError(f"No resident aligner registered for '{spec.name}'")


def _buffer_session():
    runtime = current_pipeline_runtime()
    return runtime.buffer_session if runtime is not None else None


def _managed_api(api):
    runtime = current_pipeline_runtime()
    if runtime is None:
        return api
    managed_api = runtime.managed_api
    return managed_api(api) if managed_api is not None else api


def _track_gpu_result(result):
    runtime = current_pipeline_runtime()
    if runtime is None:
        return result
    return runtime.ensure_session().track_result(result)


def _own_component(component, *, releaser=None):
    runtime = current_pipeline_runtime()
    return runtime.own(component, releaser=releaser) if runtime is not None else component


def _export_result(result):
    runtime = current_pipeline_runtime()
    if runtime is None:
        return result
    session = runtime.ensure_session()
    return session.detach(runtime.own(result))


def _destroy_work_item(item):
    """Release work buffers through the active session when one exists."""
    if item is None:
        return
    runtime = current_pipeline_runtime()
    session = runtime.buffer_session if runtime is not None else None
    if session is not None:
        session.release_tree(item)
        return
    if isinstance(item, tuple):
        for el in item:
            if el is not None and hasattr(el, "destroy"):
                try:
                    el.destroy()
                except Exception:
                    pass
    elif hasattr(item, "destroy"):
        try:
            item.destroy()
        except Exception:
            pass


def _destroy_work_item_except(item, protected):
    """Release queued work except a carrier shared with another stage."""
    if item is None or item is protected:
        return

    seen = set()

    def without_protected(value):
        if value is None or value is protected or id(value) in seen:
            return None
        if isinstance(value, (tuple, list)):
            seen.add(id(value))
            retained = tuple(
                child for child in (without_protected(item) for item in value)
                if child is not None
            )
            return retained or None
        seen.add(id(value))
        return value

    unprotected = without_protected(item)
    if unprotected is None:
        return
    runtime = current_pipeline_runtime()
    session = runtime.buffer_session if runtime is not None else None
    if session is not None:
        session.release_tree(unprotected)
        return
    values = unprotected if isinstance(unprotected, (tuple, list)) else (unprotected,)
    for value in values:
        _facade()._destroy_work_item(value)
