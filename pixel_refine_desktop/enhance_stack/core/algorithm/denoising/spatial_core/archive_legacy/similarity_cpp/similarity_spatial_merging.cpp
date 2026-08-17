#include "block_matching.hpp"
#include "spatial_merging.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <limits>
#include <numeric>
#include <omp.h>
#include <opencv2/core.hpp>
#include <opencv2/core/utility.hpp>
#include <opencv2/imgproc.hpp>
#include <string>
#include <vector>

// Fungsi helper inline yang lebih robust menggunakan Median Matching
// OPTIMIZED: Uses pre-allocated buffers to avoid std::vector re-allocation
static inline void
equalize_tile_brightness_optimized(const cv::Mat &src, const cv::Mat &ref,
                                   cv::Mat &dst, std::vector<float> &buf_src,
                                   std::vector<float> &buf_ref) {
  // --- Langkah 1: Persiapan dan Ekstraksi Data ---
  const int num_pixels = src.rows * src.cols;
  if (num_pixels < 20) {
    src.copyTo(dst);
    return;
  }

  // Resize buffer hanya jika perlu (capacity dipertahankan)
  if (buf_src.size() < num_pixels)
    buf_src.resize(num_pixels);
  if (buf_ref.size() < num_pixels)
    buf_ref.resize(num_pixels);

  // Salin data piksel (contiguous copy)
  if (src.isContinuous()) {
    std::memcpy(buf_src.data(), src.ptr<float>(0), num_pixels * sizeof(float));
  } else {
    // Fallback untuk non-continuous (ROI)
    const int w = src.cols;
    for (int r = 0; r < src.rows; ++r) {
      std::memcpy(buf_src.data() + r * w, src.ptr<float>(r), w * sizeof(float));
    }
  }

  if (ref.isContinuous()) {
    std::memcpy(buf_ref.data(), ref.ptr<float>(0), num_pixels * sizeof(float));
  } else {
    const int w = ref.cols;
    for (int r = 0; r < ref.rows; ++r) {
      std::memcpy(buf_ref.data() + r * w, ref.ptr<float>(r), w * sizeof(float));
    }
  }

  // --- Langkah 2: Hitung Median (Robust Metric) ---
  // Gunakan pointer range buffer yang valid
  auto src_begin = buf_src.begin();
  auto src_end = buf_src.begin() + num_pixels;
  auto ref_begin = buf_ref.begin();
  auto ref_end = buf_ref.begin() + num_pixels;

  auto src_median_it = src_begin + num_pixels / 2;
  std::nth_element(src_begin, src_median_it, src_end);
  float median_src = *src_median_it;

  auto ref_median_it = ref_begin + num_pixels / 2;
  std::nth_element(ref_begin, ref_median_it, ref_end);
  float median_ref = *ref_median_it;

  // --- Langkah 3: Hitung Gain ---
  double gain = median_ref / (median_src + 1e-5);

  // --- Langkah 4: Batasi dan Terapkan Gain ---
  if (gain < 0.6)
    gain = 0.6;
  if (gain > 1.8)
    gain = 1.8;

  if (std::abs(gain - 1.0) > 0.01) {
    if (dst.empty() || dst.size() != src.size()) {
      dst.create(src.size(), src.type());
    }
    // cv::multiply overhead is small for contiguous, but here we keep it for
    // simplicity can be optimized to AVX loop if needed, but gain is global
    // scalar.
    cv::multiply(src, gain, dst);
  } else {
    src.copyTo(dst);
  }
}

