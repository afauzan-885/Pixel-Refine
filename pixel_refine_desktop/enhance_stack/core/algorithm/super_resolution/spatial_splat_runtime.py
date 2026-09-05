"""Production wrapper for the backend-specific ``robust_splat`` TCM graph."""

from __future__ import annotations

import os

import numpy as np


class SpatialSplatAOT:
    """Execute sub-pixel splatting on the already selected AOT backend."""

    def __init__(self, engine=None, asset_dir: str | None = None):
        from taichi_vision.taichi_aot import get_engine

        self.engine = engine or get_engine()
        backend = str(getattr(self.engine, "arch", "cpu")).lower()
        if backend == "gles":
            backend = "opengl"
        if backend not in {"cpu", "cuda", "vulkan", "opengl"}:
            raise RuntimeError(f"unsupported spatial splat backend: {backend}")
        self.backend = backend
        self.asset_dir = asset_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../ui/data/aot_assets")
        )
        self.tcm_path = os.path.join(self.asset_dir, f"spatial_splat_{backend}.tcm")
        if not os.path.isfile(self.tcm_path):
            raise FileNotFoundError(
                f"native spatial splat artifact is missing for {backend}: {self.tcm_path}"
            )
        try:
            self.module = self.engine.load(self.tcm_path)
        except Exception as exc:
            # Keep the failure actionable.  Falling back silently here would
            # make a GPU production claim impossible and could hide an ABI
            # mismatch between the TCM and the native bridge.
            raise RuntimeError(
                f"Spatial splat TCM failed native load for {backend}: {exc}. "
                "Rebuild with the same Taichi/LLVM runtime as the active "
                "taichi_vision bridge before enabling this path."
            ) from exc
        # The offset graph is added by the resident SR compiler.  Keep this
        # tri-state so an older artifact is detected once and then uses the
        # explicit same-backend batch recovery path without probing every tile.
        self._resident_offset_available = None

    def run(
        self,
        frames: np.ndarray,
        confidence: np.ndarray,
        flow: np.ndarray,
        *,
        scale: int = 2,
        radius: float = 2.0,
        sigma: float = 0.85,
    ) -> tuple[np.ndarray, np.ndarray]:
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        confidence = np.ascontiguousarray(confidence, dtype=np.float32)
        flow = np.ascontiguousarray(flow, dtype=np.float32)
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        if confidence.shape != (n, h, w):
            raise ValueError("confidence shape must be (N,H,W)")
        if flow.shape != (n, h, w, 2):
            raise ValueError("flow shape must be (N,H,W,2)")
        if int(scale) < 1:
            raise ValueError("scale must be >= 1")

        buffers = []
        previous_memory_override = getattr(self.engine, "_force_host_accessible", None)
        if self.backend == "vulkan":
            # The current Vulkan bridge maps graph ndarray arguments during
            # dispatch.  Force shared/host-visible allocations for this
            # readback-oriented wrapper; otherwise device-local buffers fail
            # before the graph executes on drivers without a host-visible heap.
            self.engine.set_force_host_accessible(True)
        try:
            confidence_buf = self.engine.upload(confidence)
            # The public flow contract is [dx, dy].  The gray AOT graph
            # receives separate y/x planes, so split them in the graph's
            # order rather than forwarding the vector channels verbatim.
            flow_y_buf = self.engine.upload(flow[..., 1])
            flow_x_buf = self.engine.upload(flow[..., 0])
            result = np.empty((h * int(scale), w * int(scale), channels), np.float32)
            coverage = np.empty((h * int(scale), w * int(scale)), np.float32)
            buffers = [confidence_buf, flow_y_buf, flow_x_buf]
            for channel in range(channels):
                frame_buf = self.engine.upload(frames[..., channel])
                # Vulkan graph outputs are read back immediately.  Request
                # host-visible allocations explicitly; a device-local output
                # can be written by the graph but cannot be mapped by the
                # bridge's direct readback path on this driver.
                result_buf = self.engine.allocate(
                    (h * int(scale), w * int(scale)),
                    dtype=np.float32,
                    host_accessible=True,
                )
                coverage_buf = self.engine.allocate(
                    (h * int(scale), w * int(scale)),
                    dtype=np.float32,
                    host_accessible=True,
                )
                buffers.extend((frame_buf, result_buf, coverage_buf))
                self.module.run(
                    "robust_splat_gray",
                    frames=frame_buf, confidence=confidence_buf,
                    flow_y=flow_y_buf, flow_x=flow_x_buf,
                    result=result_buf, coverage=coverage_buf,
                    scale=int(scale), radius=float(radius), sigma=float(sigma),
                )
                self.engine.sync()
                result[..., channel] = result_buf.to_numpy()
                if channel == 0:
                    coverage[...] = coverage_buf.to_numpy()
            return result, coverage
        finally:
            for buffer in buffers:
                try:
                    buffer.destroy()
                except Exception:
                    pass
            if self.backend == "vulkan":
                self.engine.set_force_host_accessible(previous_memory_override)

    def run_blockwise(
        self,
        frames: np.ndarray,
        confidence: np.ndarray,
        flow: np.ndarray,
        *,
        scale: int = 2,
        block_size: int = 1024,
        radius: float = 2.0,
        sigma: float = 0.85,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Run the native graph on bounded HR tiles.

        The graph itself remains unchanged.  Source tiles include enough halo
        for the splat radius and observed displacement; flow is translated so
        each tile keeps the global sub-pixel coordinate system.  This avoids
        materialising native result/coverage buffers for the complete HR
        frame while preserving the full-frame graph semantics.
        """
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        confidence = np.ascontiguousarray(confidence, dtype=np.float32)
        flow = np.ascontiguousarray(flow, dtype=np.float32)
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        if confidence.shape != (n, h, w):
            raise ValueError("confidence shape must be (N,H,W)")
        if flow.shape != (n, h, w, 2):
            raise ValueError("flow shape must be (N,H,W,2)")
        scale = int(scale)
        block_size = max(64, int(block_size))
        if scale < 1:
            raise ValueError("scale must be >= 1")

        hr_h, hr_w = h * scale, w * scale
        result = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
        coverage = np.zeros((hr_h, hr_w), dtype=np.float32)
        finite_flow = np.nan_to_num(flow, nan=0.0, posinf=0.0, neginf=0.0)
        source_pad = int(np.ceil(float(radius) / float(scale)))
        source_pad += int(np.ceil(float(np.max(np.abs(finite_flow)))))
        source_pad = max(source_pad, 3)

        for y0 in range(0, hr_h, block_size):
            y1 = min(hr_h, y0 + block_size)
            for x0 in range(0, hr_w, block_size):
                x1 = min(hr_w, x0 + block_size)
                sy0 = max(0, (y0 // scale) - source_pad)
                sx0 = max(0, (x0 // scale) - source_pad)
                sy1 = min(h, int(np.ceil(y1 / float(scale))) + source_pad)
                sx1 = min(w, int(np.ceil(x1 / float(scale))) + source_pad)
                local_frames = frames[:, sy0:sy1, sx0:sx1, :]
                local_conf = confidence[:, sy0:sy1, sx0:sx1]
                local_flow = finite_flow[:, sy0:sy1, sx0:sx1, :].copy()
                local_flow[..., 0] += np.float32(sx0 - (x0 / float(scale)))
                local_flow[..., 1] += np.float32(sy0 - (y0 / float(scale)))
                tile_result, tile_coverage = self.run(
                    local_frames,
                    local_conf,
                    local_flow,
                    scale=scale,
                    radius=radius,
                    sigma=sigma,
                )
                result[y0:y1, x0:x1] = tile_result[: y1 - y0, : x1 - x0]
                coverage[y0:y1, x0:x1] = tile_coverage[: y1 - y0, : x1 - x0]
        return result, coverage

    def run_resident_batch(
        self,
        frames: np.ndarray,
        confidence: np.ndarray,
        flow: np.ndarray,
        *,
        scale: int = 2,
        block_size: int = 1024,
        radius: float = 2.0,
        sigma: float = 0.85,
        accumulator: tuple[np.ndarray, np.ndarray] | None = None,
    ) -> tuple[np.ndarray | None, np.ndarray | None]:
        """Run a batch while keeping its inputs resident across HR tiles.

        The legacy block adapter slices and uploads the source halo again for
        every tile.  This path uploads the batch's frame/flow/confidence planes
        once, dispatches the offset-aware graph for each output tile, and
        downloads only the completed tile.  The output accumulation remains on
        the host because it is the bounded stitching boundary of this graph.
        """
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        confidence = np.ascontiguousarray(
            np.clip(np.nan_to_num(confidence, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0),
            dtype=np.float32,
        )
        flow = np.ascontiguousarray(
            np.nan_to_num(flow, nan=0.0, posinf=0.0, neginf=0.0),
            dtype=np.float32,
        )
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        if n < 1 or channels < 1:
            raise ValueError("frames must contain at least one frame and channel")
        if confidence.shape != (n, h, w):
            raise ValueError("confidence shape must be (N,H,W)")
        if flow.shape != (n, h, w, 2):
            raise ValueError("flow shape must be (N,H,W,2)")
        scale = int(scale)
        block_size = max(64, int(block_size))
        if scale < 1:
            raise ValueError("scale must be >= 1")

        hr_h, hr_w = h * scale, w * scale
        if accumulator is None:
            numerator = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
            denominator = np.zeros((hr_h, hr_w), dtype=np.float32)
        else:
            numerator, denominator = accumulator
            if numerator.shape != (hr_h, hr_w, channels):
                raise ValueError(
                    f"accumulator numerator shape {numerator.shape} != "
                    f"expected {(hr_h, hr_w, channels)}"
                )
            if denominator.shape != (hr_h, hr_w):
                raise ValueError(
                    f"accumulator denominator shape {denominator.shape} != "
                    f"expected {(hr_h, hr_w)}"
                )
        previous_memory_override = getattr(self.engine, "_force_host_accessible", None)
        input_buffers = []
        pending_tiles = []

        def destroy_tile_buffers(tile_buffers):
            for buffer in tile_buffers:
                try:
                    buffer.destroy()
                except Exception:
                    pass

        if self.backend == "vulkan":
            self.engine.set_force_host_accessible(True)
        try:
            confidence_buf = self.engine.upload(confidence)
            flow_y_buf = self.engine.upload(flow[..., 1])
            flow_x_buf = self.engine.upload(flow[..., 0])
            input_buffers = [confidence_buf, flow_y_buf, flow_x_buf]
            frame_buffers = []
            for channel in range(channels):
                frame_buffers.append(self.engine.upload(frames[..., channel]))
            input_buffers.extend(frame_buffers)

            resident_tile_batch = 2
            try:
                tile_bytes = block_size * block_size * (channels + 1) * np.dtype(np.float32).itemsize
                recommend = getattr(self.engine, "recommend_block_batch_size", None)
                if callable(recommend):
                    resident_tile_batch = int(recommend(tile_bytes, cap=4))
            except Exception:
                pass
            resident_tile_batch = max(1, min(4, resident_tile_batch))

            def flush_tiles():
                if not pending_tiles:
                    return
                # Several independent output tiles can be queued against the
                # same resident inputs before one fence/readback cycle.
                self.engine.sync()
                while pending_tiles:
                    (
                        tile_y0,
                        tile_y1,
                        tile_x0,
                        tile_x1,
                        coverage_buf,
                        result_buffers,
                        tile_buffers,
                    ) = pending_tiles.pop(0)
                    try:
                        tile_coverage = np.array(
                            coverage_buf.to_numpy(), dtype=np.float32, copy=True
                        )
                        if accumulator is None:
                            denominator[
                                tile_y0:tile_y1, tile_x0:tile_x1
                            ] = tile_coverage
                        else:
                            denominator[
                                tile_y0:tile_y1, tile_x0:tile_x1
                            ] += tile_coverage
                        for tile_channel, result_buf in enumerate(result_buffers):
                            tile_result = np.array(
                                result_buf.to_numpy(), dtype=np.float32, copy=True
                            )
                            if accumulator is None:
                                numerator[
                                    tile_y0:tile_y1, tile_x0:tile_x1, tile_channel
                                ] = tile_result * tile_coverage
                            else:
                                numerator[
                                    tile_y0:tile_y1, tile_x0:tile_x1, tile_channel
                                ] += tile_result * tile_coverage
                    finally:
                        destroy_tile_buffers(tile_buffers)

            for y0 in range(0, hr_h, block_size):
                y1 = min(hr_h, y0 + block_size)
                for x0 in range(0, hr_w, block_size):
                    x1 = min(hr_w, x0 + block_size)
                    tile_shape = (y1 - y0, x1 - x0)
                    tile_buffers = []
                    try:
                        coverage_buf = self.engine.allocate(
                            tile_shape,
                            dtype=np.float32,
                            host_accessible=(self.backend == "vulkan"),
                        )
                        tile_buffers.append(coverage_buf)
                        result_buffers = []
                        for channel, frame_buf in enumerate(frame_buffers):
                            result_buf = self.engine.allocate(
                                tile_shape,
                                dtype=np.float32,
                                host_accessible=(self.backend == "vulkan"),
                            )
                            tile_buffers.append(result_buf)
                            result_buffers.append(result_buf)
                            self.module.run(
                                "robust_splat_gray_offset",
                                frames=frame_buf,
                                confidence=confidence_buf,
                                flow_y=flow_y_buf,
                                flow_x=flow_x_buf,
                                result=result_buf,
                                coverage=coverage_buf,
                                scale=scale,
                                radius=float(radius),
                                sigma=float(sigma),
                                origin_y=int(y0),
                                origin_x=int(x0),
                            )
                        pending_tiles.append(
                            (
                                y0,
                                y1,
                                x0,
                                x1,
                                coverage_buf,
                                result_buffers,
                                tile_buffers,
                            )
                        )
                        tile_buffers = []
                        if len(pending_tiles) >= resident_tile_batch:
                            flush_tiles()
                    finally:
                        if tile_buffers:
                            destroy_tile_buffers(tile_buffers)

            flush_tiles()

            if accumulator is not None:
                return None, None
            result = numerator
            valid = denominator > np.float32(1e-6)
            result[valid] = numerator[valid] / denominator[valid, None]
            return result, denominator
        finally:
            # If dispatch/readback failed, do not leak queued tile buffers.
            for pending in pending_tiles:
                destroy_tile_buffers(pending[-1])
            for buffer in input_buffers:
                try:
                    buffer.destroy()
                except Exception:
                    pass
            if self.backend == "vulkan":
                self.engine.set_force_host_accessible(previous_memory_override)

    def run_streaming(
        self,
        frames: np.ndarray,
        flow_provider,
        confidence_provider,
        *,
        scale: int = 2,
        block_size: int = 1024,
        radius: float = 2.0,
        sigma: float = 0.85,
        progress_callback=None,
        batch_size: int = 2,
        resident: bool = True,
        accumulator: tuple[np.ndarray, np.ndarray] | None = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Accumulate bounded frame batches through native tiled graphs.

        A batch keeps the input tensors resident while its output tiles are
        consumed.  This preserves the low-RAM contract while avoiding the
        previous ``N x tile_count`` upload/dispatch pattern.
        """
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        hr_h, hr_w = h * int(scale), w * int(scale)
        if accumulator is None:
            numerator = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
            denominator = np.zeros((hr_h, hr_w), dtype=np.float32)
        else:
            numerator, denominator = accumulator
            if numerator.shape != (hr_h, hr_w, channels):
                raise ValueError(
                    f"accumulator numerator shape {numerator.shape} != "
                    f"expected {(hr_h, hr_w, channels)}"
                )
            if denominator.shape != (hr_h, hr_w):
                raise ValueError(
                    f"accumulator denominator shape {denominator.shape} != "
                    f"expected {(hr_h, hr_w)}"
                )
            if numerator.dtype != np.float32 or denominator.dtype != np.float32:
                raise ValueError("streaming accumulator arrays must be float32")
        use_resident = bool(resident)
        batch_size = max(1, int(batch_size))
        if use_resident:
            # A resident batch contains RGB source planes plus confidence and
            # two flow planes. Keep headroom for the active tile outputs and
            # the engine's other allocations instead of blindly filling the
            # shared/device budget.
            requested_batch_size = batch_size
            bytes_per_frame = h * w * (channels + 3) * np.dtype(np.float32).itemsize
            try:
                from taichi_vision import taichi_aot

                memory = taichi_aot.get_memory_status(force=True)
                pipeline_limit = int(memory.get("pipeline_resident_limit", 0) or 0)
            except Exception:
                pipeline_limit = 0
            if pipeline_limit > 0 and bytes_per_frame > 0:
                usable_bytes = int(pipeline_limit * 0.70)
                batch_size = max(1, min(batch_size, usable_bytes // bytes_per_frame))
            if batch_size != requested_batch_size:
                print(
                    "[splattingSR] resident batch clamped for memory: "
                    f"requested={requested_batch_size} effective={batch_size} "
                    f"estimate={bytes_per_frame * batch_size / (1024 * 1024):.1f}MB "
                    f"limit={pipeline_limit / (1024 * 1024):.1f}MB"
                )
        for start in range(0, n, batch_size):
            end = min(n, start + batch_size)
            batch_flow = np.ascontiguousarray(
                np.stack(
                    [np.asarray(flow_provider(k), dtype=np.float32) for k in range(start, end)],
                    axis=0,
                ),
                dtype=np.float32,
            )
            release_flow_planes = getattr(
                flow_provider, "release_resident_flow_planes", None
            )
            if callable(release_flow_planes):
                # ``batch_flow`` now owns the planes needed by the native
                # upload. Do not retain one copy per frame in the producer's
                # cache while confidence maps are being generated.
                release_flow_planes(range(start, end))
            batch_conf = np.ascontiguousarray(
                np.stack(
                    [np.asarray(confidence_provider(k), dtype=np.float32) for k in range(start, end)],
                    axis=0,
                ),
                dtype=np.float32,
            )
            batch_frames = frames[start:end]

            resident_batch_done = False
            if use_resident and self._resident_offset_available is not False:
                try:
                    self.run_resident_batch(
                        batch_frames,
                        batch_conf,
                        batch_flow,
                        scale=scale,
                        block_size=block_size,
                        radius=radius,
                        sigma=sigma,
                        accumulator=(numerator, denominator),
                    )
                    resident_batch_done = True
                    self._resident_offset_available = True
                except Exception as resident_error:
                    # An old TCM has no offset graph.  Recover through the
                    # same active backend's existing native block graph.
                    if self._resident_offset_available is True:
                        raise
                    self._resident_offset_available = False
                    print(
                        "[splattingSR] resident offset graph unavailable; "
                        f"using same-backend batched recovery: {resident_error}"
                    )

            if not resident_batch_done:
                batch_result = None
                batch_coverage = None
                batch_result, batch_coverage = self.run_blockwise(
                    batch_frames,
                    batch_conf,
                    batch_flow,
                    scale=scale,
                    block_size=block_size,
                    radius=radius,
                    sigma=sigma,
                )
                if accumulator is None:
                    numerator += batch_result * batch_coverage[..., None]
                    denominator += batch_coverage
                else:
                    # ``run_blockwise`` is an explicit CPU recovery path. It
                    # still returns a frame-sized batch result, so copy it
                    # into the external backing store and release it before
                    # requesting the next batch.
                    numerator += batch_result * batch_coverage[..., None]
                    denominator += batch_coverage
                    del batch_result, batch_coverage
            if progress_callback:
                for processed in range(start + 1, end + 1):
                    progress_callback(processed, n)
            del batch_flow, batch_conf, batch_frames
        result = numerator
        if accumulator is None:
            valid = denominator > np.float32(1e-6)
            result[valid] = numerator[valid] / denominator[valid, None]
        else:
            # Normalize in-place by output tile.  This is intentionally a
            # scalar tile loop instead of one full-frame boolean/indexing
            # expression, which would allocate several HR-sized temporaries
            # for a memmap-backed result.
            for y0 in range(0, hr_h, block_size):
                y1 = min(hr_h, y0 + block_size)
                for x0 in range(0, hr_w, block_size):
                    x1 = min(hr_w, x0 + block_size)
                    tile_numerator = numerator[y0:y1, x0:x1]
                    tile_denominator = denominator[y0:y1, x0:x1]
                    valid = tile_denominator > np.float32(1e-6)
                    if not np.any(valid):
                        tile_numerator[...] = 0.0
                        continue
                    for channel in range(channels):
                        tile_channel = tile_numerator[..., channel]
                        tile_channel[valid] = (
                            tile_channel[valid] / tile_denominator[valid]
                        )
                    tile_numerator[~valid] = 0.0
            flush = getattr(numerator, "flush", None)
            if callable(flush):
                flush()
        return result, denominator


__all__ = ["SpatialSplatAOT"]
