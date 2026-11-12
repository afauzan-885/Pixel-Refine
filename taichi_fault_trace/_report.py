"""Fault record construction, human rendering, and JSON artifacts."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ._config import TraceConfig, current_config
from ._hints import Hint, resolve_hints
from ._native import (
    artifact_snapshot,
    environment_snapshot,
    find_artifacts,
    native_snapshot,
)
from ._summarize import summarize

_EMIT_LOCK = threading.Lock()
_LAST_FINGERPRINT: str | None = None
_LAST_EMIT: float = 0.0
_LAST_REPORT: "FaultReport | None" = None

# Expected, already-handled frontend stubs and shutdown noise stay quiet unless
# TAICHI_FAULT_ALL=1 or the exception escapes to the interpreter.
_QUIET_CODES = {"TAICHI-FRONTEND-STUB", "TAICHI-SHUTDOWN"}
_FALSY = {"0", "off", "false", "no", "none", "disabled"}


def _trace_all() -> bool:
    raw = os.environ.get("TAICHI_FAULT_ALL")
    if raw is None:
        return False
    return raw.strip().lower() not in _FALSY


@dataclass(frozen=True)
class CallRecord:
    qualname: str
    arguments: tuple[tuple[str, str], ...] = ()
    elapsed_ms: float = 0.0
    depth: int = 0


@dataclass(frozen=True)
class FrameInfo:
    filename: str
    lineno: int
    function: str
    source: str = ""
    locals: tuple[tuple[str, str], ...] = ()


@dataclass
class FaultReport:
    code: str
    title: str
    severity: str
    exception_type: str
    message: str
    calls: list[CallRecord] = field(default_factory=list)
    frames: list[FrameInfo] = field(default_factory=list)
    native: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    hints: list[Hint] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    created_at: str = ""
    fingerprint: str = ""
    artifact_path: str = ""

    # ------------------------------------------------------------------ render
    def render(self) -> str:
        width = 96
        rule = "-" * width
        lines: list[str] = [
            rule,
            "TAICHI RUNTIME FAULT",
            rule,
            f"KODE        : {self.code}",
            f"JUDUL       : {self.title}",
            f"TINGKAT     : {self.severity}",
            f"WAKTU       : {self.created_at}",
        ]
        env = self.environment or {}
        lines.append(
            f"PID/THREAD  : {env.get('pid')} / {env.get('thread')}"
            f" ({env.get('thread_id')})"
        )
        native = self.native or {}
        lines.append(
            "BACKEND     : "
            f"arch={native.get('arch')} device_id={native.get('device_id')} "
            f"generation={native.get('generation')} "
            f"gpu={native.get('gpu_name')!r} destroyed={native.get('destroyed')}"
        )
        lines.append(f"HANDLE      : {native.get('handle')}")
        lines.append(f"LIBRARY     : {native.get('library')}")
        lines.append(
            "NATIVE      : "
            f"last_error={_quote(native.get('last_error'))} "
            f"context_backend={native.get('context_backend')!r} "
            f"device={native.get('device_name')!r}"
        )
        if native.get("last_init_error"):
            lines.append(f"INIT ERROR  : {native.get('last_init_error')}")
        env_pairs = env.get("env") or {}
        if env_pairs:
            joined = " ".join(f"{key}={value}" for key, value in env_pairs.items())
            lines.append(f"ENV         : {joined}")
        lines.append(f"EXCEPTION   : {self.exception_type}: {self.message}")
        lines.append(f"LAMA FAULT  : {self.elapsed_ms:.3f} ms")
        lines.append("")

        lines.append("RANTAI RUNTIME (pemanggilan terakhir lebih dulu):")
        if self.calls:
            for index, call in enumerate(reversed(self.calls), start=1):
                marker = " <-- memicu" if index == len(self.calls) else ""
                lines.append(
                    f"  {index}. {call.qualname}  "
                    f"({call.elapsed_ms:.3f} ms){marker}"
                )
                for key, value in call.arguments:
                    lines.append(f"       {key} = {value}")
        else:
            lines.append("  <tidak ada pemanggilan runtime yang terekam>")
        lines.append("")

        lines.append("FRAME PYTHON (file:line):")
        if self.frames:
            for index, frame in enumerate(self.frames, start=1):
                location = f"{frame.filename}:{frame.lineno}"
                lines.append(f"  {index}. {frame.function}  @ {location}")
                if frame.source:
                    lines.append(f"       sumber: {frame.source.strip()}")
                if frame.locals:
                    body = ", ".join(f"{k}={v}" for k, v in frame.locals)
                    lines.append(f"       locals: {body}")
        else:
            lines.append("  <tidak ada frame Python>")
        lines.append("")

        if self.artifacts:
            lines.append("ARTEFAK TERKAIT:")
            for item in self.artifacts:
                digest = item.get("sha256") or ""
                lines.append(
                    f"  - {item.get('path')}  size={item.get('size_bytes')} "
                    f"mtime={item.get('mtime')} sha256={digest[:16]}..."
                )
            lines.append("")

        for hint in self.hints:
            lines.append(f"HINT [{hint.id}] ({hint.severity}) {hint.title}")
            if hint.causes:
                lines.append("  Kemungkinan penyebab:")
                for cause in hint.causes:
                    lines.append(f"   - {cause}")
            if hint.checks:
                lines.append("  Langkah periksa:")
                for check in hint.checks:
                    lines.append(f"   - {check}")
            if hint.docs:
                lines.append(f"  Rujukan: {hint.docs}")
            lines.append("")

        if self.artifact_path:
            lines.append(f"LAPORAN JSON: {self.artifact_path}")
        lines.append(rule)
        return "\n".join(lines)

    # ------------------------------------------------------------------- json
    def to_json(self) -> dict[str, Any]:
        return {
            "schema": 1,
            "code": self.code,
            "title": self.title,
            "severity": self.severity,
            "created_at": self.created_at,
            "fingerprint": self.fingerprint,
            "elapsed_ms": self.elapsed_ms,
            "exception": {
                "type": self.exception_type,
                "message": self.message,
            },
            "calls": [
                {
                    "qualname": call.qualname,
                    "elapsed_ms": call.elapsed_ms,
                    "depth": call.depth,
                    "arguments": dict(call.arguments),
                }
                for call in self.calls
            ],
            "frames": [
                {
                    "file": frame.filename,
                    "line": frame.lineno,
                    "function": frame.function,
                    "source": frame.source,
                    "locals": dict(frame.locals),
                }
                for frame in self.frames
            ],
            "native": self.native,
            "environment": self.environment,
            "artifacts": self.artifacts,
            "hints": [
                {
                    "id": hint.id,
                    "title": hint.title,
                    "severity": hint.severity,
                    "causes": list(hint.causes),
                    "checks": list(hint.checks),
                    "docs": hint.docs,
                }
                for hint in self.hints
            ],
            "context": self.context,
        }

    def write(self, config: TraceConfig | None = None) -> str:
        config = config or current_config()
        directory = Path(config.report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = directory / f"fault_{stamp}_{self.fingerprint[:10]}.json"
        payload = self.to_json()
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        os.replace(temporary, path)
        self.artifact_path = str(path)
        _prune(directory, config.max_artifacts)
        return self.artifact_path


def _prune(directory: Path, keep: int) -> None:
    try:
        files = sorted(
            directory.glob("fault_*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        )
    except Exception:
        return
    for stale in files[keep:]:
        try:
            stale.unlink()
        except Exception:
            pass


def _quote(value: Any) -> str:
    if value is None:
        return "<tidak ada>"
    if isinstance(value, str) and not value.strip():
        return '"" (kosong)'
    return repr(value)


def build_report(
    exc: BaseException,
    *,
    calls: list[CallRecord],
    frames: list[FrameInfo],
    artifact_candidates: list[Any],
    elapsed_ms: float,
    engine: Any = None,
    config: TraceConfig | None = None,
) -> FaultReport:
    config = config or current_config()
    message = str(exc) or repr(exc)
    exc_type = type(exc).__name__

    native = native_snapshot(engine)
    environment = environment_snapshot()
    artifacts = find_artifacts(artifact_candidates)
    context = {"native": native, "environment": environment}
    hints = resolve_hints(exc_type, message, context)

    fingerprint = hashlib.sha256(
        f"{exc_type}|{message}|{calls[-1].qualname if calls else ''}|"
        f"{native.get('last_error')}".encode("utf-8", "replace")
    ).hexdigest()

    return FaultReport(
        code=hints[0].id,
        title=hints[0].title,
        severity=hints[0].severity,
        exception_type=exc_type,
        message=message,
        calls=list(calls),
        frames=list(frames),
        native=native,
        environment=environment,
        artifacts=artifacts,
        hints=hints,
        context=context,
        elapsed_ms=float(elapsed_ms),
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        fingerprint=fingerprint,
    )


def emit(
    report: FaultReport,
    exc: BaseException,
    *,
    config: TraceConfig | None = None,
    force: bool = False,
) -> FaultReport:
    """Attach the report to ``exc`` and print/write it once per fingerprint."""

    global _LAST_FINGERPRINT, _LAST_EMIT, _LAST_REPORT
    config = config or current_config()

    try:
        setattr(exc, "__taichi_fault_report__", report)
        note = (
            f"[taichi_fault_trace] {report.code}: {report.title}. "
            f"Detail: {report.artifact_path or '(belum ditulis)'}"
        )
        if hasattr(exc, "add_note"):
            exc.add_note(note)
    except Exception:
        pass

    quiet = (
        report.code in _QUIET_CODES and not force and not _trace_all()
    )

    with _EMIT_LOCK:
        now = time.monotonic()
        duplicate = (
            not force
            and report.fingerprint == _LAST_FINGERPRINT
            and (now - _LAST_EMIT) < config.dedupe_seconds
        )
        _LAST_FINGERPRINT = report.fingerprint
        _LAST_EMIT = now
        _LAST_REPORT = report

        if not duplicate and not quiet:
            try:
                report.write(config)
            except Exception:
                pass
            if config.render_on_error:
                _write_console(report.render(), config)
    return report


def _write_console(text: str, config: TraceConfig) -> None:
    stream = sys.stdout if config.stdout else sys.stderr
    try:
        print(text, file=stream, flush=True)
    except Exception:
        pass


def last_report() -> FaultReport | None:
    return _LAST_REPORT


def reset_dedupe() -> None:
    global _LAST_FINGERPRINT, _LAST_EMIT
    _LAST_FINGERPRINT = None
    _LAST_EMIT = 0.0


__all__ = [
    "CallRecord",
    "FrameInfo",
    "FaultReport",
    "build_report",
    "emit",
    "last_report",
    "reset_dedupe",
    "summarize",
    "artifact_snapshot",
]
