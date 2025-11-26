#include "alignment_tile.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/ximgproc.hpp>
#include <vector>
#include <cmath>
#include <numeric>
#include <immintrin.h>
#include <map>
#include <algorithm>
#include <functional>
#include <omp.h>
#include <iostream>
#include <chrono>
#include <string>
#include "alignment_tile.h"
#include "cost_function.hpp"
#include "refinement.hpp"

// class SimpleTimer
// {
// public:
//     SimpleTimer(const std::string &name)
//         : m_name(name), m_start(std::chrono::high_resolution_clock::now())
//     {
//     }

//     ~SimpleTimer()
//     {
//         auto end = std::chrono::high_resolution_clock::now();
//         auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - m_start);
//         std::cout << "[C++ Timer] " << m_name << ": "
//                   << duration.count() / 1000.0 << " ms" << std::endl;
//     }

// private:
//     std::string m_name;
//     std::chrono::time_point<std::chrono::high_resolution_clock> m_start;
// };

// =========================================================================
// === HELPER FUNCTIONS - Static Implementation ===
// =========================================================================

struct Candidate
{
    cv::Point2f flow;
    float cost;
};

struct TileResult
{
    cv::Rect roi;
    cv::Point2f flow;
};

// Konstanta konfigurasi
namespace ImageAlignmentConfig
{
    constexpr int GAUSSIAN_CACHE_SIZE = 256;
    constexpr float NORMALIZATION_EPSILON = 1e-6f;
    constexpr float FLOW_UPSCALE_FACTOR = 2.0f;
    constexpr int MIN_TILE_SIZE = 8;
    constexpr int MIN_PYRAMID_LAYER_SIZE = 32;
}

namespace AlignmentFlowHelpers
{
    // Cache untuk Gaussian window
    static thread_local std::map<std::pair<int, int>, cv::Mat> gaussian_cache;

    /**
     * Mendapatkan Gaussian window dengan caching
     */
    static const cv::Mat &getGaussianWindow(int rows, int cols)
    {
        using namespace ImageAlignmentConfig;

        auto key = std::make_pair(rows, cols);
        auto it = gaussian_cache.find(key);
        if (it != gaussian_cache.end())
            return it->second;

        if (gaussian_cache.size() >= GAUSSIAN_CACHE_SIZE)
            gaussian_cache.erase(gaussian_cache.begin());

        cv::Mat kernel_y = cv::getGaussianKernel(rows, -1, CV_32F);
        cv::Mat kernel_x = cv::getGaussianKernel(cols, -1, CV_32F);
        cv::Mat window = kernel_y * kernel_x.t();

        double minVal, maxVal;
        cv::minMaxLoc(window, &minVal, &maxVal);
        if (maxVal > NORMALIZATION_EPSILON)
            window *= (1.0 / maxVal);
        else
            window = cv::Mat::zeros(rows, cols, CV_32F);

        return gaussian_cache[key] = std::move(window);
    }

    /**
     * Inisialisasi flow untuk level coarsest (paling kasar)
     */
    static cv::Mat initializeCoarsestFlow(const cv::Mat &ref_layer)
    {
        return cv::Mat::zeros(ref_layer.size(), CV_32FC2);
    }

    /**
     * Upsample flow dari level sebelumnya dengan edge-aware blending
     */
    static inline cv::Mat upsamplingFlow(
        const cv::Mat &previous_level_flow,
        const cv::Mat &ref_layer)
    {
        using namespace ImageAlignmentConfig;

        // --- LANGKAH 1: PRE-PROCESSING GAMBAR PEMANDU (GUIDE IMAGE) ---
        cv::Mat guide_image_8u;
        if (ref_layer.channels() > 1)
        {
            cv::cvtColor(ref_layer, guide_image_8u, cv::COLOR_BGR2GRAY);
        }
        else
        {
            // Konversi langsung, HILANGKAN equalizeHist
            ref_layer.convertTo(guide_image_8u, CV_8U);
        }

        // --- LANGKAH 2: UPSAMPLING KASAR PADA FLOW ---
        std::vector<cv::Mat> flow_channels;
        cv::split(previous_level_flow, flow_channels);

        cv::Mat flow_x_upsampled, flow_y_upsampled;
        // PENGGANTIAN: Gunakan INTER_LINEAR untuk upsampling yang lebih baik daripada NEAREST
        cv::resize(flow_channels[0], flow_x_upsampled, ref_layer.size(), 0, 0, cv::INTER_LINEAR);
        cv::resize(flow_channels[1], flow_y_upsampled, ref_layer.size(), 0, 0, cv::INTER_LINEAR);

        // --- LANGKAH 3: TERAPKAN SMOOTHING CEPAT (Pengganti Guided Filter) ---
        cv::Mat flow_x_smoothed, flow_y_smoothed;
        const int kernel_size = 3;

        // Gunakan Median Blur (cepat dan efektif menghilangkan noise upsampling)
        cv::medianBlur(flow_x_upsampled, flow_x_smoothed, kernel_size);
        cv::medianBlur(flow_y_upsampled, flow_y_smoothed, kernel_size);

        // --- LANGKAH 4 & 5: GABUNGKAN DAN SCALE ---
        std::vector<cv::Mat> smoothed_channels = {flow_x_smoothed, flow_y_smoothed};
        cv::Mat flow_upsampled;
        cv::merge(smoothed_channels, flow_upsampled);

        flow_upsampled *= FLOW_UPSCALE_FACTOR; // Biasanya 2.0

        return flow_upsampled;
    }

