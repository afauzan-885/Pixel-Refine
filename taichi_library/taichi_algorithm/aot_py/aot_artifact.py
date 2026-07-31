"""Validation and deterministic normalization for packed Taichi AOT modules."""

import json
import os
from pathlib import Path
import tempfile
import time
import zipfile


_FIXED_ZIP_TIME = (2000, 12, 1, 0, 0, 0)
_TEXTURE_TAGS = {3, 4}  # aot::ArgKind::kTexture / kRWTexture


def _normalize_graphs(payload):
    graphs = json.loads(payload.decode("utf-8"))
    if not isinstance(graphs, list):
        raise ValueError("graphs.json must contain a list")
    for graph in graphs:
        for dispatch in graph.get("value", {}).get("dispatches", []):
            for arg in dispatch.get("symbolic_args", []):
                if arg.get("tag") not in _TEXTURE_TAGS:
                    arg["num_channels"] = 0
    graphs.sort(key=lambda graph: graph["key"])
    return json.dumps(graphs, sort_keys=True, separators=(",", ":")).encode("utf-8")


def normalize_tcm(path):
    """Canonicalize a generated ``.tcm`` in place and return its path.

    Taichi 1.7.4 serializes an unused ``num_channels`` field of non-texture
    graph arguments without initializing it. Canonicalizing this field and the
    archive ordering makes generated artifacts reproducible and prevents
    nondeterministic graph metadata from reaching a runtime.
    """
    artifact = Path(path).resolve()
    if artifact.suffix != ".tcm":
        raise ValueError(f"Expected a .tcm artifact, got {artifact}")

    with zipfile.ZipFile(artifact, "r") as source:
        contents = {entry.filename: source.read(entry) for entry in source.infolist()}
    if "__version__" not in contents:
        raise ValueError(f"Invalid Taichi AOT artifact: {artifact}")
    # LLVM AOT modules (CPU) store graph metadata only in graphs.tcb. GFX
    # modules additionally contain graphs.json, where Taichi 1.7.4 leaves an
    # unused field uninitialized. Both formats can still be canonicalized by
    # stable archive ordering; only the GFX format needs metadata repair.
    if "graphs.json" in contents:
        contents["graphs.json"] = _normalize_graphs(contents["graphs.json"])

    with tempfile.NamedTemporaryFile(
        prefix=f"{artifact.stem}-", suffix=".tcm", dir=artifact.parent, delete=False
    ) as handle:
        staging = Path(handle.name)
    try:
        with zipfile.ZipFile(staging, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for name in sorted(contents):
                entry = zipfile.ZipInfo(name, date_time=_FIXED_ZIP_TIME)
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                target.writestr(entry, contents[name])
        last_error = None
        for attempt in range(12):
            try:
                os.replace(staging, artifact)
                last_error = None
                break
            except PermissionError as error:
                # Windows antivirus/indexer and the compiler child can hold a
                # freshly-written archive for a short interval. Retrying the
                # atomic promotion keeps normalization deterministic without
                # weakening the artifact validation contract.
                last_error = error
                if attempt == 11:
                    raise
                time.sleep(0.25 * (attempt + 1))
        if last_error is not None:
            raise last_error
    finally:
        if staging.exists():
            staging.unlink()
    return str(artifact)


def archive_module(module, path):
    """Save a Taichi module as a canonical packed artifact.

    ``Module.archive()`` in Taichi 1.7.4 emits the legacy ``graphs.tcb``
    layout for some Python compiler entry points.  Graphics AOT loaders use
    ``graphs.json`` instead.  Saving to a directory first keeps the backend
    metadata intact; packing it here then gives CPU, Vulkan, and OpenGL the
    same deterministic archive layout.
    """
    artifact = Path(path).resolve()
    if artifact.suffix != ".tcm":
        raise ValueError(f"Expected a .tcm artifact, got {artifact}")
    artifact.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f"{artifact.stem}-", dir=artifact.parent) as temp_dir:
        module.save(temp_dir)
        with zipfile.ZipFile(artifact, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for source in sorted(Path(temp_dir).rglob("*")):
                if source.is_file():
                    entry = zipfile.ZipInfo(
                        source.relative_to(temp_dir).as_posix(), date_time=_FIXED_ZIP_TIME
                    )
                    entry.compress_type = zipfile.ZIP_DEFLATED
                    entry.external_attr = 0o100644 << 16
                    target.writestr(entry, source.read_bytes())
    return normalize_tcm(artifact)
