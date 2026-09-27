"""Production wrapper for the backend-specific ``robust_splat`` TCM graph."""

from __future__ import annotations

import os

import numpy as np


class SpatialSplatAOT:
    """Execute sub-pixel splatting on the already selected AOT backend."""

    def __init__(self, engine=None, asset_dir: str | None = None, *, tcm_path: str | None = None):
        from taichi_vision.taichi_aot import get_engine

        self.engine = engine or get_engine()
        backend = str(getattr(self.engine, "arch", "cpu")).lower()
        if backend == "gles":
            backend = "opengl"
        if backend not in {"cpu", "cuda", "vulkan", "opengl"}:
            raise RuntimeError(f"unsupported spatial splat backend: {backend}")
        self.backend = backend
        self.asset_dir = asset_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../../../ui/data/aot_assets")
        )
        self.tcm_path = tcm_path or os.path.join(self.asset_dir, f"spatial_splat_{backend}.tcm")
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

    def _hann_tiles(
        self,
        frame_buffers,
        confidence_buf,
        flow_y_buf,
        flow_x_buf,
        acc_num,
        acc_den,
        hann_cache,
        *,
        scale,
        block_size,
        overlap,
        radius,
        sigma,
        session=None,
    ) -> int:
        """Blend every overlapping HR block of one resident input set.

        The source planes are already resident, so the 50% overlap costs extra
        dispatches only, never another upload.  ``hann_cache`` keeps one window
        per distinct block shape because edge blocks are clipped.
        """
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            accumulate_tile_hann_taichi,
        )

        # ``frame_buffers`` holds either (N, H, W) for a whole-burst call or
        # (H, W) for one streamed frame, so the LR geometry comes from the last
        # two dimensions.
        lr_h, lr_w = (int(v) for v in frame_buffers[0].shape[-2:])
        hr_h, hr_w = lr_h * int(scale), lr_w * int(scale)
        stride = max(1, int(round(block_size * (1.0 - overlap))))
        host_visible = self.backend == "vulkan"
        tiles = 0
        for y0 in range(0, hr_h, stride):
            for x0 in range(0, hr_w, stride):
                th = min(block_size, hr_h - y0)
                tw = min(block_size, hr_w - x0)
                if th <= 0 or tw <= 0:
                    continue
                tile_shape = (th, tw)
                hann_tile = hann_cache.get(tile_shape)
                if hann_tile is None:
                    hann_tile = taichi_aot.generate_hanning_window_2d(
                        tile_shape, exclude_boundary=True
                    )
                    hann_cache[tile_shape] = hann_tile
                for channel in range(3):
                    if session is None:
                        result_buf = self.engine.allocate(
                            tile_shape,
                            dtype=np.float32,
                            host_accessible=host_visible,
                        )
                        coverage_buf = self.engine.allocate(
                            tile_shape,
                            dtype=np.float32,
                            host_accessible=host_visible,
                        )
                    else:
                        scratch_tag = f"splat_sr.hann_tile.{th}x{tw}"
                        result_buf = session.acquire_buffer(
                            tile_shape,
                            dtype=np.float32,
                            tag=f"{scratch_tag}.result",
                        )
                        coverage_buf = session.acquire_buffer(
                            tile_shape,
                            dtype=np.float32,
                            tag=f"{scratch_tag}.coverage",
                        )
                    try:
                        self.module.run(
                            "robust_splat_gray_offset",
                            frames=frame_buffers[channel],
                            confidence=confidence_buf,
                            flow_y=flow_y_buf,
                            flow_x=flow_x_buf,
                            result=result_buf,
                            coverage=coverage_buf,
                            scale=int(scale),
                            radius=float(radius),
                            sigma=float(sigma),
                            origin_y=int(y0),
                            origin_x=int(x0),
                        )
                        accumulate_tile_hann_taichi(
                            result_buf,
                            coverage_buf,
                            hann_tile,
                            acc_num,
                            acc_den,
                            channel=channel,
                            offset=(y0, x0),
                        )
                    finally:
                        if session is None:
                            result_buf.destroy()
                            coverage_buf.destroy()
                tiles += 1
        return tiles

    def run_hann_blocks_streaming(
        self,
        frames: np.ndarray,
        flow_provider,
        confidence_provider,
        *,
        scale: int = 2,
        block_size: int = 512,
        overlap: float = 0.5,
        radius: float = 2.0,
        sigma: float = 0.85,
        progress_callback=None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Hann-blended HR reconstruction with per-frame streaming inputs.

        Memory-bounded counterpart of :meth:`run_hann_blocks`: only one frame's
        flow, confidence and source planes are resident at a time while the HR
        accumulators persist across the burst.  Accumulation is linear in the
        samples, so accumulating frame by frame yields the same normalized
        result as a single whole-burst call.
        """
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, lr_h, lr_w, channels = frames.shape
        if channels != 3:
            raise ValueError(
                "run_hann_blocks_streaming requires three-channel frames; "
                f"replicate single-channel input before calling (got C={channels})"
            )
        scale = int(scale)
        block_size = max(64, int(block_size))
        overlap = float(np.clip(overlap, 0.0, 0.9))
        if scale < 1:
            raise ValueError("scale must be >= 1")

        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            clear_f32_2d_taichi,
            clear_f32_3d_taichi,
            mean_division_vec3_weight_taichi,
        )

        hr_h, hr_w = lr_h * scale, lr_w * scale
        previous_memory_override = getattr(self.engine, "_force_host_accessible", None)
        hann_cache: dict[tuple[int, int], object] = {}
        acc_num = None
        acc_den = None
        final = None
        ref_hr_buf = None
        if self.backend == "vulkan":
            self.engine.set_force_host_accessible(True)
        try:
            acc_num = self.engine.allocate((hr_h, hr_w, 3), dtype=np.float32)
            acc_den = self.engine.allocate((hr_h, hr_w), dtype=np.float32)
            clear_f32_3d_taichi(acc_num)
            clear_f32_2d_taichi(acc_den)

            source_ref = taichi_aot.upload(
                np.ascontiguousarray(frames[0], dtype=np.float32)
            )
            try:
                ref_hr_buf = taichi_aot.resize(
                    source_ref,
                    (hr_w, hr_h),
                    interpolation=taichi_aot.INTER_CUBIC,
                    return_gpu=True,
                )
            finally:
                source_ref.destroy()

            tiles = 0
            for index in range(n):
                flow = np.ascontiguousarray(
                    np.nan_to_num(
                        np.asarray(flow_provider(index), dtype=np.float32),
                        nan=0.0,
                        posinf=0.0,
                        neginf=0.0,
                    ),
                    dtype=np.float32,
                )
                if flow.shape != (lr_h, lr_w, 2):
                    raise ValueError(
                        f"flow_provider({index}) returned {flow.shape}; "
                        f"expected {(lr_h, lr_w, 2)}"
                    )
                confidence = np.ascontiguousarray(
                    np.clip(
                        np.nan_to_num(
                            np.asarray(confidence_provider(index), dtype=np.float32),
                            nan=0.0,
                            posinf=0.0,
                            neginf=0.0,
                        ),
                        0.0,
                        1.0,
                    ),
                    dtype=np.float32,
                )
                if confidence.shape != (lr_h, lr_w):
                    raise ValueError(
                        f"confidence_provider({index}) returned {confidence.shape}; "
                        f"expected {(lr_h, lr_w)}"
                    )
                # The graph is compiled for (N, H, W) inputs, so one streamed
                # frame is uploaded with a leading batch axis of 1.
                uploaded = [
                    self.engine.upload(confidence[None, ...]),
                    self.engine.upload(np.ascontiguousarray(flow[..., 1][None, ...])),
                    self.engine.upload(np.ascontiguousarray(flow[..., 0][None, ...])),
                ]
                try:
                    frame_buffers = [
                        self.engine.upload(
                            np.ascontiguousarray(frames[index, ..., c][None, ...])
                        )
                        for c in range(3)
                    ]
                    uploaded.extend(frame_buffers)
                    tiles = self._hann_tiles(
                        frame_buffers,
                        uploaded[0],
                        uploaded[1],
                        uploaded[2],
                        acc_num,
                        acc_den,
                        hann_cache,
                        scale=scale,
                        block_size=block_size,
                        overlap=overlap,
                        radius=radius,
                        sigma=sigma,
                    )
                finally:
                    for buffer in uploaded:
                        try:
                            buffer.destroy()
                        except Exception:
                            pass
                if progress_callback:
                    progress_callback(index + 1, n)

            stride = max(1, int(round(block_size * (1.0 - overlap))))
            print(
                f"[splattingSR] Hann blocks streaming backend={self.backend} "
                f"block={block_size}px overlap={overlap:.2f} stride={stride}px "
                f"frames={n} tiles/frame={tiles}"
            )
            final = mean_division_vec3_weight_taichi(
                sum_img=acc_num, sum_weight=acc_den, ref_img=ref_hr_buf
            )
            self.engine.sync()
            result = np.asarray(final.to_numpy(), dtype=np.float32)
            coverage = np.asarray(acc_den.to_numpy(), dtype=np.float32)
            return result, coverage
        finally:
            for hann_tile in hann_cache.values():
                try:
                    hann_tile.destroy()
                except Exception:
                    pass
            for buffer in (final, ref_hr_buf, acc_den, acc_num):
                if buffer is not None:
                    try:
                        buffer.destroy()
                    except Exception:
                        pass
            if self.backend == "vulkan":
                self.engine.set_force_host_accessible(previous_memory_override)

    def run_hann_blocks(
        self,
        frames: np.ndarray,
        confidence: np.ndarray,
        flow: np.ndarray,
        *,
        scale: int = 2,
        block_size: int = 512,
        overlap: float = 0.5,
        radius: float = 2.0,
        sigma: float = 0.85,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Reconstruct HR from overlapping blocks blended by a Hann window.

        Each ``block_size`` x ``block_size`` HR block is produced by the
        resident ``robust_splat_gray_offset`` dispatch and then blended into the
        global accumulators by taichi_vision's ``accumulate_tile_hann``.  The
        accumulated weight is the Hann window times the splat coverage, so
        dividing the two yields a weighted average of the overlapping windows
        instead of a hard tile seam.

        The window (``generate_hanning_window_2d``), the blend
        (``accumulate_tile_hann``) and the final division
        (``mean_division_vec3_weight``) all come from taichi_vision.  The source
        tensors stay resident for the whole pass, so the 50% overlap costs
        dispatch time only and never an extra upload.

        Only three-channel data is accepted: the shared-weight division kernel
        is vec3, so callers that have grayscale replicate it instead of silently
        reinterpreting the accumulator layout.
        """
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        confidence = np.ascontiguousarray(
            np.clip(
                np.nan_to_num(confidence, nan=0.0, posinf=0.0, neginf=0.0),
                0.0,
                1.0,
            ),
            dtype=np.float32,
        )
        flow = np.ascontiguousarray(
            np.nan_to_num(flow, nan=0.0, posinf=0.0, neginf=0.0), dtype=np.float32
        )
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        if channels != 3:
            raise ValueError(
                "run_hann_blocks requires three-channel frames; replicate "
                f"single-channel input before calling (got C={channels})"
            )
        if confidence.shape != (n, h, w):
            raise ValueError("confidence shape must be (N,H,W)")
        if flow.shape != (n, h, w, 2):
            raise ValueError("flow shape must be (N,H,W,2)")
        scale = int(scale)
        block_size = max(64, int(block_size))
        overlap = float(np.clip(overlap, 0.0, 0.9))
        if scale < 1:
            raise ValueError("scale must be >= 1")

        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            accumulate_tile_hann_taichi,
            clear_f32_2d_taichi,
            clear_f32_3d_taichi,
            mean_division_vec3_weight_taichi,
        )

        hr_h, hr_w = h * scale, w * scale
        stride = max(1, int(round(block_size * (1.0 - overlap))))

        previous_memory_override = getattr(self.engine, "_force_host_accessible", None)
        input_buffers: list = []
        hann_cache: dict[tuple[int, int], object] = {}
        acc_num = None
        acc_den = None
        final = None
        if self.backend == "vulkan":
            self.engine.set_force_host_accessible(True)
        try:
            acc_num = self.engine.allocate((hr_h, hr_w, 3), dtype=np.float32)
            acc_den = self.engine.allocate((hr_h, hr_w), dtype=np.float32)
            # The engine pool may hand back dirty storage, so the accumulators
            # are cleared on the device rather than by uploading host zeros.
            clear_f32_3d_taichi(acc_num)
            clear_f32_2d_taichi(acc_den)

            confidence_buf = self.engine.upload(confidence)
            flow_y_buf = self.engine.upload(flow[..., 1])
            flow_x_buf = self.engine.upload(flow[..., 0])
            input_buffers = [confidence_buf, flow_y_buf, flow_x_buf]
            frame_buffers = []
            for channel in range(3):
                frame_buffers.append(self.engine.upload(frames[..., channel]))
            input_buffers.extend(frame_buffers)

            # HR reference for the uncovered fallback.  The division graph
            # substitutes it wherever the accumulated weight is ~0, so an
            # all-rejected region degrades to the reference instead of a hole.
            source_ref = taichi_aot.upload(np.ascontiguousarray(frames[0], dtype=np.float32))
            try:
                ref_hr_buf = taichi_aot.resize(
                    source_ref,
                    (hr_w, hr_h),
                    interpolation=taichi_aot.INTER_CUBIC,
                    return_gpu=True,
                )
            finally:
                source_ref.destroy()
            input_buffers.append(ref_hr_buf)

            self._hann_tiles(
                frame_buffers,
                confidence_buf,
                flow_y_buf,
                flow_x_buf,
                acc_num,
                acc_den,
                hann_cache,
                scale=scale,
                block_size=block_size,
                overlap=overlap,
                radius=radius,
                sigma=sigma,
            )
            final = mean_division_vec3_weight_taichi(
                sum_img=acc_num, sum_weight=acc_den, ref_img=ref_hr_buf
            )
            self.engine.sync()
            result = np.asarray(final.to_numpy(), dtype=np.float32)
            coverage = np.asarray(acc_den.to_numpy(), dtype=np.float32)
            return result, coverage
        finally:
            for buffer in input_buffers:
                try:
                    buffer.destroy()
                except Exception:
                    pass
            for hann_tile in hann_cache.values():
                try:
                    hann_tile.destroy()
                except Exception:
                    pass
            for buffer in (final, acc_den, acc_num):
                if buffer is not None:
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


