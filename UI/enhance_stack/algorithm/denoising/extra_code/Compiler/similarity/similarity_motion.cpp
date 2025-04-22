#include <cmath>
#include <vector>
#include <limits>
#include <algorithm>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/core/utility.hpp> // Untuk CV_Assert

//=============================================================================
// Konstanta dan Konfigurasi
//=============================================================================
namespace MotionMetricsConfig {
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-5f;
    constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f;
    constexpr float ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR = 1.5f;
    constexpr int DEFAULT_SEARCH_RADIUS = 7; // Tetap ada jika diperlukan default
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
}

//=============================================================================
// Struktur Data Hasil
//=============================================================================

/**
 * @brief Menyimpan hasil dari pencarian block matching untuk satu blok.
 */
struct BlockMatchResult {
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    std::vector<float> all_mads; // Menyimpan semua MAD yang dihitung di area pencarian
    int matches_found = 0;       // Jumlah kandidat match yang valid dievaluasi
    bool success = false;        // Menandakan apakah setidaknya satu match ditemukan/dihitung
};

//=============================================================================
// Fungsi Helper Dasar
//=============================================================================

/**
 * @brief Menghitung Mean Absolute Difference (MAD) antara dua blok cv::Mat.
 * @param block1 Blok pertama (CV_32FC<channels>).
 * @param block2 Blok kedua (CV_32FC<channels>), ukuran dan tipe harus sama.
 * @return Nilai MAD rata-rata per elemen.
 */
inline float calculate_block_mad(const cv::Mat& block1, const cv::Mat& block2)
{
    CV_Assert(block1.size() == block2.size() && block1.type() == block2.type());
    CV_Assert(block1.type() == CV_32FC(block1.channels())); // Pastikan tipe float

    // Jika salah satu blok kosong (bisa terjadi di tepi jika tidak hati-hati)
    if (block1.empty() || block2.empty()) {
        return std::numeric_limits<float>::max(); // Kembalikan nilai tinggi sebagai indikasi error/tidak valid
    }

    cv::Mat diff;
    cv::absdiff(block1, block2, diff);

    cv::Scalar sad_per_channel = cv::sum(diff);
    double total_sad = 0.0;
    for (int i = 0; i < diff.channels(); ++i) {
        total_sad += sad_per_channel[i];
    }

    // Jumlah elemen total (piksel * channel)
    float num_elements = static_cast<float>(block1.total() * block1.channels());

    if (num_elements <= 0) {
        return 0.0f; // Jika blok tidak punya elemen (secara teori tidak mungkin jika tidak empty)
    }

    return static_cast<float>(total_sad / num_elements);
}

/**
 * @brief Menghitung standar deviasi dari sekumpulan nilai MAD.
 * @param mad_values Vektor berisi nilai-nilai MAD.
 * @return Standar deviasi, atau 0.0 jika input tidak cukup.
 */
float calculate_mad_stddev(const std::vector<float>& mad_values) {
    if (mad_values.size() <= 1) {
        return 0.0f; // Stddev tidak terdefinisi untuk <= 1 elemen
    }

    // Buat Mat header tanpa menyalin data (lebih efisien)
    // Gunakan const_cast karena cv::meanStdDev tidak memiliki overload const Mat*
    cv::Mat mad_mat(mad_values.size(), 1, CV_32F, const_cast<float*>(mad_values.data()));

    cv::Scalar mean_val, stddev_val;
    cv::meanStdDev(mad_mat, mean_val, stddev_val);

    // Ambil nilai stddev dari channel pertama (karena input 1D)
    return static_cast<float>(stddev_val.val[0]);
}

/**
 * @brief Menghitung skor keyakinan (confidence) untuk sebuah match blok.
 * @param result Hasil pencarian blok dari find_best_block_match.
 * @param motion_threshold Threshold gerak dasar.
 * @return Skor keyakinan [0, 1].
 */
