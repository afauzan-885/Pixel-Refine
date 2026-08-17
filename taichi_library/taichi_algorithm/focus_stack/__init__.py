"""Focus-stacking family APIs.

The package is intentionally family-local: importing it does not alter the
legacy :mod:`taichi_algorithm` facade.  Use :func:`focus_stack` for a complete
stack and :func:`focus_measure` for individual quality maps.
"""

from .pipeline import FocusStackResult, focus_measure, focus_stack

__all__ = ["FocusStackResult", "focus_measure", "focus_stack"]

