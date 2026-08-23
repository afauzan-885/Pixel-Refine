"""Focused external qualification for native HEIC lossless profiles.

The HEVC I_PCM path is intentionally separate from the bounded compressed
DC-intra profile.  This harness proves arbitrary planar 8-bit samples, all
three supported chroma layouts, non-aligned dimensions, deterministic output,
and external FFmpeg parity.  The auto-profile gate also covers bounded
10-bit Main10 4:2:0 constant compression and arbitrary-sample I_PCM fallback.
FFmpeg is a validation-only decoder.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .heif_aot import package_heic_image_aot, package_heic_ipcm_aot, parse_heif_aot
from .hevc_general_aot import (
    hevc_general_sparse_ac_fixture_samples,
    hevc_general_sparse_ac_multi_fixture_samples,
)


def _sample_count(width: int, height: int, chroma_format_idc: int) -> int:
    if chroma_format_idc == 1:  # 4:2:0
        chroma_width = (width + 1) // 2
        chroma_height = (height + 1) // 2
    elif chroma_format_idc == 2:  # 4:2:2
        chroma_width = (width + 1) // 2
        chroma_height = height
    elif chroma_format_idc == 3:  # 4:4:4
        chroma_width = width
        chroma_height = height
    else:
        raise ValueError("unsupported chroma format")
    return width * height + 2 * chroma_width * chroma_height


def _samples(width: int, height: int, chroma_format_idc: int) -> bytes:
    count = _sample_count(width, height, chroma_format_idc)
    return bytes((index * 37 + width * 11 + height * 13 + chroma_format_idc) & 255 for index in range(count))


def _samples10(width: int, height: int) -> bytes:
    count = _sample_count(width, height, 1)
    return b"".join(
        int((index * 173 + width * 19 + height * 23 + 7) & 1023).to_bytes(2, "little")
        for index in range(count)
    )


def _constant10(width: int, height: int, value: int = 512) -> bytes:
    count = _sample_count(width, height, 1)
    return int(value).to_bytes(2, "little") * count


def _block_constant_samples10(width: int, height: int) -> bytes:
    """Build a multi-row Main10 fixture accepted by the DC predictor."""

    if width != 32 or height != 32:
        raise ValueError("the focused Main10 block-constant fixture is 32x32")

    def plane(
        plane_width: int,
        plane_height: int,
        block_width: int,
        block_height: int,
        values: tuple[int, int, int, int],
    ) -> bytes:
        output = bytearray()
        for block_y in range(plane_height // block_height):
            for row in range(block_height):
                for block_x in range(plane_width // block_width):
                    value = values[block_y * 2 + block_x]
                    output.extend(int(value).to_bytes(2, "little") * block_width)
        return bytes(output)

    return (
        plane(32, 32, 16, 16, (100, 200, 200, 300))
        + plane(16, 16, 8, 8, (400, 500, 500, 600))
        + plane(16, 16, 8, 8, (700, 800, 800, 900))
    )


def _block_constant_samples(width: int, height: int, chroma_format_idc: int) -> bytes:
    """Build a multi-row CTU fixture accepted by the bounded DC predictor."""

    if width != 32 or height != 32 or chroma_format_idc not in (1, 3):
        raise ValueError("the focused block-constant fixtures are 32x32 4:2:0/4:4:4")

    def plane(
        plane_width: int,
        plane_height: int,
        block_width: int,
        block_height: int,
        values: tuple[int, int, int, int],
    ) -> bytes:
        output = bytearray()
        for block_y in range(plane_height // block_height):
            for row in range(block_height):
                for block_x in range(plane_width // block_width):
                    value = values[block_y * 2 + block_x]
                    output.extend(bytes((value,)) * block_width)
        return bytes(output)

    if chroma_format_idc == 1:
        chroma_width, chroma_height = 16, 16
        chroma_block_width, chroma_block_height = 8, 8
    else:
        chroma_width, chroma_height = 32, 32
        chroma_block_width, chroma_block_height = 16, 16
    return (
        plane(32, 32, 16, 16, (32, 64, 64, 96))
        + plane(chroma_width, chroma_height, chroma_block_width, chroma_block_height, (128, 160, 160, 192))
        + plane(chroma_width, chroma_height, chroma_block_width, chroma_block_height, (64, 96, 96, 128))
    )


def _decode_exact(
    encoded: bytes,
    expected: bytes,
    width: int,
    height: int,
    chroma_format_idc: int,
    bit_depth: int = 8,
) -> dict[str, object]:
    executable = shutil.which("ffmpeg")
    if executable is None:
        return {"available": False, "decoded": False, "exact": False}
    if bit_depth not in (8, 10):
        raise ValueError("supported validation bit depths are 8 and 10")
    if bit_depth == 10 and chroma_format_idc != 1:
        raise ValueError("the Main10 validation gate currently uses 4:2:0")
    pix_fmt = (
        {1: "yuv420p", 2: "yuv422p", 3: "yuv444p"}[chroma_format_idc]
        if bit_depth == 8
        else "yuv420p10le"
    )
    with tempfile.TemporaryDirectory(prefix="pixel_refine_heic_production_") as directory:
        source = Path(directory) / "sample.heic"
        source.write_bytes(encoded)
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
                pix_fmt,
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    return {
        "available": True,
        "decoded": process.returncode == 0,
        "exact": process.returncode == 0 and process.stdout == expected,
        "decoded_bytes": len(process.stdout),
        "expected_bytes": len(expected),
        "stderr": process.stderr.decode("utf-8", errors="replace")[-300:],
        "width": width,
        "height": height,
        "pix_fmt": pix_fmt,
        "bit_depth": bit_depth,
    }


def run_matrix() -> dict[str, object]:
    cases: list[dict[str, object]] = []
    for width, height, chroma_format_idc in (
        (16, 16, 1),
        (32, 16, 1),
        (18, 22, 1),
        (18, 20, 2),
        (17, 19, 3),
        (32, 16, 3),
    ):
        samples = _samples(width, height, chroma_format_idc)
        encoded = package_heic_ipcm_aot(
            samples,
            width=width,
            height=height,
            chroma_format_idc=chroma_format_idc,
        )
        repeated = package_heic_ipcm_aot(
            samples,
            width=width,
            height=height,
            chroma_format_idc=chroma_format_idc,
        )
        if encoded != repeated:
            raise AssertionError("HEIC I_PCM output is not deterministic")
        if not parse_heif_aot(encoded):
            raise AssertionError("HEIC container parser rejected its own output")
        decoded = _decode_exact(
            encoded, samples, width, height, chroma_format_idc
        )
        if not decoded["exact"]:
            raise AssertionError(f"external HEIC parity failed: {decoded}")
        cases.append(
            {
                "width": width,
                "height": height,
                "chroma_format_idc": chroma_format_idc,
                "input_bytes": len(samples),
                "heic_bytes": len(encoded),
                "deterministic": True,
                "container_parser": True,
                "external": decoded,
            }
        )
    auto_cases: list[dict[str, object]] = []
    constant = bytes((128,)) * _sample_count(16, 16, 1)
    for name, samples, width, height, chroma_format_idc in (
        ("arbitrary_fallback", _samples(16, 16, 1), 16, 16, 1),
        ("arbitrary_32x32_420_fallback", _samples(32, 32, 1), 32, 32, 1),
        ("arbitrary_422_fallback", _samples(18, 20, 2), 18, 20, 2),
        ("arbitrary_444_fallback", _samples(17, 19, 3), 17, 19, 3),
        ("constant_compressed", constant, 16, 16, 1),
    ):
        encoded = package_heic_image_aot(
            samples,
            width,
            height,
            bit_depth=8,
            chroma_format_idc=chroma_format_idc,
            mode="auto",
        )
        decoded = _decode_exact(
            encoded,
            samples,
            width,
            height,
            chroma_format_idc,
        )
        if not decoded["exact"]:
            raise AssertionError(f"automatic HEIC profile failed: {decoded}")
        auto_cases.append(
            {
                "name": name,
                "bytes": len(encoded),
                "external": decoded,
            }
        )

    main10_cases: list[dict[str, object]] = []
    for name, samples in (
        ("main10_arbitrary_fallback", _samples10(16, 16)),
        ("main10_constant_compressed", _constant10(16, 16)),
    ):
        encoded = package_heic_image_aot(
            samples,
            16,
            16,
            bit_depth=10,
            chroma_format_idc=1,
            mode="auto",
        )
        repeated = package_heic_image_aot(
            samples,
            16,
            16,
            bit_depth=10,
            chroma_format_idc=1,
            mode="auto",
        )
        if encoded != repeated:
            raise AssertionError("Main10 automatic HEIC output is not deterministic")
        decoded = _decode_exact(encoded, samples, 16, 16, 1, bit_depth=10)
        if not decoded["exact"]:
            raise AssertionError(f"automatic Main10 HEIC profile failed: {decoded}")
        main10_cases.append(
            {
                "name": name,
                "width": 16,
                "height": 16,
                "bit_depth": 10,
                "chroma_format_idc": 1,
                "input_bytes": len(samples),
                "heic_bytes": len(encoded),
                "deterministic": True,
                "external": decoded,
            }
        )

    main10_large_samples = _samples10(32, 32)
    main10_large_encoded = package_heic_image_aot(
        main10_large_samples,
        32,
        32,
        bit_depth=10,
        chroma_format_idc=1,
        mode="auto",
    )
    main10_large_repeated = package_heic_image_aot(
        main10_large_samples,
        32,
        32,
        bit_depth=10,
        chroma_format_idc=1,
        mode="auto",
    )
    if main10_large_encoded != main10_large_repeated:
        raise AssertionError("larger Main10 automatic HEIC output is not deterministic")
    main10_large_decoded = _decode_exact(
        main10_large_encoded,
        main10_large_samples,
        32,
        32,
        1,
        bit_depth=10,
    )
    if not main10_large_decoded["exact"]:
        raise AssertionError(f"larger automatic Main10 HEIC profile failed: {main10_large_decoded}")
    main10_cases.append(
        {
            "name": "main10_32x32_arbitrary_fallback",
            "width": 32,
            "height": 32,
            "bit_depth": 10,
            "chroma_format_idc": 1,
            "input_bytes": len(main10_large_samples),
            "heic_bytes": len(main10_large_encoded),
            "deterministic": True,
            "external": main10_large_decoded,
        }
    )

    main10_multirow_samples = _block_constant_samples10(32, 32)
    main10_multirow_encoded = package_heic_image_aot(
        main10_multirow_samples,
        32,
        32,
        bit_depth=10,
        chroma_format_idc=1,
        mode="auto",
    )
    main10_multirow_decoded = _decode_exact(
        main10_multirow_encoded,
        main10_multirow_samples,
        32,
        32,
        1,
        bit_depth=10,
    )
    if not main10_multirow_decoded["exact"]:
        raise AssertionError(
            f"multi-row compressed Main10 HEIC profile failed: {main10_multirow_decoded}"
        )
    main10_cases.append(
        {
            "name": "main10_32x32_block_constant_compressed",
            "width": 32,
            "height": 32,
            "bit_depth": 10,
            "chroma_format_idc": 1,
            "input_bytes": len(main10_multirow_samples),
            "heic_bytes": len(main10_multirow_encoded),
            "deterministic": True,
            "external": main10_multirow_decoded,
        }
    )

    multirow_samples = _block_constant_samples(32, 32, 1)
    multirow_encoded = package_heic_image_aot(
        multirow_samples,
        32,
        32,
        bit_depth=8,
        chroma_format_idc=1,
        mode="compressed",
    )
    multirow_decoded = _decode_exact(multirow_encoded, multirow_samples, 32, 32, 1)
    if not multirow_decoded["exact"]:
        raise AssertionError(f"multi-row compressed HEIC parity failed: {multirow_decoded}")
    auto_cases.append(
        {
            "name": "multirow_block_constant_compressed",
            "bytes": len(multirow_encoded),
            "external": multirow_decoded,
        }
    )

    multirow_444_samples = _block_constant_samples(32, 32, 3)
    multirow_444_encoded = package_heic_image_aot(
        multirow_444_samples,
        32,
        32,
        bit_depth=8,
        chroma_format_idc=3,
        mode="auto",
    )
    multirow_444_decoded = _decode_exact(
        multirow_444_encoded, multirow_444_samples, 32, 32, 3
    )
    if not multirow_444_decoded["exact"]:
        raise AssertionError(
            f"multi-row 4:4:4 compressed HEIC parity failed: {multirow_444_decoded}"
        )
    auto_cases.append(
        {
            "name": "multirow_444_block_constant_auto",
            "bytes": len(multirow_444_encoded),
            "external": multirow_444_decoded,
        }
    )

    for level in (-32, -64, -96, -128, -160, -192, -256):
        sparse_ac_samples = hevc_general_sparse_ac_fixture_samples(level)
        sparse_ac_encoded = package_heic_image_aot(
            sparse_ac_samples,
            16,
            16,
            bit_depth=8,
            chroma_format_idc=1,
            mode="auto",
        )
        sparse_ac_decoded = _decode_exact(
            sparse_ac_encoded, sparse_ac_samples, 16, 16, 1
        )
        if not sparse_ac_decoded["exact"]:
            raise AssertionError(
                f"pixel-derived AC HEIC parity failed for {level}: {sparse_ac_decoded}"
            )
        auto_cases.append(
            {
                "name": f"pixel_derived_sparse_ac_auto_{level}",
                "bytes": len(sparse_ac_encoded),
                "external": sparse_ac_decoded,
            }
        )

    multi_ac_samples = hevc_general_sparse_ac_multi_fixture_samples()
    multi_ac_encoded = package_heic_image_aot(
        multi_ac_samples,
        16,
        16,
        bit_depth=8,
        chroma_format_idc=1,
        mode="auto",
    )
    multi_ac_repeated = package_heic_image_aot(
        multi_ac_samples,
        16,
        16,
        bit_depth=8,
        chroma_format_idc=1,
        mode="auto",
    )
    multi_ac_decoded = _decode_exact(multi_ac_encoded, multi_ac_samples, 16, 16, 1)
    if multi_ac_encoded != multi_ac_repeated or not multi_ac_decoded["exact"]:
        raise AssertionError(f"pixel-derived multi-AC HEIC parity failed: {multi_ac_decoded}")
    auto_cases.append(
        {
            "name": "pixel_derived_multi_ac_auto",
            "bytes": len(multi_ac_encoded),
            "external": multi_ac_decoded,
        }
    )
    for x, y in ((0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 3)):
        sparse_ac_samples = hevc_general_sparse_ac_fixture_samples(-128, x=x, y=y)
        sparse_ac_encoded = package_heic_image_aot(
            sparse_ac_samples,
            16,
            16,
            bit_depth=8,
            chroma_format_idc=1,
            mode="auto",
        )
        sparse_ac_decoded = _decode_exact(
            sparse_ac_encoded, sparse_ac_samples, 16, 16, 1
        )
        if not sparse_ac_decoded["exact"]:
            raise AssertionError(
                f"pixel-derived AC HEIC parity failed for {(x, y)}: {sparse_ac_decoded}"
            )
        auto_cases.append(
            {
                "name": f"pixel_derived_sparse_ac_auto_{x}_{y}_-128",
                "bytes": len(sparse_ac_encoded),
                "external": sparse_ac_decoded,
            }
        )

    fallback_422_samples = _samples(18, 20, 2)
    fallback_422_encoded = package_heic_image_aot(
        fallback_422_samples,
        18,
        20,
        bit_depth=8,
        chroma_format_idc=2,
        mode="auto",
    )
    fallback_422_decoded = _decode_exact(
        fallback_422_encoded, fallback_422_samples, 18, 20, 2
    )
    if not fallback_422_decoded["exact"]:
        raise AssertionError(f"4:2:2 automatic I_PCM fallback failed: {fallback_422_decoded}")
    auto_cases.append(
        {
            "name": "arbitrary_422_lossless_auto_fallback",
            "bytes": len(fallback_422_encoded),
            "external": fallback_422_decoded,
        }
    )

    compressed_rejected = False
    try:
        package_heic_image_aot(
            _samples(16, 16, 1),
            16,
            16,
            mode="compressed",
        )
    except ValueError:
        compressed_rejected = True
    if not compressed_rejected:
        raise AssertionError("unsupported arbitrary compressed HEIC input was accepted")

    compressed_422_rejected = False
    try:
        package_heic_image_aot(
            fallback_422_samples,
            18,
            20,
            bit_depth=8,
            chroma_format_idc=2,
            mode="compressed",
        )
    except Exception:
        compressed_422_rejected = True
    if not compressed_422_rejected:
        raise AssertionError("unsupported compressed 4:2:2 HEIC input was accepted")

    return {
        "passed": True,
        "case_count": len(cases),
        "auto_profile_case_count": len(auto_cases),
        "auto_profiles": auto_cases,
        "main10_auto_profile_case_count": len(main10_cases),
        "main10_auto_profiles": main10_cases,
        "unsupported_compressed_rejected": compressed_rejected,
        "unsupported_compressed_422_rejected": compressed_422_rejected,
        "lossless_8bit_arbitrary_samples": True,
        "variable_chroma_formats": True,
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_matrix()
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
