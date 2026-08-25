"""Audit target-qualified AOT coverage without initializing a GPU backend.

This is intentionally a filesystem/manifest audit.  It does not claim that a
TCM archive is numerically correct or runtime-compatible; those properties are
covered by the backend smoke and parity suites.  The report separates direct
vendor profiles from safe generic graphics profiles so a complete generic
Vulkan/OpenGL suite is not mistaken for a vendor-specific compilation.

Usage::

    python taichi_vision/taichi_algorithm/aot_py/audit_aot_matrix.py
    python taichi_vision/taichi_algorithm/aot_py/audit_aot_matrix.py --json
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parents[3]
AOT_ROOT = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
AOT_DLL_ROOT = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
MANIFEST_PATH = AOT_ROOT / "target_manifest.json"
COMPILER_PATH = PROJECT_ROOT / "taichi_vision" / "taichi_algorithm" / "aot_py" / "compile_aot_backend_suite.py"

# Load the pure target registry without importing ``taichi_vision.taichi_aot``
# itself.  The package initializer creates a GPU engine, which would make a
# filesystem-only audit unexpectedly claim an OpenGL context.
_TARGETS_PATH = PROJECT_ROOT / "taichi_vision" / "taichi_aot" / "artifact_targets.py"
_SPEC = importlib.util.spec_from_file_location("pixel_refine_audit_artifact_targets", _TARGETS_PATH)
if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - repository invariant
    raise ImportError(f"cannot load target registry: {_TARGETS_PATH}")
_TARGETS = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _TARGETS
_SPEC.loader.exec_module(_TARGETS)
TargetSpec = _TARGETS.TargetSpec

try:
    from .target_registry import TARGET_BACKENDS
except ImportError:  # Direct script execution.
    from target_registry import TARGET_BACKENDS


def _algorithms_for_target(target_dir: Path) -> list[str]:
    target_id = target_dir.name
    suffix = f"_{target_id}.tcm"
    algorithms = []
    for artifact in sorted(target_dir.glob("*.tcm")):
        if artifact.name.endswith(suffix):
            algorithms.append(artifact.name[: -len(suffix)])
        else:
            # A non-qualified archive is deliberately reported separately.
            algorithms.append(f"LEGACY:{artifact.stem}")
    return sorted(algorithms)


def _compiler_artifact_names() -> set[str]:
    """Read JOBS without importing Taichi or initializing a native context."""

    tree = ast.parse(COMPILER_PATH.read_text(encoding="utf-8"), filename=str(COMPILER_PATH))
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "JOBS" for target in node.targets)
    )
    jobs = ast.literal_eval(assignment.value)
    names = set(jobs)
    names.update(alias for value in jobs.values() for alias in value[3])
    return names


def _compiler_job_summary() -> dict[str, Any]:
    """Validate the declarative JOBS registry without importing Taichi.

    Importing compiler modules can initialize a backend or create an OpenGL
    context.  AST validation is enough to catch the common registry drift
    failure: a job points at a deleted module or a renamed callable.
    """
    tree = ast.parse(
        COMPILER_PATH.read_text(encoding="utf-8"), filename=str(COMPILER_PATH)
    )
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "JOBS"
            for target in node.targets
        )
    )
    jobs = ast.literal_eval(assignment.value)
    # Compiler modules are now colocated with their algorithm families.  The
    # orchestrator keeps a declarative short-name -> package map so it can
    # launch each compiler in a clean subprocess.  The audit must resolve the
    # same map; checking only ``aot_py/<module>.py`` falsely reported every
    # colocated compiler as missing.
    package_assignment = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "COLOCATED_COMPILER_PACKAGES"
                for target in node.targets
            )
        ),
        None,
    )
    colocated_packages = (
        ast.literal_eval(package_assignment.value)
        if package_assignment is not None
        else {}
    )
    missing_modules: list[str] = []
    missing_callables: list[str] = []
    for name, value in jobs.items():
        module_name, function_name = value[0], value[1]
        package_name = colocated_packages.get(module_name)
        if package_name:
            package_parts = str(package_name).split(".")
            module_path = PROJECT_ROOT.joinpath(*package_parts, f"{module_name}.py")
        else:
            module_path = COMPILER_PATH.with_name(f"{module_name}.py")
        if not module_path.is_file():
            missing_modules.append(f"{name}:{module_name}")
            continue
        try:
            module_tree = ast.parse(
                module_path.read_text(encoding="utf-8-sig"), filename=str(module_path)
            )
        except (OSError, SyntaxError) as error:
            missing_callables.append(f"{name}:{function_name} ({error})")
            continue
        definitions = {
            node.name
            for node in module_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        }
        if function_name not in definitions:
            missing_callables.append(f"{name}:{function_name}")
    return {
        "job_count": len(jobs),
        "artifact_count": len(_compiler_artifact_names()),
        "missing_modules": sorted(missing_modules),
        "missing_callables": sorted(missing_callables),
    }


def _payload_summary(target_dir: Path, target: TargetSpec) -> dict[str, Any]:
    """Inspect every archive payload, not just its target-qualified filename."""
    suffix = f"_{target_dir.name}.tcm"
    kinds: set[str] = set()
    triples: set[str] = set()
    invalid: list[str] = []
    for artifact in sorted(target_dir.glob(f"*{suffix}")):
        try:
            with zipfile.ZipFile(artifact, "r") as archive:
                names = set(archive.namelist())
                graphics = "graphs.json" in names and any(
                    name.endswith(".spv") for name in names
                )
                llvm_names = [name for name in names if name.endswith(".ll")]
                llvm = "graphs.tcb" in names and bool(llvm_names)
                if graphics:
                    kinds.add("graphics_spirv")
                elif llvm:
                    kinds.add("llvm_tbc")
                    text = archive.read(llvm_names[0]).decode(
                        "utf-8", errors="replace"
                    )
                    found = re.findall(r'target triple = "([^"]+)"', text)
                    # CUDA TBCs may contain host and device LLVM modules;
                    # retain every declared triple instead of depending on
                    # archive/module ordering.
                    triples.update(found)
                else:
                    kinds.add("unknown")
                valid = _TARGETS._artifact_matches_target(artifact, target)
                if not valid:
                    invalid.append(artifact.name)
        except (OSError, zipfile.BadZipFile, KeyError) as error:
            invalid.append(f"{artifact.name}: {error}")
    return {
        "payload_kinds": sorted(kinds),
        "llvm_triples": sorted(triples),
        "payload_invalid": sorted(invalid),
    }


def _bridge_summary(target: TargetSpec) -> dict[str, Any]:
    """Check the bridge/runtime pair required by one manifest target."""

    # Desktop vendor profiles intentionally share the ABI-matched generic
    # bridge. ARM/Linux/Android profiles are isolated because their ELF ABI
    # and C-API runtime differ from the Windows host.
    bridge_id = target.backend if target.os == "windows" else target.target_id
    bridge_dir = AOT_DLL_ROOT / bridge_id
    if target.os == "windows":
        bridge_candidates = (
            bridge_dir / "taichi_aot_engine.dll",
            bridge_dir / "taichi_aot_engine_renderer.dll",
        )
        runtime_candidates = (bridge_dir / "taichi_c_api.dll",)
    else:
        bridge_candidates = (bridge_dir / "taichi_aot_engine.so",)
        runtime_candidates = (bridge_dir / "libtaichi_c_api.so",)
    bridge = next((path for path in bridge_candidates if path.is_file()), None)
    runtime = next((path for path in runtime_candidates if path.is_file()), None)
    missing = []
    if bridge is None:
        missing.append(bridge_candidates[0].name)
    if runtime is None:
        missing.append(runtime_candidates[0].name)
    return {
        "bridge_target": bridge_id,
        "bridge_files": sorted(
            path.name for path in (*bridge_candidates, *runtime_candidates) if path.is_file()
        ),
        "bridge_missing": missing,
    }


def _target_entry(entry: dict[str, Any]) -> TargetSpec:
    return TargetSpec(
        backend=entry.get("backend", "cpu"),
        arch=entry.get("arch", "unknown"),
        os=entry.get("os", "unknown"),
        vendor=entry.get("vendor", "unknown"),
        abi=entry.get("abi", ""),
        variant=entry.get("variant", ""),
    )


def _runtime_gate(target: TargetSpec, requirement: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return an auditable runtime qualification for one target.

    Cross-compilation and static ELF checks are intentionally insufficient for
    an ARM native claim.  The gate opens only when the manifest explicitly
    carries ``native_runtime=true`` plus a runtime evidence identifier.
    """

    value = requirement if isinstance(requirement, Mapping) else {}
    qualification = str(value.get("qualification", "") or "").strip().lower()
    native_runtime = bool(
        qualification == "native_runtime"
        and value.get("native_runtime") is True
        and str(value.get("runtime_evidence_id", "") or "").strip()
    )
    return {
        "qualification": qualification or "unverified",
        "native_runtime": native_runtime,
        "fail_closed": bool(target.is_arm and not native_runtime),
    }


