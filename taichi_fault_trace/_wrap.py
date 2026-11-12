"""Transparent instrumentation of the taichi runtime surface.

The tracer wraps Python callables in the ``taichi`` package (and optional
extra modules) so that every runtime call is recorded in a per-thread ring
stack.  On an exception the innermost wrapper builds a rich report while the
full call chain and argument snapshots are still available.

The wrapper is deliberately transparent: it preserves ``__wrapped__``,
generator/coroutine semantics, and the original exception type.  Enrichment
never replaces the exception unless ``TAICHI_FAULT_RAISE=1``.
"""

from __future__ import annotations

import faulthandler
import functools
import inspect
import linecache
import os
import sys
import threading
import time
import traceback
import types
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from ._config import TraceConfig, current_config
from ._report import CallRecord, FrameInfo, build_report, emit
from ._summarize import summarize, summarize_mapping

_RUNTIME_SUBMODULES = {
    "taichi.aot",
    "taichi.aot_engine",
    "taichi.aot_dispatch",
    "taichi.aot_module_loader",
    "taichi.native_bridge",
    "taichi.tcm_loader",
    "taichi.tcm_artifacts",
    "taichi.buffer_session",
    "taichi.block",
    "taichi.block_adapters",
    "taichi.block_cache",
    "taichi.block_grid",
    "taichi.compute_block",
    "taichi.generic_block",
    "taichi.memory",
    "taichi.memory_policy",
    "taichi.lifecycle",
    "taichi.device_invocation",
    "taichi.onnx_native_graph",
    "taichi.engine",
    "taichi.allocator",
    "taichi.capabilities",
    "taichi.backend_manager",
    "taichi.residency",
    "taichi.auto_pipeline",
    "taichi.pipeline_scheduler",
    "taichi.device_selection",
    "taichi.artifact_targets",
    "taichi.runtime_paths",
    "taichi.compat_runtime",
    "taichi.descriptor_parity",
    "taichi.tcm_contract",
    "taichi.native_evidence",
    "taichi._api",
}

# Private methods worth instrumenting: they carry the real failure policy.
_INCLUDE_PRIVATE_METHODS = {
    "_require_live",
    "_view_sync",
    "_view_guard",
    "_run_impl",
    "_run_device_impl",
    "_raise_native_engine_error",
    "_assign_static_bindings",
}

_SKIP_EXCEPTIONS = (KeyboardInterrupt, SystemExit, GeneratorExit)
_TRACER_DIR = os.path.dirname(os.path.abspath(__file__))

_LOCAL = threading.local()
_STATE_LOCK = threading.RLock()
_INSTALLED = False
_FINDER: "_WrappingFinder | None" = None
_REGISTRY: list[tuple[Any, str, Any]] = []
_FAULT_FILE = None


@dataclass
class _RawCall:
    qualname: str
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    started: float = field(default_factory=time.perf_counter)
    depth: int = 0
    names: tuple[str, ...] = ()

    def __repr__(self) -> str:  # keep fault reports compact
        return f"<call {self.qualname}>"


def _stack() -> list[_RawCall]:
    stack = getattr(_LOCAL, "stack", None)
    if stack is None:
        stack = []
        _LOCAL.stack = stack
    return stack


def _enter(
    qualname: str,
    args: tuple,
    kwargs: dict,
    names: tuple[str, ...] = (),
) -> _RawCall:
    stack = _stack()
    record = _RawCall(qualname, args, kwargs, depth=len(stack) + 1, names=names)
    stack.append(record)
    return record


def _param_names(fn: Callable) -> tuple[str, ...]:
    try:
        return tuple(inspect.signature(fn).parameters)
    except Exception:
        return ()


def _leave(record: _RawCall) -> None:
    stack = _stack()
    if stack and stack[-1] is record:
        stack.pop()
    else:
        try:
            stack.remove(record)
        except ValueError:
            pass


