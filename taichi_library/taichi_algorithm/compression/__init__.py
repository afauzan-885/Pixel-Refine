"""AOT image-compression kernels.

This package contains device-side transform and quantization stages. Container
and entropy bitstream work is intentionally kept explicit in the public API so
the AOT contract remains inspectable.
"""
import os


from .kernels import JPEG_QUALITY_TABLE, jpeg_prepare_blocks
from .jpeg_grayscale_pipeline import encode_grayscale_taichi
from .jpeg_rgb_pipeline import encode_rgb_taichi
# Import these lazily: the canonical JPEG API reuses compression.kernels, and
# eager package-level imports would create a circular import during startup.
def encode_grayscale_aot(*args, **kwargs):
    from taichi_library.taichi_algorithm.compression.jpeg_aot import encode_grayscale_aot as _impl
    return _impl(*args, **kwargs)


def encode_rgb_aot(*args, **kwargs):
    from taichi_library.taichi_algorithm.compression.jpeg_aot import encode_rgb_aot as _impl
    return _impl(*args, **kwargs)


def jpeg_encode_aot(*args, **kwargs):
    from taichi_library.taichi_algorithm.compression.jpeg_aot import jpeg_encode_aot as _impl
    return _impl(*args, **kwargs)


# Backend-neutral aliases for callers that want the maintained AOT pipeline.
encode_grayscale = encode_grayscale_aot
encode_rgb = encode_rgb_aot
jpeg_encode = jpeg_encode_aot

if os.environ.get("AOT_MODE", "1") == "1":
    # Preserve the historical names while ensuring AOT-mode callers do not
    # accidentally enter the old JIT-only orchestration.
    encode_grayscale_taichi = encode_grayscale_aot
    encode_rgb_taichi = encode_rgb_aot

__all__ = [
    "JPEG_QUALITY_TABLE",
    "jpeg_prepare_blocks",
    "encode_grayscale_taichi",
    "encode_rgb_taichi",
    "encode_grayscale_aot",
    "encode_rgb_aot",
    "jpeg_encode_aot",
    "encode_grayscale",
    "encode_rgb",
    "jpeg_encode",
]
