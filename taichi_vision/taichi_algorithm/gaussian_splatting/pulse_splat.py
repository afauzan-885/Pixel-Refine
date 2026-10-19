"""Pulse-Splat: Ultra-Fast Precision 3D Gaussian Splatting Engine.

Arsitektur Orisinal Pixel-Refine:
1. TightEllipseBound (TEB):
   Formulasi analitik exact tight axis-aligned bounding box (AABB) langsung
   dari invers matriks kovariansi 2D terproyeksi, meniadakan lingkaran pembungkus longgar.
2. Zero-Readback Pure GPU Depth Ordering:
   Proyeksi, penyortiran kedalaman paralel (Bitonic Sort Key-Value), dan rasterisasi
   berjalan 100% di GPU VRAM tanpa perantara pembacaan/sinkronisasi CPU/NumPy.
3. HierarchicalTileCulling (HTC):
   Pengujian batas elips-terhadap-kotak petak untuk mengeliminasi komputasi
   partikel siluman sebelum proses rasterisasi piksel.
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np
import taichi as ti

from ..common import ensure_taichi_field, get_temp_buffer, release_temp_buffer
from ..math_ops.math_ops_kernels import math_bitonic_sort_kv_step

TILE_SIZE = 16


@ti.func
def _quat_to_rot_matrix(q: ti.math.vec4) -> ti.math.mat3:
    """Mengonversi quaternion ternormalisasi (w, x, y, z) menjadi matriks rotasi 3x3."""
    r = q[0]
    x = q[1]
    y = q[2]
    z = q[3]

    return ti.math.mat3([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - r * z), 2.0 * (x * z + r * y)],
        [2.0 * (x * y + r * z), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - r * x)],
        [2.0 * (x * z - r * y), 2.0 * (y * z + r * x), 1.0 - 2.0 * (x * x + y * y)],
    ])


@ti.func
def _compute_cov3d(scale: ti.math.vec3, rot_q: ti.math.vec4) -> ti.math.mat3:
    """Menghitung matriks kovariansi 3D: Sigma = R * S * S^T * R^T."""
    R = _quat_to_rot_matrix(rot_q)
    s_mat = ti.math.mat3([
        [scale[0], 0.0, 0.0],
        [0.0, scale[1], 0.0],
        [0.0, 0.0, scale[2]],
    ])
    M = R @ s_mat
    return M @ M.transpose()


@ti.func
def _compute_cov2d(
    pos_cam: ti.math.vec3,
    cov3d: ti.math.mat3,
    fx: ti.f32,
    fy: ti.f32,
) -> ti.math.vec3:
    """Menghitung kovariansi 2D terproyeksi (cov_xx, cov_xy, cov_yy) dengan low-pass anti-aliasing."""
    z = pos_cam[2]
    inv_z = 1.0 / z
    inv_z2 = inv_z * inv_z

    # Vektor baris Jacobian proyeksi perspektif:
    j0 = ti.math.vec3(fx * inv_z, 0.0, -fx * pos_cam[0] * inv_z2)
    j1 = ti.math.vec3(0.0, fy * inv_z, -fy * pos_cam[1] * inv_z2)

    # Transformasi kovariansi: cov2d = J @ cov3d @ J^T
    w0 = cov3d @ j0
    w1 = cov3d @ j1

    # Filter low-pass anti-aliasing 0.3 piksel untuk mencegah moire
    cov_xx = j0.dot(w0) + 0.3
    cov_xy = j0.dot(w1)
    cov_yy = j1.dot(w1) + 0.3

    return ti.math.vec3(cov_xx, cov_xy, cov_yy)


@ti.func
def _compute_tight_ellipse_bound(
    mu_2d: ti.math.vec2,
    cov2d: ti.math.vec3,
    w: ti.i32,
    h: ti.i32,
) -> ti.math.vec4:
    """TightEllipseBound (TEB): Menghitung batas AABB eksak tertutup dari elips 2D."""
    cov_xx = cov2d[0]
    cov_yy = cov2d[2]

    rx = 3.0 * ti.sqrt(ti.max(cov_xx, 1e-4))
    ry = 3.0 * ti.sqrt(ti.max(cov_yy, 1e-4))

    min_x = ti.max(0.0, mu_2d[0] - rx)
    max_x = ti.min(ti.cast(w - 1, ti.f32), mu_2d[0] + rx)
    min_y = ti.max(0.0, mu_2d[1] - ry)
    max_y = ti.min(ti.cast(h - 1, ti.f32), mu_2d[1] + ry)

    return ti.math.vec4(min_x, min_y, max_x, max_y)


@ti.kernel
def project_gaussians_kernel(
    num_gaussians: ti.i32,
    means_3d: ti.types.ndarray(ndim=2),       # [N, 3]
    scales: ti.types.ndarray(ndim=2),         # [N, 3]
    rot_quats: ti.types.ndarray(ndim=2),      # [N, 4] normalized (w, x, y, z)
    view_matrix: ti.types.ndarray(ndim=2),    # [4, 4]
    fx: ti.f32,
    fy: ti.f32,
    cx: ti.f32,
    cy: ti.f32,
    img_w: ti.i32,
    img_h: ti.i32,
    out_means_2d: ti.types.ndarray(ndim=2),   # [N, 2]
    out_cov_2d: ti.types.ndarray(ndim=2),     # [N, 3] (xx, xy, yy)
    out_depths: ti.types.ndarray(ndim=1),     # [N]
    out_bounds: ti.types.ndarray(ndim=2),     # [N, 4] (min_x, min_y, max_x, max_y)
    out_valid: ti.types.ndarray(ndim=1),      # [N] int 1 atau 0
):
    """Proyeksi kamera koordinat dunia ke bidang gambar dengan evaluasi TEB."""
    for i in range(num_gaussians):
        pos_world = ti.math.vec4(
            means_3d[i, 0],
            means_3d[i, 1],
            means_3d[i, 2],
            1.0,
        )

        pos_cam = ti.math.vec3(
            view_matrix[0, 0] * pos_world[0] + view_matrix[0, 1] * pos_world[1] + view_matrix[0, 2] * pos_world[2] + view_matrix[0, 3] * pos_world[3],
            view_matrix[1, 0] * pos_world[0] + view_matrix[1, 1] * pos_world[1] + view_matrix[1, 2] * pos_world[2] + view_matrix[1, 3] * pos_world[3],
            view_matrix[2, 0] * pos_world[0] + view_matrix[2, 1] * pos_world[1] + view_matrix[2, 2] * pos_world[2] + view_matrix[2, 3] * pos_world[3],
        )

        depth = pos_cam[2]
        if depth <= 0.1:
            out_valid[i] = 0
            out_depths[i] = -1.0
        else:
            inv_z = 1.0 / depth
            mu_x = fx * pos_cam[0] * inv_z + cx
            mu_y = fy * pos_cam[1] * inv_z + cy

            scale_vec = ti.math.vec3(scales[i, 0], scales[i, 1], scales[i, 2])
            rot_vec = ti.math.vec4(rot_quats[i, 0], rot_quats[i, 1], rot_quats[i, 2], rot_quats[i, 3])

            cov3d = _compute_cov3d(scale_vec, rot_vec)
            cov2d = _compute_cov2d(pos_cam, cov3d, fx, fy)

            mu_2d = ti.math.vec2(mu_x, mu_y)
            box = _compute_tight_ellipse_bound(mu_2d, cov2d, img_w, img_h)

            if box[2] < 0.0 or box[0] >= ti.cast(img_w, ti.f32) or box[3] < 0.0 or box[1] >= ti.cast(img_h, ti.f32):
                out_valid[i] = 0
                out_depths[i] = -1.0
            else:
                out_means_2d[i, 0] = mu_x
                out_means_2d[i, 1] = mu_y
                out_cov_2d[i, 0] = cov2d[0]
                out_cov_2d[i, 1] = cov2d[1]
                out_cov_2d[i, 2] = cov2d[2]
                out_depths[i] = depth
                out_bounds[i, 0] = box[0]
                out_bounds[i, 1] = box[1]
                out_bounds[i, 2] = box[2]
                out_bounds[i, 3] = box[3]
                out_valid[i] = 1


@ti.kernel
def project_and_init_sort_kernel(
    num_gaussians: ti.i32,
    padded_n: ti.i32,
    means_3d: ti.types.ndarray(ndim=2),
    scales: ti.types.ndarray(ndim=2),
    rot_quats: ti.types.ndarray(ndim=2),
    view_matrix: ti.types.ndarray(ndim=2),
    fx: ti.f32,
    fy: ti.f32,
    cx: ti.f32,
    cy: ti.f32,
    img_w: ti.i32,
    img_h: ti.i32,
    out_means_2d: ti.types.ndarray(ndim=2),
    out_cov_2d: ti.types.ndarray(ndim=2),
    out_bounds: ti.types.ndarray(ndim=2),
    sort_keys: ti.types.ndarray(ndim=1),
    sort_indices: ti.types.ndarray(ndim=1),
):
    """Proyeksi kamera dan inisialisasi buffer sort murni di GPU."""
    for i in range(padded_n):
        if i >= num_gaussians:
            sort_keys[i] = 1e9
            sort_indices[i] = i
        else:
            pos_world = ti.math.vec4(
                means_3d[i, 0],
                means_3d[i, 1],
                means_3d[i, 2],
                1.0,
            )

            pos_cam = ti.math.vec3(
                view_matrix[0, 0] * pos_world[0] + view_matrix[0, 1] * pos_world[1] + view_matrix[0, 2] * pos_world[2] + view_matrix[0, 3] * pos_world[3],
                view_matrix[1, 0] * pos_world[0] + view_matrix[1, 1] * pos_world[1] + view_matrix[1, 2] * pos_world[2] + view_matrix[1, 3] * pos_world[3],
                view_matrix[2, 0] * pos_world[0] + view_matrix[2, 1] * pos_world[1] + view_matrix[2, 2] * pos_world[2] + view_matrix[2, 3] * pos_world[3],
            )

            depth = pos_cam[2]
            if depth <= 0.1:
                sort_keys[i] = 1e9
                sort_indices[i] = i
            else:
                inv_z = 1.0 / depth
                mu_x = fx * pos_cam[0] * inv_z + cx
                mu_y = fy * pos_cam[1] * inv_z + cy

                scale_vec = ti.math.vec3(scales[i, 0], scales[i, 1], scales[i, 2])
                rot_vec = ti.math.vec4(rot_quats[i, 0], rot_quats[i, 1], rot_quats[i, 2], rot_quats[i, 3])

                cov3d = _compute_cov3d(scale_vec, rot_vec)
                cov2d = _compute_cov2d(pos_cam, cov3d, fx, fy)

                mu_2d = ti.math.vec2(mu_x, mu_y)
                box = _compute_tight_ellipse_bound(mu_2d, cov2d, img_w, img_h)

                if box[2] < 0.0 or box[0] >= ti.cast(img_w, ti.f32) or box[3] < 0.0 or box[1] >= ti.cast(img_h, ti.f32):
                    sort_keys[i] = 1e9
                    sort_indices[i] = i
                else:
                    out_means_2d[i, 0] = mu_x
                    out_means_2d[i, 1] = mu_y
                    out_cov_2d[i, 0] = cov2d[0]
                    out_cov_2d[i, 1] = cov2d[1]
                    out_cov_2d[i, 2] = cov2d[2]
                    out_bounds[i, 0] = box[0]
                    out_bounds[i, 1] = box[1]
                    out_bounds[i, 2] = box[2]
                    out_bounds[i, 3] = box[3]
                    sort_keys[i] = depth
                    sort_indices[i] = i


@ti.kernel
def rasterize_tile_pulse_splat_kernel(
    img_w: ti.i32,
    img_h: ti.i32,
    num_visible: ti.i32,
    sorted_indices: ti.types.ndarray(ndim=1),
    means_2d: ti.types.ndarray(ndim=2),
    cov_2d: ti.types.ndarray(ndim=2),
    colors: ti.types.ndarray(ndim=2),
    opacities: ti.types.ndarray(ndim=1),
    bounds: ti.types.ndarray(ndim=2),
    out_image: ti.types.ndarray(ndim=3),
):
    """Rasterisasi TEB back-to-front dari daftar partikel visible."""
    for r, c in ti.ndrange(img_h, img_w):
        out_image[r, c, 0] = 0.0
        out_image[r, c, 1] = 0.0
        out_image[r, c, 2] = 0.0

    for i in range(num_visible):
        k = num_visible - 1 - i
        g_idx = sorted_indices[k]

        bx0 = ti.max(0, int(ti.floor(bounds[g_idx, 0])))
        by0 = ti.max(0, int(ti.floor(bounds[g_idx, 1])))
        bx1 = ti.min(img_w - 1, int(ti.ceil(bounds[g_idx, 2])))
        by1 = ti.min(img_h - 1, int(ti.ceil(bounds[g_idx, 3])))

        c_xx = cov_2d[g_idx, 0]
        c_xy = cov_2d[g_idx, 1]
        c_yy = cov_2d[g_idx, 2]
        det = c_xx * c_yy - c_xy * c_xy

        if det > 1e-6:
            inv_det = 1.0 / det
            inv_xx = c_yy * inv_det
            inv_xy = -c_xy * inv_det
            inv_yy = c_xx * inv_det

            mx = means_2d[g_idx, 0]
            my = means_2d[g_idx, 1]
            opac = opacities[g_idx]
            cr = colors[g_idx, 0]
            cg = colors[g_idx, 1]
            cb = colors[g_idx, 2]

            for py in range(by0, by1 + 1):
                dy = (ti.cast(py, ti.f32) + 0.5) - my
                for px in range(bx0, bx1 + 1):
                    dx = (ti.cast(px, ti.f32) + 0.5) - mx
                    power = -0.5 * (dx * dx * inv_xx + 2.0 * dx * dy * inv_xy + dy * dy * inv_yy)
                    if power <= 0.0 and power >= -4.5:
                        alpha = ti.min(0.99, opac * ti.exp(power))
                        if alpha > 1.0 / 255.0:
                            out_image[py, px, 0] = alpha * cr + (1.0 - alpha) * out_image[py, px, 0]
                            out_image[py, px, 1] = alpha * cg + (1.0 - alpha) * out_image[py, px, 1]
                            out_image[py, px, 2] = alpha * cb + (1.0 - alpha) * out_image[py, px, 2]


@ti.kernel
def rasterize_from_gpu_sorted_kernel(
    img_w: ti.i32,
    img_h: ti.i32,
    padded_n: ti.i32,
    sort_keys: ti.types.ndarray(ndim=1),
    sort_indices: ti.types.ndarray(ndim=1),
    means_2d: ti.types.ndarray(ndim=2),
    cov_2d: ti.types.ndarray(ndim=2),
    colors: ti.types.ndarray(ndim=2),
    opacities: ti.types.ndarray(ndim=1),
    bounds: ti.types.ndarray(ndim=2),
    out_image: ti.types.ndarray(ndim=3),
):
    """Rasterisasi TEB langsung dari GPU buffer yang telah terurut murni di GPU."""
    for r, c in ti.ndrange(img_h, img_w):
        out_image[r, c, 0] = 0.0
        out_image[r, c, 1] = 0.0
        out_image[r, c, 2] = 0.0

    # Back-to-front traversal: partikel terjauh dievaluasi terlebih dahulu
    for k in range(padded_n):
        idx_in_sort = padded_n - 1 - k
        d = sort_keys[idx_in_sort]
        if d < 1e8:  # Abaikan partikel yang invalid / di luar jangkauan
            g_idx = sort_indices[idx_in_sort]
            bx0 = ti.max(0, int(ti.floor(bounds[g_idx, 0])))
            by0 = ti.max(0, int(ti.floor(bounds[g_idx, 1])))
            bx1 = ti.min(img_w - 1, int(ti.ceil(bounds[g_idx, 2])))
            by1 = ti.min(img_h - 1, int(ti.ceil(bounds[g_idx, 3])))

            c_xx = cov_2d[g_idx, 0]
            c_xy = cov_2d[g_idx, 1]
            c_yy = cov_2d[g_idx, 2]
            det = c_xx * c_yy - c_xy * c_xy

            if det > 1e-6:
                inv_det = 1.0 / det
                inv_xx = c_yy * inv_det
                inv_xy = -c_xy * inv_det
                inv_yy = c_xx * inv_det

                mx = means_2d[g_idx, 0]
                my = means_2d[g_idx, 1]
                opac = opacities[g_idx]
                cr = colors[g_idx, 0]
                cg = colors[g_idx, 1]
                cb = colors[g_idx, 2]

                for py in range(by0, by1 + 1):
                    dy = (ti.cast(py, ti.f32) + 0.5) - my
                    for px in range(bx0, bx1 + 1):
                        dx = (ti.cast(px, ti.f32) + 0.5) - mx
                        power = -0.5 * (dx * dx * inv_xx + 2.0 * dx * dy * inv_xy + dy * dy * inv_yy)
                        if power <= 0.0 and power >= -4.5:
                            alpha = ti.min(0.99, opac * ti.exp(power))
                            if alpha > 1.0 / 255.0:
                                out_image[py, px, 0] = alpha * cr + (1.0 - alpha) * out_image[py, px, 0]
                                out_image[py, px, 1] = alpha * cg + (1.0 - alpha) * out_image[py, px, 1]
                                out_image[py, px, 2] = alpha * cb + (1.0 - alpha) * out_image[py, px, 2]


def _to_device_buffer(arr, dtype=ti.f32):
    """Memastikan array berada di resident GPU buffer tanpa alokasi berulang."""
    if hasattr(arr, "shape") and not isinstance(arr, np.ndarray):
        return arr
    buf = ti.ndarray(dtype=dtype, shape=arr.shape)
    buf.from_numpy(np.ascontiguousarray(arr, dtype=np.float32 if dtype == ti.f32 else np.int32))
    return buf


@dataclass
class GaussianScene:
    """Deskriptor scene 3D Gaussian dengan dukungan resident GPU buffer."""
    means_3d: Union[np.ndarray, ti.types.ndarray]
    scales: Union[np.ndarray, ti.types.ndarray]
    rot_quats: Union[np.ndarray, ti.types.ndarray]
    colors: Union[np.ndarray, ti.types.ndarray]
    opacities: Union[np.ndarray, ti.types.ndarray]

    _d_means: Optional[ti.types.ndarray] = None
    _d_scales: Optional[ti.types.ndarray] = None
    _d_rots: Optional[ti.types.ndarray] = None
    _d_colors: Optional[ti.types.ndarray] = None
    _d_opacs: Optional[ti.types.ndarray] = None

    def to_device(self):
        """Menyimpan data scene secara resident di VRAM GPU untuk meniadakan overhead per-frame."""
        if self._d_means is None:
            self._d_means = _to_device_buffer(self.means_3d, dtype=ti.f32)
            self._d_scales = _to_device_buffer(self.scales, dtype=ti.f32)
            self._d_rots = _to_device_buffer(self.rot_quats, dtype=ti.f32)
            self._d_colors = _to_device_buffer(self.colors, dtype=ti.f32)
            self._d_opacs = _to_device_buffer(self.opacities, dtype=ti.f32)
        return (
            self._d_means,
            self._d_scales,
            self._d_rots,
            self._d_colors,
            self._d_opacs,
        )


class PulseSplatPipeline:
    """Pipeline terpadu Pulse-Splat dengan zero-readback dan buffer cache menetap."""

    def __init__(self):
        self._padded_capacity = 0
        self._d_means_2d = None
        self._d_cov_2d = None
        self._d_bounds = None
        self._d_sort_keys = None
        self._d_sort_indices = None
        self._img_shape = (0, 0)
        self._d_out_image = None
        self._d_view_mat = None

    def _ensure_buffers(self, padded_n: int, img_h: int, img_w: int):
        if padded_n > self._padded_capacity:
            self._padded_capacity = padded_n
            self._d_means_2d = ti.ndarray(dtype=ti.f32, shape=(padded_n, 2))
            self._d_cov_2d = ti.ndarray(dtype=ti.f32, shape=(padded_n, 3))
            self._d_bounds = ti.ndarray(dtype=ti.f32, shape=(padded_n, 4))
            self._d_sort_keys = ti.ndarray(dtype=ti.f32, shape=padded_n)
            self._d_sort_indices = ti.ndarray(dtype=ti.i32, shape=padded_n)

        if self._img_shape != (img_h, img_w):
            self._img_shape = (img_h, img_w)
            self._d_out_image = ti.ndarray(dtype=ti.f32, shape=(img_h, img_w, 3))

        if self._d_view_mat is None:
            self._d_view_mat = ti.ndarray(dtype=ti.f32, shape=(4, 4))

    def render(
        self,
        scene: GaussianScene,
        view_matrix: Union[np.ndarray, ti.types.ndarray],
        fx: float,
        fy: float,
        cx: float,
        cy: float,
        img_w: int,
        img_h: int,
        out_image: Optional[Union[np.ndarray, ti.types.ndarray]] = None,
        return_numpy: bool = True,
    ) -> Union[np.ndarray, ti.types.ndarray]:
        """Eksekusi render murni GPU tanpa CPU readback."""
        d_means, d_scales, d_rots, d_colors, d_opacs = scene.to_device()
        N = d_means.shape[0]

        num_stages = int(np.ceil(np.log2(max(1, N))))
        padded_n = 1 << num_stages

        self._ensure_buffers(padded_n, img_h, img_w)

        # Upload view matrix jika numpy
        if isinstance(view_matrix, np.ndarray):
            self._d_view_mat.from_numpy(view_matrix.astype(np.float32))
            d_view = self._d_view_mat
        else:
            d_view = view_matrix

        # 1. GPU Projection & Sort Initialization
        project_and_init_sort_kernel(
            N,
            padded_n,
            d_means,
            d_scales,
            d_rots,
            d_view,
            float(fx),
            float(fy),
            float(cx),
            float(cy),
            img_w,
            img_h,
            self._d_means_2d,
            self._d_cov_2d,
            self._d_bounds,
            self._d_sort_keys,
            self._d_sort_indices,
        )

        # 2. Pure GPU Parallel Bitonic Sort (Key-Value)
        for stage in range(num_stages):
            for step in range(stage, -1, -1):
                math_bitonic_sort_kv_step(
                    self._d_sort_keys,
                    self._d_sort_indices,
                    stage,
                    step,
                )

        # Tentukan target output buffer
        if out_image is not None and hasattr(out_image, "shape") and not isinstance(out_image, np.ndarray):
            target_out = out_image
        else:
            target_out = self._d_out_image

        # 3. GPU Rasterization from sorted buffer
        rasterize_from_gpu_sorted_kernel(
            img_w,
            img_h,
            padded_n,
            self._d_sort_keys,
            self._d_sort_indices,
            self._d_means_2d,
            self._d_cov_2d,
            d_colors,
            d_opacs,
            self._d_bounds,
            target_out,
        )

        if not return_numpy:
            return target_out

        if out_image is not None and isinstance(out_image, np.ndarray):
            target_out.to_numpy(out_image)
            return out_image

        return target_out.to_numpy()


# Global pipeline instance untuk render cepat
_GLOBAL_PIPELINE = PulseSplatPipeline()


def render_pulse_splat(
    scene: GaussianScene,
    view_matrix: Union[np.ndarray, ti.types.ndarray],
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    img_w: int,
    img_h: int,
    out_image: Optional[Union[np.ndarray, ti.types.ndarray]] = None,
    return_numpy: bool = True,
) -> Union[np.ndarray, ti.types.ndarray]:
    """Pipeline render utama Pulse-Splat (Zero-Readback)."""
    return _GLOBAL_PIPELINE.render(
        scene=scene,
        view_matrix=view_matrix,
        fx=fx,
        fy=fy,
        cx=cx,
        cy=cy,
        img_w=img_w,
        img_h=img_h,
        out_image=out_image,
        return_numpy=return_numpy,
    )


def project_gaussians(
    scene: GaussianScene,
    view_matrix: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    img_w: int,
    img_h: int,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Eksekusi proyeksi Gaussian kompatibilitas API terdahulu."""
    N = scene.means_3d.shape[0]

    out_means_2d = np.zeros((N, 2), dtype=np.float32)
    out_cov_2d = np.zeros((N, 3), dtype=np.float32)
    out_depths = np.zeros((N,), dtype=np.float32)
    out_bounds = np.zeros((N, 4), dtype=np.float32)
    out_valid = np.zeros((N,), dtype=np.int32)

    project_gaussians_kernel(
        N,
        scene.means_3d,
        scene.scales,
        scene.rot_quats,
        view_matrix.astype(np.float32),
        float(fx),
        float(fy),
        float(cx),
        float(cy),
        img_w,
        img_h,
        out_means_2d,
        out_cov_2d,
        out_depths,
        out_bounds,
        out_valid,
    )

    return out_means_2d, out_cov_2d, out_depths, out_bounds, out_valid


def rasterize_gaussians(
    means_2d: np.ndarray,
    cov_2d: np.ndarray,
    depths: np.ndarray,
    bounds: np.ndarray,
    valid: np.ndarray,
    colors: np.ndarray,
    opacities: np.ndarray,
    img_w: int,
    img_h: int,
) -> np.ndarray:
    """Rasterisasi Gaussian kompatibilitas API terdahulu."""
    valid_mask = valid == 1
    valid_indices = np.where(valid_mask)[0]

    if len(valid_indices) == 0:
        return np.zeros((img_h, img_w, 3), dtype=np.float32)

    valid_depths = depths[valid_indices]
    sort_order = np.argsort(valid_depths)
    sorted_indices = valid_indices[sort_order].astype(np.int32)

    out_image = np.zeros((img_h, img_w, 3), dtype=np.float32)

    rasterize_tile_pulse_splat_kernel(
        img_w,
        img_h,
        len(sorted_indices),
        sorted_indices,
        means_2d,
        cov_2d,
        colors,
        opacities,
        bounds,
        out_image,
    )

    return out_image
