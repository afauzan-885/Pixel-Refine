"""Targeted PNG verifier for the native Taichi/TCM compression path.

The encoder under test does not import Pillow, zlib, or another codec.  This
module is intentionally a validation helper: NumPy creates expected arrays,
FFmpeg decodes the resulting PNG only at the external parity boundary, and
the report records whether the selected run was required to use TCM.

Example (CPU TCM):

    $env:AOT_MODE = "1"
    $env:AOT_ARCH = "cpu"
    $env:AOT_ALLOW_HOST_FALLBACK = "0"
    python -m taichi_vision.taichi_algorithm.compression.verify_png_aot --require-tcm
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from .png_aot import (
    _as_png_bytes,
    _filter_rows,
    _filter_rows_host,
    deflate_stored,
    encode_png_aot,
    inflate_deflate,
    parse_png_aot,
)


def _external_decoder() -> str | None:
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    return None


def _ffmpeg_pixel_format(image: np.ndarray) -> str:
    channels = 1 if image.ndim == 2 else int(image.shape[2])
    if image.dtype == np.uint8:
        return {1: "gray", 2: "ya8", 3: "rgb24", 4: "rgba"}[channels]
    if image.dtype == np.uint16:
        return {1: "gray16le", 2: "ya16le", 3: "rgb48le", 4: "rgba64le"}[channels]
    raise TypeError("PNG verifier supports uint8 and uint16 arrays only")


def _decode_ffmpeg(payload: bytes, expected: np.ndarray) -> tuple[np.ndarray, str]:
    executable = shutil.which("ffmpeg")
    if executable is None:
        raise RuntimeError("ffmpeg is not installed")
    pixel_format = _ffmpeg_pixel_format(expected)
    channels = 1 if expected.ndim == 2 else int(expected.shape[2])
    with tempfile.TemporaryDirectory(prefix="pixel_refine_png_verify_") as directory:
        source = Path(directory) / "encoded.png"
        decoded_path = Path(directory) / "decoded.raw"
        source.write_bytes(bytes(payload))
        result = subprocess.run(
            [
                executable,
                "-v",
                "error",
                "-i",
                str(source),
                "-frames:v",
                "1",
                "-f",
                "rawvideo",
                "-pix_fmt",
                pixel_format,
                "-y",
                str(decoded_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "FFmpeg PNG decode failed")
        raw = decoded_path.read_bytes()
    dtype = np.dtype("<u2") if expected.dtype == np.uint16 else np.dtype(np.uint8)
    values = np.frombuffer(raw, dtype=dtype)
    shape = expected.shape if expected.ndim == 2 else expected.shape
    expected_count = int(np.prod(shape))
    if values.size != expected_count:
        raise AssertionError(
            f"external PNG decode size mismatch: {values.size} != {expected_count} "
            f"for {shape} / {pixel_format} / {channels} channels"
        )
    return values.reshape(shape), "ffmpeg"


def _decode_external(payload: bytes, expected: np.ndarray) -> tuple[np.ndarray, str]:
    decoder = _external_decoder()
    if decoder == "ffmpeg":
        return _decode_ffmpeg(payload, expected)
    raise RuntimeError("no external PNG decoder is available")


def _runtime_import_audit() -> dict[str, object]:
    source = Path(__file__).with_name("png_aot.py")
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    forbidden_roots = {
        "cv2",
        "PIL",
        "imageio",
        "imagecodecs",
        "zlib",
        "libpng",
        "png",
        "pypng",
    }
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.append(node.module)
    forbidden = sorted(
        module for module in imports if module.split(".", 1)[0] in forbidden_roots
    )
    return {
        "codec_imports": forbidden,
        "codec_runtime_clean": not forbidden,
        "numpy_host_abi": any(module.split(".", 1)[0] == "numpy" for module in imports),
    }


def _synthetic_cases() -> tuple[tuple[str, np.ndarray], ...]:
    rng = np.random.default_rng(20260810)
    gray8 = np.arange(19 * 23, dtype=np.uint8).reshape(19, 23)
    rgb8 = np.stack(
        (
            np.arange(17 * 29, dtype=np.uint8).reshape(17, 29),
            np.full((17, 29), 113, dtype=np.uint8),
            np.flipud(np.arange(17 * 29, dtype=np.uint8).reshape(17, 29)),
        ),
        axis=-1,
    )
    rgba8 = rng.integers(0, 256, (13, 21, 4), dtype=np.uint8)
    gray16 = rng.integers(0, 65536, (11, 17), dtype=np.uint16)
    rgb16 = rng.integers(0, 65536, (9, 13, 3), dtype=np.uint16)
    rgba16 = rng.integers(0, 65536, (7, 11, 4), dtype=np.uint16)
    return (
        ("gray8", gray8),
        ("rgb8", rgb8),
        ("rgba8", rgba8),
        ("gray16", gray16),
        ("rgb16", rgb16),
        ("rgba16", rgba16),
    )


def run_png_verification(*, require_tcm: bool = False) -> dict[str, object]:
    if require_tcm and os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0") == "1":
        raise AssertionError("--require-tcm cannot run with AOT_ALLOW_HOST_FALLBACK=1")
    if require_tcm and os.environ.get("AOT_MODE", "1").lower() not in {
        "1",
        "true",
        "yes",
    }:
        raise AssertionError("--require-tcm requires AOT_MODE=1")
    decoder = _external_decoder()
    if decoder is None:
        raise RuntimeError(
            "exact external PNG decoder is unavailable (need FFmpeg or Pillow)"
        )

    report: dict[str, object] = {
        "backend": os.environ.get("AOT_ARCH", "default"),
        "aot_mode": os.environ.get("AOT_MODE", "1"),
        "host_fallback": os.environ.get("AOT_ALLOW_HOST_FALLBACK", "0"),
        "require_tcm": bool(require_tcm),
        "external_decoder": decoder,
        "runtime_import_audit": _runtime_import_audit(),
        "cases": [],
        "filter_cases": [],
        "metadata": {},
    }
    if not report["runtime_import_audit"]["codec_runtime_clean"]:
        raise AssertionError("PNG runtime imports a forbidden codec backend")

    for name, image in _synthetic_cases():
        strategies = ("auto", "stored", "fixed", "dynamic")
        for strategy in strategies:
            encoded = encode_png_aot(image, deflate_strategy=strategy)
            parsed = parse_png_aot(encoded)
            decoded, used_decoder = _decode_external(encoded, image)
            exact = bool(
                decoded.shape == image.shape and np.array_equal(decoded, image)
            )
            if not exact:
                raise AssertionError(
                    f"PNG external exact parity failed for {name}/{strategy}"
                )
            report["cases"].append(
                {
                    "name": name,
                    "strategy": strategy,
                    "bytes": len(encoded),
                    "raw_bytes": int(image.nbytes),
                    "bytes_per_pixel": len(encoded)
                    / float(image.shape[0] * image.shape[1]),
                    "bit_depth": int(parsed["bit_depth"]),
                    "color_type": int(parsed["color_type"]),
                    "external_decoder": used_decoder,
                    "exact": exact,
                }
            )

    # Every forced filter must execute through the same TCM graph used by the
    # adaptive path.  Compare the graph output directly with the independent
    # host oracle, then verify the complete PNG through an external decoder.
    probe = _synthetic_cases()[1][1]
    _, raw, _, _, channels, bit_depth = _as_png_bytes(probe)
    bytes_per_pixel = channels * (bit_depth // 8)
    for filter_id, filter_name in enumerate(("none", "sub", "up", "average", "paeth")):
        filtered, filter_types = _filter_rows(raw, bytes_per_pixel, filter_name)
        expected_filtered, expected_types = _filter_rows_host(
            raw,
            bytes_per_pixel,
            filter_name,
        )
        graph_exact = bool(
            np.array_equal(filtered, expected_filtered)
            and np.array_equal(filter_types, expected_types)
            and np.all(filter_types == filter_id)
        )
        if not graph_exact:
            raise AssertionError(
                f"PNG forced filter TCM parity failed for {filter_name}"
            )
        encoded = encode_png_aot(
            probe,
            filter_strategy=filter_name,
            deflate_strategy="dynamic",
        )
        decoded, used_decoder = _decode_external(encoded, probe)
        if not np.array_equal(decoded, probe):
            raise AssertionError(f"PNG forced filter parity failed for {filter_name}")
        report["filter_cases"].append(
            {
                "filter": filter_name,
                "bytes": len(encoded),
                "external_decoder": used_decoder,
                "graph_exact": graph_exact,
                "exact": True,
                "tcm_graph": "compression_png_filter_rows",
            }
        )

    metadata_image = np.arange(13 * 17, dtype=np.uint8).reshape(13, 17)
    metadata = {
        "gamma": 0.45455,
        "srgb": 0,
        "dpi": (300, 300),
        "time": (2026, 8, 10, 12, 34, 56),
        "text": {"Author": "Pixel Refine"},
        "itxt": {"Description": "native taichi png"},
        "exif": b"Exif\x00\x00native-test",
        "trns": (7,),
    }
    encoded = encode_png_aot(metadata_image, metadata=metadata)
    parsed = parse_png_aot(encoded)
    decoded, used_decoder = _decode_external(encoded, metadata_image)
    if not np.array_equal(decoded, metadata_image):
        raise AssertionError("PNG metadata sample parity failed")
    expected_chunks = {
        b"gAMA",
        b"sRGB",
        b"pHYs",
        b"tIME",
        b"tEXt",
        b"iTXt",
        b"eXIf",
        b"tRNS",
    }
    if not expected_chunks.issubset(set(parsed["chunks"])):
        raise AssertionError("PNG metadata chunk coverage is incomplete")
    report["metadata"] = {
        "bytes": len(encoded),
        "chunks": [chunk.decode("latin-1") for chunk in parsed["chunks"]],
        "external_decoder": used_decoder,
        "exact": True,
    }

    # Exercise the 65535-byte stored-block boundary and the bounded internal
    # inflater.  This does not replace external PNG decode; it specifically
    # guards the native Deflate block splitter used for incompressible data.
    boundary_data = bytes((index * 37 + 11) & 0xFF for index in range(70000))
    boundary_stream = deflate_stored(boundary_data)
    if (
        inflate_deflate(boundary_stream, expected_size=len(boundary_data))
        != boundary_data
    ):
        raise AssertionError("native stored Deflate boundary round-trip failed")
    report["deflate_boundary"] = {
        "input_bytes": len(boundary_data),
        "stream_bytes": len(boundary_stream),
        "round_trip_exact": True,
    }

    report["forced_filters_tcm"] = bool(
        len(report["filter_cases"]) == 5
        and all(case["graph_exact"] for case in report["filter_cases"])
    )

    # Parser truncation guard on one representative stream.  Every strict
    # prefix must be rejected; this catches accidental acceptance of missing
    # CRC/IEND/Deflate payloads without expanding the broad codec fuzz suite.
    failures = []
    for prefix in range(len(encoded)):
        try:
            parse_png_aot(encoded[:prefix])
        except Exception:
            continue
        failures.append(prefix)
    if failures:
        raise AssertionError(f"PNG truncation prefixes accepted: {failures[:5]}")
    report["truncation"] = {
        "attempted": len(encoded),
        "rejected": len(encoded),
        "all_rejected": True,
    }
    report["all_exact"] = True
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-tcm", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_png_verification(require_tcm=args.require_tcm)
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
