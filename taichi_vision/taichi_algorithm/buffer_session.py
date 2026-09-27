"""
Buffer Session
==============
Provides per-job ownership, borrowed leases and reusable host/device scratch
for Taichi Vision algorithm chains. Buffer allocation/reuse and asynchronous
native retirement remain the responsibility of the canonical AOT engine.

Keeps data resident in VRAM across chained algorithms:
  Frame (GPU) -> Grayscale (GPU) -> Pyramid (GPU) -> Optical Flow (GPU) -> Remap (GPU)
Ownership operations do not move image data or introduce GPU synchronization.
"""

from __future__ import annotations
import numpy as np
import threading
import weakref
from contextlib import contextmanager
from typing import Any, Optional, Tuple, Dict, List

from taichi_vision.taichi_aot.engine import engine as default_engine, TaichiGPUBuffer


_ownership_lock = threading.RLock()
_ownership_records = weakref.WeakValueDictionary()


class _OwnedResource:
    """Python-only ownership metadata; the resource itself is never copied."""

    __slots__ = (
        "resource", "releaser", "owner_ref", "borrow_count", "pending_release",
        "released",
        "__weakref__",
    )

    def __init__(self, resource, releaser, owner):
        self.resource = resource
        self.releaser = releaser
        self.owner_ref = weakref.ref(owner)
        self.borrow_count = 0
        self.pending_release = False
        self.released = False


def _release_resource(resource):
    """Release an owned buffer, or just drop the reference for host arrays."""
    release = getattr(resource, "release", None)
    if release is None:
        release = getattr(resource, "destroy", None)
    if release is None:
        release = getattr(resource, "close", None)
    if release is not None:
        release()


class _ManagedAPI:
    """Local facade: capture native outputs, never patch the shared engine/API."""

    def __init__(self, session, api):
        self._session = session
        self._api = api
        self._methods = {}

    def __getattr__(self, name):
        value = getattr(self._api, name)
        if not callable(value) or isinstance(value, type):
            return value
        method = self._methods.get(name)
        if method is None:
            def method(*args, **kwargs):
                self._session._assert_open()
                return self._session.track_result(value(*args, **kwargs))
            self._methods[name] = method
        return method


