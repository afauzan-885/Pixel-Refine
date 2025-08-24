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
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;
    constexpr float FLATNESS_VARIANCE_THRESHOLD = 15.0f;
    constexpr float FLATNESS_CONFIDENCE_BOOST = 1.7f;
}

// =======================================================================================
// === FUNGSI HELPER (generate_pyramid_guidance_map) TIDAK BERUBAH                     ===
// =======================================================================================
static cv::Mat generate_pyramid_guidance_map(
    const cv::Mat &current_image_gray_full,
    const cv::Mat &reference_image_gray_full,
    int tile_h, int tile_w, int search_radius,
    float motion_sensitivity, float noise_offset_factor, float global_estimated_noise_sigma)
{
    using namespace MotionMetricsConfig;
    using namespace MotionMatching;

    // --- Tahap A: Piramida Level 1 (1/4) - Fondasi Paling Kasar ---
    cv::Mat current_image_gray_half, reference_image_gray_half;
    cv::pyrDown(current_image_gray_full, current_image_gray_half);
    cv::pyrDown(reference_image_gray_full, reference_image_gray_half);

    cv::Mat current_image_gray_quarter, reference_image_gray_quarter;
    cv::pyrDown(current_image_gray_half, current_image_gray_quarter);
    cv::pyrDown(reference_image_gray_half, reference_image_gray_quarter);

    cv::Mat blurred_current_quarter, blurred_reference_quarter;
    cv::GaussianBlur(current_image_gray_quarter, blurred_current_quarter, cv::Size(3, 3), 0.8);
    cv::GaussianBlur(reference_image_gray_quarter, blurred_reference_quarter, cv::Size(3, 3), 0.8);

    cv::Mat confidence_map_quarter(current_image_gray_quarter.size(), CV_32FC1, cv::Scalar(0.0f));
    int tile_h_quarter = std::max(1, tile_h / 4);
    int tile_w_quarter = std::max(1, tile_w / 4);
    int search_radius_quarter = search_radius / 4;

#pragma omp parallel for schedule(static)
    for (int r_q = 0; r_q < blurred_current_quarter.rows; r_q += tile_h_quarter)
    {
        MBMBuffers buffers_q;
        for (int c_q = 0; c_q < blurred_current_quarter.cols; c_q += tile_w_quarter)
        {
            int current_w = std::min(tile_w_quarter, blurred_current_quarter.cols - c_q);
            int current_h = std::min(tile_h_quarter, blurred_current_quarter.rows - r_q);
            if (current_w <= 0 || current_h <= 0)
                continue;

            buffers_q.diff_workspace.create(current_h, current_w, CV_32FC1);
            buffers_q.grad_x.create(current_h, current_w, CV_32F);
            buffers_q.grad_y.create(current_h, current_w, CV_32F);
            buffers_q.grad_mag_current.create(current_h, current_w, CV_32FC1);

            cv::Rect roi_q(c_q, r_q, current_w, current_h);
            BlockMatchResult res_q = find_best_block_match_mad(blurred_current_quarter(roi_q), blurred_reference_quarter, r_q, c_q, search_radius_quarter, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_q);
            float conf_q = res_q.success ? calculate_match_confidence(res_q, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
            confidence_map_quarter(roi_q).setTo(cv::Scalar(conf_q));
        }
    }

    // --- Tahap B: Piramida Level 2 (1/2) - Penyempurnaan Menengah ---
    cv::Mat guidance_map_for_half;
    cv::resize(confidence_map_quarter, guidance_map_for_half, current_image_gray_half.size(), 0, 0, cv::INTER_LINEAR);

    cv::Mat confidence_map_half(current_image_gray_half.size(), CV_32FC1, cv::Scalar(0.0f));
    int tile_h_half = std::max(1, tile_h / 2);
    int tile_w_half = std::max(1, tile_w / 2);
    int search_radius_half = search_radius / 2;

#pragma omp parallel for schedule(static)
    for (int r_h = 0; r_h < current_image_gray_half.rows; r_h += tile_h_half)
    {
        MBMBuffers buffers_h;
        for (int c_h = 0; c_h < current_image_gray_half.cols; c_h += tile_h_half)
        {
            int current_w = std::min(tile_w_half, current_image_gray_half.cols - c_h);
            int current_h = std::min(tile_h_half, current_image_gray_half.rows - r_h);
            if (current_w <= 0 || current_h <= 0)
                continue;

            buffers_h.diff_workspace.create(current_h, current_w, CV_32FC1);
            buffers_h.grad_x.create(current_h, current_w, CV_32F);
            buffers_h.grad_y.create(current_h, current_w, CV_32F);
            buffers_h.grad_mag_current.create(current_h, current_w, CV_32FC1);

            cv::Rect roi_h(c_h, r_h, current_w, current_h);
            BlockMatchResult res_h = find_best_block_match_mad(current_image_gray_half(roi_h), reference_image_gray_half, r_h, c_h, search_radius_half, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_h);
            float local_conf_h = res_h.success ? calculate_match_confidence(res_h, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;

            cv::Scalar mean_guidance_scalar = cv::mean(guidance_map_for_half(roi_h));
            float guidance_conf = static_cast<float>(mean_guidance_scalar[0]);

            confidence_map_half(roi_h).setTo(cv::Scalar(local_conf_h * guidance_conf));
        }
    }

    // --- Tahap C: Upscale peta level 2 menjadi peta panduan akhir ---
    cv::Mat guidance_confidence_map_final;
    cv::resize(confidence_map_half, guidance_confidence_map_final, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);

    return guidance_confidence_map_final;
}

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
        int block_h, int block_w, int search_radius,
        float motion_sensitivity,
        float noise_offset_factor)
    {
        using namespace MotionMetricsConfig;

        // --- Bagian 1: Inisialisasi dan Persiapan Awal ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0)
        {
            return;
        }

        int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0)
            return;

        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        cv::Mat stability_map_mat;
        if (stability_map_ptr)
        {
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
        }

        // --- Buffer Pra-Pemrosesan ---
        cv::Mat current_image_gray_full, reference_image_gray_full;
        cv::Mat current_image_gray_temp, reference_image_gray_temp;

        // --- Konversi ke Grayscale (langsung ke buffer utama) ---
        if (channels > 1)
        {
            cv::Mat temp_curr, temp_ref;
            cv::cvtColor(current_image_mat, temp_curr, cv::COLOR_BGR2GRAY);
            cv::cvtColor(reference_image_mat, temp_ref, cv::COLOR_BGR2GRAY);
            temp_curr.convertTo(current_image_gray_full, CV_32F);
            temp_ref.convertTo(reference_image_gray_full, CV_32F);
        }
        else
        {
            current_image_mat.convertTo(current_image_gray_full, CV_32F);
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }

        // --- Estimasi Noise (dilakukan pada gambar grayscale bersih sebelum modifikasi) ---
        float global_estimated_noise_sigma = 0.015f;
#ifdef TILE_NOISE_ESTIMATION_HPP
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
        {
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
        }
#endif
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        // === PENYEMPURNAAN 1: Adaptasi Parameter Sensitivitas Berdasarkan Noise ==============
        const float base_motion_sensitivity = motion_sensitivity;
        const float base_noise_offset_factor = noise_offset_factor;
        const float adaptation_range = 0.65f;
        const float noise_threshold_for_adaptation = 0.1f; // Adaptasi hanya terjadi di bawah level noise ini

        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / noise_threshold_for_adaptation, 1.0f);

        float adapted_motion_sensitivity = base_motion_sensitivity * (1.0f - adaptation_range * adaptation_factor);
        float adapted_noise_offset_factor = base_noise_offset_factor * (1.0f + adaptation_range * adaptation_factor);
        
        // === PENYEMPURNAAN 2: Rantai Pra-Pemrosesan Efisien =================================
        // Tahap A: CLAHE Adaptif
        float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
        float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
        float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);

        if (clip_limit > 0.61f)
        {
            cv::Mat current_8u, ref_8u;
            current_image_gray_full.convertTo(current_8u, CV_8U, 255.0);
            reference_image_gray_full.convertTo(ref_8u, CV_8U, 255.0);

            cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
            
            clahe->apply(current_8u, current_8u);
            clahe->apply(ref_8u, ref_8u);

            current_8u.convertTo(current_image_gray_full, CV_32F, 1.0 / 255.0);
            ref_8u.convertTo(reference_image_gray_full, CV_32F, 1.0 / 255.0);
        }
        
        // Tahap B: Bilateral Denoising Adaptif
        const float noise_activation_threshold = 0.08f;
        const float noise_full_strength_threshold = 0.85f;
        const float transition_range = noise_full_strength_threshold - noise_activation_threshold;
        float denoising_strength_factor = 0.0f;

        if (global_estimated_noise_sigma > noise_activation_threshold)
        {
            denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
            denoising_strength_factor = std::min(1.0f, std::max(0.0f, denoising_strength_factor));
        }

        if (denoising_strength_factor > 0.01f)
        {
            int kernel_size = 5; 
            double sigma_color = 5.0 + (denoising_strength_factor * 45.0);
            double sigma_space = 7.0;

            cv::bilateralFilter(current_image_gray_full, current_image_gray_temp, kernel_size, sigma_color / 255.0, sigma_space);
            cv::bilateralFilter(reference_image_gray_full, reference_image_gray_temp, kernel_size, sigma_color / 255.0, sigma_space);

            cv::swap(current_image_gray_full, current_image_gray_temp);
            cv::swap(reference_image_gray_full, reference_image_gray_temp);
        }

        // --- Deteksi Area Datar (Dilakukan pada gambar original) ---
        std::vector<bool> is_tile_flat;
        std::vector<cv::Mat> ref_channels_for_flat_detection;
        if (channels > 1)
        {
            cv::split(reference_image_mat, ref_channels_for_flat_detection);
        }
        else
        {
            ref_channels_for_flat_detection.push_back(reference_image_mat);
        }
        TextureAnalysis::detect_flat_tiles(ref_channels_for_flat_detection, tile_h, tile_w, channels, FLATNESS_VARIANCE_THRESHOLD, is_tile_flat);

        // --- Menghasilkan Peta Panduan Spasial (menggunakan parameter yang sudah diadaptasi) ---
        cv::Mat guidance_confidence_map_final = generate_pyramid_guidance_map(
            current_image_gray_full,
            reference_image_gray_full,
            tile_h, tile_w, search_radius,
            adapted_motion_sensitivity,
            adapted_noise_offset_factor,
            global_estimated_noise_sigma);

        // --- Bagian 3: Proses Utama dengan Modulasi ---
        #pragma omp parallel
        {
            MotionMatching::MBMBuffers mbm_buffers_th;
            int mbm_alloc_h = (block_h > 0) ? block_h : tile_h;
            int mbm_alloc_w = (block_w > 0) ? block_w : tile_w;
            if (mbm_alloc_h > 0 && mbm_alloc_w > 0)
            {
                mbm_buffers_th.diff_workspace.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
                mbm_buffers_th.grad_x.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_y.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_mag_current.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
            }
            cv::Mat thread_block_confidences;
            const int num_tiles_x = (w_img > 0 && tile_w > 0) ? w_img / tile_w : 0;

            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h_img || (c + tile_w) > w_img || tile_h <= 0 || tile_w <= 0)
                        continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);

                    const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                    const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                    if (current_tile_gray_for_mbm.empty() || reference_tile_gray_for_mbm.empty() || current_tile_for_accumulation.empty())
                        continue;

                    int actual_block_h = (block_h > 0) ? block_h : tile_h;
                    int actual_block_w = (block_w > 0) ? block_w : tile_w;
                    int num_blocks_h = (tile_h > 0 && actual_block_h > 0) ? (tile_h + actual_block_h - 1) / actual_block_h : 0;
                    int num_blocks_w = (tile_w > 0 && actual_block_w > 0) ? (tile_w + actual_block_w - 1) / actual_block_w : 0;

                    if (num_blocks_h == 0 || num_blocks_w == 0)
                        continue;

                    if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w)
                    {
                        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                    }

                    const int tx = (tile_w > 0) ? c / tile_w : 0;
                    const int ty = (tile_h > 0) ? r / tile_h : 0;
                    const int tile_idx = ty * num_tiles_x + tx;
                    const bool current_tile_is_flat = (tile_idx < is_tile_flat.size()) ? is_tile_flat[tile_idx] : false;

                    for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx)
                    {
                        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx)
                        {
                            int block_local_r_start = bh_idx * actual_block_h;
                            int block_local_c_start = bw_idx * actual_block_w;
                            int current_block_h_dim = std::min(actual_block_h, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_block_w, tile_w - block_local_c_start);

                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0)
                            {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                continue;
                            }

                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            const cv::Mat current_block_to_match = current_tile_gray_for_mbm(current_block_roi_local);
                            if (current_block_to_match.empty())
                            {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                continue;
                            }

                            MotionMatching::BlockMatchResult mbm_result = MotionMatching::find_best_block_match_mad(
                                current_block_to_match, reference_tile_gray_for_mbm, block_local_r_start,
                                block_local_c_start, search_radius, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_th);

                            float confidence = 0.0f;
                            if (mbm_result.success)
                            {
                                // Gunakan parameter yang sudah diadaptasi
                                confidence = MotionMatching::calculate_match_confidence(
                                    mbm_result, global_estimated_noise_sigma, 
                                    adapted_motion_sensitivity, adapted_noise_offset_factor);

                                int global_r_pixel = r + block_local_r_start;
                                int global_c_pixel = c + block_local_c_start;

                                if (global_r_pixel >= 0 && global_r_pixel < guidance_confidence_map_final.rows &&
                                    global_c_pixel >= 0 && global_c_pixel < guidance_confidence_map_final.cols)
                                {
                                    float guidance_confidence = guidance_confidence_map_final.at<float>(global_r_pixel, global_c_pixel);
                                    confidence *= guidance_confidence;
                                }
                                else
                                {
                                    confidence = 0.0f;
                                }

                                if (confidence > 0.0f && !stability_map_mat.empty())
                                {
                                    if (global_r_pixel >= 0 && global_r_pixel < stability_map_mat.rows &&
                                        global_c_pixel >= 0 && global_c_pixel < stability_map_mat.cols)
                                    {
                                        float temporal_stability = stability_map_mat.at<float>(global_r_pixel, global_c_pixel);
                                        confidence *= temporal_stability;
                                    }
                                    else
                                    {
                                        confidence = 0.0f;
                                    }
                                }

                                if (current_tile_is_flat)
                                {
                                    confidence *= FLATNESS_CONFIDENCE_BOOST;
                                    confidence = std::min(confidence, 1.0f);
                                }
                            }
                            thread_block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                        }
                    }

                    // --- Bagian 5: Akumulasi Bobot dan Piksel ---
                    for (int y = 0; y < tile_h; ++y)
                    {
                        const float *current_tile_color_row = current_tile_for_accumulation.ptr<const float>(y);
                        const float *base_window_row = base_window_tile_mat.ptr<const float>(y);
                        int gy = r + y;
                        if (gy >= h_img)
                            continue;
                        float *global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                        float *global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);
                        for (int x = 0; x < tile_w; ++x)
                        {
                            int gx = c + x;
                            if (gx >= w_img)
                                continue;
                            int bh_idx = (actual_block_h > 0) ? std::min(y / actual_block_h, num_blocks_h - 1) : 0;
                            int bw_idx = (actual_block_w > 0) ? std::min(x / actual_block_w, num_blocks_w - 1) : 0;
                            float block_confidence = thread_block_confidences.at<float>(bh_idx, bw_idx);
                            float base_win_val = base_window_row[x];
                            float pixel_weight = base_win_val * block_confidence;
                            if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                            {
                                #pragma omp atomic update
                                global_weight_sum_row[gx] += pixel_weight;
                                int local_pixel_idx = x * channels;
                                int global_pixel_idx = gx * channels;
                                for (int ch = 0; ch < channels; ++ch)
                                {
                                    float weighted_pixel_value = current_tile_color_row[local_pixel_idx + ch] * pixel_weight;
                                    #pragma omp atomic update
                                    global_pixel_sum_row[global_pixel_idx + ch] += weighted_pixel_value;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // --- Fungsi normalize_accumulated_image_jit TIDAK BERUBAH ---
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