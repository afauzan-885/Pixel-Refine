#include "alignment_tile.h"
#include <opencv2/imgproc.hpp>
#include <opencv2/ximgproc/segmentation.hpp>
#include <vector>
#include <cmath>
#include <numeric>
#include <immintrin.h>
#include <map>
#include <algorithm>
#include <functional>
#include <omp.h>
#include <iostream> // Diperlukan untuk std::cout
#include <chrono>   // Diperlukan untuk timing
#include <string>

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

// Zero-Mean SAD dengan AVX
inline float block_cost_zsad_avx(const float* ref, const float* comp, int len)
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

static inline float bilinear_at(const cv::Mat &img, float x, float y)
{
    int x0 = (int)std::floor(x);
    int y0 = (int)std::floor(y);
    int x1 = x0 + 1;
    int y1 = y0 + 1;

    // clamp supaya tidak keluar range
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 >= img.cols) x1 = img.cols - 1;
    if (y1 >= img.rows) y1 = img.rows - 1;

    float dx = x - x0;
    float dy = y - y0;

    float v00 = img.at<float>(y0, x0);
    float v01 = img.at<float>(y0, x1);
    float v10 = img.at<float>(y1, x0);
    float v11 = img.at<float>(y1, x1);

    float v0 = v00 * (1 - dx) + v01 * dx;
    float v1 = v10 * (1 - dx) + v11 * dx;
    return v0 * (1 - dy) + v1 * dy;
}

static cv::Point2f subpixel_refinement(const cv::Mat &ref_layer,
                                      const cv::Mat &comp_layer,
                                      int x,
                                      int y,
                                      int dx,
                                      int dy,
                                      int tile_w,
                                      int tile_h)
{
    cv::Rect ref_roi(x, y, tile_w, tile_h);
    cv::Rect comp_roi(x + dx, y + dy, tile_w, tile_h);

    if ((ref_roi.x < 0) || (ref_roi.y < 0) || (comp_roi.x < 0) || (comp_roi.y < 0) ||
        (ref_roi.x + comp_roi.width > comp_layer.cols) ||
        (ref_roi.y + comp_roi.height > comp_layer.rows))
    {
        return cv::Point2f((float)dx, (float)dy);
    }

    cv::Mat ref_tile = ref_layer(ref_roi).clone();
    cv::Mat comp_tile = comp_layer(comp_roi).clone();

    cv::Point2d shift;
    double response;
    shift = cv::phaseCorrelate(ref_tile, comp_tile, cv::noArray(), &response);

    float fx = (float)dx + (float)shift.x;
    float fy = (float)dy + (float)shift.y;

    float sad_bilinear = 0.0f;
    for (int r = 0; r < tile_h; r++)
    {
        const float *p_ref = ref_tile.ptr<float>(r);
        for (int c = 0; c < tile_w; c++)
        {
            float ref_val = p_ref[c];
            float comp_val = bilinear_at(comp_layer, (float)(x + dx + shift.x + c), (float)(y + dy + shift.y + r));
            sad_bilinear += std::fabs(ref_val - comp_val);
        }
    }
    sad_bilinear /= (tile_w * tile_h);

    if (sad_bilinear > 1e5f)
    {
        return cv::Point2f((float)dx + (float)shift.x, (float)dy + (float)shift.y);
    }

    return cv::Point2f(fx, fy);
}


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

float block_cost(const float *ref, const float *comp, int len)
{
    __m256 vsum = _mm256_setzero_ps();
    int i = 0;
    for (; i + 8 <= len; i += 8)
    {
        __m256 vref = _mm256_loadu_ps(ref + i);
        __m256 vcomp = _mm256_loadu_ps(comp + i);
        __m256 vdiff = _mm256_sub_ps(vref, vcomp);
        __m256 vabs = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), vdiff); // abs()
        vsum = _mm256_add_ps(vsum, vabs);
    }
    float buf[8];
    _mm256_storeu_ps(buf, vsum);
    float total = buf[0] + buf[1] + buf[2] + buf[3] + buf[4] + buf[5] + buf[6] + buf[7];

    // tail handling
    for (; i < len; i++)
    {
        total += std::fabs(ref[i] - comp[i]);
    }
    return total;
}

