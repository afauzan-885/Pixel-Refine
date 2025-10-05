#include "refinement.hpp" // Sertakan header yang sesuai

#include <opencv2/imgproc.hpp> // Untuk cv::phaseCorrelate
#include <cmath>               // Untuk std::floor, std::fabs

// Fungsi helper ini hanya terlihat di dalam file ini (linkage internal)
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

// Implementasi subpixel refinement
// Hapus kata kunci 'static' dari sini jika ada, karena deklarasinya ada di .hpp
cv::Point2f subpixel_refinement(const cv::Mat &ref_layer,
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