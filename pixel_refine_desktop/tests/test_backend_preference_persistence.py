"""Regression guards for the persisted hardware-acceleration preference.

A ``vulkaninfo --summary`` run that times out used to collapse the option list to
CPU, and the settings page then rewrote the saved GPU preference to CPU - the
"my GPU selection randomly falls back to CPU and I have to pick it again"
report.  Measured on the affected machine, enumeration takes 9.3-12.9 s idle
against a 15 s budget, so a busy machine fails it regularly.

These tests lock the two halves of the fix:

* an incomplete scan must never overwrite the saved preference, and
* enumeration is retried before it reports "no devices".
"""

import json
import os
import subprocess
import textwrap
from types import SimpleNamespace

import pytest

CPU_OPTION = {
    "key": "cpu",
    "text": "CPU (Universal)",
    "device_type": "cpu",
    "backend": "cpu",
    "device_id": -1,
    "vendor": "cpu",
    "raw_name": "CPU (Universal)",
    "fallback_chain": ["cpu"],
}

NVIDIA_OPTION = {
    "key": "10de:1d10:native|dgpu",
    "text": "NVIDIA GeForce MX150 (Dedicated GPU)",
    "device_type": "dgpu",
    "backend": "vulkan",
    "device_id": 2,
    "vulkan_device_id": 2,
    "cuda_device_id": 0,
    "vendor": "nvidia",
    "raw_name": "NVIDIA GeForce MX150",
    "fallback_chain": ["cuda", "vulkan", "opengl", "cpu"],
    "device_selector": {
        "vendor": "nvidia",
        "name": "nvidia geforce mx150",
        "native": True,
        "fingerprint": "10de:1d10:native",
    },
}

# What a successful launch persists after the user picks the MX150.
SAVED_NVIDIA_STATE = {
    "device_backend": NVIDIA_OPTION["text"],
    "device_backend_key": NVIDIA_OPTION["key"],
    "device_backend_arch": "vulkan",
    "device_backend_id": 2,
    "device_fallback_chain": ["cuda", "vulkan", "opengl", "cpu"],
    "device_vendor": "nvidia",
    "device_selector": NVIDIA_OPTION["device_selector"],
    "auto_fallback": False,
}

SAVED_CPU_STATE = {
    "device_backend": CPU_OPTION["text"],
    "device_backend_key": "cpu",
    "device_backend_arch": "cpu",
    "device_backend_id": -1,
    "device_vendor": "cpu",
    "device_selector": {"vendor": "cpu", "name": "cpu universal"},
    "auto_fallback": True,
}


@pytest.fixture(scope="session")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture(autouse=True)
def _isolated_environment():
    """``_apply_selected_backend_to_process`` mutates os.environ; undo that."""
    snapshot = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(snapshot)


@pytest.fixture(autouse=True)
def _clean_device_cache():
    """The enumeration cache is process-global; keep tests independent."""
    from taichi_vision import device_selection

    device_selection.invalidate_vulkan_device_cache()
    yield
    device_selection.invalidate_vulkan_device_cache()


def _bound_store(tmp_path, state):
    from resources.GenericUILibrary.store import DataStore

    path = tmp_path / "app_setting.json"
    path.write_text(json.dumps(state, indent=4), encoding="utf-8")
    store = DataStore()
    store.bind_to_file(str(path))
    return store


def _make_page(store, options):
    """Stand-in for PerformanceSettingsPage owning the real backend methods."""
    from PySide6.QtWidgets import QComboBox

    from pixel_refine_desktop.ui.views.settings.General.GeneralSetting import (
        GeneralSettingsPage,
    )
    from pixel_refine_desktop.ui.views.settings.Perfomance.PerformancePage import (
        PerformanceSettingsPage,
    )

    class FakePage:
        _get_selected_backend_option = GeneralSettingsPage._get_selected_backend_option
        _apply_selected_backend_to_process = (
            GeneralSettingsPage._apply_selected_backend_to_process
        )
        _get_backend_test_options = GeneralSettingsPage._get_backend_test_options
        _migrate_saved_backend_option = (
            GeneralSettingsPage._migrate_saved_backend_option
        )
        _prepare_backend_options = PerformanceSettingsPage._prepare_backend_options
        _saved_backend_identity = PerformanceSettingsPage._saved_backend_identity
        _saved_backend_matches = staticmethod(
            PerformanceSettingsPage._saved_backend_matches
        )
        _detect_unavailable_saved_backend = (
            PerformanceSettingsPage._detect_unavailable_saved_backend
        )
        _restore_saved_backend_selection = (
            PerformanceSettingsPage._restore_saved_backend_selection
        )
        _hardware_scan_failure_summary = (
            PerformanceSettingsPage._hardware_scan_failure_summary
        )
        _log_unavailable_saved_backend = staticmethod(lambda _placeholder: None)
        refresh_backend_availability = (
            PerformanceSettingsPage.refresh_backend_availability
        )
        update_device_dropdown_style = (
            GeneralSettingsPage.update_device_dropdown_style
        )
        _flag_unavailable_backend_option = (
            PerformanceSettingsPage._flag_unavailable_backend_option
        )
        _update_retry_button_visibility = (
            PerformanceSettingsPage._update_retry_button_visibility
        )

        def __init__(self, store_, option_list):
            self.store = store_
            self.device_group = SimpleNamespace(input=QComboBox())
            self._hardware_scan_failures = []
            self._unavailable_saved_backend = None
            self._scan_hardware_backend_options = lambda: list(option_list)

        def set_scan(self, option_list):
            """Simulate the GPU becoming enumerable again."""
            self._scan_hardware_backend_options = lambda: list(option_list)

        def fill_combo(self, option_list):
            for option in option_list:
                self.device_group.input.addItem(option["text"], option)

    return FakePage(store, options)


