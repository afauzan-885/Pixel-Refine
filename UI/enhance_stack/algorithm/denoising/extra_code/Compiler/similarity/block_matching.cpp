#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>
#include <immintrin.h> // Header utama untuk AVX/AVX2

namespace MotionMatching
{
    namespace Internal
    {
        // Fungsi tidak diubah, sudah cukup optimal
        static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1);

            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;
            const int total_pixels = rows * cols;
            
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
            const cv::Mat &block1_gray,
            const cv::Mat &block2_gray,
            const cv::Mat &grad_mag_block1,
            const cv::Mat &abs_diff_block,
            float noise_level,
            float noise_threshold,
            float diff_threshold,
            float grad_weight_factor,
            float stab_epsilon)
        {
            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;

            // Memproses 8 float (256-bit) per iterasi
            const int avx_cols = cols - (cols % 8);

            // Inisialisasi register AVX untuk akumulasi
            __m256 avx_weighted_sum = _mm256_setzero_ps();
            __m256 avx_total_weight = _mm256_setzero_ps();

            // Inisialisasi register AVX untuk nilai konstan
            const __m256 v_adaptive_noise_thresh = _mm256_set1_ps(std::max(noise_threshold, noise_level * 0.1f));
            const __m256 v_adaptive_diff_thresh = _mm256_set1_ps(std::max(diff_threshold, noise_level * 0.05f));
            const __m256 v_grad_weight_factor = _mm256_set1_ps(grad_weight_factor);
            
            const __m256 v_1_0 = _mm256_set1_ps(1.0f);
            const __m256 v_1_5 = _mm256_set1_ps(1.5f);
            const __m256 v_0_5 = _mm256_set1_ps(0.5f);
            const __m256 v_0_3 = _mm256_set1_ps(0.3f);
            const __m256 v_0_4 = _mm256_set1_ps(0.4f);
            const __m256 v_4_0_times_adt = _mm256_mul_ps(v_adaptive_diff_thresh, _mm256_set1_ps(4.0f));
            const __m256 v_sign_mask = _mm256_set1_ps(-0.0f); // Untuk abs

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y);
                const float *__restrict ptr2 = block2_gray.ptr<float>(y);
                const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y);
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);

                for (int x = 0; x < avx_cols; x += 8)
                {
                    // Load 8 float dari setiap buffer
                    const __m256 v_ptr1 = _mm256_loadu_ps(ptr1 + x);
                    const __m256 v_ptr2 = _mm256_loadu_ps(ptr2 + x);
                    const __m256 v_mag_ptr = _mm256_loadu_ps(mag_ptr + x);
                    const __m256 v_diff_ptr = _mm256_loadu_ps(diff_ptr + x);

                    // const float pixel_diff = std::abs(ptr1[x] - ptr2[x]);
                    const __m256 v_pixel_diff_raw = _mm256_sub_ps(v_ptr1, v_ptr2);
                    const __m256 v_pixel_diff = _mm256_andnot_ps(v_sign_mask, v_pixel_diff_raw); // abs

                    __m256 v_noise_weight = v_1_0; // Default weight
                    if (noise_level > _mm256_cvtss_f32(v_adaptive_noise_thresh))
                    {
                        // Mask untuk if (diff_ptr[x] < adaptive_diff_threshold)
                        const __m256 mask = _mm256_cmp_ps(v_diff_ptr, v_adaptive_diff_thresh, _CMP_LT_OQ);

                        // Cabang "if" (low-difference)
                        const __m256 ratio_low = _mm256_div_ps(v_diff_ptr, v_adaptive_diff_thresh);
                        const __m256 term_low = _mm256_sub_ps(v_1_0, ratio_low);
                        const __m256 weight_low = _mm256_fmadd_ps(v_0_5, term_low, v_1_5);

                        // Cabang "else" (high-difference)
                        const __m256 ratio_high = _mm256_min_ps(_mm256_div_ps(v_diff_ptr, v_4_0_times_adt), v_1_0);
                        const __m256 term_high = _mm256_sub_ps(v_1_0, ratio_high);
                        const __m256 weight_high = _mm256_fmadd_ps(v_0_4, term_high, v_0_3);
                        
                        // Blend hasil berdasarkan mask
                        v_noise_weight = _mm256_blendv_ps(weight_high, weight_low, mask);
                    }

                    // const float normalized_grad = std::min(mag_ptr[x], 1.0f);
                    const __m256 v_normalized_grad = _mm256_min_ps(v_mag_ptr, v_1_0);
                    // const float grad_weight = 1.0f + grad_weight_factor * normalized_grad;
                    const __m256 v_grad_weight = _mm256_fmadd_ps(v_grad_weight_factor, v_normalized_grad, v_1_0);

                    // const float weight = grad_weight * noise_weight;
                    const __m256 v_weight = _mm256_mul_ps(v_grad_weight, v_noise_weight);

                    // Akumulasi
                    avx_total_weight = _mm256_add_ps(avx_total_weight, v_weight);
                    avx_weighted_sum = _mm256_fmadd_ps(v_pixel_diff, v_weight, avx_weighted_sum);
                }
            }

            // Reduksi: jumlahkan hasil dari register AVX ke skalar
            float total_weight = horizontal_add_m256(avx_total_weight);
            float weighted_sum = horizontal_add_m256(avx_weighted_sum);
            
            // Loop sisa untuk piksel yang tidak habis dibagi 8
            if (avx_cols < cols) {
                 const float adaptive_noise_threshold = std::max(noise_threshold, noise_level * 0.1f);
                 const float adaptive_diff_threshold = std::max(diff_threshold, noise_level * 0.05f);

                 for (int y = 0; y < rows; ++y) {
                    const float *__restrict ptr1 = block1_gray.ptr<float>(y);
                    const float *__restrict ptr2 = block2_gray.ptr<float>(y);
                    const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y);
                    const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
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
            
            if (total_weight <= stab_epsilon)
            {
                return calculate_plain_mad_32f(block1_gray, block2_gray);
            }
            
            return weighted_sum / total_weight;
        }

        // --- AKHIR MODIFIKASI ---


        // MODIFIKASI: Fungsi ini sekarang bertindak sebagai dispatcher
        static float calculate_noise_motion_aware_weighted_mad(
            const cv::Mat &block1_gray,
            const cv::Mat &block2_gray,
            const cv::Mat &grad_mag_block1,
            const cv::Mat &abs_diff_block,
            float noise_level,
            float noise_threshold,
            float diff_threshold,
            float grad_weight_factor,
            float stab_epsilon)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      grad_mag_block1.size() == block1_gray.size() &&
                      abs_diff_block.size() == block1_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1 &&
                      grad_mag_block1.type() == CV_32FC1 &&
                      abs_diff_block.type() == CV_32FC1);

