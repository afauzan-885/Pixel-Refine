# blending/average_blending.py
import numpy as np
from typing import List
from .base_blender import BaseBlender

class AverageBlender(BaseBlender):
    def blend(self, images: List[np.ndarray], masks: List[np.ndarray]) -> np.ndarray:
        if not images:
            return np.zeros((1, 1, 3), dtype=np.float32)

        weight_maps = [(mask > 0).astype(np.float32) for mask in masks]
        
        blended_sum = np.zeros_like(images[0], dtype=np.float32)
        weight_sum = np.zeros(images[0].shape[:2], dtype=np.float32)

        for img, weight_map in zip(images, weight_maps):
            blended_sum += img * weight_map[..., np.newaxis]
            weight_sum += weight_map
        
        safe_weight_sum = np.maximum(weight_sum, 1e-6)
        return blended_sum / safe_weight_sum[..., np.newaxis]