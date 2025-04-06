#ifndef IMAGE_ACCUMULATOR_HPP
#define IMAGE_ACCUMULATOR_HPP

// Tidak perlu include OpenCV di sini jika hanya menggunakan pointer mentah di signature
// Tapi jika ingin lebih jelas bisa ditambahkan #include <opencv2/core/hal/interface.h> untuk CV_32FC

extern "C" {
    /**
     * @brief Mengakumulasi tile-tile dari citra saat ini ke citra final berdasarkan bobot kesamaan.
     */
    void accumulate_tiles_jit(
        float *final_image_ptr, float *weight_map_ptr,
        const float *current_image_ptr, const float *reference_image_ptr,
        const float *base_window_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h, int w, int channels,
        float motion_threshold, float scale,
        int mbm_block_h, int mbm_block_w, int mbm_search_radius
    );
} // end extern "C"

#endif // IMAGE_ACCUMULATOR_HPP