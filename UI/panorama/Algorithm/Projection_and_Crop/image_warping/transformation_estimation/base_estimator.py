from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseEstimator(ABC):
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback if progress_callback else lambda p, m: print(f"{p}%: {m}")

    @abstractmethod
    def estimate(self, n_images: int, image_shapes: List[tuple], all_kps: List, all_des: List) -> Tuple[Dict[str, Any], tuple, str]:
        """
        Mengestimasi transformasi antar gambar.

        Returns:
            Tuple[Dict, tuple, str]: Berisi (warp_params, output_size, error_message).
            - warp_params: Dictionary yang akan diteruskan ke Warper.
            - output_size: Ukuran kanvas akhir (H, W).
            - error_message: Pesan error jika gagal, atau None jika berhasil.
        """
        pass