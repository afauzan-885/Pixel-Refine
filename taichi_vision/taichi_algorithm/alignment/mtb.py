"""
Median Threshold Bitmap (MTB) Alignment - Taichi GPU
Dedicated for High Dynamic Range (HDR) alignment with extreme lighting differences.
Based on Greg Ward's MTB algorithm.
"""

import numpy as np
import os
import importlib

TAICHI_AVAILABLE = False
ti = None
tm = None

if os.environ.get("AOT_MODE", "1") == "0":
    try:
        ti = importlib.import_module("taichi")
        tm = importlib.import_module("taichi.math")
        TAICHI_AVAILABLE = True
    except ImportError:
        pass

try:
    from .. import common
    from ..pyramid import pyramid
    from ..taichi_worker import ti_thread
except ImportError:
    pass


if TAICHI_AVAILABLE:
    @ti.kernel
    def _compute_histogram(img: ti.types.ndarray(dtype=ti.f32, ndim=2), hist: ti.types.ndarray(dtype=ti.i32, ndim=1)):
        h, w = img.shape
        for i, j in ti.ndrange(h, w):
            # Convert float [0, 1] to int [0, 255]
            val = ti.cast(tm.clamp(img[i, j] * 255.0, 0.0, 255.0), ti.i32)
            ti.atomic_add(hist[val], 1)

    @ti.kernel
    def _compute_bitmaps(img: ti.types.ndarray(dtype=ti.f32, ndim=2), 
                        bitmap: ti.types.ndarray(dtype=ti.i32, ndim=2),
                        exclusion: ti.types.ndarray(dtype=ti.i32, ndim=2),
                        median_val: ti.f32,
                        tolerance: ti.f32):
        h, w = img.shape
        for i, j in ti.ndrange(h, w):
            val = img[i, j]
            # Bitmap: 1 if > median, 0 otherwise
            if val > median_val:
                bitmap[i, j] = 1
            else:
                bitmap[i, j] = 0
                
            # Exclusion map: 1 if pixel is safely away from median, 0 if close (noise)
            if ti.abs(val - median_val) > tolerance:
                exclusion[i, j] = 1
            else:
                exclusion[i, j] = 0

    @ti.kernel
    def _compute_mtb_error_single(
        bitmap1: ti.types.ndarray(dtype=ti.i32, ndim=2),
        exclusion1: ti.types.ndarray(dtype=ti.i32, ndim=2),
        bitmap2: ti.types.ndarray(dtype=ti.i32, ndim=2),
        exclusion2: ti.types.ndarray(dtype=ti.i32, ndim=2),
        dx: ti.i32,
        dy: ti.i32
    ) -> ti.i32:
        h, w = bitmap1.shape
        err = 0
        for i, j in ti.ndrange(h, w):
            ni = i + dy
            nj = j + dx
            if 0 <= ni < h and 0 <= nj < w:
                b1 = bitmap1[i, j]
                e1 = exclusion1[i, j]
                b2 = bitmap2[ni, nj]
                e2 = exclusion2[ni, nj]
                diff = b1 ^ b2
                valid = e1 & e2
                err += valid * diff
            else:
                # Penalize out of bounds so it prefers smaller shifts when equal
                err += 1
        return err

    # =========================================================================
    # AOT-compatible error kernel: writes result to output buffer (no return)
    # =========================================================================
    @ti.kernel
    def _compute_mtb_error_to_buf(
        bitmap1: ti.types.ndarray(dtype=ti.i32, ndim=2),
        exclusion1: ti.types.ndarray(dtype=ti.i32, ndim=2),
        bitmap2: ti.types.ndarray(dtype=ti.i32, ndim=2),
        exclusion2: ti.types.ndarray(dtype=ti.i32, ndim=2),
        error_buf: ti.types.ndarray(dtype=ti.i32, ndim=1),
        dx: ti.i32,
        dy: ti.i32
    ):
        """AOT-compatible error computation. Writes error to error_buf[0]."""
        h, w = bitmap1.shape
        err = 0
        for i, j in ti.ndrange(h, w):
            ni = i + dy
            nj = j + dx
            if 0 <= ni < h and 0 <= nj < w:
                b1 = bitmap1[i, j]
                e1 = exclusion1[i, j]
                b2 = bitmap2[ni, nj]
                e2 = exclusion2[ni, nj]
                diff = b1 ^ b2
                valid = e1 & e2
                err += valid * diff
            else:
                err += 1
        error_buf[0] = err


