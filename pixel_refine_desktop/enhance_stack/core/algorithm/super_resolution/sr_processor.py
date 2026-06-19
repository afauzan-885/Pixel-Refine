"""
SuperResolutionProcessor — Per-tile weighted super-resolution.

Implements TileProcessor for MFDenoiser's universal tiling orchestrator.
Each tile: create TaichiWSR solver, run iterative optimization, return HR result.

Algorithm (per tile):
  1. Extract LR tiles from all frames
  2. Create TaichiWSR solver with LR data, weight maps, shifts
  3. Run iterative optimization (120 steps by default)
  4. Return HR tile (scale × input size)
"""

import gc
import numpy as np
import cv2

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    TileContext,
    TileProcessor,
)


class SuperResolutionProcessor(TileProcessor):
    """Weighted Super-Resolution processor (per-tile).

    Uses AOT engine for GPU-accelerated iterative SR.
    Output scale: configurable (default 2:1).
    """

    def __init__(self, scale=2, num_iterations=120, alpha=0.7, beta=0.005):
        self.scale = scale
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self._use_gpu = True

    def setup(self, ctx, shared_data):
        """Initialize backend (AOT engine handles GPU directly)."""
        shared_data["use_gpu"] = True

    def preprocess_batch(self, batch_float, shared_data):
        """Compute sub-pixel shifts and weight maps from the loaded batch."""
        from taichi_library.taichi_aot import phase_correlation

        if len(batch_float) < 2:
            shared_data["error"] = "Need at least 2 images for SR"
            return

        ref_image = batch_float[0]
        is_color = ref_image.ndim == 3 and ref_image.shape[2] == 3

        # Extract luminance channel for all frames
        lr_frames = []
        for img in batch_float:
            if is_color:
                img_yuv = cv2.cvtColor(
                    (img * 255).astype(np.uint8), cv2.COLOR_RGB2YCrCb
                )
                y_channel = img_yuv[:, :, 0].astype(np.float32) / 255.0
            else:
                y_channel = img if img.ndim == 2 else img[:, :, 0]
            lr_frames.append(y_channel)

        lr_frames = np.array(lr_frames, dtype=np.float32)
        shared_data["lr_frames"] = lr_frames
        shared_data["num_frames"] = len(lr_frames)
        shared_data["is_color"] = is_color

        # Compute sub-pixel shifts
        num_frames = len(lr_frames)
        shifts = np.zeros((num_frames, 2), dtype=np.float32)
        for k in range(1, num_frames):
            dx, dy, _ = phase_correlation(lr_frames[0], lr_frames[k], use_hanning=True)
            shifts[k] = [dy * self.scale, dx * self.scale]
        shared_data["shifts"] = shifts

        # Compute spatial weight maps (ghosting rejection)
        weight_maps = self._compute_spatial_weight_maps(lr_frames)
        shared_data["weight_maps"] = weight_maps

    def get_output_size(self, tile_h, tile_w):
        """Super-resolution: scale × output."""
        return (tile_h * self.scale, tile_w * self.scale)

    def process_tile(self, tile_ctx, shared_data):
        """Process a single SR tile.

        Args:
            tile_ctx: TileContext with frame_tiles (N, tile_h, tile_w, C).
            shared_data: Contains lr_frames, shifts, weight_maps from setup().

        Returns:
            (weighted_sum, weight_map) tuple:
              - weighted_sum: (hr_h, hr_w) float32 — HR luminance result
              - weight_map: (hr_h, hr_w) float32 — Hanning window weights
        """
        if "error" in shared_data:
            return None

        from pixel_refine_desktop.enhance_stack.core.algorithm.super_resolution.weighted_sr import (
            TaichiWSR,
        )

        lr_frames = shared_data["lr_frames"]
        shifts = shared_data["shifts"]
        weight_maps = shared_data["weight_maps"]

        tile_h = tile_ctx.tile_h
        tile_w = tile_ctx.tile_w
        hr_h = tile_h * self.scale
        hr_w = tile_w * self.scale

        # Extract LR tiles
        y_start = tile_ctx.tile_y
        x_start = tile_ctx.tile_x
        tile_lr = lr_frames[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
        tile_weight = weight_maps[:, y_start:y_start+tile_h, x_start:x_start+tile_w]
        num_frames = tile_lr.shape[0]

        # Create SR solver (AOT engine handles GPU allocation)
        solver = TaichiWSR(
            lr_shape=(tile_h, tile_w),
            hr_shape=(hr_h, hr_w),
            num_frames=num_frames,
            scale=self.scale,
            alpha=self.alpha,
            beta=self.beta,
            btv_window=2,
        )
        solver.set_lr_data(tile_lr, tile_weight, shifts)

        # Initial estimate via bicubic upsampling
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            normalize_image,
        )
        init_hr = cv2.resize(
            tile_lr[0], (hr_w, hr_h), interpolation=cv2.INTER_CUBIC
        )
        if init_hr.ndim == 3:
            init_hr = init_hr[:, :, 0]
        solver.set_initial_hr(init_hr)

        # Iterative optimization
        beta = self.beta
        for step_idx in range(self.num_iterations):
            if tile_ctx.stop_requested and tile_ctx.stop_requested():
                return None
            if step_idx > 0 and step_idx % 25 == 0:
                beta *= 0.90
                solver.beta = beta
            solver.step(lam=0.001)

        hr_result = solver.get_hr_image()

        # Generate Hanning window for stitching
        win_y = np.hanning(hr_h + 2)[1:-1].astype(np.float32)
        win_x = np.hanning(hr_w + 2)[1:-1].astype(np.float32)
        hanning_win = np.outer(win_y, win_x)

        # Cleanup
        del solver
        gc.collect()

        return (hr_result, hanning_win)

    def teardown(self):
        """Release resources."""
        gc.collect()

    @staticmethod
    def _compute_spatial_weight_maps(lr_frames, noise_std=0.015, sensitivity=120.0):
        """Compute spatial weight maps for ghosting rejection."""
        num_frames, h, w = lr_frames.shape
        weight_maps = np.ones_like(lr_frames)
        ref_frame = lr_frames[0]

        for k in range(1, num_frames):
            diff = lr_frames[k] - ref_frame
            local_mse = cv2.GaussianBlur(diff * diff, (5, 5), sigmaX=1.0)
            w_k = np.exp(-local_mse / (noise_std * noise_std * 2.0))
            w_k = np.clip(w_k * sensitivity, 0.0, 1.0)
            weight_maps[k] = w_k

        return weight_maps
