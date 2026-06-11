import taichi as ti
import math

@ti.func
def get_circle_offset(i: ti.template()):
    """Mendapatkan offset koordinat untuk 16 piksel lingkaran FAST."""
    offsets = [
        ti.Vector([0, 3]), ti.Vector([1, 3]), ti.Vector([2, 2]), ti.Vector([3, 1]),
        ti.Vector([3, 0]), ti.Vector([3, -1]), ti.Vector([2, -2]), ti.Vector([1, -3]),
        ti.Vector([0, -3]), ti.Vector([-1, -3]), ti.Vector([-2, -2]), ti.Vector([-3, -1]),
        ti.Vector([-3, 0]), ti.Vector([-3, 1]), ti.Vector([-2, 2]), ti.Vector([-1, 3])
    ]
    return offsets[i]

@ti.func
def compute_dynamic_fast_score(src: ti.template(), y: int, x: int) -> ti.f32:
    center = src[y, x]
    
    # 1. Ekstrak statistik lokal (Ring 16 piksel)
    max_ring = 0.0
    min_ring = 1.0
    
    for i in ti.static(range(16)):
        off = get_circle_offset(i)
        val = src[y + off.y, x + off.x]
        max_ring = ti.max(max_ring, val)
        min_ring = ti.min(min_ring, val)
        
    # 2. Threshold Dinamis (Adaptasi terhadap tekstur aspal/awan)
    local_contrast = max_ring - min_ring
    dynamic_thresh = ti.max(0.015, local_contrast * 0.4) 
    
    # 3. Hitung Skor dengan Vision Booster
    score = 0.0
    bright_count = 0
    dark_count = 0
    
    # Vision Booster: Mengukur pengali kontras lokal jika di atas noise floor
    boost_factor = 1.0
    if local_contrast > 0.003:
        boost_factor = 1.0 / (local_contrast + 0.01)
        
    for i in ti.static(range(16)):
        off = get_circle_offset(i)
        val = src[y + off.y, x + off.x]
        diff = center - val
        
        diff_boosted = diff * boost_factor
        thresh_boosted = dynamic_thresh * boost_factor
        
        if diff_boosted > thresh_boosted:
            bright_count += 1
            score += diff
        elif diff_boosted < -thresh_boosted:
            dark_count += 1
            score -= diff
            
    # 4. STAR SUPPORT (Dukungan Langit Malam / Bintang)
    # Bintang dideteksi jika jauh lebih terang dari lingkaran sekitarnya
    if center > (max_ring + 0.03):
        score += (center - max_ring) * 10.0
        bright_count = 16
        
    # 5. Threshold count (FAST-9)
    final_score = 0.0
    if bright_count >= 9 or dark_count >= 9:
        final_score = score
        
    return final_score

@ti.kernel
def compute_score_map(
    src: ti.types.ndarray(ti.f32, ndim=2),
    score_map: ti.types.ndarray(ti.f32, ndim=2),
    h: int, w: int,
    margin: int
):
    """Pass 1: Membangun peta skor FAST dinamis dengan margin sensor."""
    for y, x in ti.ndrange(h, w):
        if y >= margin and y < h - margin and x >= margin and x < w - margin:
            score_map[y, x] = compute_dynamic_fast_score(src, y, x)
        else:
            score_map[y, x] = 0.0

@ti.kernel
def extract_grid_keypoints(
    score_map: ti.types.ndarray(ti.f32, ndim=2),
    keypoints: ti.types.ndarray(ti.f32, ndim=2), 
    counter: ti.types.ndarray(ti.i32, ndim=1),
    h: int, w: int,
    grid_size: int,
    threshold: ti.f32
):
    """Pass 2: Adaptive Non-Maximal Suppression (ANMS) Berbasis Grid dengan filter threshold."""
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
                s = score_map[y, x]
                if s > best_score:
                    best_score = s
                    best_x = x
                    best_y = y
                    
        if best_score > threshold:
            idx = ti.atomic_add(counter[0], 1)
            if idx < keypoints.shape[0]:
                keypoints[idx, 0] = ti.cast(best_y, ti.f32) # y coordinate
                keypoints[idx, 1] = ti.cast(best_x, ti.f32) # x coordinate