def get_median(img_gpu):
    """Calculate median value of an image using GPU histogram."""
    hist = np.zeros(256, dtype=np.int32)
    hist_gpu, _ = common.ensure_taichi_field(hist, dtype=ti.i32)
    _compute_histogram(img_gpu, hist_gpu)
    hist_np = hist_gpu.to_numpy()
    
    total = img_gpu.shape[0] * img_gpu.shape[1]
    cum_sum = 0
    for i in range(256):
        cum_sum += hist_np[i]
        if cum_sum >= total / 2:
            return i / 255.0
    return 0.5


@ti_thread
def align_mtb(ref_img: np.ndarray, target_img: np.ndarray, max_levels: int = 6, tolerance: float = 4.0/255.0, mode: str = 'simple') -> tuple:
    """
    Computes the (dx, dy) translation to align target_img to ref_img using Median Threshold Bitmap.
    Ideal for HDR images with significant lighting/exposure differences.
    Returns:
        (dx, dy): Integer shift applied to target_img to match ref_img.
    """
    if os.environ.get("AOT_MODE", "1") == "1":
        # Stub for AOT mode if not yet implemented there.
        # Fallback to NumPy version or similar if strictly AOT.
        pass

    if not TAICHI_AVAILABLE:
        raise ImportError("Taichi not available")

    # 1. Convert to Grayscale
    ref_gray = common.cvtColor(ref_img, common.COLOR_BGR2GRAY) if len(ref_img.shape) == 3 else ref_img
    tgt_gray = common.cvtColor(target_img, common.COLOR_BGR2GRAY) if len(target_img.shape) == 3 else target_img

    # 2. Build Pyramids on GPU
    ref_pyr = pyramid.build_image_pyramid(ref_gray, n_levels=max_levels)
    tgt_pyr = pyramid.build_image_pyramid(tgt_gray, n_levels=max_levels)
    
    current_dx = 0
    current_dy = 0
    
    # 3. Coarse-to-fine shift estimation
    # Iterate from smallest (coarsest) to largest (original) image
    for level in reversed(range(len(ref_pyr))):
        ref_level_np = ref_pyr[level]
        tgt_level_np = tgt_pyr[level]
        
        # Upload to GPU
        ref_gpu, _ = common.ensure_taichi_field(ref_level_np, dtype=ti.f32)
        tgt_gpu, _ = common.ensure_taichi_field(tgt_level_np, dtype=ti.f32)
        
        h, w = ref_level_np.shape
        
        # Scale previous shifts by 2
        current_dx *= 2
        current_dy *= 2
        
        # Compute medians
        ref_med = get_median(ref_gpu)
        tgt_med = get_median(tgt_gpu)
        
        # Allocate bitmaps and exclusion maps
        ref_bitmap, _ = common.ensure_taichi_field(np.zeros((h, w), dtype=np.int32), dtype=ti.i32)
        ref_excl, _ = common.ensure_taichi_field(np.zeros((h, w), dtype=np.int32), dtype=ti.i32)
        tgt_bitmap, _ = common.ensure_taichi_field(np.zeros((h, w), dtype=np.int32), dtype=ti.i32)
        tgt_excl, _ = common.ensure_taichi_field(np.zeros((h, w), dtype=np.int32), dtype=ti.i32)
        
        # Compute maps
        _compute_bitmaps(ref_gpu, ref_bitmap, ref_excl, float(ref_med), float(tolerance))
        _compute_bitmaps(tgt_gpu, tgt_bitmap, tgt_excl, float(tgt_med), float(tolerance))
        
        # Search 3x3 neighborhood around current shift
        best_err = 2**31 - 1
        best_offset_x = 0
        best_offset_y = 0
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                test_dx = current_dx + dx
                test_dy = current_dy + dy
                
                # Compute error using Taichi kernel tree reduction
                err = _compute_mtb_error_single(
                    ref_bitmap, ref_excl,
                    tgt_bitmap, tgt_excl,
                    test_dx, test_dy
                )
                
                if err < best_err:
                    best_err = err
                    best_offset_x = dx
                    best_offset_y = dy
                    
        # Update shift
        current_dx += best_offset_x
        current_dy += best_offset_y

    return current_dx, current_dy


