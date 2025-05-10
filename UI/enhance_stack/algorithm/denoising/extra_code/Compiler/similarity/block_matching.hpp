// block_matching.hpp
#ifndef BLOCK_MATCHING_HPP
#define BLOCK_MATCHING_HPP

#include <opencv2/core.hpp>
#include <vector>
#include <limits>

namespace MotionMatching {

struct BlockMatchResult
{
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    int matches_found = 0;
    bool success = false;
    int best_match_r = -1;
    int best_match_c = -1;
};

/**
 * @brief Menemukan blok terbaik yang cocok dalam tile referensi menggunakan MAD terbobot gradien.
 *
 * @param current_block_gray Blok dari frame saat ini (CV_32FC1).
 * @param reference_tile_gray Tile dari frame referensi tempat mencari (CV_32FC1).
 * @param block_r_start_in_ref_tile Posisi baris awal (pusat) pencarian di reference_tile_gray.
 * @param block_c_start_in_ref_tile Posisi kolom awal (pusat) pencarian di reference_tile_gray.
 * @param search_radius Radius pencarian di sekitar posisi awal.
 * @param gradient_weight_factor Faktor untuk pembobotan gradien.
 * @param stability_epsilon Nilai epsilon untuk stabilitas numerik.
 * @return BlockMatchResult Hasil pencocokan blok.
 */
BlockMatchResult find_best_block_match_mad(
    const cv::Mat &current_block_gray,
    const cv::Mat &reference_tile_gray,
    int block_r_start_in_ref_tile,
    int block_c_start_in_ref_tile,
    int search_radius,
    float gradient_weight_factor,
    float stability_epsilon
);

}
#endif 