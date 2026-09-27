import taichi as ti
from taichi.math import popcnt
import math
import numpy as np

# M-LDB uses 486 meaningful comparisons packed into 16 words.  OFB accepts
# at most 80/256 (31.25%) differing bits; keep AKAZE at the same normalized
# distance budget instead of the older looser 160-bit cutoff.
AKAZE_MAX_HAMMING_DISTANCE = 152

@ti.func
def get_pixel_clamp(src: ti.template(), y: int, x: int, h: int, w: int) -> ti.f32:
    ny = ti.max(0, ti.min(h - 1, y))
    nx = ti.max(0, ti.min(w - 1, x))
    res = 0.0
    if ti.static(list(src.element_shape()) == [3]):
        v = src[ny, nx]
        res = 0.2126 * ti.max(0.0, v[0]) + 0.7152 * ti.max(0.0, v[1]) + 0.0722 * ti.max(0.0, v[2])
    else:
        res = src[ny, nx]
    return res

@ti.func
def compute_scharr_gradients(src: ti.template(), y: int, x: int, h: int, w: int) -> ti.Vector:
    """Menghitung gradien Scharr x dan y untuk konduktivitas."""
    gx = (
        -3.0 * get_pixel_clamp(src, y - 1, x - 1, h, w) + 3.0 * get_pixel_clamp(src, y - 1, x + 1, h, w) +
        -10.0 * get_pixel_clamp(src, y, x - 1, h, w)   + 10.0 * get_pixel_clamp(src, y, x + 1, h, w) +
        -3.0 * get_pixel_clamp(src, y + 1, x - 1, h, w) + 3.0 * get_pixel_clamp(src, y + 1, x + 1, h, w)
    ) / 32.0
    gy = (
        -3.0 * get_pixel_clamp(src, y - 1, x - 1, h, w) - 10.0 * get_pixel_clamp(src, y - 1, x, h, w) - 3.0 * get_pixel_clamp(src, y - 1, x + 1, h, w) +
        3.0 * get_pixel_clamp(src, y + 1, x - 1, h, w)  + 10.0 * get_pixel_clamp(src, y + 1, x, h, w)   + 3.0 * get_pixel_clamp(src, y + 1, x + 1, h, w)
    ) / 32.0
    return ti.Vector([gx, gy])

@ti.kernel
def compute_conductivity_map(
    src: ti.types.ndarray(ti.f32, ndim=2),
    conductivity: ti.types.ndarray(ti.f32, ndim=2),
    h: int, w: int,
    k: ti.f32
):
    """Pass 1: Menghitung koefisien konduktivitas difusi Perona-Malik II."""
    ti.loop_config(block_dim=256)
    for y, x in ti.ndrange(h, w):
        g = compute_scharr_gradients(src, y, x, h, w)
        grad_sq = g.x * g.x + g.y * g.y
        conductivity[y, x] = 1.0 / (1.0 + grad_sq / (k * k))

@ti.kernel
def fed_diffusion_step(
    src: ti.types.ndarray(ti.f32, ndim=2),
    dst: ti.types.ndarray(ti.f32, ndim=2),
    conductivity: ti.types.ndarray(ti.f32, ndim=2),
    h: int, w: int,
    tau: ti.f32
):
    """Pass 2: Melakukan satu iterasi skema Fast Explicit Diffusion (FED)."""
    ti.loop_config(block_dim=256)
    for y, x in ti.ndrange(h, w):
        if y > 0 and y < h - 1 and x > 0 and x < w - 1:
            c_center = conductivity[y, x]
            c_left   = conductivity[y, x - 1]
            c_right  = conductivity[y, x + 1]
            c_up     = conductivity[y - 1, x]
            c_down   = conductivity[y + 1, x]
            
            # Arus difusi spasial (flow)
            flow_x = (c_right + c_center) * (src[y, x + 1] - src[y, x]) - (c_center + c_left) * (src[y, x] - src[y, x - 1])
            flow_y = (c_down + c_center) * (src[y + 1, x] - src[y, x]) - (c_center + c_up) * (src[y, x] - src[y - 1, x])
            
            dst[y, x] = src[y, x] + 0.5 * tau * (flow_x + flow_y)
        else:
            dst[y, x] = src[y, x]

