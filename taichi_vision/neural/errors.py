"""Actionable errors raised by the public ``taichi_vision.neural`` facade.

Every error names the missing capability and the concrete remedy, so a caller
never has to dig into kernel-level internals to understand a refusal.
"""

from __future__ import annotations

from typing import Iterable, Sequence


def _format_items(items: Iterable[str], limit: int = 8) -> str:
    values = sorted(set(items))
    if not values:
        return "(none)"
    shown = ", ".join(values[:limit])
    if len(values) > limit:
        shown += f", ... (+{len(values) - limit} more)"
    return shown


class NeuralError(RuntimeError):
    """Base class for every public neural facade failure."""


class BackendUnavailable(NeuralError):
    """The requested backend has no staged artifact or device support."""

    def __init__(self, backend: str, attempts: Sequence[str] = ()):
        detail = f" attempts={list(attempts)}" if attempts else ""
        super().__init__(
            f"backend {backend!r} is not available for the neural runtime{detail}. "
            "Stage the target-qualified pool artifact and verify its manifest, "
            "or select a backend that is already qualified."
        )
        self.backend = backend
        self.attempts = tuple(attempts)


class CapabilityMissingError(NeuralError):
    """No execution strategy covers this model on the selected backend.

    Carries the structured refusal so callers *and* tests can inspect exactly
    which operators or runtime features were missing.
    """

    def __init__(
        self,
        model: str,
        *,
        missing_ops: Iterable[str] = (),
        missing_features: Iterable[str] = (),
        attempts: Sequence[str] = (),
        remedy: str = "",
    ):
        self.model = model
        self.missing_ops = tuple(sorted(set(missing_ops)))
        self.missing_features = tuple(sorted(set(missing_features)))
        self.attempts = tuple(attempts)
        self.remedy = remedy

        lines = [f"model {model!r} cannot run on the Taichi neural runtime"]
        if self.missing_ops:
            lines.append(f"  operators without a lowering: {_format_items(self.missing_ops)}")
        if self.missing_features:
            lines.append(f"  runtime features absent: {_format_items(self.missing_features)}")
        if self.attempts:
            lines.append("  strategies tried:")
            lines.extend(f"    - {item}" for item in self.attempts)
        if remedy:
            lines.append(f"  remedy: {remedy}")
        super().__init__("\n".join(lines))


class ModelNotRunnable(NeuralError):
    """The model graph itself is invalid or unsupported by every strategy."""

    def __init__(self, model: str, reason: str):
        super().__init__(f"model {model!r} is not runnable: {reason}")
        self.model = model
        self.reason = reason


__all__ = [
    "NeuralError",
    "BackendUnavailable",
    "CapabilityMissingError",
    "ModelNotRunnable",
]
