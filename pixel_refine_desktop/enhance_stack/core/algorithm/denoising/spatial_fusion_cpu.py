"""Spatial fusion denoising adapter for CPU.

This adapter delegates the CPU spatial fusion processing to SpatialFusionProcessor,
running in CPU mode to calculate similarity-weighted merges using the JIT C++ library.
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


class SpatialFusionCPUDenoisingAlgorithm:
    NAME = "Similarity"
    KIND = "denoising"
    DESCRIPTION = "Similarity-weighted spatial fusion on CPU from aligned HDF5 frames."

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
        config = self._resolve_config(ctx)

        backend = str(config.get("similarity_backend", "gpu")).strip().lower()
        if backend == "ai":
            from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.smart_fusion import (
                SmartFusionDenoisingAlgorithm,
            )
            print("[SpatialFusionCPU] similarity_backend=ai → routing to AI processor.")
            return SmartFusionDenoisingAlgorithm().run(ctx, frames, batch_plan)

        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.spatial_core.spatial_fusion import (
            SpatialFusionProcessor,
        )

        use_hdf5 = bool(ctx.hdf5_path) and os.path.exists(ctx.hdf5_path)

        if use_hdf5:
            with h5py.File(ctx.hdf5_path, "r") as h5f:
                image_keys = _sorted_image_keys(h5f)
                if not image_keys:
                    print("[SpatialFusionCPU] no aligned images in HDF5.")
                    return None

                reference = h5f[image_keys[0]][:]
                ref_h, ref_w = reference.shape[:2]
                ref_dtype = getattr(ctx, "ref_dtype", reference.dtype)
                reference_float = normalize_image(reference, ref_dtype)

                # Load images into list for CPU thread pool
                images_list = [h5f[key][:] for key in image_keys]

                tile_size = int(config.get("similarity_spatial_tile_size", 12))
                tile_size = max(4, tile_size)
                overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))
                total_images = len(image_keys)

                print(
                    f"[SpatialFusionCPU] running Similarity model on CPU: "
                    f"frames={total_images} source=HDF5 tile={tile_size} overlap={overlap:.2f}"
                )
        else:
            if not frames:
                print("[SpatialFusionCPU] aligned HDF5 and in-memory frames are both unavailable.")
                return None
            reference = frames[0]
            ref_h, ref_w = reference.shape[:2]
            ref_dtype = getattr(ctx, "ref_dtype", reference.dtype)
            reference_float = normalize_image(reference, ref_dtype)

            # Load images into list for CPU thread pool (already in frames)
            images_list = list(frames)

            tile_size = int(config.get("similarity_spatial_tile_size", 12))
            tile_size = max(4, tile_size)
            overlap = float(config.get("similarity_spatial_overlap_percent", 0.35))
            total_images = len(frames)

            print(
                f"[SpatialFusionCPU] running Similarity model on CPU: "
                f"frames={total_images} source=memory_frames tile={tile_size} overlap={overlap:.2f}"
            )

        processor = SpatialFusionProcessor()
        result, _weight, processed_count = processor.process(
            images=images_list,
            data_source=None,  # Pass images list directly to avoid string index error
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
            enable_alignment=False,
            return_raw=False,
            is_linear_mode=bool(getattr(ctx, "is_linear_mode", False)),
            proxy_scale=float(config.get("proxy_scale", 1.0)),
            process_in="cpu",
            similarity_search_radius=int(config.get("similarity_search_radius", 3)),
            early_exit_threshold=float(config.get("early_exit_threshold", 0.05)),
        )

        if result is None or processed_count <= 0:
            return None

        result = _restore_output_dtype(result, ref_dtype)
        print(
            f"[SpatialFusionCPU] finished frames={processed_count} "
            f"result shape={result.shape} dtype={result.dtype}"
        )
        return result


SimilarityDenoisingAlgorithm = SpatialFusionCPUDenoisingAlgorithm
