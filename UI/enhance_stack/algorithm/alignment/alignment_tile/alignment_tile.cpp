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
    constexpr int GAUSSIAN_CACHE_SIZE = 50;
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
            // Pastikan tipe data adalah 8-bit untuk equalizeHist
            ref_layer.convertTo(guide_image_8u, CV_8U);
        }

        // 1a. Tingkatkan kontras secara dramatis untuk mempertajam tepi
        cv::equalizeHist(guide_image_8u, guide_image_8u);

        // 1b. Konversi ke float dan normalisasi ke [0, 1] untuk parameterisasi yang stabil
        cv::Mat guide_image_32f;
        guide_image_8u.convertTo(guide_image_32f, CV_32F, 1.0 / 255.0);

        // --- LANGKAH 2: UPSAMPLING KASAR PADA FLOW ---
        std::vector<cv::Mat> flow_channels;
        cv::split(previous_level_flow, flow_channels);

        cv::Mat flow_x_upsampled, flow_y_upsampled;
        cv::resize(flow_channels[0], flow_x_upsampled, ref_layer.size(), 0, 0, cv::INTER_NEAREST);
        cv::resize(flow_channels[1], flow_y_upsampled, ref_layer.size(), 0, 0, cv::INTER_NEAREST);

        // --- LANGKAH 3: TERAPKAN GUIDED FILTER DENGAN PARAMETER YANG LEBIH BAIK ---
        int radius = 2;      // Radius lebih kecil untuk respons yang lebih lokal
        double eps = 0.0001; // Eps lebih kecil agar sangat patuh pada guide

        cv::Mat flow_x_guided, flow_y_guided;
        // Gunakan guide yang sudah ditingkatkan kontrasnya dan dinormalisasi
        cv::ximgproc::guidedFilter(guide_image_32f, flow_x_upsampled, flow_x_guided, radius, eps);
        cv::ximgproc::guidedFilter(guide_image_32f, flow_y_upsampled, flow_y_guided, radius, eps);

        // --- LANGKAH 4 & 5: GABUNGKAN DAN SCALE ---
        std::vector<cv::Mat> guided_channels = {flow_x_guided, flow_y_guided};
        cv::Mat flow_upsampled;
        cv::merge(guided_channels, flow_upsampled);

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
        // Kita akan mengumpulkan lebih banyak kandidat, jadi reserve lebih banyak
        candidate_flows.reserve(15);

        // === KASUS DASAR: Level paling kasar, hanya ada zero flow ===
        if (layer_index == total_layers - 1)
        {
            candidate_flows.emplace_back(0.0f, 0.0f);
            // Perturbasi kecil bisa ditambahkan di sini jika diperlukan,
            // tapi logika fallback di bawah sudah cukup.
            return;
        }

        // === SUMBER KANDIDAT #1: Metal-Inspired Spatial Correction (Paling Penting) ===
        // Mengambil kandidat dari tetangga di level yang SAMA (setelah upsampling)
        // untuk memperbaiki error propagasi.
        {
            // 1a. Kandidat dari tile itu sendiri (tebakan awal terbaik)
            const cv::Vec2f &center_flow = current_flow.at<cv::Vec2f>(
                tile_center_y + current_tile_h / 2,
                tile_center_x + current_tile_w / 2);
            candidate_flows.push_back(center_flow);

            // 1b. Kandidat dari tetangga horizontal dan vertikal (logika dari `correct_upsampling_error`)
            // Map pixel-coord ke tile-grid-coord untuk meniru logika `gid.x % 2` di Metal
            const int step_x = std::max(current_tile_w / 2, 1);
            const int step_y = std::max(current_tile_h / 2, 1);
            const int tile_grid_x = tile_center_x / step_x;
            const int tile_grid_y = tile_center_y / step_y;

            int dx_shift = (tile_grid_x % 2 == 0) ? -step_x : step_x;
            int dy_shift = (tile_grid_y % 2 == 0) ? -step_y : step_y;

            int h_neighbor_x = tile_center_x + dx_shift;
            int v_neighbor_y = tile_center_y + dy_shift;

            // Cek boundary dan tambahkan kandidat dari tetangga
            if (h_neighbor_x >= 0 && h_neighbor_x < current_flow.cols)
            {
                candidate_flows.push_back(current_flow.at<cv::Vec2f>(tile_center_y, h_neighbor_x));
            }
            if (v_neighbor_y >= 0 && v_neighbor_y < current_flow.rows)
            {
                candidate_flows.push_back(current_flow.at<cv::Vec2f>(v_neighbor_y, tile_center_x));
            }
        }

        // === SUMBER KANDIDAT #2: Propagasi dari Level Kasar (Logika Lama) ===
        // Memberikan keragaman dan menangkap gerakan yang lebih besar.
        {
            const int coarse_y = static_cast<int>((tile_center_y + current_tile_h * 0.5f) * 0.5f);
            const int coarse_x = static_cast<int>((tile_center_x + current_tile_w * 0.5f) * 0.5f);

            const int max_row = previous_level_flow.rows;
            const int max_col = previous_level_flow.cols;

            const cv::Vec2f *flow_ptr = previous_level_flow.ptr<cv::Vec2f>();

            // Sample dari 3x3 neighborhood di level KASAR
            for (int dr = -1; dr <= 1; ++dr)
            {
                const int ny = coarse_y + dr;
                if (ny < 0 || ny >= max_row)
                    continue;

                for (int dc = -1; dc <= 1; ++dc)
                {
                    const int nx = coarse_x + dc;
                    if (nx >= 0 && nx < max_col)
                    {
                        const cv::Vec2f &prev_flow = flow_ptr[ny * max_col + nx];
                        candidate_flows.emplace_back(prev_flow * FLOW_UPSCALE_FACTOR);
                    }
                }
            }
        }

        // === FINALISASI: Deduplikasi dan Fallback ===

        // 1. Hapus kandidat duplikat agar lebih efisien
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

        // 2. Fallback: Jika tidak ada kandidat, buat perturbasi di sekitar flow saat ini
        if (candidate_flows.empty())
        {
            const cv::Vec2f center_flow = current_flow.at<cv::Vec2f>(
                tile_center_y + current_tile_h / 2,
                tile_center_x + current_tile_w / 2);

            candidate_flows.emplace_back(center_flow);

            const float cx = center_flow[0];
            const float cy = center_flow[1];

            candidate_flows.emplace_back(cx - 1, cy - 1);
            candidate_flows.emplace_back(cx, cy - 1);
            candidate_flows.emplace_back(cx + 1, cy - 1);
            candidate_flows.emplace_back(cx - 1, cy); /* center */
            candidate_flows.emplace_back(cx + 1, cy);
            candidate_flows.emplace_back(cx - 1, cy + 1);
            candidate_flows.emplace_back(cx, cy + 1);
            candidate_flows.emplace_back(cx + 1, cy + 1);
        }
    }

    /**
     * Pencarian tile matching untuk level kasar (coarse)
     */
    static inline void searchCoarseLevelDirect(
        const cv::Mat &ref_layer,
        const cv::Mat &comp_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w,
        const cv::Vec2f &initial_flow,
        float search_dist,
        std::vector<Candidate> &out_candidates) // Reuse vector
    {
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

        for (int dy = -current_search_dist; dy <= current_search_dist; ++dy)
        {
            for (int dx = -current_search_dist; dx <= current_search_dist; ++dx)
            {
                const int test_y = tile_y + init_dy + dy;
                const int test_x = tile_x + init_dx + dx;

                if (test_y < 0 || test_x < 0 ||
                    test_y + tile_h > h_layer ||
                    test_x + tile_w > w_layer)
                    continue;

                float current_cost = 0.0f;

                if (tile_h * tile_w >= 64 * 64)
                {
                    cv::Mat ref_tile(ref_layer, cv::Rect(tile_x, tile_y, tile_w, tile_h));
                    cv::Mat comp_tile(comp_layer, cv::Rect(test_x, test_y, tile_w, tile_h));
                    current_cost = block_cost_fft(ref_tile, comp_tile);
                }
                else
                {
                    for (int r_tile = 0; r_tile < tile_h; ++r_tile)
                    {
                        const float *p_ref = ref_layer.ptr<float>(tile_y + r_tile, tile_x);
                        const float *p_comp = comp_layer.ptr<float>(test_y + r_tile, test_x);
                        current_cost += calculate_zncc(p_ref, p_comp, tile_w);
                    }
                }

                Candidate cand{cv::Point2f(init_dx + dx, init_dy + dy),
                               current_cost * tile_area_inv};

                if (out_candidates.size() < 5)
                {
                    out_candidates.push_back(cand);
                    std::sort(out_candidates.begin(), out_candidates.end(),
                              [](const Candidate &a, const Candidate &b)
                              {
                                  return a.cost < b.cost;
                              });
                }
                else if (cand.cost < out_candidates.back().cost)
                {
                    out_candidates.back() = cand;
                    std::sort(out_candidates.begin(), out_candidates.end(),
                              [](const Candidate &a, const Candidate &b)
                              {
                                  return a.cost < b.cost;
                              });
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

    /**
     * Inline versi searchFineLevel yang mengembalikan langsung ke Candidate array
     * Menghindari alokasi vector dan return by value
     */
    static inline bool searchFineLevelDirect(
        const cv::Mat &ref_layer,
        const cv::Mat &comp_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w,
        const cv::Vec2f &initial_flow,
        Candidate &out_candidate) // Output langsung ke parameter
    {
        const int init_dy = static_cast<int>(std::round(initial_flow[1]));
        const int init_dx = static_cast<int>(std::round(initial_flow[0]));

        const int test_y = tile_y + init_dy;
        const int test_x = tile_x + init_dx;

        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;

        // Early exit jika di luar bounds
        if (test_y < 0 || test_x < 0 ||
            test_y + tile_h > h_layer ||
            test_x + tile_w > w_layer)
            return false;

        const float tile_area_inv = 1.0f / static_cast<float>(tile_h * tile_w);
        float current_cost = 0.0f;

        // Compute cost langsung tanpa intermediate storage
        if (tile_h * tile_w >= 64 * 64)
        {
            cv::Mat ref_tile(ref_layer, cv::Rect(tile_x, tile_y, tile_w, tile_h));
            cv::Mat comp_tile(comp_layer, cv::Rect(test_x, test_y, tile_w, tile_h));
            current_cost = block_cost_fft(ref_tile, comp_tile);
        }
        else
        {
            for (int r_tile = 0; r_tile < tile_h; ++r_tile)
            {
                const float *p_ref = ref_layer.ptr<float>(tile_y + r_tile, tile_x);
                const float *p_comp = comp_layer.ptr<float>(test_y + r_tile, test_x);
                current_cost += calculate_zncc(p_ref, p_comp, tile_w);
            }
        }

        // Set output langsung
        out_candidate.flow = cv::Point2f(init_dx, init_dy);
        out_candidate.cost = current_cost * tile_area_inv;

        return true;
    }

    /**
     * Pilih kandidat terbaik dengan neighborhood consistency check
     */
    static inline cv::Point2f selectBestCandidate(
        const std::vector<Candidate> &candidates,
        const cv::Mat &current_flow,
        const cv::Mat &ref_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w)
    {
        // OPTIMIZED: Early exit untuk kasus tepi
        if (candidates.empty())
        {
            return cv::Point2f(0, 0);
        }

        // Pastikan kandidat sudah diurutkan (asumsi dari pemanggilan sebelumnya)
        // Di sini kita hanya butuh cost terbaik untuk analisis.
        const float best_cost_by_appearance = candidates.front().cost;
        const cv::Point2f best_flow_by_appearance = candidates.front().flow;

        // --- LANGKAH 2: Analisis Tetangga (Tidak Berubah) ---
        cv::Vec2f sum_neigh(0.0f, 0.0f);
        int neighbor_count = 0;

        // ... (Kode untuk menghitung sum_neigh dan neighbor_count tidak berubah)
        const int max_row = current_flow.rows;
        const int max_col = current_flow.cols;
        cv::Vec2f neighbor_flows[8];
        const cv::Vec2f *flow_data = current_flow.ptr<cv::Vec2f>(0);
        const int flow_step = current_flow.cols;

        for (int dy = -1; dy <= 1; dy++) {
            const int ny = tile_y + dy;
            if (ny < 0 || ny >= max_row) continue;
            const int row_offset = ny * flow_step;
            for (int dx = -1; dx <= 1; dx++) {
                if (dy == 0 && dx == 0) continue;
                const int nx = tile_x + dx;
                if (nx >= 0 && nx < max_col) {
                    const cv::Vec2f &flow = flow_data[row_offset + nx];
                    neighbor_flows[neighbor_count++] = flow;
                    sum_neigh += flow;
                }
            }
        }
        
        if (neighbor_count == 0)
        {
            return best_flow_by_appearance;
        }

        const float inv_count = 1.0f / neighbor_count;
        const cv::Vec2f avg_neigh = sum_neigh * inv_count;

        // --- LANGKAH 3: Hitung Lambda Adaptif (Ditingkatkan) ---
        const float BASE_LAMBDA = 2.0f; // Ditingkatkan sedikit dari 1.0f
        float adaptive_lambda = BASE_LAMBDA;

        // 3a. Variance calculation
        float flow_variance = 0.0f;
        for (int i = 0; i < neighbor_count; i++)
        {
            const cv::Vec2f diff = neighbor_flows[i] - avg_neigh;
            flow_variance += diff[0] * diff[0] + diff[1] * diff[1];
        }
        flow_variance *= inv_count;

        const float variance_sigma = 2.0f;
        const float inv_variance_sigma_sq = 1.0f / (variance_sigma * variance_sigma);
        const float lambda_from_neighbors = std::exp(-flow_variance * inv_variance_sigma_sq);
        adaptive_lambda *= lambda_from_neighbors;

        // 3b. Texture analysis
        const int safe_x = std::max(0, std::min(tile_x, ref_layer.cols - tile_w));
        const int safe_y = std::max(0, std::min(tile_y, ref_layer.rows - tile_h));
        const cv::Rect tile_roi(safe_x, safe_y, tile_w, tile_h);
        const cv::Mat ref_tile = ref_layer(tile_roi);

        cv::Mat grad_x, grad_y;
        cv::Sobel(ref_tile, grad_x, CV_32F, 1, 0, 3, 1.0, 0.0, cv::BORDER_REPLICATE);
        cv::Sobel(ref_tile, grad_y, CV_32F, 0, 1, 3, 1.0, 0.0, cv::BORDER_REPLICATE);

        cv::Mat magnitude;
        cv::magnitude(grad_x, grad_y, magnitude);
        const float texture_score = cv::mean(magnitude)[0];

        const float texture_sigma = 10.0f;
        const float inv_texture_sigma = 1.0f / texture_sigma;
        const float lambda_from_content = std::exp(-texture_score * inv_texture_sigma);
        adaptive_lambda *= lambda_from_content;

        // BARU: 3c. Cost Quality Analysis (memperkuat lambda jika cost buruk)
        const float cost_sigma = 0.2f; // Cost yang dianggap "buruk"
        const float blending_max_factor = 3.0f; // Maksimal 3x lipat
        
        // blending_factor = 0 jika cost=0, mendekati 1.0 jika cost >> cost_sigma
        const float blending_factor = std::min(1.0f, best_cost_by_appearance / cost_sigma);
        
        // Final adaptive_lambda akan memiliki bobot yang lebih besar jika cost buruk
        adaptive_lambda = adaptive_lambda * (1.0f + blending_factor * (blending_max_factor - 1.0f));

        // --- LANGKAH 4: Combined Cost dengan Lambda Adaptif (Ditingkatkan) ---
        float min_total_cost = std::numeric_limits<float>::max();
        cv::Point2f chosen_flow = best_flow_by_appearance;

        const float avg_x = avg_neigh[0];
        const float avg_y = avg_neigh[1];
        
        // BARU: Epsilon Charbonnier-like Spatial Cost
        const float SPATIAL_EPSILON_SQ = 0.001f; // Sangat kecil untuk transisi L1/L2 yang mulus

        for (const auto &cand : candidates)
        {
            // Manual distance calculation
            const float dx = cand.flow.x - avg_x;
            const float dy = cand.flow.y - avg_y;
            const float spatial_dist_sq = dx * dx + dy * dy;

            // Charbonnier-like Spatial Cost (L1-L2 Hybrid)
            const float spatial_cost = std::sqrt(spatial_dist_sq + SPATIAL_EPSILON_SQ);

            // Total Cost = Appearance Cost + Adaptive Regularization Cost
            const float total_cost = cand.cost + adaptive_lambda * spatial_cost;

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

    /**
     * Proses tile matching untuk satu layer (FINAL VERSION 5-LEVEL - L0 OPTIMIZED)
     * L4-L2: FFT (NO Overlap)  <-- sebelumnya, sekarang diubah: L4-L1 = 50% Overlap (Gaussian)
     * L1: Dynamic 64/96 FFT (50% Overlap)
     * L0: Original ZNCC/ZMCL (NO Overlap, NO Blend, Search Radius +/- 1) <- BARU!
     */
    static cv::Mat processSingleLayer(
        const cv::Mat &ref_layer,
        const cv::Mat &comp_layer,
        const cv::Mat &previous_level_flow,
        int layer_index,
        int total_layers,
        int tile_h, // Ukuran tile asli dari level 0
        int tile_w, // Ukuran tile asli dari level 0
        float search_dist)
    {
        using namespace ImageAlignmentConfig;

        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;

        cv::Mat flow;
        // Inisialisasi flow di level paling kasar adalah Zero Flow
        if (layer_index == total_layers - 1)
            flow = initializeCoarsestFlow(ref_layer); // Zero Flow
        // flow diinisialisasi sebagai upsampled flow dari level sebelumnya
        else
            flow = upsamplingFlow(previous_level_flow, ref_layer);

        // --- Penentuan Layer Index Baru (Implisit total_layers = 5) ---
        const int L4_INDEX = total_layers - 1; 
        const int L3_INDEX = total_layers - 2; 
        const int L2_INDEX = total_layers - 3; 
        const int L1_INDEX = total_layers - 4; 
        const int L0_INDEX = total_layers - 5; 

        int current_tile_h;
        int current_tile_w;

        // ==========================================================
        // PENENTUAN UKURAN TILE OVERRIDE (FIX TILING) & COST SWITCH
        // ==========================================================
        // ... (Logika L4, L3, L2, L1 tidak berubah kecuali tiling ukuran)
        if (layer_index == L4_INDEX) {
            current_tile_h = std::max(MIN_TILE_SIZE, h_layer / 2);
            current_tile_w = std::max(MIN_TILE_SIZE, w_layer / 2);
        }
        else if (layer_index == L3_INDEX) {
            current_tile_h = std::max(MIN_TILE_SIZE, h_layer / 4);
            current_tile_w = std::max(MIN_TILE_SIZE, w_layer / 4);
        }
        else if (layer_index == L2_INDEX) {
            current_tile_h = std::max(MIN_TILE_SIZE, h_layer / 8);
            current_tile_w = std::max(MIN_TILE_SIZE, w_layer / 8);
        }
        else if (layer_index == L1_INDEX) {
            const int base_tile = (tile_h > 32 || tile_w > 32) ? 96 : 64;
            current_tile_h = std::min(base_tile, h_layer);
            current_tile_w = std::min(base_tile, w_layer);
        }
        else // L0 (Paling Halus): Ukuran Tile Asli ZNCC/ZMCL (Overlap)
        {
            current_tile_h = std::max(MIN_TILE_SIZE, std::min(tile_h, h_layer));
            current_tile_w = std::max(MIN_TILE_SIZE, std::min(tile_w, w_layer));
        }

        // --- Safety Check ---
        if (current_tile_h <= 0 || current_tile_w <= 0 || h_layer < current_tile_h || w_layer < current_tile_w) return flow;
        // --------------------


        // ==========================================================
        // PENENTUAN STEP SIZE (Overlap vs No Overlap)
        // ==========================================================
        
        // Sekarang: Overlap aktif pada L1..L4 (50%). L0 tetap NO Overlap.
        const bool use_overlap = (layer_index >= L1_INDEX && layer_index <= L4_INDEX);

        int step_y;
        int step_x;

        if (use_overlap) {
            // L1..L4: 50% Overlap
            step_y = std::max(current_tile_h / 2, 1);
            step_x = std::max(current_tile_w / 2, 1);
        } else { // L0
            // L0: NO Overlap (Step = Ukuran Tile)
            step_y = current_tile_h; 
            step_x = current_tile_w;
        }
        
        // Penyesuaian Logika Subpixel Refinement
        const bool do_subpixel          = (layer_index > L0_INDEX);  // L1-L4 = YA (Subpixel), L0 = TIDAK

        // ========================================================================
        // === BAGIAN INTI: Agregasi Hasil Paralel (MAP PHASE) ====================
        // ========================================================================

        // 1. Buat kontainer untuk menampung hasil dari setiap thread.
        std::vector<std::vector<TileResult>> thread_results(omp_get_max_threads());

#pragma omp parallel
        {
            std::vector<cv::Vec2f> candidate_flows;
            candidate_flows.reserve(20);
            std::vector<Candidate> coarse_candidates;
            coarse_candidates.reserve(100);
            std::vector<Candidate> all_candidates;
            all_candidates.reserve(100);

            int thread_id = omp_get_thread_num();

#pragma omp for schedule(dynamic)
            for (int y = 0; y <= h_layer - current_tile_h; y += step_y)
            {
                for (int x = 0; x <= w_layer - current_tile_w; x += step_x)
                {
                    generateCandidateFlows(candidate_flows, layer_index, total_layers, previous_level_flow, flow, y, x, current_tile_h, current_tile_w);
                    all_candidates.clear();
                    
                    // Penyesuaian search_dist untuk L0 (Optimasi Kecepatan)
                    float current_search_dist = search_dist;
                    if (layer_index == L0_INDEX) { 
                        current_search_dist = 1.0f; // Hanya cari +/- 1 piksel
                    }
                    
                    // Evaluasi kandidat (Selalu menggunakan searchCoarseLevelDirect)
                    for (const auto &initial_vec : candidate_flows)
                    {
                        searchCoarseLevelDirect(ref_layer, comp_layer, y, x, current_tile_h, current_tile_w, initial_vec, current_search_dist, coarse_candidates);
                        all_candidates.insert(all_candidates.end(), coarse_candidates.begin(), coarse_candidates.end());
                    }

                    // ... (Langkah 3 & 4: Select Best Candidate & Refinement)
                    if (all_candidates.size() > 5) {
                        std::partial_sort(all_candidates.begin(), all_candidates.begin() + 5, all_candidates.end(),
                                          [](const Candidate &a, const Candidate &b) { return a.cost < b.cost; });
                        all_candidates.resize(5);
                    }

                    cv::Point2f chosen_flow = selectBestCandidate(all_candidates, flow, ref_layer, y, x, current_tile_h, current_tile_w);

                    cv::Point2f refined_flow = chosen_flow;
                    if (do_subpixel) {
                        refined_flow = subpixel_refinement(ref_layer, comp_layer, x, y, (int)std::round(chosen_flow.x), (int)std::round(chosen_flow.y), current_tile_w, current_tile_h);
                    }

                    thread_results[thread_id].push_back({cv::Rect(x, y, current_tile_w, current_tile_h), refined_flow});
                }
            }
        } // Akhir dari #pragma omp parallel

        // --- REDUCE PHASE (Serial) ---
        cv::Mat flow_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
        cv::Mat weight_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);

        // Gabungkan hasil dari semua thread ke dalam akumulator global
        for (const auto &results_from_one_thread : thread_results)
        {
            for (const auto &result : results_from_one_thread)
            {
                const cv::Rect &tile_roi = result.roi;
                const cv::Point2f &result_flow = result.flow;
                cv::Mat flow_roi = flow_accumulator(tile_roi);

                // --- LOGIKA PEMBOBOTAN GAUSSIAN/UNIFORM ---
                // Sekarang: Gaussian Window untuk semua level yang menggunakan overlap (L1..L4)
                // Uniform Window untuk No Overlap (L0)
                
                // Cek apakah tile ini adalah bagian dari level yang menggunakan overlap (L1..L4)
                const bool current_tile_use_gaussian = use_overlap; // true untuk L1..L4

                if (current_tile_use_gaussian) {
                    // Overlap -> Bobot Gaussian
                    const cv::Mat &g_window = getGaussianWindow(tile_roi.height, tile_roi.width);
                    std::vector<cv::Mat> channels;
                    cv::split(flow_roi, channels);
                    channels[0] += result_flow.x * g_window;
                    channels[1] += result_flow.y * g_window;
                    cv::merge(channels, flow_roi);

                    weight_accumulator(tile_roi) += g_window;
                }
                else {
                    // L0: No Overlap -> Bobot 1.0 (Uniform)
                    const cv::Mat ones = cv::Mat::ones(tile_roi.height, tile_roi.width, CV_32F);
                    std::vector<cv::Mat> channels;
                    cv::split(flow_roi, channels);
                    channels[0] += result_flow.x * ones;
                    channels[1] += result_flow.y * ones;
                    cv::merge(channels, flow_roi);

                    weight_accumulator(tile_roi) += ones;
                }
            }
        }

        // --- FINALISASI ---
        std::vector<cv::Mat> flow_channels;
        cv::split(flow_accumulator, flow_channels);

        cv::Mat mask = weight_accumulator > NORMALIZATION_EPSILON;
        
        // PENTING: Untuk No-Overlap, pembagi weight_accumulator akan berisi 1.0, 
        // yang secara efektif melakukan set flow. Ini sudah benar.
        cv::divide(flow_channels[0], weight_accumulator, flow_channels[0], 1.0, -1);
        cv::divide(flow_channels[1], weight_accumulator, flow_channels[1], 1.0, -1);

        flow_channels[0].setTo(0, ~mask);
        flow_channels[1].setTo(0, ~mask);

        cv::merge(flow_channels, flow);
        
        // ==========================================================
        // PENINGKATAN: MEDIAN FILTER (HANYA L4, L3, L2)
        // ==========================================================
        if (layer_index == L4_INDEX || layer_index == L3_INDEX || layer_index == L2_INDEX) {
            cv::medianBlur(flow, flow, 5); 
        }
        
        // 2. Panggil RANSAC versi asli
        RANSACOutlierRemoval(flow, layer_index, total_layers);

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

        // =========================================================================
        // === BAGIAN C: Perhitungan Optical Flow (Coarse-to-Fine) REFACTORED  ===
        // =========================================================================

        cv::Mat flow;
        cv::Mat previous_level_flow;

        {
            // SimpleTimer all_levels_timer("Coarse-to-Fine Flow (All Levels)");
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

        // =========================================================================
        // === BAGIAN D: Finalisasi dan Pengembalian Data ===
        // =========================================================================
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