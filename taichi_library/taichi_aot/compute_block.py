"""Opt-in, backend-neutral automatic block dispatch.

``compute_block`` is intentionally a small declaration rather than another
algorithm API.  A decorated function keeps its original call signature and
continues to be the full-frame reference.  When the call contains compatible
NumPy image arrays, the wrapper builds a generic block specification and lets
the existing runtime own planning, cache, checksum, retry, quarantine, and
fallback behaviour.

The wrapper is conservative by construction:

* GPU buffers, destination arguments, scalar/global reductions, and functions
  that already own a tile loop stay on the original path;
* a tile is accepted only when the returned value is an image-like NumPy
  array whose first two dimensions match the requested tile;
* any planner, tile, validation, or merge failure goes through the declared
  full-frame fallback.

This module does not rewrite Python bytecode or monkey-patch NumPy.  Source
analysis is diagnostic metadata (range/slice counts and a best-effort halo
hint); the declaration is the explicit boundary at which automatic dispatch
is allowed.
"""

from __future__ import annotations

import ast
import contextvars
import functools
import inspect
import os
import textwrap
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional

import numpy as np

from .generic_block import (
    BlockComputeSpec,
    run_generic_blocks,
    run_registered_block_adapter,
)


_DISPATCH_DEPTH = contextvars.ContextVar("compute_block_dispatch_depth", default=0)
_ACTIVE_SCOPE = contextvars.ContextVar("compute_block_active_scope", default=None)
_REGISTRY: dict[str, Any] = {}


@dataclass(frozen=True)
class ComputeBlockAnalysis:
    """Static, non-authoritative information about a decorated callable."""

    source_available: bool = False
    range_count: int = 0
    slice_count: int = 0
    has_range: bool = False
    has_slice: bool = False
    literal_halo: int = 0
    existing_tile_loop: bool = False
    source_error: str = ""

    @property
    def candidate(self) -> bool:
        return bool(self.has_range or self.has_slice)

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_available": self.source_available,
            "range_count": self.range_count,
            "slice_count": self.slice_count,
            "has_range": self.has_range,
            "has_slice": self.has_slice,
            "literal_halo": self.literal_halo,
            "existing_tile_loop": self.existing_tile_loop,
            "candidate": self.candidate,
            "source_error": self.source_error,
        }


@dataclass(frozen=True)
class ComputeBlockMetadata:
    """Runtime metadata attached to a decorated function or class."""

    name: str
    mode: str = "auto"
    automatic: bool = True
    halo: Any = "auto"
    min_halo: int = 0
    block_size: Any = None
    threshold_bytes: Optional[int] = None
    cache: bool = True
    cache_key: Optional[str] = None
    version: str = "v1"
    retries: int = 1
    fallback: str = "full_frame"
    detect_slicing: bool = True
    infer_output_shape: bool = True
    runtime: Any = field(default=None, repr=False, compare=False)
    analysis: ComputeBlockAnalysis = field(default_factory=ComputeBlockAnalysis)
    # Optional adapter bridge.  These fields are additive: existing
    # ``@compute_block`` declarations keep their generic local-tile behaviour
    # unless an operation/adapter is explicitly selected or the callable name
    # exactly resolves to a registered canonical operation.
    operation: Optional[str] = None
    adapter: Any = field(default=None, repr=False, compare=False)
    adapter_params: Any = field(default=None, repr=False, compare=False)
    require_native_evidence: bool = False
    native_evidence_device: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "mode": self.mode,
            "automatic": self.automatic,
            "halo": self.halo,
            "min_halo": self.min_halo,
            "block_size": self.block_size,
            "threshold_bytes": self.threshold_bytes,
            "cache": self.cache,
            "cache_key": self.cache_key,
            "version": self.version,
            "retries": self.retries,
            "fallback": self.fallback,
            "detect_slicing": self.detect_slicing,
            "infer_output_shape": self.infer_output_shape,
            "operation": self.operation,
            "adapter_selected": self.adapter is not None,
            "require_native_evidence": self.require_native_evidence,
            "native_evidence_device": self.native_evidence_device,
            "analysis": self.analysis.as_dict(),
        }


