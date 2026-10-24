"""Pure build-cache/archive contract tests; no Taichi import or compiler run."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile
from unittest import mock


ROOT = Path(__file__).resolve().parents[4]
AOT_PY = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py"
sys.path.insert(0, str(AOT_PY))

import aot_artifact  # noqa: E402
import compile_aot_backend_suite as suite  # noqa: E402
import background_compile  # noqa: E402
import target_registry  # noqa: E402

RUNTIME_TARGETS_PATH = ROOT / "taichi_vision" / "taichi_aot" / "artifact_targets.py"
RUNTIME_TARGETS_SPEC = importlib.util.spec_from_file_location(
    "pixel_refine_artifact_targets_direct", RUNTIME_TARGETS_PATH
)
assert RUNTIME_TARGETS_SPEC is not None and RUNTIME_TARGETS_SPEC.loader is not None
runtime_targets = importlib.util.module_from_spec(RUNTIME_TARGETS_SPEC)
sys.modules[RUNTIME_TARGETS_SPEC.name] = runtime_targets
RUNTIME_TARGETS_SPEC.loader.exec_module(runtime_targets)


class CompilePipelineContractTests(unittest.TestCase):
    @staticmethod
    def _worker_metrics_payload():
        phases = {
            name: 0.25 for name in suite.WORKER_PHASE_BOUNDARIES
        }
        phases.update({name: None for name in suite.UNKNOWN_WORKER_PHASES})
        return {
            "schema_version": suite.WORKER_METRICS_SCHEMA,
            "phase_unit": "seconds",
            "phase_boundaries": suite.WORKER_PHASE_BOUNDARIES,
            "unknown_phase_reasons": suite.UNKNOWN_WORKER_PHASES,
            "job": "sample",
            "backend": "cpu",
            "target": "cpu_x86_64_windows",
            "phases": phases,
            "artifacts": {"sample": {"inventory_status": "unavailable"}},
        }

    def test_worker_metrics_contract_keeps_unavailable_compiler_phases_null(self):
        payload = self._worker_metrics_payload()
        output = "diagnostic\nAOT_METRICS_JSON=" + json.dumps(payload)

        parsed = suite._worker_metrics(output)

        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["phase_unit"], "seconds")
        self.assertEqual(parsed["phases"]["compiler_call_seconds"], 0.25)
        for name in suite.UNKNOWN_WORKER_PHASES:
            self.assertIsNone(parsed["phases"][name], name)
            self.assertIn(name, parsed["unknown_phase_reasons"])

    def test_worker_metrics_contract_rejects_invented_or_malformed_timings(self):
        invalid_values = (1.0, True, float("nan"), -0.1, "0.1")
        for invalid in invalid_values:
            with self.subTest(invalid=invalid):
                payload = self._worker_metrics_payload()
                payload["phases"]["backend_codegen_seconds"] = invalid
                output = "AOT_METRICS_JSON=" + json.dumps(payload)
                self.assertIsNone(suite._worker_metrics(output))

        payload = self._worker_metrics_payload()
        payload["phases"].pop("worker_total_seconds")
        self.assertIsNone(
            suite._worker_metrics("AOT_METRICS_JSON=" + json.dumps(payload))
        )

        payload = self._worker_metrics_payload()
        payload["phases"]["unregistered_phase_seconds"] = 0.1
        self.assertIsNone(
            suite._worker_metrics("AOT_METRICS_JSON=" + json.dumps(payload))
        )

    def test_worker_metrics_contract_rejects_unknown_schema_and_units(self):
        invalid_contracts = (
            ("schema_version", suite.WORKER_METRICS_SCHEMA + 1),
            ("phase_unit", "milliseconds"),
        )
        for field, value in invalid_contracts:
            with self.subTest(field=field):
                payload = self._worker_metrics_payload()
                payload[field] = value
                self.assertIsNone(
                    suite._worker_metrics("AOT_METRICS_JSON=" + json.dumps(payload))
                )

    def test_fake_clock_worker_phases_reach_serialized_compile_report(self):
        class FakeClock:
            def __init__(self):
                self.values = iter((10.0, 10.5, 20.0, 20.25, 30.0, 30.125))

            def __call__(self):
                return next(self.values)

        phases = {}
        clock = FakeClock()
        suite._measure_phase(
            phases, "native_context_import_seconds", lambda: "context", clock=clock
        )
        suite._measure_phase(
            phases, "taichi_import_seconds", lambda: "taichi", clock=clock
        )
        suite._measure_phase(
            phases, "compiler_module_import_seconds", lambda: "compiler", clock=clock
        )
        self.assertEqual(phases["native_context_import_seconds"], 0.5)
        self.assertEqual(phases["taichi_import_seconds"], 0.25)
        self.assertEqual(phases["compiler_module_import_seconds"], 0.125)

        payload = self._worker_metrics_payload()
        payload["phases"].update(phases)
        output = suite._worker_metrics_line(
            payload["job"], payload["backend"], payload["target"],
            payload["phases"], payload["artifacts"],
        )
        parsed = suite._worker_metrics(output)
        self.assertIsNotNone(parsed)
        with tempfile.TemporaryDirectory() as temp:
            with mock.patch.object(suite, "BUILD_REPORT_DIR", Path(temp)):
                report_path = suite._write_compile_report(
                    {"schema": 1, "jobs": [{"worker_metrics": parsed}]}
                )
            report = json.loads(report_path.read_text(encoding="utf-8"))
        reported_phases = report["jobs"][0]["worker_metrics"]["phases"]
        self.assertEqual(reported_phases["native_context_import_seconds"], 0.5)
        self.assertEqual(reported_phases["taichi_import_seconds"], 0.25)
        self.assertEqual(reported_phases["compiler_module_import_seconds"], 0.125)

    @staticmethod
    def _write_target_archive(target, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(path, "w") as archive:
            if target.backend in {"vulkan", "opengl", "gles"}:
                archive.writestr("graphs.json", "[]")
                archive.writestr("graph_0.spv", b"\x03\x02\x23\x07payload")
                return
            if target.backend == "cuda":
                triple = "nvptx64-nvidia-cuda"
            elif target.arch == "arm64" and target.os == "android":
                triple = "aarch64-unknown-linux-android"
            elif target.arch == "arm64":
                triple = "aarch64-unknown-linux-gnu"
            else:
                triple = "x86_64-pc-windows-msvc"
            archive.writestr("graphs.tcb", b"fixture")
            archive.writestr("kernel.ll", f'target triple = "{triple}"')

    def test_target_manifest_selectors_resolver_layout_and_unqualified_gate_agree(self):
        manifest = runtime_targets.load_target_manifest(target_registry.MANIFEST_PATH)
        entries = manifest["target_matrix"]
        target_specs = [
            runtime_targets.TargetSpec(
                backend=entry["backend"],
                arch=entry["arch"],
                os=entry["os"],
                vendor=entry.get("vendor", "unknown"),
                variant=entry.get("variant", ""),
            )
            for entry in entries
        ]
        target_ids = {target.target_id for target in target_specs}
        self.assertEqual(target_ids, set(target_registry.TARGET_BACKENDS))
        self.assertEqual(target_ids, set(suite._target_cli_choices()))
        self.assertEqual(target_ids, set(background_compile._target_cli_choices()))
        for target in target_specs:
            self.assertEqual(
                target_registry.TARGET_BACKENDS[target.target_id], target.backend
            )

        payload = dict(manifest)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest_path = root / "target_manifest.json"
            manifest_path.write_text(json.dumps(payload), encoding="utf-8")
            artifact_root = root / "artifacts"
            for target in target_specs:
                artifact = artifact_root / target.target_id / target.artifact_name("probe")
                self._write_target_archive(target, artifact)
                self.assertEqual(
                    runtime_targets.resolve_artifact(
                        artifact_root, "probe", target, allow_legacy=False
                    ),
                    artifact,
                )
            artifact_report = target_registry.target_artifact_report(
                manifest_path, artifact_root
            )
            self.assertFalse(artifact_report["fail_closed"])
            self.assertEqual(artifact_report["present_count"], len(target_ids))
            runtime_report = target_registry.target_runtime_report(manifest_path)
            self.assertTrue(runtime_report["fail_closed"])
            self.assertEqual(runtime_report["native_runtime_count"], 0)
            self.assertEqual(runtime_report["unverified_count"], len(target_ids))

    def test_incomplete_target_identity_is_rejected_by_registry_and_resolver(self):
        incomplete = {
            "schema_version": 1,
            "target_matrix": [{"backend": "cpu", "os": "windows"}],
        }
        with tempfile.TemporaryDirectory() as temp:
            manifest_path = Path(temp) / "target_manifest.json"
            manifest_path.write_text(json.dumps(incomplete), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "arch"):
                runtime_targets.load_target_manifest(manifest_path)
            with self.assertRaisesRegex(ValueError, "arch"):
                target_registry.target_runtime_report(manifest_path)

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

    def test_vulkan_promotion_rejects_incomplete_source_alias_roster(self):
        with tempfile.TemporaryDirectory() as temp:
            primary = Path(temp) / "block_matching_vulkan_x86_64_windows.tcm"
            primary.write_bytes(b"primary")
            identity = self._alias_identity("block_matching")
            suite._write_build_provenance(primary, identity)
            with self.assertRaisesRegex(RuntimeError, "incomplete Vulkan desktop source roster"):
                suite._require_complete_job_outputs(
                    "block_matching",
                    [("block_matching", primary, identity)],
                    context="Vulkan desktop source",
                )

    def test_vulkan_promotion_accepts_complete_verified_source_alias_roster(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ("block_matching", "lucas_kanade_bm"):
                artifact = Path(temp) / f"{name}_vulkan_x86_64_windows.tcm"
                artifact.write_bytes(name.encode("ascii"))
                identity = self._alias_identity(name)
                suite._write_build_provenance(artifact, identity)
                outputs.append((name, artifact, identity))
            self.assertEqual(
                suite._require_complete_job_outputs(
                    "block_matching", outputs, context="Vulkan desktop source"
                ),
                outputs,
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