class SplatSRRuntime:
    """Process-wide cache for the heavy, repeated parts of the SR reconstruction.

    Resolving artifacts, loading module handles, generating Hann windows and
    allocating the HR accumulators are done once and reused, so a repeated job
    does not re-resolve, re-load, re-allocate or free them again.

    Every buffer this class hands out is **scratch**: its contents are undefined
    on entry.  Accumulator buffers are cleared before each use, so a previous job
    can never bleed into the next one.  The cache is keyed by the active backend
    and by shape, and a backend change invalidates it entirely.

    Not thread-safe: the AOT engine owns one process-global context and the SR
    route is sequential per job.
    """

    def __init__(self):
        self._arch = None
        self._splat = None
        self._spatial_module = None
        self._spatial_tcm = None
        self._hann = {}
        self._accumulators = {}
        self._output = {}
        self.counters = {"dispatch": 0, "allocate": 0, "destroy": 0, "upload": 0}

    # -- lifecycle -------------------------------------------------------
    @staticmethod
    def _current_arch() -> str:
        from taichi_vision import taichi_aot

        return str(getattr(taichi_aot.engine, "arch", "cpu")).lower()

    def _ensure(self):
        from taichi_vision import taichi_aot

        arch = self._current_arch()
        if self._arch != arch:
            # A different backend must never reuse buffers from the old context.
            self.close()
            self._arch = arch
        if self._splat is None:
            self._splat = SpatialSplatAOT()
        if self._spatial_module is None:
            from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
                _resolve_spatial_tcm,
                _tcm_graph_available,
            )

            self._spatial_tcm = _resolve_spatial_tcm(taichi_aot.engine)
            for graph in (
                "clear_f32_3d",
                "clear_f32_2d",
                "mean_division_vec3_scalar_weight",
            ):
                if not _tcm_graph_available(self._spatial_tcm, graph):
                    raise RuntimeError(
                        f"spatial TCM is missing the '{graph}' graph required by the "
                        f"fused SR route: {self._spatial_tcm}. Recompile the spatial "
                        "TCM for the active backend."
                    )
            self._spatial_module = taichi_aot.engine.load(self._spatial_tcm)
        return self

    def close(self) -> None:
        """Release every cached buffer.  Safe to call more than once."""
        for mapping in (self._hann, self._output):
            for buffer in mapping.values():
                _safe_destroy(buffer)
            mapping.clear()
        for pair in self._accumulators.values():
            for buffer in pair:
                _safe_destroy(buffer)
        self._accumulators.clear()
        self._splat = None
        self._spatial_module = None
        self._spatial_tcm = None
        self._arch = None

    # -- accessors -------------------------------------------------------
    @property
    def backend(self) -> str:
        self._ensure()
        return self._arch

    def splat(self) -> "SpatialSplatAOT":
        self._ensure()
        return self._splat

    def spatial_module(self):
        self._ensure()
        return self._spatial_module

    def hann_window(self, shape):
        self._ensure()
        from taichi_vision import taichi_aot

        key = (int(shape[0]), int(shape[1]))
        buffer = self._hann.get(key)
        if buffer is None:
            self._count_alloc(1)
            buffer = taichi_aot.generate_hanning_window_2d(key, exclude_boundary=True)
            self._hann[key] = buffer
        return buffer

    def accumulators(self, hr_h: int, hr_w: int):
        """Return cleared ``(acc_num, acc_den)`` scratch buffers for this size."""
        self._ensure()
        from taichi_vision import taichi_aot

        key = (int(hr_h), int(hr_w))
        pair = self._accumulators.get(key)
        if pair is None:
            with _force_host_visible(taichi_aot.engine, self._arch == "vulkan"):
                acc_num = taichi_aot.engine.allocate(
                    (key[0], key[1], 3), dtype=np.float32
                )
                acc_den = taichi_aot.engine.allocate(
                    (key[0], key[1]), dtype=np.float32, host_accessible=True
                )
            self._count_alloc(2)
            pair = (acc_num, acc_den)
            self._accumulators[key] = pair
        self._clear(*pair, key[0], key[1])
        return pair

    def reference(self, hr_h: int, hr_w: int):
        """Allocate the HR fallback reference.

        This one is deliberately **not** cached: the resize graph does not accept
        a plain 3-D buffer as its ``dst`` argument, so the buffer is created per
        job and released when the job ends.  It is a single allocation, not the
        per-tile churn the cache exists to remove.
        """
        self._ensure()
        from taichi_vision import taichi_aot

        with _force_host_visible(taichi_aot.engine, self._arch == "vulkan"):
            buffer = taichi_aot.engine.allocate((hr_h, hr_w, 3), dtype=np.float32)
        self._count_alloc(1)
        return buffer

    def output(self, hr_h: int, hr_w: int):
        """Return the reusable final-result buffer (read back by the caller)."""
        self._ensure()
        from taichi_vision import taichi_aot

        key = (int(hr_h), int(hr_w))
        buffer = self._output.get(key)
        if buffer is None:
            with _force_host_visible(taichi_aot.engine, self._arch == "vulkan"):
                buffer = taichi_aot.engine.allocate(
                    (key[0], key[1], 3), dtype=np.float32, host_accessible=True
                )
            self._count_alloc(1)
            self._output[key] = buffer
        return buffer

    # -- internals -------------------------------------------------------
    def _clear(self, acc_num, acc_den, hr_h: int, hr_w: int) -> None:
        module = self.spatial_module()
        module.run("clear_f32_3d", dst=acc_num, h=int(hr_h), w=int(hr_w), c=3)
        module.run("clear_f32_2d", dst=acc_den, h=int(hr_h), w=int(hr_w))
        self.counters["dispatch"] += 2

    def _count_alloc(self, count: int) -> None:
        self.counters["allocate"] += int(count)


