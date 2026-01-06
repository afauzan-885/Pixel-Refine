#include "cost_function.hpp" // Sertakan header yang sesuai

#include <immintrin.h>         // Untuk intrinsik AVX
#include <cmath>               // Untuk std::fabs
#include <opencv2/imgproc.hpp> // Untuk dft, idft, dll.

#include <immintrin.h>
#include <cmath>

constexpr float NORMALIZATION_EPSILON = 1e-6f;
constexpr float EPSILON_SQ            = NORMALIZATION_EPSILON * NORMALIZATION_EPSILON;

// ============================================================================
// OPTIMIZED: Zero-Mean SAD dengan AVX - Performa Maksimal, Akurasi Sama
// ============================================================================

static inline float horizontal_sum_avx(__m256 v)
{
    // Optimasi H-Sum
    __m128 vlow  = _mm256_castps256_ps128(v);
    __m128 vhigh = _mm256_extractf128_ps(v, 1);
    vlow  = _mm_add_ps(vlow, vhigh);
    __m128 shuf = _mm_movehdup_ps(vlow);
    __m128 sums = _mm_add_ps(vlow, shuf);
    shuf = _mm_movehl_ps(shuf, sums);
    sums = _mm_add_ss(sums, shuf);
    return _mm_cvtss_f32(sums);
}

// Versi FMA + Tail Optimization
static inline float block_cost_zmcl_avx(const float* ref, const float* comp, int len)
{
    // --- PASS 1: MEAN DIFFERENCE CALCULATION ---
    // Zero-mean alignment requires (ref - mean_ref) - (comp - mean_comp)
    // yang setara dengan (ref - comp) - (mean_ref - mean_comp).
    // Jadi kita cukup hitung mean dari (ref - comp).
    __m256 vsum_diff = _mm256_setzero_ps();
    int i = 0;

    // Unroll 16 for throughput
    for (; i + 16 <= len; i += 16) {
        __m256 d0 = _mm256_sub_ps(_mm256_loadu_ps(ref + i), _mm256_loadu_ps(comp + i));
        __m256 d1 = _mm256_sub_ps(_mm256_loadu_ps(ref + i + 8), _mm256_loadu_ps(comp + i + 8));
        vsum_diff = _mm256_add_ps(vsum_diff, _mm256_add_ps(d0, d1));
    }
    
    // Sisa block 8
    for (; i + 8 <= len; i += 8) {
        vsum_diff = _mm256_add_ps(vsum_diff, _mm256_sub_ps(_mm256_loadu_ps(ref + i), _mm256_loadu_ps(comp + i)));
    }

    float sum_diff = horizontal_sum_avx(vsum_diff);
    for (int k = i; k < len; ++k) {
        sum_diff += (ref[k] - comp[k]);
    }

    const float mean_diff = sum_diff / static_cast<float>(len);
    const __m256 v_mean_diff = _mm256_set1_ps(mean_diff);
    const __m256 v_eps2 = _mm256_set1_ps(EPSILON_SQ);

    // --- PASS 2: CHARBONNIER ACCUMULATION ---
    // Cost = sum( sqrt( ((r-c) - mean_diff)^2 + eps^2 ) )
    __m256 vcost = _mm256_setzero_ps();
    i = 0;

    // Unroll 16 to hide SQRT latency (SQRT is pipelined on modern CPUs)
    for (; i + 16 <= len; i += 16) {
        // Load & Diff
        __m256 d0 = _mm256_sub_ps(_mm256_sub_ps(_mm256_loadu_ps(ref + i), _mm256_loadu_ps(comp + i)), v_mean_diff);
        __m256 d1 = _mm256_sub_ps(_mm256_sub_ps(_mm256_loadu_ps(ref + i + 8), _mm256_loadu_ps(comp + i + 8)), v_mean_diff);

        // Core Charbonnier: sqrt(d^2 + eps^2)
        // Menggunakan SQRTPS langsung (lebih sedikit instruksi daripada RSQRT + MUL)
        __m256 x0 = _mm256_fmadd_ps(d0, d0, v_eps2);
        __m256 x1 = _mm256_fmadd_ps(d1, d1, v_eps2);
        
        vcost = _mm256_add_ps(vcost, _mm256_add_ps(_mm256_sqrt_ps(x0), _mm256_sqrt_ps(x1)));
    }

    for (; i + 8 <= len; i += 8) {
        __m256 d = _mm256_sub_ps(_mm256_sub_ps(_mm256_loadu_ps(ref + i), _mm256_loadu_ps(comp + i)), v_mean_diff);
        vcost = _mm256_add_ps(vcost, _mm256_sqrt_ps(_mm256_fmadd_ps(d, d, v_eps2)));
    }

    float total_cost = horizontal_sum_avx(vcost);
    for (; i < len; ++i) {
        float d = (ref[i] - comp[i]) - mean_diff;
        total_cost += std::sqrt(d * d + EPSILON_SQ);
    }

    return total_cost;
}

// =============================================================
// ===============  WRAPPER: calculate_fine_analysis  ===============
// =============================================================

float calculate_fine_analysis(const float* ref, const float* comp, int len)
{
    if (!ref || !comp || len <= 0)
        return 0.0f;

    float zmcl_cost = block_cost_zmcl_avx(ref, comp, len);

    // Kita harus menormalisasi ZMCL agar tidak didominasi oleh ukuran tile
    const float tile_area_inv = 1.0f / static_cast<float>(len);
    
    return zmcl_cost * tile_area_inv;
}

