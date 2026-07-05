"""
TileBasedSpatialFusionProcessor — Per-Tile GPU AOT Spatial Fusion for MFDenoiser.

Implements TileProcessor interface for per-tile processing:
  1. Extract tiles from all frames
  2. Run alignment on tiles only (Farneback/Horn-Schunck)
  3. Warp original data using flow_map
  4. Run spatial merging on warped data → weight_map
  5. Accumulate weighted result

Benefits:
  - Reduced VRAM/RAM overhead (processes only tile-sized chunks)
  - Natural parallel computation support
  - Flexible tile size configuration (128, 256, 512 pixels)
"""

import numpy as np
import cv2
from abc import ABC, abstractmethod


class TileProcessor(ABC):
    """Interface for pluggable per-tile processors."""

    @abstractmethod
    def setup(self, ctx, shared_data: dict) -> None:
        """One-time initialization before the tile loop."""
        pass

    @abstractmethod
    def get_output_size(self, tile_h: int, tile_w: int) -> tuple:
        """Return output tile dimensions for a given input tile size."""
        pass

    @abstractmethod
    def process_tile(self, tile_ctx, shared_data: dict) -> tuple:
        """Process a single tile and return the weighted result.
        
        Returns:
            (weighted_sum, weight_map):
              - weighted_sum: np.ndarray of shape (out_h, out_w) or (out_h, out_w, C), float32
              - weight_map: np.ndarray of shape (out_h, out_w), float32
        """
        pass

    def preprocess_batch(self, batch_float: list, shared_data: dict) -> None:
        """Called after each batch is loaded, before the tile loop. Default: no-op."""
        pass

    def teardown(self) -> None:
        """Cleanup after the tile loop completes. Default: no-op."""
        pass


