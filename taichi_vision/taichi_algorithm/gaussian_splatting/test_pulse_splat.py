import numpy as np
import taichi as ti
from taichi_vision.taichi_algorithm.gaussian_splatting.pulse_splat import (
    GaussianScene,
    project_gaussians,
    rasterize_gaussians,
    render_pulse_splat,
)

def test_pulse_splat_projection_and_render():
    ti.init(arch=ti.cpu)

    # 1. Buat scene sintetis 10 Gaussian sederhana
    N = 10
    means_3d = np.array([
        [0.0, 0.0, 2.0],
        [0.2, -0.1, 2.5],
        [-0.3, 0.2, 3.0],
        [0.1, 0.1, 1.8],
        [-0.1, -0.2, 2.2],
        [0.0, 0.3, 2.4],
        [0.25, 0.25, 2.7],
        [-0.2, -0.1, 2.1],
        [0.05, -0.05, 1.9],
        [-0.15, 0.15, 2.3],
    ], dtype=np.float32)

    scales = np.full((N, 3), 0.05, dtype=np.float32)
    rot_quats = np.zeros((N, 4), dtype=np.float32)
    rot_quats[:, 0] = 1.0  # Identity quaternion (w=1, x=0, y=0, z=0)

    colors = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 1.0],
        [0.8, 0.2, 0.2],
        [0.2, 0.8, 0.2],
        [0.2, 0.2, 0.8],
        [0.5, 0.5, 0.5],
    ], dtype=np.float32)

    opacities = np.full((N,), 0.9, dtype=np.float32)

    scene = GaussianScene(
        means_3d=means_3d,
        scales=scales,
        rot_quats=rot_quats,
        colors=colors,
        opacities=opacities,
    )

    view_matrix = np.eye(4, dtype=np.float32)
    w, h = 256, 256
    fx, fy = 200.0, 200.0
    cx, cy = 128.0, 128.0

    # 2. Test render Pulse-Splat
    img = render_pulse_splat(
        scene,
        view_matrix,
        fx,
        fy,
        cx,
        cy,
        w,
        h,
    )

    assert img.shape == (h, w, 3)
    assert img.dtype == np.float32
    assert np.max(img) > 0.0, "Gambar yang dirender tidak boleh kosong!"
    assert np.min(img) >= 0.0
    assert np.max(img) <= 1.0
    print("Test Pulse-Splat berhasil! Nilai piksel maksimal:", np.max(img))

if __name__ == "__main__":
    test_pulse_splat_projection_and_render()

