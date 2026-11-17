"""Canonical Taichi Vision runtime package."""

from __future__ import annotations

__all__ = []

# Public algorithm namespace
# Usage:
#   from taichi_vision import algorithm as alg
#   alg.akaze(...) / alg.AKAZE(...)
from . import taichi_algorithm as algorithm

# Public neural inference entry point (ONNX plug and play).
# Usage:
#   import taichi_vision.neural as neural
#   session = neural.InferenceSession("model.onnx")
from . import neural

__all__ = ["algorithm", "neural"]
