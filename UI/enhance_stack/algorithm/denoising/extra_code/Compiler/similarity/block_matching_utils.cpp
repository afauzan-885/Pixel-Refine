#include "block_matching_utils.hpp" // Include header pasangannya
#include "motion_metrics_config.hpp" // Perlu konstanta

// Include library lain yang dibutuhkan untuk IMPLEMENTASI
#include <cmath>
#include <limits>
#include <algorithm> // Untuk std::max, std::min
#include <opencv2/imgproc.hpp> // Untuk cv::meanStdDev
#include <opencv2/core/utility.hpp> // Untuk CV_Assert (jika ada assert tambahan di implementasi)


// --- Definisi Fungsi (yang tidak inline) ---

float calculate_mad_stddev(const std::vector<float>& mad_values) {
    if (mad_values.size() <= 1) {
        return 0.0f;
    }
    // const_cast aman di sini karena meanStdDev tidak akan memodifikasi data input
    cv::Mat mad_mat(mad_values.size(), 1, CV_32F, const_cast<float*>(mad_values.data()));
    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(mad_mat, mean_val, stddev_val);
    return static_cast<float>(stddev_val.val[0]);
}

float calculate_match_confidence(const BlockMatchResult& result, float motion_threshold)
{
    using namespace MotionMetricsConfig; // Lebih mudah pakai konstanta

    float match_confidence = 0.0f;
    float quality_denominator = CONFIDENCE_SCALE_FACTOR * motion_threshold + STABILITY_EPSILON;

    if (!result.success || result.matches_found <= 0) {
        match_confidence = 0.0f;
    } else if (result.matches_found == 1) {
        if (quality_denominator > STABILITY_EPSILON) { // Cek pembagi > 0
            match_confidence = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
             match_confidence = (result.min_mad <= CONFIDENCE_EPSILON) ? 0.5f : 0.0f;
        }
        match_confidence = std::min(0.5f, std::max(0.0f, match_confidence));
    } else {
        float ratio = 1.0f;
        if (result.second_min_mad > CONFIDENCE_EPSILON) {
            float safe_min_mad = std::max(0.0f, result.min_mad);
            ratio = safe_min_mad / result.second_min_mad;
        }
        float ratio_confidence = std::max(0.0f, 1.0f - ratio);

        float absolute_quality = 0.0f;
        if (quality_denominator > STABILITY_EPSILON) { // Cek pembagi > 0
            absolute_quality = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
            absolute_quality = (std::max(0.0f, result.min_mad) <= CONFIDENCE_EPSILON) ? 1.0f : 0.0f;
        }
        absolute_quality = std::max(0.0f, std::min(1.0f, absolute_quality));

        match_confidence = ratio_confidence * absolute_quality;
    }

    return std::max(0.0f, std::min(1.0f, match_confidence));
}


BlockMatchResult find_best_block_match(
    const cv::Mat& current_block,
    const cv::Mat& reference_tile,
    int block_r_start, int block_c_start,
    int search_radius)
{
    BlockMatchResult result; // Inisialisasi default

    int tile_h = reference_tile.rows;
    int tile_w = reference_tile.cols;
    int current_block_h = current_block.rows;
    int current_block_w = current_block.cols;

    // Cek jika blok saat ini kosong atau terlalu besar untuk tile
    if (current_block.empty() || current_block_h > tile_h || current_block_w > tile_w) {
        // Tidak bisa melakukan pencarian, kembalikan hasil default (success=false)
        return result;
    }

    int search_r_start = std::max(0, block_r_start - search_radius);
    int search_c_start = std::max(0, block_c_start - search_radius);
    int search_r_end = std::min(tile_h - current_block_h, block_r_start + search_radius);
    int search_c_end = std::min(tile_w - current_block_w, block_c_start + search_radius);

    int estimated_matches = (search_r_end - search_r_start + 1) * (search_c_end - search_c_start + 1);
    if (estimated_matches > 0) {
        result.all_mads.reserve(estimated_matches);
    }

    for (int search_r = search_r_start; search_r <= search_r_end; ++search_r) {
        for (int search_c = search_c_start; search_c <= search_c_end; ++search_c) {
            // ROI seharusnya selalu valid karena batas search_r/c_end
            cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
            const cv::Mat ref_block = reference_tile(ref_block_roi);

            // Panggil fungsi inline calculate_block_mad
            float current_mad = calculate_block_mad(current_block, ref_block);

            result.all_mads.push_back(current_mad);
            result.matches_found++;
            result.success = true;

            if (current_mad < result.min_mad) {
                result.second_min_mad = result.min_mad;
                result.min_mad = current_mad;
            } else if (current_mad < result.second_min_mad) {
                result.second_min_mad = current_mad;
            }
        }
    }

    return result;
}