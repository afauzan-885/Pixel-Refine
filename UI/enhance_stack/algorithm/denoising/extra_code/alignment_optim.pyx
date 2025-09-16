# alignment_optim.pyx

import numpy as np
import cv2
cimport numpy as np
from cython.parallel import prange
import cython

ctypedef np.float32_t DTYPE_t

@cython.boundscheck(False)
@cython.wraparound(False)
@cython.cdivision(True)
def refine_flow_layer_cython(
    np.ndarray[DTYPE_t, ndim=2] ref_layer_np,
    np.ndarray[DTYPE_t, ndim=2] comp_layer_np,
    np.ndarray[DTYPE_t, ndim=3] initial_flow_np,
    int tile_h,
    int tile_w,
    int search_dist=2):

    # =========================================================================
    # SEMUA DEKLARASI CDEF DIKUMPULKAN DI BAGIAN ATAS FUNGSI
    # =========================================================================
    cdef DTYPE_t[:, :] ref_layer = ref_layer_np
    cdef DTYPE_t[:, :] comp_layer = comp_layer_np
    cdef DTYPE_t[:, :, :] initial_flow = initial_flow_np
    cdef np.ndarray[DTYPE_t, ndim=3] refined_flow_np = initial_flow_np.copy()
    cdef DTYPE_t[:, :, :] refined_flow = refined_flow_np

    cdef int h = ref_layer.shape[0]
    cdef int w = ref_layer.shape[1]
    cdef int current_tile_h = min(tile_h, h // 4)
    cdef int current_tile_w = min(tile_w, w // 4)
    cdef int step_y = max(current_tile_h // 2, 1)
    cdef int step_x = max(current_tile_w // 2, 1)
    
    # Variabel loop luar
    cdef int y
    
    # --- SEMUA VARIABEL YANG SEBELUMNYA DI DALAM LOOP, SEKARANG DI SINI ---
    cdef int x_inner, center_y, center_x, init_dy, init_dx
    cdef int search_y_start, search_x_start, search_y_end, search_x_end
    cdef int best_dx, best_dy, comp_patch_y, comp_patch_x
    cdef int best_match_x_in_window, best_match_y_in_window
    cdef double ratio, sum_ref, sum_comp
    
    cdef np.ndarray[DTYPE_t, ndim=2] ref_tile_np, search_window_np, comp_patch_np
    cdef np.ndarray[DTYPE_t, ndim=2] corrected_search_window_np, res_np
    cdef tuple min_loc
    # =========================================================================

    if current_tile_h < 8 or current_tile_w < 8:
        return refined_flow_np
    
    for y in prange(0, h - current_tile_h + 1, step_y, nogil=True):
        for x_inner in range(0, w - current_tile_w + 1, step_x):
            center_y = y + current_tile_h // 2
            center_x = x_inner + current_tile_w // 2
            init_dy = <int>round(initial_flow[center_y, center_x, 1])
            init_dx = <int>round(initial_flow[center_y, center_x, 0])

            comp_patch_y = y + init_dy
            comp_patch_x = x_inner + init_dx
            ratio = 1.0
            
            with gil:
                if (comp_patch_y >= 0 and comp_patch_x >= 0 and
                    comp_patch_y + current_tile_h <= h and comp_patch_x + current_tile_w <= w):
                    
                    ref_tile_np = ref_layer_np[y:y + current_tile_h, x_inner:x_inner + current_tile_w]
                    comp_patch_np = comp_layer_np[comp_patch_y:comp_patch_y + current_tile_h,
                                                  comp_patch_x:comp_patch_x + current_tile_w]
                    
                    sum_ref = np.sum(ref_tile_np)
                    sum_comp = np.sum(comp_patch_np)
                    if sum_comp > 1e-9:
                        ratio = sum_ref / sum_comp
                    ratio = min(1.2, max(0.8, ratio))

            search_y_start = max(0, y + init_dy - search_dist)
            search_x_start = max(0, x_inner + init_dx - search_dist)
            search_y_end = min(h, y + init_dy + search_dist + current_tile_h)
            search_x_end = min(w, x_inner + init_dx + search_dist + current_tile_w)
            
            with gil:
                search_window_np = comp_layer_np[search_y_start:search_y_end, search_x_start:search_x_end]
                ref_tile_np = ref_layer_np[y:y + current_tile_h, x_inner:x_inner + current_tile_w]
                
                if search_window_np.shape[0] < ref_tile_np.shape[0] or search_window_np.shape[1] < ref_tile_np.shape[1]:
                    # 'continue' di dalam blok 'with gil' aman
                    continue
                
                corrected_search_window_np = search_window_np * ratio
                
                res_np = cv2.matchTemplate(corrected_search_window_np, ref_tile_np, cv2.TM_SQDIFF)
                _ , _, min_loc, _ = cv2.minMaxLoc(res_np)

            best_match_x_in_window = min_loc[0]
            best_match_y_in_window = min_loc[1]

            best_dx = (search_x_start + best_match_x_in_window) - x_inner
            best_dy = (search_y_start + best_match_y_in_window) - y
            
            # Penulisan ke memoryview bisa dilakukan tanpa gil jika tidak ada tumpang tindih
            # antara iterasi thread, yang seharusnya tidak terjadi dengan grid ini.
            refined_flow[y:y + current_tile_h, x_inner:x_inner + current_tile_w, 0] = best_dx
            refined_flow[y:y + current_tile_h, x_inner:x_inner + current_tile_w, 1] = best_dy
            
    return refined_flow_np