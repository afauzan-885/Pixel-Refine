#ifndef SPATIAL_MERGING_HPP 
#define SPATIAL_MERGING_HPP

#include <opencv2/core.hpp>

namespace MotionMerging { // Namespace tetap sama

struct SpatialMergeResult { // Struct tetap sama
    cv::Mat merged_block_gray;
    float merge_confidence = 0.0f;
    bool success = false;
};

// Nama fungsi tetap sama untuk kompatibilitas dengan pemanggil
SpatialMergeResult spatial_merge_block(
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon
);

} // namespace MotionMerging

#endif // SPATIAL_MERGING_HPP