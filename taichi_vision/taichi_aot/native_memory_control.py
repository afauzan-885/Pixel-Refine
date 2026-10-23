"""Opt-in controls for an existing AOTEngine; never creates/imports an engine.

This module does not implement another governor. The application/MemoryPolicy
chooses limits; this binding submits explicit native hard caps and idle trims.
Counters cover bridge-requested bytes, not all AOT/RHI/driver allocations or VRAM.
"""
from contextlib import contextmanager
import ctypes as C
import sys
import weakref

_MAX = (1 << 64) - 1
_PREFIX = [("struct_size", C.c_uint32), ("abi_version", C.c_uint32)]


class LimitsV1(C.Structure):
    _fields_ = _PREFIX + [(name, C.c_uint64) for name in
        ("budget_bytes", "cache_max_bytes", "cache_max_entries")] + [("reserved", C.c_uint64 * 2)]


_SNAPSHOT_FIELDS = (
    "flags budget_bytes cache_max_bytes cache_max_entries budget_charge_bytes "
    "retained_bytes pending_bytes unresolved_bytes live_bytes caller_bytes "
    "private_staging_bytes idle_cache_bytes mapped_bytes quarantined_bytes leased_private_bytes "
    "retained_count unresolved_count caller_count private_staging_count idle_cache_count mapped_count "
    "quarantined_count leased_private_count allocation_requests allocation_requested_bytes_total "
    "allocation_failures high_water_retained_bytes high_water_budget_charge_bytes cache_hits cache_misses "
    "physical_bytes driver_budget_bytes in_flight_bytes"
).split()


class SnapshotV1(C.Structure):
    _fields_ = _PREFIX + [(name, C.c_uint64) for name in _SNAPSHOT_FIELDS]


class TrimV1(C.Structure):
    _fields_ = _PREFIX + [(name, C.c_uint64) for name in (
        "valid", "freed_bytes", "freed_entries", "remaining_cache_bytes", "remaining_cache_entries")]


class NativeMemoryControlError(RuntimeError):
    def __init__(self, message, *, partial=None):
        super().__init__(message)
        self.partial = partial


class NativeMemoryControlUnavailable(NativeMemoryControlError):
    pass


def _new(kind):
    value = kind()
    value.struct_size, value.abi_version = C.sizeof(kind), 1
    return value


def _values(value):
    if value.abi_version != 1 or value.struct_size < C.sizeof(type(value)):
        raise NativeMemoryControlError("Native memory control response ABI/size mismatch")
    return {name: int(getattr(value, name)) for name, _ in type(value)._fields_}


def _u64(value, name):
    if type(value) is not int or not 0 <= value <= _MAX:
        raise ValueError(f"{name} must be an unsigned 64-bit integer")
    return value


class NativeMemoryControl:
    """Use the caller's current live runtime under its existing ownership lock.

    Passing library is intended for an already-loaded bridge or test fake.
    Without it, use only the already-imported engine module's _LIB. Runtime
    handles are resolved on every call, so close/reinitialize cannot reuse a
    captured stale handle. Native caps reset when that owner creates a context.
    """
    def __init__(self, engine, *, library=None):
        self._engine = weakref.ref(engine)
        self._library = library

    @contextmanager
    def _live(self):
        engine = self._engine()
        if engine is None:
            raise NativeMemoryControlError("AOT engine owner no longer exists")
        lock = getattr(engine, "_lock", None)
        guard = getattr(engine, "_assert_native_context_owner", None)
        if lock is None or not callable(guard):
            raise NativeMemoryControlError("Expected existing AOTEngine ownership lock/guard")
        with lock:
            guard("native memory controls")
            runtime = getattr(engine, "runtime", None)
            if not runtime:
                raise NativeMemoryControlError("AOT engine runtime is closed")
            library = self._library
            if library is None:
                module = sys.modules.get("taichi_vision.taichi_aot.engine")
                library = getattr(module, "_LIB", None)
            if library is None:
                raise NativeMemoryControlUnavailable("No already-loaded AOT bridge")
            specs = {
                "ti_aot_get_memory_snapshot": [C.c_void_p, C.POINTER(SnapshotV1)],
                "ti_aot_set_memory_limits": [C.c_void_p, C.POINTER(LimitsV1)],
                "ti_aot_trim_memory_cache": [C.c_void_p, C.c_uint64, C.c_uint64, C.POINTER(TrimV1)],
            }
            try:
                for name, args in specs.items():
                    function = getattr(library, name)
                    function.argtypes, function.restype = args, C.c_int
                error = library.get_last_engine_error
                error.argtypes, error.restype = [C.c_void_p], C.c_char_p
            except AttributeError as exc:
                raise NativeMemoryControlUnavailable("Loaded bridge has no memory control ABI v1") from exc
            yield runtime, library

    @staticmethod
    def _failure(library, runtime, *, partial=None):
        message = library.get_last_engine_error(runtime)
        if isinstance(message, bytes):
            message = message.decode("utf-8", errors="replace")
        raise NativeMemoryControlError(message or "Native memory control failed", partial=partial)

    def snapshot(self):
        value = _new(SnapshotV1)
        with self._live() as (runtime, library):
            if library.ti_aot_get_memory_snapshot(runtime, C.byref(value)) != 1:
                self._failure(library, runtime)
        result = _values(value)
        for name, flag in (("physical_bytes", 1), ("driver_budget_bytes", 1), ("in_flight_bytes", 2)):
            if result["flags"] & flag or result[name] == _MAX:
                result[name] = None
        return result

    def configure(self, *, budget_bytes=0, cache_max_bytes=0, cache_max_entries=0):
        value = _new(LimitsV1)
        for name, number in (("budget_bytes", budget_bytes), ("cache_max_bytes", cache_max_bytes),
                             ("cache_max_entries", cache_max_entries)):
            setattr(value, name, _u64(number, name))
        if bool(cache_max_bytes) != bool(cache_max_entries):
            raise ValueError("Cache requires both byte and entry limits, or both zero")
        with self._live() as (runtime, library):
            if library.ti_aot_set_memory_limits(runtime, C.byref(value)) != 1:
                self._failure(library, runtime)

    def trim(self, *, target_bytes=0, target_entries=0):
        target_bytes, target_entries = _u64(target_bytes, "target_bytes"), _u64(target_entries, "target_entries")
        value = _new(TrimV1)
        with self._live() as (runtime, library):
            if library.ti_aot_trim_memory_cache(runtime, target_bytes, target_entries, C.byref(value)) != 1:
                partial = _values(value) if value.valid == 1 else None
                self._failure(library, runtime, partial=partial)
        if value.valid != 1:
            raise NativeMemoryControlError("Native trim did not return valid counters")
        return _values(value)
