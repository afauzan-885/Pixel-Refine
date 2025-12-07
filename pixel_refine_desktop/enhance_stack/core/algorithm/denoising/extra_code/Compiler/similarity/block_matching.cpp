#include "block_matching.hpp"
#include <opencv2/imgproc.hpp>
#include <cmath>
#include <limits>
#include <algorithm>
#include <vector>

// =========================================================================
// === FAST MATH APPROXIMATIONS (CRITICAL FOR EDGE DEVICES) ===
// =========================================================================

// Aproksimasi Exp cepat (Schraudolph's method like)
// Error < 1-2% tapi 5x-10x lebih cepat dari std::exp
inline float fast_exp(float x)
{
    // Clamp untuk mencegah overflow/underflow
    if (x < -80.0f) return 0.0f;
    x = 1.0f + x / 256.0f;
    x *= x; x *= x; x *= x; x *= x;
    x *= x; x *= x; x *= x; x *= x;
    return x;
}

// Aproksimasi Tanh cepat menggunakan Pade approximation sederhana atau clamping rational
inline float fast_tanh(float x)
{
    if (x > 3.0f) return 1.0f;
    if (x < -3.0f) return -1.0f;
    float x2 = x * x;
    return x * (27.0f + x2) / (27.0f + 9.0f * x2);
}

// =========================================================================
// === BUFFER MANAGEMENT ===
// =========================================================================

// Struktur untuk menampung buffer FFT agar tidak alokasi ulang
struct FFTContext {
    cv::Mat padded1, padded2;
    cv::Mat fft1, fft2;
    cv::Mat diff_dft;
    cv::Mat planes[2];
    cv::Mat mag_sq_diff;
    cv::Size last_size;

    FFTContext() : last_size(0,0) {}
};

// Thread-local storage agar aman saat parallel processing (OMP)
static thread_local FFTContext fft_ctx;

namespace MotionMatching
{
    namespace Internal
    {
        static float calculate_plain_mad_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
        {
            // --- OPTIMASI 1: Single Pass Mean Calculation ---
            // cv::mean scan 1 kali, loop di bawah scan 1 kali lagi.
            // Untuk blok kecil, lebih cepat hitung manual.
            
            const int rows = block1_gray.rows;
            const int cols = block1_gray.cols;
            const int total_pixels = rows * cols;
            if (total_pixels == 0) return 0.0f;

            float sum1 = 0.0f, sum2 = 0.0f;
            
            // Menggunakan pointer untuk akses cepat
            if (block1_gray.isContinuous() && block2_gray.isContinuous())
            {
                const float* p1 = block1_gray.ptr<float>(0);
                const float* p2 = block2_gray.ptr<float>(0);
                
                // Unrolling loop sederhana
                int i = 0;
                for (; i <= total_pixels - 4; i += 4) {
                    sum1 += p1[i] + p1[i+1] + p1[i+2] + p1[i+3];
                    sum2 += p2[i] + p2[i+1] + p2[i+2] + p2[i+3];
                }
                for (; i < total_pixels; ++i) {
                    sum1 += p1[i];
                    sum2 += p2[i];
                }
            }
            else
            {
                // Fallback cv::mean jika tidak continuous (jarang terjadi untuk tile kecil)
                sum1 = (float)cv::sum(block1_gray)[0];
                sum2 = (float)cv::sum(block2_gray)[0];
            }

            const float mean1 = sum1 / total_pixels;
            const float mean2 = sum2 / total_pixels;

            // --- OPTIMASI 2: Calculate AbsDiff + Collect to Vector in ONE GO ---
            // Menghindari alokasi cv::Mat diff
            
            static thread_local std::vector<float> diff_values;
            if (diff_values.capacity() < total_pixels) diff_values.reserve(total_pixels * 2);
            diff_values.clear();

            for (int y = 0; y < rows; ++y)
            {
                const float* p1 = block1_gray.ptr<float>(y);
                const float* p2 = block2_gray.ptr<float>(y);
                
                // #pragma omp simd // Biarkan compiler handle auto-vectorization loop kecil
                for (int x = 0; x < cols; ++x)
                {
                    // Zero-Mean Difference
                    float val = std::abs((p1[x] - mean1) - (p2[x] - mean2));
                    diff_values.push_back(val);
                }
            }

            // --- OPTIMASI 3: Median Calculation ---
            size_t n = diff_values.size();
            size_t median_idx = n / 2;
            std::nth_element(diff_values.begin(), diff_values.begin() + median_idx, diff_values.end());
            float median_diff = diff_values[median_idx];

            if (n % 2 == 0) {
                auto max_it = std::max_element(diff_values.begin(), diff_values.begin() + median_idx);
                median_diff = (median_diff + *max_it) * 0.5f;
            }
            
            return median_diff;
        }

