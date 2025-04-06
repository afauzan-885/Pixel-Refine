#ifndef BLOCK_MATCHING_UTILS_HPP
#define BLOCK_MATCHING_UTILS_HPP

#include <vector>
#include <opencv2/core.hpp> // Perlu cv::Mat untuk deklarasi
#include "motion_metrics_types.hpp" // Perlu definisi BlockMatchResult

// --- Deklarasi Fungsi ---
// (Implementasi ada di block_matching_utils.cpp, kecuali inline)

/**
 * @brief Menghitung Mean Absolute Difference (MAD) antara dua blok cv::Mat.
 * (Fungsi inline didefinisikan langsung di header)
 */
inline float calculate_block_mad(const cv::Mat& block1, const cv::Mat& block2);

/**
 * @brief Menghitung standar deviasi dari sekumpulan nilai MAD.
 */
float calculate_mad_stddev(const std::vector<float>& mad_values);

/**
 * @brief Menghitung skor keyakinan (confidence) untuk sebuah match blok.
 */
float calculate_match_confidence(const BlockMatchResult& result, float motion_threshold);

/**
 * @brief Mencari MAD minimum, kedua minimum, dan semua nilai MAD dalam area pencarian.
 */
BlockMatchResult find_best_block_match(
    const cv::Mat& current_block,
    const cv::Mat& reference_tile,
    int block_r_start, int block_c_start,
    int search_radius);


// --- Definisi Fungsi Inline ---
#include <opencv2/imgproc.hpp> // Diperlukan untuk implementasi inline (absdiff, sum)
#include <opencv2/core/utility.hpp> // Untuk CV_Assert

inline float calculate_block_mad(const cv::Mat& block1, const cv::Mat& block2)
{
    CV_Assert(block1.size() == block2.size() && block1.type() == block2.type());
    // Pastikan tipe float multi-channel (misal CV_32FC1, CV_32FC3)
    CV_Assert(block1.depth() == CV_32F);

    if (block1.empty() || block2.empty()) {
        return std::numeric_limits<float>::max();
    }

    cv::Mat diff;
    cv::absdiff(block1, block2, diff);

    cv::Scalar sad_per_channel = cv::sum(diff);
    double total_sad = 0.0;
    for (int i = 0; i < diff.channels(); ++i) {
        total_sad += sad_per_channel[i];
    }

    float num_elements = static_cast<float>(block1.total() * block1.channels());

    if (num_elements <= 0) {
        return 0.0f;
    }

    return static_cast<float>(total_sad / num_elements);
}


#endif // BLOCK_MATCHING_UTILS_HPP