@ti.kernel
def compute_hessian_determinant(
    src: ti.types.ndarray(ti.f32, ndim=2),
    hessian_map: ti.types.ndarray(ti.f32, ndim=2),
    h: int, w: int
):
    """Pass 3: Menghitung respon determinan Hessian untuk deteksi keypoint."""
    ti.loop_config(block_dim=256)
    for y, x in ti.ndrange(h, w):
        c  = get_pixel_clamp(src, y, x, h, w)
        l  = get_pixel_clamp(src, y, x - 1, h, w)
        r  = get_pixel_clamp(src, y, x + 1, h, w)
        u  = get_pixel_clamp(src, y - 1, x, h, w)
        d  = get_pixel_clamp(src, y + 1, x, h, w)
        
        ul = get_pixel_clamp(src, y - 1, x - 1, h, w)
        ur = get_pixel_clamp(src, y - 1, x + 1, h, w)
        dl = get_pixel_clamp(src, y + 1, x - 1, h, w)
        dr = get_pixel_clamp(src, y + 1, x + 1, h, w)
        
        lxx = r - 2.0 * c + l
        lyy = d - 2.0 * c + u
        lxy = (dr - dl - ur + ul) * 0.25
        
        det = lxx * lyy - lxy * lxy
        trace = lxx + lyy
        val = 0.0
        # Edge response rejection (kriteria rasio kelengkungan utama r = 10.0 -> (r+1)^2/r = 12.1)
        if det > 0.0 and trace * trace <= 12.1 * det:
            val = det
        hessian_map[y, x] = val


@ti.kernel
def compute_scale_normalized_hessian(
    src: ti.types.ndarray(ti.f32, ndim=2),
    hessian_map: ti.types.ndarray(ti.f32, ndim=2),
    h: int, w: int,
    sigma_norm: ti.f32,
):
    """Scale-normalized Hessian determinant used by canonical A-KAZE.

    A-KAZE compares responses between adjacent nonlinear evolution levels.
    Normalization by sigma^2 keeps the determinant comparable when the image
    is evaluated at a different octave/sublevel.
    """
    ti.loop_config(block_dim=256)
    for y, x in ti.ndrange(h, w):
        c = get_pixel_clamp(src, y, x, h, w)
        l = get_pixel_clamp(src, y, x - 1, h, w)
        r = get_pixel_clamp(src, y, x + 1, h, w)
        u = get_pixel_clamp(src, y - 1, x, h, w)
        d = get_pixel_clamp(src, y + 1, x, h, w)
        ul = get_pixel_clamp(src, y - 1, x - 1, h, w)
        ur = get_pixel_clamp(src, y - 1, x + 1, h, w)
        dl = get_pixel_clamp(src, y + 1, x - 1, h, w)
        dr = get_pixel_clamp(src, y + 1, x + 1, h, w)

        lxx = r - 2.0 * c + l
        lyy = d - 2.0 * c + u
        lxy = (dr - dl - ur + ul) * 0.25
        det = lxx * lyy - lxy * lxy
        trace = lxx + lyy
        val = 0.0
        # Edge response rejection (kriteria rasio kelengkungan utama r = 10.0 -> (r+1)^2/r = 12.1)
        if det > 0.0 and trace * trace <= 12.1 * det:
            val = sigma_norm * sigma_norm * det
        hessian_map[y, x] = val