class _SourcePatternVisitor(ast.NodeVisitor):
    """Collect only safe-to-report syntax facts; never rewrites the AST."""

    _TILE_NAMES = {
        "blockgrid",
        "block_grid",
        "iter_runtime_flow_blocks",
        "_build_tiles",
        "tile_plan",
        "tiles",
        "roi",
        "valid",
    }

    def __init__(self) -> None:
        self.range_count = 0
        self.slice_count = 0
        self.literal_halo = 0
        self.names: set[str] = set()

    @staticmethod
    def _constant_int(node: ast.AST | None) -> Optional[int]:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return int(abs(node.value))
        if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
            if isinstance(node.operand.value, (int, float)):
                return int(abs(node.operand.value))
        return None

    def _record_numeric_offsets(self, node: ast.AST | None) -> None:
        for item in ast.walk(node) if node is not None else ():
            value = self._constant_int(item)
            if value is not None:
                # Small literals in slice expressions are useful halo hints;
                # cap the hint so an unrelated image-size constant cannot
                # allocate a huge read region automatically.
                self.literal_halo = min(256, max(self.literal_halo, value))

    def visit_Name(self, node: ast.Name) -> Any:  # noqa: N802
        self.names.add(node.id.lower())
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:  # noqa: N802
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> Any:  # noqa: N802
        function = node.func
        if isinstance(function, ast.Name) and function.id == "range":
            self.range_count += 1
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:  # noqa: N802
        value_name = getattr(node.value, "id", "")
        slice_node = node.slice
        parts = (
            list(slice_node.elts) if isinstance(slice_node, ast.Tuple) else [slice_node]
        )
        has_2d_slice = sum(isinstance(part, ast.Slice) for part in parts) >= 2
        has_any_slice = any(isinstance(part, ast.Slice) for part in parts)
        if has_2d_slice or has_any_slice:
            self.slice_count += 1
            self._record_numeric_offsets(slice_node)
        if isinstance(value_name, str) and value_name:
            self.names.add(value_name.lower())
        self.generic_visit(node)

    @property
    def existing_tile_loop(self) -> bool:
        return bool(self.names.intersection(self._TILE_NAMES))


def analyze_compute_block_source(function: Callable[..., Any]) -> ComputeBlockAnalysis:
    """Return diagnostic source facts without making dispatch decisions."""

    try:
        source = textwrap.dedent(inspect.getsource(inspect.unwrap(function)))
        tree = ast.parse(source)
    except Exception as exc:  # interactive/dynamic functions are still valid
        return ComputeBlockAnalysis(source_error=f"{type(exc).__name__}: {exc}")
    visitor = _SourcePatternVisitor()
    visitor.visit(tree)
    return ComputeBlockAnalysis(
        source_available=True,
        range_count=visitor.range_count,
        slice_count=visitor.slice_count,
        has_range=visitor.range_count > 0,
        has_slice=visitor.slice_count > 0,
        literal_halo=visitor.literal_halo,
        existing_tile_loop=visitor.existing_tile_loop,
    )


def _is_array(value: Any) -> bool:
    return isinstance(value, np.ndarray) and value.ndim >= 2


def _contains_gpu_buffer(value: Any) -> bool:
    return bool(
        hasattr(value, "to_numpy")
        and hasattr(value, "handle")
        and hasattr(value, "shape")
    )


_UNSAFE_CACHE_VALUE = object()


def _cache_value(value: Any, array_slots: Mapping[int, int]) -> Any:
    """Return a deterministic cache fragment for non-image call arguments.

    Image arrays are represented by their stable positional slot; their shape,
    dtype, and source checksum are handled by ``GenericBlockExecutor``. An
    unsupported mutable/object argument disables caching for that invocation
    instead of risking reuse for a different algorithm parameter/state.
    """

    slot = array_slots.get(id(value))
    if slot is not None:
        return ("array", int(slot))
    if isinstance(value, np.ndarray):
        return _UNSAFE_CACHE_VALUE
    if isinstance(value, np.generic):
        return _cache_value(value.item(), array_slots)
    if isinstance(value, np.dtype):
        return ("dtype", value.str)
    if value is None or isinstance(value, (bool, int, float, str, bytes)):
        return value
    if isinstance(value, tuple):
        values = tuple(_cache_value(item, array_slots) for item in value)
        return _UNSAFE_CACHE_VALUE if _UNSAFE_CACHE_VALUE in values else values
    if isinstance(value, list):
        values = tuple(_cache_value(item, array_slots) for item in value)
        return (
            _UNSAFE_CACHE_VALUE if _UNSAFE_CACHE_VALUE in values else ("list", values)
        )
    if isinstance(value, Mapping):
        values = []
        for key, item in sorted(value.items(), key=lambda pair: str(pair[0])):
            key_value = _cache_value(key, array_slots)
            item_value = _cache_value(item, array_slots)
            if key_value is _UNSAFE_CACHE_VALUE or item_value is _UNSAFE_CACHE_VALUE:
                return _UNSAFE_CACHE_VALUE
            values.append((str(key), key_value, item_value))
        return ("mapping", tuple(values))
    cache_hook = getattr(value, "__compute_block_cache_key__", None)
    if callable(cache_hook):
        try:
            return ("hook", _cache_value(cache_hook(), array_slots))
        except Exception:
            return _UNSAFE_CACHE_VALUE
    return _UNSAFE_CACHE_VALUE


