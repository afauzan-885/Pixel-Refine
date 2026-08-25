from __future__ import annotations

import pytest

from taichi_vision.cuda_arch_matrix import (
    _run_target_probe,
    bridge_target_status,
    normalize_compute_capability,
    normalize_cuda_target,
    query_nvidia_smi,
    simulate_cuda_device,
    validate_bridge_manifest,
)
from taichi_vision.taichi_algorithm.aot_py.validate_cuda_tcm_codegen import (
    _graph_inventory,
    _lowering_summary,
    _target_gate_diagnostics,
    _unsupported_ir_features,
)
from taichi_vision.taichi_aot.llvm20_profiles import CUDA_X86_64_WINDOWS_NVIDIA


def test_bridge_manifest_keeps_blackwell_variant_tokens_lossless() -> None:
    manifest = validate_bridge_manifest(
        {
            "schema_version": 1,
            "backend": "cuda",
            "runtime_sms": ["sm_120", "sm_120a"],
            "graph_lowering_sms": ["sm_120a"],
            "native_runtime_sms": ["sm_120a"],
        }
    )

    assert "sm_120a" in manifest["runtime_sms"]
    assert "sm_120a" in manifest["native_runtime_sms"]
    assert bridge_target_status("sm_120a", manifest) == "native"
    # The baseline and architecture-specific variant are distinct bridge
    # claims; evidence for one must not silently qualify the other.
    assert bridge_target_status("sm_120", manifest) == "runtime_candidate"


def test_numeric_manifest_remains_backward_compatible() -> None:
    manifest = validate_bridge_manifest(
        {
            "schema_version": 1,
            "backend": "cuda",
            "runtime_sms": [52, "sm_61"],
            "graph_lowering_sms": ["sm_61"],
        }
    )

    assert manifest["runtime_sms"] == [52, 61]
    assert bridge_target_status(52, manifest) == "runtime_candidate"
    assert bridge_target_status(61, manifest) == "runtime_candidate"


@pytest.mark.parametrize("value", ["11.0", "110", "sm_110", "compute_110"])
def test_thor_driver_spelling_maps_to_canonical_blackwell(value: object) -> None:
    # NVIDIA tooling may report the Thor/Blackwell target as 11.0 (or sm_110),
    # while the canonical target model uses CC 10.1.  The compatibility API
    # must accept every spelling instead of dropping the device from probes.
    assert normalize_compute_capability(value) == 101


def test_nvidia_smi_query_keeps_thor_device(monkeypatch) -> None:
    from types import SimpleNamespace

    def fake_run(command, **kwargs):
        return SimpleNamespace(
            returncode=0,
            stdout="0, NVIDIA Thor, 580.1, 11.0, 16384\n",
            stderr="",
        )

    monkeypatch.setattr("taichi_vision.cuda_arch_matrix.subprocess.run", fake_run)
    devices = query_nvidia_smi()
    assert devices and devices[0]["compute_capability"] == 101
    assert devices[0]["target"] == "sm_101"
    assert devices[0]["architecture"] == "Blackwell"


def test_nvidia_smi_query_is_fail_closed_for_nonzero_status(monkeypatch) -> None:
    from types import SimpleNamespace

    monkeypatch.setattr(
        "taichi_vision.cuda_arch_matrix.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=1,
            stdout="0, NVIDIA RTX, 580.1, 8.9, 8192\n",
            stderr="driver unavailable",
        ),
    )
    assert query_nvidia_smi() == []


def test_nvidia_smi_query_skips_malformed_rows_and_keeps_quoted_names(monkeypatch) -> None:
    from types import SimpleNamespace

    monkeypatch.setattr(
        "taichi_vision.cuda_arch_matrix.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=(
                'bad, row, not, a, device\n'
                '0,"NVIDIA, Test GPU",580.1,8.9,N/A\n'
            ),
            stderr="",
        ),
    )
    devices = query_nvidia_smi()
    assert len(devices) == 1
    assert devices[0]["name"] == "NVIDIA, Test GPU"
    assert devices[0]["compute_capability"] == 89
    assert devices[0]["memory_mb"] is None


