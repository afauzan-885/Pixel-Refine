// block_matching.cpp

#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>
#ifdef _MSC_VER
#include <intrin.h>
#else
#include <immintrin.h>
#endif

namespace MotionMatching
{
    // Semua fungsi internal untuk menghitung skor MAD (plain, weighted, AVX2)
    // masih sangat relevan dan dipertahankan seperti adanya.
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
        
        static inline float horizontal_add_m256(__m256 reg) {
            __m128 lo = _mm256_castps256_ps128(reg);
            __m128 hi = _mm256_extractf128_ps(reg, 1);
            __m128 sum = _mm_add_ps(lo, hi);
            sum = _mm_hadd_ps(sum, sum);
            sum = _mm_hadd_ps(sum, sum);
            return _mm_cvtss_f32(sum);
        }

        static float calculate_noise_motion_aware_weighted_mad_avx2(
            const cv::Mat &block1_gray, const cv::Mat &block2_gray, const cv::Mat &grad_mag_block1,
            const cv::Mat &abs_diff_block, float noise_level, float noise_threshold,
            float diff_threshold, float grad_weight_factor, float stab_epsilon)
        {
            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;
            const int avx_cols = cols - (cols % 8);
            __m256 avx_weighted_sum = _mm256_setzero_ps();
            __m256 avx_total_weight = _mm256_setzero_ps();
            const __m256 v_adaptive_noise_thresh = _mm256_set1_ps(std::max(noise_threshold, noise_level * 0.1f));
            const __m256 v_adaptive_diff_thresh = _mm256_set1_ps(std::max(diff_threshold, noise_level * 0.05f));
            const __m256 v_grad_weight_factor = _mm256_set1_ps(grad_weight_factor);
            const __m256 v_1_0 = _mm256_set1_ps(1.0f), v_1_5 = _mm256_set1_ps(1.5f), v_0_5 = _mm256_set1_ps(0.5f);
            const __m256 v_0_3 = _mm256_set1_ps(0.3f), v_0_4 = _mm256_set1_ps(0.4f);
            const __m256 v_4_0_times_adt = _mm256_mul_ps(v_adaptive_diff_thresh, _mm256_set1_ps(4.0f));
            const __m256 v_sign_mask = _mm256_set1_ps(-0.0f);

            for (int y = 0; y < rows; ++y) {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y), *__restrict ptr2 = block2_gray.ptr<float>(y);
                const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y), *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
                for (int x = 0; x < avx_cols; x += 8) {
                    const __m256 v_ptr1 = _mm256_loadu_ps(ptr1 + x), v_ptr2 = _mm256_loadu_ps(ptr2 + x);
                    const __m256 v_mag_ptr = _mm256_loadu_ps(mag_ptr + x), v_diff_ptr = _mm256_loadu_ps(diff_ptr + x);
                    const __m256 v_pixel_diff = _mm256_andnot_ps(v_sign_mask, _mm256_sub_ps(v_ptr1, v_ptr2));
                    __m256 v_noise_weight = v_1_0;
                    if (noise_level > _mm256_cvtss_f32(v_adaptive_noise_thresh)) {
                        const __m256 mask = _mm256_cmp_ps(v_diff_ptr, v_adaptive_diff_thresh, _CMP_LT_OQ);
                        const __m256 weight_low = _mm256_fmadd_ps(v_0_5, _mm256_sub_ps(v_1_0, _mm256_div_ps(v_diff_ptr, v_adaptive_diff_thresh)), v_1_5);
                        const __m256 weight_high = _mm256_fmadd_ps(v_0_4, _mm256_sub_ps(v_1_0, _mm256_min_ps(_mm256_div_ps(v_diff_ptr, v_4_0_times_adt), v_1_0)), v_0_3);
                        v_noise_weight = _mm256_blendv_ps(weight_high, weight_low, mask);
                    }
                    const __m256 v_grad_weight = _mm256_fmadd_ps(v_grad_weight_factor, _mm256_min_ps(v_mag_ptr, v_1_0), v_1_0);
                    const __m256 v_weight = _mm256_mul_ps(v_grad_weight, v_noise_weight);
                    avx_total_weight = _mm256_add_ps(avx_total_weight, v_weight);
                    avx_weighted_sum = _mm256_fmadd_ps(v_pixel_diff, v_weight, avx_weighted_sum);
                }
            }

            float total_weight = horizontal_add_m256(avx_total_weight);
            float weighted_sum = horizontal_add_m256(avx_weighted_sum);
            
            if (avx_cols < cols) {
                 const float adaptive_noise_threshold = std::max(noise_threshold, noise_level * 0.1f);
                 const float adaptive_diff_threshold = std::max(diff_threshold, noise_level * 0.05f);
                 for (int y = 0; y < rows; ++y) {
                    const float *__restrict ptr1 = block1_gray.ptr<float>(y), *__restrict ptr2 = block2_gray.ptr<float>(y);
                    const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y), *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
                    for (int x = avx_cols; x < cols; ++x) {
                        const float pixel_diff = std::abs(ptr1[x] - ptr2[x]);
                        float noise_weight = 1.0f;
                        if (noise_level > adaptive_noise_threshold) {
                             if (diff_ptr[x] < adaptive_diff_threshold) {
                                noise_weight = 1.5f + 0.5f * (1.0f - diff_ptr[x] / adaptive_diff_threshold);
                            } else {
                                const float ratio = std::min(diff_ptr[x] / (adaptive_diff_threshold * 4.0f), 1.0f);
                                noise_weight = 0.3f + 0.4f * (1.0f - ratio);
                            }
                        }
                        const float normalized_grad = std::min(mag_ptr[x], 1.0f);
                        const float grad_weight = 1.0f + grad_weight_factor * normalized_grad;
                        const float weight = grad_weight * noise_weight;
                        total_weight += weight;
                        weighted_sum += pixel_diff * weight;
                    }
                }
            }
            return (total_weight <= stab_epsilon) ? calculate_plain_mad_32f(block1_gray, block2_gray) : (weighted_sum / total_weight);
        }

        static float calculate_noise_motion_aware_weighted_mad(
            const cv::Mat &block1_gray, const cv::Mat &block2_gray, const cv::Mat &grad_mag_block1,
            const cv::Mat &abs_diff_block, float noise_level, float noise_threshold,
            float diff_threshold, float grad_weight_factor, float stab_epsilon)
        {
#ifdef __AVX2__
            if (block1_gray.cols >= 8 && block1_gray.isContinuous() && block2_gray.isContinuous() && grad_mag_block1.isContinuous() && abs_diff_block.isContinuous()) {
                return calculate_noise_motion_aware_weighted_mad_avx2(block1_gray, block2_gray, grad_mag_block1, abs_diff_block,
                    noise_level, noise_threshold, diff_threshold, grad_weight_factor, stab_epsilon);
            }
#endif
            const int rows = block1_gray.rows, cols = block1_gray.cols;
            float weighted_sum = 0.0f, total_weight = 0.0f;
            const float adaptive_noise_threshold = std::max(noise_threshold, noise_level * 0.1f);
            const float adaptive_diff_threshold = std::max(diff_threshold, noise_level * 0.05f);
            for (int y = 0; y < rows; ++y) {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y), *__restrict ptr2 = block2_gray.ptr<float>(y);
                const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y), *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
#pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < cols; ++x) {
                    const float pixel_diff = std::abs(ptr1[x] - ptr2[x]);
                    float noise_weight = 1.0f;
                    if (noise_level > adaptive_noise_threshold) {
                        if (diff_ptr[x] < adaptive_diff_threshold) {
                            noise_weight = 1.5f + 0.5f * (1.0f - diff_ptr[x] / adaptive_diff_threshold);
                        } else {
                            const float ratio = std::min(diff_ptr[x] / (adaptive_diff_threshold * 4.0f), 1.0f);
                            noise_weight = 0.3f + 0.4f * (1.0f - ratio);
                        }
                    }
                    const float normalized_grad = std::min(mag_ptr[x], 1.0f);
                    const float grad_weight = 1.0f + grad_weight_factor * normalized_grad;
                    const float weight = grad_weight * noise_weight;
                    total_weight += weight;
                    weighted_sum += pixel_diff * weight;
                }
            }
            return (total_weight <= stab_epsilon) ? calculate_plain_mad_32f(block1_gray, block2_gray) : (weighted_sum / total_weight);
        }
    } // namespace Internal


    // --- MODIFIKASI: Implementasi fungsi baru yang disederhanakan ---
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

        const bool use_plain = (std::abs(gradient_weight_factor) < stability_epsilon || bh < 3 || bw < 3);

        cv::Mat grad_mag;
        if (!use_plain)
        {
            CV_Assert(buffers.grad_x.rows >= bh && buffers.grad_x.cols >= bw);
            CV_Assert(buffers.grad_y.rows >= bh && buffers.grad_y.cols >= bw);
            CV_Assert(buffers.grad_mag_current.rows >= bh && buffers.grad_mag_current.cols >= bw);

            cv::Mat grad_x = buffers.grad_x(cv::Rect(0, 0, bw, bh));
            cv::Mat grad_y = buffers.grad_y(cv::Rect(0, 0, bw, bh));
            grad_mag = buffers.grad_mag_current(cv::Rect(0, 0, bw, bh));

            cv::Sobel(current_tile_gray, grad_x, CV_32F, 1, 0, 3, 1, 0, cv::BORDER_REPLICATE);
            cv::Sobel(current_tile_gray, grad_y, CV_32F, 0, 1, 3, 1, 0, cv::BORDER_REPLICATE);
            cv::magnitude(grad_x, grad_y, grad_mag);
        }

        float noise_level = global_noise_sigma; // Jauh lebih cepat!

        const float noise_threshold = std::max(0.01f, noise_level * 0.2f);
        const float diff_threshold = std::max(0.005f, noise_level * 0.1f);
        
        // Siapkan workspace untuk `absdiff`
        if (buffers.diff_workspace.rows < bh || buffers.diff_workspace.cols < bw ||
            buffers.diff_workspace.type() != CV_32FC1)
        {
            buffers.diff_workspace = cv::Mat(cv::Size(bw, bh), CV_32FC1);
        }
        cv::Mat abs_diff_block = buffers.diff_workspace(cv::Rect(0, 0, bw, bh));
        cv::absdiff(current_tile_gray, reference_tile_gray, abs_diff_block);

        // Langsung hitung skor, TIDAK ADA LOOP PENCARIAN
        if (use_plain)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            result.mad_score = Internal::calculate_noise_motion_aware_weighted_mad(
                current_tile_gray, reference_tile_gray, grad_mag, abs_diff_block,
                noise_level, // <--- Gunakan noise_level dari parameter
                noise_threshold, diff_threshold,
                gradient_weight_factor, stability_epsilon);
        }

        result.success = true;
        return result;
    }

} // namespace MotionMatching