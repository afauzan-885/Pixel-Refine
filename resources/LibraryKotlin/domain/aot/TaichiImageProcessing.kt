package org.pixelrefine.genericui.domain.aot

/**
 * Flag / Enums untuk Operasi Algoritma Taichi AOT
 */
enum class InterpolationMode {
    NEAREST,
    BILINEAR,
    BICUBIC,
    AREA,
    LANCZOS4
}

enum class ColorConversionCode {
    BGR2RGB,
    RGB2BGR,
    BGR2GRAY,
    RGB2GRAY,
    BGR2HSV,
    HSV2BGR,
    BGR2LAB,
    LAB2BGR,
    BGR2YCrCb,
    YCrCb2BGR,
}

enum class ThresholdType {
    BINARY,
    BINARY_INV,
    TRUNC,
    TOZERO,
    TOZERO_INV,
    OTSU,
}

enum class BorderType {
    CONSTANT,
    REPLICATE,
    REFLECT_101,
}

enum class DemosaicAlgorithm {
    HAMILTON,
    ARM,
    MLRI_ADMM,
}

/**
 * Pustaka Pemrosesan Citra & Visi Komputer Taichi AOT (1:1 Paritas Python `taichi_algorithm`).
 *
 * Menggabungkan OpenCV-Style Image Ops, Demosaicing RAW, Denoising (NLM/BM3D),
 * Optical Flow, HDR Fusion, dan Tone Mapping.
 */

// ==========================================
// 1. SMOOTHING & BLURRING
// ==========================================

fun TaichiAot.gaussian_blur(
    src: TaichiGpuBuffer,
    ksize: Pair<Int, Int> = Pair(5, 5),
    sigmaX: Float = 1.5f,
    sigmaY: Float = sigmaX,
    returnGpu: Boolean = true,
): Any = run(
    "gaussian_blur",
    "src" to src,
    "kernel_w" to ksize.first,
    "kernel_h" to ksize.second,
    "sigma_x" to sigmaX,
    "sigma_y" to sigmaY,
    returnGpu = returnGpu,
)

fun TaichiAot.box_filter(
    src: TaichiGpuBuffer,
    ksize: Pair<Int, Int> = Pair(3, 3),
    returnGpu: Boolean = true,
): Any = run(
    "box_filter",
    "src" to src,
    "ksize_x" to ksize.first,
    "ksize_y" to ksize.second,
    returnGpu = returnGpu,
)

fun TaichiAot.median_filter(
    src: TaichiGpuBuffer,
    radius: Int = 1,
    returnGpu: Boolean = true,
): Any = run(
    "median_filter",
    "src" to src,
    "radius" to radius,
    returnGpu = returnGpu,
)

fun TaichiAot.bilateral_filter(
    src: TaichiGpuBuffer,
    d: Int = 9,
    sigmaColor: Float = 75.0f,
    sigmaSpace: Float = 75.0f,
    returnGpu: Boolean = true,
): Any = run(
    "bilateral_filter",
    "src" to src,
    "d" to d,
    "sigma_color" to sigmaColor,
    "sigma_space" to sigmaSpace,
    returnGpu = returnGpu,
)

fun TaichiAot.guided_filter(
    guide: TaichiGpuBuffer,
    src: TaichiGpuBuffer,
    radius: Int = 8,
    eps: Float = 0.04f,
    returnGpu: Boolean = true,
): Any = run(
    "guided_filter",
    "guide" to guide,
    "src" to src,
    "radius" to radius,
    "eps" to eps,
    returnGpu = returnGpu,
)

// ==========================================
// 2. GEOMETRI & INTERPOLASI
// ==========================================

fun TaichiAot.resize(
    src: TaichiGpuBuffer,
    dsize: Pair<Int, Int>,
    interpolation: InterpolationMode = InterpolationMode.BILINEAR,
    returnGpu: Boolean = true,
): Any {
    val graphName = when (interpolation) {
        InterpolationMode.NEAREST -> "nearest_resize"
        InterpolationMode.BILINEAR -> "bilinear_resize"
        InterpolationMode.BICUBIC -> "bicubic_resize"
        else -> "bilinear_resize"
    }
    return run(
        graphName,
        "src" to src,
        "target_w" to dsize.first,
        "target_h" to dsize.second,
        returnGpu = returnGpu,
    )
}

fun TaichiAot.remap(
    src: TaichiGpuBuffer,
    mapX: TaichiGpuBuffer,
    mapY: TaichiGpuBuffer,
    interpolation: InterpolationMode = InterpolationMode.BILINEAR,
    returnGpu: Boolean = true,
): Any = run(
    "remap",
    "src" to src,
    "map_x" to mapX,
    "map_y" to mapY,
    "interpolation" to interpolation.name.lowercase(),
    returnGpu = returnGpu,
)

