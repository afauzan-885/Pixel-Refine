"""Focused semantic CPU contracts for flow-map, normalization, and BRIEF helpers.

These tests intentionally do not qualify a graphics backend.  They exercise
non-multiple output grids and keep automatic/native dispatch fail-closed.
"""

from __future__ import annotations

import unittest

import numpy as np

import taichi_vision.taichi_aot as taichi_aot_facade
from taichi_vision.taichi_algorithm import aot_api

from taichi_vision.taichi_aot.block import (
    can_auto_block,
    can_auto_partition_dispatch,
    can_partition_block,
    registered_block_adapters,
)
from taichi_vision.taichi_aot.block_adapters import (
    BRIEF_PATTERN_ADAPTER_OPERATIONS,
    FLOW_MAP_ADAPTER_OPERATIONS,
    NORMALIZATION_ADAPTER_OPERATIONS,
    register_flow_map_adapters,
    register_specialized_block_adapters,
    run_output_domain_tiled,
    verify_flow_maps_parity,
    verify_normalize_image_parity,
    register_coordinate_domain_adapters,
    verify_coordinate_parity,
)


class SpecializedAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adapters = register_specialized_block_adapters()
        register_coordinate_domain_adapters()

    def test_registration_is_explicit_and_native_fail_closed(self):
        self.assertEqual(set(FLOW_MAP_ADAPTER_OPERATIONS), {"build_flow_maps"})
        self.assertEqual(set(NORMALIZATION_ADAPTER_OPERATIONS), {"normalize_image"})
        self.assertEqual(set(BRIEF_PATTERN_ADAPTER_OPERATIONS), {"generate_brief_pattern"})
        for operation in (
            *FLOW_MAP_ADAPTER_OPERATIONS,
            *NORMALIZATION_ADAPTER_OPERATIONS,
            *BRIEF_PATTERN_ADAPTER_OPERATIONS,
        ):
            with self.subTest(operation=operation):
                adapter = registered_block_adapters()[operation]
                self.assertTrue(adapter.partition_ready)
                self.assertTrue(adapter.metadata["semantic_only"])
                self.assertFalse(adapter.metadata["native_runtime"])
                self.assertTrue(can_partition_block(operation, "cpu"))
                self.assertFalse(can_auto_block(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "cpu"))
                self.assertFalse(can_auto_partition_dispatch(operation, "vulkan"))

    def test_public_facades_export_specialized_contracts(self):
        for facade in (taichi_aot_facade, aot_api):
            with self.subTest(facade=facade.__name__):
                self.assertIs(facade.register_flow_map_adapters, register_flow_map_adapters)
                self.assertTrue(hasattr(facade, "verify_flow_maps_parity"))
                self.assertTrue(hasattr(facade, "verify_normalize_image_parity"))
                self.assertEqual(facade.FLOW_MAP_ADAPTER_OPERATIONS, ("build_flow_maps",))

    def test_flow_maps_two_input_forms_non_multiple(self):
        rng = np.random.default_rng(20260810)
        flow = rng.normal(0.0, 0.25, size=(7, 11, 2)).astype(np.float32)
        for inputs in ((flow,), (flow[..., 0], flow[..., 1])):
            with self.subTest(input_count=len(inputs)):
                report = verify_flow_maps_parity(
                    inputs,
                    output_shape=(23, 29),
                    block_size=(7, 9),
                )
                self.assertTrue(report["passed"], report)
                self.assertEqual(report["max_abs_error"], 0.0)
                self.assertEqual(report["output_shape"], [23, 29])
                self.assertFalse(report["native_runtime"])

    def test_flow_maps_reject_unsupported_contracts(self):
        flow = np.zeros((3, 5, 2), dtype=np.float32)
        with self.assertRaises(ValueError):
            verify_flow_maps_parity((flow,), output_shape=(1, 9), block_size=3)
        with self.assertRaises(TypeError):
            verify_flow_maps_parity(
                (flow.astype(np.int16),), output_shape=(9, 11), block_size=3
            )

    def test_normalize_image_spatial_parity_and_channel_expansion(self):
        rng = np.random.default_rng(7)
        gray = rng.integers(0, 65536, size=(23, 29), dtype=np.uint16)
        adapter = registered_block_adapters()["normalize_image"]
        self.assertEqual(
            adapter.metadata["output_shape_policy"],
            "same_spatial_expand_gray_to_rgb",
        )
        self.assertEqual(
            adapter.metadata["output_channel_policy"]["grayscale"],
            "expand_to_3",
        )
        self.assertEqual(adapter.metadata["output_dtype"], "float32")
        report = verify_normalize_image_parity(
            gray, dtype=np.uint16, block_size=(7, 9)
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["output_shape"], [23, 29, 3])
        self.assertEqual(report["max_abs_error"], 0.0)

        # Signed integer and half-precision declarations use the same bridge
        # policy as the public normalizer: integer domains scale by their
        # declared maximum, floating domains are already normalized.  A
        # strided view ensures the tiled reader does not depend on contiguous
        # source storage.
        signed = np.arange(-1200, 1200, dtype=np.int16).reshape(40, 60)[::2, 1::3]
        signed_report = verify_normalize_image_parity(
            signed, dtype=np.int16, block_size=(5, 7)
        )
        self.assertTrue(signed_report["passed"], signed_report)
        self.assertEqual(signed_report["max_abs_error"], 0.0)
        self.assertEqual(signed_report["output_shape"], [20, 20, 3])

        half = rng.random((21, 25), dtype=np.float32).astype(np.float16)
        half_report = verify_normalize_image_parity(
            half, dtype=np.float16, block_size=(6, 8)
        )
        self.assertTrue(half_report["passed"], half_report)
        self.assertEqual(half_report["max_abs_error"], 0.0)
        self.assertEqual(half_report["output_shape"], [21, 25, 3])

        rgb = rng.random((23, 29, 3), dtype=np.float32)
        report = verify_normalize_image_parity(
            rgb, dtype=np.float32, block_size=(7, 9)
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["output_shape"], [23, 29, 3])
        self.assertEqual(report["max_abs_error"], 0.0)

    def test_brief_pattern_deterministic_non_multiple_output_domain(self):
        params = {"num_pairs": 263, "patch_size": 31, "seed": 42}
        first = run_output_domain_tiled(
            "generate_brief_pattern", params=params, block_size=(37, 3)
        )
        second = run_output_domain_tiled(
            "generate_brief_pattern", params=params, block_size=(37, 3)
        )
        self.assertEqual(first.shape, (263, 4))
        np.testing.assert_array_equal(first, second)
        self.assertTrue(np.isfinite(first).all())

    def test_resize_coordinate_contract_non_multiple_output_is_read_only(self):
        source = np.arange(7 * 11, dtype=np.float32).reshape(7, 11) / np.float32(77.0)
        report = verify_coordinate_parity(
            "resize", (source,), output_shape=(13, 17),
            params={"interpolation": 1}, block_size=(5, 7), atol=0.0, rtol=0.0,
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["full_shape"], [[13, 17]])
        self.assertEqual(report["tiled_shape"], [[13, 17]])
        self.assertEqual(report["max_abs_error"], 0.0)
        self.assertFalse(report["native_runtime"])


if __name__ == "__main__":
    unittest.main()
