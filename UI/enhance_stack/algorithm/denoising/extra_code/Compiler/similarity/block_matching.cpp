// block_matching.cpp
#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <algorithm>
#include <cmath>
#include <limits> // Pastikan ini ada

namespace MotionMatching {
namespace Internal {

// Fungsi baru yang dioptimalkan untuk menggunakan workspace
static float calculate_plain_mad_32f_optimized(
    const cv::Mat &block1_gray,
    const cv::Mat &block2_gray,
    cv::Mat &diff_workspace) // Menerima workspace
{
    CV_Assert(block1_gray.size() == block2_gray.size() &&
              block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1 &&
              diff_workspace.size() == block1_gray.size() && diff_workspace.type() == CV_32FC1);

    if (block1_gray.empty()) return std::numeric_limits<float>::max();

    cv::absdiff(block1_gray, block2_gray, diff_workspace); // Menggunakan workspace
    cv::Scalar total_sad_scalar = cv::sum(diff_workspace);
    double total_sad = total_sad_scalar.val[0];
    float num_elements = static_cast<float>(block1_gray.total());

    if (num_elements <= 0) return std::numeric_limits<float>::max();
    return static_cast<float>(total_sad / num_elements);
}

// Fungsi asli, dipertahankan untuk fallback atau jika tidak ada workspace
static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray) {
    CV_Assert(block1_gray.size() == block2_gray.size() && block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1);
    if (block1_gray.empty()) return std::numeric_limits<float>::max();

    cv::Mat diff; // Alokasi lokal
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

    if (block1_gray.empty()) { // Cek block1_gray.empty() sudah cukup
        return std::numeric_limits<float>::max();
    }

    double weighted_sad_sum = 0.0;
    double total_weight_sum = 0.0;
    const int rows = block1_gray.rows;
    const int cols = block1_gray.cols;

   #pragma omp parallel for reduction(+:weighted_sad_sum, total_weight_sum) schedule(static)
    for (int row = 0; row < rows; ++row) {
        const float *p1_row = block1_gray.ptr<float>(row);
        const float *p2_row = block2_gray.ptr<float>(row);
        const float *mag_row = grad_mag_block1.ptr<float>(row);

        for (int col = 0; col < cols; ++col) {
            float magnitude = mag_row[col];
            float weight = 1.0f + grad_weight_factor * magnitude;
            total_weight_sum += weight;
            float diff_val = std::abs(p1_row[col] - p2_row[col]); // ganti nama variabel agar tidak bentrok jika ada 'diff' cv::Mat
            weighted_sad_sum += diff_val * weight;
        }
    }

    double denominator = total_weight_sum + stab_epsilon;

    if (denominator <= stab_epsilon) {
        // Menggunakan versi standar calculate_plain_mad_32f untuk fallback ini
        return calculate_plain_mad_32f(block1_gray, block2_gray);
    }
    return static_cast<float>(weighted_sad_sum / denominator);
}

} // namespace Internal

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

    bool use_plain_mad_path = (std::abs(gradient_weight_factor) < stability_epsilon) ||
                              (current_block_h < 3 || current_block_w < 3);

    cv::Mat grad_mag_current;
    cv::Mat diff_workspace; // Dideklarasikan di sini

    if (use_plain_mad_path) {
        diff_workspace.create(current_block_gray.size(), CV_32FC1);
    } else {
        cv::Mat grad_x, grad_y;
        cv::Scharr(current_block_gray, grad_x, CV_32F, 1, 0, 1, 0, cv::BORDER_REPLICATE);
        cv::Scharr(current_block_gray, grad_y, CV_32F, 0, 1, 1, 0, cv::BORDER_REPLICATE);
        cv::magnitude(grad_x, grad_y, grad_mag_current);
    }

    int search_center_r = block_r_start_in_ref_tile;
    int search_center_c = block_c_start_in_ref_tile;

    int search_r_start_abs = std::max(0, search_center_r - search_radius);
    int search_c_start_abs = std::max(0, search_center_c - search_radius);
    int search_r_end_abs = std::min(tile_h_ref - current_block_h, search_center_r + search_radius);
    int search_c_end_abs = std::min(tile_w_ref - current_block_w, search_center_c + search_radius);

    for (int r_search_ref = search_r_start_abs; r_search_ref <= search_r_end_abs; ++r_search_ref) {
        for (int c_search_ref = search_c_start_abs; c_search_ref <= search_c_end_abs; ++c_search_ref) {
            cv::Rect ref_block_roi(c_search_ref, r_search_ref, current_block_w, current_block_h);
            const cv::Mat ref_block_candidate_gray = reference_tile_gray(ref_block_roi);

            if(ref_block_candidate_gray.empty() || ref_block_candidate_gray.rows != current_block_h || ref_block_candidate_gray.cols != current_block_w){
                continue;
            }

            float current_metric_score;
            if (use_plain_mad_path) {
                // ***** KESALAHAN ADA DI SINI, GUNAKAN VERSI _OPTIMIZED *****
                current_metric_score = Internal::calculate_plain_mad_32f_optimized( // <--- PERBAIKAN
                    current_block_gray,
                    ref_block_candidate_gray,
                    diff_workspace // Sekarang argumennya cocok
                );
            } else {
                current_metric_score = Internal::calculate_gradient_weighted_mad_internal(
                    current_block_gray,
                    ref_block_candidate_gray,
                    grad_mag_current,
                    gradient_weight_factor,
                    stability_epsilon
                );
            }
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

} // namespace MotionMatching