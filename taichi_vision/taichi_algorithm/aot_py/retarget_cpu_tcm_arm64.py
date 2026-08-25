"""Produce a *validated experimental* AArch64 CPU TCM set.

Taichi 1.7.4's Python wheel emits CPU LLVM IR for the host triple.  On an
x86_64 Windows worker ``ti.arm64`` silently falls back to x64, so copying
those archives into an ARM directory would be an invalid artifact.  This
tool performs the narrow, reproducible part that can be done off-device:

* rewrite the target triple/data layout in the textual LLVM kernels;
* remove host-only LLVM metadata that crashes AArch64 lowering;
* parse every rewritten kernel with the Android NDK AArch64 LLVM frontend;
* keep ``graphs.tcb`` and graph names unchanged;
* promote atomically only after every archive passes validation.

This is intentionally labelled experimental.  Running the kernels still
requires an ARM64 Taichi runtime containing a matching ``runtime_arm64.bc``;
the companion ``build_arm64_runtime.py`` creates that runtime bitcode.
Use ``validate_arm_tcm_codegen.py`` to additionally lower all kernels to
AArch64 objects with an external LLVM toolchain.
The script never overwrites the x86_64 artifacts.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile

try:
    from .aot_artifact import normalize_tcm
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from aot_artifact import normalize_tcm


ROOT = Path(__file__).resolve().parents[3]
TCM_ROOT = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
ARM_DATALAYOUT = (
    "e-m:e-p270:32:32-p271:32:32-p272:64:64-i8:8:32-i16:16:32-"
    "i64:64-i128:128-n32:64-S128-Fn32"
)
TRIPLES = {
    "cpu_arm64_android": "aarch64-unknown-linux-android26",
    "cpu_arm64_linux": "aarch64-unknown-linux-gnu",
}

DEFAULT_ANDROID_API = int(os.environ.get("PIXEL_REFINE_ANDROID_API", "26"))


def _rewrite_ir(payload: bytes, triple: str) -> bytes:
    text = payload.decode("utf-8")
    if "target triple =" not in text or "target datalayout =" not in text:
        raise ValueError("LLVM kernel is missing target metadata")
    text = re.sub(
        r'target datalayout = "[^"]+"',
        f'target datalayout = "{ARM_DATALAYOUT}"',
        text,
        count=1,
    )
    text = re.sub(
        r'target triple = "[^"]+"',
        f'target triple = "{triple}"',
        text,
        count=1,
    )
    if triple.startswith("aarch64-"):
        # The host compiler bakes x86-64 CPU attributes into every function
        # even when the IR body itself is generic.  Leaving those attributes
        # in an ARM archive can make an ARM LLVM target reject the module or
        # silently disable vector code generation.  AArch64 Android devices
        # all provide the NEON/FP baseline; the runtime may still specialize
        # further when it JITs the graph on the actual CPU.
        text = re.sub(r'"target-cpu"="[^"]+"', '"target-cpu"="generic"', text)
        text = re.sub(r'"target-features"="[^"]+"', '"target-features"="+neon"', text)
        # A small number of host kernels have an attribute group without any
        # CPU feature annotation.  Leave optimization/ABI attributes intact,
        # but make the AArch64 baseline explicit so the runtime can use NEON
        # consistently instead of silently selecting a feature-less scalar
        # path.  AArch64 NEON is mandatory on Android arm64-v8a and Linux
        # arm64, so this does not narrow the supported CPU set.
        def _add_arm_features(match: re.Match[str]) -> str:
            group, attrs = match.group(1), match.group(2)
            if "target-features" in attrs:
                return match.group(0)
            return (
                f'attributes #{group} = {{{attrs}'
                ' "target-cpu"="generic" "target-features"="+neon"}'
            )

        text = re.sub(
            r'^attributes #(\d+) = \{([^}]*)\}$',
            _add_arm_features,
            text,
            flags=re.MULTILINE,
        )

        # Taichi's host CPU IR carries LLVM 15 Windows module/debug metadata
        # which is harmless for the AOT graph but triggers an LLVM 14/20
        # AArch64 code-generation crash (0xC000001D) when the module is
        # lowered to an object file.  Graph names and arguments live in
        # ``graphs.tcb``; this metadata is not required by the Taichi runtime,
        # so remove only metadata attachments/definitions for the ARM copy.
        # Keeping the host archive untouched preserves x86 debug information.
        text = re.sub(
            r', !(?:llvm\.[A-Za-z0-9_.-]+|[A-Za-z0-9_.-]+) !\d+',
            '',
            text,
        )
        text = re.sub(r'^![0-9]+ = .*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'^!llvm\.[^\n]+\n?', '', text, flags=re.MULTILINE)
    return text.encode("utf-8")


def _validate_ir(path: Path, clang: Path, triple: str, out_dir: Path) -> None:
    output = out_dir / (path.stem + ".bc")
    command = [
        "cmd",
        "/c",
        str(clang),
        "-x",
        "ir",
        str(path),
        "-target",
        triple,
        "-c",
        "-emit-llvm",
        "-o",
        str(output),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()[-2000:]
        raise RuntimeError(f"AArch64 LLVM validation failed for {path.name}: {detail}")


def _retarget_archive(source: Path, destination: Path, clang: Path, triple: str) -> int:
    with zipfile.ZipFile(source, "r") as archive:
        entries = {item.filename: archive.read(item) for item in archive.infolist()}
    if "graphs.tcb" not in entries or "__version__" not in entries:
        raise ValueError(f"{source.name} is not a CPU LLVM/TBC archive")
    ir_names = [name for name in entries if name.endswith(".ll")]
    if not ir_names:
        raise ValueError(f"{source.name} contains no textual LLVM kernels")

    with tempfile.TemporaryDirectory(prefix="arm64-ir-") as temp:
        temp_dir = Path(temp)
        for name in ir_names:
            rewritten = _rewrite_ir(entries[name], triple)
            ir_path = temp_dir / Path(name).name
            ir_path.write_bytes(rewritten)
            _validate_ir(ir_path, clang, triple, temp_dir)
            entries[name] = rewritten

    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_suffix(".staging.tcm")
    if staging.exists():
        staging.unlink()
    with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as output:
        for name in sorted(entries):
            output.writestr(name, entries[name])
    staging.replace(destination)
    normalize_tcm(destination)
    return len(ir_names)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=sorted(TRIPLES),
        default="cpu_arm64_android",
        help="ARM target triple/profile to generate",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=TCM_ROOT / "cpu_x86_64_windows",
        help="validated host CPU TCM directory",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="target directory (defaults to aot_tcm/<target>)",
    )
    parser.add_argument(
        "--clang",
        type=Path,
        default=None,
        help="AArch64 clang wrapper used for textual IR validation",
    )
    parser.add_argument("--api-level", type=int, default=DEFAULT_ANDROID_API)
    parser.add_argument("--limit", type=int, default=0, help="validate only the first N archives")
    args = parser.parse_args()

    source = args.source.resolve()
    output = (args.output or TCM_ROOT / args.target).resolve()
    clang = (
        args.clang
        or ROOT
        / "test_algorithm"
        / "android_ndk_extract"
        / "android-ndk-r25c"
        / "toolchains"
        / "llvm"
        / "prebuilt"
        / "windows-x86_64"
        / "bin"
        / f"aarch64-linux-android{args.api_level}-clang.cmd"
    ).resolve()
    if args.target == "cpu_arm64_android" and args.api_level < 26:
        raise SystemExit("ARM Android retargeting requires API26 or newer")
    if not source.is_dir():
        raise SystemExit(f"source directory does not exist: {source}")
    if not clang.exists():
        raise SystemExit(f"AArch64 clang wrapper does not exist: {clang}")
    version_command = (
        str(clang) + " --version"
        if clang.suffix.lower() == ".cmd"
        else [str(clang), "--version"]
    )
    version_result = subprocess.run(
        version_command,
        capture_output=True,
        text=True,
        check=False,
        shell=clang.suffix.lower() == ".cmd",
    )
    version_match = re.search(
        r"(?:clang version|clang)\s+(\d+)",
        version_result.stdout + version_result.stderr,
        re.IGNORECASE,
    )
    if version_match is None or int(version_match.group(1)) != 20:
        raise SystemExit(
            "ARM TCM retargeting requires LLVM/Clang 20; legacy NDK LLVM14 "
            "must not be mixed with LLVM20 runtime bitcode"
        )
    archives = sorted(source.glob("*.tcm"))
    if args.limit > 0:
        archives = archives[: args.limit]
    if not archives:
        raise SystemExit(f"no .tcm archives found in {source}")

    output.mkdir(parents=True, exist_ok=True)
    triple = (
        f"aarch64-unknown-linux-android{args.api_level}"
        if args.target == "cpu_arm64_android"
        else TRIPLES[args.target]
    )
    total_ir = 0
    for index, archive in enumerate(archives, 1):
        destination = output / f"{archive.stem.rsplit('_cpu_x86_64_windows', 1)[0]}_{args.target}.tcm"
        count = _retarget_archive(archive, destination, clang, triple)
        total_ir += count
        print(f"[{index}/{len(archives)}] {destination.name}: {count} LLVM kernels validated")
    print(f"[PASS] {len(archives)} ARM64 archives, {total_ir} LLVM kernels; target={triple}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