fun TaichiAot.copy_make_border(
    src: TaichiGpuBuffer,
    top: Int,
    bottom: Int,
    left: Int,
    right: Int,
    borderType: BorderType = BorderType.REFLECT_101,
    returnGpu: Boolean = true,
): Any = run(
    "copy_make_border",
    "src" to src,
    "top" to top,
    "bottom" to bottom,
    "left" to left,
    "right" to right,
    "border_type" to borderType.name.lowercase(),
    returnGpu = returnGpu,
)

// ==========================================
// 3. GRADIENT, EDGES & SEGMENTASI
// ==========================================

fun TaichiAot.sobel(
    src: TaichiGpuBuffer,
    dx: Int = 1,
    dy: Int = 1,
    ksize: Int = 3,
    returnGpu: Boolean = true,
): Any = run(
    "sobel",
    "src" to src,
    "dx" to dx,
    "dy" to dy,
    "ksize" to ksize,
    returnGpu = returnGpu,
)

fun TaichiAot.laplacian(
    src: TaichiGpuBuffer,
    ksize: Int = 3,
    returnGpu: Boolean = true,
): Any = run(
    "laplacian",
    "src" to src,
    "ksize" to ksize,
    returnGpu = returnGpu,
)

fun TaichiAot.canny(
    src: TaichiGpuBuffer,
    threshold1: Float = 100.0f,
    threshold2: Float = 200.0f,
    returnGpu: Boolean = true,
): Any = run(
    "canny",
    "src" to src,
    "low_thresh" to threshold1,
    "high_thresh" to threshold2,
    returnGpu = returnGpu,
)

fun TaichiAot.threshold(
    src: TaichiGpuBuffer,
    thresh: Float,
    maxVal: Float = 255.0f,
    type: ThresholdType = ThresholdType.BINARY,
    returnGpu: Boolean = true,
): Any = run(
    "threshold",
    "src" to src,
    "thresh" to thresh,
    "max_val" to maxVal,
    "type" to type.name.lowercase(),
    returnGpu = returnGpu,
)

fun TaichiAot.otsu_threshold(
    src: TaichiGpuBuffer,
    returnGpu: Boolean = true,
): Any = run(
    "otsu_threshold",
    "src" to src,
    returnGpu = returnGpu,
)

// ==========================================
// 4. COLOR CONVERSION & ENHANCEMENT
// ==========================================

fun TaichiAot.cvtColor(
    src: TaichiGpuBuffer,
    code: ColorConversionCode,
    returnGpu: Boolean = true,
): Any = run(
    "cvt_color",
    "src" to src,
    "code" to code.name.lowercase(),
    returnGpu = returnGpu,
)

fun TaichiAot.clahe(
    src: TaichiGpuBuffer,
    clipLimit: Float = 2.0f,
    tileGridSize: Pair<Int, Int> = Pair(8, 8),
    returnGpu: Boolean = true,
): Any = run(
    "clahe",
    "src" to src,
    "clip_limit" to clipLimit,
    "grid_x" to tileGridSize.first,
    "grid_y" to tileGridSize.second,
    returnGpu = returnGpu,
)

fun TaichiAot.reinhard_tone_map(
    src: TaichiGpuBuffer,
    intensity: Float = 1.0f,
    returnGpu: Boolean = true,
): Any = run(
    "reinhard_tone_map",
    "src" to src,
    "intensity" to intensity,
    returnGpu = returnGpu,
)

// ==========================================
// 5. DEMOSAICING & DENOISING (RAW PIPELINE)
// ==========================================

fun TaichiAot.demosaic(
    rawBayer: TaichiGpuBuffer,
    algorithm: DemosaicAlgorithm = DemosaicAlgorithm.HAMILTON,
    bayerPattern: String = "rggb",
    returnGpu: Boolean = true,
): Any {
    val graph = when (algorithm) {
        DemosaicAlgorithm.HAMILTON -> "hamilton_demosaic"
        DemosaicAlgorithm.ARM -> "arm_demosaic"
        DemosaicAlgorithm.MLRI_ADMM -> "mlri_admm_demosaic"
    }
    return run(
        graph,
        "src" to rawBayer,
        "pattern" to bayerPattern,
        returnGpu = returnGpu,
    )
}

fun TaichiAot.non_local_means(
    src: TaichiGpuBuffer,
    h: Float = 3.0f,
    templateWindowSize: Int = 7,
    searchWindowSize: Int = 21,
    returnGpu: Boolean = true,
): Any = run(
    "non_local_means",
    "src" to src,
    "h" to h,
    "template_w" to templateWindowSize,
    "search_w" to searchWindowSize,
    returnGpu = returnGpu,
)

fun TaichiAot.farneback_flow(
    prev: TaichiGpuBuffer,
    next: TaichiGpuBuffer,
    pyrScale: Float = 0.5f,
    levels: Int = 3,
    winSize: Int = 15,
    iterations: Int = 3,
    returnGpu: Boolean = true,
): Any = run(
    "farneback_flow",
    "prev" to prev,
    "next" to next,
    "pyr_scale" to pyrScale,
    "levels" to levels,
    "win_size" to winSize,
    "iterations" to iterations,
    returnGpu = returnGpu,
)
