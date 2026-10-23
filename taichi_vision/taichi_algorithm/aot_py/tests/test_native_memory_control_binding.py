"""Pure tests of the production binding; no package/engine/Taichi/native import."""
import ctypes as C
import importlib.util
from pathlib import Path
import threading
from types import SimpleNamespace
import unittest
from unittest import mock

path = Path(__file__).resolve().parents[3] / "taichi_aot" / "native_memory_control.py"
spec = importlib.util.spec_from_file_location("native_memory_control_pure_test", path)
control = importlib.util.module_from_spec(spec)
spec.loader.exec_module(control)


class Function:
    def __init__(self, callback):
        self.callback = callback

    def __call__(self, *args):
        return self.callback(*args)


class Owner:
    def __init__(self):
        self._lock = threading.RLock()
        self.runtime = 17
        self.guarded = 0
        self.reject = False

    def _assert_native_context_owner(self, operation):
        if self.reject:
            raise RuntimeError("wrong owner thread")
        self.guarded += 1


class FakeLibrary:
    def __init__(self):
        self.calls = []
        self.fail = False
        self.bad_abi = False
        self.ti_aot_get_memory_snapshot = Function(self.snapshot)
        self.ti_aot_set_memory_limits = Function(self.limits)
        self.ti_aot_trim_memory_cache = Function(self.trim)
        self.get_last_engine_error = Function(lambda runtime: b"native budget or cleanup error")

    def snapshot(self, runtime, pointer):
        value = C.cast(pointer, C.POINTER(control.SnapshotV1)).contents
        self.calls.append(("snapshot", runtime, value.struct_size, value.abi_version))
        value.retained_bytes, value.budget_charge_bytes = 32, 48
        value.unresolved_bytes = 16
        value.flags = 1 | 2 | 8
        value.physical_bytes = value.driver_budget_bytes = value.in_flight_bytes = (1 << 64) - 1
        if self.bad_abi:
            value.abi_version = 2
        return 0 if self.fail else 1

    def limits(self, runtime, pointer):
        value = C.cast(pointer, C.POINTER(control.LimitsV1)).contents
        self.calls.append(("limits", runtime, value.budget_bytes, value.cache_max_bytes,
                           value.cache_max_entries, list(value.reserved)))
        return 0 if self.fail else 1

    def trim(self, runtime, bytes_target, entries_target, pointer):
        value = C.cast(pointer, C.POINTER(control.TrimV1)).contents
        value.valid, value.freed_bytes, value.freed_entries = 1, 16, 1
        value.remaining_cache_bytes, value.remaining_cache_entries = 32, 2
        self.calls.append(("trim", runtime, bytes_target, entries_target))
        return 0 if self.fail else 1


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.owner, self.library = Owner(), FakeLibrary()
        self.api = control.NativeMemoryControl(self.owner, library=self.library)

    def test_layout_and_lazy_owner_runtime(self):
        self.assertEqual((C.sizeof(control.LimitsV1), C.sizeof(control.SnapshotV1), C.sizeof(control.TrimV1)),
                         (48, 272, 48))
        self.assertEqual(self.library.calls, [])
        result = self.api.snapshot()
        self.assertEqual((result["retained_bytes"], result["unresolved_bytes"]), (32, 16))
        self.assertIsNone(result["physical_bytes"])
        self.assertIsNone(result["driver_budget_bytes"])
        self.assertIsNone(result["in_flight_bytes"])
        self.owner.runtime = 29
        self.api.snapshot()
        self.assertEqual(self.library.calls[-1][1], 29)
        self.assertEqual(self.owner.guarded, 2)

    def test_caps_are_explicit_and_width_checked_before_native_call(self):
        self.api.configure(budget_bytes=128, cache_max_bytes=32, cache_max_entries=2)
        self.assertEqual(self.library.calls[-1], ("limits", 17, 128, 32, 2, [0, 0]))
        for value in (-1, 1 << 64, True, 1.5):
            with self.assertRaises(ValueError):
                self.api.configure(budget_bytes=value)
        with self.assertRaises(ValueError):
            self.api.configure(cache_max_bytes=32)
        self.assertEqual(len(self.library.calls), 1)

    def test_closed_or_wrong_owner_does_not_call_native(self):
        self.owner.runtime = None
        with self.assertRaises(control.NativeMemoryControlError): self.api.snapshot()
        self.owner.runtime, self.owner.reject = 17, True
        with self.assertRaisesRegex(RuntimeError, "owner thread"): self.api.trim()
        self.assertEqual(self.library.calls, [])

    def test_unsupported_binary_has_clear_error_without_engine_init(self):
        api = control.NativeMemoryControl(self.owner, library=object())
        with self.assertRaises(control.NativeMemoryControlUnavailable): api.snapshot()
        self.assertEqual(self.library.calls, [])

    def test_abi_mismatch_and_native_failure_are_not_silently_accepted(self):
        self.library.bad_abi = True
        with self.assertRaisesRegex(control.NativeMemoryControlError, "ABI/size"): self.api.snapshot()
        self.library.fail = True
        with self.assertRaisesRegex(control.NativeMemoryControlError, "native budget"): self.api.configure()

    def test_trim_preserves_native_partial_progress_on_failure(self):
        self.library.fail = True
        with self.assertRaises(control.NativeMemoryControlError) as caught:
            self.api.trim(target_bytes=32, target_entries=2)
        self.assertEqual(caught.exception.partial["freed_bytes"], 16)
        self.assertEqual(caught.exception.partial["remaining_cache_entries"], 2)
        self.assertEqual(self.library.calls[-1], ("trim", 17, 32, 2))

    def test_existing_module_library_is_lazy_and_can_follow_owner_reinitialization(self):
        api = control.NativeMemoryControl(self.owner)
        module = SimpleNamespace(_LIB=self.library)
        with mock.patch.dict(control.sys.modules, {"taichi_vision.taichi_aot.engine": module}):
            api.snapshot()
            other = FakeLibrary()
            module._LIB = other
            self.owner.runtime = 31
            api.snapshot()
            self.assertEqual(other.calls[-1][1], 31)
        self.assertEqual(len(self.library.calls), 1)

    def test_owner_garbage_collection_never_leaves_a_usable_stale_runtime(self):
        del self.owner
        with self.assertRaisesRegex(control.NativeMemoryControlError, "no longer exists"):
            self.api.snapshot()
        self.assertEqual(self.library.calls, [])


if __name__ == "__main__":
    unittest.main()
