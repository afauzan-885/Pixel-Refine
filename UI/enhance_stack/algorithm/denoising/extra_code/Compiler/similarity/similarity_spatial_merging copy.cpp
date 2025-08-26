#include <cmath>
#include <vector>
#include <limits>
#include <iostream>
#include <chrono>
#include <string>
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

// class SimpleTimer
// {
// public:
//     SimpleTimer(const std::string &name)
//         : m_name(name), m_start(std::chrono::high_resolution_clock::now())
//     {
//     }

//     ~SimpleTimer()
//     {
//         auto end = std::chrono::high_resolution_clock::now();
//         auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - m_start);
//         std::cout << "[C++ Timer] " << m_name << ": "
//                   << duration.count() / 1000.0 << " ms" << std::endl;
//     }

// private:
//     std::string m_name;
//     std::chrono::time_point<std::chrono::high_resolution_clock> m_start;
// };

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

        // =========================================================================
        // === BAGIAN A: Pra-pemrosesan (PARALELISME GRANULAR dengan OMP TASK) ====
        // =========================================================================
        // SimpleTimer preprocess_timer("A. Preprocessing (Total)");

        cv::Mat current_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(reference_image_ptr));
        cv::Mat stability_map_mat;
        if (stability_map_ptr)
        {
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
        }

        cv::Mat current_image_gray_full, reference_image_gray_full;
        float global_estimated_noise_sigma;
        float adapted_motion_sensitivity, adapted_noise_offset_factor;
        std::vector<bool> is_tile_flat;

