"""Fail-closed native graph dispatch seam for compression codecs.

The existing compression modules and NumPy ``_dispatch`` path are intentionally
untouched.  This module defines the request contract for a future additive
``AOTEngine.run_native_graph(request)`` method.  Until that method exists, the
seam raises :class:`NativeDispatchUnavailable`; it never guesses, imports
NumPy, or falls back to the legacy graph wrapper.
"""

from __future__ import annotations

import ctypes
import importlib.util
import math
import os
import struct
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Optional, Protocol, Sequence, Tuple


def _load_native_codec_abi() -> Any:
    """Load the ABI source without executing the legacy taichi_aot facade.

    Importing ``taichi_vision.taichi_aot.native_codec_abi`` through Python's
    normal package machinery first executes ``taichi_aot/__init__.py``.  That
    compatibility facade imports the legacy NumPy-backed engine, which would
    make an explicitly native compression import fail the no-NumPy contract
    before a graph is even requested.  The ABI module itself is standard
    library only, so load that source directly for this additive seam.  The
    standalone verifier may already have installed the qualified module; in
    that case reusing it preserves class identity for its isolated test.
    """

    qualified_name = "taichi_vision.taichi_aot.native_codec_abi"
    existing = sys.modules.get(qualified_name)
    if existing is not None and hasattr(existing, "NativeTensor"):
        return existing
    private_name = "taichi_vision._native_codec_abi_direct"
    existing = sys.modules.get(private_name)
    if existing is not None and hasattr(existing, "NativeTensor"):
        return existing
    root = Path(__file__).resolve().parents[3]
    source = root / "taichi_vision" / "taichi_aot" / "native_codec_abi.py"
    spec = importlib.util.spec_from_file_location(private_name, source)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load native codec ABI source: {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[private_name] = module
    spec.loader.exec_module(module)
    return module


_NATIVE_CODEC_ABI = _load_native_codec_abi()
ABI_VERSION = _NATIVE_CODEC_ABI.ABI_VERSION
NativeTensor = _NATIVE_CODEC_ABI.NativeTensor
NativeTensorDescriptor = _NATIVE_CODEC_ABI.NativeTensorDescriptor


NATIVE_ENGINE_METHOD = "run_native_graph"
NativeScalar = bool | int | float

__all__ = [
    "NATIVE_ENGINE_METHOD",
    "NativeDispatchContractError",
    "NativeDispatchError",
    "NativeDispatchUnavailable",
    "NativeAOTEngine",
    "NativeGraphEngine",
    "NativeGraphRequest",
    "build_native_request",
    "dispatch_native_graph",
    "native_dispatch_report",
    "native_engine_available",
    "run_self_tests",
]


class NativeDispatchError(RuntimeError):
    """Base error for the native codec dispatch seam."""


class NativeDispatchUnavailable(NativeDispatchError):
    """Raised when the additive native engine API is not installed."""


class NativeDispatchContractError(NativeDispatchError):
    """Raised when a request cannot be represented by the native ABI."""


@dataclass(frozen=True, slots=True)
class NativeGraphRequest:
    """A backend-neutral request for the future native engine method.

    The request retains the ``NativeTensor`` objects for the duration of the
    call, so borrowed owners cannot be collected while a native engine is
    reading them.  An additive engine implementation should consume this
    object through the documented fields and return its normal native result.
    """

    module_name: str
    graph_name: str
    inputs: Tuple[NativeTensor, ...]
    outputs: Tuple[NativeTensor, ...] = ()
    scalars: Mapping[str, NativeScalar] = MappingProxyType({})
    backend: Optional[str] = None
    input_names: Tuple[str, ...] = ()
    output_names: Tuple[str, ...] = ()
    abi_version: int = ABI_VERSION

    def __post_init__(self) -> None:
        if not isinstance(self.module_name, str) or not self.module_name.strip():
            raise NativeDispatchContractError("module_name must be a non-empty string")
        if not isinstance(self.graph_name, str) or not self.graph_name.strip():
            raise NativeDispatchContractError("graph_name must be a non-empty string")
        if self.backend is not None and (
            not isinstance(self.backend, str) or not self.backend.strip()
        ):
            raise NativeDispatchContractError("backend must be a non-empty string or None")
        if self.abi_version != ABI_VERSION:
            raise NativeDispatchContractError(
                f"unsupported native ABI version {self.abi_version}; expected {ABI_VERSION}"
            )

        try:
            normalized_inputs = tuple(self.inputs)
            normalized_outputs = tuple(self.outputs)
        except TypeError as exc:
            raise NativeDispatchContractError("inputs and outputs must be iterable") from exc
        if not normalized_inputs:
            raise NativeDispatchContractError("native graph requests require at least one input")
        for label, tensors in (("inputs", normalized_inputs), ("outputs", normalized_outputs)):
            for index, tensor in enumerate(tensors):
                if not isinstance(tensor, NativeTensor):
                    raise NativeDispatchContractError(
                        f"{label}[{index}] must be a NativeTensor"
                    )
                if tensor.released:
                    raise NativeDispatchContractError(
                        f"{label}[{index}] is already released"
                    )

        if not isinstance(self.scalars, Mapping):
            raise NativeDispatchContractError("scalars must be a mapping")
        normalized_scalars: dict[str, NativeScalar] = {}
        for name, value in self.scalars.items():
            if not isinstance(name, str) or not name.strip():
                raise NativeDispatchContractError("scalar names must be non-empty strings")
            if isinstance(value, bool):
                normalized_scalars[name] = value
            elif isinstance(value, int):
                normalized_scalars[name] = value
            elif isinstance(value, float) and math.isfinite(value):
                normalized_scalars[name] = value
            else:
                raise NativeDispatchContractError(
                    f"scalar {name!r} must be a finite float, integer, or boolean"
                )

        object.__setattr__(self, "inputs", normalized_inputs)
        object.__setattr__(self, "outputs", normalized_outputs)
        object.__setattr__(self, "scalars", MappingProxyType(normalized_scalars))

        normalized_input_names = tuple(self.input_names)
        normalized_output_names = tuple(self.output_names)
        if not normalized_input_names:
            normalized_input_names = tuple(f"input{index}" for index in range(len(normalized_inputs)))
        if not normalized_output_names:
            normalized_output_names = tuple(f"output{index}" for index in range(len(normalized_outputs)))
        if len(normalized_input_names) != len(normalized_inputs):
            raise NativeDispatchContractError(
                "input_names must contain exactly one name per input tensor"
            )
        if len(normalized_output_names) != len(normalized_outputs):
            raise NativeDispatchContractError(
                "output_names must contain exactly one name per output tensor"
            )
        for label, names in (("input_names", normalized_input_names), ("output_names", normalized_output_names)):
            for index, name in enumerate(names):
                if not isinstance(name, str) or not name.strip():
                    raise NativeDispatchContractError(
                        f"{label}[{index}] must be a non-empty string"
                    )
        if len(set(normalized_input_names + normalized_output_names + tuple(self.scalars))) != (
            len(normalized_input_names) + len(normalized_output_names) + len(self.scalars)
        ):
            raise NativeDispatchContractError(
                "native graph argument names must be unique"
            )
        object.__setattr__(self, "input_names", normalized_input_names)
        object.__setattr__(self, "output_names", normalized_output_names)

    @property
    def input_descriptors(self) -> Tuple[NativeTensorDescriptor, ...]:
        return tuple(tensor.to_descriptor() for tensor in self.inputs)

    @property
    def output_descriptors(self) -> Tuple[NativeTensorDescriptor, ...]:
        return tuple(tensor.to_descriptor() for tensor in self.outputs)

    def metadata(self) -> dict[str, Any]:
        """Return metadata without copying tensor payload bytes."""

        return {
            "abi_version": self.abi_version,
            "module_name": self.module_name,
            "graph_name": self.graph_name,
            "backend": self.backend,
            "input_names": self.input_names,
            "output_names": self.output_names,
            "inputs": tuple(descriptor.as_dict() for descriptor in self.input_descriptors),
            "outputs": tuple(descriptor.as_dict() for descriptor in self.output_descriptors),
            "scalars": dict(self.scalars),
        }


class NativeGraphEngine(Protocol):
    """Structural contract for the future additive engine API."""

    def run_native_graph(self, request: NativeGraphRequest) -> Any:
        ...


class _NativeDynamicArg(ctypes.Structure):
    """Private mirror of the bridge DynamicArg layout.

    This is intentionally kept local to the additive adapter.  The existing
    ``engine.py`` mirror remains the compatibility path for legacy callers;
    the two structures are ABI-compatible and neither changes the public
    Python engine API.
    """

    _fields_ = [
        ("name", ctypes.c_char_p),
        ("arg_type", ctypes.c_int),
        ("dtype", ctypes.c_int),
        ("dim_count", ctypes.c_int),
        ("shape", ctypes.c_int32 * 8),
        ("elem_dim_count", ctypes.c_int),
        ("elem_shape", ctypes.c_int32 * 8),
        ("is_vector", ctypes.c_int),
        ("vector_dim", ctypes.c_int),
        ("val_u64", ctypes.c_uint64),
    ]


_NATIVE_DTYPE_CODES = {
    "f32": 0,
    "i32": 1,
    "u8": 2,
    "u16": 3,
    "i16": 4,
    "f16": 5,
}
_NATIVE_ARCH_IDS = {
    "vulkan": 0,
    "cuda": 1,
    "cpu": 2,
    "opengl": 3,
    "gles": 4,
}


def _native_backend_name(backend: Optional[str]) -> str:
    value = str(backend or os.environ.get("AOT_ARCH", "cpu")).strip().lower()
    aliases = {"host": "cpu", "llvm": "cpu", "gl": "opengl"}
    value = aliases.get(value, value)
    if value == "auto":
        value = str(os.environ.get("TARGET_BACKEND", "cpu")).strip().lower()
        value = aliases.get(value, value)
    if value not in _NATIVE_ARCH_IDS:
        raise NativeDispatchUnavailable(
            f"native codec backend {value!r} is not supported by the additive bridge"
        )
    return value


def _native_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _native_library_path(backend: str, device_id: int = 0) -> tuple[Path, list[Any]]:
    """Resolve and load no-Python-dependency bridge prerequisites."""

    root = _native_repo_root() / "taichi_vision" / "taichi_algorithm" / "aot_py" / "aot_dll"
    extension = ".dll" if os.name == "nt" else ".dylib" if sys.platform == "darwin" else ".so"
    explicit = os.environ.get("AOT_ENGINE_DLL", "").strip()
    backend_dir = root / backend
    target_variant = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
    target_dir = root / target_variant if target_variant else None
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    staged_bundle = None
    try:
        from taichi_vision.llvm20_runtime_paths import bundle_root as staged_bundle_root

        staged_target = target_variant or _native_target_variant(backend, device_id)
        staged_bundle = staged_bundle_root(staged_target)
    except (ImportError, OSError, ValueError):
        staged_bundle = None
    if staged_bundle is not None:
        candidates.append(staged_bundle / f"taichi_aot_engine{extension}")
    if target_dir is not None:
        candidates.append(target_dir / f"taichi_aot_engine{extension}")
    # Legacy repository bridges are opt-in once an LLVM20 release exists;
    # silently mixing them with an LLVM20 runtime is an ABI violation.
    if staged_bundle is None or os.environ.get("PIXEL_REFINE_AOT_ALLOW_LEGACY_ARTIFACTS") == "1":
        candidates.extend(
            (
                backend_dir / f"taichi_aot_engine{extension}",
                root / f"taichi_aot_engine{extension}",
            )
        )
    library = next((candidate.resolve() for candidate in candidates if candidate.is_file()), None)
    if library is None:
        attempted = ", ".join(str(candidate) for candidate in candidates)
        raise NativeDispatchUnavailable(
            "native codec bridge was not found; checked: " + attempted
        )

    dll_dirs: list[Any] = []
    if os.name == "nt" and hasattr(os, "add_dll_directory"):
        directories = [backend_dir, target_dir, root]
        if staged_bundle is not None:
            directories.extend(
                (
                    staged_bundle,
                    staged_bundle / "python" / "taichi" / "_lib" / "core",
                    staged_bundle / "python" / "taichi" / "_lib" / "c_api" / "bin",
                )
            )
        for directory in directories:
            if directory is not None and directory.is_dir():
                try:
                    dll_dirs.append(os.add_dll_directory(str(directory)))
                except OSError:
                    pass
        # Taichi's C API is a native runtime dependency, not a Python codec
        # dependency.  Discover its directory without importing Taichi.
        try:
            spec = importlib.util.find_spec("taichi")
            if spec is not None and spec.origin:
                taichi_root = Path(spec.origin).resolve().parent
                for directory in (
                    taichi_root / "_lib" / "c_api" / "bin",
                    taichi_root / "_lib" / "runtime",
                ):
                    if directory.is_dir():
                        dll_dirs.append(os.add_dll_directory(str(directory)))
                runtime = taichi_root / "_lib" / "runtime"
                if runtime.is_dir():
                    os.environ.setdefault("TI_LIB_DIR", str(runtime))
        except (ImportError, OSError, ValueError):
            pass
    return library, dll_dirs


def _native_target_variant(backend: str, device_id: int) -> str:
    explicit = os.environ.get("PIXEL_REFINE_TARGET_VARIANT", "").strip()
    if explicit:
        return explicit
    if os.name == "nt":
        vendor = os.environ.get("TARGET_VENDOR", "").strip().lower()
        suffix = "_nvidia" if vendor == "nvidia" else "_intel" if vendor == "intel" else ""
        return f"{backend}_x86_64_windows{suffix}"
    return f"{backend}_x86_64_linux"


def _default_native_tcm(module_name: str, backend: str, device_id: int) -> Path:
    target = _native_target_variant(backend, device_id)
    # An isolated release bundle can provide its exact target-qualified TCM
    # root.  Keep the repository tree as the default, but never search both
    # roots: mixing an LLVM15 archive with an LLVM20 bridge is an ABI error.
    explicit_root = os.environ.get("PIXEL_REFINE_AOT_TCM_ROOT", "").strip()
    if explicit_root:
        root = Path(explicit_root).expanduser().resolve()
    else:
        try:
            from taichi_vision.llvm20_runtime_paths import tcm_root as staged_tcm_root

            staged_root = staged_tcm_root(target)
        except (ImportError, OSError, ValueError):
            staged_root = None
        root = (
            Path(staged_root).resolve()
            if staged_root is not None
            else _native_repo_root() / "taichi_vision" / "taichi_algorithm" / "aot_tcm"
        )
    candidates = (
        root / target / f"{module_name}_{target}.tcm",
        root / target / f"{module_name}.tcm",
        root / f"{module_name}_{target}.tcm",
        root / f"{module_name}.tcm",
    )
    for candidate in candidates:
        if candidate.is_file() and candidate.stat().st_size > 0:
            return candidate.resolve()
    raise NativeDispatchUnavailable(
        f"native TCM for module {module_name!r} was not found for target {target!r}"
    )


class NativeAOTEngine:
    """Direct buffer-protocol AOT runner for codec graphs.

    The adapter talks to the existing C bridge with ``ctypes`` and
    ``NativeTensor`` buffers.  It never imports NumPy, ``InputArray``, or the
    legacy Python graph wrapper.  This is deliberately additive: callers opt
    in explicitly, and unavailable targets fail closed.
    """

    def __init__(self, backend: Optional[str] = None, device_id: Optional[int] = None):
        self.backend = _native_backend_name(backend)
        self.device_id = 0 if self.backend in {"cpu", "opengl", "gles"} else int(
            os.environ.get("AOT_DEVICE", "0") if device_id is None else device_id
        )
        self._lock = threading.RLock()
        self._modules: dict[str, int] = {}
        self._module_paths: dict[str, Path] = {}
        self._dll_dirs: list[Any] = []
        library_path, self._dll_dirs = _native_library_path(self.backend)
        try:
            self._lib = ctypes.CDLL(str(library_path))
        except OSError as exc:
            raise NativeDispatchUnavailable(
                f"unable to load native codec bridge {library_path}: {exc}"
            ) from exc
        self._configure_abi()
        self.runtime = self._lib.init_aot_engine(
            _NATIVE_ARCH_IDS[self.backend], self.device_id
        )
        if not self.runtime:
            detail = self.last_error() or "bridge initialization returned a null runtime"
            raise NativeDispatchUnavailable(detail)
        self._closed = False

    def _configure_abi(self) -> None:
        lib = self._lib
        lib.init_aot_engine.argtypes = [ctypes.c_int, ctypes.c_int]
        lib.init_aot_engine.restype = ctypes.c_void_p
        lib.destroy_aot_engine.argtypes = [ctypes.c_void_p]
        lib.destroy_aot_engine.restype = None
        lib.load_aot_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lib.load_aot_module.restype = ctypes.c_void_p
        lib.destroy_aot_module.argtypes = [ctypes.c_void_p]
        lib.destroy_aot_module.restype = None
        lib.allocate_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_uint64, ctypes.c_int]
        lib.allocate_gpu_buffer.restype = ctypes.c_void_p
        lib.free_gpu_buffer.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        lib.free_gpu_buffer.restype = None
        lib.write_to_gpu_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        lib.write_to_gpu_buffer.restype = None
        lib.read_from_gpu_buffer.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        ]
        lib.read_from_gpu_buffer.restype = None
        lib.run_aot_graph.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(_NativeDynamicArg),
            ctypes.c_int,
        ]
        lib.run_aot_graph.restype = None
        lib.sync_runtime.argtypes = [ctypes.c_void_p]
        lib.sync_runtime.restype = None
        try:
            lib.get_last_engine_error.argtypes = [ctypes.c_void_p]
            lib.get_last_engine_error.restype = ctypes.c_char_p
            lib.clear_last_engine_error.argtypes = [ctypes.c_void_p]
            lib.clear_last_engine_error.restype = None
        except AttributeError:
            pass

    def last_error(self) -> str:
        function = getattr(self._lib, "get_last_engine_error", None)
        if function is None or not getattr(self, "runtime", None):
            return ""
        try:
            value = function(self.runtime)
            return value.decode("utf-8", "replace") if value else ""
        except (OSError, ValueError):
            return ""

    def _clear_error(self) -> None:
        function = getattr(self._lib, "clear_last_engine_error", None)
        if function is not None:
            function(self.runtime)

    def load_module(self, module_name: str, path: Optional[os.PathLike[str] | str] = None) -> int:
        if not isinstance(module_name, str) or not module_name.strip():
            raise NativeDispatchContractError("module_name must be a non-empty string")
        with self._lock:
            self._ensure_open()
            existing = self._modules.get(module_name)
            if existing:
                return existing
            module_path = Path(path) if path is not None else _default_native_tcm(
                module_name, self.backend, self.device_id
            )
            module_path = module_path.resolve()
            if not module_path.is_file() or module_path.stat().st_size <= 0:
                raise NativeDispatchUnavailable(
                    f"native TCM path is missing or empty: {module_path}"
                )
            module_ptr = self._lib.load_aot_module(
                self.runtime, str(module_path).encode("utf-8")
            )
            if not module_ptr:
                raise NativeDispatchUnavailable(
                    f"native bridge failed to load TCM {module_path}: {self.last_error()}"
                )
            token = int(getattr(module_ptr, "value", module_ptr) or 0)
            self._modules[module_name] = token
            self._module_paths[module_name] = module_path
            return token

    def _ensure_open(self) -> None:
        if self._closed or not getattr(self, "runtime", None):
            raise NativeDispatchUnavailable("native codec engine is closed")

    @staticmethod
    def _fill_tensor_arg(
        arg: _NativeDynamicArg,
        name: bytes,
        tensor: NativeTensor,
        handle: int,
    ) -> None:
        descriptor = tensor.to_descriptor()
        if descriptor.ndim > 8:
            raise NativeDispatchContractError("native graph tensors support at most 8 dimensions")
        arg.name = name
        arg.arg_type = 0
        arg.dtype = _NATIVE_DTYPE_CODES[descriptor.dtype_code]
        arg.dim_count = descriptor.ndim
        for index, dimension in enumerate(descriptor.shape):
            arg.shape[index] = int(dimension)
        arg.elem_dim_count = 1 if descriptor.vector_dim is not None else 0
        if descriptor.vector_dim is not None:
            arg.elem_shape[0] = int(descriptor.vector_dim)
            arg.is_vector = 1
            arg.vector_dim = int(descriptor.vector_dim)
        else:
            arg.is_vector = 0
            arg.vector_dim = 1
        arg.val_u64 = int(handle)

    @staticmethod
    def _fill_scalar_arg(arg: _NativeDynamicArg, name: bytes, value: NativeScalar) -> None:
        arg.name = name
        arg.arg_type = 1
        if isinstance(value, bool) or isinstance(value, int):
            arg.dtype = _NATIVE_DTYPE_CODES["i32"]
            arg.val_u64 = int(value) & ((1 << 64) - 1)
        elif isinstance(value, float) and math.isfinite(value):
            arg.dtype = _NATIVE_DTYPE_CODES["f32"]
            arg.val_u64 = struct.unpack("<I", struct.pack("<f", value))[0]
        else:
            raise NativeDispatchContractError(
                "native graph scalar values must be finite float, integer, or boolean"
            )

    def _allocate(self, nbytes: int) -> int:
        handle = self._lib.allocate_gpu_buffer(self.runtime, int(nbytes), 1)
        token = int(getattr(handle, "value", handle) or 0)
        if not token:
            raise NativeDispatchUnavailable(
                f"native graph buffer allocation failed for {nbytes} bytes: {self.last_error()}"
            )
        return token

    def _write(self, handle: int, tensor: NativeTensor) -> None:
        view = tensor.buffer
        if view.readonly:
            holder: Any = ctypes.create_string_buffer(view.tobytes())
            pointer = ctypes.cast(holder, ctypes.c_void_p)
        else:
            holder = (ctypes.c_ubyte * view.nbytes).from_buffer(view)
            pointer = ctypes.cast(holder, ctypes.c_void_p)
        self._lib.write_to_gpu_buffer(self.runtime, handle, pointer, view.nbytes)

    def _read(self, handle: int, tensor: NativeTensor) -> None:
        view = tensor.buffer
        if view.readonly:
            raise NativeDispatchContractError("native graph outputs must be writable tensors")
        holder = (ctypes.c_ubyte * view.nbytes).from_buffer(view)
        self._lib.read_from_gpu_buffer(
            self.runtime, handle, ctypes.cast(holder, ctypes.c_void_p), view.nbytes
        )

    def run_native_graph(self, request: NativeGraphRequest) -> Any:
        if not isinstance(request, NativeGraphRequest):
            raise NativeDispatchContractError("request must be a NativeGraphRequest")
        if request.backend is not None and _native_backend_name(request.backend) != self.backend:
            raise NativeDispatchContractError(
                f"request backend {request.backend!r} does not match engine backend {self.backend!r}"
            )
        with self._lock:
            self._ensure_open()
            module_ptr = self.load_module(request.module_name)
            handles: list[int] = []
            output_handles: list[int] = []
            try:
                for tensor in request.inputs:
                    handle = self._allocate(tensor.nbytes)
                    handles.append(handle)
                    self._write(handle, tensor)
                for tensor in request.outputs:
                    handle = self._allocate(tensor.nbytes)
                    handles.append(handle)
                    output_handles.append(handle)

                names: list[bytes] = []
                total_args = len(request.inputs) + len(request.outputs) + len(request.scalars)
                args = (_NativeDynamicArg * total_args)()
                index = 0
                for name, tensor, handle in zip(request.input_names, request.inputs, handles[: len(request.inputs)]):
                    encoded = name.encode("utf-8")
                    names.append(encoded)
                    self._fill_tensor_arg(args[index], encoded, tensor, handle)
                    index += 1
                output_offset = len(request.inputs)
                for output_index, (name, tensor) in enumerate(zip(request.output_names, request.outputs)):
                    encoded = name.encode("utf-8")
                    names.append(encoded)
                    self._fill_tensor_arg(args[index], encoded, tensor, handles[output_offset + output_index])
                    index += 1
                for name, value in request.scalars.items():
                    encoded = name.encode("utf-8")
                    names.append(encoded)
                    self._fill_scalar_arg(args[index], encoded, value)
                    index += 1

                self._clear_error()
                self._lib.run_aot_graph(
                    self.runtime,
                    module_ptr,
                    request.graph_name.encode("utf-8"),
                    args,
                    total_args,
                )
                self._lib.sync_runtime(self.runtime)
                error = self.last_error()
                if error:
                    raise NativeDispatchError(
                        f"native graph {request.graph_name!r} failed: {error}"
                    )
                for handle, tensor in zip(output_handles, request.outputs):
                    self._read(handle, tensor)
            finally:
                if getattr(self, "runtime", None):
                    for handle in handles:
                        try:
                            self._lib.free_gpu_buffer(self.runtime, handle)
                        except (OSError, ValueError):
                            pass
            if len(request.outputs) == 1:
                return request.outputs[0]
            return request.outputs

    def close(self) -> None:
        with getattr(self, "_lock", threading.RLock()):
            if getattr(self, "_closed", True):
                return
            for module_ptr in tuple(self._modules.values()):
                try:
                    self._lib.destroy_aot_module(module_ptr)
                except (OSError, TypeError):
                    pass
            self._modules.clear()
            runtime = self.runtime
            self.runtime = None
            self._closed = True
            if runtime:
                try:
                    self._lib.destroy_aot_engine(runtime)
                except (OSError, TypeError):
                    pass
            for directory in self._dll_dirs:
                try:
                    directory.close()
                except (AttributeError, OSError):
                    pass
            self._dll_dirs.clear()

    def __enter__(self) -> "NativeAOTEngine":
        self._ensure_open()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass


