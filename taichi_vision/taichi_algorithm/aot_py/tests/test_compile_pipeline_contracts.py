"""Pure build-cache/archive contract tests; no Taichi import or compiler run."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[4]
AOT_PY = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py"
sys.path.insert(0, str(AOT_PY))

import aot_artifact  # noqa: E402
import compile_aot_backend_suite as suite  # noqa: E402
import target_registry  # noqa: E402


class CompilePipelineContractTests(unittest.TestCase):
    def test_cache_requires_matching_build_and_artifact_provenance(self):
        identity = {"source_sha256": "source-a", "target": "cpu_x64"}
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "sample.tcm"
            artifact.write_bytes(b"first payload")
            self.assertEqual(suite._verified_build(artifact, identity), (False, "provenance_missing"))

            suite._write_build_provenance(artifact, identity)
            self.assertEqual(suite._verified_build(artifact, identity), (True, "fingerprint_and_payload_match"))

            changed_identity = {**identity, "source_sha256": "source-b"}
            self.assertEqual(suite._verified_build(artifact, changed_identity), (False, "build_inputs_mismatch"))
            artifact.write_bytes(b"changed payload")
            self.assertEqual(suite._verified_build(artifact, identity), (False, "artifact_size_mismatch"))

    @staticmethod
    def _alias_identity(output_name: str, source: str = "source-a"):
        return {
            "source_sha256": source,
            "target": "cpu_x64",
            "job": "block_matching",
            "aliases": ["lucas_kanade_bm"],
            "output_artifact": output_name,
            "output_roster": ["block_matching", "lucas_kanade_bm"],
            "graph_build_signature": "graph-signature-v1",
            "with_tcm_manifest": True,
        }

    def test_job_cache_hit_requires_verified_primary_and_alias(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ("block_matching", "lucas_kanade_bm"):
                artifact = Path(temp) / f"{name}.tcm"
                artifact.write_bytes(name.encode("ascii"))
                identity = self._alias_identity(name)
                suite._write_build_provenance(artifact, identity)
                outputs.append((name, artifact, identity))
            self.assertEqual(suite._verified_job_build(outputs), (True, "all_outputs_verified"))

    def test_missing_alias_invalidates_whole_job_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            primary = Path(temp) / "block_matching.tcm"
            alias = Path(temp) / "lucas_kanade_bm.tcm"
            primary.write_bytes(b"primary")
            primary_identity = self._alias_identity("block_matching")
            alias_identity = self._alias_identity("lucas_kanade_bm")
            suite._write_build_provenance(primary, primary_identity)
            self.assertEqual(
                suite._verified_job_build([
                    ("block_matching", primary, primary_identity),
                    ("lucas_kanade_bm", alias, alias_identity),
                ]),
                (False, "lucas_kanade_bm:artifact_missing"),
            )

    def test_missing_alias_sidecar_invalidates_whole_job_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            primary = Path(temp) / "block_matching.tcm"
            alias = Path(temp) / "lucas_kanade_bm.tcm"
            primary.write_bytes(b"primary")
            alias.write_bytes(b"alias")
            primary_identity = self._alias_identity("block_matching")
            alias_identity = self._alias_identity("lucas_kanade_bm")
            suite._write_build_provenance(primary, primary_identity)
            self.assertEqual(
                suite._verified_job_build([
                    ("block_matching", primary, primary_identity),
                    ("lucas_kanade_bm", alias, alias_identity),
                ]),
                (False, "lucas_kanade_bm:provenance_missing"),
            )

    def test_changed_alias_payload_invalidates_whole_job_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ("block_matching", "lucas_kanade_bm"):
                artifact = Path(temp) / f"{name}.tcm"
                artifact.write_bytes(b"payload")
                identity = self._alias_identity(name)
                suite._write_build_provenance(artifact, identity)
                outputs.append((name, artifact, identity))
            outputs[1][1].write_bytes(b"changed")  # same size; hash must catch it
            self.assertEqual(
                suite._verified_job_build(outputs),
                (False, "lucas_kanade_bm:artifact_hash_mismatch"),
            )

    def test_stale_alias_fingerprint_invalidates_whole_job_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ("block_matching", "lucas_kanade_bm"):
                artifact = Path(temp) / f"{name}.tcm"
                artifact.write_bytes(b"payload")
                identity = self._alias_identity(name)
                stamped_identity = self._alias_identity(name, source="old-source") if name.endswith("bm") else identity
                suite._write_build_provenance(artifact, stamped_identity)
                outputs.append((name, artifact, identity))
            self.assertEqual(
                suite._verified_job_build(outputs),
                (False, "lucas_kanade_bm:build_inputs_mismatch"),
            )

    def test_manifest_bytes_cannot_rescue_alias_without_producer_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            primary = Path(temp) / "block_matching.tcm"
            alias = Path(temp) / "lucas_kanade_bm.tcm"
            primary.write_bytes(b"primary")
            alias.write_bytes(b'{"tcm_manifest":{"compiler_version":"current"}}')
            primary_identity = self._alias_identity("block_matching")
            alias_identity = self._alias_identity("lucas_kanade_bm")
            suite._write_build_provenance(primary, primary_identity)
            self.assertEqual(
                suite._verified_job_build([
                    ("block_matching", primary, primary_identity),
                    ("lucas_kanade_bm", alias, alias_identity),
                ]),
                (False, "lucas_kanade_bm:provenance_missing"),
            )

    def test_arm_profiles_are_selectable_from_active_target_manifest(self):
        self.assertIn("cpu_arm64_android", target_registry.TARGET_BACKENDS)
        self.assertIn("cpu_arm64_linux", target_registry.TARGET_BACKENDS)
        self.assertIn("vulkan_arm64_android", target_registry.TARGET_BACKENDS)

    def test_read_only_normalized_archive_check_accepts_canonical_payload(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "sample.tcm"
            with zipfile.ZipFile(artifact, "w") as archive:
                for name, payload in (("__version__", b"1.7.4"), ("graphs.json", b"[]")):
                    info = zipfile.ZipInfo(name, date_time=(2000, 12, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, payload)
            before = artifact.read_bytes()
            aot_artifact.validate_normalized_tcm(artifact)
            self.assertEqual(artifact.read_bytes(), before)

    def test_read_only_normalized_archive_check_rejects_noncanonical_order(self):
        with tempfile.TemporaryDirectory() as temp:
            artifact = Path(temp) / "sample.tcm"
            with zipfile.ZipFile(artifact, "w") as archive:
                archive.writestr("z", b"z")
                archive.writestr("__version__", b"1.7.4")
            with self.assertRaisesRegex(ValueError, "not normalized"):
                aot_artifact.validate_normalized_tcm(artifact)


if __name__ == "__main__":
    unittest.main()
