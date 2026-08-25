"""Offline validator for the Pixel Refine TCM/runtime ABI envelope."""

from __future__ import annotations

import argparse
import json
import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]

# Loading the contract by file path is intentional.  Importing the public
# ``taichi_aot`` package initializes the native AOT engine; this command is an
# offline validator and must never create a GPU context or watchdog heartbeat.
_CONTRACT_PATH = ROOT / "taichi_vision" / "taichi_aot" / "tcm_contract.py"
_SPEC = importlib.util.spec_from_file_location("pixel_refine_tcm_contract", _CONTRACT_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - packaging error
    raise RuntimeError(f"cannot load TCM contract module: {_CONTRACT_PATH}")
_CONTRACT = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_CONTRACT)
TcmContractError = _CONTRACT.TcmContractError
validate_tcm = _CONTRACT.validate_tcm


def _target_from_args(args: argparse.Namespace) -> dict[str, str] | None:
    if not any((args.backend, args.arch, args.os, args.vendor)):
        return None
    return {
        "backend": args.backend or "cpu",
        "arch": args.arch or "x86_64",
        "os": args.os or "unknown",
        "vendor": args.vendor or "unknown",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--runtime-abi", type=int, default=1)
    parser.add_argument("--feature", action="append", default=[])
    parser.add_argument("--backend")
    parser.add_argument("--arch")
    parser.add_argument("--os")
    parser.add_argument("--vendor")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        report = validate_tcm(
            args.path,
            runtime_abi=args.runtime_abi,
            runtime_features=args.feature,
            requested_target=_target_from_args(args),
        )
    except (OSError, TcmContractError, ValueError) as exc:
        if args.as_json:
            print(json.dumps({"status": "invalid", "path": str(args.path), "error": str(exc)}))
        else:
            print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{report['status'].upper()}: {args.path}")
        print(f"entries={len(report['entries'])}")
        if report["status"] == "valid":
            manifest = report["manifest"]
            print(
                f"format={manifest['tcm_format_version']} "
                f"runtime_abi>={manifest['minimum_runtime_abi']} "
                f"target={manifest['target']['backend']}/{manifest['target']['arch']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
