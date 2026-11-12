"""Opt-in static AOT graph wrapper with same-backend universal fallback."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np

from .runtime import DEFAULT_POOL_DIR, UniversalSession
from .static_graph import (
    _configured_runtime_abi,
    _kernel_source_fingerprint,
    _target_identity,
    load_static_profile,
)

DEFAULT_STATIC_MODEL_DIR = DEFAULT_POOL_DIR / "universal" / "models"


class StaticGraphSession:
    """Use an exact-profile AOT graph when valid; otherwise call UniversalSession.

    This wrapper is opt-in and does not alter the production/default resolver.
    Static graph activation is observable through ``fast_path_active`` and
    ``last_fallback_reason``. Any profile or call-mode mismatch delegates to the
    generic session on the same selected backend.
    """

    def __init__(
        self,
        model_path_or_bytes,
        *,
        backend: str = "cpu",
        profile_root: Optional[Path] = None,
        profile_variant: Optional[str] = None,
        pool_dir: Optional[Path] = None,
    ):
        self.generic = UniversalSession(
            model_path_or_bytes, backend=backend, pool_dir=pool_dir
        )
        self.engine = self.generic.engine
        self.backend = self.generic.backend
        self.plan = self.generic.plan
        self.profile_root = Path(profile_root) if profile_root else DEFAULT_STATIC_MODEL_DIR
        self.profile_variant = profile_variant
        self.profile: Optional[Dict[str, Any]] = None
        self.static_module = None
        self.fast_path_active = False
        self.last_run_used_fast_path = False
        self.last_fallback_reason: Optional[str] = None
        self._static_buffers: Dict[str, Any] = {}
        self._constant_arrays: Dict[str, np.ndarray] = {}
        self._run_needs_sync = False
        self._closed = False

        model_bytes = self.generic.model_bytes
        self.model_sha256 = hashlib.sha256(model_bytes).hexdigest()
        candidate = self.profile_root / self.model_sha256 / self.backend
        if profile_variant:
            candidate = candidate / profile_variant
        try:
            profile = load_static_profile(candidate)
            self._validate_profile(profile)
            with np.load(profile["constants_path"], allow_pickle=False) as constants_file:
                self._constant_arrays = {
                    name: np.ascontiguousarray(constants_file[name])
                    for name in constants_file.files
                }
            expected_constants = set(profile["constant_args"]) | {profile["dummy_arg"]}
            if set(self._constant_arrays) != expected_constants:
                raise ValueError(
                    "static graph constant archive names do not match profile manifest"
                )
            self.static_module = self.engine.load(str(profile["tcm_path"]))
            self.profile = profile
            self.fast_path_active = True
        except Exception as exc:  # noqa: BLE001
            self.last_fallback_reason = f"static profile unavailable/incompatible: {exc}"

    def _validate_profile(self, profile: Dict[str, Any]) -> None:
        policy = profile.get("compiler_policy")
        explicit_variant = getattr(self, "profile_variant", None) is not None
        versioned = (any(name in profile for name in ("compiler_schema_version", "compiler_mode", "profile_variant"))
                     or profile.get("schema_version", 1) not in (None, 1))
        if explicit_variant or versioned or profile.get("binary_regions") or profile.get("pointwise_regions"):
            if (type(profile.get("schema_version")) is not int
                    or profile.get("schema_version") != 2
                    or type(profile.get("compiler_schema_version")) is not int
                    or profile.get("compiler_schema_version") != 2
                    or not isinstance(profile.get("compiler_mode"), str)
                    or not isinstance(policy, dict)):
                raise ValueError("explicit/versioned static profile requires compiler policy schema")
            if explicit_variant and profile.get("profile_variant") != self.profile_variant:
                raise ValueError("static compiler profile variant does not match requested variant")
        if policy is not None:
            from .scalar_specialization import POLICY, compiler_fingerprint
            if (not isinstance(policy, dict)
                    or type(policy.get("schema_version")) is not int
                    or policy.get("schema_version") != 2
                    or policy.get("mode") != profile.get("compiler_mode")
                    or policy.get("source_sha256") != compiler_fingerprint()
                    or policy.get("scalar_specialization") not in (None, POLICY)
                    or policy.get("fast_math") is not False):
                raise ValueError("static compiler policy/source mismatch")
            if policy.get("scalar_specialization") and profile.get("scalar_values"):
                raise ValueError("specialized graph must not bind runtime scalars")
            original = policy.get("original_scalar_values")
            keys = policy.get("specialization_keys")
            if not isinstance(original, dict) or not isinstance(keys, list):
                raise ValueError("static compiler scalar metadata missing")
            if policy.get("scalar_specialization"):
                if len(keys) != profile.get("dispatches") or any(
                    not isinstance(key, str) or len(key) != 64
                    or any(char not in "0123456789abcdef" for char in key) for key in keys
                ):
                    raise ValueError("static compiler specialization inventory mismatch")
            elif keys or profile.get("scalar_values") != original:
                raise ValueError("static compiler runtime scalar inventory mismatch")
            from .binary_chain import POLICY as BINARY_POLICY
            from .pointwise_ssa import POLICY as POINTWISE_POLICY, MAX_EVENTS, MAX_OPS, MAX_OUTPUTS, MAX_INPUTS, _OPS
            from .binary_chain import _shape, _broadcast
            pointwise = profile.get("pointwise_regions", [])
            if policy.get("pointwise_ssa") not in (None, POINTWISE_POLICY) or not isinstance(pointwise, list):
                raise ValueError("unknown pointwise SSA policy/inventory")
            savings = 0
            for region in pointwise:
                if (not isinstance(region, dict) or region.get("policy") != POINTWISE_POLICY
                        or policy.get("pointwise_ssa") != POINTWISE_POLICY
                        or type(region.get("source_event_count")) is not int
                        or not 2 <= region["source_event_count"] <= MAX_EVENTS
                        or type(region.get("operation_count")) is not int
                        or not region["source_event_count"] <= region["operation_count"] <= MAX_OPS
                        or not isinstance(region.get("outputs"), list)
                        or not 1 <= len(region["outputs"]) <= MAX_OUTPUTS):
                    raise ValueError("pointwise SSA region inventory mismatch")
                savings += region["source_event_count"] - 1
                shapes = profile.get("logical_shapes")
                if not isinstance(shapes, dict):
                    raise ValueError("pointwise SSA logical shape inventory missing")
                outputs, inputs = region["outputs"], region.get("external_names")
                shape = region.get("shape")
                if (not isinstance(inputs, list) or not 1 <= len(inputs) <= MAX_INPUTS
                        or any(not isinstance(name, str) or not name for name in inputs + outputs)
                        or len(set(inputs)) != len(inputs)
                        or len(set(outputs)) != len(outputs)
                        or not isinstance(shape, (list, tuple)) or any(type(dim) is not int for dim in shape)
                        or any(name not in shapes or not isinstance(shapes[name], (list, tuple))
                               or any(type(dim) is not int for dim in shapes[name]) for name in inputs + outputs)
                        or _shape({"domain": shape}, "domain") != tuple(shape)
                        or any(_shape(shapes, name) != tuple(shape) for name in outputs)
                        or any(_broadcast(_shape(shapes, name), tuple(shape)) != tuple(shape) for name in inputs)):
                    raise ValueError("pointwise SSA output/input shape inventory mismatch")
                indices, steps, operations = region.get("source_event_indices"), region.get("source_steps"), region.get("operations")
                if (not isinstance(indices, list) or len(indices) != region["source_event_count"]
                        or any(type(index) is not int or index < 0 or index >= profile.get("original_dispatch_count", 0) for index in indices)
                        or indices != list(range(indices[0], indices[0] + len(indices)))
                        or not isinstance(steps, list) or len(steps) != len(indices)
                        or any(type(step) is not int or step < 0 for step in steps)
                        or not isinstance(operations, list) or len(operations) != len(indices)
                        or any(not isinstance(ops, list) or not ops or any(not isinstance(op, str) or op not in _OPS for op in ops) for ops in operations)
                        or sum(map(len, operations)) != region["operation_count"]):
                    raise ValueError("pointwise SSA operation/source inventory mismatch")
            expected_mode = ("pointwise_ssa_" if policy.get("pointwise_ssa") else "") + ("binary_chain_" if policy.get("binary_chains") else "") + (
                "scalar_specialized" if policy.get("scalar_specialization") else "runtime_scalars"
            )
            if policy.get("mode") != expected_mode:
                raise ValueError("static compiler mode does not match optimization policy")
            regions = profile.get("binary_regions", [])
            if policy.get("binary_chains") not in (None, BINARY_POLICY):
                raise ValueError("unknown binary chain compiler policy")
            if (not isinstance(regions, list)
                    or (regions and policy.get("binary_chains") != BINARY_POLICY)
                    or profile.get("original_dispatch_count", profile.get("dispatches")) - profile.get("dispatches", 0) != len(regions) + savings):
                raise ValueError("binary chain region inventory mismatch")
        if profile.get("model_sha256") != self.model_sha256:
            raise ValueError("model SHA-256 mismatch")
        if profile.get("backend") != self.backend:
            raise ValueError("backend mismatch")
        if profile.get("runtime_abi") != _configured_runtime_abi():
            raise ValueError("runtime ABI mismatch")
        if profile.get("kernel_sources_sha256") != _kernel_source_fingerprint():
            raise ValueError("universal kernel source fingerprint mismatch")
        if profile.get("target_identity") != _target_identity(
            self.backend, getattr(self.engine, "gpu_name", None)
        ):
            raise ValueError("target identity mismatch")
        overrides = profile.get("kernel_overrides", {})
        allowed_overrides = {
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_kahan_unrolled"),
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_kahan_linear_ci"),
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_kahan_ndrange"),
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_kahan_p8"),
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_spatial_2x2"),
            ("nu_conv2d_1x1", "nu_conv2d_1x1_spatial4"),
            ("nu_conv2d_4x4_s2", "nu_conv2d_4x4_s2_plain"),
        }
        if overrides and (
            self.backend != "cpu"
            or self.model_sha256 != "142d1c8685d1d6bb71aec04bf9aa2522d7c5f0dcff3c12c293a9a5cdf0009184"
            or len(overrides) != 1
            or next(iter(overrides.items())) not in allowed_overrides
        ):
            raise ValueError("kernel override is not admitted for this exact profile")
        if profile.get("model_input_dtypes") != {
            name: self.plan.dtypes[name] for name in self.plan.input_names
        }:
            raise ValueError("model input dtype mismatch")
        if set(profile.get("model_input_shapes", {})) != set(self.plan.input_names):
            raise ValueError("model input shape names mismatch")
        if set(profile.get("outputs", {})) != set(self.plan.output_names):
            raise ValueError("model output set mismatch")
        if profile.get("tcm_sha256") is None or profile.get("constants_sha256") is None:
            raise ValueError("profile is missing artifact hashes")

    def _ensure_static_buffers(self, input_arrays: Dict[str, np.ndarray]) -> Dict[str, Any]:
        assert self.profile is not None
        for name, array in input_arrays.items():
            arg_name = self.profile["input_args"][name]
            buffer = self._static_buffers.get(arg_name)
            flattened = np.ascontiguousarray(array).reshape(-1)
            if buffer is None:
                buffer = self.engine.upload(flattened, is_vector=False)
                self._static_buffers[arg_name] = buffer
            else:
                self.engine.write_into(buffer, flattened, synchronize=False)

        for arg_name, data in self._constant_arrays.items():
            if arg_name in self._static_buffers:
                continue
            self._static_buffers[arg_name] = self.engine.upload(
                np.ascontiguousarray(data).reshape(-1), is_vector=False
            )

        for slot in self.profile["slots"]:
            name = slot["name"]
            if name not in self._static_buffers:
                dtype = np.dtype({"f32": np.float32, "i32": np.int32, "i64": np.int64}[slot["dtype"]])
                self._static_buffers[name] = self.engine.allocate(
                    (int(slot["elements"]),), dtype=dtype, is_vector=False
                )

        for spec in self.profile["outputs"].values():
            name = spec["arg"]
            if name in self._static_buffers:
                continue
            dtype = np.dtype({"f32": np.float32, "i32": np.int32, "i64": np.int64}[spec["dtype"]])
            shape = tuple(spec["shape"])
            elements = int(np.prod(shape, dtype=np.int64)) if shape else 1
            self._static_buffers[name] = self.engine.allocate(
                (elements,), dtype=dtype, is_vector=False
            )

        kwargs = dict(self._static_buffers)
        kwargs.update(self.profile["scalar_values"])
        return kwargs

    def _static_input_arrays(self, input_feed: Dict[str, Any]) -> Optional[Dict[str, np.ndarray]]:
        assert self.profile is not None
        if set(input_feed) != set(self.profile["input_args"]):
            return None
        arrays = {}
        for name, value in input_feed.items():
            if not isinstance(value, np.ndarray):
                return None
            expected_shape = tuple(self.profile["model_input_shapes"][name])
            expected_dtype = np.dtype({"f32": np.float32, "i32": np.int32, "i64": np.int64}[self.plan.dtypes[name]])
            if tuple(value.shape) != expected_shape or value.dtype != expected_dtype:
                return None
            arrays[name] = np.ascontiguousarray(value)
        return arrays

    def run(
        self,
        output_names: Optional[Sequence[str]] = None,
        input_feed: Optional[Dict[str, Any]] = None,
        return_gpu: bool = False,
        borrowed_outputs: bool = False,
        step_limit: Optional[int] = None,
        step_callback: Optional[Any] = None,
    ):
        if self._closed:
            raise RuntimeError("static graph session is closed")
        requested = list(output_names) if output_names else list(self.plan.output_names)
        full_outputs = requested == list(self.plan.output_names)
        feed = dict(input_feed or {})
        arrays = self._static_input_arrays(feed) if self.fast_path_active else None
        can_use_static = (
            self.fast_path_active
            and arrays is not None
            and full_outputs
            and step_limit is None
            and step_callback is None
        )
        if not can_use_static:
            if self._run_needs_sync:
                self.engine.sync()
                self._run_needs_sync = False
            reasons = []
            if not self.fast_path_active:
                reasons.append(self.last_fallback_reason or "profile not active")
            if arrays is None:
                reasons.append("input key/shape/dtype mismatch")
            if not full_outputs:
                reasons.append("requested outputs require per-node execution")
            if step_limit is not None or step_callback is not None:
                reasons.append("step controls require per-node execution")
            self.last_fallback_reason = "; ".join(reasons)
            self.last_run_used_fast_path = False
            return self.generic.run(
                output_names, feed, return_gpu, borrowed_outputs,
                step_limit, step_callback,
            )

        if self._run_needs_sync:
            self.engine.sync()
            self._run_needs_sync = False
        graph_args = self._ensure_static_buffers(arrays)
        self.static_module.run(self.profile["graph_name"], **graph_args)
        self.generic.buffers = {
            name: self._static_buffers[spec["arg"]]
            for name, spec in self.profile["outputs"].items()
        }
        self.last_run_used_fast_path = True
        self.last_fallback_reason = None
        if return_gpu or borrowed_outputs:
            self._run_needs_sync = True
            return [self._static_buffers[self.profile["outputs"][name]["arg"]]
                    for name in requested]
        results = []
        for name in requested:
            spec = self.profile["outputs"][name]
            shape = tuple(spec["shape"])
            elements = int(np.prod(shape, dtype=np.int64)) if shape else 1
            array = self._static_buffers[spec["arg"]].to_numpy().reshape(-1)[:elements]
            results.append(array.reshape(shape))
        return results

    def get_inputs(self):
        return self.generic.get_inputs()

    def get_outputs(self):
        return self.generic.get_outputs()

    def get_providers(self):
        return self.generic.get_providers()

    def close(self) -> None:
        if self._closed:
            return
        if self._run_needs_sync:
            self.engine.sync()
        for buffer in self._static_buffers.values():
            try:
                buffer.destroy()
            except Exception:  # noqa: BLE001
                pass
        self._static_buffers.clear()
        self.generic.close()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


# Preserve the initial public name for callers created before the generic API
# name was introduced.
StaticWeightNetSession = StaticGraphSession

__all__ = ["StaticGraphSession", "StaticWeightNetSession"]
