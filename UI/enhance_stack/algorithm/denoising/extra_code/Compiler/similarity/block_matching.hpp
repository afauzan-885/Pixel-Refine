#ifndef BLOCK_MATCHING_HPP
#define BLOCK_MATCHING_HPP

#include <opencv2/core.hpp>
#include <vector>
#include <limits>

namespace MotionMatching {

struct MBMBuffers {
    cv::Mat diff_workspace;   // Untuk calculate_plain_mad_32f_optimized
    cv::Mat grad_x;           // Untuk Scharr
    cv::Mat grad_y;           // Untuk Scharr
    cv::Mat grad_mag_current; // Untuk magnitude
};

struct BlockMatchResult
{
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    int matches_found = 0;
    bool success = false;
    int best_match_r = -1;
    int best_match_c = -1;
};

BlockMatchResult find_best_block_match_mad(
    const cv::Mat &current_block_gray,
    const cv::Mat &reference_tile_gray,
    int block_r_start_in_ref_tile,
    int block_c_start_in_ref_tile,
    int search_radius,
    float gradient_weight_factor,
    float stability_epsilon,
    MBMBuffers& buffers 
);

} 
#endif