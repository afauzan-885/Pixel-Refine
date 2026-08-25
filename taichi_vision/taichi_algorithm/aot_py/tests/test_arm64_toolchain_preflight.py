"""Read-only ARM64 LLVM20 toolchain discovery tests."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from taichi_vision.taichi_algorithm.aot_py.arm64_toolchain_preflight import (
    preflight_arm64_toolchain,
)


class _Result:
    def __init__(self, text: str, returncode: int = 0):
        self.stdout = text
        self.stderr = ""
        self.returncode = returncode


class Arm64ToolchainPreflightTests(unittest.TestCase):
    def _runner(self, command, **_kwargs):
        args = " ".join(command) if isinstance(command, list) else command
        if "--version" in args:
            return _Result("clang version 20.1.5 (LLVM)\n")
        if "-print-target-triple" in args:
            return _Result("aarch64-linux-android26\n")
        return _Result("", 1)

    def test_android_report_requires_llvm20_and_aarch64_target(self):
        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang.exe"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_arm64_toolchain(
                "cpu_arm64_android_api26",
                compiler,
                runner=self._runner,
            )
        self.assertTrue(report.ok)
        self.assertEqual(report.llvm_major, 20)
        self.assertEqual(report.requested_triple, "aarch64-linux-android26")
        self.assertEqual(report.reported_target, "aarch64-linux-android26")

    def test_android_accepts_vendor_qualified_clang_triple(self):
        """Clang may report the ABI-equivalent unknown-vendor triple."""

        def runner(command, **_kwargs):
            args = " ".join(command) if isinstance(command, list) else command
            if "--version" in args:
                return _Result("clang version 20.1.5 (LLVM)\n")
            return _Result("aarch64-unknown-linux-android26\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang.exe"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_arm64_toolchain(
                "cpu_arm64_android_api26", compiler, runner=runner
            )
        self.assertTrue(report.ok)
        self.assertEqual(report.reported_target, "aarch64-unknown-linux-android26")

    def test_host_clang_target_override_is_verified(self):
        """An LLVM20 host clang may be used only with an explicit target."""

        def runner(command, **_kwargs):
            args = " ".join(command) if isinstance(command, list) else command
            if "--version" in args:
                return _Result("clang version 20.1.5 (LLVM)\n")
            if "--target=aarch64-linux-android26" in args:
                return _Result("aarch64-unknown-linux-android26\n")
            return _Result("x86_64-pc-windows-msvc\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang.exe"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_arm64_toolchain(
                "cpu_arm64_android_api26",
                compiler,
                target_args=("--target=aarch64-linux-android26",),
                runner=runner,
            )
        self.assertTrue(report.ok)
        self.assertEqual(report.reported_target, "aarch64-unknown-linux-android26")

    def test_linux_accepts_gnu_triple_alias(self):
        def runner(command, **_kwargs):
            args = " ".join(command) if isinstance(command, list) else command
            if "--version" in args:
                return _Result("clang version 20.1.5\n")
            return _Result("aarch64-none-linux-gnu\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang"
            compiler.write_text("placeholder", encoding="utf-8")
            sysroot = Path(root) / "sysroot"
            sysroot.mkdir()
            report = preflight_arm64_toolchain(
                "cpu_arm64_linux", compiler, sysroot=sysroot, runner=runner
            )
        self.assertTrue(report.ok)
        self.assertEqual(report.reported_target, "aarch64-none-linux-gnu")

    def test_wrong_version_and_target_fail_closed(self):
        def runner(command, **_kwargs):
            args = " ".join(command) if isinstance(command, list) else command
            if "--version" in args:
                return _Result("clang version 14.0.6\n")
            return _Result("x86_64-pc-windows-msvc\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang.exe"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_arm64_toolchain(
                "cpu_arm64_android_api26", compiler, runner=runner
            )
        self.assertFalse(report.ok)
        self.assertEqual(report.llvm_major, 14)
        self.assertEqual(len(report.diagnostics), 2)

    def test_android_api_mismatch_fails_closed(self):
        """A lower Android sysroot must not satisfy a higher API profile."""

        def runner(command, **_kwargs):
            args = " ".join(command) if isinstance(command, list) else command
            if "--version" in args:
                return _Result("clang version 20.1.5\n")
            return _Result("aarch64-linux-android24\n")

        with tempfile.TemporaryDirectory() as root:
            compiler = Path(root) / "clang.exe"
            compiler.write_text("placeholder", encoding="utf-8")
            report = preflight_arm64_toolchain(
                "cpu_arm64_android_api26", compiler, runner=runner
            )
        self.assertFalse(report.ok)
        self.assertTrue(
            any("compiler target is not compatible with" in item for item in report.diagnostics)
        )

    def test_missing_compiler_does_not_probe_or_create_output(self):
        report = preflight_arm64_toolchain(
            "cpu_arm64_android_api26", "does-not-exist-clang.exe", runner=self._runner
        )
        self.assertFalse(report.ok)
        self.assertIn("compiler does not exist", report.diagnostics[0])


if __name__ == "__main__":
    unittest.main()
