"""Dependency-free AV1 intra prediction reference helpers.

The numeric Taichi graph with the same contract is compiled as
``compression_av1_dc_predict_residual_4x4``.  This module is the small,
auditable host reference used by tests and by the future tile serializer; it
does not serialize AV1 symbols or claim to be a complete encoder.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass


AV1_DC_BLOCK_SIZE = 4
AV1_8BIT_MIDPOINT = 128


class AV1PredictionError(ValueError):
    """Invalid or unsupported AV1 prediction input."""


@dataclass(frozen=True)
class AV1DCResidualPlane:
    """Exact result of one 8-bit plane's 4x4 DC prediction pass."""

    height: int
    width: int
    residual: tuple[int, ...]
    reconstructed: tuple[int, ...]


def _validate_plane(samples: Sequence[int], height: int, width: int) -> tuple[int, ...]:
    if isinstance(height, bool) or not isinstance(height, int) or height <= 0:
        raise AV1PredictionError("height must be a positive integer")
    if isinstance(width, bool) or not isinstance(width, int) or width <= 0:
        raise AV1PredictionError("width must be a positive integer")
    try:
        values = tuple(int(value) for value in samples)
    except (TypeError, ValueError) as exc:
        raise AV1PredictionError("plane must be an integer sequence") from exc
    if len(values) != height * width:
        raise AV1PredictionError("plane length does not match height*width")
    if any(value < 0 or value > 255 for value in values):
        raise AV1PredictionError("the first profile accepts 8-bit samples only")
    return values


def av1_dc_predict_residual_4x4(
    samples: Sequence[int], height: int, width: int
) -> AV1DCResidualPlane:
    """Return lossless 4x4 ``DC_PRED`` residuals and reconstruction.

    The top and left edges are taken from the source plane.  This is equivalent
    to using already reconstructed edges for a lossless raster tile because
    every earlier block reconstructs exactly.  At a frame edge the available
    edge samples are averaged with AV1's rounded integer rule; a block with no
    available edge uses the 8-bit midpoint.
    """

    source = _validate_plane(samples, height, width)
    residual = [0] * len(source)
    reconstructed = [0] * len(source)
    for y in range(height):
        for x in range(width):
            block_y = y // AV1_DC_BLOCK_SIZE
            block_x = x // AV1_DC_BLOCK_SIZE
            y0 = block_y * AV1_DC_BLOCK_SIZE
            x0 = block_x * AV1_DC_BLOCK_SIZE
            top_count = min(AV1_DC_BLOCK_SIZE, width - x0)
            left_count = min(AV1_DC_BLOCK_SIZE, height - y0)
            ref_sum = 0
            ref_count = 0
            if block_y:
                ref_sum += sum(source[(y0 - 1) * width + x0 + i] for i in range(top_count))
                ref_count += top_count
            if block_x:
                ref_sum += sum(source[(y0 + i) * width + x0 - 1] for i in range(left_count))
                ref_count += left_count
            prediction = (
                AV1_8BIT_MIDPOINT
                if ref_count == 0
                else (ref_sum + ref_count // 2) // ref_count
            )
            index = y * width + x
            residual[index] = source[index] - prediction
            reconstructed[index] = prediction + residual[index]
    return AV1DCResidualPlane(
        height=height,
        width=width,
        residual=tuple(residual),
        reconstructed=tuple(reconstructed),
    )


def av1_dc_predict_capability_report() -> dict[str, object]:
    """Describe the bounded numeric stage without overstating AV1 support."""

    return {
        "codec": "AV1",
        "profile": "4x4-dc-prediction-residual-8bit",
        "native_runtime": True,
        "lossless_reconstruction": True,
        "arbitrary_plane_dimensions": True,
        "bit_depth": 8,
        "chroma_formats": ("400", "420"),
        "graph_name": "compression_av1_dc_predict_residual_4x4",
        "runtime_dependencies": (),
        "complete_frame_encoder": False,
    }


__all__ = [
    "AV1_8BIT_MIDPOINT",
    "AV1_DC_BLOCK_SIZE",
    "AV1DCResidualPlane",
    "AV1PredictionError",
    "av1_dc_predict_capability_report",
    "av1_dc_predict_residual_4x4",
]
