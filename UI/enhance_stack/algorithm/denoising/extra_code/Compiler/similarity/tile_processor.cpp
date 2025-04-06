#include "tile_processor.hpp"       // Header sendiri
#include "block_matching_utils.hpp" // Perlu fungsi-fungsi matching
#include "motion_metrics_config.hpp"// Perlu konstanta
#include "motion_metrics_types.hpp" // Perlu BlockMatchResult (meskipun sudah include di utils.hpp)

#include <cmath>
#include <limits>
#include <algorithm> // Untuk std::min, std::max

// Definisi fungsi compute_tile_motion_metrics
// TIDAK perlu extern "C" di sini, hanya di deklarasi header
void compute_tile_motion_metrics(
    const cv::Mat& current_tile, const cv::Mat& reference_tile,
    int block_h, int block_w,
    int search_radius,
    float motion_threshold,
    float *similarity_weight,
    float *adaptive_threshold
) {
    using namespace MotionMetricsConfig;

    int tile_h = current_tile.rows;
    int tile_w = current_tile.cols;

    *similarity_weight = 0.0f;
    *adaptive_threshold = motion_threshold;

    if (tile_h <= 0 || tile_w <= 0 || block_h <= 0 || block_w <= 0 ||
        current_tile.empty() || reference_tile.empty() ||
        current_tile.size() != reference_tile.size() ||
        current_tile.type() != reference_tile.type())
    {
        return;
    }

    int num_blocks_h = (block_h > 0) ? (tile_h + block_h - 1) / block_h : 0;
    int num_blocks_w = (block_w > 0) ? (tile_w + block_w - 1) / block_w : 0;
    int num_blocks = num_blocks_h * num_blocks_w;

    if (num_blocks == 0) {
        float diff = calculate_block_mad(current_tile, reference_tile); // Panggil fungsi utilitas
        float sim_denominator = motion_threshold + STABILITY_EPSILON;
        if (sim_denominator > STABILITY_EPSILON) {
            *similarity_weight = std::exp(-std::max(0.0f, diff) / sim_denominator);
        } else {
            *similarity_weight = (diff <= STABILITY_EPSILON) ? 1.0f : 0.0f;
        }
        *similarity_weight = std::max(0.0f, std::min(1.0f, *similarity_weight));
        return;
    }

    double sum_adjusted_min_mad = 0.0;
    double sum_block_mad_stddev = 0.0;
    int valid_blocks_processed = 0;

    for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
            int block_r_start = bh_idx * block_h;
            int block_c_start = bw_idx * block_w;

            int current_block_h = std::min(block_h, tile_h - block_r_start);
            int current_block_w = std::min(block_w, tile_w - block_c_start);

            if (current_block_h <= 0 || current_block_w <= 0) continue;

            cv::Rect current_block_roi(block_c_start, block_r_start, current_block_w, current_block_h);
            const cv::Mat current_block = current_tile(current_block_roi);

            // Panggil fungsi utilitas
            BlockMatchResult block_result = find_best_block_match(
                current_block, reference_tile,
                block_r_start, block_c_start, search_radius
            );

            if (!block_result.success) {
                 if (block_r_start + current_block_h <= tile_h && block_c_start + current_block_w <= tile_w) {
                     cv::Rect ref_block_orig_roi(block_c_start, block_r_start, current_block_w, current_block_h);
                     const cv::Mat ref_block_orig = reference_tile(ref_block_orig_roi);
                     // Panggil fungsi utilitas
                     block_result.min_mad = calculate_block_mad(current_block, ref_block_orig);
                     block_result.second_min_mad = block_result.min_mad;
                     block_result.all_mads.push_back(block_result.min_mad);
                     block_result.matches_found = 1;
                     block_result.success = true;
                 } else {
                    continue;
                 }
            }

            // Panggil fungsi utilitas
            float mad_stddev = calculate_mad_stddev(block_result.all_mads);
            sum_block_mad_stddev += static_cast<double>(mad_stddev);

            // Panggil fungsi utilitas
            float match_confidence = calculate_match_confidence(block_result, motion_threshold);

            float adjusted_mad = block_result.min_mad / (match_confidence + CONFIDENCE_EPSILON);
            adjusted_mad = std::max(0.0f, adjusted_mad);
            sum_adjusted_min_mad += static_cast<double>(adjusted_mad);

            valid_blocks_processed++;
        }
    }

    if (valid_blocks_processed > 0) {
        float average_adjusted_mad = static_cast<float>(sum_adjusted_min_mad / valid_blocks_processed);
        float sim_denominator = motion_threshold + STABILITY_EPSILON;
        if (sim_denominator > STABILITY_EPSILON) {
            *similarity_weight = std::exp(-average_adjusted_mad / sim_denominator);
        } else {
             *similarity_weight = (average_adjusted_mad <= STABILITY_EPSILON) ? 1.0f : 0.0f;
        }
        *similarity_weight = std::max(0.0f, std::min(1.0f, *similarity_weight));

        float average_mad_stddev = static_cast<float>(sum_block_mad_stddev / valid_blocks_processed);
        *adaptive_threshold = motion_threshold + ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR * average_mad_stddev;
        *adaptive_threshold = std::max(0.0f, *adaptive_threshold);
    }
}