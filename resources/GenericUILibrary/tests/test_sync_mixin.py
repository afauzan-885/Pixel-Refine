"""Contract tests for the 3-API store binding (bind / sync / on_sync)."""

import pytest
from PySide6.QtCore import QObject

from resources.GenericUILibrary.mixins import RealtimeMixin, SyncMixin


class StoreSignal:
    def __init__(self):
        self.slots = []

    def connect(self, slot):
        self.slots.append(slot)

    def disconnect(self, slot):
        if slot not in self.slots:
            raise RuntimeError("not connected")
        self.slots.remove(slot)

    def emit(self, key, value):
        for slot in list(self.slots):
            slot(key, value)


class FakeStore:
    """Minimal dotted-key store with the DataStore contract the mixin relies on."""

    def __init__(self, data=None):
        self.data = data or {}
        self.changed = StoreSignal()
        self.emits = []
        self.writes = []
        self.saves = 0

    def get(self, key=None, default=None):
        if key is None:
            return self.data
        current = self.data
        for part in str(key).split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def _set_path(self, key, value):
        parts = str(key).split(".")
        current = self.data
        for part in parts[:-1]:
            child = current.get(part)
            if not isinstance(child, dict):
                child = {}
                current[part] = child
            current = child
        current[parts[-1]] = value

    def set(self, key, value, notify=True):
        self.writes.append((key, value, notify))
        self._set_path(key, value)
        if notify:
            self.emits.append((key, value))
            self.changed.emit(key, value)

    def silent_set(self, key, value):
        self.set(key, value, notify=False)

    def update_bulk(self, data, deep=True, save=True):
        for key, value in data.items():
            self.writes.append((key, value, True))
            self._set_path(key, value)
        self.emits.append((None, self.data))
        self.changed.emit(None, self.data)

    def save_to_file(self):
        self.saves += 1


class RecordingWidget:
    def __init__(self, name="widget"):
        self.name = name
        self.value = "<unset>"
        self.blocked_states = []

    def set_value(self, value):
        self.value = value

    def blockSignals(self, blocked):
        self.blocked_states.append(blocked)
        return blocked


class ExplodingWidget(RecordingWidget):
    def set_value(self, value):
        raise RuntimeError("widget deleted")


class Host(QObject, SyncMixin):
    def __init__(self):
        super().__init__()
        self.calls = []

    def on_sync(self, payload, *, key=None, origin=None):
        self.calls.append({"payload": payload, "key": key, "origin": origin})


def last_call(host):
    return host.calls[-1]


# ---------------------------------------------------------------- bind
def test_bind_initializes_state_and_follows_store():
    store = FakeStore()
    host = Host()
    host.bind(store)
    assert host._bindings == {}
    assert host._scope_prefix == ""
    assert host._follow is True
    assert store.changed.slots == [host._handle_store_change]


def test_bind_key_and_scope_are_exclusive():
    host = Host()
    with pytest.raises(ValueError):
        host.bind(FakeStore(), key="language", scope="7")


def test_bind_bindings_cannot_combine_with_key():
    host = Host()
    with pytest.raises(ValueError):
        host.bind(FakeStore(), key="language", bindings={"a": RecordingWidget()})