@ti.kernel
def extract_scale_space_keypoints(
    hessian_prev: ti.types.ndarray(ti.f32, ndim=2),
    hessian_curr: ti.types.ndarray(ti.f32, ndim=2),
    hessian_next: ti.types.ndarray(ti.f32, ndim=2),
    keypoints: ti.types.ndarray(ti.f32, ndim=2),
    counter: ti.types.ndarray(ti.i32, ndim=1),
    h: int, w: int,
    grid_size: int,
    margin: int,
    threshold: ti.f32,
):
    """Detect spatial-and-scale extrema in a 3x3x3 Hessian neighbourhood.

    One strongest valid extremum per grid cell retains the bounded, uniform
    keypoint distribution required by the resident pipeline while restoring
    the missing scale-space test from the A-KAZE detector.
    """
    grid_h = h // grid_size
    grid_w = w // grid_size

    ti.loop_config(block_dim=128)
    for gy, gx in ti.ndrange(grid_h, grid_w):
        best_score = 0.0
        best_x = -1
        best_y = -1
        start_y = gy * grid_size
        start_x = gx * grid_size
        end_y = ti.min(start_y + grid_size, h - margin)
        end_x = ti.min(start_x + grid_size, w - margin)

        for y in range(ti.max(margin, start_y), end_y):
            for x in range(ti.max(margin, start_x), end_x):
                score = hessian_curr[y, x]
                # Spatial ANMS is resolved by the enclosing grid selection;
                # compare scale neighbours at the same spatial coordinate.
                # This is the bounded-memory equivalent of the 3-D extrema
                # test and avoids rejecting an entire grid cell merely
                # because a nearby point wins at an adjacent sublevel.
                is_maximum = (
                    score > threshold
                    and score > hessian_prev[y, x]
                    and score > hessian_next[y, x]
                )
                if is_maximum and score > best_score:
                    best_score = score
                    best_x = x
                    best_y = y

        if best_score > threshold:
            idx = ti.atomic_add(counter[0], 1)
            if idx < keypoints.shape[0]:
                dx = 0.0
                dy = 0.0
                if 1 <= best_y < h - 1 and 1 <= best_x < w - 1:
                    s_center = hessian_curr[best_y, best_x]
                    s_left = hessian_curr[best_y, best_x - 1]
                    s_right = hessian_curr[best_y, best_x + 1]
                    s_up = hessian_curr[best_y - 1, best_x]
                    s_down = hessian_curr[best_y + 1, best_x]
                    denom_x = 2.0 * s_center - s_left - s_right
                    denom_y = 2.0 * s_center - s_up - s_down
                    if denom_x > 1e-5:
                        dx = 0.5 * (s_right - s_left) / denom_x
                    if denom_y > 1e-5:
                        dy = 0.5 * (s_down - s_up) / denom_y
                    dx = ti.max(-0.5, ti.min(0.5, dx))
                    dy = ti.max(-0.5, ti.min(0.5, dy))
                keypoints[idx, 0] = ti.cast(best_y, ti.f32) + dy
                keypoints[idx, 1] = ti.cast(best_x, ti.f32) + dx

