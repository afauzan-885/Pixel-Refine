"""Run the qualified JPEG and bounded HEIC/HEVC gates per backend.

This is an orchestration verifier, not a second codec implementation.  Each
child process receives an explicit backend contract so a successful run cannot
be mistaken for automatic backend selection.  The native no-NumPy verifier is
intentionally separate because it must be launched by file path rather than
through the legacy package initializer.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
COMPRESSION_ROOT = Path(__file__).resolve().parent

BACKENDS = {
    "cpu": {
        "target": "cpu_x86_64_windows",
        "vendor": None,
    },
    "cuda": {
        "target": "cuda_x86_64_windows_nvidia",
        "vendor": "nvidia",
    },
    "vulkan": {
        "target": "vulkan_x86_64_windows_nvidia",
        "vendor": "nvidia",
    },
    "opengl": {
        "target": "opengl_x86_64_windows_nvidia",
        "vendor": "nvidia",
    },
}

VERIFIERS = {
    "jpeg": ("-m", "taichi_vision.taichi_algorithm.compression.verify_jpeg_production"),
    "heic": ("-m", "taichi_vision.taichi_algorithm.compression.verify_heic_production"),
    "hevc_general": ("-m", "taichi_vision.taichi_algorithm.compression.verify_hevc_general_aot"),
}


def _last_report(stdout: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for index, character in enumerate(stdout):
        if character != "{":
            continue
        try:
            value, _end = decoder.raw_decode(stdout[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            candidates.append(value)
    if not candidates:
        return None
    # The verifier output contains nested JSON objects.  Select the report
    # envelope rather than the final nested ``external``/``artifact`` object.
    def score(value: dict[str, Any]) -> tuple[int, int]:
        keys = set(value)
        envelope = int(
            "all_exact" in keys
            or "case_count" in keys
            or "auto_profile_case_count" in keys
        )
        return envelope, len(keys)

    return max(candidates, key=score)


def _environment(backend: str, vendor: str | None) -> dict[str, str]:
    environment = os.environ.copy()
    for name, value in {
        "AOT_MODE": "1",
        "AOT_ARCH": backend,
        "TAICHI_ARCH": backend,
        "PIXEL_REFINE_AOT_ARCH": backend,
        "PIXEL_REFINE_BACKEND": backend,
        "AOT_ALLOW_HOST_FALLBACK": "0",
        "AOT_DEVICE": "0",
    }.items():
        environment[name] = value
    if vendor is None:
        environment.pop("TARGET_VENDOR", None)
    else:
        environment["TARGET_VENDOR"] = vendor
    return environment


def _run_verifier(backend: str, verifier: str) -> dict[str, Any]:
    command = [sys.executable, *VERIFIERS[verifier]]
    attempts: list[dict[str, Any]] = []
    # A GPU process can transiently report a native launch failure while the
    # driver is reclaiming resources after the preceding isolated child.  One
    # clean retry is allowed, but every attempt remains recorded so a flaky
    # target is visible in the qualification artifact rather than hidden.
    for attempt_index in range(2):
        process = subprocess.run(
            command,
            cwd=str(ROOT),
            env=_environment(backend, BACKENDS[backend]["vendor"]),
            capture_output=True,
            text=True,
            timeout=900,
        )
        report = _last_report(process.stdout) or {}
        if process.returncode != 0:
            report["passed"] = False
        attempts.append(
            {
                "attempt": attempt_index + 1,
                "returncode": int(process.returncode),
                "passed": bool(report.get("passed", report.get("all_exact", False))),
                "report": report,
                "stdout_tail": process.stdout[-2000:],
                "stderr_tail": process.stderr[-2000:],
            }
        )
        if process.returncode == 0:
            break
    final = attempts[-1]
    return {
        "command": command,
        "returncode": int(final["returncode"]),
        "passed": bool(final["passed"]),
        "report": final["report"],
        "attempts": attempts,
    }


def _artifact_status(backend: str) -> dict[str, Any]:
    target = BACKENDS[backend]["target"]
    path = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / target / f"compression_image_{target}.tcm"
    return {"target": target, "path": str(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}


def run_matrix(backends: tuple[str, ...]) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for backend in backends:
        artifact = _artifact_status(backend)
        backend_result: dict[str, Any] = {"artifact": artifact, "verifiers": {}}
        if not artifact["exists"] or artifact["bytes"] <= 0:
            backend_result["passed"] = False
            backend_result["error"] = "target-qualified compression TCM is missing or empty"
            results[backend] = backend_result
            continue
        for verifier in VERIFIERS:
            backend_result["verifiers"][verifier] = _run_verifier(backend, verifier)
        backend_result["passed"] = all(
            bool(item["passed"])
            for item in backend_result["verifiers"].values()
        )
        results[backend] = backend_result
    return {
        "schema": "compression-backend-matrix-v1",
        "backends": list(backends),
        "verifiers": list(VERIFIERS),
        "results": results,
        "passed": all(bool(item["passed"]) for item in results.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--backend",
        action="append",
        choices=tuple(BACKENDS),
        help="run only the selected backend; may be repeated",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    selected = tuple(args.backend or BACKENDS)
    report = run_matrix(selected)
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
