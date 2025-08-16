from abc import ABC, abstractmethod
import numpy as np
from typing import List, Tuple, Dict, Any

class BaseWarper(ABC):
    def __init__(self, image_paths: List[str], image_shapes: List[tuple], **kwargs):
        self.image_paths = image_paths
        self.image_shapes = image_shapes

    @abstractmethod
    def build_task_list(self, output_shape: tuple, tile_size: tuple) -> List[Dict]:
        """Merencanakan semua pekerjaan rendering untuk setiap ubin."""
        pass

    @abstractmethod
    def warp_and_mask_layer(self, image: np.ndarray, task_info: Dict, image_index: int) -> Tuple[np.ndarray, np.ndarray]:
        """Melakukan warping dan membuat mask untuk SATU gambar."""
        pass