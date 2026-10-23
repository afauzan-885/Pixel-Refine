"""Pure checked views and fail-fast serial invocation ownership.

No native imports, finalizers, background threads or implicit synchronization.
Adapters provide live-owner checks and a real synchronous completion barrier.
"""
from dataclasses import dataclass
import threading

_MAX = (1 << 64) - 1
_active = {}  # Explicit leases retain resources even if callers drop wrappers.
_hazard_lock = threading.RLock()


class InvocationBusyError(RuntimeError):
    pass


def _uint(value, name):
    if type(value) is not int or not 0 <= value <= _MAX:
        raise ValueError(f"{name} must fit uint64")
    return value


@dataclass(frozen=True)
class DeviceViewDescriptor:
    owner: object
    device: object
    storage: object
    capacity_bytes: int
    shape: tuple
    dtype: str = "float32"
    offset_bytes: int = 0
    strides_bytes: tuple = ()

    def __post_init__(self):
        if self.owner is None or self.device is None or self.storage is None:
            raise ValueError("View requires owner/device/storage identity")
        if self.dtype != "float32":
            raise ValueError("Only float32 device views are bindable")
        _uint(self.capacity_bytes, "capacity")
        _uint(self.offset_bytes, "offset")
        if self.offset_bytes % 4:
            raise ValueError("float32 view offset must be four-byte aligned")
        shape = tuple(self.shape)
        strides, size = [], 4
        for extent in reversed(shape):
            if type(extent) is not int or extent <= 0:
                raise ValueError("View extents must be positive integers")
            strides.insert(0, size)
            if extent > _MAX // size:
                raise ValueError("View byte extent overflows uint64")
            size *= extent
        actual = tuple(self.strides_bytes) if self.strides_bytes else tuple(strides)
        if len(actual) != len(shape):
            raise ValueError("Stride rank must match shape rank")
        span = 4
        for extent, stride in zip(shape, actual):
            if type(stride) is not int or stride <= 0 or stride > _MAX:
                raise ValueError("Strides must be positive uint64 byte distances")
            if stride % 4:
                raise ValueError("float32 byte strides must be four-byte aligned")
            if extent - 1 > (_MAX - span) // stride:
                raise ValueError("Strided byte extent overflows uint64")
            span += (extent - 1) * stride
        if self.offset_bytes > self.capacity_bytes or span > self.capacity_bytes - self.offset_bytes:
            raise ValueError("View exceeds allocation capacity")
        object.__setattr__(self, "shape", shape)
        object.__setattr__(self, "strides_bytes", actual)

    @property
    def byte_range(self):
        size = 4 + sum((extent - 1) * stride for extent, stride in zip(self.shape, self.strides_bytes))
        return self.offset_bytes, self.offset_bytes + size

    def require_flat_binding(self):
        strides, size = [], 4
        for extent in reversed(self.shape):
            strides.insert(0, size)
            size *= extent
        if self.offset_bytes or self.strides_bytes != tuple(strides):
            raise ValueError("Runtime supports only offset-zero contiguous device views")


class DeviceView:
    """Strong storage reference with adapter-defined lifecycle validation.

    Raw storage is intentionally private. Explicit mutation/destruction through
    an independently retained legacy raw handle is outside this contract.
    """
    def __init__(self, descriptor, storage, validate, retain=None):
        self.descriptor = descriptor
        self._storage = storage
        self._validate = validate
        self._retain = retain

    def _bind(self, owner, device):
        self._validate()
        self.descriptor.require_flat_binding()
        if self.descriptor.owner != owner or self.descriptor.device != device:
            raise ValueError("Device view owner/device mismatch")
        return self._storage

    def _pin(self):
        self._validate()
        return self._retain() if self._retain is not None else lambda: None


@dataclass(frozen=True)
class Access:
    descriptor: DeviceViewDescriptor
    write: bool = False
    immutable: bool = False

    def __post_init__(self):
        if self.write and self.immutable:
            raise ValueError("Shared weights are immutable")


def conflicts(a, b):
    x, y = a.descriptor, b.descriptor
    return ((a.write or b.write) and x.owner == y.owner and x.device == y.device
            and x.storage == y.storage
            and x.byte_range[0] < y.byte_range[1] and y.byte_range[0] < x.byte_range[1])


class InvocationSlot:
    """One mutable scratch/output set. Capacity is exactly one, never waits.

    Active submissions across runners share byte-range hazard admission. This
    tracks host ownership, not device overlap or an external fence timeline.
    """
    def __init__(self):
        self.token = None
        self.closed = False

    def idle(self):
        if self.closed:
            raise RuntimeError("Invocation owner is closed")
        if self.token is not None:
            raise InvocationBusyError("Invocation slot held; release outputs or drain failed completion first")

    def begin(self, accesses, resources):
        with _hazard_lock:
            self.idle()
            accesses = tuple(accesses)
            for token in _active.values():
                if any(conflicts(a, b) for a in accesses for b in token.accesses):
                    raise InvocationBusyError("Read/write device-range dependency is still held")
            token = _Invocation(self, accesses, tuple(resources))
            self.token = token
            _active[id(token)] = token
            return token

    def close(self):
        with _hazard_lock:
            self.idle()
            self.closed = True


