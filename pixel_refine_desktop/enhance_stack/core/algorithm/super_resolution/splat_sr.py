# splat_sr.py - Splatting Super Resolution AOT
#
# Production: Re-exports SplatSRAOTEngine from splat_sr_runtime.py (no Taichi dependency).
# Compile: Set AOT_MODE=0 to access JIT kernels and compile .tcm modules.
#
# Iterative back-projection with BTV regularization for multi-frame super resolution.

import os
import sys

_IS_COMPILE_MODE = os.environ.get("AOT_MODE", "1") == "0"

# Always re-export the production runtime class (no Taichi needed)
# When running as __main__ (compile mode), skip this — only the JIT kernels are needed.
if not _IS_COMPILE_MODE:
    from .splat_sr_runtime import SplatSRAOTEngine
    TaichiSplatSR = SplatSRAOTEngine
    # Block Taichi import in production mode to prevent any accidental initialization
    sys.modules["taichi"] = None
else:
    # Compile mode: Taichi is available, no need for runtime class
    SplatSRAOTEngine = None
    TaichiSplatSR = None

# ==============================================================================
# JIT KERNELS & AOT COMPILATION (only available when AOT_MODE=0)
# ==============================================================================
if _IS_COMPILE_MODE:
    import taichi as ti
    import numpy as np
    import shutil
    import zipfile

    # --- 1. HELPER FUNCTIONS (@ti.func) ---

    @ti.func
    def bilinear_sample(img: ti.template(), y: ti.f32, x: ti.f32) -> ti.f32:
        """Bilinear interpolation with boundary clamping."""
        h = img.shape[0]
        w = img.shape[1]
        y_clamped = ti.max(0.0, ti.min(float(h) - 1.0 - 1e-4, y))
        x_clamped = ti.max(0.0, ti.min(float(w) - 1.0 - 1e-4, x))

        y0 = int(ti.floor(y_clamped))
        x0 = int(ti.floor(x_clamped))
        y1 = y0 + 1
        x1 = x0 + 1

        dy = y_clamped - float(y0)
        dx = x_clamped - float(x0)

        val00 = img[y0, x0]
        val01 = img[y0, x1]
        val10 = img[y1, x0]
        val11 = img[y1, x1]

        return (1.0 - dy) * ((1.0 - dx) * val00 + dx * val01) + dy * ((1.0 - dx) * val10 + dx * val11)

    # --- 2. SR KERNELS (@ti.kernel) ---

    @ti.kernel
    def simulate_lr_frames_kernel(
        hr_image: ti.types.ndarray(),
        sim_lr: ti.types.ndarray(),
        shifts: ti.types.ndarray(),
        scale: ti.i32
    ):
        """D * H * F * X — Simulate LR frames from HR estimate with Gaussian PSF blur."""
        for k, y_lr, x_lr in ti.ndrange(sim_lr.shape[0], sim_lr.shape[1], sim_lr.shape[2]):
            cy = float(y_lr * scale) + shifts[k, 0]
            cx = float(x_lr * scale) + shifts[k, 1]

            val = 0.0
            weight_sum = 0.0

            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    dist2 = float(dy * dy + dx * dx)
                    w = ti.exp(-dist2 / 2.0)

                    val += w * bilinear_sample(hr_image, cy + float(dy), cx + float(dx))
                    weight_sum += w

            sim_lr[k, y_lr, x_lr] = val / weight_sum

    @ti.kernel
    def compute_lr_error_kernel(
        sim_lr: ti.types.ndarray(),
        lr_frames: ti.types.ndarray(),
        weight_maps: ti.types.ndarray(),
        lr_error: ti.types.ndarray()
    ):
        """Weighted L2 error: W_k^2 * (sim_lr - lr_frames)."""
        for k, y, x in ti.ndrange(lr_error.shape[0], lr_error.shape[1], lr_error.shape[2]):
            diff = sim_lr[k, y, x] - lr_frames[k, y, x]
            w = weight_maps[k, y, x]
            lr_error[k, y, x] = (w * w) * diff

    @ti.kernel
    def reset_grad_kernel(hr_grad: ti.types.ndarray()):
        """Zero the gradient buffer."""
        for i, j in ti.ndrange(hr_grad.shape[0], hr_grad.shape[1]):
            hr_grad[i, j] = 0.0

    @ti.kernel
    def backproject_phase1_kernel(
        temp_hr: ti.types.ndarray(),
        lr_error: ti.types.ndarray(),
        k: ti.i32,
        scale: ti.i32
    ):
        """D^T + H^T: Upsample lr_error[k] with Gaussian PSF into temp_hr."""
        hr_h = temp_hr.shape[0]
        hr_w = temp_hr.shape[1]
        lr_h = lr_error.shape[1]
        lr_w = lr_error.shape[2]

        for i_hr, j_hr in ti.ndrange(hr_h, hr_w):
            val = 0.0
            lr_y_center = i_hr // scale
            lr_x_center = j_hr // scale

            for dy_lr in range(-2, 3):
                for dx_lr in range(-2, 3):
                    ly = lr_y_center + dy_lr
                    lx = lr_x_center + dx_lr

                    if 0 <= ly < lr_h and 0 <= lx < lr_w:
                        upsampled_y = ly * scale
                        upsampled_x = lx * scale

                        dist_y = abs(i_hr - upsampled_y)
                        dist_x = abs(j_hr - upsampled_x)

                        if dist_y <= 2 and dist_x <= 2:
                            dist2 = float(dist_y * dist_y + dist_x * dist_x)
                            w = ti.exp(-dist2 / 2.0)
                            val += w * lr_error[k, ly, lx]
            temp_hr[i_hr, j_hr] = val / 6.0

    @ti.kernel
    def backproject_phase2_kernel(
        hr_grad: ti.types.ndarray(),
        temp_hr: ti.types.ndarray(),
        shifts: ti.types.ndarray(),
        k: ti.i32
    ):
        """F_k^T: Shift-back via bilinear interpolation, accumulate to hr_grad."""
        for i_hr, j_hr in ti.ndrange(hr_grad.shape[0], hr_grad.shape[1]):
            target_y = float(i_hr) + shifts[k, 0]
            target_x = float(j_hr) + shifts[k, 1]
            hr_grad[i_hr, j_hr] += bilinear_sample(temp_hr, target_y, target_x)

    @ti.kernel
    def apply_btv_kernel(
        hr_image: ti.types.ndarray(),
        hr_grad: ti.types.ndarray(),
        lam: ti.f32,
        alpha: ti.f32,
        btv_window: ti.i32
    ):
        """Asymmetric BTV regularization gradient."""
        hr_h = hr_image.shape[0]
        hr_w = hr_image.shape[1]

        for i, j in ti.ndrange(hr_h, hr_w):
            btv_grad = 0.0
            for dy in range(0, 4):  # Max btv_window = 3
                for dx in range(-3, 4):  # Max btv_window = 3
                    if dy >= 0 and (dy > 0 or dx >= 0):
                        if dy != 0 or dx != 0:
                            if dy <= btv_window and abs(dx) <= btv_window:
                                power = abs(dy) + abs(dx)
                                weight = ti.pow(alpha, float(power))

                                y_fwd = ti.max(0, ti.min(hr_h - 1, i + dy))
                                x_fwd = ti.max(0, ti.min(hr_w - 1, j + dx))

                                y_bwd = ti.max(0, ti.min(hr_h - 1, i - dy))
                                x_bwd = ti.max(0, ti.min(hr_w - 1, j - dx))

                                diff_fwd = hr_image[i, j] - hr_image[y_fwd, x_fwd]
                                sgn_fwd = 0.0
                                if diff_fwd > 1e-5:
                                    sgn_fwd = 1.0
                                elif diff_fwd < -1e-5:
                                    sgn_fwd = -1.0

                                diff_bwd = hr_image[i, j] - hr_image[y_bwd, x_bwd]
                                sgn_bwd = 0.0
                                if diff_bwd > 1e-5:
                                    sgn_bwd = 1.0
                                elif diff_bwd < -1e-5:
                                    sgn_bwd = -1.0

                                btv_grad += weight * (sgn_fwd - sgn_bwd)

            hr_grad[i, j] += lam * btv_grad

    @ti.kernel
    def update_hr_kernel(
        hr_image: ti.types.ndarray(),
        hr_grad: ti.types.ndarray(),
        beta: ti.f32
    ):
        """Gradient descent step with clamp to [0, 1]."""
        for i, j in ti.ndrange(hr_image.shape[0], hr_image.shape[1]):
            hr_image[i, j] = ti.max(0.0, ti.min(1.0, hr_image[i, j] - beta * hr_grad[i, j]))

    @ti.kernel
    def robust_splat_kernel(
        frames: ti.types.ndarray(dtype=ti.f32, ndim=4),
        confidence: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow: ti.types.ndarray(dtype=ti.f32, ndim=4),
        result: ti.types.ndarray(dtype=ti.f32, ndim=3),
        coverage: ti.types.ndarray(dtype=ti.f32, ndim=2),
        scale: ti.i32,
        radius: ti.f32,
        sigma: ti.f32,
    ):
        """Deterministic output-centric evaluation of a sub-pixel splat.

        The mathematical operation is forward splatting, evaluated from the
        output pixel to its nearby source samples.  This avoids floating-point
        atomics and makes CPU/Vulkan/OpenGL/CUDA results reproducible.  The
        fixed search radius is intentionally bounded for AOT portability.
        """
        hr_h = result.shape[0]
        hr_w = result.shape[1]
        channels = result.shape[2]
        lr_h = frames.shape[1]
        lr_w = frames.shape[2]
        sigma_safe = ti.max(sigma, 1e-4)
        inv_two_sigma2 = 0.5 / (sigma_safe * sigma_safe)
        for i, j in ti.ndrange(hr_h, hr_w):
            lr_y = i // scale
            lr_x = j // scale
            denom = 0.0
            for k, oy, ox in ti.ndrange(frames.shape[0], (-3, 4), (-3, 4)):
                ly = lr_y + oy
                lx = lr_x + ox
                if 0 <= ly < lr_h and 0 <= lx < lr_w:
                    tx = (float(lx) + flow[k, ly, lx, 0]) * float(scale)
                    ty = (float(ly) + flow[k, ly, lx, 1]) * float(scale)
                    dx = float(j) - tx
                    dy = float(i) - ty
                    dist2 = dx * dx + dy * dy
                    if dist2 <= radius * radius:
                        w = confidence[k, ly, lx] * ti.exp(-dist2 * inv_two_sigma2)
                        denom += w
                        for c in range(channels):
                            result[i, j, c] += w * frames[k, ly, lx, c]
            coverage[i, j] = denom
            for c in range(channels):
                result[i, j, c] = ti.select(denom > 1e-8, result[i, j, c] / denom, 0.0)

    @ti.kernel
    def clear_splat_outputs_kernel(
        result: ti.types.ndarray(dtype=ti.f32, ndim=3),
        coverage: ti.types.ndarray(dtype=ti.f32, ndim=2),
    ):
        for i, j in ti.ndrange(coverage.shape[0], coverage.shape[1]):
            coverage[i, j] = 0.0
            for c in range(result.shape[2]):
                result[i, j, c] = 0.0

    @ti.kernel
    def robust_splat_gray_kernel(
        frames: ti.types.ndarray(dtype=ti.f32, ndim=3), confidence: ti.types.ndarray(dtype=ti.f32, ndim=3),
        flow_y: ti.types.ndarray(dtype=ti.f32, ndim=3), flow_x: ti.types.ndarray(dtype=ti.f32, ndim=3),
        result: ti.types.ndarray(dtype=ti.f32, ndim=2), coverage: ti.types.ndarray(dtype=ti.f32, ndim=2),
        scale: ti.i32, radius: ti.f32, sigma: ti.f32,
    ):
        """Scalar-channel graph that stays within the compact 3-D ABI."""
        inv_two_sigma2 = 0.5 / ti.max(sigma, 1e-4) ** 2
        for i, j in ti.ndrange(result.shape[0], result.shape[1]):
            cy = i // scale
            cx = j // scale
            value = 0.0
            denom = 0.0
            for k, oy, ox in ti.ndrange(frames.shape[0], (-3, 4), (-3, 4)):
                y = cy + oy
                x = cx + ox
                if 0 <= y < frames.shape[1] and 0 <= x < frames.shape[2]:
                    ty = (float(y) + flow_y[k, y, x]) * float(scale)
                    tx = (float(x) + flow_x[k, y, x]) * float(scale)
                    d2 = (float(i) - ty) ** 2 + (float(j) - tx) ** 2
                    if d2 <= radius * radius:
                        weight = confidence[k, y, x] * ti.exp(-d2 * inv_two_sigma2)
                        value += weight * frames[k, y, x]
                        denom += weight
            result[i, j] = ti.select(denom > 1e-8, value / denom, 0.0)
            coverage[i, j] = denom

    # --- 3. AOT GRAPH COMPILATION ---

    def _build_sr_step_graph(module, K):
        """Build a single-step SR graph for K frames.
        Dispatches: simulate → compute_error → reset_grad → [phase1+phase2 × K] → btv → update
        """
        # Array argument symbols
        sym_hr_image = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hr_image", dtype=ti.f32, ndim=2)
        sym_hr_grad = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "hr_grad", dtype=ti.f32, ndim=2)
        sym_temp_hr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "temp_hr", dtype=ti.f32, ndim=2)
        sym_lr_frames = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "lr_frames", dtype=ti.f32, ndim=3)
        sym_sim_lr = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "sim_lr", dtype=ti.f32, ndim=3)
        sym_lr_error = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "lr_error", dtype=ti.f32, ndim=3)
        sym_weight_maps = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "weight_maps", dtype=ti.f32, ndim=3)
        sym_shifts = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "shifts", dtype=ti.f32, ndim=2)

        # Scalar argument symbols
        sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.i32)
        sym_lam = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "lam", dtype=ti.f32)
        sym_beta = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "beta", dtype=ti.f32)
        sym_alpha = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "alpha", dtype=ti.f32)
        sym_btv_window = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "btv_window", dtype=ti.i32)

        # Per-frame k-index symbols
        sym_k = []
        for i in range(K):
            sym_k.append(ti.graph.Arg(ti.graph.ArgKind.SCALAR, f"k_{i}", dtype=ti.i32))

        # Build graph
        g = ti.graph.GraphBuilder()

        # 1. Simulate LR frames from current HR estimate
        g.dispatch(simulate_lr_frames_kernel, sym_hr_image, sym_sim_lr, sym_shifts, sym_scale)

        # 2. Compute weighted LR error
        g.dispatch(compute_lr_error_kernel, sym_sim_lr, sym_lr_frames, sym_weight_maps, sym_lr_error)

        # 3. Reset gradient buffer
        g.dispatch(reset_grad_kernel, sym_hr_grad)

        # 4. Backprojection for each frame
        for i in range(K):
            g.dispatch(backproject_phase1_kernel, sym_temp_hr, sym_lr_error, sym_k[i], sym_scale)
            g.dispatch(backproject_phase2_kernel, sym_hr_grad, sym_temp_hr, sym_shifts, sym_k[i])

        # 5. BTV regularization
        g.dispatch(apply_btv_kernel, sym_hr_image, sym_hr_grad, sym_lam, sym_alpha, sym_btv_window)

        # 6. Update HR image
        g.dispatch(update_hr_kernel, sym_hr_image, sym_hr_grad, sym_beta)

        module.add_graph(f"sr_step_K{K}", g.compile())

    def _package_tcm(module, out_dir, tcm_name):
        """Package AOT module into a .tcm zip file."""
        tmp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "tmp_aot_splat_sr"))
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        os.makedirs(tmp_dir)
        module.save(tmp_dir)
        tcm_path = os.path.join(out_dir, tcm_name)
        with zipfile.ZipFile(tcm_path, "w", zipfile.ZIP_DEFLATED) as tcm_zip:
            for root, dirs, files in os.walk(tmp_dir):
                for file in files:
                    tcm_zip.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), tmp_dir))
        shutil.rmtree(tmp_dir)
        print(f"  -> {tcm_path}")
        return tcm_path

    def _build_splat_graph(module, include_vector=True):
        """Add the backend-neutral robust splat graph to an AOT module."""
        sym_frames = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "frames", dtype=ti.f32, ndim=4)
        sym_confidence = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "confidence", dtype=ti.f32, ndim=3)
        sym_flow = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow", dtype=ti.f32, ndim=4)
        sym_result = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "result", dtype=ti.f32, ndim=3)
        sym_coverage = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coverage", dtype=ti.f32, ndim=2)
        sym_scale = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "scale", dtype=ti.i32)
        sym_radius = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "radius", dtype=ti.f32)
        sym_sigma = ti.graph.Arg(ti.graph.ArgKind.SCALAR, "sigma", dtype=ti.f32)
        graph = ti.graph.GraphBuilder()
        graph.dispatch(clear_splat_outputs_kernel, sym_result, sym_coverage)
        graph.dispatch(
            robust_splat_kernel,
            sym_frames,
            sym_confidence,
            sym_flow,
            sym_result,
            sym_coverage,
            sym_scale,
            sym_radius,
            sym_sigma,
        )
        if include_vector:
            module.add_graph("robust_splat", graph.compile())
        f = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "frames", dtype=ti.f32, ndim=3)
        c = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "confidence", dtype=ti.f32, ndim=3)
        fy = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_y", dtype=ti.f32, ndim=3)
        fx = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "flow_x", dtype=ti.f32, ndim=3)
        r = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "result", dtype=ti.f32, ndim=2)
        cov = ti.graph.Arg(ti.graph.ArgKind.NDARRAY, "coverage", dtype=ti.f32, ndim=2)
        scalar_graph = ti.graph.GraphBuilder()
        scalar_graph.dispatch(robust_splat_gray_kernel, f, c, fy, fx, r, cov, sym_scale, sym_radius, sym_sigma)
        module.add_graph("robust_splat_gray", scalar_graph.compile())

    def compile_splat_sr():
        """Compile all SR step graphs and package as TCM."""
        ti.init(arch=ti.vulkan, offline_cache=False)
        module = ti.aot.Module(ti.vulkan)

        for K in [2, 3, 4, 5, 8]:
            print(f"  Building sr_step_K{K} graph...")
            _build_sr_step_graph(module, K)

        print("  Building robust_splat graph...")
        _build_splat_graph(module)

        out_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "../../../../../ui/data/aot_assets"
        ))
        os.makedirs(out_dir, exist_ok=True)
        tcm_path = _package_tcm(module, out_dir, "splat_sr_vulkan.tcm")
        print(f"splattingSR compiled and packaged to: {tcm_path}")
        ti.reset()
        return tcm_path


if __name__ == "__main__":
    if _IS_COMPILE_MODE:
        print("=" * 60)
        print("Compiling splattingSR TCM module...")
        print("=" * 60)
        compile_splat_sr()
        print("=" * 60)
    else:
        print("Set AOT_MODE=0 to compile. In production, import SplatSRAOTEngine directly.")
