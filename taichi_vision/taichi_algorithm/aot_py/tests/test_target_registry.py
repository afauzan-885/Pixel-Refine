"""Pure target-registry canonicalization tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

from taichi_vision.taichi_aot.artifact_targets import TargetSpec, _artifact_matches_target


ROOT = Path(__file__).resolve().parents[4]
PATH = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "target_registry.py"
SPEC = importlib.util.spec_from_file_location("pixel_refine_target_registry_test", PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TargetRegistryTests(unittest.TestCase):
    def test_graphics_artifact_requires_spirv_payload(self):
        """A graphics target must never accept a CPU/CUDA LLVM archive."""
        target = TargetSpec(
            backend="vulkan", arch="x86_64", os="windows", vendor="intel"
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wrong.tcm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("graphs.tcb", b"llvm")
                archive.writestr("kernel.ll", b'target triple = "x86_64-pc-windows-msvc"')
            self.assertFalse(_artifact_matches_target(path, target))

    def test_graphics_artifact_accepts_graph_index_and_spirv(self):
        target = TargetSpec(
            backend="opengl", arch="x86_64", os="windows", vendor="nvidia"
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "valid.tcm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("graphs.json", b"{}")
                archive.writestr("graph_0.spv", b"\x03\x02\x23\x07payload")
            self.assertTrue(_artifact_matches_target(path, target))

    def test_graphics_artifact_rejects_placeholder_shader_payload(self):
        target = TargetSpec(
            backend="vulkan", arch="x86_64", os="windows", vendor="intel"
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "placeholder.tcm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("graphs.json", b"{}")
                archive.writestr("graph_0.spv", b"SPIR-V")
            self.assertFalse(_artifact_matches_target(path, target))

    def test_graphics_artifact_rejects_malformed_graph_index(self):
        target = TargetSpec(
            backend="opengl", arch="x86_64", os="windows", vendor="nvidia"
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "malformed.tcm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("graphs.json", b"not-json")
                archive.writestr("graph_0.spv", b"\x03\x02\x23\x07payload")
            self.assertFalse(_artifact_matches_target(path, target))

    def test_android_opengl_alias_matches_runtime_gles_identity(self):
        self.assertEqual(
            MODULE.target_id_from_entry(
                {
                    "backend": "opengl",
                    "arch": "aarch64",
                    "os": "android",
                    "vendor": "unknown",
                }
            ),
            "gles_arm64_android",
        )

    def test_architecture_alias_matches_target_spec_contract(self):
        self.assertEqual(
            MODULE.target_id_from_entry(
                {
                    "backend": "cpu",
                    "arch": "arm64-v8a",
                    "os": "linux",
                }
            ),
            "cpu_arm64_linux",
        )

    def test_cuda_identity_rejects_non_nvidia_vendor(self):
        with self.assertRaises(ValueError):
            MODULE.validate_target_identity(
                {
                    "backend": "cuda",
                    "arch": "x86_64",
                    "os": "windows",
                    "vendor": "amd",
                }
            )

    def test_identity_rejects_path_escape_tokens(self):
        """Manifest identity cannot escape the artifact target root."""
        with self.assertRaisesRegex(ValueError, "unsafe architecture"):
            MODULE.validate_target_identity(
                {
                    "backend": "cpu",
                    "arch": "../outside",
                    "os": "windows",
                }
            )

        with self.assertRaisesRegex(ValueError, "unsafe OS"):
            MODULE.validate_target_identity(
                {
                    "backend": "cpu",
                    "arch": "x86_64",
                    "os": "C:",
                }
            )

    def test_runtime_report_marks_targets_without_qualification_fail_closed(self):
        report = MODULE.target_runtime_report()
        self.assertEqual(report["target_count"], 16)
        self.assertEqual(report["unverified_count"], 8)
        self.assertEqual(report["native_runtime_count"], 0)
        self.assertEqual(report["compile_only_count"], 8)
        self.assertEqual(report["native_runtime_percent"], 0.0)
        self.assertEqual(report["non_native_count"], 16)
        self.assertTrue(report["fail_closed"])
        self.assertEqual(report["backend_summary"]["cuda"]["target_count"], 2)
        self.assertEqual(report["backend_summary"]["cuda"]["native_runtime_percent"], 0.0)
        self.assertTrue(report["backend_summary"]["cuda"]["fail_closed"])
        records = {record["target_id"]: record for record in report["records"]}
        self.assertEqual(records["opengl_x86_64_windows_nvidia"]["status"], "unverified")
        self.assertTrue(records["opengl_x86_64_windows_nvidia"]["fail_closed"])
        self.assertIn("runtime_requirements", records["opengl_x86_64_windows_nvidia"]["missing"])
        self.assertEqual(records["cpu_arm64_android"]["status"], "compile_only")
        self.assertTrue(records["cpu_arm64_android"]["fail_closed"])

    def test_runtime_report_flags_orphan_requirement_identity(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ],
            "runtime_requirements": {
                "cpu_x86_64_windows_stale": {
                    "qualification": "native_runtime",
                    "native_runtime": True,
                    "runtime_evidence_id": "stale-probe",
                }
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = MODULE.target_runtime_report(manifest_path)
        self.assertEqual(
            report["orphan_runtime_requirements"],
            ("cpu_x86_64_windows_stale",),
        )
        self.assertTrue(report["fail_closed"])

    def test_runtime_report_requires_traceable_native_evidence_id(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ],
            "runtime_requirements": {
                "cpu_x86_64_windows": {
                    "qualification": "native_runtime",
                    "native_runtime": True,
                }
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = MODULE.target_runtime_report(manifest_path)
        record = report["records"][0]
        self.assertEqual(record["status"], "unverified")
        self.assertFalse(record["native_runtime"])
        self.assertIsNone(record["runtime_evidence_id"])
        self.assertIn("runtime_evidence_id", record["missing"])
        self.assertTrue(report["fail_closed"])

    def test_runtime_report_accepts_native_runtime_with_evidence_id(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ],
            "runtime_requirements": {
                "cpu_x86_64_windows": {
                    "qualification": "native_runtime",
                    "native_runtime": True,
                    "runtime_evidence_id": "cpu-win-ci-2026-08-14",
                }
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = MODULE.target_runtime_report(manifest_path)
        record = report["records"][0]
        self.assertEqual(record["status"], "native_runtime")
        self.assertTrue(record["native_runtime"])
        self.assertEqual(record["runtime_evidence_id"], "cpu-win-ci-2026-08-14")
        self.assertFalse(report["fail_closed"])

    def test_runtime_report_rejects_contradictory_compile_only_native_claim(self):
        """A compile-only row must not expose native_runtime=True."""
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ],
            "runtime_requirements": {
                "cpu_x86_64_windows": {
                    "qualification": "compile_only",
                    "native_runtime": True,
                    "runtime_evidence_id": "contradictory-probe",
                }
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = MODULE.target_runtime_report(manifest_path)
        record = report["records"][0]
        self.assertFalse(record["native_runtime"])
        self.assertEqual(record["status"], "compile_only")
        self.assertIn("native_runtime_qualification", record["missing"])
        self.assertTrue(report["fail_closed"])

    def test_runtime_report_rejects_invalid_cuda_identity_before_promotion(self):
        """Runtime evidence must not bypass the canonical vendor gate."""
        manifest = {
            "target_matrix": [
                {
                    "backend": "cuda",
                    "arch": "x86_64",
                    "os": "windows",
                    "vendor": "amd",
                }
            ],
            "runtime_requirements": {
                "cuda_x86_64_windows_amd": {
                    "qualification": "native_runtime",
                    "native_runtime": True,
                    "runtime_evidence_id": "invalid-cuda-vendor",
                }
            },
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CUDA target identity"):
                MODULE.target_runtime_report(manifest_path)

    def test_runtime_report_rejects_duplicate_canonical_target_identity(self):
        """Runtime status must not depend on duplicate manifest row order."""
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
                # amd64/win32 canonicalizes to the same target ID.
                {"backend": "cpu", "arch": "amd64", "os": "win32"},
            ],
            "runtime_requirements": {},
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                ValueError, "duplicate target ID in runtime report"
            ):
                MODULE.target_runtime_report(manifest_path)

    def test_artifact_report_requires_exact_target_qualified_filename(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
                {"backend": "cuda", "arch": "x86_64", "os": "windows", "vendor": "nvidia"},
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "cpu_x86_64_windows").mkdir()
            (root / "cpu_x86_64_windows" / "gaussian_cpu_x86_64_windows.tcm").touch()
            (root / "cuda_x86_64_windows_nvidia").mkdir()
            # A foreign suffix must not count as a CUDA artifact.
            (root / "cuda_x86_64_windows_nvidia" / "resize_cuda_x86_64_windows.tcm").touch()
            report = MODULE.target_artifact_report(manifest_path, root)
            records = {record["target_id"]: record for record in report["records"]}
            self.assertEqual(report["present_count"], 1)
            self.assertEqual(report["missing_count"], 1)
            self.assertEqual(report["missing_targets"], ("cuda_x86_64_windows_nvidia",))
            self.assertEqual(
                report["backend_summary"]["cuda"]["missing_count"], 1
            )
            self.assertFalse(records["cuda_x86_64_windows_nvidia"]["artifact_identity_valid"])
            self.assertEqual(
                records["cuda_x86_64_windows_nvidia"]["missing_reasons"],
                ("target_qualified_tcm", "foreign_or_stale_tcm"),
            )
            self.assertIn(
                "resize_cuda_x86_64_windows.tcm",
                records["cuda_x86_64_windows_nvidia"]["invalid_artifact_names"],
            )
            self.assertTrue(report["fail_closed"])

    def test_artifact_report_rejects_invalid_target_identity(self):
        """Filesystem presence must not bypass the canonical CUDA identity gate."""
        manifest = {
            "target_matrix": [
                {
                    "backend": "cuda",
                    "arch": "x86_64",
                    "os": "windows",
                    "vendor": "amd",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CUDA target identity"):
                MODULE.target_artifact_report(manifest_path, root)

    def test_artifact_report_flags_directory_not_declared_in_manifest(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "cpu_x86_64_windows").mkdir()
            (root / "cpu_x86_64_windows" / "gaussian_cpu_x86_64_windows.tcm").touch()
            (root / "stale_target").mkdir()
            report = MODULE.target_artifact_report(manifest_path, root)
            self.assertEqual(report["unexpected_target_dirs"], ("stale_target",))
            self.assertTrue(report["fail_closed"])

    def test_artifact_report_flags_root_level_tcm_as_foreign(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            target_dir = root / "cpu_x86_64_windows"
            target_dir.mkdir()
            (target_dir / "gaussian_cpu_x86_64_windows.tcm").touch()
            (root / "stale_root_module.tcm").touch()
            report = MODULE.target_artifact_report(manifest_path, root)
            self.assertEqual(report["present_count"], 1)
            self.assertEqual(
                report["unexpected_root_artifacts"], ("stale_root_module.tcm",)
            )
            self.assertTrue(report["fail_closed"])

    def test_artifact_report_excludes_atomic_replacement_files(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            target_dir = root / "cpu_x86_64_windows"
            target_dir.mkdir()
            (target_dir / "gaussian_cpu_x86_64_windows.tcm").touch()
            (target_dir / "gaussian_cpu_x86_64_windows.next.tcm").touch()
            (root / "staging_cpu_x86_64_windows.staging.tcm").touch()
            report = MODULE.target_artifact_report(manifest_path, root)
            self.assertEqual(report["present_count"], 1)
            self.assertFalse(report["fail_closed"])
            self.assertEqual(
                report["records"][0]["temporary_artifact_names"],
                ("gaussian_cpu_x86_64_windows.next.tcm",),
            )
            self.assertEqual(
                report["temporary_root_artifacts"],
                ("staging_cpu_x86_64_windows.staging.tcm",),
            )
            self.assertEqual(report["missing_targets"], ())

    def test_artifact_report_diagnoses_target_with_only_temporary_tcm(self):
        manifest = {
            "target_matrix": [
                {"backend": "cpu", "arch": "x86_64", "os": "windows"},
            ]
        }
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            target_dir = root / "cpu_x86_64_windows"
            target_dir.mkdir()
            temporary = target_dir / "gaussian_cpu_x86_64_windows.next.tcm"
            temporary.touch()

            report = MODULE.target_artifact_report(manifest_path, root)
            record = report["records"][0]
            self.assertEqual(report["present_count"], 0)
            self.assertEqual(report["missing_targets"], ("cpu_x86_64_windows",))
            self.assertEqual(
                record["missing_reasons"],
                ("target_qualified_tcm", "temporary_only_tcm"),
            )
            self.assertEqual(record["temporary_artifact_names"], (temporary.name,))
            self.assertTrue(report["fail_closed"])


if __name__ == "__main__":
    unittest.main()
