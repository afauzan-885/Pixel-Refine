"""External qualification for the bounded HEVC DC-intra profiles.

FFmpeg is an oracle used only by this verifier.  The encoder and HEIF
packager do not import or invoke it.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from .heif_aot import package_heic_ctu_stripes_aot, package_heic_flat_aot
from .hevc_general_aot import (
    HEVCGeneralProfileError,
    build_hevc_general_picture,
    hevc_general_sparse_ac_fixture_samples,
    hevc_general_sparse_ac_multi_fixture_samples,
)
from .hevc_general10_aot import build_hevc_general10_picture


def _constant_samples(width: int, height: int, y: int, cb: int, cr: int) -> bytes:
    chroma_samples = (width // 2) * (height // 2)
    return (
        bytes((y,)) * (width * height)
        + bytes((cb,)) * chroma_samples
        + bytes((cr,)) * chroma_samples
    )


def _stripe_samples(
    width: int,
    y_values: tuple[int, ...],
    cb_values: tuple[int, ...],
    cr_values: tuple[int, ...],
) -> bytes:
    ctu_count = width // 16
    if not (len(y_values) == len(cb_values) == len(cr_values) == ctu_count):
        raise ValueError("one Y/Cb/Cr value is required for every horizontal CTU")
    y_row = b"".join(bytes((value,)) * 16 for value in y_values)
    cb_row = b"".join(bytes((value,)) * 8 for value in cb_values)
    cr_row = b"".join(bytes((value,)) * 8 for value in cr_values)
    return y_row * 16 + cb_row * 8 + cr_row * 8


def _constant_samples_444(width: int, height: int, y: int, cb: int, cr: int) -> bytes:
    plane_samples = width * height
    return (
        bytes((y,)) * plane_samples
        + bytes((cb,)) * plane_samples
        + bytes((cr,)) * plane_samples
    )


def _constant_samples_10(width: int, height: int, y: int, cb: int, cr: int) -> bytes:
    chroma_samples = (width // 2) * (height // 2)

    def plane(value: int, count: int) -> bytes:
        return b"".join(int(value).to_bytes(2, "little") for _ in range(count))

    return (
        plane(y, width * height)
        + plane(cb, chroma_samples)
        + plane(cr, chroma_samples)
    )


def _stripe_samples_10(
    y_values: tuple[int, ...],
    cb_values: tuple[int, ...],
    cr_values: tuple[int, ...],
) -> bytes:
    if not (len(y_values) == len(cb_values) == len(cr_values) == 2):
        raise ValueError("the Main10 stripe fixture requires two CTUs")

    def row(values: tuple[int, ...], block_width: int) -> bytes:
        return b"".join(int(value).to_bytes(2, "little") * block_width for value in values)

    return (
        row(y_values, 16) * 16
        + row(cb_values, 8) * 8
        + row(cr_values, 8) * 8
    )


def _stripe_samples_444(
    width: int,
    y_values: tuple[int, ...],
    cb_values: tuple[int, ...],
    cr_values: tuple[int, ...],
) -> bytes:
    ctu_count = width // 16
    if not (len(y_values) == len(cb_values) == len(cr_values) == ctu_count):
        raise ValueError("one Y/Cb/Cr value is required for every horizontal CTU")
    y_row = b"".join(bytes((value,)) * 16 for value in y_values)
    cb_row = b"".join(bytes((value,)) * 16 for value in cb_values)
    cr_row = b"".join(bytes((value,)) * 16 for value in cr_values)
    return y_row * 16 + cb_row * 16 + cr_row * 16


def _decode_exact(
    executable: str,
    encoded: bytes,
    suffix: str,
    expected: bytes,
    *,
    pix_fmt: str = "yuv420p",
) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="pixel_refine_hevc_general_") as directory:
        source = Path(directory) / f"sample{suffix}"
        source.write_bytes(encoded)
        process = subprocess.run(
            [
                executable,
                "-v", "error",
                "-i", str(source),
                "-frames:v", "1",
                "-f", "rawvideo",
                "-pix_fmt", pix_fmt,
                "-",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    return {
        "returncode": process.returncode,
        "decoded_bytes": len(process.stdout),
        "expected_bytes": len(expected),
        "exact": process.returncode == 0 and process.stdout == expected,
        "stderr": process.stderr.decode("utf-8", errors="replace")[-500:],
    }


def _rejection_checks() -> dict[str, bool]:
    width, height = 32, 16
    arbitrary_inside_ctu = bytearray(_constant_samples(width, height, 128, 128, 128))
    arbitrary_inside_ctu[1] = 129
    rejected_inside_ctu = False
    try:
        build_hevc_general_picture(arbitrary_inside_ctu, width, height)
    except HEVCGeneralProfileError:
        rejected_inside_ctu = True

    multirow = bytearray(_constant_samples(32, 32, 128, 128, 128))
    multirow[16] = 129
    rejected_nonconstant_multirow = False
    try:
        build_hevc_general_picture(multirow, 32, 32)
    except HEVCGeneralProfileError:
        rejected_nonconstant_multirow = True

    rejected_stripe_height = False
    try:
        package_heic_ctu_stripes_aot(_constant_samples(32, 32, 128, 128, 128), 32, 32)
    except ValueError:
        rejected_stripe_height = True

    rejected_422_compressed = False
    try:
        samples_422 = (
            bytes((128,)) * (32 * 16)
            + bytes((128,)) * (16 * 16)
            + bytes((128,)) * (16 * 16)
        )
        build_hevc_general_picture(
            samples_422,
            32,
            16,
            chroma_format_idc=2,
        )
    except HEVCGeneralProfileError:
        rejected_422_compressed = True

    return {
        "arbitrary_inside_ctu": rejected_inside_ctu,
        "nonconstant_multirow": rejected_nonconstant_multirow,
        "stripe_height": rejected_stripe_height,
        "compressed_422_is_explicitly_bounded": rejected_422_compressed,
    }


def run_verification() -> dict[str, object]:
    executable = shutil.which("ffmpeg")
    if executable is None:
        return {"ffmpeg_available": False, "all_exact": False, "reason": "ffmpeg_not_found"}

    max_ctus = 4096 // 16
    max_y = tuple((index * 73 + 19) & 0xFF for index in range(max_ctus))
    max_cb = tuple((index * 151 + 7) & 0xFF for index in range(max_ctus))
    max_cr = tuple((index * 199 + 241) & 0xFF for index in range(max_ctus))
    fixtures = (
        ("constant_16x16", 16, 16, _constant_samples(16, 16, 0, 255, 64), False),
        ("constant_32x32", 32, 32, _constant_samples(32, 32, 127, 129, 1), False),
        (
            "stripes_32x16",
            32,
            16,
            _stripe_samples(32, (32, 224), (64, 192), (240, 16)),
            True,
        ),
        (
            "stripes_64x16",
            64,
            16,
            _stripe_samples(64, (0, 255, 48, 192), (255, 0, 160, 32), (1, 254, 96, 208)),
            True,
        ),
        (
            "stripes_4096x16",
            4096,
            16,
            _stripe_samples(4096, max_y, max_cb, max_cr),
            True,
        ),
    )
    cases: list[dict[str, object]] = []
    for name, width, height, expected, stripe in fixtures:
        picture = build_hevc_general_picture(expected, width, height)
        heic = (
            package_heic_ctu_stripes_aot(expected, width, height)
            if stripe
            else package_heic_flat_aot(expected, width, height)
        )
        annex_result = _decode_exact(executable, picture.annex_b, ".h265", expected)
        heic_result = _decode_exact(executable, heic, ".heic", expected)
        cases.append(
            {
                "name": name,
                "width": width,
                "height": height,
                "input_bytes": len(expected),
                "annex_b_bytes": len(picture.annex_b),
                "heic_bytes": len(heic),
                "annex_b": annex_result,
                "heic": heic_result,
            }
        )

    fixtures_444 = (
        (
            "constant_444_16x16",
            16,
            16,
            _constant_samples_444(16, 16, 17, 231, 91),
            False,
        ),
        (
            "stripes_444_32x16",
            32,
            16,
            _stripe_samples_444(32, (32, 224), (64, 192), (240, 16)),
            True,
        ),
    )
    for name, width, height, expected, stripe in fixtures_444:
        picture = build_hevc_general_picture(
            expected,
            width,
            height,
            chroma_format_idc=3,
        )
        heic = (
            package_heic_ctu_stripes_aot(
                expected,
                width,
                height,
                chroma_format_idc=3,
            )
            if stripe
            else package_heic_flat_aot(
                expected,
                width,
                height,
                chroma_format_idc=3,
            )
        )
        annex_result = _decode_exact(
            executable,
            picture.annex_b,
            ".h265",
            expected,
            pix_fmt="yuv444p",
        )
        heic_result = _decode_exact(
            executable,
            heic,
            ".heic",
            expected,
            pix_fmt="yuv444p",
        )
        cases.append(
            {
                "name": name,
                "width": width,
                "height": height,
                "chroma_format_idc": 3,
                "input_bytes": len(expected),
                "annex_b_bytes": len(picture.annex_b),
                "heic_bytes": len(heic),
                "annex_b": annex_result,
                "heic": heic_result,
            }
        )

    # Syntax-only AC probe: these streams intentionally do not claim exact
    # reconstruction of the all-128 source because the supplied coefficient
    # is an independent residual.  The gate is external decoder acceptance
    # and the expected frame size, which validates significance, sign, and
    # coeff_abs_level_remaining ordering before pixel-to-transform derivation
    # is connected to the production profile.
    probe_expected = _constant_samples(16, 16, 128, 128, 128)
    probe_cases: list[dict[str, object]] = []
    for coefficient in ((1, 0, 2), (0, 2, -128), (3, 3, 255)):
        picture = build_hevc_general_picture(
            probe_expected,
            16,
            16,
            sparse_chroma_coeff=coefficient,
        )

        heic = package_heic_flat_aot(
            probe_expected,
            16,
            16,
            sparse_chroma_coeff=coefficient,
        )
        annex_result = _decode_exact(
            executable,
            picture.annex_b,
            ".h265",
            probe_expected,
        )
        heic_result = _decode_exact(
            executable,
            heic,
            ".heic",
            probe_expected,
        )
        probe_cases.append(
            {
                "coefficient": coefficient,
                "annex_b": annex_result,
                "heic": heic_result,
                "annex_b_valid": annex_result["returncode"] == 0
                and annex_result["decoded_bytes"] == len(probe_expected),
                "heic_valid": heic_result["returncode"] == 0
                and heic_result["decoded_bytes"] == len(probe_expected),
            }
        )

    multi_probe_coefficients = ((0, 1, 1), (1, 0, -1))
    multi_probe_picture = build_hevc_general_picture(
        probe_expected,
        16,
        16,
        sparse_chroma_coefficients=multi_probe_coefficients,
    )
    multi_probe_heic = package_heic_flat_aot(
        probe_expected,
        16,
        16,
        sparse_chroma_coefficients=multi_probe_coefficients,
    )
    multi_probe_annex_result = _decode_exact(
        executable,
        multi_probe_picture.annex_b,
        ".h265",
        probe_expected,
    )
    multi_probe_heic_result = _decode_exact(
        executable,
        multi_probe_heic,
        ".heic",
        probe_expected,
    )
    multi_probe_valid = bool(
        multi_probe_annex_result["returncode"] == 0
        and multi_probe_heic_result["returncode"] == 0
        and multi_probe_annex_result["decoded_bytes"] == len(probe_expected)
        and multi_probe_heic_result["decoded_bytes"] == len(probe_expected)
    )

    pixel_ac_expected = hevc_general_sparse_ac_fixture_samples()
    pixel_ac_picture = build_hevc_general_picture(pixel_ac_expected, 16, 16)
    pixel_ac_heic = package_heic_flat_aot(pixel_ac_expected, 16, 16)
    pixel_ac_annex_result = _decode_exact(
        executable, pixel_ac_picture.annex_b, ".h265", pixel_ac_expected
    )
    pixel_ac_heic_result = _decode_exact(
        executable, pixel_ac_heic, ".heic", pixel_ac_expected
    )
    pixel_ac_exact = bool(
        pixel_ac_annex_result["exact"] and pixel_ac_heic_result["exact"]
    )

    pixel_multi_ac_expected = hevc_general_sparse_ac_multi_fixture_samples()
    pixel_multi_ac_picture = build_hevc_general_picture(pixel_multi_ac_expected, 16, 16)
    pixel_multi_ac_heic = package_heic_flat_aot(pixel_multi_ac_expected, 16, 16)
    pixel_multi_ac_annex_result = _decode_exact(
        executable,
        pixel_multi_ac_picture.annex_b,
        ".h265",
        pixel_multi_ac_expected,
    )
    pixel_multi_ac_heic_result = _decode_exact(
        executable,
        pixel_multi_ac_heic,
        ".heic",
        pixel_multi_ac_expected,
    )
    pixel_multi_ac_exact = bool(
        pixel_multi_ac_annex_result["exact"] and pixel_multi_ac_heic_result["exact"]
    )

    main10_expected = _constant_samples_10(16, 16, 512, 700, 100)
    main10_picture = build_hevc_general10_picture(main10_expected, 16, 16)
    main10_heic = package_heic_flat_aot(
        main10_expected,
        16,
        16,
        bit_depth=10,
    )
    main10_annex_result = _decode_exact(
        executable,
        main10_picture.annex_b,
        ".h265",
        main10_expected,
        pix_fmt="yuv420p10le",
    )
    main10_heic_result = _decode_exact(
        executable,
        main10_heic,
        ".heic",
        main10_expected,
        pix_fmt="yuv420p10le",
    )
    main10_exact = bool(main10_annex_result["exact"] and main10_heic_result["exact"])

    main10_stripe_expected = _stripe_samples_10(
        (100, 900),
        (200, 800),
        (700, 300),
    )
    main10_stripe_picture = build_hevc_general10_picture(
        main10_stripe_expected,
        32,
        16,
    )
    main10_stripe_heic = package_heic_flat_aot(
        main10_stripe_expected,
        32,
        16,
        bit_depth=10,
    )
    main10_stripe_annex_result = _decode_exact(
        executable,
        main10_stripe_picture.annex_b,
        ".h265",
        main10_stripe_expected,
        pix_fmt="yuv420p10le",
    )
    main10_stripe_heic_result = _decode_exact(
        executable,
        main10_stripe_heic,
        ".heic",
        main10_stripe_expected,
        pix_fmt="yuv420p10le",
    )
    main10_stripe_exact = bool(
        main10_stripe_annex_result["exact"] and main10_stripe_heic_result["exact"]
    )

    rejection = _rejection_checks()
    all_exact = all(
        bool(case[container]["exact"])
        for case in cases
        for container in ("annex_b", "heic")
    )
    return {
        "ffmpeg_available": True,
        "ffmpeg_path": executable,
        "profile": "8-bit 4:2:0/4:4:4 QP0 DC-intra horizontal CTU stripes",
        "cases": cases,
        "rejection_checks": rejection,
        "residual_probe_cases": probe_cases,
        "residual_probe_valid": all(
            bool(case["annex_b_valid"]) and bool(case["heic_valid"])
            for case in probe_cases
        ),
        "multi_residual_probe": {
            "coefficients": multi_probe_coefficients,
            "annex_b": multi_probe_annex_result,
            "heic": multi_probe_heic_result,
            "valid": multi_probe_valid,
        },
        "pixel_derived_ac_case": {
            "annex_b": pixel_ac_annex_result,
            "heic": pixel_ac_heic_result,
            "exact": pixel_ac_exact,
        },
        "pixel_derived_multi_ac_case": {
            "annex_b": pixel_multi_ac_annex_result,
            "heic": pixel_multi_ac_heic_result,
            "exact": pixel_multi_ac_exact,
        },
        "main10_case": {
            "annex_b": main10_annex_result,
            "heic": main10_heic_result,
            "exact": main10_exact,
        },
        "main10_stripe_case": {
            "annex_b": main10_stripe_annex_result,
            "heic": main10_stripe_heic_result,
            "exact": main10_stripe_exact,
        },
        "all_exact": (
            all_exact
            and all(rejection.values())
            and main10_exact
            and main10_stripe_exact
            and pixel_multi_ac_exact
        ),
    }


def main() -> int:
    report = run_verification()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (
        report.get("all_exact")
        and report.get("residual_probe_valid")
        and report.get("multi_residual_probe", {}).get("valid")
        and report.get("pixel_derived_ac_case", {}).get("exact")
        and report.get("pixel_derived_multi_ac_case", {}).get("exact")
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
