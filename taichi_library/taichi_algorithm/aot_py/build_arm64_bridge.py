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
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[3]
TAICHI_ROOT = ROOT / "test_algorithm" / "taichi_upstream" / "stable-v1.7.4-development"
SOURCE = ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "taichi_aot_engine.cpp"
NDK_PREBUILT = ROOT / "test_algorithm" / "android_ndk_extract" / "android-ndk-r25c" / "toolchains" / "llvm" / "prebuilt" / "windows-x86_64"
ANDROID_CLANG = NDK_PREBUILT / "bin" / "aarch64-linux-android21-clang++.cmd"
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
        "triple": "aarch64-linux-android21",
        "clang": ANDROID_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "cpu_arm64_android" / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "cpu_arm64_android" / "out" / "libtaichi_c_api.so",
    },
    "cpu_arm64_linux": {
        "backend": "cpu",
        "triple": "aarch64-unknown-linux-gnu",
        "clang": LINUX_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "cpu_arm64_linux" / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "cpu_arm64_linux" / "out" / "libtaichi_c_api.so",
    },
    "opengl_arm64_linux": {
        "backend": "opengl",
        "triple": "aarch64-unknown-linux-gnu",
        # Prefer a real glibc cross compiler when it is vendored.  The NDK
        # clang fallback is still accepted via --clang for environments that
        # provide a Linux sysroot separately.
        "clang": GNU_AARCH64_CXX if GNU_AARCH64_CXX.exists() else LINUX_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "opengl_arm64_linux" / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "opengl_arm64_linux" / "out" / "libtaichi_c_api.so",
        "sysroot": GNU_AARCH64_SYSROOT,
    },
    "gles_arm64_linux": {
        "backend": "gles",
        "triple": "aarch64-unknown-linux-gnu",
        "clang": GNU_AARCH64_CXX if GNU_AARCH64_CXX.exists() else LINUX_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "gles_arm64_linux" / "taichi_aot_engine.so",
        "shell": False,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "gles_arm64_linux" / "out" / "libtaichi_c_api.so",
        "sysroot": GNU_AARCH64_SYSROOT,
    },
    "vulkan_arm64_android": {
        "backend": "vulkan",
        "triple": "aarch64-linux-android21",
        "clang": ANDROID_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "vulkan_arm64_android" / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "vulkan_arm64_android" / "out" / "libtaichi_c_api.so",
    },
    "gles_arm64_android": {
        "backend": "gles",
        "triple": "aarch64-linux-android21",
        "clang": ANDROID_CLANG,
        "output": ROOT / "taichi_library" / "taichi_algorithm" / "aot_py" / "aot_dll" / "gles_arm64_android" / "taichi_aot_engine.so",
        "shell": True,
        "runtime_lib": ROOT / "test_algorithm" / "aot_targets" / "build" / "gles_arm64_android" / "out" / "libtaichi_c_api.so",
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
    if result.returncode or "elf64-littleaarch64" not in text or "EM_AARCH64" not in text:
        raise RuntimeError(f"bridge is not an ELF AArch64 shared object: {text[-1000:]}")


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
    parser.add_argument("--target", choices=sorted(PROFILES), default="cpu_arm64_android")
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--clang", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--llvm-readobj", type=Path, default=Path(r"C:\msys64\ucrt64\bin\llvm-readobj.exe"))
    args = parser.parse_args()

    profile = PROFILES[args.target]
    source = args.source.resolve()
    clang = (args.clang or profile["clang"]).resolve()
    output = (args.output or profile["output"]).resolve()
    readobj = args.llvm_readobj.resolve() if args.llvm_readobj else None
    for path, label in ((source, "bridge source"), (clang, "AArch64 clang++"), (API_INCLUDE, "Taichi C API headers"), (TAICHI_ROOT, "Taichi root")):
        if not path.exists():
            raise SystemExit(f"{label} does not exist: {path}")
    if args.target == "cpu_arm64_linux":
        for path, label in ((SYSROOT, "sysroot"), (CXX_INCLUDE, "libc++ include"), (ARCH_INCLUDE, "AArch64 sysroot include")):
            if not path.exists():
                raise SystemExit(f"{label} does not exist: {path}")

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
        gnu_cross = _is_gnu_cross_compiler(clang)
        command = [str(clang)]
        if not gnu_cross:
            command.append("--target=" + profile["triple"])
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
        if gnu_cross and profile["triple"].endswith("linux-gnu"):
            sysroot = Path(profile.get("sysroot", "")).resolve()
            if not sysroot.is_dir():
                raise SystemExit(
                    "GNU AArch64 compiler requires a Linux sysroot; "
                    f"not found: {sysroot}"
                )
            command[1:1] = ["--sysroot=" + str(sysroot)]
        if profile["backend"] == "cpu":
            command.insert(command.index("-I"), "-DPIXEL_REFINE_AOT_DISABLE_OPENGL_INTEROP")
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
            raise RuntimeError("clang produced an empty or implausibly small ARM64 bridge")
        _check_architecture(staging, readobj if readobj and readobj.exists() else None)
        staging.replace(output)

    if runtime_lib is not None:
        packaged_runtime = output.parent / runtime_lib.name
        if runtime_lib.resolve() != packaged_runtime.resolve():
            shutil.copy2(runtime_lib, packaged_runtime)
    suffix = f", linked={runtime_lib.name}" if runtime_lib is not None else ""
    print(
        f"[PASS] {output} ({output.stat().st_size} bytes, "
        f"triple={profile['triple']}{suffix})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
