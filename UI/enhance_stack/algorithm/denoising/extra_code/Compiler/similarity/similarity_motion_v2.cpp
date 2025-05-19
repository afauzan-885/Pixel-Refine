#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>
#include "DFT_merging.hpp"
#include "tile_noise_estimation.hpp"
#include "block_matching.hpp"

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig
{
    // Konstanta Dasar
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;

    // --- Konstanta untuk Pembobotan Gradien ---
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;

    // Konstanta Adaptasi Noise
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;

    constexpr float DARK_UPPER_THRESHOLD = 127.0f / 255.0f;
    constexpr float MAX_MIN_DARK_CONFIDENCE = 1e-3f;
    constexpr int DARKNESS_MAP_BLUR_KERNEL_SIZE = 1;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;

    // --- Konstanta untuk Merging Domain Frekuensi ---
    constexpr bool  APPLY_FREQ_DOMAIN_MERGING = true;
}

extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, float *weight_map_sum_ptr,
        const float *current_image_ptr, const float *reference_image_ptr,
        const float *base_window_ptr, const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts, int tile_h, int tile_w,
        int h_img, int w_img, int channels_input,
        int mbm_block_h, int mbm_block_w, int mbm_search_radius,
        float frame_max_adaptive_multiplier,
        float p_mbm_mad_sensitivity,
        float p_mbm_noise_mad_offset_factor,
        float p_mbm_confidence_skip_dft_threshold,
        int p_coarse_alignment_search_margin,
        float p_freq_merge_wiener_c_factor
        )
    {
        using namespace MotionMetricsConfig;

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels_input <= 0 ||
            (mbm_block_h <=0 && tile_h > 0 && mbm_block_w >0) || 
            (mbm_block_w <=0 && tile_w > 0 && mbm_block_h >0) ) { 
            return;
        }
       
        int channels_cpp = channels_input;
        int mat_type_color = CV_32FC(channels_cpp);
        if (mat_type_color == 0 && channels_cpp > 0) return;

        // Wrapper Mat, tidak ada alokasi data baru di sini
        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat_input_const(h_img, w_img, CV_32FC(channels_input), const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat_input_const(h_img, w_img, CV_32FC(channels_input), const_cast<float *>(reference_image_ptr));

        // --- OPTIMASI: Konversi Grayscale Sekali di Awal ---
        cv::Mat current_image_gray_full_data, reference_image_gray_full_data; 
        cv::Mat current_image_gray_full, reference_image_gray_full;  

        if (current_image_mat_input_const.channels() > 1) {
            cv::cvtColor(current_image_mat_input_const, current_image_gray_full_data, cv::COLOR_BGR2GRAY);
            if (current_image_gray_full_data.type() != CV_32F) {
                current_image_gray_full_data.convertTo(current_image_gray_full_data, CV_32F);
            }
            current_image_gray_full = current_image_gray_full_data;
        } else {
            if (current_image_mat_input_const.type() == CV_32FC1) {
                current_image_gray_full = current_image_mat_input_const; 
            } else {
                current_image_mat_input_const.convertTo(current_image_gray_full_data, CV_32F);
                current_image_gray_full = current_image_gray_full_data;
            }
        }

        if (reference_image_mat_input_const.channels() > 1) {
            cv::cvtColor(reference_image_mat_input_const, reference_image_gray_full_data, cv::COLOR_BGR2GRAY);
            if (reference_image_gray_full_data.type() != CV_32F) {
                reference_image_gray_full_data.convertTo(reference_image_gray_full_data, CV_32F);
            }
            reference_image_gray_full = reference_image_gray_full_data;
        } else {
            if (reference_image_mat_input_const.type() == CV_32FC1) {
                reference_image_gray_full = reference_image_mat_input_const; // Berbagi data
            } else {
                reference_image_mat_input_const.convertTo(reference_image_gray_full_data, CV_32F);
                reference_image_gray_full = reference_image_gray_full_data;
            }
        }

        if (current_image_gray_full.empty() || reference_image_gray_full.empty()) {
            return;
        }
        CV_Assert(current_image_gray_full.type() == CV_32FC1 && reference_image_gray_full.type() == CV_32FC1);
     

#pragma omp parallel
        {
            // --- OPTIMASI: Deklarasi buffer per-thread di luar loop tile ---
            cv::Mat darkness_map_raw_th, darkness_map_smoothed_th;
            cv::Mat block_confidences_raw_th, block_confidences_smoothed_th;
            cv::Mat noise_estimation_source_th; 

            std::vector<cv::Mat> merged_gray_blocks_for_tile_th;

            // === TAMBAHKAN BUFFER DFT DI SINI ===
            MotionMerging::DFTBuffers dft_buffers_th;
            int max_block_h_for_dft = (mbm_block_h > 0) ? mbm_block_h : tile_h;
            int max_block_w_for_dft = (mbm_block_w > 0) ? mbm_block_w : tile_w;
            if (tile_h < max_block_h_for_dft && tile_h > 0) max_block_h_for_dft = tile_h;
            if (tile_w < max_block_w_for_dft && tile_w > 0) max_block_w_for_dft = tile_w;


            if (max_block_h_for_dft > 0 && max_block_w_for_dft > 0) {
                int max_optimal_rows = cv::getOptimalDFTSize(max_block_h_for_dft);
                int max_optimal_cols = cv::getOptimalDFTSize(max_block_w_for_dft);
                max_optimal_rows = std::max(max_optimal_rows, max_block_h_for_dft);
                max_optimal_cols = std::max(max_optimal_cols, max_block_w_for_dft);


                if (max_optimal_rows > 0 && max_optimal_cols > 0) {
                    dft_buffers_th.current_padded.create(max_optimal_rows, max_optimal_cols, CV_32FC1);
                    dft_buffers_th.ref_padded.create(max_optimal_rows, max_optimal_cols, CV_32FC1);
                    dft_buffers_th.current_dft.create(max_optimal_rows, max_optimal_cols, CV_32FC2); // DFT complex output
                    dft_buffers_th.ref_dft.create(max_optimal_rows, max_optimal_cols, CV_32FC2);
                    dft_buffers_th.merged_dft.create(max_optimal_rows, max_optimal_cols, CV_32FC2);
                    dft_buffers_th.temp_spatial_merged.create(max_optimal_rows, max_optimal_cols, CV_32FC1); // Real output
                }
            }


            #pragma omp for collapse(2) schedule(static)
            for (int i_tile_row = 0; i_tile_row < num_row_starts; i_tile_row++) {
                for (int j_tile_col = 0; j_tile_col < num_col_starts; j_tile_col++) {
                    int r_tile_start = row_starts[i_tile_row];
                    int c_tile_start = col_starts[j_tile_col];

                    if (r_tile_start < 0 || c_tile_start < 0 || (r_tile_start + tile_h) > h_img || (c_tile_start + tile_w) > w_img || tile_h <= 0 || tile_w <= 0)
                        continue;

                    cv::Rect tile_roi_orig(c_tile_start, r_tile_start, tile_w, tile_h);
                    
                    const cv::Mat current_tile_color_th = current_image_mat_input_const(tile_roi_orig);
                    const cv::Mat current_tile_gray_master_th = current_image_gray_full(tile_roi_orig);
                    const cv::Mat reference_tile_gray_for_mbm_th = reference_image_gray_full(tile_roi_orig); // ROI untuk MBM

                    const cv::Mat base_window_tile_mat_th(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));


                    if (current_tile_color_th.empty() || current_tile_gray_master_th.empty() || reference_tile_gray_for_mbm_th.empty()) {
                        continue;
                    }

                    float estimated_noise_sigma_tile = 0.0f;
                    int larger_tile_factor_noise = 2;
                    int noise_est_base_r = r_tile_start;
                    int noise_est_base_c = c_tile_start;
                    int larger_r_noise = std::max(0, noise_est_base_r - tile_h * (larger_tile_factor_noise - 1) / 2);
                    int larger_c_noise = std::max(0, noise_est_base_c - tile_w * (larger_tile_factor_noise - 1) / 2);
                    int larger_h_dim_noise = std::min(h_img - larger_r_noise, tile_h * larger_tile_factor_noise);
                    int larger_w_dim_noise = std::min(w_img - larger_c_noise, tile_w * larger_tile_factor_noise);

                    cv::Mat noise_estimation_source_th;
                    if (larger_h_dim_noise >= 3 && larger_w_dim_noise >= 3) {
                        cv::Rect larger_roi_noise(larger_c_noise, larger_r_noise, larger_w_dim_noise, larger_h_dim_noise);
                        if (larger_roi_noise.x >= 0 && larger_roi_noise.y >= 0 &&
                            larger_roi_noise.width > 0 && larger_roi_noise.height > 0 && 
                            larger_roi_noise.x + larger_roi_noise.width <= reference_image_gray_full.cols &&
                            larger_roi_noise.y + larger_roi_noise.height <= reference_image_gray_full.rows) {
                            noise_estimation_source_th = reference_image_gray_full(larger_roi_noise);
                        }
                    }
                    if (noise_estimation_source_th.empty() || noise_estimation_source_th.rows < 3 || noise_estimation_source_th.cols < 3) {
                        if (reference_tile_gray_for_mbm_th.rows >=3 && reference_tile_gray_for_mbm_th.cols >=3) {
                           noise_estimation_source_th = reference_tile_gray_for_mbm_th;
                        }
                    }

                    if (!noise_estimation_source_th.empty()) {
                         estimated_noise_sigma_tile = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                            noise_estimation_source_th, MAD_TO_SIGMA_FACTOR
                        );
                    }
                    


                    int actual_mbm_block_h_tile = (mbm_block_h > 0 && tile_h > 0) ? mbm_block_h : tile_h;
                    int actual_mbm_block_w_tile = (mbm_block_w > 0 && tile_w > 0) ? mbm_block_w : tile_w;
                   
                    int num_blocks_h_tile = (actual_mbm_block_h_tile > 0 && tile_h > 0) ? (tile_h + actual_mbm_block_h_tile - 1) / actual_mbm_block_h_tile : (tile_h > 0 ? 1:0);
                    int num_blocks_w_tile = (actual_mbm_block_w_tile > 0 && tile_w > 0) ? (tile_w + actual_mbm_block_w_tile - 1) / actual_mbm_block_w_tile : (tile_w > 0 ? 1:0);

                    if (num_blocks_h_tile == 0 || num_blocks_w_tile == 0) continue;

                    
                    if (darkness_map_raw_th.rows != num_blocks_h_tile || darkness_map_raw_th.cols != num_blocks_w_tile || darkness_map_raw_th.type() != CV_32F) {
                        darkness_map_raw_th.create(num_blocks_h_tile, num_blocks_w_tile, CV_32F);
                    }
                    darkness_map_raw_th.setTo(cv::Scalar(0.0f));

                   
                    for (int bh_idx = 0; bh_idx < num_blocks_h_tile; ++bh_idx) {
                        for (int bw_idx = 0; bw_idx < num_blocks_w_tile; ++bw_idx) {
                            int block_local_r_start = bh_idx * actual_mbm_block_h_tile;
                            int block_local_c_start = bw_idx * actual_mbm_block_w_tile;
                            int current_block_h_dim = std::min(actual_mbm_block_h_tile, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_mbm_block_w_tile, tile_w - block_local_c_start);
                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) continue;

                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                           
                            if (current_block_roi_local.x >= 0 && current_block_roi_local.y >= 0 &&
                                current_block_roi_local.x + current_block_roi_local.width <= current_tile_gray_master_th.cols &&
                                current_block_roi_local.y + current_block_roi_local.height <= current_tile_gray_master_th.rows)
                            {
                                const cv::Mat current_block_gray_for_darkness_th = current_tile_gray_master_th(current_block_roi_local);
                                if (!current_block_gray_for_darkness_th.empty()) {
                                    float avg_intensity = static_cast<float>(cv::mean(current_block_gray_for_darkness_th)[0]);
                                    float darkness_factor = 0.0f;
                                    if (avg_intensity < DARK_UPPER_THRESHOLD) {
                                        float norm_intens = avg_intensity / DARK_UPPER_THRESHOLD;
                                        darkness_factor = 1.0f - norm_intens * norm_intens;
                                    }
                                    darkness_map_raw_th.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, darkness_factor));
                                } 
                            } 
                        }
                    }
                    
                    int kernel_sz_dark_tile = (DARKNESS_MAP_BLUR_KERNEL_SIZE >= 1 && DARKNESS_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? DARKNESS_MAP_BLUR_KERNEL_SIZE : 1;
                    if (!darkness_map_raw_th.empty() && kernel_sz_dark_tile >=3 ) { 
                        cv::GaussianBlur(darkness_map_raw_th, darkness_map_smoothed_th, cv::Size(kernel_sz_dark_tile, kernel_sz_dark_tile), 0);
                    } else if (!darkness_map_raw_th.empty()) {
                        darkness_map_raw_th.copyTo(darkness_map_smoothed_th);
                    } else {
                        if(darkness_map_smoothed_th.rows != num_blocks_h_tile || darkness_map_smoothed_th.cols != num_blocks_w_tile || darkness_map_smoothed_th.type() != CV_32F) {
                           darkness_map_smoothed_th.create(num_blocks_h_tile, num_blocks_w_tile, CV_32F);
                        }
                        darkness_map_smoothed_th.setTo(cv::Scalar(0.0f));
                    }
                   

                   
                    if (block_confidences_raw_th.rows != num_blocks_h_tile || block_confidences_raw_th.cols != num_blocks_w_tile || block_confidences_raw_th.type() != CV_32F) {
                        block_confidences_raw_th.create(num_blocks_h_tile, num_blocks_w_tile, CV_32F);
                    }
                    block_confidences_raw_th.setTo(cv::Scalar(0.0f));

                    bool darkness_map_is_usable_tile = !darkness_map_smoothed_th.empty() &&
                                                  darkness_map_smoothed_th.rows == num_blocks_h_tile &&
                                                  darkness_map_smoothed_th.cols == num_blocks_w_tile;

                    
                    size_t required_block_storage_size = static_cast<size_t>(num_blocks_h_tile) * num_blocks_w_tile;
                    if (merged_gray_blocks_for_tile_th.size() < required_block_storage_size) {
                        merged_gray_blocks_for_tile_th.resize(required_block_storage_size);
                    }
                    

                    for (int bh_idx = 0; bh_idx < num_blocks_h_tile; ++bh_idx) {
                        for (int bw_idx = 0; bw_idx < num_blocks_w_tile; ++bw_idx) {
                            size_t block_idx_flat = static_cast<size_t>(bh_idx) * num_blocks_w_tile + bw_idx;
                            
                            int block_local_r_start = bh_idx * actual_mbm_block_h_tile;
                            int block_local_c_start = bw_idx * actual_mbm_block_w_tile;
                            int current_block_h_dim = std::min(actual_mbm_block_h_tile, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_mbm_block_w_tile, tile_w - block_local_c_start);

                            
                            cv::Mat current_block_merged_gray_output_th; 

                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) {
                                block_confidences_raw_th.at<float>(bh_idx, bw_idx) = 0.0f;
                                if(block_idx_flat < merged_gray_blocks_for_tile_th.size()) merged_gray_blocks_for_tile_th[block_idx_flat].release(); // Kosongkan jika tidak valid
                                continue;
                            }

                            cv::Rect current_block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            
                            if (!(current_block_roi_local.x >= 0 && current_block_roi_local.y >= 0 &&
                                  current_block_roi_local.x + current_block_roi_local.width <= current_tile_gray_master_th.cols &&
                                  current_block_roi_local.y + current_block_roi_local.height <= current_tile_gray_master_th.rows))
                            {
                                block_confidences_raw_th.at<float>(bh_idx, bw_idx) = 0.0f;
                                
                                if(block_idx_flat < merged_gray_blocks_for_tile_th.size()) {
                                     merged_gray_blocks_for_tile_th[block_idx_flat].create(current_block_h_dim, current_block_w_dim, CV_32FC1);
                                     merged_gray_blocks_for_tile_th[block_idx_flat].setTo(cv::Scalar(0.0f));
                                }
                                continue;
                            }

                            const cv::Mat current_block_gray_th = current_tile_gray_master_th(current_block_roi_local);
                            current_block_gray_th.copyTo(current_block_merged_gray_output_th); 

                            if (current_block_gray_th.empty()) { 
                                 block_confidences_raw_th.at<float>(bh_idx, bw_idx) = 0.0f;
                                 if(block_idx_flat < merged_gray_blocks_for_tile_th.size()) merged_gray_blocks_for_tile_th[block_idx_flat] = current_block_merged_gray_output_th.clone();
                                 continue;
                            }

                            MotionMatching::BlockMatchResult block_result =
                                MotionMatching::find_best_block_match_mad(
                                    current_block_gray_th, reference_tile_gray_for_mbm_th, 
                                    block_local_r_start, block_local_c_start, mbm_search_radius,
                                    GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON
                                );

                            float mbm_confidence_score = 0.0f;
                            if (block_result.success) {
                                float noise_induced_mad_offset_block = p_mbm_noise_mad_offset_factor * estimated_noise_sigma_tile;
                                float excess_mad = std::max(0.0f, block_result.min_mad - noise_induced_mad_offset_block);
                                mbm_confidence_score = std::exp(-excess_mad * p_mbm_mad_sensitivity);
                                mbm_confidence_score = std::max(0.0f, std::min(1.0f, mbm_confidence_score));
                            }

                            float freq_merge_confidence_val = 0.0f; 
                            if (APPLY_FREQ_DOMAIN_MERGING && block_result.success && mbm_confidence_score >= p_mbm_confidence_skip_dft_threshold) {
                                cv::Rect best_ref_block_roi(block_result.best_match_c, block_result.best_match_r, current_block_w_dim, current_block_h_dim);
                                
                                if (best_ref_block_roi.x >= 0 && best_ref_block_roi.y >= 0 &&
                                    best_ref_block_roi.x + best_ref_block_roi.width <= reference_tile_gray_for_mbm_th.cols && 
                                    best_ref_block_roi.y + best_ref_block_roi.height <= reference_tile_gray_for_mbm_th.rows)
                                {
                                    
                                    
                                    const cv::Mat ref_block_from_mbm_gray_th = reference_tile_gray_for_mbm_th(best_ref_block_roi);
                                    
                                    MotionMerging::FrequencyMergeResult merge_result =
                                        MotionMerging::merge_blocks_frequency_domain(
                                            current_block_gray_th,
                                            ref_block_from_mbm_gray_th,
                                            estimated_noise_sigma_tile,
                                            p_freq_merge_wiener_c_factor,
                                            STABILITY_EPSILON,
                                            dft_buffers_th
                                        );

                                    if (merge_result.success && !merge_result.merged_block_gray.empty()) {
                                        
                                        current_block_merged_gray_output_th = merge_result.merged_block_gray;
                                        freq_merge_confidence_val = merge_result.merge_confidence;
                                    } 
                                }
                            } else if (!APPLY_FREQ_DOMAIN_MERGING && block_result.success) {
                                freq_merge_confidence_val = 1.0f;
                            }
                            if(block_idx_flat < merged_gray_blocks_for_tile_th.size()) {
                                if (current_block_merged_gray_output_th.data == current_block_gray_th.data) {
                                   merged_gray_blocks_for_tile_th[block_idx_flat] = current_block_merged_gray_output_th.clone();
                                } else {
                                   merged_gray_blocks_for_tile_th[block_idx_flat] = current_block_merged_gray_output_th;
                                }
                            }


                            float combined_confidence = mbm_confidence_score * freq_merge_confidence_val;
                            if (!APPLY_FREQ_DOMAIN_MERGING && block_result.success) {
                                combined_confidence = mbm_confidence_score;
                            }

                            float final_block_confidence = combined_confidence;
                            float smoothed_darkness_factor_block = 0.0f;
                            if (darkness_map_is_usable_tile && bh_idx < darkness_map_smoothed_th.rows && bw_idx < darkness_map_smoothed_th.cols) {
                                smoothed_darkness_factor_block = darkness_map_smoothed_th.at<float>(bh_idx, bw_idx);
                            }
                           if (mbm_confidence_score > CONFIDENCE_EPSILON) {
                               final_block_confidence = std::max(final_block_confidence, smoothed_darkness_factor_block * MAX_MIN_DARK_CONFIDENCE);
                            } else { 
                               final_block_confidence = std::min(final_block_confidence, smoothed_darkness_factor_block * MAX_MIN_DARK_CONFIDENCE);
                            }
                            block_confidences_raw_th.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, final_block_confidence));
                        }
                    } 

                    int kernel_sz_conf_tile = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE >= 1 && CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : 1;
                    if (!block_confidences_raw_th.empty() && kernel_sz_conf_tile >= 3) {
                        cv::GaussianBlur(block_confidences_raw_th, block_confidences_smoothed_th, cv::Size(kernel_sz_conf_tile, kernel_sz_conf_tile), 0);
                    } else if (!block_confidences_raw_th.empty()) {
                        block_confidences_raw_th.copyTo(block_confidences_smoothed_th);
                    } else {
                        if(block_confidences_smoothed_th.rows != num_blocks_h_tile || block_confidences_smoothed_th.cols != num_blocks_w_tile || block_confidences_smoothed_th.type() != CV_32F) {
                           block_confidences_smoothed_th.create(num_blocks_h_tile, num_blocks_w_tile, CV_32F);
                        }
                        block_confidences_smoothed_th.setTo(cv::Scalar(0.0f));
                    }
                    
                    
                    bool confidence_map_is_usable_for_pixels_tile = !block_confidences_smoothed_th.empty() &&
                                                               block_confidences_smoothed_th.rows == num_blocks_h_tile &&
                                                               block_confidences_smoothed_th.cols == num_blocks_w_tile;

                    
                    if (confidence_map_is_usable_for_pixels_tile) { 
                        for (int y_in_tile = 0; y_in_tile < tile_h; ++y_in_tile) {
                            const float *base_window_row_ptr = base_window_tile_mat_th.ptr<const float>(y_in_tile);
                            int gy_global = r_tile_start + y_in_tile;
                            
                            if (gy_global >= h_img) continue;

                            float* final_image_sum_row_ptr = final_image_sum_mat.ptr<float>(gy_global);
                            float* weight_map_sum_row_ptr = weight_map_sum_mat.ptr<float>(gy_global);

                            for (int x_in_tile = 0; x_in_tile < tile_w; ++x_in_tile) {
                                int bh_idx_pixel = (actual_mbm_block_h_tile > 0) ? std::min(y_in_tile / actual_mbm_block_h_tile, num_blocks_h_tile - 1) : 0;
                                int bw_idx_pixel = (actual_mbm_block_w_tile > 0) ? std::min(x_in_tile / actual_mbm_block_w_tile, num_blocks_w_tile - 1) : 0;
                                

                                float block_confidence_pixel_val = block_confidences_smoothed_th.at<float>(bh_idx_pixel, bw_idx_pixel);
                                float base_win_val = base_window_row_ptr[x_in_tile];
                                float pixel_accum_weight = base_win_val * block_confidence_pixel_val;

                                if (pixel_accum_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    int gx_global = c_tile_start + x_in_tile;
                                    
                                    if (gx_global >= w_img) continue;

                                    #pragma omp atomic update
                                    weight_map_sum_row_ptr[gx_global] += pixel_accum_weight;

                                    int block_local_r_start_pixel = bh_idx_pixel * actual_mbm_block_h_tile;
                                    int block_local_c_start_pixel = bw_idx_pixel * actual_mbm_block_w_tile;
                                    int y_in_block_pixel = y_in_tile - block_local_r_start_pixel;
                                    int x_in_block_pixel = x_in_tile - block_local_c_start_pixel;
                                    
                                    size_t flat_block_index_pixel = static_cast<size_t>(bh_idx_pixel) * num_blocks_w_tile + bw_idx_pixel;
                                    
                                    
                                    if (flat_block_index_pixel >= merged_gray_blocks_for_tile_th.size() || merged_gray_blocks_for_tile_th[flat_block_index_pixel].empty() ||
                                        y_in_block_pixel < 0 || y_in_block_pixel >= merged_gray_blocks_for_tile_th[flat_block_index_pixel].rows ||
                                        x_in_block_pixel < 0 || x_in_block_pixel >= merged_gray_blocks_for_tile_th[flat_block_index_pixel].cols) {
                                        continue; 
                                    }
                                    const cv::Mat& active_merged_gray_block_pixel = merged_gray_blocks_for_tile_th[flat_block_index_pixel];
                                    
                                    
                                    int current_block_h_dim_pixel = std::min(actual_mbm_block_h_tile, tile_h - block_local_r_start_pixel);
                                    int current_block_w_dim_pixel = std::min(actual_mbm_block_w_tile, tile_w - block_local_c_start_pixel);
                                    cv::Rect current_block_roi_pixel_orig(block_local_c_start_pixel, block_local_r_start_pixel, current_block_w_dim_pixel, current_block_h_dim_pixel);

                                    if (!(y_in_block_pixel < current_block_h_dim_pixel && x_in_block_pixel < current_block_w_dim_pixel)) continue; // Pastikan y_in_block & x_in_block valid untuk ROI

                                    const cv::Mat current_block_color_orig_pixel_th = current_tile_color_th(current_block_roi_pixel_orig);
                                    const cv::Mat current_block_gray_orig_pixel_th = current_tile_gray_master_th(current_block_roi_pixel_orig);

                                    if (current_block_color_orig_pixel_th.empty() || current_block_gray_orig_pixel_th.empty()) continue;
                                            
                                    float gray_merged_val_pixel = active_merged_gray_block_pixel.at<float>(y_in_block_pixel, x_in_block_pixel);
                                    float gray_orig_val_pixel = current_block_gray_orig_pixel_th.at<float>(y_in_block_pixel, x_in_block_pixel);
                                    
                                    float ratio_gray = (gray_orig_val_pixel > STABILITY_EPSILON) ? (gray_merged_val_pixel / gray_orig_val_pixel) : 1.0f;
                                    ratio_gray = std::max(0.0f, std::min(ratio_gray, 2.0f));

                                    float ratio_deviation = ratio_gray - 1.0f;
                                    float adjusted_ratio_gray = 1.0f + (ratio_deviation * block_confidence_pixel_val);

                                    for (int ch = 0; ch < channels_cpp; ++ch) {
                                        float color_val_orig_pixel;
                                        if (channels_cpp == 1) {
                                            color_val_orig_pixel = current_block_color_orig_pixel_th.at<float>(y_in_block_pixel, x_in_block_pixel);
                                        } else {
                                            color_val_orig_pixel = current_block_color_orig_pixel_th.ptr<const float>(y_in_block_pixel)[x_in_block_pixel * channels_cpp + ch];
                                        }

                                        float final_color_val_pixel = color_val_orig_pixel * adjusted_ratio_gray;
                                        final_color_val_pixel = std::max(0.0f, std::min(1.0f, final_color_val_pixel)); // Pastikan dalam rentang [0,1]

                                        float weighted_pixel_color_value = final_color_val_pixel * pixel_accum_weight;
                                        #pragma omp atomic update
                                        final_image_sum_row_ptr[gx_global * channels_cpp + ch] += weighted_pixel_color_value;
                                    }
                                }
                            }
                        }
                    } 
                }
            }
        }
    }

    [[nodiscard]] float estimate_global_noise(
        const float *reference_image_ptr,
        int h, int w, int channels,
        int tile_h, int tile_w,
        const int *row_starts, int num_row_starts,
        const int *col_starts, int num_col_starts)
    {
        using namespace MotionMetricsConfig;

        if (!reference_image_ptr || !row_starts || !col_starts || h <= 0 || w <= 0 ||
            channels <= 0 || tile_h <= 0 || tile_w <= 0 || num_row_starts <= 0 || num_col_starts <= 0)
        {
            return 0.0f;
        }

        int mat_type = CV_32FC(channels);
        if (mat_type == 0 && channels > 0) return 0.0f;

        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float *>(reference_image_ptr));
        cv::Mat ref_gray_float;

        if (reference_image_mat.channels() > 1) {
            cv::cvtColor(reference_image_mat, ref_gray_float, cv::COLOR_BGR2GRAY);
        } else {
            reference_image_mat.copyTo(ref_gray_float);
        }
        if (ref_gray_float.type() != CV_32F) {
            ref_gray_float.convertTo(ref_gray_float, CV_32F);
        }

        if (ref_gray_float.empty()) {
            return 0.0f;
        }

        double total_sigma_sum = 0.0;
        long long valid_tile_count = 0;

        #pragma omp parallel
        {
            cv::Mat thread_tile;

            #pragma omp for collapse(2) schedule(static) reduction(+:total_sigma_sum, valid_tile_count)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w)
                        continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    thread_tile = ref_gray_float(tile_roi);

                    if (thread_tile.rows < 3 || thread_tile.cols < 3) {
                        continue;
                    }

                    float estimated_sigma_tile = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                                                    thread_tile,
                                                    MAD_TO_SIGMA_FACTOR
                                                );

                    if (estimated_sigma_tile > 0) {
                        total_sigma_sum += static_cast<double>(estimated_sigma_tile);
                        valid_tile_count++;
                    }
                }
            }
        }

        if (valid_tile_count > 0) {
            return static_cast<float>(total_sigma_sum / valid_tile_count);
        } else {
            return 0.0f;
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
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

        #pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            for (int gx = 0; gx < w; ++gx) {
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);
                float *final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx_base = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx_base + ch] *= inv_total_weight;
                    }
                } else {
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx_base + ch] = 0.0f;
                    }
                }
            }
        }
    }
}