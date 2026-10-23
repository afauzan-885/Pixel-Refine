"""Versioned identity checks for resident ONNX AOT artifacts.

This module is stdlib-only so manifest validation can be tested without
initializing Taichi, loading a native bridge, or selecting a device.
"""
from __future__ import annotations

import re


RESIDENT_MANIFEST_FORMAT = 2
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TARGET_FIELDS = ("backend", "arch", "os", "abi", "vendor", "variant")


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
        if field == "vendor" and actual == "unknown":
            continue  # vendor-neutral target profile, consistent with AOT resolver
        if str(actual or "").lower() != str(expected or "").lower():
            raise RuntimeError(f"Resident ONNX target mismatch: {field}")

    if metadata.get("runtime_abi") != int(runtime_abi):
        raise RuntimeError("Resident ONNX runtime ABI mismatch")
    taichi_version = metadata.get("taichi_version")
    if not isinstance(taichi_version, str) or not taichi_version:
        raise RuntimeError("Resident ONNX Taichi version identity is missing")
    if not isinstance(metadata.get("io_schema"), dict):
        raise RuntimeError("Resident ONNX input/output schema is missing")
    if not isinstance(metadata.get("opsets"), dict):
        raise RuntimeError("Resident ONNX opset identity is missing")
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
