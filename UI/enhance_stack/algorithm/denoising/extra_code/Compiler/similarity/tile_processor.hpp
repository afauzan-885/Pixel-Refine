#ifndef TILE_PROCESSOR_HPP
#define TILE_PROCESSOR_HPP

#include <opencv2/core.hpp> // Perlu cv::Mat

// Deklarasi fungsi yang akan dipanggil dari luar (mungkin Python)
// Gunakan extern "C" untuk memastikan C linkage (tidak ada name mangling C++)
extern "C" {
    /**
     * @brief Menghitung bobot kesamaan (similarity) dan threshold gerak adaptif antara dua tile citra.
     */
    void compute_tile_motion_metrics(
        const cv::Mat& current_tile, const cv::Mat& reference_tile,
        int block_h, int block_w,
        int search_radius,
        float motion_threshold,
        float *similarity_weight, // Output
        float *adaptive_threshold // Output
    );
} // end extern "C"

#endif // TILE_PROCESSOR_HPP