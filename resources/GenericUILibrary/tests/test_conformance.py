"""PySide6 execution of the same compact behavior/style contract as the Flet port."""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtCore import QObject, Signal as QtSignal, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtTest import QTest
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDialog, QInputDialog, QCheckBox,
    QFrame, QLineEdit, QListWidget, QScrollBar,
)

import UILibrary as ui

TEST_DIR = Path(__file__).parent
TRACES = json.loads((TEST_DIR / "behavior_traces.json").read_text(encoding="utf-8"))
STYLE_GOLDEN = json.loads((TEST_DIR / "golden_styles.json").read_text(encoding="utf-8"))
CONTRACT = json.loads((TEST_DIR / "golden_signatures.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session", autouse=True)
def qapp():
    return QApplication.instance() or QApplication([])


def test_canonical_package_and_root_api():
    assert ui.BACKEND == "pyside6"
    assert ui.__all__ == CONTRACT["meta"]["root_exports"]
    assert len(ui.__all__) == 79
    for module_name, class_name in (
        ("config_panel", "ConfigPanel"), ("selector_panel", "SelectorPanel"),
        ("viewer_panel", "ViewerPanel"), ("workspace_layout", "WorkspaceLayout"),
    ):
        assert hasattr(getattr(ui, module_name), class_name)
        assert class_name not in ui.__all__
        assert not hasattr(ui, class_name)


def test_neutral_style_values_and_pyside_adapter(qapp):
    from UILibrary.theme import (
        Theme, DarkTheme, apply_style, create_button_style, create_card_style,
        create_input_style, create_select_style, create_list_style,
        create_scrollbar_style, create_checkbox_style,
    )

    builders = {
        "button_primary": lambda t: create_button_style("primary", t),
        "button_success": lambda t: create_button_style("success", t),
        "button_danger": lambda t: create_button_style("danger", t),
        "button_secondary": lambda t: create_button_style("secondary", t),
        "card": create_card_style, "input": create_input_style,
        "select": create_select_style, "list": create_list_style,
        "scrollbar": create_scrollbar_style, "checkbox": create_checkbox_style,
    }
    for theme_name, theme in (("light", Theme()), ("dark", DarkTheme())):
        assert {name: builder(theme).to_dict() for name, builder in builders.items()} == STYLE_GOLDEN[theme_name]

    button = ui.Button("Apply", variant="primary")
    apply_style(button, create_button_style("primary"))
    assert "#E8F5E9" in button.styleSheet()
    checkbox = QCheckBox("Enabled")
    apply_style(checkbox, create_checkbox_style())
    assert "QCheckBox::indicator" in checkbox.styleSheet()
    assert "QCheckBox:disabled" in checkbox.styleSheet()
    assert "QCheckBox::indicator:disabled" in checkbox.styleSheet()
    assert "width: 15px" in checkbox.styleSheet()

    field = QLineEdit()
    apply_style(field, create_input_style())
    assert "QLineEdit:focus" in field.styleSheet()
    assert "QLineEdit:disabled" in field.styleSheet()
    select = QComboBox()
    apply_style(select, create_select_style())
    assert "QComboBox QAbstractItemView::item:selected" in select.styleSheet()
    list_widget = QListWidget()
    apply_style(list_widget, create_list_style())
    assert "QListWidget::item:selected" in list_widget.styleSheet()
    assert "QListWidget::item:hover" in list_widget.styleSheet()
    frame = QFrame()
    apply_style(frame, create_card_style())
    assert "QFrame" in frame.styleSheet()
    scrollbar = QScrollBar(Qt.Orientation.Vertical)
    apply_style(scrollbar, create_scrollbar_style())
    assert "QScrollBar::handle:hover" in scrollbar.styleSheet()


def test_signal_connection_semantics_match_flet():
    class Probe(QObject):
        fired = QtSignal(str)

    probe = Probe()
    seen = []
    slot = seen.append
    probe.fired.connect(slot)
    probe.fired.connect(slot)
    probe.fired.emit("x")
    assert seen == ["x", "x"]
    probe.fired.disconnect(slot)
    seen.clear()
    probe.fired.emit("y")
    assert seen == ["y"]
    probe.fired.connect(lambda: seen.append("zero"))
    seen.clear()
    probe.fired.emit("z")
    assert seen == ["z", "zero"]


def test_config_panel_behavior_trace(qapp):
    panel = ui.config_panel.ConfigPanel()
    seen = []
    panel.apply_clicked.connect(seen.append)
    panel.tabs.setCurrentIndex(1)
    assert panel.tabs.currentIndex() == 1
    panel.cmb_method.setCurrentText(TRACES["config_apply"]["method"])
    panel.btn_apply.click()
    assert seen == [TRACES["config_apply"]]


def test_selector_panel_behavior_trace(qapp, monkeypatch):
    panel = ui.selector_panel.SelectorPanel(action_btn_text="Process")
    selected, deleted, added, actions, cleared = [], [], [], [], []
    panel.item_selected.connect(lambda item_id, label: selected.append((item_id, label)))
    panel.delete_requested.connect(deleted.append)
    panel.add_requested.connect(added.append)
    panel.action_requested.connect(lambda: actions.append(True))
    panel.selection_cleared.connect(lambda: cleared.append(True))
    panel.add_item("a", "First")
    panel.add_item("b", "Second")
    panel.list_widget.item(0).setSelected(True)
    assert selected == [tuple(TRACES["selector"]["selected"])]
    panel.btn_del.click()
    assert deleted == TRACES["selector"]["deleted"]
    monkeypatch.setattr(QInputDialog, "getText", lambda *args, **kwargs: ("Third", True))
    panel.btn_add.click()
    assert added == TRACES["selector"]["added"]
    panel.btn_action.click()
    assert len(actions) == TRACES["selector"]["action_count"]
    panel.list_widget.clearSelection()
    assert bool(cleared) is TRACES["selector"]["selection_cleared"]


def test_viewer_panel_behavior_trace(qapp):
    panel = ui.viewer_panel.ViewerPanel()
    imported, back = [], []
    panel.import_clicked.connect(lambda: imported.append(True))
    panel.back_clicked.connect(lambda: back.append(True))
    trace = TRACES["viewer"]
    panel.set_view_title(trace["title"])
    panel.add_grid_item("img-1", "Image 1")
    assert panel.lbl_title.text() == trace["title"]
    assert panel.grid_layout.count() == trace["items_before_clear"]
    panel.show_loading("Working")
    assert panel.loading_view.lbl_text.text() == trace["loading_text"]
    panel.btn_import.click()
    panel.btn_back.click()
    assert imported == [True] and back == [True]
    panel.show_empty_state()
    assert panel.grid_layout.count() == trace["items_after_clear"]


def test_workspace_and_grouped_feature_card_traces(qapp):
    workspace = ui.workspace_layout.WorkspaceLayout()
    trace = TRACES["workspace"]
    assert workspace.is_config_open is trace["initial_open"]
    workspace.toggle_config_panel(True)
    QTest.qWait(370)
    assert workspace.is_config_open is trace["open"]
    workspace.toggle_config_panel(False)
    QTest.qWait(370)
    assert workspace.is_config_open is trace["closed"]

    feature = TRACES["feature_card"]
    card = ui.FeatureCard("Denoising", "Long description", [feature["selected"]], feature["fallback"])
    group = ui.FeatureCardGroup(columns=2)
    group.add_card(card)
    checked, values = [], []
    card.checked_changed.connect(checked.append)
    card.value_changed.connect(values.append)
    card.combo.setCurrentText(feature["selected"])
    assert card.is_checked is True and card.get_value() == feature["selected"]
    card.combo.setCurrentText(feature["fallback"])
    assert card.is_checked is False and card.get_value() == feature["fallback"]
    assert checked == feature["checked_events"]
    assert values == feature["value_events"]


def test_shared_store_list_tabs_collapse_modal_comparison_progress_trace(qapp):
    trace = TRACES["shared"]

    store = ui.DataStore()
    store_events = []
    store.changed.connect(lambda key, value: store_events.append((key, value)))
    with store.transaction():
        store.set("alpha", 1)
        store.set("beta", 2)
        during = len(store_events)
    normalized = sorted(store_events, key=lambda event: event[0])
    assert during == trace["store"]["during_transaction"]
    assert [key for key, _ in normalized] == trace["store"]["keys"]
    assert [value for _, value in normalized] == trace["store"]["values"]

    group = ui.ListGroup()
    for key in ("a", "b", "c"):
        group.add_item(key.upper(), key)
    group.select_item_by_value("b")
    selected = group.get_selected_values()
    group.remove_selected_items()
    assert selected == trace["list"]["selected"]
    assert group.get_all_values() == trace["list"]["remaining"]

    tabs = ui.TabContainer(enable_animations=False)
    tabs.add_tab("General")
    tabs.add_tab("Advanced")
    tab_events = []
    tabs.tab_changed.connect(lambda index, title: tab_events.append([index, title]))
    tabs.set_current_tab(1)
    assert list(tabs.get_current_tab()) == trace["tabs"]["current"]
    assert tab_events == trace["tabs"]["changed"]

    collapse = ui.Collapse("Advanced settings")
    states = [collapse.is_expanded]
    collapse_events = []
    collapse.toggled.connect(collapse_events.append)
    collapse.toggle()
    states.append(collapse.is_expanded)
    assert states == trace["collapse"]["states"]
    assert collapse_events == trace["collapse"]["events"]

    accepted_dialog = ui.ModalDialog("Confirm?")
    accepted_dialog.accept()
    accepted = accepted_dialog.result() == int(QDialog.DialogCode.Accepted)
    rejected_dialog = ui.ModalDialog("Confirm?")
    rejected_dialog.reject()
    rejected = rejected_dialog.result() == int(QDialog.DialogCode.Accepted)
    assert [accepted, rejected] == trace["modal"]["results"]

    compare = ui.ImageCompareWidget(QPixmap(100, 50), QPixmap(100, 50))
    compare.resize(100, 100)
    compare._update_slider(-20)
    low = compare.slider_pos
    compare._update_slider(120)
    high = compare.slider_pos
    assert [low, high] == trace["comparison"]["positions"]

    progress = ui.ProgressBar()
    progress_events = []
    progress.value_changed.connect(progress_events.append)
    progress.set_value(trace["progress"]["value"], smooth=False)
    assert progress.get_value() == trace["progress"]["value"]
    assert progress_events == trace["progress"]["events"]
