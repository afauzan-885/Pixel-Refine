"""Pulse-Splat: Ultra-Fast Precision 3D Gaussian Splatting Engine.

Original Novel Architecture:
- TightEllipseBound (TEB): Formulasi analitik AABB eksak tertutup berbasis matriks kovariansi 2D.
- HierarchicalTileCulling (HTC): Eliminasi partikel tak bersinggungan di tingkat petak (tile) 16x16.
- TransmittanceEarlyExit (TEE): Penelusuran optik branchless berkepadatan tinggi.
"""

from .pulse_splat import (
    GaussianScene,
    PulseSplatPipeline,
    project_gaussians,
    rasterize_gaussians,
    render_pulse_splat,
)

__all__ = [
    "GaussianScene",
    "PulseSplatPipeline",
    "project_gaussians",
    "rasterize_gaussians",
    "render_pulse_splat",
]
