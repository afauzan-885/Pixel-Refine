"""
SpatialDenoiseProcessor — Per-tile spatial similarity denoising.

Implements TileProcessor for MFDenoiser's universal tiling orchestrator.
Each tile: compute per-frame weights via local window MSE, accumulate weighted sum.

Algorithm (per tile):
  1. Reference = frame_tiles[0]
  2. For each non-reference frame:
     - Compute local MSE window vs reference
     - Weight = exp(-local_mse / (2 * noise_std^2)) * sensitivity
  3. Accumulate: sum += frame * weight, weight_sum += weight
"""

import numpy as np
import cv2

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    TileContext,
    TileProcessor,
)


class SpatialDenoiseProcessor(TileProcessor):
    """Spatial similarity-based denoising processor (per-tile).

    CPU-only implementation. No Taichi dependency.
    Output scale: 1:1 (output tile = input tile size).
    """

    def __init__(
        self,
        motion_sensitivity=150.0,
        noise_offset_factor=0.15,
    ):
        self.motion_sensitivity = motion_sensitivity
        self.noise_offset_factor = noise_offset_factor
        self._ref_noise_sigma = 0.0

    def setup(self, ctx, shared_data):
        """Precompute reference noise sigma for weight calculation."""
        ref_float = ctx.reference_float
        if ref_float is None:
            shared_data["ref_noise_sigma"] = 0.015
            return

        ref_gray = (
            cv2.cvtColor(ref_float, cv2.COLOR_BGR2GRAY)
            if ref_float.ndim == 3
            else ref_float
        )

        # Estimate noise via median absolute deviation (MAD)
        noise_sigma = self._estimate_noise_mad(ref_gray)
        shared_data["ref_noise_sigma"] = max(noise_sigma, 1e-6)
        self._ref_noise_sigma = shared_data["ref_noise_sigma"]

    def get_output_size(self, tile_h, tile_w):
        """Denoising: 1:1 output scale."""
        return (tile_h, tile_w)

    def process_tile(self, tile_ctx, shared_data):
        """Process a single denoising tile.

        Args:
            tile_ctx: TileContext with frame_tiles (N, tile_h, tile_w, C).
            shared_data: Contains ref_noise_sigma from setup().

        Returns:
            (weighted_sum, weight_map) tuple:
              - weighted_sum: (tile_h, tile_w, C) float32 — sum of frame * weight_k
              - weight_map: (tile_h, tile_w) float32 — sum of per-frame weights
        """
        frame_tiles = tile_ctx.frame_tiles  # (N, tile_h, tile_w, C)
        num_frames = frame_tiles.shape[0]
        if num_frames < 1:
            return None

        tile_h = tile_ctx.tile_h
        tile_w = tile_ctx.tile_w
        channels = frame_tiles.shape[3] if frame_tiles.ndim == 4 else 1

        ref_tile = frame_tiles[0]  # (tile_h, tile_w, C) float32

        noise_sigma = shared_data.get("ref_noise_sigma", 0.015)
        sensitivity = self.motion_sensitivity

        # Accumulators
        weighted_sum = np.zeros((tile_h, tile_w, channels), dtype=np.float32)
        weight_sum = np.zeros((tile_h, tile_w), dtype=np.float32)

        # Reference grayscale for weight computation
        if ref_tile.ndim == 3 and ref_tile.shape[2] >= 3:
            ref_gray = cv2.cvtColor(ref_tile, cv2.COLOR_RGB2GRAY)
        elif ref_tile.ndim == 3:
            ref_gray = ref_tile[:, :, 0]
        else:
            ref_gray = ref_tile

        for k in range(num_frames):
            curr_tile = frame_tiles[k]

            # Compute local MSE window vs reference
            if curr_tile.ndim == 3 and curr_tile.shape[2] >= 3:
                curr_gray = cv2.cvtColor(curr_tile, cv2.COLOR_RGB2GRAY)
            elif curr_tile.ndim == 3:
                curr_gray = curr_tile[:, :, 0]
            else:
                curr_gray = curr_tile

            diff = curr_gray - ref_gray
            local_mse = cv2.GaussianBlur(
                diff * diff, (5, 5), sigmaX=1.0
            )

            # Weight: exp(-local_mse / (2 * sigma^2)) * sensitivity
            w_k = np.exp(-local_mse / (2.0 * noise_sigma * noise_sigma + 1e-10))
            w_k = np.clip(w_k * sensitivity, 0.0, 1.0).astype(np.float32)

            # Accumulate
            weighted_sum += curr_tile * w_k[..., np.newaxis]
            weight_sum += w_k

        return (weighted_sum, weight_sum)

    @staticmethod
    def _estimate_noise_mad(gray):
        """Estimate noise sigma via Median Absolute Deviation of Laplacian."""
        if gray.dtype != np.float32:
            gray = gray.astype(np.float32)
        laplacian = cv2.Laplacian(gray, cv2.CV_32F)
        sigma = np.median(np.abs(laplacian)) * 1.4826 / 2.0
        return float(sigma)

    def teardown(self):
        """No GPU resources to release."""
        pass
