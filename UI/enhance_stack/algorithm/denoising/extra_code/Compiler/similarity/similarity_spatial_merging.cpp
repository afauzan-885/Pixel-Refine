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

        cv::Mat current_image_gray_full, reference_image_gray_full;
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
        TextureAnalysis::detect_flat_tiles(
            ref_channels_for_flat_detection, tile_h, tile_w, channels,
            FLATNESS_VARIANCE_THRESHOLD, is_tile_flat);

        float global_estimated_noise_sigma = 0.015f;
#ifdef TILE_NOISE_ESTIMATION_HPP
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
        {
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
        }
#endif
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

#pragma omp parallel
        {
            MotionCompensate::MotionCompensationBuffers buffers_th;

            // ======================== SOLUSI ========================
            // Blok kode yang menyebabkan error DIHAPUS.
            // `compensated_..._tile` adalah bagian dari hasil (`MotionData`),
            // bukan bagian dari buffer input (`MotionCompensationBuffers`).
            // ========================================================

            // Inisialisasi buffer untuk block matching (ini sudah benar)
            int mbm_alloc_h = (block_h > 0) ? block_h : tile_h;
            int mbm_alloc_w = (block_w > 0) ? block_w : tile_w;
            if (mbm_alloc_h > 0 && mbm_alloc_w > 0)
            {
                buffers_th.mbm_buffers.diff_workspace.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
                buffers_th.mbm_buffers.grad_x.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                buffers_th.mbm_buffers.grad_y.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                buffers_th.mbm_buffers.grad_mag_current.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
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

                    MotionCompensate::MotionData motion_data = MotionCompensate::process_tile_motion(
                        current_image_mat, current_image_gray_full, reference_image_gray_full,
                        tile_roi, search_radius, buffers_th);

                    cv::Mat current_tile_for_accumulation;
                    cv::Mat current_tile_gray_for_mbm;
                    if (motion_data.compensation_applied)
                    {
                        current_tile_for_accumulation = motion_data.compensated_color_tile;
                        current_tile_gray_for_mbm = motion_data.compensated_gray_tile;
                    }
                    else
                    {
                        current_tile_for_accumulation = current_image_mat(tile_roi);
                        current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    }

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
                                block_local_c_start, search_radius, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_th.mbm_buffers);

                            float confidence = 0.0f;
                            if (mbm_result.success)
                            {
                                confidence = MotionMatching::calculate_match_confidence(
                                    mbm_result, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor);

                                if (current_tile_is_flat)
                                {
                                    confidence *= FLATNESS_CONFIDENCE_BOOST;
                                    confidence = std::min(confidence, 1.0f);
                                }
                            }
                            thread_block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                        }
                    }

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