"""Backend-neutral spatial fusion denoising adapter.

The public denoising algorithm is intentionally a single class.  General
Settings selects the native Taichi backend; this adapter only translates that
selection into the CPU or GPU execution lane of ``SpatialFusionProcessor``.
"""

import os

import h5py
import numpy as np


def _active_backend():
    """Resolve the backend selected by General Settings at call time."""
    from taichi_library.backend_config import requested_backend

    requested, _explicit, _source = requested_backend()
    if requested != "auto":
        return requested
    try:
        from taichi_library import taichi_aot

        return str(getattr(taichi_aot.engine, "arch", "cpu")).strip().lower()
    except Exception:
        return "cpu"


def _sorted_image_keys(h5f):
    return sorted(
        (key for key in h5f.keys() if key.startswith("image_")),
        key=lambda item: int(item.split("_", 1)[1]),
    )


def _restore_output_dtype(image, dtype):
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
        if image.dtype.kind == "f" and float(np.nanmax(image)) <= 1.5:
            image = image * float(info.max)
        image = np.clip(image, info.min, info.max)
    return image.astype(dtype, copy=False)


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
        batch_params = getattr(ctx, "params", {}).get("similarity_params")
        if isinstance(batch_params, dict):
            config.update(batch_params)
        return config

    @staticmethod
    def _load_inputs(ctx, frames):
        """Return a concrete frame list for both CPU and GPU lanes."""
        use_hdf5 = bool(getattr(ctx, "hdf5_path", None)) and os.path.exists(ctx.hdf5_path)
        if use_hdf5:
            with h5py.File(ctx.hdf5_path, "r") as h5f:
                keys = _sorted_image_keys(h5f)
                return [h5f[key][:] for key in keys], "hdf5"
        if frames:
            return list(frames), "memory"
        return [], "none"

    def run(self, ctx, frames, batch_plan=None):
        config = self._resolve_config(ctx)
        backend = _active_backend()
        gpu_backend = backend in {"cuda", "vulkan", "opengl", "gles"}
        # SpatialFusionProcessor is AOT-only now.  The historical name
        # ``process_in=gpu`` denotes the Taichi AOT lane, including an AOT CPU
        # target; it no longer means a C++/CPU fallback.
        process_in = "gpu"

        # The backend is selected by General Settings.  Do not route to a
        # second CPU/GPU adapter or silently fall back when the selected GPU
        # engine is unavailable.
        from taichi_library import taichi_aot

        engine_arch = str(getattr(taichi_aot.engine, "arch", backend)).strip().lower()
        if gpu_backend and engine_arch == "cpu":
            raise RuntimeError(
                f"[SpatialFusion] backend '{backend}' was selected, but the "
                "active Taichi engine is CPU. Restart after applying General Settings."
            )
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
            SpatialFusionProcessor,
        )

        images, source = self._load_inputs(ctx, frames)
        if not images:
            print("[SpatialFusion] no aligned images available.")
            return None

        reference = images[0]
        ref_h, ref_w = reference.shape[:2]
        ref_dtype = getattr(ctx, "ref_dtype", reference.dtype)
        reference_float = normalize_image(reference, ref_dtype)
        tile_size = max(4, int(config.get("similarity_spatial_tile_size", 12)))
        overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))
        total_images = len(images)

        print(
            f"[SpatialFusion] backend={backend} process={process_in} "
            f"frames={total_images} source={source} tile={tile_size} overlap={overlap:.2f}"
        )

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
            motion_sensitivity=float(config.get("similarity_spatial_motion_sensitivity", 150.0)),
            noise_offset_factor=float(config.get("similarity_spatial_noise_mad_offset_factor", 0.15)),
            update_progress=getattr(ctx, "update_progress", None),
            stop_requested=getattr(ctx, "stop_requested", None),
            total_overall_images=total_images,
            images_processed_so_far=0,
            enable_alignment=False,
            return_raw=False,
            is_linear_mode=bool(getattr(ctx, "is_linear_mode", False)),
            proxy_scale=float(config.get("proxy_scale", 1.0)),
            process_in=process_in,
            merging_backend="taichi",
            merge_progress_start=60,
            merge_progress_end=95,
            similarity_search_radius=int(config.get("similarity_search_radius", 3)),
            early_exit_threshold=float(config.get("early_exit_threshold", 0.05)),
        )

        if gpu_backend:
            with engine_reservation(taichi_aot.engine, "spatial_fusion"):
                result, _weight, processed_count = processor.process(**kwargs)
        else:
            result, _weight, processed_count = processor.process(**kwargs)

        if result is None or processed_count <= 0:
            return None
        result = _restore_output_dtype(result, ref_dtype)
        print(
            f"[SpatialFusion] finished backend={backend} frames={processed_count} "
            f"result shape={result.shape} dtype={result.dtype}"
        )
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
