#include "alignment_tile.h"
#include "cpp/cost_function.hpp"
#include "cpp/refinement.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <functional>
#include <immintrin.h>
#include <iostream>
#include <map>
#include <numeric>
#include <omp.h>
#include <opencv2/imgproc.hpp>
#include <string>
#include <vector>

// =========================================================================
// === PROFILING UTILS ===
// =========================================================================
struct SimpleTimer {
  std::string name;
  std::chrono::high_resolution_clock::time_point start;
  SimpleTimer(const std::string &n)
      : name(n), start(std::chrono::high_resolution_clock::now()) {}
  ~SimpleTimer() {
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> elapsed = end - start;
    std::cout << "[C++ Timer] " << name << ": " << elapsed.count() << " ms\n";
  }
};

// =========================================================================
// === HELPER FUNCTIONS - Static Implementation ===
// =========================================================================

namespace ImageAlignmentConfig {
constexpr float FLOW_UPSCALE_FACTOR = 4.0f; // HDR+ style 4x pyramid
constexpr int MIN_TILE_SIZE = 8;
constexpr int MIN_PYRAMID_LAYER_SIZE = 190;
} // namespace ImageAlignmentConfig

namespace AlignmentFlowHelpers {

static thread_local std::vector<float> ref_tile_buffer_g;
static thread_local std::vector<float> comp_tile_buffer_g;

static inline bool copyTileToContiguousBuffer(const cv::Mat &layer, int tile_y,
                                              int tile_x, int tile_h, int tile_w,
                                              std::vector<float> &buffer) {
  const int tile_area = tile_h * tile_w;
  if (buffer.size() < (size_t)tile_area) {
    buffer.resize(tile_area);
  }

  int buffer_idx = 0;
  for (int r = 0; r < tile_h; ++r) {
    const float *p_row = layer.ptr<float>(tile_y + r) + tile_x;
    std::memcpy(buffer.data() + buffer_idx, p_row, tile_w * sizeof(float));
    buffer_idx += tile_w;
  }
  return true;
}

static inline float compute_zmssd_cost(
    const cv::Mat &ref_layer, const cv::Mat &comp_layer,
    int /*y*/, int /*x*/, int test_y, int test_x,
    int tile_h, int tile_w,
    int /*h*/, int /*w*/, int comp_h, int comp_w) {
    
    if (test_y < 0 || test_x < 0 || test_y + tile_h > comp_h || test_x + tile_w > comp_w) {
        return std::numeric_limits<float>::max();
    }
    
    copyTileToContiguousBuffer(comp_layer, test_y, test_x, tile_h, tile_w, comp_tile_buffer_g);
    return calculate_fine_analysis(ref_tile_buffer_g.data(), comp_tile_buffer_g.data(), tile_h * tile_w);
}

static void _initialize_coarsest_flow_kernel(cv::Mat& flow, int h, int w, float init_dx, float init_dy) {
    flow = cv::Mat(h, w, CV_32FC2, cv::Scalar(init_dx, init_dy));
}

struct RegParams {
    float avg_dx;
    float avg_dy;
    float weight;
};

static inline RegParams _compute_regularization_params(
    const cv::Mat &flow,
    int y, int x,
    int tile_h, int tile_w,
    int h_total, int w_total
) {
    float sum_dx = 0.0f;
    float sum_dy = 0.0f;
    float sum_sq_diff = 0.0f;
    float count = 0.0f;
    
    int step_y = tile_h;
    int step_x = tile_w;
    
    int center_y = y + tile_h / 2;
    int center_x = x + tile_w / 2;
    
    for (int dy = -1; dy <= 1; ++dy) {
        for (int dx = -1; dx <= 1; ++dx) {
            if (dy == 0 && dx == 0) continue;
            
            int ny = center_y + dy * step_y;
            int nx = center_x + dx * step_x;
            
            if (ny >= 0 && ny < h_total && nx >= 0 && nx < w_total) {
                cv::Vec2f val = flow.at<cv::Vec2f>(ny, nx);
                sum_dx += val[0];
                sum_dy += val[1];
                count += 1.0f;
            }
        }
    }
    
    float avg_dx = 0.0f, avg_dy = 0.0f, variance = 0.0f, lambda_val = 1.5f;
    
    if (count > 0.0f) {
        avg_dx = sum_dx / count;
        avg_dy = sum_dy / count;
        
        for (int dy = -1; dy <= 1; ++dy) {
            for (int dx = -1; dx <= 1; ++dx) {
                if (dy == 0 && dx == 0) continue;
                
                int ny = center_y + dy * step_y;
                int nx = center_x + dx * step_x;
                
                if (ny >= 0 && ny < h_total && nx >= 0 && nx < w_total) {
                    cv::Vec2f val = flow.at<cv::Vec2f>(ny, nx);
                    float dist = (val[0] - avg_dx) * (val[0] - avg_dx) + (val[1] - avg_dy) * (val[1] - avg_dy);
                    sum_sq_diff += dist;
                }
            }
        }
        
        variance = sum_sq_diff / count;
        
        if (variance > 5.0f) lambda_val *= 0.5f;
        else if (variance < 0.5f) lambda_val *= 1.5f;
        
    } else {
        cv::Vec2f val = flow.at<cv::Vec2f>(center_y, center_x);
        avg_dx = val[0];
        avg_dy = val[1];
    }
    
    float weight = lambda_val * 0.1f;
    if (count < 8.0f) weight *= 2.0f;
    if (count < 4.0f) weight *= 4.0f;
    
    return {avg_dx, avg_dy, weight};
}

static void _block_search_kernel(
    const cv::Mat &ref_layer, const cv::Mat &comp_layer,
    cv::Mat &refined_flow,
    int tile_h, int tile_w, int search_radius
) {
    int h = ref_layer.rows, w = ref_layer.cols;
    int comp_h = comp_layer.rows, comp_w = comp_layer.cols;
    int step_y = tile_h, step_x = tile_w;

    for (int tile_y = 0; tile_y < (h + step_y - 1) / step_y; ++tile_y) {
        for (int tile_x = 0; tile_x < (w + step_x - 1) / step_x; ++tile_x) {
            int y = std::max(0, std::min(tile_y * step_y, h - tile_h));
            int x = std::max(0, std::min(tile_x * step_x, w - tile_w));

            copyTileToContiguousBuffer(ref_layer, y, x, tile_h, tile_w, ref_tile_buffer_g);

            float best_cost = 1e10f;
            float best_dx = 0.0f, best_dy = 0.0f;
            float bias_weight = 0.999f;

            for (int dy = -search_radius; dy <= search_radius; ++dy) {
                for (int dx = -search_radius; dx <= search_radius; ++dx) {
                    float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+dy, x+dx, tile_h, tile_w, h, w, comp_h, comp_w);
                    if (dx == 0 && dy == 0) cost *= bias_weight;
                    if (cost < best_cost) {
                        best_cost = cost; best_dx = static_cast<float>(dx); best_dy = static_cast<float>(dy);
                    }
                }
            }

            if (-search_radius < best_dx && best_dx < search_radius && -search_radius < best_dy && best_dy < search_radius) {
                float c0 = best_cost;
                float cx_m1 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int(best_dy), x+int(best_dx)-1, tile_h, tile_w, h, w, comp_h, comp_w);
                float cx_p1 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int(best_dy), x+int(best_dx)+1, tile_h, tile_w, h, w, comp_h, comp_w);
                float cy_m1 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int(best_dy)-1, x+int(best_dx), tile_h, tile_w, h, w, comp_h, comp_w);
                float cy_p1 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int(best_dy)+1, x+int(best_dx), tile_h, tile_w, h, w, comp_h, comp_w);

                float denom_x = 2.0f * (cx_p1 + cx_m1 - 2.0f * c0);
                if (std::abs(denom_x) > 1e-6f) best_dx -= (cx_p1 - cx_m1) / denom_x;
                float denom_y = 2.0f * (cy_p1 + cy_m1 - 2.0f * c0);
                if (std::abs(denom_y) > 1e-6f) best_dy -= (cy_p1 - cy_m1) / denom_y;
            }

            for (int r = 0; r < tile_h; ++r) {
                cv::Vec2f* row_ptr = refined_flow.ptr<cv::Vec2f>(y+r);
                for (int c = 0; c < tile_w; ++c) {
                    if (y + r < h && x + c < w) row_ptr[x+c] = cv::Vec2f(best_dx, best_dy);
                }
            }
        }
    }
}

