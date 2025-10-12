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

// Konstanta konfigurasi
namespace ImageAlignmentConfig
{
    constexpr int GAUSSIAN_CACHE_SIZE = 50;
    constexpr float NORMALIZATION_EPSILON = 1e-6f;
    constexpr float FLOW_UPSCALE_FACTOR = 2.0f;
    constexpr int MIN_TILE_SIZE = 8;
    constexpr int MIN_PYRAMID_LAYER_SIZE = 32;
}

namespace OpticalFlowHelpers
{
    // Cache untuk Gaussian window
    static thread_local std::map<std::pair<int, int>, cv::Mat> gaussian_cache;

    /**
     * Mendapatkan Gaussian window dengan caching
     */
    static const cv::Mat& getGaussianWindow(int rows, int cols)
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
    static cv::Mat initializeCoarsestFlow(const cv::Mat& ref_layer)
    {
        return cv::Mat::zeros(ref_layer.size(), CV_32FC2);
    }

    /**
     * Upsample flow dari level sebelumnya dengan edge-aware blending
     */
    static inline cv::Mat upsamplingFlow(
        const cv::Mat& previous_level_flow,
        const cv::Mat& ref_layer)
    {
        using namespace ImageAlignmentConfig;

        // --- LANGKAH 1: PRE-PROCESSING GAMBAR PEMANDU (GUIDE IMAGE) ---
        cv::Mat guide_image_8u;
        if (ref_layer.channels() > 1) {
            cv::cvtColor(ref_layer, guide_image_8u, cv::COLOR_BGR2GRAY);
        } else {
            // Pastikan tipe data adalah 8-bit untuk equalizeHist
            ref_layer.convertTo(guide_image_8u, CV_8U);
        }
        
        // 1a. Tingkatkan kontras secara dramatis untuk mempertajam tepi
        cv::equalizeHist(guide_image_8u, guide_image_8u);

        // 1b. Konversi ke float dan normalisasi ke [0, 1] untuk parameterisasi yang stabil
        cv::Mat guide_image_32f;
        guide_image_8u.convertTo(guide_image_32f, CV_32F, 1.0/255.0);

        // --- LANGKAH 2: UPSAMPLING KASAR PADA FLOW ---
        std::vector<cv::Mat> flow_channels;
        cv::split(previous_level_flow, flow_channels);

        cv::Mat flow_x_upsampled, flow_y_upsampled;
        cv::resize(flow_channels[0], flow_x_upsampled, ref_layer.size(), 0, 0, cv::INTER_NEAREST);
        cv::resize(flow_channels[1], flow_y_upsampled, ref_layer.size(), 0, 0, cv::INTER_NEAREST);

        // --- LANGKAH 3: TERAPKAN GUIDED FILTER DENGAN PARAMETER YANG LEBIH BAIK ---
        int radius = 2;       // Radius lebih kecil untuk respons yang lebih lokal
        double eps = 0.0001;   // Eps lebih kecil agar sangat patuh pada guide
        
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
        std::vector<cv::Vec2f>& candidate_flows,
        int layer_index,
        int total_layers,
        const cv::Mat& previous_level_flow,
        const cv::Mat& current_flow,
        int tile_center_y,
        int tile_center_x,
        int current_tile_h,
        int current_tile_w)
    {
        using namespace ImageAlignmentConfig;
        
        candidate_flows.clear();

        if (layer_index == total_layers - 1)
        {
            // Level paling kasar: mulai dari zero flow
            candidate_flows.emplace_back(0.0f, 0.0f);
        }
        else
        {
            // OPTIMIZED: Pre-calculate koordinat sekali saja
            const int coarse_y = static_cast<int>((tile_center_y + current_tile_h * 0.5f) * 0.5f);
            const int coarse_x = static_cast<int>((tile_center_x + current_tile_w * 0.5f) * 0.5f);
            
            // OPTIMIZED: Pre-calculate boundary checks
            const int max_row = previous_level_flow.rows;
            const int max_col = previous_level_flow.cols;
            
            // OPTIMIZED: Reserve space untuk menghindari reallocation (max 9 candidates)
            candidate_flows.reserve(9);
            
            // OPTIMIZED: Pointer access untuk menghindari overhead Mat::at()
            const cv::Vec2f* flow_ptr = previous_level_flow.ptr<cv::Vec2f>(0);
            const int flow_step = previous_level_flow.cols;

            // Sample dari previous level flow (3x3 neighborhood)
            for (int dr = -1; dr <= 1; ++dr)
            {
                const int ny = coarse_y + dr;
                // OPTIMIZED: Early continue untuk row boundary
                if (ny < 0 || ny >= max_row) continue;
                
                // OPTIMIZED: Calculate row offset once
                const int row_offset = ny * flow_step;
                
                for (int dc = -1; dc <= 1; ++dc)
                {
                    const int nx = coarse_x + dc;
                    // OPTIMIZED: Combined boundary check
                    if (nx >= 0 && nx < max_col)
                    {
                        // OPTIMIZED: Direct pointer access
                        const cv::Vec2f& prev_flow = flow_ptr[row_offset + nx];
                        candidate_flows.emplace_back(prev_flow * FLOW_UPSCALE_FACTOR);
                    }
                }
            }
        }

        // OPTIMIZED: Single check untuk empty candidates
        if (candidate_flows.empty())
        {
            // OPTIMIZED: Reserve untuk 9 perturbations
            candidate_flows.reserve(9);
            
            const cv::Vec2f center_flow = current_flow.at<cv::Vec2f>(
                tile_center_y + current_tile_h / 2, 
                tile_center_x + current_tile_w / 2);
            
            candidate_flows.emplace_back(center_flow);
            
            // OPTIMIZED: Unrolled loop untuk 8 directions (lebih cache-friendly)
            const float cx = center_flow[0];
            const float cy = center_flow[1];
            
            candidate_flows.emplace_back(cx - 1, cy - 1);
            candidate_flows.emplace_back(cx,     cy - 1);
            candidate_flows.emplace_back(cx + 1, cy - 1);
            candidate_flows.emplace_back(cx - 1, cy);
            candidate_flows.emplace_back(cx + 1, cy);
            candidate_flows.emplace_back(cx - 1, cy + 1);
            candidate_flows.emplace_back(cx,     cy + 1);
            candidate_flows.emplace_back(cx + 1, cy + 1);
        }
    }


