"""Shared low-level helpers used by image-processing algorithms.

These helpers contain backend-neutral data rules. Processing adapters keep
their own algorithms, while ordering, dtype restoration, memory reporting,
and batch overrides stay consistent across CPU, GPU, AI, and optical-flow
paths.
"""

import psutil
import numpy as np


def get_ram_usage():
    """Return the current process RSS in MiB."""
    return psutil.Process().memory_info().rss / 1024 / 1024


def sorted_image_keys(h5f):
    """Return HDF5 image datasets in numeric order."""
    return sorted(
        (key for key in h5f.keys() if key.startswith("image_")),
        key=lambda item: int(item.split("_", 1)[1]),
    )


def restore_output_dtype(image, dtype):
    """Restore a fused image to its reference dtype with safe clipping."""
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        if image.dtype.kind == "f" and float(np.nanmax(image)) <= 1.5:
            image = image * float(info.max)
        image = np.clip(image, info.min, info.max)
    return image.astype(dtype, copy=False)


def resolve_batch_config(ctx, loader, parameter_key="similarity_params"):
    """Load defaults and overlay per-batch parameters when present."""
    config = loader()
    batch_params = getattr(ctx, "params", {}).get(parameter_key)
    if isinstance(batch_params, dict):
        config.update(batch_params)
    return config
