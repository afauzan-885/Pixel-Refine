"""Fail-closed validation for staged target-qualified AOT release bundles.

This validator is intentionally independent from ``engine.py`` and does not
initialize Taichi or a graphics context.  Packagers can run it after staging
and before invoking their compiler, while CI can use it as a cheap integrity
gate for a produced bundle.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


TEMPORARY_SUFFIXES = (".staging.tcm", ".next.tcm", ".previous.tcm")
GRAPHICS_BACKENDS = {"cuda", "vulkan", "opengl", "gles"}
_BACKEND_ALIASES = {
    "cpu": "cpu",
    "x86": "cpu",
    "x64": "cpu",
    "cuda": "cuda",
    "vulkan": "vulkan",
    "vk": "vulkan",
    "opengl": "opengl",
    "gl": "opengl",
    "gles": "gles",
}


def _canonical_os(value: Any) -> str:
    return {
        "win32": "windows",
        "windows": "windows",
        "linux": "linux",
        "android": "android",
    }.get(str(value or "").strip().lower(), str(value or "").strip().lower())


def _canonical_arch(value: Any) -> str:
    raw = str(value or "").strip().lower().replace(" ", "")
    return {
        "amd64": "x86_64",
        "x64": "x86_64",
        "x86_64": "x86_64",
        "aarch64": "arm64",
        "arm64-v8a": "arm64",
        "arm64": "arm64",
    }.get(raw, raw)


class NativeBundleValidationError(ValueError):
    """Raised when a staged bundle cannot be proven target-consistent."""


@dataclass(frozen=True)
class NativeBundleValidationResult:
    root: str
    targets: tuple[str, ...]
    modules: tuple[str, ...]
    artifact_count: int
    bridge_count: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _target_id(entry: Mapping[str, Any]) -> str:
    backend_raw = str(entry.get("backend", "cpu")).strip().lower()
    backend = _BACKEND_ALIASES.get(backend_raw)
    # This validator is an independent release gate.  Do not rely on the
    # planner having run first: an extracted or hand-edited manifest with an
    # arbitrary backend string must not become a seemingly valid target merely
    # because matching files happen to exist on disk.
    if backend is None:
        _fail(f"unsupported AOT target backend: {backend_raw!r}")
    # Keep release validation aligned with the canonical target contract: a
    # CUDA artifact is meaningful only for NVIDIA's CUDA runtime.  Without
    # this gate a hand-edited manifest could package a ``cuda_*_amd`` target
    # and bypass the stricter build-time target registry validation.
    if backend == "cuda" and str(entry.get("vendor", "unknown")).strip().lower() != "nvidia":
        _fail("CUDA target identity requires vendor=nvidia")
    os_name = _canonical_os(entry.get("os", "unknown"))
    # Android OpenGL profiles are emitted into the GLES target directory by
    # release_bundle; validation must use the exact same canonical identity.
    if backend == "opengl" and os_name == "android":
        backend = "gles"
    parts = [backend, _canonical_arch(entry.get("arch", "unknown"))]
    vendor = str(entry.get("vendor", "unknown")).strip().lower()
    if os_name != "unknown":
        parts.append(os_name)
    if vendor != "unknown" and backend in GRAPHICS_BACKENDS:
        parts.append(vendor)
    variant = str(entry.get("variant", "")).strip().lower()
    if variant:
        parts.append(variant)
    return "_".join(parts)


def _required_bridge_names(
    payload: Mapping[str, Any], target_id: str
) -> tuple[str, ...]:
    """Return manifest-declared bridge/C-API basenames for one target.

    A release record containing one arbitrary native library is not proof that
    the target can start: the bridge may depend on the matching Taichi C API
    runtime.  The manifest is the portable source of truth for that pair.  A
    missing ``runtime_requirements`` entry remains permissive for legacy and
    synthetic manifests that intentionally do not describe native metadata.
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
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            _fail(f"runtime_requirements.{target_id}.{key} must be a path string")
        name = Path(value).name
        if not name or name in {".", ".."}:
            _fail(f"runtime_requirements.{target_id}.{key} has no filename")
        if name not in names:
            names.append(name)
    return tuple(names)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fail(message: str) -> None:
    raise NativeBundleValidationError(message)


def _safe_child(parent: Path, name: str) -> Path:
    if not name or Path(name).name != name:
        _fail(f"bundle manifest contains an unsafe filename: {name!r}")
    path = (parent / name).resolve()
    try:
        path.relative_to(parent.resolve())
    except ValueError:
        _fail(f"bundle manifest escapes its target directory: {name!r}")
    return path