def _call_summaries(stack: list[_RawCall], config: TraceConfig) -> list[CallRecord]:
    now = time.perf_counter()
    result: list[CallRecord] = []
    for record in stack:
        arguments: tuple[tuple[str, str], ...] = ()
        if config.full and config.capture_args:
            arguments = tuple(
                _argument_items(record, config)
            )
        result.append(
            CallRecord(
                qualname=record.qualname,
                arguments=arguments,
                elapsed_ms=(now - record.started) * 1000.0,
                depth=record.depth,
            )
        )
    return result


def _argument_items(record: _RawCall, config: TraceConfig):
    try:
        for index, value in enumerate(record.args):
            if index < len(record.names):
                name = record.names[index]
            else:
                name = f"arg{index + 1}"
            yield name, summarize(value, limit=config.max_value_chars, config=config)
        for name, value in record.kwargs.items():
            yield str(name), summarize(
                value, limit=config.max_value_chars, config=config
            )
    except Exception:
        return


def _looks_like_engine(value: Any) -> bool:
    try:
        if value is None:
            return False
        name = type(value).__name__
        if name in {"AOTEngine", "GraphEngine", "_EngineHandle"}:
            return True
        return (
            hasattr(value, "handle")
            and hasattr(value, "arch")
            and hasattr(value, "generation")
        )
    except Exception:
        return False


def _find_engine(stack: list[_RawCall]) -> Any:
    for record in reversed(stack):
        candidates = list(record.args) + list(record.kwargs.values())
        for value in candidates:
            if _looks_like_engine(value):
                return value
        for value in candidates:
            try:
                nested = getattr(value, "engine", None)
            except Exception:
                nested = None
            if _looks_like_engine(nested):
                return nested
    return None


def _artifact_candidates(stack: list[_RawCall]) -> list[Any]:
    values: list[Any] = []
    for record in stack[-5:]:
        values.extend(record.args)
        values.extend(record.kwargs.values())
    return values


def _frame_info(
    frame, lineno: int, config: TraceConfig, tracked_prefixes: tuple[str, ...]
) -> FrameInfo:
    filename = frame.f_code.co_filename
    source = ""
    try:
        source = linecache.getline(filename, lineno, frame.f_globals).strip()
    except Exception:
        source = ""
    locals_summary: tuple[tuple[str, str], ...] = ()
    if config.capture_locals:
        locals_summary = tuple(_locals_items(frame, config, tracked_prefixes))
    return FrameInfo(
        filename=filename,
        lineno=lineno,
        function=frame.f_code.co_name,
        source=source,
        locals=locals_summary,
    )


def _frame_infos(
    exc: BaseException,
    config: TraceConfig,
    *,
    tracked_prefixes: tuple[str, ...],
    live_from=None,
) -> list[FrameInfo]:
    """Collect traceback frames plus the still-live caller chain.

    The report is built inside the innermost wrapper, so ``exc.__traceback__``
    only contains frames up to the raise point.  Walking the live stack from
    the wrapper's caller restores the application frames (``close`` ->
    ``_view_sync`` -> ...) that have not unwound yet.
    """

    frames: list[FrameInfo] = []
    seen: set[tuple[str, int, str]] = set()

    def _append(frame, lineno: int) -> bool:
        filename = frame.f_code.co_filename
        if filename.startswith(_TRACER_DIR):
            return False
        key = (filename, int(lineno), frame.f_code.co_name)
        if key in seen:
            return False
        seen.add(key)
        try:
            frames.append(_frame_info(frame, int(lineno), config, tracked_prefixes))
        except Exception:
            return False
        return True

    try:
        walked = list(traceback.walk_tb(exc.__traceback__))
    except Exception:
        walked = []
    for frame, lineno in walked[-config.max_frames :]:
        if len(frames) >= config.max_frames:
            break
        try:
            _append(frame, lineno)
        except Exception:
            continue

    frame = live_from
    while frame is not None and len(frames) < config.max_frames:
        try:
            _append(frame, frame.f_lineno)
        except Exception:
            pass
        frame = frame.f_back
    return frames


