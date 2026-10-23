"""Backward-compatibility facade for resident WeightNet AOT compiler.

The canonical implementation has moved to:
pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.neural_compiler
"""

from __future__ import annotations

import sys
from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.neural_compiler.compile_resident_weightnet_tcm import (
    DEFAULT_BUNDLE,
    DEFAULT_TCM_DIR,
    compile_single_target,
    main,
)

__all__ = [
    "DEFAULT_BUNDLE",
    "DEFAULT_TCM_DIR",
    "compile_single_target",
    "main",
]

if __name__ == "__main__":
    main()
