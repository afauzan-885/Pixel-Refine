"""NumPy-free Y/Cb/Cr preparation through the compression TCM.

This is an additive low-level API for callers that already own contiguous
``NativeTensor`` buffers.  It deliberately accepts an explicitly padded
8-bit RGB ``f32`` tensor and returns native output tensors; it never converts
through the legacy Python AOT wrapper and never enables a host fallback.
Variable-length HEVC/AV1 syntax remains outside this numeric preparation
stage.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from .native_dispatch import (
    NativeAOTEngine,
    NativeGraphRequest,
    NativeTensor,
    NativeDispatchContractError,
    build_native_request,
)


_SUBSAMPLING = {"444": "444", "422": "422", "420": "420"}


def _normalize_mode(subsampling: str) -> str:
    mode = str(subsampling).replace(":", "")
    try:
        return _SUBSAMPLING[mode]
    except KeyError as exc:
        raise ValueError("subsampling must be 444, 422, or 420") from exc


def _validate_rgb_tensor(rgb: NativeTensor) -> tuple[int, int]:
    if not isinstance(rgb, NativeTensor):
        raise NativeDispatchContractError("rgb must be a NativeTensor")
    if rgb.dtype_code != "f32" or rgb.vector_dim is not None or rgb.shape[-1:] != (3,):
        raise NativeDispatchContractError(
            "rgb must be a scalar-layout NativeTensor with shape (height, width, 3) and dtype f32"
        )
    if len(rgb.shape) != 3:
        raise NativeDispatchContractError("rgb must have exactly three dimensions")
    height, width, channels = rgb.shape
    if height <= 0 or width <= 0 or channels != 3:
        raise NativeDispatchContractError("rgb dimensions must be positive and have three channels")
    return int(height), int(width)


def prepare_yuv_native(
    rgb: NativeTensor,
    *,
    subsampling: str = "420",
    engine: Optional[NativeAOTEngine] = None,
) -> Mapping[str, Any]:
    """Run the RGB-to-Y/Cb/Cr graph without NumPy or host fallback.

    The input dimensions must already satisfy the selected format: 4:2:2
    requires an even width and 4:2:0 requires even width and height.  Padding
    is intentionally explicit so a caller cannot accidentally encode hidden
    edge pixels.
    """

    mode = _normalize_mode(subsampling)
    height, width = _validate_rgb_tensor(rgb)
    if mode in {"422", "420"} and width % 2:
        raise ValueError(f"4:{mode[1:]} native preparation requires an even width")
    if mode == "420" and height % 2:
        raise ValueError("4:2:0 native preparation requires an even height")

    owns_engine = engine is None
    active_engine = engine or NativeAOTEngine()
    try:
        if mode == "444":
            ycbcr = NativeTensor.allocate((height, width, 3), "f32")
            request = build_native_request(
                "compression_image",
                "compression_rgb_to_ycbcr",
                (rgb,),
                outputs=(ycbcr,),
                scalars={"h": height, "w": width},
                backend=active_engine.backend,
                input_names=("src",),
                output_names=("dst",),
            )
            active_engine.run_native_graph(request)
            return {
                "ycbcr": ycbcr,
                "width": width,
                "height": height,
                "padded_width": width,
                "padded_height": height,
                "bit_depth": 8,
                "subsampling": mode,
                "used_host_fallback": False,
            }

        chroma_height = height if mode == "422" else height // 2
        chroma_width = width // 2
        y = NativeTensor.allocate((height, width), "f32")
        chroma = NativeTensor.allocate((chroma_height, chroma_width, 2), "f32")
        graph = (
            "compression_rgb_to_ycbcr_422_pair"
            if mode == "422"
            else "compression_rgb_to_ycbcr_420_pair"
        )
        request = build_native_request(
            "compression_image",
            graph,
            (rgb,),
            outputs=(y, chroma),
            scalars={"h": height, "w": width},
            backend=active_engine.backend,
            input_names=("src",),
            output_names=("y_dst", "chroma_dst"),
        )
        active_engine.run_native_graph(request)
        return {
            "y": y,
            "chroma": chroma,
            "width": width,
            "height": height,
            "padded_width": width,
            "padded_height": height,
            "bit_depth": 8,
            "subsampling": mode,
            "used_host_fallback": False,
        }
    finally:
        if owns_engine:
            active_engine.close()


def prepare_av1_dc_residual_native(
    plane: NativeTensor,
    *,
    engine: Optional[NativeAOTEngine] = None,
) -> Mapping[str, Any]:
    """Run the bounded AV1 8-bit 4x4 DC residual graph natively.

    The input is a scalar ``i32`` plane.  Keeping samples in a signed integer
    tensor avoids an implicit dtype conversion at the ABI boundary; values
    are still required to be valid 8-bit samples by the caller's input
    contract.  The returned reconstruction is exact for the lossless graph.
    """

    if not isinstance(plane, NativeTensor):
        raise NativeDispatchContractError("plane must be a NativeTensor")
    if plane.dtype_code != "i32" or plane.vector_dim is not None or len(plane.shape) != 2:
        raise NativeDispatchContractError("plane must be a scalar-layout i32 tensor with shape (height, width)")
    height, width = (int(plane.shape[0]), int(plane.shape[1]))
    owns_engine = engine is None
    active_engine = engine or NativeAOTEngine()
    try:
        residual = NativeTensor.allocate((height, width), "i32")
        reconstructed = NativeTensor.allocate((height, width), "i32")
        request = build_native_request(
            "compression_image",
            "compression_av1_dc_predict_residual_4x4",
            (plane,),
            outputs=(residual, reconstructed),
            scalars={"height": height, "width": width},
            backend=active_engine.backend,
            input_names=("src",),
            output_names=("residual", "reconstructed"),
        )
        active_engine.run_native_graph(request)
        return {
            "residual": residual,
            "reconstructed": reconstructed,
            "width": width,
            "height": height,
            "bit_depth": 8,
            "block_size": 4,
            "used_host_fallback": False,
        }
    finally:
        if owns_engine:
            active_engine.close()


def native_video_prep_capability_report() -> Mapping[str, Any]:
    return {
        "available": True,
        "dtype": "f32",
        "bit_depth": 8,
        "subsampling": ("444", "422", "420"),
        "native_buffer_abi": True,
        "host_fallback": False,
        "variable_length_codec_syntax": False,
        "av1_dc_predictor_graph": True,
        "fail_closed": True,
    }


__all__ = [
    "prepare_yuv_native",
    "prepare_av1_dc_residual_native",
    "native_video_prep_capability_report",
]
