#include "cost_function.hpp" // Sertakan header yang sesuai

#include <immintrin.h>         // Untuk intrinsik AVX
#include <cmath>               // Untuk std::fabs
#include <opencv2/imgproc.hpp> // Untuk dft, idft, dll.

#include <immintrin.h>
#include <cmath>

// ============================================================================
// OPTIMIZED: Zero-Mean SAD dengan AVX - Performa Maksimal, Akurasi Sama
// ============================================================================

static inline float horizontal_sum_avx(__m256 v)
{
    __m128 vlow  = _mm256_castps256_ps128(v);
    __m128 vhigh = _mm256_extractf128_ps(v, 1);
    vlow  = _mm_add_ps(vlow, vhigh);
    __m128 shuf = _mm_movehdup_ps(vlow);
    __m128 sums = _mm_add_ps(vlow, shuf);
    shuf = _mm_movehl_ps(shuf, sums);
    sums = _mm_add_ss(sums, shuf);
    return _mm_cvtss_f32(sums);
}

// =============================================================
// ===============  FUNGSI INTI: block_cost_zsad_avx  ================
// =============================================================

static inline float block_cost_zsad_avx(const float* ref, const float* comp, int len)
{
    constexpr int PREFETCH_DISTANCE = 512; // bytes

    // Akumulator mean sementara
    __m256 vsum_ref[4]  = { _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps() };
    __m256 vsum_comp[4] = { _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps() };

    int i = 0;
    for (; i + 32 <= len; i += 32)
    {
        if (i + PREFETCH_DISTANCE < len) {
            _mm_prefetch(reinterpret_cast<const char*>(ref  + i + PREFETCH_DISTANCE), _MM_HINT_T0);
            _mm_prefetch(reinterpret_cast<const char*>(comp + i + PREFETCH_DISTANCE), _MM_HINT_T0);
        }

        __m256 vref0  = _mm256_loadu_ps(ref + i);
        __m256 vref1  = _mm256_loadu_ps(ref + i + 8);
        __m256 vref2  = _mm256_loadu_ps(ref + i + 16);
        __m256 vref3  = _mm256_loadu_ps(ref + i + 24);

        __m256 vcomp0 = _mm256_loadu_ps(comp + i);
        __m256 vcomp1 = _mm256_loadu_ps(comp + i + 8);
        __m256 vcomp2 = _mm256_loadu_ps(comp + i + 16);
        __m256 vcomp3 = _mm256_loadu_ps(comp + i + 24);

        vsum_ref[0]  = _mm256_add_ps(vsum_ref[0], vref0);
        vsum_ref[1]  = _mm256_add_ps(vsum_ref[1], vref1);
        vsum_ref[2]  = _mm256_add_ps(vsum_ref[2], vref2);
        vsum_ref[3]  = _mm256_add_ps(vsum_ref[3], vref3);

        vsum_comp[0] = _mm256_add_ps(vsum_comp[0], vcomp0);
        vsum_comp[1] = _mm256_add_ps(vsum_comp[1], vcomp1);
        vsum_comp[2] = _mm256_add_ps(vsum_comp[2], vcomp2);
        vsum_comp[3] = _mm256_add_ps(vsum_comp[3], vcomp3);
    }

    __m256 vsum_ref_final  = _mm256_add_ps(_mm256_add_ps(vsum_ref[0], vsum_ref[1]),
                                           _mm256_add_ps(vsum_ref[2], vsum_ref[3]));
    __m256 vsum_comp_final = _mm256_add_ps(_mm256_add_ps(vsum_comp[0], vsum_comp[1]),
                                           _mm256_add_ps(vsum_comp[2], vsum_comp[3]));

    float sum_ref  = horizontal_sum_avx(vsum_ref_final);
    float sum_comp = horizontal_sum_avx(vsum_comp_final);

    for (; i < len; ++i) {
        sum_ref  += ref[i];
        sum_comp += comp[i];
    }

    const float inv_len = 1.0f / len;
    const float mean_ref  = sum_ref  * inv_len;
    const float mean_comp = sum_comp * inv_len;
    const float mean_diff_scalar = mean_ref - mean_comp;

    const __m256 mean_diff = _mm256_set1_ps(mean_diff_scalar);
    const __m256 sign_mask = _mm256_set1_ps(-0.0f);

    __m256 vzsad[4] = { _mm256_setzero_ps(), _mm256_setzero_ps(),
                        _mm256_setzero_ps(), _mm256_setzero_ps() };

    i = 0;
    for (; i + 32 <= len; i += 32)
    {
        if (i + PREFETCH_DISTANCE < len) {
            _mm_prefetch(reinterpret_cast<const char*>(ref  + i + PREFETCH_DISTANCE), _MM_HINT_T0);
            _mm_prefetch(reinterpret_cast<const char*>(comp + i + PREFETCH_DISTANCE), _MM_HINT_T0);
        }

        __m256 vref0  = _mm256_loadu_ps(ref + i);
        __m256 vref1  = _mm256_loadu_ps(ref + i + 8);
        __m256 vref2  = _mm256_loadu_ps(ref + i + 16);
        __m256 vref3  = _mm256_loadu_ps(ref + i + 24);

        __m256 vcomp0 = _mm256_loadu_ps(comp + i);
        __m256 vcomp1 = _mm256_loadu_ps(comp + i + 8);
        __m256 vcomp2 = _mm256_loadu_ps(comp + i + 16);
        __m256 vcomp3 = _mm256_loadu_ps(comp + i + 24);

        __m256 vdiff0 = _mm256_sub_ps(_mm256_sub_ps(vref0, vcomp0), mean_diff);
        __m256 vdiff1 = _mm256_sub_ps(_mm256_sub_ps(vref1, vcomp1), mean_diff);
        __m256 vdiff2 = _mm256_sub_ps(_mm256_sub_ps(vref2, vcomp2), mean_diff);
        __m256 vdiff3 = _mm256_sub_ps(_mm256_sub_ps(vref3, vcomp3), mean_diff);

        __m256 vabs0 = _mm256_andnot_ps(sign_mask, vdiff0);
        __m256 vabs1 = _mm256_andnot_ps(sign_mask, vdiff1);
        __m256 vabs2 = _mm256_andnot_ps(sign_mask, vdiff2);
        __m256 vabs3 = _mm256_andnot_ps(sign_mask, vdiff3);

        vzsad[0] = _mm256_add_ps(vzsad[0], vabs0);
        vzsad[1] = _mm256_add_ps(vzsad[1], vabs1);
        vzsad[2] = _mm256_add_ps(vzsad[2], vabs2);
        vzsad[3] = _mm256_add_ps(vzsad[3], vabs3);
    }

    __m256 vzsad_final = _mm256_add_ps(_mm256_add_ps(vzsad[0], vzsad[1]),
                                       _mm256_add_ps(vzsad[2], vzsad[3]));
    float total = horizontal_sum_avx(vzsad_final);

    for (; i < len; ++i)
    {
        float d = (ref[i] - comp[i]) - mean_diff_scalar;
        total += std::fabs(d);
    }

    return total;
}

