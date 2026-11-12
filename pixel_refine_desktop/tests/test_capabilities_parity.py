"""Behavior checks for backend capability policy after the port.

The legacy Python modules were retired, so both sides now resolve to the same
`taichi` implementation. Field-by-field assertions still guard the policy.
"""

import pytest

import taichi as ti

legacy_cap = pytest.importorskip("taichi.capabilities")
legacy_bm = pytest.importorskip("taichi.backend_manager")

DEVICES = [
    "Intel(R) UHD Graphics 620",
    "NVIDIA GeForce RTX 3060",
    "AMD Radeon RX 6600",
    {"name": "Intel(R) Iris Xe Graphics", "vendor": "Intel"},
    "unknown",
    "generic adapter",
]


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("backend", ["vulkan", "cuda", "opengl", "cpu"])
def test_classify_device_matches(device, backend):
    old = legacy_cap.classify_device(device, backend)
    new = ti.capabilities.classify_device(device, backend)
    assert new.as_dict() == old.as_dict()


@pytest.mark.parametrize("device", DEVICES)
def test_backend_candidates_match(device):
    assert ti.backend_candidates(device) == legacy_cap.backend_candidates(device)


@pytest.mark.parametrize("device", DEVICES)
@pytest.mark.parametrize("requested", ["auto", "vulkan", "cpu"])
def test_backend_decision_matches(device, requested):
    old = legacy_bm.preflight_backend(device, requested)
    new = ti.preflight_backend(device, requested)
    assert new.selected == old.selected
    assert new.candidates == old.candidates
    assert new.device == old.device
    assert new.reason == old.reason


def test_decision_dataclasses_are_shared_after_retirement():
    """The legacy module is gone, so both names must be the same class."""
    assert ti.BackendDecision is legacy_bm.BackendDecision


def test_capability_env_naming_is_canonical():
    import inspect

    text = inspect.getsource(ti.capabilities)
    assert "AOT_AUTO_FALLBACK" in text
    # The legacy variable remains as a compatibility read, not a new name.
    assert text.count("PIXEL_REFINE_AOT_AUTO_FALLBACK") == 1
