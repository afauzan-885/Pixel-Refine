# blending/base_blender.py
from abc import ABC, abstractmethod
import numpy as np
from typing import List

class BaseBlender(ABC):
    """
    Kelas dasar abstrak untuk semua implementasi blender.
    Setiap blender harus mengimplementasikan metode blend().
    """
    @abstractmethod
    def blend(self, images: List[np.ndarray], masks: List[np.ndarray]) -> np.ndarray:
        """
        Menggabungkan daftar gambar (float32, rentang 0-1) menggunakan mask yang sesuai.

        Args:
            images: Daftar gambar yang akan digabungkan.
            masks: Daftar mask biner (uint8) untuk setiap gambar.

        Returns:
            Gambar tunggal hasil penggabungan (float32).
        """
        pass