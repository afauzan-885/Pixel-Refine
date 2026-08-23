"""Canonical Taichi Vision runtime package.

The project was historically published under ``taichi_library``.  A number
of internal modules still use that absolute name for compatibility with old
serialized graphs and application imports.  Registering this package under
the retired name keeps those imports working without requiring a duplicate
source tree or changing the public API.
"""

from __future__ import annotations

import sys as _sys

_sys.modules.setdefault("taichi_library", _sys.modules[__name__])

__all__ = []
