"""Tests for the pure TCM preflight adapter."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[4]
CONTRACT_PATH = ROOT / "taichi_vision" / "taichi_aot" / "tcm_contract.py"
PREFLIGHT_PATH = ROOT / "taichi_vision" / "taichi_aot" / "tcm_preflight.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


CONTRACT = _load(CONTRACT_PATH, "pixel_refine_tcm_contract_preflight_test")
PREFLIGHT = _load(PREFLIGHT_PATH, "pixel_refine_tcm_preflight_test")


def _write_legacy(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("__version__", "1.7.4")
        archive.writestr("graphs.tcb", b"graph")
        archive.writestr("kernel.ll", b"llvm")


def _write_legacy_cuda_with_host_ir(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("__version__", "1.7.4")
        archive.writestr("graphs.tcb", b"graph")
        archive.writestr(
            "kernel.ll",
            b'target triple = "x86_64-pc-windows-msvc"\n',
        )


def _write_legacy_cpu_windows_ir(path: Path) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("__version__", "1.7.4")
        archive.writestr("graphs.tcb", b"graph")
        archive.writestr(
            "kernel.ll",
            b'target triple = "x86_64-pc-windows-msvc19.44.35228"\n',
        )


class TcmPreflightTests(unittest.TestCase):
    def test_legacy_compatibility_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "legacy.tcm"
            _write_legacy(path)
            accepted = PREFLIGHT.preflight_tcm(path, allow_legacy=True)
            rejected = PREFLIGHT.preflight_tcm(path, allow_legacy=False)
            self.assertTrue(accepted.allowed)
            self.assertEqual(accepted.status, "legacy")
            self.assertFalse(rejected.allowed)
            self.assertEqual(rejected.status, "rejected")

    def test_invalid_archive_is_rejected_without_native_load(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "broken.tcm"
            path.write_bytes(b"not a zip")
            decision = PREFLIGHT.preflight_tcm(path)
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.status, "rejected")

    def test_manifest_failure_is_structured(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.tcm"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(CONTRACT.TCM_MANIFEST_NAME, "{}")
                archive.writestr("kernel.ll", b"llvm")
            decision = PREFLIGHT.preflight_tcm(path)
            self.assertFalse(decision.allowed)
            self.assertIn("magic", decision.reason)

    def test_legacy_cuda_host_payload_is_rejected_before_load(self) -> None:
        """A CUDA target must not accept a legacy archive containing host IR."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sfm_registration_cuda.tcm"
            _write_legacy_cuda_with_host_ir(path)
            decision = PREFLIGHT.preflight_tcm(
                path,
                requested_target={
                    "backend": "cuda",
                    "os": "windows",
                    "arch": "x86_64",
                    "vendor": "nvidia",
                },
            )
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.status, "rejected")
            self.assertIn("expected NVPTX LLVM triple", decision.reason)

    def test_legacy_cpu_windows_payload_is_rejected_for_linux_target(self) -> None:
        """A CPU archive must not cross the OS target boundary by filename."""

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "gaussian_cpu.tcm"
            _write_legacy_cpu_windows_ir(path)
            decision = PREFLIGHT.preflight_tcm(
                path,
                requested_target={
                    "backend": "cpu",
                    "os": "linux",
                    "arch": "x86_64",
                },
            )
            self.assertFalse(decision.allowed)
            self.assertEqual(decision.status, "rejected")
            self.assertIn("expected Linux LLVM triple", decision.reason)


if __name__ == "__main__":
    unittest.main()