class _Invocation:
    def __init__(self, slot, accesses, resources):
        self.slot, self.accesses, self.resources = slot, accesses, resources
        self.completed = False
        self.references = 1

    def complete(self):
        self.completed = True
        # Completed output consumers may read, while writes remain blocked
        # until every consumer releases the producing slot.
        self.accesses = tuple(Access(a.descriptor, False, a.immutable) for a in self.accesses)

    def retain(self):
        with _hazard_lock:
            if not self.references or not self.completed:
                raise RuntimeError("Output dependency is not complete/live")
            self.references += 1
            return self.release

    def release(self):
        with _hazard_lock:
            if not self.completed:
                raise RuntimeError("Cannot release invocation before actual completion")
            if not self.references:
                raise RuntimeError("Invocation dependency already released")
            self.references -= 1
            if self.references == 0:
                for release in reversed(getattr(self, "pins", [])):
                    release()
                self.pins = []
                self.slot.token = None
                _active.pop(id(self), None)
                self.resources = ()


class OutputLease:
    """Explicit synchronous consumer lease; no GC/native cleanup hook.

    Consume callbacks must not retain raw storage after returning. They may
    enqueue work on this owner's stream: the adapter waits before returning.
    A dropped lease deliberately holds the bounded slot until explicit release.
    """
    def __init__(self, token, views, guard, synchronize, lock):
        self._token, self._views = token, views
        self._guard, self._sync, self._lock = guard, synchronize, lock
        self._released = False
        self._consuming = False

    def _live(self):
        if self._released:
            raise RuntimeError("Output lease was released")
        self._guard()

    @property
    def descriptors(self):
        with self._lock:
            self._live()
            return {name: view.descriptor for name, view in self._views.items()}

    def view(self, name):
        """Borrow a checked view for another runner's synchronous run_leased.

        The downstream runner pins the producer until its real completion.
        Creating a view alone does not extend the explicit lease lifetime.
        """
        with self._lock:
            self._live()
            source = self._views[name]
            def validate():
                self._guard()
                if not self._token.references:
                    raise RuntimeError("Output dependency was released")
                source._validate()
            return DeviceView(source.descriptor, source._storage, validate, self._token.retain)

    def consume(self, callback):
        with self._lock:
            self._live()
            if self._consuming:
                raise InvocationBusyError("Output consumer is already active")
            self._consuming = True
            # Completion failure retains slot/resources; a later release retries.
            self._token.completed = False
            try:
                return callback({name: view._bind(view.descriptor.owner, view.descriptor.device)
                                 for name, view in self._views.items()})
            finally:
                try:
                    self._sync()
                    self._token.complete()
                finally:
                    self._consuming = False

    def release(self):
        with self._lock:
            if self._released:
                return
            if self._consuming:
                raise InvocationBusyError("Cannot release during an active output consumer")
            self._live()
            self._sync()
            self._token.complete()
            self._token.release()
            self._released = True
            self._views = {}

    def __enter__(self):
        self._live()
        return self

    def __exit__(self, *exc):
        self.release()


class SerialDeviceInvocations:
    """Adapter shared by real runners; protects both safe and legacy entrypoints."""
    def __init__(self, guard, synchronize, owner_lock=None):
        self.lock = _OwnerLock(owner_lock)
        self.slot = InvocationSlot()
        self.guard, self.synchronize = guard, synchronize

    def check_legacy(self):
        self.guard()
        self.slot.idle()

    def submit(self, views, accesses, resources, execute, describe_output):
        with self.lock:
            self.guard()
            pins = []
            try:
                for view in views.values():
                    pins.append(view._pin())
                token = self.slot.begin(accesses, (self,) + tuple(resources) + tuple(views.values()))
            except BaseException:
                for release in reversed(pins):
                    release()
                raise
            token.pins = pins
            token.orphaned_submission = False
            try:
                outputs = execute()
                self.synchronize()
                token.complete()
                output_views = {name: describe_output(name, value) for name, value in outputs.items()}
                token.resources += tuple(outputs.values())
                return OutputLease(token, output_views, self.guard, self.synchronize, self.lock)
            except BaseException:
                # Includes cancellation/KeyboardInterrupt; never free queued work.
                token.orphaned_submission = True
                self.synchronize()
                token.complete()
                token.release()
                raise

    def drain_failed(self):
        with self.lock:
            self.guard()
            token = self.slot.token
            if token is not None and token.orphaned_submission:
                self.synchronize()
                token.complete()
                token.release()


class _OwnerLock:
    def __init__(self, owner_lock):
        self.local = threading.RLock()
        self.owner = owner_lock

    def __enter__(self):
        # Owner first: callers may already hold an engine reservation.
        if self.owner is not None:
            self.owner.acquire()
        self.local.acquire()
        return self

    def __exit__(self, *exc):
        self.local.release()
        if self.owner is not None:
            self.owner.release()