    /**
     * Generate kandidat flow untuk tile matching
     */
    static inline void generateCandidateFlows(
        std::vector<cv::Vec2f> &candidate_flows,
        int layer_index,
        int total_layers,
        const cv::Mat &previous_level_flow, // Flow dari level LEBIH KASAR
        const cv::Mat &current_flow,        // Flow dari level sebelumnya, SUDAH DI-UPSAMPLE
        int tile_center_y,
        int tile_center_x,
        int current_tile_h,
        int current_tile_w)
    {
        using namespace ImageAlignmentConfig;

        candidate_flows.clear();
        candidate_flows.reserve(15);

        // === KASUS DASAR: Level paling kasar, hanya ada zero flow ===
        if (layer_index == total_layers - 1)
        {
            candidate_flows.emplace_back(0.0f, 0.0f);
            return;
        }

        // === SUMBER KANDIDAT #1: Metal-Inspired Spatial Correction ===
        {
            // 1a. Kandidat dari tile itu sendiri (tebakan awal terbaik)
            // Menggunakan titik tengah tile
            const cv::Vec2f &center_flow = current_flow.at<cv::Vec2f>(
                tile_center_y + current_tile_h / 2,
                tile_center_x + current_tile_w / 2);
            candidate_flows.push_back(center_flow);

            // 1b. Kandidat dari tetangga horizontal dan vertikal
            const int step_x = std::max(current_tile_w / 2, 1);
            const int step_y = std::max(current_tile_h / 2, 1);
            const int tile_grid_x = tile_center_x / step_x;
            const int tile_grid_y = tile_center_y / step_y;

            int dx_shift = (tile_grid_x % 2 == 0) ? -step_x : step_x;
            int dy_shift = (tile_grid_y % 2 == 0) ? -step_y : dy_shift;

            int h_neighbor_x = tile_center_x + dx_shift;
            int v_neighbor_y = tile_center_y + dy_shift;

            if (h_neighbor_x >= 0 && h_neighbor_x < current_flow.cols)
            {
                candidate_flows.push_back(current_flow.at<cv::Vec2f>(tile_center_y, h_neighbor_x));
            }
            if (v_neighbor_y >= 0 && v_neighbor_y < current_flow.rows)
            {
                candidate_flows.push_back(current_flow.at<cv::Vec2f>(v_neighbor_y, tile_center_x));
            }
        }

        // === SUMBER KANDIDAT #2: Propagasi dari Level Kasar (Optimasi) ===
        // OPTIMASI: Hanya lakukan sampling 1x1 di level kasar, kecuali di level paling kasar kedua (L4)
        {
            const int coarse_y = static_cast<int>((tile_center_y + current_tile_h * 0.5f) * 0.5f);
            const int coarse_x = static_cast<int>((tile_center_x + current_tile_w * 0.5f) * 0.5f);

            const int max_row = previous_level_flow.rows;
            const int max_col = previous_level_flow.cols;

            const cv::Vec2f *flow_ptr = previous_level_flow.ptr<cv::Vec2f>(0);
            const int flow_step = previous_level_flow.cols;

            // Tentukan radius sampling
            // Kita hanya ambil pusat (dr=0, dc=0) untuk menghemat cost,
            // karena kandidat spatial (sumber #1) sudah cukup.
            int dr_max = 0;
            int dc_max = 0;

            // Opsional: Jika Anda hanya ingin 3x3 search di level L4 (paling kasar kedua)
            /*
            if (layer_index == total_layers - 2) {
                dr_max = 1;
                dc_max = 1;
            }
            */

            for (int dr = -dr_max; dr <= dr_max; ++dr)
            {
                const int ny = coarse_y + dr;
                if (ny < 0 || ny >= max_row)
                    continue;

                for (int dc = -dc_max; dc <= dc_max; ++dc)
                {
                    const int nx = coarse_x + dc;
                    if (nx >= 0 && nx < max_col)
                    {
                        const cv::Vec2f &prev_flow = flow_ptr[ny * flow_step + nx];
                        candidate_flows.emplace_back(prev_flow * FLOW_UPSCALE_FACTOR);
                    }
                }
            }
        }

        // === FINALISASI: Deduplikasi dan Fallback ===

        // 1. Hapus kandidat duplikat
        std::sort(candidate_flows.begin(), candidate_flows.end(),
                  [](const cv::Vec2f &a, const cv::Vec2f &b)
                  {
                      if (a[0] != b[0])
                          return a[0] < b[0];
                      return a[1] < b[1];
                  });
        candidate_flows.erase(
            std::unique(candidate_flows.begin(), candidate_flows.end()),
            candidate_flows.end());

        // 2. Fallback
        if (candidate_flows.empty())
        {
            // ... (Logika fallback tetap sama) ...
            const cv::Vec2f center_flow = current_flow.at<cv::Vec2f>(
                tile_center_y + current_tile_h / 2,
                tile_center_x + current_tile_w / 2);

            candidate_flows.emplace_back(center_flow);

            const float cx = center_flow[0];
            const float cy = center_flow[1];

            candidate_flows.emplace_back(cx - 1, cy - 1);
            candidate_flows.emplace_back(cx, cy - 1);
            candidate_flows.emplace_back(cx + 1, cy - 1);
            candidate_flows.emplace_back(cx - 1, cy);
            candidate_flows.emplace_back(cx + 1, cy);
            candidate_flows.emplace_back(cx - 1, cy + 1);
            candidate_flows.emplace_back(cx, cy + 1);
            candidate_flows.emplace_back(cx + 1, cy + 1);
        }
    }

