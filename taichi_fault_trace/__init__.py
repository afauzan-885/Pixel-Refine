"""Readable fault tracing for the taichi 1.8.0 runtime in this venv.

Public surface::

    import taichi_fault_trace as tft

    tft.install()                    # instrument taichi + future imports
    tft.instrument("my.module")      # extend coverage to app modules
    with tft.trace_scope("burst"):   # explicit logical boundary
        ...

    tft.diagnose()                   # backend/device/artifact snapshot
    tft.last_report()                # last FaultReport (or None)

The tracer never replaces the original exception type unless
``TAICHI_FAULT_RAISE=1`` is set; reports are attached with
``add_note`` (PEP 678) and written to ``TAICHI_FAULT_DIR``.
"""

from __future__ import annotations

from typing import Any

from ._config import TraceConfig, current_config, load_config, set_config as _configure
from ._native import diagnose, environment_snapshot, native_snapshot
from ._report import FaultReport, last_report, reset_dedupe
from ._wrap import (
    current_call_chain,
    install,
    instrument,
    is_installed,
    trace,
    trace_scope,
    uninstall,
    wrapped_inventory,
)

__all__ = [
    "TraceConfig",
    "FaultReport",
    "TaichiFaultError",
    "configure",
    "current_call_chain",
    "current_config",
    "diagnose",
    "environment_snapshot",
    "install",
    "instrument",
    "is_installed",
    "last_report",
    "load_config",
    "native_snapshot",
    "reset_dedupe",
    "trace",
    "trace_scope",
    "uninstall",
    "version",
    "wrapped_inventory",
]

version = "1.0.0"


class TaichiFaultError(RuntimeError):
    """RuntimeError carrying a fully rendered taichi fault report.

    It subclasses ``RuntimeError`` so existing ``except RuntimeError`` handlers
    keep working when enrichment is enabled explicitly.
    """

    def __init__(self, report: FaultReport):
        super().__init__(
            f"[{report.code}] {report.title}: "
            f"{report.exception_type}: {report.message}"
        )
        self.report = report

    def __str__(self) -> str:
        return self.report.render() if self.report else super().__str__()


def configure(**overrides: Any) -> TraceConfig:
    """Update the active config (only explicit keyword overrides)."""

    config = load_config(**overrides)
    _configure(config)
    return config
