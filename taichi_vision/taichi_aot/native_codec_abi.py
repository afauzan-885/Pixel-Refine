"""NumPy-free tensor descriptors for a future native Taichi AOT codec ABI.

This module deliberately contains only Python standard-library imports.  It
does not upload data, load a TCM, or know about the current NumPy-based AOT
engine.  ``NativeTensor`` owns (or keeps alive) a contiguous byte view and its
descriptor records the shape/dtype/vector metadata that an additive engine
API can consume later.

The current runtime engine does not expose the native buffer API described by
this module.  Consequently this file is an ABI preparation layer, not proof
of a strict no-NumPy runtime dependency.
"""

from __future__ import annotations

import array
import ctypes
import math
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Iterable, Literal, Optional, Sequence, Tuple


ABI_VERSION = 1

__all__ = [
    "ABI_VERSION",
    "NativeCodecABIError",
    "NativeDTypeCode",
    "NativeOwnership",
    "NativeTensor",
    "NativeTensorDescriptor",
    "NativeTensorReleasedError",
    "SUPPORTED_DTYPE_CODES",
    "dtype_itemsize",
    "normalize_dtype_code",
    "required_nbytes",
    "run_self_tests",
]

NativeDTypeCode = Literal["f32", "i32", "u8", "u16", "i16", "f16"]

SUPPORTED_DTYPE_CODES: Tuple[str, ...] = ("f32", "i32", "u8", "u16", "i16", "f16")

# The ABI uses native-endian compact scalar buffers.  The type-code field is
# intentionally independent of Python's memoryview format: an f16 buffer, for
# example, is commonly backed by bytearray because ``array.array`` has no
# portable half-float type code.
_DTYPE_ITEMSIZE = MappingProxyType(
    {
        "f32": 4,
        "i32": 4,
        "u8": 1,
        "u16": 2,
        "i16": 2,
        "f16": 2,
    }
)


class NativeCodecABIError(ValueError):
    """Raised when a native tensor cannot satisfy the ABI contract."""


class NativeTensorReleasedError(NativeCodecABIError):
    """Raised when a released tensor is used."""


class NativeOwnership(str, Enum):
    """Lifetime policy for the backing buffer.

    ``BORROWED`` means the caller owns the source object and the tensor keeps
    a strong reference to it.  ``OWNED`` means the tensor allocated the
    backing bytearray and may release its reference through ``release()``.
    There is deliberately no implicit deallocator for foreign buffers.
    """

    BORROWED = "borrowed"
    OWNED = "owned"


def normalize_dtype_code(dtype_code: str) -> NativeDTypeCode:
    """Return a canonical ABI dtype code or raise a descriptive error."""

    if not isinstance(dtype_code, str):
        raise NativeCodecABIError("dtype_code must be a string")
    code = dtype_code.strip().lower()
    if code not in _DTYPE_ITEMSIZE:
        supported = ", ".join(SUPPORTED_DTYPE_CODES)
        raise NativeCodecABIError(
            f"unsupported native dtype_code {dtype_code!r}; expected one of {supported}"
        )
    return code  # type: ignore[return-value]


def dtype_itemsize(dtype_code: str) -> int:
    """Return the ABI byte width for a supported dtype code."""

    return int(_DTYPE_ITEMSIZE[normalize_dtype_code(dtype_code)])


def _normalize_shape(shape: Iterable[int]) -> Tuple[int, ...]:
    if isinstance(shape, (str, bytes, bytearray)):
        raise NativeCodecABIError("shape must be an iterable of positive integers")
    try:
        normalized = tuple(shape)
    except TypeError as exc:
        raise NativeCodecABIError("shape must be an iterable of positive integers") from exc
    if not normalized:
        raise NativeCodecABIError("shape must contain at least one dimension")
    for dimension in normalized:
        if isinstance(dimension, bool) or not isinstance(dimension, int):
            raise NativeCodecABIError("shape dimensions must be integers")
        if dimension <= 0:
            raise NativeCodecABIError("shape dimensions must be positive")
    return normalized


