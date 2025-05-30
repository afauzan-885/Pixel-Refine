#ifndef DFT_merging_HPP
#define DFT_merging_HPP

#include <opencv2/core.hpp>
#include <omp.h>

namespace MotionMerging {

struct DFTBuffers {
    cv::Mat current_padded;
    cv::Mat ref_padded;
    cv::Mat current_dft;
    cv::Mat ref_dft;
    cv::Mat merged_dft;
    cv::Mat temp_spatial_merged;

    // Optional cache ukuran optimal DFT (untuk optimasi lebih lanjut)
    int cached_rows = -1;
    int cached_cols = -1;
};

struct FrequencyMergeResult {
    cv::Mat merged_block_gray; 
    float merge_confidence = 0.0f;
    bool success = false;
};

// Fungsi utama merging blok grayscale di domain frekuensi
FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon,
    DFTBuffers& buffers
);

} // namespace MotionMerging

#endif
