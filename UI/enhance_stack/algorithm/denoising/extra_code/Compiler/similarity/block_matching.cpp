// block_matching.cpp

#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>

// Sertakan header yang sesuai untuk intrinsik SIMD
#ifdef _MSC_VER
#else
#include <immintrin.h> 
#endif

namespace MotionMatching
{
    namespace Internal
    {
        static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1);

            const int total_pixels = block1_gray.rows * block1_gray.cols;
            if (total_pixels == 0) return 0.0f;
            
            cv::Mat diff;
            cv::absdiff(block1_gray, block2_gray, diff);
            cv::Scalar sum_scalar = cv::sum(diff);
            
            return static_cast<float>(sum_scalar[0] / total_pixels);
        }

        // --- FUNGSI UTAMA YANG DIMODIFIKASI: Sekarang juga menerima hasil Laplacian ---
        static float calculate_hybrid_gradient_weighted_mad(
            const cv::Mat &block1_gray, const cv::Mat &block2_gray,
            const cv::Mat &grad_x1, const cv::Mat &grad_y1, 
            const cv::Mat &grad_x2, const cv::Mat &grad_y2,
            const cv::Mat &laplacian1, const cv::Mat &laplacian2, // <-- INPUT BARU
            const cv::Mat &abs_diff_block, float noise_level,
            float gradient_weight_factor, float stab_epsilon)
        {
            const int rows = block1_gray.rows, cols = block1_gray.cols;
            float weighted_sum = 0.0f, total_weight = 0.0f;
            
            const float grad_sensitivity = 50.0f;
            const float laplacian_sensitivity = 8.0f; // Laplacian bisa sangat "noisy", jadi sensitivitas lebih rendah
            
            const float adaptive_noise_threshold = std::max(0.01f, noise_level * 0.2f);
            const float adaptive_diff_threshold = std::max(0.005f, noise_level * 0.1f);

            for (int y = 0; y < rows; ++y) {
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
                const float *__restrict gx1_ptr = grad_x1.ptr<float>(y);
                const float *__restrict gy1_ptr = grad_y1.ptr<float>(y);
                const float *__restrict gx2_ptr = grad_x2.ptr<float>(y);
                const float *__restrict gy2_ptr = grad_y2.ptr<float>(y);
                const float *__restrict l1_ptr = laplacian1.ptr<float>(y); // <-- POINTER BARU
                const float *__restrict l2_ptr = laplacian2.ptr<float>(y); // <-- POINTER BARU

                #pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < cols; ++x) {
                    const float pixel_diff = diff_ptr[x];

                    float noise_weight = 1.0f;
                    if (noise_level > adaptive_noise_threshold) {
                        if (pixel_diff < adaptive_diff_threshold) {
                            noise_weight = 1.3f + 0.3f * (1.0f - pixel_diff / adaptive_diff_threshold);
                        } else {
                            const float ratio = std::min(pixel_diff / (adaptive_diff_threshold * 4.0f), 1.0f);
                            noise_weight = 0.3f + 0.4f * (1.0f - ratio);
                        }
                    }

                    // --- 2. Perhitungan Bobot Vektor Gradien (Scharr) ---
                    const float gx1 = gx1_ptr[x], gy1 = gy1_ptr[x];
                    const float gx2 = gx2_ptr[x], gy2 = gy2_ptr[x];

                    const float mag1_sq = gx1 * gx1 + gy1 * gy1;
                    const float mag2_sq = gx2 * gx2 + gy2 * gy2;

                    float structure_weight = 1.0f;
                    if (mag1_sq > stab_epsilon && mag2_sq > stab_epsilon) {
                        const float dot_product = gx1 * gx2 + gy1 * gy2;
                        const float cos_similarity = dot_product / std::sqrt(mag1_sq * mag2_sq);
                        const float avg_mag = (std::sqrt(mag1_sq) + std::sqrt(mag2_sq)) * 0.5f;
                        const float similarity_score = std::max(0.0f, cos_similarity) * avg_mag;
                        structure_weight = 1.0f + gradient_weight_factor * std::tanh(similarity_score * grad_sensitivity);
                    }

                    // --- 3. LOGIKA BARU: Perhitungan Bobot Tekstur (Laplacian) ---
                    const float l1 = l1_ptr[x], l2 = l2_ptr[x];
                    const float laplacian_diff = std::abs(l1 - l2);
                    // Bobot tinggi jika perbedaan Laplacian kecil (tekstur mirip).
                    const float texture_weight = std::exp(-laplacian_diff * laplacian_sensitivity);
                    
                    // --- 4. Bobot Final Gabungan ---
                    // Menggabungkan semua informasi: tepi, tekstur, dan noise.
                    const float final_weight = structure_weight * texture_weight * noise_weight;
                    total_weight += final_weight;
                    weighted_sum += pixel_diff * final_weight;
                }
            }
            return (total_weight <= stab_epsilon) ? calculate_plain_mad_32f(block1_gray, block2_gray) : (weighted_sum / total_weight);
        }
    } // namespace Internal
    

    // --- FUNGSI PUBLIK UTAMA (Dimodifikasi untuk memanggil logika hybrid) ---
    TileMatchResult calculate_tile_similarity(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma, 
        float gradient_weight_factor,
        float stability_epsilon,
        MBMBuffers &buffers)
    {
        TileMatchResult result;

        if (current_tile_gray.empty() || reference_tile_gray.empty() ||
            current_tile_gray.size() != reference_tile_gray.size())
        {
            result.success = false;
            return result;
        }

        const int bh = current_tile_gray.rows;
        const int bw = current_tile_gray.cols;

        // Laplacian, seperti Scharr, membutuhkan kernel 3x3.
        const bool use_plain_mad = (std::abs(gradient_weight_factor) < stability_epsilon || bh < 3 || bw < 3);

        if (use_plain_mad)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            CV_Assert(buffers.grad_x.rows >= bh && buffers.grad_x.cols >= bw);
            CV_Assert(buffers.grad_y.rows >= bh && buffers.grad_y.cols >= bw);
            CV_Assert(buffers.grad_mag_current.rows >= bh && buffers.grad_mag_current.cols >= bw);
            CV_Assert(buffers.diff_workspace.rows >= bh && buffers.diff_workspace.cols >= bw);

            cv::Rect roi(0, 0, bw, bh);
            // Alokasi buffer untuk Scharr (menggunakan buffer yang ada)
            cv::Mat grad_x_current = buffers.grad_x(roi);
            cv::Mat grad_y_current = buffers.grad_y(roi);
            cv::Mat grad_x_ref = buffers.grad_mag_current(roi); 
            cv::Mat grad_y_ref = buffers.diff_workspace(roi);

            // Hitung gradien Scharr (Turunan Pertama)
            cv::Scharr(current_tile_gray, grad_x_current, CV_32F, 1, 0);
            cv::Scharr(current_tile_gray, grad_y_current, CV_32F, 0, 1);
            cv::Scharr(reference_tile_gray, grad_x_ref, CV_32F, 1, 0);
            cv::Scharr(reference_tile_gray, grad_y_ref, CV_32F, 0, 1);
            
            // --- LOGIKA BARU: Hitung Laplacian (Turunan Kedua) ---
            // Kita perlu Mat lokal baru untuk menyimpan hasil Laplacian.
            // Overhead performa sangat kecil.
            cv::Mat laplacian_current(cv::Size(bw, bh), CV_32F);
            cv::Mat laplacian_ref(cv::Size(bw, bh), CV_32F);
            
            // ksize=3 memberikan kernel yang lebih stabil.
            cv::Laplacian(current_tile_gray, laplacian_current, CV_32F, 3);
            cv::Laplacian(reference_tile_gray, laplacian_ref, CV_32F, 3);
            
            // Hitung perbedaan absolut
            cv::Mat abs_diff_block(cv::Size(bw, bh), CV_32FC1);
            cv::absdiff(current_tile_gray, reference_tile_gray, abs_diff_block);

            // Panggil fungsi weighted MAD hybrid yang baru
            result.mad_score = Internal::calculate_hybrid_gradient_weighted_mad(
                current_tile_gray, reference_tile_gray,
                grad_x_current, grad_y_current,
                grad_x_ref, grad_y_ref,
                laplacian_current, laplacian_ref, // <-- Berikan hasil Laplacian
                abs_diff_block,
                global_noise_sigma,
                gradient_weight_factor, stability_epsilon);
        }

        result.success = true;
        return result;
    }

} // namespace MotionMatching