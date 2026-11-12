"""CLI: ``python -m taichi_fault_trace [--diagnose|--hints|--selftest]``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ._config import current_config
from ._hints import iter_hints
from ._native import artifact_snapshot, diagnose


def _print_diagnose(as_json: bool) -> int:
    snapshot = diagnose()
    if as_json:
        print(json.dumps(snapshot, indent=2, ensure_ascii=False, default=str))
        return 0
    environment = snapshot["environment"]
    native = snapshot["native"]
    print("ENVIRONMENT")
    for key in ("timestamp", "pid", "thread", "python", "platform", "cwd", "taichi_version"):
        print(f"  {key:14}: {environment.get(key)}")
    for key, value in (environment.get("env") or {}).items():
        print(f"  env.{key:11}: {value}")
    print("NATIVE")
    for key in (
        "engine_type",
        "arch",
        "device_id",
        "generation",
        "gpu_name",
        "handle",
        "library",
        "last_error",
        "last_init_error",
        "context_backend",
        "device_name",
    ):
        print(f"  {key:14}: {native.get(key)}")
    return 0


def _print_hints() -> int:
    for hint in iter_hints():
        print(f"{hint.id}  [{hint.severity}]  {hint.title}")
        for cause in hint.causes:
            print(f"    sebab : {cause}")
        for check in hint.checks:
            print(f"    periksa: {check}")
        if hint.docs:
            print(f"    rujukan: {hint.docs}")
        print()
    return 0


def _print_artifacts(directory: str) -> int:
    root = Path(directory)
    if not root.exists():
        print(f"direktori tidak ditemukan: {root}", file=sys.stderr)
        return 2
    count = 0
    for path in sorted(root.rglob("*.tcm")):
        info = artifact_snapshot(path)
        print(json.dumps(info, ensure_ascii=False))
        count += 1
    print(f"total={count}", file=sys.stderr)
    return 0


def _print_inventory() -> int:
    import importlib

    import taichi_fault_trace as tracer
    from ._wrap import _RUNTIME_SUBMODULES

    for name in sorted(_RUNTIME_SUBMODULES):
        try:
            importlib.import_module(name)
        except Exception:
            continue
    tracer.install()
    names = tracer.wrapped_inventory()
    for name in names:
        print(name)
    print(f"total={len(names)}", file=sys.stderr)
    return 0


def _selftest() -> int:
    import taichi_fault_trace as tracer

    tracer.install()
    print(f"config: mode={current_config().mode} dir={current_config().report_dir}")

    failures = 0

    try:
        import taichi.aot_engine as aot_engine

        aot_engine._raise_native_engine_error(None, "selftest-native")
    except RuntimeError as exc:
        failures += 1
        report = getattr(exc, "__taichi_fault_report__", None)
        print(
            "selftest #1:",
            "OK" if report is not None else "TANPA LAPORAN",
            f"code={getattr(report, 'code', None)}",
        )

    def outer():
        def inner():
            raise ValueError("selftest contract mismatch: expected shape (1,3)")
        inner()

    try:
        with tracer.trace_scope("selftest-scope"):
            outer()
    except ValueError as exc:
        failures += 1
        report = getattr(exc, "__taichi_fault_report__", None)
        print(
            "selftest #2:",
            "OK" if report is not None else "TANPA LAPORAN",
            f"code={getattr(report, 'code', None)}",
        )

    last = tracer.last_report()
    if last is not None:
        print(f"laporan terakhir: {last.artifact_path}")
    return 0 if failures == 2 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="taichi_fault_trace")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--diagnose", action="store_true", help="snapshot backend/env")
    group.add_argument("--json", action="store_true", help="diagnose as JSON")
    group.add_argument("--hints", action="store_true", help="list hint rules")
    group.add_argument("--selftest", action="store_true", help="run tracer selftest")
    group.add_argument("--inventory", action="store_true", help="list wrapped runtime functions")
    group.add_argument("--artifacts", metavar="DIR", help="hash .tcm artifacts")
    args = parser.parse_args(argv)

    if args.hints:
        return _print_hints()
    if args.selftest:
        return _selftest()
    if args.inventory:
        return _print_inventory()
    if args.artifacts:
        return _print_artifacts(args.artifacts)
    return _print_diagnose(args.json)


if __name__ == "__main__":
    raise SystemExit(main())
