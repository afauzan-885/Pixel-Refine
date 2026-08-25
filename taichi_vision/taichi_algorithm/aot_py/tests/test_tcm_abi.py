"""Offline golden tests for the TCM/runtime ABI v1 envelope."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / "taichi_vision" / "taichi_aot" / "tcm_contract.py"
SPEC = importlib.util.spec_from_file_location("pixel_refine_tcm_contract_test", CONTRACT_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError(f"cannot load {CONTRACT_PATH}")
CONTRACT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CONTRACT)


def _manifest(payload: bytes = b"target triple = \\\"x86_64-pc-windows-msvc\\\"\n") -> dict:
    digest = hashlib.sha256(payload).hexdigest()
    return {
        "magic": CONTRACT.TCM_MAGIC,
        "schema_version": 1,
        "tcm_format_version": 1,
        "compiler_version": "test-compiler-1.0",
        "minimum_runtime_abi": 1,
        "required_runtime_features": ["COMPUTE"],
        "target": {
            "backend": "cpu",
            "arch": "x86_64",
            "os": "windows",
            "vendor": "unknown",
        },
        "payloads": [
            {
                "path": "kernel.ll",
                "kind": "llvm_ir",
                "version": "llvm20",
                "size": len(payload),
                "sha256": digest,
            }
        ],
        "kernels": [
            {
                "name": "copy_kernel",
                "graph": "copy_graph",
                "payload": "kernel.ll",
                "args": [
                    {
                        "name": "src",
                        "type": "buffer",
                        "dtype": "f32",
                        "ndim": 2,
                        "access": "read",
                        "binding": 0,
                    },
                    {
                        "name": "gain",
                        "type": "scalar",
                        "dtype": "f32",
                        "access": "value",
                        "binding": 1,
                    },
                ],
            }
        ],
    }


def _write_archive(path: Path, manifest: dict | None, payload: bytes = b"target triple = \\\"x86_64-pc-windows-msvc\\\"\n") -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("__version__", "1.7.4")
        archive.writestr("graphs.tcb", b"graph")
        archive.writestr("kernel.ll", payload)
        if manifest is not None:
            archive.writestr(CONTRACT.TCM_MANIFEST_NAME, json.dumps(manifest, sort_keys=True))


class TcmAbiTests(unittest.TestCase):
    def test_legacy_archive_is_reported_without_gpu_initialization(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.tcm"
            _write_archive(path, None)
            report = CONTRACT.validate_tcm(path)
            self.assertEqual(report["status"], "legacy")
            self.assertTrue(report["legacy"])

    def test_valid_manifest_and_payload_checksum(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "valid.tcm"
            _write_archive(path, _manifest())
            report = CONTRACT.validate_tcm(
                path,
                runtime_features={"COMPUTE"},
                requested_target={
                    "backend": "cpu",
                    "arch": "amd64",
                    "os": "win32",
                    "vendor": "unknown",
                },
            )
            self.assertEqual(report["status"], "valid")
            self.assertEqual(report["manifest"]["target"]["arch"], "x86_64")
            self.assertEqual(report["manifest"]["kernels"][0]["args"][0]["ndim"], 2)

    def test_missing_runtime_feature_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "feature.tcm"
            _write_archive(path, _manifest())
            with self.assertRaisesRegex(CONTRACT.TcmContractError, "COMPUTE"):
                CONTRACT.validate_tcm(path)

    def test_target_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "target.tcm"
            _write_archive(path, _manifest())
            with self.assertRaisesRegex(CONTRACT.TcmContractError, "target mismatch"):
                CONTRACT.validate_tcm(
                    path,
                    runtime_features={"COMPUTE"},
                    requested_target={
                        "backend": "cuda",
                        "arch": "x86_64",
                        "os": "windows",
                        "vendor": "nvidia",
                    },
                )

    def test_checksum_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "checksum.tcm"
            manifest = _manifest()
            manifest["payloads"][0]["sha256"] = "0" * 64
            _write_archive(path, manifest)
            with self.assertRaisesRegex(CONTRACT.TcmContractError, "checksum mismatch"):
                CONTRACT.validate_tcm(path, runtime_features={"COMPUTE"})

    def test_newer_runtime_abi_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "abi.tcm"
            manifest = _manifest()
            manifest["minimum_runtime_abi"] = 2
            _write_archive(path, manifest)
            with self.assertRaisesRegex(CONTRACT.TcmContractError, "runtime ABI 2"):
                CONTRACT.validate_tcm(path, runtime_features={"COMPUTE"})

    def test_unsafe_payload_path_is_rejected(self) -> None:
        manifest = _manifest()
        manifest["payloads"][0]["path"] = "../kernel.ll"
        with self.assertRaisesRegex(CONTRACT.TcmContractError, "relative POSIX"):
            CONTRACT.validate_manifest(manifest, runtime_features={"COMPUTE"})

    def test_manifest_builder_and_explicit_attach_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "attach.tcm"
            _write_archive(path, None)
            manifest = CONTRACT.build_manifest_from_archive(
                path,
                target={
                    "backend": "cpu",
                    "arch": "x86_64",
                    "os": "windows",
                    "vendor": "unknown",
                },
                compiler_version="taichi-1.7.4-custom",
                required_runtime_features=("COMPUTE",),
            )
            self.assertEqual(manifest["payloads"][0]["kind"], "llvm_ir")
            CONTRACT.attach_manifest(path, manifest)
            report = CONTRACT.validate_tcm(path, runtime_features={"COMPUTE"})
            self.assertEqual(report["status"], "valid")
            self.assertEqual(report["manifest"]["compiler_version"], "taichi-1.7.4-custom")


if __name__ == "__main__":
    unittest.main()
