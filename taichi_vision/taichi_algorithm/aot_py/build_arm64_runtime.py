"""Build the ARM64 LLVM runtime bitcode used by CPU ARM AOT artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import os
import re
import subprocess
import tempfile

try:  # direct script execution and package imports are both supported
    from .arm64_toolchain_preflight import preflight_arm64_toolchain
except ImportError:  # pragma: no cover - exercised by ``python build_*.py``
    from arm64_toolchain_preflight import preflight_arm64_toolchain


ROOT = Path(__file__).resolve().parents[3]
RUNTIME_SOURCE = (
    ROOT
    / "test_algorithm"
    / "taichi_upstream"
    / "stable-v1.7.4-development"
    / "taichi"
    / "runtime"
    / "llvm"
    / "runtime_module"
    / "runtime.cpp"
)
NDK_PREBUILT = (
    ROOT
    / "test_algorithm"
    / "android_ndk_extract"
    / "android-ndk-r25c"
    / "toolchains"
    / "llvm"
    / "prebuilt"
    / "windows-x86_64"
)


def android_clang(api_level: int) -> Path:
    return NDK_PREBUILT / "bin" / f"aarch64-linux-android{int(api_level)}-clang.cmd"


DEFAULT_ANDROID_API = int(os.environ.get("PIXEL_REFINE_ANDROID_API", "26"))
DEFAULT_CLANG = android_clang(DEFAULT_ANDROID_API)
DEFAULT_OUTPUT = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "cpu_arm64_android" / "runtime_arm64_android.bc"
TARGET_PROFILES = {
    "cpu_arm64_android": {
        "triple": lambda api: f"aarch64-unknown-linux-android{int(api)}",
        "clang": DEFAULT_CLANG,
        "output": DEFAULT_OUTPUT,
    },
    "cpu_arm64_linux": {
        "triple": lambda api: "aarch64-unknown-linux-gnu",
        # The Android clang wrapper hard-codes an Android target.  Use the
        # underlying clang executable for the Linux profile and supply the
        # NDK libc++/sysroot include paths explicitly.  This still produces
        # portable LLVM bitcode; linking against a Linux libc happens on the
        # target device/toolchain, not during AOT archive generation.
        "clang": NDK_PREBUILT / "bin" / "clang.exe",
        "output": ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "cpu_arm64_linux" / "runtime_arm64_linux.bc",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=sorted(TARGET_PROFILES),
        default="cpu_arm64_android",
        help="ARM64 runtime profile to build",
    )
    parser.add_argument("--clang", type=Path, default=None)
    parser.add_argument("--source", type=Path, default=RUNTIME_SOURCE)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--api-level", type=int, default=DEFAULT_ANDROID_API)
    parser.add_argument(
        "--sysroot",
        type=Path,
        default=NDK_PREBUILT / "sysroot",
        help="sysroot used by the Linux profile",
    )
    parser.add_argument(
        "--cxx-include",
        type=Path,
        default=NDK_PREBUILT / "sysroot" / "usr" / "include" / "c++" / "v1",
        help="libc++ headers used by the Linux profile",
    )
    args = parser.parse_args()

    profile = TARGET_PROFILES[args.target]
    # Preserve the historical Android CLI while selecting sensible defaults
    # for the new Linux profile.  Explicit --clang/--output always win.
    clang_arg = args.clang
    if clang_arg is None:
        clang_arg = android_clang(args.api_level) if args.target == "cpu_arm64_android" else profile["clang"]
    clang = clang_arg.resolve()
    source = args.source.resolve()
    output = (args.output or profile["output"]).resolve()
    if not clang.exists():
        raise SystemExit(f"AArch64 clang tool does not exist: {clang}")
    if not source.exists():
        raise SystemExit(f"Taichi runtime source does not exist: {source}")

    if args.target == "cpu_arm64_android" and args.api_level < 26:
        raise SystemExit("LLVM20 ARM Android profile requires Android API 26 or newer")

    target_name = (
        f"{args.target}_api{args.api_level}"
        if args.target.endswith("_android")
        else args.target
    )
    triple = profile["triple"](args.api_level)
    # NDK .cmd wrappers already encode the target.  A standalone LLVM20 host
    # clang needs an explicit target during both preflight and compilation;
    # the response is still checked against the strict profile triple.
    explicit_target_args = () if clang.suffix.lower() == ".cmd" else (f"--target={triple}",)
    report = preflight_arm64_toolchain(
        target_name,
        clang,
        sysroot=(args.sysroot if args.target == "cpu_arm64_linux" or explicit_target_args else None),
        cxx_include=(args.cxx_include if args.target == "cpu_arm64_linux" or explicit_target_args else None),
        arch_include=(
            args.sysroot / "usr" / "include" / "aarch64-linux-android"
            if args.target == "cpu_arm64_linux"
            else None
        ),
        target_args=explicit_target_args,
    )
    if not report.ok:
        raise SystemExit(
            "ARM64 LLVM20 toolchain preflight failed: "
            + "; ".join(report.diagnostics)
        )

    include_root = ROOT / "test_algorithm" / "taichi_upstream" / "stable-v1.7.4-development"
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="arm64-runtime-", dir=output.parent) as temp:
        staging = Path(temp) / output.name
        # The NDK distributes a small ``.cmd`` wrapper.  ``shell=True`` lets
        # Windows resolve that wrapper while preserving quoted paths.
        command = [
            str(clang),
            "-c",
            str(source),
            "-o",
            str(staging),
            "-fno-exceptions",
            "-emit-llvm",
            "-std=c++17",
            "-DARCH_arm64",
            "-I",
            str(include_root),
            # ARMv8-A mandates the SIMD/NEON extension for the supported
            # arm64 profiles.  Make it explicit in the runtime bitcode while
            # keeping the CPU baseline generic for broad device coverage.
            "-march=armv8-a+simd",
            "-mtune=generic",
        ]
        if args.target == "cpu_arm64_linux":
            sysroot = args.sysroot.resolve()
            cxx_include = args.cxx_include.resolve()
            arch_include = sysroot / "usr" / "include" / "aarch64-linux-android"
            for path, label in (
                (sysroot, "sysroot"),
                (cxx_include, "libc++ include"),
                (arch_include, "AArch64 sysroot include"),
            ):
                if not path.exists():
                    raise SystemExit(f"{label} does not exist: {path}")
            command[1:1] = [
                "--target=aarch64-unknown-linux-gnu",
                f"--sysroot={sysroot}",
                "-stdlib=libc++",
                "-isystem",
                str(cxx_include),
                "-isystem",
                str(arch_include),
            ]
        elif explicit_target_args:
            # A standalone LLVM20 clang does not inherit the NDK wrapper's
            # target/sysroot settings.  Keep those settings explicit and
            # identical to the preflight contract.
            command[1:1] = [
                *explicit_target_args,
                f"--sysroot={args.sysroot.resolve()}",
                "-stdlib=libc++",
                "-isystem",
                str(args.cxx_include.resolve()),
            ]
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            # .cmd wrappers need cmd.exe; the Linux profile uses clang.exe
            # directly and therefore remains shell-free.
            shell=clang.suffix.lower() == ".cmd",
        )
        if result.returncode:
            raise RuntimeError((result.stdout + result.stderr).strip())
        if not staging.exists() or staging.stat().st_size < 4096:
            raise RuntimeError("clang produced an empty or implausibly small runtime bitcode")
        # LLVM bitcode is intentionally not disassembled/re-serialized here:
        # the LLVM20 compiler and ARM Taichi runtime must consume the same
        # major-version bitcode contract.
        staging.replace(output)

    print(f"[PASS] {output} ({output.stat().st_size} bytes, triple={triple})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
