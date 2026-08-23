"""Shared SpatialFusion weight-map stage for confidence-guided SR.

This module deliberately owns only the alignment-aware confidence stage.  It
does not normalize or merge frames: SplattingSR consumes the returned map as a
per-source confidence, while SpatialFusion keeps its existing weighted-sum
accumulator.  All temporary buffers are target-owned and released by
``close()``.
"""

from __future__ import annotations

import numpy as np


def _numpy_spatial_weight(reference: np.ndarray, current: np.ndarray, noise_sigma: float) -> np.ndarray:
    """Deterministic CPU oracle used only when the CPU spatial TCM is invalid."""
    import cv2

    diff = np.asarray(current, dtype=np.float32) - np.asarray(reference, dtype=np.float32)
    local_mse = cv2.GaussianBlur(diff * diff, (5, 5), sigmaX=1.0)
    denom = max(2.0 * float(noise_sigma) * float(noise_sigma), 1.0e-8)
    return np.clip(np.exp(-local_mse / np.float32(denom)), 0.0, 1.0).astype(np.float32)


def _numpy_remap_with_flow(current: np.ndarray, flow: np.ndarray) -> np.ndarray:
    """CPU oracle for the analysis warp (flow[...,0]=x, flow[...,1]=y)."""
    import cv2

    h, w = current.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    map_x = np.ascontiguousarray(xx + flow[..., 0], dtype=np.float32)
    map_y = np.ascontiguousarray(yy + flow[..., 1], dtype=np.float32)
    return np.ascontiguousarray(
        cv2.remap(
            np.ascontiguousarray(current, dtype=np.float32),
            map_x,
            map_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE,
        ),
        dtype=np.float32,
    )


