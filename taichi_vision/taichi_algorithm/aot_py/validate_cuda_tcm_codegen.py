"""Offline CUDA TCM lowering gate for several NVIDIA compute capabilities.

CUDA TCM archives contain LLVM NVPTX IR, not cubins.  This validator extracts
every embedded ``.ll`` graph and asks LLVM ``llc`` to lower it for each selected
SM.  It is useful on machines without the target GPU, but it is deliberately
only a compile/lowering gate: it cannot validate a CUDA driver, numerical
parity, or native performance.

Example::

    python validate_cuda_tcm_codegen.py --root \
        taichi_vision/taichi_algorithm/aot_tcm/cuda_x86_64_windows_nvidia \
        --llc path\\to\\llvm\\bin\\llc.exe --targets 52,53,61,120
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import defaultdict
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from taichi_vision.cuda_arch_matrix import CudaTarget, normalize_cuda_target


DEFAULT_ROOT = (
    ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "cuda_x86_64_windows_nvidia"
)


def _find_llc(explicit: Path | None) -> Path:
    candidates = [explicit] if explicit else []
    found = shutil.which("llc")
    if found:
        candidates.append(Path(found))
    for candidate in candidates:
        if candidate is not None and candidate.expanduser().is_file():
            return candidate.expanduser().resolve()
    raise FileNotFoundError("llc was not found; pass --llc or put it on PATH")


def _ptx_feature(target: CudaTarget) -> str:
    """Select the PTX dialect required by the target family.

    This is only an LLVM lowering hint; matching ``ptxas`` and driver tests
    remain separate evidence gates.  Blackwell 100/101/120 uses PTX8.7,
    while 103/121 requires PTX8.8.
    """

    sm = target.compute_capability
    if sm in {103, 121}:
        return "ptx88"
    if sm in {100, 101, 120}:
        return "ptx87"
    if sm >= 52:
        # Existing Taichi IR uses stack operations that LLVM20 lowers through
        # the PTX7.3 feature set.  ptxas is still required for final support.
        return "ptx73"
    return "ptx60"


_FORBIDDEN_BY_CC: tuple[tuple[bytes, int, str], ...] = (
    (b"cuda_match_any_sync_i32", 70, "match.any.sync requires SM70+"),
    (b"llvm.nvvm.match.any.sync", 70, "match.any.sync requires SM70+"),
    (b"atom.add.noftz.f16x2", 60, "half2 atomic operations require SM60+"),
    # LLVM's generic NVPTX lowering emits these intrinsics for Taichi's
    # dynamic stack slots. PTX 7.3 introduced dynamic alloca support and
    # LLVM rejects them for sm_50 even when the surrounding IR is valid.
    # Catch them before invoking llc so reports expose the actionable
    # limitation instead of repeating the same diagnostic for every graph.
    (b"llvm.stacksave", 52, "dynamic stack allocation requires SM52+ (llvm.stacksave)"),
    (b"llvm.stackrestore", 52, "dynamic stack allocation requires SM52+ (llvm.stackrestore)"),
)


def _unsupported_ir_features(payload: bytes, target: CudaTarget) -> tuple[str, ...]:
    """Find architecture-illegal intrinsics before invoking ``llc``."""

    errors: list[str] = []
    for marker, minimum_cc, reason in _FORBIDDEN_BY_CC:
        if marker in payload and target.compute_capability < minimum_cc:
            errors.append(reason)
    return tuple(errors)


def _target_gate_diagnostics(output: str) -> tuple[str, ...]:
    """Extract non-fatal LLVM target warnings that invalidate a qualification.

    Some LLVM releases return exit code zero while silently ignoring an
    unknown ``sm_*`` processor or ``ptx*`` feature.  Treating that result as a
    successful lowering would be a false Blackwell (or future-SM) claim.  The
    validator therefore promotes these warnings to an explicit target gate.
    """

    markers = (
        "not a recognized processor",
        "not a recognized feature",
        "ignoring processor",
        "ignoring feature",
    )
    return tuple(
        line.strip()
        for line in output.splitlines()
        if any(marker in line.lower() for marker in markers)
    )


def _graph_inventory(
    root: Path, limit: int = 0
) -> tuple[list[tuple[str, str, bytes]], list[dict[str, str]], list[str]]:
    """Read every graph and retain archive-level completeness information.

    A lowering result is only a *full graph* result when every LLVM module in
    every TCM archive was visited.  The old implementation silently omitted
    malformed archives and archives without an ``.ll`` member, which made a
    limited successful report look like complete coverage.  Keep the public
    ``_graphs`` helper for existing callers, while the CLI uses this richer
    inventory and fails closed on incomplete input.
    """

    items: list[tuple[str, str, bytes]] = []
    errors: list[dict[str, str]] = []
    archives_without_graphs: list[str] = []
    for archive in sorted(root.glob("*.tcm")):
        try:
            with zipfile.ZipFile(archive) as payload:
                names = [name for name in sorted(payload.namelist()) if name.endswith(".ll")]
                if not names:
                    archives_without_graphs.append(archive.name)
                for name in names:
                    items.append((archive.name, name, payload.read(name)))
                    if limit > 0 and len(items) >= limit:
                        return items, errors, archives_without_graphs
        except (OSError, zipfile.BadZipFile, RuntimeError, KeyError) as exc:
            errors.append({"archive": archive.name, "error": f"{type(exc).__name__}: {exc}"})
    return items, errors, archives_without_graphs


def _graphs(root: Path, limit: int = 0) -> list[tuple[str, str, bytes]]:
    """Return graph payloads for compatibility with existing build scripts."""

    items, _errors, _empty = _graph_inventory(root, limit)
    return items


def _lowering_summary(
    results: list[dict[str, object]],
    *,
    targets: Sequence[CudaTarget],
    graph_count: int,
    input_errors: Sequence[Mapping[str, str]] = (),
    archives_without_graphs: Sequence[str] = (),
    limited: bool = False,
) -> dict[str, object]:
    """Build an explicit per-target full-graph qualification summary.

    ``ok`` for a handful of kernels is not enough to route a bridge.  A
    target is ``full_graph`` only when all expected graphs passed and the
    input inventory itself is complete.  This distinction is persisted in
    JSON so a later manifest writer cannot accidentally promote a partial
    sweep to ``graph_lowering_sms``.
    """

    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in results:
        by_target[str(item.get("sm", ""))].append(item)
    inventory_complete = (
        not limited
        and not input_errors
        and not archives_without_graphs
        and graph_count > 0
    )
    target_summaries: list[dict[str, object]] = []
    qualified: list[str] = []
    for target in targets:
        rows = by_target.get(target.sm, [])
        passed = sum(1 for row in rows if bool(row.get("ok")))
        failed = graph_count - passed if len(rows) == graph_count else graph_count - passed
        complete = inventory_complete and len(rows) == graph_count and passed == graph_count
        if complete:
            qualified.append(target.sm)
        target_summaries.append(
            {
                "sm": target.sm,
                "compute_capability": target.compute_capability,
                "expected_graphs": graph_count,
                "observed_results": len(rows),
                "passed_graphs": passed,
                "failed_graphs": max(0, failed),
                "full_graph": complete,
                "status": "full_graph" if complete else ("partial" if passed else "failed"),
                "failed_items": [
                    {"archive": row.get("archive"), "graph": row.get("graph"), "stage": row.get("stage"), "diagnostic": row.get("diagnostic")}
                    for row in rows
                    if not bool(row.get("ok"))
                ][:50],
            }
        )
    return {
        "inventory_complete": inventory_complete,
        "input_errors": list(input_errors),
        "archives_without_graphs": list(archives_without_graphs),
        "limited": bool(limited),
        "graph_count": graph_count,
        "qualified_targets": qualified,
        "full_graph": bool(qualified) and len(qualified) == len(targets),
        "target_summaries": target_summaries,
    }


def _lower_one(
    llc: Path,
    item: tuple[str, str, bytes],
    target: CudaTarget,
    temp_root: Path,
    timeout: float,
) -> dict[str, object]:
    archive, name, payload = item
    feature_errors = _unsupported_ir_features(payload, target)
    if feature_errors:
        return {
            "archive": archive,
            "graph": name,
            "sm": target.sm,
            "compute_capability": target.compute_capability,
            "ok": False,
            "returncode": None,
            "diagnostic": "; ".join(feature_errors),
            "stage": "feature_gate",
        }
    with tempfile.NamedTemporaryFile(
        suffix=".ll", prefix="cuda-tcm-", dir=temp_root, delete=False
    ) as handle:
        source = Path(handle.name)
        handle.write(payload)
    output = source.with_suffix(".ptx")
    command = [
        str(llc),
        "-march=nvptx64",
        f"-mcpu={target.sm}",
        f"-mattr=+{_ptx_feature(target)}",
        "-O2",
        "-o",
        str(output),
        str(source),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=float(timeout),
            check=False,
        )
        detail = (result.stdout + result.stderr).strip()[-2000:]
        target_diagnostics = _target_gate_diagnostics(detail)
        if target_diagnostics:
            return {
                "archive": archive,
                "graph": name,
                "sm": target.sm,
                "compute_capability": target.compute_capability,
                "ok": False,
                "returncode": result.returncode,
                "diagnostic": "; ".join(target_diagnostics),
                "stage": "target_gate",
            }
        return {
            "archive": archive,
            "graph": name,
            "sm": target.sm,
            "compute_capability": target.compute_capability,
            "ok": result.returncode == 0,
            "returncode": result.returncode,
            "diagnostic": detail,
            "stage": "llc",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "archive": archive,
            "graph": name,
            "sm": target.sm,
            "compute_capability": target.compute_capability,
            "ok": False,
            "returncode": None,
            "diagnostic": f"{type(exc).__name__}: {exc}",
            "stage": "llc",
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--llc", type=Path, default=None)
    parser.add_argument(
        "--targets",
        default="50,52,53,60,61,62,70,72,75,80,86,89,90,100,101,103,120,121",
    )
    parser.add_argument("--limit", type=int, default=0, help="limit extracted graphs (0 = all)")
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--json", type=Path, default=None)
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"CUDA TCM directory does not exist: {root}")
    llc = _find_llc(args.llc)
    targets = [
        normalize_cuda_target(value)
        for value in args.targets.split(",")
        if value.strip()
    ]
    graphs, input_errors, archives_without_graphs = _graph_inventory(root, args.limit)
    if not graphs:
        raise SystemExit(f"no LLVM .ll graphs found in {root}")

    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="cuda-tcm-lowering-") as temp:
        temp_root = Path(temp)
        jobs = [(target, item) for target in targets for item in graphs]
        workers = max(1, min(int(args.workers), 16))
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [
                pool.submit(_lower_one, llc, item, target, temp_root, args.timeout)
                for target, item in jobs
            ]
            for future in futures:
                results.append(future.result())

    lowering = _lowering_summary(
        results,
        targets=targets,
        graph_count=len(graphs),
        input_errors=input_errors,
        archives_without_graphs=archives_without_graphs,
        limited=args.limit > 0,
    )
    report = {
        "kind": "cuda_tcm_codegen_lowering",
        "root": str(root),
        "llc": str(llc),
        "targets": [target.as_dict() for target in targets],
        "graphs": len(graphs),
        "archives": len(list(root.glob("*.tcm"))),
        "archives_without_graphs": archives_without_graphs,
        "input_errors": input_errors,
        "results": results,
        "full_graph_lowering": lowering,
        "native_runtime_tested": False,
        "native_performance_tested": False,
    }
    encoded = json.dumps(report, indent=2, sort_keys=True)
    if args.json:
        args.json.write_text(encoded + "\n", encoding="utf-8")
    passed = sum(1 for item in results if item["ok"])
    print(
        f"[CUDA TCM] graphs={len(graphs)} targets={[target.sm for target in targets]} "
        f"pass={passed} fail={len(results) - passed} "
        f"full_graph={lowering['full_graph']} "
        f"qualified={lowering['qualified_targets']}"
    )
    for item in results:
        if not item["ok"]:
            print(f"[FAIL] {item['sm']} {item['archive']}:{item['graph']}: {item['diagnostic']}")
    # A partial inventory is never a successful full-graph gate, even if all
    # extracted modules happened to lower successfully.
    return 0 if bool(lowering["full_graph"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
