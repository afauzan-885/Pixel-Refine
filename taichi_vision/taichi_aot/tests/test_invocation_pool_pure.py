"""Bounded pool/DAG tests using actual adapters and verified fake-only harness."""
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

path = Path(__file__).with_name("test_device_invocation_pure.py")
spec = importlib.util.spec_from_file_location("invocation_pool_harness", path)
harness = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = harness
spec.loader.exec_module(harness)
C = harness.contract


class PoolRunnerTests(harness.RunnerTests):
    """Inherited D1 regressions also run against the updated production adapter."""
    def resident_pool(self, count=2):
        runner = self.resident()
        runner.metadata["constants"] = ["w"]
        runner.buffers["w"] = harness.Buffer(runner.engine, 80)
        self.install_allocator(runner.engine)
        runner.configure_invocation_slots(count, max_requested_bytes=1024)
        return runner

    def install_allocator(self, engine):
        engine.allocations = []
        def allocate(shape, **kw):
            value = harness.Buffer(engine, 1000 + len(engine.allocations), tuple(shape))
            engine.allocations.append(value)
            return value
        engine.allocate = allocate

    def inputs(self, runner, handle=1):
        return {"x":runner.device_view(harness.Buffer(runner.engine, handle))}

    def test_resident_slots_isolate_mutable_outputs_share_weights_and_bound_capacity(self):
        runner = self.resident_pool()
        weight = runner.buffers["w"]
        def execute(*args, **values):
            self.assertIs(values["w"], weight)
            values["y"].stamp = values["x"].handle
        runner.module.run = execute
        first = runner.run_leased(self.inputs(runner,1))
        second = runner.run_leased(self.inputs(runner,9))
        self.assertNotEqual(first.descriptors["y"].storage, second.descriptors["y"].storage)
        self.assertEqual(first.consume(lambda values:values["y"].stamp), 1)
        self.assertEqual(second.consume(lambda values:values["y"].stamp), 9)
        with self.assertRaises(C.InvocationBusyError): runner.run_leased(self.inputs(runner))
        with self.assertRaises(C.InvocationBusyError): runner.close()
        first.release()
        with self.assertRaises(C.InvocationBusyError): runner.run_device({"x":harness.Buffer(runner.engine,1)})
        third = runner.run_leased(self.inputs(runner,7))
        self.assertEqual(third.consume(lambda values:values["y"].stamp), 7)
        third.release(); second.release()
        capabilities = runner.invocation_capabilities()
        self.assertEqual(capabilities["requested_bytes"]["total"], 48)
        self.assertFalse(capabilities["device_overlap"])
        runner.close()
        self.assertTrue(all(value.handle is None for value in runner.engine.allocations))

    def test_resident_cap_and_overflow_reject_before_any_clone(self):
        runner = self.resident(); self.install_allocator(runner.engine)
        for count, cap in ((2, 31), (9, 9999), (True,9999), (2,0), (2,1<<64)):
            with self.assertRaises(ValueError): runner.configure_invocation_slots(count,max_requested_bytes=cap)
        self.assertEqual(runner.engine.allocations, [])
        with self.assertRaises(ValueError): runner.configure_invocation_slots(2,max_requested_bytes=1024,mode="parallel")
        self.assertEqual(runner.invocation_capabilities()["slot_count"],1)

    def test_partial_allocation_failure_retains_known_resource_until_explicit_close(self):
        runner = self.resident(); self.install_allocator(runner.engine)
        allocate = runner.engine.allocate
        def failing(shape, **kw):
            if runner.engine.allocations:
                raise MemoryError("second slot allocation failed")
            return allocate(shape,**kw)
        runner.engine.allocate = failing
        with self.assertRaises(MemoryError): runner.configure_invocation_slots(3,max_requested_bytes=1024)
        held = runner.engine.allocations[0]
        self.assertIsNotNone(held.handle)
        self.assertTrue(runner.invocation_capabilities()["allocation_failed"])
        with self.assertRaises(C.InvocationBusyError): runner.run_leased(self.inputs(runner))
        with self.assertRaises(C.InvocationBusyError): runner.run_device({"x":harness.Buffer(runner.engine,1)})
        runner.close()
        self.assertIsNone(held.handle)

    def test_drain_failed_secondary_slot_keeps_primary_and_upstream_safe(self):
        runner = self.resident_pool()
        first = runner.run_leased(self.inputs(runner))
        original = runner.module.run
        def fail(*args,**kw): raise ValueError("dispatch failed")
        runner.module.run = fail
        runner.engine.sync_errors = ["secondary completion failure"]
        with self.assertRaisesRegex(RuntimeError,"secondary completion failure"):
            runner.run_leased(self.inputs(runner,2))
        self.assertIsNotNone(runner._invocations.slots[1].token)
        runner.drain_failed_invocation()
        self.assertIsNone(runner._invocations.slots[1].token)
        self.assertIsNotNone(runner._invocations.slots[0].token)
        runner.module.run = original
        second = runner.run_leased(self.inputs(runner,3)); second.release(); first.release()

    def test_native_graph_pool_preserves_aliases_scratch_and_shared_constants(self):
        runner = self.jit()
        runner.constants["w"] = np.ones(4,np.float32)
        runner.runtime_constant_names.add("w")
        runner.shapes["w"] = (4,)
        runner.shapes["y_alias"] = (4,)
        runner.aliases["y_alias"] = "y"
        runner.buffer_plan["y_alias"] = 1
        runner.allocate()
        scratch = harness.Array("float32", (8,))
        runner.scratch = {"sum0":scratch,"sum1":scratch}
        stats = runner.configure_invocation_slots(2,max_requested_bytes=1024)
        self.assertEqual(stats["total"],152)
        bundles = runner._invocations.bundles
        self.assertIs(bundles[0][("buffer","w")],bundles[1][("buffer","w")])
        self.assertIs(bundles[1][("buffer","y")],bundles[1][("buffer","y_alias")])
        self.assertIsNot(bundles[0][("dummy","dummy")],bundles[1][("dummy","dummy")])
        self.assertIs(bundles[1][("scratch","sum0")],bundles[1][("scratch","sum1")])
        self.assertIsNot(bundles[0][("scratch","sum0")],bundles[1][("scratch","sum0")])
        view = runner.allocate_device_view((4,))
        first = runner.run_leased({"x":view}); second = runner.run_leased({"x":view})
        self.assertNotEqual(first.descriptors["y"].storage,second.descriptors["y"].storage)
        with self.assertRaises(C.InvocationBusyError): runner.run_leased({"x":view})
        first.release(); second.release(); runner.close()

    def test_native_graph_budget_preflight_does_not_allocate_first_slot(self):
        runner = self.jit()
        with self.assertRaises(ValueError): runner.configure_invocation_slots(2,max_requested_bytes=1)
        self.assertFalse(runner._allocated)

    def test_dag_real_resident_dependency_chain_pin_result_and_cancel(self):
        runner = self.resident_pool()
        dag = C.InvocationDAG(max_nodes=2)
        dag.add("producer",runner,self.inputs(runner))
        dag.add("consumer",runner,{"x":C.InvocationInput("producer","y")})
        with self.assertRaises(C.InvocationBusyError): dag.add("extra",runner,self.inputs(runner))
        state = dag.run_ready()
        self.assertEqual(state["states"],{"producer":"completed","consumer":"completed"})
        with self.assertRaises(RuntimeError): dag.result("producer")
        result = dag.result("consumer")
        self.assertTrue(all(slot.token for slot in runner._invocations.slots))
        result.release()
        self.assertTrue(all(slot.token is None for slot in runner._invocations.slots))
        with self.assertRaises(RuntimeError): dag.result("consumer")
        dag.cancel()

    def test_dag_branch_backpressure_cancel_failure_and_retry(self):
        runner = self.resident_pool()
        dag = C.InvocationDAG()
        dag.add("root",runner,self.inputs(runner))
        dag.add("left",runner,{"x":C.InvocationInput("root","y")})
        dag.add("right",runner,{"x":C.InvocationInput("root","y")})
        state = dag.run_ready()
        self.assertEqual(state["states"]["right"],"queued")
        dag.result("left").release()
        self.assertEqual(dag.run_ready()["states"]["right"],"completed")
        runner.engine.sync_errors = ["cancel wait failed"]
        with self.assertRaisesRegex(RuntimeError,"cancel wait failed"): dag.cancel()
        self.assertTrue(any(slot.token for slot in runner._invocations.slots))
        dag.cancel()
        self.assertTrue(all(slot.token is None for slot in runner._invocations.slots))

    def test_dag_native_graph_chain_and_invalid_edges(self):
        runner = self.jit(); runner.configure_invocation_slots(2,max_requested_bytes=1024)
        dag = C.InvocationDAG()
        with self.assertRaises(ValueError): dag.add("bad",runner,{"x":C.InvocationInput("future","y")})
        dag.add("root",runner,{"x":runner.allocate_device_view((4,))})
        dag.add("child",runner,{"x":C.InvocationInput("root","y")})
        with self.assertRaises(C.InvocationBusyError):
            dag.add("too_deep",runner,{"x":C.InvocationInput("child","y")})
        self.assertEqual(dag.run_ready()["progress"],2)
        dag.result("child").release(); dag.cancel()
        with self.assertRaises(ValueError): dag.add("later",runner,{})

    def test_dag_failed_submission_cancel_drains_orphaned_slot(self):
        runner = self.resident_pool()
        original = runner.module.run
        calls = []
        def execute(*args,**kw):
            calls.append(True)
            if len(calls) == 2:
                runner.engine.sync_errors = ["failed child wait"]
                raise ValueError("failed child dispatch")
            return original(*args,**kw)
        runner.module.run = execute
        dag = C.InvocationDAG()
        dag.add("root",runner,self.inputs(runner))
        dag.add("child",runner,{"x":C.InvocationInput("root","y")})
        with self.assertRaisesRegex(RuntimeError,"failed child wait"): dag.run_ready()
        self.assertTrue(any(slot.token for slot in runner._invocations.slots))
        dag.cancel()
        self.assertTrue(all(slot.token is None for slot in runner._invocations.slots))


if __name__ == "__main__":
    unittest.main()
