"""Temporary: bisect the first RAFT node that diverges from ONNX Runtime.

Earlier versions of this script had two defects, both fixed here:
  * every intermediate was declared FLOAT, so ONNX Runtime refused any cut whose
    output was really int64 or bool — those `None` results were load failures being
    read as agreement;
  * a full prefix sweep is quadratic and never finished.

A cut now declares one output with the dtype the plan assigned it, and the search is
a bisection: about log2(nodes) runs instead of 4326.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from taichi_vision.taichi_algorithm.neural.universal import plan_wire  # noqa: E402
from taichi_vision.taichi_algorithm.neural.universal.plan import Plan  # noqa: E402

ELEMENT_TYPE = {
    "f32": onnx.TensorProto.FLOAT,
    "i32": onnx.TensorProto.INT32,
    "bool": onnx.TensorProto.INT32,
    "i64": onnx.TensorProto.INT64,
}


def main() -> int:
    import taichi.taichi_python as native_module

    model_bytes = Path(sys.argv[1]).read_bytes()
    plan = Plan.from_model_bytes(model_bytes)
    nodes = plan.nodes
    template = onnx.load_model_from_string(model_bytes)

    rng = np.random.default_rng(3)
    feeds = {
        "0": rng.uniform(0, 1, (1, 3, 360, 480)).astype(np.float32),
        "1": rng.uniform(0, 1, (1, 3, 360, 480)).astype(np.float32),
    }
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1

    def cut_bytes(upto: int, output_name: str, dtype: str) -> bytes:
        model = onnx.load_model_from_string(template.SerializeToString())
        graph = model.graph
        for node in list(graph.node)[upto + 1 :]:
            graph.node.remove(node)
        while len(graph.output):
            graph.output.pop()
        graph.output.append(
            onnx.helper.make_tensor_value_info(output_name, ELEMENT_TYPE[dtype], None)
        )
        return model.SerializeToString()

    def error_at(upto: int) -> float | None:
        node = nodes[upto]
        name = node.outputs[0]
        dtype = plan.dtypes.get(name)
        if dtype != "f32":
            return None
        blob_model = cut_bytes(upto, name, dtype)
        try:
            reference = ort.InferenceSession(
                blob_model, options, providers=["CPUExecutionProvider"]
            ).run(None, feeds)[0]
        except Exception:
            return None
        cut_plan = Plan.from_model_bytes(blob_model)
        blob = plan_wire.encode_plan(cut_plan, {k: v.shape for k, v in feeds.items()})
        session = native_module.NeuralSession(blob, backend="cpu")
        for constant, value in plan_wire.constant_values(cut_plan).items():
            session.set_constant(constant, np.ascontiguousarray(value))
        for key, value in feeds.items():
            session.set_input(key, np.ascontiguousarray(value))
        if session.missing_ops:
            return None
        produced = session.run()
        if name not in produced:
            return None
        got = np.asarray(produced[name]).ravel().astype(np.float64)
        want = np.asarray(reference).ravel().astype(np.float64)
        if got.shape != want.shape:
            return float("inf")
        return float(np.abs(got - want).max()) / max(float(np.abs(want).max()), 1e-12)

    good, bad, step = 0, None, 30
    while good < len(nodes) - 1:
        probe = min(good + step, len(nodes) - 1)
        value = error_at(probe)
        print(f"probe {probe:5d} {nodes[probe].op:22s} rel={value}", flush=True)
        if value is not None and value > 1e-3:
            bad = probe
            break
        good = probe
        step *= 2
    if bad is None:
        print("no bad prefix found; the graph agrees end to end")
        return 0

    while bad - good > 1:
        middle = (good + bad) // 2
        value = error_at(middle)
        print(f"  bisect {middle:5d} {nodes[middle].op:22s} rel={value}", flush=True)
        if value is not None and value > 1e-3:
            bad = middle
        else:
            good = middle

    node = nodes[bad]
    print(f"\nfirst bad node {bad}: {node.op} rel={error_at(bad)}")
    print(f"  attrs   {node.attrs}")
    print(f"  inputs  {node.inputs}")
    print(f"  outputs {node.outputs}")
    for name in node.inputs:
        print(f"    in  {name:30s} {plan.dtypes.get(name)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