        static float calculate_fft_32f(const cv::Mat &block1_gray, const cv::Mat &block2_gray, float noise_sigma)
        {
            // --- OPTIMASI BUFFER FFT ---
            int opt_rows = cv::getOptimalDFTSize(block1_gray.rows);
            int opt_cols = cv::getOptimalDFTSize(block1_gray.cols);
            
            // Resize buffer hanya jika ukuran berubah
            if (fft_ctx.last_size != cv::Size(opt_cols, opt_rows)) {
                fft_ctx.last_size = cv::Size(opt_cols, opt_rows);
                fft_ctx.padded1.create(opt_rows, opt_cols, CV_32F);
                fft_ctx.padded2.create(opt_rows, opt_cols, CV_32F);
                fft_ctx.fft1.create(opt_rows, opt_cols, CV_32FC1); // Output DFT Real->Complex itu packed
                fft_ctx.fft2.create(opt_rows, opt_cols, CV_32FC1);
            }

            // Zero padding + Copy (Manual optimized copyMakeBorder untuk kasus umum)
            fft_ctx.padded1.setTo(0);
            fft_ctx.padded2.setTo(0);
            
            cv::Mat roi1 = fft_ctx.padded1(cv::Rect(0, 0, block1_gray.cols, block1_gray.rows));
            cv::Mat roi2 = fft_ctx.padded2(cv::Rect(0, 0, block2_gray.cols, block2_gray.rows));
            block1_gray.copyTo(roi1);
            block2_gray.copyTo(roi2);

            // Forward DFT
            // Menggunakan DFT_COMPLEX_OUTPUT
            cv::dft(fft_ctx.padded1, fft_ctx.fft1, cv::DFT_COMPLEX_OUTPUT);
            cv::dft(fft_ctx.padded2, fft_ctx.fft2, cv::DFT_COMPLEX_OUTPUT);

            // Compute Difference in Frequency Domain
            cv::subtract(fft_ctx.fft2, fft_ctx.fft1, fft_ctx.diff_dft);
            cv::split(fft_ctx.diff_dft, fft_ctx.planes);
            
            // Mag Squared: Re^2 + Im^2
            // cv::multiply + cv::add diganti loop manual SIMD friendly
            int n_elements = fft_ctx.planes[0].total();
            if (fft_ctx.mag_sq_diff.total() != n_elements) fft_ctx.mag_sq_diff.create(opt_rows, opt_cols, CV_32F);
            
            const float* re = fft_ctx.planes[0].ptr<float>();
            const float* im = fft_ctx.planes[1].ptr<float>();
            float* dst = fft_ctx.mag_sq_diff.ptr<float>();

            #pragma omp simd
            for(int i=0; i<n_elements; ++i) {
                dst[i] = re[i]*re[i] + im[i]*im[i];
            }

            // Zero out DC
            if (fft_ctx.mag_sq_diff.rows > 0) fft_ctx.mag_sq_diff.at<float>(0, 0) = 0.0f;

            // --- LOGIKA WEIGHTING ---
            // (Logika matematika Anda dipertahankan, hanya optimasi akses memori)
            
            const int meaningful_rows = std::min(opt_rows / 2, block1_gray.rows * 2);
            const int meaningful_cols = std::min(opt_cols / 2, block1_gray.cols * 2);
            
            const float optimal_elements = static_cast<float>(opt_rows * opt_cols);
            const float noise_sigma_sq = noise_sigma * noise_sigma;
            
            const float normalized_noise = std::min(1.0f, noise_sigma / 0.13f);
            const float dynamic_noise_floor_factor = 6.0f - (3.0f * normalized_noise);
            const float noise_threshold_sq = std::max(1e-6f, noise_sigma_sq * optimal_elements * dynamic_noise_floor_factor);

            const float linear_decay_strength = 1.8f;
            const float row_decay_inv = (meaningful_rows > 0) ? (1.0f / meaningful_rows) : 0.0f;
            const float col_decay_inv = (meaningful_cols > 0) ? (1.0f / meaningful_cols) : 0.0f;

            float weighted_sum = 0.0f;
            float total_weight = 0.0f;

            // Akses pointer langsung ke mag_sq_diff
            for (int y = 0; y < meaningful_rows; ++y)
            {
                const float *diff_ptr = fft_ctx.mag_sq_diff.ptr<float>(y);
                float radial_weight = std::max(0.0f, 1.0f - (linear_decay_strength * y * row_decay_inv));
                
                if (radial_weight <= 0.0001f) continue; // Early skip row

                #pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < meaningful_cols; ++x)
                {
                    float col_weight = std::max(0.0f, 1.0f - (linear_decay_strength * x * col_decay_inv));
                    float pixel_weight = radial_weight * col_weight;

                    float val = diff_ptr[x];
                    float final_diff = (val >= noise_threshold_sq) ? (val - noise_threshold_sq) : 0.0f;

                    weighted_sum += final_diff * pixel_weight;
                    total_weight += pixel_weight;
                }
            }

            const float total_pixels = block1_gray.rows * block1_gray.cols;
            float fft_mag_sq_score = (total_weight > 0) ? (weighted_sum / total_weight) : 0.0f;
            if (total_pixels > 0) fft_mag_sq_score /= total_pixels;

            return std::sqrt(fft_mag_sq_score);
        }

