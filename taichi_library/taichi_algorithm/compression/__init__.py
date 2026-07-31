"""AOT image-compression kernels.

This package contains device-side transform and quantization stages. Container
and entropy bitstream work is intentionally kept explicit in the public API so
the AOT contract remains inspectable.
"""

from .kernels import JPEG_QUALITY_TABLE, jpeg_prepare_blocks
from .jpeg_grayscale_pipeline import encode_grayscale_taichi
from .jpeg_rgb_pipeline import encode_rgb_taichi

__all__ = [
    "JPEG_QUALITY_TABLE",
    "jpeg_prepare_blocks",
    "encode_grayscale_taichi",
    "encode_rgb_taichi",
]

__all__ = ["JPEG_QUALITY_TABLE", "jpeg_prepare_blocks"]
