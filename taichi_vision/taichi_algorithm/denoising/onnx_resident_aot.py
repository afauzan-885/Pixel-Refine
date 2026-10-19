"""Static ONNX graphs on the application's existing Taichi C API runtime.

The compiler specializes the admitted NativeGraph kernels. Runtime execution
uses AOTEngine buffers throughout; Python/JIT ndarray handles are never mixed
with C API allocation handles.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import inspect
import io
import json
import math
from pathlib import Path
import tempfile
import textwrap
import threading
import zipfile

import numpy as np


GRAPH_NAME = "deno_onnx_resident_f32_v1"


def compile_resident_onnx(model_bytes, output_path, backend="cuda", *, patch_tools=False):
    """Compile an admitted static FP32 model, without changing engine.py."""
    import onnx
    import taichi as ti
    from taichi_vision.taichi_aot.onnx_native_graph import NativeGraph
    from taichi_vision.taichi_algorithm.aot_py.aot_artifact import archive_module

    model = onnx.load_model_from_string(model_bytes)
    plan = NativeGraph(
        model.graph,
        model.opset_import,
        enable_conv_gelu_fusion=True,
        enable_concat_gather=True,
        enable_weightnet_gate_fusion=True,
        enable_mul_clip_fusion=True,
        enable_weightnet_sigmoid_product_clip_fusion=True,
        enable_weightnet_pow2_sub_clip_sqrt_fusion=True,
        enable_weightnet_stats_tanh_fusion=True,
        enable_weightnet_stats_tanh_algebraic_simplification=True,
        enable_constant_pow2_mul_lowering=True,
        enable_weightnet_pow2_reduce_mean_fusion=(backend == "cuda"),
        enable_weightnet_full_range_slice_alias=True,
        enable_weightnet_concat_conv_gelu_fusion=True,
        enable_weightnet_conv_transpose_mul_clip_fusion=True,
        enable_weightnet_abs_conv_fusion=True,
        enable_weightnet_pool_abs_concat_fusion=True,
        enable_weightnet_fused_heads_and_gate_fusion=True,
        enable_weightnet_phase_gate_concat23_fusion=True,
    )
    arch = {"cpu": ti.cpu, "cuda": ti.cuda, "vulkan": ti.vulkan,
            "opengl": ti.opengl}[backend]
    ti.init(arch=arch, offline_cache=False)
    if ti.lang.impl.current_cfg().arch != arch:
        raise RuntimeError(f"Compiler did not initialize requested backend {backend}")
    plan.backend = backend
    bindings, sizes, symbols = {}, {}, {}

    def buffer(name, elements):
        if name not in symbols:
            symbols[name] = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, name, ti.f32, ndim=1)
            sizes[name] = max(1, int(elements))
        return symbols[name]

    constants = {}
    # Inputs have independent bindings: liveness slots must never overwrite
    # the caller's borrowed input image/patch allocations.
    for index, name in enumerate(plan.inputs):
        bindings[name] = f"input_{index}"
        buffer(bindings[name], math.prod(plan.shapes[name]))
    for index, name in enumerate(sorted(plan.runtime_constant_names)):
        bindings[name] = f"constant_{index}"
        constants[bindings[name]] = np.ascontiguousarray(
            plan.constants[name], dtype=np.float32
        ).reshape(-1)
        buffer(bindings[name], constants[bindings[name]].size)
    for name in plan.shapes:
        if name in plan.aliases or name in bindings or name in plan.constants:
            continue
        if name not in plan.buffer_plan:
            continue
        bindings[name] = f"slot_{plan.buffer_plan[name]}"
        buffer(bindings[name], math.prod(plan.shapes[name]))
    for name in plan.shapes:
        if name in plan.aliases:
            root = plan.alias_roots.get(name, name)
            if root in bindings:
                bindings[name] = bindings[root]
    plan.buffers = {name: symbols[binding] for name, binding in bindings.items() if binding in symbols}
    plan.dummy = buffer("dummy", 1)
    plan.scratch = {}
    for step in plan.steps:
        if (step["op"] == "ReduceMean"
                and len(step.get("axes", [])) == len(plan.shapes[step["inputs"][0]])):
            elements = math.prod(plan.shapes[step["inputs"][0]])
            key = f"scratch_{(elements + 255) // 256}"
            plan.scratch[step["output"]] = buffer(key, (elements + 255) // 256)

    sources, calls, used = [], [], set()
    symbol_names = {id(value): name for name, value in symbols.items()}

    def record(kernel, *values):
        if kernel in (ti.tensor.add, ti.tensor.subtract, ti.tensor.multiply, ti.tensor.divide):
            op_code = {ti.tensor.add: 0, ti.tensor.subtract: 1, ti.tensor.multiply: 2, ti.tensor.divide: 3}[kernel]
            from taichi_vision.taichi_aot.onnx_native_graph import _binary_flat
            kernel = _binary_flat
            values = (values[0], values[1], values[2], op_code)
        target = getattr(kernel, "_primal", None)
        target_func = getattr(target, "func", kernel)
        tree = ast.parse(textwrap.dedent(inspect.getsource(target_func)))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
        substitutions = {}
        kept_args, graph_args = [], []
        for arg, value in zip(function.args.args, values):
            symbol = symbol_names.get(id(value))
            if symbol is not None:
                if arg.annotation is None:
                    arg.annotation = ast.parse("ti.types.ndarray(ti.f32, 1)", mode="eval").body
                kept_args.append(arg)
                graph_args.append(value)
                used.add(symbol)
            else:
                substitutions[arg.arg] = ast.parse(repr(value), mode="eval").body

        class Specialize(ast.NodeTransformer):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load) and node.id in substitutions:
                    return ast.copy_location(copy.deepcopy(substitutions[node.id]), node)
                return node

        function.name = f"node_{len(sources)}"
        function.args.args = kept_args
        function.args.defaults = []
        function.body = [Specialize().visit(node) for node in function.body]
        function.decorator_list = [ast.Attribute(ast.Name("ti", ast.Load()), "kernel", ast.Load())]
        ast.fix_missing_locations(tree)
        sources.append(ast.unparse(tree))
        calls.append((function.name, graph_args))

    for step in plan.steps:
        plan._dispatch(step, emit=record)
    module = ti.aot.Module(arch)
    graph = ti.graph.GraphBuilder()
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="resident_onnx_compile_") as folder:
        source = Path(folder) / "specialized_graph.py"
        source.write_text(
            "import taichi as ti\nfrom math import inf, nan\n"
            "from taichi_vision.taichi_aot.onnx_native_graph import _activation\n"
            + "\n\n".join(sources), encoding="utf-8"
        )
        spec = importlib.util.spec_from_file_location("_resident_specialized_graph", source)
        generated = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated)
        for name, args in calls:
            graph.dispatch(getattr(generated, name), *args)
        module.add_graph(GRAPH_NAME, graph.compile())
        if patch_tools:
            from .resident_patch_kernels import register_graphs
            register_graphs(module)
        archive_module(module, output_path)
    weights = io.BytesIO()
    np.savez(weights, **constants)
    metadata = {
        "format": 1, "backend": backend, "graph": GRAPH_NAME, "patch_tools": patch_tools,
        "model_sha256": hashlib.sha256(model_bytes).hexdigest(),
        "bindings": bindings, "sizes": sizes, "arguments": sorted(used),
        "constants": sorted(constants), "inputs": plan.inputs,
        "outputs": plan.outputs, "shapes": {k: list(v) for k, v in plan.shapes.items()},
    }
    with zipfile.ZipFile(output_path, "a", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("resident_onnx.json", json.dumps(metadata))
        archive.writestr("resident_weights.npz", weights.getvalue())
    return str(output_path)


class ResidentONNXGraph:
    """Borrowed device outputs, valid until the next serial model execution.

    Input and output bindings are flat float32 AOT buffers. No host image
    transfer occurs in run(). The owning pipeline controls synchronization.
    """

    runtime = "taichi_aot"

    def __init__(self, path, *, engine=None, model_sha256=None):
        if engine is None:
            from taichi_vision import taichi_aot
            engine = taichi_aot.get_engine()
        self.engine = engine
        self.path = Path(path).resolve()
        self._lock = threading.RLock()
        self.buffers = {}
        with zipfile.ZipFile(self.path) as archive:
            self.metadata = json.loads(archive.read("resident_onnx.json"))
            weights = archive.read("resident_weights.npz")
        if self.metadata["backend"] != str(engine.arch).lower():
            raise RuntimeError("Resident ONNX artifact/backend mismatch")
        if model_sha256 and self.metadata["model_sha256"] != model_sha256:
            raise RuntimeError("Resident ONNX artifact does not match the selected model")
        self.module = engine.load(str(self.path))
        try:
            input_bindings = {self.metadata["bindings"][key] for key in self.metadata["inputs"]}
            with np.load(io.BytesIO(weights), allow_pickle=False) as values:
                for name in self.metadata["arguments"]:
                    if name in input_bindings:
                        continue
                    self.buffers[name] = (
                        engine.upload(values[name], is_vector=False)
                        if name in self.metadata["constants"]
                        else engine.allocate((self.metadata["sizes"][name],), dtype=np.float32,
                                             is_vector=False, host_accessible=False)
                    )
        except Exception:
            self.close()
            raise

    def get_inputs(self):
        from types import SimpleNamespace
        return [SimpleNamespace(name=name, shape=self.metadata["shapes"][name])
                for name in self.metadata["inputs"]]

    def get_outputs(self):
        from types import SimpleNamespace
        return [SimpleNamespace(name=name, shape=self.metadata["shapes"][name])
                for name in self.metadata["outputs"]]

    def get_providers(self):
        return [f"TaichiAOT_{str(self.engine.arch).upper()}ExecutionProvider"]

    def run_device(self, inputs):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        if set(inputs) != set(self.metadata["inputs"]):
            raise ValueError("Resident ONNX input names do not match model")
        with self._lock:
            args = dict(self.buffers)
            for name, value in inputs.items():
                elements = max(1, math.prod(self.metadata["shapes"][name]))
                if (not isinstance(value, TaichiGPUBuffer) or value.engine is None
                        or value.engine.runtime != self.engine.runtime
                        or tuple(value.shape) != (elements,) or np.dtype(value.dtype) != np.float32):
                    raise ValueError(f"{name} requires same-runtime flat float32 buffer ({elements},)")
                value._require_live("Resident ONNX input")
                args[self.metadata["bindings"][name]] = value
            self.module.run(self.metadata["graph"], **args)
            return {name: args[self.metadata["bindings"][name]]
                    for name in self.metadata["outputs"]}

    def run(self, output_names=None, input_feed=None, return_gpu=False, borrowed_outputs=False):
        """Execute model with support for NumPy, PyTorch, and TaichiGPUBuffer inputs."""
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        if input_feed is None:
            input_feed = {}
        if set(input_feed) != set(self.metadata["inputs"]):
            raise ValueError(f"Expected inputs {self.metadata['inputs']}, got {list(input_feed.keys())}")

        device_inputs = {}
        uploaded_temps = []
        with self._lock:
            for name, value in input_feed.items():
                expected_shape = tuple(self.metadata["shapes"][name])
                elements = max(1, math.prod(expected_shape))
                if isinstance(value, TaichiGPUBuffer):
                    if (value.engine is None or value.engine.runtime != self.engine.runtime
                            or tuple(value.shape) != (elements,) or np.dtype(value.dtype) != np.float32):
                        raise ValueError(f"{name} requires same-runtime flat float32 buffer ({elements},)")
                    value._require_live("Resident ONNX input")
                    device_inputs[name] = value
                else:
                    if hasattr(value, "detach") and hasattr(value, "cpu"):
                        arr = value.detach().cpu().numpy()
                    elif hasattr(value, "to_numpy"):
                        arr = value.to_numpy()
                    else:
                        arr = np.asarray(value)
                    if tuple(arr.shape) != expected_shape and arr.size != elements:
                        raise ValueError(f"Input '{name}' shape mismatch: expected {expected_shape}, got {arr.shape}")
                    arr = np.ascontiguousarray(arr, dtype=np.float32).reshape(-1)
                    buf = self.engine.upload(arr, is_vector=False)
                    uploaded_temps.append(buf)
                    device_inputs[name] = buf
            try:
                res_device = self.run_device(device_inputs)
                if return_gpu:
                    results = res_device
                else:
                    results = {}
                    for name, dev_buf in res_device.items():
                        shape = self.metadata["shapes"][name]
                        results[name] = dev_buf.to_numpy().reshape(shape)
            finally:
                for t in uploaded_temps:
                    t.destroy()
            if output_names is None:
                return list(results.values())
            return [results.get(name) for name in output_names]

    def close(self):
        for value in self.buffers.values():
            value.destroy()
        self.buffers.clear()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--member", help="ONNX member when --model is a bundle")
    parser.add_argument("--backend", choices=("cpu", "cuda", "vulkan", "opengl"), required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--patch-tools", action="store_true")
    options = parser.parse_args()
    if options.member:
        with zipfile.ZipFile(options.model) as bundle:
            source_bytes = bundle.read(options.member)
    else:
        source_bytes = Path(options.model).read_bytes()
    print(compile_resident_onnx(source_bytes, options.output, options.backend, patch_tools=options.patch_tools))
