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
MANIFEST_PATH = ROOT / "taichi_library" / "taichi_algorithm" / "aot_tcm" / "target_manifest.json"
SUPPORTED_BACKENDS = ("cpu", "vulkan", "opengl", "gles", "cuda")


def _canonical(value: object, default: str = "unknown") -> str:
    raw = str(value or "").strip().lower()
    return raw or default


def target_id_from_entry(entry: Mapping[str, object]) -> str:
    """Build the same target ID contract used by ``TargetSpec``."""

    backend = _canonical(entry.get("backend"), "cpu")
    arch = _canonical(entry.get("arch"))
    os_name = _canonical(entry.get("os"))
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
        backend = _canonical(entry.get("backend"), "cpu")
        if backend not in SUPPORTED_BACKENDS:
            raise ValueError(f"unsupported backend in AOT target manifest: {backend}")
        target_id = target_id_from_entry(entry)
        previous = result.get(target_id)
        if previous is not None and previous != backend:
            raise ValueError(f"duplicate target ID with conflicting backend: {target_id}")
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
    "target_id_from_entry",
    "validate_target_registry",
]
