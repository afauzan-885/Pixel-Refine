"""Parity verifier for the opt-in NativeTensor YUV preparation path."""

from __future__ import annotations

import argparse
import array
import json
from typing import Iterable

from .native_dispatch import NativeAOTEngine, NativeTensor
from .native_video_prep import prepare_yuv_native


def _rgb_samples() -> tuple[int, int, tuple[tuple[int, int, int], ...]]:
    pixels = (
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255),
        (12, 34, 56), (78, 90, 123), (145, 167, 189), (201, 223, 245),
        (5, 250, 15), (25, 35, 245), (125, 15, 205), (245, 125, 15),
        (64, 64, 64), (128, 128, 128), (192, 192, 192), (1, 2, 3),
    )
    return 4, 4, pixels


def _tensor_from_pixels(pixels: Iterable[tuple[int, int, int]], shape: tuple[int, int, int]) -> NativeTensor:
    storage = array.array("f", (float(value) for pixel in pixels for value in pixel))
    return NativeTensor.from_buffer(storage, shape, "f32")


def _ycbcr(pixel: tuple[int, int, int]) -> tuple[float, float, float]:
    red, green, blue = pixel
    return (
        0.299 * red + 0.587 * green + 0.114 * blue,
        -0.168736 * red - 0.331264 * green + 0.5 * blue + 128.0,
        0.5 * red - 0.418688 * green - 0.081312 * blue + 128.0,
    )


def _values(tensor: NativeTensor) -> list[float]:
    return list(array.array("f", tensor.buffer.cast("f")))


def _assert_close(actual: Iterable[float], expected: Iterable[float], *, tolerance: float = 2e-4) -> None:
    actual_values = list(actual)
    expected_values = list(expected)
    if len(actual_values) != len(expected_values):
        raise AssertionError(f"length mismatch: {len(actual_values)} != {len(expected_values)}")
    for index, (got, want) in enumerate(zip(actual_values, expected_values)):
        if abs(got - want) > tolerance:
            raise AssertionError(f"value mismatch at {index}: {got} != {want}")


def verify(backend: str = "cpu", device_id: int = 0) -> dict[str, object]:
    height, width, pixels = _rgb_samples()
    rgb = _tensor_from_pixels(pixels, (height, width, 3))
    checks: list[str] = []
    with NativeAOTEngine(backend, device_id=device_id) as active_engine:
        result_444 = prepare_yuv_native(rgb, subsampling="444", engine=active_engine)
        expected_444 = [component for pixel in pixels for component in _ycbcr(pixel)]
        _assert_close(_values(result_444["ycbcr"]), expected_444)
        checks.append("444")

        result_422 = prepare_yuv_native(rgb, subsampling="422", engine=active_engine)
        expected_y = [_ycbcr(pixel)[0] for pixel in pixels]
        _assert_close(_values(result_422["y"]), expected_y)
        expected_422_chroma: list[float] = []
        for row in range(height):
            row_pixels = pixels[row * width:(row + 1) * width]
            for column in range(0, width, 2):
                left = _ycbcr(row_pixels[column])
                right = _ycbcr(row_pixels[column + 1])
                expected_422_chroma.extend(((left[1] + right[1]) * 0.5, (left[2] + right[2]) * 0.5))
        _assert_close(_values(result_422["chroma"]), expected_422_chroma)
        checks.append("422")

        result_420 = prepare_yuv_native(rgb, subsampling="420", engine=active_engine)
        _assert_close(_values(result_420["y"]), expected_y)
        expected_420_chroma: list[float] = []
        for row in range(0, height, 2):
            for column in range(0, width, 2):
                block = [_ycbcr(pixels[(row + dy) * width + column + dx]) for dy in range(2) for dx in range(2)]
                expected_420_chroma.extend((sum(value[1] for value in block) * 0.25, sum(value[2] for value in block) * 0.25))
        _assert_close(_values(result_420["chroma"]), expected_420_chroma)
        checks.append("420")

        try:
            prepare_yuv_native(_tensor_from_pixels(pixels[:12], (4, 3, 3)), subsampling="422", engine=active_engine)
            prepare_yuv_native(_tensor_from_pixels(pixels[:12], (3, 4, 3)), subsampling="420", engine=active_engine)
        except ValueError:
            checks.append("alignment-rejection")
        else:
            raise AssertionError("invalid format alignment was accepted")

    return {
        "backend": backend,
        "device_id": int(device_id),
        "passed": len(checks),
        "checks": tuple(checks),
        "host_fallback": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()
    print(json.dumps(verify(args.backend, args.device), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