    // --- THREAD-LOCAL BUFFERS (Optimasi Cost Calculation) ---
    // Buffers ini digunakan untuk menyimpan data tile 2D menjadi 1D contiguous.
    // Dideklarasikan static thread_local di namespace helper.
    static thread_local std::vector<float> ref_tile_buffer_g;
    static thread_local std::vector<float> comp_tile_buffer_g;

    /**
     * Helper untuk memuat data tile yang tidak contiguous di Mat ke buffer 1D contiguous.
     * Menggunakan std::memcpy untuk transfer data cepat.
     */
    static inline bool copyTileToContiguousBuffer(
        const cv::Mat &layer, int tile_y, int tile_x, int tile_h, int tile_w,
        std::vector<float> &buffer)
    {
        const int tile_area = tile_h * tile_w;
        if (buffer.size() < tile_area)
        {
            buffer.resize(tile_area);
        }

        int buffer_idx = 0;
        const int step = layer.step1(0); // Stride per baris dalam float

        for (int r = 0; r < tile_h; ++r)
        {
            // Ambil pointer ke awal baris ROI di layer
            const float *p_row = layer.ptr<float>(tile_y + r) + tile_x;

            // Salin satu baris (tile_w elemen) ke buffer
            std::memcpy(buffer.data() + buffer_idx, p_row, tile_w * sizeof(float));
            buffer_idx += tile_w;
        }
        return true;
    }

    // =========================================================================
    // searchCoarseLevelDirect (Optimized)
    // =========================================================================
    static inline void searchCoarseLevelDirect(
        const cv::Mat &ref_layer,
        const cv::Mat &comp_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w,
        const cv::Vec2f &initial_flow,
        float search_dist,
        std::vector<Candidate> &out_candidates)
    {
        // OPTIMASI 1: Menaikkan batas ZMCL dari 64x64 menjadi 128x128
        constexpr int ZMCL_MAX_AREA = 128 * 128;

        out_candidates.clear();

        const int init_dy = static_cast<int>(std::round(initial_flow[1]));
        const int init_dx = static_cast<int>(std::round(initial_flow[0]));

        float flow_mag = std::sqrt(initial_flow[0] * initial_flow[0] +
                                   initial_flow[1] * initial_flow[1]);
        int current_search_dist = static_cast<int>(
            search_dist * (1.0f + 0.5f * std::min(flow_mag / 5.0f, 2.0f)));
        current_search_dist = std::max(1, std::min(current_search_dist, (int)search_dist));

        const float tile_area_inv = 1.0f / static_cast<float>(tile_h * tile_w);
        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;
        const int tile_area = tile_h * tile_w;

        const bool use_zmcl = (tile_area <= ZMCL_MAX_AREA);

        // --- PRE-COPY REFERENCE TILE (Hanya dilakukan sekali di luar loop search) ---
        if (use_zmcl)
        {
            // Salin Reference Tile ke buffer kontigu sekali saja
            copyTileToContiguousBuffer(ref_layer, tile_y, tile_x, tile_h, tile_w, ref_tile_buffer_g);
        }

        for (int dy = -current_search_dist; dy <= current_search_dist; ++dy)
        {
            for (int dx = -current_search_dist; dx <= current_search_dist; ++dx)
            {
                const int test_y = tile_y + init_dy + dy;
                const int test_x = tile_x + init_dx + dx;

                // Batas Cek
                if (test_y < 0 || test_x < 0 ||
                    test_y + tile_h > h_layer ||
                    test_x + tile_w > w_layer)
                    continue;

                float current_cost = 0.0f;

                if (!use_zmcl) // Tile besar: FFT
                {
                    cv::Mat ref_tile(ref_layer, cv::Rect(tile_x, tile_y, tile_w, tile_h));
                    cv::Mat comp_tile(comp_layer, cv::Rect(test_x, test_y, tile_w, tile_h));
                    current_cost = block_cost_fft(ref_tile, comp_tile);
                }
                else // Tile kecil/menengah: ZMCL AVX (OPTIMASI: Panggilan tunggal)
                {
                    // 1. Copy Comparison Tile untuk posisi test (test_x, test_y)
                    copyTileToContiguousBuffer(comp_layer, test_y, test_x, tile_h, tile_w, comp_tile_buffer_g);

                    // 2. Hitung cost AVX sekali jalan
                    current_cost = calculate_fine_analysis(ref_tile_buffer_g.data(),
                                                           comp_tile_buffer_g.data(),
                                                           tile_area);
                }

                Candidate cand{cv::Point2f(init_dx + dx, init_dy + dy),
                               current_cost * tile_area_inv};

                // --- Logika Seleksi Top 5 Kandidat ---
                if (out_candidates.size() < 5)
                {
                    out_candidates.push_back(cand);
                    std::sort(out_candidates.begin(), out_candidates.end(),
                              [](const Candidate &a, const Candidate &b)
                              { return a.cost < b.cost; });
                }
                else if (cand.cost < out_candidates.back().cost)
                {
                    out_candidates.back() = cand;
                    std::sort(out_candidates.begin(), out_candidates.end(),
                              [](const Candidate &a, const Candidate &b)
                              { return a.cost < b.cost; });
                }
            }
        }
    }

