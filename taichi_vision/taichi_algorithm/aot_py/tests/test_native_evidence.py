"""Tests for device-scoped native partition evidence."""

from __future__ import annotations

import unittest

from taichi_vision.taichi_aot.block import (
    block_coverage_report,
    can_auto_block,
    can_auto_partition_dispatch,
)
from taichi_vision.taichi_aot.native_evidence import (
    NativePartitionEvidence,
    clear_native_partition_evidence,
    lookup_native_partition_evidence,
    native_partition_evidence_report,
    native_partition_evidence_snapshot,
    native_partition_evidence_supported,
    native_partition_promotion_report,
    native_partition_promotion_matrix_report,
    register_native_partition_evidence,
    register_probe_result,
    register_verified_native_partition_evidence,
    register_verified_native_stencil_evidence,
    register_verified_native_local_stencil_evidence,
    register_verified_native_vulkan_intel_local_stencil_evidence,
    register_verified_native_vulkan_intel_base_evidence,
    register_verified_native_vulkan_nvidia_resize_evidence,
    register_verified_native_vulkan_intel_resize_evidence,
    register_verified_native_cuda_resize_evidence,
    register_verified_native_cuda_partition_evidence,
    register_verified_native_opengl_partition_evidence,
    register_verified_native_opengl_intel_evidence,
)
from taichi_vision.taichi_aot.block_adapters import register_low_risk_block_adapters


