"""Removal/mutation regression gates before any native artifact is loaded."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from taichi_vision.taichi_aot.neural_universal.scalar_specialization import compiler_fingerprint
from taichi_vision.taichi_aot.neural_universal.static_session import StaticGraphSession

ROOT = Path(__file__).resolve().parents[3]
VARIANT = "binary_chain_scalar_specialized_v3"
VARIANTS = {
    "runtime_scalars_v3": ("scalar_runtime_strict", "runtime_scalars"),
    "scalar_specialized_v3": ("scalar_specialized_strict", "scalar_specialized"),
    VARIANT: ("binary_chain_specialized_strict", "binary_chain_scalar_specialized"),
}
EXACT_FUSED = (ROOT / "taichi_vision/taichi_aot/neural_universal/models/binary_chain_cpu_x86_64_windows_20261027_v1"
    / "93ddbcdbf2dfcc283aaaf1e3f3692fa97bd9ccdcdfb3ac0f3fda43025d4bfce5/cpu/binary_chain_specialized_strict/profile.json")


def _manifest(variant=VARIANT):
    # Deep-copy each exact prior accepted sidecar. Only
    # upgrade metadata in memory for schema guard testing; never rewrite it.
    previous, mode = VARIANTS[variant]
    profile = copy.deepcopy(json.loads((EXACT_FUSED.parent.parent / previous / "profile.json").read_text()))
    profile.update(schema_version=2, compiler_schema_version=2, compiler_mode=mode, profile_variant=variant)
    profile["compiler_policy"].update(schema_version=2, mode=mode, source_sha256=compiler_fingerprint())
    return profile


def _session(profile, variant):
    instance = StaticGraphSession.__new__(StaticGraphSession)
    instance.profile_variant = variant
    instance.model_sha256 = profile["model_sha256"]
    instance.backend = profile["backend"]
    instance.engine = NS(gpu_name="")
    instance.plan = NS(dtypes=profile["model_input_dtypes"], input_names=list(profile["model_input_shapes"]), output_names=list(profile["outputs"]))
    return instance


@pytest.mark.parametrize("variant", VARIANTS)
def test_exact_current_profile_accepted_with_required_schema(variant):
    profile = _manifest(variant)
    _session(profile, variant)._validate_profile(profile)


@pytest.mark.parametrize("variant", VARIANTS)
@pytest.mark.parametrize("change", ["remove_policy", "remove_every_marker", "policy_none", "policy_list", "policy_schema", "top_schema", "mode", "hash", "fast_math", "variant",
    "schema_float", "schema_bool", "top_schema_float", "top_schema_bool", "policy_schema_float", "policy_schema_bool"])
def test_policy_tampering_rejected_before_native_load(monkeypatch, change, variant):
    import taichi_vision.taichi_aot.neural_universal.static_session as module
    profile = _manifest(variant)
    if change == "remove_policy": profile.pop("compiler_policy")
    elif change == "remove_every_marker":
        for name in ["compiler_policy", "compiler_schema_version", "compiler_mode", "profile_variant", "schema_version", "binary_regions"]:
            profile.pop(name, None)
    elif change == "policy_none": profile["compiler_policy"] = None
    elif change == "policy_list": profile["compiler_policy"] = []
    elif change == "policy_schema": profile["compiler_policy"]["schema_version"] = 99
    elif change == "top_schema": profile["compiler_schema_version"] = "2"
    elif change == "mode": profile["compiler_policy"]["mode"] = "invalid_mode"
    elif change == "hash": profile["compiler_policy"]["source_sha256"] = "0" * 64
    elif change == "fast_math": profile["compiler_policy"]["fast_math"] = True
    elif change == "variant": profile["profile_variant"] = "another_variant"
    elif change == "schema_float": profile["schema_version"] = 2.0
    elif change == "schema_bool": profile["schema_version"] = True
    elif change == "top_schema_float": profile["compiler_schema_version"] = 2.0
    elif change == "top_schema_bool": profile["compiler_schema_version"] = True
    elif change == "policy_schema_float": profile["compiler_policy"]["schema_version"] = 2.0
    elif change == "policy_schema_bool": profile["compiler_policy"]["schema_version"] = True
    engine = NS(load=lambda *args: pytest.fail("native load must not happen"))
    plan = NS()
    monkeypatch.setattr(module, "UniversalSession", lambda *args, **kwargs: NS(engine=engine, backend="cpu", plan=plan, model_bytes=b"guard-only"))
    monkeypatch.setattr(module, "load_static_profile", lambda *args: copy.deepcopy(profile))
    session = StaticGraphSession(b"guard-only", backend="cpu", profile_root=ROOT, profile_variant=variant)
    assert not session.fast_path_active
    assert "compiler" in session.last_fallback_reason


def test_genuine_historical_none_variant_remains_compatible(monkeypatch):
    import taichi_vision.taichi_aot.neural_universal.static_session as module
    historical = (ROOT / "pixel_refine_desktop/ui/data/aot_assets/neural/universal/models"
        / "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184/cpu/profile.json")
    profile = json.loads(historical.read_text())
    assert profile["schema_version"] == 1 and "compiler_policy" not in profile
    # Simulate the recorded historical environment rather than modifying its
    # immutable manifest to pretend its stale kernel fingerprint is current.
    monkeypatch.setattr(module, "_kernel_source_fingerprint", lambda: profile["kernel_sources_sha256"])
    monkeypatch.setattr(module, "_configured_runtime_abi", lambda: profile["runtime_abi"])
    monkeypatch.setattr(module, "_target_identity", lambda *args: profile["target_identity"])
    _session(profile, None)._validate_profile(profile)


def test_exact_old_manifest_policy_removal_rejected_even_with_regions():
    exact = copy.deepcopy(json.loads(EXACT_FUSED.read_text()))
    exact.pop("compiler_policy")
    assert len(exact["binary_regions"]) == 5
    with pytest.raises(ValueError, match="requires compiler policy"):
        _session(exact, "explicit_variant_v3")._validate_profile(exact)
