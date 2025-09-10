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

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
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
    const float *reference_image_processed_ptr,
    const float *base_window_ptr,
    const float *stability_map_ptr,
    const int *row_starts, const int *col_starts,
    int num_row_starts, int num_col_starts,
    int tile_h, int tile_w,
    int h_img, int w_img, int channels,
    float motion_sensitivity,
    float noise_offset_factor,
    float precomputed_ref_noise_sigma)
{
    using namespace MotionMetricsConfig;

    if (!final_image_sum_ptr || !weight_map_sum_ptr)
        return;

    // =========================================================================
    // === BAGIAN A: Pra-pemrosesan ==
    // =========================================================================

    cv::Mat current_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(current_image_ptr));
    const cv::Mat reference_image_gray_full(h_img, w_img, CV_32FC1, const_cast<float *>(reference_image_processed_ptr));

    cv::Mat stability_map_mat;
    if (stability_map_ptr)
    {
        stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, const_cast<float *>(stability_map_ptr));
    }

    cv::Mat current_image_gray_full;
    float adapted_motion_sensitivity, adapted_noise_offset_factor;

    // --- LANGKAH 1: Konversi Warna ---
    if (channels > 1)
    {
        cv::cvtColor(current_image_mat, current_image_gray_full, cv::COLOR_BGR2GRAY);
    }
    else
    {
        current_image_mat.convertTo(current_image_gray_full, CV_32F);
    }

    // --- LANGKAH 2: Filtering ---
    float global_estimated_noise_sigma = precomputed_ref_noise_sigma;

    const float noise_activation_threshold = 0.07f;
    if (global_estimated_noise_sigma > noise_activation_threshold)
    {
        const float median_filter_threshold = 0.14f;
        if (global_estimated_noise_sigma >= median_filter_threshold)
        {
            cv::medianBlur(current_image_gray_full, current_image_gray_full, 5);
        }
        else
        {
            cv::Mat temp_filtered;
            cv::bilateralFilter(current_image_gray_full, temp_filtered, 5, 50.0 / 255.0, 7.0);
            current_image_gray_full = temp_filtered;
        }
    }

    // === LOGIKA PRE-PROSESING YANG TELAH DI-ENHANCE (SEKARANG MENJADI SATU-SATUNYA PROSES) ===
    
    // --- (BARU) LANGKAH 1.5: Kalkulasi Faktor Agresi Berdasarkan Kontras ---
    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(current_image_gray_full, mean_val, stddev_val);
    float contrast_metric = static_cast<float>(stddev_val[0]);

    const float low_contrast_thresh = 0.12f;
    const float high_contrast_thresh = 0.20f;

    float aggression_factor = 1.0f - std::max(0.0f, std::min(1.0f, 
        (contrast_metric - low_contrast_thresh) / (high_contrast_thresh - low_contrast_thresh)));


    // --- LANGKAH 2: Peningkatan Mikro-Kontras (DIUBAH) ---
    const float micro_contrast_noise_threshold = 0.05f;
    float micro_contrast_strength = 1.0f - std::min(1.0f, global_estimated_noise_sigma / micro_contrast_noise_threshold);

    if (micro_contrast_strength > 0.01f)
    {
        cv::Mat blurred_image;
        cv::GaussianBlur(current_image_gray_full, blurred_image, cv::Size(0, 0), 1.0);
        
        float base_amount = micro_contrast_strength * 0.8f;
        float boosted_amount = base_amount * (1.0f + 0.5f * aggression_factor);

        cv::addWeighted(current_image_gray_full, 1.0f + boosted_amount, blurred_image, -boosted_amount, 0, current_image_gray_full);
        
        cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
        cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);
    }

    // --- (BARU & DIUBAH) LANGKAH 3: Peningkatan Kontras Lokal Adaptif (CLAHE) ---
    float linear_strength = 1.0f - std::min(1.0f, global_estimated_noise_sigma / 0.12f);
    float curved_strength = std::pow(linear_strength, 0.45f);

    const float base_clip_multiplier = 3.0f;
    float boosted_clip_multiplier = base_clip_multiplier * (1.0f + 0.5f * aggression_factor);

    float clip_limit = 0.6f + (curved_strength * boosted_clip_multiplier);

    if (clip_limit > 0.61f)
    {
        cv::Mat img_8u, img_8u_clahe;
        current_image_gray_full.convertTo(img_8u, CV_8U, 255.0);
        
        cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
        clahe->apply(img_8u, img_8u_clahe);

        img_8u_clahe.convertTo(current_image_gray_full, CV_32F, 1.0/255.0);
    }

    // --- LANGKAH 4: Penyesuaian Kecerahan Adaptif (Gamma) ---
    cv::Scalar mean_scalar = cv::mean(current_image_gray_full);
    float mean_brightness = static_cast<float>(mean_scalar[0]);
    const float dark_threshold = 0.4f;

    if (mean_brightness < dark_threshold)
    {
        const float max_gamma_reduction = 0.3f;
        float factor = (dark_threshold - mean_brightness) / dark_threshold;
        float gamma = 1.0f - (max_gamma_reduction * factor);
        cv::pow(current_image_gray_full, gamma, current_image_gray_full);
    }

    // --- LANGKAH 5: Tone Mapping Global (S-Curve) ---
    const float s_curve_contrast = 4.0f; 
    float adaptive_s_curve_contrast = s_curve_contrast + (2.0f * aggression_factor);

    auto sigmoid_contrast_cpp = [&](float x, float contrast) {
        return 1.0f / (1.0f + std::exp(-contrast * (x - 0.5f)));
    };

    float low = sigmoid_contrast_cpp(0.0f, adaptive_s_curve_contrast);
    float high = sigmoid_contrast_cpp(1.0f, adaptive_s_curve_contrast);

    cv::Mat temp_exp;
    cv::exp(-adaptive_s_curve_contrast * (current_image_gray_full - 0.5), temp_exp);
    current_image_gray_full = 1.0 / (1.0 + temp_exp);
    current_image_gray_full = (current_image_gray_full - low) / (high - low);

    cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
    cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);

    // --- Kalkulasi Parameter Adaptif ---
    float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / 0.1f, 1.0f);
    adapted_motion_sensitivity = motion_sensitivity * (1.0f - 0.65f * adaptation_factor);
    adapted_noise_offset_factor = noise_offset_factor * (1.0f + 0.85f * adaptation_factor);

    // =================================================================================
    // === BAGIAN B: ANALISIS SKALA KASAR (OPTIMASI BARU DENGAN GRID + INTERPOLASI) ===
    // =================================================================================
        // SimpleTimer coarse_analysis_timer("B. Coarse Scale Analysis (Pyramid)");

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
                    for (int i = 0; i < num_pyramid_levels - 1; ++i)
                    {
                        cv::Mat next_current;
                        cv::pyrDown(current_pyramid.back(), next_current);
                        current_pyramid.push_back(next_current);
                    }
                }
