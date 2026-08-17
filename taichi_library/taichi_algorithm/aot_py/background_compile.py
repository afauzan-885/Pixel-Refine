"""Background, isolated multi-backend AOT compilation orchestrator."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import platform
import subprocess
import sys
from pathlib import Path

try:
    from .target_registry import SUPPORTED_BACKENDS, SUPPORTED_TARGETS, TARGET_BACKENDS
except ImportError:  # Direct script execution.
    from target_registry import SUPPORTED_BACKENDS, SUPPORTED_TARGETS, TARGET_BACKENDS


ROOT = Path(__file__).resolve().parents[3]
SUITE = Path(__file__).with_name("compile_aot_backend_suite.py")


def _host_is_arm64() -> bool:
    """Return whether the current worker can execute an ARM64 host build."""
    values = {
        str(platform.machine() or ""),
        str(os.environ.get("PROCESSOR_ARCHITECTURE", "")),
        str(os.environ.get("PROCESSOR_ARCHITEW6432", "")),
    }
    return any(value.lower() in {"arm64", "aarch64"} for value in values)


def target_toolchain_pending(target: str) -> str | None:
    """Explain profiles unavailable on this worker without relabeling output."""
    target = str(target)
    if target == "cpu_x86_64_linux" and os.name == "nt":
        return (
            "requires a Linux/glibc worker; this orchestrator has no "
            "target-aware x86_64-linux cross compiler"
        )
    # This orchestrator has no CUDA ARM64 cross-compiler.  Do not let the
    # generic CPU cross override relabel a host-x86 CUDA payload as ARM64.
    if target.startswith("cuda_arm64") and not _host_is_arm64():
        return (
            "requires an ARM64 CUDA host worker; no CUDA ARM64 cross-compiler "
            "is implemented by this orchestrator"
        )
    return None


def compile_backend(backend: str, timeout: int = 900):
    env = os.environ.copy()
    env["AOT_ARCH"] = backend
    env["AOT_COMPILE_ONLY"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(SUITE), "--backend", backend],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "backend": backend,
            "returncode": 124,
            "ok": False,
            "status": "timeout",
            "output": f"worker timed out after {error.timeout}s",
        }
    except OSError as error:
        return {
            "backend": backend,
            "returncode": 127,
            "ok": False,
            "status": "worker_error",
            "output": str(error),
        }
    return {
        "backend": backend,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "status": "success" if proc.returncode == 0 else "failed",
        "output": proc.stdout[-12000:],
    }


def _collect_progress(futures, labels):
    """Collect isolated workers while preserving input order and progress."""
    results = [None] * len(futures)
    positions = {future: index for index, future in enumerate(futures)}
    for future in concurrent.futures.as_completed(futures):
        index = positions[future]
        result = future.result()
        results[index] = result
        label = labels[index]
        if result.get("status") == "pending_toolchain":
            status = "PENDING"
        else:
            status = "PASS" if result.get("ok") else "FAIL"
        print(f"[AOT compile] {label}: {status}", flush=True)
    return results


def compile_all(backends, workers=None, timeout=900):
    workers = workers or min(len(backends), 3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [
            pool.submit(compile_backend, backend, timeout) for backend in backends
        ]
        return _collect_progress(futures, tuple(backends))


def compile_target(target: str, timeout: int = 900):
    """Compile one exact target profile in an isolated worker process.

    The source compiler is still shared with the backend-only command.  The
    target ID controls the artifact directory, ABI, and any cross-toolchain
    validation; it never relabels an artifact emitted for another target.
    """
    if target not in TARGET_BACKENDS:
        raise ValueError(f"unsupported AOT target: {target}")
    backend = TARGET_BACKENDS[target]
    env = os.environ.copy()
    env["AOT_ARCH"] = backend
    env["AOT_COMPILE_ONLY"] = "1"
    try:
        proc = subprocess.run(
            [sys.executable, str(SUITE), "--target", target],
            cwd=str(ROOT),
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as error:
        return {
            "target": target,
            "backend": backend,
            "returncode": 124,
            "ok": False,
            "status": "timeout",
            "output": f"worker timed out after {error.timeout}s",
        }
    except OSError as error:
        return {
            "target": target,
            "backend": backend,
            "returncode": 127,
            "ok": False,
            "status": "worker_error",
            "output": str(error),
        }
    return {
        "target": target,
        "backend": backend,
        "returncode": proc.returncode,
        "ok": proc.returncode == 0,
        "status": "success" if proc.returncode == 0 else "failed",
        "output": proc.stdout[-12000:],
    }


def compile_targets(targets, workers=None, timeout=900):
    targets = tuple(targets)
    workers = workers or min(len(targets), 3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(compile_target, target, timeout) for target in targets]
        return _collect_progress(futures, targets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--backends",
        nargs="+",
        default=["cpu", "vulkan", "opengl", "cuda"],
        choices=SUPPORTED_BACKENDS,
        help=(
            "Backend names to compile in isolated workers. GLES is available "
            "for explicit Android/ES builds; it is excluded from the desktop "
            "default because it requires the GLES target profile."
        ),
    )
    selection.add_argument(
        "--targets",
        nargs="+",
        choices=SUPPORTED_TARGETS,
        help=(
            "Compile exact architecture/OS/vendor profiles using the same "
            "source compiler. Toolchains for ARM/Android must already be "
            "configured."
        ),
    )
    selection.add_argument(
        "--all-targets",
        action="store_true",
        help=(
            "Compile the complete target matrix with the same source jobs. "
            "ARM/Android profiles require their configured cross-toolchains; "
            "existing validated artifacts are skipped."
        ),
    )
    parser.add_argument(
        "--best-effort",
        action="store_true",
        help=(
            "For target-matrix builds, skip profiles whose host/cross toolchain "
            "is unavailable and report them as PENDING. Without this flag the "
            "matrix remains strict."
        ),
    )
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument(
        "--timeout",
        type=int,
        default=900,
        help="timeout in seconds for each isolated backend/target worker",
    )
    args = parser.parse_args()
    import json

    if args.all_targets or args.targets:
        requested_targets = tuple(
            SUPPORTED_TARGETS if args.all_targets else args.targets
        )
        pending = []
        build_targets = []
        for target in requested_targets:
            reason = target_toolchain_pending(target) if args.best_effort else None
            if reason is None:
                build_targets.append(target)
            else:
                pending.append(
                    {
                        "target": target,
                        "backend": TARGET_BACKENDS[target],
                        "returncode": 2,
                        "ok": False,
                        "status": "pending_toolchain",
                        "output": reason,
                    }
                )
        result = (
            compile_targets(build_targets, args.workers or None, args.timeout)
            if build_targets
            else []
        )
        result.extend(pending)
    else:
        result = compile_all(args.backends, args.workers or None, args.timeout)
    print(json.dumps(result, indent=2))