_RUNTIME = SplatSRRuntime()


def get_runtime() -> SplatSRRuntime:
    """Return the process-wide SR runtime cache."""
    return _RUNTIME


class _force_host_visible:
    """Scope the engine's host-visible override to specific allocations.

    The Vulkan bridge maps graph ndarray arguments during dispatch, so buffers
    that are read back must stay host visible.  Keeping the override off for the
    rest avoids forcing every allocation into shared memory.
    """

    def __init__(self, engine, enabled: bool):
        self._engine = engine
        self._enabled = bool(enabled)
        self._previous = None

    def __enter__(self):
        if self._enabled:
            self._previous = getattr(self._engine, "_force_host_accessible", None)
            self._engine.set_force_host_accessible(True)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._enabled:
            self._engine.set_force_host_accessible(self._previous)
        return False


def _as_scalar_3d(buffer):
    """Present a vector-field buffer as a plain 3-D ndarray for graph dispatch."""
    if getattr(buffer, "is_vector", False):
        return buffer.view_as_vector(False)
    return buffer


def _safe_destroy(buffer) -> None:
    if buffer is None:
        return
    try:
        buffer.destroy()
    except Exception:
        pass


def run_fused_burst(
    frames: np.ndarray,
    confidence: np.ndarray,
    flow: np.ndarray,
    *,
    scale: int = 2,
    block_size: int = 512,
    overlap: float = 0.5,
    radius: float = 2.0,
    sigma: float = 0.85,
    runtime: SplatSRRuntime | None = None,
    progress_callback=None,
) -> tuple[np.ndarray, np.ndarray]:
    """Reconstruct HR from a whole burst with one dispatch per output tile.

    The fused graph carries the splat, the Hann blend and the accumulation, so
    this path needs **no per-tile buffers and no second graph**.  Inputs are
    uploaded as four batches instead of per frame, which matters because a single
    upload is the dominant fixed cost on CUDA.

    Returns ``(result, coverage)`` as fresh arrays; the internal buffers are
    cached and reused by the next job.
    """
    frames = np.ascontiguousarray(frames, dtype=np.float32)
    confidence = np.ascontiguousarray(
        np.clip(np.nan_to_num(confidence, nan=0.0, posinf=0.0, neginf=0.0), 0.0, 1.0),
        dtype=np.float32,
    )
    flow = np.ascontiguousarray(
        np.nan_to_num(flow, nan=0.0, posinf=0.0, neginf=0.0), dtype=np.float32
    )
    if frames.ndim != 4:
        raise ValueError("frames must have shape (N,H,W,C)")
    n, lr_h, lr_w, channels = frames.shape
    if channels != 3:
        raise ValueError(
            "run_fused_burst requires three-channel frames; replicate "
            f"single-channel input before calling (got C={channels})"
        )
    if confidence.shape != (n, lr_h, lr_w):
        raise ValueError("confidence shape must be (N,H,W)")
    if flow.shape != (n, lr_h, lr_w, 2):
        raise ValueError("flow shape must be (N,H,W,2)")
    scale = int(scale)
    block_size = max(64, int(block_size))
    overlap = float(np.clip(overlap, 0.0, 0.9))
    if scale < 1:
        raise ValueError("scale must be >= 1")

    from taichi_vision import taichi_aot

    rt = runtime or get_runtime()
    splat = rt.splat()
    spatial_module = rt.spatial_module()
    arch = rt.backend
    hr_h, hr_w = lr_h * scale, lr_w * scale
    stride = max(1, int(round(block_size * (1.0 - overlap))))

    acc_num, acc_den = rt.accumulators(hr_h, hr_w)
    out = rt.output(hr_h, hr_w)

    # Five batched transfers instead of six per frame: the burst planes, the
    # confidence, both flow axes, and the LR reference used for the fallback.
    owned = []
    ref_hr = None
    try:
        with _force_host_visible(taichi_aot.engine, arch == "vulkan"):
            frames_gpu = taichi_aot.upload(frames)
            confidence_gpu = taichi_aot.upload(confidence)
            flow_y_gpu = taichi_aot.upload(np.ascontiguousarray(flow[..., 1]))
            flow_x_gpu = taichi_aot.upload(np.ascontiguousarray(flow[..., 0]))
            reference_lr_gpu = taichi_aot.upload(np.ascontiguousarray(frames[0]))
            rt.counters["upload"] += 5
            ref_hr = taichi_aot.resize(
                reference_lr_gpu,
                (hr_w, hr_h),
                interpolation=taichi_aot.INTER_CUBIC,
                return_gpu=True,
            )
        rt.counters["dispatch"] += 1
        owned = [frames_gpu, confidence_gpu, flow_y_gpu, flow_x_gpu, reference_lr_gpu]

        tiles = 0
        for y0 in range(0, hr_h, stride):
            for x0 in range(0, hr_w, stride):
                th = min(block_size, hr_h - y0)
                tw = min(block_size, hr_w - x0)
                if th <= 0 or tw <= 0:
                    continue
                hann_tile = rt.hann_window((th, tw))
                splat.module.run(
                    "robust_splat_hann_offset",
                    frames=frames_gpu,
                    confidence=confidence_gpu,
                    flow_y=flow_y_gpu,
                    flow_x=flow_x_gpu,
                    hann_tile=hann_tile,
                    acc_num=acc_num,
                    acc_den=acc_den,
                    scale=scale,
                    radius=float(radius),
                    sigma=float(sigma),
                    origin_y=int(y0),
                    origin_x=int(x0),
                    tile_h=int(th),
                    tile_w=int(tw),
                )
                rt.counters["dispatch"] += 1
                tiles += 1
                if progress_callback:
                    progress_callback(tiles)
        print(
            f"[splattingSR] fused burst backend={arch} block={block_size}px "
            f"overlap={overlap:.2f} stride={stride}px frames={n} tiles={tiles}"
        )

        # The resident inputs are per job and cannot be reused (upload always
        # allocates), so release them before the division to keep the peak down.
        for buffer in owned:
            _safe_destroy(buffer)
        owned = []

        with _force_host_visible(taichi_aot.engine, arch == "vulkan"):
            # ``resize`` returns a vector field for 3-channel input; the division
            # graph expects plain 3-D ndarrays, so normalize the view the same way
            # the canonical wrapper does.
            spatial_module.run(
                "mean_division_vec3_scalar_weight",
                sum_img=_as_scalar_3d(acc_num),
                sum_weight=acc_den,
                ref_img=_as_scalar_3d(ref_hr),
                dst=_as_scalar_3d(out),
                h=int(hr_h),
                w=int(hr_w),
            )
            rt.counters["dispatch"] += 1
            taichi_aot.engine.sync()
            result = np.array(out.to_numpy(), dtype=np.float32, copy=True)
            coverage = np.array(acc_den.to_numpy(), dtype=np.float32, copy=True)
        return result, coverage
    finally:
        for buffer in owned:
            _safe_destroy(buffer)
        _safe_destroy(ref_hr)


