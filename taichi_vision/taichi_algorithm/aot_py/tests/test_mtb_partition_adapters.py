"""Deterministic semantic CPU gates for the staged MTB adapter."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    MTB_PARTITION_ADAPTER_OPERATIONS,
    register_mtb_partition_adapters,
    run_mtb_partition_tiled,
    verify_mtb_partition_parity,
)


class MTBPartitionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_mtb_partition_adapters()

    def test_registration_is_explicit_and_fail_closed(self):
        self.assertEqual(MTB_PARTITION_ADAPTER_OPERATIONS, ("align_mtb",))
        adapter = registered_block_adapters()["align_mtb"]
        self.assertTrue(adapter.partition_ready)
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["deterministic_merge"])
        self.assertTrue(can_partition_block("align_mtb", "cpu"))
        self.assertFalse(can_auto_block("align_mtb", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("align_mtb", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("align_mtb", "vulkan"))

    def test_non_multiple_parity_and_deterministic_tie(self):
        rows, cols = np.indices((17, 23), dtype=np.float32)
        reference = np.mod(rows * 17.0 + cols * 9.0, 256.0).astype(np.uint8)
        target = np.mod(rows * 17.0 + cols * 9.0 + 13.0, 256.0).astype(np.uint8)
        params = {"max_levels": 4, "tolerance": 4.0 / 255.0}
        first = verify_mtb_partition_parity(
            "align_mtb", (reference, target), block_size=(5, 7), params=params
        )
        second = verify_mtb_partition_parity(
            "align_mtb", (reference, target), block_size=(8, 9), params=params
        )
        self.assertTrue(first["passed"], first)
        self.assertTrue(second["passed"], second)
        self.assertEqual(first["max_abs_error"], 0.0)
        self.assertEqual(second["max_abs_error"], 0.0)
        left = run_mtb_partition_tiled(
            "align_mtb", (reference, target), block_size=(5, 7), params=params
        )
        right = run_mtb_partition_tiled(
            "align_mtb", (reference, target), block_size=(8, 9), params=params
        )
        repeat = run_mtb_partition_tiled(
            "align_mtb", (reference, target), block_size=(5, 7), params=params
        )
        self.assertEqual(left, right)
        self.assertEqual(left, repeat)

    def test_unsupported_parameters_fail_closed(self):
        reference = np.zeros((9, 13), dtype=np.uint8)
        target = np.zeros((9, 13), dtype=np.uint8)
        for params in ({"max_levels": 0}, {"max_levels": 13}, {"tolerance": 1.1}):
            with self.subTest(params=params):
                with self.assertRaises(ValueError):
                    verify_mtb_partition_parity(
                        "align_mtb",
                        (reference, target),
                        block_size=(4, 5),
                        params=params,
                    )
        with self.assertRaises(ValueError):
            verify_mtb_partition_parity(
                "align_mtb",
                (reference, target[:-1]),
                block_size=(4, 5),
            )


if __name__ == "__main__":
    unittest.main()
