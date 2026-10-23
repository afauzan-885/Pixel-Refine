"""Production contracts and real runner methods with fake owner/device only.

Run this file directly with -B. No Taichi/engine package import, JIT or native
initialization occurs; module import names are temporarily backed by fakes.
"""
import ctypes
import importlib.util
from pathlib import Path
import sys
import threading
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


contract = load("device_invocation_pure", ROOT / "taichi_aot/device_invocation.py")
D, V, A = contract.DeviceViewDescriptor, contract.DeviceView, contract.Access


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.owner, self.device = object(), object()
        self.slots = []

    def tearDown(self):
        for slot in self.slots:
            if slot.token:
                slot.token.complete()
                while slot.token:
                    slot.token.release()

    def desc(self, storage=1, **kw):
        return D(self.owner, self.device, storage, kw.pop("capacity_bytes", 16), kw.pop("shape", (4,)), **kw)

    def slot(self):
        result = contract.InvocationSlot()
        self.slots.append(result)
        return result

    def test_checked_shape_layout_and_overflow(self):
        self.assertEqual(self.desc(shape=(2, 2)).strides_bytes, (8, 4))
        self.assertEqual(self.desc().byte_range, (0, 16))
        for kw in ({"shape": (-1,)}, {"shape": (True,)}, {"shape": (1 << 63,)},
                   {"offset_bytes": 4}, {"strides_bytes": (8,)}, {"dtype": "float16"},
                   {"capacity_bytes": 15}, {"shape": (0,)}):
            with self.assertRaises(ValueError): self.desc(**kw)

    def test_identity_and_stale_validation_before_binding(self):
        live = [True]
        def validate():
            if not live[0]: raise RuntimeError("stale")
        view = V(self.desc(), object(), validate)
        with self.assertRaises(ValueError): view._bind(object(), self.device)
        live[0] = False
        with self.assertRaisesRegex(RuntimeError, "stale"): view._bind(self.owner, self.device)

    def test_capacity_and_completion_prevent_early_reuse(self):
        slot = self.slot()
        token = slot.begin([A(self.desc(), True)], [object()])
        with self.assertRaises(contract.InvocationBusyError): slot.begin([], [])
        with self.assertRaises(RuntimeError): token.release()
        with self.assertRaises(contract.InvocationBusyError): slot.close()
        token.complete(); token.release(); slot.close()
        with self.assertRaises(RuntimeError): slot.begin([], [])

    def test_read_write_dependencies_independent_ranges_and_weights(self):
        x = self.desc()
        y = self.desc(storage=2)
        self.assertTrue(contract.conflicts(A(x, True), A(x)))
        self.assertFalse(contract.conflicts(A(x), A(x)))
        self.assertFalse(contract.conflicts(A(x, True), A(y, True)))
        low = self.desc(shape=(2,), capacity_bytes=32)
        high = self.desc(shape=(2,), capacity_bytes=32, offset_bytes=8)
        overlap = self.desc(shape=(2,), capacity_bytes=32, offset_bytes=4)
        self.assertFalse(contract.conflicts(A(low, True), A(high, True)))
        self.assertTrue(contract.conflicts(A(low, True), A(overlap)))
        with self.assertRaises(ValueError): high.require_flat_binding()
        with self.assertRaises(ValueError): A(x, True, True)
        first, second, third = self.slot(), self.slot(), self.slot()
        t = first.begin([A(x, True)], [])
        with self.assertRaises(contract.InvocationBusyError): second.begin([A(x)], [])
        u = third.begin([A(y, True)], []); u.complete(); u.release()
        t.complete()
        u = second.begin([A(x)], []); u.complete(); u.release(); t.release()

    def test_submission_cancellation_waits_before_reuse(self):
        events = []
        api = contract.SerialDeviceInvocations(lambda: None, lambda: events.append("wait"))
        self.slots.append(api.slot)
        def execute():
            events.append("execute")
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt): api.submit({}, [], [], execute, lambda n,v: v)
        self.assertEqual(events, ["execute", "wait"])
        self.assertIsNone(api.slot.token)

    def test_failed_completion_retains_resources_until_explicit_drain(self):
        fail = [True]
        def sync():
            if fail[0]: raise RuntimeError("completion unknown")
        api = contract.SerialDeviceInvocations(lambda: None, sync)
        self.slots.append(api.slot)
        resource = object()
        with self.assertRaises(RuntimeError): api.submit({}, [], [resource], lambda: {}, lambda n,v: v)
        self.assertIn(resource, api.slot.token.resources)
        with self.assertRaises(RuntimeError): api.drain_failed()
        fail[0] = False; api.drain_failed()
        self.assertIsNone(api.slot.token)

    def test_lease_consumer_failure_waits_and_explicit_release(self):
        events = []
        api = contract.SerialDeviceInvocations(lambda: None, lambda: events.append("wait"))
        self.slots.append(api.slot)
        storage = object(); view = V(self.desc(), storage, lambda: None)
        lease = api.submit({}, [A(view.descriptor, True)], [], lambda: {"x": storage}, lambda n,v: view)
        with self.assertRaises(ValueError): lease.consume(lambda values: (_ for _ in ()).throw(ValueError("consumer")))
        self.assertEqual(events, ["wait", "wait"])
        lease.release(); lease.release()
        with self.assertRaises(RuntimeError): lease.view("x")
        self.assertIsNone(api.slot.token)

    def test_downstream_pin_outlives_original_lease_release(self):
        producer = contract.SerialDeviceInvocations(lambda: None, lambda: None)
        downstream = contract.SerialDeviceInvocations(lambda: None, lambda: None)
        self.slots.extend([producer.slot, downstream.slot])
        storage = object(); view = V(self.desc(), storage, lambda: None)
        lease = producer.submit({}, [A(view.descriptor, True)], [], lambda: {"x": storage}, lambda n,v: view)
        borrowed = lease.view("x")
        def execute():
            lease.release()
            self.assertIsNotNone(producer.slot.token)
            return {}
        result = downstream.submit({"x": borrowed}, [A(borrowed.descriptor)], [], execute, lambda n,v: v)
        self.assertIsNotNone(producer.slot.token)
        result.release()
        self.assertIsNone(producer.slot.token)
        with self.assertRaises(RuntimeError): borrowed._pin()

    def test_consumer_cannot_reenter_release_or_drain_its_live_lease(self):
        api = contract.SerialDeviceInvocations(lambda: None, lambda: None)
        self.slots.append(api.slot)
        view = V(self.desc(), object(), lambda: None)
        lease = api.submit({}, [], [], lambda: {"x":view._storage}, lambda n,v: view)
        def consume(values):
            with self.assertRaises(contract.InvocationBusyError): lease.release()
            api.drain_failed()
            self.assertIsNotNone(api.slot.token)
        lease.consume(consume); lease.release()

    def test_lease_completion_error_requires_retry_release_not_orphan_drain(self):
        fail = [False]
        def sync():
            if fail[0]: raise RuntimeError("wait failed")
        api = contract.SerialDeviceInvocations(lambda: None, sync)
        self.slots.append(api.slot)
        lease = api.submit({}, [], [], lambda: {}, lambda n,v: v)
        fail[0] = True
        with self.assertRaises(RuntimeError): lease.consume(lambda values: None)
        api.drain_failed()
        self.assertIsNotNone(api.slot.token)
        with self.assertRaises(RuntimeError): lease.release()
        fail[0] = False; lease.release()
        self.assertIsNone(api.slot.token)


