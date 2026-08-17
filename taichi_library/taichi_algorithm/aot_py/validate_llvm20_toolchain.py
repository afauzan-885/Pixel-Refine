r"""Preflight an LLVM20 toolchain without compiling or creating a GPU context.

The command intentionally performs only executable ``--version`` probes.  It
is used before a target build to catch an accidental LLVM15/LLVM14 selection or
an incomplete LLVM installation.  A successful preflight is not a build or a
runtime qualification.

Example::

    python validate_llvm20_toolchain.py --root path\to\llvm20 --json report.json
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Iterable


REQUIRED_MAJOR = 20
TOOLS = ("clang", "clang++", "llc", "llvm-config")
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LLVM20_ROOT = (
    ROOT
    / "test_algorithm"
    / "llvm_msvc_dev_extract"
    / "clang+llvm-20.1.5-x86_64-pc-windows-msvc"
)


def _run_version(path: Path) -> tuple[int | None, str]:
    command: object
    shell = path.suffix.lower() == ".cmd"
    command = str(path) + " --version" if shell else [str(path), "--version"]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            shell=shell,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, f"{type(exc).__name__}: {exc}"
    text = (result.stdout or "") + (result.stderr or "")
    match = re.search(
        r"(?:clang|LLVM)\s+(?:version\s+)?(\d+)|^\s*(\d+)\.",
        text,
        re.IGNORECASE | re.MULTILINE,
    )
    major = next((group for group in match.groups() if group), None) if match else None
    return (int(major) if major else None), text.strip()[-1000:]


def _resolve_tool(root: Path | None, name: str) -> Path | None:
    suffix = ".exe" if os.name == "nt" else ""
    candidates: list[Path] = []
    if root is not None:
        candidates.extend((root / "bin" / f"{name}{suffix}", root / "bin" / name))
    # A pinned root is an identity boundary.  Falling back to PATH for just
    # one missing executable could silently combine LLVM20 clang with LLVM15
    # llc, which is unsafe even when every individual --version probe passes.
    if root is None:
        found = shutil.which(name)
        if found:
            candidates.append(Path(found))
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def inspect_toolchain(root: Path | None = None, tools: Iterable[str] = TOOLS) -> dict[str, object]:
    records: dict[str, object] = {}
    for name in tools:
        path = _resolve_tool(root, name)
        if path is None:
            records[name] = {"present": False, "ok": False}
            continue
        major, output = _run_version(path)
        records[name] = {
            "present": True,
            "path": str(path),
            "major": major,
            "ok": major == REQUIRED_MAJOR,
            "version_output": output,
        }
    missing_or_wrong = [
        name for name, record in records.items()
        if not isinstance(record, dict) or not bool(record.get("ok"))
    ]
    resolved_roots = {
        str(Path(record["path"]).parent.parent.resolve())
        for record in records.values()
        if isinstance(record, dict) and record.get("present") and record.get("path")
    }
    coherent_root = len(resolved_roots) <= 1
    if not coherent_root:
        failed_tools = list(missing_or_wrong)
        failed_tools.append("coherent_toolchain_root")
    else:
        failed_tools = missing_or_wrong
    return {
        "kind": "llvm20_toolchain_preflight",
        "required_major": REQUIRED_MAJOR,
        "tools": records,
        "ok": not missing_or_wrong,
        "failed_tools": failed_tools,
        "toolchain_root": str(root.resolve()) if root is not None else None,
        "resolved_toolchain_roots": tuple(sorted(resolved_roots)),
        "coherent_toolchain_root": coherent_root,
        "compiled": False,
        "native_runtime_tested": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_LLVM20_ROOT,
        help="LLVM20 installation root (defaults to the pinned repository toolchain)",
    )
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)
    root = args.root.expanduser().resolve() if args.root else None
    report = inspect_toolchain(root)
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(encoded + "\n", encoding="utf-8")
    print(encoded)
    return 0 if bool(report["ok"]) else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
