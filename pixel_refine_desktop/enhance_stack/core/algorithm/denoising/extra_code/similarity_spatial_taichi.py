import numpy as np
import cv2

try:
    import taichi as ti
    import taichi.math as tm
except ImportError:
    ti = None
    tm = None

# =================================================================================
# CONSTANTS & CONFIG
# =================================================================================
STABILITY_EPSILON = 1e-6
GRADIENT_WEIGHT_FACTOR = 1.0  # From C++ Header
MAD_TO_SIGMA_FACTOR = 1.4826

# =================================================================================
# HELPER FUNCTIONS (DEVICE)
# =================================================================================


@ti.func
def fast_tanh(x: float) -> float:
    # Use standard tanh on GPU, it's hardware accelerated and precise enough.
    # C++ used approximation for CPU speed.
    return tm.tanh(x)


@ti.func
def get_pixel_clamp(
    img: ti.types.ndarray(ndim=2), y: int, x: int, h: int, w: int
) -> float:
    # Mirror behavior or clamp? C++ loop avoids borders, so this is mostly for safety
    y_clamped = tm.clamp(y, 0, h - 1)
    x_clamped = tm.clamp(x, 0, w - 1)
    return img[y_clamped, x_clamped]


@ti.func
def calculate_hybrid_gradient_mad(
    current_tile: ti.types.ndarray(ndim=2),
    ref_tile: ti.types.ndarray(ndim=2),
    tile_h: int,
    tile_w: int,
    noise_level: float,
    gradient_weight_factor: float,
    stab_epsilon: float,
) -> float:
    """
    Replicates Internal::calculate_hybrid_gradient_optimized from block_matching.cpp
    """
    weighted_sum = 0.0
    total_weight = 0.0

    # Constants from C++
    grad_sensitivity = 202.5
    structure_max_thresh_sq = 150.0  # Used? In C++ called structure_thresh_sq

    # Adaptive noise constants
    # adaptive_noise_threshold = max(0.01, noise_level * 0.4)
    # adaptive_diff_threshold = max(0.005, noise_level * 0.2)
    # These are calculated inside the loop in C++, but depend only on noise_level?
    # Actually in C++ they are inside loop but depend on noise_level which is const for the function.
    # So we calculate them once here.

    adaptive_noise_thr = ti.max(0.01, noise_level * 0.4)
    adaptive_diff_thr = ti.max(0.005, noise_level * 0.2)
    structure_min_thr_sq = 150.0

    # Iterate skipping 1-pixel border (matches C++ logic to avoid checks)
    for y in range(1, tile_h - 1):
        for x in range(1, tile_w - 1):

            # 1. Pixel Difference
            p1_val = current_tile[y, x]
            p2_val = ref_tile[y, x]
            pixel_diff = ti.abs(p1_val - p2_val)

            # 2. Gradients (Option A: Diagonal Averaging from C++)
            # Horizontal Gradients
            # Current
            p1_r = current_tile[y, x + 1]
            p1_l = current_tile[y, x - 1]
            p1_tr = current_tile[y - 1, x + 1]
            p1_tl = current_tile[y - 1, x - 1]
            p1_br = current_tile[y + 1, x + 1]
            p1_bl = current_tile[y + 1, x - 1]

            gx1_center = p1_r - p1_l
            gx1_top = p1_tr - p1_tl
            gx1_bottom = p1_br - p1_bl
            gx1 = (gx1_center + gx1_top + gx1_bottom) * 0.3333333

            # Reference
            p2_r = ref_tile[y, x + 1]
            p2_l = ref_tile[y, x - 1]
            p2_tr = ref_tile[y - 1, x + 1]
            p2_tl = ref_tile[y - 1, x - 1]
            p2_br = ref_tile[y + 1, x + 1]
            p2_bl = ref_tile[y + 1, x - 1]

            gx2_center = p2_r - p2_l
            gx2_top = p2_tr - p2_tl
            gx2_bottom = p2_br - p2_bl
            gx2 = (gx2_center + gx2_top + gx2_bottom) * 0.3333333

            # Vertical Gradients
            p1_d = current_tile[y + 1, x]
            p1_u = current_tile[y - 1, x]
            gy1 = p1_d - p1_u

            p2_d = ref_tile[y + 1, x]
            p2_u = ref_tile[y - 1, x]
            gy2 = p2_d - p2_u

            # Magnitudes
            mag1_sq = gx1 * gx1 + gy1 * gy1
            mag2_sq = gx2 * gx2 + gy2 * gy2
            min_mag_sq = ti.min(mag1_sq, mag2_sq)

            # --- Noise Weighting Logic ---
            noise_weight = 1.0
            if noise_level > stab_epsilon:
                if min_mag_sq < structure_min_thr_sq:
                    # Flat area
                    local_thr = adaptive_diff_thr * 1.5
                    if pixel_diff < local_thr:
                        noise_weight = 0.05 + 0.95 * (pixel_diff / local_thr)
                    else:
                        ratio = (pixel_diff - local_thr) / local_thr
                        if ratio > 1.0:
                            ratio = 1.0
                        noise_weight = 1.0 - 0.2 * ratio
                else:
                    # Edge area
                    if pixel_diff < adaptive_diff_thr:
                        noise_weight = 1.15 + 0.15 * (
                            1.0 - pixel_diff / adaptive_diff_thr
                        )
                    else:
                        ratio = pixel_diff / (adaptive_diff_thr * 4.0)
                        if ratio > 1.0:
                            ratio = 1.0
                        noise_weight = 0.3 + 0.4 * (1.0 - ratio)

            # --- Structure Weighting Logic ---
            structure_weight = 1.0
            if (
                min_mag_sq > stab_epsilon
                and mag1_sq > stab_epsilon
                and mag2_sq > stab_epsilon
            ):
                dot = gx1 * gx2 + gy1 * gy2
                cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                score = (ti.max(0.0, cos_sim)) * ti.sqrt(min_mag_sq)

                structure_weight = 1.0 + gradient_weight_factor * fast_tanh(
                    score * grad_sensitivity
                )

            final_weight = structure_weight * noise_weight

            weighted_sum += pixel_diff * final_weight
            total_weight += final_weight

    # Result
    result = 0.0
    if total_weight < 1e-4:
        # Fallback L1 (Plain Mean)
        # Re-calculate simple L1 mean for the whole block
        l1_sum = 0.0
        count = 0.0
        for y_l in range(tile_h):
            for x_l in range(tile_w):
                l1_sum += ti.abs(current_tile[y_l, x_l] - ref_tile[y_l, x_l])
                count += 1.0
        result = l1_sum / count
    else:
        result = weighted_sum / total_weight

    return result