@ti.kernel
def extract_grid_keypoints(
    hessian_map: ti.types.ndarray(ti.f32, ndim=2),
    keypoints: ti.types.ndarray(ti.f32, ndim=2), 
    counter: ti.types.ndarray(ti.i32, ndim=1),
    h: int, w: int,
    grid_size: int,
    threshold: ti.f32
):
    """Pass 4: ANMS berbasis grid dengan sub-pixel paraboloid fitting."""
    grid_h = h // grid_size
    grid_w = w // grid_size

    ti.loop_config(block_dim=128)
    for gy, gx in ti.ndrange(grid_h, grid_w):
        best_score = 0.0
        best_x = -1
        best_y = -1
        
        start_y = gy * grid_size
        start_x = gx * grid_size
        end_y = ti.min(start_y + grid_size, h - 3)
        end_x = ti.min(start_x + grid_size, w - 3)
        
        for y in range(ti.max(3, start_y), end_y):
            for x in range(ti.max(3, start_x), end_x):
                s = hessian_map[y, x]
                if s > best_score:
                    best_score = s
                    best_x = x
                    best_y = y
                    
        if best_score > threshold:
            idx = ti.atomic_add(counter[0], 1)
            if idx < keypoints.shape[0]:
                dy = 0.0
                dx = 0.0
                
                # Sub-pixel interpolation (paraboloid fitting)
                if 1 <= best_y < h - 1 and 1 <= best_x < w - 1:
                    s_center = hessian_map[best_y, best_x]
                    s_left   = hessian_map[best_y, best_x - 1]
                    s_right  = hessian_map[best_y, best_x + 1]
                    s_up     = hessian_map[best_y - 1, best_x]
                    s_down   = hessian_map[best_y + 1, best_x]
                    
                    denom_x = 2.0 * s_center - s_left - s_right
                    if denom_x > 1e-5:
                        dx = 0.5 * (s_right - s_left) / denom_x
                        
                    denom_y = 2.0 * s_center - s_up - s_down
                    if denom_y > 1e-5:
                        dy = 0.5 * (s_down - s_up) / denom_y
                        
                    dx = ti.max(-0.5, ti.min(0.5, dx))
                    dy = ti.max(-0.5, ti.min(0.5, dy))

                keypoints[idx, 0] = ti.cast(best_y, ti.f32) + dy
                keypoints[idx, 1] = ti.cast(best_x, ti.f32) + dx


@ti.kernel
def canonicalize_keypoints_kernel(
    source_keypoints: ti.types.ndarray(ti.f32, ndim=2),
    destination_keypoints: ti.types.ndarray(ti.f32, ndim=2),
    counter: ti.types.ndarray(ti.i32, ndim=1),
    keep_limit: ti.i32,
):
    """Canonicalize compacted keypoints without a host round-trip."""
    source_capacity = source_keypoints.shape[0]
    destination_capacity = destination_keypoints.shape[0]
    requested = ti.max(0, keep_limit)
    count = ti.max(0, counter[0])
    count = ti.min(count, source_capacity)
    keep_count = ti.min(count, ti.min(requested, destination_capacity))

    # Match the legacy NumPy lexsort order, including duplicate coordinates.
    for source_index in range(count):
        y_value = source_keypoints[source_index, 0]
        x_value = source_keypoints[source_index, 1]
        rank = 0
        for other_index in range(count):
            other_y = source_keypoints[other_index, 0]
            other_x = source_keypoints[other_index, 1]
            if (
                other_y < y_value
                or (
                    other_y == y_value
                    and (
                        other_x < x_value
                        or (
                            other_x == x_value
                            and other_index < source_index
                        )
                    )
                )
            ):
                rank += 1
        if rank < keep_count:
            destination_keypoints[rank, 0] = y_value
            destination_keypoints[rank, 1] = x_value

    for destination_index in range(destination_capacity):
        if destination_index >= keep_count:
            destination_keypoints[destination_index, 0] = 0.0
            destination_keypoints[destination_index, 1] = 0.0

    counter[0] = keep_count


@ti.kernel
def compact_matches_to_points_kernel(
    results: ti.types.ndarray(ti.f32, ndim=2),
    result_offset: ti.i32,
    segment_length: ti.i32,
    coordinate_scale: ti.f32,
    output_offset: ti.i32,
    segment_index: ti.i32,
    segment_counts: ti.types.ndarray(ti.i32, ndim=1),
    points_ref: ti.types.ndarray(ti.f32, ndim=2),
    points_supp: ti.types.ndarray(ti.f32, ndim=2),
    counter: ti.types.ndarray(ti.i32, ndim=1),
):
    """Compact one packed-match segment into a resident point segment."""
    first = ti.max(0, result_offset)
    available = ti.max(0, results.shape[0] - first)
    length = ti.min(ti.max(0, segment_length), available)
    valid_count = 0
    # Keep the bounded prefix scan deterministic while avoiding O(N^2) work.
    ti.loop_config(serialize=True)
    for index in range(length):
        row = first + index
        if results[row, 5] > 0.5:
            destination = output_offset + valid_count
            if destination < points_ref.shape[0]:
                points_ref[destination, 0] = results[row, 0] * coordinate_scale
                points_ref[destination, 1] = results[row, 1] * coordinate_scale
                points_supp[destination, 0] = results[row, 2] * coordinate_scale
                points_supp[destination, 1] = results[row, 3] * coordinate_scale
            valid_count += 1
    counter[0] = valid_count
    if segment_index >= 0 and segment_index < segment_counts.shape[0]:
        segment_counts[segment_index] = valid_count


