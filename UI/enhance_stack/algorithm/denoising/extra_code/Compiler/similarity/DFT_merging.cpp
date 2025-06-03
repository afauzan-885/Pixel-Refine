#include "DFT_merging.hpp"
#include <opencv2/imgproc.hpp>
#include <iostream>
#include <cmath>

namespace MotionMerging
{

FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat &current_block_gray,
    const cv::Mat &reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon,
    DFTBuffers &buffers)
{
    FrequencyMergeResult result;
    result.success = false;

    // Jika kedua blok kosong, langsung return kosong
    if (current_block_gray.empty() && reference_block_gray.empty())
    {
        result.merged_block_gray = cv::Mat();
        return result;
    }
    // Jika current kosong, copy reference
    if (current_block_gray.empty())
    {
        reference_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }
    // Jika reference kosong, copy current
    if (reference_block_gray.empty())
    {
        current_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }

    // Validasi ukuran dan tipe
    if (current_block_gray.size() != reference_block_gray.size() ||
        current_block_gray.type() != CV_32FC1 || reference_block_gray.type() != CV_32FC1)
    {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    int block_h = current_block_gray.rows;
    int block_w = current_block_gray.cols;

    if (block_h <= 0 || block_w <= 0)
    {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Hitung ukuran optimal DFT
    int optimal_rows = cv::getOptimalDFTSize(block_h);
    int optimal_cols = cv::getOptimalDFTSize(block_w);

    try
    {
        // Re-allocasi buffer jika ukuran optimal berubah (precomputed buffers)
        if (buffers.cached_rows != optimal_rows || buffers.cached_cols != optimal_cols)
        {
            buffers.current_padded.create(optimal_rows, optimal_cols, CV_32FC1);
            buffers.ref_padded.create(optimal_rows, optimal_cols, CV_32FC1);

            buffers.current_dft.create(optimal_rows, optimal_cols, CV_32FC2);
            buffers.ref_dft.create(optimal_rows, optimal_cols, CV_32FC2);
            buffers.merged_dft.create(optimal_rows, optimal_cols, CV_32FC2);

            buffers.temp_spatial_merged.create(optimal_rows, optimal_cols, CV_32FC1);

            buffers.cached_rows = optimal_rows;
            buffers.cached_cols = optimal_cols;
        }

        // Padding blok input ke ukuran optimal (isi nol)
        cv::copyMakeBorder(current_block_gray, buffers.current_padded,
                           0, optimal_rows - block_h,
                           0, optimal_cols - block_w,
                           cv::BORDER_CONSTANT, cv::Scalar::all(0));
        cv::copyMakeBorder(reference_block_gray, buffers.ref_padded,
                           0, optimal_rows - block_h,
                           0, optimal_cols - block_w,
                           cv::BORDER_CONSTANT, cv::Scalar::all(0));

        // Hitung DFT in-place langsung di buffer yang sudah ada
        cv::dft(buffers.current_padded, buffers.current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(buffers.ref_padded, buffers.ref_dft, cv::DFT_COMPLEX_OUTPUT);

    }
    catch (const cv::Exception &e)
    {
        std::cerr << "OpenCV Exception during padding or DFT: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Parameter penghitungan noise untuk Wiener filter
    float optimal_elements = static_cast<float>(optimal_rows * optimal_cols);
    float sigma_sq_spatial_block = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    float sigma_sq_dft_eff_block = sigma_sq_spatial_block * optimal_elements;
    sigma_sq_dft_eff_block = std::max(sigma_sq_dft_eff_block, stability_epsilon);

    float const_noise_floor_freq_part = wiener_c_factor * sigma_sq_dft_eff_block;
    const_noise_floor_freq_part = std::max(const_noise_floor_freq_part, stability_epsilon);

    float sum_freq_weights = 0.0f;
    int count_freq_weights = 0;

    // Parallel loop OpenMP per baris DFT (per kanal frekuensi)
#pragma omp parallel for reduction(+ : sum_freq_weights, count_freq_weights)
    for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f)
    {
        const cv::Vec2f *p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f *p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f *p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);

        for (int c_f = 0; c_f < buffers.current_dft.cols; ++c_f)
        {
            const cv::Vec2f &coeff_curr = p_curr_dft_row[c_f];
            const cv::Vec2f &coeff_ref = p_ref_dft_row[c_f];

            // Tangani NaN atau Inf
            if (std::isnan(coeff_curr[0]) || std::isnan(coeff_curr[1]) ||
                std::isinf(coeff_curr[0]) || std::isinf(coeff_curr[1]) ||
                std::isnan(coeff_ref[0]) || std::isnan(coeff_ref[1]) ||
                std::isinf(coeff_ref[0]) || std::isinf(coeff_ref[1]))
            {
                p_merged_dft_row[c_f] = coeff_curr;
                sum_freq_weights += 1.0f;
                count_freq_weights++;
                continue;
            }

            // Hitung selisih dan magnitude kuadrat
            cv::Vec2f diff_coeff = coeff_ref - coeff_curr;
            float mag_sq_diff = diff_coeff[0] * diff_coeff[0] + diff_coeff[1] * diff_coeff[1];

            // Wiener weighting frekuensi
            float weight_denominator = mag_sq_diff + const_noise_floor_freq_part + stability_epsilon;
            float weight_curr_freq = (weight_denominator < stability_epsilon) ?
                                    1.0f :
                                    const_noise_floor_freq_part / weight_denominator;
            weight_curr_freq = std::clamp(weight_curr_freq, 0.0f, 1.0f);

            if (std::isnan(weight_curr_freq))
                weight_curr_freq = 1.0f;

            // Gabungkan frekuensi berdasarkan bobot
            p_merged_dft_row[c_f][0] = coeff_ref[0] * (1.0f - weight_curr_freq) + coeff_curr[0] * weight_curr_freq;
            p_merged_dft_row[c_f][1] = coeff_ref[1] * (1.0f - weight_curr_freq) + coeff_curr[1] * weight_curr_freq;

            sum_freq_weights += weight_curr_freq;
            count_freq_weights++;
        }
    }

    if (count_freq_weights > 0)
    {
        result.merge_confidence = sum_freq_weights / static_cast<float>(count_freq_weights);
    }
    else
    {
        // Jika tak ada frekuensi, fallback
        result.merge_confidence = 0.0f;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Inverse DFT ke domain spasial
    try
    {
        cv::idft(buffers.merged_dft, buffers.temp_spatial_merged,
                 cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);

        if (buffers.temp_spatial_merged.rows < block_h || buffers.temp_spatial_merged.cols < block_w)
        {
            current_block_gray.copyTo(result.merged_block_gray);
            return result;
        }
        // Salin hasil akhir (clone supaya tidak tergantung buffer)
        result.merged_block_gray = buffers.temp_spatial_merged(cv::Rect(0, 0, block_w, block_h)).clone();
    }
    catch (const cv::Exception &e)
    {
        std::cerr << "OpenCV Exception during IDFT or cropping: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    cv::patchNaNs(result.merged_block_gray, 0.0);
    result.success = true;
    return result;
}

} 