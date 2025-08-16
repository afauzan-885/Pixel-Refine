from .base_estimator import BaseEstimator
from .planar_estimator import PlanarEstimator
from .rotational_estimator import RotationalEstimator

ESTIMATOR_FACTORY = {
    "planar": PlanarEstimator,
    "cylindrical": RotationalEstimator,
    "mercator": RotationalEstimator,
}

def get_estimator(name: str, **kwargs) -> BaseEstimator:
    EstimatorClass = ESTIMATOR_FACTORY.get(name)
    if EstimatorClass is None:
        raise ValueError(f"Metode estimasi untuk '{name}' tidak dikenali.")
    return EstimatorClass(**kwargs)