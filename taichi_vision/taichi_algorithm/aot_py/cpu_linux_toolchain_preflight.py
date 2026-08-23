"""Read-only preflight for the CPU x86_64 Linux/glibc LLVM20 profile.

The Windows LLVM20 bundle can emit x86_64 code, but its default target and
CRT are ``x86_64-pc-windows-msvc``.  This module makes the Linux gate
explicit: a compiler must report a Linux GNU triple and, for a cross build,
the supplied sysroot must contain the glibc headers and startup objects used
by the linker.  No compiler output, TCM, bridge, or cache is written.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any, Callable


LLVM20_MAJOR = 20
EXPECTED_TRIPLE = "x86_64-unknown-linux-gnu"
_VERSION_RE = re.compile(r"(?:clang version|clang)\s+(\d+)", re.I)


@dataclass(frozen=True)
class CpuLinuxToolchainReport:
    target: str
    compiler: str
    requested_triple: str
    reported_target: str
    llvm_major: int | None
    sysroot: str = ""
    host_platform: str = ""
    compiler_kind: str = "unknown"
    compiler_ok: bool = False
    target_ok: bool = False
    sysroot_ok: bool = False
    link_inputs_ok: bool = False
    ok: bool = False
    diagnostics: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["diagnostics"] = list(self.diagnostics)
        return result


def _run_probe(
    compiler: Path,
    args: list[str],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> tuple[int, str]:
    result = runner(
        [str(compiler), *args], capture_output=True, text=True, check=False
    )
    return int(getattr(result, "returncode", 1)), str(
        getattr(result, "stdout", "")
    ) + str(getattr(result, "stderr", ""))


def _linux_target(text: str) -> bool:
    value = text.strip().lower()
    # Accept the ABI-equivalent vendor spellings emitted by clang/GCC, but
    # never accept a Windows, musl, Android, or bare x86 target.
    return bool(
        re.search(r"^x86_64(?:-[^\s-]+)?-linux-gnu$", value)
        or re.search(r"^x86_64-linux-gnu$", value)
    )


def _sysroot_inputs(root: Path) -> tuple[bool, list[str]]:
    diagnostics: list[str] = []
    include = root / "usr" / "include"
    # glibc's startup objects may be under usr/lib or a multiarch directory.
    startup_names = ("crt1.o", "crti.o", "crtn.o")
    search_roots = [root / "usr" / "lib", root / "lib"]
    if not include.is_dir():
        diagnostics.append(f"sysroot missing glibc include directory: {include}")
    missing = [
        name
        for name in startup_names
        if not any((candidate / name).is_file() for candidate in search_roots)
        and not any(
            path.name == name
            for base in search_roots
            if base.is_dir()
            for path in base.rglob(name)
        )
    ]
    if missing:
        diagnostics.append("sysroot missing glibc startup objects: " + ", ".join(missing))
    return not diagnostics, diagnostics


def preflight_cpu_linux_toolchain(
    compiler: str | Path,
    *,
    sysroot: str | Path | None = None,
    host_platform: str | None = None,
    target_args: tuple[str, ...] = (),
    runner: Callable[..., Any] = subprocess.run,
) -> CpuLinuxToolchainReport:
    """Return a deterministic, side-effect-free Linux toolchain report."""

    path = Path(compiler).expanduser()
    platform_name = str(host_platform or "").strip().lower()
    diagnostics: list[str] = []
    if not path.is_file():
        diagnostics.append(f"compiler does not exist: {path}")
        return CpuLinuxToolchainReport(
            target="cpu_x86_64_linux",
            compiler=str(path),
            requested_triple=EXPECTED_TRIPLE,
            reported_target="",
            llvm_major=None,
            sysroot=str(sysroot or ""),
            host_platform=platform_name,
            diagnostics=tuple(diagnostics),
        )

    compiler_kind = "gcc" if "gcc" in path.name.lower() else "clang"
    code, version_text = _run_probe(path, ["--version"], runner=runner)
    match = _VERSION_RE.search(version_text)
    llvm_major = int(match.group(1)) if match else None
    compiler_ok = code == 0 and llvm_major == LLVM20_MAJOR
    if not compiler_ok:
        diagnostics.append("compiler must report LLVM/Clang major version 20")

    probe = list(target_args)
    probe.append("-dumpmachine" if compiler_kind == "gcc" else "-print-target-triple")
    target_code, target_text = _run_probe(path, probe, runner=runner)
    reported = target_text.strip().splitlines()[-1].strip() if target_text.strip() else ""
    target_ok = target_code == 0 and _linux_target(reported)
    if not target_ok:
        diagnostics.append(
            f"compiler target is not compatible with {EXPECTED_TRIPLE} (reported {reported or 'unknown'})"
        )

    sysroot_value = str(sysroot or "")
    sysroot_ok = False
    link_inputs_ok = False
    if sysroot is None:
        # Native Linux workers may use their standard glibc sysroot.  The
        # caller must explicitly identify that it is running on Linux; a
        # Windows host cannot borrow its MSVC CRT for this target.
        sysroot_ok = platform_name.startswith("linux")
        link_inputs_ok = sysroot_ok
        if not sysroot_ok:
            diagnostics.append("Linux/glibc sysroot is required on a non-Linux host")
    else:
        root = Path(sysroot).expanduser()
        if not root.is_dir():
            diagnostics.append(f"sysroot does not exist: {root}")
        else:
            sysroot_ok, sysroot_diagnostics = _sysroot_inputs(root)
            diagnostics.extend(sysroot_diagnostics)
            link_inputs_ok = sysroot_ok

    return CpuLinuxToolchainReport(
        target="cpu_x86_64_linux",
        compiler=str(path),
        requested_triple=EXPECTED_TRIPLE,
        reported_target=reported,
        llvm_major=llvm_major,
        sysroot=sysroot_value,
        host_platform=platform_name,
        compiler_kind=compiler_kind,
        compiler_ok=compiler_ok,
        target_ok=target_ok,
        sysroot_ok=sysroot_ok,
        link_inputs_ok=link_inputs_ok,
        ok=not diagnostics,
        diagnostics=tuple(diagnostics),
    )


__all__ = ["CpuLinuxToolchainReport", "preflight_cpu_linux_toolchain"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", required=True, type=Path)
    parser.add_argument("--sysroot", type=Path, default=None)
    parser.add_argument("--host-platform", default=os.name)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)
    report = preflight_cpu_linux_toolchain(
        args.compiler,
        sysroot=args.sysroot,
        host_platform=args.host_platform,
    )
    encoded = json.dumps(report.as_dict(), indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if report.ok else 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
