"""Late-bound access to the resident pipeline facade namespace.

Modules extracted out of ``resident_pipeline`` reach sibling implementations
through :func:`api` instead of importing them directly.  The resident facade
re-exports every symbol, so ``monkeypatch.setattr(resident_pipeline, name, fake)``
keeps reaching the live call path exactly as it did when every symbol shared a
single module.

Call sites on per-frame / per-stage boundaries pay one dict lookup; per-pixel
inner loops keep calling local functions directly and pay nothing.
"""

from __future__ import annotations

import sys
from importlib import import_module

_FACADE_NAME = __name__.rsplit(".", 1)[0] + ".resident_pipeline"


def api():
    """Return the resident facade module, importing it on first use."""
    module = sys.modules.get(_FACADE_NAME)
    if module is None:
        module = import_module(_FACADE_NAME)
    return module


__all__ = ["api"]
