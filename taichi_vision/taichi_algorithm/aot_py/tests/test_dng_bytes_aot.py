"""Focused regressions for the NumPy-free DNG byte-buffer surface."""
from __future__ import annotations

import importlib
import struct
import sys
import types
import unittest
import zlib
from pathlib import Path


def _load_dng_module_without_package_initializers():
    algorithm_dir = Path(__file__).resolve().parents[2]
    compression_dir = algorithm_dir / "compression"
    name = "_pixel_refine_dng_native_probe"
    package = types.ModuleType(name)
    package.__path__ = [str(compression_dir)]
    package.__package__ = name
    sys.modules[name] = package
    return importlib.import_module(f"{name}.dng_aot")


def _pack_rows(values: list[int], width: int, height: int, bits: int) -> bytes:
    if bits == 8:
        return bytes(values)
    if bits == 16:
        return struct.pack(f"<{len(values)}H", *values)
    output = bytearray()
    for row_index in range(height):
        accumulator = 0
        available = 0
        row = values[row_index * width:(row_index + 1) * width]
        for value in row:
            accumulator = (accumulator << bits) | value
            available += bits
            while available >= 8:
                available -= 8
                output.append((accumulator >> available) & 255)
                accumulator &= (1 << available) - 1 if available else 0
        if available:
            output.append((accumulator << (8 - available)) & 255)
    return bytes(output)


class DNGBytesAOTTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.numpy_was_loaded = "numpy" in sys.modules
        cls.dng = _load_dng_module_without_package_initializers()

    def test_module_and_round_trip_do_not_import_numpy(self):
        if not self.numpy_was_loaded:
            self.assertNotIn("numpy", sys.modules)
        source = bytes((index * 19 + 7) & 255 for index in range(35))
        encoded = self.dng.encode_dng_bytes(
            memoryview(source),
            width=7,
            height=5,
            bits_per_sample=8,
            compression="packbits",
            predictor="horizontal",
            metadata={"rows_per_strip": 2},
        )
        frame = self.dng.decode_dng_bytes(memoryview(encoded))
        self.assertEqual(frame.raw_bytes, source)
        self.assertEqual(frame.raw_view().tobytes(), source)
        if not self.numpy_was_loaded:
            self.assertNotIn("numpy", sys.modules)

    def test_none_packbits_and_deflate_are_exact_across_bit_depths(self):
        cases = ((8, 7, 5), (12, 9, 4), (16, 6, 3))
        for bits, width, height in cases:
            values = [
                (index * 37 + 11) & ((1 << bits) - 1)
                for index in range(width * height)
            ]
            source = _pack_rows(values, width, height, bits)
            for compression in ("none", "packbits", "deflate"):
                for predictor in ("none", "horizontal"):
                    with self.subTest(
                        bits=bits,
                        compression=compression,
                        predictor=predictor,
                    ):
                        encoded = self.dng.encode_dng_aot(
                            memoryview(source),
                            compression=compression,
                            predictor=predictor,
                            bits_per_sample=bits,
                            width=width,
                            height=height,
                            metadata={"rows_per_strip": 2},
                        )
                        frame = self.dng.decode_dng_bytes(encoded)
                        self.assertEqual(frame.raw_bytes, source)
                        self.assertTrue(
                            self.dng.dng_capability_report(encoded).supported
                        )

    def test_native_inflater_accepts_external_dynamic_deflate(self):
        source = bytes((index * 37 + (index >> 3)) & 255 for index in range(20_000))
        encoded = zlib.compress(source, level=9)
        self.assertEqual((encoded[2] >> 1) & 3, 2)
        decoded = self.dng.inflate_deflate(encoded, len(source))
        self.assertEqual(decoded, source)

    def test_native_deflate_encoder_crosses_stored_block_boundary(self):
        source = bytes(index & 255 for index in range(70_000))
        encoded = self.dng.encode_dng_bytes(
            source,
            width=len(source),
            height=1,
            bits_per_sample=8,
            compression="deflate",
        )
        _endian, tags = self.dng._read_tiff_tags_only(encoded)
        offset = int(tags[273])
        count = int(tags[279])
        self.assertEqual(zlib.decompress(encoded[offset:offset + count]), source)

    def test_fixed_lz77_roundtrip_and_beats_stored_on_repetitive_data(self):
        source = (b"0123456789abcdef" * 8192) + (b"raw-pixel-pattern" * 257)
        fixed = self.dng.deflate_fixed(source)
        stored = self.dng.deflate_stored(source)
        self.assertEqual(fixed[2] & 0x07, 0x03)  # final fixed-Huffman block
        self.assertEqual(self.dng.inflate_deflate(fixed, len(source)), source)
        self.assertLess(len(fixed), len(stored))

        # Verify that the DNG ``compression='deflate'`` route uses the same
        # fixed/LZ77 encoder rather than the legacy PNG implementation.
        width, height = 1024, 64
        dng_source = (b"\x00\x01\x02\x03" * (width * height // 4))
        dng = self.dng.encode_dng_bytes(
            dng_source,
            width=width,
            height=height,
            bits_per_sample=8,
            compression="deflate",
        )
        _endian, tags = self.dng._read_tiff_tags_only(dng)
        offset = int(tags[273])
        count = int(tags[279])
        self.assertEqual(dng[offset + 2] & 0x07, 0x03)
        self.assertEqual(
            self.dng.decode_dng_bytes(dng).raw_bytes,
            dng_source,
        )
        self.assertLess(count, len(dng_source))

    def test_noncanonical_padding_and_truncation_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "padding"):
            self.dng.encode_dng_bytes(
                b"\x00\x01",
                width=1,
                height=1,
                bits_per_sample=12,
            )
        source = bytes(range(16))
        encoded = self.dng.encode_dng_bytes(
            source,
            width=4,
            height=4,
            bits_per_sample=8,
            compression="deflate",
        )
        with self.assertRaises(ValueError):
            self.dng.decode_dng_bytes(encoded[:-1])

    def test_z_legacy_ndarray_dispatch_remains_compatible(self):
        import numpy as np

        source = ((np.arange(30, dtype=np.uint16) * 97 + 13) & 0x0FFF).reshape(5, 6)
        for compression in ("none", "packbits", "deflate", "lossless_jpeg"):
            with self.subTest(compression=compression):
                encoded = self.dng.encode_dng_aot(
                    source,
                    compression=compression,
                    bits_per_sample=12,
                    metadata={"rows_per_strip": 2},
                )
                decoded = self.dng.read_dng_aot(encoded).samples()
                self.assertTrue(np.array_equal(decoded, source))


if __name__ == "__main__":
    unittest.main()
