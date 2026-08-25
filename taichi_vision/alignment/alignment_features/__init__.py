"""Compatibility helpers for legacy AOT alignment APIs.

The maintained implementation lives in
``taichi_vision.taichi_algorithm.alignment.taichi_bridge``.  This namespace
is intentionally kept as a tiny import shim so older application code keeps
working while the algorithm source has a single home.
"""

from taichi_vision.taichi_algorithm.alignment.taichi_bridge import (
    normalize_image_gpu,
    to_gamma_proxy_gpu,
)

__all__ = ["normalize_image_gpu", "to_gamma_proxy_gpu"]
