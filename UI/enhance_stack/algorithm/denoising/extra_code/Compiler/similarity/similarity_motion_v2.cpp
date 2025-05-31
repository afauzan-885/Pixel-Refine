// similarity_motion_dft_only.cpp
#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>
// #include "block_matching.hpp" // DIHILANGKAN
#include "tile_noise_estimation.hpp"
#include "DFT_merging.hpp"

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    // constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f; // Tidak digunakan lagi
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;
    constexpr float DFT_WIENER_C_FACTOR = 3.0f; // Anda bisa sesuaikan ini
} // namespace MotionMetricsConfig

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
        int mbm_block_h, int mbm_block_w,
        int mbm_search_radius,       // Tidak digunakan lagi secara aktif jika MBM dihilangkan
        float p_motion_sensitivity,  // Tidak digunakan lagi
        float p_noise_offset_factor) // Tidak digunakan lagi
    {
        using namespace MotionMetricsConfig;

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            (mbm_block_h <= 0 && tile_h > 0 && mbm_block_w > 0) || // Validasi ukuran blok tetap relevan untuk pembagian tile
            (mbm_block_w <= 0 && tile_w > 0 && mbm_block_h > 0))
        {
            return;
        }

        int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0) return;

        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));

        // Kita masih butuh reference_image_gray_full untuk estimasi noise
        cv::Mat reference_image_gray_full;
        if (channels > 1) {
            cv::Mat reference_image_gray_full_data;
            cv::cvtColor(reference_image_mat, reference_image_gray_full_data, cv::COLOR_BGR2GRAY);
            reference_image_gray_full_data.convertTo(reference_image_gray_full, CV_32F);
        } else {
            reference_image_mat.convertTo(reference_image_gray_full, CV_32F);
        }
        CV_Assert(reference_image_gray_full.type() == CV_32FC1 && !reference_image_gray_full.empty());


