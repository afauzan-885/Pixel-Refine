#include "cost_function.hpp" // Sertakan header yang sesuai

#include <immintrin.h>         // Untuk intrinsik AVX
#include <cmath>               // Untuk std::fabs
#include <opencv2/imgproc.hpp> // Untuk dft, idft, dll.

// Implementasi Zero-Mean SAD dengan AVX
float block_cost_zsad_avx(const float* ref, const float* comp, int len)
{
    // ===== 1. Hitung sum_ref & sum_comp =====
    __m256 vsum_ref = _mm256_setzero_ps();
    __m256 vsum_comp = _mm256_setzero_ps();

    int i = 0;
    for (; i + 8 <= len; i += 8) {
        __m256 vref  = _mm256_loadu_ps(ref + i);
        __m256 vcomp = _mm256_loadu_ps(comp + i);

        vsum_ref  = _mm256_add_ps(vsum_ref, vref);
        vsum_comp = _mm256_add_ps(vsum_comp, vcomp);
    }

    float buf_ref[8], buf_comp[8];
    _mm256_storeu_ps(buf_ref, vsum_ref);
    _mm256_storeu_ps(buf_comp, vsum_comp);

    float sum_ref = buf_ref[0] + buf_ref[1] + buf_ref[2] + buf_ref[3] +
                    buf_ref[4] + buf_ref[5] + buf_ref[6] + buf_ref[7];
    float sum_comp = buf_comp[0] + buf_comp[1] + buf_comp[2] + buf_comp[3] +
                     buf_comp[4] + buf_comp[5] + buf_comp[6] + buf_comp[7];

    // Tail handling (sisa < 8 elemen)
    for (; i < len; i++) {
        sum_ref  += ref[i];
        sum_comp += comp[i];
    }

    float mean_ref  = sum_ref  / len;
    float mean_comp = sum_comp / len;

    __m256 vmean_ref  = _mm256_set1_ps(mean_ref);
    __m256 vmean_comp = _mm256_set1_ps(mean_comp);

    // ===== 2. Hitung ZSAD =====
    __m256 vsum = _mm256_setzero_ps();
    i = 0;
    for (; i + 8 <= len; i += 8) {
        __m256 vref  = _mm256_loadu_ps(ref + i);
        __m256 vcomp = _mm256_loadu_ps(comp + i);

        __m256 vref_norm  = _mm256_sub_ps(vref, vmean_ref);
        __m256 vcomp_norm = _mm256_sub_ps(vcomp, vmean_comp);
        __m256 vdiff      = _mm256_sub_ps(vref_norm, vcomp_norm);

        __m256 vabs = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), vdiff); // abs()
        vsum = _mm256_add_ps(vsum, vabs);
    }

    float buf[8];
    _mm256_storeu_ps(buf, vsum);
    float total = buf[0] + buf[1] + buf[2] + buf[3] +
                  buf[4] + buf[5] + buf[6] + buf[7];

    for (; i < len; i++) {
        total += std::fabs((ref[i] - mean_ref) - (comp[i] - mean_comp));
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