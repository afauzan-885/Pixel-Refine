#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>      // Untuk cv::Laplacian, cv::cvtColor
#include <opencv2/core/utility.hpp> // Untuk CV_Assert

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig
{
    // Konstanta Dasar
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-5f;
    constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;

    // --- Konstanta untuk Pembobotan Gradien ---
    constexpr float GRADIENT_WEIGHT_FACTOR = 1.4f;

    // Konstanta Adaptasi Noise
    constexpr float NOISE_ADAPTATION_FACTOR = 6.0f;           // Pengaruh noise pada threshold
    constexpr float MIN_ADAPTIVE_THRESHOLD_MULTIPLIER = 1.0f; // Batas bawah threshold adaptif
    constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;            // Faktor konversi MAD ke Sigma untuk noise Gaussian

    // --- Konstanta untuk Penanganan Area Gelap dengan Fading ---
    // Batas intensitas untuk *mulai* dianggap gelap dan *sepenuhnya* gelap
    constexpr float DARK_UPPER_THRESHOLD = 127.5f / 255.0f;

    constexpr double SSIM_K1_SENSITIVE = 0.0005; // (Perbedaan Cahaya atau luminance)
    constexpr double SSIM_K2_SENSITIVE = 0.005; // (Perbedaan Struktur, tekstur, atau pola)

    // Parameter *maksimum* untuk area yang sepenuhnya gelap
    constexpr float MAX_DARK_AREA_THRESHOLD_BOOST_FACTOR = 1.55f; // Toleransi Confidence terhadap area gelap, 1.5 artinya confidence di naikan sebesar 50%
    constexpr float MAX_WEIGHT_IN_DARK = 0.3f;                   // Bobot *maksimum* untuk SSIM (misal 0.3 = 30%). TALA (turunkan dari 0.6).
    constexpr float MAX_MIN_DARK_CONFIDENCE = 1e-3f;             // Confidence minimum *maksimum* (misal 0.05). TALA (turunkan dari 0.1).
    constexpr int DARKNESS_MAP_BLUR_KERNEL_SIZE = 1;             // Ukuran kernel Gaussian (harus ganjil)
    constexpr int CONFIDENCE_MAP_BLUR_KERNEL_SIZE = 3;           // Kernel Gaussian untuk menghaluskan peta confidence. TALA (coba 3 atau 5). Harus ganjil.
}

//=============================================================================
// Struktur Data Hasil
//=============================================================================
struct BlockMatchResult
{
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    std::vector<float> all_mads;
    int matches_found = 0;
    bool success = false;
    int best_match_r = -1;
    int best_match_c = -1;
};

//=============================================================================
// Fungsi Helper Dasar
//=============================================================================

inline float calculate_block_mad(const cv::Mat &block1_color, const cv::Mat &block2_color)
{
    CV_Assert(block1_color.size() == block2_color.size());

    if (block1_color.empty() || block2_color.empty())
    {
        return std::numeric_limits<float>::max();
    }

    cv::Mat block1_gray, block2_gray;
    // Konversi ke Grayscale Float
    if (block1_color.channels() > 1)
        cv::cvtColor(block1_color, block1_gray, cv::COLOR_BGR2GRAY);
    else
        block1_gray = block1_color;
    if (block2_color.channels() > 1)
        cv::cvtColor(block2_color, block2_gray, cv::COLOR_BGR2GRAY);
    else
        block2_gray = block2_color;
    if (block1_gray.type() != CV_32F)
        block1_gray.convertTo(block1_gray, CV_32F);
    if (block2_gray.type() != CV_32F)
        block2_gray.convertTo(block2_gray, CV_32F);

    if (block1_gray.empty() || block2_gray.empty())
    {
        return std::numeric_limits<float>::max();
    } // Cek lagi setelah konversi

    cv::Mat diff;
    cv::absdiff(block1_gray, block2_gray, diff); // Hitung diff pada grayscale

    cv::Scalar total_sad_scalar = cv::sum(diff);
    double total_sad = total_sad_scalar.val[0]; // Hanya channel 0

    float num_elements = static_cast<float>(block1_gray.total()); // Hanya 1 channel

    if (num_elements <= 0)
    {
        return 0.0f;
    }
    return static_cast<float>(total_sad / num_elements);
}

float calculate_mad_stddev(const std::vector<float> &mad_values)
{
    if (mad_values.size() <= 1)
    {
        return 0.0f;
    }
    cv::Mat mad_mat(mad_values.size(), 1, CV_32F, const_cast<float *>(mad_values.data()));
    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(mad_mat, mean_val, stddev_val);
    return static_cast<float>(stddev_val.val[0]);
}

