"""Protocol checks for task mode routing; no processing algorithm is executed."""

import pytest

from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_process import (
    _single_process_mode,
    _validate_pipeline_plan,
    WorkerRunner,
)


@pytest.mark.parametrize(
    ("payload", "expected"),
    [({}, False), ({"single_process": False}, False), ({"single_process": True}, True)],
)
def test_single_process_mode_reads_json_boolean(payload, expected):
    assert _single_process_mode(payload) is expected


@pytest.mark.parametrize("value", ["true", "false", 1, None, []])
def test_single_process_mode_rejects_non_boolean_values(value):
    with pytest.raises(ValueError, match="JSON boolean"):
        _single_process_mode({"single_process": value})


def test_pipeline_plan_preserves_kotlin_order_after_validating_stage_membership():
    selections = {
        "alignment": "No Alignment",
        "denoising": "No Denoising",
        "super_resolution": "splattingSR",
        "hdr": "Weighted HDR",
    }
    requested = [
        {"category": "hdr", "algorithm": "Weighted HDR"},
        {"category": "super_resolution", "algorithm": "splattingSR"},
    ]
    assert _validate_pipeline_plan(requested, selections) == [
        ("hdr", "Weighted HDR"),
        ("super_resolution", "splattingSR"),
    ]


def test_worker_does_not_announce_ready_when_engine_initialization_fails(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    events = []
    runner = WorkerRunner()
    monkeypatch.setattr(worker, "send_ipc", events.append)

    def fail_engine():
        raise RuntimeError("configured backend could not initialize")

    monkeypatch.setattr(runner, "_initialize_engine", fail_engine)
    monkeypatch.setattr(runner, "_initialize_algorithms", lambda: None)

    runner.run_loop()

    assert runner.is_running is False
    assert not any(event["type"] == "ready" for event in events)
    startup_error = next(event for event in events if event["type"] == "error")
    assert startup_error["phase"] == "startup"
    assert "configured backend could not initialize" in startup_error["details"]


def test_worker_does_not_announce_ready_when_required_adapter_import_fails(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    events = []
    runner = WorkerRunner()
    monkeypatch.setattr(worker, "send_ipc", events.append)
    monkeypatch.setattr(runner, "_initialize_engine", lambda: None)

    def fail_algorithms():
        raise ImportError("required adapter is unavailable")

    monkeypatch.setattr(runner, "_initialize_algorithms", fail_algorithms)

    runner.run_loop()

    assert runner.is_running is False
    assert not any(event["type"] == "ready" for event in events)
    startup_error = next(event for event in events if event["type"] == "error")
    assert startup_error["phase"] == "startup"
    assert "required adapter is unavailable" in startup_error["details"]


def test_worker_announces_ready_only_after_required_initialization_succeeds(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    events = []
    runner = WorkerRunner()
    monkeypatch.setattr(worker, "send_ipc", events.append)
    monkeypatch.setattr(runner, "_initialize_engine", lambda: None)
    monkeypatch.setattr(runner, "_initialize_algorithms", lambda: None)
    runner.cmd_queue.put({"cmd": "shutdown"})

    runner.run_loop()

    ready = next(event for event in events if event["type"] == "ready")
    assert ready["protocol_version"] == 2
    assert ready["capabilities"] == ["stage_session_v1"]
    assert not any(event["type"] == "error" and event.get("phase") == "startup" for event in events)


@pytest.mark.parametrize(
    ("plan", "message"),
    [
        (None, "JSON array"),
        (["not-an-object"], "must be an object"),
        ([{"category": "alignment"}], "requires string"),
        ([{"category": "alignment", "algorithm": "OFB"}], "unselected stage"),
        ([], "missing selected stages"),
        (
            [
                {"category": "super_resolution", "algorithm": "splattingSR"},
                {"category": "super_resolution", "algorithm": "splattingSR"},
                {"category": "hdr", "algorithm": "Weighted HDR"},
            ],
            "multiple stages",
        ),
        (
            [
                {"category": "super_resolution", "algorithm": "No Super Resolution"},
                {"category": "hdr", "algorithm": "Weighted HDR"},
            ],
            "does not match selected",
        ),
    ],
)
def test_pipeline_plan_rejects_invalid_or_incomplete_stage_lists(plan, message):
    selections = {
        "alignment": "No Alignment",
        "denoising": "No Denoising",
        "super_resolution": "splattingSR",
        "hdr": "Weighted HDR",
    }
    with pytest.raises(ValueError, match=message):
        _validate_pipeline_plan(plan, selections)


def test_task_scoped_cancel_does_not_cancel_a_different_active_task():
    runner = WorkerRunner()
    runner.current_task_id = "current-task"

    runner.request_task_cancel("stale-task")
    runner.apply_pending_cancel("current-task")

    assert not runner.current_stop_event.is_set()
    assert runner.pending_cancel_task_id is None


def test_finish_pipeline_runs_cleanup_once_even_if_finish_is_repeated(monkeypatch):
    runner = WorkerRunner()
    runner.pipeline_session = {"task_id": "pipeline-1", "pipeline_id": "pipeline-1"}
    cleanup_calls = []
    events = []
    monkeypatch.setattr(runner, "_cleanup_after_pipeline", lambda: cleanup_calls.append("cleanup"))
    monkeypatch.setattr("pixel_refine_desktop.enhance_stack.core.logic.backend_worker_process.send_ipc", events.append)

    message = {"cmd": "finish_pipeline", "task_id": "pipeline-1", "pipeline_id": "pipeline-1"}
    runner.finish_pipeline(message)
    runner.finish_pipeline(message)

    assert cleanup_calls == ["cleanup"]
    assert [event["type"] for event in events] == ["pipeline_finished", "pipeline_finished"]
    assert runner.pipeline_session is None


def _stage_request(task_id, stage_index, plan, settings):
    return {
        "cmd": "execute_stage",
        "task_id": task_id,
        "pipeline_id": task_id,
        "stage_index": stage_index,
        "pipeline_plan": plan,
        "batch_id": 17,
        "db_path": "session.sqlite",
        "settings": settings,
        "single_process": True,
    }


def _stage_settings():
    import config

    return {
        config.KEY_CHECKBOX_ALIGN: False,
        config.KEY_CHECKBOX_SUPER_RES: True,
        config.KEY_SUPER_RESOLUTION: "splattingSR",
        config.KEY_CHECKBOX_HDR: True,
        config.KEY_HDR: "Weighted HDR",
        config.KEY_CHECKBOX_DENOISING: False,
        config.KEY_DENOISING: "No Denoising",
    }


def test_cancel_between_stages_marks_session_terminal_and_shutdown_cleans_once(monkeypatch):
    from pixel_refine_desktop.enhance_stack.core.algorithm.HDR import HDR
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution import SplatSR
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    calls = []
    events = []
    cleanup_calls = []
    monkeypatch.setattr(SplatSR, "running_splatting_sr", lambda **_: calls.append("sr") or "sr.tif")
    monkeypatch.setattr(HDR, "running_hdr_fusion", lambda **_: calls.append("hdr") or "hdr.tif")
    monkeypatch.setattr(worker, "send_ipc", events.append)
    runner = WorkerRunner()
    monkeypatch.setattr(runner, "_cleanup_after_pipeline", lambda: cleanup_calls.append("cleanup"))
    plan = [
        {"category": "super_resolution", "algorithm": "splattingSR"},
        {"category": "hdr", "algorithm": "Weighted HDR"},
    ]
    settings = _stage_settings()

    runner.execute_task(_stage_request("cancel-stage", 0, plan, settings), stage_only=True)
    runner.request_task_cancel("cancel-stage")
    runner.execute_task(_stage_request("cancel-stage", 1, plan, settings), stage_only=True)

    terminal = [event for event in events if event["type"] in ("finished", "cancelled", "error")]
    assert [event["type"] for event in terminal] == ["finished", "cancelled"]
    assert [event["stage_index"] for event in terminal] == [0, 1]
    assert runner.pipeline_session["failed"] is True
    assert calls == ["sr"]
    assert cleanup_calls == []

    runner.shutdown()

    assert runner.pipeline_session is None
    assert runner.is_running is False
    assert cleanup_calls == ["cleanup"]
    assert events[-1]["type"] == "pipeline_finished"


def test_stage_adapter_error_fails_session_and_legacy_execute_still_cleans(monkeypatch):
    import config
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution import SplatSR
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    events = []
    cleanup_calls = []
    monkeypatch.setattr(worker, "send_ipc", events.append)

    def fail_adapter(**_):
        raise RuntimeError("fixture adapter error")

    monkeypatch.setattr(SplatSR, "running_splatting_sr", fail_adapter)
    runner = WorkerRunner()
    monkeypatch.setattr(runner, "_cleanup_after_pipeline", lambda: cleanup_calls.append("cleanup"))
    plan = [{"category": "super_resolution", "algorithm": "splattingSR"}]
    settings = _stage_settings()
    settings[config.KEY_CHECKBOX_HDR] = False
    settings[config.KEY_HDR] = "No HDR"
    runner.execute_task(_stage_request("error-stage", 0, plan, settings), stage_only=True)

    assert events[-1]["type"] == "error"
    assert events[-1]["error"] == "fixture adapter error"
    assert events[-1]["stage_index"] == 0
    assert runner.pipeline_session["failed"] is True

    # A failed session must not dispatch the adapter again when retried.
    runner.execute_task(_stage_request("error-stage", 0, plan, settings), stage_only=True)
    assert events[-1]["type"] == "error"
    assert "already failed" in events[-1]["error"]
    runner.finish_pipeline({"task_id": "error-stage", "pipeline_id": "error-stage"})
    assert cleanup_calls == ["cleanup"]

    legacy = WorkerRunner()
    legacy_cleanup = []
    monkeypatch.setattr(legacy, "_cleanup_after_pipeline", lambda: legacy_cleanup.append("cleanup"))
    legacy_settings = {
        config.KEY_CHECKBOX_ALIGN: False,
        config.KEY_CHECKBOX_SUPER_RES: False,
        config.KEY_CHECKBOX_HDR: False,
        config.KEY_CHECKBOX_DENOISING: False,
    }
    legacy.execute_task({
        "cmd": "execute",
        "task_id": "legacy-task",
        "batch_id": 3,
        "settings": legacy_settings,
        "single_process": False,
    })
    assert events[-1]["type"] == "finished"
    assert events[-1]["task_id"] == "legacy-task"
    assert legacy_cleanup == ["cleanup"]


def test_stage_session_dispatches_each_kotlin_index_once_with_one_snapshot(monkeypatch):
    import config
    from pixel_refine_desktop.enhance_stack.core.algorithm import HDR
    from pixel_refine_desktop.enhance_stack.core.algorithm.denoising import MFDenoiser
    from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution import SplatSR
    from pixel_refine_desktop.enhance_stack.core.logic import backend_worker_process as worker

    calls = []
    events = []
    monkeypatch.setattr(
        SplatSR,
        "running_splatting_sr",
        lambda **kwargs: calls.append(("super_resolution", kwargs["batch_id"], kwargs["db_path"])) or "sr-output.tif",
    )
    monkeypatch.setattr(
        HDR,
        "running_hdr_fusion",
        lambda **kwargs: calls.append(("hdr", kwargs["batch_id"], kwargs["db_path"]))
        or {"ldr_path": "hdr-output.tif", "radiance_path": "hdr-radiance.tif"},
    )
    monkeypatch.setattr(worker, "send_ipc", events.append)

    settings = {
        config.KEY_CHECKBOX_ALIGN: False,
        config.KEY_CHECKBOX_SUPER_RES: True,
        config.KEY_SUPER_RESOLUTION: "splattingSR",
        config.KEY_CHECKBOX_HDR: True,
        config.KEY_HDR: "Weighted HDR",
        config.KEY_CHECKBOX_DENOISING: False,
        config.KEY_DENOISING: "No Denoising",
    }
    plan = [
        {"category": "super_resolution", "algorithm": "splattingSR"},
        {"category": "hdr", "algorithm": "Weighted HDR"},
    ]
    runner = WorkerRunner()
    cleanup_calls = []
    monkeypatch.setattr(runner, "_cleanup_after_pipeline", lambda: cleanup_calls.append("cleanup"))

    for stage_index in range(2):
        runner.execute_task(
            {
                "cmd": "execute_stage",
                "task_id": "pipeline-1",
                "pipeline_id": "pipeline-1",
                "stage_index": stage_index,
                "pipeline_plan": plan,
                "batch_id": 17,
                "db_path": "session.sqlite",
                "settings": settings,
                "single_process": True,
            },
            stage_only=True,
        )

    runner.finish_pipeline({"task_id": "pipeline-1", "pipeline_id": "pipeline-1"})

    assert calls == [
        ("super_resolution", 17, "session.sqlite"),
        ("hdr", 17, "session.sqlite"),
    ]
    terminals = [event for event in events if event["type"] in ("finished", "error", "cancelled")]
    assert [event["stage_index"] for event in terminals] == [0, 1]
    assert [event["output_paths"] for event in terminals] == [
        ["sr-output.tif"],
        ["hdr-output.tif", "hdr-radiance.tif"],
    ]
    assert cleanup_calls == ["cleanup"]

    staged_call_trace = list(calls)
    staged_outputs = [path for event in terminals for path in event["output_paths"]]
    calls.clear()
    full_plan_events = []
    monkeypatch.setattr(worker, "send_ipc", full_plan_events.append)
    full_plan_runner = WorkerRunner()
    full_plan_cleanup = []
    monkeypatch.setattr(
        full_plan_runner,
        "_cleanup_after_pipeline",
        lambda: full_plan_cleanup.append("cleanup"),
    )
    full_plan_runner.execute_task({
        "cmd": "execute",
        "task_id": "full-plan-reference",
        "batch_id": 17,
        "db_path": "session.sqlite",
        "settings": settings,
        "single_process": True,
        "pipeline_plan": plan,
    })
    full_plan_terminal = [event for event in full_plan_events if event["type"] == "finished"]

    assert calls == staged_call_trace
    assert len(full_plan_terminal) == 1
    assert full_plan_terminal[0]["output_paths"] == staged_outputs
    assert full_plan_cleanup == ["cleanup"]
