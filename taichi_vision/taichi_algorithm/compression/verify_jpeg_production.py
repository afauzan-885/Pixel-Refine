"""Focused JPEG production matrix.

This is a validation-only harness.  NumPy creates deterministic fixtures and
Pillow is used only as an independent decoder; neither is imported by the
native codec runtime.  The matrix covers odd dimensions, all supported RGB
subsampling modes, both Huffman modes, quality extremes, restart intervals,
grayscale, deterministic output, and external decode shape parity.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .jpeg_aot import jpeg_encode_aot
from .verify_compression import _decode_png_or_jpeg, _jpeg_restart_state


def _fixture(height: int, width: int, channels: int) -> np.ndarray:
    yy, xx = np.indices((int(height), int(width)), dtype=np.uint32)
    red = (xx * 17 + yy * 5 + (xx ^ yy)) & 255
    green = (xx * 3 + yy * 19 + ((xx * yy) & 63)) & 255
    blue = ((xx * 29) ^ (yy * 11) ^ (xx * yy * 3)) & 255
    if channels == 1:
        return ((red + green + blue) // 3).astype(np.uint8)
    return np.stack((red, green, blue), axis=-1).astype(np.uint8)


def _mcu_count(height: int, width: int, subsampling: str) -> int:
    block_height = 16 if subsampling == "420" else 8
    block_width = 16 if subsampling in {"422", "420"} else 8
    return ((int(height) + block_height - 1) // block_height) * (
        (int(width) + block_width - 1) // block_width
    )


def _validate(encoded: bytes, source: np.ndarray, *, subsampling: str, restart: int) -> dict:
    if not encoded.startswith(b"\xff\xd8") or not encoded.endswith(b"\xff\xd9"):
        raise AssertionError("JPEG SOI/EOI markers are missing")
    decoded = _decode_png_or_jpeg(encoded, "jpeg")
    expected_shape = [int(source.shape[0]), int(source.shape[1]), 3]
    if list(decoded.shape) != expected_shape:
        raise AssertionError(f"decoded shape mismatch: {decoded.shape} != {expected_shape}")
    dri, markers = _jpeg_restart_state(encoded)
    expected_count = 0 if not restart else max(0, (_mcu_count(*source.shape[:2], subsampling) - 1) // restart)
    expected_markers = tuple(index % 8 for index in range(expected_count))
    if restart:
        if dri != restart or markers != expected_markers:
            raise AssertionError(
                f"restart state mismatch: DRI={dri}, markers={markers}, expected={expected_markers}"
            )
    elif dri is not None or markers:
        raise AssertionError("restart markers present for restart_interval=0")
    return {
        "bytes": len(encoded),
        "decoded_shape": list(decoded.shape),
        "dri": dri,
        "restart_markers": list(markers),
    }


def run_matrix() -> dict:
    dimensions = ((1, 1), (7, 9), (16, 17), (31, 33))
    qualities = (1, 50, 100)
    restart_intervals = (0, 1, 3)
    cases: list[dict] = []
    for height, width in dimensions:
        for subsampling in ("444", "422", "420"):
            image = _fixture(height, width, 3)
            for quality in qualities:
                for huffman in ("standard", "optimized"):
                    for restart in restart_intervals:
                        encoded = jpeg_encode_aot(
                            image,
                            quality=quality,
                            subsampling=subsampling,
                            huffman=huffman,
                            restart_interval=restart,
                        )
                        repeated = jpeg_encode_aot(
                            image,
                            quality=quality,
                            subsampling=subsampling,
                            huffman=huffman,
                            restart_interval=restart,
                        )
                        if encoded != repeated:
                            raise AssertionError("JPEG output is not deterministic")
                        result = _validate(
                            encoded, image, subsampling=subsampling, restart=restart
                        )
                        cases.append(
                            {
                                "channels": 3,
                                "shape": [height, width, 3],
                                "subsampling": subsampling,
                                "quality": quality,
                                "huffman": huffman,
                                "restart_interval": restart,
                                "deterministic": True,
                                **result,
                            }
                        )

        for quality in qualities:
            for huffman in ("standard", "optimized"):
                for restart in restart_intervals:
                    image = _fixture(height, width, 1)
                    encoded = jpeg_encode_aot(
                        image,
                        quality=quality,
                        grayscale=True,
                        huffman=huffman,
                        restart_interval=restart,
                    )
                    repeated = jpeg_encode_aot(
                        image,
                        quality=quality,
                        grayscale=True,
                        huffman=huffman,
                        restart_interval=restart,
                    )
                    if encoded != repeated:
                        raise AssertionError("grayscale JPEG output is not deterministic")
                    if not encoded.startswith(b"\xff\xd8") or not encoded.endswith(b"\xff\xd9"):
                        raise AssertionError("grayscale JPEG SOI/EOI markers are missing")
                    from PIL import Image
                    import io

                    with Image.open(io.BytesIO(encoded)) as decoded_image:
                        decoded = np.asarray(decoded_image.convert("L"))
                    if list(decoded.shape) != [height, width]:
                        raise AssertionError(f"grayscale shape mismatch: {decoded.shape}")
                    dri, markers = _jpeg_restart_state(encoded)
                    expected_count = 0 if not restart else max(0, (_mcu_count(height, width, "444") - 1) // restart)
                    expected_markers = tuple(index % 8 for index in range(expected_count))
                    if restart and (dri != restart or markers != expected_markers):
                        raise AssertionError("grayscale restart state mismatch")
                    if not restart and (dri is not None or markers):
                        raise AssertionError("grayscale restart markers present unexpectedly")
                    cases.append(
                        {
                            "channels": 1,
                            "shape": [height, width],
                            "quality": quality,
                            "huffman": huffman,
                            "restart_interval": restart,
                            "bytes": len(encoded),
                            "decoded_shape": list(decoded.shape),
                            "deterministic": True,
                        }
                    )
    metadata_image = _fixture(17, 19, 3)
    metadata_cases = (
        {"exif": b"unit-exif", "xmp": b"<xmpmeta/>", "icc": b"unit-icc", "comment": "UTF-8 ✓"},
        {
            "exif": b"Exif\x00\x00already-prefixed",
            "xmp": b"http://ns.adobe.com/xap/1.0/\x00<xmpmeta/>",
            "icc": b"",
            "comment": b"bytes-comment",
        },
        {"comment": b""},
        {"icc": bytes(65519)},
        {"icc": bytes(65520)},
        {},
    )
    for metadata in metadata_cases:
        encoded = jpeg_encode_aot(
            metadata_image,
            quality=80,
            subsampling="420",
            huffman="optimized",
            metadata=metadata,
        )
        repeated = jpeg_encode_aot(
            metadata_image,
            quality=80,
            subsampling="420",
            huffman="optimized",
            metadata=metadata,
        )
        if encoded != repeated:
            raise AssertionError("metadata JPEG output is not deterministic")
        decoded = _decode_png_or_jpeg(encoded, "jpeg")
        if list(decoded.shape) != [17, 19, 3]:
            raise AssertionError(f"metadata JPEG shape mismatch: {decoded.shape}")
        icc_count = encoded.count(b"ICC_PROFILE\x00")
        expected_icc_count = 1 if "icc" in metadata else 0
        if "icc" in metadata and len(bytes(metadata["icc"])) > 65519:
            expected_icc_count = 2
        if icc_count != expected_icc_count:
            raise AssertionError(
                f"ICC segmentation mismatch: {icc_count} != {expected_icc_count}"
            )

    invalid_metadata = (
        {"exif": 4},
        {"xmp": "not-bytes"},
        {"icc": True},
        {"comment": 3},
        {"comment": bytes(65534)},
        {"exif": bytes(65534)},
        {"xmp": bytes(65534)},
        {"unknown": b"x"},
        [],
    )
    rejected_metadata = 0
    for metadata in invalid_metadata:
        try:
            jpeg_encode_aot(metadata_image, metadata=metadata)
        except (TypeError, ValueError):
            rejected_metadata += 1
    if rejected_metadata != len(invalid_metadata):
        raise AssertionError("invalid JPEG metadata was accepted")

    return {
        "passed": True,
        "case_count": len(cases),
        "rgb_case_count": sum(case["channels"] == 3 for case in cases),
        "grayscale_case_count": sum(case["channels"] == 1 for case in cases),
        "metadata_case_count": len(metadata_cases),
        "invalid_metadata_rejected": rejected_metadata == len(invalid_metadata),
        "dimensions": [list(value) for value in dimensions],
        "qualities": list(qualities),
        "restart_intervals": list(restart_intervals),
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args()
    report = run_matrix()
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