def _call_cache_parameters(args, kwargs, array_slots: Mapping[int, int]):
    """Build a safe cache namespace for scalar/configuration call arguments."""

    positional = _cache_value(tuple(args), array_slots)
    keyword = _cache_value(dict(kwargs), array_slots)
    if positional is _UNSAFE_CACHE_VALUE or keyword is _UNSAFE_CACHE_VALUE:
        return None, False
    return ("args", positional, "kwargs", keyword), True


def _walk_call_values(args: tuple[Any, ...], kwargs: Mapping[str, Any]):
    """Yield mutable call locations for simple positional/keyword containers."""

    def walk(value: Any, setter: Callable[[Any], None], path: tuple[Any, ...]):
        if _is_array(value) or _contains_gpu_buffer(value):
            yield path, value, setter
            return
        if isinstance(value, tuple):
            for index, item in enumerate(value):
                yield from walk(
                    item,
                    lambda replacement, value=value, index=index: None,
                    path + (index,),
                )
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from walk(
                    item,
                    lambda replacement, value=value, index=index: value.__setitem__(
                        index, replacement
                    ),
                    path + (index,),
                )
        elif isinstance(value, dict):
            for key, item in value.items():
                yield from walk(
                    item,
                    lambda replacement, value=value, key=key: value.__setitem__(
                        key, replacement
                    ),
                    path + (key,),
                )

    for index, value in enumerate(args):
        yield from walk(value, lambda replacement, index=index: None, ("arg", index))
    for key, value in kwargs.items():
        yield from walk(value, lambda replacement, key=key: None, ("kw", key))


def _replace_value(value: Any, replacements: Mapping[int, Any], block) -> Any:
    identity = id(value)
    if identity in replacements:
        if _contains_gpu_buffer(value):
            raise TypeError("automatic compute_block does not slice GPU buffers")
        return np.ascontiguousarray(value[block.read_slice])
    if isinstance(value, tuple):
        return tuple(_replace_value(item, replacements, block) for item in value)
    if isinstance(value, list):
        return [_replace_value(item, replacements, block) for item in value]
    if isinstance(value, dict):
        return {
            key: _replace_value(item, replacements, block)
            for key, item in value.items()
        }
    return value


def _replace_call(args, kwargs, replacements, block):
    return (
        tuple(_replace_value(value, replacements, block) for value in args),
        {
            key: _replace_value(value, replacements, block)
            for key, value in kwargs.items()
        },
    )


def _replace_full_frame(args, kwargs, replacements, arrays):
    values = iter(arrays)
    by_identity = {}
    for identity in replacements:
        by_identity[identity] = next(values)

    def replace(value):
        if id(value) in by_identity:
            return by_identity[id(value)]
        if isinstance(value, tuple):
            return tuple(replace(item) for item in value)
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        return value

    return tuple(replace(value) for value in args), {
        key: replace(value) for key, value in kwargs.items()
    }


def _resolve_runtime(explicit):
    if explicit is not None:
        return explicit
    try:
        from .engine import engine

        return engine
    except Exception:
        return None


