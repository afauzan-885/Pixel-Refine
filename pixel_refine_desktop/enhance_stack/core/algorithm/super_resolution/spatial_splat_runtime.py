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
                result_buf = self.engine.allocate((h * int(scale), w * int(scale)), dtype=np.float32)
                coverage_buf = self.engine.allocate((h * int(scale), w * int(scale)), dtype=np.float32)
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
    ) -> tuple[np.ndarray, np.ndarray]:
        """Accumulate one source frame at a time through native tiled graphs."""
        frames = np.ascontiguousarray(frames, dtype=np.float32)
        if frames.ndim != 4:
            raise ValueError("frames must have shape (N,H,W,C)")
        n, h, w, channels = frames.shape
        hr_h, hr_w = h * int(scale), w * int(scale)
        numerator = np.zeros((hr_h, hr_w, channels), dtype=np.float32)
        denominator = np.zeros((hr_h, hr_w), dtype=np.float32)
        for k in range(n):
            one_flow = np.ascontiguousarray(flow_provider(k), dtype=np.float32)
            one_conf = np.ascontiguousarray(confidence_provider(k), dtype=np.float32)
            one_result, one_coverage = self.run_blockwise(
                frames[k : k + 1],
                one_conf[None, ...],
                one_flow[None, ...],
                scale=scale,
                block_size=block_size,
                radius=radius,
                sigma=sigma,
            )
            numerator += one_result * one_coverage[..., None]
            denominator += one_coverage
            if progress_callback:
                progress_callback(k + 1, n)
            del one_flow, one_conf, one_result, one_coverage
        result = np.zeros_like(numerator)
        valid = denominator > np.float32(1e-6)
        result[valid] = numerator[valid] / denominator[valid, None]
        return result, denominator


__all__ = ["SpatialSplatAOT"]
