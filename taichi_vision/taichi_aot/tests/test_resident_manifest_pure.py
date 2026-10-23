"""Pure resident-manifest checks; no Taichi, native bridge, or device import."""
import importlib.util
from pathlib import Path
import unittest


SOURCE = (
    Path(__file__).resolve().parents[2]
    / "taichi_algorithm"
    / "denoising"
    / "resident_manifest.py"
)
SPEC = importlib.util.spec_from_file_location("resident_manifest_pure", SOURCE)
manifest = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(manifest)


class ResidentManifestTests(unittest.TestCase):
    def setUp(self):
        self.target = {
            "backend": "cpu",
            "arch": "x86_64",
            "os": "windows",
            "abi": "",
            "vendor": "unknown",
            "target_id": "cpu_x86_64_windows",
        }
        self.members = {"graphs.tcb": "a" * 64}
        self.metadata = {
            "format": 2,
            "backend": "cpu",
            "model_sha256": "b" * 64,
            "target_identity": dict(self.target),
            "runtime_abi": 1,
            "compiler_version": "test-compiler",
            "runtime_version": "test-runtime",
            "io_schema": {"input": {"shape": [1], "dtype": "float32", "layout": "flat-contiguous"}},
            "artifact_members_sha256": dict(self.members),
        }

    def validate(self, **kwargs):
        return manifest.validate_resident_metadata(
            self.metadata,
            backend="cpu",
            target_identity=self.target,
            model_sha256="b" * 64,
            artifact_members=self.members,
            **kwargs,
        )

    def test_current_identity_and_content_pass(self):
        self.assertEqual(self.validate(), "current")

    def test_model_target_abi_and_member_mismatch_fail_closed(self):
        with self.assertRaisesRegex(RuntimeError, "selected model"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="c" * 64, artifact_members=self.members,
            )
        wrong_target = dict(self.target, arch="arm64")
        with self.assertRaisesRegex(RuntimeError, "target mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=wrong_target,
                model_sha256="b" * 64, artifact_members=self.members,
            )
        with self.assertRaisesRegex(RuntimeError, "ABI mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="b" * 64, runtime_abi=2, artifact_members=self.members,
            )
        with self.assertRaisesRegex(RuntimeError, "member hash mismatch"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target,
                model_sha256="b" * 64, artifact_members={"graphs.tcb": "c" * 64},
            )

    def test_artifact_only_mode_is_explicit_and_legacy_is_bounded(self):
        with self.assertRaisesRegex(RuntimeError, "requires model_sha256"):
            manifest.validate_resident_metadata(
                self.metadata, backend="cpu", target_identity=self.target
            )
        legacy = {"format": 1, "backend": "cpu", "model_sha256": "b" * 64}
        self.assertEqual(
            manifest.validate_resident_metadata(
                legacy, backend="cpu", target_identity=self.target,
                artifact_only=True,
            ),
            "legacy-artifact-only",
        )
        with self.assertRaisesRegex(RuntimeError, "explicit artifact-only"):
            manifest.validate_resident_metadata(
                legacy, backend="cpu", target_identity=self.target
            )
        with self.assertRaisesRegex(RuntimeError, "backend mismatch"):
            manifest.validate_resident_metadata(
                legacy, backend="vulkan", target_identity=self.target,
                artifact_only=True,
            )


if __name__ == "__main__":
    unittest.main()
