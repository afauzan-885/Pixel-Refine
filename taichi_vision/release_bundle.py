"""Manifest-driven native AOT payload planner for release builders.

The module intentionally sits at ``taichi_vision`` (whose package initializer
is side-effect free) so Nuitka/PyInstaller can use it without importing the
runtime package or creating a GPU context.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import platform
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


ALIASES = {"cpu": "cpu", "x86": "cpu", "x64": "cpu", "cuda": "cuda", "vulkan": "vulkan", "vk": "vulkan", "opengl": "opengl", "gl": "opengl", "gles": "gles"}
TEMPORARY_SUFFIXES = (".staging.tcm", ".next.tcm", ".previous.tcm")


def _canonical_bundle_os(value: str | None) -> str:
    raw = str(value or "").strip().lower()
    return {"win32": "windows", "windows": "windows", "linux": "linux", "android": "android"}.get(raw, raw)


def _canonical_bundle_arch(value: str | None) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    return {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64-v8a": "arm64",
        "arm64": "arm64",
    }.get(raw, raw)


def detect_bundle_host() -> tuple[str, str]:
    """Return target OS/architecture for packaging selection.

    Explicit Pixel Refine overrides take precedence, followed by the generic
    target variables used by cross-build tooling. The historical Windows
    x86_64 defaults remain the final fallback for backward compatibility.
    """

    os_value = os.environ.get("PIXEL_REFINE_BUNDLE_TARGET_OS") or os.environ.get("TARGET_OS")
    arch_value = os.environ.get("PIXEL_REFINE_BUNDLE_TARGET_ARCH") or os.environ.get("TARGET_ARCH")
    detected_os = _canonical_bundle_os(os_value or ("windows" if os.name == "nt" else sys.platform))
    detected_arch = _canonical_bundle_arch(arch_value or platform.machine())
    return detected_os or "windows", detected_arch or "x86_64"


@dataclass(frozen=True)
class AOTBundlePlan:
    backends: tuple[str, ...]
    target_ids: tuple[str, ...]
    modules: tuple[str, ...]
    artifacts: tuple[Path, ...]
    bridges: tuple[Path, ...]
    data_dirs: tuple[tuple[Path, str], ...]
    staging_dir: Path
    # Populated only when manifest-wide preflight was explicitly requested.
    # Keeping it optional preserves the historical planner payload and cost.
    preflight_report: Mapping[str, Any] | None = None

    @property
    def data_args(self) -> tuple[str, ...]:
        return tuple(f"--include-data-dir={src}={dst}" for src, dst in self.data_dirs)

    def as_dict(self) -> dict[str, Any]:
        return {
            "backends": self.backends,
            "target_ids": self.target_ids,
            "modules": self.modules,
            "artifacts": self.artifacts,
            "bridges": self.bridges,
            "data_dirs": self.data_dirs,
            "data_args": self.data_args,
            "staging_dir": self.staging_dir,
            "preflight_report": self.preflight_report,
        }


def validate_entrypoint(project_root: os.PathLike[str] | str, entrypoint: os.PathLike[str] | str) -> Path:
    """Resolve a packager entrypoint and reject unsafe/missing paths.

    Both release builders accept a relative entrypoint, but an accidental
    absolute path or a path outside the project could otherwise package an
    unrelated script.  This check is build-time only and does not affect the
    public runtime API.
    """

    root = Path(project_root).resolve()
    candidate = Path(entrypoint)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise ValueError(f"packaging entrypoint is outside project root: {entrypoint}") from error
    if resolved.suffix.lower() != ".py":
        raise ValueError(f"packaging entrypoint must be a Python file: {resolved}")
    if not resolved.is_file():
        raise FileNotFoundError(f"packaging entrypoint does not exist: {resolved}")
    return resolved


def _csv(value: str | None, default: str = "") -> tuple[str, ...]:
    raw = default if value is None else value
    return tuple(item.strip() for item in str(raw).split(",") if item.strip())


def _target_id(entry: Mapping[str, Any]) -> str:
    backend = ALIASES.get(str(entry.get("backend", "cpu")).strip().lower(), str(entry.get("backend", "cpu")).strip().lower())
    # CUDA artifacts are tied to NVIDIA's CUDA runtime.  Keep this release
    # planner gate aligned with target_registry/validate_native_bundle so a
    # hand-edited manifest cannot select a non-NVIDIA CUDA target merely
    # because a matching directory happens to exist.
    if backend == "cuda" and str(entry.get("vendor", "unknown")).strip().lower() != "nvidia":
        raise ValueError("CUDA target identity requires vendor=nvidia")
    os_name = _canonical_bundle_os(str(entry.get("os", "unknown")))
    arch = _canonical_bundle_arch(str(entry.get("arch", "unknown")))
    # Android OpenGL profiles are represented by GLES target directories.
    if backend == "opengl" and os_name == "android":
        backend = "gles"
    parts = [backend, arch]

    vendor = str(entry.get("vendor", "unknown")).strip().lower()
    if os_name != "unknown":
        parts.append(os_name)
    if vendor != "unknown" and backend in {"cuda", "vulkan", "opengl", "gles"}:
        parts.append(vendor)
    variant = str(entry.get("variant", "")).strip().lower()
    if variant:
        parts.append(variant)
    return "_".join(parts)


def _safe_target_id(target: str) -> str:
    if not target or Path(target).name != target or target in {".", ".."}:
        raise ValueError(f"unsafe AOT target ID in manifest: {target!r}")
    return target


def _load_manifest(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("unsupported AOT target manifest schema")
    entries = payload.get("target_matrix")
    if not isinstance(entries, list) or not entries:
        raise ValueError("AOT target manifest has no target_matrix")
    # Do not silently discard malformed entries.  The previous list
    # comprehension in the callers skipped non-object rows, which could make
    # a manifest appear complete while the runtime and release bundle used
    # different target sets.  Canonical IDs must also be unique: otherwise
    # the last row wins in ``by_id`` and an artifact can be attributed to the
    # wrong backend/vendor profile.
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise ValueError("AOT target manifest contains a non-object target entry")
        raw_backend = str(entry.get("backend", "cpu")).strip().lower()
        backend = ALIASES.get(raw_backend)
        if backend is None:
            raise ValueError(f"unsupported AOT target backend: {raw_backend!r}")
        # CUDA artifacts are NVIDIA-specific.  Keep the release planner's
        # manifest gate aligned with target_registry/validate_native_bundle so
        # a hand-edited AMD/Intel CUDA row cannot enter target selection and
        # later be mistaken for a valid native profile.
        if backend == "cuda" and str(entry.get("vendor", "unknown")).strip().lower() != "nvidia":
            raise ValueError("CUDA target identity requires vendor=nvidia")
        target_id = _safe_target_id(_target_id(entry))
        if target_id in seen:
            raise ValueError(f"duplicate AOT target ID in manifest: {target_id}")
        seen.add(target_id)
    return payload


def _select_targets(payload: Mapping[str, Any], backends: Sequence[str], targets: Sequence[str], vendors: Sequence[str], host_os: str, host_arch: str) -> tuple[str, ...]:
    entries = [dict(item) for item in payload["target_matrix"] if isinstance(item, Mapping)]
    by_id = {_target_id(item): item for item in entries}
    if targets:
        missing = sorted(set(targets) - set(by_id))
        if missing:
            raise ValueError("requested AOT target(s) are absent: " + ", ".join(missing))
        incompatible = sorted(
            target
            for target in targets
            if _canonical_bundle_arch(str(by_id[target].get("arch", ""))) != host_arch
            or _canonical_bundle_os(str(by_id[target].get("os", ""))) != host_os
        )
        if incompatible:
            raise ValueError(
                "requested AOT target(s) do not match the release host "
                f"{host_arch}/{host_os}: " + ", ".join(incompatible)
            )
        return tuple(_safe_target_id(target) for target in dict.fromkeys(targets))
    vendor_values = {item.lower() for item in vendors}
    include_all_vendors = "all" in vendor_values
    allowed_vendors = None if not vendors or include_all_vendors else vendor_values
    selected: list[str] = []
    for backend in backends:
        candidates = [
            (_target_id(item), item)
            for item in entries
            if ALIASES.get(str(item.get("backend", "")).strip().lower(), str(item.get("backend", "")).strip().lower()) == backend
            and _canonical_bundle_arch(str(item.get("arch", ""))) == host_arch
            and _canonical_bundle_os(str(item.get("os", ""))) == host_os
            and (allowed_vendors is None or str(item.get("vendor", "unknown")).lower() in allowed_vendors)
        ]
        if not candidates:
            raise FileNotFoundError(f"no {backend} target for {host_arch}/{host_os}")
        if include_all_vendors:
            selected.extend(target for target, _item in candidates)
        elif allowed_vendors:
            selected.extend(target for target, _item in candidates)
        elif backend == "opengl":
            # Desktop releases support vendor-neutral GL plus the Intel
            # profile because Intel's renderer has historically required a
            # separate target-qualified artifact. Set
            # PIXEL_REFINE_BUNDLE_VENDORS=unknown to request generic-only.
            preferred = [
                target
                for target, item in candidates
                if str(item.get("vendor", "unknown")).lower() in {"unknown", "intel"}
            ]
            selected.extend(preferred or [candidates[0][0]])
        else:
            neutral = [target for target, item in candidates if str(item.get("vendor", "unknown")).lower() == "unknown"]
            selected.extend(neutral or [candidates[0][0]])
    return tuple(_safe_target_id(target) for target in dict.fromkeys(selected))


def _module(path: Path, target_id: str) -> str | None:
    suffix = f"_{target_id}.tcm"
    if not path.name.endswith(suffix):
        return None
    module = path.name[:-len(suffix)]
    # A bare ``_<target>.tcm`` is not an algorithm artifact and cannot be
    # addressed by the runtime through a graph/module name.
    return module or None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_bridge_names(
    payload: Mapping[str, Any], target_id: str, host_os: str
) -> tuple[str, ...]:
    """Return manifest-declared bridge basenames required by one target.

    A directory containing an arbitrary ``.so``/``.dll`` is not sufficient to
    make a target runnable.  The manifest is the portable source of truth for
    the bridge and C-API pair; synthetic manifests without runtime metadata
    intentionally retain the historical permissive behaviour used by unit
    tests and local tooling.
    """

    requirements = payload.get("runtime_requirements")
    if not isinstance(requirements, Mapping):
        return ()
    entry = requirements.get(target_id)
    if not isinstance(entry, Mapping):
        return ()
    names: list[str] = []
    for key in ("bridge", "c_api_runtime"):
        value = entry.get(key)
        if not isinstance(value, str) or not value.strip():
            continue
        # Manifest paths are relative metadata; only the basename belongs in
        # the target-qualified bridge directory selected below.
        name = Path(value).name
        if name and name not in names:
            names.append(name)
    return tuple(names)


def preflight_manifest_targets(
    *,
    tcm_root: os.PathLike[str] | str,
    dll_root: os.PathLike[str] | str,
    manifest_path: os.PathLike[str] | str,
) -> dict[str, Any]:
    """Audit every manifest target without creating a bundle or GPU context.

    The release planner intentionally validates only explicitly selected
    targets.  This companion audit is useful in CI to expose *all* portable
    gaps at once (for example a compile-only ARM target with no bridge), while
    preserving the planner's ability to build a CPU-only desktop payload.
    """

    tcm_root, dll_root, manifest_path = Path(tcm_root), Path(dll_root), Path(manifest_path)
    payload = _load_manifest(manifest_path)
    entries = [item for item in payload["target_matrix"] if isinstance(item, Mapping)]
    report: dict[str, Any] = {"schema_version": 1, "targets": {}}
    declared_target_ids: set[str] = set()
    for entry in entries:
        target_id = _safe_target_id(_target_id(entry))
        declared_target_ids.add(target_id)
        target_os = _canonical_bundle_os(str(entry.get("os", "")))
        # Resolve the bridge directory from the same canonical backend used
        # by ``_target_id``.  In particular, Android OpenGL profiles are
        # represented by GLES target directories; using the raw ``opengl``
        # spelling here would incorrectly report a missing bridge for a
        # valid ``gles_arm64_android`` payload.
        backend = ALIASES.get(
            str(entry.get("backend", "cpu")).strip().lower(),
            str(entry.get("backend", "cpu")).strip().lower(),
        )
        if backend == "opengl" and target_os == "android":
            backend = "gles"
        target_dir = tcm_root / target_id
        all_tcm = sorted(
            path for path in target_dir.glob("*.tcm") if path.is_file()
        ) if target_dir.is_dir() else []
        artifact_names = sorted(
            path.name for path in all_tcm if _module(path, target_id) is not None
        )
        invalid_artifact_names = sorted(
            path.name for path in all_tcm
            if _module(path, target_id) is None
            and not any(path.name.lower().endswith(suffix) for suffix in TEMPORARY_SUFFIXES)
        )
        temporary_artifact_names = sorted(
            path.name
            for path in all_tcm
            if any(path.name.lower().endswith(suffix) for suffix in TEMPORARY_SUFFIXES)
        )
        qualified = dll_root / target_id
        qualified_present = qualified.is_dir()
        bridge_dir = qualified if qualified_present else dll_root / backend
        bridge_resolution = "target_qualified" if qualified_present else "legacy_backend"
        extension = ".dll" if target_os == "windows" else ".so"
        bridge_names = sorted(path.name for path in bridge_dir.glob(f"*{extension}")) if bridge_dir.is_dir() else []
        required_bridge_names = _required_bridge_names(payload, target_id, target_os)
        missing: list[str] = []
        if not target_dir.is_dir():
            missing.append("tcm_directory")
        elif not artifact_names:
            missing.append("tcm_artifacts")
        elif invalid_artifact_names:
            missing.append("invalid_tcm_artifacts")
        if not bridge_dir.is_dir():
            missing.append("bridge_directory")
        elif not bridge_names:
            missing.append(f"bridge{extension}")
        for required in required_bridge_names:
            if required not in bridge_names:
                missing.append(required)
        report["targets"][target_id] = {
            "backend": backend,
            "os": target_os,
            "arch": _canonical_bundle_arch(str(entry.get("arch", ""))),
            "tcm_count": len(artifact_names),
            "tcm_artifacts": tuple(artifact_names),
            "temporary_tcm_artifacts": temporary_artifact_names,
            "invalid_tcm_artifacts": invalid_artifact_names,
            "bridge_directory": str(bridge_dir),
            "bridge_resolution": bridge_resolution,
            "qualified_bridge_directory_present": qualified_present,
            "bridge_files": bridge_names,
            "required_bridge_files": required_bridge_names,
            "missing_required_bridge_files": tuple(
                name for name in required_bridge_names if name not in bridge_names
            ),
            "missing": tuple(dict.fromkeys(missing)),
            "ready": not missing,
        }
    # A manifest-wide preflight must also detect stale target directories and
    # root-level TCM files.  Checking only declared targets would allow an
    # extracted bundle to carry an unqualified target that later packaging
    # stages could accidentally pick up.
    unexpected_target_dirs = tuple(
        sorted(
            path.name
            for path in tcm_root.iterdir()
            if path.is_dir()
            and path.name != "_quarantine"
            and path.name not in declared_target_ids
        )
    ) if tcm_root.is_dir() else tuple()
    root_tcm = tuple(
        sorted(path.name for path in tcm_root.glob("*.tcm") if path.is_file())
    ) if tcm_root.is_dir() else tuple()
    temporary_root_tcm = tuple(
        name for name in root_tcm
        if any(name.lower().endswith(suffix) for suffix in TEMPORARY_SUFFIXES)
    )
    unexpected_root_tcm = tuple(name for name in root_tcm if name not in temporary_root_tcm)
    report["ready_targets"] = tuple(target for target, item in report["targets"].items() if item["ready"])
    report["incomplete_targets"] = tuple(target for target, item in report["targets"].items() if not item["ready"])
    backend_summary: dict[str, dict[str, Any]] = {}
    for backend in sorted({item["backend"] for item in report["targets"].values()}):
        backend_targets = [
            item for item in report["targets"].values() if item["backend"] == backend
        ]
        backend_summary[backend] = {
            "target_count": len(backend_targets),
            "ready_count": sum(bool(item["ready"]) for item in backend_targets),
            "incomplete_count": sum(not bool(item["ready"]) for item in backend_targets),
            "fail_closed": any(not bool(item["ready"]) for item in backend_targets),
        }
    report["target_count"] = len(report["targets"])
    report["ready_count"] = len(report["ready_targets"])
    report["incomplete_count"] = len(report["incomplete_targets"])
    report["backend_summary"] = backend_summary
    report["unexpected_target_dirs"] = unexpected_target_dirs
    report["unexpected_root_artifacts"] = unexpected_root_tcm
    report["temporary_root_artifacts"] = temporary_root_tcm
    report["fail_closed"] = bool(
        report["incomplete_targets"]
        or unexpected_target_dirs
        or unexpected_root_tcm
    )
    return report


def plan_aot_bundle(*, tcm_root: os.PathLike[str] | str, dll_root: os.PathLike[str] | str, manifest_path: os.PathLike[str] | str, backends: Sequence[str] | None = None, targets: Sequence[str] | None = None, modules: Sequence[str] | None = None, vendors: Sequence[str] | None = None, host_os: str | None = None, host_arch: str | None = None, staging_parent: os.PathLike[str] | str | None = None, preflight_all: bool = False) -> AOTBundlePlan:
    """Validate and stage a minimal target-qualified release payload."""

    tcm_root, dll_root, manifest_path = Path(tcm_root), Path(dll_root), Path(manifest_path)
    detected_os, detected_arch = detect_bundle_host()
    host_os = _canonical_bundle_os(host_os) or detected_os
    host_arch = _canonical_bundle_arch(host_arch) or detected_arch
    preflight_report: Mapping[str, Any] | None = None
    if preflight_all or os.environ.get("PIXEL_REFINE_BUNDLE_PREFLIGHT_ALL") == "1":
        audit = preflight_manifest_targets(
            tcm_root=tcm_root,
            dll_root=dll_root,
            manifest_path=manifest_path,
        )
        preflight_report = audit
        incomplete = audit.get("incomplete_targets", ())
        global_issues = tuple(audit.get("unexpected_target_dirs", ())) + tuple(
            audit.get("unexpected_root_artifacts", ())
        )
        if incomplete or global_issues or audit.get("fail_closed"):
            details = "; ".join(
                f"{target}: {', '.join(audit['targets'][target]['missing'])}"
                for target in incomplete
            )
            if global_issues:
                details = "; ".join(filter(None, (details, "global: " + ", ".join(global_issues))))
            raise FileNotFoundError(
                "manifest-wide AOT preflight failed before bundling: " + details
            )
    payload = _load_manifest(manifest_path)
    raw_backends = tuple(backends or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_BACKENDS"), "cpu,cuda,vulkan,opengl"))
    selected_backends: list[str] = []
    for value in raw_backends:
        backend = ALIASES.get(str(value).lower())
        if backend is None:
            raise ValueError(f"unsupported AOT bundle backend: {value}")
        if backend not in selected_backends:
            selected_backends.append(backend)
    requested_targets = tuple(targets or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_TARGETS")))
    requested_vendors = tuple(vendors or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_VENDORS")))
    target_ids = _select_targets(payload, selected_backends, requested_targets, requested_vendors, host_os, host_arch)
    entries_by_id = {_target_id(item): item for item in payload["target_matrix"] if isinstance(item, Mapping)}
    selected_backends = list(dict.fromkeys(str(entries_by_id[target]["backend"]).lower() for target in target_ids))

    requested_modules = tuple(modules or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_MODULES")))
    explicit_modules = bool(requested_modules and set(requested_modules) - {"auto", "all"})
    requested_set = set(requested_modules) if explicit_modules else None
    artifacts: list[Path] = []
    available: dict[str, dict[str, Path]] = {}
    for target_id in target_ids:
        target_dir = tcm_root / target_id
        if not target_dir.is_dir():
            raise FileNotFoundError(f"AOT target directory is missing: {target_dir}")
        candidates = {}
        all_tcm = sorted(path for path in target_dir.glob("*.tcm") if path.is_file())
        invalid_artifacts = [
            artifact.name for artifact in all_tcm
            if _module(artifact, target_id) is None
            and not any(
                artifact.name.lower().endswith(suffix)
                for suffix in TEMPORARY_SUFFIXES
            )
        ]
        if invalid_artifacts:
            raise ValueError(
                f"AOT target directory contains invalid .tcm artifacts for "
                f"{target_id}: {', '.join(invalid_artifacts)}"
            )
        for artifact in all_tcm:
            if any(artifact.name.lower().endswith(suffix) for suffix in TEMPORARY_SUFFIXES):
                continue
            module = _module(artifact, target_id)
            if module:
                candidates[module] = artifact
        available[target_id] = candidates
        artifacts.extend(candidates[name] for name in sorted(requested_set & set(candidates)) if requested_set is not None) if requested_set is not None else artifacts.extend(candidates.values())
    if requested_set is not None:
        missing = {target: sorted(requested_set - set(items)) for target, items in available.items() if requested_set - set(items)}
        if missing:
            detail = "; ".join(f"{target}: {', '.join(names)}" for target, names in missing.items())
            raise FileNotFoundError("requested AOT modules are missing: " + detail)
    bridges: list[Path] = []
    qualification_tools: list[Path] = []
    for target_id, backend in zip(
        target_ids,
        (str(entries_by_id[target]["backend"]).lower() for target in target_ids),
    ):
        # ARM/Linux and Android bridges are target-qualified directories. The
        # historical desktop Windows layout uses ``aot_dll/<backend>``. If a
        # target-qualified directory exists, it is authoritative: do not fall
        # back to a desktop bridge when it is empty or has the wrong ABI.
        qualified = dll_root / target_id
        directory = qualified if qualified.is_dir() else dll_root / backend
        if not directory.is_dir():
            raise FileNotFoundError(
                f"AOT bridge directory is missing for {target_id}: {directory}"
            )
        libraries = sorted(directory.glob("*.dll" if host_os == "windows" else "*.so"))
        if not libraries:
            raise FileNotFoundError(
                f"AOT bridge directory has no {host_os} runtime library for "
                f"{target_id}: {directory}"
            )
        required_names = _required_bridge_names(payload, target_id, host_os)
        if required_names:
            present_names = {path.name for path in libraries}
            missing_names = tuple(name for name in required_names if name not in present_names)
            if missing_names:
                raise FileNotFoundError(
                    "AOT bridge preflight failed for "
                    f"{target_id}: missing manifest-declared runtime library "
                    + ", ".join(missing_names)
                    + f" in {directory}"
                )
        bridges.extend(libraries)
        if backend == "vulkan" and host_os == "windows":
            qualification_tools.extend(
                path
                for name in (
                    "spirv-val.exe",
                    "spirv-dis.exe",
                    "SPIRV-Tools-LICENSE.txt",
                )
                if (path := directory / name).is_file()
            )

    # Generic desktop OpenGL bridges can be selected for both the generic and
    # Intel target profiles. Deduplicate before writing release metadata so a
    # shared DLL is represented exactly once in the staged bundle.
    bridges = list(dict.fromkeys(bridges))

    if "cuda" in selected_backends and host_os == "windows":
        # Taichi loads this bitcode at first CUDA allocation.  A bundle that
        # omits it can be built successfully but is not runnable, so reject it
        # before invoking either packager.  Synthetic/unit-test roots without
        # a project venv are allowed to exercise selection logic.
        project_root = manifest_path.parents[3] if len(manifest_path.parents) > 3 else None
        runtime_bc = project_root / "venv" / "Lib" / "site-packages" / "taichi" / "_lib" / "runtime" / "runtime_cuda.bc" if project_root else None
        if runtime_bc is not None and (project_root / "venv").is_dir() and not runtime_bc.is_file() and os.environ.get("PIXEL_REFINE_ALLOW_MISSING_CUDA_BC") != "1":
            raise FileNotFoundError(f"CUDA bundle selected but Taichi runtime bitcode is missing: {runtime_bc}")

    modules_out = tuple(sorted({name for items in available.values() for name in items if requested_set is None or name in requested_set}))
    staging_dir = Path(tempfile.mkdtemp(prefix="pixel-refine-aot-bundle-", dir=str(staging_parent) if staging_parent else None))
    staging_tcm = staging_dir / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
    staging_dll = staging_dir / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
    try:
        for target in target_ids:
            (staging_tcm / target).mkdir(parents=True, exist_ok=True)
        for artifact in artifacts:
            shutil.copy2(artifact, staging_tcm / artifact.parent.name / artifact.name)
        filtered = dict(payload)
        filtered["target_matrix"] = [dict(item) for item in payload["target_matrix"] if isinstance(item, Mapping) and _target_id(item) in set(target_ids)]
        requirements = payload.get("runtime_requirements")
        if isinstance(requirements, Mapping):
            filtered["runtime_requirements"] = {key: value for key, value in requirements.items() if key in set(target_ids)}
        filtered["release_bundle"] = {
            "schema_version": 1,
            "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "targets": list(target_ids),
            "modules": list(modules_out),
            "temporary_artifacts_excluded": list(TEMPORARY_SUFFIXES),
            "artifacts": [
                {
                    "target": artifact.parent.name,
                    "module": _module(artifact, artifact.parent.name),
                    "filename": artifact.name,
                    "sha256": _sha256(artifact),
                    "size": artifact.stat().st_size,
                }
                for artifact in artifacts
            ],
            "bridges": [
                {
                    "directory": bridge.parent.name,
                    "filename": bridge.name,
                    "sha256": _sha256(bridge),
                    "size": bridge.stat().st_size,
                }
                for bridge in bridges
            ],
            "qualification_tools": [
                {
                    "directory": tool.parent.name,
                    "filename": tool.name,
                    "sha256": _sha256(tool),
                    "size": tool.stat().st_size,
                }
                for tool in qualification_tools
            ],
        }
        if preflight_report is not None:
            # Keep the complete audit in the staged manifest so a build log or
            # downstream packager can show which portable targets were ready.
            preflight_targets = {
                target: {
                    **dict(details),
                    "missing": list(details.get("missing", ())),
                    "bridge_files": list(details.get("bridge_files", ())),
                }
                for target, details in preflight_report.get("targets", {}).items()
            }
            filtered["release_bundle"]["manifest_preflight"] = {
                "ready_targets": list(preflight_report.get("ready_targets", ())),
                "incomplete_targets": list(preflight_report.get("incomplete_targets", ())),
                "targets": preflight_targets,
            }
        (staging_tcm / "target_manifest.json").write_text(json.dumps(filtered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        for bridge in bridges:
            destination = staging_dll / bridge.parent.name
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(bridge, destination / bridge.name)
        for tool in qualification_tools:
            destination = staging_dll / tool.parent.name
            destination.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tool, destination / tool.name)
        # Validate the exact staged tree before handing it to Nuitka or
        # PyInstaller. The import is lazy to keep this planner standalone and
        # avoid any runtime/engine initialization during packaging.
        from .validate_native_bundle import validate_native_bundle

        validate_native_bundle(staging_dir)
    except Exception:
        shutil.rmtree(staging_dir, ignore_errors=True)
        raise
    return AOTBundlePlan(
        tuple(selected_backends), target_ids, modules_out, tuple(artifacts),
        tuple(bridges),
        ((staging_tcm, "taichi_vision/taichi_algorithm/aot_tcm"),
         (staging_dll, "taichi_vision/taichi_algorithm/aot_py/aot_dll")),
        staging_dir,
        preflight_report,
    )


def plan_runtime_payload(
    *,
    runtime_root: os.PathLike[str] | str,
    backends: Sequence[str] | None = None,
    targets: Sequence[str] | None = None,
    modules: Sequence[str] | None = None,
) -> AOTBundlePlan:
    """Plan the pruned LLVM20 ``release/`` payload for a packager.

    The release layout is intentionally different from the historical flat
    ``aot_tcm``/``aot_dll`` tree: each target lives under
    ``bundles/<target>/{tcm,python}``.  This planner validates the
    self-relative release manifest and exposes one data directory per target,
    so PyInstaller/Nuitka package the D: payload without copying compiler
    intermediates or rebuilding a legacy flat tree.
    """

    root = Path(runtime_root).expanduser().resolve()
    manifest_path = root / "RELEASE_MANIFEST.json"
    bundles_root = root / "bundles"
    if not manifest_path.is_file() or not bundles_root.is_dir():
        raise FileNotFoundError(
            f"LLVM20 release payload is incomplete: {root}"
        )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or payload.get("scope") != "runtime_payload":
        raise ValueError("LLVM20 release manifest is not a runtime_payload manifest")
    if payload.get("record_root") and Path(str(payload["record_root"])).resolve() != root:
        raise ValueError("LLVM20 release manifest record_root does not match runtime_root")

    target_entries = {str(item["target"]): item for item in payload.get("bundles", []) if isinstance(item, Mapping) and item.get("target")}
    if not target_entries:
        raise ValueError("LLVM20 release manifest has no target bundles")
    requested_backends = tuple(
        ALIASES.get(str(value).strip().lower(), str(value).strip().lower())
        for value in (backends or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_BACKENDS"), "cpu,cuda,vulkan,opengl"))
        if str(value).strip()
    )
    if any(value not in ALIASES.values() for value in requested_backends):
        raise ValueError("unsupported backend in LLVM20 release payload request")
    requested_targets = tuple(targets or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_TARGETS")))
    if requested_targets:
        target_ids = tuple(dict.fromkeys(requested_targets))
    else:
        target_ids = tuple(
            target for target in target_entries
            if any(target == f"{backend}_x86_64_windows" or target.startswith(f"{backend}_x86_64_windows_") for backend in requested_backends)
        )
    missing_targets = sorted(set(target_ids) - set(target_entries))
    if missing_targets:
        raise FileNotFoundError("LLVM20 release target(s) are absent: " + ", ".join(missing_targets))

    requested_modules = tuple(modules or _csv(os.environ.get("PIXEL_REFINE_BUNDLE_MODULES")))
    module_filter = None if not requested_modules or set(requested_modules) & {"auto", "all"} else set(requested_modules)
    artifacts: list[Path] = []
    bridges: list[Path] = []
    data_dirs: list[tuple[Path, str]] = []
    modules_by_target: dict[str, set[str]] = {}
    for target in target_ids:
        entry = target_entries[target]
        target_root = bundles_root / target
        if not target_root.is_dir():
            raise FileNotFoundError(f"LLVM20 release target directory is missing: {target_root}")
        expected_files = entry.get("files")
        if not isinstance(expected_files, list):
            raise ValueError(f"LLVM20 release target has no file manifest: {target}")
        target_files: list[Path] = []
        for record in expected_files:
            if not isinstance(record, Mapping):
                raise ValueError(f"malformed release file record for {target}")
            relative = Path(str(record.get("path", "")))
            candidate = (root / relative).resolve()
            if candidate != target_root and target_root not in candidate.parents:
                raise ValueError(f"release manifest path escapes target {target}: {relative}")
            if not candidate.is_file():
                raise FileNotFoundError(f"release payload file is missing: {candidate}")
            if int(record.get("size", -1)) != candidate.stat().st_size or _sha256(candidate) != str(record.get("sha256", "")):
                raise ValueError(f"release payload checksum/size mismatch: {candidate}")
            target_files.append(candidate)
        tcm_files = [path for path in target_files if path.suffix.lower() == ".tcm"]
        if len(tcm_files) != int(entry.get("tcm_count", len(tcm_files))):
            raise ValueError(f"release target TCM count mismatch: {target}")
        target_modules: set[str] = set()
        for artifact in sorted(tcm_files):
            module = _module(artifact, target)
            if module is None:
                raise ValueError(f"invalid target-qualified TCM name: {artifact.name}")
            target_modules.add(module)
            if module_filter is None or module in module_filter:
                artifacts.append(artifact)
            with zipfile.ZipFile(artifact) as archive:
                if "tcm_manifest.json" not in archive.namelist():
                    raise ValueError(f"TCM manifest missing: {artifact}")
        modules_by_target[target] = target_modules
        bridges.extend(path for path in target_files if path.suffix.lower() == ".dll")
        data_dirs.append((target_root, f"bundles/{target}"))
    if module_filter is not None:
        missing = {target: sorted(module_filter - available) for target, available in modules_by_target.items() if module_filter - available}
        if missing:
            detail = "; ".join(f"{target}: {', '.join(names)}" for target, names in missing.items())
            raise FileNotFoundError("requested LLVM20 release modules are missing: " + detail)

    staging_dir = Path(tempfile.mkdtemp(prefix="pixel-refine-release-payload-"))
    return AOTBundlePlan(
        tuple(dict.fromkeys(requested_backends)),
        target_ids,
        tuple(sorted({module for values in modules_by_target.values() for module in values if module_filter is None or module in module_filter})),
        tuple(artifacts),
        tuple(dict.fromkeys(bridges)),
        tuple(data_dirs),
        staging_dir,
        {"scope": "runtime_payload", "manifest": str(manifest_path), "targets": list(target_ids)},
    )


def cleanup_aot_bundle(plan: AOTBundlePlan | Mapping[str, Any] | None) -> None:
    if plan is None:
        return
    staging = plan.staging_dir if isinstance(plan, AOTBundlePlan) else plan.get("staging_dir")
    if staging:
        shutil.rmtree(Path(staging), ignore_errors=True)


__all__ = [
    "AOTBundlePlan",
    "cleanup_aot_bundle",
    "plan_aot_bundle",
    "plan_runtime_payload",
    "preflight_manifest_targets",
    "validate_entrypoint",
]
