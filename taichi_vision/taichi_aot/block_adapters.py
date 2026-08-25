"""Parity-qualified adapters for the smallest local block operations.

The legacy AOT API already owns tile executors for a handful of data-movement
and pointwise operations.  This module supplies the missing *contract* around
those executors without changing the public dispatch path.  Registration is
explicit (``register_low_risk_block_adapters``) and does not mutate
``AUTO_BLOCK_SAFE`` or the maintained operation contracts.

Only CPU semantic parity is qualified here.  The callbacks are deterministic
NumPy oracles used to compare a full-frame evaluation with the exact same
operation evaluated over a ``BlockGrid``.  Sliding-window NCC/ZNCC uses a
derived output grid and an explicit template-footprint halo; stitch adapters
use a canonical ordered overlap reduction.  Both retain the same fail-closed
semantic-only rule.  No Vulkan/OpenGL/CUDA parity is
claimed: graphics adapters need their own native-device evidence before they
can be added to the backend capability map.

Callback protocol
-----------------

``reader(context, block)`` returns a :class:`PartitionContext` containing the
input windows for one block.  ``runner(context)`` computes one tile,
``validator(context, result)`` validates its shape/dtype, and
``merger(output, result, block)`` publishes the tile core into the output.
The protocol is intentionally small and backend-neutral so the future
automatic planner can use it without importing the algorithm facade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence
import inspect
import threading

import numpy as np

from .block import (
    BackendCapability,
    BlockAdapter,
    BlockGrid,
    BlockSpec,
    BorderPolicy,
    HaloPolicy,
    MergePolicy,
    OperationContract,
    PartitionStrategy,
    ReductionPolicy,
    ShapeTransform,
    canonical_operation_name,
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    legacy_partition_evidence,
    lookup_block_adapter,
    operation_capability,
    operation_contract,
    operation_path,
    register_block_adapter,
)


@dataclass(frozen=True)
class PartitionContext:
    """Input window and metadata passed between adapter callbacks."""

    operation: str
    inputs: tuple[np.ndarray, ...]
    block: Optional[BlockSpec] = None
    full_shape: Optional[tuple[int, ...]] = None
    params: Mapping[str, Any] = field(default_factory=dict)
    # Coordinate-domain adapters may produce a different output shape than
    # their source frame.  These fields are additive and intentionally
    # optional so the original local/stencil callback protocol remains
    # backwards compatible.
    output_shape: Optional[tuple[int, ...]] = None
    stage: int = 0


# Adapter registration is intentionally lazy.  Importing ``block_adapters``
# must remain cheap and, more importantly, must not change the historical
# empty-registry behaviour used by diagnostics and tests.  The compute_block
# bridge calls ``ensure_default_block_adapters`` only after the caller has
# explicitly selected a known operation (or an exact registered operation
# name); the normal undecorated/generic path is therefore untouched.
_DEFAULT_ADAPTERS_LOCK = threading.RLock()
_DEFAULT_ADAPTERS_INITIALIZED = False
_DEFAULT_ADAPTER_REGISTRATION_ERRORS: dict[str, str] = {}


def ensure_default_block_adapters(
    operation: Optional[str] = None,
    *,
    replace: bool = False,
) -> Optional[BlockAdapter | Mapping[str, BlockAdapter]]:
    """Lazily register all maintained semantic adapters.

    The function is deliberately idempotent and best-effort.  A registration
    error in one optional adapter family is recorded and does not make an
    unrelated explicitly selected operation unusable; the dispatcher still
    applies the normal backend/parity gate and falls back to the original
    same-backend full-frame call when that operation is unavailable.

    ``operation`` returns the canonical adapter (or ``None``); omitting it
    returns a snapshot of all adapters registered by this helper.  Native
    evidence and ``AUTO_BLOCK_SAFE`` are never modified here.
    """

    global _DEFAULT_ADAPTERS_INITIALIZED
    canonical = canonical_operation_name(operation) if operation else None
    with _DEFAULT_ADAPTERS_LOCK:
        if not _DEFAULT_ADAPTERS_INITIALIZED:
            # Discover registration helpers at call time so newly added
            # adapter tranches participate without a second central list.
            # Imported ``register_block_adapter`` does not match this suffix.
            helpers = []
            for name, value in sorted(globals().items()):
                if not name.startswith("register_") or not name.endswith("_adapters"):
                    continue
                if name == "register_block_adapters":
                    continue
                if not callable(value):
                    continue
                helpers.append((name, value))
            for name, helper in helpers:
                try:
                    signature = inspect.signature(helper)
                    if "replace" in signature.parameters:
                        helper(replace=replace)
                    else:
                        helper()
                except Exception as exc:
                    _DEFAULT_ADAPTER_REGISTRATION_ERRORS[name] = (
                        f"{type(exc).__name__}: {exc}"
                    )
            _DEFAULT_ADAPTERS_INITIALIZED = True

        if canonical:
            return lookup_block_adapter(canonical)
        # ``lookup_block_adapter`` is intentionally not exposed as a mutable
        # registry; this snapshot is enough for diagnostics and callers that
        # want to know what lazy initialization populated.
        from .block import registered_block_adapters

        return dict(registered_block_adapters())


def default_block_adapter_registration_errors() -> Mapping[str, str]:
    """Return registration errors captured by the lazy default helper."""

    with _DEFAULT_ADAPTERS_LOCK:
        return dict(_DEFAULT_ADAPTER_REGISTRATION_ERRORS)


def _context_value(context: Any, name: str, default: Any = None) -> Any:
    if isinstance(context, Mapping):
        return context.get(name, default)
    return getattr(context, name, default)


def _as_inputs(context: Any) -> tuple[np.ndarray, ...]:
    values = _context_value(context, "inputs", ())
    return tuple(np.asarray(value) for value in values)


def _as_params(context: Any) -> Mapping[str, Any]:
    values = _context_value(context, "params", {})
    if not values:
        metadata = _context_value(context, "metadata", {})
        if isinstance(metadata, Mapping):
            values = metadata.get("params", {})
    return values if isinstance(values, Mapping) else {}


def _copy_reference(array: np.ndarray) -> np.ndarray:
    return np.array(array, copy=True, order="C")


def _absdiff_reference(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    if first.shape != second.shape:
        raise ValueError("absdiff inputs must have matching shape")
    # Graphics and CPU integer graphs compute the absolute difference in a
    # widened type.  Widen first so unsigned subtraction cannot wrap around.
    if np.issubdtype(first.dtype, np.integer):
        values = np.abs(first.astype(np.int64) - second.astype(np.int64))
        info = np.iinfo(first.dtype)
        values = np.clip(values, info.min, info.max)
        return values.astype(first.dtype, copy=False)
    return np.abs(first - second).astype(first.dtype, copy=False)


def _rgb2gray_reference(array: np.ndarray) -> np.ndarray:
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("rgb2gray expects an HxWx3 array")
    if np.issubdtype(array.dtype, np.integer):
        values = array.astype(np.int64, copy=False)
        # This is the integer graph used by common.tcm:
        # (306*R + 601*G + 117*B) >> 10.
        gray = (306 * values[..., 0] + 601 * values[..., 1] + 117 * values[..., 2]) >> 10
        info = np.iinfo(array.dtype)
        return np.clip(gray, info.min, info.max).astype(array.dtype, copy=False)
    values = array.astype(np.float32, copy=False)
    return (
        0.299 * values[..., 0]
        + 0.587 * values[..., 1]
        + 0.114 * values[..., 2]
    ).astype(array.dtype, copy=False)


def _split_reference(array: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("split_3ch expects an HxWx3 array")
    return tuple(np.ascontiguousarray(array[..., index]) for index in range(3))  # type: ignore[return-value]


def _merge_reference(
    first: np.ndarray, second: np.ndarray, third: np.ndarray
) -> np.ndarray:
    if first.ndim != 2 or first.shape != second.shape or first.shape != third.shape:
        raise ValueError("merge_3ch inputs must be matching 2D arrays")
    if first.dtype != second.dtype or first.dtype != third.dtype:
        raise ValueError("merge_3ch inputs must have matching dtype")
    return np.ascontiguousarray(np.stack((first, second, third), axis=-1))


def _extract_reference(array: np.ndarray, channel: int) -> np.ndarray:
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("extract_channel expects an HxWx3 array")
    channel = int(channel)
    if channel not in (0, 1, 2):
        raise ValueError("channel index must be in [0, 2]")
    return np.ascontiguousarray(array[..., channel])


def _insert_reference(
    source: np.ndarray, destination: np.ndarray, channel: int
) -> np.ndarray:
    if source.ndim != 2 or destination.ndim != 3 or destination.shape[2] != 3:
        raise ValueError("insert_channel expects a 2D source and HxWx3 destination")
    if source.shape != destination.shape[:2] or source.dtype != destination.dtype:
        raise ValueError("insert_channel source and destination must match")
    channel = int(channel)
    if channel not in (0, 1, 2):
        raise ValueError("channel index must be in [0, 2]")
    result = np.array(destination, copy=True, order="C")
    result[..., channel] = source
    return result


def _cvt_color_reference(array: np.ndarray, code: int) -> np.ndarray:
    if array.ndim != 3 or array.shape[2] != 3:
        raise ValueError("cvtColor expects an HxWx3 array")
    values = array.astype(np.float32, copy=False)
    code = int(code)
    # OpenCV constants used by aot_api: BGR2GRAY=6, RGB2GRAY=7.
    if code == 6:
        r, g, b = values[..., 2], values[..., 1], values[..., 0]
    elif code == 7:
        r, g, b = values[..., 0], values[..., 1], values[..., 2]
    else:
        raise ValueError(f"unsupported cvtColor code: {code}")
    return (0.299 * r + 0.587 * g + 0.114 * b).astype(np.float32, copy=False)


def _enhance_grayscale_reference(
    source: np.ndarray,
    blurred: np.ndarray,
    lut: np.ndarray,
    micro_contrast: float,
    clarity: float,
    noise_coring: float,
) -> np.ndarray:
    if source.shape != blurred.shape or source.ndim != 2:
        raise ValueError("enhance_grayscale inputs must be matching 2D arrays")
    table = np.asarray(lut, dtype=np.float32)
    if table.ndim != 1 or table.size < 256:
        raise ValueError("enhance_grayscale LUT must contain at least 256 values")
    source = np.asarray(source, dtype=np.float32)
    blurred = np.asarray(blurred, dtype=np.float32)
    difference = source - blurred
    magnitude = np.abs(difference)
    noise = float(noise_coring)
    attenuation = np.where(
        magnitude < noise,
        magnitude / max(noise, 1.0e-10),
        1.0,
    )
    shaped = difference * attenuation / (1.0 + magnitude * 5.0)
    midtone = 16.0 * source * source * (1.0 - source) * (1.0 - source)
    enhanced = source + shaped * float(micro_contrast) + shaped * float(clarity) * midtone
    indices = np.clip((enhanced * 255.0).astype(np.int32), 0, 255)
    return np.ascontiguousarray(table[indices], dtype=np.float32)


# ---------------------------------------------------------------------------
# Local/stencil semantic oracles
# ---------------------------------------------------------------------------
#
# The public image-processing wrappers already own halo-aware ``_run_blockwise``
# executors.  The helpers below intentionally mirror only the bounded parameter
# subset used by the parity harness.  They are semantic CPU oracles; they do
# not promote an operation to a native backend and they fail closed for dynamic
# contracts (for example a guided-filter radius other than one).


def _edge_pad(array: np.ndarray, radius: int) -> np.ndarray:
    """Pad an image with the same replicate border used by local AOT graphs."""

    radius = int(radius)
    if radius <= 0:
        return np.asarray(array)
    return np.pad(
        np.asarray(array),
        ((radius, radius), (radius, radius))
        + ((0, 0),) * max(0, np.asarray(array).ndim - 2),
        mode="edge",
    )


def _stencil_reference(
    array: np.ndarray,
    kernel: np.ndarray,
    *,
    mode: str = "sum",
    border: str = "edge",
) -> np.ndarray:
    """Apply a small 2-D kernel to a scalar or HxWxC array.

    A loop is deliberate here.  These functions are test/reference code and a
    straightforward implementation makes the halo/core mapping auditable.
    """

    source = np.asarray(array, dtype=np.float32)
    if source.ndim not in (2, 3):
        raise ValueError("stencil input must be a 2D or HxWxC array")
    table = np.asarray(kernel, dtype=np.float32)
    if table.ndim != 2 or table.shape[0] != table.shape[1] or table.shape[0] % 2 == 0:
        raise ValueError("stencil kernel must be a square odd 2D array")
    radius = table.shape[0] // 2
    if border == "reflect":
        padded = np.pad(
            source,
            ((radius, radius), (radius, radius))
            + ((0, 0),) * max(0, source.ndim - 2),
            mode="reflect",
        )
    else:
        padded = _edge_pad(source, radius)
    height, width = source.shape[:2]
    output = np.empty_like(source, dtype=np.float32)
    for row in range(height):
        for col in range(width):
            window = padded[row : row + 2 * radius + 1, col : col + 2 * radius + 1]
            if source.ndim == 2:
                values = window
                if mode == "min":
                    output[row, col] = np.min(values[table > 0])
                elif mode == "max":
                    output[row, col] = np.max(values[table > 0])
                else:
                    output[row, col] = np.sum(values * table)
            else:
                values = window
                if mode == "min":
                    output[row, col, :] = np.min(
                        values[table > 0], axis=0
                    )
                elif mode == "max":
                    output[row, col, :] = np.max(
                        values[table > 0], axis=0
                    )
                else:
                    output[row, col, :] = np.sum(
                        values * table[..., None], axis=(0, 1)
                    )
    return np.ascontiguousarray(output, dtype=np.float32)


# ---------------------------------------------------------------------------
# Legacy local/stencil semantic oracles
# ---------------------------------------------------------------------------
#
# The public AOT facade already owns halo-aware executors for these operations
# (``_run_blockwise``, ``_run_blockwise_pair`` and the flow/demosaic helpers).
# Keep the semantic references here deliberately independent from those
# executors.  Registration below is CPU-only and explicit; it does not alter
# ``AUTO_BLOCK_SAFE`` or add native GPU evidence.  Every operation rejects the
# parameter ranges which the maintained graph cannot represent so a future
# planner cannot silently tile a different algorithm.


def _legacy_local_source(array: Any, operation: str, *, channels: Optional[set[int]] = None) -> np.ndarray:
    values = np.asarray(array)
    if values.ndim not in (2, 3) or values.size == 0:
        raise ValueError(f"{operation} expects a non-empty 2D or HxWxC image")
    if values.ndim == 3 and channels is not None and int(values.shape[2]) not in channels:
        allowed = ", ".join(str(value) for value in sorted(channels))
        raise ValueError(f"{operation} supports only channel counts {{{allowed}}}")
    if not np.issubdtype(values.dtype, np.number):
        raise TypeError(f"{operation} input must be numeric")
    result = np.ascontiguousarray(values, dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError(f"{operation} input must contain only finite values")
    return result


def _gaussian_weights_reference(sigma: float, radius: int) -> np.ndarray:
    sigma = float(sigma)
    radius = int(radius)
    if not np.isfinite(sigma) or sigma <= 0.0:
        raise ValueError("gaussian_blur sigma must be finite and positive")
    # The compiled Gaussian graph statically unrolls k=1..16.
    if radius < 0 or radius > 16:
        raise ValueError("gaussian_blur supports radius in [0, 16]")
    weights = np.exp(
        -np.arange(radius + 1, dtype=np.float32) ** 2
        / np.float32(2.0 * sigma * sigma)
    ).astype(np.float32)
    normalizer = np.float32(weights[0] + np.float32(2.0) * np.sum(weights[1:], dtype=np.float32))
    if not np.isfinite(normalizer) or normalizer <= 0.0:
        raise ValueError("gaussian_blur weights are invalid")
    return np.ascontiguousarray(weights / normalizer, dtype=np.float32)


def _gaussian_blur_reference(
    array: np.ndarray,
    *,
    sigma: float = 1.0,
    kernel_size: int = 7,
) -> np.ndarray:
    """Separable REFLECT_101 Gaussian matching ``gaussian.py`` graphs."""

    source = _legacy_local_source(array, "gaussian_blur")
    kernel_size = int(kernel_size)
    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError("gaussian_blur kernel_size must be a positive odd integer")
    radius = kernel_size // 2
    weights = _gaussian_weights_reference(sigma, radius)
    height, width = source.shape[:2]
    horizontal = np.empty_like(source, dtype=np.float32)
    vertical = np.empty_like(source, dtype=np.float32)
    for row in range(height):
        for col in range(width):
            value = source[row, _reflect101_index(col, width)] * weights[0]
            for offset in range(1, radius + 1):
                weight = weights[offset]
                value = value + (
                    source[row, _reflect101_index(col - offset, width)]
                    + source[row, _reflect101_index(col + offset, width)]
                ) * weight
            horizontal[row, col] = value
    for row in range(height):
        for col in range(width):
            value = horizontal[_reflect101_index(row, height), col] * weights[0]
            for offset in range(1, radius + 1):
                weight = weights[offset]
                value = value + (
                    horizontal[_reflect101_index(row - offset, height), col]
                    + horizontal[_reflect101_index(row + offset, height), col]
                ) * weight
            vertical[row, col] = value
    return np.ascontiguousarray(vertical, dtype=np.float32)


def _box_filter_reference(
    array: np.ndarray,
    *,
    kernel_size: int = 3,
) -> np.ndarray:
    """Replicate-border box filter matching the smoothing AOT graphs."""

    source = _legacy_local_source(array, "box_filter")
    kernel_size = int(kernel_size)
    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError("box_filter kernel_size must be a positive odd integer")
    radius = kernel_size // 2
    if radius > 32:
        raise ValueError("box_filter radius is too large for the semantic adapter")
    height, width = source.shape[:2]
    horizontal = np.empty_like(source, dtype=np.float32)
    vertical = np.empty_like(source, dtype=np.float32)
    divisor = np.float32(kernel_size)
    for row in range(height):
        for col in range(width):
            value = np.zeros(source.shape[2:], dtype=np.float32)
            for offset in range(-radius, radius + 1):
                value = value + source[row, max(0, min(width - 1, col + offset))]
            horizontal[row, col] = value / divisor
    for row in range(height):
        for col in range(width):
            value = np.zeros(source.shape[2:], dtype=np.float32)
            for offset in range(-radius, radius + 1):
                value = value + horizontal[max(0, min(height - 1, row + offset)), col]
            vertical[row, col] = value / divisor
    return np.ascontiguousarray(vertical, dtype=np.float32)


def _median_filter_reference(
    array: np.ndarray,
    *,
    kernel_size: int = 3,
) -> np.ndarray:
    """Clamp-border independent-channel 3x3 median matching median.tcm."""

    source = _legacy_local_source(array, "median_filter", channels={2, 3})
    kernel_size = int(kernel_size)
    if kernel_size != 3:
        raise ValueError("median_filter semantic adapter supports kernel_size=3 only")
    height, width = source.shape[:2]
    output = np.empty_like(source, dtype=np.float32)
    channel_count = 1 if source.ndim == 2 else int(source.shape[2])
    for row in range(height):
        for col in range(width):
            window = source[
                max(0, row - 1) : min(height, row + 2),
                max(0, col - 1) : min(width, col + 2),
            ]
            # The native graph clamps each neighbour independently, so a
            # sliced edge window must be expanded explicitly rather than
            # using the smaller window median.
            rows = [max(0, min(height - 1, row + dy)) for dy in (-1, 0, 1)]
            cols = [max(0, min(width - 1, col + dx)) for dx in (-1, 0, 1)]
            if source.ndim == 2:
                values = np.asarray([source[yy, xx] for yy in rows for xx in cols], dtype=np.float32)
                output[row, col] = np.sort(values, kind="stable")[4]
            else:
                for channel in range(channel_count):
                    values = np.asarray(
                        [source[yy, xx, channel] for yy in rows for xx in cols],
                        dtype=np.float32,
                    )
                    output[row, col, channel] = np.sort(values, kind="stable")[4]
            del window
    return np.ascontiguousarray(output, dtype=np.float32)


def _sobel_reference(array: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sobel pair matching gradients.py scalar/vector3 graph semantics."""

    source = _legacy_local_source(array, "sobel", channels={3})
    if source.ndim == 2:
        return _sobel_clamp_reference(source)
    channel_dx = []
    channel_dy = []
    for channel in range(3):
        dx, dy = _sobel_clamp_reference(source[..., channel])
        channel_dx.append(dx)
        channel_dy.append(dy)
    weights = np.asarray((0.299, 0.587, 0.114), dtype=np.float32)
    dx = np.ascontiguousarray(sum(value * weight for value, weight in zip(channel_dx, weights)), dtype=np.float32)
    dy = np.ascontiguousarray(sum(value * weight for value, weight in zip(channel_dy, weights)), dtype=np.float32)
    return dx, dy


def _laplacian_reference(array: np.ndarray) -> np.ndarray:
    """Four-neighbour clamp-border Laplacian matching gradients.py."""

    source = _legacy_local_source(array, "laplacian")
    if source.ndim != 2:
        raise ValueError("laplacian semantic adapter supports a 2D image only")
    padded = np.pad(source, ((1, 1), (1, 1)), mode="edge")
    result = (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - np.float32(4.0) * padded[1:-1, 1:-1]
    )
    return np.ascontiguousarray(result, dtype=np.float32)


def _smooth_flow_reference(
    array: np.ndarray,
    *,
    sigma: float = 1.0,
    kernel_size: int = 5,
) -> np.ndarray:
    """Two-pass clamp-border Gaussian smoothing of an HxWx2 flow field."""

    source = _legacy_local_source(array, "smooth_flow", channels={2})
    if source.ndim != 3 or source.shape[2] != 2:
        raise ValueError("smooth_flow expects an HxWx2 flow field")
    kernel_size = int(kernel_size)
    if kernel_size <= 0 or kernel_size % 2 == 0:
        raise ValueError("smooth_flow kernel_size must be a positive odd integer")
    radius = kernel_size // 2
    if radius > 16:
        raise ValueError("smooth_flow radius must not exceed 16")
    # ``smooth_flow``'s graph indexes a symmetric ``2*radius+1`` vector
    # (unlike the separable Gaussian graphs, which use the compact half-vector
    # returned by ``compute_gaussian_weights``).  Build that vector explicitly
    # so the semantic contract does not reproduce the historical out-of-range
    # access when a caller requests a non-zero radius.
    offsets = np.arange(-radius, radius + 1, dtype=np.float32)
    weights = np.exp(
        -(offsets * offsets)
        / np.float32(2.0 * float(sigma) * float(sigma))
    ).astype(np.float32)
    weights /= np.float32(np.sum(weights, dtype=np.float32))
    height, width = source.shape[:2]
    horizontal = np.empty_like(source, dtype=np.float32)
    output = np.empty_like(source, dtype=np.float32)
    for row in range(height):
        for col in range(width):
            value = np.zeros(2, dtype=np.float32)
            total = np.float32(0.0)
            for offset in range(-radius, radius + 1):
                weight = weights[offset + radius]
                value += source[row, max(0, min(width - 1, col + offset))] * weight
                total += weight
            horizontal[row, col] = value / (total + np.float32(1.0e-12))
    for row in range(height):
        for col in range(width):
            value = np.zeros(2, dtype=np.float32)
            total = np.float32(0.0)
            for offset in range(-radius, radius + 1):
                weight = weights[offset + radius]
                value += horizontal[max(0, min(height - 1, row + offset)), col] * weight
                total += weight
            output[row, col] = value / (total + np.float32(1.0e-12))
    return np.ascontiguousarray(output, dtype=np.float32)


def _highlight_recovery_reference(
    array: np.ndarray,
    *,
    wb_r: float = 1.0,
    wb_g: float = 1.0,
    wb_b: float = 1.0,
    strength: float = 1.0,
) -> np.ndarray:
    """Reference implementation of ``highlight_recover_rgb`` (11x11 halo)."""

    source = _legacy_local_source(array, "highlight_recovery", channels={3})
    if source.ndim != 3 or source.shape[2] != 3:
        raise ValueError("highlight_recovery expects an HxWx3 image")
    gains = np.asarray((wb_r, wb_g, wb_b), dtype=np.float32)
    if not np.isfinite(gains).all() or np.any(gains <= 0.0):
        raise ValueError("highlight_recovery white-balance gains must be positive")
    strength_value = np.float32(np.clip(float(strength), 0.0, 1.0))
    wb_scale = np.float32(np.max(gains))
    height, width = source.shape[:2]
    result = np.empty_like(source, dtype=np.float32)

    def smoothstep(value: np.float32) -> np.float32:
        value = np.float32(np.clip(value, 0.0, 1.0))
        return np.float32(value * value * (np.float32(3.0) - np.float32(2.0) * value))

    for row in range(height):
        for col in range(width):
            rgb = source[row, col]
            raw = rgb / gains
            raw_peak = np.float32(np.max(raw))
            rg_sum = np.float32(0.0)
            bg_sum = np.float32(0.0)
            weight_sum = np.float32(0.0)
            for dy in range(11):
                ny = max(0, min(height - 1, row + dy - 5))
                for dx in range(11):
                    nx = max(0, min(width - 1, col + dx - 5))
                    neighbour = source[ny, nx]
                    neighbour_peak = np.float32(np.max(neighbour / gains))
                    ng = np.float32(neighbour[1])
                    if ng > np.float32(1.0e-5):
                        distance = np.float32(abs(dy - 5) + abs(dx - 5))
                        confidence = smoothstep((np.float32(1.0) - neighbour_peak) / np.float32(0.12))
                        weight = confidence / (np.float32(1.0) + distance)
                        rg_sum += np.float32(np.clip(neighbour[0] / ng, 0.45, 1.80)) * weight
                        bg_sum += np.float32(np.clip(neighbour[2] / ng, 0.45, 1.80)) * weight
                        weight_sum += weight
            rg = rg_sum / weight_sum if weight_sum > np.float32(1.0e-5) else np.float32(1.0)
            bg = bg_sum / weight_sum if weight_sum > np.float32(1.0e-5) else np.float32(1.0)
            fade = smoothstep((raw_peak - np.float32(0.80)) / np.float32(0.20)) * strength_value
            fully_clipped = smoothstep((np.float32(np.min(raw)) - np.float32(0.94)) / np.float32(0.06))
            neutral_mix = fade * fully_clipped * np.float32(0.35)
            rg = rg * (np.float32(1.0) - neutral_mix) + neutral_mix
            bg = bg * (np.float32(1.0) - neutral_mix) + neutral_mix
            reliability = smoothstep((np.float32(1.0) - raw) / np.float32(0.12))
            green_sum = (
                (rgb[0] / np.maximum(rg, np.float32(1.0e-4))) * reliability[0]
                + rgb[1] * reliability[1]
                + (rgb[2] / np.maximum(bg, np.float32(1.0e-4))) * reliability[2]
            )
            reliable_weight = np.float32(np.sum(reliability))
            green_intensity = (
                green_sum / reliable_weight
                if reliable_weight > np.float32(1.0e-4)
                else np.minimum(rgb[1], np.minimum(rgb[0] / np.maximum(rg, np.float32(1.0e-4)), rgb[2] / np.maximum(bg, np.float32(1.0e-4))))
            )
            recovered = np.asarray(
                (
                    rgb[0] * reliability[0] + green_intensity * rg * (np.float32(1.0) - reliability[0]),
                    rgb[1] * reliability[1] + green_intensity * (np.float32(1.0) - reliability[1]),
                    rgb[2] * reliability[2] + green_intensity * bg * (np.float32(1.0) - reliability[2]),
                ),
                dtype=np.float32,
            )
            blend = smoothstep((raw_peak - np.float32(0.80)) / np.float32(0.20)) * strength_value
            result[row, col] = np.clip(
                (rgb * (np.float32(1.0) - blend) + recovered * blend) / np.maximum(wb_scale, np.float32(1.0e-4)),
                0.0,
                1.0,
            )
    return np.ascontiguousarray(result, dtype=np.float32)


def _cvt_color_extended_reference(array: np.ndarray, code: int) -> np.ndarray:
    """Pure-NumPy equivalent of ``image_processing/color_convert.py`` graphs."""

    source = _legacy_local_source(array, "cvtColor_extended", channels={3})
    if source.ndim != 3 or source.shape[2] != 3:
        raise ValueError("cvtColor_extended expects an HxWx3 image")
    code = int(code)
    b, g, r = source[..., 0], source[..., 1], source[..., 2]
    if code == 40:  # BGR -> HSV, OpenCV's 0..180/0..255 convention
        cmax = np.maximum(r, np.maximum(g, b))
        cmin = np.minimum(r, np.minimum(g, b))
        delta = cmax - cmin
        hue = np.zeros_like(cmax, dtype=np.float32)
        mask = delta > 0.0
        rmask = mask & (r >= g) & (r >= b)
        gmask = mask & ~rmask & (g >= r) & (g >= b)
        bmask = mask & ~rmask & ~gmask
        hue[rmask] = np.float32(60.0) * (g[rmask] - b[rmask]) / delta[rmask]
        hue[rmask & (hue < 0.0)] += np.float32(360.0)
        hue[gmask] = np.float32(60.0) * ((b[gmask] - r[gmask]) / delta[gmask] + np.float32(2.0))
        hue[bmask] = np.float32(60.0) * ((r[bmask] - g[bmask]) / delta[bmask] + np.float32(4.0))
        sat = np.divide(delta * np.float32(255.0), cmax, out=np.zeros_like(delta), where=cmax > 0.0)
        return np.ascontiguousarray(np.stack((hue * np.float32(0.5), sat, cmax), axis=-1), dtype=np.float32)
    if code == 54:  # HSV -> BGR
        h = source[..., 0] * np.float32(2.0)
        s = source[..., 1] / np.float32(255.0)
        v = source[..., 2]
        c = v * s
        hp = h / np.float32(60.0)
        x = c * (np.float32(1.0) - np.abs(np.mod(hp, np.float32(2.0)) - np.float32(1.0)) )
        m = v - c
        rgb = np.zeros((*h.shape, 3), dtype=np.float32)
        masks = (hp < 1.0, (hp >= 1.0) & (hp < 2.0), (hp >= 2.0) & (hp < 3.0), (hp >= 3.0) & (hp < 4.0), (hp >= 4.0) & (hp < 5.0), hp >= 5.0)
        choices = ((c, x, 0.0), (x, c, 0.0), (0.0, c, x), (0.0, x, c), (x, 0.0, c), (c, 0.0, x))
        for mask, choice in zip(masks, choices):
            for channel, value in enumerate(choice):
                rgb[..., channel] = np.where(mask, value, rgb[..., channel])
        # Internal ``rgb`` is R,G,B while the public buffer is B,G,R.
        return np.ascontiguousarray(np.stack((rgb[..., 2] + m, rgb[..., 1] + m, rgb[..., 0] + m), axis=-1), dtype=np.float32)
    if code == 36:  # BGR -> YCrCb
        y_out = np.float32(0.299) * r + np.float32(0.587) * g + np.float32(0.114) * b
        cr = np.clip(np.float32(0.5) * r - np.float32(0.4187) * g - np.float32(0.0813) * b + np.float32(128.0), 0.0, 255.0)
        cb = np.clip(-np.float32(0.1687) * r - np.float32(0.3313) * g + np.float32(0.5) * b + np.float32(128.0), 0.0, 255.0)
        return np.ascontiguousarray(np.stack((y_out, cr, cb), axis=-1), dtype=np.float32)
    if code == 38:  # YCrCb -> BGR
        y_out, cr, cb = source[..., 0], source[..., 1] - np.float32(128.0), source[..., 2] - np.float32(128.0)
        red = y_out + np.float32(1.402) * cr
        green = y_out - np.float32(0.3441) * cb - np.float32(0.7141) * cr
        blue = y_out + np.float32(1.772) * cb
        return np.ascontiguousarray(np.stack((np.clip(blue, 0.0, 255.0), np.clip(green, 0.0, 255.0), np.clip(red, 0.0, 255.0)), axis=-1), dtype=np.float32)
    if code == 44:  # BGR -> LAB, D65
        bs, gs, rs = b / np.float32(255.0), g / np.float32(255.0), r / np.float32(255.0)
        linear = lambda value: np.where(value > np.float32(0.04045), np.power((value + np.float32(0.055)) / np.float32(1.055), np.float32(2.4)), value / np.float32(12.92))
        rl, gl, bl = linear(rs), linear(gs), linear(bs)
        x_xyz = np.float32(0.4124564) * rl + np.float32(0.3575761) * gl + np.float32(0.1804375) * bl
        y_xyz = np.float32(0.2126729) * rl + np.float32(0.7151522) * gl + np.float32(0.0721750) * bl
        z_xyz = np.float32(0.0193339) * rl + np.float32(0.1191920) * gl + np.float32(0.9503041) * bl
        def lab_f(value: np.ndarray) -> np.ndarray:
            return np.where(value > np.float32(0.008856), np.power(np.maximum(value, np.float32(1.0e-10)), np.float32(1.0 / 3.0)), np.float32(7.787) * value + np.float32(16.0 / 116.0))
        fx, fy, fz = lab_f(x_xyz / np.float32(0.95047)), lab_f(y_xyz), lab_f(z_xyz / np.float32(1.08883))
        l_out = np.clip((np.float32(116.0) * fy - np.float32(16.0)) * np.float32(255.0 / 100.0), 0.0, 255.0)
        a_out = np.clip(np.float32(500.0) * (fx - fy) + np.float32(128.0), 0.0, 255.0)
        b_out = np.clip(np.float32(200.0) * (fy - fz) + np.float32(128.0), 0.0, 255.0)
        return np.ascontiguousarray(np.stack((l_out, a_out, b_out), axis=-1), dtype=np.float32)
    if code in (55, 56):  # LAB -> BGR; both historical constants are accepted
        l_out = source[..., 0] * np.float32(100.0 / 255.0)
        a_out = source[..., 1] - np.float32(128.0)
        b_out = source[..., 2] - np.float32(128.0)
        fy = (l_out + np.float32(16.0)) / np.float32(116.0)
        fx, fz = a_out / np.float32(500.0) + fy, fy - b_out / np.float32(200.0)
        def lab_f_inv(value: np.ndarray) -> np.ndarray:
            return np.where(value > np.float32(6.0 / 29.0), value * value * value, (value - np.float32(16.0 / 116.0)) / np.float32(7.787))
        x_xyz, y_xyz, z_xyz = np.float32(0.95047) * lab_f_inv(fx), lab_f_inv(fy), np.float32(1.08883) * lab_f_inv(fz)
        rl = np.float32(3.2404542) * x_xyz - np.float32(1.5371385) * y_xyz - np.float32(0.4985314) * z_xyz
        gl = -np.float32(0.9692660) * x_xyz + np.float32(1.8760108) * y_xyz + np.float32(0.0415560) * z_xyz
        bl = np.float32(0.0556434) * x_xyz - np.float32(0.2040259) * y_xyz + np.float32(1.0572252) * z_xyz
        encode = lambda value: np.where(value > np.float32(0.0031308), np.float32(1.055) * np.power(np.maximum(value, np.float32(1.0e-10)), np.float32(1.0 / 2.4)) - np.float32(0.055), np.float32(12.92) * value)
        red, green, blue = encode(rl), encode(gl), encode(bl)
        return np.ascontiguousarray(np.stack((np.clip(blue * 255.0, 0.0, 255.0), np.clip(green * 255.0, 0.0, 255.0), np.clip(red * 255.0, 0.0, 255.0)), axis=-1), dtype=np.float32)
    raise ValueError(f"unsupported cvtColor_extended code: {code}")


def _filter2d_reference(array: np.ndarray, kernel: Any) -> np.ndarray:
    table = np.asarray(kernel, dtype=np.float32)
    return _stencil_reference(array, table, mode="sum", border="reflect")


def _morphology_reference(
    array: np.ndarray, *, operation: str = "dilate", kernel: Any = None
) -> np.ndarray:
    table = np.ones((3, 3), dtype=np.float32) if kernel is None else np.asarray(kernel)
    if table.shape != (3, 3):
        raise ValueError("semantic morphology adapter supports only a 3x3 kernel")
    mode = "max" if str(operation).lower() == "dilate" else "min"
    if str(operation).lower() not in {"dilate", "erode"}:
        raise ValueError("morphology operation must be dilate or erode")
    return _stencil_reference(array, table, mode=mode, border="edge")


def _threshold_reference(
    array: np.ndarray,
    threshold: float,
    max_value: float,
    mode: int = 0,
) -> np.ndarray:
    source = np.asarray(array, dtype=np.float32)
    threshold = np.float32(threshold)
    max_value = np.float32(max_value)
    mode = int(mode)
    if mode == 0:
        result = np.where(source > threshold, max_value, 0.0)
    elif mode == 1:
        result = np.where(source > threshold, 0.0, max_value)
    elif mode == 2:
        result = np.minimum(source, threshold)
    elif mode == 3:
        result = np.where(source > threshold, source, 0.0)
    elif mode == 4:
        result = np.where(source > threshold, 0.0, source)
    else:
        raise ValueError("unsupported threshold mode")
    return np.ascontiguousarray(result, dtype=np.float32)


def _normalize_reference(
    array: np.ndarray,
    *,
    alpha: float = 0.0,
    beta: float = 255.0,
    mode: Any = "MINMAX",
    src_min: Optional[float] = None,
    src_max: Optional[float] = None,
    norm_value: Optional[float] = None,
) -> np.ndarray:
    source = np.asarray(array, dtype=np.float32)
    selected = str(mode).upper() if isinstance(mode, str) else int(mode)
    if selected == "MINMAX" or selected == 32:
        low = float(np.min(source) if src_min is None else src_min)
        high = float(np.max(source) if src_max is None else src_max)
        if high <= low:
            return np.full_like(source, np.float32(alpha), dtype=np.float32)
        result = (source - np.float32(low)) * np.float32(
            (float(beta) - float(alpha)) / (high - low)
        ) + np.float32(alpha)
    else:
        norm = float(norm_value if norm_value is not None else 1.0)
        if norm <= 0.0:
            raise ValueError("normalize norm_value must be positive")
        if selected in (0, "INF"):
            measured = float(np.max(np.abs(source)))
        elif selected in (1, "L1"):
            measured = float(np.sum(np.abs(source)))
        elif selected in (2, "L2"):
            measured = float(np.sqrt(np.sum(source * source)))
        else:
            raise ValueError("unsupported normalize mode")
        result = source * np.float32(float(alpha) / max(measured, norm))
    return np.ascontiguousarray(result, dtype=np.float32)


def _bilateral_reference(
    source: np.ndarray,
    guide: np.ndarray,
    *,
    radius: int = 1,
    inv_space: float = 0.5,
    inv_range: float = 50.0,
) -> np.ndarray:
    values = np.asarray(source, dtype=np.float32)
    guidance = np.asarray(guide, dtype=np.float32)
    if values.ndim not in (2, 3) or guidance.ndim != 2:
        raise ValueError("bilateral adapter expects image and 2D guide")
    if values.shape[:2] != guidance.shape:
        raise ValueError("bilateral guide must match source height/width")
    radius = int(radius)
    if radius != 1:
        raise ValueError("semantic bilateral adapter supports radius=1")
    padded_values = _edge_pad(values, radius)
    padded_guide = _edge_pad(guidance, radius)
    output = np.empty_like(values, dtype=np.float32)
    height, width = values.shape[:2]
    offsets = [(dy, dx) for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1)]
    for row in range(height):
        for col in range(width):
            center = padded_guide[row + radius, col + radius]
            total = np.float32(0.0)
            weighted = np.zeros(values.shape[2:], dtype=np.float32)
            for dy, dx in offsets:
                sample_guide = padded_guide[row + radius + dy, col + radius + dx]
                spatial = np.float32(dy * dy + dx * dx)
                weight = np.exp(
                    np.float32(-spatial * float(inv_space))
                    - np.float32((sample_guide - center) ** 2 * float(inv_range))
                )
                total += weight
                weighted += weight * padded_values[row + radius + dy, col + radius + dx]
            output[row, col] = weighted / np.maximum(total, np.float32(1.0e-8))
    return np.ascontiguousarray(output, dtype=np.float32)


def _guided_filter_reference(
    guide: np.ndarray, source: np.ndarray, *, radius: int = 1, epsilon: float = 1.0e-4
) -> np.ndarray:
    I = np.asarray(guide, dtype=np.float32)
    p = np.asarray(source, dtype=np.float32)
    if I.ndim != 2 or p.ndim != 2 or I.shape != p.shape:
        raise ValueError("guided filter adapter expects matching 2D arrays")
    radius = int(radius)
    if radius != 1:
        raise ValueError("semantic guided filter adapter supports radius=1")

    def mean(values: np.ndarray) -> np.ndarray:
        return _stencil_reference(values, np.full((3, 3), np.float32(1.0 / 9.0)))

    mean_I = mean(I)
    mean_p = mean(p)
    mean_II = mean(I * I)
    mean_Ip = mean(I * p)
    variance = mean_II - mean_I * mean_I
    covariance = mean_Ip - mean_I * mean_p
    a = covariance / (variance + np.float32(epsilon))
    b = mean_p - a * mean_I
    mean_a = mean(a)
    mean_b = mean(b)
    return np.ascontiguousarray(mean_a * I + mean_b, dtype=np.float32)


def _non_local_means_reference(
    source: np.ndarray,
    *,
    h_param: float = 10.0,
    search_radius: int = 1,
    patch_radius: int = 1,
    refinement_strength: float = 1.0,
    shrinkage_strength: float = 1.0,
) -> np.ndarray:
    """Small deterministic NLM oracle for the (3, 1) native variant."""

    values = np.asarray(source, dtype=np.float32)
    if values.ndim not in (2, 3):
        raise ValueError("NLM adapter expects a 2D or HxWxC array")
    if int(search_radius) != 1 or int(patch_radius) != 1:
        raise ValueError("semantic NLM adapter supports search_window=3, patch_size=1")
    patch = int(patch_radius)
    padded = _edge_pad(values, int(search_radius) + patch)
    h = max(float(h_param), 1.0e-6) / 255.0
    output = np.empty_like(values, dtype=np.float32)
    height, width = values.shape[:2]
    for row in range(height):
        for col in range(width):
            center_patch = padded[row + search_radius : row + search_radius + 2 * patch + 1,
                                   col + search_radius : col + search_radius + 2 * patch + 1]
            total = np.float32(0.0)
            weighted = np.zeros(values.shape[2:], dtype=np.float32)
            for dy in range(-search_radius, search_radius + 1):
                for dx in range(-search_radius, search_radius + 1):
                    candidate = padded[
                        row + search_radius + dy : row + search_radius + dy + 2 * patch + 1,
                        col + search_radius + dx : col + search_radius + dx + 2 * patch + 1,
                    ]
                    distance = np.mean((center_patch - candidate) ** 2)
                    weight = np.exp(-np.float32(distance) / np.float32(h * h))
                    total += weight
                    weighted += weight * padded[row + search_radius + dy + patch,
                                                col + search_radius + dx + patch]
            value = weighted / np.maximum(total, np.float32(1.0e-8))
            # Keep the two refinement knobs visible while preserving a bounded
            # local operation.  The native graph uses the same convex blend.
            blend = np.float32(np.clip(float(refinement_strength), 0.0, 1.0))
            shrink = np.float32(np.clip(float(shrinkage_strength), 0.0, 1.0))
            output[row, col] = (1.0 - blend * shrink) * values[row, col] + blend * shrink * value
    return np.ascontiguousarray(output, dtype=np.float32)


def _weighted_input_shapes(
    sum_img: np.ndarray,
    sum_weight: np.ndarray,
    reference: Optional[np.ndarray] = None,
) -> tuple[np.ndarray, np.ndarray, Optional[np.ndarray]]:
    """Validate the accumulator shapes used by the common AOT kernels.

    ``mean_division`` and ``normalize_accumulator`` are historically classified
    as global operations because they are normally called at the end of a
    multi-tile fusion.  Their actual kernel body is a per-pixel map, however:
    each output pixel reads only its corresponding accumulator and weight (and,
    for ``mean_division``, the corresponding reference pixel).  This helper
    keeps that distinction explicit and makes the semantic adapter fail closed
    for malformed or non-floating inputs.
    """

    values = np.asarray(sum_img)
    weights = np.asarray(sum_weight)
    if values.ndim not in (2, 3):
        raise ValueError("accumulator image must be a 2D image or HxWxC array")
    if weights.ndim != 2 or tuple(weights.shape) != tuple(values.shape[:2]):
        raise ValueError("accumulator weights must match the image's first two dimensions")
    if not np.issubdtype(values.dtype, np.floating):
        raise TypeError("accumulator image must use a floating-point dtype")
    if not np.issubdtype(weights.dtype, np.number):
        raise TypeError("accumulator weights must use a numeric dtype")
    if np.issubdtype(weights.dtype, np.complexfloating):
        raise TypeError("accumulator weights must use a real numeric dtype")
    # NaN/Inf would make the tile result dependent on the reduction route
    # (and can silently turn every guarded division into its fallback).  The
    # native accumulator graphs have no portable non-finite contract, so fail
    # closed before partitioning rather than claiming deterministic parity.
    if not np.isfinite(values).all() or not np.isfinite(weights).all():
        raise ValueError("accumulator inputs must contain only finite values")
    ref_values: Optional[np.ndarray] = None
    if reference is not None:
        ref_values = np.asarray(reference)
        if tuple(ref_values.shape) != tuple(values.shape):
            raise ValueError("reference image must match the accumulator image shape")
        if not np.issubdtype(ref_values.dtype, np.number):
            raise TypeError("reference image must use a numeric dtype")
        if np.issubdtype(ref_values.dtype, np.complexfloating):
            raise TypeError("reference image must use a real numeric dtype")
        if not np.isfinite(ref_values).all():
            raise ValueError("reference image must contain only finite values")
    return values, weights, ref_values


def _mean_division_reference(
    sum_img: np.ndarray,
    sum_weight: np.ndarray,
    ref_img: np.ndarray,
    *,
    epsilon: float = 1.0e-6,
) -> np.ndarray:
    """Pointwise oracle matching ``common._mean_division_kernel``.

    The operation remains a semantic CPU adapter only.  It does not promote
    the historical global operation to automatic/native dispatch.  A tile can
    therefore be evaluated independently as long as the caller has already
    produced the per-pixel accumulators for that tile.
    """

    values, weights, reference = _weighted_input_shapes(sum_img, sum_weight, ref_img)
    assert reference is not None  # shape helper guarantees this branch
    epsilon = float(epsilon)
    if not np.isfinite(epsilon) or epsilon < 0.0:
        raise ValueError("mean_division epsilon must be finite and non-negative")
    dtype = values.dtype
    weighted = np.asarray(weights, dtype=dtype)
    fallback = np.asarray(reference, dtype=dtype)
    result = np.empty_like(values, order="C")
    mask = weighted > np.asarray(epsilon, dtype=dtype)
    if values.ndim == 2:
        np.divide(values, weighted, out=result, where=mask)
        result[~mask] = fallback[~mask]
    else:
        mask3 = mask[..., None]
        np.divide(values, weighted[..., None], out=result, where=mask3)
        result[~mask, :] = fallback[~mask, :]
    return np.ascontiguousarray(result, dtype=dtype)


def _normalize_accumulator_reference(
    sum_img: np.ndarray,
    sum_weight: np.ndarray,
    *,
    epsilon: float = 1.0e-6,
) -> np.ndarray:
    """Pointwise oracle matching ``common._normalize_accum*_kernel``."""

    values, weights, _ = _weighted_input_shapes(sum_img, sum_weight)
    epsilon = float(epsilon)
    if not np.isfinite(epsilon) or epsilon <= 0.0:
        raise ValueError("normalize_accumulator epsilon must be finite and positive")
    dtype = values.dtype
    weighted = np.asarray(weights, dtype=dtype)
    denominator = np.maximum(weighted, np.asarray(epsilon, dtype=dtype))
    if values.ndim == 2:
        result = np.divide(values, denominator)
    else:
        result = np.divide(values, denominator[..., None])
    return np.ascontiguousarray(result, dtype=dtype)


def _to_gamma_proxy_reference(array: np.ndarray, scale: float = 1.0) -> np.ndarray:
    """Pointwise gamma-proxy transform used by the alignment bridge."""

    values = np.asarray(array, dtype=np.float32)
    x = values * np.float32(scale)
    mapped = x / np.sqrt(np.float32(1.0) + x * x)
    return np.ascontiguousarray(
        np.power(np.clip(mapped, 0.0, 1.0), np.float32(1.0 / 2.22)),
        dtype=np.float32,
    )


def _rotate_by_flip_reference(array: np.ndarray, flip: int = 0) -> np.ndarray:
    """Reference for the same-shape LibRaw flip values (0..3).

    LibRaw values 4..7 transpose the image and therefore change the output
    shape.  They remain deliberately outside this adapter's contract.
    """

    value = int(flip)
    source = np.asarray(array)
    if value == 0:
        return np.array(source, copy=True, order="C")
    if value == 1:
        return np.ascontiguousarray(np.fliplr(source))
    if value in (2, 3):
        return np.ascontiguousarray(np.rot90(source, 2))
    raise ValueError("rotate_by_flip semantic adapter supports only flip values 0..3")


def _hanning_window_reference(
    shape: Sequence[int], *, exclude_boundary: bool = False, dtype: Any = np.float32
) -> np.ndarray:
    """Generate the full output-domain Hanning window deterministically."""

    if len(tuple(shape)) != 2:
        raise ValueError("Hanning output shape must be (height, width)")
    height, width = (int(shape[0]), int(shape[1]))
    if height <= 0 or width <= 0:
        raise ValueError("Hanning output dimensions must be positive")
    rows = np.arange(height, dtype=np.float32)
    cols = np.arange(width, dtype=np.float32)
    if height > 1:
        denominator = float(height + 1 if exclude_boundary else height - 1)
        wy = 0.5 - 0.5 * np.cos(
            np.float32(2.0 * np.pi) * ((rows + (1.0 if exclude_boundary else 0.0)) / denominator)
        )
    else:
        wy = np.ones(1, dtype=np.float32)
    if width > 1:
        denominator = float(width + 1 if exclude_boundary else width - 1)
        wx = 0.5 - 0.5 * np.cos(
            np.float32(2.0 * np.pi) * ((cols + (1.0 if exclude_boundary else 0.0)) / denominator)
        )
    else:
        wx = np.ones(1, dtype=np.float32)
    result = np.maximum(wy[:, None], np.float32(1.0e-4)) * np.maximum(
        wx[None, :], np.float32(1.0e-4)
    )
    return np.ascontiguousarray(result, dtype=np.dtype(dtype))


def _gaussian_window_reference(
    shape: Sequence[int], *, sigma: float
) -> np.ndarray:
    """Generate the full output-domain Gaussian window used by extended AOT."""

    if len(tuple(shape)) != 2:
        raise ValueError("Gaussian output shape must be (height, width)")
    height, width = (int(shape[0]), int(shape[1]))
    sigma = float(sigma)
    if height <= 0 or width <= 0 or sigma <= 0.0:
        raise ValueError("Gaussian output dimensions and sigma must be positive")
    rows = np.arange(height, dtype=np.float32)[:, None]
    cols = np.arange(width, dtype=np.float32)[None, :]
    center_y = np.float32(height / 2.0)
    center_x = np.float32(width / 2.0)
    distance = (rows - center_y) ** 2 + (cols - center_x) ** 2
    return np.ascontiguousarray(
        np.exp(-distance / np.float32(2.0 * sigma * sigma)), dtype=np.float32
    )


def _brief_pattern_reference(
    *, num_pairs: int = 256, patch_size: int = 31, seed: int = 42
) -> np.ndarray:
    """Deterministic BRIEF coordinates matching :func:`generate_brief_pattern`.

    The public helper historically uses ``np.random.seed`` followed by four
    normal draws.  ``RandomState`` preserves that legacy stream locally,
    avoiding mutation of the process-global NumPy RNG while keeping exact
    coordinates for the same seed/arguments.
    """

    num_pairs = int(num_pairs)
    patch_size = int(patch_size)
    if num_pairs <= 0:
        raise ValueError("generate_brief_pattern requires num_pairs > 0")
    if patch_size <= 0:
        raise ValueError("generate_brief_pattern requires patch_size > 0")
    rng = np.random.RandomState(int(seed))
    sigma = np.float64(patch_size / 5.0)
    x1 = rng.normal(0.0, sigma, num_pairs)
    y1 = rng.normal(0.0, sigma, num_pairs)
    x2 = rng.normal(0.0, sigma, num_pairs)
    y2 = rng.normal(0.0, sigma, num_pairs)
    radius = patch_size // 2
    x1 = np.clip(np.round(x1), -radius, radius)
    y1 = np.clip(np.round(y1), -radius, radius)
    x2 = np.clip(np.round(x2), -radius, radius)
    y2 = np.clip(np.round(y2), -radius, radius)
    return np.ascontiguousarray(np.stack((x1, y1, x2, y2), axis=1), dtype=np.float32)


def _normalize_image_reference(
    source: np.ndarray, *, dtype: Any
) -> np.ndarray:
    """Reference for ``alignment.taichi_bridge.normalize_image_gpu``.

    The bridge returns float32 data, scales integer source domains by the
    *declared* dtype's maximum, and expands a grayscale frame to RGB.  This
    adapter deliberately keeps those semantics instead of clipping or
    silently changing the public dtype contract.
    """

    value = np.asarray(source)
    if value.ndim not in (2, 3):
        raise ValueError("normalize_image expects a 2D or HxWxC source image")
    try:
        target_dtype = np.dtype(dtype)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"unsupported normalize_image dtype: {dtype!r}") from exc
    if np.issubdtype(target_dtype, np.integer):
        scale = float(np.iinfo(target_dtype).max)
    elif np.issubdtype(target_dtype, np.floating):
        scale = 1.0
    else:
        raise TypeError(f"unsupported normalize_image dtype: {target_dtype}")
    result = np.asarray(value, dtype=np.float32) / np.float32(scale)
    if result.ndim == 2:
        result = np.repeat(result[..., None], 3, axis=-1)
    return np.ascontiguousarray(result, dtype=np.float32)


def _reflect_idx_101_reference(indices: np.ndarray, size: int) -> np.ndarray:
    """Vectorized equivalent of ``common.reflect_idx`` for flow maps."""

    size = int(size)
    if size <= 0:
        raise ValueError("flow-map source dimensions must be positive")
    values = np.abs(np.asarray(indices, dtype=np.int64))
    diff = values - (size - 1)
    result = values - 2 * np.maximum(diff, 0)
    return np.clip(result, 0, size - 1).astype(np.int64, copy=False)


def _flow_map_inputs(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[np.ndarray, np.ndarray, int, int, np.float32, np.float32]:
    """Validate flow-map input forms and resolve the output grid metadata."""

    arrays = tuple(np.asarray(value) for value in inputs)
    if len(arrays) == 1:
        flow = arrays[0]
        if flow.ndim != 3 or flow.shape[2] != 2:
            raise ValueError("build_flow_maps expects HxWx2 flow or separate dx/dy")
        dx, dy = flow[..., 0], flow[..., 1]
    elif len(arrays) == 2:
        dx, dy = arrays
        if dx.ndim != 2 or dy.ndim != 2 or dx.shape != dy.shape:
            raise ValueError("build_flow_maps dx/dy inputs must be matching 2D arrays")
    else:
        raise ValueError("build_flow_maps expects one HxWx2 or two HxW inputs")
    if not np.issubdtype(dx.dtype, np.floating) or not np.issubdtype(dy.dtype, np.floating):
        raise TypeError("build_flow_maps flow inputs must use a floating-point dtype")
    dx = np.ascontiguousarray(dx, dtype=np.float32)
    dy = np.ascontiguousarray(dy, dtype=np.float32)
    if not np.isfinite(dx).all() or not np.isfinite(dy).all():
        raise ValueError("build_flow_maps flow inputs must be finite")
    h_flow, w_flow = (int(dx.shape[0]), int(dx.shape[1]))
    if h_flow <= 0 or w_flow <= 0:
        raise ValueError("build_flow_maps flow dimensions must be positive")
    shape = params.get("output_shape", params.get("shape"))
    if shape is None:
        h_dst = params.get("full_h", params.get("h_dst"))
        w_dst = params.get("full_w", params.get("w_dst"))
        if h_dst is None or w_dst is None:
            raise ValueError("build_flow_maps requires output_shape or full_h/full_w")
        shape = (h_dst, w_dst)
    shape = tuple(int(value) for value in shape)
    if len(shape) != 2 or any(value <= 0 for value in shape):
        raise ValueError("build_flow_maps output shape must be positive 2D")
    h_dst, w_dst = shape
    # The native graph divides by (destination_size - 1).  Reject the
    # undefined singleton grid rather than inventing a different native
    # contract in the semantic adapter.
    if h_dst < 2 or w_dst < 2:
        raise ValueError("build_flow_maps requires destination dimensions >= 2")
    scale_x = params.get("scale_x")
    scale_y = params.get("scale_y")
    if scale_x is None:
        scale_x = float(w_dst) / float(w_flow)
    if scale_y is None:
        scale_y = float(h_dst) / float(h_flow)
    scale_x = np.float32(scale_x)
    scale_y = np.float32(scale_y)
    if not np.isfinite(scale_x) or not np.isfinite(scale_y):
        raise ValueError("build_flow_maps scales must be finite")
    return dx, dy, h_dst, w_dst, scale_x, scale_y


def _flow_map_compute_region(
    dx: np.ndarray,
    dy: np.ndarray,
    h_dst: int,
    w_dst: int,
    scale_x: np.float32,
    scale_y: np.float32,
    row_start: int,
    row_stop: int,
    col_start: int,
    col_stop: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute one output-domain region with the remap graph's formula."""

    h_flow, w_flow = int(dx.shape[0]), int(dx.shape[1])
    rows = np.arange(int(row_start), int(row_stop), dtype=np.float32)
    cols = np.arange(int(col_start), int(col_stop), dtype=np.float32)
    # Keep each intermediate in f32: this mirrors the Taichi graph's scalar
    # argument and float arithmetic and makes non-multiple tile parity stable.
    fx = rows * np.float32(h_flow - 1) / np.float32(h_dst - 1)
    fy = cols * np.float32(w_flow - 1) / np.float32(w_dst - 1)
    # ``rows`` indexes the destination Y axis; ``cols`` indexes X.  Name the
    # source coordinates explicitly to avoid accidental transposition.
    src_y = fx.astype(np.float32, copy=False)
    src_x = fy.astype(np.float32, copy=False)
    iy = np.floor(src_y).astype(np.int64)
    ix = np.floor(src_x).astype(np.int64)
    fy_frac = src_y - iy.astype(np.float32)
    fx_frac = src_x - ix.astype(np.float32)
    iy0 = _reflect_idx_101_reference(iy, h_flow)
    iy1 = _reflect_idx_101_reference(iy + 1, h_flow)
    ix0 = _reflect_idx_101_reference(ix, w_flow)
    ix1 = _reflect_idx_101_reference(ix + 1, w_flow)

    # Broadcast four corner samples over the output tile.  The expression
    # ordering follows ``common.bilinear_at`` (top, bottom, then blend).
    def sample(source: np.ndarray) -> np.ndarray:
        v00 = source[iy0[:, None], ix0[None, :]]
        v01 = source[iy0[:, None], ix1[None, :]]
        v10 = source[iy1[:, None], ix0[None, :]]
        v11 = source[iy1[:, None], ix1[None, :]]
        top = v00 * (np.float32(1.0) - fx_frac[None, :]) + v01 * fx_frac[None, :]
        bottom = v10 * (np.float32(1.0) - fx_frac[None, :]) + v11 * fx_frac[None, :]
        return top * (np.float32(1.0) - fy_frac[:, None]) + bottom * fy_frac[:, None]

    sampled_dx = sample(dx)
    sampled_dy = sample(dy)
    identity_x = np.broadcast_to(cols[None, :], sampled_dx.shape)
    identity_y = np.broadcast_to(rows[:, None], sampled_dy.shape)
    map_x = identity_x + sampled_dx * scale_x
    map_y = identity_y + sampled_dy * scale_y
    return (
        np.ascontiguousarray(map_x, dtype=np.float32),
        np.ascontiguousarray(map_y, dtype=np.float32),
    )


def _flow_maps_reference(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[np.ndarray, np.ndarray]:
    dx, dy, h_dst, w_dst, scale_x, scale_y = _flow_map_inputs(inputs, params)
    return _flow_map_compute_region(
        dx, dy, h_dst, w_dst, scale_x, scale_y, 0, h_dst, 0, w_dst
    )


def _natural_tone_lut(
    exposure: float,
    shoulder: float,
    gamma: float,
    shadow_offset: float,
    *,
    size: int = 65536,
) -> np.ndarray:
    """Build the deterministic LUT used by ``apply_natural_tone_mapping_np``."""

    raw_indices = np.linspace(0.0, 1.0, int(size), dtype=np.float32)
    x = np.maximum(0.0, raw_indices - np.float32(shadow_offset))
    x = x * np.float32(exposure)
    if abs(float(shoulder) - 1.0) > 1.0e-4:
        denominator = np.power(
            1.0 + np.power(x, np.float32(shoulder)),
            np.float32(1.0 / float(shoulder)),
        )
        x = x / np.maximum(denominator, np.float32(1.0e-8))
    else:
        x = x / np.sqrt(1.0 + x * x)
    x = np.clip(x, 0.0, 1.0)
    if abs(float(gamma) - 1.0) > 1.0e-4:
        x = np.power(x, np.float32(1.0 / float(gamma)))
    return np.clip(x, 0.0, 1.0).astype(np.float32, copy=False)


def _natural_tonemapping_reference(
    array: np.ndarray,
    *,
    exposure: float = 1.43,
    shoulder: float = 2.99,
    gamma: float = 1.50,
    shadow_offset: float = 0.01,
    saturation: float = 1.0,
    texture_amount: float = 0.0,
) -> np.ndarray:
    """Pointwise semantic oracle for natural tone mapping.

    ``texture_amount`` invokes a Gaussian/global texture stage in the public
    API.  That dependency is deliberately rejected here rather than silently
    pretending it is local; callers can keep that configuration on the
    existing full-frame path until a halo-aware proof is added.
    """

    if abs(float(texture_amount)) > 1.0e-4:
        raise ValueError(
            "natural tone semantic adapter requires texture_amount=0; "
            "texture enhancement is global"
        )
    source = np.asarray(array)
    if source.ndim not in (2, 3):
        raise ValueError("natural tone input must be a 2D or 3D image")
    if source.ndim == 3 and source.shape[2] not in (1, 3, 4):
        raise ValueError("natural tone input must have 1, 3, or 4 channels")

    lut = _natural_tone_lut(
        exposure,
        shoulder,
        gamma,
        shadow_offset,
    )
    if source.dtype == np.uint16:
        toned = lut[source]
    elif source.dtype in (np.float16, np.float32, np.float64):
        indices = np.clip(
            (source.astype(np.float32, copy=False) * np.float32(65535.0)).astype(
                np.int32, copy=False
            ),
            0,
            65535,
        )
        toned = lut[indices]
    else:
        x = np.maximum(
            0.0, source.astype(np.float32, copy=False) - np.float32(shadow_offset)
        )
        x = x * np.float32(exposure)
        if abs(float(shoulder) - 1.0) > 1.0e-4:
            denominator = np.power(
                1.0 + np.power(x, np.float32(shoulder)),
                np.float32(1.0 / float(shoulder)),
            )
            x = x / np.maximum(denominator, np.float32(1.0e-8))
        else:
            x = x / np.sqrt(1.0 + x * x)
        toned = np.clip(x, 0.0, 1.0)
        if abs(float(gamma) - 1.0) > 1.0e-4:
            toned = np.power(toned, np.float32(1.0 / float(gamma)))

    toned = np.asarray(toned, dtype=np.float32)
    if (
        abs(float(saturation) - 1.0) > 1.0e-4
        and toned.ndim == 3
        and toned.shape[2] == 3
    ):
        luma = (
            np.float32(0.299) * toned[..., 0]
            + np.float32(0.587) * toned[..., 1]
            + np.float32(0.114) * toned[..., 2]
        )
        luma3 = np.stack((luma, luma, luma), axis=-1)
        toned = np.clip(
            luma3 + np.float32(saturation) * (toned - luma3), 0.0, 1.0
        )
    return np.ascontiguousarray(toned, dtype=np.float32)


# ---------------------------------------------------------------------------
# Analysis-family semantic oracles (Canny / CLAHE)
# ---------------------------------------------------------------------------
#
# Both algorithms have a local prefix followed by a global or stateful stage.
# They must not be represented as an ordinary same-shape stencil: Canny's
# hysteresis can cross arbitrary block boundaries and CLAHE's interpolation
# consumes one LUT field built from the complete image.  The helpers below
# therefore expose explicit stage contracts to ``run_analysis_tiled`` while
# keeping the maintained full-frame AOT path untouched.


def _analysis_float_image(array: np.ndarray, operation: str) -> np.ndarray:
    values = np.asarray(array)
    if values.ndim != 2 or values.size == 0:
        raise ValueError(f"{operation} semantic adapter expects a non-empty 2D image")
    if not np.issubdtype(values.dtype, np.number):
        raise TypeError(f"{operation} input must be numeric")
    result = np.ascontiguousarray(values, dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError(f"{operation} input must contain only finite values")
    return result


def _canny_parameters(
    source: np.ndarray, params: Mapping[str, Any]
) -> tuple[np.ndarray, float, float]:
    values = _analysis_float_image(source, "canny_aot")
    aperture = int(params.get("aperture_size", 3))
    if aperture != 3:
        raise ValueError("canny_aot semantic adapter supports aperture_size=3 only")
    low = float(params.get("low_threshold", params.get("low", 50.0)))
    high = float(params.get("high_threshold", params.get("high", 150.0)))
    if not np.isfinite(low) or not np.isfinite(high) or low < 0.0 or high < low:
        raise ValueError("canny_aot thresholds must satisfy 0 <= low <= high")
    return values, low, high


def _sobel_clamp_reference(source: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Sobel implementation matching ``gradients._sobel_kernel`` clamp edges."""

    values = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    padded = np.pad(values, ((1, 1), (1, 1)), mode="edge")
    top = padded[:-2]
    middle = padded[1:-1]
    bottom = padded[2:]
    gx = (top[:, 2:] + np.float32(2.0) * middle[:, 2:] + bottom[:, 2:]) - (
        top[:, :-2] + np.float32(2.0) * middle[:, :-2] + bottom[:, :-2]
    )
    gy = (bottom[:, :-2] + np.float32(2.0) * bottom[:, 1:-1] + bottom[:, 2:]) - (
        top[:, :-2] + np.float32(2.0) * top[:, 1:-1] + top[:, 2:]
    )
    return np.ascontiguousarray(gx, dtype=np.float32), np.ascontiguousarray(gy, dtype=np.float32)


def _canny_nms_reference(
    gx: np.ndarray, gy: np.ndarray, magnitude: np.ndarray
) -> np.ndarray:
    """NMS with the same four-sector tests and clamp borders as the AOT graph."""

    dx = np.asarray(gx, dtype=np.float32)
    dy = np.asarray(gy, dtype=np.float32)
    mag = np.asarray(magnitude, dtype=np.float32)
    if dx.shape != dy.shape or dx.shape != mag.shape or dx.ndim != 2:
        raise ValueError("canny NMS arrays must be matching 2D shapes")
    height, width = dx.shape
    output = np.zeros_like(mag, dtype=np.float32)
    # A small explicit loop mirrors the branch ordering in the Taichi kernel
    # and avoids backend/NumPy vectorization differences at sector ties.
    tg22 = np.float32(0.41421356237)
    for row in range(height):
        ym = max(0, row - 1)
        yp = min(height - 1, row + 1)
        for col in range(width):
            xm = max(0, col - 1)
            xp = min(width - 1, col + 1)
            value = np.float32(np.abs(dx[row, col]) + np.abs(dy[row, col]))
            if value < np.float32(1.0e-6):
                continue
            ax = np.float32(np.abs(dx[row, col]))
            ay = np.float32(np.abs(dy[row, col]))
            if ax > ay * (np.float32(1.0) / tg22):
                first, second = mag[row, xm], mag[row, xp]
            elif ay > ax * (np.float32(1.0) / tg22):
                first, second = mag[ym, col], mag[yp, col]
            elif np.float32(dx[row, col] * dy[row, col]) >= np.float32(0.0):
                first, second = mag[ym, xm], mag[yp, xp]
            else:
                first, second = mag[ym, xp], mag[yp, xm]
            if value >= first and value >= second:
                output[row, col] = value
    return np.ascontiguousarray(output, dtype=np.float32)


def _canny_local_prefix(source: np.ndarray, low: float, high: float) -> np.ndarray:
    """Run Sobel -> magnitude -> NMS -> threshold for one source window."""

    values = _analysis_float_image(source, "canny_aot")
    gx, gy = _sobel_clamp_reference(values)
    magnitude = np.ascontiguousarray(np.abs(gx) + np.abs(gy), dtype=np.float32)
    nms = _canny_nms_reference(gx, gy, magnitude)
    edges = np.zeros_like(nms, dtype=np.float32)
    edges[nms >= np.float32(high)] = np.float32(255.0)
    weak = (nms >= np.float32(low)) & (nms < np.float32(high))
    edges[weak] = np.float32(128.0)
    return edges


def _canny_hysteresis_reference(edges: np.ndarray) -> np.ndarray:
    """Deterministic global hysteresis stage (8-connected, bounded passes)."""

    state = np.ascontiguousarray(np.asarray(edges), dtype=np.float32).copy()
    if state.ndim != 2:
        raise ValueError("canny hysteresis expects a 2D state image")
    height, width = state.shape
    # The AOT wrapper uses min(h+w, 256) fixed dispatches.  Updating from a
    # snapshot per pass makes the intended stage boundary deterministic and
    # avoids relying on thread scheduling to propagate a chain in one pass.
    for _ in range(min(height + width, 256)):
        strong = state == np.float32(255.0)
        padded = np.pad(strong, ((1, 1), (1, 1)), mode="edge")
        adjacent = np.zeros_like(strong, dtype=bool)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue
                adjacent |= padded[1 + dy : 1 + dy + height, 1 + dx : 1 + dx + width]
        promote = (state == np.float32(128.0)) & adjacent
        if not bool(promote.any()):
            break
        state[promote] = np.float32(255.0)
    return np.where(state == np.float32(255.0), np.float32(255.0), np.float32(0.0)).astype(
        np.float32, copy=False
    )


def _canny_reference(
    source: np.ndarray,
    *,
    low_threshold: float = 50.0,
    high_threshold: float = 150.0,
    aperture_size: int = 3,
) -> np.ndarray:
    values, low, high = _canny_parameters(
        source,
        {
            "low_threshold": low_threshold,
            "high_threshold": high_threshold,
            "aperture_size": aperture_size,
        },
    )
    return _canny_hysteresis_reference(_canny_local_prefix(values, low, high))


def _clahe_parameters(
    source: np.ndarray, params: Mapping[str, Any]
) -> tuple[np.ndarray, float, tuple[int, int], int]:
    values = _analysis_float_image(source, "clahe_aot")
    clip_limit = float(params.get("clip_limit", 2.0))
    if not np.isfinite(clip_limit) or clip_limit < 0.0 or clip_limit > 64.0:
        raise ValueError("clahe_aot clip_limit must be finite and within [0, 64]")
    grid = params.get("tile_grid_size", (8, 8))
    try:
        grid_values = tuple(grid)
        if len(grid_values) != 2:
            raise ValueError("tile_grid_size must contain exactly two values")
        tiles_x, tiles_y = (int(grid_values[0]), int(grid_values[1]))
    except (TypeError, IndexError, ValueError) as exc:
        raise ValueError("clahe_aot tile_grid_size must be a pair") from exc
    if tiles_x < 1 or tiles_y < 1 or tiles_x > 64 or tiles_y > 64:
        raise ValueError("clahe_aot tile_grid_size values must be in [1, 64]")
    if tiles_x * tiles_y > 1024:
        raise ValueError("clahe_aot tile grid is too large (maximum 1024 tiles)")
    bins = int(params.get("num_bins", 256))
    if bins != 256:
        # The maintained AOT facade hard-codes 256 bins.  Refusing other
        # values avoids a semantic adapter silently diverging from that graph.
        raise ValueError("clahe_aot semantic adapter supports num_bins=256 only")
    if "max_val" in params and float(params["max_val"]) != 255.0:
        raise ValueError("clahe_aot semantic adapter supports max_val=255 only")
    return values, clip_limit, (tiles_x, tiles_y), bins


def _clahe_lut_reference(
    source: np.ndarray,
    *,
    clip_limit: float,
    tile_grid_size: tuple[int, int],
    num_bins: int = 256,
) -> tuple[np.ndarray, int, int]:
    """Build the global histogram/LUT field using the maintained AOT rules."""

    values = _analysis_float_image(source, "clahe_aot")
    height, width = values.shape
    tiles_x, tiles_y = tile_grid_size
    tile_h = (height + tiles_y - 1) // tiles_y
    tile_w = (width + tiles_x - 1) // tiles_x
    tile_pixels = tile_h * tile_w
    beta = max(int(float(clip_limit) * tile_pixels / num_bins), 1)
    hist = np.zeros((tiles_y * tiles_x, num_bins), dtype=np.int32)
    clipped = np.clip(values, 0.0, 255.0)
    bins = np.minimum(
        (clipped * np.float32(num_bins / 255.0)).astype(np.int32),
        num_bins - 1,
    )
    for row in range(height):
        ty = min(row // tile_h, tiles_y - 1)
        for col in range(width):
            tx = min(col // tile_w, tiles_x - 1)
            hist[ty * tiles_x + tx, bins[row, col]] += 1

    lut = np.empty((tiles_y * tiles_x, num_bins), dtype=np.float32)
    for tile in range(tiles_y * tiles_x):
        row = hist[tile]
        excess = 0
        for index in range(num_bins):
            if row[index] > beta:
                excess += int(row[index] - beta)
                row[index] = beta
        redist_batch = excess // num_bins
        residual = excess - redist_batch * num_bins
        row[:] += np.int32(redist_batch)
        if residual > 0:
            step = max(num_bins // residual, 1)
            index = 0
            remaining = residual
            while remaining > 0 and index < num_bins:
                row[index] += 1
                remaining -= 1
                index += step
        cdf = 0
        scale = np.float32(num_bins - 1) / np.float32(tile_pixels)
        for index in range(num_bins):
            cdf += int(row[index])
            lut[tile, index] = np.minimum(np.float32(cdf) * scale, np.float32(num_bins - 1))
    return np.ascontiguousarray(lut, dtype=np.float32), tile_h, tile_w


def _clahe_interpolate_reference(
    source: np.ndarray,
    lut: np.ndarray,
    *,
    tile_grid_size: tuple[int, int],
    tile_h: int,
    tile_w: int,
    block: Optional[BlockSpec] = None,
    source_origin: tuple[int, int] = (0, 0),
) -> np.ndarray:
    values = _analysis_float_image(source, "clahe_aot")
    height, width = values.shape
    origin_y, origin_x = (int(source_origin[0]), int(source_origin[1]))
    tiles_x, tiles_y = tile_grid_size
    bins = int(lut.shape[1])
    if bins != 256 or lut.shape[0] != tiles_x * tiles_y:
        raise ValueError("clahe LUT shape does not match the declared tile grid")
    if block is None:
        y0, y1, x0, x1 = origin_y, origin_y + height, origin_x, origin_x + width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    output = np.empty((y1 - y0, x1 - x0), dtype=np.float32)
    for row in range(y0, y1):
        for col in range(x0, x1):
            local_row, local_col = row - origin_y, col - origin_x
            if not (0 <= local_row < height and 0 <= local_col < width):
                raise ValueError("CLAHE interpolation block is outside its source window")
            value = np.float32(np.clip(values[local_row, local_col], 0.0, 255.0))
            bin_index = min(int(value * np.float32(bins / 255.0)), bins - 1)
            fx = (np.float32(col) - np.float32(tile_w) * np.float32(0.5)) / np.float32(tile_w)
            fy = (np.float32(row) - np.float32(tile_h) * np.float32(0.5)) / np.float32(tile_h)
            tx0 = int(np.floor(fx)); ty0 = int(np.floor(fy))
            tx1, ty1 = tx0 + 1, ty0 + 1
            wx, wy = np.float32(fx - np.float32(tx0)), np.float32(fy - np.float32(ty0))
            tx0 = max(0, min(tiles_x - 1, tx0)); tx1 = max(0, min(tiles_x - 1, tx1))
            ty0 = max(0, min(tiles_y - 1, ty0)); ty1 = max(0, min(tiles_y - 1, ty1))
            tile_tl = ty0 * tiles_x + tx0; tile_tr = ty0 * tiles_x + tx1
            tile_bl = ty1 * tiles_x + tx0; tile_br = ty1 * tiles_x + tx1
            top = lut[tile_tl, bin_index] * (np.float32(1.0) - wx) + lut[tile_tr, bin_index] * wx
            bottom = lut[tile_bl, bin_index] * (np.float32(1.0) - wx) + lut[tile_br, bin_index] * wx
            output[row - y0, col - x0] = (
                (top * (np.float32(1.0) - wy) + bottom * wy)
                * np.float32(255.0) / np.float32(bins - 1)
            )
    return np.ascontiguousarray(output, dtype=np.float32)


def _clahe_reference(
    source: np.ndarray,
    *,
    clip_limit: float = 2.0,
    tile_grid_size: tuple[int, int] = (8, 8),
    num_bins: int = 256,
) -> np.ndarray:
    values, clip, grid, bins = _clahe_parameters(
        source,
        {"clip_limit": clip_limit, "tile_grid_size": tile_grid_size, "num_bins": num_bins},
    )
    lut, tile_h, tile_w = _clahe_lut_reference(
        values, clip_limit=clip, tile_grid_size=grid, num_bins=bins
    )
    result = _clahe_interpolate_reference(
        values, lut, tile_grid_size=grid, tile_h=tile_h, tile_w=tile_w
    )
    # The public AOT wrapper rounds its f32 output before returning it.
    return np.rint(result).astype(np.float32, copy=False)


# ---------------------------------------------------------------------------
# Global/staged semantic oracles (RANSAC flow cleanup / Hough)
# ---------------------------------------------------------------------------
#
# These operations have a bounded map stage but a global model/accumulator.
# The adapters below deliberately keep the reduction and variable-cardinality
# peak stage explicit.  They never turn the legacy global operations into
# automatic/native dispatch.


def _flow_parameters(source: np.ndarray, params: Mapping[str, Any]) -> tuple[np.ndarray, float]:
    values = np.asarray(source)
    if values.ndim != 3 or values.shape[2] != 2 or values.size == 0:
        raise ValueError("ransac_flow_cleanup expects a non-empty HxWx2 flow field")
    if not np.issubdtype(values.dtype, np.number):
        raise TypeError("ransac_flow_cleanup flow must be numeric")
    flow = np.ascontiguousarray(values, dtype=np.float32)
    if not np.isfinite(flow).all():
        raise ValueError("ransac_flow_cleanup flow must contain only finite values")
    threshold = float(params.get("threshold", 1.0))
    if not np.isfinite(threshold) or threshold < 0.0 or threshold > 1.0e4:
        raise ValueError("ransac_flow_cleanup threshold must be finite and in [0, 10000]")
    for name in ("stride_refine", "stride_final"):
        if name in params and int(params[name]) != 1:
            raise ValueError(f"ransac_flow_cleanup semantic adapter supports {name}=1 only")
    return flow, threshold


def _ransac_reference(
    source: np.ndarray,
    *,
    threshold: float = 1.0,
    stride_refine: int = 1,
    stride_final: int = 1,
) -> np.ndarray:
    flow, cutoff = _flow_parameters(
        source,
        {
            "threshold": threshold,
            "stride_refine": stride_refine,
            "stride_final": stride_final,
        },
    )
    vectors = flow.reshape(-1, 2)
    # Float64 accumulation and a fixed row-major reduction order are the
    # semantic contract.  This avoids tile-size-dependent rounding while
    # preserving the graph's mean -> inlier mask -> refined mean -> apply
    # stage ordering.
    model = np.mean(vectors, axis=0, dtype=np.float64) if vectors.size else np.zeros(2, dtype=np.float64)
    squared = np.sum((vectors.astype(np.float64) - model) ** 2, axis=1)
    mask = squared < float(cutoff) * float(cutoff)
    if bool(mask.any()):
        model = np.mean(vectors[mask], axis=0, dtype=np.float64)
    output = vectors.astype(np.float64, copy=True)
    output[~mask] = model
    return np.ascontiguousarray(output.reshape(flow.shape), dtype=np.float32)


def _ransac_partial(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    if len(inputs) != 1:
        raise ValueError("ransac map expects one flow input")
    flow = np.asarray(inputs[0], dtype=np.float32)
    if flow.ndim != 3 or flow.shape[2] != 2:
        raise ValueError("ransac map expects an HxWx2 tile")
    values = flow.reshape(-1, 2).astype(np.float64, copy=False)
    return np.asarray(
        (np.sum(values[:, 0], dtype=np.float64), np.sum(values[:, 1], dtype=np.float64), float(values.shape[0])),
        dtype=np.float64,
    )


def _ransac_partial_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result, dtype=np.float64).reshape(-1)
    return bool(value.shape == (3,) and np.isfinite(value).all() and value[2] >= 0.0)


def _sum_partial_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype)
    if destination.shape != value.shape:
        raise ValueError("global partial accumulator shape mismatch")
    destination[...] += value
    return output


def _ransac_finalize_partial(
    accumulator: np.ndarray,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> np.ndarray:
    flow, cutoff = _flow_parameters(inputs[0], params)
    values = np.asarray(accumulator, dtype=np.float64).reshape(-1)
    if values.shape != (3,) or values[2] <= 0.0:
        return np.ascontiguousarray(flow, dtype=np.float32)
    model = values[:2] / values[2]
    vectors = flow.reshape(-1, 2)
    squared = np.sum((vectors.astype(np.float64) - model) ** 2, axis=1)
    mask = squared < float(cutoff) * float(cutoff)
    if bool(mask.any()):
        # The second reduction is intentionally global and deterministic.
        model = np.mean(vectors[mask], axis=0, dtype=np.float64)
    output = vectors.astype(np.float64, copy=True)
    output[~mask] = model
    return np.ascontiguousarray(output.reshape(flow.shape), dtype=np.float32)


def _hough_parameters(source: np.ndarray, params: Mapping[str, Any]) -> dict[str, Any]:
    edges = np.asarray(source)
    if edges.ndim != 2 or edges.size == 0:
        raise ValueError("hough_lines_aot expects a non-empty 2D edge image")
    if not np.issubdtype(edges.dtype, np.number):
        raise TypeError("hough_lines_aot edge image must be numeric")
    if not np.isfinite(np.asarray(edges, dtype=np.float32)).all():
        raise ValueError("hough_lines_aot edge image must contain only finite values")
    rho_resolution = float(params.get("rho_resolution", 1.0))
    theta_resolution = float(params.get("theta_resolution", 1.0))
    threshold = int(params.get("threshold", 80))
    edge_threshold = float(params.get("edge_threshold", 128.0))
    nms_radius = int(params.get("nms_radius", 10))
    max_peaks = int(params.get("max_peaks", 500))
    # The maintained AOT graph keeps ``rho_offset=diag`` while allocating
    # ``num_rho=int(2*diag/rho_resolution)+1``.  Values above one can make its
    # clamp range exceed the allocated accumulator, so this adapter refuses
    # those historically unsafe variants instead of masking an OOB write.
    if not np.isfinite(rho_resolution) or abs(rho_resolution - 1.0) > 1.0e-6:
        raise ValueError("hough semantic adapter supports rho_resolution=1 only")
    if not np.isfinite(theta_resolution) or theta_resolution <= 0.0 or theta_resolution > 180.0:
        raise ValueError("hough theta_resolution must be finite and in (0, 180]")
    num_theta = int(180.0 / theta_resolution)
    if num_theta < 1 or num_theta > 720:
        raise ValueError("hough theta_resolution yields unsupported theta count")
    if threshold < 0 or threshold > int(edges.shape[0] * edges.shape[1]):
        raise ValueError("hough threshold is outside the image vote range")
    if not np.isfinite(edge_threshold) or edge_threshold < 0.0:
        raise ValueError("hough edge_threshold must be finite and non-negative")
    if nms_radius < 0 or nms_radius > 64:
        raise ValueError("hough nms_radius must be in [0, 64]")
    if max_peaks < 1 or max_peaks > 500:
        raise ValueError("hough max_peaks must be in [1, 500]")
    height, width = edges.shape[:2]
    diag = int(np.sqrt(float(height * height + width * width)))
    num_rho = int(2 * diag / rho_resolution) + 1
    if num_rho < 1 or num_rho > 100000:
        raise ValueError("hough rho_resolution yields an unsupported accumulator")
    # Match the public AOT API's Python-math table construction rather than
    # relying on a backend-specific sin/cos implementation.
    import math

    cos_table = np.asarray(
        [math.cos(math.radians(index * theta_resolution)) for index in range(num_theta)],
        dtype=np.float32,
    )
    sin_table = np.asarray(
        [math.sin(math.radians(index * theta_resolution)) for index in range(num_theta)],
        dtype=np.float32,
    )
    return {
        "rho_resolution": rho_resolution,
        "theta_resolution": theta_resolution,
        "threshold": threshold,
        "edge_threshold": edge_threshold,
        "nms_radius": nms_radius,
        "max_peaks": max_peaks,
        "num_theta": num_theta,
        "rho_offset": diag,
        "num_rho": num_rho,
        "cos_table": cos_table,
        "sin_table": sin_table,
    }


def _hough_vote_partial(
    source: np.ndarray,
    *,
    params: Mapping[str, Any],
    origin: tuple[int, int] = (0, 0),
) -> np.ndarray:
    values = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    resolved = _hough_parameters(values, params) if "num_theta" not in params else dict(params)
    num_rho = int(resolved["num_rho"])
    num_theta = int(resolved["num_theta"])
    rho_offset = int(resolved["rho_offset"])
    cos_table = np.asarray(resolved["cos_table"], dtype=np.float32)
    sin_table = np.asarray(resolved["sin_table"], dtype=np.float32)
    threshold = np.float32(resolved.get("edge_threshold", 128.0))
    output = np.zeros((num_rho, num_theta), dtype=np.int64)
    origin_y, origin_x = int(origin[0]), int(origin[1])
    for row in range(values.shape[0]):
        for col in range(values.shape[1]):
            if np.float32(values[row, col]) < threshold:
                continue
            global_y = np.float32(row + origin_y)
            global_x = np.float32(col + origin_x)
            for index in range(num_theta):
                rho = global_x * cos_table[index] + global_y * sin_table[index]
                rho_bin = int(np.rint(rho) + np.float32(rho_offset))
                rho_bin = max(0, min(2 * rho_offset, rho_bin))
                output[rho_bin, index] += 1
    return output


def _hough_peaks_reference(accumulator: np.ndarray, params: Mapping[str, Any]) -> list[tuple[float, float]]:
    import math

    acc = np.asarray(accumulator)
    threshold = int(params["threshold"])
    nms_radius = int(params["nms_radius"])
    max_peaks = int(params["max_peaks"])
    rho_resolution = float(params["rho_resolution"])
    theta_resolution = float(params["theta_resolution"])
    num_rho, num_theta = acc.shape
    peaks: list[tuple[int, int, int]] = []
    # Row-major order plus strict ``>`` is the deterministic tie contract.
    for rho_index in range(num_rho):
        for theta_index in range(num_theta):
            votes = int(acc[rho_index, theta_index])
            if votes < threshold:
                continue
            is_max = True
            for dr in range(-nms_radius, nms_radius + 1):
                for dt in range(-nms_radius, nms_radius + 1):
                    if dr == 0 and dt == 0:
                        continue
                    neighbour_rho = rho_index + dr
                    neighbour_theta = theta_index + dt
                    if (
                        0 <= neighbour_rho < num_rho
                        and 0 <= neighbour_theta < num_theta
                        and int(acc[neighbour_rho, neighbour_theta]) > votes
                    ):
                        is_max = False
                        break
                if not is_max:
                    break
            if is_max:
                peaks.append((rho_index, theta_index, votes))
                if len(peaks) >= max_peaks:
                    break
        if len(peaks) >= max_peaks:
            break
    return [
        (
            np.float32((rho_index - int(params["rho_offset"])) * np.float32(rho_resolution)),
            np.float32(theta_index * np.float32(theta_resolution) * np.float32(math.pi / 180.0)),
        )
        for rho_index, theta_index, _votes in peaks
    ]


def _hough_reference(
    source: np.ndarray,
    *,
    rho_resolution: float = 1.0,
    theta_resolution: float = 1.0,
    threshold: int = 80,
    nms_radius: int = 10,
    max_peaks: int = 500,
    edge_threshold: float = 128.0,
) -> list[tuple[float, float]]:
    values = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    params = _hough_parameters(
        values,
        {
            "rho_resolution": rho_resolution,
            "theta_resolution": theta_resolution,
            "threshold": threshold,
            "nms_radius": nms_radius,
            "max_peaks": max_peaks,
            "edge_threshold": edge_threshold,
        },
    )
    accumulator = _hough_vote_partial(values, params=params)
    return _hough_peaks_reference(accumulator, params)


# ---------------------------------------------------------------------------
# Staged semantic oracle (MTB alignment)
# ---------------------------------------------------------------------------
#
# MTB has two bounded map/reduce stages (histograms and shifted error sums)
# surrounding a global, deterministic 3x3 search at each pyramid level.  The
# adapter below partitions only those independent map stages.  Pyramid
# construction, median selection, bitmap/exclusion materialisation, and the
# level-to-level displacement update remain explicit stage boundaries.  This
# is a CPU semantic proof only; it intentionally does not alter the legacy
# ``align_mtb`` dispatch or claim native GPU parity.

_MTB_PARTITION_ADAPTER_OPERATIONS = ("align_mtb",)


def _mtb_parameters(
    ref_source: np.ndarray,
    target_source: np.ndarray,
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray, int, float]:
    """Validate and canonicalize the bounded semantic MTB parameter set."""

    ref = np.asarray(ref_source)
    target = np.asarray(target_source)
    if ref.ndim not in (2, 3) or target.ndim != ref.ndim:
        raise ValueError("align_mtb expects matching 2D images or HxWx3 images")
    if ref.ndim == 3 and (ref.shape[2] != 3 or target.shape[2] != 3):
        raise ValueError("align_mtb color inputs must have exactly three channels")
    if ref.shape[:2] != target.shape[:2] or ref.size == 0:
        raise ValueError("align_mtb inputs must be non-empty and shape matched")
    if not np.issubdtype(ref.dtype, np.number) or not np.issubdtype(target.dtype, np.number):
        raise TypeError("align_mtb inputs must be numeric")
    if not np.isfinite(np.asarray(ref, dtype=np.float32)).all() or not np.isfinite(
        np.asarray(target, dtype=np.float32)
    ).all():
        raise ValueError("align_mtb inputs must contain only finite values")
    max_levels = int(params.get("max_levels", 6))
    if max_levels < 1 or max_levels > 12:
        raise ValueError("align_mtb max_levels must be in [1, 12]")
    tolerance = float(params.get("tolerance", 4.0 / 255.0))
    if not np.isfinite(tolerance) or tolerance < 0.0 or tolerance > 1.0:
        raise ValueError("align_mtb tolerance must be finite and in [0, 1]")

    def gray(value: np.ndarray) -> np.ndarray:
        array = np.ascontiguousarray(value)
        if array.ndim == 3:
            array = _rgb2gray_reference(array)
        # The maintained MTB graph receives float32 [0, 1] values after the
        # public wrapper's conversion.  Keep that conversion explicit so all
        # partition sizes observe one shared quantization convention.
        result = np.ascontiguousarray(array, dtype=np.float32) / np.float32(255.0)
        return np.ascontiguousarray(result, dtype=np.float32)

    return gray(ref), gray(target), max_levels, tolerance


def _mtb_reflect101(index: int, size: int) -> int:
    """Scalar REFLECT_101 index matching the pyramid AOT kernel."""

    size = int(size)
    if size <= 1:
        return 0
    period = 2 * (size - 1)
    value = int(index) % period
    return value if value < size else period - value


def _mtb_downsample(source: np.ndarray) -> np.ndarray:
    """One 5x5 Gaussian/2x downsample with REFLECT_101 borders."""

    values = np.ascontiguousarray(source, dtype=np.float32)
    height, width = values.shape
    next_height, next_width = height // 2, width // 2
    if next_height < 1 or next_width < 1:
        return np.ascontiguousarray(values, dtype=np.float32)
    weights = (1.0, 4.0, 6.0, 4.0, 1.0)
    output = np.empty((next_height, next_width), dtype=np.float32)
    for row in range(next_height):
        source_y = row * 2
        for col in range(next_width):
            source_x = col * 2
            value = np.float32(0.0)
            for dy in range(-2, 3):
                mapped_y = _mtb_reflect101(source_y + dy, height)
                for dx in range(-2, 3):
                    mapped_x = _mtb_reflect101(source_x + dx, width)
                    value = np.float32(
                        value
                        + values[mapped_y, mapped_x]
                        * np.float32(weights[dy + 2] * weights[dx + 2])
                    )
            output[row, col] = np.float32(value / np.float32(256.0))
    return np.ascontiguousarray(output, dtype=np.float32)


def _mtb_pyramid(source: np.ndarray, levels: int) -> list[np.ndarray]:
    pyramid = [np.ascontiguousarray(source, dtype=np.float32)]
    for _ in range(int(levels) - 1):
        current = pyramid[-1]
        if current.shape[0] // 2 < 1 or current.shape[1] // 2 < 1:
            break
        next_level = _mtb_downsample(current)
        if next_level.shape == current.shape:
            break
        pyramid.append(next_level)
    return pyramid


def _mtb_histogram(source: np.ndarray) -> np.ndarray:
    """Return the 256-bin truncating histogram used by ``mtb_histogram_f32``."""

    values = np.asarray(source, dtype=np.float32)
    quantized = np.floor(np.clip(values * np.float32(255.0), 0.0, 255.0)).astype(
        np.int32,
        copy=False,
    )
    return np.bincount(quantized.reshape(-1), minlength=256).astype(np.int64, copy=False)


def _mtb_median(histogram: np.ndarray, total: int) -> float:
    counts = np.asarray(histogram, dtype=np.int64).reshape(-1)
    cumulative = 0
    target = int(total) // 2
    for index in range(min(256, counts.size)):
        cumulative += int(counts[index])
        if cumulative >= target:
            return float(index) / 255.0
    return 0.5


def _mtb_bitmaps(source: np.ndarray, median: float, tolerance: float) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(source, dtype=np.float32)
    bitmap = (values > np.float32(median)).astype(np.int32, copy=False)
    exclusion = (np.abs(values - np.float32(median)) > np.float32(tolerance)).astype(
        np.int32,
        copy=False,
    )
    return np.ascontiguousarray(bitmap), np.ascontiguousarray(exclusion)


def _mtb_error_block(
    bitmap_ref: np.ndarray,
    exclusion_ref: np.ndarray,
    bitmap_target: np.ndarray,
    exclusion_target: np.ndarray,
    block: Optional[BlockSpec],
    dx: int,
    dy: int,
) -> int:
    """Compute one source block's deterministic MTB error contribution."""

    height, width = bitmap_ref.shape
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1 = int(block.y0), int(block.y1)
        x0, x1 = int(block.x0), int(block.x1)
    if y0 >= y1 or x0 >= x1:
        return 0
    # Every out-of-bounds source sample contributes one error, irrespective of
    # bitmap/exclusion state, matching mtb_error_f32's explicit penalty.
    total = (y1 - y0) * (x1 - x0)
    source_y0 = max(y0, -int(dy))
    source_y1 = min(y1, height - int(dy))
    source_x0 = max(x0, -int(dx))
    source_x1 = min(x1, width - int(dx))
    if source_y0 >= source_y1 or source_x0 >= source_x1:
        return int(total)
    ref_bitmap = bitmap_ref[source_y0:source_y1, source_x0:source_x1]
    tgt_bitmap = bitmap_target[
        source_y0 + int(dy): source_y1 + int(dy),
        source_x0 + int(dx): source_x1 + int(dx),
    ]
    ref_exclusion = exclusion_ref[source_y0:source_y1, source_x0:source_x1]
    tgt_exclusion = exclusion_target[
        source_y0 + int(dy): source_y1 + int(dy),
        source_x0 + int(dx): source_x1 + int(dx),
    ]
    valid = ref_exclusion.astype(np.int64) & tgt_exclusion.astype(np.int64)
    mismatches = np.bitwise_xor(ref_bitmap, tgt_bitmap).astype(np.int64)
    overlap_error = int(np.sum(valid * mismatches, dtype=np.int64))
    overlap_size = int((source_y1 - source_y0) * (source_x1 - source_x0))
    return int(overlap_error + total - overlap_size)


def _mtb_error_full(
    bitmap_ref: np.ndarray,
    exclusion_ref: np.ndarray,
    bitmap_target: np.ndarray,
    exclusion_target: np.ndarray,
    dx: int,
    dy: int,
) -> int:
    return _mtb_error_block(
        bitmap_ref, exclusion_ref, bitmap_target, exclusion_target, None, dx, dy
    )


def _mtb_alignment_impl(
    ref_source: np.ndarray,
    target_source: np.ndarray,
    *,
    max_levels: int,
    tolerance: float,
    block_size: int | tuple[int, int] | None,
) -> tuple[int, int]:
    ref, target, levels, cutoff = _mtb_parameters(
        ref_source,
        target_source,
        {"max_levels": max_levels, "tolerance": tolerance},
    )
    ref_pyramid = _mtb_pyramid(ref, levels)
    target_pyramid = _mtb_pyramid(target, levels)
    current_dx, current_dy = 0, 0
    for level in reversed(range(len(ref_pyramid))):
        ref_level = ref_pyramid[level]
        target_level = target_pyramid[level]
        height, width = ref_level.shape
        current_dx *= 2
        current_dy *= 2
        if block_size is None:
            ref_hist = _mtb_histogram(ref_level)
            target_hist = _mtb_histogram(target_level)
        else:
            grid = BlockGrid(ref_level.shape, size=block_size)
            ref_hist = np.zeros(256, dtype=np.int64)
            target_hist = np.zeros(256, dtype=np.int64)
            for block in sorted(tuple(grid), key=lambda item: int(item.index)):
                ref_hist += _mtb_histogram(ref_level[block.read_slice])
                target_hist += _mtb_histogram(target_level[block.read_slice])
        ref_median = _mtb_median(ref_hist, height * width)
        target_median = _mtb_median(target_hist, height * width)
        ref_bitmap, ref_exclusion = _mtb_bitmaps(ref_level, ref_median, cutoff)
        target_bitmap, target_exclusion = _mtb_bitmaps(target_level, target_median, cutoff)
        best_error = 2**31 - 1
        best_offset = (0, 0)
        grid = None if block_size is None else BlockGrid(ref_level.shape, size=block_size)
        blocks = (None,) if grid is None else tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
        for offset_y in (-1, 0, 1):
            for offset_x in (-1, 0, 1):
                test_dx = current_dx + offset_x
                test_dy = current_dy + offset_y
                if grid is None:
                    error = _mtb_error_full(
                        ref_bitmap,
                        ref_exclusion,
                        target_bitmap,
                        target_exclusion,
                        test_dx,
                        test_dy,
                    )
                else:
                    error = sum(
                        _mtb_error_block(
                            ref_bitmap,
                            ref_exclusion,
                            target_bitmap,
                            target_exclusion,
                            block,
                            test_dx,
                            test_dy,
                        )
                        for block in blocks
                    )
                if error < best_error:
                    best_error = int(error)
                    best_offset = (offset_x, offset_y)
        current_dx += best_offset[0]
        current_dy += best_offset[1]
    return int(current_dx), int(current_dy)


def _mtb_reference(
    ref_source: np.ndarray,
    target_source: np.ndarray,
    *,
    max_levels: int = 6,
    tolerance: float = 4.0 / 255.0,
) -> tuple[int, int]:
    return _mtb_alignment_impl(
        ref_source,
        target_source,
        max_levels=max_levels,
        tolerance=tolerance,
        block_size=None,
    )


def _mtb_map_runner(context: Any) -> np.ndarray:
    arrays = _as_inputs(context)
    if len(arrays) != 2:
        raise ValueError("align_mtb map expects reference and target tiles")
    return np.stack((_mtb_histogram(arrays[0]), _mtb_histogram(arrays[1])), axis=0)


def _mtb_map_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(value.shape == (2, 256) and np.issubdtype(value.dtype, np.integer) and np.all(value >= 0))


def _mtb_map_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype)
    if destination.shape != value.shape:
        raise ValueError("align_mtb histogram accumulator shape mismatch")
    destination[...] += value
    return output


def _run_mtb_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> tuple[int, int]:
    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        canonical not in _MTB_PARTITION_ADAPTER_OPERATIONS
        or adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete MTB adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 2:
        raise ValueError("align_mtb adapter expects reference and target inputs")
    values = dict(params or {})
    _ref, _target, max_levels, tolerance = _mtb_parameters(arrays[0], arrays[1], values)
    return _mtb_alignment_impl(
        arrays[0],
        arrays[1],
        max_levels=max_levels,
        tolerance=tolerance,
        block_size=block_size,
    )


def run_mtb_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> tuple[int, int]:
    """Run the explicit CPU MTB histogram/error partition contract."""

    return _run_mtb_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_mtb_partition_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Compare deterministic full-frame and partitioned MTB alignment."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_mtb_partition_tiled(canonical, arrays, block_size=block_size, params=values)
    adapter = lookup_block_adapter(canonical)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_mtb_staged_map_reduce",
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[0].shape, size=block_size).block_height,
            BlockGrid(arrays[0].shape, size=block_size).block_width,
        ),
        "passed": bool(tuple(full) == tuple(tiled)),
        "max_abs_error": float(max(abs(int(left) - int(right)) for left, right in zip(full, tiled))),
        "deterministic_merge": bool(adapter.metadata.get("deterministic_merge", False)) if adapter else False,
        "stage_contract": dict(adapter.metadata.get("stage_contract", {})) if adapter else {},
        "native_runtime": False,
    }


# ---------------------------------------------------------------------------
# Coordinate/output-domain semantic oracle (joint bilateral upsample)
# ---------------------------------------------------------------------------
#
# JBLU is a pointwise map over the *high-resolution guide domain*.  Each
# destination pixel reads a bounded 5x5 low-resolution neighbourhood and a
# guide sample selected by the same floor/clamp/round coordinates as the AOT
# graph.  Partitioning therefore slices only the output grid; source/guide
# arrays remain immutable shared inputs.  The adapter is explicit CPU semantic
# evidence and never promotes the legacy global operation to AUTO/native.

_JBLU_PARTITION_ADAPTER_OPERATIONS = ("joint_bilateral_upsample",)
_JBLU_PRESETS = {
    "high": (0.8, 0.05),
    "medium": (1.5, 0.10),
    "low": (2.5, 0.20),
}


def _jblu_parameters(
    source_input: np.ndarray,
    guide_input: np.ndarray,
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray, str, float, float]:
    source = np.asarray(source_input)
    guide = np.asarray(guide_input)
    if source.ndim not in (2, 3) or source.size == 0:
        raise ValueError("joint_bilateral_upsample expects a non-empty 2D/3D source")
    if source.ndim == 3 and source.shape[2] not in (1, 2, 3):
        raise ValueError("joint_bilateral_upsample source channels must be 1, 2, or 3")
    if guide.ndim not in (2, 3) or guide.size == 0:
        raise ValueError("joint_bilateral_upsample expects a non-empty 2D/3D guide")
    if guide.ndim == 3 and guide.shape[2] != 3:
        raise ValueError("joint_bilateral_upsample guide must be grayscale or 3-channel")
    # The maintained native JBLU graphs are f32-only.  Keep unsupported
    # source dtypes fail-closed rather than silently changing the public
    # fallback's interpolation semantics.
    if np.dtype(source.dtype) != np.dtype(np.float32):
        raise TypeError("joint_bilateral_upsample semantic adapter requires float32 source")
    if not np.issubdtype(guide.dtype, np.number):
        raise TypeError("joint_bilateral_upsample guide must be numeric")
    if not np.isfinite(source).all() or not np.isfinite(np.asarray(guide, dtype=np.float32)).all():
        raise ValueError("joint_bilateral_upsample inputs must contain only finite values")
    preset = str(params.get("preset", "medium")).lower()
    if preset not in _JBLU_PRESETS:
        raise ValueError("joint_bilateral_upsample preset must be low, medium, or high")
    sigma_s, sigma_r = _JBLU_PRESETS[preset]
    inv_space = float(1.0 / (2.0 * sigma_s * sigma_s))
    inv_range = float(1.0 / (2.0 * sigma_r * sigma_r))

    guide_values = np.ascontiguousarray(guide, dtype=np.float32)
    if guide_values.ndim == 3:
        # The AOT guide preparation treats a 3-channel input as BGR.
        guide_values = (
            np.float32(0.299) * guide_values[..., 2]
            + np.float32(0.587) * guide_values[..., 1]
            + np.float32(0.114) * guide_values[..., 0]
        )
    peak = float(np.max(guide_values)) if guide_values.size else 0.0
    if peak > 1.0:
        guide_values = guide_values / np.float32(255.0 if peak <= 255.0 else 65535.0)
    return (
        np.ascontiguousarray(source, dtype=np.float32),
        np.ascontiguousarray(guide_values, dtype=np.float32),
        preset,
        inv_space,
        inv_range,
    )


def _jblu_compute(
    source: np.ndarray,
    guide: np.ndarray,
    *,
    inv_space: float,
    inv_range: float,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    source_values = np.asarray(source, dtype=np.float32)
    guide_values = np.asarray(guide, dtype=np.float32)
    h_low, w_low = source_values.shape[:2]
    height, width = guide_values.shape
    scale_y = np.float32(float(height) / float(h_low))
    scale_x = np.float32(float(width) / float(w_low))
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in source_values.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    vector_source = source_values.ndim == 3
    for row in range(y0, y1):
        low_y = int(np.floor(np.float32(row) * np.float32(h_low) / np.float32(height)))
        center_row = guide_values[row]
        for col in range(x0, x1):
            low_x = int(np.floor(np.float32(col) * np.float32(w_low) / np.float32(width)))
            center_guide = np.float32(center_row[col])
            total_weight = np.float32(1.0e-12)
            if vector_source:
                accumulated = np.zeros(trailing, dtype=np.float32)
            else:
                accumulated = np.float32(0.0)
            for dy in range(-2, 3):
                sample_y = max(0, min(h_low - 1, low_y + dy))
                guide_y = max(
                    0,
                    min(
                        height - 1,
                        int(np.float32(sample_y) * np.float32(height) / np.float32(h_low) + np.float32(0.5)),
                    ),
                )
                for dx in range(-2, 3):
                    sample_x = max(0, min(w_low - 1, low_x + dx))
                    guide_x = max(
                        0,
                        min(
                            width - 1,
                            int(np.float32(sample_x) * np.float32(width) / np.float32(w_low) + np.float32(0.5)),
                        ),
                    )
                    guide_delta = np.float32(guide_values[guide_y, guide_x] - center_guide)
                    weight = np.float32(
                        np.exp(
                            -np.float32(dx * dx + dy * dy) * np.float32(inv_space)
                            -guide_delta * guide_delta * np.float32(inv_range)
                        )
                    )
                    total_weight = np.float32(total_weight + weight)
                    accumulated = np.asarray(
                        accumulated + source_values[sample_y, sample_x] * weight,
                        dtype=np.float32,
                    )
            result = np.asarray(accumulated / total_weight, dtype=np.float32)
            if vector_source and trailing[0] == 2:
                # The flow graph stores x/y in channel order and rescales to
                # the high-resolution coordinate domain.
                result = np.asarray(
                    (result[0] * scale_x, result[1] * scale_y), dtype=np.float32
                )
            output[row - y0, col - x0] = result
    return np.ascontiguousarray(output, dtype=np.float32)


def _jblu_reference(
    source_input: np.ndarray,
    guide_input: np.ndarray,
    *,
    preset: str = "medium",
) -> np.ndarray:
    source, guide, _preset, inv_space, inv_range = _jblu_parameters(
        source_input, guide_input, {"preset": preset}
    )
    return _jblu_compute(source, guide, inv_space=inv_space, inv_range=inv_range)


def _jblu_reader(first: Any, second: Any) -> Any:
    if isinstance(first, BlockSpec):
        return tuple(np.asarray(value) for value in second)
    context, block = first, second
    arrays = _as_inputs(context)
    return PartitionContext(
        operation="joint_bilateral_upsample",
        inputs=arrays,
        block=block,
        full_shape=tuple(_context_value(context, "full_shape", ())),
        output_shape=tuple(_context_value(context, "output_shape", ())),
        params=_as_params(context),
    )


def _jblu_runner(context: Any) -> np.ndarray:
    arrays = _as_inputs(context)
    if len(arrays) != 2:
        raise ValueError("joint_bilateral_upsample map expects source and guide")
    source, guide, _preset, inv_space, inv_range = _jblu_parameters(
        arrays[0], arrays[1], _as_params(context)
    )
    return _jblu_compute(
        source,
        guide,
        inv_space=inv_space,
        inv_range=inv_range,
        block=_context_value(context, "block"),
    )


def _jblu_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(value.ndim in (2, 3) and value.size > 0 and np.isfinite(value).all())


def _jblu_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = _context_value(context_or_block, "block", context_or_block)
    if block is None:
        raise ValueError("joint_bilateral_upsample merge requires an output block")
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype)
    destination[block.write_slice] = value
    return output


def _run_jblu_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        canonical not in _JBLU_PARTITION_ADAPTER_OPERATIONS
        or adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete JBLU adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 2:
        raise ValueError("joint_bilateral_upsample adapter expects source and guide inputs")
    values = dict(params or {})
    source, guide, _preset, inv_space, inv_range = _jblu_parameters(
        arrays[0], arrays[1], values
    )
    output_shape = guide.shape + tuple(source.shape[2:])
    output = np.empty(output_shape, dtype=np.float32)
    grid = BlockGrid(guide.shape, size=block_size)
    for block in sorted(tuple(grid), key=lambda item: int(item.index)):
        tile = _jblu_compute(
            source,
            guide,
            inv_space=inv_space,
            inv_range=inv_range,
            block=block,
        )
        output[block.write_slice] = tile
    return np.ascontiguousarray(output, dtype=np.float32)


def run_jblu_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run explicit semantic CPU JBLU output-domain blocks."""

    return _run_jblu_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_jblu_partition_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 1.0e-6,
    atol: float = 1.0e-6,
) -> dict[str, Any]:
    """Compare full-frame and output-domain JBLU semantic results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_jblu_partition_tiled(canonical, arrays, block_size=block_size, params=values)
    left = np.asarray(full, dtype=np.float64)
    right = np.asarray(tiled, dtype=np.float64)
    error = float(np.max(np.abs(left - right))) if left.size else 0.0
    adapter = lookup_block_adapter(canonical)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_jblu_output_domain",
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[1].shape, size=block_size).block_height,
            BlockGrid(arrays[1].shape, size=block_size).block_width,
        ),
        "output_shape": list(left.shape),
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "deterministic_merge": bool(adapter.metadata.get("deterministic_merge", False)) if adapter else False,
        "native_runtime": False,
    }


# ---------------------------------------------------------------------------
# Staged semantic oracle (bilateral grid)
# ---------------------------------------------------------------------------
#
# Bilateral-grid filtering has a global splat/reduction followed by independent
# separable blur stages and an output-domain trilinear slice.  The adapter
# partitions only input splat contributions and the final slice; the complete
# grid remains the explicit stage boundary.  Float64 accumulators and a fixed
# row-major merge make the CPU semantic result invariant to block size.

_BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS = ("bilateral_grid_filter",)
_BILATERAL_GRID_PRESETS = {
    "light": (32, 32, 1.0, 1.0),
    "medium": (16, 16, 1.0, 1.0),
    "heavy": (8, 8, 2.0, 1.5),
}


def _bilateral_grid_parameters(
    source_input: np.ndarray,
    params: Mapping[str, Any],
) -> tuple[np.ndarray, str, int, int, float, float, tuple[int, int, int]]:
    source = np.asarray(source_input)
    if source.ndim not in (2, 3) or source.size == 0:
        raise ValueError("bilateral_grid_filter expects a non-empty 2D/3D image")
    if source.ndim == 3 and source.shape[2] != 3:
        raise ValueError("bilateral_grid_filter semantic adapter supports 3 channels only")
    if np.dtype(source.dtype) != np.dtype(np.float32):
        raise TypeError("bilateral_grid_filter semantic adapter requires float32 source")
    if not np.isfinite(source).all():
        raise ValueError("bilateral_grid_filter source must contain only finite values")
    preset = str(params.get("preset", "medium")).lower()
    if preset not in _BILATERAL_GRID_PRESETS:
        raise ValueError("bilateral_grid_filter preset must be light, medium, or heavy")
    s_s, s_r, sigma_s, sigma_r = _BILATERAL_GRID_PRESETS[preset]
    height, width = source.shape[:2]
    grid_shape = (
        (height + s_s - 1) // s_s + 2,
        (width + s_s - 1) // s_s + 2,
        256 // s_r + 2,
    )
    return (
        np.ascontiguousarray(source, dtype=np.float32),
        preset,
        int(s_s),
        int(s_r),
        float(sigma_s),
        float(sigma_r),
        tuple(int(value) for value in grid_shape),
    )


def _bilateral_grid_round(value: float) -> int:
    # Inputs are image intensities; use a documented half-up rule rather than
    # NumPy's banker rounding so map contributions are backend-independent.
    return int(np.floor(float(value) + 0.5))


def _bilateral_grid_splat(
    source: np.ndarray,
    *,
    s_s: int,
    s_r: int,
    grid_shape: tuple[int, int, int],
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    values = np.asarray(source, dtype=np.float32)
    height, width = values.shape[:2]
    gn, gm, gl = grid_shape
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    channels = int(values.shape[2]) if values.ndim == 3 else 1
    grid = np.zeros((gn, gm, gl, 2 * channels), dtype=np.float64)
    for row in range(y0, y1):
        for col in range(x0, x1):
            sample = values[row, col]
            gx = max(0, min(gn - 1, _bilateral_grid_round(float(row) / float(s_s))))
            gy = max(0, min(gm - 1, _bilateral_grid_round(float(col) / float(s_s))))
            if channels == 1:
                scalar = float(sample)
                gz = max(0, min(gl - 1, _bilateral_grid_round(scalar / float(s_r))))
                grid[gx, gy, gz, 0] += scalar
                grid[gx, gy, gz, 1] += 1.0
            else:
                for channel in range(channels):
                    scalar = float(sample[channel])
                    gz = max(0, min(gl - 1, _bilateral_grid_round(scalar / float(s_r))))
                    grid[gx, gy, gz, 2 * channel] += scalar
                    grid[gx, gy, gz, 2 * channel + 1] += 1.0
    return grid


def _bilateral_grid_blur(
    source: np.ndarray,
    *,
    axis: int,
    radius: int,
    sigma: float,
) -> np.ndarray:
    values = np.asarray(source, dtype=np.float64)
    output = np.empty_like(values)
    size = values.shape[axis]
    weights = np.asarray(
        [np.exp(-float(offset * offset) / (2.0 * float(sigma) * float(sigma))) for offset in range(-radius, radius + 1)],
        dtype=np.float64,
    )
    total_weight = float(np.sum(weights, dtype=np.float64))
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            for k in range(values.shape[2]):
                accumulator = np.zeros(values.shape[3], dtype=np.float64)
                for offset, weight in zip(range(-radius, radius + 1), weights):
                    index = max(0, min(size - 1, (i, j, k)[axis] + offset))
                    coords = [i, j, k]
                    coords[axis] = index
                    accumulator += values[coords[0], coords[1], coords[2]] * weight
                output[i, j, k] = accumulator / total_weight
    return output


def _bilateral_grid_trilinear(
    grid: np.ndarray,
    *,
    u: float,
    v: float,
    w: float,
    channels: int,
) -> np.ndarray:
    gn, gm, gl = grid.shape[:3]
    i_int, j_int, k_int = int(np.floor(u)), int(np.floor(v)), int(np.floor(w))
    fi, fj, fk = np.float64(u - i_int), np.float64(v - j_int), np.float64(w - k_int)

    # Each lane carries [numerator, denominator]; interpolate independently.
    lane_count = 2 * channels
    def lane(i: int, j: int, k: int) -> np.ndarray:
        ii = max(0, min(gn - 1, i)); jj = max(0, min(gm - 1, j)); kk = max(0, min(gl - 1, k))
        return grid[ii, jj, kk, :lane_count]

    v000 = lane(i_int, j_int, k_int); v100 = lane(i_int + 1, j_int, k_int)
    v010 = lane(i_int, j_int + 1, k_int); v110 = lane(i_int + 1, j_int + 1, k_int)
    v001 = lane(i_int, j_int, k_int + 1); v101 = lane(i_int + 1, j_int, k_int + 1)
    v011 = lane(i_int, j_int + 1, k_int + 1); v111 = lane(i_int + 1, j_int + 1, k_int + 1)
    m00 = v000 * (1.0 - fi) + v100 * fi
    m10 = v010 * (1.0 - fi) + v110 * fi
    m01 = v001 * (1.0 - fi) + v101 * fi
    m11 = v011 * (1.0 - fi) + v111 * fi
    n0 = m00 * (1.0 - fj) + m10 * fj
    n1 = m01 * (1.0 - fj) + m11 * fj
    interpolated = n0 * (1.0 - fk) + n1 * fk
    result = np.empty(channels, dtype=np.float64)
    for channel in range(channels):
        result[channel] = (
            interpolated[2 * channel] / interpolated[2 * channel + 1]
            if interpolated[2 * channel + 1] > 1.0e-6
            else np.nan
        )
    return result


def _bilateral_grid_slice(
    source: np.ndarray,
    grid: np.ndarray,
    *,
    s_s: int,
    s_r: int,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    values = np.asarray(source, dtype=np.float32)
    height, width = values.shape[:2]
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    channels = int(values.shape[2]) if values.ndim == 3 else 1
    output_shape = (y1 - y0, x1 - x0, channels) if channels > 1 else (y1 - y0, x1 - x0)
    output = np.empty(output_shape, dtype=np.float32)
    for row in range(y0, y1):
        for col in range(x0, x1):
            sample = values[row, col]
            scalar = float(sample[0] if channels > 1 else sample)
            # The source intensity coordinate is per-channel in the native
            # RGB loop; process each channel independently below.
            if channels == 1:
                result = _bilateral_grid_trilinear(
                    grid,
                    u=float(row) / float(s_s),
                    v=float(col) / float(s_s),
                    w=scalar / float(s_r),
                    channels=1,
                )[0]
                output[row - y0, col - x0] = np.float32(result if np.isfinite(result) else scalar)
            else:
                result_values = np.empty(channels, dtype=np.float32)
                for channel in range(channels):
                    result = _bilateral_grid_trilinear(
                        grid[channel],
                        u=float(row) / float(s_s),
                        v=float(col) / float(s_s),
                        w=float(values[row, col, channel]) / float(s_r),
                        channels=1,
                    )[0]
                    result_values[channel] = np.float32(
                        result if np.isfinite(result) else values[row, col, channel]
                    )
                output[row - y0, col - x0] = result_values
    return np.ascontiguousarray(output, dtype=np.float32)


def _bilateral_grid_reference(source_input: np.ndarray, *, preset: str = "medium") -> np.ndarray:
    source, _preset, s_s, s_r, sigma_s, sigma_r, grid_shape = _bilateral_grid_parameters(
        source_input, {"preset": preset}
    )
    channels = int(source.shape[2]) if source.ndim == 3 else 1
    if channels == 1:
        grid = _bilateral_grid_splat(
            source, s_s=s_s, s_r=s_r, grid_shape=grid_shape
        )
        radius_s, radius_r = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))
        blurred = _bilateral_grid_blur(grid, axis=0, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=1, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=2, radius=radius_r, sigma=sigma_r)
        return _bilateral_grid_slice(source, blurred, s_s=s_s, s_r=s_r)
    outputs = []
    for channel in range(channels):
        channel_source = source[..., channel]
        channel_grid = _bilateral_grid_splat(
            channel_source, s_s=s_s, s_r=s_r, grid_shape=grid_shape
        )
        radius_s, radius_r = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))
        blurred = _bilateral_grid_blur(channel_grid, axis=0, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=1, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=2, radius=radius_r, sigma=sigma_r)
        outputs.append(_bilateral_grid_slice(channel_source, blurred, s_s=s_s, s_r=s_r))
    return np.ascontiguousarray(np.stack(outputs, axis=-1), dtype=np.float32)


def _bilateral_grid_partial_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(value.ndim == 4 and value.shape[-1] == 2 and np.isfinite(value).all())


def _bilateral_grid_partial_runner(context: Any) -> np.ndarray:
    arrays = _as_inputs(context)
    if len(arrays) != 1:
        raise ValueError("bilateral grid map expects one source input")
    source, _preset, s_s, s_r, _sigma_s, _sigma_r, grid_shape = _bilateral_grid_parameters(
        arrays[0], _as_params(context)
    )
    return _bilateral_grid_splat(
        source,
        s_s=s_s,
        s_r=s_r,
        grid_shape=grid_shape,
        block=_context_value(context, "block"),
    )


def _bilateral_grid_partial_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype)
    if destination.shape != value.shape:
        raise ValueError("bilateral grid partial shape mismatch")
    destination[...] += value
    return output


def _bilateral_grid_partial_reader(first: Any, second: Any) -> Any:
    return _global_reader(first, second)


def _run_bilateral_grid_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        canonical not in _BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS
        or adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete bilateral-grid adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 1:
        raise ValueError("bilateral_grid_filter adapter expects one source input")
    source, _preset, s_s, s_r, sigma_s, sigma_r, grid_shape = _bilateral_grid_parameters(
        arrays[0], dict(params or {})
    )
    channels = int(source.shape[2]) if source.ndim == 3 else 1
    if channels == 1:
        accumulator = np.zeros((*grid_shape, 2), dtype=np.float64)
        grid = BlockGrid(source.shape, size=block_size)
        for block in sorted(tuple(grid), key=lambda item: int(item.index)):
            accumulator += _bilateral_grid_splat(
                source,
                s_s=s_s,
                s_r=s_r,
                grid_shape=grid_shape,
                block=block,
            )
        radius_s, radius_r = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))
        blurred = _bilateral_grid_blur(accumulator, axis=0, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=1, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=2, radius=radius_r, sigma=sigma_r)
        output = np.empty(source.shape, dtype=np.float32)
        for block in sorted(tuple(BlockGrid(source.shape, size=block_size)), key=lambda item: int(item.index)):
            output[block.write_slice] = _bilateral_grid_slice(
                source, blurred, s_s=s_s, s_r=s_r, block=block
            )
        return output
    output = np.empty(source.shape, dtype=np.float32)
    for channel in range(channels):
        channel_source = source[..., channel]
        accumulator = np.zeros((*grid_shape, 2), dtype=np.float64)
        grid = BlockGrid(channel_source.shape, size=block_size)
        for block in sorted(tuple(grid), key=lambda item: int(item.index)):
            accumulator += _bilateral_grid_splat(
                channel_source,
                s_s=s_s,
                s_r=s_r,
                grid_shape=grid_shape,
                block=block,
            )
        radius_s, radius_r = int(np.ceil(sigma_s * 3.0)), int(np.ceil(sigma_r * 3.0))
        blurred = _bilateral_grid_blur(accumulator, axis=0, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=1, radius=radius_s, sigma=sigma_s)
        blurred = _bilateral_grid_blur(blurred, axis=2, radius=radius_r, sigma=sigma_r)
        for block in sorted(tuple(BlockGrid(channel_source.shape, size=block_size)), key=lambda item: int(item.index)):
            output[block.write_slice + (channel,)] = _bilateral_grid_slice(
                channel_source, blurred, s_s=s_s, s_r=s_r, block=block
            )
    return np.ascontiguousarray(output, dtype=np.float32)


def run_bilateral_grid_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run explicit semantic CPU bilateral-grid map/reduce blocks."""

    return _run_bilateral_grid_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_bilateral_grid_partition_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 1.0e-6,
    atol: float = 1.0e-6,
) -> dict[str, Any]:
    """Compare full-frame and tiled bilateral-grid semantic results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_bilateral_grid_partition_tiled(canonical, arrays, block_size=block_size, params=values)
    left, right = np.asarray(full, dtype=np.float64), np.asarray(tiled, dtype=np.float64)
    error = float(np.max(np.abs(left - right))) if left.size else 0.0
    adapter = lookup_block_adapter(canonical)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_bilateral_grid_staged_map_reduce",
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[0].shape, size=block_size).block_height,
            BlockGrid(arrays[0].shape, size=block_size).block_width,
        ),
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "deterministic_merge": bool(adapter.metadata.get("deterministic_merge", False)) if adapter else False,
        "native_runtime": False,
    }


# ---------------------------------------------------------------------------
# Iterative semantic oracle (bounded inpainting)
# ---------------------------------------------------------------------------
#
# The native inpaint graph is an iterative distance-level diffusion.  This
# adapter makes the level boundary explicit: every level reads an immutable
# snapshot, map blocks compute weighted fills, and a deterministic row-major
# merge publishes the level before the next level begins.  Only float32
# scalar/RGB inputs, binary masks, flags 0/1, and integer radius 1..8 are
# admitted.  Graphics/native dispatch remains unchanged and fail-closed.

_INPAINT_PARTITION_ADAPTER_OPERATIONS = ("inpaint", "inpaint_aot")


def _inpaint_parameters(
    source_input: np.ndarray,
    mask_input: np.ndarray,
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray, int, int]:
    source = np.asarray(source_input)
    mask = np.asarray(mask_input)
    if source.ndim not in (2, 3) or source.size == 0:
        raise ValueError("inpaint expects a non-empty 2D/3D source")
    if source.ndim == 3 and source.shape[2] != 3:
        raise ValueError("inpaint semantic adapter supports scalar or 3-channel source")
    if mask.ndim != 2 or mask.shape != source.shape[:2]:
        raise ValueError("inpaint mask must be a matching 2D array")
    if np.dtype(source.dtype) != np.dtype(np.float32):
        raise TypeError("inpaint semantic adapter requires float32 source")
    if not np.issubdtype(mask.dtype, np.number):
        raise TypeError("inpaint mask must be numeric")
    if not np.isfinite(source).all() or not np.isfinite(np.asarray(mask, dtype=np.float32)).all():
        raise ValueError("inpaint inputs must contain only finite values")
    radius_value = float(params.get("inpaint_radius", params.get("radius", 3)))
    if not np.isfinite(radius_value):
        raise ValueError("inpaint semantic adapter supports integer radius in [1, 8]")
    radius = int(radius_value)
    if radius_value != float(radius) or radius < 1 or radius > 8:
        raise ValueError("inpaint semantic adapter supports integer radius in [1, 8]")
    flags_value = float(params.get("flags", 0))
    if not np.isfinite(flags_value):
        raise ValueError("inpaint flags must be 0 (Telea) or 1 (NS)")
    flags = int(flags_value)
    if flags_value != float(flags) or flags not in (0, 1):
        raise ValueError("inpaint flags must be 0 (Telea) or 1 (NS)")
    return (
        np.ascontiguousarray(source, dtype=np.float32),
        np.ascontiguousarray(np.asarray(mask, dtype=np.float32) > np.float32(0.5)),
        radius,
        flags,
    )


def _inpaint_distance(mask: np.ndarray) -> np.ndarray:
    """Deterministic 8-neighbour distance levels matching dilation stages."""

    unknown = np.asarray(mask, dtype=bool)
    height, width = unknown.shape
    distance = np.full((height, width), -1, dtype=np.int32)
    distance[~unknown] = 0
    for _ in range(max(height, width) + 1):
        changed = False
        next_distance = distance.copy()
        for row in range(height):
            for col in range(width):
                if distance[row, col] >= 0:
                    continue
                best = None
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue
                        ny, nx = row + dy, col + dx
                        if 0 <= ny < height and 0 <= nx < width and distance[ny, nx] >= 0:
                            candidate = int(distance[ny, nx]) + 1
                            best = candidate if best is None else min(best, candidate)
                if best is not None:
                    next_distance[row, col] = best
                    changed = True
        distance = next_distance
        if not changed:
            break
    return distance


def _inpaint_level_compute(
    source_snapshot: np.ndarray,
    filled_snapshot: np.ndarray,
    distance: np.ndarray,
    *,
    target_level: int,
    radius: int,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    source = np.asarray(source_snapshot, dtype=np.float32)
    height, width = source.shape[:2]
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in source.shape[2:])
    output = np.array(source[y0:y1, x0:x1], dtype=np.float32, copy=True)
    radius_squared = float(radius * radius)
    for row in range(y0, y1):
        for col in range(x0, x1):
            if int(distance[row, col]) != int(target_level):
                continue
            total_weight = 0.0
            if trailing:
                accumulated = np.zeros(trailing, dtype=np.float64)
            else:
                accumulated = 0.0
            for dy in range(-radius, radius + 1):
                for dx in range(-radius, radius + 1):
                    if dy == 0 and dx == 0:
                        continue
                    squared = float(dy * dy + dx * dx)
                    if squared > radius_squared:
                        continue
                    ny, nx = row + dy, col + dx
                    if not (0 <= ny < height and 0 <= nx < width) or not bool(filled_snapshot[ny, nx]):
                        continue
                    weight = 1.0 / squared
                    total_weight += weight
                    accumulated = accumulated + np.asarray(source[ny, nx], dtype=np.float64) * weight
            if total_weight > 1.0e-12:
                output[row - y0, col - x0] = np.asarray(
                    accumulated / total_weight,
                    dtype=np.float32,
                )
    return np.ascontiguousarray(output, dtype=np.float32)


def _inpaint_reference(
    source_input: np.ndarray,
    mask_input: np.ndarray,
    *,
    inpaint_radius: Any = 3,
    flags: Any = 0,
) -> np.ndarray:
    source, mask, radius, _flags = _inpaint_parameters(
        source_input,
        mask_input,
        {"inpaint_radius": inpaint_radius, "flags": flags},
    )
    distance = _inpaint_distance(mask)
    filled = ~mask.copy()
    output = np.array(source, dtype=np.float32, copy=True)
    max_level = int(np.max(distance)) if np.any(distance >= 0) else 0
    for level in range(1, max_level + 1):
        snapshot = np.array(output, dtype=np.float32, copy=True)
        filled_snapshot = np.array(filled, dtype=bool, copy=True)
        level_result = _inpaint_level_compute(
            snapshot,
            filled_snapshot,
            distance,
            target_level=level,
            radius=radius,
        )
        output[...] = level_result
        filled[distance == level] = True
    return np.ascontiguousarray(output, dtype=np.float32)


def _inpaint_reader(first: Any, second: Any) -> Any:
    return _global_reader(first, second)


def _inpaint_runner(context: Any) -> np.ndarray:
    arrays = _as_inputs(context)
    if len(arrays) != 2:
        raise ValueError("inpaint map expects source and mask inputs")
    source, mask, radius, _flags = _inpaint_parameters(arrays[0], arrays[1], _as_params(context))
    distance = _context_value(context, "distance")
    filled = _context_value(context, "filled")
    if distance is None or filled is None:
        raise ValueError("inpaint stage context requires distance and filled snapshots")
    return _inpaint_level_compute(
        source,
        np.asarray(filled, dtype=bool),
        np.asarray(distance, dtype=np.int32),
        target_level=int(_context_value(context, "target_level", 1)),
        radius=radius,
        block=_context_value(context, "block"),
    )


def _inpaint_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(value.ndim in (2, 3) and value.size > 0 and np.isfinite(value).all())


def _inpaint_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = _context_value(context_or_block, "block", context_or_block)
    if block is None:
        raise ValueError("inpaint merge requires an output block")
    destination = np.asarray(output)
    destination[block.write_slice] = np.asarray(result, dtype=destination.dtype)
    return output


def _run_inpaint_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        canonical != "inpaint"
        or adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete inpaint adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 2:
        raise ValueError("inpaint adapter expects source and mask inputs")
    values = dict(params or {})
    source, mask, radius, _flags = _inpaint_parameters(arrays[0], arrays[1], values)
    distance = _inpaint_distance(mask)
    filled = ~mask.copy()
    output = np.array(source, dtype=np.float32, copy=True)
    max_level = int(np.max(distance)) if np.any(distance >= 0) else 0
    blocks = tuple(sorted(tuple(BlockGrid(source.shape, size=block_size)), key=lambda item: int(item.index)))
    for level in range(1, max_level + 1):
        snapshot = np.array(output, dtype=np.float32, copy=True)
        filled_snapshot = np.array(filled, dtype=bool, copy=True)
        level_output = np.empty_like(output)
        for block in blocks:
            level_output[block.write_slice] = _inpaint_level_compute(
                snapshot,
                filled_snapshot,
                distance,
                target_level=level,
                radius=radius,
                block=block,
            )
        output[...] = level_output
        filled[distance == level] = True
    return np.ascontiguousarray(output, dtype=np.float32)


def run_inpaint_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run explicit semantic CPU deterministic inpaint levels."""

    return _run_inpaint_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_inpaint_partition_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full-frame and deterministic level-partitioned inpaint."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_inpaint_partition_tiled(canonical, arrays, block_size=block_size, params=values)
    left, right = np.asarray(full, dtype=np.float64), np.asarray(tiled, dtype=np.float64)
    error = float(np.max(np.abs(left - right))) if left.size else 0.0
    adapter = lookup_block_adapter(canonical)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_inpaint_iterative_snapshot",
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[0].shape, size=block_size).block_height,
            BlockGrid(arrays[0].shape, size=block_size).block_width,
        ),
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "deterministic_merge": bool(adapter.metadata.get("deterministic_merge", False)) if adapter else False,
        "native_runtime": False,
    }


# ---------------------------------------------------------------------------
# Coordinate-domain semantic oracles
# ---------------------------------------------------------------------------
#
# A coordinate operation cannot use the ordinary same-shape ``BlockGrid``
# reader: a destination block has its own coordinate domain and may sample a
# different source region (or a different pyramid level).  The helpers below
# intentionally implement the exact coordinate conventions used by the
# maintained AOT kernels.  They are CPU semantic adapters only.  Registration
# never changes AUTO_BLOCK_SAFE and no native backend evidence is implied.


def _reflect101_index(index: int, size: int) -> int:
    """Return the OpenCV/Taichi REFLECT_101 index used by AOT kernels."""

    size = int(size)
    if size <= 1:
        return 0
    period = 2 * (size - 1)
    value = int(index) % period
    return value if value < size else period - value


def _border_index_reference(index: int, size: int, mode: int) -> Optional[int]:
    """Map a source index according to ``copy_make_border``'s five modes."""

    size = int(size)
    if size <= 0:
        raise ValueError("source dimensions must be positive")
    mode = int(mode)
    if mode == 0:  # BORDER_CONSTANT
        return None if index < 0 or index >= size else int(index)
    if mode == 1:  # BORDER_REPLICATE
        return max(0, min(size - 1, int(index)))
    if mode == 2:  # BORDER_REFLECT
        period = max(1, 2 * size)
        value = int(index) % period
        return value if value < size else period - 1 - value
    if mode == 3:  # BORDER_WRAP
        return int(index) % size
    if mode == 4:  # BORDER_REFLECT_101
        return _reflect101_index(index, size)
    raise ValueError(f"unsupported border mode: {mode}")


def _interpolation_name(value: Any) -> str:
    """Normalize public/AOT interpolation constants without importing cv2."""

    if isinstance(value, str):
        name = value.strip().lower()
        aliases = {
            "inter_linear": "linear",
            "linear": "linear",
            "inter_cubic": "cubic",
            "cubic": "cubic",
            "inter_area": "area",
            "area": "area",
        }
        if name in aliases:
            return aliases[name]
    # The maintained AOT facade uses the OpenCV-compatible values 1/2/3 for
    # linear/cubic/area.  Nearest is deliberately not admitted here because
    # the existing coordinate probe has no native offset graph for it.
    values = {1: "linear", 2: "cubic", 3: "area"}
    try:
        name = values.get(int(value))
    except (TypeError, ValueError):
        name = None
    if name is None:
        raise ValueError(
            "coordinate resize adapter supports only INTER_LINEAR, "
            "INTER_CUBIC, and INTER_AREA"
        )
    return name


def _cubic_weights_reference(t: float) -> np.ndarray:
    """Catmull-Rom (a=-0.75) weights used by ``bicubic`` AOT kernels."""

    d = abs(float(t))
    a = -0.75
    values = []
    x = d + 1.0
    values.append(a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a)
    x = d
    values.append((a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0)
    x = 1.0 - d
    values.append((a + 2.0) * x**3 - (a + 3.0) * x**2 + 1.0)
    x = 2.0 - d
    values.append(a * x**3 - 5.0 * a * x**2 + 8.0 * a * x - 4.0 * a)
    return np.asarray(values, dtype=np.float32)


def _resize_sample_reference(source: np.ndarray, y: float, x: float, mode: str) -> Any:
    """Sample one source coordinate using the maintained interpolation rules."""

    values = np.asarray(source, dtype=np.float32)
    height, width = values.shape[:2]
    if mode == "linear":
        y0 = int(np.floor(y))
        x0 = int(np.floor(x))
        fy = np.float32(y - y0)
        fx = np.float32(x - x0)
        ya, yb = max(0, min(height - 1, y0)), max(0, min(height - 1, y0 + 1))
        xa, xb = max(0, min(width - 1, x0)), max(0, min(width - 1, x0 + 1))
        top = values[ya, xa] * (np.float32(1.0) - fx) + values[ya, xb] * fx
        bottom = values[yb, xa] * (np.float32(1.0) - fx) + values[yb, xb] * fx
        return top * (np.float32(1.0) - fy) + bottom * fy
    if mode == "cubic":
        xi = int(np.floor(x))
        yi = int(np.floor(y))
        wx = _cubic_weights_reference(x - xi)
        wy = _cubic_weights_reference(y - yi)
        value = np.zeros(values.shape[2:], dtype=np.float32)
        for j in range(-1, 3):
            row_value = np.zeros(values.shape[2:], dtype=np.float32)
            yy = max(0, min(height - 1, yi + j))
            for i in range(-1, 3):
                xx = max(0, min(width - 1, xi + i))
                row_value = row_value + values[yy, xx] * wx[i + 1]
            value = value + row_value * wy[j + 1]
        return value
    raise ValueError(f"unsupported coordinate interpolation: {mode}")


def _resize_coordinate_compute(
    source: np.ndarray,
    output_shape: tuple[int, ...],
    interpolation: Any,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    """Compute a resize destination or one destination block."""

    data = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    if data.ndim not in (2, 3):
        raise ValueError("resize coordinate adapter expects a 2D or 3D image")
    height, width = int(output_shape[0]), int(output_shape[1])
    if height <= 0 or width <= 0:
        raise ValueError("resize output dimensions must be positive")
    mode = _interpolation_name(interpolation)
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1 = int(block.y0), int(block.y1)
        x0, x1 = int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in data.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    scale_y = np.float32(data.shape[0] / float(height))
    scale_x = np.float32(data.shape[1] / float(width))
    for row in range(y0, y1):
        for col in range(x0, x1):
            if mode == "area":
                x_start = float(col) * float(scale_x)
                x_end = float(col + 1) * float(scale_x)
                y_start = float(row) * float(scale_y)
                y_end = float(row + 1) * float(scale_y)
                acc = np.zeros(trailing, dtype=np.float32)
                total = np.float32(0.0)
                for iy in range(int(np.floor(y_start)), int(np.ceil(y_end))):
                    for ix in range(int(np.floor(x_start)), int(np.ceil(x_end))):
                        wx = max(0.0, min(float(ix + 1), x_end) - max(float(ix), x_start))
                        wy = max(0.0, min(float(iy + 1), y_end) - max(float(iy), y_start))
                        weight = np.float32(wx * wy)
                        yy = max(0, min(data.shape[0] - 1, iy))
                        xx = max(0, min(data.shape[1] - 1, ix))
                        acc = acc + data[yy, xx] * weight
                        total = total + weight
                output[row - y0, col - x0] = acc / np.maximum(total, np.float32(1.0e-9))
            else:
                y = (np.float32(row) + np.float32(0.5)) * scale_y - np.float32(0.5)
                x = (np.float32(col) + np.float32(0.5)) * scale_x - np.float32(0.5)
                output[row - y0, col - x0] = _resize_sample_reference(data, float(y), float(x), mode)
    return np.ascontiguousarray(output, dtype=np.float32)


def _pyramid_downsample_compute(
    source: np.ndarray,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    """One 2x Gaussian pyramid level (the same 5x5/REFLECT_101 AOT rule)."""

    data = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    if data.ndim not in (2, 3):
        raise ValueError("image_pyramid expects a 2D or 3D image")
    height, width = data.shape[0] // 2, data.shape[1] // 2
    if height < 1 or width < 1:
        raise ValueError("image_pyramid source is too small for another level")
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1 = int(block.y0), int(block.y1)
        x0, x1 = int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in data.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    weights = (1.0, 4.0, 6.0, 4.0, 1.0)
    for row in range(y0, y1):
        for col in range(x0, x1):
            acc = np.zeros(trailing, dtype=np.float32)
            for j in range(-2, 3):
                yy = _reflect101_index(row * 2 + j, data.shape[0])
                for i in range(-2, 3):
                    xx = _reflect101_index(col * 2 + i, data.shape[1])
                    acc = acc + data[yy, xx] * np.float32(weights[j + 2] * weights[i + 2])
            output[row - y0, col - x0] = acc / np.float32(256.0)
    return np.ascontiguousarray(output, dtype=np.float32)


def _image_pyramid_reference(
    source: np.ndarray, *, levels: int = 4
) -> np.ndarray:
    current = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    count = int(levels)
    if count < 0:
        raise ValueError("image_pyramid levels must be non-negative")
    for _ in range(count):
        if current.shape[0] // 2 < 1 or current.shape[1] // 2 < 1:
            break
        current = _pyramid_downsample_compute(current)
    return current


def _warp_affine_matrix(params: Mapping[str, Any]) -> np.ndarray:
    matrix = np.asarray(params.get("matrix"), dtype=np.float32)
    if matrix.shape != (2, 3) or not np.isfinite(matrix).all():
        raise ValueError("warp_affine adapter requires a finite 2x3 matrix")
    homogeneous = np.eye(3, dtype=np.float32)
    homogeneous[:2] = matrix
    try:
        inverse = np.linalg.inv(homogeneous)[:2].astype(np.float32)
    except np.linalg.LinAlgError as exc:
        raise ValueError("warp_affine matrix must be invertible") from exc
    return inverse


def _warp_affine_compute(
    source: np.ndarray,
    output_shape: tuple[int, ...],
    params: Mapping[str, Any],
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    data = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    if data.ndim not in (2, 3):
        raise ValueError("warp_affine adapter expects a 2D or 3D image")
    height, width = int(output_shape[0]), int(output_shape[1])
    inverse = _warp_affine_matrix(params)
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1 = int(block.y0), int(block.y1)
        x0, x1 = int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in data.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    for row in range(y0, y1):
        for col in range(x0, x1):
            sx = float(inverse[0, 0]) * col + float(inverse[0, 1]) * row + float(inverse[0, 2])
            sy = float(inverse[1, 0]) * col + float(inverse[1, 1]) * row + float(inverse[1, 2])
            ix, iy = int(np.floor(sx)), int(np.floor(sy))
            fx, fy = np.float32(sx - ix), np.float32(sy - iy)
            x0i, x1i = _reflect101_index(ix, data.shape[1]), _reflect101_index(ix + 1, data.shape[1])
            y0i, y1i = _reflect101_index(iy, data.shape[0]), _reflect101_index(iy + 1, data.shape[0])
            top = data[y0i, x0i] * (np.float32(1.0) - fx) + data[y0i, x1i] * fx
            bottom = data[y1i, x0i] * (np.float32(1.0) - fx) + data[y1i, x1i] * fx
            output[row - y0, col - x0] = top * (np.float32(1.0) - fy) + bottom * fy
    return np.ascontiguousarray(output, dtype=np.float32)


_BORDER_TYPE_NAMES = {
    "constant": 0,
    "replicate": 1,
    "reflect": 2,
    "wrap": 3,
    "reflect_101": 4,
    "reflect101": 4,
    "default": 4,
}


def _border_mode(value: Any) -> int:
    if isinstance(value, str):
        key = value.strip().lower()
        if key in _BORDER_TYPE_NAMES:
            return int(_BORDER_TYPE_NAMES[key])
    try:
        mode = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("copy_make_border adapter received an invalid border_type") from exc
    if mode not in range(5):
        raise ValueError("copy_make_border adapter supports border modes 0..4")
    return mode


def _copy_make_border_compute(
    source: np.ndarray,
    output_shape: tuple[int, ...],
    params: Mapping[str, Any],
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    data = np.ascontiguousarray(np.asarray(source), dtype=np.float32)
    if data.ndim not in (2, 3):
        raise ValueError("copy_make_border adapter expects a 2D or 3D image")
    top = int(params.get("top", 0)); bottom = int(params.get("bottom", 0))
    left = int(params.get("left", 0)); right = int(params.get("right", 0))
    if min(top, bottom, left, right) < 0:
        raise ValueError("border sizes must be non-negative")
    mode = _border_mode(params.get("border_type", params.get("mode", 4)))
    constants = np.asarray(params.get("value", params.get("constant", 0.0)), dtype=np.float32).reshape(-1)
    if constants.size == 0:
        raise ValueError("border value must contain at least one scalar")
    if data.ndim == 3 and constants.size not in (1, data.shape[2]):
        raise ValueError("3D border value must be scalar or one value per channel")
    height, width = int(output_shape[0]), int(output_shape[1])
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1 = int(block.y0), int(block.y1)
        x0, x1 = int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in data.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    for row in range(y0, y1):
        sy = _border_index_reference(row - top, data.shape[0], mode)
        for col in range(x0, x1):
            sx = _border_index_reference(col - left, data.shape[1], mode)
            if sy is None or sx is None:
                if data.ndim == 2:
                    output[row - y0, col - x0] = np.float32(constants[0])
                elif constants.size == 1:
                    output[row - y0, col - x0] = np.float32(constants[0])
                else:
                    output[row - y0, col - x0] = constants[: data.shape[2]]
            else:
                output[row - y0, col - x0] = data[sy, sx]
    return np.ascontiguousarray(output, dtype=np.float32)


_REFERENCE_FUNCTIONS: Mapping[str, Callable[..., Any]] = {
    "copy": _copy_reference,
    "absdiff": _absdiff_reference,
    "rgb2gray": _rgb2gray_reference,
    "split_3ch": _split_reference,
    "merge_3ch": _merge_reference,
    "extract_channel": _extract_reference,
    "insert_channel": _insert_reference,
    "cvtColor": _cvt_color_reference,
    "enhance_grayscale": _enhance_grayscale_reference,
}


# ---------------------------------------------------------------------------
# Frequency-domain semantic adapters
# ---------------------------------------------------------------------------
#
# ``aot_api.fft2`` first pads each source dimension to the next power of two,
# converts the real input to a float32 complex pair, then performs a row pass
# followed by a column pass.  ``ifft2`` reverses that order and normalizes each
# pass by its dimension before cropping ``target_shape``.  The helpers below
# preserve those public conventions in a deterministic NumPy oracle while
# allowing each independent row/column pass to be evaluated in bounded
# slices.  They intentionally do not pretend that a spatial FFT tile is
# independent: the complete row-pass/column-pass intermediate remains
# resident, and only stage-local strips are partitioned.

_FFT_MAX_BLOCK_DIMENSION = 4096


def _fft_next_power_of_two(value: int) -> int:
    value = int(value)
    if value <= 0:
        raise ValueError("FFT dimensions must be positive")
    return 1 << (value - 1).bit_length()


def _fft_real_input(value: Any) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 2:
        raise ValueError("FFT semantic adapter expects a 2D real input")
    if not np.issubdtype(array.dtype, np.number) or np.iscomplexobj(array):
        raise TypeError("FFT input must be a finite real numeric array")
    result = np.ascontiguousarray(array, dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError("FFT input must contain only finite values")
    return result


def _fft_pair_input(value: Any) -> np.ndarray:
    """Decode the public AOT ``vec2`` representation into complex64."""

    array = np.asarray(value)
    if array.ndim == 3 and array.shape[2] == 2:
        if not np.issubdtype(array.dtype, np.number):
            raise TypeError("IFFT pair input must be numeric")
        real = np.asarray(array[..., 0], dtype=np.float32)
        imag = np.asarray(array[..., 1], dtype=np.float32)
        if not np.isfinite(real).all() or not np.isfinite(imag).all():
            raise ValueError("IFFT pair input must contain only finite values")
        return np.ascontiguousarray(real + np.complex64(1j) * imag, dtype=np.complex64)
    if array.ndim == 2 and np.iscomplexobj(array):
        result = np.ascontiguousarray(array, dtype=np.complex64)
        if not np.isfinite(result.real).all() or not np.isfinite(result.imag).all():
            raise ValueError("IFFT complex input must contain only finite values")
        return result
    raise ValueError("IFFT input must be an HxWx2 pair or a 2D complex array")


def _fft_pair_output(value: np.ndarray) -> np.ndarray:
    complex_value = np.ascontiguousarray(value, dtype=np.complex64)
    return np.ascontiguousarray(
        np.stack((complex_value.real, complex_value.imag), axis=-1),
        dtype=np.float32,
    )


def _fft_block_dimensions(
    block_size: int | tuple[int, int],
    shape: tuple[int, int],
) -> tuple[int, int]:
    """Resolve bounded row/column strip sizes for staged execution."""

    if isinstance(block_size, (tuple, list)):
        if len(block_size) != 2:
            raise ValueError("FFT block_size must be an int or (rows, columns)")
        row_size, column_size = int(block_size[0]), int(block_size[1])
    else:
        row_size = column_size = int(block_size)
    if row_size <= 0 or column_size <= 0:
        raise ValueError("FFT block dimensions must be positive")
    if row_size > _FFT_MAX_BLOCK_DIMENSION or column_size > _FFT_MAX_BLOCK_DIMENSION:
        raise ValueError(
            f"FFT block dimensions must not exceed {_FFT_MAX_BLOCK_DIMENSION}"
        )
    return min(row_size, int(shape[0])), min(column_size, int(shape[1]))


def _fft_hanning_source(source: np.ndarray) -> np.ndarray:
    """Apply the public AOT Hanning convention to the unpadded source."""

    height, width = (int(source.shape[0]), int(source.shape[1]))
    if height < 2 or width < 2:
        # The native graph divides by ``h-1``/``w-1``.  Rejecting this case is
        # safer than returning a NaN-filled spectrum from a semantic adapter.
        raise ValueError("FFT Hanning requires both source dimensions >= 2")
    rows = np.arange(height, dtype=np.float32)
    columns = np.arange(width, dtype=np.float32)
    row_window = np.float32(0.5) * (
        np.float32(1.0)
        - np.cos(np.float32(2.0 * np.pi) * rows / np.float32(height - 1))
    )
    column_window = np.float32(0.5) * (
        np.float32(1.0)
        - np.cos(np.float32(2.0 * np.pi) * columns / np.float32(width - 1))
    )
    window = np.outer(row_window, column_window).astype(np.float32, copy=False)
    return np.ascontiguousarray(source * window, dtype=np.float32)


def _fft_padded_source(source: Any, *, use_hanning: bool = False) -> np.ndarray:
    real = _fft_real_input(source)
    if use_hanning:
        real = _fft_hanning_source(real)
    padded_shape = (_fft_next_power_of_two(real.shape[0]), _fft_next_power_of_two(real.shape[1]))
    padded = np.zeros(padded_shape, dtype=np.float32)
    padded[: real.shape[0], : real.shape[1]] = real
    return np.ascontiguousarray(padded, dtype=np.float32)


def _fft2_complex_staged(
    source: Any,
    *,
    use_hanning: bool = False,
    block_size: int | tuple[int, int] | None = None,
) -> np.ndarray:
    """Forward FFT with separately partitioned row and column passes."""

    padded = _fft_padded_source(source, use_hanning=use_hanning)
    height, width = (int(padded.shape[0]), int(padded.shape[1]))
    row_size, column_size = (
        (height, width)
        if block_size is None
        else _fft_block_dimensions(block_size, (height, width))
    )

    row_pass = np.empty((height, width), dtype=np.complex64)
    for y0 in range(0, height, row_size):
        y1 = min(height, y0 + row_size)
        # Each row is independent during this stage.  Cast after the NumPy
        # transform to mirror the native f32 graph's intermediate precision.
        row_pass[y0:y1] = np.asarray(
            np.fft.fft(padded[y0:y1], axis=1), dtype=np.complex64
        )

    column_pass = np.empty_like(row_pass)
    for x0 in range(0, width, column_size):
        x1 = min(width, x0 + column_size)
        # Columns are independent only after the complete row pass.  This is
        # why the adapter is MULTI_STAGE rather than a spatial local block.
        column_pass[:, x0:x1] = np.asarray(
            np.fft.fft(row_pass[:, x0:x1], axis=0), dtype=np.complex64
        )
    return np.ascontiguousarray(column_pass, dtype=np.complex64)


def _fft2_real_reference(
    source: Any,
    *,
    use_hanning: bool = False,
    block_size: int | tuple[int, int] | None = None,
) -> np.ndarray:
    return _fft_pair_output(
        _fft2_complex_staged(
            source,
            use_hanning=bool(use_hanning),
            block_size=block_size,
        )
    )


def _fft_target_shape(
    value: Any,
    source_shape: tuple[int, int],
    params: Mapping[str, Any],
) -> tuple[int, int]:
    target = params.get("target_shape", value)
    if target is None:
        return source_shape
    try:
        values = tuple(int(item) for item in target)
    except (TypeError, ValueError) as exc:
        raise ValueError("IFFT target_shape must contain two integers") from exc
    if len(values) != 2 or any(item <= 0 for item in values):
        raise ValueError("IFFT target_shape must be positive (height, width)")
    if values[0] > source_shape[0] or values[1] > source_shape[1]:
        raise ValueError("IFFT target_shape cannot exceed the spectrum dimensions")
    return values


def _ifft2_real_staged(
    spectrum: Any,
    *,
    target_shape: Any = None,
    block_size: int | tuple[int, int] | None = None,
) -> np.ndarray:
    """Inverse FFT with column/row staging and per-axis normalization."""

    complex_input = _fft_pair_input(spectrum)
    height, width = (int(complex_input.shape[0]), int(complex_input.shape[1]))
    if height & (height - 1) or width & (width - 1):
        raise ValueError("IFFT spectrum dimensions must be powers of two")
    row_size, column_size = (
        (height, width)
        if block_size is None
        else _fft_block_dimensions(block_size, (height, width))
    )

    column_pass = np.empty_like(complex_input)
    for x0 in range(0, width, column_size):
        x1 = min(width, x0 + column_size)
        column_pass[:, x0:x1] = np.asarray(
            np.fft.ifft(complex_input[:, x0:x1], axis=0), dtype=np.complex64
        )

    row_pass = np.empty_like(column_pass)
    for y0 in range(0, height, row_size):
        y1 = min(height, y0 + row_size)
        row_pass[y0:y1] = np.asarray(
            np.fft.ifft(column_pass[y0:y1], axis=1), dtype=np.complex64
        )

    out_height, out_width = _fft_target_shape(
        target_shape, (height, width), {}
    )
    return np.ascontiguousarray(
        row_pass.real[:out_height, :out_width], dtype=np.float32
    )


def _fft_reference(
    operation: str,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
    *,
    block_size: int | tuple[int, int] | None = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    arrays = tuple(inputs)
    if canonical in {"fft", "fft2"}:
        if len(arrays) != 1:
            raise ValueError(f"{canonical} expects one real input")
        return _fft2_real_reference(
            arrays[0],
            use_hanning=bool(params.get("use_hanning", False)),
            block_size=block_size,
        )
    if canonical == "ifft2":
        if len(arrays) != 1:
            raise ValueError("ifft2 expects one complex spectrum")
        return _ifft2_real_staged(
            arrays[0],
            target_shape=params.get("target_shape"),
            block_size=block_size,
        )
    raise ValueError(f"unknown FFT adapter operation: {canonical}")


def _phase_inputs(inputs: Sequence[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    if len(inputs) != 2:
        raise ValueError("phase_correlation expects reference and comparison images")
    reference = _fft_real_input(inputs[0])
    comparison = _fft_real_input(inputs[1])
    if reference.shape != comparison.shape:
        raise ValueError("phase_correlation inputs must have matching 2D shapes")
    return reference, comparison


def _phase_cross_power(
    reference_spectrum: np.ndarray,
    comparison_spectrum: np.ndarray,
) -> np.ndarray:
    if reference_spectrum.shape != comparison_spectrum.shape:
        raise ValueError("phase spectra must have matching shapes")
    # Native AOT computes G * conj(F) in a float32 vec2 graph.  Keep the
    # complex64 intermediate and explicitly zero bins whose magnitude is too
    # small, matching ``fft_phase_normalize_f32`` instead of returning NaN.
    product = np.asarray(
        comparison_spectrum * np.conj(reference_spectrum),
        dtype=np.complex64,
    )
    magnitude = np.asarray(np.abs(product), dtype=np.float32)
    normalized = np.zeros_like(product, dtype=np.complex64)
    valid = magnitude > np.float32(1.0e-12)
    np.divide(product, magnitude, out=normalized, where=valid)
    return np.ascontiguousarray(normalized, dtype=np.complex64)


def _phase_peak_reduce(
    correlation: np.ndarray,
    source_shape: tuple[int, int],
    block_size: int | tuple[int, int] | None = None,
) -> tuple[float, float, float]:
    """Reduce a correlation surface in deterministic row-major tile order."""

    surface = np.ascontiguousarray(np.asarray(correlation), dtype=np.float32)
    if surface.ndim != 2 or surface.size == 0:
        raise ValueError("phase correlation surface must be a non-empty 2D array")
    # A non-finite correlation surface would make ``argmax``/the strict
    # tie-break below depend on NumPy's NaN ordering rather than on the
    # deterministic native reduction contract.  Reject it before selecting a
    # peak instead of returning an invalid shift/value tuple.
    if not np.isfinite(surface).all():
        raise ValueError("phase correlation surface must contain only finite values")
    try:
        source_height, source_width = (int(source_shape[0]), int(source_shape[1]))
    except (TypeError, ValueError, IndexError) as exc:
        raise ValueError("phase correlation source_shape must contain two integers") from exc
    if source_height <= 0 or source_width <= 0:
        raise ValueError("phase correlation source_shape must be positive")
    if source_height > surface.shape[0] or source_width > surface.shape[1]:
        raise ValueError(
            "phase correlation source_shape cannot exceed the correlation surface"
        )
    row_size, column_size = (
        (int(surface.shape[0]), int(surface.shape[1]))
        if block_size is None
        else _fft_block_dimensions(block_size, tuple(int(v) for v in surface.shape))
    )
    best_value = -np.inf
    best_row = 0
    best_column = 0
    # Strict ``>`` preserves the first row-major maximum exactly like
    # ``np.argmax`` over the complete surface.
    for y0 in range(0, surface.shape[0], row_size):
        y1 = min(surface.shape[0], y0 + row_size)
        for x0 in range(0, surface.shape[1], column_size):
            x1 = min(surface.shape[1], x0 + column_size)
            tile = surface[y0:y1, x0:x1]
            local_index = int(np.argmax(tile))
            local_row, local_column = np.unravel_index(local_index, tile.shape)
            value = float(tile[local_row, local_column])
            row = y0 + int(local_row)
            column = x0 + int(local_column)
            if value > best_value:
                best_value = value
                best_row = row
                best_column = column
    height, width = source_height, source_width
    dy = int(best_row)
    dx = int(best_column)
    if dy > height // 2:
        dy -= height
    if dx > width // 2:
        dx -= width
    return float(dx), float(dy), float(best_value)


def _phase_correlation_reference(
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
    *,
    block_size: int | tuple[int, int] | None = None,
) -> tuple[float, float, float]:
    reference, comparison = _phase_inputs(inputs)
    use_hanning = bool(params.get("use_hanning", True))
    # ``max_shift`` belongs to the historical outer alignment wrapper, while
    # the maintained AOT graph does not apply it.  Accept a non-negative value
    # for compatibility but intentionally do not alter the native search
    # surface or peak semantics.
    if params.get("max_shift") is not None and int(params["max_shift"]) < 0:
        raise ValueError("phase_correlation max_shift must be non-negative")
    reference_spectrum = _fft2_complex_staged(
        reference,
        use_hanning=use_hanning,
        block_size=block_size,
    )
    comparison_spectrum = _fft2_complex_staged(
        comparison,
        use_hanning=use_hanning,
        block_size=block_size,
    )
    cross_power = _phase_cross_power(reference_spectrum, comparison_spectrum)
    correlation = _ifft2_real_staged(
        _fft_pair_output(cross_power),
        target_shape=reference.shape,
        block_size=block_size,
    )
    return _phase_peak_reduce(correlation, reference.shape, block_size=block_size)


_AKAZE_MAX_BLOCK_DIMENSION = 4096


def _akaze_source(value: Any) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 2 or not np.issubdtype(array.dtype, np.number):
        raise TypeError("AKAZE keypoint adapter expects one 2D numeric image")
    if np.iscomplexobj(array):
        raise TypeError("AKAZE keypoint adapter does not accept complex images")
    source = np.ascontiguousarray(array, dtype=np.float32)
    if source.size == 0 or not np.isfinite(source).all():
        raise ValueError("AKAZE image must be non-empty and finite")
    return source


def _akaze_parameters(
    source: np.ndarray,
    params: Mapping[str, Any],
) -> tuple[int, float, int, int, int]:
    grid_size = int(params.get("grid_size", 32))
    threshold = float(params.get("threshold", 0.008))
    margin = int(params.get("margin", 15))
    max_keypoints = int(params.get("max_keypoints", 1500))
    if grid_size < 1 or grid_size > _AKAZE_MAX_BLOCK_DIMENSION:
        raise ValueError("AKAZE grid_size must be in [1, 4096]")
    if not np.isfinite(threshold) or threshold < 0.0:
        raise ValueError("AKAZE threshold must be finite and non-negative")
    if margin < 0:
        raise ValueError("AKAZE margin must be non-negative")
    if max_keypoints <= 0:
        raise ValueError("AKAZE max_keypoints must be positive")
    # The maintained ``detect_keypoints`` graph does not receive ``margin``;
    # retain it only as validated compatibility metadata.  Its fixed interior
    # range starts at three pixels, exactly as the native graph does.
    return grid_size, threshold, margin, max_keypoints, int(source.size)


def _akaze_hessian_map(source: np.ndarray) -> np.ndarray:
    """Compute the clamped 3x3 Hessian determinant used by the AOT graph."""

    padded = np.pad(np.asarray(source, dtype=np.float32), 1, mode="edge")
    center = padded[1:-1, 1:-1]
    left = padded[1:-1, :-2]
    right = padded[1:-1, 2:]
    up = padded[:-2, 1:-1]
    down = padded[2:, 1:-1]
    upper_left = padded[:-2, :-2]
    upper_right = padded[:-2, 2:]
    lower_left = padded[2:, :-2]
    lower_right = padded[2:, 2:]
    lxx = right - np.float32(2.0) * center + left
    lyy = down - np.float32(2.0) * center + up
    lxy = (lower_right - lower_left - upper_right + upper_left) * np.float32(0.25)
    determinant = lxx * lyy - lxy * lxy
    return np.ascontiguousarray(np.maximum(determinant, np.float32(0.0)), dtype=np.float32)


def _akaze_hessian_tiled(
    source: np.ndarray,
    block_size: int | tuple[int, int],
) -> np.ndarray:
    row_size, column_size = _akaze_block_dimensions(block_size)
    hessian = np.empty_like(source, dtype=np.float32)
    grid = BlockGrid(source.shape, size=(row_size, column_size), halo=1)
    for block in grid:
        source_tile = np.ascontiguousarray(source[block.read_slice], dtype=np.float32)
        tile_hessian = _akaze_hessian_map(source_tile)
        hessian[block.write_slice] = tile_hessian[block.core_slice]
    return np.ascontiguousarray(hessian, dtype=np.float32)


def _akaze_block_dimensions(
    block_size: int | tuple[int, int],
) -> tuple[int, int]:
    """Validate and normalize a keypoint-stage tile size without allocation."""

    if isinstance(block_size, (tuple, list)):
        if len(block_size) != 2:
            raise ValueError("AKAZE block_size must be an int or (rows, columns)")
        row_size, column_size = int(block_size[0]), int(block_size[1])
    else:
        row_size = column_size = int(block_size)
    if row_size <= 0 or column_size <= 0:
        raise ValueError("AKAZE block dimensions must be positive")
    if row_size > _AKAZE_MAX_BLOCK_DIMENSION or column_size > _AKAZE_MAX_BLOCK_DIMENSION:
        raise ValueError("AKAZE block dimensions must not exceed 4096")
    return row_size, column_size


def _akaze_nms_keypoints(
    hessian: np.ndarray,
    *,
    grid_size: int,
    threshold: float,
    max_keypoints: int,
) -> np.ndarray:
    """Replicate the AOT grid NMS and sub-pixel paraboloid fit."""

    height, width = (int(hessian.shape[0]), int(hessian.shape[1]))
    grid_height = height // int(grid_size)
    grid_width = width // int(grid_size)
    keypoints: list[tuple[float, float]] = []
    for grid_y in range(grid_height):
        for grid_x in range(grid_width):
            start_y = grid_y * int(grid_size)
            start_x = grid_x * int(grid_size)
            end_y = min(start_y + int(grid_size), height - 3)
            end_x = min(start_x + int(grid_size), width - 3)
            y0 = max(3, start_y)
            x0 = max(3, start_x)
            if y0 >= end_y or x0 >= end_x:
                continue
            candidate = hessian[y0:end_y, x0:end_x]
            local_index = int(np.argmax(candidate))
            local_y, local_x = np.unravel_index(local_index, candidate.shape)
            best_y = y0 + int(local_y)
            best_x = x0 + int(local_x)
            best_score = float(hessian[best_y, best_x])
            if not best_score > float(threshold):
                continue
            delta_y = np.float32(0.0)
            delta_x = np.float32(0.0)
            center = np.float32(hessian[best_y, best_x])
            denominator_x = np.float32(2.0) * center - np.float32(
                hessian[best_y, best_x - 1]
            ) - np.float32(hessian[best_y, best_x + 1])
            if denominator_x > np.float32(1.0e-5):
                delta_x = np.float32(0.5) * (
                    np.float32(hessian[best_y, best_x + 1])
                    - np.float32(hessian[best_y, best_x - 1])
                ) / denominator_x
            denominator_y = np.float32(2.0) * center - np.float32(
                hessian[best_y - 1, best_x]
            ) - np.float32(hessian[best_y + 1, best_x])
            if denominator_y > np.float32(1.0e-5):
                delta_y = np.float32(0.5) * (
                    np.float32(hessian[best_y + 1, best_x])
                    - np.float32(hessian[best_y - 1, best_x])
                ) / denominator_y
            delta_x = np.clip(delta_x, np.float32(-0.5), np.float32(0.5))
            delta_y = np.clip(delta_y, np.float32(-0.5), np.float32(0.5))
            # Native detector stores (row, column), not public packed x/y.
            keypoints.append(
                (
                    np.float32(best_y) + np.float32(delta_y),
                    np.float32(best_x) + np.float32(delta_x),
                )
            )
            if len(keypoints) >= int(max_keypoints):
                return np.ascontiguousarray(keypoints, dtype=np.float32)
    return np.ascontiguousarray(keypoints, dtype=np.float32).reshape(-1, 2)


def _akaze_keypoints_reference(
    source: Any,
    params: Mapping[str, Any],
    *,
    block_size: int | tuple[int, int] | None = None,
) -> np.ndarray:
    image = _akaze_source(source)
    grid_size, threshold, _margin, max_keypoints, _ = _akaze_parameters(image, params)
    hessian = (
        _akaze_hessian_map(image)
        if block_size is None
        else _akaze_hessian_tiled(image, block_size)
    )
    return _akaze_nms_keypoints(
        hessian,
        grid_size=grid_size,
        threshold=threshold,
        max_keypoints=max_keypoints,
    )


def _akaze_reader(first: Any, second: Any) -> PartitionContext:
    """Build a context for the bounded AKAZE keypoint stage.

    The public ``akaze`` facade accepts a reference/comparison pair and runs
    diffusion, descriptors, and matching.  This adapter deliberately covers
    only the single-image Hessian/NMS stage, so a two-image context is rejected
    by the explicit executor below instead of silently dropping an input.
    """

    if isinstance(first, BlockSpec):
        block = first
        values = tuple(np.asarray(value) for value in second)
        full_shape = tuple(values[0].shape) if values else None
        return PartitionContext(
            operation="akaze",
            inputs=values,
            block=block,
            full_shape=full_shape,
            params={},
            stage=0,
        )
    context, block = first, second
    values = _as_inputs(context)
    full_shape = _context_value(context, "full_shape")
    if full_shape is None and values:
        full_shape = tuple(values[0].shape)
    return PartitionContext(
        operation="akaze",
        inputs=values,
        block=block,
        full_shape=None if full_shape is None else tuple(full_shape),
        params=_as_params(context),
        stage=int(_context_value(context, "stage", 0)),
    )


def _akaze_runner(context: Any) -> np.ndarray:
    """Run one semantic keypoint stage from a prepared context.

    ``_run_akaze_keypoints_partition_tiled`` owns the guard-band tile loop;
    this callback remains a full-context oracle for the generic adapter
    protocol and intentionally ignores ``context.block``.
    """

    values = _as_inputs(context)
    if len(values) != 1:
        raise ValueError(
            "AKAZE semantic partition supports one image for the keypoint stage"
        )
    return _akaze_keypoints_reference(values[0], _as_params(context))


def _akaze_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(
        value.ndim == 2
        and value.shape[1] == 2
        and value.dtype == np.dtype(np.float32)
        and np.isfinite(value).all()
    )


def _akaze_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    """Publish an already globally ordered keypoint result.

    Keypoint output is variable-cardinality and cannot be stitched by the
    ordinary fixed-shape core merger.  The explicit custom executor computes
    Hessian tiles, performs one row-major NMS pass, and returns the complete
    output; this callback is retained as a safe shape-checked fallback.
    """

    destination = np.asarray(output)
    value = np.asarray(result, dtype=np.float32)
    if destination.shape != value.shape:
        raise ValueError("AKAZE keypoint output shape mismatch")
    destination[...] = value
    return output


def _run_akaze_keypoints_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Execute the bounded AKAZE Hessian/NMS stage over guard-band tiles.

    This is an explicit semantic CPU adapter.  It preserves the exact native
    single-scale Hessian and deterministic grid NMS semantics while leaving
    descriptor extraction, FED diffusion, and matching on the established
    full-frame path.
    """

    canonical = canonical_operation_name(operation)
    if canonical not in _AKAZE_ADAPTER_OPERATIONS:
        raise ValueError(f"unknown AKAZE adapter operation: {canonical}")
    adapter = lookup_block_adapter(canonical)
    if (
        adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete AKAZE adapter registered for {canonical}")
    values = tuple(np.asarray(value) for value in inputs)
    if len(values) != 1:
        raise ValueError(
            "AKAZE semantic partition supports one image for the keypoint stage; "
            "descriptor/matching inputs remain full-frame"
        )
    image = _akaze_source(values[0])
    _akaze_parameters(image, dict(params or {}))
    # Validate dimensions before allocating the Hessian/output arrays.
    _akaze_block_dimensions(block_size)
    return _akaze_keypoints_reference(
        image,
        dict(params or {}),
        block_size=block_size,
    )


def run_akaze_keypoints_partition_tiled(
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Explicit semantic CPU AKAZE keypoint guard-band execution."""

    return _run_akaze_keypoints_partition_tiled(
        "akaze",
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_akaze_keypoint_parity(
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full-frame and guard-band-tiled AKAZE keypoint outputs."""

    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    if len(arrays) != 1:
        raise ValueError(
            "AKAZE semantic partition supports one image for the keypoint stage"
        )
    image = _akaze_source(arrays[0])
    grid_size, threshold, margin, max_keypoints, _ = _akaze_parameters(image, values)
    full = _akaze_keypoints_reference(image, values)
    tiled = _run_akaze_keypoints_partition_tiled(
        "akaze",
        (image,),
        block_size=block_size,
        params=values,
    )
    left = np.asarray(full, dtype=np.float64)
    right = np.asarray(tiled, dtype=np.float64)
    if left.shape != right.shape:
        passed = False
        error = float("inf")
    else:
        error = float(np.max(np.abs(left - right))) if left.size else 0.0
        passed = bool(
            np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)
        )
    return {
        "operation": "akaze",
        "scope": "semantic_numpy_akaze_keypoint_guard_nms",
        "backend": "cpu",
        "input_shape": list(image.shape),
        "output_shape": list(full.shape),
        "block_size": _akaze_block_dimensions(block_size),
        "grid_size": grid_size,
        "threshold": threshold,
        "margin": margin,
        "max_keypoints": max_keypoints,
        "guard_halo": 1,
        "output_domain": True,
        "output_domain_kind": "grid_nms_keypoints",
        "coordinate_order": "row_col",
        "deterministic_merge": True,
        "merge_order": "row-major grid cell; first max wins",
        "passed": passed,
        "max_abs_error": error,
        "native_runtime": False,
    }


def register_akaze_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register the bounded CPU semantic AKAZE keypoint contract.

    The registration is deliberately multi-stage and fail-closed.  It does
    not change the public two-image ``akaze`` API, automatic block flags, or
    native backend evidence.
    """

    operation = "akaze"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.VARIABLE,
        input_coordinate_map="keypoint_output_domain",
        halo=1,
        halo_policy=HaloPolicy.FIXED,
        border_policy=BorderPolicy.CLAMP,
        reduction=ReductionPolicy.GLOBAL,
        merge=MergePolicy.CUSTOM,
        variable_cardinality=True,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason=(
            "deterministic CPU semantic AKAZE single-scale Hessian/keypoint "
            "guard-band parity; descriptor/matching and native proof pending"
        ),
        partition_strategy=PartitionStrategy.MULTI_STAGE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "multi_stage",
        "pipeline_kind": "hessian_grid_nms",
        "semantic_only": True,
        "keypoint_stage": True,
        "descriptor_stage": False,
        "matching_stage": False,
        "guard_halo": 1,
        "output_domain": True,
        "output_domain_kind": "grid_nms_keypoints",
        "coordinate_order": "row_col",
        "deterministic_merge": True,
        "merge_order": "row-major grid cell; first max wins",
        "native_probe_required": True,
        "native_runtime": False,
        "custom_executor": _run_akaze_keypoints_partition_tiled,
        "full_frame_callback": lambda inputs, params: _akaze_keypoints_reference(
            inputs[0], params
        ),
        "parity_runner": verify_akaze_keypoint_parity,
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_akaze_keypoint_guard_nms",
                "native_runtime": False,
            }
        },
        "stage_contract": {
            "stages": ["guard_band_hessian", "grid_nms", "subpixel_fit"],
            "guard_halo": 1,
            "border": "clamp",
            "output": "variable Nx2 row/column keypoints",
            "unsupported": "FED diffusion, multiscale descriptors, matching",
        },
    }
    return {
        operation: register_block_adapter(
            operation,
            reader=_akaze_reader,
            runner=_akaze_runner,
            validator=_akaze_validator,
            merger=_akaze_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.MULTI_STAGE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    }


def _optical_flow_identity_inputs(
    inputs: Sequence[np.ndarray],
) -> tuple[np.ndarray, np.ndarray]:
    """Validate the restricted identity-frame flow input contract."""

    values = tuple(np.asarray(value) for value in inputs)
    if len(values) != 2:
        raise ValueError(
            "identity optical-flow partition expects reference and comparison frames"
        )
    reference, comparison = values
    if reference.ndim != 2 or comparison.ndim != 2:
        raise ValueError("identity optical-flow frames must be finite 2D arrays")
    if reference.shape != comparison.shape:
        raise ValueError("identity optical-flow frames must have matching shapes")
    if not np.issubdtype(reference.dtype, np.number) or not np.issubdtype(
        comparison.dtype, np.number
    ):
        raise TypeError("identity optical-flow frames must be numeric")
    if np.iscomplexobj(reference) or np.iscomplexobj(comparison):
        raise TypeError("identity optical-flow frames do not accept complex data")
    if not np.isfinite(reference).all() or not np.isfinite(comparison).all():
        raise ValueError("identity optical-flow frames must be finite")
    # ``array_equal`` is deliberate: approximate equality would make a tiny
    # real motion eligible for the zero-flow specialization and would hide a
    # correctness regression in the caller's optical-flow path.
    if reference.dtype != comparison.dtype or not np.array_equal(
        reference, comparison
    ):
        raise ValueError(
            "identity optical-flow adapter requires bitwise-identical frames"
        )
    return (
        np.ascontiguousarray(reference),
        np.ascontiguousarray(comparison),
    )


def _optical_flow_identity_parameters(
    operation: str,
    params: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    """Validate the small parameter subset covered by the identity proof."""

    canonical = canonical_operation_name(operation)
    if canonical not in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
        raise ValueError(f"unknown identity optical-flow operation: {operation}")
    values = dict(params or {})

    def _same_float(name: str, expected: float) -> bool:
        try:
            return bool(np.isclose(float(values.get(name, expected)), expected))
        except (TypeError, ValueError):
            return False

    def _same_int(name: str, expected: int) -> bool:
        try:
            return int(values.get(name, expected)) == int(expected)
        except (TypeError, ValueError):
            return False

    def _is_none(name: str) -> bool:
        return values.get(name) is None

    if canonical == "farneback_flow":
        checks = (
            _same_float("pyr_scale", 0.5),
            _same_int("num_levels", 1),
            _same_int("num_iters", 1),
            _same_int("poly_n", 5),
            _same_int("flags", 0),
            _is_none("flow_init"),
            not bool(values.get("return_gpu", False)),
            not bool(values.get("return_diagnostics", False)),
        )
        if not all(checks):
            raise ValueError(
                "farneback identity specialization requires the restricted "
                "single-level/no-init/no-diagnostics parameter subset"
            )
    else:
        checks = (
            _same_int("maxLevel", 0),
            _is_none("prevPts"),
            _is_none("nextPts"),
            not bool(values.get("adaptive", False)),
            str(values.get("motion_mode", "fast") or "fast").lower() == "fast",
            str(values.get("dense_mode", "smooth") or "smooth").lower()
            == "smooth",
            not bool(values.get("return_gpu", False)),
            not bool(values.get("return_diagnostics", False)),
        )
        if not all(checks):
            raise ValueError(
                f"{canonical} identity specialization requires the restricted "
                "single-level/no-init/no-diagnostics parameter subset"
            )
    return values


def _optical_flow_identity_scope(
    operation: str,
    reference: np.ndarray,
) -> None:
    """Apply operation-specific guards for the proven identity subset."""

    if canonical_operation_name(operation) == "block_matching":
        # The maintained block-matching graph performs a parabolic fit in
        # float32.  A non-constant identity image can therefore retain tiny
        # round-off residuals (even though the physical motion is zero).  A
        # constant image is the bounded case where the full-frame graph and
        # this tiled zero oracle are exactly bit-identical.
        if reference.size and not bool(np.all(reference == reference.reshape(-1)[0])):
            raise ValueError(
                "block_matching identity specialization requires a constant frame"
            )


def _optical_flow_identity_reference(
    inputs: Sequence[np.ndarray],
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Return the exact zero-flow reference for identical source frames."""

    operation = str(dict(params or {}).get("operation", "farneback_flow"))
    reference, _comparison = _optical_flow_identity_inputs(inputs)
    # Parameter validation happens before allocation so an accidental motion
    # frame never gets silently converted to a zero result.
    _optical_flow_identity_parameters(operation, params)
    _optical_flow_identity_scope(operation, reference)
    return np.zeros((*reference.shape, 2), dtype=np.float32)


def _optical_flow_identity_reader(first: Any, second: Any) -> PartitionContext:
    if isinstance(first, BlockSpec):
        block = first
        values = tuple(np.asarray(value) for value in second)
        full_shape = tuple(values[0].shape) if values else None
        operation = str(getattr(block, "operation", "") or "")
        return PartitionContext(
            operation=operation or "farneback_flow",
            inputs=values,
            block=block,
            full_shape=full_shape,
            params={},
            stage=0,
        )
    context, block = first, second
    values = _as_inputs(context)
    full_shape = _context_value(context, "full_shape")
    if full_shape is None and values:
        full_shape = tuple(values[0].shape)
    return PartitionContext(
        operation=canonical_operation_name(str(_context_value(context, "operation", ""))),
        inputs=values,
        block=block,
        full_shape=None if full_shape is None else tuple(full_shape),
        params=_as_params(context),
        stage=int(_context_value(context, "stage", 0)),
    )


def _optical_flow_identity_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(
        str(_context_value(context, "operation", "farneback_flow"))
    )
    reference, _comparison = _optical_flow_identity_inputs(_as_inputs(context))
    values = dict(_as_params(context))
    _optical_flow_identity_parameters(operation, values)
    _optical_flow_identity_scope(operation, reference)
    return np.zeros((*reference.shape, 2), dtype=np.float32)


def _optical_flow_identity_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(
        value.ndim == 3
        and value.shape[-1] == 2
        and value.dtype == np.dtype(np.float32)
        and np.isfinite(value).all()
    )


def _optical_flow_identity_merger(
    output: Any, result: Any, context_or_block: Any
) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=np.float32)
    block = _context_value(context_or_block, "block")
    if block is None and isinstance(context_or_block, BlockSpec):
        block = context_or_block
    if block is None:
        if destination.shape != value.shape:
            raise ValueError("identity optical-flow output shape mismatch")
        destination[...] = value
        return output
    expected = (int(block.shape[0]), int(block.shape[1]), 2)
    if tuple(value.shape) != expected:
        raise ValueError("identity optical-flow tile shape mismatch")
    destination[block.write_slice] = value
    return output


def _optical_flow_identity_block_dimensions(
    block_size: int | tuple[int, int],
) -> tuple[int, int]:
    if isinstance(block_size, (tuple, list)):
        if len(block_size) != 2:
            raise ValueError("optical-flow block_size must be an int or (rows, columns)")
        rows, columns = int(block_size[0]), int(block_size[1])
    else:
        rows = columns = int(block_size)
    if rows <= 0 or columns <= 0 or rows > 4096 or columns > 4096:
        raise ValueError("optical-flow block dimensions must be in [1, 4096]")
    return rows, columns


def _run_optical_flow_identity_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run the explicit CPU identity specialization over a 2D block grid."""

    canonical = canonical_operation_name(operation)
    if canonical not in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
        raise ValueError(f"unknown identity optical-flow operation: {operation}")
    reference, _comparison = _optical_flow_identity_inputs(inputs)
    values = dict(params or {})
    values.setdefault("operation", canonical)
    _optical_flow_identity_parameters(canonical, values)
    _optical_flow_identity_scope(canonical, reference)
    dimensions = _optical_flow_identity_block_dimensions(block_size)
    output = np.empty((*reference.shape, 2), dtype=np.float32)
    grid = BlockGrid(reference.shape, size=dimensions, halo=0)
    for block in grid:
        # A fixed zero tile avoids carrying a full-frame temporary and makes
        # the memory contract explicit for large identical RAW previews.
        output[block.write_slice] = np.zeros(
            (int(block.shape[0]), int(block.shape[1]), 2), dtype=np.float32
        )
    return output


def run_optical_flow_identity_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Explicit semantic CPU-only identity-frame flow execution."""

    return _run_optical_flow_identity_partition_tiled(
        operation, inputs, block_size=block_size, params=params
    )


def verify_optical_flow_identity_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Verify exact full/tiled parity for the restricted identity subset."""

    canonical = canonical_operation_name(operation)
    reference, _comparison = _optical_flow_identity_inputs(inputs)
    values = dict(params or {})
    values.setdefault("operation", canonical)
    _optical_flow_identity_parameters(canonical, values)
    _optical_flow_identity_scope(canonical, reference)
    full = np.zeros((*reference.shape, 2), dtype=np.float32)
    tiled = _run_optical_flow_identity_partition_tiled(
        canonical, (reference, reference), block_size=block_size, params=values
    )
    error = float(np.max(np.abs(full - tiled))) if full.size else 0.0
    return {
        "operation": canonical,
        "scope": "semantic_numpy_optical_flow_identity",
        "backend": "cpu",
        "input_shape": list(reference.shape),
        "block_size": _optical_flow_identity_block_dimensions(block_size),
        "identity_input": True,
        "restricted_parameters": True,
        "passed": bool(np.array_equal(full, tiled)),
        "max_abs_error": error,
        "native_runtime": False,
    }


def register_optical_flow_identity_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register restricted CPU identity-frame flow adapters.

    This registration is semantic-only and deliberately leaves the strict
    automatic flags, native evidence, and GPU runtime dispatch untouched.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.SAME,
            input_coordinate_map="identity",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=int(base.scratch_bytes),
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason=(
                "restricted semantic CPU zero-flow identity parity; "
                "non-identical motion, native, and automatic paths remain guarded"
            ),
            partition_strategy=PartitionStrategy.LOCAL,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "local_identity_specialization",
            "semantic_only": True,
            "identity_input_only": True,
            "restricted_parameters": list(_OPTICAL_FLOW_IDENTITY_RESTRICTIONS[operation]),
            "native_probe_required": True,
            "native_runtime": False,
            "custom_executor": _run_optical_flow_identity_partition_tiled,
            "full_frame_callback": (
                lambda inputs, params, _op=operation: _optical_flow_identity_reference(
                    inputs, {**dict(params or {}), "operation": _op}
                )
            ),
            "parity_runner": (
                lambda inputs, **kwargs: verify_optical_flow_identity_parity(
                    operation, inputs, **kwargs
                )
            ),
            "default_mode": "full_frame",
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_optical_flow_identity_reader,
            runner=_optical_flow_identity_runner,
            validator=_optical_flow_identity_validator,
            merger=_optical_flow_identity_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.LOCAL,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return registered

# Public image-processing wrappers which already own a maintained
# same-backend ``_run_blockwise`` executor.  The semantic adapters below use a
# bounded parameter subset; dynamic radii/kernels remain fail-closed.
_LOCAL_STENCIL_ADAPTER_OPERATIONS = (
    "morphology",
    "filter2d",
    "threshold",
    "normalize",
    "joint_bilateral_guidance",
    "enhance_image",
    "joint_bilateral_filter",
    "guided_filter",
    "non_local_means",
)


def local_stencil_contract_report(
    operation: str,
    *,
    backend: str | None = None,
    device: str | None = None,
) -> dict[str, Any]:
    """Read-only contract audit for one bounded local/stencil operation.

    This reports the existing semantic CPU adapter and exact native evidence;
    it never registers adapters, changes operation flags, or promotes a
    graphics backend merely because the CPU partition is deterministic.
    """
    canonical = canonical_operation_name(operation)
    if canonical not in _LOCAL_STENCIL_ADAPTER_OPERATIONS:
        raise ValueError(f"unsupported local/stencil operation: {operation!r}")
    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    adapter = lookup_block_adapter(canonical)
    native_records: list[dict[str, Any]] = []
    if backend_name and device_name:
        try:
            from .native_evidence import lookup_native_partition_evidence
            native_records = [item.as_dict() for item in lookup_native_partition_evidence(canonical, backend_name, device_name)]
        except Exception:
            native_records = []
    native_qualified = any(bool(item.get("qualified")) and bool(item.get("native_runtime")) for item in native_records)
    return {
        "scope": "local_stencil_contract_audit",
        "operation": canonical,
        "backend": backend_name,
        "device": device_name,
        "contract": operation_contract(canonical).as_dict(),
        "adapter_registered": adapter is not None,
        "semantic_cpu_partition": bool(adapter is not None and can_partition_block(canonical, "cpu")),
        "automatic_safe": bool(can_auto_block(canonical, backend_name)),
        "partition_safe": bool(can_partition_block(canonical, backend_name)),
        "automatic_dispatch_safe": bool(can_auto_partition_dispatch(canonical, backend_name)),
        "native_evidence_records": native_records,
        "native_partition_evidence": native_qualified,
        "status": "native_candidate" if native_qualified else ("semantic_cpu" if adapter is not None else "gap_fail_closed"),
        "runtime_dispatch_changed": False,
        "registry_mutated": False,
    }

# Legacy AOT image/flow operations with maintained host tile executors.  They
# are kept in a separate tranche from the extended image wrappers above so a
# future planner can audit their larger halos and parameter limits without
# changing the historical local-stencil list.  ``copy_field`` is a semantic
# alias for the pointwise copy operation; it has no independent legacy host
# executor and is therefore never treated as native evidence.
_LEGACY_LOCAL_ADAPTER_OPERATIONS = (
    "copy_field",
    "gaussian_blur",
    "box_filter",
    "median_filter",
    "sobel",
    "laplacian",
    "smooth_flow",
    "highlight_recovery",
    "cvtColor_extended",
)

# These wrappers do not currently own a maintained legacy tile executor.  The
# adapters below are semantic CPU oracles only, registered explicitly and
# never considered by ``can_auto_partition_dispatch``.
_COORDINATE_ADAPTER_OPERATIONS = (
    "tone_map_srgb",
    "naturalTonemapping",
    "to_gamma_proxy",
    "rotate_by_flip",
)

# Shape-changing coordinate-domain operations have their own callback/harness
# because the output grid is not the source grid.  Keep this separate from the
# older same-shape coordinate adapters so callers relying on the historical
# constant retain its exact contents.
_COORDINATE_DOMAIN_ADAPTER_OPERATIONS = (
    "resize",
    "image_pyramid",
    "warp_affine_aot",
    "copy_make_border_aot",
)

# Coordinate-domain warps have maintained offset loops in ``aot_api`` but
# their inputs do not share one spatial shape (a remap source may be larger
# than its map, and a flow field is commonly low resolution).  Keep them in a
# separate semantic tranche instead of teaching the ordinary same-shape
# adapter about these layouts.  Registration below is CPU-only and never
# promotes the historical automatic/native gates.
_COORDINATE_WARP_ADAPTER_OPERATIONS = (
    "remap",
    "remap_with_flow",
    "warp_perspective",
)
_OUTPUT_DOMAIN_ADAPTER_OPERATIONS = (
    "generate_hanning_window_2d",
    "gaussian_window_aot",
)

# Explicit output/coordinate contracts for public AOT helpers which do not
# own a safe legacy tile executor.  These are intentionally separate from the
# historical operation lists above: registering them must not change the
# automatic dispatch gate or imply native graphics parity.
_FLOW_MAP_ADAPTER_OPERATIONS = ("build_flow_maps",)
_NORMALIZATION_ADAPTER_OPERATIONS = ("normalize_image",)
_BRIEF_PATTERN_ADAPTER_OPERATIONS = ("generate_brief_pattern",)

# Fused 2x2 auxiliary demosaic graphs.  Hamilton/ARM wrappers already own
# ``_demosaic_half_blockwise`` and are proven below on odd/non-multiple CPU
# frames.  DCB/MLRI half-res wrappers currently dispatch only a full-frame
# graph.  The semantic adapter below deliberately uses the same bounded
# phase-safe CPU oracle as the other fused paths; this is *not* evidence that
# the algorithm-specific native graph is tile-safe.
_DEMOSAIC_HALF_ADAPTER_OPERATIONS = (
    "hamilton_demosaic_half_res",
    "hamilton_demosaic_rgb_half_res",
    "arm_demosaic_half_res",
    "arm_demosaic_rgb_half_res",
    "dcb_demosaic_half_res",
    "dcb_demosaic_rgb_half_res",
    "mlri_admm_demosaic_half_res",
    "mlri_admm_demosaic_rgb_half_res",
)
_DEMOSAIC_HALF_GAP_OPERATIONS: tuple[str, ...] = ()

# Full-resolution Bayer families.  The semantic adapter computes one
# phase-aware reference frame and merges output-domain tiles from that frame;
# this is intentionally conservative (the complete RAW source remains
# visible) but proves odd/non-multiple output partitioning without changing
# the public full-frame path.  MLRI remains iterative/global and is tracked by
# its existing fail-closed contract.
_DEMOSAIC_FULL_ADAPTER_OPERATIONS = (
    "hamilton_demosaic",
    "hamilton_demosaic_1channel",
    "hamilton_demosaic_3channel",
    "arm_demosaic",
    "arm_demosaic_1channel",
    "pure_arm_demosaic",
    "dcb_demosaic",
    "dcb_demosaic_1channel",
    "dcb_demosaic_3channel",
    "mlri_admm_demosaic",
    "mlri_admm_demosaic_1channel",
    "mlri_admm_demosaic_3channel",
)

# BM3D is a non-local, variable-cardinality algorithm in its normal mode.
# The only bounded semantic contract we can prove without a global group
# planner is the mathematically exact zero-noise identity (sigma == 0) on
# finite float32 images.  It is useful for pipeline validation and keeps the
# real BM3D path fail-closed for every denoising configuration.
_BM3D_ADAPTER_OPERATIONS = ("bm3d",)

# BM3D's normal sigma>0 path is non-local and variable-cardinality.  Keep a
# dedicated read-only report for the only bounded semantic baseline (sigma=0)
# so callers can distinguish that identity oracle from production denoising.
BM3D_PARTITION_GAP_REASONS = (
    "production BM3D performs non-local grouping and 3-D transforms",
    "sigma>0 requires cross-tile patch search and deterministic merge semantics",
    "same-backend native full-frame versus tiled parity is unavailable",
)

# These operations are recorded as global in the legacy capability table
# because callers normally invoke them after all tile contributions have been
# accumulated.  Their kernels are nevertheless pointwise once the accumulators
# exist, so a caller-owned semantic adapter can partition them without changing
# the legacy path.  They intentionally remain outside ``AUTO_BLOCK_SAFE`` and
# have no native backend claim here.
_ACCUMULATOR_ADAPTER_OPERATIONS = (
    "mean_division",
    "normalize_accumulator",
)

# NCC/ZNCC are sliding-window operations rather than ordinary image-local
# maps.  A tile of the *output search surface* reads a template-sized window
# from the source frame and therefore needs a dedicated coordinate/map-reduce
# adapter.  These names intentionally remain outside the strict automatic
# table: this registration is a semantic CPU proof only and does not imply
# native GPU evidence or alter the legacy full-frame API.
_NCC_ADAPTER_OPERATIONS = (
    "zncc",
    "ncc_alignment",
)

# Tile stitching is a reduction over an ordered sequence of overlapping tile
# contributions.  The semantic adapter accepts a stack of tiles plus their
# origins and applies the same weighted accumulator rules in a canonical
# row-major order.  It is intentionally explicit/CPU-only; the legacy GPU
# kernels remain the runtime source of truth until a native lifecycle proof is
# available.
_STITCH_ADAPTER_OPERATIONS = (
    "stitch_tile",
    "stitch_tile_normalized",
)

# Multi-stage analysis adapters.  They are intentionally separate from the
# local/stencil list: both require an explicit stage executor and neither is
# eligible for the legacy automatic gate merely by being registered.
_ANALYSIS_ADAPTER_OPERATIONS = (
    "canny_aot",
    "clahe_aot",
)

# FFT is a global frequency-domain transform, not an ordinary spatial tile.
# A separable row/column execution can nevertheless partition the independent
# stages while retaining the complete intermediate spectrum.  The adapter
# below is deliberately semantic/CPU-only: it does not alter AUTO_BLOCK_SAFE,
# legacy dispatch, or native backend evidence.
_FFT_ADAPTER_OPERATIONS = (
    "fft",
    "fft2",
    "ifft2",
)

# Phase correlation consumes two FFTs and reduces the inverse-correlation
# surface to one deterministic ``(dx, dy, response)`` tuple.  It is kept
# separate from the FFT family because its input/output and reduction
# contract are different, even though it reuses the staged FFT oracle.
_PHASE_CORRELATION_ADAPTER_OPERATIONS = (
    "phase_correlation",
)

# AKAZE's descriptor/matcher path is multi-stage and variable-cardinality.
# This bounded adapter qualifies only the deterministic single-scale Hessian
# keypoint detector: a one-pixel guard band protects the local Hessian stencil,
# and grid-cell NMS is merged in row-major order.  Descriptor extraction,
# multi-scale FED diffusion, and matching remain outside this contract.
_AKAZE_ADAPTER_OPERATIONS = (
    "akaze",
)

# Feature/geometry operations are audited separately from dense optical flow.
# AKAZE's bounded adapter covers only a deterministic single-scale keypoint
# stage; descriptors, FED diffusion, matching, and variable-cardinality output
# remain outside the contract.  Homography is a global model reduction and
# must stay full-frame until correspondence ordering and native reduction
# evidence are available.
FEATURE_GEOMETRY_CONTRACT_OPERATIONS = (
    "akaze",
    "find_homography",
)

_FEATURE_GEOMETRY_GAP_REASONS = {
    "akaze": (
        "descriptor/FED/matching stages are multi-stage and variable-cardinality",
        "single-scale keypoint stage is bounded to semantic CPU only",
        "same-backend native full-frame versus tiled parity is unproven",
    ),
    "find_homography": (
        "correspondence reduction and model estimation are global",
        "deterministic variable-cardinality correspondence ordering is unproven",
        "same-backend native reduction parity is unavailable",
    ),
}

_FEATURE_GEOMETRY_REQUIRED_EVIDENCE = {
    "akaze": (
        "CPU parity covering keypoints, descriptors, and matching",
        "non-multiple tiles with guard-band/NMS and stable keypoint ordering",
        "same-backend native full-frame versus tiled parity on each target device",
    ),
    "find_homography": (
        "fixed correspondence capacity and deterministic ordering",
        "global model reduction with explicit outlier/tie semantics",
        "same-backend native reduction parity on each target device",
    ),
}

_GLOBAL_PARTITION_ADAPTER_OPERATIONS = (
    "ransac_flow_cleanup",
    "ransac_flow_cleanup_aot",
    "hough_lines_aot",
)

# Dense optical-flow APIs are deliberately audited as one family.  They have
# historical tile executors (Farneback/LK/block matching) or variable-output
# feature matching (O-FB), but none has a deterministic CPU full-vs-tiled
# parity contract that is safe to promote.  Keep this list separate from the
# adapter registrations below: it is a diagnostic/gap report only and must
# not alter AUTO_BLOCK_SAFE, operation contracts, or native dispatch.
OPTICAL_FLOW_CONTRACT_OPERATIONS = (
    "farneback_flow",
    "lucas_kanade",
    "block_matching",
    "ofb",
)

_OPTICAL_FLOW_GAP_REASONS = {
    "farneback_flow": (
        "multi-stage pyramid, polynomial expansion, and iterative refinement",
        "halo depends on pyramid level and runtime parameters",
        "full-frame versus tiled semantic parity is not proven",
    ),
    "lucas_kanade": (
        "iterative pyramid tracking and dense interpolation",
        "grid-step, level, and tracking-window state crosses tile boundaries",
        "full-frame versus tiled semantic parity is not proven",
    ),
    "block_matching": (
        "iterative pyramid search with parabolic refinement",
        "search-window/level halos and merge semantics are parameter-dependent",
        "full-frame versus tiled semantic parity is not proven",
    ),
    "ofb": (
        "multi-scale FAST keypoint detection and ANMS",
        "BRIEF descriptors, ratio matching, and output ordering are variable-cardinality",
        "no fixed output-domain merge/parity contract is proven",
    ),
}

_OPTICAL_FLOW_REQUIRED_EVIDENCE = {
    "farneback_flow": (
        "deterministic CPU oracle for identical pyramid/iteration parameters",
        "non-multiple tile shapes with level-aware halos",
        "same-backend native full-frame versus tiled parity on each target device",
    ),
    "lucas_kanade": (
        "deterministic CPU oracle including grid tracking and dense interpolation",
        "non-multiple tile shapes with level-aware halos and stable point ordering",
        "same-backend native full-frame versus tiled parity on each target device",
    ),
    "block_matching": (
        "deterministic CPU oracle including search and parabolic refinement",
        "non-multiple tile shapes with search-window halos",
        "same-backend native full-frame versus tiled parity on each target device",
    ),
    "ofb": (
        "fixed keypoint/descriptor capacity and deterministic global ordering",
        "explicit boundary policy for ANMS/ratio matching across tiles",
        "same-backend native full-frame versus tiled parity on each target device",
    ),
}


# A bounded identity-frame specialization is the only dense-flow case that
# can be qualified without making assumptions about pyramid halos, iterative
# tracking state, or search-window ownership.  When the two source frames are
# bitwise identical, ``flow = 0`` is a deterministic fixed-shape map for all
# three dense-flow families.  This is intentionally an explicit semantic CPU
# adapter (not an automatic/native promotion): non-identical frames and any
# unsupported parameter combination continue to use the established
# full-frame path.
OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS = (
    "farneback_flow",
    "lucas_kanade",
    "block_matching",
)

_OPTICAL_FLOW_IDENTITY_RESTRICTIONS = {
    "farneback_flow": (
        "requires bitwise-identical finite 2D reference/comparison frames",
        "requires pyr_scale=0.5, num_levels=1, num_iters=1, poly_n=5, flags=0",
        "flow_init and diagnostics are not accepted",
    ),
    "lucas_kanade": (
        "requires bitwise-identical finite 2D reference/comparison frames",
        "requires maxLevel=0, prevPts/nextPts=None, adaptive=False",
        "requires motion_mode=fast, dense_mode=smooth, and no diagnostics/GPU output",
    ),
    "block_matching": (
        "requires bitwise-identical finite 2D reference/comparison frames",
        "requires a constant frame so the established parabolic refinement is exactly zero",
        "requires maxLevel=0, prevPts/nextPts=None, adaptive=False",
        "requires motion_mode=fast, dense_mode=smooth, and no diagnostics/GPU output",
    ),
}


_ADAPTER_OPERATIONS = tuple(_REFERENCE_FUNCTIONS)


def _histogram_reference(
    array: np.ndarray,
    bins: int = 256,
    range_min: float = 0.0,
    range_max: float = 256.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Deterministic histogram oracle matching ``histogram_aot`` semantics."""

    data = np.asarray(array, dtype=np.float32)
    bins = int(bins)
    if data.ndim not in (1, 2, 3):
        raise ValueError("histogram input must be 1D, 2D, or 3D")
    if bins <= 0 or float(range_max) <= float(range_min):
        raise ValueError("histogram range and bins are invalid")
    counts, edges = np.histogram(
        data.reshape(-1),
        bins=bins,
        range=(float(range_min), float(range_max)),
    )
    return counts.astype(np.int64, copy=False), edges.astype(np.float32, copy=False)


def _otsu_threshold_from_histogram(histogram: np.ndarray) -> float:
    counts = np.asarray(histogram, dtype=np.float64).reshape(-1)
    total = float(counts.sum())
    if total <= 0.0:
        return 0.0
    mu_total = float(np.dot(np.arange(counts.size, dtype=np.float64), counts)) / total
    weight0 = sum0 = max_sigma = 0.0
    best_t = 0
    for index, count_value in enumerate(counts):
        weight0 += float(count_value)
        if weight0 == 0.0:
            continue
        weight1 = total - weight0
        if weight1 == 0.0:
            break
        sum0 += float(index) * float(count_value)
        sigma = weight0 * weight1 * (
            (sum0 / weight0)
            - ((mu_total * total - sum0) / weight1)
        ) ** 2
        if sigma > max_sigma:
            max_sigma = sigma
            best_t = index
    return float(best_t)


def _otsu_reference(
    array: np.ndarray,
    thresh_type: int = 0,
    max_val: float = 255.0,
    bins: int = 256,
) -> tuple[float, np.ndarray]:
    data = np.asarray(array, dtype=np.float32)
    hist, _edges = _histogram_reference(data, bins=bins, range_min=0.0, range_max=max_val)
    threshold = _otsu_threshold_from_histogram(hist)
    if int(thresh_type) == 0:
        result = np.where(data > threshold, float(max_val), 0.0)
    elif int(thresh_type) == 1:
        result = np.where(data > threshold, 0.0, float(max_val))
    else:
        result = np.where(data > threshold, data, 0.0)
    return threshold, np.ascontiguousarray(result, dtype=np.float32)


def _map_histogram(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    params = _as_params(context)
    counts, _edges = _histogram_reference(
        inputs[0],
        bins=int(params.get("bins", 256)),
        range_min=float(params.get("range_min", 0.0)),
        range_max=float(params.get("range_max", 256.0)),
    )
    return counts


def _map_otsu(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    params = _as_params(context)
    counts, _edges = _histogram_reference(
        inputs[0],
        bins=int(params.get("bins", 256)),
        range_min=0.0,
        range_max=float(params.get("max_val", 255.0)),
    )
    return counts


def _map_reduce_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return value.ndim == 1 and value.size > 0 and np.issubdtype(value.dtype, np.integer)


def _map_reduce_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    output[...] += np.asarray(result, dtype=output.dtype)
    return output


def _histogram_finalize(
    accumulator: np.ndarray,
    _inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    bins = int(params.get("bins", 256))
    range_min = float(params.get("range_min", 0.0))
    range_max = float(params.get("range_max", 256.0))
    edges = np.linspace(range_min, range_max, bins + 1, dtype=np.float32)
    return np.asarray(accumulator, dtype=np.int64), edges


def _otsu_finalize(
    accumulator: np.ndarray,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> tuple[float, np.ndarray]:
    threshold = _otsu_threshold_from_histogram(accumulator)
    data = np.asarray(inputs[0], dtype=np.float32)
    thresh_type = int(params.get("thresh_type", 0))
    max_val = float(params.get("max_val", 255.0))
    if thresh_type == 0:
        result = np.where(data > threshold, max_val, 0.0)
    elif thresh_type == 1:
        result = np.where(data > threshold, 0.0, max_val)
    else:
        result = np.where(data > threshold, data, 0.0)
    return threshold, np.ascontiguousarray(result, dtype=np.float32)


def _ssim_window_radius(window_size: int) -> int:
    """Validate an SSIM window and return its symmetric halo radius.

    The AOT SSIM kernel supports odd windows up to 21 samples.  Keeping the
    same bound here is important: a dynamic halo must never be guessed from a
    caller value that the native graph would reject.
    """

    value = int(window_size)
    if value < 1 or value > 21 or value % 2 == 0:
        raise ValueError("SSIM window_size must be odd and no larger than 21")
    return value // 2


def _ssim_constants(
    array: np.ndarray, params: Mapping[str, Any]
) -> tuple[int, float, float]:
    """Resolve deterministic SSIM parameters once for the whole input."""

    radius = _ssim_window_radius(int(params.get("window_size", 11)))
    if "data_range" in params and params.get("data_range") is not None:
        data_range = float(params["data_range"])
    elif np.issubdtype(np.asarray(array).dtype, np.integer):
        data_range = float(np.iinfo(np.asarray(array).dtype).max)
    else:
        data = np.asarray(array, dtype=np.float64)
        data_range = float(np.max(data) - np.min(data)) if data.size else 1.0
        if data_range <= 0.0:
            data_range = 1.0
    if not np.isfinite(data_range) or data_range <= 0.0:
        raise ValueError("SSIM data_range must be finite and positive")
    k1 = float(params.get("k1", 0.01))
    k2 = float(params.get("k2", 0.03))
    if k1 < 0.0 or k2 < 0.0:
        raise ValueError("SSIM k1 and k2 must be non-negative")
    return radius, float((k1 * data_range) ** 2), float((k2 * data_range) ** 2)


def _ssim_map_reference(
    first: np.ndarray,
    second: np.ndarray,
    radius: int,
    c1: float,
    c2: float,
) -> np.ndarray:
    """Return the per-pixel SSIM map used by the AOT reference kernel.

    Integral images keep the oracle bounded and deterministic while preserving
    the clipped-border semantics of ``image_processing/compile_extended_tcm``.
    The map is deliberately computed in float64; both full-frame and tiled
    paths use this same oracle, and the reduction accumulator is float64 so
    merge ordering is explicit rather than dependent on NumPy's tile shape.
    """

    a = np.ascontiguousarray(np.asarray(first, dtype=np.float64))
    b = np.ascontiguousarray(np.asarray(second, dtype=np.float64))
    if a.ndim != 2 or b.ndim != 2 or a.shape != b.shape:
        raise ValueError("SSIM channel inputs must be matching 2D arrays")
    height, width = a.shape
    if height == 0 or width == 0:
        return np.empty_like(a, dtype=np.float64)

    def _integral(values: np.ndarray) -> np.ndarray:
        cumulative = np.cumsum(np.cumsum(values, axis=0, dtype=np.float64), axis=1, dtype=np.float64)
        result = np.zeros((height + 1, width + 1), dtype=np.float64)
        result[1:, 1:] = cumulative
        return result

    integral_a = _integral(a)
    integral_b = _integral(b)
    integral_a2 = _integral(a * a)
    integral_b2 = _integral(b * b)
    integral_ab = _integral(a * b)

    rows = np.arange(height, dtype=np.int64)
    cols = np.arange(width, dtype=np.int64)
    y0 = np.maximum(rows - int(radius), 0)
    y1 = np.minimum(rows + int(radius) + 1, height)
    x0 = np.maximum(cols - int(radius), 0)
    x1 = np.minimum(cols + int(radius) + 1, width)

    def _window_sum(integral: np.ndarray) -> np.ndarray:
        return (
            integral[y1[:, None], x1[None, :]]
            - integral[y0[:, None], x1[None, :]]
            - integral[y1[:, None], x0[None, :]]
            + integral[y0[:, None], x0[None, :]]
        )

    count = (y1 - y0)[:, None] * (x1 - x0)[None, :]
    count = np.maximum(count.astype(np.float64), 1.0)
    mean_a = _window_sum(integral_a) / count
    mean_b = _window_sum(integral_b) / count
    var_a = _window_sum(integral_a2) / count - mean_a * mean_a
    var_b = _window_sum(integral_b2) / count - mean_b * mean_b
    covariance = _window_sum(integral_ab) / count - mean_a * mean_b
    numerator = (2.0 * mean_a * mean_b + float(c1)) * (2.0 * covariance + float(c2))
    denominator = (mean_a * mean_a + mean_b * mean_b + float(c1)) * (
        var_a + var_b + float(c2)
    )
    # C2 is positive for the supported public defaults.  Guarding zero keeps
    # the semantic adapter deterministic for an explicitly zero-constant call.
    result = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator != 0.0)
    return np.ascontiguousarray(result, dtype=np.float64)


def _ssim_reference(
    first: np.ndarray,
    second: np.ndarray,
    *,
    window_size: int = 11,
    data_range: Optional[float] = None,
    k1: float = 0.01,
    k2: float = 0.03,
) -> float:
    """Full-frame SSIM semantic oracle matching ``ssim_aot`` aggregation."""

    a = np.asarray(first)
    b = np.asarray(second)
    if a.shape != b.shape or a.ndim not in (2, 3):
        raise ValueError("SSIM inputs must have identical 2D or 3D shapes")
    values = {
        "window_size": int(window_size),
        "k1": float(k1),
        "k2": float(k2),
    }
    if data_range is not None:
        values["data_range"] = float(data_range)
    radius, c1, c2 = _ssim_constants(a, values)
    channels = 1 if a.ndim == 2 else int(a.shape[2])
    if channels <= 0:
        return 0.0
    total = 0.0
    count = 0
    for channel in range(channels):
        left = a if a.ndim == 2 else a[..., channel]
        right = b if b.ndim == 2 else b[..., channel]
        score_map = _ssim_map_reference(left, right, radius, c1, c2)
        total += float(np.sum(score_map, dtype=np.float64))
        count += int(score_map.size)
    return float(total / max(count, 1))


def _map_ssim(context: Any) -> np.ndarray:
    """Map one halo tile to ``[sum_ssim, valid_count]``."""

    inputs = _as_inputs(context)
    if len(inputs) != 2 or inputs[0].shape != inputs[1].shape:
        raise ValueError("ssim_aot map expects two matching inputs")
    block = _context_value(context, "block")
    params = _as_params(context)
    radius, c1, c2 = _ssim_constants(inputs[0], params)
    channels = 1 if inputs[0].ndim == 2 else int(inputs[0].shape[2])
    total = 0.0
    count = 0
    for channel in range(channels):
        left = inputs[0] if inputs[0].ndim == 2 else inputs[0][..., channel]
        right = inputs[1] if inputs[1].ndim == 2 else inputs[1][..., channel]
        score_map = _ssim_map_reference(left, right, radius, c1, c2)
        if block is not None:
            score_map = score_map[block.core_slice]
        total += float(np.sum(score_map, dtype=np.float64))
        count += int(score_map.size)
    return np.asarray((total, float(count)), dtype=np.float64)


def _ssim_map_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(
        value.shape == (2,)
        and np.isfinite(value).all()
        and float(value[1]) >= 0.0
    )


def _ssim_finalize(
    accumulator: np.ndarray,
    _inputs: Sequence[np.ndarray],
    _params: Mapping[str, Any],
) -> float:
    values = np.asarray(accumulator, dtype=np.float64).reshape(-1)
    if values.size != 2:
        raise ValueError("SSIM reduction accumulator must contain sum and count")
    return float(values[0] / max(float(values[1]), 1.0))


def _ncc_inputs(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[np.ndarray, np.ndarray, int, tuple[int, int], float, float]:
    """Validate a semantic NCC call and resolve its global template stats.

    The maintained AOT graph accepts two 2-D floating arrays and evaluates a
    sliding template over the source image.  The semantic adapter accepts
    numeric NumPy arrays (matching the public wrapper's upload conversion),
    widens them to float64 for a stable oracle, and emits float32 scores just
    like the native graph's destination buffer.  Template statistics are
    resolved once for the whole call; they must never be recomputed per tile.
    """

    if len(inputs) != 2:
        raise ValueError("NCC expects image and template inputs")
    image = np.asarray(inputs[0])
    template = np.asarray(inputs[1])
    if image.ndim != 2 or template.ndim != 2:
        raise ValueError("NCC semantic adapter supports only 2D arrays")
    if image.size == 0 or template.size == 0:
        raise ValueError("NCC inputs must be non-empty")
    if not np.issubdtype(image.dtype, np.number) or not np.issubdtype(
        template.dtype, np.number
    ):
        raise TypeError("NCC inputs must be numeric")
    if not np.isfinite(image).all() or not np.isfinite(template).all():
        raise ValueError("NCC inputs must contain only finite values")
    stride = int(params.get("stride", 1))
    if stride <= 0:
        raise ValueError("NCC stride must be positive")
    image_height, image_width = (int(image.shape[0]), int(image.shape[1]))
    template_height, template_width = (int(template.shape[0]), int(template.shape[1]))
    if template_height > image_height or template_width > image_width:
        raise ValueError("NCC template must fit inside the image")
    output_shape = (
        (image_height - template_height) // stride + 1,
        (image_width - template_width) // stride + 1,
    )
    if output_shape[0] <= 0 or output_shape[1] <= 0:
        raise ValueError("NCC produces an empty search surface")
    source = np.ascontiguousarray(image, dtype=np.float64)
    pattern = np.ascontiguousarray(template, dtype=np.float64)
    sample_count = float(template_height * template_width)
    sum_template = float(np.sum(pattern, dtype=np.float64))
    variance_template_n = float(
        max(
            0.0,
            float(np.sum(pattern * pattern, dtype=np.float64))
            - (sum_template * sum_template / sample_count),
        )
    )
    return (
        source,
        pattern,
        stride,
        output_shape,
        sum_template,
        variance_template_n,
    )


def _ncc_source_halo(template: np.ndarray) -> tuple[int, int]:
    """Return the source footprint beyond an output anchor.

    This is deliberately a tuple because a rectangular template has
    independent vertical/horizontal dependencies.  ``BlockSpec.halo`` is a
    scalar for legacy image tiles, so the richer adapter carries this exact
    source halo in metadata and validates it before dispatch.
    """

    return (max(0, int(template.shape[0]) - 1), max(0, int(template.shape[1]) - 1))


def _ncc_score_tile(
    image: np.ndarray,
    template: np.ndarray,
    block: BlockSpec,
    *,
    stride: int,
    sum_template: float,
    variance_template_n: float,
) -> np.ndarray:
    """Compute one output-search tile in deterministic row-major order."""

    tile_height, tile_width = block.shape
    template_height, template_width = template.shape
    sample_count = float(template_height * template_width)
    scores = np.empty((tile_height, tile_width), dtype=np.float32)
    for local_y, output_y in enumerate(range(int(block.y0), int(block.y1))):
        source_y = output_y * int(stride)
        for local_x, output_x in enumerate(range(int(block.x0), int(block.x1))):
            source_x = output_x * int(stride)
            patch = image[
                source_y : source_y + template_height,
                source_x : source_x + template_width,
            ]
            sum_image = float(np.sum(patch, dtype=np.float64))
            variance_image_n = max(
                0.0,
                float(np.sum(patch * patch, dtype=np.float64))
                - (sum_image * sum_image / sample_count),
            )
            correlation = float(np.sum(patch * template, dtype=np.float64))
            numerator = correlation - (sum_image * sum_template / sample_count)
            denominator = float(
                np.sqrt(max(1.0e-12, variance_image_n * variance_template_n))
            )
            value = np.clip(numerator / denominator, -1.0, 1.0)
            scores[local_y, local_x] = np.float32(value)
    return np.ascontiguousarray(scores, dtype=np.float32)


def _ncc_reference(
    image: np.ndarray,
    template: np.ndarray,
    *,
    stride: int = 1,
) -> np.ndarray:
    """Full-frame ZNCC search-surface oracle matching ``ncc.py`` semantics."""

    source, pattern, resolved_stride, output_shape, sum_t, var_t_n = _ncc_inputs(
        (image, template), {"stride": stride}
    )
    full_block = BlockSpec(
        index=0,
        row=0,
        column=0,
        y0=0,
        x0=0,
        y1=output_shape[0],
        x1=output_shape[1],
        read_y0=0,
        read_x0=0,
        read_y1=output_shape[0],
        read_x1=output_shape[1],
    )
    return _ncc_score_tile(
        source,
        pattern,
        full_block,
        stride=resolved_stride,
        sum_template=sum_t,
        variance_template_n=var_t_n,
    )


def _ncc_alignment_reference(
    image: np.ndarray,
    template: np.ndarray,
    *,
    stride: int = 1,
) -> tuple[float, float, float]:
    """Return ``(dx, dy, confidence)`` using deterministic first-max order."""

    scores = _ncc_reference(image, template, stride=stride)
    flat_index = int(np.argmax(scores))
    output_y, output_x = np.unravel_index(flat_index, scores.shape)
    return (
        float(int(output_x) * int(stride)),
        float(int(output_y) * int(stride)),
        float(scores[output_y, output_x]),
    )


def _ncc_output_shape(
    arrays: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[int, int]:
    _source, _pattern, _stride, output_shape, _sum_t, _var_t_n = _ncc_inputs(
        arrays, params
    )
    return output_shape


def _ncc_reader(context: Any, block: BlockSpec) -> PartitionContext:
    """Keep the full source/template and attach the output-domain contract."""

    arrays = _as_inputs(context)
    params = _as_params(context)
    _source, pattern, _stride, output_shape, _sum_t, _var_t_n = _ncc_inputs(
        arrays, params
    )
    source_halo = _ncc_source_halo(pattern)
    # A source window is not sliced here: the runner uses the output anchor
    # and template shape to avoid accidentally applying an output-space halo
    # to source pixels.  The exact footprint remains available in metadata and
    # is asserted by the validator below.
    merged_params = dict(params)
    merged_params["source_halo"] = source_halo
    return PartitionContext(
        operation=str(_context_value(context, "operation", "zncc")),
        inputs=arrays,
        block=block,
        full_shape=output_shape,
        params=merged_params,
        output_shape=output_shape,
    )


def _ncc_map(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    params = _as_params(context)
    block = _context_value(context, "block")
    if block is None:
        raise ValueError("NCC map requires an output block")
    source, pattern, stride, _output_shape_value, sum_t, var_t_n = _ncc_inputs(
        inputs, params
    )
    return _ncc_score_tile(
        source,
        pattern,
        block,
        stride=stride,
        sum_template=sum_t,
        variance_template_n=var_t_n,
    )


def _ncc_alignment_map(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    params = _as_params(context)
    block = _context_value(context, "block")
    if block is None:
        raise ValueError("NCC alignment map requires an output block")
    source, pattern, stride, _output_shape_value, sum_t, var_t_n = _ncc_inputs(
        inputs, params
    )
    scores = _ncc_score_tile(
        source,
        pattern,
        block,
        stride=stride,
        sum_template=sum_t,
        variance_template_n=var_t_n,
    )
    local_flat = int(np.argmax(scores))
    local_y, local_x = np.unravel_index(local_flat, scores.shape)
    return np.asarray(
        (
            float(scores[local_y, local_x]),
            float(int(block.y0) + int(local_y)),
            float(int(block.x0) + int(local_x)),
        ),
        dtype=np.float64,
    )


def _ncc_map_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    value = np.asarray(result)
    if block is None:
        return False
    return bool(
        value.shape == tuple(block.shape)
        and np.isfinite(value).all()
        and np.all(value >= np.float32(-1.0))
        and np.all(value <= np.float32(1.0))
    )


def _ncc_alignment_map_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result, dtype=np.float64).reshape(-1)
    return bool(
        value.size == 3
        and np.isfinite(value).all()
        and -1.0 <= float(value[0]) <= 1.0
    )


def _ncc_map_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    output[block.write_slice] = np.asarray(result, dtype=np.float32)
    return output


def _ncc_alignment_merger(
    output: Any, result: Any, _context_or_block: Any
) -> Any:
    candidate = np.asarray(result, dtype=np.float64).reshape(-1)
    current = np.asarray(output, dtype=np.float64).reshape(-1)
    # Blocks and each tile's score map are scanned row-major.  Strict ``>``
    # preserves the first candidate on ties, matching np.argmax(full_map).
    if candidate[0] > current[0]:
        output[...] = candidate
    return output


def _ncc_map_finalize(
    accumulator: np.ndarray,
    _inputs: Sequence[np.ndarray],
    _params: Mapping[str, Any],
) -> np.ndarray:
    return np.ascontiguousarray(accumulator, dtype=np.float32)


def _ncc_alignment_finalize(
    accumulator: np.ndarray,
    _inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> tuple[float, float, float]:
    values = np.asarray(accumulator, dtype=np.float64).reshape(-1)
    if values.size != 3 or not np.isfinite(values).all():
        raise ValueError("NCC alignment reduction accumulator is invalid")
    stride = int(params.get("stride", 1))
    return (
        float(values[2] * stride),
        float(values[1] * stride),
        float(values[0]),
    )


def _stitch_inputs(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
]:
    """Validate a stack of overlapping tile contributions.

    The five-array form mirrors the common AOT kernels and takes ``y0s`` and
    ``x0s`` from ``params``.  An additive seven-array form accepts those two
    origin vectors as the final inputs, which is convenient for callers that
    avoid non-array metadata.  A shared ``tile_weight`` (H x W) and a
    per-tile weight stack (T x H x W) are both accepted.
    """

    if len(inputs) not in (5, 7):
        raise ValueError(
            "stitch adapter expects tiles, tile_weight, hanning, accum, "
            "weight_accum plus optional y0s/x0s"
        )
    tiles = np.asarray(inputs[0])
    tile_weight = np.asarray(inputs[1])
    hanning = np.asarray(inputs[2])
    accum = np.asarray(inputs[3])
    weight_accum = np.asarray(inputs[4])
    if tiles.ndim not in (3, 4):
        raise ValueError("stitch tiles must have shape (T,H,W) or (T,H,W,C)")
    tile_count, tile_height, tile_width = map(int, tiles.shape[:3])
    if tile_count <= 0 or tile_height <= 0 or tile_width <= 0:
        raise ValueError("stitch tile stack must be non-empty")
    if not np.issubdtype(tiles.dtype, np.number):
        raise TypeError("stitch tiles must be numeric")
    if tiles.ndim == 4 and int(tiles.shape[3]) not in (1, 3, 4):
        raise ValueError("stitch tile channels must be 1, 3, or 4")
    if tile_weight.ndim == 2:
        if tuple(tile_weight.shape) != (tile_height, tile_width):
            raise ValueError("shared tile_weight must match tile dimensions")
    elif tile_weight.ndim == 3:
        if tuple(tile_weight.shape) != (tile_count, tile_height, tile_width):
            raise ValueError("per-tile tile_weight must match tile stack")
    else:
        raise ValueError("tile_weight must be HxW or TxHxW")
    if tuple(hanning.shape) != (tile_height, tile_width):
        raise ValueError("hanning must match tile dimensions")
    if not np.issubdtype(tile_weight.dtype, np.number) or not np.issubdtype(
        hanning.dtype, np.number
    ):
        raise TypeError("stitch weights must be numeric")
    if accum.ndim not in (2, 3):
        raise ValueError("accum must be HxW or HxWxC")
    if tiles.ndim == 3 and accum.ndim != 2:
        raise ValueError("scalar tiles require a scalar accumulator")
    if tiles.ndim == 4:
        if accum.ndim != 3 or tuple(accum.shape[2:]) != tuple(tiles.shape[3:]):
            raise ValueError("vector tiles and accumulator channels must match")
    if weight_accum.ndim != 2 or tuple(weight_accum.shape) != tuple(accum.shape[:2]):
        raise ValueError("weight_accum must match accumulator height/width")
    if not np.issubdtype(accum.dtype, np.floating) or not np.issubdtype(
        weight_accum.dtype, np.floating
    ):
        raise TypeError("stitch accumulators must use floating-point dtypes")
    if not (
        np.isfinite(tiles).all()
        and np.isfinite(tile_weight).all()
        and np.isfinite(hanning).all()
        and np.isfinite(accum).all()
        and np.isfinite(weight_accum).all()
    ):
        raise ValueError("stitch inputs must contain only finite values")

    if len(inputs) == 7:
        y0s = np.asarray(inputs[5])
        x0s = np.asarray(inputs[6])
    else:
        if "y0s" not in params or "x0s" not in params:
            raise ValueError("stitch adapter requires y0s and x0s origins")
        y0s = np.asarray(params["y0s"])
        x0s = np.asarray(params["x0s"])
    if y0s.ndim == 0 and tile_count == 1:
        y0s = y0s.reshape(1)
    if x0s.ndim == 0 and tile_count == 1:
        x0s = x0s.reshape(1)
    if y0s.ndim != 1 or x0s.ndim != 1 or y0s.size != tile_count or x0s.size != tile_count:
        raise ValueError("stitch origins must be one-dimensional vectors of length T")
    if not np.issubdtype(y0s.dtype, np.integer) or not np.issubdtype(x0s.dtype, np.integer):
        raise TypeError("stitch origins must be integer coordinates")
    height, width = map(int, accum.shape[:2])
    if np.any(y0s < 0) or np.any(x0s < 0):
        raise ValueError("stitch origins must be non-negative")
    if np.any(y0s + tile_height > height) or np.any(x0s + tile_width > width):
        raise ValueError("stitch tile footprint exceeds accumulator bounds")
    return (
        np.ascontiguousarray(tiles, dtype=np.float64),
        np.ascontiguousarray(tile_weight, dtype=np.float64),
        np.ascontiguousarray(hanning, dtype=np.float64),
        np.ascontiguousarray(accum, dtype=np.float64),
        np.ascontiguousarray(weight_accum, dtype=np.float64),
        np.ascontiguousarray(y0s, dtype=np.int64),
        np.ascontiguousarray(x0s, dtype=np.int64),
    )


def _stitch_order(y0s: np.ndarray, x0s: np.ndarray) -> tuple[int, ...]:
    """Canonical row-major tile order with input index as a stable tie-break."""

    return tuple(
        sorted(
            range(int(y0s.size)),
            key=lambda index: (int(y0s[index]), int(x0s[index]), int(index)),
        )
    )


def _stitch_apply(
    operation: str,
    accum: np.ndarray,
    weight_accum: np.ndarray,
    tile: np.ndarray,
    tile_weight: np.ndarray,
    hanning: np.ndarray,
    y0: int,
    x0: int,
) -> None:
    weighted = hanning * tile_weight
    destination = (slice(int(y0), int(y0) + tile.shape[0]), slice(int(x0), int(x0) + tile.shape[1]))
    if operation == "stitch_tile":
        if tile.ndim == 2:
            accum[destination] += tile * weighted
        else:
            accum[destination] += tile * weighted[..., None]
        weight_accum[destination] += weighted
        return
    if operation != "stitch_tile_normalized":
        raise ValueError(f"unknown stitch operation: {operation}")
    old_weight = weight_accum[destination]
    new_weight = old_weight + weighted
    valid = new_weight > np.float64(1.0e-6)
    if tile.ndim == 2:
        old_values = accum[destination]
        accum[destination] = np.where(
            valid,
            (old_values * old_weight + tile * weighted) / np.maximum(new_weight, 1.0e-6),
            old_values,
        )
    else:
        old_values = accum[destination]
        accum[destination] = np.where(
            valid[..., None],
            (old_values * old_weight[..., None] + tile * weighted[..., None])
            / np.maximum(new_weight[..., None], 1.0e-6),
            old_values,
        )
    weight_accum[destination] = np.where(valid, new_weight, old_weight)


def _stitch_reference(
    operation: str,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    accum_dtype = np.asarray(inputs[3]).dtype
    weight_dtype = np.asarray(inputs[4]).dtype
    tiles, tile_weight, hanning, accum, weight_accum, y0s, x0s = _stitch_inputs(
        inputs, params
    )
    order = _stitch_order(y0s, x0s)
    output = np.array(accum, dtype=np.float64, copy=True)
    weights = np.array(weight_accum, dtype=np.float64, copy=True)
    for index in order:
        weights_for_tile = tile_weight if tile_weight.ndim == 2 else tile_weight[index]
        _stitch_apply(
            operation,
            output,
            weights,
            tiles[index],
            weights_for_tile,
            hanning,
            int(y0s[index]),
            int(x0s[index]),
        )
    return output.astype(accum_dtype, copy=False), weights.astype(weight_dtype, copy=False)


def _stitch_output_factory(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[np.ndarray, np.ndarray]:
    _tiles, _tile_weight, _hanning, accum, weight_accum, _y0s, _x0s = _stitch_inputs(
        inputs, params
    )
    return np.array(accum, dtype=np.float64, copy=True), np.array(
        weight_accum, dtype=np.float64, copy=True
    )


def _stitch_reader(context: Any, block: BlockSpec) -> PartitionContext:
    arrays = _as_inputs(context)
    params = _as_params(context)
    _tiles, _weights, _hanning, _accum, _weight_accum, y0s, x0s = _stitch_inputs(
        arrays, params
    )
    order = _stitch_order(y0s, x0s)
    values = dict(params)
    values["_stitch_order"] = order
    return PartitionContext(
        operation=str(_context_value(context, "operation", "stitch_tile")),
        inputs=arrays,
        block=block,
        full_shape=tuple(_context_value(context, "full_shape", ())),
        params=values,
    )


def _stitch_map(context: Any) -> list[tuple[int, np.ndarray, np.ndarray, np.ndarray, int, int]]:
    arrays = _as_inputs(context)
    params = _as_params(context)
    operation = str(_context_value(context, "operation", "stitch_tile"))
    block = _context_value(context, "block")
    if block is None:
        raise ValueError("stitch map requires a tile-index block")
    tiles, tile_weight, hanning, _accum, _weight_accum, y0s, x0s = _stitch_inputs(
        arrays, params
    )
    order = tuple(params.get("_stitch_order", _stitch_order(y0s, x0s)))
    partials: list[tuple[int, np.ndarray, np.ndarray, np.ndarray, int, int]] = []
    for rank in range(int(block.y0), int(block.y1)):
        index = int(order[rank])
        weights_for_tile = tile_weight if tile_weight.ndim == 2 else tile_weight[index]
        partials.append(
            (
                index,
                np.array(tiles[index], dtype=np.float64, copy=True),
                np.array(weights_for_tile, dtype=np.float64, copy=True),
                np.array(hanning, dtype=np.float64, copy=True),
                int(y0s[index]),
                int(x0s[index]),
            )
        )
    return partials


def _stitch_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    if not isinstance(result, (list, tuple)) or not result:
        return False
    for item in result:
        if not isinstance(item, (list, tuple)) or len(item) != 6:
            return False
        _index, tile, weights, hanning, _y0, _x0 = item
        if np.asarray(tile).ndim not in (2, 3) or np.asarray(weights).ndim != 2:
            return False
        if np.asarray(hanning).ndim != 2:
            return False
        if not np.isfinite(np.asarray(tile)).all() or not np.isfinite(np.asarray(weights)).all():
            return False
    return True


def _stitch_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    operation = "stitch_tile"
    if isinstance(_context_or_block, PartitionContext):
        operation = str(_context_or_block.operation)
    elif hasattr(_context_or_block, "operation"):
        operation = str(getattr(_context_or_block, "operation"))
    accum, weight_accum = output
    for _index, tile, tile_weight, hanning, y0, x0 in result:
        _stitch_apply(operation, accum, weight_accum, tile, tile_weight, hanning, y0, x0)
    return output


def _stitch_finalize(
    accumulator: tuple[np.ndarray, np.ndarray],
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> tuple[np.ndarray, np.ndarray]:
    _tiles, _tile_weight, _hanning, accum, weight_accum, _y0s, _x0s = _stitch_inputs(
        inputs, params
    )
    return (
        np.asarray(accumulator[0], dtype=np.asarray(inputs[3]).dtype),
        np.asarray(accumulator[1], dtype=np.asarray(inputs[4]).dtype),
    )


def _bm3d_identity_reference(
    inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> np.ndarray:
    """Exact bounded BM3D semantic baseline for ``sigma == 0``.

    The production BM3D graph performs non-local grouping and 3-D transforms;
    those dependencies are intentionally not approximated here.  With zero
    noise sigma the mathematically defined denoising result is the input
    itself, so this reference is an auditable pointwise identity for finite
    float32 grayscale/RGB frames.  Any non-zero sigma or unsupported dtype is
    rejected so the caller falls back to its original full-frame operation.
    """

    if len(inputs) != 1:
        raise ValueError("bm3d semantic identity expects one image input")
    source = np.asarray(inputs[0])
    if source.ndim not in (2, 3) or (source.ndim == 3 and source.shape[-1] not in (1, 3)):
        raise ValueError("bm3d semantic identity expects HxW or HxWx{1,3} input")
    if source.dtype != np.dtype(np.float32):
        raise TypeError("bm3d semantic identity requires float32 input")
    if not np.isfinite(source).all():
        raise ValueError("bm3d semantic identity input must be finite")
    sigma = params.get("sigma")
    if sigma is None:
        raise ValueError("bm3d semantic identity requires explicit sigma=0")
    try:
        sigma_value = float(sigma)
    except (TypeError, ValueError) as exc:
        raise ValueError("bm3d semantic identity requires sigma exactly zero") from exc
    if not np.isfinite(sigma_value) or sigma_value != 0.0:
        raise ValueError("bm3d semantic adapter only supports explicit sigma=0")
    return np.ascontiguousarray(source, dtype=np.float32)


_MAP_REDUCE_OPERATIONS = (
    "histogram",
    "otsu_threshold",
    "ssim_aot",
    *_NCC_ADAPTER_OPERATIONS,
    *_STITCH_ADAPTER_OPERATIONS,
)


def _reference(operation: str, inputs: Sequence[np.ndarray], params: Mapping[str, Any]) -> Any:
    canonical = canonical_operation_name(operation)
    if canonical in _BM3D_ADAPTER_OPERATIONS:
        return _bm3d_identity_reference(inputs, params)
    if canonical in _FFT_ADAPTER_OPERATIONS:
        return _fft_reference(canonical, inputs, params)
    if canonical in _PHASE_CORRELATION_ADAPTER_OPERATIONS:
        return _phase_correlation_reference(inputs, params)
    if canonical in _AKAZE_ADAPTER_OPERATIONS:
        if len(inputs) != 1:
            raise ValueError(
                "AKAZE semantic partition supports one image for the keypoint stage; "
                "descriptor/matching inputs remain full-frame"
            )
        return _akaze_keypoints_reference(inputs[0], params)
    if canonical in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS:
        values = dict(params or {})
        values.setdefault("operation", canonical)
        return _optical_flow_identity_reference(inputs, values)
    if canonical == "align_mtb":
        if len(inputs) != 2:
            raise ValueError("align_mtb adapter expects reference and target inputs")
        return _mtb_reference(
            inputs[0],
            inputs[1],
            max_levels=int(params.get("max_levels", 6)),
            tolerance=float(params.get("tolerance", 4.0 / 255.0)),
        )
    if canonical == "joint_bilateral_upsample":
        if len(inputs) != 2:
            raise ValueError(
                "joint_bilateral_upsample adapter expects source and guide inputs"
            )
        return _jblu_reference(
            inputs[0],
            inputs[1],
            preset=str(params.get("preset", "medium")),
        )
    if canonical == "bilateral_grid_filter":
        if len(inputs) != 1:
            raise ValueError("bilateral_grid_filter adapter expects one source input")
        return _bilateral_grid_reference(
            inputs[0],
            preset=str(params.get("preset", "medium")),
        )
    if canonical == "inpaint":
        if len(inputs) != 2:
            raise ValueError("inpaint adapter expects source and mask inputs")
        return _inpaint_reference(
            inputs[0],
            inputs[1],
            # Keep raw values here so the semantic guard rejects fractional
            # radii/invalid flags instead of silently truncating them before
            # reaching ``_inpaint_parameters``.
            inpaint_radius=params.get("inpaint_radius", params.get("radius", 3)),
            flags=params.get("flags", 0),
        )
    if canonical in {"ransac_flow_cleanup", "ransac_flow_cleanup_aot"}:
        if len(inputs) != 1:
            raise ValueError(f"{canonical} adapter expects one flow input")
        return _ransac_reference(
            inputs[0],
            threshold=float(params.get("threshold", 1.0)),
            stride_refine=int(params.get("stride_refine", 1)),
            stride_final=int(params.get("stride_final", 1)),
        )
    if canonical == "hough_lines_aot":
        if len(inputs) != 1:
            raise ValueError("hough_lines_aot adapter expects one edge image")
        return _hough_reference(
            inputs[0],
            rho_resolution=float(params.get("rho_resolution", 1.0)),
            theta_resolution=float(params.get("theta_resolution", 1.0)),
            threshold=int(params.get("threshold", 80)),
            nms_radius=int(params.get("nms_radius", 10)),
            max_peaks=int(params.get("max_peaks", 500)),
            edge_threshold=float(params.get("edge_threshold", 128.0)),
        )
    if canonical == "canny_aot":
        if len(inputs) != 1:
            raise ValueError("canny_aot adapter expects one grayscale image")
        return _canny_reference(
            inputs[0],
            low_threshold=float(params.get("low_threshold", params.get("low", 50.0))),
            high_threshold=float(params.get("high_threshold", params.get("high", 150.0))),
            aperture_size=int(params.get("aperture_size", 3)),
        )
    if canonical == "clahe_aot":
        if len(inputs) != 1:
            raise ValueError("clahe_aot adapter expects one grayscale image")
        return _clahe_reference(
            inputs[0],
            clip_limit=float(params.get("clip_limit", 2.0)),
            tile_grid_size=tuple(params.get("tile_grid_size", (8, 8))),
            num_bins=int(params.get("num_bins", 256)),
        )
    if canonical == "copy_field":
        if len(inputs) != 1:
            raise ValueError("copy_field adapter expects one source image")
        return _copy_reference(inputs[0])
    if canonical == "gaussian_blur":
        if len(inputs) != 1:
            raise ValueError("gaussian_blur adapter expects one source image")
        kernel_size = params.get("kernel_size")
        if kernel_size is None:
            kernel_size = int(np.ceil(3.0 * float(params.get("sigma", 1.0)))) * 2 + 1
        return _gaussian_blur_reference(
            inputs[0],
            sigma=float(params.get("sigma", 1.0)),
            kernel_size=int(kernel_size),
        )
    if canonical == "box_filter":
        if len(inputs) != 1:
            raise ValueError("box_filter adapter expects one source image")
        return _box_filter_reference(
            inputs[0], kernel_size=int(params.get("kernel_size", 3))
        )
    if canonical == "median_filter":
        if len(inputs) != 1:
            raise ValueError("median_filter adapter expects one source image")
        return _median_filter_reference(
            inputs[0], kernel_size=int(params.get("kernel_size", 3))
        )
    if canonical == "sobel":
        if len(inputs) != 1:
            raise ValueError("sobel adapter expects one source image")
        return _sobel_reference(inputs[0])
    if canonical == "laplacian":
        if len(inputs) != 1:
            raise ValueError("laplacian adapter expects one source image")
        return _laplacian_reference(inputs[0])
    if canonical == "smooth_flow":
        if len(inputs) != 1:
            raise ValueError("smooth_flow adapter expects one flow image")
        kernel_size = params.get("kernel_size")
        if kernel_size is None:
            kernel_size = int(np.ceil(3.0 * float(params.get("sigma", 1.0)))) * 2 + 1
        return _smooth_flow_reference(
            inputs[0],
            sigma=float(params.get("sigma", 1.0)),
            kernel_size=int(kernel_size),
        )
    if canonical == "highlight_recovery":
        if len(inputs) != 1:
            raise ValueError("highlight_recovery adapter expects one RGB image")
        return _highlight_recovery_reference(
            inputs[0],
            wb_r=float(params.get("wb_r", 1.0)),
            wb_g=float(params.get("wb_g", 1.0)),
            wb_b=float(params.get("wb_b", 1.0)),
            strength=float(params.get("strength", 1.0)),
        )
    if canonical == "cvtColor_extended":
        if len(inputs) != 1:
            raise ValueError("cvtColor_extended adapter expects one source image")
        return _cvt_color_extended_reference(
            inputs[0], int(params.get("code", 40))
        )
    if canonical == "morphology":
        return _morphology_reference(
            inputs[0],
            operation=str(params.get("operation", "dilate")),
            kernel=params.get("kernel"),
        )
    if canonical == "filter2d":
        return _filter2d_reference(
            inputs[0], params.get("kernel", np.ones((3, 3), dtype=np.float32))
        )
    if canonical == "threshold":
        return _threshold_reference(
            inputs[0],
            float(params.get("threshold", 127.0)),
            float(params.get("max_value", params.get("maxval", 255.0))),
            int(params.get("mode", 0)),
        )
    if canonical == "normalize":
        return _normalize_reference(
            inputs[0],
            alpha=float(params.get("alpha", 0.0)),
            beta=float(params.get("beta", 255.0)),
            mode=params.get("mode", "MINMAX"),
            src_min=params.get("src_min"),
            src_max=params.get("src_max"),
            norm_value=params.get("norm_value"),
        )
    if canonical in {"joint_bilateral_guidance", "joint_bilateral_filter"}:
        if len(inputs) != 2:
            raise ValueError(f"{canonical} expects source and guide inputs")
        radius = int(params.get("radius", 1))
        if "inv_space" in params:
            inv_space = float(params["inv_space"])
            inv_range = float(params.get("inv_range", 50.0))
        else:
            presets = {
                "high": (0.8, 0.05),
                "medium": (1.5, 0.10),
                "low": (2.5, 0.20),
            }
            sigma_space, sigma_range = presets.get(
                str(params.get("preset", "medium")).lower(), presets["medium"]
            )
            inv_space = 1.0 / (2.0 * sigma_space * sigma_space)
            inv_range = 1.0 / (2.0 * sigma_range * sigma_range)
        guide = np.asarray(inputs[1])
        if guide.ndim == 3:
            guide = _rgb2gray_reference(guide)
        return _bilateral_reference(
            inputs[0],
            guide,
            radius=radius,
            inv_space=inv_space,
            inv_range=inv_range,
        )
    if canonical == "guided_filter":
        if len(inputs) != 2:
            raise ValueError("guided_filter expects guide and source inputs")
        return _guided_filter_reference(
            inputs[0],
            inputs[1],
            radius=int(params.get("radius", 1)),
            epsilon=float(params.get("epsilon", 1.0e-4)),
        )
    if canonical == "non_local_means":
        return _non_local_means_reference(
            inputs[0],
            h_param=float(params.get("h_param", 10.0)),
            search_radius=int(params.get("search_radius", 1)),
            patch_radius=int(params.get("patch_radius", 1)),
            refinement_strength=float(params.get("refinement_strength", 1.0)),
            shrinkage_strength=float(params.get("shrinkage_strength", 1.0)),
        )
    if canonical == "enhance_image":
        if len(inputs) != 2:
            raise ValueError("enhance_image expects source and blurred inputs")
        return _enhance_grayscale_reference(
            inputs[0],
            inputs[1],
            params.get("lut"),
            float(params.get("micro_contrast", 2.93)),
            float(params.get("clarity", 0.0)),
            float(params.get("noise_coring", 0.0)),
        )
    if canonical == "ssim_aot":
        if len(inputs) != 2:
            raise ValueError("ssim_aot expects two matching image inputs")
        return _ssim_reference(
            inputs[0],
            inputs[1],
            window_size=int(params.get("window_size", 11)),
            data_range=params.get("data_range"),
            k1=float(params.get("k1", 0.01)),
            k2=float(params.get("k2", 0.03)),
        )
    if canonical == "zncc":
        if len(inputs) != 2:
            raise ValueError("zncc expects image and template inputs")
        return _ncc_reference(
            inputs[0], inputs[1], stride=int(params.get("stride", 1))
        )
    if canonical == "ncc_alignment":
        if len(inputs) != 2:
            raise ValueError("ncc_alignment expects image and template inputs")
        return _ncc_alignment_reference(
            inputs[0], inputs[1], stride=int(params.get("stride", 1))
        )
    if canonical == "mean_division":
        if len(inputs) != 3:
            raise ValueError("mean_division expects sum_img, sum_weight, and ref_img")
        return _mean_division_reference(
            inputs[0],
            inputs[1],
            inputs[2],
            epsilon=float(params.get("epsilon", 1.0e-6)),
        )
    if canonical == "normalize_accumulator":
        if len(inputs) != 2:
            raise ValueError("normalize_accumulator expects sum_img and sum_weight")
        return _normalize_accumulator_reference(
            inputs[0],
            inputs[1],
            epsilon=float(params.get("epsilon", 1.0e-6)),
        )
    if canonical in {"tone_map_srgb", "naturalTonemapping"}:
        return _natural_tonemapping_reference(
            inputs[0],
            exposure=float(params.get("exposure", 1.43)),
            shoulder=float(params.get("shoulder", 2.99)),
            gamma=float(params.get("gamma", 1.50)),
            shadow_offset=float(params.get("shadow_offset", 0.01)),
            saturation=float(params.get("saturation", 1.0)),
            texture_amount=float(params.get("texture_amount", 0.0)),
        )
    if canonical == "to_gamma_proxy":
        return _to_gamma_proxy_reference(
            inputs[0], scale=float(params.get("scale", 1.0))
        )
    if canonical == "rotate_by_flip":
        return _rotate_by_flip_reference(
            inputs[0], flip=int(params.get("flip", 0))
        )
    if canonical == "generate_hanning_window_2d":
        shape = params.get("shape")
        if shape is None:
            raise ValueError("Hanning output-domain adapter requires shape")
        return _hanning_window_reference(
            shape,
            exclude_boundary=bool(params.get("exclude_boundary", False)),
            dtype=params.get("dtype", np.float32),
        )
    if canonical == "gaussian_window_aot":
        shape = params.get("shape")
        if shape is None:
            shape = (
                int(params.get("height", 0)),
                int(params.get("width", 0)),
            )
        sigma = params.get("sigma")
        if sigma is None:
            sigma = max(int(shape[0]), int(shape[1])) / 6.0
        return _gaussian_window_reference(shape, sigma=float(sigma))
    if canonical == "build_flow_maps":
        return _flow_maps_reference(inputs, params)
    if canonical == "normalize_image":
        if len(inputs) != 1:
            raise ValueError("normalize_image adapter expects one source image")
        if "dtype" not in params:
            raise ValueError("normalize_image adapter requires dtype metadata")
        return _normalize_image_reference(inputs[0], dtype=params["dtype"])
    if canonical == "generate_brief_pattern":
        return _brief_pattern_reference(
            num_pairs=int(params.get("num_pairs", 256)),
            patch_size=int(params.get("patch_size", 31)),
            seed=int(params.get("seed", 42)),
        )
    if canonical == "resize":
        if len(inputs) != 1:
            raise ValueError("resize coordinate adapter expects one source image")
        shape = params.get("output_shape")
        if shape is None:
            dsize = params.get("dsize")
            if dsize is None or len(tuple(dsize)) != 2:
                raise ValueError("resize adapter requires dsize=(width, height)")
            shape = (int(dsize[1]), int(dsize[0]), *tuple(inputs[0].shape[2:]))
        return _resize_coordinate_compute(
            inputs[0], tuple(int(value) for value in shape), params.get("interpolation", 1)
        )
    if canonical == "image_pyramid":
        if len(inputs) != 1:
            raise ValueError("image_pyramid coordinate adapter expects one source image")
        return _image_pyramid_reference(
            inputs[0], levels=int(params.get("levels", 4))
        )
    if canonical == "warp_affine_aot":
        if len(inputs) != 1:
            raise ValueError("warp_affine coordinate adapter expects one source image")
        shape = params.get("output_shape")
        if shape is None:
            dsize = params.get("dsize")
            if dsize is None or len(tuple(dsize)) != 2:
                raise ValueError("warp_affine adapter requires dsize=(width, height)")
            shape = (int(dsize[1]), int(dsize[0]), *tuple(inputs[0].shape[2:]))
        return _warp_affine_compute(
            inputs[0], tuple(int(value) for value in shape), params
        )
    if canonical == "copy_make_border_aot":
        if len(inputs) != 1:
            raise ValueError("copy_make_border coordinate adapter expects one source image")
        shape = params.get("output_shape")
        if shape is None:
            shape = (
                int(inputs[0].shape[0]) + int(params.get("top", 0)) + int(params.get("bottom", 0)),
                int(inputs[0].shape[1]) + int(params.get("left", 0)) + int(params.get("right", 0)),
                *tuple(inputs[0].shape[2:]),
            )
        return _copy_make_border_compute(
            inputs[0], tuple(int(value) for value in shape), params
        )
    if canonical in _COORDINATE_WARP_ADAPTER_OPERATIONS:
        return _coordinate_warp_reference(canonical, inputs, params)
    if canonical in _DEMOSAIC_FULL_ADAPTER_OPERATIONS:
        return _demosaic_full_reference(canonical, inputs, params)
    function = _REFERENCE_FUNCTIONS[canonical]
    if operation in {"extract_channel"}:
        return function(inputs[0], int(params.get("channel", params.get("ch", 0))))
    if operation in {"insert_channel"}:
        return function(
            inputs[0],
            inputs[1],
            int(params.get("channel", params.get("ch", 0))),
        )
    if operation == "cvtColor":
        return function(inputs[0], int(params.get("code", 7)))
    if operation == "enhance_grayscale":
        return function(
            inputs[0],
            inputs[1],
            params.get("lut"),
            float(params.get("micro_contrast", 2.93)),
            float(params.get("clarity", 0.0)),
            float(params.get("noise_coring", 0.0)),
        )
    return function(*inputs)


def _make_reader(operation: str) -> Callable[..., PartitionContext]:
    def reader(first: Any, second: Any) -> Any:
        # GenericBlockExecutor's stable callback signature is
        # ``reader(block, arrays)``.  The standalone adapter harness uses
        # ``reader(context, block)``.  Supporting both keeps this registry
        # useful to the planner without coupling it to generic_block.py.
        if isinstance(first, BlockSpec):
            block = first
            arrays = tuple(np.asarray(value) for value in second)
            return tuple(
                np.ascontiguousarray(array[block.read_slice]) for array in arrays
            )
        context, block = first, second
        inputs = _as_inputs(context)
        params = _as_params(context)
        return PartitionContext(
            operation=operation,
            inputs=tuple(np.ascontiguousarray(array[block.read_slice]) for array in inputs),
            block=block,
            full_shape=tuple(inputs[0].shape),
            params=params,
        )

    return reader


def _rotate_reader(first: Any, second: Any) -> Any:
    """Map an output tile to its source coordinates for same-shape flips."""

    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        context = PartitionContext(operation="rotate_by_flip", inputs=arrays, block=block)
    else:
        context, block = first, second
    inputs = _as_inputs(context)
    if len(inputs) != 1:
        raise ValueError("rotate_by_flip expects one source array")
    source = inputs[0]
    flip = int(_as_params(context).get("flip", 0))
    if flip not in (0, 1, 2, 3):
        raise ValueError("rotate_by_flip semantic adapter supports only flip values 0..3")
    row_slice, col_slice = block.read_slice[:2]
    row_start, row_stop = int(row_slice.start), int(row_slice.stop)
    col_start, col_stop = int(col_slice.start), int(col_slice.stop)
    height, width = source.shape[:2]
    if flip == 0:
        mapped = (slice(row_start, row_stop), slice(col_start, col_stop))
    elif flip == 1:
        mapped = (slice(row_start, row_stop), slice(width - col_stop, width - col_start))
    else:
        mapped = (
            slice(height - row_stop, height - row_start),
            slice(width - col_stop, width - col_start),
        )
    tile = np.ascontiguousarray(source[mapped])
    return PartitionContext(
        operation="rotate_by_flip",
        inputs=(tile,),
        block=block,
        full_shape=tuple(source.shape),
        params=_as_params(context),
    )


def _rotate_runner(context: Any) -> np.ndarray:
    inputs = _as_inputs(context)
    if len(inputs) != 1:
        raise ValueError("rotate_by_flip expects one source array")
    tile = inputs[0]
    flip = int(_as_params(context).get("flip", 0))
    if flip == 0:
        return np.array(tile, copy=True, order="C")
    if flip == 1:
        return np.ascontiguousarray(np.fliplr(tile))
    if flip in (2, 3):
        return np.ascontiguousarray(np.rot90(tile, 2))
    raise ValueError("rotate_by_flip semantic adapter supports only flip values 0..3")


def _output_domain_reader(context: Any, block: BlockSpec) -> PartitionContext:
    """Preserve output-domain metadata; there is no source input window."""

    return PartitionContext(
        operation=str(_context_value(context, "operation", "")),
        inputs=(),
        block=block,
        full_shape=tuple(_context_value(context, "full_shape", ())),
        params=_as_params(context),
    )


def _output_domain_runner(context: Any) -> np.ndarray:
    operation = str(_context_value(context, "operation", ""))
    block = _context_value(context, "block")
    full_shape = tuple(int(value) for value in _context_value(context, "full_shape", ()))
    params = _as_params(context)
    if block is None or len(full_shape) != 2:
        raise ValueError("output-domain adapter requires a 2D output shape and block")
    row_slice, col_slice = block.read_slice[:2]
    row_start, row_stop = int(row_slice.start), int(row_slice.stop)
    col_start, col_stop = int(col_slice.start), int(col_slice.stop)
    rows = np.arange(row_start, row_stop, dtype=np.float32)[:, None]
    cols = np.arange(col_start, col_stop, dtype=np.float32)[None, :]
    height, width = full_shape
    if operation == "generate_hanning_window_2d":
        exclude = bool(params.get("exclude_boundary", False))
        if height > 1:
            denominator = float(height + 1 if exclude else height - 1)
            wy = 0.5 - 0.5 * np.cos(
                np.float32(2.0 * np.pi)
                * ((rows + (1.0 if exclude else 0.0)) / denominator)
            )
        else:
            wy = np.ones_like(rows, dtype=np.float32)
        if width > 1:
            denominator = float(width + 1 if exclude else width - 1)
            wx = 0.5 - 0.5 * np.cos(
                np.float32(2.0 * np.pi)
                * ((cols + (1.0 if exclude else 0.0)) / denominator)
            )
        else:
            wx = np.ones_like(cols, dtype=np.float32)
        return np.ascontiguousarray(
            np.maximum(wy, np.float32(1.0e-4))
            * np.maximum(wx, np.float32(1.0e-4)),
            dtype=np.dtype(params.get("dtype", np.float32)),
        )
    if operation == "gaussian_window_aot":
        sigma = params.get("sigma")
        if sigma is None:
            sigma = max(height, width) / 6.0
        center_y = np.float32(height / 2.0)
        center_x = np.float32(width / 2.0)
        distance = (rows - center_y) ** 2 + (cols - center_x) ** 2
        return np.ascontiguousarray(
            np.exp(-distance / np.float32(2.0 * float(sigma) ** 2)),
            dtype=np.float32,
        )
    if operation == "generate_brief_pattern":
        # The pattern is a deterministic row-domain generator.  Rebuilding
        # the full sequence and selecting the requested rows avoids changing
        # NumPy's legacy RandomState stream at tile boundaries.  It is small
        # (normally 256x4) and remains a semantic CPU adapter only.
        pattern = _brief_pattern_reference(
            num_pairs=int(params.get("num_pairs", height)),
            patch_size=int(params.get("patch_size", 31)),
            seed=int(params.get("seed", 42)),
        )
        if tuple(pattern.shape) != (height, width):
            raise ValueError(
                "generate_brief_pattern output shape must be (num_pairs, 4)"
            )
        return np.ascontiguousarray(pattern[row_start:row_stop, col_start:col_stop])
    raise ValueError(f"unknown output-domain operation: {operation}")


def _output_domain_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    if block is None:
        return False
    value = np.asarray(result)
    return tuple(value.shape[:2]) == tuple(block.read_shape) and bool(
        np.isfinite(value).all()
    )


def _output_domain_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    output[block.write_slice] = np.asarray(result)[block.core_slice]
    return output


def _coordinate_reader(first: Any, second: Any) -> Any:
    """Keep the complete source frame while switching to the output grid.

    A coordinate mapping can sample a source location outside the output tile
    (notably affine transforms with REFLECT_101 borders).  Returning the
    source by reference is therefore conservative and avoids an incorrect
    crop.  The semantic harness still bounds *computed output* and records the
    full-frame source dependency in adapter metadata; native promotion remains
    prohibited until a backend-specific source-window proof exists.
    """

    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        operation = ""
        params: Mapping[str, Any] = {}
        full_shape: tuple[int, ...] = tuple(block.read_shape)
    else:
        context, block = first, second
        arrays = _as_inputs(context)
        operation = str(_context_value(context, "operation", ""))
        params = _as_params(context)
        full_shape = tuple(
            int(value)
            for value in (_context_value(context, "output_shape", None) or _context_value(context, "full_shape", ()))
        )
    return PartitionContext(
        operation=operation,
        inputs=tuple(np.ascontiguousarray(value) for value in arrays),
        block=block,
        full_shape=full_shape,
        output_shape=full_shape,
        params=params,
        stage=int(params.get("stage", 0)) if isinstance(params, Mapping) else 0,
    )


def _coordinate_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    inputs = _as_inputs(context)
    params = _as_params(context)
    block = _context_value(context, "block")
    output_shape = tuple(
        int(value)
        for value in (
            _context_value(context, "output_shape", None)
            or params.get("output_shape", None)
            or _context_value(context, "full_shape", ())
        )
    )
    if operation == "resize":
        return _resize_coordinate_compute(inputs[0], output_shape, params.get("interpolation", 1), block)
    if operation == "image_pyramid":
        return _pyramid_downsample_compute(inputs[0], block)
    if operation == "warp_affine_aot":
        return _warp_affine_compute(inputs[0], output_shape, params, block)
    if operation == "copy_make_border_aot":
        return _copy_make_border_compute(inputs[0], output_shape, params, block)
    raise ValueError(f"unknown coordinate-domain operation: {operation}")


def _coordinate_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    if block is None:
        return False
    value = np.asarray(result)
    expected = tuple(block.shape)
    if tuple(value.shape[:2]) != expected:
        return False
    return bool(np.isfinite(value).all())


def _coordinate_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    value = np.asarray(result)
    output[block.write_slice] = value
    return output


def _coordinate_output_shape(operation: str, source: np.ndarray, params: Mapping[str, Any]) -> tuple[int, ...]:
    operation = canonical_operation_name(operation)
    trailing = tuple(int(value) for value in np.asarray(source).shape[2:])
    shape = params.get("output_shape")
    if shape is not None:
        values = tuple(int(value) for value in shape)
        if len(values) < 2:
            raise ValueError("output_shape must contain height and width")
        return values
    if operation in {"resize", "warp_affine_aot"}:
        dsize = params.get("dsize")
        if dsize is None or len(tuple(dsize)) != 2:
            raise ValueError(f"{operation} requires dsize=(width, height)")
        width, height = int(dsize[0]), int(dsize[1])
        if width <= 0 or height <= 0:
            raise ValueError("coordinate output dimensions must be positive")
        return (height, width, *trailing)
    if operation == "copy_make_border_aot":
        top, bottom = int(params.get("top", 0)), int(params.get("bottom", 0))
        left, right = int(params.get("left", 0)), int(params.get("right", 0))
        if min(top, bottom, left, right) < 0:
            raise ValueError("border sizes must be non-negative")
        return (int(source.shape[0]) + top + bottom, int(source.shape[1]) + left + right, *trailing)
    raise ValueError(f"{operation} requires an explicit output shape")


def _coordinate_warp_source(value: Any, operation: str) -> np.ndarray:
    """Validate an image source used by a semantic coordinate warp."""

    source = np.asarray(value)
    if source.ndim not in (2, 3) or source.shape[0] <= 0 or source.shape[1] <= 0:
        raise ValueError(f"{operation} source must be a non-empty 2D or HxWxC image")
    if source.ndim == 3 and source.shape[2] <= 0:
        raise ValueError(f"{operation} source must have at least one channel")
    if not np.issubdtype(source.dtype, np.number):
        raise TypeError(f"{operation} source must be numeric")
    result = np.ascontiguousarray(source, dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError(f"{operation} source must contain finite values")
    return result


def _bilinear_coordinate_sample(source: np.ndarray, x: float, y: float) -> Any:
    """Bilinear sample with the exact REFLECT_101 index convention of AOT."""

    height, width = int(source.shape[0]), int(source.shape[1])
    if height <= 0 or width <= 0:
        raise ValueError("coordinate source dimensions must be positive")
    ix, iy = int(np.floor(float(x))), int(np.floor(float(y)))
    fx, fy = np.float32(float(x) - ix), np.float32(float(y) - iy)
    x0, x1 = _reflect101_index(ix, width), _reflect101_index(ix + 1, width)
    y0, y1 = _reflect101_index(iy, height), _reflect101_index(iy + 1, height)
    top = source[y0, x0] * (np.float32(1.0) - fx) + source[y0, x1] * fx
    bottom = source[y1, x0] * (np.float32(1.0) - fx) + source[y1, x1] * fx
    return np.asarray(
        top * (np.float32(1.0) - fy) + bottom * fy,
        dtype=np.float32,
    )


def _remap_compute(
    source_input: Any,
    map_x_input: Any,
    map_y_input: Any,
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    """Compute one remap output region using the maintained bilinear rule."""

    source = _coordinate_warp_source(source_input, "remap")
    map_x = np.asarray(map_x_input, dtype=np.float32)
    map_y = np.asarray(map_y_input, dtype=np.float32)
    if map_x.ndim != 2 or map_x.shape != map_y.shape or map_x.size == 0:
        raise ValueError("remap maps must be matching non-empty 2D arrays")
    if not np.isfinite(map_x).all() or not np.isfinite(map_y).all():
        raise ValueError("remap maps must contain finite coordinates")
    height, width = map_x.shape
    if block is None:
        y0, y1, x0, x1 = 0, int(height), 0, int(width)
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in source.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    for row in range(y0, y1):
        for col in range(x0, x1):
            output[row - y0, col - x0] = _bilinear_coordinate_sample(
                source, float(map_x[row, col]), float(map_y[row, col])
            )
    return np.ascontiguousarray(output, dtype=np.float32)


def _coordinate_warp_shape(
    operation: str, inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> tuple[int, ...]:
    """Resolve a warp's destination shape without assuming source == output."""

    canonical = canonical_operation_name(operation)
    if canonical == "remap":
        if len(inputs) != 3:
            raise ValueError("remap expects source, map_x, and map_y inputs")
        source = _coordinate_warp_source(inputs[0], canonical)
        map_x = np.asarray(inputs[1])
        map_y = np.asarray(inputs[2])
        if map_x.ndim != 2 or map_x.shape != map_y.shape or map_x.size == 0:
            raise ValueError("remap maps must be matching non-empty 2D arrays")
        return (int(map_x.shape[0]), int(map_x.shape[1]), *source.shape[2:])
    if canonical == "remap_with_flow":
        if len(inputs) != 2:
            raise ValueError("remap_with_flow expects source and HxWx2 flow inputs")
        source = _coordinate_warp_source(inputs[0], canonical)
        flow = np.asarray(inputs[1])
        if flow.ndim != 3 or flow.shape[2] != 2 or flow.shape[0] <= 0 or flow.shape[1] <= 0:
            raise ValueError("remap_with_flow flow must be a non-empty HxWx2 array")
        shape = params.get("output_shape")
        if shape is None:
            shape = (params.get("full_h"), params.get("full_w"))
        if shape is None or len(tuple(shape)) < 2:
            raise ValueError("remap_with_flow requires full_h/full_w or output_shape")
        height, width = int(tuple(shape)[0]), int(tuple(shape)[1])
        if height <= 1 or width <= 1:
            raise ValueError("remap_with_flow destination dimensions must exceed one")
        return (height, width, *source.shape[2:])
    if canonical == "warp_perspective":
        if len(inputs) != 1:
            raise ValueError("warp_perspective expects one source image")
        source = _coordinate_warp_source(inputs[0], canonical)
        shape = params.get("output_shape")
        if shape is None:
            dsize = params.get("dsize")
            if dsize is None or len(tuple(dsize)) != 2:
                raise ValueError("warp_perspective requires dsize=(width, height)")
            shape = (int(tuple(dsize)[1]), int(tuple(dsize)[0]))
        values = tuple(int(value) for value in shape)
        if len(values) < 2 or values[0] <= 0 or values[1] <= 0:
            raise ValueError("warp_perspective output shape must be positive")
        return (values[0], values[1], *source.shape[2:])
    raise ValueError(f"unknown coordinate warp: {operation}")


def _remap_with_flow_compute(
    source_input: Any,
    flow_input: Any,
    output_shape: tuple[int, ...],
    params: Mapping[str, Any],
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    """Compute fused flow remap using the exact output/flow coordinate map."""

    source = _coordinate_warp_source(source_input, "remap_with_flow")
    flow = np.asarray(flow_input, dtype=np.float32)
    if flow.ndim != 3 or flow.shape[2] != 2 or flow.size == 0:
        raise ValueError("remap_with_flow flow must be a non-empty HxWx2 array")
    if not np.isfinite(flow).all():
        raise ValueError("remap_with_flow flow must contain finite values")
    height, width = int(output_shape[0]), int(output_shape[1])
    h_flow, w_flow = int(flow.shape[0]), int(flow.shape[1])
    if height <= 1 or width <= 1:
        raise ValueError("remap_with_flow destination dimensions must exceed one")
    scale_x = np.float32(params.get("scale_x", float(width) / float(w_flow)))
    scale_y = np.float32(params.get("scale_y", float(height) / float(h_flow)))
    if not np.isfinite(scale_x) or not np.isfinite(scale_y):
        raise ValueError("remap_with_flow scales must be finite")
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in source.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    for row in range(y0, y1):
        fy = np.float32(row * (h_flow - 1) / float(height - 1))
        for col in range(x0, x1):
            fx = np.float32(col * (w_flow - 1) / float(width - 1))
            displacement = _bilinear_coordinate_sample(flow, float(fx), float(fy))
            src_x = np.float32(col) + np.float32(displacement[0]) * scale_x
            src_y = np.float32(row) + np.float32(displacement[1]) * scale_y
            output[row - y0, col - x0] = _bilinear_coordinate_sample(
                source, float(src_x), float(src_y)
            )
    return np.ascontiguousarray(output, dtype=np.float32)


def _warp_perspective_matrix(params: Mapping[str, Any]) -> np.ndarray:
    matrix = np.asarray(params.get("matrix"), dtype=np.float32)
    if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
        raise ValueError("warp_perspective requires a finite 3x3 matrix")
    try:
        inverse = np.linalg.inv(matrix).astype(np.float32)
    except np.linalg.LinAlgError as exc:
        raise ValueError("warp_perspective matrix must be invertible") from exc
    return np.ascontiguousarray(inverse, dtype=np.float32)


def _warp_perspective_compute(
    source_input: Any,
    output_shape: tuple[int, ...],
    params: Mapping[str, Any],
    block: Optional[BlockSpec] = None,
) -> np.ndarray:
    source = _coordinate_warp_source(source_input, "warp_perspective")
    inverse = _warp_perspective_matrix(params)
    height, width = int(output_shape[0]), int(output_shape[1])
    if block is None:
        y0, y1, x0, x1 = 0, height, 0, width
    else:
        y0, y1, x0, x1 = int(block.y0), int(block.y1), int(block.x0), int(block.x1)
    trailing = tuple(int(value) for value in source.shape[2:])
    output = np.empty((y1 - y0, x1 - x0, *trailing), dtype=np.float32)
    for row in range(y0, y1):
        for col in range(x0, x1):
            u = float(inverse[0, 0]) * col + float(inverse[0, 1]) * row + float(inverse[0, 2])
            v = float(inverse[1, 0]) * col + float(inverse[1, 1]) * row + float(inverse[1, 2])
            denominator = float(inverse[2, 0]) * col + float(inverse[2, 1]) * row + float(inverse[2, 2])
            denominator += 1.0e-9
            output[row - y0, col - x0] = _bilinear_coordinate_sample(
                source, u / denominator, v / denominator
            )
    return np.ascontiguousarray(output, dtype=np.float32)


def _coordinate_warp_reference(
    operation: str, inputs: Sequence[np.ndarray], params: Mapping[str, Any]
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    shape = _coordinate_warp_shape(canonical, inputs, params)
    if canonical == "remap":
        return _remap_compute(inputs[0], inputs[1], inputs[2])
    if canonical == "remap_with_flow":
        return _remap_with_flow_compute(inputs[0], inputs[1], shape, params)
    if canonical == "warp_perspective":
        return _warp_perspective_compute(inputs[0], shape, params)
    raise ValueError(f"unknown coordinate warp: {operation}")


def _coordinate_warp_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    inputs = _as_inputs(context)
    params = _as_params(context)
    block = _context_value(context, "block")
    shape = tuple(int(value) for value in (_context_value(context, "output_shape", ()) or ()))
    if len(shape) < 2:
        shape = _coordinate_warp_shape(operation, inputs, params)
    if operation == "remap":
        return _remap_compute(inputs[0], inputs[1], inputs[2], block)
    if operation == "remap_with_flow":
        return _remap_with_flow_compute(inputs[0], inputs[1], shape, params, block)
    if operation == "warp_perspective":
        return _warp_perspective_compute(inputs[0], shape, params, block)
    raise ValueError(f"unknown coordinate warp: {operation}")


def _run_coordinate_warp_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    shape = _coordinate_warp_shape(canonical, arrays, values)
    values["output_shape"] = shape
    output = np.empty(shape, dtype=np.float32)
    grid = BlockGrid(shape[:2], size=block_size, halo=0)
    for block in grid:
        context = PartitionContext(
            operation=canonical,
            inputs=arrays,
            block=block,
            full_shape=shape,
            output_shape=shape,
            params=values,
        )
        tile_context = _coordinate_reader(context, block)
        result = _coordinate_warp_runner(tile_context)
        if not _coordinate_validator(tile_context, result):
            raise ValueError(f"{canonical} tile {block.index} failed validation")
        _coordinate_merger(output, result, block)
    return np.ascontiguousarray(output, dtype=np.float32)


def verify_coordinate_warp_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _coordinate_warp_reference(canonical, arrays, values)
    tiled = _run_coordinate_warp_tiled(
        canonical, arrays, block_size=block_size, params=values
    )
    left, right = np.asarray(full), np.asarray(tiled)
    error = float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64)))) if left.size else 0.0
    return {
        "operation": canonical,
        "scope": "semantic_numpy_coordinate_warp",
        "backend": "cpu",
        "input_shapes": [list(value.shape) for value in arrays],
        "output_shape": list(left.shape),
        "block_size": (
            BlockGrid(left.shape[:2], size=block_size).block_height,
            BlockGrid(left.shape[:2], size=block_size).block_width,
        ),
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "native_runtime": False,
    }


# Public semantic-harness alias.  The leading underscore implementation is
# retained for adapter metadata/callbacks, while callers get a stable helper
# analogous to ``run_coordinate_tiled`` and ``run_demosaic_half_tiled``.
run_coordinate_warp_tiled = _run_coordinate_warp_tiled


def run_coordinate_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    output_shape: Optional[Sequence[int]] = None,
    params: Optional[Mapping[str, Any]] = None,
    block_size: int | tuple[int, int] = 32,
) -> Any:
    """Run one explicit coordinate-domain adapter over an output grid.

    This helper is intentionally separate from ``run_adapter_tiled`` because
    shape-changing operations need an output-domain grid and custom merge.
    It is a semantic CPU harness; callers must still use the established
    same-backend full-frame path unless a target-qualified native probe is
    available.
    """

    canonical = canonical_operation_name(operation)
    if canonical in _COORDINATE_WARP_ADAPTER_OPERATIONS:
        # Warp inputs have distinct coordinate domains (source/map/flow), so
        # route them through the dedicated multi-input harness rather than
        # the historical single-source shape-changing helper.
        return _run_coordinate_warp_tiled(
            canonical,
            inputs,
            block_size=block_size,
            params=params,
        )
    adapter = lookup_block_adapter(canonical)
    if adapter is None or not adapter.partition_ready or not adapter.metadata.get("coordinate_domain"):
        raise ValueError(f"no complete coordinate-domain adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 1 or arrays[0].ndim not in (2, 3):
        raise ValueError(f"{canonical} expects one 2D or 3D source image")
    values = dict(params or {})
    if output_shape is not None:
        values["output_shape"] = tuple(int(value) for value in output_shape)

    if canonical == "image_pyramid":
        current = arrays[0].astype(np.float32, copy=False)
        levels = int(values.get("levels", 4))
        if levels < 0:
            raise ValueError("image_pyramid levels must be non-negative")
        for stage in range(levels):
            if current.shape[0] // 2 < 1 or current.shape[1] // 2 < 1:
                break
            shape = (current.shape[0] // 2, current.shape[1] // 2, *current.shape[2:])
            grid = BlockGrid(shape, size=block_size)
            output = np.empty(shape, dtype=np.float32)
            stage_params = {**values, "output_shape": shape, "stage": stage}
            for block in grid:
                context = PartitionContext(
                    canonical, (current,), block, shape, stage_params, shape, stage
                )
                tile_context = adapter.reader(context, block) if adapter.reader else context
                tile = adapter.runner(tile_context)
                if not adapter.validator(tile_context, tile):
                    raise ValueError(f"{canonical} tile {block.index} failed validation")
                adapter.merger(output, tile, block)
            current = output
        return np.ascontiguousarray(current, dtype=np.float32)

    shape = _coordinate_output_shape(canonical, arrays[0], values)
    values["output_shape"] = shape
    grid = BlockGrid(shape, size=block_size)
    output = np.empty(shape, dtype=np.float32)
    for block in grid:
        context = PartitionContext(canonical, arrays, block, shape, values, shape, 0)
        tile_context = adapter.reader(context, block) if adapter.reader else context
        tile = adapter.runner(tile_context)
        if not adapter.validator(tile_context, tile):
            raise ValueError(f"{canonical} tile {block.index} failed validation")
        adapter.merger(output, tile, block)
    return np.ascontiguousarray(output, dtype=np.float32)


def verify_coordinate_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    output_shape: Optional[Sequence[int]] = None,
    params: Optional[Mapping[str, Any]] = None,
    block_size: int | tuple[int, int] = 32,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare coordinate full-frame and output-tiled semantic results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    if output_shape is not None:
        values["output_shape"] = tuple(int(value) for value in output_shape)
    full = _reference(canonical, arrays, values)
    tiled = run_coordinate_tiled(
        canonical, arrays, output_shape=output_shape, params=values, block_size=block_size
    )
    full_values = full if isinstance(full, (tuple, list)) else (full,)
    tiled_values = tiled if isinstance(tiled, (tuple, list)) else (tiled,)
    errors = []
    passed = len(full_values) == len(tiled_values)
    dtype_match = len(full_values) == len(tiled_values)
    for left, right in zip(full_values, tiled_values):
        left_array, right_array = np.asarray(left), np.asarray(right)
        if left_array.shape != right_array.shape:
            passed = False
            errors.append(float("inf"))
            continue
        # Value-only ``allclose`` is insufficient for a partition contract:
        # a tile path that silently widens/narrows the output can appear
        # numerically equal while changing downstream memory/ABI semantics.
        # Keep this strict for coordinate-domain adapters, whose full and
        # tiled paths must expose the same dtype as well as the same values.
        if left_array.dtype != right_array.dtype:
            dtype_match = False
            passed = False
        error = float(np.max(np.abs(left_array.astype(np.float64) - right_array.astype(np.float64)))) if left_array.size else 0.0
        errors.append(error)
        passed = bool(passed and np.allclose(left_array, right_array, rtol=float(rtol), atol=float(atol), equal_nan=True))
    return {
        "operation": canonical,
        "scope": "semantic_numpy_coordinate_domain",
        "backend": "cpu",
        "block_size": (
            BlockGrid(np.asarray(tiled_values[0]).shape, size=block_size).block_height,
            BlockGrid(np.asarray(tiled_values[0]).shape, size=block_size).block_width,
        ) if tiled_values else (),
        "full_shape": [list(np.asarray(value).shape) for value in full_values],
        "tiled_shape": [list(np.asarray(value).shape) for value in tiled_values],
        "full_dtype": [np.asarray(value).dtype.name for value in full_values],
        "tiled_dtype": [np.asarray(value).dtype.name for value in tiled_values],
        "dtype_match": bool(dtype_match),
        "passed": bool(passed),
        "max_abs_error": max(errors, default=0.0),
        "native_runtime": False,
    }


def _flow_map_reader(first: Any, second: Any) -> PartitionContext:
    """Keep the full flow source while partitioning the destination grid."""

    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        params: Mapping[str, Any] = {}
        operation = "build_flow_maps"
    else:
        context, block = first, second
        arrays = _as_inputs(context)
        params = _as_params(context)
        operation = canonical_operation_name(
            str(_context_value(context, "operation", "build_flow_maps"))
        )
    _, _, h_dst, w_dst, _, _ = _flow_map_inputs(arrays, params)
    return PartitionContext(
        operation=operation,
        inputs=tuple(np.ascontiguousarray(value) for value in arrays),
        block=block,
        full_shape=(h_dst, w_dst),
        output_shape=(h_dst, w_dst),
        params=params,
    )


def _flow_map_runner(context: Any) -> tuple[np.ndarray, np.ndarray]:
    arrays = _as_inputs(context)
    block = _context_value(context, "block")
    if block is None:
        raise ValueError("build_flow_maps tile runner requires a destination block")
    params = _as_params(context)
    dx, dy, h_dst, w_dst, scale_x, scale_y = _flow_map_inputs(arrays, params)
    return _flow_map_compute_region(
        dx,
        dy,
        h_dst,
        w_dst,
        scale_x,
        scale_y,
        int(block.y0),
        int(block.y1),
        int(block.x0),
        int(block.x1),
    )


def _flow_map_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    if block is None or not isinstance(result, (tuple, list)) or len(result) != 2:
        return False
    return all(
        tuple(np.asarray(value).shape) == tuple(block.shape)
        and np.asarray(value).dtype == np.dtype(np.float32)
        and bool(np.isfinite(np.asarray(value)).all())
        for value in result
    )


def _flow_map_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    if not isinstance(output, (tuple, list)) or len(output) != 2:
        raise ValueError("build_flow_maps output must contain map_x and map_y")
    values = tuple(result) if isinstance(result, (tuple, list)) else ()
    if len(values) != 2:
        raise ValueError("build_flow_maps tile must contain map_x and map_y")
    output[0][block.write_slice] = np.asarray(values[0])
    output[1][block.write_slice] = np.asarray(values[1])
    return output


def _run_flow_maps_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> tuple[np.ndarray, np.ndarray]:
    del operation  # canonical operation is fixed by this adapter.
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    dx, dy, h_dst, w_dst, scale_x, scale_y = _flow_map_inputs(arrays, values)
    output = (
        np.empty((h_dst, w_dst), dtype=np.float32),
        np.empty((h_dst, w_dst), dtype=np.float32),
    )
    grid = BlockGrid((h_dst, w_dst), size=block_size, halo=0)
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
    if tuple(int(item.index) for item in blocks) != tuple(range(len(blocks))):
        raise ValueError("build_flow_maps block order is not deterministic")
    for block in blocks:
        context = PartitionContext(
            operation="build_flow_maps",
            inputs=arrays,
            block=block,
            full_shape=(h_dst, w_dst),
            output_shape=(h_dst, w_dst),
            params=values,
        )
        tile_context = _flow_map_reader(context, block)
        result = _flow_map_runner(tile_context)
        if not _flow_map_validator(tile_context, result):
            raise ValueError(f"build_flow_maps tile {block.index} failed validation")
        _flow_map_merger(output, result, block)
    # Keep local variables referenced for debuggers and make it explicit that
    # all tiles use one validated source/scale contract.
    del dx, dy, scale_x, scale_y
    return tuple(np.ascontiguousarray(value, dtype=np.float32) for value in output)


def verify_flow_maps_parity(
    operation_or_inputs: str | Sequence[np.ndarray],
    inputs: Optional[Sequence[np.ndarray]] = None,
    *,
    output_shape: Optional[Sequence[int]] = None,
    params: Optional[Mapping[str, Any]] = None,
    block_size: int | tuple[int, int] = 32,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare deterministic CPU flow-map output-domain tiles with full-frame."""

    if isinstance(operation_or_inputs, str):
        if canonical_operation_name(operation_or_inputs) != "build_flow_maps":
            raise ValueError("flow-map parity runner only supports build_flow_maps")
        if inputs is None:
            raise ValueError("build_flow_maps parity requires input arrays")
        arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    else:
        if inputs is not None:
            raise TypeError("flow-map inputs were supplied twice")
        arrays = tuple(np.ascontiguousarray(value) for value in operation_or_inputs)
    values = dict(params or {})
    if output_shape is not None:
        values["output_shape"] = tuple(int(value) for value in output_shape)
    full = _flow_maps_reference(arrays, values)
    tiled = _run_flow_maps_tiled(
        "build_flow_maps", arrays, block_size=block_size, params=values
    )
    errors = [
        float(
            np.max(
                np.abs(
                    np.asarray(left, dtype=np.float64)
                    - np.asarray(right, dtype=np.float64)
                )
            )
        )
        if np.asarray(left).size
        else 0.0
        for left, right in zip(full, tiled)
    ]
    return {
        "operation": "build_flow_maps",
        "scope": "deterministic_numpy_flow_map_output_domain",
        "backend": "cpu",
        "input_shapes": [list(value.shape) for value in arrays],
        "output_shape": list(np.asarray(full[0]).shape),
        "block_size": (
            BlockGrid(np.asarray(full[0]).shape, size=block_size).block_height,
            BlockGrid(np.asarray(full[0]).shape, size=block_size).block_width,
        ),
        "passed": bool(
            all(
                np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)
                for left, right in zip(full, tiled)
            )
        ),
        "max_abs_error": max(errors, default=0.0),
        "native_runtime": False,
    }


def _normalize_image_reader(first: Any, second: Any) -> PartitionContext:
    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        params: Mapping[str, Any] = {}
    else:
        context, block = first, second
        arrays = _as_inputs(context)
        params = _as_params(context)
    if len(arrays) != 1:
        raise ValueError("normalize_image expects one source image")
    return PartitionContext(
        operation="normalize_image",
        inputs=(np.ascontiguousarray(arrays[0]),),
        block=block,
        full_shape=tuple(arrays[0].shape),
        output_shape=tuple(arrays[0].shape),
        params=params,
    )


def _normalize_image_runner(context: Any) -> np.ndarray:
    arrays = _as_inputs(context)
    if len(arrays) != 1:
        raise ValueError("normalize_image expects one source image")
    params = _as_params(context)
    if "dtype" not in params:
        raise ValueError("normalize_image adapter requires dtype metadata")
    return _normalize_image_reference(arrays[0], dtype=params["dtype"])


def _normalize_image_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    inputs = _as_inputs(context)
    if block is None or len(inputs) != 1:
        return False
    expected = tuple(block.shape)
    if inputs[0].ndim == 2:
        expected += (3,)
    else:
        expected += tuple(inputs[0].shape[2:])
    value = np.asarray(result)
    return (
        tuple(value.shape) == expected
        and value.dtype == np.dtype(np.float32)
        and bool(np.isfinite(value).all())
    )


def _normalize_image_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    output[block.write_slice] = np.asarray(result)
    return output


def _run_normalize_image_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    del operation
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 1 or arrays[0].ndim not in (2, 3):
        raise ValueError("normalize_image expects one 2D or 3D source image")
    values = dict(params or {})
    reference = _normalize_image_reference(arrays[0], dtype=values.get("dtype"))
    output = np.empty_like(reference)
    grid = BlockGrid(arrays[0].shape, size=block_size, halo=0)
    for block in grid:
        tile_context = PartitionContext(
            operation="normalize_image",
            inputs=(np.ascontiguousarray(arrays[0][block.read_slice]),),
            block=block,
            full_shape=tuple(arrays[0].shape),
            output_shape=tuple(reference.shape),
            params=values,
        )
        result = _normalize_image_runner(tile_context)
        if not _normalize_image_validator(tile_context, result):
            raise ValueError(f"normalize_image tile {block.index} failed validation")
        _normalize_image_merger(output, result, block)
    return np.ascontiguousarray(output, dtype=np.float32)


def verify_normalize_image_parity(
    source_or_operation: str | np.ndarray,
    source: Optional[Sequence[np.ndarray] | np.ndarray] = None,
    *,
    dtype: Any = None,
    block_size: int | tuple[int, int] = 32,
    rtol: float = 0.0,
    atol: float = 0.0,
    params: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    if isinstance(source_or_operation, str):
        if canonical_operation_name(source_or_operation) != "normalize_image":
            raise ValueError("normalization parity runner only supports normalize_image")
        if source is None:
            raise ValueError("normalize_image parity requires one source array")
        if isinstance(source, (tuple, list)):
            if len(source) != 1:
                raise ValueError("normalize_image parity expects one input array")
            source = source[0]
        if dtype is None:
            dtype = (params or {}).get("dtype")
    else:
        if source is not None:
            raise TypeError("normalize_image source was supplied twice")
        source = source_or_operation
    if dtype is None:
        raise ValueError("normalize_image parity requires dtype metadata")
    values = {"dtype": dtype}
    source_array = np.ascontiguousarray(np.asarray(source))
    full = _normalize_image_reference(source_array, dtype=dtype)
    tiled = _run_normalize_image_tiled(
        "normalize_image", (source_array,), block_size=block_size, params=values
    )
    error = (
        float(np.max(np.abs(full.astype(np.float64) - tiled.astype(np.float64))))
        if full.size
        else 0.0
    )
    return {
        "operation": "normalize_image",
        "scope": "deterministic_numpy_normalize_image_spatial_tiles",
        "backend": "cpu",
        "input_shape": list(source_array.shape),
        "output_shape": list(full.shape),
        "dtype_metadata": str(np.dtype(dtype)),
        "block_size": (
            BlockGrid(source_array.shape, size=block_size).block_height,
            BlockGrid(source_array.shape, size=block_size).block_width,
        ),
        "passed": bool(np.allclose(full, tiled, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "native_runtime": False,
    }


def _make_runner(operation: str) -> Callable[..., Any]:
    def runner(context: Any) -> Any:
        return _reference(operation, _as_inputs(context), _as_params(context))

    return runner


def _expected_shape_for_result(result: Any, block: Optional[BlockSpec]) -> bool:
    if block is None:
        return True
    expected = tuple(block.read_shape)
    values = result if isinstance(result, (tuple, list)) else (result,)
    for value in values:
        array = np.asarray(value)
        if tuple(array.shape[:2]) != expected:
            return False
        if not np.isfinite(array).all() and np.issubdtype(array.dtype, np.floating):
            return False
    return True


def _make_validator(operation: str) -> Callable[..., bool]:
    def validator(first: Any, second: Any) -> bool:
        # GenericBlockExecutor calls ``validator(payload, context)`` while
        # the standalone adapter harness calls ``validator(context, payload)``.
        if _context_value(second, "block") is not None:
            result, context = first, second
        else:
            context, result = first, second
        if not _expected_shape_for_result(result, _context_value(context, "block")):
            return False
        expected = _context_value(context, "expected")
        if expected is None:
            return True
        values = result if isinstance(result, (tuple, list)) else (result,)
        refs = expected if isinstance(expected, (tuple, list)) else (expected,)
        if len(values) != len(refs):
            return False
        return all(np.array_equal(np.asarray(a), np.asarray(b)) for a, b in zip(values, refs))

    return validator


def _make_merger(operation: str) -> Callable[..., Any]:
    def merger(output: Any, result: Any, context_or_block: Any) -> Any:
        block = (
            context_or_block.block
            if not isinstance(context_or_block, BlockSpec)
            and _context_value(context_or_block, "block") is not None
            else context_or_block
        )
        results = result if isinstance(result, (tuple, list)) else (result,)
        outputs = output if isinstance(output, (tuple, list)) else (output,)
        if len(results) != len(outputs):
            raise ValueError(f"{operation} result/output arity mismatch")
        for destination, value in zip(outputs, results):
            destination[block.write_slice] = np.asarray(value)[block.core_slice]
        return output

    return merger


def _qualified_contract(
    operation: str,
    *,
    halo: Optional[int] = None,
    partition_strategy: Optional[PartitionStrategy] = None,
) -> OperationContract:
    """Create an adapter-local CPU contract without promoting strict flags."""

    base = operation_contract(operation)
    effective_halo = base.halo if halo is None else int(halo)
    if effective_halo < 0:
        raise ValueError("adapter halo must be non-negative")
    return OperationContract(
        operation=operation,
        shape_transform=base.shape_transform,
        input_coordinate_map=base.input_coordinate_map,
        halo=effective_halo,
        halo_policy=(HaloPolicy.FIXED if effective_halo else HaloPolicy.NONE),
        border_policy=(BorderPolicy.CLAMP if effective_halo else BorderPolicy.NONE),
        reduction=base.reduction,
        merge=base.merge,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=base.scratch_bytes,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        # Keep the legacy strict gate unchanged.  This adapter qualifies the
        # richer partition contract only; the planner can promote it later.
        automatic_safe=False,
        parity_qualified=False,
        known=base.known,
        reason="deterministic full-frame/tile semantic parity on CPU only",
        partition_strategy=partition_strategy
        or base.partition_strategy
        or PartitionStrategy.LOCAL,
        partition_qualified=True,
    )


def register_low_risk_block_adapters(*, replace: bool = False) -> Mapping[str, BlockAdapter]:
    """Register deterministic CPU-only adapters for local legacy executors.

    Registration is idempotent by default.  It never changes the operation
    capability table, strict ``AUTO_BLOCK_SAFE`` flags, or any GPU backend
    qualification.  The returned mapping is a snapshot of the adapters that
    were present after registration.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _ADAPTER_OPERATIONS:
        evidence = legacy_partition_evidence(operation)
        if evidence is None:
            # Keep the registry honest: an adapter without a maintained tile
            # executor is not eligible for the legacy dispatch gate.
            continue
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        contract = _qualified_contract(operation)
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "legacy_executor": evidence["executor"],
            "legacy_partition_evidence": {
                "operation": operation,
                "executor": evidence["executor"],
                "parity_evidence": {"cpu": True},
            },
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_semantics",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _REFERENCE_FUNCTIONS[operation],
            "parity_runner": verify_adapter_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_make_reader(operation),
            runner=_make_runner(operation),
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=contract.partition_strategy,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_local_stencil_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register bounded CPU semantic adapters for existing local executors.

    The selected wrappers already route NumPy inputs through the maintained
    same-backend ``_run_blockwise`` path.  This registration supplies explicit
    halo/shape metadata and a deterministic CPU oracle for the planner and
    parity harness.  It deliberately leaves ``AUTO_BLOCK_SAFE`` and native
    backend capability untouched; native dispatch still requires an exact
    command-backed evidence record.

    Dynamic variants are constrained by the runner/reference functions:
    morphology/filter2d/bilateral/guided use a 3x3/radius-1 contract and NLM
    uses the (search_window=3, patch_size=1) graph.  Callers requesting larger
    neighborhoods remain on the original full-frame/fallback path.
    """

    registered: dict[str, BlockAdapter] = {}
    halo_overrides = {
        "non_local_means": 2,  # search radius 1 + patch radius 1
        # The output averages ``a``/``b`` after their own radius-one means;
        # effective dependency radius is therefore two, matching the public
        # wrapper's ``halo=2*radius`` call.
        "guided_filter": 2,
        "joint_bilateral_filter": 1,
        "joint_bilateral_guidance": 1,
        "morphology": 1,
        "filter2d": 1,
    }
    strategies = {
        operation: (
            PartitionStrategy.STENCIL
            if operation in halo_overrides
            else PartitionStrategy.LOCAL
        )
        for operation in _LOCAL_STENCIL_ADAPTER_OPERATIONS
    }
    for operation in _LOCAL_STENCIL_ADAPTER_OPERATIONS:
        evidence = legacy_partition_evidence(operation)
        if evidence is None:
            # This protects the registry from claiming a tile path if a public
            # wrapper is later refactored away from _run_blockwise.
            continue
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        contract = _qualified_contract(
            operation,
            halo=halo_overrides.get(operation),
            partition_strategy=strategies[operation],
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": (
                "stencil" if operation in halo_overrides else "local"
            ),
            "semantic_only": True,
            "parameter_scope": {
                "morphology": "3x3 dilate/erode",
                "filter2d": "3x3 reflect-101",
                "threshold": "fixed threshold and mode",
                "normalize": "precomputed full-frame statistics",
                "joint_bilateral_guidance": "radius=1",
                "enhance_image": "pointwise LUT transform",
                "joint_bilateral_filter": "radius=1",
                "guided_filter": "radius=1",
                "non_local_means": "search_window=3, patch_size=1",
            }[operation],
            "legacy_executor": evidence["executor"],
            "legacy_partition_evidence": {
                "operation": operation,
                "executor": evidence["executor"],
                "parity_evidence": {"cpu": True},
            },
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_local_stencil",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_adapter_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_make_reader(operation),
            runner=_make_runner(operation),
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=contract.partition_strategy,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_legacy_local_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register the bounded semantic contract for legacy AOT local kernels.

    This tranche covers Gaussian/box/median filters, gradients, flow
    smoothing, highlight recovery, extended colour conversion, and the
    ``copy_field`` compatibility alias.  All callbacks are deterministic CPU
    oracles.  Registration deliberately leaves strict automatic flags and
    native backend evidence untouched; a graphics target still needs a
    device-scoped full-vs-block probe before dispatch can be promoted.

    The callbacks reject unsupported graph variants (for example a median
    kernel other than 3x3, a Gaussian radius above the compiled static bound,
    or a malformed flow/RGB shape).  Such calls remain on the established
    same-backend full-frame path.
    """

    registered: dict[str, BlockAdapter] = {}
    halo_overrides = {
        "gaussian_blur": 16,
        "box_filter": 32,
        "median_filter": 1,
        "sobel": 1,
        "laplacian": 1,
        "smooth_flow": 16,
        "highlight_recovery": 5,
        "cvtColor_extended": 0,
        "copy_field": 0,
    }
    strategies = {
        operation: (
            PartitionStrategy.STENCIL
            if halo_overrides[operation]
            else PartitionStrategy.LOCAL
        )
        for operation in _LEGACY_LOCAL_ADAPTER_OPERATIONS
    }
    parameter_scope = {
        "copy_field": "pointwise source copy (semantic alias)",
        "gaussian_blur": "sigma>0, odd kernel_size and radius<=16",
        "box_filter": "odd kernel_size and radius<=32, replicate border",
        "median_filter": "kernel_size=3, scalar/flow/RGB independent channels",
        "sobel": "scalar 2D or RGB vector3 with clamp border",
        "laplacian": "scalar 2D four-neighbour clamp border",
        "smooth_flow": "HxWx2, sigma>0, odd kernel_size and radius<=16",
        "highlight_recovery": "HxWx3 linear RGB, 11x11 halo",
        "cvtColor_extended": "HxWx3 float32, codes 36/38/40/44/54/55/56",
    }
    for operation in _LEGACY_LOCAL_ADAPTER_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        evidence = legacy_partition_evidence(operation)
        evidence_metadata = None
        executor = "copy_field_alias"
        if evidence is not None:
            evidence_metadata = {
                "operation": operation,
                "executor": evidence["executor"],
                "parity_evidence": {"cpu": True},
            }
            executor = str(evidence["executor"])
        contract = _qualified_contract(
            operation,
            halo=halo_overrides[operation],
            partition_strategy=strategies[operation],
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "stencil" if halo_overrides[operation] else "local",
            "semantic_only": True,
            "parameter_scope": parameter_scope[operation],
            "legacy_executor": executor,
            "legacy_partition_evidence": evidence_metadata,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_legacy_local",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": lambda arrays, params, _op=operation: _reference(
                _op, tuple(np.asarray(value) for value in arrays), dict(params or {})
            ),
            "parity_runner": verify_adapter_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_make_reader(operation),
            runner=_make_runner(operation),
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=contract.partition_strategy,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def _analysis_reader(first: Any, second: Any) -> Any:
    """Read a stage input window using the adapter's declared halo."""

    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        return tuple(np.ascontiguousarray(value[block.read_slice]) for value in arrays)
    context, block = first, second
    arrays = _as_inputs(context)
    return PartitionContext(
        operation=canonical_operation_name(str(_context_value(context, "operation", ""))),
        inputs=tuple(np.ascontiguousarray(value[block.read_slice]) for value in arrays),
        block=block,
        full_shape=tuple(arrays[0].shape),
        params=_as_params(context),
        stage=int(_context_value(context, "stage", 0)),
    )


def _analysis_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    inputs = _as_inputs(context)
    params = _as_params(context)
    if len(inputs) != 1:
        raise ValueError(f"{operation} analysis adapter expects one source image")
    if operation == "canny_aot":
        _source, low, high = _canny_parameters(inputs[0], params)
        return _canny_local_prefix(_source, low, high)
    if operation == "clahe_aot":
        source, clip, grid, bins = _clahe_parameters(inputs[0], params)
        lut = params.get("_clahe_lut")
        tile_h = params.get("_clahe_tile_h")
        tile_w = params.get("_clahe_tile_w")
        if lut is None or tile_h is None or tile_w is None:
            lut, tile_h, tile_w = _clahe_lut_reference(
                source, clip_limit=clip, tile_grid_size=grid, num_bins=bins
            )
        block = _context_value(context, "block")
        return _clahe_interpolate_reference(
            source,
            np.asarray(lut, dtype=np.float32),
            tile_grid_size=grid,
            tile_h=int(tile_h),
            tile_w=int(tile_w),
            block=block,
            source_origin=(
                (int(block.read_y0), int(block.read_x0))
                if block is not None
                else (0, 0)
            ),
        )
    raise ValueError(f"unknown analysis adapter operation: {operation}")


def _analysis_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    value = np.asarray(result)
    if value.ndim != 2 or not np.isfinite(value).all():
        return False
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    expected = tuple(block.read_shape if operation == "canny_aot" else block.shape) if block is not None else value.shape
    return tuple(value.shape) == expected


def _analysis_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    operation = canonical_operation_name(str(_context_value(context_or_block, "operation", "")))
    value = np.asarray(result)
    if operation == "canny_aot":
        output[block.write_slice] = value[block.core_slice]
    else:
        output[block.write_slice] = value
    return output


def register_analysis_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register semantic CPU adapters for Canny and CLAHE stage contracts.

    Canny is partitioned only through its Sobel/magnitude/NMS/threshold prefix;
    hysteresis is a single deterministic global stage.  CLAHE builds one
    global histogram/LUT field, then partitions only the interpolation stage.
    Neither registration changes ``AUTO_BLOCK_SAFE`` or adds native evidence.
    """

    registered: dict[str, BlockAdapter] = {}
    halos = {"canny_aot": 2, "clahe_aot": 0}
    stage_contracts = {
        "canny_aot": {
            "stages": ("sobel", "magnitude_nms", "threshold", "hysteresis_global"),
            "local_prefix": "sobel/magnitude/nms/threshold",
            "global_stage": "hysteresis",
            "parameter_scope": "aperture_size=3; finite 0<=low<=high; normalized f32 threshold domain",
        },
        "clahe_aot": {
            "stages": ("histogram_global", "clip_cdf_global", "interpolation"),
            "local_prefix": "interpolation using shared LUT field",
            "global_stage": "histogram+clip_cdf",
            "parameter_scope": "tile_grid_size 1..64 (<=1024 tiles); num_bins=256; max_val=255; clip_limit 0..64",
        },
    }
    for operation in _ANALYSIS_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.SAME,
            input_coordinate_map="identity",
            halo=halos[operation],
            halo_policy=(HaloPolicy.FIXED if halos[operation] else HaloPolicy.NONE),
            border_policy=(BorderPolicy.CLAMP if halos[operation] else BorderPolicy.NONE),
            reduction=ReductionPolicy.GLOBAL,
            merge=MergePolicy.CUSTOM,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=base.scratch_bytes,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="semantic CPU multi-stage parity; global stage remains explicit",
            partition_strategy=PartitionStrategy.MULTI_STAGE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "multi_stage",
            "semantic_only": True,
            "stage_contract": stage_contracts[operation],
            "native_probe_required": True,
            "native_runtime": False,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_multistage",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_analysis_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_analysis_reader,
            runner=_analysis_runner,
            validator=_analysis_validator,
            merger=_analysis_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.MULTI_STAGE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def _fft_reader(first: Any, second: Any) -> PartitionContext:
    """Build a stage context while retaining the complete spectrum domain."""

    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        operation = "fft2"
        return PartitionContext(
            operation=operation,
            inputs=arrays,
            block=block,
            full_shape=tuple(arrays[0].shape),
            params={},
            stage=0,
        )
    context, block = first, second
    arrays = _as_inputs(context)
    return PartitionContext(
        operation=canonical_operation_name(str(_context_value(context, "operation", "fft2"))),
        inputs=arrays,
        block=block,
        full_shape=tuple(arrays[0].shape),
        params=_as_params(context),
        stage=int(_context_value(context, "stage", 0)),
    )


def _fft_runner(context: Any) -> np.ndarray:
    """Fallback callback for direct adapter inspection.

    ``run_adapter_tiled`` routes FFT adapters through ``custom_executor`` so
    this callback is not used for normal staged execution.  Keeping it
    deterministic and full-frame avoids a partially-sliced spectrum if a
    caller invokes the adapter callbacks directly.
    """

    operation = canonical_operation_name(str(_context_value(context, "operation", "fft2")))
    return _fft_reference(operation, _as_inputs(context), _as_params(context))


def _fft_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    return bool(value.size and np.isfinite(value).all())


def _fft_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    # The custom executor owns staged allocation/merge.  This callback is a
    # conservative direct-use fallback and never crops or broadcasts a
    # spectrum implicitly.
    destination = np.asarray(output)
    source = np.asarray(result)
    if destination.shape != source.shape:
        raise ValueError("FFT adapter output shape mismatch")
    destination[...] = source
    return output


def _run_fft_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run one semantic separable FFT adapter over bounded stage strips."""

    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete FFT adapter registered for {canonical}")
    values = dict(params or {})
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    # Validate block dimensions against the eventual padded/spectrum shape
    # before doing work.  This also makes oversized requests fail closed.
    if canonical in {"fft", "fft2"}:
        if len(arrays) != 1:
            raise ValueError(f"{canonical} expects one real input")
        source = _fft_real_input(arrays[0])
        padded_shape = (
            _fft_next_power_of_two(source.shape[0]),
            _fft_next_power_of_two(source.shape[1]),
        )
        _fft_block_dimensions(block_size, padded_shape)
    elif canonical == "ifft2":
        if len(arrays) != 1:
            raise ValueError("ifft2 expects one complex spectrum")
        spectrum = _fft_pair_input(arrays[0])
        _fft_block_dimensions(block_size, tuple(int(value) for value in spectrum.shape[:2]))
    else:
        raise ValueError(f"unknown FFT adapter operation: {canonical}")
    return _fft_reference(canonical, arrays, values, block_size=block_size)


def run_fft_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Explicit semantic CPU entry point for staged FFT partitioning."""

    return _run_fft_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_fft_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 2.0e-5,
    atol: float = 2.0e-5,
) -> dict[str, Any]:
    """Compare full-frame and staged semantic FFT results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _fft_reference(canonical, arrays, values)
    tiled = _run_fft_partition_tiled(
        canonical,
        arrays,
        block_size=block_size,
        params=values,
    )
    left = np.asarray(full, dtype=np.float64)
    right = np.asarray(tiled, dtype=np.float64)
    error = float(np.max(np.abs(left - right))) if left.size else 0.0
    if canonical in {"fft", "fft2"}:
        source = _fft_real_input(arrays[0])
        domain = (
            _fft_next_power_of_two(source.shape[0]),
            _fft_next_power_of_two(source.shape[1]),
        )
    else:
        spectrum = _fft_pair_input(arrays[0])
        domain = tuple(int(value) for value in spectrum.shape[:2])
    return {
        "operation": canonical,
        "scope": "semantic_numpy_fft_separable",
        "backend": "cpu",
        "input_shape": [list(np.asarray(value).shape) for value in arrays],
        "output_shape": list(np.asarray(full).shape),
        "frequency_shape": list(domain),
        "block_size": tuple(_fft_block_dimensions(block_size, domain)),
        "stages": (
            ["pad", "row_fft", "column_fft", "pair_pack"]
            if canonical in {"fft", "fft2"}
            else ["pair_unpack", "column_ifft", "row_ifft", "crop"]
        ),
        "passed": bool(
            np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)
        ),
        "max_abs_error": error,
        "native_runtime": False,
    }


def register_fft_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register fail-closed CPU semantic adapters for FFT family operations.

    Frequency-domain dependencies remain global, so this registration is
    explicitly MULTI_STAGE and never enables ``AUTO_BLOCK_SAFE`` or native
    dispatch.  A target backend must provide an independent probe before any
    future promotion.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _FFT_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.CHANGING,
            input_coordinate_map="frequency_separable_row_column",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.GLOBAL,
            merge=MergePolicy.CUSTOM,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=int(base.scratch_bytes),
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason=(
                "deterministic CPU semantic separable FFT parity; full-frame "
                "frequency dependencies and native proof pending"
            ),
            partition_strategy=PartitionStrategy.MULTI_STAGE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "multi_stage",
            "semantic_only": True,
            "custom_executor": _run_fft_partition_tiled,
            "native_probe_required": True,
            "native_runtime": False,
            "stage_contract": (
                {
                    "stages": ["pad_to_next_power_of_two", "row_fft", "column_fft", "pair_pack"],
                    "padding": "each source dimension independently to next power of two",
                    "dtype": "float32 source -> float32 real/imag pair",
                    "hanning": "optional source-domain window before zero padding",
                }
                if operation in {"fft", "fft2"}
                else {
                    "stages": ["pair_unpack", "column_ifft", "row_ifft", "target_crop"],
                    "normalization": "1/height after column pass and 1/width after row pass",
                    "target_shape": "positive crop not exceeding spectrum dimensions",
                }
            ),
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_fft_separable",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": lambda inputs, params, _op=operation: _fft_reference(
                _op, inputs, params
            ),
            "parity_runner": verify_fft_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_fft_reader,
            runner=_fft_runner,
            validator=_fft_validator,
            merger=_fft_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.MULTI_STAGE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def _phase_reader(first: Any, second: Any) -> PartitionContext:
    if isinstance(first, BlockSpec):
        block = first
        arrays = tuple(np.asarray(value) for value in second)
        return PartitionContext(
            operation="phase_correlation",
            inputs=arrays,
            block=block,
            full_shape=tuple(arrays[0].shape),
            params={},
            stage=0,
        )
    context, block = first, second
    arrays = _as_inputs(context)
    return PartitionContext(
        operation="phase_correlation",
        inputs=arrays,
        block=block,
        full_shape=tuple(arrays[0].shape),
        params=_as_params(context),
        stage=int(_context_value(context, "stage", 0)),
    )


def _phase_runner(context: Any) -> np.ndarray:
    result = _phase_correlation_reference(_as_inputs(context), _as_params(context))
    return np.asarray(result, dtype=np.float32)


def _phase_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result, dtype=np.float32).reshape(-1)
    return bool(value.shape == (3,) and np.isfinite(value).all())


def _phase_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype).reshape(-1)
    if destination.size != value.size:
        raise ValueError("phase correlation reduction shape mismatch")
    destination[...] = value.reshape(destination.shape)
    return output


def _run_phase_correlation_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> tuple[float, float, float]:
    canonical = canonical_operation_name(operation)
    if canonical not in _PHASE_CORRELATION_ADAPTER_OPERATIONS:
        raise ValueError(f"unknown phase-correlation adapter operation: {canonical}")
    adapter = lookup_block_adapter(canonical)
    if (
        adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete phase-correlation adapter registered for {canonical}")
    values = dict(params or {})
    reference, comparison = _phase_inputs(inputs)
    frequency_shape = (
        _fft_next_power_of_two(reference.shape[0]),
        _fft_next_power_of_two(reference.shape[1]),
    )
    # Validate both the frequency-stage strips and the cropped output-domain
    # reduction strips before allocating any intermediate buffers.
    _fft_block_dimensions(block_size, frequency_shape)
    _fft_block_dimensions(block_size, tuple(int(v) for v in reference.shape))
    return _phase_correlation_reference(
        (reference, comparison),
        values,
        block_size=block_size,
    )


def run_phase_correlation_partition_tiled(
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> tuple[float, float, float]:
    """Explicit semantic CPU phase-correlation map/reduce execution."""

    return _run_phase_correlation_partition_tiled(
        "phase_correlation",
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_phase_correlation_parity(
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 2.0e-5,
    atol: float = 2.0e-5,
) -> dict[str, Any]:
    """Compare full-frame and staged phase-correlation reductions."""

    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _phase_correlation_reference(arrays, values)
    tiled = _run_phase_correlation_partition_tiled(
        "phase_correlation",
        arrays,
        block_size=block_size,
        params=values,
    )
    left = np.asarray(full, dtype=np.float64)
    right = np.asarray(tiled, dtype=np.float64)
    error = float(np.max(np.abs(left - right))) if left.size else 0.0
    reference, _comparison = _phase_inputs(arrays)
    frequency_shape = (
        _fft_next_power_of_two(reference.shape[0]),
        _fft_next_power_of_two(reference.shape[1]),
    )
    return {
        "operation": "phase_correlation",
        "scope": "semantic_numpy_phase_fft_map_reduce",
        "backend": "cpu",
        "input_shape": [list(np.asarray(value).shape) for value in arrays],
        "frequency_shape": list(frequency_shape),
        "correlation_shape": list(reference.shape),
        "block_size": tuple(_fft_block_dimensions(block_size, frequency_shape)),
        "reduction_order": "row-major correlation tiles; first maximum wins",
        "stages": [
            "pad_to_next_power_of_two",
            "row_fft_reference_and_comparison",
            "column_fft_reference_and_comparison",
            "cross_power_normalize",
            "column_ifft",
            "row_ifft_crop",
            "row_major_peak_reduce",
        ],
        "passed": bool(
            np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)
        ),
        "max_abs_error": error,
        "native_runtime": False,
    }


def register_phase_correlation_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register a CPU semantic phase-correlation map/reduce contract.

    The correlation surface has global FFT dependencies and a variable
    coordinate-domain reduction result.  Registration therefore remains
    explicit and fail-closed; no automatic or native backend capability is
    changed here.
    """

    registered: dict[str, BlockAdapter] = {}
    operation = "phase_correlation"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.REDUCE,
        input_coordinate_map="frequency_output_domain",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.NONE,
        reduction=ReductionPolicy.GLOBAL,
        merge=MergePolicy.CUSTOM,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason=(
            "deterministic CPU semantic phase-correlation FFT map/reduce "
            "parity; native proof pending"
        ),
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "map_reduce",
        "pipeline_kind": "multi_stage_frequency",
        "output_domain": True,
        "output_domain_kind": "correlation_surface_to_shift_tuple",
        "semantic_only": True,
        "custom_executor": _run_phase_correlation_partition_tiled,
        "native_probe_required": True,
        "native_runtime": False,
        "stage_contract": {
            "stages": [
                "two_padded_fft",
                "cross_power_normalize",
                "inverse_fft_crop",
                "deterministic_peak_reduce",
            ],
            "padding": "each input dimension independently to next power of two",
            "hanning": "optional source-domain window; default true per AOT API",
            "output": "(dx, dy, response), wrapped using original source dimensions",
            "max_shift": "accepted for API compatibility; maintained AOT graph does not apply it",
        },
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_phase_fft_map_reduce",
                "native_runtime": False,
            }
        },
        "full_frame_callback": lambda inputs, params: _phase_correlation_reference(
            inputs, params
        ),
        "parity_runner": verify_phase_correlation_parity,
        "deterministic_merge": True,
        "merge_order": "row-major correlation tiles; first maximum wins",
    }
    registered[operation] = register_block_adapter(
        operation,
        reader=_phase_reader,
        runner=_phase_runner,
        validator=_phase_validator,
        merger=_phase_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return registered


def _global_reader(first: Any, second: Any) -> Any:
    """Read a no-halo source tile for a global map stage."""

    return _analysis_reader(first, second)


def _global_runner(context: Any) -> Any:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    if operation in {"ransac_flow_cleanup", "ransac_flow_cleanup_aot"}:
        return _ransac_partial(context)
    if operation == "hough_lines_aot":
        inputs = _as_inputs(context)
        if len(inputs) != 1:
            raise ValueError("hough map expects one edge input")
        params = _as_params(context)
        block = _context_value(context, "block")
        origin = (
            (int(block.read_y0), int(block.read_x0))
            if block is not None
            else (0, 0)
        )
        return _hough_vote_partial(inputs[0], params=params, origin=origin)
    raise ValueError(f"unknown global adapter operation: {operation}")


def _global_validator(first: Any, second: Any) -> bool:
    result = first if _context_value(second, "block") is not None else second
    value = np.asarray(result)
    operation = canonical_operation_name(str(_context_value(second, "operation", "")))
    if operation in {"ransac_flow_cleanup", "ransac_flow_cleanup_aot"}:
        return _ransac_partial_validator(result, second)
    return bool(value.ndim == 2 and value.size > 0 and np.isfinite(value).all())


def _hough_map_merger(output: Any, result: Any, _context_or_block: Any) -> Any:
    destination = np.asarray(output)
    value = np.asarray(result, dtype=destination.dtype)
    if destination.shape != value.shape:
        raise ValueError("Hough accumulator shape mismatch")
    destination[...] += value
    return output


def _run_global_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> Any:
    """Run a deterministic global map/reduce or staged partition contract."""

    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        adapter is None
        or not adapter.partition_ready
        or not callable(adapter.metadata.get("custom_executor"))
    ):
        raise ValueError(f"no complete global adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 1:
        raise ValueError(f"{canonical} adapter expects one input")
    values = dict(params or {})
    source = arrays[0]
    grid = BlockGrid(source.shape, size=block_size, halo=0)
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))

    if canonical in {"ransac_flow_cleanup", "ransac_flow_cleanup_aot"}:
        flow, cutoff = _flow_parameters(source, values)
        accumulator = np.zeros(3, dtype=np.float64)
        for block in blocks:
            tile = np.ascontiguousarray(flow[block.read_slice])
            partial = _ransac_partial(
                PartitionContext(canonical, (tile,), block, tuple(flow.shape), values)
            )
            _sum_partial_merger(accumulator, partial, block)
        return _ransac_finalize_partial(accumulator, (flow,), {**values, "threshold": cutoff})

    resolved = _hough_parameters(source, values)
    accumulator = np.zeros((resolved["num_rho"], resolved["num_theta"]), dtype=np.int64)
    for block in blocks:
        tile = np.ascontiguousarray(source[block.read_slice])
        partial = _hough_vote_partial(
            tile,
            params=resolved,
            origin=(block.read_y0, block.read_x0),
        )
        _hough_map_merger(accumulator, partial, block)
    return _hough_peaks_reference(accumulator, resolved)


def run_global_partition_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> Any:
    """Public explicit entry point for RANSAC/Hough global contracts."""

    return _run_global_partition_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_global_partition_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Compare deterministic full-frame and global-partitioned results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_global_partition_tiled(
        canonical, arrays, block_size=block_size, params=values
    )
    if isinstance(full, list):
        passed = full == tiled
        errors = 0.0 if passed else float("inf")
    else:
        left, right = np.asarray(full), np.asarray(tiled)
        errors = float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64)))) if left.size else 0.0
        passed = bool(np.array_equal(left, right))
    adapter = lookup_block_adapter(canonical)
    # Report the requested logical grid rather than relying on a temporary
    # variable from one of the specialized executors.  Global adapters use
    # the source grid for RANSAC and the vote grid for Hough internally, but
    # the public parity report only promises the caller's partition size.
    report_grid = BlockGrid(arrays[0].shape, size=block_size)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_global_partition",
        "backend": "cpu",
        "block_size": (
            report_grid.block_height,
            report_grid.block_width,
        ),
        "passed": bool(passed),
        "max_abs_error": errors,
        "deterministic_merge": bool(adapter.metadata.get("deterministic_merge", False)) if adapter else False,
        "native_runtime": False,
    }


GLOBAL_REDUCTION_CONTRACT_OPERATIONS = (
    "histogram",
    "otsu_threshold",
    "ssim_aot",
    "zncc",
    "ncc_alignment",
)

ITERATIVE_FEATURE_GAP_OPERATIONS = (
    "mlri_admm_demosaic",
    "mlri_admm_demosaic_1channel",
    "mlri_admm_demosaic_3channel",
    "bm3d",
    "akaze",
    "ofb",
    "find_homography",
)


def iterative_feature_gap_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Audit iterative/variable-cardinality operations without promotion."""

    names = ITERATIVE_FEATURE_GAP_OPERATIONS if operations is None else operations
    if isinstance(names, str):
        names = (names,)
    selected: list[str] = []
    for raw in names:
        canonical = canonical_operation_name(raw)
        if canonical not in ITERATIVE_FEATURE_GAP_OPERATIONS:
            raise ValueError(
                "iterative feature report supports only "
                f"{ITERATIVE_FEATURE_GAP_OPERATIONS}; got {raw!r}"
            )
        if canonical not in selected:
            selected.append(canonical)
    records: dict[str, dict[str, Any]] = {}
    for operation in selected:
        adapter = lookup_block_adapter(operation)
        native_records = _native_evidence_records_for(operation, backend, device)
        records[operation] = {
            "operation": operation,
            "adapter_registered": adapter is not None,
            "semantic_cpu_partition": bool(
                adapter is not None and can_partition_block(operation, backend)
            ),
            "native_evidence_records": native_records,
            "native_partition_evidence": False,
            "native_runtime": False,
            "status": "gap_fail_closed",
            "blocked_reasons": [
                "iterative or variable-cardinality state crosses tile boundaries",
                "full-frame versus tiled semantic parity is not proven for the production parameters",
                "native backend/device evidence is unavailable or intentionally not inferred",
            ],
            "required_evidence": [
                "bounded deterministic CPU candidate validator",
                "non-multiple tile and boundary/ordering proof",
                "same-backend native full-frame versus tiled parity on exact device",
            ],
            "preserves_default_full_frame": True,
        }
    return {
        "scope": "iterative_feature_partition_contract_audit",
        "backend": None if backend is None else str(backend).strip().lower(),
        "device": None if device is None else str(device).strip(),
        "operations": records,
        "operation_order": selected,
        "semantic_cpu_parity_proven": False,
        "native_partition_parity_proven": False,
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_iterative_parity_evidence",
    }


def global_reduction_partition_gap_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Audit global reductions without promoting CPU map/reduce to native.

    The semantic adapters can provide deterministic CPU map/reduce parity, but
    reductions require an explicit same-backend native proof and deterministic
    accumulation/ordering.  This report is diagnostic and never alters
    dispatch or the automatic block registry.
    """

    names = (
        (GLOBAL_REDUCTION_CONTRACT_OPERATIONS if operations is None else operations)
    )
    if isinstance(names, str):
        names = (names,)
    selected: list[str] = []
    for raw in names:
        canonical = canonical_operation_name(raw)
        if canonical not in GLOBAL_REDUCTION_CONTRACT_OPERATIONS:
            raise ValueError(
                "global reduction report supports only "
                f"{GLOBAL_REDUCTION_CONTRACT_OPERATIONS}; got {raw!r}"
            )
        if canonical not in selected:
            selected.append(canonical)
    records: dict[str, dict[str, Any]] = {}
    for operation in selected:
        adapter = lookup_block_adapter(operation)
        native_records = _native_evidence_records_for(operation, backend, device)
        native_qualified = any(
            bool(item.get("qualified")) and bool(item.get("native_runtime"))
            for item in native_records
        )
        records[operation] = {
            "operation": operation,
            "path": operation_path(operation).value,
            "adapter_registered": adapter is not None,
            "semantic_cpu_partition": bool(
                adapter is not None and can_partition_block(operation, backend)
            ),
            "automatic_safe": bool(can_auto_block(operation, backend)),
            "partition_safe": bool(can_partition_block(operation, backend)),
            "automatic_dispatch_safe": bool(
                can_auto_partition_dispatch(operation, backend)
            ),
            "native_partition_evidence": native_qualified,
            "native_evidence_records": native_records,
            "native_runtime": native_qualified,
            "reduction_order": "row-major deterministic merge",
            "status": "semantic_cpu_qualified" if adapter is not None else "gap_fail_closed",
            "blocked_reasons": [
                "global reduction result depends on complete input domain",
                "native accumulation/order parity is not proven",
                "exact backend/device evidence is unavailable",
            ],
            "required_evidence": [
                "non-multiple shapes with deterministic CPU map/reduce parity",
                "same-backend native full-frame versus tiled reduction parity",
                "stable floating-point accumulation/error bound on each target device",
            ],
            "preserves_default_full_frame": True,
        }
    return {
        "scope": "global_reduction_partition_contract_audit",
        "backend": None if backend is None else str(backend).strip().lower(),
        "device": None if device is None else str(device).strip(),
        "operations": records,
        "operation_order": selected,
        "semantic_cpu_parity_proven": any(
            bool(item["semantic_cpu_partition"]) for item in records.values()
        ),
        "native_partition_parity_proven": any(
            bool(item["native_partition_evidence"]) for item in records.values()
        ),
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_reduction_parity_evidence",
    }


def register_global_partition_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register semantic CPU contracts for RANSAC flow cleanup and Hough."""

    registered: dict[str, BlockAdapter] = {}
    for operation in _GLOBAL_PARTITION_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        is_ransac = operation in {"ransac_flow_cleanup", "ransac_flow_cleanup_aot"}
        contract = OperationContract(
            operation=operation,
            shape_transform=(ShapeTransform.SAME if is_ransac else ShapeTransform.REDUCE),
            input_coordinate_map="identity",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.GLOBAL,
            merge=(MergePolicy.CUSTOM if is_ransac else MergePolicy.VARIABLE),
            variable_cardinality=not is_ransac,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=base.scratch_bytes,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="deterministic CPU global map/reduce parity; native proof pending",
            partition_strategy=PartitionStrategy.MAP_REDUCE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "global_map_reduce",
            "semantic_only": True,
            "custom_executor": _run_global_partition_tiled,
            "deterministic_merge": True,
            "merge_order": "row-major_block_index",
            "parameter_scope": (
                "threshold finite [0,10000], stride_refine=stride_final=1"
                if is_ransac
                else "rho/theta bounded; edge_threshold>=0; nms_radius<=64; max_peaks<=500"
            ),
            "global_stage": "refine_mean_and_apply" if is_ransac else "peak_nms_and_order",
            "native_probe_required": True,
            "native_runtime": False,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_global_map_reduce",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_global_partition_parity,
        }
        validator = _ransac_partial_validator if is_ransac else _global_validator
        merger = _sum_partial_merger if is_ransac else _hough_map_merger
        registered[operation] = register_block_adapter(
            operation,
            reader=_global_reader,
            runner=_global_runner,
            validator=validator,
            merger=merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.MAP_REDUCE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_mtb_partition_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register the explicit semantic CPU contract for ``align_mtb``.

    The contract is staged/map-reduce only: histogram and shifted-error maps
    are deterministic, while pyramid construction and 3x3 level search stay
    global stage boundaries.  Registration never changes ``AUTO_BLOCK_SAFE``
    or native backend evidence.
    """

    operation = "align_mtb"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.REDUCE,
        input_coordinate_map="identity",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.NONE,
        reduction=ReductionPolicy.GLOBAL,
        merge=MergePolicy.CUSTOM,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason="deterministic CPU MTB staged map/reduce parity; native proof pending",
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "staged_map_reduce",
        "semantic_only": True,
        "custom_executor": _run_mtb_partition_tiled,
        "native_probe_required": True,
        "native_runtime": False,
        "deterministic_merge": True,
        "merge_order": "row-major_block_index",
        "parameter_scope": "max_levels in [1,12], tolerance in [0,1]",
        "stage_contract": {
            "stages": [
                "reflect101_gaussian_pyramid",
                "per-level_histogram_map_reduce",
                "median_bitmap_and_exclusion_global_stage",
                "3x3_shift_error_map_reduce",
                "coarse_to_fine_displacement_update",
            ],
            "tie_rule": "offset_y then offset_x; strict first minimum",
            "partitioned_maps": "histogram and shifted error only",
        },
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_mtb_staged_map_reduce",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _reference,
        "parity_runner": verify_mtb_partition_parity,
    }
    registered = register_block_adapter(
        operation,
        reader=_global_reader,
        runner=_mtb_map_runner,
        validator=_mtb_map_validator,
        merger=_mtb_map_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return {operation: registered}


def register_jblu_partition_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register explicit semantic CPU output-domain JBLU blocks."""

    operation = "joint_bilateral_upsample"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.CHANGING,
        input_coordinate_map="high_guide_output_domain",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.CLAMP,
        reduction=ReductionPolicy.NONE,
        merge=MergePolicy.OVERWRITE,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason="deterministic CPU JBLU output-domain parity; native proof pending",
        partition_strategy=PartitionStrategy.COORDINATE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "output_domain",
        "semantic_only": True,
        "custom_executor": _run_jblu_partition_tiled,
        "native_probe_required": True,
        "native_runtime": False,
        "deterministic_merge": True,
        "merge_order": "row-major_guide_output_block",
        "parameter_scope": "source float32; preset low|medium|high; fixed radius=2",
        "stage_contract": {
            "output_domain": "guide_hi HxW",
            "source_footprint": "clamped 5x5 low-resolution neighborhood",
            "guide_mapping": "floor output->low; round low->guide; clamp",
            "flow_scale": "channel 0 by scale_x and channel 1 by scale_y",
        },
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_jblu_output_domain",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _reference,
        "parity_runner": verify_jblu_partition_parity,
    }
    registered = register_block_adapter(
        operation,
        reader=_jblu_reader,
        runner=_jblu_runner,
        validator=_jblu_validator,
        merger=_jblu_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.COORDINATE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return {operation: registered}


def register_bilateral_grid_partition_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register explicit semantic CPU bilateral-grid stages."""

    operation = "bilateral_grid_filter"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.SAME,
        input_coordinate_map="identity",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.CLAMP,
        reduction=ReductionPolicy.GLOBAL,
        merge=MergePolicy.CUSTOM,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason="deterministic CPU bilateral-grid staged map/reduce parity; native proof pending",
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "staged_map_reduce",
        "semantic_only": True,
        "custom_executor": _run_bilateral_grid_partition_tiled,
        "native_probe_required": True,
        "native_runtime": False,
        "deterministic_merge": True,
        "merge_order": "row-major_input_splat_block",
        "parameter_scope": "preset light|medium|heavy; source float32 grayscale or RGB",
        "stage_contract": {
            "stages": [
                "per-input-pixel-grid-splat-map",
                "deterministic-grid-reduction",
                "separable-gaussian-blur-x-y-z",
                "output-domain-trilinear-slice",
            ],
            "accumulator": "float64 semantic numerator/denominator lanes",
        },
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_bilateral_grid_staged_map_reduce",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _reference,
        "parity_runner": verify_bilateral_grid_partition_parity,
    }
    registered = register_block_adapter(
        operation,
        reader=_bilateral_grid_partial_reader,
        runner=_bilateral_grid_partial_runner,
        validator=_bilateral_grid_partial_validator,
        merger=_bilateral_grid_partial_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.MAP_REDUCE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return {operation: registered}


def register_inpaint_partition_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register bounded deterministic CPU inpaint level snapshots."""

    operation = "inpaint"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.SAME,
        input_coordinate_map="identity",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.CLAMP,
        reduction=ReductionPolicy.GLOBAL,
        merge=MergePolicy.CUSTOM,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason="deterministic CPU inpaint level-snapshot parity; native proof pending",
        partition_strategy=PartitionStrategy.ITERATIVE,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "iterative_snapshot",
        "semantic_only": True,
        "custom_executor": _run_inpaint_partition_tiled,
        "native_probe_required": True,
        "native_runtime": False,
        "deterministic_merge": True,
        "merge_order": "row-major_level_block",
        "parameter_scope": "float32 scalar/RGB; binary mask; radius integer 1..8; flags 0|1",
        "stage_contract": {
            "stages": [
                "8-neighbour_distance_levels",
                "immutable_level_snapshot",
                "inverse-distance-squared_local_fill",
                "row-major_level_publish",
            ],
            "same_level_policy": "snapshot (prevents tile-order races)",
        },
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_inpaint_iterative_snapshot",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _reference,
        "parity_runner": verify_inpaint_partition_parity,
        "alias_operations": ("inpaint_aot",),
    }
    registered = register_block_adapter(
        operation,
        reader=_inpaint_reader,
        runner=_inpaint_runner,
        validator=_inpaint_validator,
        merger=_inpaint_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.ITERATIVE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return {operation: registered, "inpaint_aot": registered}


def register_map_reduce_block_adapters(*, replace: bool = False) -> Mapping[str, BlockAdapter]:
    """Register deterministic CPU semantic map/reduce adapters.

    These adapters are intentionally not legacy-dispatch-qualified: the
    histogram path has no maintained tile executor in ``aot_api`` and Otsu's
    existing reduction is still a specialized implementation.  SSIM is
    similarly exposed as an explicit halo-aware reduction: each tile returns
    ``[sum_ssim, valid_count]`` and the row-major reducer combines those
    values in a fixed float64 accumulator.  They are therefore exposed for
    the explicit map/reduce planner only.  Their metadata carries
    ``partition_kind='map_reduce'`` plus the accumulator factory, reducer,
    and finalizer so automatic dispatch can remain fail-closed until a native
    backend proof is added.
    """

    registered: dict[str, BlockAdapter] = {}
    map_functions = {
        "histogram": _map_histogram,
        "otsu_threshold": _map_otsu,
        "ssim_aot": _map_ssim,
        "zncc": _ncc_map,
        "ncc_alignment": _ncc_alignment_map,
        "stitch_tile": _stitch_map,
        "stitch_tile_normalized": _stitch_map,
    }
    finalizers = {
        "histogram": _histogram_finalize,
        "otsu_threshold": _otsu_finalize,
        "ssim_aot": _ssim_finalize,
        "zncc": _ncc_map_finalize,
        "ncc_alignment": _ncc_alignment_finalize,
        "stitch_tile": _stitch_finalize,
        "stitch_tile_normalized": _stitch_finalize,
    }
    for operation in _MAP_REDUCE_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        base = operation_contract(operation)
        is_ssim = operation == "ssim_aot"
        is_ncc = operation in _NCC_ADAPTER_OPERATIONS
        is_stitch = operation in _STITCH_ADAPTER_OPERATIONS
        if is_ncc:
            # The output search surface is derived from image/template
            # geometry and the alignment result is a global argmax.  Keep
            # these richer semantics in the adapter-local contract; the
            # maintained global operation contract and AUTO_BLOCK_SAFE table
            # remain unchanged and therefore automatic/native dispatch stays
            # fail-closed.
            contract = OperationContract(
                operation=operation,
                shape_transform=(
                    ShapeTransform.CHANGING
                    if operation == "zncc"
                    else ShapeTransform.REDUCE
                ),
                input_coordinate_map={
                    "kind": "sliding_window",
                    "template_input": 1,
                    "stride_param": "stride",
                },
                # A rectangular template's source footprint is dynamic.  The
                # exact (height-1,width-1) halo is carried in metadata per
                # call; scalar ``halo`` remains zero for the legacy contract.
                halo=0,
                halo_policy=HaloPolicy.DYNAMIC,
                border_policy=BorderPolicy.NONE,
                reduction=ReductionPolicy.GLOBAL,
                merge=MergePolicy.CUSTOM,
                variable_cardinality=False,
                deterministic=True,
                side_effect=False,
                side_effect_free=True,
                scratch_bytes=0,
                backend_capability={"cpu": {"supported": True, "parity": True}},
                automatic_safe=False,
                parity_qualified=False,
                known=True,
                reason=(
                    "deterministic CPU NCC output-domain map/reduce parity; "
                    "native proof pending"
                ),
                partition_strategy=PartitionStrategy.MAP_REDUCE,
                partition_qualified=True,
            )
        elif is_stitch:
            contract = OperationContract(
                operation=operation,
                shape_transform=ShapeTransform.SAME,
                input_coordinate_map="tile_origins",
                halo=0,
                halo_policy=HaloPolicy.NONE,
                border_policy=BorderPolicy.NONE,
                reduction=ReductionPolicy.GLOBAL,
                merge=MergePolicy.REDUCE,
                variable_cardinality=False,
                deterministic=True,
                side_effect=False,
                side_effect_free=True,
                scratch_bytes=0,
                backend_capability={"cpu": {"supported": True, "parity": True}},
                automatic_safe=False,
                parity_qualified=False,
                known=True,
                reason=(
                    "deterministic CPU ordered overlap stitch map/reduce parity; "
                    "native proof pending"
                ),
                partition_strategy=PartitionStrategy.MAP_REDUCE,
                partition_qualified=True,
            )
        else:
            contract = None
        contract = OperationContract(
            operation=operation,
            shape_transform=(
                contract.shape_transform if (is_ncc or is_stitch) else base.shape_transform
            ),
            input_coordinate_map=(
                contract.input_coordinate_map
                if (is_ncc or is_stitch)
                else base.input_coordinate_map
            ),
            # SSIM's window radius is parameterized (1..10); 10 is the
            # contract's maximum resident halo and the runtime narrows it to
            # ``window_size // 2`` for each call.  NCC carries a rectangular
            # template footprint in metadata and retains halo=0 here.
            halo=(contract.halo if (is_ncc or is_stitch) else (10 if is_ssim else 0)),
            halo_policy=(
                contract.halo_policy
                if (is_ncc or is_stitch)
                else (HaloPolicy.DYNAMIC if is_ssim else base.halo_policy)
            ),
            border_policy=(
                contract.border_policy
                if (is_ncc or is_stitch)
                else (BorderPolicy.CLAMP if is_ssim else base.border_policy)
            ),
            reduction=(
                contract.reduction
                if (is_ncc or is_stitch)
                else base.reduction
            ),
            merge=(
                contract.merge
                if (is_ncc or is_stitch)
                else (MergePolicy.REDUCE if is_ssim else base.merge)
            ),
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=0 if (is_ncc or is_stitch) else base.scratch_bytes,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True if (is_ncc or is_stitch) else base.known,
            reason=(
                "deterministic CPU NCC output-domain map/reduce parity; native proof pending"
                if is_ncc
                else (
                    "deterministic CPU ordered overlap stitch map/reduce parity; native proof pending"
                    if is_stitch
                    else (
                        "deterministic CPU SSIM halo map/reduce parity; native proof pending"
                        if is_ssim
                        else "deterministic CPU map/reduce semantic parity; native proof pending"
                    )
                )
            ),
            partition_strategy=PartitionStrategy.MAP_REDUCE,
            partition_qualified=True,
        )
        if operation in {"histogram", "otsu_threshold"}:
            factory = lambda params=None: np.zeros(
                int((params or {}).get("bins", 256)), dtype=np.int64
            )
        elif is_ssim:
            factory = lambda params=None: np.zeros(2, dtype=np.float64)
        elif operation == "zncc":
            factory = lambda params=None, shape=None: np.empty(
                tuple(shape or (0, 0)), dtype=np.float32
            )
        elif is_stitch:
            # Sequence-domain execution allocates this from the five input
            # arrays because the output frame shape is not known from params
            # alone.  The callable remains present for metadata completeness.
            factory = lambda params=None, shape=None: None
        else:  # ncc_alignment
            factory = lambda params=None, shape=None: np.asarray(
                (-np.inf, 0.0, 0.0), dtype=np.float64
            )
        validator = _ssim_map_validator if is_ssim else _map_reduce_validator
        if operation == "zncc":
            validator = _ncc_map_validator
        elif operation == "ncc_alignment":
            validator = _ncc_alignment_map_validator
        elif is_stitch:
            validator = _stitch_validator
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "map_reduce",
            "output_grid": bool(is_ncc),
            "sequence_domain": bool(is_stitch),
            "output_shape": _ncc_output_shape if is_ncc else None,
            "source_halo": _ncc_source_halo if is_ncc else None,
            "map": map_functions[operation],
            "reduce": _map_reduce_merger,
            "output_factory": factory,
            "finalize": finalizers[operation],
            # The reducer consumes blocks in this explicit order.  This is a
            # semantic guarantee for callers and a guard against future
            # parallel reductions accidentally changing floating-point sums.
            "merge_order": "row-major_block_index",
            "deterministic_merge": True,
            "halo": (lambda params: _ssim_window_radius(int((params or {}).get("window_size", 11))))
            if is_ssim
            else 0,
            "max_halo": 10 if is_ssim else 0,
            "coordinate_contract": (
                {
                    "kind": "sliding_window",
                    "output_shape": "(H-h_t)//stride+1, (W-w_t)//stride+1",
                    "source_halo": "(h_t-1, w_t-1)",
                }
                if is_ncc
                else None
            ),
            "sequence_contract": (
                {
                    "kind": "ordered_tile_origins",
                    "order": "row_major_origin_then_input_index",
                    "overlap": "allowed",
                    "canonicalized_before_merge": True,
                    "normalized_order_sensitive": False,
                }
                if is_stitch
                else None
            ),
            "deterministic_merge": True,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": (
                        "deterministic_numpy_ncc_output_map_reduce"
                        if is_ncc
                        else (
                            "deterministic_numpy_ssim_halo_map_reduce"
                            if is_ssim
                            else "deterministic_numpy_map_reduce"
                        )
                    ),
                    "native_runtime": False,
                }
            },
            "native_runtime": False,
            "semantic_only": True,
        }
        if operation == "zncc":
            metadata["reduce"] = _ncc_map_merger
        elif operation == "ncc_alignment":
            metadata["reduce"] = _ncc_alignment_merger
        elif is_stitch:
            metadata["reduce"] = _stitch_merger
        registered[operation] = register_block_adapter(
            operation,
            reader=(
                _ncc_reader
                if is_ncc
                else (_stitch_reader if is_stitch else _make_reader(operation))
            ),
            runner=map_functions[operation],
            validator=validator,
            merger=metadata["reduce"],
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.MAP_REDUCE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_accumulator_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register semantic CPU adapters for pointwise accumulator finalizers.

    ``mean_division`` and ``normalize_accumulator`` are classified as global
    in :mod:`taichi_vision.taichi_aot.block` because their usual call site is
    the final stage of a cross-tile fusion.  Once each tile's ``sum_img`` and
    ``sum_weight`` have been produced, the common AOT kernels perform only a
    per-pixel divide (with a fallback/reference value for zero weight).  These
    adapters expose that mathematically local form for explicit CPU semantic
    partition tests and future planner work.

    Registration deliberately does *not* mutate ``AUTO_BLOCK_SAFE``, the
    legacy global path, or any native backend evidence.  Automatic dispatch
    therefore remains fail-closed until a backend-specific proof covers the
    accumulator lifecycle and merge ordering.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _ACCUMULATOR_ADAPTER_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        # Keep this contract deliberately local for the adapter, while the
        # maintained operation contract in ``block.py`` remains GLOBAL.  The
        # adapter's local contract is only used by explicit partition helpers.
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.SAME,
            input_coordinate_map="identity",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=0,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason=(
                "pointwise accumulator semantic parity on CPU; "
                "legacy operation remains global and native proof is pending"
            ),
            partition_strategy=PartitionStrategy.LOCAL,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "local_map",
            "source_path": "global",
            "semantic_only": True,
            "legacy_global_operation": True,
            "legacy_partition_evidence": None,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_accumulator_map",
                    "native_runtime": False,
                }
            },
            "native_runtime": False,
            "full_frame_callback": _reference,
            "parity_runner": verify_adapter_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_make_reader(operation),
            runner=_make_runner(operation),
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.LOCAL,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_coordinate_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register explicit CPU semantic adapters for pointwise transforms.

    ``naturalTonemapping``/``tone_map_srgb`` are qualified only when their
    global texture stage is disabled (``texture_amount=0``); the runner
    rejects any other value.  ``to_gamma_proxy`` is purely pointwise.  No
    operation in this family has legacy executor evidence, so the strict
    automatic/native dispatch gate remains false even after registration.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _COORDINATE_ADAPTER_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        contract = _qualified_contract(operation)
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "local",
            "semantic_only": True,
            "legacy_partition_evidence": None,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_semantics",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_adapter_parity,
        }
        reader = _rotate_reader if operation == "rotate_by_flip" else _make_reader(operation)
        runner = _rotate_runner if operation == "rotate_by_flip" else _make_runner(operation)
        registered[operation] = register_block_adapter(
            operation,
            reader=reader,
            runner=runner,
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.LOCAL,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_coordinate_domain_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register bounded shape/coordinate semantic adapters on CPU.

    ``resize`` is scoped to the already-probed linear/cubic/area offset
    conventions; ``image_pyramid`` is one deterministic 2x Gaussian stage;
    ``warp_affine_aot`` uses the maintained inverse-matrix plus REFLECT_101
    sampling rule; and ``copy_make_border_aot`` covers the five portable border
    modes.  Source windows are deliberately retained in full for the semantic
    adapter because affine reflection can map an arbitrary destination tile to
    the entire source period.  This is an explicit parity harness, not a claim
    that those operations are memory-safe/native on any graphics backend.
    """

    registered: dict[str, BlockAdapter] = {}
    parameter_scope = {
        "resize": "linear/cubic/area; output-domain offset convention",
        "image_pyramid": "2x Gaussian [1,4,6,4,1]/256 REFLECT_101",
        "warp_affine_aot": "finite invertible 2x3 matrix; bilinear REFLECT_101",
        "copy_make_border_aot": "modes CONSTANT/REPLICATE/REFLECT/WRAP/REFLECT_101",
    }
    strategy = {
        "resize": PartitionStrategy.COORDINATE,
        "image_pyramid": PartitionStrategy.MULTI_STAGE,
        "warp_affine_aot": PartitionStrategy.COORDINATE,
        "copy_make_border_aot": PartitionStrategy.COORDINATE,
    }
    for operation in _COORDINATE_DOMAIN_ADAPTER_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        # Use a private adapter contract rather than mutating the maintained
        # operation contract in block.py.  In particular copy_make_border is
        # shape-changing even though the legacy table historically classified
        # it as DIRECT.
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.CHANGING,
            input_coordinate_map="output_domain",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=base.border_policy if operation == "copy_make_border_aot" else BorderPolicy.UNKNOWN,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=base.scratch_bytes,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="coordinate-domain semantic parity on CPU only; native evidence pending",
            partition_strategy=strategy[operation],
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "coordinate_domain",
            "coordinate_domain": True,
            "semantic_only": True,
            "source_window": "full_frame",
            "parameter_scope": parameter_scope[operation],
            "native_probe_required": True,
            "native_runtime": False,
            "legacy_partition_evidence": None,
            # Deliberately not the maintained specialized executor marker.
            # This keeps the legacy auto-dispatch diagnostic gate false until
            # a target-qualified native probe is registered.
            "legacy_executor": "coordinate_domain_semantic",
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_coordinate_domain",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_coordinate_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_coordinate_reader,
            runner=_coordinate_runner,
            validator=_coordinate_validator,
            merger=_coordinate_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=strategy[operation],
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_coordinate_warp_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register semantic CPU contracts for remap/flow/perspective warps.

    These adapters preserve the complete source and coordinate maps while
    partitioning only the destination domain.  This is the only safe generic
    interpretation for arbitrary maps and low-resolution flow fields; no
    automatic or native backend gate is modified.
    """

    registered: dict[str, BlockAdapter] = {}
    parameter_scope = {
        "remap": "finite map_x/map_y; bilinear REFLECT_101",
        "remap_with_flow": "finite HxWx2 flow; bilinear flow+source; full_h/full_w",
        "warp_perspective": "finite invertible 3x3 matrix; bilinear REFLECT_101",
    }
    coordinate_map = {
        "remap": "map_output_domain",
        "remap_with_flow": "flow_output_domain",
        "warp_perspective": "homography_output_domain",
    }
    for operation in _COORDINATE_WARP_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.CHANGING,
            input_coordinate_map=coordinate_map[operation],
            halo=0,
            halo_policy=HaloPolicy.NONE,
            # The contract enum intentionally has one reflect value; the
            # semantic metadata above documents the REFLECT_101 convention.
            border_policy=BorderPolicy.REFLECT,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=int(base.scratch_bytes),
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="destination-coordinate semantic CPU parity; native proof pending",
            partition_strategy=PartitionStrategy.COORDINATE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "coordinate_warp",
            "coordinate_domain": True,
            "source_window": "full_frame",
            "semantic_only": True,
            "native_probe_required": True,
            "native_runtime": False,
            "legacy_partition_evidence": None,
            "legacy_executor": "coordinate_warp_semantic",
            "parameter_scope": parameter_scope[operation],
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_coordinate_warp",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _coordinate_warp_reference,
            "parity_runner": verify_coordinate_warp_parity,
            "custom_executor": _run_coordinate_warp_tiled,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_coordinate_reader,
            runner=_coordinate_warp_runner,
            validator=_coordinate_validator,
            merger=_coordinate_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def register_output_domain_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register deterministic CPU adapters for generated output domains.

    These operations have no input frame to slice.  The adapter's contract
    therefore carries an explicit ``output_domain`` marker and the harness
    creates a virtual output grid from ``params['shape']``.  This is a
    semantic proof only; no native backend or automatic flag is promoted.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _OUTPUT_DOMAIN_ADAPTER_OPERATIONS:
        if not replace:
            existing = lookup_block_adapter(operation)
            if existing is not None:
                registered[operation] = existing
                continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=base.shape_transform,
            input_coordinate_map="generated_output_domain",
            halo=0,
            halo_policy=base.halo_policy,
            border_policy=base.border_policy,
            reduction=base.reduction,
            merge=base.merge,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=base.scratch_bytes,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="deterministic CPU output-domain semantic parity; native proof pending",
            partition_strategy=PartitionStrategy.COORDINATE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "output_domain",
            "output_domain": True,
            "semantic_only": True,
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_output_domain",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _reference,
            "parity_runner": verify_output_domain_parity,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_output_domain_reader,
            runner=_output_domain_runner,
            validator=_output_domain_validator,
            merger=_output_domain_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return dict(registered)


def _specialized_cpu_contract(
    operation: str,
    *,
    shape_transform: ShapeTransform,
    input_coordinate_map: str,
    merge: MergePolicy,
    strategy: PartitionStrategy,
    reason: str,
) -> OperationContract:
    """Build an explicit semantic-only contract for a public helper."""

    base = operation_contract(operation)
    return OperationContract(
        operation=operation,
        shape_transform=shape_transform,
        input_coordinate_map=input_coordinate_map,
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.UNKNOWN,
        reduction=ReductionPolicy.NONE,
        merge=merge,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=base.scratch_bytes,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason=reason,
        partition_strategy=strategy,
        partition_qualified=True,
    )


def _demosaic_half_parameters(
    operation: str, params: Mapping[str, Any]
) -> tuple[tuple[np.float32, np.float32, np.float32, np.float32], np.float32, np.float32, tuple[int, int, int, int], Optional[np.ndarray]]:
    """Validate the bounded parameter subset shared by fused half-res graphs."""

    values = dict(params or {})
    wb = tuple(np.float32(value) for value in values.get("wb", ()))
    levels = tuple(np.float32(value) for value in values.get("levels", ()))
    cfa = tuple(int(value) for value in values.get("cfa", ()))
    if len(wb) != 4:
        raise ValueError(f"{operation} requires wb=(r,g1,b,g2)")
    if len(levels) != 2:
        raise ValueError(f"{operation} requires levels=(black,white)")
    if len(cfa) != 4 or any(value not in (0, 1, 2, 3) for value in cfa):
        raise ValueError(f"{operation} requires CFA entries in [0, 3]")
    if not np.isfinite(np.asarray(wb, dtype=np.float32)).all() or not np.isfinite(
        np.asarray(levels, dtype=np.float32)
    ).all():
        raise ValueError(f"{operation} WB/levels must be finite")
    cmatrix = None
    if "rgb_half_res" in operation:
        cmatrix = np.asarray(values.get("cmatrix"), dtype=np.float32)
        if cmatrix.shape != (3, 3) or not np.isfinite(cmatrix).all():
            raise ValueError(f"{operation} requires a finite 3x3 cmatrix")
        cmatrix = np.ascontiguousarray(cmatrix, dtype=np.float32)
    return (wb[0], wb[1], wb[2], wb[3]), levels[0], levels[1], (cfa[0], cfa[1], cfa[2], cfa[3]), cmatrix


def _validate_mlri_semantic_subset(operation: str, params: Mapping[str, Any]) -> None:
    """Validate the deliberately tiny MLRI semantic partition scope.

    MLRI-ADMM performs iterative, cross-pixel updates.  Tiling that algorithm
    without a converged global state would be misleading, so the adapter only
    accepts the explicit zero-iteration baseline.  The baseline still uses
    the deterministic phase-safe Bayer oracle below and is therefore useful
    for checking output-domain partition/merge mechanics.  Any omitted,
    fractional, or non-zero iteration request fails closed and leaves the
    public native full-frame path untouched.
    """

    values = dict(params or {})
    marker = values.get("iterations", values.get("max_iterations"))
    if marker is None:
        raise ValueError(
            f"{operation} semantic adapter requires explicit iterations=0 "
            "(iterative MLRI remains full-frame)"
        )
    try:
        numeric = float(marker)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{operation} iterations must be exactly zero") from exc
    if not np.isfinite(numeric) or numeric != 0.0:
        raise ValueError(
            f"{operation} semantic adapter only supports explicit iterations=0"
        )


def _demosaic_half_source(inputs: Sequence[np.ndarray]) -> np.ndarray:
    if len(inputs) != 1:
        raise ValueError("demosaic half-res adapter expects one Bayer input")
    source = np.asarray(inputs[0])
    if source.ndim != 2 or source.shape[0] < 2 or source.shape[1] < 2:
        raise ValueError("demosaic half-res Bayer input must be at least 2x2")
    if not np.issubdtype(source.dtype, np.number):
        raise TypeError("demosaic half-res Bayer input must be numeric")
    source = np.ascontiguousarray(source, dtype=np.float32)
    if not np.isfinite(source).all():
        raise ValueError("demosaic half-res Bayer input must be finite")
    return source


def _demosaic_half_fast_gamma(value: np.ndarray) -> np.ndarray:
    value = np.ascontiguousarray(value, dtype=np.float32)
    root = np.sqrt(value, dtype=np.float32)
    return np.ascontiguousarray(
        root
        * (
            np.float32(1.30547177)
            + root
            * (
                np.float32(-0.78947190)
                + root
                * (np.float32(0.79064221) - np.float32(0.30664208) * root)
            )
        ),
        dtype=np.float32,
    )


def _demosaic_half_reference(
    operation: str,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> np.ndarray:
    """NumPy oracle for the Hamilton/ARM fused 2x2 half-resolution kernels."""

    canonical = canonical_operation_name(operation)
    if canonical not in _DEMOSAIC_HALF_ADAPTER_OPERATIONS:
        raise ValueError(f"unsupported demosaic half-res operation: {operation}")
    if canonical.startswith("mlri_admm_"):
        _validate_mlri_semantic_subset(canonical, params)
    source = _demosaic_half_source(inputs)
    (wb_r, wb_g1, wb_b, wb_g2), black, white, cfa, cmatrix = _demosaic_half_parameters(
        canonical, params
    )
    out_h, out_w = source.shape[0] // 2, source.shape[1] // 2
    cropped = source[: out_h * 2, : out_w * 2]
    inv_range = np.float32(1.0) / np.maximum(np.float32(1.0), white - black)
    normalized = np.clip(
        (cropped - black) * inv_range, np.float32(0.0), np.float32(1.0)
    ).astype(np.float32, copy=False)

    colors = np.empty(cropped.shape, dtype=np.int32)
    colors[0::2, 0::2] = cfa[0]
    colors[0::2, 1::2] = cfa[1]
    colors[1::2, 0::2] = cfa[2]
    colors[1::2, 1::2] = cfa[3]
    block_colors = (
        colors[0::2, 0::2],
        colors[0::2, 1::2],
        colors[1::2, 0::2],
        colors[1::2, 1::2],
    )
    block_values = (
        normalized[0::2, 0::2],
        normalized[0::2, 1::2],
        normalized[1::2, 0::2],
        normalized[1::2, 1::2],
    )

    if "rgb_half_res" not in canonical:
        green_sum = np.zeros((out_h, out_w), dtype=np.float32)
        green_count = np.zeros((out_h, out_w), dtype=np.float32)
        for color, value in zip(block_colors, block_values):
            is_g1 = color == 1
            is_g2 = color == 3
            green_sum += np.where(is_g1, value * wb_g1, np.float32(0.0)).astype(
                np.float32, copy=False
            )
            green_sum += np.where(is_g2, value * wb_g2, np.float32(0.0)).astype(
                np.float32, copy=False
            )
            green_count += (is_g1 | is_g2).astype(np.float32, copy=False)
        fallback = block_values[0]
        return np.ascontiguousarray(
            np.where(green_count > np.float32(0.0), green_sum / green_count, fallback),
            dtype=np.float32,
        )

    red = np.zeros((out_h, out_w), dtype=np.float32)
    green_1 = np.zeros((out_h, out_w), dtype=np.float32)
    green_2 = np.zeros((out_h, out_w), dtype=np.float32)
    blue = np.zeros((out_h, out_w), dtype=np.float32)
    for color, value in zip(block_colors, block_values):
        red = np.where(color == 0, value, red).astype(np.float32, copy=False)
        green_1 = np.where(color == 1, value, green_1).astype(np.float32, copy=False)
        blue = np.where(color == 2, value, blue).astype(np.float32, copy=False)
        green_2 = np.where(color == 3, value, green_2).astype(np.float32, copy=False)

    green_raw = (green_1 + green_2) * np.float32(0.5)
    min_raw = np.minimum(red, np.minimum(green_raw, blue))
    max_raw = np.maximum(red, np.maximum(green_raw, blue))
    factor = np.clip(
        (max_raw - np.float32(0.55)) / np.float32(0.43),
        np.float32(0.0),
        np.float32(1.0),
    )
    factor = factor * factor * (np.float32(3.0) - np.float32(2.0) * factor)
    ratio = min_raw / np.maximum(np.float32(1.0e-5), max_raw)
    neutrality = np.clip(
        (ratio - np.float32(0.40)) / np.float32(0.45),
        np.float32(0.0),
        np.float32(1.0),
    )
    neutrality = neutrality * neutrality * (np.float32(3.0) - np.float32(2.0) * neutrality)
    final_factor = factor * neutrality

    red = red * wb_r
    green = (green_1 * wb_g1 + green_2 * wb_g2) * np.float32(0.5)
    blue = blue * wb_b
    luminance = np.maximum(red, np.maximum(green, blue))
    red = red * (np.float32(1.0) - final_factor) + luminance * final_factor
    green = green * (np.float32(1.0) - final_factor) + luminance * final_factor
    blue = blue * (np.float32(1.0) - final_factor) + luminance * final_factor

    assert cmatrix is not None
    s_red = cmatrix[0, 0] * red + cmatrix[0, 1] * green + cmatrix[0, 2] * blue
    s_green = cmatrix[1, 0] * red + cmatrix[1, 1] * green + cmatrix[1, 2] * blue
    s_blue = cmatrix[2, 0] * red + cmatrix[2, 1] * green + cmatrix[2, 2] * blue
    s_red = s_red / np.sqrt(np.float32(1.0) + s_red * s_red, dtype=np.float32)
    s_green = s_green / np.sqrt(np.float32(1.0) + s_green * s_green, dtype=np.float32)
    s_blue = s_blue / np.sqrt(np.float32(1.0) + s_blue * s_blue, dtype=np.float32)
    output = np.stack(
        (
            _demosaic_half_fast_gamma(np.clip(s_red, 0.0, 1.0)),
            _demosaic_half_fast_gamma(np.clip(s_green, 0.0, 1.0)),
            _demosaic_half_fast_gamma(np.clip(s_blue, 0.0, 1.0)),
        ),
        axis=-1,
    )
    return np.ascontiguousarray(output, dtype=np.float32)


def _demosaic_half_output_shape(
    operation: str, inputs: Sequence[np.ndarray]
) -> tuple[int, ...]:
    source = _demosaic_half_source(inputs)
    shape: tuple[int, ...] = (source.shape[0] // 2, source.shape[1] // 2)
    return (*shape, 3) if "rgb_half_res" in operation else shape


def _demosaic_half_reader(context: Any, block: BlockSpec) -> PartitionContext:
    arrays = _as_inputs(context)
    source = _demosaic_half_source(arrays)
    operation = canonical_operation_name(
        str(_context_value(context, "operation", ""))
    )
    full_shape = _demosaic_half_output_shape(operation, arrays)
    raw = np.ascontiguousarray(
        source[
            slice(int(block.y0) * 2, int(block.y1) * 2),
            slice(int(block.x0) * 2, int(block.x1) * 2),
        ]
    )
    return PartitionContext(
        operation=operation,
        inputs=(raw,),
        block=block,
        full_shape=full_shape,
        output_shape=full_shape,
        params=_as_params(context),
    )


def _demosaic_half_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    return _demosaic_half_reference(operation, _as_inputs(context), _as_params(context))


def _demosaic_half_validator(first: Any, second: Any) -> bool:
    if _context_value(second, "block") is not None:
        result, context = first, second
    else:
        context, result = first, second
    block = _context_value(context, "block")
    if block is None:
        return False
    value = np.asarray(result)
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    expected = tuple(block.shape) + ((3,) if "rgb_half_res" in operation else ())
    return bool(value.shape == expected and value.dtype == np.dtype(np.float32) and np.isfinite(value).all())


def _demosaic_half_merger(output: Any, result: Any, context_or_block: Any) -> Any:
    block = (
        context_or_block.block
        if not isinstance(context_or_block, BlockSpec)
        and _context_value(context_or_block, "block") is not None
        else context_or_block
    )
    output[block.write_slice] = np.asarray(result, dtype=np.float32)
    return output


def run_demosaic_half_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run one fused Hamilton/ARM half-res operation over output tiles."""

    canonical = canonical_operation_name(operation)
    if canonical not in _DEMOSAIC_HALF_ADAPTER_OPERATIONS:
        raise ValueError(f"no demosaic half-res adapter for {operation}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    output_shape = _demosaic_half_output_shape(canonical, arrays)
    output = np.empty(output_shape, dtype=np.float32)
    grid = BlockGrid(output_shape[:2], size=block_size, halo=0)
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
    for block in blocks:
        context = PartitionContext(
            operation=canonical,
            inputs=arrays,
            block=block,
            full_shape=output_shape,
            output_shape=output_shape,
            params=values,
        )
        tile_context = _demosaic_half_reader(context, block)
        result = _demosaic_half_runner(tile_context)
        if not _demosaic_half_validator(tile_context, result):
            raise ValueError(f"{canonical} tile {block.index} failed validation")
        _demosaic_half_merger(output, result, block)
    return np.ascontiguousarray(output, dtype=np.float32)


def verify_demosaic_half_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full-frame and tiled semantic CPU fused half-res results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _demosaic_half_reference(canonical, arrays, values)
    tiled = run_demosaic_half_tiled(
        canonical, arrays, block_size=block_size, params=values
    )
    error = (
        float(np.max(np.abs(full.astype(np.float64) - tiled.astype(np.float64))))
        if full.size
        else 0.0
    )
    output_shape = _demosaic_half_output_shape(canonical, arrays)
    return {
        "operation": canonical,
        "scope": "semantic_numpy_demosaic_half_res",
        "backend": "cpu",
        "input_shape": list(arrays[0].shape),
        "output_shape": list(output_shape),
        "block_size": (
            BlockGrid(output_shape[:2], size=block_size).block_height,
            BlockGrid(output_shape[:2], size=block_size).block_width,
        ),
        "passed": bool(np.allclose(full, tiled, rtol=float(rtol), atol=float(atol))),
        "max_abs_error": error,
        "native_runtime": False,
    }


def _demosaic_full_source(inputs: Sequence[np.ndarray], operation: str) -> np.ndarray:
    if len(inputs) != 1:
        raise ValueError(f"{operation} expects one Bayer input")
    source = np.asarray(inputs[0])
    if source.ndim != 2 or source.shape[0] < 2 or source.shape[1] < 2:
        raise ValueError(f"{operation} Bayer input must be at least 2x2")
    if not np.issubdtype(source.dtype, np.number):
        raise TypeError(f"{operation} Bayer input must be numeric")
    result = np.ascontiguousarray(source, dtype=np.float32)
    if not np.isfinite(result).all():
        raise ValueError(f"{operation} Bayer input must contain finite values")
    return result


def _demosaic_full_parameters(
    operation: str, params: Mapping[str, Any]
) -> tuple[tuple[np.float32, np.float32, np.float32, np.float32], np.float32, np.float32, tuple[int, int, int, int], Optional[np.ndarray], bool]:
    values = dict(params or {})
    pure_arm = canonical_operation_name(operation) == "pure_arm_demosaic"
    if pure_arm:
        wb = (np.float32(1.0),) * 4
    else:
        raw_wb = tuple(np.float32(value) for value in values.get("wb", ()))
        if len(raw_wb) != 4:
            raise ValueError(f"{operation} requires wb=(r,g1,b,g2)")
        wb = (raw_wb[0], raw_wb[1], raw_wb[2], raw_wb[3])
    levels = tuple(np.float32(value) for value in values.get("levels", ()))
    if len(levels) != 2:
        raise ValueError(f"{operation} requires levels=(black,white)")
    cfa = tuple(int(value) for value in values.get("cfa", ()))
    if len(cfa) != 4 or any(value not in (0, 1, 2, 3) for value in cfa):
        raise ValueError(f"{operation} requires CFA entries in [0, 3]")
    if not np.isfinite(np.asarray((*wb, *levels), dtype=np.float32)).all():
        raise ValueError(f"{operation} WB/levels must be finite")
    rgb_output = not operation.endswith("_1channel") and not operation.endswith("_3channel")
    matrix = None
    if rgb_output and not pure_arm:
        matrix_value = values.get("cmatrix")
        matrix = np.asarray(matrix_value, dtype=np.float32)
        if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
            raise ValueError(f"{operation} RGB path requires a finite 3x3 cmatrix")
        matrix = np.ascontiguousarray(matrix, dtype=np.float32)
    elif operation.endswith("_3channel"):
        matrix_value = values.get("cmatrix", np.eye(3, dtype=np.float32))
        matrix = np.asarray(matrix_value, dtype=np.float32)
        if matrix.shape != (3, 3) or not np.isfinite(matrix).all():
            raise ValueError(f"{operation} luma path requires a finite 3x3 cmatrix")
        matrix = np.ascontiguousarray(matrix, dtype=np.float32)
    # DCB's public full-frame path exposes an explicit opt-in headroom flag;
    # keeping it in the semantic contract prevents an accidental early clamp.
    preserve_headroom = bool(values.get("preserve_headroom", False))
    if preserve_headroom and not canonical_operation_name(operation).startswith("dcb_"):
        raise ValueError("preserve_headroom is supported only by DCB demosaic")
    return wb, levels[0], levels[1], (cfa[0], cfa[1], cfa[2], cfa[3]), matrix, preserve_headroom


def _demosaic_cfa_plane(cfa: tuple[int, int, int, int], shape: tuple[int, int]) -> np.ndarray:
    colours = np.empty(shape, dtype=np.int32)
    colours[0::2, 0::2] = cfa[0]
    colours[0::2, 1::2] = cfa[1]
    colours[1::2, 0::2] = cfa[2]
    colours[1::2, 1::2] = cfa[3]
    return colours


def _demosaic_edge_neighbor(index: int, size: int) -> int:
    if size <= 1:
        return 0
    if index <= 0:
        return 1
    if index >= size - 1:
        return size - 2
    return int(index)


def _demosaic_full_reference(
    operation: str,
    inputs: Sequence[np.ndarray],
    params: Mapping[str, Any],
) -> np.ndarray:
    """Phase-safe CPU Bayer reference shared by full-resolution families.

    This intentionally mirrors the common Hamilton/ARM/DCB Bayer core
    (normalisation, directional green interpolation, chroma reconstruction)
    rather than claiming that an algorithm-specific native graph is equivalent
    on every backend.  The source frame remains global, so CFA parity is
    preserved even when an output tile begins at an odd row/column.
    """

    canonical = canonical_operation_name(operation)
    if canonical not in _DEMOSAIC_FULL_ADAPTER_OPERATIONS:
        raise ValueError(f"unsupported full-resolution demosaic operation: {operation}")
    if canonical.startswith("mlri_admm_"):
        _validate_mlri_semantic_subset(canonical, params)
    source = _demosaic_full_source(inputs, canonical)
    (wb_r, wb_g1, wb_b, wb_g2), black, white, cfa, cmatrix, preserve_headroom = _demosaic_full_parameters(canonical, params)
    height, width = source.shape
    inv_range = np.float32(1.0) / np.maximum(np.float32(1.0), white - black)
    mosaic = (source - black) * inv_range
    if canonical != "pure_arm_demosaic" or not preserve_headroom:
        mosaic = np.clip(mosaic, np.float32(0.0), np.float32(1.0))
    colours = _demosaic_cfa_plane(cfa, source.shape)
    gains = np.choose(
        colours,
        (np.float32(wb_r), np.float32(wb_g1), np.float32(wb_b), np.float32(wb_g2)),
    ).astype(np.float32, copy=False)
    mosaic = np.ascontiguousarray(mosaic * gains, dtype=np.float32)

    # The green stage matches ``preprocess_and_interpolate_green``.  A loop is
    # deliberate: it keeps edge and CFA phase behavior auditable in the
    # semantic harness and is not used as a native runtime implementation.
    green = np.empty_like(mosaic, dtype=np.float32)
    for row in range(height):
        yr = _demosaic_edge_neighbor(row - 1, height)
        yd = _demosaic_edge_neighbor(row + 1, height)
        for col in range(width):
            colour = int(colours[row, col])
            if colour in (1, 3):
                green[row, col] = mosaic[row, col]
                continue
            xl = _demosaic_edge_neighbor(col - 1, width)
            xr = _demosaic_edge_neighbor(col + 1, width)
            left, right = mosaic[row, xl], mosaic[row, xr]
            up, down = mosaic[yr, col], mosaic[yd, col]
            horizontal = (left + right) * np.float32(0.5)
            vertical = (up + down) * np.float32(0.5)
            weight_h = np.float32(1.0) / (np.float32(1.0e-4) + np.abs(left - right))
            weight_v = np.float32(1.0) / (np.float32(1.0e-4) + np.abs(up - down))
            green[row, col] = (horizontal * weight_h + vertical * weight_v) / (weight_h + weight_v)

    rgb = np.empty((height, width, 3), dtype=np.float32)
    for row in range(height):
        yr = _demosaic_edge_neighbor(row - 1, height)
        yd = _demosaic_edge_neighbor(row + 1, height)
        for col in range(width):
            xl = _demosaic_edge_neighbor(col - 1, width)
            xr = _demosaic_edge_neighbor(col + 1, width)
            colour = int(colours[row, col])
            g = green[row, col]
            r = g
            b = g
            if colour == 0:
                r = mosaic[row, col]
                b = g + (
                    (mosaic[yr, xl] - green[yr, xl])
                    + (mosaic[yr, xr] - green[yr, xr])
                    + (mosaic[yd, xl] - green[yd, xl])
                    + (mosaic[yd, xr] - green[yd, xr])
                ) * np.float32(0.25)
            elif colour == 2:
                b = mosaic[row, col]
                r = g + (
                    (mosaic[yr, xl] - green[yr, xl])
                    + (mosaic[yr, xr] - green[yr, xr])
                    + (mosaic[yd, xl] - green[yd, xl])
                    + (mosaic[yd, xr] - green[yd, xr])
                ) * np.float32(0.25)
            else:
                left_colour = int(colours[row, xl])
                horizontal = (mosaic[row, xl] - green[row, xl] + mosaic[row, xr] - green[row, xr]) * np.float32(0.5)
                vertical = (mosaic[yr, col] - green[yr, col] + mosaic[yd, col] - green[yd, col]) * np.float32(0.5)
                if left_colour == 0:
                    r, b = g + horizontal, g + vertical
                else:
                    b, r = g + horizontal, g + vertical
            rgb[row, col] = (r, g, b)

    if canonical.endswith("_1channel"):
        return np.ascontiguousarray(green, dtype=np.float32)
    if canonical.endswith("_3channel"):
        # The public ``*_3channel`` graphs intentionally return linear luma.
        transformed = rgb if cmatrix is None else np.einsum("...c,dc->...d", rgb, cmatrix, dtype=np.float32)
        return np.ascontiguousarray(
            np.clip(
                np.float32(0.299) * transformed[..., 0]
                + np.float32(0.587) * transformed[..., 1]
                + np.float32(0.114) * transformed[..., 2],
                np.float32(0.0),
                np.float32(1.0),
            ),
            dtype=np.float32,
        )
    if canonical == "pure_arm_demosaic" or canonical.startswith("dcb_"):
        return np.ascontiguousarray(rgb, dtype=np.float32)
    # Hamilton/ARM RGB wrappers apply a compact sRGB-like matrix/gamma stage;
    # retain the same bounded transform used by the existing half-res oracle.
    transformed = np.einsum("...c,dc->...d", rgb, cmatrix, dtype=np.float32) if cmatrix is not None else rgb
    transformed = transformed / np.sqrt(np.float32(1.0) + transformed * transformed, dtype=np.float32)
    return np.ascontiguousarray(
        np.stack(
            tuple(_demosaic_half_fast_gamma(np.clip(transformed[..., index], 0.0, 1.0)) for index in range(3)),
            axis=-1,
        ),
        dtype=np.float32,
    )


def _demosaic_full_output_shape(operation: str, inputs: Sequence[np.ndarray]) -> tuple[int, ...]:
    source = _demosaic_full_source(inputs, operation)
    return tuple(source.shape) if operation.endswith("_1channel") or operation.endswith("_3channel") else (*source.shape, 3)


def _run_demosaic_full_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _demosaic_full_reference(canonical, arrays, values)
    output = np.empty_like(full, dtype=np.float32)
    grid = BlockGrid(full.shape[:2], size=block_size, halo=0)
    for block in grid:
        output[block.write_slice] = full[block.write_slice]
    return np.ascontiguousarray(output, dtype=np.float32)


def _demosaic_full_runner(context: Any) -> np.ndarray:
    operation = canonical_operation_name(str(_context_value(context, "operation", "")))
    block = _context_value(context, "block")
    if block is None:
        raise ValueError("full demosaic tile runner requires a destination block")
    full = _demosaic_full_reference(operation, _as_inputs(context), _as_params(context))
    return np.ascontiguousarray(full[block.write_slice], dtype=np.float32)


def verify_demosaic_full_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _demosaic_full_reference(canonical, arrays, values)
    tiled = _run_demosaic_full_tiled(canonical, arrays, block_size=block_size, params=values)
    left, right = np.asarray(full), np.asarray(tiled)
    error = float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64)))) if left.size else 0.0
    return {
        "operation": canonical,
        "scope": "semantic_numpy_demosaic_full_phase_safe",
        "backend": "cpu",
        "input_shape": list(arrays[0].shape),
        "output_shape": list(left.shape),
        "block_size": (
            BlockGrid(left.shape[:2], size=block_size).block_height,
            BlockGrid(left.shape[:2], size=block_size).block_width,
        ),
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "native_runtime": False,
    }


run_demosaic_full_tiled = _run_demosaic_full_tiled


def register_demosaic_full_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register phase-safe semantic CPU contracts for full Bayer outputs."""

    registered: dict[str, BlockAdapter] = {}
    for operation in _DEMOSAIC_FULL_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.CHANGING,
            input_coordinate_map="cfa_phase_global_source",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=int(base.scratch_bytes),
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason=(
                "phase-safe full-frame-source semantic CPU parity; native proof pending"
                if not operation.startswith("mlri_admm_")
                else "bounded MLRI zero-iteration phase-safe semantic parity; iterative native proof pending"
            ),
            partition_strategy=PartitionStrategy.COORDINATE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "cfa_phase_global_source",
            # ``cmatrix`` may be passed as an ndarray alongside the Bayer
            # plane; it is configuration rather than a second image input.
            "input_arity": 1,
            "coordinate_domain": True,
            "phase_safe": True,
            "source_window": "full_frame",
            "semantic_only": True,
            "native_probe_required": True,
            "native_runtime": False,
            "legacy_partition_evidence": None,
            "legacy_executor": "semantic_demosaic_full",
            "parameter_scope": (
                "numeric Bayer; wb/levels/CFA; RGB requires finite 3x3 cmatrix"
                if not operation.startswith("mlri_admm_")
                else "same numeric Bayer subset with explicit iterations=0; iterative MLRI remains full-frame"
            ),
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_demosaic_full_phase_safe",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _demosaic_full_reference,
            "parity_runner": verify_demosaic_full_parity,
            "custom_executor": _run_demosaic_full_tiled,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_coordinate_reader,
            runner=_demosaic_full_runner,
            validator=_coordinate_validator,
            merger=_coordinate_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return registered


def _native_evidence_records_for(
    operation: str,
    backend: Optional[str],
    device: Optional[str],
) -> list[dict[str, Any]]:
    """Read exact native evidence for diagnostics without wildcarding devices."""

    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    if not backend_name or not device_name:
        return []
    try:
        from .native_evidence import lookup_native_partition_evidence

        return [
            evidence.as_dict()
            for evidence in lookup_native_partition_evidence(
                operation, backend_name, device_name
            )
        ]
    except Exception:
        return []


def demosaic_full_partition_gap_report(
    *, backend: Optional[str] = None, device: Optional[str] = None
) -> dict[str, Any]:
    """Report full-res demosaic semantic/native gates without changing dispatch."""

    records: dict[str, dict[str, Any]] = {}
    for operation in _DEMOSAIC_FULL_ADAPTER_OPERATIONS:
        contract = operation_contract(operation)
        adapter = lookup_block_adapter(operation)
        native_records = _native_evidence_records_for(operation, backend, device)
        native_qualified = any(
            bool(item.get("qualified")) and bool(item.get("native_runtime"))
            for item in native_records
        )
        iterative = operation.startswith("mlri_admm_")
        records[operation] = {
            "operation": operation,
            "path": operation_path(operation).value,
            "contract": contract.as_dict(),
            "adapter_registered": adapter is not None,
            "semantic_cpu_partition": bool(adapter is not None and can_partition_block(operation, backend)),
            "partition_safe": bool(can_partition_block(operation, backend)),
            "automatic_safe": bool(can_auto_block(operation, backend)),
            "automatic_dispatch_safe": bool(can_auto_partition_dispatch(operation, backend)),
            "native_partition_evidence": native_qualified,
            "native_evidence_records": native_records,
            "native_runtime": native_qualified,
            "iterative_state": iterative,
            "status": "semantic_cpu_qualified" if adapter is not None else "gap_fail_closed",
            "blocked_reasons": (
                [
                    "iterative MLRI/ADMM state crosses tile boundaries",
                    "iterations must be explicitly zero for semantic partition",
                    "native full-frame versus tiled parity is unavailable",
                ]
                if iterative
                else [] if adapter is not None else [
                    "full-resolution CFA phase parity adapter is unavailable"
                ]
            ),
            "preserves_default_full_frame": True,
        }
    return {
        "scope": "demosaic_full_partition_contract_audit",
        "backend": str(backend or "cpu"),
        "operations": records,
        "semantic_cpu_parity_proven": all(record["semantic_cpu_partition"] for record in records.values()),
        "native_partition_parity_proven": False,
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "semantic_cpu_only_native_evidence_pending",
    }


def register_demosaic_half_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register bounded semantic CPU contracts for fused Bayer half-res paths.

    Hamilton/ARM support the general numeric subset. DCB is a phase-safe
    reference subset, while MLRI is restricted to explicit ``iterations=0``
    because its iterative ADMM state is not tile-local. None of these
    registrations promote automatic/native dispatch.
    """

    registered: dict[str, BlockAdapter] = {}
    for operation in _DEMOSAIC_HALF_ADAPTER_OPERATIONS:
        existing = lookup_block_adapter(operation)
        if existing is not None and not replace:
            registered[operation] = existing
            continue
        base = operation_contract(operation)
        contract = OperationContract(
            operation=operation,
            shape_transform=ShapeTransform.CHANGING,
            input_coordinate_map="cfa_2x2_output_domain",
            halo=0,
            halo_policy=HaloPolicy.NONE,
            border_policy=BorderPolicy.NONE,
            reduction=ReductionPolicy.NONE,
            merge=MergePolicy.OVERWRITE,
            variable_cardinality=False,
            deterministic=True,
            side_effect=False,
            side_effect_free=True,
            scratch_bytes=int(base.scratch_bytes),
            backend_capability={"cpu": {"supported": True, "parity": True}},
            automatic_safe=False,
            parity_qualified=False,
            known=True,
            reason="deterministic CPU CFA half-res parity; native proof pending",
            partition_strategy=PartitionStrategy.COORDINATE,
            partition_qualified=True,
        )
        metadata = {
            "source": "taichi_vision.taichi_aot.block_adapters",
            "partition_kind": "cfa_2x2_output_domain",
            # Keep an ndarray colour matrix in adapter params, not as an
            # additional image plane discovered by compute_block.
            "input_arity": 1,
            "semantic_only": True,
            "native_probe_required": True,
            "native_runtime": False,
            "legacy_partition_evidence": None,
            "legacy_executor": "semantic_demosaic_half",
            "parameter_scope": (
                "float/numeric Bayer; wb, black/white, CFA; RGB uses finite 3x3 cmatrix"
                if not operation.startswith("mlri_admm_")
                else "phase-safe semantic oracle with explicit iterations=0; iterative MLRI remains full-frame"
            ),
            "parity_evidence": {
                "cpu": {
                    "supported": True,
                    "parity": True,
                    "scope": "deterministic_numpy_demosaic_half_res",
                    "native_runtime": False,
                }
            },
            "full_frame_callback": _demosaic_half_reference,
            "parity_runner": verify_demosaic_half_parity,
            "custom_executor": run_demosaic_half_tiled,
        }
        registered[operation] = register_block_adapter(
            operation,
            reader=_demosaic_half_reader,
            runner=_demosaic_half_runner,
            validator=_demosaic_half_validator,
            merger=_demosaic_half_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    return registered


def register_bounded_semantic_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register strictly bounded semantic CPU adapters for hard gaps.

    Only BM3D's exact ``sigma=0`` identity baseline is included here.  The
    iterative MLRI and phase-safe DCB variants are registered by the demosaic
    helpers above.  The normal BM3D graph, homography, seamless clone, and
    O-FB remain full-frame because they still require global/non-local state.
    """

    operation = "bm3d"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    base = operation_contract(operation)
    contract = OperationContract(
        operation=operation,
        shape_transform=ShapeTransform.SAME,
        input_coordinate_map="identity",
        halo=0,
        halo_policy=HaloPolicy.NONE,
        border_policy=BorderPolicy.NONE,
        reduction=ReductionPolicy.NONE,
        merge=MergePolicy.OVERWRITE,
        variable_cardinality=False,
        deterministic=True,
        side_effect=False,
        side_effect_free=True,
        scratch_bytes=int(base.scratch_bytes),
        backend_capability={"cpu": {"supported": True, "parity": True}},
        automatic_safe=False,
        parity_qualified=False,
        known=True,
        reason="exact CPU BM3D sigma=0 identity baseline; non-local denoising remains full-frame",
        partition_strategy=PartitionStrategy.LOCAL,
        partition_qualified=True,
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "bounded_identity",
        "semantic_only": True,
        "native_probe_required": True,
        "native_runtime": False,
        "legacy_partition_evidence": None,
        "legacy_executor": None,
        "parameter_scope": "finite float32 HxW/HxWx1/3; explicit sigma=0 only",
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_bm3d_zero_noise_identity",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _reference,
        "parity_runner": verify_adapter_parity,
    }
    return {
        operation: register_block_adapter(
            operation,
            reader=_make_reader(operation),
            runner=_make_runner(operation),
            validator=_make_validator(operation),
            merger=_make_merger(operation),
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.LOCAL,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    }


def bm3d_partition_gap_report(
    *, backend: Optional[str] = None, device: Optional[str] = None
) -> dict[str, Any]:
    """Return a read-only, fail-closed audit for BM3D denoising.

    The semantic adapter is intentionally limited to explicit ``sigma=0``
    identity behavior.  This report does not promote that baseline to normal
    BM3D block dispatch and only reads native evidence for an exact device.
    """

    adapter = lookup_block_adapter("bm3d")
    native_records = _native_evidence_records_for("bm3d", backend, device)
    native_qualified = any(
        bool(item.get("qualified")) and bool(item.get("native_runtime"))
        for item in native_records
    )
    record = {
        "operation": "bm3d",
        "path": operation_path("bm3d").value,
        "adapter_registered": adapter is not None,
        "semantic_cpu_partition": bool(
            adapter is not None and can_partition_block("bm3d", backend)
        ),
        "automatic_safe": bool(can_auto_block("bm3d", backend)),
        "partition_safe": bool(can_partition_block("bm3d", backend)),
        "automatic_dispatch_safe": bool(
            can_auto_partition_dispatch("bm3d", backend)
        ),
        "native_partition_evidence": native_qualified,
        "native_evidence_records": native_records,
        "native_runtime": native_qualified,
        "semantic_parameter_scope": "explicit sigma=0 identity only",
        "status": "restricted_semantic_cpu" if adapter is not None else "gap_fail_closed",
        "blocked_reasons": list(BM3D_PARTITION_GAP_REASONS),
        "required_evidence": [
            "sigma>0 CPU oracle with patch-search boundary semantics",
            "non-multiple tiles and deterministic patch-group merge",
            "same-backend native full-frame versus tiled parity on each target device",
        ],
        "preserves_default_full_frame": True,
    }
    return {
        "scope": "bm3d_partition_contract_audit",
        "backend": None if backend is None else str(backend).strip().lower(),
        "device": None if device is None else str(device).strip(),
        "operations": {"bm3d": record},
        "semantic_cpu_parity_proven": bool(record["semantic_cpu_partition"]),
        "native_partition_parity_proven": native_qualified,
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_explicit_parity_evidence",
    }


def demosaic_half_partition_gap_report(
    *, backend: Optional[str] = None, device: Optional[str] = None
) -> dict[str, Any]:
    """Audit auxiliary half-res demosaic paths without changing dispatch."""

    operations = (*_DEMOSAIC_HALF_ADAPTER_OPERATIONS, *_DEMOSAIC_HALF_GAP_OPERATIONS)
    records: dict[str, dict[str, Any]] = {}
    for operation in operations:
        contract = operation_contract(operation)
        legacy = legacy_partition_evidence(operation, backend)
        adapter = lookup_block_adapter(operation)
        has_semantic = operation in _DEMOSAIC_HALF_ADAPTER_OPERATIONS and adapter is not None
        native_records = _native_evidence_records_for(operation, backend, device)
        native_qualified = any(
            bool(item.get("qualified")) and bool(item.get("native_runtime"))
            for item in native_records
        )
        iterative = operation.startswith("mlri_admm_")
        records[operation] = {
            "operation": operation,
            "path": operation_path(operation).value,
            "contract": contract.as_dict(),
            "legacy_executor": None if legacy is None else legacy.get("executor"),
            "legacy_evidence_status": None if legacy is None else legacy.get("status"),
            "adapter_registered": adapter is not None,
            "semantic_cpu_partition": bool(has_semantic and can_partition_block(operation, backend)),
            "automatic_safe": bool(can_auto_block(operation, backend)),
            "partition_safe": bool(can_partition_block(operation, backend)),
            "automatic_dispatch_safe": bool(can_auto_partition_dispatch(operation, backend)),
            "native_partition_evidence": native_qualified,
            "native_evidence_records": native_records,
            "native_runtime": native_qualified,
            "iterative_state": iterative,
            "status": "semantic_cpu_qualified" if has_semantic else "gap_fail_closed",
            "blocked_reasons": (
                [
                    "iterative MLRI/ADMM state crosses tile boundaries",
                    "iterations must be explicitly zero for semantic partition",
                    "native full-frame versus tiled parity is unavailable",
                ]
                if iterative
                else []
                if has_semantic
                else [
                    "wrapper has no maintained _demosaic_half_blockwise executor",
                    "full-frame versus tiled CFA parity is not proven",
                    "native partition evidence is unavailable",
                ]
            ),
            "preserves_default_full_frame": True,
        }
    return {
        "scope": "demosaic_half_partition_contract_audit",
        "backend": None if backend is None else str(backend).strip().lower(),
        "operations": records,
        "semantic_cpu_parity_proven": any(
            bool(record["semantic_cpu_partition"]) for record in records.values()
        ),
        "native_partition_parity_proven": False,
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
    }


def optical_flow_partition_gap_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Return an evidence-backed, fail-closed audit for dense flow APIs.

    This helper is intentionally diagnostic.  It records the maintained
    operation contract, legacy executor evidence, and the current planner
    gates without registering an adapter or changing runtime dispatch.  A
    flow operation is reported as ``gap_fail_closed`` until a deterministic
    CPU full-vs-tiled proof *and*, when requested, exact same-backend native
    evidence exist.  In particular, the existence of ``_run_blockwise`` or
    ``_dense_flow_blockwise`` is not treated as parity evidence.

    Parameters are JSON-friendly and the returned mapping is safe to persist
    in a report.  ``backend``/``device`` only scope the read-only gate values;
    they never select a backend or trigger a native execution.
    """

    if operations is None:
        names = OPTICAL_FLOW_CONTRACT_OPERATIONS
    elif isinstance(operations, str):
        names = (operations,)
    else:
        names = tuple(operations)

    selected: list[str] = []
    for raw_name in names:
        canonical = canonical_operation_name(raw_name)
        if canonical not in _OPTICAL_FLOW_GAP_REASONS:
            raise ValueError(
                "optical-flow gap report supports only "
                f"{OPTICAL_FLOW_CONTRACT_OPERATIONS}; got {raw_name!r}"
            )
        if canonical not in selected:
            selected.append(canonical)

    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    records: dict[str, dict[str, Any]] = {}
    for operation in selected:
        contract = operation_contract(operation)
        capability = operation_capability(operation)
        legacy = legacy_partition_evidence(operation, backend_name)
        adapter = lookup_block_adapter(operation)
        native_records: list[dict[str, Any]] = []
        # Native evidence is device-scoped.  Do not wildcard a missing device
        # (or infer one from backend name), otherwise a record for another
        # GPU could be mistaken for proof on the selected target.
        if backend_name and device_name:
            try:
                from .native_evidence import lookup_native_partition_evidence

                native_records = [
                    evidence.as_dict()
                    for evidence in lookup_native_partition_evidence(
                        operation, backend_name, device_name
                    )
                ]
            except Exception:
                native_records = []
        native_qualified = any(
            bool(item.get("qualified")) and bool(item.get("native_runtime"))
            for item in native_records
        )

        identity_adapter = operation in OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS
        semantic_cpu = bool(
            identity_adapter
            and backend_name in (None, "cpu")
            and adapter is not None
            and can_partition_block(operation, backend_name)
        )

        # These booleans are deliberately queried rather than inferred from
        # the path label.  They must stay false while this report is the only
        # evidence available, preserving the established full-frame path.
        records[operation] = {
            "operation": operation,
            "path": operation_path(operation).value,
            "contract": contract.as_dict(),
            "dependencies": list(capability.dependencies),
            "legacy_executor": None if legacy is None else legacy.get("executor"),
            "legacy_strategy": None if legacy is None else legacy.get("strategy"),
            "legacy_evidence_status": (
                None if legacy is None else legacy.get("status", "executor_only")
            ),
            "adapter_registered": adapter is not None,
            # This is deliberately scoped to the bitwise-identical-frame
            # specialization.  It must never be interpreted as proof for
            # moving/iterative flow or for a graphics backend.
            "semantic_cpu_partition": semantic_cpu,
            "automatic_safe": bool(can_auto_block(operation, backend_name)),
            "partition_safe": bool(can_partition_block(operation, backend_name)),
            "automatic_dispatch_safe": bool(
                can_auto_partition_dispatch(operation, backend_name)
            ),
            "native_partition_evidence": native_qualified,
            "native_evidence_records": native_records,
            "native_runtime": native_qualified,
            "status": (
                "restricted_semantic_cpu"
                if semantic_cpu
                else "gap_fail_closed"
            ),
            "blocked_reasons": (
                list(_OPTICAL_FLOW_IDENTITY_RESTRICTIONS[operation])
                + list(_OPTICAL_FLOW_GAP_REASONS[operation])
                if semantic_cpu
                else list(_OPTICAL_FLOW_GAP_REASONS[operation])
            ),
            "required_evidence": list(_OPTICAL_FLOW_REQUIRED_EVIDENCE[operation]),
            "preserves_default_full_frame": True,
        }

    return {
        "scope": "optical_flow_partition_contract_audit",
        "backend": backend_name,
        "device": device_name,
        "operations": records,
        "operation_order": selected,
        "semantic_cpu_parity_proven": any(
            bool(record.get("semantic_cpu_partition"))
            for record in records.values()
        ),
        "native_partition_parity_proven": any(
            bool(record.get("native_partition_evidence"))
            for record in records.values()
        ),
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_explicit_parity_evidence",
    }


def moving_optical_flow_partition_gap_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Audit moving-frame optical flow without enabling block dispatch.

    This is a stricter view of :func:`optical_flow_partition_gap_report`: all
    entries are explicitly marked as moving/coarse-to-fine and require a
    level-aware halo, point-order, and same-backend native proof.  It exists so
    callers cannot mistake the bounded identity-frame specialization for
    moving-flow support.
    """

    report = optical_flow_partition_gap_report(
        operations, backend=backend, device=device
    )
    records: dict[str, dict[str, Any]] = {}
    for operation, original in report["operations"].items():
        record = dict(original)
        reasons = list(record.get("blocked_reasons", ()))
        if "moving-frame coarse-to-fine parity is not proven" not in reasons:
            reasons.append("moving-frame coarse-to-fine parity is not proven")
        if "native moving-flow evidence is unavailable" not in reasons:
            reasons.append("native moving-flow evidence is unavailable")
        record.update(
            {
                "moving_frame": True,
                "identity_frame_specialization": False,
                "blocked_reasons": reasons,
                "required_evidence": list(record.get("required_evidence", ()))
                + [
                    "moving synthetic pair with known translation and non-multiple tiles",
                    "level-aware halo exchange and deterministic merge validation",
                ],
                # Identity-frame evidence is intentionally not accepted here.
                "semantic_cpu_partition": False,
                "native_partition_evidence": False,
                "native_runtime": False,
                "status": "moving_gap_fail_closed",
                "preserves_default_full_frame": True,
            }
        )
        records[operation] = record
    return {
        "scope": "moving_optical_flow_partition_contract_audit",
        "backend": report["backend"],
        "device": report["device"],
        "operations": records,
        "operation_order": report["operation_order"],
        "semantic_cpu_parity_proven": False,
        "native_partition_parity_proven": False,
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_moving_parity_evidence",
    }


def verify_moving_flow_translation_contract(
    full_output: Any,
    tiled_output: Any,
    *,
    expected_translation: tuple[float, float],
    block_selected: bool,
    backend: str,
    device: str,
    parity_tolerance: float = 1.0e-4,
    translation_tolerance: float = 0.5,
    halo: int = 0,
    pyramid_levels: int = 1,
    deterministic_merge: bool = False,
    same_backend: bool = True,
) -> dict[str, Any]:
    """Validate a bounded synthetic moving-flow observation.

    This helper is an evidence gate, not an executor.  It accepts outputs from
    a real full-frame and tiled run and qualifies only when shape, finiteness,
    block selection, same-backend identity, full/tiled parity, and the known
    synthetic translation all pass.  It deliberately never registers native
    evidence or changes dispatch; callers may persist the returned report for
    a later device-scoped review.
    """

    if not str(backend or "").strip() or not str(device or "").strip():
        raise ValueError("moving-flow evidence requires backend and exact device")
    parity_tolerance = float(parity_tolerance)
    translation_tolerance = float(translation_tolerance)
    if parity_tolerance < 0.0 or translation_tolerance < 0.0:
        raise ValueError("moving-flow tolerances must be non-negative")
    halo = int(halo)
    pyramid_levels = int(pyramid_levels)
    if halo < 0 or pyramid_levels < 1:
        raise ValueError("moving-flow halo must be non-negative and levels >= 1")
    full = np.asarray(full_output)
    tiled = np.asarray(tiled_output)
    shape_ok = full.shape == tiled.shape and full.ndim == 3 and full.shape[-1] == 2
    finite = bool(np.isfinite(full).all() and np.isfinite(tiled).all()) if shape_ok else False
    parity_error = (
        float(np.max(np.abs(full.astype(np.float64) - tiled.astype(np.float64))))
        if shape_ok and full.size
        else float("inf")
    )
    expected_dx, expected_dy = (float(expected_translation[0]), float(expected_translation[1]))
    median_flow = (
        np.median(full.reshape(-1, 2), axis=0)
        if shape_ok and full.size
        else np.asarray([np.nan, np.nan], dtype=np.float64)
    )
    translation_error = float(
        np.max(np.abs(median_flow - np.asarray([expected_dx, expected_dy])))
    )
    passed = bool(
        bool(block_selected)
        and shape_ok
        and finite
        and parity_error <= parity_tolerance
        and translation_error <= translation_tolerance
        and halo >= 0
        and pyramid_levels >= 1
        and bool(deterministic_merge)
        and bool(same_backend)
    )
    return {
        "scope": "synthetic_moving_flow_translation_contract",
        "backend": str(backend).strip().lower(),
        "device": str(device).strip(),
        "shape": list(full.shape),
        "block_selected": bool(block_selected),
        "expected_translation": [expected_dx, expected_dy],
        "median_translation": [float(median_flow[0]), float(median_flow[1])],
        "translation_error": translation_error,
        "parity_max_abs_error": parity_error,
        "parity_tolerance": parity_tolerance,
        "translation_tolerance": translation_tolerance,
        "halo": halo,
        "pyramid_levels": pyramid_levels,
        "deterministic_merge": bool(deterministic_merge),
        "same_backend": bool(same_backend),
        "finite": finite,
        "passed": passed,
        "native_runtime": False,
        "evidence_status": "candidate_only" if passed else "fail_closed",
        "dispatch_changed": False,
    }


def aggregate_moving_flow_candidate_evidence(
    reports: Sequence[Mapping[str, Any]],
    *,
    required: Sequence[tuple[str, str]] = (),
) -> dict[str, Any]:
    """Aggregate candidate reports without promoting runtime dispatch.

    ``reports`` are produced by :func:`verify_moving_flow_translation_contract`
    or an equivalent native probe.  Every required backend/device pair must
    have an independently passing report; duplicates and malformed records are
    rejected.  The result is deliberately ``candidate_only`` and never writes
    the native-evidence registry.
    """

    expected = tuple((str(backend).strip().lower(), str(device).strip()) for backend, device in required)
    if any(not backend or not device for backend, device in expected):
        raise ValueError("required moving-flow evidence needs backend and device")
    seen: set[tuple[str, str]] = set()
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for raw in reports:
        if not isinstance(raw, Mapping):
            rejected.append({"reason": "record_not_mapping"})
            continue
        backend = str(raw.get("backend", "")).strip().lower()
        device = str(raw.get("device", "")).strip()
        key = (backend, device)
        if not backend or not device:
            rejected.append({"backend": backend, "device": device, "reason": "missing_identity"})
            continue
        if key in seen:
            rejected.append({"backend": backend, "device": device, "reason": "duplicate_identity"})
            continue
        seen.add(key)
        reasons: list[str] = []
        if not bool(raw.get("passed")):
            reasons.append("probe_not_passed")
        if not bool(raw.get("native_runtime")):
            reasons.append("native_runtime_not_proven")
        if not bool(raw.get("block_selected")):
            reasons.append("block_not_selected")
        if not bool(raw.get("deterministic_merge")):
            reasons.append("merge_not_deterministic")
        if not bool(raw.get("same_backend", True)):
            reasons.append("same_backend_not_proven")
        if not bool(raw.get("finite")):
            reasons.append("non_finite_output")
        if str(raw.get("evidence_status", "candidate_only")) != "candidate_only":
            reasons.append("invalid_evidence_status")
        if reasons:
            rejected.append({"backend": backend, "device": device, "reason": ",".join(reasons)})
        else:
            accepted.append(dict(raw))
    missing = [list(item) for item in expected if item not in {(item["backend"], item["device"]) for item in accepted}]
    passed = bool(accepted) and not rejected and not missing
    return {
        "scope": "moving_flow_candidate_evidence_aggregate",
        "required": [list(item) for item in expected],
        "accepted": accepted,
        "rejected": rejected,
        "missing": missing,
        "backend_count": len(accepted),
        "passed": passed,
        "evidence_status": "candidate_only" if passed else "fail_closed",
        "native_runtime": bool(passed),
        "registry_mutated": False,
        "dispatch_changed": False,
    }


def aggregate_native_moving_flow_candidates(
    records: Sequence[Mapping[str, Any]],
    *,
    expected_targets: Sequence[Mapping[str, Any] | tuple[str, str]],
    expected_translation: tuple[float, float] | None = None,
    parity_tolerance: float = 1.0e-4,
    translation_tolerance: float = 0.5,
    shape: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Aggregate native moving-flow probes without qualifying dispatch.

    Each expected ``(backend, exact device)`` pair must have one passing
    candidate record.  Records are intentionally treated as untrusted JSON:
    native runtime, block selection, finite/shape checks, parity tolerance,
    and deterministic repeat evidence are all required.  The returned report
    is always ``candidate_only`` when complete; this function never writes the
    native evidence registry or changes automatic block policy.
    """
    parity_tolerance = float(parity_tolerance)
    translation_tolerance = float(translation_tolerance)
    if parity_tolerance < 0.0 or translation_tolerance < 0.0:
        raise ValueError("moving-flow tolerances must be non-negative")

    def target_key(value: Mapping[str, Any] | tuple[str, str]) -> tuple[str, str]:
        if isinstance(value, Mapping):
            backend = value.get("backend")
            device = value.get("device")
        else:
            try:
                backend, device = value
            except (TypeError, ValueError) as exc:
                raise ValueError("expected_targets entries must be backend/device pairs") from exc
        backend_name = str(backend or "").strip().lower()
        device_name = str(device or "").strip()
        if not backend_name or not device_name:
            raise ValueError("expected targets require backend and exact device")
        return backend_name, device_name

    targets = tuple(target_key(item) for item in expected_targets)
    if not targets:
        raise ValueError("expected_targets must not be empty")
    seen: set[tuple[str, str]] = set()
    checked: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    expected_shape = None if shape is None else tuple(int(item) for item in shape)
    expected_motion = None if expected_translation is None else tuple(float(item) for item in expected_translation)
    for raw in records:
        item = dict(raw) if isinstance(raw, Mapping) else {}
        key = (str(item.get("backend") or "").strip().lower(), str(item.get("device") or "").strip())
        reasons: list[str] = []
        if key not in targets:
            reasons.append("backend/device is not an expected exact target")
        elif key in seen:
            reasons.append("duplicate backend/device candidate")
        else:
            seen.add(key)
        if not bool(item.get("native_runtime")):
            reasons.append("native_runtime is not true")
        if not bool(item.get("block_selected")):
            reasons.append("block_selected is not true")
        observed_shape = tuple(int(value) for value in item.get("shape", ()))
        if len(observed_shape) != 3 or observed_shape[-1] != 2:
            reasons.append("shape is not HxWx2")
        if expected_shape is not None and observed_shape != expected_shape:
            reasons.append("shape does not match expected shape")
        if not bool(item.get("finite")):
            reasons.append("finite output evidence is missing")
        try:
            parity_error = float(item.get("max_abs_error_vs_same_backend_full", item.get("parity_max_abs_error", float("inf"))))
        except (TypeError, ValueError):
            parity_error = float("inf")
        if not np.isfinite(parity_error) or parity_error > parity_tolerance:
            reasons.append("full-frame/block parity exceeds tolerance")
        repeat_error_value = item.get("repeat_max_abs_error")
        deterministic = bool(item.get("deterministic_merge"))
        try:
            repeat_error = float(repeat_error_value)
        except (TypeError, ValueError):
            repeat_error = float("inf")
        if not deterministic or not np.isfinite(repeat_error) or repeat_error > parity_tolerance:
            reasons.append("deterministic repeat evidence is missing or exceeds tolerance")
        if expected_motion is not None:
            observed_motion = item.get("median_translation")
            try:
                motion_error = float(np.max(np.abs(np.asarray(observed_motion, dtype=np.float64) - np.asarray(expected_motion, dtype=np.float64))))
            except (TypeError, ValueError):
                motion_error = float("inf")
            if not np.isfinite(motion_error) or motion_error > translation_tolerance:
                reasons.append("known translation exceeds tolerance")
        else:
            motion_error = None
        result = {
            "backend": key[0], "device": key[1], "passed": not reasons,
            "reasons": reasons, "parity_max_abs_error": parity_error,
            "repeat_max_abs_error": repeat_error, "translation_error": motion_error,
            "candidate_only": True,
        }
        checked.append(result)
        if reasons:
            failures.append(result)
    missing = [key for key in targets if key not in seen]
    passed = not missing and not failures and len(checked) == len(targets)
    return {
        "scope": "native_moving_flow_candidate_aggregate",
        "expected_targets": [{"backend": key[0], "device": key[1]} for key in targets],
        "checked": checked,
        "missing_targets": [{"backend": key[0], "device": key[1]} for key in missing],
        "passed": bool(passed),
        "evidence_status": "candidate_only" if passed else "fail_closed",
        "native_runtime": bool(passed),
        "registry_mutated": False,
        "dispatch_changed": False,
    }


def qualify_native_moving_flow_candidates(
    records: Sequence[Mapping[str, Any]],
    *,
    expected_targets: Sequence[Mapping[str, Any] | tuple[str, str]],
    expected_translation: tuple[float, float] | None = None,
    parity_tolerance: float = 1.0e-4,
    translation_tolerance: float = 0.5,
    shape: Sequence[int] | None = None,
    verified_contracts: Mapping[Any, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a read-only promotion decision for native moving-flow probes.

    ``promotion_eligible`` means every explicitly supplied target passed the
    candidate gates and is ready for a human/device-scoped evidence review.
    It does *not* register evidence or alter automatic dispatch.  Missing
    candidate metadata is reported by name so a probe cannot accidentally be
    treated as a qualification merely because its numeric output looks good.
    """
    aggregate = aggregate_native_moving_flow_candidates(
        records,
        expected_targets=expected_targets,
        expected_translation=expected_translation,
        parity_tolerance=parity_tolerance,
        translation_tolerance=translation_tolerance,
        shape=shape,
    )
    reasons: list[str] = []
    if not aggregate["passed"]:
        reasons.append("aggregate candidate gates did not pass")
    contract_overrides = dict(verified_contracts or {})
    for index, raw in enumerate(records):
        item = dict(raw) if isinstance(raw, Mapping) else {}
        if str(item.get("evidence_status", "")).strip().lower() != "candidate_only":
            reasons.append(f"record[{index}] is not explicitly candidate_only")
        if not bool(item.get("deterministic_merge")):
            reasons.append(f"record[{index}] lacks deterministic merge evidence")
        contract = item.get("block_plan", {}).get("contract", {}) if isinstance(item.get("block_plan"), Mapping) else {}
        # External metadata is deliberately opt-in and keyed by the exact
        # backend/device pair.  It is never written back to the probe or the
        # maintained operation contract.
        override = contract_overrides.get((str(item.get("backend") or "").strip().lower(), str(item.get("device") or "").strip()))
        if override is not None:
            contract = dict(override)
            if str(contract.get("operation", "farneback_flow")) != "farneback_flow":
                reasons.append(f"record[{index}] verified contract operation is not farneback_flow")
        elif contract_overrides:
            reasons.append(f"record[{index}] has no exact verified contract metadata")
        if not bool(contract.get("partition_qualified")):
            reasons.append(f"record[{index}] contract is not partition_qualified")
        if not bool(contract.get("automatic_safe")):
            reasons.append(f"record[{index}] contract is not automatic_safe")
    eligible = not reasons
    return {
        "scope": "native_moving_flow_promotion_review",
        "aggregate": aggregate,
        "promotion_eligible": bool(eligible),
        # A candidate report is review metadata only.  Even when all probe
        # gates pass, it must never advertise dispatch-safe state or be
        # consumed as an automatic promotion signal.
        "automatic_safe": False,
        "parity_qualified": False,
        "dispatch_promotion": False,
        "status": "candidate_ready_for_review" if eligible else "fail_closed",
        "reasons": reasons,
        "evidence_status": "candidate_only",
        "registry_mutated": False,
        "dispatch_changed": False,
    }


def feature_geometry_partition_gap_report(
    operations: Optional[Sequence[str] | str] = None,
    *,
    backend: Optional[str] = None,
    device: Optional[str] = None,
) -> dict[str, Any]:
    """Return a read-only, fail-closed audit for feature/geometry stages.

    The report distinguishes AKAZE's bounded semantic CPU keypoint adapter from
    its descriptor/matching pipeline and from global homography reduction.  It
    never registers an adapter, changes automatic dispatch, or treats a TCM
    artifact as native block evidence.  Native records are read only when both
    backend and exact device are supplied.
    """

    if operations is None:
        names = FEATURE_GEOMETRY_CONTRACT_OPERATIONS
    elif isinstance(operations, str):
        names = (operations,)
    else:
        names = tuple(operations)

    selected: list[str] = []
    for raw_name in names:
        canonical = canonical_operation_name(raw_name)
        if canonical not in _FEATURE_GEOMETRY_GAP_REASONS:
            raise ValueError(
                "feature/geometry gap report supports only "
                f"{FEATURE_GEOMETRY_CONTRACT_OPERATIONS}; got {raw_name!r}"
            )
        if canonical not in selected:
            selected.append(canonical)

    backend_name = None if backend is None else str(backend).strip().lower()
    device_name = None if device is None else str(device).strip()
    records: dict[str, dict[str, Any]] = {}
    for operation in selected:
        contract = operation_contract(operation)
        capability = operation_capability(operation)
        adapter = lookup_block_adapter(operation)
        legacy = legacy_partition_evidence(operation, backend_name)
        native_records: list[dict[str, Any]] = []
        if backend_name and device_name:
            try:
                from .native_evidence import lookup_native_partition_evidence

                native_records = [
                    evidence.as_dict()
                    for evidence in lookup_native_partition_evidence(
                        operation, backend_name, device_name
                    )
                ]
            except Exception:
                native_records = []
        native_qualified = any(
            bool(item.get("qualified")) and bool(item.get("native_runtime"))
            for item in native_records
        )
        semantic_cpu = bool(
            operation == "akaze"
            and backend_name in (None, "cpu")
            and adapter is not None
            and can_partition_block(operation, backend_name)
        )
        records[operation] = {
            "operation": operation,
            "path": operation_path(operation).value,
            "contract": contract.as_dict(),
            "dependencies": list(capability.dependencies),
            "legacy_executor": None if legacy is None else legacy.get("executor"),
            "legacy_strategy": None if legacy is None else legacy.get("strategy"),
            "legacy_evidence_status": (
                None if legacy is None else legacy.get("status", "executor_only")
            ),
            "adapter_registered": adapter is not None,
            "semantic_cpu_partition": semantic_cpu,
            "automatic_safe": bool(can_auto_block(operation, backend_name)),
            "partition_safe": bool(can_partition_block(operation, backend_name)),
            "automatic_dispatch_safe": bool(
                can_auto_partition_dispatch(operation, backend_name)
            ),
            "native_partition_evidence": native_qualified,
            "native_evidence_records": native_records,
            "native_runtime": native_qualified,
            "status": "restricted_semantic_cpu" if semantic_cpu else "gap_fail_closed",
            "blocked_reasons": list(_FEATURE_GEOMETRY_GAP_REASONS[operation]),
            "required_evidence": list(_FEATURE_GEOMETRY_REQUIRED_EVIDENCE[operation]),
            "preserves_default_full_frame": True,
        }

    return {
        "scope": "feature_geometry_partition_contract_audit",
        "backend": backend_name,
        "device": device_name,
        "operations": records,
        "operation_order": selected,
        "semantic_cpu_parity_proven": any(
            bool(record.get("semantic_cpu_partition"))
            for record in records.values()
        ),
        "native_partition_parity_proven": any(
            bool(record.get("native_partition_evidence"))
            for record in records.values()
        ),
        "runtime_dispatch_changed": False,
        "default_mode": "full_frame",
        "status": "fail_closed_until_explicit_parity_evidence",
    }


def validate_homography_correspondence_contract(
    pts1: Any,
    pts2: Any,
    *,
    max_points: Optional[int] = None,
) -> dict[str, Any]:
    """Validate the stable input contract for the global homography stage.

    ``find_homography`` is intentionally still a full-frame/global operation;
    this helper does *not* register a block adapter and does not claim tiled or
    native parity.  It provides the deterministic, side-effect-free preflight
    needed before a future partitioned reducer can be considered: both point
    arrays must contain the same number of finite ``(x, y)`` pairs, with the
    original row pairing preserved.  The returned arrays are not exposed, so
    callers cannot accidentally infer that the public API reordered points.
    """

    first = np.asarray(pts1)
    second = np.asarray(pts2)
    if first.ndim != 2 or first.shape[1:] != (2,):
        raise ValueError("homography pts1 must have shape (N, 2)")
    if second.ndim != 2 or second.shape[1:] != (2,):
        raise ValueError("homography pts2 must have shape (N, 2)")
    if first.shape[0] != second.shape[0]:
        raise ValueError("homography correspondence arrays must have equal length")
    count = int(first.shape[0])
    if count < 4:
        raise ValueError("homography requires at least four correspondences")
    if max_points is not None:
        limit = int(max_points)
        if limit < 4:
            raise ValueError("homography max_points must be at least four")
        if count > limit:
            raise ValueError("homography correspondence count exceeds max_points")
    if not np.issubdtype(first.dtype, np.number) or not np.issubdtype(
        second.dtype, np.number
    ):
        raise TypeError("homography correspondences must be numeric")
    if np.iscomplexobj(first) or np.iscomplexobj(second):
        raise TypeError("homography correspondences must be real-valued")
    first32 = np.ascontiguousarray(first, dtype=np.float32)
    second32 = np.ascontiguousarray(second, dtype=np.float32)
    if not np.isfinite(first32).all() or not np.isfinite(second32).all():
        raise ValueError("homography correspondences must be finite")
    return {
        "operation": "find_homography",
        "scope": "semantic_cpu_input_contract",
        "backend": "cpu",
        "device": "host",
        "point_count": count,
        "shape": [count, 2],
        "dtype": "float32",
        "contiguous": bool(first32.flags.c_contiguous and second32.flags.c_contiguous),
        "finite": True,
        "ordering": "input_row_order_preserved",
        "paired_rows": True,
        "passed": True,
        "native_runtime": False,
        "partition_qualified": False,
    }


def register_flow_map_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register the CPU semantic ``build_flow_maps`` output-domain contract.

    The remap TCM contains native full-frame graphs, but no backend-qualified
    tiled lifecycle proof is attached here.  Consequently this registration
    remains explicit/CPU-only and cannot alter automatic dispatch.
    """

    registered: dict[str, BlockAdapter] = {}
    operation = "build_flow_maps"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    contract = _specialized_cpu_contract(
        operation,
        shape_transform=ShapeTransform.CHANGING,
        input_coordinate_map="flow_output_domain",
        merge=MergePolicy.CUSTOM,
        strategy=PartitionStrategy.COORDINATE,
        reason="deterministic CPU flow-map output-domain parity; native proof pending",
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "flow_map_output_domain",
        "coordinate_domain": True,
        "source_window": "full_frame",
        "semantic_only": True,
        "native_probe_required": True,
        "native_runtime": False,
        "legacy_partition_evidence": None,
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_flow_map_output_domain",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _flow_maps_reference,
        "parity_runner": verify_flow_maps_parity,
        "custom_executor": _run_flow_maps_tiled,
    }
    registered[operation] = register_block_adapter(
        operation,
        reader=_flow_map_reader,
        runner=_flow_map_runner,
        validator=_flow_map_validator,
        merger=_flow_map_merger,
        contract=contract,
        metadata=metadata,
        partition_strategy=PartitionStrategy.COORDINATE,
        backend_capability={"cpu": {"supported": True, "parity": True}},
        replace=replace,
    )
    return registered


def register_normalization_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register the CPU semantic ``normalize_image`` spatial-tile contract."""

    operation = "normalize_image"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    contract = _specialized_cpu_contract(
        operation,
        shape_transform=ShapeTransform.EXPAND,
        input_coordinate_map="identity_spatial",
        merge=MergePolicy.OVERWRITE,
        strategy=PartitionStrategy.COORDINATE,
        reason="deterministic CPU normalize_image spatial parity; native proof pending",
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "normalize_image_spatial",
        "coordinate_domain": True,
        # ``normalize_image_gpu`` preserves the source spatial domain but
        # expands a grayscale frame to three channels.  Keep this explicit in
        # the adapter metadata so a generic planner cannot infer a plain
        # same-shape copy from ``ShapeTransform.EXPAND`` alone.
        "output_shape_policy": "same_spatial_expand_gray_to_rgb",
        "output_channel_policy": {
            "grayscale": "expand_to_3",
            "multi_channel": "preserve_trailing_channels",
        },
        "output_dtype": "float32",
        "declared_dtype_policy": "integer_scale_by_max_float_identity",
        "supported_declared_dtype_kinds": ("integer", "floating"),
        "semantic_only": True,
        "native_probe_required": True,
        "native_runtime": False,
        "legacy_partition_evidence": None,
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_normalize_image_spatial_tiles",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _normalize_image_reference,
        "parity_runner": verify_normalize_image_parity,
        "custom_executor": _run_normalize_image_tiled,
    }
    return {
        operation: register_block_adapter(
            operation,
            reader=_normalize_image_reader,
            runner=_normalize_image_runner,
            validator=_normalize_image_validator,
            merger=_normalize_image_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    }


def register_brief_pattern_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register deterministic output-domain BRIEF pattern generation."""

    operation = "generate_brief_pattern"
    existing = lookup_block_adapter(operation)
    if existing is not None and not replace:
        return {operation: existing}
    contract = _specialized_cpu_contract(
        operation,
        shape_transform=ShapeTransform.CHANGING,
        input_coordinate_map="generated_output_domain",
        merge=MergePolicy.OVERWRITE,
        strategy=PartitionStrategy.COORDINATE,
        reason="deterministic CPU BRIEF output-domain parity; native proof pending",
    )
    metadata = {
        "source": "taichi_vision.taichi_aot.block_adapters",
        "partition_kind": "output_domain",
        "output_domain": True,
        "semantic_only": True,
        "native_probe_required": True,
        "native_runtime": False,
        "legacy_partition_evidence": None,
        "parity_evidence": {
            "cpu": {
                "supported": True,
                "parity": True,
                "scope": "deterministic_numpy_brief_pattern_output_domain",
                "native_runtime": False,
            }
        },
        "full_frame_callback": _brief_pattern_reference,
        "parity_runner": verify_output_domain_parity,
    }
    return {
        operation: register_block_adapter(
            operation,
            reader=_output_domain_reader,
            runner=_output_domain_runner,
            validator=_output_domain_validator,
            merger=_output_domain_merger,
            contract=contract,
            metadata=metadata,
            partition_strategy=PartitionStrategy.COORDINATE,
            backend_capability={"cpu": {"supported": True, "parity": True}},
            replace=replace,
        )
    }


def register_specialized_block_adapters(
    *, replace: bool = False
) -> Mapping[str, BlockAdapter]:
    """Register all additive semantic adapters in the explicit helper.

    This convenience function remains opt-in.  Adding FFT, phase correlation,
    or the bounded AKAZE keypoint stage here only populates the adapter
    registry; their contracts are still semantic CPU-only and cannot enable
    automatic/native dispatch.
    """

    registered: dict[str, BlockAdapter] = {}
    registered.update(register_flow_map_adapters(replace=replace))
    registered.update(register_normalization_adapters(replace=replace))
    registered.update(register_brief_pattern_adapters(replace=replace))
    registered.update(register_fft_block_adapters(replace=replace))
    registered.update(register_phase_correlation_block_adapters(replace=replace))
    registered.update(register_akaze_block_adapters(replace=replace))
    registered.update(register_optical_flow_identity_adapters(replace=replace))
    registered.update(register_coordinate_warp_adapters(replace=replace))
    registered.update(register_demosaic_full_adapters(replace=replace))
    registered.update(register_demosaic_half_adapters(replace=replace))
    registered.update(register_bounded_semantic_adapters(replace=replace))
    registered.update(register_legacy_local_block_adapters(replace=replace))
    return registered


def _allocate_output(reference: Any) -> Any:
    if isinstance(reference, (tuple, list)):
        return tuple(np.empty_like(value) for value in reference)
    return np.empty_like(reference)


def _prepare_map_reduce_params(
    operation: str,
    arrays: Sequence[np.ndarray],
    params: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    """Resolve parameters that must be global before map dispatch.

    A float SSIM input's implicit ``data_range`` is defined by the complete
    frame.  Resolving it before slicing prevents each tile from selecting a
    different range based on its local extrema.  Integer inputs retain the
    public dtype-derived range and do not require an extra full-frame scan.
    """

    values = dict(params or {})
    if canonical_operation_name(operation) == "ssim_aot":
        if not arrays:
            raise ValueError("ssim_aot requires at least one input")
        first = np.asarray(arrays[0])
        if "data_range" not in values or values.get("data_range") is None:
            if np.issubdtype(first.dtype, np.integer):
                values["data_range"] = float(np.iinfo(first.dtype).max)
            else:
                data = np.asarray(first, dtype=np.float64)
                span = float(np.max(data) - np.min(data)) if data.size else 1.0
                values["data_range"] = span if span > 0.0 else 1.0
        # Validate all scalar parameters before allocating a BlockGrid; this
        # gives callers a clear error instead of a partial reduction.
        _ssim_constants(first, values)
    elif canonical_operation_name(operation) in _NCC_ADAPTER_OPERATIONS:
        # NCC's template statistics and output shape are global call metadata;
        # resolve/validate them before constructing the output grid so a bad
        # template or stride cannot leave a partially reduced accumulator.
        _ncc_inputs(arrays, values)
    elif canonical_operation_name(operation) in _STITCH_ADAPTER_OPERATIONS:
        _stitch_inputs(arrays, values)
    return values


def _run_output_grid_map_reduce(
    operation: str,
    adapter: BlockAdapter,
    arrays: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int],
    params: Mapping[str, Any],
) -> Any:
    """Run an adapter whose blocks live on a derived output search domain.

    NCC is the first consumer.  Its image and template have different shapes,
    so the ordinary map/reduce harness (which requires matching input grids)
    cannot be reused safely.  This small executor keeps the same deterministic
    row-major order and reducer protocol while making the coordinate contract
    explicit and preserving the public full-frame functions unchanged.
    """

    shape_factory = adapter.metadata.get("output_shape")
    output_factory = adapter.metadata.get("output_factory")
    reducer = adapter.metadata.get("reduce", adapter.merger)
    finalizer = adapter.metadata.get("finalize")
    if not callable(shape_factory) or not callable(output_factory):
        raise ValueError(f"{operation} output-domain metadata is incomplete")
    output_shape = tuple(int(value) for value in shape_factory(arrays, params))
    if len(output_shape) != 2 or any(value <= 0 for value in output_shape):
        raise ValueError(f"{operation} output shape must be positive 2D")
    try:
        accumulator = output_factory(params, output_shape)
    except TypeError:
        # Existing map/reduce factories accept only the parameter mapping.
        accumulator = output_factory(params)
    grid = BlockGrid(output_shape, size=block_size, halo=0)
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
    expected = tuple(range(len(blocks)))
    actual = tuple(int(item.index) for item in blocks)
    if actual != expected:
        raise ValueError(f"{operation} output map/reduce order is not deterministic")
    for block in blocks:
        context = PartitionContext(
            operation=canonical_operation_name(operation),
            inputs=tuple(np.asarray(value) for value in arrays),
            block=block,
            full_shape=output_shape,
            output_shape=output_shape,
            params=dict(params),
        )
        tile_context = adapter.reader(context, block) if adapter.reader else context
        partial = adapter.runner(tile_context)
        if adapter.validator is not None and not adapter.validator(tile_context, partial):
            raise ValueError(f"{operation} map result failed validation at block {block.index}")
        reducer(accumulator, partial, block)
    if not callable(finalizer):
        return accumulator
    return finalizer(accumulator, arrays, params)


def _run_sequence_map_reduce(
    operation: str,
    adapter: BlockAdapter,
    arrays: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int],
    params: Mapping[str, Any],
) -> Any:
    """Run a deterministic reduction over an ordered tile-index domain."""

    tiles, _tile_weight, _hanning, accum, weight_accum, _y0s, _x0s = _stitch_inputs(
        arrays, params
    )
    tile_count = int(tiles.shape[0])
    initial = _stitch_output_factory(arrays, params)
    # ``BlockGrid`` supplies stable row-major chunk indices while the adapter
    # reader maps each rank to the canonical origin order.  The width is one
    # because the domain is a sequence, not a spatial image grid.
    if isinstance(block_size, tuple):
        chunk_size = max(1, int(block_size[0]))
    else:
        chunk_size = max(1, int(block_size))
    grid = BlockGrid((tile_count, 1), size=(chunk_size, 1), halo=0)
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
    expected = tuple(range(len(blocks)))
    actual = tuple(int(item.index) for item in blocks)
    if actual != expected:
        raise ValueError(f"{operation} sequence block order is not deterministic")
    output = initial
    for block in blocks:
        context = PartitionContext(
            operation=canonical_operation_name(operation),
            inputs=tuple(np.asarray(value) for value in arrays),
            block=block,
            full_shape=tuple(accum.shape),
            output_shape=tuple(accum.shape),
            params=dict(params),
        )
        tile_context = adapter.reader(context, block) if adapter.reader else context
        partial = adapter.runner(tile_context)
        if adapter.validator is not None and not adapter.validator(tile_context, partial):
            raise ValueError(f"{operation} map result failed validation at block {block.index}")
        # Pass context to the merger so operation-specific semantics remain
        # explicit; the partial itself also carries the hanning weights.
        adapter.merger(output, partial, tile_context)
    finalizer = adapter.metadata.get("finalize")
    if callable(finalizer):
        return finalizer(output, arrays, params)
    return output


def run_adapter_map_reduce(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> Any:
    """Run one explicit map/reduce adapter over deterministic blocks."""

    adapter = lookup_block_adapter(operation)
    if adapter is None or adapter.metadata.get("partition_kind") != "map_reduce":
        raise ValueError(f"no map/reduce adapter registered for {operation}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if adapter.metadata.get("sequence_domain"):
        values = _prepare_map_reduce_params(operation, arrays, params)
        return _run_sequence_map_reduce(
            operation,
            adapter,
            arrays,
            block_size=block_size,
            params=values,
        )
    if adapter.metadata.get("output_grid"):
        values = _prepare_map_reduce_params(operation, arrays, params)
        return _run_output_grid_map_reduce(
            operation,
            adapter,
            arrays,
            block_size=block_size,
            params=values,
        )
    if not arrays or any(value.ndim < 2 for value in arrays):
        raise ValueError("map/reduce inputs must be at least two-dimensional")
    if any(value.shape[:2] != arrays[0].shape[:2] for value in arrays):
        raise ValueError("map/reduce inputs must share their first two dimensions")
    values = _prepare_map_reduce_params(operation, arrays, params)
    factory = adapter.metadata.get("output_factory")
    reducer = adapter.metadata.get("reduce", adapter.merger)
    finalizer = adapter.metadata.get("finalize")
    if not callable(factory) or not callable(reducer) or not callable(finalizer):
        raise ValueError(f"map/reduce adapter metadata is incomplete for {operation}")
    try:
        accumulator = factory(values)
    except TypeError:
        accumulator = factory()
    halo_spec = adapter.metadata.get("halo", 0)
    if callable(halo_spec):
        halo = int(halo_spec(values))
    else:
        halo = int(halo_spec or 0)
    max_halo = adapter.metadata.get("max_halo")
    if max_halo is not None and halo > int(max_halo):
        raise ValueError(f"{operation} requested halo exceeds adapter maximum")
    grid = BlockGrid(arrays[0].shape, size=block_size, halo=halo)
    # BlockGrid is scanline ordered today.  Sorting explicitly makes that
    # ordering part of the map/reduce contract rather than an incidental
    # iterator detail and keeps floating-point merges reproducible.
    blocks = tuple(sorted(tuple(grid), key=lambda item: int(item.index)))
    if adapter.metadata.get("deterministic_merge"):
        expected = tuple(range(len(blocks)))
        actual = tuple(int(item.index) for item in blocks)
        if actual != expected:
            raise ValueError(f"{operation} map/reduce block order is not deterministic")
    for block in blocks:
        context = PartitionContext(
            operation=canonical_operation_name(operation),
            inputs=arrays,
            block=block,
            full_shape=tuple(arrays[0].shape),
            params=values,
        )
        tile_context = adapter.reader(context, block) if adapter.reader else context
        partial = adapter.runner(tile_context)
        if adapter.validator is not None and not adapter.validator(tile_context, partial):
            raise ValueError(f"{operation} map result failed validation at block {block.index}")
        reducer(accumulator, partial, block)
    return finalizer(accumulator, arrays, values)


def verify_map_reduce_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Compare the full-frame oracle with a deterministic tile reduction."""

    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = _prepare_map_reduce_params(operation, arrays, params)
    canonical = canonical_operation_name(operation)
    if canonical == "histogram":
        full = _histogram_reference(
            arrays[0],
            bins=int(values.get("bins", 256)),
            range_min=float(values.get("range_min", 0.0)),
            range_max=float(values.get("range_max", 256.0)),
        )
    elif canonical == "otsu_threshold":
        full = _otsu_reference(
            arrays[0],
            thresh_type=int(values.get("thresh_type", 0)),
            max_val=float(values.get("max_val", 255.0)),
            bins=int(values.get("bins", 256)),
        )
    elif canonical == "ssim_aot":
        if len(arrays) != 2:
            raise ValueError("ssim_aot parity requires two inputs")
        full = _ssim_reference(
            arrays[0],
            arrays[1],
            window_size=int(values.get("window_size", 11)),
            data_range=float(values["data_range"]),
            k1=float(values.get("k1", 0.01)),
            k2=float(values.get("k2", 0.03)),
        )
    elif canonical == "zncc":
        if len(arrays) != 2:
            raise ValueError("zncc parity requires image and template inputs")
        full = _ncc_reference(
            arrays[0], arrays[1], stride=int(values.get("stride", 1))
        )
    elif canonical == "ncc_alignment":
        if len(arrays) != 2:
            raise ValueError("ncc_alignment parity requires image and template inputs")
        full = _ncc_alignment_reference(
            arrays[0], arrays[1], stride=int(values.get("stride", 1))
        )
    elif canonical in _STITCH_ADAPTER_OPERATIONS:
        full = _stitch_reference(canonical, arrays, values)
    else:
        raise ValueError(f"unknown map/reduce operation: {operation}")
    tiled = run_adapter_map_reduce(
        operation, arrays, block_size=block_size, params=values
    )
    full_values = full if isinstance(full, (tuple, list)) else (full,)
    tiled_values = tiled if isinstance(tiled, (tuple, list)) else (tiled,)
    # Keep tuple-valued operations auditable without changing their public
    # return value.  In particular split_3ch must expose three fixed 2-D
    # planes and merge_3ch one 3-channel image; an arity/shape mismatch must
    # never be hidden behind a scalar ``passed`` flag.
    output_shapes = [list(np.asarray(value).shape) for value in tiled_values]
    expected_shapes = [list(np.asarray(value).shape) for value in full_values]
    if len(full_values) != len(tiled_values):
        passed = False
        max_error = float("inf")
    else:
        errors = [
            float(
                np.max(
                    np.abs(
                        np.asarray(left).astype(np.float64)
                        - np.asarray(right).astype(np.float64)
                    )
                )
            )
            if np.asarray(left).size
            else 0.0
            for left, right in zip(full_values, tiled_values)
        ]
        max_error = max(errors, default=0.0)
        if canonical in {
            "ssim_aot",
            "zncc",
            "ncc_alignment",
            *_STITCH_ADAPTER_OPERATIONS,
        }:
            # SSIM reduces per-pixel floating-point scores in a fixed
            # row-major tile order.  NCC tiles use the same float32 score
            # kernel and deterministic first-max tie rule; allclose is kept
            # as the public semantic gate so the adapter never overclaims
            # bit-exact parity across alternate numeric backends.
            passed = all(
                np.allclose(
                    np.asarray(left),
                    np.asarray(right),
                    rtol=1.0e-12,
                    atol=1.0e-12,
                    equal_nan=True,
                )
                for left, right in zip(full_values, tiled_values)
            )
        else:
            passed = all(
                np.array_equal(np.asarray(left), np.asarray(right))
                for left, right in zip(full_values, tiled_values)
            )
    return {
        "operation": canonical,
        "scope": (
            "deterministic_numpy_ssim_halo_map_reduce"
            if canonical == "ssim_aot"
            else (
                "deterministic_numpy_ncc_output_map_reduce"
                if canonical in _NCC_ADAPTER_OPERATIONS
                else (
                    "deterministic_numpy_stitch_sequence_map_reduce"
                    if canonical in _STITCH_ADAPTER_OPERATIONS
                    else "deterministic_numpy_map_reduce"
                )
            )
        ),
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[0].shape, size=block_size).block_height,
            BlockGrid(arrays[0].shape, size=block_size).block_width,
        ),
        "passed": bool(passed),
        "max_abs_error": max_error,
        "native_runtime": False,
        "merge_order": "row-major_block_index",
        "halo": (
            _ssim_window_radius(int(values.get("window_size", 11)))
            if canonical == "ssim_aot"
            else 0
        ),
        "source_halo": (
            _ncc_source_halo(arrays[1])
            if canonical in _NCC_ADAPTER_OPERATIONS
            else None
        ),
        "output_shape": (
            list(_ncc_output_shape(arrays, values))
            if canonical in _NCC_ADAPTER_OPERATIONS
            else (
                list(np.asarray(arrays[3]).shape)
                if canonical in _STITCH_ADAPTER_OPERATIONS
                else None
            )
        ),
        "tile_order": (
            "row_major_origin_then_input_index"
            if canonical in _STITCH_ADAPTER_OPERATIONS
            else None
        ),
    }


def _merge_reference_output(output: Any, result: Any, block: BlockSpec) -> Any:
    values = result if isinstance(result, (tuple, list)) else (result,)
    destinations = output if isinstance(output, (tuple, list)) else (output,)
    if len(values) != len(destinations):
        raise ValueError("partition output arity mismatch")
    for destination, value in zip(destinations, values):
        destination[block.write_slice] = np.asarray(value)[block.core_slice]
    return output


def _run_analysis_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Run an explicit CPU multi-stage analysis contract.

    This executor is intentionally not folded into the generic local runner:
    Canny needs a global hysteresis convergence stage and CLAHE needs one
    shared histogram/LUT field.  Local blocks are still evaluated with their
    declared halo/output coordinates, then the global stage is run once in a
    deterministic order.  It is a semantic parity harness, not a native
    backend or GPU-overlap claim.
    """

    canonical = canonical_operation_name(operation)
    adapter = lookup_block_adapter(canonical)
    if (
        adapter is None
        or not adapter.partition_ready
        or adapter.metadata.get("partition_kind") != "multi_stage"
    ):
        raise ValueError(f"no complete multi-stage adapter registered for {canonical}")
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if len(arrays) != 1:
        raise ValueError(f"{canonical} analysis adapter expects one input")

    values = dict(params or {})
    if canonical == "canny_aot":
        source, low, high = _canny_parameters(arrays[0], values)
        threshold_state = np.empty(source.shape, dtype=np.float32)
        grid = BlockGrid(source.shape, size=block_size, halo=2)
        for block in tuple(sorted(tuple(grid), key=lambda item: int(item.index))):
            tile = np.ascontiguousarray(source[block.read_slice])
            local = _canny_local_prefix(tile, low, high)
            if tuple(local.shape) != tuple(block.read_shape):
                raise ValueError(f"canny_aot prefix shape mismatch at block {block.index}")
            threshold_state[block.write_slice] = local[block.core_slice]
        # Explicit stage boundary: no block-local hysteresis is allowed to
        # decide connectivity, because weak chains may cross any tile edge.
        return _canny_hysteresis_reference(threshold_state)

    source, clip, grid_shape, bins = _clahe_parameters(arrays[0], values)
    lut, tile_h, tile_w = _clahe_lut_reference(
        source,
        clip_limit=clip,
        tile_grid_size=grid_shape,
        num_bins=bins,
    )
    output = np.empty(source.shape, dtype=np.float32)
    grid = BlockGrid(source.shape, size=block_size, halo=0)
    for block in tuple(sorted(tuple(grid), key=lambda item: int(item.index))):
        tile = np.ascontiguousarray(source[block.read_slice])
        local = _clahe_interpolate_reference(
            tile,
            lut,
            tile_grid_size=grid_shape,
            tile_h=tile_h,
            tile_w=tile_w,
            block=block,
            source_origin=(block.read_y0, block.read_x0),
        )
        if tuple(local.shape) != tuple(block.shape):
            raise ValueError(f"clahe_aot interpolation shape mismatch at block {block.index}")
        output[block.write_slice] = np.rint(local).astype(np.float32, copy=False)
    return np.ascontiguousarray(output, dtype=np.float32)


def run_analysis_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> np.ndarray:
    """Public explicit entry point for a registered analysis stage contract."""

    return _run_analysis_tiled(
        operation,
        inputs,
        block_size=block_size,
        params=params,
    )


def verify_analysis_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full-frame and explicit stage-partitioned analysis results."""

    canonical = canonical_operation_name(operation)
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical, arrays, values)
    tiled = _run_analysis_tiled(
        canonical, arrays, block_size=block_size, params=values
    )
    left = np.asarray(full)
    right = np.asarray(tiled)
    error = float(np.max(np.abs(left.astype(np.float64) - right.astype(np.float64)))) if left.size else 0.0
    adapter = lookup_block_adapter(canonical)
    halo = int(adapter.contract.halo) if adapter is not None and adapter.contract is not None else 0
    return {
        "operation": canonical,
        "scope": "semantic_numpy_multistage",
        "backend": "cpu",
        "block_size": (
            BlockGrid(left.shape, size=block_size).block_height,
            BlockGrid(left.shape, size=block_size).block_width,
        ),
        "halo": halo,
        "stage_contract": dict(adapter.metadata.get("stage_contract", {})) if adapter else {},
        "passed": bool(np.allclose(left, right, rtol=float(rtol), atol=float(atol), equal_nan=True)),
        "max_abs_error": error,
        "native_runtime": False,
    }


def run_adapter_tiled(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
) -> Any:
    """Evaluate a registered adapter over a deterministic ``BlockGrid``."""

    adapter = lookup_block_adapter(operation)
    if adapter is None or not adapter.partition_ready:
        raise ValueError(f"no complete block adapter registered for {operation}")
    custom_executor = adapter.metadata.get("custom_executor")
    if callable(custom_executor):
        return custom_executor(
            operation,
            inputs,
            block_size=block_size,
            params=params,
        )
    if adapter.metadata.get("partition_kind") == "multi_stage":
        return _run_analysis_tiled(
            operation,
            inputs,
            block_size=block_size,
            params=params,
        )
    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    if not arrays or any(array.ndim < 2 for array in arrays):
        raise ValueError("adapter inputs must be at least two-dimensional")
    if any(array.shape[:2] != arrays[0].shape[:2] for array in arrays):
        raise ValueError("adapter inputs must share their first two dimensions")
    values = dict(params or {})
    reference = _reference(canonical_operation_name(operation), arrays, values)
    output = _allocate_output(reference)
    # Use the adapter's declared read halo.  The previous harness always used
    # zero, which could make a stencil adapter appear to pass while silently
    # reading an artificial tile edge.  A missing/unknown contract remains
    # fail-closed at halo=0 for legacy pointwise adapters.
    declared_halo = 0
    if adapter.contract is not None:
        try:
            declared_halo = int(adapter.contract.halo)
        except (TypeError, ValueError):
            declared_halo = 0
    grid = BlockGrid(arrays[0].shape, size=block_size, halo=max(0, declared_halo))
    for block in grid:
        context = PartitionContext(
            operation=canonical_operation_name(operation),
            inputs=arrays,
            block=block,
            full_shape=tuple(arrays[0].shape),
            params=values,
        )
        tile_context = adapter.reader(context, block) if adapter.reader else context
        result = adapter.runner(tile_context)
        if adapter.validator is not None and not adapter.validator(tile_context, result):
            raise ValueError(f"{operation} adapter rejected tile {block.index}")
        adapter.merger(output, result, block)
    return output


def _output_domain_shape(operation: str, params: Mapping[str, Any]) -> tuple[int, int]:
    values = dict(params)
    shape = values.get("shape")
    if shape is None:
        canonical = canonical_operation_name(operation)
        if canonical == "generate_brief_pattern":
            shape = (values.get("num_pairs", 256), 4)
        else:
            shape = (values.get("height", 0), values.get("width", 0))
    shape = tuple(int(value) for value in shape)
    if len(shape) != 2 or any(value <= 0 for value in shape):
        raise ValueError(f"{operation} requires a positive 2D output shape")
    return shape


def run_output_domain_tiled(
    operation: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    block_size: int | tuple[int, int] = 32,
) -> np.ndarray:
    """Evaluate a generated-output adapter over a virtual output grid."""

    adapter = lookup_block_adapter(operation)
    if adapter is None or not adapter.partition_ready:
        raise ValueError(f"no complete output-domain adapter registered for {operation}")
    if not adapter.metadata.get("output_domain"):
        raise ValueError(f"adapter {operation} is not output-domain qualified")
    values = dict(params or {})
    shape = _output_domain_shape(operation, values)
    reference = _reference(canonical_operation_name(operation), (), values)
    output = np.empty_like(reference)
    grid = BlockGrid(shape, size=block_size, halo=0)
    for block in grid:
        context = PartitionContext(
            operation=canonical_operation_name(operation),
            inputs=(),
            block=block,
            full_shape=shape,
            params=values,
        )
        tile_context = adapter.reader(context, block) if adapter.reader else context
        result = adapter.runner(tile_context)
        if adapter.validator is not None and not adapter.validator(tile_context, result):
            raise ValueError(f"{operation} output tile failed validation at block {block.index}")
        adapter.merger(output, result, block)
    return output


def verify_output_domain_parity(
    operation: str,
    *,
    params: Optional[Mapping[str, Any]] = None,
    block_size: int | tuple[int, int] = 32,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full generated output with deterministic tiled coordinates."""

    values = dict(params or {})
    shape = _output_domain_shape(operation, values)
    full = _reference(canonical_operation_name(operation), (), values)
    tiled = run_output_domain_tiled(
        operation, params=values, block_size=block_size
    )
    error = float(
        np.max(
            np.abs(
                np.asarray(full).astype(np.float64, copy=False)
                - np.asarray(tiled).astype(np.float64, copy=False)
            )
        )
    ) if np.asarray(full).size else 0.0
    return {
        "operation": canonical_operation_name(operation),
        "scope": "semantic_numpy_output_domain",
        "backend": "cpu",
        "shape": list(shape),
        "block_size": (
            BlockGrid(shape, size=block_size).block_height,
            BlockGrid(shape, size=block_size).block_width,
        ),
        "passed": bool(
            np.allclose(
                np.asarray(full),
                np.asarray(tiled),
                rtol=float(rtol),
                atol=float(atol),
                equal_nan=True,
            )
        ),
        "max_abs_error": error,
        "native_runtime": False,
    }


def verify_adapter_parity(
    operation: str,
    inputs: Sequence[np.ndarray],
    *,
    block_size: int | tuple[int, int] = 32,
    params: Optional[Mapping[str, Any]] = None,
    rtol: float = 0.0,
    atol: float = 0.0,
) -> dict[str, Any]:
    """Compare full-frame and tiled semantic results for one adapter.

    The report deliberately labels this ``semantic`` parity.  It is not a
    native Vulkan/OpenGL/CUDA execution proof and therefore cannot qualify
    those backends.
    """

    arrays = tuple(np.ascontiguousarray(value) for value in inputs)
    values = dict(params or {})
    full = _reference(canonical_operation_name(operation), arrays, values)
    tiled = run_adapter_tiled(
        operation, arrays, block_size=block_size, params=values
    )
    full_values = full if isinstance(full, (tuple, list)) else (full,)
    tiled_values = tiled if isinstance(tiled, (tuple, list)) else (tiled,)
    if len(full_values) != len(tiled_values):
        passed = False
        max_error = float("inf")
    else:
        errors = [
            float(np.max(np.abs(np.asarray(left).astype(np.float64) - np.asarray(right).astype(np.float64))))
            if np.asarray(left).size
            else 0.0
            for left, right in zip(full_values, tiled_values)
        ]
        max_error = max(errors, default=0.0)
        passed = all(
            np.allclose(np.asarray(left), np.asarray(right), rtol=rtol, atol=atol, equal_nan=True)
            for left, right in zip(full_values, tiled_values)
        )
    output_shapes = [list(np.asarray(value).shape) for value in tiled_values]
    expected_shapes = [list(np.asarray(value).shape) for value in full_values]
    return {
        "operation": canonical_operation_name(operation),
        "scope": "semantic_numpy",
        "backend": "cpu",
        "block_size": (
            BlockGrid(arrays[0].shape, size=block_size).block_height,
            BlockGrid(arrays[0].shape, size=block_size).block_width,
        ),
        "passed": bool(passed),
        "max_abs_error": max_error,
        "output_arity": len(tiled_values),
        "expected_output_arity": len(full_values),
        "output_shapes": output_shapes,
        "expected_output_shapes": expected_shapes,
        "native_runtime": False,
    }


LOW_RISK_ADAPTER_OPERATIONS = _ADAPTER_OPERATIONS
LOCAL_STENCIL_ADAPTER_OPERATIONS = _LOCAL_STENCIL_ADAPTER_OPERATIONS
LEGACY_LOCAL_ADAPTER_OPERATIONS = _LEGACY_LOCAL_ADAPTER_OPERATIONS
MAP_REDUCE_ADAPTER_OPERATIONS = _MAP_REDUCE_OPERATIONS
NCC_ADAPTER_OPERATIONS = _NCC_ADAPTER_OPERATIONS
STITCH_ADAPTER_OPERATIONS = _STITCH_ADAPTER_OPERATIONS
COORDINATE_ADAPTER_OPERATIONS = _COORDINATE_ADAPTER_OPERATIONS
COORDINATE_DOMAIN_ADAPTER_OPERATIONS = _COORDINATE_DOMAIN_ADAPTER_OPERATIONS
COORDINATE_WARP_ADAPTER_OPERATIONS = _COORDINATE_WARP_ADAPTER_OPERATIONS
OUTPUT_DOMAIN_ADAPTER_OPERATIONS = _OUTPUT_DOMAIN_ADAPTER_OPERATIONS
FLOW_MAP_ADAPTER_OPERATIONS = _FLOW_MAP_ADAPTER_OPERATIONS
NORMALIZATION_ADAPTER_OPERATIONS = _NORMALIZATION_ADAPTER_OPERATIONS
BRIEF_PATTERN_ADAPTER_OPERATIONS = _BRIEF_PATTERN_ADAPTER_OPERATIONS
ACCUMULATOR_ADAPTER_OPERATIONS = _ACCUMULATOR_ADAPTER_OPERATIONS
ANALYSIS_ADAPTER_OPERATIONS = _ANALYSIS_ADAPTER_OPERATIONS
GLOBAL_PARTITION_ADAPTER_OPERATIONS = _GLOBAL_PARTITION_ADAPTER_OPERATIONS
MTB_PARTITION_ADAPTER_OPERATIONS = _MTB_PARTITION_ADAPTER_OPERATIONS
JBLU_PARTITION_ADAPTER_OPERATIONS = _JBLU_PARTITION_ADAPTER_OPERATIONS
BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS = _BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS
INPAINT_PARTITION_ADAPTER_OPERATIONS = _INPAINT_PARTITION_ADAPTER_OPERATIONS
FFT_ADAPTER_OPERATIONS = _FFT_ADAPTER_OPERATIONS
OPTICAL_FLOW_ADAPTER_OPERATIONS = OPTICAL_FLOW_CONTRACT_OPERATIONS
OPTICAL_FLOW_IDENTITY_OPERATIONS = OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS
PHASE_CORRELATION_ADAPTER_OPERATIONS = _PHASE_CORRELATION_ADAPTER_OPERATIONS
AKAZE_ADAPTER_OPERATIONS = _AKAZE_ADAPTER_OPERATIONS
DEMOSAIC_HALF_ADAPTER_OPERATIONS = _DEMOSAIC_HALF_ADAPTER_OPERATIONS
DEMOSAIC_HALF_GAP_OPERATIONS = _DEMOSAIC_HALF_GAP_OPERATIONS
DEMOSAIC_FULL_ADAPTER_OPERATIONS = _DEMOSAIC_FULL_ADAPTER_OPERATIONS
BM3D_ADAPTER_OPERATIONS = _BM3D_ADAPTER_OPERATIONS


__all__ = [
    "PartitionContext",
    "LOW_RISK_ADAPTER_OPERATIONS",
    "LOCAL_STENCIL_ADAPTER_OPERATIONS",
    "LEGACY_LOCAL_ADAPTER_OPERATIONS",
    "MAP_REDUCE_ADAPTER_OPERATIONS",
    "NCC_ADAPTER_OPERATIONS",
    "STITCH_ADAPTER_OPERATIONS",
    "COORDINATE_ADAPTER_OPERATIONS",
    "COORDINATE_DOMAIN_ADAPTER_OPERATIONS",
    "COORDINATE_WARP_ADAPTER_OPERATIONS",
    "OUTPUT_DOMAIN_ADAPTER_OPERATIONS",
    "FLOW_MAP_ADAPTER_OPERATIONS",
    "NORMALIZATION_ADAPTER_OPERATIONS",
    "BRIEF_PATTERN_ADAPTER_OPERATIONS",
    "ACCUMULATOR_ADAPTER_OPERATIONS",
    "ANALYSIS_ADAPTER_OPERATIONS",
    "GLOBAL_PARTITION_ADAPTER_OPERATIONS",
    "MTB_PARTITION_ADAPTER_OPERATIONS",
    "JBLU_PARTITION_ADAPTER_OPERATIONS",
    "BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS",
    "INPAINT_PARTITION_ADAPTER_OPERATIONS",
    "FFT_ADAPTER_OPERATIONS",
    "OPTICAL_FLOW_CONTRACT_OPERATIONS",
    "OPTICAL_FLOW_ADAPTER_OPERATIONS",
    "OPTICAL_FLOW_IDENTITY_ADAPTER_OPERATIONS",
    "OPTICAL_FLOW_IDENTITY_OPERATIONS",
    "FEATURE_GEOMETRY_CONTRACT_OPERATIONS",
    "feature_geometry_partition_gap_report",
    "moving_optical_flow_partition_gap_report",
    "verify_moving_flow_translation_contract",
    "aggregate_moving_flow_candidate_evidence",
    "aggregate_native_moving_flow_candidates",
    "PHASE_CORRELATION_ADAPTER_OPERATIONS",
    "AKAZE_ADAPTER_OPERATIONS",
    "DEMOSAIC_HALF_ADAPTER_OPERATIONS",
    "DEMOSAIC_HALF_GAP_OPERATIONS",
    "DEMOSAIC_FULL_ADAPTER_OPERATIONS",
    "BM3D_ADAPTER_OPERATIONS",
    "BM3D_PARTITION_GAP_REASONS",
    "ensure_default_block_adapters",
    "default_block_adapter_registration_errors",
    "register_low_risk_block_adapters",
    "register_local_stencil_block_adapters",
    "register_legacy_local_block_adapters",
    "register_analysis_block_adapters",
    "register_fft_block_adapters",
    "register_phase_correlation_block_adapters",
    "register_akaze_block_adapters",
    "register_optical_flow_identity_adapters",
    "register_demosaic_half_adapters",
    "register_global_partition_adapters",
    "register_mtb_partition_adapters",
    "register_jblu_partition_adapters",
    "register_bilateral_grid_partition_adapters",
    "register_inpaint_partition_adapters",
    "register_map_reduce_block_adapters",
    "register_accumulator_block_adapters",
    "register_coordinate_block_adapters",
    "register_coordinate_domain_adapters",
    "register_coordinate_warp_adapters",
    "register_output_domain_adapters",
    "register_flow_map_adapters",
    "register_normalization_adapters",
    "register_brief_pattern_adapters",
    "register_demosaic_full_adapters",
    "register_bounded_semantic_adapters",
    "bm3d_partition_gap_report",
    "register_specialized_block_adapters",
    "run_adapter_tiled",
    "run_analysis_tiled",
    "run_fft_partition_tiled",
    "run_phase_correlation_partition_tiled",
    "run_akaze_keypoints_partition_tiled",
    "run_optical_flow_identity_partition_tiled",
    "run_global_partition_tiled",
    "run_mtb_partition_tiled",
    "run_jblu_partition_tiled",
    "run_bilateral_grid_partition_tiled",
    "run_inpaint_partition_tiled",
    "verify_analysis_parity",
    "verify_fft_parity",
    "verify_phase_correlation_parity",
    "verify_akaze_keypoint_parity",
    "verify_optical_flow_identity_parity",
    "run_demosaic_half_tiled",
    "verify_demosaic_half_parity",
    "demosaic_half_partition_gap_report",
    "verify_demosaic_full_parity",
    "demosaic_full_partition_gap_report",
    "run_demosaic_full_tiled",
    "verify_global_partition_parity",
    "GLOBAL_REDUCTION_CONTRACT_OPERATIONS",
    "global_reduction_partition_gap_report",
    "ITERATIVE_FEATURE_GAP_OPERATIONS",
    "iterative_feature_gap_report",
    "verify_mtb_partition_parity",
    "verify_jblu_partition_parity",
    "verify_bilateral_grid_partition_parity",
    "verify_inpaint_partition_parity",
    "run_coordinate_tiled",
    "run_output_domain_tiled",
    "run_adapter_map_reduce",
    "verify_adapter_parity",
    "verify_coordinate_parity",
    "verify_coordinate_warp_parity",
    "run_coordinate_warp_tiled",
    "verify_flow_maps_parity",
    "verify_normalize_image_parity",
    "optical_flow_partition_gap_report",
    "verify_output_domain_parity",
    "verify_map_reduce_parity",
]