def align_mtb_complex(ref_img: np.ndarray, target_img: np.ndarray, max_kps: int = 1000, ransac_thresh: float = 3.0):
    """Feature-based refinement using OFB detector + GPU descriptors/matcher + RANSAC homography.

    Returns:
        dict with keys: 'homography'(3x3 or None), 'matches' (list), 'kps_ref', 'kps_tgt', 'inliers' (mask)
    """
    import cv2

    # 1. Optionally compute coarse translation via MTB to quickly align
    try:
        dx, dy = align_mtb(ref_img, target_img)
    except Exception:
        dx, dy = 0, 0

    # Apply coarse translation to target for better matching (use cv2.warpAffine)
    h, w = ref_img.shape[:2]
    M = np.array([[1, 0, dx], [0, 1, dy]], dtype=np.float32)
    tgt_warp = cv2.warpAffine(target_img, M, (w, h), flags=cv2.INTER_LINEAR)

    # 2. Detect keypoints using OFB detector (GPU)
    try:
        from ..features.ofb import detect_ofb_keypoints
    except Exception:
        detect_ofb_keypoints = None

    if detect_ofb_keypoints is None:
        # fallback to ORB if OFB not available
        orb = cv2.ORB_create(nfeatures=max_kps)
        kps_ref = orb.detect(cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY), None)
        kps_tgt = orb.detect(cv2.cvtColor(tgt_warp, cv2.COLOR_BGR2GRAY), None)
    else:
        kps_ref = detect_ofb_keypoints(cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY), max_kps=max_kps)
        kps_tgt = detect_ofb_keypoints(cv2.cvtColor(tgt_warp, cv2.COLOR_BGR2GRAY), max_kps=max_kps)

    # 3. Compute descriptors on GPU via wrappers
    try:
        desc_ref = compute_descriptors_gpu(cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY), kps_ref, max_kps=max_kps)
        desc_tgt = compute_descriptors_gpu(cv2.cvtColor(tgt_warp, cv2.COLOR_BGR2GRAY), kps_tgt, max_kps=max_kps)
    except Exception:
        desc_ref = None
        desc_tgt = None

    matches = []
    if desc_ref is not None and desc_tgt is not None and desc_ref.shape[0] > 0 and desc_tgt.shape[0] > 0:
        raw_matches = match_descriptors_gpu(desc_ref, desc_tgt, ratio=0.8)
        # Convert to cv2-style matches and point arrays
        pts_ref = []
        pts_tgt = []
        for i, j, d in raw_matches:
            if i < len(kps_ref) and j < len(kps_tgt):
                y1, x1 = kps_ref[i].pt[1], kps_ref[i].pt[0]
                y2, x2 = kps_tgt[j].pt[1], kps_tgt[j].pt[0]
                pts_ref.append((x1, y1))
                pts_tgt.append((x2, y2))
                matches.append((i, j, d))

        if len(pts_ref) >= 4:
            pts_ref_np = np.array(pts_ref, dtype=np.float32)
            pts_tgt_np = np.array(pts_tgt, dtype=np.float32)
            H, mask = cv2.findHomography(pts_tgt_np, pts_ref_np, cv2.RANSAC, ransac_thresh)
            inliers = mask.ravel().tolist() if mask is not None else None
        else:
            H = None
            inliers = None
    else:
        H = None
        inliers = None

    return {
        'homography': H,
        'matches': matches,
        'kps_ref': kps_ref,
        'kps_tgt': kps_tgt,
        'inliers': inliers,
        'coarse_dx': dx,
        'coarse_dy': dy,
    }


