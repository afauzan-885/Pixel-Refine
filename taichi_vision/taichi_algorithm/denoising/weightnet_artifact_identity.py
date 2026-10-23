"""Pure source-model identity selection for resident WeightNet artifacts."""
from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile


def selected_weightnet_model_bytes(source, patch_size, search_dirs=()):
    """Return bytes for the selected model, or None when no model is available.

    An existing ONNX source or bundle is authoritative. Bundle selection uses
    the same patch-specific member name as the production loader.
    """
    source = Path(source)
    if source.suffix.lower() == ".onnx":
        if not source.is_file():
            raise FileNotFoundError(f"Selected WeightNet ONNX model does not exist: {source}")
        return source.read_bytes()

    if source.suffix.lower() == ".bundle":
        if not source.is_file():
            raise FileNotFoundError(f"Selected WeightNet bundle does not exist: {source}")
        candidates = (source,)
    else:
        candidates = tuple(
            Path(directory) / name
            for directory in search_dirs
            for name in ("weightnet_master.bundle", "weightnet_v3_master.bundle")
        )
    selected = next((candidate for candidate in candidates if candidate.is_file()), None)
    if selected is None:
        return None

    member = f"weightnet_{int(patch_size)}_gpu_1c_fp32.onnx"
    with zipfile.ZipFile(selected, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError(f"WeightNet bundle contains duplicate members: {selected}")
        if member not in names:
            raise FileNotFoundError(
                f"WeightNet model member {member!r} is missing from {selected}"
            )
        return archive.read(member)


def resident_weightnet_load_kwargs(model_bytes=None):
    """Choose exactly one loader identity mode from actual model provenance."""
    if model_bytes is None:
        return {"artifact_only": True}
    return {"model_sha256": hashlib.sha256(bytes(model_bytes)).hexdigest()}