static void _search_coarse_level_kernel(
    const cv::Mat &ref_layer, const cv::Mat &comp_layer,
    const cv::Mat &flow, const cv::Mat &previous_flow,
    cv::Mat &refined_flow,
    int tile_h, int tile_w, int search_dist, int downscale_factor
) {
    int h = ref_layer.rows, w = ref_layer.cols;
    int prev_h = previous_flow.rows, prev_w = previous_flow.cols;
    int comp_h = comp_layer.rows, comp_w = comp_layer.cols;
    int step_y = tile_h, step_x = tile_w;
    float tile_area_inv = 1.0f / (float)(tile_h * tile_w);

    const int neighbor_offsets[16][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1},
        {-1, -1}, {1, -1}, {-1, 1}, {1, 1},
        {-2, 0}, {2, 0}, {0, -2}, {0, 2},
        {-2, -2}, {2, -2}, {-2, 2}, {2, 2}
    };

    for (int tile_y = 0; tile_y < (h + step_y - 1) / step_y; ++tile_y) {
        for (int tile_x = 0; tile_x < (w + step_x - 1) / step_x; ++tile_x) {
            int y = std::max(0, std::min(tile_y * step_y, h - tile_h));
            int x = std::max(0, std::min(tile_x * step_x, w - tile_w));

            copyTileToContiguousBuffer(ref_layer, y, x, tile_h, tile_w, ref_tile_buffer_g);

            RegParams reg = _compute_regularization_params(flow, y, x, tile_h, tile_w, h, w);
            float spatial_mean_x = reg.avg_dx, spatial_mean_y = reg.avg_dy, spatial_weight = reg.weight;

            int center_y = y + tile_h / 2, center_x = x + tile_w / 2;
            cv::Vec2f init_flow = flow.at<cv::Vec2f>(center_y, center_x);
            int init_dx = static_cast<int>(std::round(init_flow[0])), init_dy = static_cast<int>(std::round(init_flow[1]));

            int cands_dx[18], cands_dy[18];
            for(int i=0; i<18; i++) { cands_dx[i] = init_dx; cands_dy[i] = init_dy; }

            for (int i = 0; i < 16; ++i) {
                int nx = center_x + neighbor_offsets[i][0] * step_x;
                int ny = center_y + neighbor_offsets[i][1] * step_y;
                if (nx >= 0 && nx < w && ny >= 0 && ny < h) {
                    cv::Vec2f nf = flow.at<cv::Vec2f>(ny, nx);
                    cands_dx[i+1] = std::round(nf[0]); cands_dy[i+1] = std::round(nf[1]);
                }
            }

            if (!previous_flow.empty() && prev_h > 1 && prev_w > 1) {
                int coarse_y = center_y / downscale_factor, coarse_x = center_x / downscale_factor;
                if (coarse_y < prev_h && coarse_x < prev_w) {
                    cv::Vec2f pf = previous_flow.at<cv::Vec2f>(coarse_y, coarse_x);
                    cands_dx[17] = std::round(pf[0] * downscale_factor); cands_dy[17] = std::round(pf[1] * downscale_factor);
                }
            }

            float best_cand_cost = 1e10f;
            int best_cand_dx = init_dx, best_cand_dy = init_dy;

            for (int i = 0; i < 6; ++i) {
                int cand_idx = (i == 5) ? 17 : i;
                int check_y = y + cands_dy[cand_idx], check_x = x + cands_dx[cand_idx];
                bool is_unique = true;
                for (int j = 0; j < i; ++j) {
                    int prev_idx = (j == 5) ? 17 : j;
                    if (cands_dx[cand_idx] == cands_dx[prev_idx] && cands_dy[cand_idx] == cands_dy[prev_idx]) { is_unique = false; break; }
                }
                if (is_unique) {
                    float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                    if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[cand_idx]; best_cand_dy = cands_dy[cand_idx]; }
                }
            }

            if (best_cand_cost > 0.005f) {
                for (int i = 6; i < 10; ++i) {
                    int check_y = y + cands_dy[i], check_x = x + cands_dx[i];
                    bool is_unique = true;
                    for (int j = 0; j < 6; ++j) {
                        int prev_idx = (j == 5) ? 17 : j;
                        if (cands_dx[i] == cands_dx[prev_idx] && cands_dy[i] == cands_dy[prev_idx]) { is_unique = false; break; }
                    }
                    if (is_unique) {
                        float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                        if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[i]; best_cand_dy = cands_dy[i]; }
                    }
                }
            }

            if (best_cand_cost > 0.01f) {
                for (int i = 10; i < 18; ++i) {
                    if (i==17) continue;
                    int check_y = y + cands_dy[i], check_x = x + cands_dx[i];
                    bool is_unique = true;
                    for (int j = 0; j < 10; ++j) {
                        int prev_idx = (j == 5) ? 17 : j;
                        if (cands_dx[i] == cands_dx[prev_idx] && cands_dy[i] == cands_dy[prev_idx]) { is_unique = false; break; }
                    }
                    if (is_unique) {
                        float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                        if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[i]; best_cand_dy = cands_dy[i]; }
                    }
                }
            }

            init_dx = best_cand_dx; init_dy = best_cand_dy;
            float best_total_cost = 1e10f;
            float best_dx = float(init_dx), best_dy = float(init_dy);

            if (best_cand_cost >= 0.001f) {
                for (int dy = -search_dist; dy <= search_dist; ++dy) {
                    float cur_dy = init_dy + dy;
                    for (int dx = -search_dist; dx <= search_dist; ++dx) {
                        float cur_dx = init_dx + dx;
                        int test_y = y + cur_dy, test_x = x + cur_dx;

                        float raw_cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, test_y, test_x, tile_h, tile_w, h, w, comp_h, comp_w);
                        if (raw_cost == std::numeric_limits<float>::max()) continue;
                        
                        float visual_cost = raw_cost * tile_area_inv;
                        float dist_sq = (cur_dx - spatial_mean_x)*(cur_dx - spatial_mean_x) + (cur_dy - spatial_mean_y)*(cur_dy - spatial_mean_y);
                        
                        float dynamic_weight = spatial_weight;
                        if (visual_cost < 0.01f) dynamic_weight *= 0.1f;
                        else if (visual_cost > 0.1f) dynamic_weight *= 3.0f;
                        
                        float boundary_penalty = 0.0f;
                        if (test_y < 0 || test_y + tile_h > h || test_x < 0 || test_x + tile_w > w) {
                            float dist_y = std::max(0.0f, std::max(float(-test_y), float(test_y + tile_h - h)));
                            float dist_x = std::max(0.0f, std::max(float(-test_x), float(test_x + tile_w - w)));
                            boundary_penalty = (dist_y + dist_x) * 0.01f;
                        }

                        float total_cost = visual_cost + (dynamic_weight * dist_sq) + boundary_penalty;
                        if (total_cost < best_total_cost) {
                            best_total_cost = total_cost; best_dx = cur_dx; best_dy = cur_dy;
                        }
                    }
                }
            }

            for (int r = 0; r < tile_h; ++r) {
                cv::Vec2f* row_ptr = refined_flow.ptr<cv::Vec2f>(y+r);
                for (int c = 0; c < tile_w; ++c) {
                    if (y + r < h && x + c < w) row_ptr[x+c] = cv::Vec2f(best_dx, best_dy);
                }
            }
        }
    }
}

