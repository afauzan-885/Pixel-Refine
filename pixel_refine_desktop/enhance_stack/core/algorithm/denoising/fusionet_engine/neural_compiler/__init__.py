"""Compiler tools and resident graph runtime for WeightNet neural models."""

from .onnx_resident_aot import (
    GRAPH_NAME,
    compile_resident_onnx,
    ResidentONNXGraph,
)
from .compile_resident_weightnet_tcm import compile_single_target

__all__ = [
    "GRAPH_NAME",
    "compile_resident_onnx",
    "ResidentONNXGraph",
    "compile_single_target",
]

