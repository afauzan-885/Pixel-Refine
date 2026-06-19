"""
SmartDenoiseProcessor — Per-tile AI-based smart fusion denoising.

Implements TileProcessor for MFDenoiser's universal tiling orchestrator.
Each tile: ONNX inference for per-frame weight computation, accumulate weighted sum.

Algorithm (per tile):
  1. Reference tile → analysis model → ref features
  2. For each non-reference frame:
     - Frame tile → analysis model → curr features
     - Fusion model(ref_feat, curr_feat, sigma, alpha) → weight map
  3. Accumulate: sum += frame * weight, weight_sum += weight
"""

import os
import gc
import cv2
import numpy as np
import onnxruntime as ort

from pixel_refine_desktop.enhance_stack.core.algorithm.denoising.MFDenoiser import (
    TileContext,
    TileProcessor,
)


class SmartDenoiseProcessor(TileProcessor):
    """AI-based Smart Fusion denoising processor (per-tile).

    Uses ONNX models for per-frame weight estimation.
    Output scale: 1:1 (output tile = input tile size).
    """

    MODEL_DIR = "database/Learning_Model/nanoburst"

    def __init__(self, noise_alpha=1.0, preferred_device="gpu"):
        self.noise_alpha = noise_alpha
        self.preferred_device = preferred_device
        self._sess_a = None
        self._sess_f = None
        self._sigma_val = 0.0

    def _load_sessions(self, tile_size):
        """Load ONNX sessions for the given tile size."""
        device_map = {
            "gpu": ["CUDAExecutionProvider", "DmlExecutionProvider", "CPUExecutionProvider"],
            "dml": ["DmlExecutionProvider", "CPUExecutionProvider"],
            "cpu": ["CPUExecutionProvider"],
        }
        providers = device_map.get(self.preferred_device, device_map["gpu"])

        fmt = "fp16_gpu" if self.preferred_device in ("gpu", "dml") else "fp32_cpu"
        a_path = os.path.join(self.MODEL_DIR, f"smart_analysis_{tile_size}_{fmt}.onnx")
        f_path = os.path.join(self.MODEL_DIR, f"smart_fusion_{tile_size}_{fmt}.onnx")

        if not os.path.exists(a_path):
            a_path = os.path.join(self.MODEL_DIR, f"smart_analysis_{tile_size}_fp32_cpu.onnx")
            f_path = os.path.join(self.MODEL_DIR, f"smart_fusion_{tile_size}_fp32_cpu.onnx")
            providers = ["CPUExecutionProvider"]

        if not os.path.exists(a_path) or not os.path.exists(f_path):
            raise FileNotFoundError(f"Smart Merging models not found for tile {tile_size}")

        self._sess_a = ort.InferenceSession(a_path, providers=providers)
        self._sess_f = ort.InferenceSession(f_path, providers=providers)

    def setup(self, ctx, shared_data):
        """Load ONNX sessions and estimate noise sigma."""
        tile_size = ctx.params.get("similarity_spatial_tile_size", 320)
        try:
            self._load_sessions(tile_size)
        except Exception as e:
            print(f"[Smart Fusion] Error loading sessions: {e}")
            shared_data["error"] = str(e)
            return

        # Estimate noise from reference
        ref_float = ctx.reference_float
        if ref_float is not None:
            gray = cv2.cvtColor(
                (ref_float * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY
            )
            from pixel_refine_desktop.enhance_stack.core.algorithm.alignment.alignment_features.global_feature import (
                estimate_noise_in_python,
            )
            self._sigma_val = estimate_noise_in_python(
                gray.astype(np.float32) / 255.0
            )
        else:
            self._sigma_val = 0.0

        shared_data["sigma_input"] = np.array([[[[self._sigma_val]]]], dtype=np.float32)
        shared_data["alpha_input"] = np.array([[[[self.noise_alpha]]]], dtype=np.float32)

        # Precompute input names
        shared_data["input_names_f"] = [i.name for i in self._sess_f.get_inputs()]

    def get_output_size(self, tile_h, tile_w):
        """Smart fusion: 1:1 output scale."""
        return (tile_h, tile_w)

    def process_tile(self, tile_ctx, shared_data):
        """Process a single smart fusion tile.

        Args:
            tile_ctx: TileContext with frame_tiles (N, tile_h, tile_w, C).
            shared_data: Contains sigma_input, alpha_input, input_names_f from setup().

        Returns:
            (weighted_sum, weight_map) tuple:
              - weighted_sum: (tile_h, tile_w, C) float32
              - weight_map: (tile_h, tile_w) float32
        """
        if self._sess_a is None or self._sess_f is None:
            return None

        frame_tiles = tile_ctx.frame_tiles  # (N, tile_h, tile_w, C)
        num_frames = frame_tiles.shape[0]
        if num_frames < 1:
            return None

        tile_h = tile_ctx.tile_h
        tile_w = tile_ctx.tile_w
        channels = frame_tiles.shape[3] if frame_tiles.ndim == 4 else 1

        sigma_input = shared_data.get("sigma_input")
        alpha_input = shared_data.get("alpha_input")
        input_names_f = shared_data.get("input_names_f", [])

        # Reference tile features
        ref_tile = frame_tiles[0]  # (tile_h, tile_w, C) float32
        ref_nchw = ref_tile.transpose(2, 0, 1)[np.newaxis].astype(np.float32)  # (1, C, H, W)
        ref_feats = self._sess_a.run(None, {"x": ref_nchw})[0]

        # Initialize accumulators with reference (weight = 1.0)
        weighted_sum = ref_tile.copy().astype(np.float32)
        weight_map = np.ones((tile_h, tile_w), dtype=np.float32)

        for k in range(1, num_frames):
            curr_tile = frame_tiles[k]

            curr_nchw = curr_tile.transpose(2, 0, 1)[np.newaxis].astype(np.float32)
            curr_feats = self._sess_a.run(None, {"x": curr_nchw})[0]

            input_feed = {"ref_feat": ref_feats, "curr_feat": curr_feats}
            if "sigma" in input_names_f and sigma_input is not None:
                input_feed["sigma"] = sigma_input
            if "alpha" in input_names_f and alpha_input is not None:
                input_feed["alpha"] = alpha_input

            w_out = self._sess_f.run(None, input_feed)[0]
            w_2d = w_out.reshape(tile_h, tile_w).astype(np.float32)

            weighted_sum += curr_tile * w_2d[..., np.newaxis]
            weight_map += w_2d

        return (weighted_sum, weight_map)

    def teardown(self):
        """Release ONNX sessions."""
        self._sess_a = None
        self._sess_f = None
        gc.collect()
