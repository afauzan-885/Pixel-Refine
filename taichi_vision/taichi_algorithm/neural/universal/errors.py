"""Shared errors for the neural universal runtime."""

from __future__ import annotations


class NeuralUniversalError(RuntimeError):
    """Base class for neural universal failures."""


class UnsupportedONNXOperatorError(NeuralUniversalError, ValueError):
    """Raised when a graph uses an operator or attribute outside the admitted profile."""


class UnsupportedStepError(NeuralUniversalError):
    """Raised when a lowering step has no dispatch implementation.

    The universal runtime must never silently skip a step: a missing branch is a
    programming error, not a reason to return stale buffers.
    """


class ArtifactError(NeuralUniversalError):
    """Raised when a compiled pool artifact does not match its expected manifest."""