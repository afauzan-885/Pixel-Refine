"""Safe block-oriented composition for large image pipelines.

This scheduler intentionally composes the existing public algorithm callables
instead of recording one oversized graphics graph.  Each callable may use the
normal AOT block executor; intermediate host arrays are released as soon as
the next stage owns the result.  The API is internal and does not alter the
algorithm functions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Any
import gc


@dataclass(frozen=True)
class PipelineStage:
    name: str
    operation: Callable[[Any], Any]

    def __post_init__(self):
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("pipeline stage name must be a non-empty string")
        if not callable(self.operation):
            raise TypeError("pipeline stage operation must be callable")


def run_block_pipeline(source, stages: Iterable[PipelineStage], *,
                       block_size: int = 256, threshold_bytes: int = 1):
    """Run a dependency-ordered pipeline through safe block-capable APIs.

    The scheduler is deliberately host-array based: this avoids mixing native
    OpenGL graph recording with host fallbacks.  Existing operations decide
    their own halo and full-frame policy, while this function controls memory
    pressure and stage ordering.
    """
    if block_size <= 0 or threshold_bytes < 0:
        raise ValueError("block_size must be positive and threshold_bytes non-negative")
    import taichi_library.taichi_aot as aot
    previous = aot.engine.get_block_config()
    aot.set_block_mode(True, size=int(block_size),
                       threshold_bytes=int(threshold_bytes))
    value = source
    try:
        for stage in stages:
            if not isinstance(stage, PipelineStage):
                raise TypeError("stages must contain PipelineStage values")
            next_value = stage.operation(value)
            if next_value is None:
                raise RuntimeError(f"pipeline stage '{stage.name}' returned None")
            if next_value is not value:
                del value
                gc.collect()
            value = next_value
        return value
    finally:
        aot.engine.configure_blocks(**previous.__dict__)
