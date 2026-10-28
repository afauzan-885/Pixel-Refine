"""Bounded, opt-in multi-output pointwise SSA over original captured calls.

Kernel bodies are composed before binary-pair rewriting. Array stores become
typed locals; captured compound kernels retain their original branches/math.
"""

import ast
import copy
import hashlib
import inspect
import json
import linecache
import math
import textwrap

import taichi as ti

from .binary_chain import _broadcast, _shape
from .scalar_specialization import typed_scalar

POLICY = "bounded_multi_output_pointwise_ssa_v1"
MAX_EVENTS, MAX_OPS, MAX_OUTPUTS, MAX_INPUTS = 12, 24, 8, 16
_OPS = {"Add", "Sub", "Mul", "Div", "Sqrt", "Clip", "Abs", "Neg", "Softplus", "Sigmoid", "Tanh"}
_BINARY = {"nu_binary_flat", "nu_binary_scalar_lhs", "nu_binary_scalar_rhs", "nu_binary_broadcast"}
_COMPOUND = {"nu_add_sqrt_clip_broadcast", "nu_sub_clip_sqrt_broadcast", "nu_binary_unary_broadcast"}
_CACHE = {}
_BINARY_CODES = {"Add": 0, "Sub": 1, "Mul": 2, "Div": 3}
_UNARY_CODES = {"Sigmoid": 2, "Tanh": 3, "Sqrt": 6, "Abs": 7, "Neg": 8, "Softplus": 10}


def normalize(event, plan, shapes, metadata, kernels):
    graph, kwargs = event["graph"], event["kwargs"]
    if graph not in _BINARY | _COMPOUND | {"nu_unary_f32"}:
        # Standalone Clip/mul-clip have different NaN behavior from the admitted
        # NaN-propagating compound Clip. They are explicit region barriers.
        raise ValueError("unsupported pointwise call")
    node = next(node for node in plan.nodes if node.index == event["step"])
    output_name = metadata[id(kwargs["y"])]["name"]
    last = plan.producer.get(output_name)
    if last is None:
        raise ValueError("missing logical output producer")
    represented = {}

    def visit(current):
        if current.index < node.index or current.index in represented:
            return
        if (current.op not in _OPS or current.domain not in ("", "ai.onnx") or current.attrs
                or len(current.outputs) != 1
                or any(plan.dtypes.get(name) != "f32" for name in current.inputs + current.outputs if name)):
            raise ValueError("unsupported logical operation")
        represented[current.index] = current
        for name in current.inputs:
            producer = plan.producer.get(name)
            if producer is not None:
                visit(producer)

    visit(last)
    if node.index not in represented or len(represented) > 3:
        raise ValueError("unknown captured compound")
    if graph in _BINARY and (len(represented) != 1 or node.op not in {"Add", "Sub", "Mul", "Div"}
                             or kwargs.get("code") != _BINARY_CODES[node.op]):
        raise ValueError("binary opcode mismatch")
    if graph == "nu_unary_f32" and (len(represented) != 1 or kwargs.get("code") != _UNARY_CODES.get(node.op)
                                     or node.op not in _UNARY_CODES):
        raise ValueError("unknown unary")
    ordered = [current for _, current in sorted(represented.items())]
    if graph in _COMPOUND:
        if any(current.inputs[0] != previous.output for previous, current in zip(ordered, ordered[1:])):
            raise ValueError("compound topology mismatch")
        if graph == "nu_binary_unary_broadcast":
            if (len(ordered) != 2 or kwargs.get("binary_code") != _BINARY_CODES.get(node.op)
                    or kwargs.get("unary_code") != _UNARY_CODES.get(last.op)
                    or node.op not in _BINARY_CODES or last.op not in _UNARY_CODES):
                raise ValueError("compound opcode mismatch")
        else:
            expected_ops = ["Add", "Sqrt", "Clip"] if graph == "nu_add_sqrt_clip_broadcast" else ["Sub", "Clip", "Sqrt"]
            if [current.op for current in ordered] != expected_ops:
                raise ValueError("compound operation order mismatch")
    output_shape = _shape(shapes, output_name)
    if kwargs.get("n") != math.prod(output_shape):
        raise ValueError("extent mismatch")
    arg_names = ("a", "b") if graph in _BINARY | _COMPOUND else ("x",)
    names = node.inputs[:len(arg_names)]
    if len(names) != len(arg_names):
        raise ValueError("logical input count mismatch")
    input_shapes = [_shape(shapes, name) for name in names]
    expected = input_shapes[0] if len(names) == 1 else _broadcast(*input_shapes)
    if expected != output_shape:
        raise ValueError("logical broadcast mismatch")
    return {"event": event, "kernel": kernels[graph], "inputs": list(zip(arg_names, names, input_shapes)),
            "output": output_name, "shape": output_shape, "nodes": represented}