def inventory() -> dict[str, Any]:
    compiler_artifacts = _compiler_artifact_names()
    compiler_jobs = _compiler_job_summary()
    directories = {}
    for target_dir in sorted(AOT_ROOT.iterdir() if AOT_ROOT.is_dir() else ()):
        if not target_dir.is_dir() or target_dir.name.startswith("."):
            continue
        algorithms = _algorithms_for_target(target_dir)
        directories[target_dir.name] = {
            "artifact_count": len(algorithms),
            "algorithms": algorithms,
            "legacy_artifacts": [name for name in algorithms if name.startswith("LEGACY:")],
        }

    manifest: dict[str, Any] = {}
    if MANIFEST_PATH.is_file():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    manifest_ids = {
        _target_entry(entry).target_id
        for entry in manifest.get("target_matrix", [])
        if isinstance(entry, dict)
    }
    compiler_ids = set(TARGET_BACKENDS)

    expected = []
    runtime_requirements = manifest.get("runtime_requirements", {})
    for entry in manifest.get("target_matrix", []):
        target = _target_entry(entry)
        runtime_gate = _runtime_gate(
            target, runtime_requirements.get(target.target_id, {})
        )
        direct = directories.get(target.target_id)
        generic_id = TargetSpec(
            backend=target.backend,
            arch=target.arch,
            os=target.os,
            abi=target.abi,
            variant=target.variant,
        ).target_id
        generic = directories.get(generic_id)
        direct_names = {
            name for name in (direct or {}).get("algorithms", ())
            if not name.startswith("LEGACY:")
        }
        generic_names = {
            name for name in (generic or {}).get("algorithms", ())
            if not name.startswith("LEGACY:")
        }
        generic_only = sorted(generic_names - direct_names)
        effective_names = direct_names | generic_names
        direct_missing = sorted(compiler_artifacts - direct_names)
        direct_extra = sorted(direct_names - compiler_artifacts)
        payload = _payload_summary(
            AOT_ROOT / target.target_id,
            target,
        ) if direct else {
            "payload_kinds": [],
            "llvm_triples": [],
            "payload_invalid": [],
        }
        bridge = _bridge_summary(target)
        expected.append(
            {
                "target_id": target.target_id,
                "backend": target.backend,
                "arch": target.arch,
                "os": target.os,
                "vendor": target.vendor,
                "direct": bool(direct),
                "direct_artifacts": len(direct_names),
                "compiler_expected_artifacts": len(compiler_artifacts),
                "direct_missing_artifacts": direct_missing,
                "direct_extra_artifacts": direct_extra,
                "effective_missing_artifacts": sorted(compiler_artifacts - effective_names),
                "generic_fallback_target": (
                    generic_id
                    if generic and generic_id != target.target_id and generic_only
                    else None
                ),
                "generic_fallback_artifacts": len(generic_names) if generic_only else 0,
                "generic_only_algorithms": generic_only,
                "effective_artifacts": len(effective_names),
                "runtime_qualification": runtime_gate["qualification"],
                "native_runtime": runtime_gate["native_runtime"],
                "runtime_fail_closed": runtime_gate["fail_closed"],
                **payload,
                **bridge,
            }
        )

    runtime_files = {}
    for target_id in ("cpu_arm64_android", "cpu_arm64_linux", "cuda_arm64_linux_nvidia"):
        target_dir = AOT_ROOT / target_id
        runtime_files[target_id] = sorted(
            path.name
            for path in target_dir.glob("runtime_*.bc")
            if path.is_file()
        )

    bridge_files = {}
    # Report every target-specific ELF bridge, including newly built
    # headless OpenGL/GLES Linux profiles. Desktop Windows vendor profiles
    # deliberately share the generic backend DLL and are checked per manifest
    # entry above instead of duplicated here.
    target_specific_bridges = sorted(
        {
            _target_entry(entry).target_id
            for entry in manifest.get("target_matrix", [])
            if isinstance(entry, dict) and entry.get("os") != "windows"
        }
    )
    for target_id in target_specific_bridges:
        bridge_dir = AOT_DLL_ROOT / target_id
        bridge_files[target_id] = sorted(
            path.name
            for path in bridge_dir.glob("taichi_aot_engine.*")
            if path.is_file()
        )
        c_api = bridge_dir / "libtaichi_c_api.so"
        if c_api.is_file():
            bridge_files[target_id].append(c_api.name)

    return {
        "schema_version": 1,
        "artifact_root": str(AOT_ROOT),
        "directories": directories,
        "compiler_artifacts": sorted(compiler_artifacts),
        "compiler_jobs": compiler_jobs,
        "compiler_target_ids": sorted(compiler_ids),
        "compiler_manifest_missing": sorted(manifest_ids - compiler_ids),
        "compiler_manifest_extra": sorted(compiler_ids - manifest_ids),
        "runtime_files": runtime_files,
        "bridge_files": bridge_files,
        "runtime_requirements": manifest.get("runtime_requirements", {}),
        "manifest_targets": expected,
    }