def build_native_request(
    module_name: str,
    graph_name: str,
    inputs: Sequence[NativeTensor],
    *,
    outputs: Sequence[NativeTensor] = (),
    scalars: Optional[Mapping[str, NativeScalar]] = None,
    backend: Optional[str] = None,
    input_names: Optional[Sequence[str]] = None,
    output_names: Optional[Sequence[str]] = None,
) -> NativeGraphRequest:
    """Construct and validate a native graph request."""

    return NativeGraphRequest(
        module_name=module_name,
        graph_name=graph_name,
        inputs=tuple(inputs),
        outputs=tuple(outputs),
        scalars={} if scalars is None else scalars,
        backend=backend,
        input_names=() if input_names is None else tuple(input_names),
        output_names=() if output_names is None else tuple(output_names),
    )


def native_engine_available(engine: Any) -> bool:
    """Return whether the exact additive hook is callable.

    No legacy method names are considered.  In particular, an engine exposing
    ``run_aot_graph`` is not treated as native-capable because that path may
    still require the NumPy ABI.
    """

    if engine is None:
        return False
    try:
        return callable(getattr(engine, NATIVE_ENGINE_METHOD, None))
    except (AttributeError, RuntimeError):
        return False


def native_dispatch_report(engine: Any = None) -> dict[str, Any]:
    """Describe seam availability without importing or probing NumPy."""

    available = native_engine_available(engine)
    return {
        "abi_version": ABI_VERSION,
        "native_engine_method": NATIVE_ENGINE_METHOD,
        "native_engine_available": available,
        "legacy_numpy_fallback": False,
        "fail_closed_when_unavailable": True,
    }


