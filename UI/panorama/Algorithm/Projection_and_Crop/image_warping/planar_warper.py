import numpy as np
import cv2
from typing import List, Tuple, Dict
from .base_warper import BaseWarper

class PlanarWarper(BaseWarper):
    def __init__(self, homographies: List[np.ndarray], **kwargs):
        super().__init__(**kwargs)
        self.homographies = homographies
        self.inv_homographies = [np.linalg.inv(H) for H in homographies if H is not None]

    def build_task_list(self, output_shape: tuple, tile_size: tuple) -> List[Dict]:
        all_tasks = []
        for y_start in range(0, output_shape[0], tile_size[0]):
            for x_start in range(0, output_shape[1], tile_size[1]):
                y_end = min(y_start + tile_size[0], output_shape[0])
                x_end = min(x_start + tile_size[1], output_shape[1])
                tile_shape = (y_end - y_start, x_end - x_start, 3)
                
                relevant_indices = []
                for i in range(len(self.image_paths)):
                    H_inv = self.inv_homographies[i]
                    corners = np.float32([[x_start, y_start], [x_end, y_start], [x_end, y_end], [x_start, y_end]]).reshape(-1, 1, 2)
                    orig_corners = cv2.perspectiveTransform(corners, H_inv)
                    min_x, min_y = np.min(orig_corners, axis=0).ravel()
                    max_x, max_y = np.max(orig_corners, axis=0).ravel()
                    h, w, _ = self.image_shapes[i]
                    if not (max_x < 0 or min_x > w or max_y < 0 or min_y > h):
                        relevant_indices.append(i)

                if relevant_indices:
                    all_tasks.append({
                        "y_start": y_start, "x_start": x_start,
                        "tile_shape": tile_shape, "relevant_indices": relevant_indices
                    })
        return all_tasks

    def warp_and_mask_layer(self, image: np.ndarray, task_info: Dict, image_index: int) -> Tuple[np.ndarray, np.ndarray]:
        H = self.homographies[image_index]
        x_start, y_start = task_info['x_start'], task_info['y_start']
        tile_shape = task_info['tile_shape']

        T_tile = np.array([[1, 0, -x_start], [0, 1, -y_start], [0, 0, 1]], dtype=np.float64)
        H_tile = T_tile @ H
        
        warped_tile = cv2.warpPerspective(image, H_tile, (tile_shape[1], tile_shape[0]))
        
        gray = cv2.cvtColor(warped_tile * 255, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray.astype(np.uint8), 1, 255, cv2.THRESH_BINARY)
        mask = cv2.erode(mask, np.ones((3, 3), np.uint8), iterations=1)
        
        return warped_tile, mask