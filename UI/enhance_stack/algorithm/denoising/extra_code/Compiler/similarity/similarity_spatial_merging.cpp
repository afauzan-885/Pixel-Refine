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

// Namespace dari kode asli Anda
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

namespace // Anonymous namespace untuk fungsi helper
{
    static cv::Mat generate_pyramid_confidence_map(
        const cv::Mat &current_image_gray_full,
        const cv::Mat &reference_image_gray_full,
        int tile_h, int tile_w, int search_radius,
        float motion_sensitivity, float noise_offset_factor, float global_estimated_noise_sigma)
    {
        using namespace MotionMetricsConfig;
        using namespace MotionMatching;

        // --- LANGKAH 1: Pra-Filter Agresif ---
        cv::Mat current_for_pyramid, reference_for_pyramid;
        const float extreme_noise_threshold = 0.15f; 
        if (global_estimated_noise_sigma >= extreme_noise_threshold) {
            cv::medianBlur(current_image_gray_full, current_for_pyramid, 5);
            cv::medianBlur(reference_image_gray_full, reference_for_pyramid, 5);
        } else {
            cv::GaussianBlur(current_image_gray_full, current_for_pyramid, cv::Size(5, 5), 1.0);
            cv::GaussianBlur(reference_image_gray_full, reference_for_pyramid, cv::Size(5, 5), 1.0);
        }

        // --- LANGKAH 2: Buat Piramida Gambar ---
        cv::Mat current_h_img, ref_h_img; // Nama diubah agar tidak bentrok
        cv::pyrDown(current_for_pyramid, current_h_img);
        cv::pyrDown(reference_for_pyramid, ref_h_img);
        cv::Mat current_q_img, ref_q_img; // Nama diubah agar tidak bentrok
        cv::pyrDown(current_h_img, current_q_img);
        cv::pyrDown(ref_h_img, ref_q_img);

        // --- LANGKAH 3: Analisis Level 1/4 ---
        int tile_h_q = std::max(1, tile_h / 4);
        int tile_w_q = std::max(1, tile_w / 4);
        int search_radius_q = search_radius > 0 ? std::max(1, search_radius / 4) : 0;
        cv::Mat confidence_map_q(current_q_img.size(), CV_32FC1);

        #pragma omp parallel for schedule(static)
        for (int r = 0; r < current_q_img.rows; r += tile_h_q) {
            MBMBuffers buffers;
            for (int c = 0; c < current_q_img.cols; c += tile_w_q) {
                // Gunakan nama variabel yang unik
                int block_w = std::min(tile_w_q, current_q_img.cols - c);
                int block_h = std::min(tile_h_q, current_q_img.rows - r);
                if (block_w <= 0 || block_h <= 0) continue;

                buffers.diff_workspace.create(block_h, block_w, CV_32FC1);
                buffers.grad_x.create(block_h, block_w, CV_32F);
                buffers.grad_y.create(block_h, block_w, CV_32F);
                buffers.grad_mag_current.create(block_h, block_w, CV_32FC1);

                cv::Rect roi(c, r, block_w, block_h);
                BlockMatchResult res = find_best_block_match_mad(current_q_img(roi), ref_q_img, r, c, search_radius_q, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers);
                float conf = res.success ? calculate_match_confidence(res, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
                confidence_map_q(roi).setTo(cv::Scalar(conf));
            }
        }

        // --- LANGKAH 4: Analisis Level 1/2 ---
        cv::Mat guidance_for_h;
        cv::resize(confidence_map_q, guidance_for_h, current_h_img.size(), 0, 0, cv::INTER_LINEAR);
        
        int tile_h_h = std::max(1, tile_h / 2);
        int tile_w_h = std::max(1, tile_w / 2);
        int search_radius_h = search_radius > 0 ? std::max(1, search_radius / 2) : 0;
        cv::Mat confidence_map_h(current_h_img.size(), CV_32FC1);

        #pragma omp parallel for schedule(static)
        for (int r = 0; r < current_h_img.rows; r += tile_h_h) {
            MBMBuffers buffers;
            for (int c = 0; c < current_h_img.cols; c += tile_w_h) {
                // Gunakan nama variabel yang unik
                int block_w = std::min(tile_w_h, current_h_img.cols - c);
                int block_h = std::min(tile_h_h, current_h_img.rows - r);
                if (block_w <= 0 || block_h <= 0) continue;

                buffers.diff_workspace.create(block_h, block_w, CV_32FC1);
                buffers.grad_x.create(block_h, block_w, CV_32F);
                buffers.grad_y.create(block_h, block_w, CV_32F);
                buffers.grad_mag_current.create(block_h, block_w, CV_32FC1);

                cv::Rect roi(c, r, block_w, block_h);
                BlockMatchResult res = find_best_block_match_mad(current_h_img(roi), ref_h_img, r, c, search_radius_h, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers);
                float local_conf = res.success ? calculate_match_confidence(res, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
                
                cv::Scalar mean_guidance_scalar = cv::mean(guidance_for_h(roi));
                float guidance_conf = static_cast<float>(mean_guidance_scalar[0]);
                
                confidence_map_h(roi).setTo(cv::Scalar(local_conf * guidance_conf));
            }
        }

        // --- LANGKAH 5: Analisis Level 1/1 ---
        cv::Mat guidance_for_full;
        cv::resize(confidence_map_h, guidance_for_full, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
        
        const cv::Mat& current_to_match_full = current_image_gray_full;
        const cv::Mat& ref_to_match_full = reference_image_gray_full;
        
        cv::Mat confidence_map_final(current_to_match_full.size(), CV_32FC1);

        #pragma omp parallel for schedule(static)
        for (int r = 0; r < current_to_match_full.rows; r += tile_h) {
            MBMBuffers buffers;
            for (int c = 0; c < current_to_match_full.cols; c += tile_w) {
                // Gunakan nama variabel yang unik
                int block_w = std::min(tile_w, current_to_match_full.cols - c);
                int block_h = std::min(tile_h, current_to_match_full.rows - r);
                if (block_w <= 0 || block_h <= 0) continue;
                
                buffers.diff_workspace.create(block_h, block_w, CV_32FC1);
                buffers.grad_x.create(block_h, block_w, CV_32F);
                buffers.grad_y.create(block_h, block_w, CV_32F);
                buffers.grad_mag_current.create(block_h, block_w, CV_32FC1);

                cv::Rect roi(c, r, block_w, block_h);
                
                BlockMatchResult res = find_best_block_match_mad(
                    current_to_match_full(roi), ref_to_match_full, r, c, search_radius,
                    GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers
                );
                float local_conf = res.success ? calculate_match_confidence(res, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
                
                cv::Scalar mean_guidance_scalar = cv::mean(guidance_for_full(roi));
                float guidance_conf = static_cast<float>(mean_guidance_scalar[0]);
                
                confidence_map_final(roi).setTo(cv::Scalar(local_conf * guidance_conf));
            }
        }
        return confidence_map_final;
    }
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
        cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        cv::Mat stability_map_mat;
        if (stability_map_ptr)
        {
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
        }
        
        // --- Normalisasi Pencahayaan Global ---
        if (channels > 1)
        {
            std::vector<cv::Mat> current_channels, ref_channels;
            cv::split(current_image_mat, current_channels);
            cv::split(reference_image_mat, ref_channels);
            for (int i = 0; i < channels; ++i)
            {
                cv::Scalar mean_curr, stddev_curr, mean_ref, stddev_ref;
                cv::meanStdDev(current_channels[i], mean_curr, stddev_curr);
                cv::meanStdDev(ref_channels[i], mean_ref, stddev_ref);
                if (stddev_curr[0] > 1e-5)
                {
                    double alpha = stddev_ref[0] / stddev_curr[0];
                    double beta = mean_ref[0] - (mean_curr[0] * alpha);
                    current_channels[i].convertTo(current_channels[i], CV_32F, alpha, beta);
                }
            }
            cv::merge(current_channels, current_image_mat);
        }
        else
        {
            cv::Scalar mean_curr, stddev_curr, mean_ref, stddev_ref;
            cv::meanStdDev(current_image_mat, mean_curr, stddev_curr);
            cv::meanStdDev(reference_image_mat, mean_ref, stddev_ref);
            if (stddev_curr[0] > 1e-5)
            {
                double alpha = stddev_ref[0] / stddev_curr[0];
                double beta = mean_ref[0] - (mean_curr[0] * alpha);
                current_image_mat.convertTo(current_image_mat, CV_32F, alpha, beta);
            }
        }
        
        // --- Buffer Pra-Pemrosesan ---
        cv::Mat current_image_gray_full, reference_image_gray_full;
        
        // --- Konversi ke Grayscale ---
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

        // --- Estimasi Noise ---
        float global_estimated_noise_sigma = 0.015f;
#ifdef TILE_NOISE_ESTIMATION_HPP
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
        {
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
        }
#endif
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        // --- Adaptasi Parameter Sensitivitas ---
        const float base_motion_sensitivity = motion_sensitivity;
        const float base_noise_offset_factor = noise_offset_factor;
        const float adaptation_range = 0.65f;
        const float noise_threshold_for_adaptation = 0.1f;
        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / noise_threshold_for_adaptation, 1.0f);
        float adapted_motion_sensitivity = base_motion_sensitivity * (1.0f - adaptation_range * adaptation_factor);
        float adapted_noise_offset_factor = base_noise_offset_factor * (1.0f + adaptation_range * adaptation_factor);
        
        // --- Rantai Pra-Pemrosesan (CLAHE & Denoising) ---
        // (Salinan bersih dari gambar grayscale sebelum modifikasi)
        cv::Mat current_image_gray_full_clahe = current_image_gray_full.clone();
        cv::Mat reference_image_gray_full_clahe = reference_image_gray_full.clone();

        float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
        float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
        float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);
        if (clip_limit > 0.61f)
        {
            cv::Mat current_8u, ref_8u;
            current_image_gray_full.convertTo(current_8u, CV_8U, 255.0);
            reference_image_gray_full.convertTo(ref_8u, CV_8U, 255.0);
            cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
            clahe->apply(current_8u, current_image_gray_full_clahe); // Tulis hasil ke buffer _clahe
            clahe->apply(ref_8u, reference_image_gray_full_clahe);
            current_image_gray_full_clahe.convertTo(current_image_gray_full_clahe, CV_32F, 1.0 / 255.0);
            reference_image_gray_full_clahe.convertTo(reference_image_gray_full_clahe, CV_32F, 1.0 / 255.0);
        }
        
        const float noise_activation_threshold = 0.07f;
        const float median_filter_threshold = 0.14f;
        if (global_estimated_noise_sigma > noise_activation_threshold)
        {
            if (global_estimated_noise_sigma >= median_filter_threshold)
            {
                cv::medianBlur(current_image_gray_full_clahe, current_image_gray_full, 5);
                cv::medianBlur(reference_image_gray_full_clahe, reference_image_gray_full, 5);
            }
            else
            {
                const float transition_range = median_filter_threshold - noise_activation_threshold;
                float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                denoising_strength_factor = std::min(1.0f, std::max(0.0f, denoising_strength_factor));
                if (denoising_strength_factor > 0.01f)
                {
                    int kernel_size = 5; 
                    double sigma_color = 5.0 + (denoising_strength_factor * 45.0);
                    double sigma_space = 7.0;
                    cv::bilateralFilter(current_image_gray_full_clahe, current_image_gray_full, kernel_size, sigma_color / 255.0, sigma_space);
                    cv::bilateralFilter(reference_image_gray_full_clahe, reference_image_gray_full, kernel_size, sigma_color / 255.0, sigma_space);
                }
            }
        } else {
             current_image_gray_full = current_image_gray_full_clahe;
             reference_image_gray_full = reference_image_gray_full_clahe;
        }

        // --- Deteksi Area Datar ---
        std::vector<bool> is_tile_flat;
        std::vector<cv::Mat> ref_channels_for_flat_detection;
        if (channels > 1) {
            cv::split(reference_image_mat, ref_channels_for_flat_detection);
        } else {
            ref_channels_for_flat_detection.push_back(reference_image_mat);
        }
        TextureAnalysis::detect_flat_tiles(ref_channels_for_flat_detection, tile_h, tile_w, channels, FLATNESS_VARIANCE_THRESHOLD, is_tile_flat);

        // --- Hasilkan Peta Kepercayaan Penuh dalam Satu Panggilan ---
        cv::Mat final_confidence_map = generate_pyramid_confidence_map(
            current_image_gray_full, reference_image_gray_full,
            tile_h, tile_w, search_radius,
            adapted_motion_sensitivity, adapted_noise_offset_factor,
            global_estimated_noise_sigma);

        // --- Loop Utama yang Ringan (Hanya Akumulasi) ---
        #pragma omp parallel for collapse(2) schedule(static)
        for (int i = 0; i < num_row_starts; i++)
        {
            for (int j = 0; j < num_col_starts; j++)
            {
                int r = row_starts[i];
                int c = col_starts[j];
                if (r < 0 || c < 0 || (r + tile_h) > h_img || (c + tile_w) > w_img || tile_h <= 0 || tile_w <= 0)
                    continue;

                cv::Rect tile_roi(c, r, tile_w, tile_h);

                cv::Mat confidence_tile = final_confidence_map(tile_roi).clone();
                
                if (!stability_map_mat.empty()) {
                    cv::multiply(confidence_tile, stability_map_mat(tile_roi), confidence_tile);
                }
                
                const int num_tiles_x = (w_img > 0 && tile_w > 0) ? w_img / tile_w : 0;
                const int tx = c / tile_w;
                const int ty = r / tile_h;
                const int tile_idx = ty * num_tiles_x + tx;
                const bool current_tile_is_flat = (tile_idx < is_tile_flat.size()) ? is_tile_flat[tile_idx] : false;

                if (current_tile_is_flat) {
                    confidence_tile *= FLATNESS_CONFIDENCE_BOOST;
                    cv::min(confidence_tile, 1.0, confidence_tile);
                }

                const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                for (int y = 0; y < tile_roi.height; ++y)
                {
                    const float* color_row = current_tile_for_accumulation.ptr<const float>(y);
                    const float* base_win_row = base_window_tile_mat.ptr<const float>(y);
                    const float* conf_row = confidence_tile.ptr<const float>(y);
                    int gy = r + y;

                    float* global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                    float* global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);

                    for (int x = 0; x < tile_roi.width; ++x)
                    {
                        int gx = c + x;
                        float pixel_weight = base_win_row[x] * conf_row[x];
                        
                        if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                        {
                            #pragma omp atomic update
                            global_weight_sum_row[gx] += pixel_weight;
                            
                            int local_pixel_idx = x * channels;
                            int global_pixel_idx = gx * channels;
                            for (int ch = 0; ch < channels; ++ch)
                            {
                                float weighted_pixel_value = color_row[local_pixel_idx + ch] * pixel_weight;
                                #pragma omp atomic update
                                global_pixel_sum_row[global_pixel_idx + ch] += weighted_pixel_value;
                            }
                        }
                    }
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