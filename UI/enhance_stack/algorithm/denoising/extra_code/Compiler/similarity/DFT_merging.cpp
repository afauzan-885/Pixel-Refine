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

    // Early returns untuk edge cases
    if (current_block_gray.empty() && reference_block_gray.empty())
    {
        result.merged_block_gray = cv::Mat();
        return result;
    }
    if (current_block_gray.empty())
    {
        reference_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }
    if (reference_block_gray.empty())
    {
        current_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }

    // Validasi ukuran dan tipe - optimized check
    if (current_block_gray.size() != reference_block_gray.size() ||
        current_block_gray.type() != CV_32FC1 || reference_block_gray.type() != CV_32FC1)
    {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    const int block_h = current_block_gray.rows;
    const int block_w = current_block_gray.cols;

    if (block_h <= 0 || block_w <= 0)
    {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Hitung ukuran optimal DFT sekali saja
    const int optimal_rows = cv::getOptimalDFTSize(block_h);
    const int optimal_cols = cv::getOptimalDFTSize(block_w);

    try
    {
        // Re-allocasi buffer hanya jika diperlukan
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

        // Zero-pad secara efisien
        buffers.current_padded.setTo(0);
        buffers.ref_padded.setTo(0);
        
        current_block_gray.copyTo(buffers.current_padded(cv::Rect(0, 0, block_w, block_h)));
        reference_block_gray.copyTo(buffers.ref_padded(cv::Rect(0, 0, block_w, block_h)));

        // DFT computation
        cv::dft(buffers.current_padded, buffers.current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(buffers.ref_padded, buffers.ref_dft, cv::DFT_COMPLEX_OUTPUT);
    }
    catch (const cv::Exception &e)
    {
        std::cerr << "OpenCV Exception during padding or DFT: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Pre-compute constants untuk optimasi
    const float optimal_elements_inv = 1.0f / static_cast<float>(optimal_rows * optimal_cols);
    const float sigma_sq_spatial_block = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    const float sigma_sq_dft_eff_block = std::max(sigma_sq_spatial_block / optimal_elements_inv, stability_epsilon);
    
    const float const_noise_floor_freq_part = std::max(wiener_c_factor * sigma_sq_dft_eff_block, stability_epsilon);
    
    // Adaptive sensitivity parameters - pre-computed
    const float noise_threshold_multiplier = 2.0f;
    const float high_confidence_boost = 0.8f;
    const float low_confidence_penalty = 0.2f;
    const float noise_floor_adaptive = 1e-6f;
    
    const float base_noise_level = sigma_sq_dft_eff_block * optimal_elements_inv;
    const float noise_boundary_multiplier = base_noise_level * noise_threshold_multiplier;
    const float noise_lower_bound = base_noise_level * 0.5f;
    
    // Precompute interpolation constants
    const float interpolation_range_inv = 1.0f / (noise_boundary_multiplier - noise_lower_bound);
    const float boost_penalty_diff = high_confidence_boost - low_confidence_penalty;

    float sum_freq_weights = 0.0f;
    int count_freq_weights = 0;

    // Optimized parallel processing
#pragma omp parallel for reduction(+ : sum_freq_weights, count_freq_weights) schedule(static)
    for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f)
    {
        const cv::Vec2f* __restrict p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f* __restrict p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f* __restrict p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);

        for (int c_f = 0; c_f < buffers.current_dft.cols; ++c_f)
        {
            const cv::Vec2f &coeff_curr = p_curr_dft_row[c_f];
            const cv::Vec2f &coeff_ref = p_ref_dft_row[c_f];

            // Fast NaN/Inf check - likely branch first
            const bool is_invalid = std::isnan(coeff_curr[0]) || std::isnan(coeff_curr[1]) ||
                                   std::isinf(coeff_curr[0]) || std::isinf(coeff_curr[1]) ||
                                   std::isnan(coeff_ref[0]) || std::isnan(coeff_ref[1]) ||
                                   std::isinf(coeff_ref[0]) || std::isinf(coeff_ref[1]);
            
            if (is_invalid) [[unlikely]]
            {
                p_merged_dft_row[c_f] = coeff_curr;
                sum_freq_weights += 1.0f;
                count_freq_weights++;
                continue;
            }

            // === OPTIMIZED ADAPTIVE SENSITIVITY CALCULATION ===
            
            // 1. Compute differences and magnitudes efficiently
            const float diff_real = coeff_ref[0] - coeff_curr[0];
            const float diff_imag = coeff_ref[1] - coeff_curr[1];
            const float mag_sq_diff_raw = diff_real * diff_real + diff_imag * diff_imag;
            
            // 2. Fast magnitude calculation
            const float mag_curr = coeff_curr[0] * coeff_curr[0] + coeff_curr[1] * coeff_curr[1];
            const float mag_ref = coeff_ref[0] * coeff_ref[0] + coeff_ref[1] * coeff_ref[1];
            const float avg_magnitude = (mag_curr + mag_ref) * 0.5f;
            
            // 3. Adaptive noise threshold dengan minimal computation
            const float adaptive_noise_threshold = std::max(base_noise_level, avg_magnitude * noise_floor_adaptive);
            const float noise_boundary = adaptive_noise_threshold * noise_threshold_multiplier;
            
            // 4. Branch-optimized sensitivity enhancement
            float enhanced_mag_sq_diff;
            if (mag_sq_diff_raw > noise_boundary) [[likely]]
            {
                // PERBEDAAN NYATA - most common case
                const float confidence_ratio = std::min(mag_sq_diff_raw / noise_boundary, 10.0f);
                const float boost_factor = 1.0f + high_confidence_boost * std::tanh(confidence_ratio - 1.0f);
                enhanced_mag_sq_diff = mag_sq_diff_raw * boost_factor;
            }
            else if (mag_sq_diff_raw < noise_lower_bound) [[unlikely]]
            {
                // PURE NOISE - uncommon case
                enhanced_mag_sq_diff = mag_sq_diff_raw * low_confidence_penalty;
            }
            else
            {
                // AMBIGUOUS ZONE - interpolation
                const float confidence_ratio = (mag_sq_diff_raw - noise_lower_bound) * interpolation_range_inv;
                const float interpolation_factor = confidence_ratio * boost_penalty_diff + low_confidence_penalty;
                enhanced_mag_sq_diff = mag_sq_diff_raw * (1.0f + interpolation_factor);
            }
            
            // 5. Clamp to stability range
            enhanced_mag_sq_diff = std::max(enhanced_mag_sq_diff, stability_epsilon);
            
            // === OPTIMIZED WIENER FILTERING ===
            const float weight_denominator = enhanced_mag_sq_diff + const_noise_floor_freq_part;
            float weight_curr_freq = const_noise_floor_freq_part / weight_denominator;
            
            // Fast clamp without std::clamp
            weight_curr_freq = (weight_curr_freq > 1.0f) ? 1.0f : 
                              (weight_curr_freq < 0.0f) ? 0.0f : weight_curr_freq;
            
            // NaN check dengan branch prediction
            if (std::isnan(weight_curr_freq)) [[unlikely]]
                weight_curr_freq = 1.0f;

            // Efficient complex multiplication
            const float weight_ref = 1.0f - weight_curr_freq;
            p_merged_dft_row[c_f][0] = coeff_ref[0] * weight_ref + coeff_curr[0] * weight_curr_freq;
            p_merged_dft_row[c_f][1] = coeff_ref[1] * weight_ref + coeff_curr[1] * weight_curr_freq;

            sum_freq_weights += weight_curr_freq;
            count_freq_weights++;
        }
    }

    // Compute merge confidence
    if (count_freq_weights > 0) [[likely]]
    {
        result.merge_confidence = sum_freq_weights * (1.0f / static_cast<float>(count_freq_weights));
    }
    else
    {
        result.merge_confidence = 0.0f;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Optimized inverse DFT
    try
    {
        cv::idft(buffers.merged_dft, buffers.temp_spatial_merged,
                 cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);

        // Bounds check sebelum crop
        if (buffers.temp_spatial_merged.rows < block_h || buffers.temp_spatial_merged.cols < block_w) [[unlikely]]
        {
            current_block_gray.copyTo(result.merged_block_gray);
            return result;
        }
        
        // Efficient crop without clone jika memungkinkan
        const cv::Rect crop_rect(0, 0, block_w, block_h);
        result.merged_block_gray = buffers.temp_spatial_merged(crop_rect).clone();
    }
    catch (const cv::Exception &e)
    {
        std::cerr << "OpenCV Exception during IDFT or cropping: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    // Final cleanup
    cv::patchNaNs(result.merged_block_gray, 0.0);
    result.success = true;
    return result;
}

}