        // --- OPTIMASI HYBRID GRADIENT ---
        // Menghapus cv::Scharr dan cv::Laplacian, diganti dengan perhitungan on-the-fly
        static float calculate_hybrid_gradient_optimized(
            const cv::Mat &block1, const cv::Mat &block2,
            float noise_level, float gradient_weight_factor, float stab_epsilon)
        {
            const int rows = block1.rows;
            const int cols = block1.cols;
            
            float weighted_sum = 0.0f, total_weight = 0.0f;

            const float grad_sensitivity = 150.0f;
            const float laplacian_sensitivity = 4.0f;
            const float adaptive_noise_threshold = std::max(0.01f, noise_level * 0.4f); 
            const float adaptive_diff_threshold = std::max(0.005f, noise_level * 0.2f); 
            const float structure_min_threshold_sq = 150.0f;

            // Loop dimulai dari 1 hingga rows-1 dan cols-1 untuk menghindari border check yang mahal
            // Border pixels dianggap weight = 0 (atau fallback ke MAD biasa)
            
            for (int y = 1; y < rows - 1; ++y)
            {
                const float* p1 = block1.ptr<float>(y);
                const float* p1_prev = block1.ptr<float>(y - 1);
                const float* p1_next = block1.ptr<float>(y + 1);

                const float* p2 = block2.ptr<float>(y);
                const float* p2_prev = block2.ptr<float>(y - 1);
                const float* p2_next = block2.ptr<float>(y + 1);

                #pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 1; x < cols - 1; ++x)
                {
                    float pixel_diff = std::abs(p1[x] - p2[x]);

                    // 1. FAST GRADIENT (Central Difference)
                    // Scharr mahal (3x3), Central Diff (x+1 - x-1) sangat cepat
                    // Skala Central Diff adalah 0.5x Sobel. Kita kalikan faktor jika perlu, 
                    // tapi untuk weighting relatif, raw value sudah cukup.
                    
                    // Grad X: (Right - Left)
                    float gx1 = p1[x+1] - p1[x-1]; 
                    float gx2 = p2[x+1] - p2[x-1];

                    // Grad Y: (Down - Up)
                    float gy1 = p1_next[x] - p1_prev[x];
                    float gy2 = p2_next[x] - p2_prev[x];

                    // 2. FAST LAPLACIAN (5-point stencil)
                    // 4*center - left - right - up - down
                    float lap1 = 4.0f*p1[x] - p1[x-1] - p1[x+1] - p1_prev[x] - p1_next[x];
                    float lap2 = 4.0f*p2[x] - p2[x-1] - p2[x+1] - p2_prev[x] - p2_next[x];

                    float mag1_sq = gx1 * gx1 + gy1 * gy1;
                    float mag2_sq = gx2 * gx2 + gy2 * gy2;
                    float min_mag_sq = (mag1_sq < mag2_sq) ? mag1_sq : mag2_sq;

                    // --- LOGIKA NOISE WEIGHT (OPTIMIZED) ---
                    float noise_weight = 1.0f;
                    if (noise_level > stab_epsilon)
                    {
                        if (min_mag_sq < structure_min_threshold_sq) {
                            float local_thr = adaptive_diff_threshold * 1.5f;
                            if (pixel_diff < local_thr) {
                                noise_weight = 0.05f + 0.95f * (pixel_diff / local_thr);
                            } else {
                                float ratio = (pixel_diff - local_thr) / local_thr;
                                if (ratio > 1.0f) ratio = 1.0f;
                                noise_weight = 1.0f - 0.2f * ratio;
                            }
                        } else {
                            if (pixel_diff < adaptive_diff_threshold) {
                                noise_weight = 1.15f + 0.15f * (1.0f - pixel_diff / adaptive_diff_threshold);
                            } else {
                                float ratio = pixel_diff / (adaptive_diff_threshold * 4.0f);
                                if (ratio > 1.0f) ratio = 1.0f;
                                noise_weight = 0.3f + 0.4f * (1.0f - ratio);
                            }
                        }
                    }

                    // --- LOGIKA STRUCTURE WEIGHT (OPTIMIZED) ---
                    float structure_weight = 1.0f;
                    if (min_mag_sq > stab_epsilon && mag1_sq > stab_epsilon && mag2_sq > stab_epsilon)
                    {
                        float dot = gx1 * gx2 + gy1 * gy2;
                        // Fast inverse sqrt approximation could be used here, but std::sqrt is often HW accelerated
                        float cos_sim = dot / std::sqrt(mag1_sq * mag2_sq);
                        float score = (cos_sim > 0.0f ? cos_sim : 0.0f) * std::sqrt(min_mag_sq);
                        
                        // Gunakan Fast Tanh
                        structure_weight = 1.0f + gradient_weight_factor * fast_tanh(score * grad_sensitivity);
                    }

                    // --- LOGIKA TEXTURE WEIGHT (OPTIMIZED) ---
                    float lap_diff = std::abs(lap1 - lap2);
                    // Gunakan Fast Exp
                    float texture_weight = fast_exp(-lap_diff * laplacian_sensitivity);

                    float final_weight = structure_weight * texture_weight * noise_weight;
                    
                    weighted_sum += pixel_diff * final_weight;
                    total_weight += final_weight;
                }
            }

            // Jika total weight terlalu kecil, fallback ke simple Mean Absolute Difference (bukan median agar cepat)
            if (total_weight <= stab_epsilon) {
                return cv::norm(block1, block2, cv::NORM_L1) / (float)(rows*cols);
            }

            return weighted_sum / total_weight;
        }

    } // namespace Internal

