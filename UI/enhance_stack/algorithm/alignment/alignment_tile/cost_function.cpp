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
    // --- PASS 1: MEAN CALCULATION ---
    __m256 vsum_ref[4]  = { _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps() };
    __m256 vsum_comp[4] = { _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps(), _mm256_setzero_ps() };

    int i = 0;
    
    // 1.a Main Loop (Unroll 32)
    for (; i + 32 <= len; i += 32)
    {
        // Load Ref
        __m256 r0 = _mm256_loadu_ps(ref + i);
        __m256 r1 = _mm256_loadu_ps(ref + i + 8);
        __m256 r2 = _mm256_loadu_ps(ref + i + 16);
        __m256 r3 = _mm256_loadu_ps(ref + i + 24);

        // Load Comp
        __m256 c0 = _mm256_loadu_ps(comp + i);
        __m256 c1 = _mm256_loadu_ps(comp + i + 8);
        __m256 c2 = _mm256_loadu_ps(comp + i + 16);
        __m256 c3 = _mm256_loadu_ps(comp + i + 24);

        // Accumulate
        vsum_ref[0] = _mm256_add_ps(vsum_ref[0], r0);
        vsum_ref[1] = _mm256_add_ps(vsum_ref[1], r1);
        vsum_ref[2] = _mm256_add_ps(vsum_ref[2], r2);
        vsum_ref[3] = _mm256_add_ps(vsum_ref[3], r3);

        vsum_comp[0] = _mm256_add_ps(vsum_comp[0], c0);
        vsum_comp[1] = _mm256_add_ps(vsum_comp[1], c1);
        vsum_comp[2] = _mm256_add_ps(vsum_comp[2], c2);
        vsum_comp[3] = _mm256_add_ps(vsum_comp[3], c3);
    }

    // Collapse Accumulators Pass 1
    __m256 vsum_ref_final  = _mm256_add_ps(_mm256_add_ps(vsum_ref[0], vsum_ref[1]),
                                           _mm256_add_ps(vsum_ref[2], vsum_ref[3]));
    __m256 vsum_comp_final = _mm256_add_ps(_mm256_add_ps(vsum_comp[0], vsum_comp[1]),
                                           _mm256_add_ps(vsum_comp[2], vsum_comp[3]));

    float sum_ref  = horizontal_sum_avx(vsum_ref_final);
    float sum_comp = horizontal_sum_avx(vsum_comp_final);

    // 1.b Intermediate Loop (Handle sisa block 8)
    // Ini penting agar tidak jatuh ke scalar loop terlalu banyak
    for (; i + 8 <= len; i += 8) {
        __m256 r = _mm256_loadu_ps(ref + i);
        __m256 c = _mm256_loadu_ps(comp + i);
        // Kita simpan ke accumulator lokal scalar via hsum nanti, 
        // atau update vsum_ref_final (lebih mudah update sum scalar langsung untuk pass ini)
        sum_ref += horizontal_sum_avx(r);
        sum_comp += horizontal_sum_avx(c);
    }

    // 1.c Scalar Loop (Handle sisa < 8)
    // Variable 'temp_i' untuk Pass 2 nanti
    int start_residual = i; 
    for (int k = i; k < len; ++k) {
        sum_ref  += ref[k];
        sum_comp += comp[k];
    }

    const float inv_len = 1.0f / static_cast<float>(len);
    const float mean_diff_scalar = (sum_ref - sum_comp) * inv_len;

    // Persiapkan konstanta untuk Pass 2
    const __m256 v_mean_diff = _mm256_set1_ps(mean_diff_scalar);
    const __m256 v_epsilon_sq = _mm256_set1_ps(EPSILON_SQ); 

    // --- PASS 2: CHARBONNIER COST (FMA OPTIMIZED) ---
    __m256 vcharb_sum[4] = { _mm256_setzero_ps(), _mm256_setzero_ps(),
                             _mm256_setzero_ps(), _mm256_setzero_ps() };

    i = 0;
    // 2.a Main Loop (Unroll 32)
    for (; i + 32 <= len; i += 32)
    {
        // Load Ref & Comp
        __m256 r0 = _mm256_loadu_ps(ref + i);
        __m256 r1 = _mm256_loadu_ps(ref + i + 8);
        __m256 r2 = _mm256_loadu_ps(ref + i + 16);
        __m256 r3 = _mm256_loadu_ps(ref + i + 24);

        __m256 c0 = _mm256_loadu_ps(comp + i);
        __m256 c1 = _mm256_loadu_ps(comp + i + 8);
        __m256 c2 = _mm256_loadu_ps(comp + i + 16);
        __m256 c3 = _mm256_loadu_ps(comp + i + 24);

        // Diff = (R - C) - MeanDiff
        // Kita gabung R-C dulu, baru subtract mean
        __m256 d0 = _mm256_sub_ps(_mm256_sub_ps(r0, c0), v_mean_diff);
        __m256 d1 = _mm256_sub_ps(_mm256_sub_ps(r1, c1), v_mean_diff);
        __m256 d2 = _mm256_sub_ps(_mm256_sub_ps(r2, c2), v_mean_diff);
        __m256 d3 = _mm256_sub_ps(_mm256_sub_ps(r3, c3), v_mean_diff);

        // Charbonnier Core: sqrt(d^2 + eps^2)
        // OPTIMASI: Menggunakan FMA (Fused Multiply Add) -> result = (a * b) + c
        // X = d*d + eps_sq
        __m256 x0 = _mm256_fmadd_ps(d0, d0, v_epsilon_sq);
        __m256 x1 = _mm256_fmadd_ps(d1, d1, v_epsilon_sq);
        __m256 x2 = _mm256_fmadd_ps(d2, d2, v_epsilon_sq);
        __m256 x3 = _mm256_fmadd_ps(d3, d3, v_epsilon_sq);

        // Approximation 1/sqrt(x)
        __m256 inv_sqrt0 = _mm256_rsqrt_ps(x0);
        __m256 inv_sqrt1 = _mm256_rsqrt_ps(x1);
        __m256 inv_sqrt2 = _mm256_rsqrt_ps(x2);
        __m256 inv_sqrt3 = _mm256_rsqrt_ps(x3);

        // sqrt(x) = x * 1/sqrt(x)
        vcharb_sum[0] = _mm256_add_ps(vcharb_sum[0], _mm256_mul_ps(x0, inv_sqrt0));
        vcharb_sum[1] = _mm256_add_ps(vcharb_sum[1], _mm256_mul_ps(x1, inv_sqrt1));
        vcharb_sum[2] = _mm256_add_ps(vcharb_sum[2], _mm256_mul_ps(x2, inv_sqrt2));
        vcharb_sum[3] = _mm256_add_ps(vcharb_sum[3], _mm256_mul_ps(x3, inv_sqrt3));
    }

    // Accumulate Main Loop Results
    __m256 vfinal = _mm256_add_ps(_mm256_add_ps(vcharb_sum[0], vcharb_sum[1]),
                                  _mm256_add_ps(vcharb_sum[2], vcharb_sum[3]));
    float total_cost = horizontal_sum_avx(vfinal);

    // 2.b Intermediate Loop (Handle sisa block 8)
    // OPTIMASI: Mencegah bottleneck di scalar loop
    for (; i + 8 <= len; i += 8)
    {
        __m256 r = _mm256_loadu_ps(ref + i);
        __m256 c = _mm256_loadu_ps(comp + i);
        __m256 d = _mm256_sub_ps(_mm256_sub_ps(r, c), v_mean_diff);
        
        // FMA + Rsqrt logic
        __m256 x = _mm256_fmadd_ps(d, d, v_epsilon_sq);
        __m256 inv_sq = _mm256_rsqrt_ps(x);
        __m256 res = _mm256_mul_ps(x, inv_sq);
        
        total_cost += horizontal_sum_avx(res);
    }

    // 2.c Scalar Loop (Handle sisa < 8)
    // Menggunakan SSE scalar intrinsics untuk single value square root jika memungkinkan,
    // atau biarkan compiler mengoptimasi FPU.
    for (; i < len; ++i)
    {
        float d = (ref[i] - comp[i]) - mean_diff_scalar;
        // Compiler modern akan mengubah ini menjadi FMADD scalar jika flag aktif
        float x = d * d + EPSILON_SQ; 
        
        // Menggunakan intrinsik SSE rsqrt scalar
        __m128 sx = _mm_set_ss(x);
        __m128 sinv = _mm_rsqrt_ss(sx);
        float f_inv = _mm_cvtss_f32(sinv);
        
        total_cost += x * f_inv;
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
    // Pastikan size match (Assert dihilangkan di Release build, hati-hati)
    if (ref.size() != comp.size()) return FLT_MAX;

    const int rows = ref.rows;
    const int cols = ref.cols;

    // --- OPTIMIZATION 8+: Context Management & Padded Buffer Reuse ---
    
    // Hitung optimal size sekali saja
    int optimal_rows = cv::getOptimalDFTSize(rows);
    int optimal_cols = cv::getOptimalDFTSize(cols);
    cv::Size optimal_size(optimal_cols, optimal_rows);

    // Cek apakah ukuran berubah, jika ya re-create mats
    // Kita cek berdasarkan ukuran INPUT, bukan ukuran PADDED.
    if (fft_ctx.last_size != ref.size()) {
        fft_ctx.last_size = ref.size();
        
        // Re-create DFT buffers dengan ukuran optimal
        // (OpenCV DFT butuh buffer khusus, create baru lebih aman daripada resize)
        fft_ctx.ref_dft.create(optimal_size, CV_32FC2); // Complex output
        fft_ctx.comp_dft.create(optimal_size, CV_32FC2);
        fft_ctx.cross.create(optimal_size, CV_32FC2); // MulSpectrums output
        
        // Buffer sementara untuk copyMakeBorder
        fft_ctx.ref_padded_buffer.create(optimal_size, CV_32F);
        fft_ctx.comp_padded_buffer.create(optimal_size, CV_32F);
    }
    
    // --- OPTIMIZATION 7 & 9: Copy & Pad in one go ---
    // Daripada convertTo lalu copyMakeBorder, lebih baik langsung copy ke buffer padded.
    
    // Clear buffer padded dengan 0 (penting untuk DFT)
    fft_ctx.ref_padded_buffer.setTo(cv::Scalar::all(0));
    fft_ctx.comp_padded_buffer.setTo(cv::Scalar::all(0));

    // Copy ROI input ke pojok kiri atas buffer padded
    // Handle tipe data input:
    cv::Mat roi_ref = fft_ctx.ref_padded_buffer(cv::Rect(0, 0, cols, rows));
    cv::Mat roi_comp = fft_ctx.comp_padded_buffer(cv::Rect(0, 0, cols, rows));

    if (ref.type() == CV_32F) ref.copyTo(roi_ref);
    else ref.convertTo(roi_ref, CV_32F);

    if (comp.type() == CV_32F) comp.copyTo(roi_comp);
    else comp.convertTo(roi_comp, CV_32F);

    // --- DFT Computation ---
    // Gunakan buffer persisten sebagai output. Flag DFT_COMPLEX_OUTPUT wajib.
    // Kita inputkan ukuran non-zero rows untuk optimasi (opsional, tapi OpenCV handle otomatis biasanya)
    cv::dft(fft_ctx.ref_padded_buffer, fft_ctx.ref_dft, cv::DFT_COMPLEX_OUTPUT, rows);
    cv::dft(fft_ctx.comp_padded_buffer, fft_ctx.comp_dft, cv::DFT_COMPLEX_OUTPUT, rows);

    // Conjugate Multiply ---
    cv::mulSpectrums(fft_ctx.ref_dft, fft_ctx.comp_dft, fft_ctx.cross, 0, true);
    
    // --- Inverse DFT ---
    cv::idft(fft_ctx.cross, fft_ctx.cross, cv::DFT_REAL_OUTPUT | cv::DFT_SCALE, rows); // Hanya perlu hitung baris valid

    // --- OPTIMIZATION 11: Norm Calculation ---
    // Hitung norm hanya pada ROI asli, bukan padded area
    double ref_norm = cv::norm(roi_ref, cv::NORM_L2SQR);
    double comp_norm = cv::norm(roi_comp, cv::NORM_L2SQR);
    
    // --- OPTIMIZATION 12: FIXED & FAST MAX SEARCH ---
    double cross_max = -DBL_MAX;

    // Cara paling aman dan cepat (OpenCV minMaxLoc sudah pakai AVX2 multithreaded)
    cv::Mat cross_valid_roi = fft_ctx.cross(cv::Rect(0, 0, cols, rows));
    
    cv::minMaxLoc(cross_valid_roi, nullptr, &cross_max);

    /* 
       JIKA ANDA BERSIKERAS MEMAKAI MANUAL LOOP (Hanya lebih cepat utk size < 64x64):
       
       if (cross_valid_roi.isContinuous()) {
           const float* ptr = cross_valid_roi.ptr<float>(0);
           int len = rows * cols;
           #pragma omp simd reduction(max:cross_max)
           for(int i=0; i<len; ++i) cross_max = (double)std::max((float)cross_max, ptr[i]);
       } else {
           for(int r=0; r<rows; ++r) {
               const float* ptr = cross_valid_roi.ptr<float>(r);
               for(int c=0; c<cols; ++c) cross_max = std::max(cross_max, (double)ptr[c]);
           }
       }
    */

    // --- Compute SSD ---
    double ssd = ref_norm + comp_norm - 2.0 * cross_max;
    
    // Numerical guard
    if (ssd < 0.0) ssd = 0.0;
    
    return static_cast<float>(std::sqrt(ssd));
}