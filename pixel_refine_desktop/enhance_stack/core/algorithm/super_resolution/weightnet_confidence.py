"""WeightNet confidence adapter for optical super-resolution experiments.

WeightNet is a reliability model, not an HR reconstructor.  This adapter keeps
that boundary explicit: callers provide a reference and an already aligned
support frame, and receive one LR confidence map to use in splatting or in the
residual back-projection stage.
"""

from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np


class WeightNetConfidenceProvider:
    """Run the existing FusionNet WeightNet and return luma confidence."""

    def __init__(
        self,
        *,
        model_path: str | Path,
        runtime: str = "auto",
        tile_size: int = 256,
        work_scale: float = 0.5,
        overlap: float = 0.30,
        ghost_penalty: float = 1.0,
        ghost_cutoff: float = 0.05,
        chroma_sensitivity: float = 1.0,
    ):
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
            load_weightnet_onnx,
        )

        self.model_path = Path(model_path)
        self.runtime = str(runtime).strip().lower()
        self.tile_size = max(256, int(tile_size))
        self.work_scale = float(np.clip(work_scale, 1.0e-3, 1.0))
        try:
            self.reference_cache_tiles = max(
                0,
                int(os.environ.get("SPLATSR_WEIGHTNET_REFERENCE_CACHE_TILES", "16")),
            )
        except (TypeError, ValueError):
            self.reference_cache_tiles = 16
        self.overlap = float(np.clip(overlap, 0.0, 0.95))
        self.ghost_penalty = float(ghost_penalty)
        self.ghost_cutoff = float(ghost_cutoff)
        self.chroma_sensitivity = float(chroma_sensitivity)
        self.session = load_weightnet_onnx(
            self.model_path,
            runtime=self.runtime,
            patch_size=self.tile_size,
        )
        setattr(
            self.session,
            "reference_cache_tiles",
            self.reference_cache_tiles,
        )
        self.last_alpha = 0.0
        self._cached_reference_key = None
        self._cached_reference_work = None

    @staticmethod
    def _as_rgb_hwc(image: np.ndarray, name: str) -> np.ndarray:
        arr = np.asarray(image, dtype=np.float32)
        if arr.ndim != 3 or arr.shape[-1] != 3:
            raise ValueError(f"{name} must have shape (H,W,3), got {arr.shape}")
        if not np.isfinite(arr).all():
            raise ValueError(f"{name} contains NaN or infinity")
        arr = np.ascontiguousarray(arr, dtype=np.float32)
        # Most callers already provide normalized float32 data. Avoid making a
        # full-resolution clip copy on every WeightNet tile request; preserve
        # the old behavior only for genuinely out-of-range inputs.
        if np.any(arr < 0.0) or np.any(arr > 1.0):
            arr = np.clip(arr, 0.0, 1.0).astype(np.float32, copy=False)
        return arr

    @staticmethod
    def _resize_work(image: np.ndarray, work_h: int, work_w: int) -> np.ndarray:
        if image.shape[:2] == (work_h, work_w):
            return image
        return np.ascontiguousarray(
            cv2.resize(image, (work_w, work_h), interpolation=cv2.INTER_AREA),
            dtype=np.float32,
        )

    def __call__(
        self,
        reference_rgb: np.ndarray,
        aligned_support_rgb: np.ndarray,
    ) -> np.ndarray:
        reference = self._as_rgb_hwc(reference_rgb, "reference_rgb")
        support = self._as_rgb_hwc(aligned_support_rgb, "aligned_support_rgb")
        if support.shape != reference.shape:
            raise ValueError(
                f"aligned_support_rgb shape {support.shape} != reference shape {reference.shape}"
            )

        full_h, full_w = reference.shape[:2]
        work_h = max(1, int(round(full_h * self.work_scale)))
        work_w = max(1, int(round(full_w * self.work_scale)))
        support_work = self._resize_work(support, work_h, work_w)
        return self._infer_work_confidence(
            reference,
            support_work,
            full_h=full_h,
            full_w=full_w,
            work_h=work_h,
            work_w=work_w,
        )

    def infer_aligned_support_with_flow(
        self,
        reference_rgb: np.ndarray,
        support_rgb: np.ndarray,
        flow: np.ndarray,
    ) -> np.ndarray:
        """Infer confidence after warping support directly at work resolution.

        Splatting already has the LK flow.  Warping the full-resolution RGB
        support only to downsample it again for WeightNet wastes CPU time and
        creates large temporary arrays.  This method performs the equivalent
        warp after downsampling, preserving the model's work-resolution input
        while avoiding the 12MP host-side RGB remap.
        """
        reference = self._as_rgb_hwc(reference_rgb, "reference_rgb")
        support = self._as_rgb_hwc(support_rgb, "support_rgb")
        if support.shape != reference.shape:
            raise ValueError(
                f"support_rgb shape {support.shape} != reference shape {reference.shape}"
            )
        flow = np.asarray(flow, dtype=np.float32)
        full_h, full_w = reference.shape[:2]
        if flow.shape != (full_h, full_w, 2):
            raise ValueError(
                f"flow shape {flow.shape} != expected {(full_h, full_w, 2)}"
            )
        if not np.isfinite(flow).all():
            raise ValueError("flow contains NaN or infinity")

        work_h = max(1, int(round(full_h * self.work_scale)))
        work_w = max(1, int(round(full_w * self.work_scale)))
        support_work = self._resize_work(support, work_h, work_w)
        flow_work = np.empty((work_h, work_w, 2), dtype=np.float32)
        flow_work[..., 0] = cv2.resize(
            flow[..., 0], (work_w, work_h), interpolation=cv2.INTER_LINEAR
        ) * np.float32(work_w / max(1, full_w))
        flow_work[..., 1] = cv2.resize(
            flow[..., 1], (work_w, work_h), interpolation=cv2.INTER_LINEAR
        ) * np.float32(work_h / max(1, full_h))

        x_coords = np.arange(work_w, dtype=np.float32)[None, :]
        y_coords = np.arange(work_h, dtype=np.float32)[:, None]
        map_x = np.empty((work_h, work_w), dtype=np.float32)
        map_y = np.empty((work_h, work_w), dtype=np.float32)
        np.add(x_coords, flow_work[..., 0], out=map_x)
        np.add(y_coords, flow_work[..., 1], out=map_y)
        aligned_work = np.empty_like(support_work, dtype=np.float32)
        for channel in range(3):
            aligned_work[..., channel] = cv2.remap(
                support_work[..., channel],
                map_x,
                map_y,
                cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT101,
            )
        return self._infer_work_confidence(
            reference,
            np.ascontiguousarray(aligned_work, dtype=np.float32),
            full_h=full_h,
            full_w=full_w,
            work_h=work_h,
            work_w=work_w,
        )

    def _infer_work_confidence(
        self,
        reference: np.ndarray,
        support_work_hwc: np.ndarray,
        *,
        full_h: int,
        full_w: int,
        work_h: int,
        work_w: int,
    ) -> np.ndarray:
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
            infer_single_support_weight_map,
        )

        support_work = self._as_rgb_hwc(support_work_hwc, "support_work_hwc")
        if support_work.shape[:2] != (work_h, work_w):
            raise ValueError(
                f"support_work_hwc shape {support_work.shape} != expected {(work_h, work_w, 3)}"
            )

        cache_key = (id(reference), reference.shape, work_h, work_w)
        if self._cached_reference_key != cache_key:
            self._cached_reference_work = self._resize_work(
                reference, work_h, work_w
            )
            self._cached_reference_key = cache_key
        ref_work = self._cached_reference_work.transpose(2, 0, 1)
        support_work = support_work.transpose(2, 0, 1)

        weight_map, self.last_alpha = infer_single_support_weight_map(
            self.session,
            np.ascontiguousarray(ref_work, dtype=np.float32),
            np.ascontiguousarray(support_work, dtype=np.float32),
            tile_size=self.tile_size,
            overlap=self.overlap,
            ghost_penalty=self.ghost_penalty,
            ghost_cutoff=self.ghost_cutoff,
            chroma_sensitivity=self.chroma_sensitivity,
        )
        weight_map = np.asarray(weight_map, dtype=np.float32)
        if weight_map.shape != (3, work_h, work_w):
            raise RuntimeError(
                f"WeightNet returned unexpected map shape {weight_map.shape}; "
                f"expected {(3, work_h, work_w)}"
            )
        confidence = np.clip(
            0.299 * weight_map[0]
            + 0.587 * weight_map[1]
            + 0.114 * weight_map[2],
            0.0,
            1.0,
        ).astype(np.float32)
        if confidence.shape != (full_h, full_w):
            confidence = cv2.resize(
                confidence,
                (full_w, full_h),
                interpolation=cv2.INTER_LINEAR,
            )
        return np.ascontiguousarray(np.clip(confidence, 0.0, 1.0), dtype=np.float32)

    @property
    def providers(self) -> list[str]:
        providers = getattr(self.session, "get_providers", lambda: [])()
        return list(providers)


__all__ = ["WeightNetConfidenceProvider"]
