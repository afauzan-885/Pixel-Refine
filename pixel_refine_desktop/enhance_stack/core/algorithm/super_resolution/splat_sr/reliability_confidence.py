"""Spatial-reliability confidence provider for the splat SR reconstruction.

This is the consumer half of the split contract:

* ``compute_spatial`` / ``generate_reliability_weights_4passes`` only *evaluates*
  how trustworthy each source sample is.
* The splat reconstruction only *uses* that map to decide which samples are
  accumulated and by how much.

The provider is a drop-in for the WeightNet slot in ``SplatSR``: it accepts a
reference and an already aligned support frame as RGB and returns one LR luma
confidence map in ``[0, 1]``.

Unlike the denoising path, the returned map is the *normalized window average*
of the fine-analysis confidence rather than a Hann-weighted accumulation count.
That matters because the reconstruction consumes it directly as a per-sample
weight instead of dividing by it at the end, so a map whose scale depends on the
tile overlap would modulate the result.
"""

from __future__ import annotations

import os

import cv2
import numpy as np


def _gray(image: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(image, dtype=np.float32)
    if arr.ndim == 3:
        if arr.shape[2] == 1:
            arr = arr[..., 0]
        elif arr.shape[2] >= 3:
            arr = cv2.cvtColor(arr[..., :3], cv2.COLOR_RGB2GRAY)
        else:
            raise ValueError(f"{name} has an unsupported channel count {arr.shape[2]}")
    elif arr.ndim != 2:
        raise ValueError(f"{name} must be HxW or HxWxC, got {arr.shape}")
    if not np.isfinite(arr).all():
        raise ValueError(f"{name} contains NaN or infinity")
    return np.ascontiguousarray(arr, dtype=np.float32)


class ReliabilityConfidenceProvider:
    """Per-sample reliability from taichi_vision's spatial analysis graphs.

    ``motion_sensitivity`` is deliberately explicit.  The SpatialFusion default
    (150.0) is tuned to reject ghosts aggressively for denoising; feeding it to
    the reconstruction unchanged drives the reliability to zero almost
    everywhere, which removes the resolution gain instead of protecting it.
    """

    def __init__(
        self,
        *,
        tile_size: int = 16,
        overlap: float = 0.35,
        motion_sensitivity: float | None = None,
        noise_offset_factor: float = 0.15,
        noise_sigma: float | None = None,
        ghost_penalty: float = 1.0,
        ghost_cutoff: float = 0.0,
        early_exit_threshold: float = 0.0,
        equalize_brightness: bool = False,
        session=None,
    ):
        self.tile_size = max(4, int(tile_size))
        self.overlap = float(np.clip(overlap, 0.0, 0.9))
        # Lower than the denoiser default on purpose: the reconstruction wants a
        # smooth reliability field, and a hard 150.0 rejects far beyond the
        # mismatching region.
        self.motion_sensitivity = float(
            motion_sensitivity
            if motion_sensitivity is not None
            else float(os.environ.get("SPLATSR_RELIABILITY_MOTION", "8.0"))
        )
        self.noise_offset_factor = float(noise_offset_factor)
        self.noise_sigma = None if noise_sigma in (None, 0.0) else float(noise_sigma)
        self.ghost_penalty = float(ghost_penalty)
        # A hard cutoff would turn near-zero weights into exact zeros, and an
        # exact zero weight becomes a reconstruction hole that falls back to the
        # reference.  Keep it off unless a caller explicitly asks for it.
        self.ghost_cutoff = float(ghost_cutoff)
        # The coarse guidance gate is disabled by default.  It is evaluated on a
        # 1/4-resolution map, so a burst with a large moving region can drive the
        # coarse confidence to zero and reject the *whole* frame, which would
        # remove the reconstruction gain instead of protecting it.  The guidance
        # value still multiplies the fine confidence, so it keeps shaping the map.
        self.early_exit_threshold = float(early_exit_threshold)
        self.equalize_brightness = bool(equalize_brightness)
        self._session = session

        self._rows = None
        self._cols = None
        self._rows_gpu = None
        self._cols_gpu = None
        self._shape = None
        self._scratch = None
        self._out = None
        self._postprocess_out = None
        self._work = None
        self._reference = None
        self._reference_host = None
        self._reference_input = None
        self.last_mean_reliability = 0.0

    # -- helpers ---------------------------------------------------------
    def _ensure_buffers(self, shape: tuple[int, int], session=None):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import SpatialScratchCache
        from taichi_vision.taichi_algorithm.spatial_fusion.compute_spatial import (
            _compute_tile_starts,
        )

        if self._shape == shape and self._session is session:
            return
        self._release()
        h, w = int(shape[0]), int(shape[1])
        self._rows = np.asarray(
            _compute_tile_starts(h, self.tile_size, overlap=self.overlap),
            dtype=np.int32,
        )
        self._cols = np.asarray(
            _compute_tile_starts(w, self.tile_size, overlap=self.overlap),
            dtype=np.int32,
        )
        engine = taichi_aot.engine
        self._scratch = SpatialScratchCache()
        self._session = session
        if session is None:
            self._out = engine.allocate(
                (h, w), dtype=np.float32, host_accessible=True
            )
            self._rows_gpu = taichi_aot.upload(self._rows)
            self._cols_gpu = taichi_aot.upload(self._cols)
        else:
            self._out = session.acquire_buffer(
                (h, w), dtype=np.float32, tag="splat_sr.reliability.output"
            )
            self._rows_gpu, _ = session.upload_if_needed(self._rows)
            self._cols_gpu, _ = session.upload_if_needed(self._cols)
            session.own(self._scratch, releaser=lambda scratch: scratch.clear())
        self._shape = shape

    def _release(self):
        session = self._session
        for name in (
            "_out",
            "_postprocess_out",
            "_work",
            "_reference",
            "_rows_gpu",
            "_cols_gpu",
        ):
            buf = getattr(self, name, None)
            if buf is not None and session is None:
                try:
                    buf.destroy()
                except Exception:
                    pass
            setattr(self, name, None)
        if self._scratch is not None and session is None:
            try:
                self._scratch.clear()
            except Exception:
                pass
        self._scratch = None
        self._reference_host = None
        self._reference_input = None
        self._shape = None

    def prepare_reference(self, reference_rgb: np.ndarray, *, session=None):
        """Upload and cache one reference analysis plane for a whole SR job."""
        from taichi_vision import taichi_aot

        session = self._session if session is None else session
        reference = _gray(reference_rgb, "reference_rgb")
        shape = (int(reference.shape[0]), int(reference.shape[1]))
        if (
            self._shape == shape
            and self._session is session
            and self._reference_input is reference_rgb
        ):
            return self._reference
        self._release()
        self._ensure_buffers(shape, session=session)
        self._reference_host = reference
        self._reference_input = reference_rgb
        if session is None:
            self._reference = taichi_aot.upload(reference)
        else:
            self._reference, _ = session.upload_if_needed(reference)
        return self._reference

    # -- public API ------------------------------------------------------
    def close(self) -> None:
        self._release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False

    def __call__(
        self,
        reference_rgb: np.ndarray,
        aligned_support_rgb: np.ndarray,
    ) -> np.ndarray:
        """Return the LR luma reliability of one aligned support frame."""
        return self._generate(
            reference_rgb, aligned_support_rgb, return_device=False
        )

    def generate_device(
        self,
        reference_rgb: np.ndarray,
        aligned_support_rgb: np.ndarray,
        *,
        session=None,
    ):
        """Return the reusable native weight buffer without host readback.

        The returned buffer is owned by the supplied per-job ``BufferSession``
        and is valid until the next generated support map or session close.
        """
        session = self._session if session is None else session
        if session is None:
            raise ValueError("generate_device requires a BufferSession")
        if self._session is not session:
            self._session = session
        return self._generate(
            reference_rgb,
            aligned_support_rgb,
            return_device=True,
            session=session,
        )

    def _generate(
        self,
        reference_rgb: np.ndarray,
        aligned_support_rgb: np.ndarray,
        *,
        return_device: bool,
        session=None,
    ):
        from taichi_vision import taichi_aot
        from taichi_vision.taichi_algorithm.spatial_fusion import (
            generate_spatial_weights_taichi,
        )

        current = _gray(aligned_support_rgb, "aligned_support_rgb")
        reference_gpu = self.prepare_reference(reference_rgb, session=session)
        if current.shape != self._shape:
            raise ValueError(
                f"aligned_support_rgb shape {current.shape} != reference shape "
                f"{self._shape}"
            )

        engine = taichi_aot.engine
        noise_sigma = (
            float(self.noise_sigma)
            if self.noise_sigma is not None
            else 0.02  # conservative default when no reference estimate is given
        )
        current_gpu = None
        owns_current = False
        result_buffer = self._out
        try:
            if session is None:
                current_gpu = taichi_aot.upload(current)
                owns_current = True
            else:
                current_gpu, owns_current = session.upload_if_needed(current)
            generate_spatial_weights_taichi(
                current_image=current_gpu,
                reference_image=reference_gpu,
                weight_map_sum=self._out,
                base_window=0,
                stability_map=None,
                row_starts=self._rows_gpu,
                col_starts=self._cols_gpu,
                tile_h=self.tile_size,
                tile_w=self.tile_size,
                noise_sigma=noise_sigma,
                motion_sensitivity=self.motion_sensitivity,
                noise_offset_factor=self.noise_offset_factor,
                equalize_brightness=self.equalize_brightness,
                buffer_provider=None,
                scratch_cache=self._scratch,
                early_exit_threshold=self.early_exit_threshold,
                reliability_mode=True,
            )
            result_buffer = self._out
            if self.ghost_penalty != 1.0 or self.ghost_cutoff > 0.0:
                from taichi_vision.taichi_algorithm.spatial_fusion import (
                    postprocess_spatial_weight_taichi,
                )

                result_buffer = postprocess_spatial_weight_taichi(
                    self._out,
                    ghost_penalty=self.ghost_penalty,
                    ghost_cutoff=self.ghost_cutoff,
                    dst=(
                        self._postprocess_out
                        if self._postprocess_out is not None
                        else None
                    ),
                )
                if session is not None and result_buffer is not self._out:
                    self._postprocess_out = session.own(result_buffer)
                elif session is None:
                    self._postprocess_out = None
            # Keep both graphs ordered on the same runtime stream. BufferSession
            # retires the support upload without reusing its handle while work
            # is in flight, so this GPU-resident handoff needs no host fence.
            if return_device:
                self.last_mean_reliability = 0.0
                return result_buffer
            result = np.asarray(result_buffer.to_numpy(), dtype=np.float32)
        finally:
            if current_gpu is not None:
                if session is not None:
                    if owns_current:
                        session.release_upload(current)
                else:
                    try:
                        current_gpu.destroy()
                    except Exception:
                        pass
            if session is None and result_buffer is not self._out:
                try:
                    result_buffer.destroy()
                except Exception:
                    pass

        result = np.nan_to_num(result, nan=0.0, posinf=1.0, neginf=0.0)
        result = np.clip(result, 0.0, 1.0).astype(np.float32, copy=False)
        self.last_mean_reliability = float(result.mean())
        return np.ascontiguousarray(result, dtype=np.float32)


__all__ = ["ReliabilityConfidenceProvider"]
