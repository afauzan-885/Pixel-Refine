"""Compatibility re-export for the dependency-free backend contract.

The implementation lives at :mod:`taichi_vision.backend_config` so callers
that only need name normalization do not import the AOT package initializer
and accidentally create a native GPU context.
"""

from taichi_vision.backend_config import *  # noqa: F401,F403
from taichi_vision.backend_config import __all__
