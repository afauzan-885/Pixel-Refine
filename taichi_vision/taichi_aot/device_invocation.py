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
        self.slots = [self.slot]
        self.bundles = None
        self.shared_ids = set()
        self.pending_resources = []
        self.extra_resources = []
        self.configuration_failed = False
        self.requested_bytes = None
        self.guard, self.synchronize = guard, synchronize

    def check_legacy(self):
        self.guard()
        self.slot.idle()

    def submit(self, views, accesses, resources, execute, describe_output, *, slot=None):
        with self.lock:
            self.guard()
            pins = []
            try:
                for view in views.values():
                    pins.append(view._pin())
                token = (slot or self.slot).begin(accesses, (self,) + tuple(resources) + tuple(views.values()))
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
            for slot in self.slots:
                token = slot.token
                if token is not None and token.orphaned_submission:
                    self.synchronize()
                    token.complete()
                    token.release()

    def all_idle(self):
        for slot in self.slots:
            slot.idle()

    def available_slot(self):
        if self.configuration_failed:
            raise InvocationBusyError("Slot configuration failed; close explicitly before reuse")
        if self.slot.closed:
            raise RuntimeError("Invocation owner is closed")
        for index, slot in enumerate(self.slots):
            if slot.token is None:
                return index, slot
        raise InvocationBusyError("All bounded invocation slots are leased or awaiting completion")

    def configure_storage(self, base, immutable, *, count, max_requested_bytes,
                          identity, nbytes, clone):
        """Configure once while idle. Count requested bytes before any clone.

        Failed partial allocation is deliberately retained for owner-thread
        close, never reclaimed by a finalizer or silently reused.
        """
        with self.lock:
            self.guard()
            self.all_idle()
            if type(count) is not int or not 1 <= count <= 8:
                raise ValueError("Invocation slot count must be an integer in [1, 8]")
            if len(self.slots) != 1 or self.configuration_failed:
                raise RuntimeError("Invocation pool already configured or allocation failed")
            cap = _uint(max_requested_bytes, "max_requested_bytes")
            if not cap:
                raise ValueError("An explicit nonzero requested-byte cap is required")
            shared = {identity(base[key]) for key in immutable}
            groups = {}
            for value in base.values():
                groups.setdefault(identity(value), value)
            shared_bytes = mutable_bytes = 0
            for key, value in groups.items():
                amount = _uint(nbytes(value), "storage requested bytes")
                if not amount:
                    raise ValueError("Storage must have nonzero requested bytes")
                if key in shared:
                    shared_bytes = checked_sum(shared_bytes, amount)
                else:
                    mutable_bytes = checked_sum(mutable_bytes, amount)
            total = checked_sum(shared_bytes, checked_product(mutable_bytes, count))
            if total > cap:
                raise ValueError("Invocation pool exceeds requested-byte cap")
            bundles = [dict(base)]
            # Preflight covers every subsequent slot; the bounded total is
            # fixed before clone invokes any device allocator.
            try:
                for _ in range(1, count):
                    copies = {}
                    for key, value in groups.items():
                        if key not in shared:
                            copies[key] = clone(value)
                            self.pending_resources.append(copies[key])
                    bundles.append({name: value if identity(value) in shared else copies[identity(value)]
                                    for name, value in base.items()})
            except BaseException:
                self.configuration_failed = True
                raise
            self.bundles, self.shared_ids = bundles, shared
            self.slots += [InvocationSlot() for _ in range(count - 1)]
            self.extra_resources = self.pending_resources
            self.pending_resources = []
            self.requested_bytes = {"shared_weights": shared_bytes, "mutable_per_slot": mutable_bytes,
                                    "slot_count": count, "total": total, "cap": cap}
            return dict(self.requested_bytes)

    def capabilities(self):
        return {"slot_count": len(self.slots), "max_slot_count": 8,
                "submission": "synchronous_owner_thread_serial", "device_overlap": False,
                "experimental_opt_in": True,
                "requested_bytes": self.requested_bytes,
                "allocation_failed": self.configuration_failed}

    def legacy_idle(self):
        if self.configuration_failed:
            raise InvocationBusyError("Failed pool allocation requires explicit owner close")
        # Legacy paths do not expose per-range access declarations. Keep them
        # conservative while any safe invocation owns storage in this runner.
        self.all_idle()

    def close_slots(self):
        self.all_idle()
        for slot in self.slots:
            slot.close()


def checked_sum(a, b):
    _uint(a, "byte sum"); _uint(b, "byte sum")
    if b > _MAX - a:
        raise ValueError("Requested-byte sum overflows uint64")
    return a + b


def checked_product(a, b):
    _uint(a, "byte product"); _uint(b, "byte product")
    if a and b > _MAX // a:
        raise ValueError("Requested-byte product overflows uint64")
    return a * b


