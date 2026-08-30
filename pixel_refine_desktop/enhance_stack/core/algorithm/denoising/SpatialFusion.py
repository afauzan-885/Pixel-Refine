"""Backend-neutral spatial fusion denoising adapter.

The public denoising algorithm is intentionally a single class.  General
Settings selects the native Taichi backend; this adapter only translates that
selection into the CPU or GPU execution lane of ``SpatialFusionProcessor``.
"""

import os
from contextlib import contextmanager

import h5py
import numpy as np


def _active_backend():
    """Resolve the backend selected by Performance Settings at call time.

    ``PerformancePage`` persists the canonical architecture as
    ``device_backend_arch``.  Reading it through the shared helper keeps
    SpatialFusion consistent with the backend shown by the settings UI and
    avoids an environment/default resolver selecting a different backend.
    """
    try:
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.backend_arch_helper import (
            get_backend_arch,
        )

        configured = str(get_backend_arch() or "").strip().lower()
        if configured in {"cpu", "cuda", "vulkan", "opengl", "gles"}:
            return configured
    except Exception:
        pass
    try:
        from taichi_vision import taichi_aot

        return str(getattr(taichi_aot.engine, "arch", "cpu")).strip().lower()
    except Exception:
        return "cpu"


def _sorted_image_keys(h5f):
    return sorted(
        (key for key in h5f.keys() if key.startswith("image_")),
        key=lambda item: int(item.split("_", 1)[1]),
    )


@contextmanager
def _synchronous_aot_execution():
    """Avoid worker/reservation lock inversion during internal alignment."""
    previous = os.environ.get("PIXEL_REFINE_AOT_MODE")
    os.environ["PIXEL_REFINE_AOT_MODE"] = "1"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("PIXEL_REFINE_AOT_MODE", None)
        else:
            os.environ["PIXEL_REFINE_AOT_MODE"] = previous


def _restore_output_dtype(image, dtype=np.uint16):
    if image is None:
        return None
    image_f32 = np.ascontiguousarray(image, dtype=np.float32)
    if dtype is None or not np.issubdtype(dtype, np.integer):
        dtype = np.uint16
    info = np.iinfo(dtype)
    max_val = float(np.nanmax(image_f32)) if image_f32.size > 0 else 1.0
    if max_val <= 1.5:
        image_f32 = image_f32 * float(info.max)
    image_clipped = np.clip(image_f32 + 0.5, float(info.min), float(info.max))
    return image_clipped.astype(dtype, copy=False)


