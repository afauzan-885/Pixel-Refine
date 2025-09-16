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
// #include "block_matching.hpp" // Tidak dibutuhkan lagi
#include "spatial_merging.hpp"

namespace MotionMetricsConfig
{
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
}

// =================================================================================
// === FUNGSI HELPER BARU: ANALISIS PIRAMIDA BERBASIS FREKUENSI                  ===
// === Diadopsi dari similarity_spatial_merging.cpp dan diadaptasi untuk DFT   ===
// =================================================================================
static cv::Mat generate_frequency_pyramid_guidance_map(
    const cv::Mat &current_image_gray_full,
    const cv::Mat &reference_image_gray_full,
    int tile_h, int tile_w,
    float global_estimated_noise_sigma,
    float dft_wiener_c_factor)
{
    using namespace MotionMetricsConfig;

    // --- Tentukan jumlah level piramida ---
    int max_level = 0;
    int temp_h = current_image_gray_full.rows, temp_w = current_image_gray_full.cols;
    while (temp_h >= tile_h * 4 && temp_w >= tile_w * 4)
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
    cv::Mat guidance_map = cv::Mat(current_pyramid[0].rows / tile_h, current_pyramid[0].cols / tile_w, CV_32FC1, cv::Scalar(1.0f));

    // --- Loop dari skala paling kasar ke yang lebih halus ---
    for (int level = 0; level < num_pyramid_levels - 1; ++level)
    {
        const cv::Mat &coarse_guidance_grid = guidance_map;
        const cv::Mat &current_img_fine = current_pyramid[level + 1];
        const cv::Mat &ref_img_fine = reference_pyramid[level + 1];

        const int num_tiles_h_fine = current_img_fine.rows / tile_h;
        const int num_tiles_w_fine = current_img_fine.cols / tile_w;
        if (num_tiles_h_fine == 0 || num_tiles_w_fine == 0) {
             cv::Mat temp_guidance_map;
             cv::resize(coarse_guidance_grid, temp_guidance_map, current_img_fine.size(), 0, 0, cv::INTER_LINEAR);
             guidance_map = temp_guidance_map;
             continue;
        }

        cv::Mat fine_confidence_grid(num_tiles_h_fine, num_tiles_w_fine, CV_32FC1);

        #pragma omp parallel for schedule(dynamic)
        for (int r_tile_fine = 0; r_tile_fine < num_tiles_h_fine; ++r_tile_fine)
        {
            MotionMerging::DFTBuffers dft_buffers_pyramid; // Buffer per-thread

            for (int c_tile_fine = 0; c_tile_fine < num_tiles_w_fine; ++c_tile_fine)
            {
                cv::Rect roi_fine(c_tile_fine * tile_w, r_tile_fine * tile_h, tile_w, tile_h);

                // 1. Hitung Confidence Lokal di Level Halus menggunakan DFT
                MotionMerging::FrequencyMergeResult dft_res = MotionMerging::merge_blocks_frequency_domain(
                    current_img_fine(roi_fine), ref_img_fine(roi_fine),
                    global_estimated_noise_sigma, dft_wiener_c_factor,
                    STABILITY_EPSILON, dft_buffers_pyramid);

                float local_confidence_fine = dft_res.success ? dft_res.merge_confidence : 0.0f;

                // 2. Kumpulkan Kandidat (Hipotesis) dari Grid Kasar
                const int r_tile_coarse = r_tile_fine / 2;
                const int c_tile_coarse = c_tile_fine / 2;

                std::vector<float> candidate_guidances;
                candidate_guidances.reserve(9);
                for (int dr = -1; dr <= 1; ++dr) {
                    for (int dc = -1; dc <= 1; ++dc) {
                        int nr = r_tile_coarse + dr;
                        int nc = c_tile_coarse + dc;
                        if (nr >= 0 && nr < coarse_guidance_grid.rows && nc >= 0 && nc < coarse_guidance_grid.cols) {
                            candidate_guidances.push_back(coarse_guidance_grid.at<float>(nr, nc));
                        }
                    }
                }
                if (candidate_guidances.empty()) candidate_guidances.push_back(1.0f);

                // 3. Uji Semua Hipotesis dengan PERKALIAN dan Pilih Hasil MAKSIMUM
                float best_multiplied_confidence = 0.0f;
                for (const float guidance_candidate : candidate_guidances) {
                    float multiplied_confidence = local_confidence_fine * guidance_candidate;
                    if (multiplied_confidence > best_multiplied_confidence) {
                        best_multiplied_confidence = multiplied_confidence;
                    }
                }
                fine_confidence_grid.at<float>(r_tile_fine, c_tile_fine) = best_multiplied_confidence;
            }
        }
        guidance_map = fine_confidence_grid;
    }

    // --- Upscale peta panduan final ke resolusi penuh ---
    cv::Mat final_guidance_map_full_res;
    if (!guidance_map.empty()) {
        cv::resize(guidance_map, final_guidance_map_full_res, current_image_gray_full.size(), 0, 0, cv::INTER_LINEAR);
    } else {
        final_guidance_map_full_res = cv::Mat(current_image_gray_full.size(), CV_32FC1, cv::Scalar(1.0f));
    }

    return final_guidance_map_full_res;
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
        int block_h, int block_w, // Parameter ini tidak lagi digunakan, tapi dipertahankan untuk kompatibilitas API
        float dft_wiener_c_factor)
    {
        using namespace MotionMetricsConfig;

        // --- Bagian 1: Inisialisasi dan Persiapan Awal ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr) return;
        
        cv::Mat final_image_sum_mat(h_img, w_img, CV_32FC(channels), final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h_img, w_img, CV_32FC(channels), const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat_full(h_img, w_img, CV_32FC(channels), const_cast<float *>(reference_image_ptr));
        
        cv::Mat current_image_gray_full, reference_image_gray_full;
        if (channels > 1) {
            cv::cvtColor(current_image_mat, current_image_gray_full, cv::COLOR_BGR2GRAY);
            cv::cvtColor(reference_image_mat_full, reference_image_gray_full, cv::COLOR_BGR2GRAY);
        } else {
            current_image_mat.copyTo(current_image_gray_full);
            reference_image_mat_full.copyTo(reference_image_gray_full);
        }

        float global_estimated_noise_sigma = 0.015f;
        if (reference_image_gray_full.rows >= 3 && reference_image_gray_full.cols >= 3) {
            #ifdef TILE_NOISE_ESTIMATION_HPP
            global_estimated_noise_sigma = NoiseEstimation::estimate_tile_noise_sigma_mad_laplacian(reference_image_gray_full, MAD_TO_SIGMA_FACTOR);
            #endif
        }
        global_estimated_noise_sigma = std::max(0.001f, std::min(0.25f, global_estimated_noise_sigma));

        // --- Bagian 2: (BARU) Menghasilkan Peta Panduan dengan Piramida Berbasis Frekuensi ---
        cv::Mat final_guidance_map_full_res = generate_frequency_pyramid_guidance_map(
            current_image_gray_full, reference_image_gray_full,
            tile_h, tile_w, 
            global_estimated_noise_sigma, dft_wiener_c_factor);
        
        // --- Bagian 3: (DIROMBAK) Akumulasi Final Berbasis DFT dan Peta Panduan ---
        #pragma omp parallel
        {
            MotionMerging::DFTBuffers dft_buffers_th; // Buffer DFT per-thread
            cv::Mat merged_tile_color; // Buffer untuk hasil merge warna
            cv::Mat local_weight_tile(tile_h, tile_w, CV_32FC1); // Buffer untuk bobot lokal

            #pragma omp for collapse(2) schedule(dynamic)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    if (r < 0 || c < 0 || (r + tile_h) > h_img || (c + tile_w) > w_img) continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);

                    // 1. Lakukan penggabungan DFT final pada data berwarna
                    float dft_confidence = 0.0f;
                    
                    if (channels == 1) {
                        MotionMerging::FrequencyMergeResult res = MotionMerging::merge_blocks_frequency_domain(
                            current_image_mat(tile_roi), reference_image_mat_full(tile_roi),
                            global_estimated_noise_sigma, dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                        if (res.success) {
                            merged_tile_color = res.merged_block_gray;
                            dft_confidence = res.merge_confidence;
                        } else {
                            current_image_mat(tile_roi).copyTo(merged_tile_color);
                        }
                    } else { // Handle multi-channel (color)
                        std::vector<cv::Mat> current_ch, ref_ch, merged_ch(channels);
                        cv::split(current_image_mat(tile_roi), current_ch);
                        cv::split(reference_image_mat_full(tile_roi), ref_ch);
                        
                        float total_conf = 0.0f;
                        int successful_ch = 0;
                        for(int ch_idx = 0; ch_idx < channels; ++ch_idx) {
                             MotionMerging::FrequencyMergeResult res = MotionMerging::merge_blocks_frequency_domain(
                                current_ch[ch_idx], ref_ch[ch_idx], global_estimated_noise_sigma,
                                dft_wiener_c_factor, STABILITY_EPSILON, dft_buffers_th);
                             if (res.success) {
                                 merged_ch[ch_idx] = res.merged_block_gray;
                                 total_conf += res.merge_confidence;
                                 successful_ch++;
                             } else {
                                 merged_ch[ch_idx] = current_ch[ch_idx];
                             }
                        }
                        
                        if (successful_ch > 0) {
                            cv::merge(merged_ch, merged_tile_color);
                            dft_confidence = total_conf / successful_ch;
                        } else {
                            current_image_mat(tile_roi).copyTo(merged_tile_color);
                        }
                    }

                    if (merged_tile_color.empty()) continue;

                    // 2. Dapatkan kepercayaan dari peta panduan
                    float guidance_confidence = static_cast<float>(cv::mean(final_guidance_map_full_res(tile_roi))[0]);

                    // 3. Hitung kepercayaan akhir
                    float final_confidence = dft_confidence * guidance_confidence;
                    
                    if (final_confidence < 1e-5f) continue;
                    
                    // 4. Siapkan bobot dan data untuk diakumulasi
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));
                    cv::multiply(base_window_tile_mat, final_confidence, local_weight_tile);

                    cv::Mat weighted_merged_tile;
                    if (channels > 1) {
                        std::vector<cv::Mat> merged_channels;
                        cv::split(merged_tile_color, merged_channels);
                        for(auto& ch : merged_channels) {
                            cv::multiply(ch, local_weight_tile, ch);
                        }
                        cv::merge(merged_channels, weighted_merged_tile);
                    } else {
                        cv::multiply(merged_tile_color, local_weight_tile, weighted_merged_tile);
                    }
                    
                    // 5. Akumulasi ke buffer global dengan critical section
                    #pragma omp critical
                    {
                        cv::add(final_image_sum_mat(tile_roi), weighted_merged_tile, final_image_sum_mat(tile_roi));
                        cv::add(weight_map_sum_mat(tile_roi), local_weight_tile, weight_map_sum_mat(tile_roi));
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