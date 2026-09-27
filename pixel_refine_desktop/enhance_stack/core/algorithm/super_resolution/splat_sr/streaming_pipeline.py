"""Splat SR domain recipe for the shared frame-streaming runtime."""

from __future__ import annotations

import os
import shutil
import tempfile
import threading
from dataclasses import dataclass
import cv2
import numpy as np


class ImagePathSource:
    """Decode one linear-RGB image only when the runtime requests it."""

    def __init__(self, paths):
        if isinstance(paths, (str, os.PathLike)):
            paths = (paths,)
        self.paths = tuple(os.fspath(path) for path in paths)
        if not self.paths:
            raise ValueError("Splat SR requires at least one input image")
        self._shape = None
        self.compute_gate = threading.RLock()

    def _load(self, index: int):
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.fusionet_engine.weightnet_inference import (
            load_rgb_linear_image,
        )

        # RAW development may dispatch Taichi work. Share a per-job gate with
        # the recipe so host prefetch never overlaps another device support.
        with self.compute_gate:
            image = np.asarray(
                load_rgb_linear_image(self.paths[index]), dtype=np.float32
            )
            if self._shape is not None and image.shape[:2] != self._shape:
                from taichi_vision import taichi_aot

                target_h, target_w = self._shape
                image = taichi_aot.resize(
                    image,
                    (target_w, target_h),
                    interpolation=taichi_aot.INTER_LINEAR,
                )
                image = np.ascontiguousarray(image, dtype=np.float32)
        if image.ndim == 2:
            image = np.repeat(image[..., None], 3, axis=2)
        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError(
                f"Splat SR expects linear RGB input, got {image.shape} from {self.paths[index]}"
            )
        image = np.ascontiguousarray(image, dtype=np.float32)
        if self._shape is None:
            self._shape = tuple(int(value) for value in image.shape[:2])
        return image

    def load_reference(self):
        return self._load(0)

    def load_support(self, index: int):
        return self._load(int(index))


class _RefinementBacking:
    """Temporary disk-backed frames/flows/confidence used only by refinement."""

    def __init__(self, count: int, height: int, width: int):
        self._directory = tempfile.TemporaryDirectory(prefix="pixelrefine_splat_sr_")
        self._closed = False
        self._maps = []
        self.required_bytes = int(count * height * width * 4 * 4)
        free_bytes = shutil.disk_usage(self._directory.name).free
        if free_bytes < self.required_bytes + 64 * 1024 * 1024:
            self._directory.cleanup()
            raise OSError(
                "Splat SR optical refinement needs approximately "
                f"{self.required_bytes / (1024**3):.2f} GiB of temporary disk space; "
                f"only {free_bytes / (1024**3):.2f} GiB is available"
            )
        try:
            self.frames = self._create("frames.f32", (count, height, width))
            self.flows = self._create("flows.f32", (count, height, width, 2))
            self.confidence = self._create(
                "confidence.f32", (count, height, width)
            )
        except Exception:
            self.close()
            raise

    def _create(self, filename, shape):
        result = np.memmap(
            os.path.join(self._directory.name, filename),
            mode="w+",
            dtype=np.float32,
            shape=shape,
        )
        self._maps.append(result)
        return result

    def close(self):
        if self._closed:
            return
        self._closed = True
        for mapping in reversed(self._maps):
            try:
                mapping.flush()
            except Exception:
                pass
            try:
                mapping._mmap.close()
            except Exception:
                pass
        self._maps.clear()
        self._directory.cleanup()


@dataclass
class _ReferenceState:
    reference_rgb: np.ndarray
    reference_gray: np.ndarray
    reference_carrier_gray: np.ndarray | None
    analysis_params: dict
    analysis_reference_rgb: np.ndarray | None
    accumulator: object
    provider: object
    algorithm: object
    use_farneback: bool
    farneback_config: dict
    matcher: object
    bm_config: dict | None
    flow_proxy_scale: float
    exposure_normalization: bool
    refinement: _RefinementBacking | None
    count: int
    processed: int = 0


