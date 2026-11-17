"""Public neural API: ONNX models on the Taichi runtime, plug and play.

    import taichi_vision.neural as neural

    session = neural.InferenceSession("model.onnx")
    outputs = session.run(None, {"input": array})

This package is the only public entry point for neural inference. Kernel pools,
operator lowerings, fusion planning, TCM artifacts, and buffer dispatch all live
inside ``taichi_vision.taichi_algorithm.neural`` and are not part of this API.

Model availability is reported, never guessed: use :func:`capabilities` and
:func:`describe` to see which execution strategy was chosen and which runtime
features are still missing.
"""

from __future__ import annotations

from .api import (
    InferenceSession,
    capabilities,
    describe,
    find_prebaked_artifact,
    get_available_providers,
    load,
    neural_asset_dir,
    pool_artifact_path,
)
from .capabilities import DEFAULT_NEURAL_DIR, INT64_CANDIDATE_OPS, NATIVE_GRAPH_OPS
from .errors import (
    BackendUnavailable,
    CapabilityMissingError,
    ModelNotRunnable,
    NeuralError,
)
from .options import ExecutionMode, GraphOptimizationLevel, NodeArg, SessionOptions
from .resolver import Resolution, ResolutionRecord, resolve

# `ops` is a module, imported rather than re-exported name by name: a caller writes
# `neural.ops.relu(x)`, and the attribute is the module itself.
from . import ops

#: onnxruntime-compatible alias for :class:`InferenceSession`.
Session = InferenceSession

__all__ = [
    # inference
    "InferenceSession",
    "Session",
    "load",
    # operator-level API
    "ops",
    # introspection
    "describe",
    "capabilities",
    "get_available_providers",
    "resolve",
    "Resolution",
    "ResolutionRecord",
    # onnxruntime-shaped helpers
    "SessionOptions",
    "GraphOptimizationLevel",
    "ExecutionMode",
    "NodeArg",
    # artifacts (public helpers, replace internal imports in applications)
    "DEFAULT_NEURAL_DIR",
    "neural_asset_dir",
    "pool_artifact_path",
    "find_prebaked_artifact",
    "NATIVE_GRAPH_OPS",
    "INT64_CANDIDATE_OPS",
    # errors
    "NeuralError",
    "BackendUnavailable",
    "CapabilityMissingError",
    "ModelNotRunnable",
]
