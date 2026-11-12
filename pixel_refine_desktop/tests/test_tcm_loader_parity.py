"""Parity of the TCM module loader after the port into the taichi library.

The loader is runtime plumbing: it decides which compiled artifact belongs to
the active target and hands the path to the engine. These tests pin that the
ported loader resolves the same paths and fails the same way as the legacy one.
"""

import os

import pytest

import taichi as ti

legacy_loader_module = pytest.importorskip("taichi.tcm_loader")
LegacyLoader = legacy_loader_module.AOTModuleLoader


class _StubEngine:
    """Minimal engine surface the loader touches."""

    arch = "vulkan"
    gpu_name = "Intel(R) UHD Graphics 620"
    _generation = 1

    def __init__(self):
        self.loaded = []

    def load(self, path):
        self.loaded.append(path)
        return type("Module", (), {"module_ptr": 1, "engine_generation": 1})()


def _loaders():
    engine_a, engine_b = _StubEngine(), _StubEngine()
    repo_tcm = os.path.join(os.getcwd(), "taichi_vision", "taichi_algorithm", "aot_tcm")
    return (
        LegacyLoader(engine_a, tcm_dir=repo_tcm),
        ti.AOTModuleLoader(engine_b, tcm_dir=repo_tcm),
        engine_a,
        engine_b,
    )


def test_target_resolution_matches():
    legacy, migrated, _, _ = _loaders()
    old_target, old_dir = legacy.resolve_target()
    new_target, new_dir = migrated.resolve_target()
    assert new_target.as_dict() == old_target.as_dict()
    assert new_dir == old_dir


def test_existing_module_directory_resolves_identically():
    legacy, migrated, _, _ = _loaders()
    target, active_dir = legacy.resolve_target()
    if not os.path.isdir(active_dir):
        pytest.skip("no compiled TCM tree on this host")
    entries = [
        name
        for name in sorted(os.listdir(active_dir))
        if os.path.isdir(os.path.join(active_dir, name))
    ]
    if not entries:
        pytest.skip("TCM tree has no per-algorithm directories")
    name = entries[0]
    assert migrated.resolve_module_path(name, target, active_dir) == legacy.resolve_module_path(
        name, target, active_dir
    )


def test_missing_artifact_raises_the_same_error():
    legacy, migrated, _, _ = _loaders()
    target, active_dir = legacy.resolve_target()
    with pytest.raises(FileNotFoundError) as old_err:
        legacy.resolve_module_path("definitely_missing_algorithm", target, active_dir)
    with pytest.raises(FileNotFoundError) as new_err:
        migrated.resolve_module_path("definitely_missing_algorithm", target, active_dir)
    assert str(new_err.value).replace(str(active_dir), "<root>") == str(old_err.value).replace(
        str(active_dir), "<root>"
    )


def test_warmup_reports_the_same_shape():
    legacy, migrated, engine_a, engine_b = _loaders()
    names = ["definitely_missing_algorithm"]
    old = legacy.warmup(names)
    new = migrated.warmup(names)
    assert new["total_modules"] == old["total_modules"]
    assert new["loaded_modules"] == old["loaded_modules"]
    assert len(new["deferred_modules"]) == len(old["deferred_modules"])
    assert [n for n, _ in new["deferred_modules"]] == [n for n, _ in old["deferred_modules"]]


def test_loader_uses_canonical_environment_names():
    """The port must not introduce brand-prefixed environment variables."""
    import inspect


    text = inspect.getsource(ti.AOTModuleLoader)
    assert "PIXEL_REFINE" not in text
    assert 'AOT_TCM_ROOT' in text