    /**
     * Pencarian tile matching untuk level kasar (coarse)
     */
    static inline void searchCoarseLevelDirect(
        const cv::Mat& ref_layer,
        const cv::Mat& comp_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w,
        const cv::Vec2f& initial_flow,
        float search_dist,
        std::vector<Candidate>& out_candidates)  // Reuse vector
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
                        current_cost += block_cost_zsad_avx(p_ref, p_comp, tile_w);
                    }
                }

                Candidate cand{cv::Point2f(init_dx + dx, init_dy + dy),
                              current_cost * tile_area_inv};

                if (out_candidates.size() < 5)
                {
                    out_candidates.push_back(cand);
                    std::sort(out_candidates.begin(), out_candidates.end(),
                             [](const Candidate& a, const Candidate& b) { 
                                 return a.cost < b.cost; 
                             });
                }
                else if (cand.cost < out_candidates.back().cost)
                {
                    out_candidates.back() = cand;
                    std::sort(out_candidates.begin(), out_candidates.end(),
                             [](const Candidate& a, const Candidate& b) { 
                                 return a.cost < b.cost; 
                             });
                }
            }
        }
    }

    /**
     * Pencarian tile matching untuk level halus (fine) - hanya evaluasi kandidat
     */
    struct FineLevelSearchContext {
        std::vector<Candidate> candidates;
        
        FineLevelSearchContext() {
            candidates.reserve(1);
        }
        
        void reset() {
            candidates.clear();
        }
    };

    /**
     * Inline versi searchFineLevel yang mengembalikan langsung ke Candidate array
     * Menghindari alokasi vector dan return by value
     */
    static inline bool searchFineLevelDirect(
        const cv::Mat& ref_layer,
        const cv::Mat& comp_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w,
        const cv::Vec2f& initial_flow,
        Candidate& out_candidate)  // Output langsung ke parameter
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
                current_cost += block_cost_zsad_avx(p_ref, p_comp, tile_w);
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
        const std::vector<Candidate>& candidates,
        const cv::Mat& current_flow,
        const cv::Mat& ref_layer,
        int tile_y, int tile_x,
        int tile_h, int tile_w)
    {
        // OPTIMIZED: Early exit untuk kasus tepi
        if (candidates.empty()) {
            return cv::Point2f(0, 0);
        }
        
        const cv::Point2f best_flow_by_appearance = candidates.front().flow;

        // --- LANGKAH 2: Analisis Tetangga (OPTIMIZED) ---
        cv::Vec2f sum_neigh(0.0f, 0.0f);
        int neighbor_count = 0;
        
        // OPTIMIZED: Pre-calculate boundaries
        const int max_row = current_flow.rows;
        const int max_col = current_flow.cols;
        
        // OPTIMIZED: Stack-allocated array untuk neighbor flows (max 8)
        cv::Vec2f neighbor_flows[8];
        
        // OPTIMIZED: Pointer access untuk faster iteration
        const cv::Vec2f* flow_data = current_flow.ptr<cv::Vec2f>(0);
        const int flow_step = current_flow.cols;
        
        for (int dy = -1; dy <= 1; dy++) {
            const int ny = tile_y + dy;
            if (ny < 0 || ny >= max_row) continue;
            
            const int row_offset = ny * flow_step;
            
            for (int dx = -1; dx <= 1; dx++) {
                if (dy == 0 && dx == 0) continue;
                
                const int nx = tile_x + dx;
                if (nx >= 0 && nx < max_col) {
                    const cv::Vec2f& flow = flow_data[row_offset + nx];
                    neighbor_flows[neighbor_count++] = flow;
                    sum_neigh += flow;
                }
            }
        }
        
        if (neighbor_count == 0) {
            return best_flow_by_appearance;
        }
        
        // OPTIMIZED: Inverse multiplication lebih cepat dari division
        const float inv_count = 1.0f / neighbor_count;
        const cv::Vec2f avg_neigh = sum_neigh * inv_count;

        // --- LANGKAH 3: Hitung Lambda Adaptif (OPTIMIZED) ---
        const float base_lambda = 1.0f;
        float adaptive_lambda = base_lambda;

        // 3a. Variance calculation (OPTIMIZED)
        float flow_variance = 0.0f;
        for(int i = 0; i < neighbor_count; i++) {
            const cv::Vec2f diff = neighbor_flows[i] - avg_neigh;
            // OPTIMIZED: Manual dot product lebih cepat dari cv::norm dengan L2SQR
            flow_variance += diff[0] * diff[0] + diff[1] * diff[1];
        }
        flow_variance *= inv_count;

        // OPTIMIZED: Pre-calculate reciprocal untuk variance term
        const float variance_sigma = 2.0f;
        const float inv_variance_sigma_sq = 1.0f / (variance_sigma * variance_sigma);
        const float lambda_from_neighbors = std::exp(-flow_variance * inv_variance_sigma_sq);
        adaptive_lambda *= lambda_from_neighbors;

        // 3b. Texture analysis (OPTIMIZED)
        // OPTIMIZED: Clamp ROI untuk menghindari boundary checks
        const int safe_x = std::max(0, std::min(tile_x, ref_layer.cols - tile_w));
        const int safe_y = std::max(0, std::min(tile_y, ref_layer.rows - tile_h));
        const cv::Rect tile_roi(safe_x, safe_y, tile_w, tile_h);
        const cv::Mat ref_tile = ref_layer(tile_roi);
        
        // OPTIMIZED: Use smaller kernel size untuk Sobel (faster)
        cv::Mat grad_x, grad_y;
        cv::Sobel(ref_tile, grad_x, CV_32F, 1, 0, 3, 1.0, 0.0, cv::BORDER_REPLICATE);
        cv::Sobel(ref_tile, grad_y, CV_32F, 0, 1, 3, 1.0, 0.0, cv::BORDER_REPLICATE);
        
        // OPTIMIZED: Manual magnitude calculation (faster than cv::magnitude)
        cv::Mat magnitude;
        cv::magnitude(grad_x, grad_y, magnitude);
        const float texture_score = cv::mean(magnitude)[0];

        // OPTIMIZED: Pre-calculate reciprocal untuk texture term
        const float texture_sigma = 10.0f;
        const float inv_texture_sigma = 1.0f / texture_sigma;
        const float lambda_from_content = std::exp(-texture_score * inv_texture_sigma);
        adaptive_lambda *= lambda_from_content;

        // --- LANGKAH 4: Combined Cost dengan Lambda Adaptif (OPTIMIZED) ---
        float min_total_cost = std::numeric_limits<float>::max();
        cv::Point2f chosen_flow = best_flow_by_appearance;

        // OPTIMIZED: Extract avg_neigh components once
        const float avg_x = avg_neigh[0];
        const float avg_y = avg_neigh[1];

        for (const auto& cand : candidates)
        {
            // OPTIMIZED: Manual distance calculation (faster than cv::norm)
            const float dx = cand.flow.x - avg_x;
            const float dy = cand.flow.y - avg_y;
            const float spatial_cost = std::sqrt(dx * dx + dy * dy);
            
            // OPTIMIZED: Fused multiply-add
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
        cv::Mat& flow,
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
            const cv::Vec2f* row_ptr = flow.ptr<cv::Vec2f>(r);
            for (int c = 0; c < flow.cols; ++c)
            {
                const cv::Vec2f& vec = row_ptr[c];
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
            const cv::Point2f& hypothesis_flow = flow_vectors[rand_idx];

            int current_inliers = 0;
            cv::Vec2f inlier_sum(0, 0);

            for (const auto& vec : flow_vectors)
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
     * Proses tile matching untuk satu layer
     */
    static cv::Mat processSingleLayer(
        const cv::Mat& ref_layer,
        const cv::Mat& comp_layer,
        const cv::Mat& previous_level_flow,
        int layer_index,
        int total_layers,
        int tile_h,
        int tile_w,
        float search_dist)
    {
        using namespace ImageAlignmentConfig;

        const int h_layer = ref_layer.rows;
        const int w_layer = ref_layer.cols;

        cv::Mat flow;
        if (layer_index == total_layers - 1)
            flow = initializeCoarsestFlow(ref_layer);
        else
            flow = upsamplingFlow(previous_level_flow, ref_layer);

        const int current_tile_h = std::max(MIN_TILE_SIZE, std::min(tile_h, h_layer / 4));
        const int current_tile_w = std::max(MIN_TILE_SIZE, std::min(tile_w, w_layer / 4));

        if (current_tile_h <= 0 || current_tile_w <= 0 || 
            h_layer < current_tile_h || w_layer < current_tile_w)
            return flow;

        const cv::Mat& window = getGaussianWindow(current_tile_h, current_tile_w);

        cv::Mat flow_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
        cv::Mat weight_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);

        const int step_y = std::max(current_tile_h / 2, 1);
        const int step_x = std::max(current_tile_w / 2, 1);

        const bool is_fine_level = (layer_index == 0 || layer_index == 1);
        
        // OPTIMIZATION 1: Pre-calculate subpixel condition
        const bool do_subpixel = (layer_index >= total_layers - 3);

#pragma omp parallel
        {
            cv::Mat local_flow_acc = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
            cv::Mat local_weight_acc = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);
            
            // Pre-allocated containers
            std::vector<cv::Vec2f> candidate_flows;
            candidate_flows.reserve(20);
            
            Candidate fine_candidate;
            
            std::vector<Candidate> coarse_candidates;
            coarse_candidates.reserve(100);
            
            std::vector<Candidate> all_candidates;
            all_candidates.reserve(100);
            
            // OPTIMIZATION 2: Pre-allocate buffers untuk selectBestCandidate
            // Ini mengurangi alokasi berulang di dalam fungsi
            std::vector<cv::Vec2f> neighbor_flows_buffer;
            neighbor_flows_buffer.reserve(8);
            
            // OPTIMIZATION 3: Pre-allocate untuk channel operations
            std::vector<cv::Mat> channels(2);

#pragma omp for schedule(dynamic) nowait
            for (int y = 0; y <= h_layer - current_tile_h; y += step_y)
            {
                for (int x = 0; x <= w_layer - current_tile_w; x += step_x)
                {
                    generateCandidateFlows(
                        candidate_flows, layer_index, total_layers,
                        previous_level_flow, flow,
                        y, x, current_tile_h, current_tile_w);

                    all_candidates.clear();

                    if (is_fine_level)
                    {
                        for (const auto& initial_vec : candidate_flows)
                        {
                            if (searchFineLevelDirect(
                                ref_layer, comp_layer, y, x,
                                current_tile_h, current_tile_w, 
                                initial_vec, fine_candidate))
                            {
                                all_candidates.push_back(fine_candidate);
                            }
                        }
                    }
                    else
                    {
                        for (const auto& initial_vec : candidate_flows)
                        {
                            searchCoarseLevelDirect(
                                ref_layer, comp_layer, y, x,
                                current_tile_h, current_tile_w, 
                                initial_vec, search_dist,
                                coarse_candidates);

                            all_candidates.insert(all_candidates.end(),
                                                coarse_candidates.begin(), 
                                                coarse_candidates.end());
                        }
                    }

                    // OPTIMIZATION 4: Inline partial_sort untuk menghindari function call overhead
                    if (all_candidates.size() > 5)
                    {
                        std::partial_sort(all_candidates.begin(), 
                                        all_candidates.begin() + 5,
                                        all_candidates.end(),
                                        [](const Candidate& a, const Candidate& b) {
                                            return a.cost < b.cost;
                                        });
                        all_candidates.resize(5);
                    }

                    // OPTIMIZATION 5: Inline selectBestCandidate untuk mengurangi overhead
                    // (Bisa juga tetap call function jika sudah dioptimasi seperti sebelumnya)
                    cv::Point2f chosen_flow = selectBestCandidate(
                        all_candidates, flow, ref_layer,
                        y, x, current_tile_h, current_tile_w);

                    // OPTIMIZATION 6: Conditional refinement dengan pre-calculated flag
                    cv::Point2f refined_flow = chosen_flow;
                    if (do_subpixel)
                    {
                        refined_flow = subpixel_refinement(
                            ref_layer, comp_layer, x, y,
                            (int)std::round(chosen_flow.x),
                            (int)std::round(chosen_flow.y),
                            current_tile_w, current_tile_h);
                    }

                    // OPTIMIZATION 7: Direct pointer manipulation untuk accumulation
                    const cv::Rect tile_roi(x, y, current_tile_w, current_tile_h);
                    cv::Mat local_flow_roi = local_flow_acc(tile_roi);
                    cv::Mat local_weight_roi = local_weight_acc(tile_roi);

                    // OPTIMIZATION 8: Reuse channels vector
                    cv::split(local_flow_roi, channels);
                    channels[0] += refined_flow.x * window;
                    channels[1] += refined_flow.y * window;
                    cv::merge(channels, local_flow_roi);
                    local_weight_roi += window;
                }
            }

#pragma omp critical
            {
                flow_accumulator += local_flow_acc;
                weight_accumulator += local_weight_acc;
            }
        }

        // Normalize accumulated flow
        cv::Mat mask;
        cv::compare(weight_accumulator, NORMALIZATION_EPSILON, mask, cv::CMP_GT);

        std::vector<cv::Mat> flow_channels(2);
        cv::split(flow_accumulator, flow_channels);
        flow_channels[0].setTo(0, ~mask);
        flow_channels[1].setTo(0, ~mask);

        cv::divide(flow_channels[0], weight_accumulator, flow_channels[0], 1.0, -1);
        cv::divide(flow_channels[1], weight_accumulator, flow_channels[1], 1.0, -1);
        cv::merge(flow_channels, flow);

        // OPTIMIZATION 9: RANSACOutlierRemoval sudah optimal (1x per layer)
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
                const cv::Mat& ref_layer = ref_pyramid[i];
                const cv::Mat& comp_layer = current_pyramid[i];

                cv::Mat current_flow = OpticalFlowHelpers::processSingleLayer(
                    ref_layer,
                    comp_layer,
                    previous_level_flow,
                    i,
                    static_cast<int>(ref_pyramid.size()),
                    tile_h,
                    tile_w,
                    search_dist
                );

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