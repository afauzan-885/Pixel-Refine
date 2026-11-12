"""Install/remove the venv-wide taichi fault tracer activation.

Usage (project venv)::

    python tools/install_taichi_fault_trace.py --install
    python tools/install_taichi_fault_trace.py --status
    python tools/install_taichi_fault_trace.py --uninstall

The installer writes ``taichi_fault_trace_activate.pth`` into the active
interpreter's ``site-packages``.  Python executes the two ``import`` lines at
startup, which append the repository root to ``sys.path`` and register the
deferred ``taichi`` import hook.  Nothing is copied or modified inside the
``taichi`` package, so reinstalling taichi cannot break the tracer and the
source of truth stays in this repository.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

MARKER = "taichi_fault_trace_activate.pth"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _site_packages() -> Path:
    candidates = [Path(p) for p in sys.path if p.endswith(("site-packages", "dist-packages"))]
    if not candidates:
        raise SystemExit("site-packages tidak ditemukan pada interpreter aktif")
    return candidates[0]


def _pth_body() -> str:
    root = str(REPO_ROOT)
    return (
        f"import sys; sys.path.append(r'{root}')\n"
        "import taichi_fault_trace.autoinstall\n"
    )


def install() -> int:
    target = _site_packages() / MARKER
    body = _pth_body()
    if target.exists() and target.read_text(encoding="utf-8") == body:
        print(f"sudah terpasang: {target}")
        return 0
    target.write_text(body, encoding="utf-8")
    print(f"terpasang: {target}")
    print(f"repo root: {REPO_ROOT}")
    return 0


def uninstall() -> int:
    target = _site_packages() / MARKER
    if not target.exists():
        print(f"tidak ada: {target}")
        return 0
    target.unlink()
    print(f"dihapus: {target}")
    return 0


def status() -> int:
    target = _site_packages() / MARKER
    if not target.exists():
        print("status: NONAKTIF")
        return 1
    print("status: AKTIF")
    print(target.read_text(encoding="utf-8").rstrip())
    return 0


def verify() -> int:
    script = (
        "import sys; "
        "import taichi; "
        "import taichi_fault_trace as t; "
        "print('tracer_installed=', t.is_installed()); "
        "print('mode=', t.current_config().mode); "
        "print('wrapped_sample=', [n for n in ('taichi.aot_engine.get_engine', "
        "'taichi.aot_engine._raise_native_engine_error') "
        "if getattr(getattr(__import__('taichi.aot_engine', fromlist=['x']), n.split('.')[-1]), "
        "'__taichi_fault_trace_wrapped__', False)])"
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    print(completed.stdout.strip())
    if completed.returncode != 0:
        print(completed.stderr.strip(), file=sys.stderr)
    return completed.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--install", action="store_true")
    group.add_argument("--uninstall", action="store_true")
    group.add_argument("--status", action="store_true")
    group.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.install:
        return install()
    if args.uninstall:
        return uninstall()
    if args.verify:
        return verify()
    return status()


if __name__ == "__main__":
    raise SystemExit(main())
