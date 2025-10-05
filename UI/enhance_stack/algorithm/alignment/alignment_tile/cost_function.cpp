#include "cost_function.hpp" // Sertakan header yang sesuai

#include <immintrin.h>         // Untuk intrinsik AVX
#include <cmath>               // Untuk std::fabs
#include <opencv2/imgproc.hpp> // Untuk dft, idft, dll.

#include <immintrin.h>
#include <cmath>

// Implementasi Zero-Mean SAD dengan AVX - Optimized Ultra-Fast
float block_cost_zsad_avx(const float* ref, const float* comp, int len)
{
    __m256 vsum_ref0 = _mm256_setzero_ps();
    __m256 vsum_ref1 = _mm256_setzero_ps();
    __m256 vsum_comp0 = _mm256_setzero_ps();
    __m256 vsum_comp1 = _mm256_setzero_ps();

    int i = 0;
    // Unroll x2 untuk throughput lebih tinggi
    for (; i + 16 <= len; i += 16) {
        __m256 vref0  = _mm256_loadu_ps(ref + i);
        __m256 vref1  = _mm256_loadu_ps(ref + i + 8);
        __m256 vcomp0 = _mm256_loadu_ps(comp + i);
        __m256 vcomp1 = _mm256_loadu_ps(comp + i + 8);

        vsum_ref0  = _mm256_add_ps(vsum_ref0, vref0);
        vsum_ref1  = _mm256_add_ps(vsum_ref1, vref1);
        vsum_comp0 = _mm256_add_ps(vsum_comp0, vcomp0);
        vsum_comp1 = _mm256_add_ps(vsum_comp1, vcomp1);
    }

    __m256 vsum_ref  = _mm256_add_ps(vsum_ref0, vsum_ref1);
    __m256 vsum_comp = _mm256_add_ps(vsum_comp0, vsum_comp1);

    // Horizontal sum AVX
    __m128 sum_ref_lo  = _mm256_castps256_ps128(vsum_ref);
    __m128 sum_ref_hi  = _mm256_extractf128_ps(vsum_ref, 1);
    __m128 sum_comp_lo = _mm256_castps256_ps128(vsum_comp);
    __m128 sum_comp_hi = _mm256_extractf128_ps(vsum_comp, 1);

    __m128 sum_ref128  = _mm_add_ps(sum_ref_lo, sum_ref_hi);
    __m128 sum_comp128 = _mm_add_ps(sum_comp_lo, sum_comp_hi);

    // Reduce ke scalar
    float sum_ref  = ((float*)&sum_ref128)[0] + ((float*)&sum_ref128)[1] +
                     ((float*)&sum_ref128)[2] + ((float*)&sum_ref128)[3];
    float sum_comp = ((float*)&sum_comp128)[0] + ((float*)&sum_comp128)[1] +
                     ((float*)&sum_comp128)[2] + ((float*)&sum_comp128)[3];

    // Tail handling (sisa <16)
    for (; i < len; ++i) {
        sum_ref  += ref[i];
        sum_comp += comp[i];
    }

    const float mean_ref  = sum_ref  / len;
    const float mean_comp = sum_comp / len;

    const __m256 vmean_ref  = _mm256_set1_ps(mean_ref);
    const __m256 vmean_comp = _mm256_set1_ps(mean_comp);
    const __m256 vzero_mask = _mm256_set1_ps(-0.0f); // untuk abs()

    __m256 vsum0 = _mm256_setzero_ps();
    __m256 vsum1 = _mm256_setzero_ps();

    i = 0;
    for (; i + 16 <= len; i += 16) {
        __m256 vref0  = _mm256_loadu_ps(ref + i);
        __m256 vref1  = _mm256_loadu_ps(ref + i + 8);
        __m256 vcomp0 = _mm256_loadu_ps(comp + i);
        __m256 vcomp1 = _mm256_loadu_ps(comp + i + 8);

        __m256 vdiff0 = _mm256_sub_ps(_mm256_sub_ps(vref0, vmean_ref),
                                      _mm256_sub_ps(vcomp0, vmean_comp));
        __m256 vdiff1 = _mm256_sub_ps(_mm256_sub_ps(vref1, vmean_ref),
                                      _mm256_sub_ps(vcomp1, vmean_comp));

        __m256 vabs0 = _mm256_andnot_ps(vzero_mask, vdiff0);
        __m256 vabs1 = _mm256_andnot_ps(vzero_mask, vdiff1);

        vsum0 = _mm256_add_ps(vsum0, vabs0);
        vsum1 = _mm256_add_ps(vsum1, vabs1);
    }

    __m256 vsum = _mm256_add_ps(vsum0, vsum1);
    __m128 sum_lo = _mm256_castps256_ps128(vsum);
    __m128 sum_hi = _mm256_extractf128_ps(vsum, 1);
    __m128 sum128 = _mm_add_ps(sum_lo, sum_hi);

    float total = ((float*)&sum128)[0] + ((float*)&sum128)[1] +
                  ((float*)&sum128)[2] + ((float*)&sum128)[3];

    for (; i < len; ++i) {
        float d = (ref[i] - mean_ref) - (comp[i] - mean_comp);
        total += std::fabs(d);
    }

    return total;
}
// Implementasi cost menggunakan FFT
float block_cost_fft(const cv::Mat &ref, const cv::Mat &comp)
{
    // Pastikan ukuran sama
    CV_Assert(ref.size() == comp.size());
    cv::Mat ref32, comp32;
    ref.convertTo(ref32, CV_32F);
    comp.convertTo(comp32, CV_32F);

    // Gunakan DFT untuk convolution
    cv::Mat ref_dft, comp_dft;
    cv::dft(ref32, ref_dft, cv::DFT_COMPLEX_OUTPUT);
    cv::dft(comp32, comp_dft, cv::DFT_COMPLEX_OUTPUT);

    // Hitung cross-correlation (ref * conj(comp))
    cv::Mat cross;
    cv::mulSpectrums(ref_dft, comp_dft, cross, 0, true);
    cv::idft(cross, cross, cv::DFT_REAL_OUTPUT | cv::DFT_SCALE);

    // Ambil nilai SSD = sum(ref^2) + sum(comp^2) - 2*cross
    double ref_norm = cv::norm(ref32, cv::NORM_L2SQR);
    double comp_norm = cv::norm(comp32, cv::NORM_L2SQR);
    double cross_val;
    cv::minMaxLoc(cross, &cross_val, nullptr); // ambil max correlation
    double ssd = ref_norm + comp_norm - 2.0 * cross_val;

    // Aproksimasi SAD
    return static_cast<float>(std::sqrt(ssd));
}