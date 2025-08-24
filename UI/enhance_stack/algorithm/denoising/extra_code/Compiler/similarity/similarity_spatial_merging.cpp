#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>
#include "block_matching.hpp"
#include "tile_noise_estimation.hpp"
#include "spatial_merging.hpp"
#include "compute_flat.hpp"

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
    constexpr float FLATNESS_VARIANCE_THRESHOLD = 15.0f;
    constexpr float FLATNESS_CONFIDENCE_BOOST = 1.7f;
}

// namespace
// {
//     static cv::Mat generate_pyramid_guidance_map(
//         const cv::Mat &current_image_gray_full,
//         const cv::Mat &reference_image_gray_full,
//         int tile_h, int tile_w, int search_radius,
//         float motion_sensitivity, float noise_offset_factor, float global_estimated_noise_sigma)
//     {
//         using namespace MotionMetricsConfig;
//         using namespace MotionMatching;

//         cv::Mat current_image_gray_half, reference_image_gray_half;
//         cv::pyrDown(current_image_gray_full, current_image_gray_half);
//         cv::pyrDown(reference_image_gray_full, reference_image_gray_half);

//         cv::Mat current_image_gray_quarter, reference_image_gray_quarter;
//         cv::pyrDown(current_image_gray_half, current_image_gray_quarter);
//         cv::pyrDown(reference_image_gray_half, reference_image_gray_quarter);

//         cv::Mat blurred_current_quarter, blurred_reference_quarter;
//         cv::GaussianBlur(current_image_gray_quarter, blurred_current_quarter, cv::Size(3, 3), 0.8);
//         cv::GaussianBlur(reference_image_gray_quarter, blurred_reference_quarter, cv::Size(3, 3), 0.8);

//         cv::Mat confidence_map_quarter(current_image_gray_quarter.size(), CV_32FC1, cv::Scalar(0.0f));
//         int tile_h_quarter = std::max(1, tile_h / 4);
//         int tile_w_quarter = std::max(1, tile_w / 4);
//         int search_radius_quarter = search_radius > 0 ? std::max(1, search_radius / 4) : 0;

//     #pragma omp parallel for schedule(static)
//         for (int r_q = 0; r_q < blurred_current_quarter.rows; r_q += tile_h_quarter)
//         {
//             MBMBuffers buffers_q;
//             for (int c_q = 0; c_q < blurred_current_quarter.cols; c_q += tile_w_quarter)
//             {
//                 int current_w = std::min(tile_w_quarter, blurred_current_quarter.cols - c_q);
//                 int current_h = std::min(tile_h_quarter, blurred_current_quarter.rows - r_q);
//                 if (current_w <= 0 || current_h <= 0) continue;

//                 buffers_q.diff_workspace.create(current_h, current_w, CV_32FC1);
//                 buffers_q.grad_x.create(current_h, current_w, CV_32F);
//                 buffers_q.grad_y.create(current_h, current_w, CV_32F);
//                 buffers_q.grad_mag_current.create(current_h, current_w, CV_32FC1);

//                 cv::Rect roi_q(c_q, r_q, current_w, current_h);
//                 BlockMatchResult res_q = find_best_block_match_mad(blurred_current_quarter(roi_q), blurred_reference_quarter, r_q, c_q, search_radius_quarter, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_q);
//                 float conf_q = res_q.success ? calculate_match_confidence(res_q, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
//                 confidence_map_quarter(roi_q).setTo(cv::Scalar(conf_q));
//             }
//         }

//         cv::Mat guidance_map_for_half;
//         cv::resize(confidence_map_quarter, guidance_map_for_half, current_image_gray_half.size(), 0, 0, cv::INTER_LINEAR);

//         cv::Mat confidence_map_half(current_image_gray_half.size(), CV_32FC1, cv::Scalar(0.0f));
//         int tile_h_half = std::max(1, tile_h / 2);
//         int tile_w_half = std::max(1, tile_w / 2);
//         int search_radius_half = search_radius > 0 ? std::max(1, search_radius / 2) : 0;