float calculate_match_confidence(const BlockMatchResult& result, float motion_threshold)
{
    using namespace MotionMetricsConfig;

    float match_confidence = 0.0f;
    // Denominator untuk skala kualitas absolut, hindari pembagian dengan nol
    float quality_denominator = CONFIDENCE_SCALE_FACTOR * motion_threshold + STABILITY_EPSILON;

    // Handle kasus tidak ada match atau hanya satu match
    if (!result.success || result.matches_found <= 0) {
        match_confidence = 0.0f; // Tidak ada match, tidak ada keyakinan
    } else if (result.matches_found == 1) {
        // Hanya satu kandidat, keyakinan hanya berdasarkan kualitas absolut
        if (quality_denominator > 0) {
             // Eksponensial decay berdasarkan MAD minimum
             // Pastikan min_mad tidak negatif sebelum dimasukkan ke exp
            match_confidence = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
            // Jika threshold (dan epsilon) nol, hanya match sempurna (MAD=0) yang punya confidence
             match_confidence = (result.min_mad <= CONFIDENCE_EPSILON) ? 0.5f : 0.0f; // Batas atas 0.5
        }
        // Batasi keyakinan maksimal hingga 0.5 jika hanya ada satu match (kurang 'unik')
        match_confidence = std::min(0.5f, std::max(0.0f, match_confidence));
    } else {
        // Lebih dari satu kandidat, gunakan rasio dan kualitas absolut

        // 1. Ratio Confidence (Seberapa unik match terbaik dibandingkan yg kedua?)
        float ratio = 1.0f; // Default jika second_min_mad sangat kecil atau sama dengan min_mad
        // Hindari pembagian dengan nol atau nilai yang sangat kecil
        if (result.second_min_mad > CONFIDENCE_EPSILON) {
            float safe_min_mad = std::max(0.0f, result.min_mad); // Pastikan non-negatif
             // Rasio MAD terbaik terhadap MAD kedua terbaik
            ratio = safe_min_mad / result.second_min_mad;
        }
        // Confidence tinggi jika ratio kecil (min_mad jauh lebih baik dari second_min_mad)
        // 1.0 - ratio memberikan nilai tinggi saat ratio mendekati 0
        float ratio_confidence = std::max(0.0f, 1.0f - ratio);

        // 2. Absolute Quality Confidence (Seberapa bagus match terbaik secara absolut?)
        float absolute_quality = 0.0f;
        if (quality_denominator > 0) {
             // Eksponensial decay berdasarkan MAD minimum
            absolute_quality = std::exp(-std::max(0.0f, result.min_mad) / quality_denominator);
        } else {
            // Jika threshold nol, match sempurna (MAD=0) -> confidence 1, lainnya 0
            absolute_quality = (std::max(0.0f, result.min_mad) <= CONFIDENCE_EPSILON) ? 1.0f : 0.0f;
        }
         // Pastikan dalam rentang [0, 1]
        absolute_quality = std::max(0.0f, std::min(1.0f, absolute_quality));

        // 3. Kombinasikan: Keyakinan adalah produk dari keunikan (ratio) dan kualitas absolut
        match_confidence = ratio_confidence * absolute_quality;
    }

    // Pastikan hasil akhir dalam rentang [0, 1] sebelum dikembalikan
    return std::max(0.0f, std::min(1.0f, match_confidence));
}

//=============================================================================
// Fungsi Pencarian Blok
//=============================================================================

/**
 * @brief Mencari MAD minimum, kedua minimum, dan semua nilai MAD dalam area pencarian.
 * @param current_block Blok dari citra saat ini yang ingin dicocokkan.
 * @param reference_tile Tile dari citra referensi tempat pencarian dilakukan.
 * @param block_r_start Posisi baris blok saat ini relatif terhadap tile.
 * @param block_c_start Posisi kolom blok saat ini relatif terhadap tile.
 * @param search_radius Jarak pencarian (radius) di sekitar posisi blok.
 * @return Struct BlockMatchResult berisi hasil pencarian.
 */
