"""Regression coverage for card selection -> common Start -> batch dispatch."""

import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QObject, Signal
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget

import config
from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import build_start_command


@pytest.fixture(scope="session")
def qapp():
    return QApplication.instance() or QApplication([])


def disabled_settings():
    return {
        config.KEY_ALIGNMENT: "No Alignment",
        config.KEY_SUPER_RESOLUTION: "No Super Resolution",
        config.KEY_DENOISING: "No Denoising",
        config.KEY_HDR: "No HDR",
        config.KEY_CHECKBOX_ALIGN: False,
        config.KEY_CHECKBOX_SUPER_RES: False,
        config.KEY_CHECKBOX_DENOISING: False,
        config.KEY_CHECKBOX_HDR: False,
    }


@pytest.mark.parametrize("algorithm", ["Weighted HDR", "SPDE-MR HDR Fusion"])
def test_hdr_command_respects_toggle_and_copies_settings(algorithm):
    settings = disabled_settings()
    settings[config.KEY_HDR] = algorithm
    assert build_start_command(settings) is None
    settings[config.KEY_CHECKBOX_HDR] = True
    settings["processing_parameters"] = "preserved"
    command = build_start_command(settings)
    received = []
    command.dispatch(received.append)
    assert command.direct_start
    assert received[0][config.KEY_HDR] == algorithm
    assert received[0][config.KEY_CHECKBOX_HDR] is True
    assert received[0]["processing_parameters"] == "preserved"
    received[0][config.KEY_HDR] = "modified by receiver"
    assert command.execution_settings()[config.KEY_HDR] == algorithm
    assert settings[config.KEY_HDR] == algorithm


@pytest.mark.parametrize("alias,canonical", [
    ("Weighted HDR (Foundation)", "Weighted HDR"),
    ("SPDE-MR (Patch-Based)", "SPDE-MR HDR Fusion"),
])
def test_saved_hdr_commands_are_normalized(alias, canonical):
    command = build_start_command({config.KEY_HDR_ALGO: alias, config.KEY_CHECKBOX_HDR: True})
    assert command.execution_settings()[config.KEY_HDR] == canonical


def test_combined_cards_keep_every_selected_stage():
    settings = disabled_settings()
    settings.update({
        config.KEY_HDR: "Weighted HDR", config.KEY_CHECKBOX_HDR: True,
        config.KEY_DENOISING: "Average", config.KEY_CHECKBOX_DENOISING: True,
        config.KEY_SUPER_RESOLUTION: "splattingSR", config.KEY_CHECKBOX_SUPER_RES: True,
    })
    command = build_start_command(settings)
    assert [stage.category for stage in command.stages] == ["super_resolution", "hdr", "denoising"]
    assert command.execution_settings() == settings


@pytest.fixture
def panels(qapp, monkeypatch):
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.left_panel import LeftPanel
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2.right_panel import RightPanel
    from pixel_refine_desktop.enhance_stack.components.batch_page_v2 import algorithm_panel

    class CapturedProcessor(QObject):
        progress_update = Signal(int, str)
        finished_processing = Signal()

        def __init__(self, batch_id, settings, parent):
            super().__init__(parent)
            self.batch_id = batch_id
            self.settings = dict(settings)
            self.started = False
            self.stopped = False

        def start(self):
            self.started = True

        def isRunning(self):
            return self.started and not self.stopped

        def stop(self):
            self.stopped = True

    monkeypatch.setattr(algorithm_panel, "AlgorithmProcessorThread", CapturedProcessor)
    left = LeftPanel()
    right = RightPanel()
    display = left.display_panel
    executor = left.algorithm_panel
    display.right_panel = right
    right.algorithm_settings_changed.connect(executor.update_settings)
    right.algorithm_settings_changed.connect(display.apply_algorithm_settings_fast)
    right.process_command_changed.connect(executor.set_process_command)
    executor.current_batch_id = display.current_batch_id = right.current_batch_id = 3
    left.resize(1000, 700)
    right.resize(340, 700)
    left.show()
    right.show()
    right.align_form.set_value("No Alignment")
    for card in (right.sr_card, right.hdr_card, right.denoise_card):
        card.setChecked(False, animate=False)
    right._on_settings_changed(save_to_store=False)
    qapp.processEvents()
    yield left, right
    executor._cancel_delay_timer.stop()
    executor._update_timer.stop()
    right._sync_store_timer.stop()
    left.close()
    right.close()
    left.deleteLater()
    right.deleteLater()
    qapp.processEvents()


