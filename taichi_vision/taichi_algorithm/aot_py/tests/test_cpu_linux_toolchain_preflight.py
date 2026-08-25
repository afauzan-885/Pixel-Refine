"""Deterministic, side-effect-free CPU Linux toolchain gate tests."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from taichi_vision.taichi_algorithm.aot_py.cpu_linux_toolchain_preflight import (
    preflight_cpu_linux_toolchain,
)


class _Result:
    def __init__(self, text: str, returncode: int = 0):
        self.stdout = text
        self.stderr = ""
        self.returncode = returncode


class CpuLinuxToolchainPreflightTests(unittest.TestCase):
    def _runner(self, command, **_kwargs):
        args = " ".join(command)
        if "--version" in args:
            return _Result("clang version 20.1.5 (LLVM)\n")
        return _Result("x86_64-unknown-linux-gnu\n")

    def test_valid_linux_sysroot_is_accepted(self):
        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang"
            compiler.write_text("placeholder", encoding="utf-8")
            sysroot = Path(root) / "sysroot"
            (sysroot / "usr" / "include").mkdir(parents=True)
            (sysroot / "usr" / "lib").mkdir(parents=True)
            for name in ("crt1.o", "crti.o", "crtn.o"):
                (sysroot / "usr" / "lib" / name).touch()
            report = preflight_cpu_linux_toolchain(
                compiler, sysroot=sysroot, host_platform="win32", runner=self._runner
            )
        self.assertTrue(report.ok)
        self.assertTrue(report.link_inputs_ok)
        self.assertEqual(report.reported_target, "x86_64-unknown-linux-gnu")

    def test_windows_clang_target_is_rejected_even_with_linux_name(self):
        def runner(command, **_kwargs):
            args = " ".join(command)
            if "--version" in args:
                return _Result("clang version 20.1.5\n")
            return _Result("x86_64-pc-windows-msvc\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_cpu_linux_toolchain(
                compiler, host_platform="win32", runner=runner
            )
        self.assertFalse(report.ok)
        self.assertFalse(report.target_ok)
        self.assertTrue(any("not compatible" in item for item in report.diagnostics))

    def test_missing_sysroot_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_cpu_linux_toolchain(
                compiler,
                sysroot=Path(root) / "missing-sysroot",
                runner=self._runner,
            )
        self.assertFalse(report.ok)
        self.assertTrue(any("sysroot does not exist" in item for item in report.diagnostics))

    def test_no_sysroot_requires_linux_worker(self):
        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_cpu_linux_toolchain(
                compiler, host_platform="win32", runner=self._runner
            )
        self.assertFalse(report.ok)
        self.assertTrue(any("required on a non-Linux host" in item for item in report.diagnostics))


if __name__ == "__main__":
    unittest.main()
