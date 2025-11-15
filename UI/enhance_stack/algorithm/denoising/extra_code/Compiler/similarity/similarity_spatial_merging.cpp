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

        if (!weight_map_sum_ptr)
            return;

        float global_estimated_noise_sigma = precomputed_ref_noise_sigma;

        // Adaptasi sensitivitas berdasarkan noise
        float adaptation_factor = 1.0f - std::min(global_estimated_noise_sigma / 0.1f, 1.0f);

        const float MAX_SENSITIVITY_BOOST = 0.00f;
        const float MAX_OFFSET_REDUCTION = 0.00f;

        float current_aggression = adaptation_factor;

        float adapted_motion_sensitivity = motion_sensitivity * (1.0f + MAX_SENSITIVITY_BOOST * current_aggression);
        float adapted_noise_offset_factor = noise_offset_factor * (1.0f - MAX_OFFSET_REDUCTION * current_aggression);

        /// =================================================================================
        // === BAGIAN B: ANALISIS SKALA KASAR (DENGAN FFT & MULTI-HIPOTESIS)           ===
        // =================================================================================
        {
            const int tile_h_fine = tile_h;
            const int tile_w_fine = tile_w;

            // --- Bungkus pointer Python sebagai cv::Mat tanpa alokasi ulang ---
            cv::Mat current_image_gray(h_img, w_img, CV_32FC1, (void *)current_image_ptr);
            cv::Mat reference_image_gray(h_img, w_img, CV_32FC1, (void *)reference_image_ptr);
            cv::Mat stability_map_mat;
            if (stability_map_ptr != nullptr)
                stability_map_mat = cv::Mat(h_img, w_img, CV_32FC1, (void *)stability_map_ptr);

            // --- Tentukan jumlah level piramida ---
            // Target: Maksimal 4 level (Indeks 0, 1, 2, 3)
            int max_level = 0;
            int temp_h = h_img, temp_w = w_img;
            while (temp_h >= tile_h_fine * 4 && temp_w >= tile_w_fine * 4)
            {
                temp_h /= 2;
                temp_w /= 2;
                max_level++;
            }
            // Batasi hingga 4 level: std::min(max_level, 3) + 1
            const int num_pyramid_levels = std::min(max_level, 3) + 1;

            // --- Bangun piramida gambar (langsung dari Mat di atas) ---
            std::vector<cv::Mat> current_pyramid, reference_pyramid;
            current_pyramid.reserve(num_pyramid_levels);
            reference_pyramid.reserve(num_pyramid_levels);

            current_pyramid.push_back(current_image_gray);
            reference_pyramid.push_back(reference_image_gray);
            for (int i = 0; i < num_pyramid_levels - 1; ++i)
            {
                cv::Mat next_current, next_ref;
                cv::pyrDown(current_pyramid.back(), next_current);
                cv::pyrDown(reference_pyramid.back(), next_ref);
                current_pyramid.push_back(next_current);
                reference_pyramid.push_back(next_ref);
            }

            // [0] Coarsest, [N-1] Finest (Full Res)
            std::reverse(current_pyramid.begin(), current_pyramid.end());
            std::reverse(reference_pyramid.begin(), reference_pyramid.end());

            // --- Peta panduan dimulai dari ukuran level terkecil ---
            cv::Mat guidance_map = cv::Mat(
                current_pyramid[0].rows / tile_h_fine,
                current_pyramid[0].cols / tile_w_fine,
                CV_32FC1, cv::Scalar(1.0f));

            // --- Loop dari skala paling kasar ke yang lebih halus (Hanya 1x Tile Size) ---
            for (int level = 0; level < num_pyramid_levels - 1; ++level)
            {
                const cv::Mat &coarse_guidance_grid = guidance_map;
                const cv::Mat &current_img_fine = current_pyramid[level + 1];
                const cv::Mat &ref_img_fine = reference_pyramid[level + 1];

                const int current_tile_h = tile_h_fine;
                const int current_tile_w = tile_w_fine;
                
                const int num_tiles_h = current_img_fine.rows / current_tile_h;
                const int num_tiles_w = current_img_fine.cols / current_tile_w;
                
                if (num_tiles_h == 0 || num_tiles_w == 0)
                {
                    // Lanjutkan dengan meng-upscale guidance_map terakhir ke ukuran resolusi level N+1,
                    // meskipun ini mungkin berarti ukuran gambar terlalu kecil.
                    cv::resize(coarse_guidance_grid, guidance_map, 
                               cv::Size(current_img_fine.cols / current_tile_w, current_img_fine.rows / current_tile_h), 
                               0, 0, cv::INTER_LINEAR);
                    continue;
                }

                cv::Mat current_confidence_grid(num_tiles_h, num_tiles_w, CV_32FC1);

#pragma omp parallel for schedule(dynamic)
                for (int r_tile = 0; r_tile < num_tiles_h; ++r_tile)
                {
                    // Buffer thread-local untuk tile yang dinormalisasi
                    cv::Mat normalized_current_tile_fft;

                    for (int c_tile = 0; c_tile < num_tiles_w; ++c_tile)
                    {
                        cv::Rect roi(c_tile * current_tile_w, r_tile * current_tile_h, current_tile_w, current_tile_h);

                        // --- [MODIFIKASI 1: Normalisasi Lokal untuk FFT] ---
                        equalize_tile_brightness(current_img_fine(roi), ref_img_fine(roi), normalized_current_tile_fft);

                        // *** GUNAKAN FFT dengan tile yang sudah dinormalisasi ***
                        MotionMatching::TileMatchResult res = MotionMatching::calculate_tile_fft(
                            normalized_current_tile_fft, 
                            ref_img_fine(roi),
                            global_estimated_noise_sigma);

                        float local_confidence = res.success
                                                          ? MotionMatching::calculate_match_confidence(
                                                                res, global_estimated_noise_sigma,
                                                                adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                          : 0.0f;

                        // Bimbingan selalu dari grid level N (yang 2x lebih kasar)
                        const int r_tile_coarse = r_tile / 2;
                        const int c_tile_coarse = c_tile / 2;

                        std::vector<float> candidate_guidances;
                        candidate_guidances.reserve(9);
                        for (int dr = -1; dr <= 1; ++dr)
                        {
                            for (int dc = -1; dc <= 1; ++dc)
                            {
                                int nr = r_tile_coarse + dr;
                                int nc = c_tile_coarse + dc;
                                if (nr >= 0 && nr < coarse_guidance_grid.rows && nc >= 0 && nc < coarse_guidance_grid.cols)
                                    candidate_guidances.push_back(coarse_guidance_grid.at<float>(nr, nc));
                            }
                        }
                        if (candidate_guidances.empty())
                            candidate_guidances.push_back(1.0f);

                        float best_multiplied_confidence = 0.0f;
                        for (const float guidance_candidate : candidate_guidances)
                            best_multiplied_confidence = std::max(best_multiplied_confidence, local_confidence * guidance_candidate);

                        current_confidence_grid.at<float>(r_tile, c_tile) = best_multiplied_confidence;
                    }
                } // end omp parallel for

                
                // ==========================================================
                // === MODIFIKASI: REGULARISASI SPASIAL (SPATIAL SMOOTHING) ===
                // ==========================================================
                if (current_confidence_grid.rows >= 3 && current_confidence_grid.cols >= 3)
                {
                    // Menggunakan Gaussian Blur pada CV_32FC1
                    cv::GaussianBlur(current_confidence_grid, current_confidence_grid, cv::Size(3, 3), 0);
                }

                // Update guidance_map untuk iterasi level berikutnya
                guidance_map = current_confidence_grid;
            } // end loop pyramid levels

            // --- Upscale peta panduan final ke resolusi penuh (interpolasi) ---
            cv::Mat final_guidance_map_full_res;
            if (!guidance_map.empty())
            {
                cv::resize(guidance_map, final_guidance_map_full_res, current_image_gray.size(), 0, 0, cv::INTER_CUBIC);
            }
            else
                final_guidance_map_full_res = cv::Mat(h_img, w_img, CV_32FC1, cv::Scalar(1.0f));

            // =================================================================================
            // === TAHAP 2: ANALISIS SKALA HALUS & AKUMULASI FINAL (DENGAN MAD SPATIAL)    ===
            // =================================================================================

            cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
            weight_map_sum_mat.setTo(0.0f);

#pragma omp parallel
            {
                cv::Mat local_weight_tile(tile_h_fine, tile_w_fine, CV_32FC1);

                // Buffer thread-local untuk normalisasi (Sekarang tidak digunakan untuk normalisasi kecerahan,
                // tapi mungkin masih diperlukan jika calculate_tile_mad memodifikasi inputnya,
                // namun biasanya ia hanya digunakan sebagai buffer sementara).
                // Kita ganti namanya agar lebih jelas.
                cv::Mat current_tile_buffer(tile_h_fine, tile_w_fine, CV_32FC1); // Buffer jika diperlukan

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

                        // --- MENGHAPUS Normalisasi Lokal ---
                        // Kita langsung menggunakan sub-region dari gambar abu-abu saat ini.
                        const cv::Mat current_tile_ref = current_image_gray(tile_roi);
                        const cv::Mat reference_tile_ref = reference_image_gray(tile_roi);
                        
                        // Buffer normalized_current_tile_mad sekarang tidak digunakan.

                        // *** GUNAKAN MAD dengan tile gambar asli ***
                        MotionMatching::TileMatchResult mbm_result = MotionMatching::calculate_tile_mad(
                            current_tile_ref, // <-- GUNAKAN TILE GAMBAR ASLI
                            reference_tile_ref,
                            global_estimated_noise_sigma,
                            GRADIENT_WEIGHT_FACTOR,
                            STABILITY_EPSILON,
                            mbm_buffers_fine);

                        float confidence_fine = mbm_result.success
                                                    ? MotionMatching::calculate_match_confidence(
                                                          mbm_result, global_estimated_noise_sigma,
                                                          adapted_motion_sensitivity, adapted_noise_offset_factor)
                                                    : 0.0f;

                        float guidance_confidence = static_cast<float>(cv::mean(final_guidance_map_full_res(tile_roi))[0]);
                        float final_confidence = confidence_fine * guidance_confidence;

                        if (!stability_map_mat.empty())
                            final_confidence *= static_cast<float>(cv::mean(stability_map_mat(tile_roi))[0]);

                        if (final_confidence < 1e-5f)
                            continue;

                        // Namun, mengikuti struktur asli:
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