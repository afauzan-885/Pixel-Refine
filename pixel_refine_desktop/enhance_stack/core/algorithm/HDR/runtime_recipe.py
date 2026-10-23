"""PipelineRuntime source and recipe for streaming HDR fusion."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import count
from typing import Callable

import numpy as np

from .hdr_fusion import (
    WeightedHDRFusion,
    estimate_noise_taichi,
    rgb_to_gray,
    srgb_to_linear,
)
from .HDR import HDRMaskAlgorithm
from .spde_mr import SPDEMRAlgorithm


class HDRPathSource:
    """Load the selected reference and one support image on demand."""

    def __init__(self, reference_rgb: np.ndarray, support_paths: list[str]):
        self.reference_rgb = reference_rgb
        self.support_paths = tuple(support_paths)

    def load_reference(self) -> np.ndarray:
        return self.reference_rgb

    def load_support(self, index: int) -> np.ndarray:
        from .streaming_pipeline import _load_rgb

        return _load_rgb(self.support_paths[index])


class HDRArraySource:
    """Adapt an already-aligned one-shot frame iterable to PipelineRuntime."""

    def __init__(self, frames):
        self._frames = iter(frames)

    def load_reference(self):
        try:
            return np.ascontiguousarray(next(self._frames), dtype=np.float32)
        except StopIteration as exc:
            raise ValueError("HDR fusion requires at least one frame") from exc

    def support_indices(self):
        return count()

    def load_support(self, _index):
        return np.ascontiguousarray(next(self._frames), dtype=np.float32)


@dataclass
class HDRFusionState:
    reference_rgb: np.ndarray
    fusion: object
    support_paths: tuple[str, ...] | None
    path_to_index: dict[str, int] | None
    processed: int = 0


def _alignment_validity(shape: tuple[int, int], dx: int, dy: int) -> np.ndarray:
    height, width = shape
    mask = np.zeros((height, width), dtype=bool)
    x0, x1 = max(0, -dx), min(width, width - dx)
    y0, y1 = max(0, -dy), min(height, height - dy)
    if x1 > x0 and y1 > y0:
        mask[y0:y1, x0:x1] = True
    return mask


class HDRFusionRecipe:
    """Apply MTB alignment and domain fusion to ordered support frames."""

    def __init__(
        self,
        *,
        analyses,
        selected_index: int,
        support_paths: list[str] | None,
        effective_exposures: list[float] | None,
        is_spde_mr: bool,
        is_hdr_mask: bool = False,
        radiance_enabled: bool = False,
        progress_callback: Callable | None = None,
        align_support: bool = True,
        cancel_callback: Callable | None = None,
        include_radiance: bool = True,
    ):
        self.selected_index = int(selected_index)
        self.support_paths = tuple(support_paths) if support_paths is not None else None
        self.effective_exposures = list(effective_exposures or ())
        self.radiance_enabled = bool(radiance_enabled)
        self.is_spde_mr = bool(is_spde_mr)
        self.is_hdr_mask = bool(is_hdr_mask)
        self.progress_callback = progress_callback
        self.align_support = bool(align_support)
        self.cancel_callback = cancel_callback
        self.include_radiance = bool(include_radiance)
        self.selected_exposure = (
            self.effective_exposures[self.selected_index]
            if self.radiance_enabled
            else None
        )
        self.path_to_index = (
            {analysis.path: index for index, analysis in enumerate(analyses)}
            if analyses is not None
            else None
        )

    def _check_cancelled(self, context) -> None:
        context.check_cancelled()
        if self.cancel_callback is not None:
            self.cancel_callback()

    def prepare_reference(self, reference_rgb, context) -> HDRFusionState:
        self._check_cancelled(context)
        if self.is_hdr_mask:
            fusion = HDRMaskAlgorithm().create_fusion(
                reference_rgb, radiance_enabled=self.radiance_enabled
            )
        elif self.is_spde_mr:
            fusion = SPDEMRAlgorithm().create_fusion(
                reference_rgb, radiance_enabled=self.radiance_enabled
            )
        else:
            fusion = WeightedHDRFusion(
                reference_rgb.shape, radiance_enabled=self.radiance_enabled
            )

        self._add_frame(
            fusion,
            reference_rgb,
            context,
            index=self.selected_index,
            is_reference=True,
        )
        return HDRFusionState(
            reference_rgb=reference_rgb,
            fusion=fusion,
            support_paths=self.support_paths,
            path_to_index=self.path_to_index,
        )

    def _add_frame(
        self,
        fusion,
        rgb,
        context,
        *,
        index: int,
        is_reference: bool = False,
        valid_mask=None,
    ) -> None:
        if self.is_hdr_mask:
            exposure_scale = 1.0
            if self.radiance_enabled:
                exposure_scale = (
                    self.effective_exposures[index] / self.selected_exposure
                )
            fusion.add_frame(
                rgb,
                exposure_scale=exposure_scale,
                valid_mask=valid_mask,
            )
            return

        gray = rgb_to_gray(rgb)
        noise_sigma = estimate_noise_taichi(gray, context.session)
        radiance_rgb = None
        if self.radiance_enabled:
            source_exposure = self.effective_exposures[index]
            radiance_rgb = srgb_to_linear(rgb) * np.float32(
                self.selected_exposure / source_exposure
            )
        if self.is_spde_mr:
            fusion.add_spde_frame(
                rgb,
                noise_sigma=noise_sigma,
                valid_mask=valid_mask,
                radiance_rgb=radiance_rgb,
                is_reference=is_reference,
            )
        else:
            fusion.add_frame(
                rgb,
                noise_sigma=noise_sigma,
                valid_mask=valid_mask,
                radiance_rgb=radiance_rgb,
            )

    def _align_support(self, index, support_rgb, state):
        """Align one support and return its valid region and source index."""
        valid = None
        source_index = index + 1
        if not self.align_support:
            return support_rgb, valid, source_index

        from taichi_vision.taichi_algorithm.aot_api import align_mtb, warp_affine_aot

        support_path = state.support_paths[index]
        if support_rgb.shape != state.reference_rgb.shape:
            raise ValueError(
                f"HDR frame shape changed during processing: {support_path}"
            )
        dx, dy = align_mtb(
            np.ascontiguousarray(state.reference_rgb * 255.0, dtype=np.float32),
            np.ascontiguousarray(support_rgb * 255.0, dtype=np.float32),
        )
        height, width = state.reference_rgb.shape[:2]
        support_rgb = warp_affine_aot(
            support_rgb,
            np.asarray([[1.0, 0.0, -dx], [0.0, 1.0, -dy]], dtype=np.float32),
            (width, height),
        )
        valid = _alignment_validity((height, width), int(dx), int(dy))
        source_index = state.path_to_index[support_path]
        return support_rgb, valid, source_index

    def _report_support_progress(self, state):
        if self.progress_callback is None:
            return
        total = len(state.support_paths)
        self.progress_callback(
            20 + int(70 * state.processed / max(total, 1)),
            f"HDR MTB alignment dan fusion {state.processed}/{total}",
        )

    def process_support(self, index, support_rgb, state, context) -> None:
        self._check_cancelled(context)
        support_rgb, valid, source_index = self._align_support(
            index, support_rgb, state
        )
        self._add_frame(
            state.fusion,
            support_rgb,
            context,
            index=source_index,
            valid_mask=valid,
        )
        state.processed += 1
        self._report_support_progress(state)

    def finalize(self, state: HDRFusionState, context):
        context.check_cancelled()
        result = state.fusion.finalize(state.reference_rgb)
        return result if self.include_radiance else result[0]


__all__ = ["HDRArraySource", "HDRFusionRecipe", "HDRPathSource"]
