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

#include <vector>
#include <algorithm>
#include <cmath> // Untuk std::abs

// Fungsi helper inline yang lebih robust menggunakan Median Matching
static inline void equalize_tile_brightness(const cv::Mat &src, const cv::Mat &ref, cv::Mat &dst)
{
    // --- Langkah 1: Persiapan dan Ekstraksi Data ---
    // Total jumlah piksel
    const int num_pixels = src.rows * src.cols;
    if (num_pixels < 20) {
        // Jika terlalu kecil, kembali ke mean atau skip
        src.copyTo(dst);
        return;
    }

    // Gunakan buffer vector thread-local untuk data (lebih cepat di-sort)
    // Untuk efisiensi, asumsikan 'src' dan 'ref' berukuran sama (tile)
    std::vector<float> src_data(num_pixels);
    std::vector<float> ref_data(num_pixels);

    // Salin data piksel dari Mat ke vector
    std::memcpy(src_data.data(), src.data, num_pixels * sizeof(float));
    std::memcpy(ref_data.data(), ref.data, num_pixels * sizeof(float));
    
    // --- Langkah 2: Hitung Median (Robust Metric) ---
    
    // Temukan elemen median (lebih cepat dari sorting penuh)
    auto src_median_it = src_data.begin() + num_pixels / 2;
    std::nth_element(src_data.begin(), src_median_it, src_data.end());
    float median_src = *src_median_it;

    auto ref_median_it = ref_data.begin() + num_pixels / 2;
    std::nth_element(ref_data.begin(), ref_median_it, ref_data.end());
    float median_ref = *ref_median_it;

    // --- Langkah 3: Hitung Gain ---
    // Gunakan median sebagai metrik kecerahan yang robust
    double gain = median_ref / (median_src + 1e-5);

    // --- Langkah 4: Batasi dan Terapkan Gain ---
    // Batasi gain agar tidak terlalu ekstrem
    if (gain < 0.6) gain = 0.6; // Agak kurang agresif di batas bawah (noise)
    if (gain > 1.8) gain = 1.8; // Agak kurang agresif di batas atas (clipping)

    // Terapkan gain jika perubahannya signifikan
    if (std::abs(gain - 1.0) > 0.01)
    {
        // Pastikan 'dst' memiliki ukuran yang sama dengan 'src'
        if (dst.empty() || dst.size() != src.size()) {
             dst.create(src.size(), src.type());
        }
        cv::multiply(src, gain, dst);
    }
    else
    {
        // Jika kecerahan sudah mirip, cukup copy
        src.copyTo(dst);
    }
}

