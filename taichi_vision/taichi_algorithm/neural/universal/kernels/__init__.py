"""Universal kernel pool assembly.

``ALL_KERNELS`` is the single source of truth for what the compiled
``neural_{backend}.tcm`` artifact must contain. The compiler asserts that the
artifact manifest matches this list exactly, so a kernel can never be silently
missing at run time.

Name introspection: the Rust-engine ``taichi`` 1.8.0 exposes compiled kernels
as ``taichi._api.Kernel`` objects carrying ``.name``, while bodies outside the
supported front-end subset silently fall back to the plain Python function
(which only has ``__name__``). ``kernel_name`` accepts both.
"""

from .attention import ALL_ATTENTION_KERNELS
from .conv import ALL_CONV_KERNELS
from .elementwise import ALL_ELEMENTWISE_KERNELS
from .index import ALL_INDEX_KERNELS
from .linear import ALL_LINEAR_KERNELS
from .macro import ALL_MACRO_KERNELS
from .movement import ALL_MOVEMENT_KERNELS
from .norm import ALL_NORM_KERNELS
from .pool import ALL_POOL_KERNELS
from .reduce import ALL_REDUCE_KERNELS

ALL_KERNELS = (
    ALL_CONV_KERNELS
    + ALL_LINEAR_KERNELS
    + ALL_ELEMENTWISE_KERNELS
    + ALL_REDUCE_KERNELS
    + ALL_NORM_KERNELS
    + ALL_MOVEMENT_KERNELS
    + ALL_POOL_KERNELS
    + ALL_INDEX_KERNELS
    + ALL_ATTENTION_KERNELS
    + ALL_MACRO_KERNELS
)


def kernel_name(kernel) -> str:
    """Return the pool graph name of one kernel object.

    Rust-engine kernels expose ``.name``; silent-fallback plain functions
    expose ``__name__``. Both spellings refer to the same pool graph name.
    """
    name = getattr(kernel, "name", None)
    if isinstance(name, str) and name:
        return name
    return kernel.__name__


KERNEL_NAMES = tuple(kernel_name(kernel) for kernel in ALL_KERNELS)

__all__ = ["ALL_KERNELS", "KERNEL_NAMES", "kernel_name"]