@dataclass(frozen=True)
class InvocationInput:
    node: str
    output: str


class InvocationDAG:
    """Bounded explicit host DAG, with serial synchronous runner submission.

    Edges refer only to earlier nodes, making cycles impossible at admission.
    No executor threads, native fences or implicit device concurrency exist.
    """
    def __init__(self, max_nodes=16):
        if type(max_nodes) is not int or not 1 <= max_nodes <= 64:
            raise ValueError("DAG capacity must be in [1, 64]")
        self.max_nodes, self.nodes = max_nodes, {}
        self.sealed = False
        self.thread = threading.get_ident()

    def _owner(self):
        if threading.get_ident() != self.thread:
            raise RuntimeError("Invocation DAG is owner-thread only")

    def add(self, name, runner, inputs, *, retain_output=False):
        self._owner()
        if self.sealed or not isinstance(name, str) or not name or name in self.nodes:
            raise ValueError("DAG sealed or node name invalid/duplicate")
        if len(self.nodes) >= self.max_nodes:
            raise InvocationBusyError("Bounded DAG capacity exceeded")
        inputs = dict(inputs)
        parents = {value.node for value in inputs.values() if isinstance(value, InvocationInput)}
        if any(parent not in self.nodes for parent in parents):
            raise ValueError("Dependency must refer to an earlier admitted node")
        if not callable(getattr(runner, "run_leased", None)):
            raise ValueError("DAG requires a real leased-invocation runner")
        # Pins retain the full producer ancestry until the last consumer lease
        # completes. Reject a topology whose own dependency closure can never
        # fit, rather than accepting a chain that can only be cancelled.
        ancestors = set(parents)
        for parent in parents:
            ancestors.update(self.nodes[parent]["ancestors"])
        needed = {}
        owners = {}
        for parent in ancestors:
            owner = self.nodes[parent]["runner"]
            needed[id(owner)] = needed.get(id(owner), 0) + 1
            owners[id(owner)] = owner
        needed[id(runner)] = needed.get(id(runner), 0) + 1
        owners[id(runner)] = runner
        for key, amount in needed.items():
            capability = getattr(owners[key], "invocation_capabilities", None)
            if not callable(capability) or amount > capability()["slot_count"]:
                raise InvocationBusyError("DAG dependency closure exceeds configured runner slot capacity")
        self.nodes[name] = {"runner":runner, "inputs":inputs, "parents":parents,
                            "ancestors":ancestors,
                            "remaining":0, "retain":bool(retain_output), "state":"queued",
                            "lease":None, "error":None}
        for parent in parents:
            self.nodes[parent]["remaining"] += 1

    def run_ready(self):
        self._owner()
        self.sealed = True
        progress = 0
        for node in self.nodes.values():
            if node["state"] != "queued":
                continue
            if any(self.nodes[p]["state"] in {"failed", "cancelled"} for p in node["parents"]):
                node["state"] = "cancelled"
                continue
            if any(self.nodes[p]["state"] != "completed" for p in node["parents"]):
                continue
            try:
                values = {name:self.nodes[value.node]["lease"].view(value.output)
                          if isinstance(value, InvocationInput) else value
                          for name,value in node["inputs"].items()}
                node["lease"] = node["runner"].run_leased(values)
            except InvocationBusyError:
                # No waiting on caller-owned leases: retry after explicit release.
                continue
            except BaseException as error:
                node["state"], node["error"] = "failed", error
                raise
            node["state"] = "completed"
            progress += 1
            for parent in node["parents"]:
                upstream = self.nodes[parent]
                upstream["remaining"] -= 1
                if not upstream["remaining"] and not upstream["retain"]:
                    upstream["lease"].release()
        return {"progress":progress, "states":{k:v["state"] for k,v in self.nodes.items()}}

    def result(self, name):
        self._owner()
        node = self.nodes[name]
        if node["state"] != "completed" or (not node["retain"] and node["remaining"] == 0
                                              and any(name in v["parents"] for v in self.nodes.values())):
            raise RuntimeError("No retained output for this node")
        if any(v["state"] == "queued" and name in v["parents"] for v in self.nodes.values()):
            raise InvocationBusyError("Dependency consumers have not submitted yet")
        node["lease"]._live()
        return node["lease"]

    def cancel(self):
        self._owner()
        self.sealed = True
        # Reverse topology releases children before producers. If completion
        # fails, leave the failing lease stored and propagate for explicit retry.
        for node in reversed(list(self.nodes.values())):
            if node["lease"] is not None:
                node["lease"].release()
            elif node["state"] == "failed":
                drain = getattr(node["runner"], "drain_failed_invocation", None)
                if not callable(drain):
                    raise RuntimeError("Failed invocation requires an explicit runner completion drain")
                drain()
            node["state"] = "cancelled"


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
