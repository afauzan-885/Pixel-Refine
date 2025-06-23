#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp>

#include "tile_noise_estimation.hpp"
#include "DFT_merging.hpp"
#include "block_matching.hpp"
#include "spatial_merging.hpp"

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;

    // Parameter dari kode spasial Anda
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.3f;
    constexpr float SPATIAL_MOTION_SENSITIVITY = 60.0f;
    constexpr float SPATIAL_NOISE_OFFSET_FACTOR = 0.08f;
    constexpr int SPATIAL_SEARCH_RADIUS = 0;
    constexpr float MIN_SPATIAL_CONF_FOR_DFT = 0.5f;
}

// =======================================================================================
// === FUNGSI HELPER YANG TELAH DISEMPURNAKAN (LEBIH GENERIK DAN AKURAT)            ===
// =======================================================================================
static cv::Mat generate_pyramid_guidance_map(
    const cv::Mat &current_image_gray_full,
    const cv::Mat &reference_image_gray_full,
    int tile_h, int tile_w, int search_radius,
    float motion_sensitivity, float noise_offset_factor, float global_estimated_noise_sigma)
{
    using namespace MotionMetricsConfig;
    using namespace MotionMatching;

    // --- Tahap A: Piramida Level 1 (1/4) - Fondasi Paling Kasar ---
    cv::Mat current_image_gray_half, reference_image_gray_half;
    cv::pyrDown(current_image_gray_full, current_image_gray_half);
    cv::pyrDown(reference_image_gray_full, reference_image_gray_half);

    cv::Mat current_image_gray_quarter, reference_image_gray_quarter;
    cv::pyrDown(current_image_gray_half, current_image_gray_quarter);
    cv::pyrDown(reference_image_gray_half, reference_image_gray_quarter);

    // <<< PENYEMPURNAAN BARU: Tambahkan Gaussian Blur untuk stabilitas >>>
    cv::Mat blurred_current_quarter, blurred_reference_quarter;
    // Kernel (3,3) dan sigma 0.8 adalah titik awal yang baik.
    cv::GaussianBlur(current_image_gray_quarter, blurred_current_quarter, cv::Size(3, 3), 0.8);
    cv::GaussianBlur(reference_image_gray_quarter, blurred_reference_quarter, cv::Size(3, 3), 0.8);
    // Sekarang, gunakan versi yang sudah di-blur untuk semua perhitungan di level 1/4.

    cv::Mat confidence_map_quarter(current_image_gray_quarter.size(), CV_32FC1, cv::Scalar(0.0f));
    int tile_h_quarter = std::max(1, tile_h / 4);
    int tile_w_quarter = std::max(1, tile_w / 4);
    int search_radius_quarter = search_radius / 4;

#pragma omp parallel for schedule(static)
    for (int r_q = 0; r_q < blurred_current_quarter.rows; r_q += tile_h_quarter)
    {
        MBMBuffers buffers_q;
        for (int c_q = 0; c_q < blurred_current_quarter.cols; c_q += tile_w_quarter)
        {
            int current_w = std::min(tile_w_quarter, blurred_current_quarter.cols - c_q);
            int current_h = std::min(tile_h_quarter, blurred_current_quarter.rows - r_q);
            if (current_w <= 0 || current_h <= 0)
                continue;

            buffers_q.diff_workspace.create(current_h, current_w, CV_32FC1);
            buffers_q.grad_x.create(current_h, current_w, CV_32F);
            buffers_q.grad_y.create(current_h, current_w, CV_32F);
            buffers_q.grad_mag_current.create(current_h, current_w, CV_32FC1);

            cv::Rect roi_q(c_q, r_q, current_w, current_h);
            // Gunakan gambar yang sudah di-blur untuk perbandingan
            BlockMatchResult res_q = find_best_block_match_mad(blurred_current_quarter(roi_q), blurred_reference_quarter, r_q, c_q, search_radius_quarter, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_q);
            float conf_q = res_q.success ? calculate_match_confidence(res_q, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;
            confidence_map_quarter(roi_q).setTo(cv::Scalar(conf_q));
        }
    }

    // --- Tahap B: Piramida Level 2 (1/2) - Penyempurnaan Menengah (Tidak Berubah) ---
    // Logika di tahap ini tidak perlu diubah. Ia sudah menerima hasil yang lebih stabil dari tahap A.
    cv::Mat guidance_map_for_half;
    cv::resize(confidence_map_quarter, guidance_map_for_half, current_image_gray_half.size(), 0, 0, cv::INTER_LINEAR);

    cv::Mat confidence_map_half(current_image_gray_half.size(), CV_32FC1, cv::Scalar(0.0f));
    int tile_h_half = std::max(1, tile_h / 2);
    int tile_w_half = std::max(1, tile_w / 2);
    int search_radius_half = search_radius / 2;

#pragma omp parallel for schedule(static)
    for (int r_h = 0; r_h < current_image_gray_half.rows; r_h += tile_h_half)
    {
        MBMBuffers buffers_h;
        for (int c_h = 0; c_h < current_image_gray_half.cols; c_h += tile_h_half)
        {
            int current_w = std::min(tile_w_half, current_image_gray_half.cols - c_h);
            int current_h = std::min(tile_h_half, current_image_gray_half.rows - r_h);
            if (current_w <= 0 || current_h <= 0)
                continue;

            buffers_h.diff_workspace.create(current_h, current_w, CV_32FC1);
            buffers_h.grad_x.create(current_h, current_w, CV_32F);
            buffers_h.grad_y.create(current_h, current_w, CV_32F);
            buffers_h.grad_mag_current.create(current_h, current_w, CV_32FC1);

            cv::Rect roi_h(c_h, r_h, current_w, current_h);
            BlockMatchResult res_h = find_best_block_match_mad(current_image_gray_half(roi_h), reference_image_gray_half, r_h, c_h, search_radius_half, GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, buffers_h);
            float local_conf_h = res_h.success ? calculate_match_confidence(res_h, global_estimated_noise_sigma, motion_sensitivity, noise_offset_factor) : 0.0f;

            cv::Scalar mean_guidance_scalar = cv::mean(guidance_map_for_half(roi_h));
            float guidance_conf = static_cast<float>(mean_guidance_scalar[0]);

            confidence_map_half(roi_h).setTo(cv::Scalar(local_conf_h * guidance_conf));
        }
    }

    // --- Tahap C: Upscale peta level 2 menjadi peta panduan akhir (Tidak Berubah) ---
    cv::Mat guidance_confidence_map_final;
    cv::resize(confidence_map_half, guidance_confidence_map_final, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);

    return guidance_confidence_map_final;
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
        int block_h, int block_w,
        float dft_wiener_c_factor)
    {
        using namespace MotionMetricsConfig;

        // --- Bagian 1: Inisialisasi dan Persiapan Awal (Tidak Berubah) ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h_img <= 0 || w_img <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            (block_h <= 0 && tile_h > 0 && block_w > 0) || (block_w <= 0 && tile_w > 0 && block_h > 0))
        {
            return;
        }
        // ... (sisa inisialisasi, cvtColor, dll. tetap sama) ...
        int mat_type_color = CV_32FC(channels);
        if (mat_type_color == 0 && channels > 0)
            return;
        cv::Mat final_image_sum_mat(h_img, w_img, mat_type_color, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, mat_type_color, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat_full(h_img, w_img, mat_type_color, const_cast<float *>(reference_image_ptr));
        cv::Mat current_image_gray_full, reference_image_gray_full;
        if (channels > 1)
        {
            cv::Mat temp_curr_gray, temp_ref_gray;
            cv::cvtColor(current_image_mat, temp_curr_gray, cv::COLOR_BGR2GRAY);
            cv::cvtColor(reference_image_mat_full, temp_ref_gray, cv::COLOR_BGR2GRAY);
            temp_curr_gray.convertTo(current_image_gray_full, CV_32FC1);
            temp_ref_gray.convertTo(reference_image_gray_full, CV_32FC1);
        }
        else
        {
            current_image_mat.convertTo(current_image_gray_full, CV_32FC1);
            reference_image_mat_full.convertTo(reference_image_gray_full, CV_32FC1);
        }
        CV_Assert(!current_image_gray_full.empty() && !reference_image_gray_full.empty());
        float global_estimated_noise_sigma = 0.015f;
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3)
        {
#ifdef TILE_NOISE_ESTIMATION_HPP
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
#endif
        }
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        // --- Bagian 2: Menghasilkan Peta Panduan dengan Memanggil Fungsi Helper ---
        cv::Mat guidance_confidence_map_final = generate_pyramid_guidance_map(
            current_image_gray_full, reference_image_gray_full,
            tile_h, tile_w, SPATIAL_SEARCH_RADIUS,
            SPATIAL_MOTION_SENSITIVITY, SPATIAL_NOISE_OFFSET_FACTOR, global_estimated_noise_sigma);

#pragma omp parallel

        {
            cv::Mat thread_block_confidences;
            MotionMerging::DFTBuffers dft_buffers_th;
            MotionMatching::MBMBuffers mbm_buffers_th;
            cv::Mat thread_merged_tile_data;

#pragma omp for collapse(2) schedule(guided)
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
                    const cv::Mat reference_tile_color_data_for_dft = reference_image_mat_full(tile_roi);
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));
                    const cv::Mat current_tile_gray_for_mbm = current_image_gray_full(tile_roi);
                    const cv::Mat reference_tile_gray_for_mbm = reference_image_gray_full(tile_roi);

                    bool tile_data_valid = !current_tile_color_data.empty() && !reference_tile_color_data_for_dft.empty() &&
                                           !current_tile_gray_for_mbm.empty() && !reference_tile_gray_for_mbm.empty();
                    if (!tile_data_valid)
                        continue;

                    int merged_tile_type = CV_32FC(channels);
                    if (thread_merged_tile_data.rows != tile_h || thread_merged_tile_data.cols != tile_w || thread_merged_tile_data.type() != merged_tile_type)
                    {
                        thread_merged_tile_data.create(tile_h, tile_w, merged_tile_type);
                    }

                    int actual_block_h = (block_h > 0) ? block_h : tile_h;
                    int actual_block_w = (block_w > 0) ? block_w : tile_w;
                    if (mbm_buffers_th.diff_workspace.empty() || mbm_buffers_th.diff_workspace.rows < actual_block_h || mbm_buffers_th.diff_workspace.cols < actual_block_w)
                    {
                        mbm_buffers_th.diff_workspace.create(actual_block_h, actual_block_w, CV_32FC1);
                        mbm_buffers_th.grad_x.create(actual_block_h, actual_block_w, CV_32F);
                        mbm_buffers_th.grad_y.create(actual_block_h, actual_block_w, CV_32F);
                        mbm_buffers_th.grad_mag_current.create(actual_block_h, actual_block_w, CV_32FC1);
                    }

                    int num_blocks_h = (actual_block_h > 0 && tile_h > 0) ? (tile_h + actual_block_h - 1) / actual_block_h : 0;
                    int num_blocks_w = (actual_block_w > 0 && tile_w > 0) ? (tile_w + actual_block_w - 1) / actual_block_w : 0;
                    if (num_blocks_h == 0 || num_blocks_w == 0)
                        continue;
                    if (thread_block_confidences.rows != num_blocks_h || thread_block_confidences.cols != num_blocks_w || thread_block_confidences.type() != CV_32FC1)
                    {
                        thread_block_confidences.create(num_blocks_h, num_blocks_w, CV_32FC1);
                    }
                    thread_block_confidences.setTo(cv::Scalar(0.0f));

                    // --- TAHAP 1: PERHITUNGAN BERAT TANPA SINKRONISASI ---
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

                            cv::Rect block_roi_local(block_local_c_start, block_local_r_start, current_block_w_dim, current_block_h_dim);
                            const cv::Mat current_block_color_orig = current_tile_color_data(block_roi_local);
                            const cv::Mat reference_block_color_for_dft_roi = reference_tile_color_data_for_dft(block_roi_local);
                            cv::Mat target_merged_submat = thread_merged_tile_data(block_roi_local);
                            const cv::Mat current_block_gray_for_mbm = current_tile_gray_for_mbm(block_roi_local);
                            const cv::Mat reference_block_gray_for_mbm_direct = reference_tile_gray_for_mbm(block_roi_local);

                            if (current_block_color_orig.empty() || reference_block_color_for_dft_roi.empty() ||
                                current_block_gray_for_mbm.empty() || reference_block_gray_for_mbm_direct.empty())
                            {
                                thread_block_confidences.at<float>(bh_idx, bw_idx) = 0.0f;
                                if (!current_block_color_orig.empty())
                                    current_block_color_orig.copyTo(target_merged_submat);
                                else
                                {
                                    if (!target_merged_submat.empty())
                                        target_merged_submat.setTo(cv::Scalar::all(0.0f));
                                }
                                continue;
                            }

                            float spatial_confidence = 0.0f;
                            MotionMatching::BlockMatchResult mbm_result =
                                MotionMatching::find_best_block_match_mad(
                                    current_block_gray_for_mbm, reference_block_gray_for_mbm_direct,
                                    0, 0, SPATIAL_SEARCH_RADIUS,
                                    GRADIENT_WEIGHT_FACTOR, STABILITY_EPSILON, mbm_buffers_th);
                            if (mbm_result.success)
                            {
                                spatial_confidence = MotionMatching::calculate_match_confidence(
                                    mbm_result, global_estimated_noise_sigma,
                                    SPATIAL_MOTION_SENSITIVITY, SPATIAL_NOISE_OFFSET_FACTOR);
                            }
                            spatial_confidence = std::max(0.0f, std::min(1.0f, spatial_confidence));

                            float dft_confidence = 0.0f;
                            if (spatial_confidence > MIN_SPATIAL_CONF_FOR_DFT)
                            {
                                if (channels == 1)
                                {
                                    MotionMerging::FrequencyMergeResult dft_res_gray =
                                        MotionMerging::merge_blocks_frequency_domain(
                                            current_block_color_orig, reference_block_color_for_dft_roi,
                                            global_estimated_noise_sigma,
                                            dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                                    if (dft_res_gray.success && !dft_res_gray.merged_block_gray.empty())
                                    {
                                        dft_res_gray.merged_block_gray.copyTo(target_merged_submat);
                                        dft_confidence = dft_res_gray.merge_confidence;
                                    }
                                    else
                                    {
                                        current_block_color_orig.copyTo(target_merged_submat);
                                        dft_confidence = 0.05f;
                                    }
                                }
                                else
                                {
                                    std::vector<cv::Mat> current_ch_vec, ref_ch_vec, merged_ch_vec;
                                    cv::split(current_block_color_orig, current_ch_vec);
                                    cv::split(reference_block_color_for_dft_roi, ref_ch_vec);
                                    merged_ch_vec.resize(channels);
                                    float total_dft_conf = 0.0f;
                                    int successful_dft_ch = 0;
                                    for (int ch_idx = 0; ch_idx < channels; ++ch_idx)
                                    {
                                        MotionMerging::FrequencyMergeResult dft_res_ch =
                                            MotionMerging::merge_blocks_frequency_domain(
                                                current_ch_vec[ch_idx], ref_ch_vec[ch_idx],
                                                global_estimated_noise_sigma,
                                                dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                                        if (dft_res_ch.success && !dft_res_ch.merged_block_gray.empty())
                                        {
                                            merged_ch_vec[ch_idx] = dft_res_ch.merged_block_gray;
                                            total_dft_conf += dft_res_ch.merge_confidence;
                                            successful_dft_ch++;
                                        }
                                        else
                                        {
                                            current_ch_vec[ch_idx].copyTo(merged_ch_vec[ch_idx]);
                                        }
                                    }
                                    bool can_merge = merged_ch_vec.size() == channels;
                                    for (const auto &c_mat : merged_ch_vec)
                                    {
                                        if (c_mat.empty())
                                        {
                                            can_merge = false;
                                            break;
                                        }
                                    }
                                    if (can_merge)
                                    {
                                        try
                                        {
                                            cv::merge(merged_ch_vec, target_merged_submat);
                                        }
                                        catch (const cv::Exception &)
                                        {
                                            current_block_color_orig.copyTo(target_merged_submat);
                                            successful_dft_ch = 0;
                                        }
                                    }
                                    else
                                    {
                                        current_block_color_orig.copyTo(target_merged_submat);
                                        successful_dft_ch = 0;
                                    }
                                    dft_confidence = (successful_dft_ch > 0) ? (total_dft_conf / successful_dft_ch) : 0.0f;
                                }
                            }
                            else
                            {
                                current_block_color_orig.copyTo(target_merged_submat);
                                dft_confidence = 0.0f;
                            }

                            float final_block_confidence = spatial_confidence * dft_confidence;
                            thread_block_confidences.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, final_block_confidence));
                        }
                    }

                    // --- TAHAP 2: AKUMULASI KE BUFFER GLOBAL DENGAN ATOMIC ---
                    for (int y_tile = 0; y_tile < tile_h; ++y_tile)
                    {
                        const float *merged_tile_row = thread_merged_tile_data.ptr<const float>(y_tile);
                        const float *base_window_row = base_window_tile_mat.ptr<const float>(y_tile);
                        int gy = r + y_tile;
                        if (gy >= h_img)
                            continue;

                        float *global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                        float *global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);

                        for (int x_tile = 0; x_tile < tile_w; ++x_tile)
                        {
                            int gx = c + x_tile;
                            if (gx >= w_img)
                                continue;

                            // Dapatkan confidence blok yang sesuai untuk piksel ini
                            int bh_idx_eff = (actual_block_h > 0) ? std::min(y_tile / actual_block_h, num_blocks_h - 1) : 0;
                            int bw_idx_eff = (actual_block_w > 0) ? std::min(x_tile / actual_block_w, num_blocks_w - 1) : 0;
                            float block_confidence = thread_block_confidences.at<float>(bh_idx_eff, bw_idx_eff);

                            // Hitung bobot akhir untuk piksel ini
                            float base_win_val = base_window_row[x_tile];
                            float pixel_weight = base_win_val * block_confidence;

                            // Hanya lakukan update jika bobotnya signifikan
                            if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                            {
// Operasi atomik hanya dipanggil di sini, di akhir pipeline untuk satu tile
#pragma omp atomic update
                                global_weight_sum_row[gx] += pixel_weight;

                                int merged_pixel_idx_local = x_tile * channels;
                                int global_pixel_idx_global = gx * channels;
                                for (int ch_idx = 0; ch_idx < channels; ++ch_idx)
                                {
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