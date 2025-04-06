#ifndef MOTION_METRICS_CONFIG_HPP
#define MOTION_METRICS_CONFIG_HPP

// Include guard gaya #ifndef/#define/#endif (alternatif #pragma once)

namespace MotionMetricsConfig {
    // Epsilon untuk stabilitas numerik
    constexpr float STABILITY_EPSILON = 1e-6f;
    constexpr float CONFIDENCE_EPSILON = 1e-5f; // Epsilon spesifik untuk confidence

    // Faktor perhitungan confidence dan threshold adaptif
    constexpr float CONFIDENCE_SCALE_FACTOR = 1.0f;
    constexpr float ADAPTIVE_THRESHOLD_VARIABILITY_FACTOR = 1.5f;

    // Radius pencarian default (contoh, bisa jadi tidak terpakai jika selalu dari parameter)
    constexpr int DEFAULT_SEARCH_RADIUS = 7;

    // Threshold untuk akumulasi bobot global
    constexpr float GLOBAL_ACCUMULATION_WEIGHT_THRESHOLD = 1e-6f;
}

#endif // MOTION_METRICS_CONFIG_HPP