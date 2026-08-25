"""Single source of truth for target-qualified AOT compilation profiles.

The compiler suite and its background orchestrator must agree on the exact
target IDs from ``aot_tcm/target_manifest.json``.  Keeping a second hand-written
list in either script made it possible to compile a profile that the runtime
could not resolve (or to forget a profile entirely).  This module only reads
the manifest and performs no Taichi/GPU initialization, so it is safe to use
from build tooling and filesystem audits.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
SUPPORTED_BACKENDS = ("cpu", "vulkan", "opengl", "gles", "cuda")
# Build jobs use these suffixes while atomically replacing a target artifact.
# They are not release modules and must not make an otherwise complete target
# appear invalid during a read-only audit.
TEMPORARY_TCM_SUFFIXES = (".staging.tcm", ".next.tcm", ".previous.tcm")

_ARCH_ALIASES = {
    "amd64": "x86_64",
    "x86_64": "x86_64",
    "x64": "x86_64",
    "aarch64": "arm64",
    "arm64-v8a": "arm64",
    "armv8": "arm64",
}
_OS_ALIASES = {
    "win32": "windows",
    "windows": "windows",
    "linux": "linux",
    "android": "android",
}


def _canonical(value: object, default: str = "unknown") -> str:
    raw = str(value or "").strip().lower()
    return raw or default


def _canonical_arch(value: object) -> str:
    return _ARCH_ALIASES.get(_canonical(value), _canonical(value))


def _canonical_os(value: object) -> str:
    raw = _canonical(value)
    return _OS_ALIASES.get(raw, raw)


def _validate_identity_token(label: str, value: str) -> str:
    """Reject manifest identity values that can escape an artifact root.

    Target IDs are used as directory names by the artifact auditor and build
    tooling.  Canonicalization intentionally accepts aliases, but it must not
    turn a hand-edited manifest value such as ``../outside`` or ``C:`` into a
    path component outside the selected artifact root.  Keep this check
    narrow: existing target/vendor tokens may still contain hyphens or dots.
    """

    if value in {".", ".."} or any(
        marker in value for marker in ("/", "\\", ":", "\x00")
    ) or any(ord(char) < 32 for char in value):
        raise ValueError(f"unsafe {label} in AOT target identity: {value!r}")
    return value


def _canonical_backend(value: object, os_name: str) -> str:
    raw = _canonical(value, "cpu")
    # Match TargetSpec: Android desktop OpenGL is not a valid artifact ID;
    # mobile compute artifacts are GLES-qualified instead.
    if raw == "opengl" and os_name == "android":
        return "gles"
    return raw


def target_id_from_entry(entry: Mapping[str, object]) -> str:
    """Build the same target ID contract used by ``TargetSpec``."""

    os_name = _canonical_os(entry.get("os"))
    backend = _canonical_backend(entry.get("backend"), os_name)
    arch = _canonical_arch(entry.get("arch"))
    vendor = _canonical(entry.get("vendor"))
    variant = _canonical(entry.get("variant"), "") if entry.get("variant") else ""
    parts = [backend, arch]
    if os_name != "unknown":
        parts.append(os_name)
    if vendor != "unknown" and backend in {"cuda", "vulkan", "gles", "opengl"}:
        parts.append(vendor)
    if variant:
        parts.append(variant)
    return "_".join(parts)


def validate_target_identity(
    entry: Mapping[str, object], *, expected_target: str | None = None
) -> dict[str, str]:
    """Normalize and validate backend/architecture/vendor identity.

    This is deliberately stricter than filename canonicalization: a CUDA
    target without an NVIDIA vendor is not a valid CUDA profile, and an
    explicitly requested target ID must round-trip to the same canonical
    identity before build tooling accepts it.
    """

    if not isinstance(entry, Mapping):
        raise ValueError("AOT target entry must be an object")
    os_name = _canonical_os(entry.get("os"))
    backend = _canonical_backend(entry.get("backend"), os_name)
    if backend not in SUPPORTED_BACKENDS:
        raise ValueError(f"unsupported backend in AOT target entry: {backend}")
    arch = _canonical_arch(entry.get("arch"))
    vendor = _canonical(entry.get("vendor"))
    _validate_identity_token("backend", backend)
    _validate_identity_token("architecture", arch)
    _validate_identity_token("OS", os_name)
    _validate_identity_token("vendor", vendor)
    if entry.get("variant"):
        _validate_identity_token("variant", _canonical(entry.get("variant"), ""))
    if backend == "cuda" and vendor != "nvidia":
        raise ValueError("CUDA target identity requires vendor=nvidia")
    target_id = target_id_from_entry(entry)
    if expected_target is not None and target_id != str(expected_target):
        raise ValueError(
            f"target identity {target_id!r} does not match expected {expected_target!r}"
        )
    return {
        "target_id": target_id,
        "backend": backend,
        "arch": arch,
        "os": os_name,
        "vendor": vendor,
    }


def _load_target_backends() -> dict[str, str]:
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"AOT target manifest does not exist: {MANIFEST_PATH}")
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = payload.get("target_matrix")
    if not isinstance(entries, list) or not entries:
        raise ValueError("AOT target manifest has no target_matrix entries")
    result: dict[str, str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("AOT target manifest contains a non-object target entry")
        identity = validate_target_identity(entry)
        backend = identity["backend"]
        target_id = identity["target_id"]
        previous = result.get(target_id)
        if previous is not None:
            if previous != backend:
                raise ValueError(f"duplicate target ID with conflicting backend: {target_id}")
            # Two rows with the same canonical identity are ambiguous even
            # when their backend string agrees (for example x86_64/windows
            # and amd64/win32).  Failing here keeps compiler and release
            # selectors from silently choosing the last row.
            raise ValueError(f"duplicate target ID in AOT target manifest: {target_id}")
        result[target_id] = backend
    return result


TARGET_BACKENDS = _load_target_backends()
SUPPORTED_TARGETS = tuple(TARGET_BACKENDS)


def backend_for_target(target: str) -> str:
    """Return the manifest backend for an exact target ID."""

    try:
        return TARGET_BACKENDS[str(target)]
    except KeyError as error:
        raise ValueError(f"unsupported AOT target: {target}") from error


def target_entry_for_id(target: str) -> dict[str, object]:
    """Return the manifest entry for one exact target ID.

    This is a pure build-tool lookup.  It does not initialize Taichi, a native
    bridge, or a GPU context.
    """

    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries = payload.get("target_matrix")
    if not isinstance(entries, list):
        raise ValueError("AOT target manifest has no target_matrix entries")
    requested = str(target)
    for entry in entries:
        if isinstance(entry, dict) and target_id_from_entry(entry) == requested:
            return dict(entry)
    raise ValueError(f"unsupported AOT target: {requested}")


def target_runtime_report(
    manifest_path: str | Path = MANIFEST_PATH,
) -> dict[str, object]:
    """Return a fail-closed qualification report for every manifest target.

    ``target_matrix`` describes what can be built, while
    ``runtime_requirements`` describes what has actually been qualified.  The
    two sections are intentionally independent in the manifest, so a target
    with no requirement entry must not be mistaken for a native runtime
    target.  This pure report makes that omission visible to release tooling
    without initializing Taichi or changing runtime dispatch.
    """

    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("target_matrix")
    if not isinstance(entries, list) or not entries:
        raise ValueError("AOT target manifest has no target_matrix entries")
    requirements = payload.get("runtime_requirements", {})
    if requirements is None:
        requirements = {}
    if not isinstance(requirements, Mapping):
        raise ValueError("runtime_requirements must be an object")

    # Runtime requirements are a qualification contract keyed by the exact
    # canonical target id.  A stale/orphan requirement otherwise looks valid
    # in a manifest review while never being consumed by any target entry.
    # Keep this audit read-only, but expose the mismatch and fail closed so a
    # release tool cannot treat the orphan evidence as shipped support.
    declared_target_ids = {
        target_id_from_entry(raw_entry)
        for raw_entry in entries
        if isinstance(raw_entry, Mapping)
    }
    orphan_runtime_requirements = tuple(
        sorted(
            str(target_id)
            for target_id in requirements
            if str(target_id) not in declared_target_ids
        )
    )

    records: list[dict[str, object]] = []
    seen_target_ids: set[str] = set()
    for raw_entry in entries:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("AOT target manifest contains a non-object target entry")
        # Runtime qualification must use the same canonical identity gate as
        # artifact auditing.  Otherwise a hand-edited CUDA row with a
        # non-NVIDIA vendor could be promoted solely because it carries a
        # native_runtime flag and an evidence ID.
        identity = validate_target_identity(raw_entry)
        target_id = identity["target_id"]
        if target_id in seen_target_ids:
            # Runtime qualification is keyed by canonical target ID.  Two
            # manifest rows that normalize to the same ID would otherwise
            # produce duplicate records and make status counts/order
            # dependent, allowing an ambiguous target to look qualified.
            raise ValueError(f"duplicate target ID in runtime report: {target_id}")
        seen_target_ids.add(target_id)
        requirement = requirements.get(target_id)
        if requirement is not None and not isinstance(requirement, Mapping):
            raise ValueError(f"runtime requirement {target_id!r} must be an object")
        qualification = (
            str(requirement.get("qualification", "") or "").strip().lower()
            if requirement is not None
            else ""
        )
        native_runtime_claim = bool(
            requirement is not None and requirement.get("native_runtime") is True
        )
        # A boolean in the manifest is not runtime evidence.  Require a
        # stable, externally traceable probe/qualification identifier before
        # exposing ``native_runtime`` to release tooling.  This mirrors the
        # ARM/native matrix gate and keeps hand-edited manifests fail-closed.
        runtime_evidence_id = (
            str(requirement.get("runtime_evidence_id", "") or "").strip()
            if requirement is not None
            else ""
        )
        # A true flag and an evidence ID are insufficient on their own.  The
        # qualification enum is part of the same contract; otherwise a
        # contradictory custom manifest (for example ``compile_only`` plus
        # ``native_runtime=true``) would expose ``native_runtime=True`` while
        # reporting an unqualified status.  Keep the report internally
        # consistent and fail closed until all three fields agree.
        native_runtime = bool(
            native_runtime_claim
            and qualification == "native_runtime"
            and runtime_evidence_id
        )
        if qualification == "native_runtime" and native_runtime:
            status = "native_runtime"
        elif qualification == "compile_only":
            status = "compile_only"
        else:
            status = "unverified"
        missing = []
        if requirement is None:
            missing.append("runtime_requirements")
        if not native_runtime:
            missing.append("native_runtime_evidence")
        if native_runtime_claim and not runtime_evidence_id:
            missing.append("runtime_evidence_id")
        if native_runtime_claim and qualification != "native_runtime":
            missing.append("native_runtime_qualification")
        records.append(
            {
                "target_id": target_id,
                "backend": identity["backend"],
                "arch": identity["arch"],
                "os": identity["os"],
                "vendor": identity["vendor"],
                "runtime_requirement_present": requirement is not None,
                "qualification": qualification or None,
                "native_runtime": native_runtime,
                "runtime_evidence_id": runtime_evidence_id or None,
                "status": status,
                "fail_closed": status != "native_runtime",
                "missing": tuple(missing),
            }
        )
    status_counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("native_runtime", "compile_only", "unverified")
    }
    backend_summary: dict[str, dict[str, object]] = {}
    for backend in SUPPORTED_BACKENDS:
        backend_records = [record for record in records if record["backend"] == backend]
        backend_counts = {
            status: sum(record["status"] == status for record in backend_records)
            for status in ("native_runtime", "compile_only", "unverified")
        }
        backend_total = len(backend_records)
        backend_summary[backend] = {
            "target_count": backend_total,
            "native_runtime_count": backend_counts["native_runtime"],
            "compile_only_count": backend_counts["compile_only"],
            "unverified_count": backend_counts["unverified"],
            "native_runtime_percent": round(
                backend_counts["native_runtime"] * 100.0 / backend_total, 2
            ) if backend_total else 0.0,
            "fail_closed": any(record["fail_closed"] for record in backend_records),
        }
    non_native_count = len(records) - status_counts["native_runtime"]
    return {
        "manifest": str(path.resolve()),
        "target_count": len(records),
        "orphan_runtime_requirements": orphan_runtime_requirements,
        "status_counts": status_counts,
        "backend_summary": backend_summary,
        "native_runtime_count": status_counts["native_runtime"],
        "compile_only_count": status_counts["compile_only"],
        "unverified_count": status_counts["unverified"],
        "native_runtime_percent": round(
            status_counts["native_runtime"] * 100.0 / len(records), 2
        ),
        "non_native_count": non_native_count,
        "records": tuple(records),
        # A manifest is globally safe only when every declared target has
        # native qualification and there are no orphan requirements.
        "fail_closed": bool(orphan_runtime_requirements) or non_native_count > 0,
    }


def target_artifact_report(
    manifest_path: str | Path = MANIFEST_PATH,
    artifact_root: str | Path | None = None,
) -> dict[str, object]:
    """Audit target-directory and filename identity without loading a TCM.

    The target matrix is a build contract, not proof that an artifact was
    actually shipped.  This read-only audit checks that every declared target
    has a target-qualified directory and at least one ``.tcm`` whose filename
    ends in the exact canonical target ID.  A directory containing a stale or
    foreign target filename is reported as invalid rather than being silently
    accepted.  It intentionally does not inspect or initialize Taichi; native
    runtime qualification remains the separate ``target_runtime_report``
    contract.
    """

    path = Path(manifest_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("target_matrix")
    if not isinstance(entries, list) or not entries:
        raise ValueError("AOT target manifest has no target_matrix entries")
    root = Path(artifact_root) if artifact_root is not None else path.parent
    records: list[dict[str, object]] = []
    declared_ids: set[str] = set()
    for raw_entry in entries:
        if not isinstance(raw_entry, Mapping):
            raise ValueError("AOT target manifest contains a non-object target entry")
        # Do not let the filesystem audit bless an artifact for a target that
        # the canonical registry itself would reject (for example CUDA with
        # a non-NVIDIA vendor).  Custom/staged manifests bypass
        # ``_load_target_backends()``, so this explicit identity gate is
        # required before any directory or filename can count as present.
        identity = validate_target_identity(raw_entry)
        target_id = identity["target_id"]
        if target_id in declared_ids:
            raise ValueError(f"duplicate target ID in artifact audit: {target_id}")
        declared_ids.add(target_id)
        target_dir = root / target_id
        tcm_files = sorted(target_dir.glob("*.tcm")) if target_dir.is_dir() else []
        suffix = f"_{target_id}.tcm"
        # Atomic replacement files append ``.next.tcm``/``.staging.tcm`` to
        # the complete artifact name (for example
        # ``gaussian_cpu_x86_64_windows.next.tcm``).  Checking the target
        # suffix first would miss that marker because the filename no longer
        # ends in ``_<target>.tcm``.  Classify by the marker itself so a
        # half-written replacement is diagnosed as temporary rather than
        # incorrectly reported as a foreign/stale artifact.
        temporary_files = [
            item.name for item in tcm_files
            if any(item.name.lower().endswith(suffix) for suffix in TEMPORARY_TCM_SUFFIXES)
        ]
        audit_files = [item for item in tcm_files if item.name not in temporary_files]
        valid_files = [
            item for item in audit_files
            if item.is_file() and item.name.endswith(suffix)
            and item.name[: -len(suffix)]
        ]
        invalid_files = [
            item.name for item in audit_files
            if not (item.is_file() and item.name.endswith(suffix)
                    and item.name[: -len(suffix)])
        ]
        directory_present = target_dir.is_dir()
        identity_valid = bool(directory_present and not invalid_files)
        status = "present" if identity_valid and valid_files else "missing"
        missing_reasons: list[str] = []
        if not directory_present:
            missing_reasons.append("target_directory")
        elif not valid_files:
            missing_reasons.append("target_qualified_tcm")
            # A build can leave only an atomic replacement file behind after
            # an interrupted compile.  Keep the target fail-closed, but make
            # the diagnosis actionable instead of presenting it as a generic
            # missing module.
            if temporary_files:
                missing_reasons.append("temporary_only_tcm")
        if invalid_files:
            missing_reasons.append("foreign_or_stale_tcm")
        records.append(
            {
                "target_id": target_id,
                "directory": str(target_dir.resolve()),
                "directory_present": directory_present,
                "artifact_count": len(valid_files),
                "artifact_names": tuple(item.name for item in valid_files),
                "invalid_artifact_names": tuple(sorted(invalid_files)),
                "temporary_artifact_names": tuple(sorted(temporary_files)),
                "missing_reasons": tuple(missing_reasons),
                "artifact_identity_valid": identity_valid and bool(valid_files),
                "status": status,
                "fail_closed": status != "present",
            }
        )
    unexpected_dirs = tuple(
        sorted(
            item.name for item in root.iterdir()
            if item.is_dir() and item.name != "_quarantine"
            and item.name not in declared_ids
        )
    ) if root.is_dir() else tuple()
    # A target-qualified artifact is expected below its target directory.  A
    # root-level TCM can otherwise look shipped while being unreachable by
    # target-aware loaders, so expose it as a stale/foreign artifact and keep
    # the audit fail-closed.  This is deliberately read-only.
    unexpected_root_artifacts = tuple(
        sorted(
            item.name for item in root.glob("*.tcm")
            if item.is_file()
        )
    ) if root.is_dir() else tuple()
    temporary_root_artifacts = tuple(
        sorted(
            item.name for item in root.glob("*.tcm")
            if item.is_file()
            and any(item.name.lower().endswith(suffix) for suffix in TEMPORARY_TCM_SUFFIXES)
        )
    ) if root.is_dir() else tuple()
    unexpected_root_artifacts = tuple(
        item for item in unexpected_root_artifacts if item not in temporary_root_artifacts
    )
    present_count = sum(record["status"] == "present" for record in records)
    missing_count = len(records) - present_count
    backend_summary: dict[str, dict[str, object]] = {}
    for backend in SUPPORTED_BACKENDS:
        backend_records = [record for record in records if record["target_id"].startswith(f"{backend}_")]
        backend_summary[backend] = {
            "target_count": len(backend_records),
            "present_count": sum(record["status"] == "present" for record in backend_records),
            "missing_count": sum(record["status"] != "present" for record in backend_records),
            "fail_closed": any(record["fail_closed"] for record in backend_records),
        }
    return {
        "manifest": str(path.resolve()),
        "artifact_root": str(root.resolve()),
        "target_count": len(records),
        "present_count": present_count,
        "missing_count": missing_count,
        "missing_targets": tuple(
            record["target_id"] for record in records if record["status"] != "present"
        ),
        "backend_summary": backend_summary,
        "unexpected_target_dirs": unexpected_dirs,
        "unexpected_root_artifacts": unexpected_root_artifacts,
        "temporary_root_artifacts": temporary_root_artifacts,
        "records": tuple(records),
        "fail_closed": (
            missing_count > 0
            or bool(unexpected_dirs)
            or bool(unexpected_root_artifacts)
        ),
    }


def validate_target_registry() -> None:
    """Raise if the manifest has drifted from the compiler target contract."""

    if set(TARGET_BACKENDS) != set(SUPPORTED_TARGETS):  # pragma: no cover
        raise AssertionError("AOT target registry is internally inconsistent")


__all__ = [
    "MANIFEST_PATH",
    "SUPPORTED_BACKENDS",
    "SUPPORTED_TARGETS",
    "TARGET_BACKENDS",
    "backend_for_target",
    "target_entry_for_id",
    "target_runtime_report",
    "target_artifact_report",
    "target_id_from_entry",
    "validate_target_identity",
    "validate_target_registry",
]