def test_bind_bindings_without_scope_register_until_a_scope_is_set():
    store = FakeStore({"7": {"a": 1}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, bindings={"a": widget}, apply=False)
    assert widget.value == "<unset>"
    host.sync(scope="7")
    assert widget.value == 1


def test_bind_applies_scope_bindings_immediately():
    store = FakeStore({"7": {"alignment_algo": "OFB", "denoising_algo": "FusionNet"}})
    host = Host()
    alignment, denoising = RecordingWidget("alignment"), RecordingWidget("denoising")
    host.bind(
        store,
        scope="7",
        bindings={
            "alignment_algo": (alignment, "value", "No Alignment"),
            "denoising_algo": denoising,
        },
        fallback="No Denoising",
    )
    assert alignment.value == "OFB"
    assert denoising.value == "FusionNet"
    assert last_call(host)["origin"] == "store"
    assert last_call(host)["payload"] == {
        "alignment_algo": "OFB",
        "denoising_algo": "FusionNet",
    }


def test_bind_merges_bindings_across_calls():
    store = FakeStore({"3": {"a": 1, "b": 2}})
    host = Host()
    first, second = RecordingWidget("a"), RecordingWidget("b")
    host.bind(store, scope="3", bindings={"a": first})
    host.bind(store, scope="3", bindings={"b": second})
    assert first.value == 1
    assert second.value == 2


def test_bind_apply_false_defers_until_sync():
    store = FakeStore({"4": {"a": 1}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="4", bindings={"a": widget}, apply=False)
    assert widget.value == "<unset>"
    host.sync()
    assert widget.value == 1


def test_bind_follow_false_ignores_store_events():
    store = FakeStore({"5": {"a": 1}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="5", bindings={"a": widget}, follow=False)
    store.data["5"]["a"] = 2
    store.changed.emit("5.a", 2)
    assert widget.value == 1


def test_rebind_other_store_disconnects_previous():
    first, second = FakeStore({"1": {"a": 1}}), FakeStore({"1": {"a": 2}})
    host = Host()
    widget = RecordingWidget()
    host.bind(first, scope="1", bindings={"a": widget})
    host.bind(second, scope="1", bindings={"a": widget})
    assert first.changed.slots == []
    first.changed.emit("1.a", 99)
    assert widget.value == 2


# ---------------------------------------------------------------- sync
def test_scope_switch_applies_without_leaking_previous_values():
    store = FakeStore({"1": {"denoising_algo": "FusionNet"}, "2": {"denoising_algo": "Average"}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="2", bindings={"denoising_algo": widget}, fallback="No Denoising")
    assert widget.value == "Average"
    host.sync(scope="1")
    assert widget.value == "FusionNet"


def test_sync_reapplies_same_scope_values():
    store = FakeStore({"3": {"denoising_algo": "Average"}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="3", bindings={"denoising_algo": widget}, fallback="No Denoising")
    store.data["3"]["denoising_algo"] = "Similarity"
    host.sync()
    assert widget.value == "Similarity"


def test_sync_values_writes_with_scope_prefix_and_skips_none():
    store = FakeStore({"7": {}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="7", bindings={"denoising_algo": widget}, fallback="No Denoising")
    host.sync(values={"denoising_algo": "Average", "alignment_algo": None})
    assert store.get("7.denoising_algo") == "Average"
    assert store.get("7.alignment_algo") is None
    assert widget.value == "Average"
    assert last_call(host)["origin"] == "self"


def test_sync_notify_false_suppresses_store_event():
    store = FakeStore({})
    host = Host()
    host.bind(store, scope="7")
    host.sync(values={"denoising_algo": "Average"}, notify=False)
    assert store.get("7.denoising_algo") == "Average"
    assert store.emits == []


def test_sync_persist_saves_synchronously():
    store = FakeStore({})
    host = Host()
    host.bind(store, scope="7")
    host.sync(values={"denoising_algo": "Average"}, persist=True)
    assert store.saves == 1


def test_sync_peek_returns_payload_without_applying():
    store = FakeStore({"8": {"denoising_algo": "FusionNet"}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="8", bindings={"denoising_algo": widget}, fallback="No Denoising")
    store.data["8"]["denoising_algo"] = "Average"
    assert host.sync(peek=True) == {"denoising_algo": "Average"}
    assert widget.value == "FusionNet"


def test_sync_peek_key_returns_scalar_in_single_key_mode():
    store = FakeStore({"language": "English"})
    host = Host()
    host.bind(store, key="language")
    assert host.sync(peek=True, key="language") == "English"


@pytest.mark.parametrize(
    "kwargs",
    [
        {"values": {"a": 1}, "peek": True},
        {"values": {"a": 1}, "keys": ["a"]},
        {"scope": "1", "key": "language"},
        {"notify": False},
        {"persist": True},
    ],
)
def test_sync_rejects_invalid_combinations(kwargs):
    host = Host()
    host.bind(FakeStore())
    with pytest.raises(ValueError):
        host.sync(**kwargs)


# ---------------------------------------------------------------- events
def test_child_key_update_only_touches_that_binding():
    store = FakeStore({"5": {"alignment_algo": "OFB", "denoising_algo": "FusionNet"}})
    host = Host()
    alignment, denoising = RecordingWidget("alignment"), RecordingWidget("denoising")
    host.bind(
        store,
        scope="5",
        bindings={
            "alignment_algo": (alignment, "value", "No Alignment"),
            "denoising_algo": (denoising, "value", "No Denoising"),
        },
    )
    store.set("5.denoising_algo", "Average")
    assert denoising.value == "Average"
    assert alignment.value == "OFB"
    assert last_call(host)["key"] == "denoising_algo"

    store.changed.emit("6.denoising_algo", "Similarity")
    assert denoising.value == "Average"


def test_scope_object_replacement_uses_payload():
    store = FakeStore({"4": {"denoising_algo": "Average"}})
    host = Host()
    widget = RecordingWidget()
    host.bind(store, scope="4", bindings={"denoising_algo": widget}, fallback="No Denoising")
    store.changed.emit("4", {"denoising_algo": "Similarity"})
    assert widget.value == "Similarity"
    assert last_call(host)["payload"] == {"denoising_algo": "Similarity"}

    store.changed.emit("4", {})
    assert widget.value == "No Denoising"


def test_bulk_reload_updates_single_key_widget():
    store = FakeStore({"language": "English"})
    host = Host()
    host.bind(store, key="language")
    assert store.get("language") == "English"
    assert last_call(host)["payload"] == {"language": "English"}

    store.data["language"] = "Indonesian"
    store.changed.emit(None, store.data)

    assert last_call(host)["payload"] == {"language": "Indonesian"}
    assert last_call(host)["origin"] == "store"


def test_broadcast_mode_reports_changed_key():
    store = FakeStore({"task1": 40})
    host = Host()
    host.bind(store)
    store.set("task1", 55)
    assert last_call(host)["payload"] == {"task1": 55}
    assert last_call(host)["key"] == "task1"


def test_missing_value_uses_per_binding_then_default_fallback():
    store = FakeStore({})
    host = Host()
    per_key, defaulted = RecordingWidget("per-key"), RecordingWidget("defaulted")
    host.bind(
        store,
        scope="9",
        bindings={
            "denoising_algo": (per_key, "value", "No Denoising"),
            "alignment_algo": defaulted,
        },
        fallback="No Alignment",
    )
    assert per_key.value == "No Denoising"
    assert defaulted.value == "No Alignment"


def test_broken_widget_does_not_block_other_bindings():
    store = FakeStore({"10": {"alignment_algo": "OFB", "denoising_algo": "FusionNet"}})
    host = Host()
    broken, denoising = ExplodingWidget("broken"), RecordingWidget("denoising")
    host.bind(
        store,
        scope="10",
        bindings={
            "alignment_algo": (broken, "value", "No Alignment"),
            "denoising_algo": (denoising, "value", "No Denoising"),
        },
    )
    assert denoising.value == "FusionNet"


def test_reentrant_sync_is_ignored():
    store = FakeStore({"11": {"denoising_algo": "FusionNet"}})
    host = Host()
    calls = []

    class ReentrantWidget(RecordingWidget):
        def set_value(self, value):
            calls.append(value)
            host.sync()
            super().set_value(value)

    widget = ReentrantWidget()
    host.bind(store, scope="11", bindings={"denoising_algo": widget}, fallback="No Denoising")
    calls.clear()
    host.sync(scope="11")
    assert calls == ["FusionNet"]


def test_realtime_mixin_exposes_the_same_three_apis():
    assert RealtimeMixin.bind is SyncMixin.bind
    assert RealtimeMixin.sync is SyncMixin.sync
    assert RealtimeMixin.on_sync is SyncMixin.on_sync
