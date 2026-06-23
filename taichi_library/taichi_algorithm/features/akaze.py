import taichi as ti
import math
import numpy as np

@ti.func
def get_pixel_clamp(src: ti.template(), y: int, x: int, h: int, w: int) -> ti.f32:
    ny = ti.max(0, ti.min(h - 1, y))
    nx = ti.max(0, ti.min(w - 1, x))
    return src[ny, nx]

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
        hessian_map[y, x] = ti.max(0.0, det)

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
    x = x - ((x >> 1) & 0x55555555)
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
    x = (x + (x >> 4)) & 0x0F0F0F0F
    x = x + (x >> 8)
    x = x + (x >> 16)
    return int(x & 0x3F)

@ti.kernel
def hamming_matcher_kernel(
    desc1: ti.types.ndarray(ti.i32, ndim=2),
    desc2: ti.types.ndarray(ti.i32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    counter1: ti.types.ndarray(ti.i32, ndim=1),
    counter2: ti.types.ndarray(ti.i32, ndim=1),
    ratio_threshold: ti.f32
):
    """Pencocokan deskriptor Hamming dengan Lowe's Ratio Test di GPU (untuk 486-bit)."""
    num_kps1 = counter1[0]
    num_kps2 = counter2[0]
    for i in range(desc1.shape[0]):
        if i < num_kps1:
            best_j = -1
            best_dist = 512
            second_best_dist = 512
            
            for j in range(desc2.shape[0]):
                if j < num_kps2:
                    dist = 0
                    for k in range(16):
                        diff = ti.cast(desc1[i, k] ^ desc2[j, k], ti.u32)
                        dist += popcount32(diff)
                        
                    if dist < best_dist:
                        second_best_dist = best_dist
                        best_dist = dist
                        best_j = j
                    elif dist < second_best_dist:
                        second_best_dist = dist
                        
            if float(best_dist) <= float(second_best_dist) * ratio_threshold and best_dist <= 160:
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
# Selesai Modul Detektor AKAZE