def _normalize_vector_dim(vector_dim: Optional[int]) -> Optional[int]:
    if vector_dim is None:
        return None
    if isinstance(vector_dim, bool) or not isinstance(vector_dim, int):
        raise NativeCodecABIError("vector_dim must be an integer or None")
    # Taichi graph ndarray vector fields are represented by a spatial shape
    # plus a small vector width.  Keep this bounded to the portable vec2/3/4
    # ABI rather than silently treating an arbitrary trailing dimension as a
    # vector field.
    if vector_dim not in (2, 3, 4):
        raise NativeCodecABIError("vector_dim must be 2, 3, 4, or None")
    return vector_dim


def _element_count(shape: Tuple[int, ...], vector_dim: Optional[int]) -> int:
    count = math.prod(shape)
    if vector_dim is not None:
        count *= vector_dim
    if count <= 0:
        raise NativeCodecABIError("tensor element count must be positive")
    return count


def required_nbytes(
    shape: Iterable[int], dtype_code: str, vector_dim: Optional[int] = None
) -> int:
    """Return the exact contiguous byte size required by the descriptor."""

    normalized_shape = _normalize_shape(shape)
    normalized_dtype = normalize_dtype_code(dtype_code)
    normalized_vector = _normalize_vector_dim(vector_dim)
    return _element_count(normalized_shape, normalized_vector) * dtype_itemsize(normalized_dtype)


def _as_byte_view(data: Any, *, copy: bool) -> tuple[memoryview, Any]:
    """Obtain a one-dimensional byte view and a strong owner reference."""

    try:
        source = data if isinstance(data, memoryview) else memoryview(data)
    except (TypeError, ValueError) as exc:
        raise NativeCodecABIError(
            "data must expose the Python buffer protocol"
        ) from exc

    is_c_contiguous = bool(getattr(source, "c_contiguous", False))
    if not is_c_contiguous:
        if not copy:
            raise NativeCodecABIError(
                "native tensors require a C-contiguous buffer; pass copy=True to compact it"
            )
        compact_owner = bytearray(source.tobytes())
        return memoryview(compact_owner), compact_owner

    try:
        byte_view = source.cast("B")
    except (TypeError, ValueError) as exc:
        if not copy:
            raise NativeCodecABIError(
                "buffer cannot be exposed as a contiguous byte view; pass copy=True"
            ) from exc
        compact_owner = bytearray(source.tobytes())
        return memoryview(compact_owner), compact_owner

    if copy:
        compact_owner = bytearray(byte_view.tobytes())
        return memoryview(compact_owner), compact_owner
    return byte_view, data


def _address_of_writable_view(view: memoryview) -> Optional[int]:
    """Return a stable address when the buffer is writable, else ``None``."""

    if view.readonly:
        return None
    try:
        return int(ctypes.addressof(ctypes.c_ubyte.from_buffer(view)))
    except (BufferError, TypeError, ValueError):
        # A future engine may use the buffer protocol rather than a raw
        # pointer.  The descriptor therefore treats an address as optional.
        return None