class BufferSession:
    """Host/device resource lifecycle with scratch leasing and reference caching.

    A session owns its uploaded and scratch buffers until they are explicitly
    released or the session closes. Use one session for a bounded pipeline or
    burst, and call ``release_upload`` after the last use of streaming inputs.

    Attributes:
        engine: Canonical Taichi AOT engine handle.
        sync_on_exit: Whether to call engine.sync() on context exit.
    """

    __slots__ = (
        "engine",
        "_leased_buffers",
        "_scratch_cache",
        "_ring_pools",
        "_ring_indices",
        "_upload_cache",
        "_reference_entry",
        "_reference_pyramids",
        "_owned_resources",
        "_borrowed_resources",
        "_closed",
        "sync_on_exit",
        "_alloc_fn",
        "_upload_fn",
        "_sync_fn",
        "_managed_apis",
        "__weakref__",
    )

    def __init__(self, engine=None, sync_on_exit: bool = True):
        self.engine = engine if engine is not None else default_engine
        self._leased_buffers: Dict[int, Any] = {}
        self._scratch_cache: Dict[Tuple, Any] = {}
        self._ring_pools: Dict[Tuple, List[TaichiGPUBuffer]] = {}
        self._ring_indices: Dict[Tuple, int] = {}
        self._upload_cache: Dict[int, Tuple[Any, TaichiGPUBuffer]] = {}
        self._reference_entry: Optional[
            Tuple[Tuple, Any, TaichiGPUBuffer, List[TaichiGPUBuffer]]
        ] = None
        self._reference_pyramids: Dict[
            Tuple, Tuple[Any, List[TaichiGPUBuffer]]
        ] = {}
        self._owned_resources: Dict[int, _OwnedResource] = {}
        self._borrowed_resources: Dict[int, Tuple[_OwnedResource, int]] = {}
        self._closed = False
        self.sync_on_exit = sync_on_exit

        # Fast local method caching to minimize LOAD_ATTR / LOAD_GLOBAL in hot loops
        self._alloc_fn = self.engine.allocate
        self._upload_fn = self.engine.upload
        self._sync_fn = self.engine.sync
        self._managed_apis = {}

    @property
    def owned_count(self) -> int:
        with _ownership_lock:
            return len(self._owned_resources)

    @property
    def borrowed_count(self) -> int:
        with _ownership_lock:
            return sum(count for _, count in self._borrowed_resources.values())

    def managed_api(self, api):
        """Track GPU outputs from an existing API without changing its signature.

        Host results are not retained automatically. Kernel-private temporaries
        remain owned by their algorithm; only returned owning handles are leased.
        """
        with _ownership_lock:
            self._assert_open()
            if isinstance(api, _ManagedAPI):
                if api._session is not self:
                    raise ValueError("managed API belongs to another session")
                return api
            facade = self._managed_apis.get(id(api))
            if facade is None:
                facade = _ManagedAPI(self, api)
                self._managed_apis[id(api)] = facade
            return facade

    def track_result(self, result):
        if isinstance(result, TaichiGPUBuffer):
            if getattr(result, "is_owner", True):
                with _ownership_lock:
                    borrowed = self._borrowed_resources.get(id(result))
                    if borrowed is not None and borrowed[0].resource is result:
                        return result
                self.own(result)
        elif isinstance(result, (tuple, list)):
            for value in result:
                self.track_result(value)
        return result

    def release_tree(self, resource) -> None:
        """Release nested application buffers early, preserving engine retirement."""
        if isinstance(resource, (tuple, list)):
            for value in resource:
                self.release_tree(value)
            return
        with _ownership_lock:
            record = self._owned_resources.get(id(resource))
            owned = record is not None and record.resource is resource
        if owned:
            self.release_buffer(resource)
        elif isinstance(resource, TaichiGPUBuffer) and getattr(resource, "is_owner", True):
            # Direct domain calls can return a native owner outside the facade.
            # Cleanup must remain usable by component callbacks during close.
            with _ownership_lock:
                record = _ownership_records.get(id(resource))
                if record is not None and record.resource is resource:
                    if record.pending_release:
                        return  # Already retired logically; borrowers still pin it.
                    raise RuntimeError("resource belongs to another session")
                self._check_engine(resource)
            _release_resource(resource)

    def release_all_except(self, *keep) -> None:
        """End a phase, retaining only explicitly named application resources.

        Quiesce workers first. Reverse registration order closes components
        before earlier carriers where possible; all releases are attempted.
        """
        preserved = {id(value) for value in keep}
        with _ownership_lock:
            resources = tuple(self._leased_buffers.values())
        first_error = None
        for resource in reversed(resources):
            if id(resource) in preserved:
                continue
            try:
                self.release_buffer(resource)
            except Exception as error:
                if first_error is None:
                    first_error = error
        if first_error is not None:
            raise first_error

    def detach(self, resource):
        """Transfer sole ownership to the caller without copying the data."""
        with _ownership_lock:
            self._assert_open()
            record = self._owned_resources.get(id(resource))
            if record is None or record.resource is not resource:
                raise ValueError("resource is not owned by this session")
            if record.borrow_count:
                raise RuntimeError("cannot detach a resource with active borrowers")
            if self._is_cached_reference(resource):
                raise RuntimeError("release the reference cache before detaching its buffer")
            self._forget_owned_references(resource)
            del self._owned_resources[id(resource)]
            _ownership_records.pop(id(resource), None)
        return resource

    def _assert_open(self) -> None:
        if self._closed:
            raise RuntimeError("BufferSession is closed")

    def _check_engine(self, resource: Any) -> None:
        if isinstance(resource, TaichiGPUBuffer):
            resource_engine = getattr(resource, "engine", None)
            live_engine = (
                self.engine._live() if hasattr(self.engine, "_live") else self.engine
            )
            if resource_engine is not None and resource_engine is not live_engine:
                raise ValueError("GPU buffer belongs to another engine")

    @staticmethod
    def _final_release(record: _OwnedResource):
        if record.pending_release and record.borrow_count == 0 and not record.released:
            record.released = True
            key = id(record.resource)
            if _ownership_records.get(key) is record:
                _ownership_records.pop(key, None)
            return record.releaser, record.resource
        return None

    def own(self, resource: Any, *, releaser=None) -> Any:
        """Take ownership without allocating or copying the resource."""
        if releaser is not None and not callable(releaser):
            raise TypeError("releaser must be callable")
        with _ownership_lock:
            self._assert_open()
            key = id(resource)
            record = _ownership_records.get(key)
            if record is not None and record.resource is resource:
                if record.owner_ref() is self and not record.pending_release:
                    return resource
                raise RuntimeError("resource already has an owner or is pending release")
            self._check_engine(resource)
            if isinstance(resource, TaichiGPUBuffer) and not getattr(
                resource, "is_owner", True
            ):
                raise ValueError("non-owning GPU views must remain with their parent owner")
            record = _OwnedResource(
                resource,
                _release_resource if releaser is None else releaser,
                self,
            )
            _ownership_records[key] = record
            self._owned_resources[key] = record
            self._leased_buffers[key] = resource
        return resource

    def borrow(self, resource: Any, *, from_session: BufferSession | None = None) -> Any:
        """Pin the same object until release_borrow(); writes remain caller-owned."""
        owner = self if from_session is None else from_session
        with _ownership_lock:
            self._assert_open()
            owner._assert_open()
            self._check_engine(resource)
            record = owner._owned_resources.get(id(resource))
            if record is None or record.resource is not resource or record.pending_release:
                raise ValueError("resource is not owned by the given live session")
            previous = self._borrowed_resources.get(id(resource))
            if previous is not None and previous[0] is not record:
                raise RuntimeError("borrowed resource identity changed")
            self._borrowed_resources[id(resource)] = (
                record, 1 if previous is None else previous[1] + 1
            )
            record.borrow_count += 1
        return resource

    def release_borrow(self, resource: Any) -> None:
        """End one borrow; a deferred owner release completes after the last one."""
        final = None
        with _ownership_lock:
            entry = self._borrowed_resources.get(id(resource))
            if entry is None or entry[0].resource is not resource:
                raise ValueError("resource is not borrowed by this session")
            record, count = entry
            if count == 1:
                del self._borrowed_resources[id(resource)]
            else:
                self._borrowed_resources[id(resource)] = (record, count - 1)
            record.borrow_count -= 1
            final = self._final_release(record)
        if final is not None:
            final[0](final[1])

    @contextmanager
    def borrowed(self, resource: Any, *, from_session: BufferSession | None = None):
        """Scope a borrow while passing the original object to the caller."""
        value = self.borrow(resource, from_session=from_session)
        try:
            yield value
        finally:
            self.release_borrow(value)

    def _forget_owned_references(self, resource: Any) -> None:
        """Remove reusable aliases when ownership leaves this session."""
        self._leased_buffers.pop(id(resource), None)
        for key, item in list(self._scratch_cache.items()):
            if item is resource:
                del self._scratch_cache[key]
        for key, ring in list(self._ring_pools.items()):
            ring[:] = [item for item in ring if item is not resource]
            if not ring:
                del self._ring_pools[key]
                self._ring_indices.pop(key, None)
            else:
                # Do not reuse a surviving slot until the next frame boundary.
                self._ring_indices[key] = len(ring)
        for key, entry in list(self._upload_cache.items()):
            if entry[1] is resource:
                del self._upload_cache[key]

    def _is_cached_reference(self, resource: Any) -> bool:
        if self._reference_entry is not None:
            _, _, gray, pyramid = self._reference_entry
            if resource is gray or any(item is resource for item in pyramid):
                return True
        return any(
            any(item is resource for item in pyramid)
            for _, pyramid in self._reference_pyramids.values()
        )

    def transfer(self, resource: Any, to_session: BufferSession) -> Any:
        """Move sole ownership to another session without moving buffer data."""
        with _ownership_lock:
            self._assert_open()
            to_session._assert_open()
            record = self._owned_resources.get(id(resource))
            if record is None or record.resource is not resource:
                raise ValueError("resource is not owned by this session")
            if to_session is self:
                return resource
            to_session._check_engine(resource)
            if record.borrow_count:
                raise RuntimeError("cannot transfer a resource with active borrowers")
            if self._is_cached_reference(resource):
                raise RuntimeError("release the reference cache before transferring its buffer")
            self._forget_owned_references(resource)
            del self._owned_resources[id(resource)]
            record.owner_ref = weakref.ref(to_session)
            to_session._owned_resources[id(resource)] = record
            to_session._leased_buffers[id(resource)] = resource
        return resource

    def reset_ring(self) -> None:
        """Reset scratch ring indices at frame boundaries."""
        with _ownership_lock:
            self._assert_open()
            self._ring_indices.clear()

    def acquire_buffer(
        self,
        shape: Tuple[int, ...],
        dtype: Any = np.float32,
        is_vector: bool = False,
        vector_dim: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> TaichiGPUBuffer:
        """Acquire a resident GPU buffer from the session scratch pool.

        Supports tagged static slots and multi-slot ring allocation to prevent
        buffer clobbering across concurrent stages.
        """
        with _ownership_lock:
            self._assert_open()
            dtype_name = np.dtype(dtype).name
            v_dim = vector_dim if vector_dim is not None else (shape[-1] if is_vector and len(shape) >= 2 else 1)
            base_key = (shape, dtype_name, is_vector, v_dim)

            if tag is not None:
                key = (*base_key, tag)
                buf = self._scratch_cache.get(key)
                if buf is None:
                    buf = self.own(
                        self._alloc_fn(
                            shape, dtype=dtype, is_vector=is_vector,
                            vector_dim=vector_dim,
                        )
                    )
                    self._scratch_cache[key] = buf
                elif self._owned_resources[id(buf)].borrow_count:
                    raise RuntimeError("tagged scratch buffer is still borrowed")
                return buf

            idx = self._ring_indices.get(base_key, 0)
            ring = self._ring_pools.setdefault(base_key, [])
            while idx < len(ring) and self._owned_resources[id(ring[idx])].borrow_count:
                idx += 1
            if idx < len(ring):
                buf = ring[idx]
            else:
                buf = self.own(
                    self._alloc_fn(
                        shape, dtype=dtype, is_vector=is_vector,
                        vector_dim=vector_dim,
                    )
                )
                ring.append(buf)
            self._ring_indices[base_key] = idx + 1
            return buf

    def acquire_host(self, shape, dtype=np.float32, *, tag):
        """Reuse one explicitly named host scratch slot within this job."""
        shape = tuple(int(value) for value in shape)
        key = ("host", shape, np.dtype(dtype).name, tag)
        with _ownership_lock:
            self._assert_open()
            buffer = self._scratch_cache.get(key)
            if buffer is None:
                buffer = self.own(np.empty(shape, dtype=dtype))
                self._scratch_cache[key] = buffer
            elif self._owned_resources[id(buffer)].borrow_count:
                raise RuntimeError("tagged host scratch buffer is still borrowed")
            return buffer

    def upload_if_needed(
        self,
        data: Any,
        is_vector: bool = False,
        vector_dim: Optional[int] = None,
        refresh: bool = False,
    ) -> Tuple[TaichiGPUBuffer, bool]:
        """Ensure data is resident on GPU with identity caching.

        If the same NumPy array object is passed multiple times within this session,
        the existing GPU buffer is returned instantly without PCIe re-upload.
        Pass ``refresh=True`` after mutating that array in place.

        Returns:
            (gpu_buffer, is_owned_by_session)
        """
        self._assert_open()
        if isinstance(data, TaichiGPUBuffer):
            return data, False

        # Host-array identity caching for burst processing
        data_id = id(data)
        cached = self._upload_cache.get(data_id)
        if cached is not None:
            source_ref, cached_buffer = cached
            if source_ref() is data:
                if not refresh:
                    return cached_buffer, False
                self.release_buffer(cached_buffer)
            else:
                # Python may recycle object ids after a host array is collected.
                # Never return a buffer cached for a different object. Keep the old
                # lease alive until explicit release/session close in case a caller
                # is still using the returned GPU buffer.
                self._upload_cache.pop(data_id, None)

        buf = self._upload_fn(data, is_vector=is_vector, vector_dim=vector_dim)
        self.own(buf)
        try:
            source_ref = weakref.ref(data)
        except TypeError:
            # Some array-like objects cannot be weak-referenced. Upload them
            # normally but do not cache by id, which could alias a later object.
            return buf, True
        self._upload_cache[data_id] = (source_ref, buf)
        return buf, True

    def release_upload(self, data: Any) -> None:
        """Release this session's cached upload after the last GPU use is queued.

        The engine retires the underlying handle until in-flight work is safe;
        callers must not use the returned buffer again after this call.
        """
        entry = self._upload_cache.get(id(data))
        if entry is None or entry[0]() is not data:
            return
        self.release_buffer(entry[1])

    def _release_reference_caches(self) -> None:
        """Retire cached reference gray/pyramid buffers before replacing them."""
        buffers = []
        if self._reference_entry is not None:
            _, _, gray, pyramid = self._reference_entry
            buffers.append(gray)
            buffers.extend(pyramid[1:])
        for _, pyramid in self._reference_pyramids.values():
            buffers.extend(pyramid[1:])

        self._reference_entry = None
        self._reference_pyramids.clear()
        seen = set()
        if buffers:
            try:
                self._sync_fn()
            except Exception:
                pass
        for buf in buffers:
            if id(buf) in seen:
                continue
            seen.add(id(buf))
            self.release_buffer(buf)

    def get_or_create_reference(
        self,
        reference: Any,
        num_levels: int = 3,
        min_size: int = 32,
        refresh: bool = False,
    ) -> Tuple[TaichiGPUBuffer, List[TaichiGPUBuffer]]:
        """Get or create cached GPU grayscale buffer and pyramid for the burst reference frame.

        In a multi-frame sequence, the reference frame is processed once, and reused
        without rebuilding it for each subsequent comparison frame.
        Pass ``refresh=True`` after mutating the reference array in place.
        """
        ref_shape = tuple(getattr(reference, "shape", ()))
        ref_dtype = getattr(reference, "dtype", None)
        token = (id(reference), ref_shape, ref_dtype, num_levels, min_size)

        if self._reference_entry is not None:
            cached_token, cached_source_ref, cached_gray, cached_pyramid = (
                self._reference_entry
            )
            if (
                not refresh
                and cached_token == token
                and cached_source_ref() is reference
            ):
                return cached_gray, cached_pyramid

        self._release_reference_caches()

        from taichi_vision.taichi_algorithm.common import cvtColor, COLOR_BGR2GRAY
        from taichi_vision.taichi_algorithm.pyramid.pyramid import build_image_pyramid_gpu

        ref_gray_gpu = self.acquire_buffer(
            ref_shape[:2], dtype=np.float32, tag="resident_reference_gray"
        )
        ref_gray_gpu = cvtColor(
            reference,
            COLOR_BGR2GRAY,
            dst=ref_gray_gpu,
            return_gpu=True,
            session=self,
        )
        ref_pyr = build_image_pyramid_gpu(
            ref_gray_gpu,
            n_levels=num_levels,
            min_size=min_size,
            session=self,
            buffer_tag_prefix="buffer_session_reference_pyramid",
        )
        self.release_upload(reference)
        try:
            reference_ref = weakref.ref(reference)
        except TypeError:
            reference_ref = lambda reference=reference: reference
        self._reference_entry = (token, reference_ref, ref_gray_gpu, ref_pyr)
        return ref_gray_gpu, ref_pyr

    def get_or_build_reference_pyramid(
        self,
        ref_image_gpu: TaichiGPUBuffer,
        n_levels: int = 3,
        min_size: int = 32,
    ) -> List[TaichiGPUBuffer]:
        """Get or build and cache a reference image pyramid in VRAM across frames in a burst."""
        key = (id(ref_image_gpu), n_levels, min_size)
        cached_entry = self._reference_pyramids.get(key)
        if cached_entry is not None:
            cached_source_ref, cached_pyramid = cached_entry
            if cached_source_ref() is ref_image_gpu:
                return cached_pyramid
            self._reference_pyramids.pop(key, None)
            try:
                self._sync_fn()
            except Exception:
                pass
            for stale_buffer in cached_pyramid[1:]:
                self.release_buffer(stale_buffer)

        if self._reference_pyramids:
            old_buffers = []
            for _, old_pyramid in self._reference_pyramids.values():
                old_buffers.extend(old_pyramid[1:])
            self._reference_pyramids.clear()
            if old_buffers:
                try:
                    self._sync_fn()
                except Exception:
                    pass
                for old_buffer in {id(item): item for item in old_buffers}.values():
                    self.release_buffer(old_buffer)

        from taichi_vision.taichi_algorithm.pyramid.pyramid import build_image_pyramid_gpu
        pyr = build_image_pyramid_gpu(
            ref_image_gpu,
            n_levels=n_levels,
            min_size=min_size,
            session=self,
            buffer_tag_prefix="buffer_session_external_pyramid",
        )
        try:
            source_ref = weakref.ref(ref_image_gpu)
        except TypeError:
            source_ref = lambda ref_image_gpu=ref_image_gpu: ref_image_gpu
        self._reference_pyramids[key] = (source_ref, pyr)
        return pyr

    def calculate_flow(
        self,
        reference,
        target,
        algorithm: str = "farneback",
        num_levels: int = 3,
        num_iters: int = 3,
        win_size: int = 15,
        pyr_scale: float = 0.5,
        poly_n: int = 5,
        poly_sigma: float = 1.2,
        return_gpu: bool = True,
        dst: Optional[Any] = None,
    ):
        """Compute optical flow field resident on GPU without host round-trip."""
        from taichi_vision.taichi_algorithm.common import cvtColor, COLOR_BGR2GRAY
        from taichi_vision.taichi_algorithm.aot_api import farneback_flow

        ref_gray_gpu, ref_pyr = self.get_or_create_reference(reference, num_levels=num_levels)
        tgt_gray_gpu = cvtColor(target, COLOR_BGR2GRAY, return_gpu=True, session=self)

        algo_norm = str(algorithm).strip().lower()
        if algo_norm in ("lucas_kanade", "lk", "bouguet"):
            from taichi_vision.taichi_algorithm import calcOpticalFlowPyrLK
            flow = calcOpticalFlowPyrLK(
                ref_gray_gpu,
                tgt_gray_gpu,
                maxLevel=max(0, int(num_levels) - 1),
                winSize=(int(win_size), int(win_size)),
                reference_pyramid=ref_pyr,
                return_gpu=return_gpu,
                dst=dst,
            )
        elif algo_norm in ("block_matching", "bm", "block_flow"):
            from taichi_vision.taichi_algorithm.aot_wrapper import calcOpticalFlowBlockMatching
            flow = calcOpticalFlowBlockMatching(
                ref_gray_gpu,
                tgt_gray_gpu,
                maxLevel=max(0, int(num_levels) - 1),
                winSize=(int(win_size), int(win_size)),
                reference_pyramid=ref_pyr,
                return_gpu=return_gpu,
                dst=dst,
            )
        else:
            flow = farneback_flow(
                ref_gray_gpu,
                tgt_gray_gpu,
                pyr_scale=pyr_scale,
                num_levels=num_levels,
                win_size=win_size,
                num_iters=num_iters,
                poly_n=poly_n,
                poly_sigma=poly_sigma,
                reference_pyramid=ref_pyr,
                return_gpu=return_gpu,
                dst=dst,
                session=self,
            )
        return flow

    def align_and_warp(
        self,
        reference,
        target,
        algorithm: str = "farneback",
        num_levels: int = 3,
        num_iters: int = 3,
        win_size: int = 15,
        pyr_scale: float = 0.5,
        poly_n: int = 5,
        poly_sigma: float = 1.2,
        return_gpu: bool = False,
        dst: Optional[Any] = None,
    ):
        """Supercharged resident pipeline: Reference-Pyramid Cache -> Flow -> Warping.

        Executes the entire alignment and warping chain resident in GPU memory.
        """
        self.reset_ring()
        from taichi_vision.taichi_algorithm.aot_api import remap_with_flow

        h, w = reference.shape[:2]

        # 1. Flow resident in GPU
        try:
            flow_gpu = self.calculate_flow(
                reference,
                target,
                algorithm=algorithm,
                num_levels=num_levels,
                num_iters=num_iters,
                win_size=win_size,
                pyr_scale=pyr_scale,
                poly_n=poly_n,
                poly_sigma=poly_sigma,
                return_gpu=True,
            )

            # 2. Warping resident in GPU
            warped = remap_with_flow(
                target,
                flow_gpu,
                h,
                w,
                return_gpu=return_gpu,
                dst=dst,
                session=self,
            )
            return warped
        finally:
            self.release_upload(target)

    def track(self, buffer: TaichiGPUBuffer) -> TaichiGPUBuffer:
        """Compatibility alias for taking ownership of a GPU buffer."""
        if isinstance(buffer, TaichiGPUBuffer):
            self.own(buffer)
        return buffer

    def release_buffer(self, buffer: Any) -> None:
        """End ownership; active borrowers defer physical release."""
        final = None
        with _ownership_lock:
            if self._is_cached_reference(buffer):
                self._release_reference_caches()
            record = self._owned_resources.get(id(buffer))
            if record is None or record.resource is not buffer:
                if id(buffer) in self._borrowed_resources:
                    raise RuntimeError("release_borrow() must end a borrowed buffer")
            else:
                self._forget_owned_references(buffer)
                del self._owned_resources[id(buffer)]
                record.pending_release = True
                final = self._final_release(record)
        if final is not None:
            final[0](final[1])

    def sync(self) -> None:
        """Synchronize native GPU execution."""
        self._sync_fn()

    def __enter__(self) -> BufferSession:
        self._assert_open()
        return self

    def close(self) -> None:
        """Explicitly release all session resources."""
        self.__exit__(None, None, None)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        with _ownership_lock:
            if self._closed:
                return
            self._closed = True
        if self.sync_on_exit:
            try:
                self._sync_fn()
            except Exception:
                pass

        first_error = None
        for buf in tuple(self._leased_buffers.values()):
            try:
                self.release_buffer(buf)
            except Exception as error:
                if first_error is None:
                    first_error = error
        for record, count in tuple(self._borrowed_resources.values()):
            for _ in range(count):
                try:
                    self.release_borrow(record.resource)
                except Exception as error:
                    if first_error is None:
                        first_error = error

        self._leased_buffers.clear()
        self._owned_resources.clear()
        self._borrowed_resources.clear()
        self._scratch_cache.clear()
        self._ring_pools.clear()
        self._ring_indices.clear()
        self._upload_cache.clear()
        self._reference_entry = None
        self._reference_pyramids.clear()
        self._managed_apis.clear()
        if first_error is not None and exc_type is None:
            raise first_error


__all__ = ["BufferSession"]
