"""Parser/selection tests for the bounded native partition probe."""

from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition import (
    ALL_OPERATIONS,
    BASE_OPERATIONS,
    GLOBAL_DIAGNOSTIC_OPERATIONS,
    OPTIONAL_OPERATIONS,
    _parse_operations,
    _cuda_device_name,
    _operation_record,
    _validate_runtime_selection,
)

import numpy as np


class ProbeOperationSelectionTests(unittest.TestCase):
    def test_tuple_probe_contract_reports_arity_shapes_and_dtypes(self):
        """Native probe JSON must expose split output contract explicitly."""

        values = tuple(np.zeros((19, 23), dtype=np.uint8) for _ in range(3))
        record = _operation_record(
            "split_3ch",
            values,
            values,
            full_telemetry={},
            block_telemetry={"operation": "split_3ch", "status": "ok"},
            full_plan={},
            block_plan={"operation": "split_3ch", "selected": True},
        )
        self.assertTrue(record["passed"], record)
        self.assertTrue(record["correctness_passed"])
        self.assertEqual(record["output_arity"], 3)
        self.assertEqual(record["expected_output_arity"], 3)
        self.assertEqual(record["output_shapes"], [[19, 23]] * 3)
        self.assertEqual(record["expected_output_shapes"], [[19, 23]] * 3)
        self.assertEqual(record["output_dtypes"], ["uint8"] * 3)
        self.assertEqual(record["expected_output_dtypes"], ["uint8"] * 3)

    def test_failed_tuple_block_keeps_expected_contract_without_claiming_output(self):
        """A failed block call must not fabricate native output telemetry."""

        values = tuple(np.zeros((19, 23), dtype=np.uint8) for _ in range(3))
        record = _operation_record(
            "split_3ch",
            values,
            None,
            full_telemetry={},
            block_telemetry={},
            full_plan={},
            block_plan={},
            error="split block unavailable",
            phase="block",
        )
        self.assertFalse(record["passed"])
        self.assertFalse(record["correctness_passed"])
        self.assertEqual(record["expected_output_arity"], 3)
        self.assertNotIn("output_arity", record)
        self.assertNotIn("output_shapes", record)
        self.assertNotIn("output_dtypes", record)

    def test_dtype_mismatch_cannot_be_promoted_even_when_values_match(self):
        """ABI dtype drift must fail the native partition qualification gate."""

        full = np.zeros((19, 23), dtype=np.float32)
        tiled = np.zeros((19, 23), dtype=np.float64)
        record = _operation_record(
            "copy",
            full,
            tiled,
            full_telemetry={},
            block_telemetry={"operation": "copy", "status": "ok"},
            full_plan={},
            block_plan={"operation": "copy", "selected": True},
        )
        self.assertFalse(record["passed"])
        self.assertFalse(record["correctness_passed"])
        self.assertFalse(record["output_contract_match"])
        self.assertFalse(record["output_dtypes_match"])
        self.assertIn("dtype", record["reason"])

    def test_shape_mismatch_cannot_be_promoted_even_when_prefix_matches(self):
        full = np.zeros((19, 23), dtype=np.float32)
        tiled = np.zeros((19, 22), dtype=np.float32)
        record = _operation_record(
            "copy",
            full,
            tiled,
            full_telemetry={},
            block_telemetry={"operation": "copy", "status": "ok"},
            full_plan={},
            block_plan={"operation": "copy", "selected": True},
        )
        self.assertFalse(record["passed"])
        self.assertFalse(record["output_contract_match"])
        self.assertFalse(record["output_shapes_match"])

    def test_full_frame_fallback_separates_correctness_from_block_support(self):
        values = np.zeros((19, 23), dtype=np.float32)
        record = _operation_record(
            "copy",
            values,
            values,
            full_telemetry={},
            block_telemetry={},
            full_plan={},
            block_plan={"operation": "copy", "selected": False},
        )
        self.assertTrue(record["correctness_passed"])
        self.assertFalse(record["passed"])
        self.assertEqual(record["fallback"], "full_frame")
    def test_default_and_base_selection_preserve_legacy_scope(self):
        self.assertEqual(_parse_operations(None), BASE_OPERATIONS)
        self.assertEqual(_parse_operations("base"), BASE_OPERATIONS)
        self.assertEqual(_parse_operations("default"), BASE_OPERATIONS)

    def test_all_selection_includes_only_declared_optional_operations(self):
        selected = _parse_operations("all")
        self.assertEqual(selected, ALL_OPERATIONS)
        optional_start = len(BASE_OPERATIONS)
        optional_end = optional_start + len(OPTIONAL_OPERATIONS)
        self.assertEqual(selected[optional_start:optional_end], OPTIONAL_OPERATIONS)
        self.assertEqual(selected[optional_end:], GLOBAL_DIAGNOSTIC_OPERATIONS)

    def test_explicit_selection_deduplicates_without_reordering(self):
        self.assertEqual(
            _parse_operations("sobel, box_filter, sobel"),
            ("sobel", "box_filter"),
        )

    def test_unknown_operation_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "unknown probe operation"):
            _parse_operations("copy,not_a_real_operation")

    def test_global_operation_is_explicit_diagnostic_only(self):
        self.assertEqual(_parse_operations("otsu_threshold"), GLOBAL_DIAGNOSTIC_OPERATIONS)

    def test_runtime_selection_accepts_matching_backend_and_device(self):
        _validate_runtime_selection(
            SimpleNamespace(arch="vulkan", device_id=0), "vulkan", 0
        )

    def test_runtime_selection_fails_closed_on_backend_mismatch(self):
        with self.assertRaisesRegex(RuntimeError, "backend mismatch"):
            _validate_runtime_selection(
                SimpleNamespace(arch="opengl", device_id=0), "vulkan", 0
            )

    def test_cuda_device_name_uses_driver_identity(self):
        completed = SimpleNamespace(returncode=0, stdout="NVIDIA GeForce MX150\n")
        with patch(
            "taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition.subprocess.run",
            return_value=completed,
        ) as run:
            self.assertEqual(_cuda_device_name(0), "NVIDIA GeForce MX150")
        self.assertEqual(run.call_args.args[0][0], "nvidia-smi")

    def test_cuda_device_name_fails_closed_when_driver_query_fails(self):
        completed = SimpleNamespace(returncode=1, stdout="")
        with patch(
            "taichi_vision.taichi_algorithm.aot_py.tools.probe_native_partition.subprocess.run",
            return_value=completed,
        ):
            self.assertEqual(_cuda_device_name(0), "")

    def test_extended_local_selection_is_explicit_and_ordered(self):
        extended = (
            "morphology,filter2d,threshold,normalize,"
            "joint_bilateral_guidance,enhance_image,joint_bilateral_filter,"
            "guided_filter,non_local_means"
        )
        self.assertEqual(_parse_operations(extended), tuple(OPTIONAL_OPERATIONS[7:]))


if __name__ == "__main__":
    unittest.main()