@dataclass(frozen=True, slots=True)
class NativeTensorDescriptor:
    """Immutable metadata passed alongside a :class:`NativeTensor`.

    ``shape`` is the graph-visible spatial shape.  When ``vector_dim`` is set,
    the physical element count is ``prod(shape) * vector_dim`` while ``ndim``
    remains ``len(shape)``.  This matches the existing Taichi graph convention
    for vector-valued ndarrays without changing graph signatures.
    """

    shape: Tuple[int, ...]
    dtype_code: NativeDTypeCode
    ndim: int
    itemsize: int
    vector_dim: Optional[int]
    is_vector: bool
    element_count: int
    nbytes: int
    contiguous: bool
    readonly: bool
    ownership: NativeOwnership
    data_address: Optional[int] = None
    abi_version: int = ABI_VERSION

    def __post_init__(self) -> None:
        normalized_shape = _normalize_shape(self.shape)
        normalized_dtype = normalize_dtype_code(self.dtype_code)
        normalized_vector = _normalize_vector_dim(self.vector_dim)
        expected_count = _element_count(normalized_shape, normalized_vector)
        expected_itemsize = dtype_itemsize(normalized_dtype)
        if self.ndim != len(normalized_shape):
            raise NativeCodecABIError("descriptor ndim does not match shape")
        if self.itemsize != expected_itemsize:
            raise NativeCodecABIError("descriptor itemsize does not match dtype_code")
        if self.is_vector != (normalized_vector is not None):
            raise NativeCodecABIError("descriptor is_vector does not match vector_dim")
        if self.element_count != expected_count:
            raise NativeCodecABIError("descriptor element_count does not match shape")
        if self.nbytes != expected_count * expected_itemsize:
            raise NativeCodecABIError("descriptor nbytes does not match shape and dtype")
        if not self.contiguous:
            raise NativeCodecABIError("native ABI descriptors must be C-contiguous")
        if not isinstance(self.ownership, NativeOwnership):
            raise NativeCodecABIError("descriptor ownership must be NativeOwnership")
        if self.data_address is not None and (
            isinstance(self.data_address, bool)
            or not isinstance(self.data_address, int)
            or self.data_address < 0
        ):
            raise NativeCodecABIError("descriptor data_address must be a non-negative integer")
        if self.abi_version != ABI_VERSION:
            raise NativeCodecABIError(
                f"unsupported native ABI version {self.abi_version}; expected {ABI_VERSION}"
            )
        object.__setattr__(self, "shape", normalized_shape)
        object.__setattr__(self, "dtype_code", normalized_dtype)
        object.__setattr__(self, "vector_dim", normalized_vector)

    @property
    def c_contiguous(self) -> bool:
        """Compatibility spelling for callers that use memoryview terminology."""

        return self.contiguous

    @property
    def graph_shape(self) -> Tuple[int, ...]:
        return self.shape

    @property
    def owns_memory(self) -> bool:
        return self.ownership is NativeOwnership.OWNED

    def as_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly metadata snapshot."""

        return {
            "abi_version": self.abi_version,
            "shape": self.shape,
            "dtype_code": self.dtype_code,
            "ndim": self.ndim,
            "itemsize": self.itemsize,
            "vector_dim": self.vector_dim,
            "is_vector": self.is_vector,
            "element_count": self.element_count,
            "nbytes": self.nbytes,
            "contiguous": self.contiguous,
            "readonly": self.readonly,
            "ownership": self.ownership.value,
            "data_address": self.data_address,
        }


class NativeTensor:
    """A lifetime-safe contiguous byte buffer plus native graph metadata.

    The object never converts through NumPy.  ``from_buffer`` can borrow any
    C-contiguous Python buffer (including ``array.array`` and ctypes arrays),
    while ``allocate`` creates an owned ``bytearray`` suitable for an output.
    ``release`` only drops the tensor's references; it never frees memory owned
    by a caller.
    """

    __slots__ = (
        "_view",
        "_owner",
        "_ownership",
        "_shape",
        "_dtype_code",
        "_vector_dim",
        "_element_count",
        "_itemsize",
        "_released",
    )

    def __init__(
        self,
        view: memoryview,
        owner: Any,
        ownership: NativeOwnership,
        shape: Tuple[int, ...],
        dtype_code: NativeDTypeCode,
        vector_dim: Optional[int],
    ) -> None:
        self._view = view
        self._owner = owner
        self._ownership = ownership
        self._shape = shape
        self._dtype_code = dtype_code
        self._vector_dim = vector_dim
        self._element_count = _element_count(shape, vector_dim)
        self._itemsize = dtype_itemsize(dtype_code)
        self._released = False

    @classmethod
    def from_buffer(
        cls,
        data: Any,
        shape: Iterable[int],
        dtype_code: str,
        *,
        vector_dim: Optional[int] = None,
        copy: bool = False,
        ownership: Optional[NativeOwnership] = None,
    ) -> "NativeTensor":
        """Wrap a buffer after validating size, layout, and vector metadata."""

        normalized_shape = _normalize_shape(shape)
        normalized_dtype = normalize_dtype_code(dtype_code)
        normalized_vector = _normalize_vector_dim(vector_dim)
        expected_nbytes = _element_count(normalized_shape, normalized_vector) * dtype_itemsize(
            normalized_dtype
        )
        if copy and ownership not in (None, NativeOwnership.OWNED):
            raise NativeCodecABIError("copy=True requires owned tensor storage")
        byte_view, owner = _as_byte_view(data, copy=copy)
        if byte_view.nbytes != expected_nbytes:
            raise NativeCodecABIError(
                f"buffer has {byte_view.nbytes} bytes; expected {expected_nbytes} for "
                f"shape={normalized_shape}, dtype_code={normalized_dtype}, "
                f"vector_dim={normalized_vector}"
            )
        resolved_ownership = ownership or (NativeOwnership.OWNED if copy else NativeOwnership.BORROWED)
        if not isinstance(resolved_ownership, NativeOwnership):
            raise NativeCodecABIError("ownership must be NativeOwnership or None")
        return cls(
            byte_view,
            owner,
            resolved_ownership,
            normalized_shape,
            normalized_dtype,
            normalized_vector,
        )

    @classmethod
    def allocate(
        cls,
        shape: Iterable[int],
        dtype_code: str,
        *,
        vector_dim: Optional[int] = None,
        fill_byte: int = 0,
    ) -> "NativeTensor":
        """Allocate an owned, writable, zero-filled (by default) tensor."""

        if isinstance(fill_byte, bool) or not isinstance(fill_byte, int) or not 0 <= fill_byte <= 255:
            raise NativeCodecABIError("fill_byte must be an integer in the range 0..255")
        nbytes = required_nbytes(shape, dtype_code, vector_dim)
        storage = bytearray([fill_byte]) * nbytes
        return cls.from_buffer(
            storage,
            shape,
            dtype_code,
            vector_dim=vector_dim,
            ownership=NativeOwnership.OWNED,
        )

    @classmethod
    def from_bytes(
        cls,
        data: bytes | bytearray,
        shape: Iterable[int],
        dtype_code: str,
        *,
        vector_dim: Optional[int] = None,
        copy: bool = False,
    ) -> "NativeTensor":
        """Explicit bytes/bytearray convenience constructor."""

        return cls.from_buffer(
            data,
            shape,
            dtype_code,
            vector_dim=vector_dim,
            copy=copy,
        )

    def _require_live(self) -> memoryview:
        if self._released or self._view is None:
            raise NativeTensorReleasedError("native tensor has been released")
        return self._view

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._shape

    @property
    def ndim(self) -> int:
        return len(self._shape)

    @property
    def dtype_code(self) -> NativeDTypeCode:
        return self._dtype_code

    @property
    def itemsize(self) -> int:
        return self._itemsize

    @property
    def vector_dim(self) -> Optional[int]:
        return self._vector_dim

    @property
    def is_vector(self) -> bool:
        return self._vector_dim is not None

    @property
    def element_count(self) -> int:
        return self._element_count

    @property
    def nbytes(self) -> int:
        return self._element_count * self._itemsize

    @property
    def ownership(self) -> NativeOwnership:
        return self._ownership

    @property
    def owns_memory(self) -> bool:
        return self._ownership is NativeOwnership.OWNED

    @property
    def released(self) -> bool:
        return self._released

    @property
    def readonly(self) -> bool:
        return bool(self._require_live().readonly)

    @property
    def contiguous(self) -> bool:
        view = self._require_live()
        return bool(getattr(view, "c_contiguous", False))

    @property
    def c_contiguous(self) -> bool:
        return self.contiguous

    @property
    def buffer(self) -> memoryview:
        """Return the live byte view; the view keeps the owner alive."""

        return self._require_live()

    @property
    def memoryview(self) -> memoryview:
        return self.buffer

    @property
    def data_address(self) -> Optional[int]:
        return _address_of_writable_view(self._require_live())

    @property
    def descriptor(self) -> NativeTensorDescriptor:
        return self.to_descriptor()

    def to_descriptor(self) -> NativeTensorDescriptor:
        view = self._require_live()
        return NativeTensorDescriptor(
            shape=self._shape,
            dtype_code=self._dtype_code,
            ndim=self.ndim,
            itemsize=self._itemsize,
            vector_dim=self._vector_dim,
            is_vector=self.is_vector,
            element_count=self._element_count,
            nbytes=self.nbytes,
            contiguous=bool(getattr(view, "c_contiguous", False)),
            readonly=bool(view.readonly),
            ownership=self._ownership,
            data_address=_address_of_writable_view(view),
        )

    def to_bytes(self) -> bytes:
        return self._require_live().tobytes()

    def clone(self) -> "NativeTensor":
        """Make an owned copy while preserving the graph-visible metadata."""

        return NativeTensor.from_buffer(
            self._require_live(),
            self._shape,
            self._dtype_code,
            vector_dim=self._vector_dim,
            copy=True,
        )

    def release(self) -> None:
        """Release this wrapper without touching borrowed foreign storage."""

        if not self._released:
            self._released = True
            view = self._view
            self._view = None  # type: ignore[assignment]
            self._owner = None
            if view is not None:
                view.release()

    close = release

    def __enter__(self) -> "NativeTensor":
        self._require_live()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.release()

    def __repr__(self) -> str:
        state = "released" if self._released else "live"
        return (
            f"NativeTensor(shape={self._shape!r}, dtype_code={self._dtype_code!r}, "
            f"vector_dim={self._vector_dim!r}, ownership={self._ownership.value!r}, {state})"
        )


def run_self_tests() -> dict[str, Any]:
    """Run focused ABI/lifetime tests without importing NumPy or the engine."""

    checks: list[str] = []

    owned = NativeTensor.allocate((2, 3), "u16")
    assert owned.nbytes == 12
    assert owned.owns_memory and not owned.readonly and owned.contiguous
    assert owned.descriptor.as_dict()["dtype_code"] == "u16"
    checks.append("owned-allocation")

    vector = NativeTensor.allocate((2, 2), "f32", vector_dim=3)
    assert vector.element_count == 12 and vector.nbytes == 48
    assert vector.descriptor.ndim == 2 and vector.descriptor.vector_dim == 3
    checks.append("vector-metadata")

    float_array = array.array("f", [0.0, 1.0, 2.0, 3.0])
    borrowed_array = NativeTensor.from_buffer(float_array, (2, 2), "f32")
    assert borrowed_array.ownership is NativeOwnership.BORROWED
    assert borrowed_array.data_address is not None
    checks.append("array-buffer")

    ctypes_storage = (ctypes.c_int16 * 4)(1, 2, 3, 4)
    borrowed_ctypes = NativeTensor.from_buffer(ctypes_storage, (4,), "i16")
    assert borrowed_ctypes.to_bytes() == bytes(ctypes_storage)
    checks.append("ctypes-buffer")

    readonly = NativeTensor.from_bytes(bytes(4), (4,), "u8")
    assert readonly.readonly and readonly.data_address is None
    checks.append("readonly-buffer")

    stepped = memoryview(bytearray(range(8)))[::2]
    try:
        NativeTensor.from_buffer(stepped, (4,), "u8")
    except NativeCodecABIError:
        pass
    else:
        raise AssertionError("non-contiguous input must fail closed")
    compacted = NativeTensor.from_buffer(stepped, (4,), "u8", copy=True)
    assert compacted.to_bytes() == bytes((0, 2, 4, 6)) and compacted.owns_memory
    checks.append("contiguity-gate")

    try:
        NativeTensor.from_buffer(bytearray(3), (4,), "u8")
    except NativeCodecABIError:
        pass
    else:
        raise AssertionError("size mismatch must fail closed")
    checks.append("size-gate")

    owned.release()
    try:
        _ = owned.buffer
    except NativeTensorReleasedError:
        pass
    else:
        raise AssertionError("released tensor must reject access")
    checks.append("release-gate")

    return {"passed": len(checks), "checks": tuple(checks)}


if __name__ == "__main__":
    print(run_self_tests())
