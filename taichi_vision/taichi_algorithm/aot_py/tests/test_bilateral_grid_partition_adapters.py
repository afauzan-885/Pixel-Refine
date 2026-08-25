"""Deterministic semantic CPU gates for bilateral-grid filtering."""

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
    BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS,
    register_bilateral_grid_partition_adapters,
    run_bilateral_grid_partition_tiled,
    verify_bilateral_grid_partition_parity,
)


class BilateralGridPartitionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_bilateral_grid_partition_adapters()

    def test_registration_is_explicit_and_native_fail_closed(self):
        self.assertEqual(BILATERAL_GRID_PARTITION_ADAPTER_OPERATIONS, ("bilateral_grid_filter",))
        adapter = registered_block_adapters()["bilateral_grid_filter"]
        self.assertTrue(adapter.partition_ready)
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["deterministic_merge"])
        self.assertTrue(can_partition_block("bilateral_grid_filter", "cpu"))
        self.assertFalse(can_auto_block("bilateral_grid_filter", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("bilateral_grid_filter", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("bilateral_grid_filter", "vulkan"))

    def test_non_multiple_gray_and_rgb_all_presets(self):
        rng = np.random.default_rng(20260810)
        gray = rng.random((17, 23), dtype=np.float32)
        rgb = rng.random((11, 15, 3), dtype=np.float32)
        for source in (gray, rgb):
            for preset in ("light", "medium", "heavy"):
                with self.subTest(shape=source.shape, preset=preset):
                    first = verify_bilateral_grid_partition_parity(
                        "bilateral_grid_filter",
                        (source,),
                        block_size=(5, 7),
                        params={"preset": preset},
                    )
                    second = verify_bilateral_grid_partition_parity(
                        "bilateral_grid_filter",
                        (source,),
                        block_size=(8, 9),
                        params={"preset": preset},
                    )
                    self.assertTrue(first["passed"], first)
                    self.assertTrue(second["passed"], second)
                    self.assertEqual(first["max_abs_error"], 0.0)
                    self.assertEqual(second["max_abs_error"], 0.0)
                    left = run_bilateral_grid_partition_tiled(
                        "bilateral_grid_filter",
                        (source,),
                        block_size=(5, 7),
                        params={"preset": preset},
                    )
                    right = run_bilateral_grid_partition_tiled(
                        "bilateral_grid_filter",
                        (source,),
                        block_size=(8, 9),
                        params={"preset": preset},
                    )
                    np.testing.assert_array_equal(left, right)

    def test_unsupported_parameters_fail_closed(self):
        source = np.zeros((9, 13), dtype=np.float32)
        with self.assertRaises(ValueError):
            verify_bilateral_grid_partition_parity(
                "bilateral_grid_filter",
                (source,),
                block_size=(4, 5),
                params={"preset": "unsupported"},
            )
        with self.assertRaises(TypeError):
            verify_bilateral_grid_partition_parity(
                "bilateral_grid_filter",
                (source.astype(np.float16),),
                block_size=(4, 5),
            )
        with self.assertRaises(ValueError):
            verify_bilateral_grid_partition_parity(
                "bilateral_grid_filter",
                (np.zeros((9, 13, 2), dtype=np.float32),),
                block_size=(4, 5),
            )


if __name__ == "__main__":
    unittest.main()
