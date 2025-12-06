# blending/multiband_blending.py
import numpy as np
import cv2
from typing import List

from .FeatherBlending import FeatherBlender
from .base_blender import BaseBlender

class MultiBandBlender(BaseBlender):
    def __init__(self, num_levels: int = 5):
        self.num_levels = num_levels
        # Multi-band bekerja paling baik dengan feather mask, jadi kita gunakan di dalam
        self._feather_blender_helper = FeatherBlender()

    def _create_laplacian_pyramid(self, image: np.ndarray) -> List[np.ndarray]:
        # ... (kode _create_laplacian_pyramid Anda di sini) ...
        pyramid = []
        current_image = image
        for _ in range(self.num_levels - 1):
            down = cv2.pyrDown(current_image)
            up = cv2.pyrUp(down, dstsize=(current_image.shape[1], current_image.shape[0]))
            laplacian_layer = cv2.subtract(current_image, up)
            pyramid.append(laplacian_layer)
            current_image = down
        pyramid.append(current_image)
        return pyramid

    def _reconstruct_from_laplacian_pyramid(self, pyramid: List[np.ndarray]) -> np.ndarray:
        # ... (kode _reconstruct_from_laplacian_pyramid Anda di sini) ...
        current_image = pyramid[-1]
        for i in range(len(pyramid) - 2, -1, -1):
            up = cv2.pyrUp(current_image, dstsize=(pyramid[i].shape[1], pyramid[i].shape[0]))
            current_image = cv2.add(up, pyramid[i])
        return current_image

    def blend(self, images: List[np.ndarray], masks: List[np.ndarray]) -> np.ndarray:
        if not images:
            return np.zeros((1, 1, 3), dtype=np.float32)

        laplacian_pyramids = [self._create_laplacian_pyramid(img) for img in images]
        
        weight_maps = [self._feather_blender_helper._create_feather_weight_map(mask) for mask in masks]
        mask_pyramids = []
        for weight_map in weight_maps:
            mask_3ch = np.stack([weight_map] * 3, axis=-1)
            pyramid = [mask_3ch]
            for _ in range(self.num_levels - 1):
                pyramid.append(cv2.pyrDown(pyramid[-1]))
            mask_pyramids.append(list(reversed(pyramid)))

        blended_pyramid = []
        for level in range(self.num_levels):
            blended_level = np.zeros_like(laplacian_pyramids[0][level])
            weight_sum_level = np.zeros_like(laplacian_pyramids[0][level])
            for i in range(len(images)):
                laplacian_layer = laplacian_pyramids[i][level]
                mask_layer = mask_pyramids[i][self.num_levels - 1 - level]
                blended_level += laplacian_layer * mask_layer
                weight_sum_level += mask_layer
            
            weight_sum_level = np.maximum(weight_sum_level, 1e-6)
            blended_pyramid.append(blended_level / weight_sum_level)
            
        return self._reconstruct_from_laplacian_pyramid(blended_pyramid)