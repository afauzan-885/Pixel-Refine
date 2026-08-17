#ifndef REFINEMENT_HPP
#define REFINEMENT_HPP

#include <opencv2/core/types.hpp>
#include <opencv2/core/mat.hpp>

// Deklarasi fungsi untuk subpixel refinement
cv::Point2f subpixel_refinement(const cv::Mat &ref_layer,
                                      const cv::Mat &comp_layer,
                                      int x,
                                      int y,
                                      int dx,
                                      int dy,
                                      int tile_w,
                                      int tile_h);

#endif // REFINEMENT_HPP