static void _search_fine_level_kernel(
    const cv::Mat &ref_layer, const cv::Mat &comp_layer,
    const cv::Mat &flow, const cv::Mat &previous_flow,
    cv::Mat &refined_flow,
    int tile_h, int tile_w, int downscale_factor
) {
    int h = ref_layer.rows, w = ref_layer.cols;
    int prev_h = previous_flow.rows, prev_w = previous_flow.cols;
    int comp_h = comp_layer.rows, comp_w = comp_layer.cols;
    int step_y = tile_h, step_x = tile_w;
    float tile_area_inv = 1.0f / (float)(tile_h * tile_w);

    const int neighbor_offsets[16][2] = {
        {-1, 0}, {1, 0}, {0, -1}, {0, 1},
        {-1, -1}, {1, -1}, {-1, 1}, {1, 1},
        {-2, 0}, {2, 0}, {0, -2}, {0, 2},
        {-2, -2}, {2, -2}, {-2, 2}, {2, 2}
    };

    for (int tile_y = 0; tile_y < (h + step_y - 1) / step_y; ++tile_y) {
        for (int tile_x = 0; tile_x < (w + step_x - 1) / step_x; ++tile_x) {
            int y = std::max(0, std::min(tile_y * step_y, h - tile_h));
            int x = std::max(0, std::min(tile_x * step_x, w - tile_w));

            copyTileToContiguousBuffer(ref_layer, y, x, tile_h, tile_w, ref_tile_buffer_g);

            RegParams reg = _compute_regularization_params(flow, y, x, tile_h, tile_w, h, w);
            float spatial_mean_x = reg.avg_dx, spatial_mean_y = reg.avg_dy, spatial_weight = reg.weight;

            int center_y = y + tile_h / 2, center_x = x + tile_w / 2;
            cv::Vec2f init_flow = flow.at<cv::Vec2f>(center_y, center_x);
            int init_dx = static_cast<int>(std::round(init_flow[0])), init_dy = static_cast<int>(std::round(init_flow[1]));

            int cands_dx[18], cands_dy[18];
            for (int i = 0; i < 18; i++) { cands_dx[i] = init_dx; cands_dy[i] = init_dy; }

            for (int i = 0; i < 16; ++i) {
                int nx = center_x + neighbor_offsets[i][0] * step_x;
                int ny = center_y + neighbor_offsets[i][1] * step_y;
                if (nx >= 0 && nx < w && ny >= 0 && ny < h) {
                    cv::Vec2f nf = flow.at<cv::Vec2f>(ny, nx);
                    cands_dx[i+1] = std::round(nf[0]); cands_dy[i+1] = std::round(nf[1]);
                }
            }

            if (!previous_flow.empty() && prev_h > 1 && prev_w > 1) {
                int coarse_y = center_y / downscale_factor, coarse_x = center_x / downscale_factor;
                if (coarse_y < prev_h && coarse_x < prev_w) {
                    cv::Vec2f pf = previous_flow.at<cv::Vec2f>(coarse_y, coarse_x);
                    cands_dx[17] = std::round(pf[0] * downscale_factor); cands_dy[17] = std::round(pf[1] * downscale_factor);
                }
            }

            float best_cand_cost = 1e10f;
            int best_cand_dx = init_dx, best_cand_dy = init_dy;

            for (int i = 0; i < 6; ++i) {
                int cand_idx = (i == 5) ? 17 : i;
                int check_y = y + cands_dy[cand_idx], check_x = x + cands_dx[cand_idx];
                bool is_unique = true;
                for (int j = 0; j < i; ++j) {
                    int prev_idx = (j == 5) ? 17 : j;
                    if (cands_dx[cand_idx] == cands_dx[prev_idx] && cands_dy[cand_idx] == cands_dy[prev_idx]) { is_unique = false; break; }
                }
                if (is_unique) {
                    float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                    if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[cand_idx]; best_cand_dy = cands_dy[cand_idx]; }
                }
            }

            if (best_cand_cost > 0.005f) {
                for (int i = 6; i < 10; ++i) {
                    int check_y = y + cands_dy[i], check_x = x + cands_dx[i];
                    bool is_unique = true;
                    for (int j = 0; j < 6; ++j) {
                        int prev_idx = (j == 5) ? 17 : j;
                        if (cands_dx[i] == cands_dx[prev_idx] && cands_dy[i] == cands_dy[prev_idx]) { is_unique = false; break; }
                    }
                    if (is_unique) {
                        float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                        if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[i]; best_cand_dy = cands_dy[i]; }
                    }
                }
            }

            if (best_cand_cost > 0.01f) {
                for (int i = 10; i < 18; ++i) {
                    if (i==17) continue;
                    int check_y = y + cands_dy[i], check_x = x + cands_dx[i];
                    bool is_unique = true;
                    for (int j = 0; j < 10; ++j) {
                        int prev_idx = (j == 5) ? 17 : j;
                        if (cands_dx[i] == cands_dx[prev_idx] && cands_dy[i] == cands_dy[prev_idx]) { is_unique = false; break; }
                    }
                    if (is_unique) {
                        float cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, check_y, check_x, tile_h, tile_w, h, w, comp_h, comp_w) * tile_area_inv;
                        if (cost < best_cand_cost) { best_cand_cost = cost; best_cand_dx = cands_dx[i]; best_cand_dy = cands_dy[i]; }
                    }
                }
            }

            init_dx = best_cand_dx; init_dy = best_cand_dy;
            float best_total_cost = 1e10f;
            float final_dx = float(init_dx), final_dy = float(init_dy);

            if (best_cand_cost >= 0.001f) {
                for (int dy = -1; dy <= 1; ++dy) {
                    float cur_dy = init_dy + dy;
                    for (int dx = -1; dx <= 1; ++dx) {
                        float cur_dx = init_dx + dx;
                        int test_y = y + cur_dy, test_x = x + cur_dx;

                        float raw_cost = compute_zmssd_cost(ref_layer, comp_layer, y, x, test_y, test_x, tile_h, tile_w, h, w, comp_h, comp_w);
                        if (raw_cost == std::numeric_limits<float>::max()) continue;
                        
                        float visual_cost = raw_cost * tile_area_inv;
                        float dist_sq = (cur_dx - spatial_mean_x)*(cur_dx - spatial_mean_x) + (cur_dy - spatial_mean_y)*(cur_dy - spatial_mean_y);
                        
                        float dynamic_weight = spatial_weight;
                        if (visual_cost < 0.01f) dynamic_weight *= 0.1f;
                        else if (visual_cost > 0.1f) dynamic_weight *= 3.0f;
                        
                        float boundary_penalty = 0.0f;
                        if (test_y < 0 || test_y + tile_h > h || test_x < 0 || test_x + tile_w > w) {
                            float dist_y = std::max(0.0f, std::max(float(-test_y), float(test_y + tile_h - h)));
                            float dist_x = std::max(0.0f, std::max(float(-test_x), float(test_x + tile_w - w)));
                            boundary_penalty = (dist_y + dist_x) * 0.01f;
                        }

                        float total_cost = visual_cost + (dynamic_weight * dist_sq) + boundary_penalty;
                        if (total_cost < best_total_cost) {
                            best_total_cost = total_cost; final_dx = cur_dx; final_dy = cur_dy;
                        }
                    }
                }
            }

            int int_dx = std::round(final_dx), int_dy = std::round(final_dy);
            float c_0_0 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_m1_x = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx-1, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_p1_x = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx+1, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_m1_y = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy-1, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_p1_y = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy+1, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);

            float delta_x = 0.0f;
            float denom_x = 2.0f * (c_p1_x + c_m1_x - 2.0f * c_0_0);
            if (std::abs(denom_x) > 1e-6f) delta_x = -(c_p1_x - c_m1_x) / denom_x;
            delta_x = std::max(-0.5f, std::min(0.5f, delta_x));

            float delta_y = 0.0f;
            float denom_y = 2.0f * (c_p1_y + c_m1_y - 2.0f * c_0_0);
            if (std::abs(denom_y) > 1e-6f) delta_y = -(c_p1_y - c_m1_y) / denom_y;
            delta_y = std::max(-0.5f, std::min(0.5f, delta_y));

            final_dx = float(int_dx) + delta_x;
            final_dy = float(int_dy) + delta_y;

            for (int r = 0; r < tile_h; ++r) {
                cv::Vec2f* row_ptr = refined_flow.ptr<cv::Vec2f>(y+r);
                for (int c = 0; c < tile_w; ++c) {
                    if (y + r < h && x + c < w) row_ptr[x+c] = cv::Vec2f(final_dx, final_dy);
                }
            }
        }
    }
}