#ifdef __AVX2__
            // Panggil versi AVX2 jika lebar kolom memungkinkan dan kode dikompilasi dengan flag AVX2
            // Kita gunakan threshold 8 karena AVX2 memproses 8 float sekaligus
            if (block1_gray.cols >= 8 && block1_gray.isContinuous() && block2_gray.isContinuous() && grad_mag_block1.isContinuous() && abs_diff_block.isContinuous()) {
                return calculate_noise_motion_aware_weighted_mad_avx2(
                    block1_gray, block2_gray, grad_mag_block1, abs_diff_block,
                    noise_level, noise_threshold, diff_threshold, grad_weight_factor, stab_epsilon);
            }
#endif

            // Fallback ke implementasi C++ original jika AVX2 tidak tersedia atau data tidak sesuai
            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;

            float weighted_sum = 0.0f;
            float total_weight = 0.0f;
            
            const float adaptive_noise_threshold = std::max(noise_threshold, noise_level * 0.1f);
            const float adaptive_diff_threshold = std::max(diff_threshold, noise_level * 0.05f);

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict ptr1 = block1_gray.ptr<float>(y);
                const float *__restrict ptr2 = block2_gray.ptr<float>(y);
                const float *__restrict mag_ptr = grad_mag_block1.ptr<float>(y);
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);

#pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < cols; ++x)
                {
                    const float pixel_diff = std::abs(ptr1[x] - ptr2[x]);
                    
                    float noise_weight = 1.0f;
                    if (noise_level > adaptive_noise_threshold)
                    {
                        if (diff_ptr[x] < adaptive_diff_threshold)
                        {
                            noise_weight = 1.5f + 0.5f * (1.0f - diff_ptr[x] / adaptive_diff_threshold);
                        }
                        else
                        {
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

            if (total_weight <= stab_epsilon)
            {
                return calculate_plain_mad_32f(block1_gray, block2_gray);
            }

            return weighted_sum / total_weight;
        }

        // Fungsi ini tidak diubah
        static cv::Point2f refine_subpixel_match(
            const cv::Mat &current_block_gray,
            const cv::Mat &reference_tile_gray,
            int best_r, int best_c,
            float gradient_weight_factor,
            float stability_epsilon)
        {
            const int bh = current_block_gray.rows;
            const int bw = current_block_gray.cols;
            const int rh = reference_tile_gray.rows;
            const int rw = reference_tile_gray.cols;
            
            if (best_r <= 0 || best_r >= rh - bh - 1 ||
                best_c <= 0 || best_c >= rw - bw - 1)
            {
                return cv::Point2f(static_cast<float>(best_c), static_cast<float>(best_r));
            }
            
            float scores[9];
            int idx = 0;
            
            for (int dr = -1; dr <= 1; ++dr)
            {
                for (int dc = -1; dc <= 1; ++dc)
                {
                    cv::Rect roi(best_c + dc, best_r + dr, bw, bh);
                    const cv::Mat ref_block = reference_tile_gray(roi);
                    scores[idx++] = calculate_plain_mad_32f(current_block_gray, ref_block);
                }
            }
            
            const float dx = 0.5f * (scores[5] - scores[3]) / 
                           std::max(scores[3] + scores[5] - 2.0f * scores[4], stability_epsilon);
            const float dy = 0.5f * (scores[7] - scores[1]) / 
                           std::max(scores[1] + scores[7] - 2.0f * scores[4], stability_epsilon);
            
            const float clamped_dx = std::clamp(dx, -0.5f, 0.5f);
            const float clamped_dy = std::clamp(dy, -0.5f, 0.5f);
            
            return cv::Point2f(static_cast<float>(best_c) + clamped_dx, 
                              static_cast<float>(best_r) + clamped_dy);
        }

    } // namespace Internal

    // Fungsi utama tidak perlu diubah karena panggilannya ke fungsi internal sudah dioptimalkan
    BlockMatchResult find_best_block_match_mad(
        const cv::Mat &current_block_gray,
        const cv::Mat &reference_tile_gray,
        int block_r_start_in_ref_tile,
        int block_c_start_in_ref_tile,
        int search_radius,
        float gradient_weight_factor,
        float stability_epsilon,
        MBMBuffers &buffers)
    {
        // ... (seluruh isi fungsi ini tetap sama persis seperti kode asli Anda) ...
        // ... (No changes needed here) ...

        BlockMatchResult result;

        if (current_block_gray.empty() || reference_tile_gray.empty())
        {
            result.success = false;
            return result;
        }

        const int bh = current_block_gray.rows;
        const int bw = current_block_gray.cols;
        const int rh = reference_tile_gray.rows;
        const int rw = reference_tile_gray.cols;

        if (bh <= 0 || bw <= 0 || rh < bh || rw < bw)
        {
            result.success = false;
            return result;
        }

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

            cv::Sobel(current_block_gray, grad_x, CV_32F, 1, 0, 3, 1, 0, cv::BORDER_REPLICATE);
            cv::Sobel(current_block_gray, grad_y, CV_32F, 0, 1, 3, 1, 0, cv::BORDER_REPLICATE);
            cv::magnitude(grad_x, grad_y, grad_mag);
        }

        cv::Scalar mean_val, stddev_val;
        cv::meanStdDev(current_block_gray, mean_val, stddev_val);
        float noise_level = static_cast<float>(stddev_val[0] * 0.5); 
        
        const float noise_threshold = std::max(0.01f, noise_level * 0.2f);
        const float diff_threshold = std::max(0.005f, noise_level * 0.1f);

        const int r0 = std::max(0, block_r_start_in_ref_tile - search_radius);
        const int r1 = std::min(rh - bh, block_r_start_in_ref_tile + search_radius);
        const int c0 = std::max(0, block_c_start_in_ref_tile - search_radius);
        const int c1 = std::min(rw - bw, block_c_start_in_ref_tile + search_radius);

        cv::Mat abs_diff_block;
        if (buffers.diff_workspace.rows < bh || buffers.diff_workspace.cols < bw ||
            buffers.diff_workspace.type() != CV_32FC1)
        {
            buffers.diff_workspace = cv::Mat(cv::Size(bw, bh), CV_32FC1);
        }
        abs_diff_block = buffers.diff_workspace(cv::Rect(0, 0, bw, bh));

        std::vector<cv::Point2f> motion_candidates;
        motion_candidates.reserve((r1 - r0 + 1) * (c1 - c0 + 1));

        const bool use_hierarchical = (r1 - r0 > 16 || c1 - c0 > 16);
        int step = use_hierarchical ? 2 : 1;
        
        for (int phase = 0; phase < (use_hierarchical ? 2 : 1); ++phase)
        {
            if (phase == 1)
            {
                const int refined_r0 = std::max(r0, result.best_match_r - 2);
                const int refined_r1 = std::min(r1, result.best_match_r + 2);
                const int refined_c0 = std::max(c0, result.best_match_c - 2);
                const int refined_c1 = std::min(c1, result.best_match_c + 2);
                step = 1;
                
                for (int r = refined_r0; r <= refined_r1; r += step)
                {
                    for (int c = refined_c0; c <= refined_c1; c += step)
                    {
                        if (r == result.best_match_r && c == result.best_match_c)
                            continue;
                            
                        cv::Rect roi(c, r, bw, bh);
                        const cv::Mat ref_block = reference_tile_gray(roi);

                        cv::absdiff(current_block_gray, ref_block, abs_diff_block);

                        float score;
                        if (use_plain)
                        {
                            score = Internal::calculate_plain_mad_32f(current_block_gray, ref_block);
                        }
                        else
                        {
                            score = Internal::calculate_noise_motion_aware_weighted_mad(
                                current_block_gray, ref_block, grad_mag, abs_diff_block,
                                noise_level, noise_threshold, diff_threshold,
                                gradient_weight_factor, stability_epsilon);
                        }

                        result.matches_found++;
                        if (score < result.min_mad)
                        {
                            result.second_min_mad = result.min_mad;
                            result.min_mad = score;
                            result.best_match_r = r;
                            result.best_match_c = c;
                            result.success = true;
                        }
                        else if (score < result.second_min_mad)
                        {
                            result.second_min_mad = score;
                        }
                    }
                }
            }
            else
            {
                for (int r = r0; r <= r1; r += step)
                {
                    for (int c = c0; c <= c1; c += step)
                    {
                        cv::Rect roi(c, r, bw, bh);
                        const cv::Mat ref_block = reference_tile_gray(roi);

                        cv::absdiff(current_block_gray, ref_block, abs_diff_block);

                        float score;
                        if (use_plain)
                        {
                            score = Internal::calculate_plain_mad_32f(current_block_gray, ref_block);
                        }
                        else
                        {
                            score = Internal::calculate_noise_motion_aware_weighted_mad(
                                current_block_gray, ref_block, grad_mag, abs_diff_block,
                                noise_level, noise_threshold, diff_threshold,
                                gradient_weight_factor, stability_epsilon);
                        }

                        result.matches_found++;
                        if (score < result.min_mad)
                        {
                            result.second_min_mad = result.min_mad;
                            result.min_mad = score;
                            result.best_match_r = r;
                            result.best_match_c = c;
                            result.success = true;
                        }
                        else if (score < result.second_min_mad)
                        {
                            result.second_min_mad = score;
                        }

                        motion_candidates.emplace_back(static_cast<float>(c - block_c_start_in_ref_tile),
                                                       static_cast<float>(r - block_r_start_in_ref_tile));
                    }
                }
            }
        }

        if (result.success)
        {
            cv::Point2f subpixel_match = Internal::refine_subpixel_match(
                current_block_gray, reference_tile_gray,
                result.best_match_r, result.best_match_c,
                gradient_weight_factor, stability_epsilon);

            const float ref_dx = subpixel_match.x - static_cast<float>(block_c_start_in_ref_tile);
            const float ref_dy = subpixel_match.y - static_cast<float>(block_r_start_in_ref_tile);
            
            float sum_dx = 0.0f, sum_dy = 0.0f;
            float total_weight = 0.0f;
            const float max_dev = 1.5f;
            const float confidence_threshold = result.second_min_mad / std::max(result.min_mad, stability_epsilon);

            if (confidence_threshold > 1.1f)
            {
                for (const auto &mv : motion_candidates)
                {
                    float dist = std::sqrt((mv.x - ref_dx) * (mv.x - ref_dx) +
                                           (mv.y - ref_dy) * (mv.y - ref_dy));
                    if (dist <= max_dev)
                    {
                        float weight = std::exp(-dist * dist / (2.0f * max_dev * max_dev / 4.0f));
                        sum_dx += mv.x * weight;
                        sum_dy += mv.y * weight;
                        total_weight += weight;
                    }
                }

                if (total_weight > stability_epsilon)
                {
                    float avg_dx = sum_dx / total_weight;
                    float avg_dy = sum_dy / total_weight;
                    
                    float blend_factor = std::min(0.3f, 1.0f / confidence_threshold);
                    avg_dx = ref_dx * (1.0f - blend_factor) + avg_dx * blend_factor;
                    avg_dy = ref_dy * (1.0f - blend_factor) + avg_dy * blend_factor;
                    
                    result.best_match_c = block_c_start_in_ref_tile + static_cast<int>(std::round(avg_dx));
                    result.best_match_r = block_r_start_in_ref_tile + static_cast<int>(std::round(avg_dy));
                }
                else
                {
                    result.best_match_c = static_cast<int>(std::round(subpixel_match.x));
                    result.best_match_r = static_cast<int>(std::round(subpixel_match.y));
                }
            }
            else
            {
                result.best_match_c = static_cast<int>(std::round(subpixel_match.x));
                result.best_match_r = static_cast<int>(std::round(subpixel_match.y));
            }
        }
        return result;
    }

}