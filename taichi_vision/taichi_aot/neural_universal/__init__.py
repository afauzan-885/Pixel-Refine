"""Neural universal runtime: one compiled kernel pool serves many ONNX models.

Public API::

    from taichi_vision.taichi_aot.neural_universal import UniversalSession

    session = UniversalSession("model.onnx", backend="cuda")
    (weights,) = session.run(None, {"ref_img": x})
    session.close()

The compiled pool lives alongside WeightNet artifacts at
``pixel_refine_desktop/ui/data/aot_assets/neural/neural_<backend>.tcm`` and is
rebuilt with ``python -m taichi_vision.taichi_aot.neural_universal.compile``.

The archived universal runtime (``taichi_vision/taichi_algorithm/neural/onnx/``)
exposed the names re-exported here. They are preserved so existing callers do
not break:

``UniversalInferenceSession`` / ``UniversalSession``, ``find_universal_tcm``,
``prepare_static_model``, ``collapse_broadcast_shapes``,
``calc_4d_strides`` / ``_calc_4d_strides``, ``DEFAULT_AOT_NEURAL_DIR`` and
``BACKEND_SUBDIRS``.

An exact-profile, opt-in static graph wrapper is available as
``StaticGraphSession``. It uses a model-specific AOT graph only when its
model/target/shape manifest matches; other calls use ``UniversalSession``.
"""

from __future__ import annotations

from .compat import (
    _calc_4d_strides,
    calc_4d_strides,
    collapse_broadcast_shapes,
    prepare_static_model,
)
from .errors import (
    ArtifactError,
    NeuralUniversalError,
    UnsupportedONNXOperatorError,
    UnsupportedStepError,
)
from .registry import OPS, OpSpec, require
from .runtime import (
    BACKEND_SUBDIRS,
    DEFAULT_AOT_NEURAL_DIR,
    DEFAULT_POOL_DIR,
    UniversalInferenceSession,
    UniversalSession,
    find_universal_tcm,
)
from .static_session import StaticGraphSession, StaticWeightNetSession

__all__ = [
    # sessions
    "UniversalSession",
    "UniversalInferenceSession",
    "StaticGraphSession",
    "StaticWeightNetSession",  # backward-compatible alias
    # archived module-level helpers
    "find_universal_tcm",
    "prepare_static_model",
    "collapse_broadcast_shapes",
    "calc_4d_strides",
    "_calc_4d_strides",
    "DEFAULT_AOT_NEURAL_DIR",
    "DEFAULT_POOL_DIR",
    "BACKEND_SUBDIRS",
    # registry
    "OPS",
    "OpSpec",
    "require",
    # errors
    "NeuralUniversalError",
    "UnsupportedONNXOperatorError",
    "UnsupportedStepError",
    "ArtifactError",
]