def _locals_items(frame, config: TraceConfig, tracked_prefixes: tuple[str, ...]):
    tracked = any(
        frame.f_code.co_filename.startswith(prefix) for prefix in tracked_prefixes
    )
    items = list(frame.f_locals.items())
    if not tracked:
        items = items[-config.max_locals :]
    else:
        items = items[: config.max_locals]
    for name, value in items:
        if name in {"__builtins__", "__loader__", "__spec__", "__package__"}:
            continue
        try:
            yield name, summarize(value, limit=config.max_value_chars, config=config)
        except Exception:
            yield name, "<error>"


def _tracked_prefixes(config: TraceConfig) -> tuple[str, ...]:
    roots = {sys.prefix, os.path.dirname(os.path.abspath(__file__))}
    modules = ["taichi", *config.extra_modules]
    for name in modules:
        module = sys.modules.get(name)
        origin = getattr(module, "__file__", None)
        if origin:
            roots.add(os.path.dirname(origin))
    return tuple(sorted(roots))


def _handle_exception(
    exc: BaseException,
    record: _RawCall,
    config: TraceConfig,
) -> None:
    if isinstance(exc, _SKIP_EXCEPTIONS):
        return
    if getattr(sys, "is_finalizing", lambda: False)():
        return
    if getattr(sys, "meta_path", None) is None:
        return
    if getattr(exc, "__taichi_fault_reported__", False):
        return
    try:
        stack = list(_stack())
        if not stack or stack[-1] is not record:
            stack.append(record)
        calls = _call_summaries(stack, config)
        live_from = None
        try:
            live_from = sys._getframe(1).f_back
        except Exception:
            live_from = None
        frames = _frame_infos(
            exc,
            config,
            tracked_prefixes=_tracked_prefixes(config),
            live_from=live_from,
        )
        elapsed_ms = (time.perf_counter() - stack[0].started) * 1000.0
        report = build_report(
            exc,
            calls=calls,
            frames=frames,
            artifact_candidates=_artifact_candidates(stack),
            elapsed_ms=elapsed_ms,
            engine=_find_engine(stack),
            config=config,
        )
        emit(report, exc, config=config)
        exc.__taichi_fault_reported__ = True
        if config.raise_enriched:
            from . import TaichiFaultError

            raise TaichiFaultError(report) from exc
    except BaseException as secondary:  # pragma: no cover - defensive
        if isinstance(secondary, _SKIP_EXCEPTIONS):
            raise
        try:
            print(
                f"[taichi_fault_trace] gagal menyusun laporan: "
                f"{type(secondary).__name__}: {secondary}",
                file=sys.stderr,
            )
        except Exception:
            pass


# --------------------------------------------------------------------------
# wrapper factories
# --------------------------------------------------------------------------

def _mark(wrapper: Callable, original: Callable, qualname: str) -> Callable:
    try:
        functools.update_wrapper(wrapper, original)
    except Exception:
        pass
    wrapper.__taichi_fault_trace_wrapped__ = True
    wrapper.__taichi_fault_trace_original__ = original
    wrapper.__taichi_fault_trace_qualname__ = qualname
    return wrapper


def _sync_wrapper(
    fn: Callable, qualname: str, config: TraceConfig, names: tuple[str, ...] = ()
) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        record = _enter(qualname, args, kwargs, names)
        try:
            return fn(*args, **kwargs)
        except BaseException as exc:
            _handle_exception(exc, record, config)
            raise
        finally:
            _leave(record)

    return _mark(wrapper, fn, qualname)


def _generator_wrapper(
    fn: Callable, qualname: str, config: TraceConfig, names: tuple[str, ...] = ()
) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        record = _enter(qualname, args, kwargs, names)
        try:
            yield from fn(*args, **kwargs)
        except BaseException as exc:
            _handle_exception(exc, record, config)
            raise
        finally:
            _leave(record)

    return _mark(wrapper, fn, qualname)


def _async_wrapper(
    fn: Callable, qualname: str, config: TraceConfig, names: tuple[str, ...] = ()
) -> Callable:
    @functools.wraps(fn)
    async def wrapper(*args, **kwargs):
        record = _enter(qualname, args, kwargs, names)
        try:
            return await fn(*args, **kwargs)
        except BaseException as exc:
            _handle_exception(exc, record, config)
            raise
        finally:
            _leave(record)

    return _mark(wrapper, fn, qualname)


