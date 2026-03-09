// block_matching.hpp

#ifndef BLOCK_MATCHING_HPP
#define BLOCK_MATCHING_HPP

#include <opencv2/core.hpp>
#include <vector>
#include <limits>

namespace MotionMatching {

struct MBMBuffers {
    cv::Mat diff_workspace;
    cv::Mat grad_x;
    cv::Mat grad_y;
    cv::Mat grad_mag_current;
};


struct TileMatchResult
{
    float mad_score = std::numeric_limits<float>::max(); 
    bool success = false;
};

// Spatial domain matching (gradient + Laplacian weighted MAD)
TileMatchResult calculate_tile_mad(
    const cv::Mat &current_tile_gray,
    const cv::Mat &reference_tile_gray,
    float global_noise_sigma,
    float gradient_weight_factor,
    float stability_epsilon,
    MBMBuffers& buffers
);

// Frequency domain matching (FFT-based similarity)
TileMatchResult calculate_tile_fft(
    const cv::Mat &current_tile_gray,
    const cv::Mat &reference_tile_gray,
    float global_noise_sigma
);

} // namespace MotionMatching
#endif // BLOCK_MATCHING_HPP