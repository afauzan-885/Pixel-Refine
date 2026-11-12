"""Opt-in adjacent FP32 binary SSA regions, before physical slot planning."""

import hashlib
import json
import linecache
import math

import numpy as np
import taichi as ti

POLICY = "adjacent_binary_ssa_f32_v1"
_OPS = {"Add": (0, "+"), "Sub": (1, "-"), "Mul": (2, "*")}
_KERNELS = {"nu_binary_flat", "nu_binary_scalar_lhs", "nu_binary_scalar_rhs", "nu_binary_broadcast"}
_CACHE = {}


def _shape(shapes, name):
    value = shapes.get(name)
    if (value is None or len(value) > 8 or any(not isinstance(d, int) or d <= 0 for d in value)
            or math.prod(value) > 2**31 - 1):
        raise ValueError("missing or unsupported logical shape")
    return tuple(value)


def _broadcast(a, b):
    rank = max(len(a), len(b))
    a, b = (1,) * (rank - len(a)) + a, (1,) * (rank - len(b)) + b
    if any(x != y and x != 1 and y != 1 for x, y in zip(a, b)):
        raise ValueError("invalid broadcast")
    return tuple(max(x, y) for x, y in zip(a, b))


def _index(shape, output):
    shape = (1,) * (len(output) - len(shape)) + shape
    terms = []
    for axis, dimension in enumerate(shape):
        if dimension != 1:
            outer = math.prod(output[axis + 1:])
            stride = math.prod(shape[axis + 1:])
            terms.append(f"((i // {outer}) % {output[axis]}) * {stride}")
    return " + ".join(terms) or "0"


def emit_region(ops, external_shapes, first_refs, second_refs, output_shape):
    """Generate only shape/operator constants; all tensor values stay arguments."""
    spec = [POLICY, ops, external_shapes, first_refs, second_refs, output_shape]
    key = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).hexdigest()
    if key in _CACHE:
        return _CACHE[key]
    expressions = [f"x{j}[{_index(shape, output_shape)}]" for j, shape in enumerate(external_shapes)]
    first = f"{expressions[first_refs[0]]} {_OPS[ops[0]][1]} {expressions[first_refs[1]]}"
    second = ["t" if ref == -1 else expressions[ref] for ref in second_refs]
    args = [f"x{j}: ti.types.ndarray(ti.f32, 1)" for j in range(len(external_shapes))]
    args.append("y: ti.types.ndarray(ti.f32, 1)")
    source = (f"@ti.kernel\ndef nu_binary_chain_{key[:20]}({', '.join(args)}):\n"
              f"    for i in range({math.prod(output_shape)}):\n"
              f"        t = ti.f32({first})\n"
              f"        y[i] = ti.f32({second[0]} {_OPS[ops[1]][1]} {second[1]})\n")
    filename = f"<binary_chain_{key}>"
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
    namespace = {"ti": ti}
    exec(compile(source, filename, "exec", dont_inherit=True), namespace)
    kernel = namespace[f"nu_binary_chain_{key[:20]}"]
    _CACHE[key] = kernel
    return kernel


def rewrite_events(events, plan, shapes, requested_outputs):
    """Fail closed to original events unless an entire private region is proven."""
    by_index = {node.index: node for node in plan.nodes}
    consumers = {}
    for node in plan.nodes:
        for name in set(node.inputs):
            consumers.setdefault(name, set()).add(node.index)
    rewritten, inventory = [], []
    position = 0
    while position < len(events):
        pair = events[position:position + 2]
        try:
            if len(pair) != 2 or any(event["graph"] not in _KERNELS for event in pair):
                raise ValueError("not adjacent binary calls")
            first, second = [by_index[event["step"]] for event in pair]
            for node, event in zip((first, second), pair):
                if (node.op not in _OPS or node.domain not in ("", "ai.onnx") or node.attrs
                        or len(node.inputs) != 2 or len(node.outputs) != 1
                        or event["kwargs"].get("code") != _OPS[node.op][0]):
                    raise ValueError("unsupported binary node")
                if any(plan.dtypes.get(name) != "f32" for name in node.inputs + node.outputs):
                    raise ValueError("non-FP32 operand")
                if _broadcast(*[_shape(shapes, name) for name in node.inputs]) != _shape(shapes, node.output):
                    raise ValueError("logical output shape mismatch")
                if event["kwargs"].get("n") != math.prod(_shape(shapes, node.output)):
                    raise ValueError("captured dispatch extent mismatch")
            if (first.output in requested_outputs or consumers.get(first.output) != {second.index}
                    or first.output not in second.inputs):
                raise ValueError("intermediate is not private")
            external, buffers = [], []
            for node, event in zip((first, second), pair):
                for name, arg in zip(node.inputs, ("a", "b")):
                    if name == first.output:
                        if event["kwargs"][arg] is not pair[0]["kwargs"]["y"]:
                            raise ValueError("intermediate binding mismatch")
                        continue
                    producer = plan.producer.get(name)
                    if producer is not None and producer.index >= first.index:
                        raise ValueError("external input not ready")
                    if name not in external:
                        external.append(name)
                        buffers.append(event["kwargs"][arg])
                    elif buffers[external.index(name)] is not event["kwargs"][arg]:
                        raise ValueError("inconsistent external binding")
            output = pair[1]["kwargs"]["y"]
            if any(output is buf for buf in buffers):
                raise ValueError("logical input/output buffers alias")
            output_shape = _shape(shapes, second.output)
            first_shape = _shape(shapes, first.output)
            if _broadcast(first_shape, output_shape) != output_shape:
                raise ValueError("intermediate broadcast mismatch")
            external_shapes = [_shape(shapes, name) for name in external]
            refs_first = [external.index(name) for name in first.inputs]
            refs_second = [-1 if name == first.output else external.index(name) for name in second.inputs]
            kernel = emit_region([first.op, second.op], external_shapes, refs_first, refs_second, output_shape)
            kwargs = {f"x{j}": buf for j, buf in enumerate(buffers)} | {"y": output}
            rewritten.append({"graph": kernel.__name__, "step": first.index, "kwargs": kwargs, "kernel": kernel,
                              "external_buffer_ids": [id(buf) for buf in buffers]})
            inventory.append({"policy": POLICY, "source_event_indices": [position, position + 1],
                              "source_steps": [first.index, second.index], "ops": [first.op, second.op],
                              "external_names": external, "external_shapes": external_shapes,
                              "intermediate": first.output, "intermediate_shape": first_shape,
                              "output": second.output, "output_shape": output_shape, "dtype": "f32",
                              "kernel": kernel.__name__})
            position += 2
        except (KeyError, ValueError, TypeError, IndexError):
            rewritten.append(events[position])
            position += 1
    return rewritten, inventory
