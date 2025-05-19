#include "DFT_merging.hpp"
#include <opencv2/imgproc.hpp>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>
// #include <omp.h> // Dihapus karena nested parallelism dihilangkan

namespace MotionMerging {

FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon,
    DFTBuffers& buffers // Menggunakan buffer yang dilewatkan
)
{
    FrequencyMergeResult result;
    result.success = false;
    // TIDAK ADA copyTo awal ke result.merged_block_gray

    if (current_block_gray.empty() && reference_block_gray.empty()) {
        result.merged_block_gray = cv::Mat(); // Atau biarkan kosong
        return result;
    }
    if (current_block_gray.empty()) {
        // Tidak bisa menggunakan buffer di sini karena ukuran mungkin tidak cocok
        // dan ini adalah jalur fallback.
        reference_block_gray.copyTo(result.merged_block_gray);
        // result.success tetap false, ini adalah kondisi fallback, bukan merge sukses
        return result;
    }
    if (reference_block_gray.empty()) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    if (current_block_gray.size() != reference_block_gray.size() ||
        current_block_gray.type() != CV_32FC1 || reference_block_gray.type() != CV_32FC1) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    int block_h = current_block_gray.rows;
    int block_w = current_block_gray.cols;

    if (block_h <= 0 || block_w <= 0) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Tidak ada copyTo default ke result.merged_block_gray lagi di sini

    int optimal_rows = cv::getOptimalDFTSize(block_h);
    int optimal_cols = cv::getOptimalDFTSize(block_w);

    optimal_rows = std::max(optimal_rows, block_h); // Pastikan tidak lebih kecil
    optimal_cols = std::max(optimal_cols, block_w); // Pastikan tidak lebih kecil


    // Gunakan buffer yang dilewatkan. Re-create jika ukurannya tidak sesuai.
    // Ini adalah trade-off; idealnya, pemanggil sudah memastikan ukuran buffer cukup.
    // Jika ukuran blok bervariasi, maka .create() diperlukan.
    // Jika ukuran blok tetap, alokasi awal di pemanggil sudah cukup.
    // Untuk kesederhanaan awal, kita asumsikan pemanggil menyiapkan buffer dengan ukuran maksimal
    // atau kita menggunakan .create() yang akan re-alokasi jika perlu.
    // Untuk performa terbaik, pemanggil harus mengelola ukuran buffer agar .create() jarang re-alokasi.
    try {
        // Pengecekan dan pembuatan buffer jika perlu (jika ukurannya bisa bervariasi)
        // atau asumsikan buffer sudah dialokasikan dengan benar oleh pemanggil.
        // Untuk contoh ini, kita akan membiarkan .create() untuk fleksibilitas,
        // tapi idealnya ini dioptimalkan lebih lanjut.

        // Padding
        // Cek apakah buffer cukup, jika tidak, create.
        if (buffers.current_padded.rows < optimal_rows || buffers.current_padded.cols < optimal_cols || buffers.current_padded.type() != current_block_gray.type()) {
            buffers.current_padded.create(optimal_rows, optimal_cols, current_block_gray.type());
        }
        cv::Mat current_padded_roi = buffers.current_padded(cv::Rect(0, 0, optimal_cols, optimal_rows)); // ROI untuk operasi
        current_padded_roi.setTo(cv::Scalar::all(0)); // Nolkan dulu area padding
        cv::copyMakeBorder(current_block_gray, current_padded_roi, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));
        // (optimasi lebih lanjut: salin current_block_gray ke pojok kiri atas, sisanya sudah nol)
        // current_block_gray.copyTo(current_padded_roi(cv::Rect(0,0,block_w,block_h)));


        if (buffers.ref_padded.rows < optimal_rows || buffers.ref_padded.cols < optimal_cols || buffers.ref_padded.type() != reference_block_gray.type()) {
            buffers.ref_padded.create(optimal_rows, optimal_cols, reference_block_gray.type());
        }
        cv::Mat ref_padded_roi = buffers.ref_padded(cv::Rect(0, 0, optimal_cols, optimal_rows));
        ref_padded_roi.setTo(cv::Scalar::all(0));
        cv::copyMakeBorder(reference_block_gray, ref_padded_roi, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));
        // reference_block_gray.copyTo(ref_padded_roi(cv::Rect(0,0,block_w,block_h)));

        // DFT
        // Pastikan buffer DFT memiliki ukuran dan tipe yang tepat
        int dft_type = CV_32FC2; // DFT_COMPLEX_OUTPUT menghasilkan 2 channel float
        if (buffers.current_dft.rows != optimal_rows || buffers.current_dft.cols != optimal_cols || buffers.current_dft.type() != dft_type) {
            buffers.current_dft.create(optimal_rows, optimal_cols, dft_type);
        }
        if (buffers.ref_dft.rows != optimal_rows || buffers.ref_dft.cols != optimal_cols || buffers.ref_dft.type() != dft_type) {
            buffers.ref_dft.create(optimal_rows, optimal_cols, dft_type);
        }

        cv::dft(current_padded_roi, buffers.current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(ref_padded_roi, buffers.ref_dft, cv::DFT_COMPLEX_OUTPUT);


        if (buffers.current_dft.empty() || buffers.ref_dft.empty() || buffers.current_dft.size() != buffers.ref_dft.size()) {
            current_block_gray.copyTo(result.merged_block_gray); // Fallback
            return result;
        }

        if (buffers.merged_dft.size() != buffers.current_dft.size() || buffers.merged_dft.type() != buffers.current_dft.type()) {
            buffers.merged_dft.create(buffers.current_dft.size(), buffers.current_dft.type());
        }

    } catch (const cv::Exception& e) {
        // std::cerr << "DFT_merging exception during DFT prep: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }


    float optimal_elements = static_cast<float>(optimal_rows * optimal_cols);
    float sigma_sq_spatial_block = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    float sigma_sq_dft_eff_block = sigma_sq_spatial_block * optimal_elements;

    sigma_sq_dft_eff_block = std::max(sigma_sq_dft_eff_block, stability_epsilon);

    float const_noise_floor_freq_part = wiener_c_factor * sigma_sq_dft_eff_block;
    const_noise_floor_freq_part = std::max(const_noise_floor_freq_part, stability_epsilon);


    float sum_freq_weights = 0.0f;
    int count_freq_weights = 0;

    // HAPUS #pragma omp parallel for dari sini
    for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f) {
        const cv::Vec2f* p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f* p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f* p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);

        for (int c_f = 0; c_f < buffers.current_dft.cols; ++c_f) {
            const cv::Vec2f& coeff_curr = p_curr_dft_row[c_f];
            const cv::Vec2f& coeff_ref = p_ref_dft_row[c_f];

            if (std::isnan(coeff_curr[0]) || std::isnan(coeff_curr[1]) ||
                std::isinf(coeff_curr[0]) || std::isinf(coeff_curr[1]) ||
                std::isnan(coeff_ref[0])  || std::isnan(coeff_ref[1]) ||
                std::isinf(coeff_ref[0])  || std::isinf(coeff_ref[1])) {

                p_merged_dft_row[c_f] = coeff_curr;
                sum_freq_weights += 1.0f;
                count_freq_weights++;
                continue;
            }

            cv::Vec2f diff_coeff;
            diff_coeff[0] = coeff_ref[0] - coeff_curr[0];
            diff_coeff[1] = coeff_ref[1] - coeff_curr[1];
            float mag_sq_diff = diff_coeff[0] * diff_coeff[0] + diff_coeff[1] * diff_coeff[1];

            float weight_denominator = mag_sq_diff + const_noise_floor_freq_part + stability_epsilon;
            float weight_curr_freq;

            if (weight_denominator < stability_epsilon) { // stability_epsilon sangat kecil
                weight_curr_freq = 1.0f;
            } else {
                weight_curr_freq = const_noise_floor_freq_part / weight_denominator;
            }

            weight_curr_freq = std::max(0.0f, std::min(1.0f, weight_curr_freq));

            if (std::isnan(weight_curr_freq)) { // Seharusnya jarang terjadi sekarang
                weight_curr_freq = 1.0f;
            }

            p_merged_dft_row[c_f][0] = coeff_ref[0] * (1.0f - weight_curr_freq) + coeff_curr[0] * weight_curr_freq;
            p_merged_dft_row[c_f][1] = coeff_ref[1] * (1.0f - weight_curr_freq) + coeff_curr[1] * weight_curr_freq;

            sum_freq_weights += weight_curr_freq;
            count_freq_weights++;
        }
    }

    if (count_freq_weights > 0) {
        result.merge_confidence = sum_freq_weights / static_cast<float>(count_freq_weights);
    } else {
        result.merge_confidence = 0.0f;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    try {
        // Pastikan buffer IDFT memiliki ukuran dan tipe yang tepat
        // IDFT REAL_OUTPUT menghasilkan 1 channel float
        if (buffers.temp_spatial_merged.rows < optimal_rows || buffers.temp_spatial_merged.cols < optimal_cols || buffers.temp_spatial_merged.type() != CV_32FC1) {
             buffers.temp_spatial_merged.create(optimal_rows, optimal_cols, CV_32FC1);
        }
        cv::Mat temp_spatial_merged_roi = buffers.temp_spatial_merged(cv::Rect(0, 0, optimal_cols, optimal_rows));

        cv::idft(buffers.merged_dft, temp_spatial_merged_roi, cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);

        if (temp_spatial_merged_roi.empty() || temp_spatial_merged_roi.rows < block_h || temp_spatial_merged_roi.cols < block_w) {
            current_block_gray.copyTo(result.merged_block_gray); // Fallback
            return result;
        }

        // Hasilnya di-clone karena `result.merged_block_gray` mungkin memiliki lifetime berbeda
        // atau bisa juga merujuk ke ROI dari buffer jika tidak di-clone, tapi itu lebih kompleks pengelolaannya.
        // `.clone()` memastikan data tersalin.
        result.merged_block_gray = temp_spatial_merged_roi(cv::Rect(0, 0, block_w, block_h)).clone();

    } catch (const cv::Exception& e) {
        // std::cerr << "DFT_merging exception during IDFT: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray); // Fallback
        return result;
    }

    cv::patchNaNs(result.merged_block_gray, 0.0);

    result.success = true;
    return result;
}

}