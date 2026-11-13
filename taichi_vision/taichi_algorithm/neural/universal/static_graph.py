"""Compile and run exact-profile neural models as one Taichi AOT graph.

This module is opt-in. The universal per-node session remains the fallback for
profiles or call modes that do not exactly match the compiled graph manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import numpy as np

from .liveness import LiveInterval, assign_liveness_slots


def _target_identity(backend: str, device: Optional[str] = None) -> Dict[str, str]:
    from taichi.artifact_targets import detect_target

    import taichi as ti

    return detect_target(backend=backend, device=device).as_dict() | {
        "platform": platform.platform(),
        "processor": platform.processor(),
        "taichi": ".".join(str(part) for part in ti.__version__),
    }


def _configured_runtime_abi() -> int:
    from taichi.tcm_contract import RUNTIME_ABI_VERSION

    return int(os.environ.get("AOT_TCM_RUNTIME_ABI", str(RUNTIME_ABI_VERSION)))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _kernel_source_fingerprint() -> str:
    root = Path(__file__).resolve().parent / "kernels"
    digest = hashlib.sha256()
    for path in sorted(root.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _array_dtype_name(dtype: Any) -> str:
    value = np.dtype(dtype)
    if value == np.dtype(np.float32):
        return "f32"
    if value == np.dtype(np.int32):
        return "i32"
    if value == np.dtype(np.int64):
        return "i64"
    raise ValueError(f"static AOT profile does not support ndarray dtype {value}")


def _numpy_dtype(name: str):
    mapping = {"f32": np.float32, "i32": np.int32, "i64": np.int64}
    try:
        return mapping[name]
    except KeyError as exc:
        raise ValueError(f"unsupported static AOT dtype {name!r}") from exc


def _graph_value_shape(value_info) -> Tuple[int, ...]:
    tensor = value_info.type.tensor_type
    dims = []
    for dimension in tensor.shape.dim:
        if dimension.dim_param or not dimension.HasField("dim_value"):
            raise ValueError(f"dynamic output shape is not admitted: {value_info.name}")
        dims.append(int(dimension.dim_value))
    return tuple(dims)


def capture_universal_session(
    model_bytes: bytes,
    input_feed: Mapping[str, np.ndarray],
    *,
    backend: str,
    pool_dir: Optional[Path] = None,
    enable_binary_chains: bool = False,
    enable_pointwise_ssa: bool = False,
) -> Dict[str, Any]:
    """Capture the exact universal lowering dispatch sequence without executing it."""
    from taichi_vision.taichi_algorithm.neural.universal.runtime import UniversalSession

    session = UniversalSession(model_bytes, backend=backend, pool_dir=pool_dir)
    current_step = [-1]
    events: List[Dict[str, Any]] = []
    uploads: Dict[int, Dict[str, Any]] = {}
    allocations: Dict[int, Dict[str, Any]] = {}

    original_upload = session.upload
    original_alloc = session.alloc_slot
    original_run = session.module.run

    def capture_upload(name, array):
        contiguous = np.ascontiguousarray(array)
        buffer = original_upload(name, contiguous)
        uploads[id(buffer)] = {
            "name": str(name),
            "dtype": _array_dtype_name(contiguous.dtype),
            "elements": int(contiguous.size),
            "data": contiguous.copy(),
        }
        return buffer

    def capture_alloc(name, shape, dtype, ctx):
        buffer = original_alloc(name, shape, dtype, ctx)
        allocations[id(buffer)] = {
            "name": str(name),
            "dtype": str(dtype),
            "elements": max(1, int(np.prod(shape, dtype=np.int64))),
            "step": int(current_step[0]),
            "shape": tuple(int(d) for d in shape),
        }
        return buffer

    def record_dispatch(graph_name, **kwargs):
        events.append({
            "graph": str(graph_name),
            "step": int(current_step[0]),
            "kwargs": dict(kwargs),
        })
        return None

    session.upload = capture_upload
    session.alloc_slot = capture_alloc
    session.module.run = record_dispatch
    try:
        session.run(
            output_names=None,
            input_feed=dict(input_feed),
            borrowed_outputs=True,
            step_callback=lambda index, _node: current_step.__setitem__(0, index),
        )
        original_dispatch_count = len(events)
        binary_regions = []
        pointwise_regions = []
        logical_shapes = {}
        if enable_binary_chains or enable_pointwise_ssa:
            import onnx
            from .binary_chain import rewrite_events
            try:
                inferred = onnx.shape_inference.infer_shapes(onnx.load_model_from_string(model_bytes))
                for value in [*inferred.graph.input, *inferred.graph.value_info, *inferred.graph.output]:
                    dims = value.type.tensor_type.shape.dim
                    if all(dim.HasField("dim_value") and dim.dim_value > 0 for dim in dims):
                        logical_shapes[value.name] = tuple(int(dim.dim_value) for dim in dims)
            except Exception:
                pass  # Unknown logical shapes keep regions unfused.
            logical_shapes.update({name: tuple(value.shape) for name, value in input_feed.items()})
            logical_shapes.update({name: tuple(value.shape) for name, value in session.plan.constants.items()})
            logical_shapes.update({item["name"]: item["shape"] for item in allocations.values()})
            if enable_pointwise_ssa:
                from .pointwise_ssa import rewrite_events as rewrite_pointwise
                from .kernels import ALL_KERNELS
                events, pointwise_regions = rewrite_pointwise(
                    events, session.plan, logical_shapes, {**uploads, **allocations},
                    {id(session.buffers[name]) for name in session.plan.output_names if name in session.buffers},
                    {kernel.__name__: kernel for kernel in ALL_KERNELS},
                )
            if enable_binary_chains:
                events, binary_regions = rewrite_events(events, session.plan, logical_shapes, set(session.plan.output_names))
        used_buffer_ids = {
            id(value)
            for event in events
            for value in event["kwargs"].values()
            if hasattr(value, "to_numpy")
        }
        metadata = dict(uploads)
        metadata.update(allocations)
        unknown = sorted(used_buffer_ids - set(metadata) - {id(session.dummy)})
        if unknown:
            raise ValueError(f"captured AOT graph has unknown buffer identities: {unknown[:8]}")

        dummy = np.zeros((1,), dtype=np.float32)
        metadata[id(session.dummy)] = {
            "name": "__dummy__",
            "dtype": "f32",
            "elements": 1,
            "data": dummy,
        }

        event_uses: Dict[int, List[int]] = {}
        for event_index, event in enumerate(events):
            for value in event["kwargs"].values():
                if hasattr(value, "to_numpy"):
                    event_uses.setdefault(id(value), []).append(event_index)

        output_ids = {
            id(session.buffers[name])
            for name in session.plan.output_names
            if name in session.buffers
        }
        output_buffer_ids = {
            name: id(session.buffers[name])
            for name in session.plan.output_names
            if name in session.buffers
        }
        internal = []
        internal_by_id = {}
        for buffer_id, item in allocations.items():
            if buffer_id in output_ids:
                continue
            uses = event_uses.get(buffer_id, [])
            if not uses:
                continue
            first = min(uses)
            last = max(uses)
            interval = LiveInterval(
                name=item["name"], dtype=item["dtype"],
                elements=item["elements"], start=first, end=last,
            )
            internal.append(interval)
            internal_by_id[buffer_id] = item

        liveness = assign_liveness_slots(internal)
        buffer_slot_by_id = {
            buffer_id: liveness.assignments[item["name"]]
            for buffer_id, item in internal_by_id.items()
        }

        input_arg_by_id: Dict[int, str] = {}
        constant_arg_by_id: Dict[int, str] = {}
        constant_arrays: Dict[str, np.ndarray] = {}
        for buffer_id, item in uploads.items():
            if item["name"] in session.plan.input_names:
                input_arg_by_id[buffer_id] = f"input_{len(input_arg_by_id)}"
            else:
                arg_name = f"constant_{len(constant_arg_by_id)}"
                constant_arg_by_id[buffer_id] = arg_name
                constant_arrays[arg_name] = item["data"]
        dummy_arg = "constant_dummy"
        constant_arrays[dummy_arg] = dummy

        graph_buffer_args: Dict[int, str] = {}
        graph_buffer_args.update(input_arg_by_id)
        graph_buffer_args.update(constant_arg_by_id)
        graph_buffer_args[id(session.dummy)] = dummy_arg
        output_arg_by_id: Dict[int, str] = {}
        for output_name in session.plan.output_names:
            buffer_id = output_buffer_ids.get(output_name)
            if buffer_id is None or buffer_id in graph_buffer_args:
                continue
            arg_name = output_arg_by_id.setdefault(
                buffer_id, f"output_{len(output_arg_by_id)}"
            )
            graph_buffer_args[buffer_id] = arg_name
        for buffer_id, slot in buffer_slot_by_id.items():
            graph_buffer_args[buffer_id] = f"slot_{slot}"
        for event in events:
            if "external_buffer_ids" in event:
                output_args = [graph_buffer_args[identity] for identity in event.get(
                    "output_buffer_ids", [id(event["kwargs"].get("y"))]
                )]
                if len(set(output_args)) != len(output_args):
                    raise ValueError("fused call output storage aliases after liveness planning")
                if any(graph_buffer_args[buffer_id] in output_args for buffer_id in event["external_buffer_ids"]):
                    raise ValueError("fused call input/output storage aliases after liveness planning")

        scalar_arg_by_value: Dict[Tuple[str, Any], str] = {}
        scalar_values: Dict[str, Any] = {}
        dispatch_specs = []
        from .kernels import ALL_KERNELS

        kernels = {kernel.__name__: kernel for kernel in ALL_KERNELS}
        import taichi as ti

        for event in events:
            kernel = event.get("kernel") or kernels.get(event["graph"])
            if kernel is None:
                raise ValueError(f"static graph refers to unknown kernel {event['graph']!r}")
            ordered_args = []
            for arg in kernel._primal.arguments:
                name = arg.name
                if name not in event["kwargs"]:
                    raise ValueError(f"missing {name!r} for captured graph {event['graph']!r}")
                value = event["kwargs"][name]
                if hasattr(value, "to_numpy"):
                    graph_arg_name = graph_buffer_args.get(id(value))
                    if graph_arg_name is None:
                        raise ValueError(
                            f"no graph argument for buffer {name!r} in {event['graph']!r}"
                        )
                    dtype = _numpy_dtype(metadata[id(value)]["dtype"])
                    dtype_ti = {
                        np.dtype(np.float32): ti.f32,
                        np.dtype(np.int32): ti.i32,
                        np.dtype(np.int64): ti.i64,
                    }[np.dtype(dtype)]
                    ordered_args.append(
                        ti.graph.Arg(ti.graph.ArgKind.NDARRAY, graph_arg_name,
                                     dtype_ti, ndim=1)
                    )
                else:
                    annotation = arg.annotation
                    if isinstance(value, np.generic):
                        value = value.item()
                    # Numeric equality merges signed zeros; preserve typed bits.
                    from .scalar_specialization import scalar_binding_key
                    scalar_key = scalar_binding_key(value, annotation)
                    graph_arg_name = scalar_arg_by_value.get(scalar_key)
                    if graph_arg_name is None:
                        graph_arg_name = f"scalar_{len(scalar_arg_by_value)}"
                        scalar_arg_by_value[scalar_key] = graph_arg_name
                        scalar_values[graph_arg_name] = value
                    ordered_args.append(
                        ti.graph.Arg(ti.graph.ArgKind.SCALAR, graph_arg_name, annotation)
                    )
            dispatch_specs.append((kernel, ordered_args))

        return {
            "session": session,
            "plan": session.plan,
            "device_name": getattr(session.engine, "gpu_name", None),
            "output_buffer_ids": output_buffer_ids,
            "input_shapes": {
                name: list(np.asarray(value).shape)
                for name, value in input_feed.items()
            },
            "events": events,
            "metadata": metadata,
            "uploads": uploads,
            "allocations": allocations,
            "output_ids": output_ids,
            "liveness": liveness,
            "buffer_slot_by_id": buffer_slot_by_id,
            "graph_buffer_args": graph_buffer_args,
            "input_arg_by_id": input_arg_by_id,
            "constant_arg_by_id": constant_arg_by_id,
            "constant_arrays": constant_arrays,
            "scalar_values": scalar_values,
            "dispatch_specs": dispatch_specs,
            "binary_regions": binary_regions,
            "binary_chains_enabled": enable_binary_chains,
            "original_dispatch_count": original_dispatch_count,
            "logical_shapes": logical_shapes,
            "pointwise_regions": pointwise_regions,
            "pointwise_ssa_enabled": enable_pointwise_ssa,
        }
    finally:
        session.close()


def compile_static_graph_from_capture(
    capture: Dict[str, Any], backend: str, graph_name: str,
    kernel_overrides: Optional[Mapping[str, Any]] = None,
    *, specialize_scalars: bool = False, fast_math: Optional[bool] = None,
):
    """Compile captured universal dispatches into one Taichi GraphBuilder graph."""
    import taichi as ti

    if (specialize_scalars or capture.get("binary_chains_enabled") or capture.get("pointwise_ssa_enabled")) and fast_math is not False:
        raise ValueError("compiler optimization requires explicit fast_math=False")
    arch = {"cpu": ti.cpu, "vulkan": ti.vulkan, "cuda": ti.cuda}.get(backend)
    if arch is None:
        raise ValueError(f"unsupported static graph backend {backend!r}")
    from taichi.lang import impl

    if impl.get_runtime().prog is None:
        # AOTEngine capture uses the native bridge and does not initialize the
        # Python Taichi runtime required by GraphBuilder's kernel compilation.
        ti.init(arch=arch, offline_cache=False, **({"fast_math": fast_math} if fast_math is not None else {}))
    elif impl.current_cfg().arch != arch:
        raise ValueError(
            f"Taichi runtime arch {impl.current_cfg().arch} "
            f"does not match static profile backend {backend}"
        )
    if fast_math is not None and bool(impl.current_cfg().fast_math) != fast_math:
        raise ValueError("existing Taichi runtime fast_math does not match compile policy")
    builder = ti.graph.GraphBuilder()
    specialization_keys = []
    for kernel, args in capture["dispatch_specs"]:
        kernel = (kernel_overrides or {}).get(kernel.__name__, kernel)
        if specialize_scalars:
            from .scalar_specialization import specialize_kernel
            kernel, args, key = specialize_kernel(
                kernel, args, capture["scalar_values"], backend=backend, fast_math=fast_math
            )
            specialization_keys.append(key)
        builder.dispatch(kernel, *args)
    module = ti.aot.Module(arch)
    module.add_graph(graph_name, builder.compile())
    capture["specialization_keys"] = specialization_keys
    return module


def write_static_profile(*args, **kwargs):
    raise RuntimeError(
        "taichi_vision is load-only; build static profiles with the Taichi venv toolchain."
    )


def load_static_profile(profile_dir: Path) -> Dict[str, Any]:
    profile_dir = Path(profile_dir)
    manifest_path = profile_dir / "profile.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    dispatch_counts = manifest.get("dispatch_graph_counts")
    if not isinstance(dispatch_counts, dict) or sum(dispatch_counts.values()) != manifest.get("dispatches"):
        raise ValueError("static graph dispatch count does not match its kernel inventory")
    tcm_path = profile_dir / manifest["tcm"]
    constants_path = profile_dir / manifest["constants"]
    if _sha256_file(tcm_path) != manifest.get("tcm_sha256"):
        raise ValueError("static graph TCM hash does not match its profile manifest")
    if _sha256_file(constants_path) != manifest.get("constants_sha256"):
        raise ValueError("static graph constants hash does not match its profile manifest")
    with zipfile.ZipFile(tcm_path) as archive:
        content = archive.read("__content__").decode("utf-8", errors="replace")
    graphs = {
        line.split(":", 1)[1].strip()
        for line in content.splitlines()
        if line.startswith("cgraph:")
    }
    if graphs != {manifest.get("graph_name")}:
        raise ValueError(
            f"static graph TCM graph manifest mismatch: expected "
            f"{manifest.get('graph_name')!r}, found {sorted(graphs)}"
        )
    return {**manifest, "profile_dir": profile_dir, "tcm_path": tcm_path,
            "constants_path": constants_path}


__all__ = [
    "assign_liveness_slots", "capture_universal_session", "compile_static_graph_from_capture",
    "load_static_profile", "write_static_profile",
]
