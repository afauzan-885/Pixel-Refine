import json
import os

import cv2
import numpy as np

from config import ALGORITHM_PARAMETER_SETTINGS_FILE
from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.optical_flow_utils.flow_blocking import (
    align_with_block_flow,
)


DEFAULT_FARNEBACK_CONFIG = {
    "pyr_scale": 0.5,
    "levels": 3,
    "winsize": 15,
    "iterations": 3,
    "poly_n": 5,
    "poly_sigma": 1.2,
    "flags": 0,
    "use_multi_core": True,
    "tile_overlap": 0.20,
}


class FarnebackFlowCPU:
    NAME = "Farneback Optical Flow"
    KIND = "alignment"
    DESCRIPTION = "Tile-based CPU Farneback optical flow alignment."

    @staticmethod
    def load_config(batch_id=None, config_filename=None):
        config = DEFAULT_FARNEBACK_CONFIG.copy()
        config_filename = config_filename or ALGORITHM_PARAMETER_SETTINGS_FILE
        try:
            if os.path.exists(config_filename):
                with open(config_filename, "r") as config_file:
                    params = json.load(config_file)
                config.update(params.get("Farneback", {}))
                config.update(params.get("Farneback_BATCH", {}))
        except Exception as exc:
            print(f"[FarnebackFlowCPU] Failed to load config: {exc}")
        return config

    @staticmethod
    def load_farneback_config(config_filename=None):
        return FarnebackFlowCPU.load_config(config_filename=config_filename)

    @staticmethod
    def load_farneback_config_for_batch(config_filename=None):
        return FarnebackFlowCPU.load_config(config_filename=config_filename)

    def calculate_flow(self, reference_gray, target_gray, config):
        return cv2.calcOpticalFlowFarneback(
            reference_gray,
            target_gray,
            None,
            pyr_scale=float(config.get("pyr_scale", 0.5)),
            levels=int(config.get("levels", 3)),
            winsize=int(config.get("winsize", 15)),
            iterations=int(config.get("iterations", 3)),
            poly_n=int(config.get("poly_n", 5)),
            poly_sigma=float(config.get("poly_sigma", 1.2)),
            flags=int(config.get("flags", 0)),
        )

    def align_frame(self, reference, target, config=None, stop_requested=None, target_for_warping=None):
        config = config or self.load_config()

        def flow_func(reference_gray, target_gray):
            return self.calculate_flow(reference_gray, target_gray, config)

        halo = max(
            int(config.get("winsize", 15)),
            int(config.get("poly_n", 5)) * (2 ** max(0, int(config.get("levels", 3)) - 1)),
        )
        return align_with_block_flow(
            reference,
            target,
            flow_func,
            halo=halo,
            use_multi_core=bool(config.get("use_multi_core", True)),
            stop_requested=stop_requested,
            target_for_warping=target_for_warping,
        )

    def build_flow_alignment(self, ctx, reference, target_dims, orchestrator, config):
        os.makedirs(os.path.dirname(ctx.hdf5_path), exist_ok=True)
        if os.path.exists(ctx.hdf5_path):
            os.remove(ctx.hdf5_path)

        import gc
        import h5py
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            extract_exif,
            save_to_hdf5,
            write_alignment_cache_attrs,
        )

        saved_count = 0
        with h5py.File(ctx.hdf5_path, "w") as h5f:
            write_alignment_cache_attrs(
                h5f,
                ref_image_path=ctx.image_paths[0],
                alignment_selection=getattr(ctx, "alignment_selection_name", self.NAME),
                alignment_algorithm=getattr(ctx, "alignment_effective_name", self.NAME),
                alignment_process="tile_optical_flow",
                cache_key=getattr(ctx, "alignment_cache_key", ""),
                cache_payload=getattr(ctx, "alignment_cache_payload", ""),
            )

            for index, path in enumerate(ctx.image_paths):
                if ctx.stop_requested and ctx.stop_requested():
                    break
                if index == 0:
                    aligned = np.array(reference, copy=True)
                else:
                    frame = orchestrator._load_single_frame(
                        ctx, path, target_dims=target_dims
                    )
                    if frame is None:
                        continue
                    aligned = self.align_frame(
                        reference,
                        frame,
                        config=config,
                        stop_requested=ctx.stop_requested,
                    )
                    del frame
                if aligned is None:
                    continue
                save_to_hdf5(h5f, f"image_{index}", aligned, extract_exif(path))
                h5f.flush()
                saved_count += 1
                print(
                    f"[FarnebackFlowCPU] saved image_{index} shape={aligned.shape} dtype={aligned.dtype}"
                )
                del aligned
                gc.collect()

                if ctx.update_progress:
                    progress = 25 + int(((index + 1) / max(1, ctx.total_images)) * 65)
                    ctx.update_progress(
                        progress, f"Farneback flow {index + 1}/{ctx.total_images}"
                    )

        ctx.aligned_frames = []
        ctx.frames = []
        ctx.data_source = ctx.hdf5_path
        ctx.needs_alignment = False
        print(
            f"[FarnebackFlowCPU] finished saved={saved_count} hdf5_path={ctx.hdf5_path}"
        )
        return ctx

    def run(self, ctx, frames, batch_plan=None):
        return list(frames)


def running_farneback_flow(*args, **kwargs):
    raise RuntimeError("Farneback Optical Flow is now orchestrated by MFDenoiser.")