// FAST ACCUMULATION KERNEL (AVX-Friendly)
// Menggantikan cv::add untuk ROI kecil. Jauh lebih cepat karena:
// 1. Tidak ada overhead validasi ROI/Type OpenCV
// 2. Loop sederhana yang mudah di-autovectorize oleh compiler
// 3. Cache friendly
static inline void
accumulate_tile(cv::Mat &accum_map,         // Global map (CV_32FC1)
                const cv::Mat &tile_weight, // Local tile weight (CV_32FC1)
                const cv::Rect &roi)        // Region to accumulate
{
  const int h = roi.height;
  const int w = roi.width;

  // Pointer akses
  // Accum map mungkin besar, jadi kita pakai stride
  size_t accum_step = accum_map.step1();
  size_t tile_step = tile_weight.step1();

  float *accum_ptr_base = accum_map.ptr<float>(roi.y) + roi.x;
  const float *tile_ptr_base = tile_weight.ptr<float>(0);

  for (int r = 0; r < h; ++r) {
    float *dst_row = accum_ptr_base + r * accum_step;
    const float *src_row = tile_ptr_base + r * tile_step;

// Auto-vectorized loop
#pragma omp simd
    for (int c = 0; c < w; ++c) {
      dst_row[c] += src_row[c];
    }
  }
}

namespace MotionMetricsConfig {
constexpr float STABILITY_EPSILON = 1e-6f;
constexpr float CONFIDENCE_EPSILON = 1e-6f;
constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
constexpr float GRADIENT_WEIGHT_FACTOR = 1.0f;
constexpr float MAD_TO_SIGMA_FACTOR = 1.4826f;
} // namespace MotionMetricsConfig

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
    // std::cout << "[C++ Timer] " << name << ": " << elapsed.count() << " ms"
    //           << std::endl;
  }
};