def _print_text(report: dict[str, Any]) -> None:
    print(f"AOT root: {report['artifact_root']}")
    print("\nTarget directories:")
    for target_id, data in report["directories"].items():
        legacy = len(data["legacy_artifacts"])
        suffix = f", legacy={legacy}" if legacy else ""
        print(f"  {target_id:34s} {data['artifact_count']:3d} TCM{suffix}")
    print("\nTarget runtime bitcode:")
    for target_id, files in report.get("runtime_files", {}).items():
        print(f"  {target_id:34s} {', '.join(files) if files else 'MISSING'}")
    print("\nTarget native bridges:")
    for target_id, files in report.get("bridge_files", {}).items():
        print(f"  {target_id:34s} {', '.join(files) if files else 'MISSING'}")
    missing = report.get("compiler_manifest_missing", [])
    extra = report.get("compiler_manifest_extra", [])
    print("\nCompiler/manifest registry:")
    print(
        f"  compiler-targets={len(report.get('compiler_target_ids', []))} "
        f"manifest-missing={len(missing)} manifest-extra={len(extra)}"
    )
    if missing:
        print(f"  missing-from-compiler: {', '.join(missing)}")
    if extra:
        print(f"  extra-in-compiler: {', '.join(extra)}")
    jobs = report.get("compiler_jobs", {})
    print(
        f"  source-jobs={jobs.get('job_count', 0)} "
        f"artifact-names={jobs.get('artifact_count', 0)} "
        f"missing-modules={len(jobs.get('missing_modules', []))} "
        f"missing-callables={len(jobs.get('missing_callables', []))}"
    )
    if jobs.get("missing_modules"):
        print(f"  missing-job-modules: {', '.join(jobs['missing_modules'])}")
    if jobs.get("missing_callables"):
        print(f"  missing-job-callables: {', '.join(jobs['missing_callables'])}")
    requirements = report.get("runtime_requirements", {})
    if requirements:
        print("\nRuntime validation status:")
        for target_id, data in requirements.items():
            print(f"  {target_id:34s} {data.get('validation_status', 'unspecified')}")
    print("\nManifest coverage:")
    for item in report["manifest_targets"]:
        if item["direct"]:
            status = f"direct={item['direct_artifacts']} effective={item['effective_artifacts']}"
            if item["generic_fallback_target"]:
                status += f" +generic={item['generic_fallback_target']} ({item['generic_fallback_artifacts']})"
        elif item["generic_fallback_target"]:
            status = f"generic={item['generic_fallback_target']} ({item['generic_fallback_artifacts']})"
        else:
            status = "MISSING"
        if item.get("payload_invalid"):
            status += f" payload-invalid={len(item['payload_invalid'])}"
        if item.get("effective_missing_artifacts"):
            status += f" compiler-missing={len(item['effective_missing_artifacts'])}"
        if item.get("direct_extra_artifacts"):
            status += f" compiler-extra={len(item['direct_extra_artifacts'])}"
        if item.get("bridge_missing"):
            status += f" bridge-missing={','.join(item['bridge_missing'])}"
        if item.get("runtime_fail_closed"):
            status += " runtime=compile-only/fail-closed"
        elif item.get("native_runtime"):
            status += " runtime=native-qualified"
        print(f"  {item['target_id']:34s} {status}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--output", type=Path, help="write JSON report to this path")
    args = parser.parse_args()
    report = inventory()
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_text(report)


if __name__ == "__main__":
    main()