# =================================================================================
# MAIN CLASS
# =================================================================================


@ti.data_oriented
class TaichiSpatialMerger:
    def __init__(self):
        # Configure Taichi offline cache for "Instant Run"
        try:
            ti.init(arch=ti.gpu, offline_cache=True)
        except:
            ti.init(arch=ti.cpu)

        # Track last image size for buffer reuse
        self._last_img_size = None
        self._last_buffers = {}

    def _get_or_create_buffer(self, key, shape, dtype):
        """
        Smart buffer allocation: reuse if size unchanged, reallocate if changed.
        key: string identifier for this buffer type (e.g., 'curr_img', 'weight_map')
        """
        current_size = (shape, dtype)

        # Check if buffer exists and matches size
        if key in self._last_buffers:
            last_size, buffer = self._last_buffers[key]
            if last_size == current_size:
                return buffer
            # Size mismatch - clear old buffer
            self._last_buffers[key] = None

        # Allocate new buffer
        new_buffer = ti.ndarray(dtype=dtype, shape=shape)
        self._last_buffers[key] = (current_size, new_buffer)
        return new_buffer

    @ti.kernel
    def downsample_kernel(
        self,
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        s_h: int,
        s_w: int,
        d_h: int,
        d_w: int,
    ):
        # Simple box downsample or nearest/bilinear?
        # C++ uses cv::resize with INTER_AREA.
        # For simplicity on GPU, we can do a simple average of corresponding block.
        # Scale factors
        scale_y = float(s_h) / float(d_h)
        scale_x = float(s_w) / float(d_w)

        for y, x in ti.ndrange(d_h, d_w):
            # Map dst pixel to src rect
            src_y_start = int(y * scale_y)
            src_x_start = int(x * scale_x)
            src_y_end = int((y + 1) * scale_y)
            src_x_end = int((x + 1) * scale_x)

            # Safety
            src_y_end = ti.min(src_y_end, s_h)
            src_x_end = ti.min(src_x_end, s_w)

            sum_val = 0.0
            count = 0.0

            for ry in range(src_y_start, src_y_end):
                for rx in range(src_x_start, src_x_end):
                    sum_val += src[ry, rx]
                    count += 1.0

            if count > 0:
                dst[y, x] = sum_val / count
            else:
                dst[y, x] = src[src_y_start, src_x_start]  # Fallback

    @ti.kernel
    def upsample_guidance_kernel(
        self,
        src: ti.types.ndarray(),
        dst: ti.types.ndarray(),
        s_h: int,
        s_w: int,
        d_h: int,
        d_w: int,
    ):
        # Bilinear interpolation
        scale_y = float(s_h - 1) / float(d_h - 1)
        scale_x = float(s_w - 1) / float(d_w - 1)

        for y, x in ti.ndrange(d_h, d_w):
            src_y = y * scale_y
            src_x = x * scale_x

            y0 = int(ti.floor(src_y))
            x0 = int(ti.floor(src_x))
            y1 = ti.min(y0 + 1, s_h - 1)
            x1 = ti.min(x0 + 1, s_w - 1)

            dy = src_y - y0
            dx = src_x - x0

            v00 = src[y0, x0]
            v10 = src[y1, x0]
            v01 = src[y0, x1]
            v11 = src[y1, x1]

            res = (1.0 - dy) * ((1.0 - dx) * v00 + dx * v01) + dy * (
                (1.0 - dx) * v10 + dx * v11
            )
            dst[y, x] = res

    @ti.kernel
    def phase1_coarse_mad_kernel(
        self,
        current: ti.types.ndarray(),
        reference: ti.types.ndarray(),
        confidence_map: ti.types.ndarray(),
        img_h: int,
        img_w: int,
        tile_h: int,
        tile_w: int,
        global_noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
    ):
        """
        Computes coarse confidence map.
        Grid size determined by output confidence_map shape.
        """
        grid_rows = confidence_map.shape[0]
        grid_cols = confidence_map.shape[1]

        for gy, gx in ti.ndrange(grid_rows, grid_cols):
            # Define ROI in source images
            y_start = gy * tile_h
            x_start = gx * tile_w

            # Check bounds (C++ uses safeguard)
            if y_start < img_h and x_start < img_w:
                eff_tile_h = ti.min(tile_h, img_h - y_start)
                eff_tile_w = ti.min(tile_w, img_w - x_start)

                # Extract tile (virtual, we just pass coords to func or use slice)
                # Taichi doesn't support passing slices easily to functions expecting ndarrays if we want efficiency?
                # Actually we can't pass a "slice" object. We have to make the function accept coordinates.
                # BUT `calculate_hybrid_gradient_mad` above expects 2D arrays.
                # Refactoring `calculate_hybrid_gradient_mad` to take full image + offsets is better for kernel usage.

                # Inline logic or call modified helper?
                # Let's Modify Helper to be Inline-able or take offsets.
                # To minimize code dup, let's assume we copy to local buffer? No, slow.
                # We will adapt the helper below to take accessors.

                # ... see optimized helper below ...
                mad_score = self.device_calculate_mad(
                    current,
                    reference,
                    y_start,
                    x_start,
                    eff_tile_h,
                    eff_tile_w,
                    global_noise_sigma,
                    1.0,
                    1e-6,
                )

                # Confidence Calculation
                # float val = res.mad_score;
                # float sigma = std::max(1e-6f, global_estimated_noise_sigma);
                # float diff_ratio = val / sigma;
                # float adjusted = std::max(0.0f, diff_ratio - noise_offset_factor);
                # float exponent = adjusted * motion_sensitivity * 0.5f;
                # if (exponent > 20.0f) conf = 0.0f;
                # else conf = 1.0f / (1.0f + std::exp(exponent - 2.0f));

                sigma = ti.max(1e-6, global_noise_sigma)
                diff_ratio = mad_score / sigma
                adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
                exponent = adjusted * motion_sensitivity * 0.5

                conf = 0.0
                if exponent <= 20.0:
                    conf = 1.0 / (1.0 + tm.exp(exponent - 2.0))

                confidence_map[gy, gx] = conf

    @ti.func
    def device_calculate_mad(
        self,
        img1: ti.types.ndarray(ndim=2),
        img2: ti.types.ndarray(ndim=2),
        y_start: int,
        x_start: int,
        h: int,
        w: int,
        noise_level: float,
        grad_weight: float,
        eps: float,
    ) -> float:
        # Re-implementation of calculate_hybrid_gradient_mad taking Global coordinates
        weighted_sum = 0.0
        total_weight = 0.0

        adaptive_noise_thr = ti.max(0.01, noise_level * 0.4)
        adaptive_diff_thr = ti.max(0.005, noise_level * 0.2)
        structure_min_thr_sq = 150.0
        grad_sensitivity = 202.5

        # Loop 1 to h-1 (relative)
        for dy in range(1, h - 1):
            for dx in range(1, w - 1):
                y = y_start + dy
                x = x_start + dx

                # 1. Pixel Diff
                p1 = img1[y, x]
                p2 = img2[y, x]
                diff = ti.abs(p1 - p2)

                # 2. Gradients (Option A: Diagonal Averaging)
                # Helper to get pixel safely? We are inside bounds [1, h-1], so +1/-1 is safe relative to y_start.
                # Assuming image bounds are handled by h, w being effective size.

                # H-Gradients
                gx1 = (
                    (img1[y, x + 1] - img1[y, x - 1])
                    + (img1[y - 1, x + 1] - img1[y - 1, x - 1])
                    + (img1[y + 1, x + 1] - img1[y + 1, x - 1])
                ) * 0.3333333

                gx2 = (
                    (img2[y, x + 1] - img2[y, x - 1])
                    + (img2[y - 1, x + 1] - img2[y - 1, x - 1])
                    + (img2[y + 1, x + 1] - img2[y + 1, x - 1])
                ) * 0.3333333

                # V-Gradients
                gy1 = img1[y + 1, x] - img1[y - 1, x]
                gy2 = img2[y + 1, x] - img2[y - 1, x]

                mag1_sq = gx1**2 + gy1**2
                mag2_sq = gx2**2 + gy2**2
                min_mag_sq = ti.min(mag1_sq, mag2_sq)

                # Noise Weight
                n_w = 1.0
                if noise_level > eps:
                    if min_mag_sq < structure_min_thr_sq:
                        local_thr = adaptive_diff_thr * 1.5
                        if diff < local_thr:
                            n_w = 0.05 + 0.95 * (diff / local_thr)
                        else:
                            ratio = (diff - local_thr) / local_thr
                            if ratio > 1.0:
                                ratio = 1.0
                            n_w = 1.0 - 0.2 * ratio
                    else:
                        if diff < adaptive_diff_thr:
                            n_w = 1.15 + 0.15 * (1.0 - diff / adaptive_diff_thr)
                        else:
                            ratio = diff / (adaptive_diff_thr * 4.0)
                            if ratio > 1.0:
                                ratio = 1.0
                            n_w = 0.3 + 0.4 * (1.0 - ratio)

                # Structure Weight
                s_w = 1.0
                if min_mag_sq > eps and mag1_sq > eps and mag2_sq > eps:
                    dot = gx1 * gx2 + gy1 * gy2
                    cos_sim = dot / ti.sqrt(mag1_sq * mag2_sq)
                    score = ti.max(0.0, cos_sim) * ti.sqrt(min_mag_sq)
                    s_w = 1.0 + grad_weight * tm.tanh(score * grad_sensitivity)

                fw = s_w * n_w
                weighted_sum += diff * fw
                total_weight += fw

        res = 0.0
        if total_weight < 1e-4:
            # Fallback L1
            l1_sum = 0.0
            cnt = 0.0
            for dy in range(h):
                for dx in range(w):
                    l1_sum += ti.abs(
                        img1[y_start + dy, x_start + dx]
                        - img2[y_start + dy, x_start + dx]
                    )
                    cnt += 1.0
            res = l1_sum / cnt
        else:
            res = weighted_sum / total_weight
        return res

    @ti.kernel
    def phase2_accumulate_kernel(
        self,
        current: ti.types.ndarray(),
        reference: ti.types.ndarray(),
        weight_map_sum: ti.types.ndarray(),
        base_window: ti.types.ndarray(),
        guidance_map: ti.types.ndarray(),
        row_starts: ti.types.ndarray(),
        col_starts: ti.types.ndarray(),
        pass_row_mod: int,
        pass_col_mod: int,
        tile_h: int,
        tile_w: int,
        img_h: int,
        img_w: int,
        global_noise_sigma: float,
        motion_sensitivity: float,
        noise_offset_factor: float,
    ):

        # Grid based on row_starts/col_starts size
        n_rows = row_starts.shape[0]
        n_cols = col_starts.shape[0]  # Actually 1D, so shape[0]

        # We iterate over the logical grid of tiles
        for r_idx, c_idx in ti.ndrange(n_rows, n_cols):
            # Checkerboard check
            if r_idx % 2 == pass_row_mod and c_idx % 2 == pass_col_mod:
                r = row_starts[r_idx]
                c = col_starts[c_idx]

                curr_h = ti.min(tile_h, img_h - r)
                curr_w = ti.min(tile_w, img_w - c)

                if curr_h > 0 and curr_w > 0:
                    # 1. Compute MAD
                    mad_score = self.device_calculate_mad(
                        current,
                        reference,
                        r,
                        c,
                        curr_h,
                        curr_w,
                        global_noise_sigma,
                        1.0,
                        1e-6,
                    )

                    # 2. Compute Match Confidence (Fine)
                    sigma = ti.max(1e-6, global_noise_sigma)
                    diff_ratio = mad_score / sigma
                    adjusted = ti.max(0.0, diff_ratio - noise_offset_factor)
                    exponent = adjusted * motion_sensitivity

                    # Fine sensitivity is usually higher or same?
                    # C++: exponent = adjusted * motion_sensitivity * 0.5f (for coarse)
                    # C++: calculate_match_confidence (Fine) -> uses motion_sensitivity DIRECTLY (no 0.5 factor)
                    # Implementation Check block_matching.cpp line 280 vs line 350
                    # Line 280 (Coarse): sensitivity * 0.5
                    # Line 350 (Fine): calculate_match_confidence(..., sensitivity, ...)
                    # Let's assume calculate_match_confidence uses plain sensitivity.

                    conf = 0.0
                    if exponent <= 20.0:
                        conf = 1.0 / (1.0 + tm.exp(exponent - 2.0))

                    # 3. Combine with Guidance
                    center_x = ti.min(c + curr_w // 2, img_w - 1)
                    center_y = ti.min(r + curr_h // 2, img_h - 1)
                    guide_val = guidance_map[center_y, center_x]

                    final_conf = conf * guide_val

                    # 4. Accumulate Window
                    if final_conf > 1e-6:
                        for wy in range(curr_h):
                            for wx in range(curr_w):
                                # Access base_window (assuming it's exactly tile_h x tile_w)
                                # Handle partial tiles: just read the top-left part of window
                                win_val = base_window[wy, wx]
                                weight = win_val * final_conf

                                # Global Accumulate (Safe due to checkerboard)
                                weight_map_sum[r + wy, c + wx] += weight

    def compute_spatial_merging(
        self,
        current_img,
        reference_img,
        base_window,
        row_starts,
        col_starts,
        tile_h,
        tile_w,
        motion_sensitivity,
        noise_offset_factor,
        precomputed_ref_noise_sigma,
    ):
        """
        Main Entry Point.
        """
        h_img, w_img = current_img.shape[:2]

        # Ensure float32 contiguous
        curr_g = np.ascontiguousarray(current_img, dtype=np.float32)
        ref_g = np.ascontiguousarray(reference_img, dtype=np.float32)

        # Smart GPU buffer allocation - reuse if size matches, reallocate if changed
        curr_gpu = self._get_or_create_buffer("curr_img", (h_img, w_img), ti.f32)
        ref_gpu = self._get_or_create_buffer("ref_img", (h_img, w_img), ti.f32)
        weight_map_gpu = self._get_or_create_buffer(
            "weight_map", (h_img, w_img), ti.f32
        )

        # Upload data to GPU
        curr_gpu.from_numpy(curr_g)
        ref_gpu.from_numpy(ref_g)
        weight_map_gpu.fill(0.0)

        # --- PHASE 1: COARSE GUIDANCE ---
        coarse_h = max(64, h_img // 4)
        coarse_w = max(64, w_img // 4)

        curr_coarse_gpu = self._get_or_create_buffer(
            "curr_coarse", (coarse_h, coarse_w), ti.f32
        )
        ref_coarse_gpu = self._get_or_create_buffer(
            "ref_coarse", (coarse_h, coarse_w), ti.f32
        )

        self.downsample_kernel(
            curr_gpu, curr_coarse_gpu, h_img, w_img, coarse_h, coarse_w
        )
        self.downsample_kernel(
            ref_gpu, ref_coarse_gpu, h_img, w_img, coarse_h, coarse_w
        )

        # Compute Coarse Confidence
        coarse_tile_h = max(8, tile_h // 4)
        coarse_tile_w = max(8, tile_w // 4)

        grid_h = coarse_h // coarse_tile_h
        grid_w = coarse_w // coarse_tile_w

        coarse_conf_gpu = self._get_or_create_buffer(
            "coarse_conf", (grid_h, grid_w), ti.f32
        )

        self.phase1_coarse_mad_kernel(
            curr_coarse_gpu,
            ref_coarse_gpu,
            coarse_conf_gpu,
            coarse_h,
            coarse_w,
            coarse_tile_h,
            coarse_tile_w,
            precomputed_ref_noise_sigma,
            motion_sensitivity,
            noise_offset_factor,
        )

        # Upsample Guidance
        guidance_map_gpu = self._get_or_create_buffer(
            "guidance_map", (h_img, w_img), ti.f32
        )
        self.upsample_guidance_kernel(
            coarse_conf_gpu, guidance_map_gpu, grid_h, grid_w, h_img, w_img
        )

        # --- PHASE 2: FINE ACCUMULATION (4-PASS) ---
        r_starts_np = np.ascontiguousarray(row_starts, dtype=np.int32)
        c_starts_np = np.ascontiguousarray(col_starts, dtype=np.int32)
        base_win_np = np.ascontiguousarray(base_window, dtype=np.float32)

        # Upload auxiliary arrays (these are typically small and consistent)
        r_starts_gpu = self._get_or_create_buffer(
            "row_starts", r_starts_np.shape, ti.i32
        )
        c_starts_gpu = self._get_or_create_buffer(
            "col_starts", c_starts_np.shape, ti.i32
        )
        base_win_gpu = self._get_or_create_buffer(
            "base_window", base_win_np.shape, ti.f32
        )

        r_starts_gpu.from_numpy(r_starts_np)
        c_starts_gpu.from_numpy(c_starts_np)
        base_win_gpu.from_numpy(base_win_np)

        # 4 Passes
        for i in range(4):
            pass_row = i // 2
            pass_col = i % 2
            self.phase2_accumulate_kernel(
                curr_gpu,
                ref_gpu,
                weight_map_gpu,
                base_win_gpu,
                guidance_map_gpu,
                r_starts_gpu,
                c_starts_gpu,
                pass_row,
                pass_col,
                tile_h,
                tile_w,
                h_img,
                w_img,
                precomputed_ref_noise_sigma,
                motion_sensitivity,
                noise_offset_factor,
            )

        return weight_map_gpu.to_numpy()


# Singleton Instance
instance = None


def compute_spatial_merging_taichi(
    current_img,
    reference_img,
    base_window,
    row_starts,
    col_starts,
    tile_h,
    tile_w,
    motion_sensitivity,
    noise_offset_factor,
    precomputed_ref_noise_sigma,
):
    global instance
    if instance is None:
        instance = TaichiSpatialMerger()

    return instance.compute_spatial_merging(
        current_img,
        reference_img,
        base_window,
        row_starts,
        col_starts,
        tile_h,
        tile_w,
        motion_sensitivity,
        noise_offset_factor,
        precomputed_ref_noise_sigma,
    )
