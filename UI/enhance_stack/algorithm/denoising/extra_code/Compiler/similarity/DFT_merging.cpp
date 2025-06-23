#include "DFT_merging.hpp"
#include <opencv2/imgproc.hpp>
#include <iostream>
#include <cmath>
#include <vector>
#include <numeric>
#include <immintrin.h> // Sertakan header untuk AVX

namespace MotionMerging
{
namespace Internal
{

// --- Helper Functions untuk AVX2 ---

// Menjumlahkan 8 float dalam sebuah register __m256 menjadi satu skalar.
static inline float horizontal_add_m256(__m256 reg) {
    __m128 lo = _mm256_castps256_ps128(reg);
    __m128 hi = _mm256_extractf128_ps(reg, 1);
    __m128 sum = _mm_add_ps(lo, hi);
    sum = _mm_hadd_ps(sum, sum);
    sum = _mm_hadd_ps(sum, sum);
    return _mm_cvtss_f32(sum);
}

// Menghitung magnitudo kuadrat dari 4 bilangan kompleks [r,i,r,i,...] dalam register AVX.
static inline __m256 _mm256_complex_mag_sq_ps(const __m256& a) {
    const __m256 a_sq = _mm256_mul_ps(a, a);
    const __m256 hsum = _mm256_hadd_ps(a_sq, a_sq);
    return _mm256_permute_ps(hsum, 0b10100000);
}

// Versi AVX2 dari loop pemrosesan frekuensi.
// Fungsi ini sekarang mengembalikan jumlah total dari semua bobot frekuensi.
#if defined(__GNUC__) || defined(__clang__)
__attribute__((target("avx2,fma")))
#endif
static float merge_frequency_loop_avx2(
    DFTBuffers &buffers,
    float const_noise_floor_freq_part,
    float base_noise_level,
    float noise_threshold_multiplier,
    float high_confidence_boost,
    float low_confidence_penalty,
    float interpolation_range_inv,
    float boost_penalty_diff,
    float noise_lower_bound,
    float stability_epsilon
) {
    // Pre-compute konstanta untuk AVX
    const __m256 v_const_noise = _mm256_set1_ps(const_noise_floor_freq_part);
    const __m256 v_stability_eps = _mm256_set1_ps(stability_epsilon);
    const __m256 v_noise_floor_adaptive = _mm256_set1_ps(1e-6f);
    const __m256 v_half = _mm256_set1_ps(0.5f);
    const __m256 v_one = _mm256_set1_ps(1.0f);
    const __m256 v_zero = _mm256_setzero_ps();
    const __m256 v_high_conf_boost_factor = _mm256_set1_ps(1.0f + high_confidence_boost); // Aproksimasi Tanh
    const __m256 v_low_conf_penalty = _mm256_set1_ps(low_confidence_penalty);
    
    // Akumulator untuk bobot
    __m256 v_sum_weights = _mm256_setzero_ps();

    const int avx_cols = buffers.current_dft.cols - (buffers.current_dft.cols % 4);

    for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f) {
        const cv::Vec2f* p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f* p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f* p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);

