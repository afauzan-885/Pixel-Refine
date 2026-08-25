"""Focused ARM compile-only/native qualification gates."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
AOT_PY = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py"
if str(AOT_PY) not in sys.path:
    sys.path.insert(0, str(AOT_PY))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load("arm_matrix_audit", AOT_PY / "audit_aot_matrix.py")
VALIDATOR = _load("arm_bridge_validator", AOT_PY / "validate_arm_bridge.py")
TARGETS = _load(
    "arm_artifact_targets",
    ROOT / "taichi_vision" / "taichi_aot" / "artifact_targets.py",
)


class ArmNativeMatrixTests(unittest.TestCase):
    def test_cross_compiled_arm_target_is_fail_closed(self):
        target = TARGETS.TargetSpec(
            backend="vulkan", arch="arm64", os="android", abi="arm64-v8a"
        )
        gate = AUDIT._runtime_gate(
            target,
            {
                "qualification": "compile_only",
                "native_runtime": False,
                "runtime_evidence_required": True,
            },
        )
        self.assertEqual(gate["qualification"], "compile_only")
        self.assertFalse(gate["native_runtime"])
        self.assertTrue(gate["fail_closed"])

    def test_native_arm_requires_explicit_evidence_id(self):
        target = TARGETS.TargetSpec(backend="cpu", arch="arm64", os="linux")
        missing_id = AUDIT._runtime_gate(
            target, {"qualification": "native_runtime", "native_runtime": True}
        )
        self.assertFalse(missing_id["native_runtime"])
        self.assertTrue(missing_id["fail_closed"])
        with_id = AUDIT._runtime_gate(
            target,
            {
                "qualification": "native_runtime",
                "native_runtime": True,
                "runtime_evidence_id": "arm-ci-2026-08-13",
            },
        )
        self.assertTrue(with_id["native_runtime"])
        self.assertFalse(with_id["fail_closed"])

    def test_manifest_rejects_contradictory_arm_qualification(self):
        manifest_path = (
            ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
        )
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["runtime_requirements"]["cpu_arm64_android"]["native_runtime"] = True
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "manifest.json"
            candidate.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                TARGETS.load_target_manifest(candidate)

    def test_bridge_validator_labels_static_result_compile_only(self):
        # The real ELF/NEON validator requires an ARM toolchain artifact.  Its
        # result contract can still be checked without pretending this host is
        # an ARM runtime.
        self.assertEqual(VALIDATOR.STATIC_QUALIFICATION, "compile_only")
        self.assertIn("ti_cast_buffer", VALIDATOR.REQUIRED_SYMBOLS)


if __name__ == "__main__":
    unittest.main()
