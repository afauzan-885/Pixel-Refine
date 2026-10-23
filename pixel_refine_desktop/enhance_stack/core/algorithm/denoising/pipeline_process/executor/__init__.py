"""Resident executor extracted from the monolithic pipeline module.

The package stays lazy so importing it never initialises the compute engine.
"""

from __future__ import annotations

__all__ = ["run_gpu_resident_pipeline"]


def __getattr__(name):
    if name != "run_gpu_resident_pipeline":
        raise AttributeError(name)
    from .run import run_gpu_resident_pipeline

    return run_gpu_resident_pipeline