def test_incomplete_scan_preserves_the_saved_gpu_preference(qapp, tmp_path):
    """A CPU-only scan must not rewrite the persisted GPU choice."""
    store = _bound_store(tmp_path, SAVED_NVIDIA_STATE)
    # vulkaninfo timed out, so only the CPU entry could be enumerated.
    page = _make_page(store, [CPU_OPTION])

    options = page._prepare_backend_options()

    placeholder = options[-1]
    assert placeholder["not_detected"] is True
    assert placeholder["key"] == SAVED_NVIDIA_STATE["device_backend_key"]

    page.fill_combo(options)
    page._restore_saved_backend_selection(options)
    assert page._get_selected_backend_option()["not_detected"] is True

    # Both paths that used to overwrite the preference must now be inert.
    page._apply_selected_backend_to_process()
    store.save_to_file()

    persisted = json.loads(
        (tmp_path / "app_setting.json").read_text(encoding="utf-8")
    )
    for key in (
        "device_backend",
        "device_backend_key",
        "device_backend_arch",
        "device_backend_id",
        "device_selector",
    ):
        assert persisted[key] == SAVED_NVIDIA_STATE[key], f"{key} was overwritten"


def test_detected_gpu_is_still_applied_normally(qapp, tmp_path):
    """The non-destructive path must not stop a real GPU from being applied."""
    store = _bound_store(tmp_path, SAVED_NVIDIA_STATE)
    page = _make_page(store, [CPU_OPTION, NVIDIA_OPTION])

    options = page._prepare_backend_options()

    assert not any(option.get("not_detected") for option in options)
    page.fill_combo(options)
    page._restore_saved_backend_selection(options)
    assert page._get_selected_backend_option()["key"] == NVIDIA_OPTION["key"]

    page._apply_selected_backend_to_process()

    assert store.get("device_backend_key") == NVIDIA_OPTION["key"]
    assert store.get("device_selector") == NVIDIA_OPTION["device_selector"]
    assert store.get("device_backend_arch") == "vulkan"


def test_cpu_preference_is_never_reported_as_missing(qapp, tmp_path):
    """CPU is always available, so it must not produce a placeholder entry."""
    store = _bound_store(tmp_path, SAVED_CPU_STATE)
    page = _make_page(store, [CPU_OPTION])

    assert page._detect_unavailable_saved_backend([CPU_OPTION]) is None

    options = page._prepare_backend_options()

    assert options == [CPU_OPTION]
    assert store.get("device_backend_key") == "cpu"


def test_not_detected_entry_is_not_offered_for_hardware_testing(qapp, tmp_path):
    """The placeholder preserves a preference; it is not a testable backend."""
    store = _bound_store(tmp_path, SAVED_NVIDIA_STATE)
    page = _make_page(store, [CPU_OPTION])

    options = page._prepare_backend_options()
    page.fill_combo(options)

    assert [option["key"] for option in page._get_backend_test_options()] == ["cpu"]


VULKANINFO_SUMMARY = textwrap.dedent(
    """\
    ==========
    VULKANINFO
    ==========

    Devices:
    ========
    GPU0:
        deviceName         = NVIDIA GeForce MX150
        deviceType         = PHYSICAL_DEVICE_TYPE_DISCRETE_GPU
        vendorID           = 0x10de
        deviceID           = 0x1d10
        driverID           = DRIVER_ID_NVIDIA_PROPRIETARY
    """
)


def _fake_completed(args):
    return subprocess.CompletedProcess(args, 0, stdout=VULKANINFO_SUMMARY, stderr="")