@pytest.mark.parametrize("card_attr,algorithm,key,enabled_key", [
    ("hdr_card", "Weighted HDR", config.KEY_HDR, config.KEY_CHECKBOX_HDR),
    ("hdr_card", "SPDE-MR HDR Fusion", config.KEY_HDR, config.KEY_CHECKBOX_HDR),
    ("denoise_card", "Average", config.KEY_DENOISING, config.KEY_CHECKBOX_DENOISING),
    ("sr_card", "splattingSR", config.KEY_SUPER_RESOLUTION, config.KEY_CHECKBOX_SUPER_RES),
])
def test_card_shows_start_and_click_dispatches_selection(panels, qapp, card_attr, algorithm, key, enabled_key):
    left, right = panels
    card = getattr(right, card_attr)
    card.combo.setCurrentIndex(card.combo.findText(algorithm))
    card.setChecked(True, animate=False)
    qapp.processEvents()
    assert left.display_panel.start_btn_ref.isVisible()
    # The delayed adaptive update must not hide HDR Start again.
    QTest.qWait(100)
    assert left.display_panel.start_btn_ref.isVisible()
    left.display_panel.start_btn_ref.click()
    processor = left.algorithm_panel.processor_thread
    assert processor.started
    assert processor.batch_id == 3
    assert processor.settings[key] == algorithm
    assert processor.settings[enabled_key] is True
    left.algorithm_panel._enable_cancel_button()
    left.display_panel.start_btn_ref.click()
    assert processor.stopped


def test_hdr_start_disappears_when_card_disabled(panels, qapp):
    left, right = panels
    right.hdr_card.setChecked(True, animate=False)
    assert left.display_panel.start_btn_ref.isVisible()
    right.hdr_card.setChecked(False, animate=False)
    QTest.qWait(100)
    assert not left.display_panel.start_btn_ref.isVisible()


def test_general_start_accepts_an_external_card_command(panels):
    from pixel_refine_desktop.enhance_stack.core.logic.card_process_command import CardProcessCommand, StartProcessCommand
    left, _ = panels
    command = StartProcessCommand(disabled_settings(), (
        CardProcessCommand("custom_stage", "Custom Fusion", "Custom Card", "checkbox_custom"),
    ))
    left.algorithm_panel.set_process_command(command)
    QTest.qWait(100)
    assert left.display_panel.start_btn_ref.isVisible()
    left.display_panel.start_btn_ref.click()
    assert left.algorithm_panel.processor_thread.settings["custom_stage"] == "Custom Fusion"
    assert left.algorithm_panel.processor_thread.settings["checkbox_custom"] is True


def test_restored_hdr_settings_keep_start_enabled(panels, monkeypatch):
    left, _ = panels
    executor = left.algorithm_panel
    monkeypatch.setattr(executor, "get_data", lambda *args: {
        config.KEY_HDR_ALGO: "SPDE-MR HDR Fusion", config.KEY_CHECKBOX_HDR: True,
    })
    executor.on_store_changed(None, None)
    assert executor.get_settings()[config.KEY_HDR] == "SPDE-MR HDR Fusion"
    assert executor.get_settings()[config.KEY_CHECKBOX_HDR] is True
    assert left.display_panel.start_btn_ref.isVisible()


@pytest.mark.parametrize("algorithm", ["Weighted HDR", "SPDE-MR HDR Fusion"])
def test_hdr_command_reaches_existing_hdr_entry_point(qapp, monkeypatch, algorithm):
    from pixel_refine_desktop.enhance_stack.core.logic import algorithm_processor
    calls = []
    monkeypatch.setattr(algorithm_processor, "running_hdr_fusion", lambda **kwargs: calls.append(kwargs))
    settings = disabled_settings()
    settings.update({config.KEY_HDR: algorithm, config.KEY_CHECKBOX_HDR: True})
    parent = QWidget()
    parent.controller = SimpleNamespace(db_path="hdr_test_session.sqlite")
    processor = algorithm_processor.AlgorithmProcessorThread(3, build_start_command(settings).execution_settings(), parent)
    errors = []
    processor.error_occurred.connect(errors.append)
    processor._run_in_process()
    assert not errors
    assert len(calls) == 1
    assert calls[0]["algorithm_name"] == algorithm
    assert calls[0]["batch_id"] == 3
    assert calls[0]["db_path"] == "hdr_test_session.sqlite"


@pytest.mark.parametrize("algorithm", ["Weighted HDR", "SPDE-MR HDR Fusion"])
def test_hdr_command_is_sent_to_isolated_worker(qapp, monkeypatch, algorithm):
    from pixel_refine_desktop.enhance_stack.core.logic.algorithm_processor import AlgorithmProcessorThread
    from pixel_refine_desktop.enhance_stack.core.logic.backend_worker_manager import BackendWorkerManager
    payloads = []

    def dispatch(payload, **callbacks):
        payloads.append(payload)
        return {"success": True}

    worker = SimpleNamespace(ensure_worker_ready=lambda: True, dispatch_task=dispatch)
    monkeypatch.setattr(BackendWorkerManager, "instance", lambda: worker)
    monkeypatch.delenv("PIXEL_REFINE_DISABLE_WORKER", raising=False)
    settings = disabled_settings()
    settings.update({config.KEY_HDR: algorithm, config.KEY_CHECKBOX_HDR: True})
    parent = QWidget()
    parent.controller = SimpleNamespace(db_path="hdr_test_session.sqlite")
    processor = AlgorithmProcessorThread(3, build_start_command(settings).execution_settings(), parent)
    errors = []
    processor.error_occurred.connect(errors.append)
    processor.run()
    assert not errors
    assert len(payloads) == 1
    assert payloads[0]["batch_id"] == 3
    assert payloads[0]["db_path"] == "hdr_test_session.sqlite"
    assert payloads[0]["settings"][config.KEY_HDR] == algorithm
    assert payloads[0]["settings"][config.KEY_CHECKBOX_HDR] is True