def _resolve_adapter_selection(metadata: ComputeBlockMetadata):
    """Resolve an optional registered adapter without changing global state."""

    try:
        from .block import (
            BlockAdapter,
            canonical_operation_name,
            lookup_block_adapter,
            operation_path,
        )
    except Exception:
        return None, metadata.adapter

    explicit = metadata.adapter
    operation = metadata.operation

    def lazy_lookup(canonical: str, current: Any = None):
        """Resolve an explicitly named adapter without broadening auto mode."""

        if current is not None:
            return current
        try:
            from .block_adapters import ensure_default_block_adapters

            return ensure_default_block_adapters(canonical)
        except Exception:
            return None

    if isinstance(explicit, BlockAdapter):
        operation = operation or explicit.operation
        return canonical_operation_name(operation), explicit
    if isinstance(explicit, str):
        operation = operation or explicit
        canonical = canonical_operation_name(operation)
        return canonical, lazy_lookup(canonical, lookup_block_adapter(canonical))
    if callable(explicit):
        # The generic bridge treats a callable as a custom executor.  The
        # operation name is still required for cache/evidence diagnostics; the
        # function's fully-qualified name is a safe fallback for force mode.
        operation = operation or metadata.name
        return canonical_operation_name(operation), explicit

    if operation:
        canonical = canonical_operation_name(operation)
        return canonical, lazy_lookup(canonical, lookup_block_adapter(canonical))

    # Safe auto-by-name: only an exact registered canonical/alias match can
    # select this route.  A normal ``module.function`` decorator name therefore
    # continues through the established generic image wrapper unchanged.
    canonical = canonical_operation_name(metadata.name)
    adapter = lookup_block_adapter(canonical)
    if adapter is None and operation_path(canonical) is not None:
        # Exact operation names are safe to resolve lazily.  Arbitrary
        # decorated helper names remain on the generic path and do not pay
        # the registration cost or gain an accidental algorithm mapping.
        try:
            from .block_adapters import ensure_default_block_adapters

            adapter = ensure_default_block_adapters(canonical)
        except Exception:
            adapter = None
    if adapter is None:
        return None, None
    return canonical, adapter


def _adapter_call_parameters(
    function: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    arrays: tuple[np.ndarray, ...],
    explicit: Any = None,
) -> dict[str, Any]:
    """Infer scalar adapter parameters while excluding image arrays."""

    array_ids = {id(value) for value in arrays}
    values: dict[str, Any] = {}
    try:
        bound = inspect.signature(function).bind_partial(*args, **kwargs)
        bound.apply_defaults()
        arguments = dict(bound.arguments)
        signature_parameters = inspect.signature(function).parameters
    except Exception:
        arguments = dict(kwargs)
        signature_parameters = {}
    for name, value in arguments.items():
        # Arrays that are not part of the selected image-input set are valid
        # adapter configuration (e.g. a 3x3 colour matrix).  Keep them in the
        # parameter mapping; only the actual image inputs are excluded.
        if name in {"self", "cls"} or id(value) in array_ids:
            continue
        if _contains_gpu_buffer(value):
            continue
        # Public wrappers often expose a ``params``/``options`` mapping.  The
        # adapter protocol expects its members directly, so flatten those
        # names while retaining ordinary mapping arguments as a namespaced
        # value.
        parameter = signature_parameters.get(name)
        is_var_keyword = bool(
            parameter is not None and parameter.kind is inspect.Parameter.VAR_KEYWORD
        )
        if (name in {"params", "options", "config"} or is_var_keyword) and isinstance(
            value, Mapping
        ):
            values.update(dict(value))
        else:
            values[name] = value
    if explicit is not None:
        if callable(explicit):
            candidate = None
            for call in (
                lambda: explicit(args, kwargs),
                lambda: explicit(values),
                lambda: explicit(),
            ):
                try:
                    candidate = call()
                    break
                except TypeError:
                    continue
            if candidate is not None:
                if not isinstance(candidate, Mapping):
                    raise TypeError("adapter_params callable must return a mapping")
                values.update(dict(candidate))
        elif isinstance(explicit, Mapping):
            values.update(dict(explicit))
        else:
            raise TypeError("adapter_params must be a mapping or callable")
    return values


def get_compute_block_registry() -> dict[str, Any]:
    """Return a copy of decorated callable metadata for diagnostics."""

    return dict(_REGISTRY)


def current_compute_block_scope() -> Optional[Mapping[str, Any]]:
    """Return the active ``with compute_block():`` scope, if any."""

    return _ACTIVE_SCOPE.get()


