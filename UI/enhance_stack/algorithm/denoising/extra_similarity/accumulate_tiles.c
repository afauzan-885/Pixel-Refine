#include <math.h>
#ifdef _OPENMP
#include <omp.h>
#endif

#ifdef _WIN32
#define API_EXPORT __declspec(dllexport)
#else
#define API_EXPORT
#endif

// Fungsi untuk menghitung Mean Squared Error (MSE) antara dua tile
static double calculate_mse(const double *current, const double *reference, int w, int channels, int r, int c, int tile_h, int tile_w) {
    double mse = 0.0;
    int count = tile_h * tile_w * channels;
    
    for (int a = 0; a < tile_h; a++) {
        for (int b = 0; b < tile_w; b++) {
            int index = ((r + a) * w + (c + b)) * channels;
            for (int ch = 0; ch < channels; ch++) {
                double diff = current[index + ch] - reference[index + ch];
                mse += diff * diff;
            }
        }
    }
    return mse / count;
}

// Fungsi utama untuk mengakumulasi tile ke dalam gambar akhir
API_EXPORT void accumulate_tiles(
    double *final_image,
    double *weight_map,
    const double *current_image,
    const double *reference_image,
    const double *base_window,
    const int *row_starts,
    const int *col_starts,
    int num_rows, int num_cols,
    int h, int w, int channels,
    int tile_h, int tile_w,
    double motion_threshold, double noise_threshold, double scale
) {
    #pragma omp parallel for schedule(dynamic)
    for (int i = 0; i < num_rows; i++) {
        int r = row_starts[i];
        for (int j = 0; j < num_cols; j++) {
            int c = col_starts[j];
            if (r + tile_h > h || c + tile_w > w) continue; // Pastikan tile dalam batas

            double mse = calculate_mse(current_image, reference_image, w, channels, r, c, tile_h, tile_w);
            double adaptive_threshold = motion_threshold + noise_threshold * mse;
            double similarity_weight = exp(-mse / adaptive_threshold);
            
            for (int a = 0; a < tile_h; a++) {
                for (int b = 0; b < tile_w; b++) {
                    int window_idx = a * tile_w + b;
                    double window_val = base_window[window_idx];
                    int pixel_index = (r + a) * w + (c + b);
                    int pixel_index3 = pixel_index * channels;
                    
                    for (int ch = 0; ch < channels; ch++) {
                        final_image[pixel_index3 + ch] += current_image[pixel_index3 + ch] * window_val * similarity_weight * scale;
                    }
                    
                    #pragma omp atomic
                    weight_map[pixel_index] += window_val * similarity_weight;
                }
            }
        }
    }
}