def _make_wrapper(fn: Callable, qualname: str, config: TraceConfig) -> Callable | None:
    try:
        if getattr(fn, "__taichi_fault_trace_wrapped__", False):
            return None
        names = _param_names(fn)
        if inspect.isgeneratorfunction(fn):
            return _generator_wrapper(fn, qualname, config, names)
        if inspect.iscoroutinefunction(fn):
            return _async_wrapper(fn, qualname, config, names)
        if inspect.isfunction(fn) or inspect.ismethod(fn) or inspect.isbuiltin(fn):
            return _sync_wrapper(fn, qualname, config, names)
    except Exception:
        return None
    return None


def _wrap_callable_attr(
    owner: Any, name: str, value: Any, qualname: str, config: TraceConfig
) -> bool:
    if isinstance(value, staticmethod):
        original = value.__func__
        wrapper = _make_wrapper(original, qualname, config)
        if wrapper is None:
            return False
        setattr(owner, name, staticmethod(wrapper))
        _REGISTRY.append((owner, name, value))
        return True
    if isinstance(value, classmethod):
        original = value.__func__
        wrapper = _make_wrapper(original, qualname, config)
        if wrapper is None:
            return False
        setattr(owner, name, classmethod(wrapper))
        _REGISTRY.append((owner, name, value))
        return True
    if inspect.isfunction(value):
        wrapper = _make_wrapper(value, qualname, config)
        if wrapper is None:
            return False
        try:
            setattr(owner, name, wrapper)
        except Exception:
            return False
        _REGISTRY.append((owner, name, value))
        return True
    return False


def _wrap_class(cls: type, qualname_prefix: str, config: TraceConfig) -> list[str]:
    wrapped: list[str] = []
    for name, value in list(vars(cls).items()):
        if name.startswith("__"):
            continue
        if name.startswith("_") and name not in _INCLUDE_PRIVATE_METHODS:
            continue
        if isinstance(value, property):
            continue
        if _wrap_callable_attr(cls, name, value, f"{qualname_prefix}.{name}", config):
            wrapped.append(f"{qualname_prefix}.{name}")
    return wrapped


def _instrument_module(module: types.ModuleType, config: TraceConfig) -> list[str]:
    name = module.__name__
    wrapped: list[str] = []
    for attr_name, value in list(vars(module).items()):
        if attr_name.startswith("__"):
            continue
        if inspect.ismodule(value):
            continue
        qualname = f"{name}.{attr_name}"
        if inspect.isclass(value):
            if getattr(value, "__module__", None) != name:
                continue
            if issubclass(value, BaseException):
                continue
            wrapped.extend(_wrap_class(value, qualname, config))
            continue
        if isinstance(value, (staticmethod, classmethod)) or inspect.isfunction(value):
            if _wrap_callable_attr(module, attr_name, value, qualname, config):
                wrapped.append(qualname)
    return wrapped


def _wanted(fullname: str, config: TraceConfig) -> bool:
    if fullname == "taichi":
        return True
    if fullname in _RUNTIME_SUBMODULES:
        return True
    return fullname in config.extra_modules


class _WrappingLoader:
    """Delegating loader that instruments a module right after execution."""

    def __init__(self, loader, fullname: str):
        self._loader = loader
        self._fullname = fullname

    def __getattr__(self, name):
        return getattr(self._loader, name)

    def create_module(self, spec):
        return self._loader.create_module(spec)

    def exec_module(self, module):
        self._loader.exec_module(module)
        try:
            _instrument_module(module, current_config())
        except Exception:
            pass


