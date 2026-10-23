"""Deferred real-device lease tests. Not run in the no-compilation session.

The NativeGraph case can trigger JIT; resident case requires an existing
matching artifact. Enable only in a separately authorized dynamic session.
"""
import os
import unittest


@unittest.skipUnless(os.environ.get("PIXEL_REFINE_RUN_DEVICE_LEASE_TESTS") == "1",
                     "Real-device/JIT gate explicitly deferred")
class RealDeviceLeaseTests(unittest.TestCase):
    def test_native_two_storage_slots_and_serial_dependency_dag(self):
        import numpy as np
        from onnx import TensorProto, helper
        import taichi as ti
        from taichi_vision.taichi_aot.onnx_native_graph import NativeGraph
        from taichi_vision.taichi_aot.device_invocation import InvocationDAG, InvocationInput
        ti.init(arch=ti.cpu)
        graph = helper.make_graph([helper.make_node("Add", ["x","x"], ["y"])], "pool",
            [helper.make_tensor_value_info("x",TensorProto.FLOAT,[4])],
            [helper.make_tensor_value_info("y",TensorProto.FLOAT,[4])])
        runner = NativeGraph(graph,[helper.make_opsetid("",13)])
        runner.configure_invocation_slots(2,max_requested_bytes=1024*1024)
        view = runner.allocate_device_view((4,))
        runner.consume_input(view,lambda value:value.from_numpy(np.arange(4,dtype=np.float32)))
        dag = InvocationDAG()
        dag.add("first",runner,{"x":view})
        dag.add("second",runner,{"x":InvocationInput("first","y")})
        self.assertEqual(dag.run_ready()["progress"],2)
        with dag.result("second") as output:
            actual = output.consume(lambda values:values["y"].to_numpy())
            np.testing.assert_array_equal(actual,4*np.arange(4,dtype=np.float32))
        dag.cancel(); runner.close()

    def test_native_graph_reshape_downstream_and_busy(self):
        import numpy as np
        import onnx
        from onnx import TensorProto, helper, numpy_helper
        import taichi as ti
        from taichi_vision.taichi_aot.onnx_native_graph import NativeGraph
        from taichi_vision.taichi_aot.device_invocation import InvocationBusyError
        ti.init(arch=ti.cpu)
        shape = numpy_helper.from_array(np.array([2, 2], np.int64), "shape")
        graph = helper.make_graph([helper.make_node("Reshape", ["x", "shape"], ["y"])],
            "view", [helper.make_tensor_value_info("x", TensorProto.FLOAT, [4])],
            [helper.make_tensor_value_info("y", TensorProto.FLOAT, [2, 2])], [shape])
        first = NativeGraph(graph, [helper.make_opsetid("", 13)])
        second = NativeGraph(graph, [helper.make_opsetid("", 13)])
        view = first.allocate_device_view((4,))
        first.consume_input(view, lambda buffer: buffer.from_numpy(np.arange(4, dtype=np.float32)))
        with first.run_leased({"x": view}) as output:
            with self.assertRaises(InvocationBusyError): first.run({"x": np.zeros(4,np.float32)})
            with second.run_leased({"x": output.view("y")}) as result:
                actual = result.consume(lambda values: values["y"].to_numpy())
                np.testing.assert_array_equal(actual.reshape(-1), np.arange(4, dtype=np.float32))
        first.close(); second.close()

    def test_resident_matching_artifact_slot_and_native_completion(self):
        path = os.environ.get("PIXEL_REFINE_LEASE_TEST_RESIDENT_ARTIFACT")
        if not path:
            self.skipTest("Provide a matching simple FP32 resident artifact")
        import numpy as np
        from taichi_vision.taichi_algorithm.denoising.onnx_resident_aot import ResidentONNXGraph
        from taichi_vision.taichi_aot.device_invocation import InvocationBusyError
        runner = ResidentONNXGraph(path)
        buffers = {}
        try:
            for item in runner.get_inputs():
                buffers[item.name] = runner.engine.upload(np.zeros(max(1, int(np.prod(item.shape))), np.float32), is_vector=False)
            with runner.run_leased({name: runner.device_view(value) for name,value in buffers.items()}) as output:
                with self.assertRaises(InvocationBusyError): runner.run_device(buffers)
                self.assertEqual(set(output.descriptors), {item.name for item in runner.get_outputs()})
                output.consume(lambda values: {name: value.to_numpy() for name,value in values.items()})
        finally:
            runner.close()
            for value in buffers.values(): value.destroy()


if __name__ == "__main__":
    unittest.main()
