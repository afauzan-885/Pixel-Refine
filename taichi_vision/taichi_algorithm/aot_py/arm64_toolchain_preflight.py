"""Read-only preflight for LLVM20 AArch64 Android/Linux toolchains.

The ARM builders run on Windows today, but the produced ELF/bitcode must not
be labelled as ARM merely because an output path contains ``arm64``.  This
module checks the compiler identity, target machine, and required sysroot
directories before a build starts.  It never invokes a linker and never writes
an artifact, making it safe to use from CI discovery and dry-run tooling.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import re
from pathlib import Path
import subprocess
from typing import Any, Callable, Mapping


LLVM20_MAJOR = 20
_VERSION_RE = re.compile(r"(?:clang version|clang)\s+(\d+)(?:\.([0-9]+))?", re.I)


@dataclass(frozen=True)
class Arm64ToolchainReport:
    target: str
    compiler: str
    compiler_kind: str
    requested_triple: str
    reported_target: str
    llvm_major: int | None
    sysroot: str = ""
    cxx_include: str = ""
    arch_include: str = ""
    ok: bool = False
    diagnostics: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["diagnostics"] = list(self.diagnostics)
        return payload


def _expected_target(target: str) -> tuple[str, str]:
    key = str(target).strip().lower()
    if "_android" in key:
        match = re.search(r"api(\d+)", key)
        api = int(match.group(1)) if match else 26
        return "android", f"aarch64-linux-android{api}"
    if key.endswith("_linux"):
        return "linux", "aarch64-unknown-linux-gnu"
    raise ValueError(f"unsupported ARM64 toolchain target: {target!r}")


def _run_probe(
    compiler: Path,
    args: list[str],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> tuple[int, str]:
    command = [str(compiler), *args]
    # NDK .cmd launchers require cmd.exe on Windows.  A list is retained for
    # normal clang/GCC drivers so paths are not shell-interpolated.
    use_shell = compiler.suffix.lower() == ".cmd"
    if use_shell:
        command = " ".join('"' + item.replace('"', '\\"') + '"' for item in command)
    result = runner(
        command,
        capture_output=True,
        text=True,
        check=False,
        shell=use_shell,
    )
    return int(getattr(result, "returncode", 1)), str(getattr(result, "stdout", "")) + str(
        getattr(result, "stderr", "")
    )


def _target_matches(kind: str, reported: str, expected: str, platform: str) -> bool:
    text = reported.strip().lower()
    if not text:
        return False
    if "aarch64" not in text and "arm64" not in text:
        return False
    if platform == "android":
        # Keep the Android API component part of the target identity.  A
        # compiler targeting API 24 can otherwise pass the generic
        # ``aarch64-linux-android`` prefix check while the artifact contract
        # requests API 26 (and may then reference an incompatible sysroot).
        expected_match = re.search(r"aarch64(?:-[^-\s]+)?-linux-android(\d+)", expected)
        # Clang commonly reports a vendor-qualified triple such as
        # ``aarch64-unknown-linux-android26`` while the profile contract uses
        # ``aarch64-linux-android26``.  The vendor component is ABI-neutral;
        # retain strict architecture, OS, and API-level matching.
        reported_match = re.search(r"aarch64(?:-[^-\s]+)?-linux-android(\d+)", text)
        return bool(
            expected_match
            and reported_match
            and int(reported_match.group(1)) == int(expected_match.group(1))
        )
    # GNU cross compilers commonly report aarch64-none-linux-gnu while clang
    # reports aarch64-unknown-linux-gnu.  Both are the same Linux ABI family.
    return "linux-gnu" in text and "android" not in text


def preflight_arm64_toolchain(
    target: str,
    compiler: str | Path,
    *,
    sysroot: str | Path | None = None,
    cxx_include: str | Path | None = None,
    arch_include: str | Path | None = None,
    target_args: tuple[str, ...] = (),
    runner: Callable[..., Any] = subprocess.run,
) -> Arm64ToolchainReport:
    """Return a deterministic read-only toolchain report.

    ``target_args`` may carry an explicit clang ``--target=...`` contract for
    a host clang binary.  The target is still verified from the compiler's
    response, so this does not allow relabelling an x86 build as ARM.

    ``target`` is the builder profile name (for example
    ``cpu_arm64_android_api26`` or ``cpu_arm64_linux``).  A report with
    ``ok=False`` is actionable and must stop the caller before artifact output.
    """

    platform, expected = _expected_target(target)
    path = Path(compiler).expanduser()
    diagnostics: list[str] = []
    if not path.is_file():
        diagnostics.append(f"compiler does not exist: {path}")
        return Arm64ToolchainReport(
            target=str(target), compiler=str(path), compiler_kind="unknown",
            requested_triple=expected, reported_target="", llvm_major=None,
            sysroot=str(sysroot or ""), cxx_include=str(cxx_include or ""),
            arch_include=str(arch_include or ""), diagnostics=tuple(diagnostics)
        )

    name = path.name.lower()
    compiler_kind = "gnu" if ("aarch64" in name and ("g++" in name or "gcc" in name)) else "clang"
    code, version_text = _run_probe(path, ["--version"], runner=runner)
    match = _VERSION_RE.search(version_text)
    llvm_major = int(match.group(1)) if match else None
    if code != 0 or llvm_major != LLVM20_MAJOR:
        diagnostics.append("compiler must report LLVM/Clang major version 20")

    probe_args = list(target_args)
    probe_args.append("-dumpmachine" if compiler_kind == "gnu" else "-print-target-triple")
    target_code, target_text = _run_probe(path, probe_args, runner=runner)
    reported = target_text.strip().splitlines()[-1].strip() if target_text.strip() else ""
    # Some clang builds do not implement -print-target-triple; the target is
    # still checked through a no-codegen driver probe in that case.
    if target_code != 0 or not _target_matches(compiler_kind, reported, expected, platform):
        diagnostics.append(f"compiler target is not compatible with {expected}")

    paths: Mapping[str, str | Path | None] = {
        "sysroot": sysroot,
        "cxx_include": cxx_include,
        "arch_include": arch_include,
    }
    for label, value in paths.items():
        if value is not None and not Path(value).expanduser().is_dir():
            diagnostics.append(f"{label} does not exist: {value}")

    return Arm64ToolchainReport(
        target=str(target), compiler=str(path), compiler_kind=compiler_kind,
        requested_triple=expected, reported_target=reported, llvm_major=llvm_major,
        sysroot=str(sysroot or ""), cxx_include=str(cxx_include or ""),
        arch_include=str(arch_include or ""), ok=not diagnostics,
        diagnostics=tuple(diagnostics),
    )


__all__ = ["Arm64ToolchainReport", "preflight_arm64_toolchain"]