#pragma omp parallel
        {
            cv::Mat thread_block_confidences;
            MotionMerging::DFTBuffers dft_buffers_th;
            cv::Mat thread_merged_tile_data;

            // Variabel mbm_alloc_h/w tidak lagi relevan jika MBM buffers dihilangkan
            // Namun, actual_mbm_block_h/w masih digunakan untuk iterasi blok

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
                    const cv::Mat current_tile_color_data = current_image_mat(tile_roi);
                    const cv::Mat reference_tile_color_data = reference_image_mat(tile_roi);
                    const cv::Mat reference_tile_gray_for_noise_est = reference_image_gray_full(tile_roi); // Untuk estimasi noise
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

                    if (current_tile_color_data.empty() || reference_tile_color_data.empty() || reference_tile_gray_for_noise_est.empty())
                    {
                        continue;
                    }

                    int merged_tile_type = (channels == 1) ? CV_32FC1 : CV_32FC(channels);
                    if (thread_merged_tile_data.rows != tile_h || thread_merged_tile_data.cols != tile_w || thread_merged_tile_data.type() != merged_tile_type) {
                        thread_merged_tile_data.create(tile_h, tile_w, merged_tile_type);
                    }
                    thread_merged_tile_data.setTo(cv::Scalar::all(0.0f));

                    float estimated_noise_sigma_tile = 0.0f;
                    if (reference_tile_gray_for_noise_est.rows >= 3 && reference_tile_gray_for_noise_est.cols >= 3)
                    {
#ifdef TILE_NOISE_ESTIMATION_HPP
                        estimated_noise_sigma_tile = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(
                            reference_tile_gray_for_noise_est, MAD_TO_SIGMA_FACTOR);
#endif
                    }

                    // actual_mbm_block_h/w sekarang hanya berarti ukuran blok untuk DFT merging
                    int actual_block_h = (mbm_block_h > 0) ? mbm_block_h : tile_h;
                    int actual_block_w = (mbm_block_w > 0) ? mbm_block_w : tile_w;
                    int num_blocks_h = (actual_block_h > 0 && tile_h > 0) ? (tile_h + actual_block_h - 1) / actual_block_h : 0;
                    int num_blocks_w = (actual_block_w > 0 && tile_w > 0) ? (tile_w + actual_block_w - 1) / actual_block_w : 0;

                    if (num_blocks_h == 0 || num_blocks_w == 0) continue;

                    if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w || thread_block_confidences.type() != CV_32FC1)
                    {
                        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                    }
                    thread_block_confidences.setTo(cv::Scalar(0.0f));

                    for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx)
                    {
                        for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx)
                        {
                            int block_local_r_start = bh_idx * actual_block_h;
                            int block_local_c_start = bw_idx * actual_block_w;
                            int current_block_h_dim = std::min(actual_block_h, tile_h - block_local_r_start);
                            int current_block_w_dim = std::min(actual_block_w, tile_w - block_local_c_start);

                            if (current_block_h_dim <= 0 || current_block_w_dim <= 0) {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                continue;
                            }

                            cv::Rect block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            const cv::Mat current_block_color_for_merge = current_tile_color_data(block_roi_local);
                            const cv::Mat reference_block_color_at_same_pos = reference_tile_color_data(block_roi_local); // Ambil dari posisi yang sama
                            cv::Mat target_merged_submat = thread_merged_tile_data(block_roi_local);

                            if (current_block_color_for_merge.empty() || reference_block_color_at_same_pos.empty()) {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                if(!current_block_color_for_merge.empty()) current_block_color_for_merge.copyTo(target_merged_submat);
                                else { target_merged_submat.setTo(cv::Scalar::all(0.0f));} // Jika current kosong, isi dengan nol
                                continue;
                            }

                            float dft_confidence_for_block = 0.0f;

                            if (channels == 1) {
                                MotionMerging::FrequencyMergeResult dft_result_gray =
                                    MotionMerging::merge_blocks_frequency_domain(
                                        current_block_color_for_merge, // Ini adalah grayscale
                                        reference_block_color_at_same_pos, // Ini juga grayscale
                                        estimated_noise_sigma_tile,
                                        DFT_WIENER_C_FACTOR,
                                        STABILITY_EPSILON,
                                        dft_buffers_th);
                                if (dft_result_gray.success && !dft_result_gray.merged_block_gray.empty()) {
                                    dft_result_gray.merged_block_gray.copyTo(target_merged_submat);
                                    dft_confidence_for_block = dft_result_gray.merge_confidence;
                                } else {
                                    current_block_color_for_merge.copyTo(target_merged_submat); // Fallback
                                    dft_confidence_for_block = 0.1f; // Confidence rendah jika merge gagal
                                }
                            } else { // channels > 1
                                std::vector<cv::Mat> current_channels, ref_channels_same_pos, merged_channels_vec;
                                cv::split(current_block_color_for_merge, current_channels);
                                cv::split(reference_block_color_at_same_pos, ref_channels_same_pos);
                                merged_channels_vec.resize(channels);

                                float total_confidence = 0.0f;
                                bool all_channels_merged_successfully = true;

                                for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                    MotionMerging::FrequencyMergeResult dft_result_ch =
                                        MotionMerging::merge_blocks_frequency_domain(
                                            current_channels[ch_idx],
                                            ref_channels_same_pos[ch_idx],
                                            estimated_noise_sigma_tile,
                                            DFT_WIENER_C_FACTOR,
                                            STABILITY_EPSILON,
                                            dft_buffers_th);
                                    if (dft_result_ch.success && !dft_result_ch.merged_block_gray.empty()) {
                                        merged_channels_vec[ch_idx] = dft_result_ch.merged_block_gray;
                                        total_confidence += dft_result_ch.merge_confidence;
                                    } else {
                                        current_channels[ch_idx].copyTo(merged_channels_vec[ch_idx]); // Fallback
                                        total_confidence += 0.1f;
                                        all_channels_merged_successfully = false;
                                    }
                                }
                                cv::merge(merged_channels_vec, target_merged_submat);
                                dft_confidence_for_block = (channels > 0) ? (total_confidence / channels) : 0.0f;
                                if (!all_channels_merged_successfully && dft_confidence_for_block > 0.2f) dft_confidence_for_block = 0.2f;
                            }
                            thread_block_confidences.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, dft_confidence_for_block));
                        }
                    }

                    if (CONFIDENCE_MAP_BLUR_KERNEL_SIZE > 1 && num_blocks_h > 0 && num_blocks_w > 0) {
                        int ksize = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : CONFIDENCE_MAP_BLUR_KERNEL_SIZE + 1;
                        cv::GaussianBlur(thread_block_confidences, thread_block_confidences, cv::Size(ksize, ksize), 0, 0, cv::BORDER_REPLICATE);
                    }

                    // Loop akumulasi tetap sama
                    for (int y_tile = 0; y_tile < tile_h; ++y_tile) {
                        const float *merged_tile_row = thread_merged_tile_data.ptr<const float>(y_tile);
                        const float *base_window_row = base_window_tile_mat.ptr<const float>(y_tile);
                        int gy = r + y_tile;
                        float *global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                        float *global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);

                        for (int x_tile = 0; x_tile < tile_w; ++x_tile) {
                            int bh_idx = (actual_block_h > 0) ? std::min(y_tile / actual_block_h, num_blocks_h - 1) : 0;
                            int bw_idx = (actual_block_w > 0) ? std::min(x_tile / actual_block_w, num_blocks_w - 1) : 0;
                            float block_confidence = (num_blocks_h > 0 && num_blocks_w > 0) ? thread_block_confidences.at<float>(bh_idx, bw_idx) : 0.0f;
                            float base_win_val = base_window_row[x_tile];
                            float pixel_weight = base_win_val * block_confidence;

                            if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                int gx = c + x_tile;
#pragma omp atomic update
                                global_weight_sum_row[gx] += pixel_weight;
                                int merged_pixel_idx_local = x_tile * channels;
                                int global_pixel_idx_global = gx * channels;
                                for (int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                                    float merged_pixel_value_ch = merged_tile_row[merged_pixel_idx_local + ch_idx];
                                    float weighted_pixel_value = merged_pixel_value_ch * pixel_weight;
#pragma omp atomic update
                                    global_pixel_sum_row[global_pixel_idx_global + ch_idx] += weighted_pixel_value;
                                }
                            }
                        }
                    }
                }
            }
        } // end pragma omp parallel
    }

    // normalize_accumulated_image_jit tetap sama
    void normalize_accumulated_image_jit(
        float *final_image_ptr,
        const float *weight_map_sum_ptr,
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;
        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0) return;
        int mat_type = CV_32FC(channels);
        if (mat_type == 0 && channels > 0) return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

#pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            float *final_pixel_row_ptr = final_image_mat.ptr<float>(gy);
            const float *weight_map_sum_row_ptr = weight_map_sum_mat.ptr<const float>(gy);
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
} // extern C