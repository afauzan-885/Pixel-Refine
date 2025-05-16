#include "spatial_merging.hpp" 
#include <opencv2/imgproc.hpp>  
#include <vector>
#include <cmath>
#include <algorithm>
#include <omp.h>

namespace MotionMerging {

static void calculate_patch_mean_variance(const cv::Mat& block, int r_center, int c_center, int patch_radius, float& mean, float& variance) {
    float sum = 0.0f;
    float sum_sq = 0.0f;
    int count = 0;

    int r_start = std::max(0, r_center - patch_radius);
    int r_end = std::min(block.rows, r_center + patch_radius + 1);
    int c_start = std::max(0, c_center - patch_radius);
    int c_end = std::min(block.cols, c_center + patch_radius + 1);

    for (int pr = r_start; pr < r_end; ++pr) {
        const float* p_row = block.ptr<const float>(pr);
        for (int pc = c_start; pc < c_end; ++pc) {
            float val = p_row[pc];
            sum += val;
            sum_sq += val * val;
            count++;
        }
    }

    if (count > 0) {
        mean = sum / static_cast<float>(count);
        if (count > 1) {
             variance = (sum_sq / static_cast<float>(count)) - (mean * mean);
            variance = std::max(0.0f, variance); 
        } else {
            variance = 0.0f; 
        }
    } else {
        
        mean = block.at<float>(r_center, c_center);
        variance = 0.0f;
    }
}


SpatialMergeResult spatial_merge_block( 
    const cv::Mat& current_block_gray,
    const cv::Mat& reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon)
{
    SpatialMergeResult result;
    result.success = false;

    if (current_block_gray.empty() && reference_block_gray.empty()) {
        return result;
    }
    if (current_block_gray.empty()) {
        reference_block_gray.copyTo(result.merged_block_gray);
        result.success = false; 
        return result;
    }
    if (reference_block_gray.empty()) {
        current_block_gray.copyTo(result.merged_block_gray);
        result.success = false; 
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

    result.merged_block_gray.create(block_h, block_w, CV_32FC1);

    const int patch_radius = 2;
    const int min_block_dim_for_patch = 2 * patch_radius + 1;


    if (block_h < min_block_dim_for_patch || block_w < min_block_dim_for_patch) {
        current_block_gray.copyTo(result.merged_block_gray);
        result.merge_confidence = 0.5f; 
        result.success = true; 
        return result;
    }

    float sigma_sq_noise = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    float weighted_sigma_sq_noise = wiener_c_factor * sigma_sq_noise;
    weighted_sigma_sq_noise = std::max(weighted_sigma_sq_noise, stability_epsilon * stability_epsilon); // Epsilon untuk noise floor minimal

    double total_weight_curr_sum = 0.0; 
    int processed_pixel_count = 0;

    #pragma omp parallel for reduction(+:total_weight_curr_sum, processed_pixel_count) schedule(static)
    for (int r = 0; r < block_h; ++r) {
        const float* p_curr_row = current_block_gray.ptr<const float>(r);
        const float* p_ref_row = reference_block_gray.ptr<const float>(r);
        float* p_merged_row = result.merged_block_gray.ptr<float>(r);

        for (int c = 0; c < block_w; ++c) {
            float mean_curr_patch, var_curr_patch;
            calculate_patch_mean_variance(current_block_gray, r, c, patch_radius, mean_curr_patch, var_curr_patch);

            float signal_sq_curr_patch = std::max(0.0f, var_curr_patch - sigma_sq_noise);

            float W_curr_denominator = signal_sq_curr_patch + weighted_sigma_sq_noise + stability_epsilon; // Tambah epsilon untuk pembagian
            float W_curr_pixel;

            if (W_curr_denominator < stability_epsilon) { 
                W_curr_pixel = 0.5f;
            } else {
                W_curr_pixel = signal_sq_curr_patch / W_curr_denominator;
            }
            
            W_curr_pixel = std::max(0.0f, std::min(1.0f, W_curr_pixel)); 

            if (std::isnan(W_curr_pixel)) {
                W_curr_pixel = 0.5f;
            }

            p_merged_row[c] = p_curr_row[c] * W_curr_pixel + p_ref_row[c] * (1.0f - W_curr_pixel);

            total_weight_curr_sum += W_curr_pixel;
            processed_pixel_count++;
        }
    }

    if (processed_pixel_count > 0) {
        result.merge_confidence = static_cast<float>(total_weight_curr_sum / processed_pixel_count);
    } else {
        current_block_gray.copyTo(result.merged_block_gray); 
        result.merge_confidence = 0.0f;
        return result;
    }
    
    cv::patchNaNs(result.merged_block_gray, 0.0); 

    result.success = true;
    return result;
}

} 