float calculate_match_confidence(const BlockMatchResult &result, float threshold_for_quality)
{
    using namespace MotionMetricsConfig;

    float match_confidence = 0.0f;
    float quality_denominator = CONFIDENCE_SCALE_FACTOR * threshold_for_quality + STABILITY_EPSILON;

    if (!result.success || result.matches_found <= 0)
    {
        match_confidence = 0.0f;
    }
    else if (result.matches_found == 1)
    {
        if (quality_denominator > 0)
        {
            match_confidence = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        }
        else
        {
            match_confidence = (result.min_mad <= CONFIDENCE_EPSILON) ? 0.5f : 0.0f;
        }
        match_confidence = std::min(0.5f, std::max(0.0f, match_confidence));
    }
    else
    {
        float ratio = 1.0f;
        if (result.second_min_mad > CONFIDENCE_EPSILON)
        {
            float safe_min_mad = std::max(0.0f, result.min_mad);
            ratio = safe_min_mad / result.second_min_mad;
        }
        float ratio_confidence = std::max(0.0f, 1.0f - ratio);

        float absolute_quality = 0.0f;
        if (quality_denominator > 0)
        {
            absolute_quality = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        }
        else
        {
            absolute_quality = (std::max(0.0f, result.min_mad) <= CONFIDENCE_EPSILON) ? 1.0f : 0.0f;
        }
        absolute_quality = std::max(0.0f, std::min(1.0f, absolute_quality));
        match_confidence = ratio_confidence * absolute_quality;
    }
    return std::max(0.0f, std::min(1.0f, match_confidence));
}

inline float calculate_gradient_weighted_mad(
    const cv::Mat &block1_gray,     // Sekarang grayscale
    const cv::Mat &block2_gray,     // Sekarang grayscale
    const cv::Mat &grad_mag_block1, // Ini sudah grayscale
    float gradient_weight_factor)
{
    using namespace MotionMetricsConfig;
    // Validasi ukuran dan tipe
    CV_Assert(block1_gray.size() == block2_gray.size());
    CV_Assert(block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1);
    CV_Assert(grad_mag_block1.size() == block1_gray.size() && grad_mag_block1.type() == CV_32FC1);

    // --- Tidak perlu konversi Grayscale lagi ---
    if (block1_gray.empty() || block2_gray.empty())
    { // Cek input langsung
        return std::numeric_limits<float>::max();
    }

    double weighted_sad_sum = 0.0;
    double total_weight_sum = 0.0;

    for (int row = 0; row < block1_gray.rows; ++row)
    {
        const float *p1_row = block1_gray.ptr<float>(row);
        const float *p2_row = block2_gray.ptr<float>(row);
        const float *mag_row = grad_mag_block1.ptr<float>(row);

        for (int col = 0; col < block1_gray.cols; ++col)
        {
            float magnitude = mag_row[col];
            float weight = 1.0f + gradient_weight_factor * magnitude;
            total_weight_sum += weight;
            // Hitung diff hanya pada channel grayscale
            float diff = std::abs(p1_row[col] - p2_row[col]);
            weighted_sad_sum += diff * weight;
        }
    }

    // Normalisasi
    double denominator = total_weight_sum + STABILITY_EPSILON;

    if (denominator <= STABILITY_EPSILON)
    {
        // Panggil versi grayscale dari block mad jika diperlukan
        return calculate_block_mad(block1_gray, block2_gray); // Panggil versi grayscale baru
    }
    return static_cast<float>(weighted_sad_sum / denominator);
}

inline float calculate_block_ssim(const cv::Mat &block1_gray, const cv::Mat &block2_gray)
{
    using namespace MotionMetricsConfig;
    BlockMatchResult result;
    // Gunakan konstanta sensitif yang baru didefinisikan
    // L = 1.0 untuk float [0, 1]
    const double C1 = (SSIM_K1_SENSITIVE * 1.0) * (SSIM_K1_SENSITIVE * 1.0);
    const double C2 = (SSIM_K2_SENSITIVE * 1.0) * (SSIM_K2_SENSITIVE * 1.0);

    CV_Assert(block1_gray.size() == block2_gray.size() &&
              block1_gray.type() == CV_32FC1 && block2_gray.type() == CV_32FC1);

    if (block1_gray.empty()) { return 0.0f; }

    cv::Scalar mean1_s, mean2_s, stddev1_s, stddev2_s;
    cv::meanStdDev(block1_gray, mean1_s, stddev1_s);
    cv::meanStdDev(block2_gray, mean2_s, stddev2_s);

    double mean1 = mean1_s.val[0];
    double mean2 = mean2_s.val[0];
    double var1 = stddev1_s.val[0] * stddev1_s.val[0];
    double var2 = stddev2_s.val[0] * stddev2_s.val[0];

    cv::Mat block12_mul;
    cv::multiply(block1_gray, block2_gray, block12_mul);
    double mean12 = cv::mean(block12_mul).val[0];
    double covar12 = mean12 - mean1 * mean2;

    double luminance = (2.0 * mean1 * mean2 + C1) / (mean1 * mean1 + mean2 * mean2 + C1);
    double structure_contrast = (2.0 * covar12 + C2) / (var1 + var2 + C2);

    double ssim_val = luminance * structure_contrast;

    return static_cast<float>(std::max(0.0, std::min(1.0, ssim_val)));
}

