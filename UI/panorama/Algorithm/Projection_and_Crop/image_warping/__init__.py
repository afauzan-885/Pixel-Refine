from .base_warper import BaseWarper
from .planar_warper import PlanarWarper
from .cylindrical_warper import CylindricalWarper
from .mercator_warper import MercatorWarper

WARPER_FACTORY = {
    "planar": PlanarWarper,
    "cylindrical": CylindricalWarper,
    "mercator": MercatorWarper,
}

def get_warper(name: str, **kwargs) -> BaseWarper:
    WarperClass = WARPER_FACTORY.get(name)
    if WarperClass is None:
        raise ValueError(f"Metode warp '{name}' tidak dikenali.")
    return WarperClass(**kwargs)