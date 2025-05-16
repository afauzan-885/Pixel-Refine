#include "DFT_merging.hpp"
#include <opencv2/imgproc.hpp>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iostream>  
#include <omp.h>    

namespace MotionMerging {

FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon)
{
    FrequencyMergeResult result;
    result.success = false; 

    if (current_block_gray.empty() && reference_block_gray.empty()) {
        return result;
    }
    if (current_block_gray.empty()) {
        reference_block_gray.copyTo(result.merged_block_gray);
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

    current_block_gray.copyTo(result.merged_block_gray);

    int optimal_rows = cv::getOptimalDFTSize(block_h);
    int optimal_cols = cv::getOptimalDFTSize(block_w);

    optimal_rows = std::max(optimal_rows, block_h);
    optimal_cols = std::max(optimal_cols, block_w);

    
    cv::Mat current_padded, ref_padded;
    cv::Mat current_dft, ref_dft;
    cv::Mat merged_dft;
    cv::Mat temp_spatial_merged;

    try {
        cv::copyMakeBorder(current_block_gray, current_padded, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));
        cv::copyMakeBorder(reference_block_gray, ref_padded, 0, optimal_rows - block_h, 0, optimal_cols - block_w, cv::BORDER_CONSTANT, cv::Scalar::all(0));

        if (current_padded.empty() || ref_padded.empty()) {
            return result; 
        }

        cv::dft(current_padded, current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(ref_padded, ref_dft, cv::DFT_COMPLEX_OUTPUT);

        if (current_dft.empty() || ref_dft.empty() || current_dft.size() != ref_dft.size()) {
            return result; 
        }

        merged_dft.create(current_dft.size(), current_dft.type());

    } catch (const cv::Exception& e) {
       
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

   
    #pragma omp parallel for reduction(+:sum_freq_weights, count_freq_weights) schedule(static)
    for (int r_f = 0; r_f < current_dft.rows; ++r_f) {
        const cv::Vec2f* p_curr_dft_row = current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f* p_ref_dft_row = ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f* p_merged_dft_row = merged_dft.ptr<cv::Vec2f>(r_f);

        for (int c_f = 0; c_f < current_dft.cols; ++c_f) {
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

            float weight_denominator = mag_sq_diff + const_noise_floor_freq_part + stability_epsilon; // Tambah epsilon sekali lagi untuk pembagian
            float weight_curr_freq;

            if (weight_denominator < stability_epsilon) {
                weight_curr_freq = 1.0f; 
            } else {
                weight_curr_freq = const_noise_floor_freq_part / weight_denominator;
            }
            
            weight_curr_freq = std::max(0.0f, std::min(1.0f, weight_curr_freq));

            if (std::isnan(weight_curr_freq)) {
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
        return result;
    }
    try {
        cv::idft(merged_dft, temp_spatial_merged, cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);

        if (temp_spatial_merged.empty() || temp_spatial_merged.rows < block_h || temp_spatial_merged.cols < block_w) {
            return result; 
        }
        
        result.merged_block_gray = temp_spatial_merged(cv::Rect(0, 0, block_w, block_h)).clone();

    } catch (const cv::Exception& e) {
        return result;
    }
    
    cv::patchNaNs(result.merged_block_gray, 0.0); 

    result.success = true;
    return result;
}

}