def _build(items, start, all_events, plan, shapes, requested_ids):
    shape = items[0]["shape"]
    if any(item["shape"] != shape for item in items) or sum(len(item["nodes"]) for item in items) > MAX_OPS:
        raise ValueError("non-uniform domain or IR budget")
    external, external_names, internal, bodies, namespace = [], [], {}, [], {"ti": ti}
    entry = items[0]["event"]["step"]
    outside_ids = {id(value) for event in all_events[:start] + all_events[start + len(items):]
                   for value in event["kwargs"].values() if hasattr(value, "to_numpy")}
    output_items = [item for item in items if id(item["event"]["kwargs"]["y"]) in outside_ids | requested_ids]
    if not output_items or len(output_items) > MAX_OUTPUTS:
        raise ValueError("output budget")
    output_buffers = [item["event"]["kwargs"]["y"] for item in output_items]
    if len({id(buffer) for buffer in output_buffers}) != len(output_buffers):
        raise ValueError("overlapping logical outputs")
    for number, item in enumerate(items):
        event, kernel = item["event"], item["kernel"]
        kwargs = event["kwargs"]
        output_id = id(kwargs["y"])
        if output_id in internal or any(kwargs["y"] is buf for buf in external):
            raise ValueError("in-place output")
        arrays = {}
        for arg, name, input_shape in item["inputs"]:
            buffer = kwargs[arg]
            if id(buffer) in internal:
                if input_shape != shape:
                    raise ValueError("internal broadcast changes domain")
                arrays[arg] = internal[id(buffer)]
            else:
                producer = plan.producer.get(name)
                if producer is not None and producer.index >= entry:
                    raise ValueError("external input not ready at entry")
                if not any(buffer is buf for buf in external):
                    external.append(buffer)
                    external_names.append(name)
                arrays[arg] = "x" + str(next(i for i, buf in enumerate(external) if buffer is buf))
        if len(external) > MAX_INPUTS:
            raise ValueError("input budget")
        primal = kernel._primal
        namespace.update(primal.func.__globals__)
        function = next(node for node in ast.parse(textwrap.dedent(inspect.getsource(primal.func))).body if isinstance(node, ast.FunctionDef))
        loops = [node for node in function.body if isinstance(node, ast.For)]
        if len(loops) != 1 or not isinstance(loops[0].target, ast.Name) or loops[0].target.id != "i":
            raise ValueError("unsupported kernel loop")
        loop = loops[0]
        locals_ = {node.id for node in ast.walk(function) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)}
        locals_.update(parameter.name for parameter in primal.arguments if parameter.name not in arrays and parameter.name != "y")
        locals_.discard("i")
        target = f"t{number}"
        initializers = [ast.parse(f"{target} = ti.f32(0.0)").body[0]]
        for parameter in primal.arguments:
            if parameter.name in arrays or parameter.name == "y":
                continue
            dtype, value = typed_scalar(kwargs[parameter.name], parameter.annotation)
            initializers.append(ast.parse(f"e{number}_{parameter.name} = ti.{dtype}({value!r})").body[0])

        class Compose(ast.NodeTransformer):
            def visit_Subscript(self, node):
                if isinstance(node.value, ast.Name) and node.value.id in arrays:
                    if not isinstance(node.ctx, ast.Load):
                        raise ValueError("input write")
                    reference = arrays[node.value.id]
                    if reference.startswith("t"):
                        return ast.copy_location(ast.Name(reference, ast.Load()), node)
                    return ast.copy_location(ast.Subscript(ast.Name(reference, ast.Load()), self.visit(node.slice), ast.Load()), node)
                if isinstance(node.value, ast.Name) and node.value.id == "y":
                    if not isinstance(node.ctx, ast.Store):
                        raise ValueError("output read")
                    return ast.copy_location(ast.Name(target, ast.Store()), node)
                raise ValueError("unknown array access")

            def visit_Name(self, node):
                if node.id in locals_:
                    return ast.copy_location(ast.Name(f"e{number}_{node.id}", node.ctx), node)
                return node

        # Original captured compound body and its NaN branches stay intact.
        prelude = [node for node in function.body[:function.body.index(loop)] if not isinstance(node, ast.Expr)]
        transformed = [Compose().visit(copy.deepcopy(node)) for node in prelude + loop.body]
        bodies.extend(initializers + transformed)
        bodies.append(ast.parse(f"{target} = ti.f32({target})").body[0])
        internal[output_id] = target
    if any(any(output is buf for buf in external) for output in output_buffers):
        raise ValueError("external input/output overlap")
    for index, buffer in enumerate(output_buffers):
        bodies.append(ast.parse(f"y{index}[i] = {internal[id(buffer)]}").body[0])
    args = [f"x{i}: ti.types.ndarray(ti.f32, 1)" for i in range(len(external))]
    args += [f"y{i}: ti.types.ndarray(ti.f32, 1)" for i in range(len(output_buffers))]
    skeleton = ast.parse(f"@ti.kernel\ndef generated({','.join(args)}):\n    for i in range({math.prod(shape)}):\n        pass\n")
    skeleton.body[0].body[0].body = bodies
    ast.fix_missing_locations(skeleton)
    source = ast.unparse(skeleton)
    key = hashlib.sha256((POLICY + source).encode()).hexdigest()
    name = "nu_pointwise_ssa_" + key[:20]
    source = source.replace("def generated(", f"def {name}(") + "\n"
    if key not in _CACHE:
        filename = f"<pointwise_ssa_{key}>"
        linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
        exec(compile(source, filename, "exec", dont_inherit=True), namespace)
        _CACHE[key] = namespace[name]
    kwargs = {f"x{i}": buffer for i, buffer in enumerate(external)} | {f"y{i}": buffer for i, buffer in enumerate(output_buffers)}
    event = {"graph": name, "kernel": _CACHE[key], "step": entry, "kwargs": kwargs,
             "external_buffer_ids": [id(buf) for buf in external], "output_buffer_ids": [id(buf) for buf in output_buffers]}
    inventory = {"policy": POLICY, "source_event_indices": list(range(start, start + len(items))),
                 "source_event_count": len(items), "operation_count": sum(len(item["nodes"]) for item in items),
                 "source_steps": [item["event"]["step"] for item in items],
                 "operations": [[node.op for _, node in sorted(item["nodes"].items())] for item in items],
                 "external_names": external_names, "outputs": [item["output"] for item in output_items],
                 "shape": shape, "dtype": "f32", "kernel": name}
    return event, inventory


def rewrite_events(events, plan, shapes, metadata, requested_ids, kernels):
    """Greedy bounded adjacent regions; unsupported calls remain on same backend."""
    rewritten, inventory, position = [], [], 0
    while position < len(events):
        items, best = [], None
        for index in range(position, min(len(events), position + MAX_EVENTS)):
            try:
                items.append(normalize(events[index], plan, shapes, metadata, kernels))
                if len(items) >= 2:
                    best = (_build(items, position, events, plan, shapes, requested_ids), len(items))
            except (KeyError, ValueError, TypeError, IndexError, StopIteration):
                break
        if best:
            (event, region), consumed = best
            rewritten.append(event)
            inventory.append(region)
            position += consumed
        else:
            rewritten.append(events[position])
            position += 1
    return rewritten, inventory
