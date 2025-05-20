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

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig {
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
        int mbm_block_h, int mbm_block_w, int mbm_search_radius,
        float p_motion_sensitivity,
        float p_noise_offset_factor
        )
    {
        using namespace MotionMetricsConfig;

        const float current_mad_sensitivity = p_motion_sensitivity;
        const float current_noise_offset_factor = p_noise_offset_factor;

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            (mbm_block_h <=0 && tile_h > 0 && mbm_block_w >0) || // Kondisi mbm_block yang lebih tepat
            (mbm_block_w <=0 && tile_w > 0 && mbm_block_h >0) ) {
            return;
        }
        int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0) return;

        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float*>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float*>(reference_image_ptr));
        
        cv::Mat current_image_gray_full_data, reference_image_gray_full_data;
        cv::Mat current_image_gray_full, reference_image_gray_full;

        if (current_image_mat.channels() > 1) {
            cv::cvtColor(current_image_mat, current_image_gray_full_data, cv::COLOR_BGR2GRAY);
            current_image_gray_full_data.convertTo(current_image_gray_full, CV_32F);
        } else {
            current_image_mat.convertTo(current_image_gray_full, CV_32F);
        }
        if (reference_image_mat.channels() > 1) {
            cv::cvtColor(reference_image_mat, reference_image_gray_full_data, cv::COLOR_BGR2GRAY);
            reference_image_gray_full_data.convertTo(reference_image_gray_full, CV_32F);
        } else {
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }
        CV_Assert(current_image_gray_full.type() == CV_32FC1 && reference_image_gray_full.type() == CV_32FC1);
        CV_Assert(!current_image_gray_full.empty() && !reference_image_gray_full.empty());
      
        #pragma omp parallel
        {
            cv::Mat thread_block_confidences; 
            MotionMatching::MBMBuffers mbm_buffers_th;
            int mbm_alloc_h = tile_h;
            if (mbm_block_h > 0 && mbm_block_h < tile_h) {
                mbm_alloc_h = mbm_block_h;
            }
            int mbm_alloc_w = tile_w;
            if (mbm_block_w > 0 && mbm_block_w < tile_w) {
                mbm_alloc_w = mbm_block_w;
            }

            if (mbm_alloc_h > 0 && mbm_alloc_w > 0) {
                mbm_buffers_th.diff_workspace.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
                mbm_buffers_th.grad_x.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_y.create(mbm_alloc_h, mbm_alloc_w, CV_32F);
                mbm_buffers_th.grad_mag_current.create(mbm_alloc_h, mbm_alloc_w, CV_32FC1);
            }
         
            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h_img || (c + tile_w) > w_img || tile_h <= 0 || tile_w <=0) continue; // Cek tile_h/w > 0

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    const cv::Mat current_tile_for_accumulation = current_image_mat(tile_roi);
                    const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi); 
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));


                    if (current_tile_gray_for_mbm.empty() || reference_tile_gray_for_mbm.empty() || current_tile_for_accumulation.empty()){
                        continue;
                    }
                    float estimated_noise_sigma_tile = 0.0f;
                    if (reference_tile_gray_for_mbm.rows >=3 && reference_tile_gray_for_mbm.cols >=3) {
                        #ifdef TILE_NOISE_ESTIMATION_HPP
                            estimated_noise_sigma_tile = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                               reference_tile_gray_for_mbm, MAD_TO_SIGMA_FACTOR
                            );
                        #else
                        
                        #endif
                    }


                    int actual_mbm_block_h = (mbm_block_h > 0) ? mbm_block_h : tile_h; 
                    int actual_mbm_block_w = (mbm_block_w > 0) ? mbm_block_w : tile_w; 
                    int num_blocks_h = (actual_mbm_block_h > 0 && tile_h > 0) ? (tile_h + actual_mbm_block_h - 1) / actual_mbm_block_h : 0;
                    int num_blocks_w = (actual_mbm_block_w > 0 && tile_w > 0) ? (tile_w + actual_mbm_block_w - 1) / actual_mbm_block_w : 0;
                    
                    if (num_blocks_h == 0 || num_blocks_w == 0) continue; 

                    if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w || thread_block_confidences.type() != CV_32FC1) {
                        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                    }
                    thread_block_confidences.setTo(cv::Scalar(0.0f)); 

                    for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                            int block_local_r_start = bh_idx * actual_mbm_block_h;
                            int block_local_c_start = bw_idx * actual_mbm_block_w;
                            int current_block_h_dim = std::min(actual_mbm_block_h, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_mbm_block_w, tile_w - block_local_c_start);

                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) {
                                 thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f; 
                                 continue;
                            }

                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            const cv::Mat current_block_to_match = current_tile_gray_for_mbm(current_block_roi_local);

                            if (current_block_to_match.empty()) {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                continue;
                            }
                            
                            MotionMatching::BlockMatchResult mbm_result =
                                MotionMatching::find_best_block_match_mad(
                                    current_block_to_match,
                                    reference_tile_gray_for_mbm,
                                    block_local_r_start,
                                    block_local_c_start,
                                    mbm_search_radius,
                                    GRADIENT_WEIGHT_FACTOR,
                                    STABILITY_EPSILON,
                                    mbm_buffers_th
                                );

                            float confidence = 0.0f;
                            if(mbm_result.success) {
                                confidence = calculate_match_confidence(
                                    mbm_result,
                                    estimated_noise_sigma_tile,
                                    current_mad_sensitivity,
                                    current_noise_offset_factor
                                );
                            }
                            thread_block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                        }
                    }
                    
                    if (num_blocks_h * num_blocks_w > 0) {
                        for (int y = 0; y < tile_h; ++y) {
                            const float* current_tile_color_row = current_tile_for_accumulation.ptr<const float>(y); 
                            const float* base_window_row = base_window_tile_mat.ptr<const float>(y); 
                            int gy = r + y;
                            float* global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                            float* global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);
                            for (int x = 0; x < tile_w; ++x) {
                                int bh_idx = (actual_mbm_block_h > 0) ? std::min(y / actual_mbm_block_h, num_blocks_h - 1) : 0;
                                int bw_idx = (actual_mbm_block_w > 0) ? std::min(x / actual_mbm_block_w, num_blocks_w - 1) : 0;
                                
                                float block_confidence = thread_block_confidences.at<float>(bh_idx, bw_idx);
                                float base_win_val = base_window_row[x];
                                float pixel_weight = base_win_val * block_confidence;

                                if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    int gx = c + x;
                                    #pragma omp atomic update
                                    global_weight_sum_row[gx] += pixel_weight;
                                    int current_pixel_idx_local = x * channels;
                                    int current_pixel_idx_global = gx * channels;
                                    for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                        float weighted_pixel_value = current_tile_color_row[current_pixel_idx_local + ch_idx] * pixel_weight;
                                        #pragma omp atomic update
                                        global_pixel_sum_row[current_pixel_idx_global + ch_idx] += weighted_pixel_value;
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

        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0) {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0 && channels > 0) return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float*>(weight_map_sum_ptr));

        #pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            float* final_pixel_row_ptr = final_image_mat.ptr<float>(gy);
            const float* weight_map_sum_row_ptr = weight_map_sum_mat.ptr<const float>(gy);
            for (int gx = 0; gx < w; ++gx) {
                float total_weight = weight_map_sum_row_ptr[gx]; 
                int pixel_idx_base = gx * channels; 

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row_ptr[pixel_idx_base + ch] *= inv_total_weight;
                    }
                } else {
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row_ptr[pixel_idx_base + ch] = 0.0f;
                    }
                }
            }
        }
    }
}