class NativeEvidenceTests(unittest.TestCase):
    def setUp(self):
        clear_native_partition_evidence()

    def tearDown(self):
        clear_native_partition_evidence()

    def test_malformed_identity_is_rejected_without_registry_mutation(self):
        before = native_partition_evidence_snapshot()
        for fields in (
            {"backend": "cpu", "device": "gpu", "command": "probe"},
            {"operation": "copy", "device": "gpu", "command": "probe"},
            {"operation": "copy", "backend": "cpu", "command": "probe"},
        ):
            with self.assertRaises(ValueError):
                register_native_partition_evidence(**fields)
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_invalid_error_magnitude_is_rejected_fail_closed(self):
        before = native_partition_evidence_snapshot()
        for value in (-1.0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                register_native_partition_evidence(
                    operation="copy",
                    backend="cuda",
                    device="NVIDIA test",
                    command="probe",
                    max_abs_error=value,
                )
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_malformed_passed_metadata_cannot_qualify_evidence(self):
        """JSON-like status values are normalized; ambiguous values reject."""

        for value, expected in ((True, True), (False, False), (1, True), (0, False),
                                ("true", True), ("false", False), ("1", True), ("0", False)):
            record = NativePartitionEvidence(
                operation="copy",
                backend="cuda",
                device="NVIDIA test",
                command="probe",
                passed=value,
                block_size=8,
            )
            self.assertEqual(record.passed, expected, value)
        for value in ("falsey", "", 2, -1, object()):
            with self.assertRaises(ValueError):
                NativePartitionEvidence(
                    operation="copy",
                    backend="cuda",
                    device="NVIDIA test",
                    command="probe",
                    passed=value,
                    block_size=8,
                )

    def test_invalid_device_ordinal_is_rejected_fail_closed(self):
        """An evidence ordinal must not be silently coerced from bad data."""

        before = native_partition_evidence_snapshot()
        for value in (True, False, -1, -1.0, 1.5, float("nan"), float("inf"), "1.5", ""):
            with self.assertRaises(ValueError):
                register_native_partition_evidence(
                    operation="copy",
                    backend="cuda",
                    device="NVIDIA test",
                    command="probe",
                    device_id=value,
                )
            self.assertEqual(native_partition_evidence_snapshot(), before)

        record = register_native_partition_evidence(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            device_id="0",
        )
        self.assertEqual(record.device_id, 0)

    def test_non_integral_block_size_cannot_qualify_partition_promotion(self):
        # ``int()`` truncation and bool-as-int must not let malformed probe
        # metadata pass the native partition gate.
        for block_size in (True, 8.5, float("nan"), float("inf"), "8.5"):
            record = NativePartitionEvidence(
                operation="copy",
                backend="cuda",
                device="NVIDIA test",
                command="probe",
                block_size=block_size,
            )
            self.assertFalse(record.partition_qualified, block_size)
        for block_size in (8, 8.0, "8"):
            record = NativePartitionEvidence(
                operation="copy",
                backend="cuda",
                device="NVIDIA test",
                command="probe",
                block_size=block_size,
            )
            self.assertTrue(record.partition_qualified, block_size)

    def test_target_identity_metadata_is_preserved_and_reported(self):
        record = register_native_partition_evidence(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            target_id="cuda_x86_64_windows_nvidia",
            architecture="sm_5.0",
            driver_version="555.99",
            vendor="NVIDIA",
            block_size=8,
        )
        self.assertTrue(record.identity_complete)
        payload = record.as_dict()
        self.assertEqual(payload["target_id"], "cuda_x86_64_windows_nvidia")
        self.assertEqual(payload["architecture"], "sm_5.0")
        report = native_partition_evidence_report("cuda", "NVIDIA test")
        self.assertEqual(report["identity_complete_count"], 1)
        self.assertEqual(report["identity_complete_percent"], 100.0)

    def test_legacy_name_only_evidence_remains_compatible_but_not_complete(self):
        record = register_native_partition_evidence(
            operation="copy",
            backend="cpu",
            device="CPU test",
            command="probe",
            block_size=8,
        )
        self.assertFalse(record.identity_complete)
        self.assertTrue(record.partition_qualified)
        report = native_partition_evidence_report("cpu", "CPU test")
        self.assertEqual(report["identity_complete_count"], 0)

    def test_exact_device_promotion_review_requires_complete_identity(self):
        register_native_partition_evidence(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            block_size=8,
        )
        report = native_partition_promotion_report(
            "cuda", "NVIDIA test", "copy"
        )
        self.assertFalse(report["promotion_eligible"])
        self.assertEqual(report["status"], "fail_closed")
        self.assertIn("target identity metadata is incomplete", report["reasons"])
        self.assertFalse(report["dispatch_promotion"])

    def test_exact_device_promotion_review_accepts_matching_target_identity(self):
        common = dict(
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            block_size=8,
            target_id="cuda_x86_64_windows_nvidia",
            architecture="sm_6.1",
            driver_version="555.99",
            vendor="NVIDIA Corporation",
        )
        register_native_partition_evidence(operation="copy", **common)
        register_native_partition_evidence(operation="absdiff", **common)
        report = native_partition_promotion_report(
            "cuda", "NVIDIA test", ("copy", "absdiff"),
            target_id="cuda_x86_64_windows_nvidia",
        )
        self.assertTrue(report["promotion_eligible"])
        self.assertEqual(report["status"], "promotion_eligible")
        self.assertEqual(report["accepted_operations"], ("copy", "absdiff"))
        self.assertFalse(report["automatic_safe"])
        self.assertFalse(report["dispatch_promotion"])
        self.assertFalse(report["registry_mutated"])

    def test_promotion_matrix_is_deterministic_and_partitioned_by_device(self):
        common = dict(
            command="probe",
            block_size=8,
            target_id="cuda_x86_64_windows_nvidia",
            architecture="sm_6.1",
            driver_version="555.99",
            vendor="NVIDIA Corporation",
        )
        register_native_partition_evidence(
            operation="copy", backend="cuda", device="NVIDIA test", **common
        )
        register_native_partition_evidence(
            operation="absdiff", backend="cuda", device="NVIDIA test", **common
        )
        register_native_partition_evidence(
            operation="copy",
            backend="opengl",
            device="Intel test",
            command="probe",
            block_size=8,
            target_id="opengl_x86_64_windows_intel",
            architecture="gen9",
            driver_version="31.0",
            vendor="Intel Corporation",
        )
        first = native_partition_promotion_matrix_report(
            ("copy", "absdiff"),
            target_id_by_scope={
                ("cuda", "NVIDIA test"): "cuda_x86_64_windows_nvidia",
                ("opengl", "Intel test"): "opengl_x86_64_windows_intel",
            },
        )
        second = native_partition_promotion_matrix_report(
            ("copy", "absdiff"),
            target_id_by_scope={
                ("cuda", "NVIDIA test"): "cuda_x86_64_windows_nvidia",
                ("opengl", "Intel test"): "opengl_x86_64_windows_intel",
            },
        )
        self.assertEqual(first, second)
        self.assertEqual(
            first["eligible_scopes"], (("cuda", "NVIDIA test"),)
        )
        self.assertEqual(
            first["rejected_scopes"], (("opengl", "Intel test"),)
        )
        self.assertEqual(first["backend_summary"]["cuda"]["eligible_scope_count"], 1)
        rejected = first["reports"][1]
        self.assertEqual(rejected["missing_operations"], ("absdiff",))
        self.assertIn("missing exact-device evidence: absdiff", rejected["reasons"])
        self.assertFalse(first["dispatch_promotion"])
        self.assertFalse(first["registry_mutated"])

    def test_empty_promotion_matrix_is_explicitly_fail_closed(self):
        report = native_partition_promotion_matrix_report(("copy",))
        self.assertEqual(report["scope_count"], 0)
        self.assertEqual(report["status"], "fail_closed")
        self.assertTrue(report["fail_closed"])
        self.assertFalse(report["dispatch_promotion"])
        self.assertFalse(report["registry_mutated"])

    def test_exact_device_promotion_rejects_vendor_or_target_mismatch(self):
        register_native_partition_evidence(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            block_size=8,
            target_id="cuda_x86_64_windows_nvidia",
            architecture="sm_6.1",
            driver_version="555.99",
            vendor="Intel Corporation",
        )
        report = native_partition_promotion_report(
            "cuda", "NVIDIA test", "copy",
            target_id="cuda_x86_64_windows_nvidia",
        )
        self.assertFalse(report["promotion_eligible"])
        self.assertTrue(any("vendor mismatch" in reason for reason in report["reasons"]))

    def test_single_interpolation_name_is_not_split_into_characters(self):
        record = register_native_partition_evidence(
            operation="resize",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
            interpolations="linear",
            block_size=16,
        )
        self.assertEqual(record.interpolations, ("linear",))
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA test", interpolation="linear"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA test", interpolation="nearest"
            )
        )

    def test_duplicate_identity_fails_closed_when_replace_disabled(self):
        fields = dict(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="probe",
        )
        register_native_partition_evidence(**fields)
        before = native_partition_evidence_snapshot()
        with self.assertRaises(KeyError):
            register_native_partition_evidence(**fields, replace=False)
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_records_are_exactly_scoped_and_do_not_promote_flags(self):
        before = can_auto_block("copy", "cpu")
        register_verified_native_partition_evidence()
        cpu = native_partition_evidence_report("cpu")
        vk = native_partition_evidence_report("vulkan", "NVIDIA GeForce MX150")
        self.assertEqual(cpu["record_count"], 8)
        self.assertEqual(cpu["qualified_count"], 8)
        self.assertEqual(vk["record_count"], 8)
        self.assertEqual(vk["qualified_count"], 8)
        self.assertEqual(native_partition_evidence_report("opengl")["record_count"], 0)
        self.assertEqual(
            native_partition_evidence_report("vulkan", "Intel(R) UHD Graphics 620")[
                "record_count"
            ],
            0,
        )
        self.assertEqual(len(lookup_native_partition_evidence("copy", "vulkan")), 1)
        self.assertTrue(
            native_partition_evidence_supported(
                "copy", "vulkan", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "copy", "vulkan", "Intel(R) UHD Graphics 620"
            )
        )
        self.assertTrue(before == can_auto_block("copy", "cpu"))
        register_low_risk_block_adapters()
        self.assertTrue(
            can_auto_partition_dispatch(
                "copy",
                "cpu",
                require_native_evidence=True,
            )
        )
        self.assertFalse(
            can_auto_partition_dispatch(
                "copy", "opengl", require_native_evidence=True
            )
        )

    def test_mapping_and_probe_json_registration(self):
        record = register_native_partition_evidence(
            {
                "operation": "copy",
                "backend": "cpu",
                "device": "test-cpu",
                "device_id": 0,
                "command": "python probe.py",
                "passed": True,
                "max_abs_error": 0.0,
                "block_size": 16,
            }
        )
        self.assertIsInstance(record, NativePartitionEvidence)
        self.assertTrue(record.qualified)
        result = {
            "backend": "vulkan",
            "device_name": "NVIDIA test",
            "device_id": 3,
            "target_id": "vulkan_x86_64_windows_nvidia",
            "architecture": "sm_5.0",
            "driver_version": "555.99",
            "vendor": "NVIDIA",
            "block_size": 8,
            "operations": {
                "copy": {
                    "passed": True,
                    "max_abs_error": 0.0,
                    "block_selected": True,
                    "shape": [[4, 4]],
                    "dtype": ["float32"],
                },
                "absdiff": {
                    "passed": False,
                    "max_abs_error": 1.0,
                    "block_selected": False,
                },
                "smooth_flow_gpu": {
                    "passed": True,
                    "max_abs_error": 0.0,
                    "block_selected": True,
                },
            },
        }
        register_probe_result(result, command="python probe.py")
        report = native_partition_evidence_report("vulkan", "NVIDIA test")
        self.assertEqual(report["record_count"], 2)
        self.assertEqual(report["qualified_count"], 2)
        self.assertEqual(report["qualified_operations"], ("copy", "smooth_flow"))
        self.assertEqual(report["identity_complete_count"], 2)

    def test_probe_schema_rejects_non_mapping_before_registry_mutation(self):
        """Malformed top-level telemetry must fail as a schema error."""

        before = native_partition_evidence_snapshot()
        for payload in (None, [], ("backend", "cuda"), "not-json-object"):
            with self.assertRaises(ValueError):
                register_probe_result(payload, command="python probe.py")
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_probe_status_strings_are_decoded_without_truthiness_or_partial_mutation(self):
        """Malformed JSON flags cannot qualify or partially register a probe."""

        result = {
            "backend": "cuda",
            "device_name": "NVIDIA test",
            "block_size": 8,
            "operations": {
                "copy": {
                    "passed": "false",
                    "block_selected": "true",
                    "max_abs_error": 1.0,
                },
                "absdiff": {
                    "passed": "true",
                    "block_selected": "false",
                },
            },
        }
        register_probe_result(result, command="probe")
        report = native_partition_evidence_report("cuda", "NVIDIA test")
        self.assertEqual(report["record_count"], 1)
        self.assertEqual(report["records"][0]["operation"], "copy")
        self.assertFalse(report["records"][0]["passed"])
        self.assertFalse(report["records"][0]["qualified"])

        before = native_partition_evidence_snapshot()
        malformed = dict(result)
        malformed["operations"] = {
            "copy": {"passed": "definitely-not-a-boolean", "block_selected": True}
        }
        with self.assertRaisesRegex(ValueError, "passed must be a boolean"):
            register_probe_result(malformed, command="probe")
        self.assertEqual(native_partition_evidence_snapshot(), before)

    def test_probe_backend_identity_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            register_probe_result(
                {
                    "backend": "cuda",
                    "runtime_backend": "vulkan",
                    "device_name": "NVIDIA test",
                    "operations": {},
                },
                command="probe",
            )

    def test_probe_operations_and_details_must_be_mappings(self):
        """Malformed JSON containers fail before registry mutation."""

        with self.assertRaisesRegex(ValueError, "operations must be a mapping"):
            register_probe_result(
                {
                    "backend": "cuda",
                    "device_name": "NVIDIA test",
                    "operations": ["copy"],
                },
                command="probe",
            )
        with self.assertRaisesRegex(ValueError, "details must be a mapping"):
            register_probe_result(
                {
                    "backend": "cuda",
                    "device_name": "NVIDIA test",
                    "operations": {"copy": [True]},
                },
                command="probe",
            )
        self.assertEqual(native_partition_evidence_snapshot(), {})

    def test_probe_metrics_are_staged_before_registry_mutation(self):
        """A malformed later metric must not leave an earlier record behind."""

        payload = {
            "backend": "cuda",
            "device_name": "NVIDIA test",
            "block_size": 8,
            "operations": {
                "copy": {"passed": True, "max_abs_error": 0.0},
                "absdiff": {"passed": True, "max_abs_error": "not-a-number"},
            },
        }
        with self.assertRaisesRegex(ValueError, "max_abs_error must be finite"):
            register_probe_result(payload, command="probe")
        self.assertEqual(native_partition_evidence_snapshot(), {})

    def test_probe_string_interpolation_is_one_name_not_character_tuple(self):
        payload = {
            "backend": "cuda",
            "device_name": "NVIDIA test",
            "block_size": 8,
            "operations": {
                "resize": {
                    "passed": True,
                    "max_abs_error": 0.0,
                    "interpolations": "linear",
                }
            },
        }
        records = register_probe_result(payload, command="probe")
        self.assertEqual(records[0].interpolations, ("linear",))

    def test_probe_target_id_backend_mismatch_is_rejected(self):
        with self.assertRaises(ValueError):
            register_probe_result(
                {
                    "backend": "cuda",
                    "target_id": "vulkan_x86_64_windows_nvidia",
                    "device_name": "NVIDIA test",
                    "operations": {},
                },
                command="probe",
            )

    def test_probe_vendor_qualified_target_requires_matching_runtime_vendor(self):
        payload = {
            "backend": "vulkan",
            "target_id": "vulkan_x86_64_windows_nvidia",
            "device_name": "NVIDIA test",
            "vendor": "Intel Corporation",
            "operations": {},
        }
        with self.assertRaisesRegex(ValueError, "target vendor mismatch"):
            register_probe_result(payload, command="probe")

    def test_probe_vendor_aliases_match_target_and_generic_arm_target_stays_open(self):
        nvidia = {
            "backend": "vulkan",
            "target_id": "vulkan_x86_64_windows_nvidia",
            "device_name": "NVIDIA test",
            "vendor": "NVIDIA Corporation",
            "operations": {},
        }
        self.assertEqual(register_probe_result(nvidia, command="probe"), ())

        nvidia_product = dict(nvidia, vendor="NVIDIA GeForce MX150")
        self.assertEqual(register_probe_result(nvidia_product, command="probe"), ())

        arm = {
            "backend": "vulkan",
            "target_id": "vulkan_arm64_android",
            "device_name": "Adreno test",
            # A generic ARM target does not assert a GPU vendor.  The exact
            # runtime device name is still retained in each evidence record.
            "operations": {},
        }
        self.assertEqual(register_probe_result(arm, command="probe"), ())

    def test_report_distinguishes_native_status_from_semantic_records(self):
        register_native_partition_evidence(
            operation="copy",
            backend="cpu",
            device="semantic-only",
            command="python semantic_probe.py",
            scope="semantic_cpu",
        )
        report = native_partition_evidence_report("cpu", "semantic-only")
        self.assertEqual(report["qualified_count"], 1)
        self.assertEqual(report["native_record_count"], 0)
        self.assertEqual(report["native_qualified_count"], 0)
        self.assertEqual(report["native_status"], "unverified")

        register_native_partition_evidence(
            operation="copy",
            backend="cpu",
            device="native-partial",
            command="python native_probe.py",
            max_abs_error=0.0,
        )
        register_native_partition_evidence(
            operation="absdiff",
            backend="cpu",
            device="native-partial",
            command="python native_probe.py",
            passed=False,
            max_abs_error=1.0,
        )
        report = native_partition_evidence_report("cpu", "native-partial")
        self.assertEqual(report["native_record_count"], 2)
        self.assertEqual(report["native_qualified_count"], 1)
        self.assertEqual(report["native_failed_count"], 1)
        self.assertEqual(report["native_coverage_percent"], 50.0)
        self.assertEqual(report["native_status"], "partial")

    def test_native_promotion_requires_canonical_partition_scope_and_block_size(self):
        # A native-looking diagnostic scope is still insufficient for the
        # strict partition gate.  This protects automatic promotion from
        # semantic/native pipeline records that happen to share the prefix.
        register_native_partition_evidence(
            operation="copy",
            backend="cuda",
            device="NVIDIA test",
            command="python probe.py",
            scope="native_semantic_only",
            block_size=16,
        )
        self.assertFalse(
            native_partition_evidence_supported("copy", "cuda", "NVIDIA test")
        )
        report = native_partition_evidence_report("cuda", "NVIDIA test")
        self.assertEqual(report["native_qualified_count"], 1)
        self.assertEqual(report["native_partition_qualified_count"], 0)
        self.assertEqual(report["native_partition_status"], "partial")

        register_native_partition_evidence(
            operation="absdiff",
            backend="cuda",
            device="NVIDIA test",
            command="python probe.py",
            scope="native_full_frame_vs_block",
        )
        self.assertFalse(
            native_partition_evidence_supported("absdiff", "cuda", "NVIDIA test")
        )

        register_native_partition_evidence(
            operation="rgb2gray",
            backend="cuda",
            device="NVIDIA test",
            command="python probe.py",
            scope="native_full_frame_vs_block",
            block_size=16,
        )
        self.assertTrue(
            native_partition_evidence_supported("rgb2gray", "cuda", "NVIDIA test")
        )

    def test_coverage_report_separates_native_records_from_contract_flags(self):
        # The evidence registry is intentionally diagnostic: it must be
        # visible in the audit without changing the maintained AUTO flags.
        register_verified_native_partition_evidence()
        report = block_coverage_report("vulkan")
        self.assertEqual(report["native_evidence_qualified_operations"], 8)
        self.assertEqual(report["native_evidence_qualified_percent"], 7.3394)
        scoped = block_coverage_report("vulkan", "NVIDIA GeForce MX150")
        self.assertEqual(scoped["native_evidence_qualified_operations"], 8)
        self.assertEqual(scoped["device"], "NVIDIA GeForce MX150")
        self.assertEqual(report["strict_auto_safe"], 48)

    def test_optional_stencil_records_are_exact_target_scoped_and_canonical(self):
        records = register_verified_native_stencil_evidence()
        self.assertEqual(len(records), 14)
        cpu = native_partition_evidence_report("cpu")
        vk = native_partition_evidence_report("vulkan", "NVIDIA GeForce MX150")
        self.assertEqual(cpu["record_count"], 7)
        self.assertEqual(cpu["qualified_count"], 7)
        self.assertEqual(vk["record_count"], 7)
        self.assertEqual(vk["qualified_count"], 7)
        self.assertIn("smooth_flow", vk["qualified_operations"])
        self.assertNotIn("smooth_flow_gpu", vk["qualified_operations"])
        self.assertEqual(
            native_partition_evidence_report("opengl")["record_count"], 0
        )
        coverage = block_coverage_report("vulkan")
        self.assertEqual(coverage["native_evidence_qualified_operations"], 7)
        self.assertEqual(coverage["native_partition_dispatch_safe"], 7)
        self.assertIn("smooth_flow", coverage["native_evidence_qualified_operation_names"])
        # The maintained legacy stencil executor is itself the adapter once
        # the exact native probe has passed; no semantic NumPy adapter is
        # required to qualify this opt-in diagnostic gate.
        self.assertTrue(
            can_auto_partition_dispatch(
                "box_filter",
                "vulkan",
                require_native_evidence=True,
                device="NVIDIA GeForce MX150",
            )
        )
        self.assertFalse(
            can_auto_partition_dispatch(
                "box_filter",
                "opengl",
                require_native_evidence=True,
                device="NVIDIA GeForce MX150",
            )
        )
        # Evidence is diagnostic only and cannot alter strict AUTO flags.
        self.assertEqual(coverage["strict_auto_safe"], 48)

    def test_extended_local_stencil_records_are_exact_cpu_and_vulkan_targets(self):
        records = register_verified_native_local_stencil_evidence()
        self.assertEqual(len(records), 18)
        cpu = native_partition_evidence_report("cpu", "CPU (x86_64 Windows)")
        self.assertEqual(cpu["record_count"], 9)
        self.assertEqual(cpu["qualified_count"], 9)
        vk = native_partition_evidence_report("vulkan", "NVIDIA GeForce MX150")
        self.assertEqual(vk["record_count"], 9)
        self.assertEqual(vk["qualified_count"], 9)
        for operation in (
            "morphology",
            "filter2d",
            "threshold",
            "normalize",
            "joint_bilateral_guidance",
            "enhance_image",
            "joint_bilateral_filter",
            "guided_filter",
            "non_local_means",
        ):
            self.assertTrue(
                can_auto_partition_dispatch(
                    operation,
                    "cpu",
                    require_native_evidence=True,
                    device="CPU (x86_64 Windows)",
                )
            )
        coverage = block_coverage_report("cpu", "CPU (x86_64 Windows)")
        self.assertEqual(coverage["native_evidence_qualified_operations"], 9)
        self.assertEqual(coverage["native_partition_dispatch_safe"], 9)
        self.assertEqual(coverage["strict_auto_safe"], 48)
        vk_coverage = block_coverage_report("vulkan", "NVIDIA GeForce MX150")
        self.assertEqual(vk_coverage["native_evidence_qualified_operations"], 9)
        self.assertEqual(vk_coverage["native_partition_dispatch_safe"], 9)
        self.assertTrue(
            can_auto_partition_dispatch(
                "guided_filter",
                "vulkan",
                require_native_evidence=True,
                device="NVIDIA GeForce MX150",
            )
        )
        self.assertFalse(
            can_auto_partition_dispatch(
                "guided_filter",
                "opengl",
                require_native_evidence=True,
                device="NVIDIA GeForce MX150",
            )
        )

    def test_opengl_records_are_renderer_scoped(self):
        records = register_verified_native_opengl_partition_evidence()
        self.assertEqual(len(records), 17)
        renderer = "NVIDIA Corporation - NVIDIA GeForce MX150/PCIe/SSE2"
        report = native_partition_evidence_report("opengl", renderer)
        self.assertEqual(report["record_count"], 17)
        self.assertEqual(report["qualified_count"], 17)
        self.assertTrue(
            can_auto_partition_dispatch(
                "guided_filter",
                "opengl",
                require_native_evidence=True,
                device=renderer,
            )
        )
        # The exact renderer identity must not qualify Intel or another ICD.
        self.assertFalse(
            native_partition_evidence_supported(
                "guided_filter", "opengl", "Intel(R) UHD Graphics 620"
            )
        )
        self.assertEqual(block_coverage_report("opengl")["strict_auto_safe"], 48)

    def test_vulkan_intel_extended_records_are_device_scoped(self):
        records = register_verified_native_vulkan_intel_local_stencil_evidence()
        self.assertEqual(len(records), 9)
        report = native_partition_evidence_report(
            "vulkan", "Intel(R) UHD Graphics 620"
        )
        self.assertEqual(report["record_count"], 9)
        self.assertEqual(report["qualified_count"], 9)
        self.assertEqual(report["native_status"], "qualified")
        self.assertEqual(report["native_qualified_count"], 9)
        self.assertTrue(
            can_auto_partition_dispatch(
                "filter2d",
                "vulkan",
                require_native_evidence=True,
                device="Intel(R) UHD Graphics 620",
            )
        )
        # The exact Intel Vulkan observation must not qualify a different
        # physical device or a different graphics backend.
        self.assertFalse(
            native_partition_evidence_supported(
                "filter2d", "vulkan", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "filter2d", "opengl", "Intel(R) UHD Graphics 620"
            )
        )

    def test_vulkan_intel_base_records_are_exact_device_scoped(self):
        records = register_verified_native_vulkan_intel_base_evidence()
        self.assertEqual(len(records), 8)
        report = native_partition_evidence_report(
            "vulkan", "Intel(R) UHD Graphics 620"
        )
        self.assertEqual(report["record_count"], 8)
        self.assertEqual(report["native_qualified_count"], 8)
        self.assertEqual(report["native_status"], "qualified")
        self.assertTrue(
            native_partition_evidence_supported(
                "copy", "vulkan", "Intel(R) UHD Graphics 620"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "copy", "vulkan", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "copy", "opengl", "Intel(R) UHD Graphics 620"
            )
        )

    def test_vulkan_nvidia_resize_record_captures_four_case_cache_probe(self):
        records = register_verified_native_vulkan_nvidia_resize_evidence()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.operation, "resize")
        self.assertEqual(record.backend, "vulkan")
        self.assertEqual(record.device, "NVIDIA GeForce MX150")
        self.assertEqual(record.device_id, 2)
        self.assertEqual(record.block_size, 7)
        self.assertEqual(len(record.shape), 4)
        self.assertEqual(record.dtype, ["float32"])
        self.assertTrue(record.qualified)
        self.assertIn("batch_offset", record.note)
        self.assertIn("cache hits", record.note)
        report = native_partition_evidence_report(
            "vulkan", "NVIDIA GeForce MX150"
        )
        self.assertEqual(report["record_count"], 1)
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "vulkan", "NVIDIA GeForce MX150"
            )
        )
        # Exact-device/backend scope: this record must not promote Intel or
        # an OpenGL renderer.
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "vulkan", "Intel(R) UHD Graphics 620"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "opengl", "NVIDIA GeForce MX150"
            )
        )

    def test_vulkan_intel_resize_record_is_exact_device_scoped(self):
        records = register_verified_native_vulkan_intel_resize_evidence()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.operation, "resize")
        self.assertEqual(record.backend, "vulkan")
        self.assertEqual(record.device, "Intel(R) UHD Graphics 620")
        self.assertEqual(record.device_id, 0)
        self.assertEqual(record.block_size, 7)
        self.assertEqual(len(record.shape), 4)
        self.assertEqual(record.dtype, ["float32"])
        self.assertTrue(record.qualified)
        self.assertIn("batch_offset", record.note)
        self.assertIn("cache hits", record.note)
        report = native_partition_evidence_report(
            "vulkan", "Intel(R) UHD Graphics 620"
        )
        self.assertEqual(report["record_count"], 1)
        self.assertEqual(report["native_status"], "qualified")
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "vulkan", "Intel(R) UHD Graphics 620"
            )
        )
        # Exact-device/backend scope: this record must not promote NVIDIA or
        # the OpenGL path.
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "vulkan", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "opengl", "Intel(R) UHD Graphics 620"
            )
        )

    def test_cuda_resize_record_retains_float32_tolerance(self):
        records = register_verified_native_cuda_resize_evidence()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record.operation, "resize")
        self.assertEqual(record.backend, "cuda")
        self.assertEqual(record.device, "NVIDIA GeForce MX150")
        self.assertEqual(record.device_id, 0)
        self.assertEqual(record.block_size, 7)
        self.assertEqual(record.tolerance, 2.0e-5)
        self.assertEqual(record.interpolations, ("linear", "cubic", "area"))
        self.assertAlmostEqual(record.max_abs_error, 1.1920928955078125e-7)
        self.assertTrue(record.passed)
        self.assertTrue(record.qualified)
        self.assertIn("float32 tolerance", record.note)
        report = native_partition_evidence_report("cuda", "NVIDIA GeForce MX150")
        self.assertEqual(report["record_count"], 1)
        self.assertEqual(report["native_status"], "qualified")
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150"
            )
        )
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150", "linear"
            )
        )
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150", "cubic"
            )
        )
        self.assertTrue(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150", "area"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150", "lanczos"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "cuda", "NVIDIA GeForce MX150", ""
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "resize", "cuda", "other NVIDIA device"
            )
        )

    def test_cuda_records_are_exact_mx150_scoped(self):
        records = register_verified_native_cuda_partition_evidence()
        self.assertEqual(len(records), 24)
        report = native_partition_evidence_report("cuda", "NVIDIA GeForce MX150")
        self.assertEqual(report["record_count"], 24)
        self.assertEqual(report["native_qualified_count"], 24)
        self.assertEqual(report["native_status"], "qualified")
        self.assertEqual(len(report["qualified_operations"]), 24)
        self.assertIn("smooth_flow", report["qualified_operations"])
        self.assertNotIn("smooth_flow_gpu", report["qualified_operations"])
        self.assertNotIn("otsu_threshold", report["qualified_operations"])
        self.assertTrue(
            native_partition_evidence_supported(
                "filter2d", "cuda", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "filter2d", "cuda", "other NVIDIA device"
            )
        )
        self.assertTrue(
            native_partition_evidence_supported(
                "guided_filter", "cuda", "NVIDIA GeForce MX150"
            )
        )
        self.assertFalse(
            native_partition_evidence_supported(
                "otsu_threshold", "cuda", "NVIDIA GeForce MX150"
            )
        )

    def test_opengl_intel_only_registers_passed_subset(self):
        records = register_verified_native_opengl_intel_evidence()
        self.assertEqual(len(records), 16)
        report = native_partition_evidence_report("opengl", "Intel(R) UHD Graphics 620")
        self.assertEqual(report["record_count"], 16)
        self.assertEqual(report["qualified_count"], 16)
        self.assertFalse(
            native_partition_evidence_supported(
                "guided_filter", "opengl", "Intel(R) UHD Graphics 620"
            )
        )


if __name__ == "__main__":
    unittest.main()
