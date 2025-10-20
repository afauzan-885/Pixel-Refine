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
            if (total_pixels == 0)
                return 0.0f;

            // =========================================================================
            // --- LANGKAH 1: Zero-Mean Normalization (ZMN) untuk Robustness terhadap Flicker ---
            // =========================================================================
            
            // Hitung rata-rata (mean) dari setiap blok
            cv::Scalar mean1 = cv::mean(block1_gray);
            cv::Scalar mean2 = cv::mean(block2_gray);
            
            // Kurangi mean dari setiap blok.
            // cv::MatExpr (hasil dari operasi Mat - Scalar) digunakan untuk operasi cepat.
            cv::Mat block1_zm = block1_gray - mean1[0];
            cv::Mat block2_zm = block2_gray - mean2[0];
            
            // Hitung selisih absolut pada blok yang sudah dinormalisasi (Zero-Mean)
            cv::Mat diff;
            cv::absdiff(block1_zm, block2_zm, diff);
            
            // =========================================================================
            // --- LANGKAH 2: Hitung Median Absolute Difference (MeAD) ---
            // =========================================================================
            
            std::vector<float> diff_values;
            diff_values.reserve(total_pixels);
            
            // Salin data Mat diff (selisih absolut) ke vector untuk pengurutan cepat
            if (diff.isContinuous()) {
                // Salin semua data sekaligus jika Mat kontinyu
                diff_values.assign((float*)diff.datastart, (float*)diff.dataend);
            } else {
                // Jika tidak, salin baris demi baris
                for (int i = 0; i < diff.rows; ++i) {
                    diff_values.insert(diff_values.end(), diff.ptr<float>(i), diff.ptr<float>(i) + diff.cols);
                }
            }
            
            size_t n = diff_values.size();
            if (n == 0) return 0.0f;
            
            // Gunakan std::nth_element untuk menemukan elemen median (O(N) rata-rata)
            size_t median_idx = n / 2;
            std::nth_element(diff_values.begin(), diff_values.begin() + median_idx, diff_values.end());
            
            float median_diff = diff_values[median_idx];
            
            // Jika jumlah piksel genap, rata-rata dua elemen tengah
            if (n % 2 == 0) {
                // Temukan elemen yang lebih rendah (median_idx - 1)
                // Kita hanya perlu mencari di bagian diff_values.begin() hingga diff_values.begin() + median_idx
                std::nth_element(diff_values.begin(), diff_values.begin() + median_idx - 1, diff_values.begin() + median_idx);
                median_diff = (median_diff + diff_values[median_idx - 1]) / 2.0f;
            }
            
            return median_diff;
        }

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

            const int meaningful_rows = std::min(opt_rows / 2, block1_gray.rows * 2);
            const int meaningful_cols = std::min(opt_cols / 2, block1_gray.cols * 2);
            cv::Rect roi_freq(0, 0, meaningful_cols, meaningful_rows);
            cv::Mat mag_sq_diff_roi = mag_sq_diff(roi_freq);
            // ------------------------------------

            // --- LOGIKA NOISE ADAPTIF DENGAN FAKTOR DINAMIS ---
            const float optimal_elements = static_cast<float>(opt_rows * opt_cols);
            const float noise_sigma_sq = noise_sigma * noise_sigma;
            const float theoretical_noise_power_floor = noise_sigma_sq * optimal_elements;

            // Dynamic Noise Floor Factor: Disesuaikan untuk Sensitivitas Kontras Rendah
            // PENTING: Ambang batas noise yang lebih tinggi untuk normalisasi
            const float normalized_noise = std::min(1.0f, noise_sigma / 0.13f); // DARI 0.05 MENJADI 0.10
            const float min_factor = 3.0f;                                      // Lebih stabil saat noisy
            const float max_factor = 6.0f;                                      // Lebih ketat saat bersih
            const float dynamic_noise_floor_factor = max_factor - (max_factor - min_factor) * normalized_noise;

            const float stability_constant = 1e-6f;
            const float noise_threshold_sq = std::max(stability_constant, theoretical_noise_power_floor * dynamic_noise_floor_factor);

            // Hitung weighted mean: bobot lebih tinggi pada frekuensi rendah
            float weighted_sum = 0.0f;
            float total_weight = 0.0f;

            // FAKTOR PENURUNAN LINEAR: DILEMBUTKAN (Mempertahankan detail halus)
            const float linear_decay_strength = 1.8f;
            const float max_row_val = static_cast<float>(mag_sq_diff_roi.rows);
            const float max_col_val = static_cast<float>(mag_sq_diff_roi.cols);
            const float row_decay_inv = (max_row_val > 0.0f) ? (1.0f / max_row_val) : 0.0f;
            const float col_decay_inv = (max_col_val > 0.0f) ? (1.0f / max_col_val) : 0.0f;

            for (int y = 0; y < mag_sq_diff_roi.rows; ++y)
            {
                const float *__restrict diff_ptr = mag_sq_diff_roi.ptr<float>(y);

                // Bobot menurun LINEAR
                float radial_weight_linear = 1.0f - (linear_decay_strength * y * row_decay_inv);
                float radial_weight = std::max(0.0f, radial_weight_linear);

#pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < mag_sq_diff_roi.cols; ++x)
                {
                    float col_weight_linear = 1.0f - (linear_decay_strength * x * col_decay_inv);
                    float col_weight = std::max(0.0f, col_weight_linear);

                    float pixel_weight = radial_weight * col_weight;

                    float pixel_mag_sq_diff = diff_ptr[x];

                    // Soft Thresholding: Mengambil hanya sinyal di atas noise_floor
                    float final_diff_value = 0.0f;
                    if (pixel_mag_sq_diff >= noise_threshold_sq)
                    {
                        // Soft Thresholding: Menghapus noise power yang terkandung dalam sinyal
                        final_diff_value = pixel_mag_sq_diff - noise_threshold_sq;
                    }

                    weighted_sum += final_diff_value * pixel_weight;
                    total_weight += pixel_weight;
                }
            }

            // Normalisasi: Normalisasi terhadap ukuran blok ASLI (total_pixels)
            const float normalization_factor = static_cast<float>(total_pixels);

            float fft_mag_sq_score = (total_weight > 0) ? (weighted_sum / total_weight) : 0.0f;

            // Normalisasi terhadap ukuran blok spasial
            if (normalization_factor > 0)
            {
                fft_mag_sq_score /= normalization_factor;
            }

            float fft_score = std::sqrt(fft_mag_sq_score);

            return fft_score;
        }

        // --- FUNGSI UTAMA YANG DIMODIFIKASI: Sekarang juga menerima hasil Laplacian ---
        static float calculate_hybrid_gradient_weighted_mad(
            const cv::Mat &block1_gray, const cv::Mat &block2_gray,
            const cv::Mat &grad_x1, const cv::Mat &grad_y1,
            const cv::Mat &grad_x2, const cv::Mat &grad_y2,
            const cv::Mat &laplacian1, const cv::Mat &laplacian2,
            const cv::Mat &abs_diff_block, float noise_level,
            float gradient_weight_factor, float stab_epsilon)
        {
            const int rows = block1_gray.rows, cols = block1_gray.cols;
            float weighted_sum = 0.0f, total_weight = 0.0f;

            // Parameter Adaptasi:
            const float grad_sensitivity = 150.0f;
            const float laplacian_sensitivity = 4.0f;

            // Ambang batas noise spasial (Disesuaikan agar lebih agresif terhadap noise tinggi)
            const float adaptive_noise_threshold = std::max(0.01f, noise_level * 0.4f); 
            const float adaptive_diff_threshold = std::max(0.005f, noise_level * 0.2f); 

            // Konstanta baru untuk menentukan 'struktur yang signifikan'
            const float structure_min_threshold_sq = 150.0f; // TETAP

            for (int y = 0; y < rows; ++y)
            {
                const float *__restrict diff_ptr = abs_diff_block.ptr<float>(y);
                const float *__restrict gx1_ptr = grad_x1.ptr<float>(y);
                const float *__restrict gy1_ptr = grad_y1.ptr<float>(y);
                const float *__restrict gx2_ptr = grad_x2.ptr<float>(y);
                const float *__restrict gy2_ptr = grad_y2.ptr<float>(y);
                const float *__restrict l1_ptr = laplacian1.ptr<float>(y);
                const float *__restrict l2_ptr = laplacian2.ptr<float>(y);

#pragma omp simd reduction(+ : weighted_sum, total_weight)
                for (int x = 0; x < cols; ++x)
                {
                    const float pixel_diff = diff_ptr[x];

                    const float gx1 = gx1_ptr[x], gy1 = gy1_ptr[x];
                    const float gx2 = gx2_ptr[x], gy2 = gy2_ptr[x];
                    const float mag1_sq = gx1 * gx1 + gy1 * gy1;
                    const float mag2_sq = gx2 * gx2 + gy2 * gy2;
                    const float min_mag_sq = std::min(mag1_sq, mag2_sq);

                    // --- NOISE WEIGHT: Penanganan Adaptif Berdasarkan Tingkat Struktur ---
                    float noise_weight = 1.0f;
                    if (noise_level > stab_epsilon)
                    {
                        if (min_mag_sq < structure_min_threshold_sq)
                        {
                            // AREA POLOS: Harder Noise Thresholding
                            const float local_noise_threshold = adaptive_diff_threshold * 1.5f;
                            if (pixel_diff < local_noise_threshold)
                            {
                                // PERUBAHAN A: Jika perbedaan di bawah ambang batas noise, RENTAN (bobot rendah)
                                const float min_floor_weight = 0.05f; 
                                noise_weight = min_floor_weight +
                                               (1.0f - min_floor_weight) * (pixel_diff / local_noise_threshold);
                            }
                            else
                            {
                                // PERUBAHAN B: Jika perbedaan di ATAS ambang batas noise, KITA ANGGAP STRUKTUR.
                                // Ini adalah gerakan/struktur yang signifikan di area datar (sky/wall).
                                // Bobot hampir 1.0, hanya sedikit damping (lebih konservatif dari area bertekstur)
                                const float ratio = std::min((pixel_diff - local_noise_threshold) / (local_noise_threshold * 1.0f), 1.0f);
                                noise_weight = 1.0f - 0.2f * ratio; // Damping maksimal 20%
                            }
                        }
                        else
                        {
                            // AREA KAYA STRUKTUR: Logika peningkat bobot yang dimoderasi (mengurangi false positive)
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

                    // --- STRUCTURE WEIGHT: Pembatasan oleh Struktur Terlemah ---
                    float structure_weight = 1.0f;
                    
                    if (min_mag_sq < stab_epsilon) { // Area Datar (Gradien hampir nol)
                         // PERUBAHAN C: Atur bobot struktur di area datar menjadi 1.0
                         // Perbedaan struktural ditangani oleh NOISE_WEIGHT di atas
                         structure_weight = 1.0f; 
                    }
                    else if (mag1_sq > stab_epsilon && mag2_sq > stab_epsilon)
                    {
                        // Area Bertekstur (TETAP)
                        const float dot_product = gx1 * gx2 + gy1 * gy2;
                        const float mag_denom = std::sqrt(mag1_sq * mag2_sq);
                        const float cos_similarity = dot_product / mag_denom;

                        const float limiting_magnitude = std::sqrt(min_mag_sq);

                        const float similarity_score = std::max(0.0f, cos_similarity) * limiting_magnitude;

                        structure_weight = 1.0f + gradient_weight_factor * std::tanh(similarity_score * grad_sensitivity);
                    }
                    // --- AKHIR STRUCTURE WEIGHT ---

                    // Texture Weight (dari Laplacian - tidak berubah)
                    const float l1 = l1_ptr[x], l2 = l2_ptr[x];
                    const float laplacian_diff = std::abs(l1 - l2);
                    const float texture_weight = std::exp(-laplacian_diff * laplacian_sensitivity);

                    const float final_weight = structure_weight * texture_weight * noise_weight;
                    total_weight += final_weight;
                    weighted_sum += pixel_diff * final_weight;
                }
            }
            return (total_weight <= stab_epsilon) ? calculate_plain_mad_32f(block1_gray, block2_gray) : (weighted_sum / total_weight);
        }
    } // namespace Internal

    // --- FUNGSI PUBLIK: MAD Spatial
    TileMatchResult calculate_tile_mad(
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
            cv::Mat grad_x_current = buffers.grad_x(roi);
            cv::Mat grad_y_current = buffers.grad_y(roi);
            cv::Mat grad_x_ref = buffers.grad_mag_current(roi);
            cv::Mat grad_y_ref = buffers.diff_workspace(roi);

            cv::Scharr(current_tile_gray, grad_x_current, CV_32F, 1, 0);
            cv::Scharr(current_tile_gray, grad_y_current, CV_32F, 0, 1);
            cv::Scharr(reference_tile_gray, grad_x_ref, CV_32F, 1, 0);
            cv::Scharr(reference_tile_gray, grad_y_ref, CV_32F, 0, 1);

            cv::Mat laplacian_current(cv::Size(bw, bh), CV_32F);
            cv::Mat laplacian_ref(cv::Size(bw, bh), CV_32F);

            cv::Laplacian(current_tile_gray, laplacian_current, CV_32F, 3);
            cv::Laplacian(reference_tile_gray, laplacian_ref, CV_32F, 3);

            cv::Mat abs_diff_block(cv::Size(bw, bh), CV_32FC1);
            cv::absdiff(current_tile_gray, reference_tile_gray, abs_diff_block);

            result.mad_score = Internal::calculate_hybrid_gradient_weighted_mad(
                current_tile_gray, reference_tile_gray,
                grad_x_current, grad_y_current,
                grad_x_ref, grad_y_ref,
                laplacian_current, laplacian_ref,
                abs_diff_block,
                global_noise_sigma,
                gradient_weight_factor, stability_epsilon);
        }

        result.success = true;
        return result;
    }

    // --- FUNGSI PUBLIK BARU: FFT-based similarity ---
    TileMatchResult calculate_tile_fft(
        const cv::Mat &current_tile_gray,
        const cv::Mat &reference_tile_gray,
        float global_noise_sigma) // TAMBAHAN: global_noise_sigma
    {
        TileMatchResult result;

        if (current_tile_gray.empty() || reference_tile_gray.empty() ||
            current_tile_gray.size() != reference_tile_gray.size())
        {
            result.success = false;
            return result;
        }

        // FFT bekerja optimal pada block yang cukup besar (min 8x8)
        // Untuk block kecil, fallback ke plain MAD
        const int bh = current_tile_gray.rows;
        const int bw = current_tile_gray.cols;

        if (bh < 8 || bw < 8)
        {
            result.mad_score = Internal::calculate_plain_mad_32f(current_tile_gray, reference_tile_gray);
        }
        else
        {
            // Meneruskan global_noise_sigma ke fungsi internal
            result.mad_score = Internal::calculate_fft_32f(current_tile_gray, reference_tile_gray, global_noise_sigma);
        }

        result.success = true;
        return result;
    }

} // namespace MotionMatching