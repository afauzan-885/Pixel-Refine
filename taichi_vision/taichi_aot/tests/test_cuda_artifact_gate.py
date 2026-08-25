"""Regression tests for CUDA target-qualified artifact quarantine.

These tests exercise the resolver and the offline TCM preflight independently
of a CUDA driver.  A CUDA archive containing only host LLVM IR must never be
selected, while an otherwise identical archive with an NVPTX target remains
loadable by the normal resolver.
"""

from __future__ import annotations

from pathlib import Path
import zipfile

from taichi_vision.taichi_aot.artifact_targets import TargetSpec, resolve_artifact
from taichi_vision.taichi_aot.tcm_preflight import preflight_tcm


CUDA_TARGET = TargetSpec(
    backend="cuda",
    arch="x86_64",
    os="windows",
    vendor="nvidia",
)


def _write_legacy_cuda(path: Path, triple: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("__version__", "1.7.4")
        archive.writestr("graphs.tcb", b"graph")
        archive.writestr("kernel.ll", f'target triple = "{triple}"\n'.encode())


def test_resolver_quarantines_host_only_cuda_archive(tmp_path: Path) -> None:
    """A stale host payload is not selected merely due to its CUDA filename."""

    path = tmp_path / CUDA_TARGET.target_id / CUDA_TARGET.artifact_name("sfm_registration")
    _write_legacy_cuda(path, "x86_64-pc-windows-msvc19.44.35228")

    assert resolve_artifact(tmp_path, "sfm_registration", CUDA_TARGET, allow_legacy=False) is None
    decision = preflight_tcm(path, requested_target=CUDA_TARGET.as_dict())
    assert decision.allowed is False
    assert decision.status == "rejected"
    assert "expected NVPTX LLVM triple" in decision.reason


def test_resolver_keeps_valid_cuda_archive_selected(tmp_path: Path) -> None:
    """The host-payload gate must not affect a valid NVPTX archive."""

    path = tmp_path / CUDA_TARGET.target_id / CUDA_TARGET.artifact_name("sfm_stereo")
    _write_legacy_cuda(path, "nvptx64-nvidia-cuda")

    resolved = resolve_artifact(tmp_path, "sfm_stereo", CUDA_TARGET, allow_legacy=False)
    assert resolved == path
    decision = preflight_tcm(path, requested_target=CUDA_TARGET.as_dict())
    assert decision.allowed is True
    assert decision.status == "legacy"


def test_legacy_cuda_host_payload_cannot_be_enabled_by_compatibility_flag(tmp_path: Path) -> None:
    """allow_legacy only controls manifest compatibility, not target safety."""

    path = tmp_path / "sfm_registration_cuda.tcm"
    _write_legacy_cuda(path, "x86_64-pc-windows-msvc19.44.35228")
    assert resolve_artifact(tmp_path, "sfm_registration", CUDA_TARGET, allow_legacy=True) is None