def validate_native_bundle(root: str | Path) -> NativeBundleValidationResult:
    """Validate manifest, checksums, artifact set, and native bridge set.

    ``root`` is either the temporary staging root returned by
    :func:`taichi_vision.release_bundle.plan_aot_bundle` or the root of an
    extracted release.  Every listed artifact must exist exactly once, match
    its SHA-256/size record, and belong to a listed target.  Target-qualified
    bridge directories are authoritative when present; a generic backend
    directory is accepted only for the legacy desktop layout.
    """

    root = Path(root).resolve()
    manifest_path = root / "taichi_vision" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
    tcm_root = manifest_path.parent
    dll_root = root / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
    if not manifest_path.is_file():
        _fail(f"release manifest is missing: {manifest_path}")
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        _fail(f"release manifest is unreadable: {error}")
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        _fail("release manifest schema_version must be 1")
    release = payload.get("release_bundle")
    if not isinstance(release, Mapping) or release.get("schema_version") != 1:
        _fail("release_bundle metadata with schema_version=1 is required")
    targets = release.get("targets")
    modules = release.get("modules")
    records = release.get("artifacts")
    if not isinstance(targets, list) or not targets or len(set(targets)) != len(targets):
        _fail("release_bundle.targets must be a non-empty unique list")
    for target in targets:
        if not isinstance(target, str) or not target or Path(target).name != target or target in {".", ".."}:
            _fail(f"release_bundle contains an unsafe target ID: {target!r}")
    if not isinstance(modules, list) or any(not isinstance(item, str) or not item for item in modules):
        _fail("release_bundle.modules must be a list of non-empty strings")
    if len(set(modules)) != len(modules):
        _fail("release_bundle.modules must be unique")
    if not isinstance(records, list):
        _fail("release_bundle.artifacts must be a list")
    bridge_records = release.get("bridges")
    if not isinstance(bridge_records, list):
        _fail("release_bundle.bridges must be a list")
    source_hash = release.get("source_manifest_sha256")
    if not isinstance(source_hash, str) or len(source_hash) != 64:
        _fail("release_bundle.source_manifest_sha256 must be a 64-character hash")
    try:
        int(source_hash, 16)
    except ValueError:
        _fail("release_bundle.source_manifest_sha256 is not hexadecimal")
    excluded = release.get("temporary_artifacts_excluded")
    if tuple(excluded or ()) != TEMPORARY_SUFFIXES:
        _fail("release_bundle temporary-artifact policy is incomplete")

    entries = payload.get("target_matrix")
    if not isinstance(entries, list):
        _fail("target_manifest.target_matrix must be a list")
    entry_by_id: dict[str, Mapping[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, Mapping):
            _fail("target_manifest.target_matrix contains a non-object entry")
        target_id = _target_id(entry)
        if target_id in entry_by_id:
            _fail(f"duplicate target_matrix entry: {target_id}")
        entry_by_id[target_id] = entry
    if set(entry_by_id) != set(targets):
        _fail(
            "target manifest and release_bundle.targets disagree: "
            f"manifest={sorted(entry_by_id)} release={sorted(targets)}"
        )
    # Runtime qualification metadata is keyed by canonical target ID.  An
    # orphan entry can otherwise survive filtering and falsely suggest that a
    # target was qualified even though the bundle cannot address it.
    runtime_requirements = payload.get("runtime_requirements")
    if runtime_requirements is not None and not isinstance(runtime_requirements, Mapping):
        _fail("target_manifest.runtime_requirements must be an object")
    if isinstance(runtime_requirements, Mapping):
        orphan_requirements = sorted(
            str(target_id)
            for target_id in runtime_requirements
            if str(target_id) not in entry_by_id
        )
        if orphan_requirements:
            _fail(
                "runtime_requirements contains unlisted target IDs: "
                + ", ".join(orphan_requirements)
            )

    expected_paths: set[Path] = set()
    record_keys: set[tuple[str, str]] = set()
    record_modules: set[str] = set()
    for record in records:
        if not isinstance(record, Mapping):
            _fail("release_bundle.artifacts contains a non-object record")
        target = str(record.get("target", ""))
        module = str(record.get("module", ""))
        filename = str(record.get("filename", ""))
        digest = str(record.get("sha256", ""))
        size = record.get("size")
        if target not in targets:
            _fail(f"artifact record references unlisted target: {target!r}")
        if not module or not filename or len(digest) != 64:
            _fail(f"artifact record is incomplete for {target}/{module}")
        if not isinstance(size, int) or size < 0:
            _fail(f"artifact record has invalid size for {target}/{module}")
        expected_name = f"{module}_{target}.tcm"
        if filename != expected_name:
            _fail(f"artifact filename does not match target/module: {filename!r}")
        key = (target, module)
        if key in record_keys:
            _fail(f"duplicate artifact record: {target}/{module}")
        record_keys.add(key)
        record_modules.add(module)
        artifact = _safe_child(tcm_root / target, filename)
        if not artifact.is_file():
            _fail(f"listed TCM artifact is missing: {artifact}")
        if artifact.stat().st_size != size:
            _fail(f"TCM size mismatch for {artifact.name}")
        if _sha256(artifact).lower() != digest.lower():
            _fail(f"TCM checksum mismatch for {artifact.name}")
        expected_paths.add(artifact)

    if record_modules != set(modules):
        _fail(
            "release_bundle.modules disagrees with artifact records: "
            f"metadata={sorted(modules)} records={sorted(record_modules)}"
        )
    actual_paths: set[Path] = set()
    stray_root_files = {
        path.name
        for path in tcm_root.iterdir()
        if path.is_file() and path.name != "target_manifest.json"
    } if tcm_root.is_dir() else set()
    if stray_root_files:
        _fail(
            "staged TCM root contains unlisted files: "
            + ", ".join(sorted(stray_root_files))
        )
    unlisted_tcm_targets: set[str] = set()
    for candidate_dir in tcm_root.iterdir() if tcm_root.is_dir() else ():
        if not candidate_dir.is_dir() or candidate_dir.name in targets:
            continue
        # Empty target directories are also stale release payload structure;
        # rejecting them keeps the extracted tree canonical and prevents a
        # later packaging step from accidentally populating an unqualified
        # target without updating the manifest.
        unlisted_tcm_targets.add(candidate_dir.name)
    if unlisted_tcm_targets:
        _fail(
            "staged TCM set contains unlisted target directories: "
            + ", ".join(sorted(unlisted_tcm_targets))
        )
    for target in targets:
        target_dir = tcm_root / target
        if not target_dir.is_dir():
            _fail(f"target artifact directory is missing: {target_dir}")
        for artifact in target_dir.glob("*.tcm"):
            if any(artifact.name.lower().endswith(suffix) for suffix in TEMPORARY_SUFFIXES):
                _fail(f"temporary TCM artifact is present in release: {artifact.name}")
            actual_paths.add(artifact.resolve())
    if actual_paths != expected_paths:
        _fail(
            "staged TCM set differs from manifest: "
            f"missing={len(expected_paths - actual_paths)} extra={len(actual_paths - expected_paths)}"
        )

    bridge_paths: list[Path] = []
    for target in targets:
        entry = entry_by_id[target]
        backend = _BACKEND_ALIASES.get(
            str(entry.get("backend", "cpu")).strip().lower(),
            str(entry.get("backend", "cpu")).strip().lower(),
        )
        os_name = _canonical_os(entry.get("os", "unknown"))
        qualified = dll_root / target
        directory = qualified if qualified.is_dir() else dll_root / backend
        extension = ".dll" if os_name == "windows" else ".so"
        if not directory.is_dir():
            _fail(f"native bridge directory is missing for {target}: {directory}")
        libraries = sorted(directory.glob(f"*{extension}"))
        if not libraries:
            _fail(f"native bridge for {target} has no {extension} library: {directory}")
        required_names = _required_bridge_names(payload, target)
        if required_names:
            present_names = {path.name for path in libraries}
            missing_names = tuple(name for name in required_names if name not in present_names)
            if missing_names:
                _fail(
                    "native bridge preflight failed for "
                    f"{target}: missing manifest-declared runtime library "
                    + ", ".join(missing_names)
                    + f" in {directory}"
                )
        bridge_paths.extend(path.resolve() for path in libraries)

    expected_bridges = set(bridge_paths)
    recorded_bridges: set[Path] = set()
    bridge_record_keys: set[tuple[str, str]] = set()
    for record in bridge_records:
        if not isinstance(record, Mapping):
            _fail("release_bundle.bridges contains a non-object record")
        directory = str(record.get("directory", ""))
        filename = str(record.get("filename", ""))
        digest = str(record.get("sha256", ""))
        size = record.get("size")
        if not directory or not filename or Path(directory).name != directory or Path(filename).name != filename:
            _fail("release_bundle.bridges contains an unsafe path")
        if len(digest) != 64 or not isinstance(size, int) or size < 0:
            _fail(f"release bridge record is incomplete: {directory}/{filename}")
        bridge_key = (directory, filename)
        if bridge_key in bridge_record_keys:
            _fail(f"duplicate release bridge record: {directory}/{filename}")
        bridge_record_keys.add(bridge_key)
        bridge = _safe_child(dll_root / directory, filename)
        if not bridge.is_file() or bridge.stat().st_size != size or _sha256(bridge).lower() != digest.lower():
            _fail(f"release bridge checksum/size mismatch: {directory}/{filename}")
        recorded_bridges.add(bridge)
    if recorded_bridges != expected_bridges:
        _fail("release bridge records do not match target bridge selection")
    actual_bridges = {
        path.resolve()
        for pattern in ("*.dll", "*.so")
        for path in dll_root.rglob(pattern)
        if path.is_file()
    }
    stale_bridges = actual_bridges - recorded_bridges
    if stale_bridges:
        _fail(
            "staged native bridge set contains unselected/stale libraries: "
            + ", ".join(sorted(path.name for path in stale_bridges))
        )

    return NativeBundleValidationResult(
        root=str(root),
        targets=tuple(targets),
        modules=tuple(sorted(modules)),
        artifact_count=len(expected_paths),
        bridge_count=len(set(bridge_paths)),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle_root", type=Path, help="staged/extracted release root")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    try:
        result = validate_native_bundle(args.bundle_root)
    except NativeBundleValidationError as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 2
    if args.as_json:
        print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    else:
        print(
            f"[OK] targets={len(result.targets)} modules={len(result.modules)} "
            f"artifacts={result.artifact_count} bridges={result.bridge_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