        for (int c_f = 0; c_f < avx_cols; c_f += 4) {
            const __m256 v_curr = _mm256_loadu_ps(reinterpret_cast<const float*>(p_curr_dft_row + c_f));
            const __m256 v_ref = _mm256_loadu_ps(reinterpret_cast<const float*>(p_ref_dft_row + c_f));

            const __m256 v_diff = _mm256_sub_ps(v_ref, v_curr);
            const __m256 v_mag_sq_diff = _mm256_complex_mag_sq_ps(v_diff);
            
            const __m256 v_mag_curr = _mm256_complex_mag_sq_ps(v_curr);
            const __m256 v_mag_ref = _mm256_complex_mag_sq_ps(v_ref);
            const __m256 v_avg_mag = _mm256_mul_ps(_mm256_add_ps(v_mag_curr, v_mag_ref), v_half);

            const __m256 v_adaptive_noise_thresh = _mm256_max_ps(_mm256_set1_ps(base_noise_level), _mm256_mul_ps(v_avg_mag, v_noise_floor_adaptive));
            const __m256 v_noise_boundary = _mm256_mul_ps(v_adaptive_noise_thresh, _mm256_set1_ps(noise_threshold_multiplier));

            const __m256 mask_is_real_diff = _mm256_cmp_ps(v_mag_sq_diff, v_noise_boundary, _CMP_GT_OQ);
            const __m256 v_enhanced_real_diff = _mm256_mul_ps(v_mag_sq_diff, v_high_conf_boost_factor);
            __m256 v_enhanced_mag_sq_diff = _mm256_blendv_ps(v_mag_sq_diff, v_enhanced_real_diff, mask_is_real_diff);

            const __m256 v_weight_denom = _mm256_add_ps(v_enhanced_mag_sq_diff, v_const_noise);
            __m256 v_weight_curr = _mm256_div_ps(v_const_noise, v_weight_denom);

            v_weight_curr = _mm256_max_ps(v_zero, _mm256_min_ps(v_one, v_weight_curr));

            v_sum_weights = _mm256_add_ps(v_sum_weights, v_weight_curr);

            const __m256 v_weight_ref = _mm256_sub_ps(v_one, v_weight_curr);
            const __m256 v_merged = _mm256_fmadd_ps(v_curr, v_weight_curr, _mm256_mul_ps(v_ref, v_weight_ref));
            _mm256_storeu_ps(reinterpret_cast<float*>(p_merged_dft_row + c_f), v_merged);
        }
    }

    float total_sum = horizontal_add_m256(v_sum_weights);
    
    // Loop sisa skalar TIDAK diparalelkan di sini karena biasanya sangat sedikit
    for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f) {
        const cv::Vec2f* p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
        const cv::Vec2f* p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
        cv::Vec2f* p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);
        for (int c_f = avx_cols; c_f < buffers.current_dft.cols; ++c_f) {
             const cv::Vec2f &coeff_curr = p_curr_dft_row[c_f];
             const cv::Vec2f &coeff_ref = p_ref_dft_row[c_f];
             // Implementasi skalar sederhana untuk sisa
             const float diff_real = coeff_ref[0] - coeff_curr[0];
             const float diff_imag = coeff_ref[1] - coeff_curr[1];
             const float mag_sq_diff = diff_real * diff_real + diff_imag * diff_imag;
             const float weight_denominator = mag_sq_diff + const_noise_floor_freq_part;
             float weight_curr_freq = const_noise_floor_freq_part / weight_denominator;
             weight_curr_freq = std::clamp(weight_curr_freq, 0.0f, 1.0f);
             total_sum += weight_curr_freq;
             const float weight_ref = 1.0f - weight_curr_freq;
             p_merged_dft_row[c_f][0] = coeff_ref[0] * weight_ref + coeff_curr[0] * weight_curr_freq;
             p_merged_dft_row[c_f][1] = coeff_ref[1] * weight_ref + coeff_curr[1] * weight_curr_freq;
        }
    }
    return total_sum;
}

}


