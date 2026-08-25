"""Pure helper tests for the resize coordinate-domain parity probe."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_algorithm.aot_py.tools.probe_resize_partition import (
    DEFAULT_CASES,
    _parse_interpolations,
    _validate_device_identity,
)


class ResizePartitionProbeTests(unittest.TestCase):
    def test_default_interpolation_order(self):
        self.assertEqual(_parse_interpolations(None), ("linear", "cubic", "area"))

    def test_explicit_interpolations_are_deduplicated(self):
        self.assertEqual(
            _parse_interpolations("cubic,linear,cubic"),
            ("cubic", "linear"),
        )

    def test_unknown_interpolation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown interpolation"):
            _parse_interpolations("linear,lanczos")

    def test_fixture_shapes_are_non_multiple_of_default_tile(self):
        for source_shape, target_dsize in DEFAULT_CASES:
            self.assertNotEqual(source_shape[0] % 7, 0)
            self.assertNotEqual(source_shape[1] % 7, 0)
            self.assertNotEqual(target_dsize[0] % 7, 0)
            self.assertNotEqual(target_dsize[1] % 7, 0)

    def test_device_identity_guard_fails_closed(self):
        _validate_device_identity(
            "Intel(R) UHD Graphics 620",
            expected_vendor="intel",
            expected_device="Intel(R) UHD Graphics 620",
        )
        with self.assertRaisesRegex(RuntimeError, "vendor mismatch"):
            _validate_device_identity(
                "Intel(R) UHD Graphics 620", expected_vendor="nvidia"
            )
        with self.assertRaisesRegex(RuntimeError, "device mismatch"):
            _validate_device_identity(
                "Intel(R) UHD Graphics 620",
                expected_device="NVIDIA GeForce MX150",
            )


if __name__ == "__main__":
    unittest.main()
