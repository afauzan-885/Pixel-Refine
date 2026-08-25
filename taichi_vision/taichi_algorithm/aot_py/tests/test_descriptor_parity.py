"""Bounded semantic parity for fixed-capacity binary descriptor matching."""

from __future__ import annotations

import unittest

import numpy as np

from taichi_vision.taichi_aot.descriptor_parity import (
    cross_check_binary_descriptors_reference,
    match_binary_descriptors_reference,
    ratio_cross_check_binary_descriptors_reference,
    ratio_test_binary_descriptors_reference,
    verify_binary_descriptor_partition_parity,
    verify_binary_descriptor_matching_partition_parity,
)


class BinaryDescriptorParityTests(unittest.TestCase):
    def test_query_partition_matches_full_reference_and_is_deterministic(self):
        query = np.arange(17 * 8, dtype=np.uint8).reshape(17, 8)
        train = np.roll(query[:9], 1, axis=1).copy()
        report = verify_binary_descriptor_partition_parity(
            query, train, block_rows=5
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0)
        self.assertTrue(report["deterministic_merge"])
        self.assertFalse(report["native_runtime"])
        self.assertFalse(report["automatic_safe"])
        self.assertEqual(report["qualification"], "candidate_only")

    def test_ties_keep_row_major_first_train_descriptor(self):
        query = np.zeros((3, 4), dtype=np.uint8)
        train = np.zeros((2, 4), dtype=np.uint8)
        result = match_binary_descriptors_reference(query, train, block_rows=1)
        np.testing.assert_array_equal(result, np.zeros(3, dtype=np.int32))

    def test_invalid_shape_dtype_and_width_are_rejected(self):
        with self.assertRaises(TypeError):
            match_binary_descriptors_reference(np.zeros((2, 4), np.float32), np.zeros((2, 4), np.uint8))
        with self.assertRaises(ValueError):
            match_binary_descriptors_reference(np.zeros((2, 4), np.uint8), np.zeros((2, 5), np.uint8))
        with self.assertRaises(ValueError):
            match_binary_descriptors_reference(np.zeros((2, 4), np.uint8), np.zeros((2, 4), np.uint8), block_rows=0)

    def test_ratio_and_cross_check_have_exact_partition_parity(self):
        rng = np.random.default_rng(19)
        query = rng.integers(0, 256, size=(23, 8), dtype=np.uint8)
        train = rng.integers(0, 256, size=(17, 8), dtype=np.uint8)
        report = verify_binary_descriptor_matching_partition_parity(
            query, train, ratio_threshold=0.9, block_rows=4
        )
        self.assertTrue(report["passed"], report)
        self.assertEqual(report["max_abs_error"], 0)
        self.assertFalse(report["native_runtime"])
        self.assertFalse(report["automatic_safe"])
        self.assertEqual(report["qualification"], "candidate_only")

    def test_ratio_rejection_is_fixed_capacity_and_cross_check_is_mutual(self):
        query = np.array([[0, 0], [255, 255], [15, 15]], dtype=np.uint8)
        train = np.array([[0, 0], [0, 0], [255, 255]], dtype=np.uint8)
        ratio = ratio_test_binary_descriptors_reference(
            query, train, ratio_threshold=0.8, block_rows=1
        )
        self.assertEqual(ratio["indices"].shape, (3,))
        self.assertEqual(ratio["accepted"].dtype, np.bool_)
        np.testing.assert_array_equal(ratio["indices"], np.array([-1, 2, -1], np.int32))
        cross = cross_check_binary_descriptors_reference(query, train, block_rows=2)
        combined = ratio_cross_check_binary_descriptors_reference(
            query, train, ratio_threshold=0.8, block_rows=2
        )
        self.assertEqual(cross.shape, (3,))
        self.assertEqual(combined.shape, (3,))

    def test_ratio_requires_two_train_rows_and_valid_threshold(self):
        query = np.zeros((1, 4), dtype=np.uint8)
        with self.assertRaises(ValueError):
            ratio_test_binary_descriptors_reference(query, np.zeros((1, 4), np.uint8))
        with self.assertRaises(ValueError):
            ratio_test_binary_descriptors_reference(query, np.zeros((2, 4), np.uint8), ratio_threshold=1.0)


if __name__ == "__main__":
    unittest.main()