def dispatch_native_graph(
    engine: NativeGraphEngine,
    request: NativeGraphRequest,
) -> Any:
    """Dispatch only through the additive native engine hook.

    This is deliberately a narrow seam.  If the current engine lacks
    ``run_native_graph(request)``, it raises immediately.  It does not call
    ``run_aot_graph``, ``InputArray``, ``OutputArray``, or a codec's existing
    NumPy ``_dispatch`` path, so current callers remain unchanged and no
    accidental fallback can create a false strict-no-NumPy claim.
    """

    if not isinstance(request, NativeGraphRequest):
        raise NativeDispatchContractError("request must be a NativeGraphRequest")
    if engine is None:
        raise NativeDispatchUnavailable(
            "native codec dispatch unavailable: no engine was supplied; "
            "legacy NumPy dispatch is intentionally not used"
        )
    try:
        method = getattr(engine, NATIVE_ENGINE_METHOD, None)
    except (AttributeError, RuntimeError) as exc:
        raise NativeDispatchUnavailable(
            "native codec dispatch unavailable: engine does not expose "
            f"{NATIVE_ENGINE_METHOD}(request); legacy NumPy dispatch is intentionally not used"
        ) from exc
    if not callable(method):
        raise NativeDispatchUnavailable(
            "native codec dispatch unavailable: engine does not expose "
            f"{NATIVE_ENGINE_METHOD}(request); legacy NumPy dispatch is intentionally not used"
        )
    # Do not catch exceptions from the future engine method.  Once present,
    # its validation/device errors must be visible to the caller.
    return method(request)