def test_nvidia_smi_query_rejects_invalid_physical_metadata(monkeypatch) -> None:
    from types import SimpleNamespace

    monkeypatch.setattr(
        "taichi_vision.cuda_arch_matrix.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout=(
                "-1, NVIDIA Invalid, 580.1, 8.9, 8192\\n"
                "0,,580.1,8.9,8192\\n"
                "1,NVIDIA Invalid,,8.9,8192\\n"
                "2,NVIDIA Invalid,580.1,8.9,-1\\n"
            ),
            stderr="",
        ),
    )
    assert query_nvidia_smi() == []


@pytest.mark.parametrize("value", ["sm_50", "compute_50", "5.0"])
def test_simulator_is_explicitly_compile_only(value: object) -> None:
    record = simulate_cuda_device(value)
    assert record["physical_device"] is False
    assert record["simulated"] is True
    assert record["qualification"] == "compile_only"
    assert record["native_runtime_tested"] is False


def test_variant_subset_is_exact_not_numeric() -> None:
    with pytest.raises(ValueError, match="subset"):
        validate_bridge_manifest(
            {
                "schema_version": 1,
                "backend": "cuda",
                "runtime_sms": ["sm_120"],
                "custom_runtime_sms": ["sm_120a"],
            }
        )


def test_manifest_rejects_duplicate_sm_targets() -> None:
    with pytest.raises(ValueError, match="duplicate SM targets"):
        validate_bridge_manifest(
            {
                "schema_version": 1,
                "backend": "cuda",
                "runtime_sms": ["sm_61", 61],
            }
        )


def test_graph_evidence_requires_complete_inventory_for_full_claim() -> None:
    base = {
        "schema_version": 1,
        "backend": "cuda",
        "runtime_sms": ["sm_61"],
        "graph_lowering_sms": ["sm_61"],
    }
    with pytest.raises(ValueError, match="complete inventory"):
        validate_bridge_manifest(
            {
                **base,
                "graph_lowering_evidence": {
                    "sm_61": {
                        "expected_graphs": 3,
                        "observed_results": 3,
                        "passed_graphs": 3,
                        "full_graph": True,
                        "inventory_complete": False,
                    }
                },
            }
        )
    normalized = validate_bridge_manifest(
        {
            **base,
            "graph_lowering_evidence": {
                "sm_61": {
                    "expected_graphs": 3,
                    "observed_results": 3,
                    "passed_graphs": 3,
                    "full_graph": True,
                    "inventory_complete": True,
                }
            },
        }
    )
    assert normalized["graph_lowering_evidence"]["sm_61"]["full_graph"] is True


@pytest.mark.parametrize("field", ["expected_graphs", "observed_results", "passed_graphs"])
@pytest.mark.parametrize("value", [True, 1.5, "3"])
def test_graph_evidence_counts_reject_non_integer_metadata(field: str, value: object) -> None:
    with pytest.raises(ValueError, match="counts must be integers"):
        validate_bridge_manifest(
            {
                "schema_version": 1,
                "backend": "cuda",
                "runtime_sms": ["sm_61"],
                "graph_lowering_sms": ["sm_61"],
                "graph_lowering_evidence": {
                    "sm_61": {
                        "expected_graphs": 3,
                        "observed_results": 3,
                        "passed_graphs": 3,
                        field: value,
                    }
                },
            }
        )


def test_llvm20_cuda_profile_covers_lowered_and_blackwell_variants() -> None:
    variants = set(CUDA_X86_64_WINDOWS_NVIDIA.optional_variants)
    assert {"sm_52", "sm_53", "sm_61", "sm_120", "sm_120a", "sm_120f"} <= variants


