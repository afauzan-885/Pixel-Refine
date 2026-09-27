"""Bounded native RGB splatting with one RAM-backed HR accumulator."""

from __future__ import annotations

from contextlib import contextmanager
import os
import operator
import shutil
import tempfile

import numpy as np


class RamAccumulatorBacking:
    """One job's numerator/denominator, owned together by BufferSession.

    The availability guard is conservative, not a reservation or a process
    memory limit. It must never spill silently to disk on allocation failure.
    """

    storage = "ram"
    zero_copy_reads = True
    numerator_path = "numerator"
    denominator_path = "denominator"

    def __init__(self, shape, *, minimum_headroom_bytes=0):
        import psutil

        self.shape = tuple(operator.index(value) for value in shape)
        if len(self.shape) != 3 or self.shape[2] != 3 or min(self.shape) < 1:
            raise ValueError("RAM accumulator requires positive (H,W,3) dimensions")
        height, width, _ = self.shape
        self.required_bytes = height * width * 16
        if self.required_bytes > np.iinfo(np.intp).max:
            raise OverflowError("Splat SR accumulator exceeds addressable array size")
        self.closed = False
        self.numerator = self.denominator = None
        available = int(psutil.virtual_memory().available)
        minimum_headroom_bytes = operator.index(minimum_headroom_bytes)
        if minimum_headroom_bytes < 0:
            raise ValueError("minimum_headroom_bytes must be nonnegative")
        reserve = max(256 * 1024**2, self.required_bytes // 2, minimum_headroom_bytes)
        if self.required_bytes + reserve > available:
            raise MemoryError(
                "Splat SR RAM accumulator requires "
                f"{self.required_bytes / 1024**2:.1f} MiB plus "
                f"{reserve / 1024**2:.1f} MiB safety headroom; "
                f"only {available / 1024**2:.1f} MiB RAM is available. "
                "No automatic disk spill is performed."
            )
        try:
            self.numerator = np.empty(self.shape, dtype=np.float32)
            self.numerator.fill(0.0)
            self.denominator = np.empty((height, width), dtype=np.float32)
            self.denominator.fill(0.0)
        except BaseException:
            self.close()
            raise

    @contextmanager
    def region(self, plane, y0, y1, x0, x1, *, channels, writable=False):
        if self.closed:
            raise RuntimeError("Splat SR backing store is closed")
        height, width, _ = self.shape
        if not (0 <= y0 < y1 <= height and 0 <= x0 < x1 <= width):
            raise ValueError("tile lies outside the HR image")
        if plane == self.numerator_path and channels == 3:
            array = self.numerator
        elif plane == self.denominator_path and channels == 1:
            array = self.denominator
        else:
            raise ValueError("invalid accumulator plane or channel count")
        if array is None:
            raise RuntimeError("accumulator plane has been released")
        tile = array[y0:y1, x0:x1].view()
        if not writable:
            tile.setflags(write=False)
        yield tile

    def accumulate(self, y0, x0, numerator, denominator):
        height, width = denominator.shape
        bounds = (y0, y0 + height, x0, x0 + width)
        with self.region(self.numerator_path, *bounds, channels=3, writable=True) as target:
            np.add(target, numerator, out=target)
        with self.region(self.denominator_path, *bounds, channels=1, writable=True) as target:
            np.add(target, denominator, out=target)

    def accumulate_packed(self, y0, x0, packed):
        height, width = packed.shape[:2]
        bounds = (y0, y0 + height, x0, x0 + width)
        with self.region(self.numerator_path, *bounds, channels=3, writable=True) as target:
            np.add(target, packed[..., :3], out=target)
        with self.region(self.denominator_path, *bounds, channels=1, writable=True) as target:
            np.add(target, packed[..., 3], out=target)

    def release_denominator(self):
        self.denominator = None

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.numerator = self.denominator = None


class _TileBacking:
    """Map only the rows being used, then unmap them before the next tile."""

    storage = "disk"
    zero_copy_reads = False

    def __init__(self, shape, directory=None):
        self.shape = tuple(int(value) for value in shape)
        self.closed = False
        directory = directory or os.environ.get("SPLATSR_SCRATCH_DIR") or None
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(
            prefix="pixelrefine_splat_tiles_", dir=directory
        )
        self.numerator_path = os.path.join(self.directory.name, "numerator.f32")
        self.denominator_path = os.path.join(self.directory.name, "denominator.f32")
        height, width, channels = self.shape
        self.required_bytes = height * width * (channels + 1) * 4
        try:
            free = shutil.disk_usage(self.directory.name).free
            if free < self.required_bytes + 64 * 1024 * 1024:
                raise OSError(
                    "Splat SR tiled accumulation requires "
                    f"{self.required_bytes / 1024**3:.2f} GiB scratch disk space; "
                    f"only {free / 1024**3:.2f} GiB is available"
                )
            for path, count in (
                (self.numerator_path, height * width * channels),
                (self.denominator_path, height * width),
            ):
                # Newly extended file bytes are zero. No full HR zero array or
                # permanent full-image mapping is created in the process.
                with open(path, "w+b") as stream:
                    stream.truncate(count * 4)
        except Exception:
            self.close()
            raise

    @contextmanager
    def region(self, path, y0, y1, x0, x1, *, channels, writable=False):
        if self.closed:
            raise RuntimeError("Splat SR backing store is closed")
        height, width, _ = self.shape
        if not (0 <= y0 < y1 <= height and 0 <= x0 < x1 <= width):
            raise ValueError("tile lies outside the HR image")
        shape = (y1 - y0, width, channels) if channels > 1 else (y1 - y0, width)
        mapping = np.memmap(
            path, mode="r+" if writable else "r", dtype=np.float32,
            offset=y0 * width * channels * 4, shape=shape,
        )
        try:
            yield mapping[:, x0:x1]
        finally:
            # Closing a shared file mapping retains writes in the OS file
            # cache and drops its pages from this process's working set.
            # A synchronous disk flush for every tile would serialize I/O.
            mapping._mmap.close()

    def accumulate(self, y0, x0, numerator, denominator):
        height, width = denominator.shape
        bounds = (y0, y0 + height, x0, x0 + width)
        with self.region(self.numerator_path, *bounds, channels=3, writable=True) as target:
            np.add(target, numerator, out=target)
        with self.region(self.denominator_path, *bounds, channels=1, writable=True) as target:
            np.add(target, denominator, out=target)

    def accumulate_packed(self, y0, x0, packed):
        height, width = packed.shape[:2]
        bounds = (y0, y0 + height, x0, x0 + width)
        with self.region(self.numerator_path, *bounds, channels=3, writable=True) as target:
            np.add(target, packed[..., :3], out=target)
        with self.region(self.denominator_path, *bounds, channels=1, writable=True) as target:
            np.add(target, packed[..., 3], out=target)

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.directory.cleanup()

    def release_denominator(self):
        os.remove(self.denominator_path)


class TiledRGBResult:
    """Transferred tile-only RGB result; RAM views are borrowed read-only.

    Consumers must finish using a view before closing its result owner. Disk
    slices are copied out of short-lived mappings. No whole-image conversion.
    """

    ndim = 3
    dtype = np.dtype(np.float32)

    def __init__(self, backing):
        self.backing = backing
        self.shape = backing.shape

    def __array__(self, *args, **kwargs):
        raise TypeError("Read TiledRGBResult through rectangular tiles")

    def __getitem__(self, key):
        if not isinstance(key, tuple) or len(key) not in (2, 3):
            raise TypeError("TiledRGBResult requires rectangular row/column slices")
        ys, xs = key[:2]
        if not isinstance(ys, slice) or not isinstance(xs, slice):
            raise TypeError("TiledRGBResult requires rectangular row/column slices")
        y0, y1, ystep = ys.indices(self.shape[0])
        x0, x1, xstep = xs.indices(self.shape[1])
        if ystep != 1 or xstep != 1:
            raise ValueError("TiledRGBResult supports unit-stride tile slices")
        with self.backing.region(
            self.backing.numerator_path, y0, y1, x0, x1, channels=3
        ) as tile:
            result = tile if self.backing.zero_copy_reads else np.array(tile, dtype=np.float32, copy=True)
        return result if len(key) == 2 else result[..., key[2]]

    def iter_tiles(self, block_size=1024):
        if block_size < 1:
            raise ValueError("block_size must be positive")
        height, width = self.shape[:2]
        for y0 in range(0, height, block_size):
            for x0 in range(0, width, block_size):
                y1, x1 = min(height, y0 + block_size), min(width, x0 + block_size)
                yield y0, y1, x0, x1, self[y0:y1, x0:x1]

    def add_luma_delta(self, initial, refined, *, block_size=1024, check_cancelled=None):
        height, width = self.shape[:2]
        for y0 in range(0, height, block_size):
            for x0 in range(0, width, block_size):
                if check_cancelled:
                    check_cancelled()
                y1, x1 = min(height, y0 + block_size), min(width, x0 + block_size)
                delta = refined[y0:y1, x0:x1] - initial[y0:y1, x0:x1]
                with self.backing.region(
                    self.backing.numerator_path, y0, y1, x0, x1,
                    channels=3, writable=True,
                ) as tile:
                    np.add(tile, delta[..., None], out=tile)
                    np.clip(tile, 0.0, 1.0, out=tile)

    def close(self):
        self.backing.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


class DiskBackedRGB(TiledRGBResult):
    """Compatibility result for the explicit disk comparison backing."""


def _packed_view(buffer, shape):
    """Use the start of an owned scratch buffer as a smaller packed ndarray."""
    from taichi_vision.taichi_aot.engine import TaichiGPUBuffer

    shape = tuple(int(value) for value in shape)
    size_bytes = int(np.prod(shape)) * np.dtype(buffer.dtype).itemsize
    if size_bytes > buffer.size_bytes:
        raise ValueError("packed tile view exceeds its scratch allocation")
    view = TaichiGPUBuffer(
        size_bytes, buffer.handle, shape, dtype=buffer.dtype,
        is_vector=False, engine=buffer.engine, is_owner=False,
        host_accessible=buffer.host_accessible,
    )
    view._parent_ref = buffer
    return view


class TiledHannAccumulator:
    """Splat one source halo to one HR tile with fused RGB and Hann weighting.

    Tile dimensions refer to the HR output. The existing gather kernel visits
    only +/-3 LR pixels around each output sample, so a three-pixel LR halo
    exactly preserves its full-frame candidate set, including nonzero flow.
    Only bounded tile numerator/coverage leave the device for host stitching.
    """

    def __init__(
        self, reference_rgb, *, session, scale=2, block_size=1024,
        overlap=0.25, radius=2.0, sigma=0.85, check_cancelled=None, asset_dir=None,
        backing_factory=RamAccumulatorBacking,
    ):
        from taichi_vision import taichi_aot
        from .spatial_splat_runtime import SpatialSplatAOT, _force_host_visible
        from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
            _tcm_graph_available,
        )

        self.reference = np.ascontiguousarray(reference_rgb, dtype=np.float32)
        if self.reference.ndim != 3 or self.reference.shape[2] != 3:
            raise ValueError("tiled Splat SR requires linear RGB reference")
        self.session = session
        self.engine = taichi_aot.engine
        backend = str(getattr(self.engine, "arch", "cpu")).lower()
        backend = "opengl" if backend == "gles" else backend
        asset_dir = asset_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../../ui/data/aot_assets")
        )
        self.splat = SpatialSplatAOT(tcm_path=os.path.join(
            asset_dir, f"spatial_splat_tiled_packed_{backend}.tcm"
        ))
        self.backend = self.splat.backend
        if not _tcm_graph_available(self.splat.tcm_path, "deno_splat_rgb_hann_tile"):
            raise RuntimeError(
                f"Fused RGB Hann splat graph is missing on {self.backend}: "
                f"{self.splat.tcm_path}. Rebuild the splat TCM for this backend."
            )
        self.scale = int(scale)
        if self.scale < 1:
            raise ValueError("scale must be >= 1")
        self.lr_h, self.lr_w = self.reference.shape[:2]
        self.hr_h, self.hr_w = self.lr_h * self.scale, self.lr_w * self.scale
        self.block_size = max(64, int(block_size))
        self.overlap = float(np.clip(overlap, 0.0, 0.9))
        self.radius, self.sigma = float(radius), float(sigma)
        self.check_cancelled = check_cancelled or (lambda: None)
        self.closed = self.finalized = False
        self.hann_cache = {}
        self.tiles_processed = 0
        self.readbacks = 0
        self.backing = session.own(backing_factory((self.hr_h, self.hr_w, 3)))

        height = min(self.block_size, self.hr_h)
        width = min(self.block_size, self.hr_w)
        source_h = min(self.lr_h, (self.block_size + self.scale - 1) // self.scale + 7)
        source_w = min(self.lr_w, (self.block_size + self.scale - 1) // self.scale + 7)
        self.output_shape = (height, width)
        with _force_host_visible(self.engine, self.backend == "vulkan"):
            self.accumulation_tile = session.acquire_buffer(
                (height, width, 4), tag="splat_sr.tiled.packed_accumulation"
            )
            self.confidence_scratch = session.acquire_buffer(
                (source_h, source_w), tag="splat_sr.tiled.confidence"
            )
            self.zero_crop_flow = session.own(
                self.engine.upload(np.zeros((1, 1, 2), dtype=np.float32))
            )
        self.host_packed = session.acquire_host(
            (height * width * 4,), tag="splat_sr.tiled.read_packed_accumulation"
        )
        session.own(self, releaser=lambda accumulator: accumulator.close())
        print(
            f"[splattingSR] tiled reconstruction: HR tile={self.block_size} "
            f"overlap={self.overlap:.2f} stride={self.stride} RGB+coverage=packed "
            f"HR accumulator={self.backing.storage} ({self.backing.required_bytes / 1024**2:.1f} MiB)"
        )

    @property
    def stride(self):
        return max(1, int(round(self.block_size * (1.0 - self.overlap))))

    def _tiles(self, *, overlapping=True):
        stride = self.stride if overlapping else self.block_size
        for y0 in range(0, self.hr_h, stride):
            for x0 in range(0, self.hr_w, stride):
                yield y0, min(self.hr_h, y0 + self.block_size), x0, min(self.hr_w, x0 + self.block_size)

    def add_frame(self, frame_rgb, flow, confidence):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer

        if isinstance(confidence, TaichiGPUBuffer):
            with self.session.borrowed(confidence):
                return self._add_frame(frame_rgb, flow, confidence)
        return self._add_frame(frame_rgb, flow, confidence)

    def _add_frame(self, frame_rgb, flow, confidence):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        from .spatial_splat_runtime import SessionHannAccumulator, _force_host_visible

        if self.closed or self.finalized:
            raise RuntimeError("tiled accumulator is no longer accepting frames")
        frame = np.asarray(frame_rgb, dtype=np.float32)
        if frame.shape != self.reference.shape:
            raise ValueError("support dimensions differ from reference")
        if flow is not None and (flow.shape != (self.lr_h, self.lr_w, 2) or flow.dtype != np.float32):
            raise ValueError("splat flow must be float32 (H,W,2)")
        borrowed = isinstance(confidence, TaichiGPUBuffer)
        if borrowed:
            # Reuse the existing engine/shape validation without a readback.
            SessionHannAccumulator._batched_confidence_view(
                confidence, (self.lr_h, self.lr_w), self.engine
            )
            if len(confidence.shape) != 2:
                confidence = _packed_view(confidence, (self.lr_h, self.lr_w))
        elif confidence is not None:
            confidence = np.asarray(confidence, dtype=np.float32)
            if confidence.shape != (self.lr_h, self.lr_w):
                raise ValueError("confidence must have shape (H,W)")

        tiles = 0
        # Provider confidence is borrowed for this callback only. The recipe
        # and accumulator execute sequentially on the same engine stream.
        for y0, y1, x0, x1 in self._tiles():
            self.check_cancelled()
            sy0, sx0 = max(0, y0 // self.scale - 3), max(0, x0 // self.scale - 3)
            sy1 = min(self.lr_h, (y1 - 1) // self.scale + 4)
            sx1 = min(self.lr_w, (x1 - 1) // self.scale + 4)
            sh, sw = sy1 - sy0, sx1 - sx0
            th, tw = y1 - y0, x1 - x0
            accumulation = _packed_view(self.accumulation_tile, (th, tw, 4))
            uploaded = []
            graph_dispatched = False
            device_complete = False
            try:
                with _force_host_visible(self.engine, self.backend == "vulkan"):
                    if borrowed:
                        local_conf = _packed_view(self.confidence_scratch, (sh, sw))
                        if self.lr_h > 1 and self.lr_w > 1:
                            taichi_aot.remap_with_flow_tile(
                                confidence, self.zero_crop_flow,
                                self.lr_h, self.lr_w, sy0, sx0, sh, sw,
                                dst=local_conf,
                            )
                        else:
                            mx, my = np.meshgrid(
                                np.arange(sx0, sx1, dtype=np.float32),
                                np.arange(sy0, sy1, dtype=np.float32),
                            )
                            local_conf = self.session.track_result(
                                taichi_aot.remap(confidence, mx, my, return_gpu=True)
                            )
                            uploaded.append(local_conf)
                    else:
                        local = np.ones((sh, sw), dtype=np.float32) if confidence is None else confidence[sy0:sy1, sx0:sx1]
                        local = np.clip(np.nan_to_num(local, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0)
                        local_conf = self.session.own(self.engine.upload(local))
                        uploaded.append(local_conf)
                    local_frame = self.session.own(self.engine.upload(
                        np.ascontiguousarray(frame[sy0:sy1, sx0:sx1])
                    ))
                    uploaded.append(local_frame)
                    flow_tile = (
                        np.zeros((sh, sw, 2), dtype=np.float32)
                        if flow is None
                        else np.ascontiguousarray(flow[sy0:sy1, sx0:sx1])
                    )
                    local_flow = self.session.own(self.engine.upload(flow_tile))
                    uploaded.append(local_flow)
                    window = self.hann_cache.get((th, tw))
                    if window is None:
                        window = self.session.track_result(
                            taichi_aot.generate_hanning_window_2d((th, tw), exclude_boundary=True)
                        )
                        self.hann_cache[(th, tw)] = window
                    graph_dispatched = True
                    self.splat.module.run(
                        "deno_splat_rgb_hann_tile",
                        frames=_packed_view(local_frame, (sh, sw, 3)),
                        confidence=local_conf, flow=local_flow,
                        hann_tile=window, accumulation=accumulation,
                        scale=self.scale, radius=self.radius, sigma=self.sigma,
                        source_y=sy0, source_x=sx0, output_y=y0, output_x=x0,
                    )
                    host_packed = self.host_packed[:th * tw * 4].reshape(th, tw, 4)
                    accumulation.to_numpy(out=host_packed)
                    # read_from_gpu_buffer waits for the Taichi runtime before
                    # mapping/copying, so no separate engine.sync is needed.
                    device_complete = True
                    self.readbacks += 1
                    self.backing.accumulate_packed(y0, x0, host_packed)
                tiles += 1
            finally:
                # Includes partial dispatch failures and cancellation: inputs
                # cannot be retired while a queued crop/splat still uses them.
                if graph_dispatched and not device_complete:
                    self.engine.sync()
                for buffer in reversed(uploaded):
                    self.session.release_buffer(buffer)
        self.tiles_processed += tiles
        return tiles

    def _fallback_tile(self, y0, y1, x0, x1):
        from taichi_vision import taichi_aot

        sy0, sx0 = max(0, y0 // self.scale - 2), max(0, x0 // self.scale - 2)
        sy1 = min(self.lr_h, (y1 - 1) // self.scale + 3)
        sx1 = min(self.lr_w, (x1 - 1) // self.scale + 3)
        source = np.ascontiguousarray(self.reference[sy0:sy1, sx0:sx1])
        resized = taichi_aot.resize(
            source, ((sx1 - sx0) * self.scale, (sy1 - sy0) * self.scale),
            interpolation=taichi_aot.INTER_CUBIC,
        )
        oy, ox = y0 - sy0 * self.scale, x0 - sx0 * self.scale
        return resized[oy:oy + y1 - y0, ox:ox + x1 - x0]

    def finalize(self):
        if self.closed or self.finalized:
            raise RuntimeError("tiled accumulator cannot be finalized again")
        for y0, y1, x0, x1 in self._tiles(overlapping=False):
            self.check_cancelled()
            bounds = (y0, y1, x0, x1)
            with self.backing.region(self.backing.numerator_path, *bounds, channels=3, writable=True) as numerator:
                with self.backing.region(self.backing.denominator_path, *bounds, channels=1) as denominator:
                    valid = denominator > np.float32(1e-8)
                    np.divide(numerator, denominator[..., None], out=numerator, where=valid[..., None])
                    if not np.all(valid):
                        fallback = self._fallback_tile(*bounds)
                        np.copyto(numerator, fallback, where=(~valid)[..., None])
        # Region managers and yielded views can retain the final denominator
        # slice; drop them before retiring its owning array.
        del numerator, denominator
        self.backing.release_denominator()
        result_type = DiskBackedRGB if self.backing.storage == "disk" else TiledRGBResult
        result = result_type(self.backing)
        # The writer owns the backing after the job/session has closed.
        self.session.detach(self.backing)
        self.finalized = True
        return result

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.engine.sync()


__all__ = ["TiledRGBResult", "RamAccumulatorBacking", "DiskBackedRGB", "TiledHannAccumulator"]
