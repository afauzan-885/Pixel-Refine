"""Versioned identity checks for resident ONNX AOT artifacts.

This module is stdlib-only so manifest validation can be tested without
initializing Taichi, loading a native bridge, or selecting a device.
"""
from __future__ import annotations

import re
from math import prod
import os
import hashlib
import json
import zipfile
import zlib


RESIDENT_MANIFEST_FORMAT = 2
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TARGET_FIELDS = ("backend", "arch", "os", "abi", "vendor", "driver", "variant")
_MAX_SIGNED_BYTES = (1 << 63) - 1


def configured_runtime_abi(source_default=1):
    raw = os.environ.get("AOT_TCM_RUNTIME_ABI", str(source_default))
    try:
        value = int(raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("Configured AOT TCM runtime ABI is invalid") from exc
    if value <= 0:
        raise RuntimeError("Configured AOT TCM runtime ABI must be positive")
    return value


def _zip_member_sha256(archive, name):
    digest = hashlib.sha256()
    with archive.open(name, "r") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _reject_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON manifest key: {key}")
        result[key] = value
    return result


def archive_member_hashes(path, excluded=()):
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RuntimeError("Resident ONNX archive contains duplicate ZIP members")
            return {
                name: _zip_member_sha256(archive, name)
                for name in names
                if name not in set(excluded)
            }
    except (OSError, EOFError, RuntimeError, zipfile.BadZipFile, zlib.error) as exc:
        raise RuntimeError(f"Invalid resident ONNX archive: {path}") from exc


def read_resident_archive(path):
    """Read the resident envelope and hash payloads before any native load."""
    try:
        with zipfile.ZipFile(path, "r") as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise RuntimeError("Resident ONNX artifact contains duplicate ZIP members")
            metadata = json.loads(
                archive.read("resident_onnx.json"),
                object_pairs_hook=_reject_duplicate_json_keys,
            )
            weights = archive.read("resident_weights.npz")
            member_hashes = {
                name: _zip_member_sha256(archive, name)
                for name in names
                if name not in {"resident_onnx.json", "resident_weights.npz"}
            }
        return metadata, weights, member_hashes
    except (
        OSError,
        EOFError,
        KeyError,
        RuntimeError,
        UnicodeDecodeError,
        ValueError,
        zipfile.BadZipFile,
        zlib.error,
    ) as exc:
        raise RuntimeError(f"Invalid or corrupt resident ONNX artifact: {path}") from exc


def _name_list(value, field):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise RuntimeError(f"Resident ONNX {field} must be a list of non-empty names")
    if len(value) != len(set(value)):
        raise RuntimeError(f"Resident ONNX {field} contains duplicate names")
    return value


def _validate_schema(metadata):
    shapes = metadata.get("shapes")
    if not isinstance(shapes, dict) or not shapes:
        raise RuntimeError("Resident ONNX shape schema is missing")
    shape_elements = {}
    for name, shape in shapes.items():
        if not isinstance(name, str) or not name or not isinstance(shape, list):
            raise RuntimeError("Resident ONNX shape entries are malformed")
        if any(type(dim) is not int or dim <= 0 for dim in shape):
            raise RuntimeError(f"Resident ONNX shape has invalid dimensions: {name}")
        elements = prod(shape) if shape else 1
        if elements > _MAX_SIGNED_BYTES // 4:
            raise RuntimeError(f"Resident ONNX shape byte range overflows: {name}")
        shape_elements[name] = elements

    inputs = _name_list(metadata.get("inputs"), "inputs")
    outputs = _name_list(metadata.get("outputs"), "outputs")
    io_names = set(inputs) | set(outputs)
    if not io_names or not io_names.issubset(shapes):
        raise RuntimeError("Resident ONNX inputs/outputs do not match shape names")

    io_schema = metadata.get("io_schema")
    if not isinstance(io_schema, dict) or set(io_schema) != io_names:
        raise RuntimeError("Resident ONNX IO schema keys mismatch inputs/outputs")
    for name in io_names:
        entry = io_schema[name]
        if not isinstance(entry, dict) or entry.get("shape") != shapes[name]:
            raise RuntimeError(f"Resident ONNX IO shape mismatch: {name}")
        if entry.get("dtype") != "float32" or entry.get("layout") != "flat-contiguous":
            raise RuntimeError(f"Resident ONNX IO dtype/layout unsupported: {name}")

    bindings = metadata.get("bindings")
    sizes = metadata.get("sizes")
    if not isinstance(bindings, dict) or not isinstance(sizes, dict) or not sizes:
        raise RuntimeError("Resident ONNX bindings/sizes are missing")
    total_bytes = 0
    for name, amount in sizes.items():
        if not isinstance(name, str) or not name or type(amount) is not int or amount <= 0:
            raise RuntimeError("Resident ONNX allocation sizes are malformed")
        if amount > _MAX_SIGNED_BYTES // 4:
            raise RuntimeError(f"Resident ONNX allocation size overflows: {name}")
        total_bytes += amount * 4
        if total_bytes > _MAX_SIGNED_BYTES:
            raise RuntimeError("Resident ONNX aggregate allocation size overflows")
    if any(
        not isinstance(name, str) or not name or name not in shapes
        or not isinstance(binding, str) or binding not in sizes
        for name, binding in bindings.items()
    ):
        raise RuntimeError("Resident ONNX tensor bindings reference missing names")
    for name in io_names:
        binding = bindings.get(name)
        if binding not in sizes or sizes[binding] < shape_elements[name]:
            raise RuntimeError(f"Resident ONNX IO binding capacity mismatch: {name}")

    arguments = _name_list(metadata.get("arguments"), "arguments")
    constants = _name_list(metadata.get("constants"), "constants")
    if not set(arguments).issubset(sizes) or not set(constants).issubset(sizes):
        raise RuntimeError("Resident ONNX arguments/constants reference missing allocations")
    if not set(inputs + outputs).issubset(bindings):
        raise RuntimeError("Resident ONNX input/output binding is missing")

    opsets = metadata.get("opsets")
    if not isinstance(opsets, dict) or not opsets:
        raise RuntimeError("Resident ONNX opset identity is missing")
    for domain, version in opsets.items():
        if not isinstance(domain, str) or not domain.strip():
            raise RuntimeError("Resident ONNX opset domain is malformed")
        if type(version) is not int or not 1 <= version <= (1 << 31) - 1:
            raise RuntimeError(f"Resident ONNX opset version is invalid: {domain}")

    graph = metadata.get("graph")
    if not isinstance(graph, str) or not graph:
        raise RuntimeError("Resident ONNX graph identity is missing")


def validate_resident_metadata(
    metadata,
    *,
    backend,
    target_identity,
    model_sha256=None,
    artifact_only=False,
    runtime_abi=1,
    artifact_members=None,
    weights_sha256=None,
    runtime_taichi_version=None,
    runtime_capabilities=None,
):
    """Reject stale model, target, ABI, or modified inner-module entries.

    Format 1 is deliberately rejected: it has no target/ABI/member-integrity
    envelope, so artifact-only mode cannot safely establish its identity.
    """
    if not isinstance(metadata, dict):
        raise RuntimeError("Resident ONNX manifest must be an object")
    fmt = metadata.get("format")
    if type(fmt) is int and fmt == 1:
        raise RuntimeError(
            "Legacy resident ONNX metadata lacks target/ABI integrity; rebuild the artifact"
        )
    if type(fmt) is not int or fmt != RESIDENT_MANIFEST_FORMAT:
        raise RuntimeError(f"Unsupported resident ONNX manifest format: {fmt!r}")
    if artifact_only and model_sha256 is not None:
        raise ValueError("artifact_only cannot be combined with model_sha256")

    recorded_hash = metadata.get("model_sha256")
    if not isinstance(recorded_hash, str) or not _SHA256_RE.fullmatch(recorded_hash):
        raise RuntimeError("Resident ONNX manifest has an invalid model SHA-256")
    if model_sha256 is None and not artifact_only:
        raise RuntimeError(
            "Resident ONNX load requires model_sha256 or explicit artifact_only=True"
        )
    if model_sha256 is not None and recorded_hash != str(model_sha256).lower():
        raise RuntimeError("Resident ONNX artifact does not match the selected model")

    if str(metadata.get("backend", "")).lower() != str(backend).lower():
        raise RuntimeError("Resident ONNX artifact/backend mismatch")
    recorded_target = metadata.get("target_identity")
    if not isinstance(recorded_target, dict) or not isinstance(target_identity, dict):
        raise RuntimeError("Resident ONNX target identity is missing")
    for field in _TARGET_FIELDS:
        expected = target_identity.get(field)
        actual = recorded_target.get(field)
        if not isinstance(expected, str) or not isinstance(actual, str):
            raise RuntimeError(f"Resident ONNX target identity field is missing: {field}")
        if field == "vendor" and actual == "unknown":
            continue  # vendor-neutral target profile, consistent with AOT resolver
        if str(actual or "").lower() != str(expected or "").lower():
            raise RuntimeError(f"Resident ONNX target mismatch: {field}")

    recorded_runtime_abi = metadata.get("runtime_abi")
    if type(recorded_runtime_abi) is not int or recorded_runtime_abi != int(runtime_abi):
        raise RuntimeError("Resident ONNX runtime ABI mismatch")
    taichi_version = metadata.get("taichi_version")
    if not isinstance(taichi_version, str) or not taichi_version:
        raise RuntimeError("Resident ONNX Taichi version identity is missing")
    if not isinstance(runtime_taichi_version, str) or not runtime_taichi_version:
        raise RuntimeError("Current Taichi runtime version is unavailable; refusing artifact load")
    if taichi_version != runtime_taichi_version:
        raise RuntimeError("Resident ONNX Taichi compiler/runtime version mismatch")

    capability_identity = metadata.get("device_capabilities")
    if not isinstance(capability_identity, dict):
        raise RuntimeError(
            "Resident ONNX device capability identity is missing; rebuild with a qualified target"
        )
    if capability_identity.get("status") != "known":
        raise RuntimeError(
            "Resident ONNX capability identity is unknown; artifact is non-portable and cannot load "
            "until capability-qualified rebuild support exists"
        )
    if not isinstance(capability_identity.get("requirements"), dict):
        raise RuntimeError("Resident ONNX capability requirements are malformed")
    if not isinstance(runtime_capabilities, dict):
        raise RuntimeError(
            "Current device capability identity is unavailable; refusing artifact load"
        )
    if capability_identity["requirements"] != runtime_capabilities:
        raise RuntimeError("Resident ONNX device capability mismatch")

    _validate_schema(metadata)
    if not isinstance(metadata.get("weights_sha256"), str) or not _SHA256_RE.fullmatch(
        metadata["weights_sha256"]
    ):
        raise RuntimeError("Resident ONNX weights hash is missing or invalid")
    if weights_sha256 is not None and metadata["weights_sha256"] != weights_sha256:
        raise RuntimeError("Resident ONNX weights hash mismatch")

    expected_members = metadata.get("artifact_members_sha256")
    if not isinstance(expected_members, dict) or not expected_members:
        raise RuntimeError("Resident ONNX artifact member hashes are missing")
    if artifact_members is not None:
        if set(expected_members) != set(artifact_members):
            raise RuntimeError("Resident ONNX artifact member set mismatch")
        for name, expected in expected_members.items():
            actual = artifact_members[name]
            if not isinstance(expected, str) or not _SHA256_RE.fullmatch(expected):
                raise RuntimeError(f"Resident ONNX member hash is invalid: {name}")
            if actual != expected:
                raise RuntimeError(f"Resident ONNX artifact member hash mismatch: {name}")
    return "current"
