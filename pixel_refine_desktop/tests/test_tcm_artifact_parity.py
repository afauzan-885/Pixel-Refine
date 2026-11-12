"""Parity of TCM artifact materialization after the port into taichi.

The packed archive is what the desktop tree ships, while the CPU bridge loads a
directory. Extraction must therefore produce exactly the same tree as the
legacy materializer: same cache key, same members, same bytes.
"""

import hashlib
import os
import sys

import pytest

import taichi as ti

TCM_ROOT = os.path.join("taichi_vision", "taichi_algorithm", "aot_tcm")


def _legacy_module():
    pytest.importorskip("taichi")
    return sys.modules.get("taichi.aot_engine") or pytest.importorskip(
        "taichi.aot_engine"
    )


def _cpu_artifact():
    candidates = []
    for root, _dirs, names in os.walk(TCM_ROOT):
        for name in names:
            if name.endswith(".tcm") and "cpu" in name.lower():
                candidates.append(os.path.join(root, name))
    if not candidates:
        pytest.skip("no CPU TCM artifact on this host")
    return sorted(candidates)[0]


def _tree_digest(root):
    entries = []
    for current, _dirs, names in os.walk(root):
        for name in sorted(names):
            path = os.path.join(current, name)
            relative = os.path.relpath(path, root)
            with open(path, "rb") as handle:
                entries.append((relative, hashlib.sha256(handle.read()).hexdigest()))
    return sorted(entries)


def test_materialization_matches_legacy(tmp_path):
    artifact = _cpu_artifact()
    legacy = _legacy_module()
    assert legacy is not None

    old_dir = legacy._materialize_cpu_aot_directory(artifact)
    new_dir = ti.tcm_artifacts.materialize_artifact(artifact, cache_root=str(tmp_path))
    assert os.path.isdir(new_dir)
    assert os.path.isfile(os.path.join(new_dir, ti.tcm_artifacts.CONTENT_MARKER))
    assert _tree_digest(new_dir) == _tree_digest(old_dir)


def test_materialization_is_content_addressed_and_reused(tmp_path):
    artifact = _cpu_artifact()
    first = ti.tcm_artifacts.materialize_artifact(artifact, cache_root=str(tmp_path))
    second = ti.tcm_artifacts.materialize_artifact(artifact, cache_root=str(tmp_path))
    assert first == second
    digest = ti.tcm_artifacts.artifact_digest(artifact)
    assert os.path.basename(first) == digest


def test_packed_archive_detection():
    artifact = _cpu_artifact()
    assert ti.tcm_artifacts.is_packed_archive(artifact) is True
    assert ti.tcm_artifacts.is_packed_archive(__file__) is False


def test_arch_variant_prefers_suffixed_artifact(tmp_path):
    base = tmp_path / "demo.tcm"
    variant = tmp_path / "demo_vulkan.tcm"
    base.write_bytes(b"x")
    variant.write_bytes(b"y")
    assert ti.tcm_artifacts.resolve_arch_variant(str(base), "vulkan") == str(variant)
    assert ti.tcm_artifacts.resolve_arch_variant(str(base), "cpu") == str(base)


def test_non_archive_fails_closed(tmp_path):
    plain = tmp_path / "plain.tcm"
    plain.write_bytes(b"not a zip")
    with pytest.raises(RuntimeError, match="Not a packed AOT artifact"):
        ti.tcm_artifacts.materialize_artifact(str(plain), cache_root=str(tmp_path / "cache"))
