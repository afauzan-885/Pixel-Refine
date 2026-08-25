"""Standalone no-NumPy verifier for the direct native compression bridge.

It loads only the three native-buffer modules by file path, so importing this
verifier does not execute the legacy ``taichi_algorithm`` or ``taichi_aot``
package initializers.  That makes the dependency claim observable rather than
assuming that a normal application import has the same closure.
"""

from __future__ import annotations

import argparse
import importlib.util
import array
import json
import pathlib
import sys
import types


def _load_stack():
    root = pathlib.Path(__file__).resolve().parents[3]
    package_paths = {
        "taichi_vision": root / "taichi_vision",
        "taichi_vision.taichi_algorithm": root / "taichi_vision" / "taichi_algorithm",
        "taichi_vision.taichi_algorithm.compression": root / "taichi_vision" / "taichi_algorithm" / "compression",
        "taichi_vision.taichi_aot": root / "taichi_vision" / "taichi_aot",
    }
    for name, path in package_paths.items():
        package = types.ModuleType(name)
        package.__path__ = [str(path)]
        sys.modules[name] = package

    def load(name: str, path: pathlib.Path):
        spec = importlib.util.spec_from_file_location(name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load native module {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

    compression = root / "taichi_vision" / "taichi_algorithm" / "compression"
    abi = load("taichi_vision.taichi_aot.native_codec_abi", root / "taichi_vision" / "taichi_aot" / "native_codec_abi.py")
    dispatch = load("taichi_vision.taichi_algorithm.compression.native_dispatch", compression / "native_dispatch.py")
    prep = load("taichi_vision.taichi_algorithm.compression.native_video_prep", compression / "native_video_prep.py")
    verify = load("taichi_vision.taichi_algorithm.compression.verify_native_video_prep", compression / "verify_native_video_prep.py")
    predictor = load(
        "taichi_vision.taichi_algorithm.compression.av1_predict_aot",
        compression / "av1_predict_aot.py",
    )
    return abi, dispatch, prep, verify, predictor


def _verify_hevc_dc_levels(abi, dispatch, backend: str, device_id: int) -> None:
    """Exercise the newly compiled HEVC DC-level graph through the C bridge."""

    residual_storage = array.array("i", (-128, 0, 88, -112))
    residuals = abi.NativeTensor.from_buffer(residual_storage, (4,), "i32")
    levels = abi.NativeTensor.allocate((4,), "i32")
    request = dispatch.build_native_request(
        "compression_image",
        "compression_hevc_dc_levels",
        (residuals,),
        outputs=(levels,),
        scalars={"count": 4, "block_size": 8, "level_divisor": 4},
        backend=backend,
        input_names=("residuals",),
        output_names=("levels",),
    )
    with dispatch.NativeAOTEngine(backend, device_id=device_id) as engine:
        engine.run_native_graph(request)
    actual = list(array.array("i", levels.buffer.cast("i")))
    expected = [-410, 0, 282, -358]
    if actual != expected:
        raise AssertionError(f"HEVC DC-level graph mismatch: {actual} != {expected}")


def _verify_av1_dc_predictor(abi, dispatch, predictor, backend: str, device_id: int) -> None:
    """Exercise the native AV1 4x4 DC residual preparation graph."""

    height, width = 8, 10
    source_values = [
        (y * 37 + x * 19 + (y ^ x) * 3) & 0xFF
        for y in range(height)
        for x in range(width)
    ]
    source_storage = array.array("i", source_values)
    source = abi.NativeTensor.from_buffer(source_storage, (height, width), "i32")
    residual = abi.NativeTensor.allocate((height, width), "i32")
    reconstructed = abi.NativeTensor.allocate((height, width), "i32")
    request = dispatch.build_native_request(
        "compression_image",
        "compression_av1_dc_predict_residual_4x4",
        (source,),
        outputs=(residual, reconstructed),
        scalars={"height": height, "width": width},
        backend=backend,
        input_names=("src",),
        output_names=("residual", "reconstructed"),
    )
    with dispatch.NativeAOTEngine(backend, device_id=device_id) as engine:
        engine.run_native_graph(request)
    actual_residual = list(array.array("i", residual.buffer.cast("i")))
    actual_reconstructed = list(array.array("i", reconstructed.buffer.cast("i")))

    reference = predictor.av1_dc_predict_residual_4x4(source_values, height, width)
    expected_residual = list(reference.residual)
    expected_reconstructed = list(reference.reconstructed)
    if actual_residual != expected_residual:
        raise AssertionError(
            f"AV1 DC residual graph mismatch: actual={actual_residual} expected={expected_residual}"
        )
    if actual_reconstructed != expected_reconstructed:
        raise AssertionError("AV1 DC reconstruction graph is not exact")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="cpu")
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()
    abi, dispatch, _prep, verify, predictor = _load_stack()
    result = dict(verify.verify(args.backend, args.device))
    _verify_hevc_dc_levels(abi, dispatch, args.backend, args.device)
    _verify_av1_dc_predictor(abi, dispatch, predictor, args.backend, args.device)
    result["checks"] = tuple(result.get("checks", ())) + (
        "hevc-dc-levels",
        "av1-dc-predictor",
    )
    result["passed"] = int(result.get("passed", 0)) + 2
    result["numpy_loaded"] = "numpy" in sys.modules
    if result["numpy_loaded"]:
        raise RuntimeError("native bridge verifier imported NumPy")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
