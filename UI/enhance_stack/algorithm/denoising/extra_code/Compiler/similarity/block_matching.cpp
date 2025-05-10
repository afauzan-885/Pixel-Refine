// block_matching.cpp
#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <algorithm>           
#include <cmath>               

namespace MotionMatching {
namespace Internal {
static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray) {
    CV_Assert(block1_gray.size() == block2_gray.size() && block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1);
    if (block1_gray.empty()) return std::numeric_limits<float>::max();

    cv::Mat diff;
    cv::absdiff(block1_gray, block2_gray, diff);
    cv::Scalar total_sad_scalar = cv::sum(diff);
    double total_sad = total_sad_scalar.val[0];
    float num_elements = static_cast<float>(block1_gray.total());
    if (num_elements <= 0) return std::numeric_limits<float>::max();
    return static_cast<float>(total_sad / num_elements);
}

static float calculate_gradient_weighted_mad_internal(
    const cv::Mat &block1_gray,
    const cv::Mat &block2_gray,
    const cv::Mat &grad_mag_block1,
    float grad_weight_factor,
    float stab_epsilon)
{
    CV_Assert(block1_gray.size() == block2_gray.size() && grad_mag_block1.size() == block1_gray.size());
    CV_Assert(block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1 && grad_mag_block1.type() == CV_32FC1);

    if (block1_gray.empty() || block2_gray.empty()) { // grad_mag_block1 bisa kosong jika blok terlalu kecil
        return std::numeric_limits<float>::max();
    }

    double weighted_sad_sum = 0.0;
    double total_weight_sum = 0.0;

    for (int row = 0; row < block1_gray.rows; ++row) {
        const float *p1_row = block1_gray.ptr<float>(row);
        const float *p2_row = block2_gray.ptr<float>(row);
        const float *mag_row = grad_mag_block1.ptr<float>(row);

        for (int col = 0; col < block1_gray.cols; ++col) {
            float magnitude = mag_row[col]; 

            float weight = 1.0f + grad_weight_factor * magnitude;
            total_weight_sum += weight;
            float diff = std::abs(p1_row[col] - p2_row[col]);
            weighted_sad_sum += diff * weight;
        }
    }
    double denominator = total_weight_sum + stab_epsilon;

    if (denominator <= stab_epsilon) {
        return calculate_plain_mad_32f(block1_gray, block2_gray);
    }
    return static_cast<float>(weighted_sad_sum / denominator);
}

} 

BlockMatchResult find_best_block_match_mad(
    const cv::Mat &current_block_gray,
    const cv::Mat &reference_tile_gray,
    int block_r_start_in_ref_tile,
    int block_c_start_in_ref_tile,
    int search_radius,
    float gradient_weight_factor,
    float stability_epsilon)
{
    BlockMatchResult result;

    if (current_block_gray.empty() || reference_tile_gray.empty()) {
        result.success = false;
        return result;
    }
    CV_Assert(current_block_gray.type() == CV_32FC1 && reference_tile_gray.type() == CV_32FC1);

    int tile_h_ref = reference_tile_gray.rows;
    int tile_w_ref = reference_tile_gray.cols;
    int current_block_h = current_block_gray.rows;
    int current_block_w = current_block_gray.cols;

    if (current_block_h <= 0 || current_block_w <= 0 ||
        tile_h_ref < current_block_h || tile_w_ref < current_block_w) {
        result.success = false;
        return result;
    }

    cv::Mat grad_x, grad_y, grad_mag_current;
    if (current_block_h >= 3 && current_block_w >= 3) {
        cv::Scharr(current_block_gray, grad_x, CV_32F, 1, 0, 1, 0, cv::BORDER_REPLICATE); // border replicate
        cv::Scharr(current_block_gray, grad_y, CV_32F, 0, 1, 1, 0, cv::BORDER_REPLICATE); // border replicate
        cv::magnitude(grad_x, grad_y, grad_mag_current);
    } else {
        grad_mag_current = cv::Mat::zeros(current_block_gray.size(), CV_32FC1);
    }

    int search_center_r = block_r_start_in_ref_tile;
    int search_center_c = block_c_start_in_ref_tile;

    int search_r_start_abs = std::max(0, search_center_r - search_radius);
    int search_c_start_abs = std::max(0, search_center_c - search_radius);
    int search_r_end_abs = std::min(tile_h_ref - current_block_h, search_center_r + search_radius);
    int search_c_end_abs = std::min(tile_w_ref - current_block_w, search_center_c + search_radius);

    if (search_r_start_abs > search_r_end_abs || search_c_start_abs > search_c_end_abs) {
        result.success = false;
        return result;
    }

    for (int r_search_ref = search_r_start_abs; r_search_ref <= search_r_end_abs; ++r_search_ref) {
        for (int c_search_ref = search_c_start_abs; c_search_ref <= search_c_end_abs; ++c_search_ref) {
            cv::Rect ref_block_roi(c_search_ref, r_search_ref, current_block_w, current_block_h);
            const cv::Mat ref_block_candidate_gray = reference_tile_gray(ref_block_roi); // ROI

            if(ref_block_candidate_gray.empty()){
                continue;
            }

            float current_metric_score = Internal::calculate_gradient_weighted_mad_internal(
                current_block_gray,
                ref_block_candidate_gray,
                grad_mag_current,
                gradient_weight_factor,
                stability_epsilon
            );
            result.matches_found++;

            if (current_metric_score < result.min_mad) {
                result.second_min_mad = result.min_mad;
                result.min_mad = current_metric_score;
                result.best_match_r = r_search_ref;
                result.best_match_c = c_search_ref;
                result.success = true;
            } else if (current_metric_score < result.second_min_mad) {
                 result.second_min_mad = current_metric_score;
            }
        }
    }
    return result;
}

}