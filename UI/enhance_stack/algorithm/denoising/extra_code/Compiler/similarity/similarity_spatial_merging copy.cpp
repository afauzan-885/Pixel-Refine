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
#include "motion_compensate.hpp"

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
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
        int block_h, int block_w, int search_radius,
        float motion_sensitivity,
        float noise_offset_factor)
    {
        using namespace MotionMetricsConfig;

        // Pengecekan awal, tidak berubah
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr ||
            !reference_image_ptr || !base_window_ptr || !row_starts || !col_starts ||
            h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0)
            return;

        const int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0)
            return;

        // Pre-kalkulasi konstanta, tidak berubah
        const int actual_block_h = block_h > 0 ? block_h : tile_h;
        const int actual_block_w = block_w > 0 ? block_w : tile_w;

        // Konstanta yang tidak berhubungan dengan kompensasi gerakan tetap ada
        static constexpr float CONFIDENCE_OFFSET_FACTOR = 2.0f;
        static constexpr float LOW_TEXTURE_THRESHOLD = 8.0f;
        static constexpr float LOW_TEXTURE_BOOST = 1.2f;

        // Wrapper matriks (tanpa copy), tidak berubah
        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        // Konversi ke grayscale, tidak berubah
        cv::Mat current_image_gray_full, reference_image_gray_full;

        if (current_image_mat.channels() == 3)
        {
            cv::cvtColor(current_image_mat, current_image_gray_full, cv::COLOR_BGR2GRAY);
        }
        else if (current_image_mat.channels() == 1)
        {
            current_image_gray_full = current_image_mat;
        }
        else
        {
            current_image_mat.convertTo(current_image_gray_full, CV_32F);
        }

        if (reference_image_mat.channels() == 3)
        {
            cv::cvtColor(reference_image_mat, reference_image_gray_full, cv::COLOR_BGR2GRAY);
        }
        else if (reference_image_mat.channels() == 1)
        {
            reference_image_gray_full = reference_image_mat;
        }
        else
        {
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }

        if (current_image_gray_full.type() != CV_32F)
        {
            current_image_gray_full.convertTo(current_image_gray_full, CV_32F);
        }
        if (reference_image_gray_full.type() != CV_32F)
        {
            reference_image_gray_full.convertTo(reference_image_gray_full, CV_32F);
        }

        // Lambda helper yang masih relevan (tidak dipindahkan)
        const auto calculate_confidence_with_offset = [](float base_confidence, float offset_magnitude,
                                                         float noise_sigma, float motion_sens) -> float
        {
            const float offset_penalty = 1.0f / (1.0f + CONFIDENCE_OFFSET_FACTOR * offset_magnitude);
            const float noise_factor = (noise_sigma > 0.01f) ? (1.0f + noise_sigma * 0.1f) : 1.0f;
            const float motion_factor = std::clamp(motion_sens * (2.0f - offset_magnitude * 0.2f), 0.1f, 2.0f);
            return std::clamp(base_confidence * offset_penalty * motion_factor / noise_factor, 0.0f, 1.0f);
        };

        // Pengaturan threading, tidak berubah
        const int total_tiles = num_row_starts * num_col_starts;
        const int num_threads = std::min(omp_get_max_threads(), std::max(1, total_tiles / 4));
        const int chunk_size = std::max(1, total_tiles / (num_threads * 2));