def test_full_graph_summary_does_not_promote_partial_sweep() -> None:
    from taichi_vision.cuda_arch_matrix import normalize_cuda_target

    target = normalize_cuda_target("sm_61")
    result = {
        "sm": "sm_61",
        "archive": "common.tcm",
        "graph": "one.ll",
        "ok": True,
        "stage": "llc",
    }
    partial = _lowering_summary(
        [result], targets=[target], graph_count=2
    )
    assert partial["full_graph"] is False
    assert partial["qualified_targets"] == []
    assert partial["target_summaries"][0]["status"] == "partial"

    complete = _lowering_summary(
        [result, {**result, "graph": "two.ll"}], targets=[target], graph_count=2
    )
    assert complete["full_graph"] is True
    assert complete["qualified_targets"] == ["sm_61"]


def test_sm50_dynamic_stack_intrinsics_are_rejected_before_llc() -> None:
    payload = (
        b"declare ptr @llvm.stacksave.p0()\n"
        b"declare void @llvm.stackrestore.p0(ptr)\n"
    )
    errors = _unsupported_ir_features(payload, normalize_cuda_target("sm_50"))
    assert errors == (
        "dynamic stack allocation requires SM52+ (llvm.stacksave)",
        "dynamic stack allocation requires SM52+ (llvm.stackrestore)",
    )


def test_sm52_dynamic_stack_intrinsics_are_allowed_by_feature_gate() -> None:
    payload = b"declare ptr @llvm.stacksave.p0()\n"
    assert _unsupported_ir_features(payload, normalize_cuda_target("sm_52")) == ()


def test_unknown_llvm_target_warnings_are_not_successful_lowering() -> None:
    diagnostics = _target_gate_diagnostics(
        "'sm_103' is not a recognized processor for this target (ignoring processor)\n"
        "'+ptx88' is not a recognized feature for this target (ignoring feature)\n"
    )
    assert len(diagnostics) == 2


def test_graph_inventory_records_bad_and_empty_archives(tmp_path) -> None:
    import zipfile

    (tmp_path / "broken.tcm").write_bytes(b"not a zip")
    with zipfile.ZipFile(tmp_path / "empty.tcm", "w"):
        pass
    with zipfile.ZipFile(tmp_path / "valid.tcm", "w") as archive:
        archive.writestr("kernel.ll", b"define void @kernel() { ret void }\n")

    graphs, errors, empty = _graph_inventory(tmp_path)
    assert len(graphs) == 1
    assert errors and errors[0]["archive"] == "broken.tcm"
    assert empty == ["empty.tcm"]


def test_nvcc_probe_passes_explicit_stdin_operand(monkeypatch) -> None:
    """The nvcc stdin probe must not report false failures for every SM."""

    from types import SimpleNamespace

    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout=".target sm_61\n", stderr="")

    monkeypatch.setattr("taichi_vision.cuda_arch_matrix.subprocess.run", fake_run)
    result = _run_target_probe("nvcc", "sm_61", mode="nvcc", timeout=1)

    assert result["ok"] is True
    command, kwargs = calls[0]
    assert command[-1] == "-"
    assert command[-2:] == ["-", "-"]
    assert kwargs["input"].startswith('extern "C" __device__')


def test_compile_probe_reports_explicit_coverage_summary(monkeypatch) -> None:
    """Aggregate coverage must distinguish compile-only support from runtime."""

    from types import SimpleNamespace
    from taichi_vision.cuda_arch_matrix import probe_compiler_targets

    def fake_run(command, **kwargs):
        target = next(item for item in command if str(item).startswith("--gpu-architecture="))
        ok = target.endswith("compute_61")
        return SimpleNamespace(
            returncode=0 if ok else 1,
            stdout=".target sm_61\n" if ok else "unsupported target\n",
            stderr="",
        )

    monkeypatch.setattr("taichi_vision.cuda_arch_matrix.subprocess.run", fake_run)
    report = probe_compiler_targets("nvcc", ["sm_61", "sm_120"], mode="nvcc")
    assert report["summary"] == {
        "requested_targets": 2,
        "passed_targets": 1,
        "failed_targets": 1,
        "supported_targets": ["sm_61"],
        "unsupported_targets": ["sm_120"],
        "all_passed": False,
        "qualification": "compile_only",
    }
    assert report["native_runtime_tested"] is False