class SplatSRRecipe:
    """Alignment → confidence → one-frame Hann splat, under one BufferSession."""

    def __init__(
        self,
        paths,
        *,
        scale=2,
        weight_source="compute_spatial",
        alignment_method="farneback",
        reliability_provider=None,
        block_size=1024,
        block_overlap=0.25,
        refinement_iterations=0,
        refinement_step=0.1,
        refinement_regularization=0.1,
        exposure_normalization=True,
    ):
        if isinstance(paths, (str, os.PathLike)):
            paths = (paths,)
        self.paths = tuple(os.fspath(path) for path in paths)
        self.scale = int(scale)
        self.weight_source = str(weight_source or "compute_spatial").strip().lower()
        self.alignment_method = str(alignment_method or "farneback").strip().lower()
        self.reliability_provider = reliability_provider
        self.block_size = max(64, int(block_size))
        self.block_overlap = float(np.clip(block_overlap, 0.0, 0.9))
        self.refinement_iterations = max(0, int(refinement_iterations))
        self.refinement_step = float(refinement_step)
        self.refinement_regularization = float(refinement_regularization)
        self.exposure_normalization = bool(exposure_normalization)
        self.compute_gate = threading.RLock()

    @staticmethod
    def _report(context, progress, message):
        context.report(int(progress), str(message))

    def _configure_alignment(self, height, width):
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.farneback_flow import (
            FarnebackFlow,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import (
            _BLOCK_MATCHING_ALIGNMENT_ALIASES,
            _DEFAULT_FARNEBACK_PRESET,
            _FARNEBACK_ALIGNMENT_ALIASES,
            SplatSRAlgorithm,
        )

        requested = self.alignment_method
        use_farneback = requested in _FARNEBACK_ALIGNMENT_ALIASES
        if not use_farneback and requested not in _BLOCK_MATCHING_ALIGNMENT_ALIASES:
            raise ValueError(
                "Splat SR supports Taichi Vision Farneback or native block matching; "
                f"got {requested!r}"
            )
        preset = os.environ.get(
            "SPLATSR_FARNEBACK_PRESET", _DEFAULT_FARNEBACK_PRESET
        ).strip().lower()
        if preset not in FarnebackFlow.PRESETS:
            preset = _DEFAULT_FARNEBACK_PRESET
        farneback_config = dict(FarnebackFlow.PRESETS[preset])
        matcher = None
        bm_config = None
        if not use_farneback:
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.block_matching import (
                BlockMatching,
            )

            matcher = BlockMatching()
            bm_config = dict(matcher.load_config())
            bm_config.update(
                grid_step=max(64, int(bm_config.get("grid_step", 48))),
                max_level=0,
                iterations=1,
                motion_mode="fast",
                adaptive=False,
                strict=True,
            )

        frame_mp = (height * width) / 1.0e6
        flow_proxy_max = max(
            128,
            int(
                os.environ.get(
                    "SPLATSR_FLOW_PROXY_MAX",
                    "768" if use_farneback else "256",
                )
            ),
        )
        flow_proxy_scale = min(1.0, flow_proxy_max / float(max(height, width)))
        print(
            f"[splattingSR] streaming alignment={'farneback' if use_farneback else 'block_matching'} "
            f"proxy={flow_proxy_scale:.3f} preset={preset if use_farneback else 'n/a'}"
        )
        return (
            SplatSRAlgorithm(":memory:"),
            use_farneback,
            farneback_config,
            matcher,
            bm_config,
            flow_proxy_scale,
        )

    def prepare_reference(self, reference, context):
        from functools import partial
        from taichi_vision import taichi_aot
        from .tiled_accumulator import TiledHannAccumulator, RamAccumulatorBacking

        context.check_cancelled()
        reference = np.ascontiguousarray(reference, dtype=np.float32)
        if reference.ndim != 3 or reference.shape[2] != 3:
            raise ValueError("Splat SR reference must be linear RGB (H,W,3)")
        height, width = reference.shape[:2]
        if self.scale < 1:
            raise ValueError("scale must be >= 1")

        params = taichi_aot.analyze_auto_enhance_params(reference, mode="analysis")
        analysis_reference_rgb = np.ascontiguousarray(
            taichi_aot.AutoEnhance(reference, params=params), dtype=np.float32
        )
        reference_gray = cv2.cvtColor(
            analysis_reference_rgb, cv2.COLOR_RGB2GRAY
        )
        reference_gray = np.ascontiguousarray(reference_gray, dtype=np.float32)
        reference_carrier_gray = (
            np.ascontiguousarray(
                cv2.cvtColor(reference, cv2.COLOR_RGB2GRAY), dtype=np.float32
            )
            if self.exposure_normalization or self.refinement_iterations > 0
            else None
        )

        algorithm, use_farneback, farneback_config, matcher, bm_config, proxy_scale = (
            self._configure_alignment(height, width)
        )
        accumulator = TiledHannAccumulator(
            reference,
            session=context.session,
            scale=self.scale,
            block_size=self.block_size,
            overlap=self.block_overlap,
            check_cancelled=context.check_cancelled,
            # Admission headroom for queued decoded RGB, one active carrier,
            # RGB analysis, flow, and five scalar host scratch planes. This
            # is an estimate, not a reservation for all backend/refine caches.
            backing_factory=partial(
                RamAccumulatorBacking,
                minimum_headroom_bytes=(
                    int(context.options.prefetch_depth) * reference.nbytes
                    + height * width * 52
                    + (height * width * self.scale**2 * 8 if self.refinement_iterations > 0 else 0)
                ),
            ),
        )
        if self.weight_source in ("compute_spatial", "spatial", "reliability"):
            provider = self.reliability_provider
            if provider is None:
                from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.reliability_confidence import (
                    ReliabilityConfidenceProvider,
                )

                provider = ReliabilityConfidenceProvider(session=context.session)
            prepare = getattr(provider, "prepare_reference", None)
            if callable(prepare):
                prepare(reference_gray, session=context.session)
            analysis_reference_for_provider = None
        elif self.weight_source in ("weightnet", "fusionnet"):
            provider = self.reliability_provider
            if provider is None:
                from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import (
                    _build_weightnet_provider,
                )

                provider = _build_weightnet_provider()
            analysis_reference_for_provider = analysis_reference_rgb
        else:
            raise ValueError(
                f"unsupported confidence source {self.weight_source!r}; "
                "use compute_spatial or weightnet"
            )

        refinement = None
        if self.refinement_iterations > 0:
            refinement = _RefinementBacking(
                len(self.paths), height, width
            )
            context.session.own(
                refinement, releaser=lambda backing: backing.close()
            )
            refinement.frames[0] = reference_carrier_gray
            refinement.flows[0] = 0.0
            refinement.confidence[0] = 1.0

        accumulator.add_frame(reference, None, None)
        del analysis_reference_rgb

        return _ReferenceState(
            reference_rgb=reference,
            reference_gray=reference_gray,
            reference_carrier_gray=reference_carrier_gray,
            analysis_params=params,
            analysis_reference_rgb=analysis_reference_for_provider,
            accumulator=accumulator,
            provider=provider,
            algorithm=algorithm,
            use_farneback=use_farneback,
            farneback_config=farneback_config,
            matcher=matcher,
            bm_config=bm_config,
            flow_proxy_scale=proxy_scale,
            exposure_normalization=self.exposure_normalization,
            refinement=refinement,
            count=len(self.paths),
        )

    def process_support(self, index, support, state, context):
        from taichi_vision import taichi_aot
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.legacy import (
            SplatSRAlgorithm,
        )

        context.check_cancelled()
        support = np.asarray(support, dtype=np.float32)
        if support.shape != state.reference_rgb.shape:
            raise ValueError(
                f"support shape {support.shape} != reference shape {state.reference_rgb.shape}"
            )
        total_supports = max(1, state.count - 1)
        local_index = int(index)
        stop = context.is_cancelled
        self._report(
            context,
            8 + int((state.processed / total_supports) * 10),
            f"Preparing Splat SR frame {local_index + 1}/{state.count}...",
        )

        # The support is owned by PipelineRuntime for this callback, so its
        # linear RGB carrier can be adjusted in-place without a burst copy.
        height, width = support.shape[:2]
        raw_gray = context.session.acquire_host(
            (height, width), dtype=np.float32, tag="splat_sr.raw_gray"
        )
        cv2.cvtColor(support, cv2.COLOR_RGB2GRAY, dst=raw_gray)
        pre_gain = np.float32(1.0)
        if state.exposure_normalization:
            pre_gain = SplatSRAlgorithm._estimate_exposure_gain(
                state.reference_carrier_gray, raw_gray
            )
            if abs(float(pre_gain) - 1.0) > 1.0e-5:
                np.multiply(support, pre_gain, out=support)
                np.multiply(raw_gray, pre_gain, out=raw_gray)

        with self.compute_gate:
            analysis_rgb = taichi_aot.AutoEnhance(
                support, params=state.analysis_params
            )
        analysis_rgb = np.ascontiguousarray(analysis_rgb, dtype=np.float32)
        analysis_gray = context.session.acquire_host(
            (height, width), dtype=np.float32, tag="splat_sr.analysis_gray"
        )
        cv2.cvtColor(analysis_rgb, cv2.COLOR_RGB2GRAY, dst=analysis_gray)
        with self.compute_gate:
            alignment_flow = state.algorithm._estimate_alignment_pair(
                use_farneback=state.use_farneback,
                farneback_config=state.farneback_config,
                matcher=state.matcher,
                bm_config=state.bm_config,
                reference_gray=state.reference_gray,
                target_gray=analysis_gray,
                index=local_index,
                matching_scale=state.flow_proxy_scale,
                update_progress=context.progress_callback,
                stop_requested=stop,
            )
        if alignment_flow is None:
            context.check_cancelled()
            raise RuntimeError(f"alignment returned no flow for support frame {index}")
        alignment_flow = np.ascontiguousarray(alignment_flow, dtype=np.float32)
        if alignment_flow.shape != (*support.shape[:2], 2):
            raise RuntimeError(
                f"alignment flow shape {alignment_flow.shape} != {*support.shape[:2], 2}"
            )

        map_x = context.session.acquire_host(
            (height, width), dtype=np.float32, tag="splat_sr.warp_map_x"
        )
        map_y = context.session.acquire_host(
            (height, width), dtype=np.float32, tag="splat_sr.warp_map_y"
        )
        aligned_gray = context.session.acquire_host(
            (height, width), dtype=np.float32, tag="splat_sr.aligned_gray"
        )
        np.add(
            alignment_flow[..., 0],
            np.arange(width, dtype=np.float32)[None, :],
            out=map_x,
        )
        np.add(
            alignment_flow[..., 1],
            np.arange(height, dtype=np.float32)[:, None],
            out=map_y,
        )
        cv2.remap(
            analysis_gray,
            map_x,
            map_y,
            cv2.INTER_LINEAR,
            dst=aligned_gray,
            borderMode=cv2.BORDER_REFLECT101,
        )
        if state.exposure_normalization:
            post_gain = SplatSRAlgorithm._estimate_exposure_gain(
                state.reference_gray, aligned_gray
            )
            if abs(float(post_gain) - 1.0) > 1.0e-5:
                np.multiply(support, post_gain, out=support)
                np.multiply(raw_gray, post_gain, out=raw_gray)
                np.multiply(aligned_gray, post_gain, out=aligned_gray)

        if self.weight_source in ("compute_spatial", "spatial", "reliability"):
            generate_device = getattr(state.provider, "generate_device", None)
            with self.compute_gate:
                if callable(generate_device):
                    confidence = generate_device(
                        state.reference_gray,
                        aligned_gray,
                        session=context.session,
                    )
                else:
                    confidence = state.provider(state.reference_gray, aligned_gray)
        else:
            fast_path = getattr(
                state.provider, "infer_aligned_support_with_flow", None
            )
            with self.compute_gate:
                if callable(fast_path):
                    confidence = fast_path(
                        state.analysis_reference_rgb,
                        analysis_rgb,
                        alignment_flow,
                    )
                else:
                    warped_analysis = SplatSRAlgorithm._warp_rgb_for_confidence(
                        analysis_rgb, alignment_flow
                    )
                    confidence = state.provider(
                        state.analysis_reference_rgb, warped_analysis
                    )
                    del warped_analysis

        # Confidence has consumed RGB analysis; release it before tile uploads.
        del analysis_rgb
        # Once confidence has consumed reference-to-support flow, invert that
        # same allocation in-place for source-to-HR splatting.
        np.negative(alignment_flow, out=alignment_flow)
        if state.refinement is not None:
            state.refinement.frames[index] = raw_gray
            state.refinement.flows[index] = alignment_flow
            if hasattr(confidence, "to_numpy"):
                state.refinement.confidence[index] = confidence.to_numpy()
            else:
                state.refinement.confidence[index] = confidence

        with self.compute_gate:
            state.accumulator.add_frame(support, alignment_flow, confidence)
        state.processed += 1
        context.session.reset_ring()
        self._report(
            context,
            20 + int((state.processed / total_supports) * 70),
            f"Splat SR frame {index + 1}/{state.count} complete",
        )
        del raw_gray, analysis_gray, aligned_gray, alignment_flow

    def finalize(self, state, context):
        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.splat_sr.spatial_splat_sr import (
            iterative_optical_refine_stream,
        )

        context.check_cancelled()
        with self.compute_gate:
            result = state.accumulator.finalize()
        try:
            if state.refinement is not None and self.refinement_iterations > 0:
                self._report(context, 92, "Running disk-backed optical refinement...")
                # Refinement retains its existing full-HR grayscale contract,
                # without materializing a full-HR RGB copy of the tile result.
                initial = np.empty(result.shape[:2], dtype=np.float32)
                for y0, y1, x0, x1, tile in result.iter_tiles(self.block_size):
                    context.check_cancelled()
                    initial[y0:y1, x0:x1] = cv2.cvtColor(tile, cv2.COLOR_RGB2GRAY)
                refined = iterative_optical_refine_stream(
                    state.refinement.frames,
                    lambda frame_index: state.refinement.flows[frame_index],
                    lambda frame_index: state.refinement.confidence[frame_index],
                    scale=self.scale,
                    block_size=self.block_size,
                    initial=initial,
                    iterations=self.refinement_iterations,
                    step=self.refinement_step,
                    regularization=self.refinement_regularization,
                )
                result.add_luma_delta(
                    initial, refined, block_size=self.block_size,
                    check_cancelled=context.check_cancelled,
                )
                state.refinement.close()
            self._report(context, 96, "Splat SR reconstruction ready")
            return result
        except BaseException:
            result.close()
            raise


__all__ = ["ImagePathSource", "SplatSRRecipe"]
