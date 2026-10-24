"""
Taichi AOT Native Optical Flow Alignment Engine (compute_flow.tcm).

Compatibility facade: the implementation lives in :mod:`.flow_aligner`.
Keeping the symbols re-exported here preserves every existing import and
``monkeypatch.setattr(flownet_inference, "AOTOpticalFlowAligner", ...)``.
"""

from .flow_aligner import AOTOpticalFlowAligner, load_compute_flow_module

__all__ = [
    "AOTOpticalFlowAligner",
    "load_compute_flow_module",
]