static void _parabolic_subpixel_refinement_kernel(
    const cv::Mat &ref_layer, const cv::Mat &comp_layer,
    const cv::Mat &flow, cv::Mat &refined_flow,
    int tile_h, int tile_w
) {
    int h = ref_layer.rows, w = ref_layer.cols;
    int comp_h = comp_layer.rows, comp_w = comp_layer.cols;
    int step_y = tile_h, step_x = tile_w;

    for (int tile_y = 0; tile_y < (h + step_y - 1) / step_y; ++tile_y) {
        for (int tile_x = 0; tile_x < (w + step_x - 1) / step_x; ++tile_x) {
            int y = std::max(0, std::min(tile_y * step_y, h - tile_h));
            int x = std::max(0, std::min(tile_x * step_x, w - tile_w));

            copyTileToContiguousBuffer(ref_layer, y, x, tile_h, tile_w, ref_tile_buffer_g);

            int center_y = y + tile_h / 2, center_x = x + tile_w / 2;
            cv::Vec2f flow_val = flow.at<cv::Vec2f>(center_y, center_x);
            int int_dx = std::round(flow_val[0]), int_dy = std::round(flow_val[1]);

            float c_0_0 = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_m1_x = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx-1, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_p1_x = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy, x+int_dx+1, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_m1_y = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy-1, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);
            float c_p1_y = compute_zmssd_cost(ref_layer, comp_layer, y, x, y+int_dy+1, x+int_dx, tile_h, tile_w, h, w, comp_h, comp_w);

            float delta_x = 0.0f;
            float denom_x = 2.0f * (c_p1_x + c_m1_x - 2.0f * c_0_0);
            if (std::abs(denom_x) > 1e-6f) delta_x = -(c_p1_x - c_m1_x) / denom_x;
            delta_x = std::max(-0.5f, std::min(0.5f, delta_x));

            float delta_y = 0.0f;
            float denom_y = 2.0f * (c_p1_y + c_m1_y - 2.0f * c_0_0);
            if (std::abs(denom_y) > 1e-6f) delta_y = -(c_p1_y - c_m1_y) / denom_y;
            delta_y = std::max(-0.5f, std::min(0.5f, delta_y));

            float final_dx = float(int_dx) + delta_x;
            float final_dy = float(int_dy) + delta_y;

            for (int r = 0; r < tile_h; ++r) {
                cv::Vec2f* row_ptr = refined_flow.ptr<cv::Vec2f>(y+r);
                for (int c = 0; c < tile_w; ++c) {
                    if (y + r < h && x + c < w) row_ptr[x+c] = cv::Vec2f(final_dx, final_dy);
                }
            }
        }
    }
}