class _ComputeBlockDirective:
    def __init__(self, **options: Any) -> None:
        allowed = {
            "name",
            "mode",
            "automatic",
            "halo",
            "min_halo",
            "block_size",
            "threshold_bytes",
            "cache",
            "cache_key",
            "version",
            "retries",
            "fallback",
            "detect_slicing",
            "infer_output_shape",
            "runtime",
            "operation",
            "adapter",
            "adapter_params",
            "require_native_evidence",
            "native_evidence_device",
        }
        unknown = set(options).difference(allowed)
        if unknown:
            raise TypeError(f"unknown compute_block option(s): {sorted(unknown)}")
        self.options = dict(options)
        self._scope_token = None

    def _metadata(self, target: Any) -> ComputeBlockMetadata:
        name = self.options.get("name") or (
            f"{getattr(target, '__module__', '__main__')}."
            f"{getattr(target, '__qualname__', getattr(target, '__name__', 'compute_block'))}"
        )
        mode = str(self.options.get("mode", "auto")).lower().strip()
        if mode not in {"auto", "force", "off"}:
            raise ValueError("compute_block mode must be 'auto', 'force', or 'off'")
        fallback = str(self.options.get("fallback", "full_frame")).lower().strip()
        if fallback not in {"return_none", "full_frame", "error"}:
            raise ValueError(
                "compute_block fallback must be 'return_none', 'full_frame', or 'error'"
            )
        halo = self.options.get("halo", "auto")
        if halo != "auto":
            halo = max(0, int(halo))
        return ComputeBlockMetadata(
            name=str(name),
            mode=mode,
            automatic=bool(self.options.get("automatic", True)),
            halo=halo,
            min_halo=max(0, int(self.options.get("min_halo", 0))),
            block_size=self.options.get("block_size"),
            threshold_bytes=self.options.get("threshold_bytes"),
            cache=bool(self.options.get("cache", True)),
            cache_key=self.options.get("cache_key"),
            version=str(self.options.get("version", "v1")),
            retries=max(0, int(self.options.get("retries", 1))),
            fallback=fallback,
            detect_slicing=bool(self.options.get("detect_slicing", True)),
            infer_output_shape=bool(self.options.get("infer_output_shape", True)),
            runtime=self.options.get("runtime"),
            analysis=analyze_compute_block_source(target),
            operation=(
                None
                if self.options.get("operation") is None
                else str(self.options.get("operation")).strip()
            ),
            adapter=self.options.get("adapter"),
            adapter_params=self.options.get("adapter_params"),
            require_native_evidence=bool(
                self.options.get("require_native_evidence", False)
            ),
            native_evidence_device=(
                None
                if self.options.get("native_evidence_device") is None
                else str(self.options.get("native_evidence_device"))
            ),
        )

    @staticmethod
    def _should_bypass(
        metadata: ComputeBlockMetadata,
        args,
        kwargs,
        *,
        adapter_requested: bool = False,
    ) -> bool:
        if os.environ.get("AUTO_BLOCK", "1").strip().lower() in {
            "0",
            "false",
            "off",
        }:
            return True
        if (
            metadata.mode == "off"
            or not metadata.automatic
            or not metadata.detect_slicing
        ):
            return True
        # AST range/slice analysis is diagnostic only. Automatic mode requires
        # an explicit halo so an arbitrary numeric literal cannot authorize a
        # potentially incorrect neighbourhood tile.
        if (
            metadata.mode == "auto"
            and metadata.halo == "auto"
            and not adapter_requested
        ):
            return True
        if kwargs.get("return_gpu") is True:
            return True
        if any(
            key in kwargs and kwargs[key] is not None
            for key in ("dst", "out", "output")
        ):
            return True
        if metadata.analysis.existing_tile_loop and not adapter_requested:
            # An existing tile loop owns its own lifecycle.  Wrapping its
            # outer frame would double-tile and can change coordinate origin.
            return True
        return False

    @staticmethod
    def _collect_arrays(
        args,
        kwargs,
        *,
        allow_mismatched: bool = False,
        adapter: Any = None,
    ):
        entries = []
        seen = set()
        for path, value, _setter in _walk_call_values(tuple(args), kwargs):
            if _contains_gpu_buffer(value):
                return None, None, "GPU buffer input"
            if not _is_array(value):
                continue
            if id(value) in seen:
                continue
            seen.add(id(value))
            entries.append((path, value))
        if not entries:
            return None, None, "no NumPy image input"
        # Some adapters accept matrix/table configuration arrays (for example
        # a 3x3 colour matrix) in addition to the image itself.  Their
        # contract may declare the number of true image inputs so those
        # configuration arrays remain in ``adapter_params`` instead of being
        # mistaken for another image plane.
        try:
            input_arity = int(getattr(adapter, "metadata", {}).get("input_arity", 0))
        except (TypeError, ValueError, AttributeError):
            input_arity = 0
        if input_arity > 0 and len(entries) > input_arity:
            entries = entries[:input_arity]
        shape = tuple(int(item) for item in entries[0][1].shape[:2])
        if not allow_mismatched and any(
            tuple(item[1].shape[:2]) != shape for item in entries[1:]
        ):
            return None, None, "image inputs have mismatched grid shapes"
        return entries, shape, ""

    def _wrap_function(
        self, function: Callable[..., Any], metadata: ComputeBlockMetadata
    ):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            depth = _DISPATCH_DEPTH.get()
            if depth:
                return function(*args, **kwargs)
            adapter_operation, selected_adapter = _resolve_adapter_selection(metadata)
            adapter_requested = bool(
                adapter_operation
                and (
                    metadata.operation is not None
                    or metadata.adapter is not None
                    or selected_adapter is not None
                )
            )
            if self._should_bypass(
                metadata,
                args,
                kwargs,
                adapter_requested=adapter_requested,
            ):
                return function(*args, **kwargs)

            entries, shape, reason = self._collect_arrays(
                args,
                kwargs,
                allow_mismatched=adapter_requested,
                adapter=selected_adapter,
            )
            if entries is None:
                return function(*args, **kwargs)
            replacements = {id(value): value for _path, value in entries}
            arrays = tuple(value for _path, value in entries)
            array_slots = {id(value): index for index, value in enumerate(arrays)}
            cache_parameters, cache_safe = _call_cache_parameters(
                args, kwargs, array_slots
            )
            halo = metadata.halo
            if halo == "auto":
                # A literal hint is useful for simple neighbourhood kernels;
                # otherwise zero is the conservative default and callers may
                # supply halo=... in the one-line declaration.
                halo = metadata.analysis.literal_halo
            token = _DISPATCH_DEPTH.set(depth + 1)

            def invoke_tile(context):
                tile_args, tile_kwargs = _replace_call(
                    args, kwargs, replacements, context.block
                )
                return function(*tile_args, **tile_kwargs)

            def invoke_full(full_arrays):
                full_args, full_kwargs = _replace_full_frame(
                    args, kwargs, replacements, full_arrays
                )
                return function(*full_args, **full_kwargs)

            runtime = _resolve_runtime(metadata.runtime)

            try:
                if adapter_requested:
                    adapter_halo = int(halo)
                    if selected_adapter is not None:
                        try:
                            adapter_halo = max(
                                0,
                                int(
                                    getattr(
                                        getattr(selected_adapter, "contract", None),
                                        "halo",
                                        adapter_halo,
                                    )
                                ),
                            )
                        except (TypeError, ValueError):
                            adapter_halo = int(halo)
                    adapter_params = _adapter_call_parameters(
                        function,
                        tuple(args),
                        kwargs,
                        arrays,
                        metadata.adapter_params,
                    )
                    result = run_registered_block_adapter(
                        adapter_operation or metadata.name,
                        arrays,
                        runtime=runtime,
                        adapter=(
                            selected_adapter
                            if selected_adapter is not None
                            else metadata.adapter
                        ),
                        block_size=metadata.block_size,
                        params=adapter_params,
                        mode=metadata.mode,
                        automatic=metadata.automatic,
                        min_halo=metadata.min_halo,
                        threshold_bytes=metadata.threshold_bytes,
                        halo=adapter_halo,
                        require_native_evidence=metadata.require_native_evidence,
                        native_evidence_device=metadata.native_evidence_device,
                    )
                    return result

                spec = BlockComputeSpec(
                    metadata.name,
                    invoke_tile,
                    output_shape=None,
                    grid_shape=shape,
                    halo=int(halo),
                    mode=metadata.mode,
                    automatic=metadata.automatic,
                    min_halo=metadata.min_halo,
                    block_size=metadata.block_size,
                    threshold_bytes=metadata.threshold_bytes,
                    cache=bool(metadata.cache and cache_safe),
                    cache_key=metadata.cache_key,
                    version=metadata.version,
                    retries=metadata.retries,
                    infer_output_shape=metadata.infer_output_shape,
                    full_frame=invoke_full,
                    fallback=metadata.fallback,
                    metadata={
                        "compute_block": True,
                        "source_analysis": metadata.analysis.as_dict(),
                        "callable": metadata.name,
                        "call_parameters": cache_parameters,
                        "cache_disabled_reason": (
                            "unsupported runtime argument state"
                            if not cache_safe
                            else ""
                        ),
                    },
                )
                result = run_generic_blocks(
                    arrays,
                    spec,
                    runtime=runtime,
                )
                # ``return_none`` is an explicit policy. Do not turn it into
                # an unexpected full-frame execution at the decorator layer.
                if result is None:
                    if runtime is not None and hasattr(
                        runtime, "set_last_block_execution"
                    ):
                        try:
                            runtime.set_last_block_execution(
                                {
                                    "operation": metadata.name,
                                    "selected": False,
                                    "fallback": metadata.fallback,
                                    "reason": "generic block executor returned no result",
                                    "cache_safe": cache_safe,
                                }
                            )
                        except Exception:
                            pass
                    if metadata.fallback == "return_none":
                        return None
                return function(*args, **kwargs) if result is None else result
            except Exception as exc:
                if runtime is not None and hasattr(runtime, "set_last_block_execution"):
                    try:
                        runtime.set_last_block_execution(
                            {
                                "operation": metadata.name,
                                "selected": False,
                                "fallback": metadata.fallback,
                                "reason": f"decorator exception: {type(exc).__name__}: {exc}",
                                "cache_safe": cache_safe,
                            }
                        )
                    except Exception:
                        pass
                if metadata.fallback == "error":
                    raise
                if adapter_requested and metadata.fallback == "return_none":
                    return None
                return function(*args, **kwargs)
            finally:
                _DISPATCH_DEPTH.reset(token)

        metadata = ComputeBlockMetadata(
            **{
                key: getattr(metadata, key)
                for key in ComputeBlockMetadata.__dataclass_fields__
            }
        )
        wrapped.__compute_block__ = metadata
        wrapped.__compute_block_original__ = function
        wrapped.__compute_block_analysis__ = metadata.analysis
        _REGISTRY[metadata.name] = wrapped
        return wrapped

    def __call__(self, target):
        metadata = self._metadata(target)
        if inspect.isclass(target):
            target.__compute_block__ = metadata
            target.__compute_block_analysis__ = metadata.analysis
            # A callable class has one unambiguous entry point.  Wrapping
            # only ``__call__`` keeps ordinary helper methods untouched while
            # making ``@compute_block`` useful at class scope as well.
            call_method = target.__dict__.get("__call__")
            if call_method is not None and callable(call_method):
                setattr(target, "__call__", self._wrap_function(call_method, metadata))
            _REGISTRY[metadata.name] = target
            return target
        if not callable(target):
            raise TypeError("@compute_block can decorate a function or class")
        return self._wrap_function(target, metadata)

    def __enter__(self):
        self._scope_token = _ACTIVE_SCOPE.set(dict(self.options))
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._scope_token is not None:
            _ACTIVE_SCOPE.reset(self._scope_token)
            self._scope_token = None
        return False


def compute_block(target=None, **options):
    """Mark a function/class for automatic generic block dispatch.

    Supported forms are ``@compute_block``, ``@compute_block(halo=8)``, and
    ``with compute_block(halo=8):``.  The latter exposes scope metadata for
    nested runtime helpers; it does not rewrite arbitrary Python statements.
    """

    directive = _ComputeBlockDirective(**options)
    if target is None:
        return directive
    return directive(target)


__all__ = [
    "ComputeBlockAnalysis",
    "ComputeBlockMetadata",
    "analyze_compute_block_source",
    "compute_block",
    "current_compute_block_scope",
    "get_compute_block_registry",
]
