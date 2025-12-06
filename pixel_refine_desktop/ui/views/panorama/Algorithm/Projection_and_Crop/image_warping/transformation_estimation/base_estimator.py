from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseEstimator(ABC):
    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback if progress_callback else lambda p, m: print(f"{p}%: {m}")

    @abstractmethod
    def estimate(self, image_shapes: List[tuple], pairwise_matches: List[Dict]) -> Tuple[Dict[str, Any], tuple, str]:
        """
        Mengestimasi transformasi dan ukuran kanvas dari hasil pencocokan.

        Args:
            image_shapes: Daftar shape (H, W, C) dari setiap gambar.
            pairwise_matches: Hasil pencocokan fitur antar gambar.

        Returns:
            Tuple[Dict, tuple, str]: (warp_params, output_size, error_message).
        """
        pass