//     #pragma omp parallel for schedule(static)
//         for (int r_h = 0; r_h < current_image_gray_half.rows; r_h += tile_h_half)
//         {
//             MBMBuffers buffers_h;
//             for (int c_h = 0; c_h < current_image_gray_half.cols; c_h += tile_h_half)
//             {
//                 int current_w = std::min(tile_w_half, current_image_gray_half.cols - c_h);
//                 int current_h = std::min(tile_h_half, current_image_gray_half.rows - r_h);
//                 if (current_w <= 0 || current_h <= 0) continue;

//                 buffers_h.diff_workspace.create(current_h, current_w, CV_32FC1);
//                 buffers_h.grad_x.create(current_h, current_w, CV_32F);
//                 buffers_h.grad_y.create(current_h, current_w, CV_32F);
//                 buffers_h.grad_mag_current.create(current_h, current_w, CV_32FC1);

//                 cv::Rect roi_h(c_h, r_h, current_w, current_h);
//                 BlockMatchResult res_h = find_best_block_match_mad(current_image_gray_half(roi_h), reference_image_gray_half, r_h, c_h, search_radius_half, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_h);
//                 float local_conf_h = res_h.success ? calculate_match_confidence(res_h, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;

//                 cv::Scalar mean_guidance_scalar = cv::mean(guidance_map_for_half(roi_h));
//                 float guidance_conf = static_cast<float>(mean_guidance_scalar[0]);
//                 confidence_map_half(roi_h).setTo(cv::Scalar(local_conf_h * guidance_conf));
//             }
//         }

//         cv::Mat guidance_confidence_map_final;
//         cv::resize(confidence_map_half, guidance_confidence_map_final, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
//         return guidance_confidence_map_final;
//     }
// }

extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr,
        float *weight_map_sum_ptr,
        const float *current_image_ptr,
        const float *reference_image_ptr,
        const float *base_window_ptr,
        const float *stability_map_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h_img, int w_img, int channels,
        float motion_sensitivity,
        float noise_offset_factor,
        // NEW PARAMETERS for integrated resize logic
        int orig_h, int orig_w,           // Original image dimensions
        int target_h, int target_w,       // Target working resolution
        bool auto_resize,                 // Enable/disable auto resize
        float target_megapixels)          // Target MP for auto-sizing
    {
        using namespace MotionMetricsConfig;

        // --- PART 1: Input validation and auto-resize logic ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0)
        {
            return;
        }

        // --- OPTIMIZATION 1: Integrated Auto-Resize Logic (moved from Python) ---
        int work_h = h_img, work_w = w_img;
        bool needs_resize = false;
        
        if (auto_resize) {
            const float current_mp = static_cast<float>(orig_h * orig_w);
            const float target_mp_limit = target_megapixels * 1e6f;
            
            if (current_mp > target_mp_limit) {
                // Downscale to target megapixels
                const float scale_factor = std::sqrt(target_mp_limit / current_mp);
                work_h = static_cast<int>(orig_h * scale_factor);
                work_w = static_cast<int>(orig_w * scale_factor);
                needs_resize = true;
            } else {
                // Scale to 70% for processing efficiency
                work_h = static_cast<int>(orig_h * 0.7f);
                work_w = static_cast<int>(orig_w * 0.7f);
                needs_resize = (work_h != orig_h || work_w != orig_w);
            }
            
            // Ensure even dimensions for better SIMD processing
            work_h = (work_h / 2) * 2;
            work_w = (work_w / 2) * 2;
        } else {
            work_h = target_h;
            work_w = target_w;
            needs_resize = (work_h != h_img || work_w != w_img);
        }

        // --- OPTIMIZATION 2: Parallel Image Preparation ---
        cv::Mat current_work, reference_work;
        cv::Mat current_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(current_image_ptr));
        cv::Mat reference_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(reference_image_ptr));
        
        cv::Mat stability_map_work;
        cv::Mat stability_map_mat;
        if (stability_map_ptr) {
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
        }

        #pragma omp parallel sections
        {
            #pragma omp section
            {
                // Resize current image to working resolution
                if (needs_resize) {
                    cv::resize(current_image_mat, current_work, cv::Size(work_w, work_h), 0, 0, cv::INTER_AREA);
                } else {
                    current_work = current_image_mat;
                }
            }
            
            #pragma omp section
            {
                // Resize reference image to working resolution
                if (needs_resize) {
                    cv::resize(reference_image_mat, reference_work, cv::Size(work_w, work_h), 0, 0, cv::INTER_AREA);
                } else {
                    reference_work = reference_image_mat;
                }
            }
            
            #pragma omp section
            {
                // Resize stability map if provided
                if (stability_map_ptr) {
                    if (needs_resize) {
                        cv::resize(stability_map_mat, stability_map_work, cv::Size(work_w, work_h), 0, 0, cv::INTER_AREA);
                    } else {
                        stability_map_work = stability_map_mat;
                    }
                }
            }
        }

        // --- OPTIMIZATION 3: Parallel Global Illumination Normalization ---
        #pragma omp parallel sections
        {
            #pragma omp section
            {
                // Normalization for current image
                if (channels > 1) {
                    std::vector<cv::Mat> current_channels;
                    cv::split(current_work, current_channels);
                    #pragma omp parallel for
                    for (int i = 0; i < channels; ++i) {
                        cv::Scalar mean_curr, stddev_curr;
                        cv::meanStdDev(current_channels[i], mean_curr, stddev_curr);
                        // Store results for sync with reference
                    }
                }
            }
            
            #pragma omp section  
            {
                // Parallel processing for reference image statistics
                if (channels > 1) {
                    std::vector<cv::Mat> ref_channels;
                    cv::split(reference_work, ref_channels);
                    #pragma omp parallel for
                    for (int i = 0; i < channels; ++i) {
                        cv::Scalar mean_ref, stddev_ref;
                        cv::meanStdDev(ref_channels[i], mean_ref, stddev_ref);
                        // Store results for sync
                    }
                }
            }
        }

        // Complete normalization synchronously (dependency required)
        if (channels > 1) {
            std::vector<cv::Mat> current_channels, ref_channels;
            cv::split(current_work, current_channels);
            cv::split(reference_work, ref_channels);
            
            #pragma omp parallel for
            for (int i = 0; i < channels; ++i) {
                cv::Scalar mean_curr, stddev_curr, mean_ref, stddev_ref;
                cv::meanStdDev(current_channels[i], mean_curr, stddev_curr);
                cv::meanStdDev(ref_channels[i], mean_ref, stddev_ref);
                if (stddev_curr[0] > 1e-5) {
                    double alpha = stddev_ref[0] / stddev_curr[0];
                    double beta = mean_ref[0] - (mean_curr[0] * alpha);
                    current_channels[i].convertTo(current_channels[i], CV_32F, alpha, beta);
                }
            }
            cv::merge(current_channels, current_work);
        } else {
            cv::Scalar mean_curr, stddev_curr, mean_ref, stddev_ref;
            cv::meanStdDev(current_work, mean_curr, stddev_curr);
            cv::meanStdDev(reference_work, mean_ref, stddev_ref);
            if (stddev_curr[0] > 1e-5) {
                double alpha = stddev_ref[0] / stddev_curr[0];
                double beta = mean_ref[0] - (mean_curr[0] * alpha);
                current_work.convertTo(current_work, CV_32F, alpha, beta);
            }
        }
        
        // --- OPTIMIZATION 4: Parallel Grayscale Conversion ---
        cv::Mat current_image_gray_full, reference_image_gray_full;

        #pragma omp parallel sections
        {
            #pragma omp section
            {
                if (channels > 1) {
                    cv::Mat temp_curr;
                    cv::cvtColor(current_work, temp_curr, cv::COLOR_BGR2GRAY);
                    temp_curr.convertTo(current_image_gray_full, CV_32F);
                } else {
                    current_work.convertTo(current_image_gray_full, CV_32F);
                }
            }
            
            #pragma omp section
            {
                if (channels > 1) {
                    cv::Mat temp_ref;
                    cv::cvtColor(reference_work, temp_ref, cv::COLOR_BGR2GRAY);
                    temp_ref.convertTo(reference_image_gray_full, CV_32F);
                } else {
                    reference_work.convertTo(reference_image_gray_full, CV_32F);
                }
            }
        }

        // --- Noise estimation and parameter adaptation (unchanged) ---
        float global_estimated_noise_sigma = 0.015f;
#ifdef TILE_NOISE_ESTIMATION_HPP
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3) {
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
        }
#endif
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        const float base_motion_sensitivity = motion_sensitivity;
        const float base_noise_offset_factor = noise_offset_factor;
        const float adaptation_range = 0.65f;
        const float noise_threshold_for_adaptation = 0.1f;
        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / noise_threshold_for_adaptation, 1.0f);
        float adapted_motion_sensitivity = base_motion_sensitivity * (1.0f - adaptation_range * adaptation_factor);
        float adapted_noise_offset_factor = base_noise_offset_factor * (1.0f + adaptation_range * adaptation_factor);
        
        // --- OPTIMIZATION 5: Parallel CLAHE & Denoising Pipeline ---
        cv::Mat current_image_gray_full_clahe, reference_image_gray_full_clahe;
        float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
        float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
        float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);
        
        #pragma omp parallel sections
        {
            #pragma omp section
            {
                current_image_gray_full_clahe = current_image_gray_full.clone();
                if (clip_limit > 0.61f) {
                    cv::Mat current_8u;
                    current_image_gray_full.convertTo(current_8u, CV_8U, 255.0);
                    cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
                    clahe->apply(current_8u, current_image_gray_full_clahe);
                    current_image_gray_full_clahe.convertTo(current_image_gray_full_clahe, CV_32F, 1.0 / 255.0);
                }
            }
            
            #pragma omp section
            {
                reference_image_gray_full_clahe = reference_image_gray_full.clone();
                if (clip_limit > 0.61f) {
                    cv::Mat ref_8u;
                    reference_image_gray_full.convertTo(ref_8u, CV_8U, 255.0);
                    cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
                    clahe->apply(ref_8u, reference_image_gray_full_clahe);
                    reference_image_gray_full_clahe.convertTo(reference_image_gray_full_clahe, CV_32F, 1.0 / 255.0);
                }
            }
        }
        
        // Parallel denoising (unchanged from previous optimization)
        const float noise_activation_threshold = 0.07f;
        const float median_filter_threshold = 0.14f;
        if (global_estimated_noise_sigma > noise_activation_threshold) {
            #pragma omp parallel sections
            {
                #pragma omp section
                {
                    if (global_estimated_noise_sigma >= median_filter_threshold) {
                        cv::medianBlur(current_image_gray_full_clahe, current_image_gray_full, 5);
                    } else {
                        const float transition_range = median_filter_threshold - noise_activation_threshold;
                        float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                        denoising_strength_factor = std::min(1.0f, std::max(0.0f, denoising_strength_factor));
                        if (denoising_strength_factor > 0.01f) {
                            int kernel_size = 5; 
                            double sigma_color = 5.0 + (denoising_strength_factor * 45.0);
                            double sigma_space = 7.0;
                            cv::bilateralFilter(current_image_gray_full_clahe, current_image_gray_full, kernel_size, sigma_color / 255.0, sigma_space);
                        }
                    }
                }
                
                #pragma omp section
                {
                    if (global_estimated_noise_sigma >= median_filter_threshold) {
                        cv::medianBlur(reference_image_gray_full_clahe, reference_image_gray_full, 5);
                    } else {
                        const float transition_range = median_filter_threshold - noise_activation_threshold;
                        float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                        denoising_strength_factor = std::min(1.0f, std::max(0.0f, denoising_strength_factor));
                        if (denoising_strength_factor > 0.01f) {
                            int kernel_size = 5; 
                            double sigma_color = 5.0 + (denoising_strength_factor * 45.0);
                            double sigma_space = 7.0;
                            cv::bilateralFilter(reference_image_gray_full_clahe, reference_image_gray_full, kernel_size, sigma_color / 255.0, sigma_space);
                        }
                    }
                }
            }
        } else {
             current_image_gray_full = current_image_gray_full_clahe;
             reference_image_gray_full = reference_image_gray_full_clahe;
        }

        // --- Flat tile detection (unchanged) ---
        std::vector<bool> is_tile_flat;
        std::vector<cv::Mat> ref_channels_for_flat_detection;
        if (channels > 1) {
            cv::split(reference_work, ref_channels_for_flat_detection);
        } else {
            ref_channels_for_flat_detection.push_back(reference_work);
        }
        TextureAnalysis::detect_flat_tiles(ref_channels_for_flat_detection, tile_h, tile_w, channels, FLATNESS_VARIANCE_THRESHOLD, is_tile_flat);

        // --- OPTIMIZATION 6: Work Resolution Processing with Full Resolution Output ---
        // Process at working resolution, but accumulate to full resolution
        cv::Mat final_image_sum_work = cv::Mat::zeros(work_h, work_w, CV_32FC(channels));
        cv::Mat weight_map_sum_work = cv::Mat::zeros(work_h, work_w, CV_32FC1);

        // Main processing loop (adapted for working resolution)
        const int total_tiles = num_row_starts * num_col_starts;
        const int num_tiles_x = (work_w > 0 && tile_w > 0) ? (work_w + tile_w - 1) / tile_w : 0;
        
        std::vector<std::pair<int, int>> tile_indices;
        tile_indices.reserve(total_tiles);
        for (int i = 0; i < num_row_starts; i++) {
            for (int j = 0; j < num_col_starts; j++) {
                int r = row_starts[i];
                int c = col_starts[j];
                if (r + tile_h <= work_h && c + tile_w <= work_w) {
                    tile_indices.emplace_back(i, j);
                }
            }
        }
        
        const int valid_tiles = tile_indices.size();
        if (valid_tiles > 0) {
            // Main tile processing loop (same as previous optimization but on working resolution)
            #pragma omp parallel
            {
                MotionMatching::MBMBuffers mbm_buffers_th;
                if (tile_h > 0 && tile_w > 0) {
                    mbm_buffers_th.diff_workspace.create(tile_h, tile_w, CV_32FC1);
                    mbm_buffers_th.grad_x.create(tile_h, tile_w, CV_32F);
                    mbm_buffers_th.grad_y.create(tile_h, tile_w, CV_32F);
                    mbm_buffers_th.grad_mag_current.create(tile_h, tile_w, CV_32FC1);
                }

                cv::Mat temp_weighted_tile(tile_h, tile_w, CV_32FC(channels));
                cv::Mat temp_weight_tile(tile_h, tile_w, CV_32FC1);
                cv::Mat weighted_mask(tile_h, tile_w, CV_32FC1);
                cv::Mat weighted_mask_color;
                if (channels > 1) {
                    weighted_mask_color.create(tile_h, tile_w, CV_32FC(channels));
                }

                #pragma omp for schedule(guided, 4) nowait
                for (int tile_idx = 0; tile_idx < valid_tiles; ++tile_idx) {
                    const auto& [i, j] = tile_indices[tile_idx];
                    int r = row_starts[i];
                    int c = col_starts[j];

                    cv::Rect tile_roi(c, r, tile_w, tile_h);

                    const cv::Mat current_tile_for_accumulation = current_work(tile_roi);
                    const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                    if (current_tile_gray_for_mbm.empty()) continue;

                    MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_similarity(
                        current_tile_gray_for_mbm, reference_tile_gray_for_mbm,
                        GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_th
                    );

                    float confidence = 0.0f;
                    if (mbm_result.success) {
                        confidence = MotionMatching::calculate_match_confidence(
                            mbm_result, global_estimated_noise_sigma, 
                            adapted_motion_sensitivity, adapted_noise_offset_factor);

                        if (confidence > 0.0f && !stability_map_work.empty()) {
                            cv::Scalar mean_stability = cv::mean(stability_map_work(tile_roi));
                            confidence *= static_cast<float>(mean_stability[0]);
                        }
                        
                        const int tx = c / tile_w;
                        const int ty = r / tile_h;
                        const int flat_tile_idx = ty * num_tiles_x + tx;
                        if (flat_tile_idx < is_tile_flat.size() && is_tile_flat[flat_tile_idx]) {
                            confidence = std::min(confidence * FLATNESS_CONFIDENCE_BOOST, 1.0f);
                        }
                    }
                    
                    if (confidence < 1e-5f) continue;
                    
                    // Vectorized computation and atomic accumulation (same as before)
                    cv::multiply(base_window_tile_mat, confidence, weighted_mask);
                    cv::multiply(base_window_tile_mat, confidence, temp_weight_tile);

                    if (channels > 1) {
                        std::vector<cv::Mat> mask_channels(channels);
                        for (int ch = 0; ch < channels; ++ch) {
                            mask_channels[ch] = weighted_mask;
                        }
                        cv::merge(mask_channels, weighted_mask_color);
                        cv::multiply(current_tile_for_accumulation, weighted_mask_color, temp_weighted_tile);
                    } else {
                        cv::multiply(current_tile_for_accumulation, weighted_mask, temp_weighted_tile);
                    }

                    // Atomic accumulation to work resolution buffers
                    float* final_sum_roi_ptr = reinterpret_cast<float*>(final_image_sum_work.ptr(r)) + c * channels;
                    float* weight_sum_roi_ptr = reinterpret_cast<float*>(weight_map_sum_work.ptr(r)) + c;
                    
                    const float* temp_weighted_ptr = reinterpret_cast<const float*>(temp_weighted_tile.ptr(0));
                    const float* temp_weight_ptr = reinterpret_cast<const float*>(temp_weight_tile.ptr(0));

                    for (int tile_r = 0; tile_r < tile_h; ++tile_r) {
                        const int row_offset = tile_r * work_w;
                        const int tile_row_offset = tile_r * tile_w;
                        
                        if (tile_r + 1 < tile_h) {
                            __builtin_prefetch(&weight_sum_roi_ptr[(tile_r + 1) * work_w], 1, 1);
                            __builtin_prefetch(&final_sum_roi_ptr[(tile_r + 1) * work_w * channels], 1, 1);
                        }
                        
                        for (int tile_c = 0; tile_c < tile_w; ++tile_c) {
                            const int global_idx = row_offset + tile_c;
                            const int tile_pixel_idx = tile_row_offset + tile_c;
                            
                            const float weight_val = temp_weight_ptr[tile_pixel_idx];
                            if (weight_val > 1e-8f) {
                                #pragma omp atomic
                                weight_sum_roi_ptr[global_idx] += weight_val;
                            }
                            
                            const int base_img_idx = global_idx * channels;
                            const int base_tile_idx = tile_pixel_idx * channels;
                            
                            for (int ch = 0; ch < channels; ++ch) {
                                const float pixel_val = temp_weighted_ptr[base_tile_idx + ch];
                                if (std::abs(pixel_val) > 1e-8f) {
                                    #pragma omp atomic
                                    final_sum_roi_ptr[base_img_idx + ch] += pixel_val;
                                }
                            }
                        }
                    }
                }
            }
        }

        // --- OPTIMIZATION 7: Resize Results Back to Full Resolution ---
        cv::Mat final_image_sum_mat(h_img, w_img, CV_32FC(channels), final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);

        #pragma omp parallel sections
        {
            #pragma omp section
            {
                if (needs_resize) {
                    cv::resize(final_image_sum_work, final_image_sum_mat, cv::Size(w_img, h_img), 0, 0, cv::INTER_CUBIC);
                } else {
                    final_image_sum_work.copyTo(final_image_sum_mat);
                }
            }
            
            #pragma omp section
            {
                if (needs_resize) {
                    cv::resize(weight_map_sum_work, weight_map_sum_mat, cv::Size(w_img, h_img), 0, 0, cv::INTER_CUBIC);
                } else {
                    weight_map_sum_work.copyTo(weight_map_sum_mat);
                }
            }
        }
    }

    // --- Fungsi normalize_accumulated_image_jit  ---
    void normalize_accumulated_image_jit(
        float *final_image_ptr,
        const float *weight_map_sum_ptr,
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;
        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0)
            return;
        int mat_type = CV_32FC(channels);
        if (mat_type == 0 && channels > 0)
            return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

#pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy)
        {
            float *final_pixel_row_ptr = final_image_mat.ptr<float>(gy);
            const float *weight_map_sum_row_ptr = weight_map_sum_mat.ptr<const float>(gy);
            for (int gx = 0; gx < w; ++gx)
            {
                float total_weight = weight_map_sum_row_ptr[gx];
                int pixel_idx_base = gx * channels;
                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row_ptr[pixel_idx_base + ch] *= inv_total_weight;
                    }
                }
                else
                {
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row_ptr[pixel_idx_base + ch] = 0.0f;
                    }
                }
            }
        }
    }
}