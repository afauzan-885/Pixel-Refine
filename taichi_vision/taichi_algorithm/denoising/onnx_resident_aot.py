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
from taichi_vision.taichi_algorithm.neural.device_invocation import (
    Access, DeviceView, DeviceViewDescriptor, SerialDeviceInvocations,
)

def _resolve_output(source, dst=None):
    """True when the result should stay resident (device-owned)."""
    from taichi.aot_engine import is_resident

    if dst is not None and is_resident(dst):
        return True
    if isinstance(source, dict):
        return any(is_resident(value) for value in source.values())
    if isinstance(source, (list, tuple)):
        return any(is_resident(value) for value in source)
    return is_resident(source)




GRAPH_NAME = "deno_onnx_resident_f32_v1"


def compile_resident_onnx(*args, **kwargs):
    raise RuntimeError(
        "taichi_vision is load-only; compile ONNX artifacts with the Taichi venv toolchain."
    )


class ResidentONNXGraph:
    """Borrowed device outputs, valid until the next serial model execution.

    Input and output bindings are flat float32 AOT buffers. No host image
    transfer occurs in run(). The owning pipeline controls synchronization.
    """

    runtime = "taichi_aot"

    def __init__(self, path, *, engine=None, model_sha256=None, artifact_only=False):
        if engine is None:
            import taichi.aot_engine as taichi_aot
            engine = taichi_aot.get_engine()
        self.engine = engine
        self.path = Path(path).resolve()
        self._lock = threading.RLock()
        self._view_owner = (id(engine), engine.runtime, getattr(engine, "_generation", 0))
        self._view_device = (str(engine.arch).lower(), getattr(engine, "device_id", 0), engine.runtime)
        self._view_thread = threading.get_ident()
        self._invocations = SerialDeviceInvocations(self._view_guard, self._view_sync, engine._lock)
        self.buffers = {}
        from taichi.artifact_targets import detect_target
        from taichi.tcm_contract import RUNTIME_ABI_VERSION
        from taichi_vision.taichi_algorithm.denoising.resident_manifest import (
            configured_runtime_abi,
            read_resident_archive,
            validate_resident_metadata,
        )
        from taichi_vision.taichi_algorithm.denoising.resident_capabilities import (
            runtime_capabilities,
        )
        import taichi as ti

        self.metadata, weights, member_hashes = read_resident_archive(self.path)
        target = detect_target(
            backend=str(engine.arch).lower(), device=getattr(engine, "gpu_name", "")
        ).as_dict()
        self.manifest_compatibility = validate_resident_metadata(
            self.metadata,
            backend=str(engine.arch).lower(),
            target_identity=target,
            model_sha256=model_sha256,
            artifact_only=artifact_only,
            runtime_abi=configured_runtime_abi(RUNTIME_ABI_VERSION),
            artifact_members=member_hashes,
            weights_sha256=hashlib.sha256(weights).hexdigest(),
            runtime_taichi_version=str(getattr(ti, "__version__", "")),
            runtime_capabilities=runtime_capabilities(
                str(engine.arch).lower(), getattr(engine, "gpu_name", "")
            ),
        )
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
        from taichi import native_bridge
        from taichi.aot_engine import _raise_native_engine_error
        with self.engine._lock:
            self._view_guard()
            self.engine.sync()
            # `_raise_native_engine_error` always raises. Gate it on an actual
            # native message: a completed sync with an empty error slot is a
            # success, and raising there produced a phantom "unknown native
            # failure" fault after output had already been written.
            if native_bridge.last_error(self.engine.runtime):
                _raise_native_engine_error(
                    self.engine.runtime, "Resident invocation completion"
                )

    def device_view(self, buffer, *, shape=None, offset_bytes=0, strides_bytes=()):
        from taichi.aot_engine import TaichiGPUBuffer
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
            index, slot = self._invocations.available_slot()
            if set(inputs) != set(self.metadata["inputs"]) or not all(isinstance(v, DeviceView) for v in inputs.values()):
                raise ValueError("run_leased requires checked views for every model input")
            values = {}
            for name, view in inputs.items():
                if math.prod(view.descriptor.shape) != max(1, math.prod(self.metadata["shapes"][name])):
                    raise ValueError(f"{name}: device view element count mismatch")
                values[name] = view._bind(self._view_owner, self._view_device)
            if self._invocations.bundles is not None:
                old = self.buffers
                self.buffers = dict(self._invocations.bundles[index])
                try:
                    return self._submit_leased(inputs, values, slot)
                finally:
                    self.buffers = old
            return self._submit_leased(inputs, values, slot)

    def _submit_leased(self, inputs, values, slot):
        accesses = [Access(view.descriptor) for view in inputs.values()]
        shared = {getattr(value.handle, "value", value.handle)
                  for name,value in self.buffers.items() if name in self.metadata["constants"]}
        for name, value in self.buffers.items():
            constant = getattr(value.handle, "value", value.handle) in shared
            accesses.append(Access(self.device_view(value).descriptor, write=not constant, immutable=constant))
        return self._invocations.submit(inputs, accesses, (self,),
            lambda: self._run_device_impl(values),
            lambda name, value: self.device_view(value, shape=self.metadata["shapes"][name]), slot=slot)

    def configure_invocation_slots(self, count=1, *, max_requested_bytes, mode="serial"):
        """Bounded opt-in storage pool on the existing synchronous owner queue."""
        with self._invocations.lock:
            self._view_guard()
            if mode != "serial":
                raise ValueError("Device overlap/parallel streams are unsupported")
            return self._invocations.configure_storage(self.buffers,
                set(self.metadata["constants"]) & set(self.buffers), count=count,
                max_requested_bytes=max_requested_bytes,
                identity=lambda value:getattr(value.handle, "value", value.handle),
                nbytes=lambda value:int(value.size_bytes),
                clone=lambda value:self.engine.allocate(tuple(value.shape), dtype=np.float32,
                    is_vector=False, host_accessible=getattr(value,"host_accessible",False)))

    def invocation_capabilities(self):
        return self._invocations.capabilities()

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
            self._invocations.legacy_idle()
            return self._run_device_impl(inputs)

    def _run_device_impl(self, inputs):
        from taichi.aot_engine import TaichiGPUBuffer
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
            self._invocations.legacy_idle()
            return self._prepare_static_device_bindings_impl(inputs)

    def _prepare_static_device_bindings_impl(self, inputs):
        """Pre-bind persistent GPU input buffers once to eliminate Python allocation/validation in hot tile loops."""
        from taichi.aot_engine import TaichiGPUBuffer
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
            self._invocations.legacy_idle()
            self.module.run(self.metadata["graph"], **self._static_args)
            return self._static_outputs

    def run(self, output_names=None, input_feed=None, borrowed_outputs=False):
        _resident_output = _resolve_output(input_feed)
        with self._invocations.lock:
            self._invocations.legacy_idle()
            return self._run_impl(output_names, input_feed, _resident_output, borrowed_outputs)

    def _run_impl(self, output_names=None, input_feed=None, borrowed_outputs=False):
        """Execute model with support for NumPy, PyTorch, and TaichiGPUBuffer inputs."""
        _resident_output = _resolve_output(input_feed)
        from taichi.aot_engine import TaichiGPUBuffer
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
                if _resident_output:
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
            self._invocations.all_idle()
            self._view_sync()
            # Failed pool construction retains every known partial allocation
            # until this explicit, synchronized owner-thread cleanup.
            for resources in (self._invocations.pending_resources, self._invocations.extra_resources):
                while resources:
                    resources[-1].destroy()
                    resources.pop()
            self._close_impl()
            self._invocations.close_slots()
            self._invocations.bundles = None

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
