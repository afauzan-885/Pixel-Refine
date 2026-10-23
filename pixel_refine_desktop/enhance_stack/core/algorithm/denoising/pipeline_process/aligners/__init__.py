"""Resident aligners extracted from the monolithic pipeline module.

The package stays lazy: importing it must not pull in ``taichi_vision`` or the
engine.  Import the concrete module you need, or resolve a name through
``__getattr__``.
"""

from __future__ import annotations

__all__ = [
    "NoAlignmentGPUAligner",
    "BlockMatchingResidentAligner",
    "LucasKanadeResidentAligner",
    "FarnebackResidentAligner",
    "FeatureMatchingGPUAligner",
    "create_resident_aligner",
]

_SOURCES = {
    "NoAlignmentGPUAligner": ".base",
    "BlockMatchingResidentAligner": ".flow",
    "LucasKanadeResidentAligner": ".flow",
    "FarnebackResidentAligner": ".flow",
    "FeatureMatchingGPUAligner": ".feature",
    "create_resident_aligner": ".factory",
}


def __getattr__(name):
    source = _SOURCES.get(name)
    if source is None:
        raise AttributeError(name)
    from importlib import import_module

    return getattr(import_module(source, __name__), name)