BlockMatchResult find_best_block_match(
    const cv::Mat& current_block,
    const cv::Mat& reference_tile,
    int block_r_start, int block_c_start,
    int search_radius)
{
    BlockMatchResult result; // Inisialisasi default (nilai max, count 0, success false)

    int tile_h = reference_tile.rows;
    int tile_w = reference_tile.cols;
    int current_block_h = current_block.rows;
    int current_block_w = current_block.cols;

    // Tentukan Batas Area Pencarian yang valid di dalam tile referensi
    // Pastikan batas awal tidak negatif
    int search_r_start = std::max(0, block_r_start - search_radius);
    int search_c_start = std::max(0, block_c_start - search_radius);
    // Pastikan batas akhir memungkinkan blok referensi muat sepenuhnya di dalam tile
    int search_r_end = std::min(tile_h - current_block_h, block_r_start + search_radius);
    int search_c_end = std::min(tile_w - current_block_w, block_c_start + search_radius);

    // Pre-alokasi vektor MAD jika memungkinkan (estimasi kasar ukuran area pencarian)
    int estimated_matches = (search_r_end - search_r_start + 1) * (search_c_end - search_c_start + 1);
    if (estimated_matches > 0) {
        result.all_mads.reserve(estimated_matches);
    }

    // Loop Pencarian di Area Referensi
    for (int search_r = search_r_start; search_r <= search_r_end; ++search_r) {
        for (int search_c = search_c_start; search_c <= search_c_end; ++search_c) {
            // Boundary check (seharusnya sudah aman karena perhitungan search_r/c_end, tapi double check)
            if (search_r < 0 || search_c < 0 ||
                search_r + current_block_h > tile_h ||
                search_c + current_block_w > tile_w) {
                continue;
            }

            // Dapatkan ROI untuk blok referensi kandidat
            cv::Rect ref_block_roi(search_c, search_r, current_block_w, current_block_h);
            const cv::Mat ref_block = reference_tile(ref_block_roi);

            // Hitung MAD antara blok saat ini dan blok referensi kandidat
            float current_mad = calculate_block_mad(current_block, ref_block);

            result.all_mads.push_back(current_mad);
            result.matches_found++;
            result.success = true; // Setidaknya satu perbandingan berhasil

            // Update MAD minimum pertama dan kedua
            if (current_mad < result.min_mad) {
                result.second_min_mad = result.min_mad; // Geser min lama ke second min
                result.min_mad = current_mad;        // Simpan min baru
            } else if (current_mad < result.second_min_mad) {
                result.second_min_mad = current_mad; // Update second min
            }
        } // End search_c loop
    } // End search_r loop

    // Jika setelah loop tidak ada match ditemukan (area pencarian 0 atau masalah lain)
    // 'success' akan tetap false, dan nilai MAD akan tetap max.

    return result;
}