def run_self_tests() -> dict[str, Any]:
    """Run focused request validation and fail-closed dispatch tests."""

    tensor = NativeTensor.allocate((2, 2), "u8")
    request = build_native_request(
        "compression_image",
        "codec_prepare",
        (tensor,),
        outputs=(NativeTensor.allocate((2, 2), "u8"),),
        scalars={"quality": 90, "lossless": False},
        backend="vulkan",
    )
    assert request.input_descriptors[0].nbytes == 4
    assert request.scalars["quality"] == 90

    class LegacyOnlyEngine:
        def __init__(self) -> None:
            self.legacy_called = False

        def run_aot_graph(self, *_args: Any, **_kwargs: Any) -> None:
            self.legacy_called = True
            raise AssertionError("legacy graph path must never be called")

    legacy = LegacyOnlyEngine()
    assert not native_engine_available(legacy)
    try:
        dispatch_native_graph(legacy, request)
    except NativeDispatchUnavailable:
        pass
    else:
        raise AssertionError("missing native engine hook must fail closed")
    assert not legacy.legacy_called

    class NativeOnlyEngine:
        def __init__(self) -> None:
            self.received: Optional[NativeGraphRequest] = None

        def run_native_graph(self, received: NativeGraphRequest) -> str:
            self.received = received
            return "native-ok"

    native = NativeOnlyEngine()
    assert native_engine_available(native)
    assert dispatch_native_graph(native, request) == "native-ok"
    assert native.received is request
    assert native_dispatch_report(legacy)["legacy_numpy_fallback"] is False

    try:
        build_native_request("compression_image", "bad", ())
    except NativeDispatchContractError:
        pass
    else:
        raise AssertionError("empty input requests must fail closed")

    return {
        "passed": 5,
        "checks": (
            "request-metadata",
            "legacy-path-not-called",
            "missing-hook-fail-closed",
            "additive-hook-dispatch",
            "request-validation",
        ),
    }


if __name__ == "__main__":
    print(run_self_tests())