//=============================================================================
// Fungsi Pencarian Blok
//=============================================================================
BlockMatchResult find_best_block_match(
    const cv::Mat &current_block_gray,        // Sekarang grayscale
    const cv::Mat &reference_tile_gray, // Sekarang grayscale
    int block_r_start, int block_c_start,
    int search_radius)
{
    using namespace MotionMetricsConfig;
    BlockMatchResult result;

    // Ukuran dari input grayscale
    int tile_h = reference_tile_gray.rows;
    int tile_w = reference_tile_gray.cols;
    int current_block_h = current_block_gray.rows;
    int current_block_w = current_block_gray.cols;

    // Tipe input sudah grayscale float
    CV_Assert(current_block_gray.type() == CV_32FC1 && reference_tile_gray.type() == CV_32FC1);

    // --- Hitung gradien dari current_block_gray ---
    cv::Mat grad_x, grad_y, grad_mag_current;
    if (!current_block_gray.empty() && current_block_gray.rows >= 3 && current_block_gray.cols >= 3)
    {
        cv::Scharr(current_block_gray, grad_x, CV_32F, 1, 0);
        cv::Scharr(current_block_gray, grad_y, CV_32F, 0, 1);
        cv::magnitude(grad_x, grad_y, grad_mag_current);
    }
    else
    {
        // Buat gradien nol jika blok terlalu kecil atau kosong
        grad_mag_current = cv::Mat::zeros(current_block_gray.size(), CV_32FC1);
    }
    // -------------------------------------------

    int search_r_start = std::max(0, block_r_start - search_radius);
    int search_c_start = std::max(0, block_c_start - search_radius);
    int search_r_end = std::min(tile_h - current_block_h, block_r_start + search_radius);
    int search_c_end = std::min(tile_w - current_block_w, block_c_start + search_radius);

    int estimated_matches = (search_r_end - search_r_start + 1) * (search_c_end - search_c_start + 1);
    if (estimated_matches > 0)
    {
        result.all_mads.reserve(estimated_matches);
    }

    for (int search_r = search_r_start; search_r <= search_r_end; ++search_r)
    {
        for (int search_c = search_c_start; search_c <= search_c_end; ++search_c)
        {
            // Boundary check (redundant jika search_r/c_end dihitung benar, tapi aman)
            if (search_r < 0 || search_c < 0 || search_r + current_block_h > tile_h || search_c + current_block_w > tile_w)
            {
                continue;
            }

            cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
            // Ambil ROI dari reference tile GRAYSCALE
            const cv::Mat ref_block_gray = reference_tile_gray(ref_block_roi);

            // Panggil calculate_gradient_weighted_mad dengan input GRAYSCALE
            float current_metric_score = calculate_gradient_weighted_mad(
                current_block_gray, // Grayscale
                ref_block_gray,     // Grayscale
                grad_mag_current,   // Grayscale (gradien dari current_block_gray)
                GRADIENT_WEIGHT_FACTOR);

            result.all_mads.push_back(current_metric_score);
            result.matches_found++;
            result.success = true; // Set success jika setidaknya satu kandidat dievaluasi

            if (current_metric_score < result.min_mad)
            {
                result.second_min_mad = result.min_mad;
                result.min_mad = current_metric_score;
                result.best_match_r = search_r;
                result.best_match_c = search_c;
            }
            else if (current_metric_score < result.second_min_mad)
            {
                result.second_min_mad = current_metric_score;
            }
        }
    }
    // Jika tidak ada match sama sekali (misalnya search window 0 dan di luar batas),
    // result.success akan tetap false (default)
    if (result.matches_found == 0)
    {
        result.success = false;
    }

    return result;
}

//=============================================================================
// Fungsi Estimasi Noise (BARU: Menggunakan MAD)
//=============================================================================

/**
 * @brief Menghitung Median Absolute Deviation (MAD) dari data dalam cv::Mat (CV_32FC1).
 * @param data_mat Mat input 1 channel float.
 * @return Nilai MAD, atau 0.0 jika input tidak valid atau kurang dari 2 elemen.
 */
