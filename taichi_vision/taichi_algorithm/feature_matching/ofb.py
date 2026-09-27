import taichi as ti
from taichi.math import popcnt
import math
import numpy as np


class TaichiKeyPoint:
    """Small OpenCV-compatible point record without importing OpenCV."""

    def __init__(self, x, y, size=15.0, response=0.0):
        self.pt = (float(x), float(y))
        self.size = float(size)
        self.response = float(response)

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
    
    final_score = 0.0
    is_star = center > (max_ring + 0.03)

    # Early-Exit: Lewati evaluasi penuh jika kontras lokal di bawah ambang batas dan bukan bintang
    if local_contrast >= dynamic_thresh or is_star:
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
        if is_star:
            score += (center - max_ring) * 10.0
            bright_count = 16
            
        # 5. Threshold count (FAST-9)
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
    ti.loop_config(block_dim=256)
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
    """Pass 2: Adaptive Non-Maximal Suppression (ANMS) Berbasis Grid dengan filter threshold dan sub-pixel refinement."""
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
                s = score_map[y, x]
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
                    s_center = score_map[best_y, best_x]
                    s_left   = score_map[best_y, best_x - 1]
                    s_right  = score_map[best_y, best_x + 1]
                    s_up     = score_map[best_y - 1, best_x]
                    s_down   = score_map[best_y + 1, best_x]
                    
                    denom_x = 2.0 * s_center - s_left - s_right
                    if denom_x > 1e-5:
                        dx = 0.5 * (s_right - s_left) / denom_x
                        
                    denom_y = 2.0 * s_center - s_up - s_down
                    if denom_y > 1e-5:
                        dy = 0.5 * (s_down - s_up) / denom_y
                        
                    # Clamp shifts to [-0.5, 0.5] to keep them within the pixel boundary
                    dx = ti.max(-0.5, ti.min(0.5, dx))
                    dy = ti.max(-0.5, ti.min(0.5, dy))

                keypoints[idx, 0] = ti.cast(best_y, ti.f32) + dy # y coordinate
                keypoints[idx, 1] = ti.cast(best_x, ti.f32) + dx # x coordinate


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

    # Detection uses an atomic counter, so source row order depends on the
    # backend scheduler.  Stable ranking matches the legacy NumPy lexsort
    # order: (y, x, source_index).  Source and destination are distinct in
    # the resident pipeline, so all reads remain valid during the pass.
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
    # A serialized scan is deterministic and O(N).  The former parallel
    # prefix-per-row implementation was O(N^2) and made resident matching
    # measurably slower for the bounded feature capacity.
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
    counter: ti.types.ndarray(ti.i32, ndim=1),
    h: int, w: int
):
    """Mengekstrak deskriptor Oriented BRIEF 256-bit di GPU secara penuh."""
    num_kps = counter[0]
    ti.loop_config(block_dim=64)
    for i in range(kps.shape[0]):
        if i < num_kps:
            cy = int(kps[i, 0])
            cx = int(kps[i, 1])
            
            angle = compute_centroid_angle(src, cy, cx, h, w)
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
    """Hardware-accelerated Popcount menggunakan instruksi native hardware (LLVM POPCNT / CUDA __popc / SPIR-V OpBitCount)."""
    return ti.cast(popcnt(x), ti.i32)

