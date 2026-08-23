"""Repeatable native-compression verification and benchmark harness.

This module deliberately keeps Pillow/rawpy imports inside validation helpers.
They are external reference decoders for tests only; the compression runtime
does not depend on them.  The report distinguishes exact lossless checks from
lossy metric checks and records the selected AOT target from the environment.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np


def runtime_dependency_audit() -> dict:
    """Report forbidden codec imports separately from the host array ABI."""
    root = Path(__file__).resolve().parent
    codec_backends = {
        "cv2",
        "PIL",
        "imageio",
        "imagecodecs",
        "zlib",
        "libjpeg",
        "libheif",
        "libavif",
        "libwebp",
        "libpng",
        "x265",
        "aom",
        "avm",
        "rawpy",
        "tifffile",
    }
    forbidden = []
    numpy_imports = []
    validation_helpers = {
        source.name
        for source in root.glob("*.py")
        if source.name == "benchmark_compression.py"
        or source.name.startswith("verify_")
        or source.name.startswith("test_")
    }
    for source in sorted(root.glob("*.py")):
        if source.name in validation_helpers:
            continue
        try:
            tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        except (OSError, SyntaxError):
            continue
        modules = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                modules.append(node.module)
        for module in modules:
            root_name = module.split(".", 1)[0]
            if root_name in codec_backends:
                forbidden.append((source.name, module))
            if root_name == "numpy":
                numpy_imports.append((source.name, module))
    return {
        "codec_backend_imports": tuple(sorted(set(forbidden))),
        "numpy_host_abi_imports": tuple(sorted(set(numpy_imports))),
        "codec_runtime_clean": not forbidden,
        "strict_no_numpy": not numpy_imports,
    }


def _window_mean(value: np.ndarray, radius: int = 5) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    if value.ndim == 2:
        value = value[..., None]
    size = 2 * radius + 1
    padded = np.pad(value, ((radius, radius), (radius, radius), (0, 0)), mode="reflect")
    integral = (
        np.pad(padded, ((1, 0), (1, 0), (0, 0)), mode="constant").cumsum(0).cumsum(1)
    )
    return (
        integral[size:, size:]
        - integral[:-size, size:]
        - integral[size:, :-size]
        + integral[:-size, :-size]
    ) / float(size * size)


def psnr(reference: np.ndarray, decoded: np.ndarray, peak: float = 255.0) -> float:
    first = np.asarray(reference, dtype=np.float64)
    second = np.asarray(decoded, dtype=np.float64)
    if first.shape != second.shape:
        raise ValueError(f"metric shape mismatch: {first.shape} != {second.shape}")
    mse = float(np.mean((first - second) ** 2))
    return float("inf") if mse == 0.0 else float(10.0 * np.log10((peak * peak) / mse))


def ssim(reference: np.ndarray, decoded: np.ndarray, peak: float = 255.0) -> float:
    first = np.asarray(reference, dtype=np.float64)
    second = np.asarray(decoded, dtype=np.float64)
    if first.shape != second.shape:
        raise ValueError(f"metric shape mismatch: {first.shape} != {second.shape}")
    if first.ndim == 2:
        first, second = first[..., None], second[..., None]
    mu_first = _window_mean(first)
    mu_second = _window_mean(second)
    sigma_first = _window_mean(first * first) - mu_first * mu_first
    sigma_second = _window_mean(second * second) - mu_second * mu_second
    covariance = _window_mean(first * second) - mu_first * mu_second
    c1 = (0.01 * peak) ** 2
    c2 = (0.03 * peak) ** 2
    score = ((2.0 * mu_first * mu_second + c1) * (2.0 * covariance + c2)) / (
        (mu_first * mu_first + mu_second * mu_second + c1)
        * (sigma_first + sigma_second + c2)
    )
    return float(np.mean(score))


def _synthetic_rgb(height: int, width: int) -> np.ndarray:
    yy, xx = np.indices((height, width), dtype=np.uint32)
    red = (xx * 7 + yy * 3) & 255
    green = (xx * 5 + yy * 11 + ((xx ^ yy) & 31)) & 255
    blue = ((xx * 13) ^ (yy * 17) ^ (xx * yy)) & 255
    return np.stack((red, green, blue), axis=-1).astype(np.uint8)


def _timed(callable_, repeats: int):
    start = time.perf_counter()
    first = callable_()
    first_ms = (time.perf_counter() - start) * 1000.0
    samples = []
    for _ in range(max(1, int(repeats))):
        start = time.perf_counter()
        result = callable_()
        samples.append((time.perf_counter() - start) * 1000.0)
    return (
        first,
        first_ms,
        float(np.mean(samples)),
        float(np.min(samples)),
        float(np.max(samples)),
    )


def _decode_png_or_jpeg(encoded: bytes, mode: str) -> np.ndarray:
    # External validation boundary only.  The native modules do not import PIL.
    from PIL import Image

    with Image.open(io.BytesIO(encoded)) as image:
        return np.asarray(image.convert("RGB" if mode == "jpeg" else image.mode))


def _decode_webp_rgba(encoded: bytes) -> np.ndarray:
    # External validation boundary only.  The native WebP module does not
    # import Pillow or any other WebP implementation.
    from PIL import Image

    with Image.open(io.BytesIO(encoded)) as image:
        return np.asarray(image.convert("RGBA"))


def _decode_avif_with_ffmpeg(
    encoded: bytes, width: int, height: int
) -> dict[str, object]:
    """Validate the constrained AVIF payload through FFmpeg, if installed.

    FFmpeg is deliberately a test-only decoder.  A missing executable is
    reported as ``available=False`` rather than changing the native runtime
    behavior or turning a structural AVIF test into a false production claim.
    """

    executable = shutil.which("ffmpeg")
    if executable is None:
        return {"available": False, "decoded": False, "reason": "ffmpeg_not_found"}
    with tempfile.TemporaryDirectory(prefix="pixel_refine_avif_verify_") as directory:
        source = Path(directory) / "sample.avif"
        source.write_bytes(bytes(encoded))
        process = subprocess.run(
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
                "yuv420p",
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    expected_size = int(width) * int(height) * 3 // 2
    decoded = process.returncode == 0 and len(process.stdout) == expected_size
    # The current native profile is a constant neutral frame.  Keep this
    # exact check scoped to the profile rather than implying a general AV1
    # pixel parity result.
    exact_constant = decoded and process.stdout == bytes((128,)) * expected_size
    return {
        "available": True,
        "decoded": bool(decoded),
        "exact_constant": bool(exact_constant),
        "returncode": int(process.returncode),
        "stderr": (
            process.stderr.decode("utf-8", errors="replace")[-400:]
            if not decoded
            else ""
        ),
    }


def _decode_heic_with_ffmpeg(
    encoded: bytes,
    width: int,
    height: int,
    expected: bytes | None = None,
    *,
    pix_fmt: str = "yuv420p",
    bytes_per_sample: int = 1,
    chroma_format_idc: int = 1,
) -> dict[str, object]:
    """Validate the bounded HEVC-in-HEIF profile through FFmpeg only in tests."""

    executable = shutil.which("ffmpeg")
    if executable is None:
        return {"available": False, "decoded": False, "reason": "ffmpeg_not_found"}
    with tempfile.TemporaryDirectory(prefix="pixel_refine_heic_verify_") as directory:
        source = Path(directory) / "sample.heic"
        source.write_bytes(bytes(encoded))
        process = subprocess.run(
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
                str(pix_fmt),
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    if chroma_format_idc == 1:
        chroma_width = (int(width) + 1) // 2
        chroma_height = (int(height) + 1) // 2
    elif chroma_format_idc == 2:
        chroma_width = (int(width) + 1) // 2
        chroma_height = int(height)
    elif chroma_format_idc == 3:
        chroma_width = int(width)
        chroma_height = int(height)
    else:
        raise ValueError("chroma_format_idc must be 1, 2, or 3")
    expected_size = (int(width) * int(height) + 2 * chroma_width * chroma_height) * int(
        bytes_per_sample
    )
    decoded = process.returncode == 0 and len(process.stdout) == expected_size
    exact_constant = decoded and process.stdout == bytes((128,)) * expected_size
    exact_expected = (
        expected is not None and decoded and process.stdout == bytes(expected)
    )
    return {
        "available": True,
        "decoded": bool(decoded),
        "exact_constant": bool(exact_constant),
        "exact_expected": bool(exact_expected),
        "returncode": int(process.returncode),
        "stderr": (
            process.stderr.decode("utf-8", errors="replace")[-400:]
            if not decoded
            else ""
        ),
    }


def _jpeg_container_regression() -> dict[str, bool]:
    """Check the host-side marker invariants used by every JPEG scan."""

    from .jpeg_container import dqt
    from .jpeg_aot import _optimized_table
    from .kernels import JPEG_ZIGZAG

    table = tuple(range(1, 65))
    marker = dqt(table)
    expected = bytes(table[index] for index in JPEG_ZIGZAG)
    payload = marker[4:]
    dqt_zigzag = payload[:1] == b"\x00" and payload[1:] == expected
    large_histogram = np.asarray(
        [1 << min(index, 60) for index in range(256)], dtype=np.int64
    )
    optimized_codes, optimized_marker = _optimized_table(large_histogram, 1, 1)
    codes_valid = bool(
        len(optimized_codes) == 256
        and len(optimized_marker) == 277
        and all(code < (1 << length) for code, length in optimized_codes.values())
        and len(set(optimized_codes.values())) == len(optimized_codes)
    )
    return {
        "dqt_zigzag": bool(dqt_zigzag),
        "optimized_large_histogram": codes_valid,
    }


def _jpeg_restart_state(encoded: bytes) -> tuple[int | None, tuple[int, ...]]:
    """Read the native JPEG DRI value and restart markers from one scan."""

    dri_offset = encoded.find(b"\xff\xdd")
    interval = None
    if dri_offset >= 0 and dri_offset + 6 <= len(encoded):
        segment_length = int.from_bytes(encoded[dri_offset + 2 : dri_offset + 4], "big")
        if segment_length == 4:
            interval = int.from_bytes(encoded[dri_offset + 4 : dri_offset + 6], "big")
    sos_offset = encoded.find(b"\xff\xda")
    if sos_offset < 0 or sos_offset + 4 > len(encoded):
        return interval, ()
    sos_length = int.from_bytes(encoded[sos_offset + 2 : sos_offset + 4], "big")
    scan_start = sos_offset + 2 + sos_length
    eoi_offset = encoded.find(b"\xff\xd9", scan_start)
    if eoi_offset < 0:
        eoi_offset = len(encoded)
    restart_markers = []
    index = scan_start
    while index + 1 < eoi_offset:
        if encoded[index] != 0xFF:
            index += 1
            continue
        code = encoded[index + 1]
        if code == 0x00:
            index += 2
            continue
        if 0xD0 <= code <= 0xD7:
            restart_markers.append(code - 0xD0)
        index += 2
    return interval, tuple(restart_markers)


def run_bitstream_regression() -> dict:
    """Verify the shared HEVC-RBSP and AV1-OBU bit primitives."""

    from .bitstream import (
        RbspReader,
        RbspWriter,
        leb128_decode,
        leb128_encode,
        rbsp_escape,
        rbsp_unescape,
    )

    unsigned = (0, 1, 2, 3, 7, 31, 255, 1024)
    signed = (-10, -1, 0, 1, 10)
    writer = RbspWriter()
    for value in unsigned:
        writer.write_ue(value)
    for value in signed:
        writer.write_se(value)
    writer.trailing_bits()
    encoded = writer.finish()
    reader = RbspReader(encoded, bit_count=writer.bit_count)
    decoded_unsigned = tuple(reader.read_ue() for _ in unsigned)
    decoded_signed = tuple(reader.read_se() for _ in signed)
    reader.require_trailing_bits()
    if decoded_unsigned != unsigned or decoded_signed != signed:
        raise AssertionError("RBSP Exp-Golomb round-trip mismatch")

    rbsp_cases = (
        b"",
        b"\x00\x00\x01\x02\x00\x00\x03\x04\x00\x00\x00\x01",
        bytes(range(64)),
    )
    for raw in rbsp_cases:
        if rbsp_unescape(rbsp_escape(raw)) != raw:
            raise AssertionError("RBSP emulation-prevention round-trip mismatch")

    leb_cases = (0, 1, 127, 128, 16384, (1 << 55) - 1)
    for value in leb_cases:
        payload = leb128_encode(value)
        decoded, end = leb128_decode(payload)
        if decoded != value or end != len(payload):
            raise AssertionError("AV1 LEB128 round-trip mismatch")
    rejected = 0
    for malformed in (
        b"\x80",
        b"\x80\x80\x80\x80\x80\x80\x80\x80",
        b"\xff\xff\xff\xff\xff\xff\xff\xff\x00",
    ):
        try:
            leb128_decode(malformed)
        except ValueError:
            rejected += 1
    return {
        "rbsp_exact": True,
        "leb128_exact": True,
        "malformed_rejected": rejected == 3,
        "cases": len(unsigned) + len(signed) + len(rbsp_cases) + len(leb_cases),
    }


def _container_regression_inputs(
    width: int, height: int
) -> dict[str, tuple[bytes, bytes]]:
    """Build bounded native HEIF/AVIF payload/configuration pairs."""

    from .av1_aot import build_av1c, make_av1_still_profile
    from .av1_intra_aot import encode_av1_intra_constant
    from .hevc_aot import build_hvcc, build_hevc_parameter_sets
    from .hevc_vcl_aot import build_hevc_vcl_picture

    hevc_sets = build_hevc_parameter_sets(int(width), int(height), bit_depth=8)
    picture = build_hevc_vcl_picture()
    heic_payload = b"".join(len(nal).to_bytes(4, "big") + nal for nal in picture.nals)
    heic_config = build_hvcc(picture.nals[:3])
    av1_profile = make_av1_still_profile(16, 16, bit_depth=8, chroma="420")
    av1_payload = encode_av1_intra_constant(128, 128, 128)
    return {
        # Keep the parameter-set-only stream available to callers that need a
        # structural negative case, but make the default HEIC regression a
        # complete fixed-profile VCL item.
        "heic_structural": (hevc_sets.annex_b, hevc_sets.hvcc),
        "heic": (heic_payload, heic_config),
        "avif": (av1_payload, build_av1c(av1_profile)),
    }


def run_container_fuzz(height: int = 8, width: int = 10) -> dict:
    """Exercise deterministic truncation rejection for native container readers."""
    from .avif_aot import package_avif_aot, parse_avif_aot
    from .dng_aot import encode_dng_aot, read_dng_aot
    from .heif_aot import (
        package_heic_aot,
        package_heic_flat_aot,
        package_heic_ipcm10_aot,
        package_heic_ipcm_aot,
        package_heic_neutral_aot,
        parse_heif_aot,
    )
    from .hevc_ipcm10_aot import hevc_ipcm10_sample_count
    from .png_aot import encode_png_aot, parse_png_aot
    from .webp_aot import encode_webp_lossless_aot, parse_webp_aot

    image = _synthetic_rgb(int(height), int(width))
    raw = (
        np.arange(int(height) * int(width), dtype=np.uint16).reshape(
            int(height), int(width)
        )
        * 17
    ) & 1023
    ipcm_samples = bytes(
        (index * 37 + 11) & 255 for index in range(16 * 16 + 2 * 8 * 8)
    )
    ipcm10_values = (
        (index * 37 + 5) & 1023 for index in range(hevc_ipcm10_sample_count())
    )
    ipcm10_samples = b"".join(value.to_bytes(2, "little") for value in ipcm10_values)
    structural = _container_regression_inputs(int(width), int(height))
    cases = (
        (
            "dng",
            encode_dng_aot(raw, compression="none", bits_per_sample=10),
            read_dng_aot,
        ),
        (
            "dng_lossless_jpeg",
            encode_dng_aot(
                raw,
                compression="lossless_jpeg",
                bits_per_sample=10,
                metadata={
                    "rows_per_strip": max(1, int(height) // 2),
                    "jpeg_predictor": 1,
                },
            ),
            read_dng_aot,
        ),
        ("png", encode_png_aot(image), parse_png_aot),
        ("webp", encode_webp_lossless_aot(image), parse_webp_aot),
        (
            "heif",
            package_heic_aot(structural["heic"][0], 16, 16, 8, structural["heic"][1]),
            parse_heif_aot,
        ),
        ("heif_ipcm", package_heic_ipcm_aot(ipcm_samples), parse_heif_aot),
        ("heif_ipcm10", package_heic_ipcm10_aot(ipcm10_samples), parse_heif_aot),
        ("heif_neutral", package_heic_neutral_aot(), parse_heif_aot),
        (
            "heif_flat",
            package_heic_flat_aot(
                bytes([0]) * 256 + bytes([255]) * 64 + bytes([64]) * 64
            ),
            parse_heif_aot,
        ),
        (
            "avif",
            package_avif_aot(structural["avif"][0], 16, 16, 8, structural["avif"][1]),
            parse_avif_aot,
        ),
    )
    failures = []
    attempted = 0
    rejected = 0
    for codec, payload, parser in cases:
        parser(payload)
        for prefix_length in range(len(payload)):
            attempted += 1
            try:
                parser(payload[:prefix_length])
            except Exception as exc:
                rejected += 1
                continue
            failures.append(
                {
                    "codec": codec,
                    "prefix_length": prefix_length,
                    "input_bytes": len(payload),
                }
            )
    return {
        "cases": len(cases),
        "attempted_truncations": attempted,
        "rejected_truncations": rejected,
        "failures": failures,
        "all_rejected": not failures and attempted == rejected,
    }


def run_verification(
    height: int = 128,
    width: int = 160,
    repeats: int = 2,
    quality: int = 80,
    fuzz: bool = False,
) -> dict:
    from .dng_aot import encode_dng_aot, read_dng_aot
    from .avif_aot import package_avif_aot, parse_avif_aot
    from .heif_aot import (
        package_heic_aot,
        package_heic_flat_aot,
        package_heic_ipcm10_aot,
        package_heic_ipcm_aot,
        package_heic_neutral_aot,
        package_heic_vcl_aot,
        parse_heif_aot,
    )
    from .hevc_ipcm10_aot import hevc_ipcm10_sample_count
    from .jpeg_aot import jpeg_encode_aot
    from .png_aot import encode_png_aot, parse_png_aot
    from .video_prep import prepare_yuv_aot
    from .webp_aot import encode_webp_lossless_aot, parse_webp_aot

    image = _synthetic_rgb(int(height), int(width))
    pixels = int(height) * int(width)
    report = {
        "backend": os.environ.get("AOT_ARCH", "default"),
        "aot_mode": os.environ.get("AOT_MODE", "1"),
        "shape": [int(height), int(width), 3],
        "runtime_dependency_audit": runtime_dependency_audit(),
        "bitstream_regression": run_bitstream_regression(),
        "jpeg_container_regression": _jpeg_container_regression(),
        "cases": [],
        "errors": [],
        "jpeg_quality_regression": {},
    }
    if not all(report["jpeg_container_regression"].values()):
        raise AssertionError("JPEG container/Huffman regression failed")
    for subsampling, expected_chroma_shape in (
        ("444", (int(height), int(width))),
        ("422", (int(height), (int(width) + 1) // 2)),
        ("420", ((int(height) + 1) // 2, (int(width) + 1) // 2)),
    ):
        prepared = prepare_yuv_aot(image, bit_depth=8, subsampling=subsampling)
        if prepared["y"].shape != (int(height), int(width)):
            raise AssertionError(f"YUV {subsampling} luma shape mismatch")
        if (
            prepared["cb"].shape != expected_chroma_shape
            or prepared["cr"].shape != expected_chroma_shape
        ):
            raise AssertionError(f"YUV {subsampling} chroma shape mismatch")
        report["cases"].append(
            {
                "codec": "video_prep",
                "subsampling": subsampling,
                "profile": "native Y/Cb/Cr preparation for HEIF/AVIF",
                "numeric_samples": int(
                    prepared["y"].size + prepared["cb"].size + prepared["cr"].size
                ),
                "used_host_fallback": bool(prepared["used_host_fallback"]),
                "exact_shapes": True,
            }
        )
    jpeg_decoded_by_subsampling = {}
    for subsampling in ("444", "422", "420"):
        for huffman in ("standard", "optimized"):
            encoded, cold_ms, warm_ms, min_ms, max_ms = _timed(
                lambda: jpeg_encode_aot(
                    image, quality=quality, subsampling=subsampling, huffman=huffman
                ),
                repeats,
            )
            decoded = _decode_png_or_jpeg(encoded, "jpeg")
            parity = True
            if huffman == "standard":
                jpeg_decoded_by_subsampling[subsampling] = decoded
            else:
                parity = bool(
                    np.array_equal(jpeg_decoded_by_subsampling[subsampling], decoded)
                )
                if not parity:
                    raise AssertionError(
                        f"JPEG optimized Huffman pixel parity failed for {subsampling}"
                    )
            report["cases"].append(
                {
                    "codec": "jpeg",
                    "subsampling": subsampling,
                    "huffman": huffman,
                    "bytes": len(encoded),
                    "bytes_per_pixel": len(encoded) / pixels,
                    "cold_ms": cold_ms,
                    "warm_mean_ms": warm_ms,
                    "warm_min_ms": min_ms,
                    "warm_max_ms": max_ms,
                    "psnr_db": psnr(image, decoded),
                    "ssim": ssim(image, decoded),
                    "huffman_pixel_parity": parity,
                    "external_decode": True,
                }
            )
        restart_interval = 2
        (
            restart_encoded,
            restart_cold_ms,
            restart_warm_ms,
            restart_min_ms,
            restart_max_ms,
        ) = _timed(
            lambda: jpeg_encode_aot(
                image,
                quality=quality,
                subsampling=subsampling,
                huffman="optimized",
                restart_interval=restart_interval,
            ),
            1,
        )
        restart_decoded = _decode_png_or_jpeg(restart_encoded, "jpeg")
        dri_value, restart_markers = _jpeg_restart_state(restart_encoded)
        if subsampling == "444":
            total_mcus = ((int(height) + 7) // 8) * ((int(width) + 7) // 8)
        elif subsampling == "422":
            total_mcus = ((int(height) + 7) // 8) * ((int(width) + 15) // 16)
        else:
            total_mcus = ((int(height) + 15) // 16) * ((int(width) + 15) // 16)
        expected_restart_markers = max(0, (total_mcus - 1) // restart_interval)
        restart_parity = bool(
            np.array_equal(jpeg_decoded_by_subsampling[subsampling], restart_decoded)
        )
        restart_sequence = tuple(restart_markers) == tuple(
            index % 8 for index in range(expected_restart_markers)
        )
        restart_valid = (
            dri_value == restart_interval
            and len(restart_markers) == expected_restart_markers
            and restart_sequence
            and restart_parity
        )
        if not restart_valid:
            raise AssertionError(
                f"JPEG restart parity/marker validation failed for {subsampling}"
            )
        report["cases"].append(
            {
                "codec": "jpeg",
                "subsampling": subsampling,
                "huffman": "optimized",
                "profile": "DRI/RST MCU restart resilience",
                "restart_interval": restart_interval,
                "restart_markers": list(restart_markers),
                "expected_restart_markers": expected_restart_markers,
                "dri_valid": dri_value == restart_interval,
                "restart_sequence_valid": restart_sequence,
                "pixel_parity": restart_parity,
                "bytes": len(restart_encoded),
                "bytes_per_pixel": len(restart_encoded) / pixels,
                "cold_ms": restart_cold_ms,
                "warm_mean_ms": restart_warm_ms,
                "warm_min_ms": restart_min_ms,
                "warm_max_ms": restart_max_ms,
                "psnr_db": psnr(image, restart_decoded),
                "ssim": ssim(image, restart_decoded),
                "external_decode": True,
            }
        )
    for quality_subsampling in ("444", "422", "420"):
        quality_decoded = {}
        for quality_probe in (50, 90):
            quality_encoded = jpeg_encode_aot(
                image,
                quality=quality_probe,
                subsampling=quality_subsampling,
                huffman="optimized",
            )
            quality_decoded[quality_probe] = _decode_png_or_jpeg(
                quality_encoded, "jpeg"
            )
        reference_float = image.astype(np.float64)
        mse_q50 = float(
            np.mean((reference_float - quality_decoded[50].astype(np.float64)) ** 2)
        )
        mse_q90 = float(
            np.mean((reference_float - quality_decoded[90].astype(np.float64)) ** 2)
        )
        monotonic = mse_q90 <= mse_q50 + 1e-12
        report["jpeg_quality_regression"][quality_subsampling] = {
            "q50_mse": mse_q50,
            "q90_mse": mse_q90,
            "higher_quality_not_worse": monotonic,
        }
        if not monotonic:
            raise AssertionError(
                f"JPEG quality monotonicity failed for {quality_subsampling}"
            )
    metadata_jpeg = jpeg_encode_aot(
        image,
        quality=quality,
        preset="high",
        metadata={
            "exif": b"II*\x00",
            "xmp": b"<xmpmeta/> Pixel Refine",
            "icc": b"Pixel Refine ICC profile",
            "comment": "native JPEG metadata",
        },
    )
    metadata_jpeg_decoded = _decode_png_or_jpeg(metadata_jpeg, "jpeg")
    metadata_markers = all(
        marker in metadata_jpeg
        for marker in (
            b"Exif\x00\x00",
            b"http://ns.adobe.com/xap/1.0/\x00",
            b"ICC_PROFILE\x00",
            b"native JPEG metadata",
        )
    )
    if not metadata_markers:
        raise AssertionError("JPEG metadata marker regression failed")
    report["cases"].append(
        {
            "codec": "jpeg",
            "profile": "high preset with EXIF/XMP/ICC/COM",
            "bytes": len(metadata_jpeg),
            "bytes_per_pixel": len(metadata_jpeg) / pixels,
            "preset": "high",
            "psnr_db": psnr(image, metadata_jpeg_decoded),
            "ssim": ssim(image, metadata_jpeg_decoded),
            "metadata_markers": metadata_markers,
            "external_decode": True,
        }
    )
    jpeg_error_inputs = (
        ("quality_zero", lambda: jpeg_encode_aot(image, quality=0)),
        ("invalid_subsampling", lambda: jpeg_encode_aot(image, subsampling="411")),
        (
            "negative_restart_interval",
            lambda: jpeg_encode_aot(image, restart_interval=-1),
        ),
        (
            "unknown_metadata",
            lambda: jpeg_encode_aot(image[:8, :8], metadata={"unknown": b"x"}),
        ),
        (
            "invalid_channel_count",
            lambda: jpeg_encode_aot(np.zeros((8, 8, 4), dtype=np.uint8)),
        ),
    )
    for label, invalid_call in jpeg_error_inputs:
        try:
            invalid_call()
        except Exception as exc:
            report["errors"].append(
                {
                    "codec": "jpeg",
                    "case": label,
                    "rejected": True,
                    "error": type(exc).__name__,
                }
            )
        else:
            report["errors"].append({"codec": "jpeg", "case": label, "rejected": False})
    if not all(
        item["rejected"] for item in report["errors"] if item.get("codec") == "jpeg"
    ):
        raise AssertionError("JPEG invalid-input regression failed")
    encoded, cold_ms, warm_ms, min_ms, max_ms = _timed(
        lambda: encode_png_aot(image, compression="dynamic", effort="best"),
        repeats,
    )
    decoded = _decode_png_or_jpeg(encoded, "png")
    report["cases"].append(
        {
            "codec": "png",
            "compression": "dynamic",
            "bytes": len(encoded),
            "bytes_per_pixel": len(encoded) / pixels,
            "cold_ms": cold_ms,
            "warm_mean_ms": warm_ms,
            "warm_min_ms": min_ms,
            "warm_max_ms": max_ms,
            "exact_pixels": bool(np.array_equal(image, decoded)),
            "container_parser": bool(parse_png_aot(encoded)),
            "external_decode": True,
        }
    )
    palette = np.asarray(
        ((255, 0, 0), (0, 255, 0), (0, 0, 255), (32, 64, 96)), dtype=np.uint8
    )
    palette_indices = ((image[..., 0] // 64) & 3).astype(np.uint8)
    palette_alpha = bytes((255, 192, 128, 64))
    palette_encoded = encode_png_aot(
        palette_indices,
        metadata={
            "palette": palette,
            "trns": palette_alpha,
            "itxt": {"Description": ("en-US", "Description", "Pixel Refine")},
        },
        compression="dynamic",
        effort="balanced",
    )
    from PIL import Image

    with Image.open(io.BytesIO(palette_encoded)) as palette_image:
        palette_decoded = np.asarray(palette_image.convert("RGBA"))
    palette_reference = np.concatenate(
        (
            palette[palette_indices],
            np.frombuffer(palette_alpha, dtype=np.uint8)[palette_indices][..., None],
        ),
        axis=-1,
    )
    report["cases"].append(
        {
            "codec": "png",
            "compression": "dynamic",
            "profile": "indexed palette/tRNS/iTXt",
            "bytes": len(palette_encoded),
            "bytes_per_pixel": len(palette_encoded) / pixels,
            "exact_pixels": bool(np.array_equal(palette_decoded, palette_reference)),
            "container_parser": bool(parse_png_aot(palette_encoded)),
            "metadata": True,
            "external_decode": True,
        }
    )

    yy, _ = np.indices((int(height), int(width)), dtype=np.uint16)
    alpha = ((yy * 19) & 255).astype(np.uint8)
    opaque = np.full((*image.shape[:2], 1), 255, dtype=np.uint8)
    webp_inputs = (
        (
            "gray",
            image[..., 0],
            np.concatenate(
                (image[..., 0:1], image[..., 0:1], image[..., 0:1], opaque), axis=-1
            ),
        ),
        ("rgb", image, np.concatenate((image, opaque), axis=-1)),
        (
            "rgba",
            np.concatenate((image, alpha[..., None]), axis=-1),
            np.concatenate((image, alpha[..., None]), axis=-1),
        ),
    )
    for channels, source, reference in webp_inputs:
        for effort in ("baseline", "fast", "best"):
            encoded, cold_ms, warm_ms, min_ms, max_ms = _timed(
                lambda source=source, effort=effort: encode_webp_lossless_aot(
                    source, effort=effort
                ),
                repeats,
            )
            decoded = _decode_webp_rgba(encoded)
            report["cases"].append(
                {
                    "codec": "webp",
                    "profile": "VP8L literal/LZ77 lossless",
                    "effort": effort,
                    "channels": channels,
                    "bytes": len(encoded),
                    "bytes_per_pixel": len(encoded) / pixels,
                    "cold_ms": cold_ms,
                    "warm_mean_ms": warm_ms,
                    "warm_min_ms": min_ms,
                    "warm_max_ms": max_ms,
                    "exact_pixels": bool(np.array_equal(reference, decoded)),
                    "container_parser": bool(parse_webp_aot(encoded)),
                    "external_decode": True,
                }
            )
    metadata_webp = encode_webp_lossless_aot(
        image,
        effort="baseline",
        metadata={"icc": b"ICC-profile", "exif": b"Exif\x00\x00", "xmp": b"<xmpmeta/>"},
    )
    metadata_decoded = _decode_webp_rgba(metadata_webp)
    report["cases"].append(
        {
            "codec": "webp",
            "profile": "VP8L metadata with VP8X",
            "bytes": len(metadata_webp),
            "bytes_per_pixel": len(metadata_webp) / pixels,
            "exact_pixels": bool(
                np.array_equal(
                    metadata_decoded, np.concatenate((image, opaque), axis=-1)
                )
            ),
            "container_parser": bool(parse_webp_aot(metadata_webp)),
            "metadata": True,
            "external_decode": True,
        }
    )

    # HEIC/AVIF cases are deliberately bounded native pixel profiles.  They do
    # not imply a general HEVC/AV1 encoder until the profile restrictions are
    # removed and arbitrary-image parity is proven.
    structural = _container_regression_inputs(int(width), int(height))
    for codec, package, parser, (payload, config) in (
        ("heic", package_heic_vcl_aot, parse_heif_aot, structural["heic"]),
        ("avif", package_avif_aot, parse_avif_aot, structural["avif"]),
    ):
        container_width, container_height = (16, 16)
        encoded = (
            package()
            if codec == "heic"
            else package(payload, container_width, container_height, 8, config)
        )
        external = (
            _decode_heic_with_ffmpeg(encoded, container_width, container_height)
            if codec == "heic"
            else _decode_avif_with_ffmpeg(encoded, container_width, container_height)
        )
        report["cases"].append(
            {
                "codec": codec,
                "profile": (
                    "native AV1 16x16 palette constant-pixel smoke"
                    if codec == "avif"
                    else "native HEVC 16x16 neutral IDR VCL smoke"
                ),
                "bytes": len(encoded),
                "bytes_per_pixel": len(encoded)
                / float(container_width * container_height),
                "container_parser": bool(parser(encoded)),
                "encoded_pixel_payload": codec in {"heic", "avif"},
                "external_decode": bool(external.get("decoded", False)),
                "external_decoder": external,
            }
        )

    ipcm_samples = bytes(
        (index * 37 + 11) & 255 for index in range(16 * 16 + 2 * 8 * 8)
    )
    ipcm_encoded = package_heic_ipcm_aot(ipcm_samples)
    ipcm_external = _decode_heic_with_ffmpeg(
        ipcm_encoded, 16, 16, expected=ipcm_samples
    )
    if ipcm_external.get("available") and not ipcm_external.get("exact_expected"):
        raise AssertionError(
            "external HEIC I_PCM decode is not exact for arbitrary planar samples"
        )
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC 16x16 8-bit 4:2:0 lossless I_PCM",
            "bytes": len(ipcm_encoded),
            "bytes_per_pixel": len(ipcm_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(ipcm_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(ipcm_external.get("decoded", False)),
            "external_exact_samples": bool(ipcm_external.get("exact_expected", False)),
            "external_decoder": ipcm_external,
        }
    )
    report["heic_ipcm_external_validation"] = {
        "available": bool(ipcm_external.get("available", False)),
        "decoded": bool(ipcm_external.get("decoded", False)),
        "exact_arbitrary_planar_samples": bool(
            ipcm_external.get("exact_expected", False)
        ),
    }
    multi_width, multi_height = 32, 16
    multi_samples = bytes(
        (index * 53 + 19) & 255
        for index in range(
            multi_width * multi_height + 2 * (multi_width // 2) * (multi_height // 2)
        )
    )
    multi_encoded = package_heic_ipcm_aot(multi_samples, multi_width, multi_height)
    multi_external = _decode_heic_with_ffmpeg(
        multi_encoded,
        multi_width,
        multi_height,
        expected=multi_samples,
    )
    if multi_external.get("available") and not multi_external.get("exact_expected"):
        raise AssertionError("external HEIC multi-CTU I_PCM decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC multi-CTU 8-bit 4:2:0 lossless I_PCM",
            "width": multi_width,
            "height": multi_height,
            "bytes": len(multi_encoded),
            "bytes_per_pixel": len(multi_encoded) / float(multi_width * multi_height),
            "container_parser": bool(parse_heif_aot(multi_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(multi_external.get("decoded", False)),
            "external_exact_samples": bool(multi_external.get("exact_expected", False)),
            "external_decoder": multi_external,
        }
    )
    report["heic_ipcm_external_validation"]["multi_ctu_exact"] = bool(
        multi_external.get("exact_expected", False)
    )

    # The I_PCM encoder also pads the final 16x16 CTU and uses the SPS
    # conformance window for even, non-16-aligned visible dimensions.
    edge_width, edge_height = 18, 22
    edge_chroma_width, edge_chroma_height = edge_width // 2, edge_height // 2
    edge_samples = bytes(
        (x * 7 + y * 11) & 255
        for y in range(edge_height)
        for x in range(edge_width)
    ) + bytes(
        (x * 13 + y * 5 + 17) & 255
        for y in range(edge_chroma_height)
        for x in range(edge_chroma_width)
    ) + bytes(
        (x * 3 + y * 19 + 91) & 255
        for y in range(edge_chroma_height)
        for x in range(edge_chroma_width)
    )
    edge_encoded = package_heic_ipcm_aot(edge_samples, edge_width, edge_height)
    edge_external = _decode_heic_with_ffmpeg(
        edge_encoded, edge_width, edge_height, expected=edge_samples
    )
    if edge_external.get("available") and not edge_external.get("exact_expected"):
        raise AssertionError("external HEIC non-aligned I_PCM decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC even non-16-aligned 8-bit 4:2:0 lossless I_PCM",
            "width": edge_width,
            "height": edge_height,
            "bytes": len(edge_encoded),
            "bytes_per_pixel": len(edge_encoded) / float(edge_width * edge_height),
            "container_parser": bool(parse_heif_aot(edge_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(edge_external.get("decoded", False)),
            "external_exact_samples": bool(edge_external.get("exact_expected", False)),
            "external_decoder": edge_external,
        }
    )
    report["heic_ipcm_external_validation"]["non_aligned_exact"] = bool(
        edge_external.get("exact_expected", False)
    )

    ipcm10_values = tuple(
        (index * 37 + 5) & 1023 for index in range(hevc_ipcm10_sample_count())
    )
    ipcm10_samples = b"".join(value.to_bytes(2, "little") for value in ipcm10_values)
    ipcm10_encoded = package_heic_ipcm10_aot(ipcm10_samples)
    ipcm10_external = _decode_heic_with_ffmpeg(
        ipcm10_encoded,
        16,
        16,
        expected=ipcm10_samples,
        pix_fmt="yuv420p10le",
        bytes_per_sample=2,
    )
    if ipcm10_external.get("available") and not ipcm10_external.get("exact_expected"):
        raise AssertionError("external HEIC Main10 I_PCM decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC Main10 16x16 4:2:0 lossless I_PCM",
            "width": 16,
            "height": 16,
            "bit_depth": 10,
            "bytes": len(ipcm10_encoded),
            "bytes_per_pixel": len(ipcm10_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(ipcm10_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(ipcm10_external.get("decoded", False)),
            "external_exact_samples": bool(
                ipcm10_external.get("exact_expected", False)
            ),
            "external_decoder": ipcm10_external,
        }
    )
    report["heic_ipcm10_external_validation"] = {
        "available": bool(ipcm10_external.get("available", False)),
        "decoded": bool(ipcm10_external.get("decoded", False)),
        "exact_arbitrary_planar_samples": bool(
            ipcm10_external.get("exact_expected", False)
        ),
    }

    multi10_width, multi10_height = 32, 16
    multi10_values = tuple(
        (index * 73 + 11) & 1023
        for index in range(hevc_ipcm10_sample_count(multi10_width, multi10_height))
    )
    multi10_samples = b"".join(value.to_bytes(2, "little") for value in multi10_values)
    multi10_encoded = package_heic_ipcm10_aot(
        multi10_samples,
        multi10_width,
        multi10_height,
    )
    multi10_external = _decode_heic_with_ffmpeg(
        multi10_encoded,
        multi10_width,
        multi10_height,
        expected=multi10_samples,
        pix_fmt="yuv420p10le",
        bytes_per_sample=2,
    )
    if multi10_external.get("available") and not multi10_external.get("exact_expected"):
        raise AssertionError("external HEIC Main10 multi-CTU I_PCM decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC Main10 multi-CTU 4:2:0 lossless I_PCM",
            "width": multi10_width,
            "height": multi10_height,
            "bit_depth": 10,
            "bytes": len(multi10_encoded),
            "bytes_per_pixel": len(multi10_encoded)
            / float(multi10_width * multi10_height),
            "container_parser": bool(parse_heif_aot(multi10_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(multi10_external.get("decoded", False)),
            "external_exact_samples": bool(
                multi10_external.get("exact_expected", False)
            ),
            "external_decoder": multi10_external,
        }
    )
    report["heic_ipcm10_external_validation"]["multi_ctu_exact"] = bool(
        multi10_external.get("exact_expected", False)
    )

    edge10_values = tuple(
        ((x * 17 + y * 23 + 3) & 1023)
        for y in range(edge_height)
        for x in range(edge_width)
    ) + tuple(
        ((x * 29 + y * 7 + 31) & 1023)
        for y in range(edge_chroma_height)
        for x in range(edge_chroma_width)
    ) + tuple(
        ((x * 5 + y * 41 + 99) & 1023)
        for y in range(edge_chroma_height)
        for x in range(edge_chroma_width)
    )
    edge10_samples = b"".join(value.to_bytes(2, "little") for value in edge10_values)
    edge10_encoded = package_heic_ipcm10_aot(edge10_samples, edge_width, edge_height)
    edge10_external = _decode_heic_with_ffmpeg(
        edge10_encoded,
        edge_width,
        edge_height,
        expected=edge10_samples,
        pix_fmt="yuv420p10le",
        bytes_per_sample=2,
    )
    if edge10_external.get("available") and not edge10_external.get("exact_expected"):
        raise AssertionError("external HEIC non-aligned Main10 I_PCM decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC even non-16-aligned Main10 4:2:0 lossless I_PCM",
            "width": edge_width,
            "height": edge_height,
            "bit_depth": 10,
            "bytes": len(edge10_encoded),
            "bytes_per_pixel": len(edge10_encoded) / float(edge_width * edge_height),
            "container_parser": bool(parse_heif_aot(edge10_encoded)),
            "encoded_pixel_payload": True,
            "lossless_ipcm": True,
            "external_decode": bool(edge10_external.get("decoded", False)),
            "external_exact_samples": bool(edge10_external.get("exact_expected", False)),
            "external_decoder": edge10_external,
        }
    )
    report["heic_ipcm10_external_validation"]["non_aligned_exact"] = bool(
        edge10_external.get("exact_expected", False)
    )

    # Exercise the variable-subsampling I_PCM path independently of the
    # 4:2:0/Main10 cases above.  These are lossless interoperability gates;
    # the compressed residual path remains a separate HEVC milestone.
    for chroma_format_idc, chroma_name, chroma_width, chroma_height, width, height, pix_fmt in (
        (2, "4:2:2", 9, 21, 18, 21, "yuv422p"),
        (3, "4:4:4", 17, 19, 17, 19, "yuv444p"),
    ):
        chroma_samples = bytes(
            (x * 13 + y * 5 + 17 + chroma_format_idc) & 255
            for y in range(chroma_height)
            for x in range(chroma_width)
        )
        variable_samples = bytes(
            (x * 7 + y * 11 + chroma_format_idc) & 255
            for y in range(height)
            for x in range(width)
        ) + chroma_samples + bytes(
            (x * 3 + y * 19 + 91 + chroma_format_idc) & 255
            for y in range(chroma_height)
            for x in range(chroma_width)
        )
        variable_encoded = package_heic_ipcm_aot(
            variable_samples,
            width,
            height,
            chroma_format_idc,
        )
        variable_external = _decode_heic_with_ffmpeg(
            variable_encoded,
            width,
            height,
            expected=variable_samples,
            pix_fmt=pix_fmt,
            chroma_format_idc=chroma_format_idc,
        )
        if variable_external.get("available") and not variable_external.get("exact_expected"):
            raise AssertionError(f"external HEIC {chroma_name} I_PCM decode is not exact")
        report["cases"].append(
            {
                "codec": "heic",
                "profile": f"native HEVC non-aligned 8-bit {chroma_name} lossless I_PCM",
                "width": width,
                "height": height,
                "bytes": len(variable_encoded),
                "bytes_per_pixel": len(variable_encoded) / float(width * height),
                "chroma_format_idc": chroma_format_idc,
                "container_parser": bool(parse_heif_aot(variable_encoded)),
                "encoded_pixel_payload": True,
                "lossless_ipcm": True,
                "external_decode": bool(variable_external.get("decoded", False)),
                "external_exact_samples": bool(variable_external.get("exact_expected", False)),
                "external_decoder": variable_external,
            }
        )
    report["heic_ipcm_external_validation"]["variable_subsampling_exact"] = True

    flat_y, flat_cb, flat_cr = 0, 255, 64
    flat_samples = (
        bytes((flat_y,)) * 256 + bytes((flat_cb,)) * 64 + bytes((flat_cr,)) * 64
    )
    flat_encoded = package_heic_flat_aot(flat_samples)
    flat_external = _decode_heic_with_ffmpeg(
        flat_encoded,
        16,
        16,
        expected=flat_samples,
    )
    if flat_external.get("available") and not flat_external.get("exact_expected"):
        raise AssertionError("external HEIC flat DC-intra decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC 16x16 8-bit 4:2:0 constant-plane DC intra",
            "width": 16,
            "height": 16,
            "bytes": len(flat_encoded),
            "bytes_per_pixel": len(flat_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(flat_encoded)),
            "encoded_pixel_payload": True,
            "lossless_for_profile": True,
            "constant_planes": {"y": flat_y, "cb": flat_cb, "cr": flat_cr},
            "external_decode": bool(flat_external.get("decoded", False)),
            "external_exact_samples": bool(flat_external.get("exact_expected", False)),
            "external_decoder": flat_external,
        }
    )
    report["heic_flat_external_validation"] = {
        "available": bool(flat_external.get("available", False)),
        "decoded": bool(flat_external.get("decoded", False)),
        "exact_constant_planes": bool(flat_external.get("exact_expected", False)),
    }
    flat_matrix = (
        (0, 0, 0),
        (255, 255, 255),
        (0, 255, 128),
        (255, 0, 64),
        (64, 192, 255),
        (127, 129, 1),
    )
    matrix_results = []
    for matrix_y, matrix_cb, matrix_cr in flat_matrix:
        matrix_samples = (
            bytes((matrix_y,)) * 256
            + bytes((matrix_cb,)) * 64
            + bytes((matrix_cr,)) * 64
        )
        matrix_encoded = package_heic_flat_aot(matrix_samples)
        matrix_external = _decode_heic_with_ffmpeg(
            matrix_encoded,
            16,
            16,
            expected=matrix_samples,
        )
        matrix_results.append(
            {
                "planes": {"y": matrix_y, "cb": matrix_cb, "cr": matrix_cr},
                "bytes": len(matrix_encoded),
                "decoded": bool(matrix_external.get("decoded", False)),
                "exact": bool(matrix_external.get("exact_expected", False)),
            }
        )
        if matrix_external.get("available") and not matrix_external.get(
            "exact_expected"
        ):
            raise AssertionError("HEIC flat DC-intra matrix is not exact")
    report["heic_flat_external_validation"]["matrix"] = matrix_results
    report["heic_flat_external_validation"]["matrix_exact"] = all(
        bool(item["exact"]) for item in matrix_results
    )
    multi_width, multi_height = 32, 32
    multi_chroma_samples = (multi_width // 2) * (multi_height // 2)
    multi_samples = (
        bytes((flat_y,)) * (multi_width * multi_height)
        + bytes((flat_cb,)) * multi_chroma_samples
        + bytes((flat_cr,)) * multi_chroma_samples
    )
    multi_encoded = package_heic_flat_aot(
        multi_samples,
        width=multi_width,
        height=multi_height,
    )
    multi_external = _decode_heic_with_ffmpeg(
        multi_encoded,
        multi_width,
        multi_height,
        expected=multi_samples,
    )
    if multi_external.get("available") and not multi_external.get("exact_expected"):
        raise AssertionError("external HEIC flat multi-CTU decode is not exact")
    report["heic_flat_external_validation"]["multi_ctu"] = {
        "width": multi_width,
        "height": multi_height,
        "bytes": len(multi_encoded),
        "decoded": bool(multi_external.get("decoded", False)),
        "exact": bool(multi_external.get("exact_expected", False)),
    }

    main10_flat_values = np.concatenate(
        (
            np.full(256, 512, dtype="<u2"),
            np.full(64, 700, dtype="<u2"),
            np.full(64, 100, dtype="<u2"),
        )
    )
    main10_flat_samples = main10_flat_values.tobytes()
    main10_flat_encoded = package_heic_flat_aot(
        main10_flat_samples,
        width=16,
        height=16,
        bit_depth=10,
    )
    main10_flat_external = _decode_heic_with_ffmpeg(
        main10_flat_encoded,
        16,
        16,
        expected=main10_flat_samples,
        pix_fmt="yuv420p10le",
        bytes_per_sample=2,
    )
    if main10_flat_external.get("available") and not main10_flat_external.get(
        "exact_expected"
    ):
        raise AssertionError("external HEIC compressed Main10 flat decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC Main10 16x16 4:2:0 constant-plane DC intra",
            "width": 16,
            "height": 16,
            "bit_depth": 10,
            "bytes": len(main10_flat_encoded),
            "bytes_per_pixel": len(main10_flat_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(main10_flat_encoded)),
            "encoded_pixel_payload": True,
            "lossless_for_profile": True,
            "external_decode": bool(main10_flat_external.get("decoded", False)),
            "external_exact_samples": bool(
                main10_flat_external.get("exact_expected", False)
            ),
            "external_decoder": main10_flat_external,
        }
    )
    report["heic_flat10_external_validation"] = {
        "available": bool(main10_flat_external.get("available", False)),
        "decoded": bool(main10_flat_external.get("decoded", False)),
        "exact_constant_planes": bool(main10_flat_external.get("exact_expected", False)),
    }

    flat_444_samples = (
        bytes((flat_y,)) * 256
        + bytes((flat_cb,)) * 256
        + bytes((flat_cr,)) * 256
    )
    flat_444_encoded = package_heic_flat_aot(
        flat_444_samples,
        width=16,
        height=16,
        chroma_format_idc=3,
    )
    flat_444_external = _decode_heic_with_ffmpeg(
        flat_444_encoded,
        16,
        16,
        expected=flat_444_samples,
        pix_fmt="yuv444p",
        chroma_format_idc=3,
    )
    if flat_444_external.get("available") and not flat_444_external.get(
        "exact_expected"
    ):
        raise AssertionError("external HEIC compressed 4:4:4 decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC 16x16 8-bit 4:4:4 constant-plane DC intra",
            "width": 16,
            "height": 16,
            "chroma_format_idc": 3,
            "bytes": len(flat_444_encoded),
            "bytes_per_pixel": len(flat_444_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(flat_444_encoded)),
            "encoded_pixel_payload": True,
            "lossless_for_profile": True,
            "external_decode": bool(flat_444_external.get("decoded", False)),
            "external_exact_samples": bool(
                flat_444_external.get("exact_expected", False)
            ),
            "external_decoder": flat_444_external,
        }
    )

    neutral_encoded = package_heic_neutral_aot()
    neutral_external = _decode_heic_with_ffmpeg(
        neutral_encoded,
        16,
        16,
    )
    if neutral_external.get("available") and not neutral_external.get("exact_constant"):
        raise AssertionError("external HEIC compressed neutral decode is not exact")
    report["cases"].append(
        {
            "codec": "heic",
            "profile": "native HEVC 8-bit 4:2:0 CABAC DC intra neutral profile",
            "width": 16,
            "height": 16,
            "bytes": len(neutral_encoded),
            "bytes_per_pixel": len(neutral_encoded) / float(16 * 16),
            "container_parser": bool(parse_heif_aot(neutral_encoded)),
            "encoded_pixel_payload": True,
            "lossless_for_profile": True,
            "smaller_than_ipcm": len(neutral_encoded) < len(ipcm_encoded),
            "external_decode": bool(neutral_external.get("decoded", False)),
            "external_exact_constant": bool(
                neutral_external.get("exact_constant", False)
            ),
            "external_decoder": neutral_external,
        }
    )
    report["heic_neutral_external_validation"] = {
        "available": bool(neutral_external.get("available", False)),
        "decoded": bool(neutral_external.get("decoded", False)),
        "exact_constant": bool(neutral_external.get("exact_constant", False)),
        "smaller_than_ipcm": len(neutral_encoded) < len(ipcm_encoded),
    }
    try:
        package_heic_neutral_aot(bytes((127,)) * (16 * 16 + 2 * 8 * 8))
    except Exception as exc:
        report["errors"].append(
            {
                "codec": "heic",
                "case": "neutral_profile_out_of_domain",
                "rejected": True,
                "error": type(exc).__name__,
            }
        )
    else:
        report["errors"].append(
            {
                "codec": "heic",
                "case": "neutral_profile_out_of_domain",
                "rejected": False,
            }
        )

    raw = (
        np.arange(int(height) * int(width), dtype=np.uint16).reshape(
            int(height), int(width)
        )
        * 17
    ) & 1023
    for compression in ("none", "packbits", "deflate", "deflate_dynamic"):
        encoded, cold_ms, warm_ms, min_ms, max_ms = _timed(
            lambda compression=compression: encode_dng_aot(
                raw,
                compression=compression,
                predictor="horizontal" if compression != "none" else "none",
                bits_per_sample=10,
                metadata={"rows_per_strip": max(1, int(height) // 4)},
            ),
            repeats,
        )
        decoded = read_dng_aot(encoded).samples()
        report["cases"].append(
            {
                "codec": "dng",
                "compression": compression,
                "bits_per_sample": 10,
                "bytes": len(encoded),
                "bytes_per_pixel": len(encoded) / pixels,
                "cold_ms": cold_ms,
                "warm_mean_ms": warm_ms,
                "warm_min_ms": min_ms,
                "warm_max_ms": max_ms,
                "exact_samples": bool(np.array_equal(raw, decoded)),
            }
        )
    encoded, cold_ms, warm_ms, min_ms, max_ms = _timed(
        lambda: encode_dng_aot(
            raw,
            compression="lossless_jpeg",
            predictor="none",
            bits_per_sample=10,
            metadata={
                "rows_per_strip": max(1, int(height) // 2),
                "jpeg_predictor": 4,
                "jpeg_huffman": "optimized",
            },
        ),
        repeats,
    )
    decoded = read_dng_aot(encoded).samples()
    report["cases"].append(
        {
            "codec": "dng",
            "compression": "lossless_jpeg",
            "bits_per_sample": 10,
            "jpeg_predictor": 4,
            "bytes": len(encoded),
            "bytes_per_pixel": len(encoded) / pixels,
            "cold_ms": cold_ms,
            "warm_mean_ms": warm_ms,
            "warm_min_ms": min_ms,
            "warm_max_ms": max_ms,
            "exact_samples": bool(np.array_equal(raw, decoded)),
        }
    )
    for malformed in (b"", b"II\x2a\x00\x08\x00\x00\x00"):
        try:
            read_dng_aot(malformed)
        except Exception as exc:
            report["errors"].append(
                {
                    "input_bytes": len(malformed),
                    "rejected": True,
                    "error": type(exc).__name__,
                }
            )
        else:
            report["errors"].append({"input_bytes": len(malformed), "rejected": False})
    valid_webp = encode_webp_lossless_aot(image, effort="baseline")
    valid_webp_chunks = parse_webp_aot(valid_webp)
    valid_vp8l = next(item for item in valid_webp_chunks if item[0] == b"VP8L")
    truncated_vp8l = valid_webp[: valid_vp8l[1] + 8 + 5]
    invalid_version = bytearray(valid_webp)
    invalid_version[valid_vp8l[1] + 8 + 4] |= 0x20
    for malformed in (
        b"",
        b"RIFF\x04\x00\x00\x00WEBP",
        truncated_vp8l,
        bytes(invalid_version),
    ):
        try:
            parse_webp_aot(malformed)
        except Exception as exc:
            report["errors"].append(
                {
                    "codec": "webp",
                    "input_bytes": len(malformed),
                    "rejected": True,
                    "error": type(exc).__name__,
                }
            )
        else:
            report["errors"].append(
                {"codec": "webp", "input_bytes": len(malformed), "rejected": False}
            )
    report["all_lossless_exact"] = all(
        case.get("exact_pixels", case.get("exact_samples", True))
        for case in report["cases"]
        if case["codec"] in {"png", "dng", "webp"}
    )
    report["all_malformed_rejected"] = all(
        item["rejected"] for item in report["errors"]
    )
    if fuzz:
        report["container_fuzz"] = run_container_fuzz(int(height), int(width))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--height", type=int, default=128)
    parser.add_argument("--width", type=int, default=160)
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--quality", type=int, default=80)
    parser.add_argument(
        "--fuzz",
        action="store_true",
        help="run deterministic truncation fuzz checks for native containers",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.height < 8 or args.width < 8 or args.repeats < 1:
        parser.error("height/width must be >= 8 and repeats must be positive")
    report = run_verification(
        args.height, args.width, args.repeats, args.quality, fuzz=args.fuzz
    )
    if not all(
        report["bitstream_regression"].get(key, False)
        for key in ("rbsp_exact", "leb128_exact", "malformed_rejected")
    ):
        raise SystemExit("shared codec bitstream regression failed")
    if args.fuzz and not report["container_fuzz"]["all_rejected"]:
        raise SystemExit("container truncation fuzz failed")
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