float calculate_mad_from_mat(const cv::Mat &data_mat)
{
    CV_Assert(data_mat.type() == CV_32FC1);

    if (data_mat.empty() || !data_mat.isContinuous())
    {
        // Handle non-continuous or empty matrices if necessary,
        // For simplicity, let's copy to a vector directly.
        // If performance critical and matrices are often non-continuous,
        // optimize this part.
        if (data_mat.empty())
            return 0.0f;
    }

    // 1. Salin data ke std::vector<float>
    std::vector<float> data_vec;
    data_vec.reserve(data_mat.total());
    if (data_mat.isContinuous())
    {
        const float *ptr = data_mat.ptr<float>(0);
        data_vec.assign(ptr, ptr + data_mat.total());
    }
    else
    {
        for (int r = 0; r < data_mat.rows; ++r)
        {
            const float *ptr_row = data_mat.ptr<float>(r);
            data_vec.insert(data_vec.end(), ptr_row, ptr_row + data_mat.cols);
        }
    }

    size_t n = data_vec.size();
    if (n <= 1)
    {
        return 0.0f; // MAD tidak terdefinisi atau nol untuk <= 1 elemen
    }

    // 2. Hitung Median dari data asli
    // Gunakan nth_element untuk efisiensi, tidak perlu sort penuh
    std::vector<float>::iterator median_it = data_vec.begin() + n / 2;
    std::nth_element(data_vec.begin(), median_it, data_vec.end());
    float median_val = *median_it;
    // Jika jumlah genap, median adalah rata-rata dari dua elemen tengah
    if (n % 2 == 0)
    {
        std::vector<float>::iterator median_it_prev = data_vec.begin() + n / 2 - 1;
        std::nth_element(data_vec.begin(), median_it_prev, data_vec.end()); // Pastikan elemen sebelumnya juga benar
        median_val = (median_val + *median_it_prev) / 2.0f;
    }

    // 3. Hitung Deviasi Absolut dari Median
    std::vector<float> abs_deviations;
    abs_deviations.reserve(n);
    // Perlu akses elemen asli lagi, jadi pakai data dari Mat atau salin vector di awal
    // Cara termudah: Gunakan Mat asli lagi (jika isContinuous) atau loop lagi
    if (data_mat.isContinuous())
    {
        const float *ptr = data_mat.ptr<float>(0);
        for (size_t i = 0; i < n; ++i)
        {
            abs_deviations.push_back(std::abs(ptr[i] - median_val));
        }
    }
    else
    {
        for (int r = 0; r < data_mat.rows; ++r)
        {
            const float *ptr_row = data_mat.ptr<float>(r);
            for (int c = 0; c < data_mat.cols; ++c)
            {
                abs_deviations.push_back(std::abs(ptr_row[c] - median_val));
            }
        }
    }
    // Alternatif jika vector data_vec di-copy di awal:
    // for (float val : original_data_copy) { // perlu copy tambahan
    //    abs_deviations.push_back(std::abs(val - median_val));
    // }

    // 4. Hitung Median dari Deviasi Absolut (ini adalah MAD)
    size_t n_dev = abs_deviations.size(); // Seharusnya sama dengan n
    if (n_dev == 0)
        return 0.0f; // Safety check

    std::vector<float>::iterator mad_it = abs_deviations.begin() + n_dev / 2;
    std::nth_element(abs_deviations.begin(), mad_it, abs_deviations.end());
    float mad_val = *mad_it;

    // Jika jumlah genap, ambil rata-rata dua tengah
    if (n_dev % 2 == 0)
    {
        std::vector<float>::iterator mad_it_prev = abs_deviations.begin() + n_dev / 2 - 1;
        // Pastikan elemen sebelumnya juga benar
        std::nth_element(abs_deviations.begin(), mad_it_prev, abs_deviations.end());
        mad_val = (mad_val + *mad_it_prev) / 2.0f;
    }

    return mad_val;
}

/**
 * @brief Mengestimasi standar deviasi noise Gaussian dari sebuah tile menggunakan MAD
 *        dari filter Laplacian, yang lebih robust terhadap outlier (tepi/tekstur).
 * @param tile_gray_float Tile input (CV_32FC1). Diharapkan sudah grayscale dan float.
 * @return Estimasi standar deviasi noise (sigma_n), atau 0.0 jika input tidak valid.
 */
float estimate_tile_noise_sigma_mad_laplacian(const cv::Mat &tile_gray_float)
{
    using namespace MotionMetricsConfig; // Untuk MAD_TO_SIGMA_FACTOR

    // Validasi input
    if (tile_gray_float.empty() || tile_gray_float.channels() != 1 || tile_gray_float.type() != CV_32F)
    {
        return 0.0f;
    }
    if (tile_gray_float.rows < 3 || tile_gray_float.cols < 3)
    {
        return 0.0f; // Terlalu kecil untuk Laplacian 3x3
    }

    // 1. Terapkan Filter Laplacian
    cv::Mat laplacian_output;
    cv::Laplacian(tile_gray_float, laplacian_output, CV_32F, 1); // ksize=1 -> 3x3 kernel

    // 2. Hitung Median Absolute Deviation (MAD) dari hasil Laplacian
    float mad_value = calculate_mad_from_mat(laplacian_output);

    // 3. Konversi MAD ke estimasi Sigma (untuk noise Gaussian)
    // sigma ≈ 1.4826 * MAD
    float estimated_sigma = mad_value * MAD_TO_SIGMA_FACTOR;

    // 4. Kembalikan hasil, pastikan non-negatif
    return std::max(0.0f, estimated_sigma);
}

//=============================================================================
// Fungsi Akumulasi Tile (Tingkat Atas)
//=============================================================================
extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, float *weight_map_sum_ptr,
        const float *current_image_ptr, const float *reference_image_ptr,
        const float *base_window_ptr, const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts, int tile_h, int tile_w,
        int h, int w, int channels, float motion_threshold,
        int mbm_block_h, int mbm_block_w, int mbm_search_radius,
        float frame_max_adaptive_multiplier)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h <= 0 || w <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            mbm_block_h <= 0 || mbm_block_w <= 0)
        {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0)
        {
            return;
        }

        cv::Mat final_image_sum_mat(h, w, mat_type, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h, w, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h, w, mat_type, const_cast<float *>(current_image_ptr));
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float *>(reference_image_ptr));
        // const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float *>(base_window_ptr));

        // --- OPTIMASI: Pre-calculate Grayscale Images ---
        cv::Mat current_image_gray_mat;
        cv::Mat reference_image_gray_mat;

        // Konversi current_image
        if (current_image_mat.channels() > 1)
        {
            cv::cvtColor(current_image_mat, current_image_gray_mat, cv::COLOR_BGR2GRAY); // Asumsi BGR
        }
        else
        {
            current_image_gray_mat = current_image_mat; // Langsung assign jika sudah 1 channel
        }
        if (current_image_gray_mat.type() != CV_32F)
        {
            current_image_gray_mat.convertTo(current_image_gray_mat, CV_32F);
        }

        // Konversi reference_image
        if (reference_image_mat.channels() > 1)
        {
            cv::cvtColor(reference_image_mat, reference_image_gray_mat, cv::COLOR_BGR2GRAY); // Asumsi BGR
        }
        else
        {
            reference_image_gray_mat = reference_image_mat; // Langsung assign jika sudah 1 channel
        }
        if (reference_image_gray_mat.type() != CV_32F)
        {
            reference_image_gray_mat.convertTo(reference_image_gray_mat, CV_32F);
        }

        // Periksa apakah konversi berhasil (opsional tapi bagus)
        if (current_image_gray_mat.empty() || reference_image_gray_mat.empty())
        {
            // std::cerr << "Grayscale conversion failed." << std::endl;
            return;
        }
        // ----------------------------------------------------
