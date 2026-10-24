"""Static ONNX resident compiler facade.

The canonical implementation lives in
``taichi_vision.taichi_algorithm.denoising.onnx_resident_aot``: the
application-side copy had forked an older ``ResidentONNXGraph`` (without the
leased-invocation lifecycle) while ``compile_resident_onnx`` itself was
byte-identical.  Keeping one compiler removes the ABI drift risk between the
compile CLI and the resident runtime.
"""

from __future__ import annotations

from taichi_vision.taichi_algorithm.denoising.onnx_resident_aot import (
    GRAPH_NAME,
    ResidentONNXGraph,
    compile_resident_onnx,
)

__all__ = [
    "GRAPH_NAME",
    "ResidentONNXGraph",
    "compile_resident_onnx",
]
