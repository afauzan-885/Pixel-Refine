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
from taichi_vision.taichi_aot.device_invocation import (
    Access, DeviceView, DeviceViewDescriptor, SerialDeviceInvocations,
)


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
        enable_weightnet_fused_tile_statistics=True,
    )
    arch = {"cpu": ti.cpu, "cuda": ti.cuda, "vulkan": ti.vulkan,
            "opengl": ti.opengl}[backend]
    if backend == "cpu":
        import multiprocessing
        ti.init(arch=ti.cpu, cpu_max_num_threads=multiprocessing.cpu_count(),
                fast_math=True, advanced_optimization=True, offline_cache=False)
    else:
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
            "from taichi_vision.taichi_aot.weightnet_gate_fusions import _stable_softplus\n"
            "from taichi_vision.taichi_aot.onnx_native_graph import _weightnet_fused_tile_statistics\n"
            + "\n\n".join(sources), encoding="utf-8"
        )
        spec = importlib.util.spec_from_file_location("_resident_specialized_graph", source)
        generated = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generated)
        for name, args in calls:
            graph.dispatch(getattr(generated, name), *args)
        module.add_graph(GRAPH_NAME, graph.compile())
        tile_step_graph_name = None
        tile_step_cached_graph_name = None
        if patch_tools:
            from .resident_patch_kernels import extract, extract_with_ref_cache, stitch, register_graphs
            register_graphs(module)
            if {"ref_img", "support_img", "weight_map", "alpha"} <= set(bindings):
                tile_step_graph_name = "deno_resident_tile_step_v1"
                tile_step_cached_graph_name = "deno_resident_tile_step_cached_v1"
                ref_tile_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, bindings["ref_img"], ti.f32, ndim=1)
                supp_tile_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, bindings["support_img"], ti.f32, ndim=1)
                weight_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, bindings["weight_map"], ti.f32, ndim=1)
                alpha_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, bindings["alpha"], ti.f32, ndim=1)
                patch_ref_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_reference", ti.f32, ndim=1)
                patch_ref_cache_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_ref_cache", ti.f32, ndim=1)
                patch_supp_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_support", ti.f32, ndim=1)
                patch_win_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_window", ti.f32, ndim=1)
                patch_num_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_numerator", ti.f32, ndim=2)
                patch_den_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_denominator", ti.f32, ndim=2)
                patch_asum_arg = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "patch_alpha_sum", ti.f32, ndim=1)
                patch_h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_height", ti.i32)
                patch_w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_width", ti.i32)
                patch_sz_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_size", ti.i32)
                patch_tile_idx_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_tile_idx", ti.i32)
                patch_cur_h_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_cur_h", ti.i32)
                patch_cur_w_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_cur_w", ti.i32)
                patch_y0_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_y0", ti.i32)
                patch_x0_arg = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "patch_x0", ti.i32)

                tile_graph = ti.graph.GraphBuilder()
                tile_graph.dispatch(
                    extract,
                    patch_ref_arg,
                    patch_supp_arg,
                    ref_tile_arg,
                    supp_tile_arg,
                    patch_h_arg,
                    patch_w_arg,
                    patch_sz_arg,
                    patch_y0_arg,
                    patch_x0_arg,
                )
                for name, args in calls:
                    tile_graph.dispatch(getattr(generated, name), *args)
                tile_graph.dispatch(
                    stitch,
                    weight_arg,
                    patch_win_arg,
                    patch_num_arg,
                    patch_den_arg,
                    alpha_arg,
                    patch_asum_arg,
                    patch_sz_arg,
                    patch_cur_h_arg,
                    patch_cur_w_arg,
                    patch_y0_arg,
                    patch_x0_arg,
                )
                module.add_graph(tile_step_graph_name, tile_graph.compile())

                cached_graph = ti.graph.GraphBuilder()
                cached_graph.dispatch(
                    extract_with_ref_cache,
                    patch_ref_cache_arg,
                    patch_supp_arg,
                    ref_tile_arg,
                    supp_tile_arg,
                    patch_h_arg,
                    patch_w_arg,
                    patch_sz_arg,
                    patch_tile_idx_arg,
                    patch_y0_arg,
                    patch_x0_arg,
                )
                for name, args in calls:
                    cached_graph.dispatch(getattr(generated, name), *args)
                cached_graph.dispatch(
                    stitch,
                    weight_arg,
                    patch_win_arg,
                    patch_num_arg,
                    patch_den_arg,
                    alpha_arg,
                    patch_asum_arg,
                    patch_sz_arg,
                    patch_cur_h_arg,
                    patch_cur_w_arg,
                    patch_y0_arg,
                    patch_x0_arg,
                )
                module.add_graph(tile_step_cached_graph_name, cached_graph.compile())
        archive_module(module, output_path)
    weights = io.BytesIO()
    np.savez(weights, **constants)
    metadata = {
        "format": 1, "backend": backend, "graph": GRAPH_NAME, "patch_tools": patch_tools,
        "tile_step_graph": tile_step_graph_name,
        "tile_step_cached_graph": tile_step_cached_graph_name,
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
        self._view_owner = (id(engine), engine.runtime, getattr(engine, "_generation", 0))
        self._view_device = (str(engine.arch).lower(), getattr(engine, "device_id", 0), engine.runtime)
        self._view_thread = threading.get_ident()
        self._invocations = SerialDeviceInvocations(self._view_guard, self._view_sync, engine._lock)
        self.buffers = {}
        with zipfile.ZipFile(self.path) as archive:
            self.metadata = json.loads(archive.read("resident_onnx.json"))
            weights = archive.read("resident_weights.npz")
        if self.metadata["backend"] != str(engine.arch).lower():
            raise RuntimeError("Resident ONNX artifact/backend mismatch")
        # Model provenance check commented out: run directly from .tcm artifact
        # if model_sha256 and self.metadata["model_sha256"] != model_sha256:
        #     raise RuntimeError("Resident ONNX artifact does not match the selected model")
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

    def _view_guard(self):
        engine = self.engine
        if (self._invocations.slot.closed or threading.get_ident() != self._view_thread or not engine.runtime
                or getattr(engine, "_destroyed", False)
                or self._view_owner != (id(engine), engine.runtime, getattr(engine, "_generation", 0))):
            raise RuntimeError("Resident device view owner closed, reinitialized or wrong thread")
        engine._assert_native_context_owner("resident leased invocation")

    def _view_sync(self):
        from taichi_vision.taichi_aot.engine import _raise_native_engine_error
        with self.engine._lock:
            self._view_guard()
            self.engine.sync()
            # Use the owner's existing read/consume/raise policy. Never clear
            # before sync: a fresh completion failure must keep the slot held.
            _raise_native_engine_error(self.engine.runtime, "Resident invocation completion")

    def device_view(self, buffer, *, shape=None, offset_bytes=0, strides_bytes=()):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        with self._invocations.lock, self.engine._lock:
            self._view_guard()
            if (not isinstance(buffer, TaichiGPUBuffer) or buffer.engine is not self.engine
                    or np.dtype(buffer.dtype) != np.float32 or buffer.is_vector or len(buffer.shape) != 1):
                raise ValueError("Resident views require same-owner flat scalar float32 buffers")
            runtime, handle = buffer._require_live("resident device view")
            identity = getattr(handle, "value", handle)
            if not identity:
                raise ValueError("Resident device view requires a non-null native handle")
            descriptor = DeviceViewDescriptor(self._view_owner, self._view_device, identity,
                int(buffer.size_bytes), tuple(shape if shape is not None else buffer.shape),
                offset_bytes=offset_bytes, strides_bytes=tuple(strides_bytes))
            descriptor.require_flat_binding()
            if descriptor.byte_range[1] != int(buffer.shape[0]) * 4:
                raise ValueError("Partial buffer ranges cannot be bound without native offset/extent support")
            def validate():
                self._view_guard()
                live_runtime, live_handle = buffer._require_live("resident device view")
                if live_runtime != runtime or getattr(live_handle, "value", live_handle) != identity:
                    raise RuntimeError("Resident device view storage changed")
            return DeviceView(descriptor, buffer, validate)

    def run_leased(self, inputs):
        """Synchronous one-slot invocation; checked views in, explicit lease out."""
        with self._invocations.lock, self.engine._lock:
            self._view_guard()
            self._invocations.slot.idle()
            if set(inputs) != set(self.metadata["inputs"]) or not all(isinstance(v, DeviceView) for v in inputs.values()):
                raise ValueError("run_leased requires checked views for every model input")
            values = {}
            for name, view in inputs.items():
                if math.prod(view.descriptor.shape) != max(1, math.prod(self.metadata["shapes"][name])):
                    raise ValueError(f"{name}: device view element count mismatch")
                values[name] = view._bind(self._view_owner, self._view_device)
            accesses = [Access(view.descriptor) for view in inputs.values()]
            for name, value in self.buffers.items():
                constant = name in self.metadata["constants"]
                accesses.append(Access(self.device_view(value).descriptor, write=not constant, immutable=constant))
            return self._invocations.submit(inputs, accesses, (self,),
                lambda: self._run_device_impl(values),
                lambda name, value: self.device_view(value, shape=self.metadata["shapes"][name]))

    def drain_failed_invocation(self):
        with self.engine._lock:
            self._invocations.drain_failed()

    def get_outputs(self):
        from types import SimpleNamespace
        return [SimpleNamespace(name=name, shape=self.metadata["shapes"][name])
                for name in self.metadata["outputs"]]

    def get_providers(self):
        return [f"TaichiAOT_{str(self.engine.arch).upper()}ExecutionProvider"]

    def run_device(self, inputs):
        with self._invocations.lock:
            self._invocations.slot.idle()
            return self._run_device_impl(inputs)

    def _run_device_impl(self, inputs):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        inputs = dict(inputs)
        if "max_safety" in self.metadata.get("inputs", []) and "max_safety" not in inputs:
            if not hasattr(self, "_default_max_safety_buf") or self._default_max_safety_buf is None:
                val = getattr(self, "max_safety", 0.30)
                self._default_max_safety_buf = self.engine.upload(
                    np.array([val], dtype=np.float32), is_vector=False
                )
            inputs["max_safety"] = self._default_max_safety_buf
        if set(inputs) != set(self.metadata["inputs"]):
            raise ValueError(f"Resident ONNX input names do not match model: expected {sorted(self.metadata['inputs'])}, got {sorted(inputs.keys())}")
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

    def prepare_static_device_bindings(self, inputs):
        with self._invocations.lock:
            self._invocations.slot.idle()
            return self._prepare_static_device_bindings_impl(inputs)

    def _prepare_static_device_bindings_impl(self, inputs):
        """Pre-bind persistent GPU input buffers once to eliminate Python allocation/validation in hot tile loops."""
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        inputs = dict(inputs)
        if "max_safety" in self.metadata.get("inputs", []) and "max_safety" not in inputs:
            if not hasattr(self, "_default_max_safety_buf") or self._default_max_safety_buf is None:
                val = getattr(self, "max_safety", 0.30)
                self._default_max_safety_buf = self.engine.upload(
                    np.array([val], dtype=np.float32), is_vector=False
                )
            inputs["max_safety"] = self._default_max_safety_buf
        if set(inputs) != set(self.metadata["inputs"]):
            raise ValueError(
                f"Resident ONNX input names do not match model: expected {sorted(self.metadata['inputs'])}, got {sorted(inputs.keys())}"
            )
        args = dict(self.buffers)
        for name, value in inputs.items():
            elements = max(1, math.prod(self.metadata["shapes"][name]))
            if (not isinstance(value, TaichiGPUBuffer) or value.engine is None
                    or value.engine.runtime != self.engine.runtime
                    or tuple(value.shape) != (elements,) or np.dtype(value.dtype) != np.float32):
                raise ValueError(f"{name} requires same-runtime flat float32 buffer ({elements},)")
            value._require_live("Resident ONNX input")
            args[self.metadata["bindings"][name]] = value
        self._static_args = args
        self._static_outputs = {
            name: args[self.metadata["bindings"][name]]
            for name in self.metadata["outputs"]
        }
        return self._static_outputs

    def run_device_fast(self):
        """Zero-allocation, zero-validation fast path executing pre-bound static graph."""
        with self._invocations.lock, self._lock:
            self._invocations.slot.idle()
            self.module.run(self.metadata["graph"], **self._static_args)
            return self._static_outputs

    def run(self, output_names=None, input_feed=None, return_gpu=False, borrowed_outputs=False):
        with self._invocations.lock:
            self._invocations.slot.idle()
            return self._run_impl(output_names, input_feed, return_gpu, borrowed_outputs)

    def _run_impl(self, output_names=None, input_feed=None, return_gpu=False, borrowed_outputs=False):
        """Execute model with support for NumPy, PyTorch, and TaichiGPUBuffer inputs."""
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        if input_feed is None:
            input_feed = {}
        else:
            input_feed = dict(input_feed)
        if "max_safety" in self.metadata.get("inputs", []) and "max_safety" not in input_feed:
            input_feed["max_safety"] = getattr(self, "max_safety", 0.30)
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
        with self._invocations.lock:
            if self._invocations.slot.closed:
                return
            self._invocations.slot.idle()
            self._view_sync()
            self._close_impl()
            self._invocations.slot.close()

    def _close_impl(self):
        if hasattr(self, "_default_max_safety_buf") and self._default_max_safety_buf is not None:
            try:
                self._default_max_safety_buf.destroy()
            except Exception:
                pass
            self._default_max_safety_buf = None
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