static cv::Mat process_single_layer(
    const cv::Mat &ref_layer_gpu, const cv::Mat &comp_layer_gpu,
    const cv::Mat &previous_flow_gpu, int layer_index, int total_layers,
    int tile_h, int tile_w, float search_dist, int downscale_factor = 4) {
    
    int h = ref_layer_gpu.rows;
    int w = ref_layer_gpu.cols;
    bool is_coarsest_layer = (layer_index == total_layers - 1);
    bool is_finest_layer = (layer_index == 0);

    cv::Mat flow_gpu = cv::Mat::zeros(h, w, CV_32FC2);

    if (is_coarsest_layer) {
        _initialize_coarsest_flow_kernel(flow_gpu, h, w, 0.0f, 0.0f);
    } else {
        cv::resize(previous_flow_gpu, flow_gpu, cv::Size(w, h), 0, 0, cv::INTER_LINEAR);
        flow_gpu *= static_cast<float>(downscale_factor);
    }

    int current_tile_h = std::max(ImageAlignmentConfig::MIN_TILE_SIZE, std::min(tile_h, h));
    int current_tile_w = std::max(ImageAlignmentConfig::MIN_TILE_SIZE, std::min(tile_w, w));

    cv::Mat refined_flow_gpu = cv::Mat::zeros(h, w, CV_32FC2);
    _initialize_coarsest_flow_kernel(refined_flow_gpu, h, w, 0.0f, 0.0f);

    cv::Mat safe_prev_flow = previous_flow_gpu;
    if (safe_prev_flow.empty()) safe_prev_flow = cv::Mat::zeros(1, 1, CV_32FC2);

    if (is_finest_layer) {
        _search_fine_level_kernel(
            ref_layer_gpu, comp_layer_gpu, flow_gpu, safe_prev_flow, refined_flow_gpu,
            current_tile_h, current_tile_w, downscale_factor);
    } else if (is_coarsest_layer) {
        int search_radius = std::max(4, int(search_dist * 2.0f));
        _block_search_kernel(
            ref_layer_gpu, comp_layer_gpu, refined_flow_gpu,
            current_tile_h, current_tile_w, search_radius);
    } else {
        int current_search_dist = std::max(2, int(search_dist));
        _search_coarse_level_kernel(
            ref_layer_gpu, comp_layer_gpu, flow_gpu, safe_prev_flow, refined_flow_gpu,
            current_tile_h, current_tile_w, current_search_dist, downscale_factor);
    }

    if (!is_finest_layer) {
        flow_gpu = refined_flow_gpu.clone();
        _parabolic_subpixel_refinement_kernel(
            ref_layer_gpu, comp_layer_gpu, flow_gpu, refined_flow_gpu,
            current_tile_h, current_tile_w);
    }

    return refined_flow_gpu;
}
} // namespace AlignmentFlowHelpers

