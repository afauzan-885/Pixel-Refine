"""Pure preflight adapter for the TCM/runtime ABI contract.

The adapter deliberately stops before the native loader.  It converts a
contract exception into a structured decision that a future ``AOTEngine.load``
hook can record/quarantine without changing the public algorithm API.
"""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional

try:  # Normal package import after taichi_aot has already been initialized.
    from .tcm_contract import TcmContractError, validate_tcm
except ImportError:  # Standalone/offline loading must not initialize the package.
    _CONTRACT_PATH = Path(__file__).with_name("tcm_contract.py")
    _SPEC = importlib.util.spec_from_file_location("pixel_refine_tcm_contract_preflight", _CONTRACT_PATH)
    if _SPEC is None or _SPEC.loader is None:  # pragma: no cover - packaging error
        raise RuntimeError(f"cannot load TCM contract module: {_CONTRACT_PATH}")
    _CONTRACT = importlib.util.module_from_spec(_SPEC)
    _SPEC.loader.exec_module(_CONTRACT)
    TcmContractError = _CONTRACT.TcmContractError
    validate_tcm = _CONTRACT.validate_tcm


@dataclass(frozen=True, slots=True)
class TcmPreflightDecision:
    """A fail-closed decision made before native TCM loading."""

    allowed: bool
    status: str
    path: str
    reason: str
    report: Optional[Mapping[str, Any]] = None


def preflight_tcm(
    path: str | Path,
    *,
    requested_target: Any = None,
    runtime_abi: int = 1,
    runtime_features: Iterable[str] = (),
    allow_legacy: bool = True,
) -> TcmPreflightDecision:
    """Validate one artifact without calling Taichi or a native bridge.

    Legacy archives are allowed only when ``allow_legacy`` is true.  They are
    explicitly labelled ``legacy`` so release tooling can require manifests
    without changing the compatibility behavior of the current application.
    """

    artifact = str(Path(path).resolve())
    try:
        report = validate_tcm(
            artifact,
            runtime_abi=runtime_abi,
            runtime_features=runtime_features,
            requested_target=requested_target,
        )
    except (OSError, TcmContractError, ValueError) as exc:
        return TcmPreflightDecision(
            allowed=False,
            status="rejected",
            path=artifact,
            reason=str(exc),
            report=None,
        )
    if report.get("status") == "legacy":
        return TcmPreflightDecision(
            allowed=bool(allow_legacy),
            status="legacy" if allow_legacy else "rejected",
            path=artifact,
            reason=(
                "legacy TCM accepted by compatibility policy"
                if allow_legacy
                else "legacy TCM rejected because a manifest is required"
            ),
            report=report,
        )
    return TcmPreflightDecision(
        allowed=True,
        status="valid",
        path=artifact,
        reason="TCM ABI manifest validated before native load",
        report=report,
    )


__all__ = ["TcmPreflightDecision", "preflight_tcm"]
