"""Dependency-light contracts shared by resident frame providers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Protocol

import numpy as np


SourceMode = Literal["rgb", "raw_rgb", "raw_native", "video_rgb"]
CarrierKind = Literal["rgb", "cfa"]


@dataclass(frozen=True)
class ResidentGeometry:
    """Canonical full/work geometry shared by RGB and RAW analysis paths.

    ``full_shape`` is always ``(height, width)``.  The effective work scales
    are resolved here once so providers cannot silently choose different
    dimensions for the same burst.
    """

    full_shape: tuple[int, int]
    align_shape: tuple[int, int]
    weight_shape: tuple[int, int]
    requested_align_scale: float
    requested_weight_scale: float
    effective_align_scale: float
    effective_weight_scale: float
    # ``None`` disables the generic work-size cap and makes the requested
    # scale authoritative.  The default stays bounded for compatibility.
    max_work_dimension: int | None = 2048

    @classmethod
    def resolve(
        cls,
        full_shape: tuple[int, int],
        *,
        align_scale: float,
        weight_scale: float,
        max_work_dimension: int | None = 2048,
    ) -> "ResidentGeometry":
        height, width = (max(1, int(full_shape[0])), max(1, int(full_shape[1])))
        max_dim = max(height, width)
        align_requested = float(align_scale)
        weight_requested = float(weight_scale)
        max_dimension_limit = (
            None
            if max_work_dimension is None
            else max(1, int(max_work_dimension))
        )
        if max_dimension_limit is not None and max_dim > max_dimension_limit:
            cap = float(max_dimension_limit) / float(max_dim)
            align_effective = min(align_requested, cap)
            weight_effective = min(weight_requested, cap)
        else:
            align_effective = align_requested
            weight_effective = weight_requested

        def _shape(scale: float) -> tuple[int, int]:
            return (
                max(32, int(height * float(scale))),
                max(32, int(width * float(scale))),
            )

        return cls(
            full_shape=(height, width),
            align_shape=_shape(align_effective),
            weight_shape=_shape(weight_effective),
            requested_align_scale=align_requested,
            requested_weight_scale=weight_requested,
            effective_align_scale=align_effective,
            effective_weight_scale=weight_effective,
            max_work_dimension=max_dimension_limit,
        )

    @property
    def full_to_align_scale(self) -> tuple[float, float]:
        return (
            float(self.align_shape[1]) / float(self.full_shape[1]),
            float(self.align_shape[0]) / float(self.full_shape[0]),
        )

    @property
    def full_to_weight_scale(self) -> tuple[float, float]:
        return (
            float(self.weight_shape[1]) / float(self.full_shape[1]),
            float(self.weight_shape[0]) / float(self.full_shape[0]),
        )


@dataclass
class ResidentAnalysisContext:
    """Shared analysis state owned by the resident lifecycle.

    Providers may attach carrier-specific state, but they must consume these
    same analysis objects rather than recomputing them independently.
    """

    geometry: ResidentGeometry
    analysis_params: Mapping[str, Any] = field(default_factory=dict)
    noise_score: float | None = None
    reference_proxy: Any = None
    alignment_reference: Any = None
    weight_reference: Any = None
    clahe_transfer_map: Any = None
    reference_transform_cache: Any = None


def scale_homography(
    homography: Any,
    *,
    source_shape: tuple[int, int],
    destination_shape: tuple[int, int],
) -> np.ndarray:
    """Convert a full-resolution support→reference H to another grid.

    Feature aligners estimate matrices in the full carrier coordinate system,
    while analysis proxies are sampled on a work grid.  Applying the matrix
    without this conjugation magnifies translations by ``1 / work_scale``.
    """

    matrix = np.asarray(homography, dtype=np.float32)
    if matrix.shape != (3, 3):
        raise ValueError(f"homography must have shape (3, 3), got {matrix.shape}")
    src_h, src_w = (float(source_shape[0]), float(source_shape[1]))
    dst_h, dst_w = (float(destination_shape[0]), float(destination_shape[1]))
    if src_h <= 0 or src_w <= 0 or dst_h <= 0 or dst_w <= 0:
        raise ValueError("homography coordinate shapes must be positive")
    sx = dst_w / src_w
    sy = dst_h / src_h
    scale = np.asarray(((sx, 0.0, 0.0), (0.0, sy, 0.0), (0.0, 0.0, 1.0)), dtype=np.float32)
    inv_scale = np.asarray(((1.0 / sx, 0.0, 0.0), (0.0, 1.0 / sy, 0.0), (0.0, 0.0, 1.0)), dtype=np.float32)
    result = scale @ matrix @ inv_scale
    if abs(float(result[2, 2])) > 1.0e-12:
        result = result / result[2, 2]
    return np.ascontiguousarray(result, dtype=np.float32)


@dataclass(frozen=True)
class FrameMetadata:
    source_id: str
    shape: tuple[int, ...]
    dtype: str
    color_model: str = "normalized_rgb"
    carrier_kind: CarrierKind = "rgb"
    orientation: int = 1
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ProviderFrame:
    carrier: Any
    metadata: FrameMetadata
    analysis_proxy: Any = None


@dataclass
class ResidentResult:
    value: Any
    mean_alpha: float = 1.0
    source_mode: SourceMode = "rgb"
    report: dict[str, Any] = field(default_factory=dict)


class FrameProvider(Protocol):
    source_mode: SourceMode
    carrier_kind: CarrierKind

    def load_reference(self) -> ProviderFrame:
        ...

    def load_support(self, index: int) -> ProviderFrame:
        ...

    def accumulate(self, frame: ProviderFrame, transform: Any, weight_map: Any) -> None:
        ...

    def finalize(self, mean_alpha: float = 1.0) -> ResidentResult:
        ...

    def close(self) -> None:
        ...


__all__ = [
    "CarrierKind",
    "FrameMetadata",
    "FrameProvider",
    "ResidentAnalysisContext",
    "ProviderFrame",
    "ResidentGeometry",
    "ResidentResult",
    "SourceMode",
    "scale_homography",
]
