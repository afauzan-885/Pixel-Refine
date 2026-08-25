"""Deterministic ARM64 block/memory simulation (no native execution).

This module is intentionally a *planning* aid for hosts that do not have an
AArch64 device.  It exercises the same shape-aware memory policy used by the
runtime and checks that a proposed tile partition covers an image exactly
once.  It does not load a bridge, execute a TCM, or promote an artifact to
``native_runtime``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any, Sequence

from taichi_vision.taichi_aot.memory import MemoryGovernor, MemorySnapshot


_DTYPE_ALIASES = {
    # Canonical transport dtypes used by the AOT boundary.
    "u8": 1,
    "uint8": 1,
    "u16": 2,
    "uint16": 2,
    "i16": 2,
    "int16": 2,
    "f16": 2,
    "float16": 2,
    "f32": 4,
    "float32": 4,
    # NumPy/PEP-3118 spellings which are unambiguous for the supported set.
    "u1": 1,
    "u2": 2,
    "i2": 2,
    "f2": 2,
    "f4": 4,
    "byte": 1,
    "half": 2,
    "single": 4,
}

_DTYPE_CANONICAL = {
    "u8": "u8", "uint8": "u8", "u1": "u8", "byte": "u8",
    "u16": "u16", "uint16": "u16", "u2": "u16",
    "i16": "i16", "int16": "i16", "i2": "i16",
    "f16": "f16", "float16": "f16", "f2": "f16", "half": "f16",
    "f32": "f32", "float32": "f32", "f4": "f32", "single": "f32",
}


@dataclass(frozen=True)
class Arm64SimulationReport:
    """Serializable result of an offline ARM64 planning simulation."""

    target: str
    qualification: str
    native_runtime: bool
    shape: tuple[int, int]
    channels: int
    dtype: str
    sample_bytes: int
    block_size: int
    block_rows: int
    block_cols: int
    block_count: int
    covered_pixels: int
    expected_pixels: int
    coverage_complete: bool
    estimated_peak_bytes: int
    available_bytes: int
    within_budget: bool
    pressure: str = "healthy"
    recommended_block_size: int = 2048

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _strict_positive_int(value: Any, label: str) -> int:
    """Parse simulation metadata without truncating unsafe values."""

    if isinstance(value, bool):
        raise ValueError(f"{label} must be a positive integer")
    try:
        integer = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{label} must be a positive integer") from exc
    try:
        exact = float(value) == float(integer)
    except (TypeError, ValueError, OverflowError):
        exact = False
    if not exact or integer <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return integer


def _shape_2d(shape: Sequence[int], channels: int) -> tuple[int, int]:
    try:
        raw_values = tuple(shape)
    except TypeError as exc:
        raise ValueError("shape must be a sequence of 2 or 3 dimensions") from exc
    if len(raw_values) not in (2, 3):
        raise ValueError(
            "shape must contain 2 or 3 dimensions (height, width, optional channels)"
        )
    height = _strict_positive_int(raw_values[0], "shape height")
    width = _strict_positive_int(raw_values[1], "shape width")
    if len(raw_values) == 3:
        shape_channels = _strict_positive_int(raw_values[2], "shape channels")
        if shape_channels != channels:
            raise ValueError(
                f"shape channel count ({shape_channels}) does not match channels ({channels})"
            )
    return height, width


def _dtype_info(dtype: str) -> tuple[str, int]:
    # Accept NumPy scalar/dtype objects without importing NumPy into this
    # lightweight planner (``np.dtype('f32').name`` is already canonical).
    raw = getattr(dtype, "name", None)
    if raw is None:
        raw = getattr(dtype, "__name__", dtype)
    key = str(raw).strip().lower().replace(" ", "")
    # ``str(np.uint8)`` is ``<class 'numpy.uint8'>``; retain only the final
    # scalar token instead of importing NumPy into this lightweight planner.
    if "." in key:
        key = key.rsplit(".", 1)[-1]
    key = key.rstrip(">'")
    try:
        return _DTYPE_CANONICAL[key], _DTYPE_ALIASES[key]
    except KeyError as exc:
        raise ValueError(
            "unsupported simulation dtype; expected u8/u16/i16/f16/f32"
        ) from exc


def simulate_arm64_block_plan(
    target: str,
    shape: Sequence[int],
    *,
    dtype: str = "f32",
    channels: int = 3,
    total_bytes: int = 16 * 1024**3,
    available_bytes: int = 8 * 1024**3,
    block_size: int | None = None,
    live_buffers: int = 4,
) -> Arm64SimulationReport:
    """Plan ARM64 tiles against synthetic memory telemetry.

    ``target`` is metadata only and must identify an ARM64 profile.  The
    result is marked ``qualification=simulated`` and ``native_runtime=False``
    even when all structural checks pass.  This makes it suitable for CI
    coverage without accidentally advertising device execution.
    """

    target_key = str(target).strip().lower()
    if not target_key or not any(
        token in {"arm64", "aarch64"}
        for token in target_key.replace("-", "_").split("_")
    ):
        raise ValueError("ARM64 simulator requires an arm64/aarch64 target")
    channels = _strict_positive_int(channels, "channels")
    height, width = _shape_2d(shape, channels)
    normalized_dtype, sample_bytes = _dtype_info(dtype)
    live_buffers = _strict_positive_int(live_buffers, "live_buffers")
    try:
        total_bytes = int(total_bytes)
        available_bytes = int(available_bytes)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("memory telemetry must be integer byte counts") from exc
    if isinstance(total_bytes, bool) or isinstance(available_bytes, bool):
        raise ValueError("memory telemetry must be integer byte counts")
    if total_bytes <= 0 or available_bytes < 0 or available_bytes > total_bytes:
        raise ValueError("memory telemetry must satisfy 0 <= available <= total")

    governor = MemoryGovernor(
        provider=lambda: MemorySnapshot(total_bytes, available_bytes, 0.0),
        configured_max_bytes=None,
        sample_interval=0.05,
    )
    recommended = governor.recommend_block_size(
        channels=channels, sample_bytes=sample_bytes, live_buffers=live_buffers,
        force=True,
    )
    if block_size is None:
        requested_side = recommended
    else:
        requested_side = _strict_positive_int(block_size, "block_size")
    # Explicit requests are hints, not permission to bypass adaptive memory
    # policy.  Clamp to the current governor recommendation so the simulator
    # models the same safety invariant as the native planner.
    side = min(requested_side, recommended)
    if side < 256 or side > 2048:
        raise ValueError("block_size must be within the 256..2048 contract")

    rows = math.ceil(height / side)
    cols = math.ceil(width / side)
    block_count = rows * cols
    covered = 0
    peak = 0
    for row in range(rows):
        tile_height = min(side, height - row * side)
        for col in range(cols):
            tile_width = min(side, width - col * side)
            pixels = tile_height * tile_width
            covered += pixels
            peak = max(peak, pixels * channels * sample_bytes * live_buffers)

    # Do not use the synthetic shared budget as a device-runtime claim; the
    # report only says whether this *plan* fits the selected telemetry.
    return Arm64SimulationReport(
        target=str(target), qualification="simulated", native_runtime=False,
        shape=(height, width), channels=channels, dtype=normalized_dtype,
        sample_bytes=sample_bytes, block_size=side, block_rows=rows,
        block_cols=cols, block_count=block_count, covered_pixels=covered,
        expected_pixels=height * width, coverage_complete=covered == height * width,
        estimated_peak_bytes=peak, available_bytes=available_bytes,
        within_budget=peak <= available_bytes,
        pressure=governor.refresh(force=True).pressure.name.lower(),
        recommended_block_size=recommended,
    )


__all__ = ["Arm64SimulationReport", "simulate_arm64_block_plan"]
