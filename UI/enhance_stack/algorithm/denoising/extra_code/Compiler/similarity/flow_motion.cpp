#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp> // Untuk CV_Assert
#include <opencv2/quality.hpp>
#include <map>

namespace MotionMetricsConfig {
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-5f;
    constexpr double SSIM_K1 = 0.01;
    constexpr double SSIM_K2 = 0.03;
    constexpr double SSIM_L = 1.0; // Range piksel [0, 1]
    constexpr double SSIM_C1 = (SSIM_K1 * SSIM_L) * (SSIM_K1 * SSIM_L);
    constexpr double SSIM_C2 = (SSIM_K2 * SSIM_L) * (SSIM_K2 * SSIM_L);
    constexpr float ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR = 1.5f;
    constexpr int DEFAULT_SEARCH_RADIUS = 7;
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
    constexpr float MIN_LBP_ENTROPY_FOR_CONFIDENCE = 1e-6f;
    constexpr float MAX_LBP_ENTROPY_FOR_FULL_CONFIDENCE = 4.0f;
    // --- Konstanta untuk Logika Statis  ---
    // Threshold SSIM di posisi nol yang menunjukkan area SANGAT mungkin statis
    constexpr float STRONG_STATIC_SSIM_THRESHOLD = 0.5f; // Tune! (Harus TINGGI)
    // Confidence yang diberikan jika bukti statis kuat ditemukan
    // (Bisa dibuat sedikit di bawah 1.0 untuk memungkinkan sedikit blending jika perlu)
    constexpr float CONFIDENCE_FOR_STRONG_STATIC = 0.65f; // Tune! (Tinggi)
    // --- Konstanta untuk Adaptive Threshold ---
    // Seberapa besar pengaruh noise sigma terhadap penurunan threshold
    constexpr float NOISE_INFLUENCE_FACTOR = 1.5f; // Tune! (Nilai positif)
    // Batas bawah dan atas untuk adaptive threshold
    constexpr float MIN_ADAPTIVE_MOTION_THRESHOLD = 0.2f; // Tune!
    constexpr float MAX_ADAPTIVE_MOTION_THRESHOLD = 0.95f; // Tune!
    
}

//=============================================================================
// Fungsi Helper LBP & Entropi
//=============================================================================

/**
 * @brief Menghitung nilai LBP 8-bit untuk satu piksel.
 * @param gray_block Blok grayscale (CV_32FC1).
 * @param r Baris piksel tengah.
 * @param c Kolom piksel tengah.
 * @return Nilai LBP (0-255).
 */
inline unsigned char calculate_lbp_pixel(const cv::Mat& gray_block, int r, int c) {
    // Pastikan tipe CV_32FC1
    CV_Assert(gray_block.type() == CV_32FC1);
    float center = gray_block.at<float>(r, c);
    unsigned char lbp_value = 0;
    int rows = gray_block.rows;
    int cols = gray_block.cols;

    // Koordinat 8 tetangga (radius 1)
    const int dr[] = {-1, -1, -1,  0,  0,  1,  1,  1};
    const int dc[] = {-1,  0,  1, -1,  1, -1,  0,  1};

    for (int i = 0; i < 8; ++i) {
        int nr = r + dr[i];
        int nc = c + dc[i];

        // Penanganan batas (replikasi tepi sederhana)
        nr = std::max(0, std::min(rows - 1, nr));
        nc = std::max(0, std::min(cols - 1, nc));

        // Bandingkan dengan tetangga dan set bit
        if (gray_block.at<float>(nr, nc) >= center) {
            lbp_value |= (1 << i);
        }
    }
    return lbp_value;
}

/**
 * @brief Menghitung entropi Shannon dari histogram LBP.
 * @param gray_block Blok grayscale (CV_32FC1).
 * @return Entropi histogram LBP. Nilai lebih tinggi menandakan tekstur lebih kompleks/acak.
 */
