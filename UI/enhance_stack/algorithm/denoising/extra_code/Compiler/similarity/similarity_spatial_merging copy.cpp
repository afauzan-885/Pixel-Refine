// similarity_motion.cpp
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

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;
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

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            (block_h <= 0 && tile_h > 0 && block_w > 0) ||
            (block_w <= 0 && tile_w > 0 && block_h > 0))
            return;

        int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0) return;

        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        cv::Mat current_image_gray_full, reference_image_gray_full;
        if (current_image_mat.channels() > 1) {
            cv::Mat tmp;
            cv::cvtColor(current_image_mat, tmp, cv::COLOR_BGR2GRAY);
            tmp.convertTo(current_image_gray_full, CV_32F);
        } else {
            current_image_mat.convertTo(current_image_gray_full, CV_32F);
        }

        if (reference_image_mat.channels() > 1) {
            cv::Mat tmp;
            cv::cvtColor(reference_image_mat, tmp, cv::COLOR_BGR2GRAY);
            tmp.convertTo(reference_image_gray_full, CV_32F);
        } else {
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }

        CV_Assert(current_image_gray_full.type() == CV_32FC1 && reference_image_gray_full.type() == CV_32FC1);

    #pragma omp parallel
        {
            cv::Mat thread_block_confidences;
            MotionMatching::MBMBuffers mbm_buffers_th;

            int mbm_alloc_h = (block_h > 0 && block_h < tile_h) ? block_h : tile_h;
            int mbm_alloc_w = (block_w > 0 && block_w < tile_w) ? block_w : tile_w;

            if (mbm_alloc_h > 0 && mbm_alloc_w > 0) {
                mbm_buffers_th.diff_workspace.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
                mbm_buffers_th.grad_x.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_y.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_mag_current.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
            }

    #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; ++i) {
                for (int j = 0; j < num_col_starts; ++j) {
                    int r = row_starts[i], c = col_starts[j];
                    if (r < 0 || c < 0 || r + tile_h > h_img || c + tile_w > w_img) continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    const cv::Mat current_tile = current_image_mat(tile_roi);
                    const cv::Mat current_tile_gray = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray = reference_image_gray_full(tile_roi);
                    const cv::Mat base_window_tile(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                    float estimated_noise_sigma = 0.0f;
    #ifdef TILE_NOISE_ESTIMATION_HPP
                    if (reference_tile_gray.rows >= 3 && reference_tile_gray.cols >= 3) {
                        estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                            reference_tile_gray, MAD_TO_SIGMA_FACTOR);
                    }
    #endif

                    int actual_block_h = block_h > 0 ? block_h : tile_h;
                    int actual_block_w = block_w > 0 ? block_w : tile_w;
                    int num_blocks_h = (tile_h + actual_block_h - 1) / actual_block_h;
                    int num_blocks_w = (tile_w + actual_block_w - 1) / actual_block_w;

                    if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w ||
                        thread_block_confidences.type() != CV_32FC1) {
                        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                    }
                    thread_block_confidences.setTo(0.0f);

                    for (int bh = 0; bh < num_blocks_h; ++bh) {
                        float* conf_row = thread_block_confidences.ptr<float>(bh);
                        for (int bw = 0; bw < num_blocks_w; ++bw) {
                            int block_r = bh * actual_block_h;
                            int block_c = bw * actual_block_w;
                            int block_h_eff = std::min(actual_block_h, tile_h - block_r);
                            int block_w_eff = std::min(actual_block_w, tile_w - block_c);
                            if (block_h_eff <= 0 || block_w_eff <= 0) {
                                conf_row[bw] = 0.0f;
                                continue;
                            }

                            cv::Rect block_roi(block_c, block_r, block_w_eff, block_h_eff);
                            const cv::Mat current_block = current_tile_gray(block_roi);

                            if (current_block.empty()) {
                                conf_row[bw] = 0.0f;
                                continue;
                            }

                            auto result = MotionMatching::find_best_block_match_mad(
                                current_block, reference_tile_gray,
                                block_r, block_c, search_radius,
                                GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON,
                                mbm_buffers_th);

                            conf_row[bw] = result.success
                                ? calculate_match_confidence(result, estimated_noise_sigma, motion_sensitivity, noise_offset_factor)
                                : 0.0f;
                        }
                    }

                    if (CONFIDENCE_MAP_BLUR_KERNEL_SIZE > 1) {
                        int k = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : CONFIDENCE_MAP_BLUR_KERNEL_SIZE + 1;
                        cv::GaussianBlur(thread_block_confidences, thread_block_confidences, cv::Size(k, k), 0, 0, cv::BORDER_REPLICATE);
                    }

                    for (int y = 0; y < tile_h; ++y) {
                    const float* color_row = current_tile.ptr<const float>(y);
                    const float* base_row = base_window_tile.ptr<const float>(y);
                    int gy = r + y;
                    float* weight_row = weight_map_sum_mat.ptr<float>(gy);
                    float* sum_row = final_image_sum_mat.ptr<float>(gy);

                    for (int x = 0; x < tile_w; ++x) {
                        int bh = std::min(y / actual_block_h, num_blocks_h - 1);
                        int bw = std::min(x / actual_block_w, num_blocks_w - 1);

                        float confidence = thread_block_confidences.ptr<float>(bh)[bw];
                        float weight = base_row[x] * confidence;

                        if (weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                            int gx = c + x;

                            // update weight map
                            weight_row[gx] += weight;

                            int idx_local = x * channels;
                            int idx_global = gx * channels;

                            // asumsi channels kelipatan 4 (atau minimal 1), kita pakai simd pragma
                            #pragma omp simd
                            for (int ch = 0; ch < channels; ++ch) {
                                sum_row[idx_global + ch] += color_row[idx_local + ch] * weight;
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