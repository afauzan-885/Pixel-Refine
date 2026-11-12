"""Universal kernel pool assembly.

``ALL_KERNELS`` is the single source of truth for what the compiled
``neural_{backend}.tcm`` artifact must contain. The compiler asserts that the
artifact manifest matches this list exactly, so a kernel can never be silently
missing at run time.
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

KERNEL_NAMES = tuple(kernel.__name__ for kernel in ALL_KERNELS)

__all__ = ["ALL_KERNELS", "KERNEL_NAMES"]