class Array:
    def __init__(self, dtype="float32", shape=(4,)):
        self.dtype, self.shape, self.arr = dtype, tuple(shape), object()
    def from_numpy(self, value): pass
    def to_numpy(self): return np.zeros(self.shape, np.float32)


class Buffer:
    def __init__(self, engine, handle, shape=(4,)):
        self.engine, self.handle, self.shape = engine, handle, shape
        self.size_bytes = 4 * int(np.prod(shape))
        self.dtype, self.is_vector = np.float32, False
        self.engine_generation = engine._generation
    def _require_live(self, operation):
        if self.handle is None or self.engine_generation != self.engine._generation or not self.engine.runtime:
            raise RuntimeError("stale buffer")
        return self.engine.runtime, self.handle
    def destroy(self): self.handle = None


class Engine:
    def __init__(self):
        self._lock = threading.RLock()
        self.runtime, self._generation, self.arch, self.device_id = 17, 1, "vulkan", 0
        self._destroyed, self.events = False, []
    def _assert_native_context_owner(self, op): self.events.append("guard")
    def sync(self): self.events.append("sync")
    def last_error(self): return ""


class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = SimpleNamespace(prog=object())
        fake = ModuleType("taichi")
        class Annotation:
            def __call__(self, *args, **kw): return self
            def __getattr__(self, name): return self
        fake.func = fake.kernel = lambda f: f
        fake.f32, fake.i32 = "float32", "int32"
        fake.template = Annotation(); fake.types = Annotation()
        fake.Ndarray, fake.ndarray = Array, Array
        fake.sync = lambda: None
        fake.lang = SimpleNamespace(impl=SimpleNamespace(get_runtime=lambda: cls.runtime))
        cls.fake_ti = fake
        fusions = ModuleType("fusions")
        fusions._fused_mul_clip_kernel = fusions._weightnet_gate_flat_kernel = lambda *a: None
        engine = ModuleType("engine"); engine.TaichiGPUBuffer = Buffer
        cls.mapping = {
            "taichi": fake,
            "taichi_vision.taichi_aot.device_invocation": contract,
            "taichi_vision.taichi_aot.fused_mul_clip": fusions,
            "taichi_vision.taichi_aot.weightnet_gate_fusions": fusions,
            "taichi_vision.taichi_aot.engine": engine,
        }
        with patch.dict(sys.modules, cls.mapping):
            cls.jit_module = load("native_graph_fake_device", ROOT / "taichi_aot/onnx_native_graph.py")
            cls.aot_module = load("resident_graph_fake_device", ROOT / "taichi_algorithm/denoising/onnx_resident_aot.py")

    def setUp(self):
        self.patch = patch.dict(sys.modules, self.mapping); self.patch.start()
        self.runners = []

    def tearDown(self):
        for runner in self.runners:
            token = runner._invocations.slot.token
            if token:
                token.complete()
                while runner._invocations.slot.token: token.release()
        self.patch.stop()

    def resident(self, engine=None, handle=2):
        runner = self.aot_module.ResidentONNXGraph.__new__(self.aot_module.ResidentONNXGraph)
        runner.engine = engine or Engine()
        runner._lock = threading.RLock()
        runner._view_owner = (id(runner.engine), runner.engine.runtime, runner.engine._generation)
        runner._view_device = (runner.engine.arch, runner.engine.device_id, runner.engine.runtime)
        runner._view_thread = threading.get_ident()
        runner._invocations = contract.SerialDeviceInvocations(runner._view_guard, runner._view_sync, runner.engine._lock)
        runner.metadata = {"inputs": ["x"], "outputs": ["y"], "shapes": {"x": [4], "y": [2,2]},
                           "bindings": {"x": "x", "y": "y"}, "constants": [], "graph": "graph"}
        runner.buffers = {"y": Buffer(runner.engine, handle)}
        runner.module = SimpleNamespace(run=lambda *args, **kw: runner.engine.events.append("run"))
        self.runners.append(runner)
        return runner

    def test_real_resident_lease_blocks_all_legacy_entrypoints_and_close(self):
        runner = self.resident()
        value = Buffer(runner.engine, 1)
        lease = runner.run_leased({"x": runner.device_view(value)})
        for call in (lambda: runner.run_device({"x":value}), lambda: runner.run_device_fast(),
                     lambda: runner.prepare_static_device_bindings({"x":value}),
                     lambda: runner.run(input_feed={"x":value}), runner.close):
            with self.assertRaises(contract.InvocationBusyError): call()
        self.assertEqual(lease.descriptors["y"].shape, (2,2))
        self.assertEqual(lease.consume(lambda result: result["y"].handle), 2)
        lease.release()
        self.assertEqual(runner.run_device({"x":value})["y"].handle, 2)
        runner.close(); runner.close()

    def test_real_resident_downstream_without_copy_and_dependency_release(self):
        first = self.resident()
        second = self.resident(first.engine, handle=3)
        lease = first.run_leased({"x": first.device_view(Buffer(first.engine, 1))})
        second.module.run = lambda *args, **kw: self.assertIs(kw["x"], first.buffers["y"])
        result = second.run_leased({"x": lease.view("y")})
        result.release(); lease.release()

    def test_resident_weightnet_scalar_alpha_and_logical_weight_map(self):
        # Match the actual WeightNet-shaped source fixture in
        # test_onnx_resident_aot.py: rank-4 map, scalar ReduceMean alpha.
        runner = self.resident()
        shape = [1, 1, 4, 4]
        runner.metadata = {"inputs": ["ref_img", "support_img"], "outputs": ["weight_map", "alpha"],
            "shapes": {"ref_img": shape, "support_img": shape, "weight_map": shape, "alpha": []},
            "bindings": {name:name for name in ("ref_img", "support_img", "weight_map", "alpha")},
            "constants": [], "graph": "graph"}
        runner.buffers = {"weight_map":Buffer(runner.engine, 2, (16,)), "alpha":Buffer(runner.engine, 3, (1,))}
        views = {name:runner.device_view(Buffer(runner.engine, handle, (16,)), shape=shape)
                 for name,handle in (("ref_img", 4), ("support_img", 5))}
        with runner.run_leased(views) as lease:
            descriptors = lease.descriptors
            self.assertEqual(descriptors["alpha"].shape, ())
            self.assertEqual(descriptors["alpha"].byte_range, (0,4))
            self.assertEqual(descriptors["weight_map"].shape, (1,1,4,4))
            self.assertEqual(descriptors["weight_map"].byte_range, (0,64))
            lease.consume(lambda values: self.assertEqual(values["alpha"].shape, (1,)))

    def test_real_resident_rejects_stale_offsets_owner_and_wrong_thread(self):
        runner = self.resident(); buffer = Buffer(runner.engine, ctypes.c_void_p(1))
        with self.assertRaises(ValueError): runner.device_view(buffer, offset_bytes=4)
        with self.assertRaises(ValueError): runner.device_view(buffer, shape=(2,))
        view = runner.device_view(buffer)
        runner.engine._generation += 1
        with self.assertRaises(RuntimeError): runner.run_leased({"x": view})
        runner.engine._generation -= 1
        errors = []
        def work():
            try: runner.run_leased({"x":view})
            except RuntimeError as error: errors.append(str(error))
        thread = threading.Thread(target=work); thread.start(); thread.join()
        self.assertIn("wrong thread", errors[0])
        buffer.handle = None
        with self.assertRaises(RuntimeError): runner.run_leased({"x":view})

    def test_real_resident_engine_close_invalidates_access_without_native_work(self):
        runner = self.resident()
        lease = runner.run_leased({"x":runner.device_view(Buffer(runner.engine, 1))})
        previous = list(runner.engine.events)
        runner.engine._destroyed = True
        with self.assertRaises(RuntimeError): lease.consume(lambda values: self.fail("must not expose stale handles"))
        with self.assertRaises(RuntimeError): lease.release()
        self.assertEqual(runner.engine.events, previous)
        runner.engine._destroyed = False
        lease.release()

    def jit(self):
        runner = self.jit_module.NativeGraph.__new__(self.jit_module.NativeGraph)
        runner._lock, runner._allocation_lock = threading.Lock(), threading.Lock()
        runner._allocated, runner._view_context, runner._view_inputs = False, None, {}
        runner._invocations = contract.SerialDeviceInvocations(runner._view_guard, self.fake_ti.sync)
        runner.inputs, runner.outputs = ["x"], ["y"]
        runner.shapes, runner.aliases, runner.alias_roots = {"x": (4,), "y": (4,)}, {}, {}
        runner.constants, runner.runtime_constant_names, runner.steps = {}, set(), []
        runner.buffer_plan, runner.buffers, runner.scratch = {"x":0,"y":1}, {}, {}
        self.runners.append(runner)
        return runner

    def test_real_native_graph_lease_and_provenance(self):
        runner = self.jit()
        with self.assertRaises(ValueError): runner.device_view(Array())
        view = runner.allocate_device_view((2,2))
        runner.consume_input(view, lambda value: self.assertEqual(value.shape, (4,)))
        lease = runner.run_leased({"x":view})
        with self.assertRaises(contract.InvocationBusyError): runner.run({"x": np.zeros(4,np.float32)})
        with self.assertRaises(contract.InvocationBusyError): runner.close()
        lease.release(); runner.close()
        with self.assertRaises(RuntimeError): view._bind(view.descriptor.owner, view.descriptor.device)

    def test_real_native_graph_downstream_and_runtime_reset(self):
        first, second = self.jit(), self.jit()
        lease = first.run_leased({"x": first.allocate_device_view((4,))})
        downstream = second.run_leased({"x":lease.view("y")})
        downstream.release(); lease.release()
        view = first.allocate_device_view((4,))
        old = self.runtime.prog
        try:
            self.runtime.prog = object()
            with self.assertRaises(RuntimeError): first.run_leased({"x":view})
        finally: self.runtime.prog = old


if __name__ == "__main__":
    unittest.main()
