// block_matching.cpp

#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>

#ifdef _MSC_VER
#else
#include <immintrin.h>
#endif

namespace MotionMatching
{
    namespace Internal
    {
        // Konstanta untuk Charbonnier Loss
        const float CHARB_EPSILON = 0.01f;
        const float CHARB_EPSILON_SQ = CHARB_EPSILON * CHARB_EPSILON;

        // =========================================================================
        // --- FAST POLYNOMIAL APPROXIMATIONS (SCALAR) ---
        
        static inline float fast_tanh_pos(float x)
        {
            const float MAX_X_CLAMP = 3.5f;
            
            if (x >= MAX_X_CLAMP) {
                return 1.0f;
            }
            
            float x_sq = x * x;
            float P = x * (1.0f - 0.238f * x_sq); 
            
            return std::min(1.0f, std::max(0.0f, P));
        }

        static inline float fast_exp_neg(float z)
        {
            const float MAX_Z_CLAMP = 5.0f;
            
            if (z >= MAX_Z_CLAMP) {
                return 0.0f;
            }

            const float C1 = -0.9997f;
            const float C2 = 0.4982f;
            const float C3 = -0.1583f;

            float P = 1.0f + z * (C1 + z * (C2 + z * C3));

            return std::max(0.0f, P);
        }

        // --- Charbonnier Loss (Scalar) ---
        static inline float charbonnier_loss(float x)
        {
            float x_sq = x * x;
            return std::sqrt(x_sq + CHARB_EPSILON_SQ);
        }
        
        // =========================================================================
        // --- AVX IMPLEMENTATION FUNCTION ---
        
#ifdef __AVX__
        
        // --- Charbonnier Loss (AVX) ---
        static inline __m256 charbonnier_loss_avx(__m256 x)
        {
            __m256 x_sq = _mm256_mul_ps(x, x);
            __m256 epsilon_sq = _mm256_set1_ps(CHARB_EPSILON_SQ);
            __m256 sum_sq = _mm256_add_ps(x_sq, epsilon_sq);
            return _mm256_sqrt_ps(sum_sq);
        }

        // Fungsi pembantu untuk horizontal reduction AVX
        static inline float hsum_ps_avx(__m256 v) {
            __m128 v128 = _mm256_castps256_ps128(v);
            __m128 v256_upper = _mm256_extractf128_ps(v, 1);
            v128 = _mm_add_ps(v128, v256_upper);
            __m128 v64 = _mm_add_ps(v128, _mm_shuffle_ps(v128, v128, 0x55));
            __m128 v32 = _mm_add_ss(v64, _mm_shuffle_ps(v64, v64, 0xaa));
            return _mm_cvtss_f32(v32);
        }