#pragma omp parallel
        {
            // Buffer per Thread (Tetap Sama)
            // cv::Mat thread_current_block_gray;
            // cv::Mat thread_ref_block_best_match_gray;
            // cv::Mat thread_result_ncc; // Tidak dipakai lagi jika SSIM saja
            // cv::Mat thread_larger_ref_gray_float;
            cv::Mat thread_darkness_map_raw;
            cv::Mat thread_darkness_map_smoothed;
            cv::Mat thread_block_confidences_raw;
            cv::Mat thread_block_confidences_smoothed;
            cv::Mat thread_larger_ref_tile;
            cv::Mat thread_larger_ref_tile_gray;
            
            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w)
                        continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);

                    // Ambil ROI dari gambar WARNA untuk akumulasi akhir
                    const cv::Mat current_tile_color = current_image_mat(tile_roi);
                    // Ambil ROI dari gambar GRAYSCALE untuk perhitungan
                    const cv::Mat current_tile_gray = current_image_gray_mat(tile_roi);
                    const cv::Mat reference_tile_gray = reference_image_gray_mat(tile_roi);
                    // Buat Mat header untuk base_window per tile
                    const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

                    // --- LANGKAH 1: Estimasi Noise Lokal (Gunakan reference_image_gray_mat) ---
                    float estimated_noise_sigma = 0.0f;
                    // Gunakan tile referensi grayscale yang lebih besar jika memungkinkan
                    int larger_tile_factor = 2; // Faktor pembesaran tile untuk noise
                    int larger_r = std::max(0, r - tile_h * (larger_tile_factor - 1) / 2);
                    int larger_c = std::max(0, c - tile_w * (larger_tile_factor - 1) / 2);
                    int larger_h = std::min(h - larger_r, tile_h * larger_tile_factor);
                    int larger_w = std::min(w - larger_c, tile_w * larger_tile_factor);

                    if (larger_h >= 3 && larger_w >= 3)
                    {
                        cv::Rect larger_roi(larger_c, larger_r, larger_w, larger_h);
                        // Ambil ROI langsung dari reference_image_gray_mat
                        thread_larger_ref_tile_gray = reference_image_gray_mat(larger_roi);
                        if (!thread_larger_ref_tile_gray.empty()) {
                             estimated_noise_sigma = estimate_tile_noise_sigma_mad_laplacian(thread_larger_ref_tile_gray);
                        }
                    }
                    // Fallback: gunakan tile referensi ukuran normal jika tile besar gagal/tidak valid
                    else if (reference_tile_gray.rows >= 3 && reference_tile_gray.cols >= 3) {
                         if (!reference_tile_gray.empty()) {
                            estimated_noise_sigma = estimate_tile_noise_sigma_mad_laplacian(reference_tile_gray);
                         }
                    }

                    // LANGKAH 1.B: Hitung & Clamp Threshold Adaptif (Sama)
                    float tile_adaptive_threshold = motion_threshold + NOISE_ADAPTATION_FACTOR * estimated_noise_sigma;
                    tile_adaptive_threshold = std::max(motion_threshold * MIN_ADAPTIVE_THRESHOLD_MULTIPLIER, tile_adaptive_threshold);
                    tile_adaptive_threshold = std::min(motion_threshold * frame_max_adaptive_multiplier, tile_adaptive_threshold);
                    tile_adaptive_threshold = std::max(0.0f, tile_adaptive_threshold);

                    // Tahap 2 & 3 (Darkness, Confidence, Akumulasi)
                    int num_blocks_h = (mbm_block_h > 0) ? (tile_h + mbm_block_h - 1) / mbm_block_h : 0;
                    int num_blocks_w = (mbm_block_w > 0) ? (tile_w + mbm_block_w - 1) / mbm_block_w : 0;
                    int num_blocks_in_tile = num_blocks_h * num_blocks_w;

                    // 2.A: Darkness Map Raw (Sama)
                    thread_darkness_map_raw.create(num_blocks_h, num_blocks_w, CV_32F);
                    if (num_blocks_in_tile > 0)
                    {
                        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                                int block_local_r_start = bh_idx * mbm_block_h;
                                int block_local_c_start = bw_idx * mbm_block_w;
                                int current_block_h = std::min(mbm_block_h, tile_h - block_local_r_start);
                                int current_block_w = std::min(mbm_block_w, tile_w - block_local_c_start);

                                if (current_block_h <= 0 || current_block_w <= 0) {
                                    thread_darkness_map_raw.at<float>(bh_idx, bw_idx) = 0.0f; continue;
                                }
                                cv::Rect current_block_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);

                                // Ambil ROI dari current_tile_GRAY
                                const cv::Mat current_block_gray = current_tile_gray(current_block_roi);

                                float avg_intensity = 0.0f;
                                if (!current_block_gray.empty()) {
                                    // Langsung hitung mean dari block grayscale
                                    avg_intensity = static_cast<float>(cv::mean(current_block_gray)[0]);
                                }

                                // Hitung darkness factor (sama)
                                float darkness_factor = 0.0f;
                                if (avg_intensity < DARK_UPPER_THRESHOLD) {
                                    float normalized_intensity_in_dark = avg_intensity / DARK_UPPER_THRESHOLD;
                                    darkness_factor = 1.0f - normalized_intensity_in_dark * normalized_intensity_in_dark;
                                }
                                thread_darkness_map_raw.at<float>(bh_idx, bw_idx) = std::max(0.0f, std::min(1.0f, darkness_factor));
                            }
                        }
                        // 2.B: Smooth Darkness Map
                        int kernel_sz_dark = (DARKNESS_MAP_BLUR_KERNEL_SIZE > 0 && DARKNESS_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? DARKNESS_MAP_BLUR_KERNEL_SIZE : 3;
                        if (kernel_sz_dark < 3)
                            kernel_sz_dark = 3;
                        if (!thread_darkness_map_raw.empty() && kernel_sz_dark > 0)
                        {
                            cv::GaussianBlur(thread_darkness_map_raw, thread_darkness_map_smoothed, cv::Size(kernel_sz_dark, kernel_sz_dark), 0);
                        }
                        else
                        {
                            if (!thread_darkness_map_raw.empty())
                                thread_darkness_map_raw.copyTo(thread_darkness_map_smoothed);
                            else
                                thread_darkness_map_smoothed.create(0, 0, CV_32F);
                        }
                    }
                    else
                    {
                        thread_darkness_map_smoothed.create(0, 0, CV_32F);
                    }

                    // 2.C: Confidence Map Raw
                    thread_block_confidences_raw.create(num_blocks_h, num_blocks_w, CV_32F);
                    bool darkness_map_valid = num_blocks_in_tile > 0 && !thread_darkness_map_smoothed.empty() && thread_darkness_map_smoothed.rows == num_blocks_h && thread_darkness_map_smoothed.cols == num_blocks_w;

                    if (num_blocks_in_tile > 0) {
                        // reference_tile_gray sudah di-ROI di atas
                        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                                int block_local_r_start = bh_idx * mbm_block_h; int block_local_c_start = bw_idx * mbm_block_w;
                                int current_block_h = std::min(mbm_block_h, tile_h - block_local_r_start); int current_block_w = std::min(mbm_block_w, tile_w - block_local_c_start);

                                if (current_block_h <= 0 || current_block_w <= 0) { thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = 0.0f; continue; }

                                cv::Rect current_block_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                // Ambil ROI dari tile GRAYSCALE
                                const cv::Mat current_block_gray = current_tile_gray(current_block_roi);

                                float smoothed_darkness_factor = 0.0f;
                                if (darkness_map_valid) { smoothed_darkness_factor = thread_darkness_map_smoothed.at<float>(bh_idx, bw_idx); }

                                // --- MBM menggunakan input GRAYSCALE ---
                                BlockMatchResult block_result = find_best_block_match(current_block_gray, reference_tile_gray, block_local_r_start, block_local_c_start, mbm_search_radius);
                                // --- ----------------------------------- ---

                                // --- Fallback MBM (Gunakan input GRAYSCALE) ---
                                if (!block_result.success) {
                                     if (block_local_r_start + current_block_h <= tile_h && block_local_c_start + current_block_w <= tile_w) {
                                        cv::Rect ref_block_orig_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                        const cv::Mat ref_block_orig_gray = reference_tile_gray(ref_block_orig_roi); // Dari tile grayscale
                                        if (!current_block_gray.empty() && !ref_block_orig_gray.empty()) {
                                            block_result.min_mad = calculate_block_mad(current_block_gray, ref_block_orig_gray); // Panggil versi grayscale
                                            block_result.second_min_mad = block_result.min_mad; block_result.matches_found = 1; block_result.success = true; block_result.best_match_r = -1; block_result.best_match_c = -1;
                                        } else { block_result.success = false; }
                                    } else { block_result.success = false; }
                                }
                                // --- --------------------------------------- ---

                                float final_confidence = 0.0f;
                                if (block_result.success) {
                                    // Perhitungan threshold adaptif (sama)
                                    float final_threshold_for_block = tile_adaptive_threshold;
                                    if (MAX_DARK_AREA_THRESHOLD_BOOST_FACTOR != 1.0f && smoothed_darkness_factor > 0.0f) {
                                        float threshold_boost = 1.0f + smoothed_darkness_factor * (MAX_DARK_AREA_THRESHOLD_BOOST_FACTOR - 1.0f);
                                        final_threshold_for_block *= threshold_boost;
                                    }
                                    final_threshold_for_block = std::max(0.0f, final_threshold_for_block);

                                    // Hitung MAD confidence (hasil MBM sudah dari grayscale)
                                    float mad_confidence = calculate_match_confidence(block_result, final_threshold_for_block);
                                    final_confidence = mad_confidence; // Default

                                    float effective_ssim_weight = smoothed_darkness_factor * MAX_WEIGHT_IN_DARK;
                                    effective_ssim_weight = std::min(effective_ssim_weight, 1.0f);

                                    // --- Modulasi SSIM (Gunakan input GRAYSCALE) ---
                                    if (effective_ssim_weight > CONFIDENCE_EPSILON && block_result.best_match_r >= 0)
                                    {
                                        cv::Rect best_ref_roi(block_result.best_match_c, block_result.best_match_r, current_block_w, current_block_h);
                                        // Boundary check untuk best_ref_roi
                                        if (best_ref_roi.x >= 0 && best_ref_roi.y >= 0 &&
                                            best_ref_roi.x + best_ref_roi.width <= tile_w &&
                                            best_ref_roi.y + best_ref_roi.height <= tile_h)
                                        {
                                            // Ambil ROI match terbaik dari tile GRAYSCALE
                                            const cv::Mat ref_block_best_match_gray = reference_tile_gray(best_ref_roi);
                                            // current_block_gray sudah ada

                                            if (!current_block_gray.empty() && !ref_block_best_match_gray.empty()) {
                                                try {
                                                    // Panggil SSIM dengan blok grayscale
                                                    float ssim_score = calculate_block_ssim(current_block_gray, ref_block_best_match_gray);
                                                    float ssim_modulator = (1.0f - effective_ssim_weight) + (effective_ssim_weight * ssim_score);
                                                    final_confidence = mad_confidence * ssim_modulator;
                                                } catch (const cv::Exception &e) {
                                                    // Jika SSIM gagal, final_confidence tetap = mad_confidence
                                                }
                                            }
                                        }
                                    }
                                    // --- ------------------------------------ ---

                                    // Terapkan batas bawah confidence (sama)
                                    float effective_min_confidence = smoothed_darkness_factor * MAX_MIN_DARK_CONFIDENCE;
                                    final_confidence = std::max(final_confidence, effective_min_confidence);
                                }

                                thread_block_confidences_raw.at<float>(bh_idx, bw_idx) = final_confidence;
                            } // end bw_idx
                        } // end bh_idx

                        // 2.D: Smooth Confidence Map (Sama)
                        int kernel_sz_conf = (CONFIDENCE_MAP_BLUR_KERNEL_SIZE > 0 && CONFIDENCE_MAP_BLUR_KERNEL_SIZE % 2 == 1) ? CONFIDENCE_MAP_BLUR_KERNEL_SIZE : 3;
                        if(kernel_sz_conf < 1) kernel_sz_conf = 1;
                        if (!thread_block_confidences_raw.empty() && kernel_sz_conf >= 3) {
                            cv::GaussianBlur(thread_block_confidences_raw, thread_block_confidences_smoothed, cv::Size(kernel_sz_conf, kernel_sz_conf), 0);
                        } else {
                            thread_block_confidences_raw.copyTo(thread_block_confidences_smoothed);
                        }
                    } else {
                        thread_block_confidences_raw.create(0, 0, CV_32F);
                        thread_block_confidences_smoothed.create(0, 0, CV_32F);
                    }
                    // ----------------------------------------------------------

                    // --- Tahap 3: Akumulasi (Gunakan current_tile_COLOR) ---
                    bool confidence_map_smoothed_valid = num_blocks_in_tile > 0 && !thread_block_confidences_smoothed.empty() && thread_block_confidences_smoothed.rows == num_blocks_h && thread_block_confidences_smoothed.cols == num_blocks_w;
                    if (confidence_map_smoothed_valid) {
                        for (int y = 0; y < tile_h; ++y) {
                            // Akses row dari tile WARNA
                            const float *current_tile_color_row = current_tile_color.ptr<float>(y);
                            const float *base_window_row = base_window_tile_mat.ptr<float>(y);
                            int gy = r + y;
                            if (gy < 0 || gy >= h) continue;

                            float *global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                            float *global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);

                            for (int x = 0; x < tile_w; ++x) {
                                int bh_idx = std::min(y / mbm_block_h, num_blocks_h - 1);
                                int bw_idx = std::min(x / mbm_block_w, num_blocks_w - 1);

                                // Pastikan indeks blok valid (penting jika num_blocks_h/w bisa 0)
                                if (bh_idx < 0 || bw_idx < 0) continue;

                                float block_confidence = thread_block_confidences_smoothed.at<float>(bh_idx, bw_idx);
                                float base_win_val = base_window_row[x];
                                float pixel_weight = base_win_val * block_confidence;

                                if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                    int gx = c + x;
                                    if (gx >= 0 && gx < w) {
                                        // --- Akumulasi Bobot (Grayscale - Tetap Sama) ---
                                        #pragma omp atomic update
                                        global_weight_sum_row[gx] += pixel_weight;
                                        // -----------------------------------------------

                                        // --- Akumulasi Piksel (WARNA) ---
                                        int current_pixel_idx_local = x * channels; // Indeks di tile berwarna
                                        int current_pixel_idx_global = gx * channels; // Indeks di gambar global berwarna
                                        for (int ch = 0; ch < channels; ++ch) {
                                            // Ambil nilai dari TILE WARNA
                                            float weighted_pixel_value = current_tile_color_row[current_pixel_idx_local + ch] * pixel_weight;
                                            #pragma omp atomic update
                                            global_pixel_sum_row[current_pixel_idx_global + ch] += weighted_pixel_value;
                                        }
                                        // -------------------------------
                                    }
                                }
                            } // end x loop
                        } // end y loop
                    }
                    // -------------------------------------------------------

                } // End col_starts loop (j)
            } // End row_starts loop (i)
        } // End parallel region
    } // End accumulate_frame_weighted_jit

    float estimate_global_noise(
        const float *reference_image_ptr,
        int h, int w, int channels,
        int tile_h, int tile_w,
        const int *row_starts, int num_row_starts,
        const int *col_starts, int num_col_starts)
    {
        using namespace MotionMetricsConfig;

        // --- Validasi Input Dasar ---
        if (!reference_image_ptr || !row_starts || !col_starts || h <= 0 || w <= 0 ||
            channels <= 0 || tile_h <= 0 || tile_w <= 0 || num_row_starts <= 0 || num_col_starts <= 0)
        {
            return 0.0f; // Kembalikan 0 jika input tidak valid
        }

        int mat_type = CV_32FC(channels);
        if (mat_type == 0)
        {
            return 0.0f;
        } // Tipe tidak valid

        // --- Buat Mat Header untuk Input ---
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float *>(reference_image_ptr));
        cv::Mat ref_gray_float;

        // --- Konversi ke Grayscale Float ---
        if (reference_image_mat.channels() > 1)
        {
            cv::cvtColor(reference_image_mat, ref_gray_float, cv::COLOR_BGR2GRAY); // Asumsi BGR jika > 1
            if (ref_gray_float.type() != CV_32F)
            { // Pastikan float setelah cvtColor
                ref_gray_float.convertTo(ref_gray_float, CV_32F);
            }
        }
        else
        {
            // Jika sudah 1 channel, pastikan tipenya float
            if (reference_image_mat.type() != CV_32F)
            {
                reference_image_mat.convertTo(ref_gray_float, CV_32F);
            }
            else
            {
                // Tidak perlu copy jika tipe sudah benar
                ref_gray_float = reference_image_mat;
            }
        }

        if (ref_gray_float.empty())
        {
            return 0.0f;
        }

        // --- Variabel untuk Akumulasi Sigma ---
        double total_sigma_sum = 0.0;
        long long valid_tile_count = 0; // Gunakan long long untuk jumlah tile yang besar

