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
    void generate_weight_map_jit(
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

        if (!weight_map_sum_ptr)
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

        // --- LANGKAH 2: Filtering Adaptif ---
        float global_estimated_noise_sigma = precomputed_ref_noise_sigma;

        // sesuai versi Python: noise 0.04–0.18 bilateral, >0.18 median
        if (global_estimated_noise_sigma > 0.04f)
        {
            if (global_estimated_noise_sigma < 0.18f)
            {
                float norm_noise = std::clamp((global_estimated_noise_sigma - 0.04f) / (0.18f - 0.04f), 0.0f, 1.0f);
                int diameter = 3 + static_cast<int>(4 * norm_noise);   // 3–7
                float d_sigma = 3.0f + 6.0f * norm_noise;              // 3–9
                float r_sigma = (20.0f + 80.0f * norm_noise) / 255.0f; // 0.078–0.39

                cv::Mat temp_filtered;
                cv::bilateralFilter(current_image_gray_full, temp_filtered, diameter, r_sigma, d_sigma);
                current_image_gray_full = temp_filtered;
            }
            else
            {
                int ksize = (global_estimated_noise_sigma < 0.22f) ? 3 : 5;
                cv::medianBlur(current_image_gray_full, current_image_gray_full, ksize);
            }
        }

        // --- LANGKAH 1.5: Faktor Agresi Berdasarkan Kontras ---
        cv::Scalar mean_val, stddev_val;
        cv::meanStdDev(current_image_gray_full, mean_val, stddev_val);
        float contrast_metric = static_cast<float>(stddev_val[0]);

        const float low_contrast_thresh = 0.12f;
        const float high_contrast_thresh = 0.20f;

        float aggression_factor = 1.0f - std::clamp(
                                             (contrast_metric - low_contrast_thresh) / (high_contrast_thresh - low_contrast_thresh),
                                             0.0f, 1.0f);

        // --- LANGKAH 2: Multi-scale Micro-Contrast Enhancement ---
        const float micro_contrast_noise_threshold = 0.05f;
        float micro_contrast_strength = 1.0f - std::min(1.0f, global_estimated_noise_sigma / micro_contrast_noise_threshold);

        if (micro_contrast_strength > 0.01f)
        {
            cv::Mat blur_small, blur_large;
            cv::GaussianBlur(current_image_gray_full, blur_small, cv::Size(0, 0), 0.8);
            cv::GaussianBlur(current_image_gray_full, blur_large, cv::Size(0, 0), 2.0);

            cv::Mat detail_small = current_image_gray_full - blur_small;
            cv::Mat detail_large = current_image_gray_full - blur_large;
            cv::Mat detail_mix = detail_small + 0.6f * detail_large;

            float base_strength = 0.6f + 0.4f * aggression_factor;
            float boost = base_strength * micro_contrast_strength;

            current_image_gray_full += boost * detail_mix;
            cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
            cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);
        }

        // --- LANGKAH 3: CLAHE dua tahap adaptif ---
        float linear_strength = 1.0f - std::min(1.0f, global_estimated_noise_sigma / 0.12f);
        float curved_strength = std::pow(linear_strength, 0.45f);
        float clip_limit = 0.6f + (curved_strength * (3.0f * (1.0f + 0.5f * aggression_factor)));

        if (clip_limit > 0.61f)
        {
            cv::Mat img_8u;
            current_image_gray_full.convertTo(img_8u, CV_8U, 255.0);

            cv::Ptr<cv::CLAHE> clahe = cv::createCLAHE(clip_limit, cv::Size(8, 8));
            clahe->apply(img_8u, img_8u);

            // tahap kedua jika aggression_factor > 0.5
            if (aggression_factor > 0.5f)
            {
                cv::Ptr<cv::CLAHE> clahe2 = cv::createCLAHE(clip_limit * 0.6f, cv::Size(12, 12));
                clahe2->apply(img_8u, img_8u);
            }

            img_8u.convertTo(current_image_gray_full, CV_32F, 1.0 / 255.0);
        }

        // --- LANGKAH 4: Local Structure Enhancement (Laplacian) ---
        cv::Mat lap;
        cv::Laplacian(current_image_gray_full, lap, CV_32F, 3);
        float lap_strength = 0.15f * aggression_factor * (1.0f - global_estimated_noise_sigma * 2.0f);
        current_image_gray_full += lap_strength * lap;
        cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
        cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);

        // --- LANGKAH 5: Adaptive Gamma Correction ---
        cv::Scalar mean_scalar = cv::mean(current_image_gray_full);
        float mean_brightness = static_cast<float>(mean_scalar[0]);
        if (mean_brightness < 0.4f)
        {
            float factor = (0.4f - mean_brightness) / 0.4f;
            float gamma = 1.0f - (0.3f * factor);
            cv::pow(current_image_gray_full + 1e-6f, gamma, current_image_gray_full);
            cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
            cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);
        }

        // --- LANGKAH 6: Adaptive S-Curve Tone Mapping ---
        const float s_curve_contrast = 4.0f;
        float adaptive_s_curve_contrast = s_curve_contrast + (2.0f * aggression_factor);

        auto sigmoid_contrast_cpp = [&](float x, float contrast)
        {
            return 1.0f / (1.0f + std::exp(-contrast * (x - 0.5f)));
        };

        float low = sigmoid_contrast_cpp(0.0f, adaptive_s_curve_contrast);
        float high = sigmoid_contrast_cpp(1.0f, adaptive_s_curve_contrast);

        cv::Mat temp_exp;
        cv::exp(-adaptive_s_curve_contrast * (current_image_gray_full - 0.5f), temp_exp);
        current_image_gray_full = 1.0f / (1.0f + temp_exp);
        current_image_gray_full = (current_image_gray_full - low) / (high - low);

        cv::threshold(current_image_gray_full, current_image_gray_full, 1.0f, 1.0f, cv::THRESH_TRUNC);
        cv::threshold(current_image_gray_full, current_image_gray_full, 0.0f, 0.0f, cv::THRESH_TOZERO);

        // --- Kalkulasi Parameter Adaptif ---
        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / 0.1f, 1.0f);
        adapted_motion_sensitivity = motion_sensitivity * (1.0f - 0.1f * adaptation_factor);
        adapted_noise_offset_factor = noise_offset_factor * (1.0f + 0.1f * adaptation_factor);

        /// =================================================================================
        // === BAGIAN B: ANALISIS SKALA KASAR (DENGAN MULTI-HIPOTESIS & PERKALIAN)      ===
        // =================================================================================
        {
            const int tile_h_fine = tile_h;
            const int tile_w_fine = tile_w;

            // --- Tentukan jumlah level piramida ---
            int max_level = 0;
            int temp_h = h_img, temp_w = w_img;
            while (temp_h >= tile_h_fine * 4 && temp_w >= tile_w_fine * 4)
            {
                temp_h /= 2;
                temp_w /= 2;
                max_level++;
            }
            const int num_pyramid_levels = std::min(max_level, 2) + 1;

            // --- Bangun piramida gambar ---
            std::vector<cv::Mat> current_pyramid, reference_pyramid;
            current_pyramid.reserve(num_pyramid_levels);
            reference_pyramid.reserve(num_pyramid_levels);

            current_pyramid.push_back(current_image_gray_full);
            reference_pyramid.push_back(reference_image_gray_full);
            for (int i = 0; i < num_pyramid_levels - 1; ++i)
            {
                cv::Mat next_current, next_ref;
                cv::pyrDown(current_pyramid.back(), next_current);
                cv::pyrDown(reference_pyramid.back(), next_ref);
                current_pyramid.push_back(next_current);
                reference_pyramid.push_back(next_ref);
            }

            std::reverse(current_pyramid.begin(), current_pyramid.end());
            std::reverse(reference_pyramid.begin(), reference_pyramid.end());

            // --- Peta panduan dimulai dari ukuran level terkecil ---
            cv::Mat guidance_map = cv::Mat(current_pyramid[0].rows / tile_h_fine, current_pyramid[0].cols / tile_w_fine, CV_32FC1, cv::Scalar(1.0f));

            // --- Loop dari skala paling kasar ke yang lebih halus ---
            for (int level = 0; level < num_pyramid_levels - 1; ++level)
            {
                const cv::Mat &coarse_guidance_grid = guidance_map; // Peta dari iterasi sebelumnya (kasar)

                const cv::Mat &current_img_fine = current_pyramid[level + 1];
                const cv::Mat &ref_img_fine = reference_pyramid[level + 1];

                const int num_tiles_h_fine = current_img_fine.rows / tile_h_fine;
                const int num_tiles_w_fine = current_img_fine.cols / tile_w_fine;
                if (num_tiles_h_fine == 0 || num_tiles_w_fine == 0)
                {
                    cv::Mat temp_guidance_map;
                    cv::resize(coarse_guidance_grid, temp_guidance_map, current_img_fine.size(), 0, 0, cv::INTER_LINEAR);
                    guidance_map = temp_guidance_map;
                    continue;
                }

                // Grid baru yang akan kita bangun untuk level halus
                cv::Mat fine_confidence_grid(num_tiles_h_fine, num_tiles_w_fine, CV_32FC1);

#pragma omp parallel for schedule(dynamic)
                for (int r_tile_fine = 0; r_tile_fine < num_tiles_h_fine; ++r_tile_fine)
                {
                    MotionMatching::MBMBuffers mbm_buffers;
                    if (tile_h_fine > 0 && tile_w_fine > 0)
                    {
                        mbm_buffers.diff_workspace.create(tile_h_fine, tile_w_fine, CV_32FC1);
                        mbm_buffers.grad_x.create(tile_h_fine, tile_w_fine, CV_32F);
                        mbm_buffers.grad_y.create(tile_h_fine, tile_w_fine, CV_32F);
                        mbm_buffers.grad_mag_current.create(tile_h_fine, tile_w_fine, CV_32FC1);
                    }

                    for (int c_tile_fine = 0; c_tile_fine < num_tiles_w_fine; ++c_tile_fine)
                    {
                        // 1. Hitung Confidence Lokal di Level Halus
                        cv::Rect roi_fine(c_tile_fine * tile_w_fine, r_tile_fine * tile_h_fine, tile_w_fine, tile_h_fine);

                        MotionMatching::TileMatchResult res = MotionMatching::calculate_tile_similarity(
                            current_img_fine(roi_fine), ref_img_fine(roi_fine),
                            global_estimated_noise_sigma,
                            GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers);

                        float local_confidence_fine = res.success ? MotionMatching::calculate_match_confidence(
                                                                        res, global_estimated_noise_sigma, adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                                  : 0.0f;

                        // 2. Kumpulkan Kandidat (Hipotesis) dari Grid Kasar
                        const int r_tile_coarse = r_tile_fine / 2;
                        const int c_tile_coarse = c_tile_fine / 2;

                        std::vector<float> candidate_guidances;
                        candidate_guidances.reserve(9);

                        for (int dr = -1; dr <= 1; ++dr)
                        {
                            for (int dc = -1; dc <= 1; ++dc)
                            {
                                int nr = r_tile_coarse + dr;
                                int nc = c_tile_coarse + dc;
                                if (nr >= 0 && nr < coarse_guidance_grid.rows && nc >= 0 && nc < coarse_guidance_grid.cols)
                                {
                                    candidate_guidances.push_back(coarse_guidance_grid.at<float>(nr, nc));
                                }
                            }
                        }
                        if (candidate_guidances.empty())
                        {
                            candidate_guidances.push_back(1.0f);
                        }

                        // 3. Uji Semua Hipotesis dengan PERKALIAN dan Pilih Hasil MAKSIMUM
                        float best_multiplied_confidence = 0.0f; // Inisialisasi ke 0

                        for (const float guidance_candidate : candidate_guidances)
                        {
                            float multiplied_confidence = local_confidence_fine * guidance_candidate;
                            if (multiplied_confidence > best_multiplied_confidence)
                            {
                                best_multiplied_confidence = multiplied_confidence;
                            }
                        }

                        // 4. Simpan hasil terbaik ke grid halus yang baru
                        fine_confidence_grid.at<float>(r_tile_fine, c_tile_fine) = best_multiplied_confidence;
                    }
                }

                // 5. Update `guidance_map` untuk iterasi selanjutnya (sekarang menjadi grid baru)
                guidance_map = fine_confidence_grid;
            }

            // --- Upscale peta panduan final ke resolusi penuh (interpolasi) ---
            cv::Mat final_guidance_map_full_res;
            if (!guidance_map.empty())
            {
                cv::resize(guidance_map, final_guidance_map_full_res, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
            }
            else
            {
                final_guidance_map_full_res = cv::Mat(h_img, w_img, CV_32FC1, cv::Scalar(1.0f));
            }

            // =================================================================================
            // === TAHAP 2: ANALISIS SKALA HALUS & AKUMULASI FINAL (DENGAN PERKALIAN)      ===
            // =================================================================================

            cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
            weight_map_sum_mat.setTo(0.0f);

#pragma omp parallel
            {
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

                        MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_similarity(
                            current_image_gray_full(tile_roi), reference_image_gray_full(tile_roi),
                            global_estimated_noise_sigma,
                            GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_fine);

                        float confidence_fine = mbm_result.success ? MotionMatching::calculate_match_confidence(
                                                                         mbm_result, global_estimated_noise_sigma,
                                                                         adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                                   : 0.0f;

                        // Ambil nilai dari peta panduan yang sudah di-upscale
                        float guidance_confidence = static_cast<float>(cv::mean(final_guidance_map_full_res(tile_roi))[0]);

                        // Gunakan perkalian murni seperti yang diminta
                        float final_confidence = confidence_fine * guidance_confidence;

                        if (!stability_map_mat.empty())
                        {
                            final_confidence *= static_cast<float>(cv::mean(stability_map_mat(tile_roi))[0]);
                        }

                        if (final_confidence < 1e-5f)
                            continue;

                        // ==============================================================
                        // === PENYISIPAN: Adaptive Spatial Proximity Weighting (Gaussian)
                        // ==============================================================
                        static thread_local cv::Mat spatial_weight;
                        if (spatial_weight.empty() ||
                            spatial_weight.rows != tile_h_fine || spatial_weight.cols != tile_w_fine)
                        {
                            spatial_weight.create(tile_h_fine, tile_w_fine, CV_32F);
                            const float sigma_x = tile_w_fine * 0.35f;
                            const float sigma_y = tile_h_fine * 0.35f;
                            const float cx = (tile_w_fine - 1) * 0.5f;
                            const float cy = (tile_h_fine - 1) * 0.5f;

                            for (int y = 0; y < tile_h_fine; ++y)
                            {
                                float *ptr = spatial_weight.ptr<float>(y);
                                for (int x = 0; x < tile_w_fine; ++x)
                                {
                                    const float dx = (x - cx);
                                    const float dy = (y - cy);
                                    ptr[x] = std::exp(-0.5f * (dx * dx / (sigma_x * sigma_x) + dy * dy / (sigma_y * sigma_y)));
                                }
                            }
                            double minv, maxv;
                            cv::minMaxLoc(spatial_weight, &minv, &maxv);
                            spatial_weight /= static_cast<float>(maxv);
                        }
                        // ==============================================================
                        // === AKHIR PENYISIPAN
                        // ==============================================================

                        const cv::Mat base_window_tile_mat(tile_h_fine, tile_w_fine, CV_32FC1, const_cast<float *>(base_window_ptr));
                        cv::multiply(base_window_tile_mat, final_confidence, local_weight_tile);

#pragma omp critical
                        {
                            cv::add(weight_map_sum_mat(tile_roi), local_weight_tile, weight_map_sum_mat(tile_roi));
                        }
                    }
                }
            }
        }
    }
}