    /**
     * Pencarian tile matching untuk level halus (fine) - hanya evaluasi kandidat
     */
    struct FineLevelSearchContext
    {
        std::vector<Candidate> candidates;

        FineLevelSearchContext()
        {
            candidates.reserve(1);
        }

        void reset()
        {
            candidates.clear();
        }
    };

    static inline bool searchFineLevelDirect(
            const cv::Mat &ref_layer,
            const cv::Mat &comp_layer,
            int tile_y, int tile_x,
            int tile_h, int tile_w,
            const cv::Vec2f &initial_flow,
            Candidate &out_candidate,
            std::vector<float>& ref_buf,
            std::vector<float>& comp_buf)
    {
        // Parameter Threshold Adaptive
        constexpr float ADAPTIVE_THRESHOLD = 0.05f; 

        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;
        const int tile_area = tile_h * tile_w;
        // Pre-calculation inverse area untuk normalisasi
        const float tile_area_inv = 1.0f / static_cast<float>(tile_area);

        // 1. Setup Center Point
        const int center_dx = static_cast<int>(std::round(initial_flow[0]));
        const int center_dy = static_cast<int>(std::round(initial_flow[1]));

        // Cek Bounds Awal (Early Exit jika titik awal di luar gambar)
        if (tile_y + center_dy < 0 || tile_x + center_dx < 0 ||
            tile_y + center_dy + tile_h > h_layer ||
            tile_x + center_dx + tile_w > w_layer)
            return false;

        // 2. Load Reference Tile (SEKALI SAJA)
        // Kita menggunakan ZMCL/AVX untuk SEMUA ukuran tile di level ini.
        // Asumsi: calculate_fine_analysis bisa menangani ukuran tile berapapun 
        // selama buffer vector-nya cukup (yang sudah dihandle oleh copyTileToContiguousBuffer).
        copyTileToContiguousBuffer(ref_layer, tile_y, tile_x, tile_h, tile_w, ref_buf);

        // Helper Lambda Ringan
        // Tidak ada lagi percabangan FFT vs ZMCL
        auto evaluate_offset = [&](int dx, int dy, float& cost_out) -> bool {
            const int ty = tile_y + dy;
            const int tx = tile_x + dx;

            // Bounds check per titik
            if (ty < 0 || tx < 0 || ty + tile_h > h_layer || tx + tile_w > w_layer) {
                cost_out = std::numeric_limits<float>::max();
                return false;
            }

            // Copy Comp tile ke buffer & Hitung Cost
            copyTileToContiguousBuffer(comp_layer, ty, tx, tile_h, tile_w, comp_buf);
            cost_out = calculate_fine_analysis(ref_buf.data(), comp_buf.data(), tile_area);
            
            return true;
        };

        // --- PHASE 1: Cek Center ---
        float best_cost = std::numeric_limits<float>::max();
        evaluate_offset(center_dx, center_dy, best_cost);
        
        int best_dx = center_dx;
        int best_dy = center_dy;

        // Normalisasi cost agar thresholding konsisten
        float normalized_current_cost = best_cost * tile_area_inv;

        // --- PHASE 2: Adaptive Correction (Cross Search) ---
        // Hanya dijalankan jika hasil center kurang memuaskan
        if (normalized_current_cost > ADAPTIVE_THRESHOLD)
        {
            // Pola Cross (Atas, Bawah, Kiri, Kanan)
            const int neighbors[4][2] = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

            // Loop unrolling hint untuk compiler (opsional, tapi bagus)
            #pragma unroll
            for (int i = 0; i < 4; ++i) {
                int check_dx = center_dx + neighbors[i][0];
                int check_dy = center_dy + neighbors[i][1];
                float neighbor_cost;

                // Evaluasi tetangga
                if (evaluate_offset(check_dx, check_dy, neighbor_cost)) {
                    if (neighbor_cost < best_cost) {
                        best_cost = neighbor_cost;
                        best_dx = check_dx;
                        best_dy = check_dy;
                    }
                }
            }
        }

        // Output Result
        out_candidate.flow = cv::Point2f(static_cast<float>(best_dx), static_cast<float>(best_dy));
        out_candidate.cost = best_cost * tile_area_inv; 
        
        return true;
    }