@ti.kernel
def pack_compacted_points_kernel(
    segmented_ref: ti.types.ndarray(ti.f32, ndim=2),
    segmented_supp: ti.types.ndarray(ti.f32, ndim=2),
    segment_offsets: ti.types.ndarray(ti.i32, ndim=1),
    segment_counts: ti.types.ndarray(ti.i32, ndim=1),
    segment_count: ti.i32,
    points_ref: ti.types.ndarray(ti.f32, ndim=2),
    points_supp: ti.types.ndarray(ti.f32, ndim=2),
    counter: ti.types.ndarray(ti.i32, ndim=1),
):
    """Pack all resident pyramid point segments into one contiguous view."""
    level_count = ti.min(
        ti.max(0, segment_count),
        ti.min(segment_offsets.shape[0], segment_counts.shape[0]),
    )
    destination_offset = 0
    total = 0
    ti.loop_config(serialize=True)
    for segment in range(level_count):
        count = ti.max(0, segment_counts[segment])
        source_offset = ti.max(0, segment_offsets[segment])

        for local_index in range(count):
            source_index = source_offset + local_index
            destination_index = destination_offset + local_index
            if (
                source_index < segmented_ref.shape[0]
                and destination_index < points_ref.shape[0]
            ):
                points_ref[destination_index, 0] = segmented_ref[source_index, 0]
                points_ref[destination_index, 1] = segmented_ref[source_index, 1]
                points_supp[destination_index, 0] = segmented_supp[source_index, 0]
                points_supp[destination_index, 1] = segmented_supp[source_index, 1]
        destination_offset += count
        total += count
    counter[0] = ti.min(total, points_ref.shape[0])

@ti.func
def compute_centroid_angle(src: ti.template(), cy: int, cx: int, h: int, w: int) -> ti.f32:
    m10 = 0.0
    m01 = 0.0
    for u in range(-15, 16):
        for v in range(-15, 16):
            if u*u + v*v <= 225:
                ny = cy + u
                nx = cx + v
                if ny >= 0 and ny < h and nx >= 0 and nx < w:
                    val = src[ny, nx]
                    m10 += float(v) * val
                    m01 += float(u) * val
    angle = 0.0
    if m10 != 0.0 or m01 != 0.0:
        angle = ti.atan2(m01, m10)
    return angle