class SpatialWeightMapGenerator:
    """Generate one SpatialFusion-compatible weight map per source frame."""

    def __init__(
        self,
        reference: np.ndarray,
        *,
        tile_size: int = 256,
        overlap: float = 0.2,
        motion_sensitivity: float = 1.0,
        noise_offset_factor: float = 0.0,
        noise_sigma: float = 0.015,
        early_exit_threshold: float = 0.05,
    ):
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            SpatialScratchCache,
        )
        from taichi_vision import taichi_aot

        reference = np.ascontiguousarray(reference, dtype=np.float32)
        if reference.ndim != 2:
            raise ValueError("SpatialWeightMapGenerator expects a 2-D luminance reference")
        self._aot = taichi_aot
        self._engine = taichi_aot.engine
        self._shape = tuple(int(v) for v in reference.shape)
        self._tile_h = max(8, min(int(tile_size), self._shape[0]))
        self._tile_w = max(8, min(int(tile_size), self._shape[1]))
        self._overlap = float(np.clip(overlap, 0.0, 0.95))
        self._motion_sensitivity = float(motion_sensitivity)
        self._noise_offset_factor = float(noise_offset_factor)
        self._noise_sigma = float(noise_sigma)
        self._early_exit_threshold = float(early_exit_threshold)
        # Keep a host oracle for CPU recovery and avoid re-downloading the
        # reference once per block when an old/invalid CPU TCM cache is found.
        self._reference_host = reference.copy()
        self._scratch = SpatialScratchCache()
        self._closed = False

        h, w = self._shape
        step_y = max(1, int(self._tile_h * (1.0 - self._overlap)))
        step_x = max(1, int(self._tile_w * (1.0 - self._overlap)))
        rows = np.arange(0, max(1, h - self._tile_h + 1), step_y, dtype=np.int32)
        cols = np.arange(0, max(1, w - self._tile_w + 1), step_x, dtype=np.int32)
        if h > self._tile_h and (rows.size == 0 or rows[-1] != h - self._tile_h):
            rows = np.append(rows, h - self._tile_h)
        if w > self._tile_w and (cols.size == 0 or cols[-1] != w - self._tile_w):
            cols = np.append(cols, w - self._tile_w)

        self._reference = self._aot.upload(reference)
        self._rows = self._aot.upload(np.ascontiguousarray(np.unique(rows), dtype=np.int32))
        self._cols = self._aot.upload(np.ascontiguousarray(np.unique(cols), dtype=np.int32))
        self._weight = self._engine.allocate(self._shape, dtype=np.float32, host_accessible=True)

    def generate(self, current: np.ndarray, flow: np.ndarray | None = None) -> np.ndarray:
        """Return a finite ``float32`` confidence map in ``[0, 1]``.

        ``flow`` is the LR displacement used to compare the source at aligned
        coordinates.  Splatting still receives the original source and flow;
        only the confidence analysis uses the warped view.
        """
        if self._closed:
            raise RuntimeError("SpatialWeightMapGenerator is already closed")
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.similarity_taichi.compute_spatial import (
            generate_spatial_weights_taichi,
        )

        current = np.ascontiguousarray(current, dtype=np.float32)
        if tuple(current.shape) != self._shape:
            raise ValueError(f"current shape {current.shape} != reference shape {self._shape}")

        analysis = current
        if flow is not None:
            flow = np.ascontiguousarray(flow, dtype=np.float32)
            if flow.shape != (*self._shape, 2):
                raise ValueError(f"flow shape {flow.shape} is not HxWx2")
            active_arch = str(getattr(self._engine, "arch", "")).lower()
            if active_arch == "cpu":
                # CPU TCM caches may be absent or stale after a runtime
                # rebuild.  Keep this recovery explicit and deterministic.
                analysis = _numpy_remap_with_flow(current, flow)
            else:
                analysis = self._aot.remap_with_flow(
                    current, flow, self._shape[0], self._shape[1], return_gpu=False
                )
                analysis = np.asarray(analysis, dtype=np.float32)
                if analysis.ndim != 2:
                    raise RuntimeError(
                        f"remap_with_flow returned unexpected luminance shape {analysis.shape}"
                    )

        current_gpu = self._aot.upload(np.ascontiguousarray(analysis, dtype=np.float32))
        try:
            generate_spatial_weights_taichi(
                current_image=current_gpu,
                reference_image=self._reference,
                weight_map_sum=self._weight,
                base_window=None,
                stability_map=None,
                row_starts=self._rows,
                col_starts=self._cols,
                tile_h=self._tile_h,
                tile_w=self._tile_w,
                noise_sigma=self._noise_sigma,
                motion_sensitivity=self._motion_sensitivity,
                noise_offset_factor=self._noise_offset_factor,
                equalize_brightness=False,
                buffer_provider="pool",
                scratch_cache=self._scratch,
                early_exit_threshold=self._early_exit_threshold,
            )
            result = np.asarray(self._weight.to_numpy(), dtype=np.float32)
        except Exception as exc:
            active_arch = str(getattr(self._engine, "arch", "")).lower()
            if active_arch != "cpu":
                raise
            print(
                "[SpatialWeight] CPU spatial TCM unavailable; using explicit "
                f"NumPy oracle recovery: {exc}"
            )
            result = _numpy_spatial_weight(
                self._reference_host,
                np.asarray(analysis, dtype=np.float32),
                self._noise_sigma,
            )
        finally:
            current_gpu.destroy()

        result = np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=0.0)
        # SpatialFusion's overlap accumulation can exceed one.  Splatting
        # needs a confidence, not an accumulation count, so normalize only
        # this per-frame map and never divide the SR accumulator here.
        peak = float(np.max(result)) if result.size else 0.0
        if peak > 1.0:
            result = result / np.float32(peak)
        return np.ascontiguousarray(np.clip(result, 0.0, 1.0), dtype=np.float32)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._scratch.clear()
        for name in ("_weight", "_rows", "_cols", "_reference"):
            buf = getattr(self, name, None)
            if buf is not None:
                try:
                    buf.destroy()
                except Exception:
                    pass
                setattr(self, name, None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def generate_spatial_weight_map_blockwise(
    reference: np.ndarray,
    current: np.ndarray,
    flow: np.ndarray | None,
    *,
    block_size: int,
    halo: int = 32,
    **kwargs,
) -> np.ndarray:
    """Generate a full-resolution map while keeping AOT residency bounded."""
    reference = np.asarray(reference, dtype=np.float32)
    current = np.asarray(current, dtype=np.float32)
    if reference.ndim != 2 or current.shape != reference.shape:
        raise ValueError("reference/current must be matching 2-D luminance arrays")
    if flow is not None and np.asarray(flow).shape != (*reference.shape, 2):
        raise ValueError("flow must have shape HxWx2")

    h, w = reference.shape
    block_size = max(64, int(block_size))
    halo = max(0, int(halo))
    output = np.zeros((h, w), dtype=np.float32)
    for y0 in range(0, h, block_size):
        for x0 in range(0, w, block_size):
            y1, x1 = min(h, y0 + block_size), min(w, x0 + block_size)
            cy0, cx0 = max(0, y0 - halo), max(0, x0 - halo)
            cy1, cx1 = min(h, y1 + halo), min(w, x1 + halo)
            local_flow = None if flow is None else flow[cy0:cy1, cx0:cx1]
            with SpatialWeightMapGenerator(
                reference[cy0:cy1, cx0:cx1], **kwargs
            ) as generator:
                local = generator.generate(
                    current[cy0:cy1, cx0:cx1], local_flow
                )
            output[y0:y1, x0:x1] = local[y0 - cy0:y1 - cy0, x0 - cx0:x1 - cx0]
    return output