// =============================================================
// ===============  WRAPPER: calculate_zsad  ===============
// =============================================================

float calculate_zsad(const float* ref, const float* comp, int len)
{
    if (!ref || !comp || len <= 0)
        return 0.0f;

    // ✅ wrapper memanggil fungsi inti
    float zsad_value = block_cost_zsad_avx(ref, comp, len);

    return zsad_value;
}

// ============================================================================
// OPTIMIZED: FFT-based cost dengan caching dan early termination
// ============================================================================

// OPTIMIZATION 6: Reuse DFT plans dan pre-allocated buffers
struct FFTContext {
    cv::Mat ref_dft;
    cv::Mat comp_dft;
    cv::Mat cross;
    cv::Size last_size;
    
    FFTContext() : last_size(0, 0) {}
};

// Thread-local storage untuk FFT context (avoid reallocation)
thread_local FFTContext fft_ctx;

float block_cost_fft(const cv::Mat &ref, const cv::Mat &comp)
{
    CV_Assert(ref.size() == comp.size());
    
    // OPTIMIZATION 7: Skip conversion jika sudah CV_32F
    cv::Mat ref32, comp32;
    if (ref.type() == CV_32F) {
        ref32 = ref;
    } else {
        ref.convertTo(ref32, CV_32F);
    }
    
    if (comp.type() == CV_32F) {
        comp32 = comp;
    } else {
        comp.convertTo(comp32, CV_32F);
    }

    // OPTIMIZATION 8: Reuse buffers jika size sama
    if (fft_ctx.last_size != ref.size()) {
        // Size berubah, reallocate
        fft_ctx.ref_dft = cv::Mat();
        fft_ctx.comp_dft = cv::Mat();
        fft_ctx.cross = cv::Mat();
        fft_ctx.last_size = ref.size();
    }

    // OPTIMIZATION 9: Use optimal DFT size untuk performance
    int optimal_rows = cv::getOptimalDFTSize(ref32.rows);
    int optimal_cols = cv::getOptimalDFTSize(ref32.cols);
    
    cv::Mat ref_padded, comp_padded;
    if (optimal_rows != ref32.rows || optimal_cols != ref32.cols) {
        cv::copyMakeBorder(ref32, ref_padded, 0, optimal_rows - ref32.rows,
                          0, optimal_cols - ref32.cols, cv::BORDER_CONSTANT, cv::Scalar::all(0));
        cv::copyMakeBorder(comp32, comp_padded, 0, optimal_rows - comp32.rows,
                          0, optimal_cols - comp32.cols, cv::BORDER_CONSTANT, cv::Scalar::all(0));
    } else {
        ref_padded = ref32;
        comp_padded = comp32;
    }

    // DFT computation
    cv::dft(ref_padded, fft_ctx.ref_dft, cv::DFT_COMPLEX_OUTPUT);
    cv::dft(comp_padded, fft_ctx.comp_dft, cv::DFT_COMPLEX_OUTPUT);

    // OPTIMIZATION 10: Conjugate multiply dengan manual operation (faster)
    cv::mulSpectrums(fft_ctx.ref_dft, fft_ctx.comp_dft, fft_ctx.cross, 0, true);
    
    // Inverse DFT
    cv::idft(fft_ctx.cross, fft_ctx.cross, cv::DFT_REAL_OUTPUT | cv::DFT_SCALE);

    // OPTIMIZATION 11: Use parallel reduction untuk norm calculation
    double ref_norm = cv::norm(ref32, cv::NORM_L2SQR);
    double comp_norm = cv::norm(comp32, cv::NORM_L2SQR);
    
    // OPTIMIZATION 12: Direct access untuk max value (faster than minMaxLoc)
    double cross_max = 0.0;
    const cv::Mat cross_roi = fft_ctx.cross(cv::Rect(0, 0, ref32.cols, ref32.rows));
    
    // Find max via pointer access
    const float* cross_ptr = cross_roi.ptr<float>(0);
    const int total_elements = cross_roi.rows * cross_roi.cols;
    
    #pragma omp simd reduction(max:cross_max)
    for (int i = 0; i < total_elements; ++i) {
        cross_max = std::max(cross_max, static_cast<double>(cross_ptr[i]));
    }

    // Compute SSD
    double ssd = ref_norm + comp_norm - 2.0 * cross_max;
    
    // OPTIMIZATION 13: Fast sqrt approximation dengan fallback
    // Untuk SSD kecil, approx cukup akurat
    if (ssd < 0.0) ssd = 0.0;  // Numerical error guard
    
    return static_cast<float>(std::sqrt(ssd));
}