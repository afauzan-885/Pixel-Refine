"""Tests for the background GPU availability watch and recovery.

The watch exists because a startup enumeration can fail transiently while the
machine is busy (see ``test_backend_preference_persistence.py`` for the measured
timings).  These tests pin the recovery contract without a GPU: the probe is
injected and the worker manager is faked.

No real ``vulkaninfo`` is spawned and no settings file is touched.
"""

import os
import time

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def _device_record():
    return {
        "ordinal": 2,
        "name": "NVIDIA GeForce MX150",
        "vendor": "nvidia",
        "vendor_id": 0x10DE,
        "device_id": 0x1D10,
        "native": True,
        "translation": False,
    }


def _selector():
    from taichi_vision.device_selection import make_device_selector

    return make_device_selector(_device_record())


class _Probe:
    """Raises for the first ``failures`` calls, then reports the device."""

    def __init__(self, failures):
        self.failures = failures
        self.calls = 0

    def __call__(self):
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("vulkaninfo timed out")
        return [_device_record()]


@pytest.fixture
def bus():
    """A per-test signal object.

    The tests never attach to the process-wide ``gpu_watch.signals()`` object:
    leaving connections on it outlived the test module and faulted during
    interpreter teardown.
    """
    from pixel_refine_desktop.app_core import gpu_watch

    return gpu_watch.GpuAvailabilitySignals()


def _capture(bus, captured):
    bus.device_available.connect(
        lambda payload: captured.setdefault("device", payload),
        Qt.ConnectionType.DirectConnection,
    )
    bus.watch_finished.connect(
        lambda result: captured.setdefault("finished", result),
        Qt.ConnectionType.DirectConnection,
    )
    bus.backend_switch_finished.connect(
        lambda ok, config: captured.setdefault("switched", (ok, config)),
        Qt.ConnectionType.DirectConnection,
    )


def _wait_for(captured, key, timeout=10.0):
    deadline = time.time() + timeout
    while key not in captured and time.time() < deadline:
        time.sleep(0.02)
    return captured.get(key)


def test_watch_finds_the_saved_gpu_after_transient_failures(qapp, bus):
    """A timed-out probe is not evidence of absence; keep watching."""
    from pixel_refine_desktop.app_core import gpu_watch

    probe = _Probe(failures=2)
    worker = gpu_watch.GpuWatchWorker(
        _selector(), delays=(0.0, 0.0, 0.0), probe=probe, signals_obj=bus
    )
    captured = {}
    _capture(bus, captured)

    worker.run()

    assert probe.calls == 3
    assert captured["device"]["name"] == "NVIDIA GeForce MX150"
    assert captured["finished"]["found"] is True
    assert captured["finished"]["attempts"] == 3


def test_watch_stops_after_the_backoff_schedule(qapp, bus):
    """The watch is bounded: it must not probe forever."""
    from pixel_refine_desktop.app_core import gpu_watch

    probe = _Probe(failures=99)
    worker = gpu_watch.GpuWatchWorker(
        _selector(), delays=(0.0, 0.0), probe=probe, signals_obj=bus
    )
    captured = {}
    _capture(bus, captured)

    worker.run()

    assert probe.calls == 2
    assert captured.get("device") is None
    assert captured["finished"]["found"] is False
    assert captured["finished"]["reason"] == "exhausted"
    assert "timed out" in captured["finished"]["last_error"]


def test_watch_honours_a_stop_request(qapp, bus):
    """Shutdown must not leave a probing thread behind."""
    from pixel_refine_desktop.app_core import gpu_watch

    probe = _Probe(failures=99)
    worker = gpu_watch.GpuWatchWorker(
        _selector(), delays=(0.0, 0.0), probe=probe, signals_obj=bus
    )
    worker.request_stop()
    captured = {}
    _capture(bus, captured)

    worker.run()

    assert probe.calls == 0
    assert captured["finished"]["reason"] == "stopped"


def test_watch_is_not_armed_for_a_cpu_preference(qapp, monkeypatch):
    """A CPU user must not get a background thread probing the driver."""
    from pixel_refine_desktop.app_core import gpu_watch
    from pixel_refine_desktop.ui.views.settings.General import general_store

    class FakeStore:
        def __init__(self, data):
            self._data = data

        def get(self, key, default=None):
            return self._data.get(key, default)

    cpu_state = {
        "device_backend_arch": "cpu",
        "device_vendor": "cpu",
        "device_selector": {"vendor": "cpu", "name": "cpu universal"},
    }
    monkeypatch.setattr(
        general_store, "get_general_store", lambda: FakeStore(cpu_state)
    )

    assert gpu_watch.saved_gpu_selector() is None
    assert gpu_watch.start_gpu_watch() is False

    gpu_state = dict(cpu_state)
    gpu_state.update(
        {
            "device_backend_arch": "vulkan",
            "device_vendor": "nvidia",
            "device_selector": _selector(),
        }
    )
    monkeypatch.setattr(
        general_store, "get_general_store", lambda: FakeStore(gpu_state)
    )

    assert gpu_watch.saved_gpu_selector() == _selector()


class _FakeWorkerManager:
    def __init__(self, task_active):
        self._task_active = task_active
        self.switches = []

    def is_task_active(self):
        return self._task_active

    def switch_backend(self, config, force_restart=False):
        self.switches.append((dict(config), bool(force_restart)))
        return True


def _patch_manager(monkeypatch, manager):
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
        BackendWorkerManager,
    )

    monkeypatch.setattr(
        BackendWorkerManager, "instance", classmethod(lambda cls: manager)
    )


def test_worker_switch_is_deferred_while_a_task_is_running(qapp, bus, monkeypatch):
    """Switching terminates the worker, so a running batch must never be killed."""
    from pixel_refine_desktop.app_core import gpu_watch

    manager = _FakeWorkerManager(task_active=True)
    _patch_manager(monkeypatch, manager)
    captured = {}
    _capture(bus, captured)

    gpu_watch.switch_worker_backend_when_idle(
        {"arch": "vulkan", "device_id": 2},
        poll_s=0.02,
        timeout_s=0.15,
        signals_obj=bus,
    )
    result = _wait_for(captured, "switched")

    assert manager.switches == []
    assert result is not None and result[0] is False


def test_worker_switch_runs_once_the_worker_is_idle(qapp, bus, monkeypatch):
    from pixel_refine_desktop.app_core import gpu_watch

    manager = _FakeWorkerManager(task_active=False)
    _patch_manager(monkeypatch, manager)
    captured = {}
    _capture(bus, captured)

    gpu_watch.switch_worker_backend_when_idle(
        {"arch": "vulkan", "device_id": 2},
        poll_s=0.02,
        timeout_s=5.0,
        signals_obj=bus,
    )
    result = _wait_for(captured, "switched")

    assert result is not None and result[0] is True
    assert manager.switches == [({"arch": "vulkan", "device_id": 2}, True)]
