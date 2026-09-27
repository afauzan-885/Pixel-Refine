"""Splat SR implementation, AOT compiler, and backend runtime modules."""

# Import the lightweight runtime wrapper here.  The JIT/compiler source module
# deliberately blocks Taichi imports in production mode, so it must not be
# imported as a side effect of importing this package.
from .splat_sr_runtime import SplatSRAOTEngine

TaichiSplatSR = SplatSRAOTEngine

__all__ = ["SplatSRAOTEngine", "TaichiSplatSR"]
