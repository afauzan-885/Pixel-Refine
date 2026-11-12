"""Canonical Taichi Vision runtime package."""

from __future__ import annotations

__all__ = []

# Public algorithm namespace
# Usage:
#   from taichi_vision import algorithm as alg
#   alg.akaze(...) / alg.AKAZE(...)
from . import taichi_algorithm as algorithm

__all__ = ["algorithm"]
