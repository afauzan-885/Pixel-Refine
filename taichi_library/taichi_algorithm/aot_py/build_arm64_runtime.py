"""Build the ARM64 LLVM runtime bitcode used by CPU ARM AOT artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import tempfile


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
DEFAULT_CLANG = (
    ROOT
    / "test_algorithm"
    / "android_ndk_extract"
    / "android-ndk-r25c"
    / "toolchains"
    / "llvm"
    / "prebuilt"
    / "windows-x86_64"
    / "bin"
    / "aarch64-linux-android21-clang.cmd"
)
DEFAULT_OUTPUT = ROOT / "taichi_library" / "taichi_algorithm" / "aot_tcm" / "cpu_arm64_android" / "runtime_arm64_android.bc"
NDK_PREBUILT = ROOT / "test_algorithm" / "android_ndk_extract" / "android-ndk-r25c" / "toolchains" / "llvm" / "prebuilt" / "windows-x86_64"
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
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_tcm" / "cpu_arm64_linux" / "runtime_arm64_linux.bc",
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
    parser.add_argument("--clang", type=Path, default=DEFAULT_CLANG)
    parser.add_argument("--source", type=Path, default=RUNTIME_SOURCE)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--api-level", type=int, default=21)
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
    if clang_arg == DEFAULT_CLANG and args.target != "cpu_arm64_android":
        clang_arg = profile["clang"]
    clang = clang_arg.resolve()
    source = args.source.resolve()
    output = (args.output or profile["output"]).resolve()
    if not clang.exists():
        raise SystemExit(f"AArch64 clang tool does not exist: {clang}")
    if not source.exists():
        raise SystemExit(f"Taichi runtime source does not exist: {source}")

    triple = profile["triple"](args.api_level)
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
        # the NDK compiler's LLVM 14 format remains consumable by the matching
        # ARM Taichi runtime, whereas rewriting it with host LLVM 20 would
        # change the bitcode reader compatibility contract.
        staging.replace(output)

    print(f"[PASS] {output} ({output.stat().st_size} bytes, triple={triple})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
