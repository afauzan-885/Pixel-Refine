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
        float noise_offset_factor)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_sum_ptr || !weight_map_sum_ptr)
        {
            return;
        }

        // --- Langkah 0: Persiapan Awal (Serial & Cepat) ---
        cv::Mat current_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(reference_image_ptr));
        cv::Mat stability_map_mat;
        if (stability_map_ptr) {
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
        }
        
        cv::Mat current_image_gray_full, reference_image_gray_full;
        if (channels > 1) {
            cv::cvtColor(current_image_mat, current_image_gray_full, cv::COLOR_BGR2GRAY);
            cv::cvtColor(reference_image_mat, reference_image_gray_full, cv::COLOR_BGR2GRAY);
        } else {
            current_image_mat.convertTo(current_image_gray_full, CV_32F);
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }

        float global_estimated_noise_sigma = 0.015f;
        #ifdef TILE_NOISE_ESTIMATION_HPP
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
        #endif
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / 0.1f, 1.0f);
        float adapted_motion_sensitivity = motion_sensitivity * (1.0f - 0.65f * adaptation_factor);
        float adapted_noise_offset_factor = noise_offset_factor * (1.0f + 0.65f * adaptation_factor);

        // --- Logika CLAHE dan Denoising (Lengkap dan Disertakan Kembali) ---
        cv::Mat current_image_gray_processed = current_image_gray_full.clone();
        cv::Mat reference_image_gray_processed = reference_image_gray_full.clone();

        // --- LANGKAH 1: DENOISING (Dilakukan terlebih dahulu) ---
        const float noise_activation_threshold = 0.07f;
        const float median_filter_threshold = 0.14f;
        if (global_estimated_noise_sigma > noise_activation_threshold)
        {
            if (global_estimated_noise_sigma >= median_filter_threshold)
            {
                // Gunakan filter yang lebih kuat untuk noise tinggi
                cv::medianBlur(current_image_gray_full, current_image_gray_processed, 5);
                cv::medianBlur(reference_image_gray_full, reference_image_gray_processed, 5);
            }
            else
            {
                // Gunakan filter yang lebih lembut untuk noise sedang
                const float transition_range = median_filter_threshold - noise_activation_threshold;
                float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                denoising_strength_factor = std::min(1.0f, std::max(0.0f, denoising_strength_factor));
                if (denoising_strength_factor > 0.01f)
                {
                    // Perhatikan: filter diterapkan pada gambar ASLI, hasilnya disimpan di 'processed'
                    cv::bilateralFilter(current_image_gray_full, current_image_gray_processed, 5, 50.0 / 255.0, 7.0);
                    cv::bilateralFilter(reference_image_gray_full, reference_image_gray_processed, 5, 50.0 / 255.0, 7.0);
                }
            }
        }

        // --- LANGKAH 2: CLAHE (Dilakukan pada gambar yang sudah di-denoise) ---
        float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
        float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
        float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);
        if (clip_limit > 0.61f)
        {
            cv::Mat current_8u, ref_8u;
            // Konversi gambar yang SUDAH di-denoise ke 8-bit
            current_image_gray_processed.convertTo(current_8u, CV_8U, 255.0);
            reference_image_gray_processed.convertTo(ref_8u, CV_8U, 255.0);

            cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));

            // Terapkan CLAHE dan simpan hasilnya kembali ke buffer 'processed'
            clahe->apply(current_8u, current_8u); 
            clahe->apply(ref_8u, ref_8u);
            
            // Konversi kembali ke 32-bit float untuk pemrosesan selanjutnya
            current_8u.convertTo(current_image_gray_processed, CV_32F, 1.0 / 255.0);
            ref_8u.convertTo(reference_image_gray_processed, CV_32F, 1.0 / 255.0);
        }

        // --- Akhir dari Logika Denoising dan CLAHE ---
        current_image_gray_full = current_image_gray_processed;
        reference_image_gray_full = reference_image_gray_processed;
        
        std::vector<bool> is_tile_flat;
        std::vector<cv::Mat> ref_channels_for_flat;
        if (channels > 1) { cv::split(reference_image_mat, ref_channels_for_flat); } 
        else { ref_channels_for_flat.push_back(reference_image_mat); }
        TextureAnalysis::detect_flat_tiles(ref_channels_for_flat, tile_h, tile_w, channels, FLATNESS_VARIANCE_THRESHOLD, is_tile_flat);

        // Inisialisasi buffer output
        cv::Mat final_image_sum_mat(h_img, w_img, CV_32FC(channels), final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        final_image_sum_mat.setTo(0.0f);
        weight_map_sum_mat.setTo(0.0f);

        // --- Langkah 2: Loop Akumulasi Paralel dengan Metode Hibrida ---
        #pragma omp parallel
        {
            // --- Alokasi buffer LOKAL dan KECIL per-thread. Efisien memori! ---
            cv::Mat local_weighted_tile(tile_h, tile_w, CV_32FC(channels));
            cv::Mat local_weight_tile(tile_h, tile_w, CV_32FC1);
            MotionMatching::MBMBuffers mbm_buffers_th;
            if (tile_h > 0 && tile_w > 0) {
                mbm_buffers_th.diff_workspace.create(tile_h, tile_w, CV_32FC1);
                mbm_buffers_th.grad_x.create(tile_h, tile_w, CV_32F);
                mbm_buffers_th.grad_y.create(tile_h, tile_w, CV_32F);
                mbm_buffers_th.grad_mag_current.create(tile_h, tile_w, CV_32FC1);
            }
            const int num_tiles_x = (w_img > 0 && tile_w > 0) ? (w_img + tile_w - 1) / tile_w : 0;
            
            #pragma omp for collapse(2) schedule(dynamic)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r + tile_h > h_img || c + tile_w > w_img) continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);

                    // --- Kalkulasi similarity (intensif komputasi) ---
                    const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi);
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

                        if (confidence > 0.0f && !stability_map_mat.empty()) {
                            confidence *= static_cast<float>(cv::mean(stability_map_mat(tile_roi))[0]);
                        }
                        
                        const int tile_idx = (r / tile_h) * num_tiles_x + (c / tile_w);
                        if (tile_idx < is_tile_flat.size() && is_tile_flat[tile_idx]) {
                            confidence = std::min(confidence * FLATNESS_CONFIDENCE_BOOST, 1.0f);
                        }
                    }
                    
                    if (confidence < 1e-5f) continue;
                    
                    // --- Kalkulasi bobot dilakukan di buffer LOKAL (Sangat Cepat) ---
                    const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));
                    
                    cv::multiply(base_window_tile_mat, confidence, local_weight_tile);
                    if (channels > 1) {
                        cv::Mat weighted_mask_color;
                        std::vector<cv::Mat> mask_channels(channels, local_weight_tile);
                        cv::merge(mask_channels, weighted_mask_color);
                        cv::multiply(current_tile_for_accumulation, weighted_mask_color, local_weighted_tile);
                    } else {
                        cv::multiply(current_tile_for_accumulation, local_weight_tile, local_weighted_tile);
                    }

                    // --- Penggabungan ke Buffer Global menggunakan ATOMIC (Bagian Kritis) ---
                    // Pointer ke ROI di buffer global
                    float* final_sum_roi_ptr = final_image_sum_mat.ptr<float>(r, c);
                    float* weight_sum_roi_ptr = weight_map_sum_mat.ptr<float>(r, c);
                    
                    // Pointer ke data di buffer lokal
                    const float* local_weighted_ptr = local_weighted_tile.ptr<float>(0);
                    const float* local_weight_ptr = local_weight_tile.ptr<float>(0);

                    for (int tile_r = 0; tile_r < tile_h; ++tile_r) {
                        for (int tile_c = 0; tile_c < tile_w; ++tile_c) {
                            int local_idx = tile_r * tile_w + tile_c;
                            int global_row_offset = tile_r * weight_map_sum_mat.cols;

                            // Atomic add untuk weight map
                            float weight_val = local_weight_ptr[local_idx];
                            if (weight_val > 1e-8f) {
                                #pragma omp atomic
                                weight_sum_roi_ptr[global_row_offset + tile_c] += weight_val;
                            }
                            
                            // Atomic add untuk image channels
                            for (int ch = 0; ch < channels; ++ch) {
                                float pixel_val = local_weighted_ptr[local_idx * channels + ch];
                                if (std::abs(pixel_val) > 1e-8f) {
                                    #pragma omp atomic
                                    final_sum_roi_ptr[(global_row_offset + tile_c) * channels + ch] += pixel_val;
                                }
                            }
                        }
                    }
                }
            } // --- Akhir dari #pragma omp for ---
        } // --- Akhir dari #pragma omp parallel ---
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