inline float calculate_lbp_histogram_entropy(const cv::Mat& gray_block) {
    if (gray_block.empty() || gray_block.rows < 3 || gray_block.cols < 3) {
        return 0.0f; // Tidak bisa hitung LBP jika blok terlalu kecil
    }
    CV_Assert(gray_block.type() == CV_32FC1);

    std::map<unsigned char, int> hist;
    int total_pixels = 0;

    // Hitung LBP untuk piksel internal (abaikan tepi 1 piksel)
    for (int r = 1; r < gray_block.rows - 1; ++r) {
        for (int c = 1; c < gray_block.cols - 1; ++c) {
            unsigned char lbp_val = calculate_lbp_pixel(gray_block, r, c);
            hist[lbp_val]++;
            total_pixels++;
        }
    }

    if (total_pixels == 0) {
        return 0.0f; // Tidak ada piksel valid
    }

    double entropy = 0.0;
    for (const auto& pair : hist) {
        double probability = static_cast<double>(pair.second) / total_pixels;
        if (probability > 0) { // Hindari log(0)
            entropy -= probability * std::log2(probability);
        }
    }

    return static_cast<float>(entropy);
}

//=============================================================================
// Struktur Data Hasil (Versi SSIM)
//=============================================================================
struct BlockMatchResultSSIM {
    float max_ssim = 0.0f; // Inisialisasi ke nilai terendah yang mungkin (atau -1 jika SSIM bisa negatif)
    float second_max_ssim = 0.0f;
    std::vector<float> all_ssims; // Menyimpan semua SSIM yang dihitung
    int matches_found = 0;
    bool success = false;
    float texture_metric = 0.0f;
    float ssim_at_zero_offset = 0.0f;
};

//=============================================================================
// Fungsi Helper Dasar (Termasuk SSIM Baru)
//=============================================================================

/**
 * @brief Menghitung Structural Similarity Index (SSIM) antara dua blok cv::Mat.
 *        Menghitung rata-rata SSIM per channel.
 * @param block1 Blok pertama (CV_32FC<channels>, nilai piksel [0, 1]).
 * @param block2 Blok kedua (CV_32FC<channels>, nilai piksel [0, 1]).
 * @return Nilai SSIM rata-rata [0, 1]. Mengembalikan 0 jika input tidak valid.
 */
// inline float calculate_block_ssim(const cv::Mat& block1, const cv::Mat& block2) {
//     CV_Assert(block1.size() == block2.size() && block1.type() == block2.type());
//     CV_Assert(block1.type() == CV_32FC(block1.channels())); // Pastikan tipe float

//     if (block1.empty() || block2.empty()) {
//         return 0.0f; // SSIM terendah
//     }

//     int channels = block1.channels();
//     double total_ssim = 0.0;

//     // Split channel jika perlu (lebih mudah dihitung per channel)
//     std::vector<cv::Mat> planes1(channels), planes2(channels);
//     cv::split(block1, planes1);
//     cv::split(block2, planes2);

//     for (int c = 0; c < channels; ++c) {
//         cv::Scalar mu1_s, mu2_s, stddev1_s, stddev2_s;
//         cv::meanStdDev(planes1[c], mu1_s, stddev1_s);
//         cv::meanStdDev(planes2[c], mu2_s, stddev2_s);

//         double mu1 = mu1_s.val[0];
//         double mu2 = mu2_s.val[0];
//         double sigma1_sq = stddev1_s.val[0] * stddev1_s.val[0];
//         double sigma2_sq = stddev2_s.val[0] * stddev2_s.val[0];

//         // Hitung Kovarians sigma12
//         cv::Mat block12;
//         cv::multiply(planes1[c] - mu1, planes2[c] - mu2, block12); // (x-mu_x)*(y-mu_y)
//         double sigma12 = cv::mean(block12).val[0]; // mean dari hasil perkalian

//         // --- Alternatif perhitungan kovarians (kadang lebih stabil) ---
//         // cv::Mat xy_mean_mat;
//         // cv::multiply(planes1[c], planes2[c], xy_mean_mat);
//         // double xy_mean = cv::mean(xy_mean_mat).val[0];
//         // double sigma12 = xy_mean - mu1 * mu2;
//         // -------------------------------------------------------------


//         using namespace MotionMetricsConfig; // Ambil konstanta C1, C2

//         double numerator = (2.0 * mu1 * mu2 + SSIM_C1) * (2.0 * sigma12 + SSIM_C2);
//         double denominator = (mu1 * mu1 + mu2 * mu2 + SSIM_C1) * (sigma1_sq + sigma2_sq + SSIM_C2);

