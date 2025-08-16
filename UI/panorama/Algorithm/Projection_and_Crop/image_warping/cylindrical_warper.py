import numpy as np
import cv2
from typing import List, Tuple, Dict
from .base_warper import BaseWarper

class CylindricalWarper(BaseWarper):
    def __init__(self, rotations: List[np.ndarray], focal_length: float, 
                 canvas_center_x: float, canvas_center_y: float, **kwargs):
        super().__init__(**kwargs)
        self.rotations = rotations
        self.focal_length = focal_length
        self.canvas_center_x = canvas_center_x
        self.canvas_center_y = canvas_center_y

    def build_task_list(self, output_shape: tuple, tile_size: tuple) -> List[Dict]:
        all_tasks = []
        for y_start in range(0, output_shape[0], tile_size[0]):
            for x_start in range(0, output_shape[1], tile_size[1]):
                y_end = min(y_start + tile_size[0], output_shape[0])
                x_end = min(x_start + tile_size[1], output_shape[1])
                tile_shape = (y_end - y_start, x_end - x_start, 3)
                task = {
                    "y_start": y_start, "x_start": x_start, "tile_shape": tile_shape,
                    "relevant_indices": list(range(len(self.image_paths))),
                    "canvas_center_x": self.canvas_center_x, "canvas_center_y": self.canvas_center_y
                }
                all_tasks.append(task)
        return all_tasks

    def warp_and_mask_layer(self, image: np.ndarray, task_info: Dict, image_index: int) -> Tuple[np.ndarray, np.ndarray]:
        h, w, _ = self.image_shapes[image_index]
        f = self.focal_length
        R_inv = self.rotations[image_index].T

        tile_h, tile_w, _ = task_info['tile_shape']
        
        # ### PERBAIKAN BUG #1: Typo pada x_start ###
        y_start, x_start = task_info['y_start'], task_info['x_start']

        # Buat grid koordinat di kanvas tujuan (output)
        x, y = np.meshgrid(np.arange(x_start, x_start + tile_w), np.arange(y_start, y_start + tile_h))

        # 1. Ubah koordinat kanvas 2D menjadi sudut (theta) dan tinggi (h_cyl)
        theta = (x - task_info['canvas_center_x']) / f
        h_cyl = (y - task_info['canvas_center_y'])

        # 2. Buat titik-titik 3D di permukaan silinder
        x_3d = np.sin(theta)
        # ### PERBAIKAN BUG #2: Rumus y_3d yang benar ###
        y_3d = h_cyl
        z_3d = np.cos(theta)

        # 3. Gabungkan dan putar kembali ke sistem koordinat kamera
        p_3d = np.stack([x_3d, y_3d, z_3d], axis=-1).reshape(-1, 3)
        p_cam = (R_inv @ p_3d.T).T.reshape(tile_h, tile_w, 3)

        # 4. Proyeksikan titik 3D di ruang kamera ke bidang gambar 2D
        mask = p_cam[..., 2] > 0
        
        # u = f * (X/Z) + cx  ;  v = f * (Y/Z) + cy
        u = np.where(mask, f * (p_cam[..., 0] / p_cam[..., 2]) + (w/2), -1)
        v = np.where(mask, f * (p_cam[..., 1] / p_cam[..., 2]) + (h/2), -1)
        
        valid_mask = mask & (u >= 0) & (u < w) & (v >= 0) & (v < h)
        u[~valid_mask] = -1
        v[~valid_mask] = -1

        warped_tile = cv2.remap(image, u.astype(np.float32), v.astype(np.float32), cv2.INTER_LINEAR, borderValue=(0,0,0,0))
        final_mask = valid_mask.astype(np.uint8) * 255
        
        return warped_tile, final_mask