    static inline cv::Point2f selectBestCandidate(
        const std::vector<Candidate> &candidates,
        const cv::Mat &guide_flow, // Ganti nama biar jelas (ini upsampled flow)
        const cv::Mat &ref_layer,  // Parameter ini jadi TIDAK DIPAKAI (Hapus Sobel)
        int tile_y, int tile_x,
        int tile_h, int tile_w)
    {
        // 1. Early Exit
        if (candidates.empty()) return cv::Point2f(0, 0);

        // Ambil kandidat terbaik secara visual (Cost terendah)
        const float best_appearance_cost = candidates.front().cost;
        const cv::Point2f best_appearance_flow = candidates.front().flow;

        // --- 2. Analisis Tetangga (Neighborhood Statistics) ---
        // Kita mengambil info dari 'guide_flow' (flow level sebelumnya yg di-upscale)
        // karena flow level sekarang belum fully compute.
        
        cv::Vec2f sum_neigh(0.0f, 0.0f);
        float sum_sq_diff = 0.0f;
        int neighbor_count = 0;

        const int max_row = guide_flow.rows;
        const int max_col = guide_flow.cols;
        
        // Pointer access langsung ke baris yang relevan untuk kecepatan
        // Kita hanya cek 3 baris: y-1, y, y+1
        for (int dy = -1; dy <= 1; ++dy)
        {
            const int ny = tile_y + dy;
            if (ny < 0 || ny >= max_row) continue;

            const cv::Vec2f* row_ptr = guide_flow.ptr<cv::Vec2f>(ny);
            
            for (int dx = -1; dx <= 1; ++dx)
            {
                if (dy == 0 && dx == 0) continue; // Skip center

                const int nx = tile_x + dx;
                if (nx >= 0 && nx < max_col)
                {
                    const cv::Vec2f& f = row_ptr[nx];
                    sum_neigh += f;
                    // Untuk varian kasar, kita hitung selisih dari center sementara
                    // (Nanti dikoreksi, tapi untuk speed ini cukup akurat)
                    float dist_sq = (f[0] - best_appearance_flow.x)*(f[0] - best_appearance_flow.x) + 
                                    (f[1] - best_appearance_flow.y)*(f[1] - best_appearance_flow.y);
                    sum_sq_diff += dist_sq;
                    
                    neighbor_count++;
                }
            }
        }

        // Jika tidak ada tetangga valid, kembalikan best appearance
        if (neighbor_count == 0) return best_appearance_flow;

        const float inv_count = 1.0f / static_cast<float>(neighbor_count);
        const cv::Vec2f avg_neigh = sum_neigh * inv_count;
        const float avg_x = avg_neigh[0];
        const float avg_y = avg_neigh[1];

        // --- 3. Hitung Lambda (Weight) secara Ringan ---
        // Kita ganti logika Sobel+Exp dengan logika Linear sederhana.
        
        // Logika: Semakin besar variance tetangga, semakin kita JANGAN percaya tetangga (Lambda kecil).
        // Semakin jelek cost appearance (nilai besar), semakin kita BUTUH tetangga (Lambda besar).
        
        float variance = sum_sq_diff * inv_count;
        
        // Base lambda
        float lambda = 1.5f;

        // Penalties (Pengganti Exp)
        // Jika varian tetangga tinggi (> 5.0), kurangi lambda (jangan terlalu dipaksa ikut tetangga yang galau)
        if (variance > 5.0f) lambda *= 0.5f;
        else if (variance < 0.5f) lambda *= 1.5f; // Tetangga sangat sepakat, ikuti mereka

        // Confidence Boost (Pengganti Sobel/Texture analysis)
        // Jika cost appearance sangat kecil (match bagus), kurangi pengaruh spatial
        if (best_appearance_cost < 0.01f) {
            lambda *= 0.1f; // Sangat percaya appearance
        } 
        else if (best_appearance_cost > 0.1f) {
            lambda *= 3.0f; // Appearance ragu, paksa ikut tetangga
        }

        // --- 4. Seleksi Kandidat (Squared Distance - Tanpa Sqrt) ---
        float min_total_cost = std::numeric_limits<float>::max();
        cv::Point2f chosen_flow = best_appearance_flow;

        // Pre-calcs
        const float spatial_weight = lambda; 

        for (const auto &cand : candidates)
        {
            // Squared Euclidean Distance (L2^2) -> Jauh lebih cepat dari sqrt(L2)
            const float dx = cand.flow.x - avg_x;
            const float dy = cand.flow.y - avg_y;
            const float spatial_dist_sq = dx*dx + dy*dy;

            // Total Cost = Appearance + Lambda * Spatial_Squared
            // Catatan: Karena kita pakai dist squared, nilai spatial akan membesar kuadratik.
            // Tapi karena ini hanya seleksi relatif, urutannya tetap valid.
            const float total_cost = cand.cost + (spatial_weight * spatial_dist_sq * 0.1f); // 0.1f scaling factor untuk imbangi squared

            if (total_cost < min_total_cost)
            {
                min_total_cost = total_cost;
                chosen_flow = cand.flow;
            }
        }

        return chosen_flow;
    }

    /**
     * Apply RANSAC untuk outlier removal pada level kasar
     */
    static void RANSACOutlierRemoval(
        cv::Mat &flow,
        int layer_index,
        int total_layers)
    {
        if (layer_index < static_cast<int>(total_layers) - 1)
            return;

        static thread_local std::vector<cv::Point2f> flow_vectors;
        flow_vectors.clear();
        flow_vectors.reserve(flow.total() / 4);

        const float min_magnitude = std::max(0.1f,
                                             static_cast<float>(std::min(flow.rows, flow.cols)) * 0.001f);

        // Collect valid flow vectors
        for (int r = 0; r < flow.rows; ++r)
        {
            const cv::Vec2f *row_ptr = flow.ptr<cv::Vec2f>(r);
            for (int c = 0; c < flow.cols; ++c)
            {
                const cv::Vec2f &vec = row_ptr[c];
                if (cv::norm(vec) > min_magnitude)
                    flow_vectors.emplace_back(vec[0], vec[1]);
            }
        }

        if (flow_vectors.size() <= 12)
            return;

        // RANSAC parameters
        const float distance_threshold = 1.2f;
        const int min_inliers_needed = static_cast<int>(flow_vectors.size() * 0.5);
        const int max_iterations = std::min(100, static_cast<int>(flow_vectors.size()));
        const int early_stop_threshold = static_cast<int>(flow_vectors.size() * 0.8);

        cv::Vec2f best_global_flow(0, 0);
        int max_inliers = 0;

        // RANSAC iterations
        for (int iter = 0; iter < max_iterations && max_inliers < early_stop_threshold; ++iter)
        {
            const int rand_idx = cv::theRNG().uniform(0, static_cast<int>(flow_vectors.size()));
            const cv::Point2f &hypothesis_flow = flow_vectors[rand_idx];

            int current_inliers = 0;
            cv::Vec2f inlier_sum(0, 0);

            for (const auto &vec : flow_vectors)
            {
                if (cv::norm(vec - hypothesis_flow) < distance_threshold)
                {
                    current_inliers++;
                    inlier_sum[0] += vec.x;
                    inlier_sum[1] += vec.y;
                }
            }

            if (current_inliers > max_inliers)
            {
                max_inliers = current_inliers;
                best_global_flow = inlier_sum / static_cast<float>(current_inliers);
            }
        }

        if (max_inliers > min_inliers_needed)
            flow.setTo(cv::Scalar(best_global_flow[0], best_global_flow[1]));
    }

