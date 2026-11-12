"""Runtime configuration for the taichi fault tracer.

Environment contract
--------------------
``TAICHI_FAULT``
    ``off``/``0`` disables the tracer, ``light`` records only call names and
    timings, ``full`` (default) also records argument/local summaries.
``TAICHI_FAULT_DIR``
    Directory for JSON fault artifacts (default: ``%TEMP%/taichi_fault_trace``).
``TAICHI_FAULT_MAX_ARTIFACTS``
    Rolling retention for artifacts (default 50).
``TAICHI_FAULT_EXTRA``
    Comma separated modules to instrument in addition to ``taichi``.
``TAICHI_FAULT_RAISE``
    ``1`` turns every enriched fault into ``TaichiFaultError`` (opt-in; the
    default preserves the original exception type for compatibility).
``TAICHI_FAULT_FAULTHANDLER``
    ``0`` disables the faulthandler log used for native crashes.
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path

_FALSY = {"0", "off", "false", "no", "none", "disabled"}


def _env_flag(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in _FALSY


def _default_report_dir() -> Path:
    override = os.environ.get("TAICHI_FAULT_DIR", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(tempfile.gettempdir()) / "taichi_fault_trace"


def _mode() -> str:
    raw = os.environ.get("TAICHI_FAULT")
    if raw is None:
        return "full"
    token = raw.strip().lower()
    if token in _FALSY:
        return "off"
    if token in {"light", "lite", "minimal"}:
        return "light"
    return "full"


@dataclass(frozen=True)
class TraceConfig:
    mode: str = "full"
    report_dir: Path = Path(".")
    max_artifacts: int = 50
    max_frames: int = 40
    max_locals: int = 12
    max_value_chars: int = 220
    max_sequence_items: int = 6
    capture_args: bool = True
    capture_locals: bool = True
    render_on_error: bool = True
    render_on_uncaught: bool = True
    raise_enriched: bool = False
    faulthandler: bool = True
    dedupe_seconds: float = 2.0
    stdout: bool = False
    extra_modules: tuple[str, ...] = ()

    @property
    def enabled(self) -> bool:
        return self.mode != "off"

    @property
    def full(self) -> bool:
        return self.mode == "full"


def _parse_extra() -> tuple[str, ...]:
    raw = os.environ.get("TAICHI_FAULT_EXTRA", "")
    names = [chunk.strip() for chunk in raw.replace(";", ",").split(",")]
    return tuple(name for name in names if name)


def load_config(**overrides) -> TraceConfig:
    """Build the trace config from the environment plus explicit overrides."""

    config = TraceConfig(
        mode=_mode(),
        report_dir=_default_report_dir(),
        max_artifacts=max(1, int(os.environ.get("TAICHI_FAULT_MAX_ARTIFACTS", "50") or 50)),
        max_frames=max(4, int(os.environ.get("TAICHI_FAULT_MAX_FRAMES", "40") or 40)),
        capture_args=_env_flag("TAICHI_FAULT_ARGS", True),
        capture_locals=_env_flag("TAICHI_FAULT_LOCALS", True),
        render_on_error=_env_flag("TAICHI_FAULT_RENDER", True),
        render_on_uncaught=_env_flag("TAICHI_FAULT_RENDER_UNCAUGHT", True),
        raise_enriched=_env_flag("TAICHI_FAULT_RAISE", False),
        faulthandler=_env_flag("TAICHI_FAULT_FAULTHANDLER", True),
        stdout=_env_flag("TAICHI_FAULT_STDOUT", False),
        extra_modules=_parse_extra(),
    )
    if overrides:
        config = replace(config, **overrides)
    return config


_CURRENT: TraceConfig | None = None


def current_config() -> TraceConfig:
    global _CURRENT
    if _CURRENT is None:
        _CURRENT = load_config()
    return _CURRENT


def set_config(config: TraceConfig) -> TraceConfig:
    global _CURRENT
    _CURRENT = config
    return config