// =========================================================================
// === FUNGSI UTAMA DENGAN REFACTORED CODE ===
// =========================================================================

extern "C" {
ALIGNMENT_API float *compute_alignment_flow(const float *ref_work_data,
                                            const float *current_work_data,
                                            int work_h, int work_w, int tile_h,
                                            int tile_w, int n_layers,
                                            float search_dist) {
  using namespace ImageAlignmentConfig;

  cv::Mat ref_work(work_h, work_w, CV_32FC1, const_cast<float *>(ref_work_data));
  cv::Mat current_work(work_h, work_w, CV_32FC1, const_cast<float *>(current_work_data));

  std::vector<cv::Mat> ref_pyramid, current_pyramid;
  {
    ref_pyramid.reserve(n_layers);
    current_pyramid.reserve(n_layers);

    ref_pyramid.push_back(ref_work);
    current_pyramid.push_back(current_work);

    for (int i = 0; i < n_layers - 1; ++i) {
      cv::Mat mid_ref, mid_current;
      cv::pyrDown(ref_pyramid.back(), mid_ref);
      cv::pyrDown(current_pyramid.back(), mid_current);

      cv::Mat next_ref, next_current;
      cv::pyrDown(mid_ref, next_ref);
      cv::pyrDown(mid_current, next_current);

      if (next_ref.rows < MIN_PYRAMID_LAYER_SIZE ||
          next_ref.cols < MIN_PYRAMID_LAYER_SIZE) {
        if (mid_ref.rows >= MIN_PYRAMID_LAYER_SIZE &&
            mid_ref.cols >= MIN_PYRAMID_LAYER_SIZE) {
          ref_pyramid.push_back(std::move(mid_ref));
          current_pyramid.push_back(std::move(mid_current));
        }
        break;
      }
      ref_pyramid.push_back(std::move(next_ref));
      current_pyramid.push_back(std::move(next_current));
    }
  }

  cv::Mat previous_level_flow;
  {
    for (int i = static_cast<int>(ref_pyramid.size()) - 1; i >= 0; --i) {
      cv::Mat current_flow = AlignmentFlowHelpers::process_single_layer(
          ref_pyramid[i], current_pyramid[i], previous_level_flow, i,
          static_cast<int>(ref_pyramid.size()), tile_h, tile_w, search_dist, (int)FLOW_UPSCALE_FACTOR);

      previous_level_flow = std::move(current_flow);
    }
  }

  cv::Mat flow = std::move(previous_level_flow);

  float *output_flow_data = nullptr;
  {
    if (!flow.empty()) {
      if (!flow.isContinuous())
        flow = flow.clone();

      const size_t total_pixels = flow.total();
      const size_t data_size = total_pixels * flow.elemSize();
      output_flow_data = static_cast<float *>(malloc(data_size));

      if (output_flow_data) {
        const int rows = flow.rows;
        const size_t row_size_bytes = flow.cols * flow.elemSize();

#pragma omp parallel for
        for (int r = 0; r < rows; ++r) {
          const uchar *src_ptr = flow.ptr<uchar>(r);
          uchar *dst_ptr = reinterpret_cast<uchar *>(output_flow_data) +
                           (size_t)r * row_size_bytes;
          std::memcpy(dst_ptr, src_ptr, row_size_bytes);
        }
      }
    }
  }

  return output_flow_data;
}

ALIGNMENT_API void free_flow_memory(float *flow_data) {
  if (flow_data)
    free(flow_data);
}
}