    static inline float calculateCostAtIntegerPos(
        const std::vector<float>& ref_tile_buffer, // Buffer Ref yang SUDAH diisi
        const cv::Mat& comp_layer,
        int test_y, int test_x,
        int tile_h, int tile_w,
        std::vector<float>& comp_tile_buffer     // Buffer Comp untuk diisi ulang
    )
    {
        // Cek batas gambar
        if (test_y < 0 || test_x < 0 || 
            test_y + tile_h > comp_layer.rows || 
            test_x + tile_w > comp_layer.cols)
        {
            return std::numeric_limits<float>::max();
        }

        // Salin Comparison Tile ke buffer kontigu
        // HANYA ini yang perlu dilakukan berulang per lokasi pencarian
        AlignmentFlowHelpers::copyTileToContiguousBuffer(comp_layer, test_y, test_x, tile_h, tile_w, comp_tile_buffer);

        // Hitung Cost (AVX ZMCL)
        return calculate_fine_analysis(ref_tile_buffer.data(), comp_tile_buffer.data(), tile_h * tile_w);
    }

    /**
     * Proses tile matching untuk satu layer
     * OPTIMIZED FINEST LAYER:
     * - Tidak ada Subpixel Refinement (Berat) di layer halus.
     * - Menggunakan "Smart Selection": Memilih antara mempertahankan presisi float dari layer kasar
     *   atau pindah ke grid integer baru jika ditemukan match yang lebih baik.
     */
    static cv::Mat processSingleLayer(
        const cv::Mat &ref_layer,
        const cv::Mat &comp_layer,
        const cv::Mat &previous_level_flow,
        int layer_index,
        int total_layers,
        int tile_h, 
        int tile_w, 
        float search_dist)
    {
        using namespace ImageAlignmentConfig;

        const bool is_coarsest_layer = (layer_index == total_layers - 1);
        const bool is_finest_layer   = (layer_index == 0);                
        const bool is_adaptive_mode  = (layer_index > 0); 

        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;

        cv::Mat flow;

        // --- 1. Inisialisasi Flow (Sama seperti sebelumnya) ---
        if (is_coarsest_layer) flow = initializeCoarsestFlow(ref_layer);
        else flow = upsamplingFlow(previous_level_flow, ref_layer);

        // --- 2. Konfigurasi Tile Size & Search Distance ---
        int current_tile_h, current_tile_w;
        float current_layer_search_dist;

        // LOGIKA BARU:
        // Semua layer sekarang mencoba menggunakan ukuran tile input (tile_h, tile_w).
        // Kita menggunakan std::min(..., h_layer) agar jika layer sangat kecil (coarsest),
        // ukuran tile otomatis mengecil menyesuaikan ukuran layer tsb.
        
        current_tile_h = std::max(MIN_TILE_SIZE, std::min(tile_h, h_layer));
        current_tile_w = std::max(MIN_TILE_SIZE, std::min(tile_w, w_layer));

        if (is_finest_layer) 
        {
            // Layer paling halus: Search distance sempit (verifikasi 1x1)
            current_layer_search_dist = 1.0f; 
        }
        else 
        {
            // Coarsest & Adaptive Layer: Search distance penuh
            // Baik level paling atas maupun tengah sekarang pakai tile input
            current_layer_search_dist = search_dist;
        }

        // Safety check standar
        if (current_tile_h <= 0 || current_tile_w <= 0 || h_layer < current_tile_h || w_layer < current_tile_w)
            return flow;

        const bool use_overlap = is_adaptive_mode; 
        int step_y = use_overlap ? std::max(current_tile_h / 2, 1) : current_tile_h;
        int step_x = use_overlap ? std::max(current_tile_w / 2, 1) : current_tile_w;
        const float tile_area_inv = 1.0f / (float)(current_tile_h * current_tile_w);

        std::vector<std::vector<TileResult>> thread_results(omp_get_max_threads());

#pragma omp parallel
        {
            int thread_id = omp_get_thread_num();

            // Buffer lokal thread untuk menghindari alokasi berulang
            std::vector<cv::Vec2f> temp_initial_flows; 
            temp_initial_flows.reserve(20);
            
            std::vector<Candidate> temp_search_results; 
            temp_search_results.reserve(32);

            // Buffer Pixel (Ref & Comp)
            std::vector<float> local_ref_buffer(current_tile_h * current_tile_w);
            std::vector<float> local_comp_buffer(current_tile_h * current_tile_w);

            // Cache untuk Integer Deduplication di Finest Layer
            // Key: (dy << 16) | dx (asumsi offset tidak > 32rb pixel)
            // Value: Cost
            std::map<uint32_t, float> integer_cost_cache;

#pragma omp for schedule(dynamic)
            for (int y = 0; y <= h_layer - current_tile_h; y += step_y)
            {
                for (int x = 0; x <= w_layer - current_tile_w; x += step_x)
                {
                    temp_initial_flows.clear();
                    temp_search_results.clear();

                    // 1. Generate Candidates
                    generateCandidateFlows(temp_initial_flows, layer_index, total_layers, previous_level_flow, flow, y, x, current_tile_h, current_tile_w);

                    // 2. Evaluasi
                    if (is_finest_layer) 
                    {
                        // === OPTIMASI FINEST LAYER ===
                        
                        // A. Copy Reference Tile SEKALI saja per tile
                        copyTileToContiguousBuffer(ref_layer, y, x, current_tile_h, current_tile_w, local_ref_buffer);
                        
                        integer_cost_cache.clear();

                        for (const auto &initial_vec : temp_initial_flows)
                        {
                            // Rounding ke integer terdekat untuk akses pixel
                            int i_dx = static_cast<int>(std::round(initial_vec[0]));
                            int i_dy = static_cast<int>(std::round(initial_vec[1]));

                            // Buat key unik untuk map (packing 2 int16 ke int32)
                            // Offset flow relatif kecil, jadi aman di cast ke short
                            uint32_t key = (static_cast<uint16_t>(i_dy) << 16) | static_cast<uint16_t>(i_dx);

                            float cost;
                            auto it = integer_cost_cache.find(key);

                            if (it != integer_cost_cache.end()) {
                                // Cache Hit: Gunakan cost yang sudah dihitung untuk koordinat ini
                                cost = it->second;
                            } else {
                                // Cache Miss: Hitung cost (Heavy AVX Op)
                                int test_y = y + i_dy;
                                int test_x = x + i_dx;

                                cost = calculateCostAtIntegerPos(
                                    local_ref_buffer, comp_layer, 
                                    test_y, test_x, 
                                    current_tile_h, current_tile_w, 
                                    local_comp_buffer
                                );
                                
                                // Normalisasi cost
                                if (cost != std::numeric_limits<float>::max()) {
                                    cost *= tile_area_inv;
                                }
                                
                                integer_cost_cache[key] = cost;
                            }

                            // Simpan kandidat. Perhatikan: Flow tetap menggunakan 'initial_vec' (float)
                            // meskipun cost dihitung berdasarkan posisi integer terdekat.
                            // Ini memungkinkan kita mempertahankan presisi subpixel "tebakan" jika cost-nya bagus.
                            if (cost != std::numeric_limits<float>::max()) {
                                Candidate cand;
                                cand.flow = initial_vec; // Tetap simpan float
                                cand.cost = cost;
                                temp_search_results.push_back(cand);
                            }
                        }
                    }
                    else
                    {
                        // === SCALE 2 & 3: COARSE SEARCH ===
                        for (const auto &initial_vec : temp_initial_flows)
                        {
                            searchCoarseLevelDirect(ref_layer, comp_layer, y, x, current_tile_h, current_tile_w, initial_vec, current_layer_search_dist, temp_search_results);
                        }
                    }

                    // 3. Pilih kandidat terbaik
                    cv::Point2f chosen_flow;
                    if (!temp_search_results.empty())
                    {
                        // Urutkan parsial untuk mendapatkan top candidates
                        size_t keep_count = std::min(temp_search_results.size(), (size_t)5);
                        std::partial_sort(temp_search_results.begin(), temp_search_results.begin() + keep_count, temp_search_results.end(),
                             [](const Candidate &a, const Candidate &b) { return a.cost < b.cost; });
                        
                        temp_search_results.resize(keep_count);

                        chosen_flow = selectBestCandidate(
                            temp_search_results, flow, ref_layer, y, x, current_tile_h, current_tile_w);
                    }
                    else
                    {
                        chosen_flow = flow.at<cv::Point2f>(y, x);
                    }

                    // 4. Final Flow Assignment
                    // Untuk finest layer, kita bypass subpixel refinement berat untuk performa
                    cv::Point2f final_flow;
                    if (is_finest_layer) {
                        final_flow = chosen_flow;
                    } else {
                        final_flow = subpixel_refinement(
                            ref_layer, comp_layer, x, y,
                            (int)std::round(chosen_flow.x), (int)std::round(chosen_flow.y),
                            current_tile_w, current_tile_h
                        );
                    }

                    thread_results[thread_id].push_back({cv::Rect(x, y, current_tile_w, current_tile_h), final_flow});
                }
            }
        } // End Parallel

        // === REDUCE PHASE ===
        
        cv::Mat flow_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
        cv::Mat weight_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);

