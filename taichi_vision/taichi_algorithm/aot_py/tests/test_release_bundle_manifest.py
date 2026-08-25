"""Focused packaging checks for target-qualified TCM identities."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path
import tempfile
import unittest
import zipfile

from taichi_vision.release_bundle import _target_id as release_target_id
from taichi_vision.release_bundle import preflight_manifest_targets
from taichi_vision.release_bundle import cleanup_aot_bundle, plan_runtime_payload
from taichi_vision.validate_native_bundle import (
    NativeBundleValidationError,
    _target_id as validator_target_id,
    validate_native_bundle,
)


class ReleaseBundleManifestTests(unittest.TestCase):
    def test_runtime_payload_planner_uses_self_relative_release_layout(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            target = "cpu_x86_64_windows"
            bundle = root / "bundles" / target
            tcm_dir = bundle / "tcm" / target
            tcm_dir.mkdir(parents=True)
            bridge = bundle / "taichi_aot_engine.dll"
            bridge.write_bytes(b"bridge")
            tcm = tcm_dir / f"copy_{target}.tcm"
            with zipfile.ZipFile(tcm, "w") as archive:
                archive.writestr("tcm_manifest.json", json.dumps({"format_version": 1}))

            def record(path: Path) -> dict[str, object]:
                return {
                    "path": path.relative_to(root).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }

            manifest = {
                "schema_version": 1,
                "scope": "runtime_payload",
                "record_root": root.as_posix(),
                "bundles": [{
                    "target": target,
                    "file_count": 2,
                    "tcm_count": 1,
                    "files": [record(bridge), record(tcm)],
                }],
            }
            (root / "RELEASE_MANIFEST.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            plan = plan_runtime_payload(runtime_root=root, backends=("cpu",))
            try:
                self.assertEqual(plan.target_ids, (target,))
                self.assertEqual(len(plan.artifacts), 1)
                self.assertEqual(len(plan.bridges), 1)
                self.assertEqual(plan.data_dirs[0][1], "bundles/cpu_x86_64_windows")
            finally:
                cleanup_aot_bundle(plan)

    def test_validator_target_identity_matches_release_aliases(self):
        # The release planner canonicalizes aliases before creating target
        # directories.  The final validator must use the same identity or a
        # valid staged bundle can be rejected (notably Android OpenGL -> GLES).
        entries = (
            {"backend": "cpu", "arch": "amd64", "os": "win32"},
            {"backend": "vk", "arch": "arm64-v8a", "os": "android", "vendor": "unknown"},
            {"backend": "opengl", "arch": "arm64-v8a", "os": "android"},
        )
        for entry in entries:
            self.assertEqual(validator_target_id(entry), release_target_id(entry))

    def test_validator_rejects_unknown_backend_identity(self):
        """The extracted-bundle gate must not trust a hand-edited backend."""
        with self.assertRaisesRegex(
            NativeBundleValidationError, "unsupported AOT target backend"
        ):
            validator_target_id(
                {"backend": "made_up", "arch": "x86_64", "os": "windows"}
            )

    def _fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        tcm = root / "aot_tcm"
        dll = root / "aot_dll"
        target = "cpu_x86_64_windows"
        (tcm / target).mkdir(parents=True)
        (dll / "cpu").mkdir(parents=True)
        (dll / "cpu" / "taichi_aot_engine.dll").touch()
        manifest = root / "target_manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "target_matrix": [
                        {"backend": "cpu", "arch": "x86_64", "os": "windows"}
                    ],
                }
            ),
            encoding="utf-8",
        )
        return temp, tcm, dll, manifest, target

    def test_preflight_reports_foreign_tcm_suffix(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            target_dir = tcm / target
            (target_dir / f"gaussian_{target}.tcm").touch()
            (target_dir / "resize_cpu_x86_64_linux.tcm").touch()
            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            details = report["targets"][target]
            self.assertFalse(details["ready"])
            self.assertIn("invalid_tcm_artifacts", details["missing"])
            self.assertEqual(
                details["invalid_tcm_artifacts"],
                ["resize_cpu_x86_64_linux.tcm"],
            )
            self.assertEqual(report["target_count"], 1)
            self.assertEqual(report["ready_count"], 0)
            self.assertEqual(report["incomplete_count"], 1)
            self.assertTrue(report["backend_summary"]["cpu"]["fail_closed"])
        finally:
            temp.cleanup()

    def test_preflight_rejects_non_object_target_rows(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["target_matrix"].append("not-a-target")
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-object target entry"):
                preflight_manifest_targets(
                    tcm_root=tcm, dll_root=dll, manifest_path=manifest
                )
        finally:
            temp.cleanup()

    def test_preflight_rejects_duplicate_canonical_target_rows(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            # x64/amd64 are aliases of the existing x86_64/windows target.
            payload["target_matrix"].append(
                {"backend": "cpu", "arch": "amd64", "os": "win32"}
            )
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate AOT target ID"):
                preflight_manifest_targets(
                    tcm_root=tcm, dll_root=dll, manifest_path=manifest
                )
        finally:
            temp.cleanup()

    def test_preflight_rejects_unknown_backend(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["target_matrix"] = [
                {"backend": "made_up", "arch": "x86_64", "os": "windows"}
            ]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unsupported AOT target backend"):
                preflight_manifest_targets(
                    tcm_root=tcm, dll_root=dll, manifest_path=manifest
                )
        finally:
            temp.cleanup()

    def test_preflight_rejects_cuda_target_with_non_nvidia_vendor(self):
        """Release planning must share the canonical CUDA vendor gate."""
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["target_matrix"] = [
                {"backend": "cuda", "arch": "x86_64", "os": "windows", "vendor": "amd"}
            ]
            manifest.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "CUDA target identity"):
                preflight_manifest_targets(
                    tcm_root=tcm, dll_root=dll, manifest_path=manifest
                )
        finally:
            temp.cleanup()

    def test_preflight_ignores_known_temporary_artifacts(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            target_dir = tcm / target
            (target_dir / f"gaussian_{target}.tcm").touch()
            (target_dir / f"gaussian_{target}.staging.tcm").touch()
            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            details = report["targets"][target]
            self.assertTrue(details["ready"])
            self.assertEqual(details["invalid_tcm_artifacts"], [])
            self.assertEqual(
                details["temporary_tcm_artifacts"],
                [f"gaussian_{target}.staging.tcm"],
            )
            self.assertFalse(report["fail_closed"])
        finally:
            temp.cleanup()

    def test_manifest_preflight_rejects_unexpected_target_directory(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            target_dir = tcm / target
            (target_dir / f"gaussian_{target}.tcm").touch()
            (tcm / "stale_target").mkdir()
            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            self.assertEqual(report["unexpected_target_dirs"], ("stale_target",))
            self.assertTrue(report["fail_closed"])
        finally:
            temp.cleanup()

    def test_manifest_preflight_rejects_root_tcm_but_keeps_root_temporary(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            target_dir = tcm / target
            (target_dir / f"gaussian_{target}.tcm").touch()
            (tcm / "stale_root.tcm").touch()
            (tcm / "copy_cpu_x86_64_windows.next.tcm").touch()
            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            self.assertEqual(report["unexpected_root_artifacts"], ("stale_root.tcm",))
            self.assertEqual(
                report["temporary_root_artifacts"],
                ("copy_cpu_x86_64_windows.next.tcm",),
            )
            self.assertTrue(report["fail_closed"])
        finally:
            temp.cleanup()

    def test_preflight_reports_target_qualified_bridge_mapping(self):
        temp, tcm, dll, manifest, target = self._fixture()
        try:
            target_dir = tcm / target
            (target_dir / f"gaussian_{target}.tcm").touch()
            qualified = dll / target
            qualified.mkdir()
            (qualified / "taichi_aot_engine.dll").write_bytes(b"qualified")
            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            details = report["targets"][target]
            self.assertEqual(details["bridge_resolution"], "target_qualified")
            self.assertTrue(details["qualified_bridge_directory_present"])
            self.assertEqual(details["bridge_files"], ["taichi_aot_engine.dll"])
            self.assertEqual(details["required_bridge_files"], ())
            self.assertEqual(details["missing_required_bridge_files"], ())
            self.assertTrue(details["ready"])
        finally:
            temp.cleanup()

    def test_preflight_resolves_android_opengl_alias_to_gles_bridge(self):
        """Android OpenGL aliases must use the canonical GLES bridge path."""
        temp = tempfile.TemporaryDirectory()
        try:
            root = Path(temp.name)
            tcm = root / "aot_tcm"
            dll = root / "aot_dll"
            target = "gles_arm64_android"
            (tcm / target).mkdir(parents=True)
            (tcm / target / f"copy_{target}.tcm").touch()
            (dll / "gles").mkdir(parents=True)
            (dll / "gles" / "libtaichi_aot_engine.so").write_bytes(b"bridge")
            manifest = root / "target_manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "target_matrix": [
                            {
                                "backend": "opengl",
                                "arch": "arm64-v8a",
                                "os": "android",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = preflight_manifest_targets(
                tcm_root=tcm, dll_root=dll, manifest_path=manifest
            )
            details = report["targets"][target]
            self.assertTrue(details["ready"])
            self.assertEqual(details["backend"], "gles")
            self.assertEqual(details["bridge_resolution"], "legacy_backend")
            self.assertEqual(details["bridge_files"], ["libtaichi_aot_engine.so"])
            self.assertFalse(report["fail_closed"])
        finally:
            temp.cleanup()

    def _staged_native_bundle(self, include_c_api: bool):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        target = "cpu_x86_64_windows"
        tcm_dir = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / target
        dll_dir = root / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll" / "cpu"
        tcm_dir.mkdir(parents=True)
        dll_dir.mkdir(parents=True)
        artifact = tcm_dir / f"copy_{target}.tcm"
        artifact.write_bytes(b"tcm")
        bridge = dll_dir / "taichi_aot_engine.dll"
        bridge.write_bytes(b"bridge")
        c_api = dll_dir / "taichi_c_api.dll"
        if include_c_api:
            c_api.write_bytes(b"c-api")

        def digest(path: Path) -> str:
            import hashlib
            return hashlib.sha256(path.read_bytes()).hexdigest()

        manifest = {
            "schema_version": 1,
            "target_matrix": [{"backend": "cpu", "arch": "x86_64", "os": "windows"}],
            "runtime_requirements": {
                target: {
                    "bridge": "../aot_py/aot_dll/cpu/taichi_aot_engine.dll",
                    "c_api_runtime": "../aot_py/aot_dll/cpu/taichi_c_api.dll",
                }
            },
            "release_bundle": {
                "schema_version": 1,
                "source_manifest_sha256": "0" * 64,
                "targets": [target],
                "modules": ["copy"],
                "temporary_artifacts_excluded": [".staging.tcm", ".next.tcm", ".previous.tcm"],
                "artifacts": [{
                    "target": target, "module": "copy", "filename": artifact.name,
                    "sha256": digest(artifact), "size": artifact.stat().st_size,
                }],
                "bridges": [
                    {"directory": "cpu", "filename": bridge.name, "sha256": digest(bridge), "size": bridge.stat().st_size},
                    *([{"directory": "cpu", "filename": c_api.name, "sha256": digest(c_api), "size": c_api.stat().st_size}] if include_c_api else []),
                ],
            },
        }
        manifest_path = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return temp, root

    def test_validator_requires_manifest_declared_c_api_runtime(self):
        temp, root = self._staged_native_bundle(include_c_api=False)
        try:
            with self.assertRaisesRegex(NativeBundleValidationError, "missing manifest-declared runtime library"):
                validate_native_bundle(root)
        finally:
            temp.cleanup()

    def test_validator_accepts_matching_bridge_and_c_api_pair(self):
        temp, root = self._staged_native_bundle(include_c_api=True)
        try:
            result = validate_native_bundle(root)
            self.assertEqual(result.bridge_count, 2)
        finally:
            temp.cleanup()

    def test_validator_rejects_orphan_runtime_requirement(self):
        temp, root = self._staged_native_bundle(include_c_api=True)
        try:
            manifest_path = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["runtime_requirements"]["cpu_x86_64_windows_stale"] = {}
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(NativeBundleValidationError, "unlisted target IDs"):
                validate_native_bundle(root)
        finally:
            temp.cleanup()

    def test_validator_rejects_cuda_target_with_non_nvidia_vendor(self):
        """A release manifest must honor the canonical CUDA vendor gate."""
        temp, root = self._staged_native_bundle(include_c_api=True)
        try:
            manifest_path = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            payload["target_matrix"] = [
                {"backend": "cuda", "arch": "x86_64", "os": "windows", "vendor": "amd"}
            ]
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(NativeBundleValidationError, "CUDA target identity"):
                validate_native_bundle(root)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