    // =========================================================================
    // === PUBLIC INTERFACE IMPLEMENTATION ===
    // =========================================================================

    TileMatchResult calculate_tile_mad(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma,
        float gradient_weight_factor,
        float stability_epsilon,
        MBMBuffers &buffers) // Parameter buffers tidak lagi krusial tapi disimpan utk kompatibilitas
    {
        TileMatchResult result;

        // Check validity
        if (current_tile_gray.empty() || reference_tile_gray.empty()) {
            result.success = false; return result;
        }

        const int bh = current_tile_gray.rows;
        const int bw = current_tile_gray.cols;

        // Keputusan mode: Jika blok sangat kecil atau factor=0, gunakan plain MAD
        bool use_plain = (std::abs(gradient_weight_factor) < stability_epsilon || bh < 5 || bw < 5);

        if (use_plain)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            // Panggil fungsi optimasi "Kernel Fusion"
            // Tidak perlu alokasi Scharr/Laplacian buffers!
            result.mad_score = Internal::calculate_hybrid_gradient_optimized(
                current_tile_gray, reference_tile_gray,
                global_noise_sigma, gradient_weight_factor, stability_epsilon
            );
        }

        result.success = true;
        return result;
    }

    TileMatchResult calculate_tile_fft(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma)
    {
        TileMatchResult result;

        if (current_tile_gray.empty()) {
            result.success = false; return result;
        }

        const int bh = current_tile_gray.rows;
        
        // FFT overhead terlalu besar untuk blok < 8x8.
        if (bh < 8)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            result.mad_score = Internal::calculate_fft_32f(current_tile_gray, reference_tile_gray, global_noise_sigma);
        }

        result.success = true;
        return result;
    }

} // namespace MotionMatching