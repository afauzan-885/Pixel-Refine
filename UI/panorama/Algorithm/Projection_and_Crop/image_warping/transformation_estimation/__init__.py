# Hapus RotationalEstimator, sekarang kita hanya punya satu cara untuk mengestimasi
from .base_estimator import BaseEstimator
from .planar_estimator import PlanarEstimator

def get_estimator(name: str, **kwargs) -> BaseEstimator:
    # Factory ini sekarang menjadi sangat sederhana
    if name == "planar":
        return PlanarEstimator(**kwargs)
    else:
        # Kita bisa menambahkan estimator lain di masa depan jika perlu
        raise ValueError(f"Metode estimasi untuk '{name}' tidak didukung.")