        for (const auto &results_from_one_thread : thread_results)
        {
            for (const auto &result : results_from_one_thread)
            {
                const cv::Rect &tile_roi = result.roi;
                const cv::Point2f &result_flow = result.flow;

                cv::Mat weights;
                if (use_overlap)
                    weights = getGaussianWindow(tile_roi.height, tile_roi.width);
                else
                    weights = cv::Mat::ones(tile_roi.height, tile_roi.width, CV_32F);

                const float *weight_data = weights.ptr<float>(0);

                for (int r = 0; r < tile_roi.height; ++r)
                {
                    cv::Vec2f *p_flow_start = flow_accumulator.ptr<cv::Vec2f>(tile_roi.y + r) + tile_roi.x;
                    float *p_weight_start = weight_accumulator.ptr<float>(tile_roi.y + r) + tile_roi.x;
                    const float *p_weights_row = weight_data + r * tile_roi.width;

#pragma omp simd
                    for (int c = 0; c < tile_roi.width; ++c)
                    {
                        const float w = p_weights_row[c];
                        p_flow_start[c][0] += result_flow.x * w;
                        p_flow_start[c][1] += result_flow.y * w;
                        p_weight_start[c] += w;
                    }
                }
            }
        }

        cv::Vec2f *flow_ptr = flow_accumulator.ptr<cv::Vec2f>(0);
        float *weight_ptr = weight_accumulator.ptr<float>(0);
        const int total_pixels = h_layer * w_layer;

#pragma omp parallel for simd
        for (int p = 0; p < total_pixels; ++p)
        {
            if (weight_ptr[p] > NORMALIZATION_EPSILON)
            {
                const float inv_weight = 1.0f / weight_ptr[p];
                flow_ptr[p][0] *= inv_weight;
                flow_ptr[p][1] *= inv_weight;
            }
            else
            {
                flow_ptr[p][0] = 0.0f;
                flow_ptr[p][1] = 0.0f;
            }
        }

