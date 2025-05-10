// frequency_merging.cpp
#include "frequency_merging.hpp"
#include <opencv2/imgproc.hpp> // Untuk DFT, iDFT, copyMakeBorder
#include <vector>              // Untuk cv::Vec2f
#include <cmath>               // Untuk std::isnan, std::isinf, std::sqrt, std::pow
#include <algorithm>           // Untuk std::max, std::min
#include <iostream>            // Untuk debugging (opsional, bisa dihapus)

namespace MotionMerging {

FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon)
{
    FrequencyMergeResult result;
    result.success = false; // Default ke gagal

    // --- Validasi Input Awal ---
    if (current_block_gray.empty() || reference_block_gray.empty()) {
        // std::cerr << "Error: Input block(s) for frequency merging are empty." << std::endl;
        // Jika salah satu kosong, kembalikan blok yang tidak kosong (jika ada) atau blok kosong
        if (!current_block_gray.empty()) current_block_gray.copyTo(result.merged_block_gray);
        else if (!reference_block_gray.empty()) reference_block_gray.copyTo(result.merged_block_gray);
        // result.success tetap false
        return result;
    }

    if (current_block_gray.size() != reference_block_gray.size()) {
        // std::cerr << "Error: Input block sizes do not match for frequency merging." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback ke current block
        return result;
    }

    if (current_block_gray.type() != CV_32FC1 || reference_block_gray.type() != CV_32FC1) {
        // std::cerr << "Error: Input block types are not CV_32FC1 for frequency merging." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    int block_h = current_block_gray.rows;
    int block_w = current_block_gray.cols;

    if (block_h <= 0 || block_w <= 0) {
        // std::cerr << "Error: Input block dimensions are invalid for frequency merging." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    // --- Persiapan DFT ---
    int optimal_rows = cv::getOptimalDFTSize(block_h);
    int optimal_cols = cv::getOptimalDFTSize(block_w);

    // Pastikan optimal size tidak lebih kecil (sangat jarang, tapi untuk keamanan)
    if (optimal_rows < block_h || optimal_cols < block_w) {
        // std::cerr << "Warning: Optimal DFT size smaller than block size. Using block size." << std::endl;
        optimal_rows = std::max(optimal_rows, block_h);
        optimal_cols = std::max(optimal_cols, block_w);
    }

    cv::Mat current_padded, ref_padded;
    try {
        cv::copyMakeBorder(current_block_gray, current_padded, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));
        cv::copyMakeBorder(reference_block_gray, ref_padded, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));
    } catch (const cv::Exception& e) {
        // std::cerr << "Error in copyMakeBorder: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }
    

    if (current_padded.empty() || ref_padded.empty()) {
        // std::cerr << "Error: Padded blocks are empty before DFT." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    cv::Mat current_dft, ref_dft;
    try {
        cv::dft(current_padded, current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(ref_padded, ref_dft, cv::DFT_COMPLEX_OUTPUT);
    } catch (const cv::Exception& e) {
        // std::cerr << "Error during DFT: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }


    if (current_dft.empty() || ref_dft.empty() || current_dft.size() != ref_dft.size()) {
        // std::cerr << "Error: DFT result(s) are empty or sizes mismatch." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    // --- Filter Wiener dan Penggabungan di Domain Frekuensi ---
    float sigma_sq_spatial_block = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    // Sigma DFT efektif adalah varians noise spasial dikali jumlah piksel di domain DFT (Parseval's theorem)
    float sigma_sq_dft_eff_block = sigma_sq_spatial_block * static_cast<float>(optimal_rows * optimal_cols);
    
    // Jaga agar sigma_sq_dft_eff_block tidak terlalu kecil atau negatif
    if (sigma_sq_dft_eff_block < stability_epsilon) {
        sigma_sq_dft_eff_block = stability_epsilon;
    }

    cv::Mat merged_dft;
    try {
        merged_dft.create(current_dft.size(), current_dft.type());
    } catch (const cv::Exception& e) {
        // std::cerr << "Error creating merged_dft Mat: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }


    float sum_freq_weights = 0.0f;
    int count_freq_weights = 0;

    for (int r_f = 0; r_f < current_dft.rows; ++r_f) {
        for (int c_f = 0; c_f < current_dft.cols; ++c_f) {
            const cv::Vec2f& coeff_curr = current_dft.at<cv::Vec2f>(r_f, c_f);
            const cv::Vec2f& coeff_ref = ref_dft.at<cv::Vec2f>(r_f, c_f);

            // Periksa NaN/Inf pada koefisien input (jarang, tapi bisa terjadi jika input DFT buruk)
            if (std::isnan(coeff_curr[0]) || std::isnan(coeff_curr[1]) ||
                std::isinf(coeff_curr[0]) || std::isinf(coeff_curr[1]) ||
                std::isnan(coeff_ref[0])  || std::isnan(coeff_ref[1]) ||
                std::isinf(coeff_ref[0])  || std::isinf(coeff_ref[1])) {
                // Jika ada NaN/Inf, gunakan koefisien dari current frame saja untuk piksel frekuensi ini
                merged_dft.at<cv::Vec2f>(r_f, c_f) = coeff_curr;
                sum_freq_weights += 1.0f; // Anggap bobot penuh ke current
                count_freq_weights++;
                continue;
            }

            cv::Vec2f diff_coeff = coeff_ref - coeff_curr;
            float mag_sq_diff = diff_coeff[0] * diff_coeff[0] + diff_coeff[1] * diff_coeff[1];

            // Noise floor di domain frekuensi, disesuaikan dengan Wiener C factor
            float noise_floor_freq = wiener_c_factor * sigma_sq_dft_eff_block;
            if (noise_floor_freq < stability_epsilon) { // Pastikan tidak terlalu kecil
                noise_floor_freq = stability_epsilon;
            }

            float weight_denominator = mag_sq_diff + noise_floor_freq + stability_epsilon;
            float weight_curr_freq;

            if (weight_denominator < stability_epsilon) { // Hindari pembagian dengan nol
                weight_curr_freq = 1.0f; // Jika denominator sangat kecil, beri bobot penuh ke current
            } else {
                weight_curr_freq = noise_floor_freq / weight_denominator;
            }
            
            weight_curr_freq = std::max(0.0f, std::min(1.0f, weight_curr_freq)); // Clamp bobot [0,1]

            // Periksa NaN setelah kalkulasi bobot (jika ada pembagian 0/0 atau inf/inf)
            if (std::isnan(weight_curr_freq)) {
                weight_curr_freq = 1.0f; // Default ke bobot penuh untuk current jika NaN
            }
            
            // Gabungkan koefisien
            merged_dft.at<cv::Vec2f>(r_f, c_f)[0] = coeff_ref[0] * (1.0f - weight_curr_freq) + coeff_curr[0] * weight_curr_freq;
            merged_dft.at<cv::Vec2f>(r_f, c_f)[1] = coeff_ref[1] * (1.0f - weight_curr_freq) + coeff_curr[1] * weight_curr_freq;

            sum_freq_weights += weight_curr_freq;
            count_freq_weights++;
        }
    }

    if (count_freq_weights > 0) {
        result.merge_confidence = sum_freq_weights / static_cast<float>(count_freq_weights);
    } else {
        // Ini seharusnya tidak terjadi jika DFT berhasil dan loop berjalan
        result.merge_confidence = 0.0f;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    // --- Konversi Kembali ke Domain Spasial (iDFT) ---
    cv::Mat temp_spatial_merged;
    try {
        cv::idft(merged_dft, temp_spatial_merged, cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);
    } catch (const cv::Exception& e) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }
    

    if (temp_spatial_merged.empty()) {
        // std::cerr << "Error: iDFT result is empty." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    if (temp_spatial_merged.rows >= block_h && temp_spatial_merged.cols >= block_w) {
        try {
            result.merged_block_gray = temp_spatial_merged(cv::Rect(0, 0, block_w, block_h)).clone();
        } catch (const cv::Exception& e) {
            current_block_gray.copyTo(result.merged_block_gray); // Fallback
            return result;
        }
    } else {
        // std::cerr << "Error: iDFT result smaller than original block size. Cannot crop." << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    // Bersihkan NaN yang mungkin masih ada (meskipun sudah ada pencegahan)
    cv::patchNaNs(result.merged_block_gray, 0.0); 

    result.success = true;
    return result;
}

} // namespace MotionMerging