@ti_thread
def align_mtb_mode(ref_img: np.ndarray, target_img: np.ndarray, max_levels: int = 6, tolerance: float = 4.0/255.0, mode: str = 'simple'):
    """Compatibility wrapper: choose 'simple' or 'complex'."""
    if mode == 'simple':
        return align_mtb(ref_img, target_img, max_levels=max_levels, tolerance=tolerance)
    elif mode == 'complex':
        return align_mtb_complex(ref_img, target_img)
    else:
        raise ValueError('Unknown mode')


# ---- GPU descriptor / matcher wrappers using OFB kernels ----
try:
    from ..features import ofb
except Exception:
    ofb = None


def _make_brief_pattern(radius=9, num_bits=256):
    """Create a deterministic BRIEF sampling pattern (num_bits x 4): x1,y1,x2,y2
    Coordinates are floats in range [-radius, radius]."""
    rng = np.random.RandomState(12345)
    pattern = rng.uniform(-radius, radius, size=(num_bits, 4)).astype(np.float32)
    return pattern


def compute_descriptors_gpu(img_gray: np.ndarray, keypoints: list, max_kps: int = 1000):
    """Compute GPU-oriented BRIEF descriptors using OFB's kernel.

    Returns descriptor numpy array shape (num_kps, 8) dtype=np.int32 (8 x 32-bit words).
    """
    if ofb is None:
        raise ImportError("OFB module not available for GPU descriptors")

    # Convert keypoints list (cv2.KeyPoint) to numpy (y,x)
    import cv2

    h, w = img_gray.shape[:2]
    kps_np = np.zeros((max_kps, 2), dtype=np.float32)
    for i, kp in enumerate(keypoints[:max_kps]):
        kps_np[i, 0] = kp.pt[1]  # y
        kps_np[i, 1] = kp.pt[0]  # x

    num_kps = min(len(keypoints), max_kps)

    # Ensure taichi fields
    img_gpu, _ = common.ensure_taichi_field(img_gray.astype(np.float32), dtype=ti.f32)
    kps_gpu, _ = common.ensure_taichi_field(kps_np, dtype=ti.f32)

    pattern = _make_brief_pattern()
    pattern_gpu, _ = common.ensure_taichi_field(pattern, dtype=ti.f32)

    desc_gpu = common.get_temp_buffer((max_kps, 8), dtype=ti.i32)

    # Call kernel
    ofb._compute_descriptors_kernel(img_gpu, kps_gpu, pattern_gpu, desc_gpu, h, w, int(num_kps))

    desc_np = desc_gpu.to_numpy()[:num_kps].astype(np.int32)

    # Release temporaries
    common.release_temp_buffer(desc_gpu)
    common.release_temp_buffer(kps_gpu)
    common.release_temp_buffer(pattern_gpu)

    return desc_np


def match_descriptors_gpu(desc1: np.ndarray, desc2: np.ndarray, ratio: float = 0.8):
    """Match two descriptor sets on GPU using OFB's Hamming matcher kernel.

    Returns matches as list of (idx_in_desc1, idx_in_desc2, distance) for valid matches.
    """
    if ofb is None:
        raise ImportError("OFB module not available for GPU matcher")

    n1 = desc1.shape[0]
    n2 = desc2.shape[0]

    desc1_gpu, _ = common.ensure_taichi_field(desc1.astype(np.int32), dtype=ti.i32)
    desc2_gpu, _ = common.ensure_taichi_field(desc2.astype(np.int32), dtype=ti.i32)

    matches_gpu = common.get_temp_buffer((n1, 2), dtype=ti.i32)

    ofb._hamming_matcher_kernel(desc1_gpu, desc2_gpu, matches_gpu, int(n1), int(n2), float(ratio))

    matches_np = matches_gpu.to_numpy()
    result = []
    for i in range(n1):
        j = int(matches_np[i, 0])
        dist = int(matches_np[i, 1])
        if j >= 0:
            result.append((i, j, dist))

    common.release_temp_buffer(matches_gpu)
    common.release_temp_buffer(desc1_gpu)
    common.release_temp_buffer(desc2_gpu)

    return result