        flow = flow_accumulator;

        // --- FINAL FILTERS ---
        if (layer_index > 0)
        {
            cv::medianBlur(flow, flow, 5);
        }

        if (is_coarsest_layer)
        {
            RANSACOutlierRemoval(flow, layer_index, total_layers);
        }

        return flow;
    }
}

// =========================================================================
// === FUNGSI UTAMA DENGAN REFACTORED CODE ===
// =========================================================================

extern "C"
{
    ALIGNMENT_API float *compute_alignment_flow(
        const float *ref_work_data, const float *current_work_data,
        int work_h, int work_w, int tile_h, int tile_w, int n_layers, float search_dist)
    {
        // SimpleTimer overall_timer("TOTAL FLOW COMPUTATION");
        // n_layers = 3; 
        using namespace ImageAlignmentConfig;

        // =========================================================================
        // === BAGIAN A: Pra-pemrosesan dan Setup (OPTIMIZED)                   ===
        // =========================================================================
        cv::Mat ref_work(work_h, work_w, CV_32FC1, const_cast<float *>(ref_work_data));
        cv::Mat current_work(work_h, work_w, CV_32FC1, const_cast<float *>(current_work_data));

        // =========================================================================
        // === BAGIAN B: Pembangunan Piramida Gambar (OPTIMIZED)                ===
        // =========================================================================

        std::vector<cv::Mat> ref_pyramid, current_pyramid;
        {
            // SimpleTimer pyramid_timer("Pyramid Generation"); // Opsional
            ref_pyramid.reserve(n_layers);
            current_pyramid.reserve(n_layers);

            ref_pyramid.push_back(ref_work);
            current_pyramid.push_back(current_work);

            for (int i = 0; i < n_layers - 1; ++i)
            {
                // 1. Buat Mat kosong sebagai tujuan. Ini tidak mengalokasikan buffer data.
                cv::Mat next_ref, next_current;

                // 2. panggil pyrDown. Karena 'next_ref' ukurannya tidak pas,
                cv::pyrDown(ref_pyramid.back(), next_ref);
                cv::pyrDown(current_pyramid.back(), next_current);

                // 3. Lakukan pengecekan ukuran
                if (next_ref.rows < MIN_PYRAMID_LAYER_SIZE || next_ref.cols < MIN_PYRAMID_LAYER_SIZE)
                    break;

                // 4. Pindahkan (move) Mat beserta buffer datanya ke dalam vector.
                ref_pyramid.push_back(std::move(next_ref));
                current_pyramid.push_back(std::move(next_current));
            }
        }

        // === BAGIAN C: Perhitungan Optical Flow (Coarse-to-Fine) ===
        cv::Mat flow;
        cv::Mat previous_level_flow;

        {
            // SimpleTimer flow_levels_timer("Coarse-to-Fine Flow Processing");

            for (int i = static_cast<int>(ref_pyramid.size()) - 1; i >= 0; --i)
            {
                const cv::Mat &ref_layer = ref_pyramid[i];
                const cv::Mat &comp_layer = current_pyramid[i];

                cv::Mat current_flow = AlignmentFlowHelpers::processSingleLayer(
                    ref_layer,
                    comp_layer,
                    previous_level_flow,
                    i,
                    static_cast<int>(ref_pyramid.size()),
                    tile_h,
                    tile_w,
                    search_dist);

                previous_level_flow = std::move(current_flow);
                flow = cv::Mat();
            }
        }

        flow = std::move(previous_level_flow);

        // === BAGIAN D: Finalisasi dan Pengembalian Data ===
        float *output_flow_data = nullptr;
        {
            // SimpleTimer finalization_timer("Finalization & Data Copy");
            if (!flow.empty())
            {
                if (!flow.isContinuous())
                    flow = flow.clone();

                const size_t data_size = flow.total() * flow.elemSize();
                output_flow_data = static_cast<float *>(malloc(data_size));
                if (output_flow_data)
                    std::memcpy(output_flow_data, flow.data, data_size);
            }
        }

        return output_flow_data;
    }

    ALIGNMENT_API void free_flow_memory(float *flow_data)
    {
        if (flow_data)
            free(flow_data);
    }
}