import json
import subprocess
import sys
import time
from types import SimpleNamespace

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QHeaderView

import config
from pixel_refine_desktop.enhance_stack.components.bulk_page.services.bulk_eta import BatchEtaEstimator
from pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller import (
    BatchProcessDialog, ProcessingThread,
)


def test_eta_includes_save_and_export_and_ignores_stage_percentages():
    clock = [0.0]
    eta = BatchEtaEstimator(4, clock=lambda: clock[0])
    eta.begin()
    clock[0] = 8
    assert eta.remaining() is None
    clock[0] = 12  # processing + saving + export
    eta.finish(True)
    assert eta.remaining() == 36
    eta.begin()
    clock[0] = 17
    assert eta.remaining() == 31
    clock[0] = 32  # overrun cannot claim that the active job has finished
    assert eta.remaining() == 25
    eta.finish(True)
    assert eta.remaining() == 28  # smoothed average = 14 seconds


def test_eta_reused_outputs_and_failures_do_not_lower_compute_estimate():
    clock = [0.0]
    eta = BatchEtaEstimator(4, clock=lambda: clock[0])
    eta.begin()
    clock[0] = 10
    eta.finish(True)
    eta.begin(reused=True)
    clock[0] = 10.1
    eta.finish(True)
    assert eta.remaining() == 20
    eta.begin()
    clock[0] = 10.2
    eta.finish(False)
    assert eta.remaining() == 10
    eta.begin()
    clock[0] = 20.2
    eta.finish(True)
    assert eta.remaining() == 0


@pytest.fixture
def qapp():
    return QApplication.instance() or QApplication([])


def make_job(tmp_path):
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"7": {
        config.KEY_ALIGNMENT_ALGO: "Block Flow", config.KEY_CHECKBOX_ALIGN: True,
        config.KEY_DENOISING_ALGO: "Similarity", config.KEY_CHECKBOX_DENOISING: True,
    }}))
    layout = SimpleNamespace(json_path=str(state), database_manager=SimpleNamespace(db_path="session.sqlite"))
    return ProcessingThread([], layout, str(tmp_path))


