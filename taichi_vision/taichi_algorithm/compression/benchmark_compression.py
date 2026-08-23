"""Measured image-compression benchmark for the native codec profiles.

The benchmark intentionally keeps Pillow at the validation boundary only.  It
does not participate in encoding.  Native peak device memory is reported by
the AOT engine separately; ``python_peak_bytes`` here is only the host
allocator sample from ``tracemalloc``.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path
import time
import tracemalloc

import numpy as np

from .jpeg_aot import jpeg_encode_aot
from .png_aot import encode_png_aot
from .webp_aot import encode_webp_lossless_aot
from .verify_compression import psnr, runtime_dependency_audit, ssim


def _synthetic_rgb(height: int, width: int) -> np.ndarray:
    yy, xx = np.indices((int(height), int(width)), dtype=np.uint32)
    red = (xx * 7 + yy * 3) & 255
    green = (xx * 5 + yy * 11 + ((xx ^ yy) & 31)) & 255
    blue = ((xx * 13) ^ (yy * 17) ^ (xx * yy)) & 255
    return np.stack((red, green, blue), axis=-1).astype(np.uint8)


def _load_external_image(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".dng":
        # Validation boundary only.  The native DNG/JPEG encoders never import
        # rawpy; this fixed render makes the 12 MP corpus benchmark reproducible
        # without changing the runtime codec dependency contract.
        import rawpy

        with rawpy.imread(str(path)) as raw:
            kwargs = {
                "output_bps": 8,
                "use_camera_wb": False,
                "use_auto_wb": False,
                "no_auto_bright": True,
                "median_filter_passes": 0,
            }
            demosaic = getattr(rawpy, "DemosaicAlgorithm", None)
            if demosaic is not None and hasattr(demosaic, "AHD"):
                kwargs["demosaic_algorithm"] = demosaic.AHD
            rendered = raw.postprocess(**kwargs)
        return np.ascontiguousarray(rendered, dtype=np.uint8)
    from PIL import Image

    with Image.open(path) as source:
        return np.asarray(source.convert("RGB"), dtype=np.uint8)


def _decode(encoded: bytes, *, mode: str) -> np.ndarray:
    from PIL import Image

    with Image.open(io.BytesIO(encoded)) as image:
        return np.asarray(image.convert(mode), dtype=np.uint8)


def _measure(encoder, repeats: int) -> tuple[bytes, float, float, float, float, int]:
    tracemalloc.start()
    start = time.perf_counter_ns()
    first = encoder()
    cold_ms = (time.perf_counter_ns() - start) / 1_000_000.0
    samples = []
    for _ in range(max(1, int(repeats))):
        start = time.perf_counter_ns()
        result = encoder()
        samples.append((time.perf_counter_ns() - start) / 1_000_000.0)
    _current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    if first != result:
        raise AssertionError("encoder output is not deterministic across repeats")
    return (
        bytes(first),
        float(cold_ms),
        float(np.mean(samples)),
        float(np.min(samples)),
        float(np.max(samples)),
        int(peak),
    )


def _jpeg_execution_modes() -> dict[str, str]:
    return {
        "color": os.environ.get("JPEG_COLOR_MODE", "fused").strip().lower(),
        "dct": os.environ.get("JPEG_DCT_MODE", "fused").strip().lower(),
        "token": os.environ.get("JPEG_TOKEN_MODE", "fused").strip().lower(),
        "pack": os.environ.get("JPEG_PACK_MODE", "bytes").strip().lower(),
        "native_scan_pack": os.environ.get("JPEG_NATIVE_SCAN_PACK", "auto").strip().lower(),
        "native_scan_auto_max_blocks": os.environ.get(
            "JPEG_NATIVE_SCAN_AUTO_MAX_BLOCKS", "32768"
        ).strip(),
        "native_scan_chunk_blocks": os.environ.get(
            "JPEG_SCATTER_CHUNK_BLOCKS", "2048"
        ).strip(),
    }


def run_jpeg_regression(*, quality: int = 80, seed: int = 20260810) -> dict:
    """Compare every optimized JPEG stage with the retained legacy path.

    The comparison is encoded-byte exact, which covers quantization, scan
    ordering, Huffman symbols, bit carry, and marker assembly in one gate.
    It intentionally uses small odd-sized images so padding and all three
    subsampling layouts are exercised without making the regression test a
    performance benchmark.
    """
    from .jpeg_aot import jpeg_encode_aot

    previous = {
        name: os.environ.get(name)
        for name in (
            "JPEG_COLOR_MODE",
            "JPEG_DCT_MODE",
            "JPEG_TOKEN_MODE",
            "JPEG_PACK_MODE",
        )
    }
    cases = []
    passed = True
    try:
        rng = np.random.default_rng(int(seed))
        for height, width in ((16, 16), (17, 19), (65, 71)):
            image = rng.integers(0, 256, size=(height, width, 3), dtype=np.uint8)
            for subsampling in ("444", "422", "420"):
                for huffman in ("standard", "optimized"):
                    os.environ.update(
                        {
                            "JPEG_COLOR_MODE": "legacy",
                            "JPEG_DCT_MODE": "legacy",
                            "JPEG_TOKEN_MODE": "legacy",
                            "JPEG_PACK_MODE": "bits",
                        }
                    )
                    reference = jpeg_encode_aot(
                        image, quality=quality, subsampling=subsampling, huffman=huffman
                    )
                    os.environ.update(
                        {
                            "JPEG_COLOR_MODE": "fused",
                            "JPEG_DCT_MODE": "fused",
                            "JPEG_TOKEN_MODE": "fused",
                            "JPEG_PACK_MODE": "bytes",
                        }
                    )
                    optimized = jpeg_encode_aot(
                        image, quality=quality, subsampling=subsampling, huffman=huffman
                    )
                    equal = reference == optimized
                    passed = passed and equal
                    cases.append(
                        {
                            "shape": [height, width, 3],
                            "subsampling": subsampling,
                            "huffman": huffman,
                            "bytes": len(optimized),
                            "byte_exact": bool(equal),
                        }
                    )
    finally:
        for name, value in previous.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value
    return {"passed": bool(passed), "case_count": len(cases), "cases": cases}


def _case(
    *,
    codec: str,
    profile: str,
    source: np.ndarray,
    encoded: bytes,
    cold_ms: float,
    warm_mean_ms: float,
    warm_min_ms: float,
    warm_max_ms: float,
    python_peak_bytes: int,
    decoded: np.ndarray | None,
    exact: bool | None,
) -> dict:
    payload = {
        "codec": codec,
        "profile": profile,
        "bytes": len(encoded),
        "bytes_per_pixel": len(encoded) / float(source.shape[0] * source.shape[1]),
        "cold_ms": cold_ms,
        "warm_mean_ms": warm_mean_ms,
        "warm_min_ms": warm_min_ms,
        "warm_max_ms": warm_max_ms,
        "python_peak_bytes": python_peak_bytes,
        "external_decode": decoded is not None,
    }
    if decoded is not None:
        payload["psnr_db"] = psnr(source, decoded)
        payload["ssim"] = ssim(source, decoded)
    if exact is not None:
        payload["exact_pixels"] = bool(exact)
    return payload


def run_benchmark(
    image: np.ndarray,
    *,
    quality: int = 80,
    repeats: int = 3,
    include_webp_best: bool = True,
    jpeg_subsamplings: tuple[str, ...] = ("444", "422", "420"),
    jpeg_huffmans: tuple[str, ...] = ("standard", "optimized"),
    include_other_codecs: bool = True,
) -> dict:
    image = np.ascontiguousarray(image, dtype=np.uint8)
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("benchmark input must be an HxWx3 RGB image")
    cases = []
    for subsampling in jpeg_subsamplings:
        for huffman in jpeg_huffmans:
            encoded, cold, mean, minimum, maximum, peak = _measure(
                lambda s=subsampling, h=huffman: jpeg_encode_aot(
                    image,
                    quality=int(quality),
                    subsampling=s,
                    huffman=h,
                ),
                repeats,
            )
            decoded = _decode(encoded, mode="RGB")
            cases.append(
                _case(
                    codec="jpeg",
                    profile=f"{subsampling}/{huffman}/q{int(quality)}",
                    source=image,
                    encoded=encoded,
                    cold_ms=cold,
                    warm_mean_ms=mean,
                    warm_min_ms=minimum,
                    warm_max_ms=maximum,
                    python_peak_bytes=peak,
                    decoded=decoded,
                    exact=None,
                )
            )

    if include_other_codecs:
        encoded, cold, mean, minimum, maximum, peak = _measure(
            lambda: encode_png_aot(image, compression="dynamic", effort="best"),
            repeats,
        )
        decoded = _decode(encoded, mode="RGB")
        cases.append(
            _case(
                codec="png",
                profile="dynamic/best",
                source=image,
                encoded=encoded,
                cold_ms=cold,
                warm_mean_ms=mean,
                warm_min_ms=minimum,
                warm_max_ms=maximum,
                python_peak_bytes=peak,
                decoded=decoded,
                exact=bool(np.array_equal(image, decoded)),
            )
        )

        efforts = (
            ("baseline", "fast", "best") if include_webp_best else ("baseline", "fast")
        )
        for effort in efforts:
            encoded, cold, mean, minimum, maximum, peak = _measure(
                lambda e=effort: encode_webp_lossless_aot(image, effort=e),
                repeats,
            )
            decoded = _decode(encoded, mode="RGBA")[..., :3]
            cases.append(
                _case(
                    codec="webp",
                    profile=f"VP8L/{effort}",
                    source=image,
                    encoded=encoded,
                    cold_ms=cold,
                    warm_mean_ms=mean,
                    warm_min_ms=minimum,
                    warm_max_ms=maximum,
                    python_peak_bytes=peak,
                    decoded=decoded,
                    exact=bool(np.array_equal(image, decoded)),
                )
            )

    # HEIF/AVIF are reported explicitly instead of being labelled as general
    # encoders while their current native payloads are still constrained.  The
    # externally validated HEVC profiles include lossless I_PCM and a
    # compressed all-128 DC-intra profile; the AV1 payload remains a 16x16
    # constant/palette profile.
    heif_report = {
        "status": "bounded_native_profiles",
        "native_pixel_encoder": True,
        "supported_profile": "HEVC Main 8-bit 4:2:0 I_PCM plus all-128 CABAC/DC-intra",
    }
    avif_report = {
        "status": "tiny_constant_profile_only",
        "native_pixel_encoder": True,
        "supported_profile": "AV1 8-bit 4:2:0 constant 16x16 only",
    }
    if image.shape == (16, 16, 3) and bool(np.all(image == 128)):
        from .av1_aot import (
            build_av1c,
            encode_av1_tiny_constant,
            make_av1_still_profile,
        )
        from .avif_aot import package_avif_aot, parse_avif_aot
        from .heif_aot import package_heic_neutral_aot, parse_heif_aot

        heic_encoded, heic_cold, heic_mean, heic_min, heic_max, heic_peak = _measure(
            lambda: package_heic_neutral_aot(),
            repeats,
        )
        heif_report.update(
            {
                "bytes": len(heic_encoded),
                "bytes_per_pixel": len(heic_encoded) / 256.0,
                "cold_ms": heic_cold,
                "warm_mean_ms": heic_mean,
                "warm_min_ms": heic_min,
                "warm_max_ms": heic_max,
                "python_peak_bytes": heic_peak,
                "container_parser": bool(parse_heif_aot(heic_encoded)),
                "exact_constant_profile": True,
            }
        )
        av1_profile = make_av1_still_profile(16, 16, bit_depth=8, chroma="420")
        av1_payload = encode_av1_tiny_constant()
        avif_encoded, avif_cold, avif_mean, avif_min, avif_max, avif_peak = _measure(
            lambda: package_avif_aot(av1_payload, 16, 16, 8, build_av1c(av1_profile)),
            repeats,
        )
        avif_report.update(
            {
                "bytes": len(avif_encoded),
                "bytes_per_pixel": len(avif_encoded) / 256.0,
                "cold_ms": avif_cold,
                "warm_mean_ms": avif_mean,
                "warm_min_ms": avif_min,
                "warm_max_ms": avif_max,
                "python_peak_bytes": avif_peak,
                "container_parser": bool(parse_avif_aot(avif_encoded)),
                "exact_constant_profile": True,
            }
        )

    return {
        "backend": os.environ.get("AOT_ARCH", "default"),
        "aot_mode": os.environ.get("AOT_MODE", "1"),
        "shape": list(image.shape),
        "quality": int(quality),
        "repeats": int(repeats),
        "runtime_dependency_audit": runtime_dependency_audit(),
        "jpeg_execution_modes": _jpeg_execution_modes(),
        "cases": cases,
        "heif_heic": heif_report,
        "avif": avif_report,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, help="PNG/JPEG/WebP or validation-only DNG corpus"
    )
    parser.add_argument("--height", type=int, default=128)
    parser.add_argument("--width", type=int, default=160)
    parser.add_argument("--quality", type=int, default=80)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--no-webp-best", action="store_true")
    parser.add_argument(
        "--jpeg-only", action="store_true", help="benchmark JPEG cases only"
    )
    parser.add_argument(
        "--jpeg-subsampling", choices=("444", "422", "420"), action="append"
    )
    parser.add_argument(
        "--jpeg-huffman", choices=("standard", "optimized"), action="append"
    )
    parser.add_argument("--jpeg-color-mode", choices=("fused", "legacy"))
    parser.add_argument("--jpeg-dct-mode", choices=("fused", "legacy"))
    parser.add_argument("--jpeg-token-mode", choices=("fused", "legacy"))
    parser.add_argument("--jpeg-pack-mode", choices=("bytes", "bits"))
    parser.add_argument(
        "--regression",
        action="store_true",
        help="run JPEG optimized-vs-legacy byte regression",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.input is not None:
        image = _load_external_image(args.input)
        source = str(args.input)
    else:
        if args.height < 8 or args.width < 8:
            parser.error("height/width must be >= 8")
        image = _synthetic_rgb(args.height, args.width)
        source = "synthetic"
    if args.quality < 1 or args.quality > 100 or args.repeats < 1:
        parser.error("quality must be 1..100 and repeats must be positive")
    for name, value in (
        ("JPEG_COLOR_MODE", args.jpeg_color_mode),
        ("JPEG_DCT_MODE", args.jpeg_dct_mode),
        ("JPEG_TOKEN_MODE", args.jpeg_token_mode),
        ("JPEG_PACK_MODE", args.jpeg_pack_mode),
    ):
        if value is not None:
            os.environ[name] = value
    if args.regression:
        print(json.dumps(run_jpeg_regression(quality=args.quality), indent=2))
        return
    report = run_benchmark(
        image,
        quality=args.quality,
        repeats=args.repeats,
        include_webp_best=not args.no_webp_best,
        jpeg_subsamplings=tuple(args.jpeg_subsampling or ("444", "422", "420")),
        jpeg_huffmans=tuple(args.jpeg_huffman or ("standard", "optimized")),
        include_other_codecs=not args.jpeg_only,
    )
    report["source"] = source
    rendered = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