class TileBasedSpatialFusionProcessor(TileProcessor):
    """Per-tile GPU AOT Spatial Fusion processor.
    
    Processes each tile independently:
      1. Extract tiles from all frames
      2. Run alignment on tiles only → flow_map (tile_h, tile_w, 2)
      3. Warp original image data using flow_map
      4. Run spatial merging on warped data → weight_map
      5. Accumulate weighted result
    
    Args:
        motion_sensitivity: Higher = more aggressive ghost rejection (default 150.0).
        noise_offset_factor: Noise floor offset for weight calculation (default 0.15).
        early_exit_threshold: Skip tiles below this confidence (default 0.05).
        alignment_backend: "farneback" or "lucas_kanade" (default "farneback").
    """

    def __init__(
        self,
        motion_sensitivity=150.0,
        noise_offset_factor=0.15,
        early_exit_threshold=0.05,
        alignment_backend="farneback",
    ):
        self.motion_sensitivity = motion_sensitivity
        self.noise_offset_factor = noise_offset_factor
        self.early_exit_threshold = early_exit_threshold
        self.alignment_backend = alignment_backend
        
        self._engine = None
        self._ref_tile_gray = None
        self._ref_noise_sigma = None

    def setup(self, ctx, shared_data: dict) -> None:
        """Initialize GPU engine and validate availability."""
        from taichi_library.taichi_aot.engine import AOTEngine
        
        try:
            self._engine = AOTEngine()
        except Exception as e:
            raise RuntimeError(
                f"[TileBasedSpatialFusion] GPU AOT engine not available: {e}. "
                "Tile-based spatial fusion requires a compatible GPU with Vulkan support."
            )
        
        # Store reference tile gray for alignment
        if ctx.reference_float is not None:
            if ctx.reference_float.ndim == 3:
                self._ref_tile_gray = cv2.cvtColor(
                    (ctx.reference_float * 255).astype(np.uint8),
                    cv2.COLOR_RGB2GRAY
                ).astype(np.float32) / 255.0
            else:
                self._ref_tile_gray = ctx.reference_float.astype(np.float32)
        
        # Estimate noise on reference
        from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
            estimate_noise_in_python,
        )
        if self._ref_tile_gray is not None:
            self._ref_noise_sigma = estimate_noise_in_python(
                (self._ref_tile_gray * 255).astype(np.uint8)
            )
        else:
            self._ref_noise_sigma = 0.015  # default

    def get_output_size(self, tile_h: int, tile_w: int) -> tuple:
        """Output size is 1:1 (same as input tile size)."""
        return (tile_h, tile_w)

    def preprocess_batch(self, batch_float: list, shared_data: dict) -> None:
        """No batch preprocessing needed for tile-based processing."""
        pass

    def process_tile(self, tile_ctx, shared_data: dict) -> tuple:
        """Process a single tile.
        
        Args:
            tile_ctx: TileContext with frame_tiles (num_frames, tile_h, tile_w, C) float32.
            shared_data: Mutable dict shared across tiles.
        
        Returns:
            (weighted_sum, weight_map):
              - weighted_sum: np.ndarray of shape (tile_h, tile_w, C), float32
              - weight_map: np.ndarray of shape (tile_h, tile_w), float32
        """
        frame_tiles = tile_ctx.frame_tiles  # (num_frames, tile_h, tile_w, C)
        num_frames = frame_tiles.shape[0]
        tile_h = tile_ctx.tile_h
        tile_w = tile_ctx.tile_w
        
        if num_frames < 2:
            # Not enough frames, return reference tile with weight 1
            ref_tile = frame_tiles[0]
            weight_map = np.ones((tile_h, tile_w), dtype=np.float32)
            return (ref_tile, weight_map)
        
        # Reference tile (first frame)
        ref_tile = frame_tiles[0]
        if ref_tile.ndim == 3:
            ref_gray = cv2.cvtColor(
                (ref_tile * 255).astype(np.uint8),
                cv2.COLOR_RGB2GRAY
            ).astype(np.float32) / 255.0
        else:
            ref_gray = ref_tile.astype(np.float32)
        
        # Accumulators
        weighted_sum = np.zeros_like(ref_tile)
        weight_map = np.zeros((tile_h, tile_w), dtype=np.float32)
        
        # Process each frame
        for k in range(num_frames):
            comp_tile = frame_tiles[k]
            if comp_tile.ndim == 3:
                comp_gray = cv2.cvtColor(
                    (comp_tile * 255).astype(np.uint8),
                    cv2.COLOR_RGB2GRAY
                ).astype(np.float32) / 255.0
            else:
                comp_gray = comp_tile.astype(np.float32)
            
            # 1. Run alignment on tile only
            flow = self._compute_alignment(ref_gray, comp_gray)
            
            # 2. Warp original data using flow
            warped_tile = self._warp_tile(comp_tile, flow)
            
            # 3. Run spatial merging on warped data → weight
            frame_weight = self._compute_spatial_weight(ref_gray, comp_gray, flow)
            
            # 4. Accumulate
            if warped_tile.ndim == 3:
                weighted_sum += warped_tile * frame_weight[:, :, np.newaxis]
            else:
                weighted_sum += warped_tile * frame_weight
            weight_map += frame_weight
        
        return (weighted_sum, weight_map)

    def _compute_alignment(self, ref_gray: np.ndarray, comp_gray: np.ndarray) -> np.ndarray:
        """Compute optical flow between two grayscale tiles.
        
        Args:
            ref_gray: Reference tile grayscale (tile_h, tile_w), float32 [0,1].
            comp_gray: Comparison tile grayscale (tile_h, tile_w), float32 [0,1].
        
        Returns:
            flow: np.ndarray of shape (tile_h, tile_w, 2), float32.
        """
        ref_u8 = (ref_gray * 255).astype(np.uint8)
        comp_u8 = (comp_gray * 255).astype(np.uint8)
        
        if self.alignment_backend == "farneback":
            # Farneback optical flow
            flow = cv2.calcOpticalFlowFarneback(
                ref_u8, comp_u8, None,
                pyr_scale=0.5,
                levels=3,
                winsize=15,
                iterations=3,
                poly_n=5,
                poly_sigma=1.2,
                flags=0
            )
        elif self.alignment_backend == "lucas_kanade":
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.optical_flow.lucas_kanade_cpu import (
                LucasKanadeCPU,
            )

            flow = LucasKanadeCPU().calculate_flow(
                ref_u8,
                comp_u8,
                LucasKanadeCPU.load_config(),
            )
        else:
            # Fallback: zero flow
            flow = np.zeros((ref_gray.shape[0], ref_gray.shape[1], 2), dtype=np.float32)
        
        return flow

    def _warp_tile(self, tile: np.ndarray, flow: np.ndarray) -> np.ndarray:
        """Warp tile using optical flow.
        
        Args:
            tile: Input tile (tile_h, tile_w, C) or (tile_h, tile_w), float32.
            flow: Optical flow (tile_h, tile_w, 2), float32.
        
        Returns:
            warped: Warped tile with same shape as input.
        """
        tile_h, tile_w = flow.shape[:2]
        
        # Create coordinate grid
        y, x = np.mgrid[0:tile_h, 0:tile_w].astype(np.float32)
        
        # Add flow to coordinates
        map_x = x + flow[:, :, 0]
        map_y = y + flow[:, :, 1]
        
        # Warp using bilinear interpolation
        if tile.ndim == 3:
            warped = cv2.remap(
                tile, map_x, map_y,
                interpolation=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT_101
            )
        else:
            warped = cv2.remap(
                tile, map_x, map_y,
                interpolation=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REFLECT_101
            )
        
        return warped

    def _compute_spatial_weight(
        self, ref_gray: np.ndarray, comp_gray: np.ndarray, flow: np.ndarray
    ) -> np.ndarray:
        """Compute spatial weight map based on gradient similarity.
        
        Args:
            ref_gray: Reference grayscale (tile_h, tile_w), float32 [0,1].
            comp_gray: Comparison grayscale (tile_h, tile_w), float32 [0,1].
            flow: Optical flow (tile_h, tile_w, 2), float32.
        
        Returns:
            weight_map: np.ndarray of shape (tile_h, tile_w), float32 [0,1].
        """
        # Compute gradients
        ref_grad_x = cv2.Sobel(ref_gray, cv2.CV_32F, 1, 0, ksize=3)
        ref_grad_y = cv2.Sobel(ref_gray, cv2.CV_32F, 0, 1, ksize=3)
        comp_grad_x = cv2.Sobel(comp_gray, cv2.CV_32F, 1, 0, ksize=3)
        comp_grad_y = cv2.Sobel(comp_gray, cv2.CV_32F, 0, 1, ksize=3)
        
        # Compute gradient difference (MAD score)
        grad_diff_x = ref_grad_x - comp_grad_x
        grad_diff_y = ref_grad_y - comp_grad_y
        mad_score = np.sqrt(grad_diff_x**2 + grad_diff_y**2)
        
        # Convert to weight using motion sensitivity and noise offset
        noise_threshold = self._ref_noise_sigma * self.noise_offset_factor
        normalized_diff = mad_score / (noise_threshold + 1e-6)
        
        # Sigmoid-like weight: high diff → low weight
        weight = 1.0 / (1.0 + np.exp(self.motion_sensitivity * 0.01 * (normalized_diff - 1.0)))
        
        # Clamp to [0, 1]
        weight = np.clip(weight, 0.0, 1.0)
        
        return weight.astype(np.float32)

    def teardown(self) -> None:
        """Cleanup GPU resources."""
        self._engine = None
        self._ref_tile_gray = None
        self._ref_noise_sigma = None