FrequencyMergeResult merge_blocks_frequency_domain(
    const cv::Mat &current_block_gray,
    const cv::Mat &reference_block_gray,
    float estimated_noise_sigma_for_block,
    float wiener_c_factor,
    float stability_epsilon,
    DFTBuffers &buffers)
{
    FrequencyMergeResult result;
    result.success = false;

    if (current_block_gray.empty() && reference_block_gray.empty()) {
        result.merged_block_gray = cv::Mat();
        return result;
    }
    if (current_block_gray.empty()) {
        reference_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }
    if (reference_block_gray.empty()) {
        current_block_gray.copyTo(result.merged_block_gray);
        result.success = true;
        return result;
    }
    if (current_block_gray.size() != reference_block_gray.size() ||
        current_block_gray.type() != CV_32FC1 || reference_block_gray.type() != CV_32FC1) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    const int block_h = current_block_gray.rows;
    const int block_w = current_block_gray.cols;

    if (block_h <= 0 || block_w <= 0) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    const int optimal_rows = cv::getOptimalDFTSize(block_h);
    const int optimal_cols = cv::getOptimalDFTSize(block_w);

    try {
        if (buffers.cached_rows != optimal_rows || buffers.cached_cols != optimal_cols) {
            buffers.current_padded.create(optimal_rows, optimal_cols, CV_32FC1);
            buffers.ref_padded.create(optimal_rows, optimal_cols, CV_32FC1);
            buffers.current_dft.create(optimal_rows, optimal_cols, CV_32FC2);
            buffers.ref_dft.create(optimal_rows, optimal_cols, CV_32FC2);
            buffers.merged_dft.create(optimal_rows, optimal_cols, CV_32FC2);
            buffers.temp_spatial_merged.create(optimal_rows, optimal_cols, CV_32FC1);
            buffers.cached_rows = optimal_rows;
            buffers.cached_cols = optimal_cols;
        }

        buffers.current_padded.setTo(0);
        buffers.ref_padded.setTo(0);
        current_block_gray.copyTo(buffers.current_padded(cv::Rect(0, 0, block_w, block_h)));
        reference_block_gray.copyTo(buffers.ref_padded(cv::Rect(0, 0, block_w, block_h)));

        cv::dft(buffers.current_padded, buffers.current_dft, cv::DFT_COMPLEX_OUTPUT);
        cv::dft(buffers.ref_padded, buffers.ref_dft, cv::DFT_COMPLEX_OUTPUT);
    } catch (const cv::Exception &e) {
        std::cerr << "OpenCV Exception during padding or DFT: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    const float optimal_elements = static_cast<float>(optimal_rows * optimal_cols);
    const float optimal_elements_inv = 1.0f / optimal_elements;
    const float sigma_sq_spatial_block = estimated_noise_sigma_for_block * estimated_noise_sigma_for_block;
    const float sigma_sq_dft_eff_block = std::max(sigma_sq_spatial_block / optimal_elements_inv, stability_epsilon);
    const float const_noise_floor_freq_part = std::max(wiener_c_factor * sigma_sq_dft_eff_block, stability_epsilon);
    
    const float noise_threshold_multiplier = 1.2f;
    const float high_confidence_boost = 2.0f;
    const float low_confidence_penalty = 0.1f;
    const float noise_floor_adaptive = 1e-6f;
    const float base_noise_level = sigma_sq_dft_eff_block * optimal_elements_inv;
    const float noise_boundary_multiplier = base_noise_level * noise_threshold_multiplier;
    const float noise_lower_bound = base_noise_level * 0.5f;
    const float interpolation_range_inv = 1.0f / std::max(noise_boundary_multiplier - noise_lower_bound, stability_epsilon);
    const float boost_penalty_diff = high_confidence_boost - low_confidence_penalty;

    float total_sum_of_weights = 0.0f;

#ifdef __AVX2__
    if (buffers.current_dft.cols >= 4) {
        total_sum_of_weights = Internal::merge_frequency_loop_avx2(
            buffers, const_noise_floor_freq_part, base_noise_level,
            noise_threshold_multiplier, high_confidence_boost, low_confidence_penalty,
            interpolation_range_inv, boost_penalty_diff, noise_lower_bound, stability_epsilon
        );
    } else 
#endif
    {
        float sum_freq_weights = 0.0f;
        int count_freq_weights = 0;
        #pragma omp parallel for reduction(+: sum_freq_weights, count_freq_weights) schedule(static)
        for (int r_f = 0; r_f < buffers.current_dft.rows; ++r_f) {
            const cv::Vec2f* p_curr_dft_row = buffers.current_dft.ptr<const cv::Vec2f>(r_f);
            const cv::Vec2f* p_ref_dft_row = buffers.ref_dft.ptr<const cv::Vec2f>(r_f);
            cv::Vec2f* p_merged_dft_row = buffers.merged_dft.ptr<cv::Vec2f>(r_f);

            for (int c_f = 0; c_f < buffers.current_dft.cols; ++c_f) {
                const cv::Vec2f &coeff_curr = p_curr_dft_row[c_f];
                const cv::Vec2f &coeff_ref = p_ref_dft_row[c_f];

                const bool is_invalid = std::isnan(coeff_curr[0]) || std::isnan(coeff_curr[1]) || std::isinf(coeff_curr[0]) || std::isinf(coeff_curr[1]) || std::isnan(coeff_ref[0]) || std::isnan(coeff_ref[1]) || std::isinf(coeff_ref[0]) || std::isinf(coeff_ref[1]);
                if (is_invalid) {
                    p_merged_dft_row[c_f] = coeff_curr;
                    sum_freq_weights += 1.0f;
                    count_freq_weights++;
                    continue;
                }

                const float diff_real = coeff_ref[0] - coeff_curr[0];
                const float diff_imag = coeff_ref[1] - coeff_curr[1];
                const float mag_sq_diff_raw = diff_real * diff_real + diff_imag * diff_imag;
                const float mag_curr = coeff_curr[0] * coeff_curr[0] + coeff_curr[1] * coeff_curr[1];
                const float mag_ref = coeff_ref[0] * coeff_ref[0] + coeff_ref[1] * coeff_ref[1];
                const float avg_magnitude = (mag_curr + mag_ref) * 0.5f;
                const float adaptive_noise_threshold = std::max(base_noise_level, avg_magnitude * noise_floor_adaptive);
                const float noise_boundary = adaptive_noise_threshold * noise_threshold_multiplier;
                
                float enhanced_mag_sq_diff;
                if (mag_sq_diff_raw > noise_boundary) {
                    const float confidence_ratio = std::min(mag_sq_diff_raw / noise_boundary, 10.0f);
                    const float boost_factor = 1.0f + high_confidence_boost * std::tanh(confidence_ratio - 1.0f);
                    enhanced_mag_sq_diff = mag_sq_diff_raw * boost_factor;
                } else if (mag_sq_diff_raw < noise_lower_bound) {
                    enhanced_mag_sq_diff = mag_sq_diff_raw * low_confidence_penalty;
                } else {
                    const float confidence_ratio = (mag_sq_diff_raw - noise_lower_bound) * interpolation_range_inv;
                    const float interpolation_factor = confidence_ratio * boost_penalty_diff + low_confidence_penalty;
                    enhanced_mag_sq_diff = mag_sq_diff_raw * (1.0f + interpolation_factor);
                }
                
                enhanced_mag_sq_diff = std::max(enhanced_mag_sq_diff, stability_epsilon);
                
                const float weight_denominator = enhanced_mag_sq_diff + const_noise_floor_freq_part;
                float weight_curr_freq = const_noise_floor_freq_part / weight_denominator;
                weight_curr_freq = std::clamp(weight_curr_freq, 0.0f, 1.0f);
                if (std::isnan(weight_curr_freq)) weight_curr_freq = 1.0f;

                const float weight_ref = 1.0f - weight_curr_freq;
                p_merged_dft_row[c_f][0] = coeff_ref[0] * weight_ref + coeff_curr[0] * weight_curr_freq;
                p_merged_dft_row[c_f][1] = coeff_ref[1] * weight_ref + coeff_curr[1] * weight_curr_freq;

                sum_freq_weights += weight_curr_freq;
                count_freq_weights++;
            }
        }
        total_sum_of_weights = sum_freq_weights;
    }

    if (optimal_elements > 0) {
        result.merge_confidence = total_sum_of_weights / optimal_elements;
    } else {
        result.merge_confidence = 0.0f;
    }
    
    if (result.merge_confidence <= 0.0f) {
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    try {
        cv::idft(buffers.merged_dft, buffers.temp_spatial_merged, cv::DFT_SCALE | cv::DFT_REAL_OUTPUT);
        if (buffers.temp_spatial_merged.rows < block_h || buffers.temp_spatial_merged.cols < block_w) {
            current_block_gray.copyTo(result.merged_block_gray);
            return result;
        }
        const cv::Rect crop_rect(0, 0, block_w, block_h);
        result.merged_block_gray = buffers.temp_spatial_merged(crop_rect).clone();
    } catch (const cv::Exception &e) {
        std::cerr << "OpenCV Exception during IDFT or cropping: " << e.what() << std::endl;
        current_block_gray.copyTo(result.merged_block_gray);
        return result;
    }

    cv::patchNaNs(result.merged_block_gray, 0.0);
    result.success = true;
    return result;
}

}