"""Compatibility façade for the relocated Splat SR implementation."""

from .splat_sr import legacy as _implementation

SplatSRAlgorithm = _implementation.SplatSRAlgorithm
main = _implementation.main
running_splatting_sr = _implementation.running_splatting_sr

from .splat_SR import run_splat_sr_pipeline

__all__ = [
    "SplatSRAlgorithm",
    "main",
    "run_splat_sr_pipeline",
    "running_splatting_sr",
]


def __getattr__(name):
    return getattr(_implementation, name)
