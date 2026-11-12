"""Parity of artifact target and runtime path resolution.

Both modules were ported verbatim, but the runtime path module used to derive
its project root from its own file location. Inside the taichi package that
would point at site-packages, so the port resolves the project root from the
installed taichi_vision package (or TAICHI_PROJECT_ROOT) and this test pins the
equality against the legacy resolver.
"""

import pytest

import taichi as ti
import taichi.runtime_paths as new_paths

legacy_art = pytest.importorskip("taichi.artifact_targets")
legacy_paths = pytest.importorskip("taichi.runtime_paths")


def test_detect_target_fields_match():
    old = legacy_art.detect_target()
    new = ti.detect_target()
    # The dataclass classes differ by design (legacy must stay removable), so
    # parity is asserted on the resolved fields.
    assert old.as_dict() == new.as_dict()


@pytest.mark.parametrize("value", ["cpu", "cuda", "vulkan", "opengl", "GL", "cpu_x86_64_windows"])
def test_canonical_backend_matches(value):
    assert legacy_art.canonical_backend(value) == ti.canonical_backend(value)


def test_project_root_matches_legacy_location():
    assert new_paths.PROJECT_ROOT == legacy_paths.PROJECT_ROOT


@pytest.mark.parametrize("target", ["cpu_x86_64_windows", "vulkan_x86_64_windows"])
def test_tcm_and_assets_roots_match(target):
    assert new_paths.tcm_root(target) == legacy_paths.tcm_root(target)
    assert new_paths.application_assets_root(target) == legacy_paths.application_assets_root(target)


def test_runtime_root_matches():
    assert new_paths.runtime_root() == legacy_paths.runtime_root()


def test_resolve_artifact_matches_on_missing_case(tmp_path):
    old_target = legacy_art.detect_target()
    new_target = ti.detect_target()
    with pytest.raises(Exception) as old_err:
        legacy_art.resolve_artifact("definitely_missing", old_target, root=str(tmp_path))
    with pytest.raises(Exception) as new_err:
        ti.resolve_artifact("definitely_missing", new_target, root=str(tmp_path))
    assert type(old_err.value).__name__ == type(new_err.value).__name__