class SessionHannAccumulator:
    """Per-job, one-support-at-a-time Hann splat accumulator.

    The decoded carrier and flow stay host-side for one support only. Spatial
    confidence may be passed as a borrowed 2-D GPU buffer and is reinterpreted
    as the graph's singleton-batch view without copying or reading it back.
    Persistent HR state belongs to the caller's BufferSession.
    """

    def __init__(
        self,
        reference_rgb: np.ndarray,
        *,
        session,
        scale: int = 2,
        block_size: int = 512,
        overlap: float = 0.5,
        radius: float = 2.0,
        sigma: float = 0.85,
    ):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            clear_f32_2d_taichi,
            clear_f32_3d_taichi,
        )
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer

        reference = np.ascontiguousarray(reference_rgb, dtype=np.float32)
        if reference.ndim != 3 or reference.shape[2] != 3:
            raise ValueError("SessionHannAccumulator requires HxWx3 reference RGB")
        self.session = session
        self.engine = taichi_aot.engine
        self.runtime = get_runtime()
        self.splat = self.runtime.splat()
        self.spatial_module = self.runtime.spatial_module()
        self.backend = self.runtime.backend
        self.lr_h, self.lr_w = (int(reference.shape[0]), int(reference.shape[1]))
        self.hr_h = self.lr_h * int(scale)
        self.hr_w = self.lr_w * int(scale)
        self.scale = int(scale)
        self.block_size = max(64, int(block_size))
        self.overlap = float(np.clip(overlap, 0.0, 0.9))
        self.radius = float(radius)
        self.sigma = float(sigma)
        if self.scale < 1:
            raise ValueError("scale must be >= 1")

        self._previous_memory_override = getattr(
            self.engine, "_force_host_accessible", None
        )
        self._closed = False
        self._finalized = False
        self._hann_cache: dict[tuple[int, int], object] = {}
        self._tiles_processed = 0

        with _force_host_visible(self.engine, self.backend == "vulkan"):
            self.acc_num = session.own(
                self.engine.allocate(
                    (self.hr_h, self.hr_w, 3), dtype=np.float32
                )
            )
            self.acc_den = session.own(
                self.engine.allocate(
                    (self.hr_h, self.hr_w),
                    dtype=np.float32,
                    host_accessible=(self.backend == "vulkan"),
                )
            )
            self.reference_lr = session.own(taichi_aot.upload(reference))
            self.reference_hr = session.track_result(
                taichi_aot.resize(
                    self.reference_lr,
                    (self.hr_w, self.hr_h),
                    interpolation=taichi_aot.INTER_CUBIC,
                    return_gpu=True,
                )
            )
            clear_f32_3d_taichi(self.acc_num)
            clear_f32_2d_taichi(self.acc_den)

        self._prepare_hann_windows()
        # The session releases this coordinator before its buffers. On an
        # exception/cancel it synchronizes queued work and restores Vulkan's
        # host-visible allocation override before retiring those buffers.
        session.own(self, releaser=lambda accumulator: accumulator.close())

    def _prepare_hann_windows(self) -> None:
        from taichi_vision import taichi_aot

        stride = max(1, int(round(self.block_size * (1.0 - self.overlap))))
        for y0 in range(0, self.hr_h, stride):
            for x0 in range(0, self.hr_w, stride):
                shape = (
                    min(self.block_size, self.hr_h - y0),
                    min(self.block_size, self.hr_w - x0),
                )
                if shape not in self._hann_cache:
                    self._hann_cache[shape] = self.session.track_result(
                        taichi_aot.generate_hanning_window_2d(
                            shape, exclude_boundary=True
                        )
                    )

    @staticmethod
    def _batched_confidence_view(buffer, shape, engine):
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer

        if not isinstance(buffer, TaichiGPUBuffer):
            return None
        expected_engine = (
            engine._live() if hasattr(engine, "_live") else engine
        )
        buffer_engine = (
            buffer.engine._live()
            if hasattr(buffer.engine, "_live")
            else buffer.engine
        )
        if buffer_engine is not expected_engine:
            raise ValueError("confidence buffer belongs to another AOT engine")
        expected = tuple(int(v) for v in shape)
        if tuple(int(v) for v in buffer.shape) == (1, *expected):
            return buffer
        if tuple(int(v) for v in buffer.shape) != expected:
            raise ValueError(
                f"confidence buffer shape {buffer.shape} does not match {expected}"
            )
        view = TaichiGPUBuffer(
            buffer.size_bytes,
            buffer.handle,
            (1, *expected),
            dtype=buffer.dtype,
            is_vector=False,
            engine=engine,
            is_owner=False,
            host_accessible=buffer.host_accessible,
        )
        view._parent_ref = buffer
        return view

    def add_frame(self, frame_rgb, flow, confidence) -> int:
        from taichi_vision.taichi_aot.engine import TaichiGPUBuffer
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            clear_f32_3d_taichi,
        )

        if self._closed or self._finalized:
            raise RuntimeError("Splat accumulator is no longer accepting frames")
        frame = np.ascontiguousarray(frame_rgb, dtype=np.float32)
        if frame.shape != (self.lr_h, self.lr_w, 3):
            raise ValueError(
                f"support frame shape {frame.shape} != {(self.lr_h, self.lr_w, 3)}"
            )
        if flow is not None:
            flow = np.ascontiguousarray(flow, dtype=np.float32)
            if flow.shape != (self.lr_h, self.lr_w, 2):
                raise ValueError(
                    f"flow shape {flow.shape} != {(self.lr_h, self.lr_w, 2)}"
                )

        confidence_view = self._batched_confidence_view(
            confidence, (self.lr_h, self.lr_w), self.engine
        )
        borrowed_confidence = isinstance(confidence, TaichiGPUBuffer)
        if borrowed_confidence:
            self.session.borrow(confidence)

        uploaded = []
        try:
            with _force_host_visible(self.engine, self.backend == "vulkan"):
                if confidence_view is None:
                    confidence_array = np.ascontiguousarray(
                        np.clip(
                            np.nan_to_num(
                                confidence, nan=0.0, posinf=0.0, neginf=0.0
                            ),
                            0.0,
                            1.0,
                        ),
                        dtype=np.float32,
                    )
                    confidence_view = self.session.own(
                        self.engine.upload(confidence_array[None, ...])
                    )
                    uploaded.append(confidence_view)
                if flow is None:
                    flow_y = self.session.own(
                        self.engine.allocate((1, self.lr_h, self.lr_w), dtype=np.float32)
                    )
                    flow_x = self.session.own(
                        self.engine.allocate((1, self.lr_h, self.lr_w), dtype=np.float32)
                    )
                    clear_f32_3d_taichi(flow_y)
                    clear_f32_3d_taichi(flow_x)
                else:
                    flow_y = self.session.own(
                        self.engine.upload(
                            np.ascontiguousarray(flow[..., 1][None, ...])
                        )
                    )
                    flow_x = self.session.own(
                        self.engine.upload(
                            np.ascontiguousarray(flow[..., 0][None, ...])
                        )
                    )
                uploaded.extend((flow_y, flow_x))
                frame_buffers = [
                    self.session.own(
                        self.engine.upload(
                            np.ascontiguousarray(frame[..., channel][None, ...])
                        )
                    )
                    for channel in range(3)
                ]
                uploaded.extend(frame_buffers)
                self._tiles_processed = self.splat._hann_tiles(
                    frame_buffers,
                    confidence_view,
                    flow_y,
                    flow_x,
                    self.acc_num,
                    self.acc_den,
                    self._hann_cache,
                    scale=self.scale,
                    block_size=self.block_size,
                    overlap=self.overlap,
                    radius=self.radius,
                    sigma=self.sigma,
                    session=self.session,
                )
                # A support's upload buffers and weight map are not reusable
                # until every tile has consumed them. Keep the stream strictly
                # one-support-in-flight even on asynchronous native backends.
                self.engine.sync()
        finally:
            for buffer in uploaded:
                try:
                    self.session.release_buffer(buffer)
                except Exception:
                    pass
            if borrowed_confidence:
                self.session.release_borrow(confidence)
        return self._tiles_processed

    def finalize(self) -> np.ndarray:
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            mean_division_vec3_weight_taichi,
        )

        if self._closed:
            raise RuntimeError("Splat accumulator is closed")
        if self._finalized:
            raise RuntimeError("Splat accumulator was already finalized")
        with _force_host_visible(self.engine, self.backend == "vulkan"):
            output = mean_division_vec3_weight_taichi(
                sum_img=self.acc_num,
                sum_weight=self.acc_den,
                ref_img=self.reference_hr,
            )
            output = self.session.track_result(output)
            self.engine.sync()
            # The host result outlives this job session. Transfer ownership
            # explicitly, read it once, then retire the native allocation.
            output = self.session.detach(output)
            try:
                result = np.asarray(output.to_numpy(), dtype=np.float32)
            finally:
                output.destroy()
        self._finalized = True
        return result

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if not self._finalized:
            try:
                self.engine.sync()
            except Exception:
                pass
        if self.backend == "vulkan":
            try:
                self.engine.set_force_host_accessible(
                    self._previous_memory_override
                )
            except Exception:
                pass


__all__ = [
    "SpatialSplatAOT",
    "SplatSRRuntime",
    "SessionHannAccumulator",
    "get_runtime",
    "run_fused_burst",
]
