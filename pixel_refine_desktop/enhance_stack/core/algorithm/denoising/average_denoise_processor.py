"""
AverageDenoiseProcessor — Per-tile simple average denoising.

Implements TileProcessor for MFDenoiser's universal tiling orchestrator.
Each tile: sum all frames uniformly, return equal weights.

Algorithm (per tile):
  1. frame_sum = sum(frame_tiles)  across all N frames
  2. weight_map = N  (uniform weight per pixel)
  3. MFDenoiser handles Hanning stitching and final normalization.
"""

import numpy as np

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    TileContext,
    TileProcessor,
)


class AverageDenoiseProcessor(TileProcessor):
    """Simple average denoising processor (per-tile).

    The simplest TileProcessor — just sums all frames and returns
    uniform weights. MFDenoiser's tiler handles Hanning stitching
    and final accumulation/normalization.

    Output scale: 1:1 (output tile = input tile size).
    """

    def setup(self, ctx, shared_data):
        """No preprocessing needed for simple averaging."""
        pass

    def get_output_size(self, tile_h, tile_w):
        """Denoising: 1:1 output scale."""
        return (tile_h, tile_w)

    def process_tile(self, tile_ctx, shared_data):
        """Process a single tile by averaging all frames.

        Args:
            tile_ctx: TileContext with frame_tiles (N, tile_h, tile_w, C).
            shared_data: Not used for averaging.

        Returns:
            (weighted_sum, weight_map) tuple:
              - weighted_sum: (tile_h, tile_w, C) float32 — sum of all frames
              - weight_map: (tile_h, tile_w) float32 — uniform weight = N
        """
        frame_tiles = tile_ctx.frame_tiles  # (N, tile_h, tile_w, C)
        num_frames = frame_tiles.shape[0]

        if num_frames < 1:
            return None

        # Sum all frames — simple accumulation
        frame_sum = frame_tiles.sum(axis=0).astype(np.float32)  # (tile_h, tile_w, C)

        # Uniform weight: every pixel has weight = number of frames
        weight_map = np.full(
            (tile_ctx.tile_h, tile_ctx.tile_w),
            float(num_frames),
            dtype=np.float32,
        )

        return (frame_sum, weight_map)

    def teardown(self):
        """No resources to release."""
        pass
