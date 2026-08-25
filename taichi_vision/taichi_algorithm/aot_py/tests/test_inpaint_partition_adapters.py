"""Deterministic semantic CPU gates for iterative inpainting adapters."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    lookup_block_adapter,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    INPAINT_PARTITION_ADAPTER_OPERATIONS,
    register_inpaint_partition_adapters,
    run_inpaint_partition_tiled,
    verify_inpaint_partition_parity,
)


class InpaintPartitionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_inpaint_partition_adapters()

    @staticmethod
    def _inputs(shape=(17, 23), channels=None):
        rows, cols = np.indices(shape, dtype=np.float32)
        if channels is None:
            source = (rows * np.float32(0.25) + cols * np.float32(0.75)).astype(
                np.float32
            )
        else:
            source = np.stack(
                (
                    rows * np.float32(0.25) + cols * np.float32(0.75),
                    rows * np.float32(0.50) - cols * np.float32(0.25),
                    rows * np.float32(0.125) + cols * np.float32(0.375),
                ),
                axis=2,
            ).astype(np.float32)
        mask = np.zeros(shape, dtype=np.uint8)
        # A compact hole plus an isolated sample exercise multiple distance
        # levels while remaining safe for a non-multiple block grid.
        mask[5:10, 8:13] = 255
        mask[min(13, shape[0] - 1), min(18, shape[1] - 1)] = 1
        return source, mask

    def test_registration_is_explicit_and_native_fail_closed(self):
        self.assertEqual(
            INPAINT_PARTITION_ADAPTER_OPERATIONS,
            ("inpaint", "inpaint_aot"),
        )
        adapter = registered_block_adapters()["inpaint"]
        self.assertIs(lookup_block_adapter("inpaint_aot"), adapter)
        self.assertTrue(adapter.partition_ready)
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["deterministic_merge"])
        for operation in INPAINT_PARTITION_ADAPTER_OPERATIONS:
            self.assertTrue(can_partition_block(operation, "cpu"))
            self.assertFalse(can_auto_block(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
            self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_non_multiple_scalar_rgb_and_alias_parity(self):
        for source, mask, operation, radius, flags in (
            (*self._inputs(), "inpaint", 3, 0),
            (*self._inputs(channels=3), "inpaint_aot", 2, 1),
        ):
            params = {"inpaint_radius": radius, "flags": flags}
            with self.subTest(shape=source.shape, operation=operation):
                first = verify_inpaint_partition_parity(
                    operation,
                    (source, mask),
                    block_size=(5, 7),
                    params=params,
                )
                second = verify_inpaint_partition_parity(
                    operation,
                    (source, mask),
                    block_size=(8, 9),
                    params=params,
                )
                self.assertTrue(first["passed"], first)
                self.assertTrue(second["passed"], second)
                self.assertEqual(first["max_abs_error"], 0.0)
                self.assertEqual(second["max_abs_error"], 0.0)
                left = run_inpaint_partition_tiled(
                    operation,
                    (source, mask),
                    block_size=(5, 7),
                    params=params,
                )
                right = run_inpaint_partition_tiled(
                    operation,
                    (source, mask),
                    block_size=(8, 9),
                    params=params,
                )
                repeat = run_inpaint_partition_tiled(
                    operation,
                    (source, mask),
                    block_size=(5, 7),
                    params=params,
                )
                np.testing.assert_array_equal(left, right)
                np.testing.assert_array_equal(left, repeat)

    def test_unsupported_parameters_fail_closed(self):
        source, mask = self._inputs(shape=(9, 13))
        cases = (
            {"inpaint_radius": 0},
            {"inpaint_radius": 9},
            {"inpaint_radius": 1.5},
            {"flags": 2},
            {"flags": 1.5},
        )
        for params in cases:
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    verify_inpaint_partition_parity(
                        "inpaint", (source, mask), block_size=(4, 5), params=params
                    )
        with self.assertRaises(TypeError):
            verify_inpaint_partition_parity(
                "inpaint", (source.astype(np.float16), mask), block_size=(4, 5)
            )
        with self.assertRaises(ValueError):
            verify_inpaint_partition_parity(
                "inpaint", (source, mask[:-1]), block_size=(4, 5)
            )
        with self.assertRaises(ValueError):
            verify_inpaint_partition_parity(
                "inpaint",
                (np.zeros((9, 13, 2), dtype=np.float32), mask),
                block_size=(4, 5),
            )


if __name__ == "__main__":
    unittest.main()
