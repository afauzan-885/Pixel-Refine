# blending/__init__.py
from .base_blender import BaseBlender
from .AverageBlending import AverageBlender
from .FeatherBlending import FeatherBlender
from .MultibandBlending import MultiBandBlender

# "Factory" untuk membuat objek blender
BLENDER_FACTORY = {
    "simple_average": AverageBlender(),
    "feather": FeatherBlender(),
    "multiband": MultiBandBlender(),
}

def get_blender(name: str) -> BaseBlender:
    """
    Mengembalikan instance dari blender yang diminta.
    Default ke MultiBandBlender jika nama tidak ditemukan.
    """
    blender = BLENDER_FACTORY.get(name)
    if blender is None:
        print(f"PERINGATAN: Blender '{name}' tidak dikenali. Menggunakan 'multiband' sebagai default.")
        return BLENDER_FACTORY["multiband"]
    return blender