#pragma omp task
                {
                    reference_pyramid.reserve(num_pyramid_levels);
                    reference_pyramid.push_back(reference_image_gray_full);
                    for (int i = 0; i < num_pyramid_levels - 1; ++i)
                    {
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

            if (level > 0)
            {
                cv::resize(guidance_map, guidance_map, current_img_level.size(), 0, 0, cv::INTER_LINEAR);
            }

            const int num_tiles_h = current_img_level.rows / tile_h_fine;
            const int num_tiles_w = current_img_level.cols / tile_w_fine;
            if (num_tiles_h == 0 || num_tiles_w == 0)
                continue;

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
                if (tile_h_fine > 0 && tile_w_fine > 0)
                {
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
                                                               res, global_estimated_noise_sigma, adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                         : 0.0f;

                    // --- OPTIMASI 2 (Lanjutan): Ganti cv::mean dengan lookup Integral Image (O(1)) ---
                    const int x1 = roi.x;
                    const int y1 = roi.y;
                    const int x2 = roi.x + roi.width;
                    const int y2 = roi.y + roi.height;

                    // Akses 4 titik pada integral image untuk mendapatkan jumlah area
                    const double sum = guidance_map_integral.at<double>(y2, x2) - guidance_map_integral.at<double>(y2, x1) - guidance_map_integral.at<double>(y1, x2) + guidance_map_integral.at<double>(y1, x1);

                    const float guidance_confidence = static_cast<float>(sum / (roi.width * roi.height));

                    confidence_grid.at<float>(r_tile, c_tile) = confidence_level * guidance_confidence;
                }
            }

            cv::resize(confidence_grid, guidance_map, current_img_level.size(), 0, 0, cv::INTER_LINEAR);
        }

        // --- Upscale peta panduan final ke resolusi penuh (tidak berubah) ---
        if (!guidance_map.empty() && guidance_map.size() != current_image_gray_full.size())
        {
            cv::resize(guidance_map, guidance_map, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
        }
        else if (guidance_map.empty())
        {
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
        for (int i = 0; i < h_img * w_img * channels; ++i)
            final_image_sum_ptr[i] = 0.0f;
#pragma omp parallel for
        for (int i = 0; i < h_img * w_img; ++i)
            weight_map_sum_ptr[i] = 0.0f;

#pragma omp parallel
        {
            // === Variabel Lokal per-Thread ===
            // Kita kembalikan buffer lokal kecil ini.
            // Ini penting agar setiap thread bisa bekerja tanpa mengganggu yang lain.
            cv::Mat local_weighted_tile(tile_h_fine, tile_w_fine, CV_32FC(channels));
            cv::Mat local_weight_tile(tile_h_fine, tile_w_fine, CV_32FC1);

            MotionMatching::MBMBuffers mbm_buffers_fine;
            if (tile_h_fine > 0 && tile_w_fine > 0)
            {
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
                    if (r + tile_h_fine > h_img || c + tile_w_fine > w_img)
                        continue;

                    cv::Rect tile_roi(c, r, tile_w_fine, tile_h_fine);

                    // Perhitungan confidence 
                    MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_similarity(
                        current_image_gray_full(tile_roi), reference_image_gray_full(tile_roi),
                        global_estimated_noise_sigma,
                        GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_fine);

                    float confidence_fine = mbm_result.success ? MotionMatching::calculate_match_confidence(
                                                                     mbm_result, global_estimated_noise_sigma,
                                                                     adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                               : 0.0f;

                    float guidance_confidence = static_cast<float>(cv::mean(guidance_map(tile_roi))[0]);
                    float final_confidence = confidence_fine * guidance_confidence;

                    if (!stability_map_mat.empty())
                    {
                        final_confidence *= static_cast<float>(cv::mean(stability_map_mat(tile_roi))[0]);
                    }

                    if (final_confidence < 1e-5f)
                        continue;

                    // --- LANGKAH 1: Hitung & Simpan ke Buffer LOKAL (Sangat Cepat, Tanpa Kunci/Lock) ---
                    const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h_fine, tile_w_fine, CV_32FC1, const_cast<float *>(base_window_ptr));

                    // Operasi perkalian ini sekarang mengisi buffer lokal milik thread, bukan global.
                    cv::multiply(base_window_tile_mat, final_confidence, local_weight_tile);

                    if (channels > 1)
                    {
                        cv::Mat weighted_mask_color;
                        std::vector<cv::Mat> mask_channels(channels, local_weight_tile);
                        cv::merge(mask_channels, weighted_mask_color);
                        cv::multiply(current_tile_for_accumulation, weighted_mask_color, local_weighted_tile);
                    }
                    else
                    {
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
}