#include "alignment_tile.h"
#include <opencv2/imgproc.hpp>
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

#include "refinement.hpp"

// =========================================================================
// === PROFILING UTILS ===
// =========================================================================
struct SimpleTimer {
    std::string name;
    std::chrono::high_resolution_clock::time_point start;
    SimpleTimer(const std::string& n) : name(n), start(std::chrono::high_resolution_clock::now()) {}
    ~SimpleTimer() {
        auto end = std::chrono::high_resolution_clock::now();
        std::chrono::duration<double, std::milli> elapsed = end - start;
        std::cout << "[C++ Timer] " << name << ": " << elapsed.count() << " ms" << std::endl;
    }
};

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

        cv::Mat flow_upsampled;
        // OPTIMIZATION: Use INTER_LINEAR directly on CV_32FC2.
        // This provides smoothed upsampling in a single pass, 
        // avoiding the need for manual split/boxFilter/merge.
        cv::resize(previous_level_flow, flow_upsampled, ref_layer.size(), 0, 0, cv::INTER_LINEAR);

        // Scale flow vectors by the upscale factor
        flow_upsampled *= FLOW_UPSCALE_FACTOR; // 2.0f

        return flow_upsampled;
    }

    /**
     * Generate kandidat flow untuk tile matching
     */
    static inline void generateCandidateFlows(
        std::vector<cv::Vec2f> &candidate_flows,
        int layer_index,
        int total_layers,
        const cv::Mat &previous_level_flow, // Flow level kasar (belum di-upsample)
        const cv::Mat &current_flow,        // Flow level ini (hasil upsample)
        int tile_center_y,
        int tile_center_x,
        int current_tile_h,
        int current_tile_w)
    {
        using namespace ImageAlignmentConfig;

        candidate_flows.clear();
        // Kita batasi kapasitas karena kita hanya ambil kandidat paling relevan
        candidate_flows.reserve(8);

        // --- KASUS DASAR: Level paling kasar ---
        if (layer_index == total_layers - 1)
        {
            candidate_flows.emplace_back(0.0f, 0.0f);
            return;
        }

        // --- 1. PRIMARY CANDIDATE: Inherited Flow (Tebakan dari level sebelumnya) ---
        // Ini adalah kandidat terkuat.
        const cv::Vec2f &center_flow = current_flow.at<cv::Vec2f>(
            tile_center_y + current_tile_h / 2,
            tile_center_x + current_tile_w / 2);
        candidate_flows.push_back(center_flow);

        // --- 2. SPATIAL CANDIDATES (Tetangga) ---
        // OPTIMASI: Hanya cek tetangga Kiri dan Atas.
        // Alasan: Data tetangga ini biasanya sudah selesai diproses (kausalitas) 
        // dan cukup untuk menangani pergerakan objek yang konsisten.
        
        // Jarak cek tetangga (gunakan ukuran tile penuh karena non-overlap)
        const int step_x = current_tile_w;
        const int step_y = current_tile_h;

        // Cek Tetangga Kiri
        int h_neighbor_x = tile_center_x - step_x;
        if (h_neighbor_x >= 0)
        {
            candidate_flows.push_back(current_flow.at<cv::Vec2f>(tile_center_y, h_neighbor_x));
        }

        // Cek Tetangga Atas
        int v_neighbor_y = tile_center_y - step_y;
        if (v_neighbor_y >= 0)
        {
            candidate_flows.push_back(current_flow.at<cv::Vec2f>(v_neighbor_y, tile_center_x));
        }

        // --- 3. COARSE PROJECTION (Backup) ---
        // Mengambil langsung dari raw previous level flow (jika ragu dengan hasil upsampling)
        // Hanya dilakukan jika bukan di level paling halus untuk menghemat akses memori
        if (layer_index > 0) 
        {
            // Mapping koordinat ke level kasar (koordinat / 2)
            const int coarse_y = (tile_center_y + current_tile_h / 2) / 2;
            const int coarse_x = (tile_center_x + current_tile_w / 2) / 2;

            if (coarse_y >= 0 && coarse_y < previous_level_flow.rows &&
                coarse_x >= 0 && coarse_x < previous_level_flow.cols)
            {
                // Jangan lupa dikali faktor upscale (biasanya 2.0)
                candidate_flows.emplace_back(previous_level_flow.at<cv::Vec2f>(coarse_y, coarse_x) * FLOW_UPSCALE_FACTOR);
            }
        }

        // --- 4. Fallback (Jika kosong) ---
        if (candidate_flows.empty())
        {
            candidate_flows.push_back(center_flow);
        }

        // Deduplikasi sederhana (menghapus elemen berurutan yang sama)
        // Tidak perlu sort mahal karena jumlah elemen sangat sedikit (< 6)
        // Kita biarkan saja sedikit duplikasi demi kecepatan CPU, 
        // karena cost calculation cache nanti akan menangani duplikasi integer.
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
        constexpr float REFINEMENT_QUALITY_THRESHOLD = 0.01f; // Cost threshold untuk apply refinement
        constexpr float MIN_COST_RANGE = 0.001f;  // Minimum cost range untuk meaningful parabolic fit

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

        // --- PHASE 1: Collect 9-point costs untuk cache-based parabolic refinement ---
        // Array untuk menyimpan 9 costs dalam layout row-major:
        // [-1,-1] [0,-1] [1,-1]
        // [-1, 0] [0, 0] [1, 0]
        // [-1, 1] [0, 1] [1, 1]
        float costs_3x3[9];
        int cost_idx = 0;
        float best_cost = std::numeric_limits<float>::max();
        int best_dx = center_dx;
        int best_dy = center_dy;

        for (int ddy = -1; ddy <= 1; ++ddy)
        {
            for (int ddx = -1; ddx <= 1; ++ddx)
            {
                int check_dx = center_dx + ddx;
                int check_dy = center_dy + ddy;
                float neighbor_cost;

                if (evaluate_offset(check_dx, check_dy, neighbor_cost)) {
                    costs_3x3[cost_idx] = neighbor_cost * tile_area_inv;
                    
                    if (neighbor_cost < best_cost) {
                        best_cost = neighbor_cost;
                        best_dx = check_dx;
                        best_dy = check_dy;
                    }
                } else {
                    costs_3x3[cost_idx] = std::numeric_limits<float>::max();
                }
                cost_idx++;
            }
        }

        const float center_cost = costs_3x3[4]; // [0,0]
        const float normalized_center_cost = center_cost;

        // --- PHASE 2: Conditional Cache-Based Parabolic Refinement ---
        // Hanya apply jika: ada room untuk improvement dan ada signal yang cukup
        cv::Point2f final_flow = cv::Point2f(static_cast<float>(best_dx), static_cast<float>(best_dy));

        // Count valid costs dan hitung cost range
        float cost_min = std::numeric_limits<float>::max();
        float cost_max = -std::numeric_limits<float>::max();
        int valid_costs = 0;

        for (int i = 0; i < 9; ++i) {
            if (costs_3x3[i] != std::numeric_limits<float>::max()) {
                cost_min = std::min(cost_min, costs_3x3[i]);
                cost_max = std::max(cost_max, costs_3x3[i]);
                valid_costs++;
            }
        }

        float cost_range = cost_max - cost_min;

        // --- LIGHTWEIGHT OUTLIER FILTERING ---
        // Calculate mean & std dari valid costs
        float cost_sum = 0.0f;
        for (int i = 0; i < 9; ++i) {
            if (costs_3x3[i] != std::numeric_limits<float>::max()) {
                cost_sum += costs_3x3[i];
            }
        }
        float cost_mean = (valid_costs > 0) ? cost_sum / valid_costs : 0.0f;

        // Calculate standard deviation
        float cost_sq_sum = 0.0f;
        for (int i = 0; i < 9; ++i) {
            if (costs_3x3[i] != std::numeric_limits<float>::max()) {
                float diff = costs_3x3[i] - cost_mean;
                cost_sq_sum += diff * diff;
            }
        }
        float cost_std = (valid_costs > 1) ? std::sqrt(cost_sq_sum / (valid_costs - 1)) : 0.0f;

        // Mark extreme outliers sebagai invalid (> mean + 2*sigma)
        float outlier_threshold = cost_mean + 2.0f * cost_std;
        int filtered_valid_costs = 0;
        for (int i = 0; i < 9; ++i) {
            if (costs_3x3[i] != std::numeric_limits<float>::max() && costs_3x3[i] > outlier_threshold) {
                costs_3x3[i] = std::numeric_limits<float>::max();
            } else if (costs_3x3[i] != std::numeric_limits<float>::max()) {
                filtered_valid_costs++;
            }
        }

        // Refinement condition: 
        // 1. Sufficient valid costs untuk parabolic fit (after filtering)
        // 2. Center cost > threshold (ada room untuk improvement)
        // 3. Sufficient cost range (signal yang jelas)
        if (filtered_valid_costs >= 5 && normalized_center_cost > REFINEMENT_QUALITY_THRESHOLD && cost_range > MIN_COST_RANGE)
        {
            // Parabolic fitting using CACHED costs (no new function calls!)
            float left_cost = costs_3x3[3];   // [-1,0]
            float right_cost = costs_3x3[5];  // [1,0]
            float top_cost = costs_3x3[1];    // [0,-1]
            float bottom_cost = costs_3x3[7]; // [0,1]

            // Only proceed if cardinal neighbors are valid (not filtered as outliers)
            if (left_cost != std::numeric_limits<float>::max() && 
                right_cost != std::numeric_limits<float>::max() &&
                top_cost != std::numeric_limits<float>::max() && 
                bottom_cost != std::numeric_limits<float>::max())
            {
                // X-direction parabolic fit (gunakan left, center, right)
                float delta_x = 0.0f;
                {
                    float c_coeff = (right_cost + left_cost - 2.0f * center_cost) / 2.0f;
                    if (std::fabs(c_coeff) > 1e-6f) {
                        float b_coeff = (right_cost - left_cost) / 2.0f;
                        delta_x = -b_coeff / (2.0f * c_coeff);
                        // Clamp untuk mencegah outlier
                        delta_x = std::max(-0.5f, std::min(0.5f, delta_x));
                    }
                }

                // Y-direction parabolic fit (gunakan top, center, bottom)
                float delta_y = 0.0f;
                {
                    float c_coeff = (bottom_cost + top_cost - 2.0f * center_cost) / 2.0f;
                    if (std::fabs(c_coeff) > 1e-6f) {
                        float b_coeff = (bottom_cost - top_cost) / 2.0f;
                        delta_y = -b_coeff / (2.0f * c_coeff);
                        // Clamp untuk mencegah outlier
                        delta_y = std::max(-0.5f, std::min(0.5f, delta_y));
                    }
                }

                // Apply refined offset
                final_flow = cv::Point2f(
                    static_cast<float>(best_dx) + delta_x,
                    static_cast<float>(best_dy) + delta_y
                );
            }
        }

        // Output Result
        out_candidate.flow = final_flow;
        out_candidate.cost = best_cost * tile_area_inv; 
        
        return true;
    }

    static inline cv::Point2f selectBestCandidate(
        const std::vector<Candidate> &candidates,
        const cv::Mat &guide_flow, // Ganti nama biar jelas (ini upsampled flow)
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

        const float min_magnitude_for_ransac = std::max(0.2f,
                                                        static_cast<float>(std::min(flow.rows, flow.cols)) * 0.002f); // Increased min_magnitude

        // Collect valid flow vectors and calculate their magnitudes
        std::vector<float> magnitudes;
        for (int r = 0; r < flow.rows; ++r)
        {
            const cv::Vec2f *row_ptr = flow.ptr<cv::Vec2f>(r);
            for (int c = 0; c < flow.cols; ++c)
            {
                const cv::Vec2f &vec = row_ptr[c];
                float mag = cv::norm(vec);
                if (mag > min_magnitude_for_ransac)
                {
                    flow_vectors.emplace_back(vec[0], vec[1]);
                    magnitudes.push_back(mag);
                }
            }
        }

        if (flow_vectors.size() <= 12)
            return;

        // Calculate adaptive distance_threshold
        std::sort(magnitudes.begin(), magnitudes.end());
        float median_magnitude = magnitudes[magnitudes.size() / 2];
        const float distance_threshold = std::max(1.0f, median_magnitude * 0.2f); // 20% of median magnitude, min 1.0f

        // RANSAC parameters
        const int min_inliers_needed = static_cast<int>(flow_vectors.size() * 0.5);
        const int max_iterations = std::min(100, static_cast<int>(flow_vectors.size()));
        const int early_stop_threshold = static_cast<int>(flow_vectors.size() * 0.8);

        cv::Vec2f best_global_flow(0, 0);
        int max_inliers = 0;

        // RANSAC iterations
        for (int iter = 0; iter < max_iterations && max_inliers < early_stop_threshold; ++iter)
        {
            const int rand_idx = cv::theRNG().uniform(0, static_cast<int>(flow_vectors.size()));
            const cv::Point2f hypothesis_flow = flow_vectors[rand_idx];

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

    /**
     * Spatial/Local RANSAC untuk final flow post-processing (OPTIMIZED)
     * Adaptive window processing dengan early termination untuk low-variance regions
     */
    static void spatialLocalRANSACCleanup(
        cv::Mat &flow,
        int window_size = 64,           // Adaptive window size
        float overlap_ratio = 0.0f)     // OPTIMIZATION: Zero overlap removes blending overhead
    {
        if (flow.empty() || flow.type() != CV_32FC2)
            return;

        const int h = flow.rows;
        const int w = flow.cols;
        
        // Jika overlap 0, kita gunakan step = window_size (Non-overlapping blocks)
        const int step = (overlap_ratio > 0.0f) ? 
                         static_cast<int>(window_size * (1.0f - overlap_ratio)) : 
                         window_size;

        // --- PHASE 1: PREPARE JOBS ---
        struct WindowJob { int wx, wy; };
        std::vector<WindowJob> jobs;
        jobs.reserve((h / step + 1) * (w / step + 1));

        for (int wy = 0; wy <= h - window_size; wy += step) {
            for (int wx = 0; wx <= w - window_size; wx += step) {
                jobs.push_back({wx, wy});
            }
        }

        #pragma omp parallel
        {
            // Thread-local buffers
            const int max_pixels = window_size * window_size;
            std::vector<float> magnitudes_buffer;
            magnitudes_buffer.reserve(max_pixels / 4); // Subsampled
            
            std::vector<cv::Point2f> flow_vectors;
            flow_vectors.reserve(max_pixels / 4); // Subsampled

            #pragma omp for schedule(dynamic)
            for (int i = 0; i < (int)jobs.size(); ++i) {
                const int wx = jobs[i].wx;
                const int wy = jobs[i].wy;
                
                cv::Rect window_roi(wx, wy, window_size, window_size);
                cv::Mat window_flow = flow(window_roi);

                // --- 1. Quick Variance check (Subsampled) ---
                magnitudes_buffer.clear();
                float mag_sum = 0.0f;
                for (int r = 0; r < window_size; r += 2) {
                    const cv::Vec2f* row_ptr = window_flow.ptr<cv::Vec2f>(r);
                    for (int c = 0; c < window_size; c += 2) {
                        const cv::Vec2f& f = row_ptr[c];
                        float mag = std::sqrt(f[0]*f[0] + f[1]*f[1]); 
                        magnitudes_buffer.push_back(mag);
                        mag_sum += mag;
                    }
                }

                float mag_mean = mag_sum / magnitudes_buffer.size();
                float mag_variance = 0.0f;
                for (float mag : magnitudes_buffer) {
                    float diff = mag - mag_mean;
                    mag_variance += diff * diff;
                }
                mag_variance /= magnitudes_buffer.size();

                // Skip RANSAC for low variance (Sangat umum di area statis/langit)
                if (mag_variance < 0.5f) continue; 

                // --- 2. RANSAC ---
                std::nth_element(magnitudes_buffer.begin(), magnitudes_buffer.begin() + magnitudes_buffer.size()/2, magnitudes_buffer.end());
                float median_magnitude = magnitudes_buffer[magnitudes_buffer.size() / 2];
                float distance_threshold = std::max(1.0f, median_magnitude * 0.25f);
                float dist_thresh_sq = distance_threshold * distance_threshold;

                flow_vectors.clear();
                for (int r = 0; r < window_size; r += 2) {
                    const cv::Vec2f* row_ptr = window_flow.ptr<cv::Vec2f>(r);
                    for (int c = 0; c < window_size; c += 2) {
                        const cv::Vec2f& f = row_ptr[c];
                        flow_vectors.emplace_back(f[0], f[1]);
                    }
                }

                cv::Vec2f best_local_flow(0, 0);
                int max_inliers = 0;
                const int num_vectors = (int)flow_vectors.size();
                const int min_inliers_needed = static_cast<int>(num_vectors * 0.4f);
                const int max_iterations = (mag_variance > 5.0f) ? 25 : 12;

                for (int iter = 0; iter < max_iterations && max_inliers < min_inliers_needed; ++iter) {
                    const int rand_idx = cv::theRNG().uniform(0, num_vectors);
                    const cv::Point2f &hypothesis = flow_vectors[rand_idx];

                    int current_inliers = 0;
                    float in_sum_x = 0.0f, in_sum_y = 0.0f;

                    for (const auto &v : flow_vectors) {
                        float dx = v.x - hypothesis.x;
                        float dy = v.y - hypothesis.y;
                        if ((dx*dx + dy*dy) < dist_thresh_sq) {
                            current_inliers++;
                            in_sum_x += v.x; in_sum_y += v.y;
                        }
                    }

                    if (current_inliers > max_inliers) {
                        max_inliers = current_inliers;
                        float inv = 1.0f / (float)current_inliers;
                        best_local_flow = cv::Vec2f(in_sum_x * inv, in_sum_y * inv);
                    }
                }

                // --- 3. Apply Directly (Zero Overlap logic) ---
                if (max_inliers > min_inliers_needed) {
                    for (int r = 0; r < window_size; ++r) {
                        cv::Vec2f* row_ptr = window_flow.ptr<cv::Vec2f>(r);
                        for (int c = 0; c < window_size; ++c) {
                            row_ptr[c] = best_local_flow;
                        }
                    }
                }
            }
        }
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
        float base_search_dist)
    {
        using namespace ImageAlignmentConfig;

        const bool is_coarsest_layer = (layer_index == total_layers - 1);
        const bool is_finest_layer   = (layer_index == 0);                
        
        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;

        // Timer per layer components
        SimpleTimer layer_timer("Layer " + std::to_string(layer_index) + " Processing");

        // --- 1. Inisialisasi Flow ---
        cv::Mat flow;
        {
             // Timer khusus Upsampling
             SimpleTimer upsample_timer("Layer " + std::to_string(layer_index) + " Upsampling");
             if (is_coarsest_layer) flow = AlignmentFlowHelpers::initializeCoarsestFlow(ref_layer);
             else flow = AlignmentFlowHelpers::upsamplingFlow(previous_level_flow, ref_layer);
        }

        // --- 2. Setup Tile Size ---
        // Clamp tile size agar tidak lebih besar dari gambar layer saat ini
        int current_tile_h = std::max(MIN_TILE_SIZE, std::min(tile_h, h_layer));
        int current_tile_w = std::max(MIN_TILE_SIZE, std::min(tile_w, w_layer));

        // --- 3. OPTIMASI STEP (NON-OVERLAP) ---
        // Menggunakan step sebesar ukuran tile. Mengurangi beban komputasi 75%.
        int step_y = current_tile_h;
        int step_x = current_tile_w;

        // --- 4. Adaptive Search Distance ---
        // Layer halus radius kecil, layer kasar radius besar
        float current_layer_search_dist = base_search_dist;
        if (!is_coarsest_layer) {
            // OPTIMASI: Faster decay (2.0 instead of 1.5) untuk mengurangi search area
            current_layer_search_dist = std::max(1.0f, base_search_dist / (2.0f * (total_layers - layer_index)));
        }

        const float tile_area_inv = 1.0f / (float)(current_tile_h * current_tile_w);

        // OPTIMIZATION: DIRECT WRITE (Eliminate Serial Copy Phase)
        // Kita butuh matriks tujuan terpisah agar tidak race condition saat membaca neighbor (flow)
        // Gunakan Zeros (seperti logic original) bukan Clone, untuk hemat bandwidth.
        cv::Mat refined_flow = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);

        {
             SimpleTimer search_timer("Layer " + std::to_string(layer_index) + " Search Phase");
#pragma omp parallel
        {
            // Buffer lokal thread (reusable)
            std::vector<cv::Vec2f> temp_initial_flows; 
            temp_initial_flows.reserve(10);
            
            std::vector<Candidate> temp_search_results; 
            temp_search_results.reserve(16);

            // Buffer Pixel ZMCL (Flat vector)
            std::vector<float> local_ref_buffer(current_tile_h * current_tile_w);
            std::vector<float> local_comp_buffer(current_tile_h * current_tile_w);

            // Cache Cost Integer (Hanya dipakai di finest layer)
            // OPTIMIZATION: Linear search vector is faster than std::map for small N (< 20)
            struct CacheItem { uint32_t key; float val; };
            std::vector<CacheItem> integer_cost_cache;
            integer_cost_cache.reserve(16);

            // --- OPTIMASI EARLY EXIT ---
            // Jika cost (MSE) di bawah nilai ini, hentikan pencarian kandidat lain.
            // Increased from 0.005f to 0.008f for faster exit in flat/good regions
            const float EARLY_EXIT_COST = 0.008f; 

#pragma omp for schedule(dynamic)
            for (int y = 0; y <= h_layer - current_tile_h; y += step_y)
            {
                for (int x = 0; x <= w_layer - current_tile_w; x += step_x)
                {
                    temp_initial_flows.clear();
                    temp_search_results.clear();

                    // 1. Dapatkan Kandidat
                    AlignmentFlowHelpers::generateCandidateFlows(temp_initial_flows, layer_index, total_layers, previous_level_flow, flow, y, x, current_tile_h, current_tile_w);

                    // 2. Evaluasi Kandidat
                    
                    // === JALUR CEPAT: FINEST LAYER (ZMCL/AVX Optimized) ===
                    if (is_finest_layer) 
                    {
                        // Copy Reference Tile SEKALI saja
                        AlignmentFlowHelpers::copyTileToContiguousBuffer(ref_layer, y, x, current_tile_h, current_tile_w, local_ref_buffer);
                        integer_cost_cache.clear();

                        float best_cost_so_far = std::numeric_limits<float>::max();

                        for (const auto &initial_vec : temp_initial_flows)
                        {
                            // Snap ke grid integer untuk cost calculation
                            int i_dx = static_cast<int>(std::round(initial_vec[0]));
                            int i_dy = static_cast<int>(std::round(initial_vec[1]));
                            
                            // Key packing (int16 | int16 -> int32)
                            uint32_t key = (static_cast<uint16_t>(i_dy) << 16) | static_cast<uint16_t>(i_dx);

                            float cost = -1.0f;
                            
                            // Linear Search
                            for(const auto& item : integer_cost_cache) {
                                if(item.key == key) {
                                    cost = item.val;
                                    break;
                                }
                            }

                            if (cost < 0.0f) {
                                // Cache Miss: Hitung Heavy Cost
                                int test_y = y + i_dy;
                                int test_x = x + i_dx;
                                
                                cost = AlignmentFlowHelpers::calculateCostAtIntegerPos(
                                    local_ref_buffer, comp_layer, 
                                    test_y, test_x, 
                                    current_tile_h, current_tile_w, 
                                    local_comp_buffer
                                );
                                
                                if (cost != std::numeric_limits<float>::max()) {
                                    cost *= tile_area_inv;
                                }
                                integer_cost_cache.push_back({key, cost});
                            }

                            // Simpan hasil
                            if (cost != std::numeric_limits<float>::max()) {
                                temp_search_results.push_back({initial_vec, cost});
                                if (cost < best_cost_so_far) best_cost_so_far = cost;
                            }

                            // CHECK EARLY EXIT
                            // Jika kandidat pertama (Inherited Flow) sudah bagus, stop.
                            if (best_cost_so_far < EARLY_EXIT_COST) break;
                        }
                    }
                    // === JALUR STANDARD: COARSE LAYER ===
                    else
                    {
                        for (const auto &initial_vec : temp_initial_flows)
                        {
                            AlignmentFlowHelpers::searchCoarseLevelDirect(ref_layer, comp_layer, y, x, current_tile_h, current_tile_w, initial_vec, current_layer_search_dist, temp_search_results);
                            
                            // Early exit untuk coarse search
                            if (!temp_search_results.empty() && 
                                (temp_search_results.front().cost * tile_area_inv) < EARLY_EXIT_COST) 
                            {
                                break;
                            }
                        }
                    }

                    // 3. Pilih Flow Terbaik
                    cv::Point2f chosen_flow;
                    if (temp_search_results.empty())
                    {
                        // Fallback ke nilai awal flow map jika search gagal
                        chosen_flow = flow.at<cv::Point2f>(y, x);
                    }
                    else if (temp_search_results.size() == 1)
                    {
                        // OPTIMASI: Fast path untuk single candidate (skip expensive spatial analysis)
                        chosen_flow = temp_search_results[0].flow;
                    }
                    else
                    {
                        chosen_flow = AlignmentFlowHelpers::selectBestCandidate(
                            temp_search_results, flow, y, x, current_tile_h, current_tile_w);
                    }

                    // 4. Subpixel Refinement
                    // SKIP untuk Finest Layer (boros waktu, gain visual minim di resolusi penuh)
                    // SKIP untuk Coarsest Layer (akan di-handle RANSAC)
                    if (!is_finest_layer && !is_coarsest_layer) {
                        chosen_flow = subpixel_refinement(
                            ref_layer, comp_layer, x, y,
                            (int)std::round(chosen_flow.x), (int)std::round(chosen_flow.y),
                            current_tile_w, current_tile_h
                        );
                    }

                    // 5. DIRECT WRITE TO OUTPUT MATRIX (Safe because no overlap)
                    int end_y = std::min(y + current_tile_h, h_layer);
                    int end_x = std::min(x + current_tile_w, w_layer);

                    for (int ry = y; ry < end_y; ++ry) {
                        cv::Vec2f* out_ptr = refined_flow.ptr<cv::Vec2f>(ry);
                        for (int rx = x; rx < end_x; ++rx) {
                            out_ptr[rx][0] = chosen_flow.x;
                            out_ptr[rx][1] = chosen_flow.y;
                        }
                    }
                }
            }
        } // End Parallel Region
        } // End Search Timer Scope

        // Update flow ke hasil yang sudah di-refine
        flow = refined_flow;

        // --- 5. REDUCE PHASE (REMOVED - INTEGRATED TO PARALLEL LOOP ABOVE) ---
        // (Waktu komputasi yang sebelumnya 60ms kini menyatu dengan search phase)


        // --- 6. POST-PROCESSING FILTERS ---
        SimpleTimer filter_timer("Layer " + std::to_string(layer_index) + " Filtering");

        // A. Smoothing Sambungan (De-blocking)
        // Karena kita pakai non-overlap tiles, akan muncul efek kotak-kotak.
        // Kita haluskan dengan filter cepat.
        if (is_finest_layer) {
            // Di layer akhir, gunakan Box Filter (sangat cepat, O(1))
            // Kernel 3x3 cukup (Reduced from 5x5)
            cv::boxFilter(flow, flow, -1, cv::Size(3, 3));
        } else {
            // OPTIMASI: Kernel 3x3 lebih cepat (vs 5x5) dan masih efektif
            cv::medianBlur(flow, flow, 3);
        }

        // B. RANSAC (Hanya di level paling kasar)
        // Untuk memastikan alignment global awal benar
        if (layer_index >= total_layers - 2)
        {
            AlignmentFlowHelpers::RANSACOutlierRemoval(flow, layer_index, total_layers);
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
        SimpleTimer overall_timer("TOTAL FLOW COMPUTATION");
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
            SimpleTimer pyramid_timer("Pyramid Generation"); // Opsional
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
            SimpleTimer flow_levels_timer("Coarse-to-Fine Flow Processing");

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

        // === BAGIAN C.5: Post-Processing - Spatial/Local RANSAC Cleanup ===
        // Membersihkan flow field dengan local RANSAC per window
        // window_size=64, overlap=25% (step=48) -> Reduced overlap for speed
        {
            SimpleTimer ransac_timer("Spatial RANSAC Cleanup");
            // OPTIMIZATION: Reduce overlap (0.25 -> 0.1) for speed
            AlignmentFlowHelpers::spatialLocalRANSACCleanup(flow, 64, 0.1f);
        }

        // === BAGIAN D: Finalisasi dan Pengembalian Data ===
        float *output_flow_data = nullptr;
        {
            SimpleTimer finalization_timer("Finalization & Data Copy");
            if (!flow.empty())
            {
                // OPTIMIZATION: Pastikan continuous agar copy cepat
                if (!flow.isContinuous()) flow = flow.clone();

                const size_t total_pixels = flow.total();
                const size_t data_size = total_pixels * flow.elemSize();
                output_flow_data = static_cast<float *>(malloc(data_size));
                
                if (output_flow_data)
                {
                    // OPTIMIZATION: Parallel copy using OpenMP
                    // memcpy biasa bersifat serial. Parallel copy bisa lebih cepat 
                    // menembus limit bandwidth memori pada gambar resolusi tinggi (12MP+).
                    const int rows = flow.rows;
                    const int cols = flow.cols;
                    const size_t row_size_bytes = cols * flow.elemSize();

                    #pragma omp parallel for
                    for (int r = 0; r < rows; ++r) {
                        const uchar* src_ptr = flow.ptr<uchar>(r);
                        uchar* dst_ptr = reinterpret_cast<uchar*>(output_flow_data) + (size_t)r * row_size_bytes;
                        std::memcpy(dst_ptr, src_ptr, row_size_bytes);
                    }
                }
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