@ti.func
def compute_centroid_angle(src: ti.template(), cy: int, cx: int, h: int, w: int) -> ti.f32:
    """Menghitung sudut orientasi centroid intensitas untuk kebal rotasi."""
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

@ti.func
def get_pixel_nearest(src: ti.template(), y: ti.f32, x: ti.f32, h: int, w: int) -> ti.f32:
    """Mendapatkan nilai piksel terdekat dengan validasi batas gambar."""
    ny = int(y)
    nx = int(x)
    val = 0.0
    if ny >= 0 and ny < h and nx >= 0 and nx < w:
        val = src[ny, nx]
    return val

@ti.kernel
def _compute_descriptors_kernel(
    src: ti.types.ndarray(ti.f32, ndim=2),
    kps: ti.types.ndarray(ti.f32, ndim=2),
    pattern: ti.types.ndarray(ti.f32, ndim=2),
    desc: ti.types.ndarray(ti.i32, ndim=2),
    h: int, w: int,
    num_kps: int
):
    """Mengekstrak deskriptor Oriented BRIEF 256-bit di GPU."""
    for i in range(num_kps):
        cy = int(kps[i, 0])
        cx = int(kps[i, 1])
        
        angle = 0.0
        cos_a = ti.cos(angle)
        sin_a = ti.sin(angle)
        
        for d in range(8):
            val = 0
            for b in range(32):
                pidx = d * 32 + b
                x1 = pattern[pidx, 0]
                y1 = pattern[pidx, 1]
                x2 = pattern[pidx, 2]
                y2 = pattern[pidx, 3]
                
                # Rotasikan titik pola sampling BRIEF
                x1_rot = x1 * cos_a - y1 * sin_a
                y1_rot = x1 * sin_a + y1 * cos_a
                x2_rot = x2 * cos_a - y2 * sin_a
                y2_rot = x2 * sin_a + y2 * cos_a
                
                # Ambil sampel intensitas piksel
                p1_val = get_pixel_nearest(src, float(cy) + y1_rot, float(cx) + x1_rot, h, w)
                p2_val = get_pixel_nearest(src, float(cy) + y2_rot, float(cx) + x2_rot, h, w)
                
                if p1_val < p2_val:
                    val = val | (1 << b)
                    
            desc[i, d] = val

@ti.func
def popcount32(x: ti.u32) -> int:
    """Algoritma paralel O(1) Popcount untuk menghitung jumlah bit 1."""
    x = x - ((x >> 1) & 0x55555555)
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333)
    x = (x + (x >> 4)) & 0x0F0F0F0F
    x = x + (x >> 8)
    x = x + (x >> 16)
    return int(x & 0x3F)

@ti.kernel
def _hamming_matcher_kernel(
    desc1: ti.types.ndarray(ti.i32, ndim=2),
    desc2: ti.types.ndarray(ti.i32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    num_kps1: int,
    num_kps2: int,
    ratio_threshold: ti.f32
):
    """Pencocokan Hamming Matcher dengan Lowe's Ratio Test di GPU."""
    for i in range(num_kps1):
        best_j = -1
        best_dist = 256
        second_best_dist = 256
        
        for j in range(num_kps2):
            dist = 0
            for k in range(8):
                diff = ti.cast(desc1[i, k] ^ desc2[j, k], ti.u32)
                dist += popcount32(diff)
                
            if dist < best_dist:
                second_best_dist = best_dist
                best_dist = dist
                best_j = j
            elif dist < second_best_dist:
                second_best_dist = dist
                
        # Lowe's ratio test filter + absolute distance limit (80)
        if float(best_dist) <= float(second_best_dist) * ratio_threshold and best_dist <= 80:
            matches[i, 0] = best_j
            matches[i, 1] = best_dist
        else:
            matches[i, 0] = -1
            matches[i, 1] = -1