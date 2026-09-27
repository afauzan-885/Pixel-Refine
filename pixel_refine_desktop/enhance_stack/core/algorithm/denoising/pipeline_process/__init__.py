"""Canonical resident denoising pipeline package.

The package owns the shared lifecycle while RGB and RAW Native providers own
their respective carrier representations. Legacy modules under the parent
``denoising`` package remain compatibility facades during the migration.
"""

__all__ = [
    "run_gpu_resident_pipeline",
    "run_resident_pipeline",
    "load_frame_to_gpu",
]


def __getattr__(name):
    """Load the GPU executor lazily so contracts stay dependency-light."""
    if name in __all__:
        from . import resident_pipeline

        return getattr(resident_pipeline, name)
    raise AttributeError(name)
