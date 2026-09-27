"""Engine-facing memory policy boundary.

The policy implementation currently lives in :mod:`memory` because it is also
used by standalone telemetry/tests.  This adapter gives the engine a stable
ownership boundary while allocator and lifecycle code are extracted in later
steps.  It deliberately preserves ``MemoryGovernor``'s state/method surface
so existing engine integrations and telemetry remain compatible.
"""

from .memory import (
    CacheTelemetry,
    MemoryDecision,
    MemoryGovernor,
    MemoryPressure,
    MemorySnapshot,
    system_memory_snapshot,
    validate_memory_decision,
)


class MemoryPolicy(MemoryGovernor):
    """Compatibility-preserving policy boundary for the AOT engine.

    This is intentionally a thin subclass in the first migration step.  The
    sampling and budget equations remain single-sourced in ``memory.py``;
    moving them here later can therefore be done without changing the engine's
    public status/configuration contract.
    """


__all__ = [
    "CacheTelemetry",
    "MemoryDecision",
    "MemoryGovernor",
    "MemoryPolicy",
    "MemoryPressure",
    "MemorySnapshot",
    "system_memory_snapshot",
    "validate_memory_decision",
]