// --- Paralelisasi Loop Tile ---
#pragma omp parallel
        {
            // Buffer per thread untuk menghindari race condition pada Mat temporary
            cv::Mat thread_tile;
            cv::Mat thread_laplacian_output;
            double thread_local_sigma_sum = 0.0;
            long long thread_local_valid_count = 0;

#pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++)
            {
                for (int j = 0; j < num_col_starts; j++)
                {
                    int r = row_starts[i];
                    int c = col_starts[j];

                    // Boundary check dasar untuk ROI
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w)
                        continue;

                    // --- Ekstrak Tile ROI ---
                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    // Ambil ROI dari gambar grayscale (tidak perlu copy jika hanya dibaca)
                    thread_tile = ref_gray_float(tile_roi);

                    // Cek ukuran minimum untuk Laplacian
                    if (thread_tile.rows < 3 || thread_tile.cols < 3)
                    {
                        continue;
                    }

                    // --- Hitung Laplacian (output ke buffer thread) ---
                    cv::Laplacian(thread_tile, thread_laplacian_output, CV_32F, 1);

                    // --- Hitung MAD (menggunakan fungsi yang sudah ada) ---
                    float mad_value = calculate_mad_from_mat(thread_laplacian_output);

                    // --- Konversi ke Sigma ---
                    float estimated_sigma = mad_value * MAD_TO_SIGMA_FACTOR;

                    // Akumulasi hasil thread lokal
                    thread_local_sigma_sum += static_cast<double>(std::max(0.0f, estimated_sigma)); // Pastikan non-negatif
                    thread_local_valid_count++;

                } // end loop j
            } // end loop i