@ti.kernel
def compute_descriptors_kernel(
    src: ti.types.ndarray(ti.f32, ndim=2),
    kps: ti.types.ndarray(ti.f32, ndim=2),
    pattern: ti.types.ndarray(ti.f32, ndim=2),
    desc: ti.types.ndarray(ti.i32, ndim=2),
    counter: ti.types.ndarray(ti.i32, ndim=1),
    h: int, w: int
):
    """Mengekstrak deskriptor M-LDB (486-bit binary) di GPU sesuai paper asli AKAZE."""
    num_kps = counter[0]
    ti.loop_config(block_dim=64)
    for i in range(kps.shape[0]):
        if i < num_kps:
            cy = int(kps[i, 0])
            cx = int(kps[i, 1])
            
            angle = compute_centroid_angle(src, cy, cx, h, w)
            cos_a = ti.cos(angle)
            sin_a = ti.sin(angle)
            
            # Buat buffer lokal deskriptor (16 * 32 = 512 bit)
            desc_val = ti.Vector([0]*16)
            bit_idx = 0
            
            # --- Level 1: Grid 2x2 (4 sel, 6 perbandingan, 18 bit) ---
            I_2 = ti.Vector([0.0]*4)
            Gu_2 = ti.Vector([0.0]*4)
            Gv_2 = ti.Vector([0.0]*4)
            for row in range(2):
                for col in range(2):
                    idx = row * 2 + col
                    u_min = -10.0 + float(col) * 10.0
                    v_min = -10.0 + float(row) * 10.0
                    for sy in range(4):
                        for sx in range(4):
                            u = u_min + (float(sx) + 0.5) * 2.5
                            v = v_min + (float(sy) + 0.5) * 2.5
                            rx = u * cos_a - v * sin_a
                            ry = u * sin_a + v * cos_a
                            px = cx + int(rx)
                            py = cy + int(ry)
                            
                            val = get_pixel_clamp(src, py, px, h, w)
                            gx = 0.5 * (get_pixel_clamp(src, py, px + 1, h, w) - get_pixel_clamp(src, py, px - 1, h, w))
                            gy = 0.5 * (get_pixel_clamp(src, py + 1, px, h, w) - get_pixel_clamp(src, py - 1, px, h, w))
                            
                            gu = gx * cos_a + gy * sin_a
                            gv = -gx * sin_a + gy * cos_a
                            
                            I_2[idx] += val
                            Gu_2[idx] += gu
                            Gv_2[idx] += gv
                            
            for a in range(4):
                for b in range(a + 1, 4):
                    if I_2[a] > I_2[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gu_2[a] > Gu_2[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gv_2[a] > Gv_2[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1

            # --- Level 2: Grid 3x3 (9 sel, 36 perbandingan, 108 bit) ---
            I_3 = ti.Vector([0.0]*9)
            Gu_3 = ti.Vector([0.0]*9)
            Gv_3 = ti.Vector([0.0]*9)
            for row in range(3):
                for col in range(3):
                    idx = row * 3 + col
                    u_min = -10.0 + float(col) * (20.0 / 3.0)
                    v_min = -10.0 + float(row) * (20.0 / 3.0)
                    for sy in range(4):
                        for sx in range(4):
                            u = u_min + (float(sx) + 0.5) * (5.0 / 3.0)
                            v = v_min + (float(sy) + 0.5) * (5.0 / 3.0)
                            rx = u * cos_a - v * sin_a
                            ry = u * sin_a + v * cos_a
                            px = cx + int(rx)
                            py = cy + int(ry)
                            
                            val = get_pixel_clamp(src, py, px, h, w)
                            gx = 0.5 * (get_pixel_clamp(src, py, px + 1, h, w) - get_pixel_clamp(src, py, px - 1, h, w))
                            gy = 0.5 * (get_pixel_clamp(src, py + 1, px, h, w) - get_pixel_clamp(src, py - 1, px, h, w))
                            
                            gu = gx * cos_a + gy * sin_a
                            gv = -gx * sin_a + gy * cos_a
                            
                            I_3[idx] += val
                            Gu_3[idx] += gu
                            Gv_3[idx] += gv
                            
            for a in range(9):
                for b in range(a + 1, 9):
                    if I_3[a] > I_3[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gu_3[a] > Gu_3[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gv_3[a] > Gv_3[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1

            # --- Level 3: Grid 4x4 (16 sel, 120 perbandingan, 360 bit) ---
            I_4 = ti.Vector([0.0]*16)
            Gu_4 = ti.Vector([0.0]*16)
            Gv_4 = ti.Vector([0.0]*16)
            for row in range(4):
                for col in range(4):
                    idx = row * 4 + col
                    u_min = -10.0 + float(col) * 5.0
                    v_min = -10.0 + float(row) * 5.0
                    for sy in range(4):
                        for sx in range(4):
                            u = u_min + (float(sx) + 0.5) * 1.25
                            v = v_min + (float(sy) + 0.5) * 1.25
                            rx = u * cos_a - v * sin_a
                            ry = u * sin_a + v * cos_a
                            px = cx + int(rx)
                            py = cy + int(ry)
                            
                            val = get_pixel_clamp(src, py, px, h, w)
                            gx = 0.5 * (get_pixel_clamp(src, py, px + 1, h, w) - get_pixel_clamp(src, py, px - 1, h, w))
                            gy = 0.5 * (get_pixel_clamp(src, py + 1, px, h, w) - get_pixel_clamp(src, py - 1, px, h, w))
                            
                            gu = gx * cos_a + gy * sin_a
                            gv = -gx * sin_a + gy * cos_a
                            
                            I_4[idx] += val
                            Gu_4[idx] += gu
                            Gv_4[idx] += gv
                            
            for a in range(16):
                for b in range(a + 1, 16):
                    if I_4[a] > I_4[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gu_4[a] > Gu_4[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1
                    if Gv_4[a] > Gv_4[b]:
                        desc_val[bit_idx // 32] |= (1 << (bit_idx % 32))
                    bit_idx += 1

            # Simpan buffer biner ke array deskriptor output
            for d in range(16):
                desc[i, d] = desc_val[d]

@ti.func
def popcount32(x: ti.u32) -> int:
    """Hardware-accelerated Popcount menggunakan instruksi hardware native."""
    return ti.cast(popcnt(x), ti.i32)

@ti.kernel
def hamming_matcher_kernel(
    desc1: ti.types.ndarray(ti.i32, ndim=2),
    desc2: ti.types.ndarray(ti.i32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    counter1: ti.types.ndarray(ti.i32, ndim=1),
    counter2: ti.types.ndarray(ti.i32, ndim=1),
    ratio_threshold: ti.f32
):
    """Pencocokan deskriptor Hamming dengan Lowe's Ratio Test, Register Caching, dan Early Pruning di GPU (untuk 486-bit M-LDB)."""
    num_kps1 = counter1[0]
    num_kps2 = counter2[0]
    ti.loop_config(block_dim=64)
    for i in range(desc1.shape[0]):
        if i < num_kps1:
            best_j = -1
            best_dist = 512
            second_best_dist = 512
            
            # L0 Register Cache: Cache 16 kata (512-bit) deskriptor query ke register thread lokal
            d1_0 = desc1[i, 0]
            d1_1 = desc1[i, 1]
            d1_2 = desc1[i, 2]
            d1_3 = desc1[i, 3]
            d1_4 = desc1[i, 4]
            d1_5 = desc1[i, 5]
            d1_6 = desc1[i, 6]
            d1_7 = desc1[i, 7]
            d1_8 = desc1[i, 8]
            d1_9 = desc1[i, 9]
            d1_10 = desc1[i, 10]
            d1_11 = desc1[i, 11]
            d1_12 = desc1[i, 12]
            d1_13 = desc1[i, 13]
            d1_14 = desc1[i, 14]
            d1_15 = desc1[i, 15]
            
            for j in range(desc2.shape[0]):
                if j < num_kps2:
                    # Tahap 1: Evaluasi 8 kata pertama (256-bit)
                    dist1 = (
                        popcount32(ti.cast(d1_0 ^ desc2[j, 0], ti.u32)) +
                        popcount32(ti.cast(d1_1 ^ desc2[j, 1], ti.u32)) +
                        popcount32(ti.cast(d1_2 ^ desc2[j, 2], ti.u32)) +
                        popcount32(ti.cast(d1_3 ^ desc2[j, 3], ti.u32)) +
                        popcount32(ti.cast(d1_4 ^ desc2[j, 4], ti.u32)) +
                        popcount32(ti.cast(d1_5 ^ desc2[j, 5], ti.u32)) +
                        popcount32(ti.cast(d1_6 ^ desc2[j, 6], ti.u32)) +
                        popcount32(ti.cast(d1_7 ^ desc2[j, 7], ti.u32))
                    )
                    
                    # Early Pruning: Evaluasi tahap 2 hanya jika jarak parsial berpotensi < second_best_dist dan <= 152
                    if dist1 < second_best_dist and dist1 <= AKAZE_MAX_HAMMING_DISTANCE:
                        dist2 = (
                            popcount32(ti.cast(d1_8 ^ desc2[j, 8], ti.u32)) +
                            popcount32(ti.cast(d1_9 ^ desc2[j, 9], ti.u32)) +
                            popcount32(ti.cast(d1_10 ^ desc2[j, 10], ti.u32)) +
                            popcount32(ti.cast(d1_11 ^ desc2[j, 11], ti.u32)) +
                            popcount32(ti.cast(d1_12 ^ desc2[j, 12], ti.u32)) +
                            popcount32(ti.cast(d1_13 ^ desc2[j, 13], ti.u32)) +
                            popcount32(ti.cast(d1_14 ^ desc2[j, 14], ti.u32)) +
                            popcount32(ti.cast(d1_15 ^ desc2[j, 15], ti.u32))
                        )
                        dist = dist1 + dist2
                        if dist < best_dist:
                            second_best_dist = best_dist
                            best_dist = dist
                            best_j = j
                        elif dist < second_best_dist:
                            second_best_dist = dist
                            
            if (
                float(best_dist) <= float(second_best_dist) * ratio_threshold
                and best_dist <= AKAZE_MAX_HAMMING_DISTANCE
            ):
                matches[i, 0] = best_j
                matches[i, 1] = best_dist
            else:
                matches[i, 0] = -1
                matches[i, 1] = -1

@ti.kernel
def pack_matches_kernel(
    kps1: ti.types.ndarray(ti.f32, ndim=2),
    kps2: ti.types.ndarray(ti.f32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    counter1: ti.types.ndarray(ti.i32, ndim=1),
    counter2: ti.types.ndarray(ti.i32, ndim=1),
    results: ti.types.ndarray(ti.f32, ndim=2)
):
    """Mengemas keypoint koordinat x, y dan kecocokan ke satu buffer hasil float32 di GPU."""
    num_kps1 = counter1[0]
    num_kps2 = counter2[0]
    ti.loop_config(block_dim=256)
    for i in range(kps1.shape[0]):
        if i < num_kps1:
            idx2 = matches[i, 0]
            dist = matches[i, 1]
            if idx2 >= 0 and idx2 < num_kps2:
                results[i, 0] = kps1[i, 1]  # x1
                results[i, 1] = kps1[i, 0]  # y1
                results[i, 2] = kps2[idx2, 1] # x2
                results[i, 3] = kps2[idx2, 0] # y2
                results[i, 4] = ti.cast(dist, ti.f32)
                results[i, 5] = 1.0
            else:
                results[i, 5] = 0.0
        else:
            results[i, 5] = 0.0


@ti.kernel
def pack_matches_offset_kernel(
    kps1: ti.types.ndarray(ti.f32, ndim=2),
    kps2: ti.types.ndarray(ti.f32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    counter1: ti.types.ndarray(ti.i32, ndim=1),
    counter2: ti.types.ndarray(ti.i32, ndim=1),
    results: ti.types.ndarray(ti.f32, ndim=2),
    result_offset: ti.i32,
):
    """Pack one level into a shared result buffer for a single readback."""
    num_kps1 = counter1[0]
    num_kps2 = counter2[0]
    ti.loop_config(block_dim=256)
    for i in range(kps1.shape[0]):
        out_i = result_offset + i
        if i < num_kps1:
            idx2 = matches[i, 0]
            dist = matches[i, 1]
            if idx2 >= 0 and idx2 < num_kps2:
                results[out_i, 0] = kps1[i, 1]
                results[out_i, 1] = kps1[i, 0]
                results[out_i, 2] = kps2[idx2, 1]
                results[out_i, 3] = kps2[idx2, 0]
                results[out_i, 4] = ti.cast(dist, ti.f32)
                results[out_i, 5] = 1.0
            else:
                results[out_i, 5] = 0.0
        else:
            results[out_i, 5] = 0.0
# Selesai Modul Detektor AKAZE

