"""Cross-compile target-qualified AOT bridges for ARM64 Android/Linux.

The CPU profile disables OpenGL interop; Vulkan/OpenGL/GLES profiles keep only
their selected graphics ABI. All profiles keep the exported C ABI used by the
Python engine. Android and Linux profiles link the matching target
``libtaichi_c_api.so`` when available; Linux leaves only its target libc/libm
dependencies for the target distribution to resolve.

No host desktop DLL is touched.  Android/Linux builds link and package the
matching ARM64 C API library when it is present.  This remains a cross-build
gate; execution still requires an ARM64 device or emulator.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

try:  # direct script execution and package imports are both supported
    from .arm64_toolchain_preflight import preflight_arm64_toolchain
except ImportError:  # pragma: no cover - exercised by ``python build_*.py``
    from arm64_toolchain_preflight import preflight_arm64_toolchain


ROOT = Path(__file__).resolve().parents[3]
TAICHI_ROOT = ROOT / "test_algorithm" / "taichi_upstream" / "stable-v1.7.4-development"
SOURCE = (
    ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "taichi_aot_engine.cpp"
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
DEFAULT_ANDROID_API = int(os.environ.get("PIXEL_REFINE_ANDROID_API", "26"))


def android_clang(api_level: int) -> Path:
    return NDK_PREBUILT / "bin" / f"aarch64-linux-android{int(api_level)}-clang++.cmd"


ANDROID_CLANG = android_clang(DEFAULT_ANDROID_API)


def default_llvm_readobj() -> Path | None:
    """Return the pinned LLVM20 inspection tool, if installed."""

    pinned = (
        ROOT
        / "test_algorithm"
        / "llvm_msvc_dev_extract"
        / "clang+llvm-20.1.5-x86_64-pc-windows-msvc"
        / "bin"
        / "llvm-readobj.exe"
    )
    if pinned.is_file():
        return pinned
    return None


LINUX_CLANG = NDK_PREBUILT / "bin" / "clang++.exe"
GNU_AARCH64_CXX = (
    ROOT
    / "test_algorithm"
    / "arm_gnu_toolchain_extract"
    / "bin"
    / "aarch64-none-linux-gnu-g++.exe"
)
GNU_AARCH64_SYSROOT = (
    ROOT
    / "test_algorithm"
    / "arm_gnu_toolchain_extract"
    / "aarch64-none-linux-gnu"
    / "libc"
)
SYSROOT = NDK_PREBUILT / "sysroot"
CXX_INCLUDE = SYSROOT / "usr" / "include" / "c++" / "v1"
ARCH_INCLUDE = SYSROOT / "usr" / "include" / "aarch64-linux-android"
GLAD_INCLUDE = TAICHI_ROOT / "external" / "glad" / "include"
API_INCLUDE = TAICHI_ROOT / "c_api" / "include"

PROFILES = {
    "cpu_arm64_android": {
        "backend": "cpu",
        "triple": "aarch64-linux-android26",
        "minimum_api": 26,
        "clang": ANDROID_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "cpu_arm64_android"
        / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "cpu_arm64_android"
        / "out"
        / "libtaichi_c_api.so",
    },
    "cpu_arm64_linux": {
        "backend": "cpu",
        "triple": "aarch64-unknown-linux-gnu",
        "clang": LINUX_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "cpu_arm64_linux"
        / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "cpu_arm64_linux"
        / "out"
        / "libtaichi_c_api.so",
    },
    "opengl_arm64_linux": {
        "backend": "opengl",
        "triple": "aarch64-unknown-linux-gnu",
        # Prefer a real glibc cross compiler when it is vendored.  The NDK
        # clang fallback is still accepted via --clang for environments that
        # provide a Linux sysroot separately.
        "clang": GNU_AARCH64_CXX if GNU_AARCH64_CXX.exists() else LINUX_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "opengl_arm64_linux"
        / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "opengl_arm64_linux"
        / "out"
        / "libtaichi_c_api.so",
        "sysroot": GNU_AARCH64_SYSROOT,
    },
    "gles_arm64_linux": {
        "backend": "gles",
        "triple": "aarch64-unknown-linux-gnu",
        "clang": GNU_AARCH64_CXX if GNU_AARCH64_CXX.exists() else LINUX_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "gles_arm64_linux"
        / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "gles_arm64_linux"
        / "out"
        / "libtaichi_c_api.so",
        "sysroot": GNU_AARCH64_SYSROOT,
    },
    "vulkan_arm64_android": {
        "backend": "vulkan",
        "triple": "aarch64-linux-android26",
        "minimum_api": 26,
        "clang": ANDROID_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "vulkan_arm64_android"
        / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "vulkan_arm64_android"
        / "out"
        / "libtaichi_c_api.so",
    },
    "gles_arm64_android": {
        "backend": "gles",
        "triple": "aarch64-linux-android26",
        "minimum_api": 26,
        "clang": ANDROID_CLANG,
        "output": ROOT
        / "taichi_vision"
        / "taichi_algorithm"
        / "aot_py"
        / "aot_dll"
        / "gles_arm64_android"
        / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT
        / "test_algorithm"
        / "aot_targets"
        / "build"
        / "gles_arm64_android"
        / "out"
        / "libtaichi_c_api.so",
    },
}


def _check_architecture(path: Path, llvm_readobj: Path | None) -> None:
    if llvm_readobj is None:
        return
    result = subprocess.run(
        [str(llvm_readobj), "--file-header", str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    text = result.stdout + result.stderr
    if (
        result.returncode
        or "elf64-littleaarch64" not in text
        or "EM_AARCH64" not in text
    ):
        raise RuntimeError(
            f"bridge is not an ELF AArch64 shared object: {text[-1000:]}"
        )


def _is_gnu_cross_compiler(path: Path) -> bool:
    """Return whether *path* is a GNU AArch64 driver rather than clang.

    The Android ``.cmd`` wrapper and standalone clang both accept
    ``--target=``.  GCC drivers already encode their target in the executable
    name and reject that option, so the command line must be assembled
    separately.  Keeping this detection local to the bridge builder avoids
    relabeling a host compiler as an ARM binary.
    """

    name = path.name.lower()
    return "aarch64-none-linux-gnu-g++" in name or "aarch64-linux-gnu-g++" in name


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", choices=sorted(PROFILES), default="cpu_arm64_android"
    )
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--clang", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--api-level", type=int, default=DEFAULT_ANDROID_API)
    parser.add_argument(
        "--llvm-readobj",
        type=Path,
        default=default_llvm_readobj(),
    )
    args = parser.parse_args()

    profile = PROFILES[args.target]
    if args.target.endswith("_android") and args.api_level < int(profile.get("minimum_api", 1)):
        raise SystemExit(
            f"{args.target} requires Android API {profile['minimum_api']} or newer"
        )
    source = args.source.resolve()
    default_clang = (
        android_clang(args.api_level)
        if args.target.endswith("_android")
        else profile["clang"]
    )
    clang = (args.clang or default_clang).resolve()
    output = (args.output or profile["output"]).resolve()
    readobj = args.llvm_readobj.resolve() if args.llvm_readobj else None
    for path, label in (
        (source, "bridge source"),
        (clang, "AArch64 clang++"),
        (API_INCLUDE, "Taichi C API headers"),
        (TAICHI_ROOT, "Taichi root"),
    ):
        if not path.exists():
            raise SystemExit(f"{label} does not exist: {path}")

    if args.target == "cpu_arm64_linux":
        for path, label in (
            (SYSROOT, "sysroot"),
            (CXX_INCLUDE, "libc++ include"),
            (ARCH_INCLUDE, "AArch64 sysroot include"),
        ):
            if not path.exists():
                raise SystemExit(f"{label} does not exist: {path}")

    target_name = (
        f"{args.target}_api{args.api_level}"
        if args.target.endswith("_android")
        else args.target
    )
    target_triple = (
        f"aarch64-linux-android{args.api_level}"
        if args.target.endswith("_android")
        else profile["triple"]
    )
    gnu_cross = _is_gnu_cross_compiler(clang)
    explicit_target_args = (
        () if clang.suffix.lower() == ".cmd" or gnu_cross else (f"--target={target_triple}",)
    )
    # Android standalone clang uses the NDK sysroot.  Linux graphics profiles
    # retain their profile-specific glibc sysroot; never silently substitute
    # an Android sysroot for a Linux ABI.
    host_clang_sysroot = (
        SYSROOT
        if args.target.endswith("_android") or args.target == "cpu_arm64_linux"
        else profile.get("sysroot")
    )
    report = preflight_arm64_toolchain(
        target_name,
        clang,
        sysroot=(host_clang_sysroot if args.target == "cpu_arm64_linux" or explicit_target_args else profile.get("sysroot")),
        cxx_include=(CXX_INCLUDE if args.target == "cpu_arm64_linux" or explicit_target_args else None),
        arch_include=(ARCH_INCLUDE if args.target == "cpu_arm64_linux" else None),
        target_args=explicit_target_args,
    )
    if not report.ok:
        raise SystemExit(
            "ARM64 LLVM20 toolchain preflight failed: "
            + "; ".join(report.diagnostics)
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    runtime_lib = profile.get("runtime_lib")
    if runtime_lib is not None:
        runtime_lib = Path(runtime_lib).resolve()
        if not runtime_lib.is_file():
            raise SystemExit(
                f"matching ARM64 Taichi C API runtime does not exist: {runtime_lib}"
            )
    with tempfile.TemporaryDirectory(prefix="arm64-bridge-", dir=output.parent) as temp:
        staging = Path(temp) / output.name
        command = [str(clang)]
        if not gnu_cross:
            command.append("--target=" + target_triple)
        command.extend(
            [
                "-shared",
                "-fPIC",
                # The bridge contains hand-written NEON conversion loops; O3 lets
                # LLVM optimize the scalar tails and surrounding ABI glue without
                # enabling fast-math or narrowing the ARMv8 compatibility floor.
                "-O3",
                "-std=c++20",
                "-march=armv8-a+simd",
                "-mtune=generic",
                "-I",
                str(API_INCLUDE),
                "-I",
                str(TAICHI_ROOT),
                "-I",
                str(GLAD_INCLUDE),
                str(source),
                "-Wl,--allow-shlib-undefined",
                "-Wl,-soname,taichi_aot_engine.so",
                "-o",
                str(staging),
            ]
        )
        if gnu_cross and target_triple.endswith("linux-gnu"):
            sysroot = Path(profile.get("sysroot", "")).resolve()
            if not sysroot.is_dir():
                raise SystemExit(
                    "GNU AArch64 compiler requires a Linux sysroot; "
                    f"not found: {sysroot}"
                )
            command[1:1] = ["--sysroot=" + str(sysroot)]
        if profile["backend"] == "cpu":
            command.insert(command.index("-I"), "-DAOT_DISABLE_OPENGL_INTEROP")
        if args.target == "cpu_arm64_linux" and not gnu_cross:
            command[1:1] = [
                "--sysroot=" + str(SYSROOT),
                "-stdlib=libc++",
                "-isystem",
                str(CXX_INCLUDE),
                "-isystem",
                str(ARCH_INCLUDE),
            ]
            # The Windows-hosted NDK does not ship glibc startup objects for
            # the GNU Linux triple.  Produce a relocatable shared object with
            # unresolved libc/libc++ symbols; the actual Linux toolchain and
            # Taichi C-API runtime resolve them during packaging on the ARM
            # target.  Android uses the NDK CRT and does not take this path.
        elif explicit_target_args:
            command[1:1] = [
                *explicit_target_args,
                "--sysroot=" + str(host_clang_sysroot),
                "-stdlib=libc++",
                "-isystem",
                str(CXX_INCLUDE),
            ]
            command[2:2] = ["-nostdlib", "-nostartfiles", "-nodefaultlibs"]
            if runtime_lib is not None:
                # The cross-linked C API supplies the Taichi symbols while
                # libc/libm remain target-side dependencies of that shared
                # object.  Keep the bridge relocatable and discover the
                # sibling runtime at package load time.
                command.extend([str(runtime_lib), "-Wl,-rpath,${ORIGIN}"])
        elif runtime_lib is not None:
            # The C API shared object has a stable SONAME.  Link against the
            # exact target build and make the sibling dependency discoverable
            # in an Android app's native library directory.
            command.extend([str(runtime_lib), "-Wl,-rpath,${ORIGIN}"])
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            shell=bool(profile["shell"]),
        )
        if result.returncode:
            raise RuntimeError((result.stdout + result.stderr).strip())
        if not staging.exists() or staging.stat().st_size < 64 * 1024:
            raise RuntimeError(
                "clang produced an empty or implausibly small ARM64 bridge"
            )
        _check_architecture(staging, readobj if readobj and readobj.exists() else None)
        staging.replace(output)

    if runtime_lib is not None:
        packaged_runtime = output.parent / runtime_lib.name
        if runtime_lib.resolve() != packaged_runtime.resolve():
            shutil.copy2(runtime_lib, packaged_runtime)
    suffix = f", linked={runtime_lib.name}" if runtime_lib is not None else ""
    print(
        f"[PASS] {output} ({output.stat().st_size} bytes, "
        f"triple={target_triple}{suffix}, qualification=compile_only, "
        "native_runtime=False)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
