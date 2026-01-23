#include "cost_function.hpp" // Sertakan header yang sesuai

#include <cmath>               // Untuk std::fabs
#include <immintrin.h>         // Untuk intrinsik AVX
#include <opencv2/imgproc.hpp> // Untuk dft, idft, dll.

#include <cmath>
#include <immintrin.h>

constexpr float NORMALIZATION_EPSILON = 1e-6f;
constexpr float EPSILON_SQ = NORMALIZATION_EPSILON * NORMALIZATION_EPSILON;

// ============================================================================
// OPTIMIZED: Zero-Mean SAD dengan AVX - Performa Maksimal, Akurasi Sama
// ============================================================================

static inline float horizontal_sum_avx(__m256 v) {
  // Optimasi H-Sum
  __m128 vlow = _mm256_castps256_ps128(v);
  __m128 vhigh = _mm256_extractf128_ps(v, 1);
  vlow = _mm_add_ps(vlow, vhigh);
  __m128 shuf = _mm_movehdup_ps(vlow);
  __m128 sums = _mm_add_ps(vlow, shuf);
  shuf = _mm_movehl_ps(shuf, sums);
  sums = _mm_add_ss(sums, shuf);
  return _mm_cvtss_f32(sums);
}

// Versi FMA + Tail Optimization (MODIFIED: Hybrid Gradient 1D)
static inline float block_cost_zmcl_avx(const float *ref, const float *comp,
                                        int len) {
  // --- PASS 1: MEAN DIFFERENCE CALCULATION ---
  float sum_diff = 0.0f;
#pragma omp simd reduction(+ : sum_diff)
  for (int i = 0; i < len; ++i) {
    sum_diff += (ref[i] - comp[i]);
  }

  const float mean_diff = sum_diff / static_cast<float>(len);
  const float eps_sq = EPSILON_SQ;

  // Constants for Gradient Weighting (Match Similarity Module)
  const float gradient_weight_factor = 1.4f;
  const float sensitivity = 150.0f;
  const float stab_epsilon = 1e-6f;

  // --- PASS 2: WEIGHTED CHARBONNIER ACCUMULATION ---
  // Cost = sum( weight * Charbonnier(diff_zero_mean) )
  float total_cost = 0.0f;

  // Helper lambda for fast tanh (inline)
  auto fast_tanh_local = [](float x) {
    if (x >= 3.0f)
      return 1.0f;
    if (x <= -3.0f)
      return -1.0f;
    float x2 = x * x;
    return x * (27.0f + x2) / (27.0f + 9.0f * x2);
  };

  // Iterate 1..len-1 to allow Gradient calculation (x-1, x+1)
  // Edges (0 and len-1) treated with weight 1.0

  // First pixel (no gradient)
  if (len > 0) {
    float d = (ref[0] - comp[0]) - mean_diff;
    total_cost += std::sqrt(d * d + eps_sq);
  }

#pragma omp simd reduction(+ : total_cost)
  for (int i = 1; i < len - 1; ++i) {
    // 1. Calculate 1D X-Gradient
    // Using Central Difference: (p[x+1] - p[x-1]) / 2 (or just diff)
    // Option A used: (p[x+1] - p[x-1])
    float gx1 = ref[i + 1] - ref[i - 1];
    float gx2 = comp[i + 1] - comp[i - 1];

    // 1D Gradient Magnitude
    float mag1_sq = gx1 * gx1;
    float mag2_sq = gx2 * gx2;
    float min_mag_sq = (mag1_sq < mag2_sq) ? mag1_sq : mag2_sq;

    // 2. Structure Weight (Cosine Similarity)
    float structure_weight = 1.0f;

    if (min_mag_sq > stab_epsilon && mag1_sq > stab_epsilon &&
        mag2_sq > stab_epsilon) {
      float dot = gx1 * gx2; // Dot product in 1D is just product
      float cos_sim = dot / std::sqrt(mag1_sq * mag2_sq);
      float score = (cos_sim > 0.0f ? cos_sim : 0.0f) * std::sqrt(min_mag_sq);

      structure_weight =
          1.0f + gradient_weight_factor * fast_tanh_local(score * sensitivity);
    }

    // 3. Zero-Mean Difference
    float diff = (ref[i] - comp[i]) - mean_diff;

    // 4. Weighted Charbonnier Cost
    total_cost += std::sqrt(diff * diff + eps_sq) * structure_weight;
  }

  // Last pixel (no gradient)
  if (len > 1) {
    float d = (ref[len - 1] - comp[len - 1]) - mean_diff;
    total_cost += std::sqrt(d * d + eps_sq);
  }

  return total_cost;
}

// =============================================================
// ===============  WRAPPER: calculate_fine_analysis  ===============
// =============================================================

float calculate_fine_analysis(const float *ref, const float *comp, int len) {
  if (!ref || !comp || len <= 0)
    return 0.0f;

  float zmcl_cost = block_cost_zmcl_avx(ref, comp, len);

  // Kita harus menormalisasi ZMCL agar tidak didominasi oleh ukuran tile
  const float tile_area_inv = 1.0f / static_cast<float>(len);

  return zmcl_cost * tile_area_inv;
}