//         double ssim_channel = 0.0;
//         if (std::abs(denominator) > STABILITY_EPSILON) { // Hindari pembagian nol
//             ssim_channel = numerator / denominator;
//         } else if (std::abs(numerator) < STABILITY_EPSILON && std::abs(denominator) < STABILITY_EPSILON) {
//              // Jika num & den ~ 0 (misal blok konstan identik), SSIM = 1
//              ssim_channel = 1.0;
//         }
//         // Clamp ssim per channel jika perlu (meskipun secara teori harusnya [0,1] atau dekat)
//         // ssim_channel = std::max(0.0, std::min(1.0, ssim_channel));

//         total_ssim += ssim_channel;
//     }

//     // Rata-rata SSIM dari semua channel
//     float avg_ssim = static_cast<float>(total_ssim / channels);

//     // Clamp hasil akhir ke [0, 1] untuk keamanan
//     return std::max(0.0f, std::min(1.0f, avg_ssim));
// }


// Fungsi calculate_mad_stddev diubah untuk SSIM (opsional, tapi nama lebih baik)
float calculate_score_stddev(const std::vector<float>& scores) {
    if (scores.size() <= 1) {
        return 0.0f;
    }
    cv::Mat score_mat(scores.size(), 1, CV_32F, const_cast<float*>(scores.data()));
    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(score_mat, mean_val, stddev_val);
    return static_cast<float>(stddev_val.val[0]);
}

/**
 * @brief Menghitung skor keyakinan (confidence) berdasarkan hasil SSIM.
 * @param result Hasil pencarian blok SSIM (BlockMatchResultSSIM).
 * @return Skor keyakinan [0, 1].
 */

 // --- Fungsi BARU untuk LBP Texture Confidence ---
/**
 * @brief Menghitung skor confidence berdasarkan entropi LBP.
 * @param lbp_entropy Entropi histogram LBP blok.
 * @param min_entropy Threshold entropi minimum agar confidence > 0.
 * @param max_entropy Threshold entropi untuk mencapai confidence 1.0.
 * @return Skor texture confidence [0, 1].
 */
inline float calculate_lbp_entropy_confidence(float lbp_entropy, float min_entropy, float max_entropy) {
    if (lbp_entropy < min_entropy) {
        return 0.0f; // Tekstur terlalu simpel/datar
    }
    float confidence = (lbp_entropy - min_entropy) / (max_entropy - min_entropy + MotionMetricsConfig::STABILITY_EPSILON);
    return std::max(0.0f, std::min(1.0f, confidence));
}


float calculate_match_confidence_ssim_smart_static(
    const BlockMatchResultSSIM& result,
    float adaptive_motion_threshold // <- Terima threshold ADAPTIF
) {
    using namespace MotionMetricsConfig;

    if (!result.success || result.matches_found <= 0) {
        return 0.0f;
    }

    // --- 1. Periksa Bukti Statis Kuat ---
    if (result.ssim_at_zero_offset >= STRONG_STATIC_SSIM_THRESHOLD) {
        return CONFIDENCE_FOR_STRONG_STATIC;
    }
    // -----------------------------------

    // --- 2. Logika Normal dengan Threshold Adaptif ---
    float base_ssim_confidence = 0.0f;
    float safe_max_ssim = std::max(0.0f, result.max_ssim);
    float ssim_quality_score = 0.0f;
    // Gunakan adaptive_motion_threshold di sini!
    if (safe_max_ssim >= adaptive_motion_threshold) {
        ssim_quality_score = (safe_max_ssim - adaptive_motion_threshold) / (1.0f - adaptive_motion_threshold + STABILITY_EPSILON);
    }
    ssim_quality_score = std::max(0.0f, std::min(1.0f, ssim_quality_score));

    float ratio_confidence = 1.0f;
    if (result.matches_found > 1) {
        float safe_second_max_ssim = std::max(0.0f, result.second_max_ssim);
        if (safe_max_ssim > CONFIDENCE_EPSILON) { ratio_confidence = 1.0f - (safe_second_max_ssim / safe_max_ssim); }
        else { ratio_confidence = 0.0f; }
        ratio_confidence = std::max(0.0f, std::min(1.0f, ratio_confidence));
    }

    if (result.matches_found == 1) { base_ssim_confidence = std::min(0.75f, ssim_quality_score); }
    else { base_ssim_confidence = ssim_quality_score * ratio_confidence; }
    base_ssim_confidence = std::max(0.0f, std::min(1.0f, base_ssim_confidence));

    float lbp_entropy = result.texture_metric;
    float texture_conf = calculate_lbp_entropy_confidence(lbp_entropy,
                                                          MIN_LBP_ENTROPY_FOR_CONFIDENCE,
                                                          MAX_LBP_ENTROPY_FOR_FULL_CONFIDENCE);

    float final_confidence = base_ssim_confidence * texture_conf;
    return std::max(0.0f, std::min(1.0f, final_confidence));
}


