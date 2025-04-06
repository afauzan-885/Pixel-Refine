#ifndef MOTION_METRICS_TYPES_HPP
#define MOTION_METRICS_TYPES_HPP

#include <vector>
#include <limits> // Untuk std::numeric_limits

// Deklarasi struct untuk hasil block matching
struct BlockMatchResult {
    float min_mad = std::numeric_limits<float>::max();
    float second_min_mad = std::numeric_limits<float>::max();
    std::vector<float> all_mads;
    int matches_found = 0;
    bool success = false;
};

#endif // MOTION_METRICS_TYPES_HPP