//=============================================================================
// Fungsi Perhitungan Metrik Gerak per Tile
//=============================================================================
extern "C"
{
    /**
     * @brief Menghitung bobot kesamaan (similarity) dan threshold gerak adaptif antara dua tile citra.
     * Versi ini memproses satu tile secara sekuensial (paralelisasi terjadi di level pemanggil).
     *
     * @param current_tile Tile citra saat ini (CV_32FC<channels>).
     * @param reference_tile Tile citra referensi (CV_32FC<channels>).
     * @param block_h Tinggi blok untuk matching (dalam piksel).
     * @param block_w Lebar blok untuk matching (dalam piksel).
     * @param search_radius Jarak maksimum pencarian blok referensi.
     * @param motion_threshold Threshold dasar untuk menentukan pergerakan signifikan.
     * @param similarity_weight Output: Bobot kesamaan antara tile [0, 1].
     * @param adaptive_threshold Output: Threshold gerak adaptif.
     */
    void compute_tile_motion_metrics(
        const cv::Mat& current_tile, const cv::Mat& reference_tile,
        int block_h, int block_w,
        int search_radius,
        float motion_threshold,
        // Parameter epsilon dihilangkan, gunakan konstanta namespace
        float *similarity_weight,
        float *adaptive_threshold
    ) {
        using namespace MotionMetricsConfig; // Menggunakan konstanta dari namespace

        int tile_h = current_tile.rows;
        int tile_w = current_tile.cols;

        // Inisialisasi output ke nilai default/aman
        *similarity_weight = 0.0f; // Default jika ada error atau tidak ada blok
        *adaptive_threshold = motion_threshold;

        // Validasi input dasar
        if (tile_h <= 0 || tile_w <= 0 || block_h <= 0 || block_w <= 0 ||
            current_tile.empty() || reference_tile.empty() ||
            current_tile.size() != reference_tile.size() ||
            current_tile.type() != reference_tile.type())
        {
            // Bisa ditambahkan logging error di sini jika diperlukan
            return; // Keluar dengan nilai output default
        }

        // Jumlah blok berdasarkan pembagian integer (membulatkan ke atas)
        // Pastikan pembagi tidak nol
        int num_blocks_h = (block_h > 0) ? (tile_h + block_h - 1) / block_h : 0;
        int num_blocks_w = (block_w > 0) ? (tile_w + block_w - 1) / block_w : 0;
        int num_blocks = num_blocks_h * num_blocks_w;

        // --- Fallback jika tile terlalu kecil untuk satu blok pun ---
        if (num_blocks == 0) {
             // Hitung MAD keseluruhan tile sebagai fallback sederhana
            float diff = calculate_block_mad(current_tile, reference_tile);

            // Hitung similarity berdasarkan diff global ini
            float sim_denominator = motion_threshold + STABILITY_EPSILON;
            if (sim_denominator > STABILITY_EPSILON) { // Cek pembagi > 0
                *similarity_weight = std::exp(-std::max(0.0f, diff) / sim_denominator);
            } else {
                *similarity_weight = (diff <= STABILITY_EPSILON) ? 1.0f : 0.0f;
            }
            *similarity_weight = std::max(0.0f, std::min(1.0f, *similarity_weight)); // Clamp [0, 1]
            // adaptive_threshold tetap pada nilai motion_threshold input
            return;
        }

        // --- Proses Block Matching (Sekuensial di fungsi ini) ---
        double sum_adjusted_min_mad = 0.0; // Akumulator MAD minimum per blok (disesuaikan confidence)
        double sum_block_mad_stddev = 0.0; // Akumulator standar deviasi MAD per blok
        int valid_blocks_processed = 0;     // Hitung blok yang benar-benar diproses

        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                int block_r_start = bh_idx * block_h;
                int block_c_start = bw_idx * block_w;

                // Ukuran blok aktual (penting untuk blok di tepi tile)
                int current_block_h = std::min(block_h, tile_h - block_r_start);
                int current_block_w = std::min(block_w, tile_w - block_c_start);

                // Lewati jika blok ini memiliki dimensi nol (seharusnya tidak terjadi jika num_blocks > 0)
                if (current_block_h <= 0 || current_block_w <= 0) continue;

                // Dapatkan ROI (view, tanpa copy) blok saat ini
                cv::Rect current_block_roi(block_c_start, block_r_start, current_block_w, current_block_h);
                const cv::Mat current_block = current_tile(current_block_roi);

                // Cari match terbaik di area pencarian pada tile referensi
                BlockMatchResult block_result = find_best_block_match(
                    current_block, reference_tile,
                    block_r_start, block_c_start, search_radius
                );

                // Fallback jika tidak ada match ditemukan sama sekali di area pencarian
                if (!block_result.success) {
                     // Coba bandingkan dengan posisi original di referensi sebagai fallback terakhir
                     // Pastikan posisi original valid
                     if (block_r_start + current_block_h <= tile_h && block_c_start + current_block_w <= tile_w) {
                         cv::Rect ref_block_orig_roi(block_c_start, block_r_start, current_block_w, current_block_h);
                         const cv::Mat ref_block_orig = reference_tile(ref_block_orig_roi);
                         block_result.min_mad = calculate_block_mad(current_block, ref_block_orig);
                         // Set nilai lain agar konsisten untuk kalkulasi confidence
                         block_result.second_min_mad = block_result.min_mad; // Tidak ada second best
                         block_result.all_mads.push_back(block_result.min_mad);
                         block_result.matches_found = 1;
                         block_result.success = true; // Sekarang ada hasil
                     } else {
                        // Jika posisi original pun tidak valid (sangat jarang), lewati blok ini
                        continue; // Tidak ada data valid untuk blok ini
                     }
                }

                // --- Hitung metrik untuk blok ini ---
                // 1. Standar Deviasi MAD
                float mad_stddev = calculate_mad_stddev(block_result.all_mads);
                sum_block_mad_stddev += static_cast<double>(mad_stddev);

                // 2. Keyakinan Match
                float match_confidence = calculate_match_confidence(block_result, motion_threshold);

                // 3. Sesuaikan MAD minimum berdasarkan keyakinan
                //    MAD efektif akan lebih tinggi jika confidence rendah (kurang yakin matchnya bagus)
                //    Tambahkan epsilon untuk mencegah pembagian dengan nol jika confidence = 0
                float adjusted_mad = block_result.min_mad / (match_confidence + CONFIDENCE_EPSILON);
                // Hindari nilai negatif atau sangat kecil yang tidak wajar
                adjusted_mad = std::max(0.0f, adjusted_mad);
                sum_adjusted_min_mad += static_cast<double>(adjusted_mad);

                valid_blocks_processed++; // Tambah counter blok yang diproses

            } // End block_w loop (bw_idx)
        } // End block_h loop (bh_idx)

        // ----- Hitung Metrik Akhir untuk Tile -----

        // Pastikan ada blok yang diproses untuk menghindari pembagian dengan nol
        if (valid_blocks_processed > 0) {
            // 1. Rata-rata MAD minimum per blok (yang sudah disesuaikan keyakinan)
            float average_adjusted_mad = static_cast<float>(sum_adjusted_min_mad / valid_blocks_processed);

            // 2. Hitung Similarity Weight berdasarkan rata-rata MAD yang disesuaikan
            float sim_denominator = motion_threshold + STABILITY_EPSILON;
            if (sim_denominator > STABILITY_EPSILON) { // Cek pembagi > 0
                *similarity_weight = std::exp(-average_adjusted_mad / sim_denominator);
            } else {
                 *similarity_weight = (average_adjusted_mad <= STABILITY_EPSILON) ? 1.0f : 0.0f;
            }
             // Clamp hasil akhir similarity [0, 1]
            *similarity_weight = std::max(0.0f, std::min(1.0f, *similarity_weight));

            // 3. Hitung Threshold Adaptif Rata-Rata
            float average_mad_stddev = static_cast<float>(sum_block_mad_stddev / valid_blocks_processed);
            *adaptive_threshold = motion_threshold + ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR * average_mad_stddev;
            // Pastikan threshold adaptif tidak negatif
            *adaptive_threshold = std::max(0.0f, *adaptive_threshold);
        } else {
             // Jika tidak ada blok valid yang diproses (kasus aneh), kembalikan nilai default.
             // *similarity_weight sudah 0.0f, *adaptive_threshold sudah motion_threshold.
        }

    } // End compute_tile_motion_metrics


    //=============================================================================
    // Fungsi Akumulasi Tile (Tingkat Atas) - VERSI REVISI DENGAN BOBOT LOKAL
    //=============================================================================
    /**
     * @brief Mengakumulasi tile-tile dari citra saat ini ke citra final berdasarkan
     *        bobot kesamaan LOKAL per blok MBM.
     * Fungsi ini menghitung confidence per blok MBM dan menggunakannya untuk membobot
     * piksel dalam blok tersebut. TIDAK menggunakan Motion Compensation.
     *
     * @param final_image_ptr Pointer ke buffer citra output (akumulasi). Tipe float.
     * @param weight_map_ptr Pointer ke buffer peta bobot (akumulasi). Tipe float.
     * @param current_image_ptr Pointer ke buffer citra input saat ini. Tipe float.
     * @param reference_image_ptr Pointer ke buffer citra input referensi. Tipe float.
     * @param base_window_ptr Pointer ke buffer jendela pembobot dasar (ukuran per tile). Tipe float, 1 channel.
     * @param row_starts Array posisi awal baris untuk setiap tile. int32.
     * @param col_starts Array posisi awal kolom untuk setiap tile. int32.
     * @param num_row_starts Jumlah elemen dalam row_starts.
     * @param num_col_starts Jumlah elemen dalam col_starts.
     * @param tile_h Tinggi setiap tile (untuk blending).
     * @param tile_w Lebar setiap tile (untuk blending).
     * @param h Tinggi total citra.
     * @param w Lebar total citra.
     * @param channels Jumlah channel citra.
     * @param motion_threshold Threshold dasar untuk perhitungan confidence blok.
     * @param scale Faktor skala tambahan untuk nilai piksel saat akumulasi.
     * @param mbm_block_h Tinggi blok untuk block matching (ME).
     * @param mbm_block_w Lebar blok untuk block matching (ME).
     * @param mbm_search_radius Radius pencarian untuk block matching (ME).
     */
    void accumulate_frame_weighted_jit(
        float *final_image_sum_ptr, // Buffer untuk MENAMBAH hasil
        float *weight_map_sum_ptr,  // Buffer untuk MENAMBAH bobot
        const float *current_image_ptr,
        const float *reference_image_ptr, // Masih perlu untuk confidence
        const float *base_window_ptr,
        const int *row_starts, const int *col_starts,
        int num_row_starts, int num_col_starts,
        int tile_h, int tile_w,
        int h, int w, int channels,
        float motion_threshold, // Perlu untuk confidence
        // 'scale' TIDAK diperlukan di sini
        int mbm_block_h, int mbm_block_w, int mbm_search_radius)
    {
        using namespace MotionMetricsConfig; // Menggunakan konstanta

        // --- Validasi & Setup Mat Header (Sama seperti sebelumnya) ---
        if (!final_image_sum_ptr || !weight_map_sum_ptr || !current_image_ptr || !reference_image_ptr || !base_window_ptr ||
            !row_starts || !col_starts || h <= 0 || w <= 0 || tile_h <= 0 || tile_w <= 0 || channels <= 0 ||
            mbm_block_h <= 0 || mbm_block_w <= 0) {
            return;
        }
        int mat_type = CV_32FC(channels);
        if (mat_type == 0) return;

        // Mat header untuk buffer AKUMULASI (target penambahan)
        cv::Mat final_image_sum_mat(h, w, mat_type, final_image_sum_ptr);
        cv::Mat weight_map_sum_mat(h, w, CV_32FC1, weight_map_sum_ptr);
        // Mat header untuk input frame saat ini & referensi
        const cv::Mat current_image_mat(h, w, mat_type, const_cast<float*>(current_image_ptr));
        const cv::Mat reference_image_mat(h, w, mat_type, const_cast<float*>(reference_image_ptr)); // Untuk confidence
        const cv::Mat base_window_tile_mat(tile_h, tile_w, CV_32FC1, const_cast<float*>(base_window_ptr));

        #pragma omp parallel
        {
            #pragma omp for collapse(2) schedule(static)
            for (int i = 0; i < num_row_starts; i++) {
                for (int j = 0; j < num_col_starts; j++) {
                    int r = row_starts[i];
                    int c = col_starts[j];
                    if (r < 0 || c < 0 || (r + tile_h) > h || (c + tile_w) > w) continue;

                    cv::Rect tile_roi(c, r, tile_w, tile_h);
                    const cv::Mat current_tile = current_image_mat(tile_roi);
                    const cv::Mat reference_tile = reference_image_mat(tile_roi); // Untuk confidence

                    // Tahap 1: Hitung Confidence (Sama seperti sebelumnya)
                    int num_blocks_h = (mbm_block_h > 0) ? (tile_h + mbm_block_h - 1) / mbm_block_h : 0;
                    int num_blocks_w = (mbm_block_w > 0) ? (tile_w + mbm_block_w - 1) / mbm_block_w : 0;
                    int num_blocks_in_tile = num_blocks_h * num_blocks_w;
                    cv::Mat block_confidences = cv::Mat::zeros(num_blocks_h, num_blocks_w, CV_32FC1);
                    
                    if (num_blocks_in_tile > 0) {
                        for (int bh_idx = 0; bh_idx < num_blocks_h; ++bh_idx) {
                            for (int bw_idx = 0; bw_idx < num_blocks_w; ++bw_idx) {
                                int block_local_r_start = bh_idx * mbm_block_h;
                                int block_local_c_start = bw_idx * mbm_block_w;
                                int current_block_h = std::min(mbm_block_h, tile_h - block_local_r_start);
                                int current_block_w = std::min(mbm_block_w, tile_w - block_local_c_start);

                                if (current_block_h <= 0 || current_block_w <= 0) continue;

                                cv::Rect current_block_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                const cv::Mat current_block = current_tile(current_block_roi);

                                BlockMatchResult block_result = find_best_block_match(
                                    current_block, reference_tile, // Bandingkan DENGAN referensi
                                    block_local_r_start, block_local_c_start,
                                    mbm_search_radius
                                );

                                if (!block_result.success) { // Fallback (sama seperti sebelumnya)
                                     if (block_local_r_start + current_block_h <= tile_h && block_local_c_start + current_block_w <= tile_w) {
                                         cv::Rect ref_block_orig_roi(block_local_c_start, block_local_r_start, current_block_w, current_block_h);
                                         const cv::Mat ref_block_orig = reference_tile(ref_block_orig_roi); // Bandingkan DENGAN referensi
                                         block_result.min_mad = calculate_block_mad(current_block, ref_block_orig);
                                         block_result.second_min_mad = block_result.min_mad;
                                         block_result.matches_found = 1;
                                         block_result.success = true;
                                     } else {
                                         block_result.success = false;
                                     }
                                }

                                float confidence = 0.0f;
                                if(block_result.success) {
                                    // Gunakan motion_threshold yang diterima fungsi ini
                                    confidence = calculate_match_confidence(block_result, motion_threshold);
                                }
                                block_confidences.at<float>(bh_idx, bw_idx) = confidence;
                            }
                        }
                    } // end if num_blocks_in_tile > 0


                    // Tahap 2: Akumulasi Piksel & Bobot (Sama seperti sebelumnya, TAPI targetnya beda)
                    if (num_blocks_in_tile > 0) {
                        for (int y = 0; y < tile_h; ++y) {
                            const float* current_tile_row = current_tile.ptr<float>(y);
                            const float* base_window_row = base_window_tile_mat.ptr<float>(y);
                            int gy = r + y;
                            // Pointer ke buffer AKUMULASI global
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
                                    // Akumulasi Bobot (Atomic) - Target: weight_map_sum_mat
                                    #pragma omp atomic update
                                    global_weight_sum_row[gx] += pixel_weight;

                                    // Akumulasi Piksel Terbobot (Atomic) - Target: final_image_sum_mat
                                    float weighted_pixel_value;
                                    int current_pixel_idx_local = x * channels;
                                    int current_pixel_idx_global = gx * channels;
                                    for (int ch = 0; ch < channels; ++ch) {
                                        // Pixel * weight (input pixel sudah [0,1])
                                        weighted_pixel_value = current_tile_row[current_pixel_idx_local + ch] * pixel_weight;
                                        #pragma omp atomic update
                                        global_pixel_sum_row[current_pixel_idx_global + ch] += weighted_pixel_value;
                                    }
                                } // end if pixel_weight threshold
                            } // x loop
                        } // y loop
                    } // end if num_blocks_in_tile > 0
                } // End col_starts loop (j)
            } // End row_starts loop (i)
        } // End parallel region
        // --- TIDAK ADA TAHAP NORMALISASI DI SINI ---
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