#pragma omp parallel num_threads(num_threads)
        {
            cv::Mat thread_block_confidences;
            cv::Mat grad_mag_cache;

            MotionCompensate::MotionCompensationBuffers motion_buffers_th;

            const int alloc_size = std::max(tile_h, tile_w);

            if (alloc_size > 0)
            {
                motion_buffers_th.mbm_buffers.diff_workspace.create(alloc_size, alloc_size, CV_32FC1);
                motion_buffers_th.mbm_buffers.grad_x.create(alloc_size, alloc_size, CV_32F);
                motion_buffers_th.mbm_buffers.grad_y.create(alloc_size, alloc_size, CV_32F);
                motion_buffers_th.mbm_buffers.grad_mag_current.create(alloc_size, alloc_size, CV_32FC1);

                // Alokasi untuk buffer lainnya
                grad_mag_cache.create(alloc_size, alloc_size, CV_32F);
            }

#pragma omp for schedule(dynamic, chunk_size) nowait
            for (int tile_idx = 0; tile_idx < total_tiles; ++tile_idx)
            {
                const int i = tile_idx / num_col_starts;
                const int j = tile_idx % num_col_starts;
                const int r = row_starts[i], c = col_starts[j];

                if (r < 0 || c < 0 || r + tile_h > h_img || c + tile_w > w_img)
                    continue;

                const cv::Rect tile_roi(c, r, tile_w, tile_h);
                const cv::Mat current_tile = current_image_mat(tile_roi);
                const cv::Mat current_tile_gray = current_image_gray_full(tile_roi);
                const cv::Mat reference_tile_gray = reference_image_gray_full(tile_roi);
                const cv::Mat base_window_tile(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                // Estimasi noise (logika tetap sama)
                float estimated_noise_sigma = 0.0f;
#ifdef TILE_NOISE_ESTIMATION_HPP
                if (reference_tile_gray.rows >= 3 && reference_tile_gray.cols >= 3)
                {
                    estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                        reference_tile_gray, MAD_TO_SIGMA_FACTOR);
                }
#endif

                MotionCompensate::MotionData motion_result = MotionCompensate::process_tile_motion(
                    current_image_mat,
                    current_image_gray_full,
                    reference_image_gray_full,
                    tile_roi,
                    search_radius,
                    motion_buffers_th 
                );

                const cv::Mat working_tile = motion_result.compensation_applied
                                                 ? motion_result.compensated_color_tile
                                                 : current_tile;

                const cv::Mat working_tile_gray = motion_result.compensation_applied
                                                      ? motion_result.compensated_gray_tile
                                                      : current_tile_gray;

                const float tile_offset_weight = motion_result.offset_weight;
                const bool compensation_applied = motion_result.compensation_applied;
                // =========================================================

                // Pemrosesan block (logika tidak berubah)
                const int num_blocks_h = (tile_h + actual_block_h - 1) / actual_block_h;
                const int num_blocks_w = (tile_w + actual_block_w - 1) / actual_block_w;

                if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w)
                {
                    thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                }
                thread_block_confidences.setTo(0.0f);

                for (int bh = 0; bh < num_blocks_h; ++bh)
                {
                    float *const conf_row = thread_block_confidences.ptr<float>(bh);

                    for (int bw = 0; bw < num_blocks_w; ++bw)
                    {
                        const int block_r = bh * actual_block_h;
                        const int block_c = bw * actual_block_w;
                        const int block_h_eff = std::min(actual_block_h, tile_h - block_r);
                        const int block_w_eff = std::min(actual_block_w, tile_w - block_c);

                        if (block_h_eff <= 0 || block_w_eff <= 0)
                        {
                            conf_row[bw] = 0.0f;
                            continue;
                        }

                        const cv::Rect block_roi(block_c, block_r, block_w_eff, block_h_eff);
                        const cv::Mat current_block = working_tile_gray(block_roi);

                        if (current_block.empty())
                        {
                            conf_row[bw] = 0.0f;
                            continue;
                        }

                        const int effective_search = compensation_applied ? std::max(1, search_radius / 2) : search_radius;
                        const auto result = MotionMatching::find_best_block_match_mad(
                            current_block, reference_tile_gray, block_r, block_c, effective_search,
                            GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, motion_buffers_th.mbm_buffers);

                        float confidence = 0.0f;
                        if (result.success)
                        {
                        const auto [block_offset_x, block_offset_y] = MotionCompensate::get_motion_offsets(result);
                        const float block_offset_magnitude = std::sqrt(block_offset_x * block_offset_x + block_offset_y * block_offset_y);

                        confidence = calculate_match_confidence(result, estimated_noise_sigma, motion_sensitivity, noise_offset_factor);
                            confidence = calculate_confidence_with_offset(confidence, block_offset_magnitude, estimated_noise_sigma, motion_sensitivity);
                        }

                        if (confidence > 0.1f && confidence < 0.8f)
                        {
                            const int cache_size = std::min({current_block.rows, current_block.cols, alloc_size});
                            if (cache_size > 2)
                            {
                                const cv::Rect cache_roi(0, 0, cache_size, cache_size);
                                cv::Mat grad_mag_roi = grad_mag_cache(cache_roi);

                                cv::Laplacian(current_block, grad_mag_roi, CV_32F, 1);
                                grad_mag_roi = cv::abs(grad_mag_roi);

                                const double mean_grad = cv::mean(grad_mag_roi)[0];
                                if (mean_grad < LOW_TEXTURE_THRESHOLD)
                                {
                                    confidence = std::min(confidence * LOW_TEXTURE_BOOST, 1.0f);
                                }
                            }
                        }

                        confidence *= tile_offset_weight;
                        conf_row[bw] = std::clamp(confidence, 0.0f, 1.0f);
                    }
                }

                if (thread_block_confidences.rows >= 2 && thread_block_confidences.cols >= 2)
                {
                    const int blur_kernel_size = 3;
                    const double sigma = 0.8;
                    cv::GaussianBlur(thread_block_confidences, thread_block_confidences,
                                    cv::Size(blur_kernel_size, blur_kernel_size), sigma, sigma, cv::BORDER_REPLICATE);
                }


                const float *const base_window_data = base_window_tile.ptr<const float>(0);

                for (int y = 0; y < tile_h; ++y)
                {
                    const float *const color_row = working_tile.ptr<const float>(y);
                    const float *const base_row = base_window_data + y * tile_w;
                    const int gy = r + y;

                    float *const weight_row = weight_map_sum_mat.ptr<float>(gy);
                    float *const sum_row = final_image_sum_mat.ptr<float>(gy);

                    const int bh = std::min(y / actual_block_h, num_blocks_h - 1);
                    const float *const conf_row = thread_block_confidences.ptr<const float>(bh);

                    if (channels == 1)
                    {
                        for (int x = 0; x < tile_w; ++x)
                        {
                            const int bw = std::min(x / actual_block_w, num_blocks_w - 1);
                            const float weight = base_row[x] * conf_row[bw];

                            if (weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                            {
                                const int gx = c + x;
#pragma omp atomic
                                weight_row[gx] += weight;
#pragma omp atomic
                                sum_row[gx] += color_row[x] * weight;
                            }
                        }
                    }
                    else
                    {
                        for (int x = 0; x < tile_w; ++x)
                        {
                            const int bw = std::min(x / actual_block_w, num_blocks_w - 1);
                            const float weight = base_row[x] * conf_row[bw];

                            if (weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                            {
                                const int gx = c + x;

#pragma omp atomic
                                weight_row[gx] += weight;

                                const int idx_local = x * channels;
                                const int idx_global = gx * channels;

                                if (channels == 3)
                                {
#pragma omp atomic
                                    sum_row[idx_global] += color_row[idx_local] * weight;
#pragma omp atomic
                                    sum_row[idx_global + 1] += color_row[idx_local + 1] * weight;
#pragma omp atomic
                                    sum_row[idx_global + 2] += color_row[idx_local + 2] * weight;
                                }
                                else
                                {
                                    for (int ch = 0; ch < channels; ++ch)
                                    {
#pragma omp atomic
                                        sum_row[idx_global + ch] += color_row[idx_local + ch] * weight;
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
        {
            return;
        }
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