// --- Reduksi hasil dari setiap thread (Aman untuk dilakukan setelah loop parallel for) ---
#pragma omp critical
            {
                total_sigma_sum += thread_local_sigma_sum;
                valid_tile_count += thread_local_valid_count;
            }

        } // End parallel region

        // --- Hitung Rata-rata Global ---
        if (valid_tile_count > 0)
        {
            return static_cast<float>(total_sigma_sum / valid_tile_count);
        }
        else
        {
            return 0.0f; // Kembalikan 0 jika tidak ada tile valid yang diproses
        }
    }

    // Fungsi Normalisasi (Tidak Berubah)
    void normalize_accumulated_image_jit(
        float *final_image_ptr,
        const float *weight_map_sum_ptr,
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0)
        {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0)
            return;

        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float *>(weight_map_sum_ptr));

#pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy)
        {
            for (int gx = 0; gx < w; ++gx)
            {
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);
                float *final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD)
                {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row[pixel_idx + ch] *= inv_total_weight;
                    }
                }
                else
                {
                    for (int ch = 0; ch < channels; ++ch)
                    {
                        final_pixel_row[pixel_idx + ch] = 0.0f;
                    }
                }
            } // gx loop
        } // gy loop
    } // End normalize_accumulated_image_jit

} // end extern "C"