def test_vulkan_scan_retries_once_after_a_timeout(monkeypatch):
    """A timed-out enumeration must not be reported as "no GPU present"."""
    from taichi_vision import device_selection

    attempts = []

    def fake_run(args, **kwargs):
        attempts.append(args)
        if len(attempts) == 1:
            raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))
        return _fake_completed(args)

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)
    monkeypatch.setattr(device_selection.time, "sleep", lambda _seconds: None)

    records = device_selection.scan_vulkan_device_records()

    assert len(attempts) == 2
    assert records[0]["name"] == "NVIDIA GeForce MX150"
    assert records[0]["vendor"] == "nvidia"


def test_vulkan_scan_gives_up_after_the_last_attempt(monkeypatch):
    """A device that never enumerates still raises instead of returning []."""
    from taichi_vision import device_selection

    attempts = []

    def fake_run(args, **kwargs):
        attempts.append(args)
        raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)
    monkeypatch.setattr(device_selection.time, "sleep", lambda _seconds: None)

    with pytest.raises(subprocess.TimeoutExpired):
        device_selection.scan_vulkan_device_records()

    assert len(attempts) == 2


def test_vulkan_scan_does_not_retry_a_missing_binary(monkeypatch):
    """Without vulkaninfo there is nothing to wait for; fail immediately."""
    from taichi_vision import device_selection

    attempts = []

    def fake_run(args, **kwargs):
        attempts.append(args)
        raise FileNotFoundError("vulkaninfo")

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)
    monkeypatch.setattr(device_selection.time, "sleep", lambda _seconds: None)

    with pytest.raises(FileNotFoundError):
        device_selection.scan_vulkan_device_records()

    assert len(attempts) == 1


def test_scan_reuses_one_enumeration_per_launch(monkeypatch):
    """The several consumers in one launch must share one vulkaninfo run.

    Every independent run is another chance to time out, and engine.py warns
    that the bridge and the runtime must use one enumeration source.
    """
    from taichi_vision import device_selection

    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return _fake_completed(args)

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)

    first = device_selection.scan_vulkan_device_records()
    second = device_selection.scan_vulkan_device_records()

    assert len(calls) == 1
    assert second == first

    # A caller must not be able to corrupt the shared enumeration.
    second[0]["name"] = "mutated"
    assert device_selection.scan_vulkan_device_records()[0]["name"] != "mutated"


def test_scan_failures_are_never_cached(monkeypatch):
    """A failed probe must not be remembered as "there is no GPU"."""
    from taichi_vision import device_selection

    calls = []
    state = {"fail": True}

    def fake_run(args, **kwargs):
        calls.append(args)
        if state["fail"]:
            raise subprocess.TimeoutExpired(args, kwargs.get("timeout"))
        return _fake_completed(args)

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)
    monkeypatch.setattr(device_selection.time, "sleep", lambda _seconds: None)

    with pytest.raises(subprocess.TimeoutExpired):
        device_selection.scan_vulkan_device_records(attempts=1)
    assert len(calls) == 1

    state["fail"] = False
    records = device_selection.scan_vulkan_device_records()

    assert records[0]["name"] == "NVIDIA GeForce MX150"
    assert len(calls) == 2, "the failure must not have been served from cache"


def test_fresh_scan_bypasses_and_refreshes_the_cache(monkeypatch):
    """Recovery paths must see the current driver state, not the cache."""
    from taichi_vision import device_selection

    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return _fake_completed(args)

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)

    device_selection.scan_vulkan_device_records()
    device_selection.scan_vulkan_device_records(fresh=True)
    assert len(calls) == 2

    # The fresh result replaced the cached one.
    device_selection.scan_vulkan_device_records()
    assert len(calls) == 2


def test_enumeration_is_repeated_once_the_cache_expires(monkeypatch):
    """A short TTL keeps a partial enumeration from being pinned all session."""
    from taichi_vision import device_selection

    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return _fake_completed(args)

    monkeypatch.setattr(device_selection.subprocess, "run", fake_run)
    monkeypatch.setenv("PIXEL_REFINE_AOT_DEVICE_CACHE_TTL_S", "0")

    device_selection.scan_vulkan_device_records()
    device_selection.scan_vulkan_device_records()

    assert len(calls) == 2


def test_refresh_restores_the_gpu_once_it_is_detected_again(qapp, tmp_path):
    """The retry path must turn the placeholder back into a usable selection."""
    store = _bound_store(tmp_path, SAVED_NVIDIA_STATE)
    page = _make_page(store, [CPU_OPTION])

    options = page._prepare_backend_options()
    page.fill_combo(options)
    page._restore_saved_backend_selection(options)
    assert page._unavailable_saved_backend is not None

    # The device is enumerable again.
    page.set_scan([CPU_OPTION, NVIDIA_OPTION])
    page.refresh_backend_availability()

    assert page._unavailable_saved_backend is None
    assert page._get_selected_backend_option()["key"] == NVIDIA_OPTION["key"]
    assert store.get("device_backend_key") == NVIDIA_OPTION["key"]
    assert store.get("device_backend_arch") == "vulkan"