        static inline void run_avx_fft_mad(
            const cv::Mat &mag_sq_diff_roi, 
            const float noise_threshold_sq,
            const float row_decay_inv, const float col_decay_inv, 
            const float linear_decay_strength,
            float &weighted_sum, float &total_weight)
        {
            // FUNGSI INI TIDAK DIUBAH KARENA INI BEKERJA DI DOMAIN L2 FREKUENSI
            // (Tetap menggunakan L2 noise subtraction)
            const int cols = mag_sq_diff_roi.cols;
            const int rows = mag_sq_diff_roi.rows;
            
            const int VEC_SIZE = 8;
            const int end_avx = cols - (cols % VEC_SIZE);
            
            const __m256 NOISE_THRESH_SQ = _mm256_set1_ps(noise_threshold_sq);
            const __m256 ONE = _mm256_set1_ps(1.0f);
            const __m256 ZERO = _mm256_set1_ps(0.0f);
            const __m256 LINEAR_DECAY_STRENGTH = _mm256_set1_ps(linear_decay_strength);
            const __m256 COL_DECAY_INV = _mm256_set1_ps(col_decay_inv);
            
            float total_weighted_sum_acc = 0.0f;
            float total_weight_acc = 0.0f;

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict diff_ptr = mag_sq_diff_roi.ptr<float>(y);
                
                float radial_weight_linear_scalar = 1.0f - (linear_decay_strength * y * row_decay_inv);
                float radial_weight_scalar = std::max(0.0f, radial_weight_linear_scalar);
                const __m256 RADIAL_WEIGHT = _mm256_set1_ps(radial_weight_scalar);

                __m256 sum_w_avx = _mm256_setzero_ps();
                __m256 sum_prod_avx = _mm256_setzero_ps();
                
                int x = 0;
                for (; x < end_avx; x += VEC_SIZE)
                {
                    __m256 X_VEC = _mm256_setr_ps(
                        (float)x, (float)(x+1), (float)(x+2), (float)(x+3), 
                        (float)(x+4), (float)(x+5), (float)(x+6), (float)(x+7)
                    );
                    
                    __m256 pixel_mag_sq_diff = _mm256_loadu_ps(diff_ptr + x);
                    
                    __m256 col_weight_linear = _mm256_sub_ps(ONE, 
                        _mm256_mul_ps(LINEAR_DECAY_STRENGTH, 
                            _mm256_mul_ps(X_VEC, COL_DECAY_INV)));
                    
                    __m256 col_weight = _mm256_max_ps(ZERO, col_weight_linear);
                    __m256 pixel_weight = _mm256_mul_ps(RADIAL_WEIGHT, col_weight);

                    __m256 mask = _mm256_cmp_ps(pixel_mag_sq_diff, NOISE_THRESH_SQ, _CMP_GE_OS);
                    
                    __m256 final_diff_value_raw = _mm256_sub_ps(pixel_mag_sq_diff, NOISE_THRESH_SQ);
                    
                    __m256 final_diff_value = _mm256_blendv_ps(ZERO, final_diff_value_raw, mask);

                    sum_w_avx = _mm256_add_ps(sum_w_avx, pixel_weight);
                    sum_prod_avx = _mm256_fmadd_ps(final_diff_value, pixel_weight, sum_prod_avx);
                }

                total_weighted_sum_acc += hsum_ps_avx(sum_prod_avx);
                total_weight_acc += hsum_ps_avx(sum_w_avx);
                
                // Loop Epilog Scalar (sisa piksel)
                for (; x < cols; ++x)
                {
                    float col_weight_linear = 1.0f - (linear_decay_strength * x * col_decay_inv);
                    float col_weight = std::max(0.0f, col_weight_linear);
                    float pixel_weight = radial_weight_scalar * col_weight;
                    float pixel_mag_sq_diff = diff_ptr[x];
                    
                    float final_diff_value = 0.0f;
                    if (pixel_mag_sq_diff >= noise_threshold_sq)
                    {
                        final_diff_value = pixel_mag_sq_diff - noise_threshold_sq;
                    }

                    total_weighted_sum_acc += final_diff_value * pixel_weight;
                    total_weight_acc += pixel_weight;
                }
            }
            
            weighted_sum = total_weighted_sum_acc;
            total_weight = total_weight_acc;
        }

        static inline __m256 fast_tanh_pos_avx(__m256 x)
        {
            const __m256 MAX_X_CLAMP = _mm256_set1_ps(3.5f);
            const __m256 ONE = _mm256_set1_ps(1.0f);
            const __m256 ZERO = _mm256_set1_ps(0.0f);
            const __m256 C = _mm256_set1_ps(0.238f);
            
            __m256 mask_clamp = _mm256_cmp_ps(x, MAX_X_CLAMP, _CMP_GE_OS);
            
            __m256 x_sq = _mm256_mul_ps(x, x);
            __m256 P_inner = _mm256_sub_ps(ONE, _mm256_mul_ps(C, x_sq));
            __m256 P = _mm256_mul_ps(x, P_inner);
            
            P = _mm256_max_ps(ZERO, P);
            P = _mm256_min_ps(ONE, P);

            return _mm256_blendv_ps(P, ONE, mask_clamp);
        }

