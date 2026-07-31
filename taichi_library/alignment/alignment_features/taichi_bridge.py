"""Compatibility bridge for legacy normalize/gamma AOT calls.

The original alignment_features package was removed while the public helper
signatures remained.  These routines preserve the buffer API and perform the
conversion in a deterministic NumPy pass, returning a buffer owned by the
same AOT engine.  A future TCM kernel can replace the internal transform
without changing callers.
"""

from __future__ import annotations

import numpy as np


def _upload_like(src_gpu, array):
    engine = src_gpu.engine
    return engine.upload(np.ascontiguousarray(array), is_vector=array.ndim == 3 and array.shape[-1] in (3, 4))


def normalize_image_gpu(src_gpu, dtype, out_gpu=None):
    data = np.asarray(src_gpu.to_numpy())
    if np.issubdtype(dtype, np.integer):
        scale = float(np.iinfo(dtype).max)
    elif np.issubdtype(dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"Unsupported dtype for normalization: {dtype}")
    result = data.astype(np.float32, copy=False) / np.float32(scale)
    if result.ndim == 2:
        result = np.repeat(result[..., None], 3, axis=-1)
    target = out_gpu if out_gpu is not None else _upload_like(src_gpu, result)
    if out_gpu is not None:
        target.from_numpy(np.ascontiguousarray(result))
    return target


def to_gamma_proxy_gpu(src_gpu, scale=1.0, dst_gpu=None):
    data = np.asarray(src_gpu.to_numpy()).astype(np.float32, copy=False)
    x = data * np.float32(scale)
    mapped = x / np.sqrt(np.float32(1.0) + x * x)
    result = np.power(np.clip(mapped, 0.0, 1.0), np.float32(1.0 / 2.22))
    target = dst_gpu if dst_gpu is not None else _upload_like(src_gpu, result)
    if dst_gpu is not None:
        target.from_numpy(np.ascontiguousarray(result))
    return target