//=============================================================================
// Fungsi Pencarian Blok (Versi SSIM)
//=============================================================================
/**
 * @brief Mencari SSIM maksimum, kedua maksimum, dan semua nilai SSIM dalam area pencarian.
 * @param current_block Blok dari citra saat ini yang ingin dicocokkan.
 * @param reference_tile Tile dari citra referensi tempat pencarian dilakukan.
 * @param block_r_start Posisi baris blok saat ini relatif terhadap tile.
 * @param block_c_start Posisi kolom blok saat ini relatif terhadap tile.
 * @param search_radius Jarak pencarian (radius) di sekitar posisi blok.
 * @return Struct BlockMatchResultSSIM berisi hasil pencarian.
 */
BlockMatchResultSSIM find_best_block_match_ssim(
    const cv::Mat& current_block, // block1 (bisa berwarna)
    const cv::Mat& reference_tile,
    int block_r_start, int block_c_start,
    int search_radius)
{
    BlockMatchResultSSIM result;

    if (current_block.empty() || reference_tile.empty()) return result;
    // Tipe input bisa CV_32FC1 atau CV_32FC3
    CV_Assert(current_block.depth() == CV_32F);

    int tile_h = reference_tile.rows; int tile_w = reference_tile.cols;
    int current_block_h = current_block.rows; int current_block_w = current_block.cols;
    int input_channels = current_block.channels();

    // === Konversi current_block ke Grayscale (Luminance) ===
    cv::Mat gray_block1;
    if (input_channels == 3) {
        cv::cvtColor(current_block, gray_block1, cv::COLOR_BGR2GRAY); // Asumsi BGR
        if(gray_block1.type() != CV_32F) gray_block1.convertTo(gray_block1, CV_32F);
    } else { // Asumsi sudah grayscale jika bukan 3 channel
        if(current_block.type() != CV_32FC1) current_block.convertTo(gray_block1, CV_32F);
        else gray_block1 = current_block;
    }
    // Pastikan tipe akhir adalah CV_32FC1
    CV_Assert(gray_block1.type() == CV_32FC1);
    // ======================================================

    // === Pre-calculation SSIM untuk gray_block1 ===
    cv::Scalar mu1_s, stddev1_s;
    cv::meanStdDev(gray_block1, mu1_s, stddev1_s);
    double mu1 = mu1_s.val[0];
    double sigma1_sq = stddev1_s.val[0] * stddev1_s.val[0];
    // =============================================

    // === Hitung LBP Entropy untuk gray_block1 ===
    result.texture_metric = calculate_lbp_histogram_entropy(gray_block1);
    // ==========================================

    // === Hitung SSIM di Posisi Nol (Zero Offset) menggunakan Grayscale ===
    if (block_r_start >= 0 && block_c_start >= 0 &&
        block_r_start + current_block_h <= tile_h &&
        block_c_start + current_block_w <= tile_w)
    {
        cv::Rect ref_block_orig_roi(block_c_start, block_r_start, current_block_w, current_block_h);
        const cv::Mat ref_block_orig = reference_tile(ref_block_orig_roi);
        cv::Mat gray_block_orig; // Konversi blok referensi original ke gray
        if (input_channels == 3) { cv::cvtColor(ref_block_orig, gray_block_orig, cv::COLOR_BGR2GRAY); if(gray_block_orig.type()!=CV_32F) gray_block_orig.convertTo(gray_block_orig, CV_32F); }
        else { if(ref_block_orig.type() == CV_32FC1) gray_block_orig = ref_block_orig; else ref_block_orig.convertTo(gray_block_orig, CV_32F); }

        // Hitung SSIM antara gray_block1 dan gray_block_orig
        cv::Scalar mu2_s, stddev2_s; cv::meanStdDev(gray_block_orig, mu2_s, stddev2_s);
        double mu2 = mu2_s.val[0]; double sigma2_sq = stddev2_s.val[0] * stddev2_s.val[0];
        cv::Mat block1_orig_product; cv::multiply(gray_block1 - mu1, gray_block_orig - mu2, block1_orig_product);
        double sigma12 = cv::mean(block1_orig_product).val[0];
        using namespace MotionMetricsConfig;
        double num = (2.0 * mu1 * mu2 + SSIM_C1) * (2.0 * sigma12 + SSIM_C2);
        double den = (mu1 * mu1 + mu2 * mu2 + SSIM_C1) * (sigma1_sq + sigma2_sq + SSIM_C2);
        double ssim_val = 0.0; if (std::abs(den) > STABILITY_EPSILON) ssim_val = num / den; else if (std::abs(num) < STABILITY_EPSILON && std::abs(den) < STABILITY_EPSILON) ssim_val = 1.0;
        result.ssim_at_zero_offset = static_cast<float>(std::max(0.0, std::min(1.0, ssim_val)));
    }
    // ================================================================

    int search_r_start = std::max(0, block_r_start - search_radius);
    int search_c_start = std::max(0, block_c_start - search_radius);
    int search_r_end = std::min(tile_h - current_block_h, block_r_start + search_radius);
    int search_c_end = std::min(tile_w - current_block_w, block_c_start + search_radius);

    int estimated_matches = (search_r_end - search_r_start + 1) * (search_c_end - search_c_start + 1);
    if (estimated_matches > 0) result.all_ssims.reserve(estimated_matches);

    // Buffer untuk grayscale ref_block dan perkalian kovarians
    cv::Mat gray_block2;
    cv::Mat block12_product;

    // Loop Pencarian
    for (int search_r = search_r_start; search_r <= search_r_end; ++search_r) {
        for (int search_c = search_c_start; search_c <= search_c_end; ++search_c) {
             // ... (boundary check) ...
             if (search_r < 0 || search_c < 0 || search_r + current_block_h > tile_h || search_c + current_block_w > tile_w) continue;
             cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
             const cv::Mat ref_block = reference_tile(ref_block_roi); // block2 (bisa berwarna)
             CV_Assert(ref_block.depth() == CV_32F);

             // === Konversi ref_block ke Grayscale ===
             if (input_channels == 3) { cv::cvtColor(ref_block, gray_block2, cv::COLOR_BGR2GRAY); if(gray_block2.type()!=CV_32F) gray_block2.convertTo(gray_block2, CV_32F); }
             else { if(ref_block.type() == CV_32FC1) gray_block2 = ref_block; else ref_block.convertTo(gray_block2, CV_32F); }
             CV_Assert(gray_block2.type() == CV_32FC1);
             // =======================================

             // === Hitung SSIM antara gray_block1 dan gray_block2 ===
             cv::Scalar mu2_s, stddev2_s; cv::meanStdDev(gray_block2, mu2_s, stddev2_s);
             double mu2 = mu2_s.val[0]; double sigma2_sq = stddev2_s.val[0] * stddev2_s.val[0];
             cv::multiply(gray_block1 - mu1, gray_block2 - mu2, block12_product);
             double sigma12 = cv::mean(block12_product).val[0];
             using namespace MotionMetricsConfig;
             double num = (2.0 * mu1 * mu2 + SSIM_C1) * (2.0 * sigma12 + SSIM_C2);
             double den = (mu1 * mu1 + mu2 * mu2 + SSIM_C1) * (sigma1_sq + sigma2_sq + SSIM_C2);
             double ssim_val = 0.0; if (std::abs(den) > STABILITY_EPSILON) ssim_val = num / den; else if (std::abs(num) < STABILITY_EPSILON && std::abs(den) < STABILITY_EPSILON) ssim_val = 1.0;
             float current_ssim = static_cast<float>(std::max(0.0, std::min(1.0, ssim_val))); // Clamp
             // =========================================================

             result.all_ssims.push_back(current_ssim);
             result.matches_found++;
             result.success = true;

             // Update max SSIM (sama)
             if (current_ssim > result.max_ssim) { result.second_max_ssim = result.max_ssim; result.max_ssim = current_ssim; }
             else if (current_ssim > result.second_max_ssim) { result.second_max_ssim = current_ssim; }
        }
    }

    // Fallback (Sama, menggunakan ssim_at_zero_offset jika tersedia)
    if (!result.success && result.matches_found == 0) {
        if (block_r_start >= 0 && block_c_start >= 0 && block_r_start + current_block_h <= tile_h && block_c_start + current_block_w <= tile_w) {
            if (result.ssim_at_zero_offset >= 0) { // Cek jika ssim_at_zero_offset valid (>=0)
                 result.max_ssim = result.ssim_at_zero_offset;
                 result.second_max_ssim = result.ssim_at_zero_offset;
                 result.all_ssims.push_back(result.max_ssim);
                 result.matches_found = 1;
                 result.success = true;
            }
        }
    }

    return result;
}