struct FFTContext {
    cv::Mat ref_dft;
    cv::Mat comp_dft;
    cv::Mat cross;
    cv::Size last_size;
    // Tambahkan buffer konversi persisten untuk menghindari alokasi ulang
    cv::Mat ref_padded_buffer;
    cv::Mat comp_padded_buffer;
    
    FFTContext() : last_size(0, 0) {}
};

thread_local FFTContext fft_ctx;
float block_cost_fft(const cv::Mat &ref, const cv::Mat &comp)
{
    // Pastikan size match
    if (ref.size() != comp.size()) return FLT_MAX;

    const int rows = ref.rows;
    const int cols = ref.cols;

    // --- 1. Context & Buffer Management (Sama seperti kode Anda) ---
    int optimal_rows = cv::getOptimalDFTSize(rows);
    int optimal_cols = cv::getOptimalDFTSize(cols);
    cv::Size optimal_size(optimal_cols, optimal_rows);

    if (fft_ctx.last_size != ref.size()) {
        fft_ctx.last_size = ref.size();
        fft_ctx.ref_dft.create(optimal_size, CV_32FC2);
        fft_ctx.comp_dft.create(optimal_size, CV_32FC2);
        fft_ctx.cross.create(optimal_size, CV_32FC2);
        fft_ctx.ref_padded_buffer.create(optimal_size, CV_32F);
        fft_ctx.comp_padded_buffer.create(optimal_size, CV_32F);
    }
    
    // --- 2. Copy & Pad ---
    fft_ctx.ref_padded_buffer.setTo(cv::Scalar::all(0));
    fft_ctx.comp_padded_buffer.setTo(cv::Scalar::all(0));

    cv::Mat roi_ref = fft_ctx.ref_padded_buffer(cv::Rect(0, 0, cols, rows));
    cv::Mat roi_comp = fft_ctx.comp_padded_buffer(cv::Rect(0, 0, cols, rows));

    // Convert ke CV_32F jika belum
    if (ref.type() == CV_32F) ref.copyTo(roi_ref);
    else ref.convertTo(roi_ref, CV_32F);

    if (comp.type() == CV_32F) comp.copyTo(roi_comp);
    else comp.convertTo(roi_comp, CV_32F);

    // --- 3. Forward DFT ---
    cv::dft(fft_ctx.ref_padded_buffer, fft_ctx.ref_dft, cv::DFT_COMPLEX_OUTPUT, rows);
    cv::dft(fft_ctx.comp_padded_buffer, fft_ctx.comp_dft, cv::DFT_COMPLEX_OUTPUT, rows);

    // --- 4. Conjugate Multiply (Cross-Power Spectrum) ---
    // Hasil: Ref * conj(Comp)
    cv::mulSpectrums(fft_ctx.ref_dft, fft_ctx.comp_dft, fft_ctx.cross, 0, true);

    // --- 5. ROBUST NORMALIZATION (Phase Correlation Step) ---
    // Inilah langkah yang setara dengan "Robust Loss".
    // Kita menormalisasi magnitudo setiap frekuensi menjadi 1 (atau mendekati 1).
    // Rumus: R = R / (|R| + epsilon)
    {
        const int total_elements = optimal_rows * optimal_cols;
        cv::Complexf* ptr = fft_ctx.cross.ptr<cv::Complexf>();
        
        // Epsilon kecil untuk mencegah pembagian nol pada frekuensi kosong
        const float eps = 1e-5f; 
        
        // Loop ini bisa di-autovectorize oleh compiler modern (-O3 / AVX2)
        // Kita bisa pakai intrinsik jika perlu, tapi loop manual seringkali cukup cepat.
        #pragma omp simd
        for (int i = 0; i < total_elements; ++i)
        {
            float re = ptr[i].re;
            float im = ptr[i].im;
            
            // Hitung magnitude
            // Kita gunakan pendekatan cepat: 1/sqrt(re^2 + im^2 + eps)
            float mag_sq = re*re + im*im;
            
            // Hanya normalisasi jika ada energy signal
            if (mag_sq > 1e-9f) {
                // Gunakan rsqrt approximation untuk kecepatan (setara _mm_rsqrt_ps)
                float inv_mag = 1.0f / (std::sqrt(mag_sq) + eps);
                
                // Normalisasi (Whitening)
                ptr[i].re = re * inv_mag;
                ptr[i].im = im * inv_mag;
            } else {
                ptr[i].re = 0;
                ptr[i].im = 0;
            }
        }
    }

    // --- 6. Inverse DFT ---
    // Hasilnya adalah peta korelasi tajam (Dirac delta function idealnya)
    cv::idft(fft_ctx.cross, fft_ctx.cross, cv::DFT_REAL_OUTPUT | cv::DFT_SCALE, rows); 

    // --- 7. Search Max Peak ---
    // Peak location = pergeseran terbaik.
    // Peak value = seberapa yakin (score).
    double max_val = 0.0;
    cv::Mat cross_valid_roi = fft_ctx.cross(cv::Rect(0, 0, cols, rows));
    
    cv::minMaxLoc(cross_valid_roi, nullptr, &max_val);

    // --- 8. Convert Correlation to "Cost" ---
    // Correlation 1.0 = Perfect Match -> Cost 0.0
    // Correlation 0.0 = No Match      -> Cost 1.0
    // Kita clamp agar aman
    float cost = 1.0f - static_cast<float>(max_val);
    
    return std::max(0.0f, cost);
}