        static inline void run_avx_weighted_mad(
            int cols, float stab_epsilon, float gradient_weight_factor, float noise_level,
            float adaptive_diff_threshold, float adaptive_noise_threshold_1_5,
            float &weighted_sum, float &total_weight, int &x,
            const float *__restrict diff_ptr, const float *__restrict gx1_ptr,
            const float *__restrict gy1_ptr, const float *__restrict gx2_ptr,
            const float *__restrict gy2_ptr)
        {
            const int VEC_SIZE = 8;
            const int end_avx = cols - (cols % VEC_SIZE);

            // SIMD Constants
            const __m256 STAB_EPSILON = _mm256_set1_ps(stab_epsilon);
            const __m256 GRAD_SENSITIVITY = _mm256_set1_ps(150.0f); 
            const __m256 GRAD_WEIGHT_FACTOR = _mm256_set1_ps(gradient_weight_factor);
            const __m256 NOISE_LEVEL = _mm256_set1_ps(noise_level);
            const __m256 MIN_MAG_SQ_THRESH = _mm256_set1_ps(150.0f); 
            
            const __m256 ADAPTIVE_NOISE_THRESH_1_5 = _mm256_set1_ps(adaptive_noise_threshold_1_5);
            const __m256 ADAPTIVE_DIFF_THRESH = _mm256_set1_ps(adaptive_diff_threshold);
            const __m256 MIN_FLOOR_WEIGHT = _mm256_set1_ps(0.05f);
            const __m256 ONE = _mm256_set1_ps(1.0f);
            const __m256 ZERO = _mm256_set1_ps(0.0f);
            const __m256 CONST_0_2 = _mm256_set1_ps(0.2f);
            const __m256 CONST_1_15 = _mm256_set1_ps(1.15f);
            const __m256 CONST_0_15 = _mm256_set1_ps(0.15f);
            const __m256 CONST_0_3 = _mm256_set1_ps(0.3f);
            const __m256 CONST_0_4 = _mm256_set1_ps(0.4f);
            const __m256 CONST_4_INV = _mm256_set1_ps(1.0f / 4.0f);

            __m256 sum_w_avx = _mm256_setzero_ps();
            __m256 sum_prod_avx = _mm256_setzero_ps();

            for (; x < end_avx; x += VEC_SIZE)
            {
                // 1. Load Data (Raw Absolute Difference)
                __m256 pixel_diff_raw = _mm256_loadu_ps(diff_ptr + x);
                
                // 1.1 APLIKASIKAN CHARBONNIER LOSS DI SINI
                __m256 pixel_diff = charbonnier_loss_avx(pixel_diff_raw);

                __m256 gx1 = _mm256_loadu_ps(gx1_ptr + x);
                __m256 gy1 = _mm256_loadu_ps(gy1_ptr + x);
                __m256 gx2 = _mm256_loadu_ps(gx2_ptr + x);
                __m256 gy2 = _mm256_loadu_ps(gy2_ptr + x);

                // Magnitudo Kuadrat
                __m256 mag1_sq = _mm256_fmadd_ps(gx1, gx1, _mm256_mul_ps(gy1, gy1));
                __m256 mag2_sq = _mm256_fmadd_ps(gx2, gx2, _mm256_mul_ps(gy2, gy2));
                __m256 min_mag_sq = _mm256_min_ps(mag1_sq, mag2_sq);
                
                // --- 2. NOISE WEIGHT (AVX) ---
                __m256 noise_weight = ONE;
                __m256 noise_check = _mm256_cmp_ps(NOISE_LEVEL, STAB_EPSILON, _CMP_GT_OS);
                
                __m256 is_flat_area = _mm256_cmp_ps(min_mag_sq, MIN_MAG_SQ_THRESH, _CMP_LT_OS);
                
                // Catatan: pixel_diff di sini adalah nilai robustified (Charbonnier)
                
                __m256 is_small_diff_flat = _mm256_cmp_ps(pixel_diff, ADAPTIVE_NOISE_THRESH_1_5, _CMP_LT_OS);
                __m256 diff_ratio_small_flat = _mm256_div_ps(pixel_diff, ADAPTIVE_NOISE_THRESH_1_5);
                __m256 weight_scale = _mm256_sub_ps(ONE, MIN_FLOOR_WEIGHT);
                __m256 weight_hukuman = _mm256_fmadd_ps(weight_scale, diff_ratio_small_flat, MIN_FLOOR_WEIGHT);
                
                __m256 diff_minus_thresh = _mm256_sub_ps(pixel_diff, ADAPTIVE_NOISE_THRESH_1_5);
                __m256 ratio_damping = _mm256_min_ps(ONE, _mm256_div_ps(diff_minus_thresh, ADAPTIVE_NOISE_THRESH_1_5));
                __m256 weight_damping = _mm256_sub_ps(ONE, _mm256_mul_ps(CONST_0_2, ratio_damping));
                
                __m256 noise_flat = _mm256_blendv_ps(weight_damping, weight_hukuman, is_small_diff_flat);

                __m256 is_small_diff_struc = _mm256_cmp_ps(pixel_diff, ADAPTIVE_DIFF_THRESH, _CMP_LT_OS);
                __m256 diff_ratio_small_struc = _mm256_div_ps(pixel_diff, ADAPTIVE_DIFF_THRESH);
                __m256 one_minus_ratio = _mm256_sub_ps(ONE, diff_ratio_small_struc);
                __m256 weight_boost = _mm256_fmadd_ps(CONST_0_15, one_minus_ratio, CONST_1_15);

                __m256 diff_ratio_large_struc = _mm256_mul_ps(pixel_diff, _mm256_mul_ps(ADAPTIVE_DIFF_THRESH, _mm256_set1_ps(4.0f)));
                __m256 ratio_damping_struc = _mm256_min_ps(ONE, _mm256_mul_ps(diff_ratio_large_struc, CONST_4_INV));
                __m256 weight_damping_struc_term = _mm256_mul_ps(CONST_0_4, _mm256_sub_ps(ONE, ratio_damping_struc));
                __m256 weight_damping_struc = _mm256_add_ps(CONST_0_3, weight_damping_struc_term);
                
                __m256 noise_struc = _mm256_blendv_ps(weight_damping_struc, weight_boost, is_small_diff_struc);

                __m256 final_noise_calc = _mm256_blendv_ps(noise_struc, noise_flat, is_flat_area);
                
                noise_weight = _mm256_blendv_ps(ONE, final_noise_calc, noise_check);


                // --- 3. STRUCTURE WEIGHT (AVX + RSQRT) ---
                // ... (tetap sama) ...
                __m256 structure_weight = ONE;
                
                __m256 m1_ok = _mm256_cmp_ps(mag1_sq, STAB_EPSILON, _CMP_GT_OS);
                __m256 m2_ok = _mm256_cmp_ps(mag2_sq, STAB_EPSILON, _CMP_GT_OS);
                __m256 is_textured = _mm256_and_ps(m1_ok, m2_ok);
                
                __m256 dot_product = _mm256_fmadd_ps(gx1, gx2, _mm256_mul_ps(gy1, gy2));
                __m256 mag_prod = _mm256_mul_ps(mag1_sq, mag2_sq);
                
                __m256 rsqrt_mag_prod = _mm256_rsqrt_ps(mag_prod); 
                __m256 cos_similarity = _mm256_mul_ps(dot_product, rsqrt_mag_prod);
                
                __m256 rsqrt_min_mag_sq = _mm256_rsqrt_ps(min_mag_sq); 
                __m256 limiting_magnitude = _mm256_div_ps(ONE, rsqrt_min_mag_sq);

                __m256 max_cos_sim = _mm256_max_ps(ZERO, cos_similarity);
                __m256 similarity_score = _mm256_mul_ps(max_cos_sim, limiting_magnitude);
                
                __m256 tanh_input = _mm256_mul_ps(similarity_score, GRAD_SENSITIVITY);
                __m256 tanh_result = fast_tanh_pos_avx(tanh_input);
                
                __m256 calculated_struc_w = _mm256_fmadd_ps(GRAD_WEIGHT_FACTOR, tanh_result, ONE);
                
                structure_weight = _mm256_blendv_ps(ONE, calculated_struc_w, is_textured);

                // --- 4. FINAL WEIGHT ---
                __m256 final_weight = _mm256_mul_ps(structure_weight, noise_weight);
                
                // Perhitungan Sums
                // Menggunakan pixel_diff yang sudah di robustify Charbonnier
                __m256 effective_diff = _mm256_sub_ps(pixel_diff, ADAPTIVE_DIFF_THRESH);
                effective_diff = _mm256_max_ps(ZERO, effective_diff);
                
                sum_w_avx = _mm256_add_ps(sum_w_avx, final_weight);
                sum_prod_avx = _mm256_fmadd_ps(effective_diff, final_weight, sum_prod_avx);
            }
            
            // Horizontal Summation (Reduction)
            total_weight += hsum_ps_avx(sum_w_avx);
            weighted_sum += hsum_ps_avx(sum_prod_avx);
        }

#endif // __AVX__

