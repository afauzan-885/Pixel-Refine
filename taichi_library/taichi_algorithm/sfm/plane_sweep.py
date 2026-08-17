"""
Plane Sweep Stereo — Taichi GPU
================================
GPU-accelerated plane sweep stereo untuk dense depth estimation.

Algorithm:
  1. Define depth hypothesis planes [d_min ... d_max] (linear atau log spacing)
  2. Untuk setiap depth d dan setiap pixel (x,y) di reference image:
     a. Compute homography H_d yang meng-warps reference plane ke target view
     b. Sample warped coordinates di target image (bilinear)
     c. Compute matching cost (NCC window-based) antara reference patch dan warped patch
  3. Per pixel, pilih depth d* dengan cost terbaik (winner-take-all)
  4. Optional: refine depth map dengan bilateral filter

Support:
  - Multiple target views (multi-view stereo)
  - NCC cost metric (robust terhadap brightness changes)
  - Bilateral depth refinement
  - Confidence output (peak cost vs second-best)

Hybrid precision: Float32 compute, Float32 output.
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
except ImportError:
    pass


def _ensure_taichi_runtime() -> str:
    """Initialise the explicit Taichi JIT backend without changing AOT mode."""
    if not TAICHI_AVAILABLE:
        raise RuntimeError(
            "backend='taichi' requires AOT_MODE=0 and an installed Taichi runtime"
        )
    runtime = ti.lang.impl.get_runtime()
    if getattr(runtime, "prog", None) is None:
        ti.init(arch=ti.cpu)
    try:
        arch = str(ti.lang.impl.get_runtime().prog.config().arch).lower()
    except Exception:
        arch = "unknown"
    return "taichi-cpu-jit" if "x64" in arch or "cpu" in arch else f"taichi-{arch}-jit"


def _resolve_backend(value: str | None) -> tuple[str, bool]:
    """Return the selected leaf and whether the JIT kernels should run."""
    backend = "auto" if value is None else str(value).strip().lower()
    if backend not in {"auto", "numpy", "taichi", "aot"}:
        raise ValueError("backend must be one of 'auto', 'numpy', 'taichi', or 'aot'")
    if backend == "auto":
        return ("taichi", True) if TAICHI_AVAILABLE else ("numpy", False)
    if backend == "taichi":
        _ensure_taichi_runtime()
        return "taichi", True
    return backend, False


# =============================================================================
# TAICHI KERNELS
# =============================================================================

if TAICHI_AVAILABLE:

    @ti.kernel
    def warp_and_compute_ncc_kernel(
        ref_img: ti.types.ndarray(ti.f32, ndim=2),       # (H, W)
        target_img: ti.types.ndarray(ti.f32, ndim=2),     # (H, W)
        H_inv: ti.types.ndarray(ti.f32, ndim=2),          # (3, 3) inverse homography
        depth: ti.f32,
        n_hypotheses: int,
        h: int,
        w: int,
        patch_radius: int,
        cost_out: ti.types.ndarray(ti.f32, ndim=2),       # (H, W) output cost
    ):
        """Compute NCC cost untuk satu depth hypothesis.
        Warp target image ke reference view menggunakan homography, lalu hitung NCC per patch."""
        for yi, xi in ti.ndrange(h, w):
            # Warp (xi, yi) ke target coordinates menggunakan H_inv
            fx = H_inv[0, 0] * xi + H_inv[0, 1] * yi + H_inv[0, 2]
            fy = H_inv[1, 0] * xi + H_inv[1, 1] * yi + H_inv[1, 2]
            fw = H_inv[2, 0] * xi + H_inv[2, 1] * yi + H_inv[2, 2]

            if ti.abs(fw) < 1e-10:
                cost_out[yi, xi] = 1.0  # max cost
                continue

            sx = fx / fw
            sy = fy / fw

            # NCC computation over patch
            sum_ref = ti.f32(0.0)
            sum_target = ti.f32(0.0)
            sum_ref2 = ti.f32(0.0)
            sum_target2 = ti.f32(0.0)
            sum_cross = ti.f32(0.0)
            count = ti.f32(0.0)

            for dy, dx in ti.static(ti.ndrange(
                lambda: (-patch_radius, patch_radius + 1),
                lambda: (-patch_radius, patch_radius + 1)
            )):
                ry = yi + dy
                rx = xi + dx
                if ry >= 0 and ry < h and rx >= 0 and rx < w:
                    # Sample target at warped position
                    ty = sy + dy
                    tx = sx + dx
                    tye = ti.cast(ty, ti.i32)
                    txe = ti.cast(tx, ti.i32)
                    if tye >= 0 and tye < h - 1 and txe >= 0 and txe < w - 1:
                        # Bilinear interpolation
                        wy = ty - ti.cast(tye, ti.f32)
                        wx = tx - ti.cast(txe, ti.f32)
                        v00 = target_img[tye, txe]
                        v01 = target_img[tye, txe + 1]
                        v10 = target_img[tye + 1, txe]
                        v11 = target_img[tye + 1, txe + 1]
                        target_val = (1.0 - wy) * (1.0 - wx) * v00 + \
                                     (1.0 - wy) * wx * v01 + \
                                     wy * (1.0 - wx) * v10 + \
                                     wy * wx * v11

                        ref_val = ref_img[ry, rx]
                        sum_ref += ref_val
                        sum_target += target_val
                        sum_ref2 += ref_val * ref_val
                        sum_target2 += target_val * target_val
                        sum_cross += ref_val * target_val
                        count += 1.0

            if count > 1.0:
                mean_ref = sum_ref / count
                mean_target = sum_target / count
                var_ref = sum_ref2 / count - mean_ref * mean_ref
                var_target = sum_target2 / count - mean_target * mean_target

                std_ref = ti.sqrt(ti.max(var_ref, 1e-10))
                std_target = ti.sqrt(ti.max(var_target, 1e-10))

                ncc_val = (sum_cross / count - mean_ref * mean_target) / (std_ref * std_target)
                cost_out[yi, xi] = 1.0 - ti.max(0.0, ncc_val)  # Convert to cost (lower is better)
            else:
                cost_out[yi, xi] = 1.0

    @ti.kernel
    def sweep_all_depths_kernel(
        ref_img: ti.types.ndarray(ti.f32, ndim=2),
        target_img: ti.types.ndarray(ti.f32, ndim=2),
        K_ref: ti.types.ndarray(ti.f32, ndim=2),     # (3,3) intrinsics ref
        K_target: ti.types.ndarray(ti.f32, ndim=2),   # (3,3) intrinsics target
        R_rel: ti.types.ndarray(ti.f32, ndim=2),      # (3,3) relative rotation
        t_rel: ti.types.ndarray(ti.f32, ndim=1),      # (3,) relative translation
        depth_hypotheses: ti.types.ndarray(ti.f32, ndim=1),  # (N_d,)
        n_depths: int,
        h: int,
        w: int,
        patch_radius: ti.i32,
        cost_volume: ti.types.ndarray(ti.f32, ndim=3),  # (N_d, H, W)
    ):
        """Sweep semua depth hypotheses dan isi cost volume."""
        for di, yi, xi in ti.ndrange(n_depths, h, w):
            d = depth_hypotheses[di]

            # Compute homography: H = K_target * (R - t * n^T / d) * K_ref^-1
            # For fronto-parallel plane at depth d: n = [0,0,1]
            # H = K_target * (R - t * [0,0,1/d]) * K_ref^-1

            # Precompute K_ref^-1 (assume standard pinhole)
            fx_r = K_ref[0, 0]
            fy_r = K_ref[1, 1]
            cx_r = K_ref[0, 2]
            cy_r = K_ref[1, 2]

            # Compute H for this depth
            # H = K_target * R * K_ref^-1 - K_target * t * [0,0,1] / d * K_ref^-1
            # Simplified: project using camera geometry

            # Reference pixel -> normalized coords
            nx = (xi - cx_r) / fx_r
            ny = (yi - cy_r) / fy_r

            # 3D point on plane at depth d
            X = nx * d
            Y = ny * d
            Z = d

            # Project to target camera
            # P_target = R_rel * [X,Y,Z]^T + t_rel
            Px = R_rel[0, 0] * X + R_rel[0, 1] * Y + R_rel[0, 2] * Z + t_rel[0]
            Py = R_rel[1, 0] * X + R_rel[1, 1] * Y + R_rel[1, 2] * Z + t_rel[1]
            Pz = R_rel[2, 0] * X + R_rel[2, 1] * Y + R_rel[2, 2] * Z + t_rel[2]

            if Pz < 1e-6:
                cost_volume[di, yi, xi] = 1.0
                continue

            # Target pixel
            tx = K_target[0, 0] * Px / Pz + K_target[0, 2]
            ty = K_target[1, 1] * Py / Pz + K_target[1, 2]

            # NCC patch matching
            sum_ref = ti.f32(0.0)
            sum_target = ti.f32(0.0)
            sum_ref2 = ti.f32(0.0)
            sum_target2 = ti.f32(0.0)
            sum_cross = ti.f32(0.0)
            cnt = ti.f32(0.0)

            for dy in range(-patch_radius, patch_radius + 1):
                for dx in range(-patch_radius, patch_radius + 1):
                    ry = yi + dy
                    rx = xi + dx
                    if ry >= 0 and ry < h and rx >= 0 and rx < w:
                        sty = ty + dy
                        stx = tx + dx
                        stye = ti.cast(sty, ti.i32)
                        stxe = ti.cast(stx, ti.i32)
                        if stye >= 1 and stye < h - 2 and stxe >= 1 and stxe < w - 2:
                            wy = sty - ti.cast(stye, ti.f32)
                            wx = stx - ti.cast(stxe, ti.f32)
                            v00 = target_img[stye, stxe]
                            v01 = target_img[stye, stxe + 1]
                            v10 = target_img[stye + 1, stxe]
                            v11 = target_img[stye + 1, stxe + 1]
                            tval = (1.0 - wy) * (1.0 - wx) * v00 + \
                                   (1.0 - wy) * wx * v01 + \
                                   wy * (1.0 - wx) * v10 + \
                                   wy * wx * v11
                            rval = ref_img[ry, rx]
                            sum_ref += rval
                            sum_target += tval
                            sum_ref2 += rval * rval
                            sum_target2 += tval * tval
                            sum_cross += rval * tval
                            cnt += 1.0

            if cnt > 1.0:
                mean_r = sum_ref / cnt
                mean_t = sum_target / cnt
                var_r = sum_ref2 / cnt - mean_r * mean_r
                var_t = sum_target2 / cnt - mean_t * mean_t
                std_r = ti.sqrt(ti.max(var_r, 1e-10))
                std_t = ti.sqrt(ti.max(var_t, 1e-10))
                ncc = (sum_cross / cnt - mean_r * mean_t) / (std_r * std_t)
                cost_volume[di, yi, xi] = 1.0 - ti.max(0.0, ncc)
            else:
                cost_volume[di, yi, xi] = 1.0

    @ti.kernel
    def winner_take_all_kernel(
        cost_volume: ti.types.ndarray(ti.f32, ndim=3),  # (N_d, H, W)
        depth_hypotheses: ti.types.ndarray(ti.f32, ndim=1),
        n_depths: int,
        h: int,
        w: int,
        depth_out: ti.types.ndarray(ti.f32, ndim=2),    # (H, W)
        confidence_out: ti.types.ndarray(ti.f32, ndim=2),  # (H, W)
    ):
        """Per pixel, pilih depth dengan cost terbaik dan hitung confidence."""
        for yi, xi in ti.ndrange(h, w):
            best_cost = ti.f32(1e30)
            second_cost = ti.f32(1e30)
            best_depth = ti.f32(0.0)

            for di in range(n_depths):
                c = cost_volume[di, yi, xi]
                if c < best_cost:
                    second_cost = best_cost
                    best_cost = c
                    best_depth = depth_hypotheses[di]
                elif c < second_cost:
                    second_cost = c

            depth_out[yi, xi] = best_depth
            # Confidence = gap between best and second best
            confidence_out[yi, xi] = second_cost - best_cost

    @ti.kernel
    def bilateral_refine_depth_kernel(
        depth_in: ti.types.ndarray(ti.f32, ndim=2),
        guide_img: ti.types.ndarray(ti.f32, ndim=2),
        h: int,
        w: int,
        sigma_s: ti.f32,
        sigma_r: ti.f32,
        depth_out: ti.types.ndarray(ti.f32, ndim=2),
    ):
        """Bilateral filter pada depth map menggunakan guide image.
        Mempertahankan edge dari guide image sambil menghaluskan depth."""
        for yi, xi in ti.ndrange(h, w):
            sum_val = ti.f32(0.0)
            sum_w = ti.f32(0.0)
            center_guide = guide_img[yi, xi]

            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    ny = yi + dy
                    nx = xi + dx
                    if ny >= 0 and ny < h and nx >= 0 and nx < w:
                        spatial_w = ti.exp(-ti.cast(dy * dy + dx * dx, ti.f32) / (2.0 * sigma_s * sigma_s))
                        guide_diff = guide_img[ny, nx] - center_guide
                        range_w = ti.exp(-guide_diff * guide_diff / (2.0 * sigma_r * sigma_r))
                        weight = spatial_w * range_w
                        sum_val += weight * depth_in[ny, nx]
                        sum_w += weight

            if sum_w > 1e-10:
                depth_out[yi, xi] = sum_val / sum_w
            else:
                depth_out[yi, xi] = depth_in[yi, xi]


# =============================================================================
# PYTHON API
# =============================================================================

def plane_sweep_stereo(
    ref_img,
    target_img,
    K_ref,
    K_target,
    R_rel,
    t_rel,
    depth_min=0.1,
    depth_max=100.0,
    n_depths=64,
    patch_radius=3,
    depth_spacing="linear",
    backend="auto",
):
    """
    Plane Sweep Stereo untuk dense depth estimation.

    Args:
        ref_img: (H, W) float32 grayscale reference image
        target_img: (H, W) float32 grayscale target image
        K_ref: (3, 3) float32 camera intrinsic matrix reference
        K_target: (3, 3) float32 camera intrinsic matrix target
        R_rel: (3, 3) float32 relative rotation (R_target @ R_ref.T)
        t_rel: (3,) float32 relative translation
        depth_min: minimum depth hypothesis
        depth_max: maximum depth hypothesis
        n_depths: jumlah depth hypotheses
        patch_radius: radius NCC patch (default 3 = 7x7)
        depth_spacing: "linear" atau "log"

    Returns:
        depth_map: (H, W) float32 estimated depth
        confidence: (H, W) float32 confidence map (higher = more confident)
    """
    ref_img = np.ascontiguousarray(ref_img.astype(np.float32))
    target_img = np.ascontiguousarray(target_img.astype(np.float32))
    K_ref = np.ascontiguousarray(K_ref.astype(np.float32))
    K_target = np.ascontiguousarray(K_target.astype(np.float32))
    R_rel = np.ascontiguousarray(R_rel.astype(np.float32))
    t_rel = np.ascontiguousarray(t_rel.astype(np.float32))

    h, w = ref_img.shape[:2]

    # Generate depth hypotheses
    if depth_spacing == "log":
        depth_hypotheses = np.logspace(
            np.log10(max(depth_min, 0.01)),
            np.log10(depth_max),
            n_depths,
            dtype=np.float32,
        )
    else:
        depth_hypotheses = np.linspace(depth_min, depth_max, n_depths, dtype=np.float32)

    selected_backend, use_taichi = _resolve_backend(backend)

    if selected_backend == "aot":
        try:
            from ..aot_api.research import sfm_sweep_depths_aot, sfm_winner_take_all_aot

            cost_volume = sfm_sweep_depths_aot(
                ref_img, target_img, K_ref, K_target, R_rel, t_rel,
                depth_hypotheses, patch_radius=int(patch_radius),
            )
            return sfm_winner_take_all_aot(cost_volume, depth_hypotheses)
        except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
            raise NotImplementedError(
                "plane-sweep AOT requires target-qualified sfm_stereo artifacts"
            ) from exc

    if not use_taichi:
        return _plane_sweep_numpy(
            ref_img, target_img, K_ref, K_target, R_rel, t_rel,
            depth_hypotheses, patch_radius,
        )

    # GPU path: sweep all depths
    cost_volume = np.zeros((n_depths, h, w), dtype=np.float32)

    sweep_all_depths_kernel(
        ref_img, target_img, K_ref, K_target, R_rel, t_rel,
        depth_hypotheses, n_depths, h, w, patch_radius, cost_volume,
    )

    # Winner-take-all
    depth_map = np.zeros((h, w), dtype=np.float32)
    confidence = np.zeros((h, w), dtype=np.float32)
    winner_take_all_kernel(
        cost_volume, depth_hypotheses, n_depths, h, w, depth_map, confidence,
    )

    # Bilateral refinement
    depth_refined = np.zeros_like(depth_map)
    bilateral_refine_depth_kernel(
        depth_map, ref_img, h, w, 5.0, 0.1, depth_refined,
    )

    return depth_refined, confidence


def multi_view_plane_sweep(
    ref_img,
    target_images,
    K_ref,
    K_targets,
    R_rels,
    t_rels,
    depth_min=0.1,
    depth_max=100.0,
    n_depths=64,
    patch_radius=3,
    backend="auto",
):
    """
    Multi-view plane sweep stereo.
    Aggregate cost dari multiple target views sebelum winner-take-all.

    Args:
        ref_img: (H, W) float32 reference image
        target_images: list of (H, W) float32 target images
        K_ref: (3, 3) float32
        K_targets: list of (3, 3) float32
        R_rels: list of (3, 3) float32
        t_rels: list of (3,) float32
        depth_min, depth_max, n_depths, patch_radius: same as above

    Returns:
        depth_map: (H, W) float32
        confidence: (H, W) float32
    """
    ref_img = np.ascontiguousarray(ref_img.astype(np.float32))
    selected_backend, use_taichi = _resolve_backend(backend)
    h, w = ref_img.shape[:2]

    depth_hypotheses = np.linspace(depth_min, depth_max, n_depths, dtype=np.float32)

    # Accumulate cost volume across views
    total_cost_volume = np.zeros((n_depths, h, w), dtype=np.float32)

    for target_img, K_target, R_rel, t_rel in zip(
        target_images, K_targets, R_rels, t_rels
    ):
        target_img = np.ascontiguousarray(target_img.astype(np.float32))
        K_target = np.ascontiguousarray(K_target.astype(np.float32))
        R_rel = np.ascontiguousarray(R_rel.astype(np.float32))
        t_rel = np.ascontiguousarray(t_rel.astype(np.float32))

        cost_volume = np.zeros((n_depths, h, w), dtype=np.float32)

        if selected_backend == "aot":
            try:
                from ..aot_api.research import sfm_sweep_depths_aot
                cost_volume = sfm_sweep_depths_aot(
                    ref_img, target_img, K_ref, K_target, R_rel, t_rel,
                    depth_hypotheses, patch_radius=int(patch_radius),
                )
            except (FileNotFoundError, ImportError, KeyError, OSError, RuntimeError) as exc:
                raise NotImplementedError(
                    "multi-view plane-sweep AOT requires target-qualified sfm_stereo artifacts"
                ) from exc
        elif use_taichi:
            sweep_all_depths_kernel(
                ref_img, target_img, K_ref, K_target, R_rel, t_rel,
                depth_hypotheses, n_depths, h, w, patch_radius, cost_volume,
            )
        else:
            # Numpy fallback per depth
            for di, d in enumerate(depth_hypotheses):
                cost_volume[di] = _sweep_single_depth_numpy(
                    ref_img, target_img, K_ref, K_target, R_rel, t_rel, d, patch_radius
                )

        total_cost_volume += cost_volume

    # Average across views
    total_cost_volume /= max(len(target_images), 1)

    # Winner-take-all
    depth_map = np.zeros((h, w), dtype=np.float32)
    confidence = np.zeros((h, w), dtype=np.float32)

    if TAICHI_AVAILABLE:
        winner_take_all_kernel(
            total_cost_volume, depth_hypotheses, n_depths, h, w, depth_map, confidence,
        )
        depth_refined = np.zeros_like(depth_map)
        bilateral_refine_depth_kernel(
            depth_map, ref_img, h, w, 5.0, 0.1, depth_refined,
        )
        return depth_refined, confidence
    else:
        best_idx = np.argmin(total_cost_volume, axis=0)
        depth_map = depth_hypotheses[best_idx]
        # Confidence
        sorted_costs = np.sort(total_cost_volume, axis=0)
        confidence = sorted_costs[1] - sorted_costs[0] if n_depths > 1 else np.zeros_like(depth_map)
        return depth_map, confidence


# =============================================================================
# NUMPY FALLBACK
# =============================================================================

def _sweep_single_depth_numpy(ref_img, target_img, K_ref, K_target, R_rel, t_rel, depth, patch_radius):
    """Numpy fallback: compute NCC cost untuk satu depth hypothesis."""
    h, w = ref_img.shape
    cost = np.ones((h, w), dtype=np.float32)

    fx_r, fy_r = K_ref[0, 0], K_ref[1, 1]
    cx_r, cy_r = K_ref[0, 2], K_ref[1, 2]

    # Create meshgrid of reference pixels
    xs, ys = np.meshgrid(np.arange(w), np.arange(h))
    nx = (xs - cx_r) / fx_r
    ny = (ys - cy_r) / fy_r

    # 3D points at depth
    X = nx * depth
    Y = ny * depth
    Z = np.full_like(X, depth)

    # Project to target
    Px = R_rel[0, 0] * X + R_rel[0, 1] * Y + R_rel[0, 2] * Z + t_rel[0]
    Py = R_rel[1, 0] * X + R_rel[1, 1] * Y + R_rel[1, 2] * Z + t_rel[1]
    Pz = R_rel[2, 0] * X + R_rel[2, 1] * Y + R_rel[2, 2] * Z + t_rel[2]

    valid = Pz > 1e-6
    tx = np.where(valid, K_target[0, 0] * Px / Pz + K_target[0, 2], -1)
    ty = np.where(valid, K_target[1, 1] * Py / Pz + K_target[1, 2], -1)

    # Simple NCC per pixel using small patch
    r = patch_radius
    for yi in range(r, h - r):
        for xi in range(r, w - r):
            if not valid[yi, xi]:
                continue
            stx, sty = tx[yi, xi], ty[yi, xi]
            stye, stxe = int(sty), int(stx)
            if stye < r or stye >= h - r or stxe < r or stxe >= w - r:
                continue

            ref_patch = ref_img[yi - r:yi + r + 1, xi - r:xi + r + 1].ravel()
            # Bilinear sample target patch
            dy_arr, dx_arr = np.meshgrid(
                np.arange(-r, r + 1), np.arange(-r, r + 1), indexing='ij'
            )
            sample_y = sty + dy_arr
            sample_x = stx + dx_arr
            sy0 = np.floor(sample_y).astype(int)
            sx0 = np.floor(sample_x).astype(int)
            sy1 = sy0 + 1
            sx1 = sx0 + 1
            wy = sample_y - sy0
            wx = sample_x - sx0

            # Clamp
            sy0c = np.clip(sy0, 0, h - 1)
            sy1c = np.clip(sy1, 0, h - 1)
            sx0c = np.clip(sx0, 0, w - 1)
            sx1c = np.clip(sx1, 0, w - 1)

            target_patch = (
                (1 - wy) * (1 - wx) * target_img[sy0c, sx0c] +
                (1 - wy) * wx * target_img[sy0c, sx1c] +
                wy * (1 - wx) * target_img[sy1c, sx0c] +
                wy * wx * target_img[sy1c, sx1c]
            ).ravel()

            if len(ref_patch) > 1:
                mr = ref_patch.mean()
                mt = target_patch.mean()
                vr = ref_patch.var()
                vt = target_patch.var()
                if vr > 1e-10 and vt > 1e-10:
                    ncc = np.mean((ref_patch - mr) * (target_patch - mt)) / (np.sqrt(vr) * np.sqrt(vt))
                    cost[yi, xi] = 1.0 - max(0.0, ncc)

    return cost


def _plane_sweep_numpy(ref_img, target_img, K_ref, K_target, R_rel, t_rel, depth_hypotheses, patch_radius):
    """Pure numpy fallback for plane sweep."""
    h, w = ref_img.shape
    n_depths = len(depth_hypotheses)
    cost_volume = np.ones((n_depths, h, w), dtype=np.float32)

    for di, d in enumerate(depth_hypotheses):
        cost_volume[di] = _sweep_single_depth_numpy(
            ref_img, target_img, K_ref, K_target, R_rel, t_rel, d, patch_radius
        )

    # Winner-take-all
    best_idx = np.argmin(cost_volume, axis=0)
    depth_map = depth_hypotheses[best_idx]

    sorted_costs = np.sort(cost_volume, axis=0)
    confidence = sorted_costs[1] - sorted_costs[0]

    # Simple bilateral refinement
    from scipy.ndimage import gaussian_filter
    depth_refined = gaussian_filter(depth_map, sigma=1.0)

    return depth_refined, confidence