class _WrappingFinder:
    """Meta path finder that defers instrumentation until the module exists."""

    def __init__(self, config: TraceConfig):
        self._config = config
        self._busy: set[str] = set()

    def find_spec(self, fullname, path=None, target=None):
        if not _wanted(fullname, self._config):
            return None
        if fullname in self._busy:
            return None
        self._busy.add(fullname)
        try:
            import importlib.util

            spec = importlib.util.find_spec(fullname)
        except Exception:
            return None
        finally:
            self._busy.discard(fullname)
        if spec is None or spec.loader is None:
            return None
        origin = str(getattr(spec, "origin", "") or "")
        if origin.endswith((".pyd", ".so", ".dylib", ".dll")):
            return spec
        try:
            spec.loader = _WrappingLoader(spec.loader, fullname)
        except Exception:
            pass
        return spec

    def invalidate_caches(self):
        return None


# --------------------------------------------------------------------------
# public install surface
# --------------------------------------------------------------------------

def install(config: TraceConfig | None = None) -> list[str]:
    """Instrument all loaded runtime modules and future imports."""

    global _INSTALLED, _FINDER, _FAULT_FILE
    config = config or current_config()
    if not config.enabled:
        return []
    with _STATE_LOCK:
        wrapped: list[str] = []
        for name in sorted(sys.modules):
            module = sys.modules.get(name)
            if not isinstance(module, types.ModuleType):
                continue
            if not _wanted(name, config):
                continue
            try:
                wrapped.extend(_instrument_module(module, config))
            except Exception:
                continue

        if _FINDER is None:
            _FINDER = _WrappingFinder(config)
            sys.meta_path.insert(0, _FINDER)

        _install_hooks(config)

        if config.faulthandler and _FAULT_FILE is None:
            _FAULT_FILE = _enable_faulthandler(config)

        _INSTALLED = True
        return wrapped


def uninstall() -> int:
    """Restore every wrapped attribute recorded by the tracer."""

    global _INSTALLED, _FINDER
    with _STATE_LOCK:
        restored = 0
        for owner, name, original in reversed(_REGISTRY):
            try:
                setattr(owner, name, original)
                restored += 1
            except Exception:
                continue
        _REGISTRY.clear()
        if _FINDER is not None:
            try:
                sys.meta_path.remove(_FINDER)
            except ValueError:
                pass
            _FINDER = None
        _INSTALLED = False
        return restored


def is_installed() -> bool:
    return _INSTALLED


def instrument(target: Any, config: TraceConfig | None = None) -> list[str]:
    """Instrument a module, class, or object on demand."""

    config = config or current_config()
    with _STATE_LOCK:
        if isinstance(target, types.ModuleType):
            return _instrument_module(target, config)
        if inspect.isclass(target):
            return _wrap_class(
                target,
                f"{getattr(target, '__module__', '?')}.{target.__name__}",
                config,
            )
        if isinstance(target, (str,)):
            module = sys.modules.get(target)
            if module is None:
                import importlib

                module = importlib.import_module(target)
            return _instrument_module(module, config)
        # Arbitrary object: wrap its instance-bound public callables.
        wrapped: list[str] = []
        prefix = f"{type(target).__module__}.{type(target).__name__}"
        for name in dir(target):
            if name.startswith("_"):
                continue
            try:
                value = getattr(target, name)
            except Exception:
                continue
            if not inspect.ismethod(value):
                continue
            wrapper = _make_wrapper(value, f"{prefix}.{name}", config)
            if wrapper is None:
                continue
            try:
                setattr(target, name, types.MethodType(wrapper, target))
                wrapped.append(f"{prefix}.{name}")
            except Exception:
                continue
        return wrapped


class trace_scope:
    """Logical scope that turns any escaping exception into a report."""

    def __init__(self, name: str):
        self.name = name
        self._record: _RawCall | None = None

    def __enter__(self):
        self._record = _enter(f"scope:{self.name}", (), {})
        return self

    def __exit__(self, exc_type, exc, tb):
        config = current_config()
        try:
            if exc is not None and self._record is not None:
                if tb is not None and exc.__traceback__ is None:
                    exc.__traceback__ = tb
                _handle_exception(exc, self._record, config)
        finally:
            if self._record is not None:
                _leave(self._record)
                self._record = None
        return False


def trace(func: Callable) -> Callable:
    """Decorator for application functions outside the taichi package."""

    config = current_config()
    qualname = f"{func.__module__}.{getattr(func, '__qualname__', func.__name__)}"
    wrapper = _make_wrapper(func, qualname, config)
    return wrapper if wrapper is not None else func


