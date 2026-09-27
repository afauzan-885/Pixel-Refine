"""Compatibility facade for the canonical resident pipeline package.

The implementation moved to ``denoising.pipeline_process``.  Keeping this
module as a lazy facade preserves older imports while the migration is
validated and prevents two resident executors from diverging again.
"""

from __future__ import annotations

from .pipeline_process import resident_pipeline as _canonical

__all__ = list(getattr(_canonical, "__all__", ()))


def __getattr__(name):
    return getattr(_canonical, name)


def __dir__():
    return sorted(set(__all__) | set(dir(_canonical)))