class SpatialFusionDenoisingAlgorithm:
    NAME = "Similarity"
    KIND = "denoising"
    DESCRIPTION = "Backend-neutral similarity-weighted spatial fusion."

    @staticmethod
    def load_config():
        from pixel_refine_desktop.enhance_stack.components.batch_page_v2.parameter_denoising.similarity_parameter_settings import (
            load_similarity_config,
        )

        return load_similarity_config()

    def _resolve_config(self, ctx):
        config = self.load_config()
        if hasattr(ctx, "params") and isinstance(ctx.params, dict):
            for k in (
                "similarity_spatial_tile_size",
                "similarity_spatial_motion_sensitivity",
                "similarity_spatial_noise_mad_offset_factor",
                "similarity_spatial_overlap_percent",
                "early_exit_threshold",
                "work_resolution_scale",
                "proxy_scale",
                "noise_sigma",
                "similarity_smart_noise_alpha",
                "similarity_smart_noise_aware_enable",
                "similarity_smart_noise_strength",
            ):
                if k in ctx.params and ctx.params[k] is not None:
                    config[k] = ctx.params[k]
            batch_params = ctx.params.get("similarity_params")
            if isinstance(batch_params, dict):
                config.update(batch_params)
        return config

    @staticmethod
    def _load_inputs(ctx, frames):
        """Return a concrete frame list for both CPU and GPU lanes."""
        if frames:
            return list(frames), "memory"
        return [], "none"

    def run(self, ctx, frames=None, batch_plan=None):
        config = self._resolve_config(ctx)
        backend = _active_backend()

        image_paths = getattr(ctx, "image_paths", None)
        if image_paths and len(image_paths) >= 2:
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.resident_pipeline import (
                run_resident_pipeline,
            )
            import threading

            is_raw = bool(getattr(ctx, "is_linear_mode", False))
            tile_size = max(4, int(config.get("similarity_spatial_tile_size", 16)))
            overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))
            work_scale = float(
                config.get("work_resolution_scale", config.get("proxy_scale", 0.50))
            )
            storage_mode = "direct"

            stop_req = getattr(ctx, "stop_requested", None)
            if stop_req is not None and callable(stop_req) and stop_req():
                return None

            print(
                f"[SpatialFusion] Routing to GPU-resident pipeline: backend={backend} "
                f"frames={len(image_paths)} tile={tile_size} overlap={overlap:.2f} "
                f"storage_mode={storage_mode}"
            )

            alignment_plan = (
                getattr(ctx, "alignment_selection_name", None)
                or getattr(ctx, "params", {}).get("alignment_plan", "No Alignment")
            )
            alignment_config = getattr(ctx, "params", {}).get(
                "alignment_params", {}
            )

            batch_queue = int(
                getattr(ctx, "params", {}).get(
                    "batch_queue", getattr(ctx, "params", {}).get("batch_size", 3)
                )
            )

            ghost_penalty = float(config.get("ghost_penalty", 1.0))
            ghost_cutoff = float(config.get("ghost_cutoff", 0.05))
            chroma_sensitivity = float(
                config.get(
                    "chroma_sensitivity",
                    config.get("similarity_chroma_sensitivity", 6.0),
                )
            )

            result_fp32, _ = run_resident_pipeline(
                image_paths,
                session=None,
                weight_engine="spatial_fusion",
                alignment_plan=alignment_plan,
                alignment_config=alignment_config,
                spatial_config=config,
                work_scale=work_scale,
                tile_size=tile_size,
                overlap=overlap,
                ghost_penalty=ghost_penalty,
                ghost_cutoff=ghost_cutoff,
                chroma_sensitivity=chroma_sensitivity,
                is_raw=is_raw,
                storage_mode=storage_mode,
                batch_queue=batch_queue,
                stop_event=stop_req,
                progress_callback=getattr(ctx, "update_progress", None),
            )

            if result_fp32 is None:
                return None

            ref_dtype = getattr(ctx, "ref_dtype", np.uint16 if is_raw else np.uint8)
            result = _restore_output_dtype(result_fp32, ref_dtype)
            print(
                f"[SpatialFusion] finished backend={backend} "
                f"result shape={result.shape} dtype={result.dtype}"
            )
            return result

        # Legacy fallback if frames already loaded in memory
        images, source = self._load_inputs(ctx, frames)
        if not images:
            print("[SpatialFusion] no aligned images available.")
            return None

        reference = images[0]
        ref_h, ref_w = reference.shape[:2]
        ref_dtype = getattr(ctx, "ref_dtype", reference.dtype)
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
            SpatialFusionProcessor,
        )

        reference_float = normalize_image(reference, ref_dtype)
        tile_size = max(4, int(config.get("similarity_spatial_tile_size", 12)))
        overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))
        total_images = len(images)

        processor = SpatialFusionProcessor()
        kwargs = dict(
            images=images,
            data_source=None,
            ref_image_h=ref_h,
            ref_image_w=ref_w,
            ref_channels_buffer=3,
            ref_dtype=ref_dtype,
            reference_image_float=reference_float,
            tile_size=(tile_size, tile_size),
            overlap=overlap,
            motion_sensitivity=float(
                config.get("similarity_spatial_motion_sensitivity", 150.0)
            ),
            noise_offset_factor=float(
                config.get("similarity_spatial_noise_mad_offset_factor", 0.15)
            ),
            update_progress=getattr(ctx, "update_progress", None),
            stop_requested=getattr(ctx, "stop_requested", None),
            total_overall_images=total_images,
            images_processed_so_far=0,
            enable_alignment=True,
            optical_flow_type="alignment_tile",
            return_raw=False,
            is_linear_mode=bool(getattr(ctx, "is_linear_mode", False)),
            proxy_scale=float(config.get("proxy_scale", 1.0)),
            process_in="gpu",
            merging_backend="taichi",
            merge_progress_start=60,
            merge_progress_end=95,
            similarity_search_radius=int(config.get("similarity_search_radius", 3)),
            early_exit_threshold=float(config.get("early_exit_threshold", 0.05)),
        )

        with _synchronous_aot_execution():
            result, _weight, processed_count = processor.process(**kwargs)

        if result is None or processed_count <= 0:
            return None

        result = _restore_output_dtype(result, ref_dtype)
        return result


class _EngineReservation:
    def __init__(self, engine, name):
        self.engine = engine
        self.name = name
        self._ctx = None

    def __enter__(self):
        reserve = getattr(self.engine, "reserve_device_execution", None)
        if reserve is not None:
            self._ctx = reserve(self.name)
            self._ctx.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._ctx is not None:
            return self._ctx.__exit__(exc_type, exc, tb)
        return False


def engine_reservation(engine, name):
    return _EngineReservation(engine, name)


# Existing registry/import names remain valid while all execution uses the
# single backend-neutral implementation above.
SimilarityDenoisingAlgorithm = SpatialFusionDenoisingAlgorithm