extern "C"
{
    // Struktur data bantu untuk manajemen memori thread-local yang efisien
    struct ThreadBuffers {
        cv::Mat normalized_tile;
        MotionMatching::MBMBuffers mad_buffers;
        
        void ensureSize(int h, int w) {
            if (normalized_tile.empty() || normalized_tile.rows != h || normalized_tile.cols != w) {
                normalized_tile.create(h, w, CV_32FC1);
            }
            if (mad_buffers.diff_workspace.empty() || mad_buffers.diff_workspace.rows != h || mad_buffers.diff_workspace.cols != w) {
                mad_buffers.diff_workspace.create(h, w, CV_32FC1);
                mad_buffers.grad_x.create(h, w, CV_32F);
                mad_buffers.grad_y.create(h, w, CV_32F);
                mad_buffers.grad_mag_current.create(h, w, CV_32FC1);
            }
        }
    };

     void generate_weight_map_jit(
        float *weight_map_sum_ptr,
        const float *current_image_ptr,
        const float *reference_image_ptr,
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

        if (!weight_map_sum_ptr) return;

        float global_estimated_noise_sigma = precomputed_ref_noise_sigma;

        cv::Mat current_image_gray(h_img, w_img, CV_32FC1, (void *)current_image_ptr);
        cv::Mat reference_image_gray(h_img, w_img, CV_32FC1, (void *)reference_image_ptr);
        cv::Mat stability_map_mat;
        if (stability_map_ptr != nullptr)
            stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, (void *)stability_map_ptr);

        // =================================================================================
        // === TAHAP 1: ANALISIS SKALA KASAR (COARSE ANALYSIS - FFT)                   ===
        // =================================================================================
        
        const int tile_h_fine = tile_h;
        const int tile_w_fine = tile_w;

        // Tentukan jumlah level piramida
        int num_pyramid_levels = 1;
        if (h_img / 2 >= tile_h_fine && w_img / 2 >= tile_w_fine) {
            num_pyramid_levels++;
            if (h_img / 4 >= tile_h_fine && w_img / 4 >= tile_w_fine) {
                num_pyramid_levels++;
            }
        }

        // Bangun piramida
        std::vector<cv::Mat> current_pyramid, reference_pyramid;
        current_pyramid.reserve(num_pyramid_levels);
        reference_pyramid.reserve(num_pyramid_levels);

        current_pyramid.push_back(current_image_gray);
        reference_pyramid.push_back(reference_image_gray);
        for (int i = 0; i < num_pyramid_levels - 1; ++i) {
            cv::Mat next_cur, next_ref;
            cv::pyrDown(current_pyramid.back(), next_cur);
            cv::pyrDown(reference_pyramid.back(), next_ref);
            current_pyramid.push_back(next_cur);
            reference_pyramid.push_back(next_ref);
        }

        std::reverse(current_pyramid.begin(), current_pyramid.end());
        std::reverse(reference_pyramid.begin(), reference_pyramid.end());

        cv::Mat guidance_map = cv::Mat(
            current_pyramid[0].rows / tile_h_fine,
            current_pyramid[0].cols / tile_w_fine,
            CV_32FC1, cv::Scalar(1.0f));

        // Loop dari Skala Kasar -> Halus
        for (int level = 0; level < num_pyramid_levels - 1; ++level)
        {
            const cv::Mat &coarse_guidance_grid = guidance_map;
            const cv::Mat &current_img_fine = current_pyramid[level + 1];
            const cv::Mat &ref_img_fine = reference_pyramid[level + 1];

            const int num_tiles_h = current_img_fine.rows / tile_h_fine;
            const int num_tiles_w = current_img_fine.cols / tile_w_fine;

            if (num_tiles_h == 0 || num_tiles_w == 0) {
                cv::resize(coarse_guidance_grid, guidance_map, 
                       cv::Size(current_img_fine.cols / tile_w_fine, current_img_fine.rows / tile_h_fine),
                       0, 0, cv::INTER_LINEAR);
                continue;
            }

            cv::Mat current_confidence_grid(num_tiles_h, num_tiles_w, CV_32FC1);

    #pragma omp parallel
            {
                // HAPUS: Buffer local_norm_tile tidak diperlukan lagi
                // cv::Mat local_norm_tile; 
                
    #pragma omp for schedule(dynamic)
                for (int r_tile = 0; r_tile < num_tiles_h; ++r_tile)
                {
                    for (int c_tile = 0; c_tile < num_tiles_w; ++c_tile)
                    {
                        cv::Rect roi(c_tile * tile_w_fine, r_tile * tile_h_fine, tile_w_fine, tile_h_fine);

                        // --- MODIFIKASI DISINI ---
                        // HAPUS: equalize_tile_brightness(...)
                        // GANTI: Langsung gunakan current_img_fine(roi) ke dalam FFT
                        
                        MotionMatching::TileMatchResult res = MotionMatching::calculate_tile_fft(
                            current_img_fine(roi), // Input RAW (tanpa ekualisasi)
                            ref_img_fine(roi), 
                            global_estimated_noise_sigma);

                        float local_confidence = res.success ? 
                            MotionMatching::calculate_match_confidence(res, global_estimated_noise_sigma, 
                                                motion_sensitivity, noise_offset_factor) : 0.0f;

                        // 2. Ambil Guidance (Tetap Sama)
                        const int r_coarse = r_tile / 2;
                        const int c_coarse = c_tile / 2;
                        
                        float max_neighbor_guidance = 0.0f;
                        for (int dr = -1; dr <= 1; ++dr) {
                            for (int dc = -1; dc <= 1; ++dc) {
                                int nr = r_coarse + dr;
                                int nc = c_coarse + dc;
                                if (nr >= 0 && nr < coarse_guidance_grid.rows && nc >= 0 && nc < coarse_guidance_grid.cols)
                                    max_neighbor_guidance = std::max(max_neighbor_guidance, coarse_guidance_grid.at<float>(nr, nc));
                            }
                        }
                        if (max_neighbor_guidance == 0.0f && coarse_guidance_grid.empty()) max_neighbor_guidance = 1.0f;

                        // 3. Fusi
                        float combined_conf = local_confidence * max_neighbor_guidance;
                        current_confidence_grid.at<float>(r_tile, c_tile) = combined_conf;
                    }
                }
            } // end omp parallel

            guidance_map = current_confidence_grid;
        }

        // Upscale guidance akhir
        cv::Mat final_guidance_map;
        if (!guidance_map.empty()) {
            cv::resize(guidance_map, final_guidance_map, cv::Size(w_img, h_img), 0, 0, cv::INTER_CUBIC);
        } else {
            final_guidance_map = cv::Mat::ones(h_img, w_img, CV_32FC1);
        }

        // =================================================================================
        // === TAHAP 2: ANALISIS SKALA HALUS (FINE ANALYSIS - MAD) (TETAP SAMA)        ===
        // =================================================================================

        cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
        weight_map_sum_mat.setTo(0.0f);

        const int NUM_LOCKS = omp_get_max_threads() * 8; 
        std::vector<omp_lock_t> locks(NUM_LOCKS);
        for(int i=0; i<NUM_LOCKS; i++) omp_init_lock(&locks[i]);

#pragma omp parallel
        {
            ThreadBuffers t_bufs;
            t_bufs.ensureSize(tile_h_fine, tile_w_fine);
            
            cv::Mat local_weight_tile(tile_h_fine, tile_w_fine, CV_32FC1);
            cv::Mat base_window_tile_mat(tile_h_fine, tile_w_fine, CV_32FC1, const_cast<float *>(base_window_ptr));

#pragma omp for collapse(2) schedule(dynamic)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    int curr_h = std::min(tile_h_fine, h_img - r);
                    int curr_w = std::min(tile_w_fine, w_img - c);
                    if (curr_h <= 0 || curr_w <= 0) continue;

                    cv::Rect valid_roi(c, r, curr_w, curr_h);

                    MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_mad(
                        current_image_gray(valid_roi), 
                        reference_image_gray(valid_roi),
                        global_estimated_noise_sigma,
                        GRADIENT_WEIGHT_FACTOR,
                        STABILITY_EPSILON,
                        t_bufs.mad_buffers);

                    float confidence_fine = mbm_result.success ? 
                        MotionMatching::calculate_match_confidence(mbm_result, global_estimated_noise_sigma,
                                                                motion_sensitivity, noise_offset_factor) : 0.0f;

                    float guidance_val = static_cast<float>(cv::mean(final_guidance_map(valid_roi))[0]);
                    float final_conf = confidence_fine * guidance_val;
                    
                    if (!stability_map_mat.empty()) {
                        float stab_val = stability_map_mat.at<float>(r + curr_h/2, c + curr_w/2);
                        final_conf *= stab_val;
                    }

                    if (final_conf < 1e-6f) continue;

                    if (curr_w == tile_w_fine && curr_h == tile_h_fine) {
                        cv::multiply(base_window_tile_mat, final_conf, local_weight_tile);
                    } else {
                        cv::Mat partial_window = base_window_tile_mat(cv::Rect(0,0,curr_w,curr_h));
                        cv::multiply(partial_window, final_conf, local_weight_tile(cv::Rect(0,0,curr_w,curr_h)));
                    }

                    int lock_idx = (r * NUM_LOCKS) / h_img;
                    if (lock_idx >= NUM_LOCKS) lock_idx = NUM_LOCKS - 1;

                    omp_set_lock(&locks[lock_idx]);
                    
                    int next_lock_idx = ((r + curr_h) * NUM_LOCKS) / h_img;
                    bool double_lock = (next_lock_idx != lock_idx && next_lock_idx < NUM_LOCKS);
                    if (double_lock) omp_set_lock(&locks[next_lock_idx]);

                    cv::add(weight_map_sum_mat(valid_roi), 
                            (curr_w == tile_w_fine && curr_h == tile_h_fine) ? local_weight_tile : local_weight_tile(cv::Rect(0,0,curr_w,curr_h)), 
                            weight_map_sum_mat(valid_roi));

                    if (double_lock) omp_unset_lock(&locks[next_lock_idx]);
                    omp_unset_lock(&locks[lock_idx]);
                }
            }
        }

        for(int i=0; i<NUM_LOCKS; i++) omp_destroy_lock(&locks[i]);
    }
}