// === API Fungsi yang Diekspos (C-Linkage)
extern "C"
{
    namespace ImageAlignmentConfig
    {
        constexpr int MIN_PYRAMID_LAYER_SIZE = 16;
        constexpr int MIN_TILE_SIZE = 8;
        constexpr float FLOW_UPSCALE_FACTOR = 2.0f;
        constexpr float NORMALIZATION_EPSILON = 1e-6f;
        constexpr int GAUSSIAN_CACHE_SIZE = 64; // Batasi cache untuk menghemat memori

        // Scaling factor untuk search distance per level
        constexpr float SEARCH_DIST_SCALE_L0 = 1.0f; // Level 0 â†’ 75% dari search_dist asli
        constexpr float SEARCH_DIST_SCALE_L1 = 1.0f; // Level 1 â†’ 90% 
    }

    struct Candidate
    {
        cv::Point2f flow;
        float cost;
    };

    ALIGNMENT_API float *compute_alignment_flow(
        const float *ref_work_data, const float *current_work_data,
        int work_h, int work_w, int tile_h, int tile_w, int n_layers, float search_dist)
    {
        // SimpleTimer total_timer("Total Alignment Flow Computation");
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
            // SimpleTimer pyramid_timer("Pyramid Construction");
            ref_pyramid.reserve(n_layers);
            current_pyramid.reserve(n_layers);

            ref_pyramid.push_back(ref_work);
            current_pyramid.push_back(current_work);

            cv::Mat temp_ref, temp_current;
            for (int i = 0; i < n_layers - 1; ++i)
            {
                cv::pyrDown(ref_pyramid.back(), temp_ref);
                cv::pyrDown(current_pyramid.back(), temp_current);

                if (temp_ref.rows < MIN_PYRAMID_LAYER_SIZE || temp_ref.cols < MIN_PYRAMID_LAYER_SIZE)
                    break;

                ref_pyramid.push_back(temp_ref.clone());
                current_pyramid.push_back(temp_current.clone());
            }
        }

        // =========================================================================
        // === BAGIAN C: Perhitungan Optical Flow (Coarse-to-Fine) OPTIMIZED   ===
        // =========================================================================
        cv::Mat flow;
        cv::Mat previous_level_flow;

        static thread_local std::map<std::pair<int, int>, cv::Mat> gaussian_cache;

        auto getGaussianWindow_optimized = [](int rows, int cols) -> const cv::Mat &
        {
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
        };

        cv::Mat flow_accumulator, weight_accumulator;
        std::vector<cv::Vec2f> candidate_flows;
        candidate_flows.reserve(20);

        {
            // SimpleTimer all_levels_timer("Coarse-to-Fine Flow (All Levels)");
            for (int i = static_cast<int>(ref_pyramid.size()) - 1; i >= 0; --i)
            {
                const cv::Mat &ref_layer = ref_pyramid[i];
                const cv::Mat &comp_layer = current_pyramid[i];

                if (i == ref_pyramid.size() - 1)
                    flow = cv::Mat::zeros(ref_layer.size(), CV_32FC2);
                else
                {
                    cv::resize(previous_level_flow, flow, ref_layer.size(), 0, 0, cv::INTER_LINEAR);
                    flow *= FLOW_UPSCALE_FACTOR;
                }

                const int h_layer = ref_layer.rows;
                const int w_layer = ref_layer.cols;
                const int current_tile_h = std::max(MIN_TILE_SIZE, std::min(tile_h, h_layer / 4));
                const int current_tile_w = std::max(MIN_TILE_SIZE, std::min(tile_w, w_layer / 4));

                if (current_tile_h <= 0 || current_tile_w <= 0 || h_layer < current_tile_h || w_layer < current_tile_w)
                {
                    previous_level_flow = std::move(flow);
                    continue;
                }

                const cv::Mat &window = getGaussianWindow_optimized(current_tile_h, current_tile_w);
                
                // ================================================================================
// ========================= MULAI PERUBAHAN DI SINI ==============================
// ================================================================================

                // [BARU] TAHAP 1: Pra-Kalkulasi Peta Konteks (Segmentation)
                cv::Mat context_map;
                if (i <= 1) { 
                    // Pastikan ukuran gambar bisa dibagi 2
                    int half_w = ref_layer.cols / 2;
                    int half_h = ref_layer.rows / 2;

                    // Buat gambar hasil akhir
                    context_map = cv::Mat(ref_layer.size(), CV_32SC1);

                    int max_label_offset = 0; // Untuk melacak ID segmen maksimum

                    // Kita akan memproses 4 kuadran
                    cv::Rect rois[4] = {
                        cv::Rect(0, 0, half_w, half_h),
                        cv::Rect(half_w, 0, ref_layer.cols - half_w, half_h),
                        cv::Rect(0, half_h, half_w, ref_layer.rows - half_h),
                        cv::Rect(half_w, half_h, ref_layer.cols - half_w, ref_layer.rows - half_h)
                    };

                    // Vektor untuk menyimpan hasil sementara
                    std::vector<cv::Mat> sub_maps(4);

                    // Gunakan OpenMP untuk memparalelkan 4 tugas ini
                    #pragma omp parallel for
                    for (int k = 0; k < 4; ++k) {
                        cv::Mat sub_image = ref_layer(rois[k]);
                        
                        cv::Mat sub_image_8uc3;
                        sub_image.convertTo(sub_image_8uc3, CV_8U, 255.0);
                        cv::cvtColor(sub_image_8uc3, sub_image_8uc3, cv::COLOR_GRAY2BGR);

                        cv::Ptr<cv::ximgproc::segmentation::GraphSegmentation> gs = 
                            cv::ximgproc::segmentation::createGraphSegmentation();
                        gs->setSigma(0.5);
                        gs->setK(300);
                        gs->setMinSize(sub_image.rows * sub_image.cols / 100);

                        gs->processImage(sub_image_8uc3, sub_maps[k]);
                    }

                    // --- Penggabungan dan Re-labeling (Single-threaded) ---
                    // Kuadran 1 (Kiri Atas)
                    sub_maps[0].copyTo(context_map(rois[0]));
                    double minVal, maxVal;
                    cv::minMaxLoc(sub_maps[0], &minVal, &maxVal);
                    max_label_offset = (int)maxVal + 1;

                    // Kuadran 2 (Kanan Atas)
                    cv::Mat temp_map_1 = sub_maps[1] + max_label_offset; // Hitung dan simpan ke Mat sementara
                    temp_map_1.copyTo(context_map(rois[1]));            // Sekarang copyTo akan berhasil
                    cv::minMaxLoc(sub_maps[1], &minVal, &maxVal);
                    max_label_offset += (int)maxVal + 1;

                    // Kuadran 3 (Kiri Bawah)
                    cv::Mat temp_map_2 = sub_maps[2] + max_label_offset;
                    temp_map_2.copyTo(context_map(rois[2]));
                    cv::minMaxLoc(sub_maps[2], &minVal, &maxVal);
                    max_label_offset += (int)maxVal + 1;

                    // Kuadran 4 (Kanan Bawah)
                    cv::Mat temp_map_3 = sub_maps[3] + max_label_offset;
                    temp_map_3.copyTo(context_map(rois[3]));
                }

                {
                    // SimpleTimer tile_matching_timer("  -> Level " + std::to_string(i) + " Tile Matching");

                    if (flow_accumulator.size() != cv::Size(w_layer, h_layer))
                    {
                        flow_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
                        weight_accumulator = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);
                    }
                    else
                    {
                        flow_accumulator.setTo(cv::Scalar::all(0));
                        weight_accumulator.setTo(cv::Scalar::all(0));
                    }

                    const int step_y = std::max(current_tile_h / 2, 1);
                    const int step_x = std::max(current_tile_w / 2, 1);
                    const float tile_area_inv = 1.0f / static_cast<float>(current_tile_h * current_tile_w);

                    // [BARU] Peta untuk menyimpan alur dominan per segmen
                    std::map<int, cv::Vec2f> segment_dominant_flow;
                    
                    // [BARU] Pre-computation pass untuk alur dominan jika `context_map` ada
                    if (!context_map.empty()) {
                        std::map<int, std::vector<cv::Vec2f>> all_segment_flows;
                        // Kumpulkan semua alur per segmen
                        for (int r = 0; r < h_layer - current_tile_h; r += step_y) {
                             for (int c = 0; c < w_layer - current_tile_w; c += step_x) {
                                int segment_id = context_map.at<int>(r + current_tile_h/2, c + current_tile_w/2);
                                all_segment_flows[segment_id].push_back(flow.at<cv::Vec2f>(r,c));
                             }
                        }
                        // Hitung median untuk setiap segmen
                        for (auto const& [seg_id, flows] : all_segment_flows) {
                            if (flows.size() > 3) {
                                std::vector<cv::Vec2f> sorted_flows = flows;
                                std::sort(sorted_flows.begin(), sorted_flows.end(), [](const cv::Vec2f& a, const cv::Vec2f& b){ return a[0] < b[0]; });
                                float median_x = sorted_flows[sorted_flows.size()/2][0];
                                std::sort(sorted_flows.begin(), sorted_flows.end(), [](const cv::Vec2f& a, const cv::Vec2f& b){ return a[1] < b[1]; });
                                float median_y = sorted_flows[sorted_flows.size()/2][1];
                                segment_dominant_flow[seg_id] = cv::Vec2f(median_x, median_y);
                            }
                        }
                    }

#pragma omp parallel firstprivate(candidate_flows)
                    {
                        cv::Mat local_flow_acc = cv::Mat::zeros(h_layer, w_layer, CV_32FC2);
                        cv::Mat local_weight_acc = cv::Mat::zeros(h_layer, w_layer, CV_32FC1);

#pragma omp for schedule(dynamic) nowait
                        for (int y = 0; y <= h_layer - current_tile_h; y += step_y)
                        {
                            for (int x = 0; x <= w_layer - current_tile_w; x += step_x)
                            {
                                candidate_flows.clear();
                                if (i == ref_pyramid.size() - 1)
                                    candidate_flows.emplace_back(0.0f, 0.0f);
                                else
                                {
                                    const int coarse_y = static_cast<int>((y + current_tile_h * 0.5f) * 0.5f);
                                    const int coarse_x = static_cast<int>((x + current_tile_w * 0.5f) * 0.5f);

                                    for (int dr = -1; dr <= 1; ++dr)
                                    {
                                        for (int dc = -1; dc <= 1; ++dc)
                                        {
                                            const int ny = coarse_y + dr;
                                            const int nx = coarse_x + dc;
                                            if (ny >= 0 && ny < previous_level_flow.rows &&
                                                nx >= 0 && nx < previous_level_flow.cols)
                                            {
                                                const cv::Vec2f &prev_flow = previous_level_flow.at<cv::Vec2f>(ny, nx);
                                                candidate_flows.emplace_back(prev_flow * FLOW_UPSCALE_FACTOR);
                                            }
                                        }
                                    }
                                }

                                if (candidate_flows.empty())
                                {
                                    cv::Vec2f center_flow = flow.at<cv::Vec2f>(y + current_tile_h / 2, x + current_tile_w / 2);
                                    candidate_flows.emplace_back(center_flow);
                                    for (int dy = -1; dy <= 1; ++dy)
                                    {
                                        for (int dx = -1; dx <= 1; ++dx)
                                        {
                                            if (dx == 0 && dy == 0)
                                                continue;
                                            candidate_flows.emplace_back(center_flow + cv::Vec2f(dx, dy));
                                        }
                                    }
                                }

                                // === MODIFIKASI MULTI-KANDIDAT ===
                                std::vector<Candidate> top_candidates;
                                top_candidates.reserve(5);

                                for (const auto &initial_vec : candidate_flows)
                                {
                                    const int init_dy = static_cast<int>(std::round(initial_vec[1]));
                                    const int init_dx = static_cast<int>(std::round(initial_vec[0]));

                                    // === [NEW] Adaptive search distance ===
                                    float base_dist = search_dist;
                                    if (i == 0) base_dist *= ImageAlignmentConfig::SEARCH_DIST_SCALE_L0;
                                    else if (i == 1) base_dist *= ImageAlignmentConfig::SEARCH_DIST_SCALE_L1;

                                    float flow_mag = std::sqrt(initial_vec[0] * initial_vec[0] + initial_vec[1] * initial_vec[1]);
                                    int current_search_dist = static_cast<int>(
                                        base_dist * (1.0f + 0.5f * std::min(flow_mag / 5.0f, 2.0f))
                                    );
                                    current_search_dist = std::max(1, std::min(current_search_dist, (int)search_dist));

                                    for (int dy = -current_search_dist; dy <= current_search_dist; ++dy)
                                    {
                                        for (int dx = -current_search_dist; dx <= current_search_dist; ++dx)

                                        {
                                            const int test_y = y + init_dy + dy;
                                            const int test_x = x + init_dx + dx;
                                            if (test_y < 0 || test_x < 0 ||
                                                test_y + current_tile_h > h_layer ||
                                                test_x + current_tile_w > w_layer)
                                                continue;

                                            float current_cost = 0.0f;
                                            if (current_tile_h * current_tile_w >= 64 * 64)
                                            {
                                                cv::Mat ref_tile(ref_layer, cv::Rect(x, y, current_tile_w, current_tile_h));
                                                cv::Mat comp_tile(comp_layer, cv::Rect(test_x, test_y, current_tile_w, current_tile_h));
                                                current_cost = block_cost_fft(ref_tile, comp_tile);
                                            }
                                            else
                                            {
                                                for (int r_tile = 0; r_tile < current_tile_h; ++r_tile)
                                                {
                                                    const float *p_ref = ref_layer.ptr<float>(y + r_tile, x);
                                                    const float *p_comp = comp_layer.ptr<float>(test_y + r_tile, test_x);
                                                    current_cost += block_cost_zsad_avx(p_ref, p_comp, current_tile_w);
                                                }
                                            }

                                            Candidate cand{cv::Point2f(init_dx + dx, init_dy + dy),
                                                           current_cost * tile_area_inv};

                                            if (top_candidates.size() < 5)
                                            {
                                                top_candidates.push_back(cand);
                                                std::sort(top_candidates.begin(), top_candidates.end(),
                                                          [](const Candidate &a, const Candidate &b)
                                                          { return a.cost < b.cost; });
                                            }
                                            else if (cand.cost < top_candidates.back().cost)
                                            {
                                                top_candidates.back() = cand;
                                                std::sort(top_candidates.begin(), top_candidates.end(),
                                                          [](const Candidate &a, const Candidate &b)
                                                          { return a.cost < b.cost; });
                                            }
                                        }
                                    }
                                }

                                cv::Point2f chosen_flow = top_candidates.front().flow;
                                
                                // [MODIFIKASI] TAHAP 2: Pemilihan Kandidat Berbasis Konteks
                                if (top_candidates.size() > 1 && x > 0 && y > 0)
                                {
                                    // 2a. Hitung Konsistensi Lokal (Kode Anda)
                                    cv::Vec2f avg_neigh(0.0f, 0.0f);
                                    int count = 0;
                                    // Loop ini seharusnya menggunakan step_y dan step_x untuk efisiensi
                                    for (int dy_n = -1; dy_n <= 1; dy_n++) {
                                        for (int dx_n = -1; dx_n <= 1; dx_n++) {
                                            if (dy_n == 0 && dx_n == 0) continue;
                                            int ny = y + dy_n * step_y;
                                            int nx = x + dx_n * step_x;
                                            if (ny >= 0 && ny < h_layer && nx >= 0 && nx < w_layer) {
                                                avg_neigh += flow.at<cv::Vec2f>(ny, nx);
                                                count++;
                                            }
                                        }
                                    }
                                    if (count > 0) avg_neigh *= (1.0f / count);

                                    // 2b. Dapatkan Konsistensi Kontekstual/Global
                                    cv::Vec2f context_flow = avg_neigh; // Fallback ke alur lokal
                                    if (!context_map.empty()) {
                                        int segment_id = context_map.at<int>(y + current_tile_h / 2, x + current_tile_w / 2);
                                        auto it = segment_dominant_flow.find(segment_id);
                                        if (it != segment_dominant_flow.end()) {
                                            context_flow = it->second;
                                        }
                                    }
                                    
                                    // 2c. Gabungkan Alur dan Pilih Kandidat Terbaik
                                    const float context_weight = 0.5f;
                                    cv::Vec2f target_flow = (1.0f - context_weight) * avg_neigh + context_weight * context_flow;

                                    float best_dist = 1e9f;
                                    for (const auto &cand : top_candidates)
                                    {
                                        cv::Vec2f cand_vec(cand.flow.x, cand.flow.y);
                                        float d = cv::norm(cand_vec - target_flow);
                                        if (d < best_dist)
                                        {
                                            best_dist = d;
                                            chosen_flow = cand.flow;
                                        }
                                    }
                                }


                                cv::Point2f refined_flow = chosen_flow;
                                if (i >= (int)ref_pyramid.size() - 3)
                                {
                                    refined_flow = subpixel_refinement(
                                        ref_layer, comp_layer,
                                        x, y,
                                        (int)std::round(chosen_flow.x),
                                        (int)std::round(chosen_flow.y),
                                        current_tile_w, current_tile_h);
                                }

                                cv::Rect tile_roi(x, y, current_tile_w, current_tile_h);
                                cv::Mat local_flow_roi = local_flow_acc(tile_roi);
                                cv::Mat local_weight_roi = local_weight_acc(tile_roi);

                                std::vector<cv::Mat> channels(2);
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

                    cv::Mat mask;
                    cv::compare(weight_accumulator, NORMALIZATION_EPSILON, mask, cv::CMP_GT);

                    std::vector<cv::Mat> flow_channels(2);
                    cv::split(flow_accumulator, flow_channels);
                    flow_channels[0].setTo(0, ~mask);
                    flow_channels[1].setTo(0, ~mask);

                    cv::divide(flow_channels[0], weight_accumulator, flow_channels[0], 1.0, -1);
                    cv::divide(flow_channels[1], weight_accumulator, flow_channels[1], 1.0, -1);
                    cv::merge(flow_channels, flow);
                }

                // === RANSAC tetap sama ===
                if (i >= static_cast<int>(ref_pyramid.size()) - 2)
                {
                    // SimpleTimer ransac_timer("  -> Level " + std::to_string(i) + " RANSAC");
                    static thread_local std::vector<cv::Point2f> flow_vectors;
                    flow_vectors.clear();
                    flow_vectors.reserve(flow.total() / 4);

                    const float min_magnitude = std::max(0.1f, static_cast<float>(std::min(h_layer, w_layer)) * 0.001f);

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

                    if (flow_vectors.size() > 20)
                    {
                        const float distance_threshold = 1.5f;
                        const int min_inliers_needed = static_cast<int>(flow_vectors.size() * 0.5);
                        const int max_iterations = std::min(100, static_cast<int>(flow_vectors.size()));

                        cv::Vec2f best_global_flow(0, 0);
                        int max_inliers = 0;
                        const int early_stop_threshold = static_cast<int>(flow_vectors.size() * 0.8);

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
                }

                previous_level_flow = std::move(flow);
                flow = cv::Mat();
            }
        }

        // =========================================================================
        // === BAGIAN D: Finalisasi dan Pengembalian Data (OPTIMIZED)           ===
        // =========================================================================
        float *output_flow_data = nullptr;
        {
            // SimpleTimer finalization_timer("Finalization & Data Copy");
            flow = std::move(previous_level_flow);

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