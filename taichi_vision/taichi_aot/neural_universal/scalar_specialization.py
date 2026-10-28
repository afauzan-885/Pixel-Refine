"""Typed, opt-in specialization of captured graph scalar arguments."""

import ast
import hashlib
import inspect
import json
import linecache
import math
import textwrap

import numpy as np
import taichi as ti

POLICY = "typed_scalar_literals_v1"
_CACHE = {}


def scalar_binding_key(value, annotation):
    # Capture preserves the default compiler's nonfinite scalar support. The
    # specialization boundary separately calls typed_scalar and rejects it.
    if str(annotation) == "f32":
        return "f32", np.asarray(value, dtype=np.float32).tobytes()
    dtype, normalized = typed_scalar(value, annotation)
    return dtype, np.asarray(normalized, dtype={"f32": np.float32, "i32": np.int32, "i64": np.int64}[dtype]).tobytes()


def compiler_fingerprint():
    from pathlib import Path
    root = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for name in ("scalar_specialization.py", "binary_chain.py", "pointwise_ssa.py", "static_graph.py", "static_session.py"):
        digest.update(name.encode())
        digest.update((root / name).read_bytes())
    return digest.hexdigest()


def typed_scalar(value, annotation):
    """Return the value represented by the original kernel parameter type."""
    dtype = str(annotation)
    if dtype in ("i32", "i64"):
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
            raise ValueError("integer scalar requires an integer binding")
        bits = 32 if dtype == "i32" else 64
        value = int(value)
        if not -(1 << (bits - 1)) <= value < (1 << (bits - 1)):
            raise ValueError("integer scalar out of range")
    elif dtype == "f32":
        if isinstance(value, (bool, np.bool_)) or not isinstance(value, (float, int, np.number)):
            raise ValueError("float scalar requires a numeric binding")
        if not math.isfinite(float(value)) or abs(float(value)) > float(np.finfo(np.float32).max):
            raise ValueError("float scalar must be finite and in range")
        value = float(np.float32(value))
    else:
        raise ValueError(f"unsupported scalar annotation {dtype!r}")
    return dtype, value


def specialize_kernel(kernel, args, scalar_values, *, backend, fast_math):
    """Keep ndarray arguments and replace only checked captured SCALAR arguments."""
    primal = kernel._primal
    if len(args) != len(primal.arguments):
        raise ValueError("kernel argument count mismatch")
    source = textwrap.dedent(inspect.getsource(primal.func))
    bindings, kept = {}, []
    for parameter, arg in zip(primal.arguments, args):
        if arg.name in scalar_values:
            if isinstance(parameter.annotation, ti.types.ndarray_type.NdarrayType):
                raise ValueError("scalar binding refers to non-scalar graph argument")
            bindings[parameter.name] = typed_scalar(scalar_values[arg.name], parameter.annotation)
        else:
            if not isinstance(parameter.annotation, ti.types.ndarray_type.NdarrayType):
                raise ValueError("missing scalar binding")
            kept.append(arg)
    key = hashlib.sha256(json.dumps(
        [POLICY, compiler_fingerprint(), source, bindings, backend, fast_math], sort_keys=True
    ).encode()).hexdigest()
    if key in _CACHE:
        return _CACHE[key], kept, key
    tree = ast.parse(source)
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef))
    function.name = "nu_scalar_" + key[:20]
    function.args.args = [arg for arg in function.args.args if arg.arg not in bindings]
    function.args.defaults = []
    function.decorator_list = [ast.Attribute(ast.Name("ti", ast.Load()), "kernel", ast.Load())]

    # Keep the original body, including parameter reassignment and loop scopes.
    initializers = [ast.parse(f"{name} = ti.{dtype}({value!r})").body[0]
                    for name, (dtype, value) in bindings.items()]
    function.body = initializers + function.body
    ast.fix_missing_locations(tree)
    generated = ast.unparse(tree) + "\n"
    filename = f"<neural_scalar_{key}>"
    linecache.cache[filename] = (len(generated), None, generated.splitlines(True), filename)
    namespace = dict(primal.func.__globals__)
    namespace["ti"] = ti
    exec(compile(generated, filename, "exec", dont_inherit=True), namespace)
    specialized = namespace[function.name]
    _CACHE[key] = specialized
    return specialized, kept, key
