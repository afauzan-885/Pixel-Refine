# blending/feather_blending.py
import numpy as np
import cv2
from typing import List
from .base_blender import BaseBlender

class FeatherBlender(BaseBlender):
    def _create_feather_weight_map(self, mask: np.ndarray) -> np.ndarray:
        if mask.dtype != np.uint8:
            mask = (mask > 0).astype(np.uint8)
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, cv2.DIST_MASK_5)
        max_val = np.max(dist_transform)
        if max_val == 0:
            return mask.astype(np.float32)
        weight_map = dist_transform / max_val
        return weight_map.astype(np.float32)

    def blend(self, images: List[np.ndarray], masks: List[np.ndarray]) -> np.ndarray:
        if not images:
            return np.zeros((1, 1, 3), dtype=np.float32)
            
        weight_maps = [self._create_feather_weight_map(mask) for mask in masks]
        
        blended_sum = np.zeros_like(images[0], dtype=np.float32)
        weight_sum = np.zeros(images[0].shape[:2], dtype=np.float32)

        for img, weight_map in zip(images, weight_maps):
            blended_sum += img * weight_map[..., np.newaxis]
            weight_sum += weight_map
            
        safe_weight_sum = np.maximum(weight_sum, 1e-6)
        return blended_sum / safe_weight_sum[..., np.newaxis]