@ti.kernel
def _hamming_matcher_kernel(
    desc1: ti.types.ndarray(ti.i32, ndim=2),
    desc2: ti.types.ndarray(ti.i32, ndim=2),
    matches: ti.types.ndarray(ti.i32, ndim=2),
    counter1: ti.types.ndarray(ti.i32, ndim=1),
    counter2: ti.types.ndarray(ti.i32, ndim=1),
    ratio_threshold: ti.f32
):
    """Pencocokan Hamming Matcher dengan Lowe's Ratio Test dan Register Caching di GPU secara penuh."""
    num_kps1 = counter1[0]
    num_kps2 = counter2[0]
    ti.loop_config(block_dim=64)
    for i in range(desc1.shape[0]):
        if i < num_kps1:
            best_j = -1
            best_dist = 256
            second_best_dist = 256
            
            # L0 Register Cache: Simpan 256-bit deskriptor query ke register thread lokal
            d1_0 = desc1[i, 0]
            d1_1 = desc1[i, 1]
            d1_2 = desc1[i, 2]
            d1_3 = desc1[i, 3]
            d1_4 = desc1[i, 4]
            d1_5 = desc1[i, 5]
            d1_6 = desc1[i, 6]
            d1_7 = desc1[i, 7]
            
            for j in range(desc2.shape[0]):
                if j < num_kps2:
                    # Unrolled Hamming distance evaluation dengan native hardware popcount
                    dist = (
                        popcount32(ti.cast(d1_0 ^ desc2[j, 0], ti.u32)) +
                        popcount32(ti.cast(d1_1 ^ desc2[j, 1], ti.u32)) +
                        popcount32(ti.cast(d1_2 ^ desc2[j, 2], ti.u32)) +
                        popcount32(ti.cast(d1_3 ^ desc2[j, 3], ti.u32)) +
                        popcount32(ti.cast(d1_4 ^ desc2[j, 4], ti.u32)) +
                        popcount32(ti.cast(d1_5 ^ desc2[j, 5], ti.u32)) +
                        popcount32(ti.cast(d1_6 ^ desc2[j, 6], ti.u32)) +
                        popcount32(ti.cast(d1_7 ^ desc2[j, 7], ti.u32))
                    )
                    
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
    """Pack matches into a shared multi-level result buffer.

    ``result_offset`` keeps the graph shape dynamic while allowing the
    caller to perform one host readback after all pyramid levels finish.
    The arithmetic and row ordering are identical to ``pack_matches_kernel``.
    """
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

# --- Python Wrappers ---
try:
    from .. import common
    from ..taichi_worker import ti_thread
    import numpy as np
except ImportError:
    pass

@ti_thread
def detect_ofb_keypoints(img_gray: np.ndarray, max_kps: int = 1000, grid_size: int = 30, threshold: float = 0.05) -> list:
    """
    Ekstrak keypoint menggunakan algoritma Optical Flow Based (OFB) FAST + ANMS Grid.
    Mengembalikan list berisi objek TaichiKeyPoint dengan atribut ``pt``.
    """
    if len(img_gray.shape) == 3:
        img_gray = common.cvtColor(img_gray, common.COLOR_BGR2GRAY)
        
    h, w = img_gray.shape
    
    # 1. Pastikan gambar di GPU
    img_gpu, _ = common.ensure_taichi_field(img_gray, dtype=ti.f32)
    
    # 2. Alokasi buffer
    score_map_gpu = common.get_temp_buffer((h, w), dtype=ti.f32)
    keypoints_gpu = common.get_temp_buffer((max_kps, 2), dtype=ti.f32)
    counter_gpu = common.get_temp_buffer((1,), dtype=ti.i32)
    
    score_map_gpu.fill(0)
    keypoints_gpu.fill(0)
    counter_gpu.fill(0)
    
    # 3. Jalankan kernel
    compute_score_map(img_gpu, score_map_gpu, h, w, 3)
    extract_grid_keypoints(score_map_gpu, keypoints_gpu, counter_gpu, h, w, grid_size, float(threshold))
    
    # 4. Ambil hasil
    num_kps = counter_gpu.to_numpy()[0]
    num_kps = min(num_kps, max_kps)
    
    kps_np = keypoints_gpu.to_numpy()[:num_kps]
    
    # Bersihkan buffer
    common.release_temp_buffer(score_map_gpu)
    common.release_temp_buffer(keypoints_gpu)
    common.release_temp_buffer(counter_gpu)
    
    # kps_np berisi (y, x); the public point record uses (x, y).
    return [TaichiKeyPoint(float(x), float(y), 15.0) for y, x in kps_np]
