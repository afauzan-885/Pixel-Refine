"""Spatial fusion denoising adapter.

This adapter intentionally delegates the heavy lifting to the legacy
SpatialFusionProcessor used by Similarity.py. That path already handles HDF5
streaming, work-resolution scaling, GPU buffer cleanup, and final fusion.
"""

import os

import h5py
import numpy as np


def _sorted_image_keys(h5f):
    return sorted(
        [key for key in h5f.keys() if key.startswith("image_")],
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
    DESCRIPTION = "Similarity-weighted spatial fusion from aligned HDF5 frames."

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

    def run(self, ctx, frames, batch_plan=None):
        if not ctx.hdf5_path or not os.path.exists(ctx.hdf5_path):
            print("[SpatialFusion] aligned HDF5 is not available.")
            return None

        config = self._resolve_config(ctx)

        from taichi_library import taichi_aot
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
            SpatialFusionProcessor,
        )

        engine = taichi_aot.engine
        if str(getattr(engine, "arch", "vulkan")).lower() == "cpu":
            raise RuntimeError(
                "[SpatialFusion] GPU AOT engine is running on CPU fallback. "
                "Similarity spatial fusion requires the active Vulkan/CUDA taichi_aot engine."
            )

        with h5py.File(ctx.hdf5_path, "r") as h5f:
            image_keys = _sorted_image_keys(h5f)
            if not image_keys:
                print("[SpatialFusion] no aligned images in HDF5.")
                return None

            reference = h5f[image_keys[0]][:]
            ref_h, ref_w = reference.shape[:2]
            ref_dtype = getattr(ctx, "ref_dtype", reference.dtype)
            reference_float = normalize_image(reference, ref_dtype)
            tile_size = int(config.get("similarity_spatial_tile_size", 12))
            tile_size = max(4, tile_size)
            overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))

            print(
                f"[SpatialFusion] delegating to stable Similarity model: "
                f"frames={len(image_keys)} source=HDF5 tile={tile_size} overlap={overlap:.2f}"
            )

        processor = SpatialFusionProcessor()
        result, _weight, processed_count = processor.process(
            images=[],
            data_source=ctx.hdf5_path,
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
            total_overall_images=len(image_keys),
            images_processed_so_far=0,
            enable_alignment=False,
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

        if result is None or processed_count <= 0:
            return None

        result = _restore_output_dtype(result, ref_dtype)
        print(
            f"[SpatialFusion] finished frames={processed_count} "
            f"result shape={result.shape} dtype={result.dtype}"
        )
        return result


SimilarityDenoisingAlgorithm = SpatialFusionDenoisingAlgorithm