def test_bulk_dispatches_snapshot_to_worker_and_preserves_returned_paths(tmp_path, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import BackendWorkerManager
    payloads, progress = [], []

    def dispatch(payload, progress_cb, stop_requested_cb):
        payloads.append(payload)
        assert not stop_requested_cb()
        progress_cb(96, "Menyimpan gambar...||Saving result")
        return {"success": True, "output_paths": ["fallback_ref_ldr.tif", "fallback_ref_radiance.tif"]}

    monkeypatch.setattr(BackendWorkerManager, "instance", lambda: SimpleNamespace(dispatch_task=dispatch))
    job = make_job(tmp_path)
    paths = job._process_batch(SimpleNamespace(), 7, lambda *args: progress.append(args))
    assert paths == ["fallback_ref_ldr.tif", "fallback_ref_radiance.tif"]
    assert payloads[0]["db_path"] == "session.sqlite"
    assert payloads[0]["settings"]["denoising"] == "Similarity"
    assert payloads[0]["settings"]["alignment"] == "Block Flow"
    assert progress[-1] == (96, "Menyimpan gambar...")


def test_worker_failure_and_cancellation_are_not_successful_exports(tmp_path, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import BackendWorkerManager
    worker = SimpleNamespace(dispatch_task=lambda *args, **kwargs: {"success": False, "error": "Save failed"})
    monkeypatch.setattr(BackendWorkerManager, "instance", lambda: worker)
    job = make_job(tmp_path)
    with pytest.raises(RuntimeError, match="Save failed"):
        job._process_batch(SimpleNamespace(), 7, lambda *args: None)
    worker.dispatch_task = lambda *args, **kwargs: {"type": "cancelled", "success": True}
    assert job._process_batch(SimpleNamespace(), 7, lambda *args: None) == []
    assert job._is_running  # Per-batch cancellation must not discard later queue entries.


def test_active_batch_cancel_holds_queue_slot_until_worker_returns(qapp, tmp_path, monkeypatch):
    from threading import Event

    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import (
        BackendWorkerManager,
    )
    import pixel_refine_desktop.enhance_stack.components.bulk_page.controllers.bulk_process_controller as controller

    panels = [
        SimpleNamespace(batch_id=batch_id, name=f"Batch {batch_id}")
        for batch_id in (7, 8)
    ]
    layout = SimpleNamespace(database_manager=None)
    thread = ProcessingThread([(panels[0], 0), (panels[1], 1)], layout, str(tmp_path))
    entered_worker = Event()
    release_worker = Event()
    started_batches = []
    terminal_rows = []

    monkeypatch.setattr(controller, "find_existing_outputs", lambda *args: [])
    monkeypatch.setattr(
        BackendWorkerManager,
        "instance",
        lambda: SimpleNamespace(stop_current_task=lambda: None),
    )
    thread._result_identity = lambda panel, batch_id: ([], [])

    def process_batch(panel, batch_id, progress_callback):
        started_batches.append(batch_id)
        entered_worker.set()
        release_worker.wait(5)
        return []

    thread._process_batch = process_batch
    thread.batch_finished.connect(lambda *args: terminal_rows.append(args))
    thread.start()
    try:
        assert entered_worker.wait(3)
        thread.cancel_batch(7)
        thread.cancel_batch(8)
        time.sleep(0.05)
        assert started_batches == [7]
    finally:
        release_worker.set()

    assert thread.wait(5000)
    qapp.processEvents()
    assert started_batches == [7]
    assert terminal_rows == [
        (0, False, "Cancelled during processing"),
        (1, False, "Cancelled before processing"),
    ]


def test_qt_heartbeat_continues_while_child_holds_its_gil(qapp, tmp_path, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import BackendWorkerManager

    # Mimic an uncooperative native image writer holding the child interpreter's GIL.
    code = "import ctypes; ctypes.PyDLL('kernel32').Sleep(650)" if sys.platform == "win32" else "import time; time.sleep(0.65)"

    def dispatch(*args, **kwargs):
        subprocess.run([sys.executable, "-c", code], check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        return {"success": True, "output_paths": []}

    monkeypatch.setattr(BackendWorkerManager, "instance", lambda: SimpleNamespace(dispatch_task=dispatch))
    job = make_job(tmp_path)
    job.run = lambda: job._process_batch(SimpleNamespace(), 7, lambda *args: None)
    beats = []
    timer = QTimer()
    timer.setInterval(20)
    timer.timeout.connect(lambda: beats.append(time.monotonic()))
    timer.start()
    start = time.monotonic()
    job.start()
    while job.isRunning() and time.monotonic() - start < 5:
        qapp.processEvents()
        time.sleep(0.003)
    timer.stop()
    assert job.wait(1000)
    assert len(beats) >= 10
    assert max(b - a for a, b in zip(beats, beats[1:])) < 0.3


def test_close_requests_cancel_without_waiting_for_worker():
    calls = []
    dialog = SimpleNamespace(
        processing_thread=SimpleNamespace(isRunning=lambda: True, stop=lambda: calls.append("stop")),
        action_button=SimpleNamespace(setEnabled=lambda enabled: calls.append(enabled)),
        progress_status_tag=SimpleNamespace(setText=lambda text: calls.append(text)),
    )
    event = SimpleNamespace(ignore=lambda: calls.append("ignore"))
    BatchProcessDialog.closeEvent(dialog, event)
    assert dialog._close_after_processing
    assert calls == ["stop", False, "Cancelling...", "ignore"]


def test_batch_dialog_geometry_survives_long_text_and_batch_transitions(qapp, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    panels = [SimpleNamespace(batch_id=i, name=f"Batch {i}") for i in (1, 2)]
    dialog = BatchProcessDialog(panels, SimpleNamespace(database_manager=None))
    assert dialog.table_widget.columnCount() == 5
    assert dialog.table_widget.item(0, 2).text().startswith("⏳")
    assert dialog.table_widget.cellWidget(0, 4).toolTip()
    dialog.show()
    qapp.processEvents()
    dialog._is_processing = True
    dialog.processed_count = 0
    dialog.panels_to_process_with_rows = [(panel, i) for i, panel in enumerate(panels)]
    dialog._eta = BatchEtaEstimator(2)

    def geometry():
        table = dialog.table_widget
        return (dialog.size(), table.geometry(), dialog.progress_container.geometry(),
                tuple(table.rowHeight(i) for i in range(2)))

    before = geometry()
    long_text = "Long save/error message " * 150
    try:
        dialog._on_batch_started(0, False)
        for text in ("RAW Native 1/7", "Menyimpan gambar...", long_text):
            dialog.on_progress_update_from_thread(0, "Processing", text, 96, 1, 2)
            qapp.processEvents()
            assert geometry() == before
        dialog.on_batch_finished(0, True, "Success: Saved")
        dialog._on_batch_started(1, False)
        dialog.on_progress_update_from_thread(1, "Processing", long_text, 10, 2, 2)
        qapp.processEvents()
        assert geometry() == before
        assert dialog.table_widget.item(1, 3).toolTip() == long_text
        assert dialog.table_widget.cellWidget(1, 3) is None
        assert dialog.table_widget.horizontalHeader().sectionResizeMode(2) == QHeaderView.ResizeToContents
        assert dialog.progress_detail_label.toolTip().endswith(f"({long_text})")
    finally:
        dialog.close()


@pytest.mark.parametrize("enabled", [False, True])
def test_shared_worker_recovery_respects_auto_fallback(enabled, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import algorithm_processor as processor
    from pixel_refine_desktop.ui.views.settings.General import general_store
    monkeypatch.setattr(general_store, "get_general_store", lambda: {"auto_fallback": enabled})
    monkeypatch.setattr(processor, "_fallback_backend_configs", lambda worker: [{"arch": "vulkan"}])
    attempts = []
    failure = {"success": False, "error": "AOT graph unavailable for CUDA"}

    def dispatch(*args, **kwargs):
        attempts.append("dispatch")
        return failure if len(attempts) == 1 else {"success": True, "output_paths": ["result.dng"]}

    worker = SimpleNamespace(
        dispatch_task=dispatch, get_current_backend_config=lambda: {"arch": "cuda"},
        switch_backend=lambda *args, **kwargs: True,
    )
    result = processor.dispatch_worker_task(worker, {}, lambda *args: None, lambda: False)
    assert len(attempts) == (2 if enabled else 1)
    assert result == ({"success": True, "output_paths": ["result.dng"]} if enabled else failure)


@pytest.mark.parametrize("category,method,result", [
    ("denoising", "FusionNet", "reference_fusionet.dng"),
    ("hdr", "Weighted HDR", {"ldr_path": "fallback_ldr.tif", "radiance_path": "fallback_radiance.tif"}),
])
def test_worker_ipc_returns_declared_outputs(category, method, result, monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import MFDenoiser
    from pixel_refine_desktop.enhance_stack.core.algorithm import HDR
    from taichi_vision import taichi_aot

    monkeypatch.setattr(taichi_aot, "get_engine", lambda: None)
    monkeypatch.setattr(MFDenoiser, "running_mf_denoiser", lambda **kwargs: result)
    monkeypatch.setattr(HDR, "running_hdr_fusion", lambda **kwargs: result)
    events = []
    monkeypatch.setattr(worker, "send_ipc", events.append)
    settings = {
        config.KEY_CHECKBOX_ALIGN: False,
        config.KEY_CHECKBOX_DENOISING: category == "denoising",
        config.KEY_CHECKBOX_HDR: category == "hdr",
        category: method,
    }
    worker.WorkerRunner().execute_task({"task_id": "test", "batch_id": 7, "settings": settings})
    terminal = [event for event in events if event["type"] in ("finished", "error")]
    assert len(terminal) == 1
    assert terminal[0]["type"] == "finished", terminal
    assert terminal[0]["output_paths"] == (
        [result] if isinstance(result, str) else [result["ldr_path"], result["radiance_path"]]
    )
