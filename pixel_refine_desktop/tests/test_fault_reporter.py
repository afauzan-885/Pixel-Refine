"""Contract tests for the compact, console-only taichi fault reporter."""

from dataclasses import replace

import pytest

import taichi.native_bridge as native_bridge
from fault_trace._config import current_config
from fault_trace._hints import iter_hints
from fault_trace._report import FrameInfo, build_report, emit, reset_dedupe


def _report(message="native graph launch failed for hamilton: stale handle"):
    return build_report(
        RuntimeError(message),
        calls=[],
        frames=[FrameInfo("E:/project/provider.py", 365, "finalize")],
        artifact_candidates=[],
        elapsed_ms=1.0,
    )


def test_render_is_compact_and_actionable():
    rendered = _report().render()
    lines = [line for line in rendered.splitlines() if line.strip()]
    assert len(lines) <= 8
    assert "[TAICHI FAULT]" in rendered
    assert "Error    : RuntimeError:" in rendered
    assert "Location : provider.py:365 (finalize)" in rendered
    assert "Backend  :" in rendered
    assert "LAPORAN JSON" not in rendered


def test_render_truncates_very_long_messages():
    rendered = _report("x" * 500).render()
    assert len(rendered.splitlines()) <= 8
    assert "..." in rendered


def test_hint_titles_and_checks_are_english_ascii():
    for hint in iter_hints():
        text = " ".join((hint.title, *hint.causes, *hint.checks))
        assert text.isascii(), hint.id
        assert "gagal" not in text.lower(), hint.id
        assert "tidak" not in text.lower(), hint.id


def test_emit_writes_only_compact_console_and_no_json(tmp_path, capsys):
    reset_dedupe()
    config = replace(current_config(), report_dir=tmp_path, dedupe_seconds=60.0)

    first = _report()
    emit(first, RuntimeError("same failure"), config=config)

    stderr = capsys.readouterr().err
    assert "[TAICHI FAULT]" in stderr
    assert len([line for line in stderr.splitlines() if line.strip()]) <= 8
    assert list(tmp_path.iterdir()) == []


def test_repeated_fault_is_suppressed_not_flooded(capsys):
    reset_dedupe()
    config = replace(current_config(), report_dir=None, dedupe_seconds=60.0)

    for _ in range(5):
        emit(_report("same failure"), RuntimeError("same failure"), config=config)
    stderr = capsys.readouterr().err
    assert stderr.count("[TAICHI FAULT]") == 1

    emit(_report("different failure"), RuntimeError("different failure"), config=config)
    stderr = capsys.readouterr().err
    assert "repeated error suppressed" in stderr


def _unwrapped_run_graph():
    """Bypass the fault tracer so a synthetic launch cannot initialise a GPU."""
    return getattr(native_bridge.run_graph, "__wrapped__", native_bridge.run_graph)


def test_run_graph_raises_immediately_on_native_failure(monkeypatch):
    class _FakeLib:
        def clear_last_engine_error(self, handle):
            return None

        def run_aot_graph(self, *args):
            return None

        def get_last_engine_error(self, handle):
            return b"resource handle is stale"

    monkeypatch.setattr(native_bridge, "library", lambda: _FakeLib())

    with pytest.raises(RuntimeError, match="resource handle is stale"):
        _unwrapped_run_graph()(1, 2, "hamilton_demosaic", [])


def test_run_graph_is_silent_on_success(monkeypatch):
    class _FakeLib:
        def clear_last_engine_error(self, handle):
            return None

        def run_aot_graph(self, *args):
            return None

        def get_last_engine_error(self, handle):
            return b""

    monkeypatch.setattr(native_bridge, "library", lambda: _FakeLib())
    _unwrapped_run_graph()(1, 2, "ok_graph", [])