        // =========================================================================
        // --- calculate_plain_mad_32f (MeAD) ---
        // Tidak diubah.
        static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                      block1_gray.type() == CV_32FC1 &&
                      block2_gray.type() == CV_32FC1);

            const int total_pixels = block1_gray.rows * block1_gray.cols;
            if (total_pixels == 0) return 0.0f;

            cv::Mat diff;
            cv::absdiff(block1_gray, block2_gray, diff);

            std::vector<float> diff_values;
            diff_values.reserve(total_pixels);
            
            if (diff.isContinuous()) {
                diff_values.assign((float*)diff.datastart, (float*)diff.dataend);
            } else {
                for (int i = 0; i < diff.rows; ++i) {
                    diff_values.insert(diff_values.end(), diff.ptr<float>(i), diff.ptr<float>(i) + diff.cols);
                }
            }
            
            size_t n = diff_values.size();
            if (n == 0) return 0.0f;
            
            // Menggunakan Charbonnier pada MeAD tidak umum. Kita kembalikan MeAD standar.
            size_t median_idx = n / 2;
            std::nth_element(diff_values.begin(), diff_values.begin() + median_idx, diff_values.end());
            
            float median_diff = diff_values[median_idx];
            
            if (n % 2 == 0) {
                std::nth_element(diff_values.begin(), diff_values.begin() + median_idx - 1, diff_values.begin() + median_idx);
                median_diff = (median_diff + diff_values[median_idx - 1]) / 2.0f;
            }
            
            return median_diff;
        }

        // --- FUNGSI calculate_fft_32f (Noise Adaptasi Dipulihkan) ---
        static float calculate_fft_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray, float noise_sigma)
        {
            CV_Assert(block1_gray.size() == block2_gray.size() &&
                    block1_gray.type() == CV_32FC1 &&
                    block2_gray.type() == CV_32FC1);

            const int total_pixels = block1_gray.rows * block1_gray.cols;
            if (total_pixels == 0)
                return 0.0f;

            // --- Langkah DFT (Tidak Berubah) ---
            int opt_rows = cv::getOptimalDFTSize(block1_gray.rows);
            int opt_cols = cv::getOptimalDFTSize(block1_gray.cols);
            cv::Mat padded1, padded2;
            cv::copyMakeBorder(block1_gray, padded1, 0, opt_rows - block1_gray.rows,
                            0, opt_cols - block1_gray.cols, cv::BORDER_CONSTANT, cv::Scalar::all(0));
            cv::copyMakeBorder(block2_gray, padded2, 0, opt_rows - block2_gray.rows,
                            0, opt_cols - block2_gray.cols, cv::BORDER_CONSTANT, cv::Scalar::all(0));

            cv::Mat fft1, fft2;
            cv::dft(padded1, fft1, cv::DFT_COMPLEX_OUTPUT);
            cv::dft(padded2, fft2, cv::DFT_COMPLEX_OUTPUT);

            cv::Mat diff_dft;
            cv::subtract(fft2, fft1, diff_dft);

            cv::Mat planes[2];
            cv::split(diff_dft, planes);

            cv::Mat mag_sq_diff;
            cv::multiply(planes[0], planes[0], planes[0]);
            cv::multiply(planes[1], planes[1], planes[1]);
            cv::add(planes[0], planes[1], mag_sq_diff);

            if (mag_sq_diff.rows > 0 && mag_sq_diff.cols > 0)
            {
                mag_sq_diff.at<float>(0, 0) = 0.0f;
            }

            const int meaningful_rows = std::min(opt_rows / 2, block1_gray.rows * 2);
            const int meaningful_cols = std::min(opt_cols / 2, block1_gray.cols * 2);
            cv::Rect roi_freq(0, 0, meaningful_cols, meaningful_rows);
            cv::Mat mag_sq_diff_roi = mag_sq_diff(roi_freq);
            // ------------------------------------

            // --- LOGIKA NOISE ADAPTIF DIPULIHKAN ---
            const float optimal_elements = static_cast<float>(opt_rows * opt_cols);
            const float noise_sigma_sq = noise_sigma * noise_sigma;
            const float theoretical_noise_power_floor = noise_sigma_sq * optimal_elements;

            const float STABILITY_MIN_FACTOR = 1.0f;   
            const float CONFIDENCE_MAX_FACTOR = 1.0f;  
            const float EXPONENTIAL_DECAY_RATE = 1.0f; 

            const float noise_range = CONFIDENCE_MAX_FACTOR - STABILITY_MIN_FACTOR;
            
            float decay_term = std::exp(-EXPONENTIAL_DECAY_RATE * noise_sigma);
            float noise_floor_factor = STABILITY_MIN_FACTOR + noise_range * decay_term; 

            const float stability_constant = 1e-6f;
            const float noise_threshold_sq = std::max(stability_constant, theoretical_noise_power_floor * noise_floor_factor);
            // ------------------------------------
            
            float weighted_sum = 0.0f;
            float total_weight = 0.0f;

            const float linear_decay_strength = 1.0f;
            const float max_row_val = static_cast<float>(mag_sq_diff_roi.rows);
            const float max_col_val = static_cast<float>(mag_sq_diff_roi.cols);
            const float row_decay_inv = (max_row_val > 0.0f) ? (1.0f / max_row_val) : 0.0f;
            const float col_decay_inv = (max_col_val > 0.0f) ? (1.0f / max_col_val) : 0.0f;

            // =====================================================================
            // DISPATCH LOOP PEMROSESAN FREKUENSI
            // =====================================================================

        #ifdef __AVX__
            run_avx_fft_mad(mag_sq_diff_roi, noise_threshold_sq,
                            row_decay_inv, col_decay_inv, linear_decay_strength,
                            weighted_sum, total_weight);
        #else 
            // Fallback/Scalar Loop
            for (int y = 0; y < mag_sq_diff_roi.rows; ++y)
            {
                const float *__restrict diff_ptr = mag_sq_diff_roi.ptr<float>(y);
                float radial_weight_linear = 1.0f - (linear_decay_strength * y * row_decay_inv);
                float radial_weight = std::max(0.0f, radial_weight_linear);

                #pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < mag_sq_diff_roi.cols; ++x)
                {
                    float col_weight_linear = 1.0f - (linear_decay_strength * x * col_decay_inv);
                    float col_weight = std::max(0.0f, col_weight_linear);
                    float pixel_weight = radial_weight * col_weight;
                    float pixel_mag_sq_diff = diff_ptr[x];
                    
                    float final_diff_value = 0.0f;
                    if (pixel_mag_sq_diff >= noise_threshold_sq)
                    {
                        final_diff_value = pixel_mag_sq_diff - noise_threshold_sq;
                    }

                    weighted_sum += final_diff_value * pixel_weight;
                    total_weight += pixel_weight;
                }
            }
        #endif

            const float normalization_factor = static_cast<float>(total_pixels);
            float fft_mag_sq_score = (total_weight > 0) ? (weighted_sum / total_weight) : 0.0f;

            if (normalization_factor > 0)
            {
                fft_mag_sq_score /= normalization_factor;
            }

            float fft_score = std::sqrt(fft_mag_sq_score);

            return fft_score;
        }

        // =========================================================================
        // --- calculate_hybrid_gradient_weighted_mad (CHARBONNIER & Noise Adaptasi Dipulihkan) ---
        // =========================================================================
        
        static float calculate_hybrid_gradient_weighted_mad(
            const cv::Mat &block1_gray, const cv::Mat &block2_gray,
            const cv::Mat &grad_x1, const cv::Mat &grad_y1,
            const cv::Mat &grad_x2, const cv::Mat &grad_y2,
            const cv::Mat &abs_diff_block, float noise_level,
            float gradient_weight_factor, float stab_epsilon)
        {
            const int rows = block1_gray.rows, cols = block1_gray.cols;
            float weighted_sum = 0.0f, total_weight = 0.0f;

            // Parameter Adaptasi:
            const float grad_sensitivity = 300.0f;
            const float structure_min_threshold_sq = 50.0f;

            // Pre-calculate adaptive thresholds (MENGGUNAKAN noise_level YANG SEBENARNYA)
            const float adaptive_noise_threshold = std::max(0.01f, noise_level * 0.4f); 
            const float adaptive_diff_threshold = std::max(0.005f, noise_level * 0.2f); 
            const float adaptive_noise_threshold_1_5 = adaptive_diff_threshold * 1.5f;

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
                const float *__restrict gx1_ptr = grad_x1.ptr<float>(y);
                const float *__restrict gy1_ptr = grad_y1.ptr<float>(y);
                const float *__restrict gx2_ptr = grad_x2.ptr<float>(y);
                const float *__restrict gy2_ptr = grad_y2.ptr<float>(y);
                
                int x = 0;

#ifdef __AVX__
                // Panggil fungsi SIMD terisolasi
                run_avx_weighted_mad(
                    cols, stab_epsilon, gradient_weight_factor, noise_level,
                    adaptive_diff_threshold, adaptive_noise_threshold_1_5,
                    weighted_sum, total_weight, x,
                    diff_ptr, gx1_ptr, gy1_ptr, gx2_ptr, gy2_ptr
                );
#endif // __AVX__

                // EPILOG / FALLBACK (Loop Scalar)
                for (; x < cols; ++x)
                {
                    const float pixel_diff_raw = diff_ptr[x];
                    
                    // --- APLIKASI CHARBONNIER LOSS ---
                    const float pixel_diff = charbonnier_loss(pixel_diff_raw); 
                    
                    const float gx1 = gx1_ptr[x], gy1 = gy1_ptr[x];
                    const float gx2 = gx2_ptr[x], gy2 = gy2_ptr[x];
                    const float mag1_sq = gx1 * gx1 + gy1 * gy1;
                    const float mag2_sq = gx2 * gx2 + gy2 * gy2;
                    const float min_mag_sq = std::min(mag1_sq, mag2_sq);

                    // --- NOISE WEIGHT: (Scalar, dipulihkan menggunakan noise_level) ---
                    float noise_weight = 1.0f;
                    if (noise_level > stab_epsilon)
                    {
                        if (min_mag_sq < structure_min_threshold_sq)
                        {
                            const float local_noise_threshold = adaptive_noise_threshold_1_5;
                            // Menggunakan pixel_diff (Charbonnier robustified) untuk noise check
                            if (pixel_diff < local_noise_threshold)
                            {
                                const float min_floor_weight = 0.05f; 
                                noise_weight = min_floor_weight +
                                               (1.0f - min_floor_weight) * (pixel_diff / local_noise_threshold);
                            }
                            else
                            {
                                const float ratio = std::min((pixel_diff - local_noise_threshold) / (local_noise_threshold * 1.0f), 1.0f);
                                noise_weight = 1.0f - 0.2f * ratio;
                            }
                        }
                        else
                        {
                            if (pixel_diff < adaptive_diff_threshold)
                            {
                                noise_weight = 1.15f + 0.15f * (1.0f - pixel_diff / adaptive_diff_threshold);
                            }
                            else
                            {
                                const float ratio = std::min(pixel_diff / (adaptive_diff_threshold * 4.0f), 1.0f);
                                noise_weight = 0.3f + 0.4f * (1.0f - ratio);
                            }
                        }
                    }
                    // --- AKHIR NOISE WEIGHT ---

                    // --- STRUCTURE WEIGHT ---
                    float structure_weight = 1.0f;
                    
                    if (min_mag_sq >= stab_epsilon && mag1_sq > stab_epsilon && mag2_sq > stab_epsilon)
                    {
                        const float dot_product = gx1 * gx2 + gy1 * gy2;
                        const float mag_denom = std::sqrt(mag1_sq * mag2_sq); 
                        const float cos_similarity = dot_product / mag_denom;

                        const float limiting_magnitude = std::sqrt(min_mag_sq);

                        const float similarity_score = std::max(0.0f, cos_similarity) * limiting_magnitude;

                        structure_weight = 1.0f + gradient_weight_factor * fast_tanh_pos(similarity_score * grad_sensitivity);
                    }

                    const float final_weight = structure_weight * noise_weight;
                    
                    // --- Terapkan Noise Floor Subtraction ---
                    // Menggunakan pixel_diff (Charbonnier robustified)
                    const float noise_floor = adaptive_diff_threshold;
                    const float effective_diff = std::max(0.0f, pixel_diff - noise_floor);
                    
                    total_weight += final_weight;
                    weighted_sum += effective_diff * final_weight; 
                }
            }
            return (total_weight <= stab_epsilon) ? calculate_plain_mad_32f(block1_gray, block2_gray) : (weighted_sum / total_weight);
        }
    } // namespace Internal

    // =========================================================================
    // --- Public API Functions ---
    // =========================================================================

    TileMatchResult calculate_tile_mad(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma,
        float gradient_weight_factor,
        float stability_epsilon,
        MBMBuffers &buffers) // Parameter buffers jadi tidak terpakai, tapi dibiarkan utk kompatibilitas API
    {
        TileMatchResult result;

        // 1. Validasi Dasar
        if (current_tile_gray.empty() || reference_tile_gray.empty() ||
            current_tile_gray.size() != reference_tile_gray.size())
        {
            result.success = false;
            result.mad_score = 0.0f; // Safety
            return result;
        }

        // 2. Langsung Gunakan Plain MAD (MeAD/Median Absolute Difference)
        // Kita membuang percabangan 'use_plain_mad' dan kalkulasi gradien Scharr.
        
        // Optimasi Tambahan: Jika Anda yakin input sudah float, cast tidak perlu di dalam.
        // Fungsi Internal::calculate_plain_mad_32f sudah efisien (menggunakan vector & nth_element).
        
        result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);

        // 3. Optional: Noise Weighting Sederhana (Jika Anda masih ingin adaptasi noise tanpa gradien)
        // Kalau benar-benar ingin "Murni Plain MAD", lewati langkah ini.
        // Tapi biasanya noise subtraction sederhana membantu stabilitas di area gelap.
        /* 
        float noise_floor = std::max(0.005f, global_noise_sigma * 0.2f);
        result.mad_score = std::max(0.0f, result.mad_score - noise_floor); 
        */

        result.success = true;
        return result;
    }

    TileMatchResult calculate_tile_fft(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma)
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

        if (bh < 8 || bw < 8)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            result.mad_score = Internal::calculate_fft_32f(current_tile_gray, reference_tile_gray, global_noise_sigma); // Global noise sigma digunakan kembali
        }

        result.success = true;
        return result;
    }

} // namespace MotionMatching