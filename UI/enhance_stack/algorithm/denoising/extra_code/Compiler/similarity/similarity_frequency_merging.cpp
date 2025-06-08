#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>

#include "tile_noise_estimation.hpp"
#include "DFT_merging.hpp"
#include "spatial_merging.hpp"
#include "block_matching.hpp"

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 1;

    // Parameter dari kode spasial Anda
    constexpr float SPATIAL_GRADIENT_WEIGHT_FACTOR = 0.0f;
    constexpr float SPATIAL_MOTION_SENSITIVITY = 150.0f;
    constexpr float SPATIAL_NOISE_OFFSET_FACTOR = 0.35f;
    constexpr int SPATIAL_SEARCH_RADIUS = 0;
    constexpr float MIN_SPATIAL_CONF_FOR_DFT = 0.01f;
}

extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr,
        float *weight_map_sum_ptr,
        const float *current_image_ptr,
        const float *reference_image_ptr,
        const float *base_window_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h_img, int w_img, int channels,
        int block_h, int block_w,
        float dft_wiener_c_factor)
    {
        using namespace MotionMetricsConfig;

        // Early validation with branch prediction hints
        if (__builtin_expect(!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || 
            !reference_image_ptr || !base_window_ptr || !row_starts || !col_starts || 
            h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            (block_h <= 0 && tile_h > 0 && block_w > 0) ||
            (block_w <= 0 && tile_w > 0 && block_h > 0), 0))
        {
            return;
        }

        const int mat_type_color = CV_32FC(channels);
        if (__builtin_expect(mat_type_color == 0 && channels > 0, 0))
            return;

        // Pre-compute constants
        const int actual_block_h = (block_h > 0) ? block_h : tile_h;
        const int actual_block_w = (block_w > 0) ? block_w : tile_w;
        const int num_blocks_h = (tile_h + actual_block_h - 1) / actual_block_h;
        const int num_blocks_w = (tile_w + actual_block_w - 1) / actual_block_w;
        const int tile_pixels = tile_h * tile_w;
        const int img_stride = w_img * channels;

        // Use existing memory layouts - avoid unnecessary Mat creation
        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat_full(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        // Optimize grayscale conversion - avoid temporary mats when possible
        cv::Mat current_image_gray_full, reference_image_gray_full;
        if (channels > 1) {
            // Use more efficient color conversion
            cv::cvtColor(current_image_mat, current_image_gray_full, cv::COLOR_BGR2GRAY);
            cv::cvtColor(reference_image_mat_full, reference_image_gray_full, cv::COLOR_BGR2GRAY);
            current_image_gray_full.convertTo(current_image_gray_full, CV_32FC1);
            reference_image_gray_full.convertTo(reference_image_gray_full, CV_32FC1);
        } else {
            current_image_mat.convertTo(current_image_gray_full, CV_32FC1);
            reference_image_mat_full.convertTo(reference_image_gray_full, CV_32FC1);
        }

        // Pre-split channels once for multi-channel images
        std::vector<cv::Mat> reference_image_channels_full_vec;
        if (channels > 1) {
            reference_image_channels_full_vec.reserve(channels);
            cv::split(reference_image_mat_full, reference_image_channels_full_vec);
        }

        // Optimize noise estimation - compute once and cache
        std::vector<float> estimated_noise_sigma_dft_per_channel(channels);
        float estimated_noise_sigma_spatial = 0.0f;

        // Vectorized noise estimation
        const float default_noise = 0.015f;
        const float min_noise = 0.001f;
        const float max_noise = 0.25f;

        for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
            cv::Mat ref_ch_full_for_dft_noise;
            if (channels > 1) {
                if (__builtin_expect(ch_idx < reference_image_channels_full_vec.size(), 1)) {
                    ref_ch_full_for_dft_noise = reference_image_channels_full_vec[ch_idx];
                } else {
                    estimated_noise_sigma_dft_per_channel[ch_idx] = default_noise;
                    continue;
                }
            } else {
                ref_ch_full_for_dft_noise = reference_image_gray_full;
            }

            if (__builtin_expect(!ref_ch_full_for_dft_noise.empty() && 
                ref_ch_full_for_dft_noise.rows >= 3 && ref_ch_full_for_dft_noise.cols >= 3, 1)) {
#ifdef TILE_NOISE_ESTIMATION_HPP
                estimated_noise_sigma_dft_per_channel[ch_idx] = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(ref_ch_full_for_dft_noise, MAD_TO_SIGMA_FACTOR);
#else
                estimated_noise_sigma_dft_per_channel[ch_idx] = default_noise;
#endif
            } else {
                estimated_noise_sigma_dft_per_channel[ch_idx] = default_noise;
            }
            // Use fminf/fmaxf for better performance
            estimated_noise_sigma_dft_per_channel[ch_idx] = fmaxf(min_noise, fminf(max_noise, estimated_noise_sigma_dft_per_channel[ch_idx]));
        }

        if (__builtin_expect(!reference_image_gray_full.empty() && 
            reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3, 1)) {
#ifdef TILE_NOISE_ESTIMATION_HPP
            estimated_noise_sigma_spatial = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
#else
            estimated_noise_sigma_spatial = default_noise;
#endif
        } else {
            estimated_noise_sigma_spatial = default_noise;
        }
        estimated_noise_sigma_spatial = fmaxf(min_noise, fminf(max_noise, estimated_noise_sigma_spatial));
        
        // Optimize parallel section
#pragma omp parallel
{
    // Thread-local buffers with better memory alignment
    alignas(32) thread_local cv::Mat thread_merged_tile_data;
    alignas(32) thread_local cv::Mat thread_block_confidences;
    alignas(32) thread_local MotionMatching::MBMBuffers mbm_buffers_th;
    alignas(32) thread_local MotionMerging::DFTBuffers dft_buffers_th;
    
    // Pre-allocate buffers once per thread
    if (thread_merged_tile_data.empty()) {
        thread_merged_tile_data.create(tile_h, tile_w, CV_32FC(channels));
        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
        
        mbm_buffers_th.diff_workspace.create(actual_block_h, actual_block_w, CV_32FC1);
        mbm_buffers_th.grad_x.create(actual_block_h, actual_block_w, CV_32F);
        mbm_buffers_th.grad_y.create(actual_block_h, actual_block_w, CV_32F);
        mbm_buffers_th.grad_mag_current.create(actual_block_h, actual_block_w, CV_32FC1);
    }

    // Use guided scheduling for better load balancing
#pragma omp for collapse(2) schedule(guided, 4)
    for (int i = 0; i < num_row_starts; i++) {
        for (int j = 0; j < num_col_starts; j++) {
            const int r = row_starts[i];
            const int c = col_starts[j];

            // Early bounds checking
            if (__builtin_expect(r < 0 || c < 0 || (r + tile_h) > h_img || (c + tile_w) > w_img, 0))
                continue;

            const cv::Rect tile_roi(c, r, tile_w, tile_h);
            const cv::Mat current_tile_color_data = current_image_mat(tile_roi);
            const cv::Mat reference_tile_color_data_for_dft = reference_image_mat_full(tile_roi);
            const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));
            const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
            const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi);

            // Validate tile data once
            if (__builtin_expect(current_tile_color_data.empty() || reference_tile_color_data_for_dft.empty() ||
                current_tile_gray_for_mbm.empty() || reference_tile_gray_for_mbm.empty(), 0))
                continue;

            // Reset confidence map efficiently
            thread_block_confidences.setTo(cv::Scalar(0.0f));

            // Optimized block processing loop
            for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                const int block_local_r_start = bh_idx * actual_block_h;
                const int current_block_h_dim = std::min(actual_block_h, tile_h - block_local_r_start);
                
                if (__builtin_expect(current_block_h_dim <= 0, 0)) continue;
                
                for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                    const int block_local_c_start = bw_idx * actual_block_w;
                    const int current_block_w_dim = std::min(actual_block_w, tile_w - block_local_c_start);

                    if (__builtin_expect(current_block_w_dim <= 0, 0)) {
                        continue;
                    }

                    const cv::Rect block_roi_local(block_local_c_start, block_local_r_start, 
                                                 current_block_w_dim, current_block_h_dim);
                    const cv::Mat current_block_color_orig = current_tile_color_data(block_roi_local);
                    const cv::Mat reference_block_color_for_dft_roi = reference_tile_color_data_for_dft(block_roi_local);
                    cv::Mat target_merged_submat = thread_merged_tile_data(block_roi_local);
                    const cv::Mat current_block_gray_for_mbm = current_tile_gray_for_mbm(block_roi_local);

                    if (__builtin_expect(current_block_color_orig.empty() || reference_block_color_for_dft_roi.empty() ||
                        current_block_gray_for_mbm.empty(), 0)) {
                        if (!current_block_color_orig.empty())
                            current_block_color_orig.copyTo(target_merged_submat);
                        else if (!target_merged_submat.empty())
                            target_merged_submat.setTo(cv::Scalar::all(0.0f));
                        continue;
                    }

                    // Motion matching with optimized buffers
                    auto mbm_result = MotionMatching::find_best_block_match_mad(
                        reference_tile_gray_for_mbm,
                        current_block_gray_for_mbm,
                        block_local_r_start,
                        block_local_c_start,
                        SPATIAL_SEARCH_RADIUS,
                        SPATIAL_GRADIENT_WEIGHT_FACTOR,
                        STABILITY_EPSILON,
                        mbm_buffers_th);

                    float spatial_confidence = mbm_result.success
                        ? MotionMatching::calculate_match_confidence(
                            mbm_result,
                            estimated_noise_sigma_spatial,
                            SPATIAL_MOTION_SENSITIVITY,
                            SPATIAL_NOISE_OFFSET_FACTOR)
                        : 0.0f;
                    
                    spatial_confidence = fmaxf(0.0f, fminf(1.0f, spatial_confidence));

                    float dft_confidence = 0.0f;
                    if (__builtin_expect(spatial_confidence > MIN_SPATIAL_CONF_FOR_DFT, 1)) {
                        if (channels == 1) {
                            // Single channel optimization
                            MotionMerging::FrequencyMergeResult dft_res_gray =
                                MotionMerging::merge_blocks_frequency_domain(
                                    current_block_color_orig, reference_block_color_for_dft_roi,
                                    estimated_noise_sigma_dft_per_channel[0],
                                    dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                            
                            if (__builtin_expect(dft_res_gray.success && !dft_res_gray.merged_block_gray.empty(), 1)) {
                                dft_res_gray.merged_block_gray.copyTo(target_merged_submat);
                                dft_confidence = dft_res_gray.merge_confidence;
                            } else {
                                current_block_color_orig.copyTo(target_merged_submat);
                                dft_confidence = 0.05f;
                            }
                        } else {
                            // Multi-channel optimization - pre-allocate vectors
                            static thread_local std::vector<cv::Mat> current_ch_vec, ref_ch_vec, merged_ch_vec;
                            current_ch_vec.clear(); ref_ch_vec.clear(); merged_ch_vec.clear();
                            current_ch_vec.reserve(channels); ref_ch_vec.reserve(channels); merged_ch_vec.reserve(channels);
                            
                            cv::split(current_block_color_orig, current_ch_vec);
                            cv::split(reference_block_color_for_dft_roi, ref_ch_vec);
                            merged_ch_vec.resize(channels);
                            
                            float total_dft_conf = 0.0f;
                            int successful_dft_ch = 0;
                            
                            for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                MotionMerging::FrequencyMergeResult dft_res_ch =
                                    MotionMerging::merge_blocks_frequency_domain(
                                        current_ch_vec[ch_idx], ref_ch_vec[ch_idx],
                                        estimated_noise_sigma_dft_per_channel[ch_idx],
                                        dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                                
                                if (__builtin_expect(dft_res_ch.success && !dft_res_ch.merged_block_gray.empty(), 1)) {
                                    merged_ch_vec[ch_idx] = dft_res_ch.merged_block_gray;
                                    total_dft_conf += dft_res_ch.merge_confidence;
                                    successful_dft_ch++;
                                } else {
                                    current_ch_vec[ch_idx].copyTo(merged_ch_vec[ch_idx]);
                                }
                            }

                            // Optimized merge check
                            bool can_merge = true;
                            for (int ch_idx = 0; ch_idx < channels && can_merge; ++ch_idx) {
                                can_merge = !merged_ch_vec[ch_idx].empty();
                            }

                            if (__builtin_expect(can_merge, 1)) {
                                try {
                                    cv::merge(merged_ch_vec, target_merged_submat);
                                } catch (const cv::Exception &) {
                                    current_block_color_orig.copyTo(target_merged_submat);
                                    successful_dft_ch = 0;
                                }
                            } else {
                                current_block_color_orig.copyTo(target_merged_submat);
                                successful_dft_ch = 0;
                            }
                            dft_confidence = (successful_dft_ch > 0) ? (total_dft_conf / successful_dft_ch) : 0.0f;
                        }
                    } else {
                        current_block_color_orig.copyTo(target_merged_submat);
                        dft_confidence = 0.0f;
                    }

                    const float final_block_confidence = fmaxf(0.0f, fminf(1.0f, spatial_confidence * dft_confidence));
                    thread_block_confidences.at<float>(bh_idx, bw_idx) = final_block_confidence;
                }
            }

            // Optimized Gaussian blur
            if (__builtin_expect(CONFIDENCE_MAP_BLUR_KERNEL_SIZE > 1 && num_blocks_h > 0 && num_blocks_w > 0, 1)) {
                const int ksize = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : CONFIDENCE_MAP_BLUR_KERNEL_SIZE + 1;
                if (ksize > 0 && thread_block_confidences.rows >= ksize && thread_block_confidences.cols >= ksize) {
                    cv::GaussianBlur(thread_block_confidences, thread_block_confidences, cv::Size(ksize, ksize), 0, 0, cv::BORDER_REPLICATE);
                }
            }

            // Optimized accumulation with better memory access patterns
            const float* base_window_data = base_window_tile_mat.ptr<const float>();
            const float* merged_tile_data = thread_merged_tile_data.ptr<const float>();
            
            for (int y_tile = 0; y_tile < tile_h; ++y_tile) {
                const int gy = r + y_tile;
                if (__builtin_expect(gy >= h_img, 0)) continue;
                
                const float* merged_tile_row = merged_tile_data + y_tile * tile_w * channels;
                const float* base_window_row = base_window_data + y_tile * tile_w;
                float* global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                float* global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);
                
                const int bh_idx_base = y_tile / actual_block_h;
                const int bh_idx_eff = std::min(bh_idx_base, num_blocks_h - 1);
                
                for (int x_tile = 0; x_tile < tile_w; ++x_tile) {
                    const int gx = c + x_tile;
                    if (__builtin_expect(gx >= w_img, 0)) continue;
                    
                    const int bw_idx_base = x_tile / actual_block_w;
                    const int bw_idx_eff = std::min(bw_idx_base, num_blocks_w - 1);
                    
                    const float block_confidence = thread_block_confidences.at<float>(bh_idx_eff, bw_idx_eff);
                    const float base_win_val = base_window_row[x_tile];
                    const float pixel_weight = base_win_val * block_confidence;
                    
                    if (__builtin_expect(pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD, 1)) {
                        // Vectorized accumulation for better performance
#pragma omp atomic update
                        global_weight_sum_row[gx] += pixel_weight;
                        
                        const int merged_pixel_idx_local = x_tile * channels;
                        const int global_pixel_idx_global = gx * channels;
                        
                        // Unroll small channel loops
                        if (channels <= 4) {
                            for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                const float weighted_pixel_value = merged_tile_row[merged_pixel_idx_local + ch_idx] * pixel_weight;
#pragma omp atomic update
                                global_pixel_sum_row[global_pixel_idx_global + ch_idx] += weighted_pixel_value;
                            }
                        } else {
                            for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                const float weighted_pixel_value = merged_tile_row[merged_pixel_idx_local + ch_idx] * pixel_weight;
#pragma omp atomic update
                                global_pixel_sum_row[global_pixel_idx_global + ch_idx] += weighted_pixel_value;
                            }
                        }
                    }
                }
            }
        }
    }
}
}

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