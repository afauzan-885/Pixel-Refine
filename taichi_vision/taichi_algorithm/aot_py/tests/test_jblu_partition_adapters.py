"""Deterministic semantic CPU gates for joint bilateral upsampling."""

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
    JBLU_PARTITION_ADAPTER_OPERATIONS,
    register_jblu_partition_adapters,
    run_jblu_partition_tiled,
    verify_jblu_partition_parity,
)


class JBLUPartitionAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_jblu_partition_adapters()

    def test_registration_is_explicit_and_native_fail_closed(self):
        self.assertEqual(JBLU_PARTITION_ADAPTER_OPERATIONS, ("joint_bilateral_upsample",))
        adapter = registered_block_adapters()["joint_bilateral_upsample"]
        self.assertTrue(adapter.partition_ready)
        self.assertTrue(adapter.metadata["semantic_only"])
        self.assertTrue(adapter.metadata["deterministic_merge"])
        self.assertTrue(can_partition_block("joint_bilateral_upsample", "cpu"))
        self.assertFalse(can_auto_block("joint_bilateral_upsample", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("joint_bilateral_upsample", "cpu"))
        self.assertFalse(can_auto_partition_dispatch("joint_bilateral_upsample", "vulkan"))

    def test_non_multiple_scalar_flow_and_rgb_parity(self):
        rng = np.random.default_rng(20260810)
        guide = rng.random((11, 15), dtype=np.float32)
        cases = (
            (rng.random((5, 7), dtype=np.float32), "medium"),
            (rng.random((4, 6, 2), dtype=np.float32), "low"),
            (rng.random((4, 6, 3), dtype=np.float32), "high"),
        )
        for source, preset in cases:
            with self.subTest(shape=source.shape, preset=preset):
                first = verify_jblu_partition_parity(
                    "joint_bilateral_upsample",
                    (source, guide),
                    block_size=(4, 6),
                    params={"preset": preset},
                )
                second = verify_jblu_partition_parity(
                    "joint_bilateral_upsample",
                    (source, guide),
                    block_size=(7, 5),
                    params={"preset": preset},
                )
                self.assertTrue(first["passed"], first)
                self.assertTrue(second["passed"], second)
                self.assertEqual(first["max_abs_error"], 0.0)
                self.assertEqual(second["max_abs_error"], 0.0)
                left = run_jblu_partition_tiled(
                    "joint_bilateral_upsample",
                    (source, guide),
                    block_size=(4, 6),
                    params={"preset": preset},
                )
                right = run_jblu_partition_tiled(
                    "joint_bilateral_upsample",
                    (source, guide),
                    block_size=(7, 5),
                    params={"preset": preset},
                )
                np.testing.assert_array_equal(left, right)

    def test_unsupported_parameters_fail_closed(self):
        source = np.zeros((4, 6), dtype=np.float32)
        guide = np.zeros((11, 15), dtype=np.float32)
        with self.assertRaises(ValueError):
            verify_jblu_partition_parity(
                "joint_bilateral_upsample",
                (source, guide),
                block_size=(4, 6),
                params={"preset": "unsupported"},
            )
        with self.assertRaises(TypeError):
            verify_jblu_partition_parity(
                "joint_bilateral_upsample",
                (source.astype(np.float16), guide),
                block_size=(4, 6),
            )
        with self.assertRaises(ValueError):
            verify_jblu_partition_parity(
                "joint_bilateral_upsample",
                (source, guide[..., None]),
                block_size=(4, 6),
            )


if __name__ == "__main__":
    unittest.main()