#pragma omp parallel
        {
#pragma omp single
            {
// --- TAHAP 1: Tugas Awal yang Bisa Berjalan Bersamaan ---
#pragma omp task
                {
                    // SimpleTimer cvt_current_timer("A1a. Grayscale Conversion (Current)");
                    cv::Mat temp_gray;
                    if (channels > 1)
                    {
                        cv::cvtColor(current_image_mat, temp_gray, cv::COLOR_BGR2GRAY);
                    }
                    else
                    {
                        current_image_mat.convertTo(temp_gray, CV_32F);
                    }
                    current_image_gray_full = temp_gray;
                }

#pragma omp task
                {
                    // SimpleTimer cvt_ref_timer("A1b. Grayscale Conversion (Reference)");
                    cv::Mat temp_gray;
                    if (channels > 1)
                    {
                        cv::cvtColor(reference_image_mat, temp_gray, cv::COLOR_BGR2GRAY);
                    }
                    else
                    {
                        reference_image_mat.convertTo(temp_gray, CV_32F);
                    }
                    reference_image_gray_full = temp_gray;
                }

// --- TAHAP 2: Sinkronisasi dan Tugas Dependen ---
// Menunggu TUGAS konversi grayscale selesai sebelum melanjutkan
#pragma omp taskwait

                // SimpleTimer noise_est_timer("A2. Noise Estimation");
                global_estimated_noise_sigma = 0.015f;
#ifdef TILE_NOISE_ESTIMATION_HPP
                if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
                    global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
#endif
                global_estimated_noise_sigma = std::max(0.001f, std::min(0.35f, global_estimated_noise_sigma));


                // --- TAHAP 3: Paralelkan Filter (Sekarang kita punya sigma) ---
#pragma omp task
                {
                    // SimpleTimer filter_current_timer("A3a. Filtering (Current)");
                    cv::Mat processed = current_image_gray_full.clone();

                    const float noise_activation_threshold = 0.07f;
                    const float median_filter_threshold = 0.14f;
                    if (global_estimated_noise_sigma > noise_activation_threshold)
                    {
                        if (global_estimated_noise_sigma >= median_filter_threshold)
                        {
                            cv::medianBlur(current_image_gray_full, processed, 5);
                        }
                        else
                        {
                            const float transition_range = median_filter_threshold - noise_activation_threshold;
                            float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                            if (denoising_strength_factor > 0.01f)
                            {
                                cv::bilateralFilter(current_image_gray_full, processed, 5, 50.0 / 255.0, 7.0);
                            }
                        }
                    }

                    float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
                    float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
                    float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);
                    if (clip_limit > 0.61f)
                    {
                        cv::Mat current_8u;
                        processed.convertTo(current_8u, CV_8U, 255.0);
                        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
                        clahe->apply(current_8u, current_8u);
                        current_8u.convertTo(processed, CV_32F, 1.0 / 255.0);
                    }
                    current_image_gray_full = processed;
                }

#pragma omp task
                {
                    // SimpleTimer filter_ref_timer("A3b. Filtering (Reference)");
                    cv::Mat processed = reference_image_gray_full.clone();

                    const float noise_activation_threshold = 0.07f;
                    const float median_filter_threshold = 0.14f;
                    if (global_estimated_noise_sigma > noise_activation_threshold)
                    {
                        if (global_estimated_noise_sigma >= median_filter_threshold)
                        {
                            cv::medianBlur(reference_image_gray_full, processed, 5);
                        }
                        else
                        {
                            const float transition_range = median_filter_threshold - noise_activation_threshold;
                            float denoising_strength_factor = (global_estimated_noise_sigma - noise_activation_threshold) / transition_range;
                            if (denoising_strength_factor > 0.01f)
                            {
                                cv::bilateralFilter(reference_image_gray_full, processed, 5, 50.0 / 255.0, 7.0);
                            }
                        }
                    }

                    float linear_strength_factor_clahe = 1.0f - std::min(global_estimated_noise_sigma / 0.12f, 1.0f);
                    float curved_strength_factor_clahe = std::pow(linear_strength_factor_clahe, 0.45f);
                    float clip_limit = 0.6f + (curved_strength_factor_clahe * 3.0f);
                    if (clip_limit > 0.61f)
                    {
                        cv::Mat ref_8u;
                        processed.convertTo(ref_8u, CV_8U, 255.0);
                        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
                        clahe->apply(ref_8u, ref_8u);
                        ref_8u.convertTo(processed, CV_32F, 1.0 / 255.0);
                    }
                    reference_image_gray_full = processed;
                }

// Menunggu SEMUA tugas yang diluncurkan di dalam 'single' ini selesai
#pragma omp taskwait
            } // akhir dari #pragma omp single
        } // akhir dari #pragma omp parallel

        // --- Perhitungan Akhir (Sangat Cepat, Serial) ---
        // 'global_estimated_noise_sigma' sudah tersedia dari tahap sebelumnya
        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / 0.1f, 1.0f);
        adapted_motion_sensitivity = motion_sensitivity * (1.0f - 0.50f * adaptation_factor);
        adapted_noise_offset_factor = noise_offset_factor * (1.0f + 0.95f * adaptation_factor);

        // =================================================================================
        // === BAGIAN B: ANALISIS SKALA KASAR (OPTIMASI BARU DENGAN GRID + INTERPOLASI) ===
        // =================================================================================
        // SimpleTimer pyramid_timer("B. Multi-Scale Pyramid Generation");

        const int tile_h_fine = tile_h;
        const int tile_w_fine = tile_w;

        // --- Tentukan jumlah level piramida ---
        int max_level = 0;
        int temp_h = h_img, temp_w = w_img;
        while (temp_h >= tile_h_fine * 4 && temp_w >= tile_w_fine * 4) // Perlu margin lebih besar untuk grid
        {
            temp_h /= 2;
            temp_w /= 2;
            max_level++;
        }
        const int num_pyramid_levels = std::min(max_level, 2) + 1;

        // --- Bangun piramida gambar ---
        std::vector<cv::Mat> current_pyramid, reference_pyramid;
        #pragma omp parallel
        {
            #pragma omp single
            {
                #pragma omp task
                {
                    current_pyramid.reserve(num_pyramid_levels);
                    current_pyramid.push_back(current_image_gray_full);
                    for (int i = 0; i < num_pyramid_levels - 1; ++i) {
                        cv::Mat next_current;
                        cv::pyrDown(current_pyramid.back(), next_current);
                        current_pyramid.push_back(next_current);
                    }
                }
                #pragma omp task
                {
                    reference_pyramid.reserve(num_pyramid_levels);
                    reference_pyramid.push_back(reference_image_gray_full);
                    for (int i = 0; i < num_pyramid_levels - 1; ++i) {
                        cv::Mat next_ref;
                        cv::pyrDown(reference_pyramid.back(), next_ref);
                        reference_pyramid.push_back(next_ref);
                    }
                }
                #pragma omp taskwait
            }
        }

        std::reverse(current_pyramid.begin(), current_pyramid.end());
        std::reverse(reference_pyramid.begin(), reference_pyramid.end());

        // --- Peta panduan dimulai dari ukuran level terkecil ---
        cv::Mat guidance_map = cv::Mat(current_pyramid[0].size(), CV_32FC1, cv::Scalar(1.0f));

        // --- Loop dari skala paling kasar ke yang lebih halus ---
        for (int level = 0; level < num_pyramid_levels - 1; ++level)
        {
            const cv::Mat &current_img_level = current_pyramid[level];
            const cv::Mat &ref_img_level = reference_pyramid[level];

            if (level > 0) {
                cv::resize(guidance_map, guidance_map, current_img_level.size(), 0, 0, cv::INTER_LINEAR);
            }

            const int num_tiles_h = current_img_level.rows / tile_h_fine;
            const int num_tiles_w = current_img_level.cols / tile_w_fine;
            if (num_tiles_h == 0 || num_tiles_w == 0) continue;

            // --- OPTIMASI 2: Gunakan Integral Image untuk mean lookup super cepat ---
            cv::Mat guidance_map_integral;
            // Gunakan CV_64F (double) untuk menghindari overflow/masalah presisi saat menjumlahkan
            cv::integral(guidance_map, guidance_map_integral, CV_64F);

            cv::Mat confidence_grid(num_tiles_h, num_tiles_w, CV_32FC1);

            #pragma omp parallel for schedule(dynamic)
            for (int r_tile = 0; r_tile < num_tiles_h; ++r_tile)
            {
                MotionMatching::MBMBuffers mbm_buffers;
                // ... inisialisasi buffer ...
                if (tile_h_fine > 0 && tile_w_fine > 0) {
                    mbm_buffers.diff_workspace.create(tile_h_fine, tile_w_fine, CV_32FC1);
                    mbm_buffers.grad_x.create(tile_h_fine, tile_w_fine, CV_32F);
                    mbm_buffers.grad_y.create(tile_h_fine, tile_w_fine, CV_32F);
                    mbm_buffers.grad_mag_current.create(tile_h_fine, tile_w_fine, CV_32FC1);
                }

                for (int c_tile = 0; c_tile < num_tiles_w; ++c_tile)
                {
                    cv::Rect roi(c_tile * tile_w_fine, r_tile * tile_h_fine, tile_w_fine, tile_h_fine);
                    
                    MotionMatching::TileMatchResult res = MotionMatching::calculate_tile_similarity(
                        current_img_level(roi), ref_img_level(roi),
                        global_estimated_noise_sigma, 
                        GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers);

                    float confidence_level = res.success ? MotionMatching::calculate_match_confidence(
                        res, global_estimated_noise_sigma, adapted_motion_sensitivity, adapted_noise_offset_factor) : 0.0f;
                    
                    // --- OPTIMASI 2 (Lanjutan): Ganti cv::mean dengan lookup Integral Image (O(1)) ---
                    const int x1 = roi.x;
                    const int y1 = roi.y;
                    const int x2 = roi.x + roi.width;
                    const int y2 = roi.y + roi.height;

                    // Akses 4 titik pada integral image untuk mendapatkan jumlah area
                    const double sum = guidance_map_integral.at<double>(y2, x2) 
                                    - guidance_map_integral.at<double>(y2, x1) 
                                    - guidance_map_integral.at<double>(y1, x2) 
                                    + guidance_map_integral.at<double>(y1, x1);

                    const float guidance_confidence = static_cast<float>(sum / (roi.width * roi.height));
                    
                    confidence_grid.at<float>(r_tile, c_tile) = confidence_level * guidance_confidence;
                }
            }

            cv::resize(confidence_grid, guidance_map, current_img_level.size(), 0, 0, cv::INTER_LINEAR);
        }

        // --- Upscale peta panduan final ke resolusi penuh (tidak berubah) ---
        if (!guidance_map.empty() && guidance_map.size() != current_image_gray_full.size()) {
            cv::resize(guidance_map, guidance_map, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
        } else if(guidance_map.empty()) {
            guidance_map = cv::Mat(h_img, w_img, CV_32FC1, cv::Scalar(1.0f));
        }

        // =================================================================================
        // === TAHAP 2: ANALISIS SKALA HALUS & AKUMULASI FINAL (OPTIMASI UNTUK KECEPATAN)
        // =================================================================================
        // SimpleTimer accumulation_timer("C. Fine Scale Analysis & Accumulation");

        cv::Mat final_image_sum_mat(h_img, w_img, CV_32FC(channels), final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);

        // Inisialisasi tetap bisa diparalelkan
        #pragma omp parallel for
        for (int i = 0; i < h_img * w_img * channels; ++i) final_image_sum_ptr[i] = 0.0f;
        #pragma omp parallel for
        for (int i = 0; i < h_img * w_img; ++i) weight_map_sum_ptr[i] = 0.0f;

        #pragma omp parallel
        {
            // === Variabel Lokal per-Thread ===
            // Kita kembalikan buffer lokal kecil ini.
            // Ini penting agar setiap thread bisa bekerja tanpa mengganggu yang lain.
            cv::Mat local_weighted_tile(tile_h_fine, tile_w_fine, CV_32FC(channels));
            cv::Mat local_weight_tile(tile_h_fine, tile_w_fine, CV_32FC1);

            MotionMatching::MBMBuffers mbm_buffers_fine;
            if (tile_h_fine > 0 && tile_w_fine > 0) {
                mbm_buffers_fine.diff_workspace.create(tile_h_fine, tile_w_fine, CV_32FC1);
                mbm_buffers_fine.grad_x.create(tile_h_fine, tile_w_fine, CV_32F);
                mbm_buffers_fine.grad_y.create(tile_h_fine, tile_w_fine, CV_32F);
                mbm_buffers_fine.grad_mag_current.create(tile_h_fine, tile_w_fine, CV_32FC1);
            }
            
            #pragma omp for collapse(2) schedule(dynamic)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r + tile_h_fine > h_img || c + tile_w_fine > w_img) continue;

                    cv::Rect tile_roi(c, r, tile_w_fine, tile_h_fine);

                    // Perhitungan confidence (tetap sama)
                    MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_similarity(
                        current_image_gray_full(tile_roi), reference_image_gray_full(tile_roi),
                        global_estimated_noise_sigma, 
                        GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_fine
                    );

                    float confidence_fine = mbm_result.success ? MotionMatching::calculate_match_confidence(
                        mbm_result, global_estimated_noise_sigma, 
                        adapted_motion_sensitivity, adapted_noise_offset_factor) : 0.0f;
                    
                    float guidance_confidence = static_cast<float>(cv::mean(guidance_map(tile_roi))[0]);
                    float final_confidence = confidence_fine * guidance_confidence;

                    if (!stability_map_mat.empty()) {
                        final_confidence *= static_cast<float>(cv::mean(stability_map_mat(tile_roi))[0]);
                    }
                    
                    if (final_confidence < 1e-5f) continue;
                    
                    // --- LANGKAH 1: Hitung & Simpan ke Buffer LOKAL (Sangat Cepat, Tanpa Kunci/Lock) ---
                    const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h_fine, tile_w_fine, CV_32FC1, const_cast<float *>(base_window_ptr));
                    
                    // Operasi perkalian ini sekarang mengisi buffer lokal milik thread, bukan global.
                    cv::multiply(base_window_tile_mat, final_confidence, local_weight_tile);

                    if (channels > 1) {
                        cv::Mat weighted_mask_color;
                        std::vector<cv::Mat> mask_channels(channels, local_weight_tile);
                        cv::merge(mask_channels, weighted_mask_color);
                        cv::multiply(current_tile_for_accumulation, weighted_mask_color, local_weighted_tile);
                    } else {
                        cv::multiply(current_tile_for_accumulation, local_weight_tile, local_weighted_tile);
                    }

                    // --- LANGKAH 2: Akumulasi ke Buffer GLOBAL dalam Critical Section (Jarang Terjadi) ---
                    // Hanya satu thread yang bisa masuk ke sini pada satu waktu,
                    // tapi operasinya sangat cepat (menambahkan seluruh blok memori).
                    #pragma omp critical
                    {
                        cv::add(final_image_sum_mat(tile_roi), local_weighted_tile, final_image_sum_mat(tile_roi));
                        cv::add(weight_map_sum_mat(tile_roi), local_weight_tile, weight_map_sum_mat(tile_roi));
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