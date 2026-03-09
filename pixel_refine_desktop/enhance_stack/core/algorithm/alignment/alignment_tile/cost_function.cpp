#include "cost_function.hpp"

#include <algorithm>
#include <cmath>


// ============================================================================
// ZM-SSD: Zero-Mean Sum of Squared Differences (Matching GPU Implementation)
// ============================================================================
// Single-pass variance formula: E[X²] - E[X]²
// This is identical to the GPU's compute_zmssd_cost in cost_function.py
//
// Advantages over previous Charbonnier+Gradient approach:
// - ~3-4x faster (single pass, no sqrt/gradient/tanh per pixel)
// - Identical quality to GPU alignment
// - Simpler, more maintainable code

static inline float block_cost_zmssd(const float *ref, const float *comp,
                                     int len) {
  float sum_diff = 0.0f;
  float sum_sq_diff = 0.0f;

  // Single pass: accumulate both sum and sum of squares
#pragma omp simd reduction(+ : sum_diff, sum_sq_diff)
  for (int i = 0; i < len; ++i) {
    float d = ref[i] - comp[i];
    sum_diff += d;
    sum_sq_diff += d * d;
  }

  float n = static_cast<float>(len);
  float mean_diff = sum_diff / n;

  // Variance formula: Mean(X²) - Mean(X)²
  return std::max(0.0f, (sum_sq_diff / n) - (mean_diff * mean_diff));
}

// =============================================================
// ===============  WRAPPER: calculate_fine_analysis  ===============
// =============================================================

float calculate_fine_analysis(const float *ref, const float *comp, int len) {
  if (!ref || !comp || len <= 0)
    return 0.0f;

  return block_cost_zmssd(ref, comp, len);
}