# --------------------------------------------------------------------------
# hooks
# --------------------------------------------------------------------------

def _install_hooks(config: TraceConfig) -> None:
    if getattr(_install_hooks, "_done", False):
        return
    _install_hooks._done = True  # type: ignore[attr-defined]

    previous_hook = sys.excepthook

    def excepthook(exc_type, exc, tb):
        try:
            if config.render_on_uncaught and not getattr(
                exc, "__taichi_fault_reported__", False
            ):
                frames = _frame_infos(
                    exc, config, tracked_prefixes=_tracked_prefixes(config)
                )
                report = build_report(
                    exc,
                    calls=[],
                    frames=frames,
                    artifact_candidates=[],
                    elapsed_ms=0.0,
                    engine=_find_engine([]),
                    config=config,
                )
                emit(report, exc, config=config, force=True)
        except Exception:
            pass
        previous_hook(exc_type, exc, tb)

    sys.excepthook = excepthook

    previous_thread_hook = threading.excepthook

    def thread_hook(args):
        try:
            exc = args.exc_value
            if config.render_on_uncaught and exc is not None and not getattr(
                exc, "__taichi_fault_reported__", False
            ):
                frames = _frame_infos(
                    exc, config, tracked_prefixes=_tracked_prefixes(config)
                )
                report = build_report(
                    exc,
                    calls=[],
                    frames=frames,
                    artifact_candidates=[],
                    elapsed_ms=0.0,
                    engine=None,
                    config=config,
                )
                emit(report, exc, config=config, force=True)
        except Exception:
            pass
        previous_thread_hook(args)

    threading.excepthook = thread_hook

    previous_unraisable = sys.unraisablehook

    def unraisable_hook(hook_args):
        try:
            exc = hook_args.exc_value
            if config.render_on_uncaught and exc is not None and not getattr(
                exc, "__taichi_fault_reported__", False
            ):
                frames = _frame_infos(
                    exc, config, tracked_prefixes=_tracked_prefixes(config)
                )
                report = build_report(
                    exc,
                    calls=[],
                    frames=frames,
                    artifact_candidates=[],
                    elapsed_ms=0.0,
                    engine=None,
                    config=config,
                )
                emit(report, exc, config=config, force=True)
        except Exception:
            pass
        previous_unraisable(hook_args)

    sys.unraisablehook = unraisable_hook


def _enable_faulthandler(config: TraceConfig):
    try:
        directory = Path(config.report_dir)
        directory.mkdir(parents=True, exist_ok=True)
        handle = open(directory / "faulthandler.log", "a", encoding="utf-8", buffering=1)
        handle.write(
            f"\n=== taichi_fault_trace pid={os.getpid()} "
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===\n"
        )
        faulthandler.enable(file=handle, all_threads=True)
        return handle
    except Exception:
        return None


def current_call_chain() -> list[str]:
    """Return the current thread's wrapped call chain (outermost first)."""

    return [record.qualname for record in _stack()]


def wrapped_inventory() -> list[str]:
    """List every qualified name the tracer currently instruments."""

    found: set[str] = set()
    for module in list(sys.modules.values()):
        if not isinstance(module, types.ModuleType):
            continue
        for value in list(vars(module).values()):
            if getattr(value, "__taichi_fault_trace_wrapped__", False):
                name = getattr(value, "__taichi_fault_trace_qualname__", "")
                if name:
                    found.add(name)
                continue
            if not inspect.isclass(value):
                continue
            for attribute in list(vars(value).values()):
                target = attribute
                if isinstance(attribute, (staticmethod, classmethod)):
                    target = attribute.__func__
                if getattr(target, "__taichi_fault_trace_wrapped__", False):
                    name = getattr(target, "__taichi_fault_trace_qualname__", "")
                    if name:
                        found.add(name)
    return sorted(found)


__all__ = [
    "install",
    "uninstall",
    "is_installed",
    "instrument",
    "trace",
    "trace_scope",
    "current_call_chain",
    "wrapped_inventory",
]