extern "C" {
// Struktur data bantu untuk manajemen memori thread-local yang efisien
struct ThreadBuffers {
  cv::Mat normalized_tile;
  MotionMatching::MBMBuffers mad_buffers;
  // Buffers untuk Equalization
  std::vector<float> eq_buf_src;
  std::vector<float> eq_buf_ref;

  void ensureSize(int h, int w) {
    if (normalized_tile.empty() || normalized_tile.rows != h ||
        normalized_tile.cols != w) {
      normalized_tile.create(h, w, CV_32FC1);
    }
    if (mad_buffers.diff_workspace.empty() ||
        mad_buffers.diff_workspace.rows != h ||
        mad_buffers.diff_workspace.cols != w) {
      mad_buffers.diff_workspace.create(h, w, CV_32FC1);
      mad_buffers.grad_x.create(h, w, CV_32F);
      mad_buffers.grad_y.create(h, w, CV_32F);
      mad_buffers.grad_mag_current.create(h, w, CV_32FC1);
    }
  }
};

void generate_weight_map_jit(
    float *weight_map_sum_ptr, const float *current_image_ptr,
    const float *reference_image_ptr, const float *base_window_ptr,
    const float *stability_map_ptr, const int *row_starts,
    const int *col_starts, int num_row_starts, int num_col_starts, int tile_h,
    int tile_w, int h_img, int w_img, int channels, float motion_sensitivity,
    float noise_offset_factor, float precomputed_ref_noise_sigma) {
  using namespace MotionMetricsConfig;

  SimpleTimer total_timer("Total generate_weight_map_jit");

  if (!weight_map_sum_ptr)
    return;

  float global_estimated_noise_sigma = precomputed_ref_noise_sigma;

  cv::Mat current_image_gray(h_img, w_img, CV_32FC1, (void *)current_image_ptr);
  cv::Mat reference_image_gray(h_img, w_img, CV_32FC1,
                               (void *)reference_image_ptr);
  cv::Mat stability_map_mat;
  if (stability_map_ptr != nullptr)
    stability_map_mat =
        cv::Mat(h_img, w_img, CV_32FC1, (void *)stability_map_ptr);

  const int tile_h_fine = tile_h;
  const int tile_w_fine = tile_w;
  cv::Mat final_guidance_map; // Declared once here

  // ---------------------------------------------------------------------------------
  // PHASE 1: DYNAMIC PYRAMID & GUIDANCE
  // ---------------------------------------------------------------------------------
  // ---------------------------------------------------------------------------------
  // PHASE 1: SMART SIMPLIFIED GUIDANCE (Hybrid Gradient)
  // ---------------------------------------------------------------------------------
  {
    SimpleTimer phase1_timer("Phase 1: Smart Simplified Guidance");

    // 1. Downscale to coarse resolution (Target ~512px width/height or 1/4
    // size) Using 1/4 size is faster and sufficient for guidance
    int coarse_w = std::max(64, w_img / 4);
    int coarse_h = std::max(64, h_img / 4);

    cv::Mat current_coarse, reference_coarse;
    cv::resize(current_image_gray, current_coarse, cv::Size(coarse_w, coarse_h),
               0, 0, cv::INTER_AREA);
    cv::resize(reference_image_gray, reference_coarse,
               cv::Size(coarse_w, coarse_h), 0, 0, cv::INTER_AREA);

    // 2. Coarse Grid Processing
    int coarse_tile_w = std::max(8, tile_w_fine / 4);
    int coarse_tile_h = std::max(8, tile_h_fine / 4);

    int num_tiles_h = current_coarse.rows / coarse_tile_h;
    int num_tiles_w = current_coarse.cols / coarse_tile_w;

    cv::Mat coarse_confidence_map(num_tiles_h, num_tiles_w, CV_32FC1);

// Thread-local buffers for calculate_tile_mad
#pragma omp parallel
    {
      MotionMatching::MBMBuffers local_bufs;
      local_bufs.diff_workspace.create(coarse_tile_h, coarse_tile_w, CV_32FC1);
      local_bufs.grad_x.create(coarse_tile_h, coarse_tile_w, CV_32F);
      local_bufs.grad_y.create(coarse_tile_h, coarse_tile_w, CV_32F);
      local_bufs.grad_mag_current.create(coarse_tile_h, coarse_tile_w,
                                         CV_32FC1);

#pragma omp for collapse(2) schedule(dynamic)
      for (int r = 0; r < num_tiles_h; ++r) {
        for (int c = 0; c < num_tiles_w; ++c) {
          cv::Rect roi(c * coarse_tile_w, r * coarse_tile_h, coarse_tile_w,
                       coarse_tile_h);

          // Boundary check
          if (roi.x + roi.width > current_coarse.cols)
            roi.width = current_coarse.cols - roi.x;
          if (roi.y + roi.height > current_coarse.rows)
            roi.height = current_coarse.rows - roi.y;

          if (roi.width <= 0 || roi.height <= 0)
            continue;

          // CRITICAL: Use Hybrid Gradient MAD (calculate_tile_mad) instead of
          // FFT This captures structure even at low resolution
          MotionMatching::TileMatchResult res =
              MotionMatching::calculate_tile_mad(
                  current_coarse(roi), reference_coarse(roi),
                  global_estimated_noise_sigma, GRADIENT_WEIGHT_FACTOR,
                  STABILITY_EPSILON, local_bufs);

          float conf = 0.0f;
          if (res.success) {
            // Calculate confidence from MAD score
            // Reuse the helper function available in namespace or defining new
            // logic MotionMatching::calculate_match_confidence is static helper
            // in this file? It's static member of MotionMatching? No, it was
            // static function in this file. Let's use the
            // MotionMatching::calculate_match_confidence if accessible or
            // reimplement simple one.

            // Re-implementing simplified confidence for Coarse Phase
            float val = res.mad_score;
            float sigma = std::max(1e-6f, global_estimated_noise_sigma);
            float diff_ratio = val / sigma;
            float adjusted = std::max(0.0f, diff_ratio - noise_offset_factor);
            float exponent = adjusted * motion_sensitivity *
                             0.5f; // reduced sensitivity for coarse
            if (exponent > 20.0f)
              conf = 0.0f;
            else
              conf = 1.0f / (1.0f + std::exp(exponent - 2.0f));
          }
          coarse_confidence_map.at<float>(r, c) = conf;
        }
      }
    }

    // 3. Upscale to Full Resolution
    cv::resize(coarse_confidence_map, final_guidance_map,
               cv::Size(w_img, h_img), 0, 0, cv::INTER_CUBIC);
  }

  // ---------------------------------------------------------------------------------
  // PHASE 2: FINE ANALYSIS (MAD)
  // ---------------------------------------------------------------------------------
  {
    SimpleTimer phase2_timer("Phase 2: Fine Analysis (MAD) Parallel");

    cv::Mat weight_map_sum_mat(h_img, w_img, CV_32FC1, weight_map_sum_ptr);
    weight_map_sum_mat.setTo(0.0f);

    // const int NUM_LOCKS = omp_get_max_threads() * 8; // REMOVED: No longer
    // needed std::vector<omp_lock_t> locks(NUM_LOCKS); for (int i = 0; i <
    // NUM_LOCKS; i++)
    //   omp_init_lock(&locks[i]);

#pragma omp parallel
    {
      ThreadBuffers t_bufs;
      t_bufs.ensureSize(tile_h_fine, tile_w_fine);

      cv::Mat local_weight_tile(tile_h_fine, tile_w_fine, CV_32FC1);
      cv::Mat base_window_tile_mat(tile_h_fine, tile_w_fine, CV_32FC1,
                                   const_cast<float *>(base_window_ptr));

      for (int pass = 0; pass < 4; ++pass) {
        int pass_row_mod = pass / 2;
        int pass_col_mod = pass % 2;

#pragma omp for collapse(2) schedule(dynamic)
        for (int i = 0; i < num_row_starts; i++) {
          for (int j = 0; j < num_col_starts; j++) {
            if (i % 2 != pass_row_mod || j % 2 != pass_col_mod)
              continue;

            int r = row_starts[i];
            int c = col_starts[j];

            int curr_h = std::min(tile_h_fine, h_img - r);
            int curr_w = std::min(tile_w_fine, w_img - c);
            if (curr_h <= 0 || curr_w <= 0)
              continue;

            cv::Rect valid_roi(c, r, curr_w, curr_h);

            MotionMatching::TileMatchResult mbm_result =
                MotionMatching::calculate_tile_mad(
                    current_image_gray(valid_roi),
                    reference_image_gray(valid_roi),
                    global_estimated_noise_sigma, GRADIENT_WEIGHT_FACTOR,
                    STABILITY_EPSILON, t_bufs.mad_buffers);

            float confidence_fine =
                mbm_result.success
                    ? MotionMatching::calculate_match_confidence(
                          mbm_result, global_estimated_noise_sigma,
                          motion_sensitivity, noise_offset_factor)
                    : 0.0f;

            // UPDATED: Sample from FULL RES final_guidance_map
            // Use center point of tile
            int center_x = std::min(c + curr_w / 2, w_img - 1);
            int center_y = std::min(r + curr_h / 2, h_img - 1);
            float guidance_val =
                final_guidance_map.at<float>(center_y, center_x);

            float final_conf = confidence_fine * guidance_val;

            if (!stability_map_mat.empty()) {
              float stab_val = stability_map_mat.at<float>(center_y, center_x);
              final_conf *= stab_val;
            }

            if (final_conf < 1e-6f)
              continue;

            if (curr_w == tile_w_fine && curr_h == tile_h_fine) {
              cv::multiply(base_window_tile_mat, final_conf, local_weight_tile);
            } else {
              cv::Mat partial_window =
                  base_window_tile_mat(cv::Rect(0, 0, curr_w, curr_h));
              cv::multiply(partial_window, final_conf,
                           local_weight_tile(cv::Rect(0, 0, curr_w, curr_h)));
            }

            accumulate_tile(
                weight_map_sum_mat,
                (curr_w == tile_w_fine && curr_h == tile_h_fine)
                    ? local_weight_tile
                    : local_weight_tile(cv::Rect(0, 0, curr_w, curr_h)),
                valid_roi);
          }
        }
      }
    }
    // for (int i = 0; i < NUM_LOCKS; i++) omp_destroy_lock(&locks[i]); //
    // REMOVED
  }
}
} // extern "C"