//=============================================================================
// Fungsi Akumulasi (Versi SSIM)
//=============================================================================
extern "C"
{
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr,
        float *weight_map_sum_ptr,
        const float *current_image_ptr,
        const float *reference_image_ptr,
        const float *base_window_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h, int w, int channels,
        float base_motion_threshold, // <- Terima BASE threshold dari Python
        float estimated_noise_sigma, // <- Terima estimasi noise dari Python
        int mbm_block_h, int mbm_block_w, int mbm_search_radius)
    {
        using namespace MotionMetricsConfig;
        // ... (Validasi input & setup Mat sama) ...
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h <= 0 || w <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            mbm_block_h <= 0 || mbm_block_w <= 0) return;
        int mat_type = CV_32FC(channels);
        if (mat_type == 0) return;
        cv::Mat final_image_sum_mat(h, w, mat_type, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h, w, CV_32FC1, weight_map_sum_ptr);
        const cv::Mat current_image_mat(h, w, mat_type, const_cast<float*>(current_image_ptr));
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float*>(reference_image_ptr));
        const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));


        #pragma omp parallel
        {
            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    // ... (Get tile ROIs sama) ...
                     int r = row_starts[i]; int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w) continue;
                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    const cv::Mat current_tile = current_image_mat(tile_roi);
                    const cv::Mat reference_tile = reference_image_mat(tile_roi);


                    // === Hitung Adaptive Motion Threshold untuk TILE ini ===
                    // Versi sederhana: hanya berdasarkan noise global
                    float adaptive_motion_threshold = base_motion_threshold - NOISE_INFLUENCE_FACTOR * estimated_noise_sigma;
                    // Clamp threshold ke rentang yang wajar
                    adaptive_motion_threshold = std::max(MIN_ADAPTIVE_MOTION_THRESHOLD,
                                                       std::min(MAX_ADAPTIVE_MOTION_THRESHOLD, adaptive_motion_threshold));
                    // =====================================================

                    int num_blocks_h = (mbm_block_h > 0)? (tile_h + mbm_block_h - 1) / mbm_block_h : 0;
                    int num_blocks_w = (mbm_block_w > 0)? (tile_w + mbm_block_w - 1) / mbm_block_w : 0;
                    int num_blocks_in_tile = num_blocks_h * num_blocks_w;
                    cv::Mat block_confidences = cv::Mat::zeros(num_blocks_h, num_blocks_w, CV_32FC1);

                    if (num_blocks_in_tile > 0) {
                        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                                // ... (Get MBM block ROIs sama) ...
                                int block_local_r_start = bh_idx*mbm_block_h; int block_local_c_start = bw_idx*mbm_block_w;
                                int current_block_h = std::min(mbm_block_h, tile_h - block_local_r_start);
                                int current_block_w = std::min(mbm_block_w, tile_w - block_local_c_start);
                                if(current_block_h <= 0 || current_block_w <= 0) continue;
                                cv::Rect current_block_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                const cv::Mat current_block = current_tile(current_block_roi);

                                // === Cari match SSIM ===
                                BlockMatchResultSSIM block_result = find_best_block_match_ssim(
                                    current_block, reference_tile, block_local_r_start, block_local_c_start, mbm_search_radius);

                                // === Gunakan Confidence "Pintar" dengan Threshold ADAPTIF ===
                                float confidence = calculate_match_confidence_ssim_smart_static(block_result, adaptive_motion_threshold);
                                // =============================================================

                                block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                            }
                        }
                    }

                    // Akumulasi Piksel & Bobot (Tidak Berubah)
                    if (num_blocks_in_tile > 0) {
                         // ... (Loop y, x, atomic updates sama persis) ...
                        for (int y = 0; y < tile_h; ++y) {
                             const float* current_tile_row = current_tile.ptr<float>(y);
                             const float* base_window_row = base_window_tile_mat.ptr<float>(y);
                             int gy = r + y;
                             float* global_weight_sum_row = weight_map_sum_mat.ptr<float>(gy);
                             float* global_pixel_sum_row = final_image_sum_mat.ptr<float>(gy);
                             for (int x = 0; x < tile_w; ++x) {
                                 int bh_idx = std::min(y / mbm_block_h, num_blocks_h - 1);
                                 int bw_idx = std::min(x / mbm_block_w, num_blocks_w - 1);
                                 float block_confidence = block_confidences.at<float>(bh_idx, bw_idx);
                                 float base_win_val = base_window_row[x];
                                 float pixel_weight = base_win_val * block_confidence;
                                 if (pixel_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                                     int gx = c + x;
                                     #pragma omp atomic update
                                     global_weight_sum_row[gx] += pixel_weight;
                                     float weighted_pixel_value;
                                     int current_pixel_idx_local = x * channels;
                                     int current_pixel_idx_global = gx * channels;
                                     for (int ch = 0; ch < channels; ++ch) {
                                         weighted_pixel_value = current_tile_row[current_pixel_idx_local + ch] * pixel_weight;
                                         #pragma omp atomic update
                                         global_pixel_sum_row[current_pixel_idx_global + ch] += weighted_pixel_value;
                                     }
                                 }
                             }
                         }
                    }
                } // End inner loop (j)
            } // End outer loop (i)
        } // End parallel region
    } // End accumulate_frame_weighted_jit


    // Fungsi BARU: Normalisasi Setelah Semua Frame Diakumulasi
    void normalize_accumulated_image_jit(
        float *final_image_ptr,     // Buffer hasil SUM (akan dimodifikasi jadi rata-rata)
        const float *weight_map_sum_ptr, // Buffer SUM bobot (hanya dibaca)
        int h, int w, int channels)
    {
        using namespace MotionMetricsConfig;

        if (!final_image_ptr || !weight_map_sum_ptr || h <= 0 || w <= 0 || channels <= 0) {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0) return;

        // Mat header untuk buffer SUM (target modifikasi)
        cv::Mat final_image_mat(h, w, mat_type, final_image_ptr);
        // Mat header untuk buffer bobot (read-only)
        const cv::Mat weight_map_sum_mat(h, w, CV_32FC1, const_cast<float*>(weight_map_sum_ptr));

        #pragma omp parallel for collapse(2) schedule(static)
        for (int gy = 0; gy < h; ++gy) {
            for (int gx = 0; gx < w; ++gx) {
                // Baca total bobot dari buffer sum bobot
                float total_weight = weight_map_sum_mat.at<float>(gy, gx);

                // Dapatkan pointer ke baris di buffer sum piksel (yang akan dinormalisasi)
                float* final_pixel_row = final_image_mat.ptr<float>(gy);
                int pixel_idx = gx * channels;

                if (total_weight > GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD) {
                    float inv_total_weight = 1.0f / total_weight;
                    for (int ch = 0; ch < channels; ++ch) {
                        // Normalisasi: sum(pixel*weight) / sum(weight)
                        // Modifikasi buffer final_image_mat secara langsung
                        final_pixel_row[pixel_idx + ch] *= inv_total_weight;
                    }
                } else {
                    // Set piksel ke nol jika bobot total rendah
                    for (int ch = 0; ch < channels; ++ch) {
                        final_pixel_row[pixel_idx + ch] = 0.0f;
                    }
                }
            } // gx loop
        } // gy loop
    } // End